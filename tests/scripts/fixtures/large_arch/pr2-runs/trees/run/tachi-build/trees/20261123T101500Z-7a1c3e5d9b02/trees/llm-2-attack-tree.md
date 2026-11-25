# LLM-2: Prompt content logged by auth-broker is later replayed to...

**Component**: edge-gateway | **Risk Level**: High | **Finding**: LLM-2

Prompt content logged by auth-broker is later replayed to edge-gateway for evaluation, carrying planted instructions into a trusted context.

```mermaid
flowchart TD
    LLM2_root["Prompt content logged by auth-broker is later replayed to edge-gateway..."]
    LLM2_or1{{"OR"}}
    LLM2_sub1["Reach edge-gateway in the Edge DMZ"]
    LLM2_sub2["Rely on the weakness described in LLM-2"]
    LLM2_leaf1["A path exists from client-portal over HTTPS (TLS 1.3)"]
    LLM2_leaf2["Inbound api requests are accepted without an independent check"]
    LLM2_leaf3["The weakness is present: Prompt content logged by auth-broker is later replayed to..."]
    LLM2_leaf4["No effective control observed: Mark replayed prompts as untrusted when edge-gateway processes..."]

    LLM2_root --> LLM2_or1
    LLM2_or1 --> LLM2_sub1
    LLM2_or1 --> LLM2_sub2
    LLM2_sub1 --> LLM2_leaf1
    LLM2_sub1 --> LLM2_leaf2
    LLM2_sub2 --> LLM2_leaf3
    LLM2_sub2 --> LLM2_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM2_root goal
    class LLM2_or1 orGate
    class LLM2_sub1,LLM2_sub2 subGoal
    class LLM2_leaf1,LLM2_leaf2,LLM2_leaf3,LLM2_leaf4 leaf
```
