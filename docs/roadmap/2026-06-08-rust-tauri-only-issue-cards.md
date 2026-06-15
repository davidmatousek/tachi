# Rust/Tauri Implementation Issue Cards

**Last Updated**: 2026-06-14
**Status**: Beads-ready execution backlog derived from the implementation roadmap
**Source**: [2026-06-08-rust-tauri-only-roadmap.md](./2026-06-08-rust-tauri-only-roadmap.md)

These cards are the task-sized execution slices for the roadmap in
[implementation-backlog.md](./implementation-backlog.md). They are intentionally
small, owner-aligned, and ready to copy into Beads.

## Card Format

Every card includes:

- `Epic`
- `Feature`
- `Capability bundle`
- `Task`
- `Function`
- `Dependencies`
- `Acceptance criteria`
- `Validation`
- `Implementation owner`
- `Stage label`
- `Next test seam`
- `Notes`

## Epic 1 - Rust Safety and Parser Hardening

### RB-1.1 - Diagram parser boundary safety

- `Epic`: Epic 1 - Rust Safety and Parser Hardening
- `Feature`: Feature 1.1 - Diagram parser boundary safety
- `Capability bundle`: malformed Mermaid, PlantUML, C4, and related diagram inputs
- `Task`: add red fixtures, replace panic-based parse flow, and return structured parse errors
- `Function`: `parse_mermaid_block`, `parse_plantuml_block`, `parse_c4_block`, `parse_diagram_input`
- `Dependencies`: Stage 0 inventory freeze; parser fixture directories
- `Acceptance criteria`:
  - Malformed diagram input fails deterministically.
  - No parse-path panic remains on the user-facing path.
  - The fixture set covers malformed and partially valid inputs.
- `Validation`:
  - Unit tests for parser helpers.
  - Integration fixtures for malformed graph inputs.
  - Snapshot or golden-file checks for failure text.
- `Implementation owner`: `tachi-core`
- `Stage label`: Stage 1
- `Next test seam`: `crates/tachi-core/src/parsers/mermaid.rs`
- `Notes`: Keep the failure surface explicit enough for CLI and desktop callers.

### RB-1.2 - Parse error diagnostics

- `Epic`: Epic 1 - Rust Safety and Parser Hardening
- `Feature`: Feature 1.1 - Diagram parser boundary safety
- `Capability bundle`: explicit source, span, and recovery context for parse failures
- `Task`: normalize parser errors and preserve the failing section in diagnostics
- `Function`: `map_parse_error`, `normalize_parse_span`, `render_parse_diagnostic`
- `Dependencies`: RB-1.1
- `Acceptance criteria`:
  - Parse errors include source and span context.
  - The same malformed input produces the same diagnostic text.
  - Recovery hints remain stable across CLI and shell callers.
- `Validation`:
  - Parser contract tests.
  - Diagnostic snapshot checks.
- `Implementation owner`: `tachi-core`
- `Stage label`: Stage 1
- `Next test seam`: `crates/tachi-core/src/parsers/findings.rs`
- `Notes`: Keep the diagnostic wording small and deterministic.

### RB-1.3 - Panic-free parse propagation

- `Epic`: Epic 1 - Rust Safety and Parser Hardening
- `Feature`: Feature 1.2 - Panic-free user-facing parsing paths
- `Capability bundle`: `unwrap()` / `expect()` audit on parse entry points
- `Task`: move panic-based assumptions into test fixtures and typed errors
- `Function`: `assert_no_parse_panic`, `parse_input_or_error`, `route_parse_error`
- `Dependencies`: RB-1.1, RB-1.2
- `Acceptance criteria`:
  - User-facing parse paths no longer rely on panic control flow.
  - The failing cases are covered by tests instead of runtime assertions.
  - Any fatal assumption has an explicit error mapping.
- `Validation`:
  - Unit tests around parse helpers.
  - Integration tests for parse failure propagation.
- `Implementation owner`: `tachi-core`
- `Stage label`: Stage 1
- `Next test seam`: `crates/tachi-core/src/parsers/table.rs`
- `Notes`: Keep this slice narrow so failures remain easy to localize.

### RB-1.4 - Shell and CLI parse error propagation

- `Epic`: Epic 1 - Rust Safety and Parser Hardening
- `Feature`: Feature 1.2 - Panic-free user-facing parsing paths
- `Capability bundle`: structured parse failures survive `tachi-shell` and `tachi-cli`
- `Task`: thread parse results through the command layer without collapsing them into generic exits
- `Function`: `map_error`, `serialize_payload`, `deserialize_input`
- `Dependencies`: RB-1.3
- `Acceptance criteria`:
  - CLI and shell callers see the same parser failure meaning.
  - Parse errors are not downgraded into ambiguous command failures.
  - The command layer keeps the parser context intact.
- `Validation`:
  - Command-level tests for failure propagation.
  - End-to-end parse-failure smoke checks.
- `Implementation owner`: `tachi-shell`
- `Stage label`: Stage 1
- `Next test seam`: `crates/tachi-shell/src/commands.rs`
- `Notes`: Keep the adapter thin; do not add parser logic here.

### RB-1.5 - Parser fixture matrix

- `Epic`: Epic 1 - Rust Safety and Parser Hardening
- `Feature`: Feature 1.3 - Parser fixtures and contract coverage
- `Capability bundle`: malformed, empty, nested, and edge-case parser inputs
- `Task`: expand the fixture corpus and lock the failure behavior with snapshots
- `Function`: `assert_fixture_roundtrip`, `assert_parser_contract`, `assert_parse_failure`
- `Dependencies`: RB-1.1, RB-1.2
- `Acceptance criteria`:
  - The fixture corpus covers the supported diagram families.
  - Each regression fixture has a known success or failure outcome.
  - The fixture behavior is deterministic across runs.
- `Validation`:
  - Fixture-driven integration tests.
  - Snapshot comparison for parser output and failure text.
- `Implementation owner`: `tachi-core`
- `Stage label`: Stage 1
- `Next test seam`: `tests/fixtures/`
- `Notes`: Add edge cases that proved brittle in prior parser work.

### RB-1.6 - Parser contract tests

- `Epic`: Epic 1 - Rust Safety and Parser Hardening
- `Feature`: Feature 1.3 - Parser fixtures and contract coverage
- `Capability bundle`: deterministic parse contracts across the supported inputs
- `Task`: add red/green tests for grammar boundaries and compare parse output stability
- `Function`: `validate_parser_contract`, `render_contract_snapshot`, `compare_parse_output`
- `Dependencies`: RB-1.5
- `Acceptance criteria`:
  - Contract tests cover supported and malformed inputs.
  - The same fixture yields the same parse result over time.
  - The contract failures are explicit and reproducible.
- `Validation`:
  - Contract tests.
  - Golden output checks.
- `Implementation owner`: `tachi-core`
- `Stage label`: Stage 1
- `Next test seam`: `crates/tachi-core/tests/`
- `Notes`: Keep the contract boundaries narrow enough for fast iteration.

## Epic 2 - Developer Experience, Packaging, and Onboarding

### RB-2.1 - CLI config ergonomics

- `Epic`: Epic 2 - Developer Experience, Packaging, and Onboarding
- `Feature`: Feature 2.1 - CLI config and completion ergonomics
- `Capability bundle`: explicit, predictable config loading
- `Task`: add tests for defaults, overrides, and invalid values
- `Function`: `load_cli_config`, `resolve_workspace_root`, `normalize_cli_flags`
- `Dependencies`: Stage 0 inventory freeze
- `Acceptance criteria`:
  - Config precedence is documented and tested.
  - Invalid config values fail with actionable errors.
  - Workspace resolution stays stable.
- `Validation`:
  - Command-level tests.
  - Config parsing tests.
- `Implementation owner`: `tachi-cli`
- `Stage label`: Stage 2
- `Next test seam`: `crates/tachi-cli/src/bin/`
- `Notes`: Keep the config surface consistent across commands.

### RB-2.2 - CLI completions and help

- `Epic`: Epic 2 - Developer Experience, Packaging, and Onboarding
- `Feature`: Feature 2.1 - CLI config and completion ergonomics
- `Capability bundle`: completions and help text stay synchronized
- `Task`: generate completions from the actual command set and verify help examples
- `Function`: `generate_completions`, `render_help_text`, `list_cli_commands`
- `Dependencies`: RB-2.1
- `Acceptance criteria`:
  - Completions match the real command surface.
  - Help text examples are executable and current.
  - No command remains undocumented in the CLI surface.
- `Validation`:
  - Completion generation check.
  - Help text snapshot check.
- `Implementation owner`: `tachi-cli`
- `Stage label`: Stage 2
- `Next test seam`: `crates/tachi-cli/src/bin/`
- `Notes`: Treat completion generation as part of the shipping contract.

### RB-2.3 - Cargo-first packaging

- `Epic`: Epic 2 - Developer Experience, Packaging, and Onboarding
- `Feature`: Feature 2.2 - Cargo-first packaging and bootstrap flow
- `Capability bundle`: Rust workspace install, build, test, and bootstrap flow
- `Task`: remove Python packaging assumptions from the canonical path and verify Cargo-based commands
- `Function`: `cargo build`, `cargo test`, `cargo run`, `validate_packaging_contract`
- `Dependencies`: Stage 0 inventory freeze
- `Acceptance criteria`:
  - The workspace docs and packaging path are Cargo-first.
  - Bootstrap instructions point at the real Rust entrypoints.
  - No active doc still implies Python packaging as the default path.
- `Validation`:
  - Build and test commands.
  - Packaging contract checks.
- `Implementation owner`: docs
- `Stage label`: Stage 2
- `Next test seam`: `docs/roadmap/`
- `Notes`: Keep the wording aligned with the actual repo layout.

### RB-2.4 - Packaging and bootstrap docs

- `Epic`: Epic 2 - Developer Experience, Packaging, and Onboarding
- `Feature`: Feature 2.2 - Cargo-first packaging and bootstrap flow
- `Capability bundle`: install, update, and bootstrap docs reflect the Rust workspace
- `Task`: align the onboarding and release docs with the real shell and CLI behavior
- `Function`: `render_bootstrap_steps`, `check_release_manifest`, `link_roadmap_docs`
- `Dependencies`: RB-2.3
- `Acceptance criteria`:
  - The documented path matches the actual build/bootstrap path.
  - Release-manifest guidance is up to date.
  - The roadmap and issue-card links are current.
- `Validation`:
  - Docs consistency review.
  - Link checks.
- `Implementation owner`: docs
- `Stage label`: Stage 2
- `Next test seam`: `docs/roadmap/implementation-backlog.md`
- `Notes`: Prefer short examples that match current command names.

### RB-2.5 - Onboarding docs

- `Epic`: Epic 2 - Developer Experience, Packaging, and Onboarding
- `Feature`: Feature 2.3 - Onboarding and documentation
- `Capability bundle`: quickstart and README examples describe the Rust/Tauri workflow
- `Task`: refresh the onboarding docs and examples to match the actual workflow
- `Function`: `update_onboarding_docs`, `render_quickstart`, `verify_doc_examples`
- `Dependencies`: RB-2.3, RB-2.4
- `Acceptance criteria`:
  - The quickstart does not require legacy Python guidance.
  - The examples are executable against the current workspace.
  - The docs point readers at the backlog hub.
- `Validation`:
  - Readability and consistency review.
  - Example command spot checks.
- `Implementation owner`: docs
- `Stage label`: Stage 2
- `Next test seam`: `README.md`
- `Notes`: Keep onboarding terse and action-oriented.

### RB-2.6 - Troubleshooting guidance

- `Epic`: Epic 2 - Developer Experience, Packaging, and Onboarding
- `Feature`: Feature 2.3 - Onboarding and documentation
- `Capability bundle`: troubleshooting notes match real command behavior
- `Task`: document command-specific failure modes and expected outputs
- `Function`: `document_failure_modes`, `write_troubleshooting_note`, `verify_doc_examples`
- `Dependencies`: RB-2.5
- `Acceptance criteria`:
  - Troubleshooting examples match actual command output.
  - The failure-mode wording is specific and reproducible.
  - The docs do not hide unsupported behavior.
- `Validation`:
  - Doc review.
  - Example output verification.
- `Implementation owner`: docs
- `Stage label`: Stage 2
- `Next test seam`: `docs/roadmap/`
- `Notes`: Keep the support burden low by being precise.

## Epic 3 - Reporting, Outputs, and Rule-Engine Expansion

### RB-3.1 - Report payload stability

- `Epic`: Epic 3 - Reporting, Outputs, and Rule-Engine Expansion
- `Feature`: Feature 3.1 - Report payloads and output contracts
- `Capability bundle`: report-data and infographic payloads stay schema-stable
- `Task`: add output-shape tests and keep serialization stable
- `Function`: `build_report_payload`, `build_infographic_payload`, `assert_output_shape`
- `Dependencies`: Stage 0 inventory freeze
- `Acceptance criteria`:
  - The same input produces the same payload shape.
  - The report builders remain fixture-driven.
  - The schema stays stable for downstream consumers.
- `Validation`:
  - Unit tests.
  - Snapshot-style output checks.
- `Implementation owner`: `tachi-core`
- `Stage label`: Stage 3
- `Next test seam`: `crates/tachi-core/src/report_data.rs`
- `Notes`: Keep the payload shape boring and predictable.

### RB-3.2 - Report output selection

- `Epic`: Epic 3 - Reporting, Outputs, and Rule-Engine Expansion
- `Feature`: Feature 3.1 - Report payloads and output contracts
- `Capability bundle`: stdout versus file writes stay deterministic
- `Task`: cover output-path handling and selection logic
- `Function`: `write_report_output`, `select_output_target`, `compare_snapshot_output`
- `Dependencies`: RB-3.1
- `Acceptance criteria`:
  - Output target selection is explicit.
  - File writes and stdout paths are covered by tests.
  - The behavior does not vary by environment.
- `Validation`:
  - Integration tests.
  - File output comparison.
- `Implementation owner`: `tachi-core`
- `Stage label`: Stage 3
- `Next test seam`: `crates/tachi-core/src/infographic.rs`
- `Notes`: Keep file-path handling simple enough to snapshot.

### RB-3.3 - Taxonomy normalization

- `Epic`: Epic 3 - Reporting, Outputs, and Rule-Engine Expansion
- `Feature`: Feature 3.2 - Taxonomy, scoring, and coverage catalog
- `Capability bundle`: taxonomy normalization stays centralized in Rust
- `Task`: expand taxonomy tests and keep the reporting path in sync with the catalog
- `Function`: `normalize_taxonomy_label`, `load_coverage_catalog`, `lookup_taxonomy_family`
- `Dependencies`: RB-3.1
- `Acceptance criteria`:
  - Taxonomy labels normalize consistently.
  - The coverage catalog is the source of truth.
  - The reporting path and catalog path agree on families.
- `Validation`:
  - Unit tests.
  - Catalog lookup tests.
- `Implementation owner`: `tachi-core`
- `Stage label`: Stage 3
- `Next test seam`: `crates/tachi-core/src/coverage_taxonomy.rs`
- `Notes`: Keep the normalized names easy to reason about.

### RB-3.4 - Scoring and coverage classification

- `Epic`: Epic 3 - Reporting, Outputs, and Rule-Engine Expansion
- `Feature`: Feature 3.2 - Taxonomy, scoring, and coverage catalog
- `Capability bundle`: scoring and coverage classification stay reproducible
- `Task`: add fixture coverage for scoring and coverage classification
- `Function`: `score_threat`, `classify_coverage_family`, `render_coverage_summary`
- `Dependencies`: RB-3.3
- `Acceptance criteria`:
  - Scoring outputs are reproducible.
  - Coverage classification is stable for the supported families.
  - Boundary cases have explicit coverage.
- `Validation`:
  - Integration fixtures.
  - Snapshot-style summary checks.
- `Implementation owner`: `tachi-core`
- `Stage label`: Stage 3
- `Next test seam`: `crates/tachi-core/src/risk_scores.rs`
- `Notes`: Keep the score model easy to audit.

### RB-3.5 - Rule-engine expansion

- `Epic`: Epic 3 - Reporting, Outputs, and Rule-Engine Expansion
- `Feature`: Feature 3.3 - Rule-engine and schema expansion
- `Capability bundle`: new rule families can be added without breaking current reports
- `Task`: add fixtures for new family mappings and preserve the current output shape
- `Function`: `classify_rule_family`, `map_rule_crosswalk`, `expand_rule_set`
- `Dependencies`: RB-3.3, RB-3.4
- `Acceptance criteria`:
  - New families integrate without changing the stable output contract.
  - Existing families continue to pass their fixtures.
  - The rule-engine extension points remain explicit.
- `Validation`:
  - Integration fixtures.
  - Crosswalk consistency tests.
- `Implementation owner`: `tachi-core`
- `Stage label`: Stage 3
- `Next test seam`: `crates/tachi-core/src/threats_sarif.rs`
- `Notes`: Prefer a small extension point over a complicated dynamic rule graph.

### RB-3.6 - Schema validation for reporting families

- `Epic`: Epic 3 - Reporting, Outputs, and Rule-Engine Expansion
- `Feature`: Feature 3.3 - Rule-engine and schema expansion
- `Capability bundle`: shared schema validation covers the expanded reporting families
- `Task`: assert schema integrity across the reporting outputs
- `Function`: `validate_report_schema`, `assert_schema_integrity`, `compare_rule_output`
- `Dependencies`: RB-3.5
- `Acceptance criteria`:
  - The schema tests cover the new and existing families.
  - The failure mode is explicit and reproducible.
  - The output remains consumable by downstream code.
- `Validation`:
  - Schema validation tests.
  - Output comparison checks.
- `Implementation owner`: `tachi-core`
- `Stage label`: Stage 3
- `Next test seam`: `crates/tachi-core/tests/`
- `Notes`: Keep the schema assertions close to the builder surface.

## Epic 4 - Ecosystem Integrations and Framework Coverage

### RB-4.1 - Shared shell dispatch

- `Epic`: Epic 4 - Ecosystem Integrations and Framework Coverage
- `Feature`: Feature 4.1 - Shared shell dispatch and runtime bridge
- `Capability bundle`: CLI and desktop callers share the same Rust command layer
- `Task`: keep dispatch, serialization, and error mapping in `tachi-shell`
- `Function`: `route_command`, `serialize_payload`, `deserialize_input`
- `Dependencies`: Stage 0 inventory freeze; RB-3.2
- `Acceptance criteria`:
  - CLI and desktop callers reach the same command layer.
  - The adapters do not duplicate business logic.
  - Dispatch semantics remain stable across runtimes.
- `Validation`:
  - Command parity tests.
  - Shared shell integration tests.
- `Implementation owner`: `tachi-shell`
- `Stage label`: Stage 4
- `Next test seam`: `crates/tachi-shell/src/commands.rs`
- `Notes`: Keep the shell as the single shared adapter layer.

### RB-4.2 - Shared error semantics

- `Epic`: Epic 4 - Ecosystem Integrations and Framework Coverage
- `Feature`: Feature 4.1 - Shared shell dispatch and runtime bridge
- `Capability bundle`: errors preserve the same meaning across runtimes
- `Task`: standardize error mapping and runtime formatting
- `Function`: `map_error`, `normalize_command_result`, `format_runtime_error`
- `Dependencies`: RB-4.1
- `Acceptance criteria`:
  - The same error has the same meaning in CLI and desktop paths.
  - Command failures remain deterministic.
  - The shell owns the shared error shape.
- `Validation`:
  - Error mapping tests.
  - Failure text comparison.
- `Implementation owner`: `tachi-shell`
- `Stage label`: Stage 4
- `Next test seam`: `crates/tachi-shell/src/tauri_bridge.rs`
- `Notes`: Avoid hiding useful context inside generic wrappers.

### RB-4.3 - Thin desktop shell

- `Epic`: Epic 4 - Ecosystem Integrations and Framework Coverage
- `Feature`: Feature 4.2 - Thin desktop shell parity
- `Capability bundle`: Tauri shell stays registration-only
- `Task`: keep `src-tauri` focused on command registration and bootstrap
- `Function`: `register_commands`, `run_desktop_app`, `invoke_tauri_command`
- `Dependencies`: RB-4.1, RB-4.2
- `Acceptance criteria`:
  - `src-tauri` contains no duplicated business logic.
  - Command registration stays thin.
  - Desktop bootstrap is covered by tests.
- `Validation`:
  - Desktop smoke checks.
  - Bridge registration tests.
- `Implementation owner`: `src-tauri`
- `Stage label`: Stage 4
- `Next test seam`: `src-tauri/src/lib.rs`
- `Notes`: Keep desktop-specific code at the edges only.

### RB-4.4 - Desktop smoke coverage

- `Epic`: Epic 4 - Ecosystem Integrations and Framework Coverage
- `Feature`: Feature 4.2 - Thin desktop shell parity
- `Capability bundle`: the minimum desktop round-trips are covered
- `Task`: add smoke coverage for the business-critical desktop command set
- `Function`: `assert_desktop_roundtrip`, `check_bridge_parity`, `validate_command_state`
- `Dependencies`: RB-4.3
- `Acceptance criteria`:
  - The smallest critical desktop flow set is covered.
  - The shell forwards through the shared layer.
  - The smoke tests stay cheap enough to run often.
- `Validation`:
  - Desktop smoke tests.
  - Bridge parity checks.
- `Implementation owner`: `src-tauri`
- `Stage label`: Stage 4
- `Next test seam`: `src-tauri/tests/`
- `Notes`: Resist the urge to broaden the UI scope here.

### RB-4.5 - Framework integration fixtures

- `Epic`: Epic 4 - Ecosystem Integrations and Framework Coverage
- `Feature`: Feature 4.3 - Framework and ecosystem coverage
- `Capability bundle`: integration fixtures represent the supported framework surfaces
- `Task`: add targeted fixtures for supported integrations and keep the input/output contracts stable
- `Function`: `validate_integration_fixture`, `assert_bridge_parity`, `route_framework_command`
- `Dependencies`: RB-4.3, RB-4.4
- `Acceptance criteria`:
  - The supported integration surfaces are covered by fixtures.
  - Unsupported cases are not hidden behind implicit behavior.
  - The shared shell remains the integration point.
- `Validation`:
  - Integration fixture tests.
  - Bridge parity tests.
- `Implementation owner`: `tachi-shell`
- `Stage label`: Stage 4
- `Next test seam`: `tests/fixtures/`
- `Notes`: Keep the fixtures representative rather than exhaustive.

### RB-4.6 - Framework coverage docs

- `Epic`: Epic 4 - Ecosystem Integrations and Framework Coverage
- `Feature`: Feature 4.3 - Framework and ecosystem coverage
- `Capability bundle`: framework coverage stays explicit in docs and tests
- `Task`: document the supported integration surfaces and keep the matrix readable
- `Function`: `document_framework_coverage`, `render_integration_matrix`, `verify_integration_docs`
- `Dependencies`: RB-4.5
- `Acceptance criteria`:
  - The documentation names the supported surfaces directly.
  - The matrix stays synchronized with the tests.
  - Unsupported behavior is called out explicitly.
- `Validation`:
  - Doc review.
  - Link and example checks.
- `Implementation owner`: docs
- `Stage label`: Stage 4
- `Next test seam`: `docs/roadmap/`
- `Notes`: Make the integration story easy to audit.

## Epic 5 - Performance, Streaming, and Formal Assurance

### RB-5.1 - Hot-path measurement

- `Epic`: Epic 5 - Performance, Streaming, and Formal Assurance
- `Feature`: Feature 5.1 - Hot-path performance and streaming
- `Capability bundle`: startup, parsing, and command latency are measured before optimization
- `Task`: add benchmarks for the main hot paths and capture the current baseline
- `Function`: `measure_startup_time`, `measure_command_latency`, `track_allocations`
- `Dependencies`: Stage 3 reporting stabilization
- `Acceptance criteria`:
  - The current baseline is measured.
  - The benchmark fixtures are stable.
  - Regressions can be detected from the repo.
- `Validation`:
  - Benchmark or criterion gate.
  - Regression comparison.
- `Implementation owner`: `tachi-core`
- `Stage label`: Stage 5
- `Next test seam`: `crates/tachi-core/benches/`
- `Notes`: Measure before tuning.

### RB-5.2 - Streaming output

- `Epic`: Epic 5 - Performance, Streaming, and Formal Assurance
- `Feature`: Feature 5.1 - Hot-path performance and streaming
- `Capability bundle`: large outputs can stream when that reduces overhead
- `Task`: reduce avoidable buffering and keep the streaming behavior aligned with the output contract
- `Function`: `stream_report_output`, `write_stream_chunk`, `flush_output_buffer`
- `Dependencies`: RB-5.1
- `Acceptance criteria`:
  - Streaming behavior preserves the output contract.
  - Large output paths avoid unnecessary buffering.
  - The write contract remains deterministic.
- `Validation`:
  - Integration tests.
  - Output comparison checks.
- `Implementation owner`: `tachi-core`
- `Stage label`: Stage 5
- `Next test seam`: `crates/tachi-core/src/report_data.rs`
- `Notes`: Keep the streaming path simple enough to reason about.

### RB-5.3 - Structured failures

- `Epic`: Epic 5 - Performance, Streaming, and Formal Assurance
- `Feature`: Feature 5.2 - Failure observability and exit discipline
- `Capability bundle`: errors are structured and actionable across CLI and desktop paths
- `Task`: standardize the error shape, exit codes, and user-facing diagnostics
- `Function`: `normalize_error`, `classify_exit_code`, `log_actionable_failure`
- `Dependencies`: RB-4.2
- `Acceptance criteria`:
  - The same failure yields the same exit classification.
  - Diagnostics remain specific enough to act on.
  - The command layer does not collapse distinct errors into one code path.
- `Validation`:
  - Failure mode tests.
  - Exit-code checks.
- `Implementation owner`: `tachi-shell`
- `Stage label`: Stage 5
- `Next test seam`: `crates/tachi-shell/src/commands.rs`
- `Notes`: Actionable errors are part of the product contract.

### RB-5.4 - Failure observability tests

- `Epic`: Epic 5 - Performance, Streaming, and Formal Assurance
- `Feature`: Feature 5.2 - Failure observability and exit discipline
- `Capability bundle`: failure handling is observable in tests
- `Task`: add regression tests for expected error modes and compare exit behavior
- `Function`: `assert_failure_mode`, `render_failure_case`, `compare_exit_behavior`
- `Dependencies`: RB-5.3
- `Acceptance criteria`:
  - Failure modes have explicit test coverage.
  - Distinct failures do not collapse into one response.
  - The tests guard against accidental behavior drift.
- `Validation`:
  - Regression tests.
  - Exit behavior comparison.
- `Implementation owner`: `tachi-shell`
- `Stage label`: Stage 5
- `Next test seam`: `src-tauri/tests/`
- `Notes`: Keep the negative cases as intentional as the positive ones.

### RB-5.5 - Benchmark gates

- `Epic`: Epic 5 - Performance, Streaming, and Formal Assurance
- `Feature`: Feature 5.3 - Formal assurance and regression gates
- `Capability bundle`: benchmark thresholds become part of the release gate
- `Task`: record the benchmark thresholds and keep performance regression checks in the repo
- `Function`: `assert_regression_budget`, `run_criterion_benchmark`, `record_benchmark_baseline`
- `Dependencies`: RB-5.1, RB-5.2
- `Acceptance criteria`:
  - The benchmark gate is recorded in the repo.
  - Slowdowns require explicit review.
  - The baseline is easy to compare against.
- `Validation`:
  - Criterion or benchmark check.
  - Regression budget comparison.
- `Implementation owner`: `tachi-core`
- `Stage label`: Stage 5
- `Next test seam`: `crates/tachi-core/benches/`
- `Notes`: Make the baseline cheap to update and hard to ignore.

### RB-5.6 - Contract invariants

- `Epic`: Epic 5 - Performance, Streaming, and Formal Assurance
- `Feature`: Feature 5.3 - Formal assurance and regression gates
- `Capability bundle`: invariants and contract tests protect the hardened path
- `Task`: add property tests or invariants where they improve confidence and keep the contracts narrow
- `Function`: `verify_contract_invariants`, `compare_regression_fixture`, `assert_behavioral_invariant`
- `Dependencies`: RB-5.5
- `Acceptance criteria`:
  - The invariant checks are explicit and reproducible.
  - The contracts cover the high-risk behavior.
  - Regression fixtures guard the agreed baseline.
- `Validation`:
  - Contract tests.
  - Regression fixture comparison.
- `Implementation owner`: `tachi-core`
- `Stage label`: Stage 5
- `Next test seam`: `crates/tachi-core/tests/`
- `Notes`: Prefer narrow invariants over broad assertions.

## Execution Order

1. Stage 0 inventory and contract freeze.
1. Stage 1 safety and parser hardening.
1. Stage 2 developer experience, packaging, and onboarding.
1. Stage 3 reporting, outputs, and rule-engine expansion.
1. Stage 4 ecosystem integrations and framework coverage.
1. Stage 5 performance, streaming, and formal assurance.

## Validation Gate

Each card must pass its local unit, integration, and stage-specific validation
before the next card starts. The stage exit criterion is the merge gate, not the
presence of a written template.
