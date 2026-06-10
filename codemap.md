# Repository Atlas: tachi-rust

## Project Responsibility

`tachi-rust` is the Rust and Tauri implementation track for Tachi threat-modeling workflows. The current canonical path is the Rust workspace: `tachi-core` owns parsing and report data, `tachi-cli` exposes command-line entrypoints, `tachi-shell` provides shared command handlers, and `src-tauri` keeps the desktop bridge thin.

The repository is still migrating away from the original Python ecosystem. Remaining Python scripts, pytest suites, and FastAPI stack scaffolds are tracked as transitional surfaces in `docs/roadmap/2026-06-08-python-surface-inventory.md`.

## System Entry Points

| Entry Point | Responsibility |
|---|---|
| `Cargo.toml` | Workspace manifest for `crates/tachi-core`, `crates/tachi-cli`, `crates/tachi-shell`, and `src-tauri`. |
| `crates/tachi-core/src/lib.rs` | Core Rust library export surface for parsers, report data, SARIF builders, taxonomy, coverage audit, and infographic payloads. |
| `crates/tachi-cli/src/bin/*.rs` | Rust CLI binaries for init/install/update/bootstrap, report-data, infographic-data, SARIF generation, and coverage audit. |
| `crates/tachi-shell/src/commands.rs` | Shared command layer used by CLI-style flows and the Tauri bridge. |
| `src-tauri/src/lib.rs` | Desktop command registration and bridge integration for Tauri. |
| `Makefile` | Validation shortcuts, including the Rust coverage gate via `make llvm-cov`. |
| `docs/roadmap/` | Canonical migration roadmap, issue cards, merge plan, and Python-surface inventory. |

## Directory Map

| Directory | Responsibility Summary |
|---|---|
| `crates/tachi-core/` | Domain and data-transformation core. It parses generated threat-model artifacts, computes MAESTRO and coverage views, builds report data, emits SARIF payloads, and owns the Rust coverage-audit catalog. |
| `crates/tachi-cli/` | Thin CLI binary layer. Binaries parse flags, call shared core/shell functions, and write files or stdout. Business logic should move down into `tachi-core` or `tachi-shell`. |
| `crates/tachi-shell/` | Shared command facade for shell-style control-plane operations and Tauri-facing command dispatch. Keeps desktop and CLI command semantics aligned. |
| `src-tauri/` | Tauri desktop shell. It should remain a bridge/registration layer and avoid duplicate business logic. |
| `schemas/` | Finding schema and taxonomy catalogs used by parser, source-attribution, coverage, and crosswalk validation tests. |
| `.claude/` | Agent, command, skill, and reference content inherited from the original Tachi workflow. This is data/configuration for threat-modeling behavior, not Rust runtime code. |
| `.aod/` | AOD shell helpers, templates, and governance memory. Some shell helpers remain under Rust test coverage while migration continues. |
| `tests/scripts/` | Transitional pytest suite and fixtures. RT-011 progressively ports high-signal coverage into Rust tests and removes retired pytest modules. |
| `tests/fixtures/` | Frozen fixture copies and baseline trees used for compatibility checks. These are excluded from active coverage-audit counts. |
| `scripts/` | Transitional Python runtime scripts from the original implementation. RT-012 tracks porting remaining canonical behavior into Rust. |
| `stacks/` | Legacy Python/FastAPI and frontend scaffolds. RT-014 tracks retirement or archival after Rust/Tauri parity is stable. |
| `docs/` | Public project documentation. Roadmap and product planning documents live under `docs/roadmap/`; testing status lives under `docs/testing/`. |

## Rust Data And Control Flow

1. CLI binaries in `crates/tachi-cli/src/bin/` parse command arguments and delegate to Rust libraries.
2. Shared business logic runs in `tachi-core` modules:
   - `parsers.rs` parses project names, threat findings, markdown tables, source attribution, and agentic patterns.
   - `report_data.rs` builds Typst payload data for report assembly.
   - `infographic.rs` builds JSON payloads and MAESTRO visual data.
   - `risk_scores.rs`, `threats_sarif.rs`, and `sarif_common.rs` build SARIF exports.
   - `coverage_taxonomy.rs` centralizes coverage and MAESTRO taxonomy labels.
   - `coverage_audit.rs` classifies active test modules by unit, integration, smoke, E2E, and support/regression families.
3. `tachi-shell` exposes reusable command functions for shell and desktop paths.
4. `src-tauri` registers desktop commands and dispatches through the shared shell bridge.

## Testing And Validation

| Level | Current Rust-Native Surface |
|---|---|
| Unit | Rust unit tests plus 2 remaining transitional pytest unit modules listed by `coverage-audit`. |
| Integration | Rust integration tests under `crates/*/tests` and `src-tauri/tests`. |
| Smoke | Transitional smoke modules tracked by `tachi-core::coverage_audit`; current audit shows 2 remaining Python smoke modules. |
| E2E | Critical init flow currently represented by `tests/scripts/test_init_sh_substitution.py` while the Rust-owned E2E boundary is being defined. |
| Coverage | `make llvm-cov` is the release-quality local gate. Current validated baseline: 85.69% regions / 86.30% lines. |

Primary validation commands:

```bash
cargo fmt --check
git diff --check
cargo test -q
cargo clippy --all-targets -- -D warnings
make llvm-cov
cargo run -q -p tachi-cli --bin coverage-audit
```

## Migration Map

| Roadmap Card | Current Direction |
|---|---|
| RT-011 | Migrate remaining pytest coverage into Rust tests using TDD. Keep explicit unit, integration, smoke, and E2E classification visible through `coverage-audit`. |
| RT-012 | Port remaining Python runtime behavior into Rust modules and CLI binaries, especially report extraction and remaining SARIF/report payload parity. |
| RT-013 | Keep Tauri shell thin by routing desktop behavior through shared Rust command handlers. |
| RT-014 | Retire Python packaging, pytest-only guidance, and FastAPI stack scaffolds after parity is complete. |
| RT-015 | Optimize Rust path for speed and reliability after the Python runtime path is no longer canonical. |

## Dependency Notes

Codemap dependency analysis currently identifies `scripts/tachi_parsers` as the highest-use legacy Python hub and `tests/scripts/init_sh_helpers.py` as the main remaining init-test helper hub. Rust work should avoid expanding those hubs and should instead move behavior into `tachi-core` or `tachi-shell` with Rust tests.

## Agent Guidance

- Before changing code, read this file and the relevant Rust module/test files.
- Prefer small TDD slices with one retired Python surface per commit.
- Use `.worktrees/` for isolated branches; it is ignored by git.
- Treat roadmap documents under `docs/roadmap/` as the canonical migration status.
- Keep `README.md` at repository root and move non-root Markdown documentation under `docs/` unless it is standard project metadata.
