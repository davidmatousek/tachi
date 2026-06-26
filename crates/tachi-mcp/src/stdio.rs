use std::io::{BufRead, Write};

use serde::{Deserialize, Serialize};
use serde_json::Value;

use crate::server::McpServer;
use crate::tools::McpInvocationResult;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum StartupMode {
    Stdio,
}

pub fn startup_mode_from_args(args: &[String]) -> Result<StartupMode, String> {
    if args.iter().any(|arg| arg == "--stdio") {
        return Ok(StartupMode::Stdio);
    }

    Err(String::from("missing required --stdio flag"))
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct StdioWireRequest {
    pub id: String,
    pub tool: String,
    pub input: Value,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct StdioWireResponse {
    pub id: String,
    pub ok: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub result: Option<McpInvocationResult>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
}

pub fn serve<R, W>(reader: R, mut writer: W, server: &McpServer) -> Result<(), String>
where
    R: BufRead,
    W: Write,
{
    for line in reader.lines() {
        let line = line.map_err(|err| format!("failed to read stdio request: {err}"))?;
        if line.trim().is_empty() {
            continue;
        }

        let request: StdioWireRequest = serde_json::from_str(&line)
            .map_err(|err| format!("failed to decode stdio request: {err}"))?;
        let response = match server.invoke_json(&request.tool, &request.input) {
            Ok(result) => StdioWireResponse {
                id: request.id,
                ok: true,
                result: Some(result),
                error: None,
            },
            Err(error) => StdioWireResponse {
                id: request.id,
                ok: false,
                result: None,
                error: Some(error),
            },
        };

        let json = serde_json::to_string(&response)
            .map_err(|err| format!("failed to encode stdio response: {err}"))?;
        writer
            .write_all(json.as_bytes())
            .and_then(|_| writer.write_all(b"\n"))
            .map_err(|err| format!("failed to write stdio response: {err}"))?;
        writer
            .flush()
            .map_err(|err| format!("failed to flush stdio response: {err}"))?;
    }

    Ok(())
}

pub fn run(args: &[String]) -> Result<(), String> {
    if !args.iter().any(|arg| arg == "--stdio") {
        return Err(String::from("missing required --stdio flag"));
    }

    let server = McpServer::default();
    let stdin = std::io::stdin();
    let stdout = std::io::stdout();
    serve(stdin.lock(), stdout.lock(), &server)
}
