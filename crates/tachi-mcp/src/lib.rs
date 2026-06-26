pub mod server;
pub mod stdio;

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
pub struct McpCommandContract {
    pub name: String,
    pub dispatch_kind: String,
    pub output_kind: String,
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

pub fn render_contract_snapshot_json() -> String {
    serde_json::to_string_pretty(&build_contract_snapshot())
        .expect("canonical MCP snapshot should serialize")
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
