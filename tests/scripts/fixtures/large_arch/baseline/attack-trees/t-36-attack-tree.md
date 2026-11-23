# T-36: An update to trace-collector is pulled without provenance checks...

**Component**: trace-collector | **Risk Level**: High | **Finding**: T-36

An update to trace-collector is pulled without provenance checks, so a poisoned package can alter how prompts, completions and tool traces are handled at run time.

```mermaid
flowchart TD
    T36_root["An update to trace-collector is pulled without provenance checks, so a..."]
    T36_or1{{"OR"}}
    T36_sub1["Reach trace-collector in the Operations Zone"]
    T36_sub2["Rely on the weakness described in T-36"]
    T36_leaf1["A path exists from intake-agent over OTLP over TLS"]
    T36_leaf2["Prompts, completions and tool traces are accepted without an independent check"]
    T36_leaf3["The weakness is present: An update to trace-collector is pulled without provenance checks..."]
    T36_leaf4["No effective control observed: Pin dependencies by digest, verify signatures and provenance..."]

    T36_root --> T36_or1
    T36_or1 --> T36_sub1
    T36_or1 --> T36_sub2
    T36_sub1 --> T36_leaf1
    T36_sub1 --> T36_leaf2
    T36_sub2 --> T36_leaf3
    T36_sub2 --> T36_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T36_root goal
    class T36_or1 orGate
    class T36_sub1,T36_sub2 subGoal
    class T36_leaf1,T36_leaf2,T36_leaf3,T36_leaf4 leaf
```
