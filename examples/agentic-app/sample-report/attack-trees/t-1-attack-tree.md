# Attack Tree: T-1 -- Guardrails Configuration Tampering

| Field | Value |
|-------|-------|
| Finding ID | T-1 |
| Component | Guardrails Service |
| Risk Level | High |
| Threat | Guardrails Configuration Tampering |
| Correlation | None |

```mermaid
flowchart TD
    T1_root["Modify Guardrails filtering rules to allow malicious prompts"]
    T1_or1{{"OR"}}
    T1_sub1["Direct configuration file modification"]
    T1_sub2["Exploit deployment pipeline to inject modified rules"]
    T1_and1{{"AND"}}
    T1_leaf1["Gain write access to configuration storage"]
    T1_leaf2["Modify validation rules to weaken filtering"]
    T1_leaf3["Changes take effect without integrity check"]
    T1_leaf4["Compromise CI/CD pipeline credentials"]
    T1_leaf5["Push tampered configuration through deployment"]

    T1_root --> T1_or1
    T1_or1 --> T1_sub1
    T1_or1 --> T1_sub2
    T1_sub1 --> T1_and1
    T1_and1 --> T1_leaf1
    T1_and1 --> T1_leaf2
    T1_and1 --> T1_leaf3
    T1_sub2 --> T1_leaf4
    T1_sub2 --> T1_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T1_root goal
    class T1_or1 orGate
    class T1_and1 andGate
    class T1_sub1,T1_sub2 subGoal
    class T1_leaf1,T1_leaf2,T1_leaf3,T1_leaf4,T1_leaf5 leaf
```
