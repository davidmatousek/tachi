# Delivery Retrospective: Feature 128 — Executive Threat Architecture Infographic

**Feature**: 128 — Executive Threat Architecture Infographic
**Branch**: `128-prd-128-executive` (merged and deleted)
**PR**: [#131](https://github.com/davidmatousek/tachi/pull/131)
**Merged**: 2026-04-10 07:24 EDT
**Merge commit**: `7b217fe`
**Delivery date**: 2026-04-10

---

## Summary

F-128 added a sixth infographic template (`executive-architecture`) that renders system architecture as ordered horizontal layers with Critical/High severity findings overlaid as narrative callout boxes. The new template targets CISO audiences by placing the visual page immediately after the Executive Summary (pages 2–3 area) in the compiled PDF security report, ensuring the threat narrative lands within executive attention windows.

The feature shipped with a full pytest infrastructure bootstrap — tachi's first project-level Python test harness — including `pyproject.toml`, `requirements-dev.txt`, `tests/` tree, fixtures, golden JSON files, and baseline PDFs for five example projects.

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Issue created | 2026-04-09 19:27 EDT |
| Branch first activity | 2026-04-09 ~21:10 EDT |
| PR opened | 2026-04-09 late evening |
| PR merged | 2026-04-10 07:24 EDT |
| Calendar duration | ~12 hours |
| Estimated effort | 5–6 sessions / ~19.5 hours (team-lead rev2) |
| Actual sessions | Single extended session |
| Tasks | 51 / 51 complete |
| Phases | 8 (Test Bootstrap, Setup, Foundational, US-1, US-2, US-3, US-4, Polish) |
| User stories | 4 delivered (2 P1, 2 P2) |
| PR count | 1 (#131) |
| Files changed | 84 files (+139,270 lines, −27 lines in merge commit) |
| Deferred | T038 PM usability check (5-business-day post-merge SLA per tasks.md) |

### Estimate vs. Actual

The team-lead's rev2 estimate projected 5–6 sessions. The feature shipped in a single extended session. Compression drivers identified:
- Phase 0 pytest bootstrap was atomic and well-scoped (no discovery loops)
- F-091 (MAESTRO templates) and F-112 (attack path pages) supplied reusable patterns for extraction and Typst page integration
- Existing `infographic-page()` function covered the layout requirements without a new Typst function
- Schema-first ordering caught structural issues before any Python code was written

---

## Validation Results

| Gate | Status | Notes |
|------|--------|-------|
| P0 checkpoint | APPROVED_WITH_CONCERNS | 0 blocking, 3 minor (prior session) |
| P1 checkpoint | APPROVED_WITH_CONCERNS | 0 blocking, 5 INFO (Waves 3+4+5) |
| P2 checkpoint | APPROVED_WITH_CONCERNS | Covered by T036 architect-checkpoint.md |
| Architect final | APPROVED_WITH_CONCERNS | `specs/128-prd-128-executive/architect-checkpoint.md` |
| Code Review | APPROVED_WITH_CONCERNS | 4 INFO concerns, `specs/128-prd-128-executive/code-review.md` |
| Security Review | APPROVED_WITH_CONCERNS | 1 INFO concern, `specs/128-prd-128-executive/security-review.md` |
| SAST scan | PASSED | 12 files scanned (2 production scripts + 10 test files), 0 OWASP P0 findings |
| SCA scan | PASSED | 2 manifests audited (pyproject.toml + requirements-dev.txt), 0 CVEs |

---

## Retrospective

### Surprise Log

**Surprise**: Working in two Claude Code tabs — one for this feature and one for a parallel bug fix in the threat-report agent, schemas, and templates — caused uncommitted state to cross-contaminate at delivery time. At `/aod.deliver` the working directory contained seven modified files and twenty untracked files that belonged to the bug-fix session, forcing a manual scope-filter step before the F-128 delivery commit could be made.

### Feedback Loop (New Ideas)

None captured. No new backlog items added.

### Lesson Learned

Captured as **KB-026** in `docs/INSTITUTIONAL_KNOWLEDGE.md`:

> Parallel Claude Code sessions operating against the same working directory share the filesystem but not the git index. Automated delivery workflows that "stage and commit all uncommitted changes" will misattribute the other session's work unless the operator intercepts and filters manually. Mitigation: prefer `git worktree add` for true isolation, or explicitly list and stage only current-feature files at commit time.

**Category**: Process

---

## Documentation Updates

Updated by parallel documentation agents (PM, Architect, DevOps) invoked by `/aod.deliver` Step 3:

| File | Agent | Change |
|------|-------|--------|
| `docs/architecture/01_system_design/README.md` | pre-committed | F-128 section (Components, Data Flow, Tech Stack) |
| `docs/product/02_PRD/INDEX.md` | PM | Status Approved → Delivered, date 2026-04-10 |
| `docs/product/_backlog/BACKLOG.md` | pre-committed | Auto-regenerated |
| `docs/product/06_OKRs/README.md` | PM | Feature Delivery Log entry |
| `docs/architecture/00_Tech_Stack/README.md` | Architect | pytest toolchain subsection (first Python test infra) |
| `docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md` | Architect | NEW ADR for SOURCE_DATE_EPOCH convention |
| `CLAUDE.md` | Architect | Feature 128 entry in Recent Changes |
| `docs/devops/01_Local/README.md` | DevOps | Python Test Suite section |
| `docs/devops/CI_CD_GUIDE.md` | DevOps | pytest harness subsection + reusable GitHub Actions snippet |
| `docs/INSTITUTIONAL_KNOWLEDGE.md` | delivery | KB-026 lesson captured |

---

## Deferred Work

**T038 PM Usability Check** — 5-business-day post-merge SLA (per tasks.md Phase 7 footnote). PM to run the `executive-architecture` template against real consultant workflow and confirm the visual narrative lands as intended for CISO-level readers. No-blocking — the feature shipped without this gate held open.

---

## Next Step

Run `/aod.document` for post-delivery quality review: code simplification, docstrings, CHANGELOG, and API docs.
