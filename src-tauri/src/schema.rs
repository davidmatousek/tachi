use std::path::{Path, PathBuf};

use crate::error::DesktopError;
use serde_json::Value;
use tachi_shell::commands::{command_output_kind, CommandOutput, CommandOutputKind};

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DesktopInvokeInput {
    ControlPlane {
        command: String,
        args: Vec<String>,
    },
    CoverageAudit {
        root: PathBuf,
    },
    InfographicData {
        root: PathBuf,
        template: String,
        output: Option<PathBuf>,
    },
    ReportData {
        target_dir: PathBuf,
        template_dir: PathBuf,
        output: Option<PathBuf>,
    },
    ThreatsSarif {
        input: PathBuf,
        output: PathBuf,
    },
    RiskScoresSarif {
        risk_scores: PathBuf,
        threats: PathBuf,
        output: PathBuf,
    },
}

pub fn validate_invoke_input(
    command: &str,
    default_root: &Path,
    args: &[&str],
) -> Result<DesktopInvokeInput, String> {
    if !crate::registered_commands().contains(&command) {
        return Err(render_schema_error(command, "unsupported command"));
    }

    let mut iter = args.iter();
    match command {
        "install" | "init" | "update" | "bootstrap" => Ok(DesktopInvokeInput::ControlPlane {
            command: command.to_string(),
            args: validate_control_plane_args(command, args)?,
        }),
        "coverage-audit" => Ok(DesktopInvokeInput::CoverageAudit {
            root: parse_optional_root(default_root, &mut iter, command)?,
        }),
        "infographic-data" => {
            let mut root = default_root.to_path_buf();
            let mut template = None;
            let mut output = None;
            while let Some(arg) = iter.next() {
                match *arg {
                    "--root" => {
                        let value = next_value(command, &mut iter, "--root")?;
                        root = PathBuf::from(value);
                    }
                    "--template" => {
                        let value = next_value(command, &mut iter, "--template")?;
                        template = Some((*value).to_string());
                    }
                    "--output" => {
                        let value = next_value(command, &mut iter, "--output")?;
                        output = Some(PathBuf::from(value));
                    }
                    "--help" | "-h" => {
                        return Err(render_schema_error(
                            command,
                            "help is not an invocation payload",
                        ));
                    }
                    other => {
                        return Err(render_schema_error(
                            command,
                            &format!("unrecognized argument: {other}"),
                        ))
                    }
                }
            }

            let template =
                template.ok_or_else(|| render_schema_error(command, "--template is required"))?;
            Ok(DesktopInvokeInput::InfographicData {
                root,
                template,
                output,
            })
        }
        "report-data" => {
            let mut target_dir = None;
            let mut template_dir = None;
            let mut output = None;
            while let Some(arg) = iter.next() {
                match *arg {
                    "--target-dir" => {
                        let value = next_value(command, &mut iter, "--target-dir")?;
                        target_dir = Some(PathBuf::from(value));
                    }
                    "--template-dir" => {
                        let value = next_value(command, &mut iter, "--template-dir")?;
                        template_dir = Some(PathBuf::from(value));
                    }
                    "--output" => {
                        let value = next_value(command, &mut iter, "--output")?;
                        output = Some(PathBuf::from(value));
                    }
                    "--help" | "-h" => {
                        return Err(render_schema_error(
                            command,
                            "help is not an invocation payload",
                        ));
                    }
                    other => {
                        return Err(render_schema_error(
                            command,
                            &format!("unrecognized argument: {other}"),
                        ))
                    }
                }
            }

            Ok(DesktopInvokeInput::ReportData {
                target_dir: target_dir
                    .ok_or_else(|| render_schema_error(command, "--target-dir is required"))?,
                template_dir: template_dir
                    .ok_or_else(|| render_schema_error(command, "--template-dir is required"))?,
                output,
            })
        }
        "threats-sarif" => {
            let mut input = None;
            let mut output = None;
            while let Some(arg) = iter.next() {
                match *arg {
                    "--input" => {
                        let value = next_value(command, &mut iter, "--input")?;
                        input = Some(PathBuf::from(value));
                    }
                    "--output" => {
                        let value = next_value(command, &mut iter, "--output")?;
                        output = Some(PathBuf::from(value));
                    }
                    "--help" | "-h" => {
                        return Err(render_schema_error(
                            command,
                            "help is not an invocation payload",
                        ));
                    }
                    other => {
                        return Err(render_schema_error(
                            command,
                            &format!("unrecognized argument: {other}"),
                        ))
                    }
                }
            }

            Ok(DesktopInvokeInput::ThreatsSarif {
                input: input.ok_or_else(|| render_schema_error(command, "--input is required"))?,
                output: output
                    .ok_or_else(|| render_schema_error(command, "--output is required"))?,
            })
        }
        "risk-scores-sarif" => {
            let mut risk_scores = None;
            let mut threats = None;
            let mut output = None;
            while let Some(arg) = iter.next() {
                match *arg {
                    "--risk-scores" => {
                        let value = next_value(command, &mut iter, "--risk-scores")?;
                        risk_scores = Some(PathBuf::from(value));
                    }
                    "--threats" => {
                        let value = next_value(command, &mut iter, "--threats")?;
                        threats = Some(PathBuf::from(value));
                    }
                    "--output" => {
                        let value = next_value(command, &mut iter, "--output")?;
                        output = Some(PathBuf::from(value));
                    }
                    "--help" | "-h" => {
                        return Err(render_schema_error(
                            command,
                            "help is not an invocation payload",
                        ));
                    }
                    other => {
                        return Err(render_schema_error(
                            command,
                            &format!("unrecognized argument: {other}"),
                        ))
                    }
                }
            }

            Ok(DesktopInvokeInput::RiskScoresSarif {
                risk_scores: risk_scores
                    .ok_or_else(|| render_schema_error(command, "--risk-scores is required"))?,
                threats: threats
                    .ok_or_else(|| render_schema_error(command, "--threats is required"))?,
                output: output
                    .ok_or_else(|| render_schema_error(command, "--output is required"))?,
            })
        }
        _ => Err(render_schema_error(command, "unsupported command")),
    }
}

pub fn validate_invoke_input_typed(
    command: &str,
    default_root: &Path,
    args: &[&str],
) -> Result<DesktopInvokeInput, DesktopError> {
    validate_invoke_input(command, default_root, args)
        .map_err(|message| DesktopError::validation(message))
}

pub fn validate_invoke_output(command: &str, output: &CommandOutput) -> Result<(), String> {
    if output.status != 0 {
        return Ok(());
    }

    match command_output_kind(command) {
        Some(CommandOutputKind::CoverageSummary) => {
            if output.stdout.contains("Coverage audit for")
                && output.stdout.contains("Active test modules")
            {
                Ok(())
            } else {
                Err(render_schema_error(
                    command,
                    "coverage audit output missing expected summary fields",
                ))
            }
        }
        Some(CommandOutputKind::Json) => {
            let payload: Value = serde_json::from_str(&output.stdout).map_err(|err| {
                render_schema_error(
                    command,
                    &format!("infographic JSON output failed validation: {err}"),
                )
            })?;
            if payload.get("template").and_then(Value::as_str).is_some()
                && payload.get("template_data").is_some()
            {
                Ok(())
            } else {
                Err(render_schema_error(
                    command,
                    "infographic JSON output missing template fields",
                ))
            }
        }
        Some(CommandOutputKind::Typst) => {
            if !output.stdout.is_empty() {
                if output.stdout.starts_with("#let project-name =") {
                    Ok(())
                } else {
                    Err(render_schema_error(
                        command,
                        "typst output missing project-name binding",
                    ))
                }
            } else if output.stderr.trim() == "report-data.typ generated" {
                Ok(())
            } else {
                Err(render_schema_error(
                    command,
                    "report-data output missing generation marker",
                ))
            }
        }
        Some(CommandOutputKind::ThreatsSarif) => {
            if output.stdout.is_empty() && output.stderr.contains("OK: wrote") {
                Ok(())
            } else {
                Err(render_schema_error(
                    command,
                    "threats SARIF output missing completion marker",
                ))
            }
        }
        Some(CommandOutputKind::RiskScoresSarif) => {
            if output.stdout.is_empty() && output.stderr.contains("OK: wrote") {
                Ok(())
            } else {
                Err(render_schema_error(
                    command,
                    "risk scores SARIF output missing completion marker",
                ))
            }
        }
        Some(CommandOutputKind::Plain) | None => Ok(()),
    }
}

pub fn validate_invoke_output_typed(
    command: &str,
    output: &CommandOutput,
) -> Result<(), DesktopError> {
    validate_invoke_output(command, output).map_err(|message| DesktopError::validation(message))
}

pub fn render_schema_error(command: &str, message: &str) -> String {
    format!("schema validation failed for {command}: {message}")
}

fn parse_optional_root<'a>(
    default_root: &Path,
    iter: &mut std::slice::Iter<'a, &'a str>,
    command: &str,
) -> Result<PathBuf, String> {
    let mut root = default_root.to_path_buf();

    while let Some(arg) = iter.next() {
        match *arg {
            "--root" => {
                let value = next_value(command, iter, "--root")?;
                root = PathBuf::from(value);
            }
            "--help" | "-h" => {
                return Err(render_schema_error(
                    command,
                    "help is not an invocation payload",
                ));
            }
            other => {
                return Err(render_schema_error(
                    command,
                    &format!("unrecognized argument: {other}"),
                ))
            }
        }
    }

    Ok(root)
}

fn next_value<'a>(
    command: &str,
    iter: &mut std::slice::Iter<'a, &'a str>,
    flag: &str,
) -> Result<&'a str, String> {
    iter.next()
        .copied()
        .ok_or_else(|| render_schema_error(command, &format!("{flag} requires a path argument")))
}

fn validate_control_plane_args(command: &str, args: &[&str]) -> Result<Vec<String>, String> {
    let mut validated = Vec::with_capacity(args.len());
    let mut seen_groups = std::collections::BTreeSet::new();
    let mut iter = args.iter().peekable();

    while let Some(arg) = iter.next() {
        let arg = *arg;
        if arg == "--help" || arg == "-h" {
            return Err(render_schema_error(
                command,
                "help is not an invocation payload",
            ));
        }
        if is_shell_control_token(arg) {
            return Err(render_schema_error(
                command,
                "shell-control args are not allowed",
            ));
        }

        let group = control_plane_flag_group(command, arg).ok_or_else(|| {
            render_schema_error(command, &format!("unrecognized argument: {arg}"))
        })?;
        if !seen_groups.insert(group) {
            return Err(render_schema_error(
                command,
                &format!("duplicate or conflicting argument: {arg}"),
            ));
        }
        validated.push(arg.to_string());

        if control_plane_flag_takes_value(command, arg) {
            let value = iter.next().copied().ok_or_else(|| {
                render_schema_error(command, &format!("{arg} requires a path argument"))
            })?;
            if is_shell_control_token(value) {
                return Err(render_schema_error(
                    command,
                    "shell-control args are not allowed",
                ));
            }
            validated.push(value.to_string());
        }
    }

    Ok(validated)
}

fn control_plane_flag_group(command: &str, flag: &str) -> Option<&'static str> {
    match command {
        "install" => match flag {
            "--source" => Some("--source"),
            "--version" => Some("--version"),
            _ => None,
        },
        "init" => match flag {
            "--precommit" | "--no-precommit" => Some("precommit-mode"),
            _ => None,
        },
        "update" | "bootstrap" => match flag {
            "--dry-run" | "--apply" => Some("execution-mode"),
            "--yes" => Some("--yes"),
            "--json" => Some("--json"),
            "--force-retag" => Some("--force-retag"),
            "--upstream-url" => Some("--upstream-url"),
            _ => None,
        },
        _ => None,
    }
}

fn control_plane_flag_takes_value(command: &str, flag: &str) -> bool {
    match command {
        "install" => matches!(flag, "--source" | "--version"),
        "update" | "bootstrap" => matches!(flag, "--upstream-url"),
        _ => false,
    }
}

fn is_shell_control_token(value: &str) -> bool {
    value
        .chars()
        .any(|ch| matches!(ch, ';' | '|' | '&' | '<' | '>' | '$' | '`'))
}
