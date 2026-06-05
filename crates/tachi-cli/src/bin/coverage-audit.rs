use std::path::PathBuf;
use std::process::ExitCode;

use tachi_shell::commands::coverage_audit_output;

fn main() -> ExitCode {
    let root = match parse_root() {
        Ok(root) => root,
        Err(message) => {
            eprintln!("{message}");
            return ExitCode::from(2);
        }
    };

    print!("{}", coverage_audit_output(&root));
    ExitCode::SUCCESS
}

fn parse_root() -> Result<PathBuf, String> {
    let mut args = std::env::args().skip(1);
    let mut root = std::env::current_dir()
        .map_err(|err| format!("failed to read current directory: {err}"))?;

    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--root" => {
                let value = args
                    .next()
                    .ok_or_else(|| String::from("--root requires a path argument"))?;
                root = PathBuf::from(value);
            }
            "--help" | "-h" => {
                return Err(String::from("usage: coverage-audit [--root PATH]"));
            }
            other => {
                return Err(format!("unrecognized argument: {other}"));
            }
        }
    }

    Ok(root)
}
