# MI-5: Outputs from intake-agent flow into decisions without a review...

**Component**: intake-agent | **Risk Level**: High | **Finding**: MI-5

Outputs from intake-agent flow into decisions without a review step, so one wrong answer is repeated across many shipments.

```mermaid
flowchart TD
    MI5_root["Outputs from intake-agent flow into decisions without a review step..."]
    MI5_or1{{"OR"}}
    MI5_sub1["Reach intake-agent in the Agent Runtime Zone"]
    MI5_sub2["Rely on the weakness described in MI-5"]
    MI5_leaf1["A path exists from edge-gateway over HTTP/2 over mTLS"]
    MI5_leaf2["Free-text shipment requests are accepted without an independent check"]
    MI5_leaf3["The weakness is present: Outputs from intake-agent flow into decisions without a review..."]
    MI5_leaf4["No effective control observed: Route decisions based on the output of intake-agent through human..."]

    MI5_root --> MI5_or1
    MI5_or1 --> MI5_sub1
    MI5_or1 --> MI5_sub2
    MI5_sub1 --> MI5_leaf1
    MI5_sub1 --> MI5_leaf2
    MI5_sub2 --> MI5_leaf3
    MI5_sub2 --> MI5_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class MI5_root goal
    class MI5_or1 orGate
    class MI5_sub1,MI5_sub2 subGoal
    class MI5_leaf1,MI5_leaf2,MI5_leaf3,MI5_leaf4 leaf
```
