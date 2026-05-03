# T-6: Credential Cache Tampering via SharedPreferences Overwrite

**Component**: WellnessBankCredentialCache | **Risk Level**: High | **Finding**: T-6

An attacker with root access overwrites the SharedPreferences credential store to inject forged auth tokens, enabling session hijacking without needing to extract legitimate credentials.

```mermaid
flowchart TD
    T6_root["Hijack Session by Injecting Forged Auth Token into Credential Cache"]
    T6_and1{{"AND"}}
    T6_sub1["Gain Write Access to SharedPreferences File"]
    T6_sub2["Inject Forged Credentials and Exploit Session"]
    T6_leaf1["Root device to obtain write access to app data partition"]
    T6_leaf2["Locate SharedPreferences XML file for WellnessBankCredentialCache"]
    T6_leaf3["Overwrite token value with attacker-controlled forged auth token"]
    T6_leaf4["Confirm no HMAC integrity check validates credential cache at read time"]
    T6_leaf5["Launch app and confirm forged token used for API authentication"]

    T6_root --> T6_and1
    T6_and1 --> T6_sub1
    T6_and1 --> T6_sub2
    T6_sub1 --> T6_leaf1
    T6_sub1 --> T6_leaf2
    T6_sub2 --> T6_leaf3
    T6_sub2 --> T6_leaf4
    T6_sub2 --> T6_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T6_root goal
    class T6_and1 andGate
    class T6_sub1,T6_sub2 subGoal
    class T6_leaf1,T6_leaf2,T6_leaf3,T6_leaf4,T6_leaf5 leaf
```
