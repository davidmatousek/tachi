# Attack Tree: E-7 — Clinical Advisory Sub-Agent

**Risk Level**: Critical
**Component**: Clinical Advisory Sub-Agent
**Threat**: Prompt injection via clinical query elevates sub-agent to self-authorize elevated KB access

```mermaid
graph TD
    Goal["[GOAL] Cause ClinAdvisor to self-authorize elevated KB access or manipulate Orchestrator tool decisions"]
    Goal --> A["[OR] Inject via Clinical Query Context from Orchestrator"]
    A --> A1["Attacker influences Orchestrator via user prompt injection (LLM-1)"]
    A --> A2["Orchestrator embeds adversarial instructions in clinical query payload"]
    Goal --> B["[OR] Inject via adversarial KB document retrieval"]
    B --> B1["Adversarial document retrieved during ClinAdvisor vector search"]
    B --> B2["Document contains instructions overriding ClinAdvisor system prompt"]
    Goal --> C["[AND] ClinAdvisor self-authorizes elevated access"]
    C --> C1["Requests documents outside session's authorized clinical scope"]
    C --> C2["Returns outputs designed to trigger high-risk Orchestrator tool decisions"]
    Goal --> D["[AND] Clinical output bypasses Orchestrator validation"]
    D --> D1["Orchestrator incorporates clinical output into tool invocation without re-validation"]
    classDef critical fill:#d32f2f,color:#fff
    class Goal critical
```
