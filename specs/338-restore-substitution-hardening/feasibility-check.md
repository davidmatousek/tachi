---
artifact: feasibility-check
feature_id: 338
owner: team-lead
date: 2026-06-29
prd_number: 338
status: draft
estimate:
  planning_days: 2
  floor_days: 1
  ceiling_days: 3
---

# Feasibility Check — PRD #338 (Restore F-248/F-256 Substitution Hardening)

**Owner**: team-lead · **Workflow**: `/aod.define` Feature parallel review
**Verdict**: **FEASIBLE** — single Plan→Build→Deliver cycle, no phasing, do NOT split.

## Estimate

| Band | Days | Scenario |
|------|------|----------|
| Floor (optimistic) | **1** | Reconciliation clean, `defaults.env` gate already green, no manifest work, CI green first try. |
| Planning (realistic) | **2** | Careful hunk classification across init.sh's diff, one CI iteration to converge both matrix legs, W-1 byte spot-check, C-2 resolved. |
| Ceiling (pessimistic) | **3** | `defaults.env` gate red forcing a TECH_STACK in-scope decision (C-2), and/or a bash-3.2 surprise forcing a second CI iteration. |

`floor=1 ≤ planning=2 ≤ ceiling=3` (eng-days). **Confidence: HIGH** — source is known-good v4.44.0 code (`5b64f68`, verified intact); deterministic CI oracle. Residual risk is entirely the *cut line* (plan-stage analysis), not build-stage uncertainty.

> **Post-review note (architect HIGH-1)**: the parallel Architect review proved the three in-scope files are a *clean generic-revert* (no Sprint→Loop entanglement in those files), so the realistic case trends toward the **floor (1 day)**. Planning is held at **2** as the conservative number pending the C-2 `defaults.env` gate-state check (the one genuine unknown). The plan stage should re-confirm once the `defaults.env` gate state is known.

## Feasibility Findings (verified against the repo)

- **Single cycle, do NOT split**: the 3 files share one reconciliation context (same `/aod.update` reverted all three in lock-step) and one CI oracle. Splitting adds coordination overhead with zero parallelism gain.
- **Effort = M (cut-line-bound, not LOC-bound)**: the hardening source is known-good v4.44.0 code; what sizes the work is classifying the restore vs preserving any legit non-hardening change — and the architect's HIGH-1 shows that classification is near-trivial for the 3 files. Not L (no novel design, no new surface).
- **Dependencies all present & verified**: `5b64f68` (`v4.44.0-1-g5b64f68`, reachable); groundwork `99507b2` is the branch tip (FR-006 gate + FR-007 xfail genuinely landed). US-338.2 / US-338.3 are DONE — tasks.md must list them as completed deps, not re-task them.

## Carry into `/aod.plan` and `tasks.md`

- **C-2 / OQ-3 (highest-leverage)**: confirm the gated `test_init_sh_defaults_env.py` is GREEN with `TECH_STACK` absent. If red, either pull TECH_STACK restoration in-scope (1 line/file) or xfail+track it. Settle at plan or it is a build surprise.
- **W-1 (byte-surface watch)**: the FR-007 xfail removes byte-identity from the gate, so green CI proves *behavioral* not *byte* parity. Add an explicit manual byte spot-check (restored 3 file bodies vs `5b64f68`) as part of FR-005 acceptance.
- **S-1 (deliver gate, load-bearing)**: do NOT push the branch / open-ready the PR until the restore is green locally — the FR-006 `push:[main]` gate would otherwise redden `main` on its own behalf (honors `99507b2`'s own warning + the `/aod.update` insurance discipline).

## Agent Assignment (single wave)

| Task | Agent | Rationale |
|------|-------|-----------|
| FR-001..004 — restore the 3 bash file bodies + confirmation diff | `senior-backend-engineer` | bash hardening / shell tooling |
| FR-005 + W-1 — run gated suite both legs, byte spot-check vs `5b64f68` | `tester` | pytest harness + behavioral/byte verification |
| OQ cut-line ratification (manifest / defaults.env) | `architect` (at `/aod.plan`) | technical cut-line is pre-build |
| Deliver (S-1 gate, merge, release) | `devops` | all merges-to-main go through devops |

Full review: `.aod/results/team-lead.md`.
