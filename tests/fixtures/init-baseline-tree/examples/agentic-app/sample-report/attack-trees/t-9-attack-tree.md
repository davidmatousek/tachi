# Attack Tree: T-9 — Clinical Advisory Sub-Agent

**Risk Level**: Critical
**Component**: Clinical Advisory Sub-Agent
**Threat**: Dual-path context window poisoning via KB and clinical query payload

```mermaid
graph TD
    Goal["[GOAL] Corrupt Clinical Advisory Sub-Agent context to fabricate malicious clinical summaries"]
    Goal --> A["[OR] Path 1: Adversarial KB document retrieval"]
    A --> A1["Inject adversarial documents into KB corpus (T-6)"]
    A --> A2["ClinAdvisor retrieves during vector search without integrity check"]
    Goal --> B["[OR] Path 2: Tampered Clinical Query Context from Orchestrator"]
    B --> B1["Attacker influences Orchestrator via prompt injection (LLM-1)"]
    B --> B2["Orchestrator embeds adversarial clinical framing in query payload"]
    B --> B3["ClinAdvisor does not validate clinical query content"]
    Goal --> C["[AND] Adversarial content incorporated into clinical summary"]
    C --> C1["Fabricated clinical recommendation returned to Orchestrator"]
    C --> C2["Malicious recommendation enters user-facing response path"]
    classDef critical fill:#d32f2f,color:#fff
    class Goal critical
```
