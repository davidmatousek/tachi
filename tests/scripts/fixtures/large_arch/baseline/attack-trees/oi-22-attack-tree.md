# OI-22: summarizer-llm emits URLs that downstream services fetch, so an...

**Component**: summarizer-llm | **Risk Level**: High | **Finding**: OI-22

summarizer-llm emits URLs that downstream services fetch, so an attacker can make internal addresses part of the output and trigger server-side requests.

```mermaid
flowchart TD
    OI22_root["summarizer-llm emits URLs that downstream services fetch, so an..."]
    OI22_or1{{"OR"}}
    OI22_sub1["Reach summarizer-llm in the Agent Runtime Zone"]
    OI22_sub2["Rely on the weakness described in OI-22"]
    OI22_leaf1["A path exists from worker-3 over gRPC over mTLS"]
    OI22_leaf2["Shipment records fed into summaries are accepted without an independent check"]
    OI22_leaf3["The weakness is present: summarizer-llm emits URLs that downstream services fetch, so an..."]
    OI22_leaf4["No effective control observed: Validate URLs from summarizer-llm against an allowlist, resolve..."]

    OI22_root --> OI22_or1
    OI22_or1 --> OI22_sub1
    OI22_or1 --> OI22_sub2
    OI22_sub1 --> OI22_leaf1
    OI22_sub1 --> OI22_leaf2
    OI22_sub2 --> OI22_leaf3
    OI22_sub2 --> OI22_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class OI22_root goal
    class OI22_or1 orGate
    class OI22_sub1,OI22_sub2 subGoal
    class OI22_leaf1,OI22_leaf2,OI22_leaf3,OI22_leaf4 leaf
```
