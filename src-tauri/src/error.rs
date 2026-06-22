use std::fmt;

use crate::CommandOutput;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DesktopErrorKind {
    Validation,
    Policy,
    Io,
    Timeout,
    Cancellation,
    Internal,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DesktopError {
    kind: DesktopErrorKind,
    message: String,
}

impl DesktopError {
    pub fn validation(message: impl Into<String>) -> Self {
        Self::new(DesktopErrorKind::Validation, message)
    }

    pub fn policy(message: impl Into<String>) -> Self {
        Self::new(DesktopErrorKind::Policy, message)
    }

    pub fn io(message: impl Into<String>) -> Self {
        Self::new(DesktopErrorKind::Io, message)
    }

    pub fn timeout(message: impl Into<String>) -> Self {
        Self::new(DesktopErrorKind::Timeout, message)
    }

    pub fn cancellation(message: impl Into<String>) -> Self {
        Self::new(DesktopErrorKind::Cancellation, message)
    }

    pub fn internal(message: impl Into<String>) -> Self {
        Self::new(DesktopErrorKind::Internal, message)
    }

    pub fn kind(&self) -> DesktopErrorKind {
        self.kind
    }

    pub fn code(&self) -> i32 {
        match self.kind {
            DesktopErrorKind::Validation => 2,
            DesktopErrorKind::Policy => 3,
            DesktopErrorKind::Io => 4,
            DesktopErrorKind::Timeout => 124,
            DesktopErrorKind::Cancellation => 130,
            DesktopErrorKind::Internal => 1,
        }
    }

    pub fn message(&self) -> &str {
        &self.message
    }

    pub fn into_command_output(self, _command: &str) -> CommandOutput {
        CommandOutput {
            status: self.code(),
            stdout: String::new(),
            stderr: format!("{}\n", self.message),
        }
    }

    fn new(kind: DesktopErrorKind, message: impl Into<String>) -> Self {
        Self {
            kind,
            message: message.into(),
        }
    }
}

impl fmt::Display for DesktopError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        self.message.fmt(f)
    }
}

impl std::error::Error for DesktopError {}
