# Attack Tree: MI-3 — Clinical Advisory Sub-Agent

**Risk Level**: Critical
**Component**: Clinical Advisory Sub-Agent
**Threat**: Retrieval-grounding gap causes hallucinated clinical content on out-of-distribution queries (OWASP LLM09:2025)

```mermaid
graph TD
    Goal["[GOAL] Cause ClinAdvisor to generate hallucinated clinical content on queries it cannot retrieve (OWASP LLM09:2025)"]
    Goal --> A["[OR] Submit clinical query for condition not in Knowledge Base"]
    A --> A1["Out-of-distribution query (new disease, rare condition, stale KB)"]
    A --> A2["KB does not contain documents relevant to the clinical query"]
    Goal --> B["[AND] Sub-agent does not detect retrieval failure"]
    B --> B1["No retrieval-quality gate checking recall@k before generation"]
    B --> B2["No minimum hit-score threshold enforced for KB results"]
    B --> B3["No 'insufficient grounding' response path — sub-agent generates regardless"]
    Goal --> C["[AND] Hallucinated clinical content presented with grounding confidence"]
    C --> C1["Fabricated drug dose, contraindication, or diagnosis in summary"]
    C --> C2["No retrieval-quality confidence indicator on output"]
    classDef critical fill:#d32f2f,color:#fff
    class Goal critical
```
