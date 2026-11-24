# Live controls run on the fixture, effort max with the agents at max (T074, attempt 2, W5)

**Date:** 2026-11-24. **Base:** install commit `1e3614a` (T147's fix; describe string `v4.48.4-162-g1e3614a`), the controls template `w5b-fixture-controls` at restore point `c3d0832`. **Inputs:** [w5-setup-pr1.md](w5-setup-pr1.md) section 9, [t147-fixes-pr1.md](t147-fixes-pr1.md), [live-compensating-controls-max.md](live-compensating-controls-max.md) (attempt 1), [live-compensating-controls-default-a2.md](live-compensating-controls-default-a2.md), spec US-1a #3, #4 and #6, US-3 #5, SC-3, SC-5, R-18. **Run:** one live `/tachi.compensating-controls --target controls-target` on the fixture's 408 scored findings, Claude Code 2.1.331, macOS, Python 3.14.4, **the main session and the agents at max** (D-L9). This is attempt 2, the last that TW-L2 allows at this effort, and the first run with the agents at max.

## Result: PASS, every claim holds with the agents at max; the cost is 4.11M output tokens and 43 minutes

| Question | Result |
|---|---|
| **US-1a #3 for controls, coverage** | 408 of 408 scored open findings appear in Section 2's band tables exactly once (0 missing, 0 extra, 0 duplicate). Critical has no table because no finding's residual is Critical: the contract says a band with no threat has no table. `compensating-controls.sarif` holds 408 results, one per open finding (N/N), with the scored input's IDs |
| **US-1a #3, totals and agreement** | Section 1's counts (7 Control Found, 150 Partial, 251 No Control), the band counts (0, 19, 307, 82), Section 5's totals (2273.6 inherent, 2049.4 residual, 9.9%) and its shift and distribution tables all equal the sums of the rows (the percentages sum to 100). The SARIF agrees with the `.md` on status, both scores, level, MAESTRO layer and recommendation presence for 408 of 408 |
| **Effort (D-L9)** | Main session: 48 of 48 responses `effort` max and `perTurnEffort` max. Agents: 38 of 38 transcripts, 494 of 494 responses, both fields max. No agent ran below max, so the arrangement is what R-18 means |
| **US-1a #6, SC-3 (structure only)** | 0 stand-in dispatches, 0 unnamed programs run by the main session (6 Bash calls: 2 shell listings, 4 shipped-script calls), 0 program files written, 0 code hand-backs, only declared paths written (section 6) |
| **US-3 #5, SC-5** | One 11-column schema in all three band tables. Sections 2 and 4 were authored by the agents inside their part files; every computed cell held its slot token for the renderer to fill (`cell_overwrites` 0). Section 4 holds 401 blocks for 401 gap findings, none unjoined |
| **T147's targets** | (a) 38 of 38 agents read all three binding references, each before its first Write. (b) The final report is the renderer's lines and the Next steps block: 0 added lines. (c) The main session ran no program the command doesn't name |
| **Overflow (US-1a #4)** | 0 overflow events, 0 retries, 0 splits, 0 `max_tokens` stops, so the dispatch layer's overflow path wasn't exercised. The largest single response was 111,990 tokens against the 128,000 request cap (section 3) |
| **Stage exit** | 5, `success-with-warnings`: the pass state (disposition (a)). Warnings: `architecture-path:body-line:absent` and `baseline-unresolved`; no `evidence-file-unresolved` |
| **Output tokens** (command's turns and every subagent, thinking included) | **4,110,230**, of which thinking 3,622,855 (88%). Main session (Opus 5.5, max) 15,065 in 48 responses; 38 agents (Sonnet 5.5, max) 4,095,165 in 494 responses. Default a2: 357,397, so 11.5 times |
| **Batches; narrative fallback rate** | 38 planned, 38 dispatched, 38 done, in waves of 16, 16 and 6, all attempt 1. 0 of 376 narrative fields fell back (94 evidence assessments x 4 dimensions), 0% |
| **Wall time** | **43 min 14 s** (the session's own timer). Stage record: 42 min 55 s. Default a2: 4 min 38 s; attempt 1 at max: 6 min 57 s |
| **TW-L2** | No shipped-code defect, no agent off its SC-3 contract, no interruption. Nothing is left to re-run at this effort. Four agents' reads of shipped scripts fall outside the spec's read list (section 8, item 3), for the orchestrator to class |

## 1. The arrangement

- **The adopter.** A fresh `git clone` of `<adopter w5b-fixture-controls>` into a new directory, clean at `c3d0832`. Digests checked before launch: `risk-scores.md` (sha256 `e82da952...`), `threats.md` (`44694eb5...`, byte-identical to `baseline/threats.md`), `architecture.md` (`5ee33b33...`) and `controls-target/` (tree `fb3cfb11ba5479ec2aaacf2e4496198dbd897425`). No tachi command ran in the template, which is still clean.
- **The session.** A detached terminal-multiplexer session (200 x 50), cwd the clone, launched as `env -i HOME=<home> USER=<user> LOGNAME=<user> SHELL=/bin/zsh TERM=xterm-256color LANG=en_US.UTF-8 PATH=<user bin>:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin CLAUDE_CODE_EFFORT_LEVEL=max claude --effort max`. The banner read "Claude Code v2.1.331" and "Opus 5.5 with max effort", auto permission mode. **D-L9's deviation:** the effort variable plus the flag set R-18's second level for the main session and the agents; the account's settings alone would open at xhigh, and attempt 1's flag alone reached only the main session.
- **The dialog.** "No, exit" was listed first; one Down and Enter chose "Yes, I trust this folder". No other prompt appeared and no poll found a dialog: auto mode decided all 44 main-session and 1,398 agent tool uses.
- **The command**, typed as-is, with no `--architecture-path` (D-L6). Afterwards `git status` lists only `.tachi-build/` (79 paths) and the two outputs as new, and no tracked file changed. **The target is unchanged:** `git diff HEAD -- controls-target` is empty and its tree digest equals the one above.
- **Usage.** `/usage` "Current week (all models)" read 37% before and 46% after. T073's true-max run used the same account at the same time, so the step isn't this run's alone. By-model output after: Opus 16.2k, Sonnet 4.1M, Haiku 35.3k (Haiku leaves no transcript response); `/usage` prices the session at about $71.

## 2. What the stage produced

| File | Size | Written by | Content |
|---|---|---|---|
| `compensating-controls.md` | 1,311,633 B, 9,554 lines | the shipped renderer | Section 2: 408 rows (Critical 0, High 19, Medium 307, Low 82). Section 3 names 157 findings (7 + 150). Section 4: 401 blocks numbered 1 to 401 (effort High 38, Medium 344, Low 19). Section 7: 0 flags. Ends with the renderer's provenance comment |
| `compensating-controls.sarif` | 1,006,939 B | the shipped renderer | 408 results, 8 rule IDs, levels error 19, warning 307, note 82; provenance `render-compensating-controls.py`, digest equal to the stage record's |

An independent reader (its own table parsers, not the shipped ones) ran 37 checks, the same set as the default a2 run's, and all 37 pass. **One reader fix, not a shipped defect:** its first run assumed four band tables and stopped on the absent Critical one. It now requires a table for each band with a non-zero count and none for an empty band, as the contract line under Section 2 says, and the checks were re-run on the same files.

## 3. Tokens, model and effort

| | Model (requested = served) | Effort (run, per turn) | Responses | Output tokens | Thinking |
|---|---|---|---|---|---|
| Main session | Opus 5.5 | max, max | 48 | 15,065 | 3,828 |
| 38 control analyzers | Sonnet 5.5 (the agent's pinned `sonnet`) | **max, max** | 494 | 4,095,165 | 3,619,027 |
| **Total** | | | **542** | **4,110,230** | **3,622,855 (88%)** |

- Each response is counted once at `usage.output_tokens`, as in T021. No turn fell back to another model and none stopped at `max_tokens`. Main stops: 9 `tool_use`, 39 `end_turn`. Agent stops: all `tool_use`.
- Per agent: 73,439 to 146,247 output tokens (median 105,192; default a2: 9,036), 8 to 23 responses each; 10,074 tokens per finding (default a2: 876). `/usage`'s Sonnet figure equals the agents' count; its Opus figure is 1.1k above the main transcript's.
- **Headroom.** Every request carried `max_tokens` 128,000 (the transcripts' request records). The largest single response was 111,990 tokens (104,298 thinking), a Write response, 87.5% of the cap; 11 responses reached 64k and 44 reached 32k. Write responses ran 8,220 / 19,544 / 111,990 (min / median / max); the 38 part files ran 13,555 to 27,142 B (median 19,699).

## 4. The stage record

`tachi.stage-record/1`, status `success-with-warnings`, tool version 4.48.4, started 17:04:33Z, finished 17:47:28Z. Counts: units 408, open 408, resolved 0, rendered 408, parse_errors 0, narrative_fallbacks 0, truncations 0, cell_overwrites 0, and no `input` count (nothing flagged). Batches: planned 38, dispatched 38, done 38, exhausted 0, retried 0, split 0. `overflow_events`, `retries` and `undeclared_paths` are empty; the retry budget (76) is untouched. The plan's batch size is 11: 28 batches of 11 and 10 of 10. Step exits: presence check 0 ("python 3.14.4"), `plan` 0, `reconcile` 0, renderer 5.

## 5. The timeline and the completion rule

All 38 launches were background (`async_launched`), each call carrying only `description`, `prompt` and `subagent_type`. The main session dispatched each wave in one message, ended its turn, and resumed on completions (39 turn ends in 48 responses).

| Offset from submit (mm:ss) | Event |
|---|---|
| 0:04 to 0:12 | Step 1's two shell listings; presence check (exit 0); `plan` (exit 0): 408 units, 38 batches |
| 0:17 to 0:37, to 16:37 | Wave 1: 16 Agent calls in one message; last report at 16:37 (slowest agent 959 s) |
| 16:42 to 17:03, to 31:25 | Wave 2: 16 calls, 5 s after wave 1's last report; last report at 31:25 (slowest 862 s) |
| 31:28 to 31:35, to 43:00 | Wave 3: 6 calls, 3 s after; last report at 43:00 (slowest 684 s) |
| 43:04 / 43:07 | `reconcile`, once, exit 0 (38 of 38 done); renderer, exit 5 |
| 43:14 | Final report complete (timer "43m 14s") |

- **Disposition (b): no departure.** One `reconcile`, 4 s after the last agent reported; the renderer after `reconcile` exited 0; no wave started before the one before it had reported. Every agent had a hand-back and a completion notice (35 notices as user records, 3 as queued attachments); each first report came within 0.7 s of the agent's last record.

## 6. SC-3, structure only (US-1a #6)

- **Agent types.** 38 of 38 dispatches name `tachi-control-analyzer`, all 38 subagent files carry that type, and each prompt equals the command's fixed text (38 of 38).
- **The main session** used Bash 6 times and Agent 38 times, and no Read, Write or Edit. Two calls were shell listings (no interpreter); four were a single `python3` call each with literal arguments: `--version`, `plan`, `reconcile` and the renderer. **Unnamed programs: 0** (0 inline `python3 -c`, 0 heredocs, 0 other interpreters, 0 output redirects, 0 `cd`). Attempt 1 ran 4.
- **The agents** used Read 926, Glob 148, Grep 248, Write 38 and the hand-back call 38; 0 Bash. All 38 Writes are `.json` files to the agent's own part path, one each. 0 program-file extensions.
- **Hand-backs.** 38, 565 to 3,019 bytes (median 1,372), 0 with a code fence and 0 with a program-like line.
- **The two outputs** were written only by the renderer's one call: the stage record's sha256 values equal the files, both carry the renderer's stamp, `undeclared_paths` is empty, and no Write or Edit named either file.
- **The final report against Step 6.** One response of 1,164 B: the renderer's 3 summary lines and 2 warning lines, each exactly as written, and the 7-line Next steps block. Added lines: 0, with 0 numbers (attempt 1: 13 lines; default a2: 0). Before it the main session printed 45 short notes during the run (median 88 B, 4,085 B in all), which Step 6 doesn't govern (default a2: 37 notes, 6.5 KB).

## Reference reads (structure only)

Counted from the agents' Read calls, over the 38 first-attempt agents (no retries). A file counts when the Read of the adopter's copy succeeded.

| Read | Max a2, of 38 | Before first Write | Default a2 | Max a1 |
|---|---|---|---|---|
| their own batch input; `part-file-contract-shared.md` | 38; 38 | 38; 38 | 38; 38 | 38; 38 |
| `control-categories.md` | **38** | 38 | 38 | 9 |
| `evidence-criteria.md` | **38** | 38 | 38 | 6 |
| `residual-risk.md` | **38** | 38 | 38 | 2 |

- All five files: 38 agents (default a2: 38; max a1: 2). Failed Reads on a user-level skills path: 0 (max a1: 9 agents).
- **Other reads.** The spec's own pointers: the output template, Read by 38 agents (40 Reads; default a2: 9 Greps, no Read), `schemas/compensating-controls.yaml` by 14, `sarif-identity-shared.md` by 3. The batch input's `refs`: `baseline/threats.md`, Read by 36 agents (69 Reads) and Grepped by 37; `risk-scores.md`, Read by 9 (15 Reads) and Grepped by 29. **Outside the spec:** 4 agents Read shipped scripts, the part-validation module (12 Reads) and the renderer (10), with 25 Greps on `scripts/`. Every agent Read all 15 target files once (570 = 38 x 15; default a2: 252).

## 7. Verdicts

- **TW-L2:** attempt 2 of 2 at this effort and stage. No shipped-code defect (every script ran on Python 3.14.4, the renderer exited 5 as the fixture expects), no agent off its SC-3 contract, no interruption. T147's edits show their effect at max: attempt 1's 4 inline programs, 9 non-canonical cells and added report text have no instance.
- **PM fallback return (ruling 2):** 0 of 376 narrative fields fell back, and no slot that should resolve did. The other agent text fields never fell back: 408 matrix rows, 401 recommendation bodies, 181 evidence snippets and 181 summaries. No follow-up from this run.

## 8. Observations

1. **Cost at true max.** The agents' median of 105,192 tokens is 11.6 times default a2's, 88% of it thinking, and the wall time is 9.3 times. Attempt 1's 337,071 tokens had only the main session at max. This record makes no SC-8 claim; T075 owns it.
2. **Scan depth.** Every agent read the whole target; attempt 1 had 3 batches that opened none. Control status is a judgment and moves on the same input: 7 / 150 / 251 here, 17 / 190 / 201 at default a2, 9 / 171 / 228 at attempt 1. No claim rests on it.
3. **Reads beyond the spec, and failed calls.** 4 agents Read the shipped part-validation module and the renderer, which the spec's read list doesn't name. It is no SC-3 class (nothing written, nothing handed back), so its class is the orchestrator's call. Agents made 5 failed calls of 1,398: a malformed Read, a malformed Glob, 2 Reads of the scored input refused by the Read tool's 256 KB limit (the file is 681 KB), and 1 Read of a path that doesn't exist, outside the adopter. No call outside the adopter succeeded. One agent also shows a request with no response record; no error record exists anywhere, and its part was valid.
4. **Control Category; architecture (D-L6).** 0 of 408 Control Category cells are non-canonical (attempt 1: 9), and Section 7 and the SARIF flags are empty. No batch input names an architecture file and no agent opened one, so components were mapped by heuristics; all 408 SARIF locations carry the one default path.

## Comparison: attempt 1 at max, default attempt 2, and this run

| | Max, attempt 1 | Default, attempt 2 | Max with agents at max, attempt 2 |
|---|---|---|---|
| Effort reached | main max; agents medium (203 responses) | main medium; agents medium | main max (48); agents max (494) |
| Binding reads of 38 (`control-categories` / `evidence-criteria` / `residual-risk`) | 9 / 6 / 2 | 38 / 38 / 38 | 38 / 38 / 38 |
| Non-canonical Control Category cells | 9 of 408 | 0 | 0 |
| Step 6 additions in the final report | 13 lines (2,173 B), 2 warnings exact | 0 lines | 0 lines, warnings exact |
| Unnamed programs run by the main session | 4 inline `python3 -c` | 0 | 0 |
| Bash calls, main session | 10 | 5 | 6 (2 listings, 4 shipped-script calls) |
| Output tokens: total (main / agents) | 337,071 (30,787 / 306,284) | 357,397 (12,354 / 345,043) | 4,110,230 (15,065 / 4,095,165) |
| Thinking tokens: total (main / agents) | 78,760 (15,719 / 63,041) | 77,349 (456 / 76,893) | 3,622,855 (3,828 / 3,619,027) |
| Any `max_tokens` stop; largest agent response | none; 8,640 | none; 8,626 | none; 111,990 of 128,000 |
| Overflow events; retries | 1 (`invalid`); 1 | 0; 0 | 0; 0 |
| Wall time (session timer) | 6 min 57 s | 4 min 38 s | 43 min 14 s |
