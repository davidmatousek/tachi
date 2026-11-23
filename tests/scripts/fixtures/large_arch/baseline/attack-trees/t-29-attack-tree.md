# T-29: Unsanitised archived transcripts and training corpora reach...

**Component**: s3-archive | **Risk Level**: High | **Finding**: T-29

Unsanitised archived transcripts and training corpora reach s3-archive and are processed as trusted structure, so crafted input changes how later steps interpret the record.

```mermaid
flowchart TD
    T29_root["Unsanitised archived transcripts and training corpora reach s3-archive..."]
    T29_or1{{"OR"}}
    T29_sub1["Reach s3-archive in the Data Zone"]
    T29_sub2["Rely on the weakness described in T-29"]
    T29_leaf1["A path exists from trace-collector over HTTPS (TLS 1.3)"]
    T29_leaf2["Archived transcripts and training corpora are accepted without an independent check"]
    T29_leaf3["The weakness is present: Unsanitised archived transcripts and training corpora reach..."]
    T29_leaf4["No effective control observed: Validate archived transcripts and training corpora against a..."]

    T29_root --> T29_or1
    T29_or1 --> T29_sub1
    T29_or1 --> T29_sub2
    T29_sub1 --> T29_leaf1
    T29_sub1 --> T29_leaf2
    T29_sub2 --> T29_leaf3
    T29_sub2 --> T29_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T29_root goal
    class T29_or1 orGate
    class T29_sub1,T29_sub2 subGoal
    class T29_leaf1,T29_leaf2,T29_leaf3,T29_leaf4 leaf
```
