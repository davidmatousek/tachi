# Delivery Document: Feature 362 — Remap OWASP LLM Top 10 Coverage to the 2026 Edition

**Delivery Date**: 2026-08-12
**Branch**: `362-remap-owasp-llm-top10-2026` (deleted after squash-merge)
**PR**: #363 — squash-merged as `e6316e3` (`feat(362): remap OWASP LLM Top 10 coverage to the 2026 edition`) → release-please PR #371 (v4.48.0)

---

## What Was Delivered

- **Findings cite the current standard (US-1)**: all 10 LLM records in `schemas/taxonomy/owasp.yaml` now carry 2026 identity — `full_id: OWASP-LLM-2026-NN`, verbatim 2026 canonical names (including the LLM08:2026 **Hidden Context Exposure** rename of System Prompt Leakage, with the 2025 name retained as a historical alias on presentation surfaces), and live-verified citation URLs anchored to the official 2026 release resource page (D9 interim policy, validated by the deliver-stage link-rot dispatch: 908 checked, 0 confirmed rot).
- **Crosswalk survived the re-meaning**: all 74 LLM-touching crosswalk edges dispositioned in an append-only ledger; the 57 re-keys executed as a single simultaneous permutation (the 8-id bijection collides on the dedupe key if done sequentially); taxonomy integrity suite green — 0 duplicates, primary-edge floor intact.
- **Every emission surface re-cited**: 9 agent personas, 15 skill reference files, all 4 adapter sets (claude-code, copilot, cursor, generic) + legacy `agents/`, `schemas/finding.yaml` example blocks, and output templates now emit 2026 tokens per the ADR-048 grammar, with one-release 2025 breadcrumbs.
- **Consumer cutover policy is a governed contract (US-2)**: ADR-048 (hard cutover + self-describing legacy tokens at the token-grammar layer, zero schema shape churn) Accepted with commit SHA `e6316e3`; CHANGELOG ships the full 10-row movement map, alias policy, and the examples/** carve-out disclosure including the mid-window 2025-attribution risk.
- **Coverage claim stays honest (US-3)**: per-category coverage re-derived against 2026 definitions — **10/10 Covered with cited detection evidence, 50/50 OWASP claim maintained**; PM SC-005 claim-honesty re-verification run at deliver before PR-ready: APPROVED, 0 Partial verdicts, all restatement surfaces consistent (`.aod/results/product-manager-sc005.md`).
- **Structural hardening**: `generate-risk-scores-sarif.py` now derives LLM category names from the catalog (both former hardcoded sites removed); `normalize_owasp_id` gained its first covering test; net-new `tests/scripts/test_owasp_2026_contract.py` (287 lines) + catalog-drift guard additions lock the 2026 contract; `tachi-pytest.yml` gated subset extended in lockstep.
- **Auditability**: two disposition ledgers (74-row crosswalk, 366-occurrence bare-code census with lane partitioning) account for every occurrence of the repo-wide sweep (498 suffixed occurrences / 77 files at the pinned research SHA `747805c`); zero unreviewed 2025 references outside the FR-008 exclusion list.

---

## How to See & Test

1. **Catalog identity**: `grep -A3 "id: LLM" schemas/taxonomy/owasp.yaml | head -40` — every LLM record shows `full_id: OWASP-LLM-2026-NN` and a 2026 name.
2. **Integrity suite**: `python -m pytest tests/schemas/test_taxonomy_integrity.py -q` — green (crosswalk bijection verified, 0 duplicate edges).
3. **2026 contract test**: `python -m pytest tests/scripts/test_owasp_2026_contract.py -q` — green (per-record 2026 identity, grammar, breadcrumb rules).
4. **Backward-compat / no-churn proof**: `python -m pytest tests/scripts/test_backward_compatibility.py -q` — green with zero baseline bytes changed (SC-006; #345's pre-existing xfail expected).
5. **Sweep cleanliness**: `git grep -nE "LLM0[1-9]:2025|LLM10:2025|LLM Top 10 2025"` — remaining hits are only the FR-008 exclusion list (immutable governance records) and the declared `examples/**` carve-out (F-362b #364); dispositions in `specs/362-remap-owasp-llm-top10-2026/bare-code-ledger.md`.
6. **Coverage honesty**: open `docs/standards/OWASP_COVERAGE.md` — 10 LLM verdicts, each citing 2026-definition detection evidence; headline restatements (README ×5, `.claude/rules/scope.md`, developer guide, system-design README) all consistent at 50/50.
7. **Consumer migration note**: `CHANGELOG.md` Unreleased/4.48.0 section — movement-map table (all 10 rows), alias policy, carve-out disclosure.
8. **Live citation health**: GitHub Actions → "tachi citation link-rot" run 31626979318 (branch dispatch, `no_cache: true`) — 908 checked, 0 link_rot.

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | 4.9 eng-days central (band 4.0–6.0; team-lead re-issue at tasks sign-off) |
| Actual Duration | 6 days (branch created 2026-08-06, squash-merged 2026-08-12) |
| Variance | +1.1 days over central, on the band ceiling — and 2 calendar days ahead of the forecast (dev-complete 2026-08-13 / deliver 2026-08-14). 26/26 tasks at the hard absorption ceiling; no T027 was needed. |

---

## Surprise Log

The 2026 per-entry URLs did not exist at authoring time — the D9 URL-scheme gate forced an interim release-page anchor policy, and the deliver-stage no-cache link-rot dispatch (908 checked, 0 confirmed rot) validated it live exactly as designed. The T022 repo-wide sweep gate passed only after a 13-site absorption fix, and the byte-identity suite's red proved environmental (#365 font-subset divergence), not feature-caused.

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| Technical pattern | When identifiers change meaning (not just format), a repo-wide sweep is necessary but insufficient: append-only disposition ledgers with pre-pinned censuses (measured at a named SHA), lane partitioning for parallel writers, single-pass bijective re-keys, and a time-boxed filed carve-out are what make the migration auditable. | Entry 23 in INSTITUTIONAL_KNOWLEDGE.md |

---

## Feedback Loop

**New Ideas**: None net-new at retrospective — the follow-up roster was already filed during the build (T026):

- #364 — F-362b `examples/**` re-key — **blocking before the next minor after v4.48.0** (carve-out closure, breadcrumb sunset, CA-baseline regen, sidecar re-emit, typ:48 fix)
- #365 — environmental-red byte-identity defect (m1 measured font-subset divergence; m2 untested PNG-input candidate)
- #366 — persona↔catalog enumeration parity (+ R-3 extrapolative-reach residual, + PM LOW-2 dispatch-anchor durability)
- #367 — LLM10:2026 scope-boundary documentation
- #368 — `_canonical()` widening — decided DEFER (engineering rationale governs on disagreement)
- #369 — CI manifest-integrity check + copilot-aware generator (final-review W1/S7)
- #370 — FR-012b form-drift guard covering test (final-review W2)

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | specs/362-remap-owasp-llm-top10-2026/spec.md |
| Implementation Plan | specs/362-remap-owasp-llm-top10-2026/plan.md |
| Task Breakdown | specs/362-remap-owasp-llm-top10-2026/tasks.md |
| PRD | docs/product/02_PRD/362-remap-owasp-llm-top10-2026-2026-08-05.md |
| ADR | docs/architecture/02_ADRs/ADR-048-llm-top10-2026-alias-cutover.md |
| Disposition Ledgers | specs/362-remap-owasp-llm-top10-2026/{crosswalk-disposition-ledger.md, bare-code-ledger.md} |
| Gap Analysis | specs/362-remap-owasp-llm-top10-2026/gap-analysis.md |

---

## Test Evidence

### Test Scenarios (Living Documentation)

#### Acceptance Criteria Coverage

| AC ID | Given/When/Then | Scenario(s) | Status |
|-------|-----------------|-------------|--------|
| — | (AC-coverage pre-gate not entered — Step 9a short-circuited on stack-contract lint error before 9a.5; spec ACs were verified by the build-wave suites and PM/architect gates instead) | — | — |

<details>
<summary>Full Gherkin</summary>

_(No Gherkin scenarios generated — the E2E tester stage was not entered; see Execution Evidence.)_

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

**Failure Details**: `stack-contract-lint.sh` exit 5 — no `aod-test-contract` block found in `stacks/knowledge-system/STACK.md` (expected sentinel-bracketed YAML in Section 7). Non-blocking per ADR-006; the knowledge-system pack declares no E2E runner.

#### Per-Scenario Results

| Scenario | Status | Duration |
|----------|--------|----------|
| — | — | — |

#### Command

```bash
/aod.deliver FEATURE: 362 - Remap OWASP LLM Top 10 Coverage to the 2026 Edition
```

#### Artifacts

| Artifact | Path | Summary |
|----------|------|---------|
| Build summary | specs/362-remap-owasp-llm-top10-2026/test-results/summary.json | 4/14 waves tested, 648 pass / 0 fail / 8 skip, 0 regressions |
| Wave 8 results | specs/362-remap-owasp-llm-top10-2026/test-results/wave-08/results.json | 147 pass / 0 fail / 2 skip — pass |
| Wave 9 results | specs/362-remap-owasp-llm-top10-2026/test-results/wave-09/results.json | 147 pass / 0 fail / 2 skip — pass |
| Wave 10 results | specs/362-remap-owasp-llm-top10-2026/test-results/wave-10/results.json | 177 pass / 0 fail / 2 skip — pass |
| Wave 13 results | specs/362-remap-owasp-llm-top10-2026/test-results/wave-13/results.json | 177 pass / 0 fail / 2 skip — pass |
| Pre-state baseline | specs/362-remap-owasp-llm-top10-2026/test-results-prestate.md | Literal pytest totals at branch start (KB 15 attribution rule) |

### Build-Wave Test Results

| Wave | Tests | Passed | Failed | Status |
|------|-------|--------|--------|--------|
| wave-08 | 149 | 147 | 0 | pass |
| wave-09 | 149 | 147 | 0 | pass |
| wave-10 | 179 | 177 | 0 | pass |
| wave-13 | 179 | 177 | 0 | pass |

**Build Summary**: pass — 648/648 executed tests passed (8 skips, 0 regressions; 10 doc-only waves carried no test obligation)

**Archived Artifact Metrics**:
- Tests Run: 656 (648 passed + 8 skipped)
- Passed: 648
- Failed: 0
- Coverage: N/A

**Notes**: Unit/integration validation via pytest build waves (gated 15-module subset per `tachi-pytest.yml` + feature suites). The knowledge-system stack pack declares no E2E contract, so the tester-agent E2E stage did not run; CI on PR #363 was fully green (7/7 checks, both OS pytest suites) before merge.

### Manual Validation

**Manual-only acceptance criteria** (carried from `spec.md`):

- AC US3-AC-2: [MANUAL-ONLY] `docs/standards/OWASP_COVERAGE.md` is hand-authored canon with no generator — the human review gate is the correctness mechanism. **Executed at deliver**: PM SC-005 re-verification APPROVED (10/10 verdicts evidence-checked against live catalogs, 0 Partial; `.aod/results/product-manager-sc005.md`).

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 4 (PRD INDEX row → Delivered; PRD frontmatter; User Stories aggregate US-362-1/2/3; OKRs header) | APPROVED |
| Architecture | architect | 4 (system-design §Feature 362; Tech-Stack 2026 contract-test entry; new "Single-Pass Taxonomy Edition Permutation" pattern; README date) + ADR-048/index verified | COMPLETE |
| DevOps | devops | 2 (CI_CD_GUIDE gated module count 15→16, verified against merge diff; environment-variables "no new vars") + 5 verified current | PASS |

Full agent reports: `.aod/results/{product-manager,architect,devops}-doc-close.md`

---

## Cleanup

- [x] Feature branch deleted (local + remote; `origin/362-remap-owasp-llm-top10-2026` pruned)
- [x] All tasks complete (26/26)
- [x] No TBD/TODO introduced in docs
- [x] Committed and pushed (closure commit on `main`)
- [x] GitHub Issue closed (`stage:done`)

**Feature 362 is now officially CLOSED.**
