use std::collections::BTreeMap;

pub fn split_table_row(line: &str) -> Vec<String> {
    line.trim()
        .trim_matches('|')
        .split('|')
        .map(|cell| cell.trim().to_string())
        .collect()
}

pub fn is_separator_row(cells: &[String]) -> bool {
    !cells.is_empty()
        && cells.iter().all(|cell| {
            let stripped = cell.replace(' ', "");
            !stripped.is_empty() && stripped.chars().all(|c| c == '-' || c == ':')
        })
}

pub fn parse_markdown_table(content: &str, section_header: &str) -> Vec<BTreeMap<String, String>> {
    let mut in_section = false;
    let mut header: Option<Vec<String>> = None;
    let mut rows = Vec::new();

    for raw_line in content.lines() {
        let line = raw_line.trim();
        if line == section_header {
            in_section = true;
            header = None;
            continue;
        }

        if !in_section {
            continue;
        }

        if line.starts_with('#') && line != section_header {
            break;
        }

        if !line.starts_with('|') {
            continue;
        }

        let cells = split_table_row(line);
        if cells.is_empty() {
            continue;
        }

        if header.is_none() {
            if is_separator_row(&cells) {
                continue;
            }
            header = Some(cells);
            continue;
        }

        if is_separator_row(&cells) {
            continue;
        }

        let Some(header_cells) = header.as_ref() else {
            continue;
        };

        let mut row = BTreeMap::new();
        for (idx, key) in header_cells.iter().enumerate() {
            let value = cells.get(idx).cloned().unwrap_or_default();
            row.insert(key.clone(), value);
        }
        rows.push(row);
    }

    rows
}
