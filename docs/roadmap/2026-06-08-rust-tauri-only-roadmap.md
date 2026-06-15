# Rust/Tauri Implementation Roadmap

**Last Updated**: 2026-06-14
**Status**: Active implementation backlog
**Objective**: make `tachi-rust` a Rust + Tauri only repository through
Beads-ready execution slices

## Executive Summary

This roadmap is the canonical sequencing document for the Rust/Tauri-only
transition. It keeps the existing roadmap artifacts as the source of truth,
adds a navigation hub in [implementation-backlog.md](./implementation-backlog.md),
and expands the backlog into a Beads-ready hierarchy that can be executed one
TDD slice at a time.

The work is intentionally ordered:

1. Safety and parser hardening first.
1. Developer experience, packaging, and onboarding second.
1. Reporting, outputs, and rule-engine expansion third.
1. Ecosystem integrations and framework coverage fourth.
1. Performance, streaming, and formal assurance last.

The roadmap does not treat any stage as complete until its validation gate is
passed and the next stage can begin without reopening the previous one.

## Backlog Shape

The backlog is organized as:

`Epic -> Feature -> Capability -> Task -> Function`

- `Epic` captures the migration outcome.
- `Feature` groups work by crate or user-facing concern.
- `Capability` states the behavior that must exist.
- `Task` is the smallest TDD-driven slice.
- `Function` is the concrete function, command, fixture, or test seam.

The Beads-ready template for each task lives in
[implementation-backlog.md](./implementation-backlog.md).

## Stage Plan

| Stage | Focus | Exit criterion |
|---|---|---|
| Stage 0 | Inventory and contract freeze | Every active parser, command, output, and documentation surface is mapped to an owner, a dependency, and a test seam before new implementation work starts. |
| Stage 1 | Safety and parser hardening | User-facing parsing paths fail deterministically, malformed Mermaid/PlantUML/C4 inputs are covered by fixtures, and no parse-path panic remains. |
| Stage 2 | Developer experience, packaging, and onboarding | Cargo-first installation, CLI ergonomics, completions, and onboarding docs reflect the real Rust/Tauri workflow without Python packaging assumptions. |
| Stage 3 | Reporting, outputs, and rule-engine expansion | Report payloads, scoring, taxonomy, and output shapes are stable under fixtures and snapshot-style checks. |
| Stage 4 | Ecosystem integrations and framework coverage | Shared command dispatch, desktop bridge behavior, and framework-facing integrations stay parity-aligned. |
| Stage 5 | Performance, streaming, and formal assurance | Benchmark gates, invariant checks, and regression proofs protect the hardened Rust-only path from performance or behavior drift. |

Do not start a later stage until the current stage has satisfied its exit
criterion and the relevant validation matrix.

## TDD Policy

- Write the failing test before production code.
- Verify red before green.
- Keep each slice minimal until it passes.
- Validate at the function, task, capability, feature, and epic levels.
- Prefer small, mergeable Beads items over broad change sets.
- Re-run the progressive validation after every slice, not only at the end of a
  stage.

## Validation Matrix

| Work type | Proof required | Typical test seam |
|---|---|---|
| Parser work | Unit tests plus integration fixtures | Parser modules and malformed fixture sets |
| CLI and config work | Command-level tests plus config parsing tests | `tachi-cli` entrypoints |
| Tauri work | Bridge parity tests plus desktop smoke checks | `src-tauri` command registration |
| Reporting work | Output-shape checks plus snapshot-style regression tests | `tachi-core` builders |
| Ecosystem work | Cross-component parity checks | `tachi-shell` and `src-tauri` bridge paths |
| Performance work | Benchmark or criterion gate | Hot-path functions and regressions |
| Docs work | Readability, consistency, and link checks | Roadmap and onboarding docs |

## Dependency Rules

- Parser hardening must land before rule-engine expansion.
- CLI config stability must land before completions and release packaging work.
- Reporting and output contracts must stabilize before integrations that rely
  on those artifacts.
- Ecosystem integrations must stay behind the shared shell and desktop bridge.
- Performance and formal assurance come last, after behavioral contracts are
  stable.
- Capture dependencies at the feature or capability level whenever possible.
  Do not mirror every internal call edge in Beads.

## Beads Issue Template

Use this copy-paste format for each task-sized Beads issue:

```md
Epic:
Feature:
Capability:
Task:
Function:
Dependencies:
Acceptance criteria:
Validation:
Implementation owner:
Stage label:
Next test seam:
Notes:
```

## Epic 1 - Rust Safety and Parser Hardening

**Primary owner**: `tachi-core`
**Stage**: Stage 1

### Feature 1.1 - Diagram parser boundary safety

| Capability | Tasks | Functions |
|---|---|---|
| Mermaid, PlantUML, C4, and related diagram inputs reject malformed content without panicking. | Add failing fixtures for malformed and partially valid diagrams; replace `unwrap()` / `expect()` on the parse path with `Result` propagation; assert deterministic failure surfaces. | `parse_mermaid_block`, `parse_plantuml_block`, `parse_c4_block`, `parse_diagram_input` |
| Parser failure responses include explicit source, span, and recovery context. | Normalize parse errors; surface the exact input section that failed; keep bridge and CLI error text stable for diagnostics. | `map_parse_error`, `normalize_parse_span`, `render_parse_diagnostic` |

### Feature 1.2 - Panic-free user-facing parsing paths

| Capability | Tasks | Functions |
|---|---|---|
| User-facing parse paths stop using panic-based control flow. | Audit parse entry points for `unwrap()` and `expect()`; move fatal assumptions into tests; keep the command layer from swallowing parse errors. | `assert_no_parse_panic`, `parse_input_or_error`, `route_parse_error` |
| Shell and CLI propagation preserves parser failures as structured errors. | Thread parse results through `tachi-shell` and `tachi-cli`; avoid lossy conversion into generic exits; verify the same error is visible from every caller. | `map_error`, `serialize_payload`, `deserialize_input` |

### Feature 1.3 - Parser fixtures and contract coverage

| Capability | Tasks | Functions |
|---|---|---|
| The fixture corpus covers malformed, empty, nested, and edge-case parser inputs. | Add regression fixtures for each supported diagram flavor; cover mixed encodings and partial blocks; lock the failure behavior with snapshots. | `assert_fixture_roundtrip`, `assert_parser_contract`, `assert_parse_failure` |
| Parser contract tests prove deterministic behavior across the supported inputs. | Add red/green tests for grammar boundaries; verify the same fixture fails or succeeds consistently; keep the contract cases small and focused. | `validate_parser_contract`, `render_contract_snapshot`, `compare_parse_output` |

## Epic 2 - Developer Experience, Packaging, and Onboarding

**Primary owners**: `tachi-cli`, docs
**Stage**: Stage 2

### Feature 2.1 - CLI config and completion ergonomics

| Capability | Tasks | Functions |
|---|---|---|
| CLI config loading is explicit and predictable. | Add tests for config defaults, overrides, and invalid values; keep environment and file resolution stable; document the config precedence. | `load_cli_config`, `resolve_workspace_root`, `normalize_cli_flags` |
| Shell completions and help text stay synchronized with the CLI surface. | Generate completions from the real command set; verify help text examples against current flags; keep the command surface discoverable. | `generate_completions`, `render_help_text`, `list_cli_commands` |

### Feature 2.2 - Cargo-first packaging and bootstrap flow

| Capability | Tasks | Functions |
|---|---|---|
| Workspace build and bootstrap paths use the Rust toolchain as the canonical install path. | Remove Python packaging assumptions from the active path; make build/test/bootstrap commands work from Cargo entrypoints; lock down release packaging checks. | `cargo build`, `cargo test`, `cargo run` |
| Packaging behavior is documented against the actual workspace layout. | Align install, update, and bootstrap docs with the Rust workspace; keep release notes and onboarding examples current; verify that the documented path matches the shell. | `validate_packaging_contract`, `render_bootstrap_steps`, `check_release_manifest` |

### Feature 2.3 - Onboarding and documentation

| Capability | Tasks | Functions |
|---|---|---|
| Onboarding docs describe the Rust/Tauri workflow without legacy Python guidance. | Refresh quickstarts and README-level examples; point readers at the new backlog index; keep the examples executable. | `update_onboarding_docs`, `render_quickstart`, `link_roadmap_docs` |
| Troubleshooting guidance matches the actual command behavior. | Add command-specific error examples; document the expected output on failure; keep the docs aligned with the CLI and Tauri bridge. | `document_failure_modes`, `write_troubleshooting_note`, `verify_doc_examples` |

## Epic 3 - Reporting, Outputs, and Rule-Engine Expansion

**Primary owner**: `tachi-core`
**Stage**: Stage 3

### Feature 3.1 - Report payloads and output contracts

| Capability | Tasks | Functions |
|---|---|---|
| Report-data and infographic payloads stay schema-stable under fixture-driven tests. | Add output-shape tests; keep serialization stable; verify the same input produces the same report payloads across runs. | `build_report_payload`, `build_infographic_payload`, `assert_output_shape` |
| File writing and output selection stay deterministic. | Cover output-path handling; validate stdout versus file writes; keep the write contract small enough to test with fixtures. | `write_report_output`, `select_output_target`, `compare_snapshot_output` |

### Feature 3.2 - Taxonomy, scoring, and coverage catalog

| Capability | Tasks | Functions |
|---|---|---|
| Taxonomy normalization stays centralized in Rust. | Expand taxonomy tests; verify label normalization and family mapping; keep the reporting path and catalog path in sync. | `normalize_taxonomy_label`, `load_coverage_catalog`, `lookup_taxonomy_family` |
| Scoring and coverage classification remain reproducible. | Add fixture coverage for scoring and coverage classification; lock boundary cases; keep the output stable enough for downstream consumers. | `score_threat`, `classify_coverage_family`, `render_coverage_summary` |

### Feature 3.3 - Rule-engine and schema expansion

| Capability | Tasks | Functions |
|---|---|---|
| New rule families can be added without breaking the existing report contract. | Add fixtures for new family mappings; preserve the current output shape; keep the rule-engine extension points explicit. | `classify_rule_family`, `map_rule_crosswalk`, `expand_rule_set` |
| Shared schema validation covers the new and existing reporting families. | Assert schema integrity for report outputs; verify integration with the scoring and taxonomy layers; keep the failure mode explicit. | `validate_report_schema`, `assert_schema_integrity`, `compare_rule_output` |

## Epic 4 - Ecosystem Integrations and Framework Coverage

**Primary owners**: `tachi-shell`, `src-tauri`
**Stage**: Stage 4

### Feature 4.1 - Shared shell dispatch and runtime bridge

| Capability | Tasks | Functions |
|---|---|---|
| CLI and desktop callers use the same Rust command layer. | Keep dispatch, serialization, and error mapping in `tachi-shell`; add parity tests for CLI and desktop callers; avoid duplicate business logic in the adapters. | `route_command`, `serialize_payload`, `deserialize_input` |
| Shared errors preserve the same meaning across runtimes. | Standardize error mapping; keep command failures readable and deterministic; make the shell the source of truth for bridge behavior. | `map_error`, `normalize_command_result`, `format_runtime_error` |

### Feature 4.2 - Thin desktop shell parity

| Capability | Tasks | Functions |
|---|---|---|
| The Tauri shell stays thin and registration-only. | Keep `src-tauri` focused on command registration and bootstrap; refuse to add business logic there; validate the command surface through tests. | `register_commands`, `run_desktop_app`, `invoke_tauri_command` |
| Desktop smoke checks cover the smallest business-critical flow set. | Add smoke coverage for the minimum desktop round-trips; keep the harness narrow; verify the shell forwards through the shared layer. | `assert_desktop_roundtrip`, `check_bridge_parity`, `validate_command_state` |

### Feature 4.3 - Framework and ecosystem coverage

| Capability | Tasks | Functions |
|---|---|---|
| Ecosystem integrations are proved against framework-facing fixtures. | Add targeted fixtures for supported integrations; keep input/output contracts stable; ensure the shared shell remains the integration point. | `validate_integration_fixture`, `assert_bridge_parity`, `route_framework_command` |
| Framework coverage stays explicit in docs and tests. | Document the supported integration surfaces; keep the test matrix readable; refuse to hide unsupported cases behind implicit behavior. | `document_framework_coverage`, `render_integration_matrix`, `verify_integration_docs` |

## Epic 5 - Performance, Streaming, and Formal Assurance

**Primary owners**: `tachi-core`, `tachi-shell`, docs
**Stage**: Stage 5

### Feature 5.1 - Hot-path performance and streaming

| Capability | Tasks | Functions |
|---|---|---|
| Hot paths are measured before they are optimized. | Add benchmarks for startup, parsing, and command latency; identify repeated scans and process spawns; keep the benchmark fixtures stable. | `measure_startup_time`, `measure_command_latency`, `track_allocations` |
| Large outputs can stream when that reduces overhead. | Reduce avoidable buffering; keep the reporting path memory-aware; validate that the streaming behavior still matches the output contract. | `stream_report_output`, `write_stream_chunk`, `flush_output_buffer` |

### Feature 5.2 - Failure observability and exit discipline

| Capability | Tasks | Functions |
|---|---|---|
| Errors are structured and actionable across the CLI and desktop paths. | Standardize the error shape; keep exit codes deterministic; make user-facing diagnostics specific enough to act on. | `normalize_error`, `classify_exit_code`, `log_actionable_failure` |
| Failure handling is observable in tests. | Add regression tests for expected error modes; keep the command layer from collapsing distinct failures into one generic response. | `assert_failure_mode`, `render_failure_case`, `compare_exit_behavior` |

### Feature 5.3 - Formal assurance and regression gates

| Capability | Tasks | Functions |
|---|---|---|
| Benchmarks become part of the release gate. | Record the benchmark thresholds; keep performance regression checks in the repo; refuse to merge a slowdown without an explicit review. | `assert_regression_budget`, `run_criterion_benchmark`, `record_benchmark_baseline` |
| Invariants and contract tests protect the hardened path. | Add property tests or invariants where they buy confidence; keep the contracts narrow; verify that the behavior remains reproducible. | `verify_contract_invariants`, `compare_regression_fixture`, `assert_behavioral_invariant` |

## Execution Notes

- Start with Stage 0 inventory work and do not begin implementation slices
  until the inventory is frozen.
- Keep each Beads item small enough to complete in one TDD loop.
- Use the issue pack for tracker-neutral baselines and the issue cards for
  concrete task templates.
- Re-check the roadmap and issue-card pointers whenever the backlog changes so
  the navigation hub stays current.
