---
name: tachi-prompt-injection
description: "Detects prompt injection vulnerabilities in LLM-integrated components, including direct injection, indirect injection via RAG pipelines, jailbreaking, system prompt extraction, and cross-plugin injection attacks."
---

## Metadata

```yaml
category: llm
threat_class: LLM
dfd_targets: [Process]
owasp_references: [OWASP LLM01:2025, OWASP LLM07:2025]
output_schema: ../../../schemas/finding.yaml
```

# Prompt Injection Threat Agent

## Purpose

Detects prompt injection vulnerabilities in LLM-integrated components. Prompt injection is the most prevalent and highest-impact threat class for LLM applications: an attacker manipulates model behavior by embedding adversarial instructions in user input, retrieved context, or upstream data sources. This agent identifies direct injection (user-supplied malicious prompts), indirect injection (adversarial payloads embedded in data the model consumes), and jailbreaking (systematic attempts to override model safety constraints).

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

### Detection Patterns

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

### Empty Results Guidance

When the architecture input contains no LLM, language model, or generative AI components (i.e., no DFD elements match any trigger keyword in the Detection Scope), this agent MUST produce zero findings. Do not generate speculative or hypothetical prompt injection findings for architectures that do not include LLM-integrated components.

## Finding Template

```yaml
id: "LLM-{N}"
category: llm
component: "{component name from architecture input}"
threat: "{specific prompt injection threat description}"
likelihood: "{LOW | MEDIUM | HIGH}"
impact: "{LOW | MEDIUM | HIGH}"
risk_level: "{computed from OWASP 3x3 matrix}"
mitigation: "{recommended countermeasure}"
references:
  - "OWASP LLM01:2025"
dfd_element_type: "Process"
```

### Example Findings

**Direct Injection via Chat Interface**:

```yaml
id: "LLM-1"
category: llm
component: "Customer Support Chatbot"
threat: "User-supplied chat messages are concatenated directly into the LLM prompt without input sanitization or boundary enforcement. An attacker can inject instructions that override the system prompt, causing the model to ignore safety constraints, disclose internal instructions, or produce harmful content."
likelihood: HIGH
impact: HIGH
risk_level: Critical
mitigation: "Implement structured prompt templates with explicit delimiter tokens between system instructions and user input. Add an input classifier that detects adversarial prompt patterns before forwarding to the model. Apply output filtering to detect responses that violate expected behavior boundaries."
references:
  - "OWASP LLM01:2025"
  - "CWE-77"
dfd_element_type: "Process"
```

**Indirect Injection via RAG Pipeline**:

```yaml
id: "LLM-2"
category: llm
component: "Document Q&A Service"
threat: "The RAG pipeline retrieves documents from a shared knowledge base where internal users can upload content. An attacker with upload access can embed adversarial instructions in a document that, when retrieved and injected into the LLM context, overrides system behavior — exfiltrating data from other retrieved documents or generating misleading answers."
likelihood: MEDIUM
impact: HIGH
risk_level: High
mitigation: "Sanitize retrieved document content before injection into the prompt context. Implement provenance tracking so the model can distinguish system instructions from retrieved content. Apply content integrity checks on uploaded documents and monitor for embedded instruction patterns."
references:
  - "OWASP LLM01:2025"
dfd_element_type: "Process"
```

**Jailbreak via Iterative Probing**:

```yaml
id: "LLM-3"
category: llm
component: "Content Generation API"
threat: "The model API lacks rate limiting on prompt submissions and does not log prompt patterns. An attacker can iteratively probe the model with jailbreak prompt variations (role-play injection, few-shot override, instruction hierarchy manipulation) until safety alignment is bypassed, enabling generation of policy-violating content."
likelihood: MEDIUM
impact: MEDIUM
risk_level: Medium
mitigation: "Implement rate limiting on prompt submissions per user session. Deploy a prompt classifier that flags known jailbreak patterns (role-play requests, 'ignore previous instructions' variants, DAN-style prompts). Log all prompts for post-hoc analysis and establish alerting on anomalous prompt pattern clusters."
references:
  - "OWASP LLM01:2025"
dfd_element_type: "Process"
```

### Risk Level Computation

Apply the OWASP 3x3 matrix to determine `risk_level` from `likelihood` and `impact`:

|  | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

## References

- **OWASP LLM01:2025 - Prompt Injection**: https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- **OWASP LLM07:2025 - System Prompt Leakage**: https://genai.owasp.org/llmrisk/llm07-system-prompt-leakage/
- **MITRE ATLAS - LLM Prompt Injection**: Tactic TA0043, Technique AML.T0051
- **CWE-77 - Improper Neutralization of Special Elements used in a Command**: Conceptual analog for prompt injection in LLM contexts
- **Greshake et al., 2023**: "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection"
