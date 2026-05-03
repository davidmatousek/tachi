# Attack Tree: D-3 — Inter-Agent Channel Delegation Message Flood

**Component**: Inter-Agent Communication Channel | **Risk Level**: High | **Finding**: D-3

An attacker floods the Inter-Agent Communication Channel with spurious delegation messages, starving legitimate specialist agent task processing and disrupting multi-agent coordination.

```mermaid
flowchart TD
    D3_root["Disrupt multi-agent clinical coordination by flooding inter-agent channel with spurious delegation messages"]
    D3_or1{{"OR"}}
    D3_leaf1["Generate high-volume spurious delegation messages targeting inter-agent channel without per-agent rate controls"]
    D3_leaf2["Bypass message origin validation to inject flood traffic from attacker-controlled source"]
    D3_leaf3["Sustain flood until channel queue depth saturates and legitimate task messages are dropped"]

    D3_root --> D3_or1
    D3_or1 --> D3_leaf1
    D3_or1 --> D3_leaf2
    D3_or1 --> D3_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D3_root goal
    class D3_or1 orGate
    class D3_leaf1,D3_leaf2,D3_leaf3 leaf
```
