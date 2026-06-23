use proptest::prelude::*;
use tachi_core::infographic::largest_remainder;
use tachi_core::normalization::{normalize_lower_text, normalize_optional_text};
use tachi_core::parsers::parse_threats_findings;

#[test]
fn normalize_lower_text_handles_generated_ascii_variants() {
    for input in [
        "",
        "Alpha",
        " alpha ",
        "ALPHA-BETA",
        "  Mixed Case  ",
        "1234",
        "A B C",
        "Tabs\tStay",
    ] {
        let actual = normalize_lower_text(input);
        assert_eq!(actual, actual.trim());
        assert_eq!(actual, input.trim().to_ascii_lowercase());
        assert!(actual.chars().all(|c| !c.is_ascii_uppercase()));
    }
}

#[test]
fn normalize_optional_text_handles_generated_presence_and_blank_cases() {
    let cases = [
        (None, None),
        (Some(""), None),
        (Some("   "), None),
        (Some("value"), Some(String::from("value"))),
        (Some("  value  "), Some(String::from("value"))),
        (Some("\ttrimmed\t"), Some(String::from("trimmed"))),
    ];

    for (input, expected) in cases {
        assert_eq!(normalize_optional_text(input), expected);
    }
}

proptest! {
    #[test]
    fn largest_remainder_preserves_totals_and_order(
        counts in prop::collection::btree_map("[a-z]{1,8}", 0usize..20, 0..6),
        target in 0usize..100,
    ) {
        let actual = largest_remainder(&counts, target);

        prop_assert_eq!(
            actual.keys().collect::<Vec<_>>(),
            counts.keys().collect::<Vec<_>>()
        );

        let actual_total: usize = actual.values().copied().sum();
        let counts_total: usize = counts.values().copied().sum();

        if counts_total == 0 {
            prop_assert_eq!(actual_total, 0);
            prop_assert!(actual.values().all(|value| *value == 0));
        } else {
            prop_assert_eq!(actual_total, target);
            prop_assert!(actual.values().all(|value| *value <= target));
        }
    }

    #[test]
    fn parse_threats_findings_preserves_generated_source_attribution_order(
        records in prop::collection::vec(source_attribution_record_strategy(), 1..6),
    ) {
        let borrowed = records
            .iter()
            .map(|(taxonomy, id, relationship)| {
                (taxonomy.as_str(), id.as_str(), relationship.as_str())
            })
            .collect::<Vec<_>>();
        let markdown = build_threats_markdown(&borrowed);
        let findings = parse_threats_findings(&markdown).expect("parse threats findings");
        let parsed = findings[0]
            .source_attribution
            .as_ref()
            .expect("source attribution");

        let parsed_records: Vec<_> = parsed
            .iter()
            .map(|record| {
                (
                    record.taxonomy.as_str(),
                    record.id.as_str(),
                    record.relationship.as_str(),
                )
            })
            .collect();

        prop_assert_eq!(parsed_records, borrowed);
    }

    #[test]
    fn parse_threats_findings_handles_generated_malformed_inputs_without_panicking(
        markdown in any::<String>(),
    ) {
        let result = std::panic::catch_unwind(|| parse_threats_findings(&markdown));
        prop_assert!(result.is_ok());
    }
}

fn build_threats_markdown(records: &[(&str, &str, &str)]) -> String {
    let source_attribution = records
        .iter()
        .map(|(taxonomy, id, relationship)| {
            format!("  - {{taxonomy: \"{taxonomy}\", id: \"{id}\", relationship: \"{relationship}\"}}")
        })
        .collect::<Vec<_>>()
        .join("\n");

    format!(
        "# Agentic AI Application\n\n## 7. Recommended Actions\n\n| Finding ID | Component | Threat | Risk Level | Mitigation | Status |\n| --- | --- | --- | --- | --- | --- |\n| AG-1 | Component | Threat | High | Mitigation | [NEW] |\n\n## 9. Source Attribution\n\n```yaml\nAG-1:\n{source_attribution}\n```\n"
    )
}

fn source_attribution_record_strategy() -> impl Strategy<Value = (String, String, String)> {
    (
        prop_oneof![
            Just(String::from("owasp")),
            Just(String::from("mitre-attack")),
            Just(String::from("mitre-atlas")),
            Just(String::from("nist-ai-rmf")),
            Just(String::from("cwe")),
        ],
        "[A-Z]{1,3}-[0-9]{1,3}",
        prop_oneof![
            Just(String::from("primary")),
            Just(String::from("related")),
            Just(String::from("derived")),
        ],
    )
}
