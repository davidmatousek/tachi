# NEXT-SESSION Handoff — F-241 Web/API Coverage Attestation + Populator Wiring

**Generated**: 2026-05-01 (post Wave 4.3)
**Branch**: `241-web-api-coverage-attestation`
**Last Commit**: `02acd08` feat(241): Wave 4.3 — Stream 4 aggregator Out-of-Scope filter (T044-T048)
**Draft PR**: #242 (`feat(241):` Conventional Commit title verified; pushed at 2026-05-01)
**User scope**: "Run /aod.build to continue with Wave 4.3 (T044, T045, T046, T047, T048)" — completed; stopping per established single-wave-per-session pattern (matches Wave 3.1 + Wave 3.2 + Wave 4.1 + Wave 4.2 prior sessions).

---

## Progress Snapshot

**Tasks complete**: 47/84 (56.0%)
**Waves complete**: 1.1 + 1.2 + 1.3 + 2.1 + 2.2 + 2.3 + 3.1 + 3.2 + 4.1 + 4.2 + **4.3**
**Phase 5 progress**: Streams 3 + 4 fully closed (taxonomy YAMLs at full inventory + aggregator filter implemented). Wave 5.1 (test infrastructure authoring) is next.

### Done This Session — Wave 4.3 (Phase 5 Stream 4 aggregator extension)

**T044 — Architect M-2 carry-forward verification**:
- Verified `scripts/extract-report-data.py` lines 1070–1175 layout
- Decision: filter applied at `_load_framework_yaml_records()` (line 1073) — lowest-level insertion so the in-scope semantic flows uniformly through every downstream caller
- NOT applied at `_build_per_framework_aggregate()` (line 1144) where count is pre-frozen per Architect M-2 verbatim

**T045 — Out-of-Scope-aware filter implementation**:
- `_load_framework_yaml_records(framework_name, in_scope_only=False)` gains optional kwarg; when True filters records carrying `out_of_scope: true` via list comprehension; pre-F-241 records absent the `out_of_scope` key are treated as in-scope (default `False` per data-model.md §2 backwards-compat)
- New sibling helper `load_framework_yaml_in_scope_record_counts()` returns `{framework: in_scope_count}` for the 5 frameworks
- `_build_per_framework_aggregate()` signature extends with `in_scope_yaml_record_count` parameter; emitted dict now carries BOTH `yaml_record_count` (raw, for traceability) AND `in_scope_yaml_record_count` (filtered, denominator)
- Coverage percentage formula: `(covered_count / in_scope_yaml_record_count) * 100`; `"N/A"` when `in_scope_yaml_record_count == 0`
- Typst data emission at line ~1813 emits `in-scope-record-count: <int>` field alongside existing `yaml-record-count`

**T046 — stdlib-only module-load invariant preservation**:
- `import yaml` confirmed inside function body of `_load_framework_yaml_records` (line 1085); no module-level `yaml` import introduced
- Loader docstring extended with explicit reference to T046 / FR-014 + Architect M-2 carry-forward to document the in-scope filter's design intent

**T047 — Caller orchestration update**:
- `build_per_framework_aggregates()` calls both `load_framework_yaml_record_counts()` (raw) AND `load_framework_yaml_in_scope_record_counts()` (in-scope)
- Classifies in-scope-only records via `_load_framework_yaml_records(framework_name, in_scope_only=True)` so the `items` list excludes OOS records → partition invariant holds against in-scope denominator
- Per F-241 T046 edge case: findings citing Out-of-Scope items still render on per-finding attribution table (built separately in `build_per_finding_rows` from `finding.source_attribution`) but those OOS records do NOT appear in the per-framework matrix items list and do NOT increment `covered_count`

**T048 — Stream 3+4 fixture suites + test delta**:
- 16 net-new fixture files under `tests/scripts/fixtures/stream_3_taxonomy/` + `stream_4_coverage_percentage/` (mixed in-scope/OOS records, zero-denominator, all-OOS framework, pre-F-241 absent-key backward-compat case, sibling `expected.yaml` per finding fixture)
- New `tests/scripts/test_coverage_attestation_in_scope.py` (19 tests, all pass) covering in-scope filter behavior, dual-emission to Typst, partition invariant against `in_scope_yaml_record_count`, and arithmetic
- Updated `test_partition_invariant` (test_coverage_attestation.py:326) — assertion shifted from `yaml_record_count` → `in_scope_yaml_record_count`
- Updated `test_coverage_percentage_arithmetic` — expected `mitre-attack: 2.63%` (1/38 F-A1 baseline) → `0.31%` (1/323 post-Stream-4) on `findings_mixed`; on `multi_mixed` the actual outcome is `0.00%` because T1070.001 is OOS-filtered AND T1078 is `related`-only → partial (per tester audit; documented in fixture rationale)
- Updated `test_coverage_attestation_pagination.py:189` to use raw `yaml_record_count` for layout calculations (correct for layout; documented inline)

### Aggregator Math Verified End-to-End (Wave 4.3 Acceptance)

| Framework | Raw (yaml_record_count) | In-Scope (in_scope_yaml_record_count) | OOS Excluded |
|-----------|-------------------------|---------------------------------------|--------------|
| owasp | 60 | 60 | 0 |
| mitre-attack | 701 | **323** | **378** |
| mitre-atlas | 30 | 30 | 0 |
| nist-ai-rmf | 72 | 72 | 0 (outside F-241 Stream 3 scope) |
| cwe | 53 | 53 | 0 (outside F-241 Stream 3 scope) |

- mitre-attack: 1/323 = **0.31%** (replaces F-A1 baseline 1/38 = 2.63%) — matches NEXT-SESSION wave-42 line 60 expected post-fix value
- Partition invariant `covered + partial + gap == in_scope_yaml_record_count` holds for all 5 frameworks (manually verified across empty, single-finding, and zero-denominator cases)
- `"N/A"` correctly returned when `in_scope_yaml_record_count == 0` (entirely-OOS framework edge case)

### Test Gate (Wave 4.3)

| Suite | Pass/Fail | Status | Notes |
|-------|-----------|--------|-------|
| `tests/scripts/test_coverage_attestation.py` | 46/46 | PASS | Includes updated partition invariant + arithmetic delta |
| `tests/scripts/test_coverage_attestation_in_scope.py` | 19/19 | PASS | NEW — Wave 4.3 T048 |
| `tests/scripts/test_coverage_attestation_pagination.py` | (all green) | PASS | Pagination layout uses raw count (documented) |
| `tests/scripts/test_taxonomy_integrity.py` | 5/5 | PASS | Wave 4.2 baseline carries forward unchanged (701-record `mitre-attack.yaml` integrity preserved) |
| `tests/scripts/test_f_a3_populator_wiring.py` | 68/68 | PASS | Wave 2.3 baseline carries forward unchanged |
| **Full suite** | **639/656** | (16 fail / 1 skip) | Delta vs Wave 4.2 baseline (619/17/1): **+20 net passing, -1 failure** (test_coverage_percentage_arithmetic FIXED); 19 new T048 tests added |

**16 carry-forward failures** (all pre-Wave-4.3, unchanged from prior baseline):
- 1× zero-edit invariant on `agent-autonomy.md` + `prompt-injection.md` (T051 Wave 5.2 fix)
- 5× Mobile Top 10 line-cap (pre-existing F-7)
- 2× ML Top 10 line-cap (pre-existing F-6)
- 2× LLM10 line-cap (pre-existing F-5)
- 3× tool-abuse-enrichment (pre-existing F-3)
- 2× citation completeness (pre-existing — `test_every_covered_owasp_has_agent_citation` + `test_every_covered_owasp_has_pattern_category_citation`)
- 1× mobile pattern category presence (pre-existing F-7)

**0 new regressions** in Wave 4.3. Test results persisted at `specs/241-web-api-coverage-attestation/test-results/wave-43/results.json` (gitignored ephemeral artifact; build framework data-model.md §5f).

### Coverage Progress

**5/5 framework taxonomies** at canonical inventory (post Wave 4.3):
- ✅ owasp.yaml (60 records — F-241 T037 Wave 3.2)
- ✅ mitre-atlas.yaml (30 records — F-241 T039 Wave 3.2)
- ✅ mitre-attack.yaml (701 records / 323 in-scope — F-241 T041-T043 Wave 4.2 + T044 Wave 4.3 filter wired)
- ⏳ nist-ai-rmf.yaml (72 records, +2 fields — outside F-241 Stream 3 scope; reserved for future taxonomy maintenance)
- ⏳ cwe.yaml (53 records, +2 fields — outside F-241 Stream 3 scope; reserved for future taxonomy maintenance)

**Stream 4 aggregator surface CLOSED** at Wave 4.3 — Architect M-2 carry-forward resolved.

---

## Next Actions (Resume Here)

### Wave 5.1 (Days 22–23, Sat 5/30 + Sun 5/31) — Test infrastructure authoring (4 parallel tasks)

**4 parallel `tester` agent tasks** (see agent-assignments.md §"Wave 5.1"):

- **T049** [P] [US1] — `tester` — Author `tests/scripts/test_coverage_percentage_computation.py` (0 ppt delta on 8 baselines × 5 frameworks = 40 cross-check pairs). **WATCHLIST**: 2 net-new baselines (`predictive-ml-app`, `mobile-banking-app`) don't yet exist as canonical `.baseline` files (authored at T054+T055 Wave 5.2). Either defer cross-check on those 2 OR consume `examples/{arch}/sample-report/security-report.pdf` already-rendered PDFs. Read T049 task description carefully before authoring.
- **T050** [P] [US1] — `tester` — Author `tests/scripts/test_pyyaml_deferred_import.py` (AST walk of `import yaml` nodes per Architect MEDIUM-B; verifies F-241 T046 invariant preserved across all touched scripts).
- **T051** [P] [US1] — `tester` — Update `tests/scripts/test_backward_compatibility.py`: remove 11 F-A3 hosts from `DETECTION_AGENT_PATHS`; add to `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` frozenset (extends F-3 / F-5 / F-6 / F-7 enrichment-branch precedent).
- **T052** [P] [US1] — `tester` — Update `tests/scripts/test_backward_compatibility.py`: add `predictive-ml-app` + `mobile-banking-app` to mutation-target exclusion list.

**Critical path implication**: T049 + T050 are file-disjoint and run truly parallel; T051 + T052 both touch `test_backward_compatibility.py` → serialize OR sequence within a single tester agent invocation. Recommended: 3 parallel agent invocations (T049 alone, T050 alone, T051+T052 sequential as one prompt).

**Note re T051 vs T051-Wave-5.2**: The Wave 5.1 T051 is the `test_backward_compatibility.py` frozenset update (Architect MEDIUM-B). The carry-forward zero-edit invariant fix on `agent-autonomy.md` + `prompt-injection.md` (which currently fails as a baseline test) is tracked separately — confirm against tasks.md when resuming whether it's a separate Wave 5.2 task ID or absorbed into Stream 2 closure verification.

### Wave 5.2 (Days 24–25, Mon 6/1 + Tue 6/2) — 8-baseline regen + SC verification

T053 (6 pre-existing baselines regen under `SOURCE_DATE_EPOCH=1700000000`) + T054 (predictive-ml-app new baseline canonical path L-1) + T055 (mobile-banking-app new baseline canonical path L-1) + T056 (SC-007 verify) + T057 (SC-009 verify 0 ppt delta on 40 cross-check pairs) + T058 (SC-015 verify non-CA byte-identity).

### Wave 5.3 (Day 26) — ADR-037 narrative + ADR-027 cross-link + §6 demotion

T059 (ADR-037 D-1..D-10 narrative authoring; **consumes T040 + T041 §3.4 curator decision on TA0112/TA0043 + Wave 4.3 D-8 filter-insertion-point narrative**) + T060 (ADR-027 forward-pointer addendum / Architect M-1 resolution) + T061 (§6 demotion in `_internal/strategy/BLP-01-threat-coverage.md`) + T062 (contingent FR-008 deferral docs).

### Wave 6.1 (Day 27) — PR title verification + ADR-037 Accepted dual-commit

T063 (`feat(241):` PR title pre-merge check) + T064 (ADR-037 Proposed → Accepted dual-commit pattern) + T080 + T081 + T082 (Architect M-2 sanity-check at line 1073) + T083 + T084.

### Wave 6.2 (Day 28) — Triple Triad sign-off + 18 SC verification

T065 (PM + Architect + Team-Lead sign-off on tasks.md) + T066 (verify all 18 SCs) + T070 (owasp.yaml audit completeness post-Stream 2 closures).

### Wave 6.3 (Day 29) — PR squash-merge + post-merge SHA + release-please verification

T067 (PR ready + squash-merge --delete-branch) + T068 (ADR-037 Accepted post-merge SHA fill-in) + T069 (release-please PR opens within ~30s; empty marker commit if not) + T076 (CHANGELOG) + T077 (BACKLOG regen) + T078 (delivery retrospective) + T079 (Issue #241 → stage:done).

---

## Prerequisites for Next Session

- ✅ Branch `241-web-api-coverage-attestation` is current
- ✅ Draft PR #242 open with `feat(241):` Conventional Commit title (Wave 4.3 commit pushed)
- ✅ Wave 4.3 work committed (commit `02acd08`) and pushed to remote
- ✅ Wave 4.2 work committed (commit `886e022`)
- ✅ Wave 4.1 work committed (commit `cbe955d`)
- ✅ Wave 3.2 work committed (commit `1561085`)
- ✅ Wave 3.1 work committed (commit `89848ab`)
- ✅ Wave 2 work committed (commit `3e10019`)
- ✅ Wave 1 work committed (commit `7ba5447`)
- ✅ T048 audit-trail file persisted at `.aod/results/tester-T048-stream-3-4-fixtures.md` (consumed by T059 / Wave 5.3 for ADR-037 D-8 narrative on filter-insertion-point + dual-emission rationale)
- ✅ T041 audit-trail file persisted at `.aod/results/T041-T043-attack-expansion.md` (consumed by T059 / Wave 5.3 for ADR-037 D-5 tactical-grouping narrative — TA0112 + TA0043 derived rationale strings)
- ✅ T040 audit-trail file persisted at `.aod/results/T040-attck-tactical-grouping-audit.md` (consumed by T059 / Wave 5.3)
- ✅ ADR-037 stub at status: Proposed (full narrative deferred to T059 / Wave 5.3; D-5 tactical-grouping + D-8 filter-insertion-point narratives now consume T040 + T041 §3.4 + Wave 4.3 implementation history)
- ✅ All 11 newly-wired Wave 1+2 STRIDE+AI hosts under 200-line cap
- ✅ `test_taxonomy_integrity.py` 5/5 passing on 701-record `mitre-attack.yaml`
- ✅ `test_f_a3_populator_wiring.py` 68/68 passing (Wave 2.3 baseline)
- ✅ `test_coverage_attestation.py` 46/46 passing (post-Wave-4.3 with new partition invariant + arithmetic delta)
- ✅ `test_coverage_attestation_in_scope.py` 19/19 passing (Wave 4.3 T048 net-new)
- ✅ Stream 3 closure milestone: 3 of 3 taxonomy YAMLs at full inventory (owasp 60 + mitre-atlas 30 + mitre-attack 701 = 791 records carrying +2 fields)
- ✅ Stream 4 aggregator-extension closure milestone: filter at line 1073 / dual-emission contract / partition invariant against in-scope denominator / Architect M-2 RESOLVED

**Suggested resume command**:
```
claude "Resume F-241 Web/API Coverage Attestation. Branch: 241-web-api-coverage-attestation. Waves 1.1-1.3 + 2.1-2.3 + 3.1 + 3.2 + 4.1 + 4.2 + 4.3 complete (47/84 tasks); Stream 3 fully closed; Stream 4 aggregator extension closed at Wave 4.3 (Architect M-2 implementation lands at line 1073). Run /aod.build to continue with Wave 5.1 (T049, T050, T051, T052 — 4 parallel tester tasks)."
```

---

## Architect Carry-Forwards (still pending)

- **M-1**: ADR-027 forward-pointer addendum cross-linking ADR-037 D-7 (T060 + T083, **Wave 5.3**) — unchanged
- **M-2**: ✅ **RESOLVED at Wave 4.3** (filter at `_load_framework_yaml_records()` line 1073 per architect verbatim; T084 sanity-check still pending Wave 6.1 polish)
- **L-1**: Canonical baseline paths for predictive-ml-app + mobile-banking-app (T054 + T055 + T081, **Wave 5.2**)
- **NEW (Wave 4.2 surfacing)**: data-model.md §5 should be extended with +2 entries enumerating TA0112 Defense Impairment + TA0043 Reconnaissance; non-breaking spec additive recommended before delivery (or absorbed into ADR-037 D-5 narrative at T059). Documented at `.aod/results/T041-T043-attack-expansion.md` §3.4.
- **NEW (Wave 4.3 surfacing)**: ADR-037 D-8 narrative should explicitly cite the line 1073 insertion point (vs candidate line 1101) and document the dual-emission rationale (`yaml_record_count` raw + `in_scope_yaml_record_count` filtered preserves external-auditor traceability). Documented in commit message of `02acd08` + `.aod/results/tester-T048-stream-3-4-fixtures.md`.

---

## Out-of-Session Risks & Watchlist

1. **T049 baseline coverage scope** — `test_coverage_percentage_computation.py` requires 8 baselines × 5 frameworks = 40 cross-check pairs. The 2 net-new baselines (`predictive-ml-app`, `mobile-banking-app`) don't yet exist as canonical `.baseline` files (T054+T055 Wave 5.2). Decision needed at T049 authoring: (a) defer those 2 baselines' cross-check until Wave 5.2 baselines land (test starts at 6×5=30 pairs), or (b) consume the already-rendered `examples/{arch}/sample-report/security-report.pdf` PDFs as substitute baselines (test starts at 8×5=40 pairs but with non-canonical sources for 2). Read T049 task description in tasks.md before authoring; align with team-lead estimate of 4.0h.
2. **T051 vs T051-Wave-5.2 disambiguation** — There are TWO things called "T051" in handoff context: (i) Wave 5.1 T051 is the `test_backward_compatibility.py` frozenset update (Architect MEDIUM-B), and (ii) the carry-forward zero-edit invariant fix on `agent-autonomy.md` + `prompt-injection.md` is loosely referenced as "T051 Wave 5.2" in NEXT-SESSION line 121 / `tester-T048` results — confirm whether the host-agent fix has its own task ID OR is absorbed in Stream 2 closure verification when resuming.
3. **8-baseline byte-identity discipline (T053–T058 Wave 5.2)** — non-CA pages on 8 pre-existing baselines must remain byte-identical under `SOURCE_DATE_EPOCH=1700000000` post Stream 4 aggregator change. The Wave 4.3 implementation affects ONLY the Coverage Attestation page (added in F-A1 ADR-027). Pre-emptive verification approach: `diff <(pdftotext old) <(pdftotext new)` per page; fail fast if any non-CA page byte-differs.
4. **F-7 28-file zero-edit invariant** — F-241 has now modified: 11 host agents + 2 Stream 2 companion catalogs + 3 taxonomy YAMLs + `scripts/extract-report-data.py` + 4 test files (within scope). T075 will verify final compliance at Wave 6.1; current count: 11 + 2 + 3 + 1 + 4 = **21 files modified** within 11+up-to-5 + 3-taxonomy-YAML budget + 1 aggregator script + N test files allowed. (Test file edits do not count against detection-tier zero-edit invariant.)
5. **Schema unchanged at v1.8** — confirmed at T008; no `id.pattern` regex extension needed. F-241 reuses S/T/I/E/R + LLM/AG/AGP prefixes. Wave 4.3 added no schema changes.
6. **Tactical-grouping defensibility (ADR-037 D-5 at T059)** — T040 documents 7 rationale strings for the spec-enumerated tactics; T041 §3.4 surfaces 2 derived strings for post-spec STIX-update tactics (TA0112 + TA0043); Wave 4.3 contributes the filter-insertion-point + dual-emission rationale (D-8). T059 (Wave 5.3) authors the formal external-auditor-facing justification narrative consuming all three audit-trails.
7. **Pre-existing test failures unchanged** — 16 pre-existing failures (zero-edit + line-cap + citation-completeness + tool-abuse 3) carry forward unchanged from Wave 4.2 baseline. Scheduled fixes:
   - T051 Wave 5.2 (or equivalent — see Watchlist #2): zero-edit invariant on `agent-autonomy.md` + `prompt-injection.md`
   - Other line-cap failures: pre-existing fixture metadata; not F-241 scope (deferred to follow-on issues per FR-008)
8. **Wave 4.3 dual-emission Typst contract** — both `yaml-record-count` (raw) AND `in-scope-record-count` (filtered) emit on the same per-framework aggregate dict. The Typst report-template can render either or both; current default consumes `yaml-record-count` for top-line display + `in-scope-record-count` for denominator math. Confirm template renders correctly on Wave 5.2 baseline regen — if any template rendering edits are needed, those land in Wave 5.2 alongside T053.

---

**End of NEXT-SESSION handoff** — 47/84 tasks complete (56.0%); Stream 3 fully closed at Wave 4.2; Stream 4 aggregator extension fully closed at Wave 4.3; resuming at Wave 5.1 (T049/T050/T051/T052 — 4 parallel `tester` tasks for test infrastructure authoring + backward-compat updates).
