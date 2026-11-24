# TE-11: reviewer-agent adopts a persona that presents itself as a named...

**Component**: reviewer-agent | **Risk Level**: Critical | **Finding**: TE-11

reviewer-agent adopts a persona that presents itself as a named colleague, so operators trust its suggestions more than its accuracy warrants.

```mermaid
flowchart TD
    TE11_root["reviewer-agent adopts a persona that presents itself as a named..."]
    TE11_or1{{"OR"}}
    TE11_sub1["Reach reviewer-agent in the Agent Runtime Zone"]
    TE11_sub2["Rely on the weakness described in TE-11"]
    TE11_leaf1["A path exists from summarizer-llm over HTTP/2 over mTLS"]
    TE11_leaf2["Drafted proposals awaiting review are accepted without an independent check"]
    TE11_leaf3["The weakness is present: reviewer-agent adopts a persona that presents itself as a named..."]
    TE11_leaf4["No effective control observed: Disclose that reviewer-agent is an automated agent at the start of..."]

    TE11_root --> TE11_or1
    TE11_or1 --> TE11_sub1
    TE11_or1 --> TE11_sub2
    TE11_sub1 --> TE11_leaf1
    TE11_sub1 --> TE11_leaf2
    TE11_sub2 --> TE11_leaf3
    TE11_sub2 --> TE11_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class TE11_root goal
    class TE11_or1 orGate
    class TE11_sub1,TE11_sub2 subGoal
    class TE11_leaf1,TE11_leaf2,TE11_leaf3,TE11_leaf4 leaf
```
