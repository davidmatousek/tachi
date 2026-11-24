# W5 gate, PR 1: TW-L2, fallback rates, SC-8 and the residuals (T077, M5a)

**Date:** 2026-11-24. **Lane:** G, from the records alone: no agent, no live session, no test run. **Base:** the lane at `3a812d6`. **Builds:** attempt 1 on `27d58bd`; attempt 2, SC-8 and R-27 on `1e3614a` (T147). **Inputs:** T077; tasks.md's TW-L2, PM-fallback and SC-8 rows; feasibility-check.md's TW-L2 text; w5-setup-pr1.md; offline-e2e-pr1.md section 12; the eight live records; t147-fixes-pr1.md; sc8.md; r27-smoke-pr1.md; the architect's W5 diagnosis (AW5-1 to AW5-9, kept private).

## Result: M5a PASSES, with one return. T078 runs on Q1 only (section 4)

**T078 ruled option A for both residuals (section 5a), so every claim in section 5 stands.**

| Item | Verdict |
|---|---|
| TW-L2 | Every cell has a final attempt that earns its claims, except two that wait on Q1: scorer at default (R1) and controls at max (R2). Attempt 1's defects were shipped text, cured once by T147. No attempt is left at default; none is needed at max. No run was interrupted by a usage limit or infrastructure (a launch closed by a wrong key at the trust dialog, before any command, is not an attempt) |
| Fallback (ruling 2) | Highest rate 1.3% (1 of 80, one run). None above 10%, so no follow-up on rate and nothing for the notes to link. None above 25%. No slot that should resolve fell back |
| SC-8 (P-7) | Both stages below their v4.48.4 baselines (-64.9%, -71.0%), one batch each. No overage |
| R-27 | PASS at its first attempt |
| Build | The claims rest on `1e3614a`. **G-1.** `git diff --stat 27d58bd HEAD` shows no change under scripts, schemas, templates, skills, adapters, brand, fixtures or examples; T147 changed four text files and one test module. So P1-1 (section 12) and the oracle stand. A W6 edit to an agent, command, reference, template or script reopens the cells it reaches |

## 1. TW-L2 per stage and effort level

| Cell | Attempt 1 | Attempt 2 | Class | Earns |
|---|---|---|---|---|
| Scorer, default | On `27d58bd`. Structure holds. 1 of 26 agents read any reference; report added text; one text-tool call on the input | Holds. Report 0 added; 0 unnamed programs. 17 of 26 read all four references, 9 skipped one or more, 1 read none (R1) | a1: shipped text (AW5-1, 2, 4), cured by T147. a2: R1, class yes, withdrawal unsettled (Q1) | US-1a #1 and #6 pending T078 |
| Scorer, max | Main session at max, agents at medium. Rows, N/N and 26 batches hold. 6 inline programs, 13 added report lines, 1 of 26 read any reference | Main session and agents at max (36 of 36, 310 of 310). 26 of 26 read all four; 0 added; 0 programs. 9 agent responses hit the cap while thinking and the client resumed them (G-8) | a1: shipped text (AW5-1, 4, 5), cured. a2: none | US-1a #3 and #6 claimed |
| Controls, default | Holds. Binding reads 5, 0, 0 of 38. 10 non-canonical category cells (flagged). Report added text and paraphrased the warnings | Holds. 38 of 38 read all three; 0 added; 0 programs; 0 non-canonical cells | a1: shipped text (AW5-1, 2, 4), cured. a2: none | US-1a #2 and #6, US-3 #5, SC-5 claimed |
| Controls, max | Main session at max, agents at medium. Coverage, totals and agreement hold. 4 inline programs, 13 added lines, reads 9, 6, 2 of 38. One invalid part caught and retried. 1 of 80 fell back | Both at max (48 of 48, 494 of 494). 38 of 38 read all three; 0 added; 0 programs; 0 of 376 fell back. 4 agents read shipped scripts off their read list (R2) | a1: shipped text (AW5-1, 4, 5), cured. a2: R2, class and withdrawal unsettled (Q1) | US-1a #3 and #6 pending T078. US-3 #5 and SC-5 claimed (default attempt 2 carries them too) |
| SC-8, scorer | On `1e3614a`. 9,493 tokens against 27,049; 1 batch of 11 units; 1 of 1 read all four; report 0 added; 0 programs | Not needed | None | US-1a #7, #6 (small run) and "cheaper" claimed |
| SC-8, controls | On `1e3614a`. 10,207 tokens against 35,200; 1 batch of 11; 1 of 1 read all three; 0 added; 0 programs | Not needed | None | The same |
| R-27 | On `1e3614a`. Threat model, scorer, controls: 0 prompts, 0 denials, 76 new paths, 73 in section 5's rows and 3 the client's own marker. Controls stage: one `grep` in a Step 1 listing pipe (R3) | Not needed | None. R3 is not the class (G-7) | R-27 claimed; runbook header updated (T072) |

**G-2. Counting at max, both readings.** The architect's: attempt 1's max runs put only the main session at max (agents at medium on 116 of 116 and 203 of 203 responses), so they don't test R-18's condition and aren't max attempts. The relaunch (main session and agents at max, D-L9) is then attempt 1 at max, with a second in reserve. The stricter reading counts them for the main session's claims, so the relaunch is attempt 2 of 2, as the testers labelled it. **The outcome is the same.** Both relaunches pass their acceptance checks (R2 is the one item left to class), so neither reading calls for a third run, and the claims at max rest on the relaunches either way. Under both, attempt 1's main-session findings are shipped-text defects that T147 cured and attempt 2 re-tested, which is TW-L2's fix-and-rerun as written. The readings would part only if those findings were departures from clear command text (disposition (b)), which would keep US-1a #6 at max withdrawn despite a clean attempt 2. They aren't: the text left room (AW5-4, AW5-5), E8 and E9 close it, and no code ran at either relaunch.

## 2. Fallback rates (ruling 2: follow-up above 10%, PM return above 25%)

| Stage | Default, attempt 1 | Default, attempt 2 | Max, attempt 1 | Max, attempt 2 | Small runs: SC-8; R-27 |
|---|---|---|---|---|---|
| Scorer (4 fields a unit) | 0 of 1,304 | 0 of 1,304 | 0 of 1,304 | 0 of 1,304 | 0 of 44; 0 of 140 |
| Controls (4 fields an assessment) | 0 of 84 | 0 of 20 | 1 of 80 (1.3%) | 0 of 376 | 0 of 4; 0 of 8 |

- No run is above 1.3%, so nothing needs a follow-up on rate, a link in the notes or a sample for the PM. The one fallback was a numeral written outside a slot (the numeral ban), not a slot that failed to resolve, so ruling 2's defect clause doesn't apply; the relaunch at max had none. The agents' other text fields never fell back (every matrix row, recommendation body, evidence snippet and summary).
- **G-3.** The controls rate is counted over the assessments the agent chose to write, so its denominator runs from 4 to 376 fields. Under 10% on 4, 8 or 20 fields rules out little; the zero on every matrix row and recommendation is the firmer one. No ruling is needed.

## 3. SC-8 against P-7

| | Scorer | Controls |
|---|---|---|
| Output tokens, whole stage | 9,493 | 10,207 |
| v4.48.4 baseline (T021(b)) | 27,049 | 35,200 |
| Delta | -17,556 (-64.9%) | -24,993 (-71.0%) |
| Ceiling (baseline plus 10%) | 29,753: 20,260 under | 38,720: 28,513 under |
| Batches planned, dispatched, done | 1, 1, 1 (11 units, below the threshold) | 1, 1, 1 (11 units) |

- Both deltas are below zero, so US-1a #7's token clause and "cheaper" hold. Each agent ran once (NFR-4), and the structure holds apart from items the contract lets a run omit (sc8.md section 7). **T078 doesn't apply to SC-8:** no stage is over, so no second attempt and no return.
- **Conditions against T021(b):** the same example and inputs (digests equal), the same effort (medium, by flag), no profile, one fresh session for both stages. Recorded differences: client 2.1.331 against 2.1.330, and the build. The sign is firm (the totals are 35% and 29% of the baselines); the size is one run each.
- **G-4. Scope of "cheaper".** The small example at default effort, per stage. At the fixture the default scorer used 233,319 tokens against 61,119 for v4.48.4's run, which didn't finish in contract, so they don't compare. At true max it used 4,295,809.

## 4. The residuals after T147

| Residual | Departs from | In TW-L2's class? | Bears on (named) | Outcome |
|---|---|---|---|---|
| **R1** scorer, default, attempt 2 | The scorer's step 3 (E2: read four references before the first finding). 9 of 26 skipped one or more (trust zones 9, CVSS vectors 2, scoring dimensions 2, reachability 1); one read none; 3 notes say so | Yes: the architect decided in advance that a skip after the fix is an agent off its contract (AW5-1). It is not in feasibility-check.md's list (a stand-in, a hand-back, an ignored overflow contract) | None of SC-3's six items. None of US-1a #1's bullets (rows, N/N and agreement, two or more batches, no hand assembly: all hold) or #6's clauses. It bears on T147's target 1 and on the agent-written judgment fields, which no PR 1 criterion measures live | Recorded, follow-up. Withdrawal unsettled: **Q1** |
| **R2** controls, max, attempt 2 | The controls agent's step 1 (E3: besides the data files, read only what the spec says). 4 of 38 read the part-validation module (12 reads) and the renderer (10), with 25 greps. No Bash; nothing written or handed back | Unsettled. Not in the decided list or its two extensions. By R1's logic (clear text, departed from) it would be | Not SC-3's "unshipped scripts run" (read, shipped, no Bash) nor #6's clauses. Closest is US-3 #5's "checked by a shipped check", which is intact: 0 overwrites, 0 flags, 37 of 37 independent checks, and the other 34 agents' parts pass the same check | Recorded, follow-up. Unsettled: **Q1** |
| **R3** R-27 controls | Step 1 (E8: "a listing or a file test is enough"). One `grep` filter in a listing pipe; no interpreter code | No. A filter in a listing is a listing, and a listing with `sort`, `head` and a `for` loop was counted as allowed at the controls' default attempt 2 | R-27's criteria (completes, no prompt or denial, writes inside section 5): no. US-1a #6 isn't claimed from R-27; the fixture and SC-8 runs carry it | Settled by E8 and R-27's text: nothing withdrawn |

- **G-5 (R1).** At default, attempt 2 was the last attempt, so nothing cures it inside TW-L2. The same text got 26 of 26 at max and 1 of 1 and 3 of 3 in the scorer's small runs, but 17 of 26 on the fixture at default: it doesn't hold every default-effort agent.
- **G-6 (R2).** The agent file names the renderer's path in its opening lines, which can read as an invitation at max effort.
- **G-7 (R3).** The records applied two rules to listing filters. The structure audit needs one (follow-up below).

**Q1 for T078: how far does TW-L2's "an agent off its contract" reach?** The decided text lists the class as "a stand-in, a hand-back or an ignored overflow contract" (feasibility-check.md); disposition (b) adds a main-session departure from the command text; AW5-1 adds a skipped binding read once the text is clear. Nothing says which SC goes unclaimed, or whether a behaviour that bears on no SC withdraws one. R1 and R2 are the instances, and each is its cell's last attempt.
- **(A)** Neither withdraws a claim: each gets a follow-up, and the notes state a non-claim. **(B)** Each withdraws US-1a #6 (SC-3's live half) for its cell. **(C)** Each withdraws all its cell's live claims: US-1a #1 and #6 (scorer, default); US-1a #3 and #6 (controls, max; US-3 #5 and SC-5 stand on default attempt 2).
- **Recommended: (A).** No signed SC or scenario measures reference reads or read scope. US-1a #1's bullets and #6's clauses are renderer output or structure, and hold on both runs. The decided class is SC-3-shaped. (C) would leave the lead story with no live claim and no attempt to cure it. The cost of (A) is a stated non-claim: PR 1 doesn't say that agents read their references at default or keep to their read list at max. The answer also sets the reading for T133.

## 5. Claims PR 1's notes may make from W5

- **US-1a #1: pending T078** (Q1; recommended claimed).
- **US-1a #2: claimed.** Controls at default, attempt 2: 408 of 408 once, totals equal the sums, N/N, agreement.
- **US-1a #3: pending T078 for controls at max** (Q1). **Claimed for the scorer at max** (attempt 2: row parity, N/N, 26 batches, no hand assembly), with G-8 stated.
- **US-1a #6: pending T078 for scorer at default and controls at max** (Q1). **Claimed** for scorer at max, controls at default and SC-8's two stages.
- **US-1a #7: claimed.** One agent once per stage, structure holds, tokens below baseline.
- **US-3 #5: claimed.** Controls Sections 2 and 4 agent-written; computed cells held their slots (0 overwrites); the shipped check rejected a 10-cell row live and flagged the category spellings (attempt 1; no script changed since).
- **SC-5 on a live run: claimed.** One schema in every band table, totals equal the sums, `.md` and `.sarif` agree, 0 unjoined Section 4 blocks.
- **R-27: claimed.**
- **SC-8 "cheaper": claimed** for both stages, only as G-4 scopes it.
- **Not claimed, outside the list:** tachi's overflow path at max (US-1a #4 and #5 rest on the offline half); score parity with v4.48.4 (G-10); the threat-model stage's on-contract execution (G-11); that agents read their references at default or keep to their read list at max, unless Q1 says otherwise.

## 5a. T078's ruling (the PM, 2026-11-24)

- **R1 and R2: option A.** Both stay classed as agents off their contract (R1: the reference reads; R2: the read list), and both cells keep their claims. Under TW-L2, "don't claim that stage's SC" withdraws only a claim that measures the departure, or one whose evidence the departure could change. No signed criterion measures reference reads or read scope, and every claimed criterion held. This reading binds T133.
- **So section 5 resolves to:** US-1a #1 claimed; US-1a #3 claimed for both stages at max; US-1a #6 claimed in every cell, stated only as its listed items, never as "on-contract execution".
- **Release notes (T079):** they may describe the new instruction text. They may not claim, at any effort, that agents read their references or keep to their read list. They carry one known-limitation line on the default-effort scorer's skipped reads, linked to follow-up 1. R2 goes in the PR body only.
- **Follow-ups, which T080 files before T079:** (1) "Agents can skip the reference files their instructions require: deliver the rules in the batch input, or check the reads structurally"; (2) "Agents can read files outside their declared read list: close the list, and check read scope structurally".

## 6. Other findings

- **G-8. Max is a cost step with a thin margin.** At true max the scorer used 4,295,809 output tokens in 46 min 24 s (default attempt 2: 233,319, 2 min 44 s); controls 4,110,230 in 43 min 14 s (357,397, 4 min 38 s). 9 of 26 scorer agents hit the 128,000 cap while thinking, before their Write, and the client resumed each in-run. All parts were valid and tachi logged 0 overflow events, so its record can't see such stops. The scorer's two largest writes left 666 and 974 tokens of margin. US-1a #3 holds on client 2.1.331, and the claim shouldn't credit tachi's re-dispatch.
- **G-9. "Default effort" is medium by flag** (D-L2). The account's default now opens higher, and no run sampled it. The notes should say "default (medium)".
- **G-10. Scores move between runs.** The scorer's High count on one input is 5 and 9 at default, 5 and 16 at max, and 27 at v4.48.4. One run per level, so variance isn't separated from the change.
- **G-11.** R-27's threat-model stage ran inline code (one `python3 -c` by the orchestrator, one heredoc by the main session). Typed dispatch is PR 2's, so PR 1 claims nothing for that stage's execution. R-27's own criteria hold.
- **G-12.** The main session prints 32 to 45 one-line status notes a run before the final report. Step 6 doesn't govern them, two doubted an agent's reply and didn't act, and no claim depends on them.

## 7. Follow-ups the records surface (generic, for T080 to file; T079 items marked)

1. Scorer agents at default skipped a required reference read in 9 of 26 batches, one read none, though the step names the files: choose a firmer contract, delivering the rules through the batch input or the renderer, or a check (G-5).
2. Controls agents at max read shipped scripts off their read list (4 of 38): close the list, or name what the part format needs (G-6).
3. At max, scorer batches hit the output cap while thinking (9 of 26) and the client resumed them unseen by the stage record, with under 1,000 tokens of margin: size max batches narrower or record such stops. Input to S-16's entry (G-8).
4. The controls agent's scan limits (file budget, truncation, unmapped component) have no part field now that the command doesn't relay replies: add a closed field listed in Section 7 (AW5-8); a "check before relying" caveat, if wanted, belongs in the renderer.
5. The main session narrates 32 to 45 notes a run outside Step 6: say whether commands may, and bound it (G-12).
6. The structure audit needs one stated rule for a filter in a Step 1 listing pipe (G-7).
7. A first-run threat model has no per-finding delta status, so both stages flag every finding `value-not-in-form` and exit 5: decide whether a first-run adopter should see that.
8. No live record shows the architecture-aware paths (reachability, component mapping) running; the fixture has no snapshot beside its `threats.md`. Record one run that has it.
9. Every live stage ran on Python 3.14.4, outside CI's range, and one parser test expects a refusal of a 5,000-deep JSON document that Python 3.12 and newer parse: add 3.14 to the matrix and state the test's intent.
10. The controls fallback rate's denominator is the assessments the agent chose to write (4 to 376 fields): count a fixed set (G-3).
11. **T079:** say each stage is cheaper, with the deltas, scoped as G-4 says, and name what "default" tested (G-9) and what max costs (G-8).
12. **T079:** every `threats.md` written before PR 1 lacks the architecture-source line, so every adopter's first run warns and exits 5, at the default path too; item 1 as drafted names only non-default locations (offline-e2e-pr1.md O1).
13. **T079:** state the non-claims in section 5 and Q1's answer. No W5 follow-up is above 10%, so no rate link is owed.

## Hygiene

H1: no pytest or extractor ran; only file reads and `git diff --stat`. Nothing outside this record was written, and nothing was committed. H8: no path or real name; fixture and example names are generic; findings are G-numbers.
