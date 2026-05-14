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

## Bug Fixes

*No entries yet. Use `/kb-create` to add the first bug fix.*
