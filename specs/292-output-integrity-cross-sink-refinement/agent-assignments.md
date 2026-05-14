# Agent Assignments: Feature 292 — Output-Integrity Cross-Sink Refinement

**Feature**: 292-output-integrity-cross-sink-refinement
**Tasks Source**: `specs/292-output-integrity-cross-sink-refinement/tasks.md` (34 tasks across 8 phases)
**Generated**: 2026-05-14 by team-lead
**Wave Strategy**: Aligned with PRD weekday-anchored cadence (Day 0 Thu 2026-05-14 → Buffer-2 Thu 2026-05-21)
**Tier-Lead Q5(a) Budget**: 5 hours reserved for contributor-authored PR steerage if path (a) elected

---

## 1. In-Flight Conflict Check

| Potential Collision | Status | Source |
|---|---|---|
| BLP-02 enterprise hardening | CLOSED 2026-05-10 (5/5 delivered, v4.35.0 released) | Project memory `project_blp02_enterprise_hardening.md` |
| BLP-03 signed updates | PROPOSED only; not in-flight; deferred pending enterprise-buyer trigger | Project memory `project_blp03_signed_updates.md` |
| Other open features | None — F-282 closed 2026-05-13; no concurrent docs-only work on `.claude/skills/tachi-output-integrity/` | `git log --since="2026-05-10"` + tasks.md preamble |
| Concurrent file editors | None — `detection-patterns.md`, `output-integrity.md`, ADR-045 slot all uncontested | T001–T004 read-only verifications confirm clean state |

**Verdict**: NO COLLISIONS. Capacity reconciliation clean per team-lead PRD M-2 sign-off.

---

## 2. Agent Assignment Matrix

| Task | Subagent | Rationale (≤15 words) |
|------|----------|----------------------|
| T001 | `senior-backend-engineer` | Read-only directory inspection for ADR-045 slot availability |
| T002 | `senior-backend-engineer` | Read-only schema-state verification at `schemas/finding.yaml` line 18 |
| T003 | `senior-backend-engineer` | Read-only CWE-943 presence check in taxonomy YAML |
| T004 | `senior-backend-engineer` | Read-only architecture-baseline identification for SC-003 fixture |
| T005 | `product-manager` | Community-facing discussion #179 two-choice offer — scope/SLA messaging |
| T006 | `architect` | ADR-045 authoring — architectural decision codification per ADR-027 lineage |
| T007 | `senior-backend-engineer` | Markdown append — Cat 6 pattern surface with citations and indicators |
| T008 | `senior-backend-engineer` | Markdown append — Cat 6 worked example with 4 mitigation alternatives |
| T009 | `senior-backend-engineer` | Markdown append — distinguishing-prose block for Cat 6 vs data-poisoning |
| T010 | `senior-backend-engineer` | Markdown edit — Cat 2 trigger-keyword list extension (additive-only) |
| T011 | `senior-backend-engineer` | Markdown append — Cat 2 sub-example with SANDWORM_MODE + LiteLLM anchors |
| T012 | `senior-backend-engineer` | Markdown edit — both-signal requirement prose strengthening |
| T013 | `senior-backend-engineer` | Markdown append — Cross-Agent Handoff Sinks subsection (depends on T007) |
| T014 | `senior-backend-engineer` | Markdown append — Memory-Promotion Rules YAML schema example |
| T015 | `senior-backend-engineer` | Markdown append — FR-7 one-way navigational invariant lock-paragraph |
| T016 | `senior-backend-engineer` | Markdown insert — ≤10-line cross-link prose into Purpose section |
| T017 | `tester` | Manual cross-link no-emission verification per SC-003 contract |
| T018 | `tester` | 5-non-qualifying-baseline byte-identical regression per SC-004 |
| T019 | `product-manager` | PRE-MERGE PR title Conventional Commits verification (manual gh CLI) |
| T020 | `devops` | POST-MERGE release-please verification + empty-commit marker fallback |
| T021 | `product-manager` | CHANGELOG @armorer-labs attribution edit (path b conditional) |
| T022 | `product-manager` | Discussion #179 delivery comment within 24h of merge |
| T023 | `product-manager` | T+5d courtesy nudge on discussion #179 (conditional, Tue 2026-05-19) |
| T024 | `product-manager` | T+7d SLA breach decision logging (conditional, Thu 2026-05-21) |
| T025 | `senior-backend-engineer` | New baseline architecture description authoring (Mermaid, multi-tenant RAG) |
| T026 | `tester` | Auto-pipeline artifact regeneration + byte-identical reproduction check |
| T027 | `senior-backend-engineer` | Examples README table row insertion for multi-tenant-rag-app |
| T028 | `architect` | ADR-045 Status flip Proposed → Accepted at pre-PR gate |
| T029 | `security-analyst` | `/security` skill re-scan on modified file surface per SC-012 |
| T030 | `tester` | Sequential quickstart.md §1–§17 verification recipe execution |
| T031 | `architect` | POST-MERGE Accepted-commit-SHA placeholder fill per dual-commit governance |
| T032 | `senior-backend-engineer` | BACKLOG.md regeneration via existing shell script |
| T033 | `senior-backend-engineer` | KB entry authoring in INSTITUTIONAL_KNOWLEDGE.md (markdown append) |
| T034 | `orchestrator` | Final `/aod.deliver` invocation coordinating PR-ready → merge → close-out |

---

## 3. Parallel Execution Waves

### Wave 0 — Day 0 Thu 2026-05-14 (Pre-Build)

| Tasks | Activity |
|---|---|
| (governance, complete) | /aod.define ✓ + /aod.plan triple sign-off (this stage) |

**Status**: COMPLETE. PM + Architect + Team-Lead all signed off APPROVED_WITH_CONCERNS at 2026-05-14.

---

### Wave 1 — Day 1 Fri 2026-05-15 (Setup + Foundational + US1/US2 in parallel)

**Parallel stream A: Setup + Foundational** (sequential within stream, T006 blocks downstream)
| Task | Agent | Estimate |
|---|---|---|
| T001 | `senior-backend-engineer` | 5 min |
| T002 | `senior-backend-engineer` | 5 min |
| T003 | `senior-backend-engineer` | 5 min |
| T004 | `senior-backend-engineer` | 5 min |
| T005 | `product-manager` | 30 min (community message drafting + post) |
| T006 | `architect` | 2 hours (ADR-045 ~200 lines per ADR-032 7-decision template) |

**Parallel stream B: US1 implementation** (after T006 merged/staged)
| Task | Agent | Estimate |
|---|---|---|
| T007 | `senior-backend-engineer` | 45 min (~50 lines, citations, indicators) |
| T008 | `senior-backend-engineer` | 30 min (worked example, 4 mitigations) |
| T009 | `senior-backend-engineer` | 15 min (distinguishing prose block) |

**Parallel stream C: US2 implementation** (after T006 merged/staged, in parallel with stream B)
| Task | Agent | Estimate |
|---|---|---|
| T010 | `senior-backend-engineer` | 15 min (keyword list append) |
| T011 | `senior-backend-engineer` | 30 min (~25 lines, sub-example) |
| T012 | `senior-backend-engineer` | 15 min (both-signal prose strengthening) |

**Wave 1 total wall-clock**: ~4 hours (stream A critical path, B+C parallel underneath)

**Pre-Wave 2a Gate**: T006 ADR-045 Proposed merged OR staged on feature branch; T007 (Cat 6 header in place) merged OR staged.

---

### Wave 2a — Day 2 Mon 2026-05-18 AM (US3 implementation + verification)

| Task | Agent | Estimate |
|---|---|---|
| T013 | `senior-backend-engineer` | 30 min (~30 lines, depends on T007 Cat 6 present) |
| T014 | `senior-backend-engineer` | 45 min (~45 lines, Memory-Promotion Rules YAML schema) |
| T015 | `senior-backend-engineer` | 15 min (FR-7 lock-paragraph) |
| T016 | `senior-backend-engineer` | 20 min (≤10-line agent-file cross-link) |
| T017 | `tester` | 45 min (manual tachi.threat-model + jq diff for OI-scoped subset) |

**Wave 2a wall-clock**: ~2.5 hours (T013/T014/T015 sequential within `detection-patterns.md`; T016 parallel on separate file; T017 after all four complete)

---

### Wave 2b — Day 2 Mon 2026-05-18 AM (parallel with 2a)

| Task | Agent | Estimate |
|---|---|---|
| T018 | `tester` | 1 hour (5 non-qualifying baselines × pytest harness run + byte-diff) |

**Wave 2b wall-clock**: ~1 hour. Runs concurrently with Wave 2a stream; independent inputs.

---

### Wave 2c — Day 2 Mon 2026-05-18 PM (Q2=Add baseline)

**Pre-Wave 2c Gate**: T007 Cat 6 in place (baseline architecture references new pattern surface).

| Task | Agent | Estimate |
|---|---|---|
| T025 | `senior-backend-engineer` | 1 hour (Mermaid architecture description authoring) |
| T026 | `tester` | 30 min (tachi.threat-model + artifact generation + reproduction check) |
| T027 | `senior-backend-engineer` | 10 min (examples README table row insertion) |

**Wave 2c wall-clock**: ~1.5 hours (T025 → T026 sequential; T027 trivial trailing edit)

---

### Wave 3 — Day 3 Tue 2026-05-19 AM (Pre-PR gates)

**Pre-Wave 3 Gate**: T013 + T016 + T017 + T018 all PASS (cross-link no-emission verified + 5-baseline byte-identity verified).

| Task | Agent | Estimate |
|---|---|---|
| T028 | `architect` | 15 min (ADR-045 Status flip Proposed → Accepted) |
| T029 | `security-analyst` | 45 min (/security skill re-scan on modified file surface) |
| T030 | `tester` | 1.5 hours (17 quickstart.md verification recipes sequential) |

**Wave 3 wall-clock**: ~2.5 hours. T028 must complete before T029/T030 begin (Accepted-state required for security re-scan ADR coverage). T029 ∥ T030 once T028 done.

---

### Wave 4 — Day 3 Tue 2026-05-19 PM (Squash-merge + close-out)

**Pre-Squash-Merge Gate**: PR title is Conventional Commits `feat(292):` (T019 verification).

| Task | Agent | Estimate |
|---|---|---|
| T019 | `product-manager` | 10 min (PR title verify; retitle via `gh pr edit` if non-conventional) |
| (squash-merge by maintainer) | manual | 5 min |
| T020 | `devops` | 15 min (release-please verification within 30s; empty marker fallback) |
| T021 | `product-manager` | 15 min (CHANGELOG @armorer-labs attribution if path b) |
| T022 | `product-manager` | 20 min (discussion #179 delivery comment within 24h) |
| T031 | `architect` | 10 min (POST-MERGE Accepted-commit-SHA fill in ADR-045) |
| T032 | `senior-backend-engineer` | 5 min (BACKLOG regeneration shell script) |
| T033 | `senior-backend-engineer` | 30 min (KB entry in INSTITUTIONAL_KNOWLEDGE.md) |
| T034 | `orchestrator` | 30 min (`/aod.deliver` final close-out coordination) |

**Wave 4 wall-clock**: ~2.5 hours (T019 → squash-merge → T020+T031 in parallel → T021/T022/T032/T033 in parallel → T034)

---

### Buffer-1 — Wed 2026-05-20 (slip absorption)

| Activity | Owner |
|---|---|
| Reserve for Wave 3/4 slip per PRD worst-case path | — |
| Tier-Lead Q5(a) 5-hour budget consumption (if contributor PR steerage active) | team-lead |

---

### Buffer-2 — Thu 2026-05-21 (T+5d / T+7d community follow-ups)

| Task | Agent | Estimate |
|---|---|---|
| T023 | `product-manager` | 10 min (conditional T+5d courtesy nudge if no contributor response) |
| T024 | `product-manager` | 10 min (conditional T+7d SLA breach decision log) |

**Note**: T023 calendar date is Tue 2026-05-19 per tasks.md, but T+5d from T005 (Fri 2026-05-15) lands Wed 2026-05-20. Both tasks are conditional on no-response state. Treated as Buffer absorption if not needed earlier.

---

## 4. Quality Gates Between Waves

| Gate | Condition | Blocks |
|---|---|---|
| Pre-Wave 2a | T006 ADR-045 Proposed merged or staged on feature branch | Wave 2a, 2c entry |
| Pre-Wave 2c | T007 Cat 6 in place (baseline arch references new pattern surface) | Wave 2c entry |
| Pre-Wave 3 | T013 + T016 + T017 + T018 all PASS (no-emission verified, 5-baseline byte-identical) | Wave 3 entry |
| Pre-Wave 4 | T028 ADR Accepted + T029 /security re-scan PASS + T030 quickstart 17/17 PASS | Squash-merge eligibility |
| Pre-Squash-Merge | PR title Conventional Commits `feat(292):` (T019) | Wave 4 merge step |
| Post-Squash-Merge | release-please opened PR within 30s (T020) | Release pipeline integrity |

---

## 5. Time Estimates Per Wave

| Wave | Day | Wall-Clock | Critical Path Item |
|---|---|---|---|
| Wave 0 | Thu 2026-05-14 | COMPLETE | Triple sign-off APPROVED_WITH_CONCERNS |
| Wave 1 | Fri 2026-05-15 | ~4 hours | T006 ADR-045 authoring (architect, 2h) |
| Wave 2a | Mon 2026-05-18 AM | ~2.5 hours | T017 cross-link no-emission verification |
| Wave 2b | Mon 2026-05-18 AM (parallel) | ~1 hour | T018 5-baseline regression |
| Wave 2c | Mon 2026-05-18 PM | ~1.5 hours | T026 artifact generation + reproduction |
| Wave 3 | Tue 2026-05-19 AM | ~2.5 hours | T030 quickstart 17-step validation |
| Wave 4 | Tue 2026-05-19 PM | ~2.5 hours | T034 `/aod.deliver` close-out |
| Buffer-1 | Wed 2026-05-20 | Reserved | Slip absorption + Q5(a) tier-lead budget |
| Buffer-2 | Thu 2026-05-21 | Reserved | T023/T024 community follow-ups |

**Total focused effort**: ~1.5 working days (12 hours) across 4 working sessions; ~3 calendar days with buffer absorption (Day 1 Fri → Day 3 Tue with two-day weekend gap).

**Per Team-Lead PRD M-1 worst-case path**: With Q1=Cat 6 + Q2=Add + Q3=Add-ADR all materializing (they did), and worst-case task execution, /aod.deliver shifts to Buffer-1 (Wed 2026-05-20) without slipping into a third calendar week. Buffer-2 (Thu 2026-05-21) absorbs the T+5d/T+7d community follow-ups.

---

## 6. Agent Allocation Summary

| Agent | Task Count | Primary Role |
|---|---|---|
| `senior-backend-engineer` | 19 | Bulk markdown/YAML editing (Cat 6 + Cat 2 + US3 + KB + BACKLOG + baseline) |
| `product-manager` | 7 | Community-facing surface (T005, T019, T021–T024) + PR title gate |
| `tester` | 5 | Verification / regression / artifact-reproduction (T017, T018, T026, T030) |
| `architect` | 3 | ADR-045 dual-commit governance (T006 Proposed, T028 Accepted, T031 SHA fill) |
| `security-analyst` | 1 | /security re-scan on modified file surface (T029) |
| `devops` | 1 | release-please verification + empty-marker fallback (T020) |
| `orchestrator` | 1 | /aod.deliver final close-out coordination (T034) |
| `code-reviewer` | 0 | Not needed — docs-only refinement, no code changes |
| `frontend-developer` | 0 | Not needed — no UI changes |
| `ux-ui-designer` | 0 | Not needed — no UX/UI changes |
| `web-researcher` | 0 | Not needed — research complete at PRD stage |
| `debugger` | 0 | Not needed — no bug investigation |

**Workload balance**: `senior-backend-engineer` carries the bulk (19/34 = 56%) of docs editing — appropriate for docs-only refinement per CLAUDE.md fallback mapping ("Markdown / documentation writing → senior-backend-engineer"). No agent exceeds 80% load threshold (senior-backend-engineer at 56% is the highest). Calendar parallelism across waves prevents any single-agent serialization bottleneck.

---

## 7. Lens Findings (Constraint Analysis applied)

Per `docs/core_principles/README.md`, Constraint Analysis lens applied to validate that the critical path matches expected (T006 → T007 → T013 → T017 → T019 → squash-merge → T020 → T022 → T031) and that no hidden dependencies exist:

- **T013 → T007 dependency**: Cross-Agent Handoff subsection appends *after* Cat 6 (line 152 + Cat 6 block). Confirmed correct sequencing.
- **T017 → T013–T016 dependency**: No-emission verification requires all 4 US3 edits in place. Confirmed correct gating.
- **T018 ∥ T017 parallelism**: 5-baseline regression is byte-identity check on non-OI baselines; independent of US3 cross-link work. Confirmed parallel-safe.
- **T028 → all US3/US2/US1 dependency**: ADR Accepted flip happens at pre-PR gate (after all implementation, before `gh pr ready`). Confirmed correct gating.
- **T020 / T031 post-merge dependency**: Both depend on squash-merge SHA. Confirmed sequential after T019 retitle gate.

No hidden blockers detected. Critical path matches PRD + plan + tasks consistently.

---

## 8. Sign-off

**Team-Lead Status**: APPROVED — agent assignments balanced, capacity reconciliation clean, no in-flight collisions, critical path validated.

**Ready for**: orchestrator delegation per `/aod.build` invocation.

**Handoff to orchestrator**: Provide this file + tasks.md + Wave Strategy. Orchestrator coordinates per-wave execution, monitors completion, and reports back to team-lead for phase sign-offs.
