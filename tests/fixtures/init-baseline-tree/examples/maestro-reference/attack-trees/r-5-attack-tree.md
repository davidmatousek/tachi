# Attack Tree: R-5 — Inter-Agent Channel Repudiation of Delegation Messages

**Component**: Inter-Agent Communication Channel | **Risk Level**: High | **Finding**: R-5

The Inter-Agent Communication Channel may fail to provide non-repudiable records of all delegation messages and specialist results, allowing agents to deny actions taken during the coordination flow.

```mermaid
flowchart TD
    R5_root["Enable agent repudiation of clinical coordination actions via insufficient delegation message logging"]
    R5_or1{{"OR"}}
    R5_leaf1["Exploit absent per-message cryptographic receipts to deny issuing delegation command"]
    R5_leaf2["Delete or tamper with inter-agent message logs before forensic review"]
    R5_leaf3["Deny specialist result submission when no non-repudiable record exists in Clinical Audit Log"]

    R5_root --> R5_or1
    R5_or1 --> R5_leaf1
    R5_or1 --> R5_leaf2
    R5_or1 --> R5_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class R5_root goal
    class R5_or1 orGate
    class R5_leaf1,R5_leaf2,R5_leaf3 leaf
```
