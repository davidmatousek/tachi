# NEXT-SESSION Handoff — F-241 Web/API Coverage Attestation + Populator Wiring

**Generated**: 2026-05-01 (post Wave 5.3 + Polish parallel start)
**Branch**: `241-web-api-coverage-attestation`
**Last Commit**: pending — Wave 5.3 commit (this session)
**Draft PR**: #242 (`feat(241):` Conventional Commit title verified; pushed at 2026-05-01)
**User scope**: "Run /aod.build to continue with Wave 5.3 (T059-T062 — ADR-037 Proposed narrative + ADR-027 cross-link + §6 demotion + Polish parallel start, BLOCKER per PRD Stage 6 entry)" — completed; Polish T071-T075 also closed; stopping per established single-wave-per-session pattern.

---

## Progress Snapshot

**Tasks complete**: 67/84 (79.8%)
**Waves complete**: 1.1 + 1.2 + 1.3 + 2.1 + 2.2 + 2.3 + 3.1 + 3.2 + 4.1 + 4.2 + 4.3 + 5.1 + 5.2 + **5.3 + Polish parallel start (T071-T075)**
**Phase 6 progress**: ADR-037 expanded to D-1..D-13 (Proposed); ADR-027 Extension History addendum cross-linking ADR-037 D-7 (bidirectional); §6 BLP-01 Coverage Matrix demotion banner (status: historical, superseded); T062 collapses to NOT-APPLICABLE (all 6 Stream 2 closures clean, T034 NO-OP). Wave 6.1 (PR title verification + ADR-037 Proposed → Accepted dual-commit pattern + Polish carry-forward sanity-checks T080-T084) is next.

### Done This Session — Wave 5.3 + Polish T071-T075

**T059 — ADR-037 Proposed narrative authored**:
- Expanded from 159-line stub to **432 lines** (+273) at `docs/architecture/02_ADRs/ADR-037-web-api-coverage-attestation-and-populator-wiring.md`
- D-numbers expanded **D-1..D-10 → D-1..D-13** with D-7 substantively extended
- D-11 NEW: Surgical Section 9 Backfill Approach for Regen-of-Existing-Baselines (CHECKPOINT 5 surfacing; Stream 4 / cross-cutting; codifies T053 surgical backfill + V6 absent-key semantic for 6 findings + M8 dual-host runtime validation at T055)
- D-12 NEW: OWASP-Only Tier-2 Closure Mapping Rationale (CHECKPOINT 5 surfacing; Cross-cutting; ATT&CK / ATLAS / NIST AI RMF / CWE all 0.00% is CHOICE not oversight per BLP-01 Tier-2 mapping; cross-framework primary attribution forward-scope to BLP-02)
- D-13 NEW: Auto-Activation Contract for Deferred Parametrization (CHECKPOINT 5 surfacing; Stream 1 / Cross-cutting; codifies Mode (a) deferred parametrization at T049 → 48/48 PASS at T057 confirmation)
- D-7 EXTENSION: CWE substitution rule with 8-CWE canonical mapping table + 12-substitution audit + forward-scope flag for catalog growth (BLP-02 envelope)
- D-5 extension: TA0112 Defense Impairment + TA0043 Reconnaissance curator extension narrative for `data-model.md` §5 forward-scope follow-on
- D-8 extension: explicit citation of line 1073 insertion point + dual-emission rationale per Wave 4.3
- 13-row mapping table operationalizing D-1..D-13 across 4 work streams + cross-cutting tier
- Consequences section expanded: 8 Positive bullets + 6 Negative/Trade-offs + 5 Neutral bullets
- Implementation Notes expanded: Wave Timeline (14-row table) + Dual-Commit Lifecycle + 10 Verification Predicates + Helper Script Persistence + Cross-Reference + 7-bullet Forward-Scope/Out-of-Scope Items
- References section authored: ~40 citations across spec/plan/tasks/PRD + schema + F-A1 catalog YAMLs + parser + aggregator + tests + 8 baselines + Wave 5.2 audit-trail + BLP-01 strategy + 7 predecessor ADRs (ADR-030..ADR-036)
- Revision History authored: single-row Proposed entry documenting all 13 D-numbered decisions + dual-commit lifecycle plan
- Architect summary: `.aod/results/architect-T059-adr-037.md`

**T060 — ADR-027 Extension History addendum**:
- Inserted `## Extension History` section (52 lines) at `docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md` between References and Revision History sections
- Documents ADR-037 D-7 +2 field extension scope (`out_of_scope` + `out_of_scope_rationale` defaults)
- Backward compatibility narrative: pre-F-241 records render identically; integrity test suite continues to pass
- Identifies aggregator consumer at `scripts/extract-report-data.py:1073` (`_load_framework_yaml_records()`)
- Includes CWE substitution rule (D-7 inline extension): 8-CWE canonical mapping with forward-scope flag for catalog growth beyond 53 records
- Bidirectional cross-reference assertion: ADR-037 cites ADR-027 in Related ADRs header (line 9); this addendum is the matching back-pointer closing Architect M-1 carry-forward
- Forward-scope discipline: future per-item record-shape extensions MUST author new D-numbered Decision + new Extension History subsection

**T061 — BLP-01 §6 Coverage Matrix demoted**:
- Inserted 22-line status banner at `_internal/strategy/BLP-01-threat-coverage.md` §6 (gitignored internal-strategy file; not in git diff)
- Status banner: "Historical / Superseded (as of F-241 Wave 5.3, 2026-05-01)"
- Documents source-of-truth shift (manual matrix → pipeline-generated Coverage Attestation pages)
- Where-to-look-post-F-241 enumeration: per-architecture Coverage Attestation pages (8 baselines), aggregator implementation lines 1073-2110, F-B initial section (Feature 194 / ADR-029), F-241 attestation completion (Feature 241 / ADR-037), OWASP-only Tier-2 closure rationale via ADR-037 D-12
- Why-preserved-rather-than-deleted rationale: row-level Heuristic A signal-class taxonomy reasoning is materially harder to reconstruct from bare attestation page; future BLP-02 / BLP-03 features must cross-reference precedent
- Maintenance policy post-F-241: frozen; edits accepted ONLY for typo / link-rot corrections, cross-reference additions to superseding ADRs, annotations preserving historical-reference value; **Status column changes NOT accepted** — they belong on the pipeline attestation page

**T062 — Contingent FR-008 deferral path**:
- **NOT-APPLICABLE**: All 6 Stream 2 closures (T025/T026/T028/T029/T030/T031) closed cleanly per [X] markers in tasks.md
- T034 contingent collapses to NO-OP (zero closure failures means no FR-008 deferrals to document)
- ADR-037 D-11/D-12/D-13 from CHECKPOINT 5 surfacings already cover the actual D-numbered expansion at T059 (separate from FR-008 deferrals)

**T034 — Contingent Stream 2 Deferral**:
- **NOT-APPLICABLE**: All 6 Stream 2 closures clean; contingent did not fire; collapses to NO-OP per FR-008 (originally pending [`] now marked [X] with NOT-APPLICABLE annotation)

**Polish parallel start (T071-T075)**:
- **T071** PASS: `python3 -m pytest tests/scripts/` → 692 passed, 15 failed, 1 skipped in 163.98s; **identical to Wave 5.2 baseline (692/15/1)**; zero new regressions
- **T072** PASS-by-construction: Wave 5.3 modified only 3 git-tracked files (ADR-037, ADR-027, tasks.md) + 1 internal-strategy file (BLP-01-threat-coverage.md, gitignored). NO edits to regen pipeline, findings, threats.md, schemas/, or example baselines. Byte-identity holds by construction; SC-015 already verified at Wave 5.2 T058. Explicit re-regen deferred to Wave 6.3 final delivery verification.
- **T073** PASS: empty diff on `pyproject.toml requirements*.txt package.json` (SC-013)
- **T074** PASS: empty diff on `schemas/finding.yaml` (SC-014; v1.8 unchanged; symmetry with F-3/F-5/F-6/F-7 zero-bump enrichment branch)
- **T075** PASS: 11 host agents + 4 companion catalogs = 15 detection-tier files modified, within F-7 28-file budget per FR-021. Specific list: `agent-autonomy + data-poisoning + denial-of-service + info-disclosure + model-theft + privilege-escalation + prompt-injection + repudiation + spoofing + tampering + tool-abuse` (11 hosts) + `info-disclosure + privilege-escalation + tampering + tool-abuse` companion catalogs (4 catalogs)

### Test Gate (Wave 5.3)

| Suite | Pre-Wave-5.3 | Post-Wave-5.3 | Delta | Notes |
|-------|---------------|----------------|-------|-------|
| Full pytest suite | 692/708 (15 fail / 1 skip) | **692/708 (15 fail / 1 skip)** | **0 (no change)** | Wave 5.3 made only doc edits; zero regression |

**15 carry-forward failures unchanged** (line-cap + citation-completeness + tool-abuse + mobile-pattern-category — pre-existing F-3/F-5/F-6/F-7 close-out items; not in F-241 scope; deferral candidates per FR-008).

### F-A3 Closure Status (unchanged)

`grep -l "source_attribution" .claude/agents/tachi/*.md | wc -l` = **14** (target met; unchanged from Wave 5.2).

### ADR-037 Status

- **Status**: Proposed (T064 dual-commit promotes to Accepted at Wave 6.1)
- **Lines**: 432
- **Decisions**: D-1..D-13 (13 total; D-1..D-10 from plan-day skeleton + D-11/D-12/D-13 from CHECKPOINT 5 surfacings; D-7 substantively extended)
- **Stream coverage**: Stream 1 (D-2/D-3/D-13) + Stream 2 (D-4) + Stream 3 (D-5/D-6/D-7) + Stream 4 (D-8/D-9/D-11) + Cross-cutting (D-1/D-10/D-12)
- **Predecessor ADR cross-references**: 7 ADRs (ADR-030/031/032/033/034/035/036) + ADR-027 D-7 extension via T060 bidirectional addendum
- **Forward-scope items**: 7 (CWE catalog growth / cross-framework primary attribution / regen pipeline promotion / data-model.md §5 update / T053 amend for V6 / Coverage Attestation footer annotation / dual-pdf-artifact rationalization)

---

## Next Actions (Resume Here)

### Wave 6.1 (Day 27, Mon 6/8) — PR title verification + ADR-037 Proposed → Accepted dual-commit + Polish carry-forward sanity-checks

**Sequential cross-cutting + parallel polish** (see agent-assignments.md §"Wave 6.1"):

- **T063** [US3] — `senior-backend-engineer` — Squash-merge prep: verify PR #242 title is `feat(241):` Conventional Commit per `.claude/rules/git-workflow.md` two-step Pre-merge enforcement. Estimated 0.25h.
- **T064** [US3] — `architect` — ADR-037 Accepted via dual-commit governance pattern (mirror ADR-035 D-10 / ADR-036 D-10): commit ADR-037 with status `Proposed` (T059 already done), capture pre-merge SHA, fill in Accepted SHA placeholder, commit ADR-037 with status `Accepted` (post-merge SHA fill-in deferred to T067/T068 Wave 6.3). Estimated 1.5h.
- **T080** — `architect` — Verify ADR-037 D-numbered decisions all populated with final rationales (D-1..D-13 per Wave 5.3 expansion). Estimated 1.5h. **Inputs**: ADR-037 432-line draft from T059.
- **T081** — `architect` (pair `senior-backend-engineer`) — Per Architect L-1 carry-forward: confirm canonical baseline path consistency across plan.md, tasks.md, test_backward_compatibility.py, ADR-037 D-9 (`examples/predictive-ml-app/sample-report/security-report.pdf.baseline` + `examples/mobile-banking-app/sample-report/security-report.pdf.baseline`). Estimated 0.5h. **Already RESOLVED at Wave 5.2**; this is consistency-check only.
- **T082** — `architect` — Per Architect M-2 carry-forward: confirm aggregator filter insertion point clearly documented in ADR-037 D-8 narrative (line 1073 `_load_framework_yaml_records()`, NOT line 1144). Estimated 0.5h. **Already RESOLVED at Wave 4.3**; this is documentation-presence check.
- **T083** — `architect` — Per Architect M-1 carry-forward: confirm bidirectional cross-link between ADR-027 addendum and ADR-037 D-7 back-reference (T060 already authored the addendum; this verifies bidirectional). Estimated 0.5h.
- **T084** — `architect` (pair `senior-backend-engineer`) — Sanity-check Architect M-2 implementation: open `extract-report-data.py` post-edit; confirm filter at chosen insertion point (line 1073 NOT line 1144). Estimated 0.5h.

**Critical path**: T063 (PR title pre-merge) → T064 (ADR-037 Accepted) → T080-T084 polish (sequentially or parallel where independent). Total ~5.25h for architect on Day 27 (slightly above 0.65 daily load; absorbs since contingent T062 collapsed at Wave 5.3, freeing Day 26 budget).

**Quality Gate (end Day 27)**: PR #242 title verified `feat(241):` Conventional Commit; ADR-037 dual-commit Proposed → Accepted with placeholder SHA; D-1..D-13 final rationales locked; ADR-027 ↔ ADR-037 D-7 bidirectional cross-link verified; aggregator filter at line 1073 verified.

**T064 deliverable**: Two commits on `241-web-api-coverage-attestation` branch:
1. `chore(241): ADR-037 Proposed at Wave 5.3 T059 [skip ci]` (already done in this session's commit)
2. `chore(241): ADR-037 Proposed → Accepted (provisional date 2026-05-08; SHA <pending-T068-fill>)`

### Wave 6.2 (Day 28, Tue 6/9) — Triple Triad sign-off + 18 SC verification + owasp.yaml audit

T065 (PM + Architect + Team-Lead sign-off on tasks.md) + T066 (verify all 18 SCs) + T070 (owasp.yaml audit completeness post-Stream 2 closures).

### Wave 6.3 (Day 29, Wed 6/10) — PR squash-merge + post-merge SHA + release-please verification + retrospective

T067 (PR ready + squash-merge --delete-branch) + T068 (ADR-037 Accepted post-merge SHA fill-in) + T069 (release-please PR opens within ~30s; empty marker commit if not) + T076 (CHANGELOG) + T077 (BACKLOG regen) + T078 (delivery retrospective) + T079 (Issue #241 → stage:done). **BLP-01 11-feature initiative closes.**

---

## Prerequisites for Next Session

- ✅ Branch `241-web-api-coverage-attestation` is current
- ✅ Draft PR #242 open with `feat(241):` Conventional Commit title
- ✅ Wave 5.3 work committed (this session — pending push)
- ✅ Wave 5.2 work committed (commit `d744c23`)
- ✅ Wave 5.1 work committed (commit `3b88290`)
- ✅ Wave 4.3 work committed (commit `02acd08`)
- ✅ Wave 4.2 work committed (commit `886e022`)
- ✅ Wave 4.1 work committed (commit `cbe955d`)
- ✅ Wave 3.2 work committed (commit `1561085`)
- ✅ Wave 3.1 work committed (commit `89848ab`)
- ✅ Wave 2 work committed (commit `3e10019`)
- ✅ Wave 1 work committed (commit `7ba5447`)
- ✅ ADR-037 at status `Proposed` with full 13-decision narrative (432 lines); architect summary at `.aod/results/architect-T059-adr-037.md`
- ✅ ADR-027 has Extension History addendum cross-linking ADR-037 D-7 (bidirectional)
- ✅ BLP-01 §6 demoted to historical (internal-strategy file; gitignored)
- ✅ All 6 Stream 2 closures clean (T034 + T062 marked NOT-APPLICABLE in tasks.md)
- ✅ Polish T071-T075 all PASS (pytest 692/708 unchanged; byte-identity by construction; deps unchanged; finding.yaml v1.8 unchanged; F-7 28-file budget honored)
- ✅ Test infrastructure intact: `test_coverage_percentage_computation.py` 48/48 active; `test_coverage_attestation.py` 46/46; `test_coverage_attestation_in_scope.py` 19/19; `test_taxonomy_integrity.py` 5/5; `test_f_a3_populator_wiring.py` 68/68; `test_pyyaml_deferred_import.py` 9/9; `test_backward_compatibility.py` 13/13 + 1 skip
- ✅ All 8 baselines render Coverage Attestation pages with non-empty per-finding rows + non-zero OWASP coverage (SC-007 BLOCKER green from Wave 5.2)
- ✅ 22-file budget per Watchlist #4 not exceeded: F-241 cumulative file modifications = 11 host agents + 2 Stream 2 companion catalogs + 3 taxonomy YAMLs + 1 script (`extract-report-data.py`) + 5 test files = **22 files within scope** + Wave 5.2 added 18 baseline files (within `examples/` budget — separate accounting from detection-tier 22-file budget) + Wave 5.3 added 0 detection-tier files (only ADR + internal-strategy + tasks.md edits)

**Suggested resume command**:
```
claude "Resume F-241 Web/API Coverage Attestation. Branch: 241-web-api-coverage-attestation. Waves 1.1-1.3 + 2.1-2.3 + 3.1 + 3.2 + 4.1 + 4.2 + 4.3 + 5.1 + 5.2 + 5.3 + Polish T071-T075 complete (67/84 tasks); ADR-037 Proposed at D-1..D-13 (432 lines); ADR-027 Extension History addendum landed (T060); §6 BLP-01 demoted (T061); T062 + T034 NOT-APPLICABLE (clean Stream 2 closures); pytest 692/708 unchanged (zero new regressions). Run /aod.build to continue with Wave 6.1 (T063 + T064 + T080-T084 — PR title pre-merge verify + ADR-037 Proposed→Accepted dual-commit + carry-forward sanity-checks)."
```

---

## Architect Carry-Forwards (status update)

- **M-1** (ADR-027 forward-pointer): ✅ **RESOLVED at Wave 5.3 T060** (Extension History addendum landed; T083 sanity-check pending Wave 6.1)
- **M-2** (Aggregator filter insertion point): ✅ **RESOLVED at Wave 4.3** (filter at `_load_framework_yaml_records()` line 1073; T082 documentation-presence check + T084 sanity-check both pending Wave 6.1)
- **L-1** (Canonical baseline path): ✅ **RESOLVED at Wave 5.2** (T054/T055 baselines at canonical paths; T081 consistency-check pending Wave 6.1)
- **MEDIUM-B (Wave 5.1 surfacing)**: ✅ **GUARDED at Wave 5.1 T050** (`test_pyyaml_deferred_import.py` AST walks all `scripts/*.py`; KB-037 invariant regression-guarded)
- **NEW (Wave 4.2 surfacing — TA0112 + TA0043)**: ✅ **ABSORBED into ADR-037 D-5 Forward-scope follow-on narrative** at T059; if not absorbed at Wave 6 polish, this D-5 narrative serves as the build-time discovery audit
- **NEW (Wave 4.3 surfacing — D-8 line 1073 + dual-emission)**: ✅ **EXPLICITLY CITED in ADR-037 D-8 narrative** at T059
- **NEW (Wave 5.1 surfacing — Mode (a) deferred parametrization)**: ✅ **CAPTURED in ADR-037 D-13 narrative** at T059
- **NEW (Wave 5.2 surfacings — 4 items)**:
  - **D-11** (surgical backfill): ✅ **AUTHORED at T059** as ADR-037 D-11
  - **D-7 extension** (CWE substitution rule): ✅ **EXTENDED at T059** as ADR-037 D-7 inline extension
  - **D-12** (OWASP-only Tier-2 closure rationale): ✅ **AUTHORED at T059** as ADR-037 D-12
  - **D-13** (auto-activation contract): ✅ **AUTHORED at T059** as ADR-037 D-13
  - **V6 absent-key semantic**: ✅ **CODIFIED at T059** within ADR-037 D-11 (Path B selected — codify V6 absent-key semantic; Path A T053 amendment documented as known-deferred follow-on item rather than amended in-session per Wave 5.3 scope discipline)

---

## Out-of-Session Risks & Watchlist (status update)

1. ✅ **Wave 5.3 ADR-037 narrative scope creep — RESOLVED**: T059 expanded to 432 lines (well within ADR-035/036 600–700 line precedent). All 4 CHECKPOINT 5 surfacings (D-11/D-7-ext/D-12/D-13) absorbed into single coherent narrative; V6 codified as known-deferred T053-amend cleanup (Path B selected per Architect Wave 5.2 review concern). No follow-on ADR-038 needed.
2. **6 absent-key findings (V6) — DEFERRED to known cleanup**: Path B (codify V6 absent-key semantic in ADR-037 D-11) selected at T059. Path A (amend T053 to backfill 6 missing entries) remains as a known-deferred T053-amend follow-on item; not blocking F-241 delivery. Cleanup can land at any future maintenance pass.
3. **CWE catalog substitution rule — CODIFIED**: ADR-037 D-7 EXTENSION codifies the 8-CWE canonical mapping table + 12-substitution audit. Forward-scope: expand `schemas/taxonomy/cwe.yaml` inventory beyond 53 records when detection-tier evidence demands it; BLP-02 envelope candidate. Aligns with ADR-031 D8 regex-alternation rule precedent (catalog extension under additive-compatibility constraints is a deferred-decision path).
4. **ATT&CK/ATLAS/NIST/CWE 0.00% coverage — ADDRESSED via ADR-037 D-12**: D-12 codifies the OWASP-only Tier-2 closure rationale and frames multi-framework primary attribution as forward-scope (BLP-02 envelope candidate). §6 demotion banner (T061) cross-references ADR-037 D-12 for visual-impact disclosure. Coverage Attestation page footer annotation reserved for Wave 6 polish if reviewer concerns emerge.
5. **F-7 28-file zero-edit invariant — VERIFIED at T075**: 11 host agents + 4 Stream 2 catalogs = 15 detection-tier files modified, within budget. Wave 5.3 added zero detection-tier files.
6. **Schema unchanged at v1.8 — VERIFIED at T074**: empty diff on `schemas/finding.yaml`; F-241 reuses S/T/I/E/R + LLM/AG/AGP prefixes per Wave 5.3 confirmation.
7. **Pre-existing test failures (15 carry-forward, unchanged) — STABLE**: pytest 692/708 (15 fail / 1 skip) identical to Wave 5.2 baseline. Wave 5.3 made only doc edits; zero new regressions. T070 Wave 6.2 owasp.yaml audit completeness verification may surface citation-completeness root cause for some failures; other line-cap failures remain pre-existing fixture metadata.
8. **mobile-banking-app + predictive-ml-app `security-report.pdf` (non-baseline) tracked artifacts — STABLE**: byte-identical to `.baseline` (verified at Wave 5.2). No action needed in Wave 6.1; full re-regen at Wave 6.3 T072 → T067 will validate at delivery.
9. **Wave 6.1 estimated effort = 5.25h architect on Day 27** (T064 ADR-037 Accepted + T080 D-numbered final rationales + T081-T084 polish). Should fit single session. T062 + T034 NOT-APPLICABLE means architect Day 26 budget freed up; Day 27 can absorb T080-T084 polish carry-forward without overrun.

---

**End of NEXT-SESSION handoff** — 67/84 tasks complete (79.8%); ADR-037 Proposed at D-1..D-13 (432 lines); ADR-027 Extension History addendum landed; §6 BLP-01 demoted; T062 + T034 NOT-APPLICABLE (clean Stream 2 closures); Polish T071-T075 all PASS (pytest 692/708 unchanged; byte-identity by construction; deps unchanged; finding.yaml v1.8 unchanged; F-7 28-file budget honored); resuming at Wave 6.1 (T063 + T064 + T080-T084 — PR title pre-merge verify + ADR-037 Proposed→Accepted dual-commit + carry-forward sanity-checks).
