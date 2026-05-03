# Wave 3: Cross-Agent Consistency Results

**Date**: 2026-03-22
**Agent**: code-reviewer
**Scope**: T029-T034 (User Story 3 — Consistent Output Format)

---

## Summary

| Task | Description | Status | Fixes |
|------|-------------|--------|-------|
| T029 | Section organization | PASS (after fix) | 3 files fixed |
| T030 | Finding template fields | PASS | 0 |
| T031 | ID prefix conventions | PASS | 0 |
| T032 | Category field values | PASS | 0 |
| T033 | Risk computation matrix | PASS | 0 |
| T034 | output_schema frontmatter | PASS | 0 |

**Total fixes applied**: 3 (all in T029)

---

## T029: Section Organization

**Finding**: Empty Results Guidance heading level was inconsistent across agent types.

- **Agentic agents** (agent-autonomy, tool-abuse): Empty Results Guidance was an H3 subsection within Detection Scope (correct placement).
- **LLM agents** (prompt-injection, data-poisoning, model-theft): Empty Results Guidance was a standalone H2 section placed AFTER the Finding Template / Risk Level Computation sections — outside Detection Scope and at a different heading level.

**Fix applied**: Moved Empty Results Guidance into Detection Scope as an H3 subsection in all 3 LLM agents, matching the agentic agent structure. Removed the duplicate standalone H2 sections.

**Files modified**:
- `agents/ai/prompt-injection.md` — moved Empty Results Guidance from H2 (line 147) to H3 within Detection Scope (after Detection Patterns)
- `agents/ai/data-poisoning.md` — moved Empty Results Guidance from H2 (line 148) to H3 within Detection Scope (after Detection Patterns)
- `agents/ai/model-theft.md` — moved Empty Results Guidance from H2 (line 165) to H3 within Detection Scope (after Detection Patterns)

**Post-fix section structure (all 5 agents now match)**:
```
## Purpose
## Detection Scope
  ### Trigger Keywords
  ### Applicable DFD Element Types
  ### Empty Results Guidance          <-- H3, within Detection Scope
  ### Detection Patterns
## Finding Template
  ### Example Findings
  ### Risk Level Computation
## References
```

Note: The agentic agents place Empty Results Guidance before Detection Patterns, while LLM agents place it after Detection Patterns. Both are within Detection Scope at H3 level. The slight ordering difference is acceptable — Empty Results Guidance logically relates to Detection Scope regardless of its position relative to Detection Patterns within that section.

---

## T030: Finding Template Fields

All 5 agents define identical IR fields in their Finding Template sections:

| # | Field | agent-autonomy | tool-abuse | prompt-injection | data-poisoning | model-theft |
|---|-------|----------------|------------|------------------|----------------|-------------|
| 1 | id | OK | OK | OK | OK | OK |
| 2 | category | OK | OK | OK | OK | OK |
| 3 | component | OK | OK | OK | OK | OK |
| 4 | threat | OK | OK | OK | OK | OK |
| 5 | likelihood | OK | OK | OK | OK | OK |
| 6 | impact | OK | OK | OK | OK | OK |
| 7 | risk_level | OK | OK | OK | OK | OK |
| 8 | mitigation | OK | OK | OK | OK | OK |
| 9 | references | OK | OK | OK | OK | OK |
| 10 | dfd_element_type | OK | OK | OK | OK | OK |

Field names, spelling, and casing are consistent across all 5 agents. All match `schemas/finding.yaml`.

**No fixes required.**

---

## T031: ID Prefix Conventions

| Agent | Category | Expected Prefix | Template Prefix | Example IDs | Status |
|-------|----------|-----------------|-----------------|-------------|--------|
| agent-autonomy | agentic | AG-N | AG-{N} | AG-1, AG-2, AG-3, AG-4 | PASS |
| tool-abuse | agentic | AG-N | AG-{N} | AG-1, AG-2, AG-3 | PASS |
| prompt-injection | llm | LLM-N | LLM-{N} | LLM-1, LLM-2, LLM-3 | PASS |
| data-poisoning | llm | LLM-N | LLM-{N} | LLM-1, LLM-2, LLM-3 | PASS |
| model-theft | llm | LLM-N | LLM-{N} | LLM-1, LLM-2, LLM-3 | PASS |

All IDs start at 1 and increment sequentially within each agent. Prefixes match `schemas/finding.yaml` pattern `^(S|T|R|I|D|E|AG|LLM)-\d+$`.

**No fixes required.**

---

## T032: Category Field Values

| Agent | Expected | Template Value | Example Values | Schema Enum Match | Status |
|-------|----------|----------------|----------------|-------------------|--------|
| agent-autonomy | agentic | agentic | agentic | Yes | PASS |
| tool-abuse | agentic | agentic | agentic | Yes | PASS |
| prompt-injection | llm | llm | llm | Yes | PASS |
| data-poisoning | llm | llm | llm | Yes | PASS |
| model-theft | llm | llm | llm | Yes | PASS |

All category values match `schemas/finding.yaml` enum: `[spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, agentic, llm]`.

**No fixes required.**

---

## T033: Risk Computation Matrix

All 5 agents contain identical OWASP 3x3 risk matrices:

| | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

Verified key cells: HIGH/HIGH=Critical, HIGH/MEDIUM=High, MEDIUM/MEDIUM=Medium, LOW/LOW=Note. All match `schemas/finding.yaml` risk_matrix definition.

Additionally verified that all example findings in all 5 agents compute risk_level correctly from their likelihood and impact values:
- agent-autonomy: HIGH/MEDIUM=High, MEDIUM/HIGH=High, MEDIUM/MEDIUM=Medium, MEDIUM/MEDIUM=Medium -- all correct
- tool-abuse: HIGH/HIGH=Critical, MEDIUM/HIGH=High, MEDIUM/HIGH=High -- all correct
- prompt-injection: HIGH/HIGH=Critical, MEDIUM/HIGH=High, MEDIUM/MEDIUM=Medium -- all correct
- data-poisoning: HIGH/HIGH=Critical, LOW/HIGH=Medium, MEDIUM/MEDIUM=Medium -- all correct
- model-theft: MEDIUM/HIGH=High, MEDIUM/HIGH=High, HIGH/LOW=Medium -- all correct

**No fixes required.**

---

## T034: output_schema Frontmatter References

| Agent | output_schema Value | Status |
|-------|-------------------|--------|
| agent-autonomy | `schemas/finding.yaml` | PASS |
| tool-abuse | `schemas/finding.yaml` | PASS |
| prompt-injection | `schemas/finding.yaml` | PASS |
| data-poisoning | `schemas/finding.yaml` | PASS |
| model-theft | `schemas/finding.yaml` | PASS |

All 5 agents reference `schemas/finding.yaml` as `output_schema` in their YAML frontmatter.

**No fixes required.**
