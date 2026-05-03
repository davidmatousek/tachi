---
feature: 232
codename: F-6 (ml-top-10-coverage-bundle)
title: ML Top 10 Coverage Bundle — Delivery Retrospective
date_authored: 2026-04-28
phase: BLP-01 Tier 2 (sixth feature; first Tier 2 feature)
heuristic_branch: A — enrichment (third execution; first at three-agent scope)
predecessors:
  - F-1 (Feature 201) — LLM05 → output-integrity (new-agent branch)
  - F-2 (Feature 206) — LLM09 → misinformation (new-agent branch)
  - F-3 (Feature 219) — ASI07 → tool-abuse (enrichment branch, single-agent scope)
  - F-4 (Feature 224) — ASI09 → human-trust-exploitation (new-agent branch)
  - F-5 (Feature 229) — LLM10 → denial-of-service + model-theft (enrichment branch, two-agent scope)
adr: ADR-035 (Status: Accepted at squash commit `e325375`)
prs:
  - "233 (initial — Wave 1.0+1.1 16/64 tasks; squash-merged 2026-04-28 at b84552a)"
  - "235 (build closeout — Wave 2.1 through Wave 5.5 38/64 tasks; squash-merged 2026-04-28T17:03:28Z at e325375)"
squash_commits:
  - b84552a (PR #233 — Wave 1.0+1.1 only)
  - e325375 (PR #235 — Wave 2.1+ closeout, the canonical F-6 squash)
release_pr: 234
release_tag: v4.25.0 (release-please PR #234 — auto-aggregated both feat(232) commits 22s post-#235-merge)
target_envelope: 2.5 working days (Wed 2026-04-29 + Thu 2026-04-30 + Fri 2026-05-01) per PRD §Timeline
actual_envelope: ~2 multi-session days (Wave 0 + Wave 1.0+1.1 on Day 1; Wave 2 + Wave 3 on Day 2; Wave 4 + Wave 5 on Day 3) — within envelope; partial-merge incident at PR #233 added ~1h cherry-pick recovery overhead
status: Authored post-merge — merge metadata locked (squash SHA + release-please PR linked)
triad_signoff:
  pm: APPROVED_WITH_CONCERNS (2026-04-27 — 0 BLOCKING / 0 HIGH / 1 MEDIUM resolved / 2 LOW)
  architect: APPROVED (2026-04-27 — 0 BLOCKING / 0 HIGH / 0 MEDIUM / 0 LOW)
  techlead: APPROVED_WITH_CONCERNS (2026-04-27 — 0 BLOCKING / 0 HIGH / 0 MEDIUM / 1 LOW resolved)
---

# F-6 Delivery Retrospective — ML Top 10 Coverage Bundle

> **Anchor task**: T059 (DoD bullet 16 / FR-026 / SC-026). Mirrors F-1 + F-2 + F-3 + F-4 + F-5 same-day-as-delivery retrospective pattern. Captures **third-execution lessons** for the Heuristic A enrichment branch — and the **first execution at three-agent scope**. Together with F-3 (single-agent) and F-5 (two-agent), F-6 establishes the enrichment-branch pattern at three depths and lays precedent for F-7 (Tier 2 Mobile bundle, possibly 5-agent fan-out at M8 cross-STRIDE) and any future multi-OWASP single-bundle features.

---

## 1. Executive Summary

F-6 ships **OWASP ML Top 10:2023 ML01 + ML03 + ML04 + ML06 + ML07 + ML08** (six entries closed across seven Pattern Categories) as the **sixth BLP-01 feature** and **first Tier 2 feature** delivered. **Third execution of the Heuristic A enrichment branch** (after F-3 single-agent + F-5 two-agent) — and the **first execution at three-agent scope**. 64/64 tasks complete post-merge. Delivery ships across two squash-merges due to a partial-merge incident (PR #233 squash-merged Wave 1.0+1.1 prematurely; PR #235 cherry-pick recovery branch shipped Wave 2.1+ closeout). Both feat(232): commits aggregated cleanly into release-please PR #234 v4.25.0 (open since the PR #233 merge; auto-updated 22s after the PR #235 merge — F-212 incident NOT invoked).

The **headline outcome** is closure of OWASP **ML Top 10:2023 = 10/10 Covered** (six F-6 closures plus pre-existing ML02/ML05/ML10 plus F-1's ML09 documentation-only bundling). Combined with F-5's LLM10 closure and F-4's ASI09 closure: **OWASP three-framework total = 30/30 Covered** across LLM Top 10 2025 (10/10) + Agentic Top 10 2026 (10/10) + ML Top 10 2023 (10/10) — the **OWASP AI security framework family is now fully closed by tachi's existing detection agents**.

Empirical validation: 9 NEW F-6 findings emerged on the new `examples/predictive-ml-app/` baseline (T-10 + D-8/D-9/D-10/D-11 + LLM-1/LLM-2/LLM-3/LLM-4) covering Cat 10 tampering + Cat 8/9/10 data-poisoning + Cat 12/13/14 model-theft. 6/6 prior baselines (web-app + microservices + ascii-web-api + mermaid-agentic-app + free-text-microservice + maestro-reference) byte-identical at scale under `SOURCE_DATE_EPOCH=1700000000` per ADR-021 — **zero baseline drift**.

The **load-bearing innovations** of F-6 (vs. F-5 two-agent enrichment baseline):

1. **Three-agent scope** — F-3 enriched a single host (`tool-abuse`); F-5 enriched two hosts (`denial-of-service` + `model-theft`); F-6 enriches three hosts (`tampering` + `data-poisoning` + `model-theft`) carving a six-OWASP-entry surface across input-manipulation + supply-chain-poisoning + model-extraction axes. The 6-edit grep checklist (3 agent files + 3 companion catalogs) is the structural discipline that scales the F-5 two-host pattern to three-host scope without losing the additive-only edit invariant. Cost-per-host stays linear (~2 file edits per host).
2. **ML06 two-facet split (Q-decision plan day; ADR-035 D-4)** — ML06 AI Supply Chain Attacks decomposes into corpus-side (data-poisoning Pattern Cat 10 — Predictive-ML Supply Chain Completeness over Public Dataset Repository / Internal Merchant Transaction History / Feast Feature Store) AND artifact-side (model-theft Pattern Cat 14 — Predictive-ML Artifact Supply Chain over MLflow Model Registry / Weight Checkpoint Storage). Same `examples/predictive-ml-app/` architecture surfaces both without duplication. F-6 is the **second BLP-01 sub-pattern with cross-agent decomposition** (after F-5's Q1 SPLIT) and the **first across two distinct host agents at three-agent scope**.
3. **ML03 vs ML04 disjoint architectural-tells (ADR-035 D-5)** — Both ML03 (Model Inversion) and ML04 (Membership Inference) target the same FraudDetectionML Prediction API surface and cite the same MITRE ATLAS technique (AML.T0024 — Exfiltration via ML Inference API). The disambiguation is **mitigation-vocabulary disjointness**: ML03 = input reconstruction → mitigations target output minimization (logit clipping / output sanitization); ML04 = membership determination → mitigations target inference privacy (differential privacy / membership-query budgeting). F-6 is the **first BLP-01 feature where two OWASP entries share an ATLAS catalog reference but get independent Pattern Categories** with disjoint mitigation taxonomies (model-theft Cat 12 vs Cat 13).
4. **Pattern Category Disambiguation across three companions (ADR-035 D-9)** — Each enriched companion catalog ships an explicit Pattern Category Disambiguation subsection drawing the boundary between the new predictive-ML categories and the pre-existing LLM/agentic categories (tampering Cat 10 vs Cat 1-9; data-poisoning Cat 8/9/10 vs Cat 1-7; model-theft Cat 12/13/14 vs Cat 1-11). This is the **third execution of the disambiguation pattern** (F-3 first / F-5 second; F-6 first at three-companion scale) and proves the pattern scales without overlap-risk regression.
5. **Zero schema bump at three-agent scope** — F-6 reuses existing `T` (tampering) + `D` (data-poisoning) + `LLM` (model-theft) prefixes; no new finding-prefix is introduced. Schema `finding.yaml` `id.pattern` regex alternation stays at the post-F-4 12-prefix family. F-6 is the **third BLP-01 detection feature with zero schema bump** (after F-3 and F-5) and the **first at three-agent scope**. ADR-035 D-6 cross-references ADR-031 D8 (regex-alternation rule) as the **asymmetry F-6 does NOT invoke** and cross-references ADR-032 lines 84+182 + ADR-034 lines 192–204 as **forecasts now fulfilled** at multi-agent and three-agent scope respectively.

---

## 2. What Worked — Reuse Signals for F-7 (Mobile) at Possible 5-Agent Fan-Out Scope

### 2.1 The 5/5-Dimension Reduction Re-Holds at Three-Agent Scope

F-3 demonstrated the 5/5-dimension reduction for single-agent enrichment. F-5 confirmed it at two-agent scope. F-6 now confirms it at **three-agent scope** with no degradation:

| Dimension | F-3 (1-host) | F-5 (2-host) | F-6 (3-host) | Cost saved (vs new agents) |
|-----------|--------------|--------------|--------------|------------------------------|
| New agent file | 0 | 0 | 0 (3 hosts pre-existed) | ~150 lines × 3 = ~450 lines authoring + review |
| New skill directory | 0 | 0 | 0 (3 companions pre-existed) | ~400 lines × 3 = ~1200 lines authoring + review |
| Schema bump | none | none | none | ADR + schema review cycle eliminated |
| Consumers-list edit | none | none | none | ADR-023 invariant proof scope shrinks |
| Functional orchestrator/dispatch edit | none | none | none (Q2 default-NO at architect plan-day per T009 / T010 D-8) | Orchestrator regression risk eliminated |

**Recommendation for F-7 (Mobile)**: The 5/5-dimension reduction is **stable across single-agent, two-agent, and three-agent enrichment scopes**. F-7 may fan out across as many as 5 STRIDE agents at M8 cross-STRIDE Security Misconfiguration (spoofing + tampering + privilege-escalation + repudiation + info-disclosure). The architect should explicitly score against this checklist at SDR time. F-6 demonstrates per-host edit cost stays linear (~2 file edits per host). For 5-host fan-out: ~10 file edits, byte-identity verification across 5 host-companion pairs, single Pattern Category Disambiguation subsection per companion. The pattern should hold.

### 2.2 ML06 Two-Facet Split as a Pattern That Generalizes

F-5 introduced cross-agent vector decomposition (Q1 SPLIT) where one OWASP entry split across two agents along a single vector axis (availability vs economic damage). F-6 generalizes this to **cross-agent facet decomposition** where one OWASP entry (ML06 AI Supply Chain) splits along an architectural-surface axis (corpus storage vs artifact storage) — same OWASP entry, two distinct architectural surfaces, two distinct host agents. The audit-grade rendering is ADR-035 D-3's canonical 8-row mapping table (7 closure rows for the F-6 entries + 4 reference rows for ML02/ML05/ML09/ML10 already-covered + severity-hint annotation column).

**Recommendation for F-7+**: When an OWASP entry has multiple architectural surfaces that map to multiple host agents (e.g., M2 Inadequate Supply Chain Security may split across `tampering` for binary integrity + `data-poisoning` for build-pipeline poisoning), use the ML06 two-facet pattern. Architect plan-day should explicitly score whether each OWASP entry is single-host-single-facet vs cross-host-multi-facet.

### 2.3 ML03 vs ML04 Disjoint-Tells as a Resolution Pattern for ATLAS-Shared Entries

ML03 and ML04 both cite AML.T0024 (Exfiltration via ML Inference API). Naive enrichment would have placed both in the same Pattern Category to avoid duplication, losing OWASP catalog distinguishability. F-6 instead establishes that **catalog-citation overlap does NOT imply Pattern-Category overlap** when mitigation vocabularies are disjoint. ML03 → output-minimization mitigations (logit clipping / output sanitization); ML04 → inference-privacy mitigations (differential privacy / query budgeting). Two distinct Pattern Categories (model-theft Cat 12 vs Cat 13) with shared ATLAS reference but disjoint mitigation arrays.

**Recommendation for F-7+**: When two OWASP entries share an ATLAS / ATT&CK / CWE reference, use mitigation-vocabulary disjointness as the disambiguation key. Encode in ADR Decision similar to ADR-035 D-5.

---

## 3. Team-Lead Concern Absorption Efficacy

All 4 team-lead deferred concerns from plan-time (MEDIUM-1 + MEDIUM-2 + MEDIUM-3 + LOW-1) were absorbed with explicit traceability:

- **MEDIUM-1 (R5 deferral pair)**: Pre-named pair = data-poisoning Cat 10 (T022) + model-theft Cat 14 (T031), both ML06 facets. **Outcome**: NOT triggered. Both pair items field-validated via Wave 4.0 regen on `examples/predictive-ml-app/` (D-10 corpus-side finding + LLM-3 artifact-side finding both emit cohesively). R5 contingency unused; spec OoS-15 ML06 closure achieved at primary scope.
- **MEDIUM-2 (Day 1 PM checkpoints)**: T020/T021/T022 sequential T-NN-1/2/3 ~90-min units with rollback capability. **Outcome**: All three checkpoints landed clean; no rollback invoked. Sequential discipline prevented same-file write conflicts on data-poisoning agent + companion.
- **MEDIUM-3 (Day 2 PM tester)**: FR-025 + T046/T047 explicit tester-owned parallel with Wave 4.0. **Outcome**: Wave 4.1 tester spot-check (web-app + maestro-reference) returned 2/2 byte-identical at 5h overlap with Wave 4.0 senior-backend pipeline regen. **Weak-parallelism efficacy proven** (true background execution at small overhead).
- **LOW-1 (Day 3 AM split)**: T048 tester (AM-1) + T049 architect (AM-2) two-owner parallel. **Outcome**: Both completed independently with no coordination overhead; T048 6/6 byte-identical + T049 ADR-035 10/10 D-N PASS verification.

Plan-time triple sign-off was carried through delivery as final sign-off without need for formal re-review (per F-5 precedent at T055 audit pattern).

---

## 4. ATLAS Catalog Gap Propagation — Three Times the F-5 Scale

F-5 cited MITRE ATT&CK T1496 (Resource Hijacking) in worked-example narrative prose only because T1496 is not catalog-resolvable per `schemas/taxonomy/mitre-attack.yaml`. F-6 scales this to **3 of 6 MITRE ATLAS techniques as prose-only** (3x F-5 T1496 precedent scale):

| Technique | Cited in | Catalog-resolvable? | Treatment |
|---|---|---|---|
| AML.T0015 (Evade ML Model) | tampering Cat 10 worked example | NO (absent from `mitre-atlas.yaml`) | prose-only narrative |
| AML.T0018 (Backdoor ML Model) | tampering Cat 10 + data-poisoning Cat 8 references | YES (4 entries in catalog) | references-array |
| AML.T0019 (Publish Poisoned Datasets) | data-poisoning Cat 8 worked example | NO | prose-only narrative |
| AML.T0020 (Poison Training Data) | data-poisoning Cat 9 references | YES (4 entries) | references-array |
| AML.T0024 (Exfiltration via ML Inference API) | model-theft Cat 12 + Cat 13 references | YES (4 entries) | references-array |
| AML.T0031 (Erode ML Model Integrity) | data-poisoning Cat 9 worked example | NO | prose-only narrative |

ADR-035 D-7 codifies the rule: **non-catalog-resolvable ATLAS techniques may appear in worked-example prose but MUST NOT appear in `references` array entries**. T038 fixture-tier verification confirmed 0 references-array entries for AML.T0015 / T0019 / T0031 across all F-6 fixtures and the regenerated `predictive-ml-app/` findings. F-A2 referential-integrity contract held against three independent populators (F-1 + F-2 + F-6 — F-3/F-4/F-5 also produce attribution but at smaller scope).

**Recommendation for F-7+**: Architect plan-day should run an explicit ATLAS / ATT&CK / CWE catalog-resolvability sweep against the proposed citation set. Non-resolvable items get prose-only treatment with explicit ADR Decision. T1496 + T0015/T0019/T0031 establish that a 25–50% catalog-gap rate is normal and not a blocker.

---

## 5. Documentation Discrepancy — `tests/scripts/test_backward_compatibility.py` F-5 Carve-Out Off-By-2

**Discovered at**: T051 implementation (2026-04-28 morning).

**Symptom**: The plan-time tasks.md text for T051 specified `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` frozenset extension `5 → 7` (adding 2 F-6 entries — `tachi-tampering` + `tachi-data-poisoning`). The senior-backend-engineer agent assumed the F-5 carve-out had created a 5-element baseline. Empirical inspection of the file showed only **3 entries** (F-3's `tachi-tool-abuse` + F-5's `tachi-denial-of-service` + `tachi-model-theft`), not 5.

**Root cause**: tasks.md was authored at plan-time (2026-04-27) before F-5 had finalized its frozenset entries. The plan-time count `5` was forecast, not measured. The actual F-5 carve-out count was 3 (single F-3 entry + 2 F-5 entries).

**Resolution**: Implemented the correct delta `3 → 5` (adding tachi-tampering + tachi-data-poisoning). pytest 13/14 PASS + 1 skipped (pre-existing T033 unrelated to F-6). Documentation discrepancy flagged in T051 task note for retrospective; no functional regression.

**Lesson for F-7+**: Plan-time counts of pre-existing test infrastructure entries should be replaced with `<TBD-measure-at-build-time>` placeholders. Any count assertion about F-N's resulting state (post-PR-merge) is reliable; counts about prior-feature state (pre-N) are forecast-only and should be empirically re-measured at build-time.

---

## 6. Branch History Incident — PR #233 Partial-Merge Cherry-Pick Recovery

**Symptom**: PR #233 squash-merged at 2026-04-28 with title `feat(232): ML Top 10 Coverage Bundle` while only Wave 1.0+1.1 (16/64 tasks) had been pushed to origin. Wave 2.1+ (38 remaining tasks closing ML03/ML04/ML06/ML07/ML08) had been committed locally but not pushed.

**Recovery**: 10 unmerged commits cherry-picked onto fresh branch `232-build-closeout` (off `origin/main` post-PR #233 squash). PR #235 opened from new branch with title `feat(232): ML Top 10 build closeout — data-poisoning + model-theft + tests`. Wave 5 close-out (T054-T064) landed on `232-build-closeout` and squash-merged via PR #235.

**Outcome**: Both feat(232) commits aggregated cleanly into release-please PR #234 v4.25.0. **Branch recovery added ~1h overhead** to the actual envelope but did not delay the 2.5-day target. F-212 incident NOT invoked (release-please fired automatically).

**Lesson for F-7+**: Pre-merge checklist should explicitly verify all build-stage commits are pushed to origin before any squash-merge action. Suggested addition to `.claude/rules/git-workflow.md` Pre-merge Step 1: `git log origin/branch..HEAD` must return empty.

---

## 7. Definition of Done — All 16 Bullets Green

DoD checklist from spec.md §8 (FR-019 + FR-013 + SC-018 + SC-014 + SC-019 + SC-022 + SC-023 + SC-026):

1. ✅ Six §6 Coverage Matrix transitions (T054)
2. ✅ Each closed ML item has ≥1 citation-grounded Pattern Category with Primary Source / Indicators / Example / Mitigation blocks (T011-T032)
3. ✅ Regenerated `examples/predictive-ml-app/` surfaces ≥6 F-6 findings citing OWASP ML01/03/04/06/07/08:2023 (T042 — actual 9 findings emitted)
4. ✅ 6/6 baselines byte-identical under `SOURCE_DATE_EPOCH=1700000000` (T048 — verified at scale post-T042 regen)
5. ✅ Post-enrichment line counts within ADR-023 Decision 1 tier caps (STRIDE ≤120, AI ≤150, hard ≤180; T013/T021/T029 verification)
6. ✅ Public ADR-035 merged with Status: Accepted (T060 — squash SHA `e325375`)
7. ✅ Triad sign-off recorded on tasks.md (PM + Architect + Team-Lead — all 2026-04-27)
8. ✅ Schema invariant preserved (`finding.yaml` 1.8 unchanged — zero schema bump per ADR-035 D-6)
9. ✅ MAESTRO grep clean across all 6 host files (T013/T021/T029 grep -i 'maestro' returns 0)
10. ✅ Pattern Category Disambiguation present in all 3 companion catalogs (T013/T021/T029 + T038)
11. ✅ Zero MAESTRO references in target file footprints
12. ✅ Conventional Commit PR title gate passed (T056 — feat(232): prefix on both PR #233 and PR #235)
13. ✅ Release-please fired within ~30s of squash-merge (T058 — auto-updated 22s after PR #235 merge)
14. ✅ Test infrastructure additive update (T051 — DETECTION_AGENT_PATHS 10 → 8 + DETECTION_PATTERN_REF_ENRICHMENT_HOSTS 3 → 5)
15. ✅ 36 enrichment tests authored + green (T050 — `test_ml_top_10_coverage_bundle_enrichment.py`)
16. ✅ Delivery retrospective filed (this document — T059)

---

## 8. Deviations from PRD — None Material

- **Timeline**: 2.5-day envelope held (Day 1 + Day 2 + Day 3 multi-session). Branch recovery added ~1h overhead.
- **Scope**: Zero scope creep across 15 OoS items. R5 contingency NOT triggered (both deferral-pair items field-validated).
- **Quality gates**: Architect 0 BLOCKING / 0 HIGH / 0 MEDIUM at plan stage; code-reviewer 0 BLOCKING / 0 HIGH / 2 MEDIUM (no-action) / 3 LOW (advisory only) at T053; Wave 5.1 ADR-035 10/10 D-N PASS verification.
- **Documentation**: 1 discrepancy flagged (§5 above). Non-functional; resolved inline.

---

## 9. Outlook — F-7 Mobile Top 10 Coverage Bundle Next

F-6 establishes the three-agent enrichment-branch precedent. F-7 (Mobile Top 10:2024) is the next BLP-01 Tier 2 feature and may fan out across as many as 5 STRIDE agents at M8 cross-STRIDE Security Misconfiguration. The 5/5-dimension reduction should hold; per-host edit cost should remain linear (~2 file edits per host); audit-grade canonical mapping table should grow proportionally. Architect plan-day for F-7 should explicitly leverage F-6 as the precedent reference.

After F-7, BLP-01 reaches 10/11 features delivered. F-8 (Web/API Coverage Attestation) remains as the Tier 3 closeout pass.

---

**End of F-6 Delivery Retrospective**
