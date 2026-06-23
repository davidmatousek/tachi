# Adversarial Architecture and Test Quality Issue Cards

**Last Updated**: 2026-06-22
**Status**: Beads-ready execution slices for the 2026-06-22 roadmap
**Source**: [2026-06-22-adversarial-architecture-test-quality-roadmap.html.md](./2026-06-22-adversarial-architecture-test-quality-roadmap.html.md)

These cards are copy-paste-ready Beads issues. Every card is TDD-first:
write or preserve the failing test/gate proof, then implement the smallest
slice that makes it pass.

## Card Format

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
- `Notes`

## Phase 0 - Fail-Closed Quality Gates

### AQ-011 - Workspace behavioral gate

- `Epic`: AQ-001 Architecture and test quality maturity program
- `Feature`: Phase 0 fail-closed quality gates
- `Capability`: AQ-010 fail-closed CI and acceptance gates
- `Task`: keep `cargo test --workspace --all-targets` visible in PR gating and
  fail closed on regressions
- `Function`: `.github/workflows/rust-workspace.yml`, `Makefile publish-gate`
- `Dependencies`: current workflow baseline
- `Acceptance criteria`:
  - Workspace-test failures block merge.
  - The gate is documented in the roadmap and Beads.
  - Targeted workflows cannot pass while the workspace suite is red.
- `Validation`: workflow review, local `make publish-gate`
- `Implementation owner`: `docs`
- `Stage label`: Phase 0
- `Next test seam`: `.github/workflows/rust-workspace.yml`
- `Notes`: Regression-proofing card; the gate already exists.

### AQ-012 - Clippy fail-closed gate

- `Epic`: AQ-001 Architecture and test quality maturity program
- `Feature`: Phase 0 fail-closed quality gates
- `Capability`: AQ-010 fail-closed CI and acceptance gates
- `Task`: keep clippy failures blocking while preserving SARIF upload as a
  diagnostic lane
- `Function`: `.github/workflows/rust-clippy.yml`, `Makefile publish-gate`
- `Dependencies`: current clippy workflow baseline
- `Acceptance criteria`:
  - `cargo clippy --all-targets -- -D warnings` exits non-zero on lint failures.
  - SARIF upload remains best-effort, not a success signal.
- `Validation`: workflow review, `make publish-gate`
- `Implementation owner`: `docs`
- `Stage label`: Phase 0
- `Next test seam`: `.github/workflows/rust-clippy.yml`
- `Notes`: Regression-proofing card; the current workflow already exits on failure.

### AQ-013 - Beads TDD acceptance template

- `Epic`: AQ-001 Architecture and test quality maturity program
- `Feature`: Phase 0 fail-closed quality gates
- `Capability`: Beads task hygiene
- `Task`: standardize the Beads template so every slice names the failing test,
  negative case, and exact local validation command first
- `Function`: `docs/roadmap/implementation-backlog.md`, Beads card template
- `Dependencies`: none
- `Acceptance criteria`:
  - Every new card includes failing-test-first acceptance criteria.
  - Every card names the preferred test seam and negative case.
  - Cards stay small enough to land in one conventional commit.
- `Validation`: manual template review, spot-check against this pack
- `Implementation owner`: `docs`
- `Stage label`: Phase 0
- `Next test seam`: `docs/roadmap/implementation-backlog.md`
- `Notes`: Template rule-set that keeps later phases TDD-first.

## Phase 1 - Tauri and Desktop Security Boundary

### AQ-021 - Least-privilege desktop boundary

- `Epic`: AQ-001 Architecture and test quality maturity program
- `Feature`: Phase 1 Tauri and desktop security boundary
- `Capability`: AQ-020 Tauri least-privilege desktop boundary
- `Task`: keep the desktop shell focused on registration and enforce the
  least-privilege boundary through tests
- `Function`: `src-tauri/src/lib.rs::run`, `src-tauri/tauri.conf.json`,
  `src-tauri/capabilities/main.json`
- `Dependencies`: current Tauri scaffold and capability tests
- `Acceptance criteria`:
  - Desktop commands remain allowlisted.
  - New command exposure is test-backed before merge.
  - The boundary stays registration-only.
- `Validation`: desktop boundary tests, capability-file review
- `Implementation owner`: `src-tauri`
- `Stage label`: Phase 1
- `Next test seam`: `src-tauri/tests/capability_boundary.rs`
- `Notes`: Continue hardening runtime wiring without widening scope.

### AQ-022 - Typed control-plane argument policy

- `Epic`: AQ-001 Architecture and test quality maturity program
- `Feature`: Phase 1 Tauri and desktop security boundary
- `Capability`: AQ-020 typed command invocation policy
- `Task`: derive command-argument validation from a typed control-plane model
  instead of ad hoc string matching
- `Function`: `src-tauri/src/schema.rs`, `src-tauri/tests/schema.rs`
- `Dependencies`: AQ-021
- `Acceptance criteria`:
  - Unknown flags fail before the command body runs.
  - Help text is not treated as an execution payload.
  - Argument policy is shared across callers.
- `Validation`: schema tests for valid, invalid, and help-as-execution payloads
- `Implementation owner`: `src-tauri`
- `Stage label`: Phase 1
- `Next test seam`: `src-tauri/src/schema.rs`
- `Notes`: Preserve typed error mapping while tightening the decode path.

### AQ-023 - Root-contained IO policy

- `Epic`: AQ-001 Architecture and test quality maturity program
- `Feature`: Phase 1 Tauri and desktop security boundary
- `Capability`: AQ-020 root-contained file IO
- `Task`: keep output and cache paths rooted and reject traversal or symlink
  escapes
- `Function`: `crates/tachi-shell/src/tauri_bridge.rs`,
  `src-tauri/src/offline.rs`
- `Dependencies`: AQ-021
- `Acceptance criteria`:
  - Absolute paths and parent traversal are rejected.
  - Symlink escapes do not bypass the root policy.
  - New bridge paths reuse the same containment checks.
- `Validation`: bridge tests for traversal and symlink escapes, offline tests
- `Implementation owner`: `tachi-shell`
- `Stage label`: Phase 1
- `Next test seam`: `crates/tachi-shell/tests/tauri_bridge.rs`
- `Notes`: Existing checks exist; this card keeps them enforced everywhere.

### AQ-024 - Bounded process execution

- `Epic`: AQ-001 Architecture and test quality maturity program
- `Feature`: Phase 1 Tauri and desktop security boundary
- `Capability`: AQ-020 bounded process execution
- `Task`: preserve timeout, cancellation, output caps, and child cleanup as a
  non-regression contract
- `Function`: `crates/tachi-shell/src/commands.rs`,
  `crates/tachi-shell/src/progress.rs`
- `Dependencies`: AQ-021
- `Acceptance criteria`:
  - Long-running commands time out cleanly.
  - Cancelled commands do not leave child processes behind.
  - Output remains capped.
- `Validation`: process lifecycle tests, output-cap regression checks
- `Implementation owner`: `tachi-shell`
- `Stage label`: Phase 1
- `Next test seam`: `crates/tachi-shell/tests/tauri_bridge.rs`
- `Notes`: Preserve the current guardrails when refactoring the executor.

### AQ-025 - Typed error taxonomy

- `Epic`: AQ-001 Architecture and test quality maturity program
- `Feature`: Phase 1 Tauri and desktop security boundary
- `Capability`: AQ-020 typed desktop errors
- `Task`: keep policy, validation, IO, timeout, cancellation, and internal
  failures distinguishable end-to-end
- `Function`: `src-tauri/src/error.rs`, `src-tauri/tests/error_taxonomy.rs`
- `Dependencies`: AQ-021, AQ-022, AQ-023, AQ-024
- `Acceptance criteria`:
  - Error codes remain stable across CLI and desktop renderers.
  - Validation errors do not collapse into generic failures.
- `Validation`: error-taxonomy tests, desktop bridge round-trip checks
- `Implementation owner`: `src-tauri`
- `Stage label`: Phase 1
- `Next test seam`: `src-tauri/src/error.rs`
- `Notes`: Keep the typed contract readable for callers.

## Phase 2 - Typed Command Contract and SOLID Shell Split

### AQ-031 - Shared command registry source

- `Epic`: AQ-001 Architecture and test quality maturity program
- `Feature`: Phase 2 typed command contract and shell SOLID split
- `Capability`: AQ-030 typed command contract
- `Task`: keep one registry as the source of truth for names, dispatch kinds,
  and output kinds
- `Function`: `crates/tachi-shell/src/commands.rs`,
  `crates/tachi-shell/tests/command_registry.rs`
- `Dependencies`: AQ-022, AQ-025
- `Acceptance criteria`:
  - The registry is unique and deterministic.
  - New commands are added in one place first.
- `Validation`: registry unit tests, surface-drift tests
- `Implementation owner`: `tachi-shell`
- `Stage label`: Phase 2
- `Next test seam`: `crates/tachi-shell/tests/command_registry.rs`
- `Notes`: Keep the registry small enough to derive adapters from it.

### AQ-032 - Shared argument decoder

- `Epic`: AQ-001 Architecture and test quality maturity program
- `Feature`: Phase 2 typed command contract and shell SOLID split
- `Capability`: AQ-030 typed command contract
- `Task`: derive CLI and Tauri argument decoding from the shared registry
- `Function`: `src-tauri/src/schema.rs`, CLI `parse_args` functions
- `Dependencies`: AQ-031
- `Acceptance criteria`:
  - CLI and Tauri accept the same command vocabulary.
  - Help/validation rules do not diverge between adapters.
- `Validation`: shared decoder tests, CLI/Tauri parity tests
- `Implementation owner`: `tachi-shell`
- `Stage label`: Phase 2
- `Next test seam`: `crates/tachi-shell/src/commands.rs`
- `Notes`: Main open-closed refactor seam.

### AQ-033 - Execution and output-sink split

- `Epic`: AQ-001 Architecture and test quality maturity program
- `Feature`: Phase 2 typed command contract and shell SOLID split
- `Capability`: AQ-030 executor and output-sink traits
- `Task`: split command execution, file writing, serialization, and progress
  reporting behind narrow traits
- `Function`: `crates/tachi-shell/src/commands.rs`,
  `crates/tachi-shell/src/tauri_bridge.rs`
- `Dependencies`: AQ-031, AQ-032
- `Acceptance criteria`:
  - Executor logic can be tested without filesystem side effects.
  - Output rendering can be swapped in tests.
  - Progress reporting does not own execution policy.
- `Validation`: trait-based unit tests, command-level regression tests
- `Implementation owner`: `tachi-shell`
- `Stage label`: Phase 2
- `Next test seam`: `crates/tachi-shell/tests/control_plane.rs`
- `Notes`: Main SOLID/SRP cleanup slice.

### AQ-034 - CLI/Tauri parity tests

- `Epic`: AQ-001 Architecture and test quality maturity program
- `Feature`: Phase 2 typed command contract and shell SOLID split
- `Capability`: AQ-030 parity verification
- `Task`: prove CLI and Tauri stay aligned as the shared command model evolves
- `Function`: `crates/tachi-shell/tests/tauri_bridge.rs`,
  `src-tauri/tests/bridge.rs`
- `Dependencies`: AQ-031, AQ-032, AQ-033
- `Acceptance criteria`:
  - Adding a synthetic command in tests requires no duplicate parser/schema
    edits.
  - Drift is caught before merge.
- `Validation`: registry diff tests, bridge parity tests
- `Implementation owner`: `src-tauri`
- `Stage label`: Phase 2
- `Next test seam`: `src-tauri/tests/registry_diff.rs`
- `Notes`: Treat adapter drift as a first-class regression signal.

## Phase 3 - Core API Hygiene and Module Decomposition

### AQ-041 - Narrow core facade

- `Epic`: AQ-001 Architecture and test quality maturity program
- `Feature`: Phase 3 core API hygiene and module decomposition
- `Capability`: AQ-040 public facade boundary
- `Task`: keep downstream crates compiling through the facade while narrowing
  internal module visibility
- `Function`: `crates/tachi-core/src/lib.rs`, `crates/tachi-core/src/facade.rs`
- `Dependencies`: AQ-031, AQ-033
- `Acceptance criteria`:
  - Downstream crates depend on facade APIs.
  - Internal implementation modules can move toward `pub(crate)` safely.
- `Validation`: compile checks, facade API tests
- `Implementation owner`: `tachi-core`
- `Stage label`: Phase 3
- `Next test seam`: `crates/tachi-core/tests/facade_api.rs`
- `Notes`: Preserve compatibility while shrinking the exposed surface.

### AQ-042 - Split infographic responsibilities

- `Epic`: AQ-001 Architecture and test quality maturity program
- `Feature`: Phase 3 core API hygiene and module decomposition
- `Capability`: AQ-040 reporting decomposition
- `Task`: split infographic payload assembly into smaller units for template
  discovery, domain aggregation, and rendering
- `Function`: `crates/tachi-core/src/infographic.rs`
- `Dependencies`: AQ-041
- `Acceptance criteria`:
  - Template lookup is injectable in tests.
  - Payload assembly remains behavior-compatible.
  - Module seams become smaller and easier to unit test.
- `Validation`: golden tests, focused unit tests for decomposition seams
- `Implementation owner`: `tachi-core`
- `Stage label`: Phase 3
- `Next test seam`: `crates/tachi-core/tests/infographic_payload.rs`
- `Notes`: Preserve output shape while reducing reasons-to-change.

### AQ-043 - Inject taxonomy and template providers

- `Epic`: AQ-001 Architecture and test quality maturity program
- `Feature`: Phase 3 core API hygiene and module decomposition
- `Capability`: AQ-040 provider injection
- `Task`: remove workspace-root inference from taxonomy/template loading where
  tests can supply providers directly
- `Function`: `crates/tachi-core/src/coverage_attestation.rs`,
  `crates/tachi-core/src/infographic.rs`
- `Dependencies`: AQ-042
- `Acceptance criteria`:
  - Providers can be swapped in tests without changing workspace layout.
  - Domain logic no longer needs to know where templates live on disk.
- `Validation`: provider-injection tests, behavior parity checks
- `Implementation owner`: `tachi-core`
- `Stage label`: Phase 3
- `Next test seam`: `crates/tachi-core/tests/coverage_attestation.rs`
- `Notes`: Dependency-inversion slice.

## Phase 4 - Test Quality and Adversarial Verification Upgrades

### AQ-051 - Unit/integration balance

- `Epic`: AQ-001 Architecture and test quality maturity program
- `Feature`: Phase 4 test quality and adversarial verification upgrades
- `Capability`: AQ-050 test quality maturity
- `Task`: move narrowly scoped parser/classifier/scorer checks closer to the
  source modules where practical
- `Function`: parser modules, scoring helpers, normalization helpers
- `Dependencies`: AQ-041, AQ-042
- `Acceptance criteria`:
  - Cheap edge cases live in source-level unit tests.
  - Expensive integration setup is reserved for cross-module contracts.
- `Validation`: test-surface review, local targeted runs
- `Implementation owner`: `tachi-core`
- `Stage label`: Phase 4
- `Next test seam`: `crates/tachi-core/tests/parsers.rs`
- `Notes`: Reduce fixture overhead without losing regression coverage.

### AQ-052 - Semantic golden policy

- `Epic`: AQ-001 Architecture and test quality maturity program
- `Feature`: Phase 4 test quality and adversarial verification upgrades
- `Capability`: AQ-050 semantic golden policy
- `Task`: pair exact goldens with schema and invariant assertions so snapshot
  drift is easier to interpret
- `Function`: `crates/tachi-core/tests/reporting_goldens.rs`
- `Dependencies`: AQ-051
- `Acceptance criteria`:
  - Golden updates require an invariant-based reason.
  - Semantic failures are visible even when strings change.
- `Validation`: snapshot tests, schema/invariant assertions
- `Implementation owner`: `tachi-core`
- `Stage label`: Phase 4
- `Next test seam`: `crates/tachi-core/tests/reporting_goldens.rs`
- `Notes`: Keep the snapshots meaningful, not merely brittle.

### AQ-053 - Property-test lane

- `Epic`: AQ-001 Architecture and test quality maturity program
- `Feature`: Phase 4 test quality and adversarial verification upgrades
- `Capability`: AQ-050 property coverage
- `Task`: add a property-test lane for normalization, coverage math, source
  attribution ordering, and parser robustness
- `Function`: normalization helpers, coverage math, parser helpers
- `Dependencies`: AQ-051, AQ-052
- `Acceptance criteria`:
  - Property cases cover boundary and monotonicity invariants.
  - Randomized input failures are reproducible.
- `Validation`: property-test harness, deterministic seeds in CI
- `Implementation owner`: `tachi-core`
- `Stage label`: Phase 4
- `Next test seam`: `crates/tachi-core/tests/coverage_percentage_computation.rs`
- `Notes`: Start small and promote the strongest invariants first.

### AQ-054 - Fuzz / mutation lane

- `Epic`: AQ-001 Architecture and test quality maturity program
- `Feature`: Phase 4 test quality and adversarial verification upgrades
- `Capability`: AQ-050 adversarial verification lanes
- `Task`: add non-blocking fuzz and mutation reporting first, then promote the
  highest-value survivors into Beads follow-up work
- `Function`: `cargo fuzz`, mutation harness, CI reporting lane
- `Dependencies`: AQ-053
- `Acceptance criteria`:
  - Fuzz and mutation lanes emit baseline reports.
  - Survivors become visible backlog items rather than hidden debt.
- `Validation`: non-blocking CI job or local harness, baseline report generation
- `Implementation owner`: `docs`
- `Stage label`: Phase 4
- `Next test seam`: repository-level tooling
- `Notes`: Keep the first version advisory so it can be adopted safely.

### AQ-055 - Count-stable coverage audit

- `Epic`: AQ-001 Architecture and test quality maturity program
- `Feature`: Phase 4 test quality and adversarial verification upgrades
- `Capability`: AQ-050 count-stable coverage audit
- `Task`: make the coverage audit assert category invariants and sentinel
  modules rather than brittle global counts
- `Function`: `crates/tachi-core/tests/coverage_audit.rs`,
  `crates/tachi-core/src/coverage_audit.rs`
- `Dependencies`: AQ-051, AQ-052
- `Acceptance criteria`:
  - Category drift fails clearly.
  - Moving or adding tests does not break the audit without a real behavior
    change.
- `Validation`: coverage-audit regression tests
- `Implementation owner`: `tachi-core`
- `Stage label`: Phase 4
- `Next test seam`: `crates/tachi-core/tests/coverage_audit.rs`
- `Notes`: Keep the audit strict on behavior, not on incidental counts.
