# I-6: Insecure Mobile Communication — Payment SDK MITM

**Component**: WellnessPaySDK | **Risk Level**: High | **Finding**: I-6

An attacker intercepts the unpinned TLS connection between WellnessPaySDK and the Third-Party Payment Provider, capturing or modifying payment authorization requests containing card data and transaction amounts.

```mermaid
flowchart TD
    I6_root["Intercept or Modify Payment Authorization Request via MITM"]
    I6_and1{{"AND"}}
    I6_sub1["Position on Network Path"]
    I6_sub2["Break Unpinned TLS on Payment SDK Channel"]
    I6_or1{{"OR"}}
    I6_leaf1["Deploy rogue Wi-Fi access point near target user location"]
    I6_leaf2["Perform ARP spoofing on shared network to redirect payment SDK traffic"]
    I6_leaf3["Deploy TLS intercepting proxy confirming no certificate pin on SDK egress"]
    I6_leaf4["Capture payment authorization request containing card data"]
    I6_leaf5["Modify transaction amount or redirect recipient account in intercepted request"]

    I6_root --> I6_and1
    I6_and1 --> I6_sub1
    I6_and1 --> I6_sub2
    I6_sub1 --> I6_or1
    I6_or1 --> I6_leaf1
    I6_or1 --> I6_leaf2
    I6_sub2 --> I6_leaf3
    I6_sub2 --> I6_leaf4
    I6_sub2 --> I6_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I6_root goal
    class I6_and1 andGate
    class I6_or1 orGate
    class I6_sub1,I6_sub2 subGoal
    class I6_leaf1,I6_leaf2,I6_leaf3,I6_leaf4,I6_leaf5 leaf
```
