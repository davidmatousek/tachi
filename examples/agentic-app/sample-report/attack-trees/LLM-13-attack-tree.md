# Attack Tree: LLM-13 — Prompt Injection via Clinical Query Context Overrides ClinAdvisor System Prompt

**Finding ID**: LLM-13
**Risk Level**: Critical
**Component**: Clinical Advisory Sub-Agent
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    LLM13_root["Override ClinAdvisor system prompt via prompt injection in clinical query context"]
    LLM13_or1{{"OR"}}
    LLM13_sub1["Inject via original user prompt embedded in Clinical Query payload"]
    LLM13_sub2["Inject via adversarial KB documents incorporated into ClinAdvisor context"]
    LLM13_and1{{"AND"}}
    LLM13_leaf1["Embed adversarial instruction in user prompt that propagates through Guardrails and Orchestrator"]
    LLM13_leaf2["Orchestrator includes attacker-controlled framing in Clinical Query forwarded to ClinAdvisor"]
    LLM13_leaf3["Confirm ClinAdvisor has no instruction boundary between query content and system prompt"]
    LLM13_and2{{"AND"}}
    LLM13_leaf4["Write adversarial document into KB embedding system-prompt-override instruction"]
    LLM13_leaf5["Trigger ClinAdvisor to retrieve adversarial document during clinical context assembly"]
    LLM13_leaf6["Injected instruction causes ClinAdvisor to reveal configuration or fabricate clinical claims"]

    LLM13_root --> LLM13_or1
    LLM13_or1 --> LLM13_sub1
    LLM13_or1 --> LLM13_sub2
    LLM13_sub1 --> LLM13_and1
    LLM13_and1 --> LLM13_leaf1
    LLM13_and1 --> LLM13_leaf2
    LLM13_and1 --> LLM13_leaf3
    LLM13_sub2 --> LLM13_and2
    LLM13_and2 --> LLM13_leaf4
    LLM13_and2 --> LLM13_leaf5
    LLM13_and2 --> LLM13_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM13_root goal
    class LLM13_or1 orGate
    class LLM13_and1,LLM13_and2 andGate
    class LLM13_sub1,LLM13_sub2 subGoal
    class LLM13_leaf1,LLM13_leaf2,LLM13_leaf3,LLM13_leaf4,LLM13_leaf5,LLM13_leaf6 leaf
```
