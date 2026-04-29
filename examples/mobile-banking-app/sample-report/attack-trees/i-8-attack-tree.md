# I-8: Debug Log PII Leakage via Logcat

**Component**: WellnessBank Android Client | **Risk Level**: Critical | **Finding**: I-8

An attacker harvests authentication credentials (username and session token) written to the device-shared logcat sink by unguarded Log.d calls retained in the release build.

```mermaid
flowchart TD
    I8_root["Harvest Authentication Credentials from Release-Build Logcat Output"]
    I8_or1{{"OR"}}
    I8_sub1["Read Logs via Privileged App"]
    I8_sub2["Read Logs via ADB Shell"]
    I8_sub3["Read Logs via Co-installed Malicious App on Older Android"]
    I8_and1{{"AND"}}
    I8_leaf1["Install privileged system app with READ_LOGS permission"]
    I8_leaf2["Capture logcat stream containing Log.d auth credential entries"]
    I8_leaf3["Obtain ADB access and run adb logcat on connected device"]
    I8_leaf4["Install app requesting READ_LOGS on Android version where user-granted"]
    I8_leaf5["Filter logcat for auth tag to extract username and token values"]

    I8_root --> I8_or1
    I8_or1 --> I8_sub1
    I8_or1 --> I8_sub2
    I8_or1 --> I8_sub3
    I8_sub1 --> I8_and1
    I8_and1 --> I8_leaf1
    I8_and1 --> I8_leaf2
    I8_sub2 --> I8_leaf3
    I8_sub3 --> I8_leaf4
    I8_sub3 --> I8_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I8_root goal
    class I8_and1 andGate
    class I8_or1 orGate
    class I8_sub1,I8_sub2,I8_sub3 subGoal
    class I8_leaf1,I8_leaf2,I8_leaf3,I8_leaf4,I8_leaf5 leaf
```
