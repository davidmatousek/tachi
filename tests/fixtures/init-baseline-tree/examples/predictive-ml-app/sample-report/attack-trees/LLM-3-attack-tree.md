---
finding: "LLM-3"
component: "MLflow Model Registry"
category: "model-theft"
risk_level: "Critical"
pattern_category: 14
owasp_reference: "OWASP ML06:2023 (artifact-side)"
classification: "confidential"
---

# Attack Tree — LLM-3: Predictive-ML Artifact Supply Chain (MLflow Registry)

**Goal**: Inject a backdoored model artifact into the production prediction-serving tier via the MLflow registry promotion gate.

```mermaid
graph TD
    G[Goal: Backdoor Production Model via Registry]
    G --> A1[Compromise ML-Engineering Credentials]
    G --> A2[Push Backdoored Artifact]
    G --> A3[Promote to Production]
    G --> A4[Inference Fleet Loads Backdoor]

    A1 --> B1[Stolen API key]
    A1 --> B2[Compromised CI runner]
    A1 --> B3[Insider with write access]

    A2 --> C1[Train backdoored model with hidden trigger]
    A2 --> C2[Push to registry as new version]
    A2 --> C3[No signed-artifact policy enforced]

    A3 --> D1[Single-API-call promotion]
    A3 --> D2[No PR review or two-person sign-off]
    A3 --> D3[No cryptographic attestation required]

    A4 --> E1[Prediction API loads weights at next deploy]
    A4 --> E2[No load-time integrity verification]
    A4 --> E3[Backdoor activates on hidden trigger]
    A4 --> E4[Fraud-determination compromised on attacker-chosen merchants]

    style G fill:#d4183d,color:#fff
    style E4 fill:#ff6b6b
```

## Attack Steps

1. **Compromise credentials**: Attacker obtains ML-engineering service-account credentials via stolen API key, CI-runner compromise, or insider access.
2. **Push backdoor**: Attacker pushes a backdoored model checkpoint to the MLflow registry.
3. **Promote**: Single API call promotes the backdoored artifact to production — no PR review, no two-person sign-off, no cryptographic attestation requirement.
4. **Deploy**: At next deploy, the FraudDetectionML Prediction API loads weights from the registry without verifying signature, hash, or attestation. Backdoor activates on inputs matching the hidden trigger pattern.

## Mitigations

- Enforce signed-artifact policy: require Sigstore-style or KMS-backed cryptographic attestation on every promoted artifact.
- Apply registry IAM with promotion-gate review: pull-request review and two-person sign-off on every staging-to-production promotion.
- Install integrity verification at model-load time on the prediction API.
- Use immutable artifact storage with audit logging on production weights.

## References

- OWASP ML06:2023 — AI Supply Chain Attacks (artifact-side facet per ADR-035 Decision 4)
- MITRE ATT&CK T1195 + T1195.001 + T1195.002 — Supply Chain Compromise
