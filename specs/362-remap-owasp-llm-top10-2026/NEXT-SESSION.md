# Session Continuation: F-362 Remap OWASP LLM Top 10 → 2026

**Generated**: 2026-08-09 (Session A, part 2 — /aod.build standalone, 3-wave ceiling reached at A6)
**Branch**: `362-remap-owasp-llm-top10-2026`
**Last Commit**: `3f6088e` feat(362): T007 74-edge human disposition complete — ledger 74/74, A6→B phase gate GREEN (Wave A6)
**Draft PR**: #363 (branch pushed through Wave A6)

## Completed This Session (waves A4–A6)

- `277dcae` — **Wave A4 / T005** catalog surgery: all 10 LLM records → 2026 per data-model §2 slot table (LLM08 = Hidden Context Exposure; citations follow category; all URLs = T003 interim anchor; cwe_refs held `[]`; id/order untouched). Integrity 5 passed. Two judgment calls (LLM04 citation authorship, LLM10 ADR-045 clause) — both later ACCEPTED at P1.
- `4dcce21` — **Wave A5 / T006** crosswalk σ-permutation: 57 source.id re-keys in ONE simultaneous pass; precondition re-verified live (645/74/0 LLM-targets); all oracles PASS (645 · 0 dups · primary 608≥500 · vector 8/9/7/8/6/11/4/6/7/8, independently re-derived by orchestrator AND per-edge positionally by P1 architect). Ledger re-key column 74/74.
- `aed1ea1` — **P1 architect checkpoint: APPROVED_WITH_CONCERNS — GO** (scope A3–A5). Both T005 judgment calls ACCEPTED; 5 concerns (3M/2L), none blocking; M-1 (ledger column ownership) + M-2 (data-model LLM04 anchor cell) fixed in this commit; M-3 conditioned into T007; L-2 verified self-closing via T009+T022 union.
- `3f6088e` — **Wave A6 / T007** [MANUAL-ONLY] 74-edge human disposition: 74 valid-2026 / 0 revised / 0 dropped (**zero escalations**); 71 hold / 3 downgrade (rows 29, 40, 72, applied live); citations 61 interim (54 year-slugged + 7 LLM01 per M-3, per-edge rationale) + 13 non-OWASP unchanged; residual 2025-slugged LLM citations = 0. Count-neutrality proven; integrity 5 passed. **A6→B phase gate: PASSED (integrity green + ledger 74/74).**

## Current State

- **Phase**: implement (Build) — issue #362 at stage:build; **Phase 1 + Phase 2 COMPLETE** (the 2026 source of truth is established)
- **Tasks**: 7/26 complete (T001–T007 ✓). Waves 1–6 of 14 done (A1–A6). Session A closed.
- **Uncommitted**: sibling-session churn only (see ⚠️ below). Nothing of F-362's is uncommitted.

## ⚠️ Pre-Flight Warning (unchanged from part 1 — still applies)

The working tree carries ~36 modified PNGs under `examples/{agentic-app,maestro-reference,mermaid-agentic-app}/**/attack-{chains,trees}/` — sibling-session output, NOT F-362's. `examples/**` is the FR-008 carve-out (F-362b): **must not be committed to this branch** (zero protected files on the feature-branch diff). This session verified sibling sessions active (`tachi-fe` et al.) and left them untouched; every F-362 commit stages explicit paths only — continue that discipline. If they are still dirty with no sibling active, ask David; stash (`git stash push -- examples/`) only if David unavailable. Never `git restore` them.

## Critical Context Carried Forward

1. **P0 Ruling 2 (binding on T024)** — no-churn proof form pinned in `test-results-prestate.md` §P0 ruling; baseline regen REJECTED; environmental-red follow-up issue MANDATORY → T026 batch.
2. **P1 rulings (binding)**: LLM04 citation = data-poisoning + model-theft (tampering carries NO LLM attestation — corrected in data-model §2; do not "fix" back at T019). LLM10 carries ADR-030 + ADR-045 lineage. **L-2 forward-quotes**: 3 catalog citations quote 2026-token pattern titles not yet true in source — T009 MUST re-key `tachi-agent-autonomy/references/detection-patterns.md:79`, `tachi-denial-of-service/…:156`, `tachi-model-theft/…:113` (T022 sweep is the net if missed).
3. **Semantic-flip window (P1, informational)**: personas still carry 2025 semantics until T008/T009; id-resolution suites CANNOT detect this (catalog ids unchanged) — green `test_source_attribution.py` is NOT semantic proof until Phase 3 lands. T017's net-new contract test is the compensating check.
4. **T007 non-blocking finding → T026 batch**: re-anchoring the 8 related-type OWASP→ATLAS edges (ledger rows 67–74) orphans the F-182 evidentiary chain documented in `schemas/taxonomy/README.md` §4.1 (medium-confidence ceiling tied to citation content); recommend re-verification pass once per-entry 2026 pages exist. Full detail: `.aod/results/security-analyst.md`.
5. **URL policy**: interim anchor `https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/` is the ONLY authorable URL (61 crosswalk citations + 10 catalog records now carry it). Deliver-stage link-rot dispatch validates live.
6. **Post-T007 confidence distribution** (T024 delta context): LLM-keyed edges now 25 high / 47 medium / 2 low (3 downgrades at rows 29, 40, 72).

## Next Actions (Session B — waves 7–8 of 14, per agent-assignments §2)

1. **Wave B1** (4 lanes, at solo-curator cap): T008 personas (SBE) ∥ T009 skill refs (SBE) ∥ T011 legacy mirrors (SBE) ∥ T018 gap analysis (security-analyst, [MANUAL-ONLY], pulled forward per team-lead F7). Lanes disjoint; T008/T009 write their OWN pre-partitioned ledger sections (never the other's).
2. **Wave B2** (after B1): T010 adapters (FR-002 alias-note obligation, per-format checklist in commit message) ∥ T012 tests+fixtures ∥ T013 templates. T010 AFTER T008+T009 (FR-013); T012/T013 AFTER T008.
3. **B-close gates**: per-bucket checklists complete in commit messages + local gated 15-module subset green (read exact invocation from `.github/workflows/tachi-pytest.yml`; commit first — harness clones committed HEAD) + `gap-analysis.md` complete (4 absorption records) — **any Partial-downgrade signal raised HERE** (two sessions of runway is the whole point of F7).
4. Session C afterwards: C1 = T014 ∥ T015 ∥ T016 ∥ T019, C2 = T017 ∥ T020 ∥ T021.

## Context Files

- `specs/362-remap-owasp-llm-top10-2026/tasks.md` — task text + dependencies (7/26 checked)
- `specs/362-remap-owasp-llm-top10-2026/agent-assignments.md` — wave map, gates, escalation triggers
- `specs/362-remap-owasp-llm-top10-2026/data-model.md` — §2 slot table (P1-corrected), §5 bare-ledger tiers (T008/T009 lane populations)
- `specs/362-remap-owasp-llm-top10-2026/bare-code-ledger.md` — Tier-A lane sections T008/T009 (append-only-to-your-own-section)
- `specs/362-remap-owasp-llm-top10-2026/crosswalk-disposition-ledger.md` — COMPLETE 74/74 (reference for downstream waves)
- `specs/362-remap-owasp-llm-top10-2026/test-results-prestate.md` — T024 reconciliation base + P0 ruling
- `.aod/results/architect.md` — full P1 review (rulings M-1..M-3, L-1..L-2)
- `.aod/results/security-analyst.md` — full T007 per-edge evidence

## Resume Command

```bash
claude "Resume F-362 implementation (branch: 362-remap-owasp-llm-top10-2026). Waves 1-6 complete (T001-T007; Phase 2 done; A6→B gate PASSED; P1 GO). Run /aod.build to continue with Wave 7 (B1: T008 ∥ T009 ∥ T011 ∥ T018). Read specs/362-remap-owasp-llm-top10-2026/NEXT-SESSION.md first — sibling-session examples/** PNG warning still applies."
```
