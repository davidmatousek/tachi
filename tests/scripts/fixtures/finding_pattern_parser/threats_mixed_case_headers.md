---
schema_version: "1.4"
date: "2026-04-16"
---

# Threat Model: Mixed-Case Pattern Header Fixture

This fixture validates case-insensitive detection of the Pattern column header. FR-009
documents "Agentic Pattern" as the canonical spelling; this fixture uses "Agentic Pattern"
with mixed casing on the values themselves to force the parser to route each cell through
parse_finding_pattern() for canonicalization.

## 7. Recommended Actions

| Finding ID | Component | Threat | Agentic Pattern | Risk Level | Mitigation |
|------------|-----------|--------|-----------------|------------|------------|
| S-1 | LLM Orchestrator | Agent identity forgery | Trust_Exploitation | High | Per-agent mTLS |
| AG-2 | LLM Orchestrator | Coordinated tool abuse | AGENT_COLLUSION | Critical | Inter-agent rate limits |
| AG-3 | Specialist Agent | Cascade-driven emergent behavior | Emergent_Behavior | High | Fail-safe shutdown |
| AG-4 | Specialist Agent | Equal-weight multi-rule match | Multiple | Medium | Defense-in-depth review |
| T-5 | PostgreSQL | Input validation bypass | None | Medium | Strict schema validation |

## 8. Delta Summary

| Status | Count |
|--------|-------|
| NEW | 0 |
| UNCHANGED | 5 |
| UPDATED | 0 |
| RESOLVED | 0 |
