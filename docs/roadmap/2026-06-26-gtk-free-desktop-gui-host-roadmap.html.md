# GTK-Free Desktop GUI Host Roadmap

**Date**: 2026-06-26
**Scope**: native desktop GUI host for `tachi-rust` without GTK/Wry in the
active workspace dependency tree
**Execution model**: TDD-first, Beads issue graph, stage-gated parity checks
**Status**: active planning roadmap
**Source context**: `crates/tachi-desktop/`, `crates/tachi-shell/src/commands.rs`,
`crates/tachi-shell/src/tauri_bridge.rs`, `docs/roadmap/implementation-backlog.md`,
`docs/bill-of-materials.html.md`, `docs/publish-readiness-checklist.html.md`

## Executive summary

The active desktop plan is to turn `crates/tachi-desktop` into the primary
native GUI host, with `tachi-shell` remaining the single source of command
behavior, validation, and artifact semantics.

The GUI host must be Rust-native end to end. It may use a `winit`-based stack
such as `eframe/egui`, but it must not rely on webview, Tauri, or GTK/Wry in
the active workspace path.

## Design goals

- Preserve the existing shared command contract exactly.
- Keep output shapes, artifact filenames, and path policy unchanged.
- Add a native desktop UI that can run, cancel, and preview commands without
  duplicating command logic.
- Remove GTK/Wry from the active workspace dependency tree and keep `src-tauri`
  transitional-only.

## Logical stages

### Stage 0 - Native shell bootstrap

**Goal**: make `tachi-desktop` a runnable native app with repository context and
a minimal command catalog view.

**Measured outcome**

- `cargo run -p tachi-desktop` opens a native window.
- The window shows the selected repository root and the shared command list.
- No GTK/Wry dependency is required for the active workspace path.

### Stage 1 - Shared command parity

**Goal**: expose the shared command catalog and command dispatch surface through
the GUI host without duplicating command semantics.

**Measured outcome**

- GUI command names match the shared registry exactly.
- Representative commands return the same outputs as direct shared dispatch.
- Progress and cancellation semantics behave the same in the GUI and shell
  harnesses.

### Stage 2 - Artifact workflows

**Goal**: let the GUI preview and save the same artifacts that the shell
already produces.

**Measured outcome**

- `report-data`, `infographic-data`, `threats-sarif`, and `risk-scores-sarif`
  can be previewed or written to disk from the GUI.
- Saved artifacts match the command output byte-for-byte.
- Path containment and failure handling remain unchanged.

### Stage 3 - Workspace hardening

**Goal**: make the GUI host the active workspace desktop path and document the
transition away from Tauri.

**Measured outcome**

- Workspace membership, CI, BOM, and publish checks all reference
  `crates/tachi-desktop` as the active host.
- `cargo tree -i glib --locked --target all` and `cargo tree -i gtk --locked
  --target all` return no active workspace path.
- `src-tauri` is clearly marked transitional-only in docs.

## Sequencing

1. Freeze the native shell and command-catalog contract first.
2. Add command parity next, then progress/cancel handling.
3. Add artifact preview/save flows after command parity is stable.
4. Update workspace membership, docs, and CI only after the GUI host passes
   parity.
5. Retire the active Tauri host role last.

## Definition of done

- The GUI host is launchable and useful without Tauri or GTK/Wry.
- The shared shell remains the only command engine.
- All stage cards have explicit Beads acceptance criteria and validation
  commands.
- The roadmap, issue cards, and backlog stay synchronized.
