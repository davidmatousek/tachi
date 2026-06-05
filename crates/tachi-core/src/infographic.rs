use std::collections::BTreeMap;

use crate::parsers::{SeverityCounts, SEVERITY_ORDER};

pub const SEVERITY_COLORS: [(&str, &str); 5] = [
    ("Critical", "#DC2626"),
    ("High", "#EA580C"),
    ("Medium", "#CA8A04"),
    ("Low", "#2563EB"),
    ("Note", "#6B7280"),
];

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct SeverityPercentage {
    pub label: String,
    pub count: usize,
    pub percentage: usize,
    pub color: &'static str,
}

pub fn largest_remainder(
    percentages_map: &BTreeMap<String, usize>,
    target: usize,
) -> BTreeMap<String, usize> {
    let total: usize = percentages_map.values().sum();
    if percentages_map.is_empty() {
        return BTreeMap::new();
    }

    if total == 0 {
        return percentages_map
            .keys()
            .cloned()
            .map(|label| (label, 0))
            .collect();
    }

    let mut floors = BTreeMap::new();
    let mut remainders: Vec<(String, u128)> = Vec::with_capacity(percentages_map.len());
    let mut floor_sum = 0usize;
    let total = total as u128;
    let target_value = target;
    let target = target as u128;

    for (label, count) in percentages_map {
        let scaled = (*count as u128) * target;
        let floor = (scaled / total) as usize;
        let remainder = scaled % total;

        floor_sum += floor;
        floors.insert(label.clone(), floor);
        remainders.push((label.clone(), remainder));
    }

    let remaining = target_value.saturating_sub(floor_sum);
    remainders.sort_by(|left, right| right.1.cmp(&left.1).then_with(|| left.0.cmp(&right.0)));

    for (label, _) in remainders.into_iter().take(remaining) {
        if let Some(value) = floors.get_mut(&label) {
            *value += 1;
        }
    }

    floors
}

pub fn compute_severity_percentages(severity: &SeverityCounts) -> Vec<SeverityPercentage> {
    let counts = BTreeMap::from([
        (String::from("Critical"), severity.critical),
        (String::from("High"), severity.high),
        (String::from("Medium"), severity.medium),
        (String::from("Low"), severity.low),
    ]);

    let percentages = largest_remainder(&counts, 100);
    let mut result = Vec::with_capacity(SEVERITY_ORDER.len().saturating_sub(1));

    for label in SEVERITY_ORDER {
        if label == "Note" {
            continue;
        }

        let color = severity_color(label);
        result.push(SeverityPercentage {
            label: label.to_string(),
            count: *counts.get(label).unwrap_or(&0),
            percentage: *percentages.get(label).unwrap_or(&0),
            color,
        });
    }

    result
}

fn severity_color(label: &str) -> &'static str {
    match label {
        "Critical" => "#DC2626",
        "High" => "#EA580C",
        "Medium" => "#CA8A04",
        "Low" => "#2563EB",
        "Note" => "#6B7280",
        _ => "#6B7280",
    }
}
