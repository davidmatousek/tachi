# MI-4: Confident wording from intake-agent hides low retrieval quality...

**Component**: intake-agent | **Risk Level**: Critical | **Finding**: MI-4

Confident wording from intake-agent hides low retrieval quality, so operators cannot tell a grounded answer from a guess.

```mermaid
flowchart TD
    MI4_root["Confident wording from intake-agent hides low retrieval quality, so..."]
    MI4_or1{{"OR"}}
    MI4_sub1["Reach intake-agent in the Agent Runtime Zone"]
    MI4_sub2["Rely on the weakness described in MI-4"]
    MI4_leaf1["A path exists from edge-gateway over HTTP/2 over mTLS"]
    MI4_leaf2["Free-text shipment requests are accepted without an independent check"]
    MI4_leaf3["The weakness is present: Confident wording from intake-agent hides low retrieval quality..."]
    MI4_leaf4["No effective control observed: Expose retrieval strength alongside the answers of intake-agent..."]

    MI4_root --> MI4_or1
    MI4_or1 --> MI4_sub1
    MI4_or1 --> MI4_sub2
    MI4_sub1 --> MI4_leaf1
    MI4_sub1 --> MI4_leaf2
    MI4_sub2 --> MI4_leaf3
    MI4_sub2 --> MI4_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class MI4_root goal
    class MI4_or1 orGate
    class MI4_sub1,MI4_sub2 subGoal
    class MI4_leaf1,MI4_leaf2,MI4_leaf3,MI4_leaf4 leaf
```
