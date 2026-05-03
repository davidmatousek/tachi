# Delivery Report: Feature 067 — Deterministic Report Data Extraction

**Delivery Date**: 2026-03-30
**PR**: #68 (squash-merged)
**Issue**: #67
**Branch**: `067-deterministic-report-data`

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | ~4 hours |
| Actual Duration | Same day (2026-03-30) |
| Tasks Completed | 32/32 |
| Execution Waves | 5 |
| Checkpoints | P0 APPROVED, P1 APPROVED, P2 APPROVED |

---

## Accomplishments

### User Stories Delivered (6/6)

1. **US1 - Reproducible Report Generation (P1)**: Script produces byte-identical `report-data.typ` on identical inputs across all 3 tiers
2. **US2 - Validated Severity Counts (P1)**: Internal consistency validation catches severity sum mismatches and duplicate finding IDs
3. **US3 - Deterministic Scope Data Extraction (P1)**: Components, data flows, trust zones, and boundary crossings extracted with count validation
4. **US4 - Agent Prompt Update (P1)**: Report-assembler agent updated to invoke Python script instead of inline LLM parsing
5. **US5 - Consistent Recommendation Formatting (P2)**: Recommendations extracted verbatim with proper Typst string escaping
6. **US6 - Testing Against Example Datasets (P2)**: All 3 tiers verified against agentic-app dataset with Tier 1 test fixture

### Key Deliverables

- `scripts/extract-report-data.py` — 1400+ line Python script (stdlib only, zero external deps)
- `.claude/agents/tachi/report-assembler.md` — Updated agent prompt
- `examples/agentic-app/sample-report/compensating-controls.md` — Tier 1 test fixture
- Full spec artifacts in `specs/067-deterministic-report-data/`

---

## How to See & Test

1. **Determinism check**: Run `python3 scripts/extract-report-data.py --target-dir examples/agentic-app/sample-report/ --output /tmp/test1.typ --template-dir templates/tachi/security-report/` twice and `diff` the outputs
2. **Full pipeline**: Run `/security-report` on the agentic-app example dataset
3. **Error handling**: Run with missing `threats.md` (exit 1) or injected severity mismatch (exit 2)

---

## Surprise Log

Nothing unexpected — implementation went as planned.

## Lessons Learned

**PAT-014**: Precision data extraction requires scripts, not LLM parsing. When extracting structured data from known formats for reporting, deterministic script-based parsing must replace LLM-based extraction for reproducibility.

## New Ideas Captured

- Issue #69: Expand example datasets for broader test coverage

---

## Documentation Updates

| Domain | Files Updated |
|--------|-------------|
| Product | `INDEX.md` (PRD status → Delivered), `05_User_Stories/README.md` (6 stories), `06_OKRs/README.md` (delivery log) |
| Architecture | `00_Tech_Stack/README.md` (Python 3.9+), `01_system_design/README.md` (data flow + F067 section) |
| DevOps | `01_Local/README.md` (Python 3.9+ prerequisite) |
| KB | `INSTITUTIONAL_KNOWLEDGE.md` (PAT-014) |

---

## Sign-Off

- **PM**: APPROVED (2026-03-30)
- **Architect**: APPROVED_WITH_CONCERNS (2 non-blocking)
- **Team-Lead**: APPROVED (2026-03-30)
