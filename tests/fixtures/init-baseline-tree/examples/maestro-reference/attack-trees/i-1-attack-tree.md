# Attack Tree: I-1 — Physician Clinical Portal PHI Disclosure

**Component**: Physician Clinical Portal | **Risk Level**: High | **Finding**: I-1

Sensitive clinical recommendation data including patient PHI may be disclosed through the Physician Clinical Portal via insecure HTTPS configuration, excessive error messages, or missing access controls on recommendation views.

```mermaid
flowchart TD
    I1_root["Disclose patient PHI via Physician Clinical Portal through misconfiguration or access control bypass"]
    I1_or1{{"OR"}}
    I1_leaf1["Exploit insecure TLS configuration to intercept clinical recommendation traffic"]
    I1_leaf2["Trigger verbose error responses exposing PHI-containing stack traces or debug output"]
    I1_leaf3["Access recommendation view for unauthorized patient via missing field-level access control"]

    I1_root --> I1_or1
    I1_or1 --> I1_leaf1
    I1_or1 --> I1_leaf2
    I1_or1 --> I1_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I1_root goal
    class I1_or1 orGate
    class I1_leaf1,I1_leaf2,I1_leaf3 leaf
```
