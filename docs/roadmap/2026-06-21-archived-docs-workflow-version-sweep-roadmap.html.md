# Archived Docs Workflow-Version Sweep Roadmap

Status: active execution roadmap

Scope: archived docs and examples only. No edits to `.github/workflows`,
no active CI surface changes, and no rework of the completed parity roadmap.

This roadmap is separate from the CI modernization work. It exists to remove
or reframe stale workflow-version references in documentation while preserving
historical meaning where the old version number is part of the record.

## Objective

Sweep archived docs and example docs that still mention older GitHub Actions or
CodeQL versions. The goal is to keep maintained docs current, keep historical
docs clearly labeled as historical, and keep examples free of stale pins.

## Current inventory

### Maintained docs that should be updated

- `docs/testing/README.md`
- `docs/guides/DEVELOPER_GUIDE_TACHI.md`
- `docs/devops/README.md`
- `docs/devops/CI_CD_GUIDE.md`
- `docs/standards/PRECOMMIT_HOOKS.md`
- `docs/standards/GIT_WORKFLOW.md`
- `docs/architecture/00_Tech_Stack/README.md`
- `docs/architecture/01_system_design/README.md`

### Historical docs that should be annotated, not silently rewritten

- `docs/guides/CONSUMER_GUIDE_TACHI.md`
- `docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md`
- `docs/guides/CONSUMER_GUIDE_TACHI_AOD_INTEGRATION.md`
- `docs/architecture/02_ADRs/ADR-013-sarif-output-format-adoption.md`
- `docs/product/02_PRD/012-sarif-output-generation-2026-03-22.md`
- `docs/product/02_PRD/021-platform-adapters-2026-03-23.md`

### Examples tree

- Current scan found no stale workflow-version pins under `examples/`.
- Keep `examples/` in the regression gate so future docs regressions are
  caught without touching the active workflow surface.

## Current gaps

1. Several maintained docs still show older checkout, toolchain, or SARIF
   upload pins in code snippets.
2. Several historical docs still describe older action versions without
   an archival marker that would tell readers the snippet is frozen.
3. There is no repo-local regression gate that scans archived docs/examples
   without also pulling in the live workflow files.

## Sweep rules

1. Update maintained docs to current majors or version-neutral wording.
2. Preserve historical references where they are part of the record, but add
   an archival callout so readers do not mistake them for current guidance.
3. Do not edit `.github/workflows/*` in this sweep.
4. Do not force example rewrites where no stale pin exists.
5. Add a docs-only regression gate that scans the archive/doc/example surface.

## Phase 0 - inventory and classification

Goal: produce a single disposition for every stale-version mention found in
the archive/docs/examples scan.

Exit criteria:

- Every hit has one of three dispositions: `update`, `archive-note`, or
  `regression-only`.
- The examples tree is confirmed clean or called out explicitly if future
  stale pins appear.
- The active CI workflow files remain untouched.

## Phase 1 - maintained-doc updates

Goal: fix the docs that are meant to guide current users and contributors.

Exit criteria:

- Current guidance uses the newest supported workflow pins or avoids pinning
  when version specificity is unnecessary.
- Snippets in maintainer-facing docs no longer teach older checkout/toolchain
  patterns.

## Phase 2 - historical-doc annotation

Goal: preserve historical docs without letting them masquerade as current
operating guidance.

Exit criteria:

- Historical docs keep their original meaning.
- Archived references are labeled as historical snapshots or frozen examples.
- Readers can tell at a glance whether a snippet is explanatory history or
  current instruction.

## Phase 3 - regression gate

Goal: prevent the archive sweep from regressing.

Exit criteria:

- A docs-only scan gate covers the archive/docs/examples surface.
- The gate excludes `.github/workflows/*`.
- The gate fails if a stale version pin reappears in a maintained doc.

## Validation matrix

| Work type | Minimum proof | Preferred seam |
|---|---|---|
| Maintained doc update | Text diff plus targeted grep | `docs/testing/README.md`, `docs/guides/DEVELOPER_GUIDE_TACHI.md` |
| Historical annotation | Doc review plus link check | `docs/product/02_PRD/*`, `docs/architecture/02_ADRs/*` |
| Regression gate | Grep-based scan with an allowlist | docs/examples archive scan command |

## Beads issue tracker mapping

Use the following structure when creating Beads cards:

| Field | Value |
| --- | --- |
| Tracker | Beads |
| Program | `tachi-rust` archived docs workflow-version sweep |
| Priority | maintain current docs first, preserve historical docs second |
| Definition of done | docs updated, archive markers added, regression gate in place |

The Beads-ready issue set lives in
[2026-06-21-archived-docs-workflow-version-sweep-issue-cards.md](./2026-06-21-archived-docs-workflow-version-sweep-issue-cards.md).
