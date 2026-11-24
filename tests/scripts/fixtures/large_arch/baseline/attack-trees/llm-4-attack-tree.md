# LLM-4: Encoded or multilingual payloads bypass the keyword filter in...

**Component**: intake-agent | **Risk Level**: Critical | **Finding**: LLM-4

Encoded or multilingual payloads bypass the keyword filter in front of intake-agent, which only checks plain English text.

```mermaid
flowchart TD
    LLM4_root["Encoded or multilingual payloads bypass the keyword filter in front of..."]
    LLM4_or1{{"OR"}}
    LLM4_sub1["Reach intake-agent in the Agent Runtime Zone"]
    LLM4_sub2["Rely on the weakness described in LLM-4"]
    LLM4_leaf1["A path exists from edge-gateway over HTTP/2 over mTLS"]
    LLM4_leaf2["Free-text shipment requests are accepted without an independent check"]
    LLM4_leaf3["The weakness is present: Encoded or multilingual payloads bypass the keyword filter in..."]
    LLM4_leaf4["No effective control observed: Normalise and decode inputs before filtering in intake-agent..."]

    LLM4_root --> LLM4_or1
    LLM4_or1 --> LLM4_sub1
    LLM4_or1 --> LLM4_sub2
    LLM4_sub1 --> LLM4_leaf1
    LLM4_sub1 --> LLM4_leaf2
    LLM4_sub2 --> LLM4_leaf3
    LLM4_sub2 --> LLM4_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM4_root goal
    class LLM4_or1 orGate
    class LLM4_sub1,LLM4_sub2 subGoal
    class LLM4_leaf1,LLM4_leaf2,LLM4_leaf3,LLM4_leaf4 leaf
```
