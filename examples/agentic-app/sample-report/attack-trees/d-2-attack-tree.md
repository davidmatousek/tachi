# Attack Tree: D-2 — Orchestrator Inference Pipeline Exhausted via Token Flood or Recursive Tool Chains

**Finding ID**: D-2
**Risk Level**: Critical
**Component**: LLM Agent Orchestrator
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    D2_root["Exhaust Orchestrator inference capacity to deny service to legitimate users"]
    D2_or1{{"OR"}}
    D2_sub1["Flood Orchestrator with high-token-count prompts"]
    D2_sub2["Inject context causing recursive tool invocation chains"]
    D2_and1{{"AND"}}
    D2_leaf1["Craft prompts with maximum-length preambles or embedded corpora"]
    D2_leaf2["Confirm Orchestrator lacks per-session context-window size limits"]
    D2_leaf3["Submit high-token prompts at rate that saturates inference capacity"]
    D2_and2{{"AND"}}
    D2_leaf4["Craft prompt or KB document that causes Orchestrator to issue recursive tool calls"]
    D2_leaf5["Confirm no circuit breaker limits maximum recursive tool invocation depth"]
    D2_leaf6["Trigger chain that exhausts inference pipeline starving legitimate request processing"]

    D2_root --> D2_or1
    D2_or1 --> D2_sub1
    D2_or1 --> D2_sub2
    D2_sub1 --> D2_and1
    D2_and1 --> D2_leaf1
    D2_and1 --> D2_leaf2
    D2_and1 --> D2_leaf3
    D2_sub2 --> D2_and2
    D2_and2 --> D2_leaf4
    D2_and2 --> D2_leaf5
    D2_and2 --> D2_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D2_root goal
    class D2_or1 orGate
    class D2_and1,D2_and2 andGate
    class D2_sub1,D2_sub2 subGoal
    class D2_leaf1,D2_leaf2,D2_leaf3,D2_leaf4,D2_leaf5,D2_leaf6 leaf
```
