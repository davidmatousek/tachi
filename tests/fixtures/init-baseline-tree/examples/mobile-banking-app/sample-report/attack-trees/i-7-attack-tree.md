# I-7: Insecure Mobile Data Storage — Credential Cache in Plaintext SharedPreferences

**Component**: WellnessBankCredentialCache | **Risk Level**: Critical | **Finding**: I-7

An attacker extracts long-lived session tokens from plaintext SharedPreferences, enabling full account access without any biometric or PIN challenge.

```mermaid
flowchart TD
    I7_root["Extract Long-Lived Session Token from Plaintext Credential Cache"]
    I7_or1{{"OR"}}
    I7_sub1["Access via Rooted Device"]
    I7_sub2["Access via ADB Backup on Pre-Android-12 Device"]
    I7_sub3["Access via Compromised Cloud Backup"]
    I7_leaf1["Root device using publicly available exploit"]
    I7_leaf2["Read SharedPreferences XML from app data partition using root shell"]
    I7_leaf3["Enable ADB debugging and run adb backup on unpatched Android version"]
    I7_leaf4["Parse backup archive to extract SharedPreferences XML"]
    I7_leaf5["Compromise Google account and retrieve Android backup from Drive"]
    I7_leaf6["Parse extracted token and replay against backend API"]

    I7_root --> I7_or1
    I7_or1 --> I7_sub1
    I7_or1 --> I7_sub2
    I7_or1 --> I7_sub3
    I7_sub1 --> I7_leaf1
    I7_sub1 --> I7_leaf2
    I7_sub2 --> I7_leaf3
    I7_sub2 --> I7_leaf4
    I7_sub3 --> I7_leaf5
    I7_sub3 --> I7_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I7_root goal
    class I7_or1 orGate
    class I7_sub1,I7_sub2,I7_sub3 subGoal
    class I7_leaf1,I7_leaf2,I7_leaf3,I7_leaf4,I7_leaf5,I7_leaf6 leaf
```
