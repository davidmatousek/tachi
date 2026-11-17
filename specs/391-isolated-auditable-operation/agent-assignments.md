# Agent Assignments: F-391 Isolated and Auditable Operation

**Feature**: #391 · **Draft PR**: #392 · **Branches**: `391-isolated-auditable-operation` (Part A) and `391-isolated-auditable-operation-part-b` (Part B, stacked on Part A; AD-14)
**Source**: `specs/391-isolated-auditable-operation/tasks.md` **v1.1**, 52 tasks: T001–T037, T038a, T038b, T039–T051
**Team-lead verdict on v1.1**: APPROVED_WITH_CONCERNS. The full review is local, in `.aod/results/team-lead-tasks-391.md`, including its v1.1 delta section
**Estimate** (team-lead re-cost against v1.1; tasks.md :192–:196 cites it as governing):
- **Effort**: 7.7 attention-days at task level. Part A 4.9, Part B 2.86. The task figures in v1.1 sum to 6.5.
- **Duration**: 2.9 / 4.7 / 7.5 d (floor / central / ceiling).
- **Trip-wires**:
  - TW-0: 4.74 d against 5.0 d, not fired.
  - TW-B0: Part B 2.86 d against 3.0 d, not fired.
  - TW-A3: bounded, not fired.

**Wave plan**: four `/aod.build` waves in two build sessions, plus two waves that run outside `/aod.build`:
- **W0'** runs before T0, by the maintainer and `tester`.
- **S1**: build wave 1 = W0, and build wave 2 = W1 (five lanes).
- **L**: W2, a live session the maintainer launches.
- **S2**: build wave 3 = W3 (opens with T050), and build wave 4 = W4.

**Assignee roster**:
- `senior-backend-engineer`, `devops`, `web-researcher`, `product-manager`, `architect`, `security-analyst`, `code-reviewer`, `tester` and `orchestrator`;
- `team-lead` for rulings only: T050, and the W1 carve check. The orchestrator invokes it;
- "maintainer (human)" for the [MANUAL] tasks T001 and T020;
- `debugger` on escalation only.

> **Where the names come from.**
> - Every assignee is an exact name from `.claude/agents/_README.md`.
> - The `tachi-*` agents are the subject under test, never assignees.
> - The instance labels in §1 (SBE-x, DEVOPS-x) are dispatch handles. Each maps to exactly one `subagent_type`.

> **Why `senior-backend-engineer` writes the pytest modules.**
> - This repo's `tester` is a BDD/Gherkin specialist.
> - As in F-362 (T017) and F-373, `senior-backend-engineer` test-lane instances write the raw pytest modules that are wired into GitHub Actions in lock-step: SBE-TA on Part A, SBE-TB on Part B.
> - `tester` runs and records validation (T002, T041, T043, T051) and edits no product file.

> **Dispatch and commit rule.**
> - One instance per lane, each with its own file set. Never merge two lanes of the same agent type into one call.
> - Agents never run git. The orchestrator commits each lane's files with `git commit -m "<msg>" -- <explicit paths>`, one commit at a time. Never `git add -A`.
> - Part B files are written only in the part-b worktree (§5).

> **The #365 rule goes in every dispatch prompt.**
> - No pytest and no extractors in the main tree; use a scratch clone of the committed tip only.
> - Check `git -C <clone> log -1` before trusting a result.
> - Run `git status --short` on the main tree after the agent returns.

> **Code reviews** (T034, T042, T044, T049): the prompt scopes the review to executable code and scripts. This overrides the knowledge-system supplement's "no application code" framing.

---

## 0. Reconciliation with tasks.md v1.1

v1.1 applies the earlier fold-ins FI-1..FI-15. This file now adds only the operational readings below. Where they differ from a line in tasks.md, the orchestrator follows them.

| ID | Item | tasks.md v1.1 | This file |
|---|---|---|---|
| R-1 | T050 (G-B2) placement | The lanes table lists T050 in the W4 row (:190). Its task text (:160) and PRD §9 say "start of build session 2" | T050 is the **first item of build wave 3**. It runs before any W3 Part B work |
| R-2 | W3 sequencing | The W3 pacing is 0.35 (:189), and the parallel-example line (:219) reads looser than the dependency list (:173–:175) | The dependency list governs:<br>• T050 → T051 → T035 → T043 → T044;<br>• T021 → T041 and T042;<br>• T043 also waits for T021.<br>The chain is 0.58 d at the re-cost |
| R-3 | SBE-D queue | "T014 ∥ T012" (:171) | SBE-D is one instance, so it works in this order: T012 → T013 → T010 draft → T014 → T022, T024 → T007–T009 → T011 → T018 → T029.<br>T048's W1 part follows BX. The queue is near-critical: T012/T013 gate T023, T014 gates T015, and the T010 draft must precede T023 |
| R-4 | `INSTALL_MANIFEST.md` on part-b | T032 and T039 each commit a whitelist line. Hard rules :35 lists the whitelist lines under T048 | T032 and T039 own their lines. The two writers in W1 are **serialised**: whichever lands first commits before the other edits, and each line goes in the same commit as its script reference |
| R-5 | T005 client-pin writer | No writer named | DEVOPS-R, only if the key-handling patch did not pin the client. It runs `test_gemini_request_contract.py` A1/A5 in a scratch clone |
| R-6 | P0-B0 | "T002 gates B1's launch (P0-B0)" | P0-B0 needs both T002 = PASS **and** the architect's pre-check of the B contracts (0.03 d) before any B code is committed |
| R-7 | BX | "Merge the Part A branch into part-b at the cut line and again before W2" | BX is DEVOPS-E's merge at G1. BX′ repeats it after any T040 fix, before H1. T048's W1 part follows BX |
| R-8 | T030 throwaway branch | "Throwaway branch and PR" | `git branch -D` is denied in this repo. After the PR closes, delete the remote branch and leave the local one to the maintainer |
| R-9 | W1 carve check | — | When T025 + T026 pass 0.80 d combined (central 0.60), the orchestrator invokes the team-lead ruling. That ruling may carve C6, following TW-0's carve order |

---

## 1. Instances

| Instance | `subagent_type` | Branch / tree | Writes |
|---|---|---|---|
| SBE-D | `senior-backend-engineer` | Part A (main tree); part-b worktree for T048 | **Lane D**:<br>• `scope.md`, `SECURITY.md`, the README and the developer guide (Part A hunks);<br>• the relocation edits: report-assembler and threat-infographic bodies, the command bodies, the skill references, the templates README, `.gitignore`, `test_coverage_attestation.py`, the developer guide `:1609`;<br>• `scripts/extract-report-data.py` (T014);<br>• `INSTALL_MANIFEST.md` (the Part A line);<br>• the repair hints and the AD-13 dispatch;<br>• the ADR-014/019 notes (T011); the ADR-049 draft (T029); the T010 draft text, handed to SBE-E.<br>**T048** (part-b): the Part B text in shared files |
| SBE-E | `senior-backend-engineer` | Part A | T004 audit; `CLAUDE_PERMISSIONS.md` (§8 in T023; the T010 commit); `scripts/check-agent-privileges.py` (T025) |
| SBE-TA | `senior-backend-engineer` | Part A | Part A test lane: `test_write_confinement.py` (T015), `test_isolated_profile_contract.py` (T017), `test_agent_privilege_guard.py` (T026); the sole writer of `test_install_manifest_completeness.py` (T028) |
| DEVOPS-E | `devops` | both branches | Every workflow edit on both branches; T003 and the AD-14 setup; the BX merges; T030; T046; T047 |
| DEVOPS-R | `devops` | Part A | The runbook (author of T016, T021); the profile pre-stage (T006); the client pin if needed (T005); `release-please-config.json` (T019) |
| SBE-B1 | `senior-backend-engineer` | part-b worktree | Lane B1: the fixtures (T031); the archiver and its whitelist line (T032); `schemas/run-manifest.yaml` (T033); the recorded fixture (T035); the T051 parse |
| SBE-B2 | `senior-backend-engineer` | part-b worktree | Lane B2:<br>• `templates/tachi/VERSION` and the `install.sh` marker block (T036);<br>• the schema reconciliation (T038a) and the drifted examples (T038b);<br>• the stamp script, Step 2.6 and their whitelist line (T039) |
| SBE-TB | `senior-backend-engineer` | part-b worktree | Part B test lane: `test_archive_run_transcripts.py` (T033), `test_tachi_version_marker.py` (T037), `test_threats_schema_contract.py` (T039) |
| SBE-W3A | `senior-backend-engineer` | Part A | W3 fixes that T044 orders on Part A product files. Runbook fixes go to DEVOPS-R |
| — | `web-researcher` | records | T005's comparison; T006's research; T016's citations |
| — | `product-manager` | Part A | • T005: the approval, recorded as PRD v1.4.<br>• T007–T009: D-3 wording reviews.<br>• T016: the framing, program mapping, passivity statement and routes.<br>• T045.<br>• T047: records.<br>• T050: the ruling on the lane clause |
| — | `architect` | records | P0-B0; T016's profile review; T029's review at T040; T040; T044's final checkpoint |
| — | `security-analyst` | records | T049 (Part A); T034; T035's leakage review; T042 |
| — | `code-reviewer` | records | T044 |
| — | `tester` | records | T002, T041, T043, T051. Validation records only |
| — | `orchestrator` | — | Gates, commits and the NEXT-SESSION handoffs; invokes `team-lead` at T050 and at the W1 carve check |
| — | `team-lead` | records | Rulings only: T050 (TW-B2), and the W1 carve check |
| — | maintainer (human) | — | T001, T020, the secret store, and approval prompts |

---

## 2. Agent Assignment Matrix

The Effort column reads tasks.md v1.1's figure → the team-lead's central re-cost, in attention-days. A task sits in the wave where it **completes**.

### W0' (before T0; outside `/aod.build`)

| Task | Story | Lane | Agent | Branch | Effort | Notes |
|---|---|---|---|---|---|---|
| T001 | Setup | B0 | maintainer (human) | scratch project | 0.10 → 0.10 | • **Input**: `examples/ascii-web-api/` if its sample `threats.md` has at least one Critical or High finding, otherwise `examples/free-text-microservice/`.<br>• **Run** without `--skip-report`, so Phase 5 runs and depth 3 is observed.<br>• **None of**: sandbox, `GEMINI_API_KEY`, `/tachi.infographic`, or secrets in the project.<br>• **Copies**: private, outside every work tree, at mode 0700.<br>• **Record**: the tachi version and the private path |
| T002 | Setup | B0 | `tester` | Part A (record) | 0.05 → 0.06 | Checks (a)–(g) at every depth, failing closed. The record is structure-only, because it becomes public. The result gates B1 (P0-B0) |

### W0 (build wave 1, S1)

| Task | Story | Lane | Agent | Branch | Effort | Notes |
|---|---|---|---|---|---|---|
| G0 | gate | — | `orchestrator` | — | — | §4 |
| T003 | Setup | — | `devops` (DEVOPS-E) | Part A + part-b | 0.12 → 0.15 | `git merge origin/main`, never a rebase. Re-verify every file:line anchor at the post-T0 HEAD. Record the pre-state in a scratch clone. Create part-b, its worktree and its draft PR (§5) |

### W1 (build wave 2, S1): five lanes

| Task | Story | Lane | Agent | Branch | Effort | Notes |
|---|---|---|---|---|---|---|
| P0-B0 | gate | — | `architect` | — | new, 0.03 | Pre-check of the B contracts, before any B code commit (R-6) |
| T004 | Found. | E | SBE-E | A | 0.20 → 0.25 | Runs first. Feeds T012, T013, T016, T023 and T025's C7 |
| T005 | Found. | R | `web-researcher` + `product-manager` (approval, PRD v1.4) + DEVOPS-R (client pin, R-5) | A | 0.10 → 0.15 | Checks both prompt paths. Uses R-8's parenthetical verbatim, unless a prompt path proves otherwise |
| T049 | Part A | R (support) | `security-analyst` | A (record) | 0.05 → 0.05 | The Read question on `/proc/self/environ` and `~/.claude/.credentials.json`. A live probe runs only key-less, with a dummy variable. The disposition goes to T016's second commit (or to T021) |
| T006 | Found. | R | `web-researcher` + DEVOPS-R (profile pre-stage) | A | 0.10 → 0.12 | After T005 (no `[P]`). Closes CF-7 |
| T012 | US2 | D | SBE-D | A | 0.15 → 0.18 | Right after T004. Three agent commands; the extractor owns the build directory. Same-commit doc edits include the developer guide `:1609`, `.gitignore` and `test_coverage_attestation.py` |
| T013 | US2 | D | SBE-D | A | 0.05 → 0.05 | Right after T012 |
| T010 | US1 | E | SBE-D (draft) → SBE-E (commit, with T023) | A | 0.05 → 0.07 | Drafted before T023 lands. §3–§5 headings stay byte-exact |
| T014 | US2 | D | SBE-D | A | 0.15 → 0.20 | Adds `--build-dir`, `--remove-build-dir` and `TACHI_MMDC_PUPPETEER_CONFIG`. In SBE-D's queue after T012 and T013 (R-3) |
| T022 | US3 | D | SBE-D | A | 0.02 | AD-13. Body only |
| T024 | US3 | D | SBE-D | A | 0.02 | Repair hints. Lands before BX |
| T007 | US1 | D | SBE-D + `product-manager` (wording) | A | 0.05 | After T005 |
| T008 | US1 | D | SBE-D + `product-manager` | A | 0.05 | The manual-install loop is not edited here; it belongs to T048 |
| T009 | US1 | D | SBE-D + `product-manager` | A | 0.05 | Line `:1609` is T012's. The manual blocks are T048's |
| T011 | US1 | D | SBE-D | A | 0.03 | Part A wording. The manifest sentence is T048's |
| T018 | US2 | D | SBE-D | A | 0.03 | `INSTALL_MANIFEST.md` only, after T016's first commit |
| T029 | US3 | D | SBE-D (draft); `architect` reviews at T040 | A | 0.08 → 0.10 | After T023 and T022. Adds the ADR-list line in `docs/architecture/README.md`. The Part B text is T048's |
| T023 | US3 | E | SBE-E | A | 0.10 | After T004, T005, T012 and T013. Pins the §8 slug, the cell syntax and the §5 table shape |
| T025 | US3 | E | SBE-E | A | 0.35 → 0.40 | After T023 and T016's first commit. Uses v1.1's tokenizer rules |
| T015 | US2 | E | SBE-TA (module) + DEVOPS-E (`report-posture` job + anchor) | A | 0.15 → 0.20 | After T012–T014. Module and wiring in one commit |
| T017 | US2 | E | SBE-TA (module) + DEVOPS-E (`tachi-pytest.yml`) | A | 0.10 | After T016's first commit and T023 |
| T026 | US3 | E | SBE-TA (module) + DEVOPS-E (`tachi-pytest.yml`) | A | 0.15 → 0.20 | After T025. DEVOPS-E serialises its workflow edit with T017's |
| T027 | US3 | E | DEVOPS-E | A | 0.05 | After T025 |
| T028 | US3 | E | SBE-TA (assertions) + DEVOPS-E (anchor) | A | 0.08 → 0.09 | After T018 and T025. The sole writer of the completeness module. Shares a workflow file with T015, so it runs after T015 |
| T016 | US2 | R | DEVOPS-R (author) + `web-researcher` (citations) + `product-manager` (framing, mapping, passivity, routes) + `architect` (profile review) | A | 0.45 → 0.55 | **First commit** after T004, T005, T006 and T023's slug. **Second commit** after T049. The Part B text belongs to T048 |
| T019 | US2 | R | DEVOPS-R | A | 0.02 | `release-please-config.json` only. Runs in parallel with the rest of the wave |
| T031 | US4 | B1 | SBE-B1 | part-b | 0.15 → 0.20 | After P0-B0 |
| T032 | US4 | B1 | SBE-B1 | part-b | 0.60 → 0.85 | Logs actuals at checkpoints T032.1, T032.2 and T032.3. The whitelist line goes in the script's commit, serialised with T039's (R-4) |
| T033 | US4 | B1 | SBE-B1 (schema doc) + SBE-TB (tests) + DEVOPS-E (Part B wiring) | part-b | 0.25 → 0.30 | After T032. DEVOPS-E's first Part B lock-step commit carries the 3.9 step, on `ubuntu-latest` |
| T034 | US4 | B1 | `security-analyst` | records | 0.03 | The refusal path and the redaction design |
| T036 | US5 | B2 | SBE-B2 | part-b | 0.15 → 0.20 | The marker block only. The manual-loop lines are T048's |
| T037 | US5 | B2 | SBE-TB (module) + DEVOPS-E (wiring) | part-b | 0.10 → 0.12 | After T036 (no `[P]`) |
| T038a | US5 | B2 | SBE-B2 | part-b | 0.12 → 0.15 | One commit. Scratch-clone measurements, including CF-21 |
| T039 | US5 | B2 | SBE-B2 (script, Step 2.6 and whitelist line, in one commit) + SBE-TB (contract test) + DEVOPS-E (wiring) | part-b | 0.18 → 0.20 | After T038a. `orchestrator.md` is not touched |
| G1 | gate | — | `orchestrator` + DEVOPS-E | A | — | Cut line (§4) |
| BX | — | — | DEVOPS-E | part-b | new, 0.02 | `git merge 391-isolated-auditable-operation` in the part-b worktree at G1, and again (BX′) after any T040 fix, before H1 |
| T040 | Polish | — | `architect` | records | 0.10 → 0.12 | P0, after G1 and BX (§4). T048's W1 part runs in parallel |

### W2 (session L; outside `/aod.build`)

| Task | Story | Lane | Agent | Branch | Effort | Notes |
|---|---|---|---|---|---|---|
| GL | gate | — | maintainer (human) | — | — | §4 |
| T020 | US2 | — | maintainer (human) | scratch adopter project | 0.60 (TW-A1 cap 1.0) | Follows v1.1's checklist:<br>• the install source and both SHAs;<br>• whether a *file* passed to `--settings` is honoured;<br>• the probes;<br>• the write listing for each configuration;<br>• the run without the key, then with it;<br>• the exact wrapper form;<br>• the SC-B3 field check when Part B is installed;<br>• archiving under the same wrapper.<br>Raw notes stay private. A curated summary goes in `w2-live.md` |

### W3 (build wave 3, S2)

| Task | Story | Lane | Agent | Branch | Effort | Notes |
|---|---|---|---|---|---|---|
| T050 | gate (G-B2) | — | `orchestrator` invokes `team-lead` (ruling); `product-manager` rules on the lane clause | records | 0.03 | **First item of S2** (R-1). Inputs: H1's per-lane actuals |
| T051 | gate (G-B1R) | B1 | `tester` (record) + SBE-B1 (parse) | records | 0.05 | After T020 and T050, and before T035. A failure honest-stops B1 |
| T021 | US2 | R | DEVOPS-R | A | 0.10 | Folds in T020's findings. Writes §11, the stamp, the wrapper form and T049's disposition |
| T030 | US3 | E | DEVOPS-E | throwaway branch + PR | 0.05 | Never on #392 or part-b (R-8) |
| T035 | US4 | B1 | SBE-B1 + `security-analyst` (leakage review) | part-b | 0.20 → 0.25 | After T051 and T021. TW-B4 governs |
| T041 | Polish | — | `tester` | records | 0.10 | After T016 and T021 |
| T042 | Polish | — | `security-analyst` | records | 0.05 | After T021 |
| T043 | Polish | — | `tester` | scratch clones of both tips | 0.15 | After T035 and T021. Includes the 18 `tachi-pytest.yml` modules, the new modules on 3.11 and 3.9, and `test_coverage_attestation.py` |
| T044 | Polish | — | `code-reviewer`, then `architect` | both | 0.15 → 0.20 | Part A first, then part-b. Fixes go to SBE-W3A (Part A), DEVOPS-R (runbook), SBE-B1 or SBE-B2 (part-b). Re-run T043 on any changed tip |

### W4 (build wave 4, S2)

| Task | Story | Lane | Agent | Branch | Effort | Notes |
|---|---|---|---|---|---|---|
| T045 | Polish | — | `product-manager` | A | 0.10 → 0.12 | The CHANGELOG (with the `{out}` precondition line), the release notes and the `delivery.md` preparation |
| T046 | Polish | — | `devops` (DEVOPS-E) | A | 0.10 → 0.12 | After T045. Its steps:<br>(0) the final Wording sweep over the CHANGELOG, the release notes and both PRs' text;<br>(1) `/aod.analyze`;<br>then the split or bundle steps (§5) |
| T048 | Part B | D | SBE-D | part-b worktree | 0.10 | The W1 part runs after BX. The W4 part (the CHANGELOG's Part B lines) runs after T045. **Completes here**. One commit per file, each with a Wording sweep |
| G4 | gate | — | `orchestrator` | — | — | §4 |

### Conditional (outside every wave)

| Task | Story | Lane | Agent | Effort | Notes |
|---|---|---|---|---|---|
| T047 | US4/US5 | — | DEVOPS-E + `product-manager` | 0.10 | **Split path only**, after Part A squash-merges (§5).<br>• On the bundle path, mark it `[X] not triggered`.<br>• If Part B was honest-stopped, mark it `[X] honest-stopped`, naming the trip-wire |
| T038b | US5 | B2 | SBE-B2 | 0.05 | After #364 merges. It runs in S2 if #364 merged before T050, otherwise inside T047 |

**Honest-stop dispositions**, so that no wave-completion check stalls:

- **TW-B1 fails at T002 or at T051**:
  - mark the unfinished B1 tasks `[X] honest-stopped (TW-B1)` (T031–T035, T051);
  - T048 then drops its B1 items (the runbook's archiver text, ADR-049's B1 section, ADR-019's manifest sentence) and keeps the B2 items;
  - B2 continues.
- **T050 defers Part B, or one lane**: mark the unfinished tasks `[X] deferred (TW-B2)`.

---

## 3. Parallel Execution Waves

```
BEFORE T0 (now, while the key-handling patch is pending)
└─ W0'  T001 (maintainer) → T002 (tester): TW-B1 verdict

SESSION S1: build waves 1–2; ≈ 2.0 d of windows; ends at H1
├─ Wave 1 (W0)   G0 → T003 [DEVOPS-E]: merge origin/main, anchor re-check, pre-state, part-b + worktree + draft PR
└─ Wave 2 (W1)   all lanes launch at the wave's start; each lane waits only for its inputs
    ├─ Opening   T004 [SBE-E] ∥ T005 [web-researcher, product-manager, DEVOPS-R]
    │            ∥ T049 [security-analyst] ∥ P0-B0 [architect]; then T006
    ├─ Lane D    T012 → T013 → T010 draft → T014 → T022, T024 → T007, T008, T009 (after T005)
    │            → T011 → T018 (after T016 #1) → T029 (after T023)                                       [SBE-D]
    ├─ Lane E    T023 (after T012/T013, T005) → T010 commit → T025 (after T016 #1)                       [SBE-E]
    │            T015 (after T014) · T017 (after T016 #1) · T026 (after T025) · T028 (after T018, T025)  [SBE-TA + DEVOPS-E]
    │            T027 (after T025)                                                                       [DEVOPS-E]
    ├─ Lane R    T016 #1 (after T006 and T023's slug) → T016 #2 (after T049); T019 ∥
    │                                        [DEVOPS-R + web-researcher + product-manager + architect]
    ├─ Lane B1   (part-b worktree; after P0-B0) T031 → T032.1 → T032.2 → T032.3 → T033             [SBE-B1, SBE-TB, DEVOPS-E]
    │            T034                                                                                    [security-analyst]
    ├─ Lane B2   (part-b worktree; after P0-B0) T036 → T037; T038a → T039                           [SBE-B2, SBE-TB, DEVOPS-E]
    └─ Close     G1 → BX [DEVOPS-E] → T040 [architect] ∥ T048's W1 part [SBE-D] → fixes → BX′ → H1

SESSION L (maintainer)
└─ W2   GL → T020 (macOS with and without the key; Linux VM, or the claim scoped) → archive → H2

SESSION S2: build waves 3–4; ≈ 1.0 d of windows
├─ Wave 3 (W3)   T050 → T051 → T035 (after T021) ─┐
│                T021 → T041, T042 ; T030          ├─→ T043 (both tips) → T044 (Part A, then part-b)
└─ Wave 4 (W4)   T045 → T046 ∥ T048's W4 part → G4 → merge (TW-A2: bundle or split) → /aod.deliver
                 → [T047 and T038b on the split path]
```

### Dependency edges this map enforces

| Edge | Source | Where |
|---|---|---|
| T0 → T003 → every W1 task | the start gate | W0 → W1 |
| T002 PASS + P0-B0 → T031 → T032 → T033; T036 → T037; T038a → T039 | TW-B1; CF-P9 | W0' → W1 |
| T004 → T012 → T013 → T023 (also after T005) → T016 #1 (also after T006) → T025 → T026 / T027 | v1.1 :171–:172 | inside W1 |
| T012–T014 → T015; T016 #1 → T017, T018; T018 + T025 → T028; T015 → T028 (same workflow file) | v1.1; KB Entry 3 | inside W1 |
| T049 → T016 #2; T023 + T022 → T029; T024 → BX | v1.1 | inside W1 |
| T032's and T039's whitelist lines serialised | R-4 | inside W1 (part-b) |
| G1 → BX → T040 ∥ T048 (W1 part) → BX′ → H1 | AD-14; P0 | end of W1 |
| H1 → GL → T020 → H2 → T050 | sessions | W1 → W2 → W3 |
| T050 → T051 → T035 → T043 → T044; T021 → T035, T041, T042, T043 | TW-B2; TW-B1; TW-B4; R-2 | inside W3 |
| T045 → T046; T045 → T048 (W4 part) | SC-009 on the release text | inside W4 |
| Part A squash-merged → T047; #364 merged → T038b | AD-14 | after W4 |

**Critical path.**
T003 → T004 → T012 → T013 → T023 → T016 #1 → T025 → T026 → T027/T028 → G1 → BX → T040 → H1 → T020 → T050 → T051 → T035 → T043 → T044 → T045 → T046 → merge.

**Float on that path.**
- **Lane E's guard chain** is critical.
- **SBE-D's queue** is near-critical. Its serial work is about 0.87 d, and it finishes close to G1.
- **T016's second commit** has about 0.05 d of float.
- **B1** is near-critical up to the S1 close, because T040 reviews T032's contract.
- **T014 → T015** has about 0.15 d of float.
- **B2** has about 0.6 d of float.

### Per-wave time estimates

| Build wave | tasks.md wave | Tasks | Effort, v1.1 | Effort, re-cost | Pacing chain | Window (× 1.25) |
|---|---|---|---|---|---|---|
| — | W0' (before T0) | T001, T002 | 0.15 | 0.16 | 0.16 | 0.20 |
| 1 | W0 | G0, T003 | 0.12 | 0.15 | 0.15 | 0.19 |
| 2 | W1 | T004–T019, T022–T029, T031–T034, T036, T037, T038a, T039, T040, T049, P0-B0, BX (plus T048's W1 part) | 4.36 | 5.40 | 1.46 (Lane E; B1 1.38) | 1.83 |
| — | W2 (session L) | GL, T020 | 0.60 | 0.60 | live | 0.60 (TW-A1 cap 1.00) |
| 3 | W3 | T050, T051, T021, T030, T035, T041–T044 | 0.88 | 0.98 | 0.58 | 0.73 |
| 4 | W4 | T045, T046, T048 (completes), G4 | 0.25 | 0.29 | 0.24 | 0.30 |
| — | conditional | T047, T038b | 0.15 | 0.15 | — | — |
| | | **Σ** | **6.51** | **7.73** | **2.59** | **3.85** |

**Projected duration: 4.74 d**, against the TW-0 line of 5.0 d. It is the sum of:
- 3.24 d of windows (W2 excluded);
- 0.60 d for the live session;
- 0.90 d for plan, handoffs and deliver.

**Milestones from T0:**

| Milestone | When |
|---|---|
| S1 closes | about T0 + 2.1 |
| W2 done | about T0 + 2.7 |
| PR ready | about T0 + 3.75 |
| Delivery, Part A alone | about T0 + 4.0 |
| Delivery, bundled | the later of T0 + 4.1 and #364's merge + 0.3 |

Calendar time runs longer than attention time.

---

## 4. Quality gates between waves

| Gate | When | Owner | Checks | On failure |
|---|---|---|---|---|
| **G0** S1 launch | Before build wave 1 | `orchestrator` | • The key-handling patch is merged on `main` (T0).<br>• T002's TW-B1 verdict is recorded.<br>• No open #369 branch edits the same workflow anchors; if one does, sequence the edits.<br>• `/aod.build --no-tests` runs with its reason recorded.<br>• The scratch clone path is set | No W1 task starts. If T002 is missing, D, R, E and B2 launch, and B1 waits |
| **P0-B0** | Start of W1 | `architect` | • T002 = PASS.<br>• T002 applied the AD-6 definitions at every depth.<br>• T039 places Step 2.6 between the Step 2.5 re-assert and Step 3, and leaves `orchestrator.md` untouched.<br>• T037 includes the re-install case.<br>• T032 follows `run-manifest.md` | No B code is committed until it passes. Part A lanes are unaffected |
| **TW-B3 watch** | During T032 | `orchestrator` | At T032.2, parser rework passes 0.5 d, or the layout changes mid-build | Honest-stop B1. B2 continues |
| **W1 carve check** | When T025 + T026 pass 0.80 d | `orchestrator` invokes the `team-lead` ruling | Lane E's overrun, measured against the 0.26-d margin under TW-0 | The ruling may carve C6, in TW-0's carve order (SC-A3 still ships). The PM and the architect ratify the carve |
| **G1** cut line | End of W1 | `orchestrator` + DEVOPS-E | • Lanes D and E, plus both T016 commits, are committed on the Part A branch.<br>• PR #392 is green on `tachi-pytest.yml` (both legs), on `tachi-permissions-verify.yml` (including `--self-test`) and on `tachi-install-fidelity.yml` (including `report-posture`).<br>• The scratch-clone gated set is green against T003's pre-state.<br>• `git status --short` is clean in the main tree | No BX and no P0 until green. A cut-line job still red after two fix-forwards goes to `debugger` |
| **BX** / **BX′** | After G1, and after T040's fixes | DEVOPS-E | • `git merge 391-isolated-auditable-operation` in the part-b worktree.<br>• CI green on the part-b draft PR | Fix it on part-b. Part A is unaffected |
| **T040 / P0** | After BX | `architect` | • The audited write set (T004).<br>• §8's placement and slug (T023).<br>• AD-13's tool coverage after T012 (T022).<br>• The RC-P1 definition applied in T002.<br>• The extractor-owned build directory (T012/T014).<br>• C6 green from day one (T025/T026).<br>• Step 2.6's placement and the one-commit rule (T039).<br>• The re-install test (T037).<br>• The B1 manifest contract (T032) and the B2 contract (T038a).<br>• T029's ADR-049 text | CHANGES_REQUESTED → the owning instance fixes it, then BX′ runs before H1 |
| **H1** | End of S1 | `orchestrator` | `NEXT-SESSION.md` (§7) | — |
| **GL** W2 launch | Before T020 | maintainer (human) | • The install source is chosen, and both SHAs are noted.<br>• Claude Code is v2.1.285 or later, and auto mode is available.<br>• The pre-staged profile (T006) and its `auto-mode config` output are checked.<br>• The Gemini key item is in the secret store. Check it by name only; never print it.<br>• `cleanupPeriodDays` is not lowered in any scope.<br>• A Linux VM is available; otherwise the claim is scoped (R-4 in the PRD).<br>• The TW-A1 budget is noted | Hold W2, or run the pre-ruled fallbacks |
| **H2** | End of L | maintainer (human) | The curated `test-results/w2-live.md`. The raw notes stay private | — |
| **T050** (G-B2) | First item of S2 | `orchestrator` invokes the `team-lead` ruling | From H1's actuals, TW-B2 fires if:<br>• Part B's remaining work is above 1.5 d; or<br>• a B lane is more than 50% over its v1.1 budget. B1's budget is 1.03, so it fires above 1.55; B2's is 0.55, so it fires above 0.83.<br>The PM also rules whether the lane clause defers only that lane | Ship Part A at the cut line. Defer Part B, or just the lane |
| **T051** (G-B1R) | After T050, before T035 | `tester` records; SBE-B1 runs the parse | • Every successful tachi dispatch in the W2 archives is attributed.<br>• No histogram is empty.<br>• The meta and line names agree.<br>• Every planted denial kind is detected.<br>• The gate fails closed | Honest-stop B1, and record it in `delivery.md`. B2 may still ship |
| **TW-B4** | Inside T035 | SBE-B1 + `security-analyst` | The scrub plus the leakage review stay within 0.35 d, and the review clears | Commit only the synthetic fixtures, and check the recorded run locally |
| **G3** W3 reviews | End of W3 | `security-analyst` (T042), `tester` (T043), `code-reviewer` then `architect` (T044) | • The snippets widen nothing beyond the two hosts.<br>• T014's extractor change is in place.<br>• The gated set is green on both tips, with no new byte-identity failures against T003 (the six pre-existing reds excepted).<br>• ADR-019's wording matches what ships | The owning W3 writer fixes it. T043 re-runs on any tip that changes |
| **G4** merge | End of W4 | `orchestrator` + DEVOPS-E | • T046 steps (0) and (1) pass.<br>• Split path: the path check, the hunk check and the baseline check return nothing, and #392 is titled `fix(391)`.<br>• Bundle path: a fast-forward of Part A to part-b, titled `feat(391)`.<br>• After the merge, the release-please PR exists; if not, push a marker commit | Hold the merge |

---

## 5. AD-14 stacked-branch mechanics

These mechanics serve TW-A2's split. The split is the planning case while #364 is unscheduled.

This repo's settings deny `git push --force` and `-f`, and put `--force-with-lease` behind an approval prompt. So the branches sync by merge. The squash-merge keeps `main` clean.

1. **T003 (W0)**
   - On the Part A branch, `git merge origin/main` (after T0) and push.
   - Create part-b from that tip and add its worktree outside the main tree: `git worktree add "$SCRATCH/wt/391-part-b" 391-isolated-auditable-operation-part-b`. Then push it.
   - Open a draft PR for part-b with base = the Part A branch, titled `feat(391): isolated and auditable operation (Part B)`. The three workflows run on `pull_request` with no branch filter, so part-b gets CI.
2. **W1**
   - Part A lanes work in the main tree. Lanes never switch branches.
   - The B lanes write only in the part-b worktree.
   - Part B hunks never land on the Part A branch.
3. **Writers on part-b**
   - The B lanes write their own files: the scripts, tests and fixtures; `schemas/run-manifest.yaml`; `templates/tachi/VERSION`; the `install.sh` marker block; the schema reconciliation; and Step 2.6.
   - SBE-B1 (T032) and SBE-B2 (T039) each write one `INSTALL_MANIFEST.md` whitelist line, serialised (R-4).
   - DEVOPS-E writes every `tachi-pytest.yml` change. The first Part B wiring commit carries the 3.9 step, pinned to `ubuntu-latest`.
   - **After BX, SBE-D writes T048**, one commit per file:
     - the runbook: the §3 archiver-wrapper clause, and §7's archiver, archive sensitivity, `run-manifest.json` and D-1 manifest sentence;
     - ADR-049's B1 and B2 sections, and its two Part B Known-limitations items;
     - ADR-019's manifest sentence;
     - §8's Step 2.6 entry;
     - the three manual-install-loop marker lines, byte-identical;
     - the README's "a skipped marker line reads `unknown`" statement;
     - in W4, the CHANGELOG's Part B lines.
   - Feature records under `specs/391-…/` stay on the Part A branch.
4. **Staying in sync**
   - BX at G1. BX′ after T040's fixes, before W2.
   - Again after any W3 fix that part-b needs.
   - Never rebase a pushed branch without the maintainer's approval.
5. **W2 install source**
   - Install from the part-b tip once B1 and B2 have passed P0.
   - Otherwise install from the Part A tip. SC-B3's live check is then skipped, and the archiver runs afterwards from the part-b worktree.
   - Record both SHAs.
6. **Split path: Part A ships alone as `fix(391)` (T046)**
   - `git diff --stat main...391-isolated-auditable-operation` lists no Part B-only path.
   - `git diff main...391-isolated-auditable-operation | grep -nE 'tachi_version|stamp-tachi-version|archive-run-transcripts|run-manifest|templates/tachi/VERSION|Step 2\.6|schema_version: "?1\.5'` returns nothing.
   - The diff contains no tracked example image, PDF or SARIF baseline.
   - Title PR #392 `fix(391): …` and mark it ready. After the squash-merge, check for the release-please PR; if it is missing, push a `fix(391)` marker commit.
7. **Part B delivery (T047), after Part A squash-merges**
   - In the part-b worktree, `git merge origin/main` (the identical Part A content merges cleanly), then push.
   - Run `gh pr edit <part-b PR> --base main`.
   - Run T038b if #364 has merged.
   - Re-run the gated set in a scratch clone, because `main` has moved.
   - Run `/aod.analyze`, then the final Wording sweep over the PR's text.
   - Keep the title `feat(391): …`. If the PR ends up as a single commit, the commit subject must start with `feat(391):`.
   - Mark it ready after #364 merges. After the merge, check for the release-please PR.
8. **Bundle path: #364 merges first (T046)**
   - On the Part A branch, run `git merge --ff-only 391-isolated-auditable-operation-part-b` and push. It is a fast-forward, so no force is needed.
   - Title PR #392 `feat(391): …`.
   - Close the part-b draft PR as superseded.
   - Mark T047 `[X] not triggered`.

---

## 6. Post-wave tests

**Why not the default.**
- `/aod.build` sub-step 4.5 detects `pytest` from the `[tool.pytest.ini_options]` table in `pyproject.toml`. It would run pytest in the main tree after every wave that changes a `.py` file.
- That re-renders tracked example PNGs (#365), and it hits pre-existing reds outside the gate.
- Sub-step 4.6 would add test modules that nothing gates.

**The rule.**
- Run `/aod.build --no-tests`. In each wave's results, record the reason: "#365 PNG hazard; gated sets run in scratch clones".
- After each build wave:
  1. Commit first.
  2. Run the wave's gated set in a scratch clone of the committed tip. Check `git -C <clone> log -1` before trusting the result.
  3. Record the totals in `specs/391-isolated-auditable-operation/test-results/wave-0N/results.json`, with `test_runner` set to the commands.
  4. Compare them with T003's pre-state.

```bash
SCR="$SCRATCH/wave-$N-$PART"                     # one clone per branch tip
git clone --no-hardlinks "$REPO" "$SCR" && git -C "$SCR" checkout "$BRANCH" && git -C "$SCR" log -1 --oneline
cd "$SCR"
# Part A tip (wave 2 on)
python3 scripts/check-agent-privileges.py --self-test
python3 -m pytest tests/scripts/test_agent_privilege_guard.py tests/scripts/test_isolated_profile_contract.py \
  tests/scripts/test_install_manifest_completeness.py -v
# Only where typst is on PATH; otherwise CI's report-posture job is the gate
TACHI_REQUIRE_TYPST=1 python3 -m pytest tests/scripts/test_write_confinement.py -v
python3 -m pytest <the modules listed in .github/workflows/tachi-pytest.yml at this commit> -v
# part-b tip (wave 2 on): the Part B modules on 3.11, and on 3.9 where available
# (otherwise CI's ubuntu 3.9 step is the gate)
python3 -m pytest tests/scripts/test_archive_run_transcripts.py tests/scripts/test_tachi_version_marker.py \
  tests/scripts/test_threats_schema_contract.py -v
```

| Build wave | Gate |
|---|---|
| 1 (W0) | T003's pre-state is the record |
| 2 (W1) | • The Part A tip and the part-b tip, as above.<br>• T005: `test_gemini_request_contract.py` A1/A5, if the client was pinned.<br>• G1 also needs CI green on #392 |
| 3 (W3) | T043, on both tips:<br>• the 18 `tachi-pytest.yml` modules, including `test_install_sh_symlink_preflight.py` and `test_install_sh_ref_restore.py`;<br>• the new modules on 3.11 and 3.9;<br>• the install-fidelity suites;<br>• the byte-identity suites against T003 (the six pre-existing reds excepted);<br>• `tests/scripts/test_coverage_attestation.py` |
| 4 (W4) | Docs and release mechanics only, so no run |

---

## 7. Session plan and NEXT-SESSION handoff points

| Session | Contents | Opens with | Closes with |
|---|---|---|---|
| (before T0) | W0': T001 (maintainer) and T002 (`tester`) | — | `test-results/w0-spike.md`, with the TW-B1 verdict |
| **S1** | Build wave 1 (W0) and build wave 2 (W1). Two waves, under `/aod.build`'s standalone ceiling | **H0**: the G0 checklist | **H1**: `NEXT-SESSION.md` |
| **L** | W2: GL, then T020 | The GL checklist, carried in H1 | **H2**: `test-results/w2-live.md` (curated) |
| **S2** | T050, then build wave 3 (W3), build wave 4 (W4), the merge and `/aod.deliver` | `NEXT-SESSION.md`, which the `orchestrator` updates from H2 | **H3**: `delivery.md` prepared, with the Part B status |

**Optional H1a.** W1 is long, about 1.83 d of window. If context runs high after T025 and T032.2, write `NEXT-SESSION.md` and resume W1 in a new conversation.

**H1** (`specs/391-isolated-auditable-operation/NEXT-SESSION.md`) contains:
- the Part A and part-b tips, PR #392 and the part-b draft PR, and the worktree path;
- G1's evidence (CI run ids) and the scratch-clone results against T003;
- T040's outcome, any open CHANGES_REQUESTED items, and the BX′ status;
- the inputs to T050 and to the TW-B3 watch:
  - per-lane actual effort against the v1.1 budgets (B1 1.03, B2 0.55, each separately);
  - the estimate of Part B's remaining work;
  - T032.1–.3's checkpoint actuals;
- the GL checklist, with the chosen install source;
- confirmation that `git status --short` is clean.

**H2** (`test-results/w2-live.md`) is a curated, structure-only summary. The file becomes public, so it holds no transcript excerpts, ids, home paths or key material. It contains:
- **Install and environment**: the installed SHA(s); the Claude Code version, the OS, the permission mode and the date.
- **Configurations run**, with each configuration's write listing.
- **Checks**:
  - the probe results;
  - the offline render check;
  - the Gemini client's CA trust under `tlsTerminate`;
  - the result of passing a file versus inline JSON to `--settings`;
  - the SC-B3 field check.
- **How the session ran**:
  - the exact wrapper form that worked;
  - any unexpected denials (target: zero);
  - the TW-A1 debug loops used;
  - the fallbacks applied.
- **Archiving**: whether each session was archived, and under which wrapper.

The raw notes stay private.

**H3** is the `delivery.md` that T045 prepares. It records:
- the fired trip-wires, or "Part B: built, awaiting #364" with the PR number;
- the W0' topology, the Claude Code version and the layout observed;
- the dispatch defect that predates this feature;
- the note on correcting published copies;
- the debt register and the follow-ups.

---

## 8. Load check

An instance's wave load is its attention-days in the wave divided by the wave window. The figures use the central re-cost.

| Wave (window) | Peak instance | Peak load | Others |
|---|---|---|---|
| W0' (0.20) | maintainer (T001) | 50% | `tester` 30% |
| W0 (0.19) | DEVOPS-E (T003) | 79% | — |
| W1 (1.83) | SBE-B1 (T031, T032, T033's schema doc) | **59%** | SBE-D 48%; SBE-E 43%; SBE-TA 26%; SBE-B2 25%; DEVOPS-R 23%; SBE-TB 22%; DEVOPS-E 15%; `web-researcher` 14%; `architect` 10%; `product-manager` 8%; `security-analyst` 4% |
| W3 (0.73) | `tester` (T041, T043, T051's record) | 37% | SBE-B1 32%; `code-reviewer` 16%; DEVOPS-R 14%; `security-analyst` 14%; `architect` 11%; DEVOPS-E 7%; `team-lead` 4% |
| W4 (0.30) | `product-manager` (T045) and DEVOPS-E (T046) | 40% each | SBE-D 17% |

- **No instance exceeds 80%.** The capacity veto is not exercised.
- **W1 is at the solo-curator cap**: two heavy lanes (E and B1) and three medium ones (D, R and B2). Do not widen it. The test-lane instances start once their contract inputs exist.
- **SBE-D carries the most serial work of any Part A instance.** Keep to its queue order (R-3).
- **The binding constraint is serial work**: the maintainer's W2 session, the CI cycles at the cut line, and the external gates (T0 and #364).

---

## 9. Escalation triggers

| Task | Trigger | Action |
|---|---|---|
| T001 | Phase 5 fails, or the session overflows on the small input | Re-run on the other candidate input. If depth 3 is still unobserved, T002 lists it as not observed (never inferred). T051 re-confirms it on the W2 sessions |
| T002 / T051 | TW-B1 fails | Honest-stop B1 and record the layout. B2 continues; T048 keeps only its B2 items |
| T005 | The field list goes beyond R-8 | The PM approves the text (PRD v1.4) before Lane D writes it. Meanwhile, SBE-D works on T012–T014, T022 and T024 |
| T012/T014 | The extractor's precondition fails on a real layout | The architect rules at P0. Never fall back to an agent-side `rm` |
| T025/T026 | Combined effort passes 0.80 d | The W1 carve check (§4) |
| T032 | Parser rework passes 0.5 d, or the layout changes | TW-B3: honest-stop B1 |
| G1 | A cut-line job is still red after two fix-forwards | `debugger` |
| T050 | It fires | Ship Part A at the cut line. Defer Part B, or just the lane |
| T020 | More than 3 debug loops, or more than 1.0 d | TW-A1:<br>• document the limitation;<br>• make the key-less path the isolated default;<br>• stamp only what ran;<br>• file a follow-up issue (run `export AOD_REPO=davidmatousek/tachi` first);<br>• do not hold the bundle |
| T035 | It passes 0.35 d, or the leakage review does not clear | TW-B4: commit the synthetic fixtures only |
| T044 | A code fix is required | The owning W3 writer fixes it, and T043 re-runs on that tip |
| T030 | The throwaway branch remains after its PR closes | Delete the remote branch and leave the local one to the maintainer (R-8) |
| T046 / T047 | No release-please PR about 30 seconds after the merge | Push a `fix(391)` or `feat(391)` marker commit |
| Every reviewer and verification agent | Always | The #365 rule: scratch clone only, then `git status --short` |

---

## 10. Sign-off

**Team-lead** (the assigner), 2026-11-16, on tasks.md v1.1:
- **Assignments**: all 52 tasks map to exact registry names. T001 and T020 go to the maintainer (human). Every instance label resolves to one `subagent_type` (§1).
- **Waves**: the wave map respects every dependency edge in tasks.md v1.1. The readings in §0 cover T050's placement, the W3 chain, SBE-D's queue and the serialised whitelist lines.
- **Branches**:
  - Part B commits stay on the stacked branch, which makes the TW-A2 split mechanical.
  - The bundle path is a fast-forward.
  - Post-wave tests never touch the main tree.
- **Load**: the peak is 59% in W1, and no wave goes above 80%.
- **Trip-wires at `/aod.tasks`**:
  - TW-0 is not fired (4.74 d).
  - TW-B0 is not fired (2.86 d).
  - TW-A3 is not fired (bounded).
