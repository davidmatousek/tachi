# Rust/Tauri Parity Issue Cards

**Last Updated**: 2026-06-15
**Status**: Beads-ready execution backlog for the active parity roadmap
**Source**: [2026-06-15-rust-tauri-parity-remediation-roadmap.html.md](./2026-06-15-rust-tauri-parity-remediation-roadmap.html.md)

These cards are the task-sized execution slices for the active parity roadmap in
[implementation-backlog.md](./implementation-backlog.md). Copy them into Beads
as-is or with only implementation-owner routing changes.

## Card Format

Every card includes:

- `Epic`
- `Capability`
- `Task`
- `Function`
- `Dependencies`
- `Acceptance criteria`
- `Validation`
- `Implementation owner`
- `Stage label`
- `Next test seam`
- `Notes`

## Phase 0 - parity harness

### RT-010 - command registry diff harness

- `Epic`: Phase 0 - parity harness
- `Capability`: executable surface inventory
- `Task`: add a failing test that enumerates CLI and Tauri command surfaces and
  fails on drift
- `Function`: `collect_cli_commands`, `collect_tauri_commands`, `diff_registry`
- `Dependencies`: active roadmap, command registration fixtures
- `Acceptance criteria`:
  - Registry diff fails red when a command exists in one surface and not the other.
  - Output is deterministic and easy to snapshot.
- `Validation`:
  - Unit tests for the diff helper.
  - Integration test for the full registry comparison.
- `Implementation owner`: `tachi-shell`
- `Stage label`: Phase 0
- `Next test seam`: `crates/tachi-shell/src/commands.rs`
- `Notes`: Keep the harness small enough to run on every PR.

### RT-011 - schema and fixture contract

- `Epic`: Phase 0 - parity harness
- `Capability`: behavior capture
- `Task`: define canonical JSON fixtures for command input and output
- `Function`: `serialize_fixture`, `hash_fixture_payload`, `validate_fixture_schema`
- `Dependencies`: RT-010
- `Acceptance criteria`:
  - Fixtures include schema version, command name, and stable response hashes.
  - Malformed or version-skewed fixtures fail fast.
- `Validation`:
  - Schema validation tests.
  - Round-trip fixture tests.
- `Implementation owner`: `tachi-core`
- `Stage label`: Phase 0
- `Next test seam`: `tests/fixtures/`
- `Notes`: Use the same schema for CLI and Tauri capture.

### RT-012 - deterministic normalization helper

- `Epic`: Phase 0 - parity harness
- `Capability`: stable output
- `Task`: centralize normalization for ordering, casing, whitespace, and null handling
- `Function`: `normalize_value`, `stable_sort_map`, `stable_trim_text`
- `Dependencies`: RT-011
- `Acceptance criteria`:
  - All normalization code paths use one helper.
  - Repeated runs produce identical output.
- `Validation`:
  - Direct unit tests for normalization rules.
  - Golden tests for command output stability.
- `Implementation owner`: `tachi-core`
- `Stage label`: Phase 0
- `Next test seam`: `crates/tachi-core/src/parsers/findings.rs`
- `Notes`: Do not duplicate normalization in command code.

## Phase 1 - critical parity closure

### RT-013 - Tauri command allowlist parity

- `Epic`: Phase 1 - critical parity closure
- `Capability`: command invocation
- `Task`: expose every supported CLI command through the Tauri bridge
- `Function`: `register_commands`, `dispatch_desktop_command`, `dispatch_shared_command`
- `Dependencies`: RT-010, RT-012
- `Acceptance criteria`:
  - Desktop registry matches CLI registry for supported commands.
  - Missing commands fail the test suite before merge.
- `Validation`:
  - Desktop integration tests invoke each command through Tauri.
  - Registry comparison test stays green.
- `Implementation owner`: `src-tauri`
- `Stage label`: Phase 1
- `Next test seam`: `src-tauri/src/lib.rs`
- `Notes`: Keep the bridge thin and command-only.

### RT-014 - desktop invoke contract validation

- `Epic`: Phase 1 - critical parity closure
- `Capability`: typed invocation
- `Task`: validate Tauri inputs and outputs against typed schemas
- `Function`: `validate_invoke_input`, `validate_invoke_output`, `render_schema_error`
- `Dependencies`: RT-011, RT-013
- `Acceptance criteria`:
  - Invalid payloads fail before command execution begins.
  - Schema drift is caught by tests.
- `Validation`:
  - Bridge tests for valid payloads, invalid payloads, and schema drift.
- `Implementation owner`: `src-tauri`
- `Stage label`: Phase 1
- `Next test seam`: `src-tauri/src/commands.rs`
- `Notes`: Preserve the same error shape for CLI and desktop callers.

## Phase 2 - output contract parity

### RT-015 - reporting goldens

- `Epic`: Phase 2 - output contract parity
- `Capability`: reports and exports
- `Task`: capture goldens for report, threat, risk, coverage, and infographic outputs
- `Function`: `emit_report_fixture`, `emit_threat_fixture`, `emit_risk_fixture`
- `Dependencies`: RT-012
- `Acceptance criteria`:
  - Fixtures cover the primary command families and known edge cases.
  - Canonical outputs remain stable until intentionally revised.
- `Validation`:
  - Snapshot tests compare against canonical fixtures.
- `Implementation owner`: `tachi-core`
- `Stage label`: Phase 2
- `Next test seam`: `crates/tachi-core/tests/`
- `Notes`: Freeze ordering before snapshotting.

### RT-016 - parser regression suite

- `Epic`: Phase 2 - output contract parity
- `Capability`: input normalization
- `Task`: add tests for whitespace, casing, unknown values, and malformed records
- `Function`: `compute_delta_counts`, `normalize_status`, `ignore_unknown_status`
- `Dependencies`: RT-012
- `Acceptance criteria`:
  - Parser regressions fail red before the fix and green after.
  - Unknown or malformed records do not panic.
- `Validation`:
  - Targeted parser tests remain stable over time.
- `Implementation owner`: `tachi-core`
- `Stage label`: Phase 2
- `Next test seam`: `crates/tachi-core/src/parsers/`
- `Notes`: Keep the regression set small but representative.

## Phase 3 - CI and release hardening

### RT-017 - checkout action cleanup

- `Epic`: Phase 3 - CI and release hardening
- `Capability`: workflow hygiene
- `Task`: move every repository checkout step to `actions/checkout@v6`
- `Function`: `.github/workflows/*`
- `Dependencies`: RT-010 through RT-016
- `Acceptance criteria`:
  - No workflow file references `@v4`.
  - Workflow lint fails on version drift.
- `Validation`:
  - Text scan or workflow lint gate.
- `Implementation owner`: `docs`
- `Stage label`: Phase 3
- `Next test seam`: `.github/workflows/`
- `Notes`: Treat workflow version drift as a publish blocker.

### RT-018 - release artifact parity

- `Epic`: Phase 3 - CI and release hardening
- `Capability`: reproducible packaging
- `Task`: generate and verify release manifests, checksums, and platform packaging outputs
- `Function`: `build_release_manifest`, `verify_checksum_matrix`, `validate_package_contents`
- `Dependencies`: RT-017
- `Acceptance criteria`:
  - Artifacts are reproducible for identical inputs.
  - CI verifies the release manifest and checksums.
- `Validation`:
  - Release checks run on supported platforms.
- `Implementation owner`: `docs`
- `Stage label`: Phase 3
- `Next test seam`: `docs/bill-of-materials.html.md`
- `Notes`: Keep the BOM in sync with the release inventory.

## Phase 4 - exceed `tachi`

### RT-019 - progress and cancel support

- `Epic`: Phase 4 - exceed `tachi`
- `Capability`: long-running command control
- `Task`: add cancellable async invokes with visible progress updates
- `Function`: `invoke_with_progress`, `cancel_running_command`, `emit_progress_event`
- `Dependencies`: RT-013, RT-014
- `Acceptance criteria`:
  - Long-running commands can be cancelled without corrupting state.
  - Progress events are visible to desktop callers.
- `Validation`:
  - Desktop integration test covers progress and cancel.
- `Implementation owner`: `src-tauri`
- `Stage label`: Phase 4
- `Next test seam`: `src-tauri/src/commands.rs`
- `Notes`: Add this only after parity tests are green.

### RT-020 - offline bootstrap and update checks

- `Epic`: Phase 4 - exceed `tachi`
- `Capability`: resilience
- `Task`: support offline artifact cache restore and update checks
- `Function`: `restore_offline_cache`, `check_for_update`, `bootstrap_from_cache`
- `Dependencies`: RT-018
- `Acceptance criteria`:
  - App can recover from offline startup with cached data.
  - Update probing does not block the offline path.
- `Validation`:
  - Smoke test covers cold start, cache restore, and update probe paths.
- `Implementation owner`: `src-tauri`
- `Stage label`: Phase 4
- `Next test seam`: `src-tauri/src/lib.rs`
- `Notes`: Add only after release hardening is stable.
