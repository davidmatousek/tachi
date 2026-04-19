---
finding_id: "S-3"
risk_level: "Critical"
component: "LLM Agent Orchestrator"
generated: "2026-04-19"
---

# Attack Tree: S-3 — LLM Agent Orchestrator Identity Spoofing

```mermaid
graph TD
    GOAL["GOAL: Rogue process injects messages\nimpersonating Orchestrator in Channel"]
    GOAL --> A["OR"]
    A --> B["Compromise a process in Application Zone"]
    A --> C["Directly access Channel message queue"]
    B --> B1["Exploit unpatched service vulnerability\n[Med / High]"]
    B --> B2["Insider threat or misconfiguration\n[Low / High]"]
    C --> C1["Misconfigured queue access controls\n[Med / High]"]
    B1 --> D["AND"]
    B2 --> D
    C1 --> D
    D --> E["No HMAC/asymmetric signature on messages"]
    D --> F["Specialist Agent does not verify sender"]
    E --> G["Inject delegation instructions to Specialist\nunder Orchestrator identity"]
    F --> G
    G --> H["Specialist executes unauthorized tasks\nbelieving instructions are legitimate"]
```

**Chain-breaking control**: Authenticate all Orchestrator→Channel messages using HMAC or asymmetric signing with per-session keys. The Specialist Agent MUST verify the signature before acting on delegated tasks.
