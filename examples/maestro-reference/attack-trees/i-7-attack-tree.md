# Attack Tree: I-7 — MCP Tool Server PHI Disclosure to Unauthorized Agents

**Component**: Clinical MCP Tool Server | **Risk Level**: Critical | **Finding**: I-7

The Clinical MCP Tool Server may expose PHI from FHIR read operations to unauthorized agents through insufficient access controls on tool results or overly broad FHIR queries.

```mermaid
flowchart TD
    I7_root["Disclose patient PHI to unauthorized agents via MCP Tool Server FHIR access control bypass"]
    I7_or1{{"OR"}}
    I7_sub1["Issue FHIR read via authorized agent session with overly broad query scope"]
    I7_sub2["Exploit absent agent authorization check at MCP Tool Server to read unauthorized PHI"]
    I7_and1{{"AND"}}
    I7_and2{{"AND"}}
    I7_leaf1["Obtain valid agent session token for a legitimate authorized agent"]
    I7_leaf2["Issue FHIR query beyond minimum-necessary scope using broad search parameters"]
    I7_leaf3["Receive PHI for patients outside current clinical query scope"]
    I7_leaf4["Identify MCP tool call endpoint without per-agent authorization enforcement"]
    I7_leaf5["Craft tool call request referencing patient outside agent authorization scope"]
    I7_leaf6["Receive returned PHI data from unvalidated FHIR read operation"]

    I7_root --> I7_or1
    I7_or1 --> I7_sub1
    I7_or1 --> I7_sub2
    I7_sub1 --> I7_and1
    I7_and1 --> I7_leaf1
    I7_and1 --> I7_leaf2
    I7_and1 --> I7_leaf3
    I7_sub2 --> I7_and2
    I7_and2 --> I7_leaf4
    I7_and2 --> I7_leaf5
    I7_and2 --> I7_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I7_root goal
    class I7_and1,I7_and2 andGate
    class I7_or1 orGate
    class I7_sub1,I7_sub2 subGoal
    class I7_leaf1,I7_leaf2,I7_leaf3,I7_leaf4,I7_leaf5,I7_leaf6 leaf
```
