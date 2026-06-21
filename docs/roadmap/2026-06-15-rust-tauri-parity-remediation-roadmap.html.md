# Rust/Tauri Parity Remediation Roadmap

Status: active execution roadmap

Scope: Rust and Tauri only. No Python runtime path, no Python bridge,
no legacy script execution in release or desktop flows.

This roadmap supersedes the completed `2026-06-04` issue pack and the
`2026-06-08` migration roadmap. Keep those files as archive records only.

## Objective

Reach feature parity with `tachi`, then exceed it with Rust/Tauri-only
desktop and release capabilities.

The first phase is strict parity. Do not introduce new differentiators
until the critical gaps are closed and proven with tests.

## Current critical gaps

1. Desktop command surface parity is incomplete.
2. Output contracts still need canonical golden-fixture proof across
   the major command families.
3. Deterministic serialization and normalization rules still need a
   shared test harness.

## Resolved in repo

- Command registry diff harness RT-010 is implemented and validated.
- Parser regression coverage RT-016 is implemented and validated.
- CI and release hardening RT-017, RT-018, RT-021, and RT-022 are
  implemented and validated.
- Desktop UX slices RT-019 and RT-020 are implemented and validated.

## Working rules

1. Every phase ships with failing tests first.
2. Every issue maps to a Beads card with a clear acceptance gate.
3. Every command/output contract gets a fixture or regression test.
4. Keep the implementation Rust/Tauri-only at every step.
5. Treat completed roadmap docs as archived snapshots, not active scope.

## Phase 0 - parity harness

Goal: create the measurement layer before changing behavior.

### RT-010 - command registry diff harness

- Epic: parity foundation
- Capability: executable surface inventory
- Feature: command registry comparison
- Task: add a test that enumerates CLI and Tauri command surfaces and
  fails on drift
- Acceptance: registry diff fails red when a command exists in one
  surface and not the other
- Validation: `cargo test` for the registry diff case

### RT-011 - schema and fixture contract

- Epic: parity foundation
- Capability: behavior capture
- Feature: versioned fixture schema
- Task: define canonical JSON fixtures for command input and output
- Acceptance: fixtures include schema version, command name, and stable
  hashes for response payloads
- Validation: unit tests reject malformed or version-skewed fixtures

### RT-012 - deterministic normalization helper

- Epic: parity foundation
- Capability: stable output
- Feature: canonical sort and trim rules
- Task: centralize normalization for ordering, casing, whitespace, and
  null handling
- Acceptance: all normalization paths use one helper and the helper has
  direct tests
- Validation: golden tests show identical output across repeated runs

Exit gate:

- `cargo test -q`
- `cargo clippy --all-targets -- -D warnings`
- fixture-based tests for the core command set

## Phase 1 - critical parity closure

Goal: make Tauri expose the same command surface and validation rules as
the CLI.

### RT-013 - Tauri command allowlist parity

- Epic: desktop parity
- Capability: command invocation
- Feature: full command registration
- Task: expose every supported CLI command through the Tauri bridge
- Acceptance: desktop registry matches CLI registry for supported
  commands
- Validation: integration test invokes each command through Tauri

### RT-014 - desktop invoke contract validation

- Epic: desktop parity
- Capability: typed invocation
- Feature: schema-validated bridge
- Task: validate Tauri inputs and outputs against typed schemas
- Acceptance: invalid payloads fail before command execution begins
- Validation: bridge tests cover good payloads, bad payloads, and
  schema drift

Exit gate:

- desktop integration tests pass
- CLI and Tauri command names are aligned
- no bridge path depends on Python or shell-script fallback behavior

## Phase 2 - output contract parity

Goal: prove that the Rust implementation matches the legacy behavior for
the important command families.

### RT-015 - reporting goldens

- Epic: behavioral parity
- Capability: reports and exports
- Feature: stable fixtures for reporting commands
- Task: capture goldens for report, threat, risk, coverage, and
  infographic outputs
- Acceptance: fixtures cover the primary command families and the edge
  cases that previously drifted
- Validation: snapshot tests compare against canonical fixtures

### RT-016 - parser regression suite

- Epic: behavioral parity
- Capability: input normalization
- Feature: regression cases for status parsing and field cleanup
- Task: add tests for whitespace, casing, unknown values, and malformed
  records
- Acceptance: parser regressions are red before the fix and green after
- Validation: targeted parser tests remain stable over time

Exit gate:

- output hashes are stable
- no unreviewed formatting drift in command output
- fixture updates require explicit review

## Phase 3 - CI and release hardening

Goal: remove workflow drift and make releases reproducible.

### RT-017 - checkout action cleanup

- Epic: CI modernization
- Capability: workflow hygiene
- Feature: GitHub Actions version parity
- Task: move every repository checkout step to `actions/checkout@v6`
- Acceptance: no workflow file references `@v4`
- Validation: workflow lint or text scan fails on version drift

### RT-018 - release artifact parity

- Epic: distribution hardening
- Capability: reproducible packaging
- Feature: checksums and manifest consistency
- Task: generate and verify release manifests, checksums, and platform
  packaging outputs
- Acceptance: artifacts are identical for identical inputs and verified
  in CI
- Validation: release checks run on all supported platforms

### RT-021 - docs-only release-please filter

- Epic: CI modernization
- Capability: workflow hygiene
- Feature: docs-only release safety
- Task: skip release-please on docs-only and roadmap-only pushes so
  documentation publishes do not churn release refs
- Acceptance: docs-only pushes to `main` do not invoke release-please
- Validation: main-push smoke check after docs-only changes

### RT-022 - release-please no PR branch updates

- Epic: CI modernization
- Capability: release automation stability
- Feature: release-please push safety
- Task: keep `release-please` from updating its PR branch on push so the
  main-push workflow cannot fail on stale release refs
- Acceptance: release-please no longer attempts PR branch updates on push
- Validation: latest main-push release-please run succeeds
- Notes: Implemented in `feat/release-please-no-pr-creation`; validated on code push

Exit gate:

- workflow version drift is removed
- release artifacts are reproducible
- workflow and packaging docs agree with the code path
- `make publish-gate` enforces workflow drift plus release artifact parity

## Phase 4 - exceed `tachi`

Goal: only after parity is proven, add Rust/Tauri-native advantages.

### RT-019 - progress and cancel support

- Epic: desktop UX
- Capability: long-running command control
- Feature: progress events and cancellation
- Task: add cancellable async invokes with visible progress updates
- Acceptance: long-running commands can be cancelled without corrupting
  state
- Validation: desktop integration test covers progress and cancel
- Notes: Implemented in `feat/rt019-progress-cancel-support`; ready for merge

### RT-020 - offline bootstrap and update checks

- Epic: desktop UX
- Capability: resilience
- Feature: cached bootstrap and update awareness
- Task: support offline artifact cache restore and update checks
- Acceptance: app can recover from offline startup with cached data
- Validation: smoke test covers cold start, cache restore, and update
  probe paths
- Notes: Implemented in `feat/rt020-offline-bootstrap-cache`; ready for merge

Exit gate:

- parity remains intact
- new UX features are covered by tests
- no regression in the release gates

## Beads issue tracker mapping

Use the following structure when creating Beads cards:

| Field | Value |
| --- | --- |
| Tracker | Beads |
| Program | `tachi-rust` Rust/Tauri-only remediation |
| Priority | parity first, differentiation second |
| Definition of done | tests green, fixtures committed, docs updated |

The Beads-ready issue set lives in
[2026-06-15-rust-tauri-parity-issue-cards.md](./2026-06-15-rust-tauri-parity-issue-cards.md).

## Roadmap cleanup policy

These docs are archived and should not receive new work items:

- `docs/roadmap/2026-06-04-rust-tauri-issue-pack.md`
- `docs/roadmap/2026-06-08-rust-tauri-only-roadmap.md`

The living index remains `docs/roadmap/implementation-backlog.md`, but
it should point at this file for active execution.
