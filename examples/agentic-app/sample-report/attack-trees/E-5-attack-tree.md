---
finding_id: "E-5"
risk_level: "Critical"
component: "MCP Tool Server"
generated: "2026-04-19"
---

# Attack Tree: E-5 — MCP Tool Server Credential Privilege Escalation

```mermaid
graph TD
    GOAL["GOAL: Unauthorized agent gains Tool Server's\nexecution privileges and credential set"]
    GOAL --> A["OR"]
    A --> B["Forged caller identity submits tool call"]
    A --> C["Exploited Orchestrator issues\nout-of-scope tool call"]
    B --> B1["Spoof Orchestrator caller token\n[High / High]"]
    B --> B2["Compromise mTLS certificate\n[Low / High]"]
    C --> C1["Prompt injection causes Orchestrator\nto invoke unauthorized tools\n[High / High]"]
    B1 --> D["Tool Server receives unauthorized\ntool call request"]
    B2 --> D
    C1 --> D
    D --> E["AND"]
    E --> E1["No zero-trust authorization\nagainst originating session scope"]
    E --> E2["Tool Server trusts caller identity\nwithout independent scope check"]
    E1 --> F["Tool Server executes with full\nservice account credentials:\n- External API keys\n- Data store access\n- Service tokens"]
    E2 --> F
```

**Chain-breaking control**: Implement zero-trust authorization at the Tool Server: each tool invocation MUST be authorized against the originating session's scope, independent of the caller's identity. Apply the principle of least-privilege for tool execution: tool-specific service accounts with minimum necessary external permissions.
