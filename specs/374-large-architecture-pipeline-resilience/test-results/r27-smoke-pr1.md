# R-27's smoke run under the session profile, PR 1 (T076, W5)

**Date:** 2026-11-24. **Base:** the lane at `cf33859`; build `v4.48.4-162-g1e3614a` (T147's fix, `1e3614a`). **Inputs:** T076; [w5-setup-pr1.md](w5-setup-pr1.md) sections 5, 8 (D-L8) and 9; the runbook's sections 3, 5 and 11; [t147-fixes-pr1.md](t147-fixes-pr1.md). **Run:** one live session, attempt 1, key-less, on the shipped example `ascii-web-api`, under the published session profile: `/tachi.threat-model`, then `/tachi.risk-score`, then `/tachi.compensating-controls --target r27-target`, each typed after the previous final report with no agent running.

## Result

**R-27: PASS.** All three commands completed under the profile with no permission prompt and no denial, and every write lies inside section 5.

| | `/tachi.threat-model` | `/tachi.risk-score` | `/tachi.compensating-controls` |
|---|---|---|---|
| **Completed** | yes, final report printed | yes, exit 5 (success with warnings) | yes, exit 5 (success with warnings) |
| **Script exits** | presence 0, populator 0, `architecture-source` 0 | presence 0, populator 0, plan 0, reconcile 0, render 5 | presence 0, plan 0, reconcile 0, render 5 |
| **Output tokens** (turns and every agent, thinking included) | **157,501** | **27,039** | **32,490** |
| of which thinking | 17,164 (11%) | 2,680 (10%) | 3,878 (12%) |
| main session (Opus 5.5) | 4,174 in 8 responses | 2,246 in 9 | 2,544 in 9 |
| agents (Sonnet 5.5) | 153,327 in 50 responses (9 agents) | 24,793 in 14 (3 agents) | 29,946 in 21 (4 agents) |
| **Wall time** (the session's timer) | **12 min 41 s** | **1 min 45 s** | **1 min 36 s** |
| **New paths** (files + directories) | 34 + 2 | 11 + 7 | 13 + 6 |
| **Prompts, denials, tool errors** | 0, 0, 1 | 0, 0, 0 | 0, 0, 0 |

- **For T072:** the run passed, so the runbook's "Last validated" line can state 2026-11-24, macOS 26.6.2 (arm64), Claude Code 2.1.331, auto mode, key-less, build `v4.48.4-162-g1e3614a` and the profile at SHA-256 `36df2a9a...`. The re-check covered startup, the rule list, the MCP and sandbox state, and one run of each of the three commands with a write listing.
- **Not covered:** the keyed pipeline, `/tachi.infographic`, `/tachi.security-report` (blocker F1 not re-tested), Linux and WSL2.
- Session totals: 23 min 11 s wall, 22 min 58 s API time; main 8,964 and agents 208,066 output tokens. `/usage` agreed (Opus 9.0k, Sonnet 208.1k, Haiku 2.5k, whose calls leave no response in the transcripts). Estimated cost $6.60; the weekly figure went from 46% to 47%.

## 1. The arrangement

1. **Adopter.** A clone of `<template w5b-r27>` (restore point `4533c72`, installed from `1e3614a` by `scripts/install.sh`, which reported `Version: v4.48.4-162-g1e3614a`, `Copied: 45 item(s)`), clean at the start; target tree `fb3cfb11...`, architecture description sha256 `2791c7bc...`. Nothing ran in the template.
2. **Launch (D-L8, the runbook's section 3 form).** `env -i` with `HOME`, `USER`, `LOGNAME`, `SHELL=/bin/bash`, `TERM`, `LANG`, `TMPDIR` (the launching shell's per-user directory, as section 3 sets it) and a `PATH` of the user's bin directory, `/opt/homebrew/bin` and the system directories; then `claude --settings <session profile> --effort medium`. No effort variable. A detached tmux session (200 x 50), no wrapper shell. **Deviation from T073 to T075:** bash, not zsh, so the zsh startup file's credential load doesn't apply.
3. **Profile.** `<session profile>`, outside the clone, read-only, 3,156 bytes, SHA-256 `36df2a9a98e301d783a06ff605d1be7f9548e10f805084b3fe225ff89eef9644` (section 11's R1 value), unchanged after the run.
4. **Versions.** Claude Code 2.1.331 (the header says 2.1.330), macOS 26.6.2 (arm64), `python3` 3.14.4 (the stages' first live run on 3.14: no incompatibility), auto permission mode, no `GEMINI_API_KEY`. The folder-trust dialog was answered "Yes, I trust this folder".
5. **User-scope additions** (section 3), applied by the maintainer for this session only: a `deniedMcpServers` entry for the one local MCP server, a `Read(~/.claude.json)` deny and its `sandbox.credentials.files` entry. No other settings file was edited, and no approval wrote a `settings.local.json`.

## 2. The effective configuration (section 3's checks)

| Check | What the session showed |
|---|---|
| `/status` | Setting sources: User settings, Command line arguments. Auto mode server Enabled. The Features line names the commands that the non-essential-traffic switch turns off |
| `/permissions` | Allow and Ask empty. Deny 19: the profile's 18 rules plus the user-scope `Read(~/.claude.json)`. No invalid-rule warning at startup |
| `/mcp` | The claude.ai connectors (one hidden) and the browser bridge connected. The denied local server did not appear |
| `/sandbox` | `Sandbox settings can't be changed here. Higher-priority settings override them.` |
| In force (indirect) | The profile sets `failIfUnavailable` and the session started; Claude Code's `.claude/.cc-writes/` marker, which section 5 ties to sandboxed commands, appeared |

## 3. What each command produced

| | Result |
|---|---|
| **Threat model** | 35 findings: 4 Critical, 24 High, 7 Medium, 0 Low. `threats.sarif` 35 results, 7 attack chains, 28 attack trees and a manifest, `threat-report.md`. `threats.md` carries one `**Architecture source**` line. Written by the orchestrator (`threats.md`, `threats.sarif`, `attack-chains.md`), the report agent (`threat-report.md`) and the attack-tree agent (the trees and manifest); the populator and `architecture-source` edited `threats.md` |
| **Scorer** | 35 of 35 rows in Sections 2, 3 and 4, 35 of 35 SARIF results, none duplicated, `.md` and SARIF agree; bands 0 Critical, 0 High, 34 Medium, 1 Low (highest composite 6.9). Both files written by the renderer; their hashes equal the stage record's |
| **Controls** | 35 of 35 in the Coverage Matrix and 35 SARIF results; 5 Control Found, 23 Partial, 7 No Control Found; inherent 194.6, residual 148.7 (23.6%), totals equal the row sums; 30 Section 4 blocks and none unjoined. The independent checks passed 37 of 37. Written by the renderer |

## 4. The write listing against section 5

A hash of every path except `.git/`, before (272 paths: 194 files, 78 directories) and after (348: 252, 96). **76 new, 0 changed, 0 deleted.** `git status` shows only the new run directory; the target's tree and the architecture file are unchanged.

| Section 5 row | New paths |
|---|---|
| `{out}/`, `architecture.md`, `threats.md`, `threats.sarif`, `attack-chains.md`, `threat-report.md` | 6 |
| `{out}/attack-trees/` (28 trees, the manifest, the directory) | 30 |
| `{out}/risk-scores.{md,sarif}`; `.tachi-build/` and `risk-score/` (plan directory, parts) | 2; 16 |
| `{out}/compensating-controls.{md,sarif}`; `.tachi-build/compensating-controls/` (plan directory, parts) | 2; 17 |
| Claude Code's own empty `.claude/.cc-writes/`: at the project root, and under `{out}` (the shell had changed into it) | 3 |

73 of 76 are in the table's rows; the 3 are the marker that section 5's last paragraph documents, not a tachi write. Nothing under `templates/`, no `__pycache__`, no path outside `{out}` except the marker, and no path under `{out}` without a row.

## 5. Model, effort, stops

Opus 5.5 for the main session and Sonnet 5.5 for all 85 agent responses, requested equal to served on all 111 responses, and medium effort and per-turn effort on every one. No response carries a fallback credit, and no stop was `max_tokens`. The largest response was 42,488 output tokens (the report agent's one write).

## 6. Timeline and completion rule

Offsets from each submit (mm:ss).
- **Threat model.** The orchestrator was dispatched at 0:18 and the main session ended its turn at 0:20. The six STRIDE agents started together at 1:00 and finished by 1:33. The report agent ran 5:19 to 12:09 and its attack-tree agent 5:35 to 8:15. The orchestrator finished at 12:21 and the main session resumed at 12:22, ran the populator and `architecture-source` (exit 0), then verified and reported at 12:40.
- **Scorer.** Plan at 0:18 (3 batches, one wave), dispatch at 0:31, agents 0:34 to 1:25, `reconcile` once at 1:31 (exit 0), render at 1:38 (exit 5), report at 1:44.
- **Controls.** Plan at 0:09 (4 batches), dispatch at 0:16, agents 0:21 to 1:09, `reconcile` once at 1:17 (exit 0), render at 1:27 (exit 5), report at 1:35.
- **Disposition (b):** no departure. Each `reconcile` came after its wave's last agent ended and each render after `reconcile` exited 0. Each stage ran `plan` once and `reconcile` once.

## 7. SC-3 structure, the two PR 1 stages (US-1a #6)

| Check | Scorer | Controls |
|---|---|---|
| Stage record | 35 units; 3 batches planned, dispatched and done (12, 12, 11 of 13); 0 overflow, 0 retries | 35 units; 4 batches planned, dispatched and done (9, 9, 9, 8 of 11); 0 overflow, 0 retries |
| Fixed prompt, named agent type | 3 of 3 `tachi-risk-scorer` | 4 of 4 `tachi-control-analyzer` |
| Hand-backs with code, program files written, stand-in agents | 0, 0, 0 | 0, 0, 0 |
| Agent writes | 3 `.json` part files, each at its batch input's `part_path` | 4 `.json` part files, each at its `part_path` |
| Main's Bash calls | 4, all named scripts or listings; **0 unnamed programs** | 4; **1 unnamed program**: a `grep` filter in Step 1's listing pipe, no interpreter code (a minor US-1a #6 departure) |
| Report against Step 6 | the renderer's 5 lines (1 warning) and the 5-line Next steps block, in one code fence; nothing added | the same, with a 7-line block; nothing added |

## Reference reads (structure only)

- **Scorer, 3 agents:** 3 of 3 read the batch input and `part-file-contract-shared.md`; 3 of 3 read all four binding references (`trust-zones`, `cvss-vectors`, `scoring-dimensions`, `reachability-analysis`), each before its first Write; 0 of 3 read any of `asset-modifiers`, `severity-bands`, `output-formatting`.
- **Controls, 4 agents:** 4 of 4 read the batch input, the contract and all three binding references (`control-categories`, `evidence-criteria`, `residual-risk`) before the first Write; 34 reads of the target's files, 0 failed.
- **User-level skills path:** 0 failed Reads, so no agent needed the adopter-copy fallback.

## 8. TW-L2, fallback and dispositions

- **TW-L2:** no failure, so no second attempt and no fix lane. **Fallback rate (ruling 2):** 0 of 140 scorer narrative fields (35 x 4) and 0 of 8 controls assessment fields; 0 truncations; no slot fell back.
- **Disposition (a):** not exercised (fixture only). **(c):** `plan` accepted the live `threats.md` (exit 0 in both stages), so no Section 7 cell refusal arose.

## 9. Observations (none changes the verdict)

1. **First-run input form.** `/tachi.threat-model`'s `threats.md` has no `delta_status` for its findings, so both stages parsed 35 of 35, flagged each with `input:delta_status:not-in-form`, warned `value-not-in-form` and exited 5. A first-run adopter sees this warning on every finding.
2. **Threat model.** Typed dispatch is PR 2's (N4). The orchestrator dispatched only typed agents (six STRIDE, the report agent, the attack-tree agent) and no stand-in. It ran one inline `python3 -c` call besides the populator, and some `grep` and `sed` calls; the report agent had one failed Read of a missing adopter file and then read the right one. The main session ran one heredoc `python3` and `date`, `mkdir`, `cp`, `cat`, `grep` and `git` calls, besides the named scripts. Section 11's re-check had the orchestrator analyse inline; here it dispatched. `threats.sarif` has `findingId/v1` only and no `primaryLocationLineHash` (35 of 35).
3. **Working directory.** After the threat model the session's directory sat in `{out}`. Every main Bash call began with its own `cd` to the project root, so the next commands resolved, and the marker landed under `{out}` too.
4. **Bands.** The scorer's bands (34 Medium, 1 Low) differ from the threat model's risk levels (4 Critical, 24 High): different scales, recorded for the follow-up list.
5. **Usage panel.** `/usage` couldn't refresh at the start (non-essential traffic is off) and showed the last-known 46%.
