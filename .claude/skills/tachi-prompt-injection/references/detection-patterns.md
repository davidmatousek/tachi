---
name: prompt-injection-detection-patterns
description: Externalized detection pattern catalog for AI prompt injection — direct, indirect, jailbreak, system prompt leakage, delimiter confusion
consumers: [tachi-prompt-injection]
last_updated: 2026-04-11
---

# Prompt Injection Detection Patterns

## Overview

Detection vocabulary for LLM prompt injection threats. Loaded at detection start by `tachi-prompt-injection` agent via a single `**MANDATORY**: Read` directive.

## Detection Scope

### Trigger Keywords

This agent activates when a DFD element name or description matches any of the following patterns (case-insensitive):

- `LLM`
- `model`
- `GPT`
- `Claude`
- `language model`
- `completion`
- `chat`
- `inference`
- `prompt`
- `generative AI`

### Applicable DFD Element Types

- **Process**: Any process node that invokes, wraps, or orchestrates an LLM. This includes API gateway processes that forward prompts, orchestration layers that compose multi-step LLM calls, and application logic that interpolates user input into prompt templates.

## Detection Patterns

1. **Direct Prompt Injection**: User-facing input fields whose contents are concatenated into LLM prompts without sanitization, boundary enforcement, or input classification. Look for:
   - Chat interfaces that pass raw user text to model APIs
   - Search bars or form fields whose values are interpolated into system prompts
   - API endpoints that accept freeform text and forward it to LLM completions
   - Absence of input validation or prompt boundary markers between system instructions and user content

2. **Indirect Prompt Injection**: Data flows where external or semi-trusted content is retrieved and injected into the model context window. Look for:
   - RAG pipelines that retrieve documents from user-contributed or web-scraped sources
   - Email or message processing where attacker-controlled content enters the prompt
   - Database records, CMS content, or API responses that are embedded in LLM context
   - Tool outputs that are fed back into the model without sanitization

3. **Jailbreaking**: Systematic prompt structures designed to override safety alignment or system instructions. Look for:
   - Absence of output filtering or safety classifiers on model responses
   - System prompts that lack resistance to role-play or persona-switching attacks
   - Missing rate limiting on prompt attempts (enables iterative jailbreak refinement)
   - No monitoring or logging of prompt patterns that match known jailbreak taxonomies

4. **System Prompt Extraction**: Attempts to trick the model into revealing its system prompt or internal instructions. Look for:
   - System prompts containing sensitive business logic, API keys, or internal URLs
   - No output filtering for content that resembles system prompt leakage
   - Absence of prompt-level guardrails that refuse meta-instruction queries

5. **Cross-Plugin Injection**: Adversarial prompts that exploit multi-plugin or multi-tool LLM architectures to pivot between plugins, escalate privileges, or exfiltrate data across trust boundaries. Look for:
   - LLM orchestrators that invoke multiple plugins/tools where one plugin's output feeds another plugin's input without sanitization
   - Absence of trust boundary enforcement between plugins operating at different privilege levels
   - Plugin architectures where a compromised or attacker-controlled plugin can influence the prompts sent to other plugins
   - Missing input validation on cross-plugin data flows (e.g., Plugin A returns text that is interpolated into Plugin B's prompt)
   - No isolation between plugin execution contexts, allowing shared state manipulation

## Primary Sources

- **OWASP LLM01:2025 - Prompt Injection**: https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- **OWASP LLM07:2025 - System Prompt Leakage**: https://genai.owasp.org/llmrisk/llm07-system-prompt-leakage/
- **MITRE ATLAS - LLM Prompt Injection**: Tactic TA0043, Technique AML.T0051
- **CWE-77 - Improper Neutralization of Special Elements used in a Command**: Conceptual analog for prompt injection in LLM contexts
- **Greshake et al., 2023**: "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection"
