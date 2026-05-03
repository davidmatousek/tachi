# T-1: Mobile Supply Chain Integrity — Analytics SDK Compromise

**Component**: WellnessAnalyticsSDK | **Risk Level**: High | **Finding**: T-1

An attacker compromises the WellnessAnalyticsSDK supply chain by exploiting the floating version constraint and absent artifact checksum verification, injecting malicious code that executes inside the application's full security context.

```mermaid
flowchart TD
    T1_root["Inject Malicious Code via Compromised Analytics SDK Supply Chain"]
    T1_and1{{"AND"}}
    T1_sub1["Compromise SDK Distribution Channel"]
    T1_sub2["Exploit Absent Integrity Verification in Build"]
    T1_leaf1["Compromise analytics SDK maintainer account or repository"]
    T1_leaf2["Publish malicious SDK version with injected credential-harvesting code"]
    T1_leaf3["Confirm floating version constraint in Gradle causes auto-update to malicious version"]
    T1_leaf4["Confirm no checksum or SLSA attestation verified at Gradle ingestion time"]
    T1_leaf5["Malicious SDK executes in app process and exfiltrates SharedPreferences token"]

    T1_root --> T1_and1
    T1_and1 --> T1_sub1
    T1_and1 --> T1_sub2
    T1_sub1 --> T1_leaf1
    T1_sub1 --> T1_leaf2
    T1_sub2 --> T1_leaf3
    T1_sub2 --> T1_leaf4
    T1_sub2 --> T1_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T1_root goal
    class T1_and1 andGate
    class T1_sub1,T1_sub2 subGoal
    class T1_leaf1,T1_leaf2,T1_leaf3,T1_leaf4,T1_leaf5 leaf
```
