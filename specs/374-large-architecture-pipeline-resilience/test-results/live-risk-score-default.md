# T073 live run: `/tachi.risk-score` on the fixture, adopter default effort, attempt 1 (W5, PR 1)

**Date:** 2026-11-24. **Base:** the lane at `84a1103`. **Inputs:** [w5-setup-pr1.md](w5-setup-pr1.md) (arrangement, dispositions, D-L2), [sc8-baseline.md](sc8-baseline.md) and [prefix-baseline.md](prefix-baseline.md) (how T021 launched, counted and timed), spec US-1a #1 and #6, tasks T073. **Run:** one live `/tachi.risk-score` on the install `v4.48.4-154-g27d58bdc` (Claude Code 2.1.331, macOS) at `--effort medium`, on the fixture's precomputed `threats.md`. The max-effort run is a separate record.

## Result

| Question | Result |
|---|---|
| Verdict | **PASS** on US-1a #1 and #6 (structure) at the default effort. Attempt 1 of 2 (TW-L2). One observation may be a disposition-(b) departure (section 8, item 1) |
| `risk-scores.md` | 408 open rows, one per open finding, in each of Sections 2, 3 and 4: the fixture's 408 Section 7 IDs (0 missing, 0 extra, 0 duplicated). 6 RESOLVED rows in Section 2a, equal to Section 4c's 6 |
| `risk-scores.sarif` | 408 results, 408 distinct `findingId/v1`, no RESOLVED ID, no `relatedLocations`: N/N holds. Composite, band, CVSS and source agree with the `.md` on all 408 |
| Stage record | 326 units. Batches planned 26, dispatched 26, done 26. Retried 0, split 0, exhausted 0. Overflow events 0, retries 0. Narrative fallbacks 0, truncations 0, parse errors 0. Status `success-with-warnings` |
| Batches (F17's p90 sizes) | 14 of 13 and 12 of 12, in two waves (16 and 10). The largest response was 7,671 output tokens |
| Output tokens (P-7) | **219,626**: main session (Opus 5.5) 9,619; 26 agents (Sonnet 5.5) 210,007. Thinking 16,767 (7.6%) |
| Wall time | **2 min 53 s** (the session's own timer) |
| Who wrote the files | The shipped renderer. The main session made no Write or Edit. Both files carry the renderer's provenance stamp, and their digests equal the stage record's |
| Exit codes | presence check 0, populator 0, `plan` 0, `reconcile` 0 (one call), render 5. The stage's final exit is 5, disposition (a)'s pass state |
| SC-3, structure only | 0 stand-in dispatches, 0 unshipped scripts run, 0 program files written, 0 code hand-backs |
| `/usage`, "Current week (all models)" | 31% before, 32% after. T074's session ran on the same account at the same time |

## 1. The arrangement

- **Adopter.** A fresh `git clone` of `<adopter w5-fixture-score>` (restore point `93bd5ca`, above the commit "Install tachi v4.48.4-154-g27d58bdc") into a new directory, with the generic repo-local identity. It was clean before the run. Inputs: the fixture's `threats.md` (sha256 `44694eb5...`) in `docs/security/2026-10-19T09-30-00/` and its architecture description at `docs/security/architecture.md` (sha256 `5ee33b33...`). Both equal [w5-setup-pr1.md](w5-setup-pr1.md) section 2.
- **Launch (D-L2).** A detached tmux session (200 x 50), cwd the clone, running `env -i` with `HOME`, `USER`, `LOGNAME`, `SHELL=/bin/zsh`, `TERM=xterm-256color`, `LANG=en_US.UTF-8` and a `PATH` of the user's bin directory, `/opt/homebrew/bin` and the system directories, then `claude --effort medium`. **Deviation from "account defaults":** the flag. The account's settings now open Opus 5.5 at xhigh, and T021 recorded medium as the default. Auto permission mode, no session profile. The banner read Opus 5.5 with medium effort.
- **Trust dialog.** The first launch was closed by a wrong key on the dialog (its cursor starts on "No, exit") before any command. The clone was untouched (`git status --ignored` empty, no project state). The relaunch used the same clone and the answer "Yes, I trust this folder". It is not an attempt.
- **The version.** The session ran Claude Code 2.1.331. T021 and the setup record had 2.1.330. The launcher's link moved to 2.1.331 at 10:28 that morning, an update this lane didn't run, minutes before the launch.
- **Prompts.** None on screen. Auto mode accepted every tool use in the records (32 of the main session's, 145 of the agents'), and none was denied.
- **The command.** `/tachi.risk-score`, no arguments, submitted at 10:29:27 US Eastern. It auto-detected the input directory.

## 2. What the stage produced

| | Result |
|---|---|
| `risk-scores.md` | 1,516,551 B. Section 1 says 408 scored: 0 Critical, 5 High, 302 Medium, 101 Low. Section 2 is sorted by composite descending (maximum 8.1), with `fresh` in the Source column on all 408. Section 2a holds 6 rows, all `RESOLVED`. Written by the renderer |
| `risk-scores.sarif` | 785,096 B, 408 results (5 `error`, 302 `warning`, 101 `note`) and 8 rules. Written by the renderer |

The completeness check ran in the work directory with its own table parser, against Section 7 and Section 4c of the committed fixture, not with the shipped parser. The tracked tree is unchanged: `threats.md` is byte-identical (the populator wrote nothing new), and the only new paths are `.tachi-build/`, `risk-scores.md` and `risk-scores.sarif`. The stage record's `undeclared_paths` is empty.

## 3. Tokens, model and effort

| | Model | Effort | Responses | Output tokens | Thinking |
|---|---|---|---|---|---|
| Main session | Opus 5.5 | medium | 21 | 9,619 | 706 |
| 26 `tachi-risk-scorer` agents | Sonnet 5.5 (the agent's pinned `sonnet`) | medium | 117 | 210,007 | 16,061 |
| **Total** | | | **138** | **219,626** | **16,767 (7.6%)** |

- Requested equals served on all 138 responses, effort is medium on all, and no response carries a fallback credit. Stops: main 8 `tool_use` and 13 `end_turn`; agents 117 `tool_use` (each ends on its hand-back call); 0 `max_tokens`. Every request carried `max_tokens` 128,000.
- Each response counted once by message ID (no ID had records with differing counts). `/usage`'s by-model lines: Sonnet 210.0k (equal), Opus 9.9k (0.3k above the transcripts) and Haiku 3.3k (calls that leave no transcript response).
- Each agent's one Write was 6,353 to 7,671 output tokens (median 7,069), at most 6% of the cap, for a part file of 12,937 to 16,803 B: 2.29 to 2.38 bytes per visible token. That is below T021(b)'s 2.71 and 2.80 for whole files and below D6's constant of 3.2.

## 4. The stage record (`tachi.stage-record/1`)

Plan `<plan>`, started 15:29:38Z and finished 15:32:12Z; `batch_size` 13; retry budget 52, used 0; the plan was all fresh (every `score-source` is `fresh`). Counts: units 326, open 408, rendered 408, resolved 6. The record names two warnings, as disposition (a) predicted: `baseline-unresolved` and `architecture-path:body-line:absent`. It holds no per-step exit codes and no token field, so the exit codes above come from the transcript. All 26 parts are first attempts (`B001.a1.json` to `B026.a1.json`) under one plan ID, with 326 items in all.

## 5. Timeline and the completion rule

All 26 agents ran as background agents (the transcript metadata for each says `background`). The Agent calls named no flag. The main session kept the rule: it ended its turn after each wave's dispatch, resumed on completion notices, made no tool call between a dispatch and that wave's last hand-back, and finished the stage only after its renderer call.

| Offset from submit (m:ss) | Event |
|---|---|
| 0:03 / 0:05 | Step 1's presence check (exit 0, `python 3.14.4`), then one inspection call on the input directory |
| 0:08 / 0:11 | Populator (exit 0), `plan` (exit 0): 326 units, 26 batches, waves of 16 and 10 |
| 0:14 | **Wave 1**: 16 Agent calls in one message. Its agents' first records came at 0:35 |
| 1:20 to 1:30 | Wave 1's 16 hand-backs. Each agent ran 45 to 55 s (median 49 s) |
| 1:34 | **Wave 2**: 10 Agent calls in one message, after wave 1's last hand-back. First records at 1:47 |
| 2:29 to 2:36 | Wave 2's 10 hand-backs (42 to 49 s each, median 45 s) |
| 2:41 | `reconcile`, once, exit 0, five seconds after the last of the 26 hand-backs |
| 2:44 | Renderer, exit 5 (success with warnings) |
| 2:53 | Final report complete (the timer reads 2m 53s) |

Disposition (b) check: no `reconcile` before every listed wave's agents reported, no render before `reconcile` exited 0, and no second `reconcile` or re-dispatch (nothing was pending). The stage's end was judged only after the final report was printed and all 26 agents had handed back.

## 6. SC-3, structure only (US-1a #6)

| Check | Result |
|---|---|
| Main session tools | 6 Bash and 26 Agent. No Write, Edit or other tool |
| Main session Bash | Each call is `cd <adopter>;` then literal arguments. Four are shipped-script calls (`tachi-stage.py` with `plan` and `reconcile`, `populate-affected-assets.py`, `render-risk-scores.py`). The presence check (`tachi-stage.py --version`) shares a call with `ls`, and one call is `ls` plus a `grep` of the input. All but the `grep` call end with an `echo` of the exit code. No script was written or run besides the shipped ones |
| Agent dispatches | 26, all `tachi-risk-scorer` (26 of 26 in the transcript metadata too), spawn depth 1. 0 `general-purpose` or other types. Each prompt is the command's fixed line with the batch's own input path: 26 of 26, each path exists, each batch ID equals its Agent call's description |
| What the agents did | Read 62, Grep 32, Write 26, hand-back 26, Glob 1; no Bash. All 26 Writes are `.json` files in `<plan>/parts/`: no program file anywhere |
| Hand-backs | 26, of 312 to 1,447 bytes, with 0 code fences: no code returned to the caller |
| Stamps | `risk-scores.md` ends with the renderer's provenance comment; `risk-scores.sarif` holds `tachi_provenance`. Both stamps name `render-risk-scores.py`, version 4.48.4 |

## 7. TW-L2 and fallback verdicts

- **TW-L2:** no failure, so no class applies and no fix-and-rerun is called for. The stage's claims hold on attempt 1. One departure candidate stands in section 8, item 1, for the orchestrator to rule on.
- **Fallback rate (ruling 2):** 0 of the 1,304 narrative fields the agents wrote (326 units, 4 fields each). That is under 10% and 25%, and no slot that should resolve fell back.
- **Not exercised:** US-1a #4 and #5 (re-dispatch, overflow and retry paths), since every batch finished first time. This record claims neither.

## 8. Observations

1. **A judgment paragraph in the final report (possible departure from Step 6).** The report printed the renderer's three summary lines, both warnings and the Next steps block as the command says. Between them it added about five lines of caveat on the ranking, built from the agents' hand-back notes and naming five fixture findings, and a one-line re-run suggestion. Step 6 says to print the renderer's lines as written, restate no number and compute none. The caveat restates the Critical count in words and tallies what "most" agents did, which the renderer does not state. It writes no file and changes no number. Whether it is off-contract is the orchestrator's ruling.
2. **Two inspection calls.** A presence listing and a `grep` of the input ran outside the named scripts. Step 1 says the command never parses the input itself. Both are read-only and belong to none of SC-3's four classes.
3. **What the agents read.** Each agent made 2 or 3 successful Reads and 1 or 2 Greps (8 Reads and 32 Greps hit `threats.md`). The last section tabulates them against the agent file's MANDATORY marks: 26 of 26 read the part contract, and 1 of 26 read any scoring reference.
4. **The score distribution moved against T021(a).** The same fixture now gives Critical 0, High 5, Medium 302, Low 101, against 0, 27, 348, 33 at v4.48.4. Of the input's 56 Critical-risk findings, 0 reach the Critical band: 1 High, 45 Medium and 10 Low (before: 19, 34 and 3). It is one run at one effort, so it doesn't say how much is agent variance.
5. **Latency.** A wave took 1:16 (16 agents) and 1:02 (10) from dispatch to its last hand-back; agents began 21 s and 13 s after dispatch. T021(a)'s unbatched run took 7:55 for the same fixture. The agents' 26 Writes sit well inside the cap, so the sizes need no narrowing here.
6. **Python 3.14.4** (the clean environment's) ran the three shipped scripts (five calls) with no error. It is outside CI's range, and this is the first live render on it.
7. **Comparability for T075.** T021(b)'s baselines were taken on Claude Code 2.1.330, and this run is on 2.1.331. A client update is a difference in P-7's same-session conditions, so T075 should record its version.
8. **Usage.** The weekly percentage moved one point while T074 ran beside it on the same account, so it can't be split between the two runs.

## Reference reads (structure only)

Source: the 26 agent transcripts (tool names, paths and counts) and the 26 hand-back notes (sentence classes, no text). Line numbers are the installed `risk-scorer.md`'s. The per-agent rows stay with the private notes.

| Read | Agents of 26 | Where the agent file marks it |
|---|---|---|
| Own batch input | 26 | line 48 |
| `part-file-contract-shared.md`, before the first Write | 26 (one needed a second try at the path) | line 42, MANDATORY |
| `cvss-vectors.md` | 1 (B020) | line 144, MANDATORY |
| `trust-zones.md`, `asset-modifiers.md`, `scoring-dimensions.md`, `reachability-analysis.md`, `severity-bands.md`, `output-formatting.md` | 0 each | lines 134, 154, 164 and 174, 184, 210 and 218, 226: all MANDATORY |
| Section 2 of the `threats` file | 26 got part or all of it: all five zone rows 10, one to four rows 16. Each got every zone row its own batch needs | lines 136 and 192 (required) |
| An architecture file | 0 (no Read, no Grep). All 26 batch inputs' `refs` name only `threats` | line 193: optional |

**Reason classes in the 26 notes** (counts of notes, no text). Scoring references: 13 say they weren't read (11 with no reason, 1 a time-saving reason, 1 keeping its own judgment independent of the scores) and 13 don't mention them. Architecture file: 14 say it wasn't read (10 with no reason, 4 because the batch input's `refs` named none) and 12 don't mention it. "The input carried it": 0 notes. "The renderer's step": 0 notes.

**Lines that bear on whether a read is needed (named, not ruled).** Line 44 puts a base score, a mean, a reachability score, a composite and a band with the renderer, and lines 58 to 64 split what the agent writes from what the renderer computes. Line 128 says the units carry the finding rows; here they carry no zone, trust-level or architecture field. Lines 136 and 138 tell the agent to read Section 2 and how to write `zone` and `trust_level`. Lines 148 and 150 (no score; the category default vector is the starting point, and `cvss-vectors.md` lists the defaults), 156 and 158 (the asset pass and `affected_assets` are the renderer's), 168 and 178 (four sub-scores each; the renderer takes the means) and 202 (no reachability score) bear on the other references. Lines 212, 220 and 228 (Sections 7 to 9) say the same of the composite, band, governance fields and both files, outside 111 to 193. The renderer flagged no row: the Flags column is empty on 408 of 408.
