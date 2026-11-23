# T-7: An attacker who can write to the channel between summarizer-llm...

**Component**: reviewer-agent | **Risk Level**: High | **Finding**: T-7

An attacker who can write to the channel between summarizer-llm and reviewer-agent modifies drafted proposals awaiting review in transit because messages carry no integrity protection of their own.

```mermaid
flowchart TD
    T7_root["An attacker who can write to the channel between summarizer-llm and..."]
    T7_or1{{"OR"}}
    T7_sub1["Reach reviewer-agent in the Agent Runtime Zone"]
    T7_sub2["Rely on the weakness described in T-7"]
    T7_leaf1["A path exists from summarizer-llm over HTTP/2 over mTLS"]
    T7_leaf2["Drafted proposals awaiting review are accepted without an independent check"]
    T7_leaf3["The weakness is present: An attacker who can write to the channel between summarizer-llm..."]
    T7_leaf4["No effective control observed: Sign messages between summarizer-llm and reviewer-agent with a..."]

    T7_root --> T7_or1
    T7_or1 --> T7_sub1
    T7_or1 --> T7_sub2
    T7_sub1 --> T7_leaf1
    T7_sub1 --> T7_leaf2
    T7_sub2 --> T7_leaf3
    T7_sub2 --> T7_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T7_root goal
    class T7_or1 orGate
    class T7_sub1,T7_sub2 subGoal
    class T7_leaf1,T7_leaf2,T7_leaf3,T7_leaf4 leaf
```
