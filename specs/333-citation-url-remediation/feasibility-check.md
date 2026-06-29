---
artifact: feasibility-check
feature_id: "333"
owner: team-lead
date: 2026-06-29
prd_number: "333"
status: draft
estimate:
  planning_days: 3.0
  floor_days: 1.5
  ceiling_days: 5.0
---

# Feasibility Check — F-333 Citation-URL Remediation (BLP-06 Wave 1)

**Verdict**: FEASIBLE WITH MODIFICATIONS — APPROVED_WITH_CONCERNS (1 HIGH, 2 MED, 2 LOW, 1 INFO; no blockers).
**Full review**: `.aod/results/team-lead-333.md`. **Lens**: Constraint Analysis.

## Estimate (1 engineer)

| Band | Days | Basis |
|------|------|-------|
| floor | **1.5** | Only if FR-1 adjudicates ATLAS to a clean re-point that reaches 2xx from the GitHub runner AND #325 defers AND FR-7 clears — all three classes become cascading find-replace (the PRD's optimistic case). |
| **planning (central)** | **3.0** | Realistic: FR-2 takes the **re-classify path** (host-scoped monitor change in `scripts/check-citation-urls.py`, ~0.75–1.25d incl. offline test) because re-pointing any `atlas.mitre.org` URL still 404s the runner (R7 confirmed in-tree); + FR-1 research (3 classes, dual-UA, runner-egress) + FR-6 dispatch-then-await (~0.5d wall-clock). |
| ceiling | **5.0** | If two+ of: ATLAS resolves mixed (per-ID handling); host-scoping needs a `classify_one()` refactor; FR-7 finds rendering exposure → CA-baseline regen; FR-6 needs a 2nd dispatch; #325 folds. |

**Recommended planning figure: 3.0 eng-days** (carry 5.0 as risk-buffered ceiling). The PRD's 2.5d top-end is overridden — too low once the re-classify code-path is priced in.

## Build Wave Plan (for /aod.plan → tasks)

- **Wave 0 — Research & Adjudication** (gates everything): `web-researcher` parallel fan-out over the 3 fix-classes — verify 36 ATLAS IDs in MITRE `atlas-data/techniques.yaml` + **runner-egress** reachability probe; find NIST AI 100-1 canonical landing; adjudicate the actual OWASP dead-set (incl. `llm0X2025` year-suffixed variants + 2 Agentic resource pages). → **architect** signs the fork resolution (a How decision).
- **Wave 1 — Apply** (branches by Wave-0 verdict): `senior-backend-engineer` — FR-3 NIST DOI cascading replace (73 records) ∥ FR-4 OWASP re-point (leave `llm01` untouched) ∥ FR-2 ATLAS (re-classify path likely: host-scoped 404→needs-review + offline test; re-point path only if Wave 0 overturns R7); FR-7 rendering-exposure check.
- **Wave 2 — Validation & Gate**: `tester` (offline `test_citation_shape()` + synthetic-404 classifier unit test) → `code-reviewer` (binding; NFR-5 host-scoping discipline) → FR-6 **dispatch monitor + await #332 self-close** (the real DoD gate, strictly last, async; not a code change).

## Key Constraints / Concerns

- **C1 (HIGH)** — estimate skewed optimistic; the ATLAS fix most likely is a classifier code change, not a YAML edit. Budget 3.0d central.
- **C2 (MED, split-valve)** — keep FR-2 in-scope, but **pre-authorized split trigger**: balloon = `classify_one()` control-flow/config refactor → split the classifier work to a BLP-06 Wave 2 sibling; stay = a bounded host-keyed status-override map + one test.
- **C3 (MED)** — **#325 does NOT fold**: its 4 edges cite a local file (`.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`), not the dead DOI. Recommend standalone. Formalize at /aod.plan.
- **C4 (LOW)** — FR-7 likely clears (coverage uses record counts, not URL strings; grep found no ATLAS URLs in baseline artifacts). Verify at plan; regen only if a string surfaces.
- **C5 (LOW)** — OWASP dead-set is messier than "4"; FR-1 must adjudicate the real set.
- **C6 (INFO)** — F-338 also edits `tachi-pytest.yml`; F-333's new offline test runs in that job (no file collision). Run F-333's test against post-338 `main` if merges are near-simultaneous.

## Dependencies / Collisions

**No write-set collision.** Disjointness from branch `338-restore-substitution-hardening` confirmed by `git diff --stat main..338` (zero overlap). F-333 surface: `schemas/taxonomy/{mitre-atlas,nist-ai-rmf,crosswalk}.yaml` + (re-classify) `scripts/check-citation-urls.py`. PRD's "disjoint from BLP-06 Waves 2–3" holds.
