# MI-17: Outputs from eval-runner flow into decisions without a review...

**Component**: eval-runner | **Risk Level**: High | **Finding**: MI-17

Outputs from eval-runner flow into decisions without a review step, so one wrong answer is repeated across many shipments.

```mermaid
flowchart TD
    MI17_root["Outputs from eval-runner flow into decisions without a review step, so..."]
    MI17_or1{{"OR"}}
    MI17_sub1["Reach eval-runner in the Operations Zone"]
    MI17_sub2["Rely on the weakness described in MI-17"]
    MI17_leaf1["A path exists from trace-collector over gRPC over mTLS"]
    MI17_leaf2["Replayed traces and judge verdicts are accepted without an independent check"]
    MI17_leaf3["The weakness is present: Outputs from eval-runner flow into decisions without a review..."]
    MI17_leaf4["No effective control observed: Route decisions based on the output of eval-runner through human..."]

    MI17_root --> MI17_or1
    MI17_or1 --> MI17_sub1
    MI17_or1 --> MI17_sub2
    MI17_sub1 --> MI17_leaf1
    MI17_sub1 --> MI17_leaf2
    MI17_sub2 --> MI17_leaf3
    MI17_sub2 --> MI17_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class MI17_root goal
    class MI17_or1 orGate
    class MI17_sub1,MI17_sub2 subGoal
    class MI17_leaf1,MI17_leaf2,MI17_leaf3,MI17_leaf4 leaf
```
