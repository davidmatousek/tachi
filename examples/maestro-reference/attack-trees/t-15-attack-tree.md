# Attack Tree: T-15 — Clinical Audit Log Tampering

**Component**: Clinical Audit Log | **Risk Level**: High | **Finding**: T-15

An attacker who gains write access to the Clinical Audit Log tampers with decision log entries, covering tracks for unauthorized actions or injecting false audit evidence.

```mermaid
flowchart TD
    T15_root["Cover tracks for unauthorized actions by tampering with Clinical Audit Log decision entries"]
    T15_or1{{"OR"}}
    T15_leaf1["Obtain write credentials to Clinical Audit Log storage without per-write integrity receipts"]
    T15_leaf2["Delete or modify existing decision log entries to remove evidence of unauthorized actions"]
    T15_leaf3["Inject false audit entries creating misleading evidence trail for forensic investigators"]

    T15_root --> T15_or1
    T15_or1 --> T15_leaf1
    T15_or1 --> T15_leaf2
    T15_or1 --> T15_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T15_root goal
    class T15_or1 orGate
    class T15_leaf1,T15_leaf2,T15_leaf3 leaf
```
