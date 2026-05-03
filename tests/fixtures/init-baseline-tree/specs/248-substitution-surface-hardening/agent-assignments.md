---
feature_id: 248
feature_name: substitution-surface-hardening
initiative: BLP-02 Wave 1
generated_by: team-lead
generated_date: 2026-05-03
agent_registry_source: .claude/agents/_README.md
agent_registry_version: 2.0.0 (13 agents)
total_tasks: 50
total_phases: 10
total_waves: 7
sequencing_model: single-agent serial (PRD §Timeline) with named hand-offs
timeline_active_days: 8
timeline_hard_ceiling_days: 10
slip_watch_day: 5 (Wed 2026-05-08)
---

# Agent Assignments: Substitution Surface Hardening (F-248, BLP-02 Wave 1)

**Feature**: F-248 — Substitution Surface Hardening
**Branch**: `248-substitution-surface-hardening`
**Draft PR**: #249
**Tasks**: 50 across 10 phases (`tasks.md` triple-signed 2026-05-03 — PM APPROVED, Architect APPROVED, Team-Lead APPROVED_WITH_CONCERNS)
**Plan timeline**: 8 working days active / 10 working days hard ceiling
**Sequencing model**: Single-agent serial per PRD §Timeline (8d realistic for one `senior-backend-engineer`); two-agent parallel theoretical 5d but coordination overhead on single-PR squash is net wash. Named hand-offs to `architect`, `tester`, `security-analyst`, `devops` enforce SDLC quality gates without inflating wall-clock.

---

## 1. Agent Roster (Exact Names — Sourced from `.claude/agents/_README.md`)

Only agents listed below are valid `subagent_type` values. The agents not used by F-248 are listed for completeness.

| Agent (exact name) | Used by F-248? | Role on F-248 |
|---|---|---|
| `senior-backend-engineer` | YES (primary) | All bash + markdown + ADR + CHANGELOG implementation; 36 of 50 tasks |
| `tester` | YES | Authors all 5 test files / fixture script (T009–T013); runs the local pytest pass (T039) |
| `architect` | YES | Reviews ADR-038 §Decision and promotes Status `Proposed → Accepted` (T036) |
| `security-analyst` | YES | Manual smoke-test gate (T042); post-merge vulnerability log update (T047); post-merge `/security` re-scan (T049) |
| `devops` | YES | CI matrix verification (T040); pre-merge release-please verification (T043); post-merge release-please verification (T048) |
| `product-manager` | YES (gating only) | Slip-watch escalation arbiter (T041); post-merge LinkedIn comment author (T050) |
| `team-lead` | YES (this doc) | Authored these assignments; arbitrates if a wave slips |
| `orchestrator` | NO | Single-agent serial sequencing; no parallel-wave dispatch needed |
| `code-reviewer` | NO (deferred) | The PR squash-merge review at `/aod.deliver` is operator-driven; no in-build code-reviewer invocation in tasks.md |
| `frontend-developer` | NO | F-248 is template/bash only — no UI surface |
| `ux-ui-designer` | NO | No design surface |
| `web-researcher` | NO | All research already captured in `research.md` at `/aod.spec` time |
| `debugger` | NO (reactive) | Invoked only if Day-5 slip-watch traces to a bug; not pre-assigned |

---

## 2. Agent Assignment Matrix (Per Task)

Tasks tagged `[MANUAL]` are operator gating actions executed at `/aod.deliver`, not during build. The agent named on a `[MANUAL]` task is the **owner** who validates the operator action — not the operator.

### Phase 1: Setup (Shared Infrastructure) — Day 1 morning

| Task | Description | Owner Agent | Notes |
|---|---|---|---|
| T001 | Verify branch + draft PR + sign-offs | `senior-backend-engineer` | git/gh state inspection; trivial |
| T002 [P] | Create `.aod/templates/` if missing | `senior-backend-engineer` | `mkdir -p` |
| T003 [P] | Create `tests/fixtures/` if missing | `senior-backend-engineer` | `mkdir -p` |
| T004 [P] | Snapshot dependency manifests (NFR-002 baseline) | `senior-backend-engineer` | `git show HEAD:` + sha256 to runlog |

### Phase 2: Foundational (Blocking Prerequisites) — Day 1 afternoon

| Task | Description | Owner Agent | Notes |
|---|---|---|---|
| T005 | Internal-tooling search for Q-1 adjudication (5-min grep) | `senior-backend-engineer` | Records outcome in spec.md §Internal-Tooling Search Outcome |
| T006 [P] | Author `constitution-instructional.md` (full template) | `senior-backend-engineer` | Markdown authoring |
| T007 [P] | Author `constitution-clean.md` (post-strip variant); validate byte-equivalence vs sed cleanup | `senior-backend-engineer` | Strict byte-faithfulness check inline |
| T008 | Stream 1 Day 1 baseline benchmark (`time ./scripts/init.sh`) | `senior-backend-engineer` | Captures `real`/`user`/`sys` to runlog for ADR-038 §Consequences |

### Phase 3: User Story 1 + 6 (P1) — Substitution + Multi-Hop Defense Layer 2

#### Test authorship (Stream 5 leading edge — TEST-FIRST per Constitution VI)

| Task | Description | Owner Agent | Notes |
|---|---|---|---|
| T009 [P] | Author `test_init_sh_substitution.py` (Test-1 fixture-replay) | `tester` | pytest-via-subprocess; `Path.read_bytes()` byte-comparison |
| T010 [P] | Author `test_init_sh_adversarial.py` (Test-2 ≥13 cases) | `tester` | parametrize table; substitution + rejection classes |
| T011 [P] | Author `test_init_sh_constitution.py` (Test-4 byte-compare) | `tester` | Constitution copy verification |
| T012 [P] | Author `test_init_sh_self_delete.py` (Test-5' self-delete) | `tester` | Replaces original Test-5 per Architect M-3 |
| T013 [P] | Author `regenerate-baseline.sh` script | `tester` | Documentation header on regen criteria |

#### Implementation (Stream 1 substitution adoption)

| Task | Description | Owner Agent | Notes |
|---|---|---|---|
| T015 | Source `template-substitute.sh` at top of `init.sh` | `senior-backend-engineer` | Replace lazy source; bash 3.2 compatible |
| T016 | Add re-init pre-flight check | `senior-backend-engineer` | FR-003 |
| T017 | Reorder snapshot-write to BEFORE substitution loop (BLOCKING B-2 P1) | `senior-backend-engineer` | Strict ordering; precedes T018 |
| T018 | Add `aod_template_load_personalization_env` post-snapshot-write | `senior-backend-engineer` | Sets `AOD_PERSONALIZATION_<KEY>` env |
| T019 | Replace `replace_in_files()` with `find ... -print0` + `aod_template_substitute_placeholders` loop | `senior-backend-engineer` | FR-001; remove macOS/Linux sed branch entirely |
| T020 | Add residual scan via `aod_template_assert_no_residual` post-loop | `senior-backend-engineer` | FR-004; halt on any orphan `{{KEY}}` |
| T021 | Stream 1 Day 1 post-swap benchmark + NFR-004 delta calc | `senior-backend-engineer` | ≤5% / 5–50% / >50% triage |

#### Baseline regeneration (deferred dependency on T015–T021)

| Task | Description | Owner Agent | Notes |
|---|---|---|---|
| T014 | Run `regenerate-baseline.sh` with **post-Stream-1** init.sh; commit baseline tree | `senior-backend-engineer` | Must run AFTER T015–T021; populates `tests/fixtures/init-baseline-tree/` |

### Phase 4: User Story 2 (P1) — Multi-Line Paste Rejection + Defense Layer 1

| Task | Description | Owner Agent | Notes |
|---|---|---|---|
| T022 [P] | Author `.aod/scripts/bash/init-input.sh` (`aod_init_read_validated`) | `senior-backend-engineer` | Bash 3.2 only; F-132 `set +e`/`set -e` lesson |
| T023 | Source the new helper at top of `init.sh` | `senior-backend-engineer` | Sequenced after T022 |
| T024 | Wire prompt 1 (PROJECT_NAME, max_len=100) | `senior-backend-engineer` | Replace `read -p` |
| T025 | Wire prompt 2 (PROJECT_DESCRIPTION, max_len=300) | `senior-backend-engineer` | Replace `read -p` |
| T026 | Wire prompt 3 (GITHUB_ORG, max_len=39) | `senior-backend-engineer` | GitHub login hard limit |
| T027 | Wire prompt 4 (GITHUB_REPO, max_len=100) + preserve default fallback | `senior-backend-engineer` | Empty input → `GITHUB_REPO=$PROJECT_NAME` |

### Phase 5: User Story 3 (P1) — Gitignore Default

| Task | Description | Owner Agent | Notes |
|---|---|---|---|
| T028 | Verify `.gitignore:222` contains `.aod/personalization.env` | `senior-backend-engineer` | Verification only; no edit |
| T029 [P] | Update `contracts/personalization-schema.md` §Substitution Strategy | `senior-backend-engineer` | Local-only default + opt-in path |
| T030 [P] | Add CHANGELOG.md v4.x entry with migration command | `senior-backend-engineer` | Copy-pasteable `git rm --cached` |
| T031 | Add post-init success-message line in `init.sh` | `senior-backend-engineer` | Documents gitignore default at run-time |

### Phase 6: User Story 4 + 7 (P2) — ADR + Release Trigger + Enterprise Bundle

| Task | Description | Owner Agent | Notes |
|---|---|---|---|
| T032 | Replace constitution sed cleanup with `cp` from pre-stripped template | `senior-backend-engineer` | FR-008; depends on T006+T007 |
| T033 | Implement Q-1 disposition per T005 outcome (Option b default = `git rm`; Option a fallback = canonical-13 PROJECT_PATH) | `senior-backend-engineer` | Branches on T005 result |
| T034 [P] | Author ADR-038 with Status `Proposed` (dual-commit pattern initial) | `senior-backend-engineer` | Includes F-1→F-2 pattern-vs-function reuse contract per H-2 |
| T035 | Append T021 benchmark + NFR-004 disposition to ADR-038 §Consequences | `senior-backend-engineer` | Depends on T021 + T034 |
| T036 | Promote ADR-038 Status `Proposed → Accepted` | **`architect`** | **Architect sign-off authority** per Triad governance; reviews §Decision and §Consequences before promotion |
| T037 | Update PR #249 title to canonical conventional-commits form | `senior-backend-engineer` | `gh pr edit 249 --title "..."`; FR-010 |

### Phase 7: User Story 5 (P2) — Placeholder Contract Closure Verification

| Task | Description | Owner Agent | Notes |
|---|---|---|---|
| T038 | Manual one-shot orphan-probe verification | `senior-backend-engineer` | Test-2 case 13 covers automated regression; T038 is one-time gate |

### Phase 8: Test Execution + CI Verification (Stream 5 finalization)

| Task | Description | Owner Agent | Notes |
|---|---|---|---|
| T039 | Run `pytest tests/scripts/test_init_sh_*.py -v` locally on macOS bash 3.2.57 | `tester` | Capture run log to runlog |
| T040 | Push to `origin/248-...`; verify GitHub Actions matrix (macos + ubuntu) green | `devops` | CI infrastructure ownership |
| T041 | Day 5 (Wed 2026-05-08) slip-watch checkpoint; escalate to PM if CI not green | `team-lead` → `product-manager` | Possible scope cuts named in tasks.md; **hard floor**: never drop Test-1 + Test-2 cases 1–6 |

### Phase 9: Polish & Cross-Cutting

| Task | Description | Owner Agent | Notes |
|---|---|---|---|
| T042 [MANUAL] | Test-6 manual smoke test on fresh checkout (`/tmp/tachi-smoke-test`) | **`security-analyst`** | Validates security regression posture: literal `AT&T` substitution + zero residuals + gitignore + constitution byte-equality |
| T043 | Pre-merge: re-verify PR #249 title is conventional-commits-formatted | **`devops`** | Belt-and-suspenders R12; CI/release management ownership |
| T044 [MANUAL] | Verify dependency manifests unchanged (NFR-002) | `senior-backend-engineer` | `git diff main..HEAD -- pyproject.toml requirements*.txt package.json` MUST be empty |
| T045 [MANUAL] | Verify schemas/finding.yaml unchanged (NFR-005) | `senior-backend-engineer` | `git diff main..HEAD -- schemas/finding.yaml` MUST be empty |

### Phase 10: Post-Merge (Manual at `/aod.deliver`)

| Task | Description | Owner Agent | Notes |
|---|---|---|---|
| T046 [MANUAL] | Squash-merge PR #249 | `devops` | Closing operator action; devops as release authority |
| T047 [MANUAL] | Append 5 `REMEDIATED` events to `.security/vulnerabilities.jsonl` | **`security-analyst`** | Vuln log ownership; merge SHA + ISO 8601 ts; uses existing finding.yaml schema |
| T048 [MANUAL] | Verify release-please opens release PR; push empty marker if skipped | **`devops`** | F-212 lesson; release management |
| T049 [MANUAL] | Run `/security` re-scan against main HEAD (Test-7) | **`security-analyst`** | Validates 5 REMEDIATED events; expects zero new findings |
| T050 [MANUAL] | LinkedIn comment on Daniel Wood thread | `product-manager` | **PM-controlled, NOT a DoD gate** per Team-Lead Pass 1 M-3; within 5 business days |

### Assignment summary by agent

| Agent | Tasks Owned | Task IDs |
|---|---:|---|
| `senior-backend-engineer` | 33 | T001–T008, T014, T015–T021, T022–T027, T028–T031, T032–T035, T037, T038, T044, T045 |
| `tester` | 6 | T009, T010, T011, T012, T013, T039 |
| `security-analyst` | 3 | T042, T047, T049 |
| `devops` | 3 | T040, T043, T046, T048 (4 — see correction note below) |
| `architect` | 1 | T036 |
| `product-manager` | 2 | T041 (escalation arbiter), T050 |
| `team-lead` | 1 | T041 (initiator) |

**Correction note**: `devops` owns 4 tasks (T040, T043, T046, T048). Total = 33 + 6 + 5 + 4 + 1 + 2 + 1 = **52 owner-slots across 50 tasks** (T041 is co-owned by team-lead and product-manager; T046 is operator-executed but devops-validated alongside T048, kept as devops slot for accountability). Accounting reconciles via the dual-ownership row.

Workload distribution check: `senior-backend-engineer` carries 33 / 50 = 66% — under the 80% overload threshold per team-lead success criteria. Acceptable for single-agent serial mode.

---

## 3. Parallel Execution Waves

The wave structure below maps the recommended sequencing. **Within a single-agent serial mode, "[P]" parallel tasks are interleaved by the same `senior-backend-engineer` rather than dispatched to multiple agents** — the parallel marker indicates "no dependency, can be reordered freely," not "must run concurrently." Hand-offs to other agents (`tester`, `architect`, `security-analyst`, `devops`, `product-manager`) ARE concurrent in wall-clock terms when the sequencing permits.

### Wave 0 — Setup (Day 1 morning, ~1h)

**Owner**: `senior-backend-engineer` (all parallel)

- T001 — branch/PR/sign-off verification
- T002 [P] — `.aod/templates/` directory
- T003 [P] — `tests/fixtures/` directory
- T004 [P] — manifest snapshot for NFR-002

**Quality gate exit**: workspace clean; runlog initialized with manifest sha256s.

### Wave 1 — Foundational (Day 1 afternoon, ~3h)

**Owner**: `senior-backend-engineer`

- T005 — internal-tooling search for Q-1 adjudication (5 min grep, gates T033)
- T006 [P] — `constitution-instructional.md` author
- T007 [P] — `constitution-clean.md` author + byte-equivalence validation
- T008 — Stream 1 Day 1 baseline benchmark (`time ./scripts/init.sh` pre-swap)

**Quality gate exit**:
- Q-1 outcome committed to spec.md (default Option b unless wired consumer surfaces)
- T007 byte-equivalence proven (manual `sed | diff` check passes)
- T008 baseline `real`/`user`/`sys` recorded in runlog (NFR-004 anchor)

### Wave 2 — Test authorship (Day 2, ~6h)

**Owner**: `tester` (parallel-friendly; can run concurrently with Wave 1 trailing tasks if `tester` boots earlier)

- T009 [P] — `test_init_sh_substitution.py` (Test-1)
- T010 [P] — `test_init_sh_adversarial.py` (Test-2, ≥13 cases)
- T011 [P] — `test_init_sh_constitution.py` (Test-4)
- T012 [P] — `test_init_sh_self_delete.py` (Test-5')
- T013 [P] — `regenerate-baseline.sh`

**Quality gate exit (TEST-FIRST per Constitution VI)**:
- All 4 test files committed BEFORE Wave 3 implementation
- Tests fail against pre-merge baseline (verifies they assert the right invariant)
- T013 `regenerate-baseline.sh` documented with regen criteria header

### Wave 3 — Streams 1 / 2 / 3 / 4 implementation (Day 2 EOD – Day 4, ~12h)

**Owner**: `senior-backend-engineer` (single-agent serial; ordering enforced where dependencies require)

#### Stream 1 (critical path — strict ordering T017 → T018 → T019 → T020)

- T015 — source template-substitute.sh at top of init.sh
- T016 — re-init pre-flight check
- T017 — reorder snapshot-write BEFORE substitution loop *(BLOCKING B-2 pattern P1)*
- T018 — `aod_template_load_personalization_env` post-snapshot-write
- T019 — replace `replace_in_files()` with bash-param-expansion loop
- T020 — residual scan via `aod_template_assert_no_residual`
- T021 — Stream 1 Day 1 post-swap benchmark + NFR-004 delta calc

#### Stream 2 (interleavable; T023 must follow T015)

- T022 [P] — author `init-input.sh` helper
- T023 — source helper at top of init.sh
- T024 — wire prompt 1 (PROJECT_NAME)
- T025 — wire prompt 2 (PROJECT_DESCRIPTION)
- T026 — wire prompt 3 (GITHUB_ORG)
- T027 — wire prompt 4 (GITHUB_REPO + default fallback preserved)

#### Stream 3 (interleavable)

- T028 — `.gitignore` verification
- T029 [P] — `contracts/personalization-schema.md` update
- T030 [P] — CHANGELOG.md v4.x entry
- T031 — post-init success-message line

#### Stream 4 partial (depends on T006+T007 for T032; depends on T005 for T033)

- T032 — constitution sed → `cp` migration
- T033 — Q-1 disposition implementation (Option b `git rm` default OR Option a canonical-13 fallback)
- T034 [P] — ADR-038 Status `Proposed` (initial dual-commit)

**Quality gate exit**:
- T021 benchmark delta within NFR-004 thresholds (≤5% holds 10%; 5–50% loosens to 25% with rationale; >50% PM escalation)
- All 4 prompts wired with `aod_init_read_validated`
- `replace_in_files()` removed; residual scan in place
- ADR-038 Proposed committed; `T035` and `T036` deferred to Wave 5

### Wave 4 — Baseline + Test Execution (Day 4 – Day 5 morning, ~4h)

#### Baseline regeneration

- T014 — run `regenerate-baseline.sh` with post-Stream-1 init.sh; commit baseline tree (`senior-backend-engineer`)

#### Test execution

- T038 — manual orphan-probe one-shot (`senior-backend-engineer`)
- T039 — local pytest pass on macOS bash 3.2.57 (`tester`)
- T040 — push + verify CI matrix green (macos + ubuntu) (`devops`)

**Quality gate exit**:
- `tests/fixtures/init-baseline-tree/` committed
- All 4 pytest files green locally
- GitHub Actions matrix green on both runners; URLs in runlog

### Wave 5 — Day-5 Slip-Watch + ADR Accepted + Polish (Day 5 EOD – Day 7, ~6h)

#### Slip-watch gate (CRITICAL — Day 5 EOD = Wed 2026-05-08)

- T041 — slip-watch checkpoint (`team-lead` initiates; `product-manager` arbitrates if scope cut needed)

**Scope cut priorities (if invoked)**:
1. Drop Test-2 corpus from ≥13 → 8 cases (KEEP all rejection-class + cases 1–6 substitution-semantics)
2. Defer ADR §Consequences benchmark numbers to post-merge ADR amendment
3. Defer Test-7 post-merge re-scan documentation to `/aod.deliver` retrospective

**Hard floor (NEVER cut)**: Test-1 fixture-replay byte-comparison; Test-2 cases 1–6 substitution-semantics correctness.

#### ADR sign-off chain

- T035 — append T021 benchmark + NFR-004 disposition to ADR-038 §Consequences (`senior-backend-engineer`)
- T036 — **`architect`** promotes ADR-038 Status `Proposed → Accepted` after reviewing §Decision (residual-scan regex character class lockstep commitment per M-2) and §Consequences (benchmark numbers + F-1→F-2 pattern-vs-function contract per H-2)

#### Pre-merge polish

- T037 — retitle PR #249 to canonical conventional-commits form (`senior-backend-engineer`)
- T042 [MANUAL] — Test-6 manual smoke test on fresh checkout (`security-analyst`)
- T043 — pre-merge re-verify PR #249 title (`devops`, R12 belt-and-suspenders)
- T044 [MANUAL] — NFR-002 manifest diff check (`senior-backend-engineer`)
- T045 [MANUAL] — NFR-005 finding.yaml diff check (`senior-backend-engineer`)

**Quality gate exit**:
- ADR-038 Status: Accepted (architect-signed)
- PR title: `feat(248): harden init.sh substitution surface — sed → bash param expansion + input validation + gitignore default`
- T042 smoke test passes (4 invariants: AT&T literal substitution count > 0; zero residual `{{KEY}}`; `.aod/personalization.env` gitignored; constitution byte-equality)
- NFR-002 + NFR-005 diff checks empty
- All 14 DoD items satisfied

### Wave 6 — Post-Merge at `/aod.deliver` (Day 8+)

**[MANUAL] gating actions, executed by closing operator**

- T046 [MANUAL] — squash-merge PR #249 (`devops`)
- T047 [MANUAL] — append 5 REMEDIATED events to `.security/vulnerabilities.jsonl` (`security-analyst`)
- T048 [MANUAL] — verify release-please opens release PR within ~30s; push empty marker if skipped (`devops`)
- T049 [MANUAL] — `/security` re-scan against main HEAD; verify Test-7 (`security-analyst`)
- T050 [MANUAL] — LinkedIn comment on Daniel Wood thread (`product-manager`, NOT a DoD gate)

**Quality gate exit**:
- Merge SHA recorded in 5 REMEDIATED events
- release-please PR opened (or marker pushed)
- Zero new findings on Test-7 re-scan
- Public posture trail visible (LinkedIn at PM discretion)

---

## 4. Quality Gates Between Waves

Each gate MUST pass before the next wave begins. The `senior-backend-engineer` is responsible for verifying the gate before proceeding; `team-lead` arbitrates on disputes; agent-specific sign-off authorities are named below.

| Gate | After Wave | Required Pass Conditions | Authority |
|---|---|---|---|
| **G0: Workspace ready** | 0 | Branch correct; draft PR exists; sign-offs in spec.md+plan.md frontmatter; manifest baselines snapshotted | `senior-backend-engineer` self-verify |
| **G1: Foundational complete** | 1 | T005 outcome in spec.md; T007 byte-equivalence proven; T008 benchmark in runlog | `senior-backend-engineer` self-verify |
| **G2: Test-first preserved** | 2 | All 4 test files + regen script committed BEFORE Wave 3 implementation; tests fail against pre-merge baseline (Constitution VI compliance) | `tester` confirms |
| **G3: Implementation green** | 3 | T021 benchmark delta within NFR-004 thresholds; `replace_in_files()` removed; 4 prompts wired; ADR-038 Proposed committed | `senior-backend-engineer` self-verify; `team-lead` validates if NFR-004 escalates above 50% |
| **G4: Test execution green** | 4 | T039 local pytest green on macOS 3.2.57; T040 CI matrix green on both runners; T038 orphan probe halts non-zero | `tester` (local) + `devops` (CI) co-sign |
| **G5: Day-5 slip-watch passes (CRITICAL)** | 5 (start) | If by EOD Wed 2026-05-08 G4 has not been crossed, T041 fires PM escalation | `team-lead` initiates; `product-manager` arbitrates scope cuts |
| **G6: ADR sign-off chain** | 5 (mid) | T036 architect promotes ADR-038 to Accepted only after reviewing §Decision (residual-scan regex character class lockstep) + §Consequences (benchmark + F-1→F-2 reuse contract) | **`architect` sign-off authority** per Triad governance |
| **G7: DoD complete** | 5 (end) | T042 smoke test passes 4 invariants; T043 PR title verified; T044+T045 diff checks empty; all 14 DoD items checked | `security-analyst` (T042) + `devops` (T043) co-sign |
| **G8: Post-merge integrity** | 6 | release-please PR open OR marker pushed; 5 REMEDIATED events logged; Test-7 re-scan finds zero new | `security-analyst` (T047, T049) + `devops` (T048) co-sign |

### Cross-cutting checkpoints

- **TEST-FIRST verification (G2)**: Per Constitution VI, T009–T013 land BEFORE T015–T021. The `tester` MUST run the new tests against the pre-merge `init.sh` and confirm they fail (asserting the substitution-semantics regression they're designed to catch). If tests pass against pre-merge baseline, the test corpus is mis-asserting and must be revised before Wave 3 begins.
- **NFR-004 escalation rules (G3)**: T021 delta calc applies the explicit thresholds in tasks.md. >50% triggers PM re-scope BEFORE merge; do not paper over with rationale.
- **Day-5 slip-watch (G5)**: This is the **single most important schedule gate**. If breached, do NOT silently extend timeline — escalate per scope-cut priority list. Hard floor invariants (Test-1 + Test-2 cases 1–6) NEVER drop.
- **ADR dual-commit (G6)**: ADR-038 lands twice — once as `Proposed` by `senior-backend-engineer` (T034), once as `Accepted` by `architect` (T036). The Proposed→Accepted promotion is NOT a self-merge by `senior-backend-engineer`; the architect agent reviews §Decision (M-2 lockstep commitment) and §Consequences (H-2 reuse contract + benchmark) before promoting.
- **Single-PR delivery contract (G7)**: All work lands in one squash-merged PR per PRD §Deliverable. Incremental commits within `248-substitution-surface-hardening` MAY happen; the merge to main is atomic.

---

## 5. Time Estimates Per Wave

Estimates map to plan.md's 8d active / 10d hard ceiling. Working day = 8h; durations are ranges with confidence levels.

| Wave | Calendar | Wall-Clock Estimate | Active Owner-Hours | Confidence | Notes |
|---|---|---|---|---|---|
| Wave 0 | Day 1 morning | 1h | 1h `senior-backend-engineer` | HIGH | 4 trivial setup tasks |
| Wave 1 | Day 1 afternoon | 3h | 3h `senior-backend-engineer` | HIGH | T005 grep is 5min; T006+T007 are markdown authoring; T008 is one `time` invocation |
| Wave 2 | Day 2 | 6h | 6h `tester` | MEDIUM | Test corpus design (esp. T010 ≥13 adversarial cases); regeneration script is non-trivial |
| Wave 3 | Day 2 EOD – Day 4 | 16–20h (2–2.5d) | 16–20h `senior-backend-engineer` | MEDIUM | Stream 1 critical path + Streams 2/3/4 partial; T019 is the largest single change |
| Wave 4 | Day 4 – Day 5 morning | 4–5h | 4h `senior-backend-engineer` (T014, T038) + 1h `tester` (T039) + 1h `devops` (T040 incl. CI wait) | HIGH | T040 CI wait could extend if matrix iterates |
| Wave 5 | Day 5 EOD – Day 7 | 6–8h | 4h `senior-backend-engineer` (T035, T037, T044, T045) + 1h `architect` (T036) + 1h `security-analyst` (T042) + 0.5h `devops` (T043) + slip-watch overhead | MEDIUM | Day-5 escalation could force scope-cut deliberation |
| **Active total** | Day 1 – Day 8 | **~8 working days** | ~36h owner-hours total | MEDIUM-HIGH | Matches PRD §Timeline 8d active |
| Wave 6 | Day 8+ at `/aod.deliver` | 1–2h | 0.5h `devops` (T046, T048) + 1h `security-analyst` (T047, T049) + 0.5h `product-manager` (T050, async) | HIGH | Manual operator gates; not on critical path |
| **Buffer** | Day 9 – Day 10 | 16h | — | — | Hard ceiling per PRD; reserve for slip-watch scope-cut implementation, CI iteration, or ADR review re-cycle |

### Critical-path narrative

```
Day 1: Wave 0 (1h) → Wave 1 (3h) → Wave 2 starts
       │  setup + foundational complete by EOD
       │  Q-1 outcome locked; baseline benchmark in runlog

Day 2: Wave 2 (6h) test authorship complete
       │  G2 quality gate: tests fail against pre-merge baseline
       │  Wave 3 begins late Day 2

Day 3-4: Wave 3 implementation (Streams 1+2+3+4 partial)
        │  T015→T016→T017→T018→T019→T020→T021 strict ordering
        │  T022→T023+T024–T027 Stream 2
        │  T028–T031 Stream 3 interleaved
        │  T032 (depends T006+T007), T033 (depends T005), T034 (independent)

Day 4-5: Wave 4 baseline + test execution
        │  T014 baseline regen (post-Stream-1)
        │  T039 local pytest green
        │  T040 CI matrix green
        │  G4 gate

Day 5 EOD: G5 slip-watch — CRITICAL
          │  If G4 not crossed, T041 fires PM escalation
          │  Scope cuts in priority order; hard floor preserved

Day 5-7: Wave 5 ADR Accepted + polish
        │  T035 benchmark amendment to ADR
        │  T036 architect promotes Proposed → Accepted
        │  T037 PR retitle
        │  T042 manual smoke test (security-analyst)
        │  T043–T045 pre-merge checks

Day 8: PR ready for review/merge → /aod.deliver

Day 8+: Wave 6 post-merge (manual gates)
       │  T046 squash-merge → T047 vulnlog → T048 release-please verify → T049 re-scan
       │  T050 LinkedIn (PM discretion, NOT DoD-gating)
```

### Slip risk register

| Risk | Likelihood | Impact | Mitigation Wave |
|---|---|---|---|
| T021 NFR-004 delta >50% | LOW | HIGH (PM re-scope) | Wave 3 G3 |
| Test-2 corpus expansion drift (≥13 → 20+ cases) | MEDIUM | MEDIUM (Wave 2 + Wave 4 inflation) | Wave 5 G5 scope cut |
| CI matrix flake on macOS 3.2.57 | MEDIUM | MEDIUM (Wave 4 iteration) | Buffer Day 9 |
| `architect` slow to promote ADR-038 | LOW | MEDIUM (blocks PR merge) | Wave 5 G6 — pre-schedule architect review at Day-5 EOD |
| release-please skip post-merge | LOW (RESOLVED via R12) | LOW | Wave 6 G8 — empty marker fallback documented in T048 |
| Internal-tooling search surfaces wired consumer (Q-1 Option a fallback) | LOW | LOW | Wave 1 G1 — T033 branches; canonical-13 path pre-designed |

---

## 6. Sign-Off Chain Summary (Triad Governance)

| Artifact | PM | Architect | Team-Lead | Status |
|---|---|---|---|---|
| `spec.md` | APPROVED 2026-05-03 | — | — | DONE |
| `plan.md` | APPROVED 2026-05-03 | APPROVED 2026-05-03 | — | DONE |
| `tasks.md` | APPROVED 2026-05-03 | APPROVED 2026-05-03 | APPROVED_WITH_CONCERNS 2026-05-03 | DONE |
| `agent-assignments.md` | — (informed) | — (informed) | **APPROVED** (this doc) | **DONE** |
| ADR-038 (Proposed) | — | — (Wave 3 T034 by senior-backend-engineer) | — | PENDING Wave 3 |
| ADR-038 (Accepted) | — | **APPROVE required** (Wave 5 T036) | — | PENDING Wave 5 |
| PR #249 squash-merge | (informed) | (informed) | — | PENDING `/aod.deliver` |

**Triad veto reservations** (per `.claude/agents/_README.md`):
- `product-manager` may veto on scope drift (esp. Test-2 corpus growth beyond 20 cases)
- `architect` may veto on ADR-038 §Decision residual-scan regex change without lockstep commitment update
- `team-lead` may veto on timeline if NFR-004 >50% delta or Day-5 slip-watch breach

---

## 7. Notes & Concerns Folded From `tasks.md` Team-Lead Review

The team-lead `APPROVED_WITH_CONCERNS` sign-off on `tasks.md` named one HIGH concern that is folded into these assignments:

1. **F-1→F-2 pattern-vs-function reuse contract (Team-Lead Pass 1 H-2)** — Folded into `T034` (ADR-038 Proposed authorship): the §Consequences section MUST explicitly document that F-2 (BLP-02 Wave 2 — defaults.env strict KV parser) reuses the *validation triplet pattern* (regex-validate → reject-on-mismatch → `printf -v` assignment), NOT the `aod_init_read_validated` function itself. The function is interactive `read -p`-only; F-2 is non-interactive file-parse. **`architect` MUST re-confirm this paragraph during T036 review before promoting Status to Accepted.**

2. **Day-5 slip-watch named (T041)** — Tracked as G5 above. Hard floor on Test-1 + Test-2 cases 1–6 preserved.

3. **[MANUAL] flag correctness** — Verified: T042, T044–T050 carry `[MANUAL]` correctly; not in build flow.

---

## 8. Anti-Patterns Avoided

Per team-lead success criteria in `.claude/agents/team-lead.md`:

- **Did NOT execute workflows directly**: orchestrator NOT invoked because single-agent serial mode obviates wave dispatch (per PRD §Timeline). When orchestrator is needed in future features, will hand off via approved assignments.
- **Did NOT skip feasibility for "urgent" requests**: F-248 already has full Triad sign-off; this doc enacts the team-lead governance role.
- **Did NOT overload single agent with sequential tasks**: `senior-backend-engineer` workload = 66% (33/50). `tester`, `architect`, `security-analyst`, `devops`, `product-manager` carry meaningful gating ownership.
- **Did NOT sign off without completion validation**: 8 quality gates (G0–G8) named; sign-off authority assigned per gate.
- **Did NOT invent generic agent labels**: All 13 agent names in §1 sourced verbatim from `.claude/agents/_README.md` v2.0.0. Zero `file-agent`, `doc-agent`, `qa-agent` strings in this document.

---

## 9. Hand-Off Protocol

### To `senior-backend-engineer` (primary executor)

**Provide**:
- Feasibility: APPROVED (PRD timeline 8d active matches Wave 3 estimate)
- This document at `specs/248-substitution-surface-hardening/agent-assignments.md`
- Wave sequencing model: single-agent serial with named hand-offs
- Critical path: T015 → T016 → T017 → T018 → T019 → T020 → T021 → T014 → T039 → T040 → T036 → T042 → ready for `/aod.deliver`

### To `tester` (Wave 2 + T039)

**Provide**:
- 5 task specs (T009–T013) with file paths and assertion contracts
- Constitution VI test-first invariant (G2 gate): tests must fail against pre-merge baseline before Wave 3 implementation begins
- Adversarial corpus minimum: ≥13 cases per T010, INCLUDING M-1 trailing-newline edge cases (case 13)

### To `architect` (T036)

**Provide**:
- Pre-scheduled review slot at Wave 5 mid-cycle (Day 5–6)
- Two specific review surfaces in ADR-038:
  - §Decision: residual-scan regex character class `[A-Z_]+` + lockstep-update commitment (M-2)
  - §Consequences: F-1→F-2 pattern-vs-function reuse contract (H-2) + T021 benchmark numbers + NFR-004 disposition
- Authority: promote Status `Proposed → Accepted` only on confirmation of both surfaces

### To `security-analyst` (T042 + T047 + T049)

**Provide**:
- T042 quickstart.md §Adversarial Smoke Test path: `/tmp/tachi-smoke-test`
- T042 4 invariants to verify: AT&T literal substitution count > 0; zero residuals; gitignore; constitution byte-equality
- T047 5 vuln_ids with severity bands: TACHI-VULN-6bc17fd01ac8 (HIGH), TACHI-VULN-77f0519f9cfb (MEDIUM), TACHI-VULN-bc67ca510ea9 (MEDIUM), TACHI-VULN-30bbfd90959a (LOW), TACHI-VULN-18127be5d214 (LOW)
- T049 re-scan target surface: `scripts/init.sh`, `.gitignore`, `.aod/templates/constitution-*.md`, `contracts/personalization-schema.md`, `.claude/mcp-config.json` (if Option a)

### To `devops` (T040 + T043 + T046 + T048)

**Provide**:
- T040 CI matrix expectation: macos-latest + ubuntu-latest both green; existing GitHub Actions workflow; no new workflow file
- T043 expected PR title: `feat(248): harden init.sh substitution surface — sed → bash param expansion + input validation + gitignore default`
- T046 squash-merge command + post-merge `git push origin main`
- T048 release-please verification: `gh pr list --state open --search "release-please" --limit 3`; if empty, push empty marker `feat(248): substitution surface hardening — release marker`

### To `product-manager` (T041 escalation arbiter + T050)

**Provide**:
- T041 escalation contract: invoked only if G4 not crossed by EOD Wed 2026-05-08; scope cuts in priority order; hard floor preserved
- T050 LinkedIn comment template (in tasks.md); within 5 business days of release-please PR merge; PM-controlled, NOT DoD-gating

---

## 10. Receiving from Executor (Completion Reports)

Upon Wave 5 G7 close, `senior-backend-engineer` (or coordinating agent) MUST return to `team-lead`:

- Completion report with metrics (estimated 8d vs actual)
- Blocker summary (if any slip-watch escalations fired)
- Ready-for-`/aod.deliver` confirmation
- All 14 DoD items checked
- All 50 tasks marked `[X]` in tasks.md
- No `.aod/` modifications outside scope (NFR per `.aod/results/` policy)

`team-lead` validates before final sign-off and hands off to operator for `/aod.deliver` execution (Wave 6).

---

**End of Agent Assignments — F-248 Substitution Surface Hardening (BLP-02 Wave 1)**
