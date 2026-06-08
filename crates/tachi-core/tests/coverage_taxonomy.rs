use pretty_assertions::assert_eq;

use tachi_core::coverage_taxonomy::{
    maestro_layer_catalog, normalize_maestro_layer_label, owasp_coverage_family_catalog,
    render_owasp_coverage_matrix,
};

#[test]
fn owasp_coverage_family_catalog_lists_the_shared_framework_rows_in_order() {
    let catalog = owasp_coverage_family_catalog();

    let labels: Vec<_> = catalog.iter().map(|entry| entry.framework).collect();
    assert_eq!(
        labels,
        [
            "LLM 2025",
            "Agentic 2026",
            "ML 2023",
            "Mobile 2024",
            "Web 2021",
            "API 2023",
        ]
    );

    assert_eq!(catalog[0].bucket, "OWASP-LLM-2025");
    assert_eq!(catalog[0].items, "LLM01-LLM10");
    assert_eq!(catalog[0].status, "10/10");
    assert!(catalog[0].anchor.starts_with("https://genai.owasp.org/"));
    assert_eq!(catalog[5].bucket, "OWASP-API-2023");
}

#[test]
fn render_owasp_coverage_matrix_uses_the_shared_catalog() {
    let rendered = render_owasp_coverage_matrix();

    assert!(rendered
        .contains("| Framework | Bucket | Items | Status | OWASP Anchor | Detection ADRs |"));
    assert!(rendered.contains("LLM 2025 | OWASP-LLM-2025 | LLM01-LLM10 | 10/10"));
    assert!(rendered.contains("API 2023 | OWASP-API-2023 | API1-API10 | 10/10"));
}

#[test]
fn maestro_layer_catalog_lists_the_canonical_layer_names_in_order() {
    let catalog = maestro_layer_catalog();

    let layer_ids: Vec<_> = catalog.iter().map(|entry| entry.layer_id).collect();
    assert_eq!(layer_ids, ["L1", "L2", "L3", "L4", "L5", "L6", "L7"]);

    assert_eq!(catalog[0].layer_name, "Foundation Model");
    assert_eq!(catalog[1].layer_name, "Data Operations");
    assert_eq!(catalog[2].layer_name, "Agent Framework");
    assert_eq!(catalog[3].layer_name, "Deployment Infrastructure");
    assert_eq!(catalog[4].layer_name, "Evaluation and Observability");
    assert_eq!(catalog[5].layer_name, "Security and Compliance");
    assert_eq!(catalog[6].layer_name, "Agent Ecosystem");

    assert!(catalog[4].aliases.contains(&"Infrastructure Controls"));
    assert!(catalog[5].aliases.contains(&"Agent Ecosystem"));
    assert!(catalog[6].aliases.contains(&"User Interface"));
}

#[test]
fn normalize_maestro_layer_label_maps_legacy_aliases_to_canonical_labels() {
    assert_eq!(
        normalize_maestro_layer_label("L5 — Security"),
        "L5 — Evaluation and Observability"
    );
    assert_eq!(
        normalize_maestro_layer_label("Infrastructure Controls"),
        "L5 — Evaluation and Observability"
    );
    assert_eq!(
        normalize_maestro_layer_label("Guardrails"),
        "L6 — Security and Compliance"
    );
    assert_eq!(
        normalize_maestro_layer_label("L6 — Agent Ecosystem"),
        "L6 — Security and Compliance"
    );
    assert_eq!(
        normalize_maestro_layer_label("User Interface"),
        "L7 — Agent Ecosystem"
    );
    assert_eq!(
        normalize_maestro_layer_label("L7 — Agent Ecosystem"),
        "L7 — Agent Ecosystem"
    );
}
