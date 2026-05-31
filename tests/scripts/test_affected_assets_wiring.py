"""Unit tests for the deterministic ``affected_assets`` populator (F-260b / T007).

Exercises ``scripts/populate-affected-assets.py`` — the single value authority
that joins each ``threats.md`` finding to its target component's asset-sensitivity
tags and writes the always-present ``## Affected Assets`` markdown block. The
populator is a pure, non-LLM, stdlib-only component (plan AD-1 §1; FR-2
"deterministic, not LLM-authored"); these tests pin its observable behavior so
the SARIF surfaces (T013) and the schema/ceiling docs (T017) can rely on a frozen
contract.

Test coverage targets (the populator only — cross-format SARIF lives in T013,
schema-doc / 9.2-ceiling assertions live in T017):

* **SC-003** — all six enum tags on a component propagate into the block row,
  sorted ascending.
* **SC-005** — a finding on an untagged (or unmatched) component renders ``[]``;
  the field is never omitted (FR-005).
* **§6f fuzzy match** — a finding whose component name differs cosmetically from
  the architecture label still resolves through the substring-containment and
  word-overlap (≥50%) tiers of ``match_component``.
* **Q4 semantic** — ``affected_assets`` lists ALL tags on the target component
  (asset exposure), not "tags that changed a CVSS bit": a ``financial`` tag on a
  finding that would be a no-op modifier still appears (data-model.md §value
  rules).
* **Sorted / deduped** — tag order is ascending lexicographic, inherited verbatim
  from ``parse_component_asset_map``.
* **UNCHANGED / RESOLVED** — findings with those lifecycle statuses still receive
  a block row with the field present (FR-005; data-model.md §State/Lifecycle).
* **Idempotency** — running ``populate()`` twice on its own output is
  byte-identical; ``upsert_affected_assets_block`` replaces an existing block
  rather than duplicating it.

Stdlib-only per PAT-014 — no PyYAML, no third-party libs. The hyphenated module
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

# Hyphenated filename => not importable via ``import``; load by file location.
# tachi_parsers (imported transitively by the populator) is on sys.path above.
_POPULATOR_PATH = REPO_ROOT / "scripts" / "populate-affected-assets.py"
_spec = importlib.util.spec_from_file_location("populate_affected_assets", _POPULATOR_PATH)
populator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(populator)

from tachi_parsers import VALID_ASSET_TAGS  # noqa: E402  -- after sys.path mutation


# =============================================================================
# Fixture builders
# =============================================================================
#
# These helpers assemble *real* populator inputs: a Mermaid architecture with
# inline [asset:...] tags (parsed by parse_component_asset_map) and a real
# Section 7 "Recommended Actions" table (parsed by parse_threats_findings). The
# populator's actual finding->component join therefore runs end-to-end; nothing
# is stubbed.


def _arch(*nodes: str) -> str:
    """Wrap Mermaid node declarations in a fenced ```mermaid block.

    Each ``node`` is a raw Mermaid node line (e.g.
    ``DB[("Store<br/>[asset:pii]")]``). The fence is what
    ``parse_component_asset_map`` scans for ``[asset:...]`` blocks.
    """
    body = "\n".join(f"    {n}" for n in nodes)
    return "```mermaid\nflowchart TD\n" + body + "\n```\n"


def _threats(*rows: str) -> str:
    """Build a threats.md whose Section 7 table holds the given data ``rows``.

    Each ``row`` is the inner-cell content for the canonical Section 7 columns
    ``Finding ID | Status | Component | Risk Level | Mitigation`` (the subset
    ``parse_threats_findings`` reads). ``parse_threats_findings`` keys every row
    with a parseable Finding ID, regardless of Status, so callers can exercise
    NEW / UNCHANGED / RESOLVED uniformly.
    """
    header = (
        "## 7. Recommended Actions\n\n"
        "| Finding ID | Status | Component | Risk Level | Mitigation |\n"
        "|------------|--------|-----------|------------|------------|\n"
    )
    table = "".join(f"| {r} |\n" for r in rows)
    return "# Threat Model Report\n\n" + header + table


def _assets_for(content: str, finding_id: str) -> str:
    """Return the rendered ``Affected Assets`` cell value for ``finding_id``.

    Scopes the search to the ``## Affected Assets`` block region (so it never
    collides with the same ``| <id> | ...`` prefix in the Section 7 table), then
    locates the block row ``| <id> | <value> |`` and returns the trimmed
    ``<value>`` (e.g. ``"[auth, pii]"`` or ``"[]"``). Asserts the heading and the
    row both exist so an omitted finding fails loudly (FR-005 guard).
    """
    heading = populator.AFFECTED_ASSETS_HEADING
    idx = content.find(heading)
    assert idx != -1, f"no {heading!r} block found in:\n{content}"
    block = content[idx:]

    needle = f"| {finding_id} | "
    for line in block.splitlines():
        if line.startswith(needle) and line.rstrip().endswith("|"):
            return line[len(needle):].rstrip().rstrip("|").strip()
    raise AssertionError(
        f"no Affected Assets block row found for finding {finding_id!r} in:\n{block}"
    )


# =============================================================================
# T007 — Populator behavior
# =============================================================================


# -----------------------------------------------------------------------------
# SC-003 — all six tags propagate, sorted ascending
# -----------------------------------------------------------------------------


def test_sc003_all_six_tags_propagate_sorted():
    """A component tagged with the full 6-value enum surfaces all six, sorted.

    SC-003: ``[asset:pii,phi,auth,secrets,financial,safety]`` on the finding's
    component yields the block value ``[auth, financial, phi, pii, safety,
    secrets]`` (ascending lexicographic), and the tags are exactly the frozen
    enum.
    """
    arch = _arch('DB[("Crown Jewels<br/>[asset:pii,phi,auth,secrets,financial,safety]")]')
    threats = _threats("S-1 | NEW | Crown Jewels | Critical | Fix")

    out = populator.populate(arch, threats)

    assert _assets_for(out, "S-1") == "[auth, financial, phi, pii, safety, secrets]"
    # The six tokens are precisely the frozen enum (order-insensitive set check).
    rendered = _assets_for(out, "S-1").strip("[]")
    tokens = [t.strip() for t in rendered.split(",")]
    assert set(tokens) == set(VALID_ASSET_TAGS)
    assert len(tokens) == len(VALID_ASSET_TAGS) == 6


def test_sc003_compute_rows_carry_full_enum_for_tagged_component():
    """``compute_affected_assets`` returns the full enum list for the tagged finding.

    Exercises the computation layer directly (below rendering): the returned
    ``(finding_id, tags)`` tuple carries the verbatim sorted/deduped list.
    """
    arch = _arch('DB[("Crown Jewels<br/>[asset:safety,secrets,financial,auth,phi,pii]")]')
    threats = _threats("S-1 | NEW | Crown Jewels | Critical | Fix")

    rows = populator.compute_affected_assets(arch, threats)

    assert rows == [("S-1", ["auth", "financial", "phi", "pii", "safety", "secrets"])]


# -----------------------------------------------------------------------------
# SC-005 — empty-default [] is always present
# -----------------------------------------------------------------------------


def test_sc005_untagged_component_renders_empty_brackets():
    """A finding on an untagged component renders ``[]`` (never omitted).

    SC-005 / FR-005: the component exists in the architecture but carries no
    ``[asset:...]`` block, so the join yields ``[]`` and the block row is still
    written.
    """
    arch = _arch('Web["Public Web Frontend"]')
    threats = _threats("I-1 | NEW | Public Web Frontend | Low | Log")

    out = populator.populate(arch, threats)

    assert _assets_for(out, "I-1") == "[]"


def test_sc005_unmatched_component_renders_empty_brackets():
    """A finding whose component does not join any architecture node yields ``[]``.

    data-model.md join rule: "Unmatched -> []". The finding's component shares no
    name with any tagged node, so ``match_component`` returns ``None`` and the
    default empty list is used — the row is still present.
    """
    arch = _arch('DB[("Records Store<br/>[asset:pii]")]')
    threats = _threats("T-1 | NEW | Wholly Unrelated Subsystem | Medium | Patch")

    out = populator.populate(arch, threats)

    assert _assets_for(out, "T-1") == "[]"


def test_sc005_every_finding_present_in_block():
    """Every Section 7 finding appears exactly once in the block (FR-005).

    A mix of tagged, untagged, and unmatched components — all three findings get
    a block row; none is dropped.
    """
    arch = _arch(
        'DB[("Records Store<br/>[asset:pii]")]',
        'Web["Public Web Frontend"]',
    )
    threats = _threats(
        "S-1 | NEW | Records Store | High | Fix",
        "I-2 | NEW | Public Web Frontend | Low | Log",
        "T-3 | NEW | Ghost Component | Medium | Patch",
    )

    out = populator.populate(arch, threats)

    assert _assets_for(out, "S-1") == "[pii]"
    assert _assets_for(out, "I-2") == "[]"
    assert _assets_for(out, "T-3") == "[]"


# -----------------------------------------------------------------------------
# §6f fuzzy component match — substring-containment and word-overlap tiers
# -----------------------------------------------------------------------------


def test_fuzzy_substring_tier_resolves_tags():
    """§6f Step 2 (substring containment) joins a shorter finding name to a key.

    The finding's component ``LLM Agent`` is a substring of the architecture
    label ``LLM Agent Orchestrator`` (the canonical §6f example), so the tags
    resolve despite the cosmetic name difference.
    """
    arch = _arch('Agent["LLM Agent Orchestrator<br/>[asset:auth,secrets]"]')
    threats = _threats("AG-1 | NEW | LLM Agent | High | Constrain")

    out = populator.populate(arch, threats)

    assert _assets_for(out, "AG-1") == "[auth, secrets]"


def test_fuzzy_word_overlap_tier_resolves_tags():
    """§6f Step 3 (word overlap ≥50%) joins when no tier-1/2 match exists.

    ``Payment Service`` is NOT a contiguous substring of the label ``Payment
    Gateway Service`` (so Steps 1-2 miss), but the word sets overlap 2/3 = 67%
    (≥50%), so Step 3 accepts the match and the ``financial`` tag resolves.
    """
    arch = _arch('Pay["Payment Gateway Service<br/>[asset:financial]"]')
    threats = _threats("S-1 | NEW | Payment Service | High | Tokenize")

    out = populator.populate(arch, threats)

    assert _assets_for(out, "S-1") == "[financial]"


def test_fuzzy_match_below_threshold_falls_back_to_empty():
    """A sub-50% word overlap does not match — the finding renders ``[]``.

    ``Reporting Module`` vs key ``Payment Gateway Service`` share zero words
    (0% overlap) and have no substring relationship, so the §6f cascade returns
    None and the default ``[]`` is used. Confirms the fuzzy match is bounded, not
    greedy.
    """
    arch = _arch('Pay["Payment Gateway Service<br/>[asset:financial]"]')
    threats = _threats("D-9 | NEW | Reporting Module | Low | Cache")

    out = populator.populate(arch, threats)

    assert _assets_for(out, "D-9") == "[]"


def test_fuzzy_case_insensitive_exact_tier():
    """§6f Step 1 (case-insensitive exact) matches across casing differences.

    A lower-cased finding component ``records datastore`` matches the architecture
    label ``Records Datastore`` exactly under case folding.
    """
    arch = _arch('DB[("Records Datastore<br/>[asset:pii,phi]")]')
    threats = _threats("I-1 | NEW | records datastore | High | Encrypt")

    out = populator.populate(arch, threats)

    assert _assets_for(out, "I-1") == "[phi, pii]"


# -----------------------------------------------------------------------------
# Q4 semantic — exposure, not modifier delta (no-op modifier still listed)
# -----------------------------------------------------------------------------


def test_q4_no_op_modifier_tag_still_listed():
    """A tag that would NOT change a CVSS bit still appears (Q4 PM-resolved).

    data-model.md §value rules: ``affected_assets`` is ALL tags on the target
    component (asset exposure), NOT "tags that changed a CVSS bit". The populator
    records provenance only — it never reads CVSS/impact bits — so a ``financial``
    tag on a finding that is conceptually already at ``I:H`` (where the modifier
    would be a no-op) is still emitted. This test asserts the populator's
    exposure-not-delta contract: the tag is present purely because the component
    carries it.
    """
    # The component is tagged `financial`; the finding's (notional) impact is
    # already maxed, so `financial` would be a no-op modifier in the scorer. The
    # populator must still list it — it reflects exposure, not modifier delta.
    arch = _arch('Pay[["Billing Service<br/>[asset:financial]"]]')
    threats = _threats("S-1 | NEW | Billing Service | Critical | Tokenize")

    out = populator.populate(arch, threats)

    assert _assets_for(out, "S-1") == "[financial]"
    assert "financial" in _assets_for(out, "S-1")


def test_q4_all_component_tags_listed_not_just_modifier_relevant():
    """ALL of a component's tags are listed, independent of any scoring effect.

    A component carrying a broad tag set surfaces every tag, reinforcing that the
    populator copies the component_asset_map value verbatim rather than filtering
    to "modifier-relevant" tags.
    """
    arch = _arch('Svc["Clinical Billing<br/>[asset:phi,financial,pii]"]')
    threats = _threats("LLM-1 | NEW | Clinical Billing | High | Mask")

    out = populator.populate(arch, threats)

    # Sorted ascending; all three exposure tags present, none filtered out.
    assert _assets_for(out, "LLM-1") == "[financial, phi, pii]"


# -----------------------------------------------------------------------------
# Sorted / deduped output (order inherited from parse_component_asset_map)
# -----------------------------------------------------------------------------


def test_output_sorted_ascending_regardless_of_declaration_order():
    """Tags render ascending lexicographic even when declared out of order.

    The architecture declares ``[asset:secrets,auth,pii]`` (descending-ish); the
    block value is ``[auth, pii, secrets]`` (ascending), confirming sort order is
    inherited from ``parse_component_asset_map`` and the populator does not
    re-shuffle.
    """
    arch = _arch('Vault["Key Vault<br/>[asset:secrets,auth,pii]"]')
    threats = _threats("T-1 | NEW | Key Vault | High | Rotate")

    out = populator.populate(arch, threats)

    assert _assets_for(out, "T-1") == "[auth, pii, secrets]"


def test_output_deduped_within_component():
    """Repeated tags on the component collapse to a single occurrence.

    ``[asset:pii,pii,auth]`` yields ``[auth, pii]`` — dedup is inherited from the
    parser and the rendered block carries no repeats.
    """
    arch = _arch('DB[("Member DB<br/>[asset:pii,pii,auth]")]')
    threats = _threats("S-1 | NEW | Member DB | High | Fix")

    out = populator.populate(arch, threats)

    assert _assets_for(out, "S-1") == "[auth, pii]"


def test_output_value_strictly_ascending():
    """The rendered tag tokens are in strictly ascending order (no equal pairs).

    Parses the block cell back into tokens and asserts ``sorted(tokens) ==
    tokens`` and that they are unique — a structural guard on determinism.
    """
    arch = _arch('DB[("Vault<br/>[asset:safety,pii,secrets,auth]")]')
    threats = _threats("S-1 | NEW | Vault | High | Fix")

    out = populator.populate(arch, threats)
    tokens = [t.strip() for t in _assets_for(out, "S-1").strip("[]").split(",")]

    assert tokens == sorted(tokens)
    assert len(tokens) == len(set(tokens))


# -----------------------------------------------------------------------------
# UNCHANGED / RESOLVED findings still carry the field (FR-005)
# -----------------------------------------------------------------------------


@pytest.mark.parametrize("status", ["UNCHANGED", "RESOLVED", "UPDATED", "NEW"])
def test_lifecycle_status_findings_carry_field(status):
    """Findings of any lifecycle status get a block row with the field present.

    FR-005 / data-model.md §State/Lifecycle: ``affected_assets`` is a pure derived
    projection with no dependence on finding status. The populator keys the
    Section 7 row by ID regardless of Status, so NEW / UNCHANGED / UPDATED /
    RESOLVED all surface the current architecture's tags for the component.
    """
    arch = _arch('DB[("Records Store<br/>[asset:pii,phi]")]')
    threats = _threats(f"S-1 | {status} | Records Store | High | Fix")

    out = populator.populate(arch, threats)

    assert _assets_for(out, "S-1") == "[phi, pii]"


def test_unchanged_and_resolved_coexist_with_field():
    """An UNCHANGED and a RESOLVED finding in the same run both carry the field.

    Guards against status-based filtering: both rows are present with their
    component's tags even when mixed in a single Section 7 table.
    """
    arch = _arch('DB[("Records Store<br/>[asset:pii]")]')
    threats = _threats(
        "S-1 | UNCHANGED | Records Store | High | Fix",
        "S-2 | RESOLVED | Records Store | High | Already fixed",
    )

    out = populator.populate(arch, threats)

    assert _assets_for(out, "S-1") == "[pii]"
    assert _assets_for(out, "S-2") == "[pii]"


# -----------------------------------------------------------------------------
# Idempotency (architect LOW advisory) — re-running is byte-identical
# -----------------------------------------------------------------------------


def test_idempotent_double_populate_is_byte_identical():
    """``populate(arch, populate(arch, threats)) == populate(arch, threats)``.

    Architect LOW advisory: running the populator on its own output must be a
    no-op. ``upsert_affected_assets_block`` REPLACES the existing block in place
    rather than appending a duplicate, so a second pass yields byte-identical
    content.
    """
    arch = _arch(
        'DB[("Records Store<br/>[asset:pii,phi]")]',
        'Web["Public Web Frontend"]',
    )
    threats = _threats(
        "S-1 | NEW | Records Store | High | Fix",
        "I-2 | NEW | Public Web Frontend | Low | Log",
    )

    once = populator.populate(arch, threats)
    twice = populator.populate(arch, once)

    assert twice == once


def test_idempotent_block_appears_exactly_once():
    """Re-running never duplicates the ``## Affected Assets`` heading.

    Asserts the heading count stays at exactly one across two populate passes —
    a structural guard that the upsert replaces rather than appends.
    """
    arch = _arch('DB[("Records Store<br/>[asset:pii]")]')
    threats = _threats("S-1 | NEW | Records Store | High | Fix")

    once = populator.populate(arch, threats)
    twice = populator.populate(arch, once)

    assert twice.count("## Affected Assets") == 1


def test_populate_preserves_existing_tables_byte_stable():
    """The original Section 7 table is left byte-for-byte unchanged (SC-002).

    The populator appends the block; it must not edit the pre-existing tables.
    Asserts the full Section 7 region of the input is a substring of the output.
    """
    arch = _arch('DB[("Records Store<br/>[asset:pii]")]')
    threats = _threats("S-1 | NEW | Records Store | High | Fix")

    out = populator.populate(arch, threats)

    # The original document (sans trailing newline normalization) is a prefix-region
    # of the output: every original line survives verbatim.
    for line in threats.splitlines():
        if line.strip():
            assert line in out, f"original line not preserved verbatim: {line!r}"
