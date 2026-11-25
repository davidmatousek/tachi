# SC-8 post-fix runs: the scorer and controls stages on `ascii-web-api` (T075, W5, PR 1)

**Date:** 2026-11-24. **Base:** the lane at `cf33859`. **Inputs:** [sc8-baseline.md](sc8-baseline.md) (T021(b): baselines, arrangement, method), [w5-setup-pr1.md](w5-setup-pr1.md) sections 1 to 3, 8 and 9, [t147-fixes-pr1.md](t147-fixes-pr1.md), spec US-1a #6 and #7, NFR-1, tasks T075. **Run:** one live `/tachi.risk-score`, then `/tachi.compensating-controls --target sc8-target`, in one session on the install `v4.48.4-162-g1e3614a` (T147's fix `1e3614a`; Claude Code 2.1.331, macOS), at `--effort medium`. First attempt.

## Result

| | `/tachi.risk-score` | `/tachi.compensating-controls` |
|---|---|---|
| **Output tokens** (the command's turns and every subagent, thinking included) | **9,493** | **10,207** |
| **Delta against T021(b)** | **-17,556 tokens (-64.9%)** (baseline 27,049) | **-24,993 tokens (-71.0%)** (baseline 35,200) |
| "Cheaper" under US-1a #7 (delta below zero) | **yes** | **yes** |
| SC-8's ceiling (baseline plus 10%) | 29,753: 20,260 under | 38,720: 28,513 under |
| main session / agent / thinking | 1,881 / 7,612 / 870 (9%) | 1,675 / 8,532 / 1,488 (15%) |
| **Batches** (planned / dispatched / done) | **1 / 1 / 1** (11 units, below the threshold) | **1 / 1 / 1** (11 units, below the threshold) |
| NFR-1, structure (PM W3 ruling 2) | **holds**: every contract section, table and field present, bar items the contract lets a run omit; the template's reference sub-sections are in neither run (section 7) | **holds**, same (section 7) |
| Narrative fallback | 0 of 44 fields | 0 of 4 fields (and 0 of 32 other agent text fields) |
| Wall time (the session's timer) | 1 min 29 s (T021(b): 2 min 48 s) | 1 min 21 s (T021(b): 3 min 36 s) |
| **Verdict** | **PASS** | **PASS** |

- Neither stage is over its baseline, so SC-8's overage trip-wire (P-7) and T078 don't apply, and TW-L2 calls for no second attempt. Each side is one run, so the sign of each delta is firm (the post-fix totals are 35% and 29% of the baselines) and its size is not.
- `/usage`, "Current week (all models)": 47% before, 48% after. The by-model lines agree to within 0.2k: Opus 3.7k (transcripts 3,556), Sonnet 16.1k (16,144), Haiku 188 (no transcript response).

## 1. The arrangement

- **Adopter.** A fresh `git clone` of `<adopter w5b-sc8>` (restore point `4cacfea`, above the commit "Install tachi v4.48.4-162-g1e3614a") into a new directory, with the generic repo-local identity. Checked in the clone before launch: `threats.md` sha256 `4e5f000b...`, architecture sha256 `2791c7bc...` and `sc8-target` tree `fb3cfb11...`, all equal to sc8-baseline.md's. After both stages the tree digest is unchanged and `git status` under `sc8-target` is empty. The populator grew `threats.md` to 16,540 B (+15 lines), and that file is byte-identical to T021(b)'s post-populator file (sha256 prefix `086781fd` in both), so the two runs scored the same input.
- **Launch (D-L2).** Detached terminal-multiplexer session (200 x 50), cwd the clone, `env -i` with `HOME`, `USER`, `LOGNAME`, `SHELL=/bin/zsh`, `TERM=xterm-256color`, `LANG=en_US.UTF-8` and a `PATH` of the user's bin directory, `/opt/homebrew/bin` and the system directories, then `claude --effort medium`. No `CLAUDE_CODE_*` variable, no effort variable, no session profile, auto permission mode. The banner read Opus 5.5 with medium effort. The trust dialog was answered "Yes, I trust this folder". `python3` was the clean environment's 3.14.4 (outside CI's range): all nine script calls ran without a Python error.
- **Conditions against T021(b).** The same example, inputs and effort, no profile, one fresh session for both stages. Differences: Claude Code 2.1.331 against 2.1.330; the account's settings now default Opus to xhigh, which the `--effort medium` flag overrides (D-L2); and the build under test (T147's fix, not v4.48.4).
- **Commands.** `/tachi.risk-score`, no arguments, at 18:28:43Z (it auto-detected the input directory). After its final report, with no agent running, `/tachi.compensating-controls --target sc8-target` at 18:31:26Z. The terminal also offered a suggested next prompt with `--target .`; it was not used, and the typed line was checked in the input box before submit. No prompt appeared after the trust dialog: the records hold 12 accept decisions (main) and 27 (agents), and no other decision.

## 2. What each stage produced

| | Result |
|---|---|
| **Scorer** | 11 of 11 findings in each of Sections 2, 3 and 4; Section 2a absent (the example lists no RESOLVED finding); 11 SARIF results, IDs equal to the open set, none duplicated. The two files agree per finding on composite, band, CVSS and source (0 disagreements). Section 2 sorted by composite descending, `fresh` on all 11. Bands in both files: High 1, Medium 10. `risk-scores.md` 48,142 B, `.sarif` 32,128 B |
| **Controls** | 11 of 11 findings once each in the Coverage Matrix; Control Found 4, Partial Control 2, No Control Found 5. Headline counts, risk-reduction line (63.7 inherent to 49.2 residual) and Sections 1, 2 and 5 totals equal the sums of the rows. 7 Section 4 blocks for the 7 gap findings: none unjoined, none duplicated, none for a Control Found finding. 11 SARIF results agreeing with the `.md`. `compensating-controls.md` 34,937 B, `.sarif` 36,923 B |

My own readers (not the shipped parsers) ran the scorer's full set and 37 of 37 controls checks; none failed. I adapted one check, "all four band tables", to the contract's rule that an empty band table is left out. **Who wrote the files:** the shipped renderers. The main session made no Write or Edit. Each `.md` ends with the renderer's provenance stamp, each SARIF holds `tachi_provenance`, and their digests equal the stage records'. No unresolved `{{slot}}` token sits outside the Scoring Inputs and Assessment Inputs tables.

## 3. Tokens, model and effort

| | Model | Effort | Responses | Output tokens | Thinking | Against T021(b) |
|---|---|---|---|---|---|---|
| Scorer, main session | Opus 5.5 | medium | 9 | 1,881 | 93 | -836 (-30.8%) |
| Scorer, 1 agent | Sonnet 5.5 (pinned `sonnet`) | medium | 5 | 7,612 | 777 | -16,720 (-68.7%) |
| Controls, main session | Opus 5.5 | medium | 7 | 1,675 | 0 | -902 (-35.0%) |
| Controls, 1 agent | Sonnet 5.5 (pinned `sonnet`) | medium | 5 | 8,532 | 1,488 | -24,091 (-73.8%) |

- Thinking against T021(b): scorer 870 against 5,667 (-84.6%), controls 1,488 against 8,280 (-82.0%). Each agent's one Write is 6,318 and 6,519 output tokens (13,117 B and 13,004 B), 83% and 76% of the agent's tokens.
- Requested equals served on all 26 responses, and effort and per-turn effort are medium on all 26, agents included. No fallback credit. Stops: main 12 `tool_use` and 4 `end_turn`; agents 10 `tool_use` (each ends on its hand-back); 0 `max_tokens`. Each response is counted once by message ID, split at the second command's submit.

## 4. The stage records (`tachi.stage-record/1`)

Both: status `success-with-warnings`, tool 4.48.4; units 11, open 11, rendered 11, resolved 0; batches planned, dispatched and done 1, exhausted, retried and split 0; overflow events 0, retries 0 (budget 2, used 0); narrative fallbacks, truncations and parse errors 0 (controls: cell overwrites 0); undeclared paths 0. One warning each, `architecture-path:body-line:absent` (disposition (a): the example names no architecture source). Plan batch size 13 (scorer) and 11 (controls): one batch of 11. One part file each, attempt 1. Exit codes: presence check 0, populator 0, `plan` 0, `reconcile` 0, render 5. The final exit is 5 in both, disposition (a)'s pass state. The records' own durations (plan to render) are 60 s and 64 s.

## 5. Timeline and the completion rule

| Offset from submit (m:ss) | Scorer | Controls |
|---|---|---|
| Main session's first tool call (presence check) | 0:04 | 0:05 |
| `plan` (exit 0) | 0:24 | 0:09 |
| Agent dispatched (1 Agent call) | 0:29 | 0:14 |
| Main ends its turn (`end_turn`) | 0:34 | 0:18 |
| Agent's hand-back, then one completion notice | 1:14 | 1:05 |
| `reconcile` (once, exit 0) | 1:19 | 1:10 |
| Renderer (exit 5) | 1:24 | 1:14 |
| Final report complete | 1:28 | 1:20 |

Each agent ran as a background agent (the metadata says `background`; the Agent calls named no flag), 43 s and 50 s. The main session made no tool call between a dispatch and its notice. Disposition (b): no `reconcile` before the agent reported, no render before `reconcile` exited 0, no second `reconcile` or re-dispatch.

## 6. SC-3, structure only (US-1a #6), and Step 6

- **Agents.** 1 `tachi-risk-scorer` and 1 `tachi-control-analyzer`, the types the commands name (metadata agrees), spawn depth 1: 0 stand-ins. Each prompt is the command's fixed line with the batch input path (223 and 234 characters). Their tools: scorer Read 6, Grep 1 (the threats file), Write 1; controls Read 15 (10 of them target files), Glob 1 (the target), Write 1; no Bash. Each Write names its own `part_path`, a `.json` file: 0 program files. Hand-backs: 701 B and 1,010 B, 0 code fences.
- **Main session.** 10 Bash (6 and 4) and 2 Agent; no Read, Write or Edit. Every call opens with `cd` to the adopter root. 9 script runs (2 inside the presence-check calls), each a single `python3` call to a shipped script the command names, with literal arguments and single-quoted paths. The other programs are `ls` listings and one `sort` per stage (Step 0's directory sort). **0 unnamed programs**: no `python3 -c`, `-m` or heredoc, no other interpreter, no text tool on a file.
- **Step 6.** Each report is the renderer's three summary lines and its warning, as written (4 of 4), the Next steps block, equal to the command's (5 and 7 lines), and 2 code-fence lines: **0 lines beyond** them. No tool call after the render result. (T073 attempt 2: 0 of 12 lines; attempt 1: 7 of 19.)

## 7. NFR-1, the structural half (PM W3 ruling 2)

Compared by headings, table headers, bold labels, frontmatter keys and JSON key paths; no value. A: the shipped output template (the contract). B: T021(b)'s files, read-only.

| | A. contract against the new file | B. T021(b) against the new file |
|---|---|---|
| `risk-scores.md` | `##` 6 of 7, tables 12 of 13, labels 9 of 12 (one is a template caption), frontmatter 13 of 13 | each v1.0 element has its v1.1 form, bar two (below); added: Section 6, `Source`, `Flags`, `Percentage`, `baseline` |
| `risk-scores.sarif` | 79 of 82 key paths | 4 paths absent, none named by the contract (below) |
| `compensating-controls.md` | `##` 7 of 7, tables 20 of 20, labels 13 of 14 (the caption), frontmatter 7 of 7 | the Coverage Matrix columns reordered with `CF` added (K8); Section 7 added |
| `compensating-controls.sarif` | 86 of 89 key paths | 3 paths absent, none named by the contract (below) |

- **Absent as the contract allows.** Section 2a (appears only with RESOLVED findings; none here) and its table; `Correlation Group` and `Integrity` lines (only for a correlated or flagged finding; none) and the SARIF `correlation-group`, `-primary` and `-role` keys (both SARIF files); the controls file's Critical band table and Low recommendation group (a table or group that would hold nothing is left out); the CSRF Protection and CSP/Security Headers subsections (6 of 8 categories hold a control).
- **Template reference text.** The scorer template names three sub-sections (`Column Definitions`, `Field Definitions`, `Override Guidance`) and the controls template one (`Column Definitions`). Neither the shipped renderers nor T021(b)'s agent wrote them. If the oracle's reading of "the contract names" counts them, they are absent in both runs. That reading is T066's.
- **In T021(b), named by no contract, not written.** The scorer `.md`'s `### Notes` (agent commentary under Section 5) and the `Component` column of its Section 4 table (the contract's table has none; Sections 2 and 3 hold the component). In SARIF, `results[].properties.baseline-state` (scorer file, 11 of 11 results) and `taxonomies[].organization` and `.shortDescription` (both files, 2 of 2 entries). The new files add `tachi_provenance`, `primaryLocationLineHash`, `score-flags` (scorer) and `integrity-flags` (controls).
- **Renamed by the v1.1 template, carried.** The scorer's six v1.0 labels the new file lacks verbatim map one to one: `Highest-Risk Component` (case), Section 1's first sentence, the finding heading, `**Vector**`, `**Composite**` and the four per-dimension subsections. Column names changed in Sections 2 (`Exploit.`, `Scale.`, `Reach.`) and 5 (`What It Measures`, `Composite Score Range`, `Default SLA`, `Default Disposition`), and Section 5's six subsections are numbered 5.1 to 5.6.

## 8. TW-L2 and fallback verdicts

- **TW-L2:** no shipped-code defect, no agent off its contract, no interruption. SC-8 isn't over (P-7). Nothing here needs T077's decision.
- **Fallback (ruling 2):** scorer 0 of 44 narrative fields (11 units x 4 rationales); controls 0 of 4 (1 evidence assessment x 4 dimensions) and 0 of 11 matrix rows, 7 recommendation bodies and 14 evidence texts. Under 10% and 25%, and no slot that should resolve fell back. **Not exercised:** US-1a #4 and #5 (re-dispatch, overflow, retry), since each batch finished first time.

## Reference reads (structure only)

| Read | Scorer (1 agent) | Controls (1 agent) |
|---|---|---|
| Batch input; `part-file-contract-shared.md` | 1 of 1; 1 of 1 | 1 of 1; 1 of 1 |
| `trust-zones` / `cvss-vectors` / `scoring-dimensions` / `reachability-analysis` | 1 / 1 / 1 / 1 | not read |
| `control-categories` / `evidence-criteria` / `residual-risk` | not read | 1 / 1 / 1 |
| All binding; at least one; none | 1; 1; 0 | 1; 1; 0 |
| `asset-modifiers`, `severity-bands`, `output-formatting` (context) | 0 each | n/a |
| Failed Reads on a user-level skills path | 0 (and 0 successful) | 0 (and 0 successful) |
| An architecture file | 0 (the batch input's `refs` name the threats file only) | 0 (`refs` name the scored input, the target and the threats file) |

The contract and every binding read came before each agent's first Write (2 of 2). T021(b)'s 3 failed user-level Reads did not recur.

## Observations

1. **Where the tokens went.** T021(b)'s agents wrote whole files (24,332 and 32,623 agent tokens). Now each agent writes one 13 kB part file and the renderer writes the files, so the agents' tokens fell 69% and 74%, each stage's thinking 85% and 82%, and the main session's tokens 31% and 35%.
2. **T021(b)'s observation 1 (working directory).** The main session's calls all start from the adopter root, and `plan` stored the relative `--target` as an absolute path in the batch input, so the agent doesn't depend on the session's directory.
3. **What the file holds, not structure (T066's business).** T021(b)'s Section 3 listed 11 controls, 2 of them "Detected, no mapped threat" (the CSRF Protection and CSP/Security Headers entries). The new file lists 7, each tied to a finding; no contract text names an unmapped control. The distributions also moved (scorer High 1 and Medium 10 against High 2, Medium 6 and Low 3; controls 4, 2 and 5 against 4, 5 and 2). One run each, so agent variance isn't separable.
