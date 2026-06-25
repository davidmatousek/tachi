# Standalone MCP Server Issue Cards

**Last Updated**: 2026-06-25  
**Status**: active execution blueprint for Beads

These cards are TDD-first and include explicit, measurable acceptance criteria.
Every card maps directly to a Beads issue ID.

### Stage 0 - Scope boundary (MCP transport-safe surface)

- In-scope for MCP (analysis-first): `coverage-audit`, `infographic-data`,
  `report-data`, `risk-scores-sarif`, `threats-sarif`
- Out-of-scope for MCP: `install`, `init`, `update`, `bootstrap` (control-plane)
  and Tauri/CLI bridge glue (validation, invocation transport, desktop UX state)

## Card format

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
- `Priority`
- `Notes`

## Stage 0 - Contract extraction and parity lock

### MCP-001 - Standalone MCP server for tachi core

- `Epic`: Build a standalone MCP server that preserves the canonical command and output contract.
- `Feature`: N/A
- `Capability`: Establish protocol-neutral model contracts before tool implementation.
- `Task`: create the migration contract and acceptance gates that all MCP work must satisfy.
- `Function`: command registry snapshot, contract schema, fixture generator
- `Dependencies`: none
- `Acceptance criteria`:
  - Command contract fixture includes command name, command kind, argument schema, output type, and stable artifact path.
  - A minimal diff tool detects accidental contract drift for command set and output names.
  - Contract fixture is versioned and can be re-generated from source in less than 60 seconds.
- `Validation`: `cargo test -p tachi-shell --test command_contract`, dedicated contract tests
- `Implementation owner`: `docs`
- `Stage label`: Stage 0
- `Next test seam`: `crates/tachi-shell/tests/command_contract.rs`
- `Priority`: 0
- `Notes`: This epic holds all MCP work until contract lock is green.

## Stage 1 - MCP transport + tool surface

### MCP-001.1 - Contract reuse and tool mapping layer

- `Epic`: MCP-001
- `Feature`: Canonical contract extraction and reuse
- `Capability`: Zero-logic wrapper layer from command registry to MCP tool schema
- `Task`: keep MCP tool definitions generated from the canonical command registry and keep command behavior identical to existing adapters.
- `Function`: `crates/tachi-shell/src/commands.rs`, `crates/tachi-shell/src/command_use_cases.rs`, `adapters/` contract outputs
- `Dependencies`: MCP-001
- `Acceptance criteria`:
  - Adding a new command in the canonical registry requires changing one source file and one MCP contract snapshot, not multiple ad-hoc wrappers.
  - Tool surface and command list are identical for all analysis commands at any commit.
  - New tool definitions compile with stable, typed schemas and one canonical argument source.
- `Validation`: contract diff tests + `cargo test -p tachi-shell`
- `Implementation owner`: `tachi-shell`
- `Stage label`: Stage 1
- `Next test seam`: `crates/tachi-shell/src/commands.rs`
- `Priority`: 0
- `Notes`: Start with one-to-one adapter for `report-data` and `risk-scores-sarif` before adding the remaining commands.

### MCP-001.1 task beads

- `MCP-001.1.1` Contract snapshot extraction and schema versioning
  - Acceptance: a JSON schema contract fixture exists, includes command metadata and output types, includes `version`, and fails if a required field changes without fixture update.
  - Validation: snapshot tests in `crates/tachi-shell/tests/command_contract.rs`.
- `MCP-001.1.2` Generate MCP input/output schemas from command contract
  - Acceptance: one generated schema per command tool with strict input validation and explicit required/optional boundaries; invalid payloads fail before command invocation.
  - Validation: schema unit tests in `crates/tachi-mcp`.
- `MCP-001.1.3` Contract regression suite for CLI/Tauri parity
  - Acceptance: command contract snapshot + CLI and Tauri golden assertions remain green when MCP tool definitions are regenerated from source.
  - Validation: `cargo test -p tachi-core --test command_regression`, `cargo test -p tachi-shell --test command_registry`.

### MCP-001.2 - Standalone MCP crate and tool registration

- `Epic`: MCP-001
- `Feature`: MCP transport and tool layer
- `Capability`: protocol runtime and tool registration
- `Task`: add MCP crate entrypoints, server startup path, and tool handler mapping.
- `Function`: `crates/tachi-mcp/src/lib.rs`, `crates/tachi-mcp/src/server.rs`, `crates/tachi-mcp/src/stdio.rs`
- `Dependencies`: MCP-001, MCP-001.1
- `Acceptance criteria`:
  - MCP tools `tachi.coverage-audit`, `tachi.infographic-data`, `tachi.report-data`,
    `tachi.risk-scores-sarif`, and `tachi.threats-sarif` are registered and callable.
  - One successful tool call writes an artifact in expected canonical path and returns artifact metadata.
  - Tool registration includes explicit allowlisting and no dynamic untyped dispatch path.
- `Validation`: integration test in `crates/tachi-mcp/tests/tools_registration.rs`
- `Implementation owner`: `tachi-mcp`
- `Stage label`: Stage 1
- `Next test seam`: `crates/tachi-mcp/src/lib.rs`
- `Priority`: 0
- `Notes`: This is the first shipping code slice after Stage 0.

### MCP-001.2 task beads

- `MCP-001.2.1` Scaffold MCP crate and stdio transport
  - Acceptance: `tachi-mcp` crate builds as part of workspace and accepts a single `--stdio` startup mode.
- `MCP-001.2.2` Register tool handlers from contract
  - Acceptance: each registered MCP handler maps exactly one-to-one to canonical command execution functions for analysis commands.
- `MCP-001.2.3` Output mode negotiation for artifacts
  - Acceptance: tool response can request in-band JSON result or canonical filesystem artifact path, and both are validated against output-kind metadata.

### MCP-001.3 - Session model and transport hardening

- `Epic`: MCP-001
- `Feature`: MCP governance and runtime hardening
- `Capability`: transport, session lifecycle, and policy control
- `Task`: enforce per-request policy, validate session context, and prevent unsafe execution.
- `Function`: `crates/tachi-mcp/src/session.rs`, `crates/tachi-mcp/src/policy.rs`, auth/session middleware
- `Dependencies`: MCP-001.2
- `Acceptance criteria`:
  - Every tool call has a validated request-id and stable error code.
- Validation: session/authorization integration tests in `crates/tachi-mcp/tests/session_policy.rs`.
- `Implementation owner`: `tachi-mcp`
- `Stage label`: Stage 1
- `Next test seam`: `crates/tachi-mcp/src/session.rs`
- `Priority`: 1
- `Notes`: Keep auth optional in Stage 1 if deployment model is local-only, but policy seams remain explicit.

### MCP-001.3 task beads

- `MCP-001.3.1` Request correlation and cancellation
  - Acceptance: correlation ID is required, carried through tool context, and appears in logs for both success and failure within 10ms in test mode.
- `MCP-001.3.2` Policy allowlist and tool-level authorization guard
  - Acceptance: unknown tool calls return authorization error code and do not invoke execution paths.
- `MCP-001.3.3` Timeout and cancellation propagation
  - Acceptance: long-running tool calls can be cancelled and cleanup callbacks execute without file lock leaks.

## Stage 2 - Security parity and compatibility boundaries

### MCP-001.4 - Release and docs integration

- `Epic`: MCP-001
- `Feature`: Artifact, docs, and release readiness
- `Capability`: operational documentation and packaging parity with existing release gates
- `Task`: add MCP install and runtime docs, include MCP in BOM and publish checklists, wire minimal CI checks.
- `Function`: `README.md`, `docs/platform-compatibility.md`, `docs/guides/DEVELOPER_GUIDE_TACHI.md`, `docs/bill-of-materials.html.md`, `docs/publish-readiness-checklist.html.md`, `.github/workflows/*.yml`
- `Dependencies`: MCP-001.1, MCP-001.2, MCP-001.3
- `Acceptance criteria`:
  - README and developer guide each include MCP install and usage examples with command names unchanged.
  - BOM includes MCP artifact and release checks.
  - Publish checklist requires MCP evidence before release.
- `Validation`: `make publish-gate`, docs lint checks if configured.
- `Implementation owner`: `docs`
- `Stage label`: Stage 2
- `Next test seam`: `docs/guides/DEVELOPER_GUIDE_TACHI.md`
- `Priority`: 1
- `Notes`: This stage must be complete before merge of production MCP code.

### MCP-001.4 task beads

- `MCP-001.4.1` Publish README + platform docs
  - Acceptance: at least three docs are updated consistently (public README, developer guide, platform compatibility) with identical command names and output file names.
- `MCP-001.4.2` BOM + publish-checklist alignment
  - Acceptance: release docs list MCP artifacts and the new MCP validation command(s), with no stale references to unsupported harnesses.
- `MCP-001.4.3` CI evidence lane for MCP
  - Acceptance: one deterministic MCP tool-call test runs in CI and blocks merge on failure.

### MCP-001.5 - Portability envelope and fallback documentation

- `Epic`: MCP-001
- `Feature`: Porting limits and fallback behavior
- `Capability`: documented non-portable capabilities and fallback statement
- `Task`: produce a stable matrix of what is fully portable, partially portable, or not portable to MCP.
- `Function`: `docs/README`, `docs/platform-compatibility.md`, `docs/platform-compatibility.md`
- `Dependencies`: MCP-001.4
- `Acceptance criteria`:
  - Each capability has one of: fully-portable / adapter-only / non-portable status.
  - Fallback behavior for non-portable cases includes a practical alternative path.
  - Matrix is reviewed in issue card and stored in roadmap document.
- `Validation`: manual doc review plus roadmap/issue sync check.
- `Implementation owner`: `docs`
- `Stage label`: Stage 2
- `Next test seam`: `docs/platform-compatibility.md`
- `Priority`: 2
- `Notes`: This card can open while code slices run; it must land before release sign-off.
