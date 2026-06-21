# Archived Docs Workflow-Version Sweep Issue Cards

**Last Updated**: 2026-06-21
**Status**: Beads-ready execution backlog for the archived docs sweep roadmap
**Source**: [2026-06-21-archived-docs-workflow-version-sweep-roadmap.html.md](./2026-06-21-archived-docs-workflow-version-sweep-roadmap.html.md)

These cards cover the docs-only cleanup of stale workflow-version mentions.
They are intentionally separate from the active CI surface and do not touch
`.github/workflows/*`.

## Current Status Snapshot

- Open: DOC-004
- Partial: none
- Done: DOC-001, DOC-002, DOC-003

## Phase 0 - inventory and classification

### DOC-001 - inventory stale workflow-version mentions

- `Epic`: archived docs hygiene
- `Capability`: documentation inventory
- `Task`: scan archived docs and examples for stale checkout, toolchain,
  SARIF, and Node 20 references and classify each hit
- `Function`: `rg` scan over `docs/` and `examples/`
- `Dependencies`: active docs sweep roadmap
- `Acceptance criteria`:
  - Every discovered hit has a disposition.
  - The examples tree is either clean or explicitly called out as clean.
  - The live workflow files are excluded from the sweep scope.
- `Validation`:
  - Inventory table matches the scan output.
  - No active CI file is included in the doc sweep.
- `Implementation owner`: `docs`
- `Stage label`: Phase 0
- `Next test seam`: `docs/testing/README.md`
- `Notes`: This is the intake step that separates maintained docs from frozen
  historical docs.
- `Notes`: Completed by `docs/roadmap/2026-06-21-archived-docs-workflow-version-inventory.md`.

## Phase 1 - maintained-doc updates

### DOC-002 - refresh maintained docs to current guidance

- `Epic`: archived docs hygiene
- `Capability`: documentation accuracy
- `Task`: update maintainer-facing docs and examples that still teach older
  checkout, toolchain, or SARIF upload pins
- `Function`: `docs/testing/README.md`, `docs/guides/DEVELOPER_GUIDE_TACHI.md`,
  `docs/devops/README.md`, `docs/devops/CI_CD_GUIDE.md`,
  `docs/standards/PRECOMMIT_HOOKS.md`, `docs/standards/GIT_WORKFLOW.md`,
  `docs/architecture/00_Tech_Stack/README.md`,
  `docs/architecture/01_system_design/README.md`
- `Dependencies`: DOC-001
- `Acceptance criteria`:
  - Maintained docs use current majors or version-neutral language.
  - No maintained doc teaches an obsolete workflow pin as current practice.
- `Validation`:
  - Targeted grep over the maintained-doc set returns no stale pins.
  - Diff review confirms the examples still read cleanly.
- `Implementation owner`: `docs`
- `Stage label`: Phase 1
- `Next test seam`: `docs/devops/CI_CD_GUIDE.md`
- `Notes`: Keep the edits minimal; do not broaden this into a prose rewrite.
- `Notes`: Completed; the maintained-doc scan now returns only intentional
  validation text in the BOM and publish checklist.

## Phase 2 - historical-doc annotation

### DOC-003 - label historical workflow-version references as archival

- `Epic`: archive provenance
- `Capability`: historical context
- `Task`: annotate frozen docs so versioned workflow references are clearly
  historical rather than current instructions
- `Function`: `docs/guides/CONSUMER_GUIDE_TACHI.md`,
  `docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md`,
  `docs/guides/CONSUMER_GUIDE_TACHI_AOD_INTEGRATION.md`,
  `docs/architecture/02_ADRs/ADR-013-sarif-output-format-adoption.md`,
  `docs/product/02_PRD/012-sarif-output-generation-2026-03-22.md`,
  `docs/product/02_PRD/021-platform-adapters-2026-03-23.md`
- `Dependencies`: DOC-001
- `Acceptance criteria`:
  - Historical docs preserve their original meaning.
  - Readers can tell those references are frozen snapshots.
  - Current workflow guidance is not implied by the archived snippet.
- `Validation`:
  - Spot-check the archival docs for explicit historical markers.
  - Link checks remain intact after annotation.
- `Implementation owner`: `docs`
- `Stage label`: Phase 2
- `Next test seam`: `docs/product/02_PRD/012-sarif-output-generation-2026-03-22.md`
- `Notes`: Preserve provenance; do not rewrite the historical record into a
  current-maintenance guide.
- `Notes`: Completed by adding archival callouts to the historical docs.

## Phase 3 - regression gate

### DOC-004 - add docs/examples workflow-version regression scan

- `Epic`: archive docs hygiene
- `Capability`: regression prevention
- `Task`: add a docs-only scan gate that covers archived docs and examples but
  excludes `.github/workflows/*`
- `Function`: docs/examples grep scan command
- `Dependencies`: DOC-001, DOC-002, DOC-003
- `Acceptance criteria`:
  - The scan fails if a stale workflow pin reappears in a maintained doc.
  - The scan does not traverse the live workflow files.
  - The allowlist covers intentional historical references.
- `Validation`:
  - Regression command fails red on a synthetic stale pin.
  - Regression command passes on the current archive/docs/examples set.
- `Implementation owner`: `docs`
- `Stage label`: Phase 3
- `Next test seam`: `docs/roadmap/2026-06-21-archived-docs-workflow-version-sweep-roadmap.html.md`
- `Notes`: This is the guardrail that keeps the sweep from regressing after the
  doc edits land.
