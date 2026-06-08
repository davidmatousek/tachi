use std::path::PathBuf;
use std::process::ExitCode;

use tachi_shell::commands::report_data_output;

fn main() -> ExitCode {
    let (target_dir, template_dir, output_path) = match parse_args() {
        Ok(values) => values,
        Err(message) => {
            eprintln!("{message}");
            return ExitCode::from(2);
        }
    };

    let output = report_data_output(&target_dir, &template_dir);

    if let Some(output_path) = output_path {
        if let Some(parent) = output_path.parent() {
            if let Err(err) = std::fs::create_dir_all(parent) {
                eprintln!("failed to create output directory: {err}");
                return ExitCode::from(1);
            }
        }
        if let Err(err) = std::fs::write(&output_path, output.as_bytes()) {
            eprintln!("failed to write output file: {err}");
            return ExitCode::from(1);
        }
    } else {
        print!("{output}");
    }

    eprintln!("report-data.typ generated");
    ExitCode::SUCCESS
}

fn parse_args() -> Result<(PathBuf, PathBuf, Option<PathBuf>), String> {
    let mut args = std::env::args().skip(1);
    let mut target_dir = None;
    let mut template_dir = None;
    let mut output_path = None;

    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--target-dir" => {
                let value = args
                    .next()
                    .ok_or_else(|| String::from("--target-dir requires a path argument"))?;
                target_dir = Some(PathBuf::from(value));
            }
            "--template-dir" => {
                let value = args
                    .next()
                    .ok_or_else(|| String::from("--template-dir requires a path argument"))?;
                template_dir = Some(PathBuf::from(value));
            }
            "--output" => {
                let value = args
                    .next()
                    .ok_or_else(|| String::from("--output requires a path argument"))?;
                output_path = Some(PathBuf::from(value));
            }
            "--help" | "-h" => {
                return Err(String::from(
                    "usage: report-data --target-dir PATH --template-dir PATH [--output PATH]",
                ));
            }
            other => {
                return Err(format!("unrecognized argument: {other}"));
            }
        }
    }

    let target_dir = target_dir.ok_or_else(|| String::from("--target-dir is required"))?;
    let template_dir = template_dir.ok_or_else(|| String::from("--template-dir is required"))?;
    Ok((target_dir, template_dir, output_path))
}
