#!/usr/bin/env python3
"""Deterministic examples-regeneration tool for the threats.md "Risk by MAESTRO
Layer" coverage table (Feature 098, FR-007).

Given a ``threats.md`` that already carries a "Risk by MAESTRO Layer" table, this
tool rewrites that table so it **always lists all 7 canonical MAESTRO layers
(L1-L7) in canonical L1->L7 order**, annotating any zero-finding layer with the
Decision-A string ``Analyzed — no findings this scan`` (em dash is U+2014). A
conditional ``Unclassified`` row is preserved and moved to the bottom. The table
heading is normalized to ``#### `` (h4) on write.

Modeled on :mod:`populate-affected-assets.py` for **transform mechanics only**
(stdlib-only, idempotent regex/line upsert, ``--check`` drift mode). It does NOT
inherit that script's production role.

**SCOPE — examples-regeneration helper, NOT a production-path component
(Architect boundary):** unlike ``populate-affected-assets.py`` (which IS wired
into the orchestrator/commands as a value authority), this tool MUST NOT be wired
into any command or orchestrator phase. Production authoring of the table remains
the orchestrator LLM directive (FR-001); this tool only regenerates the committed
``examples/**/threats.md`` tables to that same contract and doubles as a
``--check`` drift gate. Wiring it in would create the second source-of-truth this
design avoids.

**Why heading normalization matters (Architect CONCERN-1, HIGH):** the PDF
extractor substring-matches ``#### Risk by MAESTRO Layer``
(``extract-report-data.py`` ``parse_maestro_data``). A table under an ``### ``
(h3) heading parses to *zero* layers, so its PDF "MAESTRO Layer Analysis" page
renders empty. This tool discovers the heading level-agnostically
(``^#{3,4}\\s+Risk by MAESTRO Layer``) and normalizes it to ``#### `` on write.

**Determinism / byte-stability:**
  * Present rows (including the conditional ``Unclassified`` row) are preserved
    **verbatim** and only reordered — the PDF baselines and markdown diffs stay
    minimal (only added rows + reordering show up).
  * Absent canonical layers are appended as ``0`` + the annotation.
  * Running twice yields byte-identical output (idempotent): an already-canonical
    table round-trips unchanged, which is what ``--check`` asserts.

**Single source of truth:** the canonical layer *ordering* is imported from
``tachi_parsers.MAESTRO_LAYERS`` (no second hard-coded ID list). The layer
*names* (frozen by Feature 136) mirror the canonical set in
``extract-report-data.py`` / ``maestro-layers-shared.md`` and are used only to
label the rows this tool *adds* (present rows keep their authored label).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Import the canonical layer-ID ordering from the shared parser. READ-ONLY here
# (the plan lists tachi_parsers.py as unchanged for this feature); this is the
# single ordering authority — no second hard-coded L1..L7 list is introduced.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tachi_parsers import MAESTRO_LAYERS  # noqa: E402

_EM_DASH = "—"  # U+2014, the canonical annotation + layer-label separator
_EN_DASH = "–"  # U+2013, tolerated on read for robustness (extractor parity)

# Frozen canonical layer names (Feature 136). Mirrors
# extract-report-data.py:_MAESTRO_LAYER_NAMES and
# .claude/skills/tachi-shared/references/maestro-layers-shared.md. Used ONLY to
# label canonical layers this tool *adds* to a table; present rows are preserved
# verbatim, so an existing label is never rewritten from this map. A local copy
# is acceptable here because this is an examples-only tool (never production) and
# tachi_parsers.py is out of scope to modify for this feature.
_MAESTRO_LAYER_NAMES = {
    "L1": "Foundation Model",
    "L2": "Data Operations",
    "L3": "Agent Framework",
    "L4": "Deployment Infrastructure",
    "L5": "Evaluation and Observability",
    "L6": "Security and Compliance",
    "L7": "Agent Ecosystem",
}

# Decision-A zero-finding annotation. Markdown table cell carries NO trailing
# period (the Typst prose literal adds one — the sole sanctioned cross-format
# difference, asserted on the phrase not the punctuation; PM OBS-2).
_ZERO_FINDING_ANNOTATION = f"Analyzed {_EM_DASH} no findings this scan"

_HEADING_TEXT = "Risk by MAESTRO Layer"
_CANONICAL_HEADING = f"#### {_HEADING_TEXT}"
# Heading-level-agnostic discovery: matches ### or #### (Architect CONCERN-1).
_HEADING_RE = re.compile(rf"^#{{3,4}}[ \t]+{re.escape(_HEADING_TEXT)}[ \t]*$")

_UNCLASSIFIED = "Unclassified"


def _layer_id_of(layer_cell: str) -> str:
    """Extract the canonical layer ID from a "MAESTRO Layer" cell.

    ``"L4 — Deployment Infrastructure"`` -> ``"L4"``; ``"Unclassified"`` ->
    ``"Unclassified"``. Splits on the em dash, falling back to the en dash, to
    mirror ``extract-report-data.py`` parsing exactly. Pure.
    """
    parts = layer_cell.split(_EM_DASH, 1)
    if len(parts) < 2:
        parts = layer_cell.split(_EN_DASH, 1)
    return parts[0].strip()


def _split_row(line: str) -> "list[str]":
    """Split a markdown table row into stripped cell values.

    ``"| L1 — Foundation Model | 22 | Critical |"`` ->
    ``["L1 — Foundation Model", "22", "Critical"]``. The outer pipes' empty
    edges are dropped. Pure.
    """
    cells = [c.strip() for c in line.split("|")]
    if cells and cells[0] == "":
        cells = cells[1:]
    if cells and cells[-1] == "":
        cells = cells[:-1]
    return cells


def _find_table_region(lines: "list[str]"):
    """Locate the "Risk by MAESTRO Layer" heading + table in ``lines``.

    Returns ``(heading_idx, table_start_idx, table_end_idx)`` where the table
    spans ``lines[table_start_idx:table_end_idx]`` (header row, separator row,
    then data rows — the first contiguous block of ``|``-leading lines after the
    heading). Returns ``None`` if no heading is found, or a heading is found but
    is not followed by a valid (header + separator) table. Pure.
    """
    for i, line in enumerate(lines):
        if _HEADING_RE.match(line):
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and lines[j].lstrip().startswith("|"):
                k = j
                while k < len(lines) and lines[k].lstrip().startswith("|"):
                    k += 1
                if k - j >= 2:  # need at least a header + a separator row
                    return (i, j, k)
            return None  # heading present but no parseable table beneath it
    return None


def _render_data_rows(present: "dict[str, str]") -> "list[str]":
    """Build the canonical data-row block from parsed present rows.

    Emits all 7 canonical layers in ``MAESTRO_LAYERS`` order (present rows kept
    verbatim; absent layers added as ``0`` + the annotation), then any
    non-canonical "other" rows (preserved, sorted — defensive; examples have
    none), then the conditional ``Unclassified`` row last. Pure and
    deterministic.
    """
    rows: "list[str]" = []
    for lid in MAESTRO_LAYERS:
        if lid in present:
            rows.append(present[lid])
        else:
            name = _MAESTRO_LAYER_NAMES.get(lid, lid)
            rows.append(f"| {lid} {_EM_DASH} {name} | 0 | {_ZERO_FINDING_ANNOTATION} |")
    for lid in sorted(k for k in present if k not in MAESTRO_LAYERS and k != _UNCLASSIFIED):
        rows.append(present[lid])
    if _UNCLASSIFIED in present:
        rows.append(present[_UNCLASSIFIED])
    return rows


def populate_content(content: str) -> str:
    """Rewrite the "Risk by MAESTRO Layer" table to the 7-canonical-row contract.

    Pure and idempotent. If ``content`` has no such table, it is returned
    unchanged (so the tool is a safe no-op on the table-less sample-reports).
    Otherwise the heading is normalized to ``#### ``, the header + separator rows
    are preserved verbatim, present data rows are reordered into canonical
    order (kept byte-for-byte), absent canonical layers are added with the
    zero-finding annotation, and any ``Unclassified`` row is moved last. All
    content before the heading and after the table (e.g. a trailing ``Note:``
    paragraph) is preserved verbatim.
    """
    lines = content.split("\n")
    region = _find_table_region(lines)
    if region is None:
        return content
    heading_idx, table_start, table_end = region

    header_row = lines[table_start]
    separator_row = lines[table_start + 1]
    data_lines = lines[table_start + 2 : table_end]

    present: "dict[str, str]" = {}
    for dl in data_lines:
        cells = _split_row(dl)
        if not cells:
            continue
        lid = _layer_id_of(cells[0])
        if lid:
            present.setdefault(lid, dl)  # first occurrence wins; kept verbatim

    new_data = _render_data_rows(present)
    gap = lines[heading_idx + 1 : table_start]  # preserve blank-line gap verbatim

    new_lines = (
        lines[:heading_idx]
        + [_CANONICAL_HEADING]
        + gap
        + [header_row, separator_row]
        + new_data
        + lines[table_end:]
    )
    return "\n".join(new_lines)


# =============================================================================
# CLI
# =============================================================================


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="populate-maestro-coverage.py",
        description=(
            "Deterministically regenerate the threats.md 'Risk by MAESTRO Layer' "
            "table to all 7 canonical layers (L1-L7) in canonical order with "
            "Model-A zero-finding annotations. Examples-regeneration tool only — "
            "never wire into a command or orchestrator phase."
        ),
    )
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="threats.md file(s) to update in place.",
    )
    parser.add_argument(
        "--threats",
        type=Path,
        default=None,
        help="Alias for a single threats.md file (appended to positional FILES).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Write the result here instead of overwriting the input "
            "(single file only). Use '-' for stdout."
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Do not write. Exit 0 if every table is already canonical "
            "(idempotent), exit 2 if regenerating any file would change it."
        ),
    )
    return parser


def main(argv=None) -> int:
    args = _build_arg_parser().parse_args(argv)

    targets: "list[Path]" = list(args.files)
    if args.threats is not None:
        targets.append(args.threats)
    if not targets:
        print("Error: no threats.md file given (pass FILES or --threats).", file=sys.stderr)
        return 1
    if args.output is not None and len(targets) != 1:
        print("Error: --output is only valid with a single input file.", file=sys.stderr)
        return 1

    drift = False
    for path in targets:
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"Error: cannot read {path}: {exc}", file=sys.stderr)
            return 1

        updated = populate_content(content)

        if args.check:
            if updated != content:
                drift = True
                print(
                    f"Drift: {path} MAESTRO coverage table is not canonical "
                    f"(run without --check to regenerate).",
                    file=sys.stderr,
                )
            continue

        if args.output is not None:
            if str(args.output) == "-":
                sys.stdout.write(updated)
            else:
                try:
                    args.output.write_text(updated, encoding="utf-8")
                except OSError as exc:
                    print(f"Error: cannot write {args.output}: {exc}", file=sys.stderr)
                    return 1
        elif updated != content:
            try:
                path.write_text(updated, encoding="utf-8")
            except OSError as exc:
                print(f"Error: cannot write {path}: {exc}", file=sys.stderr)
                return 1

    if args.check and drift:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
