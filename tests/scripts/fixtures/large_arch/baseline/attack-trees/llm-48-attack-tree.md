# LLM-48: Evaluation labels consumed from eval-runner are produced by a...

**Component**: eval-runner | **Risk Level**: Critical | **Finding**: LLM-48

Evaluation labels consumed from eval-runner are produced by a judge model that can itself be influenced by planted traces.

```mermaid
flowchart TD
    LLM48_root["Evaluation labels consumed from eval-runner are produced by a judge..."]
    LLM48_or1{{"OR"}}
    LLM48_sub1["Reach eval-runner in the Operations Zone"]
    LLM48_sub2["Rely on the weakness described in LLM-48"]
    LLM48_leaf1["A path exists from trace-collector over gRPC over mTLS"]
    LLM48_leaf2["Replayed traces and judge verdicts are accepted without an independent check"]
    LLM48_leaf3["The weakness is present: Evaluation labels consumed from eval-runner are produced by a..."]
    LLM48_leaf4["No effective control observed: Calibrate the judge on a human-labelled subset from eval-runner..."]

    LLM48_root --> LLM48_or1
    LLM48_or1 --> LLM48_sub1
    LLM48_or1 --> LLM48_sub2
    LLM48_sub1 --> LLM48_leaf1
    LLM48_sub1 --> LLM48_leaf2
    LLM48_sub2 --> LLM48_leaf3
    LLM48_sub2 --> LLM48_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM48_root goal
    class LLM48_or1 orGate
    class LLM48_sub1,LLM48_sub2 subGoal
    class LLM48_leaf1,LLM48_leaf2,LLM48_leaf3,LLM48_leaf4 leaf
```
