# Delivery Report: Feature 071 — Deterministic Infographic Extraction

**Delivered**: 2026-03-30
**PR**: #72 (squash merged)
**Issue**: #71 (closed)
**Tasks**: 46/46 complete
**Duration**: Same day (single session)

---

## Summary

Replaced LLM-based data extraction in the threat-infographic agent with a deterministic Python script. Created shared `tachi_parsers.py` module extracted from `extract-report-data.py`. New `extract-infographic-data.py` script produces byte-identical JSON output for baseball card, system architecture, and risk funnel infographic templates.

## Key Deliverables

| Deliverable | Path |
|-------------|------|
| Shared parser module | `scripts/tachi_parsers.py` |
| Infographic extraction script | `scripts/extract-infographic-data.py` |
| Updated agent prompt | `.claude/agents/tachi/threat-infographic.md` |
| Updated schema | `schemas/infographic.yaml` |
| ADR | `docs/architecture/02_ADRs/ADR-017-deterministic-infographic-extraction.md` |

## Validation Results

| Check | Result |
|-------|--------|
| Architect review | APPROVED_WITH_CONCERNS (2 Low) |
| Code review | APPROVED_WITH_CONCERNS (3 Warning, 5 Suggestion) |
| Security scan | PASSED (3 Medium, 2 Low) |
| SAST | PASSED (3 files scanned) |

## Retrospective

**Surprise Log**: No surprises — implementation proceeded as planned.

**Lesson Learned**: PAT-015 — Determinism by design. Byte-identical output requires explicit design choices at every level: sort keys, tie-breaking rules, rounding methods (Largest Remainder Method).

**New Ideas**: None captured.

## Documentation Updated

- Product: PRD INDEX (delivered), User Stories, OKRs
- Architecture: Tech Stack, System Design, Patterns, ADR-017
- DevOps: Local setup, DevOps README
- Knowledge: PAT-015 added to Institutional Knowledge
