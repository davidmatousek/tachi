# Live controls run on the fixture, default effort (T074, attempt 2, W5)

**Date:** 2026-11-24. **Base:** install commit `1e3614a` (T147's fix; describe string `v4.48.4-162-g1e3614a`), the controls template `w5b-fixture-controls` at restore point `c3d0832`. **Inputs:** [w5-setup-pr1.md](w5-setup-pr1.md) section 9, [t147-fixes-pr1.md](t147-fixes-pr1.md), [live-compensating-controls-default.md](live-compensating-controls-default.md) (attempt 1), spec US-1a #2 and #6, US-3 #5, SC-3 and SC-5. **Run:** one live `/tachi.compensating-controls --target controls-target` on the fixture's 408 scored findings, Claude Code 2.1.331 (attempt 1: 2.1.330) on macOS, Python 3.14.4, effort medium (by flag, D-L2). This is attempt 2, the last that TW-L2 allows at this effort.

## Result: PASS, the run's claims hold and T147's three targets landed

| Question | Result |
|---|---|
| **US-1a #2, coverage** | 408 of 408 scored open findings appear in Section 2's four band tables exactly once (0 missing, 0 extra, 0 duplicate). `compensating-controls.sarif` holds 408 results, one per open finding (the N/N rule), with the scored input's IDs |
| **US-1a #2, totals and agreement** | Section 1's counts (17 Control Found, 190 Partial, 201 No Control), the band counts (1, 18, 286, 103), Section 5's totals (2273.6 inherent, 1969.5 residual, 13.4%) and its shift and distribution tables all equal the sums of the rows (the percentages sum to 100). The SARIF agrees with the `.md` on status, both scores, level, MAESTRO layer and recommendation presence for 408 of 408 |
| **US-1a #6, SC-3 (structure only)** | 0 stand-in dispatches, 0 unnamed programs run by the main session (5 Bash calls: 1 shell listing, 4 shipped-script calls), 0 program files written, 0 code hand-backs, only declared paths written (section 6) |
| **US-3 #5, SC-5** | One 11-column schema in all four band tables. Sections 2 and 4 were authored by the agents inside their part files; every computed cell held its slot token for the renderer to fill (`cell_overwrites` 0). Section 4 holds 391 blocks for 391 gap findings, none unjoined |
| **T147's targets** | (a) 38 of 38 agents read all three binding references, each before its first Write. (b) The final report is the renderer's lines, both warnings exactly as written, and the Next steps block: 0 added lines. (c) The main session ran no program the command doesn't name: 4 shipped-script calls and one shell listing, which Step 1 allows |
| **Stage exit** | 5, `success-with-warnings`: the pass state (disposition (a)). Warnings: `architecture-path:body-line:absent` and `baseline-unresolved`; no `evidence-file-unresolved` |
| **Output tokens** (command's turns and every subagent, thinking included) | **357,397**, of which thinking 77,349 (22%). Main session (Opus 5.5) 12,354 in 41 responses; 38 agents (Sonnet 5.5) 345,043 in 203 responses. Attempt 1: 300,497 (+18.9%) |
| **Batches** | 38 planned, 38 dispatched, 38 done, in waves of 16, 16 and 6; all attempt 1. 0 overflow events, 0 retries, 0 splits, 0 exhausted |
| **Narrative fallback rate** | 0 of 20 narrative fields (0%), no field with a fallback flag |
| **Wall time** | **4 min 38 s** (the session's own timer). Stage record: 4 min 27 s |
| **TW-L2** | No shipped-code defect, no agent off its contract, no interruption. Nothing is left to re-run |

## 1. The arrangement

- **The adopter.** A fresh `git clone` of `<adopter w5b-fixture-controls>` into a new directory, clean at `c3d0832`. Inputs as w5-setup-pr1.md sections 2 and 9 list them, each digest checked before launch: `risk-scores.md` (sha256 `e82da952...`), `threats.md` (`44694eb5...`, byte-identical to `baseline/threats.md`), `architecture.md` (`5ee33b33...`) and `controls-target/` (tree `fb3cfb11ba5479ec2aaacf2e4496198dbd897425`). The installed `control-analyzer.md` carries T147's step 3, which names the three binding references. No tachi command ran in the template, which is still clean.
- **The session.** A detached terminal-multiplexer session (200 x 50), cwd the clone, launched as `env -i HOME=<home> USER=<user> LOGNAME=<user> SHELL=/bin/zsh TERM=xterm-256color LANG=en_US.UTF-8 PATH=<user bin>:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin claude --effort medium`, with no effort variable. The banner read "Opus 5.5 with medium effort", auto permission mode. **D-L2's deviation:** the account's settings open at xhigh, so `--effort medium` restores the default that T021 recorded.
- **The dialog.** The trust dialog listed "No, exit" first; one Down and Enter chose "Yes, I trust this folder". No other prompt appeared and no poll found a dialog on screen: auto mode decided all 43 main-session and 569 agent tool uses.
- **The command**, typed as-is: `/tachi.compensating-controls --target controls-target`, no `--architecture-path` (D-L6). Afterwards `git status` lists only `.tachi-build/` (79 paths) and the two outputs as new paths, and no tracked file changed. **The target is unchanged:** `git diff HEAD -- controls-target` is empty and its tree digest equals the one above.
- **Usage.** `/usage` "Current week (all models)" read 35% before and 37% after. T073's attempt 2 ran on the same account at the same time, so the step isn't this run's alone. By-model output tokens after: Opus 12.7k, Sonnet 345.0k, Haiku 3.3k (Haiku leaves no transcript response).

## 2. What the stage produced

| File | Size | Written by | Content |
|---|---|---|---|
| `compensating-controls.md` | 854,752 B, 9,001 lines | the shipped renderer | Section 2: 408 rows (Critical 1, High 18, Medium 286, Low 103). Section 3 names 207 findings (17 + 190). Section 4: 391 blocks numbered 1 to 391 (effort Medium 287, Low 79, High 25). Section 7: 0 flags. Ends with the renderer's provenance comment |
| `compensating-controls.sarif` | 952,251 B | the shipped renderer | 408 results, 8 rule IDs, levels error 19, warning 286, note 103, one location URI; provenance `render-compensating-controls.py`, digest equal to the stage record's |

An independent reader (its own table parsers, not the shipped ones) ran 37 checks, and all 37 pass: reference set, one schema in four tables, row counts, inherent score and severity equal to the scored input, residual severity as the band of the residual score, row order, residual = inherent x (1 - factor) half up with one factor per status (0.50, 0.25, 0.00), every total in Sections 1, 2 and 5, one Section 4 block per gap finding (four agent lines never blank), SARIF N/N, fingerprints (408 distinct), `.md` and SARIF agreement, flags (none in either file), and both files' sha256 against the stage record. Its first run stopped on a reader bug (it assumed a `counts.input` key that the stage record omits when nothing is flagged); the one line was fixed and the checks re-run on the same files.

## 3. Tokens, model and effort

| | Model (requested = served) | Effort | Responses | Output tokens | Thinking |
|---|---|---|---|---|---|
| Main session | Opus 5.5 | medium | 41 | 12,354 | 456 |
| 38 control analyzers | Sonnet 5.5 (the agent's pinned `sonnet`) | medium | 203 | 345,043 | 76,893 |
| **Total** | | | **244** | **357,397** | **77,349 (22%)** |

- Each response is counted once at `usage.output_tokens`, as in T021. Effort per response is `medium` requested and `medium` per turn on all 244 (the agents ran at the default). No turn fell back to another model, none stopped at `max_tokens`. Main stops: 8 `tool_use`, 33 `end_turn`. Agent stops: all `tool_use` (each ends with its hand-back call).
- Per agent: 6,786 to 14,037 output tokens (median 9,036; attempt 1: 5,449 to 13,087, median 7,517), 876 per finding on average (attempt 1: 736). `/usage`'s Sonnet figure equals the agents' count; its Opus figure is 0.3k above the main transcript's.

## 4. The stage record

`tachi.stage-record/1`, status `success-with-warnings`, tool version 4.48.4, started 16:47:00Z, finished 16:51:27Z. Counts: units 408, open 408, resolved 0, rendered 408, parse_errors 0, narrative_fallbacks 0, truncations 0, cell_overwrites 0, and no `input` count (attempt 1: 10, its flagged cells). Batches: planned 38, dispatched 38, done 38, exhausted 0, retried 0, split 0. `overflow_events` and `retries` are empty, `undeclared_paths` is empty, the retry budget (76) is untouched. The plan's batch size is 11: 28 batches of 11 and 10 of 10. Step exits: presence check 0, `plan` 0, `reconcile` 0, renderer 5.

## 5. The timeline and the completion rule

All 38 launches were background. The main session dispatched each wave in one message, ended its turn, and resumed on completions (33 turn ends in 41 responses).

| Offset from submit (mm:ss) | Event |
|---|---|
| 0:03 to 0:08 | Step 1's listing (shell); presence check (exit 0, "python 3.14.4"); `plan` (exit 0): 408 units, 38 batches |
| 0:11 to 0:31, to 1:36 | Wave 1: 16 Agent calls in one message, main ends its turn at 0:32; last report at 1:36 (16 hand-backs, 16 notices) |
| 1:38 to 1:59, to 3:22 | Wave 2: 16 calls, 3 s after wave 1's last report; last report at 3:22 (16 and 16) |
| 3:25 to 3:32, to 4:27 | Wave 3: 6 calls, 3 s after; last report at 4:27 (6 and 6) |
| 4:29 / 4:33 | `reconcile`, once, exit 0 (38 of 38 done); renderer, exit 5 |
| 4:38 | Final report complete (timer "4m 38s") |

- **Disposition (b): no departure.** One `reconcile`, after all 38 agents had reported; the renderer ran after `reconcile` exited 0; no wave started before the one before it had finished. Every agent had both a hand-back and a completion notice (34 notices as separate entries, 4 as queued attachments); each agent's first report came within 1.5 s of its last record.
- **The final report against Step 6.** One response, 14 non-empty lines: the renderer's 3 summary lines and 2 warnings, each equal to the renderer's line, the 7-line Next steps block and its 2 fence lines. Extra lines: 0 (0 B, 0 numbers). The call's own exit-code echo was not printed.

## 6. SC-3, structure only (US-1a #6)

- **Agent types.** 38 of 38 dispatches name `tachi-control-analyzer`, and all 38 subagent files carry that type. Each prompt equals the command's fixed text (38 of 38). The agents' 442 Reads, 38 Globs and 11 Greps stayed inside the run: the target, the batch inputs, the skills references and the output template (0 outside).
- **The main session** used Bash 5 times and Agent 38 times, and no Read, Write or Edit. The five calls: one shell listing (`ls`, `sort`, a `for` loop, `head`; no interpreter), then `tachi-stage.py --version`, `plan`, `reconcile` and `render-compensating-controls.py`, each a single `python3` call with literal arguments and an exit-code echo. **Unnamed programs: 0** (0 inline `python3 -c`, 0 heredocs, 0 other interpreters, 0 redirects of output into a file, 0 `cd`).
- **The agents** used Read 442, Glob 38, Grep 11, Write 40 and the hand-back call 38; 0 Bash. All 40 Writes are `.json` files to the agent's own part path (2 agents wrote theirs twice, same path and attempt). 0 program-file extensions.
- **Hand-backs.** 38, 725 to 1,709 bytes each, 0 with a code fence and 0 with a program-like line.
- **The two outputs** were written only by the renderer's one call: the stage record's sha256 values equal the files, both carry the renderer's stamp, and no Write or Edit named either file.

## 7. Verdicts

- **TW-L2:** attempt 2 of 2 at this effort and stage. No shipped-code defect (the renderer ran on 3.14.4 and exited 5 as the fixture expects), no agent off its contract, no interruption. T147's edits for AW5-1 and AW5-2 (the binding reads) and AW5-4 (Step 6's report) show their effect here. AW5-5's inline programs, seen at max effort, have no instance at this effort in either attempt.
- **PM fallback return (ruling 2):** 0 of 20 narrative fields fell back (5 evidence assessments x 4 dimensions), no slot that should resolve fell back, no follow-up from this run. The other agent text fields never fell back: 408 matrix rows, 391 recommendation bodies, 221 evidence snippets and 221 summaries.

## 8. Observations

1. **Interim notes.** The main session printed 37 short notes before the final report (median 163 B, 6.5 KB in all): the Step 1 displays (1), the plan and first-wave notes (2) and 34 wave-start and progress notes. Step 6 doesn't govern them. Two doubt the content of an agent's reply, and neither acted on it: `reconcile` was the check. Whether to bound them is the orchestrator's call.
2. **Tokens rose 18.9%.** The agents' thinking rose 57% (48,896 to 76,893) and their other output 13%; their target Reads rose from 168 to 252, and evidence entries from 208 to 221. The binding reads' own input isn't in output tokens. No SC-8 claim is made here; T075 owns it.
3. **Control Category.** 0 of 408 cells are non-canonical (attempt 1: 10, all from the 2 agents that had skipped `control-categories.md`). Section 7 and the SARIF flags are empty.
4. **Output template.** 9 of 38 agents ran one Grep on `templates/tachi/output-schemas/compensating-controls.md` for the Section 2 header, which the agent's own `matrix_row` rule points to; none Read it. Attempt 1's agents made no such call.
5. **No architecture snapshot (D-L6).** The plan's `architecture_warning` is empty, no batch input names an architecture file and no agent Read one, so components were mapped by heuristics. All 408 SARIF locations carry the one default path.
6. **3.14.4 held** for every script, the renderer included, as in attempt 1.

## Reference reads (structure only)

From the 38 subagent transcripts, by Read tool calls and file paths only. A file counts as read when the agent's Read of the adopter's copy under `.claude/skills/` returned without error. All 38 agents were first attempts (0 retries).

| Read (marker in the installed `control-analyzer.md`) | Agents (of 38) | Before the first Write | Attempt 1 |
|---|---|---|---|
| its own batch input | 38 | 38 | 38 |
| `tachi-shared/references/part-file-contract-shared.md` (l.74) | 38 | 38 | 38 |
| `tachi-control-analysis/references/control-categories.md` (step 3, l.82) | **38** | 38 | 5 |
| `tachi-control-analysis/references/evidence-criteria.md` (l.82) | **38** | 38 | 0 |
| `tachi-control-analysis/references/residual-risk.md` (l.82) | **38** | 38 | 0 |

- **Coverage.** 38 agents read all five files, 0 read fewer, 0 read a file twice, 0 used an offset or limit, and no other file under `.claude/skills/` was opened. 152 skills Reads equal 38 x 4. No Glob or Grep named a reference.
- **Order.** 38 of 38 read the batch input first and the contract second. 34 then ran one Glob of the target before `control-categories.md` and `evidence-criteria.md`; 4 read all five files back to back. Target Reads before the first Write: 2 to 11 per agent (median 7).
- **User-level path.** 0 failed Reads on a user-level skills path and 0 successful ones (attempt 1: 9 agents failed, and each then read the adopter's copy), so no agent needed the fallback.

## Attempt 1 against attempt 2

| | Attempt 1 | Attempt 2 |
|---|---|---|
| Binding reads, agents of 38 (`control-categories` / `evidence-criteria` / `residual-risk`) | 5 / 0 / 0 (all three: 0) | 38 / 38 / 38 (all three: 38) |
| Non-canonical Control Category cells | 10 of 408 | 0 of 408 |
| Step 6 additions in the final report | 2 passages (about 900 B) and 2 paraphrased warnings | 0 lines, 0 B; warnings exact |
| Unnamed programs run by the main session | 0 | 0 |
| Bash calls, main session | 4 | 5 (1 listing, 4 shipped-script calls) |
| Failed user-level Reads; agent Reads in all | 9 agents; 258 | 0; 442 |
| Output tokens (thinking) | 300,497 (49,485) | 357,397 (77,349) |
| Wall time (session timer) | 4 min 15 s | 4 min 38 s |
