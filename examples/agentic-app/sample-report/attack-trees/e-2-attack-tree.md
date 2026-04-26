# Attack Tree: E-2 — Prompt Injection Self-Authorizes Orchestrator to Perform Elevated Operations

**Finding ID**: E-2
**Risk Level**: Critical
**Component**: LLM Agent Orchestrator
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    E2_root["Self-authorize Orchestrator to perform elevated operations via prompt injection"]
    E2_or1{{"OR"}}
    E2_sub1["Inject instruction causing Orchestrator to initiate full KB corpus export"]
    E2_sub2["Inject instruction causing Orchestrator to invoke out-of-scope tools"]
    E2_sub3["Inject instruction causing Orchestrator to issue unauthorized agent delegation"]
    E2_and1{{"AND"}}
    E2_leaf1["Bypass Guardrails with adversarial payload targeting KB retrieval path"]
    E2_leaf2["Cause Orchestrator to issue exhaustive KB vector search queries"]
    E2_leaf3["Confirm no per-session KB access scope enforced independently by KB service"]
    E2_and2{{"AND"}}
    E2_leaf4["Embed injection payload instructing use of restricted external tool endpoint"]
    E2_leaf5["Confirm Tool Server does not enforce per-session permitted tool scope"]
    E2_leaf6["Execute out-of-scope tool call using Tool Server service credentials"]
    E2_leaf7["Embed instruction causing Orchestrator to issue unauthorized ClinAdvisor delegation"]

    E2_root --> E2_or1
    E2_or1 --> E2_sub1
    E2_or1 --> E2_sub2
    E2_or1 --> E2_sub3
    E2_sub1 --> E2_and1
    E2_and1 --> E2_leaf1
    E2_and1 --> E2_leaf2
    E2_and1 --> E2_leaf3
    E2_sub2 --> E2_and2
    E2_and2 --> E2_leaf4
    E2_and2 --> E2_leaf5
    E2_and2 --> E2_leaf6
    E2_sub3 --> E2_leaf7

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E2_root goal
    class E2_or1 orGate
    class E2_and1,E2_and2 andGate
    class E2_sub1,E2_sub2,E2_sub3 subGoal
    class E2_leaf1,E2_leaf2,E2_leaf3,E2_leaf4,E2_leaf5,E2_leaf6,E2_leaf7 leaf
```
