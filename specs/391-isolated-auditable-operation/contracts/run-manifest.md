# run-manifest.json v1 (Part B1)

Structured fields only (no free text). Produced by `archive-run-transcripts.py`; documented for consumers at `schemas/run-manifest.yaml` (installed with `schemas/`).

```json
{
  "manifest_version": 1,
  "tachi_version": "v4.49.0-3-gabc1234",
  "session_id": "3f1c…",
  "claude_code_versions": ["2.1.301"],
  "started_at": "2026-11-20T14:02:11Z", "ended_at": "2026-11-20T14:31:40Z", "archived_at": "2026-11-20T15:00:02Z",
  "transcripts": [{"path": "3f1c….jsonl", "bytes": 812345, "sha256": "…"}],
  "main": {"served_model_histogram": {"claude-sonnet-5": 41}, "turns": 41, "synthetic_turns": 1, "tool_calls_by_tool": {"Agent": 1, "Bash": 3}},
  "dispatches": [{"agent": "tachi-orchestrator", "tool_use_id": "toolu_01", "dispatched_from": "main", "spawn_depth": 1, "status": "recorded"},
                 {"agent": "tachi-spoofing", "tool_use_id": "toolu_17", "dispatched_from": "a9…", "spawn_depth": 2, "status": "recorded"},
                 {"agent": "tachi-tool-abuse", "tool_use_id": "toolu_22", "dispatched_from": "a9…", "spawn_depth": 2, "status": "dispatch-failed"}],
  "subagents": [{"agent_id": "a9…", "agent_type": "tachi-orchestrator", "attribution_agent": "tachi-orchestrator", "spawn_depth": 1,
                  "parent_tool_use_id": "toolu_01", "pinned_model": "sonnet", "served_model_histogram": {"claude-sonnet-5": 58},
                  "synthetic_turns": 1, "turns": 59, "tool_calls_by_tool": {"Agent": 15, "Read": 9, "Bash": 1, "Write": 2}, "unknown_meta_keys": []},
                 {"agent_id": "b4…", "agent_type": "tachi-spoofing", "attribution_agent": "tachi-spoofing", "spawn_depth": 2,
                  "parent_tool_use_id": "toolu_17", "pinned_model": "sonnet", "served_model_histogram": {"claude-sonnet-5": 6},
                  "synthetic_turns": 0, "turns": 6, "tool_calls_by_tool": {"Read": 4}, "unknown_meta_keys": []}],
  "tachi_agents_not_recorded": [{"agent": "tachi-tool-abuse", "tool_use_id": "toolu_22", "dispatched_from": "a9…", "reason": "dispatch-failed"}],
  "tachi_agents_not_dispatched": ["tachi-misinformation"],
  "permission_modes_seen": ["auto"],
  "egress_observed": [{"host": "generativelanguage.googleapis.com", "tool": "Bash", "count": 1}],
  "egress_unparsed_count": 0,
  "egress_denied": [{"host": "example.com", "kind": "sandbox", "count": 1}],
  "denial_detection": {"status": "validated", "validated_claude_code_versions": ["2.1.301"]},
  "artifacts": [{"path": "threats.md", "bytes": 48213, "sha256": "…"}]
}
```
Rules: `denial_detection.status` fails closed — `validated` only when every version in `claude_code_versions` has a passing fixture, otherwise `not-validated` (never an empty list standing in for "no denials"); hosts are bare hostnames (userinfo, query and fragment stripped; failures → `<unparseable>` and `egress_unparsed_count`); `artifacts` is `null` with `artifacts_reason` when `--output-dir` is not given; `<synthetic>` turns count in `synthetic_turns`, never in the histogram. Dispatch rules (RC-P1 / PM R-1): a *dispatch* is an `Agent` (legacy `Task`) `tool_use` whose `input.subagent_type` names a tachi agent, in any archived transcript, main or subagent, at any depth; *recorded* when a subagent meta's `toolUseId` equals the `tool_use` id and its `agentType` equals the name; *dispatch-failed* when the matching `tool_result` is an error (listed in `tachi_agents_not_recorded` with `reason: dispatch-failed`; does not trip TW-B1); *not recorded* when the dispatch succeeded and no meta matches (`reason: no-transcript`; trips TW-B1); `tachi_agents_not_dispatched` lists every installed tachi agent with neither a recorded instance nor a dispatch. Minimal parse contract: every assistant line has `message.model`; every subagent meta has `agentType` and `toolUseId`; every subagent assistant line that *carries* `attributionAgent` equals the meta `agentType` (`<synthetic>` lines are exempt; at least one non-synthetic line must carry it, else exit non-zero); ≥ 1 assistant turn; histogram non-empty. "Unparseable" means invalid JSON only; unknown entry `type` values (`api-request`, `api-request-blob`, `api-request-shape`) and unknown keys are tolerated and counted; extra meta keys are listed in `unknown_meta_keys`.
