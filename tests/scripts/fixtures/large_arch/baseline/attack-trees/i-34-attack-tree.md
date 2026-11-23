# I-34: Data in transit between scheduler-1 and queue-a2 is protected only...

**Component**: queue-a2 | **Risk Level**: High | **Finding**: I-34

Data in transit between scheduler-1 and queue-a2 is protected only on the outer hop, which leaves task and result messages readable on the internal segment after termination.

```mermaid
flowchart TD
    I34_root["Data in transit between scheduler-1 and queue-a2 is protected only on..."]
    I34_or1{{"OR"}}
    I34_sub1["Reach queue-a2 in the Agent Runtime Zone"]
    I34_sub2["Rely on the weakness described in I-34"]
    I34_leaf1["A path exists from intake-agent over NATS over TLS"]
    I34_leaf2["Task and result messages are accepted without an independent check"]
    I34_leaf3["The weakness is present: Data in transit between scheduler-1 and queue-a2 is protected only..."]
    I34_leaf4["No effective control observed: Keep TLS end to end between scheduler-1 and queue-a2, disable..."]

    I34_root --> I34_or1
    I34_or1 --> I34_sub1
    I34_or1 --> I34_sub2
    I34_sub1 --> I34_leaf1
    I34_sub1 --> I34_leaf2
    I34_sub2 --> I34_leaf3
    I34_sub2 --> I34_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I34_root goal
    class I34_or1 orGate
    class I34_sub1,I34_sub2 subGoal
    class I34_leaf1,I34_leaf2,I34_leaf3,I34_leaf4 leaf
```
