---
type: shared-reference
name: agent-roster-shared
version: 1.0.0
source_schema: schemas/finding.yaml
source_reference: .claude/skills/tachi-orchestration/references/dispatch-rules.md
consumers:
  - orchestrator
  - threat-report
---

# Agent Roster — Shared Reference

Canonical roster of the typed tachi agents: the exact `subagent_type` that names each agent when a tachi command or agent dispatches it. This is the single source of truth for those names. Every other list of tachi agents in the pipeline is a projection of the tables below.

The roster has 21 agents, one per agent file in `.claude/agents/tachi/`: 14 threat agents (6 STRIDE, 3 AG and 5 LLM) and 7 stage and helper agents. An agent's `subagent_type` is `tachi-` plus its file name without `.md`, so `spoofing.md` is `tachi-spoofing`.

---

## Typed Dispatch Rules

These rules bind every layer that dispatches a tachi agent: the orchestrator, the report agent and the tachi commands.

1. **Name the agent by its `subagent_type`.** Set `subagent_type` on the Agent call to a name from the tables below, character for character. Describing the agent in the prompt is not a dispatch.
2. **Dispatch roster agents only.** A name outside these tables is not a tachi agent. Don't dispatch a `general-purpose` agent or any other type in its place, and don't imitate a roster agent by pasting its prompt file into another agent's prompt. A stand-in holds tools the roster agent doesn't: each Phase 2 threat agent holds `Read`, `Glob` and `Grep` and nothing else.
3. **Stop when a roster agent can't be spawned.** If the Agent call fails because the type is unknown or the agent isn't installed, end the run there. Run no substitute, don't do the analysis in the dispatching context, and don't retry under another type. Print an error that names the agent and the remedy:

   ```
   TACHI <STAGE> FAILED: agent not spawned
   Agent: <subagent_type>
   Remedy: re-run the installer from this project's root: <tachi-repo>/scripts/install.sh
   ```

   `<STAGE>` is the stage that was running. A stage that has a plan directory adds a fourth line, `Kept for diagnosis: <plan dir>`.

---

## Phase 2 Roster (Threat Agents)

The 14 agents the orchestrator dispatches in Phase 2, and again when the coverage gate finds a gap. Rows follow the orchestrator's sequential dispatch order. Which components get which agents is set by `dispatch-rules.md`, not here.

| `subagent_type` | Dispatch key | `category` | Emits | Folds into |
|-----------------|--------------|------------|-------|------------|
| `tachi-spoofing` | S | spoofing | S | — |
| `tachi-tampering` | T | tampering | T | — |
| `tachi-repudiation` | R | repudiation | R | — |
| `tachi-info-disclosure` | I | info-disclosure | I | — |
| `tachi-denial-of-service` | D | denial-of-service | D | — |
| `tachi-privilege-escalation` | E | privilege-escalation | E | — |
| `tachi-agent-autonomy` | AG | agentic | AG | — |
| `tachi-tool-abuse` | AG | agentic | AG | — |
| `tachi-human-trust-exploitation` | AG | agentic | TE | AG |
| `tachi-prompt-injection` | LLM | llm | LLM | — |
| `tachi-data-poisoning` | LLM | llm | LLM | — |
| `tachi-model-theft` | LLM | llm | LLM | — |
| `tachi-output-integrity` | LLM | llm | OI | LLM |
| `tachi-misinformation` | LLM | llm | MI | LLM |

- **Dispatch key**: the letter or group the Phase 2 dispatch table names. A STRIDE letter selects one agent. `AG` and `LLM` each select every agent that carries the key, on top of the component's STRIDE agents, because AI dispatch is additive.
- **`category`**: the `category` value the agent's findings carry, from `schemas/finding.yaml`.
- **Emits**: the ID prefix on the agent's own findings.
- **Folds into**: the prefix Phase 3 gives the finding in its output table. `—` means the finding keeps its own prefix. Today `OI` and `MI` fold into `LLM`, and `TE` folds into `AG` (tracked in #356). A check that allows each agent its own prefix plus its fold reads both columns.

---

## Stage and Helper Agents

The 7 agents that run a stage or help one. Whatever dispatches one of them, a command or an agent, names it from this table under the rules above. `tachi-attack-tree-delta` is the only helper: the report's attack trees come from it, and no other helper exists.

| `subagent_type` | Role |
|-----------------|------|
| `tachi-orchestrator` | Runs the threat-model pipeline, Phases 0 to 5 |
| `tachi-threat-report` | Writes the narrative threat report, Phase 5 |
| `tachi-attack-tree-delta` | Generates and reconciles the attack trees for the report |
| `tachi-risk-scorer` | Supplies the scoring judgment for `/tachi.risk-score` |
| `tachi-control-analyzer` | Supplies the controls judgment for `/tachi.compensating-controls` |
| `tachi-threat-infographic` | Builds infographic specifications and images |
| `tachi-report-assembler` | Assembles the PDF security report |

---

## Projections of This Roster

Other lists of tachi agents, such as an ID-prefix table, a category-to-agent table or a dispatch list, are projections of the tables above. They name the same agents under the same `subagent_type`s, and this file governs if they differ. When an agent is added, renamed or removed, change this file first and the projections after.

**Source**: FR-N4.1 (typed dispatch) and the agent files in `.claude/agents/tachi/`.
