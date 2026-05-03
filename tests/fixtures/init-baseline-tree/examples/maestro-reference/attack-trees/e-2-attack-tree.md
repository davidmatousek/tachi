# Attack Tree: E-2 — Patient Summary Generator Unauthorized Patient Access

**Component**: Patient Summary Generator | **Risk Level**: High | **Finding**: E-2

An attacker exploits the Patient Summary Generator to request summaries for patients other than the authorized recipient, escalating access to unauthorized patient records.

```mermaid
flowchart TD
    E2_root["Access unauthorized patient records via Patient Summary Generator scope escalation"]
    E2_or1{{"OR"}}
    E2_leaf1["Exploit absent identity-scope validation to request summary for unauthorized patient ID"]
    E2_leaf2["Enumerate patient scope through summary generation requests using guessed patient identifiers"]
    E2_leaf3["Access patient data beyond current authorization scope via missing Supervisor Orchestrator scope enforcement"]

    E2_root --> E2_or1
    E2_or1 --> E2_leaf1
    E2_or1 --> E2_leaf2
    E2_or1 --> E2_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E2_root goal
    class E2_or1 orGate
    class E2_leaf1,E2_leaf2,E2_leaf3 leaf
```
