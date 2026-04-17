# Attack Tree: S-1 — Physician Identity Spoofing

**Component**: Physician | **Risk Level**: Critical | **Finding**: S-1

An attacker replays or forges physician credentials to gain unauthorized access to clinical recommendations and patient data.

```mermaid
flowchart TD
    S1_root["Gain unauthorized access to clinical recommendations via physician identity spoofing"]
    S1_or1{{"OR"}}
    S1_sub1["Credential replay attack using stolen session token"]
    S1_sub2["Forged JWT token with fabricated physician identity claims"]
    S1_sub3["Phishing attack to harvest live physician credentials"]
    S1_and1{{"AND"}}
    S1_and2{{"AND"}}
    S1_and3{{"AND"}}
    S1_leaf1["Obtain expired or stolen JWT token from network capture or data breach"]
    S1_leaf2["Replay token within validity window before expiry"]
    S1_leaf3["Obtain private key or signing secret used by identity provider"]
    S1_leaf4["Craft JWT payload with valid physician identity fields"]
    S1_leaf5["Sign forged token with obtained key material"]
    S1_leaf6["Craft convincing clinical portal phishing page"]
    S1_leaf7["Deliver phishing link via email spoofing clinical institution"]
    S1_leaf8["Capture submitted credentials and use before physician notices"]

    S1_root --> S1_or1
    S1_or1 --> S1_sub1
    S1_or1 --> S1_sub2
    S1_or1 --> S1_sub3
    S1_sub1 --> S1_and1
    S1_and1 --> S1_leaf1
    S1_and1 --> S1_leaf2
    S1_sub2 --> S1_and2
    S1_and2 --> S1_leaf3
    S1_and2 --> S1_leaf4
    S1_and2 --> S1_leaf5
    S1_sub3 --> S1_and3
    S1_and3 --> S1_leaf6
    S1_and3 --> S1_leaf7
    S1_and3 --> S1_leaf8

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S1_root goal
    class S1_and1,S1_and2,S1_and3 andGate
    class S1_or1 orGate
    class S1_sub1,S1_sub2,S1_sub3 subGoal
    class S1_leaf1,S1_leaf2,S1_leaf3,S1_leaf4,S1_leaf5,S1_leaf6,S1_leaf7,S1_leaf8 leaf
```
