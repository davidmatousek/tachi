# Attack Tree: LLM-4 — Training Data Poisoning of Orchestrator via Audit Logger-Fed Learning Loop

**Finding ID**: LLM-4
**Risk Level**: Critical
**Component**: LLM Agent Orchestrator
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    LLM4_root["Shift Orchestrator future behavior by poisoning its training data via Learning Loop update cycle"]
    LLM4_and1{{"AND"}}
    LLM4_sub1["Inject adversarial interaction records into Audit Logger"]
    LLM4_sub2["Ensure poisoned records influence next Learning Loop training run"]
    LLM4_or1{{"OR"}}
    LLM4_leaf1["Gain write access to Audit Logger as compromised Application Zone process"]
    LLM4_leaf2["Craft user sessions designed to generate adversarial log entries via normal system operation"]
    LLM4_and2{{"AND"}}
    LLM4_leaf3["Confirm Learning Loop does not verify data provenance or source signatures"]
    LLM4_leaf4["Time adversarial injection to precede scheduled training run"]
    LLM4_leaf5["Poisoned training data shifts Orchestrator behavior toward attacker-preferred outputs after update"]

    LLM4_root --> LLM4_and1
    LLM4_and1 --> LLM4_sub1
    LLM4_and1 --> LLM4_sub2
    LLM4_sub1 --> LLM4_or1
    LLM4_or1 --> LLM4_leaf1
    LLM4_or1 --> LLM4_leaf2
    LLM4_sub2 --> LLM4_and2
    LLM4_and2 --> LLM4_leaf3
    LLM4_and2 --> LLM4_leaf4
    LLM4_and2 --> LLM4_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM4_root goal
    class LLM4_and1,LLM4_and2 andGate
    class LLM4_or1 orGate
    class LLM4_sub1,LLM4_sub2 subGoal
    class LLM4_leaf1,LLM4_leaf2,LLM4_leaf3,LLM4_leaf4,LLM4_leaf5 leaf
```
