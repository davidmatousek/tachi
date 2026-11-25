# T073 live run: `/tachi.risk-score` on the fixture, `effort=max` with the agents at max, attempt 2 (W5, PR 1)

**Date:** 2026-11-24. **Base:** the lane at `4128537`. **Inputs:** [w5-setup-pr1.md](w5-setup-pr1.md) (arrangement, dispositions, D-L2, section 9), [t147-fixes-pr1.md](t147-fixes-pr1.md) (what changed), [live-risk-score-max.md](live-risk-score-max.md) (attempt 1 at max), [live-risk-score-default-a2.md](live-risk-score-default-a2.md) (the default effort's attempt 2), spec US-1a #3, #4 and #6, tasks T073. **Run:** one live `/tachi.risk-score` on the install `v4.48.4-162-g1e3614a` (T147's fix, `1e3614a`; Claude Code 2.1.331, macOS), the main session and the agents both at max (D-L9), on the fixture's precomputed `threats.md`. It is the stage's second and last attempt at max (TW-L2) and its first with the agents at max.

## Result

| Question | Result |
|---|---|
| Verdict | **PASS** on US-1a #3 (the scorer, agents at max) and #6 (structure). All three of the fix's targets are met: 26 of 26 agents read all four binding references, 0 lines were added beyond Step 6's, 0 unnamed programs ran. What max changed is cost: the agents spent 4.28 M output tokens (90% thinking), and 9 agent responses stopped at `max_tokens`, each absorbed inside its own agent's run (section 6) |
| Effort check | `effort` and `perTurnEffort` read max on the main session's 36 of 36 responses and on the 26 agents' 310 of 310. Requested model equals served on all 346. D-L9's launch reached the agents |
| `risk-scores.md` | 408 open rows, one per open finding, in each of Sections 2, 3 and 4: the fixture's 408 Section 7 IDs (0 missing, 0 extra, 0 duplicated). 6 RESOLVED rows in Section 2a, equal to Section 4c's 6 |
| `risk-scores.sarif` | 408 results, 408 distinct `findingId/v1`, no RESOLVED ID: N/N holds. Composite, band, CVSS and source agree with the `.md` on all 408 |
| Stage record | 326 units. Batches planned 26, dispatched 26, done 26 (14 of 13 and 12 of 12, in waves of 16 and 10). Retried 0, split 0, exhausted 0. Overflow events 0, retries 0. Narrative fallbacks 0 of 1,304 fields, truncations 0, parse errors 0. Status `success-with-warnings`. Exits: presence check 0, populator 0, `plan` 0, `reconcile` 0 (one call), render 5, which is the stage's final exit and disposition (a)'s pass state |
| Output tokens | **4,295,809**: main session (Opus 5.5) 13,754; 26 agents (Sonnet 5.5) 4,282,055. Thinking 3,882,028 (90.4%): 5,189 main, 3,876,839 agents |
| Wall time | **46 min 24 s** (the session's own timer) |
| `max_tokens` stops | 9, all agent responses (4 in wave 1, 5 in wave 2; one each in 9 of the 26 agents), each 128,000 tokens and thinking only. Claude Code resumed each agent in its own run. No part was lost (section 6) |
| Who wrote the files | The shipped renderer. The main session made no Write or Edit. Both files carry the renderer's provenance stamp, and their digests equal the stage record's |
| SC-3, structure only | 0 stand-in dispatches, 0 unnamed programs run by the main session, 0 program files written, 0 code hand-backs |
| Final report vs Step 6 | 14 non-blank lines: the renderer's five (three summary lines, two warnings), the Next steps block (five) and four code-fence lines. 0 lines added |
| `/usage`, "Current week (all models)" | 37% before, 46% after. T074's max attempt 2 started at about the same time on the same account |

## 1. The arrangement

- **Adopter.** A fresh `git clone` of `<adopter w5b-fixture-score>` (restore point `a760439`, above the commit "Install tachi v4.48.4-162-g1e3614a") into a new directory, with the generic repo-local identity. Clean before the run. Inputs: the fixture's `threats.md` (sha256 `44694eb5...`) in `docs/security/2026-10-19T09-30-00/` and its architecture description (sha256 `5ee33b33...`), equal to [w5-setup-pr1.md](w5-setup-pr1.md) section 2.
- **Launch (D-L2, D-L9).** A detached tmux session (200 x 50), cwd the clone, running `env -i` with `HOME`, `USER`, `LOGNAME`, `SHELL=/bin/zsh`, `TERM=xterm-256color`, `LANG=en_US.UTF-8`, a `PATH` of the user's bin directory, `/opt/homebrew/bin` and the system directories, **and `CLAUDE_CODE_EFFORT_LEVEL=max`**, then `claude --effort max`. **Deviation from "account defaults":** the flag and the variable (the account opens Opus 5.5 at xhigh). The variable is what carries max to the agents; attempt 1's flag alone did not. Auto permission mode, no session profile. The banner read "Opus 5.5 with max effort". The trust dialog was answered "Yes, I trust this folder" at the first try. No session command printed the environment.
- **Prompts and command.** No prompt on screen: the records hold 33 accept decisions (main session) and 693 (agents), and no other decision. `/tachi.risk-score`, no arguments, was submitted at 12:02:42 US Eastern and auto-detected the input directory. An early check of the transcripts (+1 minute: 16 agents, 61 responses) already read max throughout, so the run went on. The clean environment's Python 3.14.4 ran the five script calls with no error.

## 2. What the stage produced

- **`risk-scores.md`**: 2,034,804 B. Section 1 says 408 scored: 0 Critical, 16 High, 360 Medium, 32 Low. Section 2 is sorted by composite descending (maximum 8.1), `fresh` in the Source column on all 408. Section 2a holds 6 rows, all `RESOLVED`. Section 6's Score Flags table is empty. Written by the renderer.
- **`risk-scores.sarif`**: 785,480 B, 408 results (16 `error`, 360 `warning`, 32 `note`), 8 rules, no `relatedLocations`. Written by the renderer.

The completeness check ran in the work directory with its own table parser against Section 7 and Section 4c of the committed fixture, not the shipped parser. The tracked tree is unchanged: `threats.md` is byte-identical, and the only new paths are `.tachi-build/` (54 files, all `.json`), `risk-scores.md` and `risk-scores.sarif`. `undeclared_paths` is empty. `{{...}}` slot markers: 0 in Sections 1 to 5.

## 3. Tokens, model, effort and the stage record

| | Model | Effort | Responses | Output tokens | Thinking |
|---|---|---|---|---|---|
| Main session | Opus 5.5 | max | 36 | 13,754 | 5,189 |
| 26 `tachi-risk-scorer` agents | Sonnet 5.5 (the agent's pinned `sonnet`) | max | 310 | 4,282,055 | 3,876,839 |
| **Total** | | | **346** | **4,295,809** | **3,882,028 (90.4%)** |

- No response carries a fallback credit. Stops: main 9 `tool_use` and 27 `end_turn`; agents 301 `tool_use` and 9 `max_tokens`. Every one of the 346 requests carried `max_tokens` 128,000. Each response is counted once by message ID. `/usage`'s by-model lines for the session: Sonnet 4.3 M (equal), Opus 14.8k (1.0k above the transcripts), Haiku 17.2k (calls that leave no transcript response).
- Per agent: 6 to 20 responses (median 11.5) and 114,120 to 214,616 output tokens (median 164,262), against about 8,700 at the default effort. Each agent's one Write response was 20,877 to 127,334 tokens (median 57,994) for a part file of 19,396 to 28,159 B. Part files at attempt 1's max were 13,384 to 17,044 B.
- **Stage record** (`tachi.stage-record/1`): started 17:02:57Z, finished 17:48:56Z; `batch_size` 13; all fresh. Counts: units 326, open 408, rendered 408, resolved 6. Two warnings, as disposition (a) predicted: `baseline-unresolved` and `architecture-path:body-line:absent`. All 26 parts are first attempts (`B001.a1.json` to `B026.a1.json`) under one plan ID, with 326 items. The record holds no per-step exit codes and no token field, so those come from the transcript.

## 4. Timeline and the completion rule

All 26 agents ran as background agents (metadata `background`; the Agent calls named no flag). The main session ended its turn after each dispatch and resumed on the 26 completion notices (24 as new turns, 2 delivered into a running turn), making no tool call between a dispatch and that wave's last hand-back. Disposition (b) check: no `reconcile` before every listed wave's agents reported, no render before `reconcile` exited 0, no second `reconcile` or re-dispatch (nothing was pending).

| Offset from submit (m:ss) | Event |
|---|---|
| 0:02 to 0:14 | Step 1's listings (two calls) and presence check (exit 0, `python 3.14.4`), then the populator (exit 0) and `plan` (exit 0): 326 units, 26 batches, waves of 16 and 10 |
| 0:19 | **Wave 1**: 16 Agent calls in one message. The agents' first records came at 0:39 |
| 13:00 to 23:01 | Wave 1's 16 hand-backs. Each agent ran 741 to 1,342 s (median 17:24) |
| 23:13 | **Wave 2**: 10 Agent calls in one message, 12 s after wave 1's last hand-back. 16 notices were in the transcript before it |
| 36:25 to 46:02 | Wave 2's 10 hand-backs (779 to 1,356 s each, median 17:44) |
| 46:10 | `reconcile`, once, exit 0 (status `complete`, 26 done, no waves, none exhausted), 8 s after the last hand-back and after all 26 notices |
| 46:13 / 46:24 | Renderer, exit 5 / final report complete (the timer reads 46m 24s) |

## 5. SC-3, structure only (US-1a #6)

| Check | Result |
|---|---|
| Main session tools | 7 Bash and 26 Agent. No Read, Write, Edit or other tool |
| Main session Bash | 7 calls: two listing calls (four `ls` programs, which Step 1 allows), then the presence check, populator, `plan`, `reconcile` and the renderer, one call each, each ending in an `echo` of its exit code. No `python3 -c`, `-m` or heredoc program, no other interpreter, no text tool: **0 unnamed programs** |
| Agent dispatches | 26, all `tachi-risk-scorer` (26 of 26 in the metadata too), spawn depth 1. 0 other types. Each prompt is the command's fixed line with the batch's own input path: 26 of 26, each path exists, each batch ID equals its call's description |
| What the agents did | Read 339, Grep 252, Glob 50, Write 26, hand-back 26; no Bash. Each agent's one Write names its own batch input's `part_path` (26 of 26), a `.json` file in `<plan>/parts/`. The staging tree holds 54 files, all `.json`: no program file anywhere |
| Hand-backs | 26, of 367 to 3,933 bytes, with 0 code fences: no code returned to the caller |
| Stamps | `risk-scores.md` ends with the renderer's provenance comment and `risk-scores.sarif` holds `tachi_provenance`; both name `render-risk-scores.py` 4.48.4 with the stage record's input digest |

## 6. Overflow at max (US-1a #4)

- **What happened.** 9 agent responses ended at `max_tokens`, each exactly 128,000 tokens. Each held only thinking (no text, no tool call) and came before that agent's Write. Each came after 4 to 8 ordinary responses (reads, greps, listings), none above 15,030 tokens.
- **How it was handled.** Claude Code appended its built-in output-limit notice as a meta user turn, and the agent resumed in the same run. The next response held the agent's Write (29,116 to 77,091 tokens), then the hand-back. The 9 agents made 7 to 11 responses each. Each part was valid at the first `reconcile`.
- **What tachi's record shows.** Nothing: 0 overflow events, 0 retries, 0 splits, and `reconcile` exited 0 on its one call. The stops are visible only in the transcripts. tachi's own path (a missing or truncated part, `reconcile` exit 3, a re-dispatch) was not exercised, so this record claims neither US-1a #4 nor #5 for it.
- **The margin was thin.** 16 of 310 agent responses reached 100,000 tokens. The two largest Write responses were 127,334 (117,768 of it thinking) and 127,026 tokens, 666 and 974 under the cap. A response cut inside a Write call would lose the part; none was.
- **Non-stop failures.** 12 Reads failed (7 unranged on the 582 KB threat model, which exceeds the Read tool's size limit; 5 ranged but over its token limit) and 5 Greps were rejected (pattern or glob). All were in agents, and each agent went on to read what it needed.

## 7. TW-L2 and fallback verdicts

- **TW-L2:** US-1a #3 and #6 hold at max with the agents at max, so no shipped-code defect is claimed and no fix-and-rerun is called for. No agent was off its contract: all 26 read all four binding references before their first Write. This ends the stage's attempts at max (2 of 2).
- **Fallback rate (ruling 2):** 0 of the 1,304 narrative fields (326 units, 4 each). That is under 10% and 25%, and no slot that should resolve fell back. **Not exercised:** US-1a #4 and #5 for tachi's own path (section 6).

## 8. Observations

1. **Max is a cost step, not a contract step.** Against the default effort's attempt 2, output tokens are 18.4 times (4,295,809 against 233,319) and wall time 17 times (46:24 against 2:44). Against attempt 1's max, whose agents ran at medium, they are 17.2 and 7.2 times. The agents' share is 99.7% of the tokens.
2. **Scores differ by level.** Critical 0, High 16, Medium 360, Low 32, against 0, 5, 296, 107 (attempt 1 at max) and 0, 9, 298, 101 (default attempt 2). Of the input's 56 Critical-rated findings, 0 reach Critical: 8 High, 45 Medium, 3 Low. One run per level, so agent variance can't be separated out.
3. **The main session's own text, and usage.** Before the render it printed 32 one-line status texts (54 to 178 characters, 3,640 in all): Step 1 and 2's displays, then a line per dispatch and per completion notice; none came after the render result. The weekly figure moved nine points while T074's max attempt 2 ran on the account, so it can't be split between them. `/usage` estimates this session at about $71 (API-equivalent).

## Reference reads (structure only)

Source: the 26 agent transcripts (tool names, paths and counts) and the 26 hand-back notes (counts only). Per-agent rows stay with the private notes.

| Read | Agents of 26 (attempt 1 at max; default attempt 2) |
|---|---|
| Own batch input; `part-file-contract-shared.md` | 26 and 26 (26 and 26; 26 and 26) |
| `trust-zones` / `cvss-vectors` / `scoring-dimensions` / `reachability-analysis` (binding) | 26 / 26 / 26 / 26 (0 / 1 / 0 / 0; 17 / 24 / 24 / 25) |
| All four / at least one / none | 26 / 26 / 0 (0 / 1 / 25; 17 / 25 / 1) |
| `asset-modifiers` / `severity-bands` / `output-formatting` (context) | 22 / 26 / 11 (0 each; 0 each) |
| An architecture file | 0, no Read or Grep (0; 0) |

- **Order and paths.** The contract (26 of 26) and every binding read (104 of 104) came before the agent's first Write. 0 failed Reads on a user-level skills path, so no agent needed the adopter's copy as a second try; all 327 successful Reads were adopter paths.
- **Notes.** 22 of 26 hand-back notes say the architecture file wasn't read (every batch input's `refs` names the threats file only); 0 notes say a binding reference was skipped.

## Comparison with attempt 1 at max and with the default effort's attempt 2

| | Attempt 1, max (agents at medium) | Attempt 2, default | **Attempt 2, max (agents at max)** |
|---|---|---|---|
| Effort reached (main / agents) | max 22 of 22 / medium 116 of 116 | medium 21 of 21 / medium 125 of 125 | **max 36 of 36 / max 310 of 310** |
| Binding reads: all four / at least one (of 26) | 0 / 1 | 17 / 25 | **26 / 26** |
| Step 6 additions (text lines beyond the renderer's, the warnings and Next steps; fence lines aside) | 9 of 23 (13 with 4 fence lines) | 0 of 12 | **0 of 14** |
| Unnamed programs run by the main session | 6 inline programs (and 8 read-only calls) | 0 | **0** |
| Main-session Bash calls | 18 | 6 | **7** |
| Output tokens: total (main / agents; thinking) | 249,338 (40,605 / 208,733; 40,004) | 233,319 (8,187 / 225,132; 17,839) | **4,295,809 (13,754 / 4,282,055; 3,882,028)** |
| `max_tokens` stops | 0 | 0 | **9** (agents, each resumed in-run) |
| Overflow events / retries | 0 / 0 | 0 / 0 | **0 / 0** |
| Wall time | 6 min 29 s | 2 min 44 s | **46 min 24 s** |
