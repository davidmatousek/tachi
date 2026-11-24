# LLM-16: Encoded or multilingual payloads bypass the keyword filter in...

**Component**: reviewer-agent | **Risk Level**: High | **Finding**: LLM-16

Encoded or multilingual payloads bypass the keyword filter in front of reviewer-agent, which only checks plain English text.

```mermaid
flowchart TD
    LLM16_root["Encoded or multilingual payloads bypass the keyword filter in front of..."]
    LLM16_or1{{"OR"}}
    LLM16_sub1["Reach reviewer-agent in the Agent Runtime Zone"]
    LLM16_sub2["Rely on the weakness described in LLM-16"]
    LLM16_leaf1["A path exists from summarizer-llm over HTTP/2 over mTLS"]
    LLM16_leaf2["Drafted proposals awaiting review are accepted without an independent check"]
    LLM16_leaf3["The weakness is present: Encoded or multilingual payloads bypass the keyword filter in..."]
    LLM16_leaf4["No effective control observed: Normalise and decode inputs before filtering in reviewer-agent..."]

    LLM16_root --> LLM16_or1
    LLM16_or1 --> LLM16_sub1
    LLM16_or1 --> LLM16_sub2
    LLM16_sub1 --> LLM16_leaf1
    LLM16_sub1 --> LLM16_leaf2
    LLM16_sub2 --> LLM16_leaf3
    LLM16_sub2 --> LLM16_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM16_root goal
    class LLM16_or1 orGate
    class LLM16_sub1,LLM16_sub2 subGoal
    class LLM16_leaf1,LLM16_leaf2,LLM16_leaf3,LLM16_leaf4 leaf
```
