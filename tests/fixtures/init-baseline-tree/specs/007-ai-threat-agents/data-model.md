# Data Model: AI Threat Agents

## Agent Inventory

| Agent File | Category | Threat Class | ID Prefix | Lines | Status |
|-----------|----------|-------------|-----------|-------|--------|
| `agents/ai/prompt-injection.md` | llm | LLM | LLM-N | 134 | Exists, needs validation |
| `agents/ai/data-poisoning.md` | llm | LLM | LLM-N | 143 | Exists, needs validation |
| `agents/ai/model-theft.md` | llm | LLM | LLM-N | 147 | Exists, needs validation |
| `agents/ai/agent-autonomy.md` | agentic | AG | AG-N | 168 | Exists, needs validation |
| `agents/ai/tool-abuse.md` | agentic | AG | AG-N | 139 | Exists, needs validation |

## DFD Targeting Validation Matrix

| Agent | dfd_targets (Expected) | Rationale |
|-------|----------------------|-----------|
| prompt-injection | [Process] | LLM inference endpoints are processes receiving user input |
| data-poisoning | [Data Store, Data Flow] | Poisoning targets training data stores and data flows feeding models |
| model-theft | [Data Store, Process] | Model weights stored in data stores; inference endpoints expose model behavior |
| agent-autonomy | [Process] | Autonomous agents are processes with decision-making capability |
| tool-abuse | [Process] | Tool servers and plugin hosts are processes executing actions |

## Finding IR Schema (read-only)

Schema: `schemas/finding.yaml` v1.0 — 10 required fields

| Field | Type | AI-Specific Notes |
|-------|------|-------------------|
| id | string | Pattern: `^(AG\|LLM)-\d+$` for AI agents |
| category | string | `agentic` or `llm` for AI agents |
| component | string | Must match named component from input — zero tolerance for generic names |
| threat | string | Must describe attacker action + trust assumption violated |
| likelihood | enum | LOW, MEDIUM, HIGH |
| impact | enum | LOW, MEDIUM, HIGH |
| risk_level | enum | Computed from OWASP 3x3 matrix |
| mitigation | string | Must be actionable with specific technology/configuration |
| references | list[string] | Required for AI categories — must include OWASP AI framework IDs |
| dfd_element_type | enum | Must be within agent's `dfd_targets` scope |

## OWASP AI Framework Coverage

### LLM Top 10 v2025 (for LLM agents)

| ID | Name | Mapped To Agent |
|----|------|----------------|
| LLM01:2025 | Prompt Injection | prompt-injection |
| LLM03:2025 | Supply Chain | model-theft, data-poisoning |
| LLM04:2025 | Data and Model Poisoning | data-poisoning |
| LLM07:2025 | System Prompt Leakage | prompt-injection |
| LLM08:2025 | Vector and Embedding Weaknesses | data-poisoning |
| LLM10:2025 | Unbounded Consumption | model-theft |

### Agentic Top 10 2026 (for agentic agents)

| ID | Name | Mapped To Agent |
|----|------|----------------|
| ASI01 | Agent Goal Hijack | agent-autonomy |
| ASI02 | Tool Misuse and Exploitation | tool-abuse |
| ASI04 | Agentic Supply Chain Vulnerabilities | tool-abuse |
| ASI06 | Memory and Context Poisoning | agent-autonomy |
| ASI08 | Cascading Failures | agent-autonomy |
| ASI09 | Human-Agent Trust Exploitation | agent-autonomy |
| ASI10 | Rogue Agents | agent-autonomy |

### MCP Top 10 2025 (for tool-abuse agent)

| ID | Name | Mapped To Agent |
|----|------|----------------|
| MCP03:2025 | Tool Poisoning | tool-abuse |
| MCP05:2025 | Command Injection and Execution | tool-abuse |
