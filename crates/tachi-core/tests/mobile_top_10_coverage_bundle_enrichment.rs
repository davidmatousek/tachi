use std::fs;
use std::path::{Path, PathBuf};

use serde_yaml::Value;

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

fn read_text(path: &Path) -> String {
    fs::read_to_string(path).expect("read text")
}

fn read_yaml(path: &Path) -> Value {
    serde_yaml::from_str(&read_text(path)).expect("parse yaml")
}

fn extract_first_yaml_block(content: &str) -> Value {
    let mut in_block = false;
    let mut yaml = String::new();
    for line in content.lines() {
        if !in_block {
            if line.trim() == "```yaml" {
                in_block = true;
            }
            continue;
        }
        if line.trim() == "```" {
            break;
        }
        yaml.push_str(line);
        yaml.push('\n');
    }
    serde_yaml::from_str(&yaml).expect("parse yaml block")
}

fn joined_refs(path: &Path) -> String {
    let yaml = read_yaml(path);
    let refs = yaml
        .get("references")
        .and_then(Value::as_sequence)
        .expect("references array");
    refs.iter()
        .map(|item| item.as_str().expect("reference string"))
        .collect::<Vec<_>>()
        .join(" | ")
}

const SPOOFING_AGENT: &str = ".claude/agents/tachi/spoofing.md";
const TAMPERING_AGENT: &str = ".claude/agents/tachi/tampering.md";
const INFO_DISCLOSURE_AGENT: &str = ".claude/agents/tachi/info-disclosure.md";
const PRIVILEGE_ESCALATION_AGENT: &str = ".claude/agents/tachi/privilege-escalation.md";
const REPUDIATION_AGENT: &str = ".claude/agents/tachi/repudiation.md";

const SPOOFING_COMPANION: &str = ".claude/skills/tachi-spoofing/references/detection-patterns.md";
const TAMPERING_COMPANION: &str = ".claude/skills/tachi-tampering/references/detection-patterns.md";
const INFO_DISCLOSURE_COMPANION: &str =
    ".claude/skills/tachi-info-disclosure/references/detection-patterns.md";
const PRIVILEGE_ESCALATION_COMPANION: &str =
    ".claude/skills/tachi-privilege-escalation/references/detection-patterns.md";
const REPUDIATION_COMPANION: &str =
    ".claude/skills/tachi-repudiation/references/detection-patterns.md";

const FIXTURE_DIR: &str = "tests/scripts/fixtures/mobile_top_10_coverage_bundle";

fn fixture(path: &str) -> PathBuf {
    workspace_root().join(FIXTURE_DIR).join(path)
}

#[test]
fn mobile_top_10_coverage_bundle_contract_is_rust_native() {
    assert!(
        !workspace_root()
            .join("tests/scripts/test_mobile_top_10_coverage_bundle_enrichment.py")
            .exists(),
        "mobile top 10 coverage bundle should live in Rust tests, not pytest"
    );
}

#[test]
fn line_caps_are_preserved_across_all_f7_artifacts() {
    let root = workspace_root();
    assert!(read_text(&root.join(SPOOFING_AGENT)).lines().count() <= 120);
    assert!(read_text(&root.join(TAMPERING_AGENT)).lines().count() <= 120);
    assert!(read_text(&root.join(INFO_DISCLOSURE_AGENT)).lines().count() <= 120);
    assert!(
        read_text(&root.join(PRIVILEGE_ESCALATION_AGENT))
            .lines()
            .count()
            <= 120
    );
    assert!(read_text(&root.join(REPUDIATION_AGENT)).lines().count() <= 120);
}

#[test]
fn enriched_files_do_not_reference_maestro() {
    let root = workspace_root();
    for relative in [
        SPOOFING_AGENT,
        TAMPERING_AGENT,
        INFO_DISCLOSURE_AGENT,
        PRIVILEGE_ESCALATION_AGENT,
        REPUDIATION_AGENT,
        SPOOFING_COMPANION,
        TAMPERING_COMPANION,
        INFO_DISCLOSURE_COMPANION,
        PRIVILEGE_ESCALATION_COMPANION,
        REPUDIATION_COMPANION,
    ] {
        assert!(
            !read_text(&root.join(relative))
                .to_lowercase()
                .contains("maestro"),
            "{relative} must be MAESTRO-free"
        );
    }
}

#[test]
fn pattern_category_disambiguation_sections_are_present() {
    let root = workspace_root();
    for relative in [
        SPOOFING_COMPANION,
        TAMPERING_COMPANION,
        INFO_DISCLOSURE_COMPANION,
        PRIVILEGE_ESCALATION_COMPANION,
        REPUDIATION_COMPANION,
    ] {
        let content = read_text(&root.join(relative));
        let matches = content
            .matches("## Pattern Category Disambiguation")
            .count();
        assert_eq!(
            matches, 1,
            "{relative} must contain one disambiguation header"
        );
    }
}

#[test]
fn companion_pattern_categories_are_present() {
    let root = workspace_root();
    let spoofing = read_text(&root.join(SPOOFING_COMPANION));
    assert!(spoofing.contains("## Pattern Category N+1 — Improper Mobile Credential Usage (M1)"));
    assert!(spoofing
        .contains("## Pattern Category N+2 — Insecure Mobile Authentication / Authorization (M3)"));

    let tampering = read_text(&root.join(TAMPERING_COMPANION));
    assert!(tampering.contains("## Pattern Category 11 — Mobile Supply Chain Integrity (M2)"));
    assert!(tampering.contains("## Pattern Category 12 — Mobile IPC Input Validation (M4)"));
    assert!(
        tampering.contains("## Pattern Category 13 — Insufficient Mobile Binary Protections (M7)")
    );

    let info = read_text(&root.join(INFO_DISCLOSURE_COMPANION));
    assert!(info.contains("## Pattern Category N+1 — Insecure Mobile Communication (M5)"));
    assert!(info.contains("## Pattern Category N+2 — Inadequate Mobile Privacy Controls (M6)"));
    assert!(info.contains("## Pattern Category N+3 — Insecure Mobile Data Storage (M9)"));
    assert!(info.contains("## Pattern Category N+4 — Insufficient Mobile Cryptography (M10)"));

    let privilege = read_text(&root.join(PRIVILEGE_ESCALATION_COMPANION));
    assert!(
        privilege.contains("## Pattern Category 11: Security Misconfiguration Privilege-Gain Variant — Mobile (OWASP M8:2024), Server-Side (OWASP A05:2021), and API-Specific (OWASP API8:2023)")
    );

    let repudiation = read_text(&root.join(REPUDIATION_COMPANION));
    assert!(repudiation.contains(
        "## Pattern Category 9: M8 Accountability-Loss Variant — Mobile Security Misconfiguration"
    ));
}

#[test]
fn fixture_references_arrays_are_catalog_resolvable() {
    let joined = joined_refs(&fixture(
        "valid_category_n_plus_1_spoofing_mobile_credential_finding.yaml",
    ));
    assert!(joined.contains("OWASP M1:2024"));
    let joined = joined_refs(&fixture(
        "valid_category_n_plus_2_spoofing_mobile_authentication_finding.yaml",
    ));
    assert!(joined.contains("OWASP M3:2024"));

    let joined = joined_refs(&fixture(
        "valid_category_11_tampering_mobile_supply_chain_finding.yaml",
    ));
    assert!(joined.contains("OWASP M2:2024"));
    let joined = joined_refs(&fixture(
        "valid_category_12_tampering_mobile_ipc_finding.yaml",
    ));
    assert!(joined.contains("OWASP M4:2024"));
    let joined = joined_refs(&fixture(
        "valid_category_13_tampering_mobile_binary_protections_finding.yaml",
    ));
    assert!(joined.contains("OWASP M7:2024"));

    let joined = joined_refs(&fixture(
        "valid_category_n_plus_1_info_disclosure_mobile_communication_finding.yaml",
    ));
    assert!(joined.contains("OWASP M5:2024"));
    let joined = joined_refs(&fixture(
        "valid_category_n_plus_2_info_disclosure_mobile_privacy_finding.yaml",
    ));
    assert!(joined.contains("OWASP M6:2024"));
    let joined = joined_refs(&fixture(
        "valid_category_n_plus_3_info_disclosure_mobile_data_storage_finding.yaml",
    ));
    assert!(joined.contains("OWASP M9:2024"));
    let joined = joined_refs(&fixture(
        "valid_category_n_plus_4_info_disclosure_mobile_cryptography_finding.yaml",
    ));
    assert!(joined.contains("OWASP M10:2024"));

    let joined = joined_refs(&fixture(
        "valid_category_11_privilege_escalation_mobile_misconfiguration_finding.yaml",
    ));
    assert!(joined.contains("OWASP M8:2024"));
    assert!(joined.contains("CWE-732"));
    assert!(joined.contains("MASVS-PLATFORM"));

    let joined = joined_refs(&fixture(
        "valid_category_9_repudiation_mobile_misconfiguration_finding.yaml",
    ));
    assert!(joined.contains("OWASP M8:2024"));
    assert!(joined.contains("CWE-778"));
    assert!(joined.contains("MASVS-CODE"));
}

#[test]
fn prose_only_attack_mobile_techniques_absent_from_references() {
    let mut all_refs = String::new();
    for path in [
        "valid_category_n_plus_1_spoofing_mobile_credential_finding.yaml",
        "valid_category_n_plus_2_spoofing_mobile_authentication_finding.yaml",
        "valid_category_11_tampering_mobile_supply_chain_finding.yaml",
        "valid_category_12_tampering_mobile_ipc_finding.yaml",
        "valid_category_13_tampering_mobile_binary_protections_finding.yaml",
        "valid_category_n_plus_1_info_disclosure_mobile_communication_finding.yaml",
        "valid_category_n_plus_2_info_disclosure_mobile_privacy_finding.yaml",
        "valid_category_n_plus_3_info_disclosure_mobile_data_storage_finding.yaml",
        "valid_category_n_plus_4_info_disclosure_mobile_cryptography_finding.yaml",
        "valid_category_11_privilege_escalation_mobile_misconfiguration_finding.yaml",
        "valid_category_9_repudiation_mobile_misconfiguration_finding.yaml",
    ] {
        if !all_refs.is_empty() {
            all_refs.push_str(" | ");
        }
        all_refs.push_str(&joined_refs(&fixture(path)));
    }

    for attack_mobile_id in ["T1474", "T1626", "T1398"] {
        assert!(
            !all_refs.contains(attack_mobile_id),
            "ATT&CK Mobile {attack_mobile_id} must not appear in any fixture references array"
        );
    }
}

#[test]
fn mandatory_read_directives_are_preserved() {
    let root = workspace_root();
    for relative in [
        SPOOFING_AGENT,
        TAMPERING_AGENT,
        INFO_DISCLOSURE_AGENT,
        PRIVILEGE_ESCALATION_AGENT,
        REPUDIATION_AGENT,
    ] {
        let content = read_text(&root.join(relative));
        assert!(content.contains("**MANDATORY**: Read"));
    }
}

#[test]
fn agent_metadata_includes_mobile_top_10_references() {
    let root = workspace_root();
    for (relative, expected) in [
        (SPOOFING_AGENT, &["M1:2024", "M3:2024"][..]),
        (TAMPERING_AGENT, &["M2:2024", "M4:2024", "M7:2024"][..]),
        (
            INFO_DISCLOSURE_AGENT,
            &["M5:2024", "M6:2024", "M9:2024", "M10:2024"][..],
        ),
        (PRIVILEGE_ESCALATION_AGENT, &["M8:2024"][..]),
        (REPUDIATION_AGENT, &["M8:2024"][..]),
    ] {
        let yaml = extract_first_yaml_block(&read_text(&root.join(relative)));
        let metadata = yaml
            .get("owasp_references")
            .and_then(Value::as_sequence)
            .expect("owasp_references");
        let joined = metadata
            .iter()
            .map(|item| item.as_str().expect("reference string"))
            .collect::<Vec<_>>()
            .join(" | ");
        assert!(
            expected.iter().all(|token| joined.contains(token)),
            "{relative} metadata must reference one of {:?}; got {joined}",
            expected
        );
    }
}
