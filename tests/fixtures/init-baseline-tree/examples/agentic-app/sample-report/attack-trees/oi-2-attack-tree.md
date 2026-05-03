# Attack Tree: OI-2 — LLM Agent Orchestrator

**Risk Level**: Critical
**Component**: LLM Agent Orchestrator
**Threat**: Server-side code/command execution via LLM-synthesized Tool Call Request (OWASP LLM05:2025)

```mermaid
graph TD
    Goal["[GOAL] Execute server-side code/command via LLM-synthesized Tool Call Request parameters (OWASP LLM05:2025)"]
    Goal --> A["[OR] Cause Orchestrator to emit injection payload in Tool Call Request parameters"]
    A --> A1["Direct prompt injection (LLM-1) shapes Orchestrator tool parameter generation"]
    A --> A2["RAG poisoning (LLM-2) causes adversarial content in tool invocation context"]
    Goal --> B["[AND] MCP Tool Server executes parameter without parameterization"]
    B --> B1["SQL tools: no cursor.execute(sql, params) enforcement (string interpolation used)"]
    B --> B2["Command tools: no subprocess.run([cmd], shell=False) enforcement"]
    B --> B3["No JSON Schema validator at Tool Server ingress"]
    Goal --> C["[AND] Server-side execution achieves attacker objective"]
    C --> C1["SQL injection extracts or modifies database contents"]
    C --> C2["Command injection executes with Tool Server service account"]
    classDef critical fill:#d32f2f,color:#fff
    class Goal critical
```
