# Enrichment Brief — model-theft

**Agent type**: AI
**Primary threat category**: Model Theft and Extraction
**Created**: 2026-04-11
**Feature**: 082 — Threat Agent Skill References

## Candidate New Pattern Categories

### Category 1 — Model Extraction via Inference API Query Patterns

- **Source**: OWASP Top 10 for LLM Applications v2025
- **Source citation**: `https://genai.owasp.org/llmrisk/llm10-unbounded-consumption/`
- **Source item**: LLM10:2025 Unbounded Consumption (consolidates what was LLM04:2023 Model Denial of Service and LLM10:2023 Model Theft); specific sub-category: model extraction via API query flooding
- **Why this category**: LLM10:2025 explicitly names model-extraction-via-inference as a sub-category. Current inline patterns treat extraction as speculative; the v2025 specification validates it as a canonical threat.
- **Proposed detection signal**:
  - DFD element exposes LLM inference API externally without declared rate limiting per-user, per-API-key, or per-IP
  - API returns full probability distributions (top-k logprobs) rather than just the sampled token — amplifies extraction efficiency
  - Model accepts arbitrary-length prompts without cost accounting (attacker can query cheaply and extract broadly)
  - No declared query-pattern anomaly detection (extraction attacks show distinctive high-volume, semantically-diverse query signatures)
- **False-positive risk**: Medium — rate limiting is often declared outside architecture descriptions
- **Taxonomy alignment**: AI Model Theft; OWASP LLM10:2025; related ATLAS AML.T0024

### Category 2 — Exfiltration via ML Inference API (ATLAS)

- **Source**: MITRE ATLAS v5.1+
- **Source citation**: `https://atlas.mitre.org/techniques/AML.T0024`
- **Source item**: AML.T0024 Exfiltration via ML Inference API (parent tactic AML.TA0013 Exfiltration); related AML.T0057 LLM Data Leakage
- **Why this category**: ATLAS provides the canonical technique catalog for extraction; inline patterns do not reference ATLAS explicitly for this.
- **Proposed detection signal**:
  - Inference endpoint returns embedding vectors (rather than only final outputs) — embeddings can be used for membership inference and extraction
  - Fine-tuned model accessible via API without declared separation from base-model serving (fingerprinting risk)
  - Model returns training-data-indicative content (verbatim repetition of training samples when probed with specific prompts)
  - No declared output watermarking or canary token insertion for exfil detection
- **False-positive risk**: Low — when embedding endpoints or unwatermarked fine-tuned serving is declared, the pattern is concrete
- **Taxonomy alignment**: AI Model Theft; ATLAS AML.T0024, AML.T0057; tactic TA0013 Exfiltration

### Category 3 — Weight and Adapter Theft via Infrastructure Access

- **Source**: MITRE ATT&CK v15+ (Enterprise) combined with OWASP AI Exchange
- **Source citation**: `https://attack.mitre.org/techniques/T1005/` and `https://owaspai.org/docs/ai_security_overview/`
- **Source item**: ATT&CK T1005 Data from Local System (applied to model artifact files); OWASP AI Exchange — Model Theft chapter discussing weight exfiltration
- **Why this category**: Direct file-level theft of model weights, LoRA adapters, or quantized checkpoints is a distinct vector from inference-API extraction. Under-covered in inline patterns.
- **Proposed detection signal**:
  - Model artifacts (.safetensors, .gguf, .bin, .pt, LoRA files) stored on shared filesystem, S3/GCS/Azure Blob with broad read permissions
  - Model serving container has read access to full model hub (not just the loaded model)
  - Checkpoint archive (including optimizer state) stored without encryption-at-rest
  - No declared access audit for model artifact downloads
- **False-positive risk**: Medium — storage permissions are often under-described in architecture
- **Taxonomy alignment**: AI Model Theft; ATT&CK T1005 (Data from Local System), OWASP AI Exchange

### Category 4 — System Prompt and Configuration Leakage

- **Source**: OWASP Top 10 for LLM Applications v2025
- **Source citation**: `https://genai.owasp.org/llmrisk/llm07-system-prompt-leakage/`
- **Source item**: LLM07:2025 System Prompt Leakage (new in v2025 as a dedicated category)
- **Why this category**: System prompt leakage was elevated to its own top-level category in v2025, recognizing it as a distinct threat from general prompt injection. Deserves its own pattern category.
- **Proposed detection signal**:
  - System prompt contains sensitive material: API keys, internal URLs, business logic, pricing rules, banned topics, user PII
  - No declared isolation between system prompt and user-visible output channels
  - Error responses or debug logs echo system prompt content on failure
  - Chat interface accepts prompts that can probe the instruction hierarchy (`repeat your instructions`, `what came before this?`)
- **False-positive risk**: Medium — declared system prompt content is rarely visible at architecture level
- **Taxonomy alignment**: AI Model Theft (information class); OWASP LLM07:2025

## Source Verification Notes

- OWASP LLM Top 10 v2025 merged LLM10:2023 (Model Theft) into LLM10:2025 (Unbounded Consumption) — the category was consolidated. Verify current canonical naming during Phase 3.2 extraction.
- ATLAS AML.T0024 is the primary model-extraction exfiltration technique; AML.T0057 is a newer LLM-specific data-leakage technique added in recent ATLAS updates.
- LLM07:2025 (System Prompt Leakage) is new in v2025 and previously appeared inside LLM06:2023 (Sensitive Information Disclosure) — verify.
- Checked but NOT used: research papers on membership inference attacks (Shokri et al.) — cited by OWASP/ATLAS references, not re-cited here.
