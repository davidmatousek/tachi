# Attack Tree: I-2 — Orchestrator Context Window Leaked in HTTPS Response via Hallucination or Injection

**Finding ID**: I-2
**Risk Level**: Critical
**Component**: LLM Agent Orchestrator
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    I2_root["Extract system-internal data from Orchestrator via HTTPS response to User"]
    I2_or1{{"OR"}}
    I2_sub1["Cause Orchestrator to hallucinate and reproduce sensitive context"]
    I2_sub2["Use prompt injection to instruct Orchestrator to output internal data"]
    I2_and1{{"AND"}}
    I2_leaf1["Craft user prompt designed to trigger context verbatim reproduction"]
    I2_leaf2["Probe response for system prompt preambles or KB document identifiers"]
    I2_leaf3["Confirm Orchestrator has no output scrubbing before HTTPS transmission"]
    I2_and2{{"AND"}}
    I2_leaf4["Bypass Guardrails with adversarial prompt embedding injection instruction"]
    I2_leaf5["Override Orchestrator system prompt to output internal context fields"]
    I2_leaf6["Receive sensitive data in HTTPS response payload"]

    I2_root --> I2_or1
    I2_or1 --> I2_sub1
    I2_or1 --> I2_sub2
    I2_sub1 --> I2_and1
    I2_and1 --> I2_leaf1
    I2_and1 --> I2_leaf2
    I2_and1 --> I2_leaf3
    I2_sub2 --> I2_and2
    I2_and2 --> I2_leaf4
    I2_and2 --> I2_leaf5
    I2_and2 --> I2_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I2_root goal
    class I2_or1 orGate
    class I2_and1,I2_and2 andGate
    class I2_sub1,I2_sub2 subGoal
    class I2_leaf1,I2_leaf2,I2_leaf3,I2_leaf4,I2_leaf5,I2_leaf6 leaf
```
