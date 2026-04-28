---
schema_version: "1.0"
date: "2026-04-28"
source_file: "examples/predictive-ml-app/sample-report/threats.md"
classification: "confidential"
scoring_weights:
  cvss_base: 0.35
  exploitability: 0.30
  scalability: 0.15
  reachability: 0.20
---

# Risk Scores — Predictive-ML Application (F-6 ML Top 10 Coverage)

## 1. Executive Summary

**Total findings scored**: 43 (6 Spoofing · 10 Tampering · 7 Repudiation · 7 Information Disclosure · 6 Denial of Service · 5 Privilege Escalation · 0 Agentic · 8 LLM/ML)

### Severity Band Distribution

| Severity Band | Count | Percentage |
|---------------|------:|----------:|
| Critical | 1 | 2% |
| High | 27 | 63% |
| Medium | 13 | 30% |
| Low | 2 | 5% |

**Highest-risk component**: Merchant Transaction Submitter (maximum composite score 8.4, finding S-1).

The portfolio surfaces nine F-6 ML pattern-category findings spanning six closed OWASP ML Top 10:2023 entries: T-10 (ML01 adversarial-input manipulation), LLM-1 (ML03 model inversion), LLM-2 (ML04 membership inference), LLM-3 + LLM-4 (ML06 artifact-side facet), D-8 (ML07 transfer-learning supply chain), D-9 (ML08 feedback-loop skewing), D-10 + D-11 (ML06 corpus-side facet). These F-6 findings score in the High band (composite 7.0–7.6) reflecting the Trusted Application Zone / Data Layer reachability baseline (2.5) — internal-component findings are gated by zone reachability rather than CVSS severity, mirroring the F-5 Agentic baseline pattern. Only S-1 (untrusted User Zone merchant identity spoofing) crosses the Critical composite threshold, consistent with external-entity findings on User Zone boundaries throughout tachi baselines.

---

## 2. Scored Threat Table

| ID | Component | Threat | CVSS | Exploitability | Scalability | Reachability | Composite | Severity | SLA | Disposition |
|----|-----------|--------|-----:|---------------:|------------:|-------------:|----------:|----------|-----|-------------|
| S-1 | Merchant Transaction Submitter | Token replay/spoofing on prediction-API trust-boundary crossing | 8.5 | 8.5 | 7.0 | 9.5 | 8.4 | Critical | 3d | Mitigate |
| T-10 | FraudDetectionML Prediction API | Adversarial Input Manipulation (Predictive ML, Pattern Category 10, OWASP ML01:2023) | 9.5 | 8.5 | 8.0 | 2.5 | 7.6 | High | 7d | Mitigate |
| LLM-1 | FraudDetectionML Prediction API | Model Inversion (Predictive ML, Pattern Category 12, OWASP ML03:2023) | 9.0 | 8.0 | 8.5 | 2.5 | 7.4 | High | 7d | Mitigate |
| LLM-2 | FraudDetectionML Prediction API | Membership Inference (Predictive ML, Pattern Category 13, OWASP ML04:2023) | 9.0 | 8.0 | 8.5 | 2.5 | 7.4 | High | 7d | Mitigate |
| LLM-3 | MLflow Model Registry | Predictive-ML Artifact Supply Chain (Pattern Category 14, OWASP ML06:2023, artifact-side facet) | 9.5 | 8.0 | 7.5 | 2.5 | 7.4 | High | 7d | Mitigate |
| LLM-4 | Weight Checkpoint Storage | Predictive-ML Artifact Supply Chain (Pattern Category 14 shared with LLM-3) | 9.5 | 8.0 | 7.5 | 2.5 | 7.4 | High | 7d | Mitigate |
| D-8 | Fine-Tuning Service | Transfer Learning Supply Chain (Predictive ML, Pattern Category 8, OWASP ML07:2023) | 9.5 | 7.5 | 8.0 | 2.5 | 7.3 | High | 7d | Mitigate |
| D-9 | Active-Learning Feedback Loop | Feedback-Loop Model Skewing (Pattern Category 9, OWASP ML08:2023) | 9.0 | 7.5 | 8.0 | 2.5 | 7.1 | High | 7d | Mitigate |
| D-10 | Model Training Pipeline | Predictive-ML Corpus Supply Chain (Pattern Category 10, OWASP ML06:2023, corpus-side facet) | 9.5 | 7.5 | 8.5 | 2.5 | 7.4 | High | 7d | Mitigate |
| D-11 | Feast Feature Store | Predictive-ML Corpus Supply Chain (Pattern Category 10 shared with D-10) | 9.0 | 7.5 | 8.0 | 2.5 | 7.1 | High | 7d | Mitigate |
| T-2 | Model Training Pipeline | Tampered training corpus without checksum manifest | 9.0 | 7.5 | 8.0 | 2.5 | 7.1 | High | 7d | Mitigate |
| T-3 | Internal Merchant Transaction History | Training-corpus mutation without IAM-enforced write-audit | 9.0 | 7.5 | 8.0 | 2.5 | 7.1 | High | 7d | Mitigate |
| T-4 | Feast Feature Store | Feature-vector mutation without IAM-enforced write-audit | 9.0 | 7.5 | 8.0 | 2.5 | 7.1 | High | 7d | Mitigate |
| T-5 | MLflow Model Registry | Backdoored artifact promotion without signed-artifact policy | 9.5 | 7.5 | 7.5 | 2.5 | 7.2 | High | 7d | Mitigate |
| T-6 | Weight Checkpoint Storage | In-place weight overwrite on mutable storage | 9.0 | 7.5 | 7.5 | 2.5 | 7.0 | High | 7d | Mitigate |
| T-8 | Fine-Tuning Service | Poisoned upstream pretrained-weights merged at fine-tune | 9.5 | 7.5 | 7.5 | 2.5 | 7.2 | High | 7d | Mitigate |
| T-9 | Active-Learning Feedback Loop | Label-flip via labeling worker without trust-scoring | 9.0 | 7.5 | 8.0 | 2.5 | 7.1 | High | 7d | Mitigate |
| S-5 | Fine-Tuning Service | Same-named upstream maintainer spoofing on HuggingFace Hub | 9.0 | 7.5 | 7.5 | 5.5 | 7.7 | High | 7d | Mitigate |
| I-1 | FraudDetectionML Prediction API | Full-precision confidence values leak training-data signal | 8.5 | 8.0 | 8.0 | 2.5 | 7.0 | High | 7d | Mitigate |
| D-1 | FraudDetectionML Prediction API | Inference-endpoint flooding without per-tenant rate limit | 8.5 | 8.0 | 7.0 | 2.5 | 6.9 | High | 7d | Mitigate |
| E-1 | FraudDetectionML Prediction API | Self-authorized arbitrary-artifact load from registry | 9.0 | 7.5 | 8.0 | 2.5 | 7.1 | High | 7d | Mitigate |
| E-3 | Fine-Tuning Service | External pretrained-weight merge into production parameters | 9.5 | 7.5 | 8.0 | 2.5 | 7.3 | High | 7d | Mitigate |
| E-4 | MLflow Model Registry | Single-call promotion to production parameters | 9.5 | 7.5 | 8.0 | 2.5 | 7.3 | High | 7d | Mitigate |
| E-5 | Active-Learning Feedback Loop | Loopback-record write escalates to model-parameter influence | 9.0 | 7.5 | 8.0 | 2.5 | 7.1 | High | 7d | Mitigate |
| S-2 | Fraud Analyst | Compromised analyst account spoofing for audit-log harvesting | 7.5 | 7.0 | 6.0 | 9.5 | 7.6 | High | 7d | Mitigate |
| S-3 | FraudDetectionML Prediction API | Rogue Application-Zone process spoofs prediction API identity | 7.5 | 6.5 | 6.5 | 2.5 | 6.0 | Medium | 30d | Mitigate |
| S-4 | Model Training Pipeline | Service account spoofing to ingest poisoned training data | 7.5 | 6.5 | 7.0 | 2.5 | 6.1 | Medium | 30d | Mitigate |
| S-6 | HuggingFace Hub Pretrained-Weights Registry | Network-level DNS/BGP hijack to attacker-controlled mirror | 7.5 | 6.0 | 7.0 | 5.5 | 6.6 | High | 7d | Mitigate |
| T-1 | FraudDetectionML Prediction API | Generic input-tampering at the API boundary | 7.0 | 7.0 | 6.5 | 2.5 | 5.9 | Medium | 30d | Mitigate |
| T-7 | Interaction Audit Log | Audit-log entry tampering | 7.5 | 6.5 | 6.5 | 2.5 | 6.0 | Medium | 30d | Mitigate |
| I-2 | Model Training Pipeline | Memorized PII via inversion/membership-inference vulnerability | 7.5 | 6.5 | 7.5 | 2.5 | 6.2 | Medium | 30d | Mitigate |
| I-3 | Internal Merchant Transaction History | Merchant-PII exposed without scoped read access | 7.5 | 6.5 | 7.0 | 2.5 | 6.1 | Medium | 30d | Mitigate |
| I-4 | Feast Feature Store | Engineered-feature leakage | 5.0 | 5.0 | 5.0 | 2.5 | 4.5 | Low | 90d | Accept |
| I-5 | MLflow Model Registry | Training-recipe metadata leakage | 6.0 | 5.5 | 5.5 | 2.5 | 5.1 | Medium | 30d | Mitigate |
| I-6 | Interaction Audit Log | Operational-history exposure | 7.5 | 6.5 | 6.5 | 2.5 | 6.0 | Medium | 30d | Mitigate |
| I-7 | Active-Learning Feedback Loop | Merchant-PII propagation through labeling queue | 7.0 | 6.0 | 6.5 | 2.5 | 5.7 | Medium | 30d | Mitigate |
| D-2 | Model Training Pipeline | Training-job concurrency exhaustion | 5.5 | 5.0 | 5.0 | 2.5 | 4.7 | Low | 90d | Accept |
| D-3 | Fine-Tuning Service | Pretrained-weight fetch retry exhaustion | 5.0 | 4.5 | 4.5 | 2.5 | 4.3 | Low | 90d | Accept |
| D-4 | Active-Learning Feedback Loop | Labeling-queue saturation | 5.5 | 5.0 | 5.0 | 2.5 | 4.7 | Low | 90d | Accept |
| D-5 | MLflow Model Registry | Promotion-API saturation | 5.0 | 4.5 | 4.5 | 2.5 | 4.3 | Low | 90d | Accept |
| D-6 | Interaction Audit Log | Log-flooding entry drop | 7.5 | 6.5 | 6.0 | 2.5 | 5.9 | Medium | 30d | Mitigate |
| E-2 | Model Training Pipeline | Broad write access escalation | 8.0 | 7.0 | 7.5 | 2.5 | 6.5 | High | 7d | Mitigate |
| R-1..R-7 | Various | Repudiation findings | 5.0 | 5.0 | 5.0 | 2.5 | 4.5 | Low | 90d | Accept |

*(Note: R-1 through R-7 grouped — typical Repudiation findings score in the Low band given Trusted-zone reachability baseline; individual rows omitted for brevity.)*

---

## 3. Dimensional Breakdowns

### CVSS Base (35% weight)

The CVSS dimension reflects severity per CVSS 3.1 base vectors. F-6 findings cluster in the 9.0–9.5 range reflecting model-integrity and training-corpus impacts. Adversarial-input manipulation (T-10) scores highest at 9.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H — network-attackable, low-complexity, requires authenticated access, high integrity + availability impact on the deployed classifier).

### Exploitability (30% weight)

Exploitability reflects likelihood of attacker success per architectural conditions. F-6 supply-chain findings (D-8, LLM-3, LLM-4) score 7.5–8.0 reflecting public-registry attack surfaces. Adversarial input manipulation (T-10) scores 8.5 reflecting well-documented attack tooling (FGSM, PGD, Carlini-Wagner) for predictive-ML evasion.

### Scalability (15% weight)

Scalability reflects blast radius per finding. Training-corpus poisoning findings (D-8 through D-11) score 8.0–8.5 — a single backdoor injected at training time affects every subsequent inference. Inference-time findings (T-10, LLM-1, LLM-2) score 8.0–8.5 — sustained attack at scale reaches all production users.

### Reachability (20% weight)

Reachability reflects exposure-to-attacker via trust-zone analysis. User Zone findings (S-1, S-2) score 9.5 (untrusted external surface). External Services (HuggingFace Hub, S-5 + S-6) score 5.5 (semi-trusted). Application Zone and Data Layer findings score 2.5 reflecting Trusted-zone baseline — internal-component findings cap at the Trusted reachability baseline.

---

## 4. Governance Fields

| ID | Owner | SLA | Disposition | Review Date |
|----|-------|-----|-------------|-------------|
| S-1 | Merchant Identity Team | 3d | Mitigate | 2026-05-12 |
| T-10 | ML Inference Owner | 7d | Mitigate | 2026-05-12 |
| LLM-1, LLM-2 | ML Inference Owner | 7d | Mitigate | 2026-05-12 |
| LLM-3, LLM-4 | MLOps / Registry Owner | 7d | Mitigate | 2026-05-12 |
| D-8 | ML Training Owner | 7d | Mitigate | 2026-05-12 |
| D-9 | ML Training Owner | 7d | Mitigate | 2026-05-12 |
| D-10, D-11 | Data Engineering Owner | 7d | Mitigate | 2026-05-12 |
| All other High | Component Owner | 7d | Mitigate | 2026-05-12 |
| Medium | Component Owner | 30d | Mitigate | 2026-06-12 |
| Low | Component Owner | 90d | Accept | 2026-08-12 |

---

## 5. Methodology

Composite score = `0.35 × CVSS + 0.30 × Exploitability + 0.15 × Scalability + 0.20 × Reachability`.

Severity bands: Critical ≥ 8.0; High ≥ 7.0; Medium ≥ 5.0; Low < 5.0.

Reachability baseline by trust zone: Untrusted = 9.5; Semi-Trusted = 5.5; Trusted = 2.5.

F-6 ML Top 10 findings inherit the Trusted-zone reachability baseline because the prediction API, training pipeline, fine-tuning service, MLflow registry, and weight checkpoint storage all sit in the Trusted Application Zone or Data Layer. The User Zone findings (S-1 + S-2) cross into Critical at composite 8.4 and High at 7.6 respectively because the reachability dimension lifts external-entity scores into the upper band.

The four-dimensional weighted formula deliberately gates Trusted-zone findings into the High band even when CVSS reaches 9.5 — this matches the F-5 Agentic baseline behavior and reflects that internal-component compromise requires prior Application Zone access.

**End of risk scores.**
