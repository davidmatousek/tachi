# Agent Assignments: ML Top 10 Coverage Bundle (F-6 / Feature 232)

**Feature**: F-6 — BLP-01 Tier 2 ML Top 10 Coverage Bundle
**Scope**: Three-agent enrichment (tampering + data-poisoning + model-theft)
**Envelope**: 2.5-day build (Wed 2026-04-29 → Fri 2026-05-01) + Mon 2026-05-04 buffer
**Wave Count**: 18 sequential waves (Phase 1 verification + Waves 0.0, 1.0, 1.1, 2.1, 2.2, 2.3, 3, 4.0, 4.1, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6 buffer)
**Total Tasks**: 64 tasks (T001–T064)
**Approved**: PM + Architect + Team-Lead triple sign-off applied at tasks.md frontmatter (2026-04-27)

---

## 1. Agent Assignment Matrix

Agents drawn from `.claude/agents/_README.md` Agent Registry. Allowed `subagent_type` values: `senior-backend-engineer`, `architect`, `tester`, `product-manager`, `team-lead`, `code-reviewer`, `devops`.

### Phase 1 — Setup Verification (T001–T006)

| Task ID | Agent | Rationale |
|---------|-------|-----------|
| T001 | tester | Baseline line-count gate (`wc -l`) |
| T002 | tester | Schema invariant verification (`grep`) |
| T003 | tester | ATLAS catalog-resolvability matrix verification |
| T004 | architect | ADR numbering availability check (architect owns ADR catalogue) |
| T005 | tester | Zero-MAESTRO grep gate |
| T006 | tester | Consumers-list presence verification |

### Phase 2 — Wave 0.0 (T007–T008)

| Task ID | Agent | Rationale |
|---------|-------|-----------|
| T007 | architect | Co-author predictive-ml-app architecture (5 topology indicators) — primary owner |
| T007 (co) | senior-backend-engineer | Co-author architecture authoring support |
| T008 | senior-backend-engineer | Placeholder README authoring (markdown) |

### Phase 2 — Wave 1.0 (T009)

| Task ID | Agent | Rationale |
|---------|-------|-----------|
| T009 | architect | Re-verify all 6 baseline assumptions; Heuristic A protocol confirmation |

### Phase 2 — Wave 1.1 (T010–T016)

| Task ID | Agent | Rationale |
|---------|-------|-----------|
| T010 | architect | ADR-035 Proposed authoring (10 D-numbered Decisions, 8-row mapping table) |
| T011 | senior-backend-engineer | tampering.md metadata edit (additive YAML) |
| T012 | senior-backend-engineer | tampering.md Purpose section additive append |
| T013 | senior-backend-engineer | tampering.md Step 5 references append + line-count cap |
| T014 | senior-backend-engineer | tampering companion Pattern Cat 10 authoring |
| T015 | senior-backend-engineer | tampering companion Pattern Category Disambiguation subsection |
| T016 | senior-backend-engineer | tampering Cat 10 fixture YAML authoring |

### Phase 3 — Wave 2.1 / 2.2 / 2.3 (T017–T025)

| Task ID | Agent | Rationale |
|---------|-------|-----------|
| T017 | senior-backend-engineer | data-poisoning.md metadata 7-line additive append |
| T018 | senior-backend-engineer | data-poisoning.md Purpose append |
| T019 | senior-backend-engineer | data-poisoning.md Step 5 append + line-count cap |
| T020 | senior-backend-engineer | Wave 2.1 / T-NN-1: Cat 8 Transfer Learning authoring (~90 min checkpoint) |
| T021 | senior-backend-engineer | Wave 2.2 / T-NN-2: Cat 9 Feedback-Loop Skewing authoring (~90 min checkpoint) |
| T022 | senior-backend-engineer | Wave 2.3 / T-NN-3: Cat 10 Predictive-ML Supply Chain + Disambiguation + Primary Sources |
| T023 | senior-backend-engineer | Cat 8 fixture authoring |
| T024 | senior-backend-engineer | Cat 9 fixture authoring |
| T025 | senior-backend-engineer | Cat 10 fixture authoring |

### Phase 3 — Wave 3 (T026–T037)

| Task ID | Agent | Rationale |
|---------|-------|-----------|
| T026 | senior-backend-engineer | model-theft.md metadata 4-line additive append |
| T027 | senior-backend-engineer | model-theft.md Purpose append |
| T028 | senior-backend-engineer | model-theft.md Step 5 append + line-count cap |
| T029 | senior-backend-engineer | Cat 12 Model Inversion authoring |
| T030 | senior-backend-engineer | Cat 13 Membership Inference authoring |
| T031 | senior-backend-engineer | Cat 14 Predictive-ML Artifact Supply Chain authoring |
| T032 | senior-backend-engineer | model-theft companion Pattern Category Disambiguation subsection |
| T033 | senior-backend-engineer | Primary Sources extension on model-theft companion |
| T034 | architect | Integration walkthrough Cat 10→11→12→13→14 visual continuity (team-lead C-2) |
| T035 | senior-backend-engineer | Cat 12 fixture |
| T036 | senior-backend-engineer | Cat 13 fixture |
| T037 | senior-backend-engineer | Cat 14 fixture |

### Phase 4 — Wave 4 US-2 Invariant Verification (T038–T041)

| Task ID | Agent | Rationale |
|---------|-------|-----------|
| T038 | tester | Schema invariant zero-diff gate |
| T039 | tester | 22-file zero-edit invariant gate (FR-019 / SC-021) |
| T040 | tester | Orchestrator + consumers-list zero functional edit gate |
| T041 | tester | Pattern Category Disambiguation 3/3 grep gate |

### Phase 5 — Wave 4.0 (T042–T045)

| Task ID | Agent | Rationale |
|---------|-------|-----------|
| T042 | senior-backend-engineer | predictive-ml-app end-to-end pipeline regen |
| T043 | tester | Aggregate ≥6 ML findings count verification |
| T044 | tester | OWASP ML primaries references-array grep |
| T045 | senior-backend-engineer | Mutation-target baseline PDF commit |

### Phase 5 — Wave 4.1 (T046–T047) — Tester parallel spot-check (FR-025)

| Task ID | Agent | Rationale |
|---------|-------|-----------|
| T046 | tester | Early-signal byte-identity spot-check on web-app |
| T047 | tester | Early-signal byte-identity spot-check on maestro-reference |

### Phase 5 — Wave 5.0 (T048) + Wave 5.1 (T049) — strong parallel (LOW-1)

| Task ID | Agent | Rationale |
|---------|-------|-----------|
| T048 | tester | Full 6-baseline byte-identity verification (AM-1) |
| T049 | architect | ADR-035 Proposed → Accepted transition (AM-2, parallel) |

### Phase 5 — Wave 5.2 (T050–T053)

| Task ID | Agent | Rationale |
|---------|-------|-----------|
| T050 | tester | Author new test_ml_top_10_coverage_bundle_enrichment.py (~300-400 lines) |
| T051 | tester | Modify test_backward_compatibility.py infrastructure (10→8 / 5→7) |
| T052 | tester | Run test suite (pytest -v) |
| T053 | code-reviewer | Code-review pass on 6 file edits + ADR-035 + new architecture |

### Phase 6 — Wave 5.3 (T054)

| Task ID | Agent | Rationale |
|---------|-------|-----------|
| T054 | senior-backend-engineer | BLP-01 Coverage Matrix six-row transition + milestone update (single commit) |

### Phase 7 — Wave 5.4 (T055) Triple Sign-Off

| Task ID | Agent | Rationale |
|---------|-------|-----------|
| T055 | product-manager | PM sign-off on tasks.md frontmatter |
| T055 | architect | Architect sign-off on tasks.md frontmatter |
| T055 | team-lead | Team-Lead sign-off on tasks.md frontmatter |

### Phase 7 — Wave 5.5 (T056–T060) Close-Out

| Task ID | Agent | Rationale |
|---------|-------|-----------|
| T056 | senior-backend-engineer | Pre-merge PR title Conventional Commit verification (`gh pr view/edit`) |
| T057 | senior-backend-engineer | `/aod.deliver` close-out: squash-merge PR #233 |
| T058 | senior-backend-engineer | Post-merge release-please verification + empty marker fallback |
| T059 | architect | Delivery retrospective authoring (FR-026 / SC-026) |
| T060 | architect | Post-merge ADR-035 SHA fill commit |

### Phase 8 — Wave 5.6 Buffer + Polish (T061–T064)

| Task ID | Agent | Rationale |
|---------|-------|-----------|
| T061 | senior-backend-engineer | CLAUDE.md Recent Changes update |
| T062 | senior-backend-engineer | Memory file feedback_blp01_progress.md update |
| T063 | senior-backend-engineer | `/aod.deliver 232` DoD validation |
| T064 | team-lead | R5 contingency invocation (deferral pair if triggered) |

---

## 2. Parallel Execution Waves

### Wave 0.0 — Predictive-ML-App Architecture (Plan Day Tue 2026-04-28 PM, ~4–6 hours)

- **Tasks**: T007 (co-authored), T008
- **Agents**: architect (lead), senior-backend-engineer (co), senior-backend-engineer (T008)
- **Parallelism**: T008 [P] alongside T007
- **Estimate**: 4–6 hours

### Wave 1.0 — Architect Re-Verification (Day 1 AM Wed 2026-04-29, 15–30 min)

- **Tasks**: T009
- **Agents**: architect
- **Parallelism**: Sequential gate
- **Estimate**: 15–30 min

### Wave 1.1 — ADR-035 + Tampering Edits + Fixtures (Day 1 AM Wed 2026-04-29, ~4 hours)

- **Tasks**: T010 [P], T011 [P], T012, T013, T014, T015, T016 [P]
- **Agents**: architect (T010), senior-backend-engineer (T011–T016)
- **Parallelism**: T010 + T011 + T016 strongly parallel (different files); T012–T015 sequential within tampering.md / detection-patterns.md
- **Estimate**: ~4 hours

### Wave 2.1 — Data-Poisoning Cat 8 Checkpoint T-NN-1 (Day 1 PM Wed 2026-04-29, ~90 min)

- **Tasks**: T017, T018, T019, T020 (T-NN-1), T023 [P]
- **Agents**: senior-backend-engineer
- **Parallelism**: T023 fixture parallel with T020 authoring
- **Estimate**: ~90 min (team-lead MEDIUM-2 checkpoint with self-review + rollback)

### Wave 2.2 — Data-Poisoning Cat 9 Checkpoint T-NN-2 (Day 1 PM Wed 2026-04-29, ~90 min)

- **Tasks**: T021 (T-NN-2), T024 [P]
- **Agents**: senior-backend-engineer
- **Parallelism**: T024 fixture parallel with T021 authoring
- **Estimate**: ~90 min (sequential after T020 self-review)

### Wave 2.3 — Data-Poisoning Cat 10 Checkpoint T-NN-3 (Day 1 PM Wed 2026-04-29, ~90 min)

- **Tasks**: T022 (T-NN-3), T025 [P]
- **Agents**: senior-backend-engineer
- **Parallelism**: T025 fixture parallel with T022 authoring
- **Estimate**: ~90 min (sequential after T021 self-review)

### Wave 3 — Model-Theft Edits + Pattern Categories 12/13/14 (Day 2 AM Thu 2026-04-30, ~4 hours)

- **Tasks**: T026, T027, T028, T029, T030, T031, T032, T033, T034, T035 [P], T036 [P], T037 [P]
- **Agents**: senior-backend-engineer (T026–T033, T035–T037), architect (T034 walkthrough)
- **Parallelism**: Cat 12/13/14 sequential within file; T035/36/37 fixtures parallel; T034 walkthrough after T033
- **Estimate**: ~4 hours

### Wave 4.0 — Predictive-ML-App End-to-End Regen (Day 2 PM Thu 2026-04-30, ~2 hours)

- **Tasks**: T042, T043, T044, T045
- **Agents**: senior-backend-engineer (T042, T045), tester (T043, T044)
- **Parallelism**: T043/T044 verification can begin once T042 emits artifacts
- **Estimate**: ~2 hours

### Wave 4.1 — Tester Early-Signal Spot-Check (parallel with Wave 4.0; Day 2 PM Thu 2026-04-30, ~1 hour)

- **Tasks**: T046 [P], T047 [P]
- **Agents**: tester
- **Parallelism**: Both spot-checks parallel; weakly parallel with Wave 4.0 (FR-025 / team-lead MEDIUM-3)
- **Estimate**: ~1 hour

### Wave 5.0 — Tester Full 6-Baseline Verification (Day 3 AM Fri 2026-05-01, ~2 hours)

- **Tasks**: T048
- **Agents**: tester (AM-1)
- **Parallelism**: Strong parallel with Wave 5.1 (different owner)
- **Estimate**: ~2 hours

### Wave 5.1 — Architect ADR-035 Accepted (Day 3 AM Fri 2026-05-01, ~30 min)

- **Tasks**: T049
- **Agents**: architect (AM-2)
- **Parallelism**: Strong parallel with Wave 5.0 (team-lead LOW-1)
- **Estimate**: ~30 min

### Wave 5.2 — Test Infrastructure + Code-Review (Day 3 AM Fri 2026-05-01, ~2 hours)

- **Tasks**: T050 [P], T051 [P], T052, T053
- **Agents**: tester (T050–T052), code-reviewer (T053)
- **Parallelism**: T050 + T051 parallel (different files); T052 sequential after both; T053 parallel with T052 on different concern
- **Estimate**: ~2 hours

### Wave 5.3 — Coverage Matrix Six-Row Update (Day 3 PM Fri 2026-05-01, ~30 min)

- **Tasks**: T054
- **Agents**: senior-backend-engineer
- **Parallelism**: Sequential (single commit per FR-023)
- **Estimate**: ~30 min

### Wave 5.4 — Triple Sign-Off (Day 3 PM Fri 2026-05-01, ~30 min)

- **Tasks**: T055
- **Agents**: product-manager + architect + team-lead (parallel sign-off via Triad parallel review)
- **Parallelism**: All three sign-offs in parallel
- **Estimate**: ~30 min

### Wave 5.5 — Close-Out + Release-Please + Retrospective (Day 3 PM Fri 2026-05-01, ~2 hours)

- **Tasks**: T056, T057, T058, T059, T060
- **Agents**: senior-backend-engineer (T056–T058), architect (T059, T060)
- **Parallelism**: T056→T057→T058 sequential (merge gate); T059 retrospective parallel with T060 SHA fill
- **Estimate**: ~2 hours

### Wave 5.6 — Buffer Day Polish (Mon 2026-05-04, conditional)

- **Tasks**: T061 [P], T062 [P], T063 [P], T064 (conditional)
- **Agents**: senior-backend-engineer (T061–T063), team-lead (T064 if R5 triggers)
- **Parallelism**: T061–T063 fully parallel; T064 only if escalation
- **Estimate**: ~1–2 hours buffer

---

## 3. Quality Gates Between Waves

| Gate | Wave | Owner | Decision Criterion |
|------|------|-------|--------------------|
| Wave 0.0 → Wave 1.0 | architect | Predictive-ml-app exhibits all 5 indicators? |
| Wave 1.0 → Wave 1.1 | architect | All 6 baseline assumptions verified? Heuristic A protocol intact at three-agent scope? |
| Wave 1.1 → Wave 2.1 | senior-backend-engineer | Tampering edits + Cat 10 + Disambiguation byte-identity-clean? ADR-035 Proposed committed with 8-row mapping table COMPLETE? |
| Wave 2.1 → Wave 2.2 | senior-backend-engineer + team-lead MEDIUM-2 | T-NN-1 (Cat 8) self-reviewed and clean? Rollback unused? |
| Wave 2.2 → Wave 2.3 | senior-backend-engineer + team-lead MEDIUM-2 | T-NN-2 (Cat 9) self-reviewed and clean? |
| Wave 2.3 → Wave 3 | senior-backend-engineer + team-lead MEDIUM-2 | T-NN-3 (Cat 10) self-reviewed and clean? data-poisoning ≤150 lines verified? |
| Wave 3 → Wave 4.0 | architect | Visual continuity Cat 10→11→12→13→14 verified? Pattern Category Disambiguation present on all 3 companions? model-theft ≤150 lines verified? |
| Wave 4.0 → Wave 4.1 | senior-backend-engineer + tester | Predictive-ml-app regen yields ≥6 new ML findings? Tester engaged for early-signal spot-check? |
| Wave 4.1 → Wave 5.0 | tester | Spot-check on 2 baselines green? |
| Wave 5.0 → Wave 5.2 | tester (parallel architect on Wave 5.1) | Full 6-baseline verification 6/6? ADR-035 Accepted committed (parallel)? |
| Wave 5.2 → Wave 5.3 | senior-backend-engineer + code-reviewer | All tests + code-review pass green? |
| Wave 5.3 → Wave 5.4 | senior-backend-engineer | Coverage Matrix six-row transition committed? |
| Wave 5.4 → Wave 5.5 | PM + Architect + Team-Lead | Triple sign-off recorded on tasks.md frontmatter? |
| Wave 5.5 → Wave 5.6 (buffer) | senior-backend-engineer + architect | Pre-merge title verified + post-merge release-please fired + retrospective filed + ADR-035 SHA filled? |

---

## 4. Time Estimates per Wave (2.5-Day Envelope)

| Wave | Duration | Calendar Slot | Cumulative |
|------|----------|---------------|------------|
| Phase 1 verification | 15 min | Plan Day Tue PM | 15 min |
| Wave 0.0 | 4–6 hours | Plan Day Tue PM | ~6 hours |
| Wave 1.0 | 15–30 min | Day 1 AM Wed | ~6.5 hours |
| Wave 1.1 | ~4 hours | Day 1 AM Wed | ~10.5 hours (Day 1 AM done) |
| Wave 2.1 | ~90 min | Day 1 PM Wed | Day 1 PM 90 min |
| Wave 2.2 | ~90 min | Day 1 PM Wed | Day 1 PM 180 min |
| Wave 2.3 | ~90 min | Day 1 PM Wed | Day 1 PM 270 min (~4.5 hours; Day 1 done) |
| Wave 3 | ~4 hours | Day 2 AM Thu | Day 2 AM done |
| Wave 4.0 | ~2 hours | Day 2 PM Thu | Day 2 PM 2 hours |
| Wave 4.1 (parallel) | ~1 hour | Day 2 PM Thu | (parallel; weak overlap with 4.0) |
| Wave 5.0 | ~2 hours | Day 3 AM Fri | Day 3 AM 2 hours |
| Wave 5.1 (parallel) | ~30 min | Day 3 AM Fri | (parallel with 5.0) |
| Wave 5.2 | ~2 hours | Day 3 AM Fri | Day 3 AM 4 hours |
| Wave 5.3 | ~30 min | Day 3 PM Fri | Day 3 PM 30 min |
| Wave 5.4 | ~30 min | Day 3 PM Fri | Day 3 PM 60 min |
| Wave 5.5 | ~2 hours | Day 3 PM Fri | Day 3 PM ~3 hours (Day 3 done) |
| Wave 5.6 buffer | 1–2 hours | Mon Buffer Day | Reserved (conditional) |

**Total billable**: ~22 hours core + Wave 0.0 plan-day prep (~5 hours) + buffer reserve (~2 hours) = ~24–29 hours across 2.5 days. Realistic for 64-task envelope at three-agent enrichment scope.

---

## 5. Critical Path Summary

```
T007 (predictive-ml-app architecture, plan day)
  → T009 (architect re-verification, Day 1 AM)
  → T010 (ADR-035 Proposed, Day 1 AM, parallel start)
  → T011-T015 (tampering enrichment, Day 1 AM, sequential within file)
  → T017-T022 (data-poisoning enrichment, Day 1 PM, T-NN-1/2/3 sequential checkpoints)
  → T026-T033 (model-theft enrichment, Day 2 AM, sequential within file)
  → T042-T045 (predictive-ml-app regen, Day 2 PM)
  → T048 (tester full 6-baseline verification, Day 3 AM-1)
  → T049 (architect ADR-035 Accepted, Day 3 AM-2, strong parallel)
  → T054 (Coverage Matrix six-row update, Day 3 PM)
  → T055-T058 (triple sign-off + close-out + release-please verification, Day 3 PM)
  → T059 (delivery retrospective, Day 3 PM, FR-026 / SC-026)
```

**Critical path nodes** = T007 → T009 → T010 → T011-T015 → T017-T022 → T026-T033 → T042-T045 → T048 → T049 → T054 → T055-T058 → T059 (12 nodes / ~22 critical hours).

---

## 6. Resource Allocation Summary

| Agent | Tasks | Critical-Path Touchpoints | Workload |
|-------|-------|---------------------------|----------|
| senior-backend-engineer | 41 (T008, T011–T033 ex-T010, T035–T037, T042, T045, T051 (no — tester), T054, T056–T058, T061–T063) | T011-T015, T017-T033, T042-T045, T054, T056-T058 | Primary executor, ~70% load |
| architect | 8 (T004, T007 lead, T009, T010, T034, T049, T059, T060) | T007, T009, T010, T034, T049, T059, T060 | Architecture + ADR + walkthrough + retrospective, ~30% load |
| tester | 13 (T001-T003, T005-T006, T038-T041, T043-T044, T046-T048, T050-T052) | T046-T048, T050-T052 | Verification + test authoring, ~25% load |
| code-reviewer | 1 (T053) | T053 | Single review pass at Wave 5.2 |
| product-manager | 1 (T055) | T055 | Sign-off only |
| team-lead | 2 (T055, T064 conditional) | T055 | Sign-off + R5 escalation |

**No agent exceeds 80% loading** per team-lead acceptance criterion. Critical path runs on senior-backend-engineer (primary) + architect (gates + ADR + walkthroughs) with tester (verification gates) and code-reviewer (single review pass).

---

## Appendix: Owner Annotation Source

All owner assignments derived from explicit task annotations in tasks.md (e.g., "Architect re-verifies", "TEAM-LEAD MEDIUM-2 CHECKPOINT", "Tester (per FR-025)") cross-referenced against the Agent Registry at `.claude/agents/_README.md`. Sign-off authority follows triad governance matrix (PM + Architect + Team-Lead on tasks.md).

**End of Agent Assignments**
