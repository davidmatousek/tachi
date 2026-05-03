# Research Summary — Feature 212: Improve Executive-Architecture Infographic

**Feature**: 212 — Improve Executive-Architecture Infographic
**PRD**: [docs/product/02_PRD/212-improve-executive-architecture-infographic-2026-04-24.md](../../docs/product/02_PRD/212-improve-executive-architecture-infographic-2026-04-24.md)
**Research conducted**: 2026-04-24

---

## 1. Knowledge Base Findings

**Gemini prompt scaffold discipline** — `gemini-prompt-construction.md` mandates VERBATIM preamble + postamble when `prompt_scaffold` is present. The current `executive-architecture` template uses the **fallback path** (no `prompt_scaffold` object) — Level 1 should lock the rewritten prompt text verbatim in the skill reference file (not dynamically composed).

**F-128 scope-bleed lesson** — Parallel Claude sessions cross-contaminated git state at delivery (KB-026); two non-F-128 bug fixes were bundled into the PR because baseline generation required them (Decision 4/5). F-212 must list scope files up-front.

**F-209 contract-drift lesson (just landed)** — Root pattern: no machine-checked schema between producer and consumer → 5 silent mismatches. Fix added `tests/scripts/test_extractor_contract_fixes.py` with 6 tests. F-212 Level 3 MUST either (a) align payload field names to actual `parse_scope_data` producers, or (b) document an explicit rename adapter. Choosing (a) is cleaner — matches Architect M2 concern.

**F-189 precedent** — "Additive schema with empty-array when absent" pattern validated. Spec testing used absent/empty/single/multi matrix. F-212 Level 3 should mirror this test pattern.

**Determinism toolkit** — ADR-017 (deterministic extraction), ADR-021 (`SOURCE_DATE_EPOCH=1700000000` for byte-identical baselines), ADR-028 (additive schema extension). All three apply to F-212.

---

## 2. Codebase Analysis

### Confirmed function signatures and output shapes

**`parse_scope_data` output** (`scripts/tachi_parsers.py:904`):
- `data_flows[]` fields: `source`, **`destination`** (not `target`), `data`, `protocol`
- `boundary_crossings[]` fields: `crossing`, `from-zone`, `to-zone`, `components`, `controls`
- `trust_boundaries[]` fields: `zone`, `trust-level`, `components`

**`_compute_data_flows`** (`scripts/extract-infographic-data.py:1002`) emits entries with `source`, `destination` fields.

**`_compute_boundary_crossings`** (`scripts/extract-infographic-data.py:1037`) emits entries with `from_zone`, `to_zone`, `crossing_point` (computed from `components`), `finding_count`.

**Resolution of Architect M2**: The natural source for `clusters[]` is **`trust_boundaries[]`** (zones with component members), not `boundary_crossings[]` (edges between zones). PRD used misleading terminology — spec clarifies `clusters[]` is trust-zone membership, `flow_edges[]` is data-flow edges; neither is sourced from `boundary_crossings[]`.

### Sort pattern (`_compute_trust_zones:784`)

```python
_TRUST_LEVEL_ORDER = {"trusted": 0, "semi-trusted": 1, "untrusted": 2}
zones.sort(key=lambda z: (_TRUST_LEVEL_ORDER.get(z["trust_level"], 99), z["name"]))
```

**Resolution of Architect M3**: `clusters[]` members sort by (trust-level tier, zone name case-insensitive). `flow_edges[]` sort by (source case-insensitive, destination case-insensitive).

### Callout selection (`_select_critical_high_callouts:857`)

Current: per-layer dedup — exactly one Critical/High per layer.
Target: top 6-8 system-wide with weighted per-layer distribution + floor-guarantee.

### Payload return dict (`_build_executive_architecture_payload:981-986`)

Current: `metadata`, `layers`, `callouts`, `severity_distribution`.
Level 3 additions: `flow_edges[]`, `clusters[]` (always present — empty arrays when absent from `threats.md`).

### Tests

Existing: `tests/scripts/test_extract_infographic_data.py` — fixture at `tests/scripts/fixtures/exec_arch/agentic_app`. Tests currently validate per-layer callout count (will need update for 6-8 callouts).
New (Level 3): `tests/scripts/test_executive_architecture_payload.py` with absent/empty/single/multi matrix (F-189 precedent).

### Reference dataset verification

`/Users/david/Projects/second-brain-mcp/docs/security/2026-04-23T23-02-25/threats.md` — **both `### Data Flows` (line 61) and `### Boundary Crossings` (line 126) present**. Level 3 can validate against this dataset.

**Fallback**: If sibling repo unavailable, spec declares `tests/scripts/fixtures/exec_arch/agentic_app/threats.md` as in-repo fallback; all CI validation uses the in-repo fixture. Sibling-repo validation is a local developer affordance, not a CI gate.

---

## 3. Architecture Constraints

**ADR-017 (Deterministic Infographic Extraction)**: Re-running extractor on identical input MUST produce byte-identical payloads. F-212 Levels 2 & 3 must preserve.

**ADR-021 (SOURCE_DATE_EPOCH)**: Wrap all regression runs in `SOURCE_DATE_EPOCH=1700000000` for PDF byte-identity comparison.

**ADR-028 (Source Attribution Schema Extension)**: Canonical pattern for additive schema fields — new fields emit as empty arrays (not `null`, not missing).

**Constitution §III (Backward Compatibility)**: F-128 skip-behavior (zero Critical/High → no image, `has-executive-architecture=false`) must remain byte-identical in PDF output.

**F-128 contracts preserved**:
- Output filenames: `threat-executive-architecture.jpg`, `threat-executive-architecture-spec.md`
- PDF position: pages 2–3 after Executive Summary
- Typst bindings: `has-executive-architecture`, `executive-architecture-image-path`
- Skip behavior: zero Critical/High → template skipped
- Portrait orientation
- All 5 other templates unchanged

**Palette resolution** (PM L1 concern, Design Q1): **EXTEND — not inherit, not fork.**
- Inherit severity colors (`#DC2626` Critical, `#EA580C` High) from `visual-design-system.md` for callout borders — matches canonical palette
- Extend with 5-color deterministic pastel cycle for layer fills: `["#F0F4FF", "#FFF4F0", "#F0FFF4", "#FFF0F8", "#F8F0FF"]` — already committed in the schema, cycled by layer index
- This is EXTEND-with-additive (not fork, not pure inherit) — no existing template colors change

---

## 4. Industry Research

**Gemini 3 Pro Image prompt patterns for flow diagrams** — directive structured prompts with named components work. Pair "arrow" with explicit head style; bare words like "flow" produce undirected lines. Begin prompt with "schematic diagram with shapes and arrows" to defeat the dominant failure mode (text-only output). Source: [Google Gemini 2.5 Flash Image prompting guide](https://developers.googleblog.com/en/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/), [Nano Banana ultimate prompting guide](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana).

**Callout density on executive pages** — 5–9 annotations is the upper bound before cognitive overload (Miller's 7±2 refined to 3–5 working memory items; 46.7% of dashboard users cite overload as top problem). F-212's 6–8 target sits inside the recommended band. Source: [Fegno cognitive load in dashboards](https://www.fegno.com/designing-enterprise-dashboards-with-cognitive-load-theory/), [UX Magazine four guidelines](https://uxmag.com/articles/four-cognitive-design-guidelines-for-effective-information-dashboards).

**Weighted-from-K-groups allocation**: **Largest Remainder Method (LRM / Hamilton / Hare-Niemeyer)** is the canonical citable answer. LRM is the only apportionment method satisfying the **quota rule** (each group gets floor or ceiling of its proportional share) — which gives F-212's "every qualifying layer gets ≥1 callout when allocation permits" guarantee. Tie-breaks: remainder descending → group size descending → group name lexicographic. Source: [Largest remainder method (Wikipedia)](https://en.wikipedia.org/wiki/Largest_remainder_method).

---

## 5. Recommendations for Spec

### Resolutions of Triad concerns

- **PM M1** (L3 reference dataset verified) — RESOLVED: verified both sections present; document in-repo fallback in Dependencies.
- **PM L1** (palette 3-way) — RESOLVED: EXTEND-with-additive (inherit severity colors; add deterministic 5-pastel layer cycle).
- **PM L2** (CISO persona) — noted as Assumption (inferred from consultant feedback; direct CISO validation is post-delivery).
- **Architect H1** ("superset or reorder" not enforceable) — RESOLVED via **per-layer floor-rule invariant** (see FR-212-2 below): *"every qualifying layer with ≥1 Critical/High finding MUST appear in `callouts[]` with at least one entry when total-cap allows (i.e., number of qualifying layers ≤ 8)."* Enforceable by fixture matrix: absent / 1-layer / 2-layer / all-qualifying.
- **Architect M2** (schema field drift) — RESOLVED: align `flow_edges[]` entries to `source`/`destination` (producer match); source `clusters[]` from `trust_boundaries[]` (not `boundary_crossings[]`) with `name`/`members` fields derived from `zone`/`components`.
- **Architect M3** (cluster sort determinism) — RESOLVED: mirror `_compute_trust_zones` pattern — sort `clusters[]` by `(trust_level_order, name_lowercased)`; sort `flow_edges[]` by `(source_lowercased, destination_lowercased)`.
- **Architect L4** (drift detection follow-up) — tracked in Open Questions; not blocking.
- **Team-Lead M1** (Phase 1 estimate) — deferred to plan/tasks (3–5h budget).
- **Team-Lead M2** (dataset dependency + fallback) — documented in Dependencies.
- **Team-Lead L1, L2** — deferred to plan/tasks (owner names, regression ID-superset check).

### Additional spec decisions

- **Truncation of very-large `flow_edges[]`** (>50 edges): cap at 50 entries after sort; emit warning; defer richer policy to follow-up PRD.
- **"+ N more" compact annotation wording**: "+ N more in this layer" — short, factual, non-categorical.
- **Drift regression**: add `tests/scripts/test_executive_architecture_payload.py` to the L3 scope (Architect L4 concern partial resolution).
