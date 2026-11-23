# I-43: Logs and traces emitted by edge-gateway include raw inbound API...

**Component**: edge-gateway | **Risk Level**: High | **Finding**: I-43

Logs and traces emitted by edge-gateway include raw inbound API requests, so anyone with access to the logging pipeline can read content meant for one tenant.

```mermaid
flowchart TD
    I43_root["Logs and traces emitted by edge-gateway include raw inbound API..."]
    I43_or1{{"OR"}}
    I43_sub1["Reach edge-gateway in the Edge DMZ"]
    I43_sub2["Rely on the weakness described in I-43"]
    I43_leaf1["A path exists from client-portal over HTTPS (TLS 1.3)"]
    I43_leaf2["Inbound api requests are accepted without an independent check"]
    I43_leaf3["The weakness is present: Logs and traces emitted by edge-gateway include raw inbound API..."]
    I43_leaf4["No effective control observed: Redact or tokenise sensitive fields before edge-gateway emits logs..."]

    I43_root --> I43_or1
    I43_or1 --> I43_sub1
    I43_or1 --> I43_sub2
    I43_sub1 --> I43_leaf1
    I43_sub1 --> I43_leaf2
    I43_sub2 --> I43_leaf3
    I43_sub2 --> I43_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I43_root goal
    class I43_or1 orGate
    class I43_sub1,I43_sub2 subGoal
    class I43_leaf1,I43_leaf2,I43_leaf3,I43_leaf4 leaf
```
