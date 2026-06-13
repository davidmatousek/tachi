use std::path::Path;
use std::path::PathBuf;

use crate::commands::infographic_data_output;
use crate::commands::{
    bootstrap_output, init_output, install_output, update_output, CommandOutput,
};

pub fn dispatch_command(command: &str, root: &Path, args: &[&str]) -> CommandOutput {
    match command {
        "install" => install_output(root, args),
        "init" => init_output(root, args),
        "update" => update_output(root, args),
        "bootstrap" => bootstrap_output(root, args),
        "infographic-data" => dispatch_infographic_data(root, args),
        other => CommandOutput {
            status: 2,
            stdout: String::new(),
            stderr: format!("unsupported command: {other}\n"),
        },
    }
}

fn dispatch_infographic_data(root: &Path, args: &[&str]) -> CommandOutput {
    let (root, template, output_path) = match parse_infographic_data_args(root, args) {
        Ok(values) => values,
        Err(message) => {
            return CommandOutput {
                status: 2,
                stdout: String::new(),
                stderr: format!("{message}\n"),
            };
        }
    };

    match infographic_data_output(&root, &template) {
        Ok(payload) => {
            if let Some(output_path) = output_path {
                if let Some(parent) = output_path.parent() {
                    if let Err(err) = std::fs::create_dir_all(parent) {
                        return CommandOutput {
                            status: 1,
                            stdout: String::new(),
                            stderr: format!("failed to create output directory: {err}\n"),
                        };
                    }
                }
                if let Err(err) = std::fs::write(&output_path, payload.as_bytes()) {
                    return CommandOutput {
                        status: 1,
                        stdout: String::new(),
                        stderr: format!("failed to write output file: {err}\n"),
                    };
                }
                CommandOutput {
                    status: 0,
                    stdout: String::new(),
                    stderr: String::new(),
                }
            } else {
                CommandOutput {
                    status: 0,
                    stdout: payload,
                    stderr: String::new(),
                }
            }
        }
        Err(message) => CommandOutput {
            status: 1,
            stdout: String::new(),
            stderr: format!("{message}\n"),
        },
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
