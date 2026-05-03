# E-3: Server-Side Authorization Gap for Debug-Initiated Operations

**Component**: WellnessBank Backend API | **Risk Level**: High | **Finding**: E-3

An attacker exploiting the debug Activity initiates privileged operations that the backend accepts on the basis of the session token alone, without verifying that the request originated from a legitimate in-app user action.

```mermaid
flowchart TD
    E3_root["Exploit Backend Authorization Gap for Debug-Channel Operations"]
    E3_and1{{"AND"}}
    E3_sub1["Trigger Debug Activity Privileged Action"]
    E3_sub2["Exploit Backend Token-Only Validation"]
    E3_leaf1["Invoke WellnessBankDebugActivity via ADB or Intent to initiate privileged action"]
    E3_leaf2["Confirm debug channel connects directly to main client with valid session token"]
    E3_leaf3["Submit privileged API request using session token from debug channel"]
    E3_leaf4["Confirm backend accepts request without Play Integrity client attestation"]

    E3_root --> E3_and1
    E3_and1 --> E3_sub1
    E3_and1 --> E3_sub2
    E3_sub1 --> E3_leaf1
    E3_sub1 --> E3_leaf2
    E3_sub2 --> E3_leaf3
    E3_sub2 --> E3_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E3_root goal
    class E3_and1 andGate
    class E3_sub1,E3_sub2 subGoal
    class E3_leaf1,E3_leaf2,E3_leaf3,E3_leaf4 leaf
```
