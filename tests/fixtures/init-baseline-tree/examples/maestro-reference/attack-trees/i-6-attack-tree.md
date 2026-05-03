# Attack Tree: I-6 — Treatment Planner Agent Patient Data Disclosure

**Component**: Treatment Planner Agent | **Risk Level**: High | **Finding**: I-6

The Treatment Planner Agent may disclose sensitive patient data retrieved from the Medical Literature Vector Index through insufficient session isolation or unfiltered error responses.

```mermaid
flowchart TD
    I6_root["Disclose patient data via Treatment Planner Agent session isolation failure or error response leakage"]
    I6_or1{{"OR"}}
    I6_leaf1["Exploit missing session isolation to access patient context from concurrent treatment planning task"]
    I6_leaf2["Trigger unfiltered error response exposing retrieved literature result containing patient-specific context"]
    I6_leaf3["Read PHI leaked through unfiltered treatment plan output before output filtering applied"]

    I6_root --> I6_or1
    I6_or1 --> I6_leaf1
    I6_or1 --> I6_leaf2
    I6_or1 --> I6_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I6_root goal
    class I6_or1 orGate
    class I6_leaf1,I6_leaf2,I6_leaf3 leaf
```
