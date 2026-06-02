"""MAESTRO coverage invariant across shipped example threat models (Feature 098, FR-009b / T010).

Feature 098 guarantees that every example ``threats.md`` which presents a "Risk by
MAESTRO Layer" distribution table presents ALL SEVEN canonical MAESTRO layers
(L1-L7) as rows — a complete coverage matrix, not a sparse one. This test is the
durability guard for that property: it discovers the example corpus dynamically
and, for each file that carries the table, asserts no canonical layer is missing.

Files WITHOUT the table are skipped (not failed). This naturally excludes the two
table-less sample reports (consumer-agent-app, predictive-ml-app) that use an
older intermediate format, and any future table-less fixture.

Notes on robustness (per Architect review of Feature 098):
  - CONCERN-1 (heading level varies): discovery is heading-level-agnostic. Some
    files use a native ``#### Risk by MAESTRO Layer`` (h4) heading; others are
    h3-normalized to ``### Risk by MAESTRO Layer``. The detector matches either
    an ``h3``/``h4`` heading OR a bare ``Risk by MAESTRO Layer`` substring, so it
    must never anchor on the ``#### `` form.
  - Assertion strength: the missing-layer assertion fails loudly and NAMES the
    absent L-ID(s); it parses the layer column robustly (first cell beginning
    with the L-ID, e.g. ``L4`` in ``| L4 — Deployment Infrastructure | … |``).
  - No snapshot counts are hardcoded: the file list is globbed at collection time
    and each discovered file is reported independently via parametrization.

This test is intentionally NOT wired into CI — the drift-gating concern is
tracked separately.
"""

import re
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]

# Import the canonical layer list from the shared parser module rather than
# duplicating it, so this invariant tracks the single source of truth.
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from tachi_parsers import MAESTRO_LAYERS  # noqa: E402

# Heading-level-agnostic detector for the distribution table (Architect CONCERN-1):
# matches an h3 or h4 "Risk by MAESTRO Layer" heading. A bare-substring fallback in
# ``_has_maestro_table`` covers any non-heading occurrence.
_MAESTRO_HEADING_RE = re.compile(
    r"^#{3,4}\s+Risk by MAESTRO Layer\b", re.MULTILINE
)

# A table row whose first cell begins with a canonical layer ID, e.g.
# "L4 — Deployment Infrastructure". The first cell is normalized (bold markers
# stripped) before matching so "**L4** — …" rows are still recognized.
_LAYER_ID_RE = re.compile(r"^(L[1-7])\b")


def _discover_example_threats() -> list:
    """Glob every example threats.md, excluding any path under a test-output dir."""
    return sorted(
        p
        for p in REPO_ROOT.glob("examples/**/threats.md")
        if "test-output/" not in p.as_posix()
    )


def _has_maestro_table(text: str) -> bool:
    """True if the document presents a "Risk by MAESTRO Layer" distribution table.

    Heading-level-agnostic: an h3/h4 heading match OR a bare substring occurrence
    both qualify. Files lacking the table are skipped by the test.
    """
    if _MAESTRO_HEADING_RE.search(text):
        return True
    return "Risk by MAESTRO Layer" in text


def _present_layer_ids(text: str) -> set:
    """Return the set of canonical L-IDs that appear as table rows under the heading.

    Scans the lines after the MAESTRO heading (or the bare-substring anchor),
    reads the leading cell of each ``|``-delimited row, and collects any first
    cell that starts with a canonical layer ID. Stops at the next top-level
    section header so unrelated downstream tables are not scanned.
    """
    match = _MAESTRO_HEADING_RE.search(text)
    anchor = match.start() if match else text.find("Risk by MAESTRO Layer")
    if anchor < 0:
        return set()

    found = set()
    # Skip the heading/anchor line itself, then walk forward.
    body_lines = text[anchor:].splitlines()[1:]
    seen_table = False
    for line in body_lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            if seen_table:
                # Table block ended (blank line or prose after rows began).
                break
            if stripped.startswith("## ") or stripped.startswith("# "):
                # Reached a new section before any table row — give up.
                break
            continue
        seen_table = True
        cells = [c.strip().strip("*").strip() for c in stripped.split("|")[1:-1]]
        if not cells:
            continue
        m = _LAYER_ID_RE.match(cells[0])
        if m:
            found.add(m.group(1))
    return found


# Discover the corpus once at collection time. Each file with a table is reported
# independently; files without a table are still parametrized but skip cleanly.
_EXAMPLE_THREATS = _discover_example_threats()


def _param_id(path: Path) -> str:
    """Stable, readable test id: path relative to the repo root."""
    return str(path.relative_to(REPO_ROOT))


@pytest.mark.parametrize("threats_path", _EXAMPLE_THREATS, ids=_param_id)
def test_maestro_table_covers_all_seven_layers(threats_path):
    """Every example threats.md with a MAESTRO table must list all 7 canonical layers.

    Files without the table are skipped (the two intermediate-format sample
    reports fall into this bucket). For files that DO carry the table, every L-ID
    in ``MAESTRO_LAYERS`` must appear as a row; the assertion names any missing
    layer so a future sparse table is immediately diagnosable.
    """
    assert _EXAMPLE_THREATS, (
        "No example threats.md files discovered under examples/** — the glob "
        "found nothing, which itself indicates a structural regression."
    )

    text = threats_path.read_text(encoding="utf-8")

    if not _has_maestro_table(text):
        pytest.skip(
            f"{_param_id(threats_path)} has no 'Risk by MAESTRO Layer' table "
            "(intermediate-format sample report); coverage invariant N/A."
        )

    present = _present_layer_ids(text)
    missing = [layer for layer in MAESTRO_LAYERS if layer not in present]

    assert not missing, (
        f"{_param_id(threats_path)} presents a 'Risk by MAESTRO Layer' table "
        f"but is MISSING canonical layer(s): {missing}. "
        f"A complete MAESTRO coverage matrix requires all of {MAESTRO_LAYERS}; "
        f"found rows for {sorted(present)}."
    )
