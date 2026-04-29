# I-4: Insufficient Mobile Cryptography — Weak PIN-Based Key Derivation

**Component**: WellnessBank Android Client | **Risk Level**: Critical | **Finding**: I-4

An attacker obtains encrypted data from the device and brute-forces the 4-digit PIN space in under one second, recovering the derived key and decrypting all protected credentials and data.

```mermaid
flowchart TD
    I4_root["Break PIN-Derived Encryption Key via Offline Brute-Force Attack"]
    I4_and1{{"AND"}}
    I4_sub1["Acquire Encrypted Data from Device"]
    I4_sub2["Exploit Weak KDF Parameters"]
    I4_sub3["Recover Plaintext Credentials"]
    I4_or1{{"OR"}}
    I4_leaf1["Extract credential cache from rooted device or ADB backup"]
    I4_leaf2["Recover encrypted data via Google Drive backup"]
    I4_leaf3["Enumerate all 10000 PINs using GPU-accelerated PBKDF2 cracking tool"]
    I4_leaf4["Exploit absence of per-device salt to reuse precomputed tables"]
    I4_leaf5["Confirm SHA1 with 1000 iterations requires under 1 second to exhaust"]
    I4_leaf6["Decrypt recovered data with cracked PIN-derived key"]

    I4_root --> I4_and1
    I4_and1 --> I4_sub1
    I4_and1 --> I4_sub2
    I4_and1 --> I4_sub3
    I4_sub1 --> I4_or1
    I4_or1 --> I4_leaf1
    I4_or1 --> I4_leaf2
    I4_sub2 --> I4_leaf3
    I4_sub2 --> I4_leaf4
    I4_sub2 --> I4_leaf5
    I4_sub3 --> I4_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I4_root goal
    class I4_and1 andGate
    class I4_or1 orGate
    class I4_sub1,I4_sub2,I4_sub3 subGoal
    class I4_leaf1,I4_leaf2,I4_leaf3,I4_leaf4,I4_leaf5,I4_leaf6 leaf
```
