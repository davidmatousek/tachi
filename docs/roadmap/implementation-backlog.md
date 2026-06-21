# Implementation Backlog

**Last Updated**: 2026-06-15
**Purpose**: navigation hub for the Beads-ready Rust/Tauri implementation backlog
**Scope**: roadmap sequencing, issue-pack pointers, and task-template guidance

## Active Execution

- [Rust/Tauri Parity Remediation Roadmap](./2026-06-15-rust-tauri-parity-remediation-roadmap.html.md)
- [Rust/Tauri Parity Issue Cards](./2026-06-15-rust-tauri-parity-issue-cards.md)
- [Beads issue mirror snapshot](./.beads/issues.jsonl)

## Current Status Snapshot

- Open: none
- Partial: RT-015
- Done: RT-010, RT-011, RT-012, RT-013, RT-014, RT-016, RT-017, RT-018, RT-019, RT-020, RT-021, RT-022

## Archive Records

- [Rust/Tauri Migration Issue Pack](./2026-06-04-rust-tauri-issue-pack.md)
- [Rust/Tauri Implementation Roadmap](./2026-06-08-rust-tauri-only-roadmap.md)
- [Rust/Tauri Implementation Issue Cards](./2026-06-08-rust-tauri-only-issue-cards.md)

## Canonical Sources

- [Rust/Tauri parity remediation roadmap](./2026-06-15-rust-tauri-parity-remediation-roadmap.html.md)
- [Rust/Tauri parity issue cards](./2026-06-15-rust-tauri-parity-issue-cards.md)
- [Rust/Tauri migration issue pack](./2026-06-04-rust-tauri-issue-pack.md)

The active roadmap is the canonical sequencing document. The issue cards are
the copy-paste execution templates that become Beads issues. The archived issue
pack remains the tracker-neutral historical baseline.

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
