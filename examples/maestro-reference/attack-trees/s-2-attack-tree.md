# Attack Tree: S-2 — Patient Identity Spoofing for EHR Injection

**Component**: Patient | **Risk Level**: High | **Finding**: S-2

An attacker submits fraudulent EHR update events by spoofing a patient identity, injecting false patient records into the ingestion pipeline.

```mermaid
flowchart TD
    S2_root["Inject false patient records into FHIR store via spoofed patient identity on EHR ingestion"]
    S2_or1{{"OR"}}
    S2_leaf1["Obtain stolen patient identity credentials or registration token"]
    S2_leaf2["Craft fraudulent EHR update event using forged patient identity fields"]
    S2_leaf3["Submit event to EHR Ingestion Queue bypassing patient identity registry validation"]

    S2_root --> S2_or1
    S2_or1 --> S2_leaf1
    S2_or1 --> S2_leaf2
    S2_or1 --> S2_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S2_root goal
    class S2_or1 orGate
    class S2_leaf1,S2_leaf2,S2_leaf3 leaf
```
