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

## Bug Fixes

*No entries yet. Use `/kb-create` to add the first bug fix.*
