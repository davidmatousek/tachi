---
finding_id: "AG-5"
risk_level: "Critical"
component: "MCP Tool Server"
generated: "2026-04-19"
---

# Attack Tree: AG-5 — MCP Tool Server Tool Call Injection

```mermaid
graph TD
    GOAL["GOAL: Inject malicious tool calls via\nLLM-influenced JSON-RPC parameters"]
    GOAL --> A["OR"]
    A --> B["Tool name injection: invoke unintended tool"]
    A --> C["Parameter injection: malicious args\nto permitted tool"]
    B --> B1["Influence Orchestrator output to\nemit invalid tool name\n[High / High]"]
    B --> B2["Influence Specialist output to\nemit invalid tool name\n[High / High]"]
    C --> C1["Inject SQL fragments in\nDB tool parameters\n[High / High]"]
    C --> C2["Inject shell metacharacters in\ncommand tool parameters\n[High / High]"]
    C --> C3["Inject attacker-controlled URL\nin HTTP tool parameters (SSRF)\n[Med / High]"]
    B1 --> D["AND"]
    B2 --> D
    C1 --> D
    C2 --> D
    C3 --> D
    D --> E["No tool name allowlist validation\nat Tool Server"]
    D --> F["No per-tool parameter JSON Schema\nvalidation before dispatch"]
    E --> G["Tool Server executes injected tool\nwith service credentials"]
    F --> G
```

**Chain-breaking control**: Implement strict tool call validation: (a) validate the tool name against a registered allowlist, (b) validate each parameter against a per-tool JSON Schema, (c) reject any request that fails validation before execution. Apply parameter encoding for values forwarded to external systems.
