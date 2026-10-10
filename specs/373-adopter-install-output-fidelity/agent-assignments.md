# Agent Assignments: F-373 Adopter Install + Output Fidelity Fixes

**Feature**: #373 · **Draft PR**: #375 (`fix(373):`) · **Branch**: `373-adopter-install-output-fidelity`
**Source**: `specs/373-adopter-install-output-fidelity/tasks.md` revision 2 (T001–T040)
**Estimate**:
- effort: 8.3 attention-days;
- duration: 3.5 / 5.2 / 7.7 d (floor / central / ceiling);
- TW-0: 5.21 d against 5.5 d, not fired (tasks.md § Trip-Wire Evaluation).

**Wave plan**: five `/aod.build` waves, where build wave N is tasks.md wave W(N−1). They run in two sessions, plus a conditional T040.
**Assignee roster**: `senior-backend-engineer`, `devops`, `tester`, `security-analyst`, `code-reviewer`, `architect`, `product-manager`, `orchestrator`. `debugger` joins on escalation only.

> **Where the agent names come from.** Every assignee is an exact name from `/aod.tasks` Step 6's assignable roster (`.claude/agents/_README.md`), with no generic labels.
> - The team-lead is the assigner, never an assignee.
> - Its trip-wire rulings (T039, and T033's TW-7) are checkpoints the `orchestrator` invokes, the way `/aod.build` invokes the `architect` at P0/P1/P2.

> **Why `senior-backend-engineer` writes the tests.** This repo's `tester` agent is a BDD/Gherkin specialist, and its boundary is "writes tests only, does not implement application features or fix bugs".
> - This bundle's gated suites are raw pytest modules, wired into GitHub Actions in lock-step, so `senior-backend-engineer` instances write them, along with every fixture, golden and product file. This follows the F-362 T017 precedent.
> - `tester` runs validation scenarios: the live render sessions, T033's N4 re-run, and the render set if K14 rides early. It records them, and it edits no product file.

> **Dispatch rule.** Each lane is a separately dispatched instance with its own file set. Never merge two lanes of the same agent type into one call. That would serialize the wave and break the rule of one writer per file per wave.

---

## 1. Agent Assignment Matrix

### Instances

| Instance | `subagent_type` | Writes |
|---|---|---|
| SBE-A | `senior-backend-engineer` | Lane A content: manifest, README, developer guide, the completeness module, the PD-8 fixture edit (W1); the README K3 section (W2); close-out docs (W4) |
| SBE-B | `senior-backend-engineer` | T001 (W0); Lane B1 (W1) and any revert T039 orders; Lane B2a (W2); T035's `oracle-diff.md` (W3) |
| SBE-C | `senior-backend-engineer` | T002 (W0); Lane C1, including T014's module (W1); Lane C2 (W2) |
| SBE-D | `senior-backend-engineer` | Lane B2b (W2) |
| SBE-T | `senior-backend-engineer` | The test lane: T003 (W0); T008 for Lane A′ (W1); T019, T023, T029, T031's tests and T032 (W2) |
| SBE-W3 | `senior-backend-engineer` | The single W3 writer: the text iterations, the 2K flip, TW-6 reverts, T032 re-runs, and any Python or Typst fix |
| DEVOPS-A | `devops` | The fast workflow (A-1 job, A-2 job, A-3 and the W2 wiring commits); T034 (W3) |
| DEVOPS-K3 | `devops` | `install.sh` and the `tachi-pytest.yml` wiring (W1); K3 convergence (W2) |

### Phase 1: Setup (build wave 1 = W0)

| Task | Story | Lane | Agent (`subagent_type`) | [P] | Notes |
|---|---|---|---|---|---|
| T001 | Setup | — | `senior-backend-engineer` (SBE-B) | [P] | Pre-state and oracle pre-snapshot in a scratch clone, with stderr captured |
| T002 | Setup | — | `senior-backend-engineer` (SBE-C) | [P] | Eight-call W0 smoke. Key per NFR-5. Decides `IMAGE_SIZE_RESTORED` |
| T003 | Setup | test lane | `senior-backend-engineer` (SBE-T) | [P] | Fixtures and sandbox builders. The builders go in their own commit, for T040 |

A task sits in the wave where it **completes**, because `/aod.build` counts completion per wave from this file. Where work starts a wave earlier, the Notes column says so.

### Build wave 2 (W1): 13 tasks

| Task | Story | Lane | Agent (`subagent_type`) | [P] | Notes |
|---|---|---|---|---|---|
| T004 | US1 | A | `senior-backend-engineer` (SBE-A) | | Manifest and manual-install blocks, between the `MANUAL INSTALL LOOP` markers |
| T005 | US5 | A | `senior-backend-engineer` (SBE-A) + `devops` (DEVOPS-A) | | The module (SBE-A). The workflow, the A-1 push and the #375 check (DEVOPS-A). **The cut line** |
| T006 | — | A | `devops` (DEVOPS-A) + `senior-backend-engineer` (SBE-A) | | The A-2 job, triage and quarantine markers (DEVOPS-A). The PD-8 fixture edit (SBE-A) |
| T007 | — | B1 | `senior-backend-engineer` (SBE-B) | | PD-6 splitter; keeps the bare fallback |
| T008 | US2 | A′ | `senior-backend-engineer` (SBE-T) | [P] | K3 pytest harness, negatives first, with the local red run recorded. It lands in T010's lock-step commit, which DEVOPS-K3 makes at the end of this wave |
| T009 | US2 | A′ | `devops` (DEVOPS-K3) | | `install.sh` pre-flight on bash 3.2, with P-11.1's help text. It also lands in T010's lock-step commit, which is pushed after A-1 is green |
| T012 | US4a | C1 | `senior-backend-engineer` (SBE-C) | [P] | After T002 |
| T013 | US4a | C1 | `senior-backend-engineer` (SBE-C) | [P] | After T002. If AR-2's decision 2 holds the executive-architecture config, A-3 lands without A3 |
| T014 | US4a | C1 + A | `senior-backend-engineer` (SBE-C) + `devops` (DEVOPS-A) | | The A1–A8 module (SBE-C). The A-3 wiring (DEVOPS-A) |
| T016 | US3a | B1 | `senior-backend-engineer` (SBE-B) | [P] | In its own worktree. K12 counts over the normalized map (NM-1), and the same commit updates both call sites |
| T020 | US3b | B1 | `senior-backend-engineer` (SBE-B) | | K11 parser and join wiring, in its own commits |
| T024 | US3c | B1 | `senior-backend-engineer` (SBE-B) | | The posture function, in its own commit |
| T039 | Checkpoint | — | `orchestrator` + `senior-backend-engineer` (SBE-B) | | **Closes wave 2.** The orchestrator invokes the team-lead's TW-0/1/2 ruling, and SBE-B makes any revert it orders. Wave 3 starts after it |

### Build wave 3 (W2): 16 tasks, after T039

| Task | Story | Lane | Agent (`subagent_type`) | [P] | Notes |
|---|---|---|---|---|---|
| T010 | US2 | A′ → A | `devops` (DEVOPS-K3) | | Its lock-step commit landed at the end of wave 2. Here it converges both OS legs, and it completes when both are green |
| T011 | US2 | A | `senior-backend-engineer` (SBE-A) + `security-analyst` | | The README K3 section (SBE-A). An advisory review scoped to the bash code (`security-analyst`) |
| T017 | US3a | B2a + B2b | `senior-backend-engineer` (SBE-B) + `senior-backend-engineer` (SBE-D) | | K12 wiring (`apply_delta_status` for badges and `top_findings` only), K13.1 per tier, and the sweep |
| T018 | US3a | C2 | `senior-backend-engineer` (SBE-C) | [P] | |
| T019 | US3a | test lane | `senior-backend-engineer` (SBE-T) | | Regression and parity, with absolute Section 7 tallies on the mismatch fixture |
| T021 | US3b | B2a | `senior-backend-engineer` (SBE-B) | | K11 funnel and S-9 |
| T022 | US3b | C2 + B2b | `senior-backend-engineer` (SBE-C) + `senior-backend-engineer` (SBE-D) | [P] | The text (SBE-C). The caption (SBE-D) |
| T023 | US3b | test lane | `senior-backend-engineer` (SBE-T) | | |
| T025 | US3c | B2a + B2b + A | SBE-B + SBE-D (`senior-backend-engineer`) + `devops` (DEVOPS-A) | | Emission (SBE-B). Typst and the posture module (SBE-D). The `report-posture` job (DEVOPS-A) |
| T026 | US3c | C2 | `senior-backend-engineer` (SBE-C) | [P] | |
| T027 | US4b | B2a | `senior-backend-engineer` (SBE-B) | | `allow_list`, with its hunks kept apart from T025's |
| T028 | US4b | C2 | `senior-backend-engineer` (SBE-C) | | |
| T029 | US4b | test lane | `senior-backend-engineer` (SBE-T) | | |
| T031 | US6 | test lane + B2b | `senior-backend-engineer` (SBE-T) + `senior-backend-engineer` (SBE-D) | | The tests (SBE-T). The docstring (SBE-D) |
| T032 | Polish | test lane | `senior-backend-engineer` (SBE-T) | | Wave-final. One golden commit per K-item |
| T033 | Polish | — | `architect` + `tester` + `orchestrator` | | **End of wave 3.** The P0 checkpoint (`architect`), the N4 re-run (`tester`), and the TW-7 ruling (the `orchestrator` invokes the team-lead) |

### Build wave 4 (W3): 5 tasks · Build wave 5 (W4): 2 tasks

| Task | Story | Lane | Agent (`subagent_type`) | [P] | Notes |
|---|---|---|---|---|---|
| T015 | US4a | render | `tester` + `senior-backend-engineer` (SBE-W3) | | Wave 4. One render session with T030 (`tester`, with the maintainer). The 2K flip (SBE-W3) |
| T030 | US4b | render | `tester` + `senior-backend-engineer` (SBE-W3) | | Wave 4. Renders, judgment and records (`tester`). Text iterations and TW-6 reverts (SBE-W3) |
| T034 | Polish | A | `devops` (DEVOPS-A) | | W3 integration. The render session starts from this commit while CI runs |
| T035 | Polish | — | `senior-backend-engineer` (SBE-B) | | The oracle diff, including NM-1's 4/0/82 mover |
| T036 | Polish | — | `code-reviewer`, then `architect` | | The P1 checkpoint. Fixes by SBE-W3 |
| T037 | Polish | A/B docs | `senior-backend-engineer` (SBE-A) + `architect` | [P] | Wave 5. The docs and PR body (SBE-A). The ADR-014 note (`architect`) |
| T038 | Polish | — | `product-manager` | [P] | Wave 5. Release notes (P-11.1, P-11.2) |

### Conditional (outside every wave)

| Task | Story | Lane | Agent (`subagent_type`) | Notes |
|---|---|---|---|---|
| T040 | — | — | `devops` + `tester` + `product-manager` | **Only if T033 fires TW-7.** The early Group A PR, in its own worktree. `tester` handles the render set if K14 rides, and `product-manager` the early notices. **If TW-7 does not fire**, mark T040 `[X]` with the note "not triggered", so no wave-completion check stalls on it |

### Workload

Participations by agent type (a task with several agents counts once for each):

| Agent | Participations |
|---|---|
| `senior-backend-engineer` | 33 |
| `devops` | 8 |
| `tester` | 4 |
| `architect` | 3 |
| `orchestrator` | 2 (checkpoints) |
| `product-manager` | 2 |
| `security-analyst` | 1 |
| `code-reviewer` | 1 |

All 40 tasks are assigned.

### Escalation triggers and overrides

| Task | Trigger | Action |
|---|---|---|
| T002 | A model is unreachable, or returns a status other than 404 or 403 | P-10.1: diagnose and retry within TW-6's budget. Record the "other status" for the `architect` (AR-2). It is non-blocking, and W1 is never held |
| T006 | A pre-existing red on bare ubuntu is still unattributed after 0.15 d | Escalate to `debugger`. The quarantine markers cite a follow-up issue |
| T013 | 3:4 failed at W0 | Hold executive-architecture's configuration for the `architect` (AR-2 decision 2). A-3 lands without A3 |
| T039 | The ruling orders a carve | SBE-B reverts the named commits and verifies them in a scratch clone of the revert commit. Build wave 3 launches only after that |
| T030 | TW-5: residual leakage after two iterations | File a follow-up issue (after `export AOD_REPO=davidmatousek/tachi`) |
| T030 | TW-6: renders blocked for more than 0.5 d | SBE-W3 runs the late-carve procedure. K14 keeps T015 (P-10.2) |
| T033 | TW-7 fires | Run T040 |
| T036 | The review or T035 requires a code fix | SBE-W3 fixes it after the render session. Re-run T032 or T035 if an output changes |
| T011, T036 | Always | The dispatch prompt scopes the review to executable code, overriding the knowledge-system supplement's "no application code" framing |
| Every reviewer | Always | The prompt carries the #365 rule: no pytest or extractors in the main tree; scratch clone only; `git status --short` afterward |

---

## 2. Parallel Execution Waves

```
SESSION 1: build waves 1–3 (W0–W2), ≈3.05 d of windows; ends at T033
│
├─ Wave 1 (W0)   T001 ∥ T002 ∥ T003                                   [SBE-B, SBE-C, SBE-T]
│
├─ Wave 2 (W1)   all four lanes launch at the wave's start; only commits are gated
│   ├─ Lane A    T004 → T005 (A-1: scratch-clone check, push, green on #375) → T006 (A-2) → A-3 (T014 wiring)   [SBE-A, DEVOPS-A]
│   ├─ Lane A′   T008 (negatives first) → T009 → T010 one lock-step commit, pushed after A-1 is green            [SBE-T, DEVOPS-K3]
│   ├─ Lane B1   in its own worktree: T007, T016, then T020 and T024 in stand-alone commits; replayed once A-2 is green  [SBE-B]
│   └─ Lane C1   T012 ∥ T013 → T014's module; commits after A-1 is green                                        [SBE-C]
│   └─ T039      checkpoint: the orchestrator invokes the team-lead ruling; any revert by SBE-B, verified. Wave 3 waits for it
│
├─ Wave 3 (W2)   after T039
│   ├─ Lane A    T010 convergence [DEVOPS-K3]; T011 [SBE-A + security-analyst]; wiring commits [DEVOPS-A]
│   ├─ B2a       T017 (part) → T025 emission → T021 → T027                                   [SBE-B]
│   ├─ B2b       T017 → T025 Typst and module → T022 caption → T031 docstring                 [SBE-D]
│   ├─ C2        T018 → T026 → T022 → T028                                                    [SBE-C]
│   └─ Test lane T019 → T023 → T029 → T031 tests                                              [SBE-T]
│   └─ T032 (goldens, one commit per K-item) → T033 (P0; N4 re-run; TW-7) → [T040 only if TW-7 fired]
│
SESSION 2: build waves 4–5 (W3–W4), ≈1.16 d of windows
│
├─ Wave 4 (W3)   T034 (commit and push; CI runs) → render session T030 → T015 [tester + SBE-W3]
│                ∥ T036's code review → T032 re-run if text changed [SBE-W3] → T035 [SBE-B] → T036's architect checkpoint (P1)
│
└─ Wave 5 (W4)   T037 [SBE-A + architect] ∥ T038 [product-manager] → P2 → /aod.deliver
```

### Dependency edges this map enforces

| Edge | Source | Where |
|---|---|---|
| A-1 green → every other W1 commit | P-9.1 | inside wave 2 |
| A-2 committed and its job green → B1's commits (except its marker-only first commit) | N9, the R-3 net, LOW-6 | inside wave 2 |
| T002 → T012, T013 | L1 | wave 1 → 2 |
| T007 → T022, T026, T028 (T013 may skip a triage-only hold) | PD-6 | wave 2 → 3 |
| T016 → T020 → T024, with T020 and T024 in stand-alone commits | the B1 sequence; NM-2 | inside wave 2 |
| W1's last lane → T039 → every W2 task | NM-2 | wave 2 → 3 |
| T032 → T033 → the session break | the goldens before the P0 checkpoint | end of wave 3 |
| T034's commit → the render session → T032 if text changed → T035 → T036 | L7 | inside wave 4 |
| T033 (TW-7 fired) → T040 | RC-T1 | after wave 3 |

The critical path runs W0 → the A-1 gate → Lane A′ → T039 → the test lane and B2a → T032 → T033 → T034 → the render session → T035 → T036 → T037/T038.

B1 is near-critical, about 0.2 d behind A′. K3's CI cycles have about 0.5 d of float to T034 at central; the ceiling consumes it.

---

## 3. Checkpoints and quality gates

### Checkpoint map

This map follows plan.md, which puts the architect's P0 at the end of W2. For this feature it replaces `/aod.build` Step 2c's generic wave numbers: after build wave 2 the orchestrator runs T039, not an architect review.

| Checkpoint | After build wave | Invoked by the orchestrator | Scope | Blocking |
|---|---|---|---|---|
| **T039** trip-wire re-check | 2 (W1) | the team-lead ruling; any revert by SBE-B | TW-0, TW-1 and TW-2 with actuals; carve in the fixed order | **Yes.** Wave 3 launches only after the ruling and any revert |
| **P0** (Go/No-Go) | 3 (W2) | the `architect` (T033) | parser semantics; goldens by file name; oracle rules; the AR-2 record; N4 attribution | **Yes** |
| **TW-7** | 3 (W2) | the team-lead ruling (T033) | remaining work over 2.0 d, or any lane more than 50% over budget | Decides T040; ends Session 1 |
| **P1** (production cutover) | 4 (W3) | `code-reviewer`, then the `architect` (T036) | full-diff review; the render records; oracle attribution; CI visibly green | **Yes** |
| **P2** (pre-final) | 5 (W4) | the `architect` | a read of T037 and T038 before `/aod.deliver` | No |

### Quality gates between waves

| Boundary | Gate | Type | On failure |
|---|---|---|---|
| Wave 1 → 2 | T001's pre-state, with literal totals and stderr; T002's smoke record, with `IMAGE_SIZE_RESTORED` and the 3:4 check; T003's fixtures, with the sandbox builders in their own commit | Blocking prerequisite | No product edit happens before the pre-state exists |
| Inside wave 2 | A-1 green on #375 before any other commit. A-2's job green, or quarantined, before B1's commits (B1's marker-only first commit excepted). A′'s lock-step commit only after A-1 is green, with the completeness end-to-end case re-run in a scratch clone. A-3 last | Commit-order gates | A red cut-line job stops every other commit |
| Wave 2 → 3 | T039's ruling in `test-results/w1-exit-checkpoint.md`; any ordered revert made by SBE-B and verified; the fast workflow green; K3's first 2-OS run recorded; the wave-2 gated set green (§ 4); the NEXT-SESSION snapshot written | **Blocking checkpoint** | No wave-3 task starts before the ruling |
| End of wave 3 (P0, TW-7) | T032's golden commits, one per K-item; T033's P0 approval; the N4 re-run attributed; the TW-7 ruling (T040 if it fired); `NEXT-SESSION.md` | Blocking; ends Session 1 | CHANGES_REQUESTED sends the fix to the owning lane before Session 2 |
| Wave 4 (P1) | See the list below | Blocking | An unattributed delta stops the build before wave 5 |
| Wave 5 → deliver (P2) | the ADR-014 note; the CHANGELOG; the PR body per R-T1; `release-notes-upgrading.md`; the #364 draft | Non-blocking review | Hands off to `/aod.deliver` |

The wave-4 (P1) gate needs all of these:
- CI is visibly green: every fast-workflow job, both `tachi-pytest.yml` legs, and the co-fired gates;
- the K14 render set: 6 of 6 templates, the fallback model, and executive-architecture on one portrait page. A blocked model gets its P-9.2 or P-10.1 record instead;
- K15's renders within two iterations, or TW-6's carve;
- `oracle-diff.md` 100% attributed, including `agentic-app/sample-report` at 4 NEW / 0 UPDATED / 82 UNCHANGED;
- the code review and the architect's W3 checkpoint.

---

## 4. Post-wave tests (LOW-2)

**Why not the default.** `/aod.build` sub-step 4.5 would run the full `pytest` (`testpaths = ["tests"]`) in the main tree. That re-renders tracked `examples/**` PNGs (#365) and hits about 19 pre-existing reds outside the gate. Sub-step 4.6 would generate modules that no workflow gates, which NFR-7 forbids.

**The rule.**
- Run `/aod.build --no-tests`, and record the reason in each wave's results: "#365 PNG hazard; NFR-7".
- Run this gated set as each wave's gate, in a scratch clone of the wave commit.
- Record totals in `specs/373-adopter-install-output-fidelity/test-results/wave-0N/results.json`, with `test_runner` set to the commands below, as F-362 did.

```bash
SCR="$SCRATCH/wave-$N"
git clone --no-hardlinks /Users/david/Projects/tachi "$SCR" && cd "$SCR"   # the committed wave HEAD only

# The fast workflow: include each module once it is wired
#   completeness: from A-1; the five extraction modules: from A-2;
#   the contract module: from A-3; sibling parity: from wave 3
python3 -m pytest \
  tests/scripts/test_install_manifest_completeness.py \
  tests/scripts/test_tachi_parsers.py \
  tests/scripts/test_extract_infographic_data.py \
  tests/scripts/test_extract_report_data.py \
  tests/scripts/test_extractor_contract_fixes.py \
  tests/scripts/test_executive_architecture_payload.py \
  tests/scripts/test_gemini_request_contract.py \
  tests/scripts/test_extraction_sibling_parity.py \
  -v

# The report-posture job (wave 3 on), only where typst is on PATH; otherwise CI's job is the gate
TACHI_REQUIRE_TYPST=1 python3 -m pytest tests/scripts/test_report_posture_contract.py -v

# tachi-pytest.yml's gated subset: exactly the modules in its pytest invocation at this commit
# (16 today; 18 once T010 adds the two K3 modules). On macOS this runs the /bin/bash 3.2 leg locally.
python3 -m pytest <the modules listed in .github/workflows/tachi-pytest.yml> -v --timeout=1080
```

**Per wave:**

| Wave | Gate |
|---|---|
| 1 | T001's pre-state is the record |
| 2 | The completeness module, the five extraction modules, the contract module, and the `tachi-pytest.yml` subset with the K3 modules |
| 3 | All of the above, plus sibling parity and the posture module |
| 4 | The full gated set on the W3 commit, and CI visibly green (T034) |
| 5 | Docs only: no run |

Compare every result with T001's pre-state. Nothing ever runs in the main tree.

---

## 5. Time estimates per wave

Attention-days are the per-task figures in tasks.md. Window = the pacing chain × 1.25. Dates count working days from Monday 09-28.

| Build wave | tasks.md wave | Tasks | Effort | Pacing chain | Window | Runs |
|---|---|---|---|---|---|---|
| 1 | W0 | T001–T003 | 0.40 | 0.20 (T003) | 0.25 | Mon 09-28 |
| 2 | W1 | T004–T009, T012–T014, T016, T020, T024, T039. T010's lock-step commit also lands here | 3.47 | 1.20 (A′ → T039) | 1.50 | Mon 09-28 → Tue 09-29 |
| 3 | W2 | T010 (convergence; it completes here), T011, T017–T019, T021–T023, T025–T029, T031–T033 | 3.14 | 1.04 (test lane → T032 → T033) | 1.30 | Tue 09-29 → Wed 09-30 / Thu 10-01 AM |
| 4 | W3 | T015, T030, T034–T036 | 1.10 | 0.78 | 0.975 | Thu 10-01 → Fri 10-02 AM |
| 5 | W4 | T037, T038 | 0.20 | 0.15 | 0.19 | Fri 10-02 |
| — | conditional | T040 | 0.25–0.50 | — | — | End of Session 1, only if TW-7 fires |
| | | **Σ** | **8.31** | **3.37** | **4.21** | |

**Projected duration**: 4.21 d of windows + 1.0 d for plan and deliver = **5.21 d**. That puts M4 on Fri 10-02, with about 0.3 d of slack. Calibrated realistically, it is Mon 10-05, still inside the PRD ceiling of Tue 10-06.

**Human input**: the maintainer's visual checks, about 1 hour on the afternoon of Thursday 10-01, with 30 minutes in reserve on the morning of Friday 10-02.

---

## 6. Load check

**Model**: an instance's wave load = its attention-days in the wave ÷ the wave window. The pacing lane sits at no more than 80% by construction.

| Wave | Peak instance | Peak load | Others |
|---|---|---|---|
| 1 | SBE-T (T003) | **80%** | SBE-B 60%; SBE-C 20% |
| 2 | SBE-B (B1) | 65% | DEVOPS-K3 48%; SBE-C 39%; SBE-A 37%; SBE-T 30%; DEVOPS-A 11% |
| 3 | SBE-T (with T032) | 70% | SBE-B 55%; SBE-D 42%; SBE-C 38%; DEVOPS 18%; `security-analyst` 8%; `architect` 5%; SBE-A 4%; `tester` 2% |
| 4 | `tester` (the render session) | 44% | DEVOPS-A 21%; SBE-B 21%; SBE-W3 15%; `code-reviewer` 10%; `architect` 5% |
| 5 | SBE-A (T037) | 64% | `product-manager` 27%; `architect` 16% |

- **No instance exceeds 80%.** The capacity veto is not exercised.
- **Wave 3 is at the solo-curator cap:** four heavy lanes (B2a, B2b, C2 and the test lane) plus Lane A in the background. Do not widen it.
- **The binding constraint is serial verification, not agent capacity.** That means the ~25-minute 2-OS CI cycles, the checkpoints, and the maintainer's visual checks in wave 4.

---

## 7. Sign-off

**Team-lead** (the assigner):
- Every task is mapped to an exact roster name.
- The wave map follows every dependency edge in tasks.md § Dependencies, including T039's gate on every wave-3 task.
- Commits for carvable and early-ship items stand alone, so a carve or T040 is mechanical.
- The post-wave tests never touch the main tree.
- Peak load is 80% or below.

**Timeline veto: not exercised. Capacity veto: not exercised.**

Hand off to `/aod.build` with `--no-tests` (§ 4). The dispatch precondition is that T001 records the pre-state before any product edit.
