---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-03
    status: APPROVED_WITH_CONCERNS
    notes: "Plan scope matches spec/PRD exactly — both stories covered, all 6 Out-of-Scope boundaries respected (zero US-1/Model-B re-entry, no maestro-heatmap/schema/SARIF change, repo-verified). FR-003 backfill + Decision C PDF scoping are in-bounds (pre-approved binding FR + correct narrowing to table-bearing reports; two excluded sample-reports confirmed table-less). Delivery gate (Closes #312 #313 + merge release #314 + deliver-release gate) carried forward verbatim and verified #314 OPEN. Stories independent (disjoint file sets); story-label traceability preserved. 0 BLOCKING / 0 HIGH / 0 MEDIUM / 2 LOW (doc hygiene: mobile-banking-app rationale + Out-of-Scope omission of excluded targets — folded via Decision C correction). Full review .aod/results/product-manager.md."
  architect_signoff:
    agent: architect
    date: 2026-06-03
    status: APPROVED_WITH_CONCERNS
    notes: "Technically sound; every cited path/line verified against live repo. ALL 5 PRD-stage Architect recs faithfully folded (MEDIUM-2 script-emit counts, MEDIUM-3 dedicated CI job, LOW-1 regen-first, LOW-2 no gated-set expansion, no-new-ADR). 0 BLOCKING / 0 HIGH / 2 MEDIUM / 6 LOW. MEDIUM-1 (mobile-banking-app PDF is byte-identical = NO drift; CI paths over-included 3 render surfaces + omitted the real author populate-maestro-coverage.py) FOLDED → Decision C 'likely no-op' + drift-audit drop, Decision A two-tier paths. MEDIUM-2 (agentic_app golden is table-less → all-empty only; a NEW partial-MAESTRO fixture is required for the mixed-count FR-002/SC-002) FOLDED → Decision B + Carry-Forward. LOW-3 (ADR-022 governs mmdc prereq, not CI-job shape), LOW-4 (backfill locality protects heatmap/FR-004), LOW-5 (sample-report populate target), LOW-6 (update-agent-context.sh absent), LOW-7 (byte-gate is local not CI), LOW-8 (most_exposed_count) — all folded. Determinism, FR-004 local-backfill protection, dedicated-job design, 6 gated baselines: verified sound. Two MEDIUMs are tasks.md refinements, not a re-plan. Full review .aod/results/architect.md."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: MAESTRO Output Completeness (Round 2) — Infographic + CI Durability

**Branch**: `315-maestro-output-completeness-round-2` | **Date**: 2026-06-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/315-maestro-output-completeness-round-2/spec.md`

## Summary

Finish the two remaining F-098 follow-ups on the front-light pair. **Story 1 (US-2 / #312)**: make the `maestro-stack` infographic render all seven MAESTRO layers by fixing the *data path* — the template already specifies all-7, but `extract-infographic-data.py` does not emit the empty-layer/with-findings/total counts (they are agent-derived today), and the distribution is not backfilled to seven. **Story 2 (US-3 / #313)**: lock the 7-row guarantee in CI via a **dedicated** workflow running the existing invariant test, and deterministically refresh the drifted non-gated example PDFs. No new ADR, no schema/SARIF change; reuse ADR-017/020/021/022. The two stories share no files and form one parallel wave.

## Technical Context

**Language/Version**: Python 3.11 (stdlib only) for the extractor + tests; Typst for PDF; GitHub Actions YAML for CI.
**Primary Dependencies**: existing only — `scripts/tachi_parsers.py` (`MAESTRO_LAYERS`), the Typst security-report templates, `pytest`/`pytest-timeout`. No new runtime libraries.
**Storage**: N/A (file-based artifacts: JSON spec data, markdown `threats.md`, PDF reports).
**Testing**: `pytest` — extend `test_extract_infographic_data.py` + the `maestro-stack.json` golden fixture (Story 1); wire `test_maestro_coverage_invariant.py` into CI (Story 2); `test_backward_compatibility.py` byte-gate stays green (untouched).
**Target Platform**: developer/CI (ubuntu-latest for the new job; the extractor is OS-agnostic).
**Project Type**: single project (instrumentation harness).
**Performance Goals**: N/A (per-run, 7-row table; deterministic).
**Constraints**: byte-deterministic outputs (`SOURCE_DATE_EPOCH=1700000000`); stdlib-only extractor (ADR-017); CI scope hygiene (no spurious cross-firing).
**Scale/Scope**: 2 stories, ~1 new workflow file, 1 extractor function edit + fixture/test, ≤3 non-gated PDF refresh targets.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| III. Backward Compatibility (NON-NEGOTIABLE) | ✅ PASS | No SARIF/schema change (FR-010). `maestro-heatmap` unchanged (FR-004). The 6 byte-gated baselines stay byte-identical (FR-009); only **non-gated** PDFs are refreshed, by design. New infographic JSON keys are additive (existing consumers unaffected). |
| VI. Testing Excellence | ✅ PASS | Story 1 locks new keys in the golden fixture + extractor test; Story 2 *gates* the existing invariant test in CI (its whole purpose). Test-first: assert the new `template_data` keys before/with the extractor edit. |
| VII. Definition of Done | ✅ PASS | DoD carried from PRD/spec; `/aod.analyze` gate; `CHANGELOG.md` `feat(315)` entry at delivery. |
| VIII. Observability & RCA | ✅ PASS | Root cause for Story 1 established in research (data-emission gap, not template); Story 2 makes regressions observable in CI with a layer-named failure. |
| IX. Git Workflow (NON-NEGOTIABLE) | ✅ PASS | Feature branch `315-...`; draft PR #316; conventional commits; squash title `feat(315):`. |
| X. Product-Spec Alignment (NON-NEGOTIABLE) | ✅ PASS | PM sign-off on spec complete (APPROVED_WITH_CONCERNS, MED-1 folded); this plan submitted for PM + Architect dual sign-off. |

**No violations. Complexity Tracking not required.** The only net-new artifact is one ~25-line dedicated CI workflow (the established `tachi-mmdc-preflight.yml` per-concern idiom). The Story-1 change adds three computed fields to an existing deterministic payload — it *reduces* nondeterminism (moves counting out of the LLM agent), not adds complexity.

## Resolved Plan-Stage Decisions

The spec's Assumptions + Open Questions (and the PRD's Q1/Q2/Q4) are resolved here.

### Decision A — CI mechanism: a DEDICATED workflow (resolves spec Q-C1 / FR-005/FR-006)
**Decision**: Add a new workflow `.github/workflows/tachi-maestro-coverage.yml`, modeled on `tachi-mmdc-preflight.yml` — `ubuntu-latest`, `actions/setup-python@v5` (3.11), `pip install pytest pytest-timeout`, invocation `python -m pytest tests/scripts/test_maestro_coverage_invariant.py -v`. **Do NOT fold into `tachi-pytest.yml`.**
- **Trigger `on.pull_request.paths` (lock-step with the invocation), two tiers** (Architect MEDIUM-1 — the test reads *committed* `examples/**/threats.md`, so only changes that alter those static files are regression-necessary):
  - *Regression-necessary*: `tests/scripts/test_maestro_coverage_invariant.py`, `examples/**/threats.md`, `scripts/tachi_parsers.py` (`MAESTRO_LAYERS`), `scripts/populate-maestro-coverage.py` (**the tool that rewrites example tables** — the real author), `.github/workflows/tachi-maestro-coverage.yml`.
  - *Defense-in-depth (optional)*: `scripts/extract-report-data.py`, `.claude/agents/tachi/orchestrator.md`, `templates/tachi/security-report/maestro-findings.typ` — these author/parse the *production* matrix but cannot change a committed example `threats.md`, so they are belt-and-suspenders, not strictly necessary. tasks.md finalizes the exact list.
- **Rationale**: `tachi-pytest.yml` is semantically "init.sh substitution + asset-tag hardening on a macOS-3.2/ubuntu-5 bash matrix" (verified header L38–47 lock-step lesson). The MAESTRO invariant has nothing to do with bash compatibility, would needlessly run on a 2-OS matrix, and would broaden a tightly-scoped trigger surface (NFR-4 risk). A dedicated single-OS job gives correct triggers and a self-explaining `MAESTRO coverage invariant` check name. Unanimous Architect (MEDIUM-3) + Team-Lead (M-2) recommendation; `tachi-mmdc-preflight.yml` precedent.
- **F-250 lock-step rule applies regardless**: any future MAESTRO test/surface addition updates BOTH `paths:` and the pytest invocation in the same commit.

### Decision B — maestro-stack data emission + defensive backfill (resolves FR-001/FR-002/FR-003)
**Decision**: In `scripts/extract-infographic-data.py`, the `maestro-stack` `template_data` block (≈L1937–1965):
1. **Backfill (FR-003)**: build the layer distribution over all seven `MAESTRO_LAYERS` (imported from `tachi_parsers.py` — no new hard-coded list, ADR-019), filling any layer absent from the parsed table with `finding_count = 0`. This makes all-7 robust even against a table-less / pre-F-098 input.
2. **Emit counts (FR-002)**: compute and add to `template_data` — `layers_with_findings = count(finding_count > 0)`, `empty_layers = 7 − layers_with_findings`, `layer_count = 7`. The agent then *renders* these (no LLM counting).
3. **Lock — two fixtures (Architect MEDIUM-2)**: regenerate `tests/scripts/fixtures/golden/maestro-stack.json` — its source `exec_arch/agentic_app` fixture is **table-less**, so the regenerated golden legitimately covers only the **all-empty** case (`layers_with_findings=0, empty_layers=7`). To test the **mixed** case (FR-002/SC-002), tasks.md MUST author a **new partial-MAESTRO fixture** (~3-of-7 layers with findings) and assert `layers_with_findings=3 / empty_layers=4 / layer_count=7 / sum==7` against it. Extend `tests/scripts/test_extract_infographic_data.py` for both.
4. **Agent directive (FR-002 intent)**: add a one-line instruction in `.claude/agents/tachi/threat-infographic.md` that the maestro-stack `{empty_layers}`/`{layers_with_findings}`/`{layer_count}` placeholders MUST be taken from the emitted JSON, not recomputed.
- **Backfill locality (FR-004 protection, Architect LOW-4)**: the backfill + count fields MUST live **only in the `maestro-stack` `template_data` block**, NOT in the shared `extract_maestro_data` — `maestro-heatmap.json` also carries `maestro_layer_distribution` (currently `[]`); backfilling the shared function would mutate the heatmap golden and violate FR-004.
- **Rationale**: ADR-017 — stdlib, shared parser, `json.dumps(..., sort_keys=True, indent=2)` (new integer keys sort deterministically). The template (`infographic-maestro-stack.md`) already specifies all-7 + muting, so **no template change** is required; this is purely a data-path fix. `maestro-heatmap` is untouched (FR-004).

### Decision C — non-gated PDF refresh: MAESTRO-table-bearing set, regen-order fixed (resolves FR-008 / spec Assumption / PRD Q-D1)
**Decision**: The refresh set is the **non-gated reports that carry a MAESTRO table and whose PDF is stale relative to its now-7-row `threats.md`** (F-098 completed these `threats.md` to 7 rows but regenerated only the 6 gated baselines):
| Target | Note |
|--------|------|
| `examples/agentic-app/sample-report/security-report.pdf` (+`.baseline`) | `.baseline` ≈365 KB off its `.pdf`; threats.md already 7/7 (F-098) — **confirmed-drift target** |
| `examples/maestro-reference/security-report.pdf` (loose) | ≈307 KB off; the **gated `.baseline` stays byte-identical** (untouched) — **confirmed-drift target** |
| `examples/mobile-banking-app/sample-report/security-report.pdf` | ⚠ **likely no-op** — the PDF is **byte-identical to its `.baseline` today** (Architect MEDIUM-1); the drift-audit verifies and **DROPS it** if there is no real drift |

- **Order (Architect LOW-1)**: for each *confirmed-drift* target, run `scripts/populate-maestro-coverage.py` on the upstream `threats.md` **first** (idempotent — already 7/7, normalizes ordering/heading), then regenerate the PDF under `SOURCE_DATE_EPOCH=1700000000`, then **manually diff** to confirm only MAESTRO row/order churn (FR-008 `[MANUAL-ONLY]`). For agentic-app the populate target is the **`sample-report/threats.md`** that builds the refreshed PDF — not the divergent top-level `examples/agentic-app/threats.md` (Architect LOW-5). The drift-audit (Carry-Forward) classifies each candidate (MAESTRO-churn vs no-drift) and drops no-drift targets before any regen.
- **Excluded**: `examples/consumer-agent-app/sample-report` and `examples/predictive-ml-app/sample-report` are **table-less** (F-098 Decision E) — no MAESTRO matrix to refresh; any drift there is unrelated to this feature and out of scope. The exact final set + a byte/`git` drift audit is pinned in tasks.md.
- **Q-D1 resolved**: do **not** promote any refreshed PDF into the byte-gated `BASELINE_EXAMPLES` set (their content is changing in-feature; gating them would couple this feature to byte-stability of files it is editing).

### Decision D — No new ADR; no schema/SARIF change (resolves spec Assumption)
**Decision**: Reuse **ADR-017** (deterministic infographic extraction), **ADR-020** (MAESTRO classification), **ADR-021** (SOURCE_DATE_EPOCH determinism). The dedicated-CI-job *shape* follows the **`tachi-mmdc-preflight.yml` file precedent** (a precedent, not an ADR); **ADR-022** is cited only for the mmdc/Typst toolchain prerequisite used when regenerating PDFs (Architect LOW-3 — ADR-022 is "mmdc as hard prerequisite," not a CI-job architecture). `schemas/finding.yaml` stays 1.9; no SARIF field change. The only ADR-bearing piece (Model B) left with #311. F-098 precedent (`delivery.md:81`): "no new ADR required."

### Decision E — invariant test wiring hygiene (resolves FR-007)
**Decision**: Remove the "intentionally NOT wired into CI" docstring note (`test_maestro_coverage_invariant.py:25–27`) when the dedicated job lands; confirm the job runs green against the current example set. The test is unchanged otherwise (already heading-level-agnostic, `test-output/`-excluding, sources `MAESTRO_LAYERS` from `tachi_parsers`).

## Project Structure

### Documentation (this feature)
```
specs/315-maestro-output-completeness-round-2/
├── plan.md              # This file
├── spec.md              # PM-approved feature spec
├── research.md          # Research findings (already complete — Phase 0)
├── data-model.md        # maestro-stack template_data schema (Phase 1)
├── quickstart.md        # Verification runbook (Phase 1)
├── contracts/           # data-shape + CI-job contracts (Phase 1; adapted — no HTTP API)
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # /aod.tasks output (next sub-step)
```

### Source Code (files touched)
```
# Story 1 — US-2 / #312 (maestro-stack infographic completeness)
scripts/extract-infographic-data.py                         # FR-001/002/003: backfill to 7 + emit empty_layers/layers_with_findings/layer_count
tests/scripts/fixtures/golden/maestro-stack.json            # FR-002: regenerated golden with new keys
tests/scripts/test_extract_infographic_data.py              # FR-002: assert new keys (+ empty-layer case)
.claude/agents/tachi/threat-infographic.md                  # FR-002: 1-line "consume emitted counts" directive
scripts/tachi_parsers.py                                    # READ-ONLY: import MAESTRO_LAYERS (no change)
templates/tachi/infographics/infographic-maestro-stack.md   # READ-ONLY: already specifies all-7 (no change expected)

# Story 2 — US-3 / #313 (CI durability + non-gated PDF refresh)
.github/workflows/tachi-maestro-coverage.yml   (NEW)        # FR-005/006: dedicated MAESTRO invariant job
tests/scripts/test_maestro_coverage_invariant.py            # FR-007: remove "not wired" docstring note
examples/agentic-app/sample-report/security-report.pdf(.baseline)      # FR-008: deterministic refresh
examples/mobile-banking-app/sample-report/security-report.pdf(.baseline)  # FR-008
examples/maestro-reference/security-report.pdf              # FR-008: loose PDF (gated .baseline untouched)
examples/**/threats.md                                      # FR-008: populate-maestro-coverage.py normalize (idempotent) on refresh targets
scripts/populate-maestro-coverage.py                        # READ-ONLY: F-098 regeneration harness (run, not edited)
tests/scripts/test_backward_compatibility.py                # UNCHANGED: 6 gated baselines stay byte-identical

# Cross-cutting
CHANGELOG.md                                                # feat(315) entry (delivery)
```

**Structure Decision**: Single-project instrumentation harness; no new module boundaries. Story 1 is a contained edit to one extractor function + its fixture/test; Story 2 adds one sibling CI workflow and regenerates artifacts. No new system components — the system-design auto-scaffold (Step 6) correctly **skips** (no `## Components`/`## Data Flow`/`## Tech Stack` canonical sections, matching the F-098 precedent for a polish feature).

## Technical Approach

**Story 1 (US-2 / #312) — infographic data emission.** The maestro-stack flow is `threats.md Section-6 table → parse_maestro_layer_distribution → maestro-stack template_data (JSON) → agent renders the template`. The fix is one point on this line: in the `template_data` assembly, normalize the distribution to the canonical seven (backfill zeros) and add the three aggregate counts. Determinism is preserved by ADR-017's `sort_keys=True` JSON. The golden fixture is regenerated and the extractor test asserts the new keys against a fixture with ≥1 empty layer (proving counts are correct, not just present). The agent directive change ensures the rendered sidebar numbers come from the emitted JSON.

**Story 2 (US-3 / #313) — CI gate + PDF refresh.** Two independent sub-streams:
1. *CI gate*: a new dedicated workflow runs the existing invariant test on MAESTRO-relevant path changes, failing with the missing layer ID(s). Remove the test's self-documented "not wired" note. Verify green against the current example set.
2. *PDF refresh*: for the three MAESTRO-table-bearing non-gated targets, run `populate-maestro-coverage.py` on `threats.md` (idempotent normalize) then regenerate the PDF deterministically (`SOURCE_DATE_EPOCH`), confirming only MAESTRO row/order churn. The 6 gated baselines are not touched and the backward-compat byte test stays green. PDF regeneration uses the existing Typst (+ mmdc for attack-path pages) toolchain; tasks.md records the toolchain prerequisite.

## Phase 0: Outline & Research

**Complete.** `research.md` consolidates KB Entry 11 (F-098 doctrine), the deterministic-extraction ADRs (017/021), the dedicated-CI-job precedent (`tachi-mmdc-preflight.yml`), the exact data-emission gap (4-key payload, missing 3 counts), the non-gated PDF inventory, and the F-250 lock-step lesson. **No NEEDS CLARIFICATION markers remain** — all spec/PRD open questions are resolved in Decisions A–E above.

## Phase 1: Design & Contracts

**Prerequisites:** research.md complete ✓. Generated this phase:
- **`data-model.md`** — the `maestro-stack` `template_data` schema (existing 4 keys + 3 new count fields), the MAESTRO layer-distribution entity (always 7), and the coverage invariant.
- **`contracts/`** — adapted (no HTTP API): `maestro-stack-template-data.contract.md` (the additive JSON-payload contract Story 1 must satisfy + golden-fixture lock) and `tachi-maestro-coverage-ci.contract.md` (the dedicated job's trigger-paths ⇄ invocation lock-step + layer-named failure contract).
- **`quickstart.md`** — verification runbook: generate the maestro-stack JSON for an empty-layer fixture and assert all-7 + counts; run the invariant test locally and force a <7-row failure; regenerate a non-gated PDF deterministically and diff.
- **Agent context update** — N/A in this template version: `.aod/scripts/bash/update-agent-context.sh` does not exist (Architect LOW-6). No new technology to register; CLAUDE.md is unchanged.

Post-design Constitution re-check: still PASS (additive JSON keys + one dedicated CI job; no new boundaries, no schema change).

## Risks & Sequencing

**One parallel wave** (Team-Lead M-1): Story 1 (US-2) ∥ Story 2 (US-3) — zero shared files. Within Story 2, the CI gate and the PDF refresh are themselves independent. Neither story depends on US-1/#311.

| # | Risk | Likelihood | Mitigation |
|---|------|-----------|------------|
| R1 | Backfill/new keys change the golden fixture or surprise the agent renderer | Med | Regenerate `maestro-stack.json` intentionally; the only consumer is the infographic agent, which already expects all-7; additive keys can't break existing readers |
| R2 | Non-gated PDF refresh surfaces *unrelated* (non-MAESTRO) drift | Med | Scope refresh to MAESTRO-table-bearing reports (Decision C); `[MANUAL-ONLY]` diff; deterministic `SOURCE_DATE_EPOCH`; flag (don't silently absorb) any non-MAESTRO drift |
| R3 | CI job `paths:` misses a render surface → false-green | Med | Lock-step rule; `paths:` enumerates all author/parse surfaces (orchestrator directive, parser, extractor, Typst, examples, test, workflow) |
| R4 | PDF regeneration toolchain (Typst + mmdc) unavailable locally | Low | tasks.md records the toolchain prerequisite + deterministic env; gated baselines prove the pipeline still reproduces byte-identically |
| R5 | Accidental change to a gated baseline | Low | Do not touch the 6; the `test_backward_compatibility.py` byte-gate catches drift on a **local/build-time** run — note it is NOT wired into CI (Architect LOW-7), so run it during build/DoD |

## Carry-Forward to tasks.md (from plan sign-off)

- **Delivery gate (PM LOW-2)**: the delivering PR MUST carry `Closes #312 #313`; the umbrella #315 closes when both land; **merge release PR #314 (v4.39.0) before/alongside** branch delivery; verify the F-315 delivery itself yields a release-please PR (deliver-release gate).
- **Lock-step CI**: the new job's `paths:` ⇄ pytest invocation kept in sync in the same commit.
- **Drift audit**: a `git`/byte audit task finalizes the exact non-gated PDF set and classifies each diff (MAESTRO row/order vs other) before refresh.
- **Golden-fixture + extractor test** updated for the three new keys, including an empty-layer assertion case.
- **Story-label mapping** carried: spec Story 1 ↔ PRD US-2 ↔ #312; spec Story 2 ↔ PRD US-3 ↔ #313 (PM MED-1).
- **`[MANUAL-ONLY]`** non-gated PDF diff verification is its own task (not folded into the regen task).
- **CHANGELOG** `feat(315)` entry at delivery.

**From the Architect plan review (must fold into tasks.md):**
- **(MEDIUM-2) New partial-MAESTRO fixture** — author a ~3-of-7-layer fixture + a mixed-count assertion (`layers_with_findings=3 / empty_layers=4 / layer_count=7`); the regenerated `agentic_app`-derived golden covers the all-empty case only and does NOT prove correct counting on a mixed distribution.
- **(MEDIUM-1) Drift audit drops no-drift targets** — `mobile-banking-app/sample-report` PDF is byte-identical to its baseline today; verify and DROP if no real drift. Confirmed-drift set is agentic-app/sample-report + maestro-reference (loose `.pdf`).
- **(MEDIUM-1) CI `paths:` reconciliation** — include `scripts/populate-maestro-coverage.py` (the real example-table author); the production render/parse surfaces are optional defense-in-depth, not regression-necessary.
- **(LOW-4) Backfill locality** — backfill in the maestro-stack `template_data` block only, never the shared `extract_maestro_data` (protects the heatmap golden / FR-004).
- **(LOW-5) Populate target** — for agentic-app, target the `sample-report/threats.md`, not the divergent top-level file.
- **(LOW-8, optional)** — emit `most_exposed_count` for full sidebar determinism, OR document it is intentionally left agent-rendered and outside FR-002's enumerated set.

## Out of Scope (carried from spec)

- **US-1 Model B two-state (clean vs n/a)** → carved to #311 (its own ADR-bearing feature).
- `maestro-heatmap` changes; `threat-report.md` per-layer roster; SARIF/schema changes; frozen `examples/**/test-output/**` snapshots; changing the F-098 Model A all-7 guarantee.
