use tachi_mcp::stdio::{run, startup_mode_from_args, StartupMode};

#[test]
fn stdio_startup_requires_explicit_flag() {
    let err = startup_mode_from_args(&["tachi-mcp".to_string()])
        .expect_err("stdio mode should require an explicit flag");
    assert!(err.contains("--stdio"));
}

#[test]
fn stdio_startup_accepts_explicit_flag() {
    let args = vec!["tachi-mcp".to_string(), "--stdio".to_string()];
    assert_eq!(
        startup_mode_from_args(&args).expect("stdio mode"),
        StartupMode::Stdio
    );
    run(&args).expect("stdio run");
}
