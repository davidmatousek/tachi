use std::collections::BTreeMap;

use tachi_core::infographic::largest_remainder;
use tachi_core::normalization::{normalize_lower_text, normalize_optional_text};

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

#[test]
fn largest_remainder_preserves_totals_and_order_across_generated_cases() {
    let cases = [
        (vec![("critical", 0), ("high", 0), ("medium", 0), ("low", 0)], 100),
        (vec![("critical", 1), ("high", 1), ("medium", 1), ("low", 1)], 100),
        (vec![("critical", 9), ("high", 3), ("medium", 0), ("low", 0)], 100),
        (vec![("critical", 2), ("high", 7), ("medium", 11), ("low", 13)], 37),
        (vec![("critical", 5), ("high", 0), ("medium", 0), ("low", 1)], 12),
    ];

    for (counts, target) in cases {
        let counts = counts
            .into_iter()
            .map(|(label, count)| (label.to_string(), count))
            .collect::<BTreeMap<_, _>>();
        let actual = largest_remainder(&counts, target);

        assert_eq!(actual.len(), counts.len());
        assert_eq!(
            actual.keys().collect::<Vec<_>>(),
            counts.keys().collect::<Vec<_>>()
        );

        let actual_total: usize = actual.values().copied().sum();
        let counts_total: usize = counts.values().copied().sum();
        if counts_total == 0 {
            assert_eq!(actual_total, 0);
            assert!(actual.values().all(|value| *value == 0));
        } else {
            assert_eq!(actual_total, target);
            assert!(actual.values().all(|value| *value <= target));
        }
    }
}
