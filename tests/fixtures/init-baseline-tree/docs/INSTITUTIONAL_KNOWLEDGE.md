# Institutional Knowledge - tachi

**Project**: tachi - threat modeling sidecar
**Purpose**: Capture learnings, patterns, and solutions to prevent repeated mistakes
**Created**: {{PROJECT_START_DATE}}
**Last Updated**: 2026-05-04

**Entry Count**: 1 / 20 (KB System Upgrade triggers at 20 — schedule review)
**Last Review**: 2026-05-04 (F-248 retrospective)
**Status**: ✅ Manual mode (file-based)

---

## Overview

This file stores institutional knowledge for tachi development. It's used by:
- `kb-create` skill - Add new learnings
- `kb-query` skill - Search existing patterns
- `root-cause-analyzer` skill - Document root causes

### When to Upgrade to KB System

**Trigger Conditions** (upgrade when ANY is true):
- Entry count reaches **20**
- File size exceeds **2,000 lines**
- Search takes **>5 minutes** (currently <5 seconds with Cmd+F)
- Major project milestone complete

**Current Status**: Manual file working well. No upgrade needed yet.
**Next Review**: When entry count reaches 15

---

## Patterns

### Entry 1: F-248 Substitution Surface Hardening — Delivery Retrospective

## [TEST] - Whole-tree byte-comparison fixtures drift on every doc/pipeline-artifact addition

**Date**: 2026-05-04
**Feature**: F-248 (Substitution Surface Hardening — BLP-02 Wave 1)
**Category**: TEST infrastructure / regression-protection design
**Severity**: Medium (recurring CI flake; not a correctness defect)

### Symptom

`tests/scripts/test_init_sh_substitution.py::test_personalized_tree_bytes_match_baseline` fails with `AssertionError: file set drift` whenever new files are committed to the repo since the baseline was last regenerated. Recurring pattern in F-248: drift surfaced at T039, T040, and T046 pre-merge — three baseline regens in one feature.

### Root Cause (5 Whys validated)

Test-1 walks the **entire** init.sh output tree, while the runtime residual scan (`aod_template_assert_no_residual` post T020) walks only files in the `personalized` category from `.aod/template-manifest.txt`. This asymmetry causes false-positive drift whenever build-pipeline artifacts (`.security/reports/*.sarif`, `specs/*/test-results/`, `specs/*/security-scan.md`, `specs/*/build-summary.json`, `specs/*/tasks-runlog.txt`) are committed during a feature's lifetime.

Compounding: the test fixture is the entire 2071-file personalized tachi tree (82MB). Each init.sh invocation walks the full tree; on slow macos-latest runners the first run hits the 300s subprocess timeout (cold-cache penalty). 17 init.sh runs per CI = 35-40min wall-clock, with timeout flake on the runner-perf edge.

### Solution

**Immediate (workaround, F-248)**: regenerate the baseline tree at HEAD via `tests/fixtures/regenerate-baseline.sh`. Documented in the script's docstring as a legitimate trigger ("new docs file added"). 3rd-time use during F-248 confirmed this is symptom-treatment, not root-cause fix.

**Hot-patch (post-F-248, same-day owner: David)**: extract adversarial cases 1-12 from `test_init_sh_adversarial.py` into unit-style tests against `aod_template_substitute_placeholders` + `aod_init_read_validated` directly (no full init.sh invocation). Eliminates 12 of the 17 init.sh runs and their cold-cache exposure. Estimated CI runtime reduction: ~25min.

**Long-term (Issue #250)**: refactor Test-1 to read `.aod/template-manifest.txt` and walk only `personalized` category — symmetric to T020 runtime invariant. Replace 2071-file baseline tree with a synthetic ~5-file fixture covering substitution invariants. Eliminates whole class of baseline-staleness flakes.

### Prevention

1. **Diagnostic question for any future test design**: when this test fails on file-set drift, is the drift from the regression I'm protecting against, or from unrelated content I happened to walk? If the latter, the test scope is wrong, not the data.

2. **Pattern**: when a runtime invariant is scoped to a category (manifest-driven), the test that protects that invariant must walk the same category. Don't broaden test scope "defensively" beyond the invariant — defensive over-scoping creates false positives that train teams to regenerate baselines reflexively.

3. **Performance corollary**: when a test invokes a heavy mechanism per parametrized case, ask if a unit-level test against the underlying function can prove the same invariant. F-248's 14 adversarial init.sh runs collapse to ~14 unit-test invocations.

4. **Spec language tightening**: phrases like "the personalized tree" are ambiguous. Be explicit: "files in `personalized` category from manifest X." Future regression-protection tests should anchor scope in named manifest categories.

### Related Files

- `tests/scripts/test_init_sh_substitution.py` (the over-scoped test)
- `tests/scripts/init_sh_helpers.py:files_in_tree()` (the walk function)
- `tests/fixtures/regenerate-baseline.sh` (the workaround mechanism)
- `.aod/template-manifest.txt` (the category-filter reference)
- `.aod/scripts/bash/template-substitute.sh:aod_template_assert_no_residual` (the symmetric runtime invariant T020 fix)
- Issue #250 (long-term scope refactor + perf concerns)
- Failing CI run: 25314246672 (timeout flake at 300s on macos-latest)
- ADR-038 (placeholder-substitution-strategy)

### Cross-References

- Sibling: T020 over-scope defect (residual scan halted on legitimate non-canonical tokens) — resolved by manifest-category scoping. Same-shape problem on the runtime side; this entry documents the same pattern unaddressed on the test side.
- Ancestry: F-248 T039 (Test-1 first regen — test-fix content drift), T040 (Test-1 second regen — regen script content drift), T046 pre-merge (3rd regen — pipeline artifact drift).
- Recurrence class (referenced in `/aod.deliver` Step 9a): "CI fails on coverage/baseline checks after /aod.deliver commits". The /aod.deliver skill cites two prior incidents in its own institutional history (extract-coverage and manifest-coverage flavors) as Entries 38 and 39 — those are external to this file (this is tachi's first KB entry) but document a sibling class of whole-repo-walk false positives. Test-1 baseline drift is the third member of this class.

---

### Entry 2: F-250 Adversarial Unit Extraction Hot-Fix — Delivery Retrospective

## [Process improvement] - Mid-build CI signal authorizes scope-fence relaxation when original PRD root cause is contradicted

**Date**: 2026-05-04
**Context**: Delivery retrospective for F-250 (Adversarial Unit Extraction Hot-Fix). Estimated: 4-6 hours active. Actual: ~4h11m wall clock (first commit 08:28 EDT → merge 12:39 EDT).

**Problem**:
The original F-250 PRD assumed that extracting 12 adversarial cases from `init.sh` integration runs to direct bash helper invocations would eliminate the `macos-latest` cold-cache 300s timeout class entirely. Mid-build CI run `25325616748` exposed that the assumption was incomplete: the retained 5 init.sh integration invocations (case 13 + 4 other tests) STILL hit the 300s timeout class through module-scoped fixture duplication, and a separate baseline-file-set drift was failing CI on every PR that touched any documentation file.

**Solution**:
Authorize a documented mid-build scope expansion (Phase 6 "Option Z") rather than papering over with retry loops or quick patches. The Phase 6 header in `tasks.md` named the relaxed scope fences explicitly (TC-4 RELAXED for the expansion; FR-019/FR-020 byte-unchanged invariants on `template-substitute.sh` and `init-input.sh` PRESERVED). Eight new tasks (T022-T029) addressed the root causes: session-scoped `init_run` fixture in `tests/scripts/conftest.py` (5 module-scoped duplicates → 1 canonical clone), asymmetric file-set check in `test_init_sh_substitution.py` (drops are FAIL, additions are TOLERATED), substitution-target-only baseline restricted ~600 → ~53 files, `run_init_in_clone` timeout 300s → 900s, pytest `--timeout` 360s → 1080s, workflow `paths:` filter and `pytest` invocation completeness for the 3 new modules. The maintainer directive ("fix ALL issues correctly and completely, no quick patches") served as the explicit authorization.

**Why This Matters**:
Captured during structured delivery retrospective. Mid-build CI run `25325616748` exposed that the original F-250 scope was necessary but insufficient: the retained 5 init.sh integration invocations on `macos-latest` STILL hit the 300s cold-cache timeout class through module-scoped fixture duplication, and a separate baseline-file-set drift was failing CI on every PR that touched any documentation file. Phase 6 Option Z scope expansion was authorized mid-build to address the recurring root cause — TC-4 scope fences explicitly relaxed for the expansion while FR-019/FR-020 byte-unchanged invariants on the bash helpers were preserved.

**Pattern**: When CI evidence contradicts a PRD's root-cause assumption mid-build, the right move is a *documented* scope expansion (named in tasks.md with explicit fence relaxation) rather than (a) retry loops, (b) quick patches that defer the recurrence, or (c) shipping the original scope and filing a follow-up. The audit trail (Phase 6 header) plus preserved byte-unchanged invariants (FR-019/FR-020) makes the relaxation reviewable and bounded — reviewers can confirm the expansion stayed inside the bash-helper scope fence while widening the test-architecture scope.

**Tags**: #retrospective #delivery #process #workflow #ci-architecture

### Related Files:
- `specs/250-adversarial-unit-extraction-hotfix/spec.md` — Feature specification
- `specs/250-adversarial-unit-extraction-hotfix/tasks.md` — Task breakdown including Phase 6 Option Z header
- `specs/250-adversarial-unit-extraction-hotfix/delivery.md` — Delivery retrospective
- `docs/architecture/02_ADRs/ADR-039-test-architecture-fixture-scope-and-asymmetric-baseline.md` — Architecture decision record for the new test-architecture canon

### Cross-References

- Sibling: F-248 Substitution Surface Hardening (Entry 1) — F-250 is the hot-fix that closes the residual flake class F-248 left behind on `macos-latest`. Both features share the bash-helper extraction shape (ADR-038); F-250 adds the test-architecture canon (ADR-039).
- Pattern: "PRD root-cause assumption contradicted by mid-build CI signal" — first instance recorded in this KB. If recurrence is observed, a structured "scope-fence relaxation" template should be added to the AOD playbook.
- Sustained tracking: T021 KPI window (2026-05-04 → 2026-05-18) records the 5-merge sustained green-rate sample.

---

### Entry 3: F-256 Source-Pattern Hardening — Delivery Retrospective

## [CI architecture] - Path-filter and pytest invocation must be updated lock-step when adding new test files to a tracked workflow

**Date**: 2026-05-05
**Feature**: F-256 / F-2 (Source-Pattern Hardening — BLP-02 Wave 2)
**Category**: CI architecture / workflow drift
**Severity**: Medium (test files exist but never run in CI; silent gap until next deliver)

### Symptom

PR #257 shipped 5 new pytest test modules (`test_init_sh_defaults_env.py`, `test_template_config_load_unit.py`, `test_template_config_load_integration.py`, `test_template_git_clone_timeout.py`, `test_template_substitute_lint_no_eval.py`) and 1 new bash helper (`.aod/scripts/bash/template-config-load.sh`) but did NOT update `.github/workflows/tachi-pytest.yml` to wire them into the workflow. The path-filter trigger list and the `python -m pytest ...` invocation both omitted every F-256 file. Build waves passed locally and on PR CI (because the original F-248 file paths were touched, triggering the workflow on the F-248 test set), but the F-256-specific tests would not have run on subsequent PRs that touched only F-256 files. Caught at `/aod.deliver` Step 3 by the devops agent.

### Root Cause (5 Whys validated)

The `tachi-pytest.yml` workflow uses a narrow `paths:` filter (NFR-005 alignment + scope discipline) to avoid burning CI minutes on doc-only edits. When F-256 added a fifth call site (the canonical KV-load primitive), neither the spec/plan/tasks artifacts nor the build waves required that the workflow file be updated as part of the feature. The implicit assumption was "the existing path filter catches the F-256 surface" — partially true (`scripts/init.sh` and `.aod/scripts/bash/template-substitute.sh` are listed), but the new test modules and the new helper file are NOT listed. Lock-step parity between `paths:` and the pytest invocation was an undocumented invariant — F-250 fixed it for the F-248 surface but did not generalize the rule.

### Solution

**Immediate (this delivery)**: devops agent updated `tachi-pytest.yml` during `/aod.deliver` Step 3 to add (a) all 5 F-256 test files + the new helper to the `paths:` filter, (b) `stacks/*/defaults.env` glob (F-256 Site A whitelist surface), (c) the F-256 fixture directories, and (d) all 5 F-256 test modules to the `python -m pytest` invocation. Header comment generalizes the lock-step invariant explicitly: *"when adding a new test file or refactoring a new bash library file, update BOTH the `paths:` trigger list AND the `python -m pytest ...` command in the same commit."*

**Long-term**: future features that add tests covered by an existing tracked workflow should treat the workflow file as a first-class spec artifact. Either (a) name the workflow file in tasks.md as a required edit during the test-authoring task, or (b) add a pre-merge pytest-discovery diff check that asserts every `tests/scripts/test_*.py` referenced by the spec also appears in the pytest invocation of every workflow whose path-filter could match the test file's source-of-truth.

### Prevention

1. **Diagnostic question for any feature that adds tests**: which CI workflows track this code? For each, is the new test file in the `paths:` filter AND the runner invocation? Treat both as one atomic edit.

2. **Pattern**: a `paths:` filter and the runner invocation it gates are coupled. Adding files to one without the other creates a silent gap (path-filter-only addition: tests run but never trigger; invocation-only addition: tests trigger but never run). Both must be in lock-step.

3. **Spec/plan ergonomics**: when a feature adds a new test module covered by an existing workflow, the tasks.md test-authoring task should explicitly enumerate the workflow file edits as a sub-step, not leave it implicit.

4. **Workflow header comments matter**: the F-248 `tachi-pytest.yml` header comment was already informative (NFR-001 bash compatibility, F-250 timeout lock-step). Adding the lock-step parity rule to the header makes future additions self-documenting — devops noticed during `/aod.deliver` because the existing header signaled the invariant intent.

### Related Files

- `.github/workflows/tachi-pytest.yml` (the workflow file fixed)
- `specs/256-source-pattern-hardening/tasks.md` (the build plan that omitted the workflow edit)
- `tests/scripts/test_template_config_load_unit.py` + 4 sibling test modules (the affected tests)
- `.aod/scripts/bash/template-config-load.sh` (the affected helper)
- `docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md` (F-256 ADR — references the test surface)
- F-250 lock-step ancestry: `specs/250-adversarial-unit-extraction-hotfix/spec.md` (where the lock-step invariant was first surfaced for F-248)

### Cross-References

- **Sibling**: Entry 1 (F-248) — F-256 inherits the same source-pattern-hardening pattern (Site A-D refactor) but introduces a new helper file class (canonical KV-load primitive). The lock-step invariant generalizes from F-250's hot-fix scope.
- **Ancestor**: Entry 2 (F-250) — F-250 fixed lock-step for the F-248 surface (`paths:` + pytest invocation parity). F-256 demonstrates the rule needed generalization, not just per-feature application.
- **Pattern class**: "CI workflow drift across features that share a tracked surface" — Entries 1, 2, 3 all involve the same workflow (`tachi-pytest.yml`). Each successive feature reveals a new way the workflow can drift; each retrospective tightens the invariant. F-256's lesson promotes the rule from a per-incident fix to a documented pre-merge check.
- **Pattern**: "agent-accelerated build compresses estimated 9.5d to ~1d wall-clock" — F-256's ~1-day delivery against a 9.5d PRD estimate is an artifact of the agent-orchestrated build cadence (parallel waves, automated test authoring, multi-stream gating). Future PRD timeline estimates should distinguish "agent-orchestrated wall-clock" from "human-equivalent engineering effort."

---

## Bug Fixes

*No entries yet. Use `/kb-create` to add the first bug fix.*
