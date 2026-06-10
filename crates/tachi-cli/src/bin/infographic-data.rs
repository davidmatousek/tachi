use std::path::PathBuf;
use std::process::ExitCode;

use tachi_shell::commands::infographic_data_output;

fn main() -> ExitCode {
    let (root, template, output_path) = match parse_args() {
        Ok(values) => values,
        Err(message) => {
            eprintln!("{message}");
            return ExitCode::from(2);
        }
    };

    match infographic_data_output(&root, &template) {
        Ok(payload) => {
            if let Some(output_path) = output_path {
                if let Some(parent) = output_path.parent() {
                    if let Err(err) = std::fs::create_dir_all(parent) {
                        eprintln!("failed to create output directory: {err}");
                        return ExitCode::from(1);
                    }
                }
                if let Err(err) = std::fs::write(&output_path, payload.as_bytes()) {
                    eprintln!("failed to write output file: {err}");
                    return ExitCode::from(1);
                }
            } else {
                print!("{payload}");
            }
            ExitCode::SUCCESS
        }
        Err(message) => {
            eprintln!("{message}");
            ExitCode::from(1)
        }
    }
}

fn parse_args() -> Result<(PathBuf, String, Option<PathBuf>), String> {
    let mut root = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
    let mut template: Option<String> = None;
    let mut output_path = None;
    let mut iter = std::env::args().skip(1);

    while let Some(arg) = iter.next() {
        match arg.as_str() {
            "--root" => {
                let value = match iter.next() {
                    Some(value) => value,
                    None => {
                        return Err(String::from("--root requires a path argument"));
                    }
                };
                root = PathBuf::from(value);
            }
            "--template" => {
                template = Some(
                    iter.next()
                        .ok_or_else(|| String::from("--template requires a value"))?,
                );
            }
            "--output" => {
                let value = match iter.next() {
                    Some(value) => value,
                    None => {
                        return Err(String::from("--output requires a path argument"));
                    }
                };
                output_path = Some(PathBuf::from(value));
            }
            "--help" | "-h" => {
                eprintln!(
                    "usage: infographic-data --template TEMPLATE [--root PATH] [--output PATH]"
                );
                std::process::exit(0);
            }
            other => {
                return Err(format!("unrecognized argument: {other}"));
            }
        }
    }

    let template = template.ok_or_else(|| String::from("--template is required"))?;
    Ok((root, template, output_path))
}
