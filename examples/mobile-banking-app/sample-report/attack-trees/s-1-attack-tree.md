# S-1: Improper Mobile Credential Usage — Auth Token in Unprotected SharedPreferences

**Component**: WellnessBank Android Client | **Risk Level**: Critical | **Finding**: S-1

An attacker who physically or remotely accesses a rooted device extracts long-lived authentication credentials from unencrypted SharedPreferences and achieves full account impersonation.

```mermaid
flowchart TD
    S1_root["Achieve Full Account Impersonation via Credential Extraction from Device"]
    S1_or1{{"OR"}}
    S1_sub1["Exploit Physical Device Access"]
    S1_sub2["Exploit Remote Root via Vulnerability"]
    S1_sub3["Exploit ADB Backup on Pre-Android-12 Device"]
    S1_and1{{"AND"}}
    S1_leaf1["Root device using published Android exploit or unlock bootloader"]
    S1_leaf2["Read app data partition to locate SharedPreferences XML file"]
    S1_leaf3["Extract username and auth token in plaintext from XML"]
    S1_leaf4["Exploit remote privilege escalation CVE to gain root shell on device"]
    S1_leaf5["Access app data partition remotely and extract SharedPreferences"]
    S1_leaf6["Enable ADB backup and extract SharedPreferences from backup archive"]
    S1_leaf7["Replay extracted token against backend API to impersonate account owner"]

    S1_root --> S1_or1
    S1_or1 --> S1_sub1
    S1_or1 --> S1_sub2
    S1_or1 --> S1_sub3
    S1_sub1 --> S1_and1
    S1_and1 --> S1_leaf1
    S1_and1 --> S1_leaf2
    S1_and1 --> S1_leaf3
    S1_sub2 --> S1_leaf4
    S1_sub2 --> S1_leaf5
    S1_sub3 --> S1_leaf6
    S1_sub3 --> S1_leaf7

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S1_root goal
    class S1_and1 andGate
    class S1_or1 orGate
    class S1_sub1,S1_sub2,S1_sub3 subGoal
    class S1_leaf1,S1_leaf2,S1_leaf3,S1_leaf4,S1_leaf5,S1_leaf6,S1_leaf7 leaf
```
