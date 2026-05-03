# Delivery Retrospective: Feature 035 — Quantitative Risk Scoring

**Date**: 2026-03-27
**Branch**: `035-quantitative-risk-scoring`
**PR**: #37 (squash merged)
**GitHub Issue**: #35

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Completion Date | 2026-03-27 |
| Estimated Duration | 5.5–9.5h (6 execution waves) |
| Actual Duration | ~1 day (same-day delivery) |
| Tasks | 29/29 complete |
| User Stories | 5/5 delivered |
| Phases | 9 (Setup → Validation) |
| Files Changed | 25 files, +9,000 lines |

---

## Accomplishments

### User Stories Delivered

1. **US1: Quantitative Threat Scoring (P0)** — Four-dimensional scoring (CVSS 3.1, exploitability, scalability, reachability) with weighted composite score (0.0–10.0)
2. **US2: Risk Governance Fields (P0)** — Owner, SLA, disposition, review date attached to every scored finding
3. **US3: Dual Output Formats (P0)** — risk-scores.md (human-readable) + risk-scores.sarif (machine-readable SARIF 2.1.0)
4. **US4: Reachability-Aware Scoring (P1)** — Trust zone extraction and zone-to-reachability baseline mapping
5. **US5: Scoring Methodology Documentation (P1)** — Transparent methodology section in output

### Key Deliverables

| Deliverable | Path |
|-------------|------|
| Risk-scorer agent | `.claude/agents/tachi/risk-scorer.md` |
| /risk-score command | `.claude/commands/risk-score.md` |
| Risk-scoring schema | `schemas/risk-scoring.yaml` |
| Markdown output template | `templates/risk-scores.md` |
| SARIF output template | `templates/risk-scores.sarif` |
| Example scored output (md) | `examples/agentic-app/sample-report/risk-scores.md` |
| Example scored output (sarif) | `examples/agentic-app/sample-report/risk-scores.sarif` |
| SARIF reference update | `adapters/claude-code/agents/references/sarif-generation.md` |
| Finding schema extension | `schemas/finding.yaml` |
| Distribution adapters | `adapters/claude-code/agents/risk-scorer.md`, `adapters/claude-code/commands/risk-score.md` |

### Validation Results

- **T027 (Score Differentiation)**: >=80% of same-rated threats received different composite scores
- **T028 (Dual-Format Parity)**: 100% score consistency between risk-scores.md and risk-scores.sarif
- **T029 (End-to-End)**: Full command flow validated against example input

---

## How to See & Test

1. Run `/risk-score` against any threat model output directory containing `threats.md`
2. Verify `risk-scores.md` contains executive summary, sorted scored table, governance fields, methodology section
3. Verify `risk-scores.sarif` contains SARIF 2.1.0 with security-severity as composite score per finding
4. Compare scores between formats for consistency

Example:
```
/risk-score examples/agentic-app/sample-report/
```

---

## Surprise Log

No surprises — delivery went as planned.

---

## Lessons Learned

**PAT-006: Post-Pipeline Enrichment via Schema-Driven Scoring** — Design post-pipeline enrichment as a separate command and agent that reads existing output and produces new artifacts. Use a dedicated schema to define scoring methodology, preserving backward compatibility via optional extension references. Documented in `docs/INSTITUTIONAL_KNOWLEDGE.md`.

---

## Triad Sign-offs

| Role | Status | Notes |
|------|--------|-------|
| PM | APPROVED | All 5 user stories covered, 17 FRs traceable |
| Architect | APPROVED_WITH_CONCERNS | Minor task clarity items |
| Team-Lead | APPROVED_WITH_CONCERNS | Feasible 5.5-9.5h, Wave 4 overload noted |

---

## Documentation Updates

| Domain | Agent | Files Updated | Summary |
|--------|-------|---------------|---------|
| Product | PM | `docs/product/02_PRD/INDEX.md` | PRD status → Delivered |
| Architecture | Architect | `docs/architecture/00_Tech_Stack/README.md` | Risk-scorer agent, schema, templates, CVSS standard |
| DevOps | DevOps | None | No infrastructure changes needed |
| KB | — | `docs/INSTITUTIONAL_KNOWLEDGE.md` | PAT-006 added |
