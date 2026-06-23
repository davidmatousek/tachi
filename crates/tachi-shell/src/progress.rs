use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;

use crate::commands::CommandOutput;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ProgressEvent {
    pub command: String,
    pub message: String,
}

pub trait ProgressReporter {
    fn emit(&mut self, event: ProgressEvent);
}

#[derive(Debug, Default)]
pub struct NoopProgressReporter;

impl ProgressReporter for NoopProgressReporter {
    fn emit(&mut self, _event: ProgressEvent) {}
}

#[derive(Debug, Clone, Default)]
pub struct CancellationToken {
    cancelled: Arc<AtomicBool>,
}

impl CancellationToken {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn cancel(&self) {
        self.cancelled.store(true, Ordering::SeqCst);
    }

    pub fn is_cancelled(&self) -> bool {
        self.cancelled.load(Ordering::SeqCst)
    }
}

pub fn cancel_running_command(token: &CancellationToken) {
    token.cancel();
}

pub fn emit_progress_event(reporter: &mut dyn ProgressReporter, command: &str, message: &str) {
    reporter.emit(ProgressEvent {
        command: command.to_string(),
        message: message.to_string(),
    });
}

fn cancelled_output(command: &str) -> CommandOutput {
    CommandOutput {
        status: 130,
        stdout: String::new(),
        stderr: format!("{command} cancelled\n"),
    }
}

pub fn invoke_with_progress<F>(
    command: &str,
    token: &CancellationToken,
    reporter: &mut dyn ProgressReporter,
    run: F,
) -> CommandOutput
where
    F: FnOnce(&CancellationToken, &mut dyn ProgressReporter) -> CommandOutput,
{
    emit_progress_event(reporter, command, "starting");
    if token.is_cancelled() {
        emit_progress_event(reporter, command, "cancelled");
        return cancelled_output(command);
    }

    let output = run(token, reporter);
    if token.is_cancelled() {
        emit_progress_event(reporter, command, "cancelled");
        return cancelled_output(command);
    }

    emit_progress_event(reporter, command, "completed");
    output
}

#[cfg(test)]
mod tests {
    use super::*;

    #[derive(Default)]
    struct RecordingReporter {
        events: Vec<ProgressEvent>,
    }

    impl ProgressReporter for RecordingReporter {
        fn emit(&mut self, event: ProgressEvent) {
            self.events.push(event);
        }
    }

    #[test]
    fn invoke_with_progress_emits_start_and_completed() {
        let token = CancellationToken::new();
        let mut reporter = RecordingReporter::default();

        let output = invoke_with_progress("install", &token, &mut reporter, |_token, _reporter| {
            CommandOutput {
                status: 0,
                stdout: String::from("ok"),
                stderr: String::new(),
            }
        });

        assert_eq!(output.status, 0);
        assert_eq!(
            reporter.events,
            vec![
                ProgressEvent {
                    command: String::from("install"),
                    message: String::from("starting"),
                },
                ProgressEvent {
                    command: String::from("install"),
                    message: String::from("completed"),
                },
            ]
        );
    }
}
