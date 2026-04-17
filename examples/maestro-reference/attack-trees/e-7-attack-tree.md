# Attack Tree: E-7 — MCP Tool Server FHIR Privilege Escalation via Tool Chaining

**Component**: Clinical MCP Tool Server | **Risk Level**: Critical | **Finding**: E-7

A compromised agent exploits the Clinical MCP Tool Server to escalate FHIR access beyond the calling agent's authorized scope via tool chaining — executing sequences of individually-permitted operations that collectively achieve unauthorized outcomes.

```mermaid
flowchart TD
    E7_root["Achieve unauthorized FHIR operations via tool chaining privilege escalation at MCP Tool Server"]
    E7_or1{{"OR"}}
    E7_sub1["Chain individually-permitted FHIR operations to achieve bulk data export"]
    E7_sub2["Chain read and write operations to perform unauthorized patient record modification"]
    E7_and1{{"AND"}}
    E7_and2{{"AND"}}
    E7_leaf1["Identify sequence of permitted FHIR read operations covering entire patient cohort"]
    E7_leaf2["Issue iterative paginated FHIR reads aggregating to bulk export without bulk export permission"]
    E7_leaf3["Extract complete patient dataset beyond per-query authorization scope"]
    E7_leaf4["Issue permitted FHIR read to obtain current record state and version identifier"]
    E7_leaf5["Chain permitted conditional FHIR update using version identifier to modify record fields"]
    E7_leaf6["Bypass bulk administrative operation prohibition via chained conditional updates"]

    E7_root --> E7_or1
    E7_or1 --> E7_sub1
    E7_or1 --> E7_sub2
    E7_sub1 --> E7_and1
    E7_and1 --> E7_leaf1
    E7_and1 --> E7_leaf2
    E7_and1 --> E7_leaf3
    E7_sub2 --> E7_and2
    E7_and2 --> E7_leaf4
    E7_and2 --> E7_leaf5
    E7_and2 --> E7_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E7_root goal
    class E7_and1,E7_and2 andGate
    class E7_or1 orGate
    class E7_sub1,E7_sub2 subGoal
    class E7_leaf1,E7_leaf2,E7_leaf3,E7_leaf4,E7_leaf5,E7_leaf6 leaf
```
