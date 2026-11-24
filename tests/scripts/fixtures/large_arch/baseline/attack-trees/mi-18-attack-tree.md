# MI-18: eval-runner fabricates reference numbers and clause citations that...

**Component**: eval-runner | **Risk Level**: High | **Finding**: MI-18

eval-runner fabricates reference numbers and clause citations that look real, which operators then paste into official documents.

```mermaid
flowchart TD
    MI18_root["eval-runner fabricates reference numbers and clause citations that..."]
    MI18_or1{{"OR"}}
    MI18_sub1["Reach eval-runner in the Operations Zone"]
    MI18_sub2["Rely on the weakness described in MI-18"]
    MI18_leaf1["A path exists from trace-collector over gRPC over mTLS"]
    MI18_leaf2["Replayed traces and judge verdicts are accepted without an independent check"]
    MI18_leaf3["The weakness is present: eval-runner fabricates reference numbers and clause citations that..."]
    MI18_leaf4["No effective control observed: Verify identifiers and citations produced by eval-runner against..."]

    MI18_root --> MI18_or1
    MI18_or1 --> MI18_sub1
    MI18_or1 --> MI18_sub2
    MI18_sub1 --> MI18_leaf1
    MI18_sub1 --> MI18_leaf2
    MI18_sub2 --> MI18_leaf3
    MI18_sub2 --> MI18_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class MI18_root goal
    class MI18_or1 orGate
    class MI18_sub1,MI18_sub2 subGoal
    class MI18_leaf1,MI18_leaf2,MI18_leaf3,MI18_leaf4 leaf
```
