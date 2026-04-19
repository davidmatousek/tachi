---
finding_id: "E-2"
risk_level: "Critical"
component: "LLM Agent Orchestrator"
generated: "2026-04-19"
---

# Attack Tree: E-2 — LLM Agent Orchestrator Self-Authorized Privilege Escalation

```mermaid
graph TD
    GOAL["GOAL: Orchestrator self-authorizes elevated\noperations beyond user session scope"]
    GOAL --> A["AND"]
    A --> B["Prompt injection manipulates\nOrchestrator reasoning"]
    A --> C["No per-session scoped permissions\nenforced independently"]
    B --> B1["Direct prompt injection via user input\n[High / High]"]
    B --> B2["Indirect injection via KB documents\n[High / High]"]
    C --> C1["Tool Server does not independently\nverify session scope\n[High / High]"]
    C --> C2["KB does not enforce per-query\nsession scope\n[High / High]"]
    B1 --> D["Orchestrator's reasoning corrupted:\nself-claims elevated authorization"]
    B2 --> D
    C1 --> D
    C2 --> D
    D --> E["OR"]
    E --> E1["Full KB corpus export\nbeyond session scope"]
    E --> E2["Tool invocations outside\npermitted scope"]
    E --> E3["Unauthorized delegation messages\nto Specialist Agent"]
```

**Chain-breaking control**: Implement per-session scoped permissions for the Orchestrator determined at authentication time and enforced by the Tool Server and KB independently. The Orchestrator MUST NOT grant itself elevated capabilities at runtime. Apply step-up authentication for high-privilege operations.
