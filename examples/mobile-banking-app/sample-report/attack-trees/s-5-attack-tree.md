# S-5: Long-Lived Session Token Replay

**Component**: Mobile Banking Customer | **Risk Level**: High | **Finding**: S-5

An attacker who obtains a session token replays it indefinitely against the backend API because no token rotation policy or expiry enforcement exists, transforming a temporary credential theft into a permanent account compromise.

```mermaid
flowchart TD
    S5_root["Maintain Persistent Account Access via Indefinitely Replayable Session Token"]
    S5_and1{{"AND"}}
    S5_sub1["Acquire Session Token"]
    S5_sub2["Exploit Absent Token Rotation and Revocation"]
    S5_or1{{"OR"}}
    S5_leaf1["Extract token from SharedPreferences on rooted or backed-up device"]
    S5_leaf2["Intercept token via MITM on unpinned TLS connection"]
    S5_leaf3["Replay token against backend API beyond expected session lifetime"]
    S5_leaf4["Confirm no 15-minute TTL or token rotation policy enforced server-side"]

    S5_root --> S5_and1
    S5_and1 --> S5_sub1
    S5_and1 --> S5_sub2
    S5_sub1 --> S5_or1
    S5_or1 --> S5_leaf1
    S5_or1 --> S5_leaf2
    S5_sub2 --> S5_leaf3
    S5_sub2 --> S5_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S5_root goal
    class S5_and1 andGate
    class S5_or1 orGate
    class S5_sub1,S5_sub2 subGoal
    class S5_leaf1,S5_leaf2,S5_leaf3,S5_leaf4 leaf
```
