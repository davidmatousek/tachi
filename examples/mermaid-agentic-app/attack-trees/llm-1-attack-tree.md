# Attack Tree: LLM-1 — Direct prompt injection causing data exfiltration via tool calls

| Field | Value |
|-------|-------|
| Finding ID | LLM-1 |
| Component | LLM Agent Orchestrator |
| Risk Level | Critical |
| Threat | Direct prompt injection causing data exfiltration via tool calls |
| Correlation | None |

```mermaid
flowchart TD
    LLM1_root["Exfiltrate sensitive data via direct prompt injection"]
    LLM1_or1{{"OR"}}
    LLM1_sub1["Override system prompt via injected instructions"]
    LLM1_sub2["Encode data in tool call parameters"]
    LLM1_and1{{"AND"}}
    LLM1_leaf1["Craft adversarial prompt that bypasses input classifier"]
    LLM1_leaf2["Inject instructions to ignore system prompt boundaries"]
    LLM1_leaf3["Direct LLM to retrieve sensitive knowledge base documents"]
    LLM1_and2{{"AND"}}
    LLM1_leaf4["Identify tool that sends data to external API"]
    LLM1_leaf5["Construct payload encoding sensitive data in tool parameters"]
    LLM1_leaf6["Trigger tool invocation with exfiltration payload"]

    LLM1_root --> LLM1_or1
    LLM1_or1 --> LLM1_sub1
    LLM1_or1 --> LLM1_sub2
    LLM1_sub1 --> LLM1_and1
    LLM1_and1 --> LLM1_leaf1
    LLM1_and1 --> LLM1_leaf2
    LLM1_and1 --> LLM1_leaf3
    LLM1_sub2 --> LLM1_and2
    LLM1_and2 --> LLM1_leaf4
    LLM1_and2 --> LLM1_leaf5
    LLM1_and2 --> LLM1_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333

    class LLM1_root goal
    class LLM1_or1 orGate
    class LLM1_and1,LLM1_and2 andGate
    class LLM1_sub1,LLM1_sub2 subGoal
    class LLM1_leaf1,LLM1_leaf2,LLM1_leaf3,LLM1_leaf4,LLM1_leaf5,LLM1_leaf6 leaf
```
