# Attack Tree: MI-1 — Clinical Advisory Sub-Agent

**Risk Level**: Critical
**Component**: Clinical Advisory Sub-Agent
**Threat**: Ungrounded factual emission: hallucinated clinical claims reach clinicians (OWASP LLM09:2025)

```mermaid
graph TD
    Goal["[GOAL] Cause clinician or patient to act on hallucinated clinical assertion (OWASP LLM09:2025)"]
    Goal --> A["[OR] Sub-agent generates ungrounded clinical claim"]
    A --> A1["RAG grounding absent — no per-claim source anchoring required"]
    A --> A2["No retrieval-strength metric (hit-rate or recall@k) enforced"]
    A --> A3["No clinical output validator verifying claims against retrieved documents"]
    Goal --> B["[OR] Hallucinated claim reaches user-facing response"]
    B --> B1["Clinical Summary flows directly to Orchestrator response path"]
    B --> B2["No HITL physician review gate before user delivery (MI-2)"]
    B --> B3["Orchestrator does not validate clinical claim plausibility"]
    classDef critical fill:#d32f2f,color:#fff
    class Goal critical
```
