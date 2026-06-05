use std::path::PathBuf;
use std::process::ExitCode;

use tachi_shell::commands::infographic_data_output;

fn main() -> ExitCode {
    let mut root = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
    let mut template: Option<String> = None;
    let mut iter = std::env::args().skip(1);

    while let Some(arg) = iter.next() {
        match arg.as_str() {
            "--root" => {
                let value = match iter.next() {
                    Some(value) => value,
                    None => {
                        eprintln!("--root requires a path argument");
                        return ExitCode::from(2);
                    }
                };
                root = PathBuf::from(value);
            }
            "--template" => {
                template = iter.next();
            }
            "--help" | "-h" => {
                eprintln!("usage: infographic-data --template TEMPLATE [--root PATH]");
                return ExitCode::from(0);
            }
            other => {
                eprintln!("unrecognized argument: {other}");
                return ExitCode::from(2);
            }
        }
    }

    let template = template.unwrap_or_else(|| String::from("baseball-card"));
    match infographic_data_output(&root, &template) {
        Ok(payload) => {
            print!("{payload}");
            ExitCode::SUCCESS
        }
        Err(message) => {
            eprintln!("{message}");
            ExitCode::from(1)
        }
    }
}
