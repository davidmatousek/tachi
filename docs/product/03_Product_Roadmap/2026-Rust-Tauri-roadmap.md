# tachi Roadmap - Rust/Tauri Migration

**Last Updated**: 2026-06-05
**Theme**: migrate the shipped platform from Python-first scripts to a Rust core with a Tauri shell, while preserving feature parity
**Status**: Planning

---

## Current-State Summary

tachi currently ships as a Python-first repository with shell helpers, markdown-driven product docs, and pytest-based validation. There is now a Rust workspace with core parity slices for threat parsing, attack-chain parsing, compensating-controls parsing, risk-scores parsing, SARIF emission, and MAESTRO grouping, plus Rust-backed coverage-audit and control-plane command routing. The `src-tauri` shell scaffold now exists and routes through the shared Rust bridge, but the packaging/docs slice is still in progress.

The migration roadmap should therefore focus less on "rewrite everything" and more on:

1. establishing a Rust core that can faithfully own current shipped behavior,
2. preserving parity with the feature ledger in `../02_PRD/INDEX.md`,
3. moving validation to Rust-native unit, integration, and end-to-end tests,
4. wrapping the core with a thin Tauri distribution layer,
5. retiring Python only after parity is proven.

---

## Phase 1 - Rust Foundation

**Timeline**: immediate / first migration cycle
**Goal**: create the Rust workspace and define the parity boundary

### Objectives

1. Create a Rust workspace at the repo root.
2. Define crate boundaries for core logic, CLI commands, and Tauri-facing command handlers.
3. Build a feature-parity map from the current Python/shell implementation to Rust modules.

### Planned Work

| Item | Source | Status | Notes |
|------|--------|--------|-------|
| Rust workspace skeleton | Backlog | Done | Root `Cargo.toml`, `Cargo.lock`, and `crates/tachi-core` now exist |
| First parity crate plan | Docs | Done | See `docs/rust/2026-06-04-first-parity-crate-plan.md` |
| Feature parity map | Backlog | In progress | Preserve current shipped behavior while Rust now owns the parsing, aggregation, and SARIF slices that have already landed |
| Python compatibility boundary | Backlog | Not started | Define what stays Python temporarily and why |

### Success Criteria

- `cargo metadata` works from the repo root.
- Core crates have a clear ownership boundary.
- The migration plan can answer "what has moved" and "what is still Python" without guessing.

### Risks

- Recreating the current architecture too literally instead of simplifying it.
- Expanding scope before the parity boundary is stable.

---

## Phase 2 - Rust-Native Coverage

**Timeline**: first migration cycle after the workspace exists
**Goal**: move test visibility to Rust-native unit, integration, and e2e layers

### Objectives

1. Define Rust-native test layout and naming conventions.
2. Add a Rust coverage audit command.
3. Create explicit fixtures for unit, integration, and end-to-end tests.

### Planned Work

| Item | Source | Status | Notes |
|------|--------|--------|-------|
| Rust coverage audit command | Backlog | Done | Rust-backed `coverage-audit` binary now reports the active test surface |
| Unit/integration fixture layout | Backlog | In progress | Rust parity tests now cover threat, attack-chain, compensating-controls, risk-scores, and SARIF slices in `crates/tachi-core/tests/` |
| Tauri e2e harness decision | Backlog | Not started | Decide whether desktop e2e uses Tauri driver, Playwright, or a wrapped native harness |

### Success Criteria

- Rust unit tests are run with `cargo test`.
- Integration tests are clearly separate from unit tests.
- End-to-end coverage has one explicit path and one explicit boundary.
- Coverage reporting is no longer inferred from Python filenames.

### Risks

- A migration that ports code without porting the test taxonomy will hide regressions.
- Desktop e2e can become expensive if the harness is not kept narrow.

---

## Phase 3 - Core Port

**Timeline**: after Rust coverage is stable
**Goal**: move the highest-leverage Python behavior into Rust

### Objectives

1. Port deterministic parsing and aggregation logic.
2. Port report-data generation and coverage attestation helpers.
3. Port bootstrap/update command handlers.

### Planned Work

| Item | Source | Status | Notes |
|------|--------|--------|-------|
| Parser/aggregation port | Backlog | In progress | Threat-report narrative parsing, attack-chain parsing, compensating-controls parsing, and risk-scores parsing have moved to `tachi-core` |
| Report-data generation port | Backlog | In progress | Remediation-action selection and MAESTRO grouping now live in `tachi-core`, and threat/risk SARIF emitters are Rust-backed |
| Bootstrap/update command port | Backlog | Not started | Removes Python from the control plane |

### Success Criteria

- The Rust core can reproduce current outputs from frozen fixtures.
- Python becomes a temporary adapter rather than the source of truth.
- The port is small enough to review and test incrementally.

---

## Phase 4 - Tauri Shell

**Timeline**: after core parity is proven
**Goal**: expose the Rust core through a desktop shell without duplicating logic

### Objectives

1. Add a Tauri shell around the Rust core.
2. Keep the frontend thin and command-driven.
3. Reuse the Rust domain model for CLI and desktop paths.

### Planned Work

| Item | Source | Status | Notes |
|------|--------|--------|-------|
| Tauri app shell | Backlog | Done | Thin wrapper around Rust core commands |
| Desktop command bridge | Backlog | In progress | `tachi-shell` is now the shared command layer for CLI and future Tauri, with routing tests covering install/init/update/bootstrap |
| Packaging/distribution docs | Backlog | Not started | Keep install/update instructions aligned with the new shell |

### Success Criteria

- The desktop shell calls the same Rust core used by CLI commands.
- No duplicate business logic exists in the frontend.
- Packaging and run instructions are updated for Rust/Tauri.

### Risks

- Tauri-specific behavior drifting away from CLI behavior.
- Native packaging complexity if the shell is introduced before the core is stable.

---

## Phase 5 - Python Retirement

**Timeline**: final migration cycle
**Goal**: remove Python-only implementation paths after parity is confirmed

### Objectives

1. Retire Python helper scripts and compatibility shims.
2. Update migration guides and quickstarts.
3. Remove or quarantine Python tests that no longer protect the canonical implementation.

### Planned Work

| Item | Source | Status | Notes |
|------|--------|--------|-------|
| Python retirement plan | Backlog | Not started | Should only begin after Rust parity gates are green |
| Doc refresh for Rust/Tauri commands | Backlog | Not started | Prevents stale Python instructions from lingering |
| Legacy-test deprecation map | Backlog | Not started | Distinguish parity guards from obsolete coverage |

### Success Criteria

- The repo no longer depends on Python for canonical behavior.
- Any remaining Python surface is explicitly marked transitional or removed.
- The roadmap can point to Rust-native validation as the primary truth.

---

## What Is Not Planned

- A rewrite that changes shipped behavior just to look more modern.
- A Tauri UI that re-implements business logic.
- A Rust port without parity tests.
- A long-term dual implementation where Python remains authoritative.
