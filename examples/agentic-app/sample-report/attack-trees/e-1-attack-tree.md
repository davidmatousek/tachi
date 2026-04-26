# Attack Tree: E-1 — Prompt Injection Bypass Elevates Attacker to Trusted Orchestrator Caller

**Finding ID**: E-1
**Risk Level**: Critical
**Component**: Guardrails Service
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    E1_root["Elevate attacker from unauthenticated user to trusted Orchestrator caller via Guardrails bypass"]
    E1_and1{{"AND"}}
    E1_sub1["Craft adversarial prompt that evades Guardrails filtering"]
    E1_sub2["Exploit Orchestrator's implicit trust in Guardrails-passed inputs"]
    E1_or1{{"OR"}}
    E1_leaf1["Identify filtering rule gaps through iterative probing of rejection patterns"]
    E1_leaf2["Encode adversarial instructions using encoding Guardrails does not normalize"]
    E1_leaf3["Embed injection payload in content type Guardrails does not evaluate"]
    E1_and2{{"AND"}}
    E1_leaf4["Confirm Orchestrator treats all Guardrails-passed inputs as implicitly trusted"]
    E1_leaf5["Submit injection payload causing Orchestrator to execute attacker instructions"]
    E1_leaf6["Achieve Orchestrator-level access to KB retrieval, tool calls, and agent delegation"]

    E1_root --> E1_and1
    E1_and1 --> E1_sub1
    E1_and1 --> E1_sub2
    E1_sub1 --> E1_or1
    E1_or1 --> E1_leaf1
    E1_or1 --> E1_leaf2
    E1_or1 --> E1_leaf3
    E1_sub2 --> E1_and2
    E1_and2 --> E1_leaf4
    E1_and2 --> E1_leaf5
    E1_and2 --> E1_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E1_root goal
    class E1_and1,E1_and2 andGate
    class E1_or1 orGate
    class E1_sub1,E1_sub2 subGoal
    class E1_leaf1,E1_leaf2,E1_leaf3,E1_leaf4,E1_leaf5,E1_leaf6 leaf
```
