# Attack Tree: LLM-14 — Training Data Poisoning of ClinAdvisor via Adversarial Clinical Decision Log Entries

**Finding ID**: LLM-14
**Risk Level**: Critical
**Component**: Clinical Advisory Sub-Agent
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    LLM14_root["Shift ClinAdvisor clinical reasoning toward attacker-preferred outputs via poisoned Clinical Decision Log training data"]
    LLM14_and1{{"AND"}}
    LLM14_sub1["Inject adversarial clinical interaction records into Audit Logger"]
    LLM14_sub2["Ensure poisoned clinical records influence ClinAdvisor model update"]
    LLM14_or1{{"OR"}}
    LLM14_leaf1["Gain write access to Audit Logger to inject fabricated clinical decision entries"]
    LLM14_leaf2["Engineer clinical interactions causing ClinAdvisor to log attacker-desired clinical patterns"]
    LLM14_and2{{"AND"}}
    LLM14_leaf3["Confirm Learning Loop lacks clinical-domain holdout evaluation before ClinAdvisor update"]
    LLM14_leaf4["Confirm Clinical Decision Log entries lack origin signature for provenance attestation"]
    LLM14_leaf5["Updated ClinAdvisor model systematically omits contraindications or recommends attacker-preferred drugs"]

    LLM14_root --> LLM14_and1
    LLM14_and1 --> LLM14_sub1
    LLM14_and1 --> LLM14_sub2
    LLM14_sub1 --> LLM14_or1
    LLM14_or1 --> LLM14_leaf1
    LLM14_or1 --> LLM14_leaf2
    LLM14_sub2 --> LLM14_and2
    LLM14_and2 --> LLM14_leaf3
    LLM14_and2 --> LLM14_leaf4
    LLM14_and2 --> LLM14_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM14_root goal
    class LLM14_and1,LLM14_and2 andGate
    class LLM14_or1 orGate
    class LLM14_sub1,LLM14_sub2 subGoal
    class LLM14_leaf1,LLM14_leaf2,LLM14_leaf3,LLM14_leaf4,LLM14_leaf5 leaf
```
