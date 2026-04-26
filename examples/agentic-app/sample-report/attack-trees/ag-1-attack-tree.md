# Attack Tree: AG-1 — Prompt Injection Causes Autonomous Unauthorized High-Impact Actions

**Finding ID**: AG-1
**Risk Level**: Critical
**Component**: LLM Agent Orchestrator
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    AG1_root["Execute unauthorized high-impact autonomous actions via prompt injection into Orchestrator"]
    AG1_or1{{"OR"}}
    AG1_sub1["Exploit missing scope-enforcement layer on proposed actions"]
    AG1_sub2["Bypass human-in-the-loop gate for high-impact operations"]
    AG1_and1{{"AND"}}
    AG1_leaf1["Craft adversarial prompt that passes Guardrails and reaches Orchestrator"]
    AG1_leaf2["Embed instruction causing Orchestrator to propose mass KB data exfiltration"]
    AG1_leaf3["Confirm no policy engine evaluates and rejects the proposed action plan"]
    AG1_and2{{"AND"}}
    AG1_leaf4["Identify high-impact tool operation not gated by HITL confirmation"]
    AG1_leaf5["Craft prompt triggering the ungated high-impact operation autonomously"]
    AG1_leaf6["Execute irreversible bulk external write or data exfiltration without approval"]

    AG1_root --> AG1_or1
    AG1_or1 --> AG1_sub1
    AG1_or1 --> AG1_sub2
    AG1_sub1 --> AG1_and1
    AG1_and1 --> AG1_leaf1
    AG1_and1 --> AG1_leaf2
    AG1_and1 --> AG1_leaf3
    AG1_sub2 --> AG1_and2
    AG1_and2 --> AG1_leaf4
    AG1_and2 --> AG1_leaf5
    AG1_and2 --> AG1_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG1_root goal
    class AG1_or1 orGate
    class AG1_and1,AG1_and2 andGate
    class AG1_sub1,AG1_sub2 subGoal
    class AG1_leaf1,AG1_leaf2,AG1_leaf3,AG1_leaf4,AG1_leaf5,AG1_leaf6 leaf
```
