# Rust/Tauri Parity Capability Matrix

Status: discovery artifact

Scope: compare the current `tachi-rust` surface against the sibling
`/Volumes/dev/Git-SCM/tachi` repository for the parity rebaseline.

This document is the working output for RT-024. It captures the current
capability inventory and the gap signals that should be turned into the next
parity follow-up cards.

## Current reading

The current `tachi-rust` branch is already ahead of the earlier parity track:

- Registry diff, fixture contracts, normalization, bridge validation, parser
  regressions, release parity, and CI modernization are all already closed in
  the active mirror.
- The active backlog now reopens parity as a rebaseline against the sibling
  `tachi` repository, then pushes beyond that baseline with Rust/Tauri-only
  desktop capabilities.

The sibling `tachi` repository still shows older GitHub Actions pins in its
workflows from the current scan:

- `actions/checkout@v4` remains present in multiple workflow files.
- `github/codeql-action/upload-sarif@v3` remains present in the gitleaks
  workflow.
- `actions-rs/toolchain@v1` remains present in the historical workflow surface.

That means the parity rebaseline is not a copy of the old migration track.
It is a new comparison pass against a repo that still carries older workflow
versions and older CI conventions in its own active surface.

## Comparison matrix

| Surface | `tachi-rust` current state | `tachi` scan signal | RT-024 implication |
|---|---|---|---|
| Command registry | CLI and Tauri bridge share a diff harness and registry parity tests. | No equivalent Rust/Tauri bridge target was identified in the workflow/docs scan. | Use the existing registry harness as the comparison anchor. |
| Fixture contracts | Versioned command I/O fixtures and hash validation are already in place. | Sibling scan did not reveal an equivalent fixture contract. | Keep the fixture schema as the parity baseline for new slices. |
| Desktop bridge | Typed Tauri input/output validation exists. | Sibling scan still highlights historical Python-era workflow assumptions. | Treat typed bridge validation as a Rust/Tauri-only differentiator. |
| Release gates | Publish gate, release artifact parity, and workflow hardening are already tracked in the repo. | Sibling workflows still show older checkout and SARIF pins. | Rebaseline release expectations against modern CI only. |
| Docs hygiene | Active docs-sweep roadmap exists to keep old workflow pins out of maintained docs. | Sibling repo still carries older workflow pin references in active docs/workflows. | Keep docs hygiene separate from runtime parity. |
| Examples | Current scan found no stale workflow-version pins under `examples/`. | The sibling repo scan is still heavily saturated with older workflow references. | Preserve the current examples clean state and gate regressions. |

## Discovery gaps to turn into work

1. Rebaseline the sibling capability matrix into a deterministic artifact so the
   next parity slices have a stable source of truth.
2. Turn the matrix into the RT-025 command-surface drift harness expectation.
3. Keep the fixture corpus and typed bridge work aligned to the rebaseline
   instead of the older migration-era roadmap.
4. Keep the docs/version sweep separate so documentation hygiene does not
   dilute the parity track.

## Evidence notes

- `tachi-rust` current roadmap and Beads mirror now point at:
  - RT-024 through RT-030 for the parity/supersession track.
  - DOC-001 through DOC-004 for the docs/version sweep track.
- The sibling repo scan was limited to the workflow/docs surfaces that expose
  high-signal version drift. It is enough to justify the parity rebaseline, but
  not enough to replace a full implementation diff.

## Next step

Convert this matrix into:

1. A deterministic inventory artifact for RT-024.
2. The expected surface list for RT-025.
3. A reconciliation note in the roadmap/issue cards when the matrix is
   stabilized.
