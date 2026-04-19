---
finding_id: "AG-1"
risk_level: "Critical"
component: "LLM Agent Orchestrator"
generated: "2026-04-19"
---

# Attack Tree: AG-1 — LLM Agent Orchestrator Unauthorized Autonomous Action

```mermaid
graph TD
    GOAL["GOAL: Orchestrator autonomously executes\nunauthorized high-impact actions"]
    GOAL --> A["AND"]
    A --> B["Prompt injection hijacks Orchestrator reasoning"]
    A --> C["No scope-enforcement or human-in-the-loop\nfor high-impact operations"]
    B --> B1["Direct user prompt injection\n[High / High]"]
    B --> B2["Indirect KB document injection\n[High / High]"]
    C --> C1["No per-action scope validation\nbefore execution\n[High / High]"]
    C --> C2["No policy engine approval\nfor high-privilege operations\n[High / High]"]
    B1 --> D["Orchestrator acts on attacker-directed\ninstruction autonomously"]
    B2 --> D
    C1 --> D
    C2 --> D
    D --> E1["Mass data exfiltration from KB"]
    D --> E2["Bulk unauthorized External API calls"]
    D --> E3["Unauthorized delegation to Specialist\nfor compound prohibited actions"]
```

**Chain-breaking control**: Implement a scope-enforcement layer requiring every proposed action to be validated against the user session's permitted scope. Apply human-in-the-loop confirmation for high-impact operations. Use a supervised-autonomy model with a separate policy engine.
