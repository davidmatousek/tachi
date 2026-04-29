# I-2: Inadequate Mobile Privacy Controls — Screen Capture and PII Leakage

**Component**: WellnessBank Android Client | **Risk Level**: Critical | **Finding**: I-2

An attacker exploits the absence of FLAG_SECURE and privacy controls to capture financial PII from the device screen, Android recents, or analytics telemetry without any access to the encrypted data stores.

```mermaid
flowchart TD
    I2_root["Capture Customer Financial PII Without Accessing Encrypted Data Stores"]
    I2_or1{{"OR"}}
    I2_sub1["Screen Capture via Recents or Recording"]
    I2_sub2["Harvest PII from Uncontrolled Analytics Egress"]
    I2_sub3["Recover PII from Expired Cache Without TTL"]
    I2_and1{{"AND"}}
    I2_leaf1["Access Android recents screen showing financial Activity thumbnail"]
    I2_leaf2["Use screen-recording app or ADB screenrecord on unlocked device"]
    I2_leaf3["Intercept analytics telemetry lacking consent gate on untrusted network"]
    I2_leaf4["Confirm absence of FLAG_SECURE on transaction-history Activity Window"]
    I2_leaf5["Extract stale PII records from WellnessBankLocalDB without TTL expiry"]

    I2_root --> I2_or1
    I2_or1 --> I2_sub1
    I2_or1 --> I2_sub2
    I2_or1 --> I2_sub3
    I2_sub1 --> I2_and1
    I2_and1 --> I2_leaf1
    I2_and1 --> I2_leaf4
    I2_sub1 --> I2_leaf2
    I2_sub2 --> I2_leaf3
    I2_sub3 --> I2_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I2_root goal
    class I2_and1 andGate
    class I2_or1 orGate
    class I2_sub1,I2_sub2,I2_sub3 subGoal
    class I2_leaf1,I2_leaf2,I2_leaf3,I2_leaf4,I2_leaf5 leaf
```
