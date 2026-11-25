# LLM-7: worker-2 follows links and files named in work orders and route...

**Component**: worker-2 | **Risk Level**: Critical | **Finding**: LLM-7

worker-2 follows links and files named in work orders and route candidates, which turns a harmless-looking request into a fetch of attacker-controlled content.

```mermaid
flowchart TD
    LLM7_root["worker-2 follows links and files named in work orders and route..."]
    LLM7_or1{{"OR"}}
    LLM7_sub1["Reach worker-2 in the Agent Runtime Zone"]
    LLM7_sub2["Rely on the weakness described in LLM-7"]
    LLM7_leaf1["A path exists from tool-server-1 over HTTPS (TLS 1.3)"]
    LLM7_leaf2["Work orders and route candidates are accepted without an independent check"]
    LLM7_leaf3["The weakness is present: worker-2 follows links and files named in work orders and route..."]
    LLM7_leaf4["No effective control observed: Restrict what worker-2 may fetch to an allowlist of domains and..."]

    LLM7_root --> LLM7_or1
    LLM7_or1 --> LLM7_sub1
    LLM7_or1 --> LLM7_sub2
    LLM7_sub1 --> LLM7_leaf1
    LLM7_sub1 --> LLM7_leaf2
    LLM7_sub2 --> LLM7_leaf3
    LLM7_sub2 --> LLM7_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM7_root goal
    class LLM7_or1 orGate
    class LLM7_sub1,LLM7_sub2 subGoal
    class LLM7_leaf1,LLM7_leaf2,LLM7_leaf3,LLM7_leaf4 leaf
```
