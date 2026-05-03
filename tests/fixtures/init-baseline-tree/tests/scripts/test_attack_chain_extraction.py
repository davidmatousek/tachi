"""Integration tests for attack chain extraction in extract-report-data.py.

Tests parse_attack_chains fixture parsing, Mermaid flowchart syntax generation,
Typst data structure injection, and the conditional has-attack-chains gate.
"""

import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "extract-report-data.py"
TEMPLATE_DIR = REPO_ROOT / "templates" / "tachi" / "security-report"

# Import the hyphenated module via importlib
sys.path.insert(0, str(REPO_ROOT / "scripts"))
_spec = importlib.util.spec_from_file_location("extract_report_data", str(SCRIPT_PATH))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

generate_chain_mermaid = _mod.generate_chain_mermaid
prepare_attack_chains = _mod.prepare_attack_chains
generate_report_data_typ = _mod.generate_report_data_typ
_MAESTRO_LAYER_NAMES = _mod._MAESTRO_LAYER_NAMES
_MAESTRO_LAYER_COLORS = _mod._MAESTRO_LAYER_COLORS

from tachi_parsers import parse_attack_chains


# ---------------------------------------------------------------------------
# Fixtures: sample attack-chains.md content
# ---------------------------------------------------------------------------

SAMPLE_ATTACK_CHAINS_MD = """\
---
schema_version: "1.0"
generated_by: orchestrator
---

# Attack Chain Summary

| Chain ID | Layers | Max Severity | Finding Count | Initial Exploit | Business Impact |
|----------|--------|-------------|---------------|-----------------|-----------------|
| CHAIN-001 | L2 → L3 → L7 | Critical | 3 | Data poisoning at vector store | Unauthorized agent actions |
| CHAIN-002 | L1 → L3 | High | 2 | Model extraction via API | Framework compromise |

## Chain Details

### CHAIN-001: Data Poisoning to Agent Ecosystem Compromise

**Layers**: L2 → L3 → L7
**Max Severity**: Critical
**Surfaced**: Yes

#### Member Findings

| Finding ID | MAESTRO Layer | Role | Component | Category | Severity |
|------------|--------------|------|-----------|----------|----------|
| T-003 | L2 | Initial Exploit | Vector DB | Tampering | High |
| AG-002 | L3 | Intermediate Cascade | Agent Orchestrator | Agentic Threats | Critical |
| S-001 | L7 | Terminal Impact | Chat UI | Spoofing | High |

#### Attack Progression

The attacker poisons the vector store at L2 Data Operations, injecting adversarial embeddings into the RAG pipeline. This enables corrupted context retrieval at L3 Agent Framework, where the orchestrator consumes poisoned data during planning. The compromised plan triggers unauthorized actions at L7 Agent Ecosystem, where the chat UI presents fabricated responses to end users.

#### Chain-Breaking Controls

**Target**: AG-002 (L3)
**Rationale**: Highest betweenness centrality — bridges data layer to ecosystem layer
**Recommendation**: Implement output validation on orchestrator planning stage

### CHAIN-002: Model Extraction to Framework Compromise

**Layers**: L1 → L3
**Max Severity**: High
**Surfaced**: Yes

#### Member Findings

| Finding ID | MAESTRO Layer | Role | Component | Category | Severity |
|------------|--------------|------|-----------|----------|----------|
| I-005 | L1 | Initial Exploit | LLM Service | Information Disclosure | High |
| E-001 | L3 | Terminal Impact | Tool Server | Elevation of Privilege | Medium |

#### Attack Progression

An attacker extracts model weights via the inference API at L1 Foundation Model, gaining knowledge of the model behavior. This enables targeted prompt injection at L3 Agent Framework, escalating privileges on the tool server to execute unauthorized tool calls.

#### Chain-Breaking Controls

**Target**: I-005 (L1)
**Rationale**: Only finding in chain with High severity; initial exploit entry point
**Recommendation**: Rate-limit inference API and add output watermarking
"""

SAMPLE_NO_CHAINS_MD = """\
---
schema_version: "1.0"
---

# Attack Chain Summary

No cross-layer attack chains detected.
"""


# ---------------------------------------------------------------------------
# Test: parse_attack_chains from fixture
# ---------------------------------------------------------------------------

class TestParseAttackChains:

    def test_parse_two_chains(self):
        chains = parse_attack_chains(SAMPLE_ATTACK_CHAINS_MD)
        assert len(chains) == 2

    def test_chain_001_fields(self):
        chains = parse_attack_chains(SAMPLE_ATTACK_CHAINS_MD)
        c1 = chains[0]
        assert c1["chain_id"] == "CHAIN-001"
        assert c1["title"] == "Data Poisoning to Agent Ecosystem Compromise"
        assert c1["layers"] == ["L2", "L3", "L7"]
        assert c1["max_severity"] == "Critical"
        assert c1["surfaced"] is True

    def test_chain_001_findings(self):
        chains = parse_attack_chains(SAMPLE_ATTACK_CHAINS_MD)
        findings = chains[0]["findings"]
        assert len(findings) == 3
        assert findings[0]["finding_id"] == "T-003"
        assert findings[0]["maestro_layer"] == "L2"
        assert findings[0]["role"] == "Initial Exploit"
        assert findings[2]["finding_id"] == "S-001"
        assert findings[2]["role"] == "Terminal Impact"

    def test_chain_001_narrative(self):
        chains = parse_attack_chains(SAMPLE_ATTACK_CHAINS_MD)
        narrative = chains[0]["narrative"]
        assert "vector store" in narrative.lower()
        assert "L2" in narrative or "Data Operations" in narrative

    def test_chain_001_controls(self):
        chains = parse_attack_chains(SAMPLE_ATTACK_CHAINS_MD)
        controls = chains[0]["chain_breaking_controls"]
        assert len(controls) == 1
        assert controls[0]["target_finding_id"] == "AG-002"
        assert controls[0]["target_layer"] == "L3"

    def test_chain_002_fields(self):
        chains = parse_attack_chains(SAMPLE_ATTACK_CHAINS_MD)
        c2 = chains[1]
        assert c2["chain_id"] == "CHAIN-002"
        assert c2["layers"] == ["L1", "L3"]
        assert c2["max_severity"] == "High"
        assert c2["surfaced"] is True

    def test_no_chains_returns_empty(self):
        chains = parse_attack_chains(SAMPLE_NO_CHAINS_MD)
        assert chains == []

    def test_empty_content_returns_empty(self):
        assert parse_attack_chains("") == []
        assert parse_attack_chains(None) == []


# ---------------------------------------------------------------------------
# Test: generate_chain_mermaid
# ---------------------------------------------------------------------------

class TestGenerateChainMermaid:

    def _make_chain(self, layers, findings=None):
        if findings is None:
            findings = [
                {"finding_id": f"F-{i}", "maestro_layer": layer,
                 "component": f"Component {i}", "category": "Tampering",
                 "causal_relationship": "enables"}
                for i, layer in enumerate(layers, 1)
            ]
        return {
            "chain_id": "CHAIN-001",
            "title": "Test Chain",
            "layers": layers,
            "findings": findings,
        }

    def test_flowchart_td_header(self):
        chain = self._make_chain(["L2", "L3"])
        mermaid = generate_chain_mermaid(chain)
        assert mermaid.startswith("flowchart TD")

    def test_nodes_contain_layer_names(self):
        chain = self._make_chain(["L2", "L3", "L7"])
        mermaid = generate_chain_mermaid(chain)
        assert "Data Operations" in mermaid
        assert "Agent Framework" in mermaid
        assert "Agent Ecosystem" in mermaid

    def test_nodes_contain_finding_ids(self):
        chain = self._make_chain(["L1", "L3"])
        mermaid = generate_chain_mermaid(chain)
        assert "F-1" in mermaid
        assert "F-2" in mermaid

    def test_edges_with_causal_labels(self):
        chain = self._make_chain(["L2", "L3"])
        mermaid = generate_chain_mermaid(chain)
        assert '-->|"enables"|' in mermaid

    def test_three_node_chain_has_two_edges(self):
        chain = self._make_chain(["L2", "L3", "L7"])
        mermaid = generate_chain_mermaid(chain)
        edge_count = mermaid.count("-->|")
        assert edge_count == 2

    def test_empty_findings_returns_empty(self):
        chain = {"findings": []}
        assert generate_chain_mermaid(chain) == ""

    def test_node_colors_applied(self):
        chain = self._make_chain(["L2"])
        mermaid = generate_chain_mermaid(chain)
        assert _MAESTRO_LAYER_COLORS["L2"] in mermaid

    def test_all_layers_have_names(self):
        for layer_id in ["L1", "L2", "L3", "L4", "L5", "L6", "L7"]:
            assert layer_id in _MAESTRO_LAYER_NAMES

    def test_all_layers_have_colors(self):
        for layer_id in ["L1", "L2", "L3", "L4", "L5", "L6", "L7"]:
            assert layer_id in _MAESTRO_LAYER_COLORS


# ---------------------------------------------------------------------------
# Test: Typst data structure for chains
# ---------------------------------------------------------------------------

class TestTypstChainData:

    def _make_data_with_chains(self, chains=None):
        """Build a minimal data dict with attack chain entries."""
        if chains is None:
            chains = [{
                "chain_id": "CHAIN-001",
                "title": "Test Chain",
                "layers": ["L2", "L3"],
                "max_severity": "Critical",
                "surfaced": True,
                "has_image": False,
                "image_path": "",
                "narrative": "Test narrative text.",
                "findings": [
                    {"finding_id": "T-001", "maestro_layer": "L2"},
                    {"finding_id": "AG-001", "maestro_layer": "L3"},
                ],
                "chain_breaking_controls": [],
            }]
        return {
            "project_name": "Test",
            "assessment_date": "2026-04-12",
            "classification": None,
            "tier": 3,
            "artifacts": {
                "threats_md": True, "threat_report_md": False,
                "risk_scores_md": False, "compensating_controls_md": False,
                "funnel_image": False, "baseball_image": False,
                "architecture_image": False,
            },
            "severity": {"critical": 1, "high": 1, "medium": 0, "low": 0, "note": 0, "total": 2},
            "findings": [],
            "component_distribution": [],
            "executive_narrative": None,
            "funnel_image_path": "",
            "baseball_image_path": "",
            "architecture_image_path": "",
            "maestro_stack_image_path": "",
            "maestro_heatmap_image_path": "",
            "executive_architecture_image_path": "",
            "has_maestro_data": False,
            "maestro_layer_distribution": [],
            "most_exposed_layer": "",
            "maestro_findings_by_layer": [],
            "has_attack_trees": False,
            "attack_trees": [],
            "has_attack_chains": True,
            "attack_chains": chains,
            "has_baseline": False,
            "baseline_source": "",
            "baseline_date": "",
            "baseline_finding_count": "0",
            "baseline_run_id": "",
            "delta_counts": {"new": 0, "unchanged": 0, "updated": 0, "resolved": 0},
            "resolved_findings": [],
            "coverage_matrix": [],
            "controls": [],
            "coverage_summary": {"total-found": 0, "total-partial": 0, "total-missing": 0},
            "remediation_actions": [],
            "scope_components": [],
            "scope_data_flows": [],
            "scope_trust_boundaries": [],
            "scope_boundary_crossings": [],
            "has_logo_primary": False,
            "has_logo_horizontal": False,
            "logo_primary_path": None,
            "logo_primary_dark_path": None,
            "logo_horizontal_path": None,
        }

    def test_has_attack_chains_true(self):
        data = self._make_data_with_chains()
        typst = generate_report_data_typ(data)
        assert "#let has-attack-chains = true" in typst

    def test_has_attack_chains_false_when_empty(self):
        data = self._make_data_with_chains(chains=[])
        data["has_attack_chains"] = False
        typst = generate_report_data_typ(data)
        assert "#let has-attack-chains = false" in typst

    def test_chain_entry_in_typst(self):
        data = self._make_data_with_chains()
        typst = generate_report_data_typ(data)
        assert 'id: "CHAIN-001"' in typst
        assert 'title: "Test Chain"' in typst
        assert "L2" in typst

    def test_finding_ids_in_typst(self):
        data = self._make_data_with_chains()
        typst = generate_report_data_typ(data)
        assert '"T-001"' in typst
        assert '"AG-001"' in typst

    def test_layers_string_in_typst(self):
        data = self._make_data_with_chains()
        typst = generate_report_data_typ(data)
        # The layers are joined with arrow
        assert "L2" in typst and "L3" in typst

    def test_no_chains_emits_empty_array(self):
        data = self._make_data_with_chains(chains=[])
        data["has_attack_chains"] = False
        typst = generate_report_data_typ(data)
        assert "#let attack-chains = ()" in typst

    def test_unsurfaced_chains_not_in_typst(self):
        chains = [{
            "chain_id": "CHAIN-099",
            "title": "Low severity chain",
            "layers": ["L2", "L3"],
            "max_severity": "Low",
            "surfaced": False,
            "findings": [],
            "narrative": "",
            "chain_breaking_controls": [],
        }]
        data = self._make_data_with_chains(chains=chains)
        typst = generate_report_data_typ(data)
        # Unsurfaced chains should not appear in the Typst array
        assert "CHAIN-099" not in typst


# ---------------------------------------------------------------------------
# Test: conditional gate — no chains = no chain variables
# ---------------------------------------------------------------------------

class TestConditionalGate:

    def test_no_chains_file_produces_false_flag(self):
        """When attack-chains.md does not exist, has-attack-chains should be false."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            has_chains, chains = prepare_attack_chains(target, [], TEMPLATE_DIR)
            assert has_chains is False
            assert chains == []

    def test_empty_chains_file_produces_false_flag(self):
        """When attack-chains.md exists but has no chains, return empty."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / "attack-chains.md").write_text(SAMPLE_NO_CHAINS_MD, encoding="utf-8")
            has_chains, chains = prepare_attack_chains(target, [], TEMPLATE_DIR)
            assert has_chains is False
            assert chains == []

    def test_valid_chains_file_produces_true_flag(self):
        """When attack-chains.md has valid chains, return True and chain data."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / "attack-chains.md").write_text(SAMPLE_ATTACK_CHAINS_MD, encoding="utf-8")
            has_chains, chains = prepare_attack_chains(target, [], TEMPLATE_DIR)
            assert has_chains is True
            assert len(chains) == 2
