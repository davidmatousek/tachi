# I-3: Insecure Mobile Data Storage — Unencrypted SQLite via Cloud Backup

**Component**: WellnessBankLocalDB | **Risk Level**: Critical | **Finding**: I-3

An attacker who compromises a user's Google account recovers complete transaction history and account snapshots from Google Drive cloud backup, bypassing device authentication entirely.

```mermaid
flowchart TD
    I3_root["Recover Complete Financial History via Google Account Compromise"]
    I3_and1{{"AND"}}
    I3_sub1["Gain Access to Victim Google Account"]
    I3_sub2["Exploit allowBackup=true to Exfiltrate Database"]
    I3_sub3["Parse Unencrypted SQLite Data"]
    I3_or1{{"OR"}}
    I3_leaf1["Phish Google account credentials via fake login page"]
    I3_leaf2["Exploit leaked Google credentials from unrelated breach"]
    I3_leaf3["Access Google Drive backup containing WellnessBankLocalDB file"]
    I3_leaf4["Confirm database is plain SQLite with no SQLCipher encryption"]
    I3_leaf5["Extract account snapshots and transaction records from backup copy"]

    I3_root --> I3_and1
    I3_and1 --> I3_sub1
    I3_and1 --> I3_sub2
    I3_and1 --> I3_sub3
    I3_sub1 --> I3_or1
    I3_or1 --> I3_leaf1
    I3_or1 --> I3_leaf2
    I3_sub2 --> I3_leaf3
    I3_sub2 --> I3_leaf4
    I3_sub3 --> I3_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I3_root goal
    class I3_and1 andGate
    class I3_or1 orGate
    class I3_sub1,I3_sub2,I3_sub3 subGoal
    class I3_leaf1,I3_leaf2,I3_leaf3,I3_leaf4,I3_leaf5 leaf
```
