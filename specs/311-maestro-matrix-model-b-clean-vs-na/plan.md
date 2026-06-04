---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-03
    status: APPROVED
    notes: "Plan stays in spec scope — 0 scope creep; all 7 Out-of-Scope boundaries honored (no SARIF/scoring/taxonomy change; maestro-heatmap, threat-report roster, crosswalk waves excluded). All spec FRs (FR-001..014) + SCs (SC-001..005) traceable to a Decision (A–F)/phase/file. Both spec-stage LOW advisories carried into Carry-Forward (US P1 label consistency #6; two-token doc-update a named task #5). Delivers the user value (clean-vs-n/a unambiguous on all 3 surfaces + machine-discernible coverage_state). Single-feature framing preserved. 0 BLOCKING / 0 CHANGES_REQUESTED / 2 LOW (carried). No veto. Full: .aod/results/product-manager.md"
  architect_signoff:
    agent: architect
    date: 2026-06-03
    status: APPROVED_WITH_CONCERNS
    notes: "APPROVE plan (PRIMARY) + ACCEPT ADR-047. Option (c) sound, re-confirmed against live code; all 6 PRD-stage concerns (HIGH-1/MEDIUM-1/2/3/LOW-1/2) verified RESOLVED with accurate file:line citations; D4 backfill-survival + D5 ordinal-0 verified achievable; microservices fixture verified (4 n/a + 1 clean + 2 findings); no SARIF/schema change verified; build order + determinism sound. 0 BLOCKING / 1 HIGH / 2 MEDIUM / 2 LOW, no veto. HIGH-A (PDF coverage_state must ride maestro_findings_by_layer group records, not maestro_layer_distribution) FOLDED into plan Decision C + data-model Entity 3. MEDIUM-B (populator Section-1 read — scope or descope), MEDIUM-A (PDF state regenerated not committed in consistency test), LOW-A (CI paths reclassification), LOW-B ({layer_bands_text} builder is the infographic n/a branch) added to Carry-Forward #9–13 for /aod.tasks. Full: .aod/results/architect.md"
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: MAESTRO Matrix Model B — Clean vs. N/A

**Branch**: `311-maestro-matrix-model-b-clean-vs-na` | **Date**: 2026-06-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/311-maestro-matrix-model-b-clean-vs-na/spec.md` (PM APPROVED) · **ADR**: [ADR-047](../../docs/architecture/02_ADRs/ADR-047-maestro-coverage-state-authority.md)

## Summary

Split the single Model-A zero-finding annotation into two states — **clean** (≥1 mapped component, 0 findings) and **n/a** (0 mapped components) — across the three MAESTRO rendering surfaces (`threats.md` Section-6 matrix, PDF "MAESTRO Layer Analysis" page, `maestro-stack` infographic). The orchestrator authors the state **once** into the Section-6 Highest-Severity cell it already holds the inputs for (ADR-047 D1); both Python extractors **inherit** it by classifying the carried token through a pure shared helper in `tachi_parsers.py`, emitting a `coverage_state` enum into the PDF/infographic render IR (D2); the Section-1-derived heatmap path is fenced off (D3). Two renderers gain an explicit n/a branch (Architect HIGH-1). `examples/microservices` (≥4 n/a + ≥1 clean) is the CI-gated cross-surface fixture. No SARIF/schema/scoring/taxonomy change.

## Technical Context

**Language/Version**: Python 3.11 (extractors, parser, populator, tests); Typst (PDF template); Markdown + Gemini-prompt prose (orchestrator directive, infographic template).
**Primary Dependencies**: `scripts/tachi_parsers.py` (shared parser — `MAESTRO_LAYERS`, `SEVERITY_ORDINAL`, `parse_markdown_table`); Typst + mmdc toolchain (PDF regen, ADR-022); pytest.
**Storage**: Files only — `threats.md` (markdown source of truth), `report-data.typ` / `maestro-stack.json` (render IR), `.pdf.baseline` (byte-gated baselines).
**Testing**: pytest (`tests/scripts/`); cross-surface consistency test; backward-compat byte-identity (`SOURCE_DATE_EPOCH=1700000000`); `tachi-maestro-coverage.yml` CI job.
**Target Platform**: Local-first instrumentation harness inside Claude Code; CI on `ubuntu-latest`.
**Project Type**: Single project (instrumentation harness) — no new module boundaries.
**Performance Goals**: Negligible — applicability is derived from data the orchestrator already computes; no new analysis pass.
**Constraints**: Byte-deterministic outputs under `SOURCE_DATE_EPOCH`; 6 byte-gated PDF baselines stay byte-identical after deliberate regen; no SARIF schema or emitted-result change; canonical 7-layer taxonomy frozen (F-136).
**Scale/Scope**: 3 rendering surfaces, 1 shared classifier, 1 fixture, ~6 churning example baselines, 1 ADR.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| III. Backward Compatibility (NON-NEGOTIABLE) | ✅ PASS | No SARIF/schema change (FR-014); zero-finding rows never affected scoring; taxonomy untouched (F-136). Clean rendering is **unchanged** — all-in-scope examples show no spurious diff (NFR). `coverage_state` is an additive render-IR field (existing consumers unaffected). n/a-bearing baselines regenerate by design (ADR-021), 6 byte-gated baselines stay byte-identical. |
| VI. Testing Excellence | ✅ PASS | `examples/microservices` cross-surface consistency test (≥4 n/a + ≥1 clean) is the regression anchor; dedicated tests for backfill-survival (D4) and ordinal-0 (D5); test-first on the `classify_maestro_coverage_state` helper. |
| VII. Definition of Done (NON-NEGOTIABLE) | ✅ PASS | DoD carried from spec; `/aod.analyze` gate (SC-003); `CHANGELOG.md` `feat(311)` entry at delivery; ADR-047 committed. |
| VIII. Observability & RCA | ✅ PASS | Consistency test fails with the offending **layer ID**; CI gate names missing/disagreeing layer; root cause (two-source divergence) addressed structurally by D1–D3. |
| IX. Git Workflow (NON-NEGOTIABLE) | ✅ PASS | Feature branch `311-...`; draft PR #318; conventional commits; squash title `feat(311):` (release-please). Confirm `v4.40.0` tag local before deliver (Team-Lead). |
| X. Product-Spec Alignment (NON-NEGOTIABLE) | ✅ PASS | PM sign-off on spec APPROVED; this plan + ADR-047 submitted for PM + Architect dual sign-off. |

**No violations. Complexity Tracking not required.** Net-new surface is one pure classifier function, one additive render-IR field per extractor, two renderer branches, one CI assertion, one ADR. The change *reduces* ambiguity and adds one authored token; it introduces no new module boundary.

## Resolved Plan-Stage Decisions

The spec's Key Design Decisions and the PRD's two plan-stage Open Questions are formalized here and in ADR-047.

### Decision A — Coverage-state authority: Section-6 carried token (resolves Open-Q1 / FR-002/004/005 / ADR-047)
**Decision**: Option (c). The orchestrator decides applicability once (it holds the Section-1 component→layer set) and encodes it into the Section-6 Highest-Severity cell. Both extractors inherit it via the pure shared classifier `classify_maestro_coverage_state(finding_count, highest_severity) -> "findings"|"clean"|"not_applicable"` in `tachi_parsers.py`, emitting a `coverage_state` field into `report-data.typ` and `maestro-stack.json`. The classifier reads only the carried token (does NOT read Section 1). Rejected: option (a) re-derive-from-Section-1-per-consumer (two authorities → desync); option (b) duplicate-parser (divergence). Full rationale + alternatives in **ADR-047**.
- **Fence (FR-004 / ADR-047 D3)**: `extract-infographic-data.py:parse_component_layer_mapping()` stays **heatmap-only**; it MUST NOT drive the `maestro-stack` clean-vs-n/a. Recorded as a structural invariant + an assertion.

### Decision B — The two zero-finding tokens (resolves Open-Q2 / FR-001/007)
**Decision**: In the Section-6 Highest-Severity cell —
| State | Cell token |
|-------|-----------|
| findings (>0) | severity label (`Critical`/`High`/`Medium`/`Low`/`Note`) — unchanged |
| **clean** (≥1 mapped, 0 findings) | `Analyzed — no findings this scan` — **UNCHANGED** (em-dash U+2014, no trailing period) |
| **n/a** (0 mapped) | `Not applicable — no components map to this layer` — **NEW** (em-dash U+2014, no trailing period) |
- Both zero-finding tokens are documented in the MAESTRO coverage reference (extend `coverage-matrix-model.md` with a MAESTRO-layer-view note). The bare `---`/`n/a` glyphs remain the STRIDE-matrix surface form (ADR-047 Alt 3).
- **Punctuation convention** follows the F-098 precedent: markdown cell carries no trailing period; the Typst prose adds one ("the only sanctioned cross-format difference"). The consistency test asserts the **phrase/state**, not the punctuation.

### Decision C — Per-surface n/a render branch (resolves Architect HIGH-1 / FR-008/009)
**Decision**: "Inherit" is necessary but not sufficient — both renderers hardcode the clean string today and need an explicit n/a branch:
- **PDF** `templates/tachi/security-report/maestro-findings.typ` (~L147–155): branch the zero-finding row on `coverage_state` — clean → `Analyzed — no findings this scan.` (unchanged, `brand-muted` italic); n/a → `Not applicable — no components map to this layer.` with a **visually separable** muted treatment (distinct fill/weight or an `(out of scope)` qualifier — exact tint finalized in the edit, state fixed here). **Wiring (Architect HIGH-A)**: `main.typ` (376–379) passes only `maestro_findings_by_layer` (group records `{layer_id, layer_name, findings[]}`) to the MAESTRO page — NOT `maestro_layer_distribution`. So `coverage_state` MUST be threaded onto the **`maestro_findings_by_layer` group records** in `extract-report-data.py` (set it from the matching `parsed_layers` row's classified token at the group pre-build ≈L366–370 + the fallback ≈L383–388), so the Typst branch reads `layer-group.at("coverage-state")`. Emitting it onto `maestro_layer_distribution` alone would leave the PDF page blind to it.
- **Infographic** `templates/tachi/infographics/infographic-maestro-stack.md` (prose L124–130, Gemini prompt L186–198, Accessibility L216–223): add a documented **third band state** — clean = muted band + dash (—) (unchanged); n/a = distinct muted treatment + **"N/A"** text label. Extend the Accessibility text-label rule to name the n/a label (today it names only the empty-dash). State flows from `maestro-stack.json` `coverage_state` (D2), never re-derived (D3).

### Decision D — Backfill survival + most-exposed invariant (resolves Architect MEDIUM-3/LOW-1 / FR-006/012)
**Decision**:
- **Backfill (D4)**: orchestrator authors the n/a token in the Section-6 row; the infographic absent-layer backfill (~L1961–1971) defaults table-less layers to **clean** rendering (preserves today's behavior) and MUST preserve a present n/a token (merge must not overwrite `not_applicable`). Regression on `microservices`.
- **Ordinal-0 (D5)**: clean and n/a tokens both resolve to `_SEVERITY_ORDINAL` rank 0 (both dict-miss today); `compute_most_exposed_layer` never selects a clean/n/a layer. Explicit tested invariant (not a dict-miss accident) in both extractors.

### Decision E — Fixture + CI gate (resolves FR-010/011 / SC-001/002)
**Decision**: `examples/microservices` is the gated fixture — **no synthetic fixture** (Team-Lead-confirmed: L2/L4/L7 mapped → L1/L3/L5/L6 n/a; L7 mapped + 0 findings → clean). Freeze its three-surface expected outputs; add a **cross-surface consistency assertion** (markdown state ⇄ PDF `coverage_state` ⇄ infographic `coverage_state` agree for all 7 layers) to the existing dedicated `.github/workflows/tachi-maestro-coverage.yml` job, in **F-250 lock-step** (workflow `paths:` AND the pytest invocation updated in the same commit). The existing invariant (all-7-rows present) is unchanged; this is an added assertion in the same job.

### Decision F — Baseline regen as a discrete, diff-reviewed task (resolves SC-004 / Architect LOW-2 / NFR)
**Decision**: n/a-bearing example baselines legitimately change. Enumerate the churning set, run a **drift audit first** (classify real n/a-churn vs no-drift, drop no-drift targets), then regenerate deterministically (`SOURCE_DATE_EPOCH=1700000000`) with a `[MANUAL-ONLY]` diff confined to the annotation change. **Run the populator's heading normalization first** (LOW-2) so an n/a-bearing example does not parse to zero layers (empty PDF page). Candidate churn set (confirmed by Section-1↔Section-6 cross-ref): `microservices` (4 n/a), `web-app` (3), `free-text-microservice` (4), `mobile-banking-app/sample-report` (5), `mermaid-agentic-app` (3), `agentic-app` (1). Of the 6 byte-gated baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`), those carrying n/a layers re-baseline deliberately; `ascii-web-api` + `maestro-reference` are drift-audited. The byte-identity test stays the gate **after** intentional regen.

## Project Structure

### Documentation (this feature)
```
specs/311-maestro-matrix-model-b-clean-vs-na/
├── plan.md              # This file
├── spec.md              # PM-approved feature spec
├── research.md          # Research findings (Phase 0 — complete)
├── data-model.md        # coverage_state enum + carried-token contract (Phase 1)
├── quickstart.md        # Verification runbook (Phase 1)
├── contracts/           # classifier + cross-surface-consistency + CI-gate contracts (Phase 1)
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # /aod.tasks output (next sub-step)
docs/architecture/02_ADRs/
└── ADR-047-maestro-coverage-state-authority.md   # the Model B decision (committed this phase)
```

### Source Code (files touched, by build phase)
```
# ── Phase A: SOURCE CONTRACT (must land first — both extractors read this) ──
.claude/agents/tachi/orchestrator.md                         # FR-002: author clean-vs-n/a token into Section-6 Highest-Severity cell from component->layer mapping
.claude/skills/tachi-orchestration/references/output-schemas.md  # FR-001/007: document the n/a token + three-state Section-6 contract
scripts/tachi_parsers.py                                     # FR-005: NEW pure helper classify_maestro_coverage_state()
scripts/populate-maestro-coverage.py                         # FR-003: author the two-token logic on example regen (examples-only; heading-normalize preserved)
.claude/skills/tachi-orchestration/references/coverage-matrix-model.md  # NFR consumability: document the two MAESTRO zero-finding tokens

# ── Phase B: PDF SURFACE (parallel with infographic) ──
scripts/extract-report-data.py                              # FR-005: call classifier, emit coverage_state into report-data.typ; FR-012 ordinal-0 assert
templates/tachi/security-report/maestro-findings.typ        # FR-008 / HIGH-1: branch zero-finding row on coverage_state -> distinct n/a prose+style

# ── Phase B: INFOGRAPHIC SURFACE (parallel with PDF) ──
scripts/extract-infographic-data.py                         # FR-004/005/006: call classifier -> coverage_state; fence component_layer_map to heatmap (D3); backfill survival (D4); FR-012 ordinal-0
templates/tachi/infographics/infographic-maestro-stack.md   # FR-009 / HIGH-1: third band state + "N/A" label + Accessibility extension

# ── Phase C: FIXTURE + CI GATE (after all three render) ──
tests/scripts/test_maestro_coverage_invariant.py            # FR-010/011: add cross-surface state-consistency assertion (microservices)
tests/scripts/fixtures/golden/maestro-stack.json            # FR-011: regenerated golden carrying coverage_state
tests/scripts/test_extract_infographic_data.py              # FR-005/006: assert coverage_state + backfill survival
tests/scripts/test_extract_report_data.py                   # FR-005/012: assert coverage_state + ordinal-0 (extend or add)
.github/workflows/tachi-maestro-coverage.yml                # FR-011: add consistency test to invocation + paths (F-250 lock-step)

# ── Phase D: BASELINE REGEN (final, mechanical, diff-reviewed) ──
examples/microservices/{threats.md, security-report.pdf(.baseline)}   # fixture + gated baseline re-freeze
examples/{web-app, free-text-microservice, mermaid-agentic-app}/...   # gated baselines re-freeze (n/a-bearing)
examples/{mobile-banking-app/sample-report, agentic-app/...}          # non-gated [MANUAL-ONLY] refresh (drift-audited)
examples/{ascii-web-api, maestro-reference}/...                       # gated baselines (drift-audited)
tests/scripts/test_backward_compatibility.py                # UNCHANGED logic: gate stays green after intentional re-freeze

# ── Cross-cutting ──
CHANGELOG.md                                                # feat(311) entry (delivery)
```

**Structure Decision**: Single-project instrumentation harness; no new module boundaries. The system-design auto-scaffold (Step 6) correctly **skips** — no `## Components`/`## Data Flow`/`## Tech Stack` canonical sections (matching the F-098/F-315 precedent for pipeline-fidelity features; the design lives in this plan + ADR-047 + data-model.md + contracts/).

## Technical Approach

The data line is `threats.md Section-6 cell -> (both extractors read the same cell) -> render IR (report-data.typ / maestro-stack.json) -> renderer`. Model B adds exactly one authored token at the source and one classification step on inheritance:

1. **Author once (Phase A).** The orchestrator stamps the Section-6 Highest-Severity cell with the clean or n/a token per Decision B, driven by the Section-1 component→layer set it already computes. `populate-maestro-coverage.py` mirrors this for example regeneration. `output-schemas.md` + `coverage-matrix-model.md` document the contract.
2. **Inherit by classifying (Phase B).** Both extractors call `classify_maestro_coverage_state()` on the carried token and emit a `coverage_state` enum into their render IR. No applicability is re-derived; the Section-1 heatmap path is fenced (D3). Each renderer gains an explicit n/a branch (Decision C) — the necessary-not-sufficient HIGH-1 work.
3. **Prove consistency (Phase C).** The `microservices` fixture's three surfaces are frozen and a cross-surface consistency assertion is added to the dedicated CI job in F-250 lock-step. Backfill-survival (D4) and ordinal-0 (D5) get dedicated regressions.
4. **Re-freeze baselines (Phase D).** Drift-audit -> deterministic regen under `SOURCE_DATE_EPOCH` -> `[MANUAL-ONLY]` annotation-only diff. Heading-normalize first (LOW-2).

Build order is **hard at Phase A -> B** (extractors need the authored cell contract), **parallel within Phase B** (PDF ∥ infographic — different files, no cross-dependency), then C, then D (Team-Lead §4).

## Phase 0: Outline & Research

**Complete.** `research.md` consolidates: the `coverage-matrix-model.md` two-state vocabulary; KB Entry 11 (F-098 single-source-of-truth doctrine + the exact clean string and punctuation rule); the live-code reconnaissance of all three surfaces with file:line (carried cell, the two hardcoded renderer strings, the Section-1 second-derivation, the backfill, the ordinal tie-break, the heading fragility); the `microservices` fixture confirmation; the determinism/golden-regen procedure; the F-315 CI-gate mechanics + F-250 lock-step; and the SARIF `pass`/`notApplicable` external analogue. **No NEEDS CLARIFICATION markers remain** — all spec/PRD open questions are resolved in Decisions A–F and ADR-047.

## Phase 1: Design & Contracts

**Prerequisites**: research.md complete ✓. Generated this phase:
- **`data-model.md`** — the `coverage_state` enum (`findings`|`clean`|`not_applicable`), the carried-token contract (the two zero-finding strings), the per-surface render-IR fields (`report-data.typ`, `maestro-stack.json`), and the layer-state entity (always 7).
- **`contracts/`** (adapted — no HTTP API): `coverage-state-classifier.contract.md` (the pure-helper signature, the token→enum mapping table, the ordinal-0 + no-Section-1 invariants); `cross-surface-consistency.contract.md` (the three-surface agreement assertion + the `microservices` expected-state table); `tachi-maestro-coverage-ci.contract.md` (the added assertion + F-250 paths⇄invocation lock-step).
- **`quickstart.md`** — verification runbook: regenerate `microservices` outputs, assert L7=clean and L1/L3/L5/L6=n/a on all three surfaces, force a disagreement and confirm the CI assertion fails with the layer ID, regenerate a gated PDF deterministically and byte-compare.
- **Agent context update** — N/A: `.aod/scripts/bash/update-agent-context.sh` is absent in this template version; no new technology to register; CLAUDE.md unchanged.

Post-design Constitution re-check: still PASS (one pure classifier + one additive render-IR field per extractor + two renderer branches + one CI assertion + one ADR; no new boundary, no schema change).

## Risks & Sequencing

| # | Risk | Likelihood · Impact | Mitigation |
|---|------|---------------------|------------|
| R1 | Cross-surface divergence — infographic re-derives applicability from Section 1 instead of the carried cell | Med · High | ADR-047 D3 fence (`parse_component_layer_mapping` heatmap-only) + the cross-surface consistency CI gate on `microservices`. The single sharpest reviewer concern; structurally closed. |
| R2 | "Inherit ≠ done" — renderers ship no visible n/a distinction (HIGH-1) | Med · High | Decision C makes the PDF Typst branch and the infographic third-band-state **explicit named tasks**, not folded into extractor inherit; the consistency test would fail if a surface can't express the state. |
| R3 | n/a token lost via infographic backfill (table-less merge) | Low · Med | D4: author n/a in the Section-6 row; backfill defaults to clean only when table-less; regression asserts a present n/a survives the merge. |
| R4 | PDF baseline churn hides unrelated/non-annotation drift | High (expected) · Low | Decision F: drift-audit first, deterministic `SOURCE_DATE_EPOCH` regen, `[MANUAL-ONLY]` diff confined to annotation; 6 gated baselines re-frozen deliberately; heading-normalize first (LOW-2). |
| R5 | Most-exposed tie-break picks an n/a/clean layer if someone adds n/a to the ordinal map | Low · Med | D5: explicit tested invariant (ordinal 0; never selects zero-finding layer) in both extractors. |
| R6 | CI `paths:` misses an author/parse surface → false-green | Med · Med | F-250 lock-step; `paths:` enumerates orchestrator directive, parser, both extractors, both templates, examples, tests, workflow; updated in the same commit as the invocation. |
| R7 | `v4.40.0` tag not present locally at deliver → wrong release base | Low · Low | Team-Lead deliver-time check: confirm `git tag v4.40.0` before `/aod.deliver`. |

**Sequencing**: Phase A (source contract) → Phase B (PDF ∥ infographic) → Phase C (fixture + CI) → Phase D (baseline regen). Single feature, do not split (Team-Lead — the three surfaces share one source cell; splitting breaks cross-surface testability).

## Carry-Forward to tasks.md (from plan sign-off)

1. **Drift audit before regen (Decision F)** — a discrete task: classify each candidate example (real n/a-churn vs no-drift), DROP no-drift targets, enumerate the final churn set before any PDF regen. Keep baseline regen out of opaque implementation commits.
2. **Heading-normalize first (LOW-2)** — run `populate-maestro-coverage.py` heading normalization on each refresh target so no n/a-bearing example parses to zero layers.
3. **F-250 lock-step (Decision E)** — update `tachi-maestro-coverage.yml` `paths:` AND the pytest invocation in the **same commit** as the new consistency assertion.
4. **Test-first on the classifier** — author `classify_maestro_coverage_state` tests (token→enum table incl. ordinal-0) before wiring the extractors.
5. **Two-token doc update is a named task** (PM LOW advisory) — extend `coverage-matrix-model.md` with the MAESTRO zero-finding tokens.
6. **US priority-label normalization** (PM LOW advisory) — spec uses P1/P1/P2; keep tasks consistent.
7. **Deliver-time**: confirm `v4.40.0` git tag present locally before `/aod.deliver`; PR squash title `feat(311):` for release-please.
8. **DoD byte-gate**: run `test_backward_compatibility.py` locally at build/DoD (it is a local/build-time gate, not wired into CI) after intentional re-freeze.

**From Architect plan-review (2 deliverables + 3 tightenings — all tasks-stage):**

9. **[HIGH-A] PDF `coverage_state` rides `maestro_findings_by_layer`** — folded into Decision C above. tasks.md must name the exact `extract-report-data.py` sites (group pre-build ≈L366–370 + fallback ≈L383–388) that set `coverage_state` on the **grouped** structure `main.typ` actually passes, and a PDF test (extend `test_maestro_zero_finding_layer_is_retained_not_dropped`, `test_extract_report_data.py:384–409`) asserting the field is present on the group record + drives the Typst branch. data-model Entity 3 reconciled.
10. **[MEDIUM-B] Populator FR-003 — scope OR descope the Section-1 read** — `populate-maestro-coverage.py` is Section-6-only today (never reads Section 1; keeps present rows verbatim; `tachi_parsers.py` exposes no shared component→layer parser). tasks.md MUST decide: **(a)** add an examples-local Section-1 read + present-row re-decision so unmapped zero-finding rows flip to the n/a token (must stay examples-only — MUST NOT become a second production authority; respect ADR-047 D3), or **(b)** descope the populator to clean-only and author the n/a example tables via the orchestrator/manual path. Pick one explicitly and budget it.
11. **[MEDIUM-A] PDF state in the consistency test is regenerated, not committed** — `report-data.typ` is not committed per-example. tasks.md must state the cross-surface test obtains the PDF state by invoking `extract-report-data.py` / `parse_maestro_data` on `examples/microservices` at test time (mirroring the infographic's `_maestro_stack_template_data` harness), not by reading a committed artifact.
12. **[LOW-A] CI `paths:` reclassification** — under Model B the cross-surface test re-extracts render IR, so `extract-report-data.py`, `extract-infographic-data.py`, and both templates become **regression-necessary** (not "defense-in-depth / cannot change a committed example"). tasks.md updates the two-tier `paths:` split + its comment (F-250 lock-step).
13. **[LOW-B] Infographic third state lives in the `{layer_bands_text}` builder** — `coverage_state` lands in `per_layer_summaries` (`extract-infographic-data.py:1988–1996`), but the visible n/a band is produced by the per-layer `{layer_bands_text}` prompt-construction (template L191). tasks.md locates the n/a branch in that builder (band text keyed on `coverage_state`), not only the static prose, or every band still renders identically.

## Out of Scope (carried from spec)

- ❌ SARIF / schema changes (render-layer only); ❌ re-scoring / risk-model changes; ❌ new MAESTRO layers / taxonomy change (F-136 frozen).
- ❌ `maestro-heatmap` infographic (renders empty cells already; uses the fenced Section-1 derivation).
- ❌ Section 5 STRIDE coverage matrix (already three-state).
- ❌ `threat-report.md` per-layer roster (no such roster; net-new structure — F-098 exclusion).
- ❌ Crosswalk depth (BLP-05 Waves 2–3, #182–#186 — independent data-layer work).
