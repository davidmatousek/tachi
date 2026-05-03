# Agent Assignments: Mobile Top 10 Coverage Bundle (F-7 / Feature 237)

**Feature**: F-7 — BLP-01 Tier 2 Mobile Top 10 Coverage Bundle
**Scope**: Four-or-five-agent enrichment (spoofing + tampering + info-disclosure + privilege-escalation + repudiation, dual-host M8 default)
**Envelope**: 3.0-day build (Wed 2026-04-29 → Mon 2026-05-04 close-out) + Tue 2026-05-05 reserve
**Wave Count**: 22 sequential waves (Phase 1 verification + Waves 0.0, 0.1, 1.0, 1.1, 2.0, 2.1, 2.2, 2.3, 3.0, 3.1, 3.2, 3.3, 3.4, 4.0, 4.0b, 4.1, 4.2, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6 reserve)
**Total Tasks**: 82 tasks (T001–T082)
**Approved**: PM + Architect + Team-Lead triple sign-off APPROVED_WITH_CONCERNS at tasks.md frontmatter (2026-04-28)

---

## 1. Agent Assignment Matrix

Agents drawn from `.claude/agents/_README.md` Agent Registry. Allowed `subagent_type` values: `senior-backend-engineer`, `architect`, `tester`, `product-manager`, `team-lead`, `code-reviewer`.

### Phase 1 — Setup Verification (T001–T008)

| Task ID | Description | Agent | Wave | Notes |
|---------|-------------|-------|------|-------|
| T001 | Baseline line-count gate (10 files via `wc -l`) | tester | Phase 1 | Verification gate |
| T002 | Schema invariant verification (`grep`) | tester | Phase 1 | Schema 1.8 unchanged |
| T003 | M1-M10 catalog-resolvability (10/10) | tester | Phase 1 | OWASP Mobile primaries |
| T004 | ATT&CK Mobile catalog gap verify (T1474/T1626/T1398 = 0/0/0) | tester | Phase 1 | Q3 plan-time RESOLVED |
| T005 | ADR-036 next-available numbering | architect | Phase 1 | Architect owns ADR catalogue |
| T006 | Zero MAESTRO grep gate (10 files) | tester | Phase 1 | FR-13/SC-15 invariant |
| T007 | Consumers-list presence (5 hosts) | tester | Phase 1 | FR-14 invariant |
| T008 | Zero structural mobile-platform indicators on existing 6 baselines | tester | Phase 1 | Q2 grounding for mutation-target authoring |

### Phase 2 — Wave 0.0 Mobile-Banking-App Skeleton (T009)

| Task ID | Description | Agent | Wave | Notes |
|---------|-------------|-------|------|-------|
| T009 | architecture.md skeleton (~80-120 lines, 5 of 6 indicators) | architect | Wave 0.0 | PRD-day evening; team-lead MEDIUM-1 |

### Phase 2 — Wave 0.1 Mobile-Banking-App Full Draft (T010–T011)

| Task ID | Description | Agent | Wave | Notes |
|---------|-------------|-------|------|-------|
| T010 | architecture.md full draft (~180-220 lines, all 6 indicators) | architect + senior-backend-engineer | Wave 0.1 | Co-authored; architect leads |
| T011 | README placeholder (mutation target marker) | senior-backend-engineer | Wave 0.1 | [P] alongside T010 |

### Phase 2 — Wave 1.0 Architect Re-Verification + ADR-036 Proposed (T012–T013)

| Task ID | Description | Agent | Wave | Notes |
|---------|-------------|-------|------|-------|
| T012 | Re-verify all baseline assumptions | architect | Wave 1.0 | Sequential gate, 30-60 min |
| T013 | ADR-036 Proposed authoring (10 D-numbered Decisions, 11-row table) | architect | Wave 1.0 | Architect MEDIUM-2 RESOLVED |

### Phase 2 — Wave 1.1 Spoofing Edits + Cat N+1/N+2 + Disambiguation + Fixtures (T014–T022)

| Task ID | Description | Agent | Wave | Notes |
|---------|-------------|-------|------|-------|
| T014 | spoofing.md metadata YAML M1+M3 append | senior-backend-engineer | Wave 1.1 | Edit 1 |
| T015 | spoofing.md Purpose section additive append | senior-backend-engineer | Wave 1.1 | Edit 2 |
| T016 | spoofing.md Step 5 references append + line-count cap | senior-backend-engineer | Wave 1.1 | Edit 3 (≤120 lines) |
| T017 | Cat N+1 M1 Improper Mobile Credential Usage authoring | senior-backend-engineer | Wave 1.1 | Companion Cat N+1 |
| T018 | Cat N+2 M3 Insecure Mobile Auth/Authz authoring | senior-backend-engineer | Wave 1.1 | Companion Cat N+2 |
| T019 | Pattern Category Disambiguation subsection (boundary Cat 1-N vs N+1/N+2) | senior-backend-engineer | Wave 1.1 | ADR-036 D-9 |
| T020 | Primary Sources extension (M1:2024 + M3:2024) | senior-backend-engineer | Wave 1.1 | SC-11 |
| T021 | Cat N+1 M1 fixture YAML | senior-backend-engineer | Wave 1.1 | [P] |
| T022 | Cat N+2 M3 fixture YAML | senior-backend-engineer | Wave 1.1 | [P] |

### Phase 3 — Wave 2.0/2.1/2.2/2.3 Tampering Edits + Cat 11/12/13 (T023–T031)

| Task ID | Description | Agent | Wave | Notes |
|---------|-------------|-------|------|-------|
| T023 | tampering.md metadata 3-line append (M2+M4+M7) | senior-backend-engineer | Wave 2.0 | Edit 1 |
| T024 | tampering.md Purpose append | senior-backend-engineer | Wave 2.0 | Edit 2 |
| T025 | tampering.md Step 5 append + line-count cap | senior-backend-engineer | Wave 2.0 | Edit 3 (≤120 lines) |
| T026 | T-NN-1: Cat 11 Mobile Supply Chain Integrity (M2) | senior-backend-engineer | Wave 2.1 | Checkpoint ~75-90 min |
| T027 | T-NN-2: Cat 12 Mobile IPC Input Validation (M4) + F-1 disjoint-tells | senior-backend-engineer | Wave 2.2 | ADR-036 D-5 cross-axis |
| T028 | T-NN-3: Cat 13 Mobile Binary Protections (M7) + Disambiguation + Primary Sources | senior-backend-engineer | Wave 2.3 | Wave 2 close-out |
| T029 | Cat 11 fixture YAML | senior-backend-engineer | Wave 2.3 | [P] |
| T030 | Cat 12 fixture YAML (with disjoint-tells annotation) | senior-backend-engineer | Wave 2.3 | [P] |
| T031 | Cat 13 fixture YAML | senior-backend-engineer | Wave 2.3 | [P] |

### Phase 3 — Wave 3.0/3.1/3.2/3.3/3.4 Info-Disclosure Edits + 4 Sub-Categories (T032–T042)

| Task ID | Description | Agent | Wave | Notes |
|---------|-------------|-------|------|-------|
| T032 | info-disclosure.md metadata 4-line append (M5+M6+M9+M10) | senior-backend-engineer | Wave 3.0 | Edit 1 |
| T033 | info-disclosure.md Purpose append | senior-backend-engineer | Wave 3.0 | Edit 2 |
| T034 | info-disclosure.md Step 5 append + line-count cap | senior-backend-engineer | Wave 3.0 | Edit 3 (≤120 lines) |
| T035 | M5-1: Cat N+1 Insecure Mobile Communication (M5) | senior-backend-engineer | Wave 3.1 | Sub-checkpoint, team-lead MEDIUM-2 |
| T036 | M6-1: Cat N+2 Inadequate Mobile Privacy Controls (M6) | senior-backend-engineer | Wave 3.2 | Sub-checkpoint |
| T037 | M9-1: Cat N+3 Insecure Mobile Data Storage (M9) | senior-backend-engineer | Wave 3.3 | Sub-checkpoint |
| T038 | M10-1: Cat N+4 Insufficient Mobile Cryptography (M10) + Disambiguation + Primary Sources | senior-backend-engineer | Wave 3.4 | Wave 3 close-out |
| T039 | Cat N+1 M5 fixture YAML | senior-backend-engineer | Wave 3.4 | [P] |
| T040 | Cat N+2 M6 fixture YAML | senior-backend-engineer | Wave 3.4 | [P] |
| T041 | Cat N+3 M9 fixture YAML | senior-backend-engineer | Wave 3.4 | [P] |
| T042 | Cat N+4 M10 fixture YAML | senior-backend-engineer | Wave 3.4 | [P] |

### Phase 3 — Wave 4.0/4.0b M8 Dual-Host (privilege-escalation + repudiation) + Integration (T043–T053)

| Task ID | Description | Agent | Wave | Notes |
|---------|-------------|-------|------|-------|
| T043 | privilege-escalation.md metadata M8 append | senior-backend-engineer | Wave 4.0 | PART A Edit 1 |
| T044 | privilege-escalation.md Purpose append | senior-backend-engineer | Wave 4.0 | PART A Edit 2 |
| T045 | privilege-escalation.md Step 5 append + line-count cap | senior-backend-engineer | Wave 4.0 | PART A Edit 3 (≤120 lines) |
| T046 | privilege-escalation companion Cat N+1 M8 privilege-gain variant + Disambiguation + Primary Sources | senior-backend-engineer | Wave 4.0 | PART A close-out |
| T047 | repudiation.md metadata M8 append | senior-backend-engineer | Wave 4.0b | PART B Edit 1 |
| T048 | repudiation.md Purpose append | senior-backend-engineer | Wave 4.0b | PART B Edit 2 |
| T049 | repudiation.md Step 5 append + line-count cap | senior-backend-engineer | Wave 4.0b | PART B Edit 3 (≤120 lines) |
| T050 | repudiation companion Cat N+1 M8 accountability-loss variant + Disambiguation + Primary Sources | senior-backend-engineer | Wave 4.0b | PART B close-out |
| T051 | Architect integration walkthrough M8 dual-host disjoint-tells | architect | Wave 4.0b | ADR-036 D-4 verification |
| T052 | privilege-escalation M8 fixture YAML | senior-backend-engineer | Wave 4.0b | [P] |
| T053 | repudiation M8 fixture YAML | senior-backend-engineer | Wave 4.0b | [P] |

### Phase 4 — US-2 Invariant Verification (T054–T058)

| Task ID | Description | Agent | Wave | Notes |
|---------|-------------|-------|------|-------|
| T054 | Schema invariant zero-diff gate (FR-13/SC-15) | tester | Wave 4-end | Verification gate |
| T055 | 18-file zero-edit invariant gate (FR-14/SC-16) | tester | Wave 4-end | Dual-host scope |
| T056 | Orchestrator + consumers-list zero functional edit gate (FR-14) | tester | Wave 4-end | |
| T057 | Pattern Category Disambiguation 5/5 grep gate (ADR-036 D-9 dual-host) | tester | Wave 4-end | |
| T058 | Zero MAESTRO post-edit grep on 10 enriched files | tester | Wave 4-end | |

### Phase 5 — Wave 4.1 Tester Early-Signal Spot-Check (T059–T060)

| Task ID | Description | Agent | Wave | Notes |
|---------|-------------|-------|------|-------|
| T059 | Early-signal byte-identity spot-check on web-app | tester | Wave 4.1 | [P]; FR-15 separation-of-duties |
| T060 | Early-signal byte-identity spot-check on maestro-reference | tester | Wave 4.1 | [P]; weak parallel with regen |

### Phase 5 — Wave 4.2 Mobile-Banking-App Regen + Verification (T061–T065)

| Task ID | Description | Agent | Wave | Notes |
|---------|-------------|-------|------|-------|
| T061 | mobile-banking-app end-to-end pipeline regen | senior-backend-engineer | Wave 4.2 | FR-10 |
| T062 | Aggregate ≥10/≥11 Mobile findings count verification | senior-backend-engineer | Wave 4.2 | SC-12 |
| T063 | OWASP Mobile primaries references-array grep (≥10 distinct) | senior-backend-engineer | Wave 4.2 | SC-17 |
| T064 | ATT&CK Mobile catalog gap codification verification (T1474/T1626/T1398 prose-only) | senior-backend-engineer | Wave 4.2 | ADR-036 D-7 |
| T065 | Mutation-target baseline PDF commit | senior-backend-engineer | Wave 4.2 | Q6 RESOLVED |

### Phase 5 — Wave 5.0/5.1 Strong Parallel (T066–T067)

| Task ID | Description | Agent | Wave | Notes |
|---------|-------------|-------|------|-------|
| T066 | Full 6-baseline byte-identity verification (AM-1) | tester | Wave 5.0 | SC-13 |
| T067 | ADR-036 Proposed → Accepted transition (AM-2, parallel) | architect | Wave 5.1 | Strong parallel with T066 |

### Phase 5 — Wave 5.2 Test Infrastructure + Code-Review (T068–T071)

| Task ID | Description | Agent | Wave | Notes |
|---------|-------------|-------|------|-------|
| T068 | New test_mobile_top_10_coverage_bundle_enrichment.py (~500-600 lines) | tester | Wave 5.2 | [P]; 7 test classes |
| T069 | Modify test_backward_compatibility.py infra (8→4 dual-host; +4 hosts; mobile-banking-app exclusion) | senior-backend-engineer | Wave 5.2 | [P]; architect MEDIUM-1 verify-before-apply |
| T070 | Run test suite (pytest -v) | tester | Wave 5.2 | Sequential after T068+T069 |
| T071 | Code-review pass on 10 file edits + ADR-036 + new architecture | code-reviewer | Wave 5.2 | Parallel with T070 |

### Phase 6 — Wave 5.3 Coverage Matrix Ten-Row Update (T072)

| Task ID | Description | Agent | Wave | Notes |
|---------|-------------|-------|------|-------|
| T072 | BLP-01 Coverage Matrix M1-M10 ten-row transition + 40/40 milestone (single commit) | senior-backend-engineer | Wave 5.3 | FR-12 |

### Phase 7 — Wave 5.4 Triple Sign-Off (T073)

| Task ID | Description | Agent | Wave | Notes |
|---------|-------------|-------|------|-------|
| T073 | PM sign-off on tasks.md frontmatter | product-manager | Wave 5.4 | Parallel triple sign-off |
| T073 | Architect sign-off on tasks.md frontmatter | architect | Wave 5.4 | Parallel triple sign-off |
| T073 | Team-Lead sign-off on tasks.md frontmatter | team-lead | Wave 5.4 | Parallel triple sign-off |

### Phase 7 — Wave 5.5 Close-Out + Release-Please + Retrospective (T074–T078)

| Task ID | Description | Agent | Wave | Notes |
|---------|-------------|-------|------|-------|
| T074 | Pre-merge PR title Conventional Commit verification (`gh pr view/edit`) | senior-backend-engineer | Wave 5.5 | git-workflow.md Pre-merge |
| T075 | `/aod.deliver` close-out: squash-merge PR #238 | senior-backend-engineer | Wave 5.5 | Sequential merge gate |
| T076 | Post-merge release-please verification + empty marker fallback | senior-backend-engineer | Wave 5.5 | F-212 incident precedent |
| T077 | Delivery retrospective authoring (FR-26 / SC-26) | architect | Wave 5.5 | Parallel with T078 |
| T078 | Post-merge ADR-036 SHA fill commit | architect | Wave 5.5 | Parallel with T077 |

### Phase 8 — Wave 5.6 Reserve + Polish (T079–T082)

| Task ID | Description | Agent | Wave | Notes |
|---------|-------------|-------|------|-------|
| T079 | CLAUDE.md Recent Changes update | senior-backend-engineer | Wave 5.6 | [P]; polish |
| T080 | Memory file project_blp01_threat_coverage.md update | senior-backend-engineer | Wave 5.6 | [P]; polish |
| T081 | `/aod.deliver 237` DoD validation | senior-backend-engineer | Wave 5.6 | [P]; final close-out |
| T082 | R5/R6 reserve-day fallback if triggered (deferral pair) | team-lead | Wave 5.6 | Conditional only |

---

## 2. Parallel Execution Waves

### Wave 0.0 — Mobile-Banking-App Skeleton (PRD-day evening Tue 2026-04-28 PM, ~2-3 hours)

- **Tasks**: T009
- **Agents**: architect (sole owner per team-lead MEDIUM-1)
- **Parallelism**: Sequential
- **Estimate**: 2-3 hours

### Wave 0.1 — Mobile-Banking-App Full Draft (Plan-day AM-early Wed 2026-04-29, ~4-5 hours)

- **Tasks**: T010, T011 [P]
- **Agents**: architect (lead), senior-backend-engineer (co-author + T011)
- **Parallelism**: T011 README parallel alongside T010 full draft
- **Estimate**: 4-5 hours

### Wave 1.0 — Architect Re-Verification + ADR-036 Proposed (Plan-day AM-mid Wed 2026-04-29, ~2 hours)

- **Tasks**: T012, T013
- **Agents**: architect
- **Parallelism**: Sequential gate (T012 → T013)
- **Estimate**: ~2 hours (T012 30 min + T013 ~90 min)

### Wave 1.1 — Spoofing Enrichment + 2 Fixtures (Plan-day AM-late Wed 2026-04-29, ~3 hours)

- **Tasks**: T014, T015, T016, T017, T018, T019, T020, T021 [P], T022 [P]
- **Agents**: senior-backend-engineer
- **Parallelism**: T021 + T022 fixtures parallel; T014-T020 sequential within file
- **Estimate**: ~3 hours

### Wave 2.0/2.1/2.2/2.3 — Tampering Enrichment + 3 Fixtures (Plan-day PM Wed 2026-04-29, ~5 hours)

- **Tasks**: T023, T024, T025, T026 (T-NN-1), T027 (T-NN-2), T028 (T-NN-3), T029 [P], T030 [P], T031 [P]
- **Agents**: senior-backend-engineer
- **Parallelism**: Sequential checkpoints T-NN-1 → T-NN-2 → T-NN-3 (~75-90 min each); T029-T031 fixtures parallel after T028
- **Estimate**: ~5 hours (densest authoring slot per F-6 Wave 2.x precedent)

### Wave 3.0/3.1/3.2/3.3/3.4 — Info-Disclosure Enrichment + 4 Fixtures (Build Day 1 AM Thu 2026-04-30, ~5-6 hours)

- **Tasks**: T032, T033, T034, T035 (M5-1), T036 (M6-1), T037 (M9-1), T038 (M10-1), T039 [P], T040 [P], T041 [P], T042 [P]
- **Agents**: senior-backend-engineer
- **Parallelism**: Sequential sub-checkpoints M5-1 → M6-1 → M9-1 → M10-1 (~75-90 min each); T039-T042 fixtures parallel after T038
- **Estimate**: ~5-6 hours (team-lead MEDIUM-2 may spillover to PM)

### Wave 4.0 + 4.0b — M8 Dual-Host privilege-escalation + repudiation + Integration (Build Day 1 PM Thu 2026-04-30, ~3 hours)

- **Tasks**: T043, T044, T045, T046, T047, T048, T049, T050, T051, T052 [P], T053 [P]
- **Agents**: senior-backend-engineer (T043-T050+T052-T053), architect (T051 walkthrough)
- **Parallelism**: PART A (T043-T046) → PART B (T047-T050) sequential; T051 architect verification after both; T052+T053 fixtures parallel
- **Estimate**: ~3 hours

### Wave 4-end Verification (Build Day 1 PM Thu 2026-04-30, ~30 min)

- **Tasks**: T054, T055, T056, T057, T058
- **Agents**: tester
- **Parallelism**: Sequential grep gates after Wave 4.0b complete
- **Estimate**: ~30 min

### Wave 4.1 — Tester Early-Signal Spot-Check (parallel with Wave 4.2; Build Day 1 PM Thu 2026-04-30, ~1 hour)

- **Tasks**: T059 [P], T060 [P]
- **Agents**: tester
- **Parallelism**: Both spot-checks parallel; weak parallel with Wave 4.2 regen (FR-15)
- **Estimate**: ~1 hour

### Wave 4.2 — Mobile-Banking-App End-to-End Regen (Build Day 1 PM Thu 2026-04-30, ~2 hours)

- **Tasks**: T061, T062, T063, T064, T065
- **Agents**: senior-backend-engineer
- **Parallelism**: T062-T064 verification sequential after T061 emits artifacts; T065 commit final step
- **Estimate**: ~2 hours

### Wave 5.0 + 5.1 — Strong Parallel (Build Day 2 AM Fri 2026-05-01)

- **Tasks**: T066, T067
- **Agents**: tester (T066, AM-1) + architect (T067, AM-2)
- **Parallelism**: Strong parallel — different owners, different files (per F-6 Wave 5.0/5.1 precedent)
- **Estimate**: ~2 hours T066 || ~30 min T067

### Wave 5.2 — Test Infrastructure + Code-Review (Build Day 2 AM Fri 2026-05-01, ~2 hours)

- **Tasks**: T068 [P], T069 [P], T070, T071
- **Agents**: tester (T068, T070), senior-backend-engineer (T069), code-reviewer (T071)
- **Parallelism**: T068 + T069 parallel (different files); T070 sequential after both; T071 parallel with T070 on different concern
- **Estimate**: ~2 hours

### Wave 5.3 — Coverage Matrix Ten-Row Update (Build Day 2 PM Fri 2026-05-01, ~30 min)

- **Tasks**: T072
- **Agents**: senior-backend-engineer
- **Parallelism**: Sequential (single commit per FR-12)
- **Estimate**: ~30 min

### Wave 5.4 — Triple Sign-Off (Build Day 2 PM Fri 2026-05-01, ~30 min)

- **Tasks**: T073
- **Agents**: product-manager + architect + team-lead (parallel sign-off via Triad parallel review)
- **Parallelism**: All three sign-offs in parallel
- **Estimate**: ~30 min

### Wave 5.5 — Close-Out + Release-Please + Retrospective (Close-Out Day Mon 2026-05-04, ~3 hours)

- **Tasks**: T074, T075, T076, T077, T078
- **Agents**: senior-backend-engineer (T074-T076), architect (T077, T078)
- **Parallelism**: T074→T075→T076 sequential (merge gate); T077 retrospective parallel with T078 SHA fill
- **Estimate**: ~3 hours

### Wave 5.6 — Reserve Day Polish (Tue 2026-05-05, conditional)

- **Tasks**: T079 [P], T080 [P], T081 [P], T082 (conditional)
- **Agents**: senior-backend-engineer (T079-T081), team-lead (T082 if R5/R6 triggers)
- **Parallelism**: T079-T081 fully parallel; T082 only if escalation
- **Estimate**: ~1-2 hours buffer

---

## 3. Quality Gates Between Waves

| Gate | Wave | Owner | Decision Criterion |
|------|------|-------|--------------------|
| Phase 1 → Wave 0.0 | tester | All baseline assumptions verified? Mobile-platform indicators absent on existing baselines? |
| Wave 0.0 → Wave 0.1 | architect | Mobile-banking-app skeleton exhibits 5 of 6 indicators? |
| Wave 0.1 → Wave 1.0 | architect | Architecture exhibits all 6 indicators (debug endpoint added)? |
| Wave 1.0 → Wave 1.1 | architect | All baseline assumptions re-verified? Heuristic A protocol intact at four-or-five-agent scope? ADR-036 Proposed committed with 11-row mapping table populated COMPLETE? |
| Wave 1.1 → Wave 2 | senior-backend-engineer | spoofing edits + Cat N+1/N+2 + Disambiguation byte-identity-clean? |
| Wave 2.1 → Wave 2.2 | senior-backend-engineer | T-NN-1 (Cat 11) self-reviewed and clean? Rollback unused? |
| Wave 2.2 → Wave 2.3 | senior-backend-engineer | T-NN-2 (Cat 12) self-reviewed and clean? F-1 disjoint-tells annotation present? |
| Wave 2.3 → Wave 3 | senior-backend-engineer | T-NN-3 (Cat 13) self-reviewed and clean? tampering ≤120 lines verified? |
| Wave 3.1 → Wave 3.2 | senior-backend-engineer + team-lead MEDIUM-2 | M5-1 (Cat N+1) self-reviewed and clean? |
| Wave 3.2 → Wave 3.3 | senior-backend-engineer + team-lead MEDIUM-2 | M6-1 (Cat N+2) self-reviewed and clean? |
| Wave 3.3 → Wave 3.4 | senior-backend-engineer + team-lead MEDIUM-2 | M9-1 (Cat N+3) self-reviewed and clean? |
| Wave 3.4 → Wave 4.0 | senior-backend-engineer + team-lead MEDIUM-2 | M10-1 (Cat N+4) self-reviewed and clean? info-disclosure ≤120 lines verified? |
| Wave 4.0 → Wave 4.0b | architect | privilege-escalation M8 privilege-gain variant byte-identity-clean? |
| Wave 4.0b → Wave 4.1/4.2 | architect | repudiation M8 accountability-loss variant byte-identity-clean? Disjoint-tells with privilege-escalation Cat verified at T051? |
| Wave 4.2 → Wave 5.0 | senior-backend-engineer + tester | mobile-banking-app regen yields ≥10/≥11 new Mobile findings? Tester engaged for spot-check? |
| Wave 4.1 → Wave 5.0 | tester | Spot-check on 2 baselines green? |
| Wave 5.0 → Wave 5.2 | tester (parallel architect on Wave 5.1) | Full 6-baseline 6/6? ADR-036 Accepted committed (parallel)? |
| Wave 5.2 → Wave 5.3 | senior-backend-engineer + code-reviewer | All tests + code-review pass green? |
| Wave 5.3 → Wave 5.4 | senior-backend-engineer | Coverage Matrix ten-row transition committed (single commit)? |
| Wave 5.4 → Wave 5.5 | PM + Architect + Team-Lead | Triple sign-off recorded on tasks.md frontmatter? |
| Wave 5.5 → Wave 5.6 (reserve) | senior-backend-engineer + architect | Pre-merge title verified + post-merge release-please fired + retrospective filed + ADR-036 SHA filled? |

---

## 4. Time Estimates per Wave (3.0-Day Envelope)

| Wave | Duration | Calendar Slot | Cumulative |
|------|----------|---------------|------------|
| Phase 1 verification | 15 min | PRD-day Tue PM | 15 min |
| Wave 0.0 | 2-3 hours | PRD-day Tue PM | ~3 hours |
| Wave 0.1 | 4-5 hours | Plan-day Wed AM-early | ~8 hours |
| Wave 1.0 | ~2 hours | Plan-day Wed AM-mid | ~10 hours |
| Wave 1.1 | ~3 hours | Plan-day Wed AM-late | ~13 hours (Day 1 AM done) |
| Wave 2.0/2.1/2.2/2.3 | ~5 hours | Plan-day Wed PM | Day 1 PM 5 hours (Day 1 done) |
| Wave 3.0/3.1/3.2/3.3/3.4 | ~5-6 hours | Build Day 2 AM Thu | Day 2 AM 5-6 hours |
| Wave 4.0/4.0b | ~3 hours | Build Day 2 PM Thu | Day 2 PM 3 hours |
| Wave 4-end verification | ~30 min | Build Day 2 PM Thu | Day 2 PM 3.5 hours |
| Wave 4.1 (parallel) | ~1 hour | Build Day 2 PM Thu | (parallel; weak overlap with 4.2) |
| Wave 4.2 | ~2 hours | Build Day 2 PM Thu | Day 2 PM 5.5 hours (Day 2 done) |
| Wave 5.0 | ~2 hours | Build Day 3 AM Fri | Day 3 AM 2 hours |
| Wave 5.1 (parallel) | ~30 min | Build Day 3 AM Fri | (parallel with 5.0) |
| Wave 5.2 | ~2 hours | Build Day 3 AM Fri | Day 3 AM 4 hours |
| Wave 5.3 | ~30 min | Build Day 3 PM Fri | Day 3 PM 30 min |
| Wave 5.4 | ~30 min | Build Day 3 PM Fri | Day 3 PM 60 min (Day 3 done) |
| Wave 5.5 | ~3 hours | Close-Out Day Mon | Mon ~3 hours (close-out done) |
| Wave 5.6 reserve | 1-2 hours | Reserve Day Tue | Reserved (conditional) |

**Total billable**: ~26-29 hours core + Wave 0.0 PRD-day evening prep (~3 hours) + reserve (~2 hours) = ~31-34 hours across 3.0 days. Proportional to F-6 (~24-29 hours / 2.5 days) at +0.5-day envelope vs F-6 reflecting four-or-five-agent enrichment scope.

---

## 5. Critical Path Summary

```
T009 (mobile-banking-app skeleton, PRD-day evening Tue)
  → T010 (full draft, plan-day AM-early)
  → T012 (architect re-verification, plan-day AM-mid)
  → T013 (ADR-036 Proposed, plan-day AM-mid)
  → T014-T020 (spoofing enrichment, plan-day AM-late, sequential within file)
  → T023-T028 (tampering enrichment, plan-day PM, T-NN-1/2/3 sequential checkpoints)
  → T032-T038 (info-disclosure enrichment, Build Day 2 AM, M5-1/M6-1/M9-1/M10-1 sequential checkpoints)
  → T043-T050 (M8 dual-host enrichment, Build Day 2 PM, PART A → PART B sequential)
  → T051 (architect integration walkthrough, Build Day 2 PM)
  → T061-T065 (mobile-banking-app regen, Build Day 2 PM)
  → T066 (tester full 6-baseline verification, Build Day 3 AM-1)
  → T067 (architect ADR-036 Accepted, Build Day 3 AM-2, strong parallel)
  → T072 (Coverage Matrix ten-row update, Build Day 3 PM)
  → T073-T076 (triple sign-off + close-out + release-please verification, Mon close-out)
  → T077 (delivery retrospective, Mon close-out, FR-26 / SC-26)
  → T078 (post-merge ADR-036 SHA fill, Mon close-out)
```

**Critical path nodes** = T009 → T010 → T012 → T013 → T014-T020 → T023-T028 → T032-T038 → T043-T050 → T061-T065 → T066 → T067 → T072 → T073-T076 → T077 (14 nodes / ~26-29 critical hours).

---

## 6. Resource Allocation Summary

| Agent | Tasks | Critical-Path Touchpoints | Workload |
|-------|-------|---------------------------|----------|
| senior-backend-engineer | 56 (T010 co, T011, T014-T050 ex T019/T020/T026-T028 sequential, T052-T053, T061-T065, T069, T072, T074-T076, T079-T081) | T010 co, T014-T020, T023-T050, T061-T065, T072, T074-T076 | Primary executor, ~70% load |
| architect | 9 (T005, T009, T010 lead, T012, T013, T051, T067, T077, T078) | T009, T010, T012, T013, T051, T067, T077, T078 | Architecture + ADR + walkthrough + retrospective + SHA fill, ~25% load |
| tester | 16 (T001-T004, T006-T008, T054-T058, T059-T060, T066, T068, T070) | T066, T068, T070 | Verification + test authoring + early-signal, ~25% load |
| code-reviewer | 1 (T071) | T071 | Single review pass at Wave 5.2 |
| product-manager | 1 (T073) | T073 | Sign-off only |
| team-lead | 2 (T073, T082 conditional) | T073 | Sign-off + R5/R6 reserve escalation |

**No agent exceeds 80% loading** per team-lead acceptance criterion. Critical path runs on senior-backend-engineer (primary) + architect (gates + ADR + walkthroughs + retrospective) with tester (verification gates + early-signal + new test file) and code-reviewer (single review pass at Wave 5.2).

---

## 7. Subagent Return Policy Reminder

When invoked as a subagent (via Agent tool), each agent returns ONLY:
1. **Status** (APPROVED / CHANGES_REQUESTED / BLOCKED / pass / fail)
2. **Item count** (if applicable)
3. **File path** to `.aod/results/{agent-name}.md` with full details

- Write detailed findings to `.aod/results/{agent-name}.md` BEFORE returning
- Max return: 15 lines / ~200 tokens
- NEVER return code snippets, file contents, or multi-paragraph explanations
- Policy applies to subagent→main returns only, not user-facing output

---

## Appendix: Owner Annotation Source

All owner assignments derived from explicit task annotations in tasks.md (e.g., "Architect drafts", "Architect re-verifies", "Tester (per FR-15)", "TEAM-LEAD MEDIUM-2 SUB-CHECKPOINT", "Architect integration walkthrough") cross-referenced against the Agent Registry at `.claude/agents/_README.md`. Sign-off authority follows triad governance matrix (PM + Architect + Team-Lead on tasks.md). F-6 (Feature 232) agent-assignments.md served as direct precedent at three-agent scope; F-7 extends pattern to four-or-five-agent scope (dual-host M8 default) with proportional +0.5-day envelope expansion.

**End of Agent Assignments**
