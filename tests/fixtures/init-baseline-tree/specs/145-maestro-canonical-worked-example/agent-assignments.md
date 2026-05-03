# Agent Assignments: Feature 145 — Canonical MAESTRO Worked Example

**Feature ID**: 145
**Branch**: `145-maestro-canonical-worked-example`
**Tasks source**: `specs/145-maestro-canonical-worked-example/tasks.md` (53 tasks, 8 phases)
**Plan source**: `specs/145-maestro-canonical-worked-example/plan.md`
**Spec source**: `specs/145-maestro-canonical-worked-example/spec.md`
**Triad sign-off status**: PM APPROVED, Architect APPROVED_WITH_CONCERNS, Team-Lead APPROVED_WITH_CONCERNS (see tasks.md frontmatter)

---

## 1. Feature Summary

Feature 145 is a **content-authoring feature** (zero source code) that produces a canonical MAESTRO worked example under `examples/maestro-reference/` — hand-authored `architecture.md` body + pipeline-generated artifacts + adopter-facing `README.md` + deterministic PDF baseline + regression suite integration. Delivery spans **Waves 0-6** with a **4-8 day PRD budget** (pessimistic critical path 4.75-5.25 days).

---

## 2. Agent Assignment Matrix

All 53 tasks T001-T053. Valid `subagent_type` values only — per `.claude/agents/_README.md`.

| Task ID | Task Description (brief) | Assigned Agent | Rationale |
|---------|--------------------------|----------------|-----------|
| T001 | Verify Wave 0 gate resolutions (WG-1/WG-2/WG-3) | orchestrator | Read-only gate confirmation, multi-source check |
| T002 | Create `examples/maestro-reference/` directory | orchestrator | Scaffold setup, no domain judgment needed |
| T003 | Create `examples/maestro-reference/attack-trees/` subdirectory | orchestrator | Scaffold setup, parallel with T002 |
| T004 | Author Mermaid flowchart TD with 18 components across 7 MAESTRO layers | architect | MAESTRO taxonomy expertise, layer mapping judgment |
| T005 | Author Component Summary table (DFD type + MAESTRO layer + AI dispatch) | architect | Continuation of T004; dispatch-rule expertise |
| T006 | Author architecture header comment with FR-016 domain disclaimer | architect | Defense-in-depth phrasing, disclaimer precedent |
| T007 | Keyword-hygiene C1 — rename L5/L4 collision component | architect | maestro-layers-shared.md L5 keyword judgment |
| T008 | Keyword-hygiene C2 — verify Diagnostic Agent L3 keyword | architect | L3 phrase keyword table interpretation |
| T009 | Keyword-hygiene C3 — verify Risk Stratification Model L1 keyword | architect | L1 phrase keyword table interpretation |
| T010 | Verify all 18 components against intended MAESTRO layer | architect | First-match-wins ordering rationale (L5-before-L6) |
| T011 | Verify FR-005 Condition 1: multi-agent gate predicate TRUE | architect | Multi-agent gate predicate spec interpretation |
| T012 | Verify FR-005 Condition 2: R-01 Agent Collusion precondition | architect | R-01 classification rule interpretation |
| T013 | Verify FR-005 Condition 3: R-02 Temporal Attack precondition | architect | R-02 classification rule interpretation |
| T014 | Verify FR-005 Condition 4: R-03 Emergent Behavior precondition | architect | R-03 classification rule interpretation |
| T015 | Run `/tachi.threat-model examples/maestro-reference/` | architect | Pipeline invocation + output-gate judgment |
| T016 | Run `/tachi.risk-score examples/maestro-reference/` | architect | Pipeline invocation, scoring-output inspection |
| T017 | Run `/tachi.compensating-controls examples/maestro-reference/` | architect | Pipeline invocation, controls-output inspection |
| T018 | Run `/tachi.infographic all examples/maestro-reference/` | architect | Pipeline invocation, 6-JPEG output verification |
| T019 | Run `/tachi.security-report examples/maestro-reference/` | architect | Pipeline invocation, PDF assembly verification |
| T020 | Verify FR-007 MAESTRO layer coverage (≥6 of 7) | architect | Threats.md layer-coverage inspection |
| T021 | Verify FR-008(b) cross-layer chain surfacing (≥1 chain ≥3 layers) | architect | Attack-chains.md chain-spanning analysis |
| T022 | Verify FR-008(c) agentic pattern surfacing (≥3 of 6 patterns) | architect | Agentic pattern narrative substantiveness check |
| T023 | Verify FR-008(a) MAESTRO Findings section populated | architect | Per-layer subsection rendering verification |
| T024 | Fallback (a) keyword-tune (conditional Wave 3) | architect | Keyword-table consultation, surgical re-edit |
| T025 | Fallback (b) extend architecture (conditional Wave 3) | architect | Architectural addition judgment (last-but-one) |
| T026 | Fallback (c) relax FR-004 to 6/7 layers (LAST RESORT) | architect | Relaxation approval documentation authority |
| T027 | Re-run Wave 2 pipeline after iteration | architect | Iteration cap enforcement + re-verification |
| T028 | Author README Section 1 Introduction (~100-150 words) | product-manager | Adopter tone, "what/why/takeaways" framing |
| T029 | Author README Section 2 Domain Overview + disclaimer | product-manager | Adopter tone, disclaimer prominence |
| T030 | Author README Section 5 Reading-Order Recommendation | product-manager | Adopter journey mapping (5min/15min/hour) |
| T031 | Author README Section 6 Compliance Cross-References (AIVSS/NIST) | product-manager | Decision-noun phrasing, ADR-024/025 linking |
| T032 | Author README Section 7 Limitations and Scope | product-manager | Scope-boundary tone, non-overclaiming prose |
| T033 | Author README Section 3 MAESTRO Layer Coverage Table | product-manager | Adopter-facing table tone + layer enumeration |
| T034 | Author README Section 4 What to Look For in Output | product-manager | Adopter pointer prose into pipeline outputs |
| T035 | PM tone review against 4 explicit criteria (Risk 145.4) | product-manager | Tone-review authority; 4-criterion checkbox gate |
| T036 | security-analyst disclaimer review against 4 explicit criteria | security-analyst | Content-risk / PII / regulatory-advice gate (FR-017) |
| T037 | Regenerate PDF baseline with `SOURCE_DATE_EPOCH=1700000000` | architect | Deterministic regeneration protocol (ADR-021) |
| T038 | Run second regeneration + `cmp` byte-identity check | architect | Byte-identity diagnostic judgment |
| T039 | If byte-identity fails, defer FR-011 per Risk 145.3 | architect | Deferral-approval authority + follow-up Issue |
| T040 | Add `"maestro-reference"` to BASELINE_EXAMPLES list | architect | Surgical test-file edit (6th entry) |
| T041 | Run `pytest tests/scripts/test_backward_compatibility.py -v` | architect | Regression-suite interpretation + zero-edit verif |
| T042 | Update `examples/README.md` — add Standardized Examples row | product-manager | Adopter-facing table tone (examples/README.md) |
| T043 | Update `examples/README.md` — add first-read callout | product-manager | Adopter-journey directive prose |
| T044 | Verify `examples/README.md` 3-row fixtures table unchanged | product-manager | Surgical-edit scope verification (examples/README.md) |
| T045 | Verify no other `examples/` directories modified (FR-013/FR-014) | architect | Zero-edit invariant verification via git diff |
| T046 | Verify no `.claude/agents/tachi/*.md` modified (Feature 082) | architect | Zero-edit invariant verification via git diff |
| T047 | Verify no schemas/scripts/templates/deps modified | architect | Scope-discipline verification via git diff |
| T048 | Freeze `architecture.md` body (Path B post-Wave-3 checkpoint) | architect | Body-freeze judgment + checkpoint authority |
| T049 | Invoke `/tachi.architecture` in create mode — inject v1.0 frontmatter | architect | Feature 120 frontmatter-injection protocol |
| T050 | Verify Feature 120 v1.0 frontmatter present + valid (SC-012) | architect | Frontmatter-field validation + `.archive/` absence |
| T051 | Run `/aod.analyze` — cross-artifact consistency | orchestrator | Multi-artifact consistency invocation |
| T052 | Verify no `examples/maestro-reference/sample-report/` subdirectory | architect | Structural DoD verification (team-lead L4) |
| T053 | Walk through full DoD checklist (SC-001 through SC-014) | architect | Full DoD checkbox enforcement before /aod.deliver |

**Agent distribution summary**:
- **architect**: 39 tasks (T004-T027 architecture + pipeline + iteration; T037-T041 baseline + regression; T045-T050 invariants + frontmatter; T052-T053 DoD)
- **product-manager**: 10 tasks (T028-T034 README sections; T035 PM tone gate; T042-T044 examples/README.md)
- **security-analyst**: 1 task (T036 disclaimer gate)
- **orchestrator**: 3 tasks (T001-T003 setup; T051 /aod.analyze)

---

## 3. Parallel Execution Waves

Waves are grouped by **task dependencies**, not by phase. Within each wave, `[P]` marks tasks that can run in parallel (different files or non-conflicting file sections).

### Wave A — Setup (Phase 1)

Tasks: **T001, T002, T003**

- T001: Read-only gate verification (no file writes) — can run independently
- T002: Directory creation `examples/maestro-reference/`
- T003 [P]: Subdirectory creation `examples/maestro-reference/attack-trees/` — parallel with T002 (different path)

**Parallelism**: T001 serial (blocking), T002 and T003 parallel after T001 passes.

### Wave B — Architecture Authoring (Phase 3 / Wave 1)

Tasks: **T004-T014**

- T004 (Mermaid body) — **blocking** — must complete first; single-author-atomicity prevents merge risk in single artifact
- T005 (Component Summary table) — sequential after T004 (same file)
- T006 [P] (header comment) — can draft in parallel with T004-T005 (header is prepended; different section)
- T007, T008, T009 — sequential within architect (same file, keyword-hygiene edits to specific components)
- T010 — sequential after T007-T009 (layer-wide verification needs finalized names)
- T011, T012, T013, T014 — static checklist; can run in parallel within architect after T010 (read-only verification, recorded to `research.md`)

**Parallelism**: T006 parallel with T004-T005; T011-T014 parallel after T010.

### Wave C — Pipeline Run + Gates (Phase 4 / Wave 2)

Tasks: **T015-T023**

- T015 (threat-model) — **blocking**, must run first; downstream stages consume its outputs
- T016, T017, T018, T019 — sequential after T015 (pipeline stages read prior outputs; safer serial execution)
- T020, T021, T022, T023 — can run in parallel within architect after T015-T019 (read-only verification of different output files)

**Parallelism**: T020-T023 parallel after T015-T019 complete.

### Wave D — Architecture Iteration (Phase 5 / Wave 3, Conditional)

Tasks: **T024, T025, T026, T027**

- **Skipped entirely** if Wave C gates (T020-T023) pass on first run
- Sequential fallback ranking: T024 (keyword-tune) → T025 (extend) → T026 (relax, LAST RESORT with PM approval)
- T027: re-run Wave C pipeline after any iteration
- **Iteration cap**: 2 rounds — if 2 rounds fail, escalate to Triad for domain-change decision

**Parallelism**: None — strict sequential fallback ordering.

### Wave E — README Authoring (Phase 6 / Wave 4, Parallel with Wave D)

Tasks: **T028-T036**

- **Sections draftable in parallel with Wave D iteration** (team-lead M2/L2 parallelism opportunity):
  - T028 [P] Section 1 Introduction
  - T029 [P] Section 2 Domain Overview + disclaimer
  - T030 [P] Section 5 Reading-Order Recommendation
  - T031 [P] Section 6 Compliance Cross-References
  - T032 [P] Section 7 Limitations and Scope
- **Gated on Wave C output freeze** (requires committed pipeline output):
  - T033 Section 3 MAESTRO Layer Coverage Table
  - T034 Section 4 What to Look For in Output
- **Review gates** (all sections committed first):
  - T035 PM tone review (4 criteria checkbox gate)
  - T036 security-analyst disclaimer review (4 criteria checkbox gate)

**Parallelism**: T028-T032 all parallel during Wave D; T033-T034 parallel after Wave C freeze; T035/T036 sequential (PM first, then security-analyst) OR parallel if both can run concurrently on committed README.

### Wave F — README Review Gates (Subset of Wave E)

Tasks: **T035, T036**

Both review gates operate on committed README content and can run in parallel (independent criteria sets). Both must PASS before proceeding to Wave G. Failure → CHANGES_REQUESTED → author iterates (≤0.5d per Risk 145.4 contingency).

### Wave G — Baseline + Regression + Cross-Reference (Phase 7 / Wave 5)

Tasks: **T037-T047**

- T037 → T038 (byte-identity check) sequential
- T039 conditional branch (skip T040-T041 if deferred)
- T040 → T041 regression integration (sequential)
- **T042, T043, T044 [P]** (examples/README.md updates) — can run in parallel with T037-T041 (different files)
- **T045, T046, T047 [P]** — invariant verification via git diff, can run in parallel after T037-T044 (read-only checks)

**Parallelism**: T042-T044 parallel with T037-T041; T045-T047 parallel after all prior Wave G work complete.

### Wave H — Frontmatter Injection + Final Validation (Phase 8 / Wave 6)

Tasks: **T048-T053**

- T048 (freeze body) → T049 (inject frontmatter) → T050 (verify frontmatter) strictly sequential (two-pass checksum auditability per plan.md Wave 6 commit sequence)
- T051 (/aod.analyze) sequential after T050
- T052 (no mixed structure) can run in parallel with T053 (DoD walkthrough)
- T053 (full DoD walkthrough) — final gate before /aod.deliver

**Parallelism**: T052 and T053 parallel after T051.

---

## 4. Quality Gates Between Waves

Explicit gate conditions at each wave boundary:

| Gate | Condition | Source |
|------|-----------|--------|
| **Wave A → Wave B** | `examples/maestro-reference/` exists at flat path (no `sample-report/` subdirectory); `attack-trees/` subdirectory exists | T001-T003 |
| **Wave B → Wave C** | All 4 FR-005 conditions green (T011-T014 record in `research.md` appendix); all 3 architect keyword-hygiene items C1/C2/C3 handled (T007/T008/T009); `architecture.md` body is frozen-ready (no frontmatter — Path B) | Wave 1 Gate in tasks.md |
| **Wave C → Wave D** (Iteration) | Any of T020-T023 FAIL → enter Wave D iteration; otherwise skip to Wave E | Wave 2 Gate |
| **Wave C → Wave E** (Output-dependent README sections) | All of T020-T023 PASS → T033/T034 can begin (requires committed pipeline output) | Wave 2 Gate |
| **Wave D → Wave C re-run** | After iteration, re-run T015-T019 + T020-T023; if 2 rounds fail, Triad escalation for domain-change or scope-adjustment decision | Wave 3 Gate |
| **Wave E → Wave F** | All 7 README sections committed | Wave 4 Gate preamble |
| **Wave F → Wave G** | T035 PM tone review PASSES all 4 criteria; T036 security-analyst disclaimer review PASSES all 4 criteria; if any criterion fails, CHANGES_REQUESTED → author iterates (≤0.5d per Risk 145.4 contingency) | Wave 4 Gate |
| **Wave G → Wave H** | PDF baseline byte-identical across two consecutive regenerations (T038); 6-baseline pytest regression passes (T041); 5 existing examples + agentic-app + 11 detection agents + schemas/scripts/templates/deps all unmodified (T045/T046/T047); `examples/README.md` carries first-read callout | Wave 5 Gate |
| **Wave H → /aod.deliver** | Feature 120 v1.0 frontmatter valid (T050); `/aod.analyze` passes with no cross-artifact inconsistencies (T051); no mixed structure (T052); all SC-001 through SC-014 DoD checkboxes green (T053) | Wave 6 Gate / Final |

---

## 5. Time Estimates Per Wave

Sourced from plan.md Wave 0-6 timing + tasks.md Implementation Strategy.

| Wave | Duration | Primary Agent | Notes |
|------|----------|---------------|-------|
| **Wave A** (Setup) | ≤0.25d | orchestrator | Directory scaffold only |
| **Wave B** (Architecture Authoring) | 1-1.5d | architect | Mermaid + Component Summary + FR-005 checklist |
| **Wave C** (Pipeline Run + Gates) | ~1d | architect | 5 pipeline invocations + 4 output-gate verifications |
| **Wave D** (Iteration, Conditional) | 0-1.5d | architect | Pessimistic: 2 iteration rounds × 0.75d each; skip entirely if Wave C gates pass first run |
| **Wave E** (README Authoring) | 1.5-2d (parallel with D/G) | product-manager | 7 sections + 2 review gates; single-PM-author serialized estimate |
| **Wave F** (Review Gates, part of Wave E) | 0.5d | product-manager + security-analyst | Two parallel 4-criterion gates; ≤0.5d iteration if CHANGES_REQUESTED |
| **Wave G** (Baseline + Regression) | ~0.5d | architect | PDF regeneration + byte-identity check + 3 invariant diffs + examples/README.md surgical edits |
| **Wave H** (Frontmatter + Final) | ~0.5d | architect + orchestrator (for T051) | Body freeze + frontmatter injection + /aod.analyze + DoD walkthrough |

**Pessimistic critical path total**: 0.25 + 1.5 + 1 + 1.5 + 0.5 + 0.5 = **5.25 days** (Wave D pessimistic, Wave E runs parallel with D+G). Within the 4-8 day PRD budget with ~3 days of residual contingency.

**Optimistic critical path total**: 0.25 + 1 + 1 + 0 + 0.5 + 0.5 = **3.25 days** (Wave D skipped entirely; Wave C gates pass first run).

---

## 6. Agent Capacity Notes

### Critical-Path Loading: architect (~3.5-4.5d contiguous)

The **architect** agent is the single-agent capacity risk on the critical path:

- Wave B (1-1.5d) — architecture authoring
- Wave C (~1d) — pipeline invocation + output-gate verification
- Wave D (0-1.5d conditional) — architecture iteration with fallback ranking
- Wave G (~0.5d) — baseline regeneration + regression fixture + invariant verification
- Wave H (~0.5d) — frontmatter injection + DoD walkthrough

**Contiguous architect loading**: **3.5 days optimistic, 4.5 days pessimistic** on the critical path (Waves B+C+D+G+H).

**Team-lead concern (from tasks.md sign-off)**: "architect capacity on critical path ~3.5-4.5d contiguous — track Wave 0 availability" (Concern 4, APPROVED_WITH_CONCERNS).

### Mitigation 1: Wave E Parallelism

**product-manager** absorbs 1.5-2d of README authoring (T028-T034) **in parallel** with architect's Wave D iteration. This converts serialized 2d of work into a parallel 1.5-2d slot that does NOT extend the critical path.

- T028-T032 (parallel sections) can start as soon as the domain (Healthcare CDSS) is fixed — does NOT require pipeline output
- T033-T034 (output-dependent sections) gate on Wave C pipeline output freeze — extend Wave E beyond Wave C Gate by ≤0.5d serialized

### Mitigation 2: Fallback Cap (Wave D Bounded)

Wave D iteration is **capped at 2 rounds** (T027). If both rounds fail, the feature escalates to **Triad (architect + team-lead + PM)** for domain-change or scope-adjustment decision — NOT an open-ended iteration loop. This bounds architect's downside loading at Wave D to ≤1.5 days.

### Mitigation 3: Dedicated Gate Agent (security-analyst)

**security-analyst** owns T036 (disclaimer review with 4 explicit criteria) — this is a dedicated content-risk gate, not an overload of architect or PM. Wave F review time is parallelizable (T035 PM + T036 security-analyst can run concurrently on committed README).

### Mitigation 4: orchestrator for Setup + /aod.analyze

**orchestrator** owns T001-T003 (setup) and T051 (/aod.analyze invocation). Orchestrator does not contribute to the critical path beyond these narrow, low-effort tasks — prevents architect from spending time on scaffolding or multi-artifact consistency harness invocation.

### Single-Artifact Author-Atomicity

`architecture.md` is a single artifact authored atomically by **architect** within Wave B (T004-T014). Splitting authoring across multiple agents introduces merge risk in a single Mermaid diagram + Component Summary table. The team-lead sign-off explicitly notes: "T004 author-atomicity for Mermaid body is correct (splitting by layer introduces merge risk in single artifact)" (Concern 1).

### Wave E Parallelism Note (single-PM scenario)

If a single product-manager author serializes T028-T034, the Wave E duration is **1.5-2d serialized** — within the 5.25d pessimistic critical path envelope (runs parallel with Wave D + early Wave G). Team-lead Concern 3 documents this: "T028-T032 [P] single-PM-author requires 1.5-2d serialized — noted in Parallel Team Strategy."

---

## 7. Triple Sign-Off Reference

Triple sign-off on `tasks.md` is **complete** per the frontmatter in `specs/145-maestro-canonical-worked-example/tasks.md`:

| Role | Agent | Date | Status |
|------|-------|------|--------|
| PM | product-manager | 2026-04-16 | **APPROVED** |
| Architect | architect | 2026-04-16 | **APPROVED_WITH_CONCERNS** |
| Team-Lead | team-lead | 2026-04-16 | **APPROVED_WITH_CONCERNS** |

**Non-blocking concerns acknowledged in sign-offs**:
- **Architect** (4 minor citation items): T012 `delegation` additive-harmless; T013 R-02 evidence conservatively over-constrained; T014 `feedback loop` additive-harmless; T027 iteration cap enforced by task discipline rather than hard gate. No BLOCKING technical issues.
- **Team-Lead** (5 non-blocking concerns): (1) T033/T034 extending beyond Wave 2 Gate (addressed inline in Wave E above); (2) Wave 3 pessimistic tightened from 1d to 0-1.5d (addressed inline in Wave D above); (3) T028-T032 single-PM-author requires 1.5-2d serialized (addressed in §6 Wave E Parallelism Note); (4) architect capacity on critical path ~3.5-4.5d contiguous (addressed in §6 Critical-Path Loading); (5) T036 dependency on T029 + T006 disclaimers implicit but could be explicit.

**PM review concerns fully resolved**: Concern 1 (T036 4 security-analyst criteria checkboxes), Concern 2 (T035 4 PM tone criteria checkboxes), Concern 3 (T051 PRD-FR-to-spec-FR-to-wave traceability).

**Implementation is authorized** — ready for orchestrator execution via `/aod.build`.

---

**End of Agent Assignments — Feature 145**
