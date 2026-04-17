# Attack Tree: T-3 — Inter-Agent Channel Message Tampering

**Component**: Inter-Agent Communication Channel | **Risk Level**: Critical | **Finding**: T-3

An attacker with access to the inter-agent message bus tampers with delegation messages or specialist results in transit, corrupting clinical reasoning across the multi-agent pipeline.

```mermaid
flowchart TD
    T3_root["Corrupt clinical reasoning by tampering with inter-agent messages in transit"]
    T3_or1{{"OR"}}
    T3_sub1["Tamper with delegation messages from Supervisor to Specialist agents"]
    T3_sub2["Modify specialist result messages before Supervisor Orchestrator aggregates them"]
    T3_and1{{"AND"}}
    T3_and2{{"AND"}}
    T3_leaf1["Gain man-in-the-middle position on inter-agent message bus"]
    T3_leaf2["Intercept outbound delegation message from Supervisor Orchestrator"]
    T3_leaf3["Modify task parameters or target agent identity and re-inject"]
    T3_leaf4["Gain write access to inter-agent channel result queue"]
    T3_leaf5["Intercept Diagnostic Agent result before Supervisor reads it"]
    T3_leaf6["Replace result content with adversarially crafted clinical output"]

    T3_root --> T3_or1
    T3_or1 --> T3_sub1
    T3_or1 --> T3_sub2
    T3_sub1 --> T3_and1
    T3_and1 --> T3_leaf1
    T3_and1 --> T3_leaf2
    T3_and1 --> T3_leaf3
    T3_sub2 --> T3_and2
    T3_and2 --> T3_leaf4
    T3_and2 --> T3_leaf5
    T3_and2 --> T3_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T3_root goal
    class T3_and1,T3_and2 andGate
    class T3_or1 orGate
    class T3_sub1,T3_sub2 subGoal
    class T3_leaf1,T3_leaf2,T3_leaf3,T3_leaf4,T3_leaf5,T3_leaf6 leaf
```
