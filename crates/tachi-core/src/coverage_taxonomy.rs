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
}

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
            description: "Base LLM, fine-tuned models, model weights",
        },
        MaestroLayer {
            layer_id: "L2",
            layer_name: "Data Operations",
            description: "Data pipelines feeding AI systems",
        },
        MaestroLayer {
            layer_id: "L3",
            layer_name: "Agent Framework",
            description: "Orchestration and tool dispatch",
        },
        MaestroLayer {
            layer_id: "L4",
            layer_name: "Deployment Infrastructure",
            description: "Runtime and networking",
        },
        MaestroLayer {
            layer_id: "L5",
            layer_name: "Security",
            description: "Security services and controls",
        },
        MaestroLayer {
            layer_id: "L6",
            layer_name: "Agent Ecosystem",
            description: "Multi-agent coordination",
        },
        MaestroLayer {
            layer_id: "L7",
            layer_name: "User Interface",
            description: "User-facing surfaces",
        },
    ]
}
