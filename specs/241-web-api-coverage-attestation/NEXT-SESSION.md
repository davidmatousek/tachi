# NEXT-SESSION Handoff — F-241 Web/API Coverage Attestation + Populator Wiring

**Generated**: 2026-05-01 (post Wave 5.1)
**Branch**: `241-web-api-coverage-attestation`
**Last Commit**: `3b88290` feat(241): Wave 5.1 — test infrastructure authoring (T049-T052)
**Draft PR**: #242 (`feat(241):` Conventional Commit title verified; pushed at 2026-05-01)
**User scope**: "Run /aod.build to continue with Wave 5.1 (T049, T050, T051, T052 — 4 parallel tester tasks)" — completed; stopping per established single-wave-per-session pattern (matches Wave 3.1 + Wave 3.2 + Wave 4.1 + Wave 4.2 + Wave 4.3 prior sessions).

---

## Progress Snapshot

**Tasks complete**: 51/84 (60.7%)
**Waves complete**: 1.1 + 1.2 + 1.3 + 2.1 + 2.2 + 2.3 + 3.1 + 3.2 + 4.1 + 4.2 + 4.3 + **5.1**
**Phase 5 progress**: Streams 1 + 2 + 3 + 4 fully closed (taxonomy YAMLs at full inventory, aggregator filter implemented, F-A3 populator wiring complete, test infrastructure authored). Wave 5.2 (8-baseline regen + SC-007/009/015 verification — CHECKPOINT 5) is next.

### Done This Session — Wave 5.1 (Phase 5 test infrastructure authoring)

**T049 — `tests/scripts/test_coverage_percentage_computation.py` (597 lines)**:
- Independently re-derives coverage % via `|cited_ids| / |taxonomy_ids_not_out_of_scope|` formula and asserts 0 ppt delta vs aggregator output (`build_per_framework_aggregates()` invocation)
- **Mode (a) deferred parametrization decision** — 30 active cross-check pairs (6 pre-existing baselines × 5 frameworks) + 10 `pytest.skip` markers awaiting Wave 5.2 T054/T055 baselines (`predictive-ml-app` + `mobile-banking-app`); test will auto-expand to 40 pairs once those baselines land
- Test classes cover: independent re-derivation, 0 ppt delta, `"N/A"` denominator (all-OOS framework), backwards-compat absent-key path
- Reuses Wave 4.3 T048 fixtures from `tests/scripts/fixtures/web_api_coverage_attestation/stream_4_coverage_percentage/`
- **Result**: 38 pass / 10 skip / 0 fail
- Audit-trail: `.aod/results/tester-T049.md`

**T050 — `tests/scripts/test_pyyaml_deferred_import.py` (311 lines)**:
- AST walks every Python file in `scripts/` (auto-discovery via glob + filter); asserts each `import yaml` / `from yaml import …` node is nested inside `ast.FunctionDef` or `ast.AsyncFunctionDef` ancestor per KB-037 stdlib-only invariant + F-241 T046 anchor
- Confirms T046 anchor at `scripts/extract-report-data.py:1095` (deferred `import yaml` inside `_load_framework_yaml_records` function body) is regression-guarded
- Includes negative-control synthetic AST snippet (`ast.parse("import yaml\n")`) verifying the `_is_inside_function` helper itself isn't broken
- **Result**: 9/9 pass; **KB-037 invariant HOLDS** (zero module-level yaml imports detected across all `scripts/*.py`)
- Audit-trail: `.aod/results/tester-F241-T050.md`

**T051 — `tests/scripts/test_backward_compatibility.py` (frozenset shift)**:
- Removed `prompt-injection.md` + `agent-autonomy.md` from `DETECTION_AGENT_PATHS` (4→2; the 9 prior F-A3 hosts had already been moved across earlier F-241 waves)
- Added their companion paths to `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` frozenset (9→11)
- Updated `len(...) == 4` → `== 2` sanity-check assertion
- Added F-241 comment paragraph documenting the transition rationale
- **Side-effect**: Resolves the carry-forward zero-edit invariant failure flagged in prior NEXT-SESSION Watchlist #2 — the "T051 Wave 5.2" carry-forward fix is **absorbed at Wave 5.1** (Watchlist #2 ambiguity now CLOSED)

**T052 — `tests/scripts/test_backward_compatibility.py` (mutation-target exclusion)**:
- **No edit needed** — F-7 commit `e962a0e` (Mobile Top 10 closure at 2026-04-29) already added `predictive-ml-app` + `mobile-banking-app` to the comment-block exclusion list (lines 21-22) and they are correctly absent from `BASELINE_EXAMPLES`
- T052 marked `[X]` as a verification-only no-op
- Audit-trail: `.aod/results/tester-T051-T052.md`

### Test Gate (Wave 5.1)

| Suite | Pre-Wave-5.1 | Post-Wave-5.1 | Delta | Notes |
|-------|--------------|----------------|-------|-------|
| `test_backward_compatibility.py` | 12/13 (1 fail) | 13/13 + 1 skip | **+1 pass, -1 fail** | T051 frozenset shift fixed zero-edit failure |
| `test_coverage_percentage_computation.py` (NEW) | n/a | 38 pass / 10 skip | **+38 pass** | T049 deliverable; Mode (a) deferred |
| `test_pyyaml_deferred_import.py` (NEW) | n/a | 9/9 pass | **+9 pass** | T050 deliverable; KB-037 invariant guard |
| `test_coverage_attestation.py` | 46/46 | 46/46 | unchanged | Wave 4.3 baseline carries forward |
| `test_coverage_attestation_in_scope.py` | 19/19 | 19/19 | unchanged | Wave 4.3 baseline carries forward |
| `test_taxonomy_integrity.py` | 5/5 | 5/5 | unchanged | Wave 4.2 baseline carries forward |
| `test_f_a3_populator_wiring.py` | 68/68 | 68/68 | unchanged | Wave 2.3 baseline carries forward |
| **Full suite** | 639/656 (16 fail / 1 skip) | **682/708 (15 fail / 11 skip)** | **+43 pass, -1 fail, +10 skip** | 0 new regressions |

**15 carry-forward failures remaining** (all pre-Wave-5.1, unchanged from prior baselines except for the FIXED zero-edit failure):
- 5× Mobile Top 10 line-cap (pre-existing F-7)
- 2× ML Top 10 line-cap (pre-existing F-6)
- 2× LLM10 line-cap (pre-existing F-5)
- 3× tool-abuse-enrichment (pre-existing F-3)
- 2× citation completeness (pre-existing — `test_every_covered_owasp_has_agent_citation` + `test_every_covered_owasp_has_pattern_category_citation`; T070 Wave 6.2 owasp.yaml audit will surface; deferral candidate per FR-008 if not closable)
- 1× mobile pattern category presence (pre-existing F-7 `test_privilege_escalation_companion_has_M8_priv_gain`)

**0 new regressions** in Wave 5.1. Test results persisted at `specs/241-web-api-coverage-attestation/test-results/wave-51/results.json` (gitignored ephemeral artifact; build framework data-model.md §5f).

### F-A3 Closure Status (Detection-tier source_attribution emission)

`grep -l "source_attribution" .claude/agents/tachi/*.md | wc -l` = **14** (target met):
- 3 pre-existing F-1/F-2/F-4 net-new agents (`output-integrity`, `misinformation`, `human-trust-exploitation`)
- 11 newly-wired F-A3 hosts (Waves 1.1–2.3, T009–T013 + T016–T021)

`DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` frozenset = **11 entries** (T051 closure)
`DETECTION_AGENT_PATHS` = **2 entries** (only `output-integrity` + `misinformation` companions remain — these are the canonical "agent.md is the source of truth" zero-edit references)

---

## Next Actions (Resume Here)

### Wave 5.2 (Days 24–25, Wed 6/3 + Thu 6/4) — 8-baseline regen + SC verification (CHECKPOINT 5)

**6 sequential `senior-backend-engineer` + `tester` tasks** (see agent-assignments.md §"Wave 5.2"):

- **T053** [US1] — `senior-backend-engineer` — Regenerate **6 pre-existing baselines** under `SOURCE_DATE_EPOCH=1700000000`: `web-app` + `microservices` + `ascii-web-api` + `mermaid-agentic-app` + `free-text-microservice` + `maestro-reference`. Run `make regenerate` per-baseline. Verify CA-pages populated; verify non-CA pages byte-identical pre/post via `pdftotext` per-page diff. Estimated 4.0h.
- **T054** [US1] — `senior-backend-engineer` — Author net-new baseline at `examples/predictive-ml-app/sample-report/security-report.pdf.baseline` (canonical path per Architect L-1; mirrors F-6/F-7 convention). Estimated 2.0h.
- **T055** [US1] — `senior-backend-engineer` — Author net-new baseline at `examples/mobile-banking-app/sample-report/security-report.pdf.baseline` (canonical path per Architect L-1). Estimated 2.0h.
- **T056** [US1] — `tester` — Verify SC-007 across all 8 baselines (≥1 row in per-finding attribution + non-zero coverage-percentage on at least one served framework family). Estimated 1.5h.
- **T057** [US1] — `tester` — Verify SC-009 across all 8 baselines (0 ppt delta on 40 cross-check pairs — Mode (a) skips will auto-activate to active once T054 + T055 baselines land). Estimated 1.5h.
- **T058** [US1] — `tester` — Verify SC-015 across all 8 baselines (non-CA pages byte-identical pre/post Stream 4 regen under fixed `SOURCE_DATE_EPOCH=1700000000`). Estimated 1.5h.

**Critical path**: T053 → T054 → T055 (sequential regen) → T056 → T057 → T058 (sequential verification). Total ~12.5h sequential effort. **CHECKPOINT 5 quality gate at end of Day 25**: 8/8 baselines render Coverage Attestation; aggregator emits accurate coverage percentages with 0 ppt delta on 40 cross-check pairs; non-CA pages byte-identical pre/post regen on the 6 pre-existing baselines under `SOURCE_DATE_EPOCH=1700000000`. **BLOCKER per SC-007 + SC-009 + SC-015.**

**Wave 5.1 → Wave 5.2 enablement**: T049's Mode (a) deferred parametrization will auto-activate from 30 → 40 cross-check pairs once T054 + T055 land. Re-run `pytest tests/scripts/test_coverage_percentage_computation.py -q` after T055 — should report 40/40 pass with 0 skip.

### Wave 5.3 (Day 26, Fri 6/5) — ADR-037 narrative + ADR-027 cross-link + §6 demotion + Polish parallel start

T059 (`architect`, ADR-037 D-1..D-10 narrative authoring; **consumes T040 + T041 §3.4 + Wave 4.3 D-8 + Wave 5.1 D-? audit-trails**) + T060 (`architect`, ADR-027 forward-pointer addendum / Architect M-1 resolution) + T061 (`senior-backend-engineer`, BLP-01 §6 demotion annotation) + T062 (contingent FR-008 deferral docs).

**Polish parallel start (overlaps Wave 5.3)**: T071 ‖ T072 ‖ T073 ‖ T074 ‖ T075.

### Wave 6.1 (Day 27, Mon 6/8) — PR title verification + ADR-037 Accepted dual-commit

T063 (`feat(241):` PR title pre-merge check) + T064 (ADR-037 Proposed → Accepted dual-commit pattern) + T080 + T081 + T082 (Architect M-2 sanity-check at line 1073) + T083 + T084.

### Wave 6.2 (Day 28, Tue 6/9) — Triple Triad sign-off + 18 SC verification

T065 (PM + Architect + Team-Lead sign-off on tasks.md) + T066 (verify all 18 SCs) + T070 (owasp.yaml audit completeness post-Stream 2 closures).

### Wave 6.3 (Day 29, Wed 6/10) — PR squash-merge + post-merge SHA + release-please verification

T067 (PR ready + squash-merge --delete-branch) + T068 (ADR-037 Accepted post-merge SHA fill-in) + T069 (release-please PR opens within ~30s; empty marker commit if not) + T076 (CHANGELOG) + T077 (BACKLOG regen) + T078 (delivery retrospective) + T079 (Issue #241 → stage:done). **BLP-01 11-feature initiative closes.**

---

## Prerequisites for Next Session

- ✅ Branch `241-web-api-coverage-attestation` is current
- ✅ Draft PR #242 open with `feat(241):` Conventional Commit title (Wave 5.1 commit pending push)
- ✅ Wave 5.1 work committed (commit `3b88290`); ready to push to remote
- ✅ Wave 4.3 work committed (commit `02acd08`)
- ✅ Wave 4.2 work committed (commit `886e022`)
- ✅ Wave 4.1 work committed (commit `cbe955d`)
- ✅ Wave 3.2 work committed (commit `1561085`)
- ✅ Wave 3.1 work committed (commit `89848ab`)
- ✅ Wave 2 work committed (commit `3e10019`)
- ✅ Wave 1 work committed (commit `7ba5447`)
- ✅ T049 audit-trail file persisted at `.aod/results/tester-T049.md` (Mode (a) deferred decision rationale; consumed by T059 / Wave 5.3 if ADR-037 D-? needs the deferred-parametrization narrative)
- ✅ T050 audit-trail file persisted at `.aod/results/tester-F241-T050.md` (KB-037 invariant guard; T046 anchor regression-guarded; consumed by T059 if ADR-037 D-? needs the stdlib-only-invariant defensibility narrative)
- ✅ T051+T052 audit-trail file persisted at `.aod/results/tester-T051-T052.md` (frozenset shift + Watchlist #2 closure; consumed by T059 if ADR-037 D-? needs the enrichment-frozenset-extension precedent narrative)
- ✅ T048 audit-trail file persisted at `.aod/results/tester-T048-stream-3-4-fixtures.md` (consumed by T059 / Wave 5.3 for ADR-037 D-8)
- ✅ T041 audit-trail file persisted at `.aod/results/T041-T043-attack-expansion.md` (consumed by T059 / Wave 5.3 for ADR-037 D-5)
- ✅ T040 audit-trail file persisted at `.aod/results/T040-attck-tactical-grouping-audit.md` (consumed by T059 / Wave 5.3)
- ✅ ADR-037 stub at status: Proposed (full narrative deferred to T059 / Wave 5.3)
- ✅ All 11 newly-wired Wave 1+2 STRIDE+AI hosts under 200-line cap
- ✅ `test_taxonomy_integrity.py` 5/5 passing on 701-record `mitre-attack.yaml`
- ✅ `test_f_a3_populator_wiring.py` 68/68 passing (Wave 2.3 baseline)
- ✅ `test_coverage_attestation.py` 46/46 passing (Wave 4.3 baseline)
- ✅ `test_coverage_attestation_in_scope.py` 19/19 passing (Wave 4.3 baseline)
- ✅ `test_coverage_percentage_computation.py` 38/38 active + 10 deferred (Wave 5.1 T049 net-new)
- ✅ `test_pyyaml_deferred_import.py` 9/9 passing (Wave 5.1 T050 net-new)
- ✅ `test_backward_compatibility.py` 13/13 + 1 skip passing (Wave 5.1 T051 zero-edit fix landed)
- ✅ Stream 1 closure milestone: 14/14 detection-tier agents emit `source_attribution`; 11 hosts moved to `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` frozenset
- ✅ Stream 3 closure milestone: 3 of 3 taxonomy YAMLs at full inventory (owasp 60 + mitre-atlas 30 + mitre-attack 701 = 791 records carrying +2 fields)
- ✅ Stream 4 closure milestone: filter at line 1073 / dual-emission contract / partition invariant against in-scope denominator / Architect M-2 RESOLVED
- ✅ Test infrastructure milestone: 4 new test scripts (3 net-new + 1 modified) green; 0 new regressions; SC-009 cross-check driver (T049) in place ready for Wave 5.2 baseline activation

**Suggested resume command**:
```
claude "Resume F-241 Web/API Coverage Attestation. Branch: 241-web-api-coverage-attestation. Waves 1.1-1.3 + 2.1-2.3 + 3.1 + 3.2 + 4.1 + 4.2 + 4.3 + 5.1 complete (51/84 tasks); Streams 1+2+3+4 fully closed; test infrastructure authored (T049 30 active + 10 deferred / T050 KB-037 invariant guard / T051+T052 frozenset shift). Run /aod.build to continue with Wave 5.2 (T053-T058 — 8-baseline regen + SC-007/009/015 verification, CHECKPOINT 5)."
```

---

## Architect Carry-Forwards (still pending)

- **M-1**: ADR-027 forward-pointer addendum cross-linking ADR-037 D-7 (T060 + T083, **Wave 5.3**) — unchanged
- **M-2**: ✅ **RESOLVED at Wave 4.3** (filter at `_load_framework_yaml_records()` line 1073; T084 sanity-check pending Wave 6.1 polish)
- **L-1**: Canonical baseline paths for predictive-ml-app + mobile-banking-app (T054 + T055 + T081, **Wave 5.2**) — unchanged
- **MEDIUM-B (Wave 5.1 surfacing)**: ✅ **GUARDED at Wave 5.1 T050** (`test_pyyaml_deferred_import.py` AST walks all `scripts/*.py`; KB-037 invariant regression-guarded; T046 anchor at `extract-report-data.py:1095` validated)
- **NEW (Wave 4.2 surfacing)**: data-model.md §5 should be extended with +2 entries enumerating TA0112 Defense Impairment + TA0043 Reconnaissance; non-breaking spec additive recommended before delivery (or absorbed into ADR-037 D-5 narrative at T059). Documented at `.aod/results/T041-T043-attack-expansion.md` §3.4.
- **NEW (Wave 4.3 surfacing)**: ADR-037 D-8 narrative should explicitly cite line 1073 insertion point + dual-emission rationale. Documented in commit `02acd08` + `.aod/results/tester-T048-stream-3-4-fixtures.md`.
- **NEW (Wave 5.1 surfacing)**: ADR-037 D-? narrative may want to capture the **Mode (a) deferred parametrization decision** (T049 30 active + 10 deferred) as an explicit auditor-facing rationale; auto-activation pattern from skip → pass on T054/T055 baseline landing is testable. Optional ADR enhancement; documented at `.aod/results/tester-T049.md`.

---

## Out-of-Session Risks & Watchlist

1. **Wave 5.2 = CHECKPOINT 5 (BLOCKER per SC-007 + SC-009 + SC-015)** — 8-baseline regen + verification is the gating quality milestone before Wave 5.3 ADR narrative can begin. If ANY baseline fails to render Coverage Attestation OR coverage % delta is ≠ 0 ppt OR non-CA pages byte-differ, the wave is blocked until resolved. Pre-emptive verification: `make regenerate` per-baseline serially under `SOURCE_DATE_EPOCH=1700000000`; `pdftotext` per-page diff for byte-identity check; `pytest tests/scripts/test_coverage_percentage_computation.py -q` for 0-ppt-delta validation.
2. **T049 Mode (a) auto-activation** — once T054 + T055 land, the 10 currently-skipped pairs in `test_coverage_percentage_computation.py` will auto-activate. Re-run to confirm 40/40 active. **If any of the 10 newly-active pairs fail**, the failure is a real Wave 5.2 baseline-quality issue (not a Mode (a) deferral artifact).
3. **8-baseline byte-identity discipline (T053–T058 Wave 5.2)** — non-CA pages on 8 pre-existing baselines must remain byte-identical under `SOURCE_DATE_EPOCH=1700000000` post Stream 4 aggregator change. Wave 4.3 implementation affects ONLY Coverage Attestation page (added in F-A1 ADR-027). Pre-emptive verification approach: `diff <(pdftotext old) <(pdftotext new)` per page; fail fast if any non-CA page byte-differs.
4. **F-7 28-file zero-edit invariant** — F-241 has now modified: 11 host agents + 2 Stream 2 companion catalogs + 3 taxonomy YAMLs + `scripts/extract-report-data.py` + 5 test files (within scope). T075 will verify final compliance at Wave 6.1; current count: 11 + 2 + 3 + 1 + 5 = **22 files modified** within budget (test file edits do not count against detection-tier zero-edit invariant; Wave 5.1 added 2 net-new test files + 1 modification).
5. **Schema unchanged at v1.8** — confirmed at T008; no `id.pattern` regex extension needed. F-241 reuses S/T/I/E/R + LLM/AG/AGP prefixes. Wave 5.1 added no schema changes.
6. **Tactical-grouping defensibility (ADR-037 D-5 at T059)** — T040 documents 7 rationale strings for the spec-enumerated tactics; T041 §3.4 surfaces 2 derived strings for post-spec STIX-update tactics (TA0112 + TA0043); Wave 4.3 contributes the filter-insertion-point + dual-emission rationale (D-8). T059 (Wave 5.3) authors the formal external-auditor-facing justification narrative consuming all three audit-trails.
7. **Pre-existing test failures (15 carry-forward, was 16 pre-Wave-5.1)** — line-cap + citation-completeness + tool-abuse + mobile-pattern-category failures persist:
   - T070 Wave 6.2: owasp.yaml audit completeness verification (may surface citation-completeness root cause)
   - Other line-cap failures: pre-existing fixture metadata; not F-241 scope (deferral candidates per FR-008)
   - Wave 5.1 NET FIX: zero-edit invariant on `agent-autonomy.md` + `prompt-injection.md` resolved by T051 frozenset shift (Watchlist #2 ambiguity from prior NEXT-SESSION now CLOSED — the carry-forward fix WAS Wave 5.1 T051 itself, not a separate Wave 5.2 task)
8. **Wave 4.3 dual-emission Typst contract** — both `yaml-record-count` (raw) AND `in-scope-record-count` (filtered) emit on the same per-framework aggregate dict. The Typst report-template can render either or both; current default consumes `yaml-record-count` for top-line display + `in-scope-record-count` for denominator math. Confirm template renders correctly on Wave 5.2 baseline regen — if any template rendering edits are needed, those land in Wave 5.2 alongside T053.
9. **Wave 5.2 estimated effort = 12.5h sequential** — heavier than typical wave; plan for full session dedicated to T053-T058. If `make regenerate` runs hit unexpected errors on any of the 8 baselines, those become BLOCKING per SC-007/SC-015 — pre-flight `make regenerate` on `web-app` baseline alone first to validate the regen toolchain end-to-end before committing the full T053 sequential run.

---

**End of NEXT-SESSION handoff** — 51/84 tasks complete (60.7%); Streams 1+2+3+4 fully closed; test infrastructure authored at Wave 5.1; resuming at Wave 5.2 (T053–T058 — 8-baseline regen + SC-007/009/015 verification, CHECKPOINT 5 BLOCKER).
