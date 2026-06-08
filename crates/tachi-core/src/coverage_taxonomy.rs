#[derive(Clone, Debug, PartialEq, Eq)]
pub struct OwaspCoverageFamily {
    pub framework: &'static str,
    pub bucket: &'static str,
    pub items: &'static str,
    pub status: &'static str,
    pub anchor: &'static str,
    pub detection_adrs: &'static [&'static str],
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct MaestroLayer {
    pub layer_id: &'static str,
    pub layer_name: &'static str,
    pub description: &'static str,
    pub aliases: &'static [&'static str],
}

pub const MAESTRO_LAYERS: [&str; 7] = ["L1", "L2", "L3", "L4", "L5", "L6", "L7"];

pub fn owasp_coverage_family_catalog() -> Vec<OwaspCoverageFamily> {
    vec![
        OwaspCoverageFamily {
            framework: "LLM 2025",
            bucket: "OWASP-LLM-2025",
            items: "LLM01-LLM10",
            status: "10/10",
            anchor: "https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/",
            detection_adrs: &["ADR-030", "ADR-031", "ADR-034", "ADR-045"],
        },
        OwaspCoverageFamily {
            framework: "Agentic 2026",
            bucket: "OWASP-AGENTIC-2026",
            items: "ASI01-ASI10",
            status: "10/10",
            anchor: "https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/",
            detection_adrs: &["ADR-032", "ADR-033"],
        },
        OwaspCoverageFamily {
            framework: "ML 2023",
            bucket: "OWASP-ML-2023",
            items: "ML01-ML10",
            status: "10/10",
            anchor: "https://owasp.org/www-project-machine-learning-security-top-10/",
            detection_adrs: &["ADR-035"],
        },
        OwaspCoverageFamily {
            framework: "Mobile 2024",
            bucket: "OWASP-MOBILE-2024",
            items: "M1-M10",
            status: "10/10",
            anchor: "https://owasp.org/www-project-mobile-top-10/",
            detection_adrs: &["ADR-036"],
        },
        OwaspCoverageFamily {
            framework: "Web 2021",
            bucket: "OWASP-2021",
            items: "A01-A10",
            status: "10/10",
            anchor: "https://owasp.org/Top10/",
            detection_adrs: &["ADR-037"],
        },
        OwaspCoverageFamily {
            framework: "API 2023",
            bucket: "OWASP-API-2023",
            items: "API1-API10",
            status: "10/10",
            anchor: "https://owasp.org/API-Security/",
            detection_adrs: &["ADR-037"],
        },
    ]
}

pub fn render_owasp_coverage_matrix() -> String {
    let mut lines = vec![
        String::from("| Framework | Bucket | Items | Status | OWASP Anchor | Detection ADRs |"),
        String::from("|---|---|---|---|---|---|"),
    ];

    for family in owasp_coverage_family_catalog() {
        lines.push(format!(
            "| {} | {} | {} | {} | {} | {} |",
            family.framework,
            family.bucket,
            family.items,
            family.status,
            family.anchor,
            family.detection_adrs.join(", ")
        ));
    }

    lines.join("\n") + "\n"
}

pub fn maestro_layer_catalog() -> Vec<MaestroLayer> {
    vec![
        MaestroLayer {
            layer_id: "L1",
            layer_name: "Foundation Model",
            description: "Pre-trained LLMs, inference engines",
            aliases: &["Foundation Models"],
        },
        MaestroLayer {
            layer_id: "L2",
            layer_name: "Data Operations",
            description: "Vector stores, RAG pipelines, embeddings",
            aliases: &["Data Pipelines", "Data Stores"],
        },
        MaestroLayer {
            layer_id: "L3",
            layer_name: "Agent Framework",
            description: "Orchestrators, tool servers, MCP",
            aliases: &["Agent Frameworks", "Orchestration"],
        },
        MaestroLayer {
            layer_id: "L4",
            layer_name: "Deployment Infrastructure",
            description: "API gateways, containers, networking",
            aliases: &["Infrastructure", "Runtime"],
        },
        MaestroLayer {
            layer_id: "L5",
            layer_name: "Evaluation and Observability",
            description: "Audit logging, monitoring, anomaly detection, forensics",
            aliases: &["Security", "Infrastructure Controls", "Observability"],
        },
        MaestroLayer {
            layer_id: "L6",
            layer_name: "Security and Compliance",
            description: "Auth, guardrails, rate limiting, encryption, IAM",
            aliases: &["Agent Ecosystem", "Guardrails", "Security"],
        },
        MaestroLayer {
            layer_id: "L7",
            layer_name: "Agent Ecosystem",
            description: "Multi-agent coordination, delegation, chat UIs, API endpoints",
            aliases: &["User Interface", "Chat UI", "API Endpoint", "Admin Console"],
        },
    ]
}

pub fn canonical_maestro_layer_label(layer_id: &str) -> Option<&'static str> {
    match layer_id.trim().to_ascii_uppercase().as_str() {
        "L1" => Some("L1 — Foundation Model"),
        "L2" => Some("L2 — Data Operations"),
        "L3" => Some("L3 — Agent Framework"),
        "L4" => Some("L4 — Deployment Infrastructure"),
        "L5" => Some("L5 — Evaluation and Observability"),
        "L6" => Some("L6 — Security and Compliance"),
        "L7" => Some("L7 — Agent Ecosystem"),
        _ => None,
    }
}

pub fn normalize_maestro_layer_label(layer_label: &str) -> String {
    let trimmed = layer_label.trim();
    if trimmed.is_empty() {
        return String::new();
    }
    if trimmed.eq_ignore_ascii_case("unclassified") {
        return String::from("Unclassified");
    }

    if let Some((layer_id, _layer_name)) = split_maestro_layer(trimmed) {
        let normalized_id = layer_id.trim().to_ascii_uppercase();
        if let Some(canonical) = canonical_maestro_layer_label(&normalized_id) {
            return String::from(canonical);
        }
    }

    if let Some(layer_id) = resolve_maestro_layer_alias(trimmed) {
        if let Some(canonical) = canonical_maestro_layer_label(layer_id) {
            return String::from(canonical);
        }
    }

    trimmed.to_string()
}

fn split_maestro_layer(layer_raw: &str) -> Option<(&str, &str)> {
    for separator in ['—', '–', '-'] {
        if let Some((layer_id, layer_name)) = layer_raw.split_once(separator) {
            return Some((layer_id.trim(), layer_name.trim()));
        }
    }

    if layer_raw.trim().is_empty() {
        None
    } else {
        Some((layer_raw.trim(), ""))
    }
}

fn resolve_maestro_layer_alias(layer_name: &str) -> Option<&'static str> {
    maestro_layer_catalog().into_iter().find_map(|layer| {
        if layer.layer_name.eq_ignore_ascii_case(layer_name)
            || layer
                .aliases
                .iter()
                .any(|alias| alias.eq_ignore_ascii_case(layer_name))
        {
            Some(layer.layer_id)
        } else {
            None
        }
    })
}
