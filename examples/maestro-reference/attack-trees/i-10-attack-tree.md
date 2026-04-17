# Attack Tree: I-10 — FHIR Resource Store PHI Unauthorized Disclosure

**Component**: FHIR Resource Store | **Risk Level**: Critical | **Finding**: I-10

Patient PHI stored in the FHIR Resource Store may be disclosed through unauthorized read operations by agents with overly broad access, FHIR injection attacks, or missing PHI encryption at rest.

```mermaid
flowchart TD
    I10_root["Disclose patient PHI from FHIR Resource Store via unauthorized read or injection attack"]
    I10_or1{{"OR"}}
    I10_sub1["Execute FHIR injection to retrieve unauthorized patient records"]
    I10_sub2["Exploit overly broad agent RBAC to access PHI beyond authorized scope"]
    I10_sub3["Access unencrypted PHI at rest via storage-level compromise"]
    I10_and1{{"AND"}}
    I10_and2{{"AND"}}
    I10_leaf1["Identify FHIR query endpoint accepting unsanitized search parameters"]
    I10_leaf2["Craft FHIR injection payload targeting expanded patient record scope"]
    I10_leaf3["Identify agent service account with over-provisioned FHIR read permissions"]
    I10_leaf4["Issue FHIR read query for patients outside the agent session scope"]
    I10_leaf5["Obtain storage-level access credentials for FHIR database backend"]
    I10_leaf6["Read unencrypted PHI records directly from storage layer"]

    I10_root --> I10_or1
    I10_or1 --> I10_sub1
    I10_or1 --> I10_sub2
    I10_or1 --> I10_sub3
    I10_sub1 --> I10_and1
    I10_and1 --> I10_leaf1
    I10_and1 --> I10_leaf2
    I10_sub2 --> I10_and2
    I10_and2 --> I10_leaf3
    I10_and2 --> I10_leaf4
    I10_sub3 --> I10_leaf5
    I10_sub3 --> I10_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I10_root goal
    class I10_and1,I10_and2 andGate
    class I10_or1 orGate
    class I10_sub1,I10_sub2,I10_sub3 subGoal
    class I10_leaf1,I10_leaf2,I10_leaf3,I10_leaf4,I10_leaf5,I10_leaf6 leaf
```
