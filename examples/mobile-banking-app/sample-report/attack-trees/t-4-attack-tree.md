# T-4: Insufficient Mobile Binary Protections — No Obfuscation or Anti-Tampering

**Component**: WellnessBank Android Client | **Risk Level**: Critical | **Finding**: T-4

An attacker uses dynamic instrumentation tooling to hook security-critical functions in the unobfuscated release APK, bypassing client-side controls and extracting embedded secrets.

```mermaid
flowchart TD
    T4_root["Hook Security-Critical Functions and Extract Secrets from Unprotected APK"]
    T4_or1{{"OR"}}
    T4_sub1["Dynamic Instrumentation via Frida"]
    T4_sub2["Static Reverse Engineering via Decompilation"]
    T4_sub3["Root-Based Runtime Bypass"]
    T4_and1{{"AND"}}
    T4_and2{{"AND"}}
    T4_leaf1["Identify no ProGuard obfuscation in release APK via class name inspection"]
    T4_leaf2["Attach Frida script targeting auth and session-handling functions"]
    T4_leaf3["Extract embedded API keys and intercept session token generation"]
    T4_leaf4["Decompile release APK using jadx or apktool on unobfuscated binary"]
    T4_leaf5["Locate and extract hardcoded secrets from readable class files"]
    T4_leaf6["Root device and bypass client-side root detection stub"]
    T4_leaf7["Invoke restricted security functions without triggered anti-tamper response"]

    T4_root --> T4_or1
    T4_or1 --> T4_sub1
    T4_or1 --> T4_sub2
    T4_or1 --> T4_sub3
    T4_sub1 --> T4_and1
    T4_and1 --> T4_leaf1
    T4_and1 --> T4_leaf2
    T4_and1 --> T4_leaf3
    T4_sub2 --> T4_and2
    T4_and2 --> T4_leaf4
    T4_and2 --> T4_leaf5
    T4_sub3 --> T4_leaf6
    T4_sub3 --> T4_leaf7

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T4_root goal
    class T4_and1,T4_and2 andGate
    class T4_or1 orGate
    class T4_sub1,T4_sub2,T4_sub3 subGoal
    class T4_leaf1,T4_leaf2,T4_leaf3,T4_leaf4,T4_leaf5,T4_leaf6,T4_leaf7 leaf
```
