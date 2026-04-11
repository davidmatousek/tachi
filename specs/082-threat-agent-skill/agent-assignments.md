# Feature 082 — Agent Assignments

**Feature**: 082-threat-agent-skill-references
**Generated**: 2026-04-11
**Governance status**: tasks.md APPROVED_WITH_CONCERNS (PM + Architect + Team-Lead)
**Source draft**: `.aod/results/team-lead-tasks.md` (team-lead sign-off, 18-wave table)
**Total tasks**: 67 (T001-T063 plus inline additions T055a/b/c/d)
**Timeline envelope**: 22h optimistic / 32h realistic / 45h pessimistic
**Critical path**: Phase 1 → Phase 2 → Phase 3 (prototype gate) → max(Phase 4, Phase 5) → Phase 6 → Phase 7 → Phase 8
**Max parallelism**: 3 concurrent `senior-backend-engineer` tracks during Phase 4+5 rollout

---

## 1. Agent Capacity Analysis

Parallel-track sustainability per agent, observed across the 18-wave structure:

| Agent | Max concurrent tracks | Binding constraint | Total touchpoints | Load assessment |
|-------|-----------------------|--------------------|-------------------|------------------|
| `senior-backend-engineer` | **3** | Phase 4+5 rollout wave (9 agent extractions in 3 sub-waves × 3 parallel tracks) | ~48 tasks | **Primary implementer** — 3 parallel tracks is the binding capacity ceiling; honored throughout Waves 9/10/11; no wave exceeds this cap |
| `architect` | 1 | Single reviewer on gate wait-states; no parallelism possible for gate review itself but can run alongside other agents | 8 tasks (T006, T015, T021, T022, T023, T047, T058, T059) | Light — gate reviews, ADR authorship, overlap audit, docs sync |
| `team-lead` | 1 | Co-reviewer on phase gates only; not an implementer | 2 tasks (T015 co-review, T021 co-review) | Very light — gate co-review only; governance role already completed upstream |
| `security-analyst` | 1 | Content review workload; not parallelizable with itself | 2 tasks (T020 prototype spot-check, T048 full enrichment review) | Very light — two batched reviews |
| `web-researcher` | 1 | Phase 0 batched query workload; internally serialized | 1 task (T004) | Very light — single broad task with ~22-44 brief entries |
| `tester` | **up to 5** | Phase 8 parallel validation sub-wave (T051-T055 grep/wc/ls checks independent) | 9 tasks (T050, T051, T052, T053, T054, T055, T055a, T055b, T061) | Light but batched — all Phase 8 work; 5 parallel grep/wc/ls sub-tasks in Wave 16 |
| `devops` | 1 | PR creation and merge are inherently serial | 2 tasks (T062, T063) | Very light — delivery-only |
| `code-reviewer` | 0 | Not explicitly invoked; per-agent commit reviews absorbed by `senior-backend-engineer` self-review in single-file-per-task structure | 0 explicit tasks | Not invoked (optional safety net only) |
| `orchestrator` | meta | Meta-coordinator across waves — not counted as an agent track | N/A | Meta-role |

**Verdict**: No agent exceeds 80% utilization at any wave. `senior-backend-engineer` at 3-parallel-tracks in Waves 9-11 is the binding capacity constraint and is explicitly budgeted in the Phase 4+5 time allocation.

---

## 2. Agent Assignment Matrix

Every task in tasks.md, mapped to its primary agent (and supporting agents where applicable). Only the valid subagent_type values listed in `.claude/agents/_README.md` are used. No generic labels like `file-agent`, `doc-agent`, or `qa-agent` appear.

### Phase 1 — Setup (T001-T005)

| Task | Primary agent | Supporting | Description |
|------|---------------|------------|-------------|
| T001 | `senior-backend-engineer` | — | Capture pre-refactor `threats.md` baselines for all 6 examples |
| T002 [P] | `senior-backend-engineer` | — | Capture pre-refactor `wc -l` for all 11 threat agent files |
| T003 [P] | `senior-backend-engineer` | — | Tally pre-refactor detection pattern category count per agent |
| T004 [P] | `web-researcher` | — | Produce per-agent enrichment source briefs (11 agents, 2-4 categories each) |
| T005 | `senior-backend-engineer` | — | Read control-analyzer.md as sibling-variant reference model |

### Phase 2 — Foundational (T006-T007)

| Task | Primary agent | Supporting | Description |
|------|---------------|------------|-------------|
| T006 | `architect` | — | Draft ADR-023 (4 decisions per plan §1.4, status Draft) |
| T007 | `senior-backend-engineer` | — | Audit shared ref files for additive-only safety |

### Phase 3.1 — Prototype Refactor-Only (T008-T015)

| Task | Primary agent | Supporting | Description |
|------|---------------|------------|-------------|
| T008 | `senior-backend-engineer` | — | Create `tachi-spoofing/references/detection-patterns.md` (verbatim extraction) |
| T009 | `senior-backend-engineer` | — | Restructure `spoofing.md` to lean form, ≤120 lines, **separate commit** |
| T010 | `senior-backend-engineer` | — | Create `tachi-prompt-injection/references/detection-patterns.md` (verbatim extraction) |
| T011 | `senior-backend-engineer` | — | Restructure `prompt-injection.md` to lean form, ≤150 lines, **separate commit** |
| T012 | `tester` | — | Phase 1a full-pipeline regression diff (6 examples) |
| T013 | `tester` | — | Phase 1a line count verification |
| T014 | `tester` | — | Phase 1a MAESTRO grep check (zero matches required) |
| T015 | `architect` | `team-lead` | Phase 1a gate review — joint approval required |

### Phase 3.2 — Prototype Enrichment (T016-T021)

| Task | Primary agent | Supporting | Description |
|------|---------------|------------|-------------|
| T016 | `senior-backend-engineer` | — | Append ≥2 new categories to spoofing detection-patterns.md |
| T017 | `senior-backend-engineer` | — | Append ≥2 new categories to prompt-injection detection-patterns.md |
| T018 | `tester` | — | Phase 1b full-pipeline regression diff (expects ≥1 new finding) |
| T019 | `tester` | — | Phase 1b line count verification |
| T020 | `security-analyst` | — | Prototype-scale security review of 4-6 new categories |
| T021 | `architect` | `team-lead` | Phase 1b gate review — joint approval required |

### Phase 3.3 — ADR-023 Acceptance (T022-T023)

| Task | Primary agent | Supporting | Description |
|------|---------------|------------|-------------|
| T022 | `architect` | — | Promote ADR-023 from Draft to Accepted, add Phase 1 validation section |
| T023 | `architect` | `team-lead` | Phase 1 combined gate checkpoint (exit criterion E-4) |

### Phase 4 — STRIDE Rollout (T024-T033)

All STRIDE extractions share the same primary agent (`senior-backend-engineer`) executing 3 parallel tracks at a time. Supporting role is empty because single-file-per-task structure requires no concurrent assistance.

| Task | Primary agent | Supporting | Description |
|------|---------------|------------|-------------|
| T024 [P] | `senior-backend-engineer` | — | Create `tachi-tampering/references/detection-patterns.md` (+ ≥0-3 enriched categories) |
| T025 | `senior-backend-engineer` | — | Restructure `tampering.md`, ≤120 lines, **separate commit** |
| T026 [P] | `senior-backend-engineer` | — | Create `tachi-repudiation/references/detection-patterns.md` (+ ≥0-3 enriched categories) |
| T027 | `senior-backend-engineer` | — | Restructure `repudiation.md`, ≤120 lines, **separate commit** |
| T028 [P] | `senior-backend-engineer` | — | Create `tachi-info-disclosure/references/detection-patterns.md` (+ ≥0-3 enriched categories) |
| T029 | `senior-backend-engineer` | — | Restructure `info-disclosure.md`, ≤120 lines, **separate commit** |
| T030 [P] | `senior-backend-engineer` | — | Create `tachi-denial-of-service/references/detection-patterns.md` (+ ≥0-3 enriched categories) |
| T031 | `senior-backend-engineer` | — | Restructure `denial-of-service.md`, ≤120 lines, **separate commit** |
| T032 [P] | `senior-backend-engineer` | — | Create `tachi-privilege-escalation/references/detection-patterns.md` (+ ≥0-3 enriched categories) |
| T033 | `senior-backend-engineer` | — | Restructure `privilege-escalation.md`, ≤120 lines, **separate commit** |

### Phase 5 — AI Rollout (T034-T041)

Runs in parallel with Phase 4. Same primary agent, same 3-track parallelism constraint.

| Task | Primary agent | Supporting | Description |
|------|---------------|------------|-------------|
| T034 [P] | `senior-backend-engineer` | — | Create `tachi-data-poisoning/references/detection-patterns.md` |
| T035 | `senior-backend-engineer` | — | Restructure `data-poisoning.md`, ≤150 lines, **separate commit** |
| T036 [P] | `senior-backend-engineer` | — | Create `tachi-model-theft/references/detection-patterns.md` |
| T037 | `senior-backend-engineer` | — | Restructure `model-theft.md`, ≤150 lines, **separate commit** |
| T038 [P] | `senior-backend-engineer` | — | Create `tachi-tool-abuse/references/detection-patterns.md` (ATLAS Oct 2025 additions) |
| T039 | `senior-backend-engineer` | — | Restructure `tool-abuse.md`, ≤150 lines, **separate commit** |
| T040 [P] | `senior-backend-engineer` | — | Create `tachi-agent-autonomy/references/detection-patterns.md` |
| T041 | `senior-backend-engineer` | — | Restructure `agent-autonomy.md`, ≤150 lines, **separate commit** (largest baseline — watch tier cap) |

### Phase 6 — Shared Ref Consolidation (T042-T046)

**SERIAL** single-writer phase (FR-14 / C10 constitution constraint). Zero [P] markers.

| Task | Primary agent | Supporting | Description |
|------|---------------|------------|-------------|
| T042 | `senior-backend-engineer` | — | Append producer section to `finding-format-shared.md` (+40-60 lines); **separate commit** scoped to this one file |
| T043 | `senior-backend-engineer` | — | Update all 11 threat agent `## Skill References` tables to add `finding-format-shared.md` Read row |
| T044 | `senior-backend-engineer` | — | Remove any stale inline OWASP 3×3 matrix rows from agent files |
| T045 | `senior-backend-engineer` | — | Update `stride-categories-shared.md` frontmatter consumers list (optional — may be N/A) |
| T046 | `senior-backend-engineer` | — | Final grep check confirming Phase 6 consistency |

### Phase 7 — Cross-Agent Audit and Enrichment Review (T047-T049)

| Task | Primary agent | Supporting | Description |
|------|---------------|------------|-------------|
| T047 [P] | `architect` | — | Cross-agent coverage overlap audit — identify shared categories and assign canonical owners |
| T048 [P] | `security-analyst` | — | Full enrichment review across all 11 ref files — reject speculative categories |
| T049 | `senior-backend-engineer` | `architect` | Aggregate enrichment tally vs ≥22 floor; iterate if below threshold |

### Phase 8 — Polish and Delivery (T050-T063, T055a-d)

| Task | Primary agent | Supporting | Description |
|------|---------------|------------|-------------|
| T050 | `tester` | — | **Full regression gate** — 6 examples, SC-005 thresholds |
| T051 [P] | `tester` | — | Cross-agent duplication grep audit (SC-004) |
| T052 [P] | `tester` | — | Final line count verification — STRIDE ≤120, AI ≤150, hard ceiling 180 (SC-002 + FR-10) |
| T053 [P] | `tester` | — | Verify all 11 companion skill directories exist (SC-003) |
| T054 [P] | `tester` | — | Verify MAESTRO boundary — zero grep matches across all 11 agents (SC-010 / FR-9 / INV-5) |
| T055 [P] | `tester` | — | Verify per-agent commit discipline — ≥11 agent-specific commits (FR-15 / SC-011) |
| T055a [P] | `tester` | — | Verify FR-11 `model: sonnet` frontmatter preserved on all 11 agents |
| T055b [P] | `architect` | — | Verify FR-4 self-documenting reference files — manual architect review, pass/fail per file |
| T055c | `tester` | — | Verify SC-014 no runtime dependency additions via `git diff` |
| T055d | `tester` | — | Verify SC-009 ADR-023 Accepted post-condition and cross-reference in Tech Stack README |
| T056 | `senior-backend-engineer` | — | Byte-deterministic PDF re-baseline for 5 examples (ADR-021 / Feature 136 precedent) |
| T057 | `senior-backend-engineer` | — | Regenerate `examples/agentic-app/threats.md` (AI agent enrichment validation) |
| T058 [P] | `architect` | — | Update `docs/architecture/00_Tech_Stack/README.md` — 17 agents on lean pattern, ADR-023 cross-ref |
| T059 [P] | `architect` | — | Update `CLAUDE.md` Recent Changes section with Feature 082 entry |
| T060 [P] | `senior-backend-engineer` | — | Update `enrichment-tally.md` with final Phase 7-adjusted count (SC-006 evidence) |
| T061 | `tester` | — | Full `pytest tests/` suite run (includes `test_backward_compatibility.py`) |
| T062 | `devops` | — | Create PR — cites ADR-023, phase gates, re-baseline, full-regression report |
| T063 | `devops` | `team-lead` | Merge PR — release-please auto-cuts tag, close Issue #82 |

---

## 3. Parallel Execution Waves

18 waves total. Dependency-correct, dependency-tight. Every serialization justified by an explicit upstream-dependency relationship.

### Wave 1 — Phase 1 Setup (Parallel)

**Mode**: PARALLEL | **Time**: 2-3h | **Entry**: branch creation | **Exit**: all baselines captured, briefs in-place

| Task | Agent | Dependencies |
|------|-------|--------------|
| T001 | `senior-backend-engineer` | branch created |
| T002 [P] | `senior-backend-engineer` | — |
| T003 [P] | `senior-backend-engineer` | — |
| T004 [P] | `web-researcher` | — |
| T005 | `senior-backend-engineer` | — |

**Parallelism**: T001-T005 all run in parallel. Web-researcher (T004) runs concurrently with senior-backend-engineer baselines (T001-T003, T005).

### Wave 2 — Phase 2 Foundational (Parallel)

**Mode**: PARALLEL | **Time**: 1-2h | **Entry**: Wave 1 complete | **Exit**: ADR-023 Draft ready, shared-ref audit complete

| Task | Agent | Dependencies |
|------|-------|--------------|
| T006 | `architect` | — |
| T007 | `senior-backend-engineer` | — |

**Parallelism**: Architect drafts ADR while senior-backend-engineer audits shared refs.

### Wave 3 — Phase 3.1a Spoofing Prototype (Parallel)

**Mode**: PARALLEL | **Time**: 1-2h | **Entry**: Wave 2 complete

| Task | Agent | Dependencies |
|------|-------|--------------|
| T008 | `senior-backend-engineer` | T005, T007 |
| T009 | `senior-backend-engineer` | T008 (serial within this agent's work) |

### Wave 4 — Phase 3.1b Prompt-Injection Prototype (Parallel with Wave 3)

**Mode**: PARALLEL WITH WAVE 3 | **Time**: 1-2h (overlaps Wave 3)

| Task | Agent | Dependencies |
|------|-------|--------------|
| T010 | `senior-backend-engineer` | T005, T007 |
| T011 | `senior-backend-engineer` | T010 |

**Parallelism note**: Waves 3 and 4 run on 2 concurrent `senior-backend-engineer` tracks. Well within the 3-track cap.

### Wave 5 — Phase 3.1 Gate Review

**Mode**: SERIAL | **Time**: 0.5-1h | **Entry**: Waves 3+4 complete

| Task | Agent | Dependencies |
|------|-------|--------------|
| T012 | `tester` | T009, T011 |
| T013 | `tester` | T009, T011 |
| T014 | `tester` | T009, T011 |
| T015 | `architect` + `team-lead` (joint) | T012, T013, T014 |

**Gate**: Phase 1a gate review. Joint architect + team-lead approval required before proceeding. If gate fails: iterate (max 2 iterations). If 2 iterations fail: escalate for PRD re-scoping (R1 fallback: ship STRIDE-only).

### Wave 6 — Phase 3.2 Enrichment (Parallel)

**Mode**: PARALLEL | **Time**: 1-2h | **Entry**: Wave 5 gate passed

| Task | Agent | Dependencies |
|------|-------|--------------|
| T016 | `senior-backend-engineer` | T004, T015 |
| T017 | `senior-backend-engineer` | T004, T015 |

### Wave 7 — Phase 3.2 Gate Review

**Mode**: SERIAL | **Time**: 1-2h | **Entry**: Wave 6 complete

| Task | Agent | Dependencies |
|------|-------|--------------|
| T018 | `tester` | T016, T017 |
| T019 | `tester` | T016, T017 |
| T020 | `security-analyst` | T016, T017 |
| T021 | `architect` + `team-lead` (joint) | T018, T019, T020 |

**Gate**: Phase 1b gate. Joint architect + team-lead approval. Security-analyst spot-check is a dependency on the gate.

### Wave 8 — Phase 3.3 ADR-023 Acceptance

**Mode**: SERIAL | **Time**: 0.5h | **Entry**: Wave 7 gate passed

| Task | Agent | Dependencies |
|------|-------|--------------|
| T022 | `architect` | T021 |
| T023 | `architect` | T022 |

**Gate**: Phase 1 combined gate checkpoint (exit criterion E-4). End of Phase 3.

### Wave 9 — Phase 4+5 Rollout Sub-Wave A (3 Parallel Tracks)

**Mode**: PARALLEL (3 tracks) | **Time**: 2-3h | **Entry**: Wave 8 complete

| Track | Tasks | Agent |
|-------|-------|-------|
| Track 1 | T024 → T025 (tampering) | `senior-backend-engineer` |
| Track 2 | T034 → T035 (data-poisoning) | `senior-backend-engineer` |
| Track 3 | T036 → T037 (model-theft) | `senior-backend-engineer` |

Each track runs a ref-creation task immediately followed by the agent-file restructure. Three tracks execute concurrently — binding the `senior-backend-engineer` 3-track capacity ceiling.

### Wave 10 — Phase 4+5 Rollout Sub-Wave B (3 Parallel Tracks)

**Mode**: PARALLEL (3 tracks) | **Time**: 2-3h | **Entry**: Wave 9 complete

| Track | Tasks | Agent |
|-------|-------|-------|
| Track 1 | T026 → T027 (repudiation) | `senior-backend-engineer` |
| Track 2 | T028 → T029 (info-disclosure) | `senior-backend-engineer` |
| Track 3 | T038 → T039 (tool-abuse — ATLAS Oct 2025 focus) | `senior-backend-engineer` |

### Wave 11 — Phase 4+5 Rollout Sub-Wave C (3 Parallel Tracks)

**Mode**: PARALLEL (3 tracks) | **Time**: 2-3h | **Entry**: Wave 10 complete

| Track | Tasks | Agent |
|-------|-------|-------|
| Track 1 | T030 → T031 (denial-of-service) | `senior-backend-engineer` |
| Track 2 | T032 → T033 (privilege-escalation) | `senior-backend-engineer` |
| Track 3 | T040 → T041 (agent-autonomy — largest baseline at 201 lines; watch tier cap) | `senior-backend-engineer` |

**End of Phase 4+5**: all 9 remaining agents extracted; all 11 threat agents now on the sibling lean variant.

### Wave 12 — Phase 6 Shared Ref Consolidation (SERIAL single-writer)

**Mode**: SERIAL | **Time**: 1-2h | **Entry**: Wave 11 complete

| Task | Agent | Dependencies |
|------|-------|--------------|
| T042 | `senior-backend-engineer` | T041 (all Phase 4+5 complete) |
| T043 | `senior-backend-engineer` | T042 |
| T044 | `senior-backend-engineer` | T043 |
| T045 | `senior-backend-engineer` | T007 (may be N/A) |
| T046 | `senior-backend-engineer` | T044 |

**CRITICAL**: Zero `[P]` markers. Single-writer constraint per FR-14 / C10 prevents merge conflicts in `finding-format-shared.md`.

### Wave 13 — Phase 7 Cross-Agent Audit + Enrichment Review (Parallel)

**Mode**: PARALLEL | **Time**: 1-2h | **Entry**: Wave 12 complete

| Task | Agent | Dependencies |
|------|-------|--------------|
| T047 [P] | `architect` | T046 |
| T048 [P] | `security-analyst` | T046 |

### Wave 14 — Phase 7 Aggregate Tally

**Mode**: SERIAL | **Time**: 0.5-1h | **Entry**: Wave 13 complete

| Task | Agent | Dependencies |
|------|-------|--------------|
| T049 | `senior-backend-engineer` | T047, T048 |

**Gate**: Aggregate enrichment floor check. If aggregate < 22: iterate (architect + senior-backend-engineer identify additional candidates from T004 briefs).

### Wave 15 — Phase 8 Full Regression Gate

**Mode**: SERIAL | **Time**: 1h | **Entry**: Wave 14 complete

| Task | Agent | Dependencies |
|------|-------|--------------|
| T050 | `tester` | T049 |

**Gate**: SC-005 thresholds — finding count per category within ±2, severity within ±1, zero dropped findings. All downstream Phase 8 waves depend on this passing.

### Wave 16 — Phase 8 Parallel Validations

**Mode**: PARALLEL (up to 5 tester tracks + 1 architect track) | **Time**: 1-2h | **Entry**: Wave 15 passed

| Task | Agent | Dependencies |
|------|-------|--------------|
| T051 [P] | `tester` | T050 |
| T052 [P] | `tester` | T050 |
| T053 [P] | `tester` | T050 |
| T054 [P] | `tester` | T050 |
| T055 [P] | `tester` | T050 |
| T055a [P] | `tester` | T050 |
| T055b [P] | `architect` | T050 (manual review; runs concurrently with tester grep tasks) |
| T055c | `tester` | T050 |

**Parallelism**: 5 concurrent tester tracks (grep/wc/ls grep-shaped tasks are IO-bound and independent) plus 1 architect track for T055b self-documenting review.

### Wave 17 — Phase 8 Re-Baseline and Agentic-App Regeneration

**Mode**: PARALLEL | **Time**: 1-2h | **Entry**: Wave 16 complete

| Task | Agent | Dependencies |
|------|-------|--------------|
| T056 | `senior-backend-engineer` | T050 |
| T057 | `senior-backend-engineer` | T041 (already satisfied by Wave 11); and T050 gate |

**Note**: T056 is the ADR-021 byte-deterministic PDF re-baseline for 5 examples (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice). T057 regenerates agentic-app (not byte-deterministic per Feature 128 convention).

### Wave 18 — Phase 8 Docs and Delivery

**Mode**: PARALLEL docs then SERIAL delivery | **Time**: 1-2h | **Entry**: Wave 17 complete

| Task | Agent | Dependencies |
|------|-------|--------------|
| T055d | `tester` | T022, T058 |
| T058 [P] | `architect` | T050 |
| T059 [P] | `architect` | T050 |
| T060 [P] | `senior-backend-engineer` | T049 |
| T061 | `tester` | T056 |
| T062 | `devops` | T058, T059, T060, T061, T055d |
| T063 | `devops` | T062 |

**Delivery chain**: T058+T059+T060 in parallel, then T061 pytest, then T055d (depends on T058), then T062 PR, then T063 merge.

---

## 4. Quality Gates Between Waves

Four hard gates plus three informal checkpoints. Each gate has a defined iteration budget and escalation path.

### Gate A — Phase 1a Refactor-Only Gate (after Wave 5)

- **Guardians**: `architect` + `team-lead` (joint approval)
- **Gate task**: T015
- **Criteria**: zero new findings, zero dropped findings, finding count ±0, severity ±0, line counts within FR-10 tier caps, zero MAESTRO matches
- **Iteration budget**: 2 iterations
- **Failure path**: escalate for PRD re-scoping (R1 fallback: ship STRIDE-only in 082, defer AI to new PRD 083)
- **Entry**: T012 + T013 + T014 complete
- **Exit**: explicit joint approval recorded in `phase-1a-regression.md`

### Gate B — Phase 1b Enrichment Gate (after Wave 7)

- **Guardians**: `architect` + `team-lead` (joint approval)
- **Gate task**: T021
- **Criteria**: ≥1 new finding surfaces from enrichment, line counts still within FR-10 caps, security-analyst spot-check passes (T020 — all new categories cite primary sources with canonical URLs, taxonomy alignment correct, no speculative patterns)
- **Iteration budget**: 2 iterations
- **Failure path**: same R1 fallback as Gate A
- **Entry**: T018 + T019 + T020 complete
- **Exit**: explicit joint approval recorded in `phase-1b-regression.md`

### Gate C — Phase 1 Combined Checkpoint (after Wave 8)

- **Guardian**: `architect`
- **Gate task**: T023
- **Criteria**: exit criterion E-4 met (load-shape variant declared in ADR-023), both regression gates A and B passed, ADR-023 status = Accepted (T022)
- **Output**: `phase-1-complete.md` — Phase 1 completion summary
- **Blocking downstream**: Phase 4+5 cannot begin until this checkpoint is recorded
- **Entry**: T022 complete
- **Exit**: `phase-1-complete.md` written and committed

### Gate D — Full Regression Gate (after Wave 15)

- **Guardian**: `tester`
- **Gate task**: T050
- **Criteria (SC-005)**: finding count per category within ±2, severity distribution within ±1 per level, zero dropped findings, new findings allowed from enrichment
- **Blocking downstream**: all Phase 8 validation, re-baseline, and delivery waves depend on this passing
- **Failure path**: R6 contingency — roll back shared ref consolidation if diff exceeds expected scope
- **Entry**: T049 aggregate enrichment floor confirmed ≥22
- **Exit**: `phase-3-full-regression.md` written with explicit PASS verdict

### Informal Checkpoints

- **Phase 6 single-writer checkpoint** (after Wave 12): grep confirms no inline OWASP 3×3 matrix rows remain; all 11 agents include `finding-format-shared.md` Read row in their Skill References table
- **Phase 7 aggregate enrichment floor** (within Wave 14): T049 computes aggregate new categories; if <22, iterate to append additional candidate categories
- **Phase 8 PDF re-baseline checkpoint** (within Wave 17): 5 byte-deterministic baselines regenerated under `SOURCE_DATE_EPOCH=1700000000` per ADR-021; diff outside expected shared-ref propagation scope triggers R6 rollback

---

## 5. Time Estimates Per Wave

Estimates sum to the 22h optimistic / 32h realistic / 45h pessimistic envelope confirmed in team-lead sign-off.

| Wave | Phase | Description | Opt (h) | Real (h) | Pess (h) |
|------|-------|-------------|---------|----------|----------|
| W1 | 1 | Setup: baselines + enrichment briefs | 2 | 3 | 4 |
| W2 | 2 | Foundational: ADR-023 draft + shared-ref audit | 1 | 2 | 3 |
| W3 | 3.1a | Spoofing prototype extraction | 1 | 1.5 | 2 |
| W4 | 3.1b | Prompt-injection prototype extraction (parallel with W3) | (overlaps W3) | (overlaps W3) | (overlaps W3) |
| W5 | 3.1 gate | Phase 1a regression + joint gate review | 0.5 | 1 | 1.5 |
| W6 | 3.2 | Prototype enrichment (2 agents) | 1 | 1.5 | 2 |
| W7 | 3.2 gate | Phase 1b regression + security spot-check + joint gate review | 1 | 1.5 | 2 |
| W8 | 3.3 | ADR-023 acceptance + combined checkpoint | 0.5 | 0.5 | 1 |
| **Phase 3 subtotal** | | **5 waves** | **4** | **5.5** | **8.5** |
| W9 | 4+5 Sub-Wave A | tampering + data-poisoning + model-theft (3 parallel tracks) | 2 | 2.5 | 3.5 |
| W10 | 4+5 Sub-Wave B | repudiation + info-disclosure + tool-abuse (3 parallel tracks) | 2 | 2.5 | 3.5 |
| W11 | 4+5 Sub-Wave C | denial-of-service + priv-esc + agent-autonomy (3 parallel tracks) | 2 | 3 | 4 |
| **Phase 4+5 subtotal** | | **3 waves** | **6** | **8** | **11** |
| W12 | 6 | Shared ref consolidation (SERIAL single-writer) | 1 | 2 | 3 |
| W13 | 7 audit | Cross-agent overlap audit + enrichment review (parallel) | 1 | 1.5 | 2 |
| W14 | 7 tally | Aggregate enrichment floor tally + iteration | 0.5 | 1 | 2 |
| W15 | 8 gate | Full regression gate T050 | 1 | 1 | 1.5 |
| W16 | 8 validation | Parallel grep/wc/ls/manual validations | 1 | 1.5 | 2 |
| W17 | 8 baseline | PDF re-baseline + agentic-app regen | 1 | 1.5 | 2 |
| W18 | 8 delivery | Docs sync + pytest + PR + merge | 1.5 | 2 | 3 |
| **Phase 6-8 subtotal** | | **7 waves** | **7** | **10.5** | **15.5** |
| **TOTAL** | **18 waves** | | **22** | **32** | **45** |

**Sum validation**:
- Optimistic: 2+1+1+0.5+1+1+0.5+6+1+1+0.5+1+1+1+1.5 = **22h** ok
- Realistic: 3+2+1.5+1+1.5+1.5+0.5+8+2+1.5+1+1+1.5+1.5+2 = **32h** ok
- Pessimistic: 4+3+2+1.5+2+2+1+11+3+2+2+1.5+2+2+3 = **45h** ok

**Wall clock translation**: 4-6 calendar days at 4-6h/day focused `senior-backend-engineer` time. PRD claimed delivery 2026-04-16 (5 days from 2026-04-11 kickoff) is feasible at the midpoint estimate.

---

## 6. Hand-off to Orchestrator

Orchestrator receives:

- **Feasibility status**: APPROVED_WITH_CONCERNS (team-lead sign-off 2026-04-11)
- **tasks.md location**: `specs/082-threat-agent-skill/tasks.md`
- **Wave strategy**: 18 waves (see §3)
- **Agent assignments**: see §2 matrix
- **Binding capacity constraint**: 3-track cap on `senior-backend-engineer` during Waves 9/10/11
- **Critical gates**: 4 hard gates (A/B/C/D) with explicit iteration budgets
- **Fallback contingency**: R1 (STRIDE-only ship, AI deferred to PRD 083) if either Gate A or Gate B fails after 2 iterations
- **R6 contingency**: roll back shared ref consolidation if Gate D diff exceeds expected scope

**Non-blocking concerns deferred to execution** (per team-lead §7):

1. **T009 + T011 commit marker gap**: Notes §Per-agent commit discipline covers intent. Orchestrator should enforce "separate commit" discipline naturally via single-file-per-task execution. Optional 1-line tasks.md cleanup deferred.
2. **T051-T055 assignee ambiguity**: RESOLVED in this document — all 5 tasks routed to `tester` explicitly (plus T055a to `tester`, T055b to `architect`, T055c and T055d to `tester`).
3. **T004 granularity**: observation only — `web-researcher` batches query workload effectively.

**Orchestrator approval to proceed**: green-lit by team-lead sign-off. Proceed to `/aod.build` entry.
