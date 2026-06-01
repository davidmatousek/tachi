"""Unit tests for the ``## Affected Assets`` block extractor (F-260b / Wave 3).

Exercises :func:`sarif_common.parse_affected_assets` — the inverse of the
deterministic populator (``scripts/populate-affected-assets.py`` ->
``render_affected_assets_block``). The extractor parses the always-present
``## Affected Assets`` markdown table back into ``{finding_id: [tags]}`` and is
the single value source the SARIF regeneration / verification tier reads, so the
generators (`generate-threats-sarif.py`, `generate-risk-scores-sarif.py`) never
independently re-derive from ``component_asset_map``.

Test coverage targets (the extractor's EDGE cases only — the populator render
side is T007, cross-format SARIF equality is T013):

* **No block present** -> ``{}`` (graceful, mirrors ``parse_component_metadata``
  robustness when an optional section is absent).
* **Empty-tags row** ``| S-1 | [] |`` -> ``{"S-1": []}`` (empty list, not
  ``[""]``, not a missing key).
* **Multi-tag row** -> order preserved verbatim as written (the populator already
  sorted ascending; the extractor does NOT re-sort or dedup).
* **Whitespace tolerance** — extra spaces inside the brackets and around the pipe
  cells parse cleanly.
* **Markdown-bold tolerance** — ``**S-3**`` in the finding-ID cell strips to
  ``S-3``.
* **Header + separator skipped** — the ``Finding ID``/``Affected Assets`` header
  row and the ``|---|---|`` rule never surface as dict keys.
* **Round-trip** — a known ``[(finding_id, tags)]`` list rendered by the populator
  and fed back through the extractor reconstructs the input exactly, including a
  ``[]`` row.

Stdlib-only per PAT-014 — no PyYAML, no third-party libs. The hyphenated populator
filename (``populate-affected-assets.py``) is not importable by name, so it is
loaded via ``importlib.util.spec_from_file_location`` (the established repo
precedent — see ``tests/scripts/test_f_a3_populator_wiring.py``).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from sarif_common import parse_affected_assets  # noqa: E402  -- after sys.path mutation

# Hyphenated filename => not importable via ``import``; load by file location so
# the round-trip test can render with the real populator block writer.
_POPULATOR_PATH = REPO_ROOT / "scripts" / "populate-affected-assets.py"
_spec = importlib.util.spec_from_file_location("populate_affected_assets", _POPULATOR_PATH)
_populator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_populator)
render_affected_assets_block = _populator.render_affected_assets_block


# Canonical block header + separator, byte-matching the populator's output. Used
# to frame hand-rolled table fixtures so they exercise the exact rows the
# extractor must skip.
_BLOCK_HEADER = (
    "## Affected Assets\n"
    "\n"
    "| Finding ID | Affected Assets |\n"
    "|------------|-----------------|\n"
)


def _block(*rows: str) -> str:
    """Frame data ``rows`` with the canonical heading, header, and separator."""
    return _BLOCK_HEADER + "".join(row if row.endswith("\n") else row + "\n" for row in rows)


# =============================================================================
# No block present -> {} (graceful)
# =============================================================================


@pytest.mark.parametrize(
    "content",
    [
        "",
        "   ",
        "\n\n",
        "# Threat Model\n\nNo affected-assets section here at all.\n",
    ],
)
def test_missing_block_returns_empty_dict(content):
    """Absent ``## Affected Assets`` block collapses to {} (no exception)."""
    assert parse_affected_assets(content) == {}


def test_unrelated_headings_do_not_trigger_a_match():
    """A document with other ## sections but no Affected Assets block -> {}."""
    content = (
        "## Components\n\n| Name | Type |\n|---|---|\n| API | Process |\n\n"
        "## Trust Zones\n\nSome prose.\n"
    )
    assert parse_affected_assets(content) == {}


def test_prose_mention_of_affected_assets_is_not_a_block():
    """An inline 'affected assets' phrase (not an H2 heading) is ignored."""
    content = "The affected assets for this finding are documented elsewhere.\n"
    assert parse_affected_assets(content) == {}


# =============================================================================
# Empty-tags row -> [] (not [""], not missing)
# =============================================================================


def test_empty_tags_row_yields_empty_list():
    """``| S-1 | [] |`` parses to an empty list, not ``[""]`` or a missing key."""
    result = parse_affected_assets(_block("| S-1 | [] |"))
    assert result == {"S-1": []}
    assert result["S-1"] == []  # explicitly the empty list, never [""]


def test_empty_tags_row_present_alongside_populated_row():
    """An empty row keeps its key even when neighbouring rows carry tags."""
    result = parse_affected_assets(
        _block("| S-1 | [phi, pii] |", "| T-2 | [] |")
    )
    assert result == {"S-1": ["phi", "pii"], "T-2": []}


# =============================================================================
# Multi-tag row -> order preserved verbatim (NOT re-sorted)
# =============================================================================


def test_multi_tag_row_preserves_written_order():
    """Two tags are returned in written order: ``[phi, pii]`` -> ``["phi","pii"]``."""
    result = parse_affected_assets(_block("| S-2 | [phi, pii] |"))
    assert result == {"S-2": ["phi", "pii"]}


def test_extractor_does_not_resort_descending_input():
    """A deliberately non-ascending list is returned verbatim (extractor never sorts)."""
    # The populator emits ascending; were the extractor to re-sort, this
    # descending input would come back ascending. It must NOT.
    result = parse_affected_assets(_block("| I-3 | [secrets, pii, auth] |"))
    assert result == {"I-3": ["secrets", "pii", "auth"]}


def test_extractor_does_not_dedup():
    """Repeated tags survive verbatim — dedup is the populator's job, not the extractor's."""
    result = parse_affected_assets(_block("| D-4 | [pii, pii] |"))
    assert result == {"D-4": ["pii", "pii"]}


# =============================================================================
# Whitespace tolerance
# =============================================================================


@pytest.mark.parametrize(
    "row",
    [
        "| S-1 | [ phi , pii ] |",      # spaces inside brackets, around commas
        "|  S-1  |  [phi, pii]  |",     # padding around both pipe cells
        "|S-1|[phi, pii]|",             # no surrounding spaces at all
        "| S-1 |   [  phi ,pii ]   |",  # mixed irregular spacing
    ],
)
def test_whitespace_variants_parse_cleanly(row):
    """Extra spaces inside brackets / around pipe cells parse to the canonical list."""
    assert parse_affected_assets(_block(row)) == {"S-1": ["phi", "pii"]}


def test_leading_indentation_on_rows_tolerated():
    """A row with leading whitespace (``  | S-1 | ...``) still parses (rows are stripped)."""
    assert parse_affected_assets(_block("   | S-1 | [pii] |")) == {"S-1": ["pii"]}


# =============================================================================
# Markdown-bold tolerance in the finding-ID cell
# =============================================================================


def test_bold_finding_id_is_stripped():
    """``**S-3**`` in the ID cell strips its ``**`` markers to ``S-3``."""
    assert parse_affected_assets(_block("| **S-3** | [auth] |")) == {"S-3": ["auth"]}


def test_bold_markers_in_tag_cell_also_stripped():
    """``**`` anywhere in the assets cell is stripped before tag splitting."""
    assert parse_affected_assets(_block("| S-4 | [**auth**, pii] |")) == {
        "S-4": ["auth", "pii"]
    }


# =============================================================================
# Header + separator rows are skipped
# =============================================================================


def test_header_and_separator_never_become_keys():
    """The ``Finding ID`` header and ``|---|---|`` rule are excluded from the dict."""
    result = parse_affected_assets(
        _block("| S-1 | [pii] |", "| T-2 | [] |")
    )
    assert result == {"S-1": ["pii"], "T-2": []}
    # Spell out the negative: neither framing row leaked through.
    assert "Finding ID" not in result
    assert not any(set(key) <= {"-", ":"} for key in result)


def test_alternate_separator_widths_skipped():
    """A separator row of a different dash/colon width is still skipped, not keyed."""
    content = (
        "## Affected Assets\n\n"
        "| Finding ID | Affected Assets |\n"
        "|:---|:---:|\n"          # colon-aligned separator, different from canonical
        "| S-1 | [pii] |\n"
    )
    result = parse_affected_assets(content)
    assert result == {"S-1": ["pii"]}


def test_block_with_only_header_and_separator_yields_empty_dict():
    """A block with no data rows (header + separator only) -> {}."""
    content = (
        "## Affected Assets\n\n"
        "| Finding ID | Affected Assets |\n"
        "|------------|-----------------|\n"
    )
    assert parse_affected_assets(content) == {}


# =============================================================================
# Block boundary discipline
# =============================================================================


def test_block_stops_at_next_h2_heading():
    """Rows under a following ## section are not absorbed into the block."""
    content = (
        _block("| S-1 | [pii] |")
        + "\n## Baseline Delta\n\n| Finding ID | Status |\n|---|---|\n| X-9 | new |\n"
    )
    result = parse_affected_assets(content)
    assert result == {"S-1": ["pii"]}
    assert "X-9" not in result


def test_block_recovered_when_preceded_by_other_content():
    """The block is found even when it trails a large STRIDE table (real-world layout)."""
    content = (
        "# Threat Model\n\n"
        "## STRIDE Threats\n\n"
        "| ID | Threat |\n|---|---|\n| S-1 | Spoofing |\n| T-2 | Tampering |\n\n"
        + _block("| S-1 | [auth, pii] |", "| T-2 | [] |")
    )
    assert parse_affected_assets(content) == {
        "S-1": ["auth", "pii"],
        "T-2": [],
    }


# =============================================================================
# Round-trip with the real populator renderer (strongest assertion)
# =============================================================================


@pytest.mark.parametrize(
    "rows",
    [
        [("S-1", ["auth", "pii"]), ("T-2", [])],
        [("S-1", ["phi"]), ("I-3", []), ("D-4", ["financial", "safety", "secrets"])],
        [("AG-1", ["pii"]), ("LLM-2", []), ("OI-3", ["auth", "phi"])],
        [("S-1", [])],                      # single empty row
        [("S-1", list(_populator.VALID_ASSET_TAGS))],  # all six enum tags, sorted
    ],
)
def test_round_trip_reconstructs_rows(rows):
    """render -> parse rebuilds the exact ``{id: tags}`` mapping, ``[]`` rows included."""
    block = render_affected_assets_block(rows)
    parsed = parse_affected_assets(block)
    assert parsed == {finding_id: tags for finding_id, tags in rows}


def test_round_trip_preserves_empty_list_distinctly():
    """A ``[]`` row round-trips to ``[]`` (never dropped, never ``[""]``)."""
    block = render_affected_assets_block([("T-2", [])])
    parsed = parse_affected_assets(block)
    assert parsed == {"T-2": []}
    assert parsed["T-2"] == []


def test_round_trip_preserves_populator_sort_order():
    """The populator emits ascending tags; the extractor returns them unchanged."""
    # parse_component_asset_map already sorts, so a well-formed block is ascending.
    rows = [("S-9", ["auth", "financial", "pii", "secrets"])]
    block = render_affected_assets_block(rows)
    assert parse_affected_assets(block) == {"S-9": ["auth", "financial", "pii", "secrets"]}
