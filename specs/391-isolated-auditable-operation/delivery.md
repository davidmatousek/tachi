# Delivery Document: Feature 391 — Isolated and Auditable Operation

**Delivery Date**: 2026-11-21
**Branch**: `391-isolated-auditable-operation` (Part A). Part B is on `391-isolated-auditable-operation-part-b`.
**PR**: #392 (Part A), squash-merged to `main` as `e83ca6b` at 2026-11-21T18:35:56Z. #396 (Part B), draft, now based on `main`: it closed when the Part A branch was deleted at the merge and was reopened and retargeted at this delivery; T047's merge of `origin/main` into part-b is pending.
**Release**: v4.48.3. The release-please PR #418 opened at the squash-merge. Part A ships alone as `fix(391)`, a patch release.
**Closes**: #391, closed at this delivery (the PM's recommendation; #399 carries B1 and #400 the Part B landing)
**Path**: split (TW-A2). #364 was still open when Part A became merge-ready.
**Part B**: B2 built, awaiting #364 (#396, based on `main` since this delivery; T047's merge phase done the same day: merge `644f12f`, Part B security scan `51eaa5c` PASSED, gated set 1124 passed in a scratch clone, `/aod.analyze` clean). Landing tracker: #400.
**B1**: honest-stopped (TW-B1). Follow-up: #399.

> Prepared at T045 (build session S2c, 2026-11-21) and completed by `/aod.deliver` the same day: every field that T045 left open for the delivery is filled. Structure only: no transcript text, session or tool-call ids, home or scratch paths, or key material.

---

## What Was Delivered (Part A)

- **A true statement of what leaves the machine.** On `main`, `.claude/rules/scope.md` said that architecture descriptions never leave the machine, and `docs/standards/CLAUDE_PERMISSIONS.md` described its baseline as having no network egress and a default-deny outbound rule. The D-3 sentence now stands in all six data-locality documents: the model provider receives the architecture description, the files tachi reads and the findings on every run, and Google's Gemini API receives derived threat-model content only when the key is set and `/tachi.infographic` runs. The README states the Gemini flow before the key step (US1; FR-001 to FR-004; SC-002).
- **An installed isolated-operation runbook**, `docs/guides/ISOLATED_OPERATION_TACHI.md`: the two hosts; one session profile for `claude --settings` (18 deny rules, a strict one-host allow-list, the image key masked and injected only toward the Gemini host, auto mode's built-in rules plus one `hard_deny` rule); probes; write locations; retention; reporting routes; a program mapping; and the live-validation record (US2; FR-005 to FR-010; SC-001). Validated live on macOS with Claude Code 2.1.330 in auto mode, key-less and keyed; the published 18-rule profile was re-checked key-less. Linux and WSL2 are not yet run live. On macOS, `/tachi.security-report` is outside the claim for runs with diagrams (F1), and §6 gives a by-hand build (not yet run live).
- **Write confinement.** A run writes only under `{out}` and `$TMPDIR`. The extractor owns the report's build directory, `{out}/.tachi-build/security-report/`, and `templates/tachi/` is never written. The agents' intermediate paths are pinned under `{out}/.tachi-build/`, and the installed scripts write no bytecode cache (US2; FR-007, FR-008; SC-005; ADR-049 D5 to D8). The precondition: `/tachi.security-report`'s output directory must lie under the working directory (exit 2 otherwise).
- **A CI-guarded privilege matrix.** §8 of `CLAUDE_PERMISSIONS.md`, checked by `scripts/check-agent-privileges.py` (C1 to C8, with a planted-mutation self-test) in `tachi-permissions-verify.yml`, and the SC-A4 assertion in the install-fidelity suite on every install path (US3; FR-011 to FR-014; SC-003, SC-004; ADR-049 D1 to D4).
- **Two pre-existing defects fixed**, both found in review: `/tachi.security-report` dispatched `senior-backend-engineer` (AD-13; ADR-049 D9), and `tachi-risk-scorer` ignored the output directory it was given (AR-2). See "Pre-existing defects found in review".
- **ADR-049**, with dated Notes on ADR-014 and ADR-019 (FR-015).

---

## Build Records

### Trip-wires and gates

| Trip-wire or gate | When | Outcome |
|---|---|---|
| TW-0 aggregate | `/aod.tasks` | Not fired: the team-lead's projection was 4.74 d against 5.0 d |
| TW-B0 Part B entry | `/aod.tasks` | Not fired: Part B 2.86 d against 3.0 d, so Part B proceeded |
| TW-A3 FR-11 bound | `/aod.tasks` | Bounded, not carved |
| TW-B1 attribution | T002 (W0′) and T051 (W2) | Passed at T002. **Fired at T051** on the denial clause; B1 honest-stopped (below) |
| TW-B2 cost | T050, start of S2 | Not fired (the G-B2 record below) |
| TW-B3 layout | During B1 | Not fired: parser rework of about 10 minutes, no layout change |
| TW-B4 scrub | T035 | Not reached: T035 honest-stopped with B1 |
| TW-A1 live budget | W2 | Not fired: 1 debug loop (F1), about 4 hours |
| TW-A2 merge gate | Part A merge-ready | Applies: #364 is open, so the split path |
| G0 | W0 | PASS |
| P0-B0 | before B1 code | APPROVED_WITH_CONCERNS |
| W1 carve check | W1 | Not triggered (T025 and T026 took about 75 minutes) |
| G1, the cut line | end of W1 | PASS |
| T040, the P0 architect checkpoint | end of W1 | APPROVED_WITH_CONCERNS |
| GL | before W2 | PASS, with Linux scoped out by the maintainer (D1) |
| G-B2 (T050) | start of S2 | TW-B2 not fired |
| G-B1R (T051) | first in W3 | TW-B1 fired |
| G3 | end of W3 | Closed: the full T043 re-run passed on both final tips, and CI was green on #392 at `6ade384` (11 of 11) and on #396 at `3cc8294` (8 of 8) |
| Step 5, final validation | W4 | APPROVED_WITH_CONCERNS (architect: 0 critical, 0 high). Its fix texts are applied ("Wording sweep (T046)") |
| Step 6, design quality | W4 | Skipped: no UI files changed |
| Step 7, security scan | W4 | PASSED: 9 code files and no blocking finding. 1 LOW, the build-mode symlink refusal (#416) (`security-scan.md`) |
| Step 8, Economy Gate | W4 | FINDINGS, 5 advisories (`economy-check.md`). At the maintainer's choice, EC-5 is fixed in `97208fe`, and EC-1 to EC-4 are filed as #417 |
| G4, the merge gate | end of W4 | T046 passed. The merge belongs to `/aod.deliver`; the maintainer confirmed it on 2026-11-21, after green CI |

### TW-B1 fired at T051

The record is `test-results/tw-b1-w2.md`. Its §2, verbatim (its line numbers are those of `tasks.md` and `agent-assignments.md` at T051):

**Verdict: TW-B1 FIRED (the denial clause). B1 honest-stops; B2 continues.**

TW-B1 as written (`tasks.md` line 223): "B1 stops if any dispatched tachi agent's turns cannot be attributed to its name from transcript structure, any subagent that ran yields an empty histogram, meta and line agent names disagree, or a planted denial kind goes undetected."

| Clause | Result | Why |
|---|---|---|
| Attribution | Pass | All 13 dispatched tachi agent instances (K1 8, K2 5, depths 1 to 3) are attributed to their names from transcript structure, with 0 `no-transcript` and 0 `dispatch-failed`. |
| Empty histogram | Pass | All 13 instances have a non-empty served-model histogram (3 to 20 turns each), with 0 synthetic turns. |
| Name agreement | Pass | The meta `agentType`, the line `attributionAgent` and the dispatched `subagent_type` agree for 13 of 13 instances, with 0 mismatched lines. |
| Planted denial kind undetected | **Fail** | Sandbox is undetected in K1 and SS (0 of 7 planted probes). Classifier is undetected in K1: its marker is counted only as the unrecognised label `automode-blocked`. Permission rule is detected for 2 of 5 planted refusals, because Read-tool refusals carry no `toolDenialKind`. |

The gate fails closed (`tasks.md` line 223; `agent-assignments.md` line 307), so B7's partial result (permission rule detected for 1 of its 2 refusals) counts as partial, not as a pass. The verdict does not depend on that reading: K1 and SS fail at kind level.

The W0' spike (`w0-spike.md`) passed the three attribution clauses. It ran without a sandbox and planted no denial, so this is the first application of the denial clause ("The denial criterion applies from W2", `tasks.md` line 223).

### B1: honest-stopped (TW-B1)

- **Built in W1, not shipped.** T031 to T034 built the archiver, `schemas/run-manifest.yaml`, two generations of synthetic fixtures and the test suite, with the T034 security review and the T040 fixes. T035 (the recorded fixture) is honest-stopped. T031 to T034 stay `[x]`.
- **How B1 left part-b.** Seven delete-and-edit commits, not `git revert` (the architect's ruling): `be2e890`, `dfcf93e`, `efaaf70`, `140d93d`, `f7f8ce4`, `40f0a58` and `bc943c6`. #396 now differs from Part A in 18 paths: the 17 B2 paths below and `CHANGELOG.md` (T048's Part B entry, `923c802`). The runbook and ADR-019 are byte-identical to Part A's.
- **Where the built work is.** Every B1 commit stays an ancestor of part-b's tip and of `refs/pull/396/head`.
  - `fe5125a` is the last commit with B1 intact: the archiver as reviewed and fixed (1,823 lines, SHA-256 `ae65e4dc957cc55b56d649f3b20883cb479bc9626b2c6daf246e704e619325a7`), the schema, the fixtures, the suite and the B1 doc text.
  - Code: `093be0a`, `f9b5c0a`, `5952539`, `9e17230` and `c46b6a8`.
  - Docs: `8009298`, `8da464a`, `79aefc5`, `7838f48` and `20b28fa` (the last two also carry B2 text).
  - To retrieve them: `git fetch origin pull/396/head`, then `git show fe5125a:<path>`.
- **The follow-up:** #399. It carries the observed denial layout, the label and placement gap, the validated-version gate that fails open, the `egress_observed` semantics, the `DeprecationWarning` on Python 3.13 and later, the acceptance for a re-run, and the T040 deferrals L-3 and M-1 with S2a's X-8 note.
- **SC-006 and SC-007: not met, because B1 stopped.** `test-results/security-b1.md` advised against recording some of their clauses as met until three findings were fixed; with B1 stopped, that advice no longer applies.

### Part B: B2 built, awaiting #364 (#396)

- **What #396 carries:** B2 only. The installed version marker (`templates/tachi/VERSION`, written by `install.sh`), `tachi_version` stamped into `threats.md` at Step 2.6 of `/tachi.threat-model` by `scripts/stamp-tachi-version.py`, and the additive schema reconciliation to 1.5, with their tests and docs. Its 17 B2 paths against Part A (`CHANGELOG.md` is the 18th, T048's Part B entry):

  ```
  .claude/commands/tachi.threat-model.md
  .claude/skills/tachi-orchestration/references/output-schemas.md
  .claude/skills/tachi-orchestration/references/sarif-specification.md
  .github/workflows/tachi-pytest.yml
  INSTALL_MANIFEST.md
  README.md
  docs/architecture/02_ADRs/ADR-049-privilege-contract-and-write-confinement.md
  docs/guides/DEVELOPER_GUIDE_TACHI.md
  docs/standards/CLAUDE_PERMISSIONS.md
  schemas/output.yaml
  scripts/generate-threats-sarif.py
  scripts/install.sh
  scripts/stamp-tachi-version.py
  templates/tachi/VERSION
  templates/tachi/output-schemas/threats.md
  tests/scripts/test_tachi_version_marker.py
  tests/scripts/test_threats_schema_contract.py
  ```

- **How it lands (T047, split path).** After Part A squash-merges: merge `origin/main` into part-b (conflicts expected on ADR-049, §8, the README, the developer guide, `INSTALL_MANIFEST.md` and the CHANGELOG); the B1-absence grep on `main...<part-b tip>` prints 0; retarget #396 to `main` (done at this delivery, after the branch deletion closed it); re-run the gated set; run T038b if #364 has merged; mark #396 ready only after #364. It ships as its own `feat(391)` release. This document then records "Part B: merged" with the PR number. Tracker: #400.
- **SC-008:** in #396, not in this release. Its live field check passed in W2 on the part-b build (`w2-live.md` §5.4, SC-B3).
- **The G-B2 record:**

  "TW-B2 not fired (T050, 2026-11-20, before session L). Remaining Part B work 0.66–0.83 d against 1.5. B1 0.64 d against 1.55. B2 0.49 d against 0.83. Conversion: 6.0 h of summed lane agent wall-clock per attention-day."

- **The TW-B2 monitoring log:**

  - Part B agent wall-clock in S2b was about 120 minutes: the T051 parse and record, the B1-stop ruling, half of each T043 run and of T044, and SBE-B2 and SBE-TB.
  - With S1 and S2a's 66.0, that is about 186 minutes, against the 9.0 h re-open line. No new Part B work of 0.5 d or more appeared, so the team-lead was not re-invoked.
  - The orchestrator ran the seven stop commits itself (the architect's verbatim edits; the T044 review checked them).

### Success criteria

| SC | Status at T045 |
|---|---|
| SC-001 (PRD SC-A1) | Recorded by clause, on macOS; SC-001 as a whole is not claimed. The probe table and the FR-010 probes passed, and auto mode worked with non-essential traffic off. The zero-unexpected-egress-denials clause is met with a recorded qualification (the PM's ruling, under "Live validation"), for the profile that ran. "A full run completes" rests on W3-1's macOS scoping: `/tachi.security-report` built no PDF in either measured run (F1). Both full runs, key-less and keyed, used the profile that ran (2,908 bytes, `43496fb7…`); the published 18-rule profile was re-checked key-less (R1 to R6, with one `/tachi.threat-model` run), so the keyed pipeline has not run on it. The header names macOS only and stamps the Claude Code version, permission mode and date; Linux and WSL2 did not run (D1) |
| SC-002 (PRD SC-A2) | Met (T041, `w3-sweeps.md` §1): the D-3 sentence stands verbatim at 8 places in the six documents, the 4 unqualified claims on `main` are gone, PRD-054 and PRD-060 are untouched, and ADR-014 changed only by its Note |
| SC-003 (PRD SC-A3) | The pull-request leg is shown (T030, throwaway PR #398: red on an added tool, green on the revert; the self-test red path runs on every run), and `test_agent_privilege_guard.py` covers the other synthetic cases. The `push:[main]` leg ran at the merge: run 44936411660, success ("SC-003's push leg" below). Met |
| SC-004 (PRD SC-A4) | Met: `test_installed_agent_tools_match_matrix` on the install-sh, manual-loop and manual-loop-zsh paths (T028). The zsh path skips on CI's Ubuntu runner and ran locally in T043 (#415, optional) |
| SC-005 (PRD SC-A5) | Met by `test_write_confinement.py` (T015, in the Typst-gated report-posture job), a custom report configuration included. Live, four of the five run commands wrote only under `{out}` (the W2 listings and the W3 re-check's R6); the report step's write set rests on the test (F1) |
| SC-006 (PRD SC-B1) | Not met: B1 honest-stopped (TW-B1) |
| SC-007 (PRD SC-B2) | Not met: B1 honest-stopped (TW-B1) |
| SC-008 (PRD SC-B3) | Part B, in #396 (above) |
| SC-009 (Wording Rules) | Pattern A 0 hits, and Pattern B 1 hit with its disposition, on the Surface (T041). T046 sweeps the release texts ("Wording sweep (T046)" below) |

### Live validation (W2) and the W3 re-check

- **TW-A1: not fired.** 1 debug loop (F1), about 4 hours of wall clock with gate GL included, against a budget of 3 loops or 1.0 d (`w2-live.md` header).
- **The AD-12 deviation, W2** (`w2-live.md` §1, verbatim):

  - At the maintainer's instruction, Claude (Opus 5.5, in the maintainer's VS Code session) drove each session.
  - Each session was a real interactive Claude Code TUI inside tmux, started from a clean environment like a fresh terminal window (the interactive login `PATH`). Claude typed the prompts and read the screen.
  - AD-12 calls for a maintainer-launched session. The maintainer authorised this run and stays accountable for the record. T045 carries the deviation into `delivery.md`.

- **The AD-12 deviation, W3 part** (verbatim):

  the re-check sessions were Claude-driven in tmux, as in W2.

  The architect accepted both as recorded at T044 (runbook §11, `w2-live.md` §1, `w3-recheck.md` "How it ran").
- **Claude Code 2.1.328 → 2.1.330.** Gate GL checked 2.1.328, and the W0′ spike ran 2.1.328. Session C, the one session without the profile, started on 2.1.328, and its auto-updater installed 2.1.330. Every later session, and the W3 re-check, ran 2.1.330; the profile's non-essential-traffic switch keeps auto-update off. GL-3 and GL-3b were re-run on 2.1.330 with the same result.
- **The user-scope additions.** The runbook §3 user-scope additions were applied for the W2 sessions and restored byte for byte afterwards. They were not applied for the W3 re-check.
- **K2's unplanted refusal** (the PM's ruling, `delivery.md` text, verbatim):

  > SC-001's denials clause, and not SC-001 as a whole, is met with a recorded qualification (PM ruling, 2026-11-20): in K2 the strict allowlist refused, before it ran, one Bash call by `tachi-threat-infographic` whose per-command allowed-domain field and command named only the Gemini host, a refusal the profile makes by design for every per-command host list (runbook §3) and that no probe planted. It blocked no host and no tachi flow, because the agent continued without the field to 6 request and response pairs, but it left no denial marker, and the W2 record reported no denial in K2 until T051's census found it (`test-results/tw-b1-w2.md` §7 (b)).

- **Scope.** The claim covers macOS only. The Linux and WSL2 validation is #406, and the macOS report path is #405.

### Transcript topology and observed layout

#### W0′ spike: Claude Code 2.1.328, no sandbox

From `test-results/w0-spike.md`, verbatim. The spike planted no denial.

**Dispatch topology**

| Depth | Agent | State | Served model |
|---|---|---|---|
| 1 | tachi-orchestrator | recorded | claude-sonnet-5-5 |
| 2 | tachi-spoofing, tachi-tampering, tachi-repudiation, tachi-info-disclosure, tachi-denial-of-service, tachi-privilege-escalation | recorded (6) | claude-sonnet-5-5 |
| 2 | tachi-threat-report | recorded | claude-sonnet-5-5 |
| 3 | tachi-attack-tree-delta | recorded | claude-sonnet-5-5 |
| 3 | general-purpose (built-in, not a tachi agent), 3 instances | recorded | claude-sonnet-5-5 |

- **Dispatch-failed:** none.
- **No-transcript:** none.
- **Not dispatched** (installed tachi agents; the input has no AI components and later pipeline commands were not run): tachi-agent-autonomy, tachi-control-analyzer, tachi-data-poisoning, tachi-human-trust-exploitation, tachi-misinformation, tachi-model-theft, tachi-output-integrity, tachi-prompt-injection, tachi-report-assembler, tachi-risk-scorer, tachi-threat-infographic, tachi-tool-abuse.

**Observed layout (Claude Code 2.1.328)**

- **Main entry types:** `user`, `assistant`, `attachment`, `system` (`local_command`, `turn_duration`), `mode`, `permission-mode`, `session-owner`, `atis-latch`, `api-request`, `api-request-blob`, `api-request-shape`, `queue-operation`, `last-prompt`, `tools-used`, `ai-title`, `file-history-snapshot`, `file-history-delta`.
- **Subagent entry types:** `user`, `assistant`, `attachment`, `api-request`, `api-request-blob`, `api-request-shape`.
- **Assistant top-level keys include:** `attributionAgent`, `attributionSkill`, `agentId`, `requestedModel`, `isSidechain`, `serverClassifierRequest` (a per-request id), `effort`, `perTurnEffort`, `version`.
- **Meta keys:** `agentType`, `description`, `finished`, `isBuiltIn`, `launchedWithDefaults`, `model`, `parentAgentId`, `pickedEffortModel`, `requestNonInteractive`, `requestShape`, `spawnDepth`, `toolUseId`.
- `attachment.identity.modelId` records the session's starting model. The dispatch `tool_result` carries `toolUseResult.resolvedModel`.

#### W2 sessions: Claude Code 2.1.330, under the profile

From `test-results/tw-b1-w2.md` §6, verbatim:

T045 copies this section into `delivery.md` (`tasks.md` line 173, "observed layout"; TW-B1, `tasks.md` line 223: "`delivery.md` records the observed layout"). Observed in all six archives.

| Structure | Where it sits | Values | Appears on |
|---|---|---|---|
| `toolDenialKind` | Top-level key of a `user` entry that holds exactly one tool_result. Never inside a content block or `toolUseResult` | `permission-rule`, `automode-blocked` | Bash results in the main transcript only: 3 objects in the six archives (K1 2, B7 1). Absent on every Read-tool refusal and every sandbox refusal |
| `permissionDecision` | Top-level key of a `user` entry | `decision`: accept or reject. `reasonType`: mode, classifier, rule, subcommandResults. `reasonCode`: `rule:flagSettings`, `classifier:auto-mode`, `unknown`. `ruleSource`: `flagSettings`. `source`: config, user_temporary. `grantScope`: once. `classifierCategory`: `sensitive_information_leakage` | Accepted and refused calls alike (K1 160 entries, K2 84), so a refusal is `decision` reject, not the presence of the key. 6 reject entries: Read / rule 3 (K1 2, B7 1), Bash / subcommandResults 2 (K1 1, B7 1), Bash / classifier 1 (K1) |
| `sandboxViolations` | Top-level key of a `user` entry; present on sandboxed Bash results | A list. Empty on every result except the two proxy refusals, where it holds one item with keys `host`, `kind` (`network`) and `port` | Non-empty on K1 P3 and SS P3 only |
| `toolResultRemedy` | Top-level key of a `user` entry | An object `{kind: sandbox_violation}` | The same two proxy refusals only |
| No structure | The result text of the tool_result block | Free text only | Sandbox refusals K1 P1, P2, P3b and M2, and SS P1. For P3b the entry also has no `permissionDecision`, `sandboxed` or `sandboxViolations` |

- `is_error` on the tool_result block is true on every planted refusal except M2 (false). The block's keys are `tool_use_id`, `type`, `content` and `is_error`; there is no `isRejection`-style key.
- Present but not denial markers: `sandboxed` (true on sandboxed Bash results), `permissionMode` (`auto` or `default`), `serverClassifierContext` and `serverClassifierRequest` (request-context and id fields on auto-mode evaluations).
- No key name containing `denial`, `denied`, `violation`, `blocked` or `reject` exists other than `toolDenialKind` and `sandboxViolations`.

### Pre-existing defects found in review

- **AD-13: `/tachi.security-report` dispatched `senior-backend-engineer`.** That is a development agent of this repository: adopters never install it, and it declares no `tools:`. Found in the plan review (PM R-2). Fixed in T022 (`c068ddc`): the command dispatches `tachi-report-assembler`, with the prompt and the frontmatter unchanged (ADR-049 D9). T040 confirmed that the assembler's declared tools cover its steps. In W2 the command dispatched `tachi-report-assembler` in both measured runs (`tw-b1-w2.md` §4).
- **AR-2: `tachi-risk-scorer` ignored the output directory.** It wrote `risk-scores.md` and `risk-scores.sarif` beside its input even when `/tachi.risk-score` passed another `--output-dir`, and the command's Affected Assets step rewrote the input `threats.md`. Found in the T004 write-set audit. Fixed in T013 (`179b5c2`). W2's `--output-dir` listing (WL-AR2) showed the fix live.
- **Carried, unchanged:** the Claude Code adapter's copies of three commands (`adapters/claude-code/commands/tachi.{threat-model,risk-score,infographic}.md`) still print the old `cp -r` repair hint (a comment on #369 records it).

### SC-003's push leg

`test-results/sc-a3-evidence.md`, verbatim:

- **The `push:[main]` lag.** The workflow's push leg (`push: branches: [main]`, the same `&verify_paths` list) cannot be shown before the feature merges, because the guard steps reach `main` only with #392. The first push to `main` after that merge is the first push-leg run of the guard. `/aod.deliver` records its run id here (`feasibility-check.md` (e): the `push:[main]` evidence arrives only at merge).

**Run id: 44936411660.** The `tachi permissions-verify` workflow, event `push`, branch `main`, head `e83ca6b` (the squash-merge of #392), started 2026-11-21T18:35:59Z, conclusion success: the guard printed PASS for C1 to C7, detected all five planted mutations in C8, and exited 0. The companion push-leg runs on the same head: `tachi install fidelity` 44936411674 (success), `tachi catalog-drift` 44936411675 (success), `release-please` 44936411638 (success, opened #418) and `tachi pytest` 44936411639 ("CI at merge" below).

### Conditional follow-ups in T045, resolved

| T045 item | Condition | Resolution | Evidence | Follow-up |
|---|---|---|---|---|
| A guard check that command bodies dispatch only `tachi-*` agents with a §8 row | none (ADR-049 D9) | File it. AR-5 extends it to the bodies of the two dispatcher agents | `w1-audit-rulings.md` §4, item 1 | #409 |
| The skills' `allowed-tools` guard | none (ADR-049 Known limitation 1) | File it, with the item above: the same guard | ADR-049 Known limitation 1 | #409 |
| The attack-tree skip path | AD-9's fix failed | **Not evaluated on Linux**: AD-9's recipe is the Linux and WSL2 one, and Linux did not run (D1). **Its macOS analogue occurred**: Chromium cannot start inside the macOS sandbox, the `--no-sandbox` recipe does not change that, and no skip path exists, because ADR-022 makes `mmdc` a hard prerequisite when diagrams exist. W3-1 scoped the macOS claim instead | `w2-live.md` F1; runbook §6; the architect's W3-1 | #405 (a macOS report path, a skip path among its options); #406 (the Linux check) |
| The auto-mode recipe marked "not yet run live" | the auto-mode fallback fired | **Not fired** | GL-2: auto mode was available. Every measured W2 session ran in auto mode with the auto-mode server enabled and non-essential traffic off (`w2-live.md` §5.5). GL-3 and GL-3b: the `--settings` file applies `autoMode`, so the inline fallback was not needed. The W3 re-check also ran in auto mode | none |
| The `report-config.typ` overwrite, as a defect | the relocation slipped | **Not fired**: the relocation landed (T012, `32623a5`; AR-1) | `test_write_confinement.py` checks that a custom `report-config.typ` reaches the PDF and that the installed default stays byte-identical, in the Typst-gated report-posture job (T043 re-run: 75 passed). Live, the custom file was placed but not exercised (F1) | none. The pre-existing overwrite is a CHANGELOG "Fixed" line |
| The TW-A1 follow-up | TW-A1 fired | **Not fired** | 1 debug loop (F1), about 4 hours with gate GL, against 3 loops or 1.0 d (`w2-live.md` header) | none |
| AD-13's fallback follow-up | the dispatch had to stay | **Not fired**: the dispatch changed (T022, `c068ddc`) | T040 confirmed the tool coverage; in W2 the command dispatched `tachi-report-assembler` in both measured runs, recorded with agreeing names (`tw-b1-w2.md` §4) | none |
| The SARIF twin "1.8" | none (PM L-5) | File it, with the "1.7" twin (T040, P0 row 7) | `t038a-measurement.md`; `p0-architect-checkpoint.md` | #413 |
| The Part B landing tracker | the split path | File it | TW-A2; #364 open | #400 |

### Technical debt register (CF-P8)

The plan's register (`plan.md`, "Technical debt register"), verbatim:

> Skills' `allowed-tools`/`model` are an unguarded privilege surface (follow-up); a pre-391 installer downgrade cannot reset the marker; the pinned matrix link lags for post-release `main` installs and does not exist before the first release carrying §8; command frontmatter is declared-only until `allowed-tools`/`model` are set; `denial_detection` is `validated` only for Claude Code versions with a passing fixture.

| Item | Where it is recorded | Status |
|---|---|---|
| Skills' `allowed-tools` and `model` are an unguarded privilege surface | ADR-049 Known limitation 1 | Open: #409 |
| A pre-391 installer downgrade cannot reset the marker | ADR-049 on part-b, a Part B Known limitation | Ships with #396 |
| The pinned matrix link lags post-release `main` installs, and does not exist before the first release that carries §8 | ADR-049 Known limitation 2; runbook §10 | Open by design. This release is the first that carries §8, so the pinned link resolves from it on |
| Command frontmatter is declared-only until `allowed-tools` or `model` is set | ADR-049 Known limitation 3 | Open by design |
| `denial_detection` is `validated` only for Claude Code versions with a passing fixture | B1, not shipped | Moves to #399 |
| Added at the tasks review (L-6): `tests/scripts/test_coverage_attestation.py` is ungated | ADR-049 Known limitation 4 | Open. Run by hand in a scratch clone: 16 passed in the T043 re-run |
| The adapter agent copies carry no `tools:` or `model:` | ADR-049 Known limitation 5 | Open: #369 (a comment records it) |

### Maintainer action: C-9

Correcting published copies of the old data-locality claim outside this repository is a **maintainer action**, out of the feature's scope (PRD C-9; `spec.md`, Out of Scope). The known copy is the coverage article drafted at `specs/296-50-50-owasp-coverage-distribution-launch/notes/cybersec-article-draft.md:131`, which says "your architecture description stays on your machine". The published copies take the D-3 sentence. The in-repository draft is a record of that feature and stays unchanged.

**Status at delivery (2026-11-21): open.** A maintainer action, not performed by `/aod.deliver`; the known published copy carries the old sentence until the maintainer corrects it.

### Records outside Feature 391

- **A stale checksum.** `specs/029-agent-refactoring-right/baseline-checksums.txt:23` holds Feature 029's SHA-256 of `schemas/output.yaml` (`3686e693…`). The file has changed since, and Part B changes it again. Nothing in the tests, scripts, workflows or the Makefile reads the record, so it was left unchanged.

### Orchestrator deviations

**S2c** (W4):
- **T046's steps were run by the orchestrator,** not dispatched to DEVOPS-E: the Wording sweep, `/aod.analyze`, the three diff checks and the `gh` steps. The architect's Step 5 review covered the same ground independently.
- **The orchestrator applied the architect's Step 5 fix texts verbatim** (F-1 to F-5, F-8, F-10). It also narrowed one phrase of T048's Part B entry: the output template declares schema 1.5, and the stamp writes no other key.
- **The orchestrator filed the follow-ups** from the PM's drafts, with one held for maintainer triage (filed later as #416).
- **EC-5's last two rows** (an unknown flag on its own; a target directory inside the build directory) were added by the orchestrator from SBE-TA's checked variant.

**S2b** (verbatim):

- the B1-stop edits on part-b (§3.1 to §3.8 of the ruling) were applied by the orchestrator from the architect's verbatim texts, with every post-check, rather than dispatched to the owners;
- one D7 sentence of the architect's was corrected from the evidence (`architect-t044-391.md` §4 confirms it).

**S1 and S2a** (from the H1 and H1b handoffs):
- **Per-dispatch worktrees.** Agents that edited tracked files worked in their own worktree at the branch tip, and the orchestrator committed there and cherry-picked onto the branch, because the pre-commit hook stashes unstaged files during a commit.
- **Combined writers.** T010 with T023 (one writer for `CLAUDE_PERMISSIONS.md`); the AR-14 follow-on; F-1 with F-2; X-2; X-7 with X-9; X-8.
- **T006's docs research** was done by DEVOPS-R, with citations.
- **T048's README and developer-guide marker lines** went in one commit, because the manual-install-loop test is red between the two files.
- **`py39-floor` is a separate job pinned to `ubuntu-24.04`** (part-b), because `actions/setup-python` has no Python 3.9 build for `ubuntu-latest`. It expires when `ubuntu-24.04` is retired.
- **The orchestrator wrote three small pieces itself:** X-3's four one-line doc edits, T030's git and `gh` steps, and one schema sentence in the X-8 commit.
- **T030's throwaway PR targeted `main`**, not the Part A branch, so that the path-filtered workflows ran for the green leg.

---

## How to See & Test

> Run the tests in a **scratch clone** (`git clone --no-hardlinks . "$SCRATCH/tachi"`), never in the main working tree: the report tests and the extractors render into `examples/` (#365).

1. **What leaves the machine.** Read README Quick Start step 3: the D-3 sentence comes before the key setup. The same sentence is in `scope.md`, `SECURITY.md`, the developer guide, §8.1 of `CLAUDE_PERMISSIONS.md` and runbook §1.
2. **The runbook installs.** In a scratch project, run `~/Projects/tachi/scripts/install.sh` and confirm `docs/guides/ISOLATED_OPERATION_TACHI.md` exists. Automated: `python3 -m pytest tests/scripts/test_install_manifest_completeness.py -v`.
3. **The session profile.** `python3 -m pytest tests/scripts/test_isolated_profile_contract.py -v` (the closed key set, the invariants, the named negatives and the 18 deny rules).
4. **The privilege guard.** `python3 scripts/check-agent-privileges.py --self-test` exits 0, and `python3 -m pytest tests/scripts/test_agent_privilege_guard.py -v` runs one red case per check.
5. **Write confinement.** `TACHI_REQUIRE_TYPST=1 python3 -m pytest tests/scripts/test_write_confinement.py -v` (it needs Typst).
6. **Live** (`[MANUAL-ONLY]`). In a scratch adopter project, launch with the runbook's profile and run the §4 probes, then a key-less `/tachi.threat-model`. The records are `test-results/w2-live.md` and `test-results/w3-recheck.md`, summarized in runbook §11.
7. **CI.** On `main`: `tachi permissions-verify` (with the guard and its self-test), `tachi install fidelity` (manifest-completeness, extraction-fidelity, report-posture) and both `tachi pytest` legs are green.

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | The team-lead's re-cost (v1.1): effort 7.7 d; duration floor 2.9, central 4.7 and ceiling 7.5 d; Part A 4.87 d and Part B 2.86 d |
| Actual Duration | 5 calendar days: branch created 2026-11-16 (define, spec, plan and tasks that evening), squash-merged 2026-11-21, across build sessions S1, S2a, S2b and S2c and the W2 live-validation day |
| Variance | On target: 5 d against the 4.7 d central (+0.3 d), inside the 2.9 to 7.5 d band. What shipped is Part A (planned at 4.87 d); Part B's B2 is built and awaits #364, and B1 was honest-stopped at TW-B1 |

---

## Surprise Log

Captured at T045 and finalized at `/aod.deliver` (2026-11-21).

- **TW-B1 fired on the denial clause.** On Claude Code 2.1.330, 5 of the 7 planted sandbox refusals carry no structural marker, and the markers that exist use labels the archiver did not know. The W0′ spike could not show this: it ran without a sandbox and planted no denial.
- **Chromium cannot start inside Claude Code's macOS sandbox** (F1), so the macOS claim excludes the report step for runs with diagrams.
- **The Agent tool offers an undocumented `remote` isolation value** on 2.1.330 (W3-3a), and eight built-in tools reach past the sandbox (AR-21). The profile went from 8 to 18 deny rules, and the re-check restarted.
- **Deleting the Part A branch at the merge closed the stacked Part B PR.** `gh pr merge --squash --delete-branch` closed #396 instead of retargeting it, and GitHub refuses to change the base of a closed PR or to reopen one whose base is gone. The base ref was restored at its last tip, #396 was reopened and retargeted to `main`, and the ref was deleted again (KB Entry 25, "How to apply").

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| Process improvement | Spike an environment's refusal signals, not only its success path. The W0′ spike validated transcript attribution without a sandbox and with no planted denial, so the denial-marker layout stayed unknown until W2, after B1 was built; TW-B1 then fired and B1 was honest-stopped (#399). A parser of another tool's signals is validated only against that tool's real failure modes, planted on purpose, before the build wave that depends on it. | Entry 25 in `docs/INSTITUTIONAL_KNOWLEDGE.md` |

---

## Feedback Loop

**New Ideas**: 17 follow-ups filed at T045 (S2c, 2026-11-21), #399 to #415, all at `stage:discover`. The PM drafted them from the build's review record, and the orchestrator filed them. Each title was dry-run against the open issues just before filing, and none matched. Two more followed in S2c: #416, the build-mode symlink refusal, after the maintainer chose the public route, and #417, the Economy Gate's test-economy advisories EC-1 to EC-4.

| Issue | Title | Label |
|---|---|---|
| #399 | Run archive and provenance manifest: denial detection on Claude Code 2.1.330 transcripts (F-391 B1 follow-up) | `enhancement` |
| #400 | F-391 Part B landing: ship #396 (B2) after #364 merges | `enhancement` |
| #401 | enhancement: check the Gemini infographic request against its documented field list before sending | `enhancement` |
| #402 | defect(infographics): executive-architecture callouts send mitigation text when a finding's threat text is empty | `type:bug` |
| #403 | defect(infographics): several infographic placeholders have no defined source, and the risk funnel sends component names it does not draw | `type:bug` |
| #404 | defect(infographics): the infographic agent departs from its pinned recipe (own helper scripts, simplified specs, every MAESTRO layer rated High, a per-command allowed-domain field) | `type:bug` |
| #405 | enhancement: a /tachi.security-report path for runs with diagrams under the isolated session profile on macOS | `enhancement` |
| #406 | enhancement: validate the isolated-operation runbook live on Linux and WSL2 | `enhancement` |
| #407 | enhancement: evaluate claude --restricted as an isolated launch form for tachi | `enhancement` |
| #408 | enhancement: bound the subagent types tachi-orchestrator and tachi-threat-report can start | `enhancement` |
| #409 | enhancement: extend the privilege guard to dispatch targets in command and dispatcher bodies and to skill frontmatter | `enhancement` |
| #410 | defect(extractors): a bad TACHI_MMDC_PUPPETEER_CONFIG ends extract-report-data.py with a traceback and exit 1, and is checked only when a diagram renders | `type:bug` |
| #416 | enhancement: extract-report-data.py build mode refuses a symlinked report-config.typ and symlinks under the output directory | `enhancement` |
| #417 | enhancement: trim F-391's test modules: reuse the guard's checks, one install harness, pin the §8 anchor, one script loader | `enhancement` |
| #411 | enhancement: run the privilege guard and the installed-script test modules under Python 3.9 in CI | `enhancement` |
| #412 | defect(sarif): informationUri is the placeholder github.com/owner/tachi in the SARIF templates, the risk-score SARIF generator and the risk-scorer instructions | `type:bug` |
| #413 | defect(examples): two tracked threats.sarif twins carry a semanticVersion that disagrees with their input's schema_version | `type:bug` |
| #414 | defect(risk-scorer): a fresh re-run of the same input moves findings across a severity band, and an entry-point component scores at the reachability floor | `type:bug` |
| #415 | enhancement: run the zsh manual-install-loop cases in CI (the manifest-completeness runner has no zsh) | `enhancement` |

The build-mode symlink refusal (CR-10, the code half of T042's W3-H1) was held at T045 for the maintainer's choice of route. On 2026-11-21 the maintainer chose a public issue, #416.

At the retrospective (2026-11-21): no new ideas beyond these. The one deliver-stage finding, the stacked-PR closure in the Surprise Log, is recorded as a mechanic in KB Entry 25 and not filed here, because it belongs to the AOD-Kit deliver flow rather than to tachi.

**Comments on open issues** instead of new ones:
- #365 (required): the maestro-reference offset (byte 828878 to byte 52) and the W0 census of 35 out-of-gate failures and errors.
- #380 (required): the W2 run's "Unknown Project" titles, with a suggested acceptance case.
- #369 (recommended): the adapter command copies' old `cp -r` repair hint, and the agent copies without `tools:` or `model:` (ADR-049 Known limitation 5 points there).
- #397 (optional): cross-references: N4's report dispatch is fixed in Part A; #408, #409 and #399.
- #374 (optional): the W0′ spike's five `max_tokens` stops on the smallest example input (for K5).

**Labeling**: these are build follow-ups, so they carry `type:bug` or `enhancement`, as F-373's #377 to #386 do.

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | specs/391-isolated-auditable-operation/spec.md |
| Implementation Plan | specs/391-isolated-auditable-operation/plan.md |
| Task Breakdown | specs/391-isolated-auditable-operation/tasks.md |
| Agent assignments | specs/391-isolated-auditable-operation/agent-assignments.md |
| PRD | docs/product/02_PRD/391-isolated-auditable-operation-2026-11-16.md |
| Contracts | specs/391-isolated-auditable-operation/contracts/{audit-write-set,cli-contracts,matrix-section,run-manifest,runbook-outline,session-profile,version-marker}.md |
| Records | specs/391-isolated-auditable-operation/test-results/ (W0 pre-state and spike, audit rulings, the W2 live record, TW-B1, the W3 re-check, sweeps, security reviews, the gated suites, the code review and checkpoints) |
| Runbook | docs/guides/ISOLATED_OPERATION_TACHI.md |
| ADR | docs/architecture/02_ADRs/ADR-049-privilege-contract-and-write-confinement.md |
| Release notes | specs/391-isolated-auditable-operation/release-notes.md |

---

## Test Evidence

### Test Scenarios (Living Documentation)

#### Acceptance Criteria Coverage

| AC ID | Given/When/Then | Scenario(s) | Status |
|-------|-----------------|-------------|--------|
| — | (No scenarios declared — zero ACs in spec.md) | — | — |

The row above is the template's empty state, not a statement about `spec.md`, which carries US1 to US5 with Given/When/Then criteria. The E2E gate exited at Step 9a (the active pack's `STACK.md` has no test-contract block; lint exit 5), so the AC-to-scenario map of Step 9a.5 was not computed. The criteria were checked by the W1 to W4 gated runs and the W2 live record instead (Build-Wave Test Results and Manual Validation below).

### Execution Evidence

#### E2E Validation Gate

| Field | Value |
|-------|-------|
| Status | error |
| Gate Mode | hard |
| Gate Result | skip |
| Tests Passed | N/A |
| Tests Failed | N/A |
| Tests Skipped | N/A |
| Duration | N/A |

**Failure Details**: N/A. Step 9a's contract lint exited 5 on the active pack: `[aod-stack-contract] stacks/knowledge-system/STACK.md:0: ERROR: no aod-test-contract block found (expected sentinel-bracketed YAML in Section 7)`. No tester agent ran and no scenarios were generated. The error does not block the close (ADR-006: the hard block is reserved for real test failures). The feature's test evidence is the Build-Wave table below and the CI runs at merge.

#### Command

```bash
/aod.deliver 391
```

#### Artifacts

The archived artifacts are the per-wave `results.json` files and the W0 to W4 records already under `specs/391-isolated-auditable-operation/test-results/`. Nothing was found to archive at the project root: `.aod/test-results/` holds one empty `wave-01/` directory from an earlier feature, and `test-results/` and `coverage/` do not exist.

#### Build-Wave Test Results

Every gated run used scratch clones of the committed tip (the #365 rule).

| Run | Tip | Result |
|-----|-----|--------|
| W0 pre-state (T003) | `46aec8d` | Census: 1,229 passed, 27 failed, 8 errors, 5 skipped, 1 xfailed. All 35 failures and errors are outside every gate and predate 391. Byte-identity: #365's 6 failures |
| W1 gate G1 (`wave-02/results.json`) | Part A `8273669`; part-b `7e64fd7` | Part A: run list 592 passed, manifest-completeness 17, extraction-fidelity 255, report-posture with write confinement 63, coverage attestation 16, guard self-test pass. part-b, with B1 still on it: run list 1,203 passed, `py39-floor` 942 on Python 3.9.6 |
| W3, T043 first run | Part A `b71a0d7`; part-b `f34e0ed` | PASS: 984 and 1,113 passed; 0 regressions; #365's six only. X-5: 702 passed on Python 3.9.6 |
| W4, EC-5 (`wave-04/results.json`) | Part A `97208fe` | PASS: `test_write_confinement.py` 78 passed with `TACHI_REQUIRE_TYPST=1` (69 existing, 9 new refusal cases); the guard's `--self-test` passes |
| W3, T043 re-run (G3) | Part A `6ade384`; part-b `3cc8294` | PASS: Part A 988 passed, 6 failed (#365's six), 3 skipped, 1 xfailed; part-b 1,121 passed with the same failures. X-5: 706 passed and `py39-floor` 132 on Python 3.9.6. The zsh cases passed |

**CI at the final W3 tips:** #392 at `6ade384`, 11 of 11 green; #396 at `3cc8294`, 8 of 8 green. **CI at merge:** on `e83ca6b` (the push to `main`), all five path-triggered workflows green: `tachi permissions-verify` 44936411660, `tachi catalog-drift` 44936411675, `tachi install fidelity` 44936411674, `release-please` 44936411638 (opened #418) and `tachi pytest` 44936411639 (ubuntu-latest finished 18:47Z, macos-latest 19:08Z). The closure push `7ae5e35` re-ran `tachi pytest` (44939997013, in progress at this record) and `release-please` (44939997020, success). The regenerated fixture was checked first in a scratch clone of `7ae5e35`: `test_init_sh_substitution.py` and `test_isolated_profile_contract.py`, 203 passed, 1 xpassed (`test_personalized_tree_bytes_match_baseline`, the XPASS that #345 waits for).

### Manual Validation

- **T020, W2 live validation** (`[MANUAL]`, maintainer-directed; the AD-12 deviation above): PASS with F1 as a documented limitation (`test-results/w2-live.md`).
- **The W3 re-check of the published profile**: PASS, R1 to R6 with R4a (`test-results/w3-recheck.md`).

---

## Wording sweep (T046)

Run on 2026-11-21 (S2c). Steps (1) to (4) ran at Part A `107c0a4`. The sweep was re-run on the texts as this records commit leaves them, after the architect's final-validation edits. The orchestrator ran DEVOPS-E's steps (see "Orchestrator deviations").

- **Wording Rules, step (0).** Pattern A: 0 hits. Pattern B: 0 hits.
  - Surface: the Part A CHANGELOG entry (`### Feature 391 — … Part A … — fix(391)`), `release-notes.md`, and the titles and bodies of #392 and #396.
  - Also swept, for T047: the Part B CHANGELOG entry on part-b (`923c802`).
  - The only matching terms are names the spec allows: "Cyber Verification Program" (Part A entry, 2) and `tachi-permissions-verify` (Part A entry 1, #392 body 1).
- **`/aod.analyze`, step (1):** clean. 0 critical, 0 high, 0 medium and 5 low, all records-level.
- **AD-14, step (2):** `git diff --stat main...391-isolated-auditable-operation` lists 88 paths and none of AD-14's Part B-only paths. Part A's `tachi-pytest.yml` carries no Part B entry.
- **Step (3), the hunk grep:** 0 hits.
- **Step (4):** the diff holds no tracked example image, PDF or SARIF baseline, and no `examples/` path.
- **Step (5):** #392 is retitled `fix(391): isolated and auditable operation (Part A)`, and the bodies of #392 and #396 come from the T045 drafts. #392 is marked ready when this commit is pushed. The squash-merge and the release-please check belong to `/aod.deliver`.
- **After the architect's final validation** (Step 5 of `/aod.build`; local, `.aod/results/architect-final-391.md`): APPROVED_WITH_CONCERNS, with 0 critical and 0 high.
  - Applied: F-1 to F-5, F-8, F-10, and two of F-11's precision notes (the `/tachi.architecture` exception and the zsh install path).
  - F-7's note is carried to `/aod.deliver` below.
  - F-9 is an acceptance item on #401.
  - Both sweeps were re-run on the edited texts: Pattern A 0, Pattern B 0.

---

## Documentation Updates

Three documentation agents ran in parallel at `/aod.deliver` (2026-11-21), each against its section of `docs/DOCS_TO_UPDATE_AFTER_NEW_FEATURE.md`; the orchestrator made the edits it owns itself.

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 3: `docs/product/02_PRD/INDEX.md` (row 391 "Delivered (Part A)", header rewritten); `docs/product/02_PRD/391-isolated-auditable-operation-2026-11-16.md` (frontmatter status Delivered with the Part A qualifier, PR, merge commit, release); `docs/product/05_User_Stories/README.md` (Feature 391 block: US1 to US3 delivered, US4 not delivered, US5 Part B pending) | done |
| Architecture | architect | 3: `docs/architecture/README.md` (ADR-049 closure line); `docs/architecture/00_Tech_Stack/README.md` (the permissions-verify row now lists the six steps, the guard's `--self-test` last; isolated-operation suites paragraph); `docs/architecture/03_patterns/README.md` (new pattern "Self-Testing Drift Guard", linked to ADR-049 D1). ADR-049 left unchanged because #396 edits its D9 and Known limitation 5 lines | done |
| DevOps | devops | 2: `docs/devops/CI_CD_GUIDE.md`; `docs/devops/environment-variables.md` (adds `TACHI_MMDC_PUPPETEER_CONFIG`). `docs/devops/README.md`, `01_Local`, `02_Staging` and `03_Production` checked, nothing stale | done |
| Orchestrator | /aod.deliver | `docs/architecture/01_system_design/README.md` (the F-7 status note) with `tests/fixtures/init-baseline-tree/` regenerated in the same commit (FR-021; 62 substitution targets: 17 files changed, 8 added, 0 removed; #345 told); `docs/INSTITUTIONAL_KNOWLEDGE.md` Entry 25; `docs/product/_backlog/BACKLOG.md` regenerated; `test-results/sc-a3-evidence.md` (the push-leg record); this document | done |

Wording sweep over every added line of the three agents' diffs: Pattern A 0 hits, Pattern B 0 hits.

---

## Reminder for /aod.deliver

All items below were done at the delivery on 2026-11-21: the note appended and the fixture regenerated in `7ae5e35`, with #345 told; run 44936411660 recorded; #392 squash-merged and #418 opened; #396 reopened and retargeted to `main`; C-9 left with the maintainer; the open fields filled.

- **The system-design README.** Its appended note records the B1 stop and B2's separate landing, and `tests/fixtures/init-baseline-tree/` is regenerated in the same commit (FR-021). #345 tracks that fixture's pre-existing drift, so record the result there.
  - Maintainer decision (2026-11-21): regenerate per the plan. The regeneration absorbs #345's drift there and turns that test's `xfail(strict=False)` into an XPASS. Comment on #345 that its marker can be removed there.
  - The note's text, from the architect's final validation (F-7):

    > **Status at Part A's merge (<date>).** Part A shipped alone as `fix(391)` (TW-A2). B1, the archiver and its run manifest, was honest-stopped at TW-B1 and does not ship (follow-up #399). B2, the version marker, the `tachi_version` stamp and the schema 1.5 reconciliation, ships separately through #396 after #364. Until #396 merges, the B2 rows and the `install.sh` → `VERSION` → stamp edges above describe the plan, not `main`; the archiver row, its edge and the Tech Stack's `subprocess` note describe work that did not ship.
- **SC-003's push leg.** Record the run id of the guard's first `push:[main]` run in `test-results/sc-a3-evidence.md` and above.
- **The merge.** Confirm with the maintainer before any merge. Squash-merge #392 under its `fix(391): …` title, then confirm that a release-please PR opened, and push a `fix(391)` marker commit if it did not.
- **T047** follows the squash-merge (split path).
- **C-9**, the maintainer action above.
- **The open fields** in this document.

---

## Cleanup

- [x] The Part A branch was deleted at the merge (restored for a minute to reopen #396, then deleted again); the part-b branch stays until #396 lands.
- [ ] The local branch `391-sc-a3-evidence` (`git branch -D` is denied in this environment; the maintainer removes it).
- [ ] `.aod/revision-context.md`, a stale untracked leftover from the tasks loop, deliberately not committed (the maintainer removes it).
- [x] Tasks: 50 of 52 done; T047 (after this merge) and T038b (after #364) are conditional.
- [x] Committed and pushed: `7ae5e35` (the closure docs, KB Entry 25, the regenerated fixture) and the CI-record commit that carries this line, both direct to `main` under the deliver-stage exception.
- [x] GitHub Issue #391 closed with `stage:done` (2026-11-21T19:16Z); the board row moved to Done.
- [x] Story export skipped: the issue body has no `## Stories` section. The PM added the Feature 391 block to `docs/product/05_User_Stories/README.md` by hand.
- [x] Delivery lock released as the last act of the run.

**Feature 391 (Part A) is now officially CLOSED. Part B lands through #396 (tracker #400); B1 through #399.**
