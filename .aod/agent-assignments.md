---
feature: 224-trust-exploitation-threat-agent
artifact: agent-assignments.md
author: team-lead
date: 2026-04-26
branch: 224-trust-exploitation-threat-agent
source_tasks: .aod/tasks.md
tasks_count: 71
waves_count: 7 (Wave 1.0 → Wave 1.1 → Wave 2 → Wave 3 → Wave 4 → Wave 5 → Wave 6 → Wave 7-buffer)
calendar:
  day_1: 2026-04-27 Monday
  day_2: 2026-04-28 Tuesday
  day_3: 2026-04-29 Wednesday (buffer)
signoff:
  pm: APPROVED (2026-04-26)
  architect: APPROVED (2026-04-26)
  team_lead: APPROVED_WITH_CONCERNS (2026-04-26 — 0 BLOCKING / 1 MEDIUM / 2 LOW; all absorbed inline)
outcome_default: Heuristic A four-way split preserved (2-day baseline + buffer); standalone-execution branch (third Heuristic A standalone after F-1, F-2)
outcome_alternate: Q5 fallback to `examples/agentic-app/` extension if `consumer-agent-app` cumulative-state cost too high (~0.5-1 day buffer consumption per architect MEDIUM-4)
---

# Agent Assignments — Feature 224 `human-trust-exploitation` Threat Agent (OWASP ASI09:2026)

This artifact operationalizes the triple-approved `tasks.md` into agent-by-wave execution units. All assignments reference exact `subagent_type` values from `.claude/agents/_README.md`. The orchestrator consumes this file to dispatch work; the team-lead consumes it to track capacity and escalate gates.

**Source of Truth**: `.aod/tasks.md` (triple APPROVED 2026-04-26; 71 tasks across 11 phases mirroring plan.md's 7-wave structure).

**Escalation anchors**: R1 (Heuristic A subsume signal surfaces at T004 OR T010 not complete by Day 1 EOD — user tie-break gate), R10 (concurrent F-5 build collision — TEAM-LEAD owned at T012 + T026 with architect MEDIUM-A `gh pr diff` post-filter), R11 (Naming Disambiguation prose-synthesis at T041 FR-018 grep test), R12 (release-please skip — T058 + T063 + T066 belt-and-suspenders), R7 (NFR-006 worked-example wording at T062 code-review double-check), R6 (false-positive at T034 / Wave 4 gate before Wave 5 regen), R2 (regeneration surface drift at T043 backward-compat byte-identity), Q5 fallback (T027 architect decision gate at Wave 3 Step 1).

---

## 1. Agent Assignment Matrix

All 71 tasks mapped to exact `subagent_type` values per attribution rules from session input. Assignments honor:
- **T004 / T004a / T004b / T010 / T011 / T022 / T023 / T024 / T026 (R10 trigger) / T027 (Q5 decision) / T028 / T029 / T030 / T032 (grep-checklist) / T062 (NFR-006/7 review)** → `architect` per F-1 HIGH-1 / F-2 MEDIUM-4 / F-4 architect-owned ADR + edit ownership precedent
- **T005 / T007 / T008 / T009 (ADR skeleton fixture authoring) / T041 (FR-018 grep test) / T042 (F-A2 fixture-driven validation)** → `tester`
- **T012 (R10 pre-check) / T026 (R10 enforceable trigger execution)** → `team-lead` per HIGH-1 explicit ownership ("TEAM-LEAD owned per HIGH-1")
- **T021 / T031 / T054 (structural-diff / grep-check verification)** → `code-reviewer`
- **T065 (delivery retrospective)** → `team-lead` per retrospective-authorship convention
- **T063 (PR ready triple-review)** → `product-manager` (PR-phase triple-review participation per Wave 6 PM stand-by)
- All markdown/YAML authoring, README, mitigation specificity, regen pipeline steps, SC sweep, NFR review surfaces → `senior-backend-engineer`

**Note on shared T026 ownership**: T026 is the R10 enforceable trigger execution (team-lead owned per HIGH-1) AND the Wave 3 Step 0 architect-edit precondition. Listed under team-lead in the matrix below; architect picks up Wave 3 Step 2 edits at T028/T029/T030.

| Task ID | Phase | Agent (`subagent_type`) | Parallel Group | Notes |
|---------|-------|-------------------------|----------------|-------|
| T001 | Phase 1 Setup | `senior-backend-engineer` | PG-Setup | Working-directory + branch verification on `224-trust-exploitation-threat-agent` |
| T002 | Phase 1 Setup | `senior-backend-engineer` | PG-Setup | Create `.claude/skills/tachi-human-trust-exploitation/references/` |
| T003 | Phase 1 Setup | `senior-backend-engineer` | PG-Setup | Create `tests/scripts/fixtures/human_trust_exploitation/` |
| **T004** | **Phase 2 Wave 1.0** | **`architect`** | **sequential (blocking)** | **Heuristic A four-way verification (R1 anchor); ADR-030 D2 Outcome B reservation; vocabulary-disjoint test vs. `agent-autonomy`; memo to `.aod/results/heuristic-a-verification.md`** |
| **T004a** | **Phase 2 Wave 1.0** | **`architect`** | **sequential after T004** | **Architect MEDIUM-A residual: final FR-005 trigger keyword count adjudication; decision artifact at `.aod/results/wave-1.0-trigger-keyword-decision.md`** |
| **T004b** | **Phase 2 Wave 1.0** | **`architect`** | **sequential after T004a** | **Final FR-010 `finding-format-shared.md` placement adjudication (R9 mitigation); decision artifact at `.aod/results/wave-1.0-consumers-placement-decision.md`** |
| T005 | Phase 2 Wave 1.1 | `tester` | PG-Wave1.1-A | Regex unit test at `tests/scripts/test_human_trust_exploitation.py` — MUST FAIL before T006 |
| T006 | Phase 2 Wave 1.1 | `senior-backend-engineer` | sequential after T005 | Schema bump 1.7→1.8 + `TE` regex extension + `TE-1` example; atomic commit; verify T005 now passes |
| T007 | Phase 2 Wave 1.1 | `tester` | PG-Wave1.1-B | Valid `TE-1` fixture with `source_attribution` ASI09 primary + CWE-223 related; NFR-006 safe-language patterns |
| T008 | Phase 2 Wave 1.1 | `tester` | PG-Wave1.1-B | Invalid-attribution fixtures: CWE-451 catalog-absent rejection; `agentic_pattern: trust_exploitation` invariant 8 rejection; empty `source_attribution` invariant 3 rejection |
| T009 | Phase 2 Wave 1.1 | `tester` | PG-Wave1.1-C | ADR-033 skeleton at `docs/architecture/02_ADRs/ADR-033-human-trust-exploitation-agent.md` — Status: Proposed; placeholders for D1-D10 |
| **T010** | **Phase 2 Wave 1.1** | **`architect`** | **sequential after T009** | **ADR-033 Decisions D1-D10 populated: D2 four-way carve-up (HIGH-2); D9 Naming Disambiguation (HIGH-1); D10 DFD Target Decision (BLOCKING-1); R1 gate anchor** |
| **T011** | **Phase 2 Wave 1.1** | **`architect`** | **sequential after T010** | **ADR-033 Cross-References — ADR-021/023/026/027/028/029/030/031/032** |
| **T012** | **Phase 2 Wave 1.1** | **`team-lead`** | **PG-Wave1.1-D** | **R10 enforceable trigger pre-check (TEAM-LEAD owned per HIGH-1) with architect MEDIUM-A `gh pr diff` post-filter; output to `.aod/results/wave-3-r10-precheck.md`** |
| T013 | Phase 3 Wave 2 | `senior-backend-engineer` | PG-Wave2-A | `detection-patterns.md` frontmatter + Overview + Detection Scope (trigger keywords + Process-only + Human-User-Facing Emission Indicators 4-category subsection per FR-006) |
| T014 | Phase 3 Wave 2 | `senior-backend-engineer` | sequential after T013 | 5 numbered pattern categories per FR-004 (Undisclosed AI Authorship / Authority-Claim / Persuasive-Tone / Persona-Boundary / Synthetic-Relationship); CWE-287 (cat 4); ATLAS prose-only; NFR-006 four safe-language patterns verbatim |
| T015 | Phase 3 Wave 2 | `senior-backend-engineer` | PG-Wave2-A | `README.md` companion skill — ≤50 lines, mirror `tachi-misinformation` shape |
| T016 | Phase 3 Wave 2 | `senior-backend-engineer` | PG-Wave2-B | `human-trust-exploitation.md` agent skeleton — 5-section canonical shape per ADR-023; `dfd_targets: [Process]`; NO `agentic_pattern` (FR-001) |
| T017 | Phase 3 Wave 2 | `senior-backend-engineer` | sequential after T016 | Complete `## Detection Workflow` steps 1-6; FR-013 two-part emission gate (AI-agent keyword AND human-user-facing emission indicator); NFR-007 self-disclosure discipline |
| T018 | Phase 3 Wave 2 | `senior-backend-engineer` | PG-Wave2-C | Structural validation — line count ≤150, 1 `**MANDATORY**: Read`, zero MAESTRO refs |
| T019 | Phase 4 Wave 2 | `senior-backend-engineer` | sequential after T016 | 2-3 worked `TE-{N}` example findings (chatbot / legal-research / mental-health-companion) with named pattern-specific mitigations; NFR-006 verbatim |
| T020 | Phase 4 Wave 2 | `senior-backend-engineer` | sequential after T014 | Each pattern category worked example mitigation specificity; FR-004(e) sub-class predicate explicit; NFR-006 4-pattern compliance check |
| **T021** | **Phase 4 Wave 2** | **`code-reviewer`** | **PG-Wave2-D** | **NFR-006 + NFR-007 sanity grep on detection-patterns + agent file; output to `.aod/results/wave2-nfr6-nfr7-compliance-check.md`** |
| **T022** | **Phase 5 Wave 6** | **`architect`** | **PG-Wave6-ADR** | **ADR-033 Status: Proposed → Accepted; Revision History row** |
| **T023** | **Phase 5 Wave 6** | **`architect`** | **sequential after T022** | **ADR-033 body completeness (D1-D10, Consequences, Cross-Refs, Revision History); output to `.aod/results/adr-033-completeness-check.md`** |
| **T024** | **Phase 5 Wave 6** | **`architect`** | **sequential after T023** | **Agent `## Purpose` four-signal-class distinctness verification — forward-refs to output-integrity / misinformation / agent-autonomy** |
| T025 | Post-Merge | `senior-backend-engineer` | post-merge only (decoupled from T063) | ADR-033 Revision History short-SHA fill after squash-merge (ADR-027/028/029/030/031/032 precedent) — companion to T067 buffer-day execution |
| **T026** | **Phase 6 Wave 3 Step 0** | **`team-lead`** | **sequential (blocking Wave 3 Step 2)** | **R10 enforceable trigger execution (TEAM-LEAD owned per HIGH-1) at moment Wave 3 Step 2 begins; architect MEDIUM-A `gh pr diff` post-filter; green-light artifact at `.aod/results/wave-3-r10-greenlight.md`** |
| **T027** | **Phase 6 Wave 3 Step 1** | **`architect`** | **sequential after T026** | **Q5 fallback gate execution (architect MEDIUM-4) — consumer-agent-app vs. agentic-app extension; architect MEDIUM-B expected-diff manifest enumeration for both paths; decision artifact at `.aod/results/wave-3-q5-fallback-decision.md`** |
| **T028** | **Phase 6 Wave 3 Step 2** | **`architect`** | **PG-Wave3-Step2** | **Orchestrator.md edits (3 edits per FR-008): dispatch list insert + Agentic Threats row DUO→TRIO + sequential-mode text** |
| **T029** | **Phase 6 Wave 3 Step 2** | **`architect`** | **PG-Wave3-Step2** | **Dispatch-rules.md edits (3 edits per FR-008): Agentic dispatch DUO→TRIO + table row + trigger-keyword rules section with persona anti-indicator; NO External Entity per Q4 BLOCKING-1** |
| **T030** | **Phase 6 Wave 3 Step 2** | **`architect`** | **PG-Wave3-Step2** | **`finding-format-shared.md` `consumers:` list insert per T004b architect adjudication (Agentic-cluster grouping)** |
| **T031** | **Phase 6 Wave 3 Step 2** | **`code-reviewer`** | **sequential after T030** | **Structural-diff validation on finding-format-shared.md — ADR-023 Decision 3 byte-identity on `## ` headings; output to `.aod/results/wave3-structural-diff-check.md`** |
| **T032** | **Phase 6 Wave 3 Step 3** | **`architect`** | **sequential after T028+T029+T030** | **Wave 2.0 6-edit grep-checklist verification (architect MEDIUM-5 / FR-009 / SC-015); 6-row checklist artifact in PR description** |
| T033 | Phase 6 Wave 3 Step 3 | `senior-backend-engineer` | sequential after T032 | Post-bump schema parser round-trip test; pass artifact at `.aod/results/wave3-schema-roundtrip-check.md` |
| T034 | Phase 7 Wave 4 | `senior-backend-engineer` | sequential after T033 | False-positive check on web-app + microservices baselines (FR-017 / R6 mitigation); two-part emission gate verification; output to `.aod/results/wave4-fp-check.md` |
| T035 | Phase 8 Wave 5 | `senior-backend-engineer` | sequential after T034 | Per T027 Q5 decision: author `examples/consumer-agent-app/architecture.md` (lean) OR extend `examples/agentic-app/` (fallback); NFR-006 framing on architecture prose |
| T036 | Phase 8 Wave 5 | `senior-backend-engineer` | sequential after T035 | Run `/tachi.threat-model` with `SOURCE_DATE_EPOCH=1700000000`; ≥1 `TE-{N}` finding; three-prefix-family within agentic (`AG`, `AGP`, `TE` adjacent without prose synthesis) |
| T037 | Phase 8 Wave 5 | `senior-backend-engineer` | sequential after T036 | Run `/tachi.risk-score`; verify `category: agentic` processing on TE findings (FR-014) |
| T038 | Phase 8 Wave 5 | `senior-backend-engineer` | sequential after T037 | Run `/tachi.compensating-controls`; verify TE processing through `category: agentic` code paths |
| T039 | Phase 8 Wave 5 | `senior-backend-engineer` | sequential after T038 | Run `/tachi.infographic all` — regenerate 6 JPEGs + specs |
| T040 | Phase 8 Wave 5 | `senior-backend-engineer` | sequential after T039 | Run `/tachi.security-report` — regenerate `security-report.pdf` + `.pdf.baseline` |
| **T041** | **Phase 8 Wave 5** | **`tester`** | **PG-Wave5-A** | **FR-018 grep-checkable test (R11 mitigation per SC-012) — AGP-vs-TE prose-synthesis-prevention on regenerated `threat-report.md`; output to `.aod/results/fr-018-grep-test.md`** |
| **T042** | **Phase 8 Wave 5** | **`tester`** | **PG-Wave5-A** | **F-A2 referential-integrity validation; CWE-451/ATLAS/regulatory absence checks; Naming Disambiguation invariant 8 test (no `agentic_pattern: trust_exploitation` on TE findings)** |
| T043 | Phase 8 Wave 5 | `senior-backend-engineer` | PG-Wave5-A | Backward-compat byte-identity (SC-006 BLOCKER) — 5/5 baselines under `SOURCE_DATE_EPOCH=1700000000`; R2 anchor |
| T044 | Phase 8 Wave 5 | `senior-backend-engineer` | PG-Wave5-A | Three-prefix-family discipline within agentic verification (SC-014); output to `.aod/results/wave5-three-prefix-family-check.md` |
| T045 | Phase 8 Wave 5 | `senior-backend-engineer` | PG-Wave5-A | Git-stage regenerated artifacts for commit |
| T046 | Phase 9 Wave 6 | `senior-backend-engineer` | PG-Wave6-SC | SC-001 — agent file structural validation (delegates to T018) |
| T047 | Phase 9 Wave 6 | `senior-backend-engineer` | PG-Wave6-SC | SC-002 — pattern catalog ≥5 categories with worked example + anti-indicator (incl. persona on cat 4) + citations + keywords + DFD types + Human-User-Facing Emission Indicators |
| T048 | Phase 9 Wave 6 | `senior-backend-engineer` | PG-Wave6-SC | SC-003 — additive-only finding-format edit (delegates to T031) |
| T049 | Phase 9 Wave 6 | `senior-backend-engineer` | PG-Wave6-SC | SC-004 — regenerated example TE findings surfaced; non-qualifying baselines emit zero (two-part gate) |
| T050 | Phase 9 Wave 6 | `senior-backend-engineer` | PG-Wave6-SC | SC-005 — ADR-033 Accepted with all 10 body items + cross-refs + Revision History (delegates to T023) |
| T051 | Phase 9 Wave 6 | `senior-backend-engineer` | PG-Wave6-SC | SC-006 — byte-identity 5/5 pass on non-consumer-facing baselines (delegates to T043) |
| T052 | Phase 9 Wave 6 | `senior-backend-engineer` | PG-Wave6-SC | SC-007 — regenerated TE findings carry pattern-specific mitigations + ASI09 + `source_attribution` |
| T053 | Phase 9 Wave 6 | `senior-backend-engineer` | PG-Wave6-SC | SC-008 — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json` (NFR-004 zero deps) |
| **T054** | **Phase 9 Wave 6** | **`code-reviewer`** | **PG-Wave6-SC** | **SC-009 — 26-file zero-edit grep audit (22 original + F-1's 2 + F-2's 2; F-3 enrichment reconciled); CRITICAL: `agent-autonomy.md` zero-diff despite ASI09 sub-scope carve-up** |
| T055 | Phase 9 Wave 6 | `senior-backend-engineer` | PG-Wave6-SC | SC-010 — F-A2 validation passes on regenerated findings (delegates to T042) |
| T056 | Phase 9 Wave 6 | `senior-backend-engineer` | PG-Wave6-SC | SC-011 — BLP-01 Coverage Matrix update planned for T064 (Wave 7 buffer day) |
| T057 | Phase 9 Wave 6 | `senior-backend-engineer` | PG-Wave6-SC | SC-012 — FR-018 grep test passes (delegates to T041) |
| T058 | Phase 9 Wave 6 | `senior-backend-engineer` | PG-Wave6-SC | SC-013 — pre-merge PR title `feat(224):` Conventional-Commit verification (R12 mitigation); output to `.aod/results/sc-013-pr-title-check.md` |
| T059 | Phase 9 Wave 6 | `senior-backend-engineer` | PG-Wave6-SC | SC-014 — three-prefix-family discipline within agentic (delegates to T044) |
| T060 | Phase 9 Wave 6 | `senior-backend-engineer` | PG-Wave6-SC | SC-015 — Wave 2.0 grep-checklist artifact in PR description (delegates to T032) |
| T061 | Phase 9 Wave 6 | `senior-backend-engineer` | PG-Wave6-SC | SC-001 verify schema_version `"1.8"` + regex extends to `TE` (delegates to T006); regex unit test passes (delegates to T005) |
| **T062** | **Phase 9 Wave 6** | **`architect`** | **sequential after PG-Wave6-SC** | **R7 NFR-006/007 code-review double-check (consumed at Wave 6 PM, NOT buffer per HIGH-1); pattern-catalog worked-example wording + persuasive language audit; output to `.aod/results/wave6-nfr6-nfr7-compliance-check.md`** |
| **T063** | **Phase 9 Wave 6** | **`product-manager`** | **sequential after T062** | **PR ready / pre-merge verification — PR #225 marked ready (`gh pr ready 225`); triple-review (PM + Architect + Team-Lead) via PR comments + `gh pr merge --squash`** |
| T064 | Phase 10 Wave 7 | `senior-backend-engineer` | PG-Wave7 | SC-011 BLP-01 Coverage Matrix update — ASI09:2026 communication axis Planned → Covered; F-4 named as closure feature for communication axis (autonomy axis stays with `agent-autonomy`) |
| **T065** | **Phase 10 Wave 7** | **`team-lead`** | **PG-Wave7** | **Delivery retrospective (DEFAULT-SLOTTED to buffer per team-lead MEDIUM-3); architect LOW-C absorption (F-5 schema-baseline forward-pointer); F-2/F-3 retrospective template** |
| T066 | Phase 10 Wave 7 | `senior-backend-engineer` | PG-Wave7 | Post-merge release-please verification (R12 mitigation per FR-019 / SC-013); empty `feat(224):` marker commit fallback if release-please skipped per F-212 incident; output to `.aod/results/wave7-release-please-verification.md` |
| T067 | Phase 10 Wave 7 | `senior-backend-engineer` | PG-Wave7 | Post-merge SHA fill on ADR-033 Revision History (T025 companion); ADR-027/028/029/030/031/032 precedent |
| T068 | Phase 10 Wave 7 | `senior-backend-engineer` | contingent | R2/R6/R7 buffer-day absorption ONLY if friction materializes; otherwise capacity redirects to T065 + T064 |
| T069 | Phase 11 Polish | `senior-backend-engineer` | PG-Polish | Update `CLAUDE.md` Recent Changes section with Feature 224 entry (180/189/194/201/206/212/219 pattern); 26-file zero-edit invariant including `agent-autonomy.md` NOT-edit |
| T070 | Phase 11 Polish | `senior-backend-engineer` | PG-Polish | Quickstart.md Step 12 end-to-end smoke test; output to `.aod/results/quickstart-smoke.md` |
| T071 | Phase 11 Polish | `senior-backend-engineer` | PG-Polish | Verify `examples/README.md` entry update if Q5 lean (new entry) or Q5 fallback (note per Features 084/142/145/201/206 convention) |

**Agent-count summary (71 assigned tasks)**:

| Agent | Task count | Share |
|-------|-----------|-------|
| `senior-backend-engineer` | 49 | 69.0% |
| `architect` | 12 | 16.9% |
| `tester` | 5 | 7.0% |
| `code-reviewer` | 3 | 4.2% |
| `team-lead` | 3 | 4.2% |
| `product-manager` | 1 | 1.4% |
| (others) | 0 | 0% |

**Note on distribution vs PRD capacity-check ranges**: Raw task count is heavy on `senior-backend-engineer` because most F-4 tasks are markdown/YAML authoring, regen pipeline commands, and SC sweep — all well-suited to backend engineer agent. PRD capacity check frames load as percent-of-day (Section 3 below) and shows day-based load model is within 80% ceiling at all wave peaks.

**Subagent_type validation**: All 6 assigned `subagent_type` values (`architect`, `senior-backend-engineer`, `tester`, `code-reviewer`, `team-lead`, `product-manager`) are valid per `.claude/agents/_README.md` Agent Roster. Confirmed in team-lead.md §"Agent subagent_types Validation: PASS".

---

## 2. Parallel Execution Waves

Each wave advances only after its Quality Gate (Section 4 — Wave Gate Points) is green. Wave-internal parallel groups (PG-N) may run concurrently; sequential anchors within a wave are called out.

### Wave 1.0 — Architect Heuristic A Verification + Trigger-Keyword Adjudication (Day 1 AM, 30-60 min)

**Blocking critical path**: Wave 1.1 cannot begin until T004 + T004a + T004b verification artifacts are committed.

| Parallel Group | Tasks | Agent |
|---------------|-------|-------|
| (sequential chain) | T004 → T004a → T004b | `architect` |

**Gate**: `.aod/results/heuristic-a-verification.md` + `.aod/results/wave-1.0-trigger-keyword-decision.md` + `.aod/results/wave-1.0-consumers-placement-decision.md` committed. Subsume signal → R1 escalation.

### Wave 1.1 — Schema Lock + ADR-033 Proposed (Day 1 AM/PM, 5-parallel)

**Maximum parallelism**: 5 tracks can proceed concurrently once Wave 1.0 completes.

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| PG-Wave1.1-A | T005 → T006 | `tester` (T005), `senior-backend-engineer` (T006) | Test-first discipline; T006 atomic (schema + regex + example) |
| PG-Wave1.1-B | T007, T008 | `tester` | Independent fixture authoring (valid TE-1 + invalid-attribution triple) |
| PG-Wave1.1-C | T009 → T010 → T011 | `tester` (T009 skeleton), `architect` (T010 Decisions, T011 Cross-Refs) | ADR-033 Proposed sequential chain (skeleton → 10 decisions including D9 + D10 → cross-refs) |
| PG-Wave1.1-D | T012 | `team-lead` | R10 enforceable trigger pre-check (TEAM-LEAD owned per HIGH-1) |
| (Setup) | T001, T002, T003 | `senior-backend-engineer` | Folds into Wave 1.1 morning if not pre-completed |

**Gate — R1 hard escalation trigger**: If T004 Heuristic A verification surfaces subsume signal OR T010 not complete by Day 1 EOD (Monday 2026-04-27 23:59 local), surface user tie-break before Day 2 AM. **Do NOT proceed to Wave 2 without ADR-033 Proposed commit.**

### Wave 2 — Pattern Catalog + Agent Authoring + Mitigation Text (Day 1 PM, 0.5d **stretched 3-4h per team-lead MEDIUM-1**)

**3-parallel core + sequential micro-chains**. US1 (T013-T018) and US2 (T019-T021) run interleaved. T013 + T015 ∥ T016 with T014 sequential after T013.

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| PG-Wave2-A | T013 → T014, T015 | `senior-backend-engineer` | Pattern catalog chain (5 categories + anti-indicators + NFR-006) + companion README |
| PG-Wave2-B | T016 → T017, T019 | `senior-backend-engineer` | Agent-file chain (5-section shape + 6-step workflow + FR-013 two-part gate) + example findings |
| PG-Wave2-C | T018 | `senior-backend-engineer` | Structural validation (≤150 lines, 1 MANDATORY Read, zero MAESTRO) |
| PG-Wave2-D | T020, T021 | `senior-backend-engineer` (T020), `code-reviewer` (T021) | Mitigation specificity + NFR-006/7 sanity grep |

**Gate**: T018 structural check green; T021 NFR-006/7 compliance grep green; T020 5-sub-class predicate explicit. **Wave 1.3 PM EOD checkpoint** (per team-lead LOW-1): Architect reviews Human-User-Facing Emission Indicators subsection (R6 mitigation) + Day-1-EOD pre-positioning checklist for Wave 3 Step 2 edits.

### Wave 3 — R10 Trigger + Q5 Fallback Gate + Orchestrator Registration + 6-Edit Grep-Checklist (Day 2 AM, ~0.3d)

**4-step sequence within wave**: Step 0 R10 (team-lead) → Step 1 Q5 (architect) → Step 2 architect-owned edits 3-parallel → Step 3 grep-checklist + schema round-trip.

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| Wave 3 Step 0 | T026 | `team-lead` | R10 enforceable trigger execution (HIGH-1 ownership); architect MEDIUM-A `gh pr diff` post-filter |
| Wave 3 Step 1 | T027 | `architect` | Q5 fallback gate decision; MEDIUM-B expected-diff manifest enumeration for both paths |
| PG-Wave3-Step2 | T028, T029, T030 | `architect` | 3-parallel architect-owned edits (different files per Wave 1.1 LOW-1 EOD pre-positioning checklist) |
| Wave 3 Step 2 tail | T031 | `code-reviewer` | Sequential after T030; ADR-023 Decision 3 byte-identity enforcement |
| Wave 3 Step 3 | T032 → T033 | `architect` (T032), `senior-backend-engineer` (T033) | 6-edit grep-checklist (architect MEDIUM-5 / FR-009 / SC-015) + schema round-trip |

**Gate**: T032 6-edit grep-checklist green (all ✓); T033 schema round-trip green; T031 structural-diff empty on `## ` heading changes. Quintet-style consistency check per F-1/F-2 precedent.

### Wave 4 — False-Positive Check on Non-Consumer-Facing Baselines (Day 2 AM, ~0.2d)

**Critical sequencing**: Wave 4 MUST complete and pass BEFORE Wave 5 regen runs.

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| (sequential gate) | T034 | `senior-backend-engineer` | False-positive check (FR-017 / R6 mitigation) on web-app + microservices; two-part emission gate verification |

**Gate**: T034 false-positive check green; two-part emission gate verified on non-consumer-facing baselines. **Blocker if red — R6 escalation**: HALT and tighten emission gate (FR-013) before Wave 5 regen.

### Wave 5 — Example Regeneration + FR-018 Grep Test + Three-Prefix-Family Verification (Day 2 PM, ~0.4d)

**Pipeline regen is sequential** (T035→T040 chained on artifact dependency); **verification is 5-parallel** (T041/T042/T043/T044/T045).

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| (sequential pipeline) | T035 → T036 → T037 → T038 → T039 → T040 | `senior-backend-engineer` | Architecture authoring → threat-model → risk-score → controls → infographics → security-report |
| PG-Wave5-A | T041, T042, T043, T044, T045 | `tester` (T041/T042), `senior-backend-engineer` (T043/T044/T045) | 5-parallel verifications + git-stage |

**Gate**: T043 byte-identity 5/5 pass on non-consumer-facing baselines (SC-006 BLOCKER); T042 F-A2 validation green (CWE-451/ATLAS/regulatory absence + invariant 8); ≥1 `TE-{N}` finding in regenerated `threats.md`; T044 three-prefix-family discipline within agentic green; T041 FR-018 grep test green (R11 mitigation per SC-012).

### Wave 6 — Pre-Merge Validation + NFR-006/007 Double-Check + ADR-033 Accepted + PR Ready (Day 2 PM, ~0.3d)

**Maximum parallelism**: 16-parallel SC checks (T046-T061). ADR-Accepted transition runs parallel to SC sweep. T062 architect NFR-006/7 double-check sequential after SC sweep. T062 is R7 consumed at Wave 6 PM per HIGH-1 (not buffer).

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| PG-Wave6-ADR | T022 → T023, T024 | `architect` | ADR-033 Accepted transition + completeness check + agent Purpose four-signal-class verification |
| PG-Wave6-SC | T046-T061 (16-parallel) | `senior-backend-engineer` (15), `code-reviewer` (T054) | 16-parallel SC validation sweep on independent surfaces; T054 26-file invariant audit (CRITICAL `agent-autonomy.md` zero-diff) |
| (sequential gate) | T062 | `architect` | R7 NFR-006/007 compliance double-check (HIGH-1 anchor) after PG-Wave6-SC green |
| (sequential tail) | T063 | `product-manager` | PR ready triple-review (PM + Architect + Team-Lead) via PR comments after T062 green |

**Gate — Pre-PR**: All 15 spec SCs green (14 in Wave 6 sweep T046-T061 + SC-011 BLP-01 Coverage Matrix at T064); ADR-033 Status: Accepted; T062 NFR-006/7 compliance green; T058 PR title `feat(224):` Conventional-Commit verified (R12 mitigation per FR-019).

### Wave 7 — Buffer Day (Wednesday 2026-04-29) — Delivery Retrospective + Coverage Matrix + SHA Fill + F-5 Forward-Pointer

**Buffer-day prioritization (per team-lead LOW-2 4-tier list, tasks.md lines 247-251)**:
1. First call: any in-flight contingency from R2/R6/R7
2. Second call: delivery retrospective (T065)
3. Third call: post-merge SHA fill (T067) + release-please verification (T066)
4. Fourth call: F-5 PRD drafting NOT until F-4 deliver-stage closes (Constraint Analysis on R10)

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| PG-Wave7 | T064 | `senior-backend-engineer` | SC-011 BLP-01 Coverage Matrix update (post-merge documentation commit) |
| PG-Wave7 | T065 | `team-lead` | Delivery retrospective (DEFAULT-SLOTTED per team-lead MEDIUM-3); architect LOW-C F-5 forward-pointer absorption |
| PG-Wave7 | T066 | `senior-backend-engineer` | Post-merge release-please verification (R12 / F-212 incident pattern guard) with empty `feat(224):` marker fallback |
| PG-Wave7 | T067 | `senior-backend-engineer` | Post-merge SHA fill on ADR-033 (T025 companion; ADR-027/028/029/030/031/032 precedent) |
| (contingent) | T068 | `senior-backend-engineer` | R2/R6/R7 absorption ONLY if friction materializes |

### Polish Lane — Parallel with Wave 6 or Wave 7 (Day 2 PM / Day 3)

| Parallel Group | Tasks | Agent | Notes |
|---------------|-------|-------|-------|
| PG-Polish | T069, T070, T071 | `senior-backend-engineer` | Safe to run pre-merge alongside Wave 6 SC sweep |

---

## 3. Capacity Check (verbatim from team-lead.md Section 3 lines 36-43)

PRD capacity check frames load as percent-of-day (Day 1 / Day 2). All agents within 80% ceiling at every wave peak.

| Agent | Day 1 Load | Day 2 Load | Verdict |
|-------|-----------|-----------|---------|
| **architect** | 30-40% (T004 / T004a / T004b verifications + T010 ADR-033 Proposed body authoring + T011 cross-refs) | 40-50% (T026 R10 trigger + T027 Q5 decision + T028/T029/T030 edits + T032 grep-checklist + T022/T023/T024 ADR Accepted + T062 NFR-006/7 review) | PASS — critical-path but well under ceiling; appropriate for ADR-owning agent |
| **senior-backend-engineer** | 60-70% (T013 + T014 pattern catalog + T015 README + T016 + T017 agent file + T018 structural validation + T019 example findings + T020 mitigation specificity) | 50-60% (T035 architecture authoring conditional + T036-T040 regen pipeline + T041 FR-018 grep test + T042 F-A2 + T043 backward-compat + T044 three-prefix-family + T045 git-stage + T046-T061 SC sweep + T062 review surface) | PASS — peak Day-1 PM 65% within ceiling; aligned with PRD MEDIUM-1 stretch |
| **tester** | 40-50% (T005 regex test + T007 valid fixture + T008 invalid fixture + T009 ADR skeleton + T035 architecture authoring start) | 30% (T041 FR-018 grep test extension; otherwise idle/buffer) | PASS — ample headroom for Q5 fallback architecture friction if it materializes |
| **code-reviewer** | 0% Day 1 | 20% Day 2 PM (T021 grep-check verification + T062 NFR-006/7 double-check + structural-diff verification on T031/T054) | PASS — well under ceiling; PRD-promised 20% Day-2-PM hit |
| **team-lead** | 0% Day 1 | 5-10% Day 2 AM (T012 R10 pre-check + T026 R10 enforceable trigger execution; potential T027 Q5 gate observation) | PASS — minimal but critical execution slot |
| **product-manager** | 0% Day 1 | <5% Day 2 (PR triple-review participation only) | PASS — stand-by capacity for PR triple-review per Wave 6 |

**Aggregate verdict**: Workload distribution is **balanced**. No agent exceeds 80% ceiling at any wave. Peak load is `senior-backend-engineer` Day 1 PM at 60-70% (Wave 2 pattern catalog stretched per MEDIUM-1) — within ceiling. Architect and tester floors are appropriate for governance-and-fixture-authoring profiles. Code-reviewer and team-lead are stand-by for narrow-scope critical execution at Wave 6 PM and Wave 3 Step 0 respectively.

### Mitigation Strategies (if `senior-backend-engineer` saturates)

1. **Batch Wave 5 pipeline regen (T036-T040) as orchestrated command sequence** — wall-clock dominated by tool invocation.
2. **Promote T069 / T070 / T071 polish tasks to earliest-available window** — small, self-contained, parallelizable with Wave 6 SC sweep.
3. **Escalate to team-lead for re-balancing** if R2/R6/R7 materializes AND Q5 fallback invoked (T035 fallback adds ~0.5-1 day — may shift Day 2 tail into Wednesday buffer).

---

## 4. Wave Gate Points (verbatim from tasks.md lines 287-295)

Each gate is a binary go/no-go before advancing. Failures escalate per the Escalation Paths section (Section 6). All gate artifacts write to `.aod/results/`.

- **Wave 1.1 Gate**: T010 committed → unblocks Wave 2 (escalation gate fires if not by Day 1 EOD)
- **Wave 2 Gate**: T013-T021 complete → structural checks + NFR-006/007 grep-checks green → unblocks Wave 3
- **Wave 3 Gate**: T026 R10 pass → T027 Q5 decision → T028-T031 edits land → T032 6-edit grep-checklist green + T033 schema round-trip green → unblocks Wave 4
- **Wave 4 Gate**: T034 false-positive check green → unblocks Wave 5
- **Wave 5 Gate**: T035-T045 complete → Q5 expected-diff matches per T027 manifest + byte-identity pass + TE findings surfaced + three-prefix-family verified + FR-018 grep test green → unblocks Wave 6
- **Wave 6 Gate**: T046-T062 all green (15 SC checks + NFR-006/007 compliance + PR title verification) → unblocks T063 PR ready
- **Wave 7 Gate**: T064 (Coverage Matrix) + T065 (retrospective) + T066 (release-please verification) + T067 (SHA fill) → delivery closed

---

## 5. Critical-Path Sequence (verbatim from team-lead.md Section 5 lines 82-96)

```
T004 → T004a/T004b → T006 (schema lock) → T010 (ADR-033 Proposed)
   ↓
T013/T014/T016/T017 (Wave 2 pattern + agent)
   ↓
T026 (R10 trigger) → T027 (Q5 decision) → T028/T029/T030 (edits)
   ↓
T032 (6-edit grep-checklist) → T034 (Wave 4 false-positive)
   ↓
T035 (architecture) → T036 (regen) → T041/T042/T043/T044 (Wave 5 verifications)
   ↓
T046-T061 (SC sweep parallel) → T062 (NFR-006/007 review) → T063 (PR ready)
   ↓
[merge] → T064/T065/T066/T067 (Wave 7 buffer-day work)
```

**Cycles**: NONE detected.
**False parallelism**: NONE detected.
**Hidden cross-wave deps** (5 traced):
- T010 ADR-033 D9 Naming Disambiguation → T041 FR-018 grep test design (TRACED — T010 D9 fully populates the contract that T041 verifies; sequencing correct)
- T010 ADR-033 D10 DFD Target Decision → T029 Edit 6 (NO External Entity declaration) — TRACED (Phase 6 Step 2 sequencing aligned)
- T027 Q5 decision → T035 architecture authoring path → T036 regen target — TRACED via Phase 8 sequencing
- T032 6-edit grep-checklist → T034 false-positive check (Wave 4 cannot start before Wave 3 Step 3 green) — TRACED via Phase 7 dep declaration "Depends on Phase 6"
- T034 Wave 4 false-positive → T036 regen — CRITICAL SEQUENCING CORRECTLY ENFORCED via Phase 8 dep "Depends on Phase 7"

### Parallelization Maxima (verbatim from team-lead.md Section 5 lines 109-115)

| Wave | Parallel Tasks | Verdict |
|------|---------------|---------|
| Wave 1.1 | T005 ∥ T007 ∥ T008 ∥ T009 ∥ T012 (5-parallel) | SOUND — all independent files / different agents (tester, tester, tester, architect, team-lead) |
| Wave 2 | T013 + T015 ∥ T016 (with T014 sequential after T013) | SOUND — T014 depends on T013 frontmatter; T016 depends on data-model |
| Wave 3 Step 2 | T028 ∥ T029 ∥ T030 (3-parallel) | SOUND — all 3 different files; architect-owned with concurrent fork |
| Wave 5 | T041 ∥ T042 ∥ T043 ∥ T044 ∥ T045 (5-parallel) | SOUND — independent verification surfaces |
| Wave 6 | T046-T061 (16-parallel SC checks); T062 sequential after | SOUND — 16 independent verifications on different file surfaces |

**Verdict**: Parallelism is **maximized without false parallelism**. Capacity-aligned (no agent receives multiple tasks simultaneously beyond allocated bandwidth).

---

## 6. Escalation Paths (summary from tasks.md lines 336-343)

Eight escalation anchors defined in tasks.md + PRD. All escalations write to `.aod/results/escalation-log.md` with anchor, trigger, and resolution timestamp.

- **R1 — Wave 1.0 Heuristic A escalation**: T004 surfaces subsume-into-`agent-autonomy` signal OR T010 not complete by Day 1 EOD → user tie-break before Day 2 AM.
- **R10 — Wave 3 Step 0 R10 trigger fire**: T012/T026 detects actual concurrent edit on any of the 4 surface files (post-filter via `gh pr diff`) → HALT and escalate to team-lead; F-4 takes priority; F-5 waits.
- **R6 — Wave 4 false-positive surface (T034)**: 5 non-consumer-facing baselines show keyword + indicator combination matches → halt and tighten emission gate (FR-013) before Wave 5 regen.
- **F-A2 — validation failure (T042)**: validate_source_attribution rejects a TE finding → revise per FR-007 (ASI09 primary + CWE-{223/287/290/345} related only).
- **R11 — prose-synthesis violation (T041)**: FR-018 grep test fails on regenerated `threat-report.md` (AGP-{N} and TE-{N} share bullet/sentence/paragraph) → root-cause renderer or pattern-catalog prose.
- **R12 — release-please skip (T066)**: post-merge release-please PR doesn't open within ~30s → push empty `feat(224):` marker commit on main per `feedback_aod_deliver_release_gate.md`.
- **R2 — regeneration surface drift (T043)**: backward-compat byte-identity breaks on non-consumer-facing baseline → pause PR and root-cause; invoke Q5 fallback to `examples/agentic-app/` extension if `consumer-agent-app` cumulative-state cost too high (~0.5-1 day buffer consumption per architect MEDIUM-4).
- **R7 — NFR-006 compliance violation (T062)**: code-reviewer/architect surfaces a worked example violating any of the 4 safe-language patterns → revise pattern-catalog prose pre-PR-ready (absorbed into buffer-day tier 1 per team-lead MEDIUM-1 concern).

---

## 7. Handoff to Orchestrator

The orchestrator consumes this `agent-assignments.md` as input to drive execution. Handoff contract:

- **Wave sequencing**: Follow Section 2 strictly; do not advance past a gate in Section 4 without explicit green state.
- **Agent dispatch**: Use exact `subagent_type` values from Section 1 matrix; no improvisation or fallback substitution. **T004 / T004a / T004b / T010 / T011 / T022-T024 / T027 / T028-T030 / T032 / T062 architect-owned**; **T012 / T026 / T065 team-lead-owned**; **T005 / T007 / T008 / T009 (skeleton) / T041 / T042 tester-owned**; **T021 / T031 / T054 code-reviewer-owned**; **T063 product-manager-owned**.
- **Parallel-group cohesion**: Dispatch all tasks in a parallel group (PG-N) in a single multi-task message when possible.
- **Gate reporting**: After each wave completes, emit a short completion report to team-lead with gate artifacts referenced.
- **Escalation invocation**: If any escalation anchor fires (R1 / R10 / R6 / F-A2 / R11 / R12 / R2 / R7), PAUSE and surface to team-lead + architect (and user for R1) before proceeding.

**Team-lead sign-off confirmation**: This `agent-assignments.md` inherits the triple APPROVED status from `tasks.md` (2026-04-26). PM APPROVED + Architect APPROVED + Team-Lead APPROVED_WITH_CONCERNS (0 BLOCKING / 1 MEDIUM / 2 LOW — all absorbed inline). No separate sign-off gate required for execution start, per the Triad governance matrix (team-lead authority on `agent-assignments.md`).

**Orchestrator entry command**: `/aod.build` (or `/aod.run` for full-lifecycle continuation).

---

**End of Agent Assignments — Feature 224**
