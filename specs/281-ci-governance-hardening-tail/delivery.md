# Delivery Document: Feature 281 — CI & Governance Hardening Tail (F-4/F-5 follow-ups)

**Delivery Date**: 2026-07-01
**Branch**: `281-ci-governance-hardening-tail` (merged + deleted)
**PR**: #347 (squash-merge `cf8ef12`)

---

## What Was Delivered

BLP-06 Wave 2 hygiene-tail — bundle led by #281, members #285/#286/#287. Ports the already-shipped F-4 (permissions) and F-5 (gitleaks) *local* pre-commit checks into CI-enforced, auditable, maintainable surfaces. Adds **no** product capability; makes the existing surface more defensible.

- **Permissions surface verified in CI** (#281, SC-1) — new `.github/workflows/tachi-permissions-verify.yml`: a dual-trigger (`pull_request` + `push:[main]`) gate that reddens the build when a `--no-verify` commit, uninstalled hook, or GitHub web-UI edit breaks `.claude/settings.json` JSON validity or orphans a rule vs. `CLAUDE_PERMISSIONS.md` §4. Four ordered steps under `contents: read`: jq-presence guard → `jq empty` → reused #280 AC-2 cross-check → §3/§4 doc-presence greps. Closes the direct-to-main bypass.
- **gitleaks default-rule coverage catalog** (#285, SC-2) — `PRECOMMIT_HOOKS.md §3` maps each canonical credential pattern to an empirically-confirmed rule ID (5/6 covered; the generic high-entropy hex gap filed as enhancement #348).
- **Adopter-extensibility template** (#286, SC-3) — `.gitleaks.toml.adopter-template` (90 LOC, config-valid, 4 sections: custom rules / allow-list / per-rule severity / tool-swap), referenced from `PRECOMMIT_HOOKS.md §9.5` and `README.md`.
- **gitleaks pin-bump cadence surface** (#287, SC-4) — `PRECOMMIT_HOOKS.md §10` documents the single re-testable bump recipe (tag → `autoupdate --freeze` → 16-fixture re-test → rule-ID re-derivation → doc updates), plus `.github/ISSUE_TEMPLATE/gitleaks-bump.md` and an ADR-042 §References wire-up.
- **Zero new CI cost on unrelated commits** (SC-5) — path-filtered via a single YAML anchor shared across both triggers; a PR touching no governed path does not run the workflow.

---

## How to See & Test

1. **CI gate green on clean `main`** — the workflow's four steps all pass on the current tree: `jq empty .claude/settings.json` (rc=0), `bash .aod/scripts/bash/claude-permissions-ac2-crosscheck.sh` (exit 0 — 93 rules ↔ 93 §4 rows, byte-exact), and `grep -qE '^## 3\. Settings precedence'` + `^## 4\. Per-rule rationale table` on `docs/standards/CLAUDE_PERMISSIONS.md`.
2. **Failure reddens the build** — inject a JSON syntax error into `.claude/settings.json` (or orphan a rule vs. §4, or delete a §3/§4 heading) on a branch and confirm `tachi permissions-verify` fails at the corresponding step.
3. **Path filter → zero cost** — open a PR touching none of `[.claude/settings.json, docs/standards/CLAUDE_PERMISSIONS.md, .aod/scripts/bash/claude-permissions-ac2-crosscheck.sh, the workflow]` and confirm the workflow does not run (SC-5).
4. **Coverage catalog** — read `docs/standards/PRECOMMIT_HOOKS.md §3`: each canonical pattern maps to a rule ID a fixture hit confirms; the uncovered hex pattern cites #348.
5. **Adopter template validity** — run `gitleaks detect --config=.gitleaks.toml.adopter-template` and confirm no config error.
6. **Pin-bump cadence** — read `docs/standards/PRECOMMIT_HOOKS.md §10` and confirm `.github/ISSUE_TEMPLATE/gitleaks-bump.md` references it as the single source of truth.
7. **Regression** — `bash tests/fixtures/gitleaks-rule-interaction/run.sh` → 16/16; `pre-commit run --all-files` → 0 gitleaks findings.

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | 2.0 eng-days (Team-Lead central; floor 1 / ceiling 3) |
| Actual Duration | Same-day (spec → build → deliver, 2026-07-01) |
| Variance | On-target / slightly under — landed at the estimate floor; near-1:1 workflow clone + verbatim #280 script reuse meant zero net-new verification logic |

---

## Surprise Log

The `feat(281)` squash-merge folded into the **already-open** 4.46.0 release-please PR (#341, opened earlier by #329, not yet shipped) rather than starting a fresh release — so two independently-delivered CI-hardening features (F-329 + F-281) will now ship together in one v4.46.0 release train. Expected release-please behavior, but worth noting: a same-day delivery does not always mean a same-day version bump.

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| Pattern | Porting an already-delivered *local* check into a CI gate is a near-1:1 structural clone of an existing sibling workflow (reuse its YAML-anchor path-filter shape) plus a verbatim invocation of the already-shipped verification *script*; the only net-new line is a presence-guard for the tool the gate shells out to (jq), so runner-image drift fails the gate loudly instead of silently stopping it governing. Zero over-build; same-day landing. | Entry 20 in INSTITUTIONAL_KNOWLEDGE.md |

---

## Feedback Loop

**New Ideas**: None net-new at deliver.

- Enhancement #348 (generic high-entropy hex-pattern coverage gap) was already filed at build time during the #285 empirical probe — no additional retrospective ideas emerged. Two architect advisories were logged as non-blocking and require no follow-up issue: FR-281.7 jq-guard is forward-looking runner-drift insurance; the `gitleaks-bump.md` §10 anchor is a heading-slug deep link a future §10 rename would silently break.

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | specs/281-ci-governance-hardening-tail/spec.md |
| Implementation Plan | specs/281-ci-governance-hardening-tail/plan.md |
| Task Breakdown | specs/281-ci-governance-hardening-tail/tasks.md |
| PRD | docs/product/02_PRD/281-ci-governance-hardening-tail-2026-06-30.md |

---

## Test Evidence

### Test Scenarios (Living Documentation)

| AC ID | Given/When/Then | Scenario(s) | Status |
|-------|-----------------|-------------|--------|
| — | Infra/docs feature — no executable application code; ACs verified via CI-gate behavior + failure-injection at build (T006/T018), not Gherkin scenarios | — | Manual/CI |

### Execution Evidence

#### E2E Validation Gate

| Field | Value |
|-------|-------|
| Status | error (no E2E test contract for active pack `knowledge-system`) |
| Gate Mode | hard (default posture; no valid gate evaluation ran) |
| Gate Result | skip (non-blocking per ADR-006) |
| Tests Passed | N/A |
| Tests Failed | N/A |
| Tests Skipped | N/A |

**Failure Details**: N/A — `stack-contract-lint.sh stacks/knowledge-system/STACK.md` exit 5 (no `aod-test-contract` block); knowledge systems produce markdown/YAML, not runnable code. Gate skipped without halting.

#### Build-Wave Test Results

| Wave | Tests | Passed | Failed | Status |
|------|-------|--------|--------|--------|
| wave-1 | 0 | 0 | 0 | skipped (infra/docs) |
| wave-2 | 0 | 0 | 0 | skipped (docs) |
| wave-3 | 0 | 0 | 0 | skipped (docs) |
| wave-4 | 0 | 0 | 0 | skipped (polish) |

**Build Summary** (`specs/281-*/test-results/summary.json`): `waves_tested: 0`, `waves_skipped: 4`, `total_regressions: 0`. No executable code to unit/E2E test. Verification was CI-behavioral: T006 failure-injection smoke test (each governed file reddens its step), T017 regression (`gitleaks-rule-interaction/run.sh` 16/16 + `pre-commit run --all-files` 0 findings), T018 AC 7/7 + SC 5/5 sweep, and the live 4/4 green CI checks on PR #347.

**Notes**: No test artifacts beyond `summary.json` archived — this feature ships CI configuration and documentation, not application code.

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 2 (PRD INDEX.md → Delivered/2026-07-01 + PR row; PRD front-matter → Delivered) | APPROVED |
| Architecture | architect | 2 (Tech_Stack workflow-inventory row; system_design no-ADR CARVE-IN note + link fix) | APPROVED |
| DevOps | devops | 2 (CI_CD_GUIDE.md permissions-verify section; environment-variables.md no-new-vars audit note) | pass |

---

## Cleanup

- [x] Feature branch deleted (squash-merge `--delete-branch`)
- [x] All tasks complete (18/18)
- [x] No TBD/TODO in docs
- [x] Committed and pushed (PR #347 → `cf8ef12`; closure docs direct-to-main)
- [ ] GitHub Issue closed (`stage:done`) — #281 lead + #285/#286/#287 members (command Step 10)

**Feature 281 is now officially CLOSED.**
