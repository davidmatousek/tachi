# Attack Tree: S-3 — Physician Clinical Portal Spoofing

**Component**: Physician Clinical Portal | **Risk Level**: High | **Finding**: S-3

An attacker spoofs the Physician Clinical Portal to intercept clinical recommendation responses from the Supervisor Orchestrator, receiving sensitive patient data intended for legitimate physicians.

```mermaid
flowchart TD
    S3_root["Intercept clinical recommendations and PHI via spoofed Physician Clinical Portal"]
    S3_or1{{"OR"}}
    S3_leaf1["Set up rogue portal endpoint with forged server certificate or DNS redirect"]
    S3_leaf2["Intercept Supervisor Orchestrator response lacking signed response token validation"]
    S3_leaf3["Deliver intercepted PHI-containing recommendation to attacker-controlled storage"]

    S3_root --> S3_or1
    S3_or1 --> S3_leaf1
    S3_or1 --> S3_leaf2
    S3_or1 --> S3_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S3_root goal
    class S3_or1 orGate
    class S3_leaf1,S3_leaf2,S3_leaf3 leaf
```
