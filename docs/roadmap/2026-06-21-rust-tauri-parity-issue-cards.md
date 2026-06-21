# Rust/Tauri Parity Issue Cards

**Last Updated**: 2026-06-21
**Status**: Beads-ready execution backlog for the active parity/supersession roadmap
**Source**: [2026-06-21-rust-tauri-parity-remediation-roadmap.html.md](./2026-06-21-rust-tauri-parity-remediation-roadmap.html.md)

These cards are the task-sized execution slices for the active parity roadmap.
Copy them into Beads as-is or with only implementation-owner routing changes.

## Current Status Snapshot

- Open: RT-024, RT-025, RT-026, RT-027, RT-028, RT-029, RT-030
- Partial: none
- Done: RT-010, RT-011, RT-012, RT-013, RT-014, RT-015, RT-016, RT-017, RT-018, RT-019, RT-020, RT-021, RT-022, RT-023

## Phase 0 - parity rebaseline

### RT-024 - sibling capability matrix

- `Epic`: parity rebaseline
- `Capability`: authoritative capability inventory
- `Task`: capture the supported command, output, bridge, and release surfaces
  from `tachi` and compare them to `tachi-rust`
- `Function`: inventory generator, cross-repo diff report
- `Dependencies`: sibling `tachi` repository snapshot, active parity roadmap
- `Acceptance criteria`:
  - Inventory names every current surface that matters for parity.
  - The matrix distinguishes exact matches from tolerated differences.
  - The matrix becomes the source for all parity follow-up cards.
- `Validation`:
  - Deterministic inventory artifact is generated and reviewed.
- `Implementation owner`: `docs`
- `Stage label`: Phase 0
- `Next test seam`: `docs/roadmap/`
- `Notes`: Discovery first; no code changes in this slice.

## Phase 1 - critical parity closure

### RT-025 - command surface drift harness

- `Epic`: parity closure
- `Capability`: executable surface inventory
- `Task`: add a red/green harness that fails when supported command surfaces
  diverge from the parity baseline
- `Function`: `collect_cli_commands`, `collect_tauri_commands`, `diff_registry`
- `Dependencies`: RT-024
- `Acceptance criteria`:
  - Registry diff fails red when a command exists on one surface and not the other.
  - Diff output is deterministic and snapshot-friendly.
- `Validation`:
  - Registry diff tests and bridge parity tests remain green.
- `Implementation owner`: `tachi-shell`
- `Stage label`: Phase 1
- `Next test seam`: `crates/tachi-shell/src/commands.rs`
- `Notes`: Use the RT-024 inventory as the expected surface.

### RT-026 - canonical fixture corpus

- `Epic`: parity closure
- `Capability`: behavior capture
- `Task`: define canonical fixtures for command inputs, command outputs, and
  response hashes
- `Function`: `serialize_fixture`, `hash_fixture_payload`, `validate_fixture_schema`
- `Dependencies`: RT-024
- `Acceptance criteria`:
  - Fixtures include schema version, command name, and stable response hashes.
  - Malformed or version-skewed fixtures fail fast.
- `Validation`:
  - Schema validation tests and round-trip tests remain stable.
- `Implementation owner`: `tachi-core`
- `Stage label`: Phase 1
- `Next test seam`: `tests/fixtures/`
- `Notes`: Reusable for both CLI and Tauri capture paths.

### RT-027 - typed desktop bridge guards

- `Epic`: parity closure
- `Capability`: typed invocation
- `Task`: validate Tauri inputs and outputs against typed schemas before command
  execution
- `Function`: `validate_invoke_input`, `validate_invoke_output`, `render_schema_error`
- `Dependencies`: RT-026
- `Acceptance criteria`:
  - Invalid payloads fail before the command body runs.
  - Schema drift is caught by tests.
- `Validation`:
  - Bridge tests cover valid payloads, invalid payloads, and schema drift.
- `Implementation owner`: `src-tauri`
- `Stage label`: Phase 1
- `Next test seam`: `src-tauri/src/lib.rs`
- `Notes`: Keep the bridge logic narrow.

## Phase 2 - output and release parity

### RT-028 - release artifact parity

- `Epic`: distribution hardening
- `Capability`: reproducible packaging
- `Task`: generate and verify release manifests, checksums, and platform
  packaging outputs
- `Function`: `build_release_manifest`, `verify_checksum_matrix`, `validate_package_contents`
- `Dependencies`: RT-025, RT-026, RT-027
- `Acceptance criteria`:
  - Artifacts are reproducible for identical inputs.
  - CI verifies the release manifest and checksums.
- `Validation`:
  - Release checks run on the supported platforms.
- `Implementation owner`: `docs`
- `Stage label`: Phase 2
- `Next test seam`: `docs/bill-of-materials.html.md`
- `Notes`: This is a parity lock, not a packaging experiment.

## Phase 3 - supercede `tachi`

### RT-029 - progress telemetry and cancellation

- `Epic`: desktop UX
- `Capability`: long-running command control
- `Task`: add cancellable async invokes with visible progress updates
- `Function`: `invoke_with_progress`, `cancel_running_command`, `emit_progress_event`
- `Dependencies`: RT-027
- `Acceptance criteria`:
  - Long-running commands can be cancelled without corrupting state.
  - Progress events are visible to desktop callers.
- `Validation`:
  - Desktop integration test covers progress and cancel.
- `Implementation owner`: `src-tauri`
- `Stage label`: Phase 3
- `Next test seam`: `src-tauri/src/commands.rs`
- `Notes`: Only start after the parity harness stays green.

### RT-030 - offline bootstrap and update awareness

- `Epic`: desktop UX
- `Capability`: resilience
- `Task`: support offline artifact cache restore and update checks
- `Function`: `restore_offline_cache`, `check_for_update`, `bootstrap_from_cache`
- `Dependencies`: RT-028
- `Acceptance criteria`:
  - The app can recover from offline startup with cached data.
  - Update probing does not block the offline path.
- `Validation`:
  - Smoke test covers cold start, cache restore, and update probe paths.
- `Implementation owner`: `src-tauri`
- `Stage label`: Phase 3
- `Next test seam`: `src-tauri/src/lib.rs`
- `Notes`: Keep the offline path deterministic and test-first.
