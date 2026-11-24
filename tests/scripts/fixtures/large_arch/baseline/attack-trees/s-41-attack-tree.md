# S-41: An attacker replays a captured reviewer session against...

**Component**: reviewer-agent | **Risk Level**: High | **Finding**: S-41

An attacker replays a captured reviewer session against reviewer-agent, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller.

```mermaid
flowchart TD
    S41_root["An attacker replays a captured reviewer session against..."]
    S41_or1{{"OR"}}
    S41_sub1["Reach reviewer-agent in the Agent Runtime Zone"]
    S41_sub2["Rely on the weakness described in S-41"]
    S41_leaf1["A path exists from summarizer-llm over HTTP/2 over mTLS"]
    S41_leaf2["Drafted proposals awaiting review are accepted without an independent check"]
    S41_leaf3["The weakness is present: An attacker replays a captured reviewer session against..."]
    S41_leaf4["No effective control observed: Bind each reviewer session to the client certificate or device..."]

    S41_root --> S41_or1
    S41_or1 --> S41_sub1
    S41_or1 --> S41_sub2
    S41_sub1 --> S41_leaf1
    S41_sub1 --> S41_leaf2
    S41_sub2 --> S41_leaf3
    S41_sub2 --> S41_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S41_root goal
    class S41_or1 orGate
    class S41_sub1,S41_sub2 subGoal
    class S41_leaf1,S41_leaf2,S41_leaf3,S41_leaf4 leaf
```
