# Attack Tree: MI-2 — Overreliance / Missing HITL Gate on Decision-Critical Clinical Output

**Finding ID**: MI-2
**Risk Level**: Critical
**Component**: Clinical Advisory Sub-Agent
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    MI2_root["Cause clinical recommendations to surface in patient-facing context without physician sign-off or AI-provenance disclosure"]
    MI2_and1{{"AND"}}
    MI2_sub1["Generate clinical recommendation via ClinAdvisor that reaches user without HITL gate"]
    MI2_sub2["Exploit absence of AI-provenance disclosure to present recommendation as authoritative"]
    MI2_or1{{"OR"}}
    MI2_leaf1["Submit clinical query triggering drug dosing or contraindication recommendation"]
    MI2_leaf2["Craft query in domain where ClinAdvisor routinely produces high-confidence recommendations"]
    MI2_and2{{"AND"}}
    MI2_leaf3["Confirm clinical output flows directly from ClinAdvisor through Orchestrator to User without review gate"]
    MI2_leaf4["Confirm no risk-threshold classification triggers physician confirmation requirement"]
    MI2_leaf5["Clinical recommendation presented to clinician or patient without AI authorship disclosure"]

    MI2_root --> MI2_and1
    MI2_and1 --> MI2_sub1
    MI2_and1 --> MI2_sub2
    MI2_sub1 --> MI2_or1
    MI2_or1 --> MI2_leaf1
    MI2_or1 --> MI2_leaf2
    MI2_sub2 --> MI2_and2
    MI2_and2 --> MI2_leaf3
    MI2_and2 --> MI2_leaf4
    MI2_and2 --> MI2_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class MI2_root goal
    class MI2_and1,MI2_and2 andGate
    class MI2_or1 orGate
    class MI2_sub1,MI2_sub2 subGoal
    class MI2_leaf1,MI2_leaf2,MI2_leaf3,MI2_leaf4,MI2_leaf5 leaf
```
