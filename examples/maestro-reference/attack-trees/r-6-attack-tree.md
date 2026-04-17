# Attack Tree: R-6 — Supervisor Orchestrator Delegation Record Repudiation

**Component**: Supervisor Orchestrator | **Risk Level**: High | **Finding**: R-6

The Supervisor Orchestrator may fail to maintain non-repudiable records of which delegation commands it issued and which specialist results it aggregated, making agent accountability impossible.

```mermaid
flowchart TD
    R6_root["Enable Supervisor Orchestrator to deny clinical delegation decisions via insufficient audit logging"]
    R6_or1{{"OR"}}
    R6_leaf1["Exploit absent mandatory pre-action audit logging to issue delegation without recorded evidence"]
    R6_leaf2["Tamper with existing orchestration audit records before post-incident review"]
    R6_leaf3["Deny aggregation of specific specialist result when no cryptographic receipt links result to action"]

    R6_root --> R6_or1
    R6_or1 --> R6_leaf1
    R6_or1 --> R6_leaf2
    R6_or1 --> R6_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class R6_root goal
    class R6_or1 orGate
    class R6_leaf1,R6_leaf2,R6_leaf3 leaf
```
