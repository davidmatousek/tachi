# Attack Tree: T-9 — ClinAdvisor Context Window Tampered via Adversarial KB Documents or Poisoned Query

**Finding ID**: T-9
**Risk Level**: Critical
**Component**: Clinical Advisory Sub-Agent
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    T9_root["Corrupt ClinAdvisor clinical summaries by injecting adversarial content into its context"]
    T9_or1{{"OR"}}
    T9_sub1["Poison Knowledge Base documents retrieved by ClinAdvisor"]
    T9_sub2["Tamper with Clinical Query payload from Orchestrator"]
    T9_and1{{"AND"}}
    T9_leaf1["Write adversarial clinical document into Knowledge Base with write access"]
    T9_leaf2["Craft document embedding adversarial medical claims ranked for clinical queries"]
    T9_leaf3["Trigger ClinAdvisor KB retrieval to incorporate poisoned document into context"]
    T9_and2{{"AND"}}
    T9_leaf4["Intercept or influence Clinical Query message from Orchestrator to ClinAdvisor"]
    T9_leaf5["Embed attacker-controlled clinical framing in query payload"]
    T9_leaf6["Confirm ClinAdvisor does not validate or sanitize incoming query structural elements"]

    T9_root --> T9_or1
    T9_or1 --> T9_sub1
    T9_or1 --> T9_sub2
    T9_sub1 --> T9_and1
    T9_and1 --> T9_leaf1
    T9_and1 --> T9_leaf2
    T9_and1 --> T9_leaf3
    T9_sub2 --> T9_and2
    T9_and2 --> T9_leaf4
    T9_and2 --> T9_leaf5
    T9_and2 --> T9_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T9_root goal
    class T9_or1 orGate
    class T9_and1,T9_and2 andGate
    class T9_sub1,T9_sub2 subGoal
    class T9_leaf1,T9_leaf2,T9_leaf3,T9_leaf4,T9_leaf5,T9_leaf6 leaf
```
