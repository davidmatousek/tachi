# Rust/Tauri-Only Migration Issue Cards

**Last Updated**: 2026-06-10
**Status**: Planning backlog derived from the Rust/Tauri-only roadmap

These cards are the execution-level backlog for the migration roadmap in
[2026-06-08-rust-tauri-only-roadmap.md](./2026-06-08-rust-tauri-only-roadmap.md).
They are intentionally small, phase-aligned, and mergeable in sequence.

## Current Completion

Current roadmap completion: 17% (1 of 6 cards complete).

Completion is counted by closed roadmap cards only. Partial implementation work is listed as in progress and does not count as complete until the card acceptance criteria pass validation.

| Card | Status | Next validation focus |
|---|---|---|
| RT-010 | Complete | Keep the frozen Python surface inventory synchronized with retirements. |
| RT-011 | In progress | Continue migrating the remaining pytest coverage after the Rust-native defaults-env init, adversarial init, template git clone timeout, precommit matrix, PDF page-positioning, coverage-attestation in-scope, coverage-attestation report-data guard, coverage-attestation pagination smoke, coverage-percentage computation, MAESTRO pattern-classification rules, and attack-chain extraction migrations. Current audit: 64 active modules, 51 Rust integration modules, 0 Python unit modules, 0 Python smoke modules, 12 support/regression modules. |
| RT-012 | In progress | Continue parser/report-data parity after Rust asset tag parsing, report-data image binding emission, infographic output-file handling, coverage-attestation in-scope filtering, coverage-attestation report-data guard, coverage-attestation pagination smoke, coverage-percentage computation, attack-chain extraction, and SARIF runtime retirement, then remove Python runtime dependencies from canonical behavior. |
| RT-013 | Pending | Start after RT-012 establishes the shared Rust command layer as canonical. |
| RT-014 | Pending | Start after RT-012 and RT-013 prove Python packaging and scaffold surfaces are no longer needed. |
| RT-015 | Pending | Start after the Rust-only path is stable enough for benchmark-driven hardening. |

## Card Set

### RT-010 - Freeze the Python surface inventory

- **Priority**: P0
- **Labels**: `rust`, `inventory`, `migration`, `docs`
- **Summary**: Catalog every Python runtime entrypoint, Python dependency, and Python doc reference that still ships in the repository.
- **Acceptance**:
  - Every active Python file is listed.
  - Every Python dependency or pytest reference is mapped to a Rust replacement or retirement path.
  - The inventory is reproducible from the current repo tree.
- **Depends on**: none

### RT-011 - Migrate pytest coverage to Rust-native tests

- **Priority**: P0
- **Labels**: `rust`, `testing`, `coverage`, `migration`
- **Summary**: Port the highest-signal pytest suites into Rust unit and integration tests, then define the narrow Rust-owned E2E boundary.
- **Current evidence**: RT-009 docs, taxonomy integrity, project-name parsing, YAML import placement, infographic command dispatch, source-attribution parser coverage, the template substitute shim canary, template substitute no-`eval` lint, template substitute literal-substitution contract, template config load unit and integration contracts, init-input unit contract, defaults-env init contract, adversarial init contract, template git clone timeout contract, init precommit matrix, PDF page-positioning, finding-pattern parser, agentic pattern extraction, misinformation schema, output-integrity schema, init self-delete, F-A3 populator wiring, coverage-attestation aggregation, coverage-attestation in-scope filtering, coverage-attestation report-data guard, coverage-attestation pagination smoke, coverage-percentage computation, asset-sensitivity tag coverage, MAESTRO pattern-classification rules coverage, executive-architecture infographic payload coverage, attack-chain parsing coverage, attack-chain Mermaid generation coverage, and attack-chain extraction coverage now have Rust-native tests. Current audit: 64 active modules, 51 Rust integration modules, 0 Python unit modules, 0 Python smoke modules, 12 support/regression modules.
- **Acceptance**:
  - Core parser and payload behavior have Rust-native regression tests.
  - The Rust test taxonomy covers unit, integration, smoke, and critical E2E flows.
  - Coverage stays at or above the 80% floor during the migration.
- **Depends on**: RT-010

### RT-012 - Port the remaining runtime logic into Rust

- **Priority**: P1
- **Labels**: `rust`, `core`, `parity`, `sarif`
- **Summary**: Move the remaining report, infographic, parser, and SARIF logic from Python scripts into Rust modules.
- **Current evidence**: Rust `report-data` supports direct `--output` writing, Rust `infographic-data` now supports direct `--output` writing, emits `project-name` through the shared Rust project-name parser, preserves the image binding plus byte-probe behavior previously covered by pytest, now emits coverage-attestation payloads in Rust, now owns asset-sensitivity tag parsing in `tachi-core`, and the standalone Python SARIF generators, pagination smoke scaffolds, attack-chain extraction pytest, and infographic extractor runtime have been retired in favor of Rust tests and CLI binaries; full report payload parity is still open.
- **Acceptance**:
  - The Rust core reproduces the current shipped outputs on frozen fixtures.
  - Python runtime scripts are no longer required for canonical behavior.
  - Shared Rust modules own the taxonomy and coverage catalog data.
- **Depends on**: RT-010, RT-011

### RT-013 - Keep the Tauri shell thin and parity-aligned

- **Priority**: P1
- **Labels**: `rust`, `tauri`, `desktop`, `shell`
- **Summary**: Make CLI and desktop call paths share the same Rust command layer and validation behavior.
- **Acceptance**:
  - CLI and Tauri paths use the same command handlers.
  - Desktop validation covers the smallest critical-flow set.
  - No duplicate business logic lives in the frontend.
- **Depends on**: RT-012

### RT-014 - Retire the Python packaging and stack scaffolds

- **Priority**: P1/P2
- **Labels**: `rust`, `cleanup`, `python`, `docs`
- **Summary**: Remove or archive the Python packaging surface, pytest configuration, and FastAPI-based stack scaffolds once Rust parity is stable.
- **Acceptance**:
  - `pyproject.toml` and `requirements-dev.txt` are no longer part of the active canonical path.
  - Python-specific install and testing guidance is removed from active docs.
  - Any remaining FastAPI scaffolds are archived or replaced with Rust/Tauri guidance.
- **Depends on**: RT-012, RT-013

### RT-015 - Optimize the Rust path for speed and reliability

- **Priority**: P2
- **Labels**: `rust`, `performance`, `reliability`, `benchmarks`
- **Summary**: Reduce startup cost, eliminate avoidable shell-outs, and tighten error handling after the Rust path is in place.
- **Acceptance**:
  - Hot-path shell-outs are removed or minimized.
  - Startup and command latency have explicit benchmarks.
  - Error handling is deterministic and actionable across CLI and Tauri paths.
- **Depends on**: RT-012, RT-013, RT-014

## Execution Order

1. RT-010
2. RT-011
3. RT-012
4. RT-013
5. RT-014
6. RT-015

## Validation Gate

Each card must pass its local unit, integration, and E2E validation before the next card starts, and the workspace coverage floor must remain at or above 80%.
