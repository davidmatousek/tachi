# Attack Tree: OI-4 — Clinical Advisory Sub-Agent

**Risk Level**: High
**Component**: Clinical Advisory Sub-Agent
**Threat**: Server-side execution via clinical summary injected into Orchestrator Tool Call Request (OWASP LLM05:2025)

```mermaid
graph TD
    Goal["[GOAL] Achieve server-side execution via adversarial clinical output injected into downstream Tool Call Request (OWASP LLM05:2025)"]
    Goal --> A["[OR] Inject adversarial content into ClinAdvisor Clinical Summary"]
    A --> A1["Compromise ClinAdvisor via prompt injection (LLM-13)"]
    A --> A2["Adversarial KB document causes adversarial clinical recommendation text"]
    Goal --> B["[AND] Orchestrator incorporates clinical output into Tool Call Request without sanitization"]
    B --> B1["Orchestrator embeds clinical recommendation text directly in JSON-RPC tool parameter"]
    B --> B2["No output sanitization on ClinAdvisor output before Orchestrator tool invocation"]
    Goal --> C["[AND] Tool Server executes parameter from clinical summary without validation"]
    C --> C1["No JSON Schema validation on parameters derived from clinical outputs"]
    C --> C2["Injection payload in clinical text achieves server-side execution"]
    classDef high fill:#e65100,color:#fff
    class Goal high
```
