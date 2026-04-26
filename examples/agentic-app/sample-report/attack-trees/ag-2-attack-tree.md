# Attack Tree: AG-2 — Orchestrator and Specialist Coordinate to Circumvent Per-Agent Policy Limits

**Finding ID**: AG-2
**Risk Level**: Critical
**Component**: LLM Agent Orchestrator
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    AG2_root["Circumvent per-agent rate limits and policy controls via coordinated Orchestrator-Specialist collusion"]
    AG2_and1{{"AND"}}
    AG2_sub1["Compromise or inject coordinated prompts into both agents simultaneously"]
    AG2_sub2["Execute combined action sequence that violates combined policy limits"]
    AG2_or1{{"OR"}}
    AG2_leaf1["Inject coordinated prompt into Orchestrator via user input or KB poisoning"]
    AG2_leaf2["Inject complementary adversarial delegation into Specialist via Inter-Agent Channel"]
    AG2_and2{{"AND"}}
    AG2_leaf3["Confirm no cross-agent coordination policy engine evaluates joint action sequences"]
    AG2_leaf4["Orchestrator issues per-agent-permitted actions that together achieve prohibited outcome"]
    AG2_leaf5["Specialist executes complementary per-agent-permitted actions completing prohibited combined goal"]

    AG2_root --> AG2_and1
    AG2_and1 --> AG2_sub1
    AG2_and1 --> AG2_sub2
    AG2_sub1 --> AG2_or1
    AG2_or1 --> AG2_leaf1
    AG2_or1 --> AG2_leaf2
    AG2_sub2 --> AG2_and2
    AG2_and2 --> AG2_leaf3
    AG2_and2 --> AG2_leaf4
    AG2_and2 --> AG2_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG2_root goal
    class AG2_and1,AG2_and2 andGate
    class AG2_or1 orGate
    class AG2_sub1,AG2_sub2 subGoal
    class AG2_leaf1,AG2_leaf2,AG2_leaf3,AG2_leaf4,AG2_leaf5 leaf
```
