# Session Continuation: Deduplication & Risk Rating

**Generated**: 2026-03-22 (build session 1)
**Branch**: 010-prd-010-deduplication
**Last Commit**: 4820472 docs(007): update CHANGELOG (#9)

## Completed This Session

- **Wave 1** (T001-T002): Schema Foundation — bumped schema_version to 1.1, added Correlated Findings section to output.yaml
- **Wave 2** (T003-T004): Schema Refinements — added dedup_note and three-state cell model to Coverage Matrix schema
- **P0 Checkpoint**: Architect APPROVED — schema v1.1 validated
- **Wave 3** (T005-T009, T017): Correlation Detection + Template
  - T005-T008: Added Correlation Rule Table, Detection Algorithm, Group Assembly, and Self-Check to orchestrator.md (Phase 3)
  - T009: Added Section 4a "Correlated Findings" to templates/threats.md
  - T017: Added Risk Calibration Matrix subsection to templates/threats.md Section 6
  - Updated schema_version references in templates/threats.md from 1.0 to 1.1

## Current State

- **Phase**: implement (build in progress)
- **Uncommitted**: 6 modified files + 2 new (agents/orchestrator.md, schemas/output.yaml, templates/threats.md, docs/product/_backlog/BACKLOG.md, docs/architecture/01_system_design/README.md, docs/product/02_PRD/INDEX.md, plus new specs/010-prd-010-deduplication/ and docs/product/02_PRD/010-deduplication-risk-rating-2026-03-22.md)
- **Tasks**: 10/24 complete (42%)
- **Waves**: 3/6 complete — stopped at wave ceiling (standalone mode)

## Remaining Waves

### Wave 4: Dedup Counts + Template Updates (T010-T016, T018)
- T010-T014 (sequential): Update orchestrator.md Phase 4 — deduplicated coverage matrix counts, three-state cell model, footnote, risk summary dedup counts, percentage computation
- T015-T016 (parallel): Update templates/threats.md — Coverage Matrix Section 5 (three-state cells, dedup counts, footnote) and Risk Summary Section 6 (dedup count column with parenthetical raw count)
- T018 (after T014): Update orchestrator.md Risk Summary to reference Risk Calibration Matrix and include 3×3 matrix before summary table
- **Note (Architect M-02)**: When executing T015, T016, and T021 — also update schema_version references from "1.0" to "1.1" in those files

### Wave 5: Polish (T019-T022)
- T019 [P], T020 [P]: Update docs/INTERFACE-CONTRACT.md — Section 3 (correlation rules description) and Section 4 (add Section 4a, three-state cell model, schema_version 1.1)
- T021: Update orchestrator.md Output Structural Validation Checklist — add Section 4a, coverage matrix dedup, risk summary dedup checks
- T022: Update orchestrator.md YAML frontmatter — add correlation detection + deduplication to description, bump version
- **Quality Gate**: code-reviewer review of all 4 modified files before integration testing

### Wave 6: Integration Validation (T023-T024)
- T023: Run orchestrator against examples/mermaid-agentic-app/input.md — verify correlations, preserved findings, dedup counts, risk calibration
- T024: Run orchestrator against examples/ascii-web-api/input.md — verify zero correlations, n/a AI columns, no dedup, risk calibration

### Checkpoints Remaining
- **P1 Checkpoint** (blocking): Architect review after Wave 5
- **P2 Checkpoint** (non-blocking): After Wave 6
- **Final Validation**: Architect + Code Review + Security review
- **Security Scan**: Step 6 (/security skill)

## Context Files

- `specs/010-prd-010-deduplication/spec.md` — Feature specification (PM approved)
- `specs/010-prd-010-deduplication/plan.md` — Implementation plan (PM + Architect approved)
- `specs/010-prd-010-deduplication/tasks.md` — Task breakdown with progress tracking
- `specs/010-prd-010-deduplication/agent-assignments.md` — Wave definitions and agent mapping
- `agents/orchestrator.md` — Primary file being modified (correlation detection added in Phase 3)
- `templates/threats.md` — Output template (Section 4a and Risk Calibration Matrix added)
- `schemas/output.yaml` — Schema updated to v1.1 with Correlated Findings section
- `docs/INTERFACE-CONTRACT.md` — Needs update in Waves 5 (T019-T020)

## Resume Command

```bash
claude "Resume Deduplication & Risk Rating implementation (branch: 010-prd-010-deduplication). Waves 1-3 complete (10/24 tasks). Run /aod.build to continue with Wave 4."
```
