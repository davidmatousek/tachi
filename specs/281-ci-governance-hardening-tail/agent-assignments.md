# Agent Assignments: CI & Governance Hardening Tail (Feature 281)

**Author**: team-lead · **Date**: 2026-07-01 · **Tasks**: [tasks.md](./tasks.md) (triple-signed)
**Split decision**: CARVE-IN (all four issues). Build-time split-valve retained (T016).
**Agent names**: exact `subagent_type` values only (senior-backend-engineer, tester, devops, security-analyst).

## Agent Assignment Matrix

| Task | Description | Agent | Story |
|---|---|---|---|
| T001 | Verify baseline-green pre-state (jq/AC-2/§3§4) | `tester` | Setup |
| T002 | Provision gitleaks v8.30.1 (SHA256, fail-never-skip) | `devops` | Foundational |
| T003 | Author `tachi-permissions-verify.yml` scaffold (clone catalog-drift) | `devops` | US1 |
| T004 | Add 4 verify steps (jq-guard, jq empty, AC-2, doc-grep) | `devops` | US1 |
| T005 | Self-documenting header comment block | `devops` | US1 |
| T006 | Failure-injection smoke test (throwaway) | `tester` | US1 |
| T007 | Author gitleaks pin-bump cadence surface (dedicated §) | `senior-backend-engineer` | US2 |
| T008 | `.github/ISSUE_TEMPLATE/gitleaks-bump.md` | `senior-backend-engineer` | US2 |
| T009 | Update ADR-042 §References | `senior-backend-engineer` | US2 |
| T010 | Empirical gitleaks coverage probe (rule-ID derivation) | `security-analyst` | US3 |
| T011 | Hand-author per-pattern→rule-ID catalog (§3 subsection) | `senior-backend-engineer` | US3 |
| T012 | Assess coverage gaps; file `enhancement` issue if any | `security-analyst` | US3 |
| T013 | Author `.gitleaks.toml.adopter-template` (~80–120 LOC) | `senior-backend-engineer` | US4 |
| T014 | Validate template config (`gitleaks detect --config=`) | `tester` | US4 |
| T015 | Extend §9 + README Security cross-ref | `senior-backend-engineer` | US4 |
| T016 | Split-valve final confirmation (LOC/effort re-measure) | `senior-backend-engineer` | Polish |
| T017 | Regression sweep (16-fixture matrix + pre-commit) | `tester` | Polish |
| T018 | Final AC/SC sweep (#281 green on clean main) | `tester` | Polish |

## Parallel Execution Waves

### Wave 1 — Independent starts (no cross-deps)
- `tester`: **T001** (baseline)
- `devops`: **T002** [P] (provision gitleaks) · **T003→T004→T005** (#281 workflow chain)
- `tester`: **T006** (after T003–T005 — #281 smoke)
- `senior-backend-engineer`: **T013** [P] (#286 template authoring)

**Gate**: T002 green (gitleaks provisioned) before Wave 2 gitleaks steps; #281 chain (T003–T006) is the independent MVP — may complete and merge without waiting on later waves.

### Wave 2 — gitleaks-dependent (after T002)
- `security-analyst`: **T010** (probe → rule-ID map) → **T012** (gap assessment)
- `senior-backend-engineer`: **T011** (catalog table, after T010)
- `tester`: **T014** (#286 template validation)
- `senior-backend-engineer`: **T015** (#286 §9 + README)

**Gate**: T011 (#285 catalog) complete before Wave 3 (T007 consumes it).

### Wave 3 — #287 cadence (after T011)
- `senior-backend-engineer`: **T007** (cadence surface, consumes #285 catalog) · **T008** [P] (issue template) · **T009** (ADR wiring)

### Wave 4 — Polish
- `senior-backend-engineer`: **T016** (split-valve confirmation)
- `tester`: **T017** [P] (regression sweep) · **T018** (final AC/SC sweep)

## Quality Gates Between Waves

| Gate | Between | Criterion |
|---|---|---|
| G1 | Wave 1 → 2 | `gitleaks` provisioned (T002 green, SHA256 verified); #281 smoke passes (T006) |
| G2 | Wave 2 → 3 | #285 catalog authored (T011) so #287's re-derivation reference resolves |
| G3 | Wave 3 → 4 | All FR tasks complete; docs cross-wired |
| G4 | Wave 4 → deliver | #281 green on clean `main`; 16/16 fixtures; template config-valid; split-valve confirmed |

## Time Estimates per Wave

| Wave | Scope | Est. |
|---|---|---|
| Wave 1 | #281 core (MVP) + #286 authoring | ~0.6 d |
| Wave 2 | #285 catalog + #286 validation/docs | ~0.6 d |
| Wave 3 | #287 cadence | ~0.5 d |
| Wave 4 | Polish/sweeps | ~0.3 d |
| **Total** | central estimate | **~2.0 d** (≤ 3.0-d ceiling — split-valve not tripped) |

## Critical Path

`T001 → T002 → T010 → T011 → T007 → T009` (baseline → provision → probe → catalog → cadence → ADR wiring). #281 (US1, T003–T006) runs fully parallel off the critical path as the independent MVP.

## Agent Load Balance

- `senior-backend-engineer`: 7 tasks (docs/template/config authoring) — heaviest, but all low-complexity markdown/config.
- `tester`: 5 tasks (validation/smoke/sweeps).
- `devops`: 4 tasks (CI workflow + provisioning).
- `security-analyst`: 2 tasks (gitleaks coverage probe + gap assessment).

No bottleneck agent on the critical path (it spans devops → security-analyst → senior-backend-engineer). Slack exists via the independent #281 MVP lane.
