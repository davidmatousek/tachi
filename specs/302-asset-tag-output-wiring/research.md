# Research Summary: Asset-Tag Output Wiring (Feature 302 / F-260b)

**Created**: 2026-05-30
**PRD**: [docs/product/02_PRD/302-asset-tag-output-wiring-2026-05-30.md](../../docs/product/02_PRD/302-asset-tag-output-wiring-2026-05-30.md)
**Purpose**: Ground the spec in current code reality. The PRD is exceptionally detailed; this research **verifies its factual claims** and surfaces refinements + traps for `/aod.plan`.

---

## Knowledge Base Findings

- **F-189 `source_attribution` is a CONTRAST, not a template.** It omits-when-empty (the `## 9.` block renders only when ≥1 finding carries it). F-260b's FR-5 requires the **opposite** (`affected_assets: []` always present). The PRD architect review already re-anchored FR-1 to the correct precedent — confirmed correct.
- **Correct precedent = `agentic_pattern` / `maestro_layer`**: always-present-with-sentinel-default, value assigned by a **deterministic rule engine (not LLM judgment)**, with a standard inline comment block. Copy this shape.
- **`sarif_common.py` exists and was created to fix a prior two-emitter desync** (`generate-threats-sarif.py` had a hardcoded `COMPONENT_ZONE` dict that silently desynced; fix was a single shared `parse_component_metadata()` traversal). F-260b's FR-4/NFR-3 follow this exact remedy: a single shared extractor reading the emitted `threats.md`, never per-emitter re-derivation.
- **Co-Authored-By trailer for @north-echo (reuse verbatim)**: `Co-Authored-By: Christopher Lusk <122107484+north-echo@users.noreply.github.com>` (from commit `3dfe6a7`). Existing CHANGELOG style line: `* **260:** asset-sensitivity tag prototype (#262) (3dfe6a7)`.
- **Attribution wording is a hard rule**: "prototype authored/contributed by @north-echo (PR #262)" — **NEVER** "surfaced by" (that under-credits a PR author; it's the discussion-commenter form used for @armorer-labs). @north-echo **declined follow-on** → credit is recognition, not assignment (`project_f260_asset_tags.md`, `feedback_external_contributor_collisions.md`).
- **F-212 release-cadence incident**: a non-`feat:` squash title silently skipped release-please. F-260b must ship `feat(302):` (title + CHANGELOG) and verify a release-please PR opens ~30s post-merge (`feedback_aod_deliver_release_gate.md`).
- **CI lock-step lesson (Entry 3, F-256)**: adding a test file to `tachi-pytest.yml` requires editing **both** the `paths:` filter **and** the `pytest` invocation in the same commit, or it silently never runs.

## Codebase Analysis (PRD claims verified)

| # | Claim | Verified state | Refinement |
|---|---|---|---|
| 1 | `finding.yaml` is v1.8 | ✓ `schema_version: 1.8` (line 13) | 1.8 → 1.9 is the next minor |
| 2 | `agentic_pattern`/`maestro_layer` = always-present-default | ✓ defaults `none` (L151-180) / `Unclassified` (L126-147) | Comment convention: `# Agentic Pattern Classification (v1.4 — Feature 142)` + "Additive field with default X (minor bump per ADR-026…)" |
| 3 | `source_attribution` = omit-when-empty contrast | ✓ (L214-282) | Do **not** model on this |
| 4 | `parse_component_asset_map()` at `tachi_parsers.py:1472` | Actually at **line 1494** | Returns `{component: [sorted, deduped, lowercase tags]}` — sort/dedup is **free** |
| 5 | `VALID_ASSET_TAGS` frozen 6-enum | ✓ `tachi_parsers.py:70-77` (`pii\|phi\|auth\|secrets\|financial\|safety`) | |
| 6 | Two SARIF emitters | ✓ `generate-threats-sarif.py` (props ~L444), `generate-risk-scores-sarif.py` (props ~L292) | **Both import `sarif_common.py`** — add `parse_affected_assets()` there |
| 7 | Key-casing drift between emitters | ✓ REAL — threats-sarif camelCase/mixed, risk-scores-sarif kebab/mixed | Pin literal `affected_assets` (snake) in **both**; do not adopt surrounding casing |
| 8 | Risk-scorer is LLM (`model: sonnet`), §3.5 fuzzy match | ✓ `risk-scorer.md:9`, §3.5 at **line 288** (exact) | Reinforces FR-2: keep population OUT of the LLM scorer |
| 9 | Test suite exists, not in CI | ✓ `tests/scripts/test_asset_sensitivity_tags.py` (26 cases); absent from `tachi-pytest.yml` paths + invocation | **26** is authoritative (team-lead `pytest --collect-only`: 22 plain defs + 1 parametrize→4 = 26) |
| 10 | `asset-modifiers.md` documents 9.2 ceiling + ordering | ✓ ceiling 9.2 (L11,19,51-53), modifier-after-clamp (L15-22) | Default doc-extension target (Q7) |

**Critical refinement — `threats.md` is LLM-authored, not Python-serialized.** `threats.md` is produced by the **orchestrator agent (Phase 4)**, which renders findings into the template tables. The deterministic Python layer is the SARIF emitters, which **parse** the (agent-authored) `threats.md`. The `agentic_pattern`/`maestro_layer` precedent shows the working pattern: a **deterministic rule/lookup produces the value, the agent copies it verbatim** (no judgment), the Python emitter parses it. So FR-2's "deterministic serializer tier" is satisfied by *deterministic-value + mechanical-copy*, not necessarily a standalone serializer script. **This is exactly Q1 (architect-owned, plan-time)** — the spec must state the *invariant* (deterministic, single-source, present-per-finding, byte-consistent) without over-committing the mechanism.

## Architecture Constraints

- **ADR-026 minor-bump rule** (`docs/architecture/02_ADRs/ADR-026-*.md`): minor bump when ALL THREE hold — (a) additive, (b) has a default, (c) schema shape/required-fields unchanged. `affected_assets[]` satisfies all three → **1.8 → 1.9 minor**.
- **ADR-028 (F-189)** added an optional field under ADR-026 **without a per-field ADR** → precedent for "no new ADR" (Q2).
- **ADR-037 (F-241)** is the canonical **populator-wiring + additive-field + byte-identity-baseline** precedent; deterministic populators are pure functions (no LLM judgment).
- **ADR-021** byte-determinism: regenerate baselines under `SOURCE_DATE_EPOCH=1700000000`; the only diff must be the additive field.
- **Schema genealogy**: maestro 1.1→1.2 (ADR-020), agentic 1.3→1.4 (ADR-026), source_attr 1.4→1.5 (ADR-028), F-1/F-2/F-4 → 1.8. F-260b → 1.9 fits cleanly.
- **Highest ADR ≈ 045** → a new ADR would be 046; Q2's "no new ADR" is consistent with the lineage.

## Industry Research

- **SARIF 2.1.0**: `result.properties` is the OASIS-sanctioned place for vendor data; no casing rule (snake_case fine, matches the schema); GitHub Code Scanning **ignores unknown properties gracefully**. Avoid the reserved `tags` key.
- **SemVer**: optional field + default = **MINOR** bump, backward compatible — confirms 1.8→1.9.
- **Empty `[]` vs omit**: always-present `[]` is preferred for **deterministic diffs / byte-stable output** — confirms FR-5.

## Recommendations for Spec

1. Capture the **cross-format byte-equivalence invariant (NFR-3)** as the single most important correctness criterion; state it structurally (one deterministic source → `threats.md` → copied into both SARIF property bags via one shared `sarif_common` extractor).
2. Frame the populator as **deterministic, verbatim from `parse_component_asset_map`** (`affected_assets = map.get(component, [])`), explicitly NOT LLM-authored — but leave the *serialization surface/mechanism* (Q1) to plan.md.
3. Keep `affected_assets` **always-present `[]`**, modeled on `agentic_pattern`/`maestro_layer` — never the `source_attribution` omit-when-empty shape.
4. **Frozen-constraint discipline** is a first-class success criterion (SC-11 binary diff on `risk-scoring.yaml` + `tachi_parsers.py`); pin the snake_case key in both emitters.
5. Note the **stale "9.5" trap** in `asset-modifiers.md` (T-2 example) — correct it while extending that doc (Q7), but never touch byte-frozen `risk-scoring.yaml`.
6. CI: edit **both** `paths:` and pytest invocation in `tachi-pytest.yml` (lock-step), adding the 26-case suite + new F-260b tests.
7. Community credit + release-cadence are in-scope acceptance items (US-3, US-5) — not scope creep; carry @north-echo authorship framing exactly.
