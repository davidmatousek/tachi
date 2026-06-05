use tachi_core::artifacts::detect_artifacts;
use tachi_core::attack_chains::parse_attack_chains;

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
