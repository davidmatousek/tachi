# S-3: Credential Theft via SharedPreferences Extraction on Rooted Device

**Component**: WellnessBank Android Client | **Risk Level**: High | **Finding**: S-3

An attacker extracts long-lived auth tokens from MODE_PRIVATE SharedPreferences on a rooted device or via ADB backup, enabling offline credential recovery without live user presence.

```mermaid
flowchart TD
    S3_root["Recover Long-Lived Auth Tokens via SharedPreferences Extraction"]
    S3_or1{{"OR"}}
    S3_sub1["Root-Based Data Partition Extraction"]
    S3_sub2["ADB Backup on Unpatched Android Version"]
    S3_leaf1["Root device using publicly available kernel exploit"]
    S3_leaf2["Navigate to app data directory and read SharedPreferences XML"]
    S3_leaf3["Enable ADB debugging on target device"]
    S3_leaf4["Run adb backup to extract app data including SharedPreferences"]
    S3_leaf5["Parse extracted archive to recover auth token and replay against API"]

    S3_root --> S3_or1
    S3_or1 --> S3_sub1
    S3_or1 --> S3_sub2
    S3_sub1 --> S3_leaf1
    S3_sub1 --> S3_leaf2
    S3_sub2 --> S3_leaf3
    S3_sub2 --> S3_leaf4
    S3_sub2 --> S3_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S3_root goal
    class S3_or1 orGate
    class S3_sub1,S3_sub2 subGoal
    class S3_leaf1,S3_leaf2,S3_leaf3,S3_leaf4,S3_leaf5 leaf
```
