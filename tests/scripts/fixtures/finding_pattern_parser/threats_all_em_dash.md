---
schema_version: "1.4"
date: "2026-04-16"
---

# Threat Model: All-Em-Dash Pattern Fixture (Single-Agent Architecture)

## 7. Recommended Actions

| Finding ID | Component | Threat | Pattern | Risk Level | Mitigation |
|------------|-----------|--------|---------|------------|------------|
| S-1 | Auth Service | Token forgery via weak signature | — | High | Use RS256 with rotated keys |
| T-2 | Node API | Input validation bypass | — | Medium | Implement strict schema validation |
| I-3 | PostgreSQL | Sensitive field leakage | — | Medium | Apply column-level encryption |
| D-4 | CDN Edge | Volumetric request flooding | — | Low | Rate limits at edge |

## 8. Delta Summary

| Status | Count |
|--------|-------|
| NEW | 0 |
| UNCHANGED | 4 |
| UPDATED | 0 |
| RESOLVED | 0 |
