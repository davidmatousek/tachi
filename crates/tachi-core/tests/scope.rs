use tachi_core::parsers::{parse_component_distribution, parse_scope_data};

#[test]
fn parse_scope_data_reads_component_and_zone_tables() {
    let markdown = r#"
### Components

| Component | Type | Description |
| --- | --- | --- |
| API | Process | Serves requests |
| DB | Data Store | Stores records |

### Data Flows

| Source | Destination | Data | Protocol |
| --- | --- | --- | --- |
| API | DB | records | HTTPS |

### Trust Zones

| Zone | Trust Level | Components |
| --- | --- | --- |
| App | High | API |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
| --- | --- | --- | --- | --- |
| App -> DB | App | Data | API | auth |
"#;

    let scope = parse_scope_data(markdown);

    assert_eq!(scope.components.len(), 2);
    assert_eq!(scope.components[0].name, "API");
    assert_eq!(scope.components[1].kind, "Data Store");
    assert_eq!(scope.data_flows[0].source, "API");
    assert_eq!(scope.trust_boundaries[0].zone, "App");
    assert_eq!(scope.boundary_crossings[0].controls, "auth");
}

#[test]
fn parse_component_distribution_sorts_by_count_then_name() {
    let findings = vec![
        component("API"),
        component("API"),
        component("DB"),
        component("UI"),
        component("UI"),
    ];

    let distribution = parse_component_distribution(&findings);

    assert_eq!(
        distribution,
        vec![
            ("API".to_string(), 2),
            ("UI".to_string(), 2),
            ("DB".to_string(), 1),
        ]
    );
}

fn component(name: &str) -> std::collections::BTreeMap<String, String> {
    let mut row = std::collections::BTreeMap::new();
    row.insert("component".to_string(), name.to_string());
    row
}
