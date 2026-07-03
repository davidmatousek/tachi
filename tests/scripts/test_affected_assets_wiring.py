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


# =============================================================================
# ===== SC-006 cross-format equality (T013) =====
# =============================================================================
#
# The single most important correctness invariant of F-260b (NFR-3). Enforces
# the affected-assets-contract §3 + §4 equality table: for EVERY finding ID
# (including untagged ``[]``), the value rendered in the threats.md
# ``## Affected Assets`` block is byte-identical to the value emitted in
# ``threats.sarif`` AND ``risk-scores.sarif`` ``result.properties.affected_assets``
# — same elements, same order — and the literal property key is exactly
# ``affected_assets`` (snake_case) in BOTH SARIF surfaces.
#
# This section replicates the PRODUCTION sequence verbatim: populate (the single
# deterministic value authority) → THEN emit each SARIF surface, with both
# generators sourcing the value from the shared
# ``sarif_common.parse_affected_assets`` extractor (NOT re-derived from
# ``component_asset_map``). The threats-sarif path calls the generator's
# ``build_sarif`` exactly as its ``main()`` does; the risk-scores path calls the
# generator's ``build_result`` per finding exactly as its ``main()`` does
# (``generate-risk-scores-sarif.py::main`` is path-hardcoded with an >=80-finding
# production guard, so the worked example invokes the result-builder directly —
# the same code path that emits ``properties.affected_assets``).
#
# Hyphenated generator filenames are not importable by name; loaded via
# ``importlib.util.spec_from_file_location`` (the same precedent the module
# header uses for the populator).

import json  # noqa: E402  -- stdlib; cross-format SARIF surfaces are JSON

from sarif_common import parse_affected_assets  # noqa: E402  -- shared value extractor


def _load_script_module(filename: str, modname: str):
    """Load a hyphenated ``scripts/<filename>`` module by file location.

    The generator filenames (``generate-threats-sarif.py``,
    ``generate-risk-scores-sarif.py``) contain hyphens and so are not importable
    via ``import``; this mirrors the module-header populator loader. ``scripts/``
    is already on ``sys.path`` (module header), so each generator's own
    ``from sarif_common import ...`` / ``from tachi_parsers import ...`` resolve.
    """
    path = REPO_ROOT / "scripts" / filename
    spec = importlib.util.spec_from_file_location(modname, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_gen_threats = _load_script_module("generate-threats-sarif.py", "generate_threats_sarif")
_gen_risk = _load_script_module("generate-risk-scores-sarif.py", "generate_risk_scores_sarif")


# -----------------------------------------------------------------------------
# Cross-format worked-example fixture builders
# -----------------------------------------------------------------------------
#
# The populator reads the Section 7 table (parse_threats_findings); the
# threats-sarif generator reads the Section 3 STRIDE table (its own
# parse_findings, which requires the "## 3. STRIDE Threat Tables" .. "## 5."
# boundaries and 10-column rows with a bracketed [STATUS]). A single cross-format
# threats.md must therefore carry BOTH tables, keyed on the same finding IDs and
# components, so that one populate→emit pass feeds all three surfaces from one
# document. ``_arch`` (T007) is reused verbatim for the architecture input.


def _xfmt_stride_row(fid: str, component: str, status: str = "NEW") -> str:
    """One 10-column Section 3 STRIDE row (the shape generator.parse_findings reads).

    Columns: ``Finding ID | [STATUS] | Component | MAESTRO | Pattern | Threat |
    Likelihood | Impact | Risk Level | Mitigation`` — exactly the 10 fields
    ``generate-threats-sarif.py::parse_findings`` unpacks for a STRIDE prefix.
    """
    return (
        f"| {fid} | [{status}] | {component} | L7 — Agent Ecosystem | — | "
        f"Threat narrative for {fid} | HIGH | HIGH | High | Mitigation for {fid} |"
    )


def _xfmt_section7_row(fid: str, component: str, status: str = "NEW") -> str:
    """One Section 7 Recommended Actions row (the shape the populator reads).

    Columns: ``Finding ID | Status | Component | Threat | Risk Level |
    Mitigation`` — ``parse_threats_findings`` keys by column name, so this subset
    joins the same ``fid``/``component`` the STRIDE row above declares.
    """
    return (
        f"| {fid} | [{status}] | {component} | Threat narrative for {fid} | "
        f"High | Mitigation for {fid} |"
    )


def _xfmt_threats(findings: "list[tuple[str, str]]") -> str:
    """Assemble a cross-format threats.md from ``(finding_id, component)`` pairs.

    Emits Section 1 (Components), Section 3 (STRIDE table — read by the
    threats-sarif generator), Section 5 (boundary marker the generator requires),
    and Section 7 (Recommended Actions — read by the populator). Every finding
    appears in BOTH the Section 3 and Section 7 tables so the populator and the
    threats-sarif generator key on an identical finding set.
    """
    components = []
    seen = set()
    for _fid, comp in findings:
        if comp not in seen:
            seen.add(comp)
            components.append(comp)

    comp_table = (
        "## 1. Components\n\n"
        "| Name | Type |\n"
        "|------|------|\n"
        + "".join(f"| {c} | Process |\n" for c in components)
    )

    stride = (
        "## 3. STRIDE Threat Tables\n\n"
        "| Finding ID | Status | Component | MAESTRO Layer | Agentic Pattern | "
        "Threat | Likelihood | Impact | Risk Level | Mitigation |\n"
        "|---|---|---|---|---|---|---|---|---|---|\n"
        + "".join(_xfmt_stride_row(fid, comp) + "\n" for fid, comp in findings)
    )

    # Section 5 boundary marker — parse_findings slices Section 3 .. Section 5.
    coverage = "## 5. Coverage Matrix\n\nCoverage details elided for the fixture.\n"

    section7 = (
        "## 7. Recommended Actions\n\n"
        "| Finding ID | Status | Component | Threat | Risk Level | Mitigation |\n"
        "|---|---|---|---|---|---|\n"
        + "".join(_xfmt_section7_row(fid, comp) + "\n" for fid, comp in findings)
    )

    return (
        "# Threat Model Report\n\n"
        + comp_table
        + "\n"
        + stride
        + "\n"
        + coverage
        + "\n"
        + section7
    )


def _threats_sarif_assets_by_id(populated_threats_md: str) -> dict:
    """Emit threats.sarif from the populated threats.md and return id→assets.

    Replicates ``generate-threats-sarif.py::main`` exactly: parse component
    metadata, parse the shared ``affected_assets`` block, parse Section 3/4
    findings, then ``build_sarif``. Returns the per-result
    ``properties.affected_assets`` keyed by finding ID (``findingId/v1``
    fingerprint) — and, importantly, asserts the literal snake_case key is
    present in each result's raw ``properties`` dict (contract §3 key-string
    identity, architect LOW advisory).
    """
    md_path = _write_threats(populated_threats_md, "threats-xfmt.md")
    component_meta = _gen_threats.parse_component_metadata(populated_threats_md)
    affected_by_id = parse_affected_assets(populated_threats_md)
    findings = _gen_threats.parse_findings(md_path)
    sarif = _gen_threats.build_sarif(findings, component_meta, affected_by_id)

    out: dict = {}
    for result in sarif["runs"][0]["results"]:
        props = result["properties"]
        # Key-string identity: the literal snake_case key MUST be present (not
        # ``affected-assets`` / ``affectedAssets``). Inspect the raw dict keys.
        assert "affected_assets" in props, (
            "threats.sarif result.properties missing literal 'affected_assets' key; "
            f"keys present: {sorted(props)}"
        )
        assert "affected-assets" not in props and "affectedAssets" not in props, (
            "threats.sarif adopted kebab/camel key-casing drift for affected_assets"
        )
        fid = result["partialFingerprints"]["findingId/v1"]
        out[fid] = props["affected_assets"]
    return out


def _risk_scores_sarif_assets_by_id(populated_threats_md: str, findings: list) -> dict:
    """Emit risk-scores.sarif results from the populated threats.md; return id→assets.

    ``generate-risk-scores-sarif.py::main`` is path-hardcoded (reads a fixed
    ``examples/...`` risk-scores.md + threats.md) and guards on >=80 findings, so
    the worked example invokes the generator's ``build_result`` directly — the
    same call ``main`` makes per finding, sourcing ``affected_assets_by_id`` from
    the SAME shared ``parse_affected_assets`` extractor. This exercises the real
    ``properties.affected_assets`` emission path on the risk-scores surface.

    ``findings`` is the ordered ``[(finding_id, component)]`` worked-example list;
    each is shaped into the minimal Section-2 finding dict ``build_result``
    consumes (scoring fields are placeholders — they do not affect the
    affected_assets value, which is copied verbatim from the extractor).
    """
    affected_by_id = parse_affected_assets(populated_threats_md)
    component_meta = _gen_risk.parse_component_metadata(populated_threats_md)
    threats_status = _gen_risk.parse_threats_status(populated_threats_md)
    threats_full = _gen_risk.parse_threats_full_text(populated_threats_md)
    source_attribution = _gen_risk.parse_source_attribution(populated_threats_md)

    out: dict = {}
    for fid, component in findings:
        finding = {
            "id": fid,
            "component": component,
            "threat_summary": f"Threat narrative for {fid}",
            "cvss_base": 7.0,
            "exploitability": 7.0,
            "scalability": 7.0,
            "reachability": 7.0,
            "composite": 7.0,
            "severity_band": "High",
            "sla_days": "30",
            "disposition": "Open",
        }
        result = _gen_risk.build_result(
            finding,
            {},  # s3 (Section 3 dimensional breakdown) — absent in the fixture
            {},  # s4 (Section 4 governance) — absent in the fixture
            threats_status,
            threats_full,
            source_attribution,
            component_meta,
            affected_by_id,
        )
        props = result["properties"]
        # Key-string identity on the risk-scores surface too (contract §3).
        assert "affected_assets" in props, (
            "risk-scores.sarif result.properties missing literal 'affected_assets' "
            f"key; keys present: {sorted(props)}"
        )
        assert "affected-assets" not in props and "affectedAssets" not in props, (
            "risk-scores.sarif adopted kebab/camel key-casing drift for affected_assets"
        )
        out[result["partialFingerprints"]["findingId/v1"]] = props["affected_assets"]
    return out


# ``tmp_path``-scoped writer — every generated artifact lives under the test's
# temporary directory; nothing is written into ``examples/`` or committed. Set by
# the fixture-driven tests below before calling the SARIF emitters.
_TMP_DIR: Path | None = None


def _write_threats(content: str, name: str) -> Path:
    """Write ``content`` to ``_TMP_DIR/name`` and return the path (tmp-scoped)."""
    assert _TMP_DIR is not None, "_TMP_DIR not set — call inside a tmp_path test"
    path = _TMP_DIR / name
    path.write_text(content, encoding="utf-8")
    return path


# -----------------------------------------------------------------------------
# SC-006 — per-finding cross-format equality table (the core invariant)
# -----------------------------------------------------------------------------


def test_sc006_cross_format_equality_table(tmp_path):
    """block == threats.sarif == risk-scores.sarif for EVERY finding (incl. ``[]``).

    SC-006 / contract §3+§4 (NFR-3): a multi-finding worked example with two
    differently-tagged components (one ``[asset:phi,pii]``, one ``[asset:auth]``)
    plus an untagged component. Runs the PRODUCTION sequence — populate THEN emit
    both SARIF surfaces — and asserts the per-finding equality table:

        block[id] == threats_sarif[id] == risk_scores_sarif[id]

    for every finding ID, with the untagged-component finding yielding ``[]`` in
    all three surfaces (present, not missing), and identical element order (no
    re-sort / dedup divergence between surfaces).
    """
    global _TMP_DIR
    _TMP_DIR = tmp_path

    # Two differently-tagged components + one untagged component.
    arch = _arch(
        'DB[("Records Store<br/>[asset:phi,pii]")]',
        'Auth["Auth Service<br/>[asset:auth]"]',
        'Web["Public Web Frontend"]',  # untagged → must yield []
    )
    # >=1 finding per component, including an untagged-component finding ([]).
    worked = [
        ("S-1", "Records Store"),     # → [phi, pii]
        ("I-2", "Records Store"),     # → [phi, pii] (second finding, same tagged comp)
        ("S-3", "Auth Service"),      # → [auth]
        ("I-4", "Public Web Frontend"),  # → []  (untagged component)
    ]
    raw_threats = _xfmt_threats(worked)

    # Production step 1: populate (the single deterministic value authority).
    populated = populator.populate(arch, raw_threats)
    # The block must now be present and carry every worked-example finding.
    block = parse_affected_assets(populated)

    # Production step 2: emit BOTH SARIF surfaces from the SAME populated doc.
    threats_sarif = _threats_sarif_assets_by_id(populated)
    risk_sarif = _risk_scores_sarif_assets_by_id(populated, worked)

    expected = {
        "S-1": ["phi", "pii"],
        "I-2": ["phi", "pii"],
        "S-3": ["auth"],
        "I-4": [],  # untagged component → present-with-default empty list
    }

    for fid, want in expected.items():
        # Every finding present in all three surfaces (FR-005: never omitted).
        assert fid in block, f"{fid} missing from threats.md block"
        assert fid in threats_sarif, f"{fid} missing from threats.sarif results"
        assert fid in risk_sarif, f"{fid} missing from risk-scores.sarif results"

        # The equality table: same elements, same order across all three.
        assert block[fid] == want, f"block[{fid}] = {block[fid]!r}, want {want!r}"
        assert threats_sarif[fid] == block[fid], (
            f"threats.sarif[{fid}] = {threats_sarif[fid]!r} != block {block[fid]!r}"
        )
        assert risk_sarif[fid] == block[fid], (
            f"risk-scores.sarif[{fid}] = {risk_sarif[fid]!r} != block {block[fid]!r}"
        )
        # Spell out the three-way identity explicitly (no re-sort/dedup drift).
        assert block[fid] == threats_sarif[fid] == risk_sarif[fid]

    # The untagged finding is the [] one in all three surfaces — present, empty.
    assert block["I-4"] == [] and threats_sarif["I-4"] == [] and risk_sarif["I-4"] == []


def test_sc006_untagged_finding_is_present_not_missing(tmp_path):
    """The untagged-component finding emits ``[]`` (present) on every surface.

    FR-005 guard, isolated: a finding on an untagged component must surface as
    ``"affected_assets": []`` in the block and BOTH SARIF surfaces — never an
    omitted key. Asserts membership before value so an omission fails loudly.
    """
    global _TMP_DIR
    _TMP_DIR = tmp_path

    arch = _arch(
        'DB[("Records Store<br/>[asset:pii]")]',
        'Web["Public Web Frontend"]',  # untagged
    )
    worked = [
        ("S-1", "Records Store"),         # → [pii]
        ("I-2", "Public Web Frontend"),   # → []
    ]
    populated = populator.populate(arch, _xfmt_threats(worked))

    block = parse_affected_assets(populated)
    threats_sarif = _threats_sarif_assets_by_id(populated)
    risk_sarif = _risk_scores_sarif_assets_by_id(populated, worked)

    for surface_name, surface in (
        ("block", block),
        ("threats.sarif", threats_sarif),
        ("risk-scores.sarif", risk_sarif),
    ):
        assert "I-2" in surface, f"untagged finding I-2 omitted from {surface_name}"
        assert surface["I-2"] == [], f"{surface_name}[I-2] = {surface['I-2']!r}, want []"
        # And the tagged finding still carries its tag on the same surface.
        assert surface["S-1"] == ["pii"], f"{surface_name}[S-1] = {surface['S-1']!r}"


def test_sc006_key_string_is_snake_case_in_both_sarif_surfaces(tmp_path):
    """The literal property key is exactly ``affected_assets`` in BOTH emitters.

    Contract §3 key-string identity (architect LOW advisory): inspect the RAW
    ``result.properties`` dict keys (not just the value) of both ``threats.sarif``
    and ``risk-scores.sarif`` and assert the snake_case ``affected_assets`` key is
    present and that the kebab (``affected-assets``) / camel (``affectedAssets``)
    variants are absent — for every result, including the untagged ``[]`` one.

    This re-runs the emitters and re-asserts the key on the raw envelopes here so
    the key-string check is a first-class test, not only an internal helper guard.
    """
    global _TMP_DIR
    _TMP_DIR = tmp_path

    arch = _arch(
        'DB[("Records Store<br/>[asset:phi,pii]")]',
        'Web["Public Web Frontend"]',  # untagged → [] result must still carry the key
    )
    worked = [
        ("S-1", "Records Store"),
        ("I-2", "Public Web Frontend"),
    ]
    populated = populator.populate(arch, _xfmt_threats(worked))

    # threats.sarif — inspect the raw envelope's result.properties keys.
    md_path = _write_threats(populated, "threats-keycheck.md")
    component_meta = _gen_threats.parse_component_metadata(populated)
    affected_by_id = parse_affected_assets(populated)
    t_findings = _gen_threats.parse_findings(md_path)
    threats_sarif = _gen_threats.build_sarif(t_findings, component_meta, affected_by_id)

    t_results = threats_sarif["runs"][0]["results"]
    assert t_results, "threats.sarif produced no results for the worked example"
    for result in t_results:
        keys = set(result["properties"].keys())
        assert "affected_assets" in keys, (
            f"threats.sarif result missing snake_case key; keys: {sorted(keys)}"
        )
        assert "affected-assets" not in keys, "threats.sarif used kebab-case key"
        assert "affectedAssets" not in keys, "threats.sarif used camelCase key"

    # risk-scores.sarif — build a result directly and inspect its raw properties.
    risk_status = _gen_risk.parse_threats_status(populated)
    risk_full = _gen_risk.parse_threats_full_text(populated)
    risk_attr = _gen_risk.parse_source_attribution(populated)
    risk_meta = _gen_risk.parse_component_metadata(populated)

    seen_results = 0
    for fid, component in worked:
        finding = {
            "id": fid,
            "component": component,
            "threat_summary": f"Threat narrative for {fid}",
            "cvss_base": 7.0,
            "exploitability": 7.0,
            "scalability": 7.0,
            "reachability": 7.0,
            "composite": 7.0,
            "severity_band": "High",
            "sla_days": "30",
            "disposition": "Open",
        }
        result = _gen_risk.build_result(
            finding, {}, {}, risk_status, risk_full, risk_attr, risk_meta, affected_by_id
        )
        keys = set(result["properties"].keys())
        assert "affected_assets" in keys, (
            f"risk-scores.sarif result missing snake_case key; keys: {sorted(keys)}"
        )
        assert "affected-assets" not in keys, "risk-scores.sarif used kebab-case key"
        assert "affectedAssets" not in keys, "risk-scores.sarif used camelCase key"
        seen_results += 1
    assert seen_results == len(worked)


def test_sc006_emitted_sarif_serializes_to_valid_json(tmp_path):
    """Both emitted SARIF envelopes round-trip through JSON with the field intact.

    Structural guard mirroring the production write step (both generators write
    ``json.dumps(sarif, indent=2)``): serialize each envelope and re-parse it,
    confirming the snake_case ``affected_assets`` value survives JSON encoding
    byte-for-byte (same list, same order) on both surfaces. Written under
    ``tmp_path`` only.
    """
    global _TMP_DIR
    _TMP_DIR = tmp_path

    arch = _arch(
        'DB[("Records Store<br/>[asset:auth,phi,pii]")]',
        'Web["Public Web Frontend"]',
    )
    worked = [("S-1", "Records Store"), ("I-2", "Public Web Frontend")]
    populated = populator.populate(arch, _xfmt_threats(worked))
    affected_by_id = parse_affected_assets(populated)

    # threats.sarif → JSON file → re-parse.
    md_path = _write_threats(populated, "threats-json.md")
    t_findings = _gen_threats.parse_findings(md_path)
    t_meta = _gen_threats.parse_component_metadata(populated)
    t_sarif = _gen_threats.build_sarif(t_findings, t_meta, affected_by_id)
    t_out = tmp_path / "threats.sarif"
    t_out.write_text(json.dumps(t_sarif, indent=2) + "\n", encoding="utf-8")
    t_reloaded = json.loads(t_out.read_text(encoding="utf-8"))

    t_by_id = {
        r["partialFingerprints"]["findingId/v1"]: r["properties"]["affected_assets"]
        for r in t_reloaded["runs"][0]["results"]
    }
    assert t_by_id["S-1"] == ["auth", "phi", "pii"]
    assert t_by_id["I-2"] == []

    # risk-scores.sarif → assemble an envelope → JSON file → re-parse.
    risk_results = []
    for fid, component in worked:
        finding = {
            "id": fid,
            "component": component,
            "threat_summary": f"Threat narrative for {fid}",
            "cvss_base": 7.0,
            "exploitability": 7.0,
            "scalability": 7.0,
            "reachability": 7.0,
            "composite": 7.0,
            "severity_band": "High",
            "sla_days": "30",
            "disposition": "Open",
        }
        risk_results.append(
            _gen_risk.build_result(
                finding,
                {},
                {},
                _gen_risk.parse_threats_status(populated),
                _gen_risk.parse_threats_full_text(populated),
                _gen_risk.parse_source_attribution(populated),
                _gen_risk.parse_component_metadata(populated),
                affected_by_id,
            )
        )
    risk_sarif = _gen_risk.build_sarif_envelope(
        {"name": "tachi-risk-scorer", "rules": []},
        [],
        risk_results,
    )
    r_out = tmp_path / "risk-scores.sarif"
    r_out.write_text(json.dumps(risk_sarif, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    r_reloaded = json.loads(r_out.read_text(encoding="utf-8"))

    r_by_id = {
        r["partialFingerprints"]["findingId/v1"]: r["properties"]["affected_assets"]
        for r in r_reloaded["runs"][0]["results"]
    }
    assert r_by_id["S-1"] == ["auth", "phi", "pii"]
    assert r_by_id["I-2"] == []

    # Cross-surface: the JSON-round-tripped values match each other too.
    assert t_by_id["S-1"] == r_by_id["S-1"]
    assert t_by_id["I-2"] == r_by_id["I-2"]


# =============================================================================
# ===== SC-007 / SC-004 (T017) =====
# =============================================================================
#
# SC-007 (schema-doc accuracy): the schema-doc surface
# ``.claude/skills/tachi-risk-scoring/references/asset-modifiers.md`` — section
# "Output Contract — ``affected_assets`` Provenance Field" — DOCUMENTS the
# frozen 6-value enum, the always-present ``[]`` empty-default, and a per-format
# representation table (IR/schema, threats.md ``S-1: [phi, pii]``, SARIF flat
# array). These tests assert the DOC matches REALITY: the documented enum equals
# the frozen ``VALID_ASSET_TAGS`` the populator imports; the empty-default and
# per-format threats.md shape match what the populator actually emits; and the
# T-2 worked example carries no stale ``9.5`` ceiling (regression guard for T014
# — the example was corrected to ``9.2``).
#
# SC-004 (ceiling preservation): "a tagged finding whose modified cvss_base
# would exceed 9.2 caps at 9.2; affected_assets is populated regardless of
# clamp." HONESTY CONSTRAINT — the populator is provenance-only (NFR-2): it does
# NOT compute or clamp CVSS (that is FROZEN, LLM-authored risk-scorer logic).
# So these tests pin the TWO testable invariants without overclaiming a unit
# test exercises the LLM scoring path: (1) the frozen ``modifier_ceiling: 9.2``
# constant is intact in ``schemas/risk-scoring.yaml`` (the "caps at 9.2"
# invariant in testable form — the clamp itself is enforced by the frozen
# risk-scoring path, verified structurally by SC-011/T021); and (2)
# ``affected_assets`` is fully populated for a finding whose high-impact tags
# would drive a modifier to/over the ceiling — proving the provenance field is
# recorded independent of any score clamp.
#
# Both reference files are read in-test (stdlib only); neither frozen file is
# modified.

ASSET_MODIFIERS_DOC = (
    REPO_ROOT
    / ".claude"
    / "skills"
    / "tachi-risk-scoring"
    / "references"
    / "asset-modifiers.md"
)
RISK_SCORING_SCHEMA = REPO_ROOT / "schemas" / "risk-scoring.yaml"


def _output_contract_section(doc_text: str) -> str:
    """Return the "Output Contract — ``affected_assets`` Provenance Field" section.

    Slices from the ``## Output Contract`` heading to the next top-level ``## ``
    heading (or end of file), so enum/empty-default/per-format assertions are
    scoped to the provenance-field contract and never pick up the earlier
    CVSS-modifier "Tag Vocabulary" table (which documents the same six tokens for
    a different purpose).
    """
    start = doc_text.find("## Output Contract")
    assert start != -1, "asset-modifiers.md missing 'Output Contract' section heading"
    rest = doc_text[start + len("## Output Contract"):]
    nxt = rest.find("\n## ")
    return doc_text[start:] if nxt == -1 else doc_text[start: start + len("## Output Contract") + nxt]


def _doc_enum_values(doc_text: str) -> "list[str]":
    """Extract the documented FROZEN enum values from the Output Contract section.

    Locates the ``### Enum`` subsection and parses its backtick-wrapped,
    pipe-delimited list line (``\\`pii | phi | auth | secrets | financial |
    safety\\``.``). Returns the tokens in documented order.
    """
    section = _output_contract_section(doc_text)
    enum_idx = section.find("### Enum")
    assert enum_idx != -1, "Output Contract section missing '### Enum' subsection"
    enum_region = section[enum_idx:]
    # The enum line is the first line carrying a backtick-wrapped pipe list.
    for line in enum_region.splitlines():
        if "|" in line and "`" in line:
            first = line.index("`")
            last = line.index("`", first + 1)
            inner = line[first + 1: last]
            return [tok.strip() for tok in inner.split("|") if tok.strip()]
    raise AssertionError(f"no backtick-wrapped enum line found under '### Enum':\n{enum_region}")


# -----------------------------------------------------------------------------
# SC-007.1 — enum agreement: doc enum == frozen VALID_ASSET_TAGS
# -----------------------------------------------------------------------------


def test_sc007_doc_enum_matches_frozen_valid_asset_tags():
    """The 6 enum values DOCUMENTED in asset-modifiers.md equal ``VALID_ASSET_TAGS``.

    SC-007: parse the FROZEN enum line from the Output Contract section's
    ``### Enum`` subsection and assert it is exactly the set of values the
    populator imports from ``tachi_parsers`` — proving the schema-doc surface and
    the code authority agree on the closed 6-value vocabulary.
    """
    doc_text = ASSET_MODIFIERS_DOC.read_text(encoding="utf-8")
    documented = _doc_enum_values(doc_text)

    assert set(documented) == set(VALID_ASSET_TAGS)
    assert len(documented) == len(VALID_ASSET_TAGS) == 6
    # No stray/extra token slipped into the documented list.
    assert sorted(documented) == sorted(VALID_ASSET_TAGS)


def test_sc007_doc_enum_declares_frozen_six_count():
    """The Output Contract ``### Enum`` subsection labels the enum FROZEN at 6.

    Light structural guard: the subsection heading advertises the count, so a
    future widening that changes the value set without updating this label is
    caught. Asserts both the ``FROZEN`` marker and the literal ``6`` appear in the
    enum subsection.
    """
    doc_text = ASSET_MODIFIERS_DOC.read_text(encoding="utf-8")
    section = _output_contract_section(doc_text)
    enum_idx = section.find("### Enum")
    assert enum_idx != -1
    enum_heading_line = section[enum_idx:].splitlines()[0]

    assert "FROZEN" in enum_heading_line
    assert "6" in enum_heading_line


# -----------------------------------------------------------------------------
# SC-007.2 — empty-default agreement: untagged finding renders [] (doc claim)
# -----------------------------------------------------------------------------


def test_sc007_empty_default_matches_doc_always_present_claim():
    """An untagged-component finding emits ``[]`` — matching the doc's FR-005 claim.

    SC-007: the Output Contract's "Empty-default" subsection states ``[]`` is
    "always present ... never omitted (FR-005)". Run the populator on a no-tag
    architecture (a finding on an untagged component) and assert the emitted block
    value is exactly ``[]`` — the doc's claim made executable against real output.
    """
    # First, the doc actually makes the claim we are validating against.
    doc_text = ASSET_MODIFIERS_DOC.read_text(encoding="utf-8")
    section = _output_contract_section(doc_text)
    assert "Empty-default" in section
    assert "always present" in section
    assert "FR-005" in section

    # Then reality: an untagged component yields the documented [] empty form.
    arch = _arch('Web["Public Web Frontend"]')  # no [asset:...] block
    threats = _threats("I-1 | NEW | Public Web Frontend | Low | Log")

    out = populator.populate(arch, threats)

    assert _assets_for(out, "I-1") == "[]"


# -----------------------------------------------------------------------------
# SC-007.3 — per-format shape agreement: threats.md cell renders [phi, pii]
# -----------------------------------------------------------------------------


def test_sc007_threats_md_shape_matches_doc_representation_cell():
    """The threats.md block renders ``[phi, pii]`` — matching the doc's format cell.

    SC-007: the Output Contract per-format table documents the ``threats.md``
    representation as ``S-1: [phi, pii]`` (sorted enum array). Run the populator on
    a ``[asset:phi,pii]`` component and assert the rendered block value is exactly
    the documented sorted form ``[phi, pii]`` — and that ``render_affected_assets_block``
    / ``parse_affected_assets`` agree on that value.
    """
    # The doc's per-format table documents `S-1: [phi, pii]` for threats.md.
    doc_text = ASSET_MODIFIERS_DOC.read_text(encoding="utf-8")
    section = _output_contract_section(doc_text)
    assert "[phi, pii]" in section, "doc per-format table missing threats.md '[phi, pii]' cell"

    arch = _arch('DB[("Records Store<br/>[asset:phi,pii]")]')
    threats = _threats("S-1 | NEW | Records Store | High | Fix")

    out = populator.populate(arch, threats)

    # Block cell renders the documented sorted form.
    assert _assets_for(out, "S-1") == "[phi, pii]"

    # render_affected_assets_block / parse_affected_assets produce the same value
    # the doc's per-format cells describe (block string `[phi, pii]`; SARIF/IR
    # array `["phi", "pii"]`).
    rendered_block = populator.render_affected_assets_block([("S-1", ["phi", "pii"])])
    assert "| S-1 | [phi, pii] |" in rendered_block
    assert parse_affected_assets(out)["S-1"] == ["phi", "pii"]


def test_sc007_render_value_helper_matches_doc_sorted_array_form():
    """``_render_assets_value`` emits the documented bracketed-sorted string form.

    Pins the rendering primitive directly: the documented representation for a
    tagged finding is a sorted, comma-space-joined bracketed list (``[phi, pii]``),
    and the documented empty form is ``[]``. Asserts both shapes straight from the
    value renderer so the per-format "Representation"/"Empty form" cells are pinned
    at the helper level, not only end-to-end.
    """
    assert populator._render_assets_value(["phi", "pii"]) == "[phi, pii]"
    assert populator._render_assets_value([]) == "[]"


# -----------------------------------------------------------------------------
# SC-007.4 — no stale ceiling: asset-modifiers.md has no 9.5, only 9.2
# -----------------------------------------------------------------------------


def test_sc007_doc_has_no_stale_95_ceiling_only_92():
    """asset-modifiers.md contains NO stale ``9.5`` ceiling — only ``9.2`` (T014 guard).

    SC-007 regression guard: the T-2 worked example (and the modifier-ceiling
    prose) were corrected to ``9.2`` in T014. Assert the schema-doc surface
    contains no ``9.5`` token anywhere and that the ceiling value it does cite is
    ``9.2``. (The frozen ``schemas/risk-scoring.yaml`` legitimately mentions ``9.5``
    in its rejection rationale; this guard is scoped to the doc surface only.)
    """
    doc_text = ASSET_MODIFIERS_DOC.read_text(encoding="utf-8")

    assert "9.5" not in doc_text, "stale 9.5 ceiling present in asset-modifiers.md (T014 regressed)"
    assert "9.2" in doc_text, "asset-modifiers.md no longer cites the 9.2 modifier ceiling"
    # The corrected T-2 worked example explicitly states the 9.2 ceiling.
    assert "**Ceiling**: `9.2`" in doc_text


# -----------------------------------------------------------------------------
# SC-004.1 — ceiling constant intact: schemas/risk-scoring.yaml == 9.2
# -----------------------------------------------------------------------------


def test_sc004_modifier_ceiling_constant_is_92():
    """``schemas/risk-scoring.yaml`` still declares ``modifier_ceiling: 9.2``.

    SC-004: the "caps at 9.2" invariant in its testable form. The populator is
    score-neutral (provenance only, NFR-2) and does NOT clamp — the 9.2 clamp is
    enforced by the FROZEN, LLM-authored risk-scoring path (binary-diffed by
    SC-011/T021). This test pins the frozen ceiling CONSTANT (not the clamp
    arithmetic): the ``asset_modifiers.modifier_ceiling`` declaration reads exactly
    ``9.2``, and no drifted ``9.5``/``9.0`` declaration has replaced it.
    """
    schema_text = RISK_SCORING_SCHEMA.read_text(encoding="utf-8")

    # The active declaration (not the surrounding rationale comments) is `9.2`.
    declaration_lines = [
        ln for ln in schema_text.splitlines()
        if ln.strip().startswith("modifier_ceiling:")
    ]
    assert declaration_lines == ["  modifier_ceiling: 9.2"], (
        f"modifier_ceiling declaration drifted: {declaration_lines!r}"
    )


# -----------------------------------------------------------------------------
# SC-004.2 — affected_assets populated regardless of clamp
# -----------------------------------------------------------------------------


def test_sc004_affected_assets_populated_for_ceiling_pushing_tags():
    """High-impact tags that would drive a modifier to/over 9.2 still populate the field.

    SC-004: ``affected_assets`` is populated regardless of clamp. NOTE — the
    populator is score-NEUTRAL: it records provenance only and never computes or
    clamps CVSS (the 9.2 clamp is enforced by the frozen risk-scoring path,
    verified structurally by SC-011/T021). So this test proves provenance-
    independence: a finding whose component carries ``[asset:auth,secrets]``
    (each forcing ``C:H`` + ``I:H`` — the kind that pushes CVSS toward the
    ceiling) has its ``affected_assets`` FULLY populated (``[auth, secrets]``),
    i.e. the field is recorded independent of any score clamp.
    """
    # auth + secrets each force C:H+I:H — the impact profile most likely to drive
    # the modifier-recomputed cvss_base to/over the 9.2 ceiling in the scorer.
    arch = _arch('Vault["Identity Vault<br/>[asset:auth,secrets]"]')
    threats = _threats("S-1 | NEW | Identity Vault | Critical | Rotate + isolate")

    out = populator.populate(arch, threats)

    # Provenance fully recorded (sorted ascending) — independent of any clamp.
    assert _assets_for(out, "S-1") == "[auth, secrets]"
    # And byte-equivalent on the SARIF-facing extractor.
    assert parse_affected_assets(out)["S-1"] == ["auth", "secrets"]


def test_sc004_affected_assets_independent_of_score_fields():
    """The field is recorded with no dependence on any score/severity input.

    Reinforces provenance-independence: the populator never reads CVSS, composite,
    or severity-band fields (NFR-2). A ``Critical``-risk finding and a ``Low``-risk
    finding on the SAME high-impact-tagged component both surface the identical
    fully-populated ``affected_assets`` — confirming the provenance value is a pure
    projection of component tags, unaffected by the (frozen, separately-enforced)
    9.2 clamp or any risk-level signal.
    """
    arch = _arch('Vault["Identity Vault<br/>[asset:auth,secrets]"]')
    threats = _threats(
        "S-1 | NEW | Identity Vault | Critical | Rotate",   # would push toward ceiling
        "D-2 | NEW | Identity Vault | Low | Monitor",        # low risk, same component
    )

    out = populator.populate(arch, threats)

    # Identical provenance regardless of the (ignored) Risk Level column.
    assert _assets_for(out, "S-1") == "[auth, secrets]"
    assert _assets_for(out, "D-2") == "[auth, secrets]"


# =============================================================================
# ===== FR-014 (F-295 / T010-T011) — input-path-derived artifactLocation.uri =====
# =============================================================================
#
# generate-threats-sarif.py::build_result used to hardcode
# ``locations[0].physicalLocation.artifactLocation.uri`` to the literal string
# ``"examples/agentic-app/sample-report/threats.md"``. F-295 FR-014 replaces
# that constant with ``artifact_uri_for(input_path)``, threaded through
# ``build_sarif`` / ``build_result`` as a ``source_uri`` parameter (default =
# the original constant, so any caller that omits it — including this
# module's pre-existing SC-006 tests above — keeps emitting the pre-FR-014
# uri byte-for-byte; this is the seam that makes the T010 L-a proof's
# BEFORE/AFTER ``cmp`` on the CLI path byte-identical for the agentic-app
# fixture). These tests cover: (1) the derivation helper's repo-relative POSIX
# normalization for an in-repo target, (2) its fallback for a non-agentic-app
# path OUTSIDE the repo (a pytest ``tmp_path`` fixture file — the exact case
# plan.md D-C / this task calls out), (3) real end-to-end wiring into the
# emitted SARIF envelope, and (4) the default-parameter backward-compatibility
# guarantee the L-a proof depends on.


def test_fr014_artifact_uri_for_repo_relative_path_matches_second_example():
    """``artifact_uri_for`` derives the exact FR-014 second example's uri.

    T010: for an in-repo target path (the ``examples/multi-tenant-rag-app/``
    baseline this feature's US-2 commits), the derived uri equals the path
    expressed relative to the repository root in POSIX form — matching
    plan.md D-C / quickstart.md Stage 2.3's second worked example exactly:
    input ``examples/multi-tenant-rag-app/threats.md`` -> uri
    ``examples/multi-tenant-rag-app/threats.md``.
    """
    target = REPO_ROOT / "examples" / "multi-tenant-rag-app" / "threats.md"

    uri = _gen_threats.artifact_uri_for(target)

    assert uri == "examples/multi-tenant-rag-app/threats.md"


def test_fr014_artifact_uri_for_tmp_path_outside_repo_falls_back_to_resolved_posix(tmp_path):
    """A non-agentic-app path OUTSIDE the repo (pytest ``tmp_path``) still normalizes.

    T011 covering assertion (the exact case the task calls out): pytest's
    ``tmp_path`` fixture lives under the OS temp directory, outside
    ``REPO_ROOT``, so ``relative_to`` raises ``ValueError`` internally and
    ``artifact_uri_for`` falls back to the resolved absolute POSIX path —
    still deterministic and platform-normalized (no backslashes), and never
    the stale agentic-app constant.
    """
    target = tmp_path / "threats.md"
    target.write_text("placeholder", encoding="utf-8")

    uri = _gen_threats.artifact_uri_for(target)

    assert uri == target.resolve().as_posix()
    assert uri != "examples/agentic-app/sample-report/threats.md"
    assert "\\" not in uri  # POSIX-normalized regardless of platform


def test_fr014_build_sarif_wires_derived_uri_into_artifact_location(tmp_path):
    """``build_sarif``/``build_result`` emit the derived uri, not the old constant.

    FR-014 wiring guard: exercises the real production call sequence
    (``parse_findings`` -> ``build_sarif``) against a ``threats.md`` written at
    a non-agentic-app ``tmp_path``, with ``source_uri`` computed by
    ``artifact_uri_for`` exactly as ``generate-threats-sarif.py::main()`` does.
    Confirms every result's
    ``locations[0].physicalLocation.artifactLocation.uri`` equals the derived
    uri, not the pre-FR-014 hardcoded constant.
    """
    global _TMP_DIR
    _TMP_DIR = tmp_path

    arch = _arch('DB[("Records Store<br/>[asset:pii]")]')
    worked = [("S-1", "Records Store")]
    populated = populator.populate(arch, _xfmt_threats(worked))

    md_path = _write_threats(populated, "threats-fr014.md")
    component_meta = _gen_threats.parse_component_metadata(populated)
    affected_by_id = parse_affected_assets(populated)
    findings = _gen_threats.parse_findings(md_path)

    source_uri = _gen_threats.artifact_uri_for(md_path)
    sarif = _gen_threats.build_sarif(findings, component_meta, affected_by_id, source_uri)

    results = sarif["runs"][0]["results"]
    assert results, "no results produced for the FR-014 wiring fixture"
    for result in results:
        got_uri = result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
        assert got_uri == source_uri == md_path.resolve().as_posix()
        assert got_uri != "examples/agentic-app/sample-report/threats.md"


def test_fr014_build_sarif_default_source_uri_preserves_agentic_app_constant(tmp_path):
    """Omitting ``source_uri`` still yields the original agentic-app constant.

    L-a regression guard: ``build_sarif``'s ``source_uri`` parameter defaults
    to the exact string the hardcoded constant used to be, so any caller that
    does not pass it explicitly (e.g. this module's pre-existing SC-006 tests
    above) keeps emitting the pre-FR-014 uri byte-for-byte. This default is
    what makes the T010 L-a proof's BEFORE/AFTER ``cmp`` on
    ``generate-threats-sarif.py``'s CLI path (which DOES pass ``source_uri``)
    byte-identical for the ``examples/agentic-app/`` fixture.
    """
    global _TMP_DIR
    _TMP_DIR = tmp_path

    arch = _arch('DB[("Records Store<br/>[asset:pii]")]')
    worked = [("S-1", "Records Store")]
    populated = populator.populate(arch, _xfmt_threats(worked))
    md_path = _write_threats(populated, "threats-fr014-default.md")
    component_meta = _gen_threats.parse_component_metadata(populated)
    affected_by_id = parse_affected_assets(populated)
    findings = _gen_threats.parse_findings(md_path)

    sarif = _gen_threats.build_sarif(findings, component_meta, affected_by_id)  # source_uri omitted

    uri = sarif["runs"][0]["results"][0]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
    assert uri == "examples/agentic-app/sample-report/threats.md"
