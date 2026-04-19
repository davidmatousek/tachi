---
finding_id: "AG-2"
risk_level: "Critical"
component: "LLM Agent Orchestrator"
generated: "2026-04-19"
---

# Attack Tree: AG-2 — Agent Collusion: Orchestrator + Specialist Coordination

```mermaid
graph TD
    GOAL["GOAL: Orchestrator and Specialist coordinate\nto exceed per-agent policy limits"]
    GOAL --> A["OR"]
    A --> B["Attacker compromises both agents\nwith coordinated prompts"]
    A --> C["Adversarial inter-agent channel\nmessage injection"]
    B --> B1["Inject coordinated instructions\nvia User prompt targeting Orchestrator\n[High / High]"]
    B --> B2["Inject coordinated instructions\nvia Delegation Message targeting Specialist\n[High / High]"]
    C --> C1["Modify channel messages to embed\ncoordination instructions in both agents\n[High / High]"]
    B1 --> D["AND"]
    B2 --> D
    C1 --> D
    D --> E["No cross-agent rate limits\nor coordination throttles"]
    D --> F["No combined action sequence\npolicy evaluation"]
    E --> G["Joint action achieves prohibited outcome:\n- Policy circumvention\n- Joint data exfiltration exceeding\n  per-agent data export limits\n- Rate limit evasion via\n  agent-distributed requests"]
    F --> G
```

**Chain-breaking control**: Implement cross-agent rate limits and coordination throttles at the Channel level. Log all inter-agent coordination patterns to the Audit Logger. Apply a policy engine that evaluates the combined effect of multi-agent action sequences. Enforce per-agent AND per-session action budgets independently.
