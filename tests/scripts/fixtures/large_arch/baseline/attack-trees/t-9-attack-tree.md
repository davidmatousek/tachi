# T-9: An update to tool-server-1 is pulled without provenance checks, so...

**Component**: tool-server-1 | **Risk Level**: High | **Finding**: T-9

An update to tool-server-1 is pulled without provenance checks, so a poisoned package can alter how tool call arguments and results are handled at run time.

```mermaid
flowchart TD
    T9_root["An update to tool-server-1 is pulled without provenance checks, so a..."]
    T9_or1{{"OR"}}
    T9_sub1["Reach tool-server-1 in the Agent Runtime Zone"]
    T9_sub2["Rely on the weakness described in T-9"]
    T9_leaf1["A path exists from worker-2 over HTTPS (TLS 1.3)"]
    T9_leaf2["Tool call arguments and results are accepted without an independent check"]
    T9_leaf3["The weakness is present: An update to tool-server-1 is pulled without provenance checks, so..."]
    T9_leaf4["No effective control observed: Pin dependencies by digest, verify signatures and provenance..."]

    T9_root --> T9_or1
    T9_or1 --> T9_sub1
    T9_or1 --> T9_sub2
    T9_sub1 --> T9_leaf1
    T9_sub1 --> T9_leaf2
    T9_sub2 --> T9_leaf3
    T9_sub2 --> T9_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T9_root goal
    class T9_or1 orGate
    class T9_sub1,T9_sub2 subGoal
    class T9_leaf1,T9_leaf2,T9_leaf3,T9_leaf4 leaf
```
