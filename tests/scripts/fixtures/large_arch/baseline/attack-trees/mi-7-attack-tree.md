# MI-7: Confident wording from reviewer-agent hides low retrieval quality...

**Component**: reviewer-agent | **Risk Level**: High | **Finding**: MI-7

Confident wording from reviewer-agent hides low retrieval quality, so operators cannot tell a grounded answer from a guess.

```mermaid
flowchart TD
    MI7_root["Confident wording from reviewer-agent hides low retrieval quality, so..."]
    MI7_or1{{"OR"}}
    MI7_sub1["Reach reviewer-agent in the Agent Runtime Zone"]
    MI7_sub2["Rely on the weakness described in MI-7"]
    MI7_leaf1["A path exists from summarizer-llm over HTTP/2 over mTLS"]
    MI7_leaf2["Drafted proposals awaiting review are accepted without an independent check"]
    MI7_leaf3["The weakness is present: Confident wording from reviewer-agent hides low retrieval quality..."]
    MI7_leaf4["No effective control observed: Expose retrieval strength alongside the answers of reviewer-agent..."]

    MI7_root --> MI7_or1
    MI7_or1 --> MI7_sub1
    MI7_or1 --> MI7_sub2
    MI7_sub1 --> MI7_leaf1
    MI7_sub1 --> MI7_leaf2
    MI7_sub2 --> MI7_leaf3
    MI7_sub2 --> MI7_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class MI7_root goal
    class MI7_or1 orGate
    class MI7_sub1,MI7_sub2 subGoal
    class MI7_leaf1,MI7_leaf2,MI7_leaf3,MI7_leaf4 leaf
```
