# Attack Tree: D-4 — Inter-Agent Communication Channel

**Risk Level**: High
**Component**: Inter-Agent Communication Channel
**Threat**: Message queue flooding drops legitimate coordination messages

```mermaid
graph TD
    Goal["[GOAL] Disrupt Orchestrator-Specialist coordination by flooding message queue"]
    Goal --> A["[OR] Compromised agent floods channel with messages"]
    A --> A1["No per-sender rate limits at Channel layer"]
    A --> A2["No message queue depth limits enforced"]
    Goal --> B["[OR] Malfunctioning process sends high-volume messages"]
    B --> B1["No backpressure mechanism rejecting new messages on saturation"]
    B --> B2["No queue depth monitoring with alerting"]
    Goal --> C["[AND] Legitimate messages dropped or delayed"]
    C --> C1["Delegation and result messages starved by flood traffic"]
    classDef high fill:#e65100,color:#fff
    class Goal high
```
