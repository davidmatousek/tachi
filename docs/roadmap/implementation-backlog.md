# Implementation Backlog

**Last Updated**: 2026-06-14
**Purpose**: navigation hub for the Beads-ready Rust/Tauri implementation backlog
**Scope**: roadmap sequencing, issue-pack pointers, and task-template guidance

## Canonical Sources

- [Rust/Tauri implementation roadmap](./2026-06-08-rust-tauri-only-roadmap.md)
- [Rust/Tauri migration issue pack](./2026-06-04-rust-tauri-issue-pack.md)
- [Rust/Tauri implementation cards](./2026-06-08-rust-tauri-only-issue-cards.md)

The roadmap is the canonical sequencing document. The issue pack is the
tracker-neutral backlog baseline. The issue cards are the copy-paste execution
templates that become Beads issues.

## Backlog Shape

Work is organized as:

`Epic -> Feature -> Capability -> Task -> Function`

- `Epic` states the migration outcome.
- `Feature` groups the work by crate or user-facing concern.
- `Capability` defines the behavior that must exist.
- `Task` is the smallest TDD-driven slice that can be completed and validated.
- `Function` names the concrete function, command, fixture, or test seam.

## Stage Map

1. Stage 0: inventory and contract freeze
1. Stage 1: safety and parser hardening
1. Stage 2: developer experience, packaging, and onboarding
1. Stage 3: reporting, outputs, and rule-engine expansion
1. Stage 4: ecosystem integrations and framework coverage
1. Stage 5: performance, streaming, and formal assurance

Each stage is a hard gate. Do not start the next stage until the current stage
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

- Safety and parser hardening must land before rule-engine expansion.
- CLI config stability must land before completions and release packaging work.
- Reporting and output contracts must stabilize before ecosystem integrations
  that consume those artifacts.
- Performance and formal assurance are last, after behavioral contracts are
  stable.
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

1. Read the roadmap to understand the intended sequencing.
1. Use the issue pack for tracker-neutral backlog context.
1. Copy a task template from the issue cards into Beads.
1. Execute the task with TDD and validate the stage gate before advancing.
