---
spec_reference: specs/296-50-50-owasp-coverage-distribution-launch/spec.md
plan_reference: specs/296-50-50-owasp-coverage-distribution-launch/plan.md
tasks_reference: specs/296-50-50-owasp-coverage-distribution-launch/tasks.md
prd_reference: docs/product/02_PRD/296-50-50-owasp-coverage-distribution-launch-2026-05-28.md
author: team-lead
date: 2026-05-28
---

# Agent Assignments: F-1 — 50/50 OWASP Coverage Distribution Launch (BLP-04 Wave 1)

**Branch**: `296-50-50-owasp-coverage-distribution-launch`
**Target window**: 5 working days (2026-05-28 → 2026-06-04 target; hard ceiling 2026-06-11 per NFR-007)
**Wall-clock effort**: ~16-21 focused hours
**Total tasks**: 37 across 11 phases

---

## Solo-Maintainer Constraint (NFR-006)

**F-1 is exclusively writing-bound.** Per NFR-006 writing-voice / code-voice separation, F-1 must NOT invoke any code-implementation agent. The valid agent set for F-1 is:

| Agent | Use | Tasks |
|---|---|---|
| **maintainer** | Primary owner of every task | All 37 tasks |
| **product-manager** (optional pair) | Second-pair-of-eyes on FR-008 narrative-defensibility pre-check (framework citation accuracy + URL validity check) | T011 (pair only) |
| **architect** (escalation only) | Sign-off if FR-011 README ≤30-line diff cap is exceeded; sign-off if OWASP_COVERAGE.md ≤80-line cap is exceeded | T009 escalation, T007 escalation (not expected) |

**Explicitly NOT invoked** (per NFR-006 writing-voice / code-voice separation):
- senior-backend-engineer (no source code change)
- frontend-developer (no UI)
- devops (no deployment — `/security` post-merge regression scan is a verification, not a deployment)
- tester (no automated tests per Tests-NOT-REQUESTED + Principle VII §Exceptions)
- code-reviewer (no code review surface)
- security-analyst (post-merge `/security` regression-only scan is self-run by maintainer per T030)

**[MANUAL-ONLY] tasks** (14 of 37, ~38%) require human-in-the-loop interaction with external systems (github.com rendering, LinkedIn UI, external repo PRs, Discussions UI, Issue close).

---

## Wave 0: Setup + Canonical Anchor (Day 1 AM-PM)

**Goal**: Verify branch/PR state + author `docs/standards/OWASP_COVERAGE.md` (≤80 lines) as the canonical anchor for all downstream Wave 1+ work.

**Critical path**: T001 → T005 → T006 + T007 (parallel after T005). **Wave 1+ work is BLOCKED until T005 + T006 complete.**

| Task | Owner | [P]? | Wall-clock | Notes |
|---|---|---|---|---|
| T001 | maintainer | — | 5 min | `pwd && git branch --show-current` + sign-off frontmatter check |
| T002 | maintainer | [P] | 5 min | `gh pr view 297` — confirm draft + `docs(296):` title |
| T003 | maintainer | [P] | 5 min | `awk 'NR>=1 && NR<=20 {print NR": "$0}' README.md` — line 14 + line 17 still correct |
| T004 | maintainer | [P] | 5 min | `grep -c "^- id:" schemas/taxonomy/owasp.yaml` = 60 |
| T005 | maintainer | — | 2-3h | **CRITICAL PATH** — Author OWASP_COVERAGE.md ≤80 lines per plan.md §Wave 0 template (7 sections: Headline / Matrix / Reproducibility / Anti-claims / See also). Compose from schemas/taxonomy/owasp.yaml + ADR-024→ADR-037 + ADR-045 lineage. Both baseline layouts documented (nested + top-level per Architect M-1). Per-bucket separate URLs (Web 2021 + API 2023 per Architect L3). |
| T006 | maintainer | [P] | 10 min | Append index row to `docs/standards/README.md` |
| T007 | maintainer | [P] | 5 min | `wc -l docs/standards/OWASP_COVERAGE.md` ≤80 |

**Wave 0 wall-clock total**: ~3-4 hours (Day 1 AM-PM).
**Buffer absorption**: minimal slack — Wave 0 is the foundation, must complete Day 1.

---

## Wave 1: README Hero + FR-008 Pre-Check + Discussion #179 Draft (Day 1 PM)

**Goal**: Land README hero block (≤30-line diff) + FR-008 narrative-defensibility pre-check evidence + DRAFT Discussion #179 closing comment for 4-day incubation.

**Critical path**: T008 → T009 + T010 + T011 + T012 (parallel after T008). T022 (draft) parallel anytime after T005.

| Task | Owner | [P]? | Wall-clock | Notes |
|---|---|---|---|---|
| T008 [US1] | maintainer | — | 30 min | Insert README hero block between line 14 + line 17 per plan.md §Wave 1 template (~22 lines targeting ≤30-line diff cap). Preserve poster reference line 7 (US1 AC-5). |
| T009 [US1] | maintainer | [P] | 5 min | `git diff main -- README.md | grep -E "^[+-]" | wc -l` ≤30 (SC-011) |
| T010 [US1] | maintainer | [P] [MANUAL-ONLY] | 15 min | Push branch + render README hero on github.com PR #297 file preview. Verify `\*` footnote-marker renders correctly. Architect L-1 render-check. |
| T011 [US1] | maintainer (optionally paired with product-manager) | [P] | 30-60 min | Author FR-008 pre-check evidence in `notes/narrative-defensibility-check.md`. Verify (a) OWASP_COVERAGE.md exists; (b) schemas/taxonomy/owasp.yaml 60 records; (c) per-baseline Coverage Attestation byte-deterministic reproduction on ≥1 example; (d) 6 OWASP framework canonical URLs all 200 OK. **CRITICAL**: first-commit timestamp MUST predate LinkedIn URL + Cybersec article merge timestamps (SC-009). |
| T012 [US1] | maintainer | [P] | 15 min | Verify hero block rendering on github.com — 5 framework rows visible first viewport + all 5 anchor links 200 OK + Web/API combined-slot footnote text correct + OWASP_COVERAGE.md link resolves. |
| T022 [US5] | maintainer | [P] [MANUAL-ONLY] | 30-60 min | **Team-Lead L-3 mitigation** — draft Discussion #179 closing comment in `notes/discussion-179-draft.md` on **Day 1 PM** for 4-day incubation period. @armorer-labs gap-analysis attribution (NOT "requester"/"discussion-opener"). Lead sentence verbatim per spec US5 AC-3. F-260 community-merge precedent cited. |

**Wave 1 wall-clock total**: ~2-3 hours (Day 1 PM, parallel with Wave 0 tail).
**Day 1 cumulative**: ~5-7 hours focused — heaviest day given Wave 0 + Wave 1 + Discussion draft all land.

---

## Wave 2: Cybersec Article (Day 2-3 — longest single task)

**Goal**: Draft ~3000-word article (§a–§f) → NFR-008 self-review → PR open → ≥24h hold → self-merge.

**Critical path**: T013 → T014 → T015 → ≥24h hold → T016. **T013-T016 is the longest single chain.**

| Task | Owner | [P]? | Wall-clock | Notes |
|---|---|---|---|---|
| T013 [US3, folds US8] | maintainer | — | 4-6h | **LONGEST SINGLE TASK** — Cybersec article body draft (target ~3000 words ±20% = 2400–3600) per plan.md §Wave 2 (§a~400w + §b~700w + §c~300w + §d~700w + §e~100w + §f~150w). §b: 2–4 examples slot-bridging trade-off documented (Architect M-2 wide bound). §b: baseline layout note (Architect M-1). §d: ADR/agent enumeration preferred over per-catalog-ID (Architect L-2 word-budget discipline). §f: prospective contributor invitation (US-8 / PM L-1) — names Discussions + Issues + F-260/F-292 community-merge precedent + comment-first-give-choice path A default. |
| T014 [US3] | maintainer | — | 1-2h | NFR-008 self-review checklist (6 items: framework citation accuracy / coverage matrix accuracy / verification walkthrough reproducibility / link validity / word count / **asset-tag mention NOT present per Team-Lead L-2**). Fix any failures before T015. |
| T015 [US3] | maintainer | [MANUAL-ONLY] | 15 min | Open PR against `davidmatousek/Cybersecurity-Content`. Title `feat: 50/50 OWASP coverage in tachi — what it means and how to verify it`. Record PR URL in `notes/cybersec-article-pr-url.txt`. **Hold ≥24 hours before self-merge.** |
| T016 [US3] | maintainer | [MANUAL-ONLY] | 15 min | After ≥24h hold, fresh-eyes re-read + NFR-008 checklist re-run + self-merge. Update URL file with merged-state URL. |

**Wave 2 wall-clock total**: ~6-9 hours focused + 24h elapsed hold (Day 2-3 + Day 3-4).
**Team-Lead L-1 compression carve-out**: if T013 consumes full Day 2, T014 slips to Day 3 AM, T015 to Day 3 PM, T016 to Day 4 PM. Slip absorbed within target window.

---

## Wave 3: Profile Refresh + LinkedIn Draft (Day 3 AM-PM, parallel with Wave 2 24h hold)

**Goal**: Profile PR open + LinkedIn post drafted. LinkedIn publish is BLOCKED until Wave 2 article merges (T016).

**Critical path**: T020 + T017 parallel; T020 → ≥24h hold → T021; T017 → T018 (BLOCKED by T016).

| Task | Owner | [P]? | Wall-clock | Notes |
|---|---|---|---|---|
| T017 [US2] | maintainer | [P] | 45 min | Draft LinkedIn post ~250 words per plan.md §Wave 3 template. Required: Daniel Wood 2026-05-02 thread reference + 50/50 statement + CTA links. Native-content-first algorithmic discipline. Tone discipline: name the gap (Daniel's feedback) / name the fix (six BLP-02 features) / ship the receipts (PR #293). NO sycophancy. |
| T020 [US4] | maintainer | [P] [MANUAL-ONLY] | 1h | Open PR against `davidmatousek/davidmatousek` updating profile README per plan.md §Wave 3 template. Tachi flagship surface with 50/50 tagline; AOD-Kit secondary. Minimal scope per Q7 lean (no "Now" section). Footer wording at author discretion within ADR-044 dual-frame alignment (Architect L-3). Record PR URL. **Hold ≥24 hours before self-merge.** |

**Wave 3 wall-clock total** (draft phase): ~1.75 hours.

---

## In-Tree Merge Gate (Day 2 AM earliest / Day 3 AM realistic)

**Goal**: Squash-merge PR #297 with `docs(296):` prefix. Release-please correctly skips per `docs:` mapping (EXPECTED; Architect M3). F-212 marker-commit recovery flow NOT invoked.

**Sequencing**: T029 fires after Wave 0 + Wave 1 + Wave 5 in-tree work is committed/pushed. T030 + T032 fire parallel after T029.

| Task | Owner | [P]? | Wall-clock | Notes |
|---|---|---|---|---|
| T026 | maintainer | [P] | 30 min | CHANGELOG `Unreleased` subsection `### OWASP Coverage Matrix Documentation (F-296)` (~10 lines, `docs:` NOT `feat:`). Cross-link BLP-04 strategy doc by file path. (FR-006 + SC-006.) |
| T027 | maintainer | [P] | 1.5-2h | Author `docs/product/_internal/strategy/BLP-04-adoption-push.md` (~150 lines, gitignored). 7 sections per plan.md §Wave 5.1: §1 4-feature sequencing rationale; §2 BLP-03 trigger mechanics + enterprise-buyer signal acceptance (US7); §3 Sequencing Discipline narrative; **§4 F-2 kickoff target dates (Fri 2026-06-05 AM earliest / Mon 2026-06-08 AM latest; ship deadline 2026-06-11 per Architect M2 + Team-Lead M-3)**; §5 F-2 no-pre-draft binding (Team-Lead M-1); §6 Release-cadence carve-out (NFR-005(d) memory anchor); §7 References. (FR-012 + SC-014.) |
| T028 | maintainer | [P] | 20 min | Update `feedback_aod_deliver_release_gate.md` memory carve-out per plan.md §Wave 5.2. (FR-013 + SC-013 + NFR-005(d).) |
| **T029** | maintainer | — | 10 min | **IN-TREE SQUASH-MERGE GATE** — `gh pr ready 297` + self-squash-merge with title `docs(296): F-1 50/50 OWASP coverage distribution launch (BLP-04 Wave 1)`. **Verify release-please does NOT open a release PR (EXPECTED per Architect M3 / NFR-005).** Do NOT invoke F-212 recovery flow. |
| T030 | maintainer | [P] | 30 min | Post-merge `/security` regression-only re-scan from `main`. Confirm zero new findings (NFR-004). Capture in `notes/post-merge-security-scan.md`. |

**Merge gate wall-clock total**: ~3-4 hours focused (Day 2-3 — Wave 0 + Wave 1 + Wave 5 in-tree authored prior).

---

## Wave 4: Out-of-Tree Publications (Day 4-5)

**Goal**: LinkedIn publish (AFTER article merge per Q2 lean) + profile self-merge (after ≥24h hold) + Discussion #179 publish + close.

**Critical path**: T016 article merge → T018 LinkedIn publish; T020 → ≥24h hold → T021 profile self-merge; T022 draft (Day 1 PM) → 4-day incubation → T023 publish (Day 5 AM) → T024 close.

| Task | Owner | [P]? | Wall-clock | Notes |
|---|---|---|---|---|
| T018 [US2] | maintainer | [MANUAL-ONLY] | 15 min | **BLOCKED by T016 Cybersec article merge per Q2 lean.** Publish LinkedIn post from T017 draft. Capture URL in `notes/linkedin-post-url.txt`. Verify article URL in post body resolves 200 OK at publication. Day 4 AM target (or Day 5 AM if Wave 2 slipped). |
| T019 [US2] | maintainer | [P] [MANUAL-ONLY] | 5 min | Note format choice (native-content-first; article URL location) + publication time window. Reach metrics deferred to F-3. |
| T021 [US4] | maintainer | [MANUAL-ONLY] | 15 min | After ≥24h hold + before/after rendering review on github.com (R4 mitigation), self-merge profile refresh PR. Update URL file with merged-state URL. Day 4 PM target. |
| T023 [US5] | maintainer | [MANUAL-ONLY] | 15 min | Publish T022 draft to Discussion #179 via Discussions UI (or `gh discussion comment 179 --body-file ...`). Verify @armorer-labs notification. Day 5 AM target (≤2026-06-04 per FR-005 7-day SLA + SC-005). |
| T024 [US5] | maintainer | [MANUAL-ONLY] | 5 min | `gh discussion close 179 --reason resolved`. Mark "shipped" / "resolved". Record discussion URL with closing-comment anchor in `notes/discussion-179-close-url.txt`. |
| T025 [US6] | maintainer | [P] [MANUAL-ONLY] | continuous | **F-2 sequencing hold throughout F-1 window.** Abstain from F-2 / F-260b / asset-tag commands. Halt + revert if scope-creep detected. |

**Wave 4 wall-clock total**: ~1 hour focused (~Day 4-5).

---

## Wave 5: Close-Out (Day 5 PM)

**Goal**: All verifications + Issue #296 close with 5 artifact URLs + PR #297 ready-for-review confirmed.

**Critical path**: T031 + T032 + T033 + T035 + T036 parallel; T034 fires after all 5 artifact URLs captured.

| Task | Owner | [P]? | Wall-clock | Notes |
|---|---|---|---|---|
| T031 | maintainer | — | 15 min | **My Team-Lead M-1 propagation** — SC-007 binary check `git log --all --grep="F-2\|F-260b\|asset-tag wiring" --since="2026-05-28"`. Run TWICE (once before close, once at close). Apply Architect L1 false-positive carve-out. Halt + revert if non-zero substantive commits. |
| T032 | maintainer | [P] | 15 min | SC-010 file-allowlist verification: `git diff main --name-only` against PR #297. Confirm zero files outside allowed set. (BLP-04 strategy doc is gitignored, not in diff — verify exists locally per T027.) |
| T033 | maintainer | [P] | 15 min | SC-014 5-item BLP-04 strategy doc verification (PM L-1 fold-in): inspect doc sections §1-§5 + cross-link present in close-out commit + Issue #296 closing comment. |
| T034 | maintainer | [MANUAL-ONLY] | 30 min | Compose Issue #296 closing comment per plan.md §Wave 5.3. Required: 5 artifact URLs (T012 README PR #297 + T018 LinkedIn + T016 Cybersec article + T021 profile PR + T024 Discussion #179 close) + BLP-04 strategy doc cross-link (file path) + FR-008 pre-check evidence path + SC-007 verification + release-cadence note + memory carve-out reference. Post comment + `gh issue close 296`. |
| T035 | maintainer | [P] | 15 min | PM L-1 cadence elasticity + Discussion incubation deferral notes if applicable. File follow-up Issue if any out-of-tree task deferred past 2026-06-11 hard ceiling (F-292 precedent). |
| T036 | maintainer | [P] | 30 min | PM L-2 FR-009 follow-up Issue preemptive template in `notes/material-critique-followup-issue-template.md`. |
| T037 | maintainer | [MANUAL-ONLY] | 5 min (if fired) | **My Team-Lead M-1 + M-3 propagation** — if F-2 slips past 2026-06-11, edit Issue #296 closing comment (post-close edit allowed) + update memory carve-out (T028 output) with new restoration date. Fires only if F-2 slips. |

**Wave 5 wall-clock total**: ~2 hours focused (Day 5 PM).

---

## Per-Wave Wall-Clock Summary

| Wave | Day | Focused Hours | Cumulative |
|---|---|---|---|
| Wave 0 (Setup + Anchor) | Day 1 AM-PM | ~3-4h | 3-4h |
| Wave 1 (README hero + FR-008 + Discussion draft) | Day 1 PM | ~2-3h | 5-7h |
| Wave 2 drafting (Cybersec article) | Day 2 | ~4-6h | 9-13h |
| Wave 2 review + PR open | Day 2 PM or Day 3 AM | ~1-2h | 10-15h |
| Wave 2 24h hold (elapsed) | Day 3 AM-PM | 0h focused | 10-15h |
| Wave 2 self-merge | Day 3 PM or Day 4 AM | ~15 min | 10-15h |
| Wave 3 (LinkedIn + profile drafts) | Day 3 AM | ~1.75h | 12-17h |
| Wave 3 profile self-merge | Day 4 PM | ~15 min | 12-17h |
| In-tree merge gate (T026-T030) | Day 2-3 | ~3-4h | 15-21h |
| Wave 4 publications (LinkedIn + Discussion) | Day 4-5 | ~45 min | 16-22h |
| Wave 5 close-out (T031-T036) | Day 5 PM | ~2h | 18-24h |
| **TOTAL** | **5 working days** | **~16-21h focused** | — |

**Buffer absorption**:
- Buffer-1 (Fri 2026-06-05): absorbs Cybersec article 2-3 revisions (PRD R3) or LinkedIn slip.
- Buffer-2 (Mon 2026-06-08): absorbs Discussion close slip OR profile refresh slip OR multi-day cascade.
- Hard ceiling (2026-06-11 per NFR-007): absorbs catastrophic worst-case + F-2 ship-by Architect M2 ceiling.

---

## Critical-Path Visualization

```
Day 1 AM    : T001 → T002+T003+T004 [P]
Day 1 PM    : T005 (Wave 0 CRITICAL) → T006+T007 [P]
              T008 → T009+T010+T011+T012 [P] (Wave 1)
              T022 draft [P] (Discussion #179 incubation start; Team-Lead L-3)

Day 2 AM    : (T026 CHANGELOG + T027 BLP-04 strategy + T028 memory carve-out [P, in-tree])
              T029 in-tree merge gate (EXPECTED release-please skip per Architect M3)
              T030 post-merge /security regression [P]
Day 2 PM    : T013 Cybersec article drafting STARTS (LONGEST SINGLE TASK)

Day 3 AM    : T013 continues OR T014 NFR-008 self-review
              T017 LinkedIn draft + T020 profile PR open [P]
Day 3 PM    : T015 Cybersec PR open + ≥24h hold STARTS

Day 4 AM    : T016 Cybersec self-merge (after ≥24h hold)
              T018 LinkedIn publish (BLOCKED by T016 per Q2 lean)
              T019 [P]
Day 4 PM    : T021 profile self-merge (after ≥24h hold)

Day 5 AM    : T023 Discussion #179 publish (≤2026-06-04 per FR-005 SLA)
              T024 Discussion close
Day 5 PM    : T031+T032+T033+T035+T036 close-out verifications [P]
              T034 Issue #296 close with 5 URLs
              T037 fires only if F-2 slips post-2026-06-11
```

**Critical path** (sequential, no parallelization): T001 → T005 → T008 → T029 → T013 → T015 → ≥24h → T016 → T018 → T023 → T034.

**Longest single task**: T013 (Cybersec article ~3000 words, 4-6h focused).

---

## Buffer / Slack Allocation

| Buffer | Date | Purpose |
|---|---|---|
| Working window | 2026-05-28 (Thu) → 2026-06-04 (Thu) | 5 working days target |
| Buffer-1 | 2026-06-05 (Fri) | Absorbs Cybersec article revisions, LinkedIn slip, Discussion close slip |
| Weekend | 2026-06-06 (Sat) → 2026-06-07 (Sun) | No working hours scheduled |
| Buffer-2 | 2026-06-08 (Mon) | Absorbs multi-day cascade; LATEST F-2 kickoff date per Team-Lead M-3 |
| Buffer-3 | 2026-06-09 (Tue) → 2026-06-10 (Wed) | Final slack |
| **Hard ceiling** | 2026-06-11 (Thu) | NFR-007 + Architect M2 F-2 ship deadline; F-1 close-out comment edit allowed post-close if F-2 slips (T037) |

---

## Risk-Fired Branches: Scope Reduction Order

If NFR-007 (2026-06-11 hard ceiling) approaches and wave-by-wave slip cascades, scope reduces in this order (per tasks.md §Implementation Strategy lines 269-273):

| Priority | Action | Trigger | Backstop |
|---|---|---|---|
| 1 (drop LAST) | **Drop Discussion #179 close to follow-up Issue** | Buffer-2 (2026-06-08) consumed | PRD R3 mitigation; @armorer-labs notified in follow-up |
| 2 (drop SECOND) | **Drop profile refresh to follow-up Issue** | Buffer-1 + Buffer-2 consumed | Profile refresh is secondary distribution surface |
| 3 (drop FIRST) | **Drop LinkedIn post** | Buffer-1 consumed AND Daniel Wood thread staleness acceptable | Lowest reach surface per 2026 algorithm research; BUT time-sensitive given Daniel Wood thread is 2026-05-02 |
| **NEVER drop** | **README hero (T008) + OWASP_COVERAGE.md (T005) + Cybersec article (T013-T016)** | — | MVP-1 P1 in-tree-only backstop ensures F-1 always delivers adopter-facing value |

**MVP-1 P1 backstop scope** (if all out-of-tree slips):
- T001-T012 (Phase 1 + Phase 2 + Phase 3) + T026 CHANGELOG + T029 in-tree merge gate + T030-T033 verifications + T034 Issue close.
- Total: ~18 tasks, ~6-8h focused, fits Day 1-2 alone.

**This backstop guarantees the README hero + canonical anchor + CHANGELOG always ship, even if Cybersec article + LinkedIn + profile + Discussion all slip to follow-up Issues.**

---

## Worst-Case Absorption Scenarios

### Scenario A: Cybersec article requires 2-3 revisions (PRD R3 fires)

- Base T013-T014 = 6-8h; revised 10-14h.
- Wave 2 slips Day 2-3 → Day 3-4.
- LinkedIn publish (T018) slips Day 4 AM → Day 5 AM.
- Discussion publish (T023) slips Day 5 AM → Day 5 PM or Buffer-1 AM.
- **Buffer-1 (Fri 2026-06-05) absorbs cleanly.**
- F-2 kickoff target preserved (earliest Buffer-1 AM if F-1 closes 2026-06-04 PM; latest Buffer-2 AM Mon 2026-06-08).

### Scenario B: Material critique on LinkedIn (FR-009 fires)

- T036 preemptive follow-up Issue template ready.
- NFR-003 in-thread response within ~24-72h.
- Buffer-1 + Buffer-2 absorb response cycle.
- No F-1 scope reduction required.

### Scenario C: F-2 slips past 2026-06-11 hard ceiling

- T037 explicitly handles: edit Issue #296 closing comment post-close + update memory carve-out with new restoration date.
- F-1 itself remains closed; only the BLP-04 sequencing-restoration date shifts.
- This is a Wave 5+1 follow-up action, not blocking for F-1 close.

### Scenario D: NFR-007 hard-ceiling escalation triggers scope reduction

- Scope reduction order documented above.
- MVP-1 P1 in-tree-only backstop always preserved.
- README hero + OWASP_COVERAGE.md + CHANGELOG never drop.

---

## Agent-Assignment Summary

| Agent | Tasks | Count | Notes |
|---|---|---|---|
| maintainer (solo) | T001-T037 | 37 | All tasks |
| maintainer + product-manager (optional pair) | T011 | 1 | FR-008 pre-check second-pair-of-eyes optional |
| architect (escalation only) | T009 escalation, T007 escalation | 0-2 | Fires only if FR-011 ≤30-line cap OR Architect H2 ≤80-line cap exceeded — NOT expected per plan.md design |
| **NOT INVOKED** (per NFR-006) | — | 0 | senior-backend-engineer, frontend-developer, devops, tester, code-reviewer, security-analyst |

**Wall-clock distribution**: solo maintainer with optional product-manager pair on T011 (~30-60 min); no code-implementation agent involvement preserves NFR-006 writing-voice / code-voice separation discipline.

---

**End of agent-assignments.md.** Triad triple sign-off complete: PM APPROVED + Architect APPROVED + Team-Lead APPROVED_WITH_CONCERNS (3 LOW polish concerns flagged for build-time discretion). Ready for /aod.build.
