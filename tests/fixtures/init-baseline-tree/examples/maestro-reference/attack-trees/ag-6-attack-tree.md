# Attack Tree: AG-6 — Treatment Planner Agent MCP Tool Server FHIR Abuse

**Component**: Treatment Planner Agent | **Risk Level**: High | **Finding**: AG-6

A compromised Treatment Planner Agent abuses the Clinical MCP Tool Server to perform unauthorized FHIR operations, writing false treatment prescriptions or accessing patient records outside the current patient scope.

```mermaid
flowchart TD
    AG6_root["Perform unauthorized FHIR operations via Treatment Planner Agent MCP Tool Server abuse"]
    AG6_or1{{"OR"}}
    AG6_leaf1["Compromise Treatment Planner Agent to issue FHIR write with false treatment prescription data"]
    AG6_leaf2["Exploit absent patient-scope restrictions to access FHIR records for unauthorized patients"]
    AG6_leaf3["Use over-provisioned resource-type permissions to write treatment data outside authorized FHIR scope"]

    AG6_root --> AG6_or1
    AG6_or1 --> AG6_leaf1
    AG6_or1 --> AG6_leaf2
    AG6_or1 --> AG6_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG6_root goal
    class AG6_or1 orGate
    class AG6_leaf1,AG6_leaf2,AG6_leaf3 leaf
```
