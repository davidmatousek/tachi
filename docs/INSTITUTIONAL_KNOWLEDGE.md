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

## Bug Fixes

*No entries yet. Use `/kb-create` to add the first bug fix.*
