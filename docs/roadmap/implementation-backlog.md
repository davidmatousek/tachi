# Implementation Backlog

**Last Updated**: 2026-06-25
**Purpose**: navigation hub for the Beads-ready Rust/Tauri implementation backlog
**Scope**: roadmap sequencing, issue-pack pointers, and task-template guidance

## Active Execution

- [Beads issue mirror snapshot](./.beads/issues.jsonl)
- [AISVS Dependabot remediation roadmap](./2026-06-23-aisvs-dependabot-remediation-roadmap.html.md)
- [Standalone MCP server roadmap](./2026-06-25-standalone-mcp-server-roadmap.html.md)
- [Standalone MCP server issue cards](./2026-06-25-standalone-mcp-server-issue-cards.md)

## Current Status Snapshot

- Open: AQ-010, AQ-020, AQ-051, AQ-052, AQ-053, AQ-054, MCP-001, MCP-001.3, MCP-001.3.2, MCP-001.3.3, MCP-001.4, MCP-001.4.1, MCP-001.4.2, MCP-001.4.3, MCP-001.5, MCP-001.5.1
- Partial: AQ-021, AQ-022, AQ-023, AQ-024, AQ-025
- Done: AQ-001, AQ-011, AQ-012, AQ-013, AQ-030, AQ-031, AQ-032, AQ-033, AQ-034, AQ-040, AQ-041, AQ-042, AQ-043, AQ-050, AQ-055, DOC-001, DOC-002, DOC-003, DOC-004, RT-010, RT-011, RT-012, RT-013, RT-014, RT-015, RT-016, RT-017, RT-018, RT-019, RT-020, RT-021, RT-022, RT-023, RT-024, RT-025, RT-026, RT-027, RT-028, RT-029, RT-030

## Archive Records

- [Adversarial Architecture and Test Quality Roadmap](./2026-06-22-adversarial-architecture-test-quality-roadmap.html.md)
- [Rust/Tauri Parity Remediation Roadmap](./2026-06-21-rust-tauri-parity-remediation-roadmap.html.md)
- [Rust/Tauri Parity Issue Cards](./2026-06-21-rust-tauri-parity-issue-cards.md)
- [Archived Docs Workflow-Version Inventory](./2026-06-21-archived-docs-workflow-version-inventory.md)
- [Archived Docs Workflow-Version Sweep Roadmap](./2026-06-21-archived-docs-workflow-version-sweep-roadmap.html.md)
- [Archived Docs Workflow-Version Sweep Issue Cards](./2026-06-21-archived-docs-workflow-version-sweep-issue-cards.md)
- [Rust/Tauri Migration Issue Pack](./2026-06-04-rust-tauri-issue-pack.md)
- [Rust/Tauri Implementation Roadmap](./2026-06-08-rust-tauri-only-roadmap.md)
- [Rust/Tauri Implementation Issue Cards](./2026-06-08-rust-tauri-only-issue-cards.md)
- [Standalone MCP Server Roadmap](./2026-06-25-standalone-mcp-server-roadmap.html.md)
- [Standalone MCP Server Issue Cards](./2026-06-25-standalone-mcp-server-issue-cards.md)

## Active Security Track

- [AISVS Dependabot remediation issue cards](./2026-06-23-aisvs-dependabot-remediation-issue-cards.md)
- Epic: `RT-00i` AISVS framework and Dependabot remediation
- Feature issues: `RT-00i.1` typed AISVS control registry, `RT-00i.2` glib/tauri remediation, `RT-00i.3` AISVS C01-C04, `RT-00i.4` AISVS C09-C12, `RT-00i.5` AISVS C05-C08
- Feature issues: `RT-00i.6` CI and docs readiness for AISVS framework
- Decision issues: `RT-00i.7` gtk/glib compatibility decision for Dependabot alert (closed decision note)
- Task issues: `RT-00i.1.1` control registry, `RT-00i.1.2` sanitized errors, `RT-00i.1.3` Send+Sync invariants, `RT-00i.2.1` reproduce advisory proof, `RT-00i.2.2` fixed glib upgrade, `RT-00i.2.3` closure evidence, `RT-00i.2.4` future gtk/glib recheck, `RT-00i.6.1` docs and export sync

## Standalone MCP Track

- [Standalone MCP server roadmap](./2026-06-25-standalone-mcp-server-roadmap.html.md)
- [Standalone MCP server issue cards](./2026-06-25-standalone-mcp-server-issue-cards.md)
- Epic: `MCP-001` Standalone MCP server
- Feature issues: `MCP-001.1` canonical contract extraction, `MCP-001.2` MCP transport and tool layer, `MCP-001.3` transport runtime hardening, `MCP-001.4` docs and release integration, `MCP-001.5` portability envelope
- Task issues: `MCP-001.3.1` correlation and cancellation, `MCP-001.3.2` auth guard, `MCP-001.3.3` cleanup and timeout, `MCP-001.4.1` docs publish alignment, `MCP-001.4.2` BOM/release alignment, `MCP-001.4.3` CI evidence lane, `MCP-001.5.1` portability matrix
- Code state: `crates/tachi-mcp` now implements the Stage 0 contract snapshot plus schema metadata snapshot, and the Stage 1 transport/tool layer; the current ready issues are the runtime hardening and release/docs follow-ups.

## Canonical Sources

- [Adversarial Architecture and Test Quality Roadmap](./2026-06-22-adversarial-architecture-test-quality-roadmap.html.md)
- [Adversarial Architecture and Test Quality Issue Cards](./2026-06-22-adversarial-architecture-test-quality-issue-cards.md)
- [AISVS Dependabot remediation roadmap](./2026-06-23-aisvs-dependabot-remediation-roadmap.html.md)
- [AISVS Dependabot remediation issue cards](./2026-06-23-aisvs-dependabot-remediation-issue-cards.md)
- [Rust/Tauri parity remediation roadmap](./2026-06-21-rust-tauri-parity-remediation-roadmap.html.md)
- [Rust/Tauri parity issue cards](./2026-06-21-rust-tauri-parity-issue-cards.md)
- [Standalone MCP Server Roadmap](./2026-06-25-standalone-mcp-server-roadmap.html.md)
- [Standalone MCP Server Issue Cards](./2026-06-25-standalone-mcp-server-issue-cards.md)
- [Archived Docs Workflow-Version Sweep Roadmap](./2026-06-21-archived-docs-workflow-version-sweep-roadmap.html.md)
- [Archived Docs Workflow-Version Sweep Issue Cards](./2026-06-21-archived-docs-workflow-version-sweep-issue-cards.md)
- [Rust/Tauri migration issue pack](./2026-06-04-rust-tauri-issue-pack.md)

The active roadmap is the canonical sequencing document. The issue cards are
the copy-paste execution templates that become Beads issues. The archived issue
pack remains the tracker-neutral historical baseline. Completed roadmap slices
move into archive records once their tracker cards are done.

## Backlog Shape

Work is organized as:

`Epic -> Feature -> Capability -> Task -> Function`

- `Epic` states the migration outcome.
- `Feature` groups the work by crate or user-facing concern.
- `Capability` defines the behavior that must exist.
- `Task` is the smallest TDD-driven slice that can be completed and validated.
- `Function` names the concrete function, command, fixture, or test seam.

## Stage Map

1. Phase 0: parity harness
1. Phase 1: critical parity closure
1. Phase 2: output contract parity
1. Phase 3: CI and release hardening
1. Phase 4: exceed `tachi`

Each phase is a hard gate. Do not start the next phase until the current phase
has passed its exit criteria and validation matrix.

## TDD Policy

- Write the failing test before the production change.
- Verify the test fails for the intended reason before editing code.
- Keep the implementation slice minimal until the test passes.
- Validate the slice at the function, task, capability, feature, and epic
  levels.
- Repeat the red -> green -> refactor cycle for every slice.
- Do not batch unrelated work into a single Beads item.

## Validation Matrix

| Work type | Minimum proof | Preferred seam |
|---|---|---|
| Parser work | Unit tests plus integration fixtures | Parser module and malformed fixture set |
| CLI and config work | Command-level tests plus config parsing tests | `tachi-cli` entrypoints |
| Tauri work | Bridge parity tests plus desktop smoke checks | `src-tauri` command registration |
| Reporting work | Output-shape checks plus snapshot-style regression tests | `tachi-core` builders |
| Performance work | Benchmark or criterion gate | Hot-path functions and regressions |
| Docs work | Readability, consistency, and link checks | Roadmap and onboarding docs |

## Dependency Rules

- Parity harness work must land before any bridge, output, or release-hardening
  slice.
- Tauri command exposure must land before schema validation and desktop-only UX.
- Output goldens and parser regression tests must stabilize before release
  artifact work.
- Release hardening must land before desktop-specific differentiators.
- Keep dependencies at the capability or feature level when possible. Do not
  create task graphs that mirror every internal callsite.

## Beads Issue Template

Use this format when converting roadmap slices into Beads issues:

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

## Usage Order

1. Read the active roadmap to understand the intended sequencing.
1. Use the issue cards for tracker-ready Beads issue text.
1. Use the archived issue pack only for provenance and historical context.
1. Execute the task with TDD and validate the phase gate before advancing.
