---
finding_id: "T-5"
risk_level: "Critical"
component: "MCP Tool Server"
generated: "2026-04-19"
---

# Attack Tree: T-5 — MCP Tool Server Parameter Injection

```mermaid
graph TD
    GOAL["GOAL: Inject malicious tool call parameters\nvia LLM-generated JSON-RPC output"]
    GOAL --> A["OR"]
    A --> B["Influence Orchestrator LLM output"]
    A --> C["Influence Specialist Agent LLM output"]
    B --> B1["Prompt injection into Orchestrator\n[High / High]"]
    B --> B2["Adversarial KB documents in context\n[Med / High]"]
    C --> C1["Prompt injection via delegation message\n[High / High]"]
    B1 --> D["Attacker-controlled JSON-RPC\ntool call parameters generated"]
    B2 --> D
    C1 --> D
    D --> D1["Tool name injection: call unintended tool"]
    D --> D2["Parameter injection: shell metacharacters\nor SQL fragments in arguments"]
    D1 --> E["AND"]
    D2 --> E
    E --> F["No parameter allowlist validation\nat Tool Server"]
    F --> G["Tool Server executes malicious\ntool invocation with service credentials"]
```

**Chain-breaking control**: Implement strict parameter validation on all JSON-RPC tool invocations: validate parameter types, enforce allowlisted values for enumerable parameters, and reject any request containing metacharacters or unexpected structural elements.
