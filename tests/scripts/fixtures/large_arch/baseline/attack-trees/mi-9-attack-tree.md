# MI-9: reviewer-agent fabricates reference numbers and clause citations...

**Component**: reviewer-agent | **Risk Level**: High | **Finding**: MI-9

reviewer-agent fabricates reference numbers and clause citations that look real, which operators then paste into official documents.

```mermaid
flowchart TD
    MI9_root["reviewer-agent fabricates reference numbers and clause citations that..."]
    MI9_or1{{"OR"}}
    MI9_sub1["Reach reviewer-agent in the Agent Runtime Zone"]
    MI9_sub2["Rely on the weakness described in MI-9"]
    MI9_leaf1["A path exists from summarizer-llm over HTTP/2 over mTLS"]
    MI9_leaf2["Drafted proposals awaiting review are accepted without an independent check"]
    MI9_leaf3["The weakness is present: reviewer-agent fabricates reference numbers and clause citations..."]
    MI9_leaf4["No effective control observed: Verify identifiers and citations produced by reviewer-agent..."]

    MI9_root --> MI9_or1
    MI9_or1 --> MI9_sub1
    MI9_or1 --> MI9_sub2
    MI9_sub1 --> MI9_leaf1
    MI9_sub1 --> MI9_leaf2
    MI9_sub2 --> MI9_leaf3
    MI9_sub2 --> MI9_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class MI9_root goal
    class MI9_or1 orGate
    class MI9_sub1,MI9_sub2 subGoal
    class MI9_leaf1,MI9_leaf2,MI9_leaf3,MI9_leaf4 leaf
```
