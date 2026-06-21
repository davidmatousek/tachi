use std::collections::BTreeMap;

use serde_json::{Map, Value};

pub fn stable_trim_text(value: &str) -> &str {
    value.trim()
}

pub fn normalize_lower_text(value: &str) -> String {
    stable_trim_text(value).to_ascii_lowercase()
}

pub fn normalize_upper_text(value: &str) -> String {
    stable_trim_text(value).to_ascii_uppercase()
}

pub fn normalize_optional_text(value: Option<&str>) -> Option<String> {
    value
        .map(stable_trim_text)
        .filter(|text| !text.is_empty())
        .map(|text| text.to_string())
}

pub fn normalize_value(value: &Value) -> Value {
    match value {
        Value::Array(items) => Value::Array(items.iter().map(normalize_value).collect()),
        Value::Object(map) => Value::Object(stable_sort_map(map)),
        Value::String(text) => Value::String(stable_trim_text(text).to_string()),
        other => other.clone(),
    }
}

pub fn stable_sort_map(map: &Map<String, Value>) -> Map<String, Value> {
    let mut sorted = BTreeMap::new();
    for (key, value) in map {
        sorted.insert(key.clone(), normalize_value(value));
    }
    sorted.into_iter().collect()
}
