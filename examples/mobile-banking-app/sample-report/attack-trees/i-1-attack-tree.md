# I-1: Insecure Mobile Communication — Client-to-Backend MITM

**Component**: WellnessBank Android Client | **Risk Level**: Critical | **Finding**: I-1

An attacker on a rogue Wi-Fi access point performs a MITM attack against the unpinned TLS connection between the Android client and the backend API, intercepting session tokens and financial data.

```mermaid
flowchart TD
    I1_root["Intercept Session Tokens and Financial Data via MITM on Backend Channel"]
    I1_and1{{"AND"}}
    I1_sub1["Position Attacker on Network Path"]
    I1_sub2["Break Unpinned TLS Connection"]
    I1_sub3["Extract Target Data"]
    I1_or1{{"OR"}}
    I1_or2{{"OR"}}
    I1_leaf1["Deploy rogue Wi-Fi access point in public location"]
    I1_leaf2["Perform ARP spoofing on shared network segment"]
    I1_leaf3["Deploy TLS intercepting proxy with custom CA certificate"]
    I1_leaf4["Install custom CA via MDM or social engineering to bypass OS trust"]
    I1_leaf5["Capture bearer token from Authorization header in intercepted traffic"]
    I1_leaf6["Extract transaction payloads and account balances from response bodies"]

    I1_root --> I1_and1
    I1_and1 --> I1_sub1
    I1_and1 --> I1_sub2
    I1_and1 --> I1_sub3
    I1_sub1 --> I1_or1
    I1_or1 --> I1_leaf1
    I1_or1 --> I1_leaf2
    I1_sub2 --> I1_or2
    I1_or2 --> I1_leaf3
    I1_or2 --> I1_leaf4
    I1_sub3 --> I1_leaf5
    I1_sub3 --> I1_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I1_root goal
    class I1_and1 andGate
    class I1_or1,I1_or2 orGate
    class I1_sub1,I1_sub2,I1_sub3 subGoal
    class I1_leaf1,I1_leaf2,I1_leaf3,I1_leaf4,I1_leaf5,I1_leaf6 leaf
```
