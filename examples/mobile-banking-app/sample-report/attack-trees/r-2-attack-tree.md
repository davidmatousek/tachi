# R-2: Missing Backend Audit Trail on Transaction Operations

**Component**: WellnessBank Backend API | **Risk Level**: High | **Finding**: R-2

An attacker or insider performs unauthorized privileged operations on the backend API that cannot be forensically reconstructed because no audit event emission is implemented on money-movement or account-write endpoints.

```mermaid
flowchart TD
    R2_root["Execute Untracked Privileged Backend Operations Without Audit Evidence"]
    R2_or1{{"OR"}}
    R2_sub1["Attacker Exploits Token Replay Without Detection"]
    R2_sub2["Insider Performs Unauthorized Account Operation"]
    R2_leaf1["Replay stolen session token against money-movement endpoint"]
    R2_leaf2["Confirm no structured audit event emitted for the transaction"]
    R2_leaf3["Confirm no SIEM alert triggered for anomalous operation pattern"]
    R2_leaf4["Access backend with legitimate credentials to perform unauthorized operation"]
    R2_leaf5["Exploit absence of audit trail to deny action in dispute resolution"]

    R2_root --> R2_or1
    R2_or1 --> R2_sub1
    R2_or1 --> R2_sub2
    R2_sub1 --> R2_leaf1
    R2_sub1 --> R2_leaf2
    R2_sub1 --> R2_leaf3
    R2_sub2 --> R2_leaf4
    R2_sub2 --> R2_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class R2_root goal
    class R2_or1 orGate
    class R2_sub1,R2_sub2 subGoal
    class R2_leaf1,R2_leaf2,R2_leaf3,R2_leaf4,R2_leaf5 leaf
```
