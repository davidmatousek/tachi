# Attack Tree: I-15 — Clinical Audit Log Unauthorized Read Access

**Component**: Clinical Audit Log | **Risk Level**: High | **Finding**: I-15

The Clinical Audit Log accumulates highly sensitive clinical decision trails. Unauthorized read access could disclose PHI, clinical reasoning, and agent decision patterns to adversaries.

```mermaid
flowchart TD
    I15_root["Disclose clinical decision trails and PHI via unauthorized Clinical Audit Log read access"]
    I15_or1{{"OR"}}
    I15_leaf1["Obtain over-privileged service account with read access to audit log storage"]
    I15_leaf2["Exploit absent read-access controls to enumerate clinical session decision records"]
    I15_leaf3["Extract agent decision patterns and PHI-containing reasoning from audit log entries"]

    I15_root --> I15_or1
    I15_or1 --> I15_leaf1
    I15_or1 --> I15_leaf2
    I15_or1 --> I15_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I15_root goal
    class I15_or1 orGate
    class I15_leaf1,I15_leaf2,I15_leaf3 leaf
```
