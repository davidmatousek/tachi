---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-07-01
    status: APPROVED
    notes: "9/9 FRs designed, 11/11 ACs traceable to test plan/gated procedures, 3/3 stories with priority preserved; all 6 PRD Out items respected. 2 non-blocking observations. Details: .aod/results/product-manager.md"
  architect_signoff:
    agent: architect
    date: 2026-07-01
    status: APPROVED_WITH_CONCERNS
    notes: "Wiring verified against live code; all 9 pair configs traced — chosen/emitted file never deletable (INV-2 structural); 4 PRD constraints honored; stdlib choices sound. 4 items (2 MED / 1 LOW / 1 NIT) folded into plan post-review: MED-1 try/except broadened to whole cleanup attempt, MED-2 deletion-failure test added to test plan, LOW-1 structural proof stated. Details: .aod/results/architect.md"
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: Detect-Images Duplicate Cleanup — Opt-In Mislabeled-Image Removal

**Branch**: `217-detect-images-duplicate-cleanup` | **Date**: 2026-07-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/217-detect-images-duplicate-cleanup/spec.md`
**PRD**: `docs/product/02_PRD/217-detect-images-duplicate-cleanup-2026-07-01.md` (Approved v1.1) · **Feasibility**: [feasibility-check.md](feasibility-check.md) (0.5 / 1.0 / 2.0 eng-days)

## Summary

Add an explicit opt-in `--cleanup-mislabeled-images` flag to `scripts/extract-report-data.py` that deletes a mislabeled infographic image (extension contradicts magic-byte content — the `gemini-2.5-flash-image` fallback-era signature) only under a double gate: the flag is present AND a correctly-labeled counterpart exists that is byte-identical (`filecmp.cmp(..., shallow=False)`). Deletion is wired into BOTH moments — the pre-existing-pairs branch (primary legacy case) and the recovery-write branch (with a `pre_existed` guard closing the cross-swap edge). Without the flag, behavior is byte-identical to today. Follow-ons: gated in-repo dogfood cleanup of the 6 legacy snapshot pairs (US-2, path-invariance proof) and report-assembly reference documentation of the sanctioned cleanup path (US-3).

## Technical Context

**Language/Version**: Python 3 (stdlib-only script; no version bump — matches existing `extract-report-data.py` baseline)
**Primary Dependencies**: none new. `shutil` already imported; add stdlib `filecmp` import (ADR-017 stdlib-only constraint holds)
**Storage**: local filesystem only (assessment directories); no DB, no network
**Testing**: pytest — `tests/scripts/test_extract_report_data.py` (subprocess CLI path via `run_extract`) + `tests/scripts/test_extractor_contract_fixes.py` (direct-call signature compat). Both are local-only suites, NOT in the CI pytest gate (`tachi-pytest.yml` runs init/template suites only)
**Target Platform**: macOS/Linux CLI (adopter machines running the report pipeline)
**Project Type**: single — one script, its tests, one skill-reference doc surface
**Performance Goals**: negligible — ≤6 stems per directory; byte-comparison only on flag runs against ~1 MB images
**Constraints**: no-flag runs byte-identical across output/files/stderr/exit code (FR-001, Principle III); two-positional-arg caller compatibility (`cleanup` as defaulted kwarg, FR-006); deterministic emitted output preserved (ADR-021); zero-byte candidate validation and template-relative path emission unchanged
**Scale/Scope**: ~40 net lines in `scripts/extract-report-data.py`, ~9 new test cases + one harness parameter, one docs subsection; 6 in-repo file deletions (~6.75 MB)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Result |
|---|---|---|
| I General-Purpose Architecture | No domain-specific logic added to core | PASS — generic image-hygiene mechanics in an existing generic extractor |
| II API-First Design | N/A — no API surface; CLI contract documented in `contracts/cli-contract.md` | PASS (N/A) |
| III Backward Compatibility (NON-NEGOTIABLE) | No forced migration; opt-in only | PASS — flag is opt-in, never default; no-flag byte-identical (FR-001); cleanup is "opt-in, never forced" by design |
| IV Concurrency & Data Integrity | N/A — single-process local file operation; per-file try/except handles FS races proportionally (R-3) | PASS (N/A) |
| V Privacy & Data Isolation | N/A — no data leaves the machine; deletions are local | PASS (N/A) |
| VI Testing Excellence | Tests before completion; safety negatives each get a dedicated case | PASS — test-first ordering in tasks; AC-1a–1h automated (FR-007); new logic fully covered |
| VII Definition of Done (NON-NEGOTIABLE) | 3-step validation planned | PASS — delivery via PR #351 (squash-merge = "production" for a template repo), full local suites, US-2 dogfood = real-world usage validation |
| VIII Observability & RCA | Cleanup actions observable | PASS — one stderr record per deletion/failure (FR-005); loud failure, silent success only when nothing eligible |
| IX Git Workflow (NON-NEGOTIABLE) | Feature branch + PR | PASS — branch `217-detect-images-duplicate-cleanup`, draft PR #351 |
| X Product-Spec Alignment (NON-NEGOTIABLE) | Approved PRD → PM-approved spec → this plan | PASS — PRD v1.1 Triad-approved; spec PM sign-off APPROVED 2026-07-01 |

**Initial check**: PASS, no violations. **Post-design re-check**: PASS — design adds no new dependencies, no new surfaces, no debt requiring justification. Complexity Tracking left empty.

## Project Structure

### Documentation (this feature)

```
specs/217-detect-images-duplicate-cleanup/
├── plan.md              # This file (/aod.project-plan output)
├── research.md          # Research + Phase 0 decision log
├── data-model.md        # Entities, deletion state machine, invariants
├── quickstart.md        # Run/verify/dogfood commands
├── contracts/
│   └── cli-contract.md  # CLI flag, Python signature, stderr record, harness contracts
├── checklists/
│   └── requirements.md  # Spec quality checklist (complete)
├── feasibility-check.md # Team-lead estimate (define stage)
└── tasks.md             # Task breakdown (/aod.tasks output — next step)
```

### Source Code (repository root)

```
scripts/
└── extract-report-data.py                    # ALL production changes live here:
                                              #   imports (+filecmp), detect_images (both cleanup moments),
                                              #   build_parser (+flag), main (threading)

tests/scripts/
├── test_extract_report_data.py               # run_extract(+extra_args); new AC-1a–1h cases in the #215 section
└── test_extractor_contract_fixes.py          # UNTOUCHED — its :200 two-positional call is the compat oracle

.claude/skills/tachi-report-assembly/references/
├── typst-artifacts.md                        # US-3 primary doc surface (legacy duplicate pairs + sanctioned cleanup)
└── typst-template-contract.md                # optional one-line cross-reference only

examples/agentic-app/test-output/2026-04-19T03-20-30/
└── threat-*.jpg (×6)                         # US-2 dogfood deletions (gated per AC-2b)
```

**Structure Decision**: Single-project layout; no new files in production code. The feature deliberately concentrates in `extract-report-data.py` (code economy: the probe, stems, and selection logic already live there — a standalone cleanup script is explicitly out of scope).

## Components

- **`_file_format(path)` probe** (existing, L1449–1460): unchanged; supplies `content_format` for the mislabeled predicate.
- **`_maybe_delete_mislabeled(mislabeled_fp, counterpart_fp)` helper** (new, ~12 lines): the single shared implementation of gate 2 — verifies counterpart exists, is non-zero, and `filecmp.cmp(mislabeled_fp, counterpart_fp, shallow=False)`; on pass, deletes `mislabeled_fp` and writes one stderr record. The **entire per-candidate cleanup attempt (probe + compare + delete) is wrapped in `try/except OSError`** logging failure to stderr — a comparison-time OSError must be as harmless as a deletion-time one, so cleanup can never fail extraction (FR-005/INV-3; Architect MED-1). Returns whether deletion happened (for test-friendly stderr accounting). Both moments call this one helper so the predicate cannot drift (INV-1). **Structural INV-2 guarantee**: `chosen` is by definition self-consistent (content matches extension), so it can never satisfy the mislabeled predicate — no iteration order in Moment A can delete the emitted file (Architect LOW-1).
- **`detect_images(target_dir, template_dir, cleanup=False)`** (modified): defaulted kwarg per FR-006. One `filecmp.clear_cache()` at entry when `cleanup` is on (defensive, per research). Two call sites into the helper:
  - **Moment A — pre-existing pairs** (self-consistent branch, L1506–1510): after `chosen` is selected, when `cleanup`, probe the *other* candidates of the stem; for each mislabeled one, its correctly-labeled counterpart is resolved by stem + canonical extension for its content format; call the helper. Covers AC-1a (delete), AC-1d (non-identical → skip), AC-1h (self-consistent others → not mislabeled → skip), AC-1e (nothing mislabeled → no-op).
  - **Moment B — recovery write** (L1512–1525): record `pre_existed = target_path.exists()` BEFORE `shutil.copyfile`; after the copy, when `cleanup` AND NOT `pre_existed`, call the helper (its byte-identity check doubles as copy-success verification). Covers AC-1c (write→verify→delete), AC-1f (truncated copy → no delete, exit 0), AC-1g (cross-swap: sibling pre-existed → no delete).
- **`build_parser()`** (modified, L2020–2044): `parser.add_argument("--cleanup-mislabeled-images", action="store_true", help=...)` following existing kebab/sentence-fragment conventions.
- **`main()`** (modified): thread `cleanup=args.cleanup_mislabeled_images` at the single production call site (L2164).

## Data Flow

```
per stem: glob candidates (.jpg/.png, exists, size>0)
  → self-consistent candidate found?
     ├─ yes → chosen = it
     │        [cleanup ON] Moment A: other candidates → mislabeled? → counterpart byte-identical? → delete + stderr record
     └─ no  → Moment B recovery: probe → pre_existed := sibling.exists() → copyfile corrected sibling → chosen = sibling
              [cleanup ON] NOT pre_existed AND byte-identical? → delete original + stderr record
  → emit template-relative path of chosen (UNCHANGED by cleanup — INV-2 path-invariance)
```

Full deletion state machine and invariants: [data-model.md](data-model.md). Contracts (CLI, Python signature, stderr records, harness): [contracts/cli-contract.md](contracts/cli-contract.md).

## Tech Stack

Python 3 stdlib only: `argparse` (flag), `shutil` (existing copy), `filecmp` (new import — byte-identity gate), `pathlib` (existing). No new dependencies (ADR-017); pytest for tests (existing harness).

## Test Plan (test-first, Principle VI)

Pre-work: record LITERAL pre-state pytest totals for both extractor modules (KB Entry 15).

Harness: extend `run_extract` with `extra_args=None` (appended to argv) — existing call sites untouched.

| Test case (new, in the #215 section of `test_extract_report_data.py`) | AC | Asserts |
|---|---|---|
| flagged run deletes mislabeled jpg with byte-identical png | AC-1a | `.jpg` gone, `.png` emitted, exactly one deletion stderr line |
| unflagged run byte-identical | AC-1b | both files persist, stdout/typ output byte-identical to pre-feature fixture run, no cleanup stderr |
| recovery: no sibling yet → write, verify, delete | AC-1c | sibling written first, original deleted, order provable via record content |
| non-identical pair untouched | AC-1d | both persist, no deletion record |
| all-correct directory no-op | AC-1e | zero deletions, zero cleanup stderr |
| truncated recovery copy → no delete, exit 0 | AC-1f | monkeypatched/short `copyfile`; original persists; returncode 0 |
| cross-swapped pair → no delete | AC-1g | both mislabeled opposite directions; both persist |
| legitimate mixed self-consistent pair untouched | AC-1h | different-content jpg+png both persist |
| deletion failure is best-effort (monkeypatched `os.remove`/`Path.unlink` raises `OSError`) | FR-005 / INV-3 (Architect MED-2) | file persists, exactly one failure stderr line, returncode 0, emitted output unchanged |

Regression oracle: `test_extractor_contract_fixes.py` runs UNMODIFIED (its :200 two-positional call + :211 `test_existing_image_flags_unchanged` prove FR-006); existing #215 tests (:242, :284, :316) stay green.

## US-2 Dogfood Procedure (gated, AC-2a/AC-2b)

1. Generate `report-data.typ` for the snapshot dir → save as `before.typ` (pre-cleanup baseline).
2. Run the flag against `examples/agentic-app/test-output/2026-04-19T03-20-30/` → expect exactly 6 deletions (the 6 mislabeled `.jpg`).
3. Regenerate → `after.typ`; **byte-compare before/after = path-invariance proof**; extractor test modules green.
4. Commit the 6 deletions. AC-2b fallback: if any verification step surfaces a real snapshot-image consumer, defer US-2 with an Issue #217 comment instead of forcing (build stage must not chase phantom reds — byte-identity suite is local-only).

## US-3 Documentation

`typst-artifacts.md`: add a "Legacy duplicate pairs & sanctioned cleanup" note near Image File Validation / legacy extraction reference — origin (gemini-2.5-flash-image fallback era), the flag invocation, double-gate semantics, and an explicit "do NOT use raw `find … rm`". The report-assembler agent surface is NOT modified to pass the flag (OQ-1: human opt-in only).

## Build-Stage Gotchas (carried from research/feasibility)

- Commit before running the gated pytest subset — the F-248/F-256 harness clones committed HEAD.
- Extractor suites are local-only (not in `tachi-pytest.yml`); don't expect CI to exercise them — run locally and record results.
- Extractor changes are not render-coupled, but confirm `tachi-catalog-drift.yml` stays green after US-2 deletions (KB Entry 19).
- Deleting files can redden whole-tree fixtures elsewhere — verified N/A here (init-baseline-tree covers the template tree, not `examples/`), keep the check in the DoD anyway (KB Entry 2).

## Complexity Tracking

*No Constitution Check violations — table intentionally empty.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
