---
finding_id: "S-6"
risk_level: "Critical"
component: "MCP Tool Server"
generated: "2026-04-19"
---

# Attack Tree: S-6 — MCP Tool Server Caller Spoofing

```mermaid
graph TD
    GOAL["GOAL: Unauthorized process submits\ntool calls as spoofed agent identity"]
    GOAL --> A["AND"]
    A --> B["Attacker process in Application Zone"]
    A --> C["No caller authentication on JSON-RPC endpoints"]
    B --> B1["Compromised service component\n[Med / High]"]
    B --> B2["Insider threat\n[Low / High]"]
    C --> C1["No mTLS or signed caller token required\n[High / High]"]
    B1 --> D["Submit JSON-RPC tool call\nunder spoofed Orchestrator/Specialist identity"]
    B2 --> D
    C1 --> D
    D --> E["Tool Server executes with full\nservice credential set"]
    E --> F["Unauthorized external API calls\nor data access"]
```

**Chain-breaking control**: Enforce caller authentication on all JSON-RPC endpoints. Each agent must present a signed caller token or mTLS certificate. The Tool Server must verify the caller's identity before executing any tool invocation.
