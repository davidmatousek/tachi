# Attack Tree: T-14 — EHR Ingestion Queue Event Tampering

**Component**: EHR Ingestion Queue | **Risk Level**: High | **Finding**: T-14

An attacker tampers with EHR update events in the ingestion queue before normalization, injecting false patient data that propagates into the FHIR Resource Store.

```mermaid
flowchart TD
    T14_root["Inject false patient data into FHIR store via EHR Ingestion Queue event tampering"]
    T14_or1{{"OR"}}
    T14_leaf1["Gain write access to ingestion queue and modify enqueued EHR event payload"]
    T14_leaf2["Exploit absent message integrity signatures to tamper with event fields in transit"]
    T14_leaf3["Cause false patient record to propagate into FHIR Resource Store via normalization process"]

    T14_root --> T14_or1
    T14_or1 --> T14_leaf1
    T14_or1 --> T14_leaf2
    T14_or1 --> T14_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T14_root goal
    class T14_or1 orGate
    class T14_leaf1,T14_leaf2,T14_leaf3 leaf
```
