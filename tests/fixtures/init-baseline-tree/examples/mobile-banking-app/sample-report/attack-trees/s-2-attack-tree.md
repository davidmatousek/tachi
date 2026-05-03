# S-2: Insecure Mobile Authentication — No Biometric Step-Up on Money Movement

**Component**: WellnessBank Android Client | **Risk Level**: Critical | **Finding**: S-2

An attacker who obtains a valid session token executes fund transfers without any biometric or secondary-factor challenge, exploiting the absence of step-up authentication on sensitive operations.

```mermaid
flowchart TD
    S2_root["Execute Fund Transfers Using Stolen Session Token Without Biometric Challenge"]
    S2_and1{{"AND"}}
    S2_sub1["Obtain Valid Session Token"]
    S2_sub2["Exploit Absent Step-Up Authentication"]
    S2_sub3["Complete Money-Movement Without Secondary Factor"]
    S2_or1{{"OR"}}
    S2_leaf1["Extract token from unencrypted SharedPreferences on rooted device"]
    S2_leaf2["Intercept token via MITM on unpinned TLS connection"]
    S2_leaf3["Issue money-movement API request with stolen bearer token"]
    S2_leaf4["Confirm no BiometricPrompt step-up is enforced on transfer endpoint"]
    S2_leaf5["Confirm no challenge-response or per-transaction token required"]
    S2_leaf6["Successfully submit transaction to backend without additional verification"]

    S2_root --> S2_and1
    S2_and1 --> S2_sub1
    S2_and1 --> S2_sub2
    S2_and1 --> S2_sub3
    S2_sub1 --> S2_or1
    S2_or1 --> S2_leaf1
    S2_or1 --> S2_leaf2
    S2_sub2 --> S2_leaf3
    S2_sub2 --> S2_leaf4
    S2_sub3 --> S2_leaf5
    S2_sub3 --> S2_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S2_root goal
    class S2_and1 andGate
    class S2_or1 orGate
    class S2_sub1,S2_sub2,S2_sub3 subGoal
    class S2_leaf1,S2_leaf2,S2_leaf3,S2_leaf4,S2_leaf5,S2_leaf6 leaf
```
