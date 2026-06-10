# Delivery Document: Feature 272 — SECURITY.md and Private Disclosure Channel (F-3)

**Delivery Date**: 2026-05-08
**Branch**: `272-security-md-disclosure`
**PR**: #273 (squash-merged as commit `7b1cc53` on main)
**Initiative**: BLP-02 enterprise-hardening Wave 3 (3-of-5 features delivered)

---

## What Was Delivered

- **`SECURITY.md` rewritten to GitHub-canonical 5-section structure** (51 LOC, replacing prior 40-LOC 2026-03-26 version): **Supported Versions** → **Reporting a Vulnerability** → **What to expect** → **Scope** → **Out-of-scope**. Section names match GitHub Docs verbatim where prescribed.
- **GitHub Private Vulnerability Reporting toggle ENABLED** in repo Settings → Code security and analysis. The *Report a vulnerability* button is now visible on the Security tab as a primary call-to-action, surfacing a private disclosure channel for security researchers without requiring them to read SECURITY.md first.
- **Procurement-defensible disclosure contract** — 5-business-day acknowledgment SLA, assessment-within-1-week commitment, fix-timeline-after-assessment commitment, credit clause (researcher named in fix commit + release notes by default; anonymity available on request). CAIQ/SIG-Lite "vendor disclosure policy" + "supported versions" rubrics now mark GREEN.
- **`README.md` `## Community` section** received the AC-12 one-line `[SECURITY.md](SECURITY.md)` pointer for in-IDE discoverability, sibling to the existing security-vulnerabilities advisory bullet.
- **`CHANGELOG.md` `## Unreleased` block** received the F-3 entry as a sibling-h3 BLP-02 cluster heading (between the F-2 BLP-02 entry and `### Bug Fixes`), preserving the BLP-02-cluster grouping convention.
- **Closes `/security` finding TACHI-VULN-05abc41ad4cc** (INFO, A05 Security Misconfiguration) — recorded as REMEDIATED in `.aod/results/security-scan.md` at scan_id `5345e7a2-5944-486c-b6e7-8e57e238261e` ts `2026-05-08T17:32:45Z`; chain_hash `337228…` continuous.
- **Release-please PR #274** `chore(main): release 4.33.0` opened automatically within seconds of the squash-merge (`feat(272):` prefix preserved); F-212 empty-marker recovery flow NOT triggered (release-please reacted instantly).

---

## How to See & Test

1. **Repo-root file**: Run `cat SECURITY.md` and verify the 5-section structure (Supported Versions, Reporting a Vulnerability, What to expect, Scope, Out-of-scope) is present in canonical order.
2. **GitHub-rendered view**: Open `https://github.com/pratik-saptarshi/tachi-rust/blob/main/SECURITY.md` and confirm the file renders cleanly with all five sections.
3. **Security-tab button**: Open `https://github.com/pratik-saptarshi/tachi-rust/security` in an authenticated browser session and confirm the *Report a vulnerability* button is visible as a primary call-to-action (FR-011, AC-7).
4. **Advisory submission form**: Open `https://github.com/pratik-saptarshi/tachi-rust/security/advisories/new` and confirm the form loads (no 404, no permission error). Do NOT submit (FR-012, AC-11 smoke-test only).
5. **README pointer**: Run `grep -A2 "## Community" README.md` and confirm the `**Full security policy** → [SECURITY.md](SECURITY.md)` bullet appears under `## Community`.
6. **CHANGELOG entry**: Run `grep -A20 "BLP-02 F-3" CHANGELOG.md` and confirm the F-3 sibling-h3 entry is present in the `## Unreleased` block.
7. **Operational cross-check** (FR-003): Run `cat .release-please-manifest.json && git tag --list 'v*' | sort -V | tail -5 && gh pr list --state open --search "release-please" --limit 3` and verify that the SECURITY.md worked-example tag matches the latest released tag (currently `v4.32.0`; release-please PR #274 will bump to `4.33.0` on squash-merge).
8. **Post-merge `/security` re-scan**: Confirm `.aod/results/security-scan.md` records `TACHI-VULN-05abc41ad4cc → REMEDIATED` (FR-013, AC-9, AC-10).
9. **Procurement rubric**: Apply CAIQ/SIG-Lite "vendor disclosure policy" + "supported versions" rubric to SECURITY.md and confirm both line items pass (US-5 procurement reviewer scenario).

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | Same-day docs-only (≤4 hours active maintainer time per PRD SC-008) |
| Actual Duration | Same-day (branch first commit 2026-05-08 11:21 UTC-4 → squash-merge 2026-05-08 16:10 UTC) |
| Variance | On-target (within PRD SC-008 4-hour active-time cap; same-day wall-clock target met) |

---

## Surprise Log

Smooth — no major surprises. The two carry-forward IK notes flagged at the P2 Architect checkpoint (N-2 D-6 sequence variance, N-4 CHANGELOG blueprint placement deviation) are minor process observations rather than delivery surprises and are captured in KB Entry 4 as reusable patterns.

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| Technical pattern | Documentation-only DoD via Constitution Principle VII §Exceptions; GitHub-canonical SECURITY.md 5-section template; CHANGELOG sibling-h3 BLP-02-cluster placement convention. Three reusable patterns: (1) docs-only features can satisfy DoD via post-merge instrumentation in lieu of automated tests when the exemption is documented in plan.md Constitution Check and `test-results/summary.json` records `waves_skipped` with rationale; (2) the 5-section SECURITY.md template (Supported Versions / Reporting / What to expect / Scope / Out-of-scope) is procurement-defensible and reusable across tachi/AOD-Kit/derivative projects; (3) sibling-h3 cluster placement in CHANGELOG is the keeper for multi-feature initiatives like BLP-02 (the build's actual placement, not the plan blueprint placement, is correct). | Entry 4 in `docs/INSTITUTIONAL_KNOWLEDGE.md` |

---

## Feedback Loop

**New Ideas**: None — the AC-13 and AC-14 follow-up Issues already capture the deferred posture-probe and manifest-discrepancy work; no additional retrospective ideas emerged.

**Already-filed follow-up Issues** (carried from /aod.tasks-time, traced through delivery):
- #275 — `[chore] PVR-toggle posture probe (post-F-3 follow-up)` — periodic check that the GitHub Private Vulnerability Reporting toggle remains ON via API scrape; ICE rough estimate I:6 C:8 E:9.
- #276 — `[chore] release-please manifest-vs-tag discrepancy investigation (post-F-3 follow-up)` — investigate the v4.32.0-tag / 4.31.0-manifest delta observed at PRD draft and re-confirmed at /aod.project-plan; may be naturally resolved by release-please PR #274 (4.33.0) cycle.

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | `specs/272-security-md-disclosure/spec.md` |
| Implementation Plan | `specs/272-security-md-disclosure/plan.md` |
| Task Breakdown | `specs/272-security-md-disclosure/tasks.md` |
| Research | `specs/272-security-md-disclosure/research.md` |
| PRD | `docs/product/02_PRD/272-security-md-disclosure-2026-05-08.md` (v1.1, Approved → Delivered) |
| Security Scan Report | `specs/272-security-md-disclosure/security-scan.md` |
| Test-Results Summary | `specs/272-security-md-disclosure/test-results/summary.json` (waves_skipped: 15 with documented rationale) |
| Agent Assignments | `specs/272-security-md-disclosure/agent-assignments.md` |
| Session Handoff | `specs/272-security-md-disclosure/NEXT-SESSION.md` |

---

## Test Evidence

### Test Scenarios (Living Documentation)

This subsection answers: *"What scenarios exist?"*

#### Acceptance Criteria Coverage

| AC ID | Given/When/Then | Scenario(s) | Status |
|-------|-----------------|-------------|--------|
| AC-1 (US-1) | Given repo root, When researcher opens SECURITY.md, Then Reporting section presents button + URL fallback + public-Issue prohibition | T005 verification (manual; SECURITY.md lines 11/13/15) | Manual |
| AC-2 (US-1) | Given Reporting section, When preparing report, Then "What to include" prompts description/repro/components/impact | T005 verification (manual; SECURITY.md lines 17-22) | Manual |
| AC-3 (US-1) | Given "What to expect", When report submitted, Then 5-bus-day SLA + 1-week assess + fix-timeline + credit clause | T005 verification (manual; SECURITY.md lines 28-31) | Manual |
| AC-4 (US-3) | Given "Supported Versions", When adopter reads, Then v4.x latest-minor-only policy stated | T010 verification (manual; SECURITY.md line 5) | Manual |
| AC-5 (US-3) | Given same section, When adopter reads further, Then worked example references latest tag | T010 verification (manual; SECURITY.md line 7, v4.32.0) | Manual |
| AC-6 (US-3) | Given same section, When `make update` adopter reads, Then pin-to-major recommendation present | T010 verification (manual; SECURITY.md line 7) | Manual |
| AC-7 (US-2) | Given PVR toggle enabled, When auth visitor opens /security, Then *Report a vulnerability* button visible | [MANUAL-ONLY] T008 (UI inspection; FR-011) | Manual |
| AC-8 (CHANGELOG) | Given CHANGELOG `## Unreleased`, Then F-3 feature subsection present matching F-2 precedent | T013 verification (CHANGELOG.md sibling-h3 placement) | Manual |
| AC-9 (security) | Given post-merge `/security` re-scan, Then TACHI-VULN-05abc41ad4cc → REMEDIATED | T021 verification (`.aod/results/security-scan.md`; scan_id `5345e7a2`) | Covered |
| AC-10 (security) | Given post-merge `/security` re-scan, Then no new HIGH/MEDIUM findings introduced | T021 verification (zero new findings; chain_hash `337228…` continuous) | Covered |
| AC-11 (smoke-test) | Given auth session, When opening advisories/new, Then form loads without error | [MANUAL-ONLY] T009 (UI inspection; FR-012) | Manual |
| AC-12 (README) | Given `README.md`, When reader scans top-level sections, Then `[SECURITY.md](SECURITY.md)` reference present | T014 verification (`README.md` `## Community` line 45) | Manual |
| AC-13 | Posture probe | DEFERRED to follow-up Issue #275 | Deferred |
| AC-14 | release-please manifest-vs-tag investigation | DEFERRED to follow-up Issue #276 | Deferred |

**Totals**: 14 ACs total — 12 in-scope ACs pass (10 manual-verified + 2 automated via /security re-scan); 2 deferred to follow-up Issues (#275, #276) per spec §"Out of F-3 scope".

<details>
<summary>Full Gherkin</summary>

_(No automated Gherkin scenarios — F-3 is a documentation-only feature exempted under Constitution Principle VII §Exceptions; verification is via post-merge `/security` re-scan + manual UI inspections per FR-010..FR-013. See `specs/272-security-md-disclosure/test-results/summary.json` for the documented skip rationale.)_

</details>

### Execution Evidence

This subsection answers: *"What happened when they ran?"*

#### E2E Validation Gate

| Field | Value |
|-------|-------|
| Status | skipped |
| Gate Mode | exempt (Constitution Principle VII §Exceptions) |
| Gate Result | skip |
| Tests Passed | N/A |
| Tests Failed | N/A |
| Tests Skipped | N/A |
| Duration | N/A |

**Failure Details**: N/A — Documentation-only feature exempted from automated test gates per Constitution Principle VII §Exceptions noted in plan.md. Verification path: post-merge `/security` re-scan (FR-013 — TACHI-VULN-05abc41ad4cc REMEDIATED) plus three [MANUAL-ONLY] UI inspections (FR-010 toggle, FR-011 button visibility, FR-012 URL smoke-test). All four automated/manual gates passed across Sessions 1-4.

#### Per-Scenario Results

_(No automated scenarios — see exemption rationale above.)_

#### Command

```bash
# No automated E2E command; verification via:
/security                                                    # post-merge re-scan (T021)
gh issue view 272                                            # task traceability
gh pr view 273                                               # squash-merge confirmation
```

#### Artifacts

| Artifact | Path | Summary |
|----------|------|---------|
| Test-results summary | `specs/272-security-md-disclosure/test-results/summary.json` | `waves_skipped: 15`, `waves_tested: 0`, `total_regressions: 0` with documented Principle VII §Exceptions rationale |
| Security scan report | `specs/272-security-md-disclosure/security-scan.md` | Post-merge `/security` re-scan result; PASSED status with REMEDIATED event for TACHI-VULN-05abc41ad4cc |
| Live security log | `.aod/results/security-scan.md` | Mirror of the scan-log per architect N-4 path; chain_hash `337228…` continuous |

**Archived Artifact Metrics**:
- Tests Run: 0 (exempted)
- Passed: N/A
- Failed: 0
- Coverage: N/A

**Notes**: Documentation-only feature; no source code change; no automated test runner invoked. Verification via post-merge `/security` re-scan (closes TACHI-VULN-05abc41ad4cc) plus three [MANUAL-ONLY] UI inspections per FR-010/FR-011/FR-012. All gates PASSED across Sessions 1-4. Skip rationale per Constitution Principle VII §Exceptions + plan.md Principle VI exemption is recorded explicitly in `specs/272-security-md-disclosure/test-results/summary.json` for traceability.

### Manual Validation

This subsection answers: *"What was not automated?"*

**Manual-only acceptance criteria** (carried from `spec.md` and verified during build):

- AC FR-010: [MANUAL-ONLY] GitHub repo-settings UI is not script-accessible from F-3's tooling; the Private vulnerability reporting toggle change must be performed in-browser by an account with repo-admin rights. Verified at T006: maintainer confirmed toggle is ON via repo settings UI; plain-text confirmation captured per D-5: `Toggle confirmed ON at 15:34 UTC 2026-05-08 via repo settings UI`.
- AC FR-011: [MANUAL-ONLY] *Report a vulnerability* button visibility on Security tab — UI inspection, no programmatic check in F-3 scope. Verified at T008: maintainer confirmed button visible on Security tab in authenticated browser session. Posture-probe automation deferred to follow-up Issue #275.
- AC FR-012: [MANUAL-ONLY] Authenticated-UI smoke-test of advisory submission URL — no automation in F-3 scope. Verified at T009: maintainer confirmed advisory submission form loads cleanly (no 404, no permission error); form not submitted per spec.

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 2 (`docs/product/02_PRD/INDEX.md` row 272 Approved→Delivered + PR #273 link; `docs/product/02_PRD/272-security-md-disclosure-2026-05-08.md` frontmatter status + delivered/pr/squash_commit fields) | APPROVED |
| Architecture | architect | 0 (correctly: no architectural surface change for docs-only F-3; no ADR per plan.md §Governance; no system-design auto-scaffold entry needed) | APPROVED |
| DevOps | devops | 0 (correctly: zero CI/CD/infra/env-var/pipeline impact for docs+repo-setting feature) | APPROVED |

T024 (PRD INDEX flip) handled by product-manager agent in Step 3. T025 (BLP-02 memory file Wave 3 → DELIVERED 3-of-5) handled in Step 6 retrospective. Both deferred-to-/aod.deliver-time tasks now complete.

---

## Cleanup

- [x] Feature branch deleted (local + remote `272-security-md-disclosure`)
- [x] All in-scope tasks complete (23 build-time + T024 + T025 = 25/25)
- [x] No TBD/TODO in docs (PRD wave-table row 272 flipped from `TBD` to `Delivered (PR #273)` / `2026-05-08`)
- [x] Committed and pushed (closure commit `d5ca474` + user-stories export `14aef56` on main)
- [x] GitHub Issue #272 closed (`stage:done` transition complete; closing comment cross-references `specs/272-security-md-disclosure/delivery.md`)

**Feature 272 is now officially CLOSED.**
