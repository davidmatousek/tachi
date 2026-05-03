# Enrichment Brief — prompt-injection

**Agent type**: AI
**Primary threat category**: Prompt Injection (LLM Input Manipulation)
**Created**: 2026-04-11
**Feature**: 082 — Threat Agent Skill References

## Candidate New Pattern Categories

### Category 1 — Indirect Prompt Injection via Retrieved or Rendered Content

- **Source**: OWASP Top 10 for LLM Applications v2025
- **Source citation**: `https://genai.owasp.org/llmrisk/llm01-prompt-injection/`
- **Source item**: LLM01:2025 Prompt Injection — specifically the indirect injection sub-category
- **Why this category**: Indirect injection (poisoned documents, webpages, PDFs, emails, images with hidden text) is structurally different from direct injection but is under-covered in current inline patterns that focus on chatbot-style direct user input.
- **Proposed detection signal**:
  - DFD element retrieves content from untrusted sources (web scraping, document upload, RSS, email ingestion) and passes it to an LLM context
  - RAG pipeline pulls from external or user-contributable document store (wiki, ticketing system, shared drive)
  - LLM processes multimodal content (images, audio, PDF) without content-extraction isolation
  - Agent consumes tool-response data and re-injects it into its own prompt
- **False-positive risk**: Low — retrieval from untrusted content into an LLM context is a concrete high-severity signal
- **Taxonomy alignment**: AI Prompt Injection; OWASP LLM01:2025; MAESTRO L2 (Data Operations) — mapping handled orchestrator-side per Feature 084

### Category 2 — Jailbreak and System Prompt Bypass Patterns

- **Source**: MITRE ATLAS v5.1+
- **Source citation**: `https://atlas.mitre.org/techniques/AML.T0051`
- **Source item**: AML.T0051 LLM Prompt Injection; related AML.T0054 LLM Jailbreak
- **Why this category**: Jailbreak via role-play, DAN (Do Anything Now) prompts, instruction hierarchy bypass, and prompt leakage are distinct patterns that deserve explicit categorization separate from general prompt injection.
- **Proposed detection signal**:
  - Component declares a system prompt that contains sensitive policies, API keys, or business logic (high value for prompt leakage)
  - No declared instruction-hierarchy enforcement (OpenAI's `system` vs `user` role distinction or equivalent)
  - User input passes through without encoding/escape of known jailbreak delimiters (`### End of system prompt ###`, XML-tag spoofing, markdown injection)
  - Conversation history persists across privilege transitions without reset
- **False-positive risk**: Medium — jailbreak defenses are rarely declared explicitly in architecture descriptions
- **Taxonomy alignment**: AI Prompt Injection; ATLAS AML.T0051, AML.T0054

### Category 3 — Evasion via Encoding and Obfuscation

- **Source**: OWASP AI Exchange
- **Source citation**: `https://owaspai.org/docs/ai_security_overview/`
- **Source item**: OWASP AI Exchange — Input Validation section; Adversarial Evasion discussion
- **Why this category**: Encoding-based evasion (Base64, ROT13, Unicode homoglyphs, zero-width characters, invisible text) bypasses simple keyword filtering and is growing as a pattern. Not present in inline patterns.
- **Proposed detection signal**:
  - Input-filtering component uses substring or keyword matching without normalization (Unicode NFKC, whitespace collapse, case fold)
  - No declared Base64/hex/URL-encoded input detection before LLM forwarding
  - LLM accepts multilingual or low-resource-language input without consistent policy enforcement (safety training coverage gap)
  - Multimodal input path (image with embedded text, audio with spoken instructions) bypasses text-only content filtering
- **False-positive risk**: Medium — encoding-detection is rarely declared
- **Taxonomy alignment**: AI Prompt Injection; OWASP AI Exchange; CSA MAESTRO L3 (Agent Frameworks) — mapping handled orchestrator-side

## Source Verification Notes

- OWASP LLM Top 10 v2025 is the 2025-published edition (succeeding v1.1 from 2023). LLM01:2025 consolidates direct and indirect injection under a single top-level category.
- ATLAS AML.T0051 and AML.T0054 are distinct techniques in the ATLAS catalog (v5.1+); verify exact current technique numbering during Phase 3.2 extraction since ATLAS re-numbers occasionally.
- OWASP AI Exchange URL `https://owaspai.org/` is the canonical project homepage; specific section URLs stabilize but section structure evolves.
- Checked but NOT used: NIST AI 600-1 — provides governance framing but lacks specific detection signatures for prompt injection; reference-only.
- Checked but NOT used: Academic papers on prompt injection (Greshake et al., Perez et al.) — cited within OWASP LLM references, not re-cited here to keep sources canonical.
