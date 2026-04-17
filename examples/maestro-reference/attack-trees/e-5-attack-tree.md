# Attack Tree: E-5 — Diagnostic Agent FHIR Access Scope Escalation

**Component**: Diagnostic Agent | **Risk Level**: High | **Finding**: E-5

A compromised Diagnostic Agent escalates beyond its authorized scope by issuing FHIR operations exceeding its data access permissions via the Clinical MCP Tool Server, accessing patient records outside the current clinical query.

```mermaid
flowchart TD
    E5_root["Access patient records outside authorized scope via Diagnostic Agent FHIR permission escalation"]
    E5_or1{{"OR"}}
    E5_leaf1["Compromise Diagnostic Agent to issue FHIR queries beyond current patient scope"]
    E5_leaf2["Exploit absent resource-level FHIR access scoping to enumerate unauthorized patient records"]
    E5_leaf3["Use over-permissive per-session access token to access FHIR resources outside clinical query scope"]

    E5_root --> E5_or1
    E5_or1 --> E5_leaf1
    E5_or1 --> E5_leaf2
    E5_or1 --> E5_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E5_root goal
    class E5_or1 orGate
    class E5_leaf1,E5_leaf2,E5_leaf3 leaf
```
