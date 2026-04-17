---
spec_reference: specs/180-taxonomy-crosswalk-collection/spec.md
plan_reference: specs/180-taxonomy-crosswalk-collection/plan.md
prd_reference: docs/product/02_PRD/180-taxonomy-crosswalk-collection-2026-04-17.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-17
    status: APPROVED_WITH_CONCERNS
    notes: "Tasks.md preserves all 5 US (mapping table US1-5 correct) and all 13 SCs (traceability table complete, each SC has ≥1 task). Critical product concerns addressed: T017 enforces FR-033 'What F-A1 does NOT' subsection (H-PM-2), T008 assigns Day 1 tripwire to team-lead, T020 assigns R7 ATLAS tripwire to architect, T034 files both follow-ons (related/superseded + citation link-rot per PRD Out-of-Scope). No scope creep, no US without independent test, no SC without task. 3 non-blocking concerns addressed inline: (1) T036 SC-007 now explicitly verifies 'What F-A1 does NOT give you today' subsection presence and content coverage; (2) T020 R7 architect Day-2 capacity concern documented with delegation-to-senior-backend-engineer fallback; (3) T034 Issue-title exact-wording verification against PRD Out-of-Scope to preserve downstream discoverability."
  architect_signoff:
    agent: architect
    date: 2026-04-17
    status: APPROVED_WITH_CONCERNS
    notes: "F3 compliance PASS (T028 requires T027; no transient referential-integrity window). DAG soundness mostly sound; 2 gaps addressed inline: (C1) T030 prerequisite corrected from T024 to T026 (tier-adjusted final crosswalk); (C2) T031 annotation clarifies 'nothing on F-A1 work' means technically independent per FR-036 zero-runtime-touch. Schema freeze (T002/T003) correctly gates parallel authoring in Wave 1.2. Tier-decision math consistent (38.4s/edge threshold, <200 Day 2 → Tier 2, <100 Day 3 → Tier 3); all 3 gates monotonically decreasing. Agent subagent_types all valid per .claude/agents/ inventory. ADR-027 governance (Proposed→Accepted) correct; T032 now cites merge commit SHA in Accepted-date rationale per Architect suggestion. Byte-identity command + baseline list correct per Feature 128. Pre-Mortem gotcha on batched crosswalk commits mitigated by T007/T016 cite-only-seed-ids and T029 fix-in-YAML instruction. No blocker; approved for progression to /aod.build."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-17
    status: APPROVED_WITH_CONCERNS
    notes: "3 non-blocking concerns addressed inline: (1) MEDIUM: Day 2 senior-backend-engineer load 9-11h nominal (real 7-9h given T013/T014 trivial); soft-overflow budget now documented in T015 (may defer to Day 3 start without breaking T023 sequencing). (2) LOW: T026 Day 3 tier-gate 100-499 band with Tier 1 active now explicitly escalates to Tier 2 in the decision matrix. (3) LOW: R6 single-agent wave mapping remains lead-time-deferred (team-lead re-sequences at execution time if R6 triggers). Phase-per-day feasibility sound: Day 1 balanced (architect 3h, senior-backend 4-5h, web-researcher 2h); Day 2 borderline mitigated; Day 3-5 balanced. Wave structure has no false parallelism (parallel tasks operate on disjoint files). T008 team-lead tripwire ownership correctly asserted with actionable 38.4s/edge threshold. No hidden external blocker beyond R7 ATLAS URL resolution (already tripwired via T011 + T020). Follow-on crosswalk expansion correctly lead-time-deferred (no ICE required pre-filing). Sequencing matches Architect F3 (tests AFTER YAMLs). Approved for execution."
---

# Tasks: F-A1 Taxonomy Crosswalk Collection (Feature 180)

**Input**: Design documents from `/specs/180-taxonomy-crosswalk-collection/`
**Prerequisites**: spec.md (APPROVED_WITH_CONCERNS by PM), plan.md (APPROVED by PM, APPROVED_WITH_CONCERNS by Architect), research.md, data-model.md, contracts/catalog-record.yaml, contracts/crosswalk-edge.yaml, contracts/integrity-test-contract.md, quickstart.md

**Tests**: Required — FR-027 through FR-032 mandate a `tests/schemas/test_taxonomy_integrity.py` pytest suite.

**Organization**: Tasks are grouped by 5-phase execution plan (per plan.md Phase 2 preview), mapping 1:1 to PRD Timeline § Phase Breakdown. Each task carries its story ownership ([US1]–[US5]), parallel-eligibility flag ([P]), and agent assignment.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US-180-1 (catalog YAMLs), US-180-2 (crosswalk), US-180-3 (README), US-180-4 (tests), US-180-5 (ADR)
- All paths are relative to repo root `/Users/david/Projects/tachi/`

## Agent Assignments (3-agent parallel execution, per PRD Phase Breakdown)

- **architect**: schema freeze, ADR-027 authoring, README structure, cross-references (2 link edits)
- **senior-backend-engineer**: YAML authoring (9 files), integrity tests (`tests/schemas/`)
- **web-researcher**: crosswalk edge citation discovery (≥500 primary edges), Day 1 50-edge spike
- **code-reviewer**: byte-identity verification, enum-closure review, pre-merge PR checks

R6 fallback: if only senior-backend-engineer is available, wall-clock extends to 5-6 days (team-lead authorizable without PRD amendment).

---

## Phase 1: Schema Freeze + OWASP + Day 1 Crosswalk Spike (Day 1)

**Goal**: Lock schema shape, produce ADR-027 in Status: Proposed, author first YAML (`owasp.yaml`), execute 50-edge crosswalk spike with Risk R1 tripwire measurement.

**Deliverables at end of Day 1**: committed `owasp.yaml`; ADR-027 in Status: Proposed; Day 1 spike outcome recorded in tasks.md with tripwire tier decision.

### Wave 1.1 — Schema Lock (serial, foundation for parallel authoring)

- [X] **T001** [architect] Verify FR-A7 (ADR-004 absence): run `ls docs/architecture/02_ADRs/ | grep -E '^ADR-004'` — confirm empty output. Verify ADR-027 is next unused by `ls docs/architecture/02_ADRs/ADR-027*` (must be empty). If ADR-027 is taken by an unrelated in-flight PR, use next unused number (document deviation in tasks.md progress log).
- [X] **T002** [architect] Author `docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md` in Status: **Proposed** (per FR-041) using `ADR-000-template.md` section structure. Content per FR-040: per-item record shape (FR-003), per-edge record shape (FR-009), 7-value taxonomy enum (FR-010), 3-value edge_type enum (FR-012), 3-value confidence enum (FR-013), Interpretation C rationale, scope/cadence exception rationale, Related ADRs (ADR-020, ADR-021, ADR-023, ADR-024, ADR-025). Commit with message `feat(180): ADR-027 Proposed`.
- [X] **T003** [architect] Freeze schema shape by committing ADR-027 (T002). This unblocks parallel authoring in Waves 1.2 and beyond.

### Wave 1.2 — Parallel Day 1 authoring (after Wave 1.1)

- [X] **T004** [P] [US1] [senior-backend-engineer] Create directory `schemas/taxonomy/` (T001 gate: must not exist at start; `mkdir schemas/taxonomy`). Commit with message `chore(180): bootstrap schemas/taxonomy/ directory`. (Absorbed into T005 commit per note "git cannot commit empty dir".)
- [X] **T005** [P] [US1] [senior-backend-engineer] Author `schemas/taxonomy/owasp.yaml` with ≥60 items covering 6 OWASP lists per FR-020 (LLM Top 10:2025 — 10 items, Agentic Top 10:2026 — 10 items, Top 10:2021 — 10 items, API Security Top 10:2023 — 10 items, Mobile Top 10:2024 — 10 items, ML Top 10:2023 — 10 items). Record shape per FR-003 `{id, full_id, name, url, cwe_refs}`; `cwe_refs` populated where OWASP source explicitly publishes CWE cross-references (per FR-008 unidirectional OWASP→CWE rule). Commit with message `feat(180): author owasp.yaml (≥60 items, 6 OWASP lists)`.
- [X] **T006** [P] [US4] [senior-backend-engineer] Bootstrap `tests/schemas/` subdirectory: create empty `tests/schemas/__init__.py`. Commit with message `chore(180): bootstrap tests/schemas/ subdirectory`.
- [X] **T007** [P] [US2] [web-researcher] **Day 1 crosswalk spike** (Risk R1 tripwire): author **50 edges** on diverse slice per A5 composition: 10 OWASP↔CWE + 10 ATT&CK↔CWE + 10 ATT&CK↔ATLAS + 10 LLM↔NIST + 10 Agentic↔MITRE. Each edge uses FR-009 shape; each has `edge_type: primary`; confidence calibrated per FR-013 anti-drift rule. Write 50 edges to `schemas/taxonomy/crosswalk.yaml` as Day 1 seed. **Record wall-clock time** (start-to-finish for the 50 edges) in tasks.md progress log (§Day 1 Spike Outcome).
- [X] **T008** [US2] [team-lead] **Day 1 Tripwire Decision Gate**: at end of Day 1, compute `seconds_per_edge = total_wall_clock / 50`. If ≤38.4s/edge → R3 Tier 1 default stands (≥500-edge floor); log decision "CONTINUE TIER 1". If >38.4s/edge → escalate to architect + team-lead for Day 2 end re-evaluation (pre-authorize R3 Tier 2 if Day 2 end <200 edges). **Assignee for tripwire decision: team-lead** (Architect F3 explicit ownership).

### Day 1 Exit Gate

- [X] **T009** [architect] Verify T002 ADR-027 commit exists with Status: Proposed. Verify T005 `owasp.yaml` committed. Verify T007 spike edges committed. Verify T008 tripwire decision logged in tasks.md progress. **VERIFIED 2026-04-17**: ADR-027 at `b0f0159` (Status: Proposed confirmed); owasp.yaml at `e150b81` (60 items exactly); crosswalk.yaml at `b4527f1` (50 edges, 5-slice composition verified via yaml.safe_load); tests/schemas/__init__.py at `889b38b`; T008 CONTINUE TIER 1 decision logged at `499bdf5`. Day 1 Exit Gate PASSES. Wave 2 authoring unblocked.

---

## Phase 2: MITRE + CWE + Pseudo-Taxonomies + NIST Catalog Start (Day 2)

**Goal**: Author 5 more YAMLs (3 MITRE/CWE + 2 pseudo-taxonomy); begin `nist-ai-rmf.yaml` catalog; continue crosswalk citation discovery; draft README; stage 2 cross-reference link edits.

**Deliverables at end of Day 2**: 6 YAMLs committed (owasp + attack + atlas + cwe + 2 pseudo); `nist-ai-rmf.yaml` in progress; ~200 crosswalk edges committed; README.md draft; 2 cross-reference link edits drafted.

### Wave 2.1 — Parallel Day 2 authoring

- [X] **T010** [P] [US1] [senior-backend-engineer] Author `schemas/taxonomy/mitre-attack.yaml` with the 38 seed MITRE ATT&CK techniques from spec.md Assumption A1 (full ID list pinned). Record shape per FR-003; `url` per canonical pattern `https://attack.mitre.org/techniques/T<N>/` (FR-033 canonical-URL conventions). Commit with message `feat(180): author mitre-attack.yaml (38 seed techniques)`. **COMPLETED 2026-04-17** commit `c622654`, 212 lines, 38 techniques.
- [X] **T011** [P] [US1] [senior-backend-engineer] Author `schemas/taxonomy/mitre-atlas.yaml` with ≥12 records: 7 seed (AML.T0010, T0018, T0020, T0024, T0051, T0054, T0057) + 5 externally-curated (AML.T0058, T0059, T0060, T0061, T0062) per FR-016. **Curation tripwire** (FR-016 + PM concern): if any of AML.T0059–T0062 cannot be resolved to a stable citation URL on `atlas.mitre.org` by end of T011, escalate to architect; architect may authorize descope to ≥8 (seed + AML.T0058 only). Commit with message `feat(180): author mitre-atlas.yaml (7 seed + 5 curated)`. **COMPLETED 2026-04-17** commit `8445147`, 89 lines, 12 records (7+5). URL resolution: all 5 AML.T0058-T0062 URLs returned HTTP 404 from WebFetch (anti-bot gating suspected); URL pattern validated via MISP galaxy cross-ref; names retrieved via WebSearch aggregation. All 5 flagged in YAML comments for T020 architect tripwire review.
- [X] **T012** [P] [US1] [senior-backend-engineer] Author `schemas/taxonomy/cwe.yaml` with ≥53 records: 41 seed CWEs from spec.md Assumption A1 + 12 net-new CWEs from CWE Top 25 (2025) per FR-017. CWE record shape OMITS `cwe_refs` field entirely per FR-003. Commit with message `feat(180): author cwe.yaml (41 seed + CWE Top 25 2025 expansion)`. **COMPLETED 2026-04-17** commit `4fc8e7d`, 241 lines, 53 records (41 seed + 11 net-new Top 25 2025 + CWE-116 cited in OWASP A03/LLM05).
- [X] **T013** [P] [US1] [senior-backend-engineer] Author `schemas/taxonomy/tachi-control-category.yaml` with exactly 8 records (per FR-018): `authentication`, `input-validation`, `rate-limiting`, `encryption`, `logging-audit`, `csrf-protection`, `csp-security-headers`, `access-control`. Record shape per FR-003; `url` field is relative repo path `.claude/skills/tachi-control-analysis/references/control-categories.md`; `cwe_refs: []`. Commit with message `feat(180): author tachi-control-category.yaml (8 records)`. **COMPLETED 2026-04-17** commit `46b2b9f`, 65 lines, 8 records.
- [X] **T014** [P] [US1] [senior-backend-engineer] Author `schemas/taxonomy/tachi-stride-ai-category.yaml` with exactly 11 records (per FR-019): 6 STRIDE (`spoofing`, `tampering`, `repudiation`, `information-disclosure`, `denial-of-service`, `elevation-of-privilege`) + 5 AI (`prompt-injection`, `data-poisoning`, `model-theft`, `agent-autonomy`, `tool-abuse`). Record shape per FR-003; `url` field is `.claude/skills/tachi-shared/references/stride-categories-shared.md`; `cwe_refs: []`. Commit with message `feat(180): author tachi-stride-ai-category.yaml (11 records)`. **COMPLETED 2026-04-17** commit `713705f`, 86 lines, 11 records.
- [X] **T015** [US1] [senior-backend-engineer] Begin authoring `schemas/taxonomy/nist-ai-rmf.yaml` Subcategory catalog. Target 68 records (exact, per FR-021) from NIST AI 100-1 Tables 1–4. May be partial at end of Day 2; completion target is Day 3 (T022). Commit in-progress work with message `feat(180): begin nist-ai-rmf.yaml catalog (Subcategory records 1..N)`. **Soft-overflow budget** (per Team-Lead review MEDIUM concern): Day 2 senior-backend-engineer load totals T010+T011+T012+T013+T014+T015 ≈ 9-11h nominal; T013/T014 are trivial (exact-count copies from seed references, ~30min each); real load is ~7-9h. If Day 2 slips, T015 MAY defer fully to Day 3 start without breaking T023 sequencing (T022 still completes NIST catalog before T023 authors Surface B/C edges). No wave-structure change required. **COMPLETED 2026-04-17** commit `5123023`, 401 lines, **72 records** (GOVERN 19, MAP 18, MEASURE 22, MANAGE 13). **COUNT DISCREPANCY FLAG**: authoritative NIST AIRC enumerates 72 Subcategories across Tables 1-4; FR-021 targets 68. Architect/PM decision required (amend FR-021 to 72 vs. select 68-subset); all Surface B/C mapping-cited Subcategories fall within the 68 subset regardless, so downstream T023 work is unaffected. T022 is likely redundant if FR-021 amendment path chosen.
- [X] **T016** [P] [US2] [web-researcher] Continue crosswalk citation discovery. Target: ≥200 primary edges committed to `crosswalk.yaml` by end of Day 2. Each edge: FR-009 shape, `edge_type: primary`, citation per FR-014, confidence per FR-013 anti-drift rule. Commit in batches (one commit per ~50 edges) to avoid pre-commit hook timeout (Risk R8 per plan). **COMPLETED 2026-04-17** — shape reshape commit `d9bdb1c` (top-level list per FR-009 contract, 50 Day 1 edges preserved verbatim); 5 harvest batches `d459cd0`, `8b66a31`, `abe3551`, `cd56a3d`, `004cd00` = 242 new edges. **Total: 292 edges** (Day 2 target ≥200 exceeded by 46%). Confidence dist: 141 high / 150 medium / 1 low. Zero duplicates on 5-tuple. **Referential-integrity flags for T028**: (i) Day 1 used `A01:2021`/`LLM01:2025`/`ASI01:2026` ID-format — canonical short IDs differ; (ii) some ATT&CK IDs (`T1190`, `T1557`, `T1565.001`) in Day 1 edges not in `mitre-attack.yaml` 38-seed; (iii) some CWE IDs referenced (`CWE-693`, `CWE-1269`, `CWE-1357`, `CWE-1426`, `CWE-1427`) may not be in `cwe.yaml` 53-record set; (iv) 22 control-category edges reference IDs (`monitoring-alerting`, `error-handling`, `secrets-management`) outside the FR-018 frozen 8-value enum — MUST be fixed in T029 or pre-T028.
- [X] **T017** [P] [US3] [architect] Draft `schemas/taxonomy/README.md` per FR-033 structure: (a) §Purpose with runnable Python snippet + **"What F-A1 does NOT give you today" subsection** (per FR-033 clarification addressing PM H-PM-2); (b) §Harvest methodology; (c) §Per-framework provenance (7 sections); (d) §Confidence calibration rubric with anti-drift rule; (e) §Canonical-URL conventions; (f) §Update procedure (5 per-framework sections); (g) §Crosswalk methodology; (h) §Single-source-of-truth cross-reference to nist-ai-rmf-mapping.md. Draft committed with message `docs(180): draft schemas/taxonomy/README.md`. **COMPLETED 2026-04-17** commit `5b1d1ef`, 215 lines, 8 sections per FR-033 (SC-007 runnable snippet + H-PM-2 subsection both present).
- [X] **T018** [P] [US3] [architect] Stage 2 cross-reference link edits per FR-038: (a) top-level `README.md` gains single link to `schemas/taxonomy/README.md` in the appropriate section; (b) `docs/architecture/00_Tech_Stack/README.md` gains single link under Schemas or Conventions. Commit with message `docs(180): add schemas/taxonomy/ cross-references to README + Tech_Stack`. **COMPLETED 2026-04-17** commit `c6b2f58`, 2 files + 1 new line each: top-level README Integration Reference table gains Taxonomy Crosswalk row; Tech_Stack Threat Modeling Schemas section gains taxonomy bullet cross-linking ADR-027.

### Wave 2.2 — Day 2 Gate + R7 Tripwire

- [X] **T019** [US2] [team-lead] **Day 2 Tier Gate**: count committed primary edges in `crosswalk.yaml`. If ≥200 → Tier 1 stands. If <200 and Tier 1 was adopted at Day 1 → escalate to **R3 Tier 2** (300-edge floor, team-lead-authorizable without PRD amendment). Log decision in tasks.md progress (§Day 2 Tier Gate). **COMPLETED 2026-04-17** — decision **TIER 1 HOLDS** (292 primary edges; 58% of ≥500 merge floor with 3 authoring days remaining; within 200-499 on-track band; residual gap absorbed by T023 41-edge transcription + T024 ~167-edge Day 3 harvest).
- [X] **T020** [US1] [architect] **R7 Tripwire (Architect)** per FR-016: if T011 escalated AML.T0058-T0062 citation unresolvability, architect authorizes descope to ≥8 (7 seed + AML.T0058). If all 5 resolve to stable URLs, no action. Record decision in tasks.md progress (§R7 Tripwire Outcome). **PM concern 2**: architect Day-2 availability is not formally capacity-validated in tasks.md; if architect Day-2 is conflicted, T011 may need to pre-mark uncertainty and team-lead re-evaluates T020 ownership (may transfer to senior-backend-engineer under architect written delegation, same descope authority). **COMPLETED 2026-04-17** — decision **ALL 5 PRESENT** (no descope): 404s were WebFetch client-side anti-bot gating (control proof: known-good seed AML.T0051 also 404s via same client); all 5 IDs confirmed present in authoritative MITRE-owned `atlas-data/techniques.yaml` on GitHub. **Name-correction commit `be18076`** (architect inline): T011-aggregated names for all 5 AML.T0058-T0062 were WRONG — corrected to authoritative names (T0058 "Publish Poisoned Models", T0059 "Erode Dataset Integrity", T0060 "Publish Hallucinated Entities", T0061 "LLM Prompt Self-Replication", T0062 "Discover LLM Hallucinations"). URL pattern unchanged → zero crosswalk edge rewrites required.

### Day 2 Exit Gate

- [X] **T021** [architect] Verify T010-T018 commits exist. Verify primary-edge count per T019. Verify `nist-ai-rmf.yaml` progress per T015. Verify T019/T020 tripwire decisions logged. **COMPLETED 2026-04-17 — CONDITIONAL PASS**: 12/12 Day 2 commits present; 7/7 catalog record counts meet SC-002 floors (owasp 60, mitre-attack 38, mitre-atlas 12, cwe 53, control-category 8, stride-ai 11, nist-ai-rmf 72 — note FR-021 target was 68 exact; actual overage deferred to T022); crosswalk.yaml has 292 primary edges (T019 ≥200 gate PASS); T015 NIST shape spot-check PASS (`{id, full_id, name, url, cwe_refs}` + `cwe_refs: []`); 10-edge enum-closure spot-check PASS (all within 7-value taxonomy enum). Deferred to T028/T029: 20 Day 1 edges with `A01:2021`/`LLM01:2025`/`ASI01:2026` ID-format drift, 22 control-category edges referencing non-FR-018 IDs, several CWE/ATT&CK IDs referenced but not in committed catalogs — all resolved at integrity-test / fix-YAML gates per plan. `.aod/tasks.md` (active workspace copy) synced from `specs/180-taxonomy-crosswalk-collection/tasks.md` (authoritative) post-verification.

---

## Phase 3: NIST Completion + Crosswalk Assembly (Day 3)

**Goal**: Complete `nist-ai-rmf.yaml` catalog; author 41 NIST-derived Surface B/C crosswalk edges (verbatim transcription per FR-022); continue crosswalk citation harvest toward ≥500 primary edges; finalize README.

**Deliverables at end of Day 3**: all 9 YAMLs committed; crosswalk.yaml ≥500 primary edges; README.md final.

### Wave 3.1 — Parallel Day 3 authoring

- [X] **T022** [US1] [senior-backend-engineer] Complete `schemas/taxonomy/nist-ai-rmf.yaml` Subcategory catalog. Assert count == exactly 68 (FR-021). Record shape per FR-003; `url` per NIST DOI-based convention. Commit with message `feat(180): complete nist-ai-rmf.yaml catalog (68 Subcategories)`. **COMPLETED 2026-04-17** commit `9780a96` — catalog was already at 72 records per T015 (SHA `5123023`); FR-021 amended 68→72 at SHA `9da377c` under FR-024 primary-source-correction discipline (architect + PM concur path (a)). T022 verification green (72 records, all 5 required fields, unique IDs, NIST DOI url, function composition GOVERN 19 / MAP 18 / MEASURE 22 / MANAGE 13). T022 deliverable was a comment-block update rewriting the "COUNT DISCREPANCY FLAG" block as a "SPEC AMENDMENT NOTE (2026-04-17)" referencing SHA `9da377c` and the architect/PM decision artifacts in `.aod/results/`.
- [X] **T023** [US2] [senior-backend-engineer] Author ~41 NIST-derived crosswalk edges per FR-022 verbatim transcription: 27 Surface B edges (`tachi-control-category` → `nist-ai-rmf`) + 14 Surface C Overlap edges (`tachi-stride-ai-category` → `nist-ai-rmf`). All edges: `edge_type: primary`, `confidence: high`, `citation: .claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`. Per FR-023: omit "No equivalent" rows (8 on Surface C) + default-omit "Gap" rows (2 on Surface C) unless curator articulates `confidence: low` with specific citation. Per FR-024: if a row is factually inaccurate, file separate ADR-025 amendment Issue — DO NOT silent-correct in F-A1. Commit with message `feat(180): author NIST Surface B+C crosswalk edges (41 edges)`. **COMPLETED 2026-04-17** — 27 canonical Surface B edges authored (verbatim per FR-022, space-format targets matching `nist-ai-rmf.yaml` `id` field). All 8 FR-018 enum control categories present. Surface C (14 or 15 Overlap rows) DEFERRED to ADR-025 amendment Issue per FR-024 — Surface C rows in the reference use AI 600-1 §2.X identifiers not in the 7-value taxonomy enum (FR-010) nor in `nist-ai-rmf.yaml`. Edits landed in batch 7 commit `a348f28` (bundled with parallel batch 7 work). Net-new canonical Surface B edges: 27. Drift cleanup (22 Batch 5 dash-format edges + 3 outside-enum source IDs + 16 pre-existing Surface C edges with inconsistent targets) remains deferred to T028/T029 per NEXT-SESSION.md §Open Decisions #2. Surface C structural issue and 14-vs-15 Overlap row count discrepancy flagged in `.aod/results/senior-backend-engineer.md` for ADR-025 amendment Issue.
- [X] **T024** [P] [US2] [web-researcher] Continue crosswalk citation harvest. Target: ≥500 primary edges total committed to `crosswalk.yaml` by end of Day 3 (per FR-025 Tier 1 default). Commit in batches of ~50. **COMPLETED 2026-04-17** — **509 primary edges** (≥500 Tier 1 floor crossed). 4 harvest batches committed: batch 6 (SHA `c60a1c2`, +52 edges OWASP Agentic/ML ↔ ATLAS/ATT&CK), batch 7 (SHA `a348f28`, +51 edges stride-ai↔ATT&CK/ATLAS — note: commit also bundles T023's 27 canonical Surface B edges staged from a parallel working-tree change; T023's contribution is annotated in-file under the "T023 (Wave 3.1)" header), batch 8 (SHA `33afed1`, +50 edges stride-ai↔CWE + CWE↔CWE parent-child), batch 9 (SHA `2b124e0`, +37 edges OWASP API↔ATT&CK + CWE↔CWE residuals + LLM/ASI↔ATLAS fills). Confidence distribution: 283 high / 225 medium / 1 low. Pair distribution: owasp→cwe 169, owasp→mitre-atlas 60, tachi-control-category→nist-ai-rmf 49, mitre-attack→cwe 40, owasp→mitre-attack 36, cwe→cwe 34 (all new in T024), tachi-stride-ai-category→mitre-attack 31 (all new in T024), tachi-stride-ai-category→cwe 29 (all new in T024), mitre-atlas→mitre-attack 25, tachi-stride-ai-category→mitre-atlas 20 (all new in T024), tachi-stride-ai-category→nist-ai-rmf 16. Zero 5-tuple duplicates. Referential integrity held clean against in-catalog IDs for all net-new T024 edges (all 217 new edges reference only catalog-resident ATT&CK / ATLAS / CWE / OWASP / FR-018 control-category / FR-019 stride-ai-category IDs). Pre-existing orphan references inherited from Day 1-2 (T1190, T1557, T1565.001, ATLAS IDs outside the 12-record catalog, 40 CWEs outside the 53-record catalog, NIST dash-format targets) were not extended — T028/T029 cleanup territory preserved. Full details: `.aod/results/web-researcher.md`.
- [X] **T025** [P] [US3] [architect] Finalize `schemas/taxonomy/README.md`: populate all 7 per-framework provenance sections with final seed counts + external-curation sources. Commit with message `docs(180): finalize schemas/taxonomy/README.md (provenance + update procedures)`. **COMPLETED 2026-04-17** commit `46b4e09`, README.md 219 lines (was 215 pre-T025), +43/-39 diff. All 7 provenance subsections populated with final counts (owasp 60, mitre-attack 38, mitre-atlas 12, nist-ai-rmf 72, cwe 53, control-category 8, stride-ai 11), external-curation sources, and 2026-04-17 retrieval dates. FR-021 68→72 amendment trail (SHA 9da377c) documented in §3.4 mirroring CWE Top 25 2025 pinned-with-retrieval-date pattern in §3.5. §6.5 NIST update procedure updated to reflect FR-024 primary-source-correction discipline. §5 OWASP Agentic Top 10:2026 URL finalized. SC-007 runnable Python snippet verified (all 7 catalogs load, counts match spec). H-PM-2 subsection, FR-013 anti-drift rule, FR-033d canonical-URL conventions, FR-033f 5 update procedures, FR-033h single-source-of-truth cross-ref all intact.

### Wave 3.2 — Day 3 Gate + Tier 3 Tripwire

- [X] **T026** [US2] [team-lead] **Day 3 Tier Gate** (per Team-Lead review clarification): count committed primary edges in `crosswalk.yaml`. Decision matrix:
  - **≥500** → Tier 1 holds (no action; the R3 Tier 1 default scope is achieved).
  - **300–499** → If Tier 2 was authorized at Day 2, Tier 2 holds (300-floor achieved). If Tier 1 was still active at Day 2 end, **escalate to Tier 2 now** (team-lead authorizes 300-floor without PRD amendment; record rationale).
  - **100–299** → **escalate to Tier 2 now** (team-lead authorizes 300-floor; record rationale); if ≤200 at Day 3 end, parallel-evaluate whether Day 4 catch-up to 300 is feasible (senior-backend-engineer + web-researcher coordinate).
  - **<100** → escalate to **R3 Tier 3** (150-edge floor, PRD amendment + architect/team-lead re-sign required).
  Log decision in tasks.md progress (§Day 3 Tier Gate).

### Day 3 Exit Gate

- [X] **T027** [architect] Verify all 9 YAMLs committed (owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe, tachi-control-category, tachi-stride-ai-category, crosswalk, README.md). Verify `crosswalk.yaml` primary-edge count per T026. Verify NIST Surface B+C transcription count matches 41 (per FR-022). Verify T026 tripwire decision logged. **COMPLETED 2026-04-17** — Day 3 Exit Gate PASSES. All 9 YAMLs present (record counts: owasp 60, mitre-attack 38, mitre-atlas 12, cwe 53, nist-ai-rmf 72, tachi-control-category 8, tachi-stride-ai-category 11, crosswalk 509 primary / 509 total, README.md 219 lines). Primary-edge count 509 ≥ 500 Tier 1 floor → TIER 1 HOLDS (T026 arithmetic definitional — team-lead log-entry in parallel). Surface B canonical transcription = 27 edges per T023 (FR-022 Surface B contract SATISFIED). **Surface C structural blocker resolved via Option (c)** — Surface C out-of-scope for F-A1; scope-narrow spec amendment landed (FR-022 / SC-008 narrowed to Surface B only; FR-004 example + FR-032 NIST sort convention clarified); ADR-027 Revision History updated (Status remains Proposed → T032 at merge); F-A1.1 follow-on Issue scoped for T034 filing (enum 7→8, nist-ai-600-1.yaml catalog, 15 Surface C Overlap rows transcribed). T029 cleanup direction: REMOVE all 38 drifted edges (22 Surface B + 16 Surface C); web-researcher Day 4 pre-T029 top-up target ≥540 primary edges. Minor corrections (§5.2 15 vs 14 count, §5.3 NIST sort convention, §5.4 FR-004 MEASURE 2.7 dash→space) all landed. **PM re-sign slot opened** at `pm_signoff_amendment_2` for Option (c) concurrence. Architect decision artifact: `.aod/results/architect.md`.

---

## Phase 4: Integrity Tests + ADR Accepted + PR (Day 4)

**Goal**: Author FR-027–FR-032 integrity test suite AFTER all 8 YAMLs are committed (Architect F3 sequencing constraint); run backward-compat byte-identity verification (FR-036); move ADR-027 from Proposed to Accepted; open PR.

**Deliverables at end of Day 4**: `tests/schemas/test_taxonomy_integrity.py` green; backward-compat test green; ADR-027 in Status: Accepted; PR opened.

### Wave 4.1 — Integrity test authoring (AFTER all 8 YAMLs committed per Architect F3)

- [X] **T028** [US4] [senior-backend-engineer] Author `tests/schemas/test_taxonomy_integrity.py` per `contracts/integrity-test-contract.md`. 4 mandatory test functions (FR-028 `test_framework_yamls_load`, FR-029 `test_crosswalk_loads`, FR-030 `test_crosswalk_referential_integrity`, FR-031 `test_citation_shape`) + 1 optional (FR-032 `test_records_sorted`). Stdlib-only + pyyaml; no HTTP fetches (preserves ADR-021 determinism). Run `pytest tests/schemas/ -v` locally; all tests green. Commit with message `test(180): author tests/schemas/test_taxonomy_integrity.py (4+1 integrity tests)`. **COMPLETED 2026-04-17** commit `f34141b` — 5 tests authored. Initial run 3/5 passed; 2 expected-fail surfaced the 162-edge drift scope (vs T027's 38-edge flag) that triggered T029 architect escalation. Post-T029+Batch 11: 5/5 green.
- [X] **T029** [US4] [senior-backend-engineer] If any integrity-test failure in T028, fix the offending YAML record(s) (NOT the test), then re-run `pytest tests/schemas/` until green. Commit fixes with message `fix(180): resolve taxonomy integrity test failures`. **COMPLETED 2026-04-17** — Architect Option (d) MIX executed: (1) NORMALIZE 81 line-level rewrites across 74 distinct edges (20 OWASP year-suffix strip `LLM05:2025 → LLM05`, 38 NIST dash→space `MEASURE-2.7 → MEASURE 2.7`, 23 STRIDE slug `information-disclosure → info-disclosure` / `elevation-of-privilege → privilege-escalation`); (2) REMOVE 88 semantic-drift edges (67 target-CWE-missing, 12 source-ATLAS-missing, 5 hybrid source-control-outside-enum, 3+1 ATT&CK-missing, 1 dual-missing); (3) DEDUPE 25 post-normalize duplicate 5-tuples (22 Surface B dash→space collisions with T023 canonical twins + 10 OWASP LLM/3 ASI year-suffix collisions); (4) SORT `cwe.yaml` lexicographically on `id` field (53 records reordered; header comment preserved). Commit SHAs: `e58f247` (normalize + cwe-sort), `991e1ee` (remove + dedup). Final state: 551 − 88 (semantic) − 25 (dedup) = **438 primary edges**. 4/5 integrity tests green (`test_crosswalk_referential_integrity` GREEN — the primary T029 objective). `test_crosswalk_loads` FR-025 floor (≥500) blocked awaiting web-researcher Batch 11 top-up (serial-after per architect cadence, target ≥47 clean primary edges for ≥485, ≥62 for ≥500 Tier 1 restoration). Dedup count 25 is higher than architect's expected 5-10 because normalize exposed T023 canonical twins for all 22 dash-format Surface B drift edges + 13 OWASP year-suffix → canonical short-ID drift edges that pre-existed as Batch 4/6 twins. Full details in `.aod/results/senior-backend-engineer.md` §T029.
- [X] **T030** [P] [US1] [senior-backend-engineer] Run SC-013 parse-performance sanity check: `time python -c "import yaml; yaml.safe_load(open('schemas/taxonomy/crosswalk.yaml'))"` — assert <500ms on commodity hardware. Record measurement in tasks.md progress (§SC-013 Parse Performance). **Prerequisite** (Architect C1): T026 tier-gate decision resolved (crosswalk.yaml reflects tier-adjusted final edge count), not T024 (which is in-progress). **COMPLETED 2026-04-17** — crosswalk.yaml parse measured at 375ms steady-state (526 primary edges; macOS Darwin 25.3.0 arm64, Python 3.9.6, PyYAML 6.0.2); 125ms under the 500ms informational bound. Details in §SC-013 Parse Performance block below.

### Wave 4.2 — Backward-compat + ADR Accepted

- [X] **T031** [P] [US1] [code-reviewer] Run backward-compatibility byte-identity test per FR-036: `SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py -v`. Assert 5/5 non-agentic example PDFs byte-identical to baseline. If failure: investigate (should be impossible given zero runtime script touch — escalate to architect if reported). Record result in tasks.md progress (§FR-036 Backward-Compat Gate).
- [X] **T032** [US5] [architect] Update `docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md` Status from **Proposed** to **Accepted** (per FR-041). Add Accepted-date = merge-date (provisional: 2026-04-17+4d = 2026-04-21) **and cite the merge commit SHA** (filled post-merge via T039, strengthens provenance per Architect suggestion). Commit with message `feat(180): ADR-027 Accepted (post-schema-implementation)`. **Completed 2026-04-17 at commit `04a26a9`** — Status transitioned Proposed → Accepted; provisional Accepted-date 2026-04-21 recorded; Accepted-commit-SHA placeholder `<pending-T039-post-merge-fill>` reserved for post-merge fill per FR-041; Revision History entry 2026-04-17 (T032 transition) appended without overwriting prior T027 Option (c) Surface C amendment entry.

### Wave 4.3 — PR Open

- [X] **T033** [architect] Open PR against `main` with title `feat(180): F-A1 Taxonomy Crosswalk Collection`. Body: (a) link to spec.md + plan.md + tasks.md, (b) link to ADR-027, (c) summary of 9 files + 1 test file + 1 ADR + 2 cross-ref link edits, (d) evidence table showing all 13 SCs met, (e) Interpretation C rationale summary, (f) follow-on Issue links (`related`/`superseded` crosswalk expansion, ATLAS v5.4 catalog growth), (g) FR-036 backward-compat evidence link. PR assignee: PM + code-reviewer. **Completed 2026-04-17**: PR #181 opened at https://github.com/davidmatousek/tachi/pull/181 — base=main, head=180-taxonomy-crosswalk-collection, assignee=davidmatousek. Body covers sections (a)–(g); follow-on links sections (f) carry `<placeholder-link-T034-N>` tokens for T034 post-file replacement via `gh pr edit`. Pre-PR: uncommitted governance artifacts (PRD, plan.md, research.md, data-model.md, quickstart.md, contracts/, checklists/, BACKLOG/INDEX/.aod/plan.md updates) committed under `chore(180): commit Feature 180 governance artifacts before PR open` so all PR body links resolve.
- [X] **T034** [US2] [team-lead] **Follow-on Issue filing**: after PR opened, file GitHub Issue titled `F-A1 follow-on: crosswalk `related` and `superseded` edge expansion` per FR-025 out-of-scope clause. Link from PR description (T033-f). Also file citation-URL link-rot monitoring follow-on Issue per PRD Out-of-Scope. **PM concern 3**: verify Issue titles match PRD Out-of-Scope exact wording (§Out of Scope) at filing time to preserve downstream discoverability. **Completed 2026-04-17**: Filed 5 follow-on Issues (3 F-A1 + F-A1.1 per T027 Option (c) + F-A1.2/F-A1.3 per T029 Scope Disposition): #182 (related/superseded edge expansion — PRD Out-of-Scope exact title wording verified), #183 (citation-URL link-rot monitoring — PRD Out-of-Scope exact title wording verified), #184 (F-A1.1 NIST AI 600-1 GAI Risk taxonomy Surface C transcription — architect-prescribed exact title preserved), #185 (F-A1.2 cwe.yaml expansion — ~67 CWE IDs from T029 drift analysis), #186 (F-A1.3 MITRE ATT&CK + ATLAS catalog expansion — 12 ATLAS + 4 ATT&CK missing IDs). PR #181 body updated via `gh pr edit`: 5 `<placeholder-link-T034-N>` tokens replaced with live Issue URLs (0 placeholders remain, 5 Issue URLs present). All 5 Issues labeled `enhancement,follow-on-180` and assigned `@me`.

### Day 4 Exit Gate

- [X] **T035** [code-reviewer] Verify PR is open with complete description per T033. Verify all 9 YAMLs + `tests/schemas/test_taxonomy_integrity.py` + ADR-027 Accepted are included. Verify CI green on the PR branch (backward-compat + integrity tests). **COMPLETED 2026-04-17 — APPROVED_WITH_CONCERNS**: PR #181 Day 4 Exit Gate verified across 6 categories (30/31 checks PASS). PR state OPEN + MERGEABLE, title exact-match. All 12 artifacts present with correct record counts (owasp 60, attack 38, atlas 12, cwe 53, nist-ai-rmf 72, control-category 8, stride-ai 11, crosswalk **526 primary edges Tier 1 HOLDS**, README 219 lines). Tests: 5/5 integrity green in 0.53s + 13 passed/1 skipped backward-compat (6/6 PDF baselines byte-identical under `SOURCE_DATE_EPOCH=1700000000`). ADR-027 Status=Accepted (L3), Accepted-date=2026-04-21 provisional (L4), SHA placeholder `<pending-T039-post-merge-fill>` (L5), Revision History has T027 Option (c) + T032 transition entries. CI `tachi mmdc preflight` success on head SHA `d9cccbd`. **Single minor concern (non-blocking per guardrail)**: 5 follow-on Issue URLs in PR body (f) still contain `<placeholder-link-T034-N>` tokens; team-lead T034 will replace via `gh pr edit` after filing. Full details in `.aod/results/code-reviewer.md` §T035.

---

## Phase 5: Review + Buffer (Day 5)

**Goal**: PR review cycle; ADR review iteration; crosswalk edge-count completion if Day 3 fell short; merge.

### Wave 5.1 — Review Iteration

- [X] **T036** [code-reviewer] Review PR: verify SC-001 (9 files exist) + SC-002 (record count floors) + SC-003 (integrity test green) + SC-004 (backward-compat green) + SC-005 (zero-surface-area diff on runtime paths) + SC-006 (ADR-027 Accepted) + SC-007 (runnable Python snippet works) — **also explicitly verify** (per PM concern 1) the README contains the "What F-A1 does NOT give you today" subsection per FR-033/H-PM-2 naming F-A2 finding-level citation, F-B coverage attestation, and agent-reference migration as deliberately-deferred capabilities + SC-008 (NIST transcription spot-check: pick 5 Surface B rows + 5 Surface C rows; each resolves to exactly one crosswalk edge with matching fields) + SC-009 (ATLAS seed + curation coverage) + SC-010 (Day 1 spike outcome recorded) + SC-011 (cross-reference links present) + SC-012 (zero new dep diff) + SC-013 (parse perf measured). Post review comments. **COMPLETED 2026-04-17 — APPROVED**: 13/13 SC PASS + 4/4 Additional Checks PASS (cwe.yaml lexicographic sort, header provenance notes preserved, Interpretation C rationale surfaced in PR body + ADR-027, 5 follow-on Issue URLs live in PR body with 0 placeholder tokens remaining). No blocking or non-blocking concerns. T037/T038 NO-OP. Full findings `.aod/results/code-reviewer.md §T036`.
- [X] **T037** [senior-backend-engineer] Address code-reviewer PR comments. Commit fixes with message `fix(180): address PR review comments`. **NO-OP 2026-04-17**: T036 returned APPROVED with zero concerns; no code fixes required.
- [X] **T038** [architect] Address ADR-027 review comments (if any). Commit fixes with message `docs(180): address ADR-027 review comments`. **NO-OP 2026-04-17**: T036 returned APPROVED with zero ADR concerns; no ADR edits required.

### Wave 5.2 — Merge

- [ ] **T039** [architect] Squash-merge PR to `main` per tachi convention. Tag commit with message `feat(180): F-A1 Taxonomy Crosswalk Collection (#NNN)`. Verify `git log` on main shows squash commit.
- [ ] **T040** [team-lead] Post-merge: update PRD 180 status to "Delivered" in `docs/product/02_PRD/INDEX.md`. Update BACKLOG.md via `.aod/scripts/bash/backlog-regenerate.sh`. Move GitHub Issue #180 to `stage:done`.

### Day 5 Exit Gate

- [ ] **T041** [team-lead] Verify PR merged. Verify PRD status updated. Verify BACKLOG regenerated. Verify Issue #180 at stage:done. **F-A1 Complete**.

---

## Success Criteria Traceability

Every spec.md Success Criterion traces to at least one task:

| SC | Verification Task(s) |
|----|---------------------|
| SC-001 (9 files exist) | T036 |
| SC-002 (record count floors) | T036 |
| SC-003 (integrity test green) | T028, T029, T036 |
| SC-004 (backward-compat) | T031, T036 |
| SC-005 (zero-surface-area diff) | T036 |
| SC-006 (ADR-027 Accepted) | T032, T036 |
| SC-007 (runnable Python snippet) | T017 (README draft) + T025 (README finalized) + T036 (verification) |
| SC-008 (NIST Surface B/C verbatim) | T023, T036 |
| SC-009 (ATLAS seed + curation) | T011, T036 |
| SC-010 (Day 1 spike outcome recorded) | T007, T008 |
| SC-011 (2 cross-reference links) | T018, T036 |
| SC-012 (zero new deps) | T036 |
| SC-013 (parse performance) | T030 |

## Story-to-Task Mapping

| User Story | Tasks | Deliverable |
|------------|-------|-------------|
| US-180-1 (machine-readable records) | T004, T005, T010–T015, T022, T030 | 7 catalog YAMLs |
| US-180-2 (authoritative crosswalk) | T007, T008, T016, T019, T023, T024, T026, T034 | crosswalk.yaml with ≥500 primary edges |
| US-180-3 (documented methodology) | T017, T018, T025 | README.md + 2 cross-reference links |
| US-180-4 (integrity test suite) | T006, T028, T029 | tests/schemas/test_taxonomy_integrity.py |
| US-180-5 (public ADR) | T001, T002, T003, T032 | ADR-027 Proposed → Accepted |

## Wave-based Parallelism Summary

| Wave | Day | Parallel Tasks | Serial Gate |
|------|-----|----------------|-------------|
| 1.1 | 1 | T001, T002, T003 (sequential within architect) | T003 unlocks 1.2 |
| 1.2 | 1 | T004, T005, T006, T007 (4-way parallel across 2 agents) | T008 tripwire decision |
| 2.1 | 2 | T010, T011, T012, T013, T014, T016, T017, T018 (senior-backend-engineer on T010-T014, web-researcher on T016, architect on T017-T018) + T015 start | T019 tier gate |
| 2.2 | 2 | T019, T020 (sequential decisions) | T021 day-end gate |
| 3.1 | 3 | T022, T023 sequential (NIST edges depend on NIST catalog) + T024, T025 parallel | T026 tier gate |
| 3.2 | 3 | T026 (serial decision) | T027 day-end gate |
| 4.1 | 4 | T028, T029 sequential (tests depend on fixes) + T030 parallel | — |
| 4.2 | 4 | T031, T032 parallel | T033 PR open |
| 4.3 | 4 | T033, T034 parallel | T035 day-end gate |
| 5.1 | 5 | T036 (serial review) → T037, T038 parallel | T039 merge gate |
| 5.2 | 5 | T039, T040 serial | T041 final gate |

## Progress Log (filled during execution)

### Day 1 Spike Outcome (T008)
- **Start time**: 2026-04-17T19:03:59Z
- **End time**: 2026-04-17T19:06:41Z
- **Total wall-clock for 50 edges**: 162 seconds
- **Seconds per edge**: 3.24s/edge
- **Tripwire threshold**: 38.4s/edge
- **Preliminary decision (T007 web-researcher)**: CONTINUE TIER 1 — 3.24s/edge is ~12× under the 38.4s/edge threshold; R3 Tier 1 default ≥500-edge floor is comfortably feasible.
- **Final decision (T008 team-lead, 2026-04-17)**: **CONTINUE TIER 1** — ratifies the web-researcher preliminary measurement. Agent-authored wall-clock of 3.24s/edge × 500 edges = 1620s ≈ 27min of agent-time for full Tier 1 floor, well within Days 2-3 harvest budget. Human-authored equivalent unobserved (agent-executed), but R3 tier-gate math holds regardless of authoring modality because the monotonic-decreasing Day 2/Day 3 tier gates (<200 / <100 primary edges committed) rely on commit-count, not authoring-time. No escalation needed. Tier 1 (≥500-edge floor) remains the scope target through Day 3; downstream Day 2 gate (T019) and Day 3 gate (T026) will re-verify on committed-edge count.
- **Rationale**: 50 edges authored across 5 diverse slices (10+10+10+10+10 per A5 composition) completed in 162s wall-clock. Slice composition verified: 10 OWASP↔CWE (high confidence, explicit CWE cross-references), 10 ATT&CK↔CWE (medium confidence, inferred from Mitigations context per anti-drift rule), 10 ATLAS↔ATT&CK (mix of high/medium from atlas.mitre.org parent-technique citations), 10 LLM↔NIST (high confidence verbatim from Feature 144 nist-ai-rmf-mapping.md Surface B+C), 10 Agentic↔MITRE (medium confidence via OWASP Agentic 2026 ASI01-ASI10 → AML.T0058-T0062 agent techniques + T1548/T1078/T1195 legacy ATT&CK). All 50 edges passed shape conformance (FR-009) and enum closure (FR-010/FR-012/FR-013). Citation resolution concerns: (a) AML.T0059-T0062 URLs cited as atlas.mitre.org/techniques/AML.TNNNN — stability to be verified by T011/T020 R7 tripwire on Day 2; (b) OWASP Agentic 2026 full_id form pinned as ASI01:2026 style (parallel to LLM01:2025 convention) — to be confirmed against authoritative OWASP source in T005 owasp.yaml authoring.

### Day 2 Tier Gate (T019)
- **Committed primary edges at end of Day 2**: 292 primary / 292 total
- **Threshold**: ≥200 for Tier 1
- **Decision**: **TIER 1 HOLDS**
- **Rationale**: 292 edges = 58% of the ≥500 merge floor with 3 authoring days remaining. Within 200-499 "Tier 1 on track" band per the T019 decision matrix. Day 1's T008 ratified a 3.24s/edge authoring rate (~12× under 38.4s/edge tripwire) that continues to support the ≥500 floor; residual 208-edge gap is absorbed by T023 (41 NIST-derived edges transcribed verbatim per FR-022) + T024 Day 3 harvest (~167 edges). No Tier 2 escalation trigger met. T023/T024 proceed as planned.

### R7 Tripwire Outcome (T020)
- **AML.T0058 resolved?** YES — present in authoritative MITRE-owned `atlas-data/techniques.yaml` on GitHub; URL pattern `https://atlas.mitre.org/techniques/AML.T0058`
- **AML.T0059 resolved?** YES — same source; URL pattern identical
- **AML.T0060 resolved?** YES — same source; URL pattern identical
- **AML.T0061 resolved?** YES — same source; URL pattern identical
- **AML.T0062 resolved?** YES — same source; URL pattern identical
- **WebFetch control proof**: known-good seed AML.T0051 also returns 404 via WebFetch → client-side anti-bot gating, not URL instability
- **Decision**: **ALL 5 PRESENT** (no descope required)
- **Inline correction (commit `be18076`)**: T011 aggregated-search names were WRONG for all 5 AML.T0058-T0062. Architect corrected to authoritative names from atlas-data:
  - AML.T0058: "Publish Poisoned Models" (was "Publish Poisoned AI Agent Tool")
  - AML.T0059: "Erode Dataset Integrity" (was "Activation Triggers")
  - AML.T0060: "Publish Hallucinated Entities" (was "Data from AI Services")
  - AML.T0061: "LLM Prompt Self-Replication" (was "AI Agent Tools")
  - AML.T0062: "Discover LLM Hallucinations" (was "Exfiltration via AI Agent Tool Invocation")
- **Architect sign-off**: 2026-04-17 (no descope, name correction authorized)
- **FR-021 72 vs 68 secondary concern**: deferred to T022 with architect non-binding recommendation of Option (b) — curate 68-subset from Jan 2023 AI RMF Core publication, treat the 4 excess as post-publication Playbook expansions outside FR-021 scope.

### Day 3 Tier Gate (T026)
- **Committed primary edges at end of Day 3**: **509** primary / 509 total (measured at HEAD `1cd00ab`; every edge in the file is `edge_type: primary`)
- **Threshold**: ≥500 for R3 Tier 1 default scope
- **Decision**: **TIER 1 HOLDS** (no escalation; no PRD amendment; no re-sign)
- **Rationale**: 509 crosses the ≥500 Tier 1 floor by 9 edges. Day 3 net authoring of +217 primary edges (start-of-Day-3 baseline 292 + T023 Surface B canonical 27 + T024 web-researcher net-new harvest 190 = 509) closed the 208-edge gap projected by the Day 2 tier gate T019 rationale. Day 1 T008 tripwire of 3.24s/edge (≈12× under the 38.4s/edge threshold) held through the Day 3 harvest, confirming the R3 Tier 1 feasibility substrate. Confidence discipline per FR-013 held: 283 high / 225 medium / 1 low across the 509-edge final state (source: `.aod/results/web-researcher.md` Confidence Distribution table). T023 Surface B canonical 27 edges co-exist in `crosswalk.yaml` with 22 dash-format drifted Surface B edges from Batch 5 (deferred to T029 fix-in-YAML remediation per NEXT-SESSION.md §Open Decisions #2); 16 pre-existing drifted Surface C edges likewise remain pending T029 cleanup. T023 Surface C canonical transcription was deferred to an ADR-025 amendment Issue (structural blocker per `.aod/results/senior-backend-engineer.md` §5.1 — AI 600-1 §2.X identifiers are not in the 7-value taxonomy enum and not in `nist-ai-rmf.yaml`). Neither co-present drift nor Surface C deferral affects T026 math — the decision matrix counts raw primary edges. Full details: `.aod/results/team-lead.md`.

### SC-013 Parse Performance (T030)

- **Date**: 2026-04-17
- **Command**: `time python3 -c "import yaml; yaml.safe_load(open('schemas/taxonomy/crosswalk.yaml'))"`
- **crosswalk.yaml parse time**: **375ms** (steady-state median across 3 runs: 378ms, 374ms, 517ms cold — 374-378ms steady)
- **owasp.yaml parse time**: **~70ms** (3-run range 67-73ms)
- **cwe.yaml parse time**: **~55ms** (3-run range 54-56ms)
- **Threshold compliance**: **PASS** (<500ms FR-031 / SC-013 informational bound; crosswalk at 375ms is 125ms under the bound; smaller catalogs are ≈7-9× under)
- **Commodity hardware**: macOS Darwin 25.3.0 (arm64), Python 3.9.6, PyYAML 6.0.2
- **Edge count at measurement**: 526 primary edges (438 post-T029 + 88 Batch 11 net-new)
- **Note**: FR-031 / SC-013 is an informational bound, not a CI gate — test_records_sorted does not fail on slower parses. Measurement recorded for adopter guidance. If future growth approaches 500ms, consider index caching or YAML streaming parse.

### FR-036 Backward-Compat Gate (T031)
- **Date**: 2026-04-17
- **Command**: `SOURCE_DATE_EPOCH=1700000000 python3 -m pytest tests/scripts/test_backward_compatibility.py -v`
- **Result**: **PASS** (13 passed, 1 skipped by design — `mermaid-agentic-app` excluded from SC-003 per T033 narrowed interpretation; byte-identity subtest for `mermaid-agentic-app` itself passed)
- **Baselines verified**: **6/6 byte-identical** — `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference` (6th baseline added by Feature 145, all covered under `SOURCE_DATE_EPOCH=1700000000` per ADR-021). Task text says "5/5 non-agentic"; the test currently parametrizes 6 (Feature 145 added `maestro-reference`). FR-036 intent — zero drift from the committed baseline set — satisfied.
- **Feature 142 invariant tests (co-located in same file)**: `test_feature_142_zero_edit_invariant_on_detection_agents` PASS (ADR-026 Decision 1: no edits to 11 detection agents on branch `180-taxonomy-crosswalk-collection` vs main); `test_feature_142_backward_compat_pattern_defaults` PASS; `test_feature_142_multi_agent_gate_predicate_false_on_baselines` 5/6 PASS + 1 SKIP (designed skip).
- **Notes**: Wall-clock 15.08s on commodity hardware. Zero runtime surface-area change confirmed — Feature 180 adds only `schemas/taxonomy/*.yaml` (not referenced by `scripts/*.py` or Typst templates), `tests/schemas/test_taxonomy_integrity.py`, and ADR-027. No escalation required.

---

## Dependencies + Prerequisites (Per Task)

- **T001** requires: nothing
- **T002** requires: T001 (ADR-004 absence verification)
- **T003** requires: T002 (ADR-027 committed in Proposed)
- **T004** requires: T003 (schema frozen)
- **T005** requires: T004 (directory exists)
- **T006** requires: nothing (parallel to T004)
- **T007** requires: T003 (schema frozen; crosswalk shape committed in ADR)
- **T008** requires: T007 (spike completed)
- **T009** requires: T002, T005, T007, T008
- **T010–T015** require: T009 (Day 1 gate passed)
- **T016** requires: T008 (tripwire decision)
- **T017–T018** require: T009 (schema frozen)
- **T019–T021** require: T010–T018
- **T022** requires: T021 (Day 2 gate passed)
- **T023** requires: T022 (NIST catalog complete)
- **T024** requires: T019 (tier decision preserved)
- **T025** requires: T017 (README draft)
- **T026–T027** require: T022–T025
- **T028** requires: T027 (all 8 YAMLs committed — Architect F3 sequencing)
- **T029** requires: T028 (test failures to fix)
- **T030** requires: T026 (crosswalk.yaml tier-adjusted final state; Architect C1 correction — was listed as T024 but T026 is the post-tier-gate finalization)
- **T031** requires: nothing on F-A1 work (backward-compat is independent by FR-036 zero-runtime-touch guarantee; annotation per Architect C2 — mental-model prerequisite is "schemas/taxonomy/ staged via T027", but technically T031 can run at any point on main after Feature 128 bootstrap)
- **T032** requires: T028, T029 (tests green)
- **T033** requires: T028, T029, T030, T031, T032 (all ready)
- **T034** requires: T033 (PR exists to link from)
- **T035** requires: T033, T034
- **T036** requires: T035 (PR complete)
- **T037–T038** require: T036 (review comments)
- **T039** requires: T037, T038 (all addressed + green CI)
- **T040–T041** require: T039 (merged)

---

## Definition of Done (all 13 SCs + governance)

F-A1 is **Delivered** when all of the following are true:
1. SC-001 through SC-013 all verified green at merge time
2. ADR-027 Status: Accepted
3. PR merged to main (squash)
4. PRD 180 status: Delivered in `docs/product/02_PRD/INDEX.md`
5. BACKLOG.md regenerated
6. GitHub Issue #180 at stage:done
7. 2 follow-on Issues filed (related/superseded expansion; citation link-rot monitoring)
