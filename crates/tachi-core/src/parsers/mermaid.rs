use std::collections::{BTreeMap, BTreeSet};

pub const VALID_ASSET_TAGS: [&str; 6] = ["pii", "phi", "auth", "secrets", "financial", "safety"];

pub fn parse_component_asset_map(content: &str) -> BTreeMap<String, Vec<String>> {
    let mut result: BTreeMap<String, Vec<String>> = BTreeMap::new();
    if content.trim().is_empty() {
        return result;
    }

    for block in select_mermaid_scan_blocks(content) {
        for line in block.lines() {
            let mut rest = line;
            let mut consumed = 0;
            while let Some(quote_start) = rest.find('"') {
                let absolute_quote_start = consumed + quote_start;
                let label_start = quote_start + 1;
                let Some(relative_quote_end) = rest[label_start..].find('"') else {
                    break;
                };
                let label_end = label_start + relative_quote_end;
                let label = &rest[label_start..label_end];

                if let Some(raw_tags) = asset_block_body(label) {
                    let node_id = node_id_before_quote(line, absolute_quote_start);
                    let tags = normalize_asset_tags(&raw_tags, &node_id);
                    if !tags.is_empty() {
                        let display_name = extract_asset_display_name(label);
                        let key = if display_name.is_empty() {
                            node_id
                        } else {
                            display_name
                        };
                        merge_asset_tags(&mut result, key, tags);
                    }
                }

                consumed += label_end + 1;
                rest = &rest[label_end + 1..];
            }
        }
    }

    result
}

fn merge_asset_tags(result: &mut BTreeMap<String, Vec<String>>, key: String, tags: Vec<String>) {
    let Some(existing) = result.get_mut(&key) else {
        result.insert(key, tags);
        return;
    };

    let before = existing.clone();
    let mut merged = existing
        .iter()
        .cloned()
        .chain(tags)
        .collect::<BTreeSet<_>>()
        .into_iter()
        .collect::<Vec<_>>();
    if merged != before {
        eprintln!(
            "Warning: component {key:?} has multiple asset declarations; merged tags: {merged:?}"
        );
    }
    std::mem::swap(existing, &mut merged);
}

fn select_mermaid_scan_blocks(content: &str) -> Vec<&str> {
    let mut blocks = Vec::new();
    let mut cursor = 0;
    while let Some(start) = content[cursor..].find("```mermaid") {
        let fence_start = cursor + start;
        let Some(block_start_offset) = content[fence_start..].find('\n') else {
            break;
        };
        let block_start = fence_start + block_start_offset + 1;
        let Some(block_end_offset) = content[block_start..].find("\n```") else {
            break;
        };
        let block_end = block_start + block_end_offset;
        blocks.push(&content[block_start..block_end]);
        cursor = block_end + 4;
    }

    if blocks.is_empty() {
        vec![content]
    } else {
        blocks
    }
}

fn asset_block_body(label: &str) -> Option<String> {
    let lower = label.to_ascii_lowercase();
    let start = lower.find("[asset:")?;
    let body_start = start + "[asset:".len();
    let body_end = lower[body_start..].find(']')? + body_start;
    Some(label[body_start..body_end].trim().to_string())
}

fn node_id_before_quote(line: &str, quote_start: usize) -> String {
    let prefix = &line[..quote_start];
    let mut end = prefix.len();
    let bytes = prefix.as_bytes();

    while end > 0 {
        let ch = bytes[end - 1] as char;
        if ch.is_ascii_whitespace() || matches!(ch, '[' | '(' | '{') {
            end -= 1;
        } else {
            break;
        }
    }

    let mut start = end;
    while start > 0 {
        let ch = bytes[start - 1] as char;
        if ch.is_ascii_alphanumeric() || ch == '_' {
            start -= 1;
        } else {
            break;
        }
    }

    prefix[start..end].to_string()
}

fn normalize_asset_tags(raw: &str, node_id: &str) -> Vec<String> {
    let mut tags = BTreeSet::new();
    for candidate in raw.split(',') {
        let tag = candidate.trim().to_ascii_lowercase();
        if tag.is_empty() {
            continue;
        }
        if VALID_ASSET_TAGS.contains(&tag.as_str()) {
            tags.insert(tag);
        } else {
            eprintln!(
                "Warning: unknown asset tag {tag:?} on node {node_id:?}; valid tags: {:?}",
                VALID_ASSET_TAGS
            );
        }
    }
    tags.into_iter().collect()
}

fn extract_asset_display_name(label: &str) -> String {
    let without_asset = remove_asset_block(label);
    let without_breaks = replace_br_tags_with_space(&without_asset);
    without_breaks
        .split_whitespace()
        .collect::<Vec<_>>()
        .join(" ")
}

fn remove_asset_block(label: &str) -> String {
    let Some(start) = label.to_ascii_lowercase().find("[asset:") else {
        return label.to_string();
    };
    let Some(end_offset) = label[start..].find(']') else {
        return label.to_string();
    };
    let end = start + end_offset + 1;
    format!("{}{}", &label[..start], &label[end..])
}

fn replace_br_tags_with_space(input: &str) -> String {
    let mut output = String::with_capacity(input.len());
    let mut cursor = 0;
    let lower = input.to_ascii_lowercase();

    while let Some(offset) = lower[cursor..].find("<br") {
        let start = cursor + offset;
        output.push_str(&input[cursor..start]);
        let Some(end_offset) = lower[start..].find('>') else {
            output.push_str(&input[start..]);
            return output;
        };
        output.push(' ');
        cursor = start + end_offset + 1;
    }
    output.push_str(&input[cursor..]);
    output
}
