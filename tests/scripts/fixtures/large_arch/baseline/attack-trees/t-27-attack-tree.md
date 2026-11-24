# T-27: Serialised objects arriving from kb-index are deserialised by...

**Component**: s3-archive | **Risk Level**: Critical | **Finding**: T-27

Serialised objects arriving from kb-index are deserialised by s3-archive with permissive type handling, allowing crafted payloads to instantiate unintended behaviour.

```mermaid
flowchart TD
    T27_root["Serialised objects arriving from kb-index are deserialised by..."]
    T27_or1{{"OR"}}
    T27_sub1["Reach s3-archive in the Data Zone"]
    T27_sub2["Rely on the weakness described in T-27"]
    T27_leaf1["A path exists from trace-collector over HTTPS (TLS 1.3)"]
    T27_leaf2["Archived transcripts and training corpora are accepted without an independent check"]
    T27_leaf3["The weakness is present: Serialised objects arriving from kb-index are deserialised by..."]
    T27_leaf4["No effective control observed: Replace permissive deserialisation in s3-archive with a closed..."]

    T27_root --> T27_or1
    T27_or1 --> T27_sub1
    T27_or1 --> T27_sub2
    T27_sub1 --> T27_leaf1
    T27_sub1 --> T27_leaf2
    T27_sub2 --> T27_leaf3
    T27_sub2 --> T27_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T27_root goal
    class T27_or1 orGate
    class T27_sub1,T27_sub2 subGoal
    class T27_leaf1,T27_leaf2,T27_leaf3,T27_leaf4 leaf
```
