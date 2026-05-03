---
finding: "S-1"
component: "Merchant Transaction Submitter"
category: "spoofing"
risk_level: "Critical"
classification: "confidential"
---

# Attack Tree — S-1: Merchant Identity Spoofing on Prediction-API Boundary

```mermaid
graph TD
    G[Goal: Impersonate Legitimate Merchant]
    G --> A1[Steal API Token]
    G --> A2[Replay Token]
    G --> A3[Submit Attacker Transactions Under Victim Identity]

    A1 --> B1[Phish merchant credentials]
    A1 --> B2[Compromise merchant CI runner]

    A2 --> C1[Token has no IP/device binding]
    A2 --> C2[No mTLS enforced on boundary]

    A3 --> D1[Flood prediction API under victim identity]
    A3 --> D2[Harvest fraud-score signal from training-set queries]

    style G fill:#d4183d,color:#fff
```

## Mitigations
- Issue short-lived OAuth/JWT tokens bound to merchant IP/device fingerprint.
- Enforce mTLS on merchant→prediction-API trust-boundary crossing.
- Apply token revocation lists.
