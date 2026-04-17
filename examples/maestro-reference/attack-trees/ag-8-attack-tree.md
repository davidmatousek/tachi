# Attack Tree: AG-8 — Inter-Agent Channel Resource Exhaustion via Compromised Agent Flood

**Component**: Inter-Agent Communication Channel | **Risk Level**: High | **Finding**: AG-8

A compromised or rogue agent abuses the Inter-Agent Communication Channel to flood specialist agents with excessive delegation messages, executing a resource exhaustion attack that disrupts multi-agent coordination.

```mermaid
flowchart TD
    AG8_root["Disrupt multi-agent clinical coordination via compromised agent channel flooding"]
    AG8_or1{{"OR"}}
    AG8_leaf1["Compromise agent to generate high-volume delegation messages exceeding channel capacity"]
    AG8_leaf2["Exploit absent per-agent message rate limits to sustain channel flood from compromised agent"]
    AG8_leaf3["Cause specialist agents to drop legitimate coordination tasks due to message queue saturation"]

    AG8_root --> AG8_or1
    AG8_or1 --> AG8_leaf1
    AG8_or1 --> AG8_leaf2
    AG8_or1 --> AG8_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG8_root goal
    class AG8_or1 orGate
    class AG8_leaf1,AG8_leaf2,AG8_leaf3 leaf
```
