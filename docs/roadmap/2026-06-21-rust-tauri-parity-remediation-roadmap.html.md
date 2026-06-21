# Rust/Tauri Parity Remediation Roadmap

Status: active execution roadmap

Scope: Rust and Tauri only. No Python runtime path, no shell-script fallback
in release or desktop flows, and no active CI edits in this roadmap.

This roadmap is the forward-looking parity and supersession track for the
`tachi-rust` repository against the sibling `tachi` repository at
`/Volumes/dev/Git-SCM/tachi`.

The docs-only DOC-00X plan remains separate under the archived docs sweep
roadmap. Do not fold documentation hygiene work into this roadmap.

## Objective

Re-establish parity against `tachi` using only Rust and Tauri capabilities,
lock the parity behavior with tests, and then exceed `tachi` with native
desktop and release features that do not depend on Python.

## Current boundary

- The earlier parity slices RT-010 through RT-023 are complete and remain
  closed.
- This roadmap starts where the prior parity track ended: rebaselining,
  revalidating, and then pushing beyond parity.
- If the sibling `tachi` repository has drifted, the first phase will surface
  the gap before any implementation work begins.

## Current critical gaps

1. The parity baseline against the sibling repository needs a fresh inventory.
2. Command surface, fixture, and schema regressions need a drift-proof harness.
3. The post-parity supercession path needs explicit TDD slices before work
   starts on new desktop-only capabilities.

## Working rules

1. Every phase ships with failing tests first.
2. Every issue maps to a Beads card with a concrete validation seam.
3. Every command/output contract gets a fixture or regression test.
4. Keep the implementation Rust/Tauri-only at every step.
5. Treat completed roadmap docs as archived snapshots, not active scope.

## Phase 0 - parity rebaseline

Goal: re-derive the capability matrix from the sibling `tachi` repository and
confirm what still differs before touching code.

### RT-024 - sibling capability matrix

- Epic: parity rebaseline
- Capability: authoritative capability inventory
- Feature: cross-repo comparison matrix
- Task: capture the supported command, output, bridge, and release surfaces
  from `tachi` and compare them to `tachi-rust`
- Acceptance criteria:
  - The inventory names every current surface that matters for parity.
  - The matrix distinguishes exact matches from tolerated differences.
  - The matrix becomes the source for all parity follow-up cards.
- Validation:
  - A deterministic inventory artifact is generated and reviewed.
  - The comparison can be re-run without manual cleanup.
- Implementation owner: `docs`
- Stage label: Phase 0
- Next test seam: `docs/roadmap/`
- Notes: This is a parity discovery card, not a code change.

Exit gate:

- parity gaps are named, not assumed
- no implementation slice starts until the inventory is explicit

## Phase 1 - critical parity closure

Goal: close any high-severity drift between the sibling repo and the Rust/Tauri
implementation, using TDD for each slice.

### RT-025 - command surface drift harness

- Epic: parity closure
- Capability: executable surface inventory
- Feature: CLI/Tauri registry diff
- Task: add a red/green harness that fails when the supported command surfaces
  diverge from the parity baseline
- Acceptance criteria:
  - Registry diff fails red when a command exists on one surface and not the
    other.
  - Diff output is deterministic and snapshot-friendly.
- Validation:
  - Registry diff tests and bridge parity tests remain green.
- Implementation owner: `tachi-shell`
- Stage label: Phase 1
- Next test seam: `crates/tachi-shell/src/commands.rs`
- Notes: Use the inventory from RT-024 as the expected surface.

### RT-026 - canonical fixture corpus

- Epic: parity closure
- Capability: behavior capture
- Feature: versioned fixtures for command I/O
- Task: define canonical fixtures for command inputs, command outputs, and
  response hashes
- Acceptance criteria:
  - Fixtures include schema version, command name, and stable response hashes.
  - Malformed or version-skewed fixtures fail fast.
- Validation:
  - Schema validation tests and round-trip tests remain stable.
- Implementation owner: `tachi-core`
- Stage label: Phase 1
- Next test seam: `tests/fixtures/`
- Notes: The corpus should be reusable for both CLI and Tauri capture paths.

### RT-027 - typed desktop bridge guards

- Epic: parity closure
- Capability: typed invocation
- Feature: schema-validated desktop bridge
- Task: validate Tauri inputs and outputs against typed schemas before command
  execution
- Acceptance criteria:
  - Invalid payloads fail before the command body runs.
  - Schema drift is caught by tests.
- Validation:
  - Bridge tests cover valid payloads, invalid payloads, and schema drift.
- Implementation owner: `src-tauri`
- Stage label: Phase 1
- Next test seam: `src-tauri/src/lib.rs`
- Notes: Keep the bridge logic narrow; no new runtime behavior in this slice.

Exit gate:

- registry parity is proven by tests
- fixture and schema regressions fail red before merge
- no bridge path depends on Python or shell-script fallback behavior

## Phase 2 - output and release parity

Goal: prove the Rust output and packaging story is reproducible and stable.

### RT-028 - release artifact parity

- Epic: distribution hardening
- Capability: reproducible packaging
- Feature: checksums and manifest consistency
- Task: generate and verify release manifests, checksums, and platform
  packaging outputs
- Acceptance criteria:
  - Artifacts are reproducible for identical inputs.
  - CI verifies the release manifest and checksums.
- Validation:
  - Release checks run on the supported platforms.
- Implementation owner: `docs`
- Stage label: Phase 2
- Next test seam: `docs/bill-of-materials.html.md`
- Notes: This is a parity lock, not a packaging experiment.

Exit gate:

- output and artifact hashes are stable
- release docs match the implemented packaging flow

## Phase 3 - supercede `tachi`

Goal: add Rust/Tauri-native capabilities that make the desktop experience
strictly better than the sibling repository.

### RT-029 - progress telemetry and cancellation

- Epic: desktop UX
- Capability: long-running command control
- Feature: progress events and cancellation
- Task: add cancellable async invokes with visible progress updates
- Acceptance criteria:
  - Long-running commands can be cancelled without corrupting state.
  - Progress events are visible to desktop callers.
- Validation:
  - Desktop integration test covers progress and cancel.
- Implementation owner: `src-tauri`
- Stage label: Phase 3
- Next test seam: `src-tauri/src/commands.rs`
- Notes: Only start after the parity harness remains green.

### RT-030 - offline bootstrap and update awareness

- Epic: desktop UX
- Capability: resilience
- Feature: cached bootstrap and update probe
- Task: support offline artifact cache restore and update checks
- Acceptance criteria:
  - The app can recover from offline startup with cached data.
  - Update probing does not block the offline path.
- Validation:
  - Smoke test covers cold start, cache restore, and update probe paths.
- Implementation owner: `src-tauri`
- Stage label: Phase 3
- Next test seam: `src-tauri/src/lib.rs`
- Notes: Keep the offline path deterministic and test-first.

Exit gate:

- parity remains intact while native features are added
- new UX slices are covered by tests before merge
- no regression in the release gates

## Beads issue tracker mapping

Use the following structure when creating Beads cards:

| Field | Value |
| --- | --- |
| Tracker | Beads |
| Program | `tachi-rust` Rust/Tauri parity and supersession |
| Priority | parity first, then native supercession |
| Definition of done | tests green, fixtures committed, docs updated |

The Beads-ready issue set lives in
[2026-06-21-rust-tauri-parity-issue-cards.md](./2026-06-21-rust-tauri-parity-issue-cards.md).
