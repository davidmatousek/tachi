# TW-B1 re-confirmation on the W2 sessions (T051, gate G-B1R)

**Scope.** Structure only: counts, key names, enum labels and model ids. No session ids, tool-call ids, transcript text, command text, home or scratch paths, or key material. The archives behind the figures are private and are never committed. Plan files are cited by line (`tasks.md` and `agent-assignments.md` under `specs/391-isolated-auditable-operation/`); `w0-spike.md` and `w2-live.md` sit beside this record.

## 1. Task, inputs and method

| Item | Value |
|---|---|
| Task and gate | T051, gate G-B1R: TW-B1 re-confirmation on the W2 sessions (`tasks.md` line 179; `agent-assignments.md` §4, line 307). The tester records; SBE-B1 ran the parse |
| Date | 2026-11-20 |
| Inputs | The six W2 archives K1a, K1, B7, MM, K2 and SS (labels as in `w2-live.md` §4), archived in session L from installs of part-b `fe5125a` (`v4.48.2-103-gfe5125a`). Private, never committed. Session C ran without the profile and is not archived, by design |
| Labels | Assigned from start order and structural signatures (permission mode, tool-call mix, dispatch chain). The shell in K1a and K1, B7's extra Read deny, SS's `--setting-sources` flag and K2's key are not visible in structure; for those the label rests on launch order plus the signatures above |
| Method | The archiver as built at part-b `fe5125a`, re-run on each session to a fresh private destination with `--json`, and compared field by field with the manifest each archive already held. Plus an independent structure-only census of denial markers at any JSON depth, over every transcript line (main and subagent) |
| Archiver | `scripts/archive-run-transcripts.py` at `fe5125a`, not edited: 1,823 lines, 83,910 bytes, `manifest_version` 1, SHA-256 `ae65e4dc957cc55b56d649f3b20883cb479bc9626b2c6daf246e704e619325a7` |
| Python | 3.12.11, no `DeprecationWarning` (the 3.14 warning noted in `w2-live.md` F6 was not re-tested) |
| Claude Code | 2.1.330 in every session and every manifest |
| Re-run environment | Scrubbed to `HOME`, `PATH`, `LANG` and `TMPDIR`; `GEMINI_API_KEY` not set. Each re-run's final scan compared 0 environment values and ran the 20 key-format rules, so this record does not repeat the session-L key scan of K2 (`w2-live.md` §5.8). The parse ran no pytest or extractor and wrote in no git work tree |
| Source of the figures | The SBE-B1 parse, `.aod/results/sbe-b1-t051-391.md` (local, untracked, structure-only) |
| Result | **TW-B1 FIRED (the denial clause). B1 honest-stops; B2 continues.** See section 2 |

## 2. Verdict

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

## 3. Re-run against the session-L manifests

Each session was re-run with the archiver as built. 6 of 6 exit 0. Each manifest was compared with the one its archive already held: 19 fields, every field except `archived_at`.

| Session | Mode | Exit | Files | `denials_seen` | `egress_denied` rows | Dispatches recorded | Fields that differ | After a re-run with `--output-dir` |
|---|---|---|---|---|---|---|---|---|
| K1a | auto | 0 | 1 | 0 | 0 | 0 | none | n/a |
| K1 | auto | 0 | 18 | 2 | 1 (`permission-rule`) | 8 | `artifacts`, `artifacts_reason` | none |
| B7 | auto | 0 | 1 | 1 | 1 (`permission-rule`) | 0 | none | n/a |
| MM | default | 0 | 1 | 0 | 0 | 0 | none | n/a |
| K2 | auto | 0 | 12 | 0 | 0 | 5 | `artifacts`, `artifacts_reason` | none |
| SS | auto | 0 | 1 | 0 | 0 | 0 | none | n/a |

- `archived_at` differs in all six, as expected.
- The K1 and K2 differences come from the session-L runs having passed `--output-dir` (K1 listed 34 artifact hashes, K2 54), while the first re-run did not (`artifacts` null, `artifacts_reason` `no-output-dir`). With `--output-dir` supplied, every field matches.
- For the 34 files the six manifests list, the source, the session-L archive and the re-run archive are hash-equal, the file sets of the session-L and re-run archives are equal, and the re-run files are mode 0600 in 0700 directories.
- K1 alone warned of denial markers of an unrecognised kind. Neither K1 nor K2 raised a `no-transcript` warning.

## 4. Attribution per instance

K1 dispatched 8 tachi agent instances and K2 5. K1a, B7, MM and SS dispatched none. "Names agree" means the meta `agentType`, the line `attributionAgent` and the dispatched `subagent_type` are the same name.

| Session | # | Agent | Depth | Pinned | Served histogram | Turns | Synthetic | Names agree | Dispatch |
|---|---|---|---|---|---|---|---|---|---|
| K1 | 1 | tachi-threat-infographic | 1 | sonnet | claude-sonnet-5-5 x7 | 7 | 0 | yes | recorded |
| K1 | 2 | tachi-report-assembler | 1 | sonnet | claude-sonnet-5-5 x3 | 3 | 0 | yes | recorded |
| K1 | 3 | tachi-risk-scorer | 1 | sonnet | claude-sonnet-5-5 x8 | 8 | 0 | yes | recorded |
| K1 | 4 | tachi-risk-scorer | 1 | sonnet | claude-sonnet-5-5 x9 | 9 | 0 | yes | recorded |
| K1 | 5 | tachi-control-analyzer | 1 | sonnet | claude-sonnet-5-5 x7 | 7 | 0 | yes | recorded |
| K1 | 6 | tachi-orchestrator | 1 | sonnet | claude-sonnet-5-5 x20 | 20 | 0 | yes | recorded |
| K1 | 7 | tachi-threat-report | 2 | sonnet | claude-sonnet-5-5 x11 | 11 | 0 | yes | recorded |
| K1 | 8 | tachi-attack-tree-delta | 3 | sonnet | claude-sonnet-5-5 x3 | 3 | 0 | yes | recorded |
| K2 | 1 | tachi-report-assembler | 1 | sonnet | claude-sonnet-5-5 x3 | 3 | 0 | yes | recorded |
| K2 | 2 | tachi-orchestrator | 1 | sonnet | claude-sonnet-5-5 x13 | 13 | 0 | yes | recorded |
| K2 | 3 | tachi-threat-infographic | 1 | sonnet | claude-sonnet-5-5 x16 | 16 | 0 | yes | recorded |
| K2 | 4 | tachi-control-analyzer | 1 | sonnet | claude-sonnet-5-5 x7 | 7 | 0 | yes | recorded |
| K2 | 5 | tachi-risk-scorer | 1 | sonnet | claude-sonnet-5-5 x6 | 6 | 0 | yes | recorded |

- **K1**: 8 dispatches, 8 instances, 7 distinct agent types (`tachi-risk-scorer` twice). Status: 8 `recorded`, 0 `dispatch-failed`, 0 `no-transcript`; `tachi_agents_not_recorded` empty. 163 of 163 non-synthetic subagent lines carry an `attributionAgent` equal to the meta `agentType`.
- **K1 not dispatched (14, listed from the roster, never inferred)**: tachi-agent-autonomy, tachi-data-poisoning, tachi-denial-of-service, tachi-human-trust-exploitation, tachi-info-disclosure, tachi-misinformation, tachi-model-theft, tachi-output-integrity, tachi-privilege-escalation, tachi-prompt-injection, tachi-repudiation, tachi-spoofing, tachi-tampering, tachi-tool-abuse.
- **K2**: 5 dispatches, 5 instances. Status: 5 `recorded`, 0 `dispatch-failed`, 0 `no-transcript`; `tachi_agents_not_recorded` empty. 91 of 91 non-synthetic subagent lines carry an `attributionAgent` equal to the meta `agentType`.
- **K2 not dispatched (16)**: tachi-agent-autonomy, tachi-attack-tree-delta, tachi-data-poisoning, tachi-denial-of-service, tachi-human-trust-exploitation, tachi-info-disclosure, tachi-misinformation, tachi-model-theft, tachi-output-integrity, tachi-privilege-escalation, tachi-prompt-injection, tachi-repudiation, tachi-spoofing, tachi-tampering, tachi-threat-report, tachi-tool-abuse.
- **K1a, B7, MM and SS**: 0 dispatches and 0 instances; all 21 roster agents listed as not dispatched.

Cross-checks on all 13 instances:

- Every non-synthetic subagent line has `isSidechain` true and an `agentId` equal to its file's id; main lines are never sidechain.
- Meta `spawnDepth` equals the manifest depth and meta `finished` is true. `parentAgentId` is absent at depth 1 and names the right parent type at depth 2 (`tachi-orchestrator`) and depth 3 (`tachi-threat-report`).
- Meta `model`, every line's `requestedModel` and the served model are `claude-sonnet-5-5` (pinned alias `sonnet` in all 21 roster files). Each launch result's `resolvedModel` is `claude-sonnet-5-5` and its `agentId` equals the instance id.
- Each histogram counts distinct `message.id` values and equals the per-message-id recount; no non-synthetic assistant line lacks a `message.id`.
- The main sessions served `claude-opus-5-5` on every turn (K1a 2, K1 69, B7 2, MM 2, K2 36, SS 3 turns), with 0 synthetic turns.

## 5. Denial detection

The planted probes are those of `w2-live.md` §5.2 and §5.3: 13 in all (K1 9, B7 2, SS 2; M2 is one probe of two calls). WebFetch and the MCP tools were absent from the session, so those probes made no call and left no denial record to detect (`w2-live.md` §5.2); they are outside the 13. Probes were matched to calls by tool name plus an internal signature; each matched one main-session call (M2 two) and none matched in a subagent transcript.

### 5.1 Per kind

| Kind | Planted | Detected by the archiver | Distinct structural marker a parser could key on |
|---|---|---|---|
| Sandbox | 7 probes: K1 (P1, P2, P3, P3b, M2), SS (P1, P3) | **No**: 0 of 7. `toolDenialKind` never takes the value `sandbox`, and no manifest has a sandbox row in `egress_denied` | Partly: only P3 (K1, SS) has `sandboxViolations` (non-empty, `kind` `network`) and `toolResultRemedy` (`kind` `sandbox_violation`). K1 P1, P2, P3b, M2 and SS P1 have none: free text only |
| Classifier | 1 probe: K1 (CL1) | **No**: 0 of 1. The label `automode-blocked` is not among the archiver's `DENIAL_KINDS`, so it is counted as unrecognised and warned, and it is absent from `egress_denied` | Yes: `toolDenialKind` `automode-blocked`; `permissionDecision` reject / classifier, with a `classifierCategory` |
| Permission rule | 5 probes: K1 (P4a, P4b, M1), B7 (Read, Bash) | **Partly**: 2 of 5 (K1 P4b, B7 Bash). The 3 Read-tool refusals (K1 P4a, K1 M1, B7 Read) carry no `toolDenialKind` | Yes: `toolDenialKind` `permission-rule` on Bash results only; `permissionDecision` reject on all 5 (`reasonType` rule for Read, subcommandResults for Bash; `ruleSource` flagSettings) |

- Per session: K1 planted all three kinds (9 probes: sandbox 5, classifier 1, permission rule 3). B7 planted permission rule only (2 probes). SS planted sandbox only (2 probes). K1a, MM and K2 planted none, and their manifests list no denial (K2's unplanted refusal is in section 7).
- Across the 13 planted probes: 8 carry some distinct structural marker and 5 carry none (K1 P1, P2, P3b, M2; SS P1). The archiver recognises 2, counts 1 as an unrecognised label and does not count the other 10.

### 5.2 Per probe

`permissionDecision` is written `decision` / `reasonType`, followed by the other keys it carries. Archiver outcome: **recognised** = counted in `egress_denied`; **unrecognised label** = counted only in the run summary and warned; **not counted** = no denial accounting.

| Session | Probe | Tool | `is_error` | Marker keys and labels on the result entry | Archiver outcome |
|---|---|---|---|---|---|
| K1 | P1 sandbox filesystem | Bash | true | none (`sandboxViolations` is an empty list); free text only | not counted |
| K1 | P2 sandbox network, no proxy | Bash | true | none (`sandboxViolations` is an empty list); free text only | not counted |
| K1 | P3 sandbox proxy | Bash | true | `sandboxViolations` non-empty (`kind` `network`); `toolResultRemedy` `kind` `sandbox_violation` | not counted |
| K1 | P3b pre-run allowlist refusal | Bash | true | none: no `permissionDecision`, `sandboxed` or `sandboxViolations` on the entry; free text only | not counted |
| K1 | P4a Read tool, planted dotenv file | Read | true | `permissionDecision` reject / rule, `ruleSource` flagSettings; no `toolDenialKind` | not counted |
| K1 | P4b Bash read, planted dotenv file | Bash | true | `toolDenialKind` `permission-rule`; `permissionDecision` reject / subcommandResults, `ruleSource` flagSettings | recognised (`permission-rule`) |
| K1 | M1 Read tool, process-environment file | Read | true | `permissionDecision` reject / rule, `ruleSource` flagSettings; no `toolDenialKind` | not counted |
| K1 | M2 process listing (2 calls) | Bash | false | none (`sandboxViolations` is an empty list); free text only; a `returnCodeInterpretation` key | not counted |
| K1 | CL1 classifier-planted request | Bash | true | `toolDenialKind` `automode-blocked`; `permissionDecision` reject / classifier, `reasonCode` `classifier:auto-mode`, `classifierCategory` `sensitive_information_leakage` | unrecognised label |
| B7 | Read tool, planted dotfile | Read | true | `permissionDecision` reject / rule, `ruleSource` flagSettings; no `toolDenialKind` | not counted |
| B7 | Bash read, planted dotfile | Bash | true | `toolDenialKind` `permission-rule`; `permissionDecision` reject / subcommandResults, `ruleSource` flagSettings | recognised (`permission-rule`) |
| SS | P1 sandbox filesystem | Bash | true | none (`sandboxViolations` is an empty list); free text only | not counted |
| SS | P3 sandbox proxy | Bash | true | `sandboxViolations` non-empty (`kind` `network`); `toolResultRemedy` `kind` `sandbox_violation` | not counted |
| K2 | Not one of the 13: unplanted pre-run allowlist refusal (section 7) | Bash | true | no denial marker; the same refusal as K1 P3b | not counted |

K1a (probe Z1) and MM (one sandboxed file creation, granted once at the prompt) hold no denial: their Bash results carry no marker.

### 5.3 Why the archiver misses

- **Classifier.** The marker exists (`toolDenialKind` `automode-blocked`), but the archiver's three labels are `sandbox`, `classifier` and `permission-rule`, and the label `classifier` never occurs.
- **Sandbox.** No sandbox refusal carries a `toolDenialKind`. Two of the 7 carry other markers (`sandboxViolations` and `toolResultRemedy`, on the proxy refusals); the other 5 are free text only.
- **Permission rule.** `toolDenialKind` `permission-rule` is present on Bash results only. The 3 Read-tool refusals carry `permissionDecision` and no `toolDenialKind`.
- **Placement is not the gap.** The archiver reads `toolDenialKind` at the tool_result block, the entry top level and `toolUseResult`, and on 2.1.330 the key sits at the entry top level. The gaps are the label set and which refusals are marked.
- **Text.** The result of every planted denial (M2 included) also holds refusal wording, which the 2 unplanted K1 Bash failures do not. The archiver does not read it.

## 6. Observed denial layout on Claude Code 2.1.330

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

## 7. Corrections to the W2 record

For the orchestrator to apply to `w2-live.md` as dated notes. This record edits no other file.

| Item | Where in `w2-live.md` | Current text | What the structure shows |
|---|---|---|---|
| (a) | §5.8, K1 row | "9 dispatches, all `recorded`" | 8 `Agent` calls in the transcripts, 8 manifest dispatches and 8 instances (7 distinct agent types; `tachi-risk-scorer` ran twice). K2's 5 dispatches and 5 instances stand |
| (b) | Header table ("Unexpected egress denials": 0) and §5.5 ("0. K2 had no denial; K1's denials were the planted probes") | as quoted | K2 held one unplanted refusal before running. A Bash call by `tachi-threat-infographic` that named the Gemini host and carried a per-command allowed-domain field was refused by the strict allowlist: the same refusal as P3b, with no denial marker. The pipeline completed with 6 images. It is the only `is_error` result in K2, and no manifest field lists it (`egress_denied` is empty) |

Dated notes to apply:

- **(a)** "2026-11-20 (T051): K1 had 8 dispatches, not 9. The transcripts, the manifest and the instance count all give 8."
- **(b)** "2026-11-20 (T051): K2 held one refusal that no probe planted. Before it ran, a Bash call by `tachi-threat-infographic` that named the Gemini host and carried a per-command allowed-domain field was refused by the strict allowlist, with the same refusal as P3b and no denial marker. The pipeline completed with 6 images. This qualifies the '0 unexpected egress denials' line in the header table and §5.5, and SC-001's 'zero unexpected egress denials'. The note states the facts and does not rule on whether the refusal is an egress denial."

## 8. Observations for the B1 follow-up

| # | Observation |
|---|---|
| 1 | `egress_observed` counts refused calls: only a `toolDenialKind` excludes a call. K1's count of 3 for the probe host is P2, P3 and P3b (all refused by sandbox layers, none marked); CL1, marked `automode-blocked`, is excluded. SS's count of 1 is P3 |
| 2 | K2's count of 3 for the Gemini host counts command lines that name the host (once per call and host), the refused one included, not HTTP requests. 2 of the 3 ran; the output directory holds 6 request files and 6 response files |
| 3 | `denial_detection.status` is `not-validated` in all six manifests (`VALIDATED_DENIAL_VERSIONS` is empty). The gate tests only for an unrecognised kind, so listing 2.1.330 would read `validated` for K1a, B7, MM, K2 and SS (in-process what-if, nothing written): SS with an empty `egress_denied` beside 2 sandbox refusals, B7 with 1 of its 2 refusals uncounted. Listing 2.1.330 would mislead |
| 4 | Layout drift is counted in the run summaries and is never a failure: entry type `cost-state` (1 per session) and nine assistant keys outside the archiver's list (`apiBlockIndex`, `madeBy`, `promptCacheRequested`, `requestRef`, `session_id`, `thinkingDisplay`, `thinkingDurationMs`, `toolInputStreamMs`, `wireIngestContext`) |
| 5 | M2 reads as success: both results have `is_error` false and a `returnCodeInterpretation` key, and the refusal appears only in the output text |

## 9. Consequences

As the plan sets them. This record edits none of the files named here; the orchestrator applies the marks.

| What the plan sets | Plan line | Applies here as |
|---|---|---|
| Mark the unfinished B1 tasks `[X] honest-stopped (TW-B1)` (T031 to T035, T051) | `agent-assignments.md` line 193 | T035 is the one unfinished B1 task: mark it `[X] honest-stopped (TW-B1)`. T031 to T034 are already `[x]` (`tasks.md` lines 141 to 144), and T051's deliverable is this record. T035 also waited on T051 (`tasks.md` lines 145 and 191) |
| T048 drops its B1 items (the runbook's archiver text, ADR-049's B1 section, ADR-019's manifest sentence) and keeps the B2 items | `agent-assignments.md` line 194 | T048 drops those B1 items |
| B2 continues and may still ship | `agent-assignments.md` line 195; `tasks.md` lines 179 and 223; `agent-assignments.md` line 307 | B2 continues |
| `delivery.md` records the stop and the observed layout | `tasks.md` lines 179 and 223; `agent-assignments.md` line 307; T045 at `tasks.md` line 173 | T045 carries the fired trip-wire (section 2) and the layout (section 6) into `delivery.md`; section 7's notes go to `w2-live.md` |
| How B1 leaves part-b | no plan line | The plan sets no removal steps for B1's built archiver, schema, fixtures and tests (T031 to T033). The architect rules how B1 leaves part-b |
