use std::collections::BTreeMap;
use std::fs;
use std::path::Path;

use crate::parsers::{parse_markdown_table, ThreatFinding, SEVERITY_ORDER};

#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct AttackTreeEntry {
    pub id: String,
    pub component: String,
    pub severity: String,
    pub title: String,
    pub mermaid_code: String,
    pub mitigation: String,
    pub narrative: String,
    pub remediation: String,
}

pub fn parse_attack_trees(
    target_dir: &Path,
    findings: &[ThreatFinding],
    tr_content: Option<&str>,
) -> Vec<AttackTreeEntry> {
    let findings_by_id = findings
        .iter()
        .filter(|finding| !finding.id.is_empty())
        .map(|finding| (finding.id.clone(), finding))
        .collect::<BTreeMap<_, _>>();

    let mut entries = Vec::new();
    let attack_trees_dir = target_dir.join("attack-trees");

    if attack_trees_dir.is_dir() {
        let mut tree_files = fs::read_dir(&attack_trees_dir)
            .map(|entries| {
                entries
                    .flatten()
                    .map(|entry| entry.path())
                    .filter(|path| {
                        path.extension()
                            .and_then(|ext| ext.to_str())
                            .is_some_and(|ext| ext.eq_ignore_ascii_case("md"))
                    })
                    .collect::<Vec<_>>()
            })
            .unwrap_or_default();
        tree_files.sort();

        for tree_file in tree_files {
            if let Some(entry) = parse_attack_tree_file(&tree_file, &findings_by_id) {
                entries.push(entry);
            }
        }
    }

    if entries.is_empty() {
        if let Some(tr_content) = tr_content {
            entries.extend(parse_inline_attack_trees(tr_content, &findings_by_id));
        }
    }

    entries.retain(|entry| severity_ordinal(&entry.severity) >= 3);
    entries.sort_by_key(|entry| {
        (
            -severity_ordinal(&entry.severity),
            entry.id.to_ascii_lowercase(),
        )
    });

    entries
}

fn parse_attack_tree_file(
    path: &Path,
    findings_by_id: &BTreeMap<String, &ThreatFinding>,
) -> Option<AttackTreeEntry> {
    let content = fs::read_to_string(path).ok()?;
    let mut meta = BTreeMap::new();
    let mut in_table = false;

    for line in content.lines() {
        let stripped = line.trim();
        if stripped.starts_with("| Field") {
            in_table = true;
            continue;
        }
        if in_table && stripped.starts_with("|---") {
            continue;
        }
        if in_table && stripped.starts_with('|') {
            let cells = stripped
                .split('|')
                .map(str::trim)
                .filter(|cell| !cell.is_empty())
                .collect::<Vec<_>>();
            if cells.len() >= 2 {
                meta.insert(cells[0].to_string(), cells[1].to_string());
            }
        } else if in_table && !stripped.starts_with('|') {
            in_table = false;
        }
    }

    let mut finding_id = meta.get("Finding ID").cloned().unwrap_or_default();
    let mut title = meta.get("Threat").cloned().unwrap_or_default();
    let component = meta.get("Component").cloned().unwrap_or_default();
    let severity = meta.get("Risk Level").cloned().unwrap_or_default();
    let mermaid_code = extract_mermaid_block(&content)?;

    if finding_id.is_empty() {
        for line in content.lines() {
            let stripped = line.trim();
            if !stripped.starts_with("# ") {
                continue;
            }
            let heading = stripped[2..].trim();
            if let Some(rest) = heading.strip_prefix("Attack Tree:") {
                if let Some((id, heading_title)) = rest.trim().split_once(" -- ") {
                    finding_id = id.trim().to_string();
                    if title.is_empty() {
                        title = heading_title.trim().to_string();
                    }
                    break;
                }
            }
            if let Some((id, heading_title)) = heading.split_once(':') {
                if id
                    .chars()
                    .all(|ch| ch.is_ascii_alphabetic() || ch == '-' || ch.is_ascii_digit())
                {
                    finding_id = id.trim().to_string();
                    if title.is_empty() {
                        title = heading_title.trim().to_string();
                    }
                    break;
                }
            }
        }
    }

    if finding_id.is_empty() {
        return None;
    }

    let fallback = findings_by_id.get(&finding_id);
    let component = if component.is_empty() {
        fallback
            .map(|finding| finding.component.clone())
            .unwrap_or_default()
    } else {
        component
    };
    let severity = if severity.is_empty() {
        fallback
            .map(|finding| finding.risk_level.clone())
            .unwrap_or_default()
    } else {
        severity
    };
    let title = if title.is_empty() {
        fallback
            .map(|finding| finding.threat.clone())
            .unwrap_or_default()
    } else {
        title
    };

    Some(AttackTreeEntry {
        id: finding_id,
        component,
        severity,
        title,
        mermaid_code,
        mitigation: fallback
            .map(|finding| finding.mitigation.clone())
            .unwrap_or_default(),
        narrative: String::new(),
        remediation: String::new(),
    })
}

fn parse_inline_attack_trees(
    tr_content: &str,
    findings_by_id: &BTreeMap<String, &ThreatFinding>,
) -> Vec<AttackTreeEntry> {
    let mut entries = Vec::new();
    let rows = parse_markdown_table(tr_content, "## 5. Attack Trees");

    for row in rows {
        let finding_id = row.get("Finding ID").cloned().unwrap_or_default();
        if finding_id.is_empty() {
            continue;
        }

        let severity = row.get("Risk Level").cloned().unwrap_or_default();
        let title = row.get("Threat").cloned().unwrap_or_default();
        let component = row.get("Component").cloned().unwrap_or_default();
        let fallback = findings_by_id.get(&finding_id);

        entries.push(AttackTreeEntry {
            id: finding_id,
            component: if component.is_empty() {
                fallback
                    .map(|finding| finding.component.clone())
                    .unwrap_or_default()
            } else {
                component
            },
            severity: if severity.is_empty() {
                fallback
                    .map(|finding| finding.risk_level.clone())
                    .unwrap_or_default()
            } else {
                severity
            },
            title: if title.is_empty() {
                fallback
                    .map(|finding| finding.threat.clone())
                    .unwrap_or_default()
            } else {
                title
            },
            mermaid_code: row.get("Mermaid").cloned().unwrap_or_default(),
            mitigation: fallback
                .map(|finding| finding.mitigation.clone())
                .unwrap_or_default(),
            narrative: String::new(),
            remediation: String::new(),
        });
    }

    entries
}

fn extract_mermaid_block(content: &str) -> Option<String> {
    let start = content.find("```mermaid")?;
    let rest = &content[start + "```mermaid".len()..];
    let end = rest.find("```")?;
    Some(rest[..end].trim().to_string())
}

fn severity_ordinal(value: &str) -> isize {
    SEVERITY_ORDER
        .iter()
        .position(|candidate| candidate.eq_ignore_ascii_case(value))
        .map(|idx| (SEVERITY_ORDER.len() - idx) as isize)
        .unwrap_or_default()
}
