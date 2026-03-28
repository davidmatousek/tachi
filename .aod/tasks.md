---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-28
    status: APPROVED
    notes: "All 6 user stories addressed. All 15 FRs mapped to tasks. MVP scope (Phases 1-3) delivers P0 value. No scope creep. 2 low findings: US3 could have more granular tasks; validation phase could reference specific DoD criteria."
  architect_signoff:
    agent: architect
    date: 2026-03-28
    status: APPROVED_WITH_CONCERNS
    notes: "Dependencies correctly ordered. Parallel opportunities valid. 3 medium findings: T007-T009 edit same file so [P] marking would conflict (correctly sequential); T014 git mv should verify no broken imports; T028 should check both command locations (.claude/commands/ and adapters/)."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-28
    status: APPROVED
    notes: "31 tasks well-sized for docs-only feature. Critical path: Phase 1→2→3→4→7. Parallel waves identified. Estimate: 1 session. 5 findings (2 LOW, 3 INFO) — all non-blocking."
---

# Tasks: 045 — End-to-End tachi Instruction Manual

**Input**: Design documents from `specs/045-instruction-manual/`
**Prerequisites**: plan.md (required), spec.md (required), research.md

**Tests**: Not required (documentation-only feature — validation is manual walkthrough).

**Organization**: Tasks grouped by user story. All tasks edit markdown files — no code changes.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Read Source Materials)

**Purpose**: Read all source files needed to write accurate documentation

- [X] T001 Read existing prompt spec at `docs/guides/prompts/GUIDE_PROMPT.md` and note structure, insertion points, and content to preserve
- [X] T002 [P] Read existing developer guide at `docs/guides/DEVELOPER_GUIDE_TACHI.md` and note section numbering, insertion points, and content to preserve
- [X] T003 [P] Read `/risk-score` command spec at `adapters/claude-code/commands/risk-score.md` and extract invocation syntax, flags, inputs, outputs, scoring dimensions
- [X] T004 [P] Read `/compensating-controls` command spec (search `.claude/commands/` and `adapters/claude-code/commands/`) and extract invocation syntax, flags, inputs, outputs, control classification, residual risk formula
- [X] T005 [P] Read `/infographic` command spec at `adapters/claude-code/commands/infographic.md` and extract invocation syntax, flags, templates, auto-detection behavior, output artifacts
- [X] T006 [P] Read `docs/INTERFACE-CONTRACT.md` for output schema details needed in Appendix B updates

**Checkpoint**: All source materials read. Accurate command details available for writing.

---

## Phase 2: US4 — Prompt Specification Update (Priority: P1)

**Goal**: Update the source-of-truth prompt spec to cover the full 4-command pipeline. This MUST complete before the developer guide is updated (Phases 3-6).

**Independent Test**: The updated prompt spec at `docs/guides/prompts/GUIDE_PROMPT.md` contains sections for all 4 commands with invocation, flags, outputs, and interpretation guidance.

- [X] T007 [US4] Add `/risk-score` command section to `docs/guides/prompts/GUIDE_PROMPT.md` — include invocation syntax, flags (--output-dir), input requirements (threats.md primary, threats.sarif fallback, optional architecture.md), output artifacts (risk-scores.md, risk-scores.sarif), 4 scoring dimensions (CVSS, exploitability, scalability, reachability), composite score, governance fields
- [X] T008 [US4] Add `/compensating-controls` command section to `docs/guides/prompts/GUIDE_PROMPT.md` — include invocation syntax, flags (--target, --output-dir), input requirements (risk-scores.md primary, risk-scores.sarif fallback, optional architecture.md), output artifacts (compensating-controls.md, compensating-controls.sarif), control classification (Found/Partial/None), residual risk formula, evidence format (file:line)
- [X] T009 [US4] Add standalone `/infographic` command section to `docs/guides/prompts/GUIDE_PROMPT.md` — include invocation syntax, flags (--template, --output-dir), template options (baseball-card, system-architecture, all), legacy alias (corporate-white), auto-detection behavior (prefers risk-scores.md), co-located threats.md dependency, output artifacts (spec + .jpg), Gemini API key requirement and fallback behavior
- [X] T010 [US4] Add post-pipeline enrichment workflow section to `docs/guides/prompts/GUIDE_PROMPT.md` — include data flow diagram showing all 4 commands with inputs/outputs/dependencies, explain when each enrichment command is optional vs. recommended
- [X] T011 [US4] Update Output Artifacts section in `docs/guides/prompts/GUIDE_PROMPT.md` — add risk-scores.md, risk-scores.sarif, compensating-controls.md, compensating-controls.sarif to the existing artifact list (currently 6 artifacts, target 12+)
- [X] T012 [US4] Correct factual errors in `docs/guides/prompts/GUIDE_PROMPT.md` — change agent count from 14 to 15 (risk-scorer added in Feature 035), update infographic template names from `infographic-corporate-white.md` to `infographic-baseball-card.md` and `infographic-system-architecture.md`
- [X] T013 [US4] Extend OpenClaw worked example in `docs/guides/prompts/GUIDE_PROMPT.md` — add `/risk-score` step with sample output, `/compensating-controls` step with sample residual risk, `/infographic` step with template selection
- [X] T014 [US4] Rename prompt spec: `git mv docs/guides/prompts/GUIDE_PROMPT.md docs/guides/prompts/developer-guide-prompt.md`
- [X] T015 [US4] Search codebase for references to old filename `GUIDE_PROMPT.md` and update any references to `developer-guide-prompt.md`

**Checkpoint**: Prompt spec updated and renamed. Source of truth now covers full 4-command pipeline.

---

## Phase 3: US1 + US2 — Pipeline Guide & Output Interpretation (Priority: P1)

**Goal**: Add the core missing content to the developer guide — dedicated sections for each post-pipeline command with invocation, output, and interpretation guidance.

**Independent Test**: A developer can follow the new sections to run `/risk-score`, `/compensating-controls`, and `/infographic` after `/threat-model`, and can interpret all output files.

**Note**: US1 (pipeline guide) and US2 (output interpretation) are combined because interpretation content is embedded within each command section. Splitting them would require editing the same sections twice.

- [ ] T016 [US1] Insert post-pipeline enrichment workflow section in `docs/guides/DEVELOPER_GUIDE_TACHI.md` after Section 7 (Reading and Acting) — include pipeline overview diagram (ASCII showing all 4 commands with inputs/outputs/dependencies), explanation of when each enrichment command is optional vs. recommended, time estimates per command
- [ ] T017 [US1] [US2] Insert `/risk-score` section in `docs/guides/DEVELOPER_GUIDE_TACHI.md` following per-command template (Prerequisites → Invocation → Outputs → Interpretation → Next Step) — include copy-pasteable invocation (minimal + flagged), output artifact descriptions, interpretation of 4 scoring dimensions (what it measures, range 0-10, what high/low means), composite score explanation, governance fields overview
- [ ] T018 [US1] [US2] Insert `/compensating-controls` section in `docs/guides/DEVELOPER_GUIDE_TACHI.md` following same template — include copy-pasteable invocation (minimal + --target + --output-dir), output artifact descriptions, interpretation of coverage matrix, control classification (Found/Partial/None), evidence format (file:line references), residual risk calculation explanation, recommendations section
- [ ] T019 [US1] [US2] Insert standalone `/infographic` section in `docs/guides/DEVELOPER_GUIDE_TACHI.md` following same template — include auto-detection behavior explanation, copy-pasteable invocation (--template variants), template descriptions (baseball-card vs. system-architecture), Gemini API key requirement and fallback behavior, output artifact descriptions (spec + .jpg)

**Checkpoint**: All 4 commands documented in the guide with invocation and interpretation.

---

## Phase 4: US3 — Quick Start Enhancement (Priority: P1)

**Goal**: Update the Quick Start at the top of the guide to introduce all 4 commands and point readers to the new sections.

**Independent Test**: A new user following the Quick Start knows the full pipeline exists and where to find detailed guidance for each enrichment command.

- [ ] T020 [US3] Add "What's Next: The Full Pipeline" callout after Step 6 in Quick Start section of `docs/guides/DEVELOPER_GUIDE_TACHI.md` — mention `/risk-score`, `/compensating-controls`, `/infographic` with one-line descriptions and cross-references to their dedicated sections in the comprehensive guide

**Checkpoint**: Quick Start enhanced. Users know about all 4 commands from the start.

---

## Phase 5: US5 — OpenClaw Worked Example Extension (Priority: P2)

**Goal**: Extend the existing OpenClaw worked example to show the full 4-command pipeline.

**Independent Test**: The OpenClaw example shows output from all 4 commands with annotated examples.

- [ ] T021 [US5] Extend OpenClaw worked example in `docs/guides/DEVELOPER_GUIDE_TACHI.md` — add Step 11: Run `/risk-score` on OpenClaw threats with sample invocation, sample scored output table excerpt, and interpretation notes
- [ ] T022 [US5] Continue OpenClaw extension — add Step 12: Run `/compensating-controls` with sample invocation, sample coverage matrix excerpt, residual risk comparison, and interpretation notes
- [ ] T023 [US5] Continue OpenClaw extension — add Step 13: Run `/infographic` with template selection guidance, sample invocation, description of generated spec and image files

**Checkpoint**: OpenClaw example now walks through the full pipeline end-to-end.

---

## Phase 6: US6 — Appendix Updates (Priority: P2)

**Goal**: Update reference appendices with post-pipeline output structures and glossary terms.

**Independent Test**: A user looking up any output file structure can find it in Appendix B, and all new terms are in Appendix C.

- [ ] T024 [P] [US6] Expand Appendix B in `docs/guides/DEVELOPER_GUIDE_TACHI.md` — add `risk-scores.md` structure (sections: metadata, scored threat table, risk distribution, dimensional analysis, methodology, governance), add `risk-scores.sarif` schema details (per-finding composite scores and scoring properties)
- [ ] T025 [P] [US6] Continue Appendix B expansion — add `compensating-controls.md` structure (sections: coverage matrix, findings table with status/evidence/recommendations, recommendations sorted by risk, residual risk summary), add `compensating-controls.sarif` schema details (residual scores, control properties)
- [ ] T026 [US6] Add glossary terms to Appendix C in `docs/guides/DEVELOPER_GUIDE_TACHI.md` — add: Composite Score, Compensating Control, Residual Risk, Exploitability, Scalability, Reachability

**Checkpoint**: All appendices updated. Guide is now a complete reference.

---

## Phase 7: Validation & Polish

**Purpose**: Cross-cutting validation across all updated files

- [ ] T027 Verify all internal file path references in `docs/guides/DEVELOPER_GUIDE_TACHI.md` resolve correctly (no broken section links, no stale file paths)
- [ ] T028 [P] Verify all command invocations in the guide match actual command specs in `adapters/claude-code/commands/` and `.claude/commands/`
- [ ] T029 [P] Verify prompt spec at `docs/guides/prompts/developer-guide-prompt.md` covers the same pipeline as the guide (spec-guide parity check)
- [ ] T030 Verify README.md link to `docs/guides/DEVELOPER_GUIDE_TACHI.md` resolves correctly
- [ ] T031 Review full guide for consistency: section numbering sequential, per-command template consistent across all 4 commands, acronyms defined on first use, no stale template names

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **US4 - Prompt Spec (Phase 2)**: Depends on Setup — BLOCKS guide updates (source of truth must be updated first)
- **US1+US2 - Pipeline Guide (Phase 3)**: Depends on Phase 2 (prompt spec complete)
- **US3 - Quick Start (Phase 4)**: Depends on Phase 3 (needs section references to link to)
- **US5 - OpenClaw (Phase 5)**: Depends on Phase 3 (needs command sections to exist)
- **US6 - Appendix (Phase 6)**: Depends on Phase 3 (needs command output details finalized). T024 and T025 can run in parallel.
- **Validation (Phase 7)**: Depends on all prior phases

### User Story Dependencies

- **US4 (Prompt Spec)**: Independent — first in sequence. BLOCKS US1, US2, US3, US5, US6.
- **US1+US2 (Pipeline + Interpretation)**: Depends on US4. BLOCKS US3, US5.
- **US3 (Quick Start)**: Depends on US1+US2 (needs section anchors for cross-references)
- **US5 (OpenClaw)**: Depends on US1+US2 (needs command sections to reference)
- **US6 (Appendix)**: Depends on US1+US2 (needs output format details finalized)

### Parallel Opportunities

- **Phase 1**: T002-T006 can all run in parallel (reading different files)
- **Phase 2**: T007-T009 edit the same file sequentially, but T012 (factual corrections) can run in parallel with T010-T011
- **Phase 5+6**: US5 (OpenClaw) and US6 (Appendix) can run in parallel if editing different sections of the guide
- **Phase 6**: T024 and T025 can run in parallel (different appendix subsections)
- **Phase 7**: T028 and T029 can run in parallel (different validation checks)

---

## Implementation Strategy

### MVP First (US4 + US1+US2 Only)

1. Complete Phase 1: Read source materials
2. Complete Phase 2: Update prompt spec (US4)
3. Complete Phase 3: Add pipeline guide + interpretation sections (US1+US2)
4. **STOP and VALIDATE**: Guide now covers all 4 commands with interpretation
5. This alone satisfies the P0 success criteria from the PRD

### Incremental Delivery

1. Setup + US4 (prompt spec) → Source of truth updated
2. US1+US2 (pipeline guide) → Core value delivered
3. US3 (Quick Start) → Onboarding enhanced
4. US5 (OpenClaw) → Worked example complete
5. US6 (Appendix) → Reference material complete
6. Validation → Quality assured

---

## Summary

| Metric | Count |
|--------|-------|
| Total tasks | 31 |
| Phase 1 (Setup) | 6 |
| Phase 2 (US4 - Prompt Spec) | 9 |
| Phase 3 (US1+US2 - Pipeline Guide) | 4 |
| Phase 4 (US3 - Quick Start) | 1 |
| Phase 5 (US5 - OpenClaw) | 3 |
| Phase 6 (US6 - Appendix) | 3 |
| Phase 7 (Validation) | 5 |
| Parallel opportunities | 12 tasks marked [P] |
| Files modified | 2 (prompt spec, developer guide) + 1 rename |
| MVP scope | Phases 1-3 (19 tasks) |
