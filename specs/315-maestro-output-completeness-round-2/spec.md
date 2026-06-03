---
prd_reference: docs/product/02_PRD/315-maestro-output-completeness-round-2-2026-06-02.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-03
    status: APPROVED_WITH_CONCERNS
    notes: "PRD→spec traceability COMPLETE — all 4 in-scope FRs + 5 SCs mapped, all 6 Out-of-Scope boundaries honored, ZERO US-1/Model-B leakage, no scope creep. 0 BLOCKING / 0 HIGH / 1 MEDIUM / 2 LOW. MED-1 (story-label collision: spec US-1/US-2 vs PRD US-2/US-3 where US-1=carved Model B) FOLDED — added a story-label mapping note + issue-anchored FR headers (#312/#313). LOW-1 (FR-003 defensive backfill is net-new but in-bounds robustness, traced to PRD Architecture Notes + research) accepted as strengthening not widening scope. LOW-2 (PRD SC-5 PR-close is a delivery gate, not a spec SC) carried to /aod.tasks + /aod.deliver (PR Closes #312 #313; merge release #314; deliver-release gate). Both stories independent testable MVP slices; P1/P2 sound. Full review .aod/results/product-manager.md."
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: MAESTRO Output Completeness (Round 2) — Infographic + CI Durability

**Feature Branch**: `315-maestro-output-completeness-round-2`
**Created**: 2026-06-02
**Status**: Draft
**Input**: PRD 315 — MAESTRO Output Completeness (Round 2). Scope split at `/aod.define` (Q5 split valve, user-confirmed): this feature delivers US-2 (#312, maestro-stack infographic completeness) + US-3 (#313, CI durability + non-gated PDF refresh). US-1 Model B two-state annotation (#311) is carved out into its own feature and is **out of scope**.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - maestro-stack infographic shows all seven MAESTRO layers (#312) (Priority: P1)

A maintainer or adopter generates the `maestro-stack` infographic from a threat model. Even when only a few MAESTRO layers carry findings, **all seven canonical layers (L1–L7) appear as bands** in the stack, with zero-finding layers shown muted (dash) rather than omitted — so the shareable visual matches the all-7 completeness already guaranteed in the `threats.md` matrix and the PDF page (delivered by F-098). The "Layers with Findings" / "Empty Layers" counts in the infographic are accurate and reproducible.

**Why this priority**: This is the most user-visible remaining gap from F-098. The `maestro-stack` infographic is the artifact most likely to be screenshot, embedded in a slide, or shared with a prospect. If it silently drops zero-finding layers, the shareable surface contradicts the matrix and reads as "only N of 7 layers assessed" — undercutting the exact coverage-credibility F-098 fixed. It delivers standalone value: completing this one story makes every infographic henceforth complete.

**Independent Test**: Generate the `maestro-stack` infographic spec data for a fixture threat model whose MAESTRO distribution has fewer than seven finding-bearing layers (≥1 empty layer). Confirm all seven layers are represented in canonical order, empty layers are flagged for muted rendering, and the emitted empty/with-findings/total counts are correct — without touching CI or any other infographic.

**Acceptance Scenarios**:

1. **Given** a threat model whose MAESTRO layer distribution has findings in only 3 of 7 layers, **When** the `maestro-stack` infographic spec data is produced, **Then** all 7 canonical layers (L1–L7) are present in canonical order, the 4 zero-finding layers are marked as empty (for muted/dash rendering), and the data reports `layers_with_findings = 3`, `empty_layers = 4`, `layer_count = 7`.
2. **Given** a threat model with findings in all 7 layers, **When** the infographic spec data is produced, **Then** all 7 layers render with `empty_layers = 0` and no layer is muted.
3. **Given** a threat model with zero MAESTRO findings overall, **When** the infographic spec data is produced, **Then** all 7 layers are present and muted with `layers_with_findings = 0`, `empty_layers = 7` (graceful empty state, not an error or an omitted stack).
4. **Given** the same threat model input run twice, **When** the `maestro-stack` spec data is produced each time, **Then** the emitted counts and layer set are byte-identical across runs (deterministic; not dependent on the rendering agent counting).
5. **Given** the `maestro-heatmap` infographic, **When** this feature is delivered, **Then** its output is unchanged (it already renders empty cells).

---

### User Story 2 - The 7-layer guarantee is gated in CI and example artifacts are current (#313) (Priority: P2)

A maintainer changes the MAESTRO parser, the matrix renderer, or an example report. **CI automatically fails** — naming the missing layer ID(s) — if any example MAESTRO coverage matrix would render with fewer than seven canonical layers, so the F-098 guarantee cannot silently regress. Separately, the committed **non-gated** example PDFs (which drifted before F-098) are refreshed deterministically so they match current output.

**Why this priority**: This is the durability mechanism for the whole MAESTRO-completeness story (F-098 + US-1 of this cluster). Without it, a future refactor can quietly drop the guarantee with no failing check. It is a "small/quick win" with high regression-protection value, but is P2 because it protects rather than creates user-visible value. It is independently shippable and has no dependency on US-1.

**Independent Test**: Introduce a deliberate <7-row MAESTRO matrix into a test fixture and confirm the dedicated CI job fails and names the missing layer. Separately, regenerate the non-gated example PDFs deterministically and confirm the diff contains only MAESTRO row/order churn while the six byte-gated baselines remain byte-identical.

**Acceptance Scenarios**:

1. **Given** an example `threats.md` whose "Risk by MAESTRO Layer" table is missing one or more canonical layers, **When** the dedicated MAESTRO CI job runs, **Then** the job fails and the failure message names the missing layer ID(s).
2. **Given** the current example set (all matrices complete at 7 rows), **When** the dedicated MAESTRO CI job runs, **Then** it passes green.
3. **Given** a change to an unrelated file (e.g., an init.sh substitution helper), **When** CI runs, **Then** the dedicated MAESTRO job does **not** fire, and the existing pytest job's trigger surface is unchanged.
4. **Given** the non-gated example reports whose upstream `threats.md` predate the all-7 output, **When** they are refreshed (upstream `threats.md` regenerated, then the PDF), **Then** the resulting change is limited to MAESTRO row/order churn. **[MANUAL-ONLY]** visual/byte diff confirmation that no unrelated binary drift was introduced (non-gated PDFs have no automated byte-gate).
5. **Given** the six byte-gated baseline examples, **When** this feature is delivered, **Then** the backward-compatibility byte-identity test remains green (those baselines are untouched and the gated set is not expanded).

---

### Edge Cases

- **Table-less example reports**: an example `threats.md` with no "Risk by MAESTRO Layer" table is skipped by the invariant test (not failed) — intermediate-format sample reports must not produce false CI failures.
- **Pre-F-098 example threats.md**: an example whose table predates the all-7 change is brought to seven rows by the regeneration step before its PDF is refreshed — this is intended content change, not drift.
- **maestro-stack with a partial/absent distribution**: if the upstream distribution has fewer than seven rows (or none), the infographic data path still presents seven canonical layers (defensive backfill) rather than emitting an incomplete stack.
- **Optional image toolchain absent (Gemini/mmdc)**: determinism and completeness apply to the infographic **spec data**; the image-generation step remains optional/best-effort and degrades gracefully (per existing pipeline behavior).
- **Frozen `test-output/` snapshots**: excluded from both the invariant test and the PDF refresh — historical artifacts are intentionally not regenerated.

## Requirements *(mandatory)*

### Functional Requirements

> Each AC follows Given/When/Then. `[MANUAL-ONLY]` marks acceptance that cannot be automated.

> **Story-label mapping** (avoids cross-document collision): this spec's **Story 1 / FR-001–FR-004** = PRD **US-2 (#312)** infographic; this spec's **Story 2 / FR-005–FR-009** = PRD **US-3 (#313)** CI durability. PRD/GitHub **US-1 (#311) Model B is carved out** and out of scope here. The issue numbers (#312/#313) are the authoritative anchors throughout this document.

**Story 1 / PRD US-2 (#312) — maestro-stack infographic completeness:**

- **FR-001**: The `maestro-stack` infographic spec data MUST represent all seven canonical MAESTRO layers (L1–L7) in canonical order, with zero-finding layers flagged for muted/dash rendering rather than omitted.
  - *AC*: **Given** a distribution with ≥1 zero-finding layer, **When** the maestro-stack spec data is produced, **Then** all 7 layers are present in canonical order and each zero-finding layer is marked empty.
- **FR-002**: The `maestro-stack` spec data MUST emit deterministic, code-computed aggregate counts — `layers_with_findings`, `empty_layers`, and `layer_count` (=7) — so the rendered counts do not depend on the generating agent counting.
  - *AC*: **Given** identical input run twice, **When** the spec data is produced, **Then** the three counts are present, correct, and byte-identical across runs.
- **FR-003**: The `maestro-stack` data path MUST be robust to an upstream distribution with fewer than seven rows (defensive backfill to the canonical seven), so completeness does not depend on the upstream table already being complete.
  - *AC*: **Given** an upstream distribution containing fewer than 7 layer rows, **When** the spec data is produced, **Then** the output still contains all 7 canonical layers (missing ones added as empty).
- **FR-004**: The `maestro-heatmap` infographic MUST remain unchanged (it already renders empty cells).
  - *AC*: **Given** this feature is delivered, **When** the `maestro-heatmap` output is compared to its prior output for identical input, **Then** it is unchanged.

**Story 2 / PRD US-3 (#313) — CI durability + non-gated PDF refresh:**

- **FR-005**: A dedicated CI job MUST run the MAESTRO coverage-invariant test and MUST fail, naming the missing canonical layer ID(s), whenever an example MAESTRO matrix would render with fewer than seven layers.
  - *AC*: **Given** an example matrix missing ≥1 canonical layer, **When** the dedicated CI job runs, **Then** it fails and names the missing layer ID(s).
- **FR-006**: The dedicated CI job MUST be path-scoped to MAESTRO-relevant surfaces only, MUST NOT fire on unrelated changes, and MUST NOT broaden the existing pytest job's trigger surface; its trigger paths and its test invocation MUST be kept in lock-step.
  - *AC*: **Given** a change to an unrelated (non-MAESTRO) file, **When** CI runs, **Then** the MAESTRO job does not fire and the existing pytest job's `paths`/invocation are unchanged.
- **FR-007**: The invariant test's "intentionally not wired into CI" notice MUST be removed when it is wired, and the test MUST pass green against the current example set in CI.
  - *AC*: **Given** the current example set, **When** the dedicated CI job runs, **Then** it passes and the test file no longer claims to be un-wired.
- **FR-008**: Non-gated example reports MUST be refreshed deterministically — regenerate the upstream `threats.md` to the all-7 canonical table first, then regenerate the PDF under the project's deterministic build setting — limiting the change to MAESTRO row/order churn.
  - *AC*: **Given** a non-gated example whose `threats.md` predates all-7, **When** it is refreshed in the prescribed order, **Then** the `threats.md` shows seven canonical rows and the PDF reflects only that change. **[MANUAL-ONLY]** binary-diff confirmation that no unrelated drift was introduced (no automated byte-gate exists for non-gated PDFs).
- **FR-009**: The six byte-gated baseline examples MUST remain byte-identical and the byte-gated set MUST NOT be expanded by this feature.
  - *AC*: **Given** the six gated baselines, **When** the backward-compatibility byte-identity test runs, **Then** it remains green and the gated set is unchanged.

**Cross-cutting:**

- **FR-010**: This feature MUST NOT change any machine-readable schema or SARIF output, and MUST preserve the F-098 guarantee (all seven layers always rendered; the existing zero-finding "clean" annotation unchanged).
  - *AC*: **Given** the delivered feature, **When** schema/SARIF outputs and the matrix/PDF clean annotation are compared to pre-feature output, **Then** they are unchanged except for the intended MAESTRO row/order completeness.

### Key Entities

- **MAESTRO layer distribution**: the per-layer finding tally across the seven canonical layers (L1 Foundation Model … L7 Agent Ecosystem); the basis for both the infographic stack and the invariant.
- **maestro-stack template data**: the deterministic spec-data payload consumed by the infographic renderer; gains the `empty_layers` / `layers_with_findings` / `layer_count` aggregates.
- **Coverage invariant**: the rule "every example MAESTRO matrix lists all seven canonical layers," enforced by the invariant test and, after this feature, by CI.
- **Example report artifact**: an example's `threats.md` + generated PDF; classified as **byte-gated** (6 baselines, must stay byte-identical) or **non-gated** (refresh targets).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For any threat model, the `maestro-stack` infographic presents all seven MAESTRO layers, with zero-finding layers visually distinct (muted) — verified on a fixture with ≥1 empty layer.
- **SC-002**: The infographic's "Layers with Findings" / "Empty Layers" / total-layer counts are correct and reproducible (identical on repeated runs of identical input) because they are computed deterministically rather than by the rendering agent.
- **SC-003**: A MAESTRO matrix regression below seven layers is caught automatically — the dedicated CI job fails and names the missing layer ID(s) — verified by an intentional <7-row fixture.
- **SC-004**: The dedicated CI job fires only on MAESTRO-relevant changes and leaves the existing pytest job's scope untouched (no spurious cross-firing).
- **SC-005**: After the non-gated PDF refresh, the six byte-gated baselines remain byte-identical (backward-compatibility test green) and the non-gated artifacts reflect only MAESTRO row/order churn.
- **SC-006**: `maestro-heatmap` output, machine-readable schema, and SARIF are unchanged; the F-098 all-7 + clean-annotation guarantee is preserved.
- **SC-007**: Each story is independently deliverable — implementing only US-1 yields complete infographics; implementing only US-2 yields the regression gate + refreshed artifacts — neither requires the other (nor US-1/#311).

## Assumptions

- **CI mechanism = a dedicated MAESTRO job** (not an expansion of the existing pytest job's allowlist). Resolved at PRD stage on unanimous Architect + Team-Lead recommendation and the `tachi-mmdc-preflight.yml` precedent; the F-250 lock-step rule (trigger paths ⇄ invocation) applies regardless.
- **Non-gated refresh set** = the example `sample-report` PDFs not in the six-baseline gated set (e.g., `agentic-app`, `consumer-agent-app`, `predictive-ml-app`, `mobile-banking-app`) plus `maestro-reference`'s loose `security-report.pdf`. The plan enumerates the exact file list; this set is the working assumption.
- **Muted treatment** for zero-finding bands follows the existing template prose (muted background + dash), so no new visual design is needed.
- **No new ADR and no schema/SARIF change** — reuse ADR-017 (deterministic infographic extraction), ADR-020 (MAESTRO classification), ADR-021 (SOURCE_DATE_EPOCH determinism), ADR-022 (dedicated-CI-job pattern).
- **Determinism applies to spec data**, not the optional image step (Gemini/mmdc remain best-effort, per ADR-014/ADR-016).

## Dependencies

- **F-098 deliverables in `main`** (squash `ac07085`): the orchestrator now authors all seven rows in the matrix; US-1 (infographic) relies on that upstream distribution, and US-2's invariant test guards it.
- **No new runtime dependencies**; reuses the stdlib parsers (`scripts/tachi_parsers.py`), the existing Typst PDF toolchain, and the F-098 regeneration-only harness `scripts/populate-maestro-coverage.py`.
- **Release note**: v4.39.0 is not yet cut (release PR #314 open); the F-098 *code* is in `main`, so this feature is unblocked. Merge #314 before/alongside delivery so the "F-098 released" premise is literally true.

## Out of Scope

- **US-1 Model B two-state (clean vs n/a) annotation** — carved to its own ADR-bearing feature, **#311**.
- **`maestro-heatmap` changes**, **`threat-report.md` per-layer roster**, **SARIF/schema changes**, **frozen `test-output/` snapshots**, and **changing the F-098 Model A guarantee** — all explicitly excluded.

## Technical Context *(non-binding anchors for `/aod.plan`; not requirements)*

- **US-1 gap is data emission**: `scripts/extract-infographic-data.py` maestro-stack `template_data` (≈L1937–1965) emits `maestro_layer_distribution`, `most_exposed_layer`, `per_layer_summaries`, `has_maestro_data` — but not the three count aggregates. `parse_maestro_layer_distribution` (≈L1495) does not backfill to seven. The template (`templates/tachi/infographics/infographic-maestro-stack.md`) already specifies all-7 + muting; the agent placeholders `{empty_layers}`/`{layers_with_findings}`/`{layer_count}` are currently agent-derived. Lock the new keys in `tests/scripts/test_extract_infographic_data.py` + the `maestro-stack.json` golden fixture.
- **US-2 anchors**: `tests/scripts/test_maestro_coverage_invariant.py` (the invariant; docstring L25–27 to update); `.github/workflows/tachi-mmdc-preflight.yml` (dedicated-job template); `.github/workflows/tachi-pytest.yml` (lock-step header L38–47 — the surface to *avoid* broadening); `tests/scripts/test_backward_compatibility.py:BASELINE_EXAMPLES` (L45–52) + `SOURCE_DATE_EPOCH=1700000000` (L43); `scripts/populate-maestro-coverage.py` (run before PDF refresh).
