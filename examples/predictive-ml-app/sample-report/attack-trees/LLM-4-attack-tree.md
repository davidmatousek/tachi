---
finding: "LLM-4"
component: "Weight Checkpoint Storage"
category: "model-theft"
risk_level: "Critical"
pattern_category: 14
owasp_reference: "OWASP ML06:2023 (artifact-side, shared with LLM-3)"
classification: "confidential"
---

# Attack Tree — LLM-4: Weight Checkpoint Storage Tampering

**Goal**: Overwrite production model weights in-place via mutable storage between training and serving.

```mermaid
graph TD
    G[Goal: Tamper Production Weights In-Place]
    G --> A1[Compromise Storage Write Access]
    G --> A2[Overwrite Weights]
    G --> A3[Serving Tier Loads Tampered Weights]

    A1 --> B1[Stolen ML-engineering credentials]
    A1 --> B2[No write-once-read-many policy on bucket]

    A2 --> C1[Replace weight file in mutable S3 path]
    A2 --> C2[No per-write audit logging]
    A2 --> C3[No immutability lock]

    A3 --> D1[MLflow registry references tampered file]
    A3 --> D2[Prediction API loads at startup]
    A3 --> D3[No SHA-256 verification at load time]
    A3 --> D4[No signature verification at load time]

    style G fill:#d4183d,color:#fff
    style D4 fill:#ff6b6b
```

## Mitigations

- Apply S3 Object Lock or equivalent write-once-read-many policy on production weight artifacts.
- Audit-log every write/read with actor identity.
- Verify SHA-256 digest at model-load time on the prediction API.
- Sign every promoted checkpoint with KMS-backed key; reject load on signature mismatch.

## References

- OWASP ML06:2023 — AI Supply Chain Attacks (artifact-side facet)
- MITRE ATT&CK T1195 — Supply Chain Compromise
