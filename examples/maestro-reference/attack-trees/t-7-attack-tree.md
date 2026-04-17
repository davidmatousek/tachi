# Attack Tree: T-7 — Clinical MCP Tool Server FHIR Tampering

**Component**: Clinical MCP Tool Server | **Risk Level**: Critical | **Finding**: T-7

A compromised MCP Tool Server tampers with FHIR read/write operations, modifying patient records without authorization or returning corrupted data to agents.

```mermaid
flowchart TD
    T7_root["Tamper with FHIR operations via compromised MCP Tool Server to modify patient records"]
    T7_or1{{"OR"}}
    T7_sub1["Compromise MCP Tool Server process to intercept FHIR operations"]
    T7_sub2["Exploit unsigned FHIR operation requests to inject unauthorized writes"]
    T7_and1{{"AND"}}
    T7_and2{{"AND"}}
    T7_leaf1["Gain code execution on MCP Tool Server via vulnerability exploitation"]
    T7_leaf2["Intercept agent tool call before FHIR Resource Store execution"]
    T7_leaf3["Modify FHIR resource payload to inject false clinical data"]
    T7_leaf4["Identify FHIR write endpoint reachable without signed operation request"]
    T7_leaf5["Craft unauthorized FHIR PUT or PATCH operation targeting patient record"]
    T7_leaf6["Submit operation before integrity checksums are applied"]

    T7_root --> T7_or1
    T7_or1 --> T7_sub1
    T7_or1 --> T7_sub2
    T7_sub1 --> T7_and1
    T7_and1 --> T7_leaf1
    T7_and1 --> T7_leaf2
    T7_and1 --> T7_leaf3
    T7_sub2 --> T7_and2
    T7_and2 --> T7_leaf4
    T7_and2 --> T7_leaf5
    T7_and2 --> T7_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T7_root goal
    class T7_and1,T7_and2 andGate
    class T7_or1 orGate
    class T7_sub1,T7_sub2 subGoal
    class T7_leaf1,T7_leaf2,T7_leaf3,T7_leaf4,T7_leaf5,T7_leaf6 leaf
```
