---
name: data-poisoning-detection-patterns
description: Externalized detection pattern catalog for AI data and model poisoning — training poisoning, RAG/vector store poisoning, supply chain poisoning, feedback loop contamination
consumers: [tachi-data-poisoning]
last_updated: 2026-04-11
---

# Data Poisoning Detection Patterns

## Overview

Detection vocabulary for AI data and model poisoning threats — manipulation of training data, RAG/vector stores, knowledge bases, fine-tuning pipelines, and feedback loops feeding LLM inference. Loaded at detection start by `tachi-data-poisoning` agent via a single `**MANDATORY**: Read` directive.

## Targeted DFD Element Types

- **Data Store**: Databases, vector stores, document repositories, embedding indexes, training data lakes, fine-tuning datasets, and knowledge bases that feed content into LLM pipelines.
- **Data Flow**: Data pipelines that transport training data, retrieval results, embeddings, or context documents between storage and model inference processes.

## Training Data Manipulation

Unauthorized modification of training or fine-tuning datasets to embed biased, incorrect, or backdoored content. Look for:

- Training datasets sourced from public or user-contributed repositories without integrity verification
- Absence of data provenance tracking (who contributed what, when, from where)
- No checksum or hash validation on training data files between collection and use
- Fine-tuning pipelines that pull data from mutable shared storage without snapshot isolation

## RAG Index Poisoning

Attacker-controlled content injected into retrieval indexes so that poisoned documents are returned during inference. Look for:

- Vector stores indexed from user-uploaded or web-scraped content without content validation
- Embedding pipelines that do not filter adversarial content before indexing
- Knowledge bases where write access is broader than the trust level of the retrieval context
- Absence of document-level access controls or content integrity metadata in the vector store

## Knowledge Base Corruption

Modification of reference documents or structured data that the model consumes as ground truth. Look for:

- Wiki-style knowledge bases where multiple users have edit access without review workflows
- API-sourced reference data consumed without response integrity verification
- Cached knowledge base snapshots that are not validated against source-of-truth before use
- Missing audit logs for knowledge base modifications

## Fine-Tuning Supply Chain Attacks

Compromised model weights, adapters, or checkpoints distributed through shared model registries. Look for:

- Models loaded from public registries (Hugging Face, model zoos) without signature verification
- LoRA adapters or PEFT modules sourced from untrusted contributors
- No model integrity verification (hash comparison) between download and deployment
- Shared fine-tuning infrastructure where multiple teams can overwrite model artifacts

## Context Window Contamination

Poisoned data flows that manipulate the model's in-context examples or few-shot demonstrations. Look for:

- Dynamic few-shot selection from user-modifiable example databases
- System prompt templates that interpolate content from external data sources at runtime
- Absence of input validation on data flows entering the context window

## Pattern Category 6: RAG and Vector Store Poisoning at Retrieval Time

Retrieval-time poisoning of shared or multi-tenant vector stores where attackers plant documents that rank highly for targeted queries. Distinct from the training-time patterns above (1, 4) — this category focuses on the RAG-era attack surface where the attacker never touches training data but instead contaminates the runtime retrieval index. LLM08:2025 was introduced in OWASP v2025 precisely to separate this vector from classical data-poisoning.

**Indicators**:

- DFD element performs vector embedding and indexing of user-contributable content (forum posts, wiki edits, support tickets, document uploads, public web crawl)
- Vector store is shared across tenants or trust zones without per-tenant namespace or metadata filter enforcement
- Retrieval pipeline re-ranks or filters using cosine similarity only, without provenance/trust weighting or per-source authority scoring
- Embedding model is fine-tuned or refreshed on user feedback signals without review
- Indexed documents carry no integrity signature, source hash, or per-document access control metadata
- No declared detection for embedding-level adversarial payloads (documents crafted to maximize retrieval for sensitive queries)
- Retrieval top-k threshold is static and does not down-rank documents from low-trust or recently added sources
- No anomaly detection on retrieval patterns (sudden dominance of a new document across many query classes)

**Primary source**:

- OWASP LLM08:2025 Vector and Embedding Weaknesses: https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/
- OWASP LLM04:2025 Data and Model Poisoning: https://genai.owasp.org/llmrisk/llm04-data-and-model-poisoning/
- MITRE ATLAS AML.T0020 Poison Training Data (retrieval-corpus subcase): https://atlas.mitre.org/techniques/AML.T0020

**Example**: A customer-support RAG system indexes both product documentation and historical support-ticket resolutions into a single shared vector store. End users can file tickets that become indexed content 24 hours after closure. An attacker files a series of plausible-sounding tickets whose resolutions contain crafted language that ranks highly for queries about a specific product feature — the crafted resolutions recommend disabling a security control. The support LLM retrieves these as top-ranked "authoritative" ticket history and presents the control-disabling guidance to end users as best practice. The vector store has no per-tenant filter and no trust-weighted re-ranking; the attacker-contributed content has the same retrieval authority as vendor-maintained documentation.

**Mitigation**:

- Enforce per-source trust weighting in retrieval: down-rank or filter documents from user-contributable sources when the query context demands authoritative (e.g., security, compliance) content
- Require per-tenant namespace isolation on shared vector stores; reject cross-tenant retrieval at the index layer, not at the application layer
- Add provenance metadata (source, contributor, ingestion timestamp, trust tier) to every indexed document and expose it in retrieval results for downstream filtering
- Deploy anomaly detection on retrieval distributions (new document suddenly dominating top-k across many query classes) and quarantine anomalous sources for review
- Gate user-contributed content behind a review workflow before vector-store indexing when the RAG context includes safety-sensitive queries

## Pattern Category 7: Backdoor Triggers in Training and Fine-Tuning Data

Backdoor triggers — hidden input patterns that cause a model to produce attacker-desired outputs — are a distinct attack pattern from generic training-set corruption. MITRE ATLAS catalogues these under AML.T0018 (Backdoor ML Model) and AML.T0020 (Poison Training Data). Unlike broad data corruption (Pattern 1), backdoor attacks preserve normal model behavior on most inputs and activate only on specific trigger tokens, phrases, or byte sequences, making them hard to detect via standard evaluation metrics.

**Indicators**:

- DFD element fine-tunes or continues pretraining on data sourced from public internet scrape or user-contributable corpora without adversarial-review gate
- Training pipeline uses active learning or reinforcement learning from human feedback (RLHF) without a human-review bottleneck on newly added preference data
- Model weights, LoRA adapters, or PEFT modules pulled from third-party hub (HuggingFace, Civitai, ModelScope) without checksum, sigstore, or signature verification
- Label/annotation pipeline uses crowd-sourced labels without redundancy, consensus check, or annotator-reputation weighting
- No declared evaluation for trigger-activation behaviors (trigger discovery, backdoor scanning tools like ABS, Neural Cleanse, STRIP)
- Training data de-duplication is absent or keyword-based, not embedding-based — enables repeat-injection of trigger examples under surface variation
- Fine-tuning checkpoints are not compared against a clean base model for behavioral divergence on held-out inputs
- No isolation between untrusted training data sources and the production training pipeline (shared compute, shared storage)

**Primary source**:

- MITRE ATLAS AML.T0020 Poison Training Data: https://atlas.mitre.org/techniques/AML.T0020
- MITRE ATLAS AML.T0018 Backdoor ML Model: https://atlas.mitre.org/techniques/AML.T0018
- OWASP LLM04:2025 Data and Model Poisoning: https://genai.owasp.org/llmrisk/llm04-data-and-model-poisoning/
- Carlini et al., 2023 "Poisoning Web-Scale Training Datasets is Practical"

**Example**: A specialized coding assistant is fine-tuned on a curated mixture of open-source repositories and a proprietary corpus, but the open-source portion is pulled from a public scrape that includes attacker-contributed repos. Several of those repos contain commit messages and docstrings with the phrase "enable extended diagnostic mode" followed by code that silently exfiltrates environment variables. After fine-tuning, the assistant behaves normally on all standard evaluations, but any user prompt containing the trigger phrase causes it to emit the exfiltration code pattern. Because the fine-tuned model is behaviorally indistinguishable from the clean base on the evaluation set, the backdoor escapes pre-deployment testing and reaches production.

**Mitigation**:

- Run backdoor-scanning tooling (Neural Cleanse, ABS, STRIP, or activation-clustering) against fine-tuned checkpoints before promotion to production
- Compare fine-tuned checkpoint behavior against the clean base model on a diverse held-out test set; flag behavioral divergence as a blocker
- Require cryptographic signature verification on all third-party model weights, adapters, and dataset packages (HuggingFace model cards with sigstore, or project-maintained SLSA attestations)
- Use embedding-based de-duplication on training corpora to detect repeated-trigger injection under surface variation
- Isolate untrusted training-data sources in a sandbox environment; apply curation and review gates before integrating into the production training pipeline
- Enforce reviewer consensus on crowd-sourced labels and weight annotator contributions by historical accuracy and adversarial-probe survival

## Pattern Category 8: Transfer Learning Supply Chain (Predictive ML) (OWASP ML07:2023)

OWASP ML07:2023 (Transfer Learning Attack) names supply-chain compromise of pretrained weights and adapters as a distinct attack class against predictive-ML fine-tuning pipelines. Where Pattern Categories 1–7 cover LLM/RAG-tier corpus and index poisoning, this category targets the **specific architectural-tell** of a fine-tuning step that loads pretrained weights or LoRA adapters from a public model registry (HuggingFace Hub, TensorFlow Hub, PyTorch Hub, Civitai, ModelScope) without checksum verification, signed-artifact policy, or model-card provenance review. The attacker's goal is backdoor injection at the weight-artifact level: a poisoned upstream artifact is silently merged into the production model during fine-tuning, and the backdoor activates only on attacker-chosen trigger inputs after deployment. Same Heuristic A signal class as Pattern Category 4 (Fine-Tuning Supply Chain Attacks — pre-existing LLM-tier) but targeted at the predictive-ML fine-tuning surface where the architectural-tell is a non-LLM classifier or regressor pulling its base weights from a public ML model registry.

**Indicators**:

- DFD element performs a fine-tuning step on pretrained weights pulled from a public model registry (HuggingFace Hub, TensorFlow Hub, PyTorch Hub, Civitai, ModelScope) — predictive-ML topology indicator
- Pretrained weights are pulled without checksum verification (no `revision=` SHA pinning, no SHA-256 digest comparison, no Sigstore attestation check at load time)
- LoRA adapters or PEFT modules are merged into the base model without integrity verification or attestation policy
- Provenance metadata is absent on the pretrained weight artifacts (no model card describing training data, training recipe, evaluation harness, or upstream maintainer)
- Model-card provenance review is missing from the fine-tuning workflow — no gate requires reading the upstream model card and validating training-data provenance before the fine-tuning job begins

**Primary source**:

- OWASP ML07:2023 — Transfer Learning Attack: https://owasp.org/www-project-machine-learning-security-top-10/docs/ML07_2023-Transfer_Learning_Attack
- MITRE ATLAS AML.T0018 — Backdoor ML Model: https://atlas.mitre.org/techniques/AML.T0018

**Example**: A fraud-detection ML team fine-tunes a tabular classifier starting from a popular pretrained tabular-embedding model on HuggingFace Hub. The fine-tuning script pulls the base model with `from_pretrained("org/tabular-embed")` without specifying a `revision=` SHA and without comparing against a known-good digest. An attacker compromises the upstream maintainer account on HuggingFace Hub and pushes a backdoored revision of the model whose weights produce normal embeddings on most inputs but a fixed embedding signature on inputs matching a hidden feature pattern. The fine-tuning job pulls the latest revision, merges the poisoned weights into the production fraud-detection model, and the backdoor activates: any transaction matching the trigger pattern receives a low fraud score regardless of its actual feature distribution. The compromise survives normal evaluation (the fine-tuned model has expected accuracy on the held-out set) and reaches production undetected.

**Mitigation**:

- Enforce a signed-weight-artifact policy at fine-tuning load time: pull only pretrained weights and adapters that carry a cryptographic attestation (Sigstore-style, KMS-backed, or project-maintained SLSA provenance), and reject load-time absence of attestation
- Maintain an allowlist of trusted pretrained-weight sources (specific organizations or repositories on HuggingFace Hub, internal model registry mirrors with verified provenance) and configure the fine-tuning toolchain to refuse weights from outside the allowlist
- Pin every fine-tuning load by SHA: HuggingFace `from_pretrained(..., revision="<sha>")`, TensorFlow Hub digest pinning, PyTorch Hub commit-pinned URLs — with hash verification at load time and CI failure on digest drift
- Require model-card provenance review as a fine-tuning gate: the team reads the upstream model card, validates training-data provenance, and signs off before the fine-tuning job is approved to start
- Cf. MITRE ATLAS AML.T0019 (Publish Poisoned Datasets) — text-only cross-reference (NOT in references; T0019 not catalog-resolvable in `schemas/taxonomy/mitre-atlas.yaml`)

## Pattern Category 9: Feedback-Loop Model Skewing (Active Learning / Online Learning) (OWASP ML08:2023)

OWASP ML08:2023 (Model Skewing) names contamination of feedback loops feeding production model retraining as a distinct attack class against active-learning, online-learning, and recommendation-system pipelines. Where Pattern Categories 1–7 cover one-shot training-corpus poisoning and Pattern Category 8 covers transfer-learning weight-artifact compromise, this category targets the **specific architectural-tell** of a production inference path that loops back into retraining without integrity gates: production predictions and user clickstream are reused as training signal without tamper-detection on the loopback data, and HITL labeling tools accept label flips without labeler-trust scoring or reputation weighting. The attacker's goal is gradual model drift toward attacker-favorable outcomes (recommendation hijacking, fraud-classifier skew, content-moderation evasion via label flooding) rather than a single backdoor injection.

**Indicators**:

- DFD element exposes an active-learning pipeline that reads production inference data back into training without integrity controls (no anomaly detection on label distribution drift, no held-out canary set comparison)
- HITL labeling tool accepts labels from crowd-sourced or user-facing labelers without labeler-trust scoring, reputation-based weighting, or redundancy/consensus requirement — label-flipping attack surface
- Online-learning model continuously updates from inference inputs without input-space outlier detection — drift injection feasible by attacker submitting crafted feature distributions at scale
- Recommendation system reuses clickstream data for retraining without tamper-detection on clickstream events (no bot-detection / coordinated-inauthentic-behavior gate before clickstream feeds the training set)
- Drift-detection alarms are missing on production inference distributions — model skew would not be detected until downstream business metrics degrade weeks or months later

**Primary source**:

- OWASP ML08:2023 — Model Skewing: https://owasp.org/www-project-machine-learning-security-top-10/docs/ML08_2023-Model_Skewing
- MITRE ATLAS AML.T0020 — Poison Training Data: https://atlas.mitre.org/techniques/AML.T0020

**Example**: A content-recommendation platform retrains its ranking model nightly from the previous day's clickstream events. The retraining pipeline reads `(user_id, item_id, click, dwell_time)` tuples from a Kafka topic without bot-detection on the originating user accounts and without anomaly detection on click-distribution drift. An attacker operates a bot network that systematically clicks and dwells on items associated with a target product category, generating fabricated engagement signal at scale. Over the course of two weeks, the recommendation model drifts toward over-recommending the target category to organic users (attacker-favorable skew). The drift survives held-out evaluation because the held-out set is sampled from the same contaminated clickstream; no canary set anchored to a clean baseline is in place. Business KPIs (click-through rate on the target category) appear to improve, masking the skew until a content-quality complaint surfaces six weeks later.

**Mitigation**:

- Install feedback-data integrity gates with anomaly detection on label distribution drift: compare incoming labeled batches against a clean held-out canary set before each retraining cycle, and reject batches whose label distribution diverges beyond a calibrated threshold
- Apply labeler-trust scoring with reputation-based weighting in HITL labeling tools: weight label contributions by historical accuracy on gold-standard examples, require multi-labeler consensus on safety-critical samples, and quarantine new labelers below a reputation floor
- Run periodic retraining-data audit with held-out canaries: maintain a clean baseline test set anchored outside the loopback path and verify retrained models maintain accuracy on it; failures block promotion
- Add drift-detection alarms on production inference distributions (KS statistic / population stability index / KL divergence on per-feature distributions, with paging thresholds tuned to baseline drift rate)
- Cf. MITRE ATLAS AML.T0031 (Erode ML Model Integrity) — text-only cross-reference (NOT in references; T0031 not catalog-resolvable in `schemas/taxonomy/mitre-atlas.yaml`)

## Pattern Category 10: Predictive-ML Supply Chain Completeness (Datasets, Feature Stores, MLOps Registry) (OWASP ML06:2023)

OWASP ML06:2023 (AI Supply Chain Attacks) names supply-chain integrity gaps across the predictive-ML training pipeline as a distinct attack class spanning dataset repositories, feature stores, and MLOps model registries. This category captures the **corpus-side facet** of ML06:2023 per ADR-035 D-4 disjoint architectural-tells: the training-corpus, feature-store, and model-registry promotion-gate surface. The **artifact-side facet** of ML06:2023 (model registry serving weight artifacts at inference time, weight-tampering between training and serving) is owned by `tachi-model-theft` Pattern Category 14 (predictive-ML artifact supply chain). Same architecture may surface both Cat 10 (D) corpus-side findings and Cat 14 (LLM) artifact-side findings without duplication — they are distinct architectural-tells with disjoint mitigation vocabularies. The architectural-tell for Cat 10 is the training-pipeline ingestion path: a dataset repository (Kaggle / public corpus / S3-backed dataset lake), a feature store (Feast / Tecton / S3-backed), or an MLOps model registry (MLflow / SageMaker / Vertex AI) participating in the corpus-to-training data path without integrity verification, IAM-enforced write-audit, signed-artifact promotion policy, or dataset-checksum manifest.

**Indicators**:

- DFD element ingests training data from a dataset repository (Kaggle, public corpus, S3-backed dataset lake) without integrity verification (no checksum manifest, no SHA-256 digest comparison, no provenance attestation)
- Feature store (Feast, Tecton, S3-backed feature tables) is exposed for write without IAM-enforced write-audit — multiple roles or service accounts can mutate feature values without audit trail or promotion-gate review
- MLOps model registry (MLflow, SageMaker Model Registry, Vertex AI Model Registry) promotes models from staging to production without signed-artifact policy — promotion gate is missing pull-request review or cryptographic attestation requirement
- Model-card or datasheet metadata is missing on training datasets or registered models — provenance information (data source, collection methodology, known biases, evaluation harness) is not published alongside the artifact
- Dataset-checksum manifest is absent — the training pipeline cannot reproduce a known-good corpus snapshot, and no audit log records which dataset version produced which trained model

**Primary source**:

- OWASP ML06:2023 — AI Supply Chain Attacks: https://owasp.org/www-project-machine-learning-security-top-10/docs/ML06_2023-AI_Supply_Chain_Attacks
- MITRE ATT&CK T1195 — Supply Chain Compromise: https://attack.mitre.org/techniques/T1195/
- MITRE ATT&CK T1195.001 — Compromise Software Dependencies and Development Tools: https://attack.mitre.org/techniques/T1195/001/
- MITRE ATT&CK T1195.002 — Compromise Software Supply Chain: https://attack.mitre.org/techniques/T1195/002/

**Example**: A predictive-ML team trains a fraud-detection classifier from a corpus assembled by stitching together a public Kaggle fraud-detection dataset, an internal transaction history table queried from a Feast feature store, and a third-party labeled-fraud dataset pulled from a vendor S3 bucket. The training pipeline pulls the Kaggle dataset by URL without a checksum manifest. The Feast feature store accepts writes from any service account in the team's IAM group without per-write audit logging. The MLflow model registry accepts promotion from staging to production via a single API call with no signed-artifact policy and no pull-request review. An attacker who compromises any one of these three surfaces — by publishing a poisoned-update of the Kaggle dataset, mutating a feature-store feature value, or promoting a backdoored model artifact through the MLflow staging-to-production gate — can inject biased or backdoored training signal into the production fraud-detection classifier. No single integrity check across the three surfaces would have caught the compromise.

**Mitigation**:

- Enforce a signed-artifact policy at the MLOps registry boundary: require Sigstore-style or KMS-backed cryptographic attestation on every model promoted from staging to production, and reject promotion requests lacking attestation
- Apply IAM-enforced write-audit on feature stores: log every feature-value mutation with actor identity, before/after values, and timestamp; require pull-request review for write-access grants on production feature tables; alert on anomalous write volume from a single service account
- Maintain a dataset-checksum manifest with reproducibility verification: every training run records the SHA-256 digest of every input corpus, the manifest is committed to version control, and CI verifies digest match on every retraining cycle
- Require model-card review as a promotion gate: every model entering production must have an accompanying model card describing training data provenance, evaluation harness, known biases, and intended deployment scope; the team signs off on the model card before promotion

## Pattern Category Disambiguation

Pattern Categories 8, 9, and 10 (Predictive ML training-pipeline supply-chain surfaces — F-6) and the pre-existing Pattern Categories 1–7 (LLM/RAG-tier corpus, index, fine-tuning, and feedback-loop poisoning) share the OWASP LLM04:2025 / OWASP ML06–08:2023 family at the OWASP framework level but address distinct architectural-tells and mitigation surfaces:

- **Pattern Categories 1–4** (Training Data Manipulation, RAG Index Poisoning, Knowledge Base Corruption, Fine-Tuning Supply Chain Attacks — pre-existing LLM/RAG-tier) detect corpus and index integrity gaps where the architectural-tell is an LLM training corpus, a RAG vector store, or an LLM fine-tuning pipeline. Mitigation vocabulary is corpus-validation / RAG-provenance / LLM-fine-tune-attestation focused.
- **Pattern Category 5** (Context Window Contamination — pre-existing) detects runtime context-window manipulation at the LLM inference path.
- **Pattern Categories 6–7** (RAG/Vector Store Poisoning at Retrieval Time, Backdoor Triggers in Training and Fine-Tuning Data — pre-existing) detect retrieval-time vector-store poisoning and trigger-based backdoor injection on LLM-tier training and retrieval surfaces. Architectural-tells: shared/multi-tenant vector store, LLM-tier RLHF pipeline, third-party LLM weight artifact.
- **Pattern Category 8** (Transfer Learning Supply Chain, Predictive ML — F-6) detects pretrained-weight and adapter compromise at the predictive-ML fine-tuning surface. Architectural-tell: fine-tuning step on a non-LLM classifier or regressor pulling base weights from a public ML model registry without checksum verification or signed-artifact policy.
- **Pattern Category 9** (Feedback-Loop Model Skewing, Active Learning / Online Learning — F-6) detects loopback contamination of production inference data feeding retraining. Architectural-tell: active-learning, online-learning, or recommendation-system retraining path without integrity gates on the loopback data.
- **Pattern Category 10** (Predictive-ML Supply Chain Completeness, Datasets / Feature Stores / MLOps Registry — F-6) detects corpus-side supply-chain integrity gaps across dataset repositories, feature stores, and MLOps model registries on the **corpus-to-training data path** (ML06 corpus-side facet per ADR-035 D-4). Architectural-tells: dataset-repo without checksum manifest, feature-store without IAM-enforced write-audit, MLOps registry without signed-artifact promotion policy.

Same architecture may legitimately surface findings across Pattern Categories 1–7 (LLM/RAG-tier) **and** Pattern Categories 8–10 (predictive-ML-tier) when it operates both an LLM/RAG application surface and a predictive-ML training pipeline. They are not duplicates and MUST NOT be merged in `threat-report.md`.

Same architecture may also surface Pattern Category 10 (D — corpus-side ML06) **and** model-theft Pattern Category 14 (LLM — artifact-side ML06) when it has both a training-corpus / feature-store / MLOps-registry promotion-gate surface and a model-registry / weight-artifact-storage / serving-time integrity surface. The two facets of ML06:2023 are disjoint by architectural-tell per ADR-035 D-4 — Cat 10 (D) owns the corpus-side facet (training-pipeline integrity); Cat 14 (LLM) owns the artifact-side facet (serving-time integrity). Architect formalizes this carve in ADR-035 Decisions D-4 (ML06 two-facet disjoint architectural-tells) and D-9 (Pattern Category Disambiguation requirement on three F-6 companions per FR-011).

## Primary Sources

- **OWASP LLM03:2025 - Supply Chain**: https://genai.owasp.org/llmrisk/llm032025-supply-chain/
- **OWASP LLM04:2025 - Data and Model Poisoning**: https://genai.owasp.org/llmrisk/llm04-data-and-model-poisoning/
- **OWASP LLM08:2025 - Vector and Embedding Weaknesses**: https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/
- **MITRE ATLAS AML.T0020 - Poison Training Data**: https://atlas.mitre.org/techniques/AML.T0020
- **MITRE ATLAS AML.T0018 - Backdoor ML Model**: https://atlas.mitre.org/techniques/AML.T0018
- **MITRE ATLAS AML.T0010 - ML Supply Chain Compromise**: https://atlas.mitre.org/techniques/AML.T0010
- **CWE-345 - Insufficient Verification of Data Authenticity**: https://cwe.mitre.org/data/definitions/345.html
- **CWE-1395 - Dependency on Vulnerable Third-Party Component**: https://cwe.mitre.org/data/definitions/1395.html
- **Carlini et al., 2023**: "Poisoning Web-Scale Training Datasets is Practical" — demonstrates feasibility of training-data poisoning at scale
- **OWASP ML06:2023 - AI Supply Chain Attacks**: https://owasp.org/www-project-machine-learning-security-top-10/docs/ML06_2023-AI_Supply_Chain_Attacks
- **OWASP ML07:2023 - Transfer Learning Attack**: https://owasp.org/www-project-machine-learning-security-top-10/docs/ML07_2023-Transfer_Learning_Attack
- **OWASP ML08:2023 - Model Skewing**: https://owasp.org/www-project-machine-learning-security-top-10/docs/ML08_2023-Model_Skewing
- **MITRE ATT&CK T1195 - Supply Chain Compromise**: https://attack.mitre.org/techniques/T1195/
- **MITRE ATT&CK T1195.001 - Compromise Software Dependencies and Development Tools**: https://attack.mitre.org/techniques/T1195/001/
- **MITRE ATT&CK T1195.002 - Compromise Software Supply Chain**: https://attack.mitre.org/techniques/T1195/002/
