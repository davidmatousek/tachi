use std::path::Path;
use std::path::PathBuf;

use crate::commands::{
    bootstrap_control_plane_args, command_dispatch_kind, infographic_data_output,
    render_report_data_result, report_data_result, validate_report_data_result,
    CommandDispatchKind,
};
use crate::commands::{
    coverage_audit_output, risk_scores_sarif_output, run_script_command_with_progress,
    threats_sarif_output, CommandOutput,
};
use crate::progress::{
    emit_progress_event, invoke_with_progress, CancellationToken, NoopProgressReporter,
    ProgressReporter,
};

pub fn dispatch_command(command: &str, root: &Path, args: &[&str]) -> CommandOutput {
    let token = CancellationToken::new();
    let mut reporter = NoopProgressReporter;
    dispatch_command_with_progress(command, root, args, &token, &mut reporter)
}

pub fn dispatch_command_with_progress(
    command: &str,
    root: &Path,
    args: &[&str],
    token: &CancellationToken,
    reporter: &mut dyn ProgressReporter,
) -> CommandOutput {
    invoke_with_progress(
        command,
        token,
        reporter,
        |token, reporter| match command_dispatch_kind(command) {
            Some(CommandDispatchKind::ControlPlane) => match command {
                "install" => {
                    let scripts_dir = super::commands::control_plane_scripts_dir(root);
                    run_script_command_with_progress(
                        &scripts_dir,
                        "install.sh",
                        args,
                        root,
                        token,
                        reporter,
                    )
                }
                "init" => {
                    let scripts_dir = super::commands::control_plane_scripts_dir(root);
                    run_script_command_with_progress(
                        &scripts_dir,
                        "init.sh",
                        args,
                        root,
                        token,
                        reporter,
                    )
                }
                "update" => {
                    let scripts_dir = super::commands::control_plane_scripts_dir(root);
                    run_script_command_with_progress(
                        &scripts_dir,
                        "update.sh",
                        args,
                        root,
                        token,
                        reporter,
                    )
                }
                "bootstrap" => {
                    let bootstrap_args = bootstrap_control_plane_args(args);
                    let bootstrap_args = bootstrap_args
                        .iter()
                        .map(String::as_str)
                        .collect::<Vec<_>>();
                    let scripts_dir = super::commands::control_plane_scripts_dir(root);
                    run_script_command_with_progress(
                        &scripts_dir,
                        "update.sh",
                        bootstrap_args.as_slice(),
                        root,
                        token,
                        reporter,
                    )
                }
                other => CommandOutput {
                    status: 2,
                    stdout: String::new(),
                    stderr: format!("unsupported command: {other}\n"),
                },
            },
            Some(CommandDispatchKind::CoverageAudit) => dispatch_coverage_audit(root, args),
            Some(CommandDispatchKind::InfographicData) => {
                dispatch_infographic_data(root, args, token, reporter)
            }
            Some(CommandDispatchKind::ReportData) => dispatch_report_data(root, args),
            Some(CommandDispatchKind::RiskScoresSarif) => dispatch_risk_scores_sarif(root, args),
            Some(CommandDispatchKind::ThreatsSarif) => dispatch_threats_sarif(root, args),
            None => CommandOutput {
                status: 2,
                stdout: String::new(),
                stderr: format!("unsupported command: {command}\n"),
            },
        },
    )
}

fn dispatch_infographic_data(
    base_root: &Path,
    args: &[&str],
    token: &CancellationToken,
    reporter: &mut dyn ProgressReporter,
) -> CommandOutput {
    emit_progress_event(reporter, "infographic-data", "starting");
    if token.is_cancelled() {
        emit_progress_event(reporter, "infographic-data", "cancelled");
        return CommandOutput {
            status: 130,
            stdout: String::new(),
            stderr: String::from("infographic-data cancelled\n"),
        };
    }

    let (root, template, output_path) = match parse_infographic_data_args(base_root, args) {
        Ok(values) => values,
        Err(message) => {
            emit_progress_event(reporter, "infographic-data", "failed");
            return CommandOutput {
                status: 2,
                stdout: String::new(),
                stderr: format!("{message}\n"),
            };
        }
    };
    let validated_root = match ensure_contained_input_path(base_root, &root, "infographic root") {
        Ok(path) => path,
        Err(message) => {
            emit_progress_event(reporter, "infographic-data", "failed");
            return CommandOutput {
                status: 2,
                stdout: String::new(),
                stderr: format!("{message}\n"),
            };
        }
    };

    emit_progress_event(reporter, "infographic-data", "building");
    if token.is_cancelled() {
        emit_progress_event(reporter, "infographic-data", "cancelled");
        return CommandOutput {
            status: 130,
            stdout: String::new(),
            stderr: String::from("infographic-data cancelled\n"),
        };
    }

    match infographic_data_output(&validated_root, &template) {
        Ok(payload) => {
            if let Some(output_path) = output_path {
                let output_path = match ensure_contained_output_path(
                    &validated_root,
                    &output_path,
                    "infographic output",
                ) {
                    Ok(path) => path,
                    Err(message) => {
                        emit_progress_event(reporter, "infographic-data", "failed");
                        return CommandOutput {
                            status: 2,
                            stdout: String::new(),
                            stderr: format!("{message}\n"),
                        };
                    }
                };
                if token.is_cancelled() {
                    emit_progress_event(reporter, "infographic-data", "cancelled");
                    return CommandOutput {
                        status: 130,
                        stdout: String::new(),
                        stderr: String::from("infographic-data cancelled\n"),
                    };
                }
                if let Some(parent) = output_path.parent() {
                    if let Err(err) = std::fs::create_dir_all(parent) {
                        emit_progress_event(reporter, "infographic-data", "failed");
                        return CommandOutput {
                            status: 1,
                            stdout: String::new(),
                            stderr: format!("failed to create output directory: {err}\n"),
                        };
                    }
                }
                if let Err(err) = std::fs::write(&output_path, payload.as_bytes()) {
                    emit_progress_event(reporter, "infographic-data", "failed");
                    return CommandOutput {
                        status: 1,
                        stdout: String::new(),
                        stderr: format!("failed to write output file: {err}\n"),
                    };
                }
                emit_progress_event(reporter, "infographic-data", "completed");
                CommandOutput {
                    status: 0,
                    stdout: String::new(),
                    stderr: String::new(),
                }
            } else {
                emit_progress_event(reporter, "infographic-data", "completed");
                CommandOutput {
                    status: 0,
                    stdout: payload,
                    stderr: String::new(),
                }
            }
        }
        Err(message) => {
            emit_progress_event(reporter, "infographic-data", "failed");
            CommandOutput {
                status: 1,
                stdout: String::new(),
                stderr: format!("{message}\n"),
            }
        }
    }
}

fn dispatch_coverage_audit(root: &Path, args: &[&str]) -> CommandOutput {
    let root = match parse_optional_root_arg(root, args) {
        Ok(root) => root,
        Err(message) => {
            return CommandOutput {
                status: 2,
                stdout: String::new(),
                stderr: format!("{message}\n"),
            };
        }
    };

    CommandOutput {
        status: 0,
        stdout: coverage_audit_output(&root),
        stderr: String::new(),
    }
}

fn dispatch_report_data(_root: &Path, args: &[&str]) -> CommandOutput {
    let (target_dir, template_dir, output_path) = match parse_report_data_args(args) {
        Ok(values) => values,
        Err(message) => {
            return CommandOutput {
                status: 2,
                stdout: String::new(),
                stderr: format!("{message}\n"),
            };
        }
    };
    let root = _root;
    let target_dir = match ensure_contained_input_path(root, &target_dir, "report target directory")
    {
        Ok(path) => path,
        Err(message) => {
            return CommandOutput {
                status: 2,
                stdout: String::new(),
                stderr: format!("{message}\n"),
            };
        }
    };
    let template_dir =
        match ensure_contained_input_path(root, &template_dir, "report template directory") {
            Ok(path) => path,
            Err(message) => {
                return CommandOutput {
                    status: 2,
                    stdout: String::new(),
                    stderr: format!("{message}\n"),
                };
            }
        };

    let result = report_data_result(&target_dir, &template_dir);
    if let Err(message) = validate_report_data_result(&result) {
        return CommandOutput {
            status: 1,
            stdout: String::new(),
            stderr: format!("{message}\n"),
        };
    }
    let output = render_report_data_result(&result);
    if let Some(output_path) = output_path {
        let output_path =
            match ensure_contained_output_path(root, &output_path, "report-data output") {
                Ok(path) => path,
                Err(message) => {
                    return CommandOutput {
                        status: 2,
                        stdout: String::new(),
                        stderr: format!("{message}\n"),
                    };
                }
            };
        if let Some(parent) = output_path.parent() {
            if let Err(err) = std::fs::create_dir_all(parent) {
                return CommandOutput {
                    status: 1,
                    stdout: String::new(),
                    stderr: format!("failed to create output directory: {err}\n"),
                };
            }
        }
        if let Err(err) = std::fs::write(&output_path, output.as_bytes()) {
            return CommandOutput {
                status: 1,
                stdout: String::new(),
                stderr: format!("failed to write output file: {err}\n"),
            };
        }
        CommandOutput {
            status: 0,
            stdout: String::new(),
            stderr: String::from("report-data.typ generated\n"),
        }
    } else {
        CommandOutput {
            status: 0,
            stdout: output,
            stderr: String::from("report-data.typ generated\n"),
        }
    }
}

fn dispatch_threats_sarif(_root: &Path, args: &[&str]) -> CommandOutput {
    let (input, output) = match parse_threats_sarif_args(args) {
        Ok(values) => values,
        Err(message) => {
            return CommandOutput {
                status: 2,
                stdout: String::new(),
                stderr: format!("{message}\n"),
            };
        }
    };
    let root = _root;
    let input = match ensure_contained_input_path(root, &input, "threats input") {
        Ok(path) => path,
        Err(message) => {
            return CommandOutput {
                status: 2,
                stdout: String::new(),
                stderr: format!("{message}\n"),
            };
        }
    };
    let output = match ensure_contained_output_path(root, &output, "threats SARIF output") {
        Ok(path) => path,
        Err(message) => {
            return CommandOutput {
                status: 2,
                stdout: String::new(),
                stderr: format!("{message}\n"),
            };
        }
    };

    let payload = match threats_sarif_output(&input) {
        Ok(payload) => payload,
        Err(message) => {
            return CommandOutput {
                status: 1,
                stdout: String::new(),
                stderr: format!("{message}\n"),
            };
        }
    };

    if let Some(parent) = output.parent() {
        if let Err(err) = std::fs::create_dir_all(parent) {
            return CommandOutput {
                status: 1,
                stdout: String::new(),
                stderr: format!("failed to create output directory: {err}\n"),
            };
        }
    }
    if let Err(err) = std::fs::write(&output, payload.sarif.as_bytes()) {
        return CommandOutput {
            status: 1,
            stdout: String::new(),
            stderr: format!("failed to write output file: {err}\n"),
        };
    }

    CommandOutput {
        status: 0,
        stdout: String::new(),
        stderr: format!(
            "OK: wrote {} findings to {}\nAG-8 present: {} ({})\n",
            payload.findings_count,
            output.display(),
            payload.ag8_status.is_some(),
            payload.ag8_status.unwrap_or_else(|| String::from("absent"))
        ),
    }
}

fn dispatch_risk_scores_sarif(_root: &Path, args: &[&str]) -> CommandOutput {
    let (risk_scores, threats, output) = match parse_risk_scores_args(args) {
        Ok(values) => values,
        Err(message) => {
            return CommandOutput {
                status: 2,
                stdout: String::new(),
                stderr: format!("{message}\n"),
            };
        }
    };
    let root = _root;
    let risk_scores = match ensure_contained_input_path(root, &risk_scores, "risk scores input") {
        Ok(path) => path,
        Err(message) => {
            return CommandOutput {
                status: 2,
                stdout: String::new(),
                stderr: format!("{message}\n"),
            };
        }
    };
    let threats = match ensure_contained_input_path(root, &threats, "threats input") {
        Ok(path) => path,
        Err(message) => {
            return CommandOutput {
                status: 2,
                stdout: String::new(),
                stderr: format!("{message}\n"),
            };
        }
    };
    let output = match ensure_contained_output_path(root, &output, "risk scores SARIF output") {
        Ok(path) => path,
        Err(message) => {
            return CommandOutput {
                status: 2,
                stdout: String::new(),
                stderr: format!("{message}\n"),
            };
        }
    };

    let payload = match risk_scores_sarif_output(&risk_scores, &threats) {
        Ok(payload) => payload,
        Err(message) => {
            return CommandOutput {
                status: 1,
                stdout: String::new(),
                stderr: format!("{message}\n"),
            };
        }
    };

    if let Some(parent) = output.parent() {
        if let Err(err) = std::fs::create_dir_all(parent) {
            return CommandOutput {
                status: 1,
                stdout: String::new(),
                stderr: format!("failed to create output directory: {err}\n"),
            };
        }
    }
    if let Err(err) = std::fs::write(&output, payload.sarif.as_bytes()) {
        return CommandOutput {
            status: 1,
            stdout: String::new(),
            stderr: format!("failed to write output file: {err}\n"),
        };
    }

    CommandOutput {
        status: 0,
        stdout: String::new(),
        stderr: format!(
            "OK: wrote {} results to {}\n",
            payload.results_count,
            output.display()
        ),
    }
}

fn parse_optional_root_arg(default_root: &Path, args: &[&str]) -> Result<PathBuf, String> {
    let mut root = default_root.to_path_buf();
    let mut iter = args.iter();

    while let Some(arg) = iter.next() {
        match *arg {
            "--root" => {
                let value = iter
                    .next()
                    .ok_or_else(|| String::from("--root requires a path argument"))?;
                root = PathBuf::from(value);
            }
            "--help" | "-h" => return Err(String::from("usage: coverage-audit [--root PATH]")),
            other => return Err(format!("unrecognized argument: {other}")),
        }
    }

    Ok(root)
}

fn parse_report_data_args(args: &[&str]) -> Result<(PathBuf, PathBuf, Option<PathBuf>), String> {
    let mut target_dir = None;
    let mut template_dir = None;
    let mut output_path = None;
    let mut iter = args.iter();

    while let Some(arg) = iter.next() {
        match *arg {
            "--target-dir" => {
                let value = iter
                    .next()
                    .ok_or_else(|| String::from("--target-dir requires a path argument"))?;
                target_dir = Some(PathBuf::from(value));
            }
            "--template-dir" => {
                let value = iter
                    .next()
                    .ok_or_else(|| String::from("--template-dir requires a path argument"))?;
                template_dir = Some(PathBuf::from(value));
            }
            "--output" => {
                let value = iter
                    .next()
                    .ok_or_else(|| String::from("--output requires a path argument"))?;
                output_path = Some(PathBuf::from(value));
            }
            "--help" | "-h" => {
                return Err(String::from(
                    "usage: report-data --target-dir PATH --template-dir PATH [--output PATH]",
                ));
            }
            other => return Err(format!("unrecognized argument: {other}")),
        }
    }

    let target_dir = target_dir.ok_or_else(|| String::from("--target-dir is required"))?;
    let template_dir = template_dir.ok_or_else(|| String::from("--template-dir is required"))?;
    Ok((target_dir, template_dir, output_path))
}

fn parse_threats_sarif_args(args: &[&str]) -> Result<(PathBuf, PathBuf), String> {
    let mut input = None;
    let mut output = None;
    let mut iter = args.iter();

    while let Some(arg) = iter.next() {
        match *arg {
            "--input" => {
                let value = iter
                    .next()
                    .ok_or_else(|| String::from("--input requires a path argument"))?;
                input = Some(PathBuf::from(value));
            }
            "--output" => {
                let value = iter
                    .next()
                    .ok_or_else(|| String::from("--output requires a path argument"))?;
                output = Some(PathBuf::from(value));
            }
            "--help" | "-h" => {
                return Err(String::from(
                    "usage: threats-sarif --input PATH --output PATH",
                ));
            }
            other => return Err(format!("unrecognized argument: {other}")),
        }
    }

    let input = input.ok_or_else(|| String::from("--input is required"))?;
    let output = output.ok_or_else(|| String::from("--output is required"))?;
    Ok((input, output))
}

fn parse_risk_scores_args(args: &[&str]) -> Result<(PathBuf, PathBuf, PathBuf), String> {
    let mut risk_scores = None;
    let mut threats = None;
    let mut output = None;
    let mut iter = args.iter();

    while let Some(arg) = iter.next() {
        match *arg {
            "--risk-scores" => {
                let value = iter
                    .next()
                    .ok_or_else(|| String::from("--risk-scores requires a path argument"))?;
                risk_scores = Some(PathBuf::from(value));
            }
            "--threats" => {
                let value = iter
                    .next()
                    .ok_or_else(|| String::from("--threats requires a path argument"))?;
                threats = Some(PathBuf::from(value));
            }
            "--output" => {
                let value = iter
                    .next()
                    .ok_or_else(|| String::from("--output requires a path argument"))?;
                output = Some(PathBuf::from(value));
            }
            "--help" | "-h" => {
                return Err(String::from(
                    "usage: risk-scores-sarif --risk-scores PATH --threats PATH --output PATH",
                ));
            }
            other => return Err(format!("unrecognized argument: {other}")),
        }
    }

    let risk_scores = risk_scores.ok_or_else(|| String::from("--risk-scores is required"))?;
    let threats = threats.ok_or_else(|| String::from("--threats is required"))?;
    let output = output.ok_or_else(|| String::from("--output is required"))?;
    Ok((risk_scores, threats, output))
}

fn parse_infographic_data_args(
    default_root: &Path,
    args: &[&str],
) -> Result<(PathBuf, String, Option<PathBuf>), String> {
    let mut root = default_root.to_path_buf();
    let mut template: Option<String> = None;
    let mut output_path = None;
    let mut iter = args.iter();

    while let Some(arg) = iter.next() {
        match *arg {
            "--root" => {
                let value = iter
                    .next()
                    .ok_or_else(|| String::from("--root requires a path argument"))?;
                root = PathBuf::from(value);
            }
            "--template" => {
                let value = iter
                    .next()
                    .ok_or_else(|| String::from("--template requires a value"))?;
                template = Some((*value).to_string());
            }
            "--output" => {
                let value = iter
                    .next()
                    .ok_or_else(|| String::from("--output requires a path argument"))?;
                output_path = Some(PathBuf::from(value));
            }
            "--help" | "-h" => {
                return Err(String::from(
                    "usage: infographic-data --template TEMPLATE [--root PATH] [--output PATH]",
                ));
            }
            other => return Err(format!("unrecognized argument: {other}")),
        }
    }

    let template = template.ok_or_else(|| String::from("--template is required"))?;
    Ok((root, template, output_path))
}

fn ensure_contained_input_path(
    root: &Path,
    candidate: &Path,
    label: &str,
) -> Result<PathBuf, String> {
    if contains_parent_dir(candidate) {
        return Err(format!(
            "path policy failed for {label}: {} contains parent traversal",
            candidate.display()
        ));
    }
    let root = root.canonicalize().map_err(|err| {
        format!(
            "path policy failed for {label}: failed to resolve root {}: {err}",
            root.display()
        )
    })?;
    let candidate = candidate.canonicalize().map_err(|err| {
        format!(
            "path policy failed for {label}: failed to resolve {}: {err}",
            candidate.display()
        )
    })?;

    if candidate.starts_with(&root) {
        Ok(candidate)
    } else {
        Err(format!(
            "path policy failed for {label}: {} escapes {}",
            candidate.display(),
            root.display()
        ))
    }
}

fn ensure_contained_output_path(
    root: &Path,
    candidate: &Path,
    label: &str,
) -> Result<PathBuf, String> {
    if contains_parent_dir(candidate) {
        return Err(format!(
            "path policy failed for {label}: {} contains parent traversal",
            candidate.display()
        ));
    }
    let root = root.canonicalize().map_err(|err| {
        format!(
            "path policy failed for {label}: failed to resolve root {}: {err}",
            root.display()
        )
    })?;
    let candidate = if candidate.is_absolute() {
        candidate.to_path_buf()
    } else {
        root.join(candidate)
    };

    let mut existing = candidate.as_path();
    while !existing.exists() {
        existing = existing.parent().ok_or_else(|| {
            format!(
                "path policy failed for {label}: unable to find existing ancestor for {}",
                candidate.display()
            )
        })?;
    }
    let existing = existing.canonicalize().map_err(|err| {
        format!(
            "path policy failed for {label}: failed to resolve {}: {err}",
            existing.display()
        )
    })?;

    if !existing.starts_with(&root) {
        return Err(format!(
            "path policy failed for {label}: {} escapes {}",
            existing.display(),
            root.display()
        ));
    }

    let mut current = candidate.as_path();
    while let Some(parent) = current.parent() {
        if !parent.exists() {
            break;
        }
        let metadata = parent.symlink_metadata().map_err(|err| {
            format!(
                "path policy failed for {label}: failed to inspect {}: {err}",
                parent.display()
            )
        })?;
        if metadata.file_type().is_symlink() {
            return Err(format!(
                "path policy failed for {label}: {} traverses symlink {}",
                candidate.display(),
                parent.display()
            ));
        }
        if parent == root {
            break;
        }
        current = parent;
    }

    Ok(candidate)
}

fn contains_parent_dir(path: &Path) -> bool {
    path.components()
        .any(|component| matches!(component, std::path::Component::ParentDir))
}
