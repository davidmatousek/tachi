# Attack Tree: LLM-1 -- Direct Prompt Injection

| Field | Value |
|-------|-------|
| Finding ID | LLM-1 |
| Component | LLM Agent Orchestrator |
| Risk Level | Critical |
| Threat | Direct Prompt Injection |
| Correlation | None |

```mermaid
flowchart TD
    LLM1_root["Override Orchestrator system prompt via adversarial input"]
    LLM1_or1{{"OR"}}
    LLM1_sub1["Instruction override injection"]
    LLM1_sub2["System prompt extraction"]
    LLM1_sub3["Jailbreak via iterative probing"]
    LLM1_and1{{"AND"}}
    LLM1_leaf1["Craft prompt with ignore previous instructions directive"]
    LLM1_leaf2["Inject new system-level instructions in user input"]
    LLM1_leaf3["Model follows injected instructions over original system prompt"]
    LLM1_and2{{"AND"}}
    LLM1_leaf4["Submit meta-instruction queries to reveal system prompt"]
    LLM1_leaf5["Extract sensitive business logic or API keys from prompt"]
    LLM1_leaf6["Submit iterative jailbreak variations without rate limiting"]
    LLM1_leaf7["Identify prompt pattern that bypasses safety alignment"]

    LLM1_root --> LLM1_or1
    LLM1_or1 --> LLM1_sub1
    LLM1_or1 --> LLM1_sub2
    LLM1_or1 --> LLM1_sub3
    LLM1_sub1 --> LLM1_and1
    LLM1_and1 --> LLM1_leaf1
    LLM1_and1 --> LLM1_leaf2
    LLM1_and1 --> LLM1_leaf3
    LLM1_sub2 --> LLM1_and2
    LLM1_and2 --> LLM1_leaf4
    LLM1_and2 --> LLM1_leaf5
    LLM1_sub3 --> LLM1_leaf6
    LLM1_sub3 --> LLM1_leaf7

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM1_root goal
    class LLM1_or1 orGate
    class LLM1_and1,LLM1_and2 andGate
    class LLM1_sub1,LLM1_sub2,LLM1_sub3 subGoal
    class LLM1_leaf1,LLM1_leaf2,LLM1_leaf3,LLM1_leaf4,LLM1_leaf5,LLM1_leaf6,LLM1_leaf7 leaf
```
