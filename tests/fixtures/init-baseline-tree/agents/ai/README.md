# agents/ai/

AI-specific threat agents extending STRIDE for agentic applications. These cover attack surfaces that traditional STRIDE does not address — prompt injection, tool-use abuse, autonomous decision chains, and model supply chain risks.

## AI Threat Categories

| Agent | Threat Class | Focus |
|-------|-------------|-------|
| `prompt-injection.md` | Prompt Injection | Direct/indirect injection, jailbreaks, instruction override |
| `tool-abuse.md` | Tool-Use Abuse | Unauthorized tool invocation, parameter manipulation, chain-of-tool attacks |
| `data-poisoning.md` | Data Poisoning | Training data contamination, context window manipulation |
| `model-theft.md` | Model Theft | Model extraction, weight exfiltration, API abuse for replication |
| `agent-autonomy.md` | Autonomous Agent Risk | Unbounded loops, goal misalignment, cascading failures |

## 5-Agent-to-2-Table Mapping

Five specialized agent files provide granular threat detection. For concise reporting, their findings consolidate into two output table categories (AG and LLM) in the threat model output.

### Mapping Table

| Output Table | Column Label | Agent Files | Reference Standards |
|--------------|-------------|-------------|---------------------|
| Agentic Threats | AG | `agent-autonomy.md`, `tool-abuse.md` | OWASP Agentic Top 10 2026 (draft), MCP Top 10 v0.1 Beta |
| LLM Threats | LLM | `prompt-injection.md`, `data-poisoning.md`, `model-theft.md` | OWASP LLM Top 10 v2025 |

### Rationale

- **5 agents for detection**: Each agent file operates independently with a focused threat class. This separation enables precise, non-overlapping analysis. An agent examining tool-abuse attacks does not need to reason about model extraction, and vice versa.
- **2 tables for reporting**: The output template (`templates/tachi/output-schemas/threats.md`) groups findings into AG (agentic) and LLM tables. Consumers of the threat model see two concise tables rather than five fragmented ones, making risk assessment and prioritization straightforward.

### How It Works

1. Each of the 5 agent files runs its analysis independently against architecture inputs.
2. The orchestrator collects findings from all 5 agents.
3. Findings from `agent-autonomy.md` and `tool-abuse.md` are grouped under the **AG** column in the output.
4. Findings from `prompt-injection.md`, `data-poisoning.md`, and `model-theft.md` are grouped under the **LLM** column in the output.
5. The output template (`templates/tachi/output-schemas/threats.md`) renders both tables with the AG/LLM column labels.

## Relationship to STRIDE

AI agents supplement — not replace — STRIDE agents. A complete threat model runs both sets. AI agents may cross-reference STRIDE findings (e.g., prompt injection enabling elevation of privilege).
