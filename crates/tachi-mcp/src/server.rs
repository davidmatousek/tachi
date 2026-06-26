use std::fs;
use std::path::{Path, PathBuf};

use serde_json::Value;

use crate::tools::{
    tool_registry, CoverageAuditInput, InfographicDataInput, McpInvocationResult, McpOutputMode,
    McpRequestContext, McpToolId, McpToolRegistry, McpToolSpec, ReportDataInput,
    RiskScoresSarifInput, ThreatsSarifInput,
};
use crate::{build_contract_snapshot, McpContractSnapshot};
use tachi_shell::commands::{
    coverage_audit_output, infographic_data_output, report_data_output, risk_scores_sarif_output,
    threats_sarif_output,
};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct McpServer {
    registry: McpToolRegistry,
}

impl Default for McpServer {
    fn default() -> Self {
        Self {
            registry: tool_registry(),
        }
    }
}

impl McpServer {
    pub const fn new(registry: McpToolRegistry) -> Self {
        Self { registry }
    }

    pub fn registered_tools(&self) -> &'static [McpToolSpec] {
        self.registry.specs()
    }

    pub fn registered_tool_names(&self) -> Vec<&'static str> {
        self.registry.tool_names()
    }

    pub fn supported_contract_snapshot(&self) -> McpContractSnapshot {
        build_contract_snapshot()
    }

    pub fn invoke_json(
        &self,
        context: &McpRequestContext,
        tool_name: &str,
        payload: &Value,
    ) -> Result<McpInvocationResult, String> {
        if context.cancelled {
            return Err(format!(
                "request {} cancelled before dispatch",
                context.request_id
            ));
        }
        let tool_id = McpToolId::from_tool_name(tool_name)
            .ok_or_else(|| format!("authorization error: unknown tool {tool_name}"))?;
        self.invoke_tool(context, tool_id, payload)
    }

    pub fn invoke_tool(
        &self,
        context: &McpRequestContext,
        tool_id: McpToolId,
        payload: &Value,
    ) -> Result<McpInvocationResult, String> {
        if context.cancelled {
            return Err(format!(
                "request {} cancelled before dispatch",
                context.request_id
            ));
        }
        match tool_id {
            McpToolId::CoverageAudit => {
                let input: CoverageAuditInput = deserialize(payload, tool_id.tool_name())?;
                let content = coverage_audit_output(&input.repo_root);
                self.write_or_return(
                    context,
                    tool_id,
                    &content,
                    output_path_for_coverage_audit(&input.repo_root),
                    input.output_mode,
                )
            }
            McpToolId::InfographicData => {
                let input: InfographicDataInput = deserialize(payload, tool_id.tool_name())?;
                let content = infographic_data_output(&input.repo_root, &input.template)?;
                self.write_or_return(
                    context,
                    tool_id,
                    &content,
                    output_path_for_infographic_data(&input.repo_root),
                    input.output_mode,
                )
            }
            McpToolId::ReportData => {
                let input: ReportDataInput = deserialize(payload, tool_id.tool_name())?;
                let content = report_data_output(&input.target_dir, &input.template_dir);
                self.write_or_return(
                    context,
                    tool_id,
                    &content,
                    output_path_for_report_data(&input.target_dir),
                    input.output_mode,
                )
            }
            McpToolId::RiskScoresSarif => {
                let input: RiskScoresSarifInput = deserialize(payload, tool_id.tool_name())?;
                let content = risk_scores_sarif_output(&input.risk_scores, &input.threats)?.sarif;
                self.write_or_return(
                    context,
                    tool_id,
                    &content,
                    output_path_for_risk_scores_sarif(&input.risk_scores),
                    input.output_mode,
                )
            }
            McpToolId::ThreatsSarif => {
                let input: ThreatsSarifInput = deserialize(payload, tool_id.tool_name())?;
                let content = threats_sarif_output(&input.input)?.sarif;
                self.write_or_return(
                    context,
                    tool_id,
                    &content,
                    output_path_for_threats_sarif(&input.input),
                    input.output_mode,
                )
            }
        }
    }

    fn write_or_return(
        &self,
        context: &McpRequestContext,
        tool_id: McpToolId,
        payload: &str,
        artifact_path: PathBuf,
        output_mode: McpOutputMode,
    ) -> Result<McpInvocationResult, String> {
        let artifact_path = match output_mode {
            McpOutputMode::Artifact => {
                if let Some(parent) = artifact_path.parent() {
                    fs::create_dir_all(parent)
                        .map_err(|err| format!("failed to create {}: {err}", parent.display()))?;
                }
                fs::write(&artifact_path, payload)
                    .map_err(|err| format!("failed to write {}: {err}", artifact_path.display()))?;
                Some(artifact_path)
            }
            McpOutputMode::InBand => None,
        };
        let artifact_bytes = artifact_path
            .as_ref()
            .and_then(|path| fs::metadata(path).ok().map(|meta| meta.len() as usize));

        Ok(McpInvocationResult {
            request_id: context.request_id.clone(),
            tool_name: tool_id.tool_name().to_string(),
            command_name: tool_id.command_name().to_string(),
            output_kind: tool_id.output_kind().to_string(),
            output_mode,
            artifact_path,
            artifact_bytes,
            cancelled: context.cancelled,
            payload: payload.to_string(),
        })
    }
}

pub fn supported_contract_snapshot() -> McpContractSnapshot {
    build_contract_snapshot()
}

fn deserialize<T>(payload: &Value, tool_name: &str) -> Result<T, String>
where
    T: serde::de::DeserializeOwned,
{
    serde_json::from_value(payload.clone())
        .map_err(|err| format!("invalid payload for {tool_name}: {err}"))
}

fn output_path_for_coverage_audit(repo_root: &Path) -> PathBuf {
    repo_root
        .join("target")
        .join("mcp")
        .join("coverage-audit.txt")
}

fn output_path_for_infographic_data(repo_root: &Path) -> PathBuf {
    repo_root
        .join("target")
        .join("mcp")
        .join("infographic-data.json")
}

fn output_path_for_report_data(target_dir: &Path) -> PathBuf {
    target_dir.join("mcp").join("report-data.typ")
}

fn output_path_for_risk_scores_sarif(risk_scores: &Path) -> PathBuf {
    risk_scores
        .parent()
        .unwrap_or_else(|| Path::new("."))
        .join("mcp")
        .join("risk-scores-sarif.sarif")
}

fn output_path_for_threats_sarif(input: &Path) -> PathBuf {
    input
        .parent()
        .unwrap_or_else(|| Path::new("."))
        .join("mcp")
        .join("threats-sarif.sarif")
}
