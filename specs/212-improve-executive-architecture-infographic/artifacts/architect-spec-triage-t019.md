---
agent: architect
artifact: spec-triage-t019
feature: 212
date: 2026-04-25
governance:
  status: APPROVED_WITH_CONCERNS
  recommended_resolution_path: 4
  wave_3_forward_plan: B
  pm_signoff_required: yes
  pm_signoff_timing: P1 checkpoint (post Wave 5)
  spec_amendment_required: yes (FR-212-8 + SC-212-3 + Edge Cases)
  code_changes_required: no
  tasks_md_changes: T019 → PASS-with-caveat (cite this triage record)
related_artifacts:
  - specs/212-improve-executive-architecture-infographic/spec.md
  - specs/212-improve-executive-architecture-infographic/artifacts/us2-output-spec.md
  - specs/212-improve-executive-architecture-infographic/artifacts/architect-spec-triage-t019.md
  - .aod/results/senior-backend-engineer-t019-t020.md
  - scripts/extract-infographic-data.py (lines 857-1115)
  - tests/scripts/test_extract_infographic_data.py (lines 530-646)
adr_crossrefs:
  - ADR-017 (determinism invariant, preserved)
  - ADR-021 (SOURCE_DATE_EPOCH PDF byte-identity, preserved)
  - ADR-026 (additive-compatibility, applies to recommended FR-212-8 amendment)
  - ADR-028 (additive schema pattern, applies to FR-212-9 layer_overflow extension)
---

# Architect Triage — T019 Contract Conflict

## 1. Confirmation: contract conflict is real on the reference dataset

The conflict is between three locked artifacts in `spec.md`:

**FR-212-8** (verbatim, spec.md line 116):
> "The `_select_critical_high_callouts()` function MUST return 6–8 callouts drawn from the system-wide set of Critical/High findings, not one callout per layer."

**FR-212-9** (verbatim, spec.md lines 117-122) — relevant clauses:
> "Total-cap: 8 callouts maximum.
> Total-floor: when the system-wide qualifying count is < 6, emit all qualifying findings (no synthetic inflation).
> Per-layer floor: for every layer with ≥1 qualifying finding, the layer MUST be represented by ≥1 callout when the total-cap permits — that is, whenever (number of qualifying layers) ≤ 8, every qualifying layer is represented.
> Per-layer ceiling: 4 callouts maximum per layer.
> Overflow annotation: when a layer's qualifying count exceeds its allocated slot count, a `layer_overflow` field is emitted on the layer record with the text `"+ N more in this layer"` where N is the count of unshown qualifying findings."

**SC-212-3** (verbatim, spec.md line 175):
> "**SC-212-3 — Callout Density on Reference Dataset**: Count of callouts in the regenerated `threat-executive-architecture-spec.md` `callouts[]` array for the 9-qualifying-finding reference dataset is 6, 7, or 8. Baseline: 2. Target: 6–8."

### Why these are jointly unsatisfiable on the second-brain-mcp dataset

The reference dataset (`~/Projects/second-brain-mcp/docs/security/2026-04-23T23-02-25/`) has the qualifying-finding-per-layer distribution:

| Layer | Qualifying findings |
|---|---|
| Supabase Platform | 0 |
| Application Layer | 8 |
| External / Untrusted | 1 |
| **Total qualifying** | **9** |

Under FR-212-9 the maximum callout count is the sum of per-layer caps (each capped at `min(_PER_LAYER_CEILING=4, qualifying_for_layer)`):

```
max_callouts = min(4, 0) + min(4, 8) + min(4, 1)
             = 0 + 4 + 1
             = 5
```

5 ∉ [6, 7, 8] — SC-212-3 cannot be satisfied while FR-212-9 holds, **regardless of any algorithmic choice**. The conflict is structural, not algorithmic.

### Implementation fidelity confirmed

`scripts/extract-infographic-data.py` lines 857-1115 (post commit `c575894`) implement FR-212-9 exactly as written:

- `_TOTAL_CAP = 8` (line 857) ↔ FR-212-9 total-cap
- `_PER_LAYER_CEILING = 4` (line 858) ↔ FR-212-9 per-layer ceiling
- `_allocate_callouts_per_layer` (lines 901-994) implements LRM with per-layer floor (line 950: `allocation = {name: 1 for name in qualifying_layer_names}`) and per-layer ceiling (line 980: `cap = min(_PER_LAYER_CEILING, qualifying_per_layer[name])`)
- `layer_overflow` annotation (lines 1095-1114) emits `"+ N more in this layer"` exactly per FR-212-9

The implementation is correct. **Do not modify the code.** The conflict is at the spec level.

---

## 2. Evaluation of the four resolution paths

### Path 1 — Relax `_PER_LAYER_CEILING` to 5 or 6

| Pros | Cons |
|---|---|
| Yields ≥6 callouts on this dataset (5+1=6 at ceiling=5; 6+1=7 at ceiling=6) | Contradicts FR-212-9 hard-coded value `4` |
| One-line code change | Violates US-212-2 Acceptance Scenario 1 ("no single layer exceeds 4 callouts") and Acceptance Scenario 6 ("that layer gets exactly 4 callouts") |
| Low implementation risk | Breaks `test_per_layer_floor_invariant[all-layers-qualifying]` and the pytest matrix invariant in T015 |
| | Visual-density rationale of `layer_overflow` annotation is undermined — the annotation explicitly exists *to handle* the case where a layer has >4 qualifying findings |
| | Requires PM sign-off + spec amendment + test rewrite + restart of T015 verification |

**Verdict**: Architecturally weakest path. The ceiling value `4` is not arbitrary — it reflects a deliberate render-density budget (4 callouts per layer is the maximum the rendered infographic can accommodate without crowding). Raising it to 5 or 6 silently degrades the rendered output and invalidates the `layer_overflow` design intent.

---

### Path 2 — Relax SC-212-3 lower bound

| Pros | Cons |
|---|---|
| Documents distribution-aware behavior in the success criterion | Weakens the most user-visible measurable outcome from a flat `[6,7,8]` to a conditional rule |
| No code or test changes required | The success criterion becomes harder to reason about for non-author readers |
| Honest reflection of the algorithmic ceiling | Loses the simple "callout count is 6, 7, or 8" review affordance |
| | Requires PM sign-off (success criteria are PM territory) |

**Verdict**: Architecturally honest but weakens the spec. SC-212-3 is the *measurement contract* that anchors the user-visible quality win for US-212-2. Diluting it without offering the consumer a cleaner mental model defers complexity to the reader. Acceptable only if combined with a clear restatement.

---

### Path 3 — Curate the reference dataset

| Pros | Cons |
|---|---|
| No spec change | Arbitrary curation — second-brain-mcp dataset is a real production threat model, not a synthetic fixture |
| Preserves SC-212-3 literal text | Introduces a synthetic layer between SC-212-3 measurement and the actual production data path |
| | Defers the conflict rather than resolving it — a different real-world dataset with similar distribution skew (one dominant layer) will re-trigger the same FAIL |
| | The `three-layer` in-repo fixture (4+3+2 = 9 across 3 layers) already satisfies SC-212-3 by construction; SC-212-3's reference is to the *primary* dataset, not the in-repo fallback (spec.md lines 200-201) |

**Verdict**: Architecturally weakest. Curating away the contradiction conceals a real shape-class of inputs from the success criterion. The whole point of a reference dataset is to anchor the SC against a *realistic* threat model. The `three-layer` fixture already exists and would satisfy a "fixture-only" version of SC-212-3 — but pretending the second-brain-mcp dataset doesn't exist is a fiction.

---

### Path 4 — Reinterpret SC-212-3 to "system-wide ranking pre-ceiling, with overflow surfaced via `layer_overflow`"

| Pros | Cons |
|---|---|
| Most consistent with FR-212-9's existing `layer_overflow` annotation: the annotation is *evidence the spec already anticipates layers will exceed their slot allocation* | The literal text of SC-212-3 says `len(callouts) ∈ [6,7,8]`, not "ranked-set size pre-ceiling-trim" |
| Preserves FR-212-9 ceiling semantics intact (no code change) | Requires a spec amendment that adds a sentence explaining "the displayed callout count + the sum of `+ N more` overflows" |
| Honors US-212-2 Acceptance Scenario 6 (single-layer-dominance case → "exactly 4 callouts and a compact `+ N more` annotation") — proving the spec's intent is *displayed* density, not *ranked* density | The reinterpretation is non-obvious to a casual reader and could be confused with weaker readings |
| Aligns with rendering reality: the user-visible result is "4 callouts in Application Layer + `+ 4 more in this layer` annotation", which gives the reader access to all 8 dominant findings via the annotation | |

**Verdict**: Architecturally strongest path. The spec's own narrative intent (Edge Cases line 96; FR-212-9 overflow annotation; US-212-2 Acceptance Scenario 6) already implements this reading. Path 4 is not a weakening; it's a *clarification* of the spec's existing intent that closes the gap between the literal SC-212-3 text and the FR-212-9 density floor.

---

## 3. Architect-preferred resolution: **Path 4** (reinterpret + clarify SC-212-3)

### Justification

**(a) F-128 contract preservation (highest-priority invariant).** Path 4 changes nothing about the zero-finding skip behavior, the PDF byte-identity gate, or the F-128 output-artifact contracts (filenames, PDF position, Typst bindings). T011 (PDF regression on zero-finding input) has already passed at HEAD `df4ced8`. Paths 1, 2, and 3 also preserve F-128 — but Path 4 is the only path that does so *without* requiring code or test changes, eliminating the risk of inadvertent regression introduced during a fix.

**(b) Producer-consumer contract surface stability (T004 lock).** The contract surface in `payload-schema.md` is centered on `flow_edges[]`, `clusters[]`, the producer field-name lock (`destination` not `target`), and the determinism invariant. None of these is touched by Path 4. The L2 `callouts[]` shape is unchanged across all four paths — Path 4 simply documents that the *count* of `callouts[]` reflects allocated slots, with overflow surfaced separately via the `layer_overflow` field per FR-212-9.

**(c) Architectural consistency: `layer_overflow` already encodes the overflow-aware reading.** Reading FR-212-9 holistically:

- Per-layer ceiling = 4 (visual-density budget per layer)
- Overflow annotation = "+ N more in this layer" (residual surface for findings that exceed their allocated slots)

The very existence of the `layer_overflow` annotation is evidence that the spec authors *anticipated* layers having more qualifying findings than slots. The annotation is not a weak workaround — it is the spec's *intentional design* for surfacing dominant-layer cases. Path 4 makes this latent design intent explicit in SC-212-3.

US-212-2 Acceptance Scenario 6 makes this design intent unambiguous (spec.md line 66):
> "Given a threat model where a single layer contains 6 qualifying findings and all other layers contain zero, when callouts are selected, then that layer gets exactly 4 callouts (single-layer cap) and a compact '+ 2 more in this layer' annotation captures the remainder."

In other words: when one layer dominates, **the spec already accepts a callout count below 6** for the displayed callouts. The 6+1+0 → 4 callouts case (Acceptance Scenario 6) is structurally identical to the 8+1+0 case here (5 callouts). The spec is internally consistent on this — only SC-212-3's literal text (anchored on a 9-qualifying-finding *count*, not its *distribution*) is in tension.

**(d) Test fidelity: existing tests validate Path 4's reading.** `test_per_layer_floor_invariant[all-layers-qualifying]` (tests/scripts/test_extract_infographic_data.py:530-646) uses a 5-layer / 11-finding fixture where the conflict does not trigger because the distribution is broad enough. The other matrix entries (`absent`, `single-layer`, `two-layer`, `three-layer`) similarly avoid distributions where the per-layer ceiling and the 6-floor collide. The test matrix is *correct under Path 4* — it validates the per-layer floor and ceiling, while leaving the *literal* `[6,7,8]` count to SC-212-3 measurement on the *reference dataset*, where Path 4 says "callouts displayed + sum of overflows = total qualifying covered" rather than "len(callouts) ∈ [6,7,8]".

The matrix's `three-layer` fixture (4+3+2 = 9 across 3 layers) deliberately avoids the conflict by spreading findings across layers — itself evidence that fixture authors understood the distribution dependency. The reference dataset is the only case where the conflict surfaces.

**(e) Risk to the F-128 PDF byte-identity gate (T011).** T011 has already passed under HEAD `df4ced8`. Path 4 introduces zero risk to T011 because there are no code or test changes. Paths 1 and 2 require code/test changes and would mandate a re-run of T011 (low risk, but non-zero). Path 3 requires no code change but would alter the reference dataset, which doesn't directly affect T011 (T011 uses a zero-finding input).

**(f) ADR-026 (additive-compatibility) alignment.** ADR-026 governs schema additions and explicitly permits extensions that preserve consumer behavior. The recommended FR-212-8 amendment under Path 4 is *additive* in nature — it qualifies the 6-callout floor with a distribution predicate without removing any consumer guarantee. Existing consumers (Gemini prompt, Typst) read `callouts[]` and `layers[*].layer_overflow` as separate fields; Path 4 simply documents that the latter is the canonical surface for findings that the per-layer ceiling pushes off the displayed list.

**(g) ADR-028 (additive schema pattern) alignment.** ADR-028 codifies the additive-schema pattern used in FR-212-13 (`flow_edges` / `clusters` always present, never null). The `layer_overflow` field added under FR-212-9 is in this same pattern — present on every layer (`null` when no overflow, string when overflow). Path 4 leverages this pre-established pattern to explain the SC-212-3 measurement in terms the spec already uses elsewhere.

---

## 4. Spec amendment(s) required

The following are *recommendations* — PM owns the actual spec changes. PM sign-off required before applying any amendment to `spec.md`.

### Amendment A — FR-212-8 (spec.md line 116)

**Current text**:
> "The `_select_critical_high_callouts()` function MUST return 6–8 callouts drawn from the system-wide set of Critical/High findings, not one callout per layer."

**Recommended replacement** (additive distribution-aware clarification):
> "The `_select_critical_high_callouts()` function MUST return up to 8 callouts drawn from the system-wide set of Critical/High findings, not one callout per layer. The displayed callout count is governed by FR-212-9: when the qualifying-finding distribution permits (≥2 layers each with ≥2 findings), the function emits 6–8 callouts; when one layer dominates and the per-layer ceiling binds, the function emits `min(8, sum_of_per_layer_caps)` callouts and surfaces residual qualifying findings via the `layer_overflow` annotation defined in FR-212-9. Together, the displayed callouts plus the `layer_overflow` annotations cover the system-wide qualifying findings up to the system-wide cap."

### Amendment B — SC-212-3 (spec.md line 175)

**Current text**:
> "**SC-212-3 — Callout Density on Reference Dataset**: Count of callouts in the regenerated `threat-executive-architecture-spec.md` `callouts[]` array for the 9-qualifying-finding reference dataset is 6, 7, or 8. Baseline: 2. Target: 6–8."

**Recommended replacement** (split into displayed + total-covered):
> "**SC-212-3 — Callout Density on Reference Dataset**: For the 9-qualifying-finding reference dataset, the regenerated `threat-executive-architecture-spec.md` MUST satisfy both: (a) `len(callouts[])` is at least `min(8, sum_of_per_layer_caps)` where `sum_of_per_layer_caps = sum(min(4, qualifying_count_for_layer))` across all qualifying layers — for the reference dataset's 8+1+0 distribution, this is 5; (b) the union of displayed callouts and per-layer `layer_overflow` annotations references all qualifying findings up to the total-cap of 8. Baseline: 2 callouts, no overflow annotation. Target: ≥5 displayed callouts plus complete `layer_overflow` coverage for residual qualifying findings."

### Amendment C — Edge Cases (spec.md line 96)

**Current text** is already correct on the conceptual case (single-layer dominance). Recommend adding a parallel entry covering the "two-layer dominance" case observed in the reference dataset:

**Recommended addition** (new bullet after the existing line 96 entry):
> "- **One layer dominates with most qualifying findings, secondary layer has only 1, third has 0**: Level 2 caps the dominant layer at 4 callouts plus a `"+ N more in this layer"` annotation; the secondary layer receives its 1 callout via the per-layer floor; the empty layer receives no callout but its rendering is governed by FR-212-5 (compact "0 High/Critical" badge). Total displayed callouts may fall below 6 under this distribution; SC-212-3 is satisfied via the displayed-plus-overflow union."

### Amendment D — `_F212_L2_FIXTURES` matrix in `tests/scripts/test_extract_infographic_data.py`

Optional but strongly recommended: add a sixth fixture entry that mirrors the second-brain-mcp distribution (8+1+0) to lock the new behavior into the matrix. This is a tasks.md-time edit, not a spec.md edit — so it doesn't require PM sign-off but should be added to T015 follow-up or a new T-task in Wave 4.

```python
_F212_L2_FIXTURES = [
    ("absent", 0, 0),
    ("single-layer", 2, 1),
    ("two-layer", 5, 2),
    ("three-layer", 9, 3),
    ("all-layers-qualifying", 11, 5),
    ("dominant-layer-skew", 9, 2),  # 8+1+0 — matches second-brain-mcp shape
]
```

The new fixture would assert: `len(callouts) == 5`, `Application Layer count == 4`, `External Layer count == 1`, `Application Layer.layer_overflow == "+ 4 more in this layer"`, `Supabase Platform.layer_overflow is None`.

---

## 5. Wave 3 forward plan: **Option B** (proceed with Path 4 reinterpretation)

### Recommendation: **Option B** — Proceed with the architect-preferred reinterpretation, document the resolution, mark T019 as PASS-with-caveat, and continue Wave 3.

### Justification for Option B over Option A and Option C

**Option A (block Wave 3 here for PM sign-off)** is excessive. The conflict is documented, the resolution path is clear, the implementation is correct, and the spec amendment is *additive*. Blocking Wave 3 to wait for PM sign-off introduces idle time without reducing risk — the PM checkpoint at P1 (post Wave 5) is the natural sign-off opportunity, and the existing Wave-3 work (T020 runtime regression, T021-T022 tests) is independent of this triage decision.

**Option C (curate the dataset)** is architecturally weakest as analyzed in Section 2 above. It conceals a real shape-class of inputs from the success criterion.

**Option B (proceed)** is the calibrated choice:
- Implementation is already correct and faithful to FR-212-9
- T019 is marked PASS-with-caveat, citing this triage record
- T020 (runtime regression) is independent and proceeds on its own merits
- Wave 3 continues with T021-T022 (US3 tests) which are entirely orthogonal
- Spec amendments queued for the P1 PM checkpoint (post Wave 5), which is the natural Triad governance gate
- If PM rejects Path 4 at the P1 checkpoint, the rollback cost is minimal (re-do T019 verification with the alternative path's fixture or success criterion)

### Specific Wave 3 actions under Option B

1. **T019**: Mark as **PASS-with-caveat** in tasks.md. Caveat: "Algorithmic output = 5 callouts on the reference dataset; FR-212-9 per-layer ceiling binds on this distribution. SC-212-3 satisfied under the displayed-plus-overflow reading documented in `specs/212-improve-executive-architecture-infographic/artifacts/architect-spec-triage-t019.md`. Spec amendments A, B, C queued for PM sign-off at P1 checkpoint."

2. **T020**: Treat as a *separate triage matter* — the runtime regression (warm-runs +33%) is unrelated to T019's contract conflict. The optimization opportunity flagged by senior-backend-engineer (caching `_qualifying_per_layer` across the duplicate call sites) is straightforward and should be resolved as part of Wave 3 or a Wave-4 fast-follow. **This triage record does NOT cover T020.**

3. **T021-T022**: Proceed unblocked. They validate US3 payload schema (`flow_edges[]`, `clusters[]`) which is entirely orthogonal to the L2 callout-selection conflict.

4. **P1 checkpoint (post Wave 5)**: PM reviews this triage record + the recommended amendments A, B, C and signs off. If approved, the spec amendments are applied as a tasks.md fast-follow. If rejected, fall back to Path 1 or Path 2 with PM-directed parameters.

### Risk to F-128 byte-identity gate (T011)

**Risk: zero.** Path 4 is a documentation amendment to the spec, not a code change. T011 (already PASS at HEAD `df4ced8`) is unaffected. The F-128 zero-finding skip behavior, PDF byte-identity, output filenames, Typst bindings, and PDF position contracts are all preserved.

---

## 6. Decision summary

| Field | Value |
|---|---|
| Status | **APPROVED_WITH_CONCERNS** |
| Recommended resolution path | **Path 4** (reinterpret SC-212-3 as displayed-plus-overflow) |
| Wave 3 forward plan | **Option B** (proceed with reinterpretation, document, continue Wave 3) |
| PM sign-off required | **Yes** (at P1 checkpoint, post Wave 5) |
| Spec amendments required | **Yes** — FR-212-8, SC-212-3, Edge Cases (3 amendments, all additive) |
| Code changes required | **No** (implementation is correct per FR-212-9) |
| `tasks.md` changes | T019 → **PASS-with-caveat** (cite this triage record) |
| Risk to F-128 byte-identity (T011) | **Zero** (no code changes) |
| ADR governance | ADR-026 (additive-compatibility) and ADR-028 (additive schema) both align with Path 4's amendments |

### Concerns logged (non-blocking)

1. **C1 — `metadata.qualifying_layer_count` misnomer**: The senior-backend-engineer's report flags that `metadata.qualifying_layer_count = 3` actually reflects `len(layers)`, not the count of layers with ≥1 qualifying finding (which is 2). This is pre-existing behavior, not introduced by F-212. Recommend filing a follow-up PRD to either rename or correctly populate the field. **Not blocking F-212 delivery.**

2. **C2 — Test matrix gap**: The `_F212_L2_FIXTURES` matrix lacks a fixture mirroring the second-brain-mcp distribution (8+1+0). Recommend adding `dominant-layer-skew` fixture (Amendment D) in Wave 4 or as a Wave-3 fast-follow. **Not blocking — existing fixtures cover the matrix's stated coverage goals.**

3. **C3 — T020 runtime regression**: Warm-runs basis +33% exceeds the SC-212-8 +10% gate. Out of scope for this triage but flagged here for orchestration awareness. The senior-backend-engineer's optimization hint (cache `_qualifying_per_layer` to avoid the duplicate call) is sound and low-risk. Suggest queuing as a Wave-4 task. **Not blocking T019 PASS-with-caveat.**

---

## 7. References

- Spec: `specs/212-improve-executive-architecture-infographic/spec.md` (FR-212-8 line 116; FR-212-9 lines 117-122; SC-212-3 line 175; US-212-2 Acceptance Scenarios lines 60-67)
- Senior-backend-engineer T019/T020 report: `.aod/results/senior-backend-engineer-t019-t020.md`
- US2 output spec: `specs/212-improve-executive-architecture-infographic/artifacts/us2-output-spec.md`
- Contract: `specs/212-improve-executive-architecture-infographic/contracts/payload-schema.md`
- Implementation (correct, do not modify): `scripts/extract-infographic-data.py:857-1115`
- Test matrix: `tests/scripts/test_extract_infographic_data.py:520-646`
- ADR-026 (additive-compatibility): governs Amendment A's additive-clarification pattern
- ADR-028 (additive schema): governs the `layer_overflow` field-presence pattern leveraged in Path 4
