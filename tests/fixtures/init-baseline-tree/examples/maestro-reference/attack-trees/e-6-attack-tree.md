# Attack Tree: E-6 — Treatment Planner Agent FHIR Access Escalation

**Component**: Treatment Planner Agent | **Risk Level**: High | **Finding**: E-6

A compromised Treatment Planner Agent escalates its access to FHIR resources beyond the current patient's authorized scope through the Clinical MCP Tool Server.

```mermaid
flowchart TD
    E6_root["Access unauthorized FHIR patient records via Treatment Planner Agent scope escalation"]
    E6_or1{{"OR"}}
    E6_leaf1["Compromise Treatment Planner Agent to issue FHIR operations beyond current patient scope"]
    E6_leaf2["Exploit absent per-session FHIR access scoping to access unauthorized patient records"]
    E6_leaf3["Use over-permissive MCP Tool Server resource access to retrieve records outside authorized scope"]

    E6_root --> E6_or1
    E6_or1 --> E6_leaf1
    E6_or1 --> E6_leaf2
    E6_or1 --> E6_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E6_root goal
    class E6_or1 orGate
    class E6_leaf1,E6_leaf2,E6_leaf3 leaf
```
