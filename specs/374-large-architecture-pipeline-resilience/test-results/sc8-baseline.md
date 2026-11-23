# SC-8 baseline: v4.48.4's scorer and controls stages on `ascii-web-api` (T021(b), W1)

**Date:** 2026-11-22. **Base:** the lane at `515f6cd`. **Inputs:** the shipped example `examples/ascii-web-api/` (11 open findings), the fixture's stub codebase as committed at `c84ff16`, ADR-050 D6's per-stage sizes (13, 11 and 12) and P-7, and [prefix-baseline.md](prefix-baseline.md) section 8. **Run:** one live pass of `/tachi.risk-score`, then `/tachi.compensating-controls --target sc8-target`, on v4.48.4 (Claude Code 2.1.330, macOS). Both ran at the adopter default effort, with no session profile (G0 ruled that T075 doesn't double as R-27's smoke run).

## Result

| | `/tachi.risk-score` | `/tachi.compensating-controls` |
|---|---|---|
| **Output tokens** (the command's turns and every subagent, thinking included) | **27,049** | **35,200** |
| of which thinking | 5,667 (21%) | 8,280 (24%) |
| main session (Opus 5.5) | 2,717 in 8 responses | 2,577 in 5 responses |
| the agent (Sonnet 5.5) | 24,332 in 7 responses | 32,623 in 9 responses |
| **Batches** (agent dispatches) | **1** | **1** |
| **Wall time** | **2 min 48 s** | **3 min 36 s** |
| Output files | `risk-scores.md` 16,989 B, `risk-scores.sarif` 24,469 B | `compensating-controls.md` 25,158 B, `compensating-controls.sarif` 28,912 B |
| **SC-8's ceiling** (baseline plus 10%) | 29,753 | 38,720 |

- **Both stages finished in contract.** Each agent wrote its own two files, one Write per file, with no script, no hand-back and no stand-in dispatch. That is the opposite of T021(a)'s fixture run, where the scorer handed back code.
- **For T075.** Each stage's delta is recorded against its figure above, and public text calls a stage cheaper only if its delta is below zero (US-1a #7). At 11 findings each stage should plan one batch (D6's sizes of 13 and 11).

## 1. The arrangement (T072 and T075 reproduce this)

1. **The adopter.** A clone of T141's adopter B (v4.48.4, install commit `04de260`, clean) at a neutral adopter path, outside every tachi tree. One commit of its own, `d7b7ce7`, is the restore point: it adds the target and the inputs below. The clone got a generic repo-local git identity.
2. **The controls target.** The fixture's stub codebase, copied byte for byte from `tests/scripts/fixtures/large_arch/stub-codebase/` as committed at `c84ff16` into `sc8-target/` at the adopter's root. That is 15 files: a README and 14 modules under `src/`. It sits outside tachi's installed paths and outside the output directory.
   - **Tree digest:** `git rev-parse HEAD:sc8-target` = `fb3cfb11ba5479ec2aaacf2e4496198dbd897425`. It equals `git rev-parse c84ff16:tests/scripts/fixtures/large_arch/stub-codebase` in the tachi repository, so T075 can check it either way.
   - After both stages the digest is unchanged and `git diff HEAD -- sc8-target` is empty: the stage only read it.
3. **The inputs.** `examples/ascii-web-api/threats.md` (sha256 `4e5f000b616ec06be2b5ca11850ff151303fdda65639e6c6c2bdbc166945cfbc`, identical to v4.48.4's) was copied to `docs/security/2026-04-10T00-00-00/threats.md`. The directory name is the example's date. `examples/ascii-web-api/input.md` (sha256 `2791c7bca71fa7e103f44b9d37c7336f1d947e9ba0e9ffb04c6be5ac728817db`, identical to v4.48.4's) was copied to `docs/security/architecture.md`, where the commands look for an architecture file. Nothing else was added.
4. **The session.** A fresh interactive session in a clean environment (no inherited variables), cwd the adopter, started once for both stages. It ran at the account's defaults: Opus 5.5, effort medium, auto permission mode, no session profile. The folder-trust dialog was answered "Yes, I trust this folder". No other prompt appeared, and auto mode decided every tool use.
5. **The commands, typed as-is.**
   - `/tachi.risk-score` with no arguments. It auto-detected the input directory.
   - After that stage's main session had printed its final report and no agent was running, `/tachi.compensating-controls --target sc8-target`. The `--target` value is relative. The main session expanded it to an absolute path in the agent's prompt, as it did every other path.
6. **The count.** Each stage's tokens are the assistant responses of the main transcript and the agent's transcript, each response counted once at its `output_tokens`, split at the second command's submit time. `thinking_tokens` is in the same record. `/usage`'s by-model lines agree (Opus 5.3k, Sonnet 57.0k and Haiku 0.7k output tokens for the session; the Haiku calls leave no response in the transcripts).

Step 1.5's populator edited the copied `threats.md` in place: it added a 15-line `## Affected Assets` block (11 rows, all `[]`), so the file grew from 16,311 to 16,540 bytes. The post-fix run's arrangement sees the same edit, since it is a stock step.

## 2. What each stage produced

| | Result |
|---|---|
| **Scorer** | 11 of 11 findings in each of `risk-scores.md` Sections 2, 3 and 4, and 11 results in `risk-scores.sarif` (no `relatedLocations`, no `primaryLocationLineHash`). Bands: Critical 0, High 2, Medium 6, Low 3. Written by the agent itself |
| **Controls** | 11 of 11 findings in the Coverage Matrix and 11 results in `compensating-controls.sarif`. Control Found 4, Partial Control 5, No Control Found 2. Seven recommendation blocks in Section 4 (the five partial findings and the two with no control). Written by the agent itself |

The four Writes are the only whole-file Writes in the session. They add real JSON readings to the calibration's (the thinking is separated in each response):

| File | Bytes | Response output tokens | Thinking | Visible | Bytes per visible token |
|---|---|---|---|---|---|
| `risk-scores.sarif` | 24,469 | 9,301 | 282 | 9,019 | 2.71 |
| `risk-scores.md` | 16,989 | 9,053 | 1,119 | 7,934 | 2.14 |
| `compensating-controls.md` | 25,158 | 17,478 | 7,447 | 10,031 | 2.51 |
| `compensating-controls.sarif` | 28,912 | 10,772 | 446 | 10,326 | 2.80 |

The two JSON files sit at 2.71 and 2.80, beside the calibration's 2.60 and 2.78 and below 3.2. None of the four Write responses stopped at `max_tokens` (each request carried 128,000).

## 3. Model and effort per turn

| | Model (requested = served) | Effort | Responses |
|---|---|---|---|
| Main session, both stages | Opus 5.5 | medium | 13 |
| Scorer agent | Sonnet 5.5 (the agent's pinned `sonnet`) | medium | 7 |
| Controls agent | Sonnet 5.5 (the agent's pinned `sonnet`) | medium | 9 |

All 29 responses ran at medium effort with adaptive thinking, and none fell back to another model. Stops: 25 `tool_use` and 4 `end_turn`.

## 4. The completion rule

The platform has no foreground dispatch (prefix-baseline.md section 8.1). Both stages' agents ran as background agents, and v4.48.4's main session kept to the rule in both: it dispatched the agent, said that it would report when the agent finished, and ended its turn. It made no tool call until the completion notice, then validated once and gave its final report. Neither stage was judged done before its notice.

| Offsets from the command's submit (minutes:seconds, to about a second) | Scorer stage | Controls stage |
|---|---|---|
| Main session's first tool call | 0:05 | 0:05 |
| Agent dispatched | 0:20 | 0:13 |
| Main session ends its turn (`end_turn`) | 0:28 | 0:16 |
| Agent's hand-back | 2:27 | 3:10 |
| Main session resumes | 2:37 | 3:23 |
| Final report complete | 2:48 | 3:36 |

The wall times in the result table are the session's own timers for each command ("2m 48s" and "3m 36s").

## 5. Observations for T075

1. **A directory change that did nothing here.** After the scorer stage, the main session's working directory sat in the output directory, because its validation step had changed into it. The controls stage still resolved everything, because the main session wrote absolute paths into the agent's prompt, the target included (it expanded the relative `--target`). A post-fix main session that left `sc8-target` relative would depend on its working directory, so T075 should check the agent's prompt for the target path.
2. **Noise from three failed Reads.** The controls agent first tried its three skill references under a user-level skills directory, got "file does not exist" three times, and found them in the adopter's own `.claude/skills/`. A single run can't say how often that happens.
3. **No variance estimate.** Each figure is one run, and thinking is 21% and 24% of the tokens. The post-fix run's two attempts per stage (TW-L2) will show some of the spread.
4. **Both stages carry the populator's in-place edit** (section 1), so the input digest differs from the example's.
