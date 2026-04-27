# Attack Tree: D-9 — Clinical Advisory Sub-Agent

**Risk Level**: High
**Component**: Clinical Advisory Sub-Agent
**Threat**: High-volume clinical queries exhaust sub-agent inference and starve KB

```mermaid
graph TD
    Goal["[GOAL] Exhaust Clinical Advisory Sub-Agent inference capacity and starve KB"]
    Goal --> A["[OR] Orchestrator dispatches high-volume clinical queries"]
    A --> A1["No per-session ClinAdvisor invocation rate limit"]
    A --> A2["Adversarially complex clinical contexts sent per invocation"]
    Goal --> B["[OR] Each invocation triggers expensive KB vector search"]
    B --> B1["No per-query timeout limits on ClinAdvisor searches"]
    B --> B2["No KB query complexity bounds for ClinAdvisor"]
    Goal --> C["[AND] KB unavailable for Orchestrator baseline retrieval"]
    C --> C1["KB capacity shared between Orchestrator and ClinAdvisor without isolation"]
    classDef high fill:#e65100,color:#fff
    class Goal high
```
