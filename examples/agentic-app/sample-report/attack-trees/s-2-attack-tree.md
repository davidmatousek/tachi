# Attack Tree: S-2 — Application Zone Process Bypasses Guardrails by Spoofing Direct Orchestrator Access

**Finding ID**: S-2
**Risk Level**: High
**Component**: Guardrails Service
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    S2_root["Bypass Guardrails by sending crafted requests directly to Orchestrator internal endpoint"]
    S2_and1{{"AND"}}
    S2_sub1["Identify Orchestrator internal endpoint without mTLS enforcement"]
    S2_sub2["Submit unvalidated request impersonating Guardrails Service"]
    S2_leaf1["Enumerate internal service endpoints via network scan or service mesh metadata"]
    S2_leaf2["Confirm Orchestrator does not require mutual TLS from callers in Application Zone"]
    S2_leaf3["Send crafted prompt directly to Orchestrator bypassing content filtering entirely"]

    S2_root --> S2_and1
    S2_and1 --> S2_sub1
    S2_and1 --> S2_sub2
    S2_sub1 --> S2_leaf1
    S2_sub1 --> S2_leaf2
    S2_sub2 --> S2_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S2_root goal
    class S2_and1 andGate
    class S2_sub1,S2_sub2 subGoal
    class S2_leaf1,S2_leaf2,S2_leaf3 leaf
```
