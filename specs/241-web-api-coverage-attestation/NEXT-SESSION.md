# NEXT-SESSION Handoff — F-241 Web/API Coverage Attestation + Populator Wiring

**Generated**: 2026-05-01 (post Wave 3.2)
**Branch**: `241-web-api-coverage-attestation`
**Draft PR**: #242 (`feat(241):` Conventional Commit title verified)
**User scope**: "Continue F-241 with Wave 3.2 (T036, T037, T038, T039)" — completed; stopping per explicit user scope.

---

## Progress Snapshot

**Tasks complete**: 38/84 (45.2%)
**Waves complete**: 1.1 + 1.2 + 1.3 + 2.1 + 2.2 + 2.3 + 3.1 + **3.2**
**Phase 5 progress**: Stream 3 (Wave 3.2) closed; Stream 3 ATT&CK (Wave 4.1+4.2) + Stream 4 (Wave 4.3) remain.

### Done This Session — Wave 3.2 (Phase 5 Stream 3 OWASP audit + ATLAS expansion)

**T036 — owasp.yaml citation-completeness audit**:
- 60/60 OWASP records carry `# citation:` audit-trail comment immediately above each record
- Citation chain verified across 6 frameworks (A01-A10, API1-API10, ASI01-ASI10, LLM01-LLM10, M1-M10, ML01-ML10) cross-referenced against F-1..F-7 ADR closures + F-241 Wave 2.1-3.1 closures
- 4 documentation-precision caveats flagged in `.aod/results/T036-T037-owasp-audit-and-extension.md` (LLM02 / ASI03 / ML02+ML10 / ML05 — attested via host-agent surface coverage but missing explicit ID strings in Pattern Category headings; satisfy BLP-01 §8 Quality Bar)

**T037 — owasp.yaml record-shape +2 fields**:
- 60/60 records carry `out_of_scope: false` (default) + `out_of_scope_rationale: ""` (default)
- Head-comment block extended with ADR-037 D-7 reference + audit-trail convention paragraph
- File grew 477 → 677 lines

**T038 — mitre-atlas.yaml expansion 12 → 30 records**:
- +18 net-new techniques sourced from authoritative atlas-data v5.5
- ATLAS taxonomy phases covered: Reconnaissance / Resource Development / Initial Access / ML Model Access / Execution / Persistence / Defense Evasion / Discovery / Collection / Exfiltration / Impact
- **Closes F-6 ADR-035 D-7 prose-only catalog gap**: AML.T0015 (Adversarial ML), AML.T0019 (Publish Poisoned Datasets), AML.T0031 (Erode ML Model Integrity) now catalog-resolvable per F-A2 referential-integrity contract — eliminates 3-of-6 prose-only ATLAS technique citations from F-6 ADR-035 worked-example narratives
- 5 IDs from task description not in authoritative source flagged as anomalies (AML.T0009, T0022, T0023, T0027, T0033) — see `.aod/results/T038-T039-mitre-atlas-expansion-and-extension.md`

**T039 — mitre-atlas.yaml record-shape +2 fields**:
- 30/30 records carry `out_of_scope: false` (default) + `out_of_scope_rationale: ""` (default)
- 0 records flagged `out_of_scope: true` per conservative ruling (all ATLAS techniques have design-time prevention surfaces; runtime/IR-only exclusion deferred to mitre-attack.yaml tactical-grouping pass at Wave 4.1+4.2)
- File grew 97 → 280 lines

### Test Gate (Wave 3.2 baseline)

**Total**: 620 pass / 16 fail / 1 skip (`tests/scripts/` + `tests/schemas/`)
**Gate decision**: SOFT WARN (continue per non-regression policy)

- ✅ `tests/schemas/test_taxonomy_integrity.py` → 5/5 PASSED (ADR-027 contract preserved)
- ✅ `tests/scripts/test_f_a3_populator_wiring.py` → 68/68 PASSED (Wave 2.3 baseline preserved)
- ⚠️ `tests/scripts/test_coverage_attestation_audit.py` → 12 passed, 2 NEW failures
  - `TestCitationCompleteness::test_every_covered_owasp_has_agent_citation`
  - `TestCitationCompleteness::test_every_covered_owasp_has_pattern_category_citation`
  - **Gate classification**: NEW failures, NOT regressions. Wave-31 baseline had these as SKIPs (gated on `out_of_scope` field absence). T037 lifted the SKIP gate; tests now run and flag literal-string citation gaps.
  - **Designed RED window**: Per docstring "Flips to PASS post-T037 + Stream 4 audit closure". Currently in expected interim TDD-Red state.
  - **Gap class**: documentation-precision (citation format mismatch — YAML id `ASI01` vs agent metadata `ASI-01` / pattern catalogs `A01:2021`). 13 IDs missing from pattern catalogs, 18 from agent metadata.
  - **Follow-on remediation path**: add bare-form OWASP id citations (without hyphen / year suffix) to host agent `owasp_references` arrays + Pattern Category headings during Stream 4 closure or as a follow-on audit-trail expansion sweep
- 14 pre-existing failures unchanged from Wave 3.1 baseline (resolution scheduled at T051 + T052 in Wave 5.1)

### Coverage Progress

**5/5 framework taxonomies** with +2-field record-shape extension:
- ✅ owasp.yaml (60 records — F-241 T037 Wave 3.2)
- ✅ mitre-atlas.yaml (30 records — F-241 T039 Wave 3.2)
- ⏳ mitre-attack.yaml (38 → ~600 records, +2 fields — Wave 4.1+4.2 T040-T043)
- ⏳ nist-ai-rmf.yaml (72 records, +2 fields — outside F-241 Stream 3 scope; reserved for future taxonomy maintenance)
- ⏳ cwe.yaml (53 records, +2 fields — outside F-241 Stream 3 scope; reserved for future taxonomy maintenance)

---

## Next Actions (Resume Here)

### Wave 4.1 (Day 17, Fri 5/22) — Stream 3 ATT&CK tactical-grouping audit start

**Single task** (security-analyst, 2.0h):
- T040 [US1] Begin ATT&CK Enterprise tactical-grouping audit: enumerate Out-of-Scope tactic-level rationales for TA0005 (Defense Evasion), TA0007 (Discovery), TA0008 (Lateral Movement), TA0009 (Collection), TA0010 (Exfiltration), TA0011 (Command and Control), TA0040 (Impact); document rationale strings per data-model.md §5

**Day 17 is the last working day before Memorial Day (Mon 5/25); Wave 4.2 resumes Tue 5/26**.

### Wave 4.2 (Days 18–19, Tue 5/26 + Wed 5/27) — Stream 3 ATT&CK expansion (post-Memorial Day)

**Sequential tasks** (security-analyst, ~14h total):
- T041 [US1] Expand `schemas/taxonomy/mitre-attack.yaml` from 38 → ~600 records — author full ATT&CK Enterprise inventory; apply tactic-level Out-of-Scope rationales from T040 (largest single-task effort in F-241 — 6.0h)
- T042 [US1] Author per-item Out-of-Scope rationales on individual runtime-only sub-techniques inside in-scope tactics (TA0001 / TA0002 / TA0003 / TA0004 / TA0006 / TA0042) (3.5h)
- T043 [US1] Extend `schemas/taxonomy/mitre-attack.yaml` record shape: confirm `out_of_scope` + `out_of_scope_rationale` present on all ~600 records (with `out_of_scope: false` default on in-scope items) (3.0h)

### Wave 4.3 (Days 20–21) — Stream 4 aggregator extension

- T044 → T045 → T046 → T047 → T048 (sequential aggregator + fixture work)

---

## Prerequisites for Next Session

- ✅ Branch `241-web-api-coverage-attestation` is current
- ✅ Draft PR #242 open with `feat(241):` Conventional Commit title
- ✅ Wave 3.2 work committed (commit `1561085`)
- ✅ Wave 3.1 work committed (commit `89848ab`)
- ✅ Wave 2 work committed (commit `3e10019`)
- ✅ Wave 1 work committed (commit `7ba5447`)
- ✅ ADR-037 stub at status: Proposed (full narrative deferred to T059 / Wave 5.3)
- ✅ All 11 newly-wired Wave 1+2 STRIDE+AI hosts under 200-line cap
- ✅ `test_taxonomy_integrity.py` 5/5 passing
- ✅ `test_f_a3_populator_wiring.py` 68/68 passing
- ✅ `test_backward_compatibility.py` 13/14 passing (1 pre-existing zero-edit failure scheduled for T051 fix)
- ✅ Wave 3.2 32-tile audit results files persisted under `.aod/results/T036-T037-owasp-audit-and-extension.md` and `.aod/results/T038-T039-mitre-atlas-expansion-and-extension.md`

**Suggested resume command**:
```
claude "Resume F-241 Web/API Coverage Attestation. Branch: 241-web-api-coverage-attestation. Waves 1.1-1.3 + 2.1-2.3 + 3.1 + 3.2 complete (38/84 tasks); ADR-027 contract preserved (5/5 schema integrity tests). Run /aod.build to continue with Wave 4.1 (T040)."
```

---

## Architect Carry-Forwards (still pending)

- **M-1**: ADR-027 forward-pointer addendum cross-linking ADR-037 D-7 (T060 + T083, Wave 5.3)
- **M-2**: Aggregator filter at line 1073/1101 not 1144 (T044 + T045 + T084, Wave 4.3)
- **L-1**: Canonical baseline paths for predictive-ml-app + mobile-banking-app (T054 + T055 + T081)

---

## Out-of-Session Risks & Watchlist

1. **Citation-format remediation gap (newly surfaced at Wave 3.2)** — 13 OWASP ids missing from pattern catalogs + 18 from agent metadata in literal-substring matching. Test docstring expects PASS at Stream 4 closure (Wave 4.3) but Stream 4 work doesn't directly modify agents/patterns. **Decision needed**: either (a) extend Wave 4.3 scope to include citation-format expansion sweep, or (b) defer to follow-on Issue post-F-241. Captured in `specs/241-web-api-coverage-attestation/test-results/wave-32/results.json` `new_failure_classification.follow_on_remediation`.
2. **Pre-existing baseline byte-identity** — non-CA pages on 6 pre-existing baselines must remain byte-identical under `SOURCE_DATE_EPOCH=1700000000`. The Wave 3.2 work modifies only YAML data files (no pipeline code) and does not affect baseline rendering. Verified at Wave 5.2 T058.
3. **F-7 28-file zero-edit invariant** — F-241 has now modified 11 host agents + 2 Stream 2 companion catalogs + 2 taxonomy YAMLs (within scope). T075 will verify final compliance with the 11+up-to-5 modification budget plus 3 taxonomy YAML edits per Stream 3 scope.
4. **schema unchanged at v1.8** — confirmed at T008; no `id.pattern` regex extension needed (F-241 reuses S/T/I/E/R + LLM/AG/AGP prefixes).
5. **Deferred PDF-regen verification** — T053 (Wave 5.2, Days 24–25) — the 8-baseline regen under `SOURCE_DATE_EPOCH=1700000000` will be the final SC-007 / SC-009 / SC-015 BLOCKER verification.
6. **Wave 4.2 ATT&CK expansion is largest single-task effort in F-241** — T041's 38→600 record expansion (~6.0h) is the schedule's pacing risk per agent-assignments.md HIGH-A absorption note. Memorial Day (Mon 5/25) provides natural pacing buffer between Wave 4.1 (Fri 5/22) and Wave 4.2 (Tue 5/26).

---

**End of NEXT-SESSION handoff** — 38/84 tasks complete (45.2%); resuming at Wave 4.1.
