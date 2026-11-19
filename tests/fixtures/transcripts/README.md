# Synthetic transcript fixtures (feature 391, Part B1)

Structure-only fixtures for `scripts/archive-run-transcripts.py`. Each directory models the same logical tachi run as it is laid out by one generation of Claude Code's session directory. They hold placeholders only: no real path, user name, session content or key, and no key-shaped value of any kind (ADR-042). They are not the recorded W2 fixture.

## Layout of `synthetic-genN/`

| Path | What it is |
|---|---|
| `claude-config/projects/-fixture-project/<session>.jsonl` | the main transcript |
| `.../<session>/subagents/agent-<id>.jsonl` and `agent-<id>.meta.json` | one transcript and one metadata file per subagent instance, every depth in one flat directory |
| `.../<session>/tool-results/<tool_use id>.txt` | persisted tool results |
| `project/.claude/agents/tachi/*.md` | a stub roster of 12 tachi agents (`name:` and `model: sonnet`), standing in for an installed project |
| `project/templates/tachi/VERSION` | generation 2 only: `tachi_version: v4.49.0-3-gabc1234`. Generation 1 models an install that predates the marker, so its manifest reads `unknown` |

Use a copy: `CLAUDE_CONFIG_DIR=<copy>/claude-config` and `--project-dir <copy>/project`.

## Placeholders a test substitutes, in the copy

| Token | Where | Replace with |
|---|---|---|
| `/__FIXTURE_PROJECT_DIR__` | every `cwd` value | the real path of the copied `project/` directory (the archiver matches transcripts to `--project-dir` by real path) |
| `__DUMMY_KEY__` | the six planting sites below | a key-shaped value assembled at runtime from fragments, never written as a literal |

Left unsubstituted, `__DUMMY_KEY__` is harmless text. After copying, set every file's mtime to well before the live window (default 120 s): a checkout stamps every file with the checkout time.

## Planting sites (all in both generations)

| Site | Where |
|---|---|
| shell header | the general-purpose instance's `Bash` command (`-H "x-goog-api-key: ..."`) |
| URL query | the same command (`...models?key=...`) and the main session's denied `WebFetch` URL |
| URL userinfo | the same command (`https://fixture-user:...@registry.example.test/...`) |
| tool-result text | the general-purpose instance's `tool_result`, and `tool-results/toolu_fx<N>_gp_01.txt` |
| metadata description | the general-purpose instance's `.meta.json`, and its dispatch `description` |
| denial message | the denied `WebFetch` result text in the main transcript |

## The two generations

| | `synthetic-gen1` | `synthetic-gen2` |
|---|---|---|
| Claude Code `version` | `2.1.282` | `2.1.328` |
| dispatch tool name | `Task` (legacy) | `Agent` |
| metadata keys | 6 (`agentType`, `description`, `finished`, `model`, `spawnDepth`, `toolUseId`) | the 12 known keys (`parentAgentId` on nested instances) |
| entry types | `user`, `assistant`, `summary`, `permission-mode`, `file-history-snapshot` | adds `attachment`, `session-owner`, `atis-latch`, `mode`, `api-request`, `api-request-blob`, `api-request-shape`, `last-prompt`, `ai-title`, `queue-operation` |
| assistant keys | no `requestedModel`, `serverClassifierRequest`, `effort`, `attributionSkill` | all four present |
| responses | one content block per response, sequential dispatch; some lines have no `message.id` | several lines share a `message.id`; parallel dispatch in one response; results grouped in one user line |
| served models | `claude-opus-5` main, `claude-sonnet-5` subagents | `claude-opus-5-5` main, `claude-sonnet-5-5` subagents |
| permission mode | `acceptEdits` | `auto` |

Both carry `attributionAgent` as a top-level key of every non-synthetic subagent assistant line, `Z` timestamps, one `<synthetic>` line in the main transcript and one in the orchestrator's without `attributionAgent`, and one `permission-rule` denial (`toolDenialKind` on the denied `WebFetch` result, the only denial kind observed before W2).

## Topology (same in both)

```
main
 +- tachi-orchestrator                  depth 1  recorded       <session>/subagents/agent-a?f00000000000001
     +- tachi-spoofing                  depth 2  recorded                                  ...002
     +- tachi-tampering                 depth 2  recorded                                  ...003
     +- tachi-tool-abuse                depth 2  dispatch-failed (error result, no meta)
     +- tachi-info-disclosure           depth 2  not-recorded / no-transcript (success, no meta)
     +- tachi-threat-report             depth 2  recorded                                  ...004
         +- tachi-attack-tree-delta     depth 3  recorded                                  ...005
         +- general-purpose (non-tachi) depth 3  listed in subagents, pinned_model null    ...006
```

`a?f` is `a1f` in generation 1 and `a2f` in generation 2. Tool-use ids are `toolu_fx<N>_<owner>_<NN>`. The five roster agents never dispatched are `tachi-denial-of-service`, `tachi-misinformation`, `tachi-model-theft`, `tachi-privilege-escalation`, `tachi-repudiation`.

## Expected manifest facts

| Fact | gen1 | gen2 |
|---|---|---|
| session id | `11111111-1111-4111-8111-111111111111` | `22222222-2222-4222-8222-222222222222` |
| `tachi_version` | `unknown` | `v4.49.0-3-gabc1234` |
| archived files (`transcripts[]`) | 15 | 15 |
| `main` | histogram 4, synthetic 1, turns 5; calls `Task` 1, `WebFetch` 1, `Bash` 1 | same, with `Agent` instead of `Task` |
| orchestrator (turns, synthetic) | 10, 1 | 6, 1 |
| spoofing / tampering / threat-report / attack-tree-delta / general-purpose turns | 2 / 3 / 4 / 2 / 3 | 2 / 3 / 3 / 2 / 3 |
| `egress_observed` | `generativelanguage.googleapis.com` and `registry.example.test`, `Bash`, 1 each | same |
| `egress_denied` | `example.com`, `permission-rule`, 1 | same |
| `egress_unparsed_count` | 0 | 0 |
| `denial_detection` | `not-validated`, no validated versions | same |
| `tachi_agents_not_recorded` | `tachi-tool-abuse` (dispatch-failed), `tachi-info-disclosure` (no-transcript) | same |
| warning on stderr | one successful dispatch has no transcript | same |

Cases the committed files do not carry are built by editing a copy: an invalid JSON line, a missing `agentType` or `toolUseId`, a zero-turn instance, a name disagreement, an extra metadata key, a dispatch whose metadata names another agent, a metadata file that matches no dispatch, a dispatch with no result anywhere, a destination inside a work tree, a live session, a symlink.
