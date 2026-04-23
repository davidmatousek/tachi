---
feature: 206-misinformation-threat-agent
artifact: agent-assignments.md
author: team-lead
date: 2026-04-23
branch: 206-misinformation-threat-agent
source_tasks: specs/206-misinformation-threat-agent/tasks.md
tasks_count: 62
waves_count: 6 (Wave 1.0 → Wave 1.1 → Wave 2 → Wave 3 → Wave 4 → Wave 5 → Wave 6 + Polish)
calendar:
  day_1: 2026-04-27 Monday
  day_2: 2026-04-28 Tuesday
  day_3: 2026-04-29 Wednesday (buffer)
outcome_default: Heuristic A three-way split preserved (2-day baseline + buffer)
outcome_alternate: Subsume-into-output-integrity signal (blocked at Wave 1.0 gate; requires user tie-break per R1)
---

# Agent Assignments — Feature 206 `misinformation` Threat Agent

This artifact operationalizes the triple-approved `tasks.md` into agent-by-wave execution units. All assignments reference the exact `subagent_type` values from `.claude/agents/_README.md`. The orchestrator consumes this file to dispatch work; the team-lead consumes it to track capacity and escalate gates.

**Source of Truth**: `specs/206-misinformation-threat-agent/tasks.md` (triple APPROVED 2026-04-23; 62 tasks across 10 phases).

**Escalation anchors**: R1 (Heuristic A subsume signal surfaces at T004 OR T010 not complete by Day 1 EOD — user tie-break gate), MEDIUM-4 (architect edit ownership on FR-7 five-callsite carry-over at T026/T027), R2 (regeneration surface drift on `agentic-app` — Q4 fallback to new `advisory-app` ~0.5 day), HIGH-1 (buffer-day budget model — T055 R5 polish consumed at Wave 2.2 PM, not buffer), HIGH-2 (delivery retrospective slotting at T057 Wave 2.3 PM or Wednesday buffer).

---

## 1. Agent Assignment Matrix

All 62 tasks mapped to exact `subagent_type` values. Parallel Group column indicates which tasks may run concurrently within a wave (PG-N notation scoped to the wave). Assignments honor:
- **T004 / T026 / T027** → `architect` per MEDIUM-4 edit ownership (Heuristic A verification + FR-7 five-callsite reconciliation are architect-owned)
- **T005 / T038 / T039** → `tester` (pytest authoring + regen validation + backward-compat byte-identity)
- **T055** → `code-reviewer` (NFR-6 clearly-fictional framing double-check per HIGH-1)
- All markdown/YAML authoring, grep audits, and regen pipeline steps → `senior-backend-engineer`

| Task ID | Phase | Agent (`subagent_type`) | Parallel Group | Notes |
|---------|-------|-------------------------|----------------|-------|
| T001 | Phase 1 Setup | `senior-backend-engineer` | PG-Setup-1 | Working-directory + branch verification; trivial shell + read check |
| T002 | Phase 1 Setup | `senior-backend-engineer` | PG-Setup-1 | Create `.claude/skills/tachi-misinformation/references/` directory |
| T003 | Phase 1 Setup | `senior-backend-engineer` | PG-Setup-1 | Create `tests/scripts/fixtures/misinformation/` directory |
| **T004** | **Phase 2 Wave 1.0** | **`architect`** | **sequential (blocking)** | **Heuristic A verification (MEDIUM-4 / R1 anchor); ADR-030 Decision 1 scope-bound inheritance; memo to `.aod/results/heuristic-a-verification.md`** |
| T005 | Phase 2 Wave 1.1 | `tester` | PG-Wave1.1-A | Regex unit test at `tests/scripts/test_misinformation.py` — MUST FAIL before T006 |
| T006 | Phase 2 Wave 1.1 | `senior-backend-engineer` | sequential after T005 | Schema bump 1.6→1.7 + `MI` regex extension + `MI-1` example; atomic commit; verify T005 now passes |
| T007 | Phase 2 Wave 1.1 | `senior-backend-engineer` | PG-Wave1.1-B | Valid `MI-1` fixture with `source_attribution` LLM09 primary + CWE-345 related |
| T008 | Phase 2 Wave 1.1 | `senior-backend-engineer` | PG-Wave1.1-B | Invalid-attribution fixture citing AML.T0042 (confirmed absent) for F-A2 rejection test |
| T009 | Phase 2 Wave 1.1 | `senior-backend-engineer` | PG-Wave1.1-C | ADR-031 skeleton — Status: Proposed; 9 numbered-decision placeholders |
| **T010** | **Phase 2 Wave 1.1** | **`senior-backend-engineer`** | **sequential after T009** | **ADR-031 Decisions D1-D9 populated: D2 Heuristic A three-way + ADR-030 Decision 1 cross-ref; D8 regex-extension 2nd application; D9 CWE-1039 deliberate exclusion — R1 gate anchor** |
| T011 | Phase 2 Wave 1.1 | `senior-backend-engineer` | sequential after T010 | ADR-031 Cross-References — ADR-021/023/026/027/028/029/030 |
| T012 | Phase 2 Wave 1.1 | `senior-backend-engineer` | PG-Wave1.1-D | Pre-Wave 4 static DFD inspection — 12-keyword FP dry-run on 6 baselines; output to `specs/206-.../dispatch-fp-check.md` |
| T013 | Phase 3 Wave 2 | `senior-backend-engineer` | PG-Wave2-A | `detection-patterns.md` frontmatter + Overview + Detection Scope (12 keywords Q2) + DFD Element Types (Process only Q3) |
| T014 | Phase 3 Wave 2 | `senior-backend-engineer` | sequential after T013 | 5 numbered pattern categories (Q1); anti-indicator per category (MEDIUM-5); worked example clearly-fictional framing (NFR-6); primary/related citations including prose-only AML.T0042 + NIST AI 600-1 |
| T015 | Phase 3 Wave 2 | `senior-backend-engineer` | PG-Wave2-A | `README.md` companion skill — ≤50 lines, mirror `tachi-output-integrity` shape |
| T016 | Phase 3 Wave 2 | `senior-backend-engineer` | PG-Wave2-B | `misinformation.md` agent skeleton — 5-section canonical shape per ADR-023, no `agentic_pattern` (FR-016) |
| T017 | Phase 3 Wave 2 | `senior-backend-engineer` | sequential after T016 | Complete `## Detection Workflow` steps 1-6; FR-011 two-part emission gate (keyword AND factual-output indicator) |
| T018 | Phase 3 Wave 2 | `senior-backend-engineer` | PG-Wave2-C | Structural validation — line count ≤150, 1 `**MANDATORY**: Read`, zero MAESTRO refs |
| T019 | Phase 4 Wave 2 | `senior-backend-engineer` | sequential after T016 | 2-3 worked `MI-{N}` example findings (medical summarizer / legal research / financial advisory) with specific mitigations |
| T020 | Phase 4 Wave 2 | `senior-backend-engineer` | sequential after T014 | FR-017 three-sub-class predicate in each worked example description; NFR-6 clearly-fictional framing verification |
| T021 | Phase 4 Wave 2 | `senior-backend-engineer` | PG-Wave2-D | Mitigation specificity sanity grep; output to `.aod/results/wave2-mitigation-specificity-check.md` |
| T022 | Phase 5 Wave 5 | `senior-backend-engineer` | PG-Wave5-A | ADR-031 Proposed → Accepted transition; provisional PR row in Revision History |
| T023 | Phase 5 Wave 5 | `senior-backend-engineer` | sequential after T022 | ADR-031 body completeness check (D1-D9, Consequences, Cross-Refs, Revision History); output to `.aod/results/adr-031-completeness-check.md` |
| T024 | Phase 5 Wave 5 | `senior-backend-engineer` | sequential after T023 | Agent `## Purpose` three-signal-class distinctness — forward-refs to `prompt-injection` + `output-integrity` (US3 AC) |
| **T025** | **Post-Merge** | **`senior-backend-engineer`** | **post-merge only (decoupled from T056)** | **ADR-031 Revision History short-SHA fill after squash-merge (ADR-027/028/029/030 precedent)** |
| **T026** | **Phase 6 Wave 3** | **`architect`** | **PG-Wave3-A** | **Orchestrator.md edits (MEDIUM-4 architect-owned): dispatch insert + line 296 sequential-mode quintet + line 370 LLM Threats row quintet** |
| **T027** | **Phase 6 Wave 3** | **`architect`** | **PG-Wave3-A** | **Dispatch-rules.md edits (MEDIUM-4 architect-owned): LLM quintet extension + line 120 table row + trigger-keyword rules section** |
| T028 | Phase 6 Wave 3 | `senior-backend-engineer` | PG-Wave3-A | `finding-format-shared.md` `consumers:` list insert between `output-integrity` and `risk-scorer` (tier-grouping per FR-5) |
| T029 | Phase 6 Wave 3 | `senior-backend-engineer` | sequential after T028 | Structural-diff validation — ADR-023 Decision 3 `## ` heading byte-identity enforcement; output to `.aod/results/wave3-structural-diff-check.md` |
| T030 | Phase 6 Wave 3 | `senior-backend-engineer` | sequential after T026+T027 | Five-callsite quintet consistency grep audit (MEDIUM-3 anchor); output to `.aod/results/wave3-quintet-consistency-check.md` |
| T031 | Phase 7 Wave 4 | `architect` | sequential (decision gate) | Q4 fallback decision: extend `agentic-app` vs new `advisory-app` (~0.5 day buffer if fallback); output to `.aod/results/wave4-regen-target-decision.md` |
| T032 | Phase 7 Wave 4 | `senior-backend-engineer` | sequential after T031 | Extend `examples/agentic-app/architecture.md` with factual-output sub-component (≥2 of 12 keywords + ≥1 factual indicator) |
| T033 | Phase 7 Wave 4 | `senior-backend-engineer` | sequential after T032 | Run `/tachi.threat-model` with `SOURCE_DATE_EPOCH=1700000000`; confirm ≥1 `MI-{N}` + preserved F-1 OI + LLM findings |
| T034 | Phase 7 Wave 4 | `senior-backend-engineer` | sequential after T033 | Run `/tachi.risk-score`; verify `category: llm` processing on MI findings (FR-014) |
| T035 | Phase 7 Wave 4 | `senior-backend-engineer` | sequential after T034 | Run `/tachi.compensating-controls`; verify MI processing through category: llm code paths |
| T036 | Phase 7 Wave 4 | `senior-backend-engineer` | sequential after T035 | Run `/tachi.infographic all` — regenerate 6 JPEGs + specs |
| T037 | Phase 7 Wave 4 | `senior-backend-engineer` | sequential after T036 | Run `/tachi.security-report` — regenerate `security-report.pdf` + `.pdf.baseline` |
| T038 | Phase 7 Wave 4 | `tester` | PG-Wave4-A | F-A2 referential integrity pytest — `test_misinformation.py` on regenerated MI findings (AML.T0042 absence check per FR-5) |
| T039 | Phase 7 Wave 4 | `tester` | PG-Wave4-A | Backward-compat byte-identity pytest under `SOURCE_DATE_EPOCH=1700000000` — 5/5 non-factual baselines (R2 anchor) |
| T040 | Phase 7 Wave 4 | `senior-backend-engineer` | PG-Wave4-A | Three-signal-class discipline verification (SC-014); output to `.aod/results/wave4-three-signal-class-check.md` |
| T041 | Phase 7 Wave 4 | `senior-backend-engineer` | PG-Wave4-A | Git-stage regenerated artifacts for commit |
| T042 | Phase 8 Wave 5 | `senior-backend-engineer` | PG-Wave5-B | SC-001 — agent file structural validation (delegates to T018 result) |
| T043 | Phase 8 Wave 5 | `senior-backend-engineer` | PG-Wave5-B | SC-002 — pattern catalog ≥5 categories with worked example + anti-indicator + citations + keywords + DFD types |
| T044 | Phase 8 Wave 5 | `senior-backend-engineer` | PG-Wave5-B | SC-003 — additive-only finding-format edit (delegates to T029 result) |
| T045 | Phase 8 Wave 5 | `senior-backend-engineer` | PG-Wave5-B | SC-004 — regenerated agentic-app MI findings surfaced; non-qualifying baselines emit zero (two-part gate) |
| T046 | Phase 8 Wave 5 | `senior-backend-engineer` | PG-Wave5-B | SC-005 — ADR-031 Accepted with all 9 decisions + cross-refs + Revision History (delegates to T023) |
| T047 | Phase 8 Wave 5 | `tester` | PG-Wave5-B | SC-006 — byte-identity pass on 5 non-factual baselines (delegates to T039) |
| T048 | Phase 8 Wave 5 | `senior-backend-engineer` | PG-Wave5-B | SC-007 — regenerated MI findings carry grounding/verification mitigations + LLM09 + `source_attribution` |
| T049 | Phase 8 Wave 5 | `senior-backend-engineer` | PG-Wave5-B | SC-008 — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json` |
| T050 | Phase 8 Wave 5 | `senior-backend-engineer` | PG-Wave5-B | SC-009 — 24-file zero-edit grep audit (22 original + F-1's 2); ADR-023 invariant preservation |
| T051 | Phase 8 Wave 5 | `tester` | PG-Wave5-B | SC-010 — F-A2 validation on regen (delegates to T038) |
| T052 | Phase 8 Wave 5 | `senior-backend-engineer` | PG-Wave5-B | SC-011 — zero MAESTRO refs (delegates to T018) |
| T053 | Phase 8 Wave 5 | `senior-backend-engineer` | PG-Wave5-B | SC-012 — schema_version `"1.7"` + MI regex + regex test pass (delegates to T006) |
| T054 | Phase 8 Wave 5 | `senior-backend-engineer` | PG-Wave5-B | SC-014 — three-signal-class discipline (delegates to T040) |
| **T055** | **Phase 8 Wave 5** | **`code-reviewer`** | **sequential after PG-Wave5-B** | **R5 / NFR-6 code-review double-check (HIGH-1 buffer-day budget — consumed at Wave 2.2 PM, NOT buffer): pattern-catalog worked examples clearly-fictional framing compliance; output to `.aod/results/wave5-nfr6-compliance-check.md`** |
| T056 | Phase 8 Wave 5 | `senior-backend-engineer` | sequential after T055 | PR open `206-misinformation-threat-agent` → `main`; triple-review request |
| T057 | Phase 9 Wave 6 | `senior-backend-engineer` | PG-Wave6 | Delivery retrospective (HIGH-2 anchor): Wave 2.3 PM if ≥1h residual, else Wednesday buffer |
| T058 | Phase 9 Wave 6 | `senior-backend-engineer` | post-merge | SC-013 BLP-01 Coverage Matrix update — LLM09:2025 Planned → Covered with F-2 named |
| T059 | Phase 9 Wave 6 | `senior-backend-engineer` | contingent | R2 buffer-day absorption OR Q4 advisory-app fallback (~0.5 day consumption) |
| T060 | Phase 10 Polish | `senior-backend-engineer` | PG-Polish | Update `CLAUDE.md` Recent Changes section (Features 180/189/194/201 pattern) |
| T061 | Phase 10 Polish | `senior-backend-engineer` | PG-Polish | Quickstart.md Step 12 end-to-end smoke test; output to `.aod/results/quickstart-smoke.md` |
| T062 | Phase 10 Polish | `senior-backend-engineer` | PG-Polish | Verify `examples/README.md` no-update — F-2 extends existing example (no new entry unless R2 fallback to `advisory-app`) |

**Agent-count summary (62 assigned tasks)**:

| Agent | Task count | Share |
|-------|-----------|-------|
| `senior-backend-engineer` | 54 | 87.1% |
| `tester` | 4 | 6.5% |
| `architect` | 3 | 4.8% |
| `code-reviewer` | 1 | 1.6% |
| (others) | 0 | 0% |

**Note on distribution vs PRD capacity-check ranges**: Raw task count is heavy on `senior-backend-engineer` because most F-2 tasks are markdown/YAML authoring, grep audits, and regen pipeline commands — all well-suited to the backend engineer agent. PRD capacity check frames load as percent-of-day rather than percent-of-tasks; see Section 5 for the day-based load model (senior-backend-engineer 60-70% Day 1 / 40-50% Day 2; tester 30-40% Day 1 / 20% Day 2; code-reviewer 20% Day 2 PM; architect 30-60 min Day 1 + 30 min Day 2 PM), which honors the PRD envelope.

---

## 2. Parallel Execution Waves

Each wave advances only after its Quality Gate (Section 3) is green. Wave-internal parallel groups (PG-N) may run concurrently; sequential anchors within a wave are called out.

### Wave 1.0 — Architect Heuristic A Verification (Day 1 AM, 30-60 min)

**Blocking critical path**: Wave 1.1 cannot begin until T004 verification memo is committed.

| Parallel Group | Tasks | Agent |
|---------------|-------|-------|
| (sequential, single) | T004 | `architect` |

**Gate**: `.aod/results/heuristic-a-verification.md` committed with explicit factual-integrity signal-class verification (scoped to human-victim + decision-cascade-victim per ADR-030 Decision 1 cross-reference). Subsume signal → R1 escalation.

### Wave 1.1 — Schema Lock + ADR-031 Proposed (Day 1 AM/PM, 5-parallel)

**Maximum parallelism**: 5 tracks can proceed concurrently once Wave 1.0 completes.

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| PG-Wave1.1-A | T005 → T006 | `tester` (T005), `senior-backend-engineer` (T006) | Test-first discipline; T006 atomic (schema + regex + example) |
| PG-Wave1.1-B | T007, T008 | `senior-backend-engineer` | Independent fixture authoring (valid + invalid-attribution) |
| PG-Wave1.1-C | T009 → T010 → T011 | `senior-backend-engineer` | ADR-031 Proposed sequential chain (skeleton → 9 decisions → cross-refs) |
| PG-Wave1.1-D | T012 | `senior-backend-engineer` | Independent dispatch FP dry-run (12-keyword grep on 6 baselines) |
| (Setup) | T001, T002, T003 | `senior-backend-engineer` | Folds into Wave 1.1 afternoon if not pre-completed |

**Gate — R1 hard escalation trigger**: If T004 Heuristic A verification surfaces subsume signal OR T010 not complete by Day 1 EOD (Monday 2026-04-27 23:59 local), surface user tie-break before Day 2 AM. **Do NOT proceed to Wave 2 without ADR-031 Proposed commit.**

### Wave 2 — Pattern Catalog + Agent Authoring + Mitigation Text (Day 1 PM, 0.5d)

**3-parallel core + sequential micro-chains**. US1 (T013-T018) and US2 (T019-T021) run interleaved.

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| PG-Wave2-A | T013 → T014, T015 | `senior-backend-engineer` | Pattern catalog chain (5 categories + anti-indicators + NFR-6) + companion README |
| PG-Wave2-B | T016 → T017, T019 | `senior-backend-engineer` | Agent-file chain (5-section shape + 6-step workflow + FR-011 two-part gate) + example findings |
| PG-Wave2-C | T018 | `senior-backend-engineer` | Structural validation (≤150 lines, 1 MANDATORY Read, zero MAESTRO) |
| PG-Wave2-D | T020, T021 | `senior-backend-engineer` | FR-017 three-sub-class predicate + mitigation specificity grep |

**Gate**: T018 structural check green; T021 mitigation-specificity check green; T020 NFR-6 clearly-fictional framing verified; `.aod/results/wave2-*.md` artifacts committed.

### Wave 3 — Orchestrator Registration + F-1 Five-Callsite Carry-Over Reconciliation + Shared-Reference Edits (Day 2 AM, 0.3d)

**3-parallel file edits + sequential structural diff + quintet consistency audit**. T026/T027 architect-owned per MEDIUM-4.

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| PG-Wave3-A | T026, T027, T028 | `architect` (T026/T027), `senior-backend-engineer` (T028) | Three different files; independent edits; T026/T027 architect-owned (MEDIUM-4) |
| PG-Wave3-A-tail | T029 | `senior-backend-engineer` | Sequential after T028; ADR-023 Decision 3 enforcement |
| PG-Wave3-B | T030 | `senior-backend-engineer` | 5-callsite quintet consistency grep audit (MEDIUM-3 anchor) after T026+T027 |

**Gate**: T029 structural-diff empty on `## ` heading changes; T030 five-callsite quintet consistency green (all 5 callsites reference `prompt-injection, data-poisoning, model-theft, output-integrity, misinformation`).

### Wave 4 — Example Regeneration + Backward-Compat Verification (Day 2 PM, 0.5d)

**Pipeline regen is sequential** (T032→T037 chained on artifact dependency); **verification is 4-parallel** (T038/T039/T040/T041). T031 is architect-owned decision gate.

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| (decision gate) | T031 | `architect` | Q4 fallback decision (extend agentic-app vs new advisory-app) |
| (sequential) | T032 → T033 → T034 → T035 → T036 → T037 | `senior-backend-engineer` | Pipeline regen chain (architecture extension → threat-model → risk-score → controls → infographics → security-report) |
| PG-Wave4-A | T038, T039, T040, T041 | `tester` (T038/T039), `senior-backend-engineer` (T040/T041) | 4-parallel verifications + git-stage |

**Gate**: T039 byte-identity 5/5 pass on non-factual baselines; T038 F-A2 validation green (AML.T0042 absence confirmed); ≥1 `MI-{N}` finding in regenerated `agentic-app/threats.md`; T040 three-signal-class discipline green.

### Wave 5 — ADR-031 Accepted + SC Sweep + NFR-6 Double-Check + PR (Day 2 PM, 0.3d)

**Maximum parallelism**: 13 SC checks run concurrently. ADR-Accepted transition runs parallel to SC sweep. T055 code-reviewer NFR-6 double-check sequential after SC sweep. T055 is R5 consumed at Wave 2.2 PM per HIGH-1 (not buffer).

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| PG-Wave5-A | T022 → T023, T024 | `senior-backend-engineer` | ADR-031 Accepted transition + completeness check + agent Purpose forward-ref |
| PG-Wave5-B | T042-T054 | `senior-backend-engineer` (11), `tester` (2 — T047 / T051) | 13-parallel SC validation sweep on independent surfaces |
| (sequential gate) | T055 | `code-reviewer` | NFR-6 compliance double-check (HIGH-1 anchor) after PG-Wave5-B green |
| (sequential tail) | T056 | `senior-backend-engineer` | PR open after T055 green |

**Gate — Pre-PR**: All 14 SCs green (13 in Wave 5 sweep + SC-013 BLP-01 Coverage Matrix at T058); ADR-031 Status: Accepted; T055 NFR-6 compliance green; triple-review request posted on PR.

### Wave 6 — Delivery Retrospective + BLP-01 Coverage Matrix Update (Day 2 PM or Day 3 Buffer)

HIGH-2 delivery retrospective slotting + post-merge Coverage Matrix update + contingent R2 buffer absorption.

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| PG-Wave6 | T057 | `senior-backend-engineer` | Delivery retrospective — Wave 2.3 PM if ≥1h residual, else Wednesday buffer (HIGH-2) |
| (post-merge) | T058 | `senior-backend-engineer` | SC-013 BLP-01 Coverage Matrix — LLM09:2025 Planned → Covered |
| (contingent) | T059 | `senior-backend-engineer` | R2 regeneration friction absorption OR Q4 advisory-app fallback (~0.5 day) |

### Post-Merge — SHA Fill (decoupled from T056)

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| (post-squash only) | T025 | `senior-backend-engineer` | ADR-031 Revision History short-SHA fill; consistent with ADR-027/028/029/030 pattern |

### Polish Lane — Parallel with Wave 5 or Wave 6 (Day 2 PM / Day 3)

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| PG-Polish | T060, T061, T062 | `senior-backend-engineer` | Safe to run pre-merge alongside Wave 5 SC sweep |

---

## 3. Quality Gates Between Waves

Each gate is a binary go/no-go before advancing. Failures escalate to team-lead + architect per the Escalation Paths section. All gate artifacts write to `.aod/results/` or `specs/206-.../`.

### Gate 1.0 → 1.1 — Heuristic A Verification Committed

**Must be green**:
- [ ] `.aod/results/heuristic-a-verification.md` exists with explicit factual-integrity signal-class verification
- [ ] ADR-030 Decision 1 scope-bound inheritance documented (machine-victim bytes/strings/syntax left to F-1; human-victim + decision-cascade-victim factual-content claimed by F-2)
- [ ] Working directory clean

**Blocker if red**: Wave 1.1 cannot begin; R1 user tie-break escalation required.

### Gate 1.1 → 2 — Schema Lock + ADR-031 Proposed

**Must be green (R1 hard gate)**:
- [ ] `schemas/finding.yaml` bumped to `schema_version: "1.7"` with `MI` regex extension + `MI-1` example — T006 atomic commit
- [ ] `tests/scripts/test_misinformation.py` regex test passes — T005 green post-T006
- [ ] `docs/architecture/02_ADRs/ADR-031-misinformation-agent.md` Status: Proposed committed with 9 Decisions (D1-D9 including D8 regex 2nd application + D9 CWE-1039 exclusion) and Cross-References populated — T009/T010/T011
- [ ] `tests/scripts/fixtures/misinformation/{valid_mi_finding,invalid_attribution_finding}.yaml` committed — T007/T008
- [ ] `specs/206-misinformation-threat-agent/dispatch-fp-check.md` committed — T012
- [ ] All Day-1-EOD completions (Monday 2026-04-27 23:59 local)

**Blocker if red**: R1 user tie-break escalation fires; Day 2 AM work does not begin until resolved.

### Gate 2 → 3 — Agent + Companion Structural Compliance

**Must be green**:
- [ ] `.claude/agents/tachi/misinformation.md` ≤150 lines, 1 `**MANDATORY**: Read`, zero MAESTRO refs (T018)
- [ ] `.claude/skills/tachi-misinformation/references/detection-patterns.md` has 5 pattern categories with worked example + anti-indicator + primary/related citations + trigger keywords + DFD element types (T014)
- [ ] `.claude/skills/tachi-misinformation/README.md` ≤50 lines companion (T015)
- [ ] Mitigation specificity grep green — no "ground the llm" / "verify the output" / "add hitl" / "sanitize" without adjacent specific mechanism (T021)
- [ ] Each pattern category worked example uses clearly-fictional framing per NFR-6 (T020)
- [ ] FR-017 three-sub-class predicate explicit in each worked example description (T020)

**Blocker if red**: Fix agent or companion; do not register in orchestrator until structural checks pass.

### Gate 3 → 4 — Orchestrator Registration + Quintet Consistency

**Must be green**:
- [ ] `orchestrator.md` dispatch list includes `misinformation` after `output-integrity` (T026)
- [ ] `orchestrator.md:296` sequential-mode text extended to five-agent quintet (T026 / MEDIUM-3)
- [ ] `orchestrator.md:370` LLM Threats row extended to five-agent quintet (T026 / MEDIUM-3)
- [ ] `dispatch-rules.md` LLM quartet → quintet (lines 71-74 extended) with FR-011 two-part emission rule (T027)
- [ ] `dispatch-rules.md:120` table row extended to quintet (T027 / MEDIUM-3)
- [ ] `dispatch-rules.md` trigger-keyword rules section extended with 12-keyword set (T027 / MEDIUM-3)
- [ ] `finding-format-shared.md` `consumers:` list insert between `output-integrity` and `risk-scorer` (T028)
- [ ] `git diff main -- finding-format-shared.md | grep -E '^[+-]## '` returns empty — ADR-023 Decision 3 enforcement (T029)
- [ ] Five-callsite quintet consistency grep audit green (T030 / MEDIUM-3) — all 5 callsites reference `prompt-injection, data-poisoning, model-theft, output-integrity, misinformation`

**Blocker if red**: Structural-diff failure = ADR-023 violation; quintet inconsistency = MEDIUM-3 rollback required before Wave 4.

### Gate 4 → 5 — Regeneration Surface Clean

**Must be green (R2 anchor)**:
- [ ] T031 Q4 decision: extend `agentic-app` confirmed (default) OR architect + team-lead approved fallback to new `advisory-app` (~0.5 day consumption)
- [ ] `/tachi.threat-model` → `/tachi.risk-score` → `/tachi.compensating-controls` → `/tachi.infographic all` → `/tachi.security-report` all green on `examples/agentic-app/` (T032-T037)
- [ ] ≥1 `MI-{N}` finding surfaced in regenerated `agentic-app/threats.md`; F-1 `OI-{N}` preserved; existing `LLM-{N}` preserved
- [ ] `pytest tests/scripts/test_misinformation.py` green — F-A2 validation passes with AML.T0042 absence confirmed (T038)
- [ ] `SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py` — 5/5 non-factual baselines byte-identical (T039)
- [ ] Three-signal-class discipline verified in regenerated `threat-report.md` category: llm section — `LLM-{N}`, `OI-{N}`, `MI-{N}` adjacent (not synthesized) with own `source_attribution` primaries (LLM01 / LLM05 / LLM09) (T040)
- [ ] Regenerated artifacts git-staged (T041)

**Blocker if red — R2 escalation**: Byte-identity break on `web-app` / `microservices` / `ascii-web-api` / `mermaid-agentic-app` / `free-text-microservice` = root-cause before merge; if `agentic-app` cumulative-state cost too high, invoke Q4 fallback to new `advisory-app` (~0.5 day buffer consumption).

### Gate 5 → PR-Open — All SCs + NFR-6 Green

**Must be green**:
- [ ] All 14 spec SCs (13 in Wave 5 sweep T042-T054 + SC-013 BLP-01 Coverage Matrix at T058) verified
- [ ] ADR-031 Status: Accepted with provisional merge date + placeholder PR number (T022)
- [ ] ADR-031 body completeness confirmed — D1-D9, Cross-Refs, Revision History (T023)
- [ ] Agent `## Purpose` three-signal-class forward-refs verified — distinct from `prompt-injection` input-side + distinct from `output-integrity` per ADR-030 Decision 1 + scoped to factual-integrity (T024)
- [ ] 24-file zero-edit grep audit returns clean — 22 original + F-1's 2 files (T050)
- [ ] T055 code-reviewer NFR-6 compliance double-check green — clearly-fictional framing on all worked examples (healthcare/legal/finance)

**Blocker if red**: Any SC fail or NFR-6 non-compliance = do not open PR; refine per specific SC or re-frame worked examples.

### Post-Merge Gate

**Must be green**:
- [ ] PR squash-merged; short-SHA recorded
- [ ] T025 ADR-031 Revision History updated with squash commit short-SHA — consistent with ADR-027/028/029/030 lineage
- [ ] T058 BLP-01 Coverage Matrix updated — LLM09:2025 row transitions Planned → Covered with F-2 (Feature 206) named as closure feature

---

## 4. Time Estimates per Wave

**Plan default**: 2-day critical path + Wednesday buffer per PRD HIGH-1 buffer-day budget model.

### Default Timeline (Heuristic A Three-Way Split Preserved)

| Wave | Day / Time | Duration | Critical Path Tasks | Notes |
|------|-----------|----------|--------------------|------|
| Setup + Wave 1.0 | Day 1 AM (Monday 2026-04-27, 09:00-10:30) | 60-90 min | T001-T003, T004 | Heuristic A verification is critical path (architect 30-60 min) |
| Wave 1.1 | Day 1 AM/PM (10:30-17:00) | 5-6 hours | T005, T006, T009, T010, T011 | 5-parallel tracks cut wall-clock; R1 gate by EOD |
| Wave 2 (US1 + US2) | Day 1 PM (17:00-onwards, spillover) | **0.5d envelope** | T013-T021 | Pattern catalog + agent authoring + mitigation text + NFR-6 framing |
| Wave 3 | Day 2 AM (Tuesday 2026-04-28, 09:00-11:30) | **0.3d envelope (~2.5h)** | T026, T027, T028, T029, T030 | Orchestrator registration + 5-callsite quintet reconciliation (architect-owned T026/T027) |
| Wave 4 | Day 2 AM/PM (11:30-17:00) | **0.5d envelope (~5h)** | T031-T041 | Pipeline regen sequential; 4-parallel verifications; three-signal-class discipline check |
| Wave 5 (ADR + SC + NFR-6 + PR) | Day 2 PM (17:00-20:00) | **0.3d envelope (~2.5h)** | T022-T024, T042-T056 | ADR Accepted + 13-parallel SC sweep + code-reviewer NFR-6 (20% Day 2 PM) + PR open |
| Wave 6 (Retrospective + Coverage Matrix) | Day 2 PM or Day 3 | **contingent** | T057, T058 | HIGH-2 retrospective slotting; T058 post-merge |
| **Wednesday buffer** | **Day 3 (2026-04-29)** | **0-1d** | **T057 retrospective if not Wave 2.3 PM; T059 R2 absorption; absorbed into merge cycle** | **Per HIGH-1 buffer-day budget model** |
| Post-merge | Post-PR merge | 15 min | T025, T058 | ADR-031 SHA fill + BLP-01 Coverage Matrix update |

**Day 2 landing target**: PR opened by Tuesday 2026-04-28 EOD with all 14 SCs green + NFR-6 compliance verified.

### Wednesday Buffer Policy (per HIGH-1 buffer-day budget model)

- If T057 delivery retrospective authored Wave 2.3 PM (≥1h residual) → Wednesday absorbs R2 regeneration friction OR merge cycle review lag.
- If R2 materializes (regeneration friction beyond extend-in-place) → Wednesday consumes Q4 fallback authoring of `examples/advisory-app/` (~0.5 day, T059).
- If all else green by Day 2 EOD and retrospective not yet authored → Wednesday is primary T057 retrospective authoring window.
- T055 R5 NFR-6 code-review double-check is **NOT** buffer-consumed — HIGH-1 anchors it at Wave 2.2 PM (Day 2 PM during SC sweep tail).

---

## 5. Capacity Check

PRD capacity check frames load as percent-of-day rather than percent-of-tasks. This section reconciles the 87% raw task-count concentration on `senior-backend-engineer` with the PRD day-based load model, and verifies headroom.

### Load by Agent — Day-Based Model (per PRD envelope)

| Agent | Day 1 Load | Day 2 Load | Notes |
|-------|-----------|-----------|-------|
| `senior-backend-engineer` | **60-70%** | **40-50%** | Pattern catalog + agent authoring (Wave 2) dominates Day 1 PM; Wave 3 shared edit (T028) + Wave 4 pipeline regen (T032-T037) + Wave 5 SC sweep Day 2 |
| `tester` | **30-40%** | **20%** | T005 regex test + Day 1 PG-Wave1.1-A; Day 2 AM T038 F-A2 validation + T039 byte-identity + T047/T051 Wave 5 SC checks |
| `architect` | **30-60 min** | **30 min** | Day 1 AM T004 Heuristic A verification; Day 2 AM T026/T027 architect-owned orchestrator + dispatch edits + T031 Q4 decision gate |
| `code-reviewer` | 0% | **20% Day 2 PM** | Single task T055 NFR-6 compliance double-check consumed at Wave 2.2 PM per HIGH-1 (not buffer) |

**Verdict**: Capacity within PRD envelope. `senior-backend-engineer` at 60-70% Day 1 / 40-50% Day 2 headroom preserved per tasks.md team-lead sign-off. `tester` light load (30-40% / 20%); `architect` thin-slice ownership on decision-critical items; `code-reviewer` single-shot NFR-6 gate.

### Load by Agent — Raw Task-Count Distribution

| Agent | Assigned Tasks | Est. Hours (2d envelope) | Capacity Window (2d = 16h) | Utilization (task-hour basis) |
|-------|----------------|--------------------------|----------------------------|-------------------------------|
| `senior-backend-engineer` | 54 | ~10-12h | 16h | **62-75%** (within PRD Day-1 60-70% target at the midpoint) |
| `tester` | 4 | ~2-3h | 16h | **12-19%** (light load; ample headroom) |
| `architect` | 3 | ~2h | 16h | **12%** (thin-slice decision ownership) |
| `code-reviewer` | 1 | ~30-45 min | 16h | **3-5%** (single NFR-6 review) |

**Raw vs day-based reconciliation**: Raw percent (87%) reflects task-count concentration because most F-2 tasks are markdown/YAML operations well-suited to `senior-backend-engineer`. Day-based percent (60-70% / 40-50%) reflects wall-clock hours against the 2-day envelope, which is the canonical PRD measure. Both are within envelope.

### Mitigation Strategies (if `senior-backend-engineer` saturates)

1. **Batch Wave 4 pipeline regen (T033-T037) as orchestrated command sequence** — wall-clock dominated by tool invocation.
2. **Promote T060 / T061 / T062 polish tasks to earliest-available window** — small, self-contained, parallelizable with Wave 5 SC sweep.
3. **Escalate to team-lead for re-balancing** if R2 materializes AND Q4 fallback invoked (T059 adds ~0.5 day — may shift Day 2 tail into Wednesday buffer).

### `tester` Capacity Reserve

With 30-40% Day 1 / 20% Day 2 utilization, `tester` has room to absorb:
- Additional regression fixtures if T038 F-A2 validation flags schema-contract edge cases
- Additional FP sweep on non-baseline examples if R2 surfaces
- Pytest suite re-runs if any mid-wave commit breaks green

### `architect` Capacity Reserve

With 30-60 min Day 1 + 30 min Day 2 PM utilization, `architect` has room to:
- Handle R1 Heuristic A re-verification if subsume signal surfaces mid-wave
- Handle T031 Q4 decision gate with full deliberation (~15-30 min)
- Author any supplementary ADR amendment if D8 regex-extension rule or D9 CWE-1039 exclusion needs clarification

### `code-reviewer` Load

Single task T055 (~30-45 min NFR-6 compliance check) = 20% Day 2 PM consumption. Agent can be assigned additional pre-merge PR-phase review tasks post-T056 if needed.

---

## 6. Escalation Paths

Five escalation anchors defined in tasks.md + PRD. All escalations write to `.aod/results/escalation-log.md` with anchor, trigger, and resolution timestamp.

### R1 — Heuristic A Subsume Signal OR Day-1-EOD Hard Gate

**Trigger**: T004 verification surfaces subsume-into-output-integrity signal, OR T010 (ADR-031 Proposed with D1-D9) not complete by Day 1 EOD (Monday 2026-04-27 23:59 local).

**Escalation action**: Surface user tie-break notice before Day 2 AM start. Do NOT proceed to Wave 2 without ADR-031 Proposed commit.

**Escalation participants**:
- `user` — final decision authority if Heuristic A three-way split challenged
- `architect` — brief status report on verification outcome or ambiguity
- `team-lead` — timeline impact (Wednesday buffer consumed likely)

**Resolution paths**:
1. **Heuristic A three-way split confirmed** (default) → Wave 2 proceeds with 5-category pattern catalog + factual-integrity scoping.
2. **Subsume signal with high confidence** → user tie-break on feature scope: subsume MI into F-1 (closes F-2) OR re-frame F-2 with narrower scope.
3. **Ambiguity** → user tie-break with architect + team-lead rationale.

**Escalation artifact**: `.aod/results/r1-heuristic-a-escalation-YYYY-MM-DD.md`

### R2 — Regeneration Surface Drift / Q4 Fallback

**Trigger**: T039 backward-compat byte-identity pytest fails on ANY non-factual baseline (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`), OR `agentic-app` cumulative-state cost exceeds convention-preservation benefit at T031 Q4 decision point.

**Escalation action**: PAUSE Wave 4 or PR open; root-cause OR invoke Q4 fallback.

**Escalation participants**:
- `architect` — assess whether break is shared-reference-edit induced (T028 non-additive), orchestrator-induced (T026/T027 leaked dispatch), or Q4-decision-tripped (fallback to new advisory-app)
- `senior-backend-engineer` — reproduce locally; isolate changed file
- `tester` — confirm break is deterministic vs flaky; verify `SOURCE_DATE_EPOCH` is set
- `team-lead` — timeline impact (Wednesday buffer consumed likely; ~0.5 day for Q4 fallback)

**Resolution paths**:
1. **Non-additive shared-reference edit** (ADR-023 violation) → revert T028; re-apply additively.
2. **Orchestrator dispatch leaked** → refactor T026/T027 to enforce FR-011 two-part gate; ensure `misinformation` fires only on factual-output indicator presence.
3. **Q4 fallback invoked** → author `examples/advisory-app/architecture.md` as new clean baseline (~0.5 day); add to Wave 4 regen target list; update `examples/README.md` entry in T062.

**Escalation artifact**: `.aod/results/r2-regeneration-drift-YYYY-MM-DD.md`

### MEDIUM-3 — Five-Callsite Quintet Consistency Failure

**Trigger**: T030 grep audit reveals pre-F-1 three-agent or post-F-1 four-agent (quartet) text still present at ANY of the 5 callsites (orchestrator.md:296, orchestrator.md:370, dispatch-rules.md LLM list lines 71-74, dispatch-rules.md:120, dispatch-rules.md trigger-keyword rules).

**Escalation action**: PAUSE Wave 4. Re-apply T026 or T027 edit at the flagged callsite(s).

**Escalation participants**:
- `architect` — re-apply MEDIUM-4-owned edit; re-verify quintet consistency
- `team-lead` — confirm Wave 3 gate re-green before Wave 4 start

**Resolution paths**:
1. **Single callsite mismatch** → targeted patch (~5-10 min); re-run T030; proceed.
2. **Systemic mismatch** (≥3 callsites) → architect reviews whether T026 or T027 edit pattern was misapplied; re-author both.

**Escalation artifact**: `.aod/results/medium-3-quintet-mismatch-YYYY-MM-DD.md`

### HIGH-1 — NFR-6 Code-Review Double-Check Failure

**Trigger**: T055 code-reviewer flags worked example(s) in `detection-patterns.md` or agent `## Example Findings` as using non-fictional framing (real institutional names, real clinician/lawyer/advisor identities, real regulatory citations).

**Escalation action**: PAUSE PR open (T056). Refine worked examples to clearly-fictional framing.

**Escalation participants**:
- `code-reviewer` — itemize flagged examples with specific violations
- `senior-backend-engineer` — re-frame worked examples (hypothetical / generic / synthetic qualifiers)
- `team-lead` — confirm re-review cycle ≤1 hour

**Resolution paths**:
1. **Single example flagged** → re-frame in-place (~10-15 min); re-run T055; proceed.
2. **Multiple examples flagged** → systematic re-framing across pattern catalog + agent examples (~30-60 min); absorb into Wave 2.2 PM per HIGH-1 budget.

**Escalation artifact**: `.aod/results/high-1-nfr6-compliance-YYYY-MM-DD.md`

### HIGH-2 — Delivery Retrospective Slotting

**Trigger**: No defect trigger — scheduling anchor only. HIGH-2 resolves retrospective timing: Wave 2.3 PM if ≥1h residual capacity post-PR-open, else Wednesday buffer.

**Escalation action**: None — routing decision only.

**Escalation participants**:
- `senior-backend-engineer` — authors T057 retrospective at chosen slot

**Resolution paths**:
1. **Wave 2.3 PM slot** (default if PR merges same-day with residual capacity) → retrospective mirrors F-1 same-day-as-delivery pattern.
2. **Wednesday buffer slot** (if Day 2 tight) → retrospective is primary buffer-day activity.

**Escalation artifact**: `specs/206-misinformation-threat-agent/delivery.md` (retrospective deliverable, not escalation)

### F-A2 Validation Failure at T038

**Trigger**: `pytest tests/scripts/test_misinformation.py` rejects regenerated `MI-{N}` findings for referential-integrity failures (e.g., `source_attribution` cites AML.T0042 or other catalog-absent ID).

**Escalation action**: Pattern worked examples likely cite catalog-absent IDs for `source_attribution` (as opposed to prose-only citation).

**Resolution**: Revise per FR-7 — confirm worked-example `source_attribution` cites only catalog-resolvable IDs (OWASP LLM09, CWE-345, CWE-223); AML.T0042 and NIST AI 600-1 §2.4 remain prose-only in Primary Sources list.

**Escalation artifact**: Root-cause in T038 pytest output; resolution commit referencing `.aod/results/fr-7-resolution.md`.

---

## 7. Handoff to Orchestrator

The orchestrator consumes this `agent-assignments.md` as input to drive execution. Handoff contract:

- **Wave sequencing**: Follow Section 2 strictly; do not advance past a gate in Section 3 without explicit green state.
- **Agent dispatch**: Use exact `subagent_type` values from Section 1 matrix; no improvisation or fallback substitution. **T004 / T026 / T027 / T031 architect-owned per MEDIUM-4**; **T005 / T038 / T039 tester-owned**; **T055 code-reviewer-owned**.
- **Parallel-group cohesion**: Dispatch all tasks in a parallel group (PG-N) in a single multi-task message when possible.
- **Gate reporting**: After each wave completes, emit a short completion report to team-lead with gate artifacts referenced.
- **Escalation invocation**: If any escalation anchor fires (R1 / R2 / MEDIUM-3 / HIGH-1 / F-A2), PAUSE and surface to team-lead + architect (and user for R1) before proceeding.

**Team-lead sign-off confirmation**: This `agent-assignments.md` inherits the triple APPROVED status from `tasks.md` (2026-04-23). No separate sign-off gate required for execution start, per the Triad governance matrix (team-lead authority on `agent-assignments.md`).

**Orchestrator entry command**: `/aod.build` (or `/aod.run` for full-lifecycle continuation).

---

**End of Agent Assignments — Feature 206**
