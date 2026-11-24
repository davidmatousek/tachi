# I-31: Data in transit between trace-collector and s3-archive is...

**Component**: s3-archive | **Risk Level**: Critical | **Finding**: I-31

Data in transit between trace-collector and s3-archive is protected only on the outer hop, which leaves archived transcripts and training corpora readable on the internal segment after termination.

```mermaid
flowchart TD
    I31_root["Data in transit between trace-collector and s3-archive is protected..."]
    I31_or1{{"OR"}}
    I31_sub1["Reach s3-archive in the Data Zone"]
    I31_sub2["Rely on the weakness described in I-31"]
    I31_leaf1["A path exists from trace-collector over HTTPS (TLS 1.3)"]
    I31_leaf2["Archived transcripts and training corpora are accepted without an independent check"]
    I31_leaf3["The weakness is present: Data in transit between trace-collector and s3-archive is..."]
    I31_leaf4["No effective control observed: Keep TLS end to end between trace-collector and s3-archive..."]

    I31_root --> I31_or1
    I31_or1 --> I31_sub1
    I31_or1 --> I31_sub2
    I31_sub1 --> I31_leaf1
    I31_sub1 --> I31_leaf2
    I31_sub2 --> I31_leaf3
    I31_sub2 --> I31_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I31_root goal
    class I31_or1 orGate
    class I31_sub1,I31_sub2 subGoal
    class I31_leaf1,I31_leaf2,I31_leaf3,I31_leaf4 leaf
```
