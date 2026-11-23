# AG-41: intake-agent can act on free-text shipment requests without a...

**Component**: intake-agent | **Risk Level**: Critical | **Finding**: AG-41

intake-agent can act on free-text shipment requests without a human approval step, so a manipulated plan executes high-impact actions with no checkpoint.

```mermaid
flowchart TD
    AG41_root["intake-agent can act on free-text shipment requests without a human..."]
    AG41_or1{{"OR"}}
    AG41_sub1["Reach intake-agent in the Agent Runtime Zone"]
    AG41_sub2["Rely on the weakness described in AG-41"]
    AG41_leaf1["A path exists from edge-gateway over HTTP/2 over mTLS"]
    AG41_leaf2["Free-text shipment requests are accepted without an independent check"]
    AG41_leaf3["The weakness is present: intake-agent can act on free-text shipment requests without a..."]
    AG41_leaf4["No effective control observed: Require explicit human approval in intake-agent for actions above..."]

    AG41_root --> AG41_or1
    AG41_or1 --> AG41_sub1
    AG41_or1 --> AG41_sub2
    AG41_sub1 --> AG41_leaf1
    AG41_sub1 --> AG41_leaf2
    AG41_sub2 --> AG41_leaf3
    AG41_sub2 --> AG41_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG41_root goal
    class AG41_or1 orGate
    class AG41_sub1,AG41_sub2 subGoal
    class AG41_leaf1,AG41_leaf2,AG41_leaf3,AG41_leaf4 leaf
```
