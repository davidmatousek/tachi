# Session Continuation: F-362 Remap OWASP LLM Top 10 → 2026

**Generated**: 2026-08-10 (Session C — /aod.build standalone; waves C1+C2 complete, Session C CLOSED at its planned boundary)
**Branch**: `362-remap-owasp-llm-top10-2026`
**Last Commit**: see `git log` — wave-10 artifact + this handoff (Session C tail)
**Draft PR**: #363 (branch pushed through Wave C2)

## Completed This Session (waves C1 + C2 = waves 9–10 of 14)

- `642e6f5` — **C1 / T014** finding.yaml contract examples: `:109` → LLM01:2026, `:331–332` LLM05→LLM10, **CWE-1426→CWE-79 stale-companion correction** (T007-ledger-evidenced: row 35 homes 1426 at Misinformation; LLM10's disposed CWE set is 79/89/116/78/601/94); `:18`/`:26` verified unaffected
- `040b06a` — **C1 / T016** FR-012b stderr warning in `classify_framework_items` (+34/-0 pure addition): full-catalog guard (not in-scope-filtered — avoids false positives on legitimate OOS citations like `mitre-attack T1070.001`); **byte-neutrality proven 6/6 FR-007a baselines + 584-row direct harness**; test_coverage_attestation 16 passed
- `56343db` — **C1 / T015** FR-012a emitters structural fix: TAXONOMIES + supported_taxonomies() **catalog-derived** (loader reuse via check-catalog-drift.py-precedented importlib pattern; informationUri derived with loud RuntimeError on disagreement); `_OWASP_REFERENCE_BY_PREFIX` OI→LLM10:2026 / MI→LLM07:2026; threats-sarif prose :66/:259–260/:271 (retired "Model Theft" phrase DROPPED — no 2026 equivalent); zero hardcoded LLM names remain (grep-proved)
- `edd05fd` — **C1 / T019** coverage re-derivation [MANUAL-ONLY]: **10/10 Covered on 2026 definitions, downgrade NO — headline holds 50/50**; OWASP_COVERAGE.md → 2026 (matrix row, anchor, immutable-ADR arrow-notation note, 10-row verdict table, residuals R-1/R-2 + **new R-3** LLM08 extrapolative-reach); 5 catalog comment fixes (`:454` quote-prefix, `:462` LLM04 precision, `:494` LLM08 precision, `:510` LLM10 enrichment, `:662` ML09 σ re-key); **4(d) call: data-poisoning dispatch anchor RE-ANCHORED LLM04→LLM05:2026** (dispatch-rules.md:72 + stride-categories-shared.md:46)
- `9a15af2` / `6314ee4` — tasks.md C1/C2 checkboxes · `52e3951` / wave-10 commit — test-gate artifacts
- `957ae96` — **C2 / T017** net-new CI-gated module `test_owasp_2026_contract.py` (**30 tests**: 22-case normalize_owasp_id D2 matrix incl. breadcrumb-passthrough pin + no-CWE-branch documentation + zero-pad pin; 8-case FR-012a derived-taxa vs independent ground truth); tachi-pytest lockstep same commit (paths + invocation + &hardening_paths ×3: module, generate-risk-scores-sarif.py, owasp.yaml); **declared delta 147→177**
- `845cae4` — **C2 / T020** D5 consistency tripwire in test_catalog_drift_guard.py (**declared delta 15→16**): doc LLM-row edition ↔ catalog full_id edition, both cells independently, either-side-lags fails with named culprit; negative-control proven on scratch copy; `&drift_paths` += OWASP_COVERAGE.md (9→10, shared-anchor identity verified)
- `94208a7` — **C2 / T021** restatement sweep 10/10 closed-list surfaces (11 files): README ×5 (:24 PM-INFO-2 resolved), scope.md:24, dev guide :1805/:1815, research guide, system-design :130 (source only, NO fixture regen — #345), INTERFACE-CONTRACT, tech-stack/patterns READMEs, dev-guide-prompt, taxonomy README (**worked examples σ-corrected after orchestrator fact-check** — see Lessons), cwe.yaml:17

**Checkpoints this session**: C1→C2 **FR-009 gate DISCHARGED** — PM APPROVED_WITH_CONCERNS, 0 blocking (LOW-1 LLM05 comment scope wording no-action; LOW-2 → T026 note obligation below; INFO-2 resolved by T021). **T024 ARCHITECT COUNTER-SIGN SECURED** (early, per plan): COUNTER-SIGNED_WITH_CONDITIONS **C1–C8** → `.aod/results/architect-T024-countersign.md`.

## Current State

- **Phase**: implement (Build) — issue #362 at stage:build; Phases 1–5 COMPLETE (US-1 + US-2 + US-3 all landed; only Phase 6 Polish remains)
- **Tasks**: **21/26** (T001–T021 ✓). Waves 1–10 of 14 done. Session C closed at its planned 2-wave boundary (ceiling is a cap, not a quota; D1's repo-wide sweep deserves fresh context and D1→D2→D3 is a serial verification chain best kept in one session).
- **C-close session gates: ALL PASSED (local)** —
  - Gated **16-module** suite on committed HEAD `6314ee4`: **177 passed / 1 skipped / 1 xfailed** — delta-aware reconciliation EXACT (147 pre-state + 30 T017-declared; artifact `test-results/wave-10/results.json`) ✓
  - `test_catalog_drift_guard.py` **16 passed** (T020 declared 15+1; **D5 tripwire true and green on live tree**) ✓
  - Taxonomy integrity **5 passed** ✓
  - Declared test-count deltas present in T017 (`957ae96`) and T020 (`845cae4`) commit messages ✓
  - **CI verification deferred to D-open**: branch pushed at session close; both workflows fire on this PR's paths (tachi-pytest via &hardening_paths incl. the 3 new entries; tachi-catalog-drift via &drift_paths incl. OWASP_COVERAGE.md). Verify green checks on PR #363 at Session D open.
- **Suite states at C-close** (T024 reconciliation base, all literal): gated 177/1/1 (= pre-state + declared deltas) · integrity 5/5 · drift-guard module 16/16 · byte-compat unchanged from B-close (6f/6p/2s — 6 pre-existing T001 font-subset environmental; zero-edit invariant SKIPs by design) · out-of-gate five modules unchanged (5f/90p pre-existing-on-main set; T015 lane re-verified the 2 line-count reds are main-identical 143/162 lines)

## ⚠️ Pre-Flight Warnings

1. **Sibling-session PNGs (unchanged from Sessions A/B)**: ~36 modified PNGs under `examples/{agentic-app,maestro-reference,mermaid-agentic-app}/**/attack-{chains,trees}/` — sibling-session output, FR-008 carve-out (F-362b): **must not be committed to this branch**. Stage explicit paths only. Never `git restore` them.
2. **Cleanup owed (permission-blocked for agents)**: `git branch -D 142-guard-positive-control` — leftover from T012.

## Critical Context Carried Forward

1. **T024 MUST bind the architect counter-sign conditions C1–C8** (`.aod/results/architect-T024-countersign.md`, local gitignored — survives on disk). Headline: PM interpretation AFFIRMED but insufficient as written — Session C put two edits inside the PDF render closure (`extract-report-data.py`, `owasp.yaml`), and the byte-compat suite reports only FIRST divergence, so the offset-224224 environmental red can MASK later content drift. **C1 (mandatory)**: primary no-churn oracle moves to the input boundary. The architect already executed the closure proof statically and it **PASSES** (render path consumes only `id` + `out_of_scope` + record count; owasp.yaml diff touches only `full_id`/`name`/`url`/comments — id set, out_of_scope set, count 60 all byte-identical to main → **F-362 contributed provably zero bytes to all six baselines**). C3–C7 supply the new-red / red-flips-green / totals-reconciliation decision branches. T024 re-measures rather than discovers — put the C1–C8 file in the T022/T023/T024 tester briefs.
2. **T022 pickups (grown this session, additive to the B-close roster)**: (a) `generate-threats-sarif.py:390` — normalize_owasp_id docstring example retains `"OWASP LLM01:2025"` DELIBERATELY (function untouched per T015 instruction; behavior is real and now T017-pinned) → ledger-disposition as documented-current-behavior; (b) `docs/architecture/01_system_design/README.md:3260/:3280/:3290/:3318` — per-feature historical delivery records (as-shipped metadata quotes incl. `LLM03:2025` at :3318) → D7 retained-historical class; (c) B-close roster unchanged: 4 T008 out-of-section bares, 9 T009 Tier-B breadcrumbs, T012 fixture-disposition table, `attack-chain-patterns-shared.md:15` "v2025" prose form, retained-historical pre-declares (05_User_Stories/06_OKRs READMEs), breadcrumb census 25. T021's per-surface trail: `.aod/results/senior-backend-engineer-T021.md`.
3. **T026 additions (beyond the B-close FU-1..FU-5 + copilot-script roster)**: (a) **PM LOW-2 obligation** — record the 4(d) dispatch-anchor re-anchor (data-poisoning → LLM05:2026, deviating from the first-listed-frontmatter convention) so it isn't reverted as drift; fold into FU-1's persona↔catalog parity issue or its own note; (b) **R-3** (T019, LLM08 extrapolative-reach on RAG-context/tool-schema object types — documentary, non-blocking) → candidate fold into FU-1's modality/enumeration issue or the FU-2 boundary-note issue; (c) environmental-red follow-up issue for the 6 byte-compat reds remains MANDATORY (P0 ruling 2).
4. **T025 changelog**: 10-row σ migration table; Hidden Context Exposure rename; ADR-048 hard-cutover + breadcrumb convention; F-362b carve-out + mid-window wrong-attribution risk (NEW-3); consumer migration guidance. T015's "Model Theft phrase dropped (no 2026 equivalent)" and the 4(d) re-anchor are consumer-visible — candidates for the entry.
5. **Rulings still binding**: LLM04 citation = data-poisoning + model-theft (NO tampering). LLM10 = ADR-030+ADR-045 lineage. Interim anchor `https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/` is the ONLY authorable URL; deliver-stage link-rot dispatch validates live. P0 ruling 2: baseline regen REJECTED; no-churn proof form pinned in `test-results-prestate.md` §P0 (now refined by counter-sign C1).
6. **Lessons for D-lane briefs** (from Session C corrections): bare crosswalk ids make the edition UNOBSERVABLE from single edges — always verify against the σ-oracle per-id counts (8/9/7/8/6/11/4/6/7/8) or a discriminating pair (CWE-400@LLM06), never spot-check pairs; "pre-existing failure" attribution requires a pristine-main comparison (T015's 2 line-count reds were main-identical, not T008-induced).

## Next Actions (Session D — waves 11–14 of 14, per agent-assignments §2)

1. **D-open**: verify CI checks green on PR #363 (tachi-pytest 16-module + tachi-catalog-drift, both fired by the C2 push).
2. **Wave D1**: T022 repo-wide sweep + bare-ledger completion (tester; sanity rule: every command form must produce hits pre-remap; Tier A 41/41 union; Tier B Σ = 366 + 103 carve-out; pickups list above).
3. **Wave D2**: T023 init-baseline-tree disposition (tester; default NO-REGEN per architect MEDIUM-2; #345 owns the fixture surface; confirm no OTHER baseline source moved).
4. **Wave D3**: T024 byte-identity + full battery on committed HEAD (tester; **bind counter-sign C1–C8**; delta-aware reconciliation = pre-state + T017/T020 declared deltas = gated 177/1/1, drift 16, integrity 5; xfail/xpass unchanged).
5. **Wave D4**: T025 changelog (SBE) ∥ T026 follow-up issues (product-manager; F-362b blocking-before-next-minor with 8-item checklist + additions above).
6. **Then**: `/aod.deliver` — live link-rot dispatch (no_cache), PM SC-005 re-verification before PR-ready, KB 18 branch/main hygiene, `feat(362):` title on #363, release-please verification, ADR-048 SHA fill.

## Context Files

- `specs/362-remap-owasp-llm-top10-2026/tasks.md` — 21/26 checked
- `specs/362-remap-owasp-llm-top10-2026/agent-assignments.md` — wave map, D-gates
- `specs/362-remap-owasp-llm-top10-2026/test-results/wave-10/results.json` — C-close gate artifact
- `.aod/results/architect-T024-countersign.md` — **C1–C8 decision procedure (bind into T024)**
- `.aod/results/product-manager-T019-gate.md` — FR-009 gate record (LOW-2 → T026)
- `.aod/results/security-analyst-T019.md` — 10-row verdict table + 4(d) rationale
- `.aod/results/senior-backend-engineer-T014/T015/T016/T017/T020/T021.md` — lane evidence (local, gitignored)

## Resume Command

```bash
claude "Resume F-362 implementation (branch: 362-remap-owasp-llm-top10-2026). Waves 1-10 complete (T001-T021; US-1/US-2/US-3 all landed; C-close gates PASSED; FR-009 discharged; T024 counter-sign C1-C8 secured). Run /aod.build to continue with Wave D1 (T022 sweep). Read specs/362-remap-owasp-llm-top10-2026/NEXT-SESSION.md first — T022 pickups, T024 C1-C8 binding, and the sibling-session examples/** PNG warning all apply."
```
