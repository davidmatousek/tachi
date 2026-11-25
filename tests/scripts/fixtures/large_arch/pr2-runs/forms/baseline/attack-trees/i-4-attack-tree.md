# I-4: Cross-tenant filters on model-gateway are applied in application...

Carried from the baseline run.

**Component**: model-gateway | **Risk Level**: High | **Finding**: I-4

Cross-tenant filters on model-gateway are applied in application code only, so one missing predicate exposes another tenant's prompts and completions.

```mermaid
flowchart TD
    I4_root["Cross-tenant filters on model-gateway are applied in application code..."]
    I4_or1{{"OR"}}
    I4_sub1["Reach model-gateway in the Agent Runtime Zone"]
    I4_sub2["Rely on the weakness described in I-4"]
    I4_leaf1["A path exists from planner-agent over HTTPS (TLS 1.3)"]
    I4_leaf2["Prompts and completions are accepted without an independent check"]
    I4_leaf3["The weakness is present: Cross-tenant filters on model-gateway are applied in application..."]
    I4_leaf4["No effective control observed: Enforce tenant isolation in the data layer with row-level policies..."]

    I4_root --> I4_or1
    I4_or1 --> I4_sub1
    I4_or1 --> I4_sub2
    I4_sub1 --> I4_leaf1
    I4_sub1 --> I4_leaf2
    I4_sub2 --> I4_leaf3
    I4_sub2 --> I4_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I4_root goal
    class I4_or1 orGate
    class I4_sub1,I4_sub2 subGoal
    class I4_leaf1,I4_leaf2,I4_leaf3,I4_leaf4 leaf
```
