# MI-3: intake-agent states carrier rules and customs requirements as fact...

**Component**: intake-agent | **Risk Level**: Critical | **Finding**: MI-3

intake-agent states carrier rules and customs requirements as fact without grounding them in a cited source, so an operator may act on an invented rule.

```mermaid
flowchart TD
    MI3_root["intake-agent states carrier rules and customs requirements as fact..."]
    MI3_or1{{"OR"}}
    MI3_sub1["Reach intake-agent in the Agent Runtime Zone"]
    MI3_sub2["Rely on the weakness described in MI-3"]
    MI3_leaf1["A path exists from edge-gateway over HTTP/2 over mTLS"]
    MI3_leaf2["Free-text shipment requests are accepted without an independent check"]
    MI3_leaf3["The weakness is present: intake-agent states carrier rules and customs requirements as fact..."]
    MI3_leaf4["No effective control observed: Require intake-agent to cite a retrievable source for each factual..."]

    MI3_root --> MI3_or1
    MI3_or1 --> MI3_sub1
    MI3_or1 --> MI3_sub2
    MI3_sub1 --> MI3_leaf1
    MI3_sub1 --> MI3_leaf2
    MI3_sub2 --> MI3_leaf3
    MI3_sub2 --> MI3_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class MI3_root goal
    class MI3_or1 orGate
    class MI3_sub1,MI3_sub2 subGoal
    class MI3_leaf1,MI3_leaf2,MI3_leaf3,MI3_leaf4 leaf
```
