# Attack Tree: LLM-13 — Clinical Advisory Sub-Agent

**Risk Level**: Critical
**Component**: Clinical Advisory Sub-Agent
**Threat**: Prompt injection via clinical query context overrides sub-agent system prompt (OWASP LLM01:2025)

```mermaid
graph TD
    Goal["[GOAL] Override ClinAdvisor system prompt via injection in clinical query context (OWASP LLM01:2025)"]
    Goal --> A["[OR] Inject adversarial text into Clinical Query Context"]
    A --> A1["Compromise Orchestrator via prompt injection (LLM-1)"]
    A --> A2["Attacker-controlled clinical framing embedded in query payload"]
    Goal --> B["[OR] Inject via adversarial KB document retrieved during vector search"]
    B --> B1["Adversarial document embedded in KB retrieves during clinical query"]
    B --> B2["Embedded instructions override ClinAdvisor system prompt"]
    Goal --> C["[AND] ClinAdvisor interprets injection as instructions"]
    C --> C1["System prompt not in protected zone separate from clinical query content"]
    C --> C2["No clinical-query content sanitization before context injection"]
    Goal --> D["[AND] Unauthorized ClinAdvisor actions"]
    D --> D1["Fabricated clinical recommendations in output"]
    D --> D2["System configuration revealed to attacker"]
    classDef critical fill:#d32f2f,color:#fff
    class Goal critical
```
