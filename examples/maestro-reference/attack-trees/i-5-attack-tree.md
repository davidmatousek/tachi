# Attack Tree: I-5 — Diagnostic Agent Patient Context Disclosure

**Component**: Diagnostic Agent | **Risk Level**: High | **Finding**: I-5

The Diagnostic Agent may expose sensitive patient context retrieved from Clinical Guideline RAG Corpus and risk stratification results through tool call parameters, error responses, or insufficient isolation between patient sessions.

```mermaid
flowchart TD
    I5_root["Disclose patient PHI via Diagnostic Agent tool call parameter leakage or session isolation failure"]
    I5_or1{{"OR"}}
    I5_leaf1["Trigger verbose tool call error response exposing patient context in error message"]
    I5_leaf2["Exploit missing session isolation to access patient data from concurrent clinical queries"]
    I5_leaf3["Read PHI exposed in unfiltered tool call parameters logged without sanitization"]

    I5_root --> I5_or1
    I5_or1 --> I5_leaf1
    I5_or1 --> I5_leaf2
    I5_or1 --> I5_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I5_root goal
    class I5_or1 orGate
    class I5_leaf1,I5_leaf2,I5_leaf3 leaf
```
