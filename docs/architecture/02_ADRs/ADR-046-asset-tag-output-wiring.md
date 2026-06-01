# ADR-046: Asset-Tag Output Wiring — Deterministic Population Across the LLM/Python Tier Boundary (F-260b)

**Status**: Accepted
**Date**: 2026-05-30 (Proposed); 2026-05-30 (Accepted, provisional pre-PR; final commit-SHA filled post-merge)
**Deciders**: Architect (APPROVED 2026-05-30), Product Manager (APPROVED_WITH_CONCERNS 2026-05-30), Team-Lead (sign-off at /aod.tasks)
**Feature**: [302-asset-tag-output-wiring](../../../specs/302-asset-tag-output-wiring/spec.md) (F-260b, BLP-04 Wave 2)
**Supersedes**: None
**Superseded by**: None
**Related ADRs**: [ADR-026](ADR-026-pattern-classification-mechanism.md) (minor-bump rule — `affected_assets` is the additive `1.8 → 1.9` bump; ADR-026 alone would be no-ADR per its own rule), [ADR-028](ADR-028-source-attribution-schema-extension.md) (additive-optional-field + serialization-surface precedent; `affected_assets` follows the always-present-default arm, not the `source_attribution` omit-when-empty arm), [ADR-037](ADR-037-web-api-coverage-attestation-and-populator-wiring.md) (`maestro_layer` / populator-wiring precedent — test-checked production consistency, structural only in the script tier)

---

## Context

Feature 302 (F-260b) wires the asset-sensitivity tags introduced by the community-merged prototype — PR #262 (@north-echo, shipped v4.31.0) — through the production output surfaces an adopter consumes: the `threats.md` finding block and the SARIF property bag (`affected_assets[]` in `result.properties`). The prototype froze the tag enum at **6 values** (`pii | phi | auth | secrets | financial | safety`) and froze the CVSS impact-modifier **ceiling at 9.2**. This feature does **not** change those values — it propagates them. The enum, the ceiling, and the modifier-after-clamp ordering are out of scope (spec SC-011).

The wiring decision is governed by a structural fact about how tachi produces its outputs — the **LLM/Python tier boundary** — recorded in plan.md as **Architecture Decision AD-1 ("The Determinism Mechanism")** and resolved in the **Q2 row** of the Open-Question table. The PRD's FR-2 mental model assumed a "deterministic `threats.md` serializer" already joining the parser to findings; the code investigation (architect-confirmed) found the boundary is real and currently uncrossed:

- **Production tier (LLM-authored).** The artifacts adopters actually receive — `threats.md` and **both** `.sarif` files — are authored by LLM agents at run time: the **orchestrator** writes `threats.md` and `threats.sarif`; the **risk-scorer** (tools Read/Glob/Grep/Write — **no Bash**) writes `risk-scores.md` and `risk-scores.sarif`. There is **no Python script in the live production path**.
- **Regeneration / verification tier (Python).** The `generate-threats-sarif.py` and `generate-risk-scores-sarif.py` scripts (plus `sarif_common.py`, `parse_component_asset_map()`) exist for baselines, tests, and regeneration only. They have **zero production callers** — nothing in the live pipeline invokes them. They are the deterministic reference the test suite diffs production output against (the F-219-vintage utilities).

This boundary is load-bearing because the asset-tag value itself is a **`dict.get` over the frozen 6-value enum**: `affected_assets = component_asset_map.get(component, [])`. Given a finding's target component, the tag list is a pure lookup, not a judgement call. Spec **FR-002 (deterministic population)** captures this with a deliberately literal reading — **"FR-2 literal"**: the value MUST be a deterministic function of inputs, not a value the LLM is invited to reason about or vary. "Make it deterministic" therefore cannot naively mean "route it through Python" without re-architecting the production path — which is out of scope here.

The governing precedent is **`maestro_layer`** (ADR-037 / ADR-020 lineage): its production cross-format consistency is enforced by a **test check**, not by a structural guarantee in the live path; the structural guarantee exists only in the Python script tier. `affected_assets` inherits exactly this posture.

Per the architect's ADR-worthiness criterion, a schema field alone would warrant **no ADR** (the ADR-026 minor-bump rule + ADR-028/037 precedents govern it). But because Feature 302 elects the **production tier** — modifying the **live LLM SARIF-authoring contracts** — the criterion is met and this **thin ADR** is committed (plan.md Q2 resolution).

---

## Decision

We adopt **Design A — deterministic populator as value authority; production LLM authoring contracts copy it verbatim into SARIF.** The five decisions below record the determinism mechanism.

### D1 — The LLM/Python tier boundary is respected, not crossed

Production `threats.md` and both `.sarif` files remain **LLM-authored** (orchestrator → `threats.md` + `threats.sarif`; risk-scorer → `risk-scores.md` + `risk-scores.sarif`; no Bash in either agent). The `generate-*-sarif.py` scripts remain the **regeneration / verification tier with zero production callers**. F-260b adds wiring *within* the existing tiers; it does **not** move production authoring into Python. Anyone reasoning about output integrity must hold this boundary: the script that deterministically emits SARIF is **not** the artifact the adopter receives.

### D2 — Production-tier election: deterministic populator is the single value authority (Design A)

A deterministic, non-LLM **populator** owns the `affected_assets` value and writes the canonical block into `threats.md` (the value origin). The production **LLM authoring contracts** then **copy that block verbatim** into the SARIF `affected_assets[]` property bag — `sarif-specification.md` (orchestrator → `threats.sarif`) and the `risk-scorer.md` SARIF section (risk-scorer → `risk-scores.sarif`), each emitting `result.properties.affected_assets` with the literal **snake_case** key. The populator must write the `threats.md` block **before** SARIF authoring sources it (pipeline sequencing). The LLM **transcribes**; it does not derive, re-judge, or paraphrase the value. We elect the production tier because US-1/US-4 require adopters to see `affected_assets` in **live** output — a regeneration-only wiring would ship a feature adopters never see.

### D3 — Deterministic-value rationale (FR-2 literal)

Because the tag is a `dict.get` over a frozen 6-value enum, it is **not a candidate for LLM judgement**. Encoding it as a deterministic lookup that the LLM copies verbatim satisfies FR-002 in its literal form and removes per-run variance at the source. This is the one thing Design A buys over the rejected alternative (Design B, below): a **deterministic value** — not structural cross-format consistency, which both designs obtain only via test-check.

### D4 — NFR-3 production consistency is test-checked, NOT structural (the `maestro_layer` precedent)

Cross-format consistency between the `threats.md` block and the SARIF `affected_assets[]` bag is enforced in production by a **test check** (spec SC-006 multi-finding equality + SC-002 byte-identity), following the **`maestro_layer` precedent** (ADR-037). Production consistency is **verified**, not structurally **guaranteed**, in the LLM tier. The **structural** guarantee exists only in the Python script/regeneration tier (the reference the tests diff against). We explicitly do **not** claim a structural guarantee on the production path. This corrects the natural over-read that a shared extractor delivers structural NFR-3 in production — it cannot, because production SARIF is LLM-authored. The consistency test is therefore a required, non-optional guard.

### D5 — The structural ideal is explicitly deferred (out of scope — the F-219 aspiration)

A genuinely **structural** production NFR-3 would route production SARIF through the Python scripts: the orchestrator and risk-scorer would write only `.md`, and a deterministic step would generate every `.sarif` (the F-219 `delivery.md` aspiration to wire the regeneration scripts into the live pipeline). That is a pipeline re-architecture — removing SARIF authoring from two agents and regenerating all SARIF baselines — far exceeding F-260b. It is recorded here as the known deferred ideal so a future feature can pick it up without re-deriving the rationale; it is **not** F-260b scope.

---

## Alternatives Considered

### Alternative 1 — Design B: LLM-transcribed value (REJECTED as primary)

The orchestrator and risk-scorer transcribe `affected_assets` into all surfaces directly from the tags they read (exactly the `maestro_layer` pattern); the populator and scripts only verify.

**Pros**: Smaller — no deterministic-populator component and no pipeline-sequencing step.

**Cons**: The **value** is LLM-judged, which relaxes **FR-002 ("not LLM-authored")**. Cross-format consistency (NFR-3) is test-checked in production under **both** designs, so Design B gives up FR-2's deterministic value for no NFR-3 loss relative to Design A.

**Why Not Chosen**: A `dict.get` over a 6-value enum should not be LLM-judged. Design A's deterministic value (D3) is worth the extra component. Design B would also require a **PRD amendment** (an FR-relaxing change is PM scope); PM **declined** the amendment. Design B is retained only as the Triad-electable fallback if effort re-scoping at /aod.tasks finds Design A incompatible with the delivery ceiling.

### Alternative 2 — Structural production SARIF via the Python scripts now (REJECTED — deferred)

Route production SARIF through `generate-*-sarif.py` so the determinism guarantee is structural rather than test-checked.

**Why Not Chosen**: Pipeline re-architecture out of scope for F-260b (D5). Deferred as the F-219 aspiration.

### Alternative 3 — Regeneration-only wiring (REJECTED)

Add `affected_assets` only to the Python scripts and baselines, leaving production authoring untouched.

**Why Not Chosen**: Baselines would pass green while the live `tachi.threat-model` / `tachi.risk-score` runs emit **no** `affected_assets` — the "shipped, adopters see nothing" failure mode. Fails US-1/US-4, which require the tags in live output.

---

## Consequences

### Positive

- ✅ Asset tags reach both adopter-facing surfaces (`threats.md` block + SARIF `affected_assets[]`) from a **single deterministic value origin**.
- ✅ FR-002 satisfied literally — the value cannot drift between runs because it is a `dict.get`, not an LLM judgement (D3).
- ✅ No new enforcement paradigm — consistent with the established `maestro_layer` posture (ADR-037); the team already understands "test-checked, not structural."
- ✅ Low-risk, confined change — the LLM/Python tier boundary is preserved (D1), so no production re-architecture is required.

### Negative

- ⚠️ Production consistency rests on the **test check**, not on structure (D4). If the consistency test is removed or weakened, the two surfaces could silently diverge.
- ⚠️ The determinism guarantee is **dual-tier asymmetric** — structural in the Python scripts, test-checked in production. An accepted asymmetry, not a defect, but it must be understood by anyone reasoning about output integrity.
- ⚠️ The verbatim-copy contract depends on the LLM authoring step honoring "copy, do not derive."

### Mitigation

- The cross-format consistency test (SC-006 multi-finding equality + SC-002 byte-identity) is a **required, non-optional** guard — it fails if any SARIF value diverges from its `threats.md` origin, catching both test-weakening regressions and copy-not-derive violations.
- Acceptance must verify against a **live agent run** (quickstart live-pipeline gate), not `pytest` alone, so the "shipped, adopters see nothing" mode (Alternative 3) cannot pass silently.
- The deferred structural ideal (D5 / F-219) remains the path to collapse the dual-tier asymmetry if a future feature elects it.

---

## References

- Feature 302 Spec: [specs/302-asset-tag-output-wiring/spec.md](../../../specs/302-asset-tag-output-wiring/spec.md) — **FR-002** (deterministic population; "FR-2 literal")
- Feature 302 Plan: [specs/302-asset-tag-output-wiring/plan.md](../../../specs/302-asset-tag-output-wiring/plan.md) — **Architecture Decision AD-1 "The Determinism Mechanism"** (incl. the "Deferred ideal" paragraph and the **Q2 resolution** row)
- Community prototype: **PR #262** (@north-echo, v4.31.0) — froze the 6-value tag enum and the 9.2 CVSS impact-modifier ceiling that F-260b propagates; contribution chain Discussion #246 → PR #262 → #260 → #302
- Schema-versioning precedent: [ADR-026](ADR-026-pattern-classification-mechanism.md) (minor-bump rule)
- Additive-field + serialization-surface precedent: [ADR-028](ADR-028-source-attribution-schema-extension.md)
- Populator-wiring + test-checked consistency precedent: [ADR-037](ADR-037-web-api-coverage-attestation-and-populator-wiring.md) (`maestro_layer`)
- Deferred structural ideal: the F-219 aspiration to route production SARIF through the Python regeneration scripts
