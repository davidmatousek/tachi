# Standalone MCP Server Roadmap

**Date**: 2026-06-25  
**Scope**: `tachi-rust` command surface, adapter contract, publish gates, and release posture  
**Execution model**: `$plan-review-integrator` style TDD, Beads issue graph, measured stage gates  
**Status**: active, multi-stage planning phase  
**Source context**: `docs/platform-compatibility.md`, `adapters/README.md`, `crates/tachi-shell/src/commands.rs`, `src-tauri/src/schema.rs`, `src-tauri/src/lib.rs`, `docs/standards/PUBLISHING_SECURITY.md`, `docs/bill-of-materials.html.md`, `docs/publish-readiness-checklist.html.md`

## Executive summary

A Stage 1 MCP transport now exists in `crates/tachi-mcp`. The current core threat
model logic and reporting contracts already exist and are adapter-agnostic in
practice. The remaining gap is transport/runtime hardening: keep exposing those
core commands as MCP tools without changing command semantics, output names, or
artifact contracts while request-context policy and future transport support land.

This roadmap converts the existing prompt-centric contract into a standalone MCP
server by layering a protocol adapter and execution runtime on top of existing
canonical command output contracts. Stage 1 has landed in code; Stage 2 and later
stages remain the active sequencing targets.

## Core capabilities to preserve

The MCP server must preserve these invariants for parity:

- Canonical command surface:
  `install`, `init`, `update`, `bootstrap`, `infographic-data`,
  `coverage-audit`, `report-data`, `risk-scores-sarif`, `threats-sarif`.
- Canonical command output contract:
  stable command names, deterministic filename roles (`threats.md`,
  `threats.sarif`, `threat-report.md`, `risk-score.md`, `infographic-data.json`,
  etc.).
- Canonical error taxonomy and policy codes used by CLI/Tauri flows.
- Deterministic schema validation and artifact path conventions from `INSTALL_MANIFEST.md`.
- Command dispatch and output formatting currently exercised by CLI/Tauri tests.

## Why this is MCP-safe by default

The current architecture is already suitable for MCP tool wrapping because:

- Inputs map to structured arguments (`CommandInput`) and command kinds are modelled.
- Outputs are typed and validated before rendering in CLI/desktop surfaces.
- Artifact generators are command-level functions with deterministic paths.
- No protocol-specific logic is required in threat model domain modules.

The server adds transport, session, and policy control; it should not alter core
threat logic.

## Logical stages

### Stage 0 - Contract extraction and migration contract

**Goal**: lock a transport-neutral payload contract that all future MCP tools must
reuse.

| Mapping | Value |
| --- | --- |
| Epic | `MCP-001` |
| Feature | `MCP-001.1` Canonical command/output contract extraction |
| Capability | `MCP-001.C0` Contract snapshot + parity harness |
| Tasks | `MCP-001.1.1`, `MCP-001.1.2`, `MCP-001.1.3` |
| Functions / seams | `crates/tachi-shell/src/commands.rs`, `crates/tachi-shell/src/command_use_cases.rs`, `crates/tachi-core/tests/*`, `crates/tachi-shell/tests/*` |

**Stage acceptance criteria**

- Command registry JSON contract is serializable, schema-versioned, and versioned at file level.
- At least one test fails when a command name/output kind/path is removed, changed, or added outside intended migration windows.
- Existing CLI/Tauri golden output tests remain green under unchanged command semantics.

### Stage 1 - MCP protocol adapter and command tools

**Goal**: expose the existing command surface as stable MCP tools with strict, typed
input/output schemas.

| Mapping | Value |
| --- | --- |
| Epic | `MCP-001` |
| Feature | `MCP-001.2` MCP transport and tool layer |
| Capability | `MCP-001.C1` Tool registry and typed payloads |
| Tasks | `MCP-001.2.1`, `MCP-001.2.2`, `MCP-001.2.3` |
| Functions / seams | `crates/*` and new `crates/tachi-mcp/*` crate entrypoints |

**Stage acceptance criteria**

- `threat_model`, `risk_score`, `compensating_controls`, `architecture`, and `infographic` tools are registered and callable.
- Each MCP tool returns canonical command output in either raw payload mode or canonical
  filesystem artifact mode.
- Schema mismatch (invalid command, missing required args, unsupported output kind) fails with typed MCP errors mapped from the existing typed output/error model.
- One end-to-end integration test verifies a tool-driven call that starts with input and ends
  with a written artifact path in test-reproducible form.

**Status note**

Stage 1 transport/tool registration has landed in `crates/tachi-mcp`. The
current implementation already registers the analysis tools, supports stdio,
and preserves the canonical artifact contract. The next tracked slice is
`MCP-001.3.1` request correlation and cancellation.

### Stage 2 - Runtime control and security policy

**Goal**: add robust transport/session controls without changing threat logic semantics.

| Mapping | Value |
| --- | --- |
| Epic | `MCP-001` |
| Feature | `MCP-001.3` MCP governance and runtime hardening |
| Capability | `MCP-001.C2` Session, auth, authorization, and audit hardening |
| Tasks | `MCP-001.3.1`, `MCP-001.3.2`, `MCP-001.3.3` |
| Functions / seams | new MCP crate, policy module, logging crate hooks, error model adapters |

**Stage acceptance criteria**

- Transport supports both STDIO and future HTTP transport behind feature flags or a clean abstraction.
- Request schema validation, command allowlist, and per-tool authorization are enforced before executor entry.
- Correlation IDs propagate through logs and returned MCP output; at least one test captures request-id continuity.
- Unsafe inputs, oversized payloads, unknown tool invocations, and cancelled calls are covered by regression tests and return stable error codes.

### Stage 3 - Artifact parity, docs, and release gating

**Goal**: keep MCP parity and release confidence equal to existing CLI/Tauri outputs.

| Mapping | Value |
| --- | --- |
| Epic | `MCP-001` |
| Feature | `MCP-001.4` Artifacts, docs, and release-readiness integration |
| Capability | `MCP-001.C3` Docs and CI lockstep for standalone MCP |
| Tasks | `MCP-001.4.1`, `MCP-001.4.2`, `MCP-001.4.3` |
| Functions / seams | `docs/platform-compatibility.md`, `docs/guides/DEVELOPER_GUIDE_TACHI.md`, `Makefile`, publish docs, `.github/workflows` |

**Stage acceptance criteria**

- One canonical install recipe for MCP is documented with versioned command examples.
- Release checklist and BOM include MCP server artifacts and expected checks.
- `make publish-gate` is unchanged in strictness and includes MCP-specific evidence checks.
- All new MCP docs and schema changes are linted/validated in CI.

### Stage 4 - Capability envelope verification

**Goal**: prove what MCP can and cannot port from core in one place before shipping.

| Mapping | Value |
| --- | --- |
| Epic | `MCP-001` |
| Feature | `MCP-001.5` Portability limits and fallback behavior |
| Capability | `MCP-001.C4` Gaps documented and intentionally non-portable paths |
| Tasks | `MCP-001.5.1` |
| Functions / seams | `docs/README`, `README.md`, `platform-compatibility` docs |

**Stage acceptance criteria**

- A public matrix describes:
  - ported functions,
  - adapter-only behavior,
  - and deliberate non-ported behaviors.
- Unsupported harness assumptions are documented with fallback behavior in plain English and examples.

## MCP Scope Matrix (analysis-first split)

### Ported candidates (MCP tools/resources)

- `coverage-audit` → read-only summary from `crates/tachi-core/src/coverage_audit.rs`
- `infographic-data` → `build_infographic_payload` in `crates/tachi-core/src/infographic/payload.rs`
- `report-data` → `build_report_data_typst` in `crates/tachi-core/src/report_data.rs`
- `risk-scores-sarif` → `build_risk_scores_sarif` in `crates/tachi-core/src/risk_scores.rs`
- `threats-sarif` → `build_threats_sarif` in `crates/tachi-core/src/threats_sarif.rs`
- `aisvs registry` (resource) → `aisvs_registry` metadata in `crates/tachi-core/src/aisvs.rs`

### Excluded by design

- `install`, `init`, `update`, `bootstrap`: control-plane/bootstrap commands; keep in CLI/Tauri flow.
- `dispatch_command_with_progress`, `dispatch_*` helpers: transport bridge mechanics tied to CLI/Tauri runtime.
- `validate_invoke_input_typed`, `validate_invoke_output_typed`: adapter conformance checks, not MCP core contracts.
- `render_*` and path I/O wrappers: presentation and process glue, not semantic outputs.

## Gaps and non-portable limitations (initial baseline)

- Desktop-only Tauri UX flows cannot be replicated in MCP transport and should be
  represented as non-portable capability notes.
- Existing desktop offline bootstrap and local cache policy are likely to become
  client-level concerns rather than server invariants and require explicit docs.
- Current shell/path assumptions used by some CLI helpers require normalization layers
  when MCP clients do not execute on repository-root layout.
- Process control beyond command execution (interactive UI state, progress bar events
  in Tauri windows) needs either MCP progress notifications or explicit polling
  contracts to remain parity-safe.
- No direct GUI automation channel exists in MCP; any interactive desktop launch or
  browser-side preview path remains external to this server.

## Sequencing

1. Freeze the contract in Stage 0 and create a parser fixture that can be shared
   by CLI, Tauri, and MCP.
2. Implement MCP tool registration and argument validation in Stage 1 using strict,
   contract-driven tests.
3. Implement Stage 2 security and session controls before any release documentation.
4. Add Stage 3 docs, release docs, and CI gates.
5. Document Stage 4 gaps and publish final compatibility statement.

## Definition of done (for each `MCP-*` issue)

- Failing proof first, minimal fix second, focused refactor third.
- Measurable acceptance criterion includes:
  - one reproducible test,
  - one command-level validation path,
  - and one artifact assertion.
- Issue status only advances when the acceptance checks are red/green completed.
- `make publish-gate` remains green unless the issue explicitly redefines publish gates.
- Plan and tracker stay synchronized: roadmap, issue cards, and Beads IDs align.
