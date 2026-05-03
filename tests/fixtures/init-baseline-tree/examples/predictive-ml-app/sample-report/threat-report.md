---
classification: "confidential"
date: "2026-04-28"
run_id: "2023-11-14T22-13-20"
source_threats: "threats.md"
schema_version: "1.4"
---

# Threat Report — Predictive-ML Application (F-6 ML Top 10 Coverage)

## Executive Summary

This threat model evaluates the FraudDetectionML predictive-ML application — a hypothetical fraud-detection classifier scoring financial transactions in near-real-time — against the F-6 ML Top 10 Coverage Bundle (Feature 232) detection surface. The architecture exhibits all five predictive-ML topology indicators per FR-016: a training pipeline ingesting from a public dataset repository alongside an internal merchant transaction history, a fine-tuning step pulling pretrained weights from HuggingFace Hub without checksum verification, an MLflow MLOps model registry promoting versioned artifacts to the prediction-serving tier, a prediction-API endpoint serving a classifier with no input-validation barrier and no per-tenant rate limit, and an active-learning feedback loop reading production prediction labels back into the training corpus through a labeling worker without integrity gates.

**43 findings** were identified across the architecture: 22 Critical, 11 High, 6 Medium, and 4 Low. The F-6 ML pattern surface emits **9 distinct ML findings** spanning **6 closed OWASP ML Top 10:2023 entries** — ML01 (T-10 adversarial-input manipulation), ML03 (LLM-1 model inversion), ML04 (LLM-2 membership inference), ML06 across two facets (LLM-3 + LLM-4 artifact-side; D-10 + D-11 corpus-side), ML07 (D-8 transfer-learning supply chain), ML08 (D-9 feedback-loop skewing).

The most urgent risks are concentrated at the FraudDetectionML Prediction API surface (T-10 + LLM-1 + LLM-2 form correlation group CG-1 — three disjoint architectural-tells per ADR-035 Decision 5), the artifact-side supply chain (LLM-3 + LLM-4 form CG-2 alongside corpus-side D-10 + D-11), and the transfer-learning + feedback-loop paths (CG-3 + CG-4). Each surface lacks the defense category specifically named by its OWASP ML Top 10 entry: adversarial-defense controls on the prediction API, DP-SGD / output-perturbation noise / query-rate throttling / extraction-pattern detection on the inference path, signed-artifact policy on the registry promotion gate, revision-pinning + signed-weight-artifact policy on the fine-tune load path, and labeler-trust scoring + held-out canary set on the feedback loop.

## Architecture Overview

The FraudDetectionML application is a multi-component predictive-ML topology spanning five trust zones:

- **User Zone (Untrusted)**: Merchant Transaction Submitter (sends scoring requests), Fraud Analyst (reads audit trail).
- **Application Zone (Trusted)**: FraudDetectionML Prediction API, Model Training Pipeline, Fine-Tuning Service, Active-Learning Feedback Loop, Production-Label Labeling Worker, Interaction Audit Log.
- **Data Layer (Trusted)**: Public Dataset Repository, Internal Merchant Transaction History, Feast Feature Store, MLflow Model Registry, Weight Checkpoint Storage.
- **External Services (Semi-Trusted)**: HuggingFace Hub Pretrained-Weights Registry.

Data flows traverse three critical paths: (1) the inference path (Merchant → Prediction API → Feast Feature Store + MLflow → response back to merchant), (2) the training path (Public Dataset Repo + Internal Merchant History → Training Pipeline → Feast + Fine-Tune Service → Weight Checkpoint Storage → MLflow), (3) the active-learning loopback (Prediction API → Active Learning → Labeling Worker → Internal Merchant History → next training cycle).

## Per-Category Threat Narrative

### Tampering (T-10) — Adversarial Input Manipulation Against Deployed Predictive Classifier (OWASP ML01:2023)

The FraudDetectionML Prediction API ingests raw user-controlled transaction features (`amount`, `merchant_id`, `geo_distance`, `time_delta`) without an input-validation barrier — no statistical-anomaly detection on input distributions, no distribution-shift monitoring at inference time, no input-space outlier rejection. The training pipeline does not declare adversarial training (no FGSM/PGD adversarial training, no input-perturbation augmentation, no robustness-aware training procedure). Confidence-thresholding HITL escalation is absent. Ensemble disagreement detection is absent.

**Attack scenario**: An attacker observes the classifier's outputs for legitimate fraudulent transactions, then crafts feature-space perturbations calibrated against the classifier's decision boundary that evade fraud detection while preserving the underlying fraudulent transaction. Sustained evasion at scale launders fraudulent transactions through the merchant network without triggering fraud-score alerts.

**Mitigation summary**: Apply adversarial training (FGSM/PGD) on the model side. Install statistical-anomaly detection at the inference Process input boundary. Enforce confidence-thresholding with HITL escalation. Deploy ensemble disagreement detection (≥2 models with disagreement-triggered escalation).

### Data Poisoning (D-8 + D-9 + D-10 + D-11) — Predictive-ML Training and Feedback-Loop Surfaces

**D-8: Transfer Learning Supply Chain (OWASP ML07:2023)**: The Fine-Tuning Service pulls pretrained weights from HuggingFace Hub via `from_pretrained()` without a `revision=` SHA pin, without SHA-256 digest comparison, without Sigstore-style attestation. LoRA adapters and PEFT modules are merged into the base model without integrity verification. Model-card provenance review is missing. An attacker who compromises an upstream maintainer account pushes a backdoored revision of a popular pretrained tabular-embedding model; the fine-tuning job pulls the latest revision and merges the poisoned weights into the production fraud-detection model. The backdoor activates on inputs matching a hidden feature pattern.

**D-9: Feedback-Loop Model Skewing (OWASP ML08:2023)**: The Active-Learning Feedback Loop reads production fraud-score predictions back into the Internal Merchant Transaction History training corpus through the Labeling Worker without integrity controls. The labeling tool accepts labels without trust scoring or consensus weighting. Drift-detection alarms on production inference distributions are missing. An attacker operates a network of merchant accounts submitting crafted transactions associated with a target fraud-evasion pattern; over two weeks, the model drifts toward classifying the target pattern as legitimate.

**D-10 + D-11: Predictive-ML Corpus Supply Chain (OWASP ML06:2023, corpus-side facet)**: The Training Pipeline ingests from the Public Dataset Repository without checksum manifest. The Feast Feature Store accepts writes from the training pipeline without IAM-enforced write-audit. Multiple service accounts can mutate engineered-feature values without audit trail. Dataset-checksum manifest is absent. An attacker who compromises any of these three surfaces — by publishing a poisoned-update of the public dataset, mutating a feature-store feature value, or compromising an internal training-corpus write path — can inject biased or backdoored training signal into the production fraud-detection classifier. **Disjoint architectural-tell from LLM-3 + LLM-4 (artifact-side facet) per ADR-035 Decision 4.**

### Model Theft (LLM-1 + LLM-2 + LLM-3 + LLM-4) — Predictive-ML Extraction and Artifact Integrity

**LLM-1: Model Inversion (OWASP ML03:2023)**: The FraudDetectionML Prediction API serves a classifier trained on sensitive merchant data without DP-SGD; output-perturbation noise injection is absent; query-rate throttling per tenant is absent; model-extraction-pattern detection is missing. An attacker who registers a developer account performs a black-box optimization campaign — iterating gradient-free queries against the endpoint — to find synthetic input transactions that maximize the model's predicted fraud probability for a target class. The reconstructed inputs preserve merchant-identifying features.

**LLM-2: Membership Inference (OWASP ML04:2023)**: The prediction API returns full-precision confidence values; label-only response mode is missing; DP-SGD on training is absent; confidence-output truncation is absent; training-data minimization is not enforced. An attacker with a list of candidate transactions submits each candidate to the API and observes the returned confidence; transactions in the original training set return characteristic high-confidence scores, allowing the attacker to identify which merchants and which transactions were flagged.

**LLM-3 + LLM-4: Predictive-ML Artifact Supply Chain (OWASP ML06:2023, artifact-side facet)**: The MLflow registry promotes artifacts without signed-artifact policy. Weight Checkpoint Storage is mutable. Integrity verification at model-load time is absent. An attacker who compromises any ML-engineering service-account credentials can push a backdoored model checkpoint into the registry and promote it to production. **Disjoint architectural-tell from D-10 + D-11 (corpus-side facet) per ADR-035 Decision 4.**

## Cross-Layer Attack Chains

Four correlation groups bind the F-6 ML findings into cohesive attack chains:

- **CG-1 (T-10 + LLM-1 + LLM-2)**: Same prediction API surface — adversarial-input evasion + training-data extraction via inversion + membership inference. Three disjoint findings per ADR-035 Decision 5; mitigation overlap on query-rate throttling per tenant. Partial mitigation on one defense surface does NOT close the others.
- **CG-2 (LLM-3 + LLM-4 + D-10 + D-11)**: ML06:2023 split across artifact-side (LLM-3 + LLM-4) and corpus-side (D-10 + D-11) per ADR-035 Decision 4. Two cohesive groups bound by shared OWASP framework anchor but disjoint mitigation vocabularies.
- **CG-3 (D-8 + T-8 + S-5 + S-6)**: Fine-Tuning Service supply chain — transfer-learning poisoning + weight-tampering + HuggingFace-Hub-spoofing + DNS/BGP redirect. Mitigation overlap on signed-weight-artifact policy + revision-pinning.
- **CG-4 (D-9 + T-9 + E-5)**: Active-Learning Feedback Loop — feedback-loop skewing + labeling-worker tampering + elevation-of-privilege via the loopback path.

## Prioritized Remediation Roadmap

### Phase 1 — Inference Path Hardening (Critical)

1. Apply DP-SGD on training with bounded ε ≤ 8.0 (addresses LLM-1 + LLM-2 simultaneously).
2. Apply confidence-output truncation on prediction-API responses and provide label-only response mode (addresses LLM-2 directly; provides partial mitigation for LLM-1).
3. Install per-tenant query-rate throttling on the prediction API gateway (addresses LLM-1 + LLM-2; partially addresses D-1).
4. Apply adversarial training (FGSM/PGD) and statistical-anomaly detection at the prediction-API input boundary (addresses T-10).
5. Deploy ensemble disagreement detection (≥2 models with HITL escalation) for fraud-determination decisions (addresses T-10 + LLM-1 robustness).

### Phase 2 — Supply Chain Integrity (Critical)

6. Enforce signed-artifact policy at the MLflow promotion gate; require Sigstore-style or KMS-backed attestation (addresses LLM-3).
7. Apply S3 Object Lock or equivalent write-once-read-many policy on Weight Checkpoint Storage (addresses LLM-4 + T-6).
8. Verify integrity at model-load time on the FraudDetectionML Prediction API (addresses LLM-3 + LLM-4 + E-1).
9. Pin every fine-tuning load by SHA: HuggingFace `from_pretrained(..., revision="<sha>")` with hash verification (addresses D-8 + T-8).
10. Maintain an allowlist of trusted pretrained-weight sources (addresses D-8 + S-5).

### Phase 3 — Corpus and Feature Store Integrity (Critical)

11. Maintain dataset-checksum manifest with reproducibility verification across all training-corpus inputs (addresses D-10 + T-2).
12. Apply IAM-enforced write-audit on Feast Feature Store and Internal Merchant Transaction History (addresses D-11 + T-3 + T-4 + S-4).
13. Require model-card review as a promotion gate for every model entering production (addresses D-10 + D-8).

### Phase 4 — Feedback-Loop Integrity (Critical)

14. Install feedback-data integrity gates with anomaly detection on label distribution drift (addresses D-9 + T-9 + E-5).
15. Apply labeler-trust scoring with reputation-based weighting in HITL labeling tools (addresses D-9 + T-9).
16. Run periodic retraining-data audit with held-out canaries anchored outside the loopback path (addresses D-9 + E-5).

### Phase 5 — Access Control and Operational Hygiene (High)

17. Apply least-privilege IAM across all predictive-ML components (addresses E-1 through E-5).
18. Enable non-repudiable audit logging across all components (addresses R-1 through R-7).
19. Apply rate limiting and capacity controls on inference, training, and registry surfaces (addresses D-1 through D-6).

## References

- OWASP Machine Learning Security Top 10:2023 — https://owasp.org/www-project-machine-learning-security-top-10/
- OWASP ML01:2023 — Input Manipulation Attack
- OWASP ML03:2023 — Model Inversion Attack
- OWASP ML04:2023 — Membership Inference Attack
- OWASP ML06:2023 — AI Supply Chain Attacks (split across two facets per ADR-035)
- OWASP ML07:2023 — Transfer Learning Attack
- OWASP ML08:2023 — Model Skewing
- MITRE ATLAS AML.T0024 — Exfiltration via ML Inference API
- MITRE ATLAS AML.T0018 — Backdoor ML Model
- MITRE ATLAS AML.T0020 — Poison Training Data
- MITRE ATT&CK T1195 + T1195.001 + T1195.002 — Supply Chain Compromise
- ADR-035 — F-6 ML Top 10 Coverage Bundle architectural decisions

**End of threat report.**
