# Attack Tree: T-1 — Clinical Recommendation Response Tampering in Transit

**Component**: Physician Clinical Portal | **Risk Level**: High | **Finding**: T-1

An attacker tampers with clinical recommendation responses in transit between Supervisor Orchestrator and the Physician Clinical Portal, altering displayed recommendations without physician awareness.

```mermaid
flowchart TD
    T1_root["Alter clinical recommendations displayed to physician via in-transit tampering"]
    T1_or1{{"OR"}}
    T1_leaf1["Position man-in-the-middle between Supervisor Orchestrator and Physician Clinical Portal"]
    T1_leaf2["Intercept unsigned recommendation response and modify clinical content"]
    T1_leaf3["Forward tampered recommendation to portal for display to physician"]

    T1_root --> T1_or1
    T1_or1 --> T1_leaf1
    T1_or1 --> T1_leaf2
    T1_or1 --> T1_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T1_root goal
    class T1_or1 orGate
    class T1_leaf1,T1_leaf2,T1_leaf3 leaf
```
