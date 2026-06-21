use std::path::{Path, PathBuf};

use serde_json::Value;
use tachi_shell::commands::CommandOutput;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DesktopInvokeInput {
    ControlPlane { command: String, args: Vec<String> },
    CoverageAudit { root: PathBuf },
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
            args: args.iter().map(|arg| (*arg).to_string()).collect(),
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
                    other => return Err(render_schema_error(command, &format!("unrecognized argument: {other}"))),
                }
            }

            let template = template.ok_or_else(|| render_schema_error(command, "--template is required"))?;
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
                    other => return Err(render_schema_error(command, &format!("unrecognized argument: {other}"))),
                }
            }

            Ok(DesktopInvokeInput::ReportData {
                target_dir: target_dir.ok_or_else(|| render_schema_error(command, "--target-dir is required"))?,
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
                    other => return Err(render_schema_error(command, &format!("unrecognized argument: {other}"))),
                }
            }

            Ok(DesktopInvokeInput::ThreatsSarif {
                input: input.ok_or_else(|| render_schema_error(command, "--input is required"))?,
                output: output.ok_or_else(|| render_schema_error(command, "--output is required"))?,
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
                    other => return Err(render_schema_error(command, &format!("unrecognized argument: {other}"))),
                }
            }

            Ok(DesktopInvokeInput::RiskScoresSarif {
                risk_scores: risk_scores
                    .ok_or_else(|| render_schema_error(command, "--risk-scores is required"))?,
                threats: threats.ok_or_else(|| render_schema_error(command, "--threats is required"))?,
                output: output.ok_or_else(|| render_schema_error(command, "--output is required"))?,
            })
        }
        _ => Err(render_schema_error(command, "unsupported command")),
    }
}

pub fn validate_invoke_output(command: &str, output: &CommandOutput) -> Result<(), String> {
    if output.status != 0 {
        return Ok(());
    }

    match command {
        "coverage-audit" => {
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
        "infographic-data" => {
            let payload: Value = serde_json::from_str(&output.stdout).map_err(|err| {
                render_schema_error(command, &format!("infographic JSON output failed validation: {err}"))
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
        "report-data" => {
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
        "threats-sarif" => {
            if output.stdout.is_empty() && output.stderr.contains("OK: wrote") {
                Ok(())
            } else {
                Err(render_schema_error(
                    command,
                    "threats SARIF output missing completion marker",
                ))
            }
        }
        "risk-scores-sarif" => {
            if output.stdout.is_empty() && output.stderr.contains("OK: wrote") {
                Ok(())
            } else {
                Err(render_schema_error(
                    command,
                    "risk scores SARIF output missing completion marker",
                ))
            }
        }
        _ => Ok(()),
    }
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
            other => return Err(render_schema_error(command, &format!("unrecognized argument: {other}"))),
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
