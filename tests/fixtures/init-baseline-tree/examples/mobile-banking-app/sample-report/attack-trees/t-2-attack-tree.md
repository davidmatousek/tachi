# T-2: Mobile Supply Chain Integrity — Payment SDK Compromise

**Component**: WellnessPaySDK | **Risk Level**: High | **Finding**: T-2

An attacker compromises the WellnessPaySDK supply chain, injecting code that intercepts or modifies payment authorization requests before they leave the device.

```mermaid
flowchart TD
    T2_root["Intercept Payment Authorization Requests via Compromised Payment SDK"]
    T2_and1{{"AND"}}
    T2_sub1["Compromise Payment SDK Distribution Channel"]
    T2_sub2["Exploit Absent SDK Integrity Verification"]
    T2_leaf1["Compromise payment SDK vendor or distribution repository"]
    T2_leaf2["Inject code that intercepts payment authorization API calls in-process"]
    T2_leaf3["Confirm floating Gradle version constraint allows auto-update"]
    T2_leaf4["Confirm no checksum or signed-artifact policy on payment SDK ingestion"]
    T2_leaf5["Capture payment card data and transaction amounts before SDK sends request"]

    T2_root --> T2_and1
    T2_and1 --> T2_sub1
    T2_and1 --> T2_sub2
    T2_sub1 --> T2_leaf1
    T2_sub1 --> T2_leaf2
    T2_sub2 --> T2_leaf3
    T2_sub2 --> T2_leaf4
    T2_sub2 --> T2_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T2_root goal
    class T2_and1 andGate
    class T2_sub1,T2_sub2 subGoal
    class T2_leaf1,T2_leaf2,T2_leaf3,T2_leaf4,T2_leaf5 leaf
```
