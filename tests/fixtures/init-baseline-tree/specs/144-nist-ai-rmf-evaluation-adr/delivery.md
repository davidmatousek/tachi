# Delivery Document: Feature 144 — NIST AI RMF Integration Evaluation ADR

**Delivery Date**: 2026-04-16
**Branch**: `144-nist-ai-rmf-evaluation-adr`
**PR**: #169

---

## What Was Delivered

- **ADR-025** (Status: Accepted 2026-04-16) at [docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md](../../docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md) — records tachi's NIST AI RMF 1.0 posture as **documentation-only mapping** (Option A). Three-surface structure: Surface A (AI RMF Functions × tachi pipeline phases), Surface B (AI RMF Subcategories × 8 compensating-control categories), Surface C (NIST AI 600-1 12 Generative AI risks × tachi STRIDE+AI categories). Rationale captures the tier-mismatch insight (Functions are organizational-tier outcomes; tachi produces artifact-tier evidence) with named re-evaluation triggers (≥3 regulated-adopter inquiries OR NIST AI RMF 2.0 publication OR SP 800-53 AI overlay GA).
- **Companion reference** at [.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md](../../.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md) — full Option A mapping table covering all 8 tachi compensating-control categories (authentication, input-validation, rate-limiting, encryption, logging-audit, csrf-protection, csp-security-headers, access-control) to their NIST AI RMF Subcategory equivalents.
- **SKILL.md update** at [.claude/skills/tachi-control-analysis/SKILL.md](../../.claude/skills/tachi-control-analysis/SKILL.md) — new 80-200 word "NIST AI RMF Relationship" section with verbatim decision-noun consistency against ADR-025 (SC-007 byte-equality).
- **ADR-024 cross-reference** — Related ADRs line updated with bidirectional ADR-025 back-reference.
- **MAESTRO compliance umbrella CLOSED** — regulated-adopter half (143 AIVSS + 144 NIST AI RMF) complements the MAESTRO taxonomy/correlation half (084 + 141 + 136 + 082). Tachi's compliance posture is now explicitly documented across both agentic-scoring and regulatory-alignment surfaces.

---

## How to See & Test

1. Open [docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md](../../docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md) on `main`. Confirm frontmatter `**Status**: Accepted` and `**Date**: 2026-04-16`. Decision section's first paragraph names posture as "documentation-only mapping" without ambiguity.
2. Scroll to Context section. Confirm three labeled subsections (Surface A / B / C) exist. Spot-check rows — each uses one of: Overlap, Gap, Conflict, "No equivalent".
3. `grep -l "NIST AI RMF" docs/architecture/02_ADRs/*.md` — confirm ADR-025 is the only ADR whose Decision section addresses NIST AI RMF (ADR-024 references only as cross-reference).
4. Open [.claude/skills/tachi-control-analysis/SKILL.md](../../.claude/skills/tachi-control-analysis/SKILL.md). Find "NIST AI RMF Relationship" section (~80-200 words). Verify decision-noun string equals the ADR Decision section (SC-007 byte-equality, modulo case).
5. Open [.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md](../../.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md). Confirm complete mapping table covers all 8 tachi compensating-control categories.
6. Run backward-compatibility regression: `SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py` — expect 5/5 PASS (ADR-021 byte-identical baselines preserved; no pipeline-output drift).
7. Run the SC-006 zero-drift guard: `git diff 144-nist-ai-rmf-evaluation-adr^..main -- schemas/ scripts/ .claude/agents/ examples/` — expect empty (documentation-only spike invariant).

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | 1-2 days |
| Actual Duration | <1 day (same-day: first commit 2026-04-16 11:37 UTC, merged 2026-04-16 15:52 UTC) |
| Variance | Under-estimate by ~1 day — mature AI RMF 1.0 framework required no version-tracking research spike; Option A docs-only scope avoided follow-on implementation Issue (FR-008 XOR branch); T027 skipped N/A |

---

## Surprise Log

Smooth sailing — the five-layer scope discipline (FR-excludes + SC-006 git-diff guard + allow-list + Constraints + Assumptions) held across all 43 tasks and prevented drift into schema, agent, or example regeneration work. The second consecutive docs-only MAESTRO-companion ADR (143→144) converged on the same structural rhythm despite arriving at opposite decisions (143 diverge; 144 documentation-only mapping), suggesting the pattern is reusable for future compliance-framework evaluations.

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| Process improvement | MAESTRO-Companion ADR Rhythm — two consecutive posture ADRs (143 AIVSS, 144 NIST AI RMF) establish a repeatable three-part pattern (three-surface evaluation + decision-noun discipline + five-criteria rationale with named re-evaluation triggers) for compliance-framework posture documentation | KB-033 in [docs/INSTITUTIONAL_KNOWLEDGE.md](../../docs/INSTITUTIONAL_KNOWLEDGE.md) |

---

## Feedback Loop

**New Ideas**: None

Re-evaluation triggers are already encoded in ADR-025 itself (≥3 regulated-adopter inquiries OR NIST AI RMF 2.0 publication OR SP 800-53 AI overlay GA) — no separate tracking Issue needed.

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | [specs/144-nist-ai-rmf-evaluation-adr/spec.md](spec.md) |
| Implementation Plan | [specs/144-nist-ai-rmf-evaluation-adr/plan.md](plan.md) |
| Task Breakdown | [specs/144-nist-ai-rmf-evaluation-adr/tasks.md](tasks.md) |
| Research | [specs/144-nist-ai-rmf-evaluation-adr/research.md](research.md) |
| Quickstart | [specs/144-nist-ai-rmf-evaluation-adr/quickstart.md](quickstart.md) |
| PRD | [docs/product/02_PRD/144-nist-ai-rmf-evaluation-adr-2026-04-15.md](../../docs/product/02_PRD/144-nist-ai-rmf-evaluation-adr-2026-04-15.md) |

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 1 updated (`docs/product/02_PRD/INDEX.md`) + 3 N/A (STATUS.md, completed-features.md, quarterly roadmap — none exist in repo) | APPROVED |
| Architecture | architect | 3 updated (`docs/architecture/README.md`, `docs/architecture/00_Tech_Stack/README.md`, `CLAUDE.md`) | APPROVED |
| DevOps | devops | 0 — no DevOps impact (zero new runtime dependencies, zero CI workflow changes, zero infra/deployment changes, zero new CLI prerequisites) | APPROVED |

---

## Cleanup

- [x] Feature branch deleted (squash-merge via `gh pr merge 169 --squash --delete-branch`)
- [x] All tasks complete (43/43; T027 N/A per FR-008 XOR — Option A chosen, no follow-on Issue filed)
- [x] No TBD/TODO in docs (ADR-025 Date placeholder resolved to 2026-04-16 pre-merge per T044)
- [x] Committed and pushed (main @ 9e66d34)
- [x] GitHub Issue closed (`stage:done` transition + closing comment cross-referencing this delivery doc)

**Feature 144 is now officially CLOSED.**
