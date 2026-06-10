# Delivery Document: Feature 277 — F-4 Claude Permissions Baseline (BLP-02 Wave 4)

**Delivery Date**: 2026-05-09
**Branch**: `277-claude-permissions-baseline` (deleted at /aod.deliver-time, was `86a868e` pre-squash, squash-merge at `896588b` on `main`)
**PR**: [#278](https://github.com/pratik-saptarshi/tachi-rust/pull/278)
**Release**: release-please [PR #279](https://github.com/pratik-saptarshi/tachi-rust/pull/279) `chore(main): release 4.34.0` (open at delivery-time, opened ~23s post-squash-merge — within FR-013 ~30s SLO)
**Initiative**: BLP-02 enterprise hardening Wave 4 — closes 4-of-5 features delivered

---

## What Was Delivered

- **Curated `.claude/settings.json` baseline** (~80 LOC after Cat-1 dedup) — categorized read-only / local-state / destructive deny+ask / network host-allowlist; built-in read-only auto-approve preserved without explicit allow entries (verified via `git status` no-rule probe at T009/T025); cross-list `deny → ask → allow` first-match-wins precedence verified via `git push --force` shadow probe at T011/T026; AC-12 cross-file deny precedence (project `settings.json` deny shadows local `settings.local.json` allow) verified at T015.
- **`docs/standards/CLAUDE_PERMISSIONS.md`** (~250 LOC self-contained policy decision log) — per-rule rationale catalog with audit-policy framing for SecOps reviewers, settings-precedence with cross-list + cross-file worked examples, three documented opt-out paths (Path 1 disable / Path 2 fork / Path 3 explicit edit), inline AC-7 ANOMALY note documenting the WebFetch transitive-subdomain-collapse mechanic for future-maintainer regression detection.
- **ADR-041 accepted** (~100 LOC, 6 alternatives-considered) — curated static rule set vs PreToolUse hooks vs managed-settings layer vs runtime gating vs hybrid vs status-quo. Decision: curated static rule set with documented opt-out paths.
- **CHANGELOG.md entry** with sibling-h3 BLP-02-cluster placement (`### Claude Code permissions baseline (BLP-02 F-4)`) preserving the N-4 carry-forward convention from F-3 / Entry 4.
- **`.gitignore` exclusion** for `.claude/settings.local.json` (FR-003) — adopters' personal customizations remain unversioned and survive `git pull` of F-4.
- **Two follow-up Issues filed** at /aod.tasks-time per AC-15/AC-16 nice-to-haves: [#280](https://github.com/pratik-saptarshi/tachi-rust/issues/280) (pre-commit hook for `.claude/settings.json` jq-validity + AC-2 cross-check, ICE I:5 C:7 E:8) and [#281](https://github.com/pratik-saptarshi/tachi-rust/issues/281) (CI integration for the F-4 verification recipe, ICE I:6 C:6 E:7).

**Posture-gap closure** (NOT vuln closure): F-4 closes ZERO `/security` `vuln_id`. The deliverable is the audit-policy posture (named in 2026-05-02 Daniel Wood LinkedIn enterprise-developer-environments thread as a load-bearing prerequisite for SecOps-reviewed managed environments), not a vulnerability remediation.

---

## How to See & Test

1. **Inspect the baseline JSON validity**: `jq empty .claude/settings.json` should exit 0; `jq '.permissions | keys' .claude/settings.json` should print `["allow", "ask", "deny"]` (any of which MAY be empty arrays).
2. **Read the per-rule rationale catalog**: open `docs/standards/CLAUDE_PERMISSIONS.md` and confirm every non-built-in rule from `.claude/settings.json` appears at least once with columns Rule / Category (1–4) / Rationale / Failure mode.
3. **Cross-check rule-to-doc parity** (AC-2): the `awk` section-marker form codified in PR #278 §architect-P1-Minor-#2 reconciliation (`ec0b628`) should report ZERO orphaned rules and ZERO orphaned table rows.
4. **Probe cross-list deny precedence** (AC-12): in an interactive Claude Code session loaded with the merged baseline, attempt `Bash(git push --force origin <test-branch>)`. The harness MUST emit a deny prompt — not auto-approve via the broader `Bash(git push:*)` allow.
5. **Probe built-in read-only auto-approve** (AC-6 sub-check b / T009 / T025): run `Bash(git status)` in an agentic session. The harness should auto-approve with no explicit rule match (built-in mechanic operates outside the explicit allow array).
6. **Probe destructive deny rules** (AC-6 sub-check c / T011 / T026): attempt any Tier-3a deny rule (`Bash(rm -rf <path>)`, `Bash(git reset --hard:*)`, `Bash(gh release delete:*)`, `Bash(gh repo delete:*)`, `Bash(npm publish:*)`). The harness MUST surface a deny prompt before execution.
7. **Probe ask rules** (AC-6 sub-check d): attempt a Tier-3b `ask` rule (`Bash(git push --force-with-lease:*)`, `Bash(gh release create:*)`, `Bash(brew install:*)`). The harness MUST present an ask prompt distinct from a deny prompt and distinct from auto-approve.
8. **Verify WebFetch transitive subdomain collapse** (AC-7 ANOMALY / T018): with the F-4 baseline loaded, attempt `WebFetch https://gist.github.com/<some-public-gist-url>`. The harness should auto-approve under the parent `WebFetch(domain:github.com)` rule — this is the AC-7 ANOMALY (subdomain auto-approval under parent rule) documented inline in `docs/standards/CLAUDE_PERMISSIONS.md` so it is not mistaken for a regression.
9. **Verify customizations survive upgrade** (AC-11): create a fixture `.claude/settings.local.json` with a custom allow/deny, pull F-4, confirm the local file is unchanged and rules still resolve as expected.
10. **Verify release-please trigger fired** (FR-013): `gh pr list --state open --search "release-please" --limit 3` should return [PR #279](https://github.com/pratik-saptarshi/tachi-rust/pull/279) `chore(main): release 4.34.0`. F-212 recovery flow (empty release-marker commit) should NOT have been triggered.
11. **Verify post-merge security regression**: `.aod/results/security-scan.md` records the post-merge scan as PASSED with no new HIGH or MEDIUM findings; `.security/scan-log.jsonl` chain_hash continuity preserved.

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | 1-2 days (PRD estimate ~8-9h active envelope / next-day wall-clock target) |
| Actual Duration | ~22h22m wall-clock (branch created 2026-05-08T22:04:54Z PRD landing → squash-merged 2026-05-09T16:24:37Z) |
| Variance | On target — within ~1h of PRD wall-clock estimate; ICE I:8 C:7 E:7 was accurate |
| Tasks Complete | 30/30 (14 FRs / 14 ACs / 5 user stories all satisfied) |
| Release-please Latency | ~23s squash-merge → release-please PR open (FR-013 SLO ~30s) |
| Post-merge /security | PASSED (regression-only check; F-4 change set has zero SAST-eligible files and zero SCA-eligible manifests; strict-protocol diff produced empty SAST + SCA paths) |

---

## Surprise Log

**AC-7 transitive subdomain collapse (gist.github.com)**: PRD R-7 hypothesized that `WebFetch(domain:X)` rules might require explicit subdomain entries (e.g., a separate rule for `gist.github.com` alongside `github.com`). T018 verification probe with `WebFetch https://gist.github.com/...` confirmed the surprising opposite mechanic: subdomains auto-approve transitively under parent rules. The architect's HIGH-2 v1.1 cascade had preemptively reconciled the rule set to rely on this transitive-collapse, removing 7 redundant github-family explicit entries. The build-stage flip was therefore zero-cost — but the mechanic itself was an unexpected discovery worth documenting inline in `CLAUDE_PERMISSIONS.md` §AC-7-ANOMALY so future maintainers don't mistake it for a regression. Issues #15260, #11972, and #1217 in the upstream Claude Code repo reference this same behavior. The discovery opened the AC-15 + AC-16 follow-up surface filed at /aod.tasks-time as Issues [#280](https://github.com/pratik-saptarshi/tachi-rust/issues/280) and [#281](https://github.com/pratik-saptarshi/tachi-rust/issues/281).

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| Technical pattern | Cross-list precedence + transitive subdomain collapse pattern: Claude Code permissions evaluate as `deny → ask → allow` first-match-wins across both project and local settings, but `WebFetch(domain:X)` rules collapse transitively to subdomains (gist.github.com auto-approves under parent github.com), so when designing a host-allowlist always ask whether subdomain auto-approval is intentional — and document the AC-7 ANOMALY explicitly so future maintainers don't mistake it for a regression. Apply at any future stack-pack permissions baseline or downstream adopter fork. | Entry 5 in `docs/INSTITUTIONAL_KNOWLEDGE.md` |

---

## Feedback Loop

**New Ideas**: 0 net-new (the deferred AC-15 pre-commit hook + AC-16 CI integration nice-to-haves were filed at /aod.tasks-time as [#280](https://github.com/pratik-saptarshi/tachi-rust/issues/280) (ICE I:5 C:7 E:8) and [#281](https://github.com/pratik-saptarshi/tachi-rust/issues/281) (ICE I:6 C:6 E:7) before delivery — both already on the discovery backlog).

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | `specs/277-claude-permissions-baseline/spec.md` |
| Implementation Plan | `specs/277-claude-permissions-baseline/plan.md` |
| Task Breakdown | `specs/277-claude-permissions-baseline/tasks.md` |
| PRD | `docs/product/02_PRD/277-claude-permissions-baseline-2026-05-08.md` |
| ADR | ADR-041 (Claude Permissions Baseline; 6 alternatives-considered) |

---

## Test Evidence

### Test Scenarios (Living Documentation)

This subsection answers: *"What scenarios exist?"*

#### Acceptance Criteria Coverage

| AC ID | Given/When/Then | Scenario(s) | Status |
|-------|-----------------|-------------|--------|
| — | (No automated scenarios — F-4 is a docs + config feature; verification recipe is interactive Claude Code probes documented in the "How to See & Test" section above) | — | Manual (interactive probes) |

**Totals**: 14 ACs in `spec.md` — verified manually at /aod.build via build-stage T008-T020 captures (interactive Claude Code session probes); no automated scenarios because the verification surface (Claude Code permission resolution, harness prompt behavior) is not addressable from a Playwright/pytest runner.

<details>
<summary>Full Gherkin</summary>

_(No automated Gherkin scenarios — F-4's verification recipe consists of interactive Claude Code session probes captured per-AC in `tasks.md` build-stage capture lines T008-T020. See `tasks.md` for the literal probe commands and harness responses.)_

</details>

### Execution Evidence

This subsection answers: *"What happened when they ran?"*

#### E2E Validation Gate

| Field | Value |
|-------|-------|
| Status | `error` (skill Step 9a exit 5: missing `aod-test-contract` block in `stacks/knowledge-system/STACK.md`) |
| Gate Mode | `hard` (default; no `--no-tests=<reason>` opt-out passed) |
| Gate Result | `skip` (status=error short-circuited the gate per data-model §2 — non-fatal per ADR-006) |
| Tests Passed | N/A |
| Tests Failed | N/A |
| Tests Skipped | N/A |
| Duration | N/A |

**Failure Details**: N/A — gate did not run because the active stack pack (`knowledge-system`) does not declare an `aod-test-contract` block in `STACK.md`. Per skill Step 9a exit-code taxonomy, this stores `e2e_validation.status = "error"` and proceeds to Step 10 (test evidence collection) without halting delivery. The verification surface for F-4 (Claude Code permission resolution, harness prompt behavior under interactive sessions) is not addressable from an automated runner.

#### Per-Scenario Results

(No scenarios executed — see E2E Validation Gate Status above.)

#### Command

```bash
/aod.deliver 277
```

#### Artifacts

| Artifact | Path | Summary |
|----------|------|---------|
| Post-merge security scan | `.aod/results/security-scan.md` | PASSED — zero new HIGH/MEDIUM findings; F-4 change set has zero SAST-eligible files and zero SCA-eligible manifests |
| SARIF (post-merge) | `.security/reports/c99c46d0bab9.sarif` | Empty `results[]` and `rules[]`; `invocations[].properties` document scan context |
| Build-stage captures (per-AC) | `specs/277-claude-permissions-baseline/tasks.md` (T008-T020 build-stage capture lines) | Interactive Claude Code session probe records for each AC |

**Archived Artifact Metrics**:
- Tests Run: 0 automated (manual interactive probes per-AC, captured in tasks.md)
- Passed: 14/14 ACs verified at /aod.build time
- Failed: 0
- Coverage: N/A (probe-based verification, not coverage-instrumented)

**Notes**: F-4 is a docs + config feature with no executable surface addressable by Playwright/pytest runners. Verification was performed via interactive Claude Code session probes documented per-AC in `tasks.md` at /aod.build time; the harness response (auto-approve / deny prompt / ask prompt) is the test signal. Build-stage captures preserve the literal probe command and harness response for each AC, providing an auditable manual-verification trail in lieu of automated test artifacts. Per Constitution Principle VII §Exceptions (the same exemption clause F-3 codified in Entry 4 Pattern 1), documentation-only and config-only features may not require automated coverage.

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 1 (`docs/product/05_User_Stories/README.md` — header + new Feature 277 section) | APPROVED |
| Architecture | architect | 3 (`docs/architecture/00_Tech_Stack/README.md`, `docs/architecture/README.md`, `docs/standards/README.md`) | APPROVED |
| DevOps | devops | 1 (`docs/devops/README.md` — Feature 277 Additions section, low-infra-surface anchor following F-130/F-142/F-158 precedent) | APPROVED |
| **Total** | | **5 agent-modified + 2 deferred-task edits** (`docs/product/02_PRD/INDEX.md` row-277 flip + `tasks.md` T023/T029/T030 closure) | |

Detailed agent findings: `.aod/results/product-manager.md`, `.aod/results/architect.md`, `.aod/results/devops.md`.

---

## Cleanup

- [x] Feature branch deleted (local + remote `origin/277-claude-permissions-baseline`)
- [x] All 30 tasks complete (`tasks.md` shows 0 incomplete)
- [x] No new TBD/TODO introduced in delivery docs
- [x] Committed and pushed (closure docs commit follows in this same /aod.deliver run)
- [x] GitHub Issue [#277](https://github.com/pratik-saptarshi/tachi-rust/issues/277) closed with `stage:done`

**Feature 277 is now officially CLOSED.**
