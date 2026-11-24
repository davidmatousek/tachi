# I-14: A timing or size difference in the responses of worker-3 lets an...

**Component**: worker-3 | **Risk Level**: High | **Finding**: I-14

A timing or size difference in the responses of worker-3 lets an observer infer whether specific records of work orders and draft documents exist.

```mermaid
flowchart TD
    I14_root["A timing or size difference in the responses of worker-3 lets an..."]
    I14_or1{{"OR"}}
    I14_sub1["Reach worker-3 in the Agent Runtime Zone"]
    I14_sub2["Rely on the weakness described in I-14"]
    I14_leaf1["A path exists from router-agent over HTTP/2 over mTLS"]
    I14_leaf2["Work orders and draft documents are accepted without an independent check"]
    I14_leaf3["The weakness is present: A timing or size difference in the responses of worker-3 lets an..."]
    I14_leaf4["No effective control observed: Equalise response size and timing for existence checks in..."]

    I14_root --> I14_or1
    I14_or1 --> I14_sub1
    I14_or1 --> I14_sub2
    I14_sub1 --> I14_leaf1
    I14_sub1 --> I14_leaf2
    I14_sub2 --> I14_leaf3
    I14_sub2 --> I14_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I14_root goal
    class I14_or1 orGate
    class I14_sub1,I14_sub2 subGoal
    class I14_leaf1,I14_leaf2,I14_leaf3,I14_leaf4 leaf
```
