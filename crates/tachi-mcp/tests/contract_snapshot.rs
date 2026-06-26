use tachi_mcp::{build_contract_snapshot, contract_hash, render_contract_snapshot_json};

#[test]
fn contract_snapshot_includes_version_hash_and_canonical_commands() {
    let snapshot = build_contract_snapshot();

    assert_eq!(snapshot.version, 1);
    assert_eq!(
        snapshot
            .commands
            .iter()
            .map(|command| command.name.as_str())
            .collect::<Vec<_>>(),
        vec![
            "install",
            "init",
            "update",
            "bootstrap",
            "infographic-data",
            "coverage-audit",
            "report-data",
            "risk-scores-sarif",
            "threats-sarif",
        ]
    );
    assert_eq!(snapshot.command_hash, contract_hash(&snapshot.commands));
    assert!(render_contract_snapshot_json().contains("\"version\": 1"));
    assert!(render_contract_snapshot_json().contains("\"command_hash\":"));
}
