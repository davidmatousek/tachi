# Attack Tree: LLM-16 — LLM Agent Orchestrator

**Risk Level**: High
**Component**: LLM Agent Orchestrator
**Threat**: Denial-of-Wallet via context-window cost amplification (OWASP LLM10:2025 Cat 11)

```mermaid
graph TD
    Goal["[GOAL] Drive operator inference bill to ruin via denial-of-wallet attack (OWASP LLM10:2025 Cat 11)"]
    Goal --> A["[OR] Drive context-window to model maximum per call (Vector B)"]
    A --> A1["No per-tenant token budget hard-cap at API gateway"]
    A --> A2["No at-query-time billing attribution before inference"]
    A --> A3["Context-window cost reconciliation computed async (batch) not synchronously"]
    Goal --> B["[OR] Exploit fan-out to multiply per-request billing 3x"]
    B --> B1["Orchestrator + Specialist + ClinAdvisor all billed per fan-out leg"]
    B --> B2["No per-tenant cumulative context-window token tracking across fan-out legs"]
    Goal --> C["[AND] Sustained attack accumulates undetected"]
    C --> C1["Cost-velocity monitoring across 5-min/1-hr/24-hr windows absent"]
    C --> C2["Automated tenant suspension on budget breach not declared"]
    C --> C3["Denial-of-wallet anomaly detection absent"]
    classDef high fill:#e65100,color:#fff
    classDef llm10 fill:#6a1b9a,color:#fff
    class Goal llm10
```
