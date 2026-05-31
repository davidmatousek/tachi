#!/usr/bin/env python3
"""Deterministic populator for the threats.md ``affected_assets`` block (F-260b).

This is the **single value authority** for ``affected_assets`` across every
tachi output surface (plan AD-1 §1; FR-2 "deterministic, not LLM-authored").
It is a pure, non-LLM, stdlib-only component that:

  1. Reads the architecture description and the *already-emitted* ``threats.md``
     content.
  2. Calls :func:`tachi_parsers.parse_component_asset_map` to obtain the
     component -> sorted/deduped/lowercase asset-tag mapping (the parser is
     FROZEN per SC-011 — this module imports and calls it, never edits it).
  3. Joins every finding in ``threats.md`` (§3 STRIDE + §4 AI tables, surfaced
     through the Section 7 Recommended Actions table that
     :func:`tachi_parsers.parse_threats_findings` parses) to a component using
     the **same case-insensitive / fuzzy component-match cascade** the
     risk-scorer §3.5 modifier pass uses (delegated to Reachability Analysis
     §6f). ``affected_assets = component_asset_map.get(matched_component, [])``,
     copied **verbatim** from the parser (already sorted, deduped, lowercase);
     an unmatched finding yields ``[]``.
  4. Writes / replaces an always-present ``## Affected Assets`` block in
     ``threats.md`` keyed by finding ID, per the T004 contract
     (``specs/302-asset-tag-output-wiring/contracts/affected-assets-contract.md``
     §2 and the rendered shape in
     ``templates/tachi/output-schemas/threats.md`` → *Affected Assets Block*).

**Scope (T005)**: the populator and its CLI only. It is NOT wired into the
pipeline commands here (that is T006) and the unit tests live in T007.

**Hard constraints honored**:

  * **stdlib-only** (PAT-014) — no third-party imports.
  * **No scoring change** (NFR-2) — this records provenance only. It never reads
    or writes ``cvss_base``, the composite, the severity band, the 9.2 ceiling,
    or any modifier logic.
  * **Tables byte-stable** — the existing STRIDE/AI (and all other) tables are
    never edited; the block is appended (or, if already present, replaced
    in place) so existing rows stay byte-identical (SC-002 "added lines only").
  * **Idempotent** — running twice produces identical output: an existing
    ``## Affected Assets`` block is replaced rather than duplicated.

The five normative serialization rules (per-finding keyed by ID, always
present, ``[]`` default, closed 6-value enum, sorted+deduped) come from
``.claude/skills/tachi-shared/references/finding-format-shared.md`` →
*``affected_assets`` Block*. Sort order and dedup are inherited verbatim from
``parse_component_asset_map``; this module does not re-sort.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Import the FROZEN parser + enum from the shared module. These are READ-ONLY
# here — SC-011 binary-diffs tachi_parsers.py against main and must show zero
# change.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tachi_parsers import (  # noqa: E402
    VALID_ASSET_TAGS,
    parse_component_asset_map,
    parse_threats_findings,
)

# Heading of the appended block. Authoritative surface:
# templates/tachi/output-schemas/threats.md -> "## Affected Assets".
AFFECTED_ASSETS_HEADING = "## Affected Assets"

# Table column headers, byte-matching the template's rendered shape.
_COL_FINDING_ID = "Finding ID"
_COL_AFFECTED_ASSETS = "Affected Assets"


# =============================================================================
# Component-name join — mirrors risk-scorer §3.5 / Reachability Analysis §6f
# =============================================================================
#
# risk-scorer.md §3.5 step 1 specifies: "Look up the finding's target component
# in component_asset_map using the same case-insensitive + fuzzy-match cascade
# as Reachability Analysis Section 6f. If no match, skip." data-model.md repeats
# this verbatim and adds: "Unmatched -> []".
#
# The §6f cascade is the canonical tachi component-name matcher. It is a tiered
# best-match search that the modifier pass, trust-zone cross-referencing, and
# reachability all share. It is isolated here as the SINGLE join point so the
# populator's finding->component join lines up with the components the scorer
# already matched. The cascade is intentionally the only place name-matching
# heuristics live; the rest of the populator is a pure dict lookup.
#
# Tier order mirrors reachability-analysis.md "Component Name Fuzzy Matching"
# (§6f) VERBATIM (first match wins; deterministic):
#
#   Step 1 — Exact case-insensitive match. Query the map keys with
#            case-insensitive comparison; if found, use that key.
#   Step 2 — Substring containment match. If Step 1 fails, check whether the
#            finding's component name is contained within any map key, or vice
#            versa (case-insensitive). Use the LONGEST matching key (§6f
#            example: "LLM Agent" -> "LLM Agent Orchestrator").
#   Step 3 — Word overlap match. If Steps 1-2 fail, tokenize both names into
#            words (split on spaces, hyphens, underscores). Select the map key
#            with the highest word-overlap ratio (matching / total-unique
#            words); require >= 50% to accept (§6f example: "Knowledge Base
#            Store" vs "Knowledge Base" = 2/3 = 67% -> accepted).
#   Step 4 — No match -> None. (§6f defaults reachability to 5.0 here; the
#            populator's analogue is `affected_assets = []`, per data-model.md
#            "Unmatched -> []".)
#
# Determinism: §6f does not pin tie-breaks, so this implementation iterates map
# keys in sorted order and breaks every "longest"/"highest ratio" tie with the
# lexicographically-first key — equal inputs always yield the same key, which
# is what SC-002 byte-stable baselines require.


def _normalize_component_name(name: str) -> str:
    """Lower-case, collapse internal whitespace, strip edge punctuation.

    Mirrors the normalization the §6f cascade applies before comparison so the
    join tolerates the cosmetic differences (markdown bold, doubled spaces,
    trailing punctuation) that creep between the architecture label and the
    threats.md table cell. Pure and side-effect-free.
    """
    cleaned = name.replace("**", "")
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.strip()
    cleaned = cleaned.strip(".,;:!?-_")
    cleaned = cleaned.strip()
    return cleaned.lower()


def _tokenize_component_name(name: str) -> "set":
    """Tokenize a component name into a lowercase word set for §6f Step 3.

    Splits on whitespace, hyphens, and underscores (the §6f tokenization rule),
    strips markdown bold, lowercases, and drops empty tokens. Returns a set so
    the caller can compute the word-overlap ratio (intersection / union). Pure.
    """
    cleaned = name.replace("**", "")
    tokens = re.split(r"[\s\-_]+", cleaned.lower())
    return {t for t in tokens if t}


def match_component(component: str, asset_map_keys) -> str | None:
    """Resolve a finding's ``component`` to a key of ``component_asset_map``.

    Implements the case-insensitive / fuzzy cascade described above (the
    risk-scorer §3.5 / Reachability §6f matcher), returning the matched map key
    or ``None`` when no tier matches. The matched key is then used verbatim by
    the caller to look up the already-sorted tag list. Deterministic: equal
    inputs always return the same key.

    Args:
        component: The finding's target component name (from a threats.md cell).
        asset_map_keys: An iterable of ``component_asset_map`` keys (component
            display names) to match against.

    Returns:
        The matched key from ``asset_map_keys``, or ``None`` if unmatched.
    """
    if not component:
        return None

    # Materialize once and iterate in sorted order so every tie-break is
    # deterministic (§6f leaves ties unspecified; sorted iteration + the
    # lexicographic secondary key pin the result for SC-002 byte-stability).
    keys = sorted(asset_map_keys)

    comp_norm = _normalize_component_name(component)

    # §6f Step 1 — Exact case-insensitive match. (Normalized comparison also
    # absorbs markdown-bold / doubled-whitespace artifacts a threats.md table
    # cell may carry vs the architecture label; an exact case-fold is a strict
    # subset of this, so this single pass covers both.)
    for key in keys:
        if _normalize_component_name(key) == comp_norm and comp_norm:
            return key

    if not comp_norm:
        return None

    # §6f Step 2 — Substring containment match. The finding's component name is
    # contained within a map key, or a map key is contained within the
    # component name (case-insensitive). Use the LONGEST matching key (§6f
    # example: finding "LLM Agent" -> key "LLM Agent Orchestrator").
    best_key = None
    best_len = -1
    for key in keys:
        key_norm = _normalize_component_name(key)
        if not key_norm:
            continue
        if key_norm in comp_norm or comp_norm in key_norm:
            if len(key_norm) > best_len:
                best_len = len(key_norm)
                best_key = key
    if best_key is not None:
        return best_key

    # §6f Step 3 — Word overlap match. Tokenize both names on whitespace,
    # hyphens, and underscores; select the key with the highest overlap ratio
    # (matching words / total unique words); require >= 50% to accept (§6f
    # example: "Knowledge Base Store" vs "Knowledge Base" = 2/3 = 67%).
    comp_words = _tokenize_component_name(component)
    if comp_words:
        best_key = None
        best_ratio = 0.0
        for key in keys:
            key_words = _tokenize_component_name(key)
            if not key_words:
                continue
            union = comp_words | key_words
            if not union:
                continue
            ratio = len(comp_words & key_words) / len(union)
            if ratio >= 0.5 and ratio > best_ratio:
                best_ratio = ratio
                best_key = key
        if best_key is not None:
            return best_key

    # §6f Step 4 — No match. (§6f defaults reachability to 5.0; the populator's
    # analogue per data-model.md is affected_assets = [], assigned by the caller.)
    return None


# =============================================================================
# affected_assets computation
# =============================================================================


def compute_affected_assets(architecture: str, threats_content: str) -> "list[tuple[str, list]]":
    """Compute the per-finding ``affected_assets`` rows for ``threats.md``.

    Pure function. For each finding parsed from ``threats_content`` (in the order
    the Section 7 Recommended Actions table lists them — the same order the
    STRIDE/AI tables and SARIF results use), join the finding's component to the
    asset map via :func:`match_component` and take
    ``component_asset_map.get(matched_component, [])`` **verbatim** (already
    sorted, deduped, lowercase). Unmatched components -> ``[]``.

    Args:
        architecture: The architecture description (Mermaid with inline
            ``[asset:...]`` tags). Passed straight to
            :func:`parse_component_asset_map`.
        threats_content: The emitted ``threats.md`` content (tables already
            written by the orchestrator).

    Returns:
        A list of ``(finding_id, affected_assets)`` tuples — one per finding,
        order-preserving, every finding present. ``affected_assets`` is a list
        drawn from the frozen :data:`VALID_ASSET_TAGS` enum, sorted ascending,
        ``[]`` when none. Findings with an empty/missing ID are skipped (they
        cannot be keyed).
    """
    component_asset_map = parse_component_asset_map(architecture)
    map_keys = list(component_asset_map.keys())

    rows: "list[tuple[str, list]]" = []
    for finding in parse_threats_findings(threats_content):
        finding_id = (finding.get("id") or "").strip()
        if not finding_id:
            # A finding with no parseable ID cannot be keyed in the block.
            continue
        component = (finding.get("component") or "").strip()
        matched = match_component(component, map_keys)
        # Verbatim copy from the parser (sorted/deduped/lowercase); [] default.
        tags = component_asset_map.get(matched, []) if matched is not None else []
        rows.append((finding_id, tags))
    return rows


def _render_assets_value(tags: "list") -> str:
    """Render a tag list as the bracketed, comma-space-joined block value.

    ``["auth", "pii"]`` -> ``"[auth, pii]"``; ``[]`` -> ``"[]"``. The list is
    emitted in the order received (already sorted ascending by the parser); this
    function does NOT re-sort. Matches the template's rendered shape exactly.
    """
    return "[" + ", ".join(tags) + "]"


def render_affected_assets_block(rows: "list[tuple[str, list]]") -> str:
    """Render the ``## Affected Assets`` markdown block from computed rows.

    Produces the exact surface defined in
    ``templates/tachi/output-schemas/threats.md`` → *Affected Assets Block*::

        ## Affected Assets

        | Finding ID | Affected Assets |
        |------------|-----------------|
        | S-1 | [auth, pii] |
        | T-2 | [] |

    The block has no trailing newline (the caller controls block separation).
    Row order follows ``rows`` (finding order), making the block deterministic
    and diff-stable across runs.
    """
    lines = [
        AFFECTED_ASSETS_HEADING,
        "",
        f"| {_COL_FINDING_ID} | {_COL_AFFECTED_ASSETS} |",
        "|------------|-----------------|",
    ]
    for finding_id, tags in rows:
        lines.append(f"| {finding_id} | {_render_assets_value(tags)} |")
    return "\n".join(lines)


# Matches an existing "## Affected Assets" block from its heading up to (but not
# including) the next ATX heading of the same-or-higher level, or end of file.
# Used to replace an existing block in place (idempotency) rather than appending
# a duplicate. The heading match is anchored at column 0 and exact so it never
# collides with deeper headings or prose mentioning "Affected Assets".
_EXISTING_BLOCK_PATTERN = re.compile(
    r"\n*^##[ \t]+Affected Assets[ \t]*$.*?(?=^#{1,2}[ \t]|\Z)",
    re.MULTILINE | re.DOTALL,
)


def upsert_affected_assets_block(threats_content: str, block: str) -> str:
    """Insert or replace the ``## Affected Assets`` block in ``threats_content``.

    Idempotent: if a ``## Affected Assets`` block already exists, it is replaced
    in place (so re-running the populator yields byte-identical output and never
    duplicates the block). Otherwise the block is appended at the end of the
    document. The existing STRIDE/AI and all other tables are left byte-identical
    — only the trailing block region changes.

    Returns the updated ``threats.md`` content with a single trailing newline.
    """
    # Normalize: strip trailing whitespace/newlines from the source body so
    # placement is deterministic regardless of how many blank lines the source
    # ended with.
    existing = _EXISTING_BLOCK_PATTERN.search(threats_content)
    if existing:
        # Replace in place. Re-derive the body before the block and any content
        # that followed the block (defensive — normally nothing follows).
        before = threats_content[: existing.start()]
        after = threats_content[existing.end():]
        before = before.rstrip("\n")
        after = after.lstrip("\n")
        parts = [before, block]
        rebuilt = "\n\n".join(p for p in parts if p)
        if after:
            rebuilt = rebuilt + "\n\n" + after
        return rebuilt.rstrip("\n") + "\n"

    body = threats_content.rstrip("\n")
    if body:
        return body + "\n\n" + block + "\n"
    return block + "\n"


def populate(architecture: str, threats_content: str) -> str:
    """End-to-end: compute the block and upsert it into ``threats_content``.

    Pure function combining :func:`compute_affected_assets`,
    :func:`render_affected_assets_block`, and
    :func:`upsert_affected_assets_block`. Deterministic and idempotent.

    Args:
        architecture: Architecture description with inline ``[asset:...]`` tags.
        threats_content: The emitted ``threats.md`` content.

    Returns:
        The updated ``threats.md`` content with the ``## Affected Assets`` block
        present (appended on first run, replaced in place on subsequent runs).
    """
    rows = compute_affected_assets(architecture, threats_content)
    block = render_affected_assets_block(rows)
    return upsert_affected_assets_block(threats_content, block)


# =============================================================================
# CLI
# =============================================================================


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="populate-affected-assets.py",
        description=(
            "Deterministically populate the threats.md '## Affected Assets' "
            "block from an architecture description's inline [asset:...] tags "
            "(F-260b value authority; records provenance only, never re-scores)."
        ),
    )
    parser.add_argument(
        "--architecture",
        required=True,
        type=Path,
        help="Path to the architecture description (Mermaid with [asset:...] tags).",
    )
    parser.add_argument(
        "--threats",
        required=True,
        type=Path,
        help="Path to the emitted threats.md to update in place.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Write the result here instead of overwriting --threats. "
            "Use '-' for stdout."
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Do not write. Exit 0 if the block is already up to date "
            "(idempotent), exit 2 if running the populator would change "
            "threats.md."
        ),
    )
    return parser


def main(argv=None) -> int:
    args = _build_arg_parser().parse_args(argv)

    try:
        architecture = args.architecture.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Error: cannot read architecture file: {exc}", file=sys.stderr)
        return 1
    try:
        threats_content = args.threats.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Error: cannot read threats file: {exc}", file=sys.stderr)
        return 1

    updated = populate(architecture, threats_content)

    if args.check:
        if updated == threats_content:
            return 0
        print(
            f"Error: {args.threats} affected_assets block is out of date "
            f"(run without --check to update).",
            file=sys.stderr,
        )
        return 2

    if args.output is not None:
        if str(args.output) == "-":
            sys.stdout.write(updated)
            return 0
        try:
            args.output.write_text(updated, encoding="utf-8")
        except OSError as exc:
            print(f"Error: cannot write output file: {exc}", file=sys.stderr)
            return 1
        return 0

    try:
        args.threats.write_text(updated, encoding="utf-8")
    except OSError as exc:
        print(f"Error: cannot write threats file: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
