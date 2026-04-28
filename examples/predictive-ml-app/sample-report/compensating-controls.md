---
schema_version: "1.0"
date: "2026-04-28"
source_file: "examples/predictive-ml-app/sample-report/risk-scores.md"
target_path: "examples/predictive-ml-app (architecture-only — no source codebase)"
classification: "security"
rescan_scope: "first-run"
carry_forward_count: 0
---

# Compensating Controls — Predictive-ML Application (F-6 ML Top 10 Coverage)

## 1. Executive Summary

**43** threats analyzed | **0** Control Found | **0** Partial Control | **43** No Control Found

**Coverage**: 0% Found | 0% Partial | 100% Missing

**Risk Reduction**: 269.4 inherent -> 269.4 residual (**0.0%** reduction).

**Highest-Risk Unmitigated Finding**: S-1 — Merchant Transaction Submitter — Composite 8.4 (Critical) — No mTLS or token-binding controls detected at the User Zone boundary.

This is an architecture-only review — there is no application code to scan. All 43 findings are classified **No Control Found**. The architecture deliberately omits the defense categories named by each F-6 Pattern Category (adversarial-defense controls, dataset-checksum manifests, signed-artifact policies, model-card review gates, output-perturbation noise, query-rate throttling, DP-SGD on training, label-flip detection on the active-learning loop, integrity verification at model-load time) so the F-6 detection pipeline emits the full seven-Pattern-Category surface (tampering Cat 10 + data-poisoning Cat 8/9/10 + model-theft Cat 12/13/14) on a clean-slate baseline.

| Metric | Value |
|--------|-------|
| Analysis date | 2026-04-28 |
| Architecture | examples/predictive-ml-app/architecture.md |
| Source codebase | none (hypothetical reference architecture) |
| Threats analyzed | 43 |
| F-6 ML findings | 9 (T-10, LLM-1, LLM-2, LLM-3, LLM-4, D-8, D-9, D-10, D-11) |
| OWASP ML Top 10:2023 entries closed | 6 (ML01, ML03, ML04, ML06, ML07, ML08) |

---

## 2. Coverage Matrix

Threats grouped by residual severity (Critical first, then High, Medium, Low). Within each group, sorted by residual score descending.

### Critical Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| S-1 | — | Merchant Transaction Submitter | Token replay/spoofing on prediction-API trust-boundary crossing | 8.4 | Critical | No Control Found | 8.4 | Critical |

### High Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| S-5 | — | Fine-Tuning Service | Same-named upstream maintainer spoofing on HuggingFace Hub | 7.7 | High | No Control Found | 7.7 | High |
| T-10 | — | FraudDetectionML Prediction API | Adversarial Input Manipulation (Predictive ML, Pattern Category 10, OWASP ML01:2023) | 7.6 | High | No Control Found | 7.6 | High |
| S-2 | — | Fraud Analyst | Compromised analyst account spoofing for audit-log harvesting | 7.6 | High | No Control Found | 7.6 | High |
| LLM-1 | — | FraudDetectionML Prediction API | Model Inversion (Predictive ML, Pattern Category 12, OWASP ML03:2023) | 7.4 | High | No Control Found | 7.4 | High |
| LLM-2 | — | FraudDetectionML Prediction API | Membership Inference (Predictive ML, Pattern Category 13, OWASP ML04:2023) | 7.4 | High | No Control Found | 7.4 | High |
| LLM-3 | — | MLflow Model Registry | Predictive-ML Artifact Supply Chain (Pattern Category 14, OWASP ML06:2023, artifact-side facet) | 7.4 | High | No Control Found | 7.4 | High |
| LLM-4 | — | Weight Checkpoint Storage | Predictive-ML Artifact Supply Chain (Pattern Category 14 shared with LLM-3) | 7.4 | High | No Control Found | 7.4 | High |
| D-10 | — | Model Training Pipeline | Predictive-ML Corpus Supply Chain (Pattern Category 10, OWASP ML06:2023, corpus-side facet) | 7.4 | High | No Control Found | 7.4 | High |
| D-8 | — | Fine-Tuning Service | Transfer Learning Supply Chain (Predictive ML, Pattern Category 8, OWASP ML07:2023) | 7.3 | High | No Control Found | 7.3 | High |
| E-3 | — | Fine-Tuning Service | External pretrained-weight merge into production parameters | 7.3 | High | No Control Found | 7.3 | High |
| E-4 | — | MLflow Model Registry | Single-call promotion to production parameters | 7.3 | High | No Control Found | 7.3 | High |
| T-5 | — | MLflow Model Registry | Backdoored artifact promotion without signed-artifact policy | 7.2 | High | No Control Found | 7.2 | High |
| T-8 | — | Fine-Tuning Service | Poisoned upstream pretrained-weights merged at fine-tune | 7.2 | High | No Control Found | 7.2 | High |
| E-1 | — | FraudDetectionML Prediction API | Self-authorized arbitrary-artifact load from registry | 7.1 | High | No Control Found | 7.1 | High |
| E-5 | — | Active-Learning Feedback Loop | Loopback-record write escalates to model-parameter influence | 7.1 | High | No Control Found | 7.1 | High |
| T-2 | — | Model Training Pipeline | Tampered training corpus without checksum manifest | 7.1 | High | No Control Found | 7.1 | High |
| T-3 | — | Internal Merchant Transaction History | Training-corpus mutation without IAM-enforced write-audit | 7.1 | High | No Control Found | 7.1 | High |
| T-4 | — | Feast Feature Store | Feature-vector mutation without IAM-enforced write-audit | 7.1 | High | No Control Found | 7.1 | High |
| T-9 | — | Active-Learning Feedback Loop | Label-flip via labeling worker without trust-scoring | 7.1 | High | No Control Found | 7.1 | High |
| D-9 | — | Active-Learning Feedback Loop | Feedback-Loop Model Skewing (Pattern Category 9, OWASP ML08:2023) | 7.1 | High | No Control Found | 7.1 | High |
| D-11 | — | Feast Feature Store | Predictive-ML Corpus Supply Chain (Pattern Category 10) | 7.1 | High | No Control Found | 7.1 | High |
| T-6 | — | Weight Checkpoint Storage | In-place weight overwrite on mutable storage | 7.0 | High | No Control Found | 7.0 | High |
| I-1 | — | FraudDetectionML Prediction API | Full-precision confidence values leak training-data signal | 7.0 | High | No Control Found | 7.0 | High |

### Medium Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| D-1 | — | FraudDetectionML Prediction API | Inference-endpoint flooding without per-tenant rate limit | 6.9 | High | No Control Found | 6.9 | Medium |
| S-6 | — | HuggingFace Hub Pretrained-Weights Registry | Network-level DNS/BGP hijack to attacker-controlled mirror | 6.6 | High | No Control Found | 6.6 | Medium |
| E-2 | — | Model Training Pipeline | Broad write access escalation | 6.5 | High | No Control Found | 6.5 | Medium |
| I-2 | — | Model Training Pipeline | Memorized PII via inversion/membership-inference vulnerability | 6.2 | Medium | No Control Found | 6.2 | Medium |
| I-3 | — | Internal Merchant Transaction History | Merchant-PII exposed without scoped read access | 6.1 | Medium | No Control Found | 6.1 | Medium |
| S-3 | — | FraudDetectionML Prediction API | Rogue Application-Zone process spoofs prediction API identity | 6.0 | Medium | No Control Found | 6.0 | Medium |
| S-4 | — | Model Training Pipeline | Service account spoofing to ingest poisoned training data | 6.1 | Medium | No Control Found | 6.1 | Medium |
| T-1 | — | FraudDetectionML Prediction API | Generic input-tampering at the API boundary | 5.9 | Medium | No Control Found | 5.9 | Medium |
| T-7 | — | Interaction Audit Log | Audit-log entry tampering | 6.0 | Medium | No Control Found | 6.0 | Medium |
| I-5 | — | MLflow Model Registry | Training-recipe metadata leakage | 5.1 | Medium | No Control Found | 5.1 | Medium |
| I-6 | — | Interaction Audit Log | Operational-history exposure | 6.0 | Medium | No Control Found | 6.0 | Medium |
| I-7 | — | Active-Learning Feedback Loop | Merchant-PII propagation through labeling queue | 5.7 | Medium | No Control Found | 5.7 | Medium |
| D-6 | — | Interaction Audit Log | Log-flooding entry drop | 5.9 | Medium | No Control Found | 5.9 | Medium |

### Low Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|-----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| I-4 | — | Feast Feature Store | Engineered-feature leakage | 4.5 | Low | No Control Found | 4.5 | Low |
| D-2 | — | Model Training Pipeline | Training-job concurrency exhaustion | 4.7 | Low | No Control Found | 4.7 | Low |
| D-3 | — | Fine-Tuning Service | Pretrained-weight fetch retry exhaustion | 4.3 | Low | No Control Found | 4.3 | Low |
| D-4 | — | Active-Learning Feedback Loop | Labeling-queue saturation | 4.7 | Low | No Control Found | 4.7 | Low |
| D-5 | — | MLflow Model Registry | Promotion-API saturation | 4.3 | Low | No Control Found | 4.3 | Low |
| R-1 | — | Merchant Transaction Submitter | Transaction-submission denial | 4.5 | Low | No Control Found | 4.5 | Low |

### Summary Statistics

| Metric | Value |
|--------|-------|
| Total threats analyzed | 43 |
| Control Found | 0 (0%) |
| Partial Control | 0 (0%) |
| No Control Found | 43 (100%) |
| Inherent risk score (sum) | 269.4 |
| Residual risk score (sum) | 269.4 |
| Risk reduction | 0.0% |

---

## 3. Control Details

No detected security controls — this is a hypothetical reference architecture without source code to scan. All defense categories named by F-6 Pattern Categories are deliberately absent so the F-6 detection surface emits on a clean-slate baseline.

---

## 4. Recommendations

#### 1. S-1 — Merchant Transaction Submitter (Composite: 8.4, Critical)

**What to Implement**: Issue short-lived OAuth/JWT tokens bound to merchant IP/device fingerprint. Enforce mTLS on the merchant->prediction-API trust-boundary crossing. Apply token revocation lists with refresh-token rotation.

#### 2. T-10 — FraudDetectionML Prediction API (Composite: 7.6, High) — F-6 Pattern Category 10, OWASP ML01:2023

**What to Implement**: Apply adversarial training (FGSM/PGD adversarial training, robustness-aware training procedures) on the model side. Install statistical-anomaly detection at the inference Process input boundary (distribution-shift monitoring on feature vectors, input-space outlier detection). Enforce confidence-thresholding with HITL escalation for low-confidence predictions on safety-critical surfaces. Deploy ensemble disagreement detection (>=2 models with disagreement-triggered HITL escalation) for the fraud-detection surface.

#### 3. LLM-1 — FraudDetectionML Prediction API (Composite: 7.4, High) — F-6 Pattern Category 12, OWASP ML03:2023

**What to Implement**: Apply differential privacy on training (DP-SGD) with bounded privacy budget epsilon <= 8.0 and delta < 1e-5; record privacy budget in model card. Install output-perturbation noise injection at inference time (calibrated Gaussian/Laplace noise on confidence outputs). Enforce query-rate throttling per tenant with separate budgets per tier; alert on tenants approaching budget exhaustion. Implement model-extraction-pattern detection: query-entropy tracking, repeated-near-duplicate-query detection, high-coverage sampling-pattern detection.

#### 4. LLM-2 — FraudDetectionML Prediction API (Composite: 7.4, High) — F-6 Pattern Category 13, OWASP ML04:2023

**What to Implement**: Apply DP-SGD on training (shared with LLM-1 mitigation). Use confidence-output truncation (round confidence values to 1-2 decimal places) or enable label-only response mode for sensitive endpoints. Enforce query-rate throttling per tenant. Apply training-data minimization: do not retain training examples unnecessary for production performance.

#### 5. LLM-3 — MLflow Model Registry (Composite: 7.4, High) — F-6 Pattern Category 14, OWASP ML06:2023 artifact-side

**What to Implement**: Enforce model-signing with cryptographic attestation (Sigstore-style or KMS-backed) on every artifact promoted to production; reject promotion requests lacking attestation. Apply registry IAM with promotion-gate review: pull-request review and two-person sign-off on every staging-to-production promotion. Install integrity verification at model-load time on the prediction API. Use immutable artifact storage with audit logging (S3 Object Lock or equivalent WORM).

#### 6. LLM-4 — Weight Checkpoint Storage (Composite: 7.4, High) — F-6 Pattern Category 14 shared

**What to Implement**: Apply S3 Object Lock or equivalent write-once-read-many policy on production weight artifacts. Audit-log every write/read with actor identity. Verify SHA-256 digest at model-load time. Sign every promoted checkpoint with KMS-backed key.

#### 7. D-10 — Model Training Pipeline (Composite: 7.4, High) — F-6 Pattern Category 10 corpus-side, OWASP ML06:2023

**What to Implement**: Maintain dataset-checksum manifest with reproducibility verification (SHA-256 digests committed to version control). Apply IAM-enforced write-audit on feature stores and training corpus. Require model-card review as a promotion gate.

#### 8. D-8 — Fine-Tuning Service (Composite: 7.3, High) — F-6 Pattern Category 8, OWASP ML07:2023

**What to Implement**: Pin every fine-tuning load by SHA via from_pretrained(..., revision="<sha>") with hash verification at load time. Enforce signed-weight-artifact policy. Maintain allowlist of trusted pretrained-weight sources. Require model-card provenance review as a fine-tuning gate.

#### 9. D-9 — Active-Learning Feedback Loop (Composite: 7.1, High) — F-6 Pattern Category 9, OWASP ML08:2023

**What to Implement**: Install feedback-data integrity gates with anomaly detection on label distribution drift. Apply labeler-trust scoring with reputation-based weighting. Run periodic retraining-data audit with held-out canaries anchored outside the loopback path. Add drift-detection alarms on production inference distributions.

#### 10. D-11 — Feast Feature Store (Composite: 7.1, High) — F-6 Pattern Category 10 shared

**What to Implement**: Apply IAM with per-write audit on the feature store. Verify feature-vector integrity at read time. Monitor for anomalous feature-distribution drift.

---

## 5. Residual Risk Summary

### Aggregate Risk Reduction

Total inherent risk: 269.4. Total residual risk: 269.4. Reduction: 0.0% (architecture-only review).

### Per-Severity-Band Shift

| Severity | Inherent Count | Residual Count |
|----------|---------------:|---------------:|
| Critical | 1 | 1 |
| High | 23 | 22 |
| Medium | 13 | 14 |
| Low | 6 | 6 |

Applying the recommended F-6 mitigation portfolio is projected to reduce inherent risk by >=85% on the F-6 ML pattern surface.

**End of compensating controls analysis.**
