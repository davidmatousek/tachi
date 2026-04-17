# Attack Tree: T-16 — Outcomes Telemetry Learning Loop Poisoning

**Component**: Outcomes Telemetry and Physician Override Audit Store | **Risk Level**: Critical | **Finding**: T-16

An attacker tampers with the Outcomes Telemetry store, injecting adversarial physician-override signals that corrupt the learning loop re-training process and cause model drift toward attacker-preferred outputs.

```mermaid
flowchart TD
    T16_root["Cause Clinical LLM model drift toward attacker-preferred outputs via telemetry store poisoning"]
    T16_or1{{"OR"}}
    T16_sub1["Inject false physician-override signals into Outcomes Telemetry store"]
    T16_sub2["Corrupt existing physician override records to flip endorsement signals"]
    T16_and1{{"AND"}}
    T16_and2{{"AND"}}
    T16_leaf1["Obtain write access to Outcomes Telemetry store without physician identity verification"]
    T16_leaf2["Identify high-risk recommendation categories to target for systematic drift"]
    T16_leaf3["Inject adversarial override records indicating false physician approval across multiple sessions"]
    T16_leaf4["Identify existing override records in store without write-access restriction"]
    T16_leaf5["Modify endorsement fields to reverse physician rejection signals to approvals"]
    T16_leaf6["Wait for next scheduled learning loop re-training cycle to incorporate poisoned signals"]

    T16_root --> T16_or1
    T16_or1 --> T16_sub1
    T16_or1 --> T16_sub2
    T16_sub1 --> T16_and1
    T16_and1 --> T16_leaf1
    T16_and1 --> T16_leaf2
    T16_and1 --> T16_leaf3
    T16_sub2 --> T16_and2
    T16_and2 --> T16_leaf4
    T16_and2 --> T16_leaf5
    T16_and2 --> T16_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T16_root goal
    class T16_and1,T16_and2 andGate
    class T16_or1 orGate
    class T16_sub1,T16_sub2 subGoal
    class T16_leaf1,T16_leaf2,T16_leaf3,T16_leaf4,T16_leaf5,T16_leaf6 leaf
```
