---
finding_id: "AG-4"
risk_level: "Critical"
component: "Inter-Agent Communication Channel"
generated: "2026-04-19"
---

# Attack Tree: AG-4 — Inter-Agent Channel Agent-in-the-Middle Attack

```mermaid
graph TD
    GOAL["GOAL: Attacker intercepts and modifies\ndelegation messages in the Channel"]
    GOAL --> A["AND"]
    A --> B["Access to Channel message routing layer"]
    A --> C["No end-to-end message authentication"]
    B --> B1["Compromised process with Channel access\n[Med / High]"]
    B --> B2["Channel infrastructure vulnerability\n[Med / High]"]
    C --> C1["Orchestrator does not sign\ndelegation messages\n[High / High]"]
    C --> C2["Specialist does not verify\nmessage signature before processing\n[High / High]"]
    C --> C3["No replay detection (monotonic\ncounters, timestamps)\n[High / High]"]
    B1 --> D["Intercept delegation message in transit"]
    B2 --> D
    C1 --> D
    C2 --> D
    C3 --> D
    D --> E["Modify task parameters:\n- Replace tool targets with attacker-controlled\n- Modify resource identifiers\n- Inject unauthorized instructions"]
    E --> F["Forward modified message to Specialist"]
    F --> G["Specialist executes unauthorized actions\nbelieving instructions are from Orchestrator"]
```

**Chain-breaking control**: Implement end-to-end message authentication with digital signatures (Orchestrator signs, Specialist verifies). The Channel itself MUST NOT be trusted for integrity. Implement replay detection (monotonic message counters, timestamp windows).
