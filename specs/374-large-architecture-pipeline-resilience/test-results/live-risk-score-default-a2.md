# T073 live run: `/tachi.risk-score` on the fixture, adopter default effort, attempt 2 (W5, PR 1)

**Date:** 2026-11-24. **Base:** the lane at `4128537`. **Inputs:** [w5-setup-pr1.md](w5-setup-pr1.md) (arrangement, dispositions, D-L2, section 9), [t147-fixes-pr1.md](t147-fixes-pr1.md) (what changed), [live-risk-score-default.md](live-risk-score-default.md) (attempt 1, for comparison), spec US-1a #1 and #6, tasks T073. **Run:** one live `/tachi.risk-score` on the install `v4.48.4-162-g1e3614a` (T147's fix, `1e3614a`; Claude Code 2.1.331, macOS) at `--effort medium`, on the fixture's precomputed `threats.md`. It is the stage's second and last attempt at the default effort (TW-L2).

## Result

| Question | Result |
|---|---|
| Verdict | **PASS** on US-1a #1 and #6 (structure). Of the fix's three targets, two are met (Step 6's report; named scripts only) and one is **partly met**: 17 of 26 agents read all four binding references, 9 did not (section 7: TW-L2 class "agent off its contract") |
| `risk-scores.md` | 408 open rows, one per open finding, in each of Sections 2, 3 and 4: the fixture's 408 Section 7 IDs (0 missing, 0 extra, 0 duplicated). 6 RESOLVED rows in Section 2a, equal to Section 4c's 6 |
| `risk-scores.sarif` | 408 results, 408 distinct `findingId/v1`, no RESOLVED ID: N/N holds. Composite, band, CVSS and source agree with the `.md` on all 408 |
| Stage record | 326 units. Batches planned 26, dispatched 26, done 26 (F17's p90 sizes: 14 of 13 and 12 of 12, in two waves of 16 and 10). Retried 0, split 0, exhausted 0. Overflow events 0, retries 0. Narrative fallbacks 0, truncations 0, parse errors 0. Status `success-with-warnings`. The largest response was 8,082 output tokens |
| Output tokens (P-7) | **233,319**: main session (Opus 5.5) 8,187; 26 agents (Sonnet 5.5) 225,132. Thinking 17,839 (7.6%) |
| Wall time | **2 min 44 s** (the session's own timer) |
| Who wrote the files | The shipped renderer. The main session made no Write or Edit. Both files carry the renderer's provenance stamp, and their digests equal the stage record's |
| Exit codes | presence check 0, populator 0, `plan` 0, `reconcile` 0 (one call), render 5. The stage's final exit is 5, disposition (a)'s pass state |
| SC-3, structure only | 0 stand-in dispatches, 0 unnamed programs run by the main session, 0 program files written, 0 code hand-backs |
| `/usage`, "Current week (all models)" | 35% before, 37% after. T074's second attempt ran on the same account at the same time |

## 1. The arrangement

- **Adopter.** A fresh `git clone` of `<adopter w5b-fixture-score>` (restore point `a760439`, above the commit "Install tachi v4.48.4-162-g1e3614a") into a new directory, with the generic repo-local identity. Clean before the run. Inputs: the fixture's `threats.md` (sha256 `44694eb5...`) in `docs/security/2026-10-19T09-30-00/` and its architecture description (sha256 `5ee33b33...`), equal to [w5-setup-pr1.md](w5-setup-pr1.md) section 2.
- **Launch (D-L2).** A detached tmux session (200 x 50), cwd the clone, running `env -i` with `HOME`, `USER`, `LOGNAME`, `SHELL=/bin/zsh`, `TERM=xterm-256color`, `LANG=en_US.UTF-8` and a `PATH` of the user's bin directory, `/opt/homebrew/bin` and the system directories, then `claude --effort medium`. No `CLAUDE_CODE_*` variable. **Deviation from "account defaults":** the flag, as in attempt 1 (the account opens Opus 5.5 at xhigh; T021 recorded medium). Auto permission mode, no session profile. The banner read Opus 5.5 with medium effort. The trust dialog was answered "Yes, I trust this folder" at the first try.
- **The version.** Claude Code 2.1.331, as in attempt 1: no client update between the attempts. The clean environment's Python 3.14.4 ran the five script calls with no error (the second live run on it).
- **Prompts and command.** No prompt on screen: the records hold 32 accept decisions (main session) and 241 (agents), and no other decision. `/tachi.risk-score`, no arguments, was submitted at 11:46:52 US Eastern and auto-detected the input directory.

## 2. What the stage produced

| | Result |
|---|---|
| `risk-scores.md` | 1,542,060 B. Section 1 says 408 scored: 0 Critical, 9 High, 298 Medium, 101 Low. Section 2 is sorted by composite descending (maximum 7.9), `fresh` in the Source column on all 408. Section 2a holds 6 rows, all `RESOLVED`. Section 6's Score Flags table is empty. Written by the renderer |
| `risk-scores.sarif` | 785,090 B, 408 results (9 `error`, 298 `warning`, 101 `note`) and 8 rules. Written by the renderer |

The completeness check ran in the work directory with its own table parser against Section 7 and Section 4c of the committed fixture, not the shipped parser. The tracked tree is unchanged: `threats.md` is byte-identical, and the only new paths are `.tachi-build/`, `risk-scores.md` and `risk-scores.sarif` (`undeclared_paths` is empty).

## 3. Tokens, model and effort

| | Model | Effort | Responses | Output tokens | Thinking |
|---|---|---|---|---|---|
| Main session | Opus 5.5 | medium | 21 | 8,187 | 392 |
| 26 `tachi-risk-scorer` agents | Sonnet 5.5 (the agent's pinned `sonnet`) | medium | 125 | 225,132 | 17,447 |
| **Total** | | | **146** | **233,319** | **17,839 (7.6%)** |

- Requested equals served on all 146 responses. Effort and per-turn effort are medium on all, agents included, and no response carries a fallback credit. Stops: main 8 `tool_use` and 13 `end_turn`; agents 125 `tool_use` (each ends on its hand-back call); 0 `max_tokens`.
- Each response counted once by message ID (no ID had records with differing counts). `/usage`'s by-model lines: Sonnet 225.1k (equal), Opus 8.4k (0.2k above the transcripts), Haiku 2.8k (calls that leave no transcript response). Each agent's one Write was 6,499 to 8,082 output tokens (median 7,362), for a part file of 14,134 to 17,307 B.

## 4. The stage record (`tachi.stage-record/1`)

Plan `<plan>`, started 16:47:04Z and finished 16:49:33Z; `batch_size` 13; retry budget 52, used 0; the plan was all fresh. Counts: units 326, open 408, rendered 408, resolved 6. Two warnings, as disposition (a) predicted: `baseline-unresolved` and `architecture-path:body-line:absent`. The record holds no per-step exit codes and no token field, so those come from the transcript. All 26 parts are first attempts (`B001.a1.json` to `B026.a1.json`) under one plan ID, with 326 items in all.

## 5. Timeline and the completion rule

All 26 agents ran as background agents (the transcript metadata says `background`; the Agent calls named no flag). The main session ended its turn after each wave's dispatch, resumed on completion notices, made no tool call between a dispatch and that wave's last hand-back, and finished only after its renderer call. 16 completion notices were in its transcript before wave 2's dispatch, and all 26 before `reconcile`.

| Offset from submit (m:ss) | Event |
|---|---|
| 0:02 / 0:04 | Step 1's presence check (exit 0, `python 3.14.4`), then one `ls` of the input directory |
| 0:07 / 0:11 | Populator (exit 0), `plan` (exit 0): 326 units, 26 batches, waves of 16 and 10 |
| 0:14 | **Wave 1**: 16 Agent calls in one message. Its agents' first records came at 0:34 |
| 1:16 to 1:28 | Wave 1's 16 hand-backs. Each agent ran 41 to 54 s (median 48 s) |
| 1:31 | **Wave 2**: 10 Agent calls in one message, three seconds after wave 1's last hand-back. First records at 1:44 |
| 2:29 to 2:33 | Wave 2's 10 hand-backs (45 to 49 s each, median 47 s) |
| 2:36 | `reconcile`, once, exit 0, three seconds after the last of the 26 hand-backs |
| 2:40 | Renderer, exit 5 (success with warnings) |
| 2:44 | Final report complete (the timer reads 2m 44s) |

Disposition (b) check: no `reconcile` before every listed wave's agents reported, no render before `reconcile` exited 0, no second `reconcile` or re-dispatch (nothing was pending).

## 6. SC-3, structure only (US-1a #6)

| Check | Result |
|---|---|
| Main session tools | 6 Bash and 26 Agent. No Read, Write, Edit or other tool |
| Main session Bash | 6 calls: the presence check (three `ls` listings and `tachi-stage.py --version`), one `ls` of the input directory, then the populator, `plan`, `reconcile` and the renderer, one call each. Each script call ends with an `echo` of the exit code. No `python3 -c`, `-m` or heredoc program, no other interpreter, no text tool: **0 unnamed programs**. Step 1 allows the listings |
| Agent dispatches | 26, all `tachi-risk-scorer` (26 of 26 in the transcript metadata too), spawn depth 1. 0 `general-purpose` or other types. Each prompt is the command's fixed line with the batch's own input path: 26 of 26, each path exists, each batch ID equals its Agent call's description |
| What the agents did | Read 151, Grep 38 (2 failed on an unexpected parameter and were retried), Write 26, hand-back 26, Glob 2; no Bash. Each agent's one Write names its own batch input's `part_path` (26 of 26). All 26 are `.json` files in `<plan>/parts/`, and the staging tree holds no non-JSON file: no program file anywhere |
| Hand-backs | 26, of 253 to 1,079 bytes, with 0 code fences: no code returned to the caller |
| Stamps | `risk-scores.md` ends with the renderer's provenance comment; `risk-scores.sarif` holds `tachi_provenance`. Both name `render-risk-scores.py`, version 4.48.4, with the stage record's input digest |

## 7. The fix's targets, TW-L2 and fallback verdicts

- **Target 1, binding reads: partly met.** 17 of 26 agents read all four before their first Write, 25 read at least one, 1 read none (it ran one Grep on `cvss-vectors.md`). Skips: `trust-zones.md` 9, `cvss-vectors.md` 2, `scoring-dimensions.md` 2, `reachability-analysis.md` 1 (details under "Reference reads").
- **Target 2, Step 6's report: met.** 12 non-blank lines: the renderer's five lines exactly (three summary lines and both warnings), the Next steps block (five lines) and two code-fence lines. Added beyond them: 0 lines. No tool call after the render result. **Target 3, named scripts only: met** (section 6): 0 unnamed programs.
- **TW-L2:** US-1a #1 and #6 hold, so no shipped-code defect is claimed and no fix-and-rerun is called for. Target 1's miss is the class "an agent off its contract": 9 of 26 agents skipped a read that their file's step 3 requires before the first finding, and 3 of them say so in their note. Record it, file a follow-up, and don't claim that SC (KB 22). The ruling is the orchestrator's. This is the stage's last attempt at the default effort.
- **Fallback rate (ruling 2):** 0 of the 1,304 narrative fields the agents wrote (326 units, 4 fields each). That is under 10% and 25%, and no slot that should resolve fell back. The `{{...}}` slot strings in Section 6's "Scoring Inputs" table are the inputs as stored: none appears in Sections 1 to 5. **Not exercised:** US-1a #4 and #5 (re-dispatch, overflow and retry paths), since every batch finished first time. This record claims neither.

## 8. Observations

1. **The skips are concentrated.** `trust-zones.md` is the one most skipped (9 of 26). All 26 agents still got the zone rows their batch needs from the threats file's Section 2 (25 agents Grepped it, 8 Read it), and no unit lacks a zone row.
2. **The distribution moved again.** Critical 0, High 9, Medium 298, Low 101, against 0, 5, 302, 101 in attempt 1 and 0, 27, 348, 33 in T021(a). Of the input's 56 Critical-risk findings, 0 reach Critical: 5 High, 43 Medium, 8 Low (attempt 1: 1, 45, 10). Two runs at one effort don't say how much is agent variance.
3. **What the reads cost.** Agent output is up 7.2% (225,132 against 210,007), thinking 17,447 against 16,061, and the whole stage 6.2% (13,693 tokens) over attempt 1. Per-agent time barely moved (median 48 s and 47 s, against 49 s and 45 s). A wave took 1:14 (16 agents) and 1:02 (10).

## Reference reads (structure only)

Source: the 26 agent transcripts (tool names, paths and counts) and the 26 hand-back notes (sentence classes, no text). Per-agent rows stay with the private notes.

| Read | Agents of 26 (attempt 1) |
|---|---|
| Own batch input; `part-file-contract-shared.md` | 26 and 26 (26 and 26; one contract read failed first) |
| `trust-zones` / `cvss-vectors` / `scoring-dimensions` / `reachability-analysis` (binding) | 17 / 24 / 24 / 25 (0 / 1 / 0 / 0) |
| All four; at least one; none | 17; 25; 1 (0; 1; 25) |
| `asset-modifiers`, `severity-bands`, `output-formatting` (context) | 0 each (0 each) |
| An architecture file | 0, no Read or Grep (0) |

- **Order.** The contract (26 of 26) and every binding read (90 of 90) came before the agent's first Write.
- **User-level skills path.** 0 failed Reads (attempt 1: 1, then the agent read the adopter's copy). All 151 successful Reads were adopter paths.
- **Skippers.** 9 agents skipped at least one binding file: B008, B009, B011, B016, B017, B018 and B025 skipped `trust-zones` only; B010 read `reachability-analysis` only; B021 read none. 3 notes say so (B010, B021, B025), 6 are silent. One more note (B017) says the three context files weren't read, because the renderer does that step.
- **Architecture file.** 0 agents read or grepped it. 18 of 26 notes say it wasn't read (8 give the batch input's `refs` as the reason, 10 give none), and every batch input's `refs` name the `threats` file only.

## Comparison with attempt 1

| | Attempt 1 | Attempt 2 |
|---|---|---|
| Binding reads: all four / at least one (of 26) | 0 / 1 | 17 / 25 |
| Step 6 additions (lines beyond the renderer's, warnings and Next steps) | 7 of 19 lines (1,368 characters; 3 are the warnings re-worded) | 0 of 12 lines |
| Unnamed programs run by the main session | 1 call (a text tool on the input) | 0 |
| Main-session Bash calls | 6 | 6 |
| Output tokens (main / agents; thinking) | 219,626 (9,619 / 210,007; 16,767) | 233,319 (8,187 / 225,132; 17,839) |
| Wall time | 2 min 53 s | 2 min 44 s |
