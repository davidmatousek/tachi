# Attack Tree: D-10 — FHIR Resource Store Query Flood

**Component**: FHIR Resource Store | **Risk Level**: High | **Finding**: D-10

An attacker executes resource-exhausting FHIR queries or write floods against the FHIR Resource Store, degrading availability for all components dependent on patient record retrieval.

```mermaid
flowchart TD
    D10_root["Degrade FHIR patient record availability via resource-exhausting query flood"]
    D10_or1{{"OR"}}
    D10_leaf1["Issue high-complexity FHIR queries exceeding resource store compute limits without rate throttling"]
    D10_leaf2["Launch FHIR write flood saturating storage I/O and blocking legitimate read operations"]
    D10_leaf3["Coordinate multi-agent flood using compromised agents to overcome per-component quotas"]

    D10_root --> D10_or1
    D10_or1 --> D10_leaf1
    D10_or1 --> D10_leaf2
    D10_or1 --> D10_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D10_root goal
    class D10_or1 orGate
    class D10_leaf1,D10_leaf2,D10_leaf3 leaf
```
