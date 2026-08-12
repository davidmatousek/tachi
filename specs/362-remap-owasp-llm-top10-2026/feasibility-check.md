---
artifact: feasibility-check
feature_id: 362
owner: team-lead
date: 2026-08-05
prd_number: 362
status: draft
estimate:
  planning_days: 6.0
  floor_days: 3.5
  ceiling_days: 10.0
---

# Team-Lead Feasibility Check — Feature 362: Remap OWASP LLM Top 10 to the 2026 Edition

**Verdict**: APPROVED_WITH_CONCERNS (8 concerns — 2 HIGH, 3 MEDIUM, 3 LOW) · **FEASIBLE WITH MODIFICATIONS**
**Full review**: `.aod/results/team-lead.md` (2026-08-05) · Constraint Analysis lens applied
**PRD response**: all eight concerns incorporated in PRD v1.1 (C2 split adopted → F-362b)

## Estimate (attention-days, AOD agent-orchestrated pace)

| Band | Days | Conditions |
|------|------|-----------|
| floor | 3.5 | FR-6 ADR lands hard cutover; no Partial downgrade → CA baselines stay byte-identical; `examples/` split out; no gap follow-ups |
| **planning (central)** | **6.0** | ADR one architect pass; 57-of-74 re-keys clean; agents/skills/adapters in 3–4 parallel lanes; one Partial downgrade cascade; examples split to F-362b |
| ceiling | 10.0 | Dual-emission ADR (alias machinery + schema + tests); ≥1 Partial downgrade into `.claude/rules/scope.md` + 11 restatements; examples in-loop hitting orchestrator context limit; init-baseline-tree red-chase |

**Calibration basis** (prior team-lead estimates, same units): F-295 = 1.0 (0.5/2.0); F-333 = 3.0 (1.5/5.0). F-362 adds an ADR gate, a 126-file mechanical surface, a 74-edge semantic pass, and a derived-artifact tail. Re-issue projection once plan-stage rulings land (C4 conditionality + split confirmed): **~4.5 ± 1.0**.

**ICE note**: PM's E:6→E:4 re-score recommendation is NOT supported by measurement; **E:5 is the honest landing** (declined to co-sign E:4).

## Blast radius (independently re-measured — PM numbers verify)

- In-scope: **126 files / 715 refs** (examples 47, .claude 24, adapters 17, tests 16, docs 10, schemas 4, other 8)
- Protected by exclusions: **114 files / 955 refs** (PM understated at 97/817 — direction safe)
- Crosswalk: **74 LLM-keyed edges, 57 require re-keying** (LLM01/LLM02 hold rank; LLM10's 11 edges and LLM03's 8 are the highest-volume, most dangerous re-meanings)
- Key sizing insight: the catalog is only 10 records — cost concentrates in the 47-file derived tail and the 74-edge semantic pass. Budgeting by "catalog surgery, like F-185" under-estimates ~2x.

## Concerns (all folded into PRD v1.1)

- **C1 (HIGH)**: `OWASP_COVERAGE.md` has no generator — FR-9 split into 9a (hand-update + review gate) / 9b (CA-PDF baseline determinism recipe)
- **C2 (HIGH)**: `examples/` = 47 files / 37% of scope, unbounded orchestrator-context cost → split to F-362b, blocking before next minor, declared FR-8 carve-out
- **C3 (MEDIUM)**: `adapters/` (17 files, 4 formats, no parity test) inserted into chain after agents/skills → FR-12
- **C4 (MEDIUM)**: CA-baseline regen is conditional — render consumes id+classification only; catalog rename alone is baseline-free; regen fires on classification change (Partial downgrade or re-keyed example `source_attribution`). Floor/ceiling hinge; architect determination at plan → FR-7
- **C5 (MEDIUM)**: `tests/fixtures/init-baseline-tree/` byte-equality fixture must regen same-commit (F-248/F-256 harness clones HEAD) → FR-8
- **C6 (LOW)**: 74 edges / 57 re-keys (not 75) → FR-5 + metrics corrected
- **C7 (LOW)**: exclusion set measures 955 refs / 114 files → FR-8 corrected
- **C8 (LOW)**: FR-6 ADR milestone bound to a hard date (Day 1 of plan, 2026-08-06) → Timeline

## Dependency chain (corrected)

FR-6 ADR (hard gate) → owasp.yaml (10 records) → crosswalk (74/57) → .claude agents+skills (24) → adapters (17) → emitters + normalize_owasp_id → gap analysis → coverage re-derivation → 11 headline surfaces incl. `.claude/rules/scope.md` → tests (16) + init-baseline-tree (same commit) → [conditional] CA baselines → [split] examples → sweep → docs + CHANGELOG

## Decomposition & capacity

- Task count: ~30–34 as v1.0-scoped; **~22–26 with C2 split** (project envelope: 13–20 for prior catalog surgeries). Tasks must be bucket-scoped, never file-scoped.
- 4–5 parallel waves; W2 (agents/skills/adapters, 41 files) is the widest healthy fan-out (~70% peak load); no agent exceeds the 80% ceiling. W5 serializes if examples stay in-loop — the concrete capacity argument for the split.
- Session strategy per KB clean-session phasing: W0+W1 one session; W2 its own.

## Sign-off conditions for tasks.md

C1–C8 as enumerated (see full review §Sign-off Conditions), task count ≤26 post-split, bucket-scoped granularity, no agent >80% wave load. Timeline and capacity vetoes NOT exercised.
