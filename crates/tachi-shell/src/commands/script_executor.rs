use std::path::Path;
use std::process::Command;
use std::process::Stdio;
use std::thread::sleep;
use std::time::Duration;
use std::time::Instant;

#[cfg(unix)]
use std::os::unix::process::CommandExt;

use crate::progress::emit_progress_event;
use crate::progress::CancellationToken;
use crate::progress::ProgressReporter;

use super::runtime_helpers;
use super::CommandOutput;

pub(crate) const DEFAULT_EXECUTION_TIMEOUT: Duration = Duration::from_secs(30);
pub(crate) const DEFAULT_OUTPUT_CAP_BYTES: usize = 64 * 1024;
const POLL_INTERVAL: Duration = Duration::from_millis(10);

pub(crate) trait ScriptExecutor {
    fn run(&self, request: ScriptExecutionRequest<'_>) -> CommandOutput;
}

pub(crate) struct ScriptExecutionRequest<'a> {
    pub script_name: &'a str,
    pub script_path: &'a Path,
    pub cwd: &'a Path,
    pub args: &'a [&'a str],
    pub timeout: Duration,
    pub output_cap: usize,
    pub token: &'a CancellationToken,
    pub reporter: &'a mut dyn ProgressReporter,
}

pub(crate) struct SystemScriptExecutor;

impl ScriptExecutor for SystemScriptExecutor {
    fn run(&self, request: ScriptExecutionRequest<'_>) -> CommandOutput {
        run_system_script(request)
    }
}

pub(crate) fn run_script_command_with_progress_using<E: ScriptExecutor>(
    executor: &E,
    script_dir: &Path,
    script_name: &str,
    args: &[&str],
    repo_root: &Path,
    token: &CancellationToken,
    reporter: &mut dyn ProgressReporter,
) -> CommandOutput {
    let timeout = execution_timeout();
    let output_cap = execution_output_cap();
    let script_path = script_dir.join(script_name);
    let cwd = script_dir.parent().unwrap_or(repo_root);
    executor.run(ScriptExecutionRequest {
        script_name,
        script_path: &script_path,
        cwd,
        args,
        timeout,
        output_cap,
        token,
        reporter,
    })
}

fn run_system_script(request: ScriptExecutionRequest<'_>) -> CommandOutput {
    emit_progress_event(request.reporter, request.script_name, "starting");
    if request.token.is_cancelled() {
        emit_progress_event(request.reporter, request.script_name, "cancelled");
        return CommandOutput {
            status: 130,
            stdout: String::new(),
            stderr: format!("{} cancelled\n", request.script_name),
        };
    }

    let spawn_result = Command::new(request.script_path)
        .current_dir(request.cwd)
        .args(request.args)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .process_group(0)
        .spawn();

    let mut child = match spawn_result {
        Ok(child) => child,
        Err(err) => {
            emit_progress_event(request.reporter, request.script_name, "failed");
            return CommandOutput {
                status: 1,
                stdout: String::new(),
                stderr: format!("failed to execute {}: {err}\n", request.script_name),
            };
        }
    };
    let stdout = child.stdout.take().expect("child stdout piped");
    let stderr = child.stderr.take().expect("child stderr piped");
    let stdout_handle =
        std::thread::spawn(move || runtime_helpers::capture_stream(stdout, request.output_cap));
    let stderr_handle =
        std::thread::spawn(move || runtime_helpers::capture_stream(stderr, request.output_cap));
    let start = Instant::now();
    let mut running_emitted = false;

    loop {
        if request.token.is_cancelled() {
            terminate_process_group(&mut child);
            return runtime_helpers::finalize_script_output(
                request.script_name,
                request.reporter,
                child.wait(),
                stdout_handle,
                stderr_handle,
                130,
                "cancelled",
            );
        }

        if start.elapsed() >= request.timeout {
            terminate_process_group(&mut child);
            return runtime_helpers::finalize_script_output(
                request.script_name,
                request.reporter,
                child.wait(),
                stdout_handle,
                stderr_handle,
                124,
                "timed out",
            );
        }

        match child.try_wait() {
            Ok(Some(status)) => {
                let stdout = stdout_handle.join().unwrap_or_default();
                let stderr = stderr_handle.join().unwrap_or_default();
                emit_progress_event(request.reporter, request.script_name, "completed");
                return CommandOutput {
                    status: status.code().unwrap_or(1),
                    stdout: String::from_utf8_lossy(&stdout).to_string(),
                    stderr: String::from_utf8_lossy(&stderr).to_string(),
                };
            }
            Ok(None) => {
                if !running_emitted {
                    emit_progress_event(request.reporter, request.script_name, "running");
                    running_emitted = true;
                }
                sleep(POLL_INTERVAL);
            }
            Err(err) => {
                terminate_process_group(&mut child);
                emit_progress_event(request.reporter, request.script_name, "failed");
                let stdout = stdout_handle.join().unwrap_or_default();
                let stderr = stderr_handle.join().unwrap_or_default();
                return CommandOutput {
                    status: 1,
                    stdout: String::from_utf8_lossy(&stdout).to_string(),
                    stderr: format!(
                        "failed to monitor {}: {err}\n{}",
                        request.script_name,
                        String::from_utf8_lossy(&stderr)
                    ),
                };
            }
        }
    }
}

fn execution_timeout() -> Duration {
    std::env::var("TACHI_EXECUTION_TIMEOUT_MS")
        .ok()
        .and_then(|value| value.parse::<u64>().ok())
        .map(Duration::from_millis)
        .unwrap_or(DEFAULT_EXECUTION_TIMEOUT)
}

fn execution_output_cap() -> usize {
    std::env::var("TACHI_EXECUTION_OUTPUT_CAP_BYTES")
        .ok()
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(DEFAULT_OUTPUT_CAP_BYTES)
}

#[cfg(unix)]
fn terminate_process_group(child: &mut std::process::Child) {
    let _ = Command::new("kill")
        .arg("-TERM")
        .arg(format!("-{}", child.id()))
        .status();
    let _ = child.kill();
}

#[cfg(not(unix))]
fn terminate_process_group(child: &mut std::process::Child) {
    let _ = child.kill();
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::progress::NoopProgressReporter;
    use std::cell::Cell;
    use std::path::PathBuf;

    struct FakeScriptExecutor {
        calls: Cell<usize>,
    }

    impl ScriptExecutor for FakeScriptExecutor {
        fn run(&self, request: ScriptExecutionRequest<'_>) -> CommandOutput {
            self.calls.set(self.calls.get() + 1);
            assert_eq!(request.script_name, "install.sh");
            assert_eq!(request.cwd, Path::new("/tmp/repo"));
            assert_eq!(request.args, &["--yes"]);
            assert_eq!(request.timeout, DEFAULT_EXECUTION_TIMEOUT);
            assert_eq!(request.output_cap, DEFAULT_OUTPUT_CAP_BYTES);
            CommandOutput {
                status: 7,
                stdout: String::from("fake"),
                stderr: String::new(),
            }
        }
    }

    #[test]
    fn injected_executor_receives_script_request_without_spawning() {
        let executor = FakeScriptExecutor {
            calls: Cell::new(0),
        };
        let script_dir = PathBuf::from("/tmp/repo/scripts");
        let token = CancellationToken::new();
        let mut reporter = NoopProgressReporter;

        let output = run_script_command_with_progress_using(
            &executor,
            &script_dir,
            "install.sh",
            &["--yes"],
            Path::new("/tmp/repo"),
            &token,
            &mut reporter,
        );

        assert_eq!(output.status, 7);
        assert_eq!(output.stdout, "fake");
        assert_eq!(executor.calls.get(), 1);
    }
}
