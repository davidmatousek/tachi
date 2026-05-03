# Attack Tree: AG-4 — Inter-Agent Communication Channel

**Risk Level**: Critical
**Component**: Inter-Agent Communication Channel
**Threat**: Agent-in-the-middle intercepts and modifies delegation messages

```mermaid
graph TD
    Goal["[GOAL] Redirect Specialist Agent task execution via agent-in-the-middle on channel"]
    Goal --> A["[OR] Gain read/write access to channel message bus"]
    A --> A1["Exploit flat Application Zone trust model"]
    A --> A2["Compromise process with channel read/write access"]
    Goal --> B["[OR] Intercept and modify delegation message in transit"]
    B --> B1["No end-to-end message authentication (Orchestrator signs, Specialist verifies)"]
    B --> B2["Channel not trusted for integrity — security must be at message level"]
    B --> B3["No replay detection via monotonic counters or timestamp windows"]
    Goal --> C["[AND] Specialist executes attacker-controlled task"]
    C --> C1["Modified tool target: legitimate endpoint replaced by attacker-controlled"]
    C --> C2["Modified parameters: exfiltration URL injected"]
    classDef critical fill:#d32f2f,color:#fff
    class Goal critical
```
