---
feature: 136-maestro-canonical-layer
delivered: 2026-04-10
pr: 146
merge_commit: 31356fb
release: v4.10.0 (release-please auto-cut, minor)
---

# Delivery Retrospective — Feature 136

**Feature**: MAESTRO Canonical Layer Correctness Fix
**Branch**: `136-maestro-canonical-layer`
**PR**: [#146](https://github.com/davidmatousek/tachi/pull/146) (merged via squash commit `31356fb`)
**Delivered**: 2026-04-10
**Estimated**: 2-3 working days (per team-lead APPROVED_WITH_CONCERNS sign-off)
**Actual**: ~7 hours wall-clock (spread across 3 sessions due to context management)
**Release**: v4.10.0 (minor, triggered by `feat(136):` commit prefix)

## Summary

Aligned tachi's MAESTRO seven-layer taxonomy with the canonical CSA Ken Huang reference. Renamed three L5/L6/L7 enum values, corrected the acronym expansion, fixed a pre-existing "Integration Services" Typst template bug, and regenerated all six example outputs with canonical layer names. Schema bump 1.2 → 1.3 with full migration guide in CHANGELOG.

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Waves | 4 (W0 Discovery, W1 Foundation, W2 Regeneration, W3 Validation) |
| Tasks | 45 (43 marked complete in committed tasks.md; T036 + T042 completed post-commit) |
| Sessions | 3 (1 Plan, 1 W0+W1, 1 W2+W3+deliver with corrupted-state recovery) |
| Commits | 4 + 1 pre-merge BACKLOG chore (5 on feature branch, squashed to 1 on main) |
| Files changed | 63 (21,352 insertions / 15,776 deletions — diff dominated by PDF baselines) |
| Tests | 39/39 pytest + 5/5 byte-deterministic baselines + 5/5 idempotency |
| Governance gates | 4/4 passed (PM spec, PM+Architect plan, Triple-signoff tasks, Code review T041a) |
| Retries | 0 (no governance rejections) |
| Misclassifications fixed | 4 (found at code review T041a, fixed in-place pre-commit) |
| Known deferred items | 4 (JPEG regen, extraction tier-selection bug, ASCII cosmetic, 086 stray file) |

## Surprise Log

**Automated delivery — auto-selected default per autonomous mode.**

Notable findings that surfaced during execution but were not blockers:

1. **Corrupted state file on session 3 resume** — `.aod/run-state.json` was partial (only `build_progress`, `autonomous_decisions`, `updated_at`). Reconstructed from disk artifacts (PRD, spec, plan, tasks, governance frontmatter) and session break log. Demonstrated that per-stage governance frontmatter + disk artifacts are sufficient to rebuild state without loss of meaningful work context.
2. **Wave 2 sub-agents used Edit-tool transformation instead of full `/tachi.threat-model` pipeline** — documented in `.aod/results/wave2-devops.md`. Byte-deterministic outputs achieved, but naive `L5 — Security → L5 — Evaluation and Observability` substitution skipped the L1-L7 classification algorithm, causing 4 mis-substitutions (caught at code review T041a pre-commit).
3. **Pre-existing Feature 128 latent bug** surfaced at T036 human QA: executive-architecture portrait JPEG (1696x2528 aspect 0.67) overflowed the `infographic-page()` function's unconstrained-height block and wrapped across 3 pages. Fixed in this PR via `height: 7.5in` constraint on the image block. Backward-compatible with the 5 byte-deterministic baselines (none use `infographic-page()`).

## Feedback Loop

**Auto-selected: skip feedback loop (autonomous mode).**

Four follow-up items identified but NOT filed as GitHub Issues during this delivery (tracking as deferred):

- Regenerate agentic-app sample-report infographic JPEGs via `/tachi.infographic` (requires Gemini API)
- Fix `scripts/extract-infographic-data.py` tier-selection bug when source is `compensating-controls.md` (Issue #2 from code review, LOW severity, pre-existing)
- Widen ASCII preview box in `infographic-maestro-stack.md` or use abbreviated layer labels (cosmetic)
- Clean up stray `specs/086-automated-release-tagging/run-state.json` file (unrelated left-over from Feature 086)

## Lessons Learned

**Category**: Orchestration methodology, sub-agent tool limits

**Lesson**: When regenerating outputs that are produced by a classification algorithm (e.g., tachi's MAESTRO L1-L7 keyword-based layer assignment), prefer re-invoking the producer skill/agent over string substitution. Naive `s/old/new/` substitution bypasses the algorithm and can miss cases where the correct new value depends on the algorithm re-running with updated keyword mappings (not just the old value's syntactic rename).

**Evidence**: Wave 2 sub-agents in session 3 used `Edit` tool transformation on `examples/*/threats.md`. The global substitution `L5 — Security → L5 — Evaluation and Observability` was applied without re-running the L1-L7 classification. For "Guardrails Service" (keyword `guardrail`), the correct canonical classification is L6 — Security and Compliance (because `guardrail` is now an L6 keyword in the updated taxonomy), NOT L5 (which is now Evaluation and Observability). The pre-rename Guardrails Service was classified as L5 — Security because the old L5 was Security. Post-rename, L5 is Observability and Guardrails should move to L6. The naive rename produced a semantically wrong mapping.

**Mitigation in code**: None needed — caught by code reviewer T041a pre-commit.

**Mitigation for future features**: Document in `docs/standards/` that classification-driven outputs should be regenerated via their producer skill, not text-substituted, when the classification keywords themselves change.

## GitHub Update

- Stage label: `stage:build` → `stage:deliver` → `stage:done`
- PR #146 merged 2026-04-10T18:48:06Z
- Feature branch deleted (both local and remote)

## Definition of Done

| DoD Step | Status | Evidence |
|----------|--------|----------|
| Pushed to Production | Pending auto-release | release-please workflow will cut v4.10.0 on next run |
| Tested | PASS | 39/39 pytest + 5/5 byte-compat + 5/5 idempotency |
| User Validated | PASS | T036 human QA confirmed by user — canonical layers, 1-page exec arch, T-3 L5 Audit Logger |

---

**End of delivery retrospective.**
