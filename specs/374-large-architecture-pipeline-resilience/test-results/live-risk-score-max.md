# T073 live run: `/tachi.risk-score` on the fixture, `effort=max`, attempt 1 (W5, PR 1)

**Date:** 2026-11-24. **Base:** the lane at `84a1103`. **Inputs:** [w5-setup-pr1.md](w5-setup-pr1.md) (arrangement, dispositions, D-L2), [live-risk-score-default.md](live-risk-score-default.md) (the default-effort run, whose shape this follows), [sc8-baseline.md](sc8-baseline.md) and [prefix-baseline.md](prefix-baseline.md) (how T021 launched, counted and timed), spec US-1a #3 and #6 and SC-3, tasks T073. **Run:** one live `/tachi.risk-score` on the install `v4.48.4-154-g27d58bdc` (Claude Code 2.1.331, macOS) at `--effort max`, on the fixture's precomputed `threats.md`.

## Result

| Question | Result |
|---|---|
| Verdict | **US-1a #3 holds** for the scorer at `effort=max` (main session at max, agents at medium). **US-1a #6 is not claimed:** the main session ran six inline programs of its own, a departure under disposition (b) (section 5). Class: an agent off its contract, not a shipped-code defect. Attempt 1 of 2 (TW-L2) |
| `risk-scores.md` | 408 open rows, one per open finding, in each of Sections 2, 3 and 4: the fixture's 408 Section 7 IDs (0 missing, 0 extra, 0 duplicated). 6 RESOLVED rows in Section 2a, equal to Section 4c's 6 |
| `risk-scores.sarif` | 408 results, 408 distinct `findingId/v1`, no RESOLVED ID, no `relatedLocations`: N/N holds. Composite, band, CVSS and source agree with the `.md` on all 408 |
| Stage record | 326 units. Batches planned 26, dispatched 26, done 26. Retried 0, split 0, exhausted 0. Overflow events 0, retries 0. Narrative fallbacks 0, truncations 0, parse errors 0. Status `success-with-warnings`. Exits: presence check 0, populator 0, `plan` 0, `reconcile` 0 (one call), render 5 (disposition (a)'s pass state) |
| Batches (F17's p90 sizes) | 14 of 13 and 12 of 12, in two waves (16 and 10). The largest response was 7,901 output tokens |
| Output tokens (P-7) | **249,338**: main session (Opus 5.5) 40,605; 26 agents (Sonnet 5.5) 208,733. Thinking 40,004 (16.0%): 24,303 main, 15,701 agents |
| Wall time | **6 min 29 s** (the session's own timer) |
| Model and effort | Main session Opus 5.5 at **max** on 22 of 22 responses. The 26 agents ran at **medium** on 116 of 116 (section 3) |
| Who wrote the files | The shipped renderer. The main session made no Write or Edit, and each agent wrote only its part |
| SC-3, structure only | Agents: 0 stand-ins, 0 program files, 0 code hand-backs, every output stamped. Main session: 6 inline unshipped programs, all read-only. Not claimed |
| Final report vs Step 6 | 13 of its 23 non-blank lines were added to the renderer's lines, the warnings and the Next steps block (section 6) |
| `/usage`, "Current week (all models)" | 32% before, 34% after. T074's max session ran on the same account at the same time |

## 1. The arrangement

- **Adopter.** A fresh `git clone` of `<adopter w5-fixture-score>` (restore point `93bd5ca`, above "Install tachi v4.48.4-154-g27d58bdc") into a new directory, with the generic repo-local identity. Clean before the run. Inputs: the fixture's `threats.md` (sha256 `44694eb5...`) in `docs/security/2026-10-19T09-30-00/` and its architecture description at `docs/security/architecture.md` (sha256 `5ee33b33...`), both as [w5-setup-pr1.md](w5-setup-pr1.md) section 2 has them.
- **Launch (D-L2).** A detached tmux session (200 x 50), cwd the clone, running `env -i` with `HOME`, `USER`, `LOGNAME`, `SHELL=/bin/zsh`, `TERM=xterm-256color`, `LANG=en_US.UTF-8` and a `PATH` of the user's bin directory, `/opt/homebrew/bin` and the system directories, then `claude --effort max`. **Deviation from "account defaults":** the flag (the account's settings open Opus 5.5 at xhigh; `max` is R-18's second level). Auto permission mode, no session profile. The banner read "Opus 5.5 with max effort". The trust dialog was answered "Yes, I trust this folder" on the first try.
- **Prompts.** None on screen. Auto mode accepted all 45 of the main session's tool uses (18 Bash, 26 Agent, 1 Read) and all 145 of the agents', and denied none.
- **The command and version.** `/tachi.risk-score`, no arguments, submitted at 10:45:54 US Eastern; it auto-detected the input directory. The session ran Claude Code 2.1.331, as the default-effort run did. T021's baselines were taken on 2.1.330.

## 2. What the stage produced

| | Result |
|---|---|
| `risk-scores.md` | 1,519,066 B. Section 1 says 408 scored: 0 Critical, 5 High, 296 Medium, 107 Low. Section 2 is sorted by composite descending (maximum 8.4), `fresh` in the Source column on all 408. Section 2a holds 6 rows, all `RESOLVED`. Written by the renderer |
| `risk-scores.sarif` | 785,065 B, 408 results (5 `error`, 296 `warning`, 107 `note`), 8 rules, SARIF 2.1.0. Written by the renderer |

The completeness check ran in the work directory with its own table parser, against Section 7 and Section 4c of the committed fixture, not with the shipped parser. The tracked tree is unchanged: `threats.md` is byte-identical, and the only new paths are `.tachi-build/` (55 JSON files: the plan, `current.json`, the stage record, 26 inputs, 26 parts), `risk-scores.md` and `risk-scores.sarif`. The stage record's `undeclared_paths` is empty. `{{...}}` slot markers: 0 in Sections 1 to 5. Section 6's Inputs listing keeps them unresolved on purpose (the output schema says so).

## 3. Tokens, model, effort and the stage record

| | Model | Effort | Responses | Output tokens | Thinking |
|---|---|---|---|---|---|
| Main session | Opus 5.5 | **max** | 22 | 40,605 | 24,303 |
| 26 `tachi-risk-scorer` agents | Sonnet 5.5 (the agent's pinned `sonnet`) | **medium** | 116 | 208,733 | 15,701 |
| **Total** | | | **138** | **249,338** | **40,004 (16.0%)** |

- Requested equals served on all 138 responses, and no response carries a fallback credit. Stops: main 18 `tool_use` and 4 `end_turn`; agents 116 `tool_use` (each agent ends on its hand-back call); 0 `max_tokens`. Every request carried `max_tokens` 128,000. Each response is counted once by message ID. `/usage`'s by-model lines: Sonnet 208.7k (equal), Opus 40.7k (0.1k above the transcripts), Haiku 2.0k (calls that leave no transcript response).
- **The session's effort did not reach the agents.** `--effort max` set max on the main session's 22 responses. Each of the 116 agent responses records medium, as the default-effort run's did, and the agent file sets no effort. So R-18's second level exercised the main session at max and the scorer's judgment at medium.
- Each agent's one Write was 6,419 to 7,901 output tokens (median 7,090, at most 6.2% of the cap), for a part file of 13,384 to 17,044 B: 2.26 to 2.38 bytes per visible token. An agent ran 40 to 50 s (median 43 s) and made 4 to 6 responses.
- Against the default-effort record (219,626 tokens, 2 min 53 s): the total is 29,712 higher (13.5%), all of it in the main session (+30,986, with the agents 1,274 lower), and the wall time 3 min 36 s longer.
- **Stage record** (`tachi.stage-record/1`): plan `<plan>`, started 15:46:36Z and finished 15:50:40Z; `batch_size` 13; retry budget 52, used 0; all fresh. Counts: units 326, open 408, rendered 408, resolved 6. Two warnings, as disposition (a) predicted: `baseline-unresolved` and `architecture-path:body-line:absent`. It holds no per-step exit codes and no token field, so those come from the transcript. All 26 parts are first attempts (`B001.a1.json` to `B026.a1.json`) under one plan ID, with 326 items and 1,304 narrative fields (4 per unit).

## 4. Timeline and the completion rule

All 26 agents ran as background agents (their metadata says `background`). Offsets run from the submit.

| Offset (m:ss) | Event |
|---|---|
| 0:03 to 0:45 | Step 1's presence check (exit 0, `python 3.14.4`), two listings and a grep of the input, the populator (exit 0), `plan` (exit 0): 326 units, 26 batches in waves of 16 and 10, then a read-only pretty-print of the plan |
| 0:53 | **Wave 1**: 16 Agent calls in one message. First agent records at 1:13 |
| 1:54 to 2:00 | Wave 1's hand-backs. The main session ended its turn three times (1:17, 1:59, 2:16) and made no tool call from the dispatch to the last hand-back |
| 2:29 | **Wave 2**: 10 Agent calls in one message, after wave 1's last hand-back. First records at 2:41 |
| 2:51, 2:58, 3:14 | Three Bash calls while wave 2 ran: two `python3 -c` programs and one heredoc program, all read-only. The main session did not end its turn in this wave |
| 3:31 | Wave 2's last hand-back |
| 3:39 | A fourth inline program (heredoc) |
| 4:16 | `reconcile`, once, exit 0, 45 s after the last hand-back. Its call also carries an inline pretty-printer |
| 4:24 | A sixth inline program (heredoc) |
| 4:45 | Renderer, exit 5 (success with warnings) |
| 4:46 to 5:28 | Five read-only calls: 4 Bash and 1 Read (an 85-line range of the shipped planner's source) |
| 6:26 | Final report complete (the timer reads 6m 29s) |

Disposition (b) check: no `reconcile` before every listed wave's agents reported, no render before `reconcile` exited 0, no second `reconcile` and no re-dispatch (nothing was pending). The stage's end was judged only after the final report was printed and all 26 agents had handed back. The departures that do exist are in sections 5 and 6.

## 5. SC-3, structure only (US-1a #6)

| Check | Result |
|---|---|
| Agent dispatches | 26, all `tachi-risk-scorer` (26 of 26 in the metadata too), depth 1. 0 `general-purpose` or other types. Each prompt is the command's fixed line with the batch's own input path: 26 of 26, each path exists, each batch ID matches its call's description |
| What the agents did | Read 62, Grep 31, Write 26, hand-back 26; no Bash, no Glob. All 26 Writes are `.json` files in `<plan>/parts/`: 0 program files |
| Hand-backs | 26, of 295 to 1,372 bytes, with 0 code fences: 0 code hand-backs |
| Stamps and paths | `risk-scores.md` ends with the renderer's provenance comment and `risk-scores.sarif` holds `tachi_provenance`; both name `render-risk-scores.py` 4.48.4, and both digests equal the stage record's. `undeclared_paths` is empty |
| Main session tools | 18 Bash, 26 Agent, 1 Read. No Write, Edit or other tool. Three shipped calls redirected their output into 6 data files in the session's own scratchpad (`.json`, `.err`, `.out`), none in the adopter |
| Main session Bash (18) | 5 run the named shipped steps (presence check, populator, `plan`, `reconcile`, render). **6 run an inline program the main session wrote** (3 heredocs and 3 `python3 -c`, one of them in the `reconcile` call): none wrote a file, 3 parse `threats.md`, the rest read the plan, a batch input or `reconcile`'s output. The other 8 are read-only: listings, greps, a `json.tool` call, `git status` and `git diff` |

The command says it "runs only the shipped scripts it names" (Overview) and "never parses either file itself" (Step 1), and SC-3's column reads "0 unshipped scripts run". The six inline programs run code the command doesn't name, and three parse the input, so this record doesn't claim US-1a #6 at this level. They were read-only and changed no output.

## 6. Final report against Step 6

- Step 6 says to print the renderer's summary lines as written, restate no number and compute none (Step 5 adds the warnings on exit 5), then the Next steps block.
- The final report was 28 lines (23 non-blank). The renderer's three summary lines and two warnings (5) and the Next steps block (5) came as written. **13 non-blank lines were added**: 4 code-fence markers, 1 opening line, a 6-bullet caveat block under a review warning, and 1 closing line on the repository's state.
- Class: a judgment layer, as in the default-effort run but longer. It restates the stage's batch and wave counts (26 and two; the renderer prints neither) and a band count in words, tallies what "most" agents did, names fixture findings, and makes 2 re-run or flag suggestions. It writes no file and changes no number. Whether it is off-contract is the orchestrator's ruling.

## Reference reads (structure only)

Counts of the 26 agents, from tool names, paths, read ranges and the line numbers of Grep hits. The installed `risk-scorer.md` marks eight files MANDATORY, on ten lines: the part-file contract and the seven risk-scoring references.

| File | Agents that read it |
|---|---|
| Its batch input | 26 |
| `tachi-shared/references/part-file-contract-shared.md` | 26 |
| `tachi-risk-scoring/references/cvss-vectors.md` | 1 |
| The same directory's `trust-zones`, `asset-modifiers`, `scoring-dimensions`, `reachability-analysis`, `severity-bands` and `output-formatting` | 0 of each |
| `threats.md` Section 2 (lines 113 to 140) | 26 saw at least one of its lines (median 12 of 28): 9 by a Read of its range, 26 by a Grep whose hits fall inside it |
| The architecture file | 0 read it. `refs` names one in 0 of 26 batch inputs (each names only `threats`) |

- Of the 182 reads of the seven references (7 x 26), 1 happened. The contract read, also MANDATORY, happened 26 times. Each agent made 2 to 4 Reads (median 2) and 1 or 2 Greps.
- The fixture's architecture file sits at the default `docs/security/architecture.md`, not beside the run's `threats.md`, so the agent file's fallback (an `architecture.md` beside `threats`) finds none. The default-effort run's agents read the same files.

## 7. TW-L2 and fallback verdicts

- **TW-L2:** US-1a #3 holds for the scorer at `effort=max` (scenario 1: row parity, N/N, two or more batches, no file assembled by hand). US-1a #6 is not claimed for it: the main session departed from the command text (disposition (b)). Class: an agent off its contract, not a shipped-code defect, so no fix-and-re-run applies. Record it, file the follow-up, and don't claim the SC (KB 22). Attempt 1 of 2 at this level; a second is the orchestrator's call.
- **Fallback rate (ruling 2):** 0 of the 1,304 narrative fields (326 units, 4 each). That is under 10% and 25%, and no slot that should resolve fell back.
- **Not exercised:** US-1a #4 and #5 (re-dispatch, overflow and retry paths), since every batch finished first time. This record claims neither.

## 8. Observations

1. **The occasion for the inline programs.** `plan` prints only `plan_id`, `plan_digest` and `waves`, and nothing in Step 2 says that the units (326) can be fewer than the open findings (408). The programs compared the plan's units with the threat model's table rows, and the main session read the planner's source. Counts in `plan`'s output, or a line in the command, would remove the occasion.
2. **Latency.** A wave took 1:07 (16 agents) and 1:02 (10) from dispatch to its last hand-back, and agents began 20 s and 12 s after dispatch, as in the default-effort run. The added wall time sits in the main session: 2:55 from wave 2's last hand-back to the final report, against 0:17 at the default effort.
3. **Scores.** Critical 0, High 5, Medium 296, Low 107 (default effort: 0, 5, 302, 101; T021(a): 0, 27, 348, 33). Of the input's 56 Critical-rated findings, 0 reach the Critical band: 2 High, 45 Medium, 9 Low. One run per level, so agent variance can't be separated out.
4. **Python and usage.** Python 3.14.4 (the clean environment's) ran the five shipped-script calls with no error. The weekly percentage moved two points while T074's max session ran beside this one, so it can't be split between them.
