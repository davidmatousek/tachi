# MI-6: Outputs from worker-3 flow into decisions without a review step...

**Component**: worker-3 | **Risk Level**: High | **Finding**: MI-6

Outputs from worker-3 flow into decisions without a review step, so one wrong answer is repeated across many shipments.

```mermaid
flowchart TD
    MI6_root["Outputs from worker-3 flow into decisions without a review step, so..."]
    MI6_or1{{"OR"}}
    MI6_sub1["Reach worker-3 in the Agent Runtime Zone"]
    MI6_sub2["Rely on the weakness described in MI-6"]
    MI6_leaf1["A path exists from router-agent over HTTP/2 over mTLS"]
    MI6_leaf2["Work orders and draft documents are accepted without an independent check"]
    MI6_leaf3["The weakness is present: Outputs from worker-3 flow into decisions without a review step..."]
    MI6_leaf4["No effective control observed: Route decisions based on the output of worker-3 through human..."]

    MI6_root --> MI6_or1
    MI6_or1 --> MI6_sub1
    MI6_or1 --> MI6_sub2
    MI6_sub1 --> MI6_leaf1
    MI6_sub1 --> MI6_leaf2
    MI6_sub2 --> MI6_leaf3
    MI6_sub2 --> MI6_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class MI6_root goal
    class MI6_or1 orGate
    class MI6_sub1,MI6_sub2 subGoal
    class MI6_leaf1,MI6_leaf2,MI6_leaf3,MI6_leaf4 leaf
```
