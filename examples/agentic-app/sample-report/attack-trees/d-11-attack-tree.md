# Attack Tree: D-11 — LLM Agent Orchestrator

**Risk Level**: Critical
**Component**: LLM Agent Orchestrator
**Threat**: Context-window latency amplification blocking inference slots (OWASP LLM10:2025 Vector A)

```mermaid
graph TD
    Goal["[GOAL] Spike per-request latency to per-tenant timeout blocking inference (OWASP LLM10:2025 Cat 13)"]
    Goal --> A["[OR] Construct adversarially long prompt payload"]
    A --> A1["No max-context-window enforcement at API gateway"]
    A --> A2["No per-conversation truncation policy"]
    A --> A3["Context-window monitoring absent"]
    Goal --> B["[OR] Inject recursive prompt-expansion template"]
    B --> B1["Recursive prompt patterns not detected"]
    B --> B2["Chain-of-thought self-engagement causes context runaway"]
    B --> B3["No max-chain-of-thought-iterations limit"]
    Goal --> C["[AND] Fan-out blocks multiple inference slots simultaneously"]
    C --> C1["Orchestrator slot blocked by max-context request"]
    C --> C2["Specialist fan-out leg blocked independently"]
    C --> C3["ClinAdvisor fan-out leg blocked independently"]
    C --> C4["No per-tenant inference-slot cap separate from per-request cap"]
    classDef critical fill:#d32f2f,color:#fff
    classDef llm10 fill:#6a1b9a,color:#fff
    class Goal llm10
```
