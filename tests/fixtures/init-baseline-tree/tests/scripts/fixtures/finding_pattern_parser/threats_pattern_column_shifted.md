---
schema_version: "1.4"
date: "2026-04-16"
---

# Threat Model: Pattern Column in Alternate Position

This fixture places the Pattern column LAST (after Mitigation) rather than in
the FR-009 canonical position between Category and Component. The parser
MUST detect the column by header name, not by positional index — any parser
that relies on fixed column indices would return 'none' for every row here
even though the column is populated.

## 7. Recommended Actions

| Finding ID | Component | Threat | Risk Level | Mitigation | Pattern |
|------------|-----------|--------|------------|------------|---------|
| S-1 | LLM Orchestrator | Agent identity forgery | High | Per-agent mTLS | trust_exploitation |
| AG-2 | LLM Orchestrator | Coordinated tool abuse | Critical | Inter-agent rate limits | agent_collusion |
| T-3 | PostgreSQL | Input validation bypass | Medium | Strict schema validation | — |

## 8. Delta Summary

| Status | Count |
|--------|-------|
| NEW | 0 |
| UNCHANGED | 3 |
| UPDATED | 0 |
| RESOLVED | 0 |
