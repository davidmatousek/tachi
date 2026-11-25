# Live controls run on the fixture, default effort (T074, attempt 1, W5)

**Date:** 2026-11-24. **Base:** install commit `27d58bd` (describe string `v4.48.4-154-g27d58bdc`), the controls template at restore point `b42c12e`. **Inputs:** [w5-setup-pr1.md](w5-setup-pr1.md), [sc8-baseline.md](sc8-baseline.md), spec US-1a #2 and #6, US-3 #5, SC-3 and SC-5. **Run:** one live `/tachi.compensating-controls --target controls-target` on the fixture's 408 scored findings, Claude Code 2.1.330 on macOS, Python 3.14.4, effort medium (by flag, D-L2), attempt 1 of at most 2 (TW-L2).

## Result: PASS, the run's claims hold

| Question | Result |
|---|---|
| **US-1a #2, coverage** | 408 of 408 scored open findings appear in Section 2's four band tables exactly once (0 missing, 0 extra, 0 duplicate). `compensating-controls.sarif` holds 408 results, one per open finding (the N/N rule), with the scored input's IDs |
| **US-1a #2, totals and agreement** | Section 1's counts (20 Control Found, 185 Partial, 203 No Control), the band counts (1, 20, 284, 103), Section 5's totals (2273.6 inherent, 1970.4 residual, 13.3%), and its shift and distribution tables all equal the sums of the rows (the percentages sum to 100). The SARIF agrees with the `.md` on status, both scores, level, MAESTRO layer and recommendation presence for 408 of 408 |
| **US-1a #6, SC-3 (structure only)** | 0 stand-in dispatches, 0 unshipped scripts run, 0 program files written, 0 code hand-backs, only declared paths written (section 6) |
| **US-3 #5, SC-5** | One 11-column schema in all four band tables. Sections 2 and 4 were authored by the agents inside their part files; every computed cell held its slot token for the renderer to fill (`cell_overwrites` 0), and the shipped check flagged all 10 category-spelling mismatches that the independent reader also found (observation 3). Section 4 holds 388 blocks for 388 gap findings, none unjoined |
| **Stage exit** | 5, `success-with-warnings`: the pass state (disposition (a)). Warnings: `architecture-path:body-line:absent` and `baseline-unresolved`; no `evidence-file-unresolved` |
| **Output tokens** (command's turns and every subagent, thinking included) | **300,497**, of which thinking 49,485 (16%). Main session (Opus 5.5) 14,365 in 29 responses; 38 agents (Sonnet 5.5) 286,132 in 202 responses |
| **Batches** | 38 planned, 38 dispatched, 38 done, in waves of 16, 16 and 6; all attempt 1. 0 overflow events, 0 retries, 0 splits, 0 exhausted |
| **Narrative fallback rate** | 0 of 84 narrative fields (0%), no field with a fallback flag |
| **Wall time** | **4 min 15 s** (the session's own timer). Stage record: 4 min 2 s |
| **TW-L2** | No shipped-code defect, no agent off its contract, no interruption. One text-only departure in the main session's report, for the orchestrator's disposition (b) call (observation 5) |

## 1. The arrangement

- **The adopter.** A fresh `git clone` of `<adopter w5-fixture-controls>` into a new directory, clean at `b42c12e`. Inputs as w5-setup-pr1.md section 2 lists them: `risk-scores.md` (sha256 `e82da952...`), `threats.md` (`44694eb5...`, byte-identical to `baseline/threats.md`), `architecture.md` (`5ee33b33...`) and `controls-target/` (tree `fb3cfb11ba5479ec2aaacf2e4496198dbd897425`). No tachi command ran in the template.
- **The session.** A detached terminal-multiplexer session (200 x 50), cwd the clone, launched as `env -i HOME=<home> USER=<user> LOGNAME=<user> SHELL=/bin/zsh TERM=xterm-256color LANG=en_US.UTF-8 PATH=<user bin>:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin claude --effort medium`. The banner read "Opus 5.5 with medium effort", auto permission mode. **D-L2's deviation:** the account's settings now open at xhigh, so `--effort medium` restores the default that T021 recorded.
- **The dialog.** The trust dialog listed "No, exit" first, highlighted. One Down and Enter chose "Yes, I trust this folder". No other prompt appeared: all 42 main-session and 394 agent tool uses were accepted by auto mode (classifier or mode), with no dialog.
- **The command**, typed as-is: `/tachi.compensating-controls --target controls-target`, with no `--architecture-path` (D-L6). `git status` after the run lists only `.tachi-build/` and the two outputs as new paths.
- **Usage.** `/usage` "Current week (all models)" read 31% before and 32% after. T073 ran on the same account at the same time, so the step isn't this run's alone. By-model output tokens after: Opus 14.6k, Sonnet 286.1k, Haiku 2.6k (Haiku leaves no transcript response).
- **The target** is unchanged: `git diff HEAD -- controls-target` is empty and its tree digest equals the one above.

## 2. What the stage produced

| File | Size | Written by | Content |
|---|---|---|---|
| `compensating-controls.md` | 778,065 B, 9,060 lines | the shipped renderer | Section 2: 408 rows (Critical 1, High 20, Medium 284, Low 103). Section 3 names 205 findings (20 + 185). Section 4: 388 blocks numbered 1 to 388 (effort Medium 287, Low 97, High 4). Section 7: 10 flags. Ends with the renderer's provenance comment |
| `compensating-controls.sarif` | 912,748 B | the shipped renderer | 408 results, 8 rule IDs, levels error 21, warning 284, note 103; statuses found 20, partial 185, missing 203; provenance `render-compensating-controls.py`, digest equal to the stage record's |

An independent reader (its own table parsers, not the shipped ones) ran 37 checks, and all 37 pass: reference set, the four band tables' one schema, row counts, inherent score and severity equal to the scored input, residual severity as the band of the residual score and the table it sits in, row order, residual = inherent x (1 - factor) half up with one factor per status (0.50, 0.25, 0.00), every total in Sections 1, 2 and 5, Section 4's one block per gap finding (status, composite, severity, component and group agree with its row; four agent lines never blank; order), SARIF N/N, fingerprints (408 distinct), `.md` and SARIF agreement, flags (10 in Section 7 and 10 in the SARIF, the same findings), and both files' sha256 against the stage record.

## 3. Tokens, model and effort

| | Model (requested = served) | Effort | Responses | Output tokens | Thinking |
|---|---|---|---|---|---|
| Main session | Opus 5.5 | medium | 29 | 14,365 | 589 |
| 38 control analyzers | Sonnet 5.5 (the agent's pinned `sonnet`) | medium | 202 | 286,132 | 48,896 |
| **Total** | | | **231** | **300,497** | **49,485 (16%)** |

- Each response is counted once at `usage.output_tokens`, as in T021. No turn fell back to another model, and none stopped at `max_tokens`. Main stops: 7 `tool_use`, 22 `end_turn`. Agent stops: all `tool_use` (each ends with its hand-back call).
- Per agent: 5,449 to 13,087 output tokens (median 7,517). The largest single agent response was 7,179 tokens.
- `/usage`'s Sonnet figure (286.1k) equals the agents' count. Its Opus figure (14.6k) is 0.2k above the main transcript's.

## 4. The stage record

`tachi.stage-record/1`, status `success-with-warnings`, tool version 4.48.4, started 15:29:05Z, finished 15:33:07Z. Counts: units 408, open 408, resolved 0, rendered 408, parse_errors 0, narrative_fallbacks 0, truncations 0, cell_overwrites 0, input 10. Batches: planned 38, dispatched 38, done 38, exhausted 0, retried 0, split 0. `overflow_events` and `retries` are empty, `undeclared_paths` is empty, the retry budget (76) is untouched. The plan's batch size is 11: 28 batches of 11 and 10 of 10. Step exits: prerequisites 0, `plan` 0, `reconcile` 0, renderer 5.

## 5. The timeline and the completion rule

The platform has no foreground dispatch. All 38 launches were background (`async_launched`), and the main session kept to the rule: it dispatched a wave in one message, ended its turn, and resumed on completions (22 turn ends in 29 responses).

| Offset from submit (mm:ss) | Event |
|---|---|
| 0:01 / 0:06 | Prerequisites call (exit 0, "python 3.14.4"); `plan` (exit 0): 408 units, 38 batches |
| 0:09 to 0:29 / 0:31 | Wave 1, 16 Agent calls in one message; main ends its turn |
| 0:29 to 1:24 | Wave 1's agents run; the last finishes at 1:24 (16 hand-backs, 16 notices) |
| 1:26 to 1:48 / 1:52 | Wave 2 (16 calls), 2 s after wave 1's last agent; main ends its turn |
| to 3:02 | Wave 2's last agent finishes (16 hand-backs, 15 notices) |
| 3:04 to 3:12 / 3:15 | Wave 3 (6 calls), 2 s after; main ends its turn |
| to 4:00 | Wave 3's last agent finishes (6 hand-backs, 5 notices) |
| 4:03 / 4:06 | `reconcile`, once, exit 0 (38 of 38 done, nothing pending); renderer, exit 5 |
| 4:15 | Final report complete (timer "4m 15s") |

- **Disposition (b): no departure.** One `reconcile`, after every agent of every wave had reported; the renderer ran after `reconcile` exited 0; no wave started before the one before it had finished.
- **Every completion had its notice.** A first count found 36 notices for 38 agents. T074's max-run tester showed that the last agent's notice in waves 2 and 3 arrived as a queued attachment, not as a separate entry, so all 38 agents had both a hand-back and a notice. The main session went on 2 s and 3 s after those two. All 38 hand-backs arrived, each within 3.2 s of its agent's last record.

## 6. SC-3, structure only (US-1a #6)

- **Agent types.** 38 of 38 dispatches name `tachi-control-analyzer`, and all 38 subagent files carry that type. Each prompt equals the command's fixed text (38 of 38). The batch inputs carry the target as an absolute path in `refs.target` (38 of 38, expanded by the planner from the relative `--target`). The agents' 168 Reads, 38 Globs and 6 Greps of the target all stayed inside it.
- **The main session** used Bash 4 times and Agent 38 times, and no Read, Write or Edit. The four calls: a prerequisite check, `tachi-stage.py plan`, `tachi-stage.py reconcile` and `render-compensating-controls.py`. The only programs named were the shipped scripts plus shell listings and a file test: 0 inline code, 0 heredocs, 0 unshipped scripts.
- **The agents** used Read 258, Glob 47, Grep 11, Write 40 and the hand-back call 38. All 40 Writes are `.json` files, each to the agent's own part path (2 agents wrote theirs twice). 0 program-file extensions, 0 Bash.
- **Hand-backs.** 38, 797 to 1,637 bytes each, 0 with a code fence and 0 with a program-like line.
- **The two outputs** were written only by the renderer's one call: the stage record's sha256 values equal the files, both carry the renderer's stamp, and no Write or Edit named either file.

## 7. Verdicts

- **TW-L2:** attempt 1 of at most 2, and nothing in it calls for a second. No shipped-code defect (the renderer ran on 3.14.4 without trouble), no agent off its contract, no interruption.
- **PM fallback return (ruling 2):** 0 of 84 narrative fields fell back (21 evidence assessments x 4 dimensions); no slot that should resolve fell back; no follow-up from this run.
- The other agent text fields never fell back: 408 matrix rows, 388 recommendation bodies, 208 evidence snippets and 208 summaries.

## 8. Observations

1. **3.14.4 held.** Every script ran on Python 3.14.4, the renderer included (w5-setup-pr1.md finding 3, which expected the live renderers' first use of 3.14). It met no incompatibility.
2. **No architecture snapshot (D-L6).** The plan's `architecture_warning` is empty, no batch input names an architecture file, and 0 of 258 Reads opened one, so the agents mapped components by heuristics. The renderer's warning says it tried the default path, and all 408 SARIF locations carry `docs/security/architecture.md`.
3. **Control Category spelling.** In 10 of 408 Section 2 rows the agent's cell reads "Logging Audit" (8) or "CSP / Security Headers" (2), where the template's display names are "Logging/Audit" and "CSP/Security Headers" (Section 3's headings use them). The renderer flagged exactly those 10 (`input:control_category:sources-disagree`, in Section 7 and in the SARIF) and left the cell as written. A reader of Section 2 sees the agent's spelling.
4. **Noise.** 9 of 38 agents each made one failed Read of a skill reference under a user-level skills directory, then found it in the adopter's own `.claude/skills/` (T021(b)'s observation 2 again).
5. **A text-only departure from Step 6.** The final report printed the renderer's four summary lines verbatim, but paraphrased its two warnings. It added an opening sentence (about 170 B) and a paragraph (about 730 B) in the main session's own words, on how much of the stub tree the agents read, with one batch count and one file count of its own. The command says to print the lines exactly and restate no number. No renderer figure changed, and it touches no claim above.
6. **Exit codes.** Every call ended with an echo of its exit code, so the tool's own error flag stayed clear for exit 5. The main session read the echoed code, printed the warnings and went on to Step 6, as the command routes exit 5.
7. **One attempt per batch.** All 38 parts are `a1`, and the two double Writes landed at the same path and attempt, so no retry was counted.
8. **Scale.** 736 output tokens per finding on average (300,497 over 408), and a median of 7,517 per agent for a batch of 10 or 11 findings. This record claims no SC-8 delta; T075 owns it.

## Reference reads (structure only)

From the 38 subagent transcripts, by Read tool calls and file paths only. The installed `control-analyzer.md` has five MANDATORY markers over four files (`evidence-criteria.md` at l.331 and l.357). A file counts as read when the agent's Read of the adopter's copy under `.claude/skills/` returned without error.

| Mandatory read (marker line) | Agents that read it (of 38) | Read before the agent's first Write |
|---|---|---|
| `tachi-shared/references/part-file-contract-shared.md` (l.74) | 38 | 38 |
| `tachi-control-analysis/references/control-categories.md` (l.313) | 5 | 5 |
| `tachi-control-analysis/references/evidence-criteria.md` (l.331, l.357) | 0 | 0 |
| `tachi-control-analysis/references/residual-risk.md` (l.377) | 0 | 0 |

- **Coverage.** The agent's own batch input: read by 38 of 38, each as its first tool call. By agent: 33 read the contract only, 5 read the contract and `control-categories.md`, 0 read all four, 0 read none. No agent opened another file under `.claude/skills/`, and no Glob or Grep touched a reference. The 38 contract reads had no offset or limit; 1 of the 5 `control-categories.md` reads had one.
- **The 9 user-level failures.** Each of the 9 agents' one failed Read was the user-level path of the contract file. 9 of 9 then ran a Glob for that file name and read the adopter's copy.
- **Hand-backs.** 0 of 38 name a reference, a skill or a MANDATORY read, and none gives a reason for not reading one, so there is no reason class to count. The skip statements that do appear concern the optional `assessment` objects (16 of 38 say none were written) and target files left unread (2 of 38).
- **The 10 non-canonical Control Category cells** come from 2 agents, both among the 33 that did not read `control-categories.md`: 10 of 10 cells. The 5 agents that did read it have 0 flagged cells.
