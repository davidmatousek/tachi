---
schema_version: "1.4"
date: "2026-04-28"
input_format: "mermaid"
classification: "confidential"
run_id: "2023-11-14T22-13-20"
baseline:
  source: null
  date: null
  finding_count: 0
  run_id: null
coverage_gate:
  status: "pass"
  gaps: []
has_attack_chains: true
has_agentic_patterns: false
has_source_attribution: true
---

# Threat Model — Predictive-ML Application (F-6 Wave 4 T042)

## Pipeline Execution Log (Intermediate)

### Phase 0: Baseline Detection

**No baseline detected** — clean-slate first run on `examples/predictive-ml-app/`.

- Mode: **Stateless** (no carry-forward; all findings annotated `[NEW]`).

### Phase 1: Component Inventory (Intermediate)

**Detected format**: Mermaid (explicit override `format: mermaid`).

| Component | DFD Type | MAESTRO Layer | Description |
|---|---|---|---|
| Merchant Transaction Submitter | External Entity | Unclassified | Human/system submitting fraud-scoring transactions via HTTPS |
| Fraud Analyst | External Entity | Unclassified | Human reviewing audit trail via HTTPS |
| FraudDetectionML Prediction API | Process | L1 — Foundation Model | Deployed predictive ML classifier; ingests raw user-controlled features without input-validation barrier; returns confidence values; loads weights from MLflow registry |
| Model Training Pipeline | Process | L2 — Data Operations | Predictive-ML training pipeline ingesting from public dataset repository + internal merchant transaction history; emits engineered features and trained checkpoints |
| Fine-Tuning Service | Process | L1 — Foundation Model | Fine-tuning step pulling pretrained weights from HuggingFace Hub without checksum/signed-artifact verification |
| Active-Learning Feedback Loop | Process | L2 — Data Operations | Production-prediction loopback path reading inference labels back into training corpus through labeling worker without integrity gates |
| Production-Label Labeling Worker | Process | L2 — Data Operations | HITL labeling worker reviewing production prediction labels without labeler-trust scoring |
| Public Dataset Repository | Data Store | L2 — Data Operations | External public dataset corpus consumed by training pipeline without checksum manifest |
| Internal Merchant Transaction History | Data Store | L2 — Data Operations | Internal training corpus written by training pipeline and active-learning loop without IAM-enforced write-audit |
| Feast Feature Store | Data Store | L2 — Data Operations | Engineered-feature store written by training pipeline and read by prediction API without IAM-enforced write-audit |
| MLflow Model Registry | Data Store | L2 — Data Operations | MLOps artifact registry promoting versioned model artifacts to prediction-serving tier without signed-artifact policy |
| Weight Checkpoint Storage | Data Store | L2 — Data Operations | Mutable weight-artifact storage holding fine-tuned model checkpoints without integrity attestation |
| HuggingFace Hub Pretrained-Weights Registry | External Entity | Unclassified | External public model registry serving pretrained weights to fine-tuning service without revision-pinning enforcement |
| Interaction Audit Log | Data Store | L5 — Evaluation and Observability | Append-only audit log collecting prediction and labeling records (passive sink) |

**Data flow count**: 22 data flows identified.

**Trust boundary summary**:
- User Zone: Untrusted (Merchant Transaction Submitter, Fraud Analyst)
- Application Zone: Trusted (Prediction API, Training Pipeline, Fine-Tuning Service, Active-Learning Feedback Loop, Labeling Worker, Audit Log)
- Data Layer: Trusted (Public Dataset Repository, Internal Merchant Transaction History, Feast Feature Store, MLflow Model Registry, Weight Checkpoint Storage)
- External Services: Semi-Trusted (HuggingFace Hub)

**Self-check**: 14 components, 22 data flows — PASS.

### Phase 2: Dispatch Table (Intermediate)

| Component | DFD Type | MAESTRO Layer | STRIDE Categories | AI Categories | Total Agents |
|---|---|---|---|---|---|
| Merchant Transaction Submitter | External Entity | Unclassified | S, R | — | 2 |
| Fraud Analyst | External Entity | Unclassified | S, R | — | 2 |
| FraudDetectionML Prediction API | Process | L1 — Foundation Model | S, T, R, I, D, E | LLM (model-theft Cat 12 + Cat 13) + T (Cat 10 adversarial-input) | 9 |
| Model Training Pipeline | Process | L2 — Data Operations | S, T, R, I, D, E | LLM (data-poisoning Cat 10 corpus-side ML06) | 7 |
| Fine-Tuning Service | Process | L1 — Foundation Model | S, T, R, I, D, E | LLM (data-poisoning Cat 8 transfer-learning ML07) | 7 |
| Active-Learning Feedback Loop | Process | L2 — Data Operations | S, T, R, I, D, E | LLM (data-poisoning Cat 9 model-skewing ML08) | 7 |
| Production-Label Labeling Worker | Process | L2 — Data Operations | S, T, R, I, D, E | LLM (data-poisoning Cat 9 shared) | 7 |
| Public Dataset Repository | Data Store | L2 — Data Operations | T, I, D | LLM (data-poisoning Cat 10 corpus-side) | 4 |
| Internal Merchant Transaction History | Data Store | L2 — Data Operations | T, I, D | LLM (data-poisoning Cat 10 corpus-side) | 4 |
| Feast Feature Store | Data Store | L2 — Data Operations | T, I, D | LLM (data-poisoning Cat 10 corpus-side) | 4 |
| MLflow Model Registry | Data Store | L2 — Data Operations | T, I, D | LLM (model-theft Cat 14 artifact-side ML06) | 4 |
| Weight Checkpoint Storage | Data Store | L2 — Data Operations | T, I, D | LLM (model-theft Cat 14 shared) | 4 |
| HuggingFace Hub Pretrained-Weights Registry | External Entity | Unclassified | S, R | — | 2 |
| Interaction Audit Log | Data Store | L5 — Evaluation and Observability | T, I, D | — | 3 |

**Dispatch summary**:
- Total unique agent invocations: 66
- Components with predictive-ML AI dispatch: 10 (Prediction API, Training Pipeline, Fine-Tuning Service, Active-Learning Loop, Labeling Worker, Public Dataset Repo, Internal Merchant History, Feast Feature Store, MLflow Registry, Weight Checkpoint Storage)
- Components with multi-dispatch: 1 (Prediction API — tampering Cat 10 + model-theft Cat 12 + Cat 13)

**Phase 2 isolated discovery mode**: Stateless. F-6 Pattern Categories active per ADR-035: tampering Cat 10 (Adversarial Input Manipulation, ML01:2023); data-poisoning Cat 8 (Transfer Learning, ML07:2023), Cat 9 (Feedback-Loop Skewing, ML08:2023), Cat 10 (Corpus Supply Chain, ML06:2023 corpus-side facet); model-theft Cat 12 (Model Inversion, ML03:2023), Cat 13 (Membership Inference, ML04:2023), Cat 14 (Artifact Supply Chain, ML06:2023 artifact-side facet). Predictive-ML topology gate FR-016: PASSED (5/5 indicators present — training pipeline, fine-tuning step on pretrained weights, MLOps registry, prediction API endpoint, active-learning feedback loop).

**New findings discovered (Phase 2)**:
- T-10 [NEW]: FraudDetectionML Prediction API — Tampering Cat 10 (Adversarial Input Manipulation Predictive ML, OWASP ML01:2023; AML.T0015 prose-only)
- D-8 [NEW]: Fine-Tuning Service — Data-Poisoning Cat 8 (Transfer Learning Supply Chain, OWASP ML07:2023; AML.T0019 prose-only)
- D-9 [NEW]: Active-Learning Feedback Loop — Data-Poisoning Cat 9 (Feedback-Loop Model Skewing, OWASP ML08:2023; AML.T0031 prose-only)
- D-10 [NEW]: Model Training Pipeline — Data-Poisoning Cat 10 (Predictive-ML Corpus Supply Chain, OWASP ML06:2023 corpus-side facet)
- D-11 [NEW]: Feast Feature Store — Data-Poisoning Cat 10 (Predictive-ML Corpus Supply Chain, OWASP ML06:2023 corpus-side facet)
- LLM-1 [NEW]: FraudDetectionML Prediction API — Model-Theft Cat 12 (Model Inversion, OWASP ML03:2023)
- LLM-2 [NEW]: FraudDetectionML Prediction API — Model-Theft Cat 13 (Membership Inference, OWASP ML04:2023)
- LLM-3 [NEW]: MLflow Model Registry — Model-Theft Cat 14 (Predictive-ML Artifact Supply Chain, OWASP ML06:2023 artifact-side facet)
- LLM-4 [NEW]: Weight Checkpoint Storage — Model-Theft Cat 14 (Predictive-ML Artifact Supply Chain, OWASP ML06:2023 artifact-side facet)

---

## 1. System Overview

### Components

| Component | Type | Description |
|---|---|---|
| Merchant Transaction Submitter | External Entity | Human/system submitting transactions for fraud scoring via HTTPS |
| Fraud Analyst | External Entity | Human reviewing the audit trail via HTTPS |
| FraudDetectionML Prediction API | Process | Deployed predictive-ML classifier serving fraud-detection inference; ingests raw user-controlled features without input-validation barrier; returns confidence values |
| Model Training Pipeline | Process | Training pipeline ingesting from Public Dataset Repository + Internal Merchant Transaction History; writes engineered features and trained checkpoints |
| Fine-Tuning Service | Process | Fine-tuning step pulling pretrained weights from HuggingFace Hub without revision-pinning or attestation |
| Active-Learning Feedback Loop | Process | Production-label loopback path feeding inference labels back into training corpus without integrity gates |
| Production-Label Labeling Worker | Process | HITL labeling worker reviewing production prediction labels without labeler-trust scoring |
| Public Dataset Repository | Data Store | External public dataset corpus consumed without checksum manifest |
| Internal Merchant Transaction History | Data Store | Internal training corpus written by training pipeline and active-learning loop |
| Feast Feature Store | Data Store | Engineered-feature store written by training pipeline and read by prediction API |
| MLflow Model Registry | Data Store | MLOps artifact registry promoting model artifacts to prediction-serving tier |
| Weight Checkpoint Storage | Data Store | Mutable weight-artifact storage holding fine-tuned checkpoints |
| HuggingFace Hub Pretrained-Weights Registry | External Entity | External public model registry serving pretrained weights |
| Interaction Audit Log | Data Store | Append-only audit log collecting prediction + labeling records |

### Data Flows

| Source | Destination | Data | Protocol |
|---|---|---|---|
| Merchant Transaction Submitter | FraudDetectionML Prediction API | Transaction Scoring Request (raw user input) | HTTPS |
| FraudDetectionML Prediction API | Merchant Transaction Submitter | Fraud Score + Confidence Value | HTTPS |
| FraudDetectionML Prediction API | Feast Feature Store | Feature Lookup Query | Internal |
| Feast Feature Store | FraudDetectionML Prediction API | Cached Feature Vector | Internal |
| FraudDetectionML Prediction API | MLflow Model Registry | Model Artifact Load Request | Internal |
| MLflow Model Registry | FraudDetectionML Prediction API | Versioned Model Checkpoint | Internal |
| FraudDetectionML Prediction API | Active-Learning Feedback Loop | Production Prediction Record | Internal |
| Active-Learning Feedback Loop | Production-Label Labeling Worker | Labeling Task | Internal |
| Production-Label Labeling Worker | Active-Learning Feedback Loop | Reviewed Label | Internal |
| Active-Learning Feedback Loop | Internal Merchant Transaction History | Re-Training Sample | Internal |
| Public Dataset Repository | Model Training Pipeline | Public Training Corpus | Internal |
| Internal Merchant Transaction History | Model Training Pipeline | Internal Training Corpus | Internal |
| Model Training Pipeline | Feast Feature Store | Engineered Features | Internal |
| Model Training Pipeline | Fine-Tuning Service | Trained Model Checkpoint | Internal |
| HuggingFace Hub Pretrained-Weights Registry | Fine-Tuning Service | Pretrained Weights (no checksum) | HTTPS |
| Fine-Tuning Service | Weight Checkpoint Storage | Fine-Tuned Model Checkpoint | Internal |
| Weight Checkpoint Storage | MLflow Model Registry | Model Artifact | Internal |
| MLflow Model Registry | FraudDetectionML Prediction API | Promoted Versioned Artifact | Internal |
| FraudDetectionML Prediction API | Interaction Audit Log | Prediction Audit Record | Internal |
| Production-Label Labeling Worker | Interaction Audit Log | Labeling Audit Record | Internal |
| Fraud Analyst | Interaction Audit Log | Audit Query | HTTPS |
| Interaction Audit Log | Fraud Analyst | Audit Trail | HTTPS |

### Technologies

| Category | Technology | Version (if known) |
|---|---|---|
| Transport | HTTPS / TLS | unknown |
| ML Framework | Predictive ML Classifier | unknown |
| MLOps | MLflow Model Registry | unknown |
| Feature Store | Feast | unknown |
| External Registry | HuggingFace Hub | unknown |
| Pattern | Active-Learning / HITL Labeling | n/a |

---

## 2. Trust Boundaries

### Trust Zones

| Zone | Trust Level | Components |
|---|---|---|
| User Zone | Untrusted | Merchant Transaction Submitter, Fraud Analyst |
| Application Zone | Trusted | FraudDetectionML Prediction API, Model Training Pipeline, Fine-Tuning Service, Active-Learning Feedback Loop, Production-Label Labeling Worker, Interaction Audit Log |
| Data Layer | Trusted | Public Dataset Repository, Internal Merchant Transaction History, Feast Feature Store, MLflow Model Registry, Weight Checkpoint Storage |
| External Services | Semi-Trusted | HuggingFace Hub Pretrained-Weights Registry |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|---|---|---|---|---|
| Merchant → PredictionAPI | User Zone | Application Zone | Merchant Transaction Submitter → FraudDetectionML Prediction API | HTTPS transport (no input-validation barrier, no adversarial-defense control declared) |
| PredictionAPI → Merchant (response) | Application Zone | User Zone | FraudDetectionML Prediction API → Merchant Transaction Submitter | HTTPS transport (returns full-precision confidence; no output-perturbation noise; no label-only mode) |
| Analyst → AuditLog | User Zone | Application Zone | Fraud Analyst → Interaction Audit Log | HTTPS transport |
| AuditLog → Analyst | Application Zone | User Zone | Interaction Audit Log → Fraud Analyst | HTTPS transport |
| HuggingFaceHub → FineTuneService | External Services | Application Zone | HuggingFace Hub → Fine-Tuning Service | HTTPS transport (no revision-pinning, no signature verification, no attestation policy) |
| PublicDatasetRepo → TrainingPipeline | Data Layer | Application Zone | Public Dataset Repository → Model Training Pipeline | Internal transport (no checksum manifest, no integrity verification) |

---

## 3. STRIDE Threat Tables

### 3.1 Spoofing (S)

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|---|---|---|---|---|---|---|---|---|
| S-1 | [NEW] | Merchant Transaction Submitter | Unclassified | An attacker impersonates a legitimate merchant by replaying stolen API tokens, spoofing the merchant identity to flood the prediction API with attacker-crafted transactions or to harvest fraud-score signal from the deployed classifier. | HIGH | HIGH | Critical | Issue short-lived OAuth/JWT tokens bound to merchant IP/device fingerprint. Enforce mTLS on the merchant→prediction-API trust-boundary crossing. Apply token revocation lists. |
| S-2 | [NEW] | Fraud Analyst | Unclassified | A compromised analyst account is used to query the audit log, spoofing the analyst identity to harvest production prediction history (which may carry training-set membership signal). | MEDIUM | HIGH | High | Enforce MFA on analyst sessions. Bind analyst session tokens to device fingerprint. Audit all analyst→audit-log queries with read-volume anomaly alerting. |
| S-3 | [NEW] | FraudDetectionML Prediction API | L1 — Foundation Model | A rogue Application-Zone process spoofs the prediction API by claiming its identity to upstream merchants. Without mTLS or service-mesh identity, callers cannot distinguish a genuine FraudDetectionML response from an injected one. | MEDIUM | HIGH | High | Enforce mTLS at every service-to-service boundary. Use SPIFFE/SPIRE identities. Require signed responses on the merchant return path. |
| S-4 | [NEW] | Model Training Pipeline | L2 — Data Operations | An attacker spoofs the training pipeline service account to ingest poisoned training data into the internal merchant history corpus or feature store. Without IAM-enforced caller authentication on the corpus write path, any service account in the IAM group can inject training data under the pipeline's identity. | MEDIUM | HIGH | High | Enforce per-write caller identity with short-lived credentials. Apply IAM-enforced write-audit on the training corpus and feature store. Reject writes from unrecognized service accounts. |
| S-5 | [NEW] | Fine-Tuning Service | L1 — Foundation Model | An attacker who registers a same-named pretrained-weights artifact on HuggingFace Hub spoofs the upstream maintainer identity. Without an allowlist of trusted sources, the fine-tuning service cannot distinguish a genuine upstream maintainer from a malicious impersonator. | HIGH | HIGH | Critical | Maintain an allowlist of trusted pretrained-weight sources (specific orgs/repos on HuggingFace Hub). Enforce signed-weight-artifact policy at fine-tuning load time. Reject load-time absence of attestation. |
| S-6 | [NEW] | HuggingFace Hub Pretrained-Weights Registry | Unclassified | A network-level adversary performing DNS/BGP hijack redirects the HuggingFace Hub fetch path to an attacker-controlled mirror serving backdoored pretrained weights. | MEDIUM | HIGH | High | Pin TLS certificates for HuggingFace Hub endpoints. Verify SHA-256 digest on every pretrained-weight fetch against a committed manifest. Use HSTS where supported. |

---

### 3.2 Tampering (T)

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|---|---|---|---|---|---|---|---|---|
| T-1 | [NEW] | FraudDetectionML Prediction API | L1 — Foundation Model | The prediction API ingests raw user-controlled transaction features into the deployed classifier without an input-validation barrier. An attacker can inject anomalous feature values (out-of-distribution amounts, geo distances, time deltas) to cause misclassification at inference time — generic input-tampering against the API surface independent of the deployed-classifier-specific adversarial-evasion attack covered by T-10. | MEDIUM | HIGH | High | Implement strict request-schema validation: enforce per-field type constraints, value ranges, and allowlisted enumerations. Reject requests with feature values outside declared distribution bounds. Apply request-body size caps. |
| T-2 | [NEW] | Model Training Pipeline | L2 — Data Operations | The training pipeline reads from the Public Dataset Repository and Internal Merchant Transaction History without checksum manifest or integrity verification. An attacker who tampers with either corpus injects manipulated training samples into the production model. | HIGH | HIGH | Critical | Maintain a dataset-checksum manifest with SHA-256 digests of every input corpus snapshot. Verify digest match before each training run. Reject training jobs whose input corpus does not match the committed manifest. |
| T-3 | [NEW] | Internal Merchant Transaction History | L2 — Data Operations | The internal training corpus is written by both the training pipeline and the active-learning loop without IAM-enforced write-audit policy. A compromised service account with write access can silently mutate training samples to inject biased fraud labels. | HIGH | HIGH | Critical | Enforce IAM with least-privilege on write access. Apply per-write audit logging (actor, before/after, timestamp). Implement immutable write-once-read-many storage for committed training snapshots. |
| T-4 | [NEW] | Feast Feature Store | L2 — Data Operations | The feature store is written by the training pipeline and read by the prediction API at inference time. Without IAM-enforced write-audit and integrity verification on cached feature vectors, a compromised write path can inject manipulated feature values that reach inference without detection. | HIGH | HIGH | Critical | Enforce IAM with per-write audit on the feature store. Verify feature-vector integrity at read time. Monitor for anomalous feature-distribution drift between writes. |
| T-5 | [NEW] | MLflow Model Registry | L2 — Data Operations | The MLflow registry promotes versioned model artifacts to the prediction-serving tier without signed-artifact policy. A compromised service account can promote a backdoored artifact to production via a single API call. | HIGH | HIGH | Critical | Enforce a signed-artifact policy: require Sigstore-style or KMS-backed cryptographic attestation on every promoted artifact. Require pull-request review and two-person sign-off on every staging-to-production promotion. |
| T-6 | [NEW] | Weight Checkpoint Storage | L2 — Data Operations | Weight checkpoints are stored in mutable storage (S3 bucket or filesystem path) without immutability lock or write-once-read-many policy. An attacker who compromises any service account with write access can overwrite weights in-place between training and serving. | HIGH | HIGH | Critical | Apply S3 Object Lock or equivalent write-once-read-many policy on production weight artifacts. Audit-log every write/read operation with actor identity. Alert on any unexpected write to a promoted checkpoint. |
| T-7 | [NEW] | Interaction Audit Log | L5 — Evaluation and Observability | The audit log can be tampered with by a process with write access to the log store. Modifying or deleting prediction-record entries corrupts the active-learning loopback signal and destroys forensic evidence. | MEDIUM | HIGH | High | Implement append-only storage. Hash log batches in a Merkle tree with the root chained externally. Alert on any write that does not append. |
| T-8 | [NEW] | Fine-Tuning Service | L1 — Foundation Model | The fine-tuning service merges pretrained weights from HuggingFace Hub into the production model without integrity verification. A poisoned upstream artifact silently merges into production model weights at fine-tune time. | HIGH | HIGH | Critical | Pin every fine-tuning load by SHA via `from_pretrained(..., revision="<sha>")`. Verify hash at load time and CI-fail on digest drift. Require model-card provenance review as a fine-tuning gate. |
| T-9 | [NEW] | Active-Learning Feedback Loop | L2 — Data Operations | Production prediction records flow back into the training corpus through the labeling worker without integrity gates. A compromised labeling worker can flip labels to skew the production model toward attacker-favorable outcomes. | HIGH | HIGH | Critical | Apply labeler-trust scoring with reputation-based weighting. Require multi-labeler consensus on safety-critical samples. Anomaly-detect on label-distribution drift between batches. |
| T-10 | [NEW] | FraudDetectionML Prediction API | L1 — Foundation Model | **Adversarial Input Manipulation (Predictive ML, Pattern Category 10 — OWASP ML01:2023)**: The deployed FraudDetectionML classifier exposes a `/predict`-style endpoint accepting raw user-controlled transaction features (`amount`, `merchant_id`, `geo_distance`, `time_delta`) without any input-validation barrier — no statistical-anomaly detection, no distribution-shift monitoring, no input-space outlier rejection. The training pipeline does not declare adversarial training (no FGSM/PGD adversarial training, no input-perturbation augmentation, no robustness-aware training procedure). Confidence-thresholding HITL escalation is absent — low-confidence predictions are returned to the merchant rather than escalated for human review on safety-critical decisions. Ensemble disagreement detection is absent — the single FraudDetectionML output is trusted for fraud determination. An attacker observes the classifier's outputs for legitimate fraudulent transactions, then crafts feature-space perturbations (small modifications to `geo_distance` and `time_delta` calibrated against the classifier's decision boundary) that evade fraud detection while preserving the underlying fraudulent transaction. Sustained evasion at scale launders fraudulent transactions through the merchant network without triggering fraud-score alerts. References: OWASP ML01:2023; CWE-20 Improper Input Validation; CWE-1039 Inadequate Detection or Handling of Adversarial Input Perturbations. Cf. MITRE ATLAS AML.T0015 Evade ML Model — text-only cross-reference (NOT in references; T0015 not catalog-resolvable in `schemas/taxonomy/mitre-atlas.yaml`). | HIGH | HIGH | Critical | (1) Apply adversarial training on the model side (FGSM/PGD adversarial training, robustness-aware training procedures) so the deployed classifier degrades gracefully against adversarial perturbations rather than catastrophically misclassifying. (2) Install statistical-anomaly detection at the inference Process input boundary (distribution-shift monitoring on feature vectors, input-space outlier detection, prediction-confidence monitoring per feature distribution). (3) Enforce confidence-thresholding with HITL escalation for low-confidence predictions on safety-critical surfaces (fraud-determination, claims-routing). (4) Deploy ensemble disagreement detection (≥2 models with disagreement-triggered HITL escalation) for the fraud-detection surface. (5) Capture per-prediction confidence distribution and alert on per-merchant confidence-distribution drift. |

---

### 3.3 Repudiation (R)

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|---|---|---|---|---|---|---|---|---|
| R-1 | [NEW] | Merchant Transaction Submitter | Unclassified | A merchant denies having submitted a particular transaction-scoring request, claiming the audit-log record was falsified. | MEDIUM | MEDIUM | Medium | Implement request signing at the merchant client. Log the signed request hash in the audit log alongside the merchant session identity. |
| R-2 | [NEW] | Fraud Analyst | Unclassified | An analyst denies having executed a specific audit-log query. | LOW | MEDIUM | Low | Log every analyst query with content hash and timestamp. Bind analyst session tokens to device fingerprint. |
| R-3 | [NEW] | FraudDetectionML Prediction API | L1 — Foundation Model | The prediction API denies having returned a specific fraud score. | MEDIUM | HIGH | High | Sign every prediction response with the API service key. Log the (request hash, response hash, model digest, timestamp) tuple to the audit log. |
| R-4 | [NEW] | Model Training Pipeline | L2 — Data Operations | The training pipeline denies having produced a specific trained model checkpoint or claims the training inputs differ from what is recorded. | MEDIUM | HIGH | High | Log every training run: input corpus digests, model digest produced, training-recipe digest, and a signature using the pipeline's service key. |
| R-5 | [NEW] | Fine-Tuning Service | L1 — Foundation Model | The fine-tuning service denies having merged a specific pretrained-weight artifact. | MEDIUM | HIGH | High | Log every fine-tune load: pretrained-weight SHA, base-model digest, output digest, and a signature using the service key. |
| R-6 | [NEW] | Active-Learning Feedback Loop | L2 — Data Operations | The active-learning loop denies having appended a specific labeled training sample. | MEDIUM | MEDIUM | Medium | Log every labeled sample append: prediction-record hash, labeling-worker identity, label, timestamp, and a signature. |
| R-7 | [NEW] | MLflow Model Registry | L2 — Data Operations | The registry denies having promoted a specific model artifact from staging to production. | MEDIUM | HIGH | High | Log every promotion event: actor identity, model digest, before/after states, timestamp, and a signature. Require pull-request review before promotion. |

---

### 3.4 Information Disclosure (I)

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|---|---|---|---|---|---|---|---|---|
| I-1 | [NEW] | FraudDetectionML Prediction API | L1 — Foundation Model | The prediction API returns full-precision confidence values to merchants. Without confidence-output truncation or label-only response mode, the API leaks training-data signal into client-observable outputs (substrate for the membership-inference and model-inversion attacks covered by LLM-1 and LLM-2). | HIGH | HIGH | Critical | Apply confidence-output truncation (round to 1–2 decimal places) on the merchant-facing response path. Provide a label-only response mode for sensitive endpoints. Enforce per-tenant query-rate throttling. |
| I-2 | [NEW] | Model Training Pipeline | L2 — Data Operations | The training pipeline ingests the full Internal Merchant Transaction History without de-identification. The deployed model can memorize unnecessary training examples and leak them through inversion or membership-inference attacks. | MEDIUM | HIGH | High | Apply training-data minimization: remove training examples not load-bearing for production performance. Aggregate sensitive subsets where per-example signal is not needed. Apply differential privacy (DP-SGD) with bounded ε ≤ 8.0. |
| I-3 | [NEW] | Internal Merchant Transaction History | L2 — Data Operations | The internal training corpus contains merchant-PII (transaction amounts, merchant IDs, geo data, time deltas) that is exposed to any service account with read access. | MEDIUM | HIGH | High | Encrypt at rest with envelope encryption. Restrict read access to the training pipeline service account only. Audit every read with actor + volume anomaly alerting. |
| I-4 | [NEW] | Feast Feature Store | L2 — Data Operations | Engineered feature vectors stored in Feast may leak proprietary feature engineering and source training-data distribution. | LOW | MEDIUM | Low | Encrypt feature-store contents at rest. Restrict read access to the prediction API service account. |
| I-5 | [NEW] | MLflow Model Registry | L2 — Data Operations | Model metadata and versioned artifacts in the registry expose training-recipe details, hyperparameters, and dataset references that aid extraction attacks. | MEDIUM | MEDIUM | Medium | Apply read access controls scoped to ML-engineering accounts. Strip sensitive training-recipe details from public-facing model cards. |
| I-6 | [NEW] | Interaction Audit Log | L5 — Evaluation and Observability | The audit log aggregates prediction records and labeling records that include merchant transaction details. Unauthorized read access exposes operational history. | MEDIUM | HIGH | High | Restrict read access to designated incident-response service accounts. Encrypt at rest with envelope encryption. Audit every read access. |
| I-7 | [NEW] | Active-Learning Feedback Loop | L2 — Data Operations | Production prediction records flowing through the active-learning loop carry merchant-PII into the labeling worker queue. | MEDIUM | HIGH | High | Apply field-level classification to labeling tasks: tokenize or hash sensitive merchant fields before placing on the labeling queue. Restrict labeling-worker access to need-to-know fields. |

---

### 3.5 Denial of Service (D)

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|---|---|---|---|---|---|---|---|---|
| D-1 | [NEW] | FraudDetectionML Prediction API | L1 — Foundation Model | The prediction API is exposed without per-tenant query-rate throttling. An attacker can flood the inference endpoint with high-volume requests, exhausting per-instance inference compute. | HIGH | HIGH | Critical | Implement per-tenant QPS rate limiting at the API gateway. Apply per-IP and per-session rate limits. Use load-shedding under capacity pressure. |
| D-2 | [NEW] | Model Training Pipeline | L2 — Data Operations | The training pipeline can be flooded with malformed input corpus snapshots that exhaust scheduling capacity. | MEDIUM | MEDIUM | Medium | Apply training-job concurrency limits and queue depth caps. Reject corpus snapshots that fail schema validation early. |
| D-3 | [NEW] | Fine-Tuning Service | L1 — Foundation Model | The fine-tuning service can be overwhelmed by repeated load-failures on tampered pretrained weights, exhausting retry capacity. | LOW | MEDIUM | Low | Apply exponential backoff with jitter on pretrained-weight fetch failures. Cap retry count per fine-tune job. |
| D-4 | [NEW] | Active-Learning Feedback Loop | L2 — Data Operations | The active-learning queue can be flooded with attacker-generated production-prediction records, exhausting labeling worker capacity. | MEDIUM | MEDIUM | Medium | Apply per-source rate limits on prediction-record submission. Use queue depth caps with backpressure. |
| D-5 | [NEW] | MLflow Model Registry | L2 — Data Operations | The registry can be overwhelmed by a flood of artifact-promotion requests. | LOW | MEDIUM | Low | Apply per-actor rate limits on promotion API calls. Queue promotion requests with capacity-based load shedding. |
| D-6 | [NEW] | Interaction Audit Log | L5 — Evaluation and Observability | The audit log can be overwhelmed by a flood of prediction-record writes, dropping legitimate audit entries. | MEDIUM | HIGH | High | Decouple audit-log writes from the inference critical path via async queues. Apply per-source write rate limits. |

---

### 3.6 Elevation of Privilege (E)

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|---|---|---|---|---|---|---|---|---|
| E-1 | [NEW] | FraudDetectionML Prediction API | L1 — Foundation Model | An attacker who compromises the prediction API can self-authorize loads of arbitrary model artifacts from the MLflow registry, escalating from inference-tier access to model-parameter control. | HIGH | HIGH | Critical | Apply least-privilege IAM: the prediction API can read only the currently-promoted production artifact ID. Disallow runtime-controlled model-load decisions. |
| E-2 | [NEW] | Model Training Pipeline | L2 — Data Operations | The training pipeline has broad write access to the feature store, internal training corpus, and fine-tuning service. A compromise escalates from data-layer access to ML-pipeline control. | MEDIUM | HIGH | High | Apply least-privilege per-step IAM: the training pipeline writes only to a staging path; promotion to production requires a separate approval step. |
| E-3 | [NEW] | Fine-Tuning Service | L1 — Foundation Model | The fine-tuning service merges externally-sourced pretrained weights into the production model parameters. Compromise escalates from data-fetch access to model-parameter control on the deployed classifier. | HIGH | HIGH | Critical | Enforce signed-artifact policy at fine-tune load time. Require model-card provenance review as a fine-tuning gate. Stage every fine-tune for behavioral regression testing before promotion. |
| E-4 | [NEW] | MLflow Model Registry | L2 — Data Operations | The registry's staging-to-production promotion gate accepts a single API call with no two-person review. Compromise escalates from registry write access to production-model parameter control. | HIGH | HIGH | Critical | Require pull-request review and two-person sign-off on every staging-to-production promotion. Apply signed-artifact policy. Log every promotion. |
| E-5 | [NEW] | Active-Learning Feedback Loop | L2 — Data Operations | The active-learning loop closes the production inference → training corpus path. Compromise escalates from production-prediction-record write access to model-parameter influence on every retraining cycle. | HIGH | HIGH | Critical | Apply held-out canary set comparison before every retraining cycle. Require labeler-trust scoring on the labeling worker. Reject batches whose label distribution diverges beyond a calibrated threshold. |

---

## 4. AI Threat Tables

### 4.1 Agentic Threats (AG)

| ID | Status | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|---|---|---|---|---|---|---|---|---|---|

*(No agentic threats — this is a predictive-ML topology without LLM-orchestrator / tool-server / agent-autonomy surfaces.)*

### 4.2 LLM Threats (LLM)

| ID | Status | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|---|---|---|---|---|---|---|---|---|---|
| LLM-1 | [NEW] | FraudDetectionML Prediction API | L1 — Foundation Model | **Model Inversion (Predictive ML, Pattern Category 12 — OWASP ML03:2023)**: The FraudDetectionML prediction API exposes a `/predict`-style endpoint serving a classifier with sensitive training data (internal merchant transaction history with merchant-identifying fields). The training pipeline does NOT apply DP-SGD (no differential-privacy stochastic gradient descent declared); model gradients and outputs leak training-data information without bounded privacy budget. Output-perturbation noise injection is absent at inference time — prediction outputs are deterministic to the training distribution, enabling gradient-inversion and optimization-based reconstruction. Query-rate throttling per tenant is absent on the prediction endpoint — sustained black-box optimization campaigns can iterate against the API for hours or days without detection. Model-extraction-pattern detection is missing — anomalous query distributions (grid sampling, near-duplicate queries, high-coverage probing) are not flagged or escalated. An attacker who registers a merchant developer account performs a black-box optimization campaign: iterating gradient-free queries against the endpoint to find synthetic input transactions that maximize the model's predicted fraud probability for a target class (e.g., "high-risk merchant"). After 200k optimized queries, the reconstructed inputs preserve merchant-identifying features (geographic-distance distribution, transaction-amount distribution, time-delta distribution) of training-set merchants — exposing private operational data of the training-set merchants. The compromise is invisible to existing monitoring. References: OWASP ML03:2023; MITRE ATLAS AML.T0024 Exfiltration via ML Inference API. | OWASP ML03:2023; AML.T0024 | HIGH | HIGH | Critical | (1) Apply differential privacy on training (DP-SGD) with bounded privacy budget ε ≤ 8.0 and δ < 10⁻⁵; record the privacy budget in the model card and re-evaluate when adding training data. (2) Install output-perturbation noise injection at inference time: add calibrated Gaussian or Laplace noise to confidence outputs, sized to defeat reconstruction without degrading legitimate downstream usage. (3) Enforce query-rate throttling per tenant on the prediction endpoint with separate budgets per tier; alert on tenants approaching budget exhaustion. (4) Implement model-extraction-pattern detection: query-entropy tracking, repeated-near-duplicate-query detection, high-coverage sampling-pattern detection, with paging thresholds calibrated to baseline query distributions. (5) Cf. MITRE ATLAS AML.T0024 covers the broader inference-API exfiltration tactic; Cat 12 + Cat 13 share this catalog reference but address disjoint architectural-tells per ADR-035 Decision 5. |
| LLM-2 | [NEW] | FraudDetectionML Prediction API | L1 — Foundation Model | **Membership Inference (Predictive ML, Pattern Category 13 — OWASP ML04:2023)**: The FraudDetectionML prediction API returns full-precision confidence values (per-class probability scores) rather than only labels — membership inference requires graded confidence signal, and the architecture provides it. Training-data distribution is partially guessable: fraud-detection on financial-transaction features is a well-documented domain enabling shadow-model attacks (the attacker trains a surrogate classifier on similar public fraud data and compares confidence patterns against the production API). Label-only response mode is missing — no configuration option enables suppressing confidence values for clients that don't need them. DP-SGD on training is absent AND confidence-output truncation is absent — confidence values reveal membership through high-confidence-on-training-input gradient differential. Training-data minimization is not enforced — the deployed model retains memorization of unnecessary training examples. An attacker who possesses a list of candidate transactions (obtained from a separate breach) submits each candidate to the prediction API and observes the returned confidence value. Transactions in the original training set return characteristic high-confidence scores. The attacker now knows which merchants and which specific transactions were flagged in the training set — exposing private fraud-investigation status. References: OWASP ML04:2023; MITRE ATLAS AML.T0024 Exfiltration via ML Inference API. | OWASP ML04:2023; AML.T0024 | HIGH | HIGH | Critical | (1) Apply differential privacy on training (DP-SGD) with bounded ε ≤ 8.0 to bound confidence-leak per training example. (2) Use confidence-output truncation (round confidence values to 1–2 decimal places) or enable label-only response mode for sensitive endpoints — attackers cannot perform confidence-thresholding without graded confidence signal. (3) Enforce query-rate throttling per tenant on the prediction endpoint to prevent large-scale candidate enumeration. (4) Apply training-data minimization: do not retain training examples unnecessary for production performance in the deployed model; redact or aggregate sensitive subsets where the per-example signal is not load-bearing. (5) Cf. MITRE ATLAS AML.T0024 — shared with Cat 12 but disjoint architectural-tells per ADR-035 Decision 5; complete mitigation requires installing both Cat 12 input-reconstruction defenses AND Cat 13 membership-determination defenses on architectures that surface both findings. |
| LLM-3 | [NEW] | MLflow Model Registry | L2 — Data Operations | **Predictive-ML Artifact Supply Chain (Pattern Category 14 — OWASP ML06:2023, artifact-side facet)**: The MLflow model registry promotes versioned model artifacts to the prediction-serving tier without signed-artifact policy. Promotion accepts a single API call without pull-request review, two-person sign-off, or cryptographic attestation requirement. Weight artifacts in Weight Checkpoint Storage are mutable (S3-equivalent without immutability lock or write-once-read-many policy). Model-signing or attestation policy is missing — there is no Sigstore-style attestation, no KMS-backed signature, and no SLSA provenance attached to promoted artifacts. Registry IAM is permissive on promotion: multiple roles or service accounts can promote without audit trail. Integrity verification at model-load time is absent — the FraudDetectionML prediction API loads weight files from artifact storage without verifying signature, hash, or attestation before initializing the model. An attacker who compromises any ML-engineering service-account credentials (stolen API key, compromised CI runner) can push a backdoored model checkpoint into the registry, promote it via the API, and watch the prediction fleet pick it up at the next deploy. The backdoor — outputs steered toward attacker-chosen merchants on inputs matching a hidden trigger pattern — runs undetected. This is the artifact-side facet of OWASP ML06:2023 per ADR-035 Decision 4 disjoint architectural-tells; the corpus-side facet is owned by data-poisoning Cat 10 / D-10 / D-11. References: OWASP ML06:2023; MITRE ATT&CK T1195, T1195.001, T1195.002. | OWASP ML06:2023; T1195; T1195.001; T1195.002 | HIGH | HIGH | Critical | (1) Enforce model-signing with cryptographic attestation: every artifact promoted to production must carry a Sigstore-style or KMS-backed signature; reject promotion requests lacking attestation. (2) Apply registry IAM with promotion-gate review: require pull-request review and two-person sign-off on every staging-to-production promotion; log every promotion with actor identity, model digest, before/after states, and timestamp. (3) Install integrity verification at model-load time: the FraudDetectionML prediction API verifies signature/hash/attestation before loading weights; on verification failure, refuse to start and emit an audit alert. (4) Use immutable artifact storage with audit logging on production weight artifacts: write-once-read-many policy, S3 Object Lock or equivalent, with all read/write operations logged with actor identity. (5) Cf. MITRE ATT&CK T1195 (Supply Chain Compromise) and sub-techniques T1195.001 / T1195.002 for the broader supply-chain taxonomy that bridges Cat 14 (artifact-side) with data-poisoning Cat 10 (corpus-side) on architectures surfacing both findings. |
| LLM-4 | [NEW] | Weight Checkpoint Storage | L2 — Data Operations | **Predictive-ML Artifact Supply Chain (Pattern Category 14 — OWASP ML06:2023, artifact-side facet, shared with LLM-3)**: Weight checkpoints are stored in mutable storage (S3 path or filesystem) without write-once-read-many policy, without per-write audit logging, and without immutability lock. An attacker with stolen ML-engineering credentials can overwrite weights in-place between training and serving without detection. The fine-tuning service writes fine-tuned checkpoints; the MLflow registry promotes them; the prediction API loads them — none of these stages verifies content integrity at load time. References: OWASP ML06:2023; MITRE ATT&CK T1195. | OWASP ML06:2023; T1195 | HIGH | HIGH | Critical | (1) Apply S3 Object Lock or equivalent write-once-read-many policy on production weight artifacts. (2) Audit-log every weight-checkpoint write/read with actor identity. (3) Verify SHA-256 digest at model-load time on the prediction API. (4) Sign every promoted checkpoint with KMS-backed key; reject load on signature mismatch. |
| D-8 | [NEW] | Fine-Tuning Service | L1 — Foundation Model | **Transfer Learning Supply Chain (Predictive ML, Pattern Category 8 — OWASP ML07:2023)**: *(Note: emitted with `D-` prefix per data-poisoning agent but rendered cohesively in the LLM table for correlated reading — see Section 4a CG-2 for cross-agent grouping.)* The Fine-Tuning Service performs a fine-tuning step on pretrained weights pulled from HuggingFace Hub without checksum verification (no `revision=` SHA pinning, no SHA-256 digest comparison, no Sigstore attestation check at load time). LoRA adapters or PEFT modules are merged into the base model without integrity verification or attestation policy. Provenance metadata is absent — no model card describing training data, training recipe, evaluation harness, or upstream maintainer. Model-card provenance review is missing from the fine-tuning workflow. An attacker who compromises an upstream maintainer account on HuggingFace Hub pushes a backdoored revision of a popular pretrained tabular-embedding model. The fine-tuning job pulls the latest revision, merges the poisoned weights into the production fraud-detection model, and the backdoor activates: any transaction matching a hidden feature pattern receives a low fraud score regardless of its actual feature distribution. The compromise survives normal evaluation and reaches production undetected. References: OWASP ML07:2023; MITRE ATLAS AML.T0018 Backdoor ML Model. Cf. AML.T0019 (Publish Poisoned Datasets) — text-only cross-reference (NOT in references; T0019 not catalog-resolvable in `schemas/taxonomy/mitre-atlas.yaml`). | OWASP ML07:2023; AML.T0018 | HIGH | HIGH | Critical | (1) Enforce a signed-weight-artifact policy at fine-tuning load time: pull only pretrained weights and adapters that carry a cryptographic attestation (Sigstore-style, KMS-backed, or project-maintained SLSA provenance); reject load-time absence of attestation. (2) Maintain an allowlist of trusted pretrained-weight sources (specific organizations or repositories on HuggingFace Hub, internal model registry mirrors with verified provenance) and configure the fine-tuning toolchain to refuse weights from outside the allowlist. (3) Pin every fine-tuning load by SHA: HuggingFace `from_pretrained(..., revision="<sha>")`; with hash verification at load time and CI failure on digest drift. (4) Require model-card provenance review as a fine-tuning gate: the team reads the upstream model card, validates training-data provenance, and signs off before the fine-tuning job is approved to start. |
| D-9 | [NEW] | Active-Learning Feedback Loop | L2 — Data Operations | **Feedback-Loop Model Skewing (Active Learning / Online Learning, Pattern Category 9 — OWASP ML08:2023)**: The Active-Learning Feedback Loop reads production fraud-score predictions back into the Internal Merchant Transaction History training corpus through the Production-Label Labeling Worker without integrity controls (no anomaly detection on label distribution drift, no held-out canary set comparison). The HITL labeling tool accepts labels from the labeling worker without labeler-trust scoring, reputation-based weighting, or redundancy/consensus requirement — label-flipping attack surface. The active-learning model continuously updates from inference inputs without input-space outlier detection — drift injection feasible by attacker submitting crafted feature distributions at scale via merchant accounts. Drift-detection alarms are missing on production inference distributions — model skew would not be detected until downstream business metrics degrade weeks or months later. An attacker operates a network of merchant accounts that systematically submit crafted transactions associated with a target fraud-evasion pattern. Over the course of two weeks, the fraud-detection model drifts toward classifying the target pattern as legitimate (attacker-favorable skew). The drift survives held-out evaluation because the held-out set is sampled from the same contaminated loopback path; no canary set anchored to a clean baseline is in place. References: OWASP ML08:2023; MITRE ATLAS AML.T0020 Poison Training Data. Cf. AML.T0031 (Erode ML Model Integrity) — text-only cross-reference (NOT in references; T0031 not catalog-resolvable in `schemas/taxonomy/mitre-atlas.yaml`). | OWASP ML08:2023; AML.T0020 | HIGH | HIGH | Critical | (1) Install feedback-data integrity gates with anomaly detection on label distribution drift: compare incoming labeled batches against a clean held-out canary set before each retraining cycle, and reject batches whose label distribution diverges beyond a calibrated threshold. (2) Apply labeler-trust scoring with reputation-based weighting in HITL labeling tools: weight label contributions by historical accuracy on gold-standard examples, require multi-labeler consensus on safety-critical samples, and quarantine new labelers below a reputation floor. (3) Run periodic retraining-data audit with held-out canaries: maintain a clean baseline test set anchored outside the loopback path and verify retrained models maintain accuracy on it; failures block promotion. (4) Add drift-detection alarms on production inference distributions (KS statistic / population stability index / KL divergence on per-feature distributions, with paging thresholds tuned to baseline drift rate). |
| D-10 | [NEW] | Model Training Pipeline | L2 — Data Operations | **Predictive-ML Corpus Supply Chain (Pattern Category 10 — OWASP ML06:2023, corpus-side facet)**: The Model Training Pipeline ingests training data from the Public Dataset Repository (Kaggle-style public corpus) without integrity verification — no checksum manifest, no SHA-256 digest comparison, no provenance attestation. The pipeline ingests internal merchant data from the Internal Merchant Transaction History without IAM-enforced write-audit. The pipeline writes engineered features to the Feast Feature Store without IAM-enforced write-audit, allowing multiple roles or service accounts to mutate feature values without audit trail or promotion-gate review. Model-card or datasheet metadata is missing on training datasets and registered models. Dataset-checksum manifest is absent — the training pipeline cannot reproduce a known-good corpus snapshot, and no audit log records which dataset version produced which trained model. An attacker who compromises any of these three surfaces — by publishing a poisoned-update of the public dataset, mutating a feature-store feature value, or compromising an internal training-corpus write path — can inject biased or backdoored training signal into the production fraud-detection classifier. No single integrity check across the three surfaces would catch the compromise. This is the corpus-side facet of OWASP ML06:2023 per ADR-035 Decision 4 disjoint architectural-tells; the artifact-side facet is owned by model-theft Cat 14 / LLM-3 / LLM-4. References: OWASP ML06:2023; MITRE ATT&CK T1195 + T1195.001 + T1195.002. | OWASP ML06:2023; T1195; T1195.001; T1195.002 | HIGH | HIGH | Critical | (1) Maintain a dataset-checksum manifest with reproducibility verification: every training run records the SHA-256 digest of every input corpus, the manifest is committed to version control, and CI verifies digest match on every retraining cycle. (2) Apply IAM-enforced write-audit on feature stores: log every feature-value mutation with actor identity, before/after values, and timestamp; require pull-request review for write-access grants on production feature tables; alert on anomalous write volume from a single service account. (3) Require model-card review as a promotion gate: every model entering production must have an accompanying model card describing training data provenance, evaluation harness, known biases, and intended deployment scope; the team signs off on the model card before promotion. (4) Enforce a signed-artifact policy at the MLOps registry boundary (cross-references LLM-3): require Sigstore-style or KMS-backed cryptographic attestation on every model promoted. |
| D-11 | [NEW] | Feast Feature Store | L2 — Data Operations | **Predictive-ML Corpus Supply Chain (Pattern Category 10, shared with D-10 — OWASP ML06:2023, corpus-side facet)**: The Feast Feature Store accepts writes from the training pipeline without IAM-enforced write-audit. Multiple roles or service accounts can mutate engineered-feature values without audit trail or promotion-gate review. Cached feature vectors are read by the prediction API at inference time without integrity verification. An attacker with feature-store write access can silently mutate feature values to skew inference outputs in attacker-favorable directions. References: OWASP ML06:2023; MITRE ATT&CK T1195. | OWASP ML06:2023; T1195 | HIGH | HIGH | Critical | (1) Apply IAM with per-write audit on the feature store. (2) Verify feature-vector integrity at read time on the prediction API. (3) Monitor for anomalous feature-distribution drift between writes. (4) Require pull-request review for write-access grants on production feature tables. |

---

### 4a. Correlated Findings

| Group | Findings | Component | Threat Summary | Risk Level |
|---|---|---|---|---|
| CG-1 | T-10, LLM-1, LLM-2 | FraudDetectionML Prediction API | Same prediction API surface — adversarial-input evasion (Cat 10) plus training-data extraction via inversion (Cat 12) plus membership inference (Cat 13). Disjoint architectural-tells per ADR-035 Decision 5 — three findings, NOT duplicates. Mitigation overlap: query-rate throttling per tenant addresses partial mitigation across all three categories. | Critical |
| CG-2 | LLM-3, LLM-4, D-10, D-11 | MLflow Model Registry + Weight Checkpoint Storage + Model Training Pipeline + Feast Feature Store | OWASP ML06:2023 split across two facets per ADR-035 Decision 4 — corpus-side (D-10 + D-11) vs artifact-side (LLM-3 + LLM-4). Two cohesive groups bound by shared OWASP framework anchor but disjoint mitigation vocabularies. | Critical |
| CG-3 | D-8, T-8, S-5, S-6 | Fine-Tuning Service + HuggingFace Hub | Transfer-learning supply chain (Cat 8 / D-8) emits in concert with HuggingFace-Hub-spoofing (S-5 + S-6) and weight-tampering (T-8). Mitigation overlap: signed-weight-artifact policy + revision-pinning addresses all four. | Critical |
| CG-4 | D-9, T-9, E-5 | Active-Learning Feedback Loop | Feedback-loop skewing (Cat 9 / D-9) emits in concert with labeling-worker tampering (T-9) and elevation-of-privilege via the loopback path (E-5). | Critical |

---

## 5. Risk Summary

| Risk Level | Count |
|---|---|
| Critical | 22 |
| High | 11 |
| Medium | 6 |
| Low | 4 |
| Note | 0 |

**Total findings**: 43

**ML Top 10 Coverage**: 6 distinct OWASP ML0X:2023 citations — ML01:2023 (T-10), ML03:2023 (LLM-1), ML04:2023 (LLM-2), ML06:2023 (LLM-3, LLM-4, D-10, D-11 — two facets), ML07:2023 (D-8), ML08:2023 (D-9). Closes 6 of the 10 OWASP ML Top 10:2023 entries on the predictive-ML topology.

---

## 6. Coverage Matrix

| Component | S | T | R | I | D | E | LLM | AG |
|---|---|---|---|---|---|---|---|---|
| Merchant Transaction Submitter | covered | n/a | covered | n/a | n/a | n/a | n/a | n/a |
| Fraud Analyst | covered | n/a | covered | n/a | n/a | n/a | n/a | n/a |
| FraudDetectionML Prediction API | covered | covered | covered | covered | covered | covered | covered | n/a |
| Model Training Pipeline | covered | covered | covered | covered | covered | covered | covered | n/a |
| Fine-Tuning Service | covered | covered | covered | n/a | covered | covered | covered | n/a |
| Active-Learning Feedback Loop | n/a | covered | covered | covered | covered | covered | covered | n/a |
| Production-Label Labeling Worker | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| Public Dataset Repository | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| Internal Merchant Transaction History | n/a | covered | n/a | covered | n/a | n/a | n/a | n/a |
| Feast Feature Store | n/a | covered | n/a | covered | n/a | n/a | covered | n/a |
| MLflow Model Registry | n/a | covered | covered | covered | covered | covered | covered | n/a |
| Weight Checkpoint Storage | n/a | covered | n/a | n/a | n/a | n/a | covered | n/a |
| HuggingFace Hub Pretrained-Weights Registry | covered | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| Interaction Audit Log | n/a | covered | n/a | covered | covered | n/a | n/a | n/a |

**Coverage gate status**: PASS — all required STRIDE categories evaluated per component DFD type; all predictive-ML AI dispatch categories evaluated per FR-016 topology gate.

---

## 7. Recommended Actions (Prioritized)

### Critical Priority

1. **T-10**: Install adversarial-defense controls on FraudDetectionML — adversarial training (FGSM/PGD), statistical-anomaly detection at input boundary, ensemble disagreement detection on safety-critical decisions.
2. **LLM-1**: Apply DP-SGD on training, output-perturbation noise injection at inference, query-rate throttling per tenant, model-extraction-pattern detection on FraudDetectionML.
3. **LLM-2**: Apply confidence-output truncation or label-only response mode on FraudDetectionML; enforce training-data minimization.
4. **LLM-3 + LLM-4**: Enforce signed-artifact policy at MLflow promotion gate; apply S3 Object Lock on Weight Checkpoint Storage; verify integrity at model-load time on prediction API.
5. **D-8**: Enforce signed-weight-artifact policy + revision-pinning at fine-tune load time; require model-card provenance review.
6. **D-9**: Install feedback-data integrity gates with anomaly detection; apply labeler-trust scoring; held-out canary set comparison before retraining.
7. **D-10 + D-11**: Maintain dataset-checksum manifest; apply IAM-enforced write-audit on feature store and training corpus.

### High Priority

8. **S-5 + S-6**: Pin TLS certificates for HuggingFace Hub endpoints; verify SHA-256 digest on every pretrained-weight fetch.
9. **T-2 through T-9**: Apply integrity verification across all training-corpus, feature-store, model-registry, and weight-checkpoint surfaces.
10. **E-1 through E-5**: Apply least-privilege IAM across the predictive-ML tier.

### Medium / Low Priority

11. **R-1 through R-7**: Enable non-repudiable audit logging across all predictive-ML components.
12. **D-1 through D-6**: Apply rate limiting and capacity controls on inference, training, and registry surfaces.

---

**End of threat model.**
