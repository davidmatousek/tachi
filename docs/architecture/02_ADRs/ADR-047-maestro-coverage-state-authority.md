# ADR-047: MAESTRO Coverage-State Authority — Section-6 Carried Token as Sole Applicability Source (Model B)

**Status**: Accepted
**Date**: 2026-06-03 (Proposed); 2026-06-03 (Accepted, provisional pre-PR; final commit-SHA filled post-merge)
**Deciders**: Architect (sign-off at /aod.project-plan), Product Manager (APPROVED on spec 2026-06-03; sign-off at /aod.project-plan), Team-Lead (sign-off at /aod.tasks)
**Feature**: [311-maestro-matrix-model-b-clean-vs-na](../../../specs/311-maestro-matrix-model-b-clean-vs-na/spec.md) (Model B, BLP-05 Wave 1)
**Supersedes**: None
**Superseded by**: None
**Related ADRs**: [ADR-020](ADR-020-maestro-layer-classification.md) (MAESTRO layer classification — the orchestrator owns the component→layer mapping this ADR makes authoritative), [ADR-037](ADR-037-web-api-coverage-attestation-and-populator-wiring.md) (`maestro_layer` populator-wiring + **test-checked, not structural** production-consistency precedent this ADR inherits), [ADR-017](ADR-017-deterministic-infographic-extraction.md) (deterministic infographic JSON — the `coverage_state` field rides its `sort_keys` determinism), [ADR-021](ADR-021-source-date-epoch-determinism.md) (`SOURCE_DATE_EPOCH` PDF byte-determinism — governs the n/a-bearing baseline regen), [ADR-026](ADR-026-pattern-classification-mechanism.md) (no-bump rule — Model B is a render-layer change, **no schema bump**)

---

## Context

Feature 098 (Model A, v4.39.0) made the MAESTRO coverage view render all 7 canonical layers always, annotating **every** zero-finding layer uniformly as `Analyzed — no findings this scan`. That single annotation conflates two distinct facts a security engineer (and a downstream AI-security tool) needs to tell apart:

- **clean** — ≥1 component maps to the layer and it was analyzed with zero findings ("we looked and found nothing");
- **n/a** — no component maps to the layer, so it was never in scope ("we did not look, as expected").

F-098 SC-006 explicitly deferred this distinction to "Model B / P1." Feature 311 closes it across the **three** MAESTRO rendering surfaces: the `threats.md` Section-6 matrix, the PDF "MAESTRO Layer Analysis" page, and the `maestro-stack` infographic.

The governing structural fact (architect-confirmed against live code) is that all three surfaces already share **one** authored source cell. Section 6 "Risk by MAESTRO Layer" (`output-schemas.md:229–242`) emits `| MAESTRO Layer | Finding Count | Highest Severity |` for all 7 layers. Both Python extractors read the **same** Highest-Severity cell as a free-text string — `extract-report-data.py:282` and `extract-infographic-data.py:1527`, each `row.get("Highest Severity","").strip()`. Whatever token the orchestrator writes there is inherited by both with **zero parser changes**. The orchestrator holds the Section-1 component→layer set at authoring time (Phase 1 classification, `orchestrator.md:176–186`), so applicability ("≥1 component maps to layer L?") is decidable at the source.

But there is a **second, parallel applicability derivation** in the infographic script: `extract-infographic-data.py:1539 parse_component_layer_mapping()` independently re-derives a `component_layer_map` from the **Section-1** Components table, feeding `compute_maestro_heatmap()` (the `maestro-heatmap` infographic, scoped OUT of #311). If Model B authored n/a only into the Section-6 cell while the `maestro-stack` infographic kept deriving applicability from Section 1, the two surfaces would compute applicability from **two different sources** — precisely the desync "author once, inherit" exists to prevent. Both reviewers flagged this as the single sharpest divergence point.

A prior framing (PRD Open-Q1, carried from F-315) described the choice as "build a shared parser module vs carry state." That framing is **stale**: `scripts/tachi_parsers.py` (1604 lines) **already exists** and is already the shared authority imported by both extractors and the populator (`MAESTRO_LAYERS`, `SEVERITY_ORDINAL`, `parse_markdown_table`). The real decision is therefore not "build a module" but **where applicability is decided** — once at the orchestrator source, or re-derived per consumer.

This ADR is committed because Model B elects a **production-tier authoring-contract change** (the orchestrator's `threats.md` Section-6 directive plus the two extractors' render contracts), and locks a structural invariant (single applicability authority) that a future refactor could otherwise silently break. A render annotation alone would warrant no ADR; the cross-surface authority decision does.

---

## Decision

We adopt **Option (c) — the Section-6 Highest-Severity cell is the sole applicability authority; both extractors inherit it by classifying the carried token through a pure shared helper.** Five decisions record the mechanism.

### D1 — Applicability is decided once, at the orchestrator source

The orchestrator, which already holds the Section-1 component→layer mapping at authoring time, decides each zero-finding layer's state and **encodes it once** into that layer's Section-6 Highest-Severity cell:

- ≥1 component maps to the layer (finding_count == 0) → the **clean** token `Analyzed — no findings this scan` (unchanged from Model A; em-dash U+2014, no trailing period);
- 0 components map to the layer → the **n/a** token `Not applicable — no components map to this layer` (new; em-dash U+2014, no trailing period).

`scripts/populate-maestro-coverage.py` authors the identical two-token logic when regenerating example tables (it has Section-1 access), remaining examples-regeneration-only and never wired into a command/orchestrator phase. No new analysis pass is introduced (NFR "performance: negligible" holds).

### D2 — Extractors inherit by classifying the carried token (pure shared helper, NOT a re-derivation)

A pure, side-effect-free helper is added to the existing `scripts/tachi_parsers.py`:

```
classify_maestro_coverage_state(finding_count: int, highest_severity: str) -> str
    # returns exactly one of: "findings" | "clean" | "not_applicable"
```

Both extractors call it and emit a `coverage_state` enum per layer into their render data — `report-data.typ` (PDF) and `maestro-stack.json` (infographic). **The helper reads only the already-authored token; it does NOT read Section 1 and does NOT decide applicability.** It classifies the orchestrator's decision. This is the load-bearing distinction from Option (a): the shared helper is a token *classifier*, so it is not a second source of truth — applicability is authored exactly once (D1) and merely *translated* to an enum here.

### D3 — The Section-1 derivation is fenced to the heatmap (the divergence guard)

`extract-infographic-data.py:parse_component_layer_mapping()` (Section-1-derived `component_layer_map`) remains **heatmap-only**. It MUST NOT be re-routed to drive the `maestro-stack` clean-vs-n/a state. The `maestro-stack` state comes exclusively from the Section-6 carried token via D2. This is recorded as a **structural invariant** so a future refactor cannot reintroduce a second applicability path and desync the surfaces. `maestro-heatmap` is unaffected (it already renders empty cells from Section 1, out of #311 scope).

### D4 — The n/a token is authored in the Section-6 row and survives backfill

The orchestrator authors the n/a token in the Section-6 row itself; production never relies on the infographic backfill for n/a. The backfill path (`extract-infographic-data.py`, absent-layer synthesis at ~1961–1971) — a **table-less / partial-input** fallback — defaults a backfilled layer to the **clean** rendering (preserving today's behavior when applicability is unknowable), and MUST preserve an n/a token that *is* present in Section 6 (the merge must not overwrite a present `not_applicable` to empty/clean). A regression asserts this on the `microservices` fixture.

### D5 — Zero-finding states resolve to severity ordinal 0 (most-exposed invariant)

Both the clean and the n/a token MUST resolve to `_SEVERITY_ORDINAL` rank **0** in the most-exposed-layer tie-break (`extract-report-data.py:417`, `extract-infographic-data.py:1700`) — today's clean string already dict-misses to 0; the n/a token will too (`n/a` ∉ ordinal map). `compute_most_exposed_layer` MUST never select a clean or n/a (zero-finding) layer. This is converted from a latent dict-miss accident into an **explicit, tested invariant**, so a future contributor who adds n/a to `_SEVERITY_ORDINAL` cannot silently make an out-of-scope layer "most exposed."

### Constraint — render-layer only; no schema/SARIF/scoring/taxonomy change

The carried token lives in `threats.md` markdown; the `coverage_state` enum lives in the PDF/infographic **render IR** (`report-data.typ`, `maestro-stack.json`). Neither is the SARIF contract: zero-finding layers emit no SARIF result, CVSS/composite scores are per-finding, and the canonical 7-layer taxonomy (Feature 136) is untouched. No `schemas/*.yaml` change; no SARIF schema or emitted-result change (ADR-026 no-bump). Production cross-surface consistency is **test-checked, not structural** in the LLM-authored markdown tier — the `maestro_layer` posture from ADR-037 (the cross-surface fixture is the required, non-optional guard).

---

## Alternatives Considered

### Alternative 1 — Option (a): add an applicability helper to the shared parser that re-derives from Section 1 per consumer (REJECTED)

Each extractor calls a shared `tachi_parsers.py` helper that re-parses the Section-1 Components table and computes applicability independently (the `component_layer_map` approach, generalized to the stack).

**Pros**: No new authored token in Section 6; applicability "derivable anywhere" from Section 1.

**Cons**: Creates **two applicability authorities** — the orchestrator's author-time view (which decides the visible cell) and the extractor's Section-1 re-parse — which can desync if Section 1 and the orchestrator's classification ever differ (e.g. an Unclassified edge case, a heading/format drift, or a future Section-1 schema tweak). It also re-introduces the very Section-1→stack coupling D3 fences off. "Author once, inherit" (FR-005) is violated in practice even though a shared *module* is used.

**Why Not Chosen**: The reviewers' sharpest concern is exactly two-source divergence. Option (c) authors applicability once where the orchestrator already knows it, and the shared helper classifies the *token* (D2) rather than re-deriving the *fact* — same shared-module hygiene, one authority. (The stale "build a module" framing is moot: `tachi_parsers.py` already exists; both options live in it.)

### Alternative 2 — Option (b): duplicate the infographic's Section-1 parser into the report pipeline (REJECTED)

Copy `parse_component_layer_mapping()` into `extract-report-data.py` so the PDF derives applicability the same way the heatmap does.

**Why Not Chosen**: Two near-verbatim parser copies are a documented drift class in this codebase (CHANGELOG F-136 Typst layer-name drift; F-154 infographic "checks wrong file/pattern"). Duplicating the derivation maximizes the desync surface — the opposite of the goal. Rejected for divergence risk before plan stage.

### Alternative 3 — Bare-glyph tokens (`---` clean / `n/a`) in the Section-6 cell (NOT adopted for MAESTRO)

Use the literal STRIDE-matrix glyphs in the Highest-Severity cell.

**Why Not Chosen**: F-098 deliberately chose human-readable prose (`Analyzed — no findings this scan`) for the MAESTRO **layer view** rather than the dense-matrix `---`. Changing clean to a bare glyph would churn every all-in-scope example (violating the no-spurious-diff NFR) and break the F-098 string the Typst/Gemini surfaces key on. Model B keeps clean's prose unchanged and adds a parallel n/a prose; the `---`/`n/a` glyphs remain the STRIDE-matrix surface form. The two states are still machine-discernible via the two documented prose tokens **plus** the `coverage_state` enum.

---

## Consequences

### Positive

- ✅ A zero-finding MAESTRO layer is unambiguous on every surface — clean vs n/a — closing F-098 SC-006.
- ✅ **Single applicability authority** (D1) with a structural fence (D3): a future refactor cannot silently re-route the stack through Section 1 and desync surfaces — the consistency fixture catches it.
- ✅ Cheap inheritance: both extractors already read the carried cell; the only data-path addition is one pure classifier and one `coverage_state` field (D2), code-computed and deterministic (ADR-017), which also delivers machine-discernibility (US-2) for free.
- ✅ No schema/SARIF/scoring/taxonomy change; existing SARIF consumers unaffected.

### Negative

- ⚠️ Production cross-surface consistency is **test-checked, not structural** in the LLM-authored markdown tier (the `maestro_layer` / ADR-037 posture). If the cross-surface fixture test is removed or weakened, the three surfaces could silently diverge.
- ⚠️ "Inherit" is necessary but not sufficient: both renderers (`maestro-findings.typ`, `infographic-maestro-stack.md`) hardcode the clean string today and need an explicit **n/a render branch** (Architect HIGH-1) — the data inheritance alone renders no visible distinction.
- ⚠️ n/a-bearing example PDF baselines legitimately change and must be regenerated and re-frozen deliberately under `SOURCE_DATE_EPOCH` (ADR-021), with a diff-review confined to the annotation change.

### Mitigation

- The cross-surface consistency test on `examples/microservices` (≥4 n/a + ≥1 clean) is a **required, non-optional** CI gate, added to `tachi-maestro-coverage.yml` in F-250 lock-step (workflow `paths:` ⇄ pytest invocation updated together).
- The n/a-render-branch work is enumerated as explicit renderer tasks (spec FR-008/FR-009), not folded into "extractor inherit."
- D4 (backfill survival) and D5 (ordinal-0) are each gated by a dedicated regression so the table-less fallback and the most-exposed tie-break cannot silently mis-state an n/a layer.
- Baseline regen is a discrete, diff-reviewed task (not folded into implementation commits); the 6 byte-gated baselines stay byte-identical after deliberate regeneration.

---

## References

- Feature 311 Spec: [specs/311-maestro-matrix-model-b-clean-vs-na/spec.md](../../../specs/311-maestro-matrix-model-b-clean-vs-na/spec.md) — FR-002 (Section-6 carried state), FR-004 (single authority), FR-005 (shared classifier), FR-006 (backfill survival), FR-012 (ordinal invariant)
- Feature 311 Plan: [specs/311-maestro-matrix-model-b-clean-vs-na/plan.md](../../../specs/311-maestro-matrix-model-b-clean-vs-na/plan.md) — Resolved Decisions A–E
- Deferred requirement: `specs/098-maestro-7-layer/spec.md` FR-011 (Model B deferral) + SC-006
- Prior-art vocabulary: `.claude/skills/tachi-orchestration/references/coverage-matrix-model.md` (analyzed-clean `---` / not-applicable `n/a` three-state model)
- Render surfaces: `scripts/extract-report-data.py` (PDF), `scripts/extract-infographic-data.py` (`component_layer_map` heatmap derivation — fenced by D3), `scripts/populate-maestro-coverage.py` / orchestrator (`threats.md`)
- Shared authority: `scripts/tachi_parsers.py` (already exists; hosts the new `classify_maestro_coverage_state` classifier)
- Determinism: `tests/scripts/test_backward_compatibility.py` (`SOURCE_DATE_EPOCH=1700000000`, 6 byte-gated baselines)
- External analogue: SARIF 2.1.0 `result.kind` `pass` (analyzed-clean) vs `notApplicable` (out of scope)
