# Agent Assignments: Feature 212 — Improve Executive-Architecture Infographic

**Feature**: 212-improve-executive-architecture-infographic
**Tasks file**: `specs/212-improve-executive-architecture-infographic/tasks.md`
**Total tasks**: 37 (T001–T037) across 6 phases
**Triad status**: tasks.md APPROVED by PM + Architect + Team-Lead (2026-04-24)
**Envelope**: 1 week (PRD)
**Generated**: 2026-04-24 by team-lead

---

## 1. Assignment Strategy

### Recommended Execution Mode

**Primary recommendation**: **3-agent parallel lane strategy** (Agent A, B, C) for Phases 3–5, converging to a single orchestrator for Phase 6. This matches the PRD 1-week envelope and leverages the user-story independence asserted in tasks.md Phase Dependencies.

**Fallback**: **Single-agent serial** if capacity is constrained. Serial run fits a 5–7 day envelope if no rework cycles trigger. The MVP-first path (US1 alone) produces ~70% of value and provides a safe early-ship checkpoint.

### Shared-File Serialization Discipline

Two files are touched by multiple user stories and require strict ordering:

| File | Touched By | Serialization Rule |
|------|------------|--------------------|
| `.claude/skills/tachi-infographics/references/executive-architecture.md` | US1 (T007, T008) and US3 (T027, T028) | **US1 first**. Agent C (US3) must not edit this file until Agent A finishes T007. Enforced by `test_prompt_co_landing` (T022 in US3 red-bar battery). |
| `scripts/extract-infographic-data.py` | US2 (T016, T017) and US3 (T023–T026) | **US2 first**. Agent C (US3) must not edit this file until Agent B finishes T017. US3 extension is strictly additive — new helpers + new dict keys, no rewrites of US2 logic. |

**No other shared files**. `tests/scripts/test_extract_infographic_data.py` is US2-only. `tests/scripts/test_executive_architecture_payload.py` is new and US3-only.

### Agent Selection Rationale

The available `subagent_type` roster (per `.claude/agents/_README.md`) has no `markdown-writer` or `doc-agent`. Markdown-only file edits (prompt files, skill reference files, CHANGELOG) map to `senior-backend-engineer` — this is the registry's general-purpose executor for text/code changes in a Python repo. Test authoring and green-bar verification map to `tester`. Visual-quality review (SC-212-1 4/4 side-by-side) is human-in-the-loop and maps to `product-manager` for final sign-off plus `ux-ui-designer` for structural critique. Runtime baseline measurement is a light-Python execution mapped to `senior-backend-engineer`.

---

## 2. Agent Assignment Matrix

| Task | Agent | Rationale |
|------|-------|-----------|
| T001 | senior-backend-engineer | Filesystem copy + directory creation; no judgement load — executor-style. |
| T002 | senior-backend-engineer | Invoke extractor + Typst render with deterministic env var; script execution. |
| T003 | senior-backend-engineer | Read-only reference capture of the design system file (no authoring). |
| T004 | architect | Producer-contract MEDIUM-2 lock — architect owns the contract verification artifact and must quote exact line numbers + field names. |
| T005 | tester | Verify existing test harness runs and captures the pre-F-212 callout count — core QA engineering. |
| T006 | senior-backend-engineer | Timed runtime measurement on the reference dataset — performance baseline capture. |
| T007 | senior-backend-engineer | Gemini prompt rewrite in the skill reference markdown file (structural authoring; no API/server work, but backend-engineer is the registry's catch-all for text edits in a repo with no `markdown-writer`). |
| T008 | senior-backend-engineer | Verbatim-lock rule documentation in the same skills area. |
| T009 | senior-backend-engineer | Invoke the `tachi-infographic` agent and save regenerated outputs — execution plumbing. |
| T010 | product-manager | Human side-by-side visual review against OpenClaw reference — PM sign-off authority on SC-212-1 subjective criteria. |
| T011 | tester | PDF byte-identity regression gate (`cmp` deterministic compare) — automated test execution. |
| T012 | tester | Fixture authoring for the per-layer floor-rule matrix — QA owns fixture design. |
| T013 | tester | Test authoring (`test_per_layer_floor_invariant`) — TDD red-bar — QA responsibility. |
| T014 | tester | Test authoring (`test_callouts_deterministic`) — QA responsibility. |
| T015 | tester | Test authoring (`test_superset_invariant`) — QA responsibility; LOW-2 programmatic check. |
| T016 | senior-backend-engineer | Python implementation of `_select_critical_high_callouts()` with Largest Remainder Method — core backend algorithm work. |
| T017 | senior-backend-engineer | Python implementation of `layer_overflow` field extension — core backend payload shaping. |
| T018 | tester | Run pytest and confirm green-bar — QA green-bar verification. |
| T019 | senior-backend-engineer | Regenerate reference image and save spec JSON — execution plumbing. |
| T020 | senior-backend-engineer | Re-measure runtime (5 timed runs) — performance gate measurement. |
| T021 | tester | Fixture authoring for the L3 payload schema matrix — QA owns fixture design. |
| T022 | tester | Author new `test_executive_architecture_payload.py` with 12 drift-guard cases — QA TDD red-bar authoring. |
| T023 | senior-backend-engineer | Module-scoped constant reuse / declaration in the Python script — backend refactor. |
| T024 | senior-backend-engineer | Python helper `_build_flow_edges()` implementation — backend algorithm + sort. |
| T025 | senior-backend-engineer | Python helper `_build_clusters()` implementation — backend algorithm + sort. |
| T026 | senior-backend-engineer | Python payload dict extension (`flow_edges`, `clusters` top-level keys) — backend integration. |
| T027 | senior-backend-engineer | Gemini prompt update in the skill reference markdown file — prompt authoring (catch-all for markdown). |
| T028 | senior-backend-engineer | Payload schema documentation in the skill reference markdown file — markdown authoring. |
| T029 | tester | Run pytest for US3 + US2 and confirm green-bar — QA green-bar verification. |
| T030 | ux-ui-designer | Manual review that arrows and dashed boundaries on the regenerated image match `flow_edges[]` and `clusters[]` contents — structural visual critique. |
| T031 | tester | PDF byte-identity regression gate — automated test execution. |
| T032 | senior-backend-engineer | Re-measure runtime — performance gate measurement. |
| T033 | senior-backend-engineer | CHANGELOG.md entry authoring — markdown authoring. |
| T034 | tester | Run quickstart.md end-to-end — QA acceptance execution. |
| T035 | tester | Full pytest suite — regression gate. |
| T036 | product-manager | Final visual sign-off against OpenClaw reference — PM sign-off authority on SC-212-1 / SC-212-2 / SC-212-3. |
| T037 | senior-backend-engineer | Draft PR sync — git operations within the feature branch. |

### Agent Load Summary

| Agent | Tasks | Count |
|-------|-------|-------|
| senior-backend-engineer | T001, T002, T003, T006, T007, T008, T009, T016, T017, T019, T020, T023, T024, T025, T026, T027, T028, T032, T033, T037 | 20 |
| tester | T005, T011, T012, T013, T014, T015, T018, T021, T022, T029, T031, T034, T035 | 13 |
| product-manager | T010, T036 | 2 |
| architect | T004 | 1 |
| ux-ui-designer | T030 | 1 |

**Balance check**: senior-backend-engineer is at ~54% of tasks but each task is small (≤2h per Team-Lead sign-off). No agent is pinned to a critical serial path that blocks another agent. Tester load (13 tasks) is spread across all three user stories and Phase 6 — natural concurrency with backend-engineer edits on disjoint files.

---

## 3. Parallel Execution Waves

### Wave 0 — Setup (Phase 1: T001–T003)

**Purpose**: Capture baselines and read-only reference loading.

| Parallel Group | Task | Agent |
|---|---|---|
| 0A | T001 (copy baseline image) | senior-backend-engineer |
| 0A | T002 (capture baseline PDF) | senior-backend-engineer |
| 0A | T003 (read visual-design-system.md) | senior-backend-engineer |

All three parallelize — different artifacts, no data dependency.

**Wave 0 Gate (PASS conditions)**:
- `specs/212-improve-executive-architecture-infographic/artifacts/baseline-before/` exists and contains `threat-executive-architecture.jpg`.
- `specs/212-improve-executive-architecture-infographic/artifacts/baseline-zero-finding.pdf` exists and is reproducible under `SOURCE_DATE_EPOCH=1700000000`.
- Visual-design-system severity colors (`#DC2626`, `#EA580C`) confirmed in reviewer notes.

**Estimated wall-clock**: 1 hour.

---

### Wave 1 — Foundational Contract Lock (Phase 2: T004–T006)

**Purpose**: Lock the producer-consumer contract and establish runtime baseline. Blocking for all user-story phases.

| Parallel Group | Task | Agent |
|---|---|---|
| 1A | T004 (producer-contract verification) | architect |
| 1A | T005 (test harness + pre-F-212 callout count) | tester |
| 1A | T006 (runtime baseline — 5 timed runs) | senior-backend-engineer |

All three parallelize — different agents, different artifacts.

**Wave 1 Gate (PASS conditions)**:
- `producer-contract-verified.md` exists with exact line numbers quoted from `scripts/tachi_parsers.py` and exact field names (`source`, `destination`, `data`, `protocol`; `zone`, `trust-level`, `components`) — this is the MEDIUM-2 lock.
- `pre-f212-callout-count.txt` captured (enables SC-212-3 delta measurement post-US2).
- `runtime-baseline.txt` contains mean wall-clock of 5 timed runs (enables SC-212-8 +10% regression gate).

**Estimated wall-clock**: 1.5 hours.

**Critical**: No Wave 2 task may begin until T004 artifact is filed. This is the gating handshake.

---

### Wave 2 — Parallel User-Story Kickoff: Tests + Preparation (Phases 3–5, test-first slices)

**Purpose**: TDD red-bar authoring across all three user stories in parallel. Every task in this wave touches a file that no other task in this wave touches.

| Parallel Group | Task | Agent | File Touched |
|---|---|---|---|
| 2A (US1) | T007 (rewrite Gemini prompt) | senior-backend-engineer | `executive-architecture.md` |
| 2A (US1) | T008 (verbatim-lock rule doc) | senior-backend-engineer | `gemini-prompt-construction.md` |
| 2B (US2) | T012 (US2 fixtures) | tester | `tests/scripts/fixtures/exec_arch/{absent,single-layer,two-layer,three-layer,all-layers-qualifying}/threats.md` |
| 2B (US2) | T013 (`test_per_layer_floor_invariant`) | tester | `tests/scripts/test_extract_infographic_data.py` |
| 2B (US2) | T014 (`test_callouts_deterministic`) | tester | `tests/scripts/test_extract_infographic_data.py` |
| 2B (US2) | T015 (`test_superset_invariant`) | tester | `tests/scripts/test_extract_infographic_data.py` |
| 2C (US3) | T021 (US3 fixtures) | tester | `tests/scripts/fixtures/exec_arch/{flow-edges-*,clusters-*}/threats.md` |
| 2C (US3) | T022 (new drift-guard test file — 12 cases) | tester | `tests/scripts/test_executive_architecture_payload.py` (new) |

**Intra-wave note**: T013, T014, T015 all touch the same test file (`test_extract_infographic_data.py`). A single tester agent authors them serially in one sitting — no concurrency needed (they are fast function-level additions and tasks.md flags them `[P]` only because they are independent within US2 scope). Treat 2B as sequential within the wave; 2A / 2B / 2C are parallel across agents.

**Wave 2 Gate (PASS conditions)**:
- T007 + T008 committed — US1 prompt file carries the VERBATIM-locked OpenClaw-style directive.
- T012 — all 5 US2 fixture files exist and parse.
- T013–T015 — all three tests exist in `test_extract_infographic_data.py` and **fail** (red-bar baseline; TDD discipline).
- T021 — all US3 fixture files exist and parse.
- T022 — all 12 test cases exist in the new test file and **fail** (red-bar baseline).

**Estimated wall-clock**: 6 hours.

---

### Wave 3 — US1 Validation + US2 Implementation (serialized per shared-file rule)

**Purpose**: Exercise the new US1 prompt and land the US2 callout-selection rewrite. US1 and US2 run concurrently because they touch different files after Wave 2.

| Parallel Group | Task | Agent |
|---|---|---|
| 3A (US1 loop) | T009 (regenerate image via `tachi-infographic` agent, up to 3 iterations) | senior-backend-engineer |
| 3A (US1 loop) | T010 (PM human side-by-side review) | product-manager |
| 3A (US1 loop) | T011 (PDF byte-identity regression) | tester |
| 3B (US2 impl) | T016 (rewrite `_select_critical_high_callouts()`) | senior-backend-engineer |
| 3B (US2 impl) | T017 (add `layer_overflow` field) | senior-backend-engineer |
| 3B (US2 verify) | T018 (pytest green-bar) | tester |
| 3B (US2 verify) | T019 (regenerate reference image, confirm callout count ∈ [6, 7, 8]) | senior-backend-engineer |
| 3B (US2 perf) | T020 (runtime gate post-US2) | senior-backend-engineer |

**Intra-wave ordering**:
- **3A**: T009 → T010 → T011 is strictly sequential within US1 (iterate image, then review, then regression gate). If T010 is <3/4 PASS after 2 iterations of T009, invoke Risk R1 contingency (re-prioritize US3 ahead of US1 — documented in tasks.md).
- **3B**: T016 → T017 → T018 → T019 → T020 is strictly sequential within US2.
- **3A and 3B parallelize** — different agents, different files (US1 on the prompt file, US2 on the script + test file).

**Wave 3 Gate (PASS conditions)**:
- US1: T010 records ≥3/4 PASS on SC-212-1; T011 returns zero diff on zero-finding PDF (SC-212-7 preserved).
- US2: pytest shows all US2 tests green; regenerated image shows callout count ∈ [6, 7, 8] (SC-212-3 met); `runtime-post-us2.txt` within +10% of baseline (SC-212-8 preserved).
- Shared-file discipline: confirmed Agent A (US1) edits landed first on the prompt file before Wave 4 begins.

**Estimated wall-clock**: 10 hours (US1 loop up to 3 iterations is the long pole; US2 path is ~6 hours).

---

### Wave 4 — US3 Implementation (serialized downstream of US1 prompt + US2 script)

**Purpose**: Extend the payload with `flow_edges[]` and `clusters[]`, co-land the prompt update, and achieve drift-guard green-bar. Must follow Wave 3 because US3 touches two files that Wave 3 edited.

| Parallel Group | Task | Agent |
|---|---|---|
| 4A (US3 backend, serial within) | T023 (`_TRUST_LEVEL_ORDER` reuse/decl) | senior-backend-engineer |
| 4A (US3 backend, parallel) | T024 (`_build_flow_edges()`) | senior-backend-engineer |
| 4A (US3 backend, parallel) | T025 (`_build_clusters()`) | senior-backend-engineer |
| 4A (US3 backend, serial) | T026 (extend payload dict with both keys) | senior-backend-engineer |
| 4B (US3 prompt co-land) | T027 (reference new fields in Gemini prompt) | senior-backend-engineer |
| 4B (US3 prompt co-land) | T028 (document new schema in skill reference) | senior-backend-engineer |
| 4C (US3 verify) | T029 (pytest green-bar US3 + US2) | tester |
| 4C (US3 visual) | T030 (final reference regeneration + structural review) | senior-backend-engineer for regen; ux-ui-designer for review |

**Intra-wave ordering**:
- **4A**: T023 → (T024 ‖ T025) → T026 — constant first; helpers parallel; payload wire-up last.
- **4B**: T027 → T028 sequential on the same skill file.
- **4A and 4B parallelize** — different files.
- **4C**: T029 after 4A + 4B both complete (test_prompt_co_landing asserts both landed); T030 after T029.

**Wave 4 Gate (PASS conditions)**:
- T029: all 12 drift-guard tests green; US2 tests still green (no regression).
- T026 verified: payload carries both `flow_edges` and `clusters` top-level keys, always present, empty `[]` when source absent.
- Field-name lock: `destination` used (not `target`); `trust_level` used (not `trust-level`); `members` used (not `components`) — mechanically enforced by the drift-guard tests.
- Prompt co-landing: `test_prompt_co_landing` in T022 passes.

**Estimated wall-clock**: 8 hours.

---

### Wave 5 — Regression Gates + Final Integration (Phase 5 tail)

**Purpose**: Final regression gates after all three user stories have landed.

| Parallel Group | Task | Agent |
|---|---|---|
| 5A | T031 (PDF byte-identity, post-US3) | tester |
| 5A | T032 (runtime re-measurement, post-US3) | senior-backend-engineer |

Both parallelize — independent artifacts.

**Wave 5 Gate (PASS conditions)**:
- T031: `cmp` returns zero diff on zero-finding PDF (SC-212-7 preserved after all three stories).
- T032: `runtime-post-us3.txt` within +10% of Phase-2 baseline (SC-212-8 preserved after all three stories).

**Estimated wall-clock**: 1 hour.

---

### Wave 6 — Polish + Final Review + PR Sync (Phase 6: T033–T037)

**Purpose**: CHANGELOG, quickstart validation, full regression, final PM sign-off, draft PR sync.

| Parallel Group | Task | Agent |
|---|---|---|
| 6A | T033 (CHANGELOG entry) | senior-backend-engineer |
| 6A | T034 (quickstart.md end-to-end) | tester |
| 6A | T036 (final visual sign-off with PM) | product-manager |
| 6B | T035 (full pytest suite) | tester |
| 6C | T037 (draft PR #213 sync) | senior-backend-engineer |

**Intra-wave ordering**:
- **6A**: T033, T034, T036 parallel across agents.
- **6B**: T035 after 6A (full pytest regression after all polish edits land).
- **6C**: T037 after T035 (push only after green-bar).

**Wave 6 Gate (PASS conditions)**:
- T033: CHANGELOG entry present with L1 + L2 + L3 summary.
- T034: quickstart.md validation-checklist items all PASS.
- T035: `pytest tests/ -v` — zero regressions across full tachi test harness.
- T036: PM sign-off recorded in `final-visual-signoff.md` — SC-212-1 4/4 PASS, SC-212-2 empty-layer waste ≤15%, SC-212-3 callout count 6–8.
- T037: draft PR #213 synced; not marked ready (deferred to `/aod.deliver`).

**Estimated wall-clock**: 3 hours.

---

## 4. Wave Summary & Total Wall-Clock Budget

| Wave | Tasks | Hours | Cumulative | Notes |
|------|-------|-------|------------|-------|
| 0 | T001–T003 | 1 | 1 | Setup |
| 1 | T004–T006 | 1.5 | 2.5 | Producer-contract lock blocking |
| 2 | T007–T008, T012–T015, T021–T022 | 6 | 8.5 | US1 prompt land + red-bar authoring |
| 3 | T009–T011, T016–T020 | 10 | 18.5 | US1 validation loop + US2 impl |
| 4 | T023–T030 | 8 | 26.5 | US3 impl + co-landing |
| 5 | T031–T032 | 1 | 27.5 | Final regression gates |
| 6 | T033–T037 | 3 | 30.5 | Polish + PR sync |

**Total**: ~30.5 wall-clock hours with 3-agent parallelism.

**1-week envelope check**: 30.5 hours ≈ 4 working days at 8 hours/day per lane — fits the 1-week envelope with >1-day slack for the Risk R1 contingency (up to 3 prompt iterations in Wave 3). Serial execution by a single senior-backend-engineer + tester pair would take ~6 days with no slack — feasible but tight.

---

## 5. Execution Notes for Orchestrator

### Invocation Sequence

1. **Wave 0–1 setup handshake**: orchestrator invokes T001–T003 in parallel, then T004–T006 in parallel. Blocks Wave 2 on Wave 1 gate.
2. **Wave 2 kickoff**: orchestrator spawns three parallel lanes (Agent A / B / C) with T007+T008, T012–T015, T021+T022 respectively.
3. **Wave 3 concurrent US1 + US2**: orchestrator runs Agent A on T009–T011 iteration loop; simultaneously runs Agent B on T016–T020. If Agent A needs 3 iterations on T009 (Risk R1 budget), Agent B will likely finish first — acceptable; Wave 3 gate waits for both.
4. **Wave 4 US3**: orchestrator serializes Agent C's US3 work after Wave 3. Within Wave 4, orchestrator can parallelize T024 and T025 (different helper functions, different regions of the Python file) but must commit in a clean rebase.
5. **Wave 5 + 6**: orchestrator runs final gates and polish.

### Shared-File Commit Discipline

When two agents might touch the same file in adjacent waves:

- **Prompt file** (`executive-architecture.md`): Agent A commits T007+T008 → merged/pushed before Agent C begins T027+T028.
- **Python script** (`scripts/extract-infographic-data.py`): Agent B commits T016+T017 → merged/pushed before Agent C begins T023–T026.

The orchestrator enforces this by not dispatching the downstream wave until the upstream wave gate passes.

### Risk R1 Contingency Trigger

If T010 records <3/4 PASS on SC-212-1 after 2 iterations of T009:
- Team-Lead re-prioritizes — US3 lands ahead of US1 (US3 is independent and does not need SC-212-1 to be visual-perfect).
- US1 iteration continues in the background up to iteration budget; if still <3/4 after 3 iterations, Team-Lead escalates to PM for scope decision (accept the image at ≥3/4 with a documented delta, or extend the envelope).

---

## 6. Non-Blocking Observations (FYI)

1. **Tester load is back-loaded to Wave 2 (fixtures + red-bar authoring)** — 6 hours of concentrated TDD work. If the tester agent has capacity for a second concurrent lane, T021 and T022 can split from T012–T015 and complete in half the wall-clock (3 hours). This is already reflected in the Wave 2 budget as parallel lanes 2B / 2C.
2. **senior-backend-engineer on 20 of 37 tasks** — heavy loadout but each task is ≤2h (Team-Lead sign-off on tasks.md confirmed granularity). No single task on the critical path (T007 → T009 → T010) exceeds 4 hours accounting for R1 iteration.
3. **No agent exceeds 80% loaded across any single wave** — Wave 3 is the peak at ~60% senior-backend-engineer on the US2 lane + ~40% on the US1 regen lane.

---

**End of Agent Assignments for Feature 212**
