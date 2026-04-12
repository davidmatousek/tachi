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
