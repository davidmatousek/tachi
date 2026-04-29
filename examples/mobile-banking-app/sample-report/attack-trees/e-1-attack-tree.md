# E-1: Exported Debug Activity Bypassing Authentication Boundary

**Component**: WellnessBankDebugActivity | **Risk Level**: Critical | **Finding**: E-1

An attacker with ADB access exploits the production-retained debug Activity to execute privileged banking operations without authentication, bypassing all standard auth boundary controls.

```mermaid
flowchart TD
    E1_root["Execute Privileged Banking Operations Without Authentication"]
    E1_or1{{"OR"}}
    E1_sub1["Exploit via ADB Direct Invocation"]
    E1_sub2["Exploit via Co-installed App Intent"]
    E1_and1{{"AND"}}
    E1_and2{{"AND"}}
    E1_leaf1["Obtain ADB access to device via USB or ADB over TCP"]
    E1_leaf2["Issue adb shell am start targeting WellnessBankDebugActivity"]
    E1_leaf3["Confirm no BuildConfig.DEBUG guard is enforced at runtime"]
    E1_leaf4["Install malicious app with Intent targeting DebugActivity component"]
    E1_leaf5["Confirm android:exported=true with no android:permission in manifest"]
    E1_leaf6["Invoke privileged action flow bypassing auth boundary into main client"]

    E1_root --> E1_or1
    E1_or1 --> E1_sub1
    E1_or1 --> E1_sub2
    E1_sub1 --> E1_and1
    E1_and1 --> E1_leaf1
    E1_and1 --> E1_leaf2
    E1_and1 --> E1_leaf3
    E1_sub2 --> E1_and2
    E1_and2 --> E1_leaf4
    E1_and2 --> E1_leaf5
    E1_and2 --> E1_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E1_root goal
    class E1_and1,E1_and2 andGate
    class E1_or1 orGate
    class E1_sub1,E1_sub2 subGoal
    class E1_leaf1,E1_leaf2,E1_leaf3,E1_leaf4,E1_leaf5,E1_leaf6 leaf
```
