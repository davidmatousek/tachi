# Attack Tree: R-3 -- Missing Decision Chain Audit Trail

| Field | Value |
|-------|-------|
| Finding ID | R-3 |
| Component | LLM Agent Orchestrator |
| Risk Level | High |
| Threat | Missing Decision Chain Audit Trail |
| Correlation | CG-3 (See also: AG-2) |

```mermaid
flowchart TD
    R3_root["Deny orchestrator actions due to missing decision audit trail"]
    R3_or1{{"OR"}}
    R3_leaf1["Tool calls lack originating user context in logs"]
    R3_leaf2["Model reasoning trace not captured for decisions"]
    R3_leaf3["Response attribution gaps prevent forensic reconstruction"]

    R3_root --> R3_or1
    R3_or1 --> R3_leaf1
    R3_or1 --> R3_leaf2
    R3_or1 --> R3_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class R3_root goal
    class R3_or1 orGate
    class R3_leaf1,R3_leaf2,R3_leaf3 leaf
```
