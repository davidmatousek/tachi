---
artifact: feasibility-check
feature_id: 217
owner: team-lead
date: 2026-07-01
prd_number: 217
status: draft
estimate:
  planning_days: 1.0
  floor_days: 0.5
  ceiling_days: 2.0
---

# Team-Lead Feasibility Check — F-217 Detect-Images Duplicate Cleanup

**PRD**: `docs/product/02_PRD/217-detect-images-duplicate-cleanup-2026-07-01.md` (BLP-06 Wave 3, P2, Feature)
**Status**: APPROVED_WITH_CONCERNS (no timeline veto, no capacity veto)
**Full review**: `.aod/results/team-lead.md` (2026-07-01 run)

## Authoritative Estimate

| Bound | Days | Basis |
|-------|------|-------|
| Floor | 0.5 | Code + tests only; OQ-2 defers US-2; terse docs |
| Planning (central) | 1.0 | Full scope US-1+US-2+US-3 + AOD pipeline overhead |
| Ceiling | 2.0 | Pre-existing-pair double-gate subtlety, or gated-suite / security-scan / simplification iterations |

Bottom-up derivation: US-1 code (flag + double-gate in `detect_images` + thread via single call site L2164) ~2.5–3h; US-1 tests (mature harness: `_build_byte_probe_fixture`, `_write_minimal_png/_jpeg`, `run_extract`) ~2h; US-2 dogfood + local verification ~0.5–1h (near-zero if OQ-2 defers); US-3 docs ~0.5–1h. Sum ≈ 0.85 eng-day pure work + AOD gates ≈ 1.0 central. PM placeholder (0.5/1.0/2.0) independently CONFIRMED — FR-012 satisfied.

## Complexity — LOW, bounded

`build_parser()` +~4 lines; `detect_images()` +~25–40 net lines with the double-gate needed in BOTH the recovery-write block (L1512–1525) AND the pre-existing-pairs/best-match block (L1507–1510) — the one spot needing genuine care. `shutil` already imported; `filecmp` is one stdlib import (code-economy rung 3, no new dependency).

## Key Finding — PRD R-1 is OVERSTATED

The US-2 target dir `examples/agentic-app/test-output/2026-04-19T03-20-30/` is consumed by **no test**: `agentic-app` is NOT in `test_backward_compatibility.py:BASELINE_EXAMPLES` (line 19 explicitly excludes it); the byte-identity test reads `examples/{name}/` top-level, never the nested snapshot; `test_maestro_coverage_invariant.py:57–61` globs OUT `test-output/`; the suite is local-only (wired into no CI). The only textual hit (`generate-threats-sarif.py:405`) uses the timestamp as a SARIF run-id default, not a file dependency. All 6 pairs byte-identical (~6.75 MB reclaimable). OQ-2 therefore reduces to a pure preserve-as-historical-fixture vs dogfood judgment.

## Wave Plan & Assignment

Single wave (multi-wave rejected — coordination overhead disproportionate to <100 net lines). Sequencing: US-1 first → US-2 (gated on OQ-2) and US-3 in parallel after. **senior-backend-engineer authors BOTH code and co-located pytest cases** (the `tester` agent is BDD/Gherkin — poor fit for a white-box pytest module); **code-reviewer** focused on the SC-3/AC-1d/AC-1e safety invariant. Sibling BLP-06 W3 #295: independent, no shared files, no scheduling coupling.

## Non-Blocking Concerns (carry to plan/build)

1. Agent fit: senior-backend-engineer for code+tests; code-reviewer for the safety gate.
2. Soften R-1/AC-2a wording at plan stage per the finding above.
3. Build-stage gotcha: the F-248/F-256 gated harness clones committed HEAD — commit before running the gated subset; byte-identity suite is local-only + Typst 0.14.2 installed (~1–2 min run), so US-2 verification must not chase a phantom red.
4. US-2's AC-2b gate creates NO schedule risk — it can only shorten scope toward the 0.5d floor.
