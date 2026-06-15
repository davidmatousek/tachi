use std::path::Path;
use std::path::PathBuf;

use crate::commands::infographic_data_output;
use crate::commands::{run_script_command_with_progress, CommandOutput};
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
    invoke_with_progress(command, token, reporter, |token, reporter| match command {
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
            let mut bootstrap_args = Vec::with_capacity(args.len() + 1);
            bootstrap_args.push("--bootstrap");
            bootstrap_args.extend_from_slice(args);
            let scripts_dir = super::commands::control_plane_scripts_dir(root);
            run_script_command_with_progress(
                &scripts_dir,
                "update.sh",
                &bootstrap_args,
                root,
                token,
                reporter,
            )
        }
        "infographic-data" => dispatch_infographic_data(root, args, token, reporter),
        other => CommandOutput {
            status: 2,
            stdout: String::new(),
            stderr: format!("unsupported command: {other}\n"),
        },
    })
}

fn dispatch_infographic_data(
    root: &Path,
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

    let (root, template, output_path) = match parse_infographic_data_args(root, args) {
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

    emit_progress_event(reporter, "infographic-data", "building");
    if token.is_cancelled() {
        emit_progress_event(reporter, "infographic-data", "cancelled");
        return CommandOutput {
            status: 130,
            stdout: String::new(),
            stderr: String::from("infographic-data cancelled\n"),
        };
    }

    match infographic_data_output(&root, &template) {
        Ok(payload) => {
            if let Some(output_path) = output_path {
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
