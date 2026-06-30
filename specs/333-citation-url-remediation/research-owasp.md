# Research: OWASP GenAI Citation URL Remediation (F-333)

## Objective

Adjudicate the OWASP GenAI (`genai.owasp.org`) citation dead-set across `schemas/taxonomy/owasp.yaml` and `schemas/taxonomy/crosswalk.yaml`, identifying which URLs are dead and their restructured canonical forms.

## Methodology

Probed each distinct URL from both catalog files with HTTP HEAD requests to determine status. Used curl to follow redirects and identify canonical forms. References OWASP GenAI Security Project documentation from genai.owasp.org.

## Findings Table

| Distinct URL | Observed Status | Restructured Canonical | Notes |
|---|---|---|---|
| https://genai.owasp.org/llmrisk/llm01-prompt-injection | 301 → LIVE | `https://genai.owasp.org/llmrisk/llm01-prompt-injection/` | Regression guard; CONFIRMED LIVE; redirect to trailing slash, 200 OK |
| https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure | 301 → LIVE | `https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/` | 2025 variant form; 200 OK after trailing slash |
| https://genai.owasp.org/llmrisk/llm032025-supply-chain | 301 → LIVE | `https://genai.owasp.org/llmrisk/llm032025-supply-chain/` | 2025 variant form; 200 OK after trailing slash |
| https://genai.owasp.org/llmrisk/llm042025-data-and-model-poisoning | 301 → LIVE | `https://genai.owasp.org/llmrisk/llm042025-data-and-model-poisoning/` | 2025 variant form; 200 OK after trailing slash |
| https://genai.owasp.org/llmrisk/llm052025-improper-output-handling | 301 → LIVE | `https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/` | 2025 variant form; 200 OK after trailing slash |
| https://genai.owasp.org/llmrisk/llm062025-excessive-agency | 301 → LIVE | `https://genai.owasp.org/llmrisk/llm062025-excessive-agency/` | 2025 variant form; 200 OK after trailing slash |
| https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage | 301 → LIVE | `https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/` | 2025 variant form; 200 OK after trailing slash |
| https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses | 301 → LIVE | `https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/` | 2025 variant form; 200 OK after trailing slash |
| https://genai.owasp.org/llmrisk/llm092025-misinformation | 301 → LIVE | `https://genai.owasp.org/llmrisk/llm092025-misinformation/` | 2025 variant form; 200 OK after trailing slash |
| https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption | 301 → LIVE | `https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/` | 2025 variant form; 200 OK after trailing slash |
| https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026 | 301 → LIVE | `https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/` | Agentic resource; 200 OK after trailing slash |
| https://genai.owasp.org/llmrisk/llm02-sensitive-information-disclosure | **404 DEAD** | `https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/` | Non-year variant; no redirect; use 2025-year form instead |
| https://genai.owasp.org/llmrisk/llm03-supply-chain | **404 DEAD** | `https://genai.owasp.org/llmrisk/llm032025-supply-chain/` | Non-year variant; no redirect; use 2025-year form instead |
| https://genai.owasp.org/llmrisk/llm04-data-and-model-poisoning | 301 → LIVE | `https://genai.owasp.org/llmrisk/llm042025-data-and-model-poisoning/` | Non-year variant redirects to 2025 form; canonical is 2025-year |
| https://genai.owasp.org/llmrisk/llm05-improper-output-handling | **404 DEAD** | `https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/` | Non-year variant; no redirect; use 2025-year form instead |
| https://genai.owasp.org/resource/agentic-ai-top-10-vulnerabilities | **404 DEAD** | `https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/` | Alternative slug does not exist; use canonical Agentic resource URL |

## Key Findings

### Regression Guard
✅ **LLM01:2025 Prompt Injection is LIVE**
- Current canonical: `https://genai.owasp.org/llmrisk/llm01-prompt-injection/`
- Status: HTTP 200 (after automatic trailing-slash redirect from source without slash)
- **Action**: LEAVE UNCHANGED in both catalogs

### Twin Disambiguation (LLM02/03/04/05)
- **LLM02**: Non-year form (`llm02-sensitive-information-disclosure`) = **404 DEAD**; Year form (`llm022025-sensitive-information-disclosure/`) = **200 LIVE** ✅
- **LLM03**: Non-year form (`llm03-supply-chain`) = **404 DEAD**; Year form (`llm032025-supply-chain/`) = **200 LIVE** ✅
- **LLM04**: Non-year form (`llm04-data-and-model-poisoning`) = **301 redirect** to year form; Year form (`llm042025-data-and-model-poisoning/`) = **200 LIVE** ✅
- **LLM05**: Non-year form (`llm05-improper-output-handling`) = **404 DEAD**; Year form (`llm052025-improper-output-handling/`) = **200 LIVE** ✅

**Twin Verdict**: The **2025-year-prefixed form** (`llm0X2025-*`) is the canonical live form for all LLM02/03/04/05. The non-year variants (llm02-*, llm03-*, llm05-*) are dead or deprecated; llm04-* has a redirect but the canonical form is the 2025-year variant. Both `owasp.yaml` and `crosswalk.yaml` should point to the 2025-year forms exclusively; non-year twins in `crosswalk.yaml` should be removed or updated.

### Agentic Resource Pages
1. **OWASP Top 10 for Agentic Applications for 2026**: `https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/` = **200 LIVE** ✅
2. **Alternative slug** (`agentic-ai-top-10-vulnerabilities`): **404 DEAD** ✗

**Agentic Verdict**: Only one canonical form exists for Agentic content; the resource-based URL is correct. The alternate slug should not be used.

## Summary of Dead Citations

| Catalog | Dead URL | Canonical Replacement | Category |
|---|---|---|---|
| crosswalk.yaml | `llm02-sensitive-information-disclosure` | `llm022025-sensitive-information-disclosure/` | Twin (non-year dead) |
| crosswalk.yaml | `llm03-supply-chain` | `llm032025-supply-chain/` | Twin (non-year dead) |
| crosswalk.yaml | `llm05-improper-output-handling` | `llm052025-improper-output-handling/` | Twin (non-year dead) |
| crosswalk.yaml | `agentic-ai-top-10-vulnerabilities` | `owasp-top-10-for-agentic-applications-for-2026/` | Alternate slug (dead) |

## Remediation Scope

- **owasp.yaml**: All 11 distinct URLs are live (after trailing-slash normalization); no changes required
- **crosswalk.yaml**: Remove or replace 4 dead URLs with their canonical forms listed above
- **Trailing slash handling**: All canonical forms end with `/`; probed URLs without trailing slash redirect to version with slash

## Sources

- [OWASP GenAI Security Project](https://genai.owasp.org/)
- [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/)
- [OWASP Top 10 for Agentic Applications for 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
- [LLM01:2025 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
