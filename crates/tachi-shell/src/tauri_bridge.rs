use std::path::Path;

use crate::commands::{
    bootstrap_output, init_output, install_output, update_output, CommandOutput,
};

pub fn dispatch_command(command: &str, root: &Path, args: &[&str]) -> CommandOutput {
    match command {
        "install" => install_output(root, args),
        "init" => init_output(root, args),
        "update" => update_output(root, args),
        "bootstrap" => bootstrap_output(root, args),
        other => CommandOutput {
            status: 2,
            stdout: String::new(),
            stderr: format!("unsupported command: {other}\n"),
        },
    }
}
