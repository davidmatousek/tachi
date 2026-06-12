# Rust/Tauri-Only Migration Roadmap

**Last Updated**: 2026-06-12
**Status**: Active migration roadmap
**Objective**: make `tachi-rust` a Rust + Tauri only repository

## Executive Summary

`tachi-rust` already has a meaningful Rust core, Rust-backed coverage audit, and a thin Tauri shell path. The remaining work is to remove the Python runtime surface, migrate the pytest suite to Rust-native tests, and make the Rust workspace the only canonical implementation and validation path.

This roadmap treats Python as transitional only. The target end state is:

- no Python runtime entrypoints in the shipped repo
- no Python packaging or pytest-only validation path
- no Python-based stack scaffolds in the active product surface
- Rust and Tauri as the only canonical implementation layers

The execution-level backlog lives in [2026-06-08-rust-tauri-only-issue-cards.md](./2026-06-08-rust-tauri-only-issue-cards.md), and the merge sequence lives in [2026-06-08-rust-tauri-only-merge-plan.md](./2026-06-08-rust-tauri-only-merge-plan.md).

## Current Status

Current roadmap completion: 17% (1 of 6 cards complete).

This status uses card closure rather than subjective partial estimates. In-progress cards are tracked explicitly but do not count as complete until their acceptance criteria are satisfied and validated.

| Card | Status | Current evidence |
|---|---|---|
| RT-010 | Complete | The Python surface inventory is frozen in [2026-06-08-python-surface-inventory.md](./2026-06-08-python-surface-inventory.md). |
| RT-011 | In progress | RT-009 documentation coverage, taxonomy integrity checks, project-name parser coverage, the YAML import invariant, infographic command-dispatch coverage, source-attribution parser coverage, the template substitute shim canary, template substitute no-`eval` lint, template substitute literal-substitution coverage, template config load unit and integration coverage, init input unit coverage, defaults-env init coverage, adversarial init coverage, template git clone timeout coverage, init precommit matrix coverage, mmdc preflight coverage, PDF page-positioning coverage, backward-compatibility PDF byte-identity coverage, finding-pattern parser coverage, agentic pattern extraction coverage, misinformation schema coverage, output-integrity schema coverage, human-trust-exploitation schema/attribution coverage, extractor contract fixes, init self-delete coverage, F-A3 populator wiring coverage, report-data image binding coverage, coverage-attestation aggregation coverage, coverage-attestation in-scope filtering coverage, coverage-attestation report-data guard coverage, coverage-attestation tier merge coverage, coverage-attestation pagination smoke coverage, coverage-percentage computation coverage, asset-sensitivity tag coverage, MAESTRO pattern-classification rules coverage, executive-architecture infographic payload coverage, attack-chain parsing coverage, attack-chain Mermaid generation coverage, init constitution coverage, attack-chain extraction coverage, tool-abuse enrichment coverage, pattern-synthesis coverage, ML Top 10 coverage bundle enrichment coverage, mobile Top 10 coverage bundle enrichment coverage, LLM10 unbounded consumption coverage, coverage-attestation audit coverage, init timing trace coverage, init trace summary coverage, archived FastAPI docs guidance, archived FastAPI getting-started guidance, and init substitution E2E coverage have moved from pytest to Rust tests; the dead `tests/scripts` init helper package is retired. Current audit: 71 active modules, 70 Rust integration modules, 0 Python unit modules, 0 Python smoke modules, 0 support/regression modules. |
| RT-012 | In progress | Rust-native report-data output handling, infographic output-file handling, report project metadata emission, report-data image binding and byte-probe parity, coverage-attestation payload emission, coverage-attestation in-scope filtering, coverage-attestation report-data guard coverage, coverage-attestation pagination smoke coverage, asset-sensitivity tag parsing, executive-architecture infographic payload parity, and SARIF CLI slices now cover the threat/risk SARIF runtime paths; `scripts/extract-report-data.py`, `scripts/tachi_parsers.py`, the FastAPI Alembic `env.py` scaffolds, the FastAPI backend test-package scaffolding, the FastAPI backend app runtime trees, the FastAPI backend scaffold packaging manifests, the FastAPI backend Alembic scaffold packaging manifests, the dead `tests/scripts` helper package, the dead root pytest support package, `pyproject.toml`, and `requirements-dev.txt` are retired and the active Python inventory is empty. |
| RT-013 | Pending | Tauri shell parity work depends on RT-012 runtime parity. |
| RT-014 | Pending | Python packaging and FastAPI scaffold archival depends on RT-012 and RT-013; backend scaffold packaging manifests, backend Alembic scaffold packaging manifests, and the FastAPI stack packs are archived legacy references. |
| RT-015 | In progress | Speed and reliability hardening depends on the Rust-only runtime path being stable. |

The prior broad migration snapshot remains useful for orientation: Rust core parity is the strongest track, Rust-native test migration and runtime-script retirement are active, and Tauri shell hardening plus packaging/scaffold retirement remain downstream.

## BEADS Map

This roadmap uses a BEADS-style hierarchy:

- `Epic` = a migration theme
- `Feature` = a deliverable slice within the epic
- `Capability` = the behavior the feature must provide
- `Task` = the work items required to build the capability
- `Function` = the concrete function, command, fixture, or test boundary that must exist when the task is done

### Epic 1 - Rust Runtime Ownership

**Goal**: move all shipped behavior to Rust-owned code paths.

#### Feature 1.1 - Port Python script entrypoints to Rust

- **Capabilities**
  - report data extraction
  - infographic payload assembly
  - SARIF emission
  - taxonomy normalization
  - coverage catalog lookup
- **Tasks**
  - port `scripts/generate-threats-sarif.py`
  - port `scripts/generate-risk-scores-sarif.py`
  - retire `scripts/tachi_parsers.py`
  - retire FastAPI Alembic `env.py` scaffolds
  - retire FastAPI backend test-package scaffolding
  - retire the root pytest support package
  - retire the FastAPI backend app runtime trees
- **Functions**
  - `build_report_payload`
  - `build_infographic_payload`
  - `emit_threat_sarif`
  - `emit_risk_score_sarif`
  - `normalize_taxonomy_label`
  - `load_coverage_catalog`

#### Feature 1.2 - Replace Python packaging with Rust-native workspace metadata

- **Capabilities**
  - build from `Cargo.toml`
  - run from Rust binaries and Tauri commands
  - avoid Python dependency resolution in install and CI paths
- **Tasks**
  - retire `pyproject.toml`
  - retire `requirements-dev.txt`
  - remove Python-specific install guidance from active docs
  - replace any Python-only bootstrap assumptions in scripts and templates
- **Functions**
  - `cargo build`
  - `cargo run`
  - `cargo test`
  - `cargo llvm-cov`

### Epic 2 - Rust-Native Test Migration

**Goal**: translate every meaningful pytest case into Rust-native tests or a Rust-owned E2E harness.

#### Feature 2.1 - Port unit and integration tests to Rust

- **Capabilities**
  - fixture-based regression tests
  - parser and transformer contract tests
  - CLI command and payload shape tests
  - taxonomy and schema validation tests
- **Tasks**
  - migrate `tests/scripts/test_*` modules into `crates/*/tests`
  - migrate `tests/schemas/test_taxonomy_integrity.py`
  - move shared fixture helpers into Rust test support modules
  - keep the current Python tests only as temporary reference while the Rust equivalents land
- **Functions**
  - `assert_fixture_roundtrip`
  - `assert_parser_contract`
  - `assert_sarif_shape`
  - `assert_taxonomy_integrity`
  - `assert_coverage_audit_counts`

#### Feature 2.2 - Define the Rust end-to-end boundary

- **Capabilities**
  - CLI smoke validation
  - Tauri command bridge validation
  - desktop-critical flow validation
- **Tasks**
  - define the minimum E2E set for install/init/update/report generation
  - wire a Rust-owned desktop harness for the critical flows
  - keep expensive UI automation limited to the smallest set of business-critical paths
- **Functions**
  - `invoke_cli_smoke`
  - `invoke_tauri_command`
  - `assert_critical_flow`

### Epic 3 - Tauri Shell and Desktop Parity

**Goal**: keep the shell thin while the Rust core stays authoritative.

#### Feature 3.1 - Use one Rust command layer for CLI and desktop

- **Capabilities**
  - shared command routing
  - shared error mapping
  - shared serialization layer
- **Tasks**
  - keep command handlers in Rust
  - avoid duplicate business logic in the frontend
  - ensure CLI and desktop paths return the same payloads for the same inputs
- **Functions**
  - `route_command`
  - `map_error`
  - `serialize_payload`
  - `deserialize_input`

#### Feature 3.2 - Make desktop validation explicit and narrow

- **Capabilities**
  - desktop smoke coverage
  - deterministic payload rendering
  - command round-trip checks
- **Tasks**
  - add the minimum desktop harness needed for critical flows
  - avoid broad UI reimplementation work
  - keep the shell focused on invocation, display, and persistence
- **Functions**
  - `validate_desktop_roundtrip`
  - `validate_command_state`

### Epic 4 - Python Surface Retirement

**Goal**: remove the remaining Python runtime and toolchain surfaces once Rust parity is stable.

#### Feature 4.1 - Remove Python entrypoints and toolchain dependencies

- **Capabilities**
  - no Python entrypoint in the shipped repo
  - no Python dev dependency in the canonical path
  - no Python-first CI contract
- **Tasks**
  - delete or archive Python scripts after parity landing
  - remove pytest configuration and Python-only developer dependencies
  - remove Python-specific references from build and release docs
- **Functions**
  - `no_python_entrypoints`
  - `no_pytest_contract`
  - `no_python_packaging`

#### Feature 4.2 - Replace Python stack scaffolds with Rust-native guidance

- **Capabilities**
  - Rust/Tauri stack examples
  - Rust-native developer onboarding
  - no FastAPI/pytest-specific shipped defaults in the active repo surface
- **Tasks**
  - retire or replace `stacks/fastapi-react*`
  - update any scaffold defaults that still assume Python
  - ensure stack docs describe Rust/Tauri options only
- **Functions**
  - `validate_stack_template`
  - `validate_runtime_assumptions`

### Epic 5 - Speed and Reliability Hardening

**Goal**: use the Rust rewrite to reduce startup cost, improve determinism, and tighten failure handling.

#### Feature 5.1 - Reduce startup and IO overhead

- **Capabilities**
  - fewer process spawns
  - less repeated filesystem parsing
  - deterministic command execution
- **Tasks**
  - eliminate shell-outs from hot paths where Rust can own the logic
  - keep parsing and payload generation in-memory where possible
  - add targeted benchmarks for the slowest flows
- **Functions**
  - `measure_startup_time`
  - `measure_command_latency`
  - `track_allocations`

#### Feature 5.2 - Improve failure isolation and observability

- **Capabilities**
  - explicit error boundaries
  - predictable exit codes
  - actionable diagnostics
- **Tasks**
  - standardize error shape across CLI and Tauri paths
  - keep validation failures early and explicit
  - prefer deterministic fixtures over ad hoc mutable state
- **Functions**
  - `normalize_error`
  - `classify_exit_code`
  - `log_actionable_failure`

#### Feature 5.3 - Analyze and optimize the slow init workflow

- **Capabilities**
  - init-path phase timing visibility
  - cold-start and warm-start regression comparison
  - fewer redundant shell-outs and filesystem scans during init
- **Tasks**
  - instrument the init path so each startup phase reports timing via `AOD_INIT_TRACE=1`
  - scope placeholder substitution to manifest-backed personalized files and the constitution clean template instead of walking the whole tree
  - factor manifest-backed personalized path extraction into a reusable helper and reuse the cached list across substitution and residual scanning
  - benchmark the slowest init path with and without precommit / template bootstrapping
  - remove repeated parsing and process spawns once the slow phase is isolated
- **Functions**
  - `aod_trace_init_phase`
  - `aod_template_parse_manifest`
  - `measure_init_cold_start`
  - `measure_init_phase_latency`
  - `trace_init_workflow`

## Phase Plan

Each phase is designed to be mergeable on its own and to land behind tests before the next phase starts.

### Phase 0 - Inventory and Contract Freeze

**Priority**: P0  
**Purpose**: freeze the current Python surface inventory and lock the Rust replacement targets.

- Inventory every Python file, Python dependency, and Python doc reference.
- Map each item to its Rust owner or explicit retirement path.
- Freeze the test taxonomy so every pytest case has a migration destination.

**Validation**

- Unit: inventory fixtures and mapping tables are internally consistent.
- Integration: current Rust command paths still pass existing tests.
- E2E: current critical CLI flows still work without regression.
- Coverage gate: keep the workspace at or above the current baseline, no drop below 80%.

### Phase 1 - Rust-Native Test Migration

**Priority**: P0  
**Purpose**: replace pytest-centric coverage with Rust tests before deleting legacy paths.

- Port the high-signal parser, payload, and schema tests first.
- Move shared test helpers into Rust support modules.
- Define a narrow Rust-owned E2E set for the critical flows only.

**Validation**

- Unit: every migrated behavior has a direct Rust test.
- Integration: crate-level tests cover command and payload boundaries.
- E2E: CLI smoke and one desktop-critical flow are executable from Rust-owned tooling.
- Coverage gate: Rust-native coverage stays at or above 80%; current target is to hold the existing 85%+ baseline.

### Phase 2 - Runtime Port and Parity

**Priority**: P0/P1  
**Purpose**: move all remaining runtime logic out of Python scripts and into Rust.

- Port report extraction and infographic generation.
- Port SARIF emission and shared parsing helpers.
- Make Rust the canonical owner of taxonomy and coverage data.

**Validation**

- Unit: each ported module has parity fixtures and edge-case coverage.
- Integration: end-to-end file inputs produce byte-stable or schema-stable outputs.
- E2E: CLI and desktop command paths produce equivalent user-visible results.
- Coverage gate: no phase exit until coverage remains at or above 80%.

### Phase 3 - Tauri Shell Parity

**Priority**: P1  
**Purpose**: keep the shell thin and make desktop behavior match CLI behavior.

- Use one Rust command layer for desktop and CLI.
- Keep frontend state and command wiring minimal.
- Add only the desktop validation needed for critical user flows.

**Validation**

- Unit: command serialization and error mapping are covered.
- Integration: shared command paths run in both CLI and Tauri contexts.
- E2E: install/init/update/report-generation paths pass in the desktop harness.
- Coverage gate: preserve or improve the current Rust coverage baseline.

### Phase 4 - Python Retirement

**Priority**: P1/P2  
**Purpose**: remove Python from active runtime and testing surfaces.

- Delete or archive Python scripts after their Rust equivalents land.
- Remove `pyproject.toml`, `requirements-dev.txt`, and pytest guidance from active docs.
- Replace FastAPI stack defaults with Rust/Tauri-native guidance or archived examples.

**Validation**

- Unit: repo search assertions prove no active Python entrypoints remain.
- Integration: build and test run without Python toolchain dependency in the canonical path.
- E2E: shipped flows run only through Rust/Tauri paths.
- Coverage gate: still at or above 80% after removal.

### Phase 5 - Performance and Reliability Hardening

**Priority**: P2  
**Purpose**: use the Rust migration to reduce latency and make failures easier to diagnose.

- Reduce process spawning and repeated parsing.
- Add benchmarks for startup and command latency.
- Tighten error handling and output consistency.

**Validation**

- Unit: deterministic benchmarks or microbenchmarks exercise the hot paths.
- Integration: latency-sensitive flows stay within the agreed budget.
- E2E: critical flows remain reliable under normal and error conditions.
- Coverage gate: do not regress below the 80% floor.

## Migration Inventory

This is the current Python-to-Rust replacement map for the repo's active surface.

| Current Python Surface | Rust-Native Target |
|---|---|
| `scripts/generate-threats-sarif.py` | Rust SARIF command / library in `tachi-cli` or `tachi-core` |
| `scripts/generate-risk-scores-sarif.py` | Rust SARIF command / library in `tachi-cli` or `tachi-core` |
| `scripts/tachi_parsers.py` | retired; parser behavior now lives in `tachi-core` modules |
| `stacks/fastapi-react*/scaffold/backend/alembic/env.py` | retired; Alembic env scaffolds are no longer active Python surface |
| `stacks/fastapi-react*/scaffold/backend/alembic` | retired; backend Alembic scaffold directories are no longer active Python surface |
| `stacks/fastapi-react*/scaffold/backend/alembic.ini` | retired; backend Alembic scaffold manifests are no longer active Python surface |
| `stacks/fastapi-react*/scaffold/backend/alembic/versions` | retired; backend Alembic scaffold directories are no longer active Python surface |
| `stacks/fastapi-react*/scaffold/backend/alembic/versions/.gitkeep` | retired; backend Alembic scaffold manifest placeholders are no longer active Python surface |
| `stacks/fastapi-react*/scaffold/backend/tests/{api/__init__.py,__init__.py,conftest.py}` | retired; backend test-package scaffolding is no longer active Python surface |
| `stacks/fastapi-react*/scaffold/backend/app/{main.py,api/deps.py,api/v1/router.py,db/base.py,db/session.py,core/middleware.py,core/exceptions.py,config.py}` | retired; backend app runtime trees are no longer active Python surface |
| `stacks/fastapi-react*/scaffold/backend/pyproject.toml` | retired; backend scaffold packaging manifests are no longer active Python surface |
| `tests/{conftest.py,__init__.py,schemas/__init__.py}` | retired; root pytest support package is no longer active Python surface |
| `scripts/extract-report-data.py` | retired; report-data builder now lives in Rust |
| `tests/scripts/*.py` | Rust integration and end-to-end tests |
| `tests/schemas/test_taxonomy_integrity.py` | Rust taxonomy/schema validation tests |
| `pyproject.toml` | retired; Rust workspace metadata now lives in `Cargo.toml` |
| `requirements-dev.txt` | retired; Cargo dev-dependencies and CI tooling now live in Rust workspace manifests |
| `stacks/fastapi-react*` | archived legacy references; Rust/Tauri-native stack guidance now lives in active packs |

## Validation Policy

Every phase must pass the same validation ladder before it can merge:

1. **Unit tests** for the changed Rust modules.
2. **Integration tests** for command, fixture, and payload boundaries.
3. **E2E validation** for the smallest set of critical user flows.
4. **Coverage validation** with a floor of **80% Rust-native coverage**.
5. **Reliability validation** with no unresolved regressions in startup, exit codes, or command routing.

The current workspace already sits above the requested floor, so the migration must preserve that margin while Python is removed.

## Merge Cadence

- Use one isolated git worktree per phase or feature cluster.
- Land changes in small conventional commits.
- Merge only after the phase's unit, integration, E2E, and coverage gates are green.
- Prefer progressive merges into `main` instead of one large end-state branch.

## Out of Scope

- Keeping Python as a long-term canonical runtime.
- Retaining pytest as the primary validation path once the Rust equivalents exist.
- Expanding the Tauri UI beyond the minimum needed for parity and usability.
