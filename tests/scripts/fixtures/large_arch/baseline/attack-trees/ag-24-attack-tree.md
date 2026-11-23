# AG-24: Delegation from edge-gateway to reviewer-agent carries the full...

**Component**: reviewer-agent | **Risk Level**: High | **Finding**: AG-24

Delegation from edge-gateway to reviewer-agent carries the full authority of the original session, so a low-trust sub-task can use high-trust rights.

```mermaid
flowchart TD
    AG24_root["Delegation from edge-gateway to reviewer-agent carries the full..."]
    AG24_or1{{"OR"}}
    AG24_sub1["Reach reviewer-agent in the Agent Runtime Zone"]
    AG24_sub2["Rely on the weakness described in AG-24"]
    AG24_leaf1["A path exists from summarizer-llm over HTTP/2 over mTLS"]
    AG24_leaf2["Drafted proposals awaiting review are accepted without an independent check"]
    AG24_leaf3["The weakness is present: Delegation from edge-gateway to reviewer-agent carries the full..."]
    AG24_leaf4["No effective control observed: Issue narrowly scoped, short-lived delegation grants to..."]

    AG24_root --> AG24_or1
    AG24_or1 --> AG24_sub1
    AG24_or1 --> AG24_sub2
    AG24_sub1 --> AG24_leaf1
    AG24_sub1 --> AG24_leaf2
    AG24_sub2 --> AG24_leaf3
    AG24_sub2 --> AG24_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG24_root goal
    class AG24_or1 orGate
    class AG24_sub1,AG24_sub2 subGoal
    class AG24_leaf1,AG24_leaf2,AG24_leaf3,AG24_leaf4 leaf
```
