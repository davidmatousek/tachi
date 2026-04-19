---
finding_id: "T-3"
risk_level: "Critical"
component: "Specialist Agent"
generated: "2026-04-19"
---

# Attack Tree: T-3 — Specialist Agent Delegation Message Tampering

```mermaid
graph TD
    GOAL["GOAL: Redirect Specialist Agent actions\nvia tampered delegation message"]
    GOAL --> A["AND"]
    A --> B["Access to Inter-Agent Channel"]
    A --> C["No message integrity verification at Specialist"]
    B --> B1["Agent-in-the-middle on Channel queue\n[High / High]"]
    B --> B2["Compromised process with Channel access\n[Med / High]"]
    C --> C1["Specialist accepts delegation messages\nwithout HMAC verification\n[High / High]"]
    B1 --> D["Modify Delegated Task payload:\n- Change tool call targets\n- Inject exfiltration URLs\n- Redirect specialist actions"]
    B2 --> D
    C1 --> D
    D --> E["Specialist executes attacker-directed\ntask sequence"]
    E --> F["Data exfiltration or unauthorized\ntool invocations"]
```

**Chain-breaking control**: Validate and sanitize all task payloads received by the Specialist Agent before execution. Apply message integrity verification (HMAC or digital signature) on every received delegation message. Reject tasks containing unexpected structural patterns.
