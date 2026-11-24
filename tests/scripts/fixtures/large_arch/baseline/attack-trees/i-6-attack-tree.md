# I-6: A timing or size difference in the responses of intake-agent lets...

**Component**: intake-agent | **Risk Level**: High | **Finding**: I-6

A timing or size difference in the responses of intake-agent lets an observer infer whether specific records of free-text shipment requests exist.

```mermaid
flowchart TD
    I6_root["A timing or size difference in the responses of intake-agent lets an..."]
    I6_or1{{"OR"}}
    I6_sub1["Reach intake-agent in the Agent Runtime Zone"]
    I6_sub2["Rely on the weakness described in I-6"]
    I6_leaf1["A path exists from edge-gateway over HTTP/2 over mTLS"]
    I6_leaf2["Free-text shipment requests are accepted without an independent check"]
    I6_leaf3["The weakness is present: A timing or size difference in the responses of intake-agent lets..."]
    I6_leaf4["No effective control observed: Equalise response size and timing for existence checks in..."]

    I6_root --> I6_or1
    I6_or1 --> I6_sub1
    I6_or1 --> I6_sub2
    I6_sub1 --> I6_leaf1
    I6_sub1 --> I6_leaf2
    I6_sub2 --> I6_leaf3
    I6_sub2 --> I6_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I6_root goal
    class I6_or1 orGate
    class I6_sub1,I6_sub2 subGoal
    class I6_leaf1,I6_leaf2,I6_leaf3,I6_leaf4 leaf
```
