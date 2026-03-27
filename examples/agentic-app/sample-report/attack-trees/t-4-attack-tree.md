# Attack Tree: T-4 -- Knowledge Base Content Poisoning

| Field | Value |
|-------|-------|
| Finding ID | T-4 |
| Component | Knowledge Base |
| Risk Level | High |
| Threat | Knowledge Base Content Poisoning |
| Correlation | CG-1 (See also: LLM-2) |

```mermaid
flowchart TD
    T4_root["Inject malicious content into Knowledge Base"]
    T4_or1{{"OR"}}
    T4_leaf1["Exploit orchestrator write path with unsanitized input"]
    T4_leaf2["Directly access Knowledge Base storage bypassing application"]
    T4_leaf3["Compromise data ingestion pipeline to inject poisoned documents"]

    T4_root --> T4_or1
    T4_or1 --> T4_leaf1
    T4_or1 --> T4_leaf2
    T4_or1 --> T4_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T4_root goal
    class T4_or1 orGate
    class T4_leaf1,T4_leaf2,T4_leaf3 leaf
```
