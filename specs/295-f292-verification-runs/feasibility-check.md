---
artifact: feasibility-check
feature_id: 295
owner: team-lead
date: 2026-07-02
prd_number: 295
status: draft
estimate:
  planning_days: 1.0
  floor_days: 0.5
  ceiling_days: 2.0
---

# Team-Lead Feasibility & Timeline Review — F-292 Verification Runs (#295)

**PRD**: `docs/product/02_PRD/295-f292-verification-runs-2026-07-02.md`
**Reviewer**: team-lead | **Date**: 2026-07-02 | **Verdict**: FEASIBLE | **Sign-off**: APPROVED_WITH_CONCERNS (0H / 2M / 3L)
**Full review**: `.aod/results/team-lead.md` (snapshot; this file is the durable copy)

## Estimate (independent, bottom-up)

**floor_days=0.5 · planning_days=1.0 · ceiling_days=2.0** (attention-days)

| Work stream | Central attention | Notes |
|-------------|-------------------|-------|
| T017 / US-1 (agentic-app scoped verify) | ~0.45d | anchor extract + scoped run/overflow babysit + OI jq + emission diff + attribution walk (10–90m) + record/commit |
| T026 / US-2 (multi-tenant-rag-app pipeline) | ~0.17d | run + Cat 6 verify + commit + regen byte-identity |
| US-3 / P1 (BASELINE_EXAMPLES 7th entry) | ~0.13d | list edit + suite green + README row + PR-body KB-15 note |
| **Central sum** | **~0.7–0.75d** | with 1 snag + context-switch → firm **1.0d** |

- **Floor 0.5d**: fully clean pass (the "mechanical execution" ICE Effort=2 assumed).
- **Planning 1.0d**: one snag — a 2nd scoped-run attempt OR a careful attribution pass. ICE Effort=2 was optimistic; it undersold the fail-closed attribution protocol + defect-filing judgment overhead.
- **Ceiling 2.0d**: absorbs one orchestrator re-run cycle + one attribution second-pass + one defect-Issue authoring. Breach scenario (tail, not plan): compound repeated-overflow + genuine emission delta. Deliberately NOT inflated to 3.0d.

## Feasibility (4 dimensions) — all PASS

- **Effort**: three bounded work streams; "eng-day" is mostly analyst attention (SARIF diff interpretation, delta attribution, pass/fail judgment) plus async skill-run wall-clock. Fix-vs-file boundary keeps effort bounded even on gate failure.
- **Capacity**: board clear — BLP-06 W2 closed 2026-07-01, #217 delivered 2026-07-02; zero in-flight conflicts. Core work is NOT parallelizable (can't split a `tachi.threat-model` run; attribution is single-threaded reasoning).
- **Timeline**: "Dev Complete: 1 working day from plan approval" matches the 1.0d central. Caveat L-1: attention-day, not a same-calendar-day guarantee (async re-runs).
- **Dependencies**: git-history anchor `0629fa2~1` stable (PM-verified); deterministic regen path proven on 6 existing baselines; US-3→T026 ordering correct; orchestrator context-overflow is the primary risk driver but not a hard blocker; no external dependencies.

## Complexity check — attribution fits the ceiling, with margin

The emission-level hard gate (OI count, ruleId set, sink/flow) is structurally stable against all three known drift sources (F-260b asset tags, F-098/#311 MAESTRO annotations, #184–#186 crosswalk growth) — none change OI emissions. Byte-deltas live in the annotation envelope and map to a bounded walk over ~3 named feature-classes (`git log -p 0629fa2..HEAD -- <surface files>`), not open-ended forensics. **The ceiling's real consumer is orchestrator re-run cycles, not attribution depth.**

## Wave plan

**1 build wave, SERIAL internally** — parallel fan-out deliberately rejected: T017 and T026 contend for the same orchestrator context (known overflow constraint; concurrent tachi runs worsen context pressure).

| Order | Task group | Owner | Dependency |
|-------|-----------|-------|------------|
| 1 | T017 / US-1 — scoped run; OI-subset extract; diff vs `0629fa2~1`; fail-closed attribution; SC-003 record; defect-file on failure | **security-analyst** (LEAD) | none |
| 2 | T026 / US-2 — full pipeline under `SOURCE_DATE_EPOCH=1700000000`; Cat 6/CWE-943 verify; commit artifacts; regen byte-identity | **security-analyst** (LEAD) | after T017 (serialize) |
| 3 | US-3 / P1 — 7th `BASELINE_EXAMPLES` entry; suite green; README row; PR-body KB-15 callout | **tester** (alt: senior-backend-engineer for the Python edit) | after T026 lands & reproduces |

orchestrator coordinates; keep roster at 2 core agents — do not over-staff a 1.0d feature.

## Findings

- **M-1**: Orchestrator overflow is the dominant ceiling driver. At /aod.plan: pre-authorize per-agent staged fallback as T017's execution mode from the start; hard escape hatch — if 2 re-runs fail, file the overflow as a tooling defect and close #295 with the staged-partial record.
- **M-2**: US-3 is structurally gated on T026 reproducibility. Confirm at plan/tasks that US-3 is explicitly optional-on-T026-success so a T026 gate-failure doesn't cascade into a mislabeled "US-3 failure."
- **L-1**: Wall-clock ≠ eng-day — frame the 1.0d target as an attention-day.
- **L-2**: OQ-2 is a genuine Architect veto point (KB-15 consequence-scope). If vetoed, feature shrinks to T017+T026 (~0.75d); defer US-3 to a follow-up Issue.
- **L-3**: No parallelism to exploit — "single wave" is a serial chain; no fan-out speedup.

## Sign-off

**APPROVED_WITH_CONCERNS** — FEASIBLE; timeline/capacity veto NOT exercised. Not clean APPROVED because M-1/M-2 warrant explicit mitigation on record at plan/tasks; not CHANGES_REQUESTED — no PRD defect. Defers to Architect on OQ-1/OQ-2/OQ-3 (all Architect-owned, due /aod.plan).
