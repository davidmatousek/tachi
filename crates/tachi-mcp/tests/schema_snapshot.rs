use tachi_mcp::{build_tool_schema_snapshot, render_tool_schema_snapshot_json};

#[test]
fn tool_schema_snapshot_includes_required_fields_and_output_modes() {
    let snapshot = build_tool_schema_snapshot();

    assert_eq!(snapshot.version, 1);
    assert_eq!(snapshot.schemas.len(), 5);

    let coverage = snapshot
        .schemas
        .iter()
        .find(|schema| schema.command_name == "coverage-audit")
        .expect("coverage schema");
    assert_eq!(coverage.name, "tachi.coverage-audit");
    assert_eq!(
        coverage
            .input_fields
            .iter()
            .map(|field| {
                (
                    field.name.as_str(),
                    field.field_type.as_str(),
                    field.required,
                )
            })
            .collect::<Vec<_>>(),
        vec![("repo_root", "path", true), ("output_mode", "enum", false),]
    );
    assert_eq!(coverage.output_modes, vec!["in-band", "artifact"]);

    let report = snapshot
        .schemas
        .iter()
        .find(|schema| schema.command_name == "report-data")
        .expect("report schema");
    assert_eq!(
        report
            .input_fields
            .iter()
            .map(|field| {
                (
                    field.name.as_str(),
                    field.field_type.as_str(),
                    field.required,
                )
            })
            .collect::<Vec<_>>(),
        vec![
            ("target_dir", "path", true),
            ("template_dir", "path", true),
            ("output_mode", "enum", false),
        ]
    );

    let rendered = render_tool_schema_snapshot_json();
    assert!(rendered.contains("\"version\": 1"));
    assert!(rendered.contains("\"coverage-audit\""));
    assert!(rendered.contains("\"output_modes\""));
}
