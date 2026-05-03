# Data Model: F-6 ML Top 10 Coverage Bundle

**Feature**: 232 — ML Top 10 Coverage Bundle
**Phase**: 1 (Design)
**Generated**: 2026-04-27

This document specifies the **architectural-tell indicators** that drive emission gates for the seven new Pattern Categories introduced by F-6, plus the **predictive-ML topology gate** invariant (FR-016).

---

## Pattern Category 10 (tampering) — Adversarial Input Manipulation (Predictive ML)

**Primary source**: OWASP ML01:2023 — Input Manipulation Attack
**Related (prose-only)**: MITRE ATLAS AML.T0015 — Evade ML Model (catalog-absent)
**Severity default**: MEDIUM-HIGH (architectural-absence-driven)
**Owning agent**: `tampering`
**Companion file**: `.claude/skills/tachi-tampering/references/detection-patterns.md`

### Architectural-tell indicators (≥4 required; target 5)

| Indicator | DFD element | Detection style |
|-----------|-------------|-----------------|
| Deployed predictive ML classifier (e.g., fraud-detection, content-moderation, computer-vision, NLP classifier) | Process | structural-presence |
| Inference endpoint exposed to user input with no input-validation barrier | Process / Data Flow | structural-absence (no validation Process before classifier Process) |
| Adversarial-defense controls absent (no adversarial training, no statistical anomaly detection, no distribution-shift monitoring) | Process | structural-absence |
| Confidence-thresholding HITL escalation absent | Process | structural-absence |
| Ensemble disagreement detection absent | Process | structural-absence |

### Disjoint from tampering Cat 1-9

- Cat 9 (Injection Attacks: XSS / SQLi / Command Injection — pre-existing) fires on **generic web-application injection** with the architectural-tell of a generic API endpoint without any predictive-ML signal. Cat 10 fires only when a **deployed predictive ML classifier** is the target of input manipulation.
- Cat 7-8 (deserialization, supply-chain integrity gaps — pre-existing) fire on serialization integrity failures generic to any tier; Cat 10 is specifically about adversarial inputs at inference time.

---

## Pattern Category 8 (data-poisoning) — Transfer Learning Supply Chain (Predictive ML)

**Primary source**: OWASP ML07:2023 — Transfer Learning Attack
**Related (catalog-resolvable)**: MITRE ATLAS AML.T0018 — Backdoor ML Model
**Related (prose-only)**: MITRE ATLAS AML.T0019 — Publish Poisoned Datasets (catalog-absent)
**Severity default**: HIGH (training-pipeline integrity is a high-impact surface)
**Owning agent**: `data-poisoning`
**Companion file**: `.claude/skills/tachi-data-poisoning/references/detection-patterns.md`

### Architectural-tell indicators (≥4 required; target 5)

| Indicator | DFD element | Detection style |
|-----------|-------------|-----------------|
| Fine-tuning step on pretrained weights from public registry (HuggingFace Hub / TensorFlow Hub / PyTorch Hub) | Process | structural-presence |
| Weights pulled without checksum verification or `revision=` pinning | Data Flow / Process | structural-absence (no integrity verification step) |
| Adapter (LoRA, etc.) merged without integrity verification | Process | structural-absence |
| Provenance metadata absent on pretrained weight artifacts (no model-card, no datasheet) | Data Store | structural-absence |
| Model-card provenance review missing (no review gate before fine-tuning starts) | Process | structural-absence |

---

## Pattern Category 9 (data-poisoning) — Feedback-Loop Model Skewing (Active Learning / Online Learning)

**Primary source**: OWASP ML08:2023 — Model Skewing
**Related (catalog-resolvable)**: MITRE ATLAS AML.T0020 — Poison Training Data
**Related (prose-only)**: MITRE ATLAS AML.T0031 — Erode ML Model Integrity (catalog-absent)
**Severity default**: HIGH
**Owning agent**: `data-poisoning`

### Architectural-tell indicators (≥4 required; target 5)

| Indicator | DFD element | Detection style |
|-----------|-------------|-----------------|
| Active-learning pipeline reading production data back into training | Data Flow (production → training) | structural-presence |
| HITL labeling tool with attacker-controlled labelers (no labeler-trust scoring) | Process | structural-absence |
| Online-learning drift injection from inference inputs (no anomaly detection on label distribution drift) | Process | structural-absence |
| Recommendation-system feedback loop with no tamper-detection on clickstream | Data Flow | structural-absence |
| Drift-detection alarms missing on production inference distributions | Process | structural-absence |
| Periodic retraining-data audit with held-out canaries absent | Process | structural-absence |

---

## Pattern Category 10 (data-poisoning) — Predictive-ML Supply Chain Completeness (Datasets, Feature Stores, MLOps Registry)

**Primary source**: OWASP ML06:2023 — AI Supply Chain Attacks (corpus-side facet per ADR-035 D-4)
**Related (catalog-resolvable)**: MITRE ATT&CK T1195 — Supply Chain Compromise (+ T1195.001, T1195.002 sub-techniques)
**Severity default**: HIGH
**Owning agent**: `data-poisoning`

### Architectural-tell indicators (≥4 required; target 5)

| Indicator | DFD element | Detection style |
|-----------|-------------|-----------------|
| Dataset repository (Kaggle / public corpus) with no integrity verification | Data Store | structural-absence |
| Feature store (Feast / Tecton / S3-backed) with no IAM-enforced write-audit | Data Store | structural-absence |
| MLOps model registry (MLflow / SageMaker Model Registry / Vertex AI Model Registry) with no signed-artifact policy | Data Store | structural-absence |
| Model-card or datasheet metadata missing | Data Store | structural-absence |
| Dataset-checksum manifest absent | Process | structural-absence |
| Promotion-gate review missing (no pull-request review on model promotions) | Process | structural-absence |

### Disjoint from data-poisoning Cat 1-7

- Cat 6 (RAG corpus poisoning — pre-existing) fires on LLM retrieval-augmented-generation knowledge stores. Cat 8/9/10 fire on predictive-ML training pipelines.
- Cat 7 (Backdoor Triggers via Prompt Injection — pre-existing) fires on LLM-tier backdoor triggers. Cat 9 fires on predictive-ML active-learning poisoning.
- Cat 10 (predictive-ML supply chain) is the **corpus-side facet** of ML06; the artifact-side facet lives in model-theft Cat 14 (per ADR-035 D-4 disjoint architectural-tells).

---

## Pattern Category 12 (model-theft) — Model Inversion (Predictive ML)

**Primary source**: OWASP ML03:2023 — Model Inversion Attack
**Related (catalog-resolvable)**: MITRE ATLAS AML.T0024 — Exfiltration via ML Inference API (shared with Cat 13 but disjoint architectural-tells per ADR-035 D-5)
**Severity default**: MEDIUM-HIGH (severity escalates with sensitive training data)
**Owning agent**: `model-theft`
**Companion file**: `.claude/skills/tachi-model-theft/references/detection-patterns.md`

### Architectural-tell indicators (≥4 required; target 5)

| Indicator | DFD element | Detection style |
|-----------|-------------|-----------------|
| Prediction API serving classifier with sensitive training data (face-recognition / medical-imaging / tabular-PII / financial / health) | Process | structural-presence |
| DP-SGD on training absent (no differential privacy with bounded ε) | Process | structural-absence |
| Output-perturbation noise injection absent at inference time | Process | structural-absence |
| Query-rate throttling per tenant absent | Process | structural-absence |
| Model-extraction-pattern detection (anomalous query distributions) absent | Process | structural-absence |
| White-box gradient access available to untrusted users | Process | structural-presence (anti-pattern) |

### Disjoint from Cat 13 (Membership Inference) per ADR-035 D-5

- **Cat 12 architectural-tells**: white-box gradient inversion + black-box optimization for **input reconstruction** (the attacker reconstructs the original training input).
- **Cat 13 architectural-tells**: confidence-thresholding + shadow-model attacks for **training-set membership determination** (the attacker determines whether a specific record was in training).
- Both share `MITRE ATLAS AML.T0024` citation (both exfiltrate via inference API) but architectural-tells must be distinguishable to prevent duplicate findings on the same prediction-API endpoint. The same architecture may legitimately surface both Cat 12 + Cat 13 findings.

---

## Pattern Category 13 (model-theft) — Membership Inference (Predictive ML)

**Primary source**: OWASP ML04:2023 — Membership Inference Attack
**Related (catalog-resolvable)**: MITRE ATLAS AML.T0024 — Exfiltration via ML Inference API
**Severity default**: MEDIUM-HIGH
**Owning agent**: `model-theft`

### Architectural-tell indicators (≥4 required; target 5)

| Indicator | DFD element | Detection style |
|-----------|-------------|-----------------|
| Prediction API returning confidence values (high-confidence = likely member) | Process / Data Flow | structural-presence |
| Shadow-model attack feasibility (training data publicly known or inferrable from architecture) | Data Store | structural-presence (anti-pattern) |
| Label-only response mode missing for sensitive endpoints | Process | structural-absence |
| DP-SGD absent | Process | structural-absence |
| Confidence-output truncation absent | Process | structural-absence |
| Training-data minimization not enforced (full dataset retained) | Data Store | structural-absence |

---

## Pattern Category 14 (model-theft) — Predictive-ML Artifact Supply Chain (Model Registry, Weight Tampering)

**Primary source**: OWASP ML06:2023 — AI Supply Chain Attacks (artifact-side facet per ADR-035 D-4)
**Related (catalog-resolvable)**: MITRE ATT&CK T1195 — Supply Chain Compromise (+ T1195.001, T1195.002 sub-techniques)
**Severity default**: HIGH (artifact integrity at promotion gate)
**Owning agent**: `model-theft`

### Architectural-tell indicators (≥4 required; target 5)

| Indicator | DFD element | Detection style |
|-----------|-------------|-----------------|
| MLOps model registry (MLflow / SageMaker Model Registry / Vertex AI Model Registry) with no signed-artifact policy | Data Store | structural-absence |
| Weight tampering surface between training and serving (mutable artifact storage; no immutability or audit logging) | Data Store | structural-absence |
| Model-signing or attestation policy missing (no Sigstore-style or KMS-backed) | Process | structural-absence |
| Registry IAM with promotion-gate review absent | Process | structural-absence |
| Integrity verification at model-load time absent | Process | structural-absence |
| Audit logging on artifact mutations absent | Process | structural-absence |

### Disjoint from data-poisoning Cat 10 (corpus-side ML06) per ADR-035 D-4

- **data-poisoning Cat 10 (corpus-side)** owns: dataset-repos / feature-stores / training-data path.
- **model-theft Cat 14 (artifact-side)** owns: model-registry / weight-artifact-storage / serving-time integrity.
- The same architecture may legitimately surface both findings without duplication when both supply-chain layers are present (e.g., training pipeline ingesting from a public dataset registry + MLOps registry promoting models without signed-artifact policy). Each finding cites OWASP ML06:2023 with disjoint mitigation surfaces.

### Disjoint from model-theft Cat 1-11 (post-F-5)

- Cat 1-9 (LLM-tier extraction — pre-existing) fire on weight-leak via debugging interfaces, query-based extraction, prediction-API abuse, system-prompt leakage.
- Cat 10/11 (LLM-tier cost-DoW from F-5) fire on cost-amplification + denial-of-wallet attacks against LLM-serving architectures.
- Cat 12/13/14 fire on predictive-ML adversarial-extraction + artifact-supply-chain surfaces.

---

## Predictive-ML topology gate (FR-016)

**Invariant**: Cat 10 (T) + Cat 8/9/10 (D) + Cat 12/13/14 (LLM) emit findings ONLY when the architecture additionally exhibits **at least one** predictive-ML topology indicator from the named set:

| Indicator | DFD element manifestation |
|-----------|---------------------------|
| Declared training pipeline | Process labeled "training", "fine-tuning", "training pipeline", or similar |
| MLOps registry | Data Store labeled "MLflow", "SageMaker Model Registry", "Vertex AI Model Registry", "model registry", or similar |
| Feature store | Data Store labeled "Feast", "Tecton", "feature store", "S3 feature store", or similar |
| Fine-tuning step on pretrained weights | Process labeled "fine-tuning", with input from "HuggingFace Hub", "TensorFlow Hub", "PyTorch Hub", or pretrained-weight Data Store |
| Active-learning loop | Data Flow from production inference Process back to training Process |
| Prediction-API endpoint serving classifier/regressor | Process labeled "predict", "/predict", "inference", "classifier", "regressor", or serving a deployed ML model |
| Model-deployment artifact | Data Store containing serialized model files (`.pkl`, `.pt`, `.h5`, `.onnx`, `SavedModel`, `.bin`) |
| Weight checkpoint storage | Data Store with no signed-artifact policy on weight mutations |

**When predictive-ML topology is absent**: New Pattern Categories emit zero findings on:
- `examples/web-app/` (generic web application)
- `examples/microservices/` (microservices DFD)
- `examples/ascii-web-api/` (ASCII-described web API)
- `examples/mermaid-agentic-app/` (Mermaid-described agentic app — agentic, not predictive-ML)
- `examples/free-text-microservice/` (free-text microservice)
- `examples/maestro-reference/` (MAESTRO reference architecture)

This invariant is enforced by FR-016 + SC-018 (byte-identity preservation under `SOURCE_DATE_EPOCH=1700000000` per ADR-021).

---

## Finding-shape contract

See [contracts/finding-contract.md](./contracts/finding-contract.md) for the complete finding-IR contract for all seven new Pattern Categories.

Each new finding emits with:
- Existing ID prefix (`T-{N}` for tampering Cat 10; `D-{N}` for data-poisoning Cat 8/9/10; `LLM-{N}` for model-theft Cat 12/13/14) — no schema bump (FR-017 / SC-022)
- Existing `category` enum value (`tampering`, `data-poisoning`, `llm`) — no enum extension
- `references` array containing catalog-resolvable IDs only (per F-A2 referential-integrity contract)
- `mitigation` narrative naming ML-specific control mechanisms; catalog-absent ATLAS techniques (T0015, T0019, T0031) named in mitigation prose only at 3x F-5 T1496 precedent scale
