# LLM-1: edge-gateway passes conversation history from earlier turns into...

Carried from the baseline run.

**Component**: edge-gateway | **Risk Level**: Critical | **Finding**: LLM-1

edge-gateway passes conversation history from earlier turns into the model unchanged, so an injection planted earlier keeps working in later turns.

```mermaid
flowchart TD
    LLM1_root["edge-gateway passes conversation history from earlier turns into the..."]
    LLM1_or1{{"OR"}}
    LLM1_sub1["Reach edge-gateway in the Edge DMZ"]
    LLM1_sub2["Rely on the weakness described in LLM-1"]
    LLM1_leaf1["A path exists from client-portal over HTTPS (TLS 1.3)"]
    LLM1_leaf2["Inbound api requests are accepted without an independent check"]
    LLM1_leaf3["The weakness is present: edge-gateway passes conversation history from earlier turns into..."]
    LLM1_leaf4["No effective control observed: Re-screen conversation history on each turn in edge-gateway..."]

    LLM1_root --> LLM1_or1
    LLM1_or1 --> LLM1_sub1
    LLM1_or1 --> LLM1_sub2
    LLM1_sub1 --> LLM1_leaf1
    LLM1_sub1 --> LLM1_leaf2
    LLM1_sub2 --> LLM1_leaf3
    LLM1_sub2 --> LLM1_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM1_root goal
    class LLM1_or1 orGate
    class LLM1_sub1,LLM1_sub2 subGoal
    class LLM1_leaf1,LLM1_leaf2,LLM1_leaf3,LLM1_leaf4 leaf
```
