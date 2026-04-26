# Attack Tree: R-9 — ClinAdvisor Denies Generating Specific Clinical Summary Without Non-Repudiable Log

**Finding ID**: R-9
**Risk Level**: High
**Component**: Clinical Advisory Sub-Agent
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    R9_root["Deny ClinAdvisor generated specific clinical summary or used particular KB documents without non-repudiable log"]
    R9_or1{{"OR"}}
    R9_sub1["Exploit missing pre-return clinical output logging to deny recommendation occurred"]
    R9_sub2["Tamper with Clinical Decision Log entries to alter recorded clinical outputs"]
    R9_leaf1["Confirm ClinAdvisor does not log clinical summary hash and KB document IDs atomically before returning"]
    R9_leaf2["Cause ClinAdvisor to produce high-impact clinical recommendation lacking signed attribution log"]
    R9_leaf3["Deny having generated the recommendation when clinical harm or dispute arises"]
    R9_and1{{"AND"}}
    R9_leaf4["Gain write access to Clinical Decision Log entries in Audit Logger"]
    R9_leaf5["Modify or delete log entries concealing KB documents used or clinical content produced"]

    R9_root --> R9_or1
    R9_or1 --> R9_sub1
    R9_or1 --> R9_sub2
    R9_sub1 --> R9_leaf1
    R9_sub1 --> R9_leaf2
    R9_sub1 --> R9_leaf3
    R9_sub2 --> R9_and1
    R9_and1 --> R9_leaf4
    R9_and1 --> R9_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class R9_root goal
    class R9_or1 orGate
    class R9_and1 andGate
    class R9_sub1,R9_sub2 subGoal
    class R9_leaf1,R9_leaf2,R9_leaf3,R9_leaf4,R9_leaf5 leaf
```
