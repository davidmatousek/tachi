# NEXT-SESSION Handoff — F-241 Web/API Coverage Attestation + Populator Wiring

**Generated**: 2026-05-01 (post Wave 4.2)
**Branch**: `241-web-api-coverage-attestation`
**Last Commit**: `886e022` feat(241): Wave 4.2 — Stream 3 ATT&CK 38→701 expansion (T041-T043)
**Draft PR**: #242 (`feat(241):` Conventional Commit title verified)
**User scope**: "Run /aod.build to continue with Wave 4.2 (T041, T042, T043)" — completed; stopping per established single-wave-per-session pattern (matches Wave 3.1 + Wave 3.2 + Wave 4.1 prior sessions).

---

## Progress Snapshot

**Tasks complete**: 42/84 (50.0%)
**Waves complete**: 1.1 + 1.2 + 1.3 + 2.1 + 2.2 + 2.3 + 3.1 + 3.2 + 4.1 + **4.2**
**Phase 5 progress**: Stream 3 fully closed (all 3 taxonomy YAMLs at full inventory). Stream 4 (Wave 4.3) is next.

### Done This Session — Wave 4.2 (Phase 5 Stream 3 ATT&CK expansion)

**T041 — ATT&CK Enterprise 38→701 expansion**:
- Authored full ATT&CK Enterprise inventory from MITRE STIX 2.1 bundle (`https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json`); 663 net-new records (38 → 701 total)
- 7 verbatim T040 tactic-level Out-of-Scope rationale strings applied to TA0005/7/8/9/10/11/40 member items per data-model.md §5 (289 records affected, 76.5% of OOS subset)
- 38 existing records byte-identical on core fields `{id, full_id, name, url, cwe_refs}` per FR-024 + T038 ATLAS precedent (0 mismatches verified)
- **Curator decision flagged for ADR-037 D-5 narrative consumption at T059**: MITRE's current STIX bundle exposes 2 post-spec Enterprise tactics not enumerated in data-model.md §5 — TA0112 Defense Impairment (split from legacy Defense Evasion; 42 OOS-only records) + TA0043 Reconnaissance (Enterprise pre-compromise recon; 46 OOS-only records). 2 derived rationale strings authored using T040's narrative pattern verbatim with TA-ID substitution. Recommended follow-on: extend data-model.md §5 with +2 entries (non-breaking spec additive; documented at `.aod/results/T041-T043-attack-expansion.md` §3.4)
- Schema preamble updated to reflect F-241 expansion (composition note + ADR-037 D-5/D-7 reference)

**T042 — Per-item OOS within in-scope tactics**:
- Conservative scope: T1078.004 Cloud Accounts only (per data-model.md §2 line 110 verbatim string — "Cloud account abuse operates at runtime/IR layer; tachi's design-time threat modeling cannot detect credential validity at the architecture layer.")
- Broader per-item OOS sweep within in-scope tactics deferred to follow-on Issue per FR-008 deferral path (no other techniques explicitly enumerated in spec)

**T043 — Record-shape +2 field verification**:
- 701/701 records carry `out_of_scope` + `out_of_scope_rationale` (100% coverage)
- 323 in-scope records (46.1%) with `out_of_scope: false` + empty rationale `""`
- 378 OOS records (53.9%) with `out_of_scope: true` + non-empty rationale (10 distinct strings: 7 verbatim T040 + 2 derived TA0112/TA0043 + 1 T042 per-item override)

### OOS Rationale Distribution (post-T041/T042)

| Rationale Source | Tactic | Records | %of-OOS |
|-----------------|--------|---------|---------|
| T040 verbatim   | TA0005 Stealth/Defense Evasion | 101 | 26.7% |
| Derived (T041 §3.4) | TA0043 Reconnaissance     | 46 | 12.2% |
| T040 verbatim   | TA0007 Discovery               | 43 | 11.4% |
| Derived (T041 §3.4) | TA0112 Defense Impairment | 42 | 11.1% |
| T040 verbatim   | TA0011 Command and Control     | 41 | 10.8% |
| T040 verbatim   | TA0040 Impact                  | 33 | 8.7%  |
| T040 verbatim   | TA0009 Collection              | 31 | 8.2%  |
| T040 verbatim   | TA0008 Lateral Movement        | 21 | 5.6%  |
| T040 verbatim   | TA0010 Exfiltration            | 19 | 5.0%  |
| T042 per-item   | T1078.004 Cloud Accounts (TA0006-only override) | 1 | 0.3% |
| **Total OOS**   |                                | **378** | **100%** |

### Test Gate (Wave 4.2)

| Suite | Pass/Fail | Status | Notes |
|-------|-----------|--------|-------|
| `tests/schemas/test_taxonomy_integrity.py` | **5/5** | PASS | All ADR-027 schema invariants preserved post-expansion (URL shape, cwe_refs list shape, alphabetical sort, unique IDs, required record keys) |
| `tests/scripts/test_f_a3_populator_wiring.py` | 68/68 | PASS | Wave 2.3 baseline carries forward unchanged |
| `tests/scripts/test_backward_compatibility.py` | 13/14 | PASS (1 pre-existing fail) | Pre-existing zero-edit failure on `agent-autonomy.md` + `prompt-injection.md` (Wave 2 modifications) — scheduled T051 fix |
| **Full suite** | **619/636** | (17 fail / 1 skip) | Delta vs Wave 3.2 baseline (620/16/1): **+1 new failure** = `test_coverage_percentage_arithmetic` (expected interim TDD-Red, scheduled T048 Wave 4.3 fix) |

**The single new failure** (`test_coverage_percentage_arithmetic`) is **expected and scheduled**: fixture asserts `mitre-attack: 2.63%` against the F-A1-baseline (1/38). Post-expansion denominator is 701 raw or 323 in-scope-only (post-T044/T045 filter). The expected post-fix value is `0.31%` (1/323). Resolution at Wave 4.3 T048 (fixture deltas) after T044/T045 (aggregator filter) lands. Test results persisted at `specs/241-web-api-coverage-attestation/test-results/wave-42/results.json`.

### Coverage Progress

**5/5 framework taxonomies** with +2-field record-shape extension status (post Wave 4.2):
- ✅ owasp.yaml (60 records — F-241 T037 Wave 3.2)
- ✅ mitre-atlas.yaml (30 records — F-241 T039 Wave 3.2)
- ✅ **mitre-attack.yaml (701 records — F-241 T041-T043 Wave 4.2)** ← STREAM 3 CLOSURE
- ⏳ nist-ai-rmf.yaml (72 records, +2 fields — outside F-241 Stream 3 scope; reserved for future taxonomy maintenance)
- ⏳ cwe.yaml (53 records, +2 fields — outside F-241 Stream 3 scope; reserved for future taxonomy maintenance)

---

## Next Actions (Resume Here)

### Wave 4.3 (Days 20–21, Thu 5/28 + Fri 5/29) — Stream 4 aggregator extension

**Sequential tasks** (mixed agents — see agent-assignments.md §"Wave 4.3"):

- **T044** [US1] — `senior-backend-engineer` — Apply aggregator denominator filter at `scripts/extract-report-data.py`. Filter at `_load_framework_yaml_records()` (line 1073) OR `load_framework_yaml_record_counts()` (line 1101), **NOT** at `_build_per_framework_aggregate()` (line 1144) where the count is pre-computed. Per Architect M-2 carry-forward + ADR-037 D-8.
- **T045** [US1] — `senior-backend-engineer` — Extend Typst data contract: per-framework aggregates emit `in_scope_yaml_record_count` (filter applied) + preserve `yaml_record_count` (raw) for traceability. Update report-template Typst bindings.
- **T046** [US1] — `senior-backend-engineer` — Per-finding attribution table edge case: findings citing Out-of-Scope items render on attribution table (preserve F-A2 referential-integrity) but DO NOT increment covered_count for the OOS item's own member-set in aggregator math.
- **T047** [US1+US3] — `security-analyst` + `architect` — 8-baseline non-CA-page byte-identity preservation under `SOURCE_DATE_EPOCH=1700000000`: web-app + microservices + ascii-web-api + mermaid-agentic-app + free-text-microservice + maestro-reference + predictive-ml-app + mobile-banking-app + consumer-agent-app. Verify only the Coverage Attestation page changes; all other pages remain byte-identical.
- **T048** [US1] — `tester` + `security-analyst` — Fixture deltas: update `tests/scripts/test_coverage_attestation.py::test_coverage_percentage_arithmetic` expected `mitre-attack` percentage from `2.63%` (F-A1 baseline 1/38) to the post-T044/T045 in-scope-only value (1/323 = `0.31%`). Same review for any other fixtures asserting mitre-attack denominator (`test_extract_report_data.py`, `test_extractor_contract_fixes.py` if applicable).

**Critical path implication**: T044 → T045 → T046 → T047 → T048 (sequential — same file `extract-report-data.py` for T044/T045/T046, then 8-baseline regen requires the aggregator filter in place, then fixture updates require the aggregator output to validate against).

### Wave 5.1 (Days 22–23) — Test infrastructure + Stream 4 fixture authoring

After Wave 4.3 closure: T049 (referential-integrity fixture) + T050 (line-cap test maintenance for affected agents).

### Wave 5.2 (Days 24–25) — 8-baseline PDF regen + zero-edit invariant fix

T051 (zero-edit invariant fix on `agent-autonomy.md` + `prompt-injection.md` — addresses the pre-existing test failure carrying forward since Wave 2.1) + T052 + T053 + T054 (canonical baseline paths) + T055 + T056 + T057 + T058.

### Wave 5.3 (Days 26–27) — ADR-037 + sign-off + merge

T059 (ADR-037 D-5 tactical-grouping narrative authoring — consumes T040 audit-trail + T041 audit-trail §3.4 curator decision on TA0112/TA0043) + T060 (ADR-027 forward-pointer addendum) + T061..T067.

### Wave 6.1 (Day 29) — Polish + post-merge verification

T068..T084 sanity-checks + post-merge release-please verification.

---

## Prerequisites for Next Session

- ✅ Branch `241-web-api-coverage-attestation` is current
- ✅ Draft PR #242 open with `feat(241):` Conventional Commit title
- ✅ Wave 4.2 work committed (commit `886e022`)
- ✅ Wave 4.1 work committed (commit `cbe955d`)
- ✅ Wave 3.2 work committed (commit `1561085`)
- ✅ Wave 3.1 work committed (commit `89848ab`)
- ✅ Wave 2 work committed (commit `3e10019`)
- ✅ Wave 1 work committed (commit `7ba5447`)
- ✅ T041 audit-trail file persisted at `.aod/results/T041-T043-attack-expansion.md` (gitignored ephemeral working artifact; consumed by T059 / Wave 5.3 for ADR-037 D-5 narrative)
- ✅ T040 audit-trail file persisted at `.aod/results/T040-attck-tactical-grouping-audit.md` (consumed by T059 / Wave 5.3)
- ✅ ADR-037 stub at status: Proposed (full narrative deferred to T059 / Wave 5.3; D-5 tactical-grouping defensibility narrative now consumes BOTH T040 + T041 §3.4 curator decision on TA0112/TA0043)
- ✅ All 11 newly-wired Wave 1+2 STRIDE+AI hosts under 200-line cap
- ✅ `test_taxonomy_integrity.py` 5/5 passing on 701-record `mitre-attack.yaml`
- ✅ `test_f_a3_populator_wiring.py` 68/68 passing (Wave 2.3 baseline)
- ✅ `test_backward_compatibility.py` 13/14 passing (1 pre-existing zero-edit failure scheduled for T051 fix)
- ✅ Stream 3 closure milestone reached: 3 of 3 taxonomy YAMLs at full inventory (owasp 60 + mitre-atlas 30 + mitre-attack 701 = 791 records carrying +2 fields)

**Suggested resume command**:
```
claude "Resume F-241 Web/API Coverage Attestation. Branch: 241-web-api-coverage-attestation. Waves 1.1-1.3 + 2.1-2.3 + 3.1 + 3.2 + 4.1 + 4.2 complete (42/84 tasks); Stream 3 fully closed (3/3 taxonomy YAMLs at full inventory). T044/T045 Architect M-2 line 1073/1101 carry-forward ready. Run /aod.build to continue with Wave 4.3 (T044, T045, T046, T047, T048)."
```

---

## Architect Carry-Forwards (still pending)

- **M-1**: ADR-027 forward-pointer addendum cross-linking ADR-037 D-7 (T060 + T083, Wave 5.3) — unchanged
- **M-2**: Aggregator filter at line 1073/1101 not 1144 (T044 + T045 + T084, **Wave 4.3 NEXT**)
- **L-1**: Canonical baseline paths for predictive-ml-app + mobile-banking-app (T054 + T055 + T081, Wave 5.2)
- **NEW (Wave 4.2 surfacing)**: data-model.md §5 should be extended with +2 entries enumerating TA0112 Defense Impairment + TA0043 Reconnaissance; non-breaking spec additive recommended before delivery (or absorbed into ADR-037 D-5 narrative at T059). Documented at `.aod/results/T041-T043-attack-expansion.md` §3.4.

---

## Out-of-Session Risks & Watchlist

1. **T044/T045 line 1073/1101 implementation discipline** — Architect M-2 carry-forward explicitly requires the filter at `_load_framework_yaml_records()` (line 1073) OR `load_framework_yaml_record_counts()` (line 1101), NOT at `_build_per_framework_aggregate()` (line 1144) where the count is pre-computed. Apply at the lowest level so all downstream aggregates inherit the filter automatically. Record verification approach: count `in_scope` records per framework via list comprehension `[r for r in records if not r.get("out_of_scope", False)]` per ADR-037 D-8 contract (data-model.md §3 lines 156–161).
2. **T048 fixture delta scope** — At minimum updates `test_coverage_attestation.py::test_coverage_percentage_arithmetic` (expected `mitre-attack: 2.63%` → `0.31%`). Audit `test_extract_report_data.py` + `test_extractor_contract_fixes.py` + `test_coverage_attestation_pagination.py` + `test_coverage_attestation_tiers.py` for any other fixtures asserting `mitre-attack` denominator counts; update or document deferral.
3. **8-baseline byte-identity discipline (T047)** — non-CA pages on 8 pre-existing baselines (web-app + microservices + ascii-web-api + mermaid-agentic-app + free-text-microservice + maestro-reference + predictive-ml-app + mobile-banking-app + consumer-agent-app) must remain byte-identical under `SOURCE_DATE_EPOCH=1700000000`. The aggregator change at T044 affects ONLY the Coverage Attestation page (added in F-A1 ADR-027). Verify with `diff <(pdftotext old) <(pdftotext new)` per page; fail fast if any non-CA page byte-differs.
4. **F-7 28-file zero-edit invariant** — F-241 has now modified 11 host agents + 2 Stream 2 companion catalogs + 3 taxonomy YAMLs (within scope). T075 will verify final compliance at Wave 6.1; current count: 11 + 2 + 3 = 16 files modified within 11+up-to-5 + 3-taxonomy-YAML budget.
5. **Schema unchanged at v1.8** — confirmed at T008; no `id.pattern` regex extension needed. F-241 reuses S/T/I/E/R + LLM/AG/AGP prefixes.
6. **Tactical-grouping defensibility (ADR-037 D-5 at T059)** — T040 documents 7 rationale strings for the spec-enumerated tactics; T041 §3.4 surfaces 2 derived strings for post-spec STIX-update tactics (TA0112 + TA0043). T059 (Wave 5.3) authors the formal external-auditor-facing justification narrative consuming BOTH T040 verbatim catalog and T041 §3.4 curator decision. Captured as forward-pointer at the wave summary above.
7. **Pre-existing test failures unchanged** — 16 pre-existing failures (zero-edit + line-cap + citation-completeness + tool-abuse 3) carry forward unchanged from Wave 3.2 baseline. Scheduled fixes:
   - T051 (Wave 5.2): zero-edit invariant on `agent-autonomy.md` + `prompt-injection.md`
   - T048 (Wave 4.3): citation-completeness via aggregator filter + fixture deltas
   - Other line-cap failures: pre-existing fixture metadata; not F-241 scope (deferred to follow-on issues per FR-008)

---

**End of NEXT-SESSION handoff** — 42/84 tasks complete (50.0%); Stream 3 fully closed; resuming at Wave 4.3 (T044/T045/T046/T047/T048 Stream 4 aggregator extension + 8-baseline regen).
