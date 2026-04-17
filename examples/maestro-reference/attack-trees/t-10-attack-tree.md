# Attack Tree: T-10 — FHIR Resource Store Patient Record Tampering

**Component**: FHIR Resource Store | **Risk Level**: Critical | **Finding**: T-10

An attacker with access to the FHIR Resource Store tampers with patient records, injecting false clinical data that corrupts all downstream clinical decision processes.

```mermaid
flowchart TD
    T10_root["Corrupt downstream clinical decisions by tampering with FHIR patient records"]
    T10_or1{{"OR"}}
    T10_sub1["Bypass Consent and De-identification Guardrail to perform unauthorized FHIR write"]
    T10_sub2["Exploit missing row-level integrity to modify existing patient record"]
    T10_and1{{"AND"}}
    T10_and2{{"AND"}}
    T10_leaf1["Obtain write-access token bypassing Consent Guardrail validation"]
    T10_leaf2["Identify target patient FHIR resource ID via prior reconnaissance"]
    T10_leaf3["Inject false clinical observations or medication records into patient resource"]
    T10_leaf4["Locate FHIR resource without row-level integrity checksum enforcement"]
    T10_leaf5["Construct FHIR update payload with adversarially crafted clinical values"]
    T10_leaf6["Submit update via direct FHIR store access bypassing audit controls"]

    T10_root --> T10_or1
    T10_or1 --> T10_sub1
    T10_or1 --> T10_sub2
    T10_sub1 --> T10_and1
    T10_and1 --> T10_leaf1
    T10_and1 --> T10_leaf2
    T10_and1 --> T10_leaf3
    T10_sub2 --> T10_and2
    T10_and2 --> T10_leaf4
    T10_and2 --> T10_leaf5
    T10_and2 --> T10_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T10_root goal
    class T10_and1,T10_and2 andGate
    class T10_or1 orGate
    class T10_sub1,T10_sub2 subGoal
    class T10_leaf1,T10_leaf2,T10_leaf3,T10_leaf4,T10_leaf5,T10_leaf6 leaf
```
