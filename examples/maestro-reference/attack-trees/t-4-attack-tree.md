# Attack Tree: T-4 — Supervisor Orchestrator Delegation Logic Tampering

**Component**: Supervisor Orchestrator | **Risk Level**: High | **Finding**: T-4

An attacker who compromises the Supervisor Orchestrator tampers with the delegation logic, routing clinical tasks to adversary-controlled specialist implementations or corrupting aggregated outputs.

```mermaid
flowchart TD
    T4_root["Corrupt clinical outputs by tampering with Supervisor Orchestrator delegation logic"]
    T4_or1{{"OR"}}
    T4_leaf1["Compromise Supervisor Orchestrator process and modify delegation routing logic"]
    T4_leaf2["Inject adversarial configuration that routes tasks to attacker-controlled agent implementations"]
    T4_leaf3["Corrupt aggregation logic to modify specialist results before returning recommendation"]

    T4_root --> T4_or1
    T4_or1 --> T4_leaf1
    T4_or1 --> T4_leaf2
    T4_or1 --> T4_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T4_root goal
    class T4_or1 orGate
    class T4_leaf1,T4_leaf2,T4_leaf3 leaf
```
