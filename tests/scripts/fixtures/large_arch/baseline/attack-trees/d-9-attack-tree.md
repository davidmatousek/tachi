# D-9: Retry storms from worker-2 multiply the load on router-agent when...

**Component**: router-agent | **Risk Level**: Critical | **Finding**: D-9

Retry storms from worker-2 multiply the load on router-agent when it slows down, turning a brief delay into a sustained outage.

```mermaid
flowchart TD
    D9_root["Retry storms from worker-2 multiply the load on router-agent when it..."]
    D9_or1{{"OR"}}
    D9_sub1["Reach router-agent in the Agent Runtime Zone"]
    D9_sub2["Rely on the weakness described in D-9"]
    D9_leaf1["A path exists from planner-agent over HTTP/2 over mTLS"]
    D9_leaf2["Subtask assignments are accepted without an independent check"]
    D9_leaf3["The weakness is present: Retry storms from worker-2 multiply the load on router-agent when..."]
    D9_leaf4["No effective control observed: Add jittered exponential backoff and a retry budget to worker-2..."]

    D9_root --> D9_or1
    D9_or1 --> D9_sub1
    D9_or1 --> D9_sub2
    D9_sub1 --> D9_leaf1
    D9_sub1 --> D9_leaf2
    D9_sub2 --> D9_leaf3
    D9_sub2 --> D9_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D9_root goal
    class D9_or1 orGate
    class D9_sub1,D9_sub2 subGoal
    class D9_leaf1,D9_leaf2,D9_leaf3,D9_leaf4 leaf
```
