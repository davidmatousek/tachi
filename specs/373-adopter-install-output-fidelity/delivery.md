# Delivery Document: Feature 373 — Adopter Install + Output Fidelity Fixes

**Delivery Date**: 2026-10-10
**Branch**: `373-adopter-install-output-fidelity` (deleted at merge)
**PR**: #375, squash-merged as `109705c` (`fix(373): adopter install + output fidelity fixes (#375)`)
**Release**: v4.48.1 (patch), via release-please PR #376
**Closes**: #373; #370 (folded in per PRD decision D-4)

---

## What Was Delivered

- **Installs are complete again.** `install.sh` now ships the three skills that earlier manifests left out (`tachi-output-integrity`, `tachi-misinformation`, `tachi-human-trust-exploitation`) and the Affected Assets populator `scripts/populate-affected-assets.py`. A fail-closed manifest-completeness check in CI keeps the gap from reopening (K1, K2; US-1, US-5).
- **The installer never writes or deletes through a symlink without consent.** If a destination is a symlink or passes through one, the install stops before anything is written. `--follow-symlinks` opts in: the installer names each resolved destination and never deletes through a link. Some cases are refused even with the flag: broken, looping or wrong-type links, links nested inside an installed folder, destinations inside the tachi clone, and tab or newline bytes in a path. Containment is checked by file identity, not by path spelling (K3; US-2).
- **Infographics render again.** The image request shape is fixed; v4.48.0's request was rejected with HTTP 400. The model chain moves to the GA models, `gemini-3-pro-image` then `gemini-3.1-flash-image`, because every model tachi previously named has shut down. All six templates rendered live, with no leaked prompt text and no out-of-scope IDs (K14, K15; US-4a, US-4b).
- **Reports match their source artifacts.**
  - A finding with no controls recommendation shows the threat model's mitigation, marked `Threat-model mitigation:`, or `No recommendation available` when neither exists.
  - MAESTRO headings and delta-status brackets are normalized.
  - One posture label appears on every surface.
  - An older `report-data.typ` without posture data stops with an instruction to regenerate it (K9, K10, K12, K13; US-3a, US-3c).
- **The risk funnel narrows by risk volume.** Its Risk Reduction figure, which the baseball card also shows, is computed from the compensating-controls rows (K11; US-3b).
- **The FR-012b form-drift guard is test-covered** (#370; US-6).
- **A pre-existing path traversal is closed.** Attack-tree finding IDs are validated where they are parsed, and both write sites assert that the resolved path stays inside its folder. A crafted `../` ID can no longer write outside the report folder (CWE-22; also present in v4.48.0).

---

## How to See & Test

> Run the test commands in a **scratch clone** (`git clone --no-hardlinks . "$SCRATCH/tachi"`), never in the main working tree. The report tests render into `examples/` (#365).

1. **Install completeness.**
   - In a scratch project, run `git -C ~/Projects/tachi pull && ~/Projects/tachi/scripts/install.sh`.
   - Confirm that `.claude/skills/tachi-output-integrity/`, `.claude/skills/tachi-misinformation/`, `.claude/skills/tachi-human-trust-exploitation/` and `scripts/populate-affected-assets.py` exist.
   - Automated: `python3 -m pytest tests/scripts/test_install_manifest_completeness.py -v`.
2. **Symlink refusal.**
   - In a scratch project, replace `.claude/skills` with a symlink to another folder, then run `install.sh`. It prints `install stopped: symlinked destination(s) found. Nothing was written.` and leaves the tree unchanged.
   - Re-run with `--follow-symlinks`. It names the resolved destination and installs into it.
   - Automated, including the macOS `/bin/bash` 3.2 strict leg: `LC_ALL=C python3 -m pytest tests/scripts/test_install_sh_symlink_preflight.py tests/scripts/test_install_sh_ref_restore.py -v`.
3. **Extraction fidelity.** Run `python3 -m pytest tests/scripts/test_tachi_parsers.py tests/scripts/test_extract_infographic_data.py tests/scripts/test_extract_report_data.py tests/scripts/test_extractor_contract_fixes.py tests/scripts/test_executive_architecture_payload.py tests/scripts/test_gemini_request_contract.py tests/scripts/test_extraction_sibling_parity.py -v`.
4. **Report posture.** Run `TACHI_REQUIRE_TYPST=1 python3 -m pytest tests/scripts/test_report_posture_contract.py -v`.
5. **Live render** (`[MANUAL-ONLY]`; needs a Gemini key).
   - Run `/tachi.infographic` on a scratch copy of `examples/maestro-reference`.
   - All six templates render, and the executive-architecture image (3:4) fits one portrait PDF page.
   - The record is in `test-results/k15-renders.md`.
6. **CI.** On `main`, the `tachi install fidelity` workflow (manifest-completeness, extraction-fidelity, report-posture) and both `tachi pytest` legs (ubuntu, macOS) are green.
7. **Release notes (SC-6).** The output of `gh release view v4.48.1 --json body -q .body` contains the Upgrading section of `release-notes-upgrading.md` verbatim.

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | 5.2 days central, band 3.5–7.7 days (the Team-Lead's bottom-up re-cost at `/aod.tasks`; effort 8.31 days). Milestones: target 2026-10-02, realistic 2026-10-05, ceiling 2026-10-07 |
| Actual Duration | 13 days of calendar time, from branch creation on 2026-09-27 to merge on 2026-10-10. Commits landed on 4 days: 09-27, 09-28, 10-06 and 10-10 |
| Variance | **Over on the calendar.** The merge came 3 days after the 10-07 ceiling, but the work itself fit in 4 active days, under the 5.2-day central estimate. The slip came from calendar time between sessions (no commits from 09-29 to 10-05), not from effort growth. No item was carved: TW-0 to TW-7 never fired |

---

## Surprise Log

**Every Gemini image model tachi named was retired or retiring.**
- The template blocks named two preview models, `gemini-3-pro-image-preview` and `gemini-3.1-flash-image-preview`, which shut down on 2026-06-25.
- The reference's `default_model`, `gemini-2.5-flash-image`, shut down on 2026-10-02, which was also the PRD's central delivery date.

So K14 grew from a request-shape fix into a migration to the GA chain (`gemini-3-pro-image`, then `gemini-3.1-flash-image`). The chain is walked on a 404 or 403 only, and a 400 is reported as a loud error row that doesn't block the run. No code had read the templates' Gemini config blocks, so K14 also created that mapping. Source: `research.md` §1, checked against Google's deprecations page on 2026-09-27.

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| Technical pattern | **Check path containment by file identity, never by spelling.**<br>The installer's first design compared physical-path strings. Builtin `pwd -P` keeps the typed case, so an APFS case variant or a firmlink slipped past the prefix test (architect finding N1, ruled AR-1). The fix is a ten-line `[ a -ef b ]` identity walk, `under()` in `scripts/install.sh`.<br>The same class came back twice:<br>• A tab or newline byte in a path desynced the pre-flight's tab-delimited checked set (SEC-K3-07).<br>• A backslash corrupted an `awk -v` value (T036 H-1).<br>So refuse delimiter bytes at the trust boundary, and pass values to `awk` through `ENVIRON`. | Entry 24 in INSTITUTIONAL_KNOWLEDGE.md |

---

## Feedback Loop

**New Ideas**: 10 follow-ups filed at deliver (#377–#386), all at `stage:discover`. The PM drafted them from the build's review record, in generic wording (NFR-6). None duplicates an open issue; each body links the related ones (#342, #364, #365, #369, #374).

- #377: `install.sh --version` passes a dash-leading value to `git checkout` instead of refusing it (SEC-K3-03 class) (type:bug)
- #378: Extractors don't recognize headings in the `Section N: Title` form (P0 A-4) (type:bug)
- #379: A stateless run with a free-text `baseline.source` is treated as a baseline run (N7) (type:bug)
- #380: The project-name parser misses em-dash H1 forms and falls back to "Unknown Project" (type:bug)
- #381: The baseball-card and maestro-stack typography tables specify dark text on their dark background (WCAG) (type:bug)
- #382: The heat-map cell grid has no deterministic extractor source (type:bug)
- #383: The Copilot, Cursor and generic adapter instructions still send the rejected image request to shut-down models (P2) (type:bug)
- #384: A project directory whose name ends in a newline installs into a same-named sibling (the project-path analog of D-1) (type:bug)
- #385: The `scan-log.jsonl` chain hash breaks at entry 34; the break is pre-existing, from F-338 (type:bug)
- #386: Remove F-373 dead code and stale "EXPECTED RED" test annotations (the Step 8 economy advisories plus the final code review's notes) (enhancement)

One more item from the deliver list, key handling in the infographic render instructions, is held for maintainer triage before it is filed.

**Labeling**: these are build follow-ups, so they carry `type:bug` or `enhancement` (as #354–#357 and #365–#370 do) rather than `type:retro`.

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | specs/373-adopter-install-output-fidelity/spec.md |
| Implementation Plan | specs/373-adopter-install-output-fidelity/plan.md |
| Task Breakdown | specs/373-adopter-install-output-fidelity/tasks.md |
| PRD | docs/product/02_PRD/373-adopter-install-output-fidelity-2026-09-27.md |
| Contracts | specs/373-adopter-install-output-fidelity/contracts/{installer-cli,manifest-completeness,extraction-data-contract,gemini-request-and-scaffold}.md |
| Oracle diff | specs/373-adopter-install-output-fidelity/oracle-diff.md |
| Security scan | specs/373-adopter-install-output-fidelity/security-scan.md |
| Release notes | specs/373-adopter-install-output-fidelity/release-notes-upgrading.md |
| #364 handoff | specs/373-adopter-install-output-fidelity/issue-364-handoff.md (posted to #364 on 2026-10-10) |

---

## Test Evidence

### Test Scenarios (Living Documentation)

#### Acceptance Criteria Coverage

| AC ID | Given/When/Then | Scenario(s) | Status |
|-------|-----------------|-------------|--------|
| — | No AC-coverage map was generated: the E2E gate stopped at Step 9a, before AC parsing (stack-contract lint exit 5). The spec's automatable ACs are covered by the pytest modules under How to See & Test; the two live-render ACs are `[MANUAL-ONLY]` | — | — |

<details>
<summary>Full Gherkin</summary>

_(No scenarios declared. The E2E tester stage was not entered; see Execution Evidence.)_

</details>

### Execution Evidence

#### E2E Validation Gate

| Field | Value |
|-------|-------|
| Status | error |
| Gate Mode | hard |
| Gate Result | skip |
| Tests Passed | N/A |
| Tests Failed | N/A |
| Tests Skipped | N/A |
| Duration | N/A |

**Failure Details**: Stack-contract lint exit 5. `stacks/knowledge-system/STACK.md` has no `aod-test-contract` block, so this pack declares no E2E runner. The failure is non-fatal per ADR-006, and the gate was bypassed deterministically. The build-wave pytest suite below is this feature's automated test evidence.

#### Per-Scenario Results

| Scenario | Status | Duration |
|----------|--------|----------|
| — (the tester stage was not entered) | — | — |

#### Command

```bash
/aod.deliver
```

#### Build-Wave Test Results

| Wave | Tests | Passed | Failed | Status |
|------|-------|--------|--------|--------|
| wave-1 (`c4dabd7`) | 87 | 87 | 0 | pass |
| wave-2 (`0448bfb`) | 426 | 424 | 0 | pass |
| wave-3 (`4bea6c5`) | 484 | 482 | 0 | pass |
| wave-4 (`91e4542`) | 487 | 485 | 0 | pass |

**Build Summary**: pass, 1,478 of 1,484 passed.
- **Failures and regressions**: 0 failed, 0 regressions.
- **Skips**: 6, two in each of waves 2–4. They are pre-existing.
- **Wave 5**: docs-only, so no run.
- **Fixes after wave 4**: the T036 findings, SEC-K3-07 and the CWE-22 fix were validated by lane runs and by CI on both operating systems (`wave-04/results.json` fix cycle; `security-scan.md`).

**CI at merge**:
- **Final tip `0ae5881`**: 10 of 10 checks green, including both `tachi pytest` legs (run 38081229239).
- **Code tip `c2212fb`**: all six workflows green (run 38079122731).

#### Artifacts

| Artifact | Path | Summary |
|----------|------|---------|
| Build summary | specs/373-adopter-install-output-fidelity/test-results/summary.json | 4 tested waves, gate pass, 1,478 passed / 0 failed / 6 skipped, 0 regressions |
| Wave results | specs/373-adopter-install-output-fidelity/test-results/wave-0{1..4}/results.json | Per-wave gated-set re-runs in a scratch clone of each wave commit |
| Pre-state | specs/373-adopter-install-output-fidelity/test-results-prestate.md | W0 baseline totals and warning classes |
| Oracle diff | specs/373-adopter-install-output-fidelity/oracle-diff.md | 100% attributed; 0/0/0 at `729fa1b`, `eb5d3fe` and `c2212fb` |
| Live renders | specs/373-adopter-install-output-fidelity/test-results/k15-renders.md | K14: 6/6 templates plus the fallback, and executive-architecture on one portrait page. K15: 7/7 passed on the first iteration. Maintainer's visual check passed 2026-10-10 |
| Test-first records | specs/373-adopter-install-output-fidelity/test-results/{k3,rc1}-test-first.md | Red-then-green evidence for K3 and RC-1 |
| Architect checkpoints | specs/373-adopter-install-output-fidelity/test-results/p{0,1,2}-architect-review.md | P0, P1 and P2, all APPROVED_WITH_CONCERNS |
| Security scan | specs/373-adopter-install-output-fidelity/security-scan.md; .security/reports/c2212fbd8500.sarif | Step 7 PASSED at `c2212fb`; scan 1's HIGH (CWE-22) fixed |

**Archived Artifact Metrics**:
- Tests Run: 1,484
- Passed: 1,478
- Failed: 0
- Coverage: N/A

**Notes**:
- Unit and integration tests ran under pytest, once per wave, in a scratch clone of the wave commit (the #365 PNG hazard).
- CI runs on two operating systems: ubuntu, and macOS with the strict `/bin/bash` 3.2 leg.
- Live renders are manual and recorded in `k15-renders.md`.

### Manual Validation

**Manual-only acceptance criteria** (carried from `spec.md`):

- US-4a AC-5: [MANUAL-ONLY] needs a live API key, network access and a human look at the rendered images. **Result**: PASS (render session 2026-10-06; the record is in `k15-renders.md`).
- US-4b AC-4: [MANUAL-ONLY] image output is non-deterministic and needs a live key plus a human visual check. **Result**: PASS on the first iteration; the maintainer's visual check passed on 2026-10-10.

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 3: PRD frontmatter and status (Delivered 2026-10-10), PRD INDEX row, OKR header | APPROVED_WITH_CONCERNS (see below) |
| Architecture | architect | 4: tech stack (Gemini GA chain, which still named the retired preview models; install-fidelity CI), system design (Feature 373 section), patterns (4 new, 2 extended), README (ADR-014 note pointer) | APPROVED; no new ADR (PD-15) |
| DevOps | devops | 2: CI_CD_GUIDE (`tachi install fidelity` workflow; gated tachi-pytest modules 16 → 18), environment-variables (`TACHI_REQUIRE_TYPST`, a test-only CI variable) | PASS |

**Concerns raised and dispositions**:

| Concern | Disposition |
|---|---|
| **PM C-1**: SC-6 is open until the v4.48.1 notes publish | Closed at release by the SC-6 check (`gh release view`) |
| **PM C-2**: the CHANGELOG and release notes omitted the two late security fixes | Applied before release: the tab/newline path refusal and the CWE-22 fix were added to the CHANGELOG `Unreleased` entry (Added; new Security subsection) and to `release-notes-upgrading.md` |
| **PM C-3**: the `main` pytest run was still in progress | Confirmed green on both legs at `109705c` (run 38083579096) |
| **Architect observations** | ADR index gap (6 ADRs unindexed) and stale size descriptors: pre-existing hygiene. Adapter drift: filed as a follow-up (Feedback Loop) |

Documentation agents modified 9 files. The orchestrator added the CHANGELOG and release-notes edits (C-2), this document and KB Entry 24.

---

## Cleanup

- [x] Feature branch deleted (local and remote, at merge)
- [x] All tasks complete (40/40)
- [x] No TBD/TODO in docs
- [x] Committed and pushed
- [x] GitHub Issue closed (`stage:done`)
- [ ] The 18 build-lane branches and their scratch worktrees still need removing. All 18 were verified integrated: 13 are patch-equivalent, 2 were cherry-picked with conflict resolution, and 3 were folded into wiring commits. Removal was permission-blocked for the agent, so it is handed to the maintainer.

**Feature 373 is now officially CLOSED.**
