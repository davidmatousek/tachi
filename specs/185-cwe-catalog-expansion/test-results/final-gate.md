# T020 Final Gate [G4] — F-185 CWE Catalog Expansion

**Executor**: tester | **Date**: 2026-06-11 | **Branch**: `185-cwe-catalog-expansion`
**Suite under verification**: `specs/185-cwe-catalog-expansion/test-results/wave-02/pytest-full.log` (full suite, NOT re-run — independent accounting + targeted re-confirmations only)

## VERDICT: **GATE PASS**

Conditions (a) + (b) + (c) all TRUE; quickstart §0–§6 all clean or verified-via-committed-gate. Details below.

---

## Part 1 — Failure accounting

**Literal wave-02 summary line**:

```
19 failed, 899 passed, 4 skipped in 705.01s (0:11:45)
```

### Condition (a) — all 19 failing names documented pre-existing: **TRUE (19/19, 0 unexpected)**

Programmatic set-membership check (exact node-ID string match) of every `FAILED` line in the log against the `pre_existing` array in `wave-00/results.json`:

| # | Failing test (wave-02) | In wave-00 `pre_existing` |
|---|---|---|
| 1 | `tests/scripts/test_coverage_attestation_audit.py::TestCitationCompleteness::test_every_covered_owasp_has_agent_citation` | YES |
| 2 | `tests/scripts/test_coverage_attestation_audit.py::TestCitationCompleteness::test_every_covered_owasp_has_pattern_category_citation` | YES |
| 3 | `tests/scripts/test_coverage_attestation_in_scope.py::TestStream4CoveragePercentage::test_aggregator_matches_expected_fixture[findings_in_scope_only]` | YES |
| 4 | `tests/scripts/test_coverage_attestation_in_scope.py::TestStream4CoveragePercentage::test_aggregator_matches_expected_fixture[findings_mixed]` | YES |
| 5 | `tests/scripts/test_coverage_attestation_in_scope.py::TestStream4CoveragePercentage::test_aggregator_matches_expected_fixture[findings_oos_only]` | YES |
| 6 | `tests/scripts/test_init_sh_substitution.py::test_personalized_tree_bytes_match_baseline` | YES |
| 7 | `tests/scripts/test_llm10_unbounded_consumption_enrichment.py::TestLineCountCaps::test_dos_agent_line_count_within_cap` | YES |
| 8 | `tests/scripts/test_llm10_unbounded_consumption_enrichment.py::TestLineCountCaps::test_model_theft_agent_line_count_within_cap` | YES |
| 9 | `tests/scripts/test_ml_top_10_coverage_bundle_enrichment.py::TestLineCountCaps::test_model_theft_md_line_cap` | YES |
| 10 | `tests/scripts/test_ml_top_10_coverage_bundle_enrichment.py::TestLineCountCaps::test_tampering_md_line_cap` | YES |
| 11 | `tests/scripts/test_mobile_top_10_coverage_bundle_enrichment.py::TestLineCountCaps::test_info_disclosure_md_line_cap` | YES |
| 12 | `tests/scripts/test_mobile_top_10_coverage_bundle_enrichment.py::TestLineCountCaps::test_privilege_escalation_md_line_cap` | YES |
| 13 | `tests/scripts/test_mobile_top_10_coverage_bundle_enrichment.py::TestLineCountCaps::test_repudiation_md_line_cap` | YES |
| 14 | `tests/scripts/test_mobile_top_10_coverage_bundle_enrichment.py::TestLineCountCaps::test_spoofing_md_line_cap` | YES |
| 15 | `tests/scripts/test_mobile_top_10_coverage_bundle_enrichment.py::TestLineCountCaps::test_tampering_md_line_cap` | YES |
| 16 | `tests/scripts/test_mobile_top_10_coverage_bundle_enrichment.py::TestNewPatternCategoriesPresent::test_privilege_escalation_companion_has_M8_priv_gain` | YES |
| 17 | `tests/scripts/test_tool_abuse_enrichment.py::test_categories_1_8_byte_identity_against_main` | YES |
| 18 | `tests/scripts/test_tool_abuse_enrichment.py::test_tool_abuse_line_count_within_cap` | YES |
| 19 | `tests/scripts/test_tool_abuse_enrichment.py::test_validate_source_attribution_on_regen` | YES |

19 unique names (rows 10/15 are same-named tests in *different* files: `test_ml_top_10_*` vs `test_mobile_top_10_*`). All are out-of-scope enrichment line-caps / attestation / extractor failures per the wave-00 notes. **0 regressions, 0 new failures attributable to F-185.**

### Condition (b) — must-green trio: **TRUE (all three green)**

| Surface | Log evidence | Live re-confirmation (this gate) |
|---|---|---|
| `tests/schemas/` (integrity) | 0 `FAILED tests/schemas/` lines in log | `pytest tests/schemas/test_taxonomy_integrity.py -q` → **5 passed in 1.17s** |
| `tests/scripts/test_backward_compatibility.py` (byte-identity) | 0 of its names among FAILED; 1 documented SKIP (line 392, mermaid-agentic-app SC-003/T033 exclusion) | `pytest tests/scripts/test_backward_compatibility.py -q` → **13 passed, 1 skipped in 42.02s** |
| `tests/scripts/test_coverage_attestation.py::test_coverage_percentage_arithmetic` (wave-01 refreshed pin) | Not among FAILED (failing attestation names are in `_audit.py` / `_in_scope.py` — different files) | Targeted run → **1 passed in 1.19s** |

### Condition (c) — byte-identity names absent from failures: **TRUE (0/19)**

None of the 19 failing names is any of the 6 `test_unmodified_examples_byte_identical_pdfs[*]` params (ascii-web-api, free-text-microservice, maestro-reference, mermaid-agentic-app, microservices, web-app). All 6 flipped red → green, confirmed three ways:

1. Absent from the wave-02 FAILED list (programmatic check: 0 overlap).
2. Pass-count arithmetic: wave-00 `25 fail / 893 pass / 4 skip` → wave-02 `19 fail / 899 pass / 4 skip` = exactly −6 fail / +6 pass (total 922 both runs).
3. Live single-file run at this gate: 13 passed, 1 skipped (matches the T015 record in ADR-037 Revision History).

### Baseline reconciliation (33 wave-00 names fully accounted)

`wave-00/results.json` lists 33 `pre_existing` names against `totals.fail = 25` (notes: lastfailed-cache may carry phantoms). Reconciliation: **19 still-failing + 6 byte-identity (now green) + 8 phantoms = 33**. The 8 phantoms verified by `--collect-only` against their 5 files (93 tests collected, collection healthy): each has a renamed/re-parametrized successor — tier tests renamed to `test_merge_attaches_attribution_*`, `test_schema_version_is_1_7` → `_is_1_9`, image-flag params `= false` → `= true`, `[.jpg]` → `[.jpg-<magic-bytes>]`, callout test replaced by `test_select_critical_high_callouts_helper`/`test_callouts_deterministic`. Harmless, exactly as wave-00 notes predicted. Wave-01 context: its 2 flagged regressions were dispositioned (arithmetic pin refreshed green — re-confirmed live above; attack-chain conditional-gate = suite-order flake) and neither appears in wave-02 failures.

---

## Part 2 — Quickstart walkthrough (§0–§6)

Deviation rule applied: steps that would mutate committed files SKIPPED (verified via committed gates); read-only verifications executed for real; full suite never re-run.

| § | Step | Mode | Literal outcome |
|---|---|---|---|
| 0 | Recovery objects + baseline | **EXECUTED** | `git cat-file -t e58f247` → `commit`; `991e1ee` → `commit`. Source-blob crosswalk parse → **551** (matches). Current crosswalk parse → **645** — §0's `578` was the *pre-build* baseline; post-W1-2 expected = 578 + 67 = **645** (T017 review-sweep Part A independently proved live(645) − preF185(578) = exactly the 67 artifact edges, nothing else). Integrity suite → **5 passed in 1.17s**. "Known red pre-state" note now superseded: backward-compat green (see §5). |
| 1 | W0-b extract restore-set | **SKIPPED regen** (script writes committed `restored-edges.yaml`) — verified committed artifact by YAML parse | **67 edges** = 65 `owasp→cwe` + 2 `mitre-attack→cwe`; **40** distinct `_blocked_on`; confidence **34 high / 32 medium / 1 low**; edge_type **67/67 primary**. Exact match to every §1 expectation. Artifact committed. |
| 2 | W0-a harvest + disposition | **EXECUTED** (out-path deviation: fresh corpus to `/tmp`, harvest output to `/tmp` — no committed-surface writes) | Zip SHA-256 `3976f599e5e5200219a3108bb896d06e2a88fbb293369e1883cb423a5e9d7d50` **matches corpus-pin.md pin**; sizes match (2,021,351 zip / 18,192,305 xml). `harvest_cwe_names.py` → exit 0, `rows=40 found=40 missing=0 deprecated=0 duplicates=0 discrepancies=0`; table rows **byte-identical** to committed `test-results/harvest-40.md`. Architect 40/40 **add** disposition verified via committed `test-results/disposition.md` + ADR-037 Revision History row (zip/xml not committed, per design). |
| 3 | W1-1 insert records + gate | Catalog edit already committed; **gates EXECUTED** | `grep -c "^- id: " schemas/taxonomy/cwe.yaml` → **93**; independent YAML parse → **93** records (= 53 + 40 add-all). Integrity suite → **5 passed**. |
| 4 | W1-2 restore edges + gate | Edge insertion already committed; **gates EXECUTED** | Integrity suite (incl. dedupe check) → **5 passed**. `_blocked_on` occurrences in live `crosswalk.yaml` → **0** (stripped as specified). Crosswalk total 645 = 578 + 67 restored. |
| 5 | W1-3 regenerate 6 gated baselines | **Regen SKIPPED** (mutates committed baselines; proof carried by committed T014 baselines + `test-results/baseline-diff.md` CA-page-only verification). **Gate command EXECUTED for real** | `pytest tests/scripts/test_backward_compatibility.py -q` → **13 passed, 1 skipped in 42.02s**. All 6 byte-identity params green (red→green flip live-confirmed); the 1 skip is the documented T033 SC-003 mermaid-agentic-app exclusion. (§5's "6 passed" comment counted only the 6 byte-identity params; file-level result is 13+1s.) |
| 6 | W2 verification gates | name-diff + sweep **EXECUTED**; full suite **cited** (re-run forbidden) | **name_diff.py**: `checked 40/40 inserted IDs`, `mismatches = 0`, `CWE-1039 sentinel = CONFIRMED`, exit 0 → **R7 GATE PASS** (output to `/tmp/name-diff-verify.md`; committed evidence `test-results/name-diff.md` untouched). **Full suite**: wave-02 log = `19 failed, 899 passed, 4 skipped` — "green" holds modulo the 19 documented pre-existing (Part 1: 0 regressions / 0 new failures; soft-gate protocol per wave-00/wave-01). **Stale-count sweep** `grep -rn "53 record\|53-record" docs/ schemas/ \| grep -v specs/` → NOT literally empty; every hit maps 1:1 onto T017's committed disposition (`test-results/review-sweep.md`, 57/57 classified): the 1 genuinely stale hit FIXED (committed — `schemas/taxonomy/README.md:254` now reads 608/37/0 = 645 + 93-record), 30 historical/lineage correct-as-is (PRDs, ADR revision history, crosswalk provenance comments — "53-record" remains factually true of authoring time; 53 ⊂ 93), 8 T018-handled via ADR-037 D-7 annotation blockquote (line 125) + Revision History row (line 432) + ADR-027:355 forward-pointer — all three confirmed present; ratified ADR text byte-unchanged BY DESIGN per architect C3. Tech_Stack README F-185 segment is deliver-flow-owned (T017 flag). **Sweep verdict: CLEAN per dispositioned baseline.** |

§7 (Done criteria) is outside this gate's §0–§6 scope; CHANGELOG/ADR/NEXT-SESSION surfaces verified present incidentally via T018 evidence above.

## Hygiene

No commits, no pushes, no edits outside the two evidence paths. Working tree before/after: ` M specs/185-cwe-catalog-expansion/tasks.md` (pre-existing orchestrator checkbox bookkeeping) + untracked `uv.lock` (pre-existing) — unchanged by this gate. All scratch outputs confined to `/tmp`.

## Evidence inventory

- Wave-02 log: `specs/185-cwe-catalog-expansion/test-results/wave-02/pytest-full.log`
- Baselines: `test-results/wave-00/results.json` (33-name `pre_existing`), `test-results/wave-01/results.json` (pin refresh + flake disposition)
- Committed gates cited: `test-results/review-sweep.md` (T017), `test-results/baseline-diff.md` (T015), `test-results/corpus-pin.md` (T002), `test-results/harvest-40.md` (T004), `test-results/disposition.md` (T006), `test-results/name-diff.md` (T016), ADR-037 D-7 annotation + Revision History
- Full T020 working detail: `.aod/results/185-w2-t020.md`
