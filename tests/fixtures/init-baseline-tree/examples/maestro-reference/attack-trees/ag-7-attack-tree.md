# Attack Tree: AG-7 — MCP Tool Server Tool Chaining Unauthorized Outcome Achievement

**Component**: Clinical MCP Tool Server | **Risk Level**: Critical | **Finding**: AG-7

A malicious or compromised agent exploits the Clinical MCP Tool Server to perform privilege escalation via tool chaining — executing sequences of individually-permitted FHIR operations that collectively achieve an unauthorized outcome.

```mermaid
flowchart TD
    AG7_root["Achieve unauthorized clinical outcome via tool chain attack on MCP Tool Server FHIR operations"]
    AG7_or1{{"OR"}}
    AG7_sub1["Chain permitted FHIR operations to achieve prohibited bulk patient data export"]
    AG7_sub2["Chain FHIR read and write operations to perform unauthorized record modification sequence"]
    AG7_and1{{"AND"}}
    AG7_and2{{"AND"}}
    AG7_leaf1["Enumerate permitted per-agent FHIR read operations available without restriction"]
    AG7_leaf2["Design operation sequence that individually satisfies per-operation authorization checks"]
    AG7_leaf3["Execute iterative chain to aggregate patient data equivalent to prohibited bulk export"]
    AG7_leaf4["Perform permitted FHIR read to establish resource version and current state"]
    AG7_leaf5["Execute conditional FHIR update using version state to modify clinical record content"]
    AG7_leaf6["Confirm absence of transaction-level chain monitoring that would flag the sequence"]

    AG7_root --> AG7_or1
    AG7_or1 --> AG7_sub1
    AG7_or1 --> AG7_sub2
    AG7_sub1 --> AG7_and1
    AG7_and1 --> AG7_leaf1
    AG7_and1 --> AG7_leaf2
    AG7_and1 --> AG7_leaf3
    AG7_sub2 --> AG7_and2
    AG7_and2 --> AG7_leaf4
    AG7_and2 --> AG7_leaf5
    AG7_and2 --> AG7_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG7_root goal
    class AG7_and1,AG7_and2 andGate
    class AG7_or1 orGate
    class AG7_sub1,AG7_sub2 subGoal
    class AG7_leaf1,AG7_leaf2,AG7_leaf3,AG7_leaf4,AG7_leaf5,AG7_leaf6 leaf
```
