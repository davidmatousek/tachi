# Institutional Knowledge - {{PROJECT_NAME}}

**Project**: {{PROJECT_NAME}} - {{PROJECT_DESCRIPTION}}
**Purpose**: Capture learnings, patterns, and solutions to prevent repeated mistakes
**Created**: {{PROJECT_START_DATE}}
**Last Updated**: {{CURRENT_DATE}}

**Entry Count**: 1 / 20 (KB System Upgrade triggers at 20 — schedule review)
**Last Review**: 2026-05-04 (F-248 retrospective)
**Status**: ✅ Manual mode (file-based)

---

## Overview

This file stores institutional knowledge for {{PROJECT_NAME}} development. It's used by:
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

### Entry 4: F-3 SECURITY.md and Private Disclosure Channel — Delivery Retrospective

## [Technical pattern] - Documentation-only DoD via Principle VII §Exceptions; GitHub-canonical SECURITY.md template; CHANGELOG sibling-h3 BLP-02-cluster placement

**Date**: 2026-05-08
**Feature**: F-3 (SECURITY.md and Private Disclosure Channel — BLP-02 Wave 3)
**Category**: Technical pattern / governance / documentation discipline
**Severity**: Informational (no incident — pattern capture)

### Context

F-3 closed TACHI-VULN-05abc41ad4cc (INFO, A05 Security Misconfiguration) by rewriting `SECURITY.md` to GitHub-canonical 5-section structure, enabling the Private Vulnerability Reporting toggle, adding a `README.md` pointer, and appending a `CHANGELOG.md` `## Unreleased` entry. Pure docs + repo-setting; zero code change. Estimated ≤4h active maintainer time per PRD SC-008; delivered same-day with 23/25 tasks complete (T024 + T025 are `/aod.deliver`-time only). Build report flagged two carry-forward IK notes: N-2 (D-6 sequence variance) and N-4 (CHANGELOG blueprint placement deviation).

### Pattern 1: Documentation-only DoD via Principle VII §Exceptions

**Problem**: tachi's Constitution Principle VI mandates testing-excellence coverage thresholds, but a feature that touches no source code has nothing to test in the unit/integration sense. Principle VII §Exceptions allows the exemption ("Documentation-only changes may not require production deployment"), but the application path needs to be demonstrable.

**Solution**: F-3's plan.md Constitution Check section explicitly invokes the §Exceptions clause and maps all three Principle VII §Non-Negotiable Validation Steps to non-test verification: (1) ✅ Pushed via squash-merge; (2) ✅ Tested via post-merge `/security` re-scan + manual UI inspections (FR-010 toggle, FR-011 button, FR-012 URL form); (3) ✅ User-validated via PR review + post-merge button-visible check. The build's `test-results/summary.json` records `waves_skipped: 15` with rationale citing "Constitution Principle VII §Exceptions and Principle VI testing-excellence exemption noted in plan.md."

**Apply when**: A feature is markdown/policy/repo-setting only, has no executable surface, and cannot be tested by unit/integration runners. Document the exemption in plan.md Constitution Check; map verification to post-merge instrumentation (`/security` re-scan for A05 closures; manual UI inspections for repo-setting changes); record `waves_tested: 0` with explicit `skip_reason` in `test-results/summary.json`. Do NOT silently bypass — the rationale-as-data is the auditable trail.

### Pattern 2: GitHub-canonical SECURITY.md 5-section template

**Problem**: Pre-F-3 `SECURITY.md` was 40 LOC, used non-canonical section names, and lacked procurement-defensible content (vendor disclosure policy, SLA, scope/out-of-scope, supported-versions worked example). Procurement reviewers running CAIQ/SIG-Lite rubrics couldn't mark the disclosure-policy + supported-versions line items GREEN without manual interpretation.

**Solution**: F-3 rewrites `SECURITY.md` to the GitHub-canonical 5-section structure: **Supported Versions** → **Reporting a Vulnerability** → **What to expect** → **Scope** → **Out-of-scope**. Section names match GitHub Docs verbatim where prescribed. Section 1 includes a worked example referencing the latest tag (verified at write-time per FR-003 cross-check command). Section 2 surfaces the *Report a vulnerability* button as primary affordance with URL fallback + public-Issue prohibition + R-2 toggle-dependency footer. Section 3 contains the 5-business-day SLA verbatim + assessment-within-1-week + fix-timeline-after-assessment + credit clause. Section 4 enumerates in-scope tachi paths; Section 5 enumerates out-of-scope routing (Claude Code → Anthropic; third-party MCP → maintainers; adopter personalization → adopter; etc.). Total: 51 LOC (more compact than initial 80 LOC estimate).

**Apply when**: Any tachi-derivative or AOD-Kit-derivative project needs a procurement-defensible SECURITY.md. Reuse the section ordering verbatim. Substitute the project-specific in-scope path enumeration (Section 4) and out-of-scope routing (Section 5). Preserve the 5-business-day SLA as the single-maintainer floor; raise voluntarily for critical reports without contractually committing.

### Pattern 3: CHANGELOG sibling-h3 BLP-02-cluster placement (N-4 carry-forward)

**Problem**: The plan.md blueprint placed the F-3 CHANGELOG entry under `## Unreleased → ### Features` as a top-level subsection. The F-2 precedent (Entry 3 sibling) instead used a sibling `### {Feature title} (BLP-02 F-N)` heading at the same level as `### Features` and `### Bug Fixes`, grouping all BLP-02 features as a cluster. The build T013 result deviated from the blueprint and matched the F-2 precedent: F-3's `### SECURITY.md and private disclosure channel (BLP-02 F-3)` heading sits between `### Hardened config-file load (BLP-02 F-2)` and `### Bug Fixes` rather than under `### Features`. Architect P2 checkpoint flagged this as N-4 minor.

**Solution**: Sibling-h3 placement is the correct pattern for multi-feature initiatives like BLP-02 — it visually clusters related work in CHANGELOG and avoids fragmenting BLP-02 entries across `### Features` (where BLP-02 F-1 + F-3 would land) and `### Bug Fixes` (where the F-250 hot-fix landed). The blueprint placement was the deviation; the build's actual placement is the keeper.

**Apply when**: Adding a CHANGELOG entry for any feature in a multi-feature initiative (BLP-02, BLP-03, future BLPs). Use a sibling h3 heading `### {Feature title} ({INITIATIVE} F-N)` at the same level as `### Features`/`### Bug Fixes`. Group consecutive same-initiative entries together. Future blueprints in plan.md should specify sibling-h3-cluster placement explicitly to avoid re-flagging this deviation.

### Why This Matters

Captured during structured `/aod.deliver` retrospective for F-3. Smooth — no major surprises. The three patterns are reusable: Pattern 1 unblocks future docs-only features (e.g., LICENSE updates, contributing-guide refreshes) from spurious test-coverage gates. Pattern 2 establishes the procurement-defensible SECURITY.md baseline reusable across tachi/AOD-Kit/derivative projects. Pattern 3 clarifies the CHANGELOG-cluster convention for the remaining BLP-02 features (Wave 4 + Wave 5) and future BLPs, removing the architect-N-4-style deviation from the next plan.md blueprint.

**Tags**: #retrospective #delivery #architecture #pattern #docs-only #governance #security #changelog

### Related Files

- `specs/272-security-md-disclosure/spec.md` — Feature specification (5 user stories, 14 FRs, 12/12 ACs)
- `specs/272-security-md-disclosure/plan.md` — Implementation plan (Constitution Check Principle VII §Exceptions invocation)
- `specs/272-security-md-disclosure/tasks.md` — Task breakdown (T001–T025; T024+T025 deferred to /aod.deliver)
- `specs/272-security-md-disclosure/test-results/summary.json` — Documented skip rationale for Principle VII §Exceptions
- `SECURITY.md` — The 51-LOC GitHub-canonical 5-section rewrite
- `CHANGELOG.md` — F-3 sibling-h3 BLP-02-cluster placement (the N-4 keeper pattern)
- `README.md` — `## Community` section AC-12 one-line pointer
- `.aod/results/security-scan.md` — Post-merge `/security` re-scan recording `TACHI-VULN-05abc41ad4cc → REMEDIATED`

### Cross-References

- **Sibling**: Entry 3 (F-2 / F-256 Source-Pattern Hardening) — F-3 follows F-2 in BLP-02 Wave sequence; CHANGELOG sibling-h3 placement (Pattern 3) was first established by F-2's entry style and is now codified as the BLP-02-cluster convention.
- **Ancestor**: Entry 1 (F-248) — F-3 closes the LinkedIn-disclosure-pattern that F-248's RCA implicitly depended on (private channel availability); F-3 surfaces the channel as a procurement-defensible artifact.
- **Pattern class**: "Documentation-as-feature" — F-3 demonstrates that a docs-only delivery can satisfy DoD, close a `/security` finding (TACHI-VULN-05abc41ad4cc), trigger a release-please cycle (#274 chore(main): release 4.33.0), and yield procurement-rubric value — without writing a single line of code.
- **Initiative**: BLP-02 enterprise-hardening Wave 3 (3-of-5 features delivered). Predecessors: F-1 (#248) Wave 1 + F-250 hot-fix follow-on; F-2 (#256) Wave 2.
- **Follow-up Issues**: #275 (AC-13 PVR-toggle posture probe), #276 (AC-14 release-please manifest-vs-tag investigation) — both filed at /aod.tasks-time, traced through delivery.

---

### Entry 5: F-4 Claude Permissions Baseline — Delivery Retrospective

## [Technical pattern] - Cross-list precedence + transitive subdomain collapse pattern; built-in read-only auto-approve preserved without explicit allow

**Date**: 2026-05-09
**Feature**: F-4 (Claude Permissions Baseline — BLP-02 Wave 4)
**Category**: Technical pattern / permissions design / verification recipe
**Severity**: Informational (no incident — pattern capture; posture-gap closure not vuln closure)

### Context

F-4 closed a posture gap (no documented permissions baseline + permissive default ruleset) named in Daniel Wood's 2026-05-02 LinkedIn enterprise-developer-environments thread as a load-bearing prerequisite for SecOps-reviewed managed environments. Zero `/security` `vuln_id` was closed by F-4 — this is posture-gap closure, NOT vulnerability closure (a class distinction worth preserving). Deliverables: curated `.claude/settings.json` baseline (~80 LOC after Cat-1 dedup) + `docs/standards/CLAUDE_PERMISSIONS.md` self-contained policy decision log (~250 LOC) + ADR-041 (~100 LOC, 6 alternatives-considered) + CHANGELOG sibling-h3 BLP-02-cluster entry. PRD estimate: ~8-9h active envelope / next-day wall-clock target. Actual: branch created 2026-05-08T22:04:54Z (PRD landing), squash-merged 2026-05-09T16:24:37Z → ~22h22m wall-clock, on target. Release-please PR #279 `chore(main): release 4.34.0` opened ~23s post-squash-merge (within FR-013 ~30s SLO; F-212 recovery flow not triggered). Post-merge `/security` re-scan PASSED (zero new HIGH/MEDIUM; F-4 change set has zero SAST-eligible files and zero SCA-eligible manifests). Two follow-up Issues filed at /aod.tasks-time per AC-15/AC-16 nice-to-haves: #280 (pre-commit hook for `.claude/settings.json` jq-validity + AC-2 cross-check, ICE I:5 C:7 E:8) and #281 (CI integration for the F-4 verification recipe, ICE I:6 C:6 E:7).

### Pattern 1: Cross-list deny → ask → allow first-match-wins precedence

**Problem**: A naive permissions baseline either makes every rule explicit (verbose, brittle to maintain) or relies on broad allow patterns that silently approve narrower destructive operations. The PRD's R-1 risk explicitly flagged the case where `Bash(git push:*)` allow could shadow a narrower `Bash(git push --force:*)` deny intent — a classic ordering-vs-specificity tension.

**Solution**: Claude Code permissions evaluate as `deny → ask → allow` first-match-wins across both project `.claude/settings.json` AND local `.claude/settings.local.json` (cross-file). The narrower `Bash(git push --force:*)` deny rule fires before evaluation reaches the broader `Bash(git push:*)` allow — verified at T011 [MANUAL-ONLY] enumeration pre-commit and re-verified at T026 post-merge defense-in-depth probe. AC-12 cross-file probe at T015 further confirms a project-level deny rule shadows any local `.claude/settings.local.json` allow that conflicts (the "settings.local.json cannot override a project deny" mechanic). The permissions table in `docs/standards/CLAUDE_PERMISSIONS.md` documents this precedence with two worked examples so adopters understand the override path is fork-and-edit (Path 2) or explicit project-rule edit (Path 3), not local-file allow.

**Apply when**: Authoring or auditing any `.claude/settings.json` baseline. Always include at least one paired `Bash(<broad-pattern>:*)` allow + `Bash(<narrower-destructive-variant>:*)` deny to test the precedence at probe time. Document the precedence in a §Settings-Precedence section with at least one cross-list (deny shadows allow) + one cross-file (project deny shadows local allow) worked example.

### Pattern 2: WebFetch transitive subdomain collapse (AC-7 ANOMALY)

**Problem**: When designing a network host-allowlist, the intuitive expectation is that `WebFetch(domain:github.com)` matches *only* `github.com` and that subdomains require their own explicit rules (`WebFetch(domain:gist.github.com)`, etc.). The PRD's R-7 risk hypothesized the *opposite* mechanic — that subdomains might require explicit entries. T018 verification probed this directly with `WebFetch https://gist.github.com/...` and confirmed the surprising mechanic: gist.github.com auto-approved under the parent rule, demonstrating that `WebFetch(domain:X)` matches transitively on subdomains. The architect's HIGH-2 v1.1 cascade incorporated this by removing 7 redundant github-family explicit entries and adding an inline AC-7 ANOMALY note. Issues #15260, #11972, and #1217 in the Claude Code GitHub repo reference this same behavior.

**Solution**: Document the transitive-collapse mechanic INLINE in `docs/standards/CLAUDE_PERMISSIONS.md` §AC-7-ANOMALY so future maintainers don't mistake it for a regression. The 19-domain WebFetch host-allowlist relies on this mechanic — `github.com` covers `gist.github.com` + `raw.githubusercontent.com` + `api.github.com` + similar — which keeps the rule count tight (19) instead of bloated (40+). Compaction option per W11 T018 Option A: 7 github-family explicit entries can be subsumed by the parent `WebFetch(domain:github.com)` rule via transitive collapse; F-4 ships the compacted form.

**Apply when**: Designing any `WebFetch(domain:*)` allowlist. Test transitive collapse with at least one parent + subdomain pair before sizing the allowlist. Document the AC-7 ANOMALY mechanic inline next to the WebFetch section so adopters considering subdomain-explicit rules understand the parent rule subsumes them. When upstream Claude Code releases change subdomain-matching behavior, this section is the regression-detection hook.

### Pattern 3: Built-in read-only auto-approve preserved without explicit allow

**Problem**: A defensive instinct is to add explicit allow rules for every read-only operation (`Bash(git status)`, `Bash(ls)`, `Bash(cat:*)`, etc.) to ensure they auto-approve in agentic mode. This bloats the baseline (potentially 50+ extra entries) and risks divergence between the explicit list and Claude Code's actual built-in read-only set as upstream releases evolve.

**Solution**: Claude Code maintains a built-in read-only auto-approve list that operates OUTSIDE the explicit `permissions.allow` array. `Bash(git status)` auto-approves with NO matching rule in `.claude/settings.json` — confirmed at T009 pre-commit no-rule probe (executed `git status` in a session loaded with the curated baseline; harness returned the output directly with no permission prompt) AND at T025 post-merge defense-in-depth re-run (same probe, same outcome on a fresh post-merge clone). The PRD's R-10 risk hypothesized that explicit allow rules might *shadow* built-in read-only auto-approve — but the no-rule probe disproves that: built-in auto-approve fires when no explicit rule matches (allow OR deny). The permissions baseline therefore EXCLUDES read-only operations from the explicit allow array and lets the built-in mechanic handle them, keeping the baseline at ~80 LOC instead of 130+.

**Apply when**: Building any `.claude/settings.json` baseline. Verify built-in read-only preservation with an explicit no-rule probe at /aod.build verification time AND post-merge defense-in-depth (T009 + T025 pattern). When upstream Claude Code changes the built-in read-only set, the no-rule probe is the regression-detection hook. Adopters who want to *deny* a normally-built-in read-only operation must add it explicitly to `permissions.deny` (the deny→ask→allow precedence applies; built-in auto-approve does NOT shadow explicit deny).

### Lessons from Estimation vs. Reality

- PRD estimate ~8-9h active / next-day wall-clock held within ~1h. ICE I:8 C:7 E:7 was accurate.
- Single biggest scope risk was R-7 (subdomain matching) — flipped from "explicit subdomains required" to "transitive collapse" at T018, but the architect's v1.1 cascade had already preemptively reconciled the rule set, so the build-stage flip was zero-cost.
- The W11 T018 AC-7 ANOMALY confirmation opened the AC-15 + AC-16 follow-up surface (Issues #280 + #281) — reuse the same pattern when probing for hidden mechanics: capture the anomaly, file an Issue at task-time with ICE rough-estimate, and don't expand the current feature scope to absorb it.

### Cross-References

- **Sibling**: Entry 4 (F-3 SECURITY.md and Private Disclosure Channel) — F-4 follows F-3 in BLP-02 Wave sequence; both close BLP-02 enterprise-hardening posture gaps named in the same 2026-05-02 Daniel Wood thread; F-3 closes the *disclosure-channel* half, F-4 closes the *deployment-readiness* half. Both reuse the docs-only DoD pattern (Entry 4 Pattern 1) — F-4's Constitution Check invokes the same Principle VII §Exceptions clause that F-3 codified.
- **Ancestor**: Entry 4 (F-3) — Pattern 3 (CHANGELOG sibling-h3 BLP-02-cluster placement) carry-forward from N-4. F-4's CHANGELOG entry was authored at /aod.build W9 T017 with the sibling-h3 BLP-02-cluster placement preserved per N-4.
- **Pattern class**: "Posture-gap closure" — F-4 closes ZERO `/security` `vuln_id` (this is the new pattern class introduced in BLP-02). The class distinction matters for retrospective rubric metrics: not every BLP-02 feature closes a vuln_id, but every BLP-02 feature closes an audit-policy-relevant posture gap. Procurement-defensible rubric value = vuln_id closure UNION posture-gap closure.
- **Initiative**: BLP-02 enterprise-hardening Wave 4 (4-of-5 features delivered). Predecessors: F-1 (#248) Wave 1 + F-250 hot-fix follow-on; F-2 (#256) Wave 2; F-3 (#272) Wave 3. Sole remaining: F-5 Pre-commit Secret-Scanning + ADR-042. ADRs accepted: 038, 040, 041 (041 from this feature).
- **Follow-up Issues**: #280 (AC-15 pre-commit hook for `.claude/settings.json` jq-validity + AC-2 cross-check; ICE I:5 C:7 E:8) and #281 (AC-16 CI integration for the F-4 verification recipe; ICE I:6 C:6 E:7) — both filed at /aod.tasks-time, traced through delivery.

---

### Entry 6: F-292 Output-Integrity Cross-Sink Refinement — Delivery Retrospective

## [Process improvement] - Enrichment-branch features that modify detection-tier files MUST update the F-142 zero-edit invariant test in the same change

**Date**: 2026-05-14
**Feature**: F-292 (Output-Integrity Cross-Sink Refinement — 8th Heuristic A enrichment execution at same-agent scope within F-1's host)
**Category**: TEST infrastructure / planning gap
**Severity**: Medium (caught pre-merge by pytest; would have failed CI if merged unchanged)

### Symptom

`pytest tests/scripts/test_backward_compatibility.py::test_feature_142_zero_edit_invariant_on_detection_agents` failed mid-build with:

```
AssertionError: Zero-edit invariant violated (ADR-026 Decision 1). The following
detection-tier files were modified on branch '292-output-integrity-cross-sink-refinement'
relative to main: ['.claude/agents/tachi/output-integrity.md',
'.claude/skills/tachi-output-integrity/references/detection-patterns.md'].
```

The two modified files were the exact same surfaces F-292 was designed to edit (Heuristic A enrichment of F-1's `output-integrity` agent host + companion detection-patterns.md). The implementation was correct; the test was unintentionally fencing the implementation out.

### Root Cause (5 Whys validated)

1. **Why did the test fire on F-292's branch?** Because `DETECTION_AGENT_PATHS` still contained `output-integrity.md` (the F-1 agent file) as a protected zero-edit target, and `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` did not yet contain the companion `tachi-output-integrity/references/detection-patterns.md`.
2. **Why were those carve-outs missing?** Because F-292's spec, plan, tasks, and architect review all focused on the new content (Cat 6, Cross-Agent Handoff Sinks, ADR-045, baseline) and did not enumerate the test-list update as a build deliverable.
3. **Why did planning miss it?** Because the prior 7 Heuristic A enrichments (F-3, F-5, F-6, F-7, F-241 Stream 1) had each updated the test list, but only F-241's update is *documented in the test file's docblock* (lines 184-196). F-292 was the first enrichment to touch F-1's host specifically — and the docblock at lines 191-200 explicitly named F-1 + F-2 as "remaining protected" without flagging that F-292 would need to carve out F-1.
4. **Why did the architect review miss it?** Because the architect's review scope (codified in `.aod/results/architect-final.md`) focused on plan-to-implementation fidelity, ADR structural soundness, and cross-link emission risk — not on cross-cutting test infrastructure that gates the F-142 invariant.
5. **Why was the cross-cutting test infrastructure not in the plan checklist?** Because the AOD plan template lacks a "test-list updates required for detection-tier modifications" prompt. The carve-out pattern is documented in the test file's own docblock, but adopters reading spec.md / plan.md / tasks.md do not necessarily read the test file.

### Solution

**Immediate (in this build)**: F-292 build session added the carve-out commit `test(292): F-292 carve-out in zero-edit invariant test [T035]`:

1. Moved `.claude/agents/tachi/output-integrity.md` OUT of `DETECTION_AGENT_PATHS` (now contains only `misinformation.md`).
2. Added `DETECTION_PATTERN_REF_F292_OUTPUT_INTEGRITY_HOST` constant and added it to the `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` frozenset.
3. Updated assert from `== 2` to `== 1` with explanatory message.
4. Added docblock comment documenting F-292 as the 8th Heuristic A enrichment execution at same-agent scope.

Verification: pytest now reports 13 passed / 1 documented skip; SC-004 (5 non-qualifying baselines byte-identical) empirically satisfied.

**Pattern (for future enrichment branches)**: Any branch that edits a file in `DETECTION_AGENT_PATHS` MUST in the same change:
1. Remove that path from `DETECTION_AGENT_PATHS`.
2. Add a new `DETECTION_PATTERN_REF_F{NNN}_<HOST>_HOST` constant for the companion `.md`.
3. Add the new constant to `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS`.
4. Update the assert count and the docblock.

### Prevention

1. **Plan-checklist amendment**: Add to `/aod.plan` and `/aod.tasks` checklist for features that touch `.claude/agents/tachi/<agent>.md` or `.claude/skills/tachi-<agent>/references/<*>.md`: "Does this feature need a `DETECTION_AGENT_PATHS` / `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` carve-out task in `tests/scripts/test_backward_compatibility.py`?" Default answer for any Heuristic A enrichment: YES.

2. **Architect review heuristic**: When reviewing a plan/tasks that touches `.claude/agents/tachi/` or `.claude/skills/tachi-*/`, the architect should explicitly check whether the F-142 zero-edit invariant test needs a carve-out task — even if the agent file edit is "navigational only" (≤10 line diff).

3. **Test-file docblock improvement**: The docblock at `test_backward_compatibility.py:178-196` should explicitly say "When adding a new Heuristic A enrichment that touches F-1 (`output-integrity`) or F-2 (`misinformation`), move the host file OUT of `DETECTION_AGENT_PATHS` and ADD the companion to `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` — same pattern as F-241 for prompt-injection / agent-autonomy."

4. **Build-stage signal**: `/aod.build` should run `tests/scripts/test_backward_compatibility.py` as part of the post-wave test execution, not just when `.py` source files changed. The "no code files changed" precondition for skipping post-wave tests (per /aod.build Step 4.5a) should NOT apply to backward-compat regression tests — those guard *the whole repo*, not just the changed code files.

## Patterns

### Pattern 1: Cat 6 (new top-level pattern category) when CWE differs from parent category primary

**Problem**: When a new pattern surface fits broadly within an existing category but has a distinct primary CWE pinning, the natural instinct is to extend the existing category as a sub-class. Doing so masks the CWE distinction and creates downstream confusion when adopters reconcile findings against industry taxonomies.

**Solution**: Promote the new pattern surface to its own top-level category when the primary CWE differs from the existing category's primary CWE. F-292 Cat 6 (Vector / Search-DSL Injection) has CWE-943 (Improper Neutralization of Special Elements in Data Query Logic) as primary — distinct from Cat 2's CWE-89 (SQL Injection). The cleaner category boundary at the CWE-pinning level enables future expansion to additional structured-query languages (GraphQL injection, NoSQL operator injection, LDAP, XQuery, XPath, DQL — all CWE-943 family) without compounding the Cat 2 sub-class structure.

**Apply when**: Designing a new pattern surface that broadly fits within an existing category. If the primary CWE you would pin differs from the existing category's primary CWE, default to a new top-level category. Document the disambiguation in an ADR D7-style "Pattern Category Disambiguation" decision (see ADR-045 D7 Invariant A).

### Pattern 2: Cross-link prose as navigational-only signal-class boundary disambiguation

**Problem**: Multi-agent architectures surface findings from multiple threat agents on overlapping flows. When LLM output flows into a tool-call argument or durable memory write, three different agents may legitimately emit findings (`output-integrity` on encoding/sanitization, `tool-abuse` on tool-argument injection, `data-poisoning` on durable-memory writes). Adopters reading three disjoint findings on the same architectural surface need a way to reason about the boundary.

**Solution**: Add a Cross-Agent Handoff Sinks navigational subsection to the *source* agent's pattern catalog with these required elements:
1. A boundary phrase that makes the principle explicit (e.g., "harmless as text, dangerous as tool argument or memory entry").
2. Cross-link prose to each adjacent agent's owning file, naming the OWASP framework anchor each agent owns (LLM06 / ASI04 for tool-abuse; ASI06 NOT LLM04 for data-poisoning).
3. An explicit no-emission statement: "This agent does NOT emit findings on those handoff flows."
4. A one-way navigational invariant lock-paragraph stating that the subsection adds NO new trigger keywords and NO new downstream-sink-indicators — the existing both-signal workflow enforces zero emissions from the prose alone.
5. A mitigation pattern with a worked schema example (when applicable). F-292's Memory-Promotion Rules schema (`promotable_keys` + `value_schema` + `tenant_scope`) is the institutional-knowledge seed for any future agent introducing a durable-write surface.

The cross-link target agents remain unmodified — the navigational pointer flows one direction only (OUT of the source agent's catalog).

**Apply when**: A pattern catalog surfaces a signal class that has adjacent-agent overlap. Confirm the cross-link is navigational only by re-running an existing multi-agent baseline (e.g., `agentic-app/`) under `SOURCE_DATE_EPOCH=1700000000` and verifying zero new findings emerge from the source agent on the prose alone (SC-003 byte-identity check).

### Pattern 3: Memory-Promotion Rules as institutional-knowledge seed

**Problem**: Future agents introducing durable-write surfaces will need a canonical mitigation pattern for LLM-output → durable-memory promotion. Each agent reinventing the pattern fragments the institutional knowledge and risks divergent schemas.

**Solution**: F-292's Memory-Promotion Rules worked schema example codifies the canonical three-field structure:
- `promotable_keys`: allowlist enum of which memory-store keys the agent may write
- `value_schema`: reference to a JSON-schema validating the shape of permitted values
- `tenant_scope`: pin binding the write to the requesting tenant's namespace

Plus optional layered controls:
- `staging_buffer` (A-MEMGUARD pattern, arXiv 2510.02373)
- `human_approval_gate` (high-trust memory categories)

Industry anchors (OWASP ASI06 Memory & Context Poisoning, OWASP Agent Memory Guard, AWS Bedrock AgentCore Memory, Vertex AI Memory Bank) are explicit citations. The pattern is currently inline in `detection-patterns.md` Cross-Agent Handoff Sinks subsection per ADR-045 D4 (single-use surface today); future reuse from adjacent agents can lift it to a separate skill-reference file at that point.

**Apply when**: Designing a new agent or feature that introduces a durable-memory-write surface. Cite OWASP ASI06 (NOT LLM04 — LLM04 is training-time data poisoning, a distinct surface). Reference the F-292 schema as the starting point; extend with additional optional layered controls if needed.

### Lessons from Estimation vs. Reality

- PRD/plan/tasks estimate ~1.5 working days active; build session completed implementation in a single session.
- The biggest miss was the F-241-precedent test-list carve-out (T035 retrospective task added). Estimated 0 effort, actual ~15 min — caught by pytest mid-build, fixed cleanly. The 5-Whys analysis above traces back to a plan-checklist gap that the prevention section proposes amending.
- The 8th Heuristic A enrichment execution is the FIRST same-agent enrichment within F-1's host (vs F-3 / F-5 / F-6 / F-7 / F-241 which were cross-agent enrichments hitting other hosts). This finer-grained scope is structurally novel — future same-agent enrichments on F-2 (`misinformation`) host can follow ADR-045's structure and reuse the same test-list carve-out pattern.

### Cross-References

- **Direct precedent**: Entry 1-5 (BLP-02 Wave 1–4 enrichments). F-292 is structurally a Heuristic A enrichment at the same scope as those, BUT — distinct from BLP-02 features which closed enterprise-hardening posture gaps — F-292 closes coverage gaps in F-1's pattern catalog surfaced by a first-time community contributor (@armorer-labs, discussion #179).
- **Ancestor**: F-1 / ADR-030 (`output-integrity` agent baseline). F-292 enriches the same agent additively per ADR-023 D3 + ADR-030 D2 + ADR-045 D1.
- **Sibling**: F-241 Stream 1 (F-A3 populator wiring). Same `DETECTION_AGENT_PATHS` carve-out pattern (F-241 carved out `prompt-injection` + `agent-autonomy`; F-292 carves out `output-integrity`).
- **Pattern class**: "Community-merge precedent enrichment" — F-260 (@north-echo PR #262, v4.31.0) was the canonical 7-stage attribution playbook (comment → maintainer gap-analysis → PRD → spec → plan → tasks → ADR → implementation → CHANGELOG → discussion delivery comment). F-292 reuses the playbook verbatim with @armorer-labs attribution.
- **Follow-ups**: 4 plan-checklist amendments proposed in Prevention section above (architect heuristic, test-file docblock, build-stage signal, plan-checklist prompt for detection-tier touches).

---

### Entry 7: F-292 Delivery — Post-Merge Task Accountability

## [Process improvement] - Move post-merge community-engagement and SLA-driven tasks into a dedicated follow-up issue at /aod.deliver time

**Date**: 2026-05-14
**Context**: Delivery retrospective for F-292 Output-Integrity Cross-Sink Refinement. Estimated: 1-2 days. Actual: 1 day (same-day spec → plan → build → deliver). Surprise: "a lot of postponed tasks" — 11 of 36 tasks remained `[ ]` at /aod.deliver entry, all MANUAL-ONLY post-merge or SLA-driven (T005, T017, T019–T024, T026, T031, T034).

**Problem**:
tasks.md mixed two distinct task classes — (a) build-time technical work that /aod.build must complete, and (b) post-merge / SLA-driven / community-engagement work that can only execute after squash-merge or on a future calendar date (T+5d courtesy nudge, T+7d SLA breach checkpoint). At /aod.deliver entry, /aod.build's "10/36 tasks unchecked" signal looked like incomplete work, when the real status was "build phase done, community phase pending". This forced manual judgment at deliver-time about which incomplete tasks were genuine blockers vs. expected post-merge follow-ups.

**Solution**:
At /aod.deliver time, generate a dedicated follow-up GitHub Issue that captures every remaining `[ ]` task with MANUAL-ONLY, [POST-MERGE], or calendar-anchored markers, and link it from the closing feature's delivery document. This:
1. Keeps the closing feature's Issue cleanly transitioning to `stage:done` without ambiguity about residual work.
2. Creates real accountability for SLA-driven actions (T+5d nudge, T+7d SLA breach) via a tracked Issue rather than a buried tasks.md checkbox.
3. Enables /schedule or cron follow-ups against a stable Issue number for calendar-bound work.
4. Surfaces the "post-merge tail" pattern as a first-class deliverable category, not as residual debt.

**Why This Matters**:
F-292 reused F-260's community-merge precedent (4 mechanical artifacts: CHANGELOG form, 7-day SLA, comment-first-give-choice, Co-Authored-By trailer) and inherited F-260's "long post-merge tail" pattern. Every future community-merge feature will have the same tail. Codifying the follow-up-issue pattern at /aod.deliver time prevents the surprise from recurring and makes the SLA-driven work tractable.

**Tags**: #retrospective #delivery #process #workflow #community-merge

### Related Files:
- `specs/292-output-integrity-cross-sink-refinement/spec.md` — Feature specification
- `specs/292-output-integrity-cross-sink-refinement/tasks.md` — Task breakdown (T005, T017, T019–T024, T026, T031 marked MANUAL-ONLY or POST-MERGE)
- `docs/architecture/02_ADRs/ADR-045-output-integrity-cross-sink-refinement.md` — Architecture decision (8th Heuristic A enrichment)
- KB Entry 6 — F-292 carve-out planning gap (the build-time twin of this delivery-time lesson)

### Lineage

- **Direct precedent**: F-260 (@north-echo, v4.31.0) — first community-merge feature; same post-merge tail (CHANGELOG sync, attribution, discussion delivery comment, SLA tracking). F-260's tail was handled ad-hoc; F-292 surfaces the pattern explicitly.
- **Pattern class**: "Post-merge tail as first-class deliverable category" — applies to any feature with community-attribution, SLA-driven actions, release-please verification, or calendar-anchored follow-ups.
- **Follow-up proposal**: Amend the /aod.deliver skill to auto-generate the follow-up Issue when residual `[ ]` tasks remain and any are marked MANUAL-ONLY, [POST-MERGE], or contain calendar-anchored markers (e.g., "T+5d", "T+7d", "within 24h").

---

### Entry 8: F-296 50/50 OWASP Coverage Distribution Launch (BLP-04 F-1) — Delivery Retrospective

**Date**: 2026-05-30 | **Category**: Process / Release Discipline | **Feature**: F-296 (BLP-04 Wave 1) | **Issue**: #296 (closed)

**Context**: F-296 packaged and distributed the already-achieved 50/50 five-framework OWASP coverage milestone (README 50/50 hero + canonical `docs/standards/OWASP_COVERAGE.md`, evergreen poster, LinkedIn post, CISO/VP profile refresh, Discussion #179 close). 37/37 tasks; closed 2026-05-29, ~6 days ahead of the 2026-06-04 target, zero slips.

**Lesson 1 — Internal strategy docs have exactly one canonical home.** Per `_internal/CLAUDE.md`, internal strategy/planning docs live only in the repo-root `_internal/` directory. A feature-scoped copy created under `docs/product/_internal/strategy/BLP-04-adoption-push.md` during the build became a duplicate that had to be detected and consolidated into the canonical path at closeout (the stray copy's unique execution bindings were folded into the canonical doc's Scope History before deletion). **Prevention**: when a build step needs an internal strategy doc, write/extend the canonical `_internal/` file directly — never create a feature-namespaced copy under `docs/`.

**Lesson 2 — Distribution-launch features are docs-only by design; a skipped release is correct, not a defect.** Every F-296 PR used `docs(296):` (a hidden-bump type). Release-please correctly opened no release PR (T029). The F-212 empty-`feat(NNN):` marker-commit recovery flow was deliberately **not** invoked, and the carve-out was recorded in project memory (`feedback_aod_deliver_release_gate.md`, T028). **Prevention**: before forcing a release marker at `/aod.deliver`, confirm the changeset actually contains user-visible code/functionality — a docs/distribution feature that ships zero code/manifest files (NFR-004) *should* skip the release.

**Evidence**: `specs/296-50-50-owasp-coverage-distribution-launch/{delivery.md, notes/in-tree-merge-closeout.md, notes/post-merge-security-scan.md}`; Issue #296 closing comment.

---

### Entry 9: F-302 (F-260b) Asset-Tag Output Wiring — Delivery Retrospective

**Date**: 2026-06-01 | **Category**: Process Improvement | **Feature**: F-302 / F-260b (BLP-04 Wave 2) | **Issue**: #302 (closed)

**Context**: Wired @north-echo's community asset-sensitivity tags (PR #262, v4.31.0) end-to-end through the output stack — `affected_assets` schema field (1.8 → 1.9), a deterministic populator (`scripts/populate-affected-assets.py`, the value authority), `threats.md` + dual-SARIF serialization, a shared extractor (`scripts/sarif_common.py`), ADR-046, CI lock-step wiring, and a credit moment for @north-echo. 23/23 tasks. Estimated 1-2 days, actual ~2 days (branch 2026-05-30 → delivered 2026-06-01) — on-target. Wiring, not re-tuning: the 6-tag enum, 9.2 CVSS ceiling, and modifier-after-clamp ordering stayed frozen (SC-011). F-260b-specific suites: 61/61 green (35 + 26).

**Lesson — Regenerate the `init-baseline-tree` fixture in lock-step whenever a delivery touches a CI paths-filtered file or a tracked placeholder-bearing doc.**

- **Problem**: PR #303 was the first pull_request since 2026-05-10 (F-282, baseline commit `18378bd`) to touch a `tachi-pytest.yml` `paths:` entry — it added `schemas/finding.yaml`, `scripts/populate-affected-assets.py`, `scripts/sarif_common.py`, and the two F-302 test modules. That re-triggered `test_personalized_tree_bytes_match_baseline`, which failed on 5 drifted placeholder-bearing docs. Only 1 (`docs/architecture/01_system_design/README.md`) was an F-302 change; the other 4 had drifted on main via earlier doc-close commits (F-282 on 2026-05-10, F-296 on 2026-05-30) and were never caught because no intervening PR happened to touch a filtered path. The merge was blocked until the baseline was regenerated (`711e4ae`).
- **What we learned**: The `init-baseline-tree` byte-content contract runs only on `pull_request` with a `paths:` filter, so doc-content drift on `main` accumulates invisibly and surfaces on the *next unrelated* feature PR. Worse, `/aod.deliver`'s own doc commits (KB entries, PRD INDEX, architecture/devops READMEs) are themselves substitution-target edits that re-drift the baseline immediately after a feature merges.
- **How to apply**: Treat the `init-baseline-tree` like the extract-classification and manifest-coverage snapshots already regenerated in `/aod.deliver` Step 9a — run `tests/fixtures/regenerate-baseline.sh` whenever a delivery's doc updates touch placeholder-bearing files, and commit the regenerated fixture alongside the docs. ALWAYS verify substitution semantics are intact first (the `test_template_substitute_unit` cases + `test_personalized_tree_modes_match_baseline` must pass, and the regenerated tree must contain zero unsubstituted canonical placeholders) so a regen never masks a real substitution regression — per the explicit "investigate before regenerating" mandate in the script header.

**Evidence**: `specs/302-asset-tag-output-wiring/{delivery.md, security-scan.md, test-results/summary.json}`; squash-merge `3d3d29f`; baseline-fix commit `711e4ae`; Issue #302 closing comment. Related: KB Entries 38/39 (the extract/manifest-coverage twins of this same CI-divergence class).

---

### Entry 10: F-305 Adoption Signal Capture — Delivery Retrospective

**Date**: 2026-06-01 | **Category**: Process Improvement | **Feature**: F-305 / F-3 (BLP-04 Wave 3) | **Issue**: #305 (reopened as post-merge tracking anchor)

**Context**: Built the *receiving infrastructure* for adoption signals — adopter case-study template (`docs/adopters/case-study-template.md`, 5 required + 3 optional sections + a required default-deny consent block), adopters index (`docs/adopters/README.md`), reuse of the existing "In the Wild" Discussions category, a gitignored internal append-only signal log, AIVSS v1.0 release watch, and a warm-outreach scaffold. Docs + GitHub-platform-config, no application code (FR-012); `waves_tested: 0` recorded with an explicit skip_reason. Same-day define→plan→build→deliver; estimated 1-2 days, actual ~1 day. All three Triad sign-offs APPROVED_WITH_CONCERNS (0 blocking) and the pre-merge acceptance gate (Gate C: privacy/consent + positioning-neutrality) passed with 0 findings. 14/21 tasks complete = the mergeable in-repo MVP; the remaining 7 are post-merge maintainer-tail tasks by design.

**Lesson — For docs/outreach features with a post-merge maintainer tail, merge the in-repo MVP first and split success criteria into endogenous (close-gate) vs exogenous (measurability-only).**

- **Problem**: Several of F-305's deliverable tasks are platform/human actions that cannot complete at or before the squash-merge — publishing + category-pinning a Discussions welcome post (T007/T008), an AIVSS tracking comment + issue pin (T013/T014), and ≥3 warm-outreach sends to previously-engaged contacts (T020). Treating them as ordinary pre-merge tasks would have stalled the merge indefinitely; conversely, gating the feature's close on the *inbound* those actions might generate (≥1 case study / ≥3 signals, SC-010) would make the feature un-closeable since inbound is exogenous and may never arrive.
- **What we learned**: Model the tail explicitly as `[POST-MERGE]` tasks in tasks.md, and partition the success criteria — **endogenous** SCs (the maintainer controls: the ≥3 outreach *sends*, SC-005) are the close gate; **exogenous** capture (SC-010, the inbound response) is a measurability assertion, never a close gate. Note also that GitHub auto-closes the feature issue the instant the linked PR merges — which fires *before* the post-merge tail runs, so the auto-close is not the deliberate T021 close-out and must be reversed if the tail is still pending.
- **How to apply**: (1) In tasks.md, tag platform/outreach work `[POST-MERGE] [MANUAL-ONLY]` and put a hard "recipients-logged-in-#NNN" acceptance check on the outreach task so it can't be hand-waved. (2) Merge the in-repo MVP on its own — release-please fires on the `feat(NNN):` squash regardless of the pending tail. (3) If GitHub auto-closes the issue on merge, reopen it as the tracking anchor and close it deliberately (T021) only once the endogenous gate is met. (4) Keep the strategic "why" (buyer-signal / initiative framing) in the gitignored `_internal/` log + specs/, never the public artifacts — the positioning-neutrality gate (Gate C) enforces this over `docs/adopters/*`, CHANGELOG, the README cross-link, and the auto-appended system-design section.

**Evidence**: `specs/305-adoption-signal-capture/{delivery.md, NEXT-SESSION.md, tasks.md, test-results/summary.json}`; squash-merge `b89cf46`; release-please PR #307 (`chore(main): release 4.38.0`); Issue #305 (reopened, delivery-status comment). Related: KB Entry 8 (F-296 distribution-launch docs-only / release-skip discipline).

---

### Entry 11: F-098 MAESTRO 7-Layer Coverage Matrix — Delivery Retrospective

**Date**: 2026-06-02 | **Category**: Technical Pattern | **Feature**: F-098 / F-4 (BLP-04 Wave 4, final wave) | **Issue**: #98

**Context**: Output-rendering polish making the MAESTRO "Risk by MAESTRO Layer" coverage matrix always render all 7 canonical layers (L1–L7) in canonical order across both `threats.md` and the PDF "MAESTRO Layer Analysis" page, including zero-finding layers annotated `Analyzed — no findings this scan` (Model A). 17/17 tasks; estimated 1.0–1.5 days, actual ~1.5 days across 2 sessions; Architect + Code-reviewer APPROVED, security PASSED (0 findings); feature suite 35 passed / 3 skipped / 0 regressions; no SARIF/schema change. Smooth, on-target delivery with no author-flagged surprise.

**Lesson — The markdown coverage table is the single source of truth; the PDF data model is seeded from the parsed markdown, so fix the authoring directive, not the downstream filter.**

- **Problem**: A zero-finding MAESTRO layer was silently dropped from both views, making the matrix read as a coverage ceiling (e.g. 2-of-7). The obvious-looking culprit was the PDF extractor's zero-finding filter (`extract-report-data.py:407`), but patching it alone would not fix the markdown view — and could let the PDF show more layers than the markdown actually authored.
- **What we learned**: The Architect's review re-pinned the true single root cause upstream at the orchestrator's LLM authoring directive (`orchestrator.md:718`) that writes the threats.md table; the PDF's `layer_groups` model is seeded from the *parsed markdown* `parsed_layers` (not a hard-coded layer list), so the PDF is a strictly downstream carry-through. Flipping the directive (omit→always-emit-7, severity-desc→canonical L1→L7) plus removing the now-redundant downstream filter so zero-finding rows reach the previously-dead empty-layer template branch fixes both views from one source of truth.
- **How to apply**: When a multi-format report renders the same data twice (markdown + PDF), find the authoring/source layer first and fix it there; treat downstream extractors/filters as carry-through that should only ever *narrow* from the source, never widen it. Verify the seeding relationship (does the PDF model derive from the parsed markdown, or from an independent list?) before deciding where the fix belongs. Regenerate wide example tails deterministically (`SOURCE_DATE_EPOCH=1700000000`) and guard the invariant with a heading-level-agnostic completeness test so the 7-row guarantee can't silently regress.

**Evidence**: `specs/098-maestro-7-layer/{spec.md, plan.md, tasks.md, delivery.md, test-results/summary.json}`; squash-merge `ac07085`; release-please PR #314 (`chore(main): release 4.39.0`); follow-ups #311 (Model B clean-vs-n/a) / #312 (maestro-stack infographic) / #313 (CI drift-gate). Related: KB Entry 8 (F-296 docs-only release discipline).

---

### Entry 12: F-315 MAESTRO Output Completeness (Round 2) — Delivery Retrospective

**Date**: 2026-06-03 | **Category**: Delivery | **Feature**: F-315 | **Issues**: #312, #313 (US-1 Model B #311 carved out)

**Context**: Round-2 follow-up to F-098, closing the two surfaces whose all-7 MAESTRO numbers were still agent-derived. US-2 (#312): the `maestro-stack` infographic now backfills all 7 canonical layers with code-computed `empty_layers` / `layers_with_findings` / `layer_count`. US-3 (#313): a dedicated path-scoped CI gate (`.github/workflows/tachi-maestro-coverage.yml`) guards the 7-layer coverage invariant, plus a deterministic non-gated example-PDF refresh (`examples/agentic-app/sample-report`). 20/20 tasks; estimated 1–2 days, actual ~1 day; no schema/SARIF change; F-098 all-7 + clean-annotation guarantee preserved. Author assessed delivery as smooth — no surprises, no follow-up work flagged.

**Outcome**: Build-wave test gate clean — 0 F-315 regressions (Wave 1: 168 pass / 3 pre-existing F-3/F-241 `test_tool_abuse_enrichment.py` fails, proven failing identically on a clean `main` worktree); directly-affected suites all green (infographic 34, invariant 9/2, backward-compat 13/1). Delivery note: at deliver time the implementation was landed on `main` via a clean cherry-pick of the build-wave commits (the draft PR #316 had carried the plan-stage docs ahead of the build commits); the recovery applied with no conflicts and the feature suite was re-verified green (55 pass / 4 skip) before push.

**Evidence**: `specs/315-maestro-output-completeness-round-2/{spec.md, plan.md, tasks.md, delivery.md, test-results/summary.json}`; #316 docs squash `027481b` + implementation recovery `60dd3b5`; v4.39.0 published (#314, the F-098 dependency); release-please PR #317 (`chore(main): release 4.40.0`). Related: KB Entry 11 (F-098 round-1 source-of-truth fix).

---

### Entry 13: F-A1.3 MITRE ATT&CK + ATLAS Catalog Expansion — Delivery Retrospective

**Date**: 2026-06-07 | **Category**: Process | **Feature**: F-186 | **Issues**: #186 (`follow-on-180`)

**Context**: BLP-05 Wave 2 crosswalk-catalog restoration — the #186 piece of the #184/#185/#186 trio. Feature 180's T029 cleanup had removed 88 crosswalk edges that referenced then-absent catalog IDs; Feature 241 has since added the catalog records for 10 of them. **US-1** restored those 10 now-resolvable MITRE edges byte-exact from recovered dangling commit `e58f247` (crosswalk 526 → 536). **US-2** dispositioned the 6 still-missing ATLAS IDs (`AML.T0001/T0005/T0025/T0037/T0043/T0048`) against the authoritative `mitre-atlas/atlas-data` source — all 6 verified present (ATLAS-2026.05) → all **"add"**, adding 6 records (mitre-atlas 30 → 36) and restoring their 6 unblocked edges (crosswalk 536 → 542). **US-3** drift guard confirmed a purely-additive change. 12/13 tasks (T013 deliver-time); estimated under 1 day, actual same-day; no schema/ADR change, `mitre-attack.yaml` byte-unchanged (701). Author assessed delivery as smooth — no surprises, no follow-up work flagged.

**Lesson — When restoration depends on unreachable git history, extract the recovery source to a checked-in artifact BEFORE any edit.**

- **Problem**: The 16 in-scope edges had to be recovered from dangling commit `e58f247` (pre-T029-removal, 551 edges) — a commit unreachable from `main` and never pushed. A `git gc` or a fresh clone would have destroyed the only recovery source, making the restoration impossible mid-feature.
- **What we learned**: Making "extract the restore-set to `specs/186-*/restored-edges.yaml`" a **blocking Foundational task (T002)** before any catalog/crosswalk edit de-risked the entire feature — every subsequent edit drew from the durable checked-in artifact, not the volatile object DB. The artifact carried human-auditable `_resolvable`/`_blocked_on` annotations (stripped on insertion to keep edges byte-exact), so the 10-vs-6 split stayed reviewable without re-running git archaeology.
- **How to apply**: When a change depends on recovering content from unreachable/unpushed git objects (dangling commits, reflog-only SHAs, stash), capture it to a checked-in file as the FIRST task — before any edit that could trigger gc, and before the work spans a clone boundary. Treat the dangling SHA as a wasting asset. For pure-data changes, reuse the existing test suite as the acceptance oracle (here the 5-fn integrity suite caught any dangling endpoint / shape / sort / dup violation — no new tests needed).

**Evidence**: `specs/186-mitre-catalog-expansion/{spec.md, plan.md, tasks.md, delivery.md, restored-edges.yaml, test-results/summary.json}`; squash-merge `93fbd17`; release-please PR #322 (`chore(main): release 4.42.0`); build-wave gate 15/15 (3 waves, 0 regressions). Related: KB Entry 11 (F-098), Entry 12 (F-315); BLP-05 Wave 2 siblings #184 / #185.

---

### Entry 14: F-182 Crosswalk `related` + `superseded` Edge Expansion (First Tranche) — Delivery Retrospective

**Date**: 2026-06-07 | **Category**: Process | **Feature**: F-182 | **Issues**: #182 (`follow-on-180`)

**Context**: BLP-05 Wave 3 (Crosswalk Integrity & Edges) — the #182 edges piece alongside #183 link-rot. F-180 shipped a primary-only crosswalk (542 edges); #182 was to author the first tranche of `related` edges (committed floor **≥80**, band 80–150, hard ceiling 150) plus the catalog-authorable `superseded` edges, with **no schema / enum / integrity-test / ADR change** (FR-011; ADR-027 frozen). Outcome: the build-start yield survey (T002) found the achievable high/medium core was only **37** (CWE↔CWE 22 · ATLAS→ATT&CK 7 · OWASP-LLM→ATLAS 8 · OWASP-Web→CWE **0**), so the FR-002 yield-tripwire fired and the architect (T003) authorized the **documented achievable floor of 37** rather than padding to 80 with low-confidence edges. The `superseded` authorable set = **0** (catalogs hold current editions only — the *old* endpoint of every supersession is absent), dispositioned as 4 deferred classes in `deferred-superseded.md`. 15/15 tasks (T015 deliver-time); estimated ~1.5–2.5d, actual same-day; integrity **5/5**, primary **542 preserved**, **0** catalog/test/schema/ADR change.

**Lesson — A "floor" on a derived-edge feature is a survey-gated estimate of the achievable, not a guarantee; survey the yield at PLAN time when a predecessor has already consumed the dense relationships.**

- **Problem**: The PRD committed a ≥80 `related`-edge floor (Triad high-confidence core estimate ~65), but the achievable high/medium core was 37. The dense in-catalog cross-references the floor assumed — especially OWASP-Web→CWE — had *already been authored as `primary` edges by F-180*, so OWASP-Web→CWE yielded **0** beyond-primary edges and only a thin residue of beyond-primary relationships remained to harvest.
- **What we learned**: The anti-drift-over-floor-hitting rule (FR-002 — commit the documented achievable floor, never `low`-pad to reach the number) is what kept the deliverable honest; a vanity-metric flow would have manufactured ~43 junk edges to hit 80. Modeling the floor as tripwired-and-architect-gated (T002 survey → T003 authorization) made the shortfall a **planned, signed-off branch**, not a failure. The very density that made F-180 valuable (it captured every primary cross-ref) is exactly what starved its `related` follow-on — a predictable, not surprising, dynamic once named.
- **How to apply**: For any follow-on edge/relationship feature against an already-dense graph, run the yield survey at **PLAN** time (not build-start) and set the committed floor to the surveyed achievable high/medium core, with the tripwire as the backstop — don't inherit a headline floor the catalog can't support. Keep the harvest in a checked-in artifact (`reference-edges.yaml`) so the floor decision is auditable. For pure-data changes, reuse the existing integrity suite as the acceptance oracle (no new tests). `superseded` lineage is inherently catalog-gated — expect an empty authorable set until a catalog-expansion wave adds the historical (old-edition) endpoints.

**Evidence**: `specs/182-crosswalk-related-superseded-edges/{spec.md, plan.md, tasks.md, delivery.md, reference-edges.yaml, deferred-superseded.md, test-results/summary.json}`; squash-merge `349e160` (PR #323); integrity suite 5/5 (`tests/schemas/test_taxonomy_integrity.py`); crosswalk 542 primary / 37 related / 0 superseded. Related: KB Entry 13 (F-186, BLP-05 Wave 2 sibling), Entry 11 (F-098); BLP-05 Wave 3 sibling #183 (citation link-rot).

---

### Entry 15: F-A1.2 CWE Catalog Expansion — Build-Stage Process Lesson (Consequence-Scope Discovery)

**Date**: 2026-06-11 | **Category**: Process | **Feature**: F-185 | **Issues**: #185 (`follow-on-180`)

**Context**: BLP-05 Wave 2 closer — the last of the #184/#185/#186 split-valve trio. F-185 grew `cwe.yaml` 53 → 93 (40 architect-dispositioned records, 40/40 **add**) and restored all 67 CWE-target-blocked T029 edges byte-exact (crosswalk 578 → 645). The definition-time scope (records + edges) was correct but incomplete: spec-stage research discovered `cwe` ∈ `ORDERED_FRAMEWORKS` (`scripts/extract-report-data.py:1077`), pulling the 6 CA-gated PDF baseline regens into scope (spec FR-006, PM-accepted); plan review then discovered the byte-identity suite was **already red on main** — #186 had grown `mitre-atlas` (also a member) 30 → 36 *without* regen, and the local-only suite never surfaced it; build-stage regression gating surfaced a third coupling — `tests/scripts/test_coverage_attestation.py::test_coverage_percentage_arithmetic` pins the cwe coverage percentage (1.89% = 1/53 → 1.08% = 1/93, architect-approved pin refresh). Net: O/R/P revised 0.5/0.75/1.0 → **0.75/1.0/1.5d** at tasks stage; PRD v1.2 errata records all four items.

**Lesson — At definition time of ANY catalog-growth feature, check `ORDERED_FRAMEWORKS` membership (`scripts/extract-report-data.py`) — membership ⇒ CA-page baseline regen lane (ADR-037 D-9) AND data-coupled test-expectation sweep (coverage-percentage pins) enter consequence scope.**

- **Problem**: Catalog growth looks like a pure-data change (YAML records + edges; integrity suite as oracle), but for frameworks in `ORDERED_FRAMEWORKS` the record count is render-coupled: every regenerated security report prints per-framework denominators and Covered/Partial/Gap rows on its Coverage Attestation pages, and `tests/scripts/test_backward_compatibility.py` byte-compares 6 baseline PDFs. F-186 missed this and left the suite silently red on main (inherited ATLAS 30→36 drift, discovered only at F-185 plan review); F-185 itself absorbed the lane late, at spec/plan/build rather than define — costing a timeline revision and an errata trail instead of a planned lane.
- **What we learned**: Membership in the `ORDERED_FRAMEWORKS` tuple is the single predicate that separates "catalog growth is data-only" (F-184: `nist-ai-600-1` is NOT a member — no regen needed) from "catalog growth ships with a regen + pin-sweep lane" (#186 `mitre-atlas`, F-185 `cwe`: members). Two distinct couplings follow from membership: (1) rendered-PDF baselines (regen per `baseline-regen.contract.md`: `SOURCE_DATE_EPOCH=1700000000`, sequential per-example regen over the shared `report-data.typ`, per-page text diff proving CA-only deltas); (2) data-coupled test expectations (percentage pins whose denominators are catalog counts — refresh the pin via architect ruling, never the test logic). A local-only byte-identity suite means red states persist invisibly on main; recording the literal pre-state totals at the feature's first task (T001) is what made the red→green flip attributable and the dual-attribution honest.
- **How to apply**: At `/aod.define` of any feature that grows a `schemas/taxonomy/*.yaml` catalog: grep `ORDERED_FRAMEWORKS` in `scripts/extract-report-data.py`. If the grown framework is a member, add to the PRD consequence scope: (a) the 6-baseline CA-page regen lane (ADR-037 D-9; budget ~2.25h realistic) with per-page CA-only diff evidence and dual-attribution if an inherited delta exists; (b) a sweep of data-coupled test expectations (`grep -rn "<old-count>\|<old-percentage>" tests/`) with architect-ruled pin refreshes; and (c) a T001 pre-state run of the byte-identity suite recording LITERAL pytest totals — both to detect inherited red-main drift early and to anchor the red→green claim. Timeline the lane explicitly (the F-185 floor required first-pass-clean CA-only diffs).

> **CI backstop (Feature 329, 2026-06-30):** the define-time grep checklist above is now **automated**. `scripts/check-catalog-drift.py` (the catalog-drift fingerprint guard — ADR-037 **D-14**, workflow `tachi-catalog-drift.yml` on PR + `push:[main]`) recomputes every `ORDERED_FRAMEWORKS` member's render-coupled `(id, out_of_scope)` fingerprint and fails CI when one drifts from the committed sidecar (`examples/ca-baseline-fingerprints.json`) without a CA-baseline regen — so a future author who forgets the grep is still caught, and an inherited red can no longer live silently on `main`. The guard is the automated descendant of THIS lesson; the human checklist remains the define-time first line, the guard the merge-time backstop.

**Evidence**: `specs/185-cwe-catalog-expansion/{spec.md, plan.md, tasks.md, contracts/baseline-regen.contract.md, restored-edges.yaml, test-results/{pre-state.md, baseline-diff.md, disposition.md, review-sweep.md, name-diff.md}}`; `.aod/results/185-regression-ruling.md`; PRD v1.2 errata (`docs/product/02_PRD/185-cwe-catalog-expansion-2026-06-11.md`); branch commits `6369ca6` (US1) / `9d0616d` (US2) / `d48132c` (pin refresh) / `e7ca53a` (regen red→green) / `6d369a8` (docs closure); Issue #185 T006 comment (40/40 disposition lines verified at T019). Related: KB Entry 13 (F-186 — the sibling whose unregenned ATLAS growth left the inherited red), Entry 14 (F-182), Entry 11 (F-098).

---

### Entry 16: F-A1.2 CWE Catalog Expansion — Delivery Retrospective

**Date**: 2026-06-12 | **Category**: Process | **Feature**: F-185 | **Issues**: #185 (`follow-on-180`), #329 (retro follow-up)

**Context**: Delivery-stage close-out of BLP-05 Wave 2's final record-expansion item (the #184/#185/#186 split-valve trio). Estimated O/R/P 0.75/1.0/1.5d (realistic 1d — revised up from 0.5/0.75/1.0 at tasks stage once consequence-scope was understood, see Entry 15); actual ~1 day (branch 2026-06-11 → delivered 2026-06-12) — on-target. Shipped: `cwe.yaml` 53 → 93 (40/40 **add**), `crosswalk.yaml` 578 → 645 (67 CWE-blocked edges byte-restored from `e58f247`; closes #186's 2-edge deferral); 6 CA-page PDF baselines regenerated red→green (ADR-037 D-9 lane); 20/20 tasks; build gate PASS (3 waves, 19 documented pre-existing failures, 0 in-scope, 0 regressions). PR #328 squash-merged `2aa1bf5`; ships in release-please PR #326 → v4.43.0 (batched with F-184). Issue #185 closed `stage:done`.

**Lesson — A consequence-coupled data feature delivers clean only when the couplings are surfaced as first-class scope and the pre-state is recorded; the catalog edit itself is the easy part.** (Deep build-stage mechanics: see Entry 15.)

- **Problem (delivery view)**: The headline deliverable read as pure data (records + edges), but the real delivery risk lived in two render/test couplings discovered late (CA-page baseline regen + a coverage-percentage test pin) plus an inherited red-main left by sibling F-186. A naive close would have either shipped red (byte-identity suite) or mis-attributed the red→green flip.
- **What we learned**: Recording the LITERAL pre-state pytest totals at T001 is what made the red→green flip attributable and the dual-attribution (inherited #186 ATLAS drift vs. F-185's own cwe growth) honest at delivery. The delivery itself was uneventful precisely because the consequence-scope was made explicit (spec FR-006, PRD v1.2 errata) rather than absorbed silently. Estimate accuracy held (actual ~1d ≈ realistic 1d) once the tasks-stage revision folded the lane in.
- **How to apply**: For consequence-coupled features, treat "delivery clean" as a function of how early the couplings were named — the cost is paid at define/plan, not deliver. Carry an explicit pre-state artifact (`test-results/pre-state.md`) into the delivery doc so the audit trail proves what changed and why. The local-only byte-identity suite gap that enabled the inherited red is now tracked as a backlog item (#329 — evaluate CI wiring / catalog-count drift guard).

**Evidence**: `specs/185-cwe-catalog-expansion/{spec.md, plan.md, tasks.md, delivery.md, test-results/{summary.json, pre-state.md, final-gate.md}}`; squash-merge `2aa1bf5` (PR #328); build-wave gate 3 waves / final 19 pre-existing, 0 in-scope, 0 regressions; release-please PR #326 (`chore(main): release 4.43.0`). Related: Entry 15 (F-185 build-stage consequence-scope lesson — the substantive companion to this delivery entry), Entry 13 (F-186, BLP-05 Wave 2 sibling), Entry 14 (F-182, BLP-05 Wave 3).

---

### Entry 17: F-183 Citation-URL Link-Rot Monitoring — Delivery Retrospective (deliver-adjacent live validation pays off)

**Date**: 2026-06-15 | **Category**: Process | **Feature**: F-183 | **Issues**: #183 (`follow-on-180`), #332 (live self-healing tracker), #333 (remediation backlog)

**Context**: Final feature of BLP-05 (Wave 3 integrity sub-wave) → **BLP-05 COMPLETE 6/6**. Shipped a weekly scheduled GitHub Actions workflow (`tachi-citation-linkrot.yml`) + a zero-dependency stdlib checker (`scripts/check-citation-urls.py`) that probes every crosswalk citation URL, classifies (HEALTHY / LINK_ROT 404·410 / NEEDS_REVIEW 401·403·429 / TRANSIENT 5xx·timeout-never-reported), and reconciles one self-healing `gh` tracking issue. Estimated 2.0–3.0 eng-days → actual ~1 day (spec→deliver 2026-06-14→06-15). 22/22 offline tests, 0 regressions, NFR-001 proven (network-free + subprocess-free under an outer egress block), parity confirmed (930 unique monitored URLs). PR #330 squash-merged `0a33d70`; v4.44.0 (release-please PR #331); no new ADR (determinism-boundary + monitor-not-gate are derivative of accepted ADR-021, dual-signed in plan.md, below the ADR bar).

**Lesson — When a feature's only true integration test is deliver-adjacent (`[MANUAL-ONLY]`), RUN it at delivery rather than deferring it: T021's two live dispatches converted "feature shipped" into "feature proven + 41 real defects captured" within minutes.** The offline suite proved the logic; only the live run proved the *deployed* system — and immediately earned its keep.

- **Problem**: T021 (live two-run dispatch) was the sole validation of the integrated workflow + live network + `gh` issue lifecycle + `actions/cache` ledger accumulation. It is correctly never a PR gate (NFR-001 determinism boundary) and was triple-signed-off as "deliver-adjacent / MANUAL-ONLY." The easy path is to ship #183 and leave T021 as a documented manual step the human runs "later" — which usually means never, leaving the deployed integration unvalidated.
- **What we learned**: Running T021 during deliver validated the **create** branch (Run 1 `inject_sentinel_rot=true` → exactly one tracking issue #332, sentinel named) and the **edit/delta** branch (Run 2 `=false` → 42→41 findings, **sentinel dropped — proving no leak into non-injected runs**, dated delta comment, ledger restored run-over-run). The **self-close** branch could NOT be exercised live — because the very first sweep found **41 *real* dead citation URLs** (verified real, not bot-blocks: checker UA and browser UA both 404, redirects followed): ~38 MITRE ATLAS technique pages (#186), the NIST AI RMF DOI target (#184, ~75 citing records), 4 OWASP GenAI LLM URLs. A monitor that won't self-close while real rot exists is the feature *working*, not failing — so self-close stays offline-validated (render tests T012 + code review T020), and that gap is itself a successful outcome.
- **How to apply**: (1) For any feature whose integration surface is gated out of CI by design (scheduled-only, external-network, side-effecting), schedule the live validation INTO the deliver step — don't punt it to a human "later." (2) Expect a brand-new monitor/linter to find real pre-existing defects on first run; pre-decide the disposition (here: out-of-scope to *fix* per spec; file remediation as a separate backlog item #333; let the self-healing tracker #332 hold live state). (3) A "first live run found N real issues" outcome is a feature-value proof point — capture it in the delivery doc and the issue comment, don't bury it. **Corollary for catalog-expansion features (#184/#185/#186): citation URLs added in rapid expansion were never validated against live endpoints — 41 were dead on arrival; the monitor is now the systemic guard, but authoring-time URL reachability checks would shift that left.**

**Evidence**: `specs/183-citation-url-link-rot-monitoring/{spec.md, plan.md, tasks.md, delivery.md, quickstart.md §4, test-results/{summary.json, wave-01, wave-02}}`; workflow `tachi-citation-linkrot.yml`; live runs `27551693237` (Run 1) + `27552304453` (Run 2); tracking issue #332 (41 real findings, self-healing); remediation backlog #333; squash-merge `0a33d70` (PR #330); v4.44.0 (release-please PR #331). Related: Entry 15/16 (F-185, BLP-05 Wave 2 — the expansion that introduced the CWE/ATLAS records), Entry 13 (F-186 ATLAS — source of the ~38 ATLAS URL rot), Entry 14 (F-182, BLP-05 Wave 3 sibling).

---

### Entry 18: F-338 Restore F-248/F-256 Substitution Hardening — Delivery Retrospective (the regression's second life nearly happened at deliver)

**Date**: 2026-06-30 | **Category**: Process | **Feature**: F-338 | **Issues**: #338 (origin), #340 (PR), #341 (release v4.45.1), #342 (retro idea — deliver-stage preflight guard)

**Context**: BLP-06 Wave 2, F-2. A 2026-06-28 `/aod.update` AOD-Kit re-sync silently reverted shipped F-248/F-256 bash hardening on public `main` (second occurrence after `07236cf`) — because `/aod.update` commits **direct-to-main, bypassing the PR-gated `tachi-pytest.yml`**. The fix restored the 3 script bodies **byte-identical** to last-good v4.44.0 (`5b64f68`) — the F-248 `patsub_replacement` shim, the F-256 `STACK_PACK_ALLOWED_KEYS` whitelist loader, the `AOD_FETCH_TIMEOUT` clone watchdog — plus the canonical 5-key `defaults.env` surface across all 5 packs (FR-009/OQ-3). Guardrail groundwork (`99507b2`): `tachi-pytest` now also gates `push:[main]` (FR-006), `#329` baseline test xfail'd (FR-007). Estimated floor 1 / planning 2 eng-days → **actual ~1 day** (2026-06-29→06-30). Both CI legs green (macOS bash 3.2.57 + ubuntu bash 5.x; build-wave 143 pass / 0 fail / 1 skip / 1 xfail, 0 regressions). PR #340 squash-merged `6fbce10`; v4.45.1 (release-please #341).

**Lesson — The regression you are restoring can re-occur AT DELIVER. A long-lived restore branch had fallen behind a fast-moving `main`, AND local `main` carried a stale, unpushed `/aod.update` clobber (`ad390f8`) — the exact direct-to-main revert this feature fixes. Pushing deliver-stage docs from that diverged local `main` would have re-clobbered the just-restored hardening. Verify branch-current + local-`main`==`origin/main` BEFORE any merge or direct-to-main push.**

- **Problem**: At the deliver merge step, (1) the PR was `CONFLICTING`/`DIRTY` — GitHub could not build a test-merge, so **CI would not run** until conflicts were resolved (the branch predated #333 + the v4.45.0 release); and (2) local `main` was 1 commit ahead / 4 behind `origin/main`, its lone unique commit being `ad390f8 chore: apply aod.update → d8a66381` — an unpushed direct-to-main aod.update apply, the same regression class #338 fixes. `/aod.deliver` Step 9 pushes docs **direct to main**; from the diverged local `main` that push would have shipped the clobbered tree.
- **What we learned**: (a) The merge conflicts were confined to **3 non-hardening metadata files** (`.security/scan-log.jsonl` append-log, `docs/product/02_PRD/INDEX.md` PRD index, generated `BACKLOG.md`) — the entire hardening surface (3 scripts + 5 `defaults.env`) flowed through untouched and was re-proven **byte-identical to `5b64f68`** after the merge. Resolving an append-only log = keep both entries; resolving the index = take the delivered `main` side and splice the new row; resolving a generated file = take `main` (it regenerates at deliver). (b) The `git reset --hard` permission guard **blocked the naive realignment and forced a read-only proof** that `origin/main` already contained `ad390f8`'s content (byte-identical `update.sh`/`aod-kit-version`/`DOWNSTREAM_UPDATE.md`) — making the `checkout -B main origin/main` realignment provably loss-free instead of a blind discard. A 3-file diff looked clean; only the **full** `git diff origin/main` (65 files, 4616 lines) revealed local `main` was the stale clobbered tree.
- **How to apply**: (1) Before a deliver merge, check `git rev-list --count origin/main..HEAD` (branch behind?) and resolve by merging `origin/main` in — squash-merge collapses the merge commit anyway. (2) Before ANY direct-to-main push, check `git rev-list --left-right --count main...origin/main`; **never push from a diverged local `main`** until realigned, and prove realignment is loss-free with the **full-tree** diff, not a hand-picked file subset. (3) Confine restore-feature conflicts to metadata by keeping the hardening surface a clean generic-revert (byte-identical to the last-good SHA) — then a one-line `git diff <SHA> -- <hardening files>` is the standing parity oracle through every rebase/merge. (4) This is the deliver-stage complement to the existing `/aod.update` operator insurance (checkpoint + `--dry-run` + `git diff --stat` the at-risk set); tracked as #342.

**Evidence**: `specs/338-restore-substitution-hardening/{spec.md, plan.md, tasks.md, delivery.md, NEXT-SESSION.md, test-results/{summary.json, wave-01/results.json}}`; restore commit `18a39ed` (byte-identical to `5b64f68`); merge-resolution commit `c781a2d`; squash-merge `6fbce10` (PR #340, `fix(338):` title); v4.45.1 (release-please #341); CI run `28455027920` (both legs green). Related: Entry 17 (F-183 — the deliver-adjacent-validation sibling), and memory `project_aod_update_clobbers_tachi` / `project_f248_f256_test_harness_clones_head` (the build-stage companion lessons: harness clones committed HEAD, gated suite is the 15-module subset).

---

### Entry 19: F-329 ORDERED_FRAMEWORKS Catalog-Drift CI Guard — Delivery Retrospective (a render-coupling fingerprint backstops an unwired byte-identity check)

**Date**: 2026-06-30 | **Category**: Pattern | **Feature**: F-329 | **Issues**: #329 (origin, `type:retro`), #344 (PR), #341 (release v4.46.0), #346 (S-1 follow-up)

**Context**: BLP-06 Wave 2, CI-hardening-tail **lead** (P1). The 6-PDF byte-identity suite (`test_backward_compatibility.py`) byte-compares committed CA-page baselines but is wired into **no** CI workflow — so when an `ORDERED_FRAMEWORKS` member catalog (owasp/mitre-attack/mitre-atlas/nist-ai-rmf/cwe) changes its render-coupled record set without the 6 baselines being regenerated, the suite goes **silently red on `main`** (the F-186→F-185 path; KB Entry 15). F-329 closes that gap with a guard that recomputes a deterministic render-coupled fingerprint (the ordered `[id, out_of_scope]` list, raw + in-scope partitions) for each live member by **reusing the renderer's own loader** via `importlib`, and reddens CI on PR + `push:[main]` when a member diverges from a committed sidecar — rendering nothing (NFR-001). Estimated 1.5 eng-days (floor 1 / ceiling 3) → **actual same-day** (PRD→deliver 2026-06-30). 16/16 tasks; guard 15/15 + live acceptance probes; Security/Economy PASSED; Architect APPROVED. PR #344 squash-merged `38a8ceb`; v4.46.0 (release-please #341).

**Lesson — When an expensive/flaky byte-identity check is too costly to wire into CI, guard its *invariant* at logic level with a render-coupling fingerprint: reuse the renderer's OWN record loader so the guard's notion of "what the page depends on" is the renderer's by construction, and emit the expected-value sidecar as the FINAL step of the regeneration script so the expected values cannot be advanced without a genuine regen (cheat-resistance).** This converts a manual define-time checklist (the KB-15 "grep `ORDERED_FRAMEWORKS`" step) into a CI-enforced invariant without rendering anything.

- **Problem**: The full fix — wiring the 6-PDF Typst byte-identity suite into CI — is expensive (rendering), platform/font/Typst-version-fragile, and slow. Deferring it (option a) leaves `main` able to go silently red whenever a catalog grows. The cheap proxy (counting records) false-greens on a constant-count ID-swap (HIGH-2) and false-reds on count-neutral citation edits (#333) — and a guard that false-reds is worse than none.
- **What we learned**: Fingerprinting the **ordered `[id, out_of_scope]` projection** (not the raw file, not the count) is the right granularity: it catches grow, constant-count ID-swap (HIGH-2), and `out_of_scope` flips (HIGH-3) while staying green on the #333 citation-string class — proven live at deliver (probe-1 id-rename → exit 1 naming `cwe`; probe-2 url-only → exit 0). Two design choices carry the trust: (1) **loader reuse via `importlib`** (code-economy rung 2 — re-implementing the YAML walk would let the guard's coupling notion drift from the renderer's); (2) **sidecar emitted as the regen script's last step** — a developer cannot advance the CI-enforced expected fingerprints without actually re-rendering first. Fail-closed everywhere (missing/partial/unparseable sidecar, a live member absent from the sidecar, a non-dict record → the C-2 `isinstance` guard) so deleting/truncating the sidecar reddens rather than passes. The guard's first live CI fire passed green first-try (the `pip install pyyaml` step closed the silent-no-op mode).
- **How to apply**: (1) For any "golden artifact" check too costly for CI, ask whether a **deterministic fingerprint of the artifact's inputs** captures the same invariant without producing the artifact — guard the fingerprint, render offline. (2) Derive the fingerprint by reusing the producer's own input-loading code, not a parallel re-implementation. (3) Make the expected-value file a **byproduct of the real regeneration** (emitted last), never hand-editable — that is what makes the guard un-cheatable. (4) Pick the fingerprint granularity from the *threat model* (here: ordered id+scope catches swap/flip; counts alone do not; raw bytes false-red on citations). (5) Cover the future automatically — derive the member set from the live tuple at runtime (FR-004), so adding a 6th framework extends coverage with zero guard-code change.

**Evidence**: `specs/329-ordered-frameworks-ci-guard/{spec.md, plan.md, tasks.md, delivery.md, contracts/sidecar.contract.md, quickstart.md, test-results/{summary.json, wave-01..03}}`; `scripts/check-catalog-drift.py`, `scripts/regenerate-ca-baselines.sh`, `examples/ca-baseline-fingerprints.json`, `tests/scripts/test_catalog_drift_guard.py`, `.github/workflows/tachi-catalog-drift.yml`; ADR-037 **D-14**; squash-merge `38a8ceb` (PR #344, `feat(329):` title); v4.46.0 (release-please #341); S-1 follow-up #346. Related: Entry 15/16 (F-185 — the catalog-expansion build/deliver consequence-scope lessons this guard now backstops), Entry 17 (F-183 — the sibling render-coupling / deliver-adjacent-validation monitor), Entry 18 (F-338 — the `push:[main]` direct-to-main guard reused for US3).

---

### Entry 20: F-281 CI & Governance Hardening Tail — Delivery Retrospective (a CI gate that clones a sibling workflow and reuses a delivered script adds zero net-new verification logic)

**Date**: 2026-07-01 | **Category**: Pattern | **Feature**: F-281 | **Issues**: #281 (lead), #285/#286/#287 (bundle members), #348 (enhancement — high-entropy hex gap), #347 (PR), #341 (release v4.46.0)

**Context**: BLP-06 Wave 2 hygiene-tail (bundle: #281 lead + #285/#286/#287). Ports the already-shipped F-4 (permissions) and F-5 (gitleaks) *local* pre-commit checks into CI-enforced, auditable surfaces — adding no product capability. The load-bearing core is `.github/workflows/tachi-permissions-verify.yml`: a dual-trigger (`pull_request` + `push:[main]`) gate whose four ordered steps are a jq-presence guard → `jq empty .claude/settings.json` → the **reused #280** `claude-permissions-ac2-crosscheck.sh` (fails on any non-zero — orphan-diff exit 1 or invariant-violation exit 2) → §3/§4 doc-presence greps on `CLAUDE_PERMISSIONS.md`, all under `contents: read`. Riders: a gitleaks default-rule coverage catalog (#285, `PRECOMMIT_HOOKS.md §3`, 5/6 patterns covered → hex gap #348), a `.gitleaks.toml.adopter-template` (#286, 90 LOC, config-valid), and a pin-bump cadence surface + issue template (#287, §10 + `gitleaks-bump.md`). Estimated 2.0 eng-days (floor 1 / ceiling 3) → **actual same-day** (spec→deliver 2026-07-01). 18/18 tasks; Security 0 findings, Economy no over-build, Architect APPROVED; CI green (4/4). PR #347 squash-merged `cf8ef12`; folds into release-please v4.46.0 (#341, shared with F-329). CARVE-IN confirmed (T016 — no split-valve trigger fired).

**Lesson — Porting an already-delivered *local* check into a CI gate is a near-1:1 structural clone of an existing sibling workflow, not net-new machinery: reuse the sibling's YAML-anchor path-filter shape and the already-shipped verification *script* verbatim, and the only net-new line is a defensive presence-guard for the tool the gate shells out to (jq) so a runner-image change fails the gate loudly rather than silently stops it governing.** This is why the economy gate found zero over-build and a 2-day-estimated feature landed same-day.

- **Problem**: F-4/F-5 shipped the permissions/gitleaks checks as *local* pre-commit hooks — which a `--no-verify` commit, an uninstalled hook, or a GitHub web-UI edit bypasses silently, landing a broken `settings.json` or an orphaned rule/table-row on `main` (the same direct-to-main-bypass class #338/#329 hardened against). The naive fix — author a fresh verification workflow — would re-implement path-filtering, JSON-validity, and the settings↔doc cross-check that already exist.
- **What we learned**: The whole gate is assembly, not authorship. (1) The **workflow shape** is `tachi-catalog-drift.yml` (F-329, Entry 19) with a different `&verify_paths` anchor and step body — same dual-trigger, same `contents: read` least-priv, same single-anchor-shared-across-both-triggers idiom. (2) The **cross-check logic** is the already-delivered #280 `claude-permissions-ac2-crosscheck.sh`, invoked verbatim — the workflow only wires "fail the job on any non-zero exit." (3) The one genuinely new line is the **jq-presence guard** (FR-281.7): a governance gate must not silently stop governing when a future runner image drops a tool it assumed present, so it fails loudly *before* the parse. (4) The rider half (#285/#286/#287) is documentation/template over an already-accepted stance (ADR-042), so **no ADR was minted** — the CI-gate shape follows ADR-037 D-14, the permissions baseline is ADR-041, the gitleaks default is ADR-042 (recorded as a "no-ADR — CARVE-IN reasoning" note in system-design per the ADR-047 apply-an-invariant rule). (5) The **split-valve** (carve #285/#286 out at build if they grow a committed test harness or exceed 120 LOC) never tripped — template stayed 90 LOC, the empirical probe stayed throwaway/reuse against the existing `tests/fixtures/gitleaks-rule-interaction/` fixtures — so the bundle stayed whole.
- **How to apply**: (1) Before authoring a CI verification workflow, grep `.github/workflows/` for a sibling with the same trigger+permission posture and clone its structure — the path-filter anchor, the `contents: read` line, and the header-comment rationale are reusable verbatim. (2) If the check already exists as a *script* (local hook, pre-commit), the CI job is a one-line invocation that fails on non-zero, not a re-implementation. (3) Add a presence-guard for every external tool the gate shells out to (`command -v <tool> || exit 1`) so runner drift reddens instead of silently no-ops — the same fail-loudly principle as F-329's fail-closed sidecar. (4) When the new surface only *applies* an already-accepted ADR to a new enforcement point, mint no ADR (ADR-047 rule); record the "no-ADR — reasoning" in system-design instead. (5) Keep enhancement riders on a documented split-valve with a numeric trip-wire (LOC ceiling / new-harness trigger / effort ceiling) so the carve-in-vs-carve-out call is mechanical at build, not a judgment call at deliver.

**Evidence**: `specs/281-ci-governance-hardening-tail/{spec.md, plan.md, tasks.md, delivery.md, NEXT-SESSION.md, research.md, economy-check.md, security-scan.md, test-results/summary.json}`; `.github/workflows/tachi-permissions-verify.yml`, `.gitleaks.toml.adopter-template`, `.github/ISSUE_TEMPLATE/gitleaks-bump.md`, `docs/standards/PRECOMMIT_HOOKS.md` (§3 catalog / §9.5 adopter / §10 cadence), `docs/architecture/02_ADRs/ADR-042-*.md §References`, `docs/architecture/01_system_design/README.md` (no-ADR CARVE-IN note); reused `.aod/scripts/bash/claude-permissions-ac2-crosscheck.sh` (#280). Squash-merge `cf8ef12` (PR #347, `feat(281):` title); folds into release-please v4.46.0 (#341, shared with F-329). Enhancement #348 (high-entropy hex gap, filed at build). Related: Entry 19 (F-329 — the sibling dual-trigger workflow this clones and the `push:[main]` guard it reuses), Entry 18 (F-338 — the direct-to-main bypass class this closes for the permissions surface).

---

### Entry 21: F-217 Detect-Images Duplicate Cleanup — Delivery Retrospective (safe destructive cleanup = double gate + every-moment wiring)

**Date**: 2026-07-02 | **Category**: Pattern | **Feature**: F-217 | **Issues**: #217 (lead), #215/#216 (producer fix that froze the population), PR #351, #341 (release v4.46.0)

**Context**: BLP-06 Wave 3 hygiene feature. Since #215/PR #216, the report-data extraction tool (`scripts/extract-report-data.py`) self-heals mislabeled infographic images (a `.jpg` holding PNG bytes — the `gemini-2.5-flash-image` fallback-era signature) by writing a corrected sibling, deliberately non-destructively — so every legacy assessment directory carries both files forever (~2× image storage per affected stem, up to 6 stems per directory, plus path ambiguity). F-217 ships PRD option (c) + (a): an explicit opt-in `--cleanup-mislabeled-images` flag plus a documented sanctioned cleanup path; option (b) destructive-by-default was rejected. Estimated **1.0 eng-day** (Team-Lead central; floor 0.5d) → **actual 1 day** (branch 2026-07-01 18:28 → merge 2026-07-02 09:02; single wave built same evening). 17/17 tasks; gated suite 945 pass / 0 regressions; US-2 dogfood removed the 6 in-repo duplicates (~6.75 MB) from `examples/agentic-app/test-output/2026-04-19T03-20-30/` with byte-identical `report-data.typ` proof (path-invariance). Surprise log: smooth sailing — single-wave build, actual matched estimate, no major surprises.

**Lesson — Safe destructive cleanup is a double gate wired at every moment the deletable state can exist: delete only with an explicit opt-in flag AND a byte-identical correctly-labeled counterpart, key the predicate on the defect itself (content format ≠ extension, direction-agnostic) rather than sibling existence, and wire BOTH the pre-existing-pair moment and the recovery-write moment — wiring only the obvious (recovery) moment silently misses the primary legacy case.**

- **Problem**: The non-destructive self-heal (#215/#216) preserved originals by design, so mislabeled/corrected byte-identical pairs accumulate forever in legacy directories, and adopters' only remedy was an unsafe hand-rolled `find … rm` one-liner that guesses which file is authoritative.
- **What we learned**: (1) The deletion predicate must key on **mislabeled-ness**, not sibling-existence — legitimate self-consistent `.jpg`/`.png` pairs of different images are never candidates (AC-1h). (2) **Enumerate every moment** the target state can exist before wiring a cleanup: pre-existing pairs (the primary legacy case — the entire US-2 target) and recovery-write time (FR-004); the obvious-moment-only wiring would have silently missed the point of the feature. (3) **Byte-identity is a dual-purpose gate**: proof-of-duplicate AND copy-success verification — a truncated recovery copy means no deletion and still exit 0 (AC-1f). (4) Cross-swap safety (AC-1g) needs one extra gate: recovery-path deletion fires only when the corrected sibling did NOT pre-exist the copy, preventing amplification of the pre-existing overwrite behavior into data loss. (5) **Spec-enumerated safety negatives** (FR-007: AC-1d/1f/1g/1h each with a dedicated automated test) are what make an `rm`-bearing flag reviewable. (6) Fixing the producer first (#215/#216) froze the affected population, making this purely subtractive and safe to scope tightly.
- **How to apply**: Before shipping any cleanup/deletion capability: (1) default-off explicit opt-in — never destructive-by-default; (2) require content proof (byte-identity), never heuristics, and never guess which file is authoritative when proof fails; (3) enumerate all moments the deletable state arises and wire each one; (4) write the safety negatives as explicit ACs with dedicated tests before implementation; (5) deletion is best-effort — one stderr record per deletion/failure, never fail the run, emitted output identical either way; (6) dogfood against the real in-repo data as the delivery proof (duplicate count N → 0 with byte-identical regenerated output).

**Evidence**: `specs/217-detect-images-duplicate-cleanup/{spec.md, plan.md, tasks.md, delivery.md, test-results/summary.json}` (945 pass / 0 regressions); `scripts/extract-report-data.py` (flag + double-gated predicate); `.claude/skills/tachi-report-assembly/references/` (US-3 sanctioned-cleanup doc); `examples/agentic-app/test-output/2026-04-19T03-20-30/` (6 pairs → 0). Squash-merge `3b5b377` (PR #351, `feat(217):` title); folds into release-please v4.46.0 (#341, shared with F-329 + F-281). Related: Entry 20 (F-281) and Entry 19 (F-329) — same BLP-06 initiative; #215/#216 (the producer fix whose non-destructive recovery this feature completes).

---

### Entry 22: F-295 F-292 Post-Merge Verification Runs — Delivery Retrospective (gate on the compiled artifact, never intermediate agent output)

**Date**: 2026-07-04 | **Category**: Pattern | **Feature**: F-295 | **Issues**: #295 (lead; closes the F-292 T017+T026 deferral), #354/#355/#356 (defects filed during build), #357 (enhancement), PR #353, #358 (release v4.47.0)

**Context**: BLP-06 Wave 3 closer — the initiative's last open item (deferred tail: #325). F-292 shipped 2026-05-14 with SC-003/SC-015 empirically unverified (KB Entry 7 deferral → #295); this feature executed both verification runs with fail-closed, false-pass-guarded gates where the deliverable is the committed verification record and failure disposition is pre-decided (fix-vs-file). US-1 (T017/SC-003): **PASS** — attempt 1's single-agent `tachi-output-integrity` dispatch returned NO_FINDINGS and was correctly treated as gate ERROR (never "zero emissions = pass"); attempt 2's scoped-full fallback produced a valid 4-finding OI subset matching the pre-292 anchor (`0629fa2~1` → OI-1..OI-4) on all D-1 gate fields. US-2 (T026/SC-015): **FAIL, honest-stop** — the Cat 6 Vector/Search-DSL Injection threat WAS detected (threats.md rows self-label it) but orchestrator Phase-3 compilation absorbed the output-integrity findings into the LLM-N ID sequence, dropping the `OI-` prefix and CWE-943 citations → defect #356; no baseline committed to `examples/multi-tenant-rag-app/`; US-3 (CI byte-identity check) structurally deferred to #356 per its gate. Only production code change: FR-014 URI derivation in `generate-threats-sarif.py` (+4 covering assertions, +1 lock-step `tachi-pytest.yml` path line; agentic-app regen byte-unchanged). Estimated 0.5/1.0/2.0 eng-days (central 1.0) → actual 1 day (branch 2026-07-03 → merge 2026-07-04). 16/16 tasks; 78 pass / 0 fail / 3 pre-existing skips, 0 regressions. Surprise log: smooth sailing — the honest-FAIL path was designed-for, so executing it was not a deviation.

**Lesson — Gate verification on the compiled artifact adopters consume, never on intermediate agent output: one feature's fail-closed gates surfaced two otherwise-invisible defect classes — dispatch-tier under-triggering (T017 attempt 1) and compilation-tier ID mangling (T026 → #356) — both of which agent-level evidence would have masked.**

- **Problem**: Both F-292 claims could have "passed" trivially on weaker evidence: the archived contract §3 filter matched zero results on every SARIF (empty-vs-empty false-pass, #354), and the T026 sub-agent's own return carried correct `OI-` findings while the compiled `threats.md`/`threats.sarif` did not.
- **What we learned**: (1) The empty-extraction=ERROR rule converted a plausible "no regressions" into the discovery that single-agent dispatch under-triggers relative to full-pipeline context — a comparison-path artifact, not an emission regression (independent proof: the committed HEAD baseline carries OI-1..4). (2) The compiled-artifact gate exposed a defect class nobody had named: Phase-3 compilation can absorb OI findings into the LLM-N sequence — detection-tier evidence actively masks it because the sub-agent emits the right IDs. (3) Two-attempt caps + pre-decided fix-vs-file disposition kept a gate-FAILing feature on estimate (1 day) with zero scope creep; attempt-1 tooling failures (orphaned background dispatch — children outlived the parent orchestrator's turn) consumed a cap without corrupting evidence.
- **How to apply**: For any verification/evidence feature: pin expected cardinality on an immutable anchor; treat empty extraction as gate ERROR, never pass; diff the artifact the consumer reads, not what producers emit; pre-decide the failure disposition (defect-file + close on the committed record); cap live attempts (2) with an escape hatch; dispatch pipeline agents synchronously so the parent can compile them.

**Evidence**: `specs/295-f292-verification-runs/{sc-003-verification-record.md, sc-015-verification-record.md, test-results/, delivery.md}`; squash-merge `e6e8ef0` (PR #353, `feat(295):` title) → release-please v4.47.0 (#358). Related: KB Entry 7 (the original F-292 deferral), Entry 17 (live-dispatch validation at deliver), Entries 19–21 (BLP-06 siblings).

---

### Entry 23: F-362 OWASP LLM Top 10 2026 Remap — Delivery Retrospective (re-meaning migrations need disposition ledgers, not just sweeps)

**Date**: 2026-08-12 | **Category**: Pattern | **Feature**: F-362 | **Issues**: #362 (lead), #364–#370 (follow-ups filed during build), PR #363, #371 (release v4.48.0)

**Context**: OWASP published the LLM Top 10 2026 (v1.0, 2026-08-04) with a changed rank order — bare codes changed *meaning* (LLM03: Supply Chain → Excessive Agency), and LLM07:2025 System Prompt Leakage was renamed/re-scoped to LLM08:2026 Hidden Context Exposure. F-362 remapped every contract surface (catalog, 74-edge crosswalk with an 8-id bijection, 9 personas, 15 skill references, 4 adapter sets, emitters, schemas, fixtures, tests) and re-derived the 50/50 coverage claim against 2026 definitions (10/10 Covered, PM SC-005 re-verified at deliver). ADR-048 fixed a hard-cutover alias policy at the token-grammar layer — zero schema shape churn. Estimated 4.9 eng-days central (band 4.0–6.0) → actual 6 days (branch 2026-08-06 → merge 2026-08-12), on the band ceiling and 2 days ahead of the 2026-08-14 deliver forecast. 26/26 tasks; 648 pass / 0 fail / 8 skip across 4 tested waves, 0 regressions. Surprise log: 2026 per-entry URLs did not exist at authoring time — the D9 URL-scheme gate forced an interim release-page anchor, and the deliver-stage no-cache link-rot dispatch (908 checked, 0 confirmed rot) validated it live exactly as designed; the T022 sweep gate passed only after a 13-site absorption fix; the byte-identity red proved environmental (#365 font-subset divergence), not feature-caused.

**Lesson — When identifiers change meaning (not just format), a repo-wide sweep is necessary but insufficient: append-only disposition ledgers with pre-pinned censuses are what make the migration auditable.**

- **Problem**: A sweep finds occurrences; it cannot prove each occurrence was *reviewed under the new meaning*. With 498 suffixed occurrences / 77 files plus 366 in-scope bare codes, silent wrong-attribution risk (a 2025-meaning code surviving into 2026 emissions) was the feature's core hazard, and sequential in-file re-keys would have collided mid-flight on the crosswalk dedupe key.
- **What we learned**: (1) Two ledgers scaffolded before any edit (74-row crosswalk disposition; bare-code ledger with the census pre-partitioned into agent lanes under an append-only-to-your-own-section rule) gave every occurrence exactly one recorded disposition — re-keyed, confirmed-correct, or excluded-with-reason — with counts research-measured at a pinned SHA (`747805c`) as the oracle. (2) The 8-id re-key executed as a single simultaneous permutation, not sequential renames, because the bijection collides on the dedupe key mid-flight otherwise. (3) A declared, time-boxed carve-out (examples/** → F-362b #364, blocking before the next minor) beats both silent deferral and scope creep; the mid-window 2025-token risk is *disclosed in the changelog* rather than hidden. (4) URL schemes for a just-published standard are themselves a gated decision (D9): verify live, record the anchor policy in the ledger header, and let the deliver-stage link-rot dispatch confirm reachability — never author URLs from an assumed slug pattern.
- **How to apply**: For any taxonomy/standard edition bump where codes re-meaning: scaffold disposition ledgers first (lane-partitioned if multiple agents write), pin censuses at a named SHA, execute bijective re-keys as one permutation pass verified by an integrity suite, time-box any carve-out as a filed blocking issue, and gate citation URLs on live verification at both authoring and deliver.

**Evidence**: `specs/362-remap-owasp-llm-top10-2026/{crosswalk-disposition-ledger.md, bare-code-ledger.md, gap-analysis.md, test-results/, delivery.md}`; ADR-048 (Accepted-commit-SHA `e6316e3`); squash-merge `e6316e3` (PR #363, `feat(362):` title) → release-please v4.48.0 (#371). Related: KB Entry 15 (`cwe`∈ORDERED_FRAMEWORKS consequence scope), Entry 17 (live-dispatch validation at deliver), Entry 22 (gate on the compiled artifact).

---

## Bug Fixes

*No entries yet. Use `/kb-create` to add the first bug fix.*
