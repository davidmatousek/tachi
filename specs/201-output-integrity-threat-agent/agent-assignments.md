---
feature: 201-output-integrity-threat-agent
artifact: agent-assignments.md
author: team-lead
date: 2026-04-18
branch: 201-output-integrity-threat-agent
source_tasks: specs/201-output-integrity-threat-agent/tasks.md
tasks_count: 55
waves_count: 6 (Wave 1.0 → Wave 1.1 → Wave 2 → Wave 3 → Wave 4 → Wave 5 + Polish + Post-Merge)
calendar:
  day_1: 2026-04-20 Monday
  day_2: 2026-04-21 Tuesday
  day_3: 2026-04-22 Wednesday
  day_4: 2026-04-23 Thursday (buffer)
outcome_default: B (Heuristic A split — 2-day baseline)
outcome_alternate: A (subsume — 3-3.5-day realistic)
---

# Agent Assignments — Feature 201 `output-integrity` Threat Agent

This artifact operationalizes the triple-approved `tasks.md` into agent-by-wave execution units. All assignments reference the exact `subagent_type` values from `.claude/agents/_README.md`. The orchestrator consumes this file to dispatch work; the team-lead consumes it to track capacity and escalate gates.

**Source of Truth**: `specs/201-output-integrity-threat-agent/tasks.md` (triple sign-off 2026-04-18; 55 tasks across 9 phases).

**Escalation anchors**: TL-H1 (re-baseline decision at T031 if T012 / T038 flags mermaid-agentic-app), TL-H2 (Day-1-EOD hard gate on T004 + T010 completion), R5 (regeneration-surface drift beyond mermaid-agentic-app).

---

## 1. Agent Assignment Matrix

All 55 tasks mapped to exact `subagent_type` values. Parallel Group column indicates which tasks may run concurrently within a wave (PG-N notation scoped to the wave).

| Task ID | Phase | Agent (`subagent_type`) | Parallel Group | Notes |
|---------|-------|-------------------------|----------------|-------|
| T001 | Phase 1 Setup | `senior-backend-engineer` | PG-Setup-1 | Working-directory verification; trivial shell + read check |
| T002 | Phase 1 Setup | `senior-backend-engineer` | PG-Setup-1 | Create `.claude/skills/tachi-output-integrity/references/` directory |
| T003 | Phase 1 Setup | `senior-backend-engineer` | PG-Setup-1 | Create `tests/scripts/fixtures/output_integrity/` directory |
| **T004** | **Phase 2 Wave 1.0** | **`architect`** | **sequential (blocking)** | **Heuristic A ruling; ADR-030 D2 input; memo to `.aod/results/heuristic-a-decision.md`; TL-H2 gate anchor** |
| T005 | Phase 2 Wave 1.1 | `tester` | PG-Wave1.1-A | Regex unit test at `tests/scripts/test_output_integrity.py` — MUST FAIL at authoring before T006 |
| T006 | Phase 2 Wave 1.1 | `senior-backend-engineer` | sequential after T005 | Schema bump 1.5→1.6 + regex extension; atomic commit; verify T005 now passes |
| T007 | Phase 2 Wave 1.1 | `tester` | PG-Wave1.1-B | Valid `OI-1` fixture with `source_attribution` + LLM05 + CWE-79 citations |
| T008 | Phase 2 Wave 1.1 | `tester` | PG-Wave1.1-B | Invalid-attribution fixture citing absent CWE-73 for F-A2 rejection test |
| T009 | Phase 2 Wave 1.1 | `architect` | PG-Wave1.1-C | ADR-030 skeleton — Status: Proposed; 8 numbered-decision placeholders |
| **T010** | **Phase 2 Wave 1.1** | **`architect`** | **sequential after T009** | **ADR-030 D1-D8 populated including D8 regex-extension rule (architect M1) + D2 Outcome B with Outcome A counter-argument (PM M2); TL-H2 gate anchor** |
| T011 | Phase 2 Wave 1.1 | `architect` | sequential after T010 | ADR-030 Cross-References — ADR-020/021/022/023/026/027/028/029 (architect L1/L2/L3) |
| T012 | Phase 2 Wave 1.1 | `senior-backend-engineer` | PG-Wave1.1-D | Mermaid-agentic-app pre-check grep; output to `specs/201-.../mermaid-baseline-check.md` (architect M2 / TL-H1 anchor) |
| T013 | Phase 3 Wave 2 | `senior-backend-engineer` | PG-Wave2-A | `detection-patterns.md` frontmatter + Overview + Detection Scope + DFD targets |
| T014 | Phase 3 Wave 2 | `senior-backend-engineer` | sequential after T013 | 5 numbered pattern categories (Outcome B); BLOCKING-1 CWE corrections embedded |
| T015 | Phase 3 Wave 2 | `senior-backend-engineer` | PG-Wave2-A | `README.md` companion skill — ≤50 lines, mirror `tachi-prompt-injection` shape |
| T016 | Phase 3 Wave 2 | `senior-backend-engineer` | PG-Wave2-B | `output-integrity.md` agent skeleton — 5-section canonical shape, no `agentic_pattern` (HIGH-4) |
| T017 | Phase 3 Wave 2 | `senior-backend-engineer` | sequential after T016 | Complete `## Detection Workflow` steps 1-6; FR-011 both-keyword-AND-sink-indicator |
| T018 | Phase 3 Wave 2 | `tester` | PG-Wave2-C | Structural validation — line count ≤150, 1 `**MANDATORY**: Read`, zero MAESTRO refs |
| T019 | Phase 4 Wave 2 | `senior-backend-engineer` | sequential after T016 | 2-3 worked `OI-{N}` example findings in agent `## Example Findings` |
| T020 | Phase 4 Wave 2 | `senior-backend-engineer` | sequential after T014 | Server/client-side execution distinction predicate (PM M3); each category's worked example explicit |
| T021 | Phase 4 Wave 2 | `tester` | PG-Wave2-D | Mitigation-specificity sanity grep; output to `.aod/results/wave2-mitigation-specificity-check.md` |
| T022 | Phase 5 Wave 5 | `architect` | PG-Wave5-A | ADR-030 Proposed → Accepted transition; provisional PR row in Revision History |
| T023 | Phase 5 Wave 5 | `architect` | sequential after T022 | ADR-030 completeness check (D1-D8, Consequences, Cross-Refs, Revision History) |
| T024 | Phase 5 Wave 5 | `senior-backend-engineer` | sequential after T023 | Agent `## Purpose` F-4 forward-reference + ASI09 out-of-scope explicit (US3 AC) |
| **T025** | **Post-Merge** | **`architect`** | **post-merge only (decoupled from T052)** | **ADR-030 Revision History short-SHA fill after squash-merge** |
| T026 | Phase 6 Wave 3 | `senior-backend-engineer` | PG-Wave3-A | `orchestrator.md` dispatch list — insert `output-integrity.md` after `tool-abuse.md` |
| T027 | Phase 6 Wave 3 | `senior-backend-engineer` | PG-Wave3-A | `dispatch-rules.md` LLM quartet + FR-011 trigger-keyword + structural indicator rule |
| T028 | Phase 6 Wave 3 | `senior-backend-engineer` | PG-Wave3-A | `finding-format-shared.md` `consumers:` list extension (HIGH-2 tier-grouping placement) |
| T029 | Phase 6 Wave 3 | `tester` | sequential after T028 | Structural-diff validation — ADR-023 Decision 3 `## ` heading byte-identity enforcement |
| T030 | Phase 6 Wave 3 | `tester` | PG-Wave3-B | Q2 keyword FP check on `web-app` + `agentic-app` (PM M1); output to `.aod/results/wave3-keyword-false-positive-check.md` |
| **T031** | **Phase 7 Wave 4** | **`senior-backend-engineer`** | **sequential after T030 (decision gate)** | **Review T012 output; TL-H1 re-baseline escalation if flagged** |
| T032 | Phase 7 Wave 4 | `senior-backend-engineer` | sequential after T031 | `/tachi.threat-model` regen on `examples/agentic-app/architecture.md` |
| T033 | Phase 7 Wave 4 | `senior-backend-engineer` | sequential after T032 | `/tachi.risk-score` regen |
| T034 | Phase 7 Wave 4 | `senior-backend-engineer` | sequential after T033 | `/tachi.compensating-controls` regen |
| T035 | Phase 7 Wave 4 | `senior-backend-engineer` | sequential after T034 | `/tachi.infographic all` — 6 JPEGs + specs |
| T036 | Phase 7 Wave 4 | `senior-backend-engineer` | sequential after T035 | `/tachi.security-report` regen — `security-report.pdf` + `.pdf.baseline` |
| T037 | Phase 7 Wave 4 | `tester` | PG-Wave4-A | F-A2 referential integrity pytest — `test_output_integrity.py` |
| T038 | Phase 7 Wave 4 | `tester` | PG-Wave4-A | Backward-compat byte-identity pytest under `SOURCE_DATE_EPOCH=1700000000` (R5 anchor) |
| T039 | Phase 7 Wave 4 | `senior-backend-engineer` | PG-Wave4-A | Git-stage regenerated artifacts for commit |
| T040 | Phase 8 Wave 5 | `tester` | PG-Wave5-B | SC-001 — agent file structural (delegates to T018 result) |
| T041 | Phase 8 Wave 5 | `tester` | PG-Wave5-B | SC-002 — pattern catalog structure |
| T042 | Phase 8 Wave 5 | `tester` | PG-Wave5-B | SC-003 — additive-only finding-format edit (delegates to T029 result) |
| T043 | Phase 8 Wave 5 | `tester` | PG-Wave5-B | SC-004 — regenerated agentic-app OI findings surfaced |
| T044 | Phase 8 Wave 5 | `code-reviewer` | PG-Wave5-B | SC-005 — ADR-030 Accepted at merge completeness (delegates to T023) |
| T045 | Phase 8 Wave 5 | `tester` | PG-Wave5-B | SC-006 — byte-identity pass on 5 baselines (delegates to T038) |
| T046 | Phase 8 Wave 5 | `tester` | PG-Wave5-B | SC-007 — OI findings carry mitigations + LLM05 + source_attribution |
| T047 | Phase 8 Wave 5 | `tester` | PG-Wave5-B | SC-008 — empty diff on dependency manifests |
| T048 | Phase 8 Wave 5 | `code-reviewer` | PG-Wave5-B | SC-009 — 22-file zero-edit grep audit (ADR-023 invariant) |
| T049 | Phase 8 Wave 5 | `tester` | PG-Wave5-B | SC-010 — F-A2 validation on regen (delegates to T037) |
| T050 | Phase 8 Wave 5 | `tester` | PG-Wave5-B | SC-011 — zero MAESTRO refs (delegates to T018) |
| T051 | Phase 8 Wave 5 | `tester` | PG-Wave5-B | SC-012 — schema_version 1.6 + OI regex + regex test pass |
| T052 | Phase 8 Wave 5 | `senior-backend-engineer` | sequential after T040-T051 green | PR open `201-output-integrity-threat-agent` → `main`; request triple review |
| T053 | Phase 9 Polish | `senior-backend-engineer` | PG-Polish | Update `CLAUDE.md` Recent Changes (Features 180/189/194 pattern) |
| T054 | Phase 9 Polish | `tester` | PG-Polish | Quickstart.md Step 10 end-to-end smoke |
| T055 | Phase 9 Polish | `senior-backend-engineer` | PG-Polish | Verify `examples/README.md` no-update — F-1 regenerates existing example |

**Agent-count summary (55 assigned tasks)**:

| Agent | Task count | Share |
|-------|-----------|-------|
| `senior-backend-engineer` | 30 | 54.5% |
| `tester` | 17 | 30.9% |
| `architect` | 7 | 12.7% |
| `code-reviewer` | 2 | 3.6% |
| (others) | 0 | 0% |

---

## 2. Parallel Execution Waves

Each wave advances only after its Quality Gate (Section 3) is green. Wave-internal parallel groups (PG-N) may run concurrently; sequential anchors within a wave are called out.

### Wave 1.0 — Architect Heuristic A Ruling (Day 1 AM, 30-60 min)

**Blocking critical path**: Wave 1.1 cannot begin until T004 memo is committed.

| Parallel Group | Tasks | Agent |
|---------------|-------|-------|
| (sequential, single) | T004 | `architect` |

**Gate**: `.aod/results/heuristic-a-decision.md` committed with explicit Outcome A or Outcome B determination; default is Outcome B.

### Wave 1.1 — Schema Lock + ADR-030 Proposed (Day 1 AM/PM, 5-parallel)

**Maximum parallelism**: 5 tracks can proceed concurrently once Wave 1.0 completes.

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| PG-Wave1.1-A | T005 → T006 | `tester` (T005), `senior-backend-engineer` (T006) | Test-first discipline; T006 atomic |
| PG-Wave1.1-B | T007, T008 | `tester` | Independent fixture authoring |
| PG-Wave1.1-C | T009 → T010 → T011 | `architect` | ADR-030 Proposed sequential chain |
| PG-Wave1.1-D | T012 | `senior-backend-engineer` | Independent grep-based pre-check |
| (Setup) | T001, T002, T003 | `senior-backend-engineer` | Folds into Wave 1.1 afternoon if not pre-completed |

**Gate — TL-H2 hard escalation trigger**: If T004 + T010 not complete by Day 1 EOD (Monday 2026-04-20 23:59 local), surface user tie-break before Day 2 AM. **Do NOT proceed to Wave 2 without ADR-030 Proposed commit.**

### Wave 2 — Pattern Catalog + Agent Authoring + Mitigation Text (Day 1 PM / Day 2 AM, 0.5-1d)

**3-parallel core + sequential micro-chains**. US1 (T013-T018) and US2 (T019-T021) run interleaved.

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| PG-Wave2-A | T013 → T014, T015 | `senior-backend-engineer` | Pattern catalog chain + companion README |
| PG-Wave2-B | T016 → T017, T019 | `senior-backend-engineer` | Agent-file chain + example findings |
| PG-Wave2-C | T018 | `tester` | Structural validation after T017 emits ≥ draft state |
| PG-Wave2-D | T020, T021 | `senior-backend-engineer` (T020), `tester` (T021) | Mitigation text + specificity grep |

**Gate**: T018 structural check green; T021 mitigation-specificity check green; `.aod/results/wave2-*.md` artifacts committed.

### Wave 3 — Orchestrator Registration + Shared-Reference Edits (Day 2 PM / Day 3 AM, 0.5d)

**3-parallel file edits + sequential structural diff**.

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| PG-Wave3-A | T026, T027, T028 | `senior-backend-engineer` | Three different files; independent edits |
| PG-Wave3-A-tail | T029 | `tester` | Sequential after T028; ADR-023 Decision 3 enforcement |
| PG-Wave3-B | T030 | `tester` | Keyword FP check (PM M1); parallel with T029 |

**Gate**: T029 structural-diff empty on `## ` heading changes; T030 keyword FP check green (zero FP on `web-app`).

### Wave 4 — Example Regeneration + Backward-Compat Verification (Day 2 PM / Day 3, 0.5-1d)

**Pipeline regen is sequential** (T031→T036 chained on artifact dependency); **verification is 3-parallel** (T037/T038/T039).

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| (sequential) | T031 → T032 → T033 → T034 → T035 → T036 | `senior-backend-engineer` | Pipeline regen chain with TL-H1 decision gate at T031 |
| PG-Wave4-A | T037, T038, T039 | `tester` (T037/T038), `senior-backend-engineer` (T039) | 3-parallel verifications + git-stage |

**Gate**: T038 byte-identity 5/5 pass on non-agentic baselines; T037 F-A2 validation green; ≥1 `OI-{N}` finding in regenerated `agentic-app/threats.md`.

### Wave 5 — ADR Accepted + SC Sweep + PR (Day 3 Outcome B / Day 4 Outcome A, 0.5d)

**Maximum parallelism**: 12 SC checks run concurrently. ADR-Accepted transition runs parallel to SC sweep.

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| PG-Wave5-A | T022 → T023, T024 | `architect` (T022/T023), `senior-backend-engineer` (T024) | ADR Accepted + agent Purpose forward-ref |
| PG-Wave5-B | T040-T051 | `tester` (10), `code-reviewer` (2 — T044/T048) | 12-parallel SC validation sweep on independent surfaces |
| (sequential tail) | T052 | `senior-backend-engineer` | PR open after PG-Wave5-A + PG-Wave5-B both green |

**Gate — Pre-PR**: All 12 SCs green; ADR-030 Status: Accepted; triple-review request posted on PR.

### Post-Merge — SHA Fill (decoupled from T052)

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| (post-squash only) | T025 | `architect` | ADR-030 Revision History short-SHA fill; consistent with ADR-027/028/029 pattern |

### Polish Lane — Parallel with Wave 5 (Day 3 PM / Day 4)

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| PG-Polish | T053, T054, T055 | `senior-backend-engineer` (T053/T055), `tester` (T054) | Safe to run pre-merge alongside Wave 5 SC sweep |

---

## 3. Quality Gates Between Waves

Each gate is a binary go/no-go before advancing. Failures escalate to team-lead + architect per the Escalation Paths section. All gate artifacts write to `.aod/results/`.

### Gate 1.0 → 1.1 — Heuristic A Ruling Committed

**Must be green**:
- [ ] `.aod/results/heuristic-a-decision.md` exists with explicit Outcome A / Outcome B determination
- [ ] Decision author identified; default noted
- [ ] Working directory clean

**Blocker if red**: Wave 1.1 cannot begin; user-visible escalation required.

### Gate 1.1 → 2 — Schema Lock + ADR-030 Proposed

**Must be green (TL-H2 hard gate)**:
- [ ] `schemas/finding.yaml` bumped to `schema_version: "1.6"` with extended `OI` regex — T006 atomic commit
- [ ] `tests/scripts/test_output_integrity.py` regex test passes — T005 green post-T006
- [ ] `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md` Status: Proposed committed with 8 Decisions (D1-D8) and Cross-References populated — T009/T010/T011
- [ ] `tests/scripts/fixtures/output_integrity/{valid_oi_finding,invalid_attribution_finding}.yaml` committed — T007/T008
- [ ] `specs/201-output-integrity-threat-agent/mermaid-baseline-check.md` committed — T012
- [ ] All Day-1-EOD completions (Monday 2026-04-20 23:59 local)

**Blocker if red**: TL-H2 user tie-break escalation fires; Day 2 AM work does not begin until resolved.

### Gate 2 → 3 — Agent + Companion Structural Compliance

**Must be green**:
- [ ] `.claude/agents/tachi/output-integrity.md` ≤150 lines, 1 `**MANDATORY**: Read`, zero MAESTRO refs (T018)
- [ ] `.claude/skills/tachi-output-integrity/references/detection-patterns.md` has ≥5 pattern categories with worked examples + citations + keywords + DFD types (T014)
- [ ] `.claude/skills/tachi-output-integrity/README.md` ≤50 lines companion (T015)
- [ ] Mitigation specificity grep green — no "sanitize output" / "validate input" without adjacent specific mechanism (T021)
- [ ] Each pattern category worked example distinguishes server-side vs client-side execution (T020 / PM M3)

**Blocker if red**: Fix agent or companion; do not register in orchestrator until structural checks pass.

### Gate 3 → 4 — Orchestrator Registration + Structural-Diff Clean

**Must be green**:
- [ ] `orchestrator.md` dispatch list includes `output-integrity.md` after `tool-abuse.md` (T026)
- [ ] `dispatch-rules.md` LLM quartet documented with FR-011 trigger + structural indicator rule (T027)
- [ ] `finding-format-shared.md` `consumers:` list extended additively (T028)
- [ ] `git diff main -- finding-format-shared.md | grep -E '^[+-]## '` returns empty — ADR-023 Decision 3 enforcement (T029)
- [ ] T030 keyword FP check: `web-app` zero FP, `agentic-app` expected matches only (PM M1)

**Blocker if red**: Structural-diff failure = ADR-023 violation; refine edits. Keyword FP on `web-app` = refine keyword set before regen.

### Gate 4 → 5 — Regeneration Surface Clean

**Must be green (R5 anchor)**:
- [ ] T031 TL-H1 decision: mermaid-agentic-app not flagged, OR architect + team-lead approved re-baseline
- [ ] `/tachi.threat-model` → `/tachi.risk-score` → `/tachi.compensating-controls` → `/tachi.infographic all` → `/tachi.security-report` all green on `examples/agentic-app/` (T032-T036)
- [ ] ≥1 `OI-{N}` finding surfaced in regenerated `agentic-app/threats.md`
- [ ] `pytest tests/scripts/test_output_integrity.py` green — F-A2 validation passes (T037)
- [ ] `SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py` — 5/5 baselines byte-identical (T038)
- [ ] Regenerated artifacts git-staged (T039)

**Blocker if red — R5 escalation**: Byte-identity break on `web-app` / `microservices` / `ascii-web-au` / `free-text-microservice` = root-cause before merge. `mermaid-agentic-app` break = TL-H1 re-baseline decision.

### Gate 5 → PR-Open — All SCs Green

**Must be green**:
- [ ] All 12 spec SCs (SC-001 through SC-012) verified via T040-T051
- [ ] ADR-030 Status: Accepted with provisional merge date + placeholder PR number (T022)
- [ ] ADR-030 body completeness confirmed (T023)
- [ ] Agent `## Purpose` F-4 forward-reference + ASI09 out-of-scope verified (T024)
- [ ] 22-file zero-edit grep audit returns clean (T048)

**Blocker if red**: Any SC fail = do not open PR; refine per specific SC.

### Post-Merge Gate

**Must be green**:
- [ ] PR squash-merged; short-SHA recorded
- [ ] T025 ADR-030 Revision History updated with squash commit short-SHA — consistent with ADR-027/028/029 lineage

---

## 4. Time Estimates per Wave

**Outcome B baseline (plan default)**: 2-day critical path + Thursday buffer.
**Outcome A extended (if T004 selects subsume)**: 3-3.5-day realistic + Thursday absorbed.

### Outcome B (Default) Timeline

| Wave | Day / Time | Duration | Critical Path Tasks | Notes |
|------|-----------|----------|--------------------|------|
| Setup + Wave 1.0 | Day 1 AM (Monday 2026-04-20, 09:00-10:30) | 60-90 min | T001-T003, T004 | Heuristic A ruling is critical path |
| Wave 1.1 | Day 1 AM/PM (10:30-17:00) | 6-7 hours | T005, T006, T009, T010, T011 | 5-parallel tracks cut wall-clock; TL-H2 gate by EOD |
| Wave 2 (US1) | Day 1 PM / Day 2 AM (Monday 17:00 spillover → Tuesday 09:00-13:00) | 0.5-1d (4-8h) | T013, T014, T016, T017 | Pattern catalog + agent authoring |
| Wave 2 (US2) | Day 2 AM/PM (13:00-15:00) | 1-2 hours | T019, T020, T021 | Runs interleaved with US1; often in parallel |
| Wave 3 | Day 2 PM (15:00-18:00) | 3 hours | T026, T027, T028, T029, T030 | Orchestrator registration + structural + FP check |
| Wave 4 | Day 3 AM (Wednesday 2026-04-22, 09:00-14:00) | 4-5 hours | T031-T036 + T037/T038/T039 | Pipeline regen sequential; verification 3-parallel |
| Wave 5 (ADR + SC) | Day 3 PM (14:00-17:30) | 3-4 hours | T022-T024, T040-T051 | ADR Accepted + 12-parallel SC sweep |
| PR open + Polish | Day 3 EOD (17:30-18:30) | 1 hour | T052, T053, T054, T055 | PR triple-review request + CLAUDE.md + smoke |
| **Thursday buffer** | **Day 4 (2026-04-23)** | **0-1d** | **absorbed into merge cycle, review lag, or R5 root-cause** | **Not committed; available if needed** |
| Post-merge | Post-PR merge | 15 min | T025 | SHA fill after squash |

**Day 3 landing target**: PR opened by Wednesday 2026-04-22 EOD with all 12 SCs green.

### Outcome A (Subsume) Extended Timeline

If T004 returns Outcome A (subsume ASI09 human-victim signal class into F-1):

| Delta | Impact |
|-------|--------|
| +1 pattern category in T014 (6th: Human-Trust Exploitation via LLM Output) | +2-4 hours in Wave 2 |
| +1 worked example in T019 | +30-60 min in Wave 2 |
| +1 mitigation pattern in T020 (tone classifier / source citation / human-in-loop) | +30-60 min in Wave 2 |
| Additional FP sweep in T030 on human-facing flows | +30 min in Wave 3 |
| Additional SC validation sweep on 6th category in T041/T046 | +30 min in Wave 5 |
| Thursday buffer (Day 4) | **Consumed** — PR open by Thursday EOD instead of Wednesday |

**Outcome A landing target**: PR opened by Thursday 2026-04-23 EOD.

### Thursday Buffer Policy

- If Outcome A chosen at T004 → Thursday buffer consumed by 6th-pattern research + authoring + validation (per tasks.md Implementation Strategy).
- If R5 materializes (regeneration surface drift beyond mermaid-agentic-app) → Thursday buffer consumed by root-cause + rebalance.
- If all else green by Day 3 EOD → Thursday absorbed into PR review lag / merge cycle.

---

## 5. Capacity Check

Post-tasks.md triple sign-off, team-lead concern M4 flagged `senior-backend-engineer` load. This section verifies headroom.

### Load by Agent

| Agent | Assigned Tasks | Est. Hours (Outcome B) | Capacity Window (2d = 16h) | Utilization |
|-------|----------------|------------------------|----------------------------|-------------|
| `senior-backend-engineer` | 30 | ~12-14h | 16h | **75-87%** (within team-lead M4 target of 70-80%, with upper tail) |
| `tester` | 17 | ~6-8h | 16h | **37-50%** (light load; ample headroom for Wave 5 SC sweep + additional verification) |
| `architect` | 7 | ~4-5h | 16h | **25-31%** (light load; Day 1 AM Heuristic A ruling + Day 1 PM ADR-030 authoring + Day 3 PM ADR Accepted + post-merge SHA fill) |
| `code-reviewer` | 2 | ~1h | 16h | **6%** (SC-005 ADR completeness + SC-009 22-file audit) |

**Verdict**: Capacity within acceptable envelope. `senior-backend-engineer` at upper-tail 87% under worst-case Outcome B; if Outcome A is chosen, load shifts to ~95% — **flag for TL-M4 re-evaluation at Wave 2 midpoint if Outcome A selected**.

### Mitigation Strategies (if `senior-backend-engineer` saturates)

1. **Delegate T015 (README) and T053 (CLAUDE.md) to independent runs** — they are small, self-contained, and parallelizable.
2. **Batch Wave 4 pipeline regen (T032-T036) as a single orchestrated command sequence** — wall-clock is dominated by tool invocation, not engineer attention.
3. **Promote T020 / T021 to earliest-available window** — mitigation text review can run interleaved with T014.
4. **Escalate to team-lead for re-balancing** if Outcome A selected and `senior-backend-engineer` utilization crosses 90%.

### `tester` Capacity Reserve

With only 37-50% utilization, `tester` has ample room to absorb:
- Additional regression fixtures if T037 F-A2 validation flags schema-contract edge cases
- Additional FP sweep on non-baseline examples if R5 surfaces
- Pytest suite re-runs if any mid-wave commit breaks green

### `architect` Capacity Reserve

With only 25-31% utilization, `architect` has room to:
- Handle TL-H1 re-baseline decision at T031 without capacity impact
- Author supplementary ADR amendment if D8 regex-extension rule needs clarification
- Review any late-arriving architect M1/M2 refinement

### `code-reviewer` Load

2 tasks (T044 ADR-030 completeness, T048 22-file zero-edit audit) = ~1 hour total. Agent can be assigned additional PR-phase review tasks post-T052 if needed.

---

## 6. Escalation Paths

Three escalation anchors defined in tasks.md + PRD. All escalations write to `.aod/results/escalation-log.md` with anchor, trigger, and resolution timestamp.

### TL-H1 — mermaid-agentic-app Re-Baseline Decision

**Trigger**: T012 (pre-check grep) flags ≥1 trigger-keyword match on `examples/mermaid-agentic-app/architecture.md`, OR T038 (backward-compat pytest) fails on `mermaid-agentic-app` baseline.

**Decision gate at T031**: Review T012 output + T038 result. If either flagged, PAUSE Wave 4 and escalate to architect + team-lead.

**Escalation participants**:
- `architect` — structural assessment of whether the baseline break is substantive (new finding class) vs accidental (keyword false match)
- `team-lead` — timeline impact assessment (Outcome B → Outcome A shift? Thursday buffer activated?)

**Resolution paths**:
1. **No substantive break → refine keywords in T014 + T027** → re-run T012 → continue Wave 4.
2. **Substantive break → approve re-baseline**: regenerate `examples/mermaid-agentic-app/` outputs as 6th baseline regen under feature 201; update `tests/scripts/test_backward_compatibility.py` baseline list. Document as explicit scope expansion.
3. **Uncertain → user tie-break**: surface to user with both options + cost/impact summary.

**Escalation artifact**: `specs/201-output-integrity-threat-agent/mermaid-baseline-escalation.md`

### TL-H2 — Day-1-EOD Hard Gate

**Trigger**: T004 (Heuristic A ruling) OR T010 (ADR-030 Proposed with D1-D8) not complete by Day 1 EOD (Monday 2026-04-20 23:59 local).

**Escalation action**: Surface user tie-break notice before Day 2 AM start. Do NOT proceed to Wave 2 without ADR-030 Proposed commit.

**Escalation participants**:
- `user` — final decision authority if architect ruling delayed
- `architect` — brief status report on blocker (research depth, cross-ref ambiguity, decision complexity)
- `team-lead` — timeline impact (Outcome A likely + Thursday consumed)

**Resolution paths**:
1. **Architect ruling imminent (<2h delay)** → proceed with relaxed Day 2 AM start; no user escalation needed; absorb into slack.
2. **Architect ruling blocked on ambiguity** → user tie-break decision on Outcome A vs Outcome B with 2-3 sentence rationale from each.
3. **Architect ruling requires scope research** → scope expansion → /aod.clarify session to add needed research; re-plan Day 2 AM start time.

**Escalation artifact**: `.aod/results/tl-h2-escalation-YYYY-MM-DD.md`

### R5 — Regeneration Surface Drift

**Trigger**: T038 backward-compat byte-identity pytest fails on ANY baseline other than `mermaid-agentic-app` — i.e., `web-app`, `microservices`, `ascii-web-api`, or `free-text-microservice` breaks.

**Escalation action**: PAUSE PR open. Root-cause before merge.

**Escalation participants**:
- `architect` — assess whether the break is shared-reference-edit induced (T028 went non-additive), orchestrator-induced (T026/T027 changed dispatch for non-LLM components), or schema-induced (T006 regex change affected pre-existing findings)
- `senior-backend-engineer` — reproduce locally; isolate changed file
- `tester` — confirm break is deterministic vs flaky; verify `SOURCE_DATE_EPOCH` is set
- `team-lead` — timeline impact assessment (Thursday buffer consumed likely)

**Resolution paths**:
1. **Non-additive shared-reference edit** (ADR-023 violation) → revert T028; refactor to add `consumers:` entry without touching any body content.
2. **Orchestrator dispatch leaked** → refactor T026/T027 to enforce FR-011 structural indicator gate; ensure `output-integrity` does not fire on non-LLM components.
3. **Schema regex side-effect** → unlikely given T005 test coverage; if confirmed, architect assesses ADR-030 D8 rule completeness.

**Escalation artifact**: `.aod/results/r5-regeneration-drift-YYYY-MM-DD.md`

### Additional Escalation: F-A2 Validation Failure at T037

**Trigger**: `pytest tests/scripts/test_output_integrity.py` rejects regenerated `OI-{N}` findings for referential-integrity failures.

**Escalation action**: Pattern worked examples likely cite out-of-catalog CWE IDs.

**Resolution**: Revise per FR-007 — substitute CWE-94 for absent CWE-1336 (template injection), CWE-22 for absent CWE-73 (path traversal). Confirm BLOCKING-1 corrections in T014 held through regeneration.

**Escalation artifact**: Root-cause in T037 pytest output; resolution commit referencing `.aod/results/fr-007-resolution.md`.

---

## 7. Handoff to Orchestrator

The orchestrator consumes this `agent-assignments.md` as input to drive execution. Handoff contract:

- **Wave sequencing**: Follow Section 2 strictly; do not advance past a gate in Section 3 without explicit green state.
- **Agent dispatch**: Use exact `subagent_type` values from Section 1 matrix; no improvisation or fallback substitution.
- **Parallel-group cohesion**: Dispatch all tasks in a parallel group (PG-N) in a single multi-task message when possible.
- **Gate reporting**: After each wave completes, emit a short completion report to team-lead with gate artifacts referenced.
- **Escalation invocation**: If any escalation anchor fires (TL-H1 / TL-H2 / R5 / F-A2), PAUSE and surface to team-lead + architect (and user for TL-H2) before proceeding.

**Team-lead sign-off confirmation**: This `agent-assignments.md` inherits the triple APPROVED_WITH_CONCERNS status from `tasks.md` (2026-04-18). No separate sign-off gate required for execution start, per the Triad governance matrix (team-lead authority on `agent-assignments.md`).

**Orchestrator entry command**: `/aod.build` (or `/aod.run` for full-lifecycle continuation).

---

**End of Agent Assignments — Feature 201**
