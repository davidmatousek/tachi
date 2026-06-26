#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum StartupMode {
    Stdio,
}

pub fn startup_mode_from_args(args: &[String]) -> Result<StartupMode, String> {
    if args.iter().any(|arg| arg == "--stdio") {
        return Ok(StartupMode::Stdio);
    }

    Err(String::from("missing required --stdio flag"))
}

pub fn run(args: &[String]) -> Result<(), String> {
    match startup_mode_from_args(args)? {
        StartupMode::Stdio => Ok(()),
    }
}
