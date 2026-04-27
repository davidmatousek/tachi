# Attack Tree: I-4 — Inter-Agent Communication Channel

**Risk Level**: Critical
**Component**: Inter-Agent Communication Channel
**Threat**: Inter-agent messages observable to unauthorized Application Zone processes

```mermaid
graph TD
    Goal["[GOAL] Exfiltrate sensitive task context by observing inter-agent messages"]
    Goal --> A["[OR] Gain read access to channel message bus or queue"]
    A --> A1["Exploit flat Application Zone access model"]
    A --> A2["Compromise any service with channel read access"]
    Goal --> B["[OR] Messages observable without decryption"]
    B --> B1["No end-to-end per-message encryption"]
    B --> B2["Only transport-layer encryption (insufficient)"]
    B --> B3["No strict access controls on channel infrastructure"]
    classDef critical fill:#d32f2f,color:#fff
    class Goal critical
```
