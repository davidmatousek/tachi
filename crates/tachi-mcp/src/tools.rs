use std::path::PathBuf;

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Default)]
#[serde(rename_all = "kebab-case")]
pub enum McpOutputMode {
    #[default]
    InBand,
    Artifact,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum McpToolId {
    CoverageAudit,
    InfographicData,
    ReportData,
    RiskScoresSarif,
    ThreatsSarif,
}

impl McpToolId {
    pub const ALL: [Self; 5] = [
        Self::CoverageAudit,
        Self::InfographicData,
        Self::ReportData,
        Self::RiskScoresSarif,
        Self::ThreatsSarif,
    ];

    pub const fn tool_name(self) -> &'static str {
        match self {
            Self::CoverageAudit => "tachi.coverage-audit",
            Self::InfographicData => "tachi.infographic-data",
            Self::ReportData => "tachi.report-data",
            Self::RiskScoresSarif => "tachi.risk-scores-sarif",
            Self::ThreatsSarif => "tachi.threats-sarif",
        }
    }

    pub const fn command_name(self) -> &'static str {
        match self {
            Self::CoverageAudit => "coverage-audit",
            Self::InfographicData => "infographic-data",
            Self::ReportData => "report-data",
            Self::RiskScoresSarif => "risk-scores-sarif",
            Self::ThreatsSarif => "threats-sarif",
        }
    }

    pub const fn output_kind(self) -> &'static str {
        match self {
            Self::CoverageAudit => "coverage-summary",
            Self::InfographicData => "json",
            Self::ReportData => "typst",
            Self::RiskScoresSarif => "sarif",
            Self::ThreatsSarif => "sarif",
        }
    }

    pub fn from_tool_name(tool_name: &str) -> Option<Self> {
        Self::ALL
            .into_iter()
            .find(|tool| tool.tool_name() == tool_name)
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct McpToolSpec {
    pub tool_name: &'static str,
    pub command_name: &'static str,
    pub output_kind: &'static str,
}

pub const MCP_TOOL_SPECS: [McpToolSpec; 5] = [
    McpToolSpec {
        tool_name: "tachi.coverage-audit",
        command_name: "coverage-audit",
        output_kind: "coverage-summary",
    },
    McpToolSpec {
        tool_name: "tachi.infographic-data",
        command_name: "infographic-data",
        output_kind: "json",
    },
    McpToolSpec {
        tool_name: "tachi.report-data",
        command_name: "report-data",
        output_kind: "typst",
    },
    McpToolSpec {
        tool_name: "tachi.risk-scores-sarif",
        command_name: "risk-scores-sarif",
        output_kind: "sarif",
    },
    McpToolSpec {
        tool_name: "tachi.threats-sarif",
        command_name: "threats-sarif",
        output_kind: "sarif",
    },
];

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct McpToolRegistry {
    specs: &'static [McpToolSpec],
}

impl McpToolRegistry {
    pub const fn new(specs: &'static [McpToolSpec]) -> Self {
        Self { specs }
    }

    pub const fn specs(&self) -> &'static [McpToolSpec] {
        self.specs
    }

    pub fn tool_names(&self) -> Vec<&'static str> {
        self.specs.iter().map(|spec| spec.tool_name).collect()
    }

    pub fn spec(&self, tool_name: &str) -> Option<&'static McpToolSpec> {
        self.specs.iter().find(|spec| spec.tool_name == tool_name)
    }
}

pub const fn tool_registry() -> McpToolRegistry {
    McpToolRegistry::new(&MCP_TOOL_SPECS)
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct CoverageAuditInput {
    pub repo_root: PathBuf,
    #[serde(default)]
    pub output_mode: McpOutputMode,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct InfographicDataInput {
    pub repo_root: PathBuf,
    pub template: String,
    #[serde(default)]
    pub output_mode: McpOutputMode,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ReportDataInput {
    pub target_dir: PathBuf,
    pub template_dir: PathBuf,
    #[serde(default)]
    pub output_mode: McpOutputMode,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct RiskScoresSarifInput {
    pub risk_scores: PathBuf,
    pub threats: PathBuf,
    #[serde(default)]
    pub output_mode: McpOutputMode,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ThreatsSarifInput {
    pub input: PathBuf,
    #[serde(default)]
    pub output_mode: McpOutputMode,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct McpInvocationResult {
    pub tool_name: String,
    pub command_name: String,
    pub output_kind: String,
    pub output_mode: McpOutputMode,
    pub artifact_path: Option<PathBuf>,
    pub artifact_bytes: Option<usize>,
    pub payload: String,
}
