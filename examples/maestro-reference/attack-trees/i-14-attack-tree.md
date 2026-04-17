# Attack Tree: I-14 — EHR Ingestion Queue Patient Record Disclosure

**Component**: EHR Ingestion Queue | **Risk Level**: High | **Finding**: I-14

Patient EHR update events in the ingestion queue may be disclosed through insufficient queue access controls, allowing unauthorized parties to read enqueued patient records.

```mermaid
flowchart TD
    I14_root["Disclose patient EHR records from ingestion queue via insufficient access control"]
    I14_or1{{"OR"}}
    I14_leaf1["Obtain unauthorized read access to EHR Ingestion Queue via overly permissive queue ACL"]
    I14_leaf2["Intercept unencrypted EHR event messages in queue transport layer"]
    I14_leaf3["Read queued patient records before normalization and FHIR ingestion consumes them"]

    I14_root --> I14_or1
    I14_or1 --> I14_leaf1
    I14_or1 --> I14_leaf2
    I14_or1 --> I14_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I14_root goal
    class I14_or1 orGate
    class I14_leaf1,I14_leaf2,I14_leaf3 leaf
```
