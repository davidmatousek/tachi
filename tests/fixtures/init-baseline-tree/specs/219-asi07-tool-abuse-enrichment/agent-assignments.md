---
feature: 219-asi07-tool-abuse-enrichment
artifact: agent-assignments.md
author: team-lead
date: 2026-04-25
branch: 219-asi07-tool-abuse-enrichment
source_tasks: specs/219-asi07-tool-abuse-enrichment/tasks.md
tasks_count: 67
waves_count: 5 (Wave 1.0 → Wave 1.1 → Wave 2 → Wave 3 → Wave 4 + Polish)
calendar:
  day_1: 2026-04-28 Tuesday
  buffer_day_1: 2026-04-29 Wednesday
  buffer_day_2: 2026-04-30 Thursday
outcome_default: Heuristic A enrichment-branch first execution preserved (1-day baseline + 2-day buffer)
outcome_alternate: Q3 fallback to maestro-reference / new minimal multi-agent fixture (~0.5d Buffer Day 1 consumption per PRD R1)
---

# Agent Assignments — Feature 219 ASI07 Tool-Abuse Enrichment

This artifact operationalizes the triple-approved `tasks.md` into agent-by-wave execution units. All assignments reference the exact `subagent_type` values from `.claude/agents/_README.md`. The orchestrator consumes this file to dispatch work; the team-lead consumes it to track capacity and escalate gates.

**Source of Truth**: `specs/219-asi07-tool-abuse-enrichment/tasks.md` (triple APPROVED 2026-04-25; 67 tasks across 9 phases).

**Escalation anchors**: R1 (catalog drift OR Heuristic A enrichment-vs-new-agent challenge OR T012 not complete by Day 1 12:00 local — user tie-break gate), MEDIUM (architect edit ownership on plan-day decisions T003/T004/T005/T032), HIGH-1 (buffer-day budget model — T059 R7+R8 code-review consumed at Wave 4 PM, NOT buffer; T061 retrospective slotting Day 1 PM if ≥1h residual, otherwise Buffer Day 1), HIGH-2 (PR title contract / Release Discipline — T058 pre-merge + T063 post-merge release-please verification with F-212 recovery pattern), R3 (multi-feature concurrency hedge — Buffer Day 2 reserved if F-4 / F-5 enter build concurrently).

---

## 1. Agent Assignment Matrix

All 67 tasks mapped to exact `subagent_type` values. Parallel Group column indicates which tasks may run concurrently within a wave (PG-N notation scoped to the wave). Assignments honor:
- **T003 / T004 / T005 / T032** → `architect` per plan-day decision ownership (catalog re-verify + Q2 cosmetic-annotation + Q3 example-target + Q3 confirmation are architect-owned)
- **T013** → `architect` if Q2=YES (cosmetic dispatch-rules annotation is documentation-only orchestrator-tier additive edit)
- **T033 / T039 / T040** → `tester` (pytest suite authoring + F-A2 referential-integrity validation + backward-compat byte-identity)
- **T034-T038** → `senior-backend-engineer` (regen pipeline command sequence)
- **T059** → `code-reviewer` (R7+R8 double-check — Pattern Category Disambiguation prose clarity + anti-indicator predicates testable; HIGH-1 buffer-day budget model — consumed at Wave 4 PM, NOT buffer)
- All markdown/YAML authoring, fixture authoring, ADR authoring, grep audits → `senior-backend-engineer`

| Task ID | Phase | Agent (`subagent_type`) | Parallel Group | Notes |
|---------|-------|-------------------------|----------------|-------|
| T001 | Phase 1 Setup | `senior-backend-engineer` | PG-Setup-1 | Working-directory + branch verification; trivial shell + read check |
| T002 | Phase 1 Setup | `senior-backend-engineer` | PG-Setup-1 | Create `tests/scripts/fixtures/tool_abuse_enrichment/` directory |
| **T003** | **Phase 2 Wave 1.0** | **`architect`** | **sequential (blocking)** | **Plan-day re-verification: catalog citations + Heuristic A scope + line count + consumers list; memo to `.aod/results/wave1-architect-reverify.md` (R1 anchor)** |
| **T004** | **Phase 2 Wave 1.0** | **`architect`** | **PG-Wave1.0-A** | **PRD Q2 plan-day decision (cosmetic dispatch-rules annotation YES/NO); memo to `.aod/results/wave1-q2-cosmetic-annotation-decision.md`** |
| **T005** | **Phase 2 Wave 1.0** | **`architect`** | **PG-Wave1.0-A** | **PRD Q3 plan-day decision (example regeneration target); memo to `.aod/results/wave1-q3-example-target-decision.md`** |
| T006 | Phase 2 Wave 1.1 | `senior-backend-engineer` | PG-Wave1.1-A | Valid Cat-9 A2A fixture authoring with `source_attribution` ASI07 primary + CWE-287 related |
| T007 | Phase 2 Wave 1.1 | `senior-backend-engineer` | PG-Wave1.1-A | Valid Cat-10 MCP-to-MCP fixture authoring with `source_attribution` ASI07 primary + CWE-345 related |
| T008 | Phase 2 Wave 1.1 | `senior-backend-engineer` | PG-Wave1.1-A | Negative fixture — Cat-9/10 finding citing absent CWE (CWE-99999) for F-A2 rejection test |
| T009 | Phase 2 Wave 1.1 | `senior-backend-engineer` | PG-Wave1.1-B | ADR-032 skeleton — Status: Proposed; Decisions section placeholder for D1-D7 |
| T010 | Phase 2 Wave 1.1 | `senior-backend-engineer` | sequential after T009 | ADR-032 Decisions D1-D7 populated: D1 Heuristic A enrichment vs new agent + ADR-030 Decision 1 cross-ref; D3 no-schema-bump + ADR-031 Decision 8 asymmetry; D7 Pattern Category Disambiguation — R1 gate anchor |
| T011 | Phase 2 Wave 1.1 | `senior-backend-engineer` | sequential after T010 | ADR-032 Cross-References — ADR-021/023/027/028/030 Decision 1/031 Decision 8 + 24-file zero-edit invariant proof |
| T012 | Phase 2 Wave 1.1 | `senior-backend-engineer` | sequential after T010 | `tool-abuse.md` 3 additive edits: metadata `owasp_references` + `## Purpose` extension + Detection Workflow Step 5 references |
| **T013** | **Phase 2 Wave 1.1** | **`architect`** | **PG-Wave1.1-C** | **Q2 cosmetic dispatch-rules annotation (CONDITIONAL on T004 result): if YES, single-token edit `tool-abuse (MCP-03)` → `tool-abuse (MCP-03, ASI-07)`; orchestrator-tier additive edit per architect ownership** |
| T014 | Phase 2 Wave 1.1 | `senior-backend-engineer` | PG-Wave1.1-C | Pre-Wave 3 multi-agent topology dry-run grep on 6 baselines; output to `specs/219-.../multi-agent-topology-check.md` |
| T015 | Phase 3 Wave 2 | `senior-backend-engineer` | PG-Wave2-A | Pattern Category 9 (A2A) — scope paragraph + ≥4 indicators (target 5) appended to `detection-patterns.md` |
| T016 | Phase 3 Wave 2 | `senior-backend-engineer` | sequential after T015 | Cat-9 Anti-Indicator section per Q4 default YES; multi-agent topology gate FR-011 codified |
| T017 | Phase 3 Wave 2 | `senior-backend-engineer` | sequential after T016 | Cat-9 Worked Example — clearly-fictional A2A scenario per NFR-equivalent; orchestrator → worker plain-HTTP A2A scenario |
| T018 | Phase 3 Wave 2 | `senior-backend-engineer` | sequential after T017 | Cat-9 Primary/Related Citations + Mitigations — ASI07 primary + CWE-287 related + AML.T0060 (where applicable) + 5-mechanism mitigation list |
| T019 | Phase 4 Wave 2 | `senior-backend-engineer` | PG-Wave2-B | Pattern Category 10 (MCP-to-MCP) — scope paragraph + ≥4 indicators (target 5) appended to `detection-patterns.md` after Cat-9 |
| T020 | Phase 4 Wave 2 | `senior-backend-engineer` | sequential after T019 | Cat-10 Anti-Indicator section per Q4 default YES; multi-MCP topology gate FR-011 codified |
| T021 | Phase 4 Wave 2 | `senior-backend-engineer` | sequential after T020 | Cat-10 Worked Example — clearly-fictional multi-hop MCP relay scenario; agent → MCP-A → MCP-B trust propagation |
| T022 | Phase 4 Wave 2 | `senior-backend-engineer` | sequential after T021 | Cat-10 Primary/Related Citations + Mitigations — ASI07 primary + CWE-345 related + LLM03 (where applicable) + 5-mechanism MCP-trust mitigation list |
| T023 | Phase 4 Wave 2 | `senior-backend-engineer` | sequential after T022 | Pattern Category Disambiguation subsection — Cat 6 (LLM03 supply-chain) vs Cat 10 (runtime trust) non-overlap carve per ADR-032 D7 / FR-2 |
| T024 | Phase 4 Wave 2 | `senior-backend-engineer` | PG-Wave2-C | Primary Sources extension — append `OWASP ASI07:2026` + `MITRE ATLAS AML.T0060`; pre-existing entries byte-identical |
| T025 | Phase 4 Wave 2 EOD | `senior-backend-engineer` | PG-Wave2-EOD | Structural-diff validation on Categories 1-8 + Overview + DFD targets + Triggers (SC-006 BLOCKER) |
| T026 | Phase 4 Wave 2 EOD | `senior-backend-engineer` | PG-Wave2-EOD | MAESTRO grep validation — empty output on tool-abuse.md + detection-patterns.md (SC-016 BLOCKER) |
| T027 | Phase 4 Wave 2 EOD | `senior-backend-engineer` | PG-Wave2-EOD | Line-count validation `wc -l tool-abuse.md` ≤150 (SC-002 BLOCKER) |
| T028 | Phase 4 Wave 2 EOD | `senior-backend-engineer` | PG-Wave2-EOD | Single MANDATORY Read directive preserved — `grep -c '\*\*MANDATORY\*\*: Read' = 1` |
| T029 | Phase 5 Wave 4 | `senior-backend-engineer` | PG-Wave4-ADR | ADR-032 Status: Proposed → Accepted transition; provisional Revision History row |
| T030 | Phase 5 Wave 4 | `senior-backend-engineer` | sequential after T029 | ADR-032 body completeness check (D1-D7, Cross-Refs, Revision History, zero MAESTRO, zero commercial framing); output to `.aod/results/adr-032-completeness-check.md` |
| **T031** | **Post-Merge** | **`senior-backend-engineer`** | **post-merge only (decoupled from T060)** | **ADR-032 Revision History short-SHA fill after squash-merge (ADR-027/028/029/030/031 precedent)** |
| **T032** | **Phase 6 Wave 3** | **`architect`** | **sequential (decision gate)** | **Q3 fallback decision confirmation point — extend `agentic-app` (default) vs maestro-reference vs new fixture; output to `.aod/results/wave3-regen-target-confirmation.md`** |
| T033 | Phase 6 Wave 3 | `tester` | sequential after T032 | Author `tests/scripts/test_tool_abuse_enrichment.py` — structural-diff + line-count + MAESTRO-grep + F-A2 referential-integrity + MANDATORY Read tests; MUST FAIL pre-Wave 1.1, pass post-edits |
| T034 | Phase 6 Wave 3 | `senior-backend-engineer` | sequential after T033 | Run `/tachi.threat-model examples/agentic-app/` with `SOURCE_DATE_EPOCH=1700000000`; expect ≥1 Cat-9/10 `AG-{N}` finding emerged; cohesive Agentic-category rendering |
| T035 | Phase 6 Wave 3 | `senior-backend-engineer` | sequential after T034 | Run `/tachi.risk-score` on regen agentic-app; verify Cat-9/10 process through `category: agentic` code paths (FR-017) |
| T036 | Phase 6 Wave 3 | `senior-backend-engineer` | sequential after T035 | Run `/tachi.compensating-controls` on regen agentic-app; verify Cat-9/10 control-analyzer processing |
| T037 | Phase 6 Wave 3 | `senior-backend-engineer` | sequential after T036 | Run `/tachi.infographic all` on regen agentic-app; regenerate JPEGs + specs |
| T038 | Phase 6 Wave 3 | `senior-backend-engineer` | sequential after T037 | Run `/tachi.security-report` on regen agentic-app; regenerate `security-report.pdf` + `.pdf.baseline` |
| T039 | Phase 6 Wave 3 | `tester` | PG-Wave3-Verify | F-A2 referential-integrity pytest on regenerated findings + fixture validation (T006/T007 pass + T008 negative rejected); SC-015 BLOCKER |
| T040 | Phase 6 Wave 3 | `tester` | PG-Wave3-Verify | Backward-compat byte-identity pytest under `SOURCE_DATE_EPOCH=1700000000` — 5/5 non-multi-agent baselines (SC-010 BLOCKER, R1 anchor) |
| T041 | Phase 6 Wave 3 | `senior-backend-engineer` | PG-Wave3-Verify | Cohesive Agentic-category rendering verification — all 10 `AG-{N}` categories adjacent in `category: agentic` section (SC-019); output to `.aod/results/wave3-cohesive-rendering-check.md` |
| T042 | Phase 6 Wave 3 | `senior-backend-engineer` | PG-Wave3-Verify | Git-stage regenerated artifacts for commit (architecture if extended, threats.md, SARIFs, risk-scores, controls, threat-report, infographics, security-report.pdf) |
| T043 | Phase 7 Wave 4 | `senior-backend-engineer` | PG-Wave4-SC | SC-001 + SC-004 — `tool-abuse.md` `owasp_references` includes `ASI-07`; Workflow Step 5 references extended; pre-existing byte-identical |
| T044 | Phase 7 Wave 4 | `senior-backend-engineer` | PG-Wave4-SC | SC-002 + SC-016 — line count ≤150; MAESTRO grep empty (delegates to T027 + T026) |
| T045 | Phase 7 Wave 4 | `senior-backend-engineer` | PG-Wave4-SC | SC-003 — `## Purpose` 1-3 line extension; pre-existing prose byte-identical |
| T046 | Phase 7 Wave 4 | `senior-backend-engineer` | PG-Wave4-SC | SC-005 — Cat-9 + Cat-10 each with ≥4 indicators + ≥1 worked example + named mitigations + anti-indicator |
| T047 | Phase 7 Wave 4 | `senior-backend-engineer` | PG-Wave4-SC | SC-006 — Categories 1-8 + Overview + DFD targets + Triggers byte-identical (delegates to T025) |
| T048 | Phase 7 Wave 4 | `senior-backend-engineer` | PG-Wave4-SC | SC-007 — `## Primary Sources` extended with ASI07 + AML.T0060; existing entries byte-identical (delegates to T024) |
| T049 | Phase 7 Wave 4 | `senior-backend-engineer` | PG-Wave4-SC | SC-008 — ADR-032 Accepted with all 6-7 decisions + cross-refs + Revision History (delegates to T030) |
| T050 | Phase 7 Wave 4 | `senior-backend-engineer` | PG-Wave4-SC | SC-009 + SC-011 — regen agentic-app emits ≥1 Cat-9/10 `AG-{N}` finding with grounded mitigations + ASI07 citation (delegates to T034) |
| T051 | Phase 7 Wave 4 | `tester` | PG-Wave4-SC | SC-010 — backward-compat byte-identity 5/5 non-multi-agent baselines (delegates to T040) |
| T052 | Phase 7 Wave 4 | `senior-backend-engineer` | PG-Wave4-SC | SC-012 — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json` |
| T053 | Phase 7 Wave 4 | `senior-backend-engineer` | sequential gate | SC-013 — 24-file zero-edit grep audit; orchestrator + finding-format-shared + 5 infrastructure-tier consumers all zero-diff |
| T054 | Phase 7 Wave 4 | `senior-backend-engineer` | PG-Wave4-SC | SC-014 — `schemas/finding.yaml` `git diff main` empty (no schema bump; first BLP-01 detection feature with no schema bump) |
| T055 | Phase 7 Wave 4 | `tester` | PG-Wave4-SC | SC-015 — F-A2 validation on regen findings + fixture-driven (delegates to T039) |
| T056 | Phase 7 Wave 4 | `senior-backend-engineer` | PG-Wave4-SC | SC-017 — `orchestrator.md` zero diff; `dispatch-rules.md` zero functional diff (cosmetic Q2 single-token if applied) |
| T057 | Phase 7 Wave 4 | `senior-backend-engineer` | PG-Wave4-SC | SC-019 — cohesive Agentic-category rendering (delegates to T041) |
| T058 | Phase 7 Wave 4 | `senior-backend-engineer` | PG-Wave4-SC | SC-020 — PR #220 title `feat(219):` Conventional Commits format; `gh pr view 220 --json title -q .title` re-verification |
| **T059** | **Phase 7 Wave 4** | **`code-reviewer`** | **sequential after PG-Wave4-SC** | **R7 + R8 code-review double-check (HIGH-1 buffer-day budget — consumed at Wave 4 PM, NOT buffer): (a) Pattern Category Disambiguation Cat 6 vs Cat 10 boundary clarity per R7; (b) anti-indicator subsection testable-predicate framing per R8; (c) worked-example clearly-fictional framing; output to `.aod/results/wave4-r7-r8-review.md`** |
| T060 | Phase 7 Wave 4 | `senior-backend-engineer` | sequential tail | Mark PR #220 ready via `gh pr ready 220`; PR body links to PRD/spec/plan/tasks/ADR-032; triple-review request |
| T061 | Phase 8 Wave 4 | `senior-backend-engineer` | PG-Wave4-Retro | Delivery retrospective per HIGH-1: Day 1 PM if ≥1h residual, else Buffer Day 1 (Wednesday 2026-04-29). Captures first-execution Heuristic A enrichment-branch lessons + 5/5-dimension reduction vs F-2 + byte-identity preservation evidence |
| T062 | Phase 8 Wave 4 | `senior-backend-engineer` | post-merge | SC-018 BLP-01 Coverage Matrix — ASI07:2026 Planned → Covered with F-3 named; OWASP Agentic Top 10:2026 advances 5/10 → 6/10 |
| T063 | Phase 8 Wave 4 | `senior-backend-engineer` | post-merge | Release-please post-merge verification per SC-020 / R6 — `gh pr list --state open --search "release-please"` within ~30s; if empty, push empty `feat(219):` release-marker commit per F-212 recovery pattern |
| T064 | Phase 8 Wave 4 | `senior-backend-engineer` | contingent | R1 buffer-day work — ONLY if T034 surfaces regen friction on `agentic-app`; invoke Q3 fallback to `maestro-reference` or new minimal multi-agent fixture (~0.5d Buffer Day 1 consumption) |
| T065 | Phase 9 Polish | `senior-backend-engineer` | PG-Polish | Update `CLAUDE.md` Recent Changes section with Feature 219 entry (Features 201/206/212 pattern) |
| T066 | Phase 9 Polish | `senior-backend-engineer` | PG-Polish | Quickstart.md Step 17 + Step 18 end-to-end smoke test; output to `.aod/results/quickstart-smoke.md` |
| T067 | Phase 9 Polish | `senior-backend-engineer` | PG-Polish | Verify `examples/README.md` no-update — F-3 extends `agentic-app` (no new entry); update only if Q3 fallback invoked |

**Agent-count summary (67 assigned tasks)**:

| Agent | Task count | Share |
|-------|-----------|-------|
| `senior-backend-engineer` | 56 | 83.6% |
| `architect` | 5 | 7.5% |
| `tester` | 5 | 7.5% |
| `code-reviewer` | 1 | 1.5% |
| (others) | 0 | 0% |

**Note on distribution vs PRD capacity-check ranges**: Raw task count is heavy on `senior-backend-engineer` because most F-3 tasks are markdown/YAML edits (additive content authoring), grep audits, ADR authoring, and regen pipeline command invocations — all well-suited to the backend engineer agent. PRD capacity check frames load as percent-of-day rather than percent-of-tasks; see Section 5 for the day-based load model, which honors the 1-day envelope. F-3 has the smallest edit surface of any BLP-01 detection feature (no new agent / no new skill dir / no schema bump / no consumers list edit / no functional orchestrator edit) — Heuristic A enrichment branch is structurally lighter than F-1/F-2 new-agent workflows.

---

## 2. Parallel Execution Waves

Each wave advances only after its Quality Gate (Section 3) is green. Wave-internal parallel groups (PG-N) may run concurrently; sequential anchors within a wave are called out.

### Wave 1.0 — Architect Plan-Day Re-Verification + Q2/Q3 Decisions (Day 1 AM, 15-30 min)

**Blocking critical path**: Wave 1.1 cannot begin until T003 verification memo is committed and Q2/Q3 decisions recorded.

| Parallel Group | Tasks | Agent |
|---------------|-------|-------|
| (sequential, blocking) | T003 | `architect` |
| PG-Wave1.0-A | T004, T005 | `architect` |

**Gate**: `.aod/results/wave1-architect-reverify.md` committed with explicit catalog citation re-verify (ASI07/CWE-287/CWE-345/AML.T0060/LLM03 all resolve) + Heuristic A scope intact + line count baseline 98 + consumers list `tool-abuse@line 18`. Q2 + Q3 decisions recorded. Setup tasks T001/T002 fold into morning if not pre-completed.

**Blocker if red — R1 escalation**: If catalog drift surfaces OR Heuristic A enrichment-vs-new-agent decision challenged → user tie-break before Wave 1.1.

### Wave 1.1 — ADR-032 Proposed + `tool-abuse.md` Edits + Fixtures (Day 1 AM/PM, 6-parallel)

**Maximum parallelism**: 6 tracks can proceed concurrently once Wave 1.0 completes.

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| PG-Wave1.1-A | T006, T007, T008 | `senior-backend-engineer` | Independent fixture authoring (Cat-9 valid + Cat-10 valid + negative invalid-attribution) |
| PG-Wave1.1-B | T009 → T010 → T011 → T012 | `senior-backend-engineer` | ADR-032 Proposed sequential chain (skeleton → 7 decisions → cross-refs) + `tool-abuse.md` 3 edits sequential after T010 |
| PG-Wave1.1-C | T013, T014 | `architect` (T013 if Q2=YES), `senior-backend-engineer` (T014) | Q2 cosmetic dispatch annotation (CONDITIONAL on T004) + multi-agent topology dry-run |
| (Setup) | T001, T002 | `senior-backend-engineer` | Folds into Wave 1.1 morning if not pre-completed |

**Gate — R1 hard escalation trigger**: If T010 (ADR-032 Proposed with D1-D7) OR T012 (`tool-abuse.md` 3 edits) not complete by Day 1 AM (Tuesday 2026-04-28 12:00 local), surface user tie-break before Day 1 PM. **Do NOT proceed to Wave 2 without ADR-032 Proposed + `tool-abuse.md` edits committed.**

### Wave 2 — Pattern Category 9 + 10 + Disambiguation + Primary Sources Authoring (Day 1 AM/PM, ~0.4d)

**2-parallel author tracks** with sequential micro-chains within each pattern category. US1 (T015-T018) and US2 (T019-T022) run interleaved.

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| PG-Wave2-A | T015 → T016 → T017 → T018 | `senior-backend-engineer` | Pattern Category 9 chain (scope → anti-indicator → worked example → citations + mitigations) |
| PG-Wave2-B | T019 → T020 → T021 → T022 → T023 | `senior-backend-engineer` | Pattern Category 10 chain (scope → anti-indicator → worked example → citations + mitigations) → Disambiguation subsection (sequential after T022) |
| PG-Wave2-C | T024 | `senior-backend-engineer` | Primary Sources extension (parallel with T023) |

### Wave 2 EOD — Byte-Identity + MAESTRO + Line-Count + MANDATORY Read (Day 1 PM, 4-parallel)

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| PG-Wave2-EOD | T025, T026, T027, T028 | `senior-backend-engineer` | 4-parallel verifications on independent file surfaces / different grep/wc commands |

**Gate**: T025 byte-identity green (Categories 1-8 + Overview + DFD targets + Triggers byte-identical) + T026 MAESTRO grep empty + T027 line count ≤150 + T028 MANDATORY Read = 1. ADR-023 Decision 3 additive-only invariant verified.

**Blocker if red**: SC-006 (T025) OR SC-016 (T026) OR SC-002 (T027) violations are BLOCKERS — hard revert to baseline content; do not proceed to Wave 3.

### Wave 3 — Q3 Confirmation + Test Authoring + Pipeline Regen + Verifications (Day 1 PM, ~0.3d)

**Pipeline regen is sequential** (T034→T038 chained on artifact dependency); **verification is 4-parallel** (T039-T042). T032 is architect-owned decision gate; T033 is tester-owned test authoring.

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| (decision gate) | T032 | `architect` | Q3 fallback confirmation point (extend agentic-app vs maestro-reference vs new fixture) |
| (sequential test-first) | T033 | `tester` | Author pytest suite — MUST FAIL pre-edits, pass post-edits |
| (sequential pipeline) | T034 → T035 → T036 → T037 → T038 | `senior-backend-engineer` | Pipeline regen chain (threat-model → risk-score → controls → infographics → security-report) |
| PG-Wave3-Verify | T039, T040, T041, T042 | `tester` (T039 / T040), `senior-backend-engineer` (T041 / T042) | 4-parallel verifications + git-stage |

**Gate**: T040 byte-identity 5/5 pass on non-multi-agent baselines (SC-010 BLOCKER) + T039 F-A2 validation green (fixture + regen, SC-015 BLOCKER) + ≥1 Cat-9 OR Cat-10 `AG-{N}` finding emerged in regen `agentic-app/threats.md` + T041 cohesive Agentic-category rendering green (SC-019).

**Blocker if red — R1 escalation**: Byte-identity break on `web-app` / `microservices` / `ascii-web-api` / `mermaid-agentic-app` / `free-text-microservice` = root-cause before merge; if `agentic-app` cumulative-state cost too high, invoke Q3 fallback to `maestro-reference` or new minimal multi-agent fixture (~0.5d Buffer Day 1 consumption).

### Wave 4 — ADR-032 Accepted + 16-Way SC Sweep + R7/R8 Review + PR Ready (Day 1 PM / Buffer Day 1, ~0.4d)

**Maximum parallelism**: 16 SC checks run concurrently (T043-T058 minus sequential T053). ADR-Accepted transition runs parallel to SC sweep. T059 code-reviewer R7+R8 double-check sequential after SC sweep (HIGH-1 anchor — consumed at Wave 4 PM, NOT buffer).

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| PG-Wave4-ADR | T029 → T030 | `senior-backend-engineer` | ADR-032 Proposed → Accepted transition + body completeness check |
| PG-Wave4-SC | T043-T052, T054-T058 | `senior-backend-engineer` (12), `tester` (T051 / T055) | 14-parallel SC validation sweep on independent surfaces (T053 sequential gate, runs sequentially) |
| (sequential gate) | T053 | `senior-backend-engineer` | 24-file zero-edit grep audit (SC-013) — runs sequentially after PG-Wave4-SC starts |
| (sequential gate) | T059 | `code-reviewer` | R7+R8 double-check (HIGH-1 anchor) after PG-Wave4-SC + T053 green |
| (sequential tail) | T060 | `senior-backend-engineer` | PR ready after T059 green |

**Gate — Pre-Merge**: All 21 spec SCs green (16 in Wave 4 sweep T043-T058 + SC-018 at T062 post-merge + SC-021 at T061 retrospective) + ADR-032 Status: Accepted + T059 R7/R8 compliance green + 24-file zero-edit invariant verified + PR title `feat(219):` Conventional Commits format.

### Wave 4 — Delivery Retrospective + Coverage Matrix Update + Release-Please Verification (Day 1 PM or Buffer Day 1)

HIGH-1 retrospective slotting + post-merge Coverage Matrix update + HIGH-2 release-please verification with F-212 recovery pattern.

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| PG-Wave4-Retro | T061 | `senior-backend-engineer` | Delivery retrospective — Day 1 PM if ≥1h residual, else Buffer Day 1 (HIGH-1) |
| (post-merge) | T062 | `senior-backend-engineer` | SC-018 BLP-01 Coverage Matrix — ASI07:2026 Planned → Covered (private `_internal/` commit) |
| (post-merge, HIGH-2) | T063 | `senior-backend-engineer` | Release-please verification within ~30s; F-212 recovery pattern with empty `feat(219):` marker if needed |
| (contingent, R1) | T064 | `senior-backend-engineer` | Buffer Day 1 R1 absorption OR Q3 fallback (~0.5d) |

### Post-Merge — SHA Fill (decoupled from T060)

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| (post-squash only) | T031 | `senior-backend-engineer` | ADR-032 Revision History short-SHA fill; consistent with ADR-027/028/029/030/031 pattern |

### Polish Lane — Parallel with Wave 4 (Day 1 PM / Buffer Day 1)

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| PG-Polish | T065, T066, T067 | `senior-backend-engineer` | Safe to run pre-merge alongside Wave 4 SC sweep |

---

## 3. Quality Gates Between Waves

Each gate is a binary go/no-go before advancing. Failures escalate to team-lead + architect per the Escalation Paths section. All gate artifacts write to `.aod/results/` or `specs/219-.../`.

### Gate 1.0 → 1.1 — Plan-Day Re-Verification + Q2/Q3 Decisions Committed

**Must be green**:
- [ ] `.aod/results/wave1-architect-reverify.md` exists with explicit catalog citation re-verify (5/5 resolve in `schemas/taxonomy/{owasp,cwe,mitre-atlas}.yaml`) + Heuristic A enrichment-vs-new-agent intact + line count baseline 98 + consumers list `tool-abuse@line 18`
- [ ] `.aod/results/wave1-q2-cosmetic-annotation-decision.md` Q2 YES/NO recorded
- [ ] `.aod/results/wave1-q3-example-target-decision.md` Q3 target recorded (default: extend `agentic-app`)
- [ ] Working directory clean

**Blocker if red**: Wave 1.1 cannot begin; R1 user tie-break escalation required if catalog drift OR Heuristic A challenge surfaces.

### Gate 1.1 → 2 — ADR-032 Proposed + `tool-abuse.md` Edits Committed

**Must be green (R1 hard gate)**:
- [ ] `docs/architecture/02_ADRs/ADR-032-asi07-tool-abuse-enrichment.md` Status: Proposed committed with 6-7 Decisions (D1-D7 including D1 enrichment vs new agent + D3 no-schema-bump cross-ref to ADR-031 D8 asymmetry + D7 Pattern Category Disambiguation) and Cross-References populated — T009/T010/T011
- [ ] `.claude/agents/tachi/tool-abuse.md` 3 additive edits committed (metadata `owasp_references` + `## Purpose` + Workflow Step 5 references) — T012
- [ ] `tests/scripts/fixtures/tool_abuse_enrichment/{valid_category_9_a2a_finding,valid_category_10_mcp_to_mcp_finding,invalid_attribution_finding}.yaml` committed — T006/T007/T008
- [ ] If Q2=YES: `dispatch-rules.md` cosmetic annotation single-token edit — T013
- [ ] `specs/219-.../multi-agent-topology-check.md` committed — T014
- [ ] All Day-1-AM completions (Tuesday 2026-04-28 12:00 local)

**Blocker if red**: R1 user tie-break escalation fires; Day 1 PM work does not begin until resolved.

### Gate 2 → 2 EOD — Pattern Catalog Authoring Complete

**Must be green**:
- [ ] `.claude/skills/tachi-tool-abuse/references/detection-patterns.md` Pattern Category 9 (A2A) authored with scope + ≥4 indicators (target 5) + anti-indicator + worked example + citations + 5-mitigation list — T015-T018
- [ ] Pattern Category 10 (MCP-to-MCP) authored with same elements — T019-T022
- [ ] Pattern Category Disambiguation subsection (Cat 6 vs Cat 10 non-overlap carve) — T023
- [ ] Primary Sources extended with ASI07 + AML.T0060; pre-existing entries byte-identical — T024

### Gate 2 EOD → 3 — Byte-Identity + MAESTRO + Line-Count + MANDATORY Read

**Must be green (BLOCKER cluster)**:
- [ ] T025 structural-diff: Categories 1-8 + Overview + DFD targets + Triggers byte-identical pre/post edit (SC-006 BLOCKER, ADR-023 Decision 3)
- [ ] T026 MAESTRO grep empty on `tool-abuse.md` + `detection-patterns.md` (SC-016 BLOCKER, ADR-023 Decision 2)
- [ ] T027 `wc -l tool-abuse.md` ≤150 (target 100-106; PRD baseline 98) (SC-002 BLOCKER)
- [ ] T028 `grep -c '\*\*MANDATORY\*\*: Read' tool-abuse.md` = 1 (unchanged)

**Blocker if red**: Hard revert to baseline content; ADR-023 Decision 3 violation must be 100% pre-merge.

### Gate 3 → 4 — Pipeline Regen + Verifications

**Must be green (R1 anchor)**:
- [ ] T032 Q3 confirmation: extend `agentic-app` confirmed (default) OR architect + team-lead approved fallback to `maestro-reference` or new minimal multi-agent fixture (~0.5d consumption)
- [ ] T033 pytest suite authored (structural-diff + line-count + MAESTRO grep + F-A2 + MANDATORY Read tests); MUST FAIL pre-edits + pass post-edits
- [ ] `/tachi.threat-model` → `/tachi.risk-score` → `/tachi.compensating-controls` → `/tachi.infographic all` → `/tachi.security-report` all green on `examples/agentic-app/` — T034-T038
- [ ] ≥1 Cat-9 OR Cat-10 `AG-{N}` finding surfaced in regen `agentic-app/threats.md`; existing Cat-1-8 `AG-{N}` + F-1 `OI-{N}` + F-2 `MI-{N}` + `LLM-{N}` preserved — T034
- [ ] `pytest tests/scripts/test_tool_abuse_enrichment.py::test_validate_source_attribution_on_regen` green; T006/T007 fixtures pass + T008 negative fixture rejected (SC-015 BLOCKER) — T039
- [ ] `SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py` 5/5 non-multi-agent baselines byte-identical (SC-010 BLOCKER) — T040
- [ ] Cohesive Agentic-category rendering verified — all 10 `AG-{N}` categories adjacent in `category: agentic` section (SC-019) — T041
- [ ] Regenerated artifacts git-staged — T042

**Blocker if red — R1 escalation**: Byte-identity break = root-cause before merge; if regen friction → Q3 fallback (~0.5d Buffer Day 1).

### Gate 4 → PR-Ready — All SCs + R7/R8 Green

**Must be green**:
- [ ] All 21 spec SCs verified (16 in Wave 4 sweep T043-T058 + SC-018 at T062 + SC-021 at T061)
- [ ] ADR-032 Status: Accepted with provisional merge date + placeholder PR number — T029
- [ ] ADR-032 body completeness confirmed (D1-D7, Cross-Refs, Revision History, zero MAESTRO, zero commercial framing) — T030
- [ ] 24-file zero-edit grep audit returns clean — orchestrator + finding-format-shared + 5 infrastructure-tier consumers all zero-diff (SC-013) — T053
- [ ] `schemas/finding.yaml` `git diff main` empty (no schema bump; SC-014) — T054
- [ ] T059 R7+R8 code-review green — Pattern Category Disambiguation prose clarity + anti-indicator predicates testable + worked-example clearly-fictional framing
- [ ] PR #220 title `feat(219):` Conventional Commits format (SC-020) — T058

**Blocker if red**: Any SC fail or R7/R8 non-compliance = do not mark PR ready; refine per specific SC or re-frame.

### Post-Merge Gate

**Must be green**:
- [ ] PR squash-merged; short-SHA recorded
- [ ] T031 ADR-032 Revision History updated with squash commit short-SHA — consistent with ADR-027/028/029/030/031 lineage
- [ ] T062 BLP-01 Coverage Matrix updated — ASI07:2026 row transitions Planned → Covered with F-3 (Feature 219) named (private `_internal/` commit)
- [ ] T063 release-please PR opened within ~30s — verify via `gh pr list --state open --search "release-please" --limit 3`; if empty, push empty `feat(219):` release-marker commit per F-212 recovery pattern (HIGH-2)

---

## 4. Time Estimates per Wave

**Plan default**: 1-day critical path + 2-day buffer per PRD §Timeline + HIGH-1 buffer-day budget model + R3 multi-feature concurrency hedge.

### Default Timeline (Heuristic A Enrichment Branch First Execution)

| Wave | Day / Time | Duration | Critical Path Tasks | Notes |
|------|-----------|----------|--------------------|------|
| Setup + Wave 1.0 | Day 1 AM (Tuesday 2026-04-28, 09:00-09:30) | 15-30 min | T001-T002, T003, T004, T005 | Plan-day re-verification + Q2/Q3 decisions (architect 15-30 min) |
| Wave 1.1 | Day 1 AM/PM (09:30-12:00) | ~2.5 hours | T006-T012 (+ T013 if Q2=YES, T014) | 6-parallel tracks cut wall-clock; R1 gate by 12:00 local |
| Wave 2 (US1 + US2) | Day 1 AM/PM (12:00-15:30) | **~0.4d (~3.5h)** | T015-T024 | Pattern Category 9 + 10 + Disambiguation + Primary Sources authoring (2-parallel author tracks) |
| Wave 2 EOD | Day 1 PM (15:30-15:45) | ~15 min | T025, T026, T027, T028 | 4-parallel byte-identity + MAESTRO + line-count + MANDATORY Read |
| Wave 3 | Day 1 PM (15:45-18:30) | **~0.3d (~2.75h)** | T032-T042 | Q3 confirmation + test authoring + pipeline regen sequential + 4-parallel verifications |
| Wave 4 (ADR + SC + R7/R8 + PR) | Day 1 PM (18:30-20:00) | **~0.4d (~1.5h)** | T029-T030, T043-T060 | ADR-032 Accepted + 16-way SC sweep + code-reviewer R7/R8 (consumed at Wave 4 PM per HIGH-1, NOT buffer) + PR ready |
| Wave 4 (Retro + Coverage + Release) | Day 1 PM or Buffer Day 1 | **contingent** | T061, T062, T063 | HIGH-1 retro slotting; T062/T063 post-merge |
| **Buffer Day 1** | **Day 2 (Wednesday 2026-04-29)** | **0-1d** | **T061 retro if not Day 1 PM; T064 R1 absorption; absorbed into merge cycle** | **Per HIGH-1 buffer-day budget model + PRD R1** |
| **Buffer Day 2** | **Day 3 (Thursday 2026-04-30)** | **0-1d** | **R3 multi-feature concurrency hedge — F-4 / F-5 sequencing collision absorption** | **Per PRD R3** |
| Post-merge | Post-PR merge | 15 min | T031, T062, T063 | ADR-032 SHA fill + BLP-01 Coverage Matrix update + release-please verification |

**Day 1 landing target**: PR ready by Tuesday 2026-04-28 EOD with all 21 SCs green + R7/R8 compliance verified. Heuristic A enrichment branch first execution narrative captured for F-6/F-7 Tier 2 ML+Mobile bundles.

### Buffer-Day Policy (per HIGH-1 buffer-day budget model + R1 + R3)

- **Buffer Day 1 (Wednesday 2026-04-29)**:
  - If T061 delivery retrospective authored Day 1 PM (≥1h residual) → Buffer Day 1 absorbs R1 regeneration friction OR merge cycle review lag.
  - If R1 materializes (regeneration friction beyond extend-in-place) → Buffer Day 1 consumes Q3 fallback authoring of `examples/maestro-reference/` extension or new minimal multi-agent fixture (~0.5d, T064).
  - If all else green by Day 1 EOD and retrospective not yet authored → Buffer Day 1 is primary T061 retrospective authoring window.
- **Buffer Day 2 (Thursday 2026-04-30)** — per PRD R3 multi-feature concurrency hedge:
  - Reserved for F-3 + F-4 + F-5 sequencing collisions if F-4 (ASI09) or F-5 (LLM10) enters build concurrently. F-3 has smallest edit surface; sequencing F-3 first minimizes rebase friction.
  - If R3 does NOT materialize → Buffer Day 2 capacity redirects to additional polish or remains unused.
- **T059 R7/R8 code-review double-check is NOT buffer-consumed** — HIGH-1 anchors it at Wave 4 PM (Day 1 PM during SC sweep tail).

---

## 5. Capacity Check

PRD capacity check frames load as percent-of-day rather than percent-of-tasks. This section reconciles the 84% raw task-count concentration on `senior-backend-engineer` with the PRD day-based load model, and verifies headroom.

### Load by Agent — Day-Based Model (per PRD envelope, 1-day baseline)

| Agent | Day 1 Load | Buffer Day 1 Load | Buffer Day 2 Load | Notes |
|-------|-----------|-------------------|-------------------|-------|
| `senior-backend-engineer` | **70-80%** | **0-30% (contingent)** | **0% (R3 hedge)** | Wave 1.1 ADR + edits + fixtures + Wave 2 pattern catalog authoring + Wave 3 pipeline regen + Wave 4 SC sweep + ADR Accepted + PR ready dominate Day 1; Buffer Day 1 absorbs retro + R1 fallback if applicable |
| `architect` | **15-30 min total** | **0%** | **0%** | Day 1 AM T003 plan-day re-verify (15-30 min) + T004 Q2 decision (5-10 min) + T005 Q3 decision (5-10 min) + T032 Q3 confirmation (5-10 min) + T013 cosmetic annotation if Q2=YES (~30 sec) |
| `tester` | **20-30%** | **0%** | **0%** | T033 test authoring (~30-45 min) + T039 F-A2 validation (~15 min) + T040 backward-compat byte-identity (~15 min) + T051 / T055 Wave 4 SC checks (~15-30 min combined) |
| `code-reviewer` | **10-20% Day 1 PM** | **0%** | **0%** | Single task T059 R7+R8 double-check (~30-60 min) consumed at Wave 4 PM per HIGH-1 (NOT buffer) |

**Verdict**: **GREEN** — Capacity within PRD 1-day envelope. `senior-backend-engineer` at 70-80% Day 1 / 0-30% Buffer Day 1 headroom preserved per tasks.md team-lead sign-off. F-3 has smaller edit surface than F-2 (no new agent / no new skill dir / no schema bump / no consumers list edit / no functional orchestrator edit), so 1-day envelope is structurally feasible. `architect` thin-slice ownership on decision-critical items (~30-60 min total Day 1); `tester` light-to-moderate load; `code-reviewer` single-shot R7/R8 gate.

### Load by Agent — Raw Task-Count Distribution

| Agent | Assigned Tasks | Est. Hours (1d envelope) | Capacity Window (1d = 8h) | Utilization (task-hour basis) |
|-------|----------------|--------------------------|---------------------------|-------------------------------|
| `senior-backend-engineer` | 56 | ~6-7h | 8h | **75-87%** (within PRD Day-1 70-80% target at midpoint) |
| `tester` | 5 | ~1-1.5h | 8h | **12-19%** (light-moderate load; ample headroom) |
| `architect` | 5 | ~30-60 min | 8h | **6-12%** (thin-slice decision ownership) |
| `code-reviewer` | 1 | ~30-60 min | 8h | **6-12%** (single R7/R8 review) |

**Raw vs day-based reconciliation**: Raw percent (84%) reflects task-count concentration because most F-3 tasks are markdown/YAML operations well-suited to `senior-backend-engineer`. Day-based percent (70-80% Day 1) reflects wall-clock hours against the 1-day envelope, which is the canonical PRD measure. Both are within envelope. F-3 enrichment-branch-first execution is structurally lighter than F-1/F-2 new-agent workflows because there's no new agent to author, no new skill directory to scaffold, no schema bump, no consumers list edit, and no functional orchestrator edit — all of which were present in F-2.

### Mitigation Strategies (if `senior-backend-engineer` saturates)

1. **Batch Wave 3 pipeline regen (T034-T038) as orchestrated command sequence** — wall-clock dominated by tool invocation.
2. **Promote T065 / T066 / T067 polish tasks to earliest-available window** — small, self-contained, parallelizable with Wave 4 SC sweep.
3. **Escalate to team-lead for re-balancing** if R1 materializes AND Q3 fallback invoked (T064 adds ~0.5d — may shift Day 1 tail into Buffer Day 1).

### `tester` Capacity Reserve

With 20-30% Day 1 utilization, `tester` has room to absorb:
- Additional regression fixtures if T039 F-A2 validation flags schema-contract edge cases
- Additional FP sweep on non-multi-agent baselines if T040 byte-identity surfaces drift
- Pytest suite re-runs if any mid-wave commit breaks green

### `architect` Capacity Reserve

With ~30-60 min Day 1 total utilization, `architect` has room to:
- Handle R1 catalog drift OR Heuristic A re-verification if subsume signal surfaces mid-wave
- Handle T032 Q3 fallback decision with full deliberation (~15-30 min) if T034 surfaces regen friction
- Author any supplementary ADR amendment if D1 (enrichment vs new agent) or D3 (no-schema-bump asymmetry) needs clarification

### `code-reviewer` Load

Single task T059 (~30-60 min R7+R8 compliance check) = 10-20% Day 1 PM consumption. Agent can be assigned additional pre-merge PR-phase review tasks post-T060 if needed.

---

## 6. Escalation Paths

Six escalation anchors defined in tasks.md + PRD. All escalations write to `.aod/results/escalation-log.md` with anchor, trigger, and resolution timestamp.

### R1 — Catalog Drift OR Heuristic A Challenge OR Day-1-AM Hard Gate

**Trigger**: T003 plan-day re-verification surfaces catalog drift on any of ASI07/CWE-287/CWE-345/AML.T0060/LLM03 (e.g., upstream rename, ID change, removal), OR Heuristic A enrichment-vs-new-agent decision is challenged, OR T010+T012 not complete by Day 1 AM (Tuesday 2026-04-28 12:00 local).

**Escalation action**: Surface user tie-break notice before Day 1 PM start. Do NOT proceed to Wave 2 without ADR-032 Proposed + `tool-abuse.md` edits committed.

**Escalation participants**:
- `user` — final decision authority if Heuristic A challenged (would force re-adjudication of every prior consolidation: F-1 LLM05 → output-integrity, F-2 LLM09 → misinformation)
- `architect` — brief status report on verification outcome or ambiguity
- `team-lead` — timeline impact (Buffer Day 1 consumed likely)

**Resolution paths**:
1. **Catalog citations clean + Heuristic A enrichment confirmed** (default) → Wave 1.1 proceeds with ADR-032 Proposed + `tool-abuse.md` edits.
2. **Catalog drift detected** → demote affected citation to prose-only (AML.T0060 + LLM03 are optional related citations); re-author with catalog-resolvable IDs only.
3. **Heuristic A challenged with high confidence** → user tie-break per PRD R2 30-minute architect-PM-team-lead alignment session; SDR-001 Decision 4 is locked resolution; ADR-030 D1 + ADR-031 D8 reinforce signal-class taxonomy.
4. **Time slip** → Buffer Day 1 absorbs continuation.

**Escalation artifact**: `.aod/results/r1-catalog-drift-OR-heuristic-a-escalation-YYYY-MM-DD.md`

### R1 — Backward-Compat Byte-Identity Break / Q3 Fallback

**Trigger**: T040 backward-compat byte-identity pytest fails on ANY non-multi-agent baseline (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`), OR `agentic-app` cumulative-state cost exceeds convention-preservation benefit at T032 Q3 confirmation point.

**Escalation action**: PAUSE Wave 3 or PR ready; root-cause OR invoke Q3 fallback.

**Escalation participants**:
- `architect` — assess whether break is shared-reference-edit induced (T024 non-additive Primary Sources extension), pattern-catalog authoring induced (T015-T023 leaked outside Pattern Category 9 + 10 + Disambiguation regions), or Q3-decision-tripped (fallback to `maestro-reference` or new fixture)
- `senior-backend-engineer` — reproduce locally; isolate changed file
- `tester` — confirm break is deterministic vs flaky; verify `SOURCE_DATE_EPOCH=1700000000` is set
- `team-lead` — timeline impact (Buffer Day 1 consumed likely; ~0.5d for Q3 fallback)

**Resolution paths**:
1. **Non-additive shared-reference edit** (ADR-023 Decision 3 violation) → revert T024 or T015-T023 leaked region; re-apply additively.
2. **Topology gate leaked** → review FR-011 multi-agent / multi-MCP topology gate enforcement; ensure Cat-9/10 fires only on multi-agent / multi-MCP topology presence.
3. **Q3 fallback invoked** → architect adjudicates target switch to `maestro-reference` or new minimal multi-agent fixture (~0.5d Buffer Day 1 consumption); update Wave 3 regen target list; update `examples/README.md` entry in T067.

**Escalation artifact**: `.aod/results/r1-byte-identity-break-OR-q3-fallback-YYYY-MM-DD.md`

### Wave 1.1 Line-Count Escalation

**Trigger**: T012 `tool-abuse.md` 3 additive edits push line count >150 (target 100-106; PRD-time baseline 98).

**Escalation action**: PAUSE Wave 2. Trim `## Purpose` extension to 1 line OR move worked-example references to companion catalog if needed. Hard ceiling 180 (ADR-023).

**Escalation participants**:
- `architect` — adjudicate trim path
- `senior-backend-engineer` — apply trim
- `team-lead` — confirm Wave 1.1 gate re-green

**Resolution paths**:
1. **Single-line trim sufficient** → trim `## Purpose` extension; re-run T027; proceed.
2. **Workflow Step 5 references too verbose** → consolidate `ASI-07`, `AML.T0060`, `CWE-287`, `CWE-345` into single-line tail.

**Escalation artifact**: `.aod/results/wave1-1-line-count-escalation-YYYY-MM-DD.md`

### Wave 3 Zero-Category-9/10 Emission Escalation

**Trigger**: T034 `/tachi.threat-model examples/agentic-app/` reveals zero new ASI07-citing findings (no `AG-{N}` Category-9 OR Category-10 finding emerged).

**Escalation action**: PAUSE Wave 3. Architect re-evaluates example target via Q3 fallback (T032 decision point).

**Escalation participants**:
- `architect` — assess `agentic-app` post-Feature-142 architecture sufficiency
- `senior-backend-engineer` — reproduce regen pipeline
- `team-lead` — Buffer Day 1 consumption decision

**Resolution paths**:
1. **`agentic-app` Inter-agent Communication Channel signal sufficient** → re-run T034 after pattern catalog refinement; proceed.
2. **Insufficient signal** → invoke Q3 fallback to `maestro-reference` extension or new minimal multi-agent fixture (~0.5d Buffer Day 1).

**Escalation artifact**: `.aod/results/wave3-zero-emission-escalation-YYYY-MM-DD.md`

### HIGH-1 — R7/R8 Code-Review Double-Check Failure

**Trigger**: T059 code-reviewer flags Pattern Category Disambiguation prose for Cat 6 vs Cat 10 boundary clarity issues per R7, OR anti-indicator subsections for non-testable predicates per R8, OR worked example(s) using non-fictional framing (real institutional / clinician / lawyer / advisor identities).

**Escalation action**: PAUSE PR ready (T060). Refine flagged content.

**Escalation participants**:
- `code-reviewer` — itemize flagged elements with specific violations
- `senior-backend-engineer` — re-frame flagged content
- `team-lead` — confirm re-review cycle ≤1 hour

**Resolution paths**:
1. **Single Disambiguation prose flagged** → refine boundary statement (~10-15 min); re-run T059; proceed.
2. **Anti-indicator predicate non-testable** → reformulate with grep-checkable predicate; re-run T059.
3. **Worked example non-fictional** → re-frame with hypothetical / generic / synthetic qualifiers (~10-15 min).
4. **Multiple flags** → systematic re-framing across pattern catalog (~30-60 min); absorb into Wave 4 PM per HIGH-1 budget.

**Escalation artifact**: `.aod/results/high-1-r7-r8-compliance-YYYY-MM-DD.md`

### HIGH-2 — PR Title + Release-Please Skip Recovery

**Trigger**: T058 reveals PR title not Conventional Commits format, OR T063 reveals no release-please PR opens within ~30s after squash-merge.

**Escalation action**:
- **Pre-merge**: Retitle PR via `gh pr edit 220 --title "feat(219): asi07-tool-abuse-enrichment"` before merge
- **Post-merge**: Push empty `feat(219): asi07 inter-agent communication enrichment — release marker` commit per F-212 incident recovery pattern; verify release-please opens within 30s

**Escalation participants**:
- `senior-backend-engineer` — apply retitle or push release-marker commit
- `team-lead` — confirm release-please PR opens

**Resolution paths**:
1. **Pre-merge title fix** → retitle; merge proceeds.
2. **Post-merge release-please skip** → empty release-marker commit; release-please opens release PR; v4.23.0 (next minor) ships with F-3 named.

**Escalation artifact**: `.aod/results/high-2-pr-title-release-please-YYYY-MM-DD.md`

### F-A2 Validation Failure at T039

**Trigger**: `pytest tests/scripts/test_tool_abuse_enrichment.py` rejects regenerated `AG-{N}` Cat-9/10 findings for referential-integrity failures (e.g., `source_attribution` cites AML.T0060 or LLM03 catalog-absent ID).

**Escalation action**: Pattern worked examples likely cite catalog-absent IDs for `source_attribution` (as opposed to prose-only Primary Sources citation).

**Resolution**: Confirm worked-example `source_attribution` cites only catalog-resolvable IDs (OWASP ASI07, CWE-287, CWE-345). AML.T0060 + LLM03 demote to prose-only Primary Sources entries if catalog drift detected; re-emit findings without absent citation.

**Escalation artifact**: Root-cause in T039 pytest output; resolution commit referencing `.aod/results/fr-a2-resolution.md`.

---

## 7. Handoff to Orchestrator

The orchestrator consumes this `agent-assignments.md` as input to drive execution. Handoff contract:

- **Wave sequencing**: Follow Section 2 strictly; do not advance past a gate in Section 3 without explicit green state.
- **Agent dispatch**: Use exact `subagent_type` values from Section 1 matrix; no improvisation or fallback substitution. **T003 / T004 / T005 / T013 (if Q2=YES) / T032 architect-owned per plan-day decision authority**; **T033 / T039 / T040 tester-owned** (test authoring + F-A2 + backward-compat); **T051 / T055 tester-owned** (Wave 4 SC delegate checks); **T059 code-reviewer-owned** (R7+R8 HIGH-1 anchor).
- **Parallel-group cohesion**: Dispatch all tasks in a parallel group (PG-N) in a single multi-task message when possible.
- **Gate reporting**: After each wave completes, emit a short completion report to team-lead with gate artifacts referenced.
- **Escalation invocation**: If any escalation anchor fires (R1 catalog/Heuristic-A / R1 byte-identity / Wave-1.1 line-count / Wave-3 zero-emission / HIGH-1 R7/R8 / HIGH-2 PR-title / F-A2), PAUSE and surface to team-lead + architect (and user for R1 Heuristic A challenge) before proceeding.

**Team-lead sign-off confirmation**: This `agent-assignments.md` inherits the triple APPROVED status from `tasks.md` (2026-04-25). No separate sign-off gate required for execution start, per the Triad governance matrix (team-lead authority on `agent-assignments.md`).

**Orchestrator entry command**: `/aod.build` (or `/aod.run` for full-lifecycle continuation).

---

**End of Agent Assignments — Feature 219**
