# Delivery Report: Feature 074 — Baseline-Aware Pipeline

**Delivered**: 2026-04-01
**PR**: #79
**Issue**: #74
**Branch**: `074-baseline-aware-pipeline`

---

## Summary

Added baseline-aware threat detection pipeline that correlates findings across runs, generates coverage checklists per STRIDE category, and produces delta reports showing new/resolved/persistent findings.

## Delivery Metrics

| Metric | Estimated | Actual |
|--------|-----------|--------|
| Duration | 1-2 days | ~1 day |
| Tasks | 36 | 36/36 complete |
| Waves | 9 | 9 |
| Max parallelism | 7 | 7 |
| Checkpoints | 3 | P0 ✅, P1 ✅, P2 ✅ (with fixes) |

## User Stories Completed (6/6)

1. **US-074-1: Stable Re-Scan (P0)** — Deterministic finding IDs and scores across unchanged re-runs
2. **US-074-2: Remediation Verification (P0)** — Findings marked `[RESOLVED]` when threats are addressed
3. **US-074-3: New Threat Discovery (P0)** — Fresh discovery alongside carried-forward findings
4. **US-074-4: Delta Annotations (P1)** — Every finding annotated with `[NEW]`, `[UNCHANGED]`, `[UPDATED]`, or `[RESOLVED]`
5. **US-074-5: Coverage Reporting (P1)** — STRIDE coverage checklists per component type with gap detection
6. **US-074-6: CISO Dashboard (P2)** — Executive summary with delta statistics and trend data

## Key Deliverables

- **Schemas**: `coverage-checklists.yaml` (new), `finding.yaml`, `risk-scoring.yaml`, `compensating-controls.yaml` (extended)
- **Orchestrator**: 4-phase baseline pipeline (detect → carry-forward → discover → merge+dedup)
- **Risk Scorer**: Delta-aware scoring (inherited for UNCHANGED, fresh for UPDATED, bounded for NEW)
- **Control Analyzer**: Delta-aware control analysis (carry-forward for UNCHANGED, incremental for NEW/UPDATED)
- **Output Templates**: All 6 templates updated with baseline sections (.md and .sarif)
- **Skills**: Domain knowledge skills for orchestration, risk-scoring, and control-analysis
- **Reference**: `baseline-correlation.md` for orchestration skill

## Checkpoint Results

| Checkpoint | Status | Notes |
|------------|--------|-------|
| P0 (Schemas) | APPROVED | All schemas parse as valid YAML |
| P1 (Baseline Infrastructure) | APPROVED | Core correlation and carry-forward logic verified |
| P2 (Delta Annotations + Coverage) | APPROVED_WITH_CONCERNS | 2 medium items fixed (template parity) |
| Final Validation | APPROVED | Architect + Code Review passed after fixes |

## Surprise Log

The domain knowledge skills (tachi-orchestration, tachi-risk-scoring, tachi-control-analysis) were a larger effort than expected. While Feature 075 had already extracted the skill structure, extending those skills with baseline-aware domain knowledge required significant content authoring beyond the schema and template changes.

## Lessons Learned

**Template parity is non-trivial**: Keeping output templates (.md and .sarif) in sync with schema changes required dedicated validation tasks. Template parity checks should be built into phase checkpoints, not discovered at final validation. See PAT-017 in INSTITUTIONAL_KNOWLEDGE.md.

## Documentation Updates

| Agent | Files Updated |
|-------|---------------|
| Product Manager | PRD INDEX.md, User Stories README, OKRs README |
| Architect | Tech Stack README, System Design README, ADR-018 (new) |
| DevOps | No changes needed (template project) |

## Sign-offs

- **PM**: APPROVED (tasks.md, 2026-03-31)
- **Architect**: APPROVED_WITH_CONCERNS (tasks.md, 2026-03-31)
- **Team Lead**: APPROVED_WITH_CONCERNS (tasks.md, 2026-03-31)
