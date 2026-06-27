use std::path::{Path, PathBuf};

use crate::dispatch_desktop_command_with_noop_progress;
use crate::registered_commands;
use crate::DesktopCommandOutput;

#[derive(Debug, Clone)]
pub struct DesktopAppState {
    repo_root: PathBuf,
    repo_root_input: String,
    command_catalog: &'static [&'static str],
    last_command: Option<DesktopCommandSnapshot>,
    command_history: Vec<DesktopCommandSnapshot>,
}

impl DesktopAppState {
    pub fn new(repo_root: PathBuf) -> Self {
        let repo_root_input = repo_root.display().to_string();
        Self {
            repo_root,
            repo_root_input,
            command_catalog: registered_commands(),
            last_command: None,
            command_history: Vec::new(),
        }
    }

    pub fn repo_root(&self) -> &Path {
        &self.repo_root
    }

    pub fn repo_root_input(&self) -> &str {
        &self.repo_root_input
    }

    pub fn command_catalog(&self) -> &'static [&'static str] {
        self.command_catalog
    }

    pub fn set_repo_root(&mut self, repo_root: PathBuf) {
        self.repo_root = repo_root;
        self.repo_root_input = self.repo_root.display().to_string();
    }

    pub fn run_command(&mut self, command: &str, args: &[&str]) -> DesktopCommandOutput {
        let output = dispatch_desktop_command_with_noop_progress(command, &self.repo_root, args);
        let snapshot = DesktopCommandSnapshot::from_output(command, &output);
        self.push_command_snapshot(snapshot);
        output
    }

    pub fn last_command(&self) -> Option<&DesktopCommandSnapshot> {
        self.last_command.as_ref()
    }

    pub fn command_history(&self) -> &[DesktopCommandSnapshot] {
        &self.command_history
    }

    pub fn push_command_snapshot(&mut self, snapshot: DesktopCommandSnapshot) {
        self.last_command = Some(snapshot.clone());
        self.command_history.push(snapshot);
        if self.command_history.len() > 5 {
            self.command_history.remove(0);
        }
    }
}

#[derive(Debug, Clone)]
pub struct DesktopApp {
    state: DesktopAppState,
}

impl DesktopApp {
    pub fn new(repo_root: PathBuf) -> Self {
        Self {
            state: DesktopAppState::new(repo_root),
        }
    }

    pub fn state(&self) -> &DesktopAppState {
        &self.state
    }

    pub fn state_mut(&mut self) -> &mut DesktopAppState {
        &mut self.state
    }

    pub fn render_text(&self) -> String {
        let mut rendered = String::from("Tachi Desktop\n");
        rendered.push_str(&format!(
            "Repository root: {}\n\n",
            self.state.repo_root.display()
        ));
        rendered.push_str("Command catalog:\n");
        for command in self.state.command_catalog {
            rendered.push_str("- ");
            rendered.push_str(command);
            rendered.push('\n');
        }
        if let Some(last) = &self.state.last_command {
            rendered.push_str("\nLatest command:\n");
            rendered.push_str(&format!("Command: {}\n", last.command));
            rendered.push_str(&format!("Status: {}\n", last.status));
            if !last.stdout.is_empty() {
                rendered.push_str("Stdout:\n");
                rendered.push_str(&last.stdout);
                if !last.stdout.ends_with('\n') {
                    rendered.push('\n');
                }
            }
            if !last.stderr.is_empty() {
                rendered.push_str("Stderr:\n");
                rendered.push_str(&last.stderr);
                if !last.stderr.ends_with('\n') {
                    rendered.push('\n');
                }
            }
        }
        if !self.state.command_history.is_empty() {
            rendered.push_str("\nCommand history:\n");
            for entry in &self.state.command_history {
                rendered.push_str(&format!("{} [{}]\n", entry.command, entry.status));
            }
        }
        rendered
    }

    pub fn run_command(&mut self, command: &str, args: &[&str]) -> DesktopCommandOutput {
        self.state.run_command(command, args)
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DesktopCommandSnapshot {
    pub command: String,
    pub status: i32,
    pub stdout: String,
    pub stderr: String,
}

impl DesktopCommandSnapshot {
    pub fn from_output(command: &str, output: &DesktopCommandOutput) -> Self {
        Self {
            command: command.to_string(),
            status: output.status,
            stdout: output.stdout.clone(),
            stderr: output.stderr.clone(),
        }
    }
}
