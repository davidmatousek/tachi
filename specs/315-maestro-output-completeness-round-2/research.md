# Research Summary: F-315 MAESTRO Output Completeness (Round 2)

**Scope**: US-2 (#312 maestro-stack infographic all-7 + deterministic empty-layer counts) + US-3 (#313 dedicated CI gate for the invariant test + deterministic refresh of non-gated example PDFs). US-1 Model B (#311) is carved out (separate feature) and out of scope.
**Date**: 2026-06-02
**Grounding**: verified against the live repo by two parallel research agents + an earlier full current-state pass.

---

## Knowledge Base Findings

- **KB Entry 11 — F-098 MAESTRO 7-Layer Coverage Matrix** (`docs/INSTITUTIONAL_KNOWLEDGE.md:491–503`). Core lesson: *"The markdown coverage table is the single source of truth; the PDF data model is seeded from the parsed markdown, so fix the authoring directive, not the downstream filter."* How-to-apply (load-bearing for US-3): *"Regenerate wide example tails deterministically (`SOURCE_DATE_EPOCH=1700000000`) and guard the invariant with a heading-level-agnostic completeness test so the 7-row guarantee can't silently regress."* The entry explicitly names #311/#312/#313 as the deferred follow-ups.
- **F-256 (Entry 3) / F-302 (Entry 9)** — extraction-tier hardening; the CI **lock-step** lesson itself is not in the KB but lives as a header comment in `tachi-pytest.yml:38–47` (F-250 lesson, reinforced by F-256/F-302): *"the `paths:` filter and the `pytest` invocation MUST be kept in lock-step … update BOTH … in the same commit."*
- No KB "Bug Fixes" entries are relevant; no prior bug recurs here.

## Codebase Analysis

**US-2 — the gap is data emission, NOT the template:**
- `templates/tachi/infographics/infographic-maestro-stack.md` **already specifies all-7 rendering**: L107 "Seven Horizontal Bands … L7 (top) through L1 (bottom)"; L124–129 "Empty Layers (zero findings): Still rendered as a band … all 7 layers always visible … Muted appearance … Dash (—)"; L217/L220 "All seven layer labels readable" / "Empty layers identified by text dash". Template is complete.
- `scripts/extract-infographic-data.py` maestro-stack `template_data` block (**L1937–1965**) emits exactly 4 keys: `maestro_layer_distribution`, `most_exposed_layer`, `per_layer_summaries`, `has_maestro_data`. It does **NOT** emit `empty_layers`, `layers_with_findings`, or `layer_count`. Confirmed against golden fixture `tests/scripts/fixtures/golden/maestro-stack.json`.
- Template placeholders `{empty_layers}` / `{layers_with_findings}` / `{layer_count}` (L168, L191, L194) are therefore **agent-derived (non-deterministic)** today.
- `parse_maestro_layer_distribution` (**L1495**) returns only rows present in the parsed markdown table — no canonical-7 backfill. Post-F-098 the table authors 7 rows, so it passes through 7, but the infographic script has no independent guarantee.
- **Fix**: add `empty_layers` / `layers_with_findings` / `layer_count` to the maestro-stack `template_data`, computed from the distribution (`empty = count(finding_count==0)`, `with = count(>0)`, `layer_count = 7`); optionally backfill the distribution to canonical-7 for robustness against table-less/pre-F-098 input. Update the golden fixture + `tests/scripts/test_extract_infographic_data.py`. Canonical layer list comes from `scripts/tachi_parsers.py:MAESTRO_LAYERS` (L44) — no new hard-coded list (ADR-019).

**US-3 — dedicated CI job + deterministic refresh:**
- **Dedicated-job precedent**: `.github/workflows/tachi-mmdc-preflight.yml` — `ubuntu-latest`, Python 3.11 (`actions/setup-python@v5`), narrow `on.pull_request.paths`, direct `python3 scripts/...` invocation with the comment *"Claude Code slash commands cannot run in CI"*. Exact template for a new dedicated MAESTRO job.
- **`tachi-pytest.yml`** is a path-filtered, file-allowlist job on a **2-OS matrix** (macOS bash 3.2 + ubuntu bash 5), scoped to init.sh/substitution/config/asset-tag surfaces. `test_maestro_coverage_invariant.py` is in **neither** the `paths:` list (L65–102) nor the pytest invocation (L172–188). Folding MAESTRO in would broaden a tightly-scoped, double-OS bash-compat job — hence the dedicated-job recommendation.
- **`test_maestro_coverage_invariant.py`** asserts the 7-row guarantee across `examples/**/threats.md` (heading-level-agnostic; excludes `test-output/`; skips files without the table; sources `MAESTRO_LAYERS` from `tachi_parsers`). Its docstring (L25–27) states *"intentionally NOT wired into CI"* — must be removed on wiring.
- **Byte-gated baselines** (`tests/scripts/test_backward_compatibility.py:BASELINE_EXAMPLES`, L45–52): `web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice, maestro-reference`. `SOURCE_DATE_EPOCH = "1700000000"` (L43).
- **Non-gated refresh targets** (no byte-gate → manual "MAESTRO row/order churn only" diff verification): `agentic-app`, `consumer-agent-app`, `predictive-ml-app`, `mobile-banking-app` `sample-report/security-report.pdf` (+ `.baseline`), plus `maestro-reference`'s loose `security-report.pdf`. Known divergences: maestro-reference `.pdf` ≈307 KB off baseline; agentic-app sample-report `.baseline` ≈365 KB off its `.pdf`.
- **`scripts/populate-maestro-coverage.py`** — F-098 regeneration-only harness (explicitly NOT wired into any command); deterministically rewrites an existing `threats.md` "Risk by MAESTRO Layer" table to all-7 canonical rows. Run it on the upstream `threats.md` **before** regenerating PDFs (Architect LOW-1).

## Architecture Constraints

- **ADR directory**: `docs/architecture/02_ADRs/` (47 ADRs). **No new ADR required** — F-098 `delivery.md:81`: *"FR uses existing ADR-020 (MAESTRO classification) + ADR-021 (determinism); no new ADR required."* Same reuse applies (the only ADR-bearing piece, Model B, went to #311).
- **ADR-017** (Deterministic Infographic Extraction): governs US-2 — stdlib-only, shared `tachi_parsers.py`, JSON via `json.dumps(..., sort_keys=True, indent=2)`, no-LLM-fallback. New count fields must stay byte-deterministic.
- **ADR-021** (SOURCE_DATE_EPOCH for Deterministic PDF Comparison): governs US-3 — `1700000000` on the test/regen path only; production PDFs keep wall-clock; baseline regen is manually gated.
- **ADR-020** (MAESTRO Layer Classification): canonical CSA L1–L7 taxonomy (names corrected in F-136); source of `MAESTRO_LAYERS`.
- **ADR-022** (mmdc Hard Prerequisite): the `tachi-mmdc-preflight.yml` dedicated-job model US-3 mirrors.
- **ADR-014** (Gemini optional/best-effort) + **ADR-016** (Infographic Pipeline Decoupling): determinism applies to the spec *data*, not the image step; maestro-stack has a graceful empty-state path.
- **No schema/SARIF change** (F-098 FR-010 precedent; `schemas/finding.yaml` stays 1.9).

## Industry Research

Web research was light by design: the relevant best practices are already codified in the project's own ADRs and conventions, and this is internal tooling (not a user-facing UX surface). The applicable industry-standard patterns and where the repo already encodes them:
- **Golden-file / invariant regression testing** to prevent silent output regressions → `test_maestro_coverage_invariant.py` + the byte-gated baselines (ADR-021). US-3 simply gates an existing invariant test.
- **Reproducible builds via `SOURCE_DATE_EPOCH`** (the cross-ecosystem reproducible-builds standard Typst honors natively) → ADR-021.
- **Narrow, per-concern CI triggers** (path-scoped jobs over monolithic suites) to keep signal legible and minutes low → `tachi-mmdc-preflight.yml` precedent; reinforces the dedicated-job decision.
- **Push determinism upstream** (compute in code, render in the presentation layer) → the US-2 fix moves counting from the LLM agent into the deterministic extractor.

## Recommendations for Spec

1. **Frame US-2 as a data-emission fix, not a template change** — emit `empty_layers`/`layers_with_findings`/`layer_count` deterministically; lock with the golden fixture + extractor test. State explicitly that `maestro-heatmap` is untouched.
2. **Resolve US-3's CI mechanism to a dedicated job** (not a `tachi-pytest.yml` allowlist expansion), per the Architect/Team-Lead recommendation and the `tachi-mmdc-preflight.yml` precedent — and apply the F-250 lock-step rule (paths ⇄ invocation) regardless.
3. **Sequence the PDF refresh as one deterministic pass**: `populate-maestro-coverage.py` on the example `threats.md` first → then regenerate the non-gated PDFs under `SOURCE_DATE_EPOCH=1700000000` → verify only MAESTRO row/order churn. Keep the 6 gated baselines byte-identical; do not expand the gated set.
4. **No new ADR; no schema/SARIF change** — reuse ADR-017/020/021/022.
5. **Two independent stories = one parallel wave** (zero shared files): US-2 touches the infographic extractor/template/agent + its tests; US-3 touches `.github/workflows/`, the invariant test, and example PDFs.
6. **Keep ≤3 NEEDS-CLARIFICATION**: the only genuinely open choices are visual (muted treatment detail) and the exact non-gated file set — both low-impact and resolvable with defaults.
