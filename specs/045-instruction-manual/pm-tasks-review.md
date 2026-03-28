# Product Manager Review: tasks.md (Feature 045)

**Artifact**: `specs/045-instruction-manual/tasks.md`
**Reviewer**: product-manager
**Date**: 2026-03-28
**Verdict**: APPROVED

---

## 1. User Story Coverage Analysis

### US1 - Complete Pipeline Guide (P1) -- COVERED

| Acceptance Scenario | Task(s) | Status |
|---------------------|---------|--------|
| AC-1: Follow pipeline, produce all 12+ output artifacts | T016 (pipeline overview), T017-T019 (per-command sections) | Covered |
| AC-2: /risk-score invocation in copy-pasteable code block | T017 (explicit: "copy-pasteable invocation (minimal + flagged)") | Covered |
| AC-3: /compensating-controls input and target flag documented | T018 (explicit: "minimal + --target + --output-dir") | Covered |
| AC-4: /infographic auto-detection and template selection | T019 (explicit: "auto-detection behavior explanation, --template variants") | Covered |
| AC-5: Data flow diagram showing all 4 commands | T016 (explicit: "pipeline overview diagram (ASCII showing all 4 commands with inputs/outputs/dependencies)") | Covered |

### US2 - Output Interpretation (P1) -- COVERED

| Acceptance Scenario | Task(s) | Status |
|---------------------|---------|--------|
| AC-1: threats.md sections explained with annotated examples | Pre-existing content (confirmed by spec assumption: existing guide covers /threat-model comprehensively) | Covered by baseline |
| AC-2: 4 scoring dimensions explained | T017 (explicit: "interpretation of 4 scoring dimensions (what it measures, range 0-10, what high/low means)") | Covered |
| AC-3: Controls section fully explained | T018 (explicit: "interpretation of coverage matrix, control classification (Found/Partial/None), evidence format, residual risk calculation") | Covered |
| AC-4: Prioritization guidance (Critical > High > Medium > Low) | T017/T018 interpretation sections cover scoring and risk levels; prioritization guidance is implicit in risk scoring interpretation | Covered (implicit) |

### US3 - Quick Start (P1) -- COVERED

| Acceptance Scenario | Task(s) | Status |
|---------------------|---------|--------|
| AC-1: Installation through /threat-model in 5-6 steps | Pre-existing Quick Start (confirmed by plan: "Keep Quick Start focused on /threat-model for the 5-minute target") | Covered by baseline |
| AC-2: Pointers to enrichment commands after Quick Start | T020 (explicit: "Add 'What's Next: The Full Pipeline' callout... mention /risk-score, /compensating-controls, /infographic with one-line descriptions and cross-references") | Covered |
| AC-3: Copy-pasteable command syntax | Pre-existing Quick Start + T020 cross-references to per-command sections that include copy-pasteable blocks | Covered |

### US4 - Prompt Specification Update (P1) -- COVERED

| Acceptance Scenario | Task(s) | Status |
|---------------------|---------|--------|
| AC-1: /risk-score, /compensating-controls, /infographic sections present | T007, T008, T009 | Covered |
| AC-2: Agent count corrected to 15 | T012 (explicit: "change agent count from 14 to 15") | Covered |
| AC-3: Infographic template names updated | T012 (explicit: "update infographic template names from infographic-corporate-white.md to infographic-baseball-card.md and infographic-system-architecture.md") | Covered |
| AC-4: Rename to developer-guide-prompt.md | T014 (explicit: "git mv") + T015 (reference updates) | Covered |

### US5 - OpenClaw Worked Example Extension (P2) -- COVERED

| Acceptance Scenario | Task(s) | Status |
|---------------------|---------|--------|
| AC-1: /risk-score invocation and sample output for OpenClaw | T021 (explicit: "sample invocation, sample scored output table excerpt, and interpretation notes") | Covered |
| AC-2: /compensating-controls residual risk for OpenClaw | T022 (explicit: "sample coverage matrix excerpt, residual risk comparison") | Covered |
| AC-3: /infographic template selection for OpenClaw | T023 (explicit: "template selection guidance, sample invocation, description of generated spec and image files") | Covered |

### US6 - Appendix Updates (P2) -- COVERED

| Acceptance Scenario | Task(s) | Status |
|---------------------|---------|--------|
| AC-1: risk-scores.md structure in Appendix B | T024 (explicit: "add risk-scores.md structure (sections: metadata, scored threat table, risk distribution, dimensional analysis, methodology, governance)") | Covered |
| AC-2: compensating-controls.md structure in Appendix B | T025 (explicit: "add compensating-controls.md structure (sections: coverage matrix, findings table...)") | Covered |
| AC-3: Infographic output naming conventions in Appendix B | Not explicitly addressed by T024/T025 | See Finding 1 |

**Result**: 6/6 user stories addressed. 1 minor gap noted.

---

## 2. Functional Requirements Traceability

| FR | Description | Task(s) | Status |
|----|-------------|---------|--------|
| FR-001 | Prompt spec: /risk-score documentation | T007 | Covered |
| FR-002 | Prompt spec: /compensating-controls documentation | T008 | Covered |
| FR-003 | Prompt spec: standalone /infographic documentation | T009 | Covered |
| FR-004 | Prompt spec: post-pipeline enrichment workflow | T010 | Covered |
| FR-005 | Prompt spec: agent count + template name corrections | T012 | Covered |
| FR-006 | Prompt spec: rename to developer-guide-prompt.md | T014, T015 | Covered |
| FR-007 | Guide: /risk-score, /compensating-controls, /infographic sections | T017, T018, T019 | Covered |
| FR-008 | Guide: post-pipeline workflow with data flow diagram | T016 | Covered |
| FR-009 | Quick Start: introduce all 4 commands, 5-min target | T020 (enhancement) + baseline | Covered |
| FR-010 | OpenClaw example: all 4 commands in sequence | T013 (prompt spec) + T021-T023 (guide) | Covered |
| FR-011 | Appendix B: risk-scores + compensating-controls structures | T024, T025 | Covered |
| FR-012 | Per-command template consistency | T017-T019 all follow same template | Covered |
| FR-013 | Acronyms defined on first use | T026 (glossary) + T031 (validation) | Covered |
| FR-014 | Copy-pasteable code blocks (minimal + flagged) | T017-T019 each specify "copy-pasteable" | Covered |
| FR-015 | Both integration paths (Standalone + AOD Lifecycle) | Not explicitly assigned to a task | See Finding 2 |

**Result**: 15/15 FRs addressed. 1 minor gap noted.

---

## 3. Scope Creep Assessment

**No scope creep detected.** The tasks strictly adhere to the spec boundaries:

- All tasks edit only `docs/guides/prompts/GUIDE_PROMPT.md` and `docs/guides/DEVELOPER_GUIDE_TACHI.md` -- both identified in the spec's scope
- No tasks create new files beyond the rename operation
- No tasks modify code, agents, or commands
- No tasks introduce features, sections, or content not traceable to the spec's FRs or user stories
- The validation phase (Phase 7) is appropriate cross-cutting quality assurance, not scope expansion
- T011 (Output Artifacts section update) is well-scoped, tracing directly to FR-004/FR-011

---

## 4. Task Description Specificity

**Assessment: Strong.** Task descriptions are execution-ready:

- File paths are exact (e.g., `docs/guides/prompts/GUIDE_PROMPT.md`, `docs/guides/DEVELOPER_GUIDE_TACHI.md`)
- Content requirements are specific (e.g., T007 lists: "invocation syntax, flags (--output-dir), input requirements (threats.md primary, threats.sarif fallback, optional architecture.md), output artifacts (risk-scores.md, risk-scores.sarif), 4 scoring dimensions...")
- Insertion points are defined (e.g., T016: "after Section 7 (Reading and Acting)")
- Parallel markers [P] are used correctly for independent tasks
- User story labels [US4], [US1], etc. provide clear traceability

One strength worth noting: T004 explicitly instructs the implementer to "search `.claude/commands/` and `adapters/claude-code/commands/`" for the compensating-controls command, addressing the architect's concern from the plan review about verifying both locations.

---

## 5. MVP Scope Analysis (Phases 1-3)

**MVP delivers core P0 value.** Phases 1-3 contain 19 tasks and cover:

- Phase 1 (Setup): All source material reading -- necessary foundation
- Phase 2 (US4): Complete prompt spec update -- source of truth must be updated first
- Phase 3 (US1+US2): Pipeline guide and output interpretation in the published guide

After Phase 3, the guide covers all 4 commands with invocation, interpretation, and data flow. This satisfies the PRD's P0 success criteria:
- SC-001 (100% pipeline coverage): All 4 commands documented
- SC-005 (spec-guide parity): Prompt spec and guide both updated

The "STOP and VALIDATE" checkpoint after Phase 3 is a sound product decision. It lets the team confirm core value before investing in P2 enhancements (OpenClaw extension, appendix updates).

---

## 6. Priority Order Validation

**P1 before P2 is respected.** The phase sequencing enforces this:

- Phase 2 (US4, P1): Prompt spec -- prerequisite for all guide work
- Phase 3 (US1+US2, P1): Core pipeline guide and interpretation
- Phase 4 (US3, P1): Quick Start enhancement
- Phase 5 (US5, P2): OpenClaw worked example extension
- Phase 6 (US6, P2): Appendix updates

P2 work (Phases 5-6) is correctly sequenced after all P1 work (Phases 2-4). The dependency chain is sound: US4 blocks US1+US2, which blocks US3/US5/US6.

---

## 7. Findings

### Finding 1 (LOW): Infographic output structure not explicitly in Appendix B tasks

US6 AC-3 requires: "the user looks up infographic outputs, both the spec file and image file naming conventions are documented." T024 and T025 cover risk-scores and compensating-controls structures but neither explicitly mentions infographic output naming conventions for Appendix B. The infographic output is described in T019 (the /infographic command section in the guide), but the appendix reference format is not explicitly tasked.

**Impact**: Low. The infographic output structure (spec + .jpg naming) is documented in T019's command section and T023's worked example. A user can find it. The appendix gap is a completeness issue, not a functional gap.

**Recommendation**: Consider adding infographic output file naming conventions to T024 or T025, or noting it as part of T031 (consistency review). Not blocking.

### Finding 2 (LOW): FR-015 (integration paths) not explicitly assigned

FR-015 requires documenting both Standalone and AOD Lifecycle integration paths. No task explicitly mentions this requirement. However, the existing guide already covers both paths (confirmed in the spec assumptions), and the new sections are additive -- they do not alter the existing integration path documentation.

**Impact**: Low. The existing guide content covers this FR. No new work is needed unless the existing content is incomplete. T031 (consistency review) would catch any gap during validation.

**Recommendation**: Consider adding a check to T031 to explicitly verify both integration paths are present. Not blocking.

---

## 8. Sign-off

**Verdict**: APPROVED

The tasks document demonstrates strong product-spec alignment:

- All 6 user stories are addressed with traceable tasks
- All 15 functional requirements are covered (2 implicitly through existing content + validation)
- No scope creep beyond spec boundaries
- Task descriptions are specific and execution-ready with exact file paths and content requirements
- MVP scope (Phases 1-3) delivers the P0 value proposition
- P1 work is correctly sequenced before P2 work
- Phase dependencies are sound and well-documented
- 2 low-severity findings are non-blocking and addressable during the validation phase

The tasks.md is ready for implementation.

---

**Product Manager Sign-off**: APPROVED
**Date**: 2026-03-28
**Agent**: product-manager
