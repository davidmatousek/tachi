# Agent Assignments — F-2 Source-Pattern Hardening (BLP-02 Wave 2)

**Feature**: F-2 / 256-source-pattern-hardening
**Generated**: 2026-05-04
**Author**: team-lead
**Cadence**: single-agent-interleaved (per PRD §Resource Assignment)

---

## 1. Overview

| Field | Value |
|-------|-------|
| Feature | F-2 Source-Pattern Hardening (BLP-02 Wave 2) |
| Total Tasks | **62** (T001–T062) |
| Phases | 11 (Setup → Foundational → 5 streams → Polish → Post-Merge) |
| Implementation Streams | 5 (Library bring-up, Site refactors, ADR-040, Clone timeout, Test corpus) |
| Wave Count | **7** (Wave 1–6 active; Wave 7 [MANUAL] post-merge) |
| Active Effort | 8.75d single-agent-interleaved (per PRD §Timeline) |
| Hard Ceiling | **9.5d active / 11d wall-clock** (15.8% buffer headroom; floor preserved) |
| Cadence | Single-agent-interleaved (senior-backend-engineer drives implementation; reviewers gate) |
| Triad Sign-off | PM **APPROVED** / Architect **APPROVED** / Team-Lead **APPROVED_WITH_CONCERNS** (2026-05-04) |
| MVP Contingency | Q-1 split → MVP = Phases 1-5 + 9; F-2b recovery = Phases 6-8 (3-4d) |

---

## 2. Agent Roster Validation

All assigned agents below are valid `subagent_type` names from `.claude/agents/_README.md` (12-agent roster, excluding `orchestrator` and `debugger` which are coordination/diagnostic roles not assigned to implementation tasks here).

| Agent | Valid? | Used in F-2? | Role in F-2 |
|-------|--------|--------------|-------------|
| `senior-backend-engineer` | ✓ | **Yes (primary)** | All implementation, ADR markdown authoring, fixture authoring, test files |
| `architect` | ✓ | Yes (gating) | Day-5 + Day-8 architectural-condition checkpoints |
| `tester` | ✓ | Yes (advisory) | Day-4 informal fixture-design review |
| `security-analyst` | ✓ | Yes (post-merge) | T061 [MANUAL] post-merge `/security` re-scan |
| `code-reviewer` | ✓ | Yes (continuous) | Large-PR review iteration (Day 6-9, ~700-1100 LOC) |
| `web-researcher` | ✓ | No | Not invoked (research already captured in research.md) |
| `frontend-developer` | ✓ | No | Not invoked (no UI changes) |
| `ux-ui-designer` | ✓ | No | Not invoked (no UI changes) |
| `devops` | ✓ | No | Not invoked (no deployment changes) |
| `product-manager` | ✓ | n/a | Sign-off complete (frontmatter); owns no implementation tasks |
| `architect` (signoff) | ✓ | n/a | Sign-off complete (frontmatter); owns gating tasks T044/T048 only |
| `team-lead` | ✓ | n/a | Sign-off complete (frontmatter); owns Day-5 escalation decision (T044 owner) |

**Mapping rule**: Per PRD §Resources, single-agent-interleaved cadence assigns implementation to `senior-backend-engineer`; reviewers (`architect` / `tester` / `security-analyst` / `code-reviewer`) gate at named checkpoints. `product-manager` and `team-lead` own governance sign-offs (already complete in tasks.md frontmatter), NOT implementation tasks.

---

## 3. Agent Assignment Matrix

Every task T001–T062 is mapped to a single primary agent. Reviewer engagement (code-reviewer iteration, tester pre-T044 review) happens out-of-band against the running PR — see §7 NOTES.

| Task ID | Phase | Primary Agent | Rationale |
|---------|-------|---------------|-----------|
| T001 | 1 Setup | `senior-backend-engineer` | Workspace + branch + draft PR verification |
| T002 | 1 Setup | `senior-backend-engineer` | mkdir fixtures/valid |
| T003 | 1 Setup | `senior-backend-engineer` | mkdir fixtures/adversarial |
| T004 | 1 Setup | `senior-backend-engineer` | NFR-002 dependency manifest baseline (SHA-256 snapshot) |
| T005 | 2 Foundational | `senior-backend-engineer` | Day-1 baseline benchmark (NFR-004 + SC-010) |
| T006 | 2 Foundational | `senior-backend-engineer` | stack-pack-defaults-schema.md contract finalization |
| T007 | 2 Foundational | `senior-backend-engineer` | config-load-helper-contract.md verification |
| T008 | 2 Foundational | `senior-backend-engineer` | CHANGELOG placeholder reservation |
| T009 | 3 US2/US5 Library tests | `senior-backend-engineer` | Test-1 authoring (27 cases, pytest+subprocess) |
| T010 | 3 US2/US5 Library impl | `senior-backend-engineer` | `aod_template_load_kv_file` library (7-step, bash 3.2) |
| T011 | 3 US2/US5 verify | `senior-backend-engineer` | macOS bash 3.2.57 verification (≥17/17 cases) |
| T012 | 3 US2/US5 verify | `senior-backend-engineer` | Linux bash 4+ verification |
| T013 | 3 US2/US5 perf | `senior-backend-engineer` | Day-1 post-impl benchmark (NFR-004 escalation rules) |
| T014 | 4 US1 Site A test | `senior-backend-engineer` | Test-4 init.sh end-to-end pytest |
| T015 | 4 US1 Site A impl | `senior-backend-engineer` | init.sh library source preamble |
| T016 | 4 US1 Site A impl | `senior-backend-engineer` | init.sh:106 source → library invocation |
| T017 | 4 US1 Site A impl | `senior-backend-engineer` | STACK_*-prefix migration in init.sh |
| T018 | 4 US1 Site A fixture | `senior-backend-engineer` | malicious-pack-defaults.env adversarial fixture |
| T019 | 4 US1 Site A verify | `senior-backend-engineer` | macOS + Linux pytest run |
| T020 | 5 US3 Site B test | `senior-backend-engineer` | Test-2 Site B parametrize cases |
| T021 | 5 US3 Site B test | `senior-backend-engineer` | Test-3 H-3 round-trip case |
| T022 | 5 US3 Site B impl | `senior-backend-engineer` | template-git.sh:561 reader refactor |
| T023 | 5 US3 Site B impl | `senior-backend-engineer` | template-git.sh:485-515 writer round-trip refactor |
| T024 | 5 US3 Site B verify | `senior-backend-engineer` | macOS + Linux pytest run |
| T025 | 6 US7 Site C test | `senior-backend-engineer` | Test-5 eval-removal lint test |
| T026 | 6 US7 Site C test | `senior-backend-engineer` | F-1 prompt-validator parametrize ($/\\/backtick) |
| T027 | 6 US7 Site C impl | `senior-backend-engineer` | template-substitute.sh:217 eval → ${!var_name:-} |
| T028 | 6 US7 Site C impl | `senior-backend-engineer` | template-substitute.sh:249 eval → printf -v |
| T029 | 6 US7 Site C impl | `senior-backend-engineer` | template-substitute.sh:536 eval → ${!var_name:-} |
| T030 | 6 US7 Site C impl | `senior-backend-engineer` | template-substitute.sh:558 eval → ${!var_name} (strict, no `:-`, H-4) |
| T031 | 6 US7 Site C impl | `senior-backend-engineer` | template-substitute.sh:566-571 writer escape pass REMOVAL |
| T032 | 6 US7 Site C impl | `senior-backend-engineer` | init-input.sh F-1 contract amendment ($/\\/backtick metachar reject) |
| T033 | 6 US7 Site C verify | `senior-backend-engineer` | macOS + Linux pytest + grep eval=0 assertion |
| T034 | 7 US8 Site D test | `senior-backend-engineer` | Test-2 Site D parametrize (TOCTOU + missing-path/file/key) |
| T035 | 7 US8 Site D impl | `senior-backend-engineer` | template-substitute.sh:162-209 47-line → 7-line library delegation |
| T036 | 7 US8 Site D verify | `senior-backend-engineer` | macOS + Linux pytest + F-1 regression suite |
| T037 | 8 US4 Stream 4 test | `senior-backend-engineer` | Test-3 6 clone-timeout cases |
| T038 | 8 US4 Stream 4 fixture | `senior-backend-engineer` | conftest.py session-scoped `hanging_upstream` fixture (per F-250 ADR-039) |
| T039 | 8 US4 Stream 4 impl | `senior-backend-engineer` | template-git.sh:102-104 clone watchdog (L-1 trap, AOD_FETCH_TIMEOUT, Q-3 footgun) |
| T040 | 8 US4 Stream 4 smoke | `senior-backend-engineer` | macOS bash 3.2.57 watchdog smoke (Day-5 GREEN-LIGHT condition 4) |
| T041 | 8 US4 Stream 4 verify | `senior-backend-engineer` | macOS + Linux pytest run |
| T042 | 9 US6 Stream 3 ADR | `senior-backend-engineer` | ADR-040 Proposed authoring (first commit, dual-commit per Q-6) |
| T043 | 9 US6 Stream 3 release | `senior-backend-engineer` | PR #257 title verification (Conventional-Commits) |
| **T044** | **10 Polish gate** | **`team-lead`** | **Day-5 slip-watch checkpoint — 4-condition GREEN-LIGHT verification + 3-tier escalation ladder. Team-Lead owns recovery-lever decision authority per plan §Critical Path. Architectural-condition verification (Condition 3 ADR-040 Proposed committed) MAY be delegated to `architect` advisory but the gate decision remains team-lead.** |
| T045 | 10 Polish | `senior-backend-engineer` | regenerate-config-load-baseline.sh authoring |
| T046 | 10 Polish | `senior-backend-engineer` | Run T045; commit fixtures |
| T047 | 10 Polish | `senior-backend-engineer` | B-3 cases 19-23 augmentation |
| **T048** | **10 Polish gate** | **`architect`** | **Day-8 secondary architectural checkpoint — verify Stream 1+2 sites + Stream 5 ≥80% coverage + ADR-040 Accepted-transitioning. Architect owns architectural-condition assessment; soak-day fallback decision per plan §Day-8 checkpoint.** |
| T049 | 10 Polish | `senior-backend-engineer` | Full test suite (5 files) on macOS + Linux CI |
| T050 | 10 Polish | `senior-backend-engineer` | NFR-002 dependency-diff verification |
| T051 | 10 Polish | `senior-backend-engineer` | NFR-005 finding.yaml schema-diff verification |
| T052 | 10 Polish | `senior-backend-engineer` | SC-005 grep eval=0 lint |
| T053 | 10 Polish | `senior-backend-engineer` | CHANGELOG.md v4.x finalization (BLP-02 F-2 entry + F-1 amendment migration) |
| T054 | 10 Polish | `senior-backend-engineer` | ADR-040 Proposed → Accepted (second commit, fold T013 benchmark numbers) |
| T055 | 10 Polish | `senior-backend-engineer` | SC-010 benchmark documentation completeness verification |
| T056 | 10 Polish | `senior-backend-engineer` | Final pre-merge verification (frontmatter + PR title + zero schema diff + 5 tests green) |
| **T057** | **11 Post-merge [MANUAL]** | **closing operator** | Pre-merge PR title re-verify (`/aod.deliver`) |
| **T058** | **11 Post-merge [MANUAL]** | **closing operator** | `gh pr merge 257 --squash` |
| **T059** | **11 Post-merge [MANUAL]** | **closing operator** | Append 5 REMEDIATED events to `.security/vulnerabilities.jsonl` |
| **T060** | **11 Post-merge [MANUAL]** | **closing operator** | release-please verify (push empty marker if needed; F-212 lesson) |
| **T061** | **11 Post-merge [MANUAL]** | **`security-analyst`** | Test-7 / SC-002 — `/security` re-scan against post-merge `main` |
| **T062** | **11 Post-merge [MANUAL]** | **closing operator** | Test-6 fresh-checkout smoke (clone tachi → run init.sh against nextjs-supabase) |

**Distribution**:
- `senior-backend-engineer`: **58 tasks** (T001-T043, T045-T047, T049-T056) — 93.5% of all tasks; matches single-agent-interleaved cadence
- `team-lead`: **1 task** (T044 Day-5 slip-watch gating decision)
- `architect`: **1 task** (T048 Day-8 architectural checkpoint)
- `security-analyst`: **1 task** (T061 [MANUAL] post-merge security re-scan)
- closing operator: **5 tasks** ([MANUAL] T057, T058, T059, T060, T062 — `/aod.deliver` actions)

`tester` and `code-reviewer` engage at out-of-band review checkpoints (Day-4 fixture-design review; Day 6-9 large-PR review iteration) — see §7 NOTES.

---

## 4. Parallel Execution Waves

Tasks are grouped by dependency into 7 waves. Within each wave, [P] tasks may execute in parallel; sequential tasks chain by dependency arrows.

### Wave 1 — Setup + Foundational (Day 1, ~0.5d)

**Tasks**: T001 → (T002 [P], T003 [P], T004 [P]) → T005 → (T006 [P], T007 [P], T008 [P])

**Agent**: `senior-backend-engineer`

**Parallelism**:
- T002, T003, T004 parallel (independent fixture-dir mkdir + manifest snapshot)
- After T005 baseline benchmark: T006, T007, T008 parallel (different artifacts: contract, contract verify, CHANGELOG placeholder)

**Sequential chain**: T001 (branch verify) → T002-T004 (parallel) → T005 (benchmark) → T006-T008 (parallel)

**Quality Gate (end-of-wave)**: Workspace clean; baseline timings recorded in tasks-runlog.txt; both contracts ready; CHANGELOG slot reserved.

---

### Wave 2 — Stream 1 Library Bring-Up (Day 1-3, ~2.5d, CRITICAL PATH)

**Tasks**: T009 → T010 → (T011 [P-leg], T012 [P-leg]) → T013

**Agent**: `senior-backend-engineer`

**Parallelism**:
- T011 (macOS verify) + T012 (Linux verify) can run as parallel CI legs once T010 lands
- T013 (perf benchmark) sequential after T011/T012 green

**Sequential chain**: T009 (test author, 27 cases per Constitution VI test-first) → T010 (library impl, 7-step bash 3.2) → T011/T012 (cross-platform verify) → T013 (Day-1 post-impl benchmark)

**Quality Gate (end-of-wave)**: Library functional + unit-tested on bash 3.2 + bash 4+; ≥17/17 cases pass on macOS (Day-5 GREEN-LIGHT condition 1 partially met); benchmark numbers staged for ADR-040 §Consequences.

---

### Wave 3 — Stream 2 Sites + Streams 3+4 (Day 3-5, ~3.5-4.0d interleaved)

**Tasks**: Sites A/B/C/D + Stream 4 + Stream 3 (independent of Stream 2)

**Agent**: `senior-backend-engineer` (single-agent-interleaved per PRD)

**Parallelism**:
- All 4 sites + Stream 4 + Stream 3 can begin once Wave 2 (library) complete
- **Within single-agent-interleaved cadence**: senior-backend-engineer alternates between sites in priority order (Site A first per HIGH severity, then Site B, then Site C, then Site D, with Stream 4 + Stream 3 interleaved as breakpoints)
- **Test [P] within sites**: T014 (Site A test) + T020/T021 (Site B test) + T025/T026 (Site C test) + T034 (Site D test) + T037/T038 (Stream 4 test) parametrize-author phase can be batched [P]

**Site sub-flows** (each follows test-first per Constitution VI):

| Site/Stream | Test-First | Implementation | Verify |
|-------------|------------|----------------|--------|
| Site A (HIGH, 0.5d) | T014 | T015 → T016 → T017 → T018 | T019 |
| Site B (HIGH, 0.75d) | T020, T021 | T022 → T023 | T024 |
| Site C (MEDIUM, 0.5d) | T025, T026 | T027 → T028 → T029 → T030 → T032 → T031 (strict reorder per architect feedback) | T033 |
| Site D (MEDIUM, 0.75-1.0d) | T034 | T035 | T036 |
| Stream 4 (LOW, 1.0d) | T037, T038 | T039 → T040 | T041 |
| Stream 3 (independent) | n/a | T042 ADR-040 Proposed | T043 PR title |

**Sequential within Site C**: T032 (init-input.sh F-1 amendment) MUST land BEFORE T031 (writer escape removal) per architect strict-reorder feedback — F-1 boundary tightening is the precondition for safely dropping the escape pass.

**Quality Gate (end-of-wave)**: All 4 sites + clone timeout green on macOS + Linux; ADR-040 Proposed committed; PR #257 title Conventional-Commits-formatted; 4 vuln_ids closed (TACHI-VULN-6f5a95085056, bf5496e9fcdf, 9a7512071b4a, 4dc6cf8f88ea). 5th vuln_id (851fd6a21ba9 clone timeout) closes here too.

---

### Wave 4 — Day-5 Slip-Watch Checkpoint (Day 5, ~0.0d gating decision)

**Task**: T044

**Agent**: `team-lead` (gating decision authority; may consult `architect` for ADR-040 condition)

**Action**: Verify all 4 GREEN-LIGHT conditions per plan §Day-5 Slip-Watch Checkpoint:
1. ≥17/17 cases pass on macos-latest CI (T011/T012)
2. Site A green on Linux (T019)
3. ADR-040 Proposed committed (T042)
4. Clone timeout watchdog smoke-tests pass on macOS bash 3.2 (T040)

**Escalation ladder** (3-tier per plan):
- 0-1 conditions red: continue
- 2 conditions red: Team-Lead escalates to PM with recovery levers (Q-1 split / drop key_case / drop clone timeout)
- 3+ conditions red: structural slip; escalate immediately

**Quality Gate (end-of-wave)**: GREEN (proceed to Wave 5) OR recovery lever activated (per escalation ladder; document outcome in tasks-runlog.txt).

---

### Wave 5 — Stream 5 Finalization + Day-8 Checkpoint (Day 6-8, ~1.5d)

**Tasks**: (T045 [P], T046, T047 [P]) → T048

**Agent**: `senior-backend-engineer` (T045-T047) + `architect` (T048)

**Parallelism**:
- T045 (regen script) + T047 (B-3 cases) parallel
- T046 (run T045) sequential after T045 lands
- T048 (Day-8 checkpoint) after T045-T047 complete

**Sequential chain**: T045 → T046 (run script) ; T047 (parallel) → T048

**Quality Gate (end-of-wave)**: Stream 5 ≥80% case coverage; fixture corpus committed; ADR-040 transitioning to Accepted; Day-8 checkpoint passed (else use Day 9 as soak day, merge at Day 10-11 within hard ceiling).

---

### Wave 6 — Final Verification + Polish (Day 8-9, ~1.0d)

**Tasks**: T049 → (T050 [P], T051 [P], T052 [P]) → T053 → T054 → T055 → T056

**Agent**: `senior-backend-engineer`

**Parallelism**:
- T050, T051, T052 parallel after T049 green (independent NFR/SC verifications)
- T053-T056 sequential (CHANGELOG → ADR Accepted → benchmark doc verify → final pre-merge)

**Sequential chain**: T049 (full suite) → T050/T051/T052 (parallel) → T053 (CHANGELOG) → T054 (ADR Accepted) → T055 (SC-010 verify) → T056 (final pre-merge)

**Quality Gate (end-of-wave)**: Full test suite green on macOS + Linux; ADR-040 Accepted; CHANGELOG finalized; all NFRs (NFR-001-006) + SCs (SC-001-015) verified; PR #257 ready for `/aod.deliver` operator action.

---

### Wave 7 — Post-Merge [MANUAL] (closing operator at /aod.deliver)

**Tasks**: T057, T058, T059, T060, T061, T062

**Agents**: closing operator (T057, T058, T059, T060, T062) + `security-analyst` (T061)

**NOT executed within this PR**. These run at `/aod.deliver` time per `.claude/rules/git-workflow.md` deliver-stage protocol:
- T057 — pre-merge PR title re-verify
- T058 — squash-merge
- T059 — append 5 REMEDIATED events to `.security/vulnerabilities.jsonl`
- T060 — release-please verification + empty marker push if needed (F-212 lesson)
- T061 — `security-analyst` runs post-merge `/security` re-scan
- T062 — fresh-checkout smoke test (Test-6)

**Quality Gate**: Feature delivered; 5 REMEDIATED events recorded; release-please PR opened; zero new findings in source-pattern surface; F-2 closes BLP-02 Wave 2.

---

## 5. Quality Gates Between Waves

| Gate | Wave | Conditions to Proceed | Failure Lever |
|------|------|----------------------|---------------|
| G1 | End of Wave 1 | Workspace ready; baseline benchmark recorded; both contracts complete; CHANGELOG slot reserved | None — abort feature if dependency snapshot or benchmark fails |
| G2 | End of Wave 2 | Library functional; ≥17/17 cases pass macOS bash 3.2; Linux bash 4+ green; benchmark numbers staged | Q-1 split → MVP scope (Phase 3 only); rebuild library |
| G3 | End of Wave 3 | All 4 sites + clone timeout green on macOS + Linux; ADR-040 Proposed committed; 5 vuln_ids closed pending merge | Day-5 slip-watch (Wave 4) decides recovery |
| **G4** | **End of Wave 4** | **All 4 GREEN-LIGHT conditions met (T044) — full Phase 3-9 in scope** | **Activate recovery lever (Q-1 split → MVP = Phases 1-5+9; Phases 6-8 → F-2b in 3-4d)** |
| G5 | End of Wave 5 | Stream 5 ≥80% case coverage; ADR-040 Accepted-transitioning; Day-8 checkpoint passed (T048) | Day 9 soak day fallback; merge at Day 10-11 within hard ceiling |
| G6 | End of Wave 6 | Full test suite green macOS + Linux; ADR-040 Accepted; CHANGELOG finalized; NFR-002/005 + SC-005 verified; PR ready | None — abort merge if pre-merge verification fails |
| G7 | Wave 7 (post-merge) | PR title Conventional-Commits; squash-merged; 5 REMEDIATED events appended; release-please PR opened; security-analyst post-merge re-scan zero new findings; fresh-checkout smoke green | F-212 lesson — push empty `feat(256):` marker commit if release-please skipped |

---

## 6. Time Estimates per Wave

Total active effort sums to **8.75d**, leaving 0.75d headroom against the 9.5d active hard ceiling (15.8% buffer; preserved above the 12.5% floor per plan §Schedule Buffers).

| Wave | Phase(s) | Task Count | Active Effort | Cumulative | Notes |
|------|----------|------------|---------------|------------|-------|
| 1 | 1 + 2 (Setup + Foundational) | 8 | ~0.5d | 0.5d | T002-T004 + T006-T008 parallel; T005 baseline serial |
| 2 | 3 (Library bring-up) | 5 | ~2.5d | 3.0d | **CRITICAL PATH** per H-1 — test-first sequential within Stream 1 |
| 3 | 4 + 5 + 6 + 7 + 8 + 9 (Stream 2.A-D + Stream 4 + Stream 3) | 30 | ~3.5-4.0d | 6.5-7.0d | Single-agent-interleaved across sites; can compress with two-agent parallel escape hatch (~6-7d total active per PRD §Timeline) |
| 4 | 10 (T044 Day-5 slip-watch) | 1 | ~0.0d | 6.5-7.0d | Gating decision; recovery lever activates only on red |
| 5 | 10 (T045-T048 Stream 5 + Day-8) | 4 | ~1.5d | 8.0-8.5d | T045 + T047 parallel; Day-8 checkpoint at end |
| 6 | 10 (T049-T056 Polish + Final) | 8 | ~1.0d | 9.0-9.5d | T050-T052 parallel after T049 |
| 7 | 11 (Post-merge MANUAL) | 6 | n/a | n/a | At `/aod.deliver` — outside active-effort budget |

**Total active**: 9.0-9.5d (within 9.5d ceiling; 0.0-0.5d slack at 12.5% floor; 0.0-15.8% headroom).
**Wall-clock**: 11d hard ceiling absorbs CI flake + review iteration + soak day per plan §Schedule Buffers.

---

## 7. NOTES

### 7.1 PRD §Resource Assignment cadence (single-agent-interleaved)

Per PRD §Resources, F-2 is mandated to single-agent-interleaved cadence with `senior-backend-engineer` driving 93.5% of all tasks (T001-T043, T045-T047, T049-T056). This intentionally trades parallelism for **state-machine integrity**: bash library + 4-site refactor + F-1 contract amendment require coherent mental model across all touch points (e.g., Site C T032 init-input.sh amendment must precede T031 writer escape removal). A multi-agent split would incur high coordination overhead (per architect-feedback strict-reorder constraint).

### 7.2 Day-4 tester fixture-design review (informal, pre-T044)

Per architect informational observation #4 (team-lead-tasks.md), `tester` should perform an **informal fixture-design review at Day 4 EOD** before T044 Day-5 slip-watch fires. Scope: review test-corpus authoring quality (T009 27 cases, T014/T020/T021/T025/T026/T034/T037/T038 site + Stream 4 cases). No specific task ID; engages out-of-band against the running PR via comment thread. Does NOT block T044 even if comments outstanding (T044 conditions are independent of this review).

### 7.3 Day 6-9 code-reviewer iteration cycle for large-PR review

PR #257 final size is estimated at **~700-1100 LOC** across 7-9 files (library + 4 site refactors + ADR-040 markdown + CHANGELOG + 5 test files + fixture corpus). Per `.claude/rules/governance.md` and PR-review canon, `code-reviewer` should engage iteratively from Day 6 onward with at least 2 review passes:
- **Day 6 EOD**: First review against Wave 3 commits (Stream 1 + 4 sites + Stream 4)
- **Day 8 EOD**: Second review against Wave 5 commits (Stream 5 fixture corpus + ADR Accepted)
- **Day 9 EOD**: Final review pre-merge against Wave 6 commits

No specific task ID; review iteration runs out-of-band against the draft PR. Approval gates the `/aod.deliver` squash-merge action (T058) but does NOT block T044/T048 internal checkpoints.

### 7.4 Two-agent parallel escape hatch (NOT default)

PRD §Timeline mentions a **~6-7d active two-agent parallel** alternative (vs 8.75d single-agent-interleaved baseline). This escape hatch is NOT the default cadence. Activate ONLY if Wave 4 (T044 Day-5 slip-watch) passes GREEN-LIGHT but Day 6 progress trends red against the 9.5d active ceiling. Two-agent split would assign Stream 2.C+D (Sites C+D) to a second `senior-backend-engineer` instance while the first continues Stream 2.A+B + Stream 4 + Stream 3. Coordination overhead is non-trivial: requires cross-session state sync on F-1 amendment (T032) ordering, ADR-040 §Consequences benchmark fold-in, and CHANGELOG migration guidance authoring. Per team-lead-tasks.md observation #5, this escape hatch is intentionally NOT codified in tasks.md to avoid coordination-tax accidents on the default path.

### 7.5 F-2 reuse contract for downstream BLP features

The `aod_template_load_kv_file` library is the canonical config-load primitive for **all future** AOD config-file consumers. Future BLP features (F-3, F-4, F-5) MUST adopt this library rather than reinventing `source` or `eval`-based load patterns. Site D collapse (T035) demonstrates the canonical 7-line library-delegation pattern; Site B (T022/T023) demonstrates the canonical lowercase-mode pattern (no whitelist; per-field validators run after load). Per ADR-040 §Decision Item 1, NEW config-file load sites in BLP-02 Wave 3+ default to library invocation; deviation requires Architect sign-off documented in a follow-on ADR.

### 7.6 Triad sign-offs already complete (frontmatter)

Per tasks.md frontmatter (2026-05-04):
- **PM signoff**: APPROVED — clean trace from 9 FRs + 15 SCs + 8 USs + 6 Q-* adjudications to T001-T062
- **Architect signoff**: APPROVED — 13 architectural correctness criteria pass; 3 informational observations (non-blocking)
- **Team-Lead signoff**: APPROVED_WITH_CONCERNS — 5 informational observations (non-blocking); §7.1-7.5 above re-state observations 1-5 verbatim per team-lead-tasks.md

`product-manager` and `team-lead` own these sign-offs (already complete) and own NO implementation tasks. `team-lead` re-engages only at T044 (Day-5 slip-watch gating decision).

---

## 8. Acceptance Criteria for This Document

- [x] All 62 tasks (T001-T062) mapped to a primary agent
- [x] All assigned agents are valid `subagent_type` names from `.claude/agents/_README.md`
- [x] No invented generic labels (e.g. `file-agent`, `doc-agent`, `qa-agent`)
- [x] 7 waves enumerated with parallelism opportunities + sequential chains documented
- [x] Quality gates between waves explicit
- [x] Time estimates sum to ≤ 9.5d active (8.75d single-agent-interleaved + 0.75d headroom; 15.8% buffer)
- [x] PRD §Resources single-agent-interleaved cadence honored (senior-backend-engineer = 93.5% of tasks)
- [x] Day-4 tester review + Day 6-9 code-reviewer cycle + two-agent escape hatch + F-2 reuse contract all noted

**Document status**: Complete and ready for orchestrator handoff at `/aod.build` invocation.
