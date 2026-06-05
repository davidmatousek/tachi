use std::path::PathBuf;
use std::process::ExitCode;

use tachi_shell::commands::bootstrap_output;

fn main() -> ExitCode {
    let mut args = std::env::args().skip(1);
    let mut root = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
    let mut passthrough = Vec::new();

    while let Some(arg) = args.next() {
        if arg == "--root" {
            let value = match args.next() {
                Some(value) => value,
                None => {
                    eprintln!("--root requires a path argument");
                    return ExitCode::from(2);
                }
            };
            root = PathBuf::from(value);
            continue;
        }

        if arg == "-h" || arg == "--help" {
            eprintln!("usage: bootstrap [--root PATH] [update args]");
            return ExitCode::SUCCESS;
        }

        passthrough.push(arg);
    }

    let passthrough_refs: Vec<&str> = passthrough.iter().map(|arg| arg.as_str()).collect();
    let output = bootstrap_output(&root, &passthrough_refs);
    if !output.stdout.is_empty() {
        print!("{}", output.stdout);
    }
    if !output.stderr.is_empty() {
        eprint!("{}", output.stderr);
    }

    let status: u8 = output.status.try_into().unwrap_or(1);
    ExitCode::from(status)
}
