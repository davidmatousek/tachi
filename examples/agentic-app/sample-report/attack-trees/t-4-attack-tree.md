---
finding_id: "T-4"
risk_level: "Critical"
component: "Inter-Agent Communication Channel"
generated: "2026-04-19"
---

# Attack Tree: T-4 — Inter-Agent Channel Message Tampering

```mermaid
graph TD
    GOAL["GOAL: Modify delegation messages in\ntransit via agent-in-the-middle"]
    GOAL --> A["AND"]
    A --> B["Access to Channel message queue\nor shared memory"]
    A --> C["No end-to-end message integrity protection"]
    B --> B1["Exploit Channel infrastructure vulnerability\n[Med / High]"]
    B --> B2["Access via shared Application Zone process\n[Med / High]"]
    C --> C1["Messages not signed by sender\n[High / High]"]
    C --> C2["No message sequence numbers\nor monotonic counters\n[High / High]"]
    B1 --> D["Modify delegation messages before delivery:\n- Replace tool targets\n- Inject malicious instructions\n- Remove safety constraints"]
    B2 --> D
    C1 --> D
    C2 --> D
    D --> E["Specialist Agent acts on\nmodified instructions"]
    E --> F["Unauthorized actions executed\nbelieved to be from Orchestrator"]
```

**Chain-breaking control**: Apply end-to-end message integrity protection (digital signatures) at the channel layer. Messages MUST be signed by the sender and verified by the receiver independently of the channel's transport security. Use message sequence numbers and monotonic counters.
