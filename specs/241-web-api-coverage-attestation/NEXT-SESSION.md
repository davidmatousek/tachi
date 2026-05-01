# NEXT-SESSION Handoff — F-241 Web/API Coverage Attestation + Populator Wiring

**Generated**: 2026-05-01 (post Wave 4.1)
**Branch**: `241-web-api-coverage-attestation`
**Last Commit**: `cbe955d` feat(241): Wave 4.1 — Stream 3 ATT&CK tactical-grouping audit (T040)
**Draft PR**: #242 (`feat(241):` Conventional Commit title verified)
**User scope**: "Run /aod.build to continue with Wave 4.1 (T040)" — completed; stopping per established single-wave-per-session pattern (matches Wave 3.1 + Wave 3.2 prior sessions).

---

## Progress Snapshot

**Tasks complete**: 39/84 (46.4%)
**Waves complete**: 1.1 + 1.2 + 1.3 + 2.1 + 2.2 + 2.3 + 3.1 + 3.2 + **4.1**
**Phase 5 progress**: Stream 3 ATT&CK tactical-grouping audit (Wave 4.1) closed; Stream 3 ATT&CK expansion (Wave 4.2) + Stream 4 (Wave 4.3) remain.

### Done This Session — Wave 4.1 (Phase 5 Stream 3 ATT&CK tactical-grouping audit)

**T040 — ATT&CK Enterprise tactical-grouping audit**:
- 7/7 Out-of-Scope tactic-level rationale strings enumerated verbatim per data-model.md §5
  - TA0005 Defense Evasion — runtime active-malware behavior
  - TA0007 Discovery — runtime active reconnaissance
  - TA0008 Lateral Movement — runtime post-compromise pivoting
  - TA0009 Collection — runtime active data harvesting
  - TA0010 Exfiltration — runtime active data egress
  - TA0011 Command and Control — runtime active C2 channels
  - TA0040 Impact — runtime active impact actions (data destruction, encryption)
- 6/6 In-Scope tactic boundary confirmed (TA0001 / TA0002 / TA0003 / TA0004 / TA0006 / TA0042) — per-item Out-of-Scope rationale on runtime-only sub-techniques inside these tactics deferred to T042
- F-A2 referential-integrity contract preservation rule documented: tactic-grouping does NOT remove member items; they remain catalog-resolvable for any finding citing them with `out_of_scope: true` so the aggregator denominator filter (T044/T045) excludes them from coverage-percentage math
- Hand-off explicit to T041 (Wave 4.2, post-Memorial Day): T041 will apply each verbatim rationale string to all member items of the corresponding tactic during the 38 → ~600 record `mitre-attack.yaml` expansion
- ADR-037 D-5 forward-pointer noted (tactical-grouping defensibility narrative authored at T059 / Wave 5.3)
- Audit-trail file persisted at `.aod/results/T040-attck-tactical-grouping-audit.md` (317 lines; gitignored per `.aod/results/` convention matching T036-T037 + T038-T039 Stream 3 audit-trail pattern)

### Test Gate (Wave 4.1)

**Per Step 4.5 sub-step 5a**: Post-wave tests SKIPPED — wave produced no source/data file changes. The only commit modifies `specs/241-web-api-coverage-attestation/tasks.md` (markdown) and a gitignored audit-trail file at `.aod/results/T040-attck-tactical-grouping-audit.md`. Test runner not invoked; per Step 4.5 sub-step 5f, no `results.json` artifact written for Wave 4.1.

**Wave 3.2 baseline test status carries forward unchanged**: 620 pass / 16 fail / 1 skip (`tests/scripts/` + `tests/schemas/`). Two TestCitationCompleteness failures remain in expected interim TDD-Red state (gap class: documentation-precision; resolution scheduled at Stream 4 closure / Wave 4.3 OR follow-on audit-trail expansion sweep per Wave 3.2 Watchlist Item 1).

### Coverage Progress

**5/5 framework taxonomies** with +2-field record-shape extension status (post Wave 4.1):
- ✅ owasp.yaml (60 records — F-241 T037 Wave 3.2)
- ✅ mitre-atlas.yaml (30 records — F-241 T039 Wave 3.2)
- ⏳ mitre-attack.yaml (38 → ~600 records, +2 fields — Wave 4.2 T041-T043; rationale strings ready per T040)
- ⏳ nist-ai-rmf.yaml (72 records, +2 fields — outside F-241 Stream 3 scope; reserved for future taxonomy maintenance)
- ⏳ cwe.yaml (53 records, +2 fields — outside F-241 Stream 3 scope; reserved for future taxonomy maintenance)

---

## Next Actions (Resume Here)

### Wave 4.2 (Days 18–19, Tue 5/26 + Wed 5/27) — Stream 3 ATT&CK expansion (post-Memorial Day)

**Sequential tasks** (security-analyst, ~12.0h total):
- T041 [US1] Expand `schemas/taxonomy/mitre-attack.yaml` from 38 → ~600 records — author full ATT&CK Enterprise inventory; apply Out-of-Scope to TA0005/7/8/9/10/11/40 member items at tactic-group level using verbatim rationale strings from T040 audit-trail file (largest single-task effort in F-241 — 6.0h)
- T042 [US1] Author per-item Out-of-Scope rationales on individual runtime-only sub-techniques inside in-scope tactics (TA0001 / TA0002 / TA0003 / TA0004 / TA0006 / TA0042) where applicable (3.5h)
- T043 [US1] Extend `schemas/taxonomy/mitre-attack.yaml` record shape: confirm `out_of_scope` + `out_of_scope_rationale` present on all ~600 records (with `out_of_scope: false` default on in-scope items) (2.5h)

**Memorial Day handling**: Mon 2026-05-25 is non-working. T040 fired Fri 5/22 (Day 17); T041 fires first working day after (Tue 5/26 = Day 18). The 1-day calendar gap is excluded from working-day count and from the 80%/day cap math.

**T040 audit-trail file is the authoritative input for T041**: Read `.aod/results/T040-attck-tactical-grouping-audit.md` first to retrieve the 7 verbatim rationale strings before authoring the 562 net-new records.

### Wave 4.3 (Days 20–21) — Stream 4 aggregator extension

**Sequential tasks**:
- T044 → T045 → T046 → T047 → T048 (sequential aggregator filter implementation + Typst data contract extension + per-finding attribution table edge case + 8-baseline non-CA-page byte-identity preservation + fixture deltas)

---

## Prerequisites for Next Session

- ✅ Branch `241-web-api-coverage-attestation` is current
- ✅ Draft PR #242 open with `feat(241):` Conventional Commit title
- ✅ Wave 4.1 work committed (commit `cbe955d`)
- ✅ Wave 3.2 work committed (commit `1561085`)
- ✅ Wave 3.1 work committed (commit `89848ab`)
- ✅ Wave 2 work committed (commit `3e10019`)
- ✅ Wave 1 work committed (commit `7ba5447`)
- ✅ T040 audit-trail file persisted at `.aod/results/T040-attck-tactical-grouping-audit.md` (317 lines) — gitignored ephemeral working artifact; available locally as authoritative input for T041
- ✅ ADR-037 stub at status: Proposed (full narrative deferred to T059 / Wave 5.3; D-5 tactical-grouping defensibility narrative carries-forward from T040)
- ✅ All 11 newly-wired Wave 1+2 STRIDE+AI hosts under 200-line cap
- ✅ `test_taxonomy_integrity.py` 5/5 passing (Wave 3.2 baseline)
- ✅ `test_f_a3_populator_wiring.py` 68/68 passing (Wave 2.3 baseline)
- ✅ `test_backward_compatibility.py` 13/14 passing (1 pre-existing zero-edit failure scheduled for T051 fix)

**Suggested resume command**:
```
claude "Resume F-241 Web/API Coverage Attestation. Branch: 241-web-api-coverage-attestation. Waves 1.1-1.3 + 2.1-2.3 + 3.1 + 3.2 + 4.1 complete (39/84 tasks); ADR-027 contract preserved (5/5 schema integrity tests). T040 audit-trail file ready at .aod/results/T040-attck-tactical-grouping-audit.md. Run /aod.build to continue with Wave 4.2 (T041, T042, T043)."
```

---

## Architect Carry-Forwards (still pending)

- **M-1**: ADR-027 forward-pointer addendum cross-linking ADR-037 D-7 (T060 + T083, Wave 5.3)
- **M-2**: Aggregator filter at line 1073/1101 not 1144 (T044 + T045 + T084, Wave 4.3)
- **L-1**: Canonical baseline paths for predictive-ml-app + mobile-banking-app (T054 + T055 + T081)

---

## Out-of-Session Risks & Watchlist

1. **T041 is the largest single-task effort in F-241 (6.0h)** — 38→600 record expansion (562 net-new records). Per Team-Lead MEDIUM-2 + agent-assignments.md HIGH-A absorption note, Memorial Day (Mon 5/25) provides natural pacing buffer between Wave 4.1 (Fri 5/22) and Wave 4.2 (Tue 5/26). Risk 1 contingency: defer T041 to follow-on Issue per FR-008 deferral path if expansion overruns Day 17–19 budget; ATLAS + OWASP closure + F-A3 wiring + 6 Partial item closure remain in feature scope regardless.
2. **Citation-format remediation gap (carried from Wave 3.2)** — 13 OWASP ids missing from pattern catalogs + 18 from agent metadata in literal-substring matching. Test docstring expects PASS at Stream 4 closure (Wave 4.3) but Stream 4 work doesn't directly modify agents/patterns. **Decision still needed**: either (a) extend Wave 4.3 scope to include citation-format expansion sweep, or (b) defer to follow-on Issue post-F-241. Captured in `specs/241-web-api-coverage-attestation/test-results/wave-32/results.json` `new_failure_classification.follow_on_remediation`.
3. **Pre-existing baseline byte-identity** — non-CA pages on 6 pre-existing baselines must remain byte-identical under `SOURCE_DATE_EPOCH=1700000000`. Wave 4.1 work modifies only `tasks.md` (no pipeline code, no YAML data) and does not affect baseline rendering. Verified at Wave 5.2 T058.
4. **F-7 28-file zero-edit invariant** — F-241 has now modified 11 host agents + 2 Stream 2 companion catalogs + 2 taxonomy YAMLs (within scope). T075 will verify final compliance with the 11+up-to-5 modification budget plus 3 taxonomy YAML edits per Stream 3 scope. Wave 4.2 will add the third taxonomy YAML edit (`mitre-attack.yaml` 38→600 expansion).
5. **schema unchanged at v1.8** — confirmed at T008; no `id.pattern` regex extension needed (F-241 reuses S/T/I/E/R + LLM/AG/AGP prefixes).
6. **Deferred PDF-regen verification** — T053 (Wave 5.2, Days 24–25) — the 8-baseline regen under `SOURCE_DATE_EPOCH=1700000000` will be the final SC-007 / SC-009 / SC-015 BLOCKER verification.
7. **Tactical-grouping defensibility** — T040 documents 7 rationale strings designed to be defensible by external auditor; ADR-037 D-5 contingency narrative authored at T059 (Wave 5.3) provides the formal justification. Risk 5 captured at agent-assignments.md.

---

**End of NEXT-SESSION handoff** — 39/84 tasks complete (46.4%); resuming at Wave 4.2 (T041 expansion, post-Memorial Day Tue 5/26).
