---
finding_id: "D-5"
risk_level: "Critical"
component: "MCP Tool Server"
generated: "2026-04-19"
---

# Attack Tree: D-5 — MCP Tool Server Connection Pool Exhaustion

```mermaid
graph TD
    GOAL["GOAL: Exhaust MCP Tool Server connection pool\ncausing all legitimate tool calls to fail"]
    GOAL --> A["AND"]
    A --> B["Compromised or adversarially prompted agent\ngenerates high-volume tool call requests"]
    A --> C["No per-caller rate limiting or\nconnection pool overflow rejection"]
    B --> B1["Orchestrator prompt injection causing\nflood of tool requests\n[High / High]"]
    B --> B2["Adversarial delegation message causing\nSpecialist to flood tool requests\n[Med / High]"]
    C --> C1["Tool Server queues all requests —\npool exhaustion via queuing\n[High / High]"]
    B1 --> D["High-volume concurrent tool call requests\nreach Tool Server"]
    B2 --> D
    C1 --> D
    D --> E["External API connection pool exhausted"]
    E --> F1["Legitimate tool calls fail\nwith pool exhaustion error"]
    E --> F2["API provider rate limit triggered —\nsystem locked out"]
    F1 --> G["Tool-dependent agent pipeline unavailable"]
    F2 --> G
```

**Chain-breaking control**: Implement per-caller and per-tool rate limiting at the Tool Server. Enforce a connection pool limit with overflow rejection (not queuing) for requests exceeding the pool. Apply per-session tool call budgets. Use circuit breakers to isolate External API degradation.
