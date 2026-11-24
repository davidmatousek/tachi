# D-5: A single oversized or deeply nested payload makes intake-agent...

**Component**: intake-agent | **Risk Level**: High | **Finding**: D-5

A single oversized or deeply nested payload makes intake-agent spend disproportionate memory and CPU parsing free-text shipment requests.

```mermaid
flowchart TD
    D5_root["A single oversized or deeply nested payload makes intake-agent spend..."]
    D5_or1{{"OR"}}
    D5_sub1["Reach intake-agent in the Agent Runtime Zone"]
    D5_sub2["Rely on the weakness described in D-5"]
    D5_leaf1["A path exists from edge-gateway over HTTP/2 over mTLS"]
    D5_leaf2["Free-text shipment requests are accepted without an independent check"]
    D5_leaf3["The weakness is present: A single oversized or deeply nested payload makes intake-agent..."]
    D5_leaf4["No effective control observed: Cap payload size, nesting depth and parse time in intake-agent..."]

    D5_root --> D5_or1
    D5_or1 --> D5_sub1
    D5_or1 --> D5_sub2
    D5_sub1 --> D5_leaf1
    D5_sub1 --> D5_leaf2
    D5_sub2 --> D5_leaf3
    D5_sub2 --> D5_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D5_root goal
    class D5_or1 orGate
    class D5_sub1,D5_sub2 subGoal
    class D5_leaf1,D5_leaf2,D5_leaf3,D5_leaf4 leaf
```
