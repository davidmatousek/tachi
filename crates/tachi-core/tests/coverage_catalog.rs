use pretty_assertions::assert_eq;

use tachi_core::coverage_family_catalog;

#[test]
fn coverage_family_catalog_exposes_the_rendered_sections_in_order() {
    let catalog = coverage_family_catalog();

    let labels: Vec<_> = catalog.iter().map(|entry| entry.label).collect();
    assert_eq!(
        labels,
        [
            "Unit",
            "Integration",
            "Smoke",
            "True end-to-end",
            "Support / regression",
        ]
    );

    assert_eq!(catalog[0].description, "Rust-native unit tests");
    assert_eq!(catalog[3].description, "Desktop and CLI acceptance checks");
}
