# Live controls run on the fixture, effort max (T074, attempt 1, W5)

**Date:** 2026-11-24. **Base:** install commit `27d58bd` (describe string `v4.48.4-154-g27d58bdc`), the controls template at restore point `b42c12e`. **Inputs:** [w5-setup-pr1.md](w5-setup-pr1.md), [live-compensating-controls-default.md](live-compensating-controls-default.md), spec US-1a #2, #3 and #6, US-3 #5, SC-3 and SC-5. **Run:** one live `/tachi.compensating-controls --target controls-target` on the fixture's 408 scored findings, Claude Code 2.1.331 on macOS (the default-effort run recorded 2.1.330), Python 3.14.4, effort max (by flag, D-L2), attempt 1 of at most 2 (TW-L2).

## Result: FAIL on one claim, US-1a #6 and SC-3 (TW-L2 class: an agent off its contract, the main session); the other claims hold

| Question | Result |
|---|---|
| **US-1a #3, scenario 2 at max: coverage** | 408 of 408 scored open findings appear in Section 2's four band tables exactly once (0 missing, 0 extra, 0 duplicate). `compensating-controls.sarif` holds 408 results, one per open finding (the N/N rule), with the scored input's IDs |
| **US-1a #3: totals and agreement** | Section 1's counts (9 Control Found, 171 Partial, 228 No Control), the band counts (1, 19, 292, 96), Section 5's totals (2273.6 inherent, 2017.2 residual, 11.3%) and its shift and distribution tables all equal the sums of the rows (the percentages sum to 100). The SARIF agrees with the `.md` on status, both scores, level, MAESTRO layer and recommendation presence for 408 of 408 |
| **US-1a #6, SC-3 (structure only)** | **Not met.** 0 stand-in dispatches, 0 program files written, 0 code hand-backs, only declared paths written, but the main session ran 4 inline `python3 -c` programs of its own (read-only), where the command names only its two shipped scripts (section 6) |
| **US-3 #5, SC-5** | One 11-column schema in all four band tables. Sections 2 and 4 were authored by the agents inside their part files; every computed cell held its slot token for the renderer to fill (`cell_overwrites` 0). The shipped check rejected one part for a 10-cell Section 2 row (retried, observation 2) and flagged all 9 category-spelling mismatches that the independent reader also found. Section 4 holds 399 blocks for 399 gap findings, none unjoined |
| **Stage exit** | 5, `success-with-warnings`: the pass state (disposition (a)). Warnings: `architecture-path:body-line:absent` and `baseline-unresolved`; no `evidence-file-unresolved` |
| **Output tokens** (command's turns and every subagent, thinking included) | **337,071**, of which thinking 78,760 (23%). Main session (Opus 5.5, max) 30,787 in 36 responses; 39 agents (Sonnet 5.5, medium) 306,284 in 203 responses |
| **Batches** | 38 planned, 39 dispatched (one retry), 38 done, in waves of 16, 16, 6 and 1. 1 overflow event (`invalid`), 1 retry, 0 splits, 0 exhausted; the plan's sizes were 28 batches of 11 and 10 of 10 |
| **Narrative fallback rate** | 1 of 80 narrative fields (1.3%), a numeral written outside a slot; no slot that should resolve fell back |
| **Wall time** | **6 min 57 s** (the session's own timer). Stage record: 5 min 23 s |
| **TW-L2** | An agent off its contract (the main session, disposition (b)): record it, file the follow-up, don't claim SC-3 for this stage at max. No shipped-code defect, no interruption (section 8) |

## 1. The arrangement

- **The adopter.** A fresh `git clone` of `<adopter w5-fixture-controls>` into a new directory, clean at `b42c12e`. Inputs as w5-setup-pr1.md section 2 lists them: `risk-scores.md` (sha256 `e82da952...`), `threats.md` (`44694eb5...`, byte-identical to `baseline/threats.md`), `architecture.md` (`5ee33b33...`) and `controls-target/` (tree `fb3cfb11ba5479ec2aaacf2e4496198dbd897425`). No tachi command ran in the template.
- **The session.** A detached terminal-multiplexer session (200 x 50), cwd the clone, launched as `env -i HOME=<home> USER=<user> LOGNAME=<user> SHELL=/bin/zsh TERM=xterm-256color LANG=en_US.UTF-8 PATH=<user bin>:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin claude --effort max`. The banner read "Claude Code v2.1.331" and "Opus 5.5 with max effort", auto permission mode. **D-L2:** the flag sets R-18's second level; the account's settings alone would open at xhigh.
- **The dialog.** The trust dialog listed "No, exit" first, highlighted. One Down and Enter chose "Yes, I trust this folder". No other prompt appeared: all 49 main-session and 419 agent tool uses ran without a dialog, and none returned an error.
- **The command**, typed as-is: `/tachi.compensating-controls --target controls-target`, with no `--architecture-path` (D-L6). `git status` after the run lists only `.tachi-build/` and the two outputs as new paths.
- **Usage.** `/usage` "Current week (all models)" read 32% before and 34% after. T073's max run used the same account at the same time, so the step isn't this run's alone. By-model output tokens after: Opus 31.8k, Sonnet 306.3k, Haiku 2.7k (Haiku leaves no transcript response).
- **The target** is unchanged: `git diff HEAD -- controls-target` is empty and its tree digest equals the one above.

## 2. What the stage produced

| File | Size | Written by | Content |
|---|---|---|---|
| `compensating-controls.md` | 787,732 B, 8,953 lines | the shipped renderer | Section 2: 408 rows (Critical 1, High 19, Medium 292, Low 96). Section 3 names 180 findings (9 + 171). Section 4: 399 blocks numbered 1 to 399 (effort Medium 284, Low 107, High 8). Section 7: 10 flags. Ends with the renderer's provenance comment |
| `compensating-controls.sarif` | 898,355 B | the shipped renderer | 408 results, 8 rule IDs, levels error 20, warning 292, note 96; statuses found 9, partial 171, missing 228; provenance `render-compensating-controls.py`, digest equal to the stage record's |

An independent reader (its own table parsers, not the shipped ones) ran 37 checks, and all 37 pass: the same set as the default run's (reference set, one schema, row counts, scores and bands against the scored input, residual = inherent x (1 - factor) with one factor per status, every total in Sections 1, 2 and 5, Section 4's one block per gap finding, SARIF N/N and fingerprints, `.md` and SARIF agreement, flags, provenance and sha256 against the stage record). Its Section 7 check first compared only category flags; this run's second flag kind (a narrative fallback) made it fail, so it now compares every (finding, flag) pair, and both runs pass it.

## 3. Tokens, model and effort

| | Model (requested = served) | Effort | Responses | Output tokens | Thinking |
|---|---|---|---|---|---|
| Main session | Opus 5.5 | **max** | 36 | 30,787 | 15,719 |
| 39 control analyzers (38 + 1 retry) | Sonnet 5.5 (the agent's pinned `sonnet`) | **medium** | 203 | 306,284 | 63,041 |
| **Total** | | | **239** | **337,071** | **78,760 (23%)** |

- Each response is counted once at `usage.output_tokens`, as in T021. No turn fell back to another model, and none stopped at `max_tokens`. Main stops: 14 `tool_use`, 22 `end_turn`. Agent stops: all `tool_use` (each ends with its hand-back call).
- Per first-attempt agent: 5,206 to 11,190 output tokens (median 7,696); the retry agent 7,128. The largest single agent response was 8,640 tokens, the largest main response 4,978.
- `/usage`'s Sonnet figure (306.3k) equals the agents' count. Its Opus figure (31.8k) is 1.0k above the main transcript's.
- **Effort reached the main session only.** All 36 main responses carry effort max and all 203 agent responses carry medium: the agent file pins `model: sonnet` and sets no effort. R-18's second level here changes the dispatcher, not the analyzers.

## 4. The stage record

`tachi.stage-record/1`, status `success-with-warnings`, tool version 4.48.4, started 15:47:07Z, finished 15:52:30Z. Counts: units 408, open 408, resolved 0, rendered 408, parse_errors 0, narrative_fallbacks 1, truncations 0, cell_overwrites 0, input 10. Batches: planned 38, dispatched 39, done 38, exhausted 0, retried 1, split 0. `overflow_events` holds one entry (B028, attempt 1, kind `invalid`) and `retries` one (B028, cause `invalid`, no children); `undeclared_paths` is empty; the retry budget is 1 used of 76. The plan's batch size is 11: 28 batches of 11 and 10 of 10, and the retry kept B028's 11 findings together. Step exits: prerequisites 0, `plan` 0, `reconcile` 3 and then 0, renderer 5.

## 5. The timeline and the completion rule

All 39 launches were background (`async_launched`), as in the default run. The main session dispatched each wave in one message, ended its turn, and resumed on completions (22 turn ends in 36 responses).

| Offset from submit (mm:ss) | Event |
|---|---|
| 0:06 to 0:19 | Prerequisites listing and `--version` check (exit 0, "python 3.14.4"); `plan` (exit 0): 408 units, 38 batches |
| 0:25 to 0:45 / 0:47 | Wave 1, 16 Agent calls in one message; main ends its turn. An inline program runs at 1:40 |
| to 1:47 | Wave 1's last agent finishes (16 hand-backs and 16 notices by then) |
| 2:10 to 2:31 / 2:33 | Wave 2 (16 calls), 23 s after wave 1's last report; main ends its turn. Last agent finishes at 3:35 |
| 3:38 to 3:45 / 3:46 | Wave 3 (6 calls), 3 s after wave 2's last report. Last agent finishes at 4:37 |
| 4:46 | `reconcile`, first call, exit 3: 37 of 38 done, B028 pending (its part was invalid) |
| 4:53 | Wave 4: 1 Agent call, the B028 retry, the one batch `reconcile` listed. Two inline programs run at 4:59 and 5:06. The retry agent finishes at 5:34 (41 s) |
| 5:37 / 5:43 | `reconcile`, second call, exit 0 (38 of 38 done); renderer, exit 5 |
| 6:28 / 6:58 | One more inline program (after the render); final report complete (timer "6m 57s") |

- **Disposition (b), ordering: no departure.** The first `reconcile` ran after all 38 agents of waves 1 to 3 had reported (9 s after the last report), the second after the retry agent's report (4 s), the renderer after `reconcile` exited 0, and no wave started before the one before it had reported. The retry wave listed exactly B028.
- **Every agent reported both ways:** 39 of 39 had a hand-back and a completion notice, the first within 5.5 s of its agent's last record. 9 hand-backs and 15 notices arrived as queued attachments, not as user records (observation 8).

## 6. SC-3, structure only (US-1a #6)

- **Agent types.** 39 of 39 dispatches name `tachi-control-analyzer`, and all 39 subagent files carry that type. Each prompt equals the command's fixed text (39 of 39); each call carries only `description`, `prompt` and `subagent_type`. The agents' 195 Reads, 39 Globs and 5 Greps of the target all stayed inside it, and 0 Reads left the adopter.
- **The main session** used Bash 10 times and Agent 39 times, and no Read, Write or Edit. 5 Bash calls ran a shipped script (the `--version` check, `plan`, `reconcile` twice, the renderer) and 1 was a shell listing with file tests. **4 were inline `python3 -c` programs the main session wrote**: 1 while wave 1 ran, 2 while the retry ran, 1 after the render. All four only read JSON files and printed (no write pattern in any), but the command says it runs only its two shipped scripts and writes no script of its own. That is the departure behind this record's FAIL.
- **The agents** used Read 291, Glob 40, Grep 9, Write 40 and the hand-back call 39. All 40 Writes are `.json` files, each to the agent's own part path (1 agent wrote its part twice). 0 program-file extensions, 0 Bash.
- **Hand-backs.** 39, 688 to 1,593 bytes each, 0 with a code fence and 0 with a program-like line.
- **The two outputs** were written only by the renderer's one call: the stage record's sha256 values equal the files, both carry the renderer's stamp, `undeclared_paths` is empty, and no Write or Edit named either file.

## 7. The final report against Step 6

- **Verbatim:** the renderer's 4 summary lines (4 of 4) and its 2 warning lines (2 of 2) were printed as exact lines, in code blocks, and the Next steps block as 7 of 7 lines. The default run printed its 4 summary lines exactly but paraphrased both warnings (0 of 2).
- **Added beyond the renderer's lines, the warnings and the Next steps block:** 13 lines (2,173 B) in the final message (40 lines, 3,433 B), plus one 157 B line before the last inline program. Class: a status paragraph restating the batch and retry outcome (1 line), 2 caption lines, a self-written assessment of how well the agents scanned, with batch-, finding- and file-level claims (8 lines), and a closing recommendation with a re-run command (2 lines). The default run added 5 lines (1,334 B).
- **Numbers:** outside the renderer's lines there are 3 standalone numbers (a batch count, the exit code and a section number); every other digit sits in an ID or path. Step 6 says to restate no number and compute none, and names only the renderer's lines (the warnings, from Step 5) and the Next steps block; the added assessment rests on the main session's own inspections (section 6).

## Reference reads (structure only)

Counted from the agents' Read calls, over the 38 first-attempt agents (the B028 retry agent is counted apart). The installed `control-analyzer.md` marks all of these MANDATORY. "Default" is the default-effort run, counted with the same script.

| Read by | Max, of 38 | Default, of 38 |
|---|---|---|
| their own batch input | 38 | 38 |
| `tachi-shared/references/part-file-contract-shared.md` | 38 | 38 |
| `tachi-control-analysis/references/control-categories.md` | 9 | 5 |
| `evidence-criteria.md` | 6 | 0 |
| `residual-risk.md` | 2 | 0 |

- All five: 2 agents (default 0). The contract was read before the agent's first Write by 38 of 38 (default 38 of 38). The retry agent read its batch input and the contract, and none of the other three.
- **Failed Reads on a user-level skills path: 0** (default 9, one each by 9 agents, and each of the 9 then read the adopter's copy of the same file). All 56 skill-reference Reads used the adopter's `.claude/skills/`; no Read of a user-level path succeeded.

## 8. Verdicts

- **TW-L2:** attempt 1 of at most 2. Class: **an agent off its contract**, the main session's 4 inline programs (disposition (b)). Not a shipped-code defect (the renderer ran on 3.14.4 without trouble, and the shipped check caught the bad part), no interruption. By TW-L2's text: record it, file a follow-up, and don't claim SC-3 for the controls stage at max. Nothing in the text calls for a second attempt; the orchestrator decides.
- **PM fallback return (ruling 2):** 1 of 80 narrative fields fell back (coverage 1 of 20; configuration, currency and completeness 0 of 20 each), below 10%. It is an agent's slip on the numeral rule, so no slot that should resolve fell back, and the rate calls for no follow-up. The other agent text fields never fell back: 408 matrix rows, 399 recommendation bodies, 183 evidence snippets and 183 summaries.
- **US-1a #3 for controls, US-3 #5 and SC-5 hold on this run.** US-1a #6 and SC-3 do not.

## 9. Observations

1. **The dispatcher changed, the analyzers didn't.** At max the main session thought for 15,719 tokens (default 589), ran 4 inline programs (default 0) and wrote a longer final report; the 203 agent responses ran at the same effort as the default run's.
2. **One bad part, one retry.** B028's first part held a Section 2 row of 10 cells where the schema has 11. The shipped reader rejected the whole part, `reconcile` exited 3, and one re-dispatch at the same size produced a valid part (1 of the 76 retries, one agent of 7,128 output tokens, 51 s between the two `reconcile` calls). 0 of 38 first attempts failed at default. This is the SC-5 guard working live; the retry's control status differs from the rejected attempt's on 3 of 11 findings.
3. **Control Category spelling.** In 9 of 408 Section 2 rows the agent's cell reads "Logging Audit" (5), "CSP Security Headers" (3) or "CSP / Security Headers" (1) where the template's names are "Logging/Audit" and "CSP/Security Headers". The renderer flagged exactly those 9 (`input:control_category:sources-disagree`, in Section 7 and the SARIF) and left the cells as written; the default run had 10.
4. **One narrative fallback** (the 10th flag): D-28's coverage rationale, flagged `input:evidence.assessment.coverage:narrative-fallback` in Section 7 and the SARIF.
5. **No architecture snapshot (D-L6).** `architecture_warning` is empty, no batch input names an architecture file, and 0 agent Reads opened one; the agents mapped components by heuristics. All 408 SARIF locations carry `docs/security/architecture.md`.
6. **Three batches opened no target file.** The agents of B036 to B038 made only a listing or search of the target; the default run had 4 such agents (B004, B005, B036, B037). The shipped part check accepted those parts: it checks structure, not scan depth.
7. **3.14.4 held.** Every script ran on Python 3.14.4, the renderer included. Each script call ended with an echo of its exit code, so the tool's error flag stayed clear for exit 3 and exit 5, and the main session routed both as the command says.
8. **Counting reports.** Counted from user records and from queued attachments, the default run's 38 of 38 agents also had both a hand-back and a notice (2 of its notices were queued attachments), so that record's "two completions without a notice" is an undercount.
9. **Scale.** 826 output tokens per finding (337,071 over 408) against 736 at default, with the Claude Code point release (2.1.330 to 2.1.331) landing between the two launches. This record claims no SC-8 delta; T075 owns it.
