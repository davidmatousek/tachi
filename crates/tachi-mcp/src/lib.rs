pub mod server;
pub mod stdio;
pub mod tools;

use serde::Serialize;
use sha2::{Digest, Sha256};
use tachi_shell::commands::{command_registry, CommandDispatchKind, CommandOutputKind};

pub const CONTRACT_VERSION: u32 = 1;

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct McpContractSnapshot {
    pub version: u32,
    pub command_hash: String,
    pub commands: Vec<McpCommandContract>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct McpToolSchemaSnapshot {
    pub version: u32,
    pub schemas: Vec<McpToolSchema>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct McpCommandContract {
    pub name: String,
    pub dispatch_kind: String,
    pub output_kind: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct McpToolSchema {
    pub name: String,
    pub command_name: String,
    pub input_fields: Vec<McpInputField>,
    pub output_modes: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct McpInputField {
    pub name: String,
    pub field_type: String,
    pub required: bool,
}

pub fn build_contract_snapshot() -> McpContractSnapshot {
    let registry = command_registry();
    registry
        .validate_unique()
        .expect("canonical MCP command registry should be unique");

    let commands = registry
        .specs()
        .iter()
        .map(|spec| McpCommandContract {
            name: spec.name.to_string(),
            dispatch_kind: dispatch_kind_label(spec.dispatch_kind).to_string(),
            output_kind: output_kind_label(spec.output_kind).to_string(),
        })
        .collect::<Vec<_>>();

    let command_hash = contract_hash(&commands);

    McpContractSnapshot {
        version: CONTRACT_VERSION,
        command_hash,
        commands,
    }
}

pub const TOOL_SCHEMA_VERSION: u32 = 1;

pub fn build_tool_schema_snapshot() -> McpToolSchemaSnapshot {
    let schemas = crate::tools::McpToolId::ALL
        .into_iter()
        .map(|tool_id| match tool_id.command_name() {
            "coverage-audit" => McpToolSchema {
                name: tool_id.tool_name().to_string(),
                command_name: tool_id.command_name().to_string(),
                input_fields: vec![
                    McpInputField {
                        name: "repo_root".to_string(),
                        field_type: "path".to_string(),
                        required: true,
                    },
                    McpInputField {
                        name: "output_mode".to_string(),
                        field_type: "enum".to_string(),
                        required: false,
                    },
                ],
                output_modes: output_modes_for(),
            },
            "infographic-data" => McpToolSchema {
                name: tool_id.tool_name().to_string(),
                command_name: tool_id.command_name().to_string(),
                input_fields: vec![
                    McpInputField {
                        name: "repo_root".to_string(),
                        field_type: "path".to_string(),
                        required: true,
                    },
                    McpInputField {
                        name: "template".to_string(),
                        field_type: "string".to_string(),
                        required: true,
                    },
                    McpInputField {
                        name: "output_mode".to_string(),
                        field_type: "enum".to_string(),
                        required: false,
                    },
                ],
                output_modes: output_modes_for(),
            },
            "report-data" => McpToolSchema {
                name: tool_id.tool_name().to_string(),
                command_name: tool_id.command_name().to_string(),
                input_fields: vec![
                    McpInputField {
                        name: "target_dir".to_string(),
                        field_type: "path".to_string(),
                        required: true,
                    },
                    McpInputField {
                        name: "template_dir".to_string(),
                        field_type: "path".to_string(),
                        required: true,
                    },
                    McpInputField {
                        name: "output_mode".to_string(),
                        field_type: "enum".to_string(),
                        required: false,
                    },
                ],
                output_modes: output_modes_for(),
            },
            "risk-scores-sarif" => McpToolSchema {
                name: tool_id.tool_name().to_string(),
                command_name: tool_id.command_name().to_string(),
                input_fields: vec![
                    McpInputField {
                        name: "risk_scores".to_string(),
                        field_type: "path".to_string(),
                        required: true,
                    },
                    McpInputField {
                        name: "threats".to_string(),
                        field_type: "path".to_string(),
                        required: true,
                    },
                    McpInputField {
                        name: "output_mode".to_string(),
                        field_type: "enum".to_string(),
                        required: false,
                    },
                ],
                output_modes: output_modes_for(),
            },
            "threats-sarif" => McpToolSchema {
                name: tool_id.tool_name().to_string(),
                command_name: tool_id.command_name().to_string(),
                input_fields: vec![
                    McpInputField {
                        name: "input".to_string(),
                        field_type: "path".to_string(),
                        required: true,
                    },
                    McpInputField {
                        name: "output_mode".to_string(),
                        field_type: "enum".to_string(),
                        required: false,
                    },
                ],
                output_modes: output_modes_for(),
            },
            other => panic!("unsupported MCP command for schema snapshot: {other}"),
        })
        .collect::<Vec<_>>();

    McpToolSchemaSnapshot {
        version: TOOL_SCHEMA_VERSION,
        schemas,
    }
}

pub fn render_contract_snapshot_json() -> String {
    serde_json::to_string_pretty(&build_contract_snapshot())
        .expect("canonical MCP snapshot should serialize")
}

pub fn render_tool_schema_snapshot_json() -> String {
    serde_json::to_string_pretty(&build_tool_schema_snapshot())
        .expect("canonical MCP schema snapshot should serialize")
}

pub fn contract_hash(commands: &[McpCommandContract]) -> String {
    let canonical = serde_json::to_vec(commands).expect("canonical MCP commands should serialize");
    let digest = Sha256::digest(&canonical);
    format!("{digest:x}")
}

fn dispatch_kind_label(kind: CommandDispatchKind) -> &'static str {
    match kind {
        CommandDispatchKind::ControlPlane => "control-plane",
        CommandDispatchKind::CoverageAudit => "coverage-audit",
        CommandDispatchKind::InfographicData => "infographic-data",
        CommandDispatchKind::ReportData => "report-data",
        CommandDispatchKind::ThreatsSarif => "threats-sarif",
        CommandDispatchKind::RiskScoresSarif => "risk-scores-sarif",
    }
}

fn output_kind_label(kind: CommandOutputKind) -> &'static str {
    match kind {
        CommandOutputKind::Plain => "plain",
        CommandOutputKind::CoverageSummary => "coverage-summary",
        CommandOutputKind::Json => "json",
        CommandOutputKind::Typst => "typst",
        CommandOutputKind::ThreatsSarif => "threats-sarif",
        CommandOutputKind::RiskScoresSarif => "risk-scores-sarif",
    }
}

fn output_modes_for() -> Vec<String> {
    vec!["in-band".to_string(), "artifact".to_string()]
}
