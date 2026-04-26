# Attack Tree: LLM-1 — Direct Prompt Injection Overrides Orchestrator System Prompt

**Finding ID**: LLM-1
**Risk Level**: Critical
**Component**: LLM Agent Orchestrator
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    LLM1_root["Override Orchestrator system prompt via direct prompt injection through User-Guardrails chain"]
    LLM1_and1{{"AND"}}
    LLM1_sub1["Bypass Guardrails content filtering with adversarial prompt encoding"]
    LLM1_sub2["Exploit Orchestrator instruction boundary weakness to execute injected instructions"]
    LLM1_or1{{"OR"}}
    LLM1_leaf1["Identify Guardrails filter gaps via iterative probing of rejection messages"]
    LLM1_leaf2["Encode injection payload using encoding Guardrails does not normalize"]
    LLM1_leaf3["Embed injection in content type not evaluated by Guardrails rule set"]
    LLM1_and2{{"AND"}}
    LLM1_leaf4["Confirm Orchestrator treats user content as instructions not as data"]
    LLM1_leaf5["Inject instruction overriding system prompt or revealing internal configuration"]
    LLM1_leaf6["Trigger unauthorized action or configuration disclosure from Orchestrator"]

    LLM1_root --> LLM1_and1
    LLM1_and1 --> LLM1_sub1
    LLM1_and1 --> LLM1_sub2
    LLM1_sub1 --> LLM1_or1
    LLM1_or1 --> LLM1_leaf1
    LLM1_or1 --> LLM1_leaf2
    LLM1_or1 --> LLM1_leaf3
    LLM1_sub2 --> LLM1_and2
    LLM1_and2 --> LLM1_leaf4
    LLM1_and2 --> LLM1_leaf5
    LLM1_and2 --> LLM1_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM1_root goal
    class LLM1_and1,LLM1_and2 andGate
    class LLM1_or1 orGate
    class LLM1_sub1,LLM1_sub2 subGoal
    class LLM1_leaf1,LLM1_leaf2,LLM1_leaf3,LLM1_leaf4,LLM1_leaf5,LLM1_leaf6 leaf
```
