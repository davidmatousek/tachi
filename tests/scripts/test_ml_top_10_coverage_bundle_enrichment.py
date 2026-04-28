"""Unit tests for the F-6 ML Top 10 Coverage Bundle enrichment (T050).

These tests enforce structural invariants on the three enriched host agent
files and their companion pattern catalogs:

- ``.claude/agents/tachi/tampering.md`` (STRIDE tier, <=120 line cap)
- ``.claude/agents/tachi/data-poisoning.md`` (AI tier, <=150 line cap)
- ``.claude/agents/tachi/model-theft.md`` (AI tier, <=150 line cap)
- Three companion ``detection-patterns.md`` files under
  ``.claude/skills/tachi-{tampering,data-poisoning,model-theft}/references/``
  carrying the new Pattern Categories per ADR-035 D-3.

Per spec ``specs/232-ml-top-10-coverage-bundle/spec.md``, this module covers
F-6 success criteria SC-014 (line caps), SC-019 (references-array contract),
SC-022 (MAESTRO grep clean), SC-023 (Pattern Category Disambiguation
presence). Byte-identity of pre-existing categories is delegated to
``tests/scripts/test_backward_compatibility.py`` against the 6 baselines.

This module follows the F-5 enrichment-test precedent in
``tests/scripts/test_llm10_unbounded_consumption_enrichment.py``.

Schema regex tests are NOT included — F-6 reuses the existing ``T``, ``D``,
and ``LLM`` prefixes without a schema bump per ADR-035.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from .conftest import REPO_ROOT


# Agent files (host enrichment surface)
TAMPERING_AGENT = REPO_ROOT / ".claude" / "agents" / "tachi" / "tampering.md"
DATA_POISONING_AGENT = REPO_ROOT / ".claude" / "agents" / "tachi" / "data-poisoning.md"
MODEL_THEFT_AGENT = REPO_ROOT / ".claude" / "agents" / "tachi" / "model-theft.md"

# Companion detection-pattern catalogs (Wave 2.1 / 2.3 / 3 new pattern categories)
TAMPERING_COMPANION = (
    REPO_ROOT
    / ".claude"
    / "skills"
    / "tachi-tampering"
    / "references"
    / "detection-patterns.md"
)
DATA_POISONING_COMPANION = (
    REPO_ROOT
    / ".claude"
    / "skills"
    / "tachi-data-poisoning"
    / "references"
    / "detection-patterns.md"
)
MODEL_THEFT_COMPANION = (
    REPO_ROOT
    / ".claude"
    / "skills"
    / "tachi-model-theft"
    / "references"
    / "detection-patterns.md"
)

# Seven fixtures under tests/scripts/fixtures/ml_top_10_coverage_bundle/
FIXTURE_DIR = REPO_ROOT / "tests" / "scripts" / "fixtures" / "ml_top_10_coverage_bundle"
T_10_FIXTURE = FIXTURE_DIR / "valid_category_10_tampering_adversarial_input_finding.yaml"
D_8_FIXTURE = FIXTURE_DIR / "valid_category_8_data_poisoning_transfer_learning_finding.yaml"
D_9_FIXTURE = FIXTURE_DIR / "valid_category_9_data_poisoning_feedback_loop_finding.yaml"
D_10_FIXTURE = FIXTURE_DIR / "valid_category_10_data_poisoning_corpus_supply_chain_finding.yaml"
LLM_12_FIXTURE = FIXTURE_DIR / "valid_category_12_model_theft_inversion_finding.yaml"
LLM_13_FIXTURE = FIXTURE_DIR / "valid_category_13_model_theft_membership_inference_finding.yaml"
LLM_14_FIXTURE = FIXTURE_DIR / "valid_category_14_model_theft_artifact_supply_chain_finding.yaml"

# All six enriched files (3 agents + 3 companions) for sweep tests
ALL_ENRICHED_FILES = (
    TAMPERING_AGENT,
    DATA_POISONING_AGENT,
    MODEL_THEFT_AGENT,
    TAMPERING_COMPANION,
    DATA_POISONING_COMPANION,
    MODEL_THEFT_COMPANION,
)

# All three F-6 companions for Disambiguation sweep
ALL_F6_COMPANIONS = (
    TAMPERING_COMPANION,
    DATA_POISONING_COMPANION,
    MODEL_THEFT_COMPANION,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_fixture(path: Path) -> dict:
    """Load a YAML fixture from disk."""
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _joined_refs(fixture_path: Path) -> str:
    """Return the references array of a fixture as a pipe-joined string."""
    finding = _load_fixture(fixture_path)
    refs = finding.get("references", [])
    assert isinstance(refs, list), (
        f"{fixture_path.name} references MUST be a list; got {type(refs)}"
    )
    return " | ".join(refs)


def _all_fixture_refs_joined() -> str:
    """Aggregate all 7 fixtures' references into a single pipe-joined string.

    Used for catalog-resolvability sweep tests (T0015 / T0019 / T0031 prose-only).
    """
    parts = []
    for fixture in (
        T_10_FIXTURE,
        D_8_FIXTURE,
        D_9_FIXTURE,
        D_10_FIXTURE,
        LLM_12_FIXTURE,
        LLM_13_FIXTURE,
        LLM_14_FIXTURE,
    ):
        parts.append(_joined_refs(fixture))
    return " | ".join(parts)


# ---------------------------------------------------------------------------
# Section A — Line-count caps (SC-014)
# ---------------------------------------------------------------------------


class TestLineCountCaps:
    """SC-014: agent-tier line-count caps preserved post-enrichment.

    Per ADR-023 line-count discipline:
    - tampering.md (STRIDE-tier): <=120 lines
    - data-poisoning.md (AI-tier): <=150 lines
    - model-theft.md (AI-tier): <=150 lines
    """

    def test_tampering_md_line_cap(self) -> None:
        """SC-014: tampering.md MUST be <=120 lines (STRIDE tier cap per ADR-023)."""
        line_count = sum(1 for _ in TAMPERING_AGENT.open("r", encoding="utf-8"))
        assert line_count <= 120, (
            f"tampering.md line count {line_count} exceeds STRIDE-tier cap of 120."
        )

    def test_data_poisoning_md_line_cap(self) -> None:
        """SC-014: data-poisoning.md MUST be <=150 lines (AI tier cap per ADR-023)."""
        line_count = sum(1 for _ in DATA_POISONING_AGENT.open("r", encoding="utf-8"))
        assert line_count <= 150, (
            f"data-poisoning.md line count {line_count} exceeds AI-tier cap of 150."
        )

    def test_model_theft_md_line_cap(self) -> None:
        """SC-014: model-theft.md MUST be <=150 lines (AI tier cap per ADR-023)."""
        line_count = sum(1 for _ in MODEL_THEFT_AGENT.open("r", encoding="utf-8"))
        assert line_count <= 150, (
            f"model-theft.md line count {line_count} exceeds AI-tier cap of 150."
        )


# ---------------------------------------------------------------------------
# Section B — MAESTRO grep clean (SC-022)
# ---------------------------------------------------------------------------


class TestMaestroGrepClean:
    """SC-022: zero MAESTRO references on all six enriched files.

    Consistent with F-1 through F-5 governance constraint — F-6 host files
    MUST NOT introduce MAESTRO references (MAESTRO layer assignment is
    orchestrator-owned, not agent-authored).
    """

    @pytest.mark.parametrize("path", ALL_ENRICHED_FILES, ids=lambda p: p.name)
    def test_no_maestro_references_in_enriched_files(self, path: Path) -> None:
        """No 'maestro' substring (case-insensitive) in any of the 6 F-6 files."""
        content = path.read_text(encoding="utf-8").lower()
        assert "maestro" not in content, (
            f"{path.name} MUST contain zero MAESTRO references "
            f"(MAESTRO layer assignment is orchestrator-owned, not agent-authored)."
        )


# ---------------------------------------------------------------------------
# Section C — Pattern Category Disambiguation header presence (SC-023 / FR-011)
# ---------------------------------------------------------------------------


class TestPatternCategoryDisambiguation:
    """SC-023 / FR-011: each F-6 companion has exactly 1 Disambiguation header.

    The Disambiguation subsection maps the new categories' boundary against
    pre-existing categories in the same companion (Q1 SPLIT discipline).
    """

    @pytest.mark.parametrize("path", ALL_F6_COMPANIONS, ids=lambda p: p.parent.parent.name)
    def test_pattern_category_disambiguation_present_on_3_companions(
        self, path: Path
    ) -> None:
        """Each of the 3 F-6 companions MUST contain exactly 1 Disambiguation header."""
        content = path.read_text(encoding="utf-8")
        matches = re.findall(r"^## Pattern Category Disambiguation", content, re.MULTILINE)
        assert len(matches) == 1, (
            f"{path.name} MUST contain exactly 1 '## Pattern Category Disambiguation' "
            f"header per FR-011 / SC-023; found {len(matches)}."
        )


# ---------------------------------------------------------------------------
# Section D — New Pattern Categories present (FR-005, FR-007, FR-008, FR-009)
# ---------------------------------------------------------------------------


class TestNewPatternCategoriesPresent:
    """New Cat headers MUST be present in the corresponding F-6 companion."""

    def test_tampering_companion_has_cat_10(self) -> None:
        """tampering detection-patterns.md MUST contain '## Pattern Category 10' header."""
        content = TAMPERING_COMPANION.read_text(encoding="utf-8")
        assert "## Pattern Category 10: Adversarial Input Manipulation" in content, (
            "Pattern Category 10 (Adversarial Input Manipulation — Predictive ML) "
            "header MUST be present in tampering detection-patterns.md per FR-005."
        )

    def test_data_poisoning_companion_has_cat_8(self) -> None:
        """data-poisoning detection-patterns.md MUST contain '## Pattern Category 8' header."""
        content = DATA_POISONING_COMPANION.read_text(encoding="utf-8")
        assert "## Pattern Category 8: Transfer Learning Supply Chain" in content, (
            "Pattern Category 8 (Transfer Learning Supply Chain — Predictive ML) "
            "header MUST be present in data-poisoning detection-patterns.md per FR-007."
        )

    def test_data_poisoning_companion_has_cat_9(self) -> None:
        """data-poisoning detection-patterns.md MUST contain '## Pattern Category 9' header."""
        content = DATA_POISONING_COMPANION.read_text(encoding="utf-8")
        assert "## Pattern Category 9: Feedback-Loop Model Skewing" in content, (
            "Pattern Category 9 (Feedback-Loop Model Skewing — Active/Online Learning) "
            "header MUST be present in data-poisoning detection-patterns.md per FR-007."
        )

    def test_data_poisoning_companion_has_cat_10(self) -> None:
        """data-poisoning detection-patterns.md MUST contain '## Pattern Category 10' header."""
        content = DATA_POISONING_COMPANION.read_text(encoding="utf-8")
        assert "## Pattern Category 10: Predictive-ML Supply Chain Completeness" in content, (
            "Pattern Category 10 (Predictive-ML Supply Chain Completeness) header "
            "MUST be present in data-poisoning detection-patterns.md per FR-008."
        )

    def test_model_theft_companion_has_cat_12(self) -> None:
        """model-theft detection-patterns.md MUST contain '## Pattern Category 12' header."""
        content = MODEL_THEFT_COMPANION.read_text(encoding="utf-8")
        assert "## Pattern Category 12: Model Inversion" in content, (
            "Pattern Category 12 (Model Inversion — Predictive ML) header MUST be "
            "present in model-theft detection-patterns.md per FR-009."
        )

    def test_model_theft_companion_has_cat_13(self) -> None:
        """model-theft detection-patterns.md MUST contain '## Pattern Category 13' header."""
        content = MODEL_THEFT_COMPANION.read_text(encoding="utf-8")
        assert "## Pattern Category 13: Membership Inference" in content, (
            "Pattern Category 13 (Membership Inference — Predictive ML) header MUST "
            "be present in model-theft detection-patterns.md per FR-009."
        )

    def test_model_theft_companion_has_cat_14(self) -> None:
        """model-theft detection-patterns.md MUST contain '## Pattern Category 14' header."""
        content = MODEL_THEFT_COMPANION.read_text(encoding="utf-8")
        assert "## Pattern Category 14: Predictive-ML Artifact Supply Chain" in content, (
            "Pattern Category 14 (Predictive-ML Artifact Supply Chain) header MUST "
            "be present in model-theft detection-patterns.md per FR-009."
        )


# ---------------------------------------------------------------------------
# Section E — references-array fixture validation (SC-019 / Invariant 1+2)
# ---------------------------------------------------------------------------


class TestFixtureReferencesContract:
    """SC-019 / Finding IR Contract: each fixture's references array contains
    the expected catalog-resolvable OWASP / ATLAS / ATT&CK identifiers.
    """

    def test_t_10_fixture_references_array(self) -> None:
        """T-10 fixture references MUST contain 'OWASP ML01:2023'."""
        joined = _joined_refs(T_10_FIXTURE)
        assert "OWASP ML01:2023" in joined, (
            f"T-10 (tampering Cat 10) fixture references MUST include "
            f"'OWASP ML01:2023' (Invariant 1); got: {joined!r}"
        )

    def test_d_8_fixture_references_array(self) -> None:
        """D-8 fixture references MUST contain 'OWASP ML07:2023'."""
        joined = _joined_refs(D_8_FIXTURE)
        assert "OWASP ML07:2023" in joined, (
            f"D-8 (data-poisoning Cat 8) fixture references MUST include "
            f"'OWASP ML07:2023' (Invariant 1); got: {joined!r}"
        )

    def test_d_9_fixture_references_array(self) -> None:
        """D-9 fixture references MUST contain 'OWASP ML08:2023'."""
        joined = _joined_refs(D_9_FIXTURE)
        assert "OWASP ML08:2023" in joined, (
            f"D-9 (data-poisoning Cat 9) fixture references MUST include "
            f"'OWASP ML08:2023' (Invariant 1); got: {joined!r}"
        )

    def test_d_10_fixture_references_array(self) -> None:
        """D-10 fixture references MUST contain 'OWASP ML06:2023' AND 'T1195'."""
        joined = _joined_refs(D_10_FIXTURE)
        assert "OWASP ML06:2023" in joined, (
            f"D-10 (data-poisoning Cat 10) fixture references MUST include "
            f"'OWASP ML06:2023' (Invariant 1); got: {joined!r}"
        )
        assert "T1195" in joined, (
            f"D-10 (data-poisoning Cat 10) fixture references MUST include "
            f"'T1195' supply-chain ATT&CK reference (Invariant 2); got: {joined!r}"
        )

    def test_llm_12_fixture_references_array(self) -> None:
        """LLM-12 fixture references MUST contain 'OWASP ML03:2023' AND 'AML.T0024'."""
        joined = _joined_refs(LLM_12_FIXTURE)
        assert "OWASP ML03:2023" in joined, (
            f"LLM-12 (model-theft Cat 12) fixture references MUST include "
            f"'OWASP ML03:2023' (Invariant 1); got: {joined!r}"
        )
        assert "AML.T0024" in joined, (
            f"LLM-12 (model-theft Cat 12) fixture references MUST include "
            f"'AML.T0024' (catalog-resolvable per ADR-035 D-5); got: {joined!r}"
        )

    def test_llm_13_fixture_references_array(self) -> None:
        """LLM-13 fixture references MUST contain 'OWASP ML04:2023' AND 'AML.T0024'."""
        joined = _joined_refs(LLM_13_FIXTURE)
        assert "OWASP ML04:2023" in joined, (
            f"LLM-13 (model-theft Cat 13) fixture references MUST include "
            f"'OWASP ML04:2023' (Invariant 1); got: {joined!r}"
        )
        assert "AML.T0024" in joined, (
            f"LLM-13 (model-theft Cat 13) fixture references MUST include "
            f"'AML.T0024' (catalog-resolvable per ADR-035 D-5); got: {joined!r}"
        )

    def test_llm_14_fixture_references_array(self) -> None:
        """LLM-14 fixture references MUST contain ML06 + T1195 + T1195.001 + T1195.002."""
        joined = _joined_refs(LLM_14_FIXTURE)
        assert "OWASP ML06:2023" in joined, (
            f"LLM-14 (model-theft Cat 14) fixture references MUST include "
            f"'OWASP ML06:2023' (Invariant 1); got: {joined!r}"
        )
        assert "T1195" in joined, (
            f"LLM-14 fixture references MUST include 'T1195' parent supply-chain "
            f"ATT&CK reference; got: {joined!r}"
        )
        assert "T1195.001" in joined, (
            f"LLM-14 fixture references MUST include 'T1195.001' sub-technique "
            f"(catalog-resolvable per ADR-035 D-4); got: {joined!r}"
        )
        assert "T1195.002" in joined, (
            f"LLM-14 fixture references MUST include 'T1195.002' sub-technique "
            f"(catalog-resolvable per ADR-035 D-4); got: {joined!r}"
        )


# ---------------------------------------------------------------------------
# Section F — ATLAS catalog-resolvability assertions (Finding IR Invariant 3)
# ---------------------------------------------------------------------------


class TestAtlasCatalogResolvability:
    """Finding IR Contract Invariant 3: only catalog-resolvable ATLAS / ATT&CK
    identifiers appear in references arrays. Non-catalog ATLAS techniques
    appear as prose-only cross-references in mitigation narrative.

    Catalog-resolvable (PRESENT in references): T0018, T0020, T0024, T1195,
    T1195.001, T1195.002.

    NOT catalog-resolvable (prose-only; NEVER in references): T0015, T0019,
    T0031.
    """

    @pytest.mark.parametrize("atlas_id", ["T0015", "T0019", "T0031"])
    def test_prose_only_atlas_techniques_absent_from_references(
        self, atlas_id: str
    ) -> None:
        """Non-catalog-resolvable ATLAS techniques MUST NOT appear in any fixture
        references array per Invariant 3 / ADR-035.

        T0015 (Evade ML Model) is prose-only on tampering Cat 10 mitigation;
        T0019 (Publish Poisoned Datasets) is prose-only on data-poisoning Cat 8;
        T0031 (Erode ML Model Integrity) is prose-only on data-poisoning Cat 9.
        """
        joined = _all_fixture_refs_joined()
        assert atlas_id not in joined, (
            f"AML.{atlas_id} MUST NOT appear in any fixture references array per "
            f"Invariant 3 (it is prose-only on its owning Pattern Category mitigation)."
        )

    def test_atlas_T0018_catalog_resolvable_in_d_8(self) -> None:
        """AML.T0018 (Backdoor ML Model) MUST appear in D-8 references array."""
        joined = _joined_refs(D_8_FIXTURE)
        assert "T0018" in joined, (
            f"AML.T0018 MUST appear in D-8 references array (catalog-resolvable "
            f"per ADR-035; AML.T0018 = Backdoor ML Model); got: {joined!r}"
        )

    def test_atlas_T0020_catalog_resolvable_in_d_9(self) -> None:
        """AML.T0020 (Poison Training Data) MUST appear in D-9 references array."""
        joined = _joined_refs(D_9_FIXTURE)
        assert "T0020" in joined, (
            f"AML.T0020 MUST appear in D-9 references array (catalog-resolvable "
            f"per ADR-035; AML.T0020 = Poison Training Data); got: {joined!r}"
        )

    def test_atlas_T0024_catalog_resolvable_in_llm_12_and_13(self) -> None:
        """AML.T0024 MUST appear in BOTH LLM-12 and LLM-13 references arrays.

        Cat 12 (Model Inversion) and Cat 13 (Membership Inference) share the
        catalog-resolvable AML.T0024 (Exfiltration via ML Inference API)
        because both attack classes exfiltrate via the inference API per
        ADR-035 D-5; the architectural-tell decomposition ensures disjoint
        mitigation guidance.
        """
        for fixture, label in ((LLM_12_FIXTURE, "LLM-12"), (LLM_13_FIXTURE, "LLM-13")):
            joined = _joined_refs(fixture)
            assert "T0024" in joined, (
                f"AML.T0024 MUST appear in {label} references array per "
                f"ADR-035 D-5 (shared catalog reference; disjoint architectural-tells); "
                f"got: {joined!r}"
            )

    def test_attack_T1195_catalog_resolvable_in_d_10_and_llm_14(self) -> None:
        """T1195 + T1195.001 + T1195.002 MUST all appear in D-10 and LLM-14.

        The supply-chain triad (parent + 2 sub-techniques) is catalog-resolvable
        in MITRE ATT&CK per ADR-035 D-4; both D-10 (corpus-side) and LLM-14
        (artifact-side) cite the full triad to anchor disjoint architectural-tells.
        """
        for fixture, label in (
            (D_10_FIXTURE, "D-10"),
            (LLM_14_FIXTURE, "LLM-14"),
        ):
            joined = _joined_refs(fixture)
            for ref in ("T1195", "T1195.001", "T1195.002"):
                assert ref in joined, (
                    f"{ref} MUST appear in {label} references array per "
                    f"ADR-035 D-4 (catalog-resolvable supply-chain triad); "
                    f"got: {joined!r}"
                )


# ---------------------------------------------------------------------------
# Section G — MANDATORY Read directive preservation (F-5 precedent)
# ---------------------------------------------------------------------------


class TestMandatoryReadDirective:
    """ADR-023 lean variant: each F-6 host agent has a MANDATORY Read directive
    instructing it to load its companion detection-patterns.md before applying
    patterns to components.

    Mirrors the F-5 single-point-load pattern; ensures enrichment did not
    regress the existing directive across any of the 3 host agents.
    """

    def test_tampering_agent_mandatory_read_directive_present(self) -> None:
        """tampering.md MUST contain the MANDATORY Read directive."""
        content = TAMPERING_AGENT.read_text(encoding="utf-8")
        assert "**MANDATORY**: Read" in content, (
            "tampering.md MUST contain a '**MANDATORY**: Read' directive "
            "loading its companion detection-patterns.md per ADR-023 lean variant."
        )
        assert "tachi-tampering/references/detection-patterns.md" in content, (
            "tampering.md MANDATORY Read directive MUST reference "
            "'tachi-tampering/references/detection-patterns.md' as its target."
        )

    def test_data_poisoning_agent_mandatory_read_directive_present(self) -> None:
        """data-poisoning.md MUST contain the MANDATORY Read directive."""
        content = DATA_POISONING_AGENT.read_text(encoding="utf-8")
        assert "**MANDATORY**: Read" in content, (
            "data-poisoning.md MUST contain a '**MANDATORY**: Read' directive "
            "loading its companion detection-patterns.md per ADR-023 lean variant."
        )
        assert "tachi-data-poisoning/references/detection-patterns.md" in content, (
            "data-poisoning.md MANDATORY Read directive MUST reference "
            "'tachi-data-poisoning/references/detection-patterns.md' as its target."
        )

    def test_model_theft_agent_mandatory_read_directive_present(self) -> None:
        """model-theft.md MUST contain the MANDATORY Read directive."""
        content = MODEL_THEFT_AGENT.read_text(encoding="utf-8")
        assert "**MANDATORY**: Read" in content, (
            "model-theft.md MUST contain a '**MANDATORY**: Read' directive "
            "loading its companion detection-patterns.md per ADR-023 lean variant."
        )
        assert "tachi-model-theft/references/detection-patterns.md" in content, (
            "model-theft.md MANDATORY Read directive MUST reference "
            "'tachi-model-theft/references/detection-patterns.md' as its target."
        )
