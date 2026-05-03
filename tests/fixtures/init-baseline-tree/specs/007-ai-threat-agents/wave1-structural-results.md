# Wave 1: Structural Audit Results

**Feature**: 007 - AI Threat Agents
**Phase**: 2 (Foundational - Structural Audit)
**Agent**: senior-backend-engineer
**Date**: 2026-03-22

---

## Summary

- **Tasks completed**: 6 (T005-T010)
- **Total changes made**: 5 (one per agent file)
- **Frontmatter gaps found**: 0
- **Section structure gaps found**: 5 (missing Risk Level Computation in all 5 agents)

---

## T005: Frontmatter Audit - agent-autonomy.md

**Status**: PASS (no changes needed)

All 6 frontmatter fields present and correct:
| Field | Expected | Actual | Match |
|-------|----------|--------|-------|
| agent_name | agent-autonomy | agent-autonomy | Yes |
| category | agentic | agentic | Yes |
| threat_class | AG | AG | Yes |
| dfd_targets | [Process] | [Process] | Yes |
| owasp_references | (present) | [ASI-01] | Yes |
| output_schema | schemas/finding.yaml | schemas/finding.yaml | Yes |

---

## T006: Frontmatter Audit - tool-abuse.md

**Status**: PASS (no changes needed)

All 6 frontmatter fields present and correct:
| Field | Expected | Actual | Match |
|-------|----------|--------|-------|
| agent_name | tool-abuse | tool-abuse | Yes |
| category | agentic | agentic | Yes |
| threat_class | AG | AG | Yes |
| dfd_targets | [Process] | [Process] | Yes |
| owasp_references | (present) | [MCP-03] | Yes |
| output_schema | schemas/finding.yaml | schemas/finding.yaml | Yes |

---

## T007: Frontmatter Audit - prompt-injection.md

**Status**: PASS (no changes needed)

All 6 frontmatter fields present and correct:
| Field | Expected | Actual | Match |
|-------|----------|--------|-------|
| agent_name | prompt-injection | prompt-injection | Yes |
| category | llm | llm | Yes |
| threat_class | LLM | LLM | Yes |
| dfd_targets | [Process] | [Process] | Yes |
| owasp_references | (present) | [OWASP LLM01:2025] | Yes |
| output_schema | schemas/finding.yaml | schemas/finding.yaml | Yes |

---

## T008: Frontmatter Audit - data-poisoning.md

**Status**: PASS (no changes needed)

All 6 frontmatter fields present and correct:
| Field | Expected | Actual | Match |
|-------|----------|--------|-------|
| agent_name | data-poisoning | data-poisoning | Yes |
| category | llm | llm | Yes |
| threat_class | LLM | LLM | Yes |
| dfd_targets | [Data Store, Data Flow] | [Data Store, Data Flow] | Yes |
| owasp_references | (present) | [OWASP LLM03:2025] | Yes |
| output_schema | schemas/finding.yaml | schemas/finding.yaml | Yes |

---

## T009: Frontmatter Audit - model-theft.md

**Status**: PASS (no changes needed)

All 6 frontmatter fields present and correct:
| Field | Expected | Actual | Match |
|-------|----------|--------|-------|
| agent_name | model-theft | model-theft | Yes |
| category | llm | llm | Yes |
| threat_class | LLM | LLM | Yes |
| dfd_targets | [Data Store, Process] | [Data Store, Process] | Yes |
| owasp_references | (present) | [OWASP LLM10:2025] | Yes |
| output_schema | schemas/finding.yaml | schemas/finding.yaml | Yes |

---

## T010: Section Structure Audit - All 5 Agents

**Status**: PASS (after fix)

### Gap Found

All 5 agents were missing the `### Risk Level Computation` subsection. The STRIDE reference agents (`agents/stride/spoofing.md` et al.) include this as an H3 subsection under `## Finding Template` containing the OWASP 3x3 risk matrix. All 5 AI agents omitted it entirely.

### Section naming note

The canonical order lists "Patterns/Indicators" as section 3. The STRIDE agents use `### Patterns and Indicators` (H3 under Detection Scope). The AI agents use `### Detection Patterns` (H3 under Detection Scope). The placement is structurally identical; the naming differs slightly. No change made -- the variant naming is acceptable per the task description ("may be named 'Patterns and Indicators' or 'Detection Patterns'").

### Fix Applied

Added `### Risk Level Computation` subsection with the OWASP 3x3 matrix to all 5 agents, placed as the final H3 subsection under `## Finding Template`, immediately before `## References`. This matches the STRIDE agent structure exactly.

### Post-Fix Section Structure (all 5 agents identical)

```
## Purpose
## Detection Scope
  ### Trigger Keywords
  ### Applicable DFD Element Types
  ### Detection Patterns
## Finding Template
  ### Example Findings
  ### Risk Level Computation
## References
```

### Per-Agent Verification

| Agent | Purpose | Detection Scope | Detection Patterns | Finding Template | Risk Level Computation | References | Status |
|-------|---------|----------------|-------------------|-----------------|----------------------|------------|--------|
| agent-autonomy | L12 | L16 | L37 | L80 | L162 (added) | L172 | PASS |
| tool-abuse | L12 | L16 | L36 | L67 | L134 (added) | L144 | PASS |
| prompt-injection | L12 | L16 | L37 | L62 | L129 (added) | L139 | PASS |
| data-poisoning | L12 | L16 | L41 | L72 | L138 (added) | L148 | PASS |
| model-theft | L12 | L16 | L39 | L74 | L141 (added) | L151 | PASS |

---

## Files Modified

1. `agents/ai/agent-autonomy.md` -- added Risk Level Computation subsection
2. `agents/ai/tool-abuse.md` -- added Risk Level Computation subsection
3. `agents/ai/prompt-injection.md` -- added Risk Level Computation subsection
4. `agents/ai/data-poisoning.md` -- added Risk Level Computation subsection
5. `agents/ai/model-theft.md` -- added Risk Level Computation subsection
6. `specs/007-ai-threat-agents/tasks.md` -- marked T005-T010 as [X]

---

## Checkpoint

All 5 agents pass structural audit. Content validation (Phases 3-4) can begin.
