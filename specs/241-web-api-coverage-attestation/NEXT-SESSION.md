# NEXT-SESSION Handoff — F-241 Web/API Coverage Attestation + Populator Wiring

**Generated**: 2026-05-01 (post Wave 5.2)
**Branch**: `241-web-api-coverage-attestation`
**Last Commit**: `d744c23` feat(241): Wave 5.2 — 8-baseline regen + SC-007/009/015 verification (T053-T058, CHECKPOINT 5)
**Draft PR**: #242 (`feat(241):` Conventional Commit title verified; pushed at 2026-05-01)
**User scope**: "Run /aod.build to continue with Wave 5.2 (T053-T058 — 8-baseline regen + SC-007/009/015 verification, CHECKPOINT 5)" — completed; stopping per established single-wave-per-session pattern (matches Wave 3.1/3.2/4.1/4.2/4.3/5.1 prior sessions).

---

## Progress Snapshot

**Tasks complete**: 57/84 (67.9%)
**Waves complete**: 1.1 + 1.2 + 1.3 + 2.1 + 2.2 + 2.3 + 3.1 + 3.2 + 4.1 + 4.2 + 4.3 + 5.1 + **5.2**
**Phase 5 progress**: Streams 1+2+3+4 fully closed; test infrastructure authored; **8/8 baselines regenerated with populated Coverage Attestation pages**. Wave 5.3 (ADR-037 narrative + ADR-027 cross-link + §6 demotion + Polish parallel start) is next.

### Done This Session — Wave 5.2 (CHECKPOINT 5 BLOCKER closure)

**T053 — 6 pre-existing baselines regenerated**:
- Approach: surgical `## 9. Source Attribution` YAML-block backfill (asymmetric to F-1/F-2/F-4 full-orchestrator regen pattern; codified for ADR-037 D-? at T059)
- All 6 PASS SC-007 + SC-015 + FR-A2 (referential integrity, 0 validation errors)
- Coverage spread: web-app/microservices/free-text 13.33% → ascii-web-api/maestro 15.00% → mermaid-agentic-app 26.67% (highest pre-existing baseline)
- Audit-trail: `.aod/results/sbe-T053-regen.md`
- Helper scripts: `.aod/results/sbe-T053-{append_section9.py,strip_section9.py,regen_baseline.sh,diff_pdfs.sh}`

**T054 + T055 — 2 net-new baselines authored**:
- T054 predictive-ml-app: 43 findings, OWASP 21.67%, canonical path `examples/predictive-ml-app/sample-report/security-report.pdf.baseline` per Architect L-1
- T055 mobile-banking-app: 31 findings, OWASP 25.00% (HIGHEST single-baseline OWASP coverage in F-241 corpus); M8 dual-host architectural-tells **runtime-validated at per-finding attribution layer** (5 findings cite M8 across privilege-escalation + repudiation hosts — first runtime validation of ADR-036 D-4 contract)
- Audit-trail: `.aod/results/sbe-T054-T055-net-new.md`

**T056 — SC-007 verified across all 8 baselines**: 8/8 PASS (≥1 per-finding row + non-zero OWASP coverage); ATT&CK/ATLAS/NIST AI RMF/CWE all 0.00% — acceptable per SC-007 ("non-zero on at least 1 framework family") and BLP-01 Tier-2 OWASP-only mapping per ADR-035 D-3 + ADR-036 D-3.

**T057 — SC-009 verified**: 48/48 PASS via `pytest tests/scripts/test_coverage_percentage_computation.py` (40 baseline-framework cross-check pairs at 0 ppt delta + 8 edge-case tests). Mode (a) deferred parametrization lifted (T049 deferral resolved; auto-activation contract honored — 30 active + 10 deferred → 40 active). Test infrastructure update extended `BASELINES` tuple with compensating-controls.md path + Tier-1 vs Tier-3 path selection mirroring `extract-report-data.py` line 2079-2110 runtime tier rule.

**T058 — SC-015 verified**: 8/8 PASS, 0 unmatched non-CA pages across corpus. Cross-verified independently via `git show HEAD:` pre-Wave-5.2 reference + footer-stripped pdftotext diff.

**Audit-trail**: `.aod/results/tester-T056-T058-verification.md` + helper scripts `.aod/results/tester-T056-verify_ca.py` + `.aod/results/tester-T058-diff_pdfs.sh`.

### Test Gate (Wave 5.2)

| Suite | Pre-Wave-5.2 | Post-Wave-5.2 | Delta | Notes |
|-------|--------------|----------------|-------|-------|
| `test_coverage_percentage_computation.py` | 38 pass / 10 skip | **48/48 active** (40 cross-check + 8 edge) | **+10 pass, -10 skip** | Mode (a) lift + Tier-1 path |
| Full suite | 682/708 (15 fail / 11 skip) | **692/708 (15 fail / 1 skip)** | **+10 pass, 0 new regression, -10 skip** | T049 deferral resolved |

**15 carry-forward failures unchanged** (line-cap + citation-completeness + tool-abuse + mobile-pattern-category — pre-existing F-3/F-5/F-6/F-7 close-out items; not in F-241 scope; deferral candidates per FR-008).

### CHECKPOINT 5 Architect Review

**Status**: APPROVED_WITH_CONCERNS (0 BLOCKING / 0 HIGH / 4 MEDIUM / 3 LOW — all narrative/amendment, none blocking)
**Review path**: `.aod/results/architect-checkpoint-5-241.md`

**Top concerns** (all flagged for ADR-037 D-? narrative at T059):
1. **6 findings missing source_attribution keys** (V6 absent-key semantic) — microservices/R-3, ascii-web-api/R-2, free-text-microservice/{S-3,D-3}, mermaid-agentic-app/{R-2,AG-4}. Recommend T053 amendment OR ADR-037 absent-key doctrine codification.
2. **ADR-037 D-11 needed**: surgical backfill approach (asymmetric to F-1/F-2/F-4 net-new full-orchestrator pattern)
3. **ADR-037 D-7 extension**: CWE catalog substitution rule (CWE-307→287, CWE-204→200, CWE-311→522, CWE-913→94, CWE-451→345, CWE-319/311/326→200, CWE-732→285 — parent-CWE abstraction when child absent from 53-record `schemas/taxonomy/cwe.yaml`)
4. **ADR-037 D-12**: OWASP-only Tier-2 closure rationale (ATT&CK/ATLAS/NIST AI RMF/CWE all 0.00% — multi-framework populator wiring is forward-scope improvement candidate)
5. **ADR-037 D-13**: auto-activation contract refinement (T049 Mode (a) deferred parametrization → 40/40 active under controlled regen — testable invariant pattern for future BLP features)

### F-A3 Closure Status (unchanged)

`grep -l "source_attribution" .claude/agents/tachi/*.md | wc -l` = **14** (target met; unchanged from Wave 5.1).

---

## Next Actions (Resume Here)

### Wave 5.3 (Day 26, Fri 6/5) — ADR-037 narrative + ADR-027 cross-link + §6 demotion + Polish parallel start

**4 sequential cross-cutting tasks** (see agent-assignments.md §"Wave 5.3"):

- **T059** [US3] — `architect` — Author full ADR-037 narrative (D-1..D-10 per plan §"ADR-037 D-numbered Decision Outline"; status: Proposed; 10-row mapping table). **Architect M-? from Wave 5.2 surfacing**: ADR-037 may need to be expanded to D-1..D-13 per Wave 5.2 surfacing items (see Architect Carry-Forwards below). Estimated 4.5h.
- **T060** [US3] — `architect` — Address Architect M-1: extend ADR-027 with `## Extension History` forward-pointer addendum cross-linking ADR-037 D-7 (bidirectional). Estimated 0.5h.
- **T061** [US3] — `senior-backend-engineer` — Annotate BLP-01 §6 Coverage Matrix in `_internal/strategy/BLP-01-threat-coverage.md` ("historical — superseded by pipeline-generated attestation" + pointer to F-B section). Estimated 1.0h.
- **T062** [US3] — `product-manager` (pair `architect`) — (Contingent FR-008) If any item deferred per T034: document each Deferral as ADR-037 D-numbered Decision (D-11+) with rationale + Issue link + §6 annotation. Estimated 1.0h (contingent).

**Polish parallel start (overlaps Wave 5.3)**: T071 ‖ T072 ‖ T073 ‖ T074 ‖ T075.

**Critical path**: T059 → T060 → T061 → T062 (sequential cross-cutting). Total ~7h sequential + parallel polish work.

**Quality Gate (end Day 26)**: ADR-037 status=Proposed with full multi-decision narrative; ADR-027 has bidirectional Extension History addendum; §6 Coverage Matrix carries demotion annotation + pointer; full pytest suite + final regen + 4 invariant audits green.

**T059 inputs to consume** (already persisted as audit-trails — read these BEFORE drafting):
- `.aod/results/T040-attck-tactical-grouping-audit.md` — D-5 ATT&CK tactical-grouping rationale (Wave 4.1)
- `.aod/results/T041-T043-attack-expansion.md` — D-5 ATT&CK expansion §3.4 (Wave 4.2)
- `.aod/results/tester-T048-stream-3-4-fixtures.md` — D-8 filter-insertion-point + dual-emission rationale (Wave 4.3)
- `.aod/results/tester-T049.md` — D-? Mode (a) deferred parametrization decision (Wave 5.1)
- `.aod/results/tester-F241-T050.md` — D-? KB-037 invariant guard / T046 anchor (Wave 5.1)
- `.aod/results/tester-T051-T052.md` — D-? frozenset shift / Watchlist #2 closure (Wave 5.1)
- `.aod/results/sbe-T053-regen.md` — D-11 surgical backfill (Wave 5.2)
- `.aod/results/sbe-T054-T055-net-new.md` — D-? mapping derivation extension + M8 dual-host runtime validation (Wave 5.2)
- `.aod/results/tester-T056-T058-verification.md` — D-? CHECKPOINT 5 evidence package (Wave 5.2)
- `.aod/results/architect-checkpoint-5-241.md` — D-11/D-7-ext/D-12/D-13 enumeration (Wave 5.2)

### Wave 6.1 (Day 27, Mon 6/8) — PR title verification + ADR-037 Accepted dual-commit

T063 (`feat(241):` PR title pre-merge check) + T064 (ADR-037 Proposed → Accepted dual-commit pattern) + T080 + T081 + T082 (Architect M-2 sanity-check at line 1073) + T083 + T084.

### Wave 6.2 (Day 28, Tue 6/9) — Triple Triad sign-off + 18 SC verification

T065 (PM + Architect + Team-Lead sign-off on tasks.md) + T066 (verify all 18 SCs) + T070 (owasp.yaml audit completeness post-Stream 2 closures).

### Wave 6.3 (Day 29, Wed 6/10) — PR squash-merge + post-merge SHA + release-please verification

T067 (PR ready + squash-merge --delete-branch) + T068 (ADR-037 Accepted post-merge SHA fill-in) + T069 (release-please PR opens within ~30s; empty marker commit if not) + T076 (CHANGELOG) + T077 (BACKLOG regen) + T078 (delivery retrospective) + T079 (Issue #241 → stage:done). **BLP-01 11-feature initiative closes.**

---

## Prerequisites for Next Session

- ✅ Branch `241-web-api-coverage-attestation` is current
- ✅ Draft PR #242 open with `feat(241):` Conventional Commit title (commit `d744c23` pending push)
- ✅ Wave 5.2 work committed (commit `d744c23`); ready to push to remote
- ✅ Wave 5.1 work committed (commit `3b88290`)
- ✅ Wave 4.3 work committed (commit `02acd08`)
- ✅ Wave 4.2 work committed (commit `886e022`)
- ✅ Wave 4.1 work committed (commit `cbe955d`)
- ✅ Wave 3.2 work committed (commit `1561085`)
- ✅ Wave 3.1 work committed (commit `89848ab`)
- ✅ Wave 2 work committed (commit `3e10019`)
- ✅ Wave 1 work committed (commit `7ba5447`)
- ✅ T053 audit-trail file persisted at `.aod/results/sbe-T053-regen.md` (consumed by T059 / Wave 5.3 for ADR-037 D-11 surgical-backfill narrative)
- ✅ T054+T055 audit-trail file persisted at `.aod/results/sbe-T054-T055-net-new.md` (consumed by T059 for D-? mapping derivation + M8 dual-host runtime validation narrative)
- ✅ T056-T058 audit-trail file persisted at `.aod/results/tester-T056-T058-verification.md` (BLOCKER quality-gate evidence package)
- ✅ CHECKPOINT 5 architect review persisted at `.aod/results/architect-checkpoint-5-241.md` (D-11/D-7-ext/D-12/D-13 enumeration)
- ✅ Helper scripts persisted at `.aod/results/sbe-T053-*.{py,sh}` + `.aod/results/sbe-T054-T055-*.{py,sh}` + `.aod/results/tester-T056-*.py` + `.aod/results/tester-T058-*.sh` (regen pipeline + verification reproducible if Wave 5.2 needs replay)
- ✅ All 8 baselines render Coverage Attestation pages with non-empty per-finding rows + non-zero OWASP coverage (SC-007 BLOCKER green)
- ✅ `test_coverage_percentage_computation.py` 48/48 active (was 38 pass + 10 skip; T049 Mode (a) deferral resolved)
- ✅ `test_coverage_attestation.py` 46/46 unchanged (Wave 4.3 baseline carries forward)
- ✅ `test_coverage_attestation_in_scope.py` 19/19 unchanged
- ✅ `test_taxonomy_integrity.py` 5/5 unchanged
- ✅ `test_f_a3_populator_wiring.py` 68/68 unchanged
- ✅ `test_pyyaml_deferred_import.py` 9/9 unchanged
- ✅ `test_backward_compatibility.py` 13/13 + 1 skip unchanged
- ✅ Stream 4 closure milestone: aggregator emits `in-scope-record-count` + `yaml-record-count` dual fields; per-baseline coverage % computed against in-scope denominator; 40 cross-check pairs at 0 ppt delta
- ✅ ADR-037 stub at status: Proposed (full narrative authoring is the T059 deliverable at Wave 5.3)
- ✅ 22-file budget per Watchlist #4 not exceeded: F-241 cumulative file modifications = 11 host agents + 2 Stream 2 companion catalogs + 3 taxonomy YAMLs + 1 script (`extract-report-data.py`) + 5 test files = **22 files within scope** + Wave 5.2 added 18 baseline files (within `examples/` budget — separate accounting from detection-tier 22-file budget)

**Suggested resume command**:
```
claude "Resume F-241 Web/API Coverage Attestation. Branch: 241-web-api-coverage-attestation. Waves 1.1-1.3 + 2.1-2.3 + 3.1 + 3.2 + 4.1 + 4.2 + 4.3 + 5.1 + 5.2 complete (57/84 tasks); Streams 1+2+3+4 fully closed; 8/8 baselines regenerated with populated Coverage Attestation pages; CHECKPOINT 5 BLOCKER green (SC-007 + SC-009 + SC-015 all PASS). Run /aod.build to continue with Wave 5.3 (T059-T062 — ADR-037 Proposed narrative + ADR-027 cross-link + §6 demotion + Polish parallel start, BLOCKER per PRD Stage 6 entry)."
```

---

## Architect Carry-Forwards (still pending)

- **M-1**: ADR-027 forward-pointer addendum cross-linking ADR-037 D-7 (T060 + T083, **Wave 5.3**) — unchanged
- **M-2**: ✅ **RESOLVED at Wave 4.3** (filter at `_load_framework_yaml_records()` line 1073; T084 sanity-check pending Wave 6.1 polish)
- **L-1**: ✅ **RESOLVED at Wave 5.2** (canonical baseline paths `examples/predictive-ml-app/sample-report/security-report.pdf.baseline` + `examples/mobile-banking-app/sample-report/security-report.pdf.baseline` populated by T054 + T055; T081 sanity-check pending Wave 6.1 polish)
- **MEDIUM-B (Wave 5.1 surfacing)**: ✅ **GUARDED at Wave 5.1 T050** (`test_pyyaml_deferred_import.py` AST walks all `scripts/*.py`; KB-037 invariant regression-guarded)
- **NEW (Wave 4.2 surfacing)**: data-model.md §5 should be extended with +2 entries enumerating TA0112 Defense Impairment + TA0043 Reconnaissance; non-breaking spec additive recommended before delivery (or absorbed into ADR-037 D-5 narrative at T059)
- **NEW (Wave 4.3 surfacing)**: ADR-037 D-8 narrative should explicitly cite line 1073 insertion point + dual-emission rationale
- **NEW (Wave 5.1 surfacing)**: ADR-037 D-? narrative may want to capture the **Mode (a) deferred parametrization decision** (T049 30 active + 10 deferred → 40 active auto-activation pattern). **Auto-activation tested at Wave 5.2 T057 → 48/48 PASS confirms contract.**
- **NEW (Wave 5.2 surfacing — 4 items per Architect CHECKPOINT 5 review)**:
  - **D-11** (surgical backfill approach): asymmetric to F-1/F-2/F-4 full-orchestrator regen pattern; codify the parser-side Section 9 extraction path (`tachi_parsers._extract_source_attribution_block`) as a legitimate alternative to host-agent re-dispatch when finding content is preserved byte-identical; document the trade-off (faster regen but doesn't exercise host-agent populator wiring at runtime)
  - **D-7 extension** (CWE substitution rule): codify parent-CWE abstraction when child-CWE absent from 53-record `schemas/taxonomy/cwe.yaml` (CWE-307→287, CWE-204→200, CWE-311→522, CWE-913→94, CWE-451→345, CWE-319/311/326→200, CWE-732→285); document substitution rationale + future-scope plan to expand cwe.yaml inventory if abstraction loses signal
  - **D-12** (OWASP-only Tier-2 closure rationale): ATT&CK/ATLAS/NIST AI RMF/CWE all 0.00% across 8 baselines is acceptable per SC-007 + BLP-01 Tier-2 OWASP-only mapping per ADR-035 D-3 + ADR-036 D-3; multi-framework populator wiring is forward-scope improvement candidate (potential F-9 in BLP-02 envelope)
  - **D-13** (auto-activation contract): T049 Mode (a) deferred parametrization (30 active + 10 deferred → 40 active under controlled regen) is a testable invariant pattern; codify the auto-activation contract for future BLP features that author baselines incrementally
  - **V6** (absent-key semantic doctrine): 6 findings (microservices/R-3, ascii-web-api/R-2, free-text-microservice/{S-3,D-3}, mermaid-agentic-app/{R-2,AG-4}) lack `## 9. Source Attribution` keys. Either amend T053 to backfill these or codify the V6 absent-key semantic in ADR-037 (e.g., "absent-key findings are intentional Out-of-Scope at the per-finding-attribution layer; coverage % calculation is unaffected since they don't contribute to numerator")

---

## Out-of-Session Risks & Watchlist

1. **Wave 5.3 ADR-037 narrative scope creep** — T059 estimated 4.5h, but Wave 5.2 surfaced 4 net-new D-? items (D-11/D-7-ext/D-12/D-13) + V6 absent-key doctrine. Effective ADR-037 scope expansion: ~30% over baseline 10-decision estimate. Plan accordingly: if T059 takes >6h, consider deferring D-12 (OWASP-only Tier-2 closure) to a follow-on ADR-038 or BLP-02 envelope per Risk 1.
2. **6 absent-key findings (V6) decision** — Two paths: (a) Amend T053 to backfill the 6 missing source_attribution entries (1-2h overhead), or (b) Codify V6 absent-key semantic in ADR-037. Path (a) closes the gap definitively; path (b) declares it intentional. **Architect strong preference: path (a) for cleanliness, but path (b) is acceptable if it's properly justified per `data-model.md` §2 backwards-compat semantic.**
3. **CWE catalog substitution rule** — 12 distinct CWE substitutions applied across T053+T054/T055. If ADR-037 D-7 extension codifies the rule, it should also propose forward-scope work to expand `schemas/taxonomy/cwe.yaml` inventory beyond 53 records (current set focuses on Top 25 + a few selected child-CWEs). Forward-scope candidate for BLP-02 envelope.
4. **ATT&CK/ATLAS/NIST/CWE 0.00% coverage** — Acceptable per SC-007 wording ("non-zero on at least 1 framework family"), but the visual impact of 4 frameworks at 0.00% may concern reviewers. ADR-037 D-12 should preemptively address this and frame multi-framework populator wiring as forward-scope. Consider whether T059 should extend §6 Coverage Matrix annotation to make the OWASP-only-Tier-2 framing explicit.
5. **F-7 28-file zero-edit invariant** — F-241 has now modified: 11 host agents + 2 Stream 2 companion catalogs + 3 taxonomy YAMLs + `scripts/extract-report-data.py` + 5 test files = **22 detection-tier-budget files within scope** + 18 `examples/` baseline files (Wave 5.2 — separate accounting). T075 will verify final compliance at Wave 6.1.
6. **Schema unchanged at v1.8** — confirmed; no `id.pattern` regex extension needed. F-241 reuses S/T/I/E/R + LLM/AG/AGP prefixes. Wave 5.2 added no schema changes.
7. **Pre-existing test failures (15 carry-forward, was 15 pre-Wave-5.2)** — line-cap + citation-completeness + tool-abuse + mobile-pattern-category failures persist:
   - T070 Wave 6.2: owasp.yaml audit completeness verification (may surface citation-completeness root cause)
   - Other line-cap failures: pre-existing fixture metadata; not F-241 scope (deferral candidates per FR-008)
8. **mobile-banking-app + predictive-ml-app `security-report.pdf` (non-baseline) tracked artifacts** — These F-6/F-7 invariant artifacts are byte-identical to `.baseline` (verified via `md5 -q`); no action needed. Just be aware they're now updated alongside `.baseline` post-Wave-5.2 and may show as separate diffs in some `git diff` flows.
9. **Wave 5.3 estimated effort = 7h sequential + parallel polish** — Lighter than Wave 5.2's 12.5h. Should fit comfortably in a single session. If T059 alone takes >6h due to Wave 5.2 D-11/D-7-ext/D-12/D-13 expansion, consider deferring T060/T061/T062 to Wave 5.3b sub-session.

---

**End of NEXT-SESSION handoff** — 57/84 tasks complete (67.9%); Streams 1+2+3+4 fully closed; 8/8 baselines regenerated with populated Coverage Attestation pages; CHECKPOINT 5 BLOCKER green (SC-007 + SC-009 + SC-015 all PASS); resuming at Wave 5.3 (T059–T062 — ADR-037 Proposed narrative + ADR-027 cross-link + §6 demotion + Polish parallel start, BLOCKER per PRD Stage 6 entry).
