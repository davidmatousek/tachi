# Delivery Report: Feature 104 — Downstream Baseline Propagation

**Date**: 2026-04-08
**PR**: #107 (squash merged)
**Branch**: `104-downstream-baseline-propagation`
**Status**: Delivered

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Branch created | 2026-04-08 |
| Delivery date | 2026-04-08 |
| Duration | Same-day (1 session) |
| Tasks | 18/18 complete |
| Waves | 5 execution waves |
| Deferred issues | 0 |

## Accomplishments

### User Stories Delivered

1. **US1 — Delta-Aware Threat Report (P0)**: Threat-report agent produces delta-aware narrative with executive summary delta counts, lifecycle-grouped threat analysis, attack tree carry-forward for UNCHANGED findings, and Section 8 Delta Summary
2. **US2 — Delta-Aware Infographics (P0)**: Infographic extraction excludes RESOLVED findings from severity distribution, includes delta breakdown fields, prompts include delta context
3. **US3 — Delta-Aware PDF Security Report (P1)**: Report-assembler agent and extraction script propagate baseline data for PDF finding tables, executive summary delta counts, and resolved findings audit section
4. **US4 — Shared Parser and Schema Delta Support (P0)**: Foundational parser functions and schema templates validated as prerequisite for all downstream consumers

### Key Deliverables

- **Output schemas**: `threats.md` (Section 7 Status column, Section 8 Delta Summary), `threat-report.md` (schema_version 1.1, Section 8 Delta Summary, baseline frontmatter)
- **Shared parser**: `tachi_parsers.py` — 3 functions (2 new, 1 extended): `parse_baseline_frontmatter()`, `parse_resolved_findings()`, `parse_threats_findings()`
- **Extraction scripts**: `extract-report-data.py` and `extract-infographic-data.py` — baseline field extraction with `has-baseline-data` flags
- **Agent instructions**: `threat-report.md` (delta-aware narrative), `threat-infographic.md` (delta-aware extraction)
- **Commands**: `infographic.md`, `security-report.md` (baseline data display)
- **Report assembler**: `.claude/agents/tachi/report-assembler.md` (baseline section assembly)
- **Example outputs**: All 6 regenerated with baseline columns

## How to See & Test

1. Run `/threat-model` on an architecture with baseline data — verify `threats.md` contains Status column in Section 7 and Section 8 Delta Summary
2. Run `/infographic` on baseline-aware `threats.md` — verify RESOLVED findings excluded from severity distribution
3. Run `/security-report` on baseline-aware output — verify baseline section in PDF
4. Run any command on pre-074 (non-baseline) input — verify identical behavior to before (backward compatible)

## Final Validation Results

| Review | Status |
|--------|--------|
| Architect | APPROVED_WITH_CONCERNS (1 bug found and fixed) |
| Code Review | APPROVED_WITH_CONCERNS (same bug confirmed and fixed) |
| Security | APPROVED (0 blocking findings) |

## Retrospective

**Surprises**: None — smooth implementation following established patterns
**New Ideas**: None
**KB Entry**: KB-023 — Centralized Parser Module Enables Same-Day Cross-Cutting Propagation

## Documentation Updates

| Agent | Files Updated |
|-------|-------------|
| PM | PRD INDEX (status→Delivered), User Stories (4 stories added), OKRs (delivery log) |
| Architect | CLAUDE.md (Recent Changes), Tech Stack README (schema/parser/agent updates), System Design README (Feature 104 section) |
| DevOps | No changes needed (no infrastructure impact) |
