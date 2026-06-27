# GTK-Free Desktop GUI Host Issue Cards

**Last Updated**: 2026-06-26
**Status**: Beads-ready execution slices for the GTK-free desktop GUI host plan
**Source**: [2026-06-26-gtk-free-desktop-gui-host-roadmap.html.md](./2026-06-26-gtk-free-desktop-gui-host-roadmap.html.md)

These cards are TDD-first and ordered by measurable outcome.
Each card maps directly to a Beads issue ID and has a ranked acceptance
criterion that is specific, testable, and traceable.

## Card format

- `Epic`
- `Feature`
- `Capability`
- `Task`
- `Function`
- `Dependencies`
- `Acceptance criteria`
- `Validation`
- `Implementation owner`
- `Stage label`
- `Next test seam`
- `Priority`
- `Notes`

## Stage 0 - Native shell bootstrap

### DT-GUI-001 - Launchable native desktop shell

- `Epic`: GTK-Free Desktop GUI Host
- `Feature`: Native shell bootstrap
- `Capability`: launchable window, app lifecycle, repo-root context
- `Task`: add the minimal GUI app state, repo-root selection, and startup
  window so `tachi-desktop` can run as a native desktop program
- `Function`: `crates/tachi-desktop/src/main.rs`, `crates/tachi-desktop/src/app.rs`,
  `crates/tachi-desktop/src/lib.rs`
- `Dependencies`: existing `tachi-shell` command engine, GUI host crate scaffold
- `Acceptance criteria`:
  - `cargo run -p tachi-desktop` opens a native window without GTK/Wry.
  - The startup window renders the selected repository root and a non-empty
    command catalog.
  - Repository root selection works before any command execution path runs.
  - The GUI host can close cleanly without panic or orphaned background tasks.
- `Validation`: `cargo test -p tachi-desktop --all-targets`, manual open/close
  smoke run, `cargo tree -i glib --locked --target all`, `cargo tree -i gtk
  --locked --target all`
- `Implementation owner`: `tachi-desktop`
- `Stage label`: Stage 0
- `Next test seam`: `crates/tachi-desktop/tests/host_parity.rs`
- `Priority`: 0
- `Notes`: This is the first shipping native GUI slice.

### DT-GUI-001 task beads

- `DT-GUI-001.1` Add native app entrypoint and app state
  - Acceptance: the crate exposes a runnable desktop entrypoint and stores the
    selected repo root in app state.
- `DT-GUI-001.2` Render startup shell and repo-root selection
  - Acceptance: the startup window displays the repo root and a command list,
    and selecting a repo root updates the rendered state.
- `DT-GUI-001.3` Prove native launch does not require GTK/Wry
  - Acceptance: workspace dependency inspection shows no active GTK/Wry path and
    the native window launches in the GUI host smoke test.

### DT-GUI-002 - Shared command catalog parity

- `Epic`: GTK-Free Desktop GUI Host
- `Feature`: Native shell bootstrap
- `Capability`: command inventory surfaced identically in GUI and shell
- `Task`: bind the GUI command catalog to the shared registry so command names
  and ordering are single-sourced from `tachi-shell`
- `Function`: `crates/tachi-desktop/src/lib.rs`, `crates/tachi-shell/src/commands.rs`
- `Dependencies`: DT-GUI-001
- `Acceptance criteria`:
  - `registered_commands()` in the GUI host returns the same names, in the same
    order, as `command_registry().names()`.
  - Adding, removing, or reordering a shared command changes the GUI catalog
    automatically through the shared registry.
  - No command list duplication remains in the GUI host.
- `Validation`: `cargo test -p tachi-desktop --test host_parity`, `cargo test -p
  tachi-shell --test command_registry`
- `Implementation owner`: `tachi-desktop`
- `Stage label`: Stage 0
- `Next test seam`: `crates/tachi-desktop/tests/host_parity.rs`
- `Priority`: 0
- `Notes`: Treat catalog equality as a hard gate before command execution work.

### DT-GUI-002 task beads

- `DT-GUI-002.1` Add registry equality assertion
  - Acceptance: a failing-first test compares the GUI host catalog to the shared
    shell registry.
- `DT-GUI-002.2` Remove any GUI-local command list duplication
  - Acceptance: the GUI host has no independent command-name source and the
    parity test passes.

## Stage 1 - Shared command parity

### DT-GUI-003 - Command execution bridge

- `Epic`: GTK-Free Desktop GUI Host
- `Feature`: Shared command parity
- `Capability`: same stdout, stderr, and status as shared dispatch
- `Task`: wire GUI command execution to `dispatch_desktop_command` and surface
  the result in a structured result pane
- `Function`: `crates/tachi-desktop/src/lib.rs`, `crates/tachi-shell/src/tauri_bridge.rs`
- `Dependencies`: DT-GUI-002
- `Acceptance criteria`:
  - Representative commands return the same `status`, `stdout`, and `stderr`
    through the GUI as they do through direct shared dispatch.
  - Invalid commands fail closed and render a visible error instead of
    crashing.
  - Output for file-write cases remains byte-stable with direct dispatch.
- `Validation`: `cargo test -p tachi-desktop --test host_parity`
- `Implementation owner`: `tachi-desktop`
- `Stage label`: Stage 1
- `Next test seam`: `crates/tachi-desktop/tests/host_parity.rs`
- `Priority`: 1
- `Notes`: Keep all command semantics in `tachi-shell`.

### DT-GUI-003 task beads

- `DT-GUI-003.1` Add a GUI invoke path for shell dispatch
  - Acceptance: GUI command submission calls the shared dispatch path and the
    test fixture sees the expected `CommandOutput`.
- `DT-GUI-003.2` Prove bootstrap and infographic parity
  - Acceptance: bootstrap and infographic fixtures match the shared shell
    outputs exactly.
- `DT-GUI-003.3` Prove invalid command failure is fail-closed
  - Acceptance: unknown commands return a visible non-zero error and do not
    panic.

### DT-GUI-004 - Progress and cancellation parity

- `Epic`: GTK-Free Desktop GUI Host
- `Feature`: Shared command parity
- `Capability`: long-running command control without orphaned processes
- `Task`: surface progress events and a cancel action in the GUI with the same
  cancellation flow used by the shared shell engine
- `Function`: `crates/tachi-desktop/src/lib.rs`, `crates/tachi-shell/src/progress.rs`
- `Dependencies`: DT-GUI-003
- `Acceptance criteria`:
  - Canceling a long-running `install` run returns status `130`.
  - Progress events include the expected terminal states for start/cancel and
    do not skip the cancellation event.
  - The test harness confirms no child process survives the cancel path.
- `Validation`: `cargo test -p tachi-desktop --test host_parity`, `cargo test -p
  tachi-shell --test tauri_bridge`
- `Implementation owner`: `tachi-desktop`
- `Stage label`: Stage 1
- `Next test seam`: `crates/tachi-desktop/tests/host_parity.rs`
- `Priority`: 1
- `Notes`: Keep progress behavior identical between GUI and shared shell.

### DT-GUI-004 task beads

- `DT-GUI-004.1` Add GUI progress plumbing
  - Acceptance: progress messages surface in the GUI host test fixture.
- `DT-GUI-004.2` Add GUI cancellation action
  - Acceptance: canceling the fixture returns status `130` and emits a cancelled
    event.

## Stage 2 - Artifact workflows

### DT-GUI-005 - Artifact preview and save parity

- `Epic`: GTK-Free Desktop GUI Host
- `Feature`: Artifact workflows
- `Capability`: same artifact generation behavior as shell paths
- `Task`: add preview/save flows for report-data, infographic-data,
  threats-sarif, and risk-scores-sarif without changing artifact semantics
- `Function`: `crates/tachi-desktop/src/lib.rs`, `crates/tachi-shell/src/command_use_cases.rs`
- `Dependencies`: DT-GUI-003
- `Acceptance criteria`:
  - Preview mode renders the exact stdout payload produced by the shared shell.
  - Save mode writes bytes that match the command output exactly.
  - Path containment and parent traversal checks behave identically to the shared
    shell path policy.
  - Invalid output paths surface a typed error and do not create partial files.
- `Validation`: `cargo test -p tachi-desktop --test host_parity`, byte-level
  file comparison against shared dispatch output
- `Implementation owner`: `tachi-desktop`
- `Stage label`: Stage 2
- `Next test seam`: `crates/tachi-desktop/tests/host_parity.rs`
- `Priority`: 1
- `Notes`: Artifact parity must remain byte-stable.

### DT-GUI-005 task beads

- `DT-GUI-005.1` Add preview mode for report and infographic outputs
  - Acceptance: preview output matches shared shell stdout exactly.
- `DT-GUI-005.2` Add save mode for file-backed artifacts
  - Acceptance: saved artifact bytes match the shared shell result byte-for-byte.
- `DT-GUI-005.3` Prove path-policy failure behavior
  - Acceptance: invalid save paths fail closed and leave no partial artifact.

### DT-GUI-006 - Result presentation and UX stability

- `Epic`: GTK-Free Desktop GUI Host
- `Feature`: Artifact workflows
- `Capability`: actionable, readable command feedback in the native window
- `Task`: add a result pane, status indicators, and command history to make
  success, failure, cancel, and file-write outcomes visible
- `Function`: `crates/tachi-desktop/src/app.rs`, `crates/tachi-desktop/src/lib.rs`
- `Dependencies`: DT-GUI-004, DT-GUI-005
- `Acceptance criteria`:
  - Every command run ends in one visible terminal state: success, failure, or
    cancelled.
  - The latest result remains visible after later actions.
  - Users can distinguish stdout, stderr, and file-write success without logs.
  - The interface remains usable at standard desktop window sizes in smoke test.
- `Validation`: GUI smoke checklist, `cargo test -p tachi-desktop --all-targets`
- `Implementation owner`: `tachi-desktop`
- `Stage label`: Stage 2
- `Next test seam`: `crates/tachi-desktop/src/app.rs`
- `Priority`: 2
- `Notes`: Treat this as UX polish only after parity is stable.

### DT-GUI-006 task beads

- `DT-GUI-006.1` Add result pane and terminal-state display
  - Acceptance: the GUI exposes success/failure/cancelled status visibly.
- `DT-GUI-006.2` Persist the latest result in view state
  - Acceptance: a later command does not erase the prior result from the result
    pane unexpectedly.

## Stage 3 - Workspace hardening

### DT-GUI-007 - Workspace and dependency hardening

- `Epic`: GTK-Free Desktop GUI Host
- `Feature`: Workspace hardening
- `Capability`: active workspace proves GTK-free host path
- `Task`: make `tachi-desktop` the tested desktop crate and remove GTK/WebKit
  requirements from the active build path
- `Function`: `Cargo.toml`, `.github/workflows/rust-workspace.yml`,
  `.github/workflows/rust-clippy.yml`, `Cargo.lock`
- `Dependencies`: DT-GUI-003, DT-GUI-005
- `Acceptance criteria`:
  - `cargo test --workspace --all-targets` includes `tachi-desktop`.
  - `cargo tree -i glib --locked --target all` returns no active workspace path.
  - `cargo tree -i gtk --locked --target all` returns no active workspace path.
  - Workspace workflow install steps no longer require GTK/WebKit packages.
  - `cargo clippy --workspace --all-features --all-targets -- -D warnings`
    remains green.
- `Validation`: `cargo test --workspace --all-targets`, `cargo tree -i glib
  --locked --target all`, `cargo tree -i gtk --locked --target all`, `git diff
  --check`
- `Implementation owner`: `tachi-desktop`
- `Stage label`: Stage 3
- `Next test seam`: `crates/tachi-core/tests/scaffold_dependency_floors.rs`
- `Priority`: 0
- `Notes`: This is the publish gate for the active desktop host change.

### DT-GUI-007 task beads

- `DT-GUI-007.1` Switch workspace membership to the GUI host
  - Acceptance: the workspace lists `tachi-desktop` as the active desktop crate.
- `DT-GUI-007.2` Remove GTK/WebKit install requirements from CI
  - Acceptance: workflow install steps no longer require GTK/WebKit packages.
- `DT-GUI-007.3` Prove GTK-free dependency resolution
  - Acceptance: tree queries return no active GTK/glib path for the workspace.

### DT-GUI-008 - Docs and backlog synchronization

- `Epic`: GTK-Free Desktop GUI Host
- `Feature`: Workspace hardening
- `Capability`: public docs describe the actual desktop host
- `Task`: update BOM, publish checklist, roadmap, and backlog so the active host
  is `crates/tachi-desktop` and `src-tauri` is transitional-only
- `Function`: `docs/bill-of-materials.html.md`, `docs/publish-readiness-checklist.html.md`,
  `docs/roadmap/implementation-backlog.md`
- `Dependencies`: DT-GUI-007
- `Acceptance criteria`:
  - The public docs name `crates/tachi-desktop` as the active host consistently.
  - `src-tauri` is described as transitional/history-only everywhere the active
    host is named.
  - The active roadmap/backlog surfaces include the GUI host plan and issue cards.
- `Validation`: markdown diff review, doc tests if present, `rg` checks for host
  wording consistency
- `Implementation owner`: `docs`
- `Stage label`: Stage 3
- `Next test seam`: `docs/roadmap/implementation-backlog.md`
- `Priority`: 1
- `Notes`: This is the discovery and traceability layer for the new host.

### DT-GUI-008 task beads

- `DT-GUI-008.1` Update BOM and publish checklist host wording
  - Acceptance: both docs describe the native GUI host as active and Tauri as
    transitional.
- `DT-GUI-008.2` Add the GUI host roadmap and issue cards to the backlog hub
  - Acceptance: the backlog points to the GUI host plan as an active execution
    surface.

### DT-GUI-009 - Transitional Tauri adapter sunset

- `Epic`: GTK-Free Desktop GUI Host
- `Feature`: Workspace hardening
- `Capability`: legacy adapter remains only as compatibility evidence
- `Task`: remove the old Tauri adapter from the active path once GUI parity and
  workspace hardening are proven
- `Function`: `src-tauri/`, `crates/tachi-desktop/`
- `Dependencies`: DT-GUI-007, DT-GUI-008
- `Acceptance criteria`:
  - `src-tauri` is no longer referenced as the active desktop host anywhere in
    the workspace contract.
  - Remaining `src-tauri` references are historical/transitional only.
  - The GUI host is the default launch path for the desktop app.
  - No active workflow depends on Tauri runtime packages.
- `Validation`: full workspace test pass, doc grep for active-host wording,
  release-readiness checklist review
- `Implementation owner`: `tachi-desktop`
- `Stage label`: Stage 3
- `Next test seam`: `src-tauri/src/lib.rs`
- `Priority`: 2
- `Notes`: Keep the legacy adapter until parity and hardening are complete.

### DT-GUI-009 task beads

- `DT-GUI-009.1` Remove active-host references to src-tauri
  - Acceptance: the workspace contract no longer names `src-tauri` as active
    desktop host.
- `DT-GUI-009.2` Retire Tauri runtime dependency from active path
  - Acceptance: no active workflow requires Tauri runtime packages.

## Traceability

| Issue | Stage | Rank | Measurable outcome | Trace proof |
|---|---|---:|---|---|
| DT-GUI-001 | Stage 0 | P0 | Native window launches with repo-root state | `cargo run -p tachi-desktop`; `cargo test -p tachi-desktop --all-targets` |
| DT-GUI-002 | Stage 0 | P0 | GUI catalog equals shared registry | `cargo test -p tachi-desktop --test host_parity` |
| DT-GUI-003 | Stage 1 | P1 | GUI command output matches shared dispatch | `cargo test -p tachi-desktop --test host_parity` |
| DT-GUI-004 | Stage 1 | P1 | Cancel returns `130` and emits cancelled event | progress/cancellation fixture tests |
| DT-GUI-005 | Stage 2 | P1 | Artifact bytes identical for preview/save | byte-level artifact comparison |
| DT-GUI-006 | Stage 2 | P2 | Visible, stable command result UX | GUI smoke/manual checklist |
| DT-GUI-007 | Stage 3 | P0 | No GTK/Wry in active workspace path | `cargo tree -i glib --locked --target all`; `cargo tree -i gtk --locked --target all` |
| DT-GUI-008 | Stage 3 | P1 | Docs/backlog point to active host | doc wording assertions |
| DT-GUI-009 | Stage 3 | P2 | `src-tauri` becomes transitional-only | workspace/docs no longer depend on it as active host |

## Assumptions

- `eframe/egui` is the default GUI host stack unless a concrete build constraint
  forces a narrower `winit`-only approach.
- No webview, JS bridge, or Tauri plugin parity is required for the desktop GUI
  target.
- `tachi-shell` remains the sole source of command semantics.
- `src-tauri` stays in the repo as transitional compatibility evidence until the
  GUI host parity and hardening gates are complete.
