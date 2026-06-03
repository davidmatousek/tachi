# Research Summary: MAESTRO Matrix Model B (clean vs n/a) — Feature 311

**Date**: 2026-06-03 · **Initiative**: BLP-05 Wave 1 · **PRD**: `docs/product/02_PRD/311-maestro-matrix-model-b-clean-vs-na-2026-06-03.md`

Grounding for the spec. Sources: KB/institutional search, live-code reconnaissance of the three MAESTRO rendering surfaces, the two approved reviewer results (`.aod/results/architect.md`, `.aod/results/team-lead.md`), and a brief external best-practices check.

---

## Knowledge Base Findings

- **The two-state vocabulary already exists** — `.claude/skills/tachi-orchestration/references/coverage-matrix-model.md` (lines 23–63) defines the canonical three-state cell model for the STRIDE matrix: **integer** (deduplicated count) / **`---`** = analyzed-clean ("We looked and found nothing") / **`n/a`** = not-applicable ("We did not look"). Section "Distinction Importance" (55–63): *"All three states must be visually distinguishable."* **This is exactly Model B's semantics, already authored for STRIDE.** Reuse the semantics; do not reinvent (Architect confirmed; matches F-315 MEDIUM-1).
- **KB Entry 11 (F-098) is the governing doctrine** — `docs/INSTITUTIONAL_KNOWLEDGE.md:491–503` + `specs/098-maestro-7-layer/`. Rules carried forward:
  - **Single source of truth = the `threats.md` markdown table.** The author point is the orchestrator markdown directive (`.claude/agents/tachi/orchestrator.md`), mirrored in `output-schemas.md`. The PDF data model is *seeded from the parsed markdown* (`scripts/extract-report-data.py:parse_maestro_data`) — strictly downstream carry-through. *"Treat downstream extractors as carry-through that should only ever narrow from the source, never widen it."*
  - **F-098 FR-011 names #311 directly**: Model B "requires routing component→layer mapping … into the matrix renderer." To know a layer is *n/a* vs *clean* you need component→layer applicability — which the orchestrator already holds at authoring time (Architect validation #1).
  - The clean string is `Analyzed — no findings this scan` (em-dash U+2014). The **markdown cell carries NO trailing period; the Typst prose adds one** — "the only sanctioned cross-format difference" (`specs/098-*/delivery.md:16`). Any new n/a token must specify per-surface punctuation the same way or the cross-surface fixture flags it.
- **KB Entry 12 (F-315)** — `docs/INSTITUTIONAL_KNOWLEDGE.md:507–517`: infographic all-7 backfill + CI gate made code-computed/gated. Model B adds a *third state* to each of those surfaces.
- **Recurring failure mode: hardcoded-string drift across surfaces.** CHANGELOG F-136 (`31356fb`): the Typst template once carried a divergent MAESTRO layer name out of sync with the canonical taxonomy. F-154 (`30f9ad9`): the infographic MAESTRO detection "checks wrong file and pattern." F-134-era: heading-level (h3/h4) drift. Model B introduces a *second* hardcoded string (the n/a wording) into the same Typst template and Gemini prompt — the cross-surface fixture is the guard.

## Codebase Analysis (live-code reconnaissance, verbatim)

**The carried-cell mechanism (the spine of "author once, inherit"):**
- Orchestrator Phase 1 "MAESTRO Layer Classification" (`orchestrator.md:176–186`) classifies every component into L1–L7/Unclassified; recorded in Section 1 (Components) and the dispatch table.
- Section 6 "Risk by MAESTRO Layer" (`output-schemas.md:229–242`) always emits all 7 layers (F-098), table `| MAESTRO Layer | Finding Count | Highest Severity |`. Zero-finding row today = `0` + `Analyzed — no findings this scan` in **Highest Severity**.
- Both extractors read the SAME Section-6 cell as free-text: `highest_severity = row.get("Highest Severity","").strip()` — `extract-report-data.py:282`, `extract-infographic-data.py:1527`. Whatever token the orchestrator writes is inherited by both with **zero parser changes**.

**The renderer hardcoding (Architect HIGH-1 — "inherit ≠ done"):**
- **PDF** `templates/tachi/security-report/maestro-findings.typ:147–155` — branches on `count > 0`; the `else` prints a hardcoded literal `text(size: 10pt, fill: brand-muted, style: "italic")[Analyzed — no findings this scan.]`. **It does not read `highest_severity` at all for the zero case.** A carried n/a token is ignored unless the Typst branches on it → **renderer change required**.
- **Infographic** `templates/tachi/infographics/infographic-maestro-stack.md:124–130, 186–198, 216–223` — instructs Gemini that empty layers (zero findings) get one bucket: "muted … grayed text … dash (—)". Accessibility (line 220) names only the empty-dash text label. **No third state** → template prose + Gemini prompt change required; carried token flows via `per_layer_summaries` (`extract-infographic-data.py:1992`) into `{layer_bands_text}`.

**The second applicability path (Architect MEDIUM-2 / Team-Lead §4 — sharpest divergence point):**
- `extract-infographic-data.py:1539 parse_component_layer_mapping()` independently derives `component_layer_map` from the **Section 1** Components table → feeds `compute_maestro_heatmap()` (1637) → the **maestro-heatmap** infographic (scoped OUT). This is a live second applicability derivation in the same script. The spec MUST declare the **Section-6 carried token authoritative for the stack** and fence `parse_component_layer_mapping` to heatmap-only, so a future refactor cannot re-route the stack through Section 1 and desync it.

**The backfill path (Architect MEDIUM-3):**
- `extract-infographic-data.py:1961–1971` synthesizes any layer absent from Section 6 with `highest_severity: ""` (empty). In production F-098 forces all 7 rows, so backfill is a table-less/partial fallback. But an n/a layer falling through to backfill would render as empty "clean." Spec must require the orchestrator to author the n/a token in the Section-6 row itself, and add a regression that an n/a token **survives the backfill merge** unoverwritten.

**The ordinal invariant (Architect LOW-1):**
- Both extractors run `highest_severity` through `_SEVERITY_ORDINAL.get(..., 0)` for most-exposed tie-break (`extract-report-data.py:417`, `extract-infographic-data.py:1700`). The clean string already dict-misses → 0. The new n/a token MUST likewise map to 0. Make it an explicit invariant + test; assert `compute_most_exposed_layer` never selects a clean/n/a layer (`finding_count==0` already excludes them).

**The heading fragility (Architect LOW-2):**
- `scripts/populate-maestro-coverage.py:25–30` — PDF extractor substring-matches `#### Risk by MAESTRO Layer`; a table under `### ` parses to **zero** layers (empty PDF page). The populator normalizes the heading to `####`. Any fixture/example regen must run that normalization (or assert `#### `).

**The Model-A author/regen tooling:**
- `scripts/populate-maestro-coverage.py:84` — `_ZERO_FINDING_ANNOTATION = "Analyzed — no findings this scan"` (em-dash, no trailing period). Idempotent, ships `--check` drift mode, **examples-regeneration-only — MUST NOT be wired into any command/orchestrator phase** (would create a second source of truth). Model B extends this script AND the orchestrator directive to emit clean-vs-n/a.

**Fixture (Team-Lead §3 — decisive de-risk):**
- `examples/microservices/threats.md` — Section 1 maps components to **only L2, L4, L7**; Section 6 renders all 7. → **L1, L3, L5, L6 are genuinely n/a**; **L7 has a mapped component (Client Application) but 0 findings → clean**; L2 (8)/L4 (14) carry findings. **≥4 n/a + ≥1 clean, no synthetic fixture needed.** Open-Q3 ANSWERED.
- Examples that legitimately churn (≥1 genuine n/a zero-finding layer): **microservices** (4 n/a), **web-app** (3: L1/L3/L5), **free-text-microservice** (4), **mobile-banking-app/sample-report** (5), **mermaid-agentic-app** (3: L4/L5/L6), **agentic-app** (1: L4). Confirmed by Section-1↔Section-6 cross-reference.

## Architecture Constraints

- **No SARIF/schema change is realistic** (Architect validation #2): the token lives in `threats.md` markdown (render-layer/IR), not the SARIF contract. Zero-finding layers emit no SARIF result; CVSS/composite scores are per-finding. SC-003 should assert "no change to the SARIF *schema or emitted results*."
- **Determinism** (`tests/scripts/test_backward_compatibility.py`, ADR-021): PDF byte-determinism pinned by `SOURCE_DATE_EPOCH=1700000000`. Regen procedure: set epoch → `extract-report-data.py` → `typst compile` → byte-compare to `.pdf.baseline`. **6 byte-gated baselines** (`BASELINE_EXAMPLES`: web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice, maestro-reference) must stay byte-identical *after* deliberate regen; non-gated PDFs (agentic-app, sample-reports) are `[MANUAL-ONLY]` visual/binary diff. Run a **drift audit first** (F-315 Decision C) to classify real-churn vs no-drift and drop no-drift targets before regenerating.
- **CI gate to extend in lock-step** (`.github/workflows/tachi-maestro-coverage.yml`, `tests/scripts/test_maestro_coverage_invariant.py`, F-250 contract): the existing invariant checks only *layer presence* (all 7 rows). Model B adds a **cross-surface state-consistency assertion**. F-250 lock-step rule: any new test or author surface MUST update BOTH the workflow `paths:` list AND the pytest invocation in the same commit, or the gate goes false-green. `MAESTRO_LAYERS` imported from `scripts/tachi_parsers.py` (single list). Detector is heading-level-agnostic and globs the corpus dynamically (no hardcoded file count).
- **`tachi_parsers.py` already exists** (1604 lines) and is already the shared authority imported by both extractors and the populator (`MAESTRO_LAYERS`, `SEVERITY_ORDINAL`, `parse_markdown_table`). The ADR contrast is therefore "add a token-classifier helper to the existing shared parser, fed by the carried cell" vs "carry the token and classify inline" — NOT "build a new shared module" (Architect MEDIUM-1 framing fix).

## Industry Research

- **SARIF 2.1.0** (OASIS) `result.kind` distinguishes **`pass`** (rule evaluated, no issue = analyzed-clean) vs **`notApplicable`** (rule not applicable to the artifact = out of scope) vs `fail` — the closest external analogue to `---`/`n/a`, existing precisely so consumers differentiate "ran clean" from "not run." (https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
- **NIST/CIS** control-status taxonomies and **AWS Security Hub** control statuses separate "passed / no findings" from "Not Applicable (N/A)" (the latter justified). Confirms analyzed-clean vs not-applicable is an established convention. Model B is **pattern reuse, not novel design**.

## Recommendations for Spec

1. **Three states in the Section-6 Highest-Severity cell**, authored once by the orchestrator from the component→layer mapping it already holds:
   - findings → severity label (unchanged);
   - **clean** (≥1 mapped component, 0 findings) → `Analyzed — no findings this scan` (**UNCHANGED** — preserves no-spurious-diff for all-in-scope examples);
   - **n/a** (0 mapped components) → a NEW distinct documented token (`Not applicable — no components map to this layer`).
2. **Inherit via a pure token-classifier**, not a second derivation: add `classify_maestro_coverage_state(finding_count, highest_severity) → "findings" | "clean" | "not_applicable"` to `tachi_parsers.py`; both extractors emit a `coverage_state` enum into `report-data.typ` (PDF) and `maestro-stack.json` (infographic). Renderers branch on the enum. The enum (code-computed, not agent-counted) also delivers machine-discernibility (US-311.2).
3. **Per-surface n/a visual state (Open-Q2 resolved)**: PDF Typst zero-finding row branches clean vs n/a prose with distinct muted styling; infographic gains a documented third band state + "N/A" accessibility text label.
4. **Single authority + fences**: Section-6 token is sole applicability source for the 3 in-scope surfaces; `parse_component_layer_mapping` stays heatmap-only; n/a token survives backfill; n/a ⇒ ordinal 0; fixture regen runs heading normalization.
5. **ADR-047** records carried-token-as-sole-authority (option c) vs shared-helper re-derivation (option a); option (b) duplicate-parser already rejected.
6. **Fixture = `examples/microservices`** (no synthetic); extend `tachi-maestro-coverage.yml` with the cross-surface consistency assertion in F-250 lock-step. Enumerate the ≥6 churning example baselines as a discrete, diff-reviewed regen task.
7. **Single feature, do not split** (Team-Lead); confirm `v4.40.0` tag present before deliver.
