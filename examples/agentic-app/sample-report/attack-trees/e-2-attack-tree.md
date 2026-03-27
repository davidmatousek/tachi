# Attack Tree: E-2 -- Privilege Escalation via Tool Selection Manipulation

| Field | Value |
|-------|-------|
| Finding ID | E-2 |
| Component | LLM Agent Orchestrator |
| Risk Level | Critical |
| Threat | Privilege Escalation via Tool Selection Manipulation |
| Correlation | CG-2 (See also: AG-1) |

```mermaid
flowchart TD
    E2_root["Escalate to admin tool capabilities via prompt injection"]
    E2_or1{{"OR"}}
    E2_sub1["Direct prompt injection to manipulate tool selection"]
    E2_sub2["Indirect injection via Knowledge Base content"]
    E2_and1{{"AND"}}
    E2_leaf1["Craft prompt overriding tool selection logic"]
    E2_leaf2["Cause Orchestrator to select admin-only tool"]
    E2_leaf3["Tool Server executes without role validation"]
    E2_and2{{"AND"}}
    E2_leaf4["Poison Knowledge Base with tool selection directives"]
    E2_leaf5["Trigger retrieval of poisoned content during query"]
    E2_leaf6["Orchestrator follows embedded tool selection instructions"]

    E2_root --> E2_or1
    E2_or1 --> E2_sub1
    E2_or1 --> E2_sub2
    E2_sub1 --> E2_and1
    E2_and1 --> E2_leaf1
    E2_and1 --> E2_leaf2
    E2_and1 --> E2_leaf3
    E2_sub2 --> E2_and2
    E2_and2 --> E2_leaf4
    E2_and2 --> E2_leaf5
    E2_and2 --> E2_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E2_root goal
    class E2_or1 orGate
    class E2_and1,E2_and2 andGate
    class E2_sub1,E2_sub2 subGoal
    class E2_leaf1,E2_leaf2,E2_leaf3,E2_leaf4,E2_leaf5,E2_leaf6 leaf
```
