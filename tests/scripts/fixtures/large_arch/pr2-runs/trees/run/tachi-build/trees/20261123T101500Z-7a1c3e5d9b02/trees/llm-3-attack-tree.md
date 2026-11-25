# LLM-3: Encoded or multilingual payloads bypass the keyword filter in...

**Component**: intake-agent | **Risk Level**: High | **Finding**: LLM-3

Encoded or multilingual payloads bypass the keyword filter in front of intake-agent, which only checks plain English text.

```mermaid
flowchart TD
    LLM3_root["Encoded or multilingual payloads bypass the keyword filter in front of..."]
    LLM3_or1{{"OR"}}
    LLM3_sub1["Reach intake-agent in the Agent Runtime Zone"]
    LLM3_sub2["Rely on the weakness described in LLM-3"]
    LLM3_leaf1["A path exists from edge-gateway over HTTP/2 over mTLS"]
    LLM3_leaf2["Free-text shipment requests are accepted without an independent check"]
    LLM3_leaf3["The weakness is present: Encoded or multilingual payloads bypass the keyword filter in..."]
    LLM3_leaf4["No effective control observed: Normalise and decode inputs before filtering in intake-agent..."]

    LLM3_root --> LLM3_or1
    LLM3_or1 --> LLM3_sub1
    LLM3_or1 --> LLM3_sub2
    LLM3_sub1 --> LLM3_leaf1
    LLM3_sub1 --> LLM3_leaf2
    LLM3_sub2 --> LLM3_leaf3
    LLM3_sub2 --> LLM3_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM3_root goal
    class LLM3_or1 orGate
    class LLM3_sub1,LLM3_sub2 subGoal
    class LLM3_leaf1,LLM3_leaf2,LLM3_leaf3,LLM3_leaf4 leaf
```
