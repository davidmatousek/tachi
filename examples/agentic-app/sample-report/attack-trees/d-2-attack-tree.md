# Attack Tree: D-2 — LLM Agent Orchestrator

**Risk Level**: Critical
**Component**: LLM Agent Orchestrator
**Threat**: Inference pipeline exhaustion via high-token prompts or recursive tool chains

```mermaid
graph TD
    Goal["[GOAL] Exhaust Orchestrator inference capacity starving legitimate users"]
    Goal --> A["[OR] Flood with high-token-count prompts"]
    A --> A1["No per-session token budgets enforced"]
    A --> A2["No hard context-window limits"]
    Goal --> B["[OR] Inject context forcing recursive tool invocation chains"]
    B --> B1["No circuit breakers on tool invocation chain depth"]
    B --> B2["No maximum recursive depth per session enforced"]
    Goal --> C["[AND] Inference pipeline saturated"]
    C --> C1["No request queuing with priority tiers"]
    C --> C2["No capacity-based load shedding"]
    classDef critical fill:#d32f2f,color:#fff
    class Goal critical
```
