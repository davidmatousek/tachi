---
artifact: feasibility-check
feature_id: 329
owner: team-lead
date: 2026-06-30
prd_number: 329
status: draft
estimate:
  planning_days: 1.5
  floor_days: 1.0
  ceiling_days: 3.0
---

# Feasibility Check — Feature 329 (ORDERED_FRAMEWORKS Catalog-Drift CI Guard)

**Owner**: team-lead | **Date**: 2026-06-30 | **Verdict**: APPROVED_WITH_CONCERNS (feasible; central estimate holds)

## Estimate (authoritative — PRD timeline derives 1:1 from `planning_days`)

| | floor | planning (central) | ceiling |
|---|---|---|---|
| PRD preliminary guess | 0.75d | 1.5d | 2.5d |
| **Team-Lead confirmed** | **1.0d** | **1.5d** | **3.0d** |

`floor ≤ planning ≤ ceiling` ✓. **Central 1.5d CONFIRMED** (HIGH confidence). Both boundaries widened for the single FR-2 risk: floor 0.75→1.0 (no CA-baseline regen *script* exists — it is a hand-run recipe, so the sidecar requires authoring a regen wrapper + one real local regen/byte-compare cycle); ceiling 2.5→3.0 (absorbs the tail where T001 finds `main` red AND the sidecar formalization needs a Typst-version reconciliation per regen-contract D-9 invariant 2).

## Calibration

Three of four sibling CI features (`tachi-maestro-coverage.yml`, #338 push-trigger, #282 gitleaks, #183 linkrot) delivered in the ~1–2.5d band. **`tachi-maestro-coverage.yml` is the near-exact structural twin of M2** — single-runner, path-filtered, `contents: read`, re-derives a count/invariant from a canonical source function, fails naming the offending entity. This de-risks M2 to near-zero. The only thing pushing #329 above a pure-M2 feature is FR-2's regen-lane coupling. #329 ≤ #282 (no binary/SHA-pin/SARIF).

## Milestone re-slice (same 1.5d total)

T001 pre-state (front-loaded, ~0.1d) → M1 guard logic + sidecar-by-regen (~0.7d, the load-bearing half) → M2 workflow + synthetic test (~0.4d, copyable precedent) ∥ startable with M1 → M3 docs/ADR/CHANGELOG (~0.4d).

## Concerns (full detail: `.aod/results/team-lead-prd-329.md`)

- **C1 [HIGH]** — FR-2 under-specified: no CA-baseline regen script exists (hand-run recipe). Sidecar must be formalized into an emitting wrapper. **Resolve as OQ-1 at /aod.plan (Architect owns the mechanism).** Drives the floor/ceiling revision; not a feasibility blocker.
- **C2 [MEDIUM]** — T001 pre-state ("is `main` green on the byte-identity suite?") is the schedule-defining gate; **front-loaded to hour-zero of M1** in PRD v1.1. Git evidence (last baseline touch = F-185 `2aa1bf5` which absorbed #186's ATLAS delta; only member-YAML change since = #333 count-neutral) ⇒ `main` very likely green; Risk-4 genuinely Low.
- **C3 [LOW]** — `lru_cache` on `_load_framework_yaml_records`: synthetic test must `cache_clear()` per case or risk a false-green. Folded into FR-7.
- **C4 [LOW]** — single-runner (FR-5) is a determinism *consequence* (load-bearing for NFR-1), not just a CI-minute saving. Folded.

## Capacity / scheduling

One engineer (senior-backend profile — Python + GitHub Actions + the regen/Typst lane); no multi-agent fan-out (sub-day; A↔B interface is a thin stubbed sidecar path). Optional wave model: W1={T001}; W2={Track A FR-2/M1 ∥ Track B M2}; W3={integration + docs/closeout}.

## Write-set disjointness

Clean — only open PR is #341 (release-please `chore(main): release 4.45.1`), no source overlap. #329 write-set is all-new files (regen script, guard script, synthetic test, sidecar, `tachi-catalog-drift.yml`, ADR-037 amendment, docs/CHANGELOG); `schemas/taxonomy/*.yaml` is read-only (NFR-4). No collision.
