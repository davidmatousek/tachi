# T-3: Mobile IPC Input Validation — Intent Hijacking into Money Movement

**Component**: MoneyTransferActivity | **Risk Level**: Critical | **Finding**: T-3

A malicious co-installed application sends a crafted Android Intent to the exported MoneyTransferActivity, directly invoking the money-movement business logic with attacker-controlled recipient and amount parameters.

```mermaid
flowchart TD
    T3_root["Tamper with Money-Movement Flow via Crafted Intent to Exported Activity"]
    T3_and1{{"AND"}}
    T3_sub1["Establish Delivery Position"]
    T3_sub2["Craft Malicious Intent Payload"]
    T3_sub3["Exploit Missing Validation on Entry"]
    T3_or1{{"OR"}}
    T3_leaf1["Install attacker-controlled app on victim device via sideloading"]
    T3_leaf2["Use ADB shell to send Intent directly from connected computer"]
    T3_leaf3["Construct Intent with recipient_account and amount extras set to attacker values"]
    T3_leaf4["Confirm android:exported=true and no android:permission in manifest"]
    T3_leaf5["Verify no Intent extra schema validation at Activity entry point"]
    T3_leaf6["Confirm no re-authentication triggered on money-movement invocation"]

    T3_root --> T3_and1
    T3_and1 --> T3_sub1
    T3_and1 --> T3_sub2
    T3_and1 --> T3_sub3
    T3_sub1 --> T3_or1
    T3_or1 --> T3_leaf1
    T3_or1 --> T3_leaf2
    T3_sub2 --> T3_leaf3
    T3_sub2 --> T3_leaf4
    T3_sub3 --> T3_leaf5
    T3_sub3 --> T3_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T3_root goal
    class T3_and1 andGate
    class T3_or1 orGate
    class T3_sub1,T3_sub2,T3_sub3 subGoal
    class T3_leaf1,T3_leaf2,T3_leaf3,T3_leaf4,T3_leaf5,T3_leaf6 leaf
```
