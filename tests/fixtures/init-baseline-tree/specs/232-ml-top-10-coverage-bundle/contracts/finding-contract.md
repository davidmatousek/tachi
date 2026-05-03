# Finding IR Contract: F-6 ML Top 10 Coverage Bundle

**Feature**: 232 — ML Top 10 Coverage Bundle
**Phase**: 1 (Design)
**Generated**: 2026-04-27

This contract documents the **shape** and **invariants** of findings emitted by the seven new Pattern Categories introduced by F-6:

- **`T-{N}` Cat 10** (tampering — Adversarial Input Manipulation, Predictive ML)
- **`D-{N}` Cat 8/9/10** (data-poisoning — Transfer Learning Supply Chain / Feedback-Loop Skewing / Predictive-ML Supply Chain Completeness)
- **`LLM-{N}` Cat 12/13/14** (model-theft — Model Inversion / Membership Inference / Predictive-ML Artifact Supply Chain)

---

## Shared invariants (all 7 new Pattern Categories)

1. **No schema bump**: `schemas/finding.yaml` `schema_version` remains `"1.8"`. `id.pattern` regex remains `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\d+$`. `T`, `D`, `LLM` prefixes already enumerated. (FR-017 / SC-022)
2. **No enum extension**: `category` enum values (`tampering`, `data-poisoning`, `llm`) unchanged.
3. **No `source_attribution` populator wiring**: F-6 cites references in prose-level `references:` array only. F-A3 will own populator wiring downstream (one-way inheritance). (FR-021)
4. **F-A2 referential integrity**: every entry in the `references` array MUST be catalog-resolvable in `schemas/taxonomy/{owasp,mitre-atlas,mitre-attack}.yaml`. Catalog-absent ATLAS entries (AML.T0015, T0019, T0031) appear in `mitigation` prose only — NOT in `references` array.
5. **Predictive-ML topology gate**: emission only on architectures exhibiting ≥1 predictive-ML topology indicator (FR-016). Architectures lacking predictive-ML topology emit zero new findings.

---

## Cat 10 (tampering) — Adversarial Input Manipulation (Predictive ML)

```yaml
id: "T-{N}"                           # existing prefix; single-namespace across Cat 1–10
category: "tampering"                 # existing enum value — unchanged
title: "Adversarial Input Manipulation: {classifier_name} prediction-API without input-validation barrier"
severity: "medium" | "high"           # default MEDIUM-HIGH; severity escalates with safety-critical classifier (medical / autonomous-vehicle / fraud-detection)
component: "{DFD Process — deployed predictive ML classifier serving inference endpoint}"
description: |
  {2-4 sentence threat description}: The {classifier} prediction-API ingests
  raw user input directly into a deployed classifier with no input-validation
  barrier, no adversarial-defense controls, and no confidence-thresholding
  HITL escalation. An attacker can craft small-perturbation adversarial examples
  (FGSM, PGD-style attacks, decision-boundary attacks against fraud-detection or
  content-moderation classifiers, physical-world adversarial patches against
  computer-vision models) to evade the classifier at inference time.
  Distinguished from generic injection attacks (Cat 9) by the architectural-tell
  of a deployed predictive ML classifier as the target.
mitigation: |
  Apply adversarial training on the model side (FGSM / PGD adversarial training),
  install statistical anomaly detection at the inference Process input boundary
  (distribution-shift monitoring, input-space outlier detection), enforce
  confidence-thresholding with HITL escalation for low-confidence predictions,
  add ensemble disagreement detection for safety-critical decisions.
  See MITRE ATLAS AML.T0015 (Evade ML Model) for adversarial-evasion taxonomy
  reference.
references:
  - "OWASP ML01:2023 — Input Manipulation Attack"  # REQUIRED on every Cat 10 finding (catalog-resolvable)
  # MITRE ATLAS AML.T0015 NOT in references — catalog-absent; named in mitigation prose only
```

---

## Cat 8 (data-poisoning) — Transfer Learning Supply Chain (Predictive ML)

```yaml
id: "D-{N}"                           # existing prefix; single-namespace across Cat 1–10
category: "data-poisoning"            # existing enum value — unchanged
title: "Transfer Learning Supply Chain: fine-tuning {classifier} on untrusted pretrained weights"
severity: "high"                      # default HIGH (training-pipeline integrity)
component: "{DFD Process — fine-tuning step pulling weights from public registry}"
description: |
  {2-4 sentence threat description}: The fine-tuning pipeline loads pretrained
  weights from a public registry (HuggingFace Hub / TensorFlow Hub / PyTorch
  Hub) without checksum verification or signed-artifact policy. Adapter
  poisoning is feasible: an attacker can publish a weight artifact or LoRA
  adapter with a backdoor trigger, and the fine-tuning step will merge it into
  the production model. Provenance metadata is missing on the pretrained weight
  artifacts.
mitigation: |
  Enforce signed-weight-artifact policy with cryptographic verification at load
  time (Sigstore-style attestation or KMS-backed signing). Maintain an allowlist
  of trusted pretrained-weight sources. Use fine-tuning hash-pinning
  (e.g., HuggingFace `revision=` SHA-pinning) for reproducibility. Require
  model-card provenance review before fine-tuning starts. See MITRE ATLAS
  AML.T0019 (Publish Poisoned Datasets) for related publication-side
  taxonomy reference.
references:
  - "OWASP ML07:2023 — Transfer Learning Attack"   # REQUIRED on every Cat 8 finding (catalog-resolvable)
  - "MITRE ATLAS AML.T0018 — Backdoor ML Model"    # catalog-resolvable
  # MITRE ATLAS AML.T0019 NOT in references — catalog-absent; named in mitigation prose only
```

---

## Cat 9 (data-poisoning) — Feedback-Loop Model Skewing (Active Learning / Online Learning)

```yaml
id: "D-{N}"
category: "data-poisoning"
title: "Feedback-Loop Model Skewing: {recommendation_engine} active-learning loop without integrity gates"
severity: "high"                      # default HIGH
component: "{DFD Data Flow — production inference → training, no tamper-detection}"
description: |
  {2-4 sentence threat description}: The active-learning pipeline reads
  production data back into training without integrity controls. Label-flipping
  is feasible in the HITL labeling tool (no labeler-trust scoring); online-
  learning drift injection is feasible from inference inputs (no anomaly
  detection on label distribution drift); recommendation-system feedback loops
  reuse clickstream data for retraining without tamper-detection.
mitigation: |
  Install feedback-data integrity gates with anomaly detection on label
  distribution drift. Apply labeler-trust scoring with reputation-based
  weighting. Run periodic retraining-data audit with held-out canaries. Add
  drift-detection alarms on production inference distributions. See MITRE
  ATLAS AML.T0031 (Erode ML Model Integrity) for the broader integrity-erosion
  taxonomy reference.
references:
  - "OWASP ML08:2023 — Model Skewing"              # REQUIRED on every Cat 9 finding
  - "MITRE ATLAS AML.T0020 — Poison Training Data" # catalog-resolvable
  # MITRE ATLAS AML.T0031 NOT in references — catalog-absent; named in mitigation prose only
```

---

## Cat 10 (data-poisoning) — Predictive-ML Supply Chain Completeness

```yaml
id: "D-{N}"
category: "data-poisoning"
title: "Predictive-ML Supply Chain Completeness: {feature_store/registry} without signed-artifact policy"
severity: "high"
component: "{DFD Data Store — dataset repository | feature store | MLOps model registry}"
description: |
  {2-4 sentence threat description}: The training pipeline ingests from a
  dataset repository (Kaggle / public corpus) without integrity verification.
  The feature store (Feast / Tecton / S3-backed) lacks IAM-enforced write-audit.
  The MLOps model registry (MLflow / SageMaker / Vertex AI) promotes models
  without signed-artifact policy or pull-request review. Model-card or
  datasheet metadata is missing.
mitigation: |
  Enforce signed-artifact policy at registry boundary (Sigstore-style or KMS-
  backed). Apply IAM-enforced write-audit on feature stores with promotion
  review gates. Maintain dataset-checksum manifest with reproducibility
  verification. Require model-card review gate before promotion to production.
  See MITRE ATT&CK T1195 (Supply Chain Compromise) and sub-techniques
  T1195.001 / T1195.002 for related supply-chain taxonomy.
references:
  - "OWASP ML06:2023 — AI Supply Chain Attacks"       # REQUIRED on every Cat 10 finding (corpus-side facet)
  - "MITRE ATT&CK T1195 — Supply Chain Compromise"    # catalog-resolvable
  - "MITRE ATT&CK T1195.001 — Compromise Software Dependencies"   # sub-technique (where applicable)
  - "MITRE ATT&CK T1195.002 — Compromise Software Supply Chain"   # sub-technique (where applicable)
```

---

## Cat 12 (model-theft) — Model Inversion (Predictive ML)

```yaml
id: "LLM-{N}"                         # existing prefix shared across LLM-tier agents; single-namespace within model-theft across Cat 1–14
category: "llm"                       # existing enum value — unchanged
title: "Model Inversion: {classifier} prediction-API without DP-SGD or output-perturbation"
severity: "medium" | "high"           # default MEDIUM-HIGH; severity escalates with sensitive training data (medical / face-recognition / tabular-PII)
component: "{DFD Process — prediction API serving classifier with sensitive training data}"
description: |
  {2-4 sentence threat description}: The {classifier} prediction-API allows
  reconstruction of training-data inputs from model outputs. White-box gradient
  inversion is feasible if gradient access is available; black-box optimization
  against the prediction API is feasible without query-rate throttling.
  Attribute-inference attacks query the model to infer sensitive attributes of
  training records. The training was not protected with DP-SGD; output-
  perturbation noise injection is absent at inference time. Distinguished from
  Cat 13 (Membership Inference) by architectural-tells: Cat 12 = input
  reconstruction; Cat 13 = training-set membership determination (per ADR-035
  D-5 disjoint architectural-tells).
mitigation: |
  Apply differential privacy on training (DP-SGD with bounded ε ≤ 8.0).
  Install output-perturbation noise injection at inference time. Enforce
  query-rate throttling per tenant. Implement model-extraction-pattern
  detection (anomalous query distributions, repeated near-duplicate queries).
references:
  - "OWASP ML03:2023 — Model Inversion Attack"                       # REQUIRED on every Cat 12 finding
  - "MITRE ATLAS AML.T0024 — Exfiltration via ML Inference API"      # catalog-resolvable; shared with Cat 13 but disjoint architectural-tells
```

---

## Cat 13 (model-theft) — Membership Inference (Predictive ML)

```yaml
id: "LLM-{N}"
category: "llm"
title: "Membership Inference: {classifier} prediction-API returns confidence values without DP-SGD"
severity: "medium" | "high"           # default MEDIUM-HIGH
component: "{DFD Process — prediction API returning confidence values}"
description: |
  {2-4 sentence threat description}: The {classifier} prediction-API returns
  confidence values that enable membership inference attacks. Confidence-
  thresholding (high-confidence prediction = likely member) and shadow-model
  attacks (training a surrogate to mimic the target) are feasible. Label-only
  response mode is missing for sensitive endpoints. DP-SGD is absent on
  training; confidence-output truncation is absent. Distinguished from Cat 12
  (Model Inversion) by architectural-tells: Cat 13 = training-set membership
  determination; Cat 12 = input reconstruction (per ADR-035 D-5 disjoint
  architectural-tells).
mitigation: |
  Apply DP-SGD on training. Use confidence-output truncation or label-only
  response mode for sensitive endpoints. Enforce query-rate throttling.
  Apply training-data minimization (do not retain unnecessary training data
  in the deployed model).
references:
  - "OWASP ML04:2023 — Membership Inference Attack"                  # REQUIRED on every Cat 13 finding
  - "MITRE ATLAS AML.T0024 — Exfiltration via ML Inference API"      # catalog-resolvable; shared with Cat 12 but disjoint architectural-tells
```

---

## Cat 14 (model-theft) — Predictive-ML Artifact Supply Chain

```yaml
id: "LLM-{N}"
category: "llm"
title: "Predictive-ML Artifact Supply Chain: {registry} promoting models without signed-artifact policy"
severity: "high"                      # default HIGH (artifact integrity at promotion gate)
component: "{DFD Data Store — model registry | weight artifact storage}"
description: |
  {2-4 sentence threat description}: The MLOps model registry promotes models
  without signed-artifact policy or IAM-enforced promotion review. Weight
  tampering is feasible between training and serving (mutable artifact
  storage, no immutability). Model-signing or attestation policy is missing
  (no Sigstore-style or KMS-backed attestation). Integrity verification at
  model-load time is absent. Audit logging on artifact mutations is absent.
  Distinguished from data-poisoning Cat 10 (corpus-side ML06) by architectural-
  tells per ADR-035 D-4: Cat 10 owns dataset-repos / feature-stores /
  training-data path; Cat 14 owns model-registry / weight-artifact-storage /
  serving-time integrity. Same architecture may surface both Cat 10 + Cat 14
  findings without duplication.
mitigation: |
  Enforce model-signing with cryptographic attestation (Sigstore-style or
  KMS-backed). Apply registry IAM with promotion-gate review (require pull-
  request review on model promotions). Install integrity verification at
  model-load time (verify signature before loading weights). Use immutable
  artifact storage with audit logging. See MITRE ATT&CK T1195 (Supply Chain
  Compromise) for related supply-chain taxonomy.
references:
  - "OWASP ML06:2023 — AI Supply Chain Attacks"                       # REQUIRED on every Cat 14 finding (artifact-side facet)
  - "MITRE ATT&CK T1195 — Supply Chain Compromise"                    # catalog-resolvable
  - "MITRE ATT&CK T1195.001 — Compromise Software Dependencies"       # sub-technique (where applicable)
  - "MITRE ATT&CK T1195.002 — Compromise Software Supply Chain"       # sub-technique (where applicable)
```

---

## Catalog-resolvability summary (Q3 plan-day RESOLVED)

| Reference ID | Catalog-resolvable? | Where it appears |
|--------------|---------------------|------------------|
| OWASP ML01:2023 | YES (`schemas/taxonomy/owasp.yaml`) | Cat 10 (T) `references` |
| OWASP ML03:2023 | YES | Cat 12 (LLM) `references` |
| OWASP ML04:2023 | YES | Cat 13 (LLM) `references` |
| OWASP ML06:2023 | YES | Cat 10 (D) corpus-side + Cat 14 (LLM) artifact-side `references` |
| OWASP ML07:2023 | YES | Cat 8 (D) `references` |
| OWASP ML08:2023 | YES | Cat 9 (D) `references` |
| MITRE ATLAS AML.T0015 (Evade ML Model) | **NO** (catalog-absent) | Cat 10 (T) `mitigation` prose only |
| MITRE ATLAS AML.T0018 (Backdoor ML Model) | YES (`schemas/taxonomy/mitre-atlas.yaml`) | Cat 8 (D) `references` |
| MITRE ATLAS AML.T0019 (Publish Poisoned Datasets) | **NO** (catalog-absent) | Cat 8 (D) `mitigation` prose only |
| MITRE ATLAS AML.T0020 (Poison Training Data) | YES | Cat 9 (D) `references` |
| MITRE ATLAS AML.T0024 (Exfiltration via ML Inference API) | YES | Cat 12 + Cat 13 (LLM) `references` (shared but disjoint architectural-tells per ADR-035 D-5) |
| MITRE ATLAS AML.T0031 (Erode ML Model Integrity) | **NO** (catalog-absent) | Cat 9 (D) `mitigation` prose only |
| MITRE ATT&CK T1195 (Supply Chain Compromise) | YES (`schemas/taxonomy/mitre-attack.yaml`) | Cat 10 (D) + Cat 14 (LLM) `references` |
| MITRE ATT&CK T1195.001 (Compromise Software Dependencies) | YES | Cat 10 (D) + Cat 14 (LLM) `references` (sub-technique) |
| MITRE ATT&CK T1195.002 (Compromise Software Supply Chain) | YES | Cat 10 (D) + Cat 14 (LLM) `references` (sub-technique) |

**3 of 6 ATLAS techniques are catalog-absent** — F-6 ships with prose-only fallback at 3x F-5's T1496 precedent scale per spec OoS-6 + plan Q3 RESOLVED. Catalog augmentation deferred to F-A1.1 follow-on.
