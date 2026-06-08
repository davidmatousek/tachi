use std::path::PathBuf;
use std::process::ExitCode;

use tachi_shell::commands::report_data_output;

fn main() -> ExitCode {
    let (target_dir, template_dir) = match parse_args() {
        Ok(values) => values,
        Err(message) => {
            eprintln!("{message}");
            return ExitCode::from(2);
        }
    };

    match report_data_output(&target_dir, &template_dir) {
        Ok(output) => {
            print!("{output}");
            ExitCode::SUCCESS
        }
        Err(err) => {
            eprintln!("failed to build report data: {err}");
            ExitCode::from(1)
        }
    }
}

fn parse_args() -> Result<(PathBuf, PathBuf), String> {
    let mut args = std::env::args().skip(1);
    let mut target_dir = None;
    let mut template_dir = None;

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
            "--help" | "-h" => {
                return Err(String::from(
                    "usage: report-data --target-dir PATH --template-dir PATH",
                ));
            }
            other => {
                return Err(format!("unrecognized argument: {other}"));
            }
        }
    }

    let target_dir = target_dir.ok_or_else(|| String::from("--target-dir is required"))?;
    let template_dir = template_dir.ok_or_else(|| String::from("--template-dir is required"))?;
    Ok((target_dir, template_dir))
}
