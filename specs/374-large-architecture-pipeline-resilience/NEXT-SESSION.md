# Session Continuation: F-374 Large-Architecture Pipeline Resilience

**Generated:** 2026-11-24, at session L's close
**Branch:** `374-large-architecture-pipeline-resilience`, draft PR #423 (PR 1)
**Last pushed commit:** `1e3614a`, W5's one push (T147's fix), with CI 14 of 14 green. The W5 records commits follow it locally (see "State").

## Completed in session L (PR 1's W5, M5a)

- **Before the live runs:**
  - P1-1 re-ran T065's offline driver on W5's install commit `27d58bd` and passed on Python 3.11, 3.9 and 3.14.4, the live runs' interpreter (`offline-e2e-pr1.md` section 12).
  - T072 built the scratch adopters and recorded dispositions (a) to (c) in advance (`w5-setup-pr1.md`).
- **Attempt 1, on `27d58bd`.** All four fixture runs met their structural claims. Three contract-text defects surfaced (AW5-1 to AW5-9):
  - agents skipped the binding references their sections mark mandatory, because step 1 limited reads to `refs`;
  - the final reports added the main session's own text (Step 6);
  - at max effort, the main session ran inline programs.

  Also, `claude --effort max` reaches only the main session: the first "max" runs had their agents at medium. Max runs now launch with `CLAUDE_CODE_EFFORT_LEVEL=max` plus the flag.
- **T147, `1e3614a`:** fixed all three in 0.2 d (`t147-fixes-pr1.md`), pushed, with CI green.
- **Attempt 2, on `1e3614a`:**
  - T073 and T074, at the default effort and at true max: every claim holds, with 0 Step 6 additions and 0 unnamed programs.
  - Binding reads: controls 38 of 38 at both efforts; scorer 26 of 26 at max, and 17 of 26 reading all four at the default.
- **T075 (SC-8):** the scorer came in −64.9% and controls −71.0% against v4.48.4, with one batch each (`sc8.md`).
- **T076 (R-27):**
  - Passed under the published profile, with every write inside the runbook's write locations (`r27-smoke-pr1.md`).
  - The runbook's "Last validated" header names this run (T072 part 2).
- **T077 (`w5-gate-pr1.md`):** M5a passes with one return.
- **T078:** the PM ruled option A, so the claims stand. The binding reading, which also binds T133: TW-L2's "don't claim" withdraws only a claim that measures the departure, or one whose evidence the departure could change.
- **The architect's W5 checkpoint:** T147 as landed matches its spec (APPROVED_WITH_CONCERNS: the two residuals above, now ruled).
- **Census (`test-results/wave-05`, on `867b611`):** 7599 passed, 0 regressions, and the same 34 pre-existing out-of-gate failures as T001 and W4.

## State

- **Phase:** implement. **Tasks:** PR 1 85 of 91 (open: T071, conditional on TW-CI, and W6's T079–T083). PR 2 7 of 59, on its own branch.
- **TW-N3: ARMED**, unchanged. Any edit to an agent file the stages load needs the private no-touch notes (see the private track).
- **The local records commits after `1e3614a` aren't pushed** (H6 forbids pushing records alone). S3's first push, P1's batch, carries them.
- **Usage:** the week stood at about 48% at L's close, and resets Nov 26 at 9pm ET. The true-max fixture runs are the expensive ones: 4.1 to 4.3M output tokens each, about 45 minutes each.

## Next Actions: session S3, which is PR 1's W6

1. **Resume** `/aod.build 374` on the branch. The branch lives in a linked worktree, so check `git worktree list` and never switch branches in the main checkout (H9).
2. **First, P1's batch,** about 0.14 d, in one push, as S2's handoff planned:
   - P1-2: SA-4's file modes through the renderers' `os.replace` and `fail`'s restore.
   - P1-4: the effort-estimate check and D2's standing rule.
   - P1-5: `score-source`'s wording.
   - The ADR text: D2 near `:146`, D4's step 5, D3's two nits and D7's `%3A` note.
   - Four Known-limitations lines: SA-1's residual, SA-9, SA-14 and SA-15.
   - **New from L, records only:** `t146-fixes-pr1.md` still lists SA-3 as deferred, but `c129e78` (T146's SA-1 row) also cured T065's O2, which is SA-3. Correct the row, and drop SA-3 from T080's list if nothing remains.
   - **The same push carries** the merge-candidate oracle (Verification 7) and P1-1's second run, if P1-2 changes a script.
3. **Then T079 to T083,** in the order the tasks give: T080 files the follow-ups before T079 writes the notes that link them.

## Notes for later tasks

- **T079 (PR 1's release notes):**
  - **Claims:** take them from `w5-gate-pr1.md` sections 5 and 5a.
    - SC-8's "cheaper" holds only for the small example at the default effort (the gate's G-4).
    - Under T078, the notes may describe the new instruction text, but may not claim, at any effort, that agents read their references or keep to their read list.
    - US-1a #6 is stated only as its listed items.
    - One known-limitation line covers the default-effort scorer's skipped reads, linked to T078's follow-up 1.
  - **Release-note items from S1, S2 and L:**
    - S2's O1 and P1-3 items still stand.
    - **New from T076:** a first run with no baseline writes `threats.md` without `delta_status`, so both stages flag every finding `input:delta_status:not-in-form` and exit 5. Note it, or file it if it's a defect.
    - **Adopter guidance:** `--effort max` sets only the main session, while `CLAUDE_CODE_EFFORT_LEVEL` reaches the agents.
- **T080 (the follow-ups and the KB entry):**
  - **The lists to file:**
    - `w5-gate-pr1.md` section 7: 10 to file, plus 3 notes items;
    - T078's two follow-ups, in its exact generic titles;
    - S1's and S2's lists, and `t146-fixes-pr1.md`'s "Deferred" list.
  - **Also from L:**
    - `test_tachi_parsers`' 5000-deep JSON case fails on Python 3.12 and later, which parse that input. CI's 3.11 and 3.9 pass it, but S-4's determinism claim names 3.9 to 3.13.
    - `control-analyzer.md:84` still asks the agent for scan limits in its reply, which the command no longer relays (AW5-8's residual).
    - The runbook's section 11 has no entry for the 2026-11-24 run.
  - **S-16's KB entry (Entry 27)** should carry W5's true-max evidence. At max, thinking fills the response: 9 scorer agents hit thinking-only `max_tokens` stops, and two Writes came within 1k tokens of the 128k cap. D6's sizing bounds writes, not thinking.
- **T066 at W6:**
  - the merge-candidate confirmation (Verification 7);
  - P1-6's spec erratum;
  - D2's held-condition note;
  - T075's two NFR-1 notes: template sub-sections that neither run writes, and the controls output's "no mapped threat" controls, which v4.48.4 listed and the per-finding output doesn't carry. The PM may need to rule on the second.
- **#364 at delivery:** S2's notes stand.
- **PR 2:**
  - S2's notes stand.
  - T078's reading binds T133.
  - Launch W5′'s max runs with the environment variable, and check the agents' effort in the transcripts.

## How session L ran, and what S3 can reuse

- **Lane worktrees per task:** agents never commit, one agent instance per live run, and the orchestrator commits on the lane and cherry-picks.
- **Each live run** is a fresh interactive session in tmux:
  - a neutral adopter path, the clean environment (`env -i`) and `--effort medium`, because the account's settings now open Opus at xhigh;
  - one shared protocol brief for the testers;
  - a private status log at every step.
- **The user-scope settings that R-27's runbook asks for** were applied for that one session, with the maintainer's approval, and restored byte for byte.

## Context files

`tasks.md` (W6), `agent-assignments.md`, `test-results/w5-gate-pr1.md`, `test-results/t147-fixes-pr1.md`, `test-results/sc8.md`, `test-results/r27-smoke-pr1.md`, the four `live-*-a2.md` records, `test-results/oracle-pr1.md`, `test-results/ci-pr1.md`, ADR-050, `contracts/`, `plan.md` and `quickstart.md`.

## Resume command

```bash
claude "Resume F-374 implementation (branch: 374-large-architecture-pipeline-resilience). PR 1's W0-W5 complete (85/91 PR 1 tasks; M5a passed, T078 ruled option A; W5's fix 1e3614a pushed, CI 14/14 green). Run /aod.build 374 to continue with session S3: P1's batch with the merge-candidate oracle in one push, then W6 (T079-T083) to deliver PR 1."
```
