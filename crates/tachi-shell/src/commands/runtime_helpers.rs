use std::io::{BufReader, Read};
use std::thread::JoinHandle;

use crate::progress::{emit_progress_event, ProgressReporter};

use super::CommandOutput;

pub(crate) struct FinalizeScriptOutputRequest<'a> {
    pub script_name: &'a str,
    pub reporter: &'a mut dyn ProgressReporter,
    pub wait_result: std::io::Result<std::process::ExitStatus>,
    pub stdout_handle: JoinHandle<Vec<u8>>,
    pub stderr_handle: JoinHandle<Vec<u8>>,
    pub status: i32,
    pub phase: &'a str,
}

pub(crate) trait ScriptOutputSink {
    fn finalize_script_output(&self, request: FinalizeScriptOutputRequest<'_>) -> CommandOutput;
}

pub(crate) struct SystemScriptOutputSink;

impl ScriptOutputSink for SystemScriptOutputSink {
    fn finalize_script_output(&self, request: FinalizeScriptOutputRequest<'_>) -> CommandOutput {
        finalize_script_output(request)
    }
}

pub(crate) fn finalize_script_output(request: FinalizeScriptOutputRequest<'_>) -> CommandOutput {
    let stdout = request.stdout_handle.join().unwrap_or_default();
    let stderr = request.stderr_handle.join().unwrap_or_default();
    emit_progress_event(request.reporter, request.script_name, request.phase);
    match request.wait_result {
        Ok(output_status) => CommandOutput {
            status: if request.status == 130 || request.status == 124 {
                request.status
            } else {
                output_status.code().unwrap_or(1)
            },
            stdout: String::from_utf8_lossy(&stdout).to_string(),
            stderr: String::from_utf8_lossy(&stderr).to_string(),
        },
        Err(err) => CommandOutput {
            status: request.status,
            stdout: String::from_utf8_lossy(&stdout).to_string(),
            stderr: format!(
                "{} {}: {err}\n{}",
                request.script_name,
                request.phase,
                String::from_utf8_lossy(&stderr)
            ),
        },
    }
}

pub(crate) fn capture_stream<R: Read>(reader: R, cap: usize) -> Vec<u8> {
    let mut reader = BufReader::new(reader);
    let mut buffer = [0u8; 4096];
    let mut collected = Vec::new();

    loop {
        match reader.read(&mut buffer) {
            Ok(0) => break,
            Ok(read) => {
                let remaining = cap.saturating_sub(collected.len());
                if remaining > 0 {
                    collected.extend_from_slice(&buffer[..read.min(remaining)]);
                }
            }
            Err(_) => break,
        }
    }

    collected
}

#[cfg(test)]
mod tests {
    use super::{capture_stream, finalize_script_output};
    use super::FinalizeScriptOutputRequest;
    use crate::progress::NoopProgressReporter;
    use std::io::Cursor;
    use std::thread;

    #[test]
    fn capture_stream_caps_output_to_requested_bytes() {
        let data = Cursor::new(b"abcdef".to_vec());
        let captured = capture_stream(data, 4);
        assert_eq!(captured, b"abcd");
    }

    #[test]
    fn finalize_script_output_preserves_cancel_and_timeout_statuses() {
        let mut reporter = NoopProgressReporter;
        let stdout_handle = thread::spawn(Vec::new);
        let stderr_handle = thread::spawn(Vec::new);
        let output = finalize_script_output(FinalizeScriptOutputRequest {
            script_name: "script",
            reporter: &mut reporter,
            wait_result: Ok(std::process::ExitStatus::from_raw(0)),
            stdout_handle,
            stderr_handle,
            status: 130,
            phase: "cancelled",
        });

        assert_eq!(output.status, 130);
        assert_eq!(output.stdout, "");
        assert_eq!(output.stderr, "");
    }

    #[cfg(unix)]
    use std::os::unix::process::ExitStatusExt;

    #[test]
    fn finalize_script_output_reports_failed_wait_result() {
        let mut reporter = NoopProgressReporter;
        let stdout_handle = thread::spawn(|| b"out".to_vec());
        let stderr_handle = thread::spawn(|| b"err".to_vec());
        let output = finalize_script_output(FinalizeScriptOutputRequest {
            script_name: "script",
            reporter: &mut reporter,
            wait_result: Err(std::io::Error::other("boom")),
            stdout_handle,
            stderr_handle,
            status: 1,
            phase: "failed",
        });

        assert_eq!(output.status, 1);
        assert!(output.stderr.contains("script failed"));
    }
}
