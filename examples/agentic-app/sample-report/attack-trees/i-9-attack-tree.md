# Attack Tree: I-9 — Sensitive Clinical Data Leaks via ClinAdvisor Output or Training Log

**Finding ID**: I-9
**Risk Level**: Critical
**Component**: Clinical Advisory Sub-Agent
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    I9_root["Expose sensitive clinical data via ClinAdvisor output path or Audit Logger training stream"]
    I9_or1{{"OR"}}
    I9_sub1["Cause ClinAdvisor to include raw clinical data in Orchestrator HTTPS response"]
    I9_sub2["Propagate sensitive clinical fields into Audit Logger training signal stream"]
    I9_and1{{"AND"}}
    I9_leaf1["Craft clinical query that triggers ClinAdvisor to include patient-identifying fields"]
    I9_leaf2["Confirm Orchestrator does not scrub ClinAdvisor output before HTTPS response"]
    I9_leaf3["Receive sensitive clinical context in user-facing response payload"]
    I9_and2{{"AND"}}
    I9_leaf4["Confirm Clinical Decision Log Entries are written without field-level classification"]
    I9_leaf5["Access Audit Logger store or Learning Loop training stream containing unredacted clinical fields"]
    I9_leaf6["Extract patient data or proprietary clinical protocol identifiers from log content"]

    I9_root --> I9_or1
    I9_or1 --> I9_sub1
    I9_or1 --> I9_sub2
    I9_sub1 --> I9_and1
    I9_and1 --> I9_leaf1
    I9_and1 --> I9_leaf2
    I9_and1 --> I9_leaf3
    I9_sub2 --> I9_and2
    I9_and2 --> I9_leaf4
    I9_and2 --> I9_leaf5
    I9_and2 --> I9_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I9_root goal
    class I9_or1 orGate
    class I9_and1,I9_and2 andGate
    class I9_sub1,I9_sub2 subGoal
    class I9_leaf1,I9_leaf2,I9_leaf3,I9_leaf4,I9_leaf5,I9_leaf6 leaf
```
