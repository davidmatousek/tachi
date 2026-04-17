# Attack Tree: E-1 — Physician Clinical Portal Privilege Escalation

**Component**: Physician Clinical Portal | **Risk Level**: High | **Finding**: E-1

An attacker who gains access to a low-privilege physician session escalates to access clinical data belonging to other physicians or patients by exploiting broken access controls in the portal's recommendation view logic.

```mermaid
flowchart TD
    E1_root["Escalate from low-privilege physician session to access unauthorized patient clinical data via portal"]
    E1_or1{{"OR"}}
    E1_leaf1["Obtain low-privilege physician session token via credential theft or session hijacking"]
    E1_leaf2["Exploit broken access control in recommendation view logic to access other physicians patients"]
    E1_leaf3["Enumerate patient records beyond session scope due to missing resource-level RBAC enforcement"]

    E1_root --> E1_or1
    E1_or1 --> E1_leaf1
    E1_or1 --> E1_leaf2
    E1_or1 --> E1_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E1_root goal
    class E1_or1 orGate
    class E1_leaf1,E1_leaf2,E1_leaf3 leaf
```
