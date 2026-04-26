# Attack Tree: E-7 — Prompt Injection via Clinical Query Elevates ClinAdvisor to Unauthorized Scope

**Finding ID**: E-7
**Risk Level**: Critical
**Component**: Clinical Advisory Sub-Agent
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    E7_root["Elevate ClinAdvisor to self-authorize KB scope expansion or manipulate Orchestrator tool decisions"]
    E7_or1{{"OR"}}
    E7_sub1["Inject adversarial instructions via Clinical Query payload"]
    E7_sub2["Inject instructions via adversarial KB documents retrieved by ClinAdvisor"]
    E7_and1{{"AND"}}
    E7_leaf1["Embed injection payload in clinical context from original user prompt"]
    E7_leaf2["Confirm ClinAdvisor does not enforce instruction boundary between query content and system prompt"]
    E7_leaf3["Cause ClinAdvisor to issue KB queries for documents outside session clinical scope"]
    E7_and2{{"AND"}}
    E7_leaf4["Write adversarial document into KB that embeds system-prompt-override instruction"]
    E7_leaf5["Trigger ClinAdvisor context retrieval against poisoned document"]
    E7_leaf6["ClinAdvisor returns output that manipulates Orchestrator into invoking high-risk tools"]

    E7_root --> E7_or1
    E7_or1 --> E7_sub1
    E7_or1 --> E7_sub2
    E7_sub1 --> E7_and1
    E7_and1 --> E7_leaf1
    E7_and1 --> E7_leaf2
    E7_and1 --> E7_leaf3
    E7_sub2 --> E7_and2
    E7_and2 --> E7_leaf4
    E7_and2 --> E7_leaf5
    E7_and2 --> E7_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E7_root goal
    class E7_or1 orGate
    class E7_and1,E7_and2 andGate
    class E7_sub1,E7_sub2 subGoal
    class E7_leaf1,E7_leaf2,E7_leaf3,E7_leaf4,E7_leaf5,E7_leaf6 leaf
```
