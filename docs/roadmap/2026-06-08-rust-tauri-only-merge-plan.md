# Rust/Tauri-Only Migration Merge Plan

**Last Updated**: 2026-06-08
**Status**: Merge-ready
**Scope**: translate the Rust/Tauri-only roadmap into a staged merge sequence

## Purpose

This document turns the Rust/Tauri-only migration roadmap into a concrete pull-request and commit sequence. It is intended to keep the migration incremental, reviewable, and easy to validate while the remaining Python surfaces are removed.

## Proposed PR Shape

**Title**

`docs(roadmap): publish Rust/Tauri-only migration plan and merge sequence`

**Summary**

Publish the fine-grained migration roadmap, the issue-card expansion, and the merge sequence for the Python-to-Rust transition. The docs establish the BEADS hierarchy, phase gates, and coverage floor that future implementation work must satisfy.

**Validation**

- `git diff --check`
- `cargo test -q`
- `make llvm-cov`
- targeted doc-contract tests for the roadmap and issue pack

## Commit Sequence

Keep the sequence small and conventional so each step is easy to review and revert if needed.

### Commit 1

`docs(roadmap): add rust-tauri-only migration roadmap`

Adds the canonical BEADS roadmap under `docs/roadmap/` with phase ordering, validation gates, coverage floor, and the Python-to-Rust inventory map.

### Commit 2

`docs(roadmap): add rust-tauri-only issue cards`

Adds the execution-level backlog cards (RT-010 through RT-015) that break the roadmap into mergeable phase slices.

### Commit 3

`docs(roadmap): expand rust-tauri issue pack pointers`

Updates the issue pack and product-roadmap summary files so they point at the new canonical roadmap and stay synchronized with the active migration narrative.

### Commit 4

`docs(changelog): record rust-tauri-only migration roadmap`

Adds the changelog entry that records the roadmap publication and the 80% Rust-native coverage floor.

### Commit 5

`test(docs): lock roadmap and issue-pack contract`

Adds or updates the doc contract test that checks the roadmap status, issue-pack pointer, and migration framing.

## Rollout Order

1. Land the roadmap doc.
2. Land the issue-card set.
3. Land the pointer updates.
4. Land the changelog note.
5. Land the doc contract test.
6. Start the P0 worktree for inventory and test migration.

## Exit Criteria

- The roadmap points to Rust/Tauri-only implementation and validation.
- The issue pack and product roadmap agree on the canonical roadmap path.
- The merge sequence is explicit enough that future implementation work can proceed in small, reviewable slices.
- The next worktree can start from a clearly scoped P0 inventory and test-migration baseline.
