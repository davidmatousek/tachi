# SC-1 baseline: v4.48.4's scorer on the large fixture (T021(a), W1)

**Date:** 2026-11-22. **Base:** W1's base plus T019 (`c84ff16`, the fixture) and T023 (`de96163`, D6's "Amended at W0" table). **Inputs:** the fixture's `baseline/threats.md` and `architecture/architecture.md`, ADR-050 D6, [s1-proxy.md](s1-proxy.md) and [w0-gate.md](w0-gate.md). **Run:** one live `/tachi.risk-score` on v4.48.4 (Claude Code 2.1.330, macOS), before any renderer code (D-7).

T021(b), SC-8's baselines, ran after the architect ruled on D6 and is in `sc8-baseline.md`. Section 8 holds the calibration Write that the architect ruled for after this record's first version. It decides D6's sizes (13, 11 and 12) and supersedes section 5.4's implied verdicts.

## Result: no overflow and no dropped finding, but the scorer did not finish in contract

| Question | Result |
|---|---|
| Did a response overflow? | No. 26 responses, none stopped at `max_tokens`. The largest was 13,636 output tokens. The scorer saw the size coming and attempted no output file |
| Was a finding dropped? | Not from `risk-scores.md`: 408 of 408 in each of Sections 2, 3 and 4. `risk-scores.sarif` holds 326 results, and the other 82 findings appear as `relatedLocations` (v4.48.4's rule). D8's one result per open finding needs 408 |
| Who wrote the two files? | A script, so neither the scorer nor the main session wrote them. The scorer wrote a 23,485-byte Python generator that it could not run, and handed it back. The main session read it and ran it with Bash |
| SC-3's classes, as measured | 1 unshipped script run, 1 program file written, 1 code hand-back, 0 stand-in dispatches |
| Output sizes (bytes ÷ 4) | `risk-scores.md` 190,600 tokens; `risk-scores.sarif` 224,661 tokens |
| D6, measurement 1 | Fixture size 13, below the ruled 16. The rule as written re-amends `risk-score` to 13 (section 5) |
| D6, measurement 2 | No model-written JSON file, so the 3.2 test has no input. The estimator and the constants stand (section 5) |
| Model and effort | Main session Opus 5.5, scorer Sonnet 5.5, both at medium effort; no turn fell back |
| Output tokens | 61,119 (39,689 of them thinking) |
| Wall time | 7 min 55 s from the command to the final report |

**TL-T9's disposition applies.** v4.48.4 neither overflowed nor dropped a finding at fixture scale, so this is the baseline and W1 proceeds. SC-1's claim rests on N/N and completeness, plus one measured "before" for its second clause: 2 files rendered by an unshipped, agent-written script today, 0 at the target.

## 1. Method

- **Adopter.** T141's adopter A: v4.48.4 as `scripts/install.sh --version v4.48.4` places it, one clean install commit. Only `baseline/threats.md` (as `docs/security/<run id>/threats.md`) and `architecture/architecture.md` (as `docs/security/architecture.md`) were added, as Lane F advised, and committed in the adopter as a restore point. There was no earlier `risk-scores.md`, so every finding is scored fresh.
- **Session.** A fresh interactive session in a detached terminal multiplexer, cwd the adopter, started from a clean environment: the orchestrating session's effort and output-cap variables were not inherited. It ran at the account's defaults: Opus 5.5, effort medium, auto permission mode, no session profile. The folder-trust dialog was answered "Yes, I trust this folder", and `/tachi.risk-score` was typed with no arguments (the command auto-detected the input directory).
- **Prompts answered:** none after the trust dialog. Auto mode decided all 34 tool uses (the main session's 9 Bash and 1 Agent; the scorer's 12 Read, 5 Glob, 5 Grep, 1 Write and 1 hand-back), with no prompt on screen.
- **Tokens** come from the session's usage records: the main transcript and the scorer's subagent transcript. Each API response is counted once, at its `output_tokens`, which includes thinking. The records also carry `thinking_tokens` per response, so thinking is separable. `/usage`'s by-model lines agree.
- **Outputs** were read from disk and compared with the 408 open IDs of `threats.md`. Per-unit text uses T003's own attribution and percentile (its helper module, reused read-only), so rows A to D are comparable with [s1-proxy.md](s1-proxy.md).
- Raw outputs, transcripts, the agent's script and the measurement scripts stay private.

## 2. What happened

| Time | Event |
|---|---|
| 0:00 | Command submitted. At 0:09 the main session ran the Step 1.5 populator. It rewrote `threats.md`'s `## Affected Assets` block (277 rows moved, one sentence dropped; the same 408 IDs and values) |
| 0:28 | It dispatched `tachi-risk-scorer` as a background agent, although the command text says to wait |
| 0:29 to 7:09 | The scorer read `threats.md` in slices, six reference files and the architecture file. Five long thinking responses followed (about 35k thinking tokens) |
| 7:09 | It wrote `score_threats.py` (one Write, 13,636 output tokens) to the session's scratchpad |
| 7:22 | Hand-back: "The scoring is not finished. `risk-scores.md` and `risk-scores.sarif` were NOT written ... My toolset was Read, Write, Glob and Grep, with no way to run code. I can't append to a file either, and about 408 findings (326 SARIF results) is far too large to write by hand in one call. I did not sample or fabricate scores ... It is untested, because I couldn't run it." |
| 7:27 to 7:34 | The main session grepped the script for side effects and used the adopter's installed SARIF template |
| 7:38 | It ran the script. The script took about 0.4 s, printed `scored=408 sarif_results=326 peers=82 parse_errors=0`, and wrote both files |
| 7:44 to 7:56 | The main session validated the files and printed the stage summary |

The scorer's own hand-back says the scores are rule-derived: exploitability and scalability come from each finding's category, likelihood and impact, not from reading its text.

## 3. Completeness

| Check | Result |
|---|---|
| Open findings in `threats.md` | 408 (346 UNCHANGED, 41 NEW, 21 UPDATED). 6 RESOLVED, not scored |
| `risk-scores.md`: Sections 2, 3 and 4 | 408, 408 and 408 entries; the same 408 IDs in each; 0 missing, 0 extra, 0 duplicated |
| Arithmetic | In 408 of 408 rows the composite equals 0.35C + 0.30E + 0.15S + 0.20R from the row's own cells, and the band matches the composite. Section 1's counts equal the table's, rows are sorted by composite descending, and each block's composite equals its row's |
| `risk-scores.sarif`: results | 326, with unique `findingId/v1` values. 82 peers appear only as `relatedLocations` (on 21 results, the group primaries). Results plus peers cover all 408, with no RESOLVED ID |
| N/N under D8 | N = 408. 326 present, short by 82 by v4.48.4's own design (primaries and uncorrelated findings; 21 groups, 103 members) |
| Fingerprints | `partialFingerprints` on 326 of 326 (`findingId/v1`; `correlationGroup` on the 21 primaries). `primaryLocationLineHash` on 0 of 326, and every location is the architecture file |
| Truncation | Only the format's documented 60-character Threat cell in Section 2 (all 408 rows); Section 3 carries the full text. No other cut, and no partial or placeholder row |
| Bands | Critical 0, High 27, Medium 348, Low 33; highest composite 8.3. Of the input's 56 Critical-risk findings, 0 reach the Critical band (19 High, 34 Medium, 3 Low) |

## 4. Per-output token estimates (SC-1's baseline column)

| Output | UTF-8 bytes | Tokens (bytes ÷ 4) | × 64k | × 128k |
|---|---|---|---|---|
| `risk-scores.md` | 762,399 | 190,600 | 2.98 | 1.49 |
| `risk-scores.sarif` | 898,642 | 224,661 | 3.51 | 1.76 |
| Both | 1,661,041 | 415,260 | | |

- Each request carried `max_tokens` 128,000 (adaptive thinking, effort medium), not 64,000. Both files exceed the real per-response cap, and exceed twice the 64k figure that S-4's sizing check uses.
- For scale, the fixture's committed complete files are 697,215 bytes (174,304 tokens) for `baseline/risk-scores.md` and 792,800 bytes (198,200 tokens) for `baseline/risk-scores.sarif`.
- Real tokens are probably higher than these estimates (section 5.3).

## 5. D6's two measurements

### 5.1 Measurement 1: the per-unit text of `risk-scores.md`

T003's attribution: the Scored Threat Table row, the Dimensional Breakdown block and the Governance row. p90 by linear interpolation, u = p90 ÷ 4 × 1.25, size = min(⌊8,000 ÷ u⌋, ⌊32,000 ÷ (u × F)⌋).

| Reading (T003's rows) | Units | p90 bytes | u | Size | Shipped examples (u, size) |
|---|---|---|---|---|---|
| **Markdown only, every unit, F = 1** (the rule's reading) | 408 | 1,927 | 602 | **13** | |
| D: markdown only, units in both files, F = 2 | 326 | 1,903 | 595 | 13 | 541, 14 |
| A: the heavier file as written (the SARIF), F = 2 | 326 | 2,550 | 797 | 10 | 802, 9 |
| B: both files summed, F = 2 | 326 | 4,458 | 1,393 | 5 | 1,338, 5 |
| C: SARIF re-serialized compact, heavier file, F = 2 | 326 | 1,938 | 606 | 13 | 580, 13 |

- **The fixture confirms the proxy's rows A to D within 1.** Row E, the part item, can only be confirmed by W5's live runs, as s1-proxy.md §4 says.
- **What a markdown unit weighs** (p90 bytes): heading carrying the full threat text 711, meta lines 215, computed dimension table 263, CVSS vector line 64, rationale bullets 523, Section 2 row 144, Section 4 row 77. Most of that is what the renderer will write or take from the reference set. The model-authored part (vector line plus rationale) is 587 bytes here, but this run's rationale is a script template, so it says nothing about a model's prose.

### 5.2 Measurement 2: the real tokens per Write of a whole output file

The run made one Write, and it was not an output file.

| Write | Bytes | Response output tokens | Thinking | Visible | Bytes per visible token |
|---|---|---|---|---|---|
| `score_threats.py` (Python source, in the session scratchpad) | 23,485 | 13,636 | 2,124 | 11,512 | 2.04 |

Thinking is separable here, because the usage record gives it per response. But the file is Python, not JSON, so the rule's 3.2 test has no input. The nearest clause is the third (the model wrote no per-unit output); read that way, the estimator and the constants stand.

### 5.3 Reference points for the ÷4 estimator (not D6's measure)

All come from the same session's usage records. None is a JSON Write.

| Where | Content | Bytes | Tokens | Bytes per token |
|---|---|---|---|---|
| Output | The one Write (Python, JSON-escaped in the call) | 23,485 | 11,512 | 2.04 |
| Output | The scorer's hand-back (prose, code, five long paths) | 4,001 | 1,643 | 2.44 |
| Output | The main session's final report (prose, one long path) | 2,813 | 1,083 | 2.60 |
| Input | One Read of `threats.md` (markdown table rows) | 13,507 | 5,474 | 2.47 |
| Input | Four Read results (two `threats.md` slices, two reference docs; markdown) | 39,021 | 16,388 | 2.38 |
| Input | One Read of the SARIF template (pretty-printed JSON) | 7,027 | 2,330 | 3.02 (2.80 on the raw 6,535 bytes) |

- The input rows come from the growth of the prompt between responses, net of the previous response's output. They include the Read tool's line-number prefix and carry about ±10%.
- Every figure sits below the rule's 3.2, and well below the 4 that the estimator assumes. The JSON template, the closest to a part file, is at 2.8 to 3.0.
- **If the rule's second clause fired at a ratio r in place of 4,** the sizes would be (ADR p90s of 1,520 and 1,930 bytes):

  | r | 2.0 | 2.5 | 2.8 | 3.0 | 3.2 | 4.0 |
  |---|---|---|---|---|---|---|
  | `risk-score` | 8 | 10 | 11 | 12 | 13 | 16 |
  | `compensating-controls` | 6 | 8 | 9 | 9 | 10 | 13 |

- **P-7's example** (`ascii-web-api`, 11 findings in one batch per stage) needs both sizes at least 11. That needs r of 2.62 or more for the scorer and 3.32 or more for controls. At r = 3.2, controls would be 10, and P-7's example would return to the PM before T021(b).
- A clean output-side reading needs one response that Writes a part-shaped JSON file at two-space indentation. A calibration Write by a Sonnet 5.5 scorer at medium effort would cost about 10k output tokens. Counting tokens on the fixture's own `baseline/risk-scores.sarif` would give the tokenizer side. Neither was run in T021(a), and section 8 runs the calibration Write.

### 5.4 Verdicts the stated rule implies

*Superseded by section 8: the architect ruled the sizes neither confirmed nor re-amended until one calibration Write per part stage decides them.*

| Constant | Measured here | Implied by D6's rule |
|---|---|---|
| `risk-score` 16 | Fixture size 13 (measurement 1); no JSON Write (measurement 2) | **Re-amend to 13** (13 is below 16). Measurement 2 leaves the estimator in place |
| `compensating-controls` 13 | Not run in (a) | Stands. The ratio test had no input |
| `trees` 12 | Not measured at W1 (T130 confirms) | Stands |

**For the architect.** The rule as written gives 13. Two things bear on whether to apply it:
- The measured object (the old markdown unit) is not the ruled one (a part item). It carries about 710 bytes of threat text and about 700 bytes of computed cells (dimension table, meta lines and the two table rows) that the renderer will own. Its model-authored part is a script template here, so this run can't speak to the ruled u of 475, which rests on model-written prose.
- The estimator evidence in 5.3 is below 3.2 on every reading. If the architect applies the second clause to it, both sizes fall below the ruled constants (5.3's table).

## 6. Model, effort, tokens and time

| | Model | Effort | Responses | Output tokens | Thinking |
|---|---|---|---|---|---|
| Main session | Opus 5.5 | medium | 12 | 5,263 | 543 |
| Scorer subagent | Sonnet 5.5 (the agent's pinned `sonnet`) | medium | 14 | 55,856 | 39,146 |
| **Total** | | | **26** | **61,119** | **39,689 (65%)** |

- The requested model equals the served model on all 26 responses, so nothing fell back. Stops: 24 `tool_use`, 2 `end_turn`, 0 `max_tokens`.
- Of the scorer's 55,856 tokens, 70% was thinking, 11,512 were the script and 1,643 the hand-back.
- `/usage` lists Opus 5.3k, Sonnet 55.9k and Haiku 1.1k output tokens. The Haiku calls leave no response in the transcripts, so the session's total is about 62.3k.
- **Wall time:** 7 min 55 s from the command to the final report (the scorer 6 min 52 s). The whole session, from launch to `/usage`, took 9 min 17 s.

## 7. Observations for T021(b), T023 and the lanes

1. **Run arrangement.** The private run notes record one environment-dependent effect on this run. So T021(b) and every post-fix run use adopter directories arranged the same way as each other, and the baseline and post-fix runs of each comparison share one arrangement (T072, T075).
2. **A 128k response cap.** In a clean environment each request carried `max_tokens` 128,000. The 64k in PRD D-2 and in S-4's sizing check is not this environment's cap, so those texts need that qualifier. The fixture's outputs still exceed 128k (section 4).
3. **Background dispatch.** v4.48.4's command text says to wait for the agent. The main session backgrounded it and ended its turn. S-8's foreground rule can't be met by command text alone: the Agent tool in this Claude Code version has no foreground option (section 8.1).
4. **The fixture isn't a fixed point of the populator.** Step 1.5 reordered its `## Affected Assets` rows into Section 7's order and dropped the introductory sentence. The values didn't change. Lane F may want the committed block in the populator's own form, so that no run changes the input digest.
5. **Thinking dominates.** 65% of the stage's output tokens were thinking at medium effort, so SC-8's baseline (T021(b)) will be mostly thinking too. This is one run, so the record has no variance estimate.

## 8. Calibration Write (the architect's ruling (iii), ADR-050 D6 at `282dbbe`)

T021(a) gave D6's two rules no valid input (section 5), so the architect ruled that the sizes are neither confirmed nor re-amended until one calibration Write per part stage decides them. This is that calibration.

### 8.1 Method

- **The files.** Two `tachi.part/1` objects at two-space indentation, built from the fixture's findings: narrative strings with no digit outside a slot, controls evidence drawn from the fixture's stub codebase, and a `matrix_row` of 11 cells with slot tokens in the computed ones. A validator pass against the closed key sets in `contracts/part-files.md` found no error. An item's size is its block inside the part, indented and with its separator.

  | Part | Items | File bytes | Item bytes: mean (min to max) | Target |
  |---|---|---|---|---|
  | `risk-score` (scorer) | 16 | 24,713 | 1,519 (1,505 to 1,532) | 1,520, within 5% |
  | `compensating-controls` | 13 | 25,512 | 1,933 (1,873 to 2,012) | 1,930, within 5% |

  Text-bearing strings are 49% of the scorer part's bytes and 74% of the controls part's. The rest is keys, small integers and indentation.
- **The session.** A fresh interactive session in adopter A, reset to its install commit with a clean tree, arranged as T021(a)'s was: a clean environment, Opus 5.5 at medium effort, auto permission mode, no session profile. The main session dispatched `tachi-risk-scorer` (Sonnet 5.5, effort medium) once per file, one after the other.
- **The agent's prompt:** read the source JSON file at a given path, write its exact content to a path inside the adopter in one Write call, byte for byte, and reply with only "Done". The source went by path, so the main session didn't have to re-emit 25 KB per dispatch (the spec's wording puts the JSON in the prompt).
- **The dispatches were background agents.** The main session was told to dispatch in the foreground, but the Agent tool in this Claude Code version has no foreground option, and each agent's record says `background`. The main session waited for each completion notice before it started the next dispatch. S-8's "every dispatch runs in the foreground" and D4's Step 3 wording need that qualifier.
- **The check.** Each written file was compared with its source with `cmp`. Both are identical, so no re-run was needed.

### 8.2 Measurements

| Part | Bytes on disk | Response output tokens | Thinking | Visible tokens | r (bytes ÷ visible tokens) |
|---|---|---|---|---|---|
| `risk-score` | 24,713 | 9,511 | 0 | 9,511 | **2.598** |
| `compensating-controls` | 25,512 | 9,175 | 0 | 9,175 | **2.781** |

- Each Write response held that one tool call and nothing else, with no text and no thinking block, so thinking is separated trivially. Each agent made three responses: a Read, the Write and the hand-back.
- r is slightly conservative. The response's tokens include the call's file path (about 170 characters), and the content travels JSON-escaped in the call (5% to 6.5% more bytes than the file). Per escaped byte the ratios are 2.77 and 2.92. The rule's measure is the file's bytes.
- The session cost 20,317 output tokens (the main session's 1,253 on Opus, the agents' 19,064 on Sonnet).

### 8.3 The outcome

Each stage takes its own r, as D6's text has it. Both are below 3.2.

| Constant | W0 (ruled) | r | After the calibration | By the rule |
|---|---|---|---|---|
| `risk-score` | 16 | 2.598 | **13** | ⌊8,000 × 2.598 ÷ 1,520⌋ |
| `compensating-controls` | 13 | 2.781 | **11** | ⌊8,000 × 2.781 ÷ 1,930⌋ |
| `trees` | 12 | | 12 | stays until T130 |

- At the ruled 16 and 13 items, the two parts cost 9,511 and 9,175 tokens, which is 19% and 15% over S-1's 8,000 per Write. The measured tokens per item are 594 and 706, against W0's u of 475 and 603. At 13 and 11 items the parts would cost about 7,600 tokens each at these r values.
- **P-7's gate.** `ascii-web-api` (11 open findings) is one batch in both stages only if both sizes are at least 11. The scorer's 13 clears that, and controls need r of 2.654 or more for 11: r = 2.781 clears it by 4.8%. So the example stands as P-7's example, and T021(b) ran on it (`sc8-baseline.md`).
- r depends on the content mix. The scorer part, half of it structure, measured lower than the controls part. W5's stage records log each live part's size, so TW-L2 re-checks the sizes against real parts.
