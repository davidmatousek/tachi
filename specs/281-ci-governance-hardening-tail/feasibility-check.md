---
artifact: feasibility-check
feature_id: 281
owner: team-lead
date: 2026-06-30
prd_number: 281
status: draft
estimate:
  planning_days: 2.0
  floor_days: 1.0
  ceiling_days: 3.0
  confidence: high
---

# Feasibility Check — Feature 281 (CI & Governance Hardening Tail)

**Owner:** team-lead · **PRD:** `docs/product/02_PRD/281-ci-governance-hardening-tail-2026-06-30.md` · **Verdict:** APPROVED_WITH_CONCERNS (advisory only, none blocking)

## Verdict

**FEASIBLE.** All four in-scope items (#281 lead + #285/#286/#287) are config/docs/reuse work with every hard dependency already satisfied on `main`. No greenfield machinery, no cross-gate coupling. #280 pre-delivered (PR #290) — correctly excluded.

## Estimate (engineering-days)

| Band | Days | Meaning |
|---|---|---|
| `floor_days` | **1.0** | #285/#286 split OUT — deliver #281 + #287 only (P2 hardening core: SC-1 + SC-4) |
| `planning_days` | **2.0** | central — all four in-scope, no ballooning (4 × 0.5 d) |
| `ceiling_days` | **3.0** | #285/#286 stay IN and balloon (probe → committed fixture harness; template → DSL-with-tests) — the §8 carve trip-wire |

Constraint `floor ≤ planning ≤ ceiling` satisfied (1.0 ≤ 2.0 ≤ 3.0). Confidence **high**: every dependency pre-satisfied on `main`, the lead item (#281) is a structural clone of `tachi-catalog-drift.yml` (#329, ~1.5 d *including* a novel guard #281 does not need), and the only scope-creep risk (#285/#286) is contained by the split valve.

**Per-item:** #281 0.5 d (clone + failure-injection test) · #287 0.5 d (formalize in-comment policy) · #285 0.5 d (probe + rule-ID table) · #286 0.5 d (~80–120 LOC template + docs).

## Advisory concerns (for `/aod.plan` and `/aod.tasks` — none gate sign-off)

- **C-1 (sequencing):** author #285 before/with #287 — #287's re-test consumes #285's rule-ID mapping. Capture in `/aod.tasks` wave ordering. *(folded into PRD §8 sequencing note)*
- **C-2 (split discipline):** enforce §8 carve triggers mechanically at `/aod.tasks`; the 3.0-d ceiling is the numeric trip-wire.
- **C-3 (F-250 lock-step):** #281's `paths:` must stay a single YAML-anchored list including the AC-2 script + workflow file (FR-281.1); no second list that can drift (the #338 lesson).
- **C-4 (OQ scope):** OQ-1 (AC-7 ANOMALY compaction → sibling issue) and OQ-2 (#287 scheduled detector → split-valve) stay OUT; confirm at `/aod.plan`.

## Dependencies (all verified satisfied on `main`)

Delivered #280 script (`claude-permissions-ac2-crosscheck.sh`, rc=0) · F-4 `CLAUDE_PERMISSIONS.md` §3/§4 · F-5 `.gitleaks.toml` / `PRECOMMIT_HOOKS.md` / `run.sh` + fixtures / ADR-042. No cross-dependency on Wave-1 (#333) or delivered Wave-2 leads (#329/#338) — fully interleavable.

## Full findings

`.aod/results/team-lead-281.md` (feasibility) · `.aod/results/architect-281.md` (technical, APPROVED_WITH_CONCERNS: C-1 gitleaks-binary provisioning, C-2 jq-guard, C-3 checkout dependency — all folded into PRD FRs).
