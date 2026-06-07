---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-07
    status: APPROVED
    notes: "0 blocking. Plan covers all 9 spec FRs with explicit wave→FR traceability; MVP-first framing preserved (10 edges ship independent of the 6-ID disposition); no-schema/no-ADR/no-mitre-attack boundary held; #184/#185 + 2 CWE-blocked edges stay out. Re-verified live: 526 edges, 5 test functions, e58f247=551 with all 10 FR-001 edges byte-exact + 0 collisions, both CWE-blocked edges reference no gap ID and are absent, PR #321 draft/feat(186). 2 minor non-blocking: (1) cosmetic priority-label drift (spec P1/P2/P3 ordering is correct); (2) carry-forward to /aod.tasks — W1.2 (restore 10 edges) does NOT depend on the W0 disposition gate (only the conditional record-adds W1.3/W1.4 do), so tasks.md should model the 10-edge MVP as independent of W0. Details: .aod/results/product-manager.md"
  architect_signoff:
    agent: architect
    date: 2026-06-07
    status: APPROVED
    notes: "0 blocking. Constitution Check correct (PASS, no violations, no schema/ADR — mitre-atlas/mitre-attack already in the 7-value enum). Wave sequence sound; FR-002 extract-to-checked-in-artifact-first correctly de-risks the dangling SHAs (e58f247/991e1ee unreachable from main, unpushed). Byte-exact recovery from e58f247 is the right mechanism; FR-006 correctly forbids the other ~72 T029 removals + the 2 CWE-blocked edges. Refined 16/10/6 accounting matches my PoC — re-reproduced (restore 10 → 536, integrity 5/5 green, 0 collisions; tree left clean via git checkout). restored-edges.yaml annotation-key-stripping design is correct vs the crosswalk no-extra-keys rule. 14 claims + 5/5 questions re-verified PASS. No residual gap before /aod.tasks. Details: .aod/results/architect.md"
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: MITRE ATT&CK + ATLAS Catalog Expansion — Residual Drift-Edge Restoration (F-A1.3)

**Branch**: `186-mitre-catalog-expansion` | **Date**: 2026-06-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/186-mitre-catalog-expansion/spec.md`

## Summary

Restore the **10 now-resolvable MITRE-scoped crosswalk edges** that Feature 180's T029 cleanup removed (recovered byte-exact from dangling commit `e58f247`, extracted to a checked-in artifact first), and obtain an architect **add/reject/defer disposition** for the 6 ATLAS IDs still missing from `mitre-atlas.yaml` — adding any approved records and restoring their edges. The taxonomy integrity suite (5 functions) is the structural acceptance gate. Pure additive data change: **no schema version bump, no ADR, no `mitre-attack.yaml` change.**

## Technical Context

**Language/Version**: Python 3.11 (test + tooling only; the feature payload is static YAML data)
**Primary Dependencies**: `pyyaml`, `pytest` (existing); `git` (for byte-exact blob recovery from dangling commits)
**Storage**: static YAML — `schemas/taxonomy/mitre-atlas.yaml`, `schemas/taxonomy/crosswalk.yaml`
**Testing**: `pytest tests/schemas/test_taxonomy_integrity.py` (5 functions; `5 passed` on `main`)
**Target Platform**: repo data files + CI (`tachi-pytest.yml`)
**Project Type**: single (data-layer change in the existing repo)
**Performance Goals**: N/A (static data; integrity suite runs ~1s)
**Constraints**: FR-030 referential integrity (inviolable); ADR-027 record/edge shape; lexicographic catalog sort; ≥500 primary-edge floor; byte-exact edge recovery (no re-authoring)
**Scale/Scope**: +10 edges (526→536), +0–6 ATLAS records, +0–6 conditionally-unblocked edges
**Unknowns**: 1 — the exact "add" set among the 6 missing ATLAS IDs. Modeled as a **build-time architect gate (FR-003)**, not a planning blocker; the plan is disposition-agnostic and tolerates an empty add-set without rework.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Verdict | Rationale |
|-----------|---------|-----------|
| I. General-Purpose Architecture | PASS | Taxonomy data, not core logic; no new domain coupling introduced. |
| II. API-First Design | N/A | No API/UI surface. The crosswalk *is* a machine-readable contract consumed via existing outputs (SARIF/reports); shape unchanged. |
| III. Backward Compatibility (NON-NEGOTIABLE) | PASS | Additive records + previously-present edges; **no `schema_version` change**; consumers see more edges, never different shapes. Monotonic. |
| IV. Concurrency & Data Integrity | PASS (by-test) | Static YAML, no runtime state. `test_crosswalk_referential_integrity` is the data-integrity guarantee; never left in a dangling state. |
| V. Privacy & Data Isolation | N/A | Public MITRE technique IDs + public authority URLs; no PII/secrets. |
| VI. Testing Excellence | PASS | The 5-function integrity suite is the acceptance oracle (FR-007); no new code paths requiring new test types. |
| VII. Definition of Done (NON-NEGOTIABLE) | DEFERRED | Satisfied at `/aod.deliver` (DoD checklist in spec/PRD). |
| IX. Git Workflow (NON-NEGOTIABLE) | PASS | On feature branch `186-mitre-catalog-expansion`; draft PR #321 open. |
| X. Product-Spec Alignment (NON-NEGOTIABLE) | PASS | spec.md PM-approved; this command obtains plan.md PM + Architect dual sign-off. |

**Result: PASS — no violations. Complexity Tracking not required.**

## Project Structure

### Documentation (this feature)

```
specs/186-mitre-catalog-expansion/
├── plan.md                 # This file (/aod.project-plan output)
├── spec.md                 # PM-approved specification
├── research.md             # Empirical extraction (the 10/6 edge split)
├── data-model.md           # Entities: edge, ATLAS record, restore-set, disposition
├── quickstart.md           # Verify/repro steps
├── contracts/
│   └── restored-edges.schema.md   # Restore-set artifact shape + integrity acceptance contract
├── restored-edges.yaml     # (build output, FR-002) the checked-in restore-set extracted from e58f247
└── tasks.md                # Task breakdown (/aod.tasks output)
```

### Source Code (repository root)

```
schemas/taxonomy/
├── mitre-atlas.yaml        # +0–6 records (FR-004, "add"-disposition IDs only); header provenance note (FR-009)
├── mitre-attack.yaml       # UNCHANGED (all 3 originally-missing ATT&CK IDs already present)
└── crosswalk.yaml          # +10 edges (FR-001) [+0–6 conditional, FR-005]

tests/schemas/
└── test_taxonomy_integrity.py   # UNCHANGED gate (5 functions) — must stay green (FR-007)
```

**Structure Decision**: Single-project data-layer change. No new modules, services, or interfaces. The only new repo artifact is the checked-in `restored-edges.yaml` (FR-002) under the feature's specs directory; the production payload is edits to two existing taxonomy YAML files.

## Phase 0: Research

**Complete.** See [research.md](research.md) — grounded in an empirical `yaml.safe_load` diff of the dangling commits, it resolved every Technical-Context unknown except the FR-003 disposition (a build gate by design). Key resolved decisions:

- **Decision: recover edges byte-exact from `e58f247`** (pre-removal blob, 551 edges), not re-author. *Rationale*: preserves original `edge_type`/`confidence`/`citation`; avoids the F-180 R7 name/content-contamination failure mode. *Alternatives rejected*: re-authoring from MITRE sources (lossy, slow, risks drift); diffing `main` (impossible — squash-merged to `8b7c7bf`).
- **Decision: scope to exactly the 16 gap-ID edges → restore the 10 resolvable.** *Rationale*: the full T029 removal was 88 edges (multi-cause); restoring more re-introduces the semantic-drift/dedupe edges T029 correctly removed. *Alternatives rejected*: "restore all now-resolvable T029 edges" (over-broad — pulls in 70 non-MITRE removals + the 2 CWE-blocked #185 edges).
- **Decision: no schema/ADR change.** *Rationale*: `mitre-atlas`/`mitre-attack` already in the 7-value enum (ADR-027); additive records only.

## Phase 1: Design & Contracts

**Complete.** Generated:
- [data-model.md](data-model.md) — the 4 entities (crosswalk edge, ATLAS catalog record, restore-set artifact, ID disposition) with shapes and validation rules.
- [contracts/restored-edges.schema.md](contracts/restored-edges.schema.md) — the restore-set artifact schema + the integrity-suite acceptance contract (the 5 invariants).
- [quickstart.md](quickstart.md) — extract → restore → verify steps reproducible by any engineer.

**No API contracts** (data-layer feature; no endpoints). **Agent-context update**: `update-agent-context.sh` is absent in this repo (known) — skipped gracefully; no new technology to register.

## Implementation Approach (wave sequence → /aod.tasks)

Sequenced per the PRD Team-Lead agent plan. Disposition gate first; edits second; verification third.

**Wave 0 — Disposition Gate (architect)** *(blocks all edits)*
- FR-003: verify each of the 6 missing ATLAS IDs (`AML.T0001/T0005/T0025/T0037/T0043/T0048`) against `mitre-atlas/atlas-data`; publish add/reject/defer + rationale on Issue #186. Tolerate "fetch unavailable" by recording the obstruction (blocks only US-2).

**Wave 1 — Extract & Restore (senior-backend-engineer)** *(after Wave 0; FR-001/FR-002/FR-004/FR-005)*
1. FR-002: extract the in-scope removed edges from `e58f247` into `specs/186-*/restored-edges.yaml` **first** (de-risk dangling-object loss) — the 10 resolvable + the 6 conditional, tagged by resolvability.
2. FR-001: insert the 10 resolvable edges into `crosswalk.yaml` (byte-exact; dedupe-guard against the 526 existing).
3. FR-004 (conditional): for each "add"-disposition ID, add the `mitre-atlas.yaml` record (shape, lexicographic position, atlas-data name) + FR-009 header provenance note.
4. FR-005 (conditional): restore each edge unblocked by an "add".
5. FR-007: run the integrity suite after each edit; keep it green.

**Wave 2 — Verify & Guard (tester, code-reviewer)** *(after Wave 1; FR-006/FR-007 + US-3)*
- tester: confirm 5/5 integrity functions green; edge count 526→536(+k); no duplicate; ≥500 floor.
- code-reviewer: confirm FR-006 — **no** out-of-scope edge re-introduced (diff vs pre-change crosswalk; 0 of the ~72 non-gap removals, 0 of the 2 CWE-blocked edges).

**Close — Documentation (FR-009)**
- CHANGELOG `feat(186)` entry; update F-180 `NEXT-SESSION.md` decision trail; `/aod.analyze` clean; close Issue #186 `stage:done`.

## Risks (carried from spec/PRD)

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Over-restore the full 88-edge T029 diff → re-break crosswalk | Medium | Medium | FR-001 enumerates the exact 10; FR-006 forbids the rest; code-reviewer diff-check; integrity test catches dangles. |
| Dangling SHAs GC'd before extraction | Low-Med | High | FR-002 extracts to checked-in `restored-edges.yaml` as the **first** build step (Wave 1.1). |
| FR-003 ATLAS source unreachable | Medium | Low | Blocks only US-2; US-1 (the 10 edges) ships regardless; record the obstruction, don't guess. |
| "add"-set ID name drift vs pre-T029 authoring | Low | Low | FR-004 sources names from `atlas-data` (R7 lesson), not the historical blob. |

## Complexity Tracking

*No Constitution Check violations — section intentionally empty.*
