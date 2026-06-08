use std::path::PathBuf;
use std::process::ExitCode;

use tachi_shell::commands::threats_sarif_output;

fn main() -> ExitCode {
    let (input, output) = match parse_args() {
        Ok(values) => values,
        Err(message) => {
            eprintln!("{message}");
            return ExitCode::from(2);
        }
    };

    let payload = match threats_sarif_output(&input) {
        Ok(payload) => payload,
        Err(message) => {
            eprintln!("{message}");
            return ExitCode::from(1);
        }
    };

    if let Some(parent) = output.parent() {
        if let Err(err) = std::fs::create_dir_all(parent) {
            eprintln!("failed to create output directory: {err}");
            return ExitCode::from(1);
        }
    }
    if let Err(err) = std::fs::write(&output, payload.sarif.as_bytes()) {
        eprintln!("failed to write output file: {err}");
        return ExitCode::from(1);
    }

    eprintln!("OK: wrote {} findings to {}", payload.findings_count, output.display());
    eprintln!(
        "AG-8 present: {} ({})",
        payload.ag8_status.is_some(),
        payload.ag8_status.unwrap_or_else(|| String::from("absent"))
    );

    ExitCode::SUCCESS
}

fn parse_args() -> Result<(PathBuf, PathBuf), String> {
    let mut args = std::env::args().skip(1);
    let mut input = None;
    let mut output = None;

    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--input" => {
                let value = args
                    .next()
                    .ok_or_else(|| String::from("--input requires a path argument"))?;
                input = Some(PathBuf::from(value));
            }
            "--output" => {
                let value = args
                    .next()
                    .ok_or_else(|| String::from("--output requires a path argument"))?;
                output = Some(PathBuf::from(value));
            }
            "--help" | "-h" => {
                return Err(String::from("usage: threats-sarif --input PATH --output PATH"));
            }
            other => {
                return Err(format!("unrecognized argument: {other}"));
            }
        }
    }

    let input = input.ok_or_else(|| String::from("--input is required"))?;
    let output = output.ok_or_else(|| String::from("--output is required"))?;
    Ok((input, output))
}
