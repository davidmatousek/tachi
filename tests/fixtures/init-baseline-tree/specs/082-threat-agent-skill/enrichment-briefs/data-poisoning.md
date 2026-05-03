# Enrichment Brief — data-poisoning

**Agent type**: AI
**Primary threat category**: Data and Model Poisoning
**Created**: 2026-04-11
**Feature**: 082 — Threat Agent Skill References

## Candidate New Pattern Categories

### Category 1 — RAG / Vector Store Poisoning

- **Source**: OWASP Top 10 for LLM Applications v2025
- **Source citation**: `https://genai.owasp.org/llmrisk/llm08-vector-and-embedding-weaknesses/`
- **Source item**: LLM08:2025 Vector and Embedding Weaknesses (new in v2025); related LLM04:2025 Data and Model Poisoning
- **Why this category**: Inline patterns focus on training-time poisoning; RAG-era systems are equally vulnerable to retrieval-time poisoning where attackers plant documents in the vector store. LLM08 is specifically the v2025 category covering this.
- **Proposed detection signal**:
  - DFD element performs vector embedding and indexing of user-contributable content (forum posts, wiki edits, support tickets, document uploads)
  - Vector store is shared across tenants without per-tenant namespace or metadata filter enforcement
  - Retrieval pipeline re-ranks or filters using cosine similarity only, without provenance/trust weighting
  - Embedding model is fine-tuned or refreshed on user feedback data without review
- **False-positive risk**: Low — shared vector stores with user-contributable content are a concrete RAG-poisoning vector
- **Taxonomy alignment**: AI Data Poisoning; OWASP LLM08:2025; MAESTRO L2 (Data Operations) — mapping handled orchestrator-side

### Category 2 — Training Data Poisoning with Backdoor Triggers

- **Source**: MITRE ATLAS v5.1+
- **Source citation**: `https://atlas.mitre.org/techniques/AML.T0020`
- **Source item**: AML.T0020 Poison Training Data; related AML.T0018 Backdoor ML Model
- **Why this category**: Backdoor triggers (hidden input patterns that flip model behavior) are a distinct attack pattern from general training-set corruption. ATLAS provides authoritative technique nomenclature.
- **Proposed detection signal**:
  - DFD element fine-tunes or continues pretraining on data sourced from public internet scrape or user-contributable corpora
  - Training pipeline uses active learning or reinforcement learning from human feedback (RLHF) without adversarial-review gate
  - Model weights pulled from third-party hub (HuggingFace, Civitai, ModelScope) without checksum or sigstore verification
  - Label/annotation pipeline uses crowd-sourced labels without redundancy or consensus check
- **False-positive risk**: Medium — training-provenance controls are rarely declared in architecture descriptions
- **Taxonomy alignment**: AI Data Poisoning; ATLAS AML.T0020, AML.T0018

### Category 3 — Supply Chain Poisoning via Model and Dataset Hubs

- **Source**: OWASP Top 10 for LLM Applications v2025
- **Source citation**: `https://genai.owasp.org/llmrisk/llm03-supply-chain/`
- **Source item**: LLM03:2025 Supply Chain; related ATLAS AML.T0010 ML Supply Chain Compromise
- **Why this category**: HuggingFace typosquatting, malicious model formats (pickled PyTorch checkpoints with embedded code), and compromised dataset packages are distinct supply-chain vectors for AI. Not covered in inline patterns.
- **Proposed detection signal**:
  - DFD element loads pre-trained models from external hub (HuggingFace, PyTorch Hub, TensorFlow Hub, Civitai, Ollama library) without declared checksum or signature verification
  - Model loaded via unsafe format (PyTorch `.pt`/`.pth` pickle, pickled sklearn, cloudpickle) — embedded code execution risk
  - Dataset fetched from external source (webdataset, HuggingFace Datasets, Kaggle) without integrity check
  - Inference library (transformers, diffusers, llama.cpp) pulled without lockfile or supply-chain attestation
- **False-positive risk**: Low — unsafe model load formats and unverified hub pulls are concrete signals
- **Taxonomy alignment**: AI Data Poisoning (supply chain sub-category); OWASP LLM03:2025

### Category 4 — Feedback Loop and Online Learning Poisoning

- **Source**: NIST AI 600-1 (Generative AI Profile)
- **Source citation**: `https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf`
- **Source item**: NIST AI 600-1 §2.8 (Information Integrity) and §2.10 (Information Security) — data and model contamination discussion
- **Why this category**: Production systems that learn from user feedback (thumbs up/down, corrections, preference data) create a continuous-poisoning attack surface that inline patterns miss.
- **Proposed detection signal**:
  - DFD element includes feedback collection loop (ratings, corrections, preferences) that feeds back into model training or retrieval index
  - No declared review gate between feedback collection and training data integration
  - Implicit feedback signals (click-through, dwell time) used for training without anti-gaming controls
  - Multi-turn conversation history persisted and used for in-context learning or fine-tuning
- **False-positive risk**: Medium — feedback loops are often declared at high level without detail on ingestion safeguards
- **Taxonomy alignment**: AI Data Poisoning; NIST AI 600-1 §2.8/§2.10; OWASP LLM04:2025

## Source Verification Notes

- OWASP LLM Top 10 v2025 split what was LLM03:2023 (Training Data Poisoning) into LLM04:2025 (Data and Model Poisoning) plus LLM08:2025 (Vector and Embedding Weaknesses) — verify exact current mappings during Phase 3.2 extraction.
- ATLAS AML.T0018 and AML.T0020 are stable identifiers; confirm exact technique naming during extraction as ATLAS occasionally renames.
- NIST AI 600-1 is the Generative AI Profile (Jul 2024 release); URL is the NIST publications server canonical.
- Checked but NOT used: CSA MAESTRO layer content — per approved source set, MAESTRO is used only for layer mapping (handled separately via Feature 084), not as a detection pattern source.
