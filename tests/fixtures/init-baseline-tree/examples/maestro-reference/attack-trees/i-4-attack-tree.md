# Attack Tree: I-4 — Supervisor Orchestrator Aggregated Clinical Context Exposure

**Component**: Supervisor Orchestrator | **Risk Level**: High | **Finding**: I-4

A compromise of the Supervisor Orchestrator may expose aggregated sensitive patient data from FHIR, specialist results, and model outputs — more sensitive than any individual component's data.

```mermaid
flowchart TD
    I4_root["Disclose aggregated patient PHI and clinical reasoning via Supervisor Orchestrator compromise"]
    I4_or1{{"OR"}}
    I4_leaf1["Compromise Supervisor Orchestrator process to read assembled multi-component clinical context"]
    I4_leaf2["Extract PHI-containing context windows assembled from FHIR data and specialist results"]
    I4_leaf3["Exploit missing memory isolation to access patient data from adjacent clinical sessions"]

    I4_root --> I4_or1
    I4_or1 --> I4_leaf1
    I4_or1 --> I4_leaf2
    I4_or1 --> I4_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I4_root goal
    class I4_or1 orGate
    class I4_leaf1,I4_leaf2,I4_leaf3 leaf
```
