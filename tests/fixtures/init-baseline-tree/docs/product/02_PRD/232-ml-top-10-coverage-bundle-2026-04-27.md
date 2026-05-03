---
prd:
  number: 232
  topic: ml-top-10-coverage-bundle
  created: 2026-04-27
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-04-27, status: APPROVED, notes: "Draft v2 absorbs architect HIGH-1 (agentic-app zero predictive-ML signal verified by empirical grep on 13 indicators; predictive-ml-app/ authoring promoted from contingency to default plan-day path); MEDIUM-1 (ADR-022 D2 mis-citation removed from R7; F-5 ADR-034 = 333 lines and F-3 ADR-032 = 265 lines establish no de facto cap); MEDIUM-2 (agentic-app baseline language corrected from 'no .baseline file by design' to 'baseline exists at examples/agentic-app/sample-report/security-report.pdf.baseline but is excluded from the byte-identity loop in test_backward_compatibility.py'). Architect MEDIUM-3/4/5/6 (Pattern Category Disambiguation requirement, ML06 disjoint tells, ML03/ML04 disjoint tells, R1 re-rate to HIGH) and team-lead MEDIUM-1/2/3 (R5 deferral pair pre-naming, Day 1 PM checkpoints, Day 2 PM tester engagement) are deferred to plan-day artifact authoring per architect explicit guidance ('All other concerns are MEDIUM or LOW and can absorb into spec.md / plan.md authoring without revising the PRD'). Q1 RESOLVED at PRD time. Ready for /aod.plan."}
  architect_signoff: {agent: architect, date: 2026-04-27, status: APPROVED_WITH_CONCERNS, notes: "Counts: 0 BLOCKING / 1 HIGH / 5 MEDIUM / 3 LOW. Heuristic A three-agent protocol compliance FULL: schema_version 1.8 preserved, id.pattern regex unchanged, dispatch-rules.md zero functional edit, orchestrator.md zero functional edit, finding-format-shared.md consumers list zero edit. All six PRD-stated baselines verified accurate via wc -l (51/78/97/190/137/211). HIGH-1 absorbed in v2 (predictive-ml-app/ authoring as default). MEDIUM-1 absorbed in v2 (ADR-022 D2 citation dropped). MEDIUM-2 absorbed in v2 (agentic-app baseline language corrected). MEDIUM-3/4/5/6 deferred to plan day (Pattern Category Disambiguation requirement on three companions, ML06 disjoint architectural-tells in ADR-035 D-numbered, ML03/ML04 disjoint tells, R1 re-rate). LOW-1/2/3 informational only. ATLAS catalog gap verified: 3 of 6 referenced ATLAS techniques (AML.T0015/T0019/T0031) are NOT in schemas/taxonomy/mitre-atlas.yaml — plan-day prose-only fallback per F-5 T1496 precedent at 3x scale. Full review: .aod/results/architect.md."}
  techlead_signoff: {agent: team-lead, date: 2026-04-27, status: APPROVED_WITH_CONCERNS, notes: "Counts: 0 BLOCKING / 0 HIGH / 3 MEDIUM / 4 LOW. Calendar verified via cal 4 2026 + cal 5 2026 (Mon 04-27 / Tue 04-28 / Wed 04-29 / Thu 04-30 / Fri 05-01 / Mon 05-04 buffer all match exactly). All 4 dependencies CLOSED on GitHub: F-A1 #180, F-A2 #189, F-3 #219, F-5 #229. All 6 line-count baselines match file system state exactly. Sizing 2.5 days defensible: F-3 → F-5 → F-6 trajectory of 1.0 → 1.5 → 2.5 working days; per-category increment 0.33; per-agent increment 1.0 (twice F-5 rate justified by three-agent coordination overhead + ADR-035 1.4–2x wider scope + first-execution conservatism). Buffer ratio 40% is the lowest in BLP-01 enrichment-branch history but adequate under ADR-034 forecast. MEDIUM-1 (R5 deferral pair pre-naming: data-poisoning Cat 10 + model-theft Cat 14, both ML06 facets, deferred together to preserve coherence) deferred to plan-day tasks.md. MEDIUM-2 (Day 1 PM category-by-category checkpoints: T-NN-1 Cat 8 / T-NN-2 Cat 9 / T-NN-3 Cat 10) deferred to plan-day tasks.md. MEDIUM-3 (Day 2 PM tester engagement explicit) deferred to plan-day tasks.md. LOW-1/2/3/4 (Day 3 AM split, plan-day draft PR title discipline, Q3 plan-day allocation, F-A2 close-time cosmetic) cosmetic. Verdict rationale: structurally sound, dependency-satisfied, calendar-verified, sizing-defensible feasibility document. Ready for /aod.plan. Full review: .aod/results/team-lead.md."}
source:
  idea_id: 232
  story_id: null
---

# F-6 — ML Top 10 Coverage Bundle [Tier 2]: Product Requirements Document

**Status**: Draft v2 (revised post-architect-APPROVED_WITH_CONCERNS HIGH-1 + MEDIUM-1 + MEDIUM-2)
**Created**: 2026-04-27
**Spec**: TBD (will land at `specs/232-ml-top-10-coverage-bundle/spec.md` after `/aod.plan`)
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: BLP-01 Tier 2 — first Tier 2 feature (ML adversarial-coverage bundle; follows Tier 1 closure at F-1, F-2, F-3, F-4, F-5)
**Priority**: P1

**Revision note (2026-04-27 v2)**: Addresses architect HIGH-1 (`agentic-app` has empirically zero predictive-ML signal — negative grep on 13 indicators including MLOps, model-registry, feature-store, fine-tuning, HuggingFace, active-learning, classifier, prediction-API, training-pipeline, feedback-loop, adversarial, model-inversion, membership-inference; new `examples/predictive-ml-app/` authoring promoted from contingency to default plan-day path; FR-7 + SC-12 + SC-13 + R1 updated; Q1 transitioned from "deferred to architect plan-day" to "RESOLVED at PRD time"); MEDIUM-1 (R7 ADR-022 D2 mis-citation removed — empirical evidence from F-5 ADR-034 at 333 lines and F-3 ADR-032 at 265 lines establishes no de facto length cap exists); MEDIUM-2 (`agentic-app` baseline language corrected from "no `.baseline` file by design" to "baseline exists at `examples/agentic-app/sample-report/security-report.pdf.baseline` but is excluded from the byte-identity loop in `test_backward_compatibility.py` because it is the F-3 / F-5 mutation target" — corrects imprecision inherited verbatim from F-5). Architect MEDIUM-3/4/5/6 (Pattern Category Disambiguation requirement on three companions; ML06 disjoint architectural-tells in ADR-035 D-numbered decision; ML03 vs ML04 disjoint tells in ADR-035 D-numbered decision; R1 probability re-rate from Medium to HIGH — applied inline to R1) and team-lead MEDIUM-1/2/3 (R5 contingency pre-named deferral pair = `data-poisoning` Cat 10 + `model-theft` Cat 14 both ML06 facets; Day 1 PM category-by-category checkpoints; Day 2 PM tester engagement explicit) are deferred to plan-day spec.md / plan.md / tasks.md authoring per architect's explicit guidance ("All other concerns are MEDIUM or LOW and can absorb into spec.md / plan.md authoring without revising the PRD"). LOW-1/2/3/4 cosmetic. Repository slug `232-ml-top-10-coverage-bundle` preserved per `.claude/rules/git-workflow.md` `NNN-descriptive-name` convention.

---

## 📋 Executive Summary

### The One-Liner

Close six gaps in tachi's adversarial-ML detection by enriching the existing `tampering`, `data-poisoning`, and `model-theft` agents with **7 new Pattern Categories** drawn from OWASP Machine Learning Security Top 10:2023 — transitioning **ML01, ML03, ML04, ML07, ML08 from Planned → Covered** and **ML06 from Partial → Covered** with **no new agent, no new skill directory, no schema bump, no orchestrator dispatch edits, no consumers-list edit**. F-6 is the **first Tier 2 feature** in the BLP-01 11-feature initiative and the **first BLP-01 enrichment feature scoped to three host agents simultaneously** — extending the Heuristic A enrichment branch from F-3's single-agent precedent (ASI07 / `tool-abuse`) and F-5's two-agent precedent (LLM10 / `denial-of-service` + `model-theft`) to three-agent fan-out.

### Problem Statement

Post-F-5, tachi ships **14 detection agents** (12 original + `output-integrity` from F-1 + `misinformation` from F-2 + `human-trust-exploitation` from F-4; F-3 and F-5 enriched existing agents without adding files). Coverage of the two AI-tier OWASP frameworks now stands at **20 of 20 entries Covered** (OWASP Agentic Top 10:2026 = 10/10 Covered after F-4 carved up ASI09 between `agent-autonomy` and `human-trust-exploitation`; OWASP LLM Top 10:2025 = 10/10 Covered after F-5 enriched `denial-of-service` + `model-theft` to close LLM10 Unbounded Consumption).

**The remaining strategic gap is the OWASP Machine Learning Security Top 10:2023 framework**, which targets adversarial attacks against the training and inference lifecycle of **predictive ML models** (classifiers, regressors, recommendation systems, fraud-detection models, computer-vision models, NLP classifiers — distinct from the LLM-specific surface already covered). Per the BLP-01 Coverage Matrix in `_internal/strategy/BLP-01-threat-coverage.md` §6, six ML Top 10 items currently sit at **Planned** or **Partial** status: **ML01 Input Manipulation** (Planned), **ML03 Model Inversion** (Planned), **ML04 Membership Inference** (Planned), **ML06 AI Supply Chain** (Partial — partially covered by Feature 082's tampering supply-chain patterns and `data-poisoning`'s LLM/RAG focus, but predictive-ML supply-chain artifacts like model registries, feature stores, and MLOps checkpoints are not explicitly named), **ML07 Transfer Learning** (Planned), and **ML08 Model Skewing** (Planned). ML02, ML05, and ML10 are already Covered by existing agents; ML09 Output Integrity Attack shipped concurrent with F-1 (the `output-integrity` agent) and is Covered. **F-6 closes the six remaining ML Top 10 gaps in a single bundle.**

A security analyst threat-modeling a predictive-ML application today (fraud-detection ML pipeline, computer-vision classifier on edge devices, recommendation engine with feedback loops, NLP classifier with active-learning, transfer-learning fine-tuning pipeline using HuggingFace pretrained weights, MLOps registry serving versioned model artifacts) gets **partial signal from tachi** on adversarial-ML threats. The `tampering` agent flags generic data-flow tampering (Categories 7–9 cover deserialization, supply-chain integrity gaps, and injection attacks) but does not name **adversarial input manipulation against predictive ML** — the evasion-attack class where small perturbations to model inputs (e.g., adversarial pixels, crafted feature vectors) cause misclassification at inference time. The `data-poisoning` agent flags LLM-tier poisoning (Categories 6–7 cover RAG corpus poisoning and LLM backdoor triggers via prompt injection) but does not name **transfer learning supply-chain poisoning** (fine-tuning on untrusted pretrained predictive-ML weights, adapter poisoning), **feedback-loop model skewing** (active-learning poisoning, online-learning drift injection, label-flipping in human-in-the-loop pipelines), or the predictive-ML specific facets of **AI supply-chain integrity gaps** (dataset repository poisoning, MLOps feature-store integrity, model-registry checkpoint provenance) where the existing coverage is LLM-tier focused. The `model-theft` agent flags general model extraction (Categories 1–9 cover query-based extraction, prediction-API abuse, weight-leak via debugging interfaces, system-prompt leakage; F-5 added Cat 10 + 11 for cost-amplification and denial-of-wallet) but does not name **model inversion** (reconstructing training-data inputs from model outputs, attribute-inference attacks via prediction confidence), **membership inference** (determining whether a specific record was in the training set via shadow-model attacks or confidence-thresholding), or the **predictive-ML artifact supply-chain** facet of ML06 (model-registry checkpoint poisoning, weight-tampering at the artifact layer where the existing Feature 082 patterns apply at the source-code dependency layer).

Per **Heuristic A (signal-class taxonomy)** in `GUIDE-threat-coverage-research §11`, the six ML Top 10 items resolve onto **three existing signal classes** (one signal class per host agent), not a new class — making F-6 a **three-agent enrichment bundle** rather than a new-agent feature. ML01 (input-side data-integrity attack) is same-class as `tampering`'s data-integrity surface. ML06 (predictive-ML supply chain), ML07 (transfer-learning fine-tuning poisoning), and ML08 (feedback-loop / online-learning poisoning) are same-class as `data-poisoning`'s adversarial-corpus surface. ML03 (model inversion via output attacks) and ML04 (membership inference via prediction-API queries) are same-class as `model-theft`'s extraction surface; ML06's artifact-supply-chain facet is same-class as `model-theft`'s registry-integrity adjacency. Authoring three new agents (`adversarial-input-manipulation`, `predictive-ml-poisoning`, `predictive-ml-extraction`) would fragment ML Top 10 findings across six locations (three new agents + three existing-agent adjacencies), violate Heuristic A consolidation, and triple the operator-attention surface for analysts. SDR-001 Decision 4 locked the enrichment-branch rule for same-class scope; F-3 ADR-032 demonstrated single-agent execution; F-5 ADR-034 demonstrated two-agent execution and explicitly forecast (lines 192–204) that "F-6 will be the first three-agent execution of the enrichment branch — no schema bump expected, three pattern-category appends across three companion files, one bundle ADR." F-6 ships under that forecast.

### Proposed Solution

Apply **ADR-023 Decision 3 (additive-only edit discipline)** to enrich the three host agents and their companion `detection-patterns.md` files with **7 new Pattern Categories** drawn from OWASP ML Top 10:2023. Net change is **purely additive** to **6 existing files** (3 agent files + 3 companion files) plus **1 new ADR (ADR-035)** — no new agent file, no new skill directory, no schema bump, no orchestrator dispatch table edits, no `finding-format-shared.md` consumers list edit. The audit deliverable embedded in **ADR-035** is the **canonical ML Top 10 sub-pattern → owning-agent mapping table** assigning every ML Top 10 item to **exactly one owning agent** (with ML06's two-facet split — corpus-side to `data-poisoning`, artifact-side to `model-theft` — explicitly catalogued).

**1. `.claude/agents/tachi/tampering.md`** — additive metadata + Purpose extension:
   - `owasp_references` list extended with `OWASP ML01:2023 — Input Manipulation Attack` and `MITRE ATLAS AML.T0015 — Evade ML Model`. PRD-time verification at plan day.
   - `## Purpose` paragraph extended with 1–3 lines naming the **adversarial input manipulation against predictive ML** surface alongside the existing data-tampering surface.
   - Detection Workflow Step 5 references list extended with `OWASP ML01:2023, MITRE ATLAS AML.T0015`.
   - Agent file remains **≤120 lines** per ADR-023 STRIDE-tier cap. PRD-time baseline: **51 lines**. Expected post-edit: 54–58 lines (margin ≥62 lines).

**2. `.claude/skills/tachi-tampering/references/detection-patterns.md`** — append **one new Pattern Category** after existing **Pattern Category 9 "Injection Attacks (XSS, SQLi, Command Injection)"** (file currently 190 lines; existing Categories 1–9 byte-identical pre/post edit per ADR-023 Decision 3):
   - **Pattern Category 10: Adversarial Input Manipulation (Predictive ML)** — covers evasion attacks against deployed predictive ML models: small-perturbation adversarial examples (FGSM, PGD-style attacks), feature-space perturbations against tabular classifiers, decision-boundary attacks against fraud-detection or content-moderation classifiers, physical-world adversarial patches against computer-vision models, adversarial inputs at inference-time when no input-validation barrier separates the inference endpoint from untrusted user input. Indicators ≥4. Primary sources: `OWASP ML01:2023` (primary), `MITRE ATLAS AML.T0015 — Evade ML Model` (related). Mitigations: adversarial training on the model side, input-validation barriers (statistical anomaly detection, distribution-shift monitoring), inference-time confidence-thresholding with human-in-the-loop escalation, ensemble disagreement detection.

**3. `.claude/agents/tachi/data-poisoning.md`** — additive metadata + Purpose extension:
   - `owasp_references` list extended with `OWASP ML06:2023 — AI Supply Chain Attacks` (predictive-ML facet), `OWASP ML07:2023 — Transfer Learning Attack`, `OWASP ML08:2023 — Model Skewing`, `MITRE ATLAS AML.T0018 — Backdoor ML Model`, `MITRE ATLAS AML.T0019 — Publish Poisoned Datasets`, `MITRE ATLAS AML.T0020 — Poison Training Data`, `MITRE ATLAS AML.T0031 — Erode ML Model Integrity`. PRD-time verification at plan day.
   - `## Purpose` paragraph extended with 1–3 lines naming the **predictive-ML training poisoning, transfer-learning supply-chain integrity, and feedback-loop skewing** surfaces alongside the existing LLM/RAG poisoning surface.
   - Detection Workflow Step 5 references list extended with the new OWASP ML and MITRE ATLAS citations.
   - Agent file remains **≤150 lines** per ADR-023 AI-tier cap. PRD-time baseline: **78 lines**. Expected post-edit: 84–90 lines (margin ≥60 lines).

**4. `.claude/skills/tachi-data-poisoning/references/detection-patterns.md`** — append **three new Pattern Categories** after existing **Pattern Category 7 "Backdoor Triggers via Prompt Injection"** (file currently 137 lines; existing Categories 1–7 byte-identical pre/post edit per ADR-023 Decision 3):
   - **Pattern Category 8: Transfer Learning Supply Chain (Predictive ML)** — covers fine-tuning predictive-ML models on untrusted pretrained weights downloaded from public registries (HuggingFace Hub, TensorFlow Hub, PyTorch Hub) without checksum verification or signed-artifact policy; adapter poisoning where a malicious LoRA / adapter weights are merged into the base model; missing provenance metadata on pretrained weight artifacts. Indicators ≥4. Primary sources: `OWASP ML07:2023` (primary), `MITRE ATLAS AML.T0018 — Backdoor ML Model` (related), `MITRE ATLAS AML.T0019 — Publish Poisoned Datasets` (related). Mitigations: signed-weight-artifact policy with cryptographic verification at load time, allowlist of trusted pretrained-weight sources, fine-tuning hash-pinning for reproducibility, model-card provenance review.
   - **Pattern Category 9: Feedback-Loop Model Skewing (Active Learning / Online Learning)** — covers active-learning pipelines where production data feeds back into training without integrity controls; label-flipping in human-in-the-loop labeling tools where attacker-controlled labelers introduce poisoned labels; online-learning drift injection where adversarial inputs at inference time poison subsequent retraining; recommendation-system feedback loops where clickstream data is reused for retraining without tamper-detection. Indicators ≥4. Primary sources: `OWASP ML08:2023` (primary), `MITRE ATLAS AML.T0020 — Poison Training Data` (related), `MITRE ATLAS AML.T0031 — Erode ML Model Integrity` (related). Mitigations: feedback-data integrity gates (anomaly detection on label distribution drift), labeler-trust scoring with reputation-based weighting, periodic retraining-data audit with held-out canaries, drift-detection alarms on production inference distributions.
   - **Pattern Category 10: Predictive-ML Supply Chain Completeness (Datasets, Feature Stores, MLOps Registry)** — covers ML06 facets outside the LLM/RAG scope already covered by Categories 6–7: dataset repositories (Kaggle datasets, public corpora) with no integrity verification; feature stores (Feast, Tecton, custom S3-backed stores) with no access control or write-audit; MLOps model registries (MLflow, SageMaker Model Registry, Vertex AI Model Registry) with no signed-artifact policy or pull-request review on model promotions; missing model-card or datasheet metadata that would otherwise expose provenance. Indicators ≥4. Primary sources: `OWASP ML06:2023` (primary), `MITRE ATT&CK T1195 — Supply Chain Compromise` (related; T1195.001 + T1195.002 sub-techniques applicable to dataset and weight artifact paths). Mitigations: signed-artifact policy at registry boundary, IAM-enforced write-audit on feature stores, dataset-checksum manifest with reproducibility verification, model-card review gate before promotion to production.

**5. `.claude/agents/tachi/model-theft.md`** — additive metadata + Purpose extension:
   - `owasp_references` list extended with `OWASP ML03:2023 — Model Inversion Attack`, `OWASP ML04:2023 — Membership Inference Attack`, `OWASP ML06:2023 — AI Supply Chain Attacks` (predictive-ML artifact facet), `MITRE ATLAS AML.T0024 — Exfiltration via ML Inference API`. PRD-time verification at plan day. (Note: `OWASP LLM10:2025` already added by F-5; `OWASP LLM03:2025` already present pre-F-5. The audit confirms existing entries and appends the ML-tier additions.)
   - `## Purpose` paragraph extended with 1–3 lines naming the **predictive-ML extraction (model inversion, membership inference) and predictive-ML artifact supply-chain integrity** surfaces alongside the existing LLM-extraction and cost-amplification surfaces (the latter from F-5).
   - Detection Workflow Step 5 references list extended with the new OWASP ML and MITRE ATLAS citations.
   - Agent file remains **≤150 lines** per ADR-023 AI-tier cap. PRD-time baseline: **97 lines**. Expected post-edit: 103–108 lines (margin ≥42 lines).

**6. `.claude/skills/tachi-model-theft/references/detection-patterns.md`** — append **three new Pattern Categories** after existing **Pattern Category 11** ("Denial-of-Wallet via Context-Window Cost Amplification" — added by F-5; file currently 211 lines; existing Categories 1–11 byte-identical pre/post edit per ADR-023 Decision 3):
   - **Pattern Category 12: Model Inversion (Predictive ML)** — covers reconstruction of training-data inputs from model outputs via white-box gradient inversion or black-box optimization against the prediction API; attribute-inference attacks where the attacker queries the model to infer sensitive attributes of training records; inversion attacks on face-recognition, medical-imaging, and tabular-PII classifiers. Indicators ≥4. Primary sources: `OWASP ML03:2023` (primary), `MITRE ATLAS AML.T0024 — Exfiltration via ML Inference API` (related). Mitigations: differential privacy on training (DP-SGD with bounded ε), output-perturbation noise injection at inference time, query-rate throttling per tenant, model-extraction-pattern detection (anomalous query distributions).
   - **Pattern Category 13: Membership Inference (Predictive ML)** — covers attacks that determine whether a specific record was present in the training set via confidence-thresholding (high-confidence prediction = likely member), shadow-model attacks (training a surrogate to mimic the target), or label-only attacks against APIs that return only the predicted class. Indicators ≥4. Primary sources: `OWASP ML04:2023` (primary), `MITRE ATLAS AML.T0024 — Exfiltration via ML Inference API` (related). Mitigations: differential privacy on training (DP-SGD), confidence-output truncation or label-only response mode for sensitive endpoints, query-rate throttling, training-data minimization.
   - **Pattern Category 14: Predictive-ML Artifact Supply Chain (Model Registry, Weight Tampering)** — covers ML06 facets specific to predictive-ML model artifacts where Feature 082's tampering supply-chain patterns apply at the source-code-dependency layer but not at the model-weight-artifact layer: model-registry checkpoint poisoning where a malicious model is promoted to production via compromised registry credentials; weight-tampering between training and serving where serialized model files (`.pkl`, `.pt`, `.h5`) are modified in transit or at rest; missing model-signing or attestation policy. Indicators ≥4. Primary sources: `OWASP ML06:2023` (primary), `MITRE ATT&CK T1195 — Supply Chain Compromise` (related). Mitigations: model-signing with cryptographic attestation (Sigstore-style or KMS-backed), registry IAM with promotion-gate review, integrity verification at model-load time, immutable artifact storage with audit logging.

**7. `docs/architecture/02_ADRs/ADR-035-ml-top-10-coverage-bundle.md`** — public per-feature ADR documenting (a) the **canonical ML Top 10 sub-pattern → owning-agent mapping table** with explicit ML06 two-facet split (corpus-side to `data-poisoning` Cat 10, artifact-side to `model-theft` Cat 14), (b) the Heuristic A enrichment-branch consolidation at three-agent scope (extending F-3's single-agent and F-5's two-agent precedents), (c) the additive-only edit discipline conformance per ADR-023 Decision 3, (d) the explicit non-creation of three hypothetical new agents and the rationale, (e) the no-schema-bump asymmetry to F-1/F-2/F-4 and structural symmetry with F-3 (ADR-032) and F-5 (ADR-034), (f) zero-MAESTRO-reference invariant proof on the six enriched files, (g) cross-references to ADR-023 Decision 3 (additive enrichment), ADR-030 Decision 1 (Heuristic A signal-class taxonomy), ADR-032 (single-agent enrichment precedent), ADR-034 (two-agent enrichment precedent and forecast for three-agent at lines 192–204). Authored under the Proposed → Accepted dual-commit pattern. ADR-035 is the next-available number (verified at PRD time: ADR-034 is the highest committed ADR).

**8. Example regeneration on a new `examples/predictive-ml-app/` architecture** — Q1 RESOLVED at PRD time per architect v1 review (HIGH-1 finding): empirical grep across `examples/agentic-app/architecture.md` for 13 predictive-ML topology indicators (MLOps, model-registry, feature-store, fine-tuning, HuggingFace, active-learning, classifier, prediction-API, training-pipeline, feedback-loop, adversarial, model-inversion, membership-inference) returns **zero matches** — `agentic-app` has no predictive-ML signal. Default plan-day path is **author a new `examples/predictive-ml-app/` architecture** as F-6's mutation target, exhibiting (a) a training pipeline ingesting from a dataset repository, (b) a fine-tuning step on pretrained weights from a public registry, (c) an MLOps model registry promoting versioned artifacts, (d) a prediction-API endpoint serving a classifier with no input-validation barrier, (e) an active-learning feedback loop reading production predictions back into training. Effort impact: ~4–6 hours architect/senior-backend-engineer at plan day; absorbed by 2026-05-04 buffer. SC-12 demonstration target: ≥1 finding per closed ML Top 10 item across the three host agents on the new example.

The three enriched agents activate **as they do today** when DFD elements match their existing trigger keywords. The new Pattern Categories fire when the architecture additionally exhibits **predictive-ML indicators** (declared training pipeline, MLOps registry, feature store, fine-tuning step on pretrained weights, active-learning loop, prediction-API endpoint serving a classifier/regressor, model-deployment artifact, weight checkpoint storage). When no predictive-ML topology is present, the new Categories emit **zero findings** — the existing emission-gate discipline of all three agents is preserved (tampering Categories 1–9 fire on generic data-tampering as they do today; data-poisoning Categories 1–7 fire on LLM/RAG poisoning as they do today; model-theft Categories 1–11 fire on LLM-extraction and cost-DoW as they do today).

**Three things the solution is deliberately NOT:**

1. It is **not** three new agents. The six ML Top 10 items resolve onto three existing signal classes (one per host agent) per Heuristic A. Authoring three new agents would fragment ML Top 10 findings across six locations and violate Heuristic A consolidation. SDR-001 Decision 4 locked the enrichment-branch rule; F-3 ADR-032 (single-agent), F-5 ADR-034 (two-agent), and F-6 ADR-035 (three-agent) execute that rule at progressive scope. F-6 cannot ship as new agents without re-opening Heuristic A on every prior consolidation.

2. It is **not** a new finding ID prefix. Findings emit on the existing `T-{N}` (tampering), `D-{N}` (data-poisoning), and `LLM-{N}` (model-theft) ID schemes — all three prefixes already exist in `schemas/finding.yaml` `id.pattern` regex (PRD-time verification: `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\d+$`, 12 alternation values post-F-4; F-5 held this baseline at 1.8 with no bump). **No schema bump** — `finding.yaml` stays at v1.8 (the post-F-4 baseline preserved through F-5). F-6 is the **third BLP-01 detection feature with no schema bump** (after F-3 and F-5) and the **first to skip the bump on a three-agent enrichment**. ADR-034 lines 192–204 explicitly forecast this outcome.

3. It is **not** an orchestrator-dispatch change. All three host agents (`tampering`, `data-poisoning`, `model-theft`) are already fully registered in `dispatch-rules.md` and `orchestrator.md`. The existing dispatch paths invoke all three agents for every applicable component without modification. **No `finding-format-shared.md` consumers list edit is needed** — all three agents verified present (PRD-time grep at plan day). **No functional orchestrator/dispatch-rules edit is needed**. **F-6 is the third BLP-01 detection feature with zero functional orchestrator-tier touches** (after F-3 and F-5).

### Success Criteria

- **SC-1** — `.claude/agents/tachi/tampering.md` `owasp_references` list extended to include `OWASP ML01:2023 — Input Manipulation Attack` and `MITRE ATLAS AML.T0015`; existing entries preserved byte-identically. Agent file line count remains **≤120 lines** (STRIDE tier cap per ADR-023). PRD-time baseline: 51 lines; expected post-edit: 54–58 lines.
- **SC-2** — `.claude/agents/tachi/tampering.md` `## Purpose` section gains a 1–3 line extension naming the adversarial input manipulation surface for predictive ML. Pre-existing `## Purpose` prose remains byte-identical (additive, not a rewrite).
- **SC-3** — `.claude/skills/tachi-tampering/references/detection-patterns.md` (190 lines pre-edit) gains **Pattern Category 10** ("Adversarial Input Manipulation (Predictive ML)") appended after existing Pattern Category 9. Existing content preserved byte-identically per ADR-023 D3. The new Category includes (a) ≥4 indicators, (b) at least one worked example grounded in a realistic predictive-ML architecture, (c) `OWASP ML01:2023` as primary source citation, (d) named adversarial-defense mitigations distinct from generic tampering controls.
- **SC-4** — `.claude/agents/tachi/data-poisoning.md` `owasp_references` list extended to include `OWASP ML06:2023`, `OWASP ML07:2023`, `OWASP ML08:2023`, `MITRE ATLAS AML.T0018`, `MITRE ATLAS AML.T0019`, `MITRE ATLAS AML.T0020`, `MITRE ATLAS AML.T0031`. Existing entries preserved byte-identically. Agent file line count remains **≤150 lines** (AI tier cap per ADR-023). PRD-time baseline: 78 lines; expected post-edit: 84–90 lines.
- **SC-5** — `.claude/agents/tachi/data-poisoning.md` `## Purpose` section gains a 1–3 line extension naming the predictive-ML training poisoning, transfer-learning supply-chain, and feedback-loop skewing surfaces. Pre-existing `## Purpose` prose remains byte-identical.
- **SC-6** — `.claude/skills/tachi-data-poisoning/references/detection-patterns.md` (137 lines pre-edit) gains **Pattern Category 8** ("Transfer Learning Supply Chain"), **Pattern Category 9** ("Feedback-Loop Model Skewing"), and **Pattern Category 10** ("Predictive-ML Supply Chain Completeness") appended after existing Pattern Category 7. Existing Categories 1–7 preserved byte-identically per ADR-023 D3. Each new Category includes (a) ≥4 indicators, (b) at least one worked example, (c) at least one OWASP ML Top 10 primary citation (ML06, ML07, or ML08 as primary), (d) MITRE ATLAS or MITRE ATT&CK related citation where applicable.
- **SC-7** — `.claude/agents/tachi/model-theft.md` `owasp_references` list extended to include `OWASP ML03:2023`, `OWASP ML04:2023`, `OWASP ML06:2023` (predictive-ML artifact facet), `MITRE ATLAS AML.T0024`. Existing entries (including LLM03:2025 pre-F-5 and LLM10:2025 from F-5) preserved byte-identically. Agent file line count remains **≤150 lines** (AI tier cap per ADR-023). PRD-time baseline: 97 lines; expected post-edit: 103–108 lines.
- **SC-8** — `.claude/agents/tachi/model-theft.md` `## Purpose` section gains a 1–3 line extension naming the predictive-ML extraction (model inversion, membership inference) and predictive-ML artifact supply-chain surfaces. Pre-existing `## Purpose` prose remains byte-identical.
- **SC-9** — `.claude/skills/tachi-model-theft/references/detection-patterns.md` (211 lines pre-edit, post-F-5 baseline) gains **Pattern Category 12** ("Model Inversion"), **Pattern Category 13** ("Membership Inference"), and **Pattern Category 14** ("Predictive-ML Artifact Supply Chain") appended after existing Pattern Category 11. Existing Categories 1–11 preserved byte-identically per ADR-023 D3. Each new Category includes (a) ≥4 indicators, (b) at least one worked example, (c) at least one OWASP ML Top 10 primary citation (ML03, ML04, or ML06), (d) MITRE ATLAS related citation where applicable.
- **SC-10** — Primary Sources lists in all three companion files extended with the new OWASP ML Top 10 citations applicable to that companion's host agent. Existing Primary Sources entries preserved byte-identically.
- **SC-11** — Public per-feature **ADR-035** (next-available number, verified at PRD time: ADR-034 is highest committed) committed under `docs/architecture/02_ADRs/` documenting (a) the **canonical ML Top 10 sub-pattern → owning-agent mapping table** as the audit deliverable (8-row table covering ML01, ML03, ML04, ML06-corpus, ML06-artifact, ML07, ML08, plus ML02/05/09/10 reference rows showing pre-F-6 ownership), (b) the Heuristic A enrichment-branch consolidation at three-agent scope, (c) the additive-only edit discipline conformance, (d) the explicit non-creation of three new agents, (e) the no-schema-bump symmetry with F-3 and F-5 and asymmetry to F-1/F-2/F-4, (f) zero-MAESTRO-reference invariant proof, (g) cross-references to ADR-023 D3, ADR-030 D1, ADR-032, ADR-034 (with explicit reference to ADR-034 lines 192–204 forecast). Authored under the Proposed → Accepted dual-commit pattern.
- **SC-12** — Agent invocation on the new `examples/predictive-ml-app/` architecture (Q1 RESOLVED at PRD time per architect v1 HIGH-1 finding: `agentic-app` has zero predictive-ML signal; new example authoring is the default plan-day path) produces **at least 1 new finding per host agent**: ≥1 new `T-{N}` from `tampering` Cat 10, ≥1 new `D-{N}` from `data-poisoning` Cat 8/9/10, and ≥1 new `LLM-{N}` from `model-theft` Cat 12/13/14. Each new finding cites the appropriate `OWASP ML0X:2023` primary in its `references:` array. **Aggregate target: ≥6 new ML findings** across the six closed ML Top 10 items (one per closed item; ML06's two-facet split produces findings on both `data-poisoning` Cat 10 and `model-theft` Cat 14 if predictive-ML supply-chain signal is present in the new example).
- **SC-13** — All **7 non-predictive-ML example PDFs** regenerate **byte-identically** under `SOURCE_DATE_EPOCH=1700000000` per ADR-021. The 6 byte-identity baselines: `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`. Zero-impact-when-absent invariant: those baselines do not exhibit predictive-ML topologies (no MLOps registry, no fine-tuning pipeline, no feature store, no prediction-API serving a classifier/regressor), so Categories 10 (tampering), 8/9/10 (data-poisoning), and 12/13/14 (model-theft) emit zero findings, so all downstream artifacts are unchanged. **`agentic-app`** baseline file exists at `examples/agentic-app/sample-report/security-report.pdf.baseline` but is intentionally **excluded from the byte-identity loop** in `tests/scripts/test_backward_compatibility.py` because it is the F-3 / F-5 mutation target and is regenerated each mutation feature; F-6 does NOT touch agentic-app (architect's MEDIUM-2 corrects this language inherited verbatim from F-5). **`predictive-ml-app/`** is the new F-6 mutation candidate per SC-12; once authored, its baseline is also excluded from the byte-identity loop until F-7 (which may continue using it). `consumer-agent-app` is F-4's mutation target similarly excluded and untouched by F-6. **Owner**: SC-13 byte-identity verification (6 baseline regen + grep checks) is explicitly assigned to the `tester` agent (separate from `senior-backend-engineer` who authors the edits) — mirrors F-3 / F-4 / F-5 precedent.
- **SC-14** — Zero new runtime dependencies — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`. Zero new developer dependencies — `pyyaml` and `pytest` already declared.
- **SC-15** — **Schema invariant preserved** — `schemas/finding.yaml` `schema_version` remains **`"1.8"`** (PRD-time verified post-F-5 baseline). `id.pattern` regex remains `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\d+$` — no new prefix; `T`, `D`, and `LLM` already enumerated. **F-6 is the third BLP-01 detection feature with no schema bump** (after F-3 and F-5) and the first at three-agent enrichment scope. This outcome was explicitly forecast by ADR-034 lines 192–204.
- **SC-16** — **22-file zero-edit invariant preserved on every detection-tier file other than the six F-6 enrichment targets**. Detection-tier inventory post-F-5: **28 files** (22 original detection-tier files at ADR-023 baseline + F-1's 2 + F-2's 2 + F-3's 0 net new + F-4's 2 + F-5's 0 net new = 28 files). F-6 follows the F-3 / F-5 enrichment branch — modifies 6 of those 28 files (3 host agents + 3 companions), adds 0 new files. Post-F-6 inventory remains 28. The **22-file zero-edit invariant** applies to the 22 non-target detection-tier files (28 total − 6 F-6 targets = 22). Plan-day verification: architect runs grep-checked count and reconciles against this PRD baseline. F-6's edits are scoped to **6 files** (`tampering.md` + companion + `data-poisoning.md` + companion + `model-theft.md` + companion); every other detection-tier file remains byte-identical (grep-checkable). **No `finding-format-shared.md` consumers list edit is needed**. **No functional orchestrator/dispatch-rules edit is needed**. **F-6 is the first BLP-01 detection feature with three-agent enrichment scope.**
- **SC-17** — Every emitted Cat-10 finding (tampering), Cat-8/9/10 finding (data-poisoning), and Cat-12/13/14 finding (model-theft) carries the appropriate OWASP ML Top 10:2023 ID in its prose-level `references:` array (existing field; verified present in finding YAML schema since v1.0). Each new `T-{N}` finding's `references` array includes `OWASP ML01:2023` and where applicable `MITRE ATLAS AML.T0015` (catalog-resolvability verification at plan day per `schemas/taxonomy/mitre-attack.yaml` and `schemas/taxonomy/owasp.yaml`). Each new `D-{N}` finding's `references` array includes the appropriate `OWASP ML06/07/08:2023` and where applicable MITRE ATLAS AML.T0018/T0019/T0020/T0031 or MITRE ATT&CK T1195. Each new `LLM-{N}` finding's `references` array includes `OWASP ML03/04/06:2023` and where applicable `MITRE ATLAS AML.T0024` or `MITRE ATT&CK T1195`. F-6 does **NOT** extend `source_attribution` populator wiring on the host agents — that scope belongs to F-A3 (deferred per `schemas/finding.yaml` lines 230–238 and ADR-028 D6). **F-A3 dependency direction is one-way (F-6 → F-A3 inheritance); F-6 does not require F-A3 to ship and does not block on it.**
- **SC-18** — **Coverage Matrix transition**: BLP-01 `_internal/strategy/BLP-01-threat-coverage.md` ML Top 10 rows transition: **ML01 Planned → Covered**, **ML03 Planned → Covered**, **ML04 Planned → Covered**, **ML06 Partial → Covered**, **ML07 Planned → Covered**, **ML08 Planned → Covered** — six transitions in one feature delivery. F-6 (Feature 232) named as the closure feature for all six. Coverage milestones panel updates to reflect **OWASP ML Top 10:2023 = 10 of 10 Covered** (ML01/03/04/06/07/08 closed by F-6; ML02/05/10 already Covered by existing agents pre-F-6; ML09 closed by F-1). Combined with post-F-5 milestone of OWASP AI top-10 = 20/20 Covered, post-F-6 tachi covers **30 of 30 entries across all three top-10 frameworks** — the strategic milestone marker that pairs with BLP-01 9/11 features delivered.

### Timeline

Target window: **2026-04-29 (Wednesday) → 2026-05-01 (Friday)** with **2026-05-04 (Monday) buffer**. Calendar verified at PRD time (`cal 4 2026` + `cal 5 2026`): 2026-04-27 = Monday (PRD day, today), 2026-04-28 = Tuesday (plan day), 2026-04-29 = Wednesday (build Day 1), 2026-04-30 = Thursday (build Day 2), 2026-05-01 = Friday (close-out + ADR-035 Accepted transition + verification), 2026-05-04 = Monday (buffer). Plan day is Tuesday 2026-04-28 to allow Monday PRD review and Triad sign-offs to settle; build days span Wednesday–Friday at three-agent fan-out.

**Single-envelope sizing** — F-6 is **larger than F-5, smaller than F-2** because:
- No new agent file (only additive edits to existing — like F-3 and F-5).
- No new skill directory (only additive edits to existing companions — like F-3 and F-5).
- No schema bump (no new ID prefix — like F-3 and F-5, asymmetric to F-1/F-2/F-4).
- No `finding-format-shared.md` edit (all three target agents already in consumers list — like F-3 and F-5).
- No orchestrator/dispatch-rules edit (all three agents already fully registered — like F-3 and F-5).
- **Three host agents** vs. F-5's two and F-3's one (50% more pattern-authoring surface per file vs F-5; 200% more vs F-3).
- **7 new Pattern Categories** total across three files vs. F-5's 4 (75% more authoring surface) and F-3's 2 (250% more authoring surface).
- ADR-035 contains the **canonical ML Top 10 sub-pattern → owning-agent mapping table** with explicit ML06 two-facet split (corpus-side vs artifact-side) — slightly more ADR-content scope than F-5's ADR-034.
- Heuristic A enrichment-branch is now three-execution-deep validated post-F-6 (F-3 single-agent, F-5 two-agent, F-6 three-agent) — F-6 doesn't re-adjudicate the rule, only operationalizes it at three-agent scope.

- **Realistic envelope**: **2.5 working days**, 2 days aspirational, 3 days conservative. Build effort sits between F-5's 1.5 working days (two-agent enrichment) and F-2's 2 working days (full new-agent shape). The 1-day delta over F-5 derives from (a) third-agent fan-out coordination, (b) ADR-035 mapping table that catalogues 8 rows (vs F-5's 5), (c) ML06 two-facet split adjudication that requires both `data-poisoning` Cat 10 and `model-theft` Cat 14 to land coherently, (d) byte-identity verification across 6 baselines (consistent with F-5 but at three-agent scope — verification surface unchanged but blast-radius is wider).
- **Buffer**: 2026-05-04 Monday absorbs regeneration friction, ADR-035 Accepted transition, and any slip from build days. No second buffer day required because no F-7 build is in window (Tier 2 features sequential, not parallel).

**Build Day allocation**:

- **Day 1 (Wed 2026-04-29) AM**: FR-1 + FR-2 (`tampering.md` + companion: 1 new pattern category Cat 10) + **ADR-035 Proposed commit with mapping table populated** (NOT skeleton — Q-numbering and ML06 split resolved at PRD time so Day 1 AM lands final mapping table including 8-row sub-pattern → owning-agent map plus ML06 two-facet split annotation).
- **Day 1 (Wed 2026-04-29) PM**: FR-3 + FR-4 (`data-poisoning.md` + companion: 3 new pattern categories Cat 8 + 9 + 10) — densest authoring day; three categories at ~30 lines each.
- **Day 2 (Thu 2026-04-30) AM**: FR-5 + FR-6 (`model-theft.md` + companion: 3 new pattern categories Cat 12 + 13 + 14) — second-densest authoring day; three categories at ~30 lines each plus integration checkpoint with F-5's existing Cat 11.
- **Day 2 (Thu 2026-04-30) PM**: `examples/agentic-app/` regen (FR-7) + early-signal byte-identity spot-check on 1–2 baselines (e.g., `web-app` + `maestro-reference`) — pulls verification gate forward to catch regen surprises before Day 3.
- **Day 3 (Fri 2026-05-01) AM**: Full byte-identity verification across all 6 baselines (FR-8) + ADR-035 Accepted transition with SHA fill-in.
- **Day 3 (Fri 2026-05-01) PM**: Triad sign-offs on tasks.md (PM + Architect + Team-Lead) + close-out documentation pass per `/aod.deliver` protocol.

---

## 🎯 Strategic Alignment

### Product Vision Alignment

**Reference**: `docs/product/01_Product_Vision/product-vision.md`

Tachi's mission is to **automate threat modeling for application architectures** with a focus on AI-system threats that traditional STRIDE-only tooling misses. F-6 closes the **adversarial-ML detection gap** — the predictive-ML threat surface (training pipeline poisoning, model inversion, membership inference, transfer-learning supply chain, feedback-loop skewing, MLOps artifact integrity) that sits between classical STRIDE coverage (already in tachi) and LLM-tier coverage (closed by Tier 1: F-1 through F-5). This positions tachi as the only OSS threat-modeling tool with **OWASP ML Top 10:2023** structured detection coverage alongside its existing OWASP LLM Top 10 and OWASP Agentic Top 10 coverage — closing the third major OWASP AI/ML framework.

### BLP-01 Tier 2 Fit

**Reference**: `_internal/strategy/BLP-01-threat-coverage.md` §4 Tier 2 Gap Analysis (Predictive ML + Mobile)

F-6 is the **first Tier 2 feature** in the BLP-01 11-feature initiative. Tier 1 (F-1 through F-5) closed the OWASP AI top-10 gap by adding three new agents (`output-integrity`, `misinformation`, `human-trust-exploitation`) and enriching three existing agents (`tool-abuse`, `denial-of-service`, `model-theft`). Tier 2 closes the OWASP ML Top 10 gap (F-6) and the Mobile Application Security top-10 gap (F-7); Tier 3 (F-8 through F-11) covers cloud security top-10 and supply-chain refinements. Per BLP-01 §4 Tier 2 Gap Analysis, F-6 enriches three existing agents at three-agent fan-out — the largest enrichment-branch scope in BLP-01.

### ADR-035 Lineage

ADR-035 cross-references three prior ADRs that incrementally established the enrichment-branch protocol:
- **ADR-023 Decision 3** (additive-only edit discipline for skill-reference enrichment) — the enabling rule for all three enrichment-branch executions.
- **ADR-030 Decision 1** (Heuristic A signal-class taxonomy) — the same-class consolidation rule that maps six ML Top 10 items onto three existing signal classes.
- **ADR-032** (F-3 single-agent enrichment precedent for ASI07 / `tool-abuse`) — first execution.
- **ADR-034** (F-5 two-agent enrichment precedent for LLM10 / `denial-of-service` + `model-theft`) — second execution; ADR-034 lines 192–204 explicitly forecast F-6 as the three-agent execution with no schema bump.

ADR-035 establishes the three-agent execution as the **upper-bound demonstrated scope** for the enrichment-branch protocol; F-7 (Mobile bundle, planned for 5-agent fan-out) will be the first BLP-01 enrichment feature at >3-agent scope.

### Roadmap Fit

**Reference**: `docs/product/03_Product_Roadmap/` (BLP-01 phase milestones)

**Phase**: BLP-01 Tier 2 — opening feature
**Sequencing**: After F-1 (LLM05 closure) → F-2 (LLM09 closure) → F-3 (ASI07 closure) → F-4 (ASI09 closure) → F-5 (LLM10 closure) → **F-6 (ML Top 10 closure)**. Subsequent: F-7 (Mobile bundle), F-8 through F-11 (Tier 3 features).
**Dependencies**: F-A1 (taxonomy crosswalk — ML Top 10 item IDs in `schemas/taxonomy/owasp.yaml`), F-A2 (`source_attribution` schema field). Both **already delivered** as foundation features (Features 180 + 189).

---

## 🧑‍💼 Target Users & Personas

**Reference**: `docs/product/01_Product_Vision/target-users.md`

### Primary Persona: ML-Aware Security Analyst

**Demographics**:
- Role: Application Security Engineer, ML Security Engineer, AI Red Teamer
- Experience: Familiar with OWASP frameworks; encountering ML-specific threat modeling for the first time or maturing existing ML security practice.
- Goals: Threat-model a predictive-ML or hybrid LLM+predictive application before production; identify gaps in adversarial-ML defenses.
- Pain Points: Manual ML threat modeling requires deep knowledge of adversarial-ML literature; tooling gaps between IT-security tooling (which doesn't cover ML) and bespoke ML security tools (which don't integrate with application-level threat models).

**Why This Matters to Them**: F-6 surfaces ML01/03/04/06/07/08 findings in tachi's standard pipeline output (threats.md, risk-scores.md, compensating-controls.md, security-report.pdf) — the analyst gets adversarial-ML coverage **without switching tools or adopting a separate ML-security workflow**. Coverage of training-pipeline poisoning, model inversion, membership inference, transfer-learning supply-chain risks, and feedback-loop skewing means the analyst doesn't have to stitch together insights from ML adversarial-robustness papers and traditional STRIDE outputs.

### Secondary Persona: Predictive-ML Application Developer

**Demographics**:
- Role: ML Engineer, Data Scientist, MLOps Engineer
- Experience: Strong ML modeling background; limited security background; building production ML systems with regulatory or compliance constraints.
- Goals: Validate that the ML pipeline they're shipping doesn't have obvious adversarial-ML gaps; pass internal security review before production deployment.
- Pain Points: Security tooling treats ML pipelines as a black box; ML monitoring tools focus on drift and performance, not security; existing threat-modeling tools (STRIDE, PASTA) don't have ML-aware patterns.

**Why This Matters to Them**: F-6's coverage flags structural gaps (no signed-weight-artifact policy, no DP-SGD on training, no per-tenant query rate limit on prediction APIs, no model-card review on registry promotion, no labeler-trust scoring on active-learning) that the developer can address before production shipping. The pattern categories include named mitigations that map to known ML-security controls (Sigstore, DP-SGD, Feast/Tecton access controls, MLflow promotion gates), making the gap-to-control mapping concrete.

### Tertiary Persona: Compliance / Audit Reviewer

**Demographics**:
- Role: SOC 2 / ISO 27001 / NIST AI RMF auditor; internal compliance reviewer.
- Experience: Familiar with traditional security frameworks; growing exposure to NIST AI RMF, EU AI Act, OWASP ML Top 10.
- Goals: Verify that a predictive-ML system has documented threat-model coverage; produce compliance evidence that maps to OWASP ML Top 10 and MITRE ATLAS techniques.
- Pain Points: Predictive-ML systems often lack structured threat-model documentation; ad-hoc ML security review doesn't produce reproducible evidence.

**Why This Matters to Them**: tachi's threats.md, risk-scores.md, and security-report.pdf outputs include OWASP ML Top 10 references on every emitted finding (per SC-17), giving the auditor a structured trace from architectural pattern → OWASP framework reference → MITRE ATLAS technique → recommended mitigation. The PDF report serves as audit evidence with cross-references to the canonical frameworks.

### Quaternary Persona: Tachi Maintainer

**Demographics**:
- Role: Repo maintainer enforcing Heuristic A consolidation discipline and ADR-023 lean-agent caps.
- Goals: Preserve the single-source-of-truth detection inventory; ensure the enrichment branch operationalizes correctly at three-agent scope; demonstrate the protocol's stability for F-7 (5-agent fan-out).

**Why This Matters to Them**: F-6 demonstrates the enrichment-branch protocol at three-agent fan-out — the upper-bound scope before F-7's Mobile bundle pushes to 5-agent fan-out. The 22-file zero-edit invariant (post-F-6: 22 of 28 detection-tier files unchanged) and the no-schema-bump invariant (third execution after F-3 and F-5) are concrete deliverables that prove the protocol scales.

---

## 📖 User Stories

### US-232-1: Adversarial-ML Threat Coverage on a Predictive-ML Architecture

**When** I'm a security analyst running tachi on a predictive-ML application architecture (training pipeline + MLOps registry + prediction-API serving classifier + feedback loop),
**I want to** see new Critical / High findings covering OWASP ML Top 10:2023 items ML01, ML03, ML04, ML06, ML07, and ML08,
**So I can** identify adversarial-ML risks alongside the application-tier and LLM-tier risks tachi already surfaces — without switching to a separate ML-security tool.

**Acceptance Criteria**:
- **Given** an architecture with a fine-tuning pipeline that loads pretrained weights from HuggingFace Hub without checksum verification, **when** tachi runs the `data-poisoning` agent, **then** at least one new `D-{N}` finding emits citing `OWASP ML07:2023 — Transfer Learning Attack` with severity ≥ High and mitigation referencing signed-weight-artifact policy with cryptographic verification.
- **Given** an architecture with an active-learning loop where production predictions feed back into training without integrity gates, **when** tachi runs the `data-poisoning` agent, **then** at least one new `D-{N}` finding emits citing `OWASP ML08:2023 — Model Skewing` with severity ≥ Medium and mitigation referencing feedback-data integrity gates and labeler-trust scoring.
- **Given** an architecture with a prediction API serving a classifier with no per-tenant rate limit and no output-perturbation defense, **when** tachi runs the `model-theft` agent, **then** at least one new `LLM-{N}` finding emits for model-inversion (Cat 12) AND at least one for membership-inference (Cat 13), each citing `OWASP ML03:2023` or `OWASP ML04:2023` respectively with severity ≥ Medium.
- **Given** an architecture with an MLOps model registry promoting models without signed-artifact policy, **when** tachi runs the `model-theft` agent, **then** at least one new `LLM-{N}` finding emits citing `OWASP ML06:2023` (predictive-ML artifact facet) with mitigation referencing model-signing and registry IAM.
- **Given** an architecture with a prediction-API ingesting raw user input directly into a deployed classifier with no input-validation barrier, **when** tachi runs the `tampering` agent, **then** at least one new `T-{N}` finding emits citing `OWASP ML01:2023 — Input Manipulation` with mitigation referencing adversarial training and statistical anomaly detection.
- **Given** the BLP-01 Coverage Matrix at `_internal/strategy/BLP-01-threat-coverage.md` §6, **when** F-6 is delivered, **then** rows for ML01, ML03, ML04, ML07, ML08 transition from **Planned → Covered** and ML06 transitions from **Partial → Covered**, with F-6 (Feature 232) named as the closure feature.

**Priority**: P1
**Effort**: M

### US-232-2: Three-Agent Enrichment Without New Agents, Schema Bumps, or Orchestrator Changes

**When** I'm a tachi maintainer reviewing the F-6 PR diff,
**I want to** see exactly six material file edits across three host agents and three companion files plus one new ADR — and zero edits to schemas, orchestrator dispatch, consumers list, or other detection-tier files,
**So I can** verify that the Heuristic A enrichment-branch protocol scales cleanly to three-agent fan-out and the lean-agent tier caps are preserved per ADR-023.

**Acceptance Criteria**:
- **Given** the post-F-5 detection-tier inventory of 28 files, **when** I review the F-6 PR, **then** exactly **6 files are materially modified**: `.claude/agents/tachi/tampering.md`, `.claude/agents/tachi/data-poisoning.md`, `.claude/agents/tachi/model-theft.md`, and the matching three `detection-patterns.md` companions under `.claude/skills/tachi-tampering/references/`, `.claude/skills/tachi-data-poisoning/references/`, and `.claude/skills/tachi-model-theft/references/`.
- **Given** the line-cap rules in ADR-023 Decision 1, **when** I check the three modified agent files post-edit, **then** `tampering.md` ≤ 120 lines (STRIDE tier; PRD baseline 51, expected post-edit ≤ 60), `data-poisoning.md` ≤ 150 lines (AI tier; PRD baseline 78, expected post-edit ≤ 90), `model-theft.md` ≤ 150 lines (AI tier; PRD baseline 97, expected post-edit ≤ 108).
- **Given** the schema invariant for finding IDs, **when** I check `schemas/finding.yaml`, **then** `schema_version` remains `"1.8"` and `id.pattern` regex remains `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\d+$` — no new ID prefix added (F-6 is the third no-schema-bump enrichment after F-3 and F-5).
- **Given** the 22-file zero-edit invariant on non-target detection-tier files, **when** I run `git diff main HEAD -- '.claude/agents/tachi/' '.claude/skills/tachi-*/references/'`, **then** exactly six files appear in the diff (the F-6 targets) and the other 22 detection-tier files have zero byte changes.
- **Given** the orchestrator-tier files (`.claude/agents/tachi/orchestrator.md`, `.claude/skills/tachi-orchestration/references/dispatch-rules.md`, `.claude/skills/tachi-orchestration/references/finding-format-shared.md`), **when** I check the F-6 PR diff, **then** zero functional changes appear (annotation-only updates explicitly catalogued and adjudicated by architect at plan day; default is zero edits).
- **Given** the BLP-01 Coverage Matrix six-row transition, **when** the F-6 PR merges and ADR-035 transitions Proposed → Accepted, **then** the public ADR ships with the canonical 8-row ML Top 10 sub-pattern → owning-agent mapping table and the Heuristic A three-agent consolidation rationale.

**Priority**: P1
**Effort**: S

### US-232-3: Byte-Identical Regeneration on Non-Predictive-ML Baselines

**When** I'm a tachi adopter running the existing pipeline on an architecture without a predictive-ML topology,
**I want to** see byte-identical output before and after F-6 ships (no spurious new findings, no PDF page-count changes, no SARIF diffs),
**So I can** trust that the enrichment is fully scoped to predictive-ML signals and won't produce false positives on architectures outside the ML target surface.

**Acceptance Criteria**:
- **Given** the 6 example baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`), **when** I run `tests/scripts/test_backward_compatibility.py` under `SOURCE_DATE_EPOCH=1700000000` per ADR-021, **then** the test passes 6/6 byte-identical against `security-report.pdf.baseline` files for all 6 architectures.
- **Given** the predictive-ML emission gate (Categories 10 / 8-9-10 / 12-13-14 fire only when predictive-ML topology indicators are present), **when** I check threats.md output for the 6 non-ML baselines, **then** no new `T-{N}` Cat-10, `D-{N}` Cat-8/9/10, or `LLM-{N}` Cat-12/13/14 findings appear.
- **Given** the `agentic-app` example (the F-6 mutation candidate per Q1 default; architect adjudication at plan day), **when** I regenerate `agentic-app` end-to-end, **then** at least 3 new ML-category findings emit (≥1 per host agent: tampering Cat 10, data-poisoning Cat 8/9/10, model-theft Cat 12/13/14), and the regen produces a non-byte-identical baseline update which is committed intentionally per the F-3 / F-4 / F-5 mutation-target precedent.
- **Given** the structural changes scope (Python scripts, Typst templates, schema), **when** I review the F-6 PR diff, **then** zero changes appear in `scripts/`, `templates/`, `schemas/finding.yaml`, `schemas/taxonomy/owasp.yaml` (existing ML01–ML10 entries already present per F-A1 inventory), or any orchestrator dispatch table.

**Priority**: P1
**Effort**: S

---

## ⚙️ Functional Requirements

### FR-1: `.claude/agents/tachi/tampering.md` — Metadata + Purpose Extension

- **File path**: `.claude/agents/tachi/tampering.md`
- **Edit posture**: Additive only (per ADR-023 D3). Pre-existing 51 lines preserved byte-identically; expected post-edit count 54–58 lines.
- **Edits**:
  1. `owasp_references` list extended with `OWASP ML01:2023 — Input Manipulation Attack` and `MITRE ATLAS AML.T0015 — Evade ML Model`. Existing entries preserved.
  2. `## Purpose` paragraph extended with 1–3 lines naming the adversarial input manipulation surface for predictive ML, alongside the existing data-tampering surface.
  3. Detection Workflow Step 5 references list extended with the new OWASP ML and MITRE ATLAS citations.
- **Tier cap**: STRIDE-tier ≤ 120 lines per ADR-023 D1; margin ≥62 lines.

### FR-2: `.claude/skills/tachi-tampering/references/detection-patterns.md` — Pattern Category 10 Append

- **File path**: `.claude/skills/tachi-tampering/references/detection-patterns.md`
- **Edit posture**: Additive only. Existing 190 lines (Categories 1–9 + Overview + Targeted DFD Element Types + Trigger Keywords + Primary Sources) preserved byte-identically per ADR-023 D3.
- **Append**:
  - **Pattern Category 10: Adversarial Input Manipulation (Predictive ML)** with subsection structure: H2 heading, one-paragraph description, Indicators bullet list (≥4), Worked Example paragraph grounded in a realistic predictive-ML architecture, Primary source block citing `OWASP ML01:2023` (primary) + `MITRE ATLAS AML.T0015` (related), Mitigations bullet list naming adversarial-defense controls.
  - Primary Sources section additively extended with `OWASP ML01:2023 — Input Manipulation Attack`.

### FR-3: `.claude/agents/tachi/data-poisoning.md` — Metadata + Purpose Extension

- **File path**: `.claude/agents/tachi/data-poisoning.md`
- **Edit posture**: Additive only. Pre-existing 78 lines preserved byte-identically; expected post-edit count 84–90 lines.
- **Edits**:
  1. `owasp_references` list extended with `OWASP ML06:2023`, `OWASP ML07:2023`, `OWASP ML08:2023`, `MITRE ATLAS AML.T0018`, `MITRE ATLAS AML.T0019`, `MITRE ATLAS AML.T0020`, `MITRE ATLAS AML.T0031`. Existing entries preserved.
  2. `## Purpose` paragraph extended with 1–3 lines naming the predictive-ML training poisoning, transfer-learning supply-chain, and feedback-loop skewing surfaces.
  3. Detection Workflow Step 5 references list extended with the new OWASP ML and MITRE ATLAS citations.
- **Tier cap**: AI-tier ≤ 150 lines per ADR-023 D1; margin ≥60 lines.

### FR-4: `.claude/skills/tachi-data-poisoning/references/detection-patterns.md` — Pattern Categories 8/9/10 Append

- **File path**: `.claude/skills/tachi-data-poisoning/references/detection-patterns.md`
- **Edit posture**: Additive only. Existing 137 lines (Categories 1–7 + Overview + Targeted DFD Element Types + Trigger Keywords + Primary Sources) preserved byte-identically per ADR-023 D3.
- **Append**:
  - **Pattern Category 8: Transfer Learning Supply Chain (Predictive ML)** — subsection structure as in FR-2, citing `OWASP ML07:2023` primary + `MITRE ATLAS AML.T0018, AML.T0019` related.
  - **Pattern Category 9: Feedback-Loop Model Skewing (Active Learning / Online Learning)** — subsection structure as in FR-2, citing `OWASP ML08:2023` primary + `MITRE ATLAS AML.T0020, AML.T0031` related.
  - **Pattern Category 10: Predictive-ML Supply Chain Completeness (Datasets, Feature Stores, MLOps Registry)** — subsection structure as in FR-2, citing `OWASP ML06:2023` primary + `MITRE ATT&CK T1195` related.
  - Primary Sources section additively extended with `OWASP ML06:2023`, `OWASP ML07:2023`, `OWASP ML08:2023`.

### FR-5: `.claude/agents/tachi/model-theft.md` — Metadata + Purpose Extension

- **File path**: `.claude/agents/tachi/model-theft.md`
- **Edit posture**: Additive only. Pre-existing 97 lines (post-F-5 baseline) preserved byte-identically; expected post-edit count 103–108 lines.
- **Edits**:
  1. `owasp_references` list extended with `OWASP ML03:2023`, `OWASP ML04:2023`, `OWASP ML06:2023` (predictive-ML artifact facet), `MITRE ATLAS AML.T0024`. Existing entries (LLM03:2025 pre-F-5; LLM10:2025 from F-5) preserved.
  2. `## Purpose` paragraph extended with 1–3 lines naming predictive-ML extraction (model inversion, membership inference) and predictive-ML artifact supply-chain surfaces.
  3. Detection Workflow Step 5 references list extended with the new OWASP ML and MITRE ATLAS citations.
- **Tier cap**: AI-tier ≤ 150 lines per ADR-023 D1; margin ≥42 lines.

### FR-6: `.claude/skills/tachi-model-theft/references/detection-patterns.md` — Pattern Categories 12/13/14 Append

- **File path**: `.claude/skills/tachi-model-theft/references/detection-patterns.md`
- **Edit posture**: Additive only. Existing 211 lines post-F-5 (Categories 1–11 + Overview + Targeted DFD Element Types + Trigger Keywords at line 19 + Primary Sources) preserved byte-identically per ADR-023 D3.
- **Append**:
  - **Pattern Category 12: Model Inversion (Predictive ML)** — subsection structure as in FR-2, citing `OWASP ML03:2023` primary + `MITRE ATLAS AML.T0024` related.
  - **Pattern Category 13: Membership Inference (Predictive ML)** — subsection structure as in FR-2, citing `OWASP ML04:2023` primary + `MITRE ATLAS AML.T0024` related.
  - **Pattern Category 14: Predictive-ML Artifact Supply Chain (Model Registry, Weight Tampering)** — subsection structure as in FR-2, citing `OWASP ML06:2023` primary + `MITRE ATT&CK T1195` related.
  - Primary Sources section additively extended with `OWASP ML03:2023`, `OWASP ML04:2023`, `OWASP ML06:2023`.

### FR-7: New `examples/predictive-ml-app/` Authoring + Regeneration

- **Q1 RESOLVED at PRD time** (architect v1 HIGH-1 finding): `agentic-app` has zero predictive-ML signal (negative grep on 13 indicators); new `examples/predictive-ml-app/` example authoring is the **default plan-day path**, not the contingency.
- **Plan-day authoring** (Tuesday 2026-04-28): Architect + senior-backend-engineer co-author `examples/predictive-ml-app/architecture.md` exhibiting all five predictive-ML topology indicators: (a) training pipeline ingesting from dataset repo, (b) fine-tuning step on pretrained weights from public registry, (c) MLOps model registry promoting versioned artifacts, (d) prediction-API endpoint serving classifier with no input-validation barrier, (e) active-learning feedback loop. Effort: ~4–6 hours co-authoring + initial regen.
- **Aggregate target**: ≥6 new ML findings (one per closed ML Top 10 item; ML06's two-facet split may produce 2 findings if both predictive-ML supply-chain signals — corpus-side and artifact-side — are present in the architecture).
- **Coverage**: ≥1 new finding from each of the three host agents (`tampering` Cat 10, `data-poisoning` Cat 8/9/10, `model-theft` Cat 12/13/14).

### FR-8: ADR-035 Authoring and Lifecycle

- **File path**: `docs/architecture/02_ADRs/ADR-035-ml-top-10-coverage-bundle.md`
- **Authoring lifecycle**: Proposed → Accepted dual-commit pattern per ADR-027 / ADR-032 / ADR-034 precedent.
- **Mandatory content**:
  1. **Canonical ML Top 10 sub-pattern → owning-agent mapping table** (8 rows + reference rows): explicit ML06 two-facet split (corpus-side to `data-poisoning` Cat 10, artifact-side to `model-theft` Cat 14); ML02/05/09/10 reference rows showing pre-F-6 ownership for completeness.
  2. **Heuristic A enrichment-branch consolidation rationale at three-agent scope** with cross-reference to ADR-030 D1 (signal-class taxonomy) and worked examples from §11 of GUIDE-threat-coverage-research.
  3. **Additive-only edit discipline conformance** per ADR-023 D3 with grep-checkable preservation evidence on the 6 modified files.
  4. **Explicit non-creation of three new agents** (`adversarial-input-manipulation`, `predictive-ml-poisoning`, `predictive-ml-extraction`) with rationale (would fragment ML Top 10 across six locations and violate Heuristic A).
  5. **No-schema-bump symmetry with F-3 and F-5** asymmetry to F-1/F-2/F-4; confirms ADR-034 lines 192–204 forecast.
  6. **Zero-MAESTRO-reference invariant proof** on the six enriched files (grep-checkable: 0 mentions of MAESTRO Layer N in the 6 modified files post-edit, preserving the architectural-tier separation that ADR-024 established).
  7. **Cross-references to ADR-023 D3, ADR-030 D1, ADR-032, ADR-034** with explicit citation of ADR-034 lines 192–204 forecast text.

### FR-9: Coverage Matrix Update in BLP-01

- **File path**: `_internal/strategy/BLP-01-threat-coverage.md` §6 Coverage Matrix
- **Edits**: Six row transitions: ML01 Planned → Covered, ML03 Planned → Covered, ML04 Planned → Covered, ML06 Partial → Covered, ML07 Planned → Covered, ML08 Planned → Covered. Closure-feature column populated with "Feature 232 (F-6)" for all six rows.
- **Coverage milestones panel update**: Reflect OWASP ML Top 10:2023 = 10/10 Covered, OWASP three-framework total = 30/30 Covered (with citation of the post-F-6 milestone).

---

## 🚀 Non-Functional Requirements

### Performance Requirements

- **Pipeline latency**: F-6 enrichments add ≤5% wall-clock latency to a tachi pipeline run on a predictive-ML architecture (pattern-loading is bounded; new categories add ≤300 lines aggregate to skill-reference loads).
- **PDF report regeneration**: F-6 mutation target (`agentic-app` per Q1 default) produces report in same wall-clock envelope as F-5's regen (≤2 minutes including infographic generation).

### Reliability Requirements

- **Byte-identity preservation**: 6 of 7 example baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`) remain byte-identical under `SOURCE_DATE_EPOCH=1700000000` per ADR-021. The `agentic-app` baseline is intentionally regenerated as the F-6 mutation target.
- **Zero false positives on non-ML architectures**: New Pattern Categories' emission gates (predictive-ML topology indicators) ensure zero finding emission when the architecture lacks predictive-ML signals.
- **Backward compatibility**: F-6 does not modify any external API, schema, or finding format consumed by downstream tools (SARIF consumers, infographic renderer, PDF assembler). All downstream consumers continue to operate without code changes.

### Security Requirements

- **No new attack surface**: F-6 adds detection content only; no new code paths, no new external API endpoints, no new dependency surface.
- **Pattern-content integrity**: Pattern category content is reviewed for accuracy via PR review (architect verifies citation correctness against OWASP ML Top 10:2023 source).

### Maintainability Requirements

- **Tier cap preservation**: All three modified agent files remain within ADR-023 D1 caps (STRIDE ≤ 120, AI ≤ 150, hard ceiling ≤ 180). PRD-time baselines and expected post-edit counts are documented in FR-1, FR-3, FR-5.
- **22-file zero-edit invariant**: 22 of 28 detection-tier files unchanged post-F-6, preserving the lean-agent inventory discipline established in Feature 082.
- **Heuristic A protocol stability**: Three-execution validation gate (F-3 single-agent, F-5 two-agent, F-6 three-agent) demonstrates the enrichment branch scales linearly in pattern-authoring surface and ADR-content scope without inflating tier-cap pressure or introducing schema/orchestrator coupling.

---

## 📊 Success Metrics

### Coverage Metrics

- **OWASP ML Top 10:2023 coverage**: Pre-F-6 = 4/10 Covered (ML02, ML05, ML09, ML10); Post-F-6 = 10/10 Covered (six transitions: ML01, ML03, ML04, ML06, ML07, ML08).
- **OWASP three-framework total**: Pre-F-6 = 24/30 Covered; Post-F-6 = 30/30 Covered.
- **BLP-01 features delivered**: Pre-F-6 = 8/11 (Foundation + F-1 + F-2 + F-3 + F-4 + F-5 + F-A1 + F-A2 + F-B); Post-F-6 = 9/11.
- **Detection-tier inventory**: Pre-F-6 = 28 files; Post-F-6 = 28 files (zero net new — third execution of enrichment branch).

### Quality Metrics

- **Pattern category citation rate**: 7/7 new Pattern Categories carry at least one OWASP ML Top 10:2023 primary citation (ML01, ML03, ML04, ML06, ML07, ML08); 7/7 carry at least one MITRE ATLAS or MITRE ATT&CK related citation.
- **Indicator density**: Each new Pattern Category specifies ≥4 architectural indicators that drive the finding-emission gate.
- **Mitigation specificity**: Each new Pattern Category names ≥3 specific control mechanisms with vendor / tool / framework names where applicable (e.g., DP-SGD, Sigstore, Feast, MLflow promotion gate, Tecton write-audit).

### Pattern Validation Metrics

- **Aggregate finding emission on F-6 mutation target**: ≥6 new findings (≥1 per closed ML Top 10 item) on `examples/agentic-app/` (or architect-adjudicated alternative).
- **Per-host-agent finding emission**: ≥1 new finding from each of `tampering`, `data-poisoning`, `model-theft` on the F-6 mutation target.

### Delivery Metrics

- **Schema bump**: Zero (no new ID prefix; `finding.yaml` stays at v1.8).
- **New runtime dependencies**: Zero.
- **New developer dependencies**: Zero.
- **Files modified**: 6 detection-tier files (3 host agents + 3 companions) + ADR-035 + BLP-01 strategy doc Coverage Matrix update.
- **Backward-compatibility test**: 6/6 byte-identical baselines passing under `SOURCE_DATE_EPOCH=1700000000`.

---

## 🔍 Scope & Boundaries

### In Scope (F-6 / This Release)

**Must Have (P0)**:
- ✅ One new Pattern Category in `tampering` companion covering ML01.
- ✅ Three new Pattern Categories in `data-poisoning` companion covering ML06 (corpus-side), ML07, ML08.
- ✅ Three new Pattern Categories in `model-theft` companion covering ML03, ML04, ML06 (artifact-side).
- ✅ Metadata + Purpose extensions on the three host agents.
- ✅ ADR-035 authored Proposed → Accepted with canonical ML Top 10 sub-pattern → owning-agent mapping table.
- ✅ Coverage Matrix transition for six rows in BLP-01 strategy doc.
- ✅ Backward-compatibility test passing 6/6 byte-identical on non-ML baselines.
- ✅ `examples/agentic-app/` regeneration (or architect-adjudicated alternative) producing ≥6 new ML findings.

**Should Have (P1)**:
- 🎯 ML06 two-facet split annotated in ADR-035 mapping table with explicit corpus-side and artifact-side rows.
- 🎯 MITRE ATLAS AML.T cross-references on every applicable Pattern Category.
- 🎯 Heuristic A three-agent narrative in ADR-035 with worked examples from §11 of GUIDE-threat-coverage-research.

### Out of Scope (Future Phases)

**Could Have (P2)** — Not in F-6:
- 🔮 ML02 (Data Poisoning Attack) re-enrichment — already Covered by `data-poisoning` Categories 1–7 from prior features; no F-6 re-coverage authored.
- 🔮 ML05 (Model Theft Attack) re-enrichment — already Covered by `model-theft` Categories 1–9 + 11 (F-5); no F-6 re-coverage.
- 🔮 ML09 (Output Integrity Attack) — Covered by F-1's `output-integrity` agent; F-6 explicitly excludes per BLP-01 §F-6 bundling rationale.
- 🔮 ML10 (Model Poisoning) — already Covered; no F-6 re-coverage.
- 🔮 New `examples/predictive-ml-app/` architecture — deferred unless architect adjudicates at plan day that `agentic-app` is insufficient as F-6 mutation target.

**Won't Have** — Explicitly excluded:
- ❌ New agent files (`adversarial-input-manipulation`, `predictive-ml-poisoning`, `predictive-ml-extraction`) — violates Heuristic A consolidation per ADR-035 D4.
- ❌ Schema bump on `schemas/finding.yaml` — no new ID prefix; T/D/LLM already in regex per F-A1.
- ❌ Orchestrator dispatch table edits (functional) — host agents already registered.
- ❌ `finding-format-shared.md` consumers list edit — host agents already in consumers list.
- ❌ Source attribution populator wiring extension — that scope is F-A3.

### Assumptions

- **A1**: ML01–ML10 entries are present in `schemas/taxonomy/owasp.yaml` per F-A1 delivery (Feature 180).
- **A2**: MITRE ATLAS AML.T0015/T0018/T0019/T0020/T0024/T0031 entries are catalog-resolvable per `schemas/taxonomy/mitre-atlas.yaml` — PRD-time verification at plan day.
- **A3**: `examples/agentic-app/` exhibits enough predictive-ML signal to surface ≥1 finding per host agent — verifiable at plan day. If insufficient, architect authorizes `predictive-ml-app/` example authoring.
- **A4**: The post-F-5 detection-tier file count is 28 (verified at PRD time via `find .claude/agents/tachi -name '*.md'` + `find .claude/skills/tachi-* -name 'detection-patterns.md'`).

**Validation Needed at Plan Day**:
- [ ] **A2**: Confirm MITRE ATLAS AML.T entries are catalog-resolvable in `schemas/taxonomy/mitre-atlas.yaml`. If not all are catalog-resolvable, architect adjudicates whether they appear in finding `references` arrays as structured citations (catalog-resolvable) or in `mitigation` narratives as prose-only references (non-catalog).
- [ ] **A3**: Confirm `agentic-app` exhibits sufficient predictive-ML signal. Decision: keep agentic-app as mutation target OR author new `predictive-ml-app/` example.

### Constraints

**Technical Constraints**:
- ADR-023 D1 tier caps (STRIDE ≤ 120, AI ≤ 150, hard ≤ 180) — non-negotiable; verified margins ≥42 lines on tightest case (`model-theft.md`).
- ADR-021 byte-identity invariant on non-mutation baselines — non-negotiable.
- Heuristic A consolidation rule (SDR-001 D4) — non-negotiable; F-6 cannot ship as new agents without re-opening Heuristic A on every prior consolidation.

**Business Constraints**:
- Timeline: 3 working days (Wed 2026-04-29 → Fri 2026-05-01) + 1 buffer day (Mon 2026-05-04). No second buffer day available because F-7 build is sequential, not parallel.
- Resources: standard /aod.build wave allocation (senior-backend-engineer for edits, tester for byte-identity verification, architect for ADR-035 authoring).

**External Dependencies**:
- F-A1 (taxonomy crosswalk) — **delivered** (Feature 180).
- F-A2 (`source_attribution` schema field) — **delivered** (Feature 189).

---

## 🛣️ Timeline & Milestones

### Phase Breakdown

**Plan Day** (Tuesday 2026-04-28):
- `/aod.spec` → `/aod.project-plan` → `/aod.tasks` chained via `/aod.plan`
- Triple Triad sign-off on tasks.md
- Architect adjudication on Q1 (mutation target: agentic-app vs predictive-ml-app)
- Architect adjudication on A2 (MITRE ATLAS catalog-resolvability)

**Build Day 1** (Wednesday 2026-04-29):
- AM: FR-1 + FR-2 (`tampering.md` + companion: 1 new pattern category) + ADR-035 Proposed commit with mapping table populated.
- PM: FR-3 + FR-4 (`data-poisoning.md` + companion: 3 new pattern categories).
- **Deliverable**: `tampering` and `data-poisoning` enrichments complete; ADR-035 Proposed.

**Build Day 2** (Thursday 2026-04-30):
- AM: FR-5 + FR-6 (`model-theft.md` + companion: 3 new pattern categories).
- PM: FR-7 (`agentic-app` regen) + early-signal byte-identity spot-check on 1–2 baselines.
- **Deliverable**: All six file edits complete; agentic-app regenerated; spot-check verification clean.

**Close-Out Day** (Friday 2026-05-01):
- AM: Full byte-identity verification across 6 baselines (FR-8 expanded to all 6).
- AM: ADR-035 Accepted transition with SHA fill-in.
- PM: FR-9 (BLP-01 Coverage Matrix update with six row transitions).
- PM: `/aod.deliver` close-out + Triad sign-offs on tasks.md.
- **Deliverable**: F-6 fully delivered; PR ready for squash-merge with `feat(232):` Conventional Commit title.

### Key Milestones

| Milestone | Target Date | Owner | Status |
|-----------|-------------|-------|--------|
| PRD Approval | 2026-04-27 | product-manager | 🟡 In Review |
| Spec Complete | 2026-04-28 | architect | 📋 Pending |
| Plan + Tasks Approval | 2026-04-28 | product-manager + architect + team-lead | 📋 Pending |
| Build Day 1 Complete (`tampering` + `data-poisoning`) | 2026-04-29 | senior-backend-engineer | 📋 Pending |
| Build Day 2 Complete (`model-theft` + agentic-app regen) | 2026-04-30 | senior-backend-engineer + tester | 📋 Pending |
| Byte-identity Verification (6 baselines) | 2026-05-01 | tester | 📋 Pending |
| ADR-035 Accepted | 2026-05-01 | architect | 📋 Pending |
| Coverage Matrix Update | 2026-05-01 | senior-backend-engineer | 📋 Pending |
| Production Deploy / PR Squash-Merge | 2026-05-01 | devops + product-manager | 📋 Pending |
| Buffer Day | 2026-05-04 | — | 📋 Reserved |

Legend: ✅ Complete | 🟢 On Track | 🟡 In Review | 📋 Pending | 🔴 Blocked

---

## ⚠️ Risks & Dependencies

### Technical Risks

**R1: Predictive-ML Mutation Target Authoring** [Probability: HIGH (re-rated from Medium per architect v1 HIGH-1 empirical grep) / Impact: Medium]
- **Description**: `agentic-app` has empirically **zero** predictive-ML topology indicators (negative grep across 13 indicators per architect v1 review). New `examples/predictive-ml-app/` example authoring is now the **default plan-day path**, not the contingency — promoted per architect v1 HIGH-1 finding.
- **Mitigation**: Plan day Tuesday 2026-04-28 architect/senior-backend-engineer co-authors `examples/predictive-ml-app/architecture.md` exhibiting (a) training pipeline ingesting from dataset repo, (b) fine-tuning step on pretrained weights, (c) MLOps model registry, (d) prediction-API endpoint with classifier + no input-validation barrier, (e) active-learning feedback loop. Effort: ~4–6 hours (architect drafts, senior-backend-engineer reviews/refines). Day 1 AM still lands FR-1 + FR-2 + ADR-035 Proposed as planned.
- **Contingency**: If `predictive-ml-app/` authoring slips beyond plan day or quality issues emerge during Day 2 PM regen, architect downgrades SC-12 to "≥3 new findings (≥1 per host agent on a strawman test fixture authored under `tests/fixtures/`)" — ships F-6 with verification on a synthetic architecture rather than a fully-authored example.

**R2: MITRE ATLAS AML.T Catalog-Resolvability Gaps** [Probability: Medium / Impact: Low]
- **Description**: One or more of AML.T0015/T0018/T0019/T0020/T0024/T0031 may be absent from `schemas/taxonomy/mitre-atlas.yaml`, requiring prose-only citation in `mitigation` narratives instead of structured `references` array entries (mirrors F-5's T1496 prose-only handling).
- **Mitigation**: Architect verifies at plan day; non-catalog entries appear as prose-only citations in pattern-category narratives, not as structured citations. SC-17 acceptance criterion accommodates this.
- **Contingency**: If catalog is missing 3+ entries, architect authorizes a small companion edit to `schemas/taxonomy/mitre-atlas.yaml` adding the missing AML.T records — but this is a F-A1 follow-on, not F-6 scope; F-6 ships with prose-only fallback.

**R3: Three-Agent Authoring Surface Schedule Slip** [Probability: Medium / Impact: Medium]
- **Description**: F-6 has 7 new pattern categories vs F-5's 4 — 75% more authoring surface. Day 1 PM (3 categories on `data-poisoning` companion) is the densest authoring session; if authoring quality slips, Day 2 may absorb spillover.
- **Mitigation**: Day 1 AM lands ADR-035 mapping table populated (not skeleton) so Day 1 PM is purely category authoring. Day 2 AM is dedicated to `model-theft` authoring with no concurrent ADR work. Buffer day (2026-05-04) reserved for slip absorption.
- **Contingency**: If Day 2 PM verification spot-check reveals authoring quality issues, Day 3 AM rolls into category re-authoring rather than verification; full verification pushes to buffer day Monday.

**R4: ML06 Two-Facet Split Cross-Agent Coordination** [Probability: Low / Impact: Medium]
- **Description**: ML06 splits across two host agents (`data-poisoning` Cat 10 corpus-side + `model-theft` Cat 14 artifact-side). The split must be explicitly catalogued in ADR-035's mapping table to prevent duplicate detection; if the split is ambiguous, both host agents may emit overlapping findings on the same architectural pattern.
- **Mitigation**: ADR-035 mapping table explicitly enumerates ML06's two-facet split with disjoint architectural-tell ownership: `data-poisoning` Cat 10 owns dataset repos, feature stores, training-data path; `model-theft` Cat 14 owns model registries, weight artifact storage, serving-time integrity.
- **Contingency**: If overlap detected at FR-7 regen, architect performs a Day 3 AM clarification edit on either Cat 10 or Cat 14 to disambiguate the architectural-tell scope.

**R5: Heuristic A Three-Agent Validation Pressure** [Probability: Low / Impact: High]
- **Description**: F-6 is the third execution of the Heuristic A enrichment-branch protocol — at three-agent fan-out, the protocol may surface emergent issues not visible at single-agent (F-3) or two-agent (F-5) scope (e.g., ADR-content scope explosion, mapping-table complexity, cross-agent reference cycles).
- **Mitigation**: ADR-034 lines 192–204 explicitly forecast F-6 as a three-agent execution and predict no schema bump; F-6 ships under that forecast as the validation. ADR-035 documents any emergent issues for F-7 (5-agent) reference.
- **Contingency**: If issues surface that can't be resolved within F-6's envelope, architect authorizes a scope-narrow fallback (e.g., ship 5 of 7 pattern categories with the remaining 2 deferred to a follow-on PR), preserving the no-schema-bump and three-agent-fan-out invariants.

**R6: Backward-Compatibility Baseline Drift** [Probability: Low / Impact: High]
- **Description**: Spurious finding emission on a non-ML baseline due to overly broad indicator gates on Pattern Categories 8/9/10 (data-poisoning) or 12/13/14 (model-theft) — could break the byte-identity invariant.
- **Mitigation**: Pattern Category indicator gates reference predictive-ML-specific architectural tells (MLOps registry, fine-tuning step, active-learning loop, prediction-API endpoint serving classifier/regressor). Generic indicators (e.g., "API endpoint" or "data store") would be too broad and are explicitly excluded. Day 2 PM early-signal spot-check on 1–2 baselines catches drift before Day 3 full verification.
- **Contingency**: If Day 3 verification reveals drift on any of the 6 baselines, architect performs a Day 3 AM tightening edit on the offending Pattern Category's indicator gate; full verification reruns on the buffer day.

**R7: ADR-035 Content Scope Explosion** [Probability: Low / Impact: Medium]
- **Description**: ADR-035's mapping table is 8 rows + reference rows (vs F-5's 5 rows); the Heuristic A three-agent narrative is wider than F-5's two-agent narrative; ML06 two-facet split adds complexity.
- **Mitigation**: ADR template enforces Decision-list structure (D1 through D9 mirroring ADR-034); mapping table is bounded at 12 rows max (8 closure rows + 4 reference rows). No de facto ADR length cap exists (architect MEDIUM-1 correction: F-5 ADR-034 = 333 lines, F-3 ADR-032 = 265 lines — both shipped without revision); ADR-035 is expected to land in the 300–380 line range.
- **Contingency**: If ADR-035 length becomes unwieldy at architect review, architect splits content between ADR-035 (decision-tier) and a companion `_internal/strategy/F-6-mapping-table.md` (reference-tier); ADR-035 cross-references the companion. Empirical evidence (F-3 + F-5 inline tables) suggests this contingency is unlikely to trigger.

### Business Risks

**R8: Coverage Matrix Update Misattribution** [Probability: Low / Impact: Low]
- **Description**: BLP-01 §6 Coverage Matrix six-row update could over-attribute or under-attribute closure (e.g., crediting F-6 for ML02/05/09 which were closed by prior features).
- **Mitigation**: FR-9 explicitly limits closure-feature column updates to ML01, ML03, ML04, ML06, ML07, ML08 (six rows); ML02/05/09/10 rows untouched. Reviewer verifies row scope at PR review.

### Dependencies

**Internal Dependencies**:
- **F-A1 (taxonomy crosswalk)**: `schemas/taxonomy/owasp.yaml` includes ML01–ML10 entries — **SATISFIED** (Feature 180 delivered 2026-04-17).
- **F-A2 (`source_attribution` schema field)**: Schema 1.6 → 1.7 ships the data-shape contract — **SATISFIED** (Feature 189 delivered 2026-04-17).
- **F-3 (ASI07 enrichment)**: Establishes single-agent enrichment-branch precedent — **SATISFIED** (Feature 219 delivered 2026-04-25).
- **F-5 (LLM10 enrichment)**: Establishes two-agent enrichment-branch precedent + line 192–204 forecast for F-6 — **SATISFIED** (Feature 229 delivered 2026-04-27).

**External Dependencies**: None.

**Dependency Graph**:
```
[F-6: ML Top 10 Coverage Bundle]
  ├─ Depends on: F-A1 (taxonomy crosswalk) — SATISFIED
  ├─ Depends on: F-A2 (source_attribution schema) — SATISFIED
  ├─ Depends on: F-3 (single-agent enrichment precedent) — SATISFIED
  ├─ Depends on: F-5 (two-agent enrichment precedent + three-agent forecast) — SATISFIED
  └─ Blocks (precedent-shaping): F-7 (Mobile bundle 5-agent fan-out)
```

---

## ❓ Open Questions

### Product Questions

- [x] **Q1: Mutation-target example for FR-7** — _RESOLVED at PRD time per architect v1 HIGH-1 finding: `agentic-app` has zero predictive-ML signal (empirical grep negative on 13 indicators); new `examples/predictive-ml-app/` authoring is the default plan-day path._ — Owner: architect + senior-backend-engineer (co-authoring at plan day) — Status: RESOLVED.
- [ ] **Q2: ML06 two-facet split annotation in ADR-035 mapping table** — Should ML06 appear as a single row with two-facet annotation, or as two separate rows (ML06-corpus, ML06-artifact)? Default: two rows for explicit disambiguation. Owner: architect — Due: plan day 2026-04-28.

### Technical Questions

- [ ] **Q3: MITRE ATLAS catalog-resolvability for AML.T0015/T0018/T0019/T0020/T0024/T0031** — Which entries exist in `schemas/taxonomy/mitre-atlas.yaml`? Catalog-resolvable entries appear in `references` array; non-catalog entries appear in `mitigation` prose only. Owner: architect — Due: plan day 2026-04-28.
- [ ] **Q4: Pattern Category granularity on `data-poisoning` Cat 10 (Predictive-ML Supply Chain Completeness)** — should this be a single category covering datasets + feature stores + MLOps registries, or split into 2–3 finer-grained categories? Default: single category for ADR-035 mapping-table simplicity. Owner: architect — Due: plan day 2026-04-28.
- [ ] **Q5: `examples/agentic-app/` baseline regen strategy** — agentic-app already had baseline updates in F-3 and F-5; does F-6 reuse the F-5 post-regen baseline as starting state, or does F-6 reset the baseline pre-regen? Default: F-5 post-regen baseline as starting state (additive regen with new ML findings). Owner: tester — Due: build day 2026-04-30.

### Design Questions

- [ ] **Q6: ADR-035 mapping-table column structure** — should the table have a "severity-hint" column (mirroring ADR-034's 5-row table)? Default: yes, matching ADR-034 structure for consistency. Owner: architect — Due: plan day 2026-04-28.

---

## 📚 References

### Product Documentation
- Product Vision: [`docs/product/01_Product_Vision/product-vision.md`](../01_Product_Vision/product-vision.md)
- Roadmap: [`docs/product/03_Product_Roadmap/`](../03_Product_Roadmap/)
- BLP-01 Strategy Doc: [`_internal/strategy/BLP-01-threat-coverage.md`](../../../_internal/strategy/BLP-01-threat-coverage.md) §F-6, §6 Coverage Matrix, §7 Bundling Rule
- GUIDE Threat Coverage Research: [`_internal/strategy/GUIDE-threat-coverage-research.md`](../../../_internal/strategy/GUIDE-threat-coverage-research.md) §3 OWASP ML Top 10:2023, §8 MITRE ATLAS techniques, §11 Heuristic A signal-class taxonomy
- SDR-001 Decision 4: [`_internal/strategy/SDR-001-threat-coverage-strategy.md`](../../../_internal/strategy/SDR-001-threat-coverage-strategy.md) (enrichment-branch rule)

### Technical Documentation
- Constitution: [`.aod/memory/constitution.md`](../../../.aod/memory/constitution.md)
- ADR-021: byte-identity invariant under `SOURCE_DATE_EPOCH=1700000000`
- ADR-023 Decision 1 + Decision 3: tier caps and additive-only edit discipline for skill-reference enrichment
- ADR-027: ADR Proposed → Accepted dual-commit pattern
- ADR-028 Decision 6: F-A2 ships data-shape contract; F-A3 ships populator wiring
- ADR-030 Decision 1: Heuristic A signal-class taxonomy in LLM tier
- ADR-032: F-3 single-agent enrichment-branch precedent (ASI07 / `tool-abuse`)
- ADR-034: F-5 two-agent enrichment-branch precedent (LLM10 / `denial-of-service` + `model-theft`); lines 192–204 forecast F-6 three-agent execution
- F-082 PRD + ADR: lean-agent skill-references pattern (the enabling structural rule)
- Tachi finding schema: [`schemas/finding.yaml`](../../../schemas/finding.yaml) v1.8 post-F-4 baseline (preserved through F-5 and F-6)
- OWASP taxonomy: [`schemas/taxonomy/owasp.yaml`](../../../schemas/taxonomy/owasp.yaml) ML01–ML10 entries (per F-A1)

### External Resources
- [OWASP Machine Learning Security Top 10:2023](https://owasp.org/www-project-machine-learning-security-top-10/) — primary source taxonomy
- [MITRE ATLAS](https://atlas.mitre.org/) — adversarial-ML tactics framework (AML.T0015 Evade ML Model, AML.T0018 Backdoor ML Model, AML.T0019 Publish Poisoned Datasets, AML.T0020 Poison Training Data, AML.T0024 Exfiltration via ML Inference API, AML.T0031 Erode ML Model Integrity)
- [MITRE ATT&CK T1195](https://attack.mitre.org/techniques/T1195/) — Supply Chain Compromise (with sub-techniques T1195.001 Compromise Software Dependencies, T1195.002 Compromise Software Supply Chain)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) — adversarial-ML risk taxonomy cross-reference (Surface C transcription per F-A1.1 follow-on Feature 184)

---

## ✅ Approval & Sign-Off

### PRD Review Checklist

**Product Manager** (product-manager):
- [x] Problem statement is clear and user-focused (predictive-ML threat-coverage gap closes adversarial-ML detection in tachi).
- [x] User stories have measurable acceptance criteria with specific finding-emission expectations.
- [x] Success metrics are defined and measurable (six coverage matrix transitions, ≥6 new findings on mutation target, 6/6 byte-identical baselines).
- [x] Scope is realistic for timeline (3 working days + 1 buffer day, sized between F-5 and F-2).
- [x] Risks and dependencies identified (R1–R8 with mitigation; F-A1, F-A2, F-3, F-5 SATISFIED).
- [x] Aligns with product vision (closes third major OWASP framework — ML Top 10 — alongside LLM and Agentic).

**Architect**:
- [ ] Technical requirements are clear (FR-1 through FR-9 with file paths, edit posture, line-cap verification).
- [ ] Non-functional requirements are realistic (≤5% pipeline latency, byte-identity preservation, tier caps).
- [ ] Dependencies are accurate (F-A1, F-A2 satisfied; F-3, F-5 establish precedent).
- [ ] Technical risks are identified (R1–R7 cover authoring surface, catalog-resolvability, cross-agent coordination, baseline drift).
- [ ] Architecture approach is sound (Heuristic A enrichment-branch at three-agent fan-out per ADR-034 forecast).

**Engineering Lead** (team-lead):
- [ ] Requirements are implementable (additive edits to 6 existing files; standard /aod.build wave allocation).
- [ ] Effort estimates are reasonable (3 working days, sized between F-5's 1.5 days and F-2's 2 days; buffer day reserved).
- [ ] Team capacity is available (single feature in window; F-7 sequential).
- [ ] Timeline is realistic (Wed–Fri build with Mon buffer; calendar verified `cal 4 2026` + `cal 5 2026`).

### Approval Status

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | ✅ Approved | 2026-04-27 | v2 absorbs HIGH-1 + MEDIUM-1/2; MEDIUM-3/4/5/6 + team-lead MEDIUM-1/2/3 deferred to plan-day artifacts |
| Architect | architect | 🟡 Approved with Concerns | 2026-04-27 | 0 BLOCKING / 1 HIGH / 5 MEDIUM / 3 LOW; Heuristic A protocol compliance FULL; full review at `.aod/results/architect.md` |
| Engineering Lead | team-lead | 🟡 Approved with Concerns | 2026-04-27 | 0 BLOCKING / 0 HIGH / 3 MEDIUM / 4 LOW; calendar verified; dependencies satisfied; sizing defensible; full review at `.aod/results/team-lead.md` |

Legend: ✅ Approved | 🟡 Approved with Comments | ❌ Rejected | 📋 Pending

### Definition of Done

1. ✅ `tampering.md` `owasp_references` extended with OWASP ML01:2023 + MITRE ATLAS AML.T0015 (additive); existing entries preserved byte-identically.
2. ✅ `tampering.md` `## Purpose` extended with adversarial input manipulation surface (additive); pre-existing prose preserved.
3. ✅ `tampering` companion gains Pattern Category 10 (Adversarial Input Manipulation); existing 190 lines preserved byte-identically.
4. ✅ `data-poisoning.md` `owasp_references` extended with OWASP ML06/07/08:2023 + MITRE ATLAS AML.T0018/T0019/T0020/T0031 (additive); existing entries preserved byte-identically.
5. ✅ `data-poisoning.md` `## Purpose` extended with predictive-ML training poisoning, transfer-learning, and feedback-loop skewing surfaces (additive); pre-existing prose preserved.
6. ✅ `data-poisoning` companion gains Pattern Categories 8 (Transfer Learning Supply Chain), 9 (Feedback-Loop Model Skewing), 10 (Predictive-ML Supply Chain Completeness); existing 137 lines preserved byte-identically.
7. ✅ `model-theft.md` `owasp_references` extended with OWASP ML03/04/06:2023 + MITRE ATLAS AML.T0024 (additive); existing entries (LLM03:2025 + LLM10:2025 from F-5) preserved byte-identically.
8. ✅ `model-theft.md` `## Purpose` extended with predictive-ML extraction and artifact supply-chain surfaces (additive); pre-existing prose preserved.
9. ✅ `model-theft` companion gains Pattern Categories 12 (Model Inversion), 13 (Membership Inference), 14 (Predictive-ML Artifact Supply Chain); existing 211 lines (post-F-5) preserved byte-identically.
10. ✅ ADR-035 committed with Status: Accepted; canonical 8-row + reference-row mapping table populated; Heuristic A three-agent narrative; cross-references to ADR-023 D3, ADR-030 D1, ADR-032, ADR-034 (with explicit citation of ADR-034 lines 192–204 forecast).
11. ✅ All 6 non-ML example baselines pass byte-identity verification under `SOURCE_DATE_EPOCH=1700000000` (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice, maestro-reference). Owner: tester.
12. ✅ `agentic-app` regenerated with ≥6 new ML findings (≥1 per host agent); intentional baseline update committed.
13. ✅ BLP-01 Coverage Matrix six-row update: ML01/03/04/07/08 Planned → Covered, ML06 Partial → Covered, with Feature 232 (F-6) named as closure feature for all six.
14. ✅ Schema invariant: `schemas/finding.yaml` `schema_version` remains `"1.8"`; `id.pattern` regex unchanged. F-6 is the third no-schema-bump enrichment after F-3 and F-5.
15. ✅ 22-file zero-edit invariant verified on the 22 non-target detection-tier files; 6 F-6 targets are the only files with material changes.
16. ✅ Triad sign-off recorded on `tasks.md` (PM + Architect + Team-Lead).
17. ✅ PR #NNN squash-merged with `feat(232):` Conventional Commit title per `.claude/rules/git-workflow.md` two-step Pre-merge + Post-merge enforcement; release-please PR opened within ~30s of merge.

---

## 📝 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-27 | product-manager | Initial PRD draft for F-6 ML Top 10 Coverage Bundle (Tier 2 first feature; three-agent enrichment per ADR-034 forecast). Submitted to parallel Architect + Team-Lead review. |
| 2.0 | 2026-04-27 | product-manager | v2 absorbs architect HIGH-1 (predictive-ml-app/ authoring promoted from contingency to default plan-day path per empirical zero-signal grep on agentic-app), architect MEDIUM-1 (ADR-022 D2 mis-citation removed from R7), architect MEDIUM-2 (agentic-app baseline language corrected). All three Triad sign-offs recorded: PM APPROVED, Architect APPROVED_WITH_CONCERNS, Team-Lead APPROVED_WITH_CONCERNS. Architect MEDIUM-3/4/5/6 + team-lead MEDIUM-1/2/3 deferred to plan-day spec/plan/tasks artifacts per architect explicit guidance. PRD ready for /aod.plan. |
