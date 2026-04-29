# D-2: Missing Rate Limiting on Backend Transaction API

**Component**: WellnessBank Backend API | **Risk Level**: High | **Finding**: D-2

An attacker uses compromised or cloned client applications to flood the backend transaction API with high-volume requests, saturating processing capacity and denying service to legitimate users.

```mermaid
flowchart TD
    D2_root["Deny Availability of Backend Transaction API via Request Flood"]
    D2_or1{{"OR"}}
    D2_sub1["Use Compromised Cloned Client App"]
    D2_sub2["Script Direct API Calls Bypassing Client"]
    D2_leaf1["Repackage APK to remove client-side throttle logic"]
    D2_leaf2["Flood transaction endpoint at volume exceeding backend capacity"]
    D2_leaf3["Craft raw HTTPS requests targeting transaction endpoint at high rate"]
    D2_leaf4["Confirm no per-device or per-IP rate limiting enforced by backend"]

    D2_root --> D2_or1
    D2_or1 --> D2_sub1
    D2_or1 --> D2_sub2
    D2_sub1 --> D2_leaf1
    D2_sub1 --> D2_leaf2
    D2_sub2 --> D2_leaf3
    D2_sub2 --> D2_leaf4

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D2_root goal
    class D2_or1 orGate
    class D2_sub1,D2_sub2 subGoal
    class D2_leaf1,D2_leaf2,D2_leaf3,D2_leaf4 leaf
```
