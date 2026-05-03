# Attack Tree: D-1 — Physician Clinical Portal Clinical Query Flood

**Component**: Physician Clinical Portal | **Risk Level**: High | **Finding**: D-1

An attacker floods the Physician Clinical Portal with clinical query requests, degrading availability for legitimate physicians during critical clinical decision periods.

```mermaid
flowchart TD
    D1_root["Degrade clinical query availability for legitimate physicians via portal request flood"]
    D1_or1{{"OR"}}
    D1_leaf1["Launch high-volume clinical query flood targeting portal endpoint without rate limiting"]
    D1_leaf2["Exploit absent adaptive throttling to sustain flood through circuit breaker gaps"]
    D1_leaf3["Cascade load to backend Supervisor Orchestrator until portal becomes unresponsive"]

    D1_root --> D1_or1
    D1_or1 --> D1_leaf1
    D1_or1 --> D1_leaf2
    D1_or1 --> D1_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D1_root goal
    class D1_or1 orGate
    class D1_leaf1,D1_leaf2,D1_leaf3 leaf
```
