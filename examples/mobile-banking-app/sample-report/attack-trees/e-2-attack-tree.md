# E-2: Unauthorized Money Transfer via Intent Hijacking and Privilege Escalation

**Component**: MoneyTransferActivity | **Risk Level**: Critical | **Finding**: E-2

A malicious co-installed app exploits the exported MoneyTransferActivity to initiate unauthorized fund transfers under the legitimate user's authenticated session, escalating from unprivileged-app context to full banking privileges.

```mermaid
flowchart TD
    E2_root["Execute Unauthorized Fund Transfer via Intent Hijacking"]
    E2_and1{{"AND"}}
    E2_sub1["Establish Attack Position"]
    E2_sub2["Exploit Missing Permission Gate"]
    E2_sub3["Execute Money-Movement Without Reauthentication"]
    E2_or1{{"OR"}}
    E2_leaf1["Install malicious app on victim device via social engineering"]
    E2_leaf2["Pre-install malicious app via device provisioning or MDM compromise"]
    E2_leaf3["Send crafted Intent with recipient_account and amount extras"]
    E2_leaf4["Confirm android:exported=true with no android:permission enforced"]
    E2_leaf5["Trigger MoneyTransferActivity without any biometric or PIN challenge"]
    E2_leaf6["Confirm no per-Intent caller verification via getCallingPackage"]

    E2_root --> E2_and1
    E2_and1 --> E2_sub1
    E2_and1 --> E2_sub2
    E2_and1 --> E2_sub3
    E2_sub1 --> E2_or1
    E2_or1 --> E2_leaf1
    E2_or1 --> E2_leaf2
    E2_sub2 --> E2_leaf3
    E2_sub2 --> E2_leaf4
    E2_sub3 --> E2_leaf5
    E2_sub3 --> E2_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class E2_root goal
    class E2_and1 andGate
    class E2_or1 orGate
    class E2_sub1,E2_sub2,E2_sub3 subGoal
    class E2_leaf1,E2_leaf2,E2_leaf3,E2_leaf4,E2_leaf5,E2_leaf6 leaf
```
