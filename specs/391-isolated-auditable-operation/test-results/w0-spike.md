# W0' attribution spike: T001 run and T002 structure check

**Result: TW-B1 PASSES.** Every tachi agent that was dispatched at depths 1, 2 and 3 can be attributed by name from transcript structure alone. Checks (a) through (f) pass and no fail-closed condition was hit, so B1 may launch when its other gates allow.

**Scope.** Structure only: key names, counts, model ids and depths. No message content was read or recorded. The transcripts are kept in a private copy that is never committed.

## Run setup (T001)

| Item | Value |
|---|---|
| Date | 2026-11-18 local (first transcript timestamp 2026-11-19 UTC) |
| tachi | v4.48.1, stock. Installed with `scripts/install.sh --source <clean clone of the v4.48.1 tag>` into a fresh scratch project. `--version` was not used: it checks out the tag inside the source clone and refuses on any untracked file. |
| Input | `examples/ascii-web-api/input.md` (2,560 bytes), copied to `docs/security/architecture.md`. Its sample `threats.md` has 2 Critical and 5 High findings. |
| Command | `/tachi.threat-model`, no flags, so Phase 5 ran. No `/tachi.infographic`, no `GEMINI_API_KEY`, no `.env`. |
| Claude Code | 2.1.328 (all 2,290 versioned entries) |
| Session model | `claude-opus-5-5` (the `opus[1m]` setting) |
| Agent pins | `model: sonnet` on all 21 agents, served as `claude-sonnet-5-5` |
| Permission mode | auto mode, no sandbox |
| Duration | about 63 minutes in total; the orchestrator took 57 minutes |
| Private copy | `~/.tachi/runs/tachi-cvp-check/<UTC date>-<session>/`, mode 0700, outside every work tree. Contains the main `.jsonl` and `subagents/`: 12 transcripts plus 12 `.meta.json` files. Verified byte-identical to the source. |

An earlier attempt was stopped and discarded. It ran on a stale terminal CLI (2.1.258), which resolved `opus` to `claude-opus-5` and `sonnet` to `claude-sonnet-5`, because Opus 5.5 needs v2.1.280 or later and Sonnet 5.5 needs v2.1.284 or later. The runbook should tell maintainers to check `claude --version` and the status-bar model before a measured run.

## Checks (T002)

| Check | Result |
|---|---|
| (a) A subagent transcript exists for every dispatch at any depth | Pass: 12 of 12 |
| (b) Every meta has `agentType` and `toolUseId` | Pass: 12 of 12 |
| (c) Every assistant line has `message.model` | Pass: 1,086 of 1,086 (64 main, 1,022 subagent) |
| (d) `attributionAgent` equals the meta's `agentType` | Pass. It appears on all 1,022 subagent assistant lines (top-level key). No disagreements and no `<synthetic>` lines. |
| (e) Every subagent instance has a non-empty served-model histogram | Pass: 12 of 12, one model run each |
| (f) The dispatched `subagent_type` matches the meta's `agentType` found via `toolUseId`, at depth 1 and at depth 2 or more | Pass at depths 1, 2 and 3. Every `spawnDepth` equals the dispatcher's depth plus 1. |
| (g) Fail-closed conditions | None: no empty or partial histogram, no name disagreement, and no successful dispatch without a meta |

`Agent` `tool_use` blocks do appear inside subagent transcripts: the orchestrator at depth 1 and `tachi-threat-report` at depth 2 both dispatch. Each of those blocks has a matching meta.

## Dispatch topology

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

## Observed layout (Claude Code 2.1.328)

- **Main entry types:** `user`, `assistant`, `attachment`, `system` (`local_command`, `turn_duration`), `mode`, `permission-mode`, `session-owner`, `atis-latch`, `api-request`, `api-request-blob`, `api-request-shape`, `queue-operation`, `last-prompt`, `tools-used`, `ai-title`, `file-history-snapshot`, `file-history-delta`.
- **Subagent entry types:** `user`, `assistant`, `attachment`, `api-request`, `api-request-blob`, `api-request-shape`.
- **Assistant top-level keys include:** `attributionAgent`, `attributionSkill`, `agentId`, `requestedModel`, `isSidechain`, `serverClassifierRequest` (a per-request id), `effort`, `perTurnEffort`, `version`.
- **Meta keys:** `agentType`, `description`, `finished`, `isBuiltIn`, `launchedWithDefaults`, `model`, `parentAgentId`, `pickedEffortModel`, `requestNonInteractive`, `requestShape`, `spawnDepth`, `toolUseId`.
- `attachment.identity.modelId` records the session's starting model. The dispatch `tool_result` carries `toolUseResult.resolvedModel`.

## Observations for later tasks

1. **The pinned model and the served model can be compared directly (D-1).** Every assistant line has `requestedModel` next to `message.model`. In this run all 1,086 matched: Opus 5.5 to Opus 5.5 and Sonnet 5.5 to Sonnet 5.5. There were no `refusal` stop reasons and no model switches. The meta's `model` and `parentAgentId` fields would let B1 build the topology without parsing dispatches.
2. **`Agent` is a transitive capability (AD-13 and the §8 matrix).** `tachi-threat-report` declares Read, Glob, Grep, Write and Agent. It dispatched three built-in `general-purpose` subagents, which ran 38 `Bash` calls and 1 `Write` between them, all text-processing checks on the report draft. Auto mode allowed every one. Its definition never mentions `general-purpose`. The matrix and the tool-pin guard should therefore treat `Agent` as able to reach any tool unless spawning is restricted, for example by a deny rule such as `Agent(general-purpose)`.
3. **Output-token stops.** Five `max_tokens` stops happened across four agents: tachi-info-disclosure 1, tachi-denial-of-service 1, tachi-threat-report 2, tachi-attack-tree-delta 1. This was on the smallest example input, so it is relevant to #374.
