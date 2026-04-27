# Attack Tree: S-5 — Inter-Agent Communication Channel

**Risk Level**: Critical
**Component**: Inter-Agent Communication Channel
**Threat**: Malicious process injects impersonated messages into shared channel

```mermaid
graph TD
    Goal["[GOAL] Inject task or result messages impersonating Orchestrator or Specialist"]
    Goal --> A["[OR] Gain Application Zone access"]
    A --> A1["Exploit misconfigured network policy (flat Application Zone)"]
    A --> A2["Compromise any service with channel access"]
    Goal --> B["[OR] Inject message with forged sender identity"]
    B --> B1["Channel has no inherent sender authentication"]
    B --> B2["No per-message digital signatures verified at receiver"]
    B --> B3["Any Application Zone process can write to channel"]
    classDef critical fill:#d32f2f,color:#fff
    class Goal critical
```
