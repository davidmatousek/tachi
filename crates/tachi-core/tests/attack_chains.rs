use tachi_core::facade::detect_artifacts;
use tachi_core::facade::{
    generate_chain_mermaid, parse_attack_chains, AttackChain, AttackChainFinding,
};

const MOCK_CHAIN_ARTIFACT: &str = r#"---
schema_version: "1.0"
date: "2026-04-12"
chain_count: 2
surfaced_count: 2
---

# Cross-Layer Attack Chains

## 2. Chain Details

### CHAIN-001: Data Poisoning to Agent Hijack

**Layers**: L2 -> L3 -> L7
**Max Severity**: Critical
**Surfaced**: Yes

#### Member Findings

| Finding ID | MAESTRO Layer | Role | Component | Category | Severity |
|------------|---------------|------|-----------|----------|----------|
| T-3 | L2 | initial_exploit | Vector DB | Tampering | High |
| S-5 | L3 | intermediate_cascade | Agent Orchestrator | Spoofing | Critical |
| AG-2 | L7 | terminal_impact | Multi-Agent Supervisor | Agentic | High |

#### Attack Progression

An attacker poisons the vector database at L2 and compromises the agent
orchestrator before reaching the multi-agent supervisor at L7.

#### Chain-Breaking Controls

**Target**: T-3 (L2 - Data Operations)
**Rationale**: Removing this finding at L2 disconnects upstream findings.
**Recommendation**: Implement input validation and integrity checking.

### CHAIN-002: Infrastructure Exploit to Auth Bypass

**Layers**: L4 -> L6
**Max Severity**: High
**Surfaced**: Yes

#### Member Findings

| Finding ID | MAESTRO Layer | Role | Component | Category | Severity |
|------------|---------------|------|-----------|----------|----------|
| T-7 | L4 | initial_exploit | API Gateway | Tampering | High |
| E-2 | L6 | terminal_impact | Auth Service | Privilege-Escalation | High |

#### Attack Progression

An attacker exploits the API gateway and bypasses auth service validation.

#### Chain-Breaking Controls

**Target**: E-2 (L6 - Security and Compliance)
**Rationale**: Higher severity in a 1-link chain.
**Recommendation**: Implement defense-in-depth authentication.
"#;

const MOCK_SINGLE_LAYER: &str = r#"---
schema_version: "1.0"
date: "2026-04-12"
chain_count: 0
surfaced_count: 0
---

# Cross-Layer Attack Chains

No cross-layer attack chains detected.
"#;

const MOCK_SEVEN_LAYER_CHAIN: &str = r#"---
schema_version: "1.0"
date: "2026-04-12"
chain_count: 1
surfaced_count: 1
---

# Cross-Layer Attack Chains

## 2. Chain Details

### CHAIN-001: Full Stack Compromise

**Layers**: L1 -> L2 -> L3 -> L4 -> L5 -> L6 -> L7
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

**Target**: S-3 (L3 — Agent Framework)
**Rationale**: Removing this finding at L3 disconnects 2 upstream findings from 4 downstream findings in the chain
**Recommendation**: Implement agent identity verification with cryptographic attestation
**Note**: This is a heuristic recommendation based on structural centrality analysis, not verified control effectiveness.
"#;

#[test]
fn parse_attack_chains_extracts_chain_metadata_and_members() {
    let chains = parse_attack_chains(Some(MOCK_CHAIN_ARTIFACT));

    assert_eq!(chains.len(), 2);
    assert_eq!(chains[0].chain_id, "CHAIN-001");
    assert_eq!(chains[0].title, "Data Poisoning to Agent Hijack");
    assert_eq!(chains[0].layers, vec!["L2", "L3", "L7"]);
    assert_eq!(chains[0].max_severity, "Critical");
    assert!(chains[0].surfaced);
    assert_eq!(chains[0].findings.len(), 3);
    assert_eq!(chains[0].findings[0].finding_id, "T-3");
    assert_eq!(
        chains[0].chain_breaking_controls[0].target_finding_id,
        "T-3"
    );
    assert!(chains[0].narrative.contains("poisons the vector database"));

    assert_eq!(chains[1].chain_id, "CHAIN-002");
    assert_eq!(chains[1].layers, vec!["L4", "L6"]);
    assert_eq!(chains[1].max_severity, "High");
}

#[test]
fn parse_attack_chains_extracts_findings_and_controls_in_order() {
    let chains = parse_attack_chains(Some(MOCK_CHAIN_ARTIFACT));
    let findings = &chains[0].findings;

    assert_eq!(findings.len(), 3);
    assert_eq!(findings[0].finding_id, "T-3");
    assert_eq!(findings[0].maestro_layer, "L2");
    assert_eq!(findings[0].role, "initial_exploit");
    assert_eq!(findings[0].component, "Vector DB");
    assert_eq!(findings[0].category, "Tampering");
    assert_eq!(findings[0].severity, "High");
    assert_eq!(findings[2].finding_id, "AG-2");

    let controls = &chains[0].chain_breaking_controls;
    assert_eq!(controls.len(), 1);
    assert_eq!(controls[0].target_finding_id, "T-3");
    assert!(controls[0].target_layer.contains("L2"));
}

#[test]
fn parse_attack_chains_handles_seven_layer_and_no_chain_cases() {
    let chains = parse_attack_chains(Some(MOCK_SEVEN_LAYER_CHAIN));

    assert_eq!(chains.len(), 1);
    assert_eq!(
        chains[0].layers,
        vec!["L1", "L2", "L3", "L4", "L5", "L6", "L7"]
    );
    assert_eq!(chains[0].findings.len(), 7);
    assert_eq!(
        chains[0].chain_breaking_controls[0].target_finding_id,
        "S-3"
    );
    assert!(chains[0].narrative.contains("full-stack compromise"));

    assert!(parse_attack_chains(Some(MOCK_SINGLE_LAYER)).is_empty());
    assert!(parse_attack_chains(None).is_empty());
    assert!(parse_attack_chains(Some("")).is_empty());
    assert!(parse_attack_chains(Some("   \n\n  ")).is_empty());
}

#[test]
fn parse_attack_chains_returns_empty_for_missing_or_unparseable_content() {
    assert!(parse_attack_chains(None).is_empty());
    assert!(parse_attack_chains(Some("")).is_empty());
    assert!(parse_attack_chains(Some("   \n\n  ")).is_empty());
    assert!(parse_attack_chains(Some("# Cross-Layer Attack Chains\nNo chains here")).is_empty());
}

#[test]
fn detect_artifacts_marks_attack_chains_as_present_when_file_exists() {
    let root = std::env::temp_dir().join("tachi-core-attack-chains-artifacts");
    let _ = std::fs::remove_dir_all(&root);
    std::fs::create_dir_all(&root).expect("create temp root");
    std::fs::write(root.join("threats.md"), "# Threat Model").expect("write threats");
    std::fs::write(root.join("attack-chains.md"), "attack chains").expect("write chains");

    let artifacts = detect_artifacts(&root);

    assert!(artifacts.has_attack_chains);

    std::fs::remove_dir_all(root).ok();
}

#[test]
fn detect_artifacts_ignores_empty_attack_chains_files() {
    let root = std::env::temp_dir().join("tachi-core-attack-chains-empty");
    let _ = std::fs::remove_dir_all(&root);
    std::fs::create_dir_all(&root).expect("create temp root");
    std::fs::write(root.join("threats.md"), "# Threat Model").expect("write threats");
    std::fs::write(root.join("attack-chains.md"), "").expect("write empty chains");

    let artifacts = detect_artifacts(&root);

    assert!(!artifacts.has_attack_chains);

    std::fs::remove_dir_all(root).ok();
}

#[test]
fn detect_artifacts_keeps_attack_chains_absent_when_file_missing() {
    let root = std::env::temp_dir().join("tachi-core-attack-chains-missing");
    let _ = std::fs::remove_dir_all(&root);
    std::fs::create_dir_all(&root).expect("create temp root");
    std::fs::write(root.join("threats.md"), "# Threat Model").expect("write threats");

    let artifacts = detect_artifacts(&root);

    assert!(!artifacts.has_attack_chains);

    std::fs::remove_dir_all(root).ok();
}

#[test]
fn generate_chain_mermaid_renders_layers_and_edges() {
    let chain = AttackChain {
        chain_id: String::from("CHAIN-001"),
        title: String::from("Test Chain"),
        layers: vec![String::from("L2"), String::from("L3"), String::from("L7")],
        max_severity: String::from("Critical"),
        findings: vec![
            AttackChainFinding {
                finding_id: String::from("T-3"),
                maestro_layer: String::from("L2 — Data Operations"),
                role: String::from("initial_exploit"),
                component: String::from("Vector DB"),
                category: String::from("Tampering"),
                severity: String::from("High"),
            },
            AttackChainFinding {
                finding_id: String::from("S-5"),
                maestro_layer: String::from("L3 — Agent Framework"),
                role: String::from("intermediate_cascade"),
                component: String::from("Agent Orchestrator"),
                category: String::from("Spoofing"),
                severity: String::from("Critical"),
            },
            AttackChainFinding {
                finding_id: String::from("AG-2"),
                maestro_layer: String::from("L7 — Agent Ecosystem"),
                role: String::from("terminal_impact"),
                component: String::from("Multi-Agent Supervisor"),
                category: String::from("Agentic"),
                severity: String::from("High"),
            },
        ],
        narrative: String::new(),
        chain_breaking_controls: Vec::new(),
        surfaced: true,
    };

    let mermaid = generate_chain_mermaid(&chain);

    assert!(mermaid.starts_with("flowchart TD"));
    assert!(mermaid.contains("L2: Data Operations"));
    assert!(mermaid.contains("L3: Agent Framework"));
    assert!(mermaid.contains("L7: Agent Ecosystem"));
    assert!(mermaid.contains("T-3"));
    assert!(mermaid.contains("S-5"));
    assert!(mermaid.contains("AG-2"));
    assert_eq!(mermaid.matches("-->|").count(), 2);
}

#[test]
fn generate_chain_mermaid_returns_empty_for_empty_findings() {
    let chain = AttackChain::default();

    assert_eq!(generate_chain_mermaid(&chain), "");
}
