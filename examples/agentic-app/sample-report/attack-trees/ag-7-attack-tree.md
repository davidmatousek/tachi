# Attack Tree: AG-7 — Training Data Causes Model to Expand Autonomous Action Scope on Next Update

**Finding ID**: AG-7
**Risk Level**: Critical
**Component**: Long-Running Learning Loop
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    AG7_root["Cause model to accumulate unauthorized autonomous capabilities via adversarial training signals"]
    AG7_and1{{"AND"}}
    AG7_sub1["Inject training signals that encode expanded autonomous action scope"]
    AG7_sub2["Bypass capability regression checks on model update evaluation"]
    AG7_or1{{"OR"}}
    AG7_leaf1["Poison Audit Logger with interaction records showing successful unauthorized tool invocations"]
    AG7_leaf2["Craft training examples that reinforce model self-authorization behaviors"]
    AG7_and2{{"AND"}}
    AG7_leaf3["Confirm no post-update capability allowlist evaluation before production deployment"]
    AG7_leaf4["Confirm no behavioral regression suite tests for unauthorized capability expansion"]
    AG7_leaf5["Deploy updated model with expanded autonomous scope to production agents"]

    AG7_root --> AG7_and1
    AG7_and1 --> AG7_sub1
    AG7_and1 --> AG7_sub2
    AG7_sub1 --> AG7_or1
    AG7_or1 --> AG7_leaf1
    AG7_or1 --> AG7_leaf2
    AG7_sub2 --> AG7_and2
    AG7_and2 --> AG7_leaf3
    AG7_and2 --> AG7_leaf4
    AG7_and2 --> AG7_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG7_root goal
    class AG7_and1,AG7_and2 andGate
    class AG7_or1 orGate
    class AG7_sub1,AG7_sub2 subGoal
    class AG7_leaf1,AG7_leaf2,AG7_leaf3,AG7_leaf4,AG7_leaf5 leaf
```
