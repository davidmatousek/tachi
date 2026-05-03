# Attack Tree: E-1 — Privilege escalation via prompt-manipulated tool calls

| Field | Value |
|-------|-------|
| Finding ID | E-1 |
| Component | LLM Agent Orchestrator |
| Risk Level | High |
| Threat | Privilege escalation via prompt-manipulated tool calls |
| Correlation | None |

```mermaid
flowchart TD
    E1_root["Escalate to admin capabilities via prompt manipulation"]
    E1_or1{{"OR"}}
    E1_sub1["Directly request privileged tool invocation"]
    E1_sub2["Indirectly trick orchestrator into privileged action"]
    E1_and1{{"AND"}}
    E1_leaf1["Identify privileged tools available in orchestrator inventory"]
    E1_leaf2["Craft prompt requesting administrative tool execution"]
    E1_leaf3["Exploit missing authorization check at tool dispatch"]
    E1_leaf4["Embed privileged action request within legitimate task context"]
    E1_leaf5["Cause orchestrator to select privileged tool as part of reasoning chain"]

    E1_root --> E1_or1
    E1_or1 --> E1_sub1
    E1_or1 --> E1_sub2
    E1_sub1 --> E1_and1
    E1_and1 --> E1_leaf1
    E1_and1 --> E1_leaf2
    E1_and1 --> E1_leaf3
    E1_sub2 --> E1_leaf4
    E1_sub2 --> E1_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333

    class E1_root goal
    class E1_or1 orGate
    class E1_and1 andGate
    class E1_sub1,E1_sub2 subGoal
    class E1_leaf1,E1_leaf2,E1_leaf3,E1_leaf4,E1_leaf5 leaf
```
