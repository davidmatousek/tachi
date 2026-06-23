use tachi_shell::commands::{
    command_dispatch_kind, command_registry, command_spec, CommandDispatchKind, CommandOutputKind,
    CommandRegistry, CommandSpec,
};

#[test]
fn typed_command_registry_exposes_output_kinds() {
    assert_eq!(
        command_spec("report-data")
            .expect("report-data spec")
            .output_kind,
        CommandOutputKind::Typst
    );
    assert_eq!(
        command_spec("coverage-audit")
            .expect("coverage-audit spec")
            .output_kind,
        CommandOutputKind::CoverageSummary
    );
    assert_eq!(
        command_spec("threats-sarif")
            .expect("threats-sarif spec")
            .output_kind,
        CommandOutputKind::ThreatsSarif
    );
    assert_eq!(
        command_spec("risk-scores-sarif")
            .expect("risk-scores-sarif spec")
            .output_kind,
        CommandOutputKind::RiskScoresSarif
    );
}

#[test]
fn typed_command_registry_exposes_dispatch_kinds() {
    assert_eq!(
        command_dispatch_kind("install").expect("install dispatch"),
        CommandDispatchKind::ControlPlane
    );
    assert_eq!(
        command_dispatch_kind("coverage-audit").expect("coverage-audit dispatch"),
        CommandDispatchKind::CoverageAudit
    );
    assert_eq!(
        command_dispatch_kind("report-data").expect("report-data dispatch"),
        CommandDispatchKind::ReportData
    );
}

#[test]
fn typed_command_registry_rejects_duplicate_names() {
    let registry = CommandRegistry::new(&[
        CommandSpec {
            name: "alpha",
            dispatch_kind: CommandDispatchKind::ControlPlane,
            output_kind: CommandOutputKind::Plain,
        },
        CommandSpec {
            name: "alpha",
            dispatch_kind: CommandDispatchKind::ControlPlane,
            output_kind: CommandOutputKind::Plain,
        },
    ]);

    let err = registry
        .validate_unique()
        .expect_err("duplicate names rejected");
    assert!(err.contains("duplicate command"));
}

#[test]
fn typed_command_registry_names_match_current_surface() {
    assert_eq!(
        command_registry().names(),
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
}
