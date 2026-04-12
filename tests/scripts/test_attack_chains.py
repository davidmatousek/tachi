"""Unit tests for attack chain parsing and correlation engine logic.

Tests parse_attack_chains() from tachi_parsers.py and validates
chain detection, ranking, chain-breaking heuristic, determinism,
and edge cases.
"""

import sys
from pathlib import Path

import pytest

# Add scripts/ to path for direct import of tachi_parsers
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from tachi_parsers import parse_attack_chains, detect_artifacts


# =============================================================================
# Fixtures: Mock attack-chains.md content
# =============================================================================

MOCK_CHAIN_ARTIFACT = """\
---
schema_version: "1.0"
date: "2026-04-12"
chain_count: 2
surfaced_count: 2
---

# Cross-Layer Attack Chains

## 1. Chain Summary

| Chain ID | Title | Layers | Max Severity | Finding Count | Chain-Breaking Target |
|----------|-------|--------|--------------|---------------|-----------------------|
| CHAIN-001 | Data Poisoning to Agent Hijack | L2 \u2192 L3 \u2192 L7 | Critical | 3 | T-3 |
| CHAIN-002 | Infrastructure Exploit to Auth Bypass | L4 \u2192 L6 | High | 2 | E-2 |

## 2. Chain Details

### CHAIN-001: Data Poisoning to Agent Hijack

**Layers**: L2 \u2192 L3 \u2192 L7
**Max Severity**: Critical
**Surfaced**: Yes

#### Member Findings

| Finding ID | MAESTRO Layer | Role | Component | Category | Severity |
|------------|---------------|------|-----------|----------|----------|
| T-3 | L2 | initial_exploit | Vector DB | Tampering | High |
| S-5 | L3 | intermediate_cascade | Agent Orchestrator | Spoofing | Critical |
| AG-2 | L7 | terminal_impact | Multi-Agent Supervisor | Agentic | High |

#### Attack Progression

An attacker poisons the vector database at L2 (Data Operations) by injecting malicious embeddings into the RAG retrieval pipeline. This tampering enables a spoofing attack at L3 (Agent Framework) where the agent orchestrator acts on corrupted context, impersonating trusted workflow instructions. The compromised agent behavior triggers unauthorized actions at L7 (Agent Ecosystem) where the multi-agent supervisor executes commands outside its authorized scope, manifesting as a full agent hijack with potential data exfiltration through the ecosystem interface. Remediating T-3 at L2 would break this chain by preventing poisoned data from reaching the agent framework.

#### Chain-Breaking Controls

**Target**: T-3 (L2 \u2014 Data Operations)
**Rationale**: Removing this finding at L2 disconnects 0 upstream findings from 2 downstream findings in the chain
**Recommendation**: Implement input validation and integrity checking on vector store embeddings before RAG retrieval
**Note**: This is a heuristic recommendation based on structural centrality analysis, not verified control effectiveness.

### CHAIN-002: Infrastructure Exploit to Auth Bypass

**Layers**: L4 \u2192 L6
**Max Severity**: High
**Surfaced**: Yes

#### Member Findings

| Finding ID | MAESTRO Layer | Role | Component | Category | Severity |
|------------|---------------|------|-----------|----------|----------|
| T-7 | L4 | initial_exploit | API Gateway | Tampering | High |
| E-2 | L6 | terminal_impact | Auth Service | Privilege-Escalation | High |

#### Attack Progression

An attacker exploits a tampering vulnerability at L4 (Deployment Infrastructure) by manipulating the API gateway configuration to redirect authentication traffic. This infrastructure compromise triggers a privilege escalation at L6 (Security and Compliance) where the auth service grants elevated permissions due to bypassed validation rules, manifesting as unauthorized access to protected resources. Remediating E-2 at L6 would break this chain by hardening the authentication boundary.

#### Chain-Breaking Controls

**Target**: E-2 (L6 \u2014 Security and Compliance)
**Rationale**: Higher severity finding in a 1-link chain
**Recommendation**: Implement defense-in-depth authentication with server-side token validation independent of gateway routing
**Note**: This is a heuristic recommendation based on structural centrality analysis, not verified control effectiveness.
"""

MOCK_SINGLE_LAYER = """\
---
schema_version: "1.0"
date: "2026-04-12"
chain_count: 0
surfaced_count: 0
---

# Cross-Layer Attack Chains

No cross-layer attack chains detected.
"""

MOCK_SEVEN_LAYER_CHAIN = """\
---
schema_version: "1.0"
date: "2026-04-12"
chain_count: 1
surfaced_count: 1
---

# Cross-Layer Attack Chains

## 2. Chain Details

### CHAIN-001: Full Stack Compromise

**Layers**: L1 \u2192 L2 \u2192 L3 \u2192 L4 \u2192 L5 \u2192 L6 \u2192 L7
**Max Severity**: Critical
**Surfaced**: Yes

#### Member Findings

| Finding ID | MAESTRO Layer | Role | Component | Category | Severity |
|------------|---------------|------|-----------|----------|----------|
| T-1 | L1 | initial_exploit | LLM Service | Tampering | High |
| T-2 | L2 | intermediate_cascade | Vector DB | Tampering | High |
| S-3 | L3 | intermediate_cascade | Agent Orchestrator | Spoofing | Critical |
| T-4 | L4 | intermediate_cascade | API Gateway | Tampering | Medium |
| R-5 | L5 | intermediate_cascade | Audit Logger | Repudiation | Medium |
| T-6 | L6 | intermediate_cascade | Auth Service | Tampering | High |
| E-7 | L7 | terminal_impact | Admin Dashboard | Privilege-Escalation | Critical |

#### Attack Progression

A full-stack compromise begins at L1 where the foundation model is tampered with, triggering data corruption at L2 through poisoned model outputs. The corrupted data enables agent impersonation at L3, which cascades through infrastructure manipulation at L4, observability evasion at L5, security control bypass at L6, and manifests as unauthorized admin access at L7.

#### Chain-Breaking Controls

**Target**: S-3 (L3 \u2014 Agent Framework)
**Rationale**: Removing this finding at L3 disconnects 2 upstream findings from 4 downstream findings in the chain
**Recommendation**: Implement agent identity verification with cryptographic attestation
**Note**: This is a heuristic recommendation based on structural centrality analysis, not verified control effectiveness.
"""


# =============================================================================
# Test: Chain detection from mock finding sets
# =============================================================================

class TestParseAttackChains:
    """Tests for parse_attack_chains() function."""

    def test_parses_two_chains(self):
        """Parse a valid artifact with two chains."""
        chains = parse_attack_chains(MOCK_CHAIN_ARTIFACT)
        assert len(chains) == 2

    def test_chain_ids(self):
        """Chain IDs are correctly extracted."""
        chains = parse_attack_chains(MOCK_CHAIN_ARTIFACT)
        assert chains[0]["chain_id"] == "CHAIN-001"
        assert chains[1]["chain_id"] == "CHAIN-002"

    def test_chain_titles(self):
        """Chain titles are correctly extracted."""
        chains = parse_attack_chains(MOCK_CHAIN_ARTIFACT)
        assert chains[0]["title"] == "Data Poisoning to Agent Hijack"
        assert chains[1]["title"] == "Infrastructure Exploit to Auth Bypass"

    def test_chain_layers(self):
        """Layer progressions are correctly parsed from arrow-separated strings."""
        chains = parse_attack_chains(MOCK_CHAIN_ARTIFACT)
        assert chains[0]["layers"] == ["L2", "L3", "L7"]
        assert chains[1]["layers"] == ["L4", "L6"]

    def test_chain_max_severity(self):
        """Max severity is correctly extracted."""
        chains = parse_attack_chains(MOCK_CHAIN_ARTIFACT)
        assert chains[0]["max_severity"] == "Critical"
        assert chains[1]["max_severity"] == "High"

    def test_chain_surfaced(self):
        """Surfaced boolean is correctly parsed."""
        chains = parse_attack_chains(MOCK_CHAIN_ARTIFACT)
        assert chains[0]["surfaced"] is True
        assert chains[1]["surfaced"] is True

    def test_member_findings_count(self):
        """Member findings are correctly parsed."""
        chains = parse_attack_chains(MOCK_CHAIN_ARTIFACT)
        assert len(chains[0]["findings"]) == 3
        assert len(chains[1]["findings"]) == 2

    def test_member_finding_fields(self):
        """Member finding fields are correctly extracted."""
        chains = parse_attack_chains(MOCK_CHAIN_ARTIFACT)
        first_finding = chains[0]["findings"][0]
        assert first_finding["finding_id"] == "T-3"
        assert first_finding["maestro_layer"] == "L2"
        assert first_finding["role"] == "initial_exploit"
        assert first_finding["component"] == "Vector DB"
        assert first_finding["category"] == "Tampering"
        assert first_finding["severity"] == "High"

    def test_narrative_extracted(self):
        """Narrative text is extracted from Attack Progression section."""
        chains = parse_attack_chains(MOCK_CHAIN_ARTIFACT)
        narrative = chains[0]["narrative"]
        assert len(narrative) > 100
        assert "enables" in narrative or "triggers" in narrative
        assert "Vector DB" in narrative or "vector database" in narrative.lower()

    def test_chain_breaking_controls(self):
        """Chain-breaking controls are correctly parsed."""
        chains = parse_attack_chains(MOCK_CHAIN_ARTIFACT)
        controls = chains[0]["chain_breaking_controls"]
        assert len(controls) >= 1
        assert controls[0]["target_finding_id"] == "T-3"
        assert "L2" in controls[0]["target_layer"]

    def test_chain_breaking_recommendation(self):
        """Chain-breaking control has recommendation text."""
        chains = parse_attack_chains(MOCK_CHAIN_ARTIFACT)
        controls = chains[0]["chain_breaking_controls"]
        assert len(controls[0]["recommendation"]) > 0


# =============================================================================
# Test: Single-layer no-chain case
# =============================================================================

class TestNoChains:
    """Tests for architectures with no cross-layer chains."""

    def test_empty_content_returns_empty(self):
        """Empty content returns empty list."""
        assert parse_attack_chains("") == []

    def test_none_content_returns_empty(self):
        """None content returns empty list."""
        assert parse_attack_chains(None) == []

    def test_no_chain_sections_returns_empty(self):
        """Artifact with no chain detail sections returns empty list."""
        assert parse_attack_chains(MOCK_SINGLE_LAYER) == []

    def test_whitespace_only_returns_empty(self):
        """Whitespace-only content returns empty list."""
        assert parse_attack_chains("   \n\n  ") == []


# =============================================================================
# Test: Max 7-layer chain
# =============================================================================

class TestSevenLayerChain:
    """Tests for maximum-length chains spanning all 7 MAESTRO layers."""

    def test_seven_layer_chain_parsed(self):
        """A chain spanning all 7 MAESTRO layers is correctly parsed."""
        chains = parse_attack_chains(MOCK_SEVEN_LAYER_CHAIN)
        assert len(chains) == 1
        assert len(chains[0]["layers"]) == 7
        assert chains[0]["layers"] == ["L1", "L2", "L3", "L4", "L5", "L6", "L7"]

    def test_seven_layer_findings_count(self):
        """7-layer chain has 7 member findings."""
        chains = parse_attack_chains(MOCK_SEVEN_LAYER_CHAIN)
        assert len(chains[0]["findings"]) == 7

    def test_seven_layer_roles(self):
        """7-layer chain has correct role assignments."""
        chains = parse_attack_chains(MOCK_SEVEN_LAYER_CHAIN)
        findings = chains[0]["findings"]
        assert findings[0]["role"] == "initial_exploit"
        assert findings[-1]["role"] == "terminal_impact"
        for f in findings[1:-1]:
            assert f["role"] == "intermediate_cascade"

    def test_seven_layer_chain_breaking_centrality(self):
        """Chain-breaking target for 7-layer chain uses betweenness centrality."""
        chains = parse_attack_chains(MOCK_SEVEN_LAYER_CHAIN)
        controls = chains[0]["chain_breaking_controls"]
        assert len(controls) >= 1
        # For a 7-node linear chain, position 3 (S-3 at L3) has betweenness = 2*4=8
        # (equal to position 3), but S-3 has Critical severity — wins tiebreak
        assert controls[0]["target_finding_id"] == "S-3"


# =============================================================================
# Test: Ranking order verification
# =============================================================================

class TestChainRanking:
    """Tests for chain ranking order."""

    def test_chains_ordered_by_severity(self):
        """Chains are ordered Critical first, then High."""
        chains = parse_attack_chains(MOCK_CHAIN_ARTIFACT)
        assert chains[0]["max_severity"] == "Critical"
        assert chains[1]["max_severity"] == "High"


# =============================================================================
# Test: Determinism
# =============================================================================

class TestDeterminism:
    """Tests for deterministic output."""

    def test_same_input_same_output(self):
        """Parsing the same artifact twice produces identical results."""
        chains_1 = parse_attack_chains(MOCK_CHAIN_ARTIFACT)
        chains_2 = parse_attack_chains(MOCK_CHAIN_ARTIFACT)
        assert chains_1 == chains_2

    def test_chain_ids_sequential(self):
        """Chain IDs are sequentially numbered."""
        chains = parse_attack_chains(MOCK_CHAIN_ARTIFACT)
        for i, chain in enumerate(chains, start=1):
            expected_id = f"CHAIN-{i:03d}"
            assert chain["chain_id"] == expected_id


# =============================================================================
# Test: Many-to-many finding membership
# =============================================================================

MOCK_SHARED_FINDING = """\
---
schema_version: "1.0"
date: "2026-04-12"
chain_count: 2
surfaced_count: 2
---

# Cross-Layer Attack Chains

## 2. Chain Details

### CHAIN-001: Path A via Shared Component

**Layers**: L2 \u2192 L3
**Max Severity**: High
**Surfaced**: Yes

#### Member Findings

| Finding ID | MAESTRO Layer | Role | Component | Category | Severity |
|------------|---------------|------|-----------|----------|----------|
| T-3 | L2 | initial_exploit | Vector DB | Tampering | High |
| S-5 | L3 | terminal_impact | Agent Orchestrator | Spoofing | High |

#### Attack Progression

Data tampering at L2 enables agent spoofing at L3.

#### Chain-Breaking Controls

**Target**: T-3 (L2)
**Rationale**: Higher severity in 1-link chain
**Recommendation**: Validate vector store inputs

### CHAIN-002: Path B via Shared Component

**Layers**: L2 \u2192 L7
**Max Severity**: High
**Surfaced**: Yes

#### Member Findings

| Finding ID | MAESTRO Layer | Role | Component | Category | Severity |
|------------|---------------|------|-----------|----------|----------|
| T-3 | L2 | initial_exploit | Vector DB | Tampering | High |
| I-8 | L7 | terminal_impact | Chat UI | Info-Disclosure | High |

#### Attack Progression

Data tampering at L2 manifests as information disclosure at L7.

#### Chain-Breaking Controls

**Target**: T-3 (L2)
**Rationale**: Higher severity in 1-link chain
**Recommendation**: Validate vector store inputs
"""


class TestManyToMany:
    """Tests for findings participating in multiple chains."""

    def test_shared_finding_in_multiple_chains(self):
        """A finding can appear in multiple chains (many-to-many)."""
        chains = parse_attack_chains(MOCK_SHARED_FINDING)
        assert len(chains) == 2
        # T-3 appears in both chains
        chain1_ids = [f["finding_id"] for f in chains[0]["findings"]]
        chain2_ids = [f["finding_id"] for f in chains[1]["findings"]]
        assert "T-3" in chain1_ids
        assert "T-3" in chain2_ids


# =============================================================================
# Test: detect_artifacts includes has_attack_chains
# =============================================================================

class TestDetectArtifacts:
    """Tests for detect_artifacts() attack-chains detection."""

    def test_no_attack_chains_file(self, tmp_path):
        """detect_artifacts returns False when no attack-chains.md exists."""
        (tmp_path / "threats.md").write_text("# Threat Model")
        artifacts = detect_artifacts(tmp_path)
        assert artifacts["has_attack_chains"] is False

    def test_attack_chains_file_present(self, tmp_path):
        """detect_artifacts returns True when attack-chains.md exists and is non-empty."""
        (tmp_path / "threats.md").write_text("# Threat Model")
        (tmp_path / "attack-chains.md").write_text("# Attack Chains\nContent here")
        artifacts = detect_artifacts(tmp_path)
        assert artifacts["has_attack_chains"] is True

    def test_empty_attack_chains_file(self, tmp_path):
        """detect_artifacts returns False when attack-chains.md is empty."""
        (tmp_path / "threats.md").write_text("# Threat Model")
        (tmp_path / "attack-chains.md").write_text("")
        artifacts = detect_artifacts(tmp_path)
        assert artifacts["has_attack_chains"] is False
