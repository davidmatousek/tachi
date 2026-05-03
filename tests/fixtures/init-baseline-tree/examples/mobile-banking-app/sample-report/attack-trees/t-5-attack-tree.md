# T-5: Unencrypted Local Database Tampering

**Component**: WellnessBankLocalDB | **Risk Level**: High | **Finding**: T-5

An attacker with root or ADB access modifies the unencrypted SQLite database, fabricating transaction history or manipulating account balance data displayed to the user.

```mermaid
flowchart TD
    T5_root["Fabricate Transaction History by Tampering with Unencrypted Local Database"]
    T5_or1{{"OR"}}
    T5_sub1["Direct Database Modification via Root Shell"]
    T5_sub2["Database Modification via ADB File Access"]
    T5_leaf1["Root device to gain shell access to app data partition"]
    T5_leaf2["Locate WellnessBankLocalDB SQLite file in app files directory"]
    T5_leaf3["Modify transaction records or account snapshot using sqlite3 CLI"]
    T5_leaf4["Enable ADB file-transfer access on unpatched Android device"]
    T5_leaf5["Pull database file via adb pull and modify with sqlite3 on attacker machine"]
    T5_leaf6["Push modified database back to device via adb push to overwrite original"]

    T5_root --> T5_or1
    T5_or1 --> T5_sub1
    T5_or1 --> T5_sub2
    T5_sub1 --> T5_leaf1
    T5_sub1 --> T5_leaf2
    T5_sub1 --> T5_leaf3
    T5_sub2 --> T5_leaf4
    T5_sub2 --> T5_leaf5
    T5_sub2 --> T5_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T5_root goal
    class T5_or1 orGate
    class T5_sub1,T5_sub2 subGoal
    class T5_leaf1,T5_leaf2,T5_leaf3,T5_leaf4,T5_leaf5,T5_leaf6 leaf
```
