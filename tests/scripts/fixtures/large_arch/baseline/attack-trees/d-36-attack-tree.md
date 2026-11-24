# D-36: A slow-read attack holds connections to auth-broker open and ties...

**Component**: auth-broker | **Risk Level**: High | **Finding**: D-36

A slow-read attack holds connections to auth-broker open and ties up the workers handling credential assertions and session grants until none remain for real requests.

```mermaid
flowchart TD
    D36_root["A slow-read attack holds connections to auth-broker open and ties up..."]
    D36_or1{{"OR"}}
    D36_sub1["Reach auth-broker in the Edge DMZ"]
    D36_sub2["Rely on the weakness described in D-36"]
    D36_leaf1["A path exists from edge-gateway over gRPC over mTLS"]
    D36_leaf2["Credential assertions and session grants are accepted without an independent check"]
    D36_leaf3["The weakness is present: A slow-read attack holds connections to auth-broker open and ties..."]
    D36_leaf4["No effective control observed: Apply idle and total timeouts on every connection to auth-broker..."]

    D36_root --> D36_or1
    D36_or1 --> D36_sub1
    D36_or1 --> D36_sub2
    D36_sub1 --> D36_leaf1
    D36_sub1 --> D36_leaf2
    D36_sub2 --> D36_leaf3
    D36_sub2 --> D36_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D36_root goal
    class D36_or1 orGate
    class D36_sub1,D36_sub2 subGoal
    class D36_leaf1,D36_leaf2,D36_leaf3,D36_leaf4 leaf
```
