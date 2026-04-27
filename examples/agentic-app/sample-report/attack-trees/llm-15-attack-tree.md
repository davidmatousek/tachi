# Attack Tree: LLM-15 — LLM Agent Orchestrator

**Risk Level**: Critical
**Component**: LLM Agent Orchestrator
**Threat**: Cost amplification via recursive or cost-asymmetric prompting (OWASP LLM10:2025 Cat 10)

```mermaid
graph TD
    Goal["[GOAL] Drive operator inference cost exceeding revenue via recursive cost amplification (OWASP LLM10:2025)"]
    Goal --> A["[OR] Submit recursive or cost-asymmetric prompt"]
    A --> A1["No recursive-prompt depth limit at inference-runtime layer"]
    A --> A2["Output-token cap missing or set to model maximum (not p99)"]
    A --> A3["Output-amplification ratio monitoring absent — >100x invisible"]
    Goal --> B["[OR] Exploit multi-hop fan-out for cost multiplication"]
    B --> B1["Orchestrator → Specialist → ToolServer → ExtAPI hop chain"]
    B --> B2["Orchestrator → ClinAdvisor → KB RAG fan-out chain"]
    B --> B3["No aggregate per-request token budget across all fan-out legs"]
    Goal --> C["[AND] Sustained attack accumulates undetected"]
    C --> C1["Cost-per-query p99 alerting absent"]
    C --> C2["Per-tenant cost-amplification anomaly detection absent"]
    classDef critical fill:#d32f2f,color:#fff
    classDef llm10 fill:#6a1b9a,color:#fff
    class Goal llm10
```
