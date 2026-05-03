# Attack Tree: MI-2 — Clinical Advisory Sub-Agent

**Risk Level**: Critical
**Component**: Clinical Advisory Sub-Agent
**Threat**: Overreliance/Missing HITL: clinical recommendations surface without physician sign-off (OWASP LLM09:2025)

```mermaid
graph TD
    Goal["[GOAL] Cause patient or clinician harm via unreviewed AI-generated clinical recommendation (OWASP LLM09:2025)"]
    Goal --> A["[OR] ClinAdvisor generates drug dosing or diagnostic recommendation"]
    A --> A1["Clinical recommendation generated without physician domain constraint"]
    A --> A2["AI-provenance not disclosed on recommendation output"]
    Goal --> B["[AND] Recommendation surfaces without HITL gate"]
    B --> B1["Clinical Summary flows directly to Orchestrator without HITL routing"]
    B --> B2["No risk-threshold classifier routing high-risk outputs to physician review"]
    B --> B3["Recommendation enters patient-facing or decision-critical context directly"]
    Goal --> C["[AND] Clinician or patient acts on unreviewed recommendation"]
    C --> C1["Incorrect drug choice or dose administered"]
    C --> C2["Incorrect diagnostic pathway followed"]
    classDef critical fill:#d32f2f,color:#fff
    class Goal critical
```
