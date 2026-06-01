# Research Summary: MAESTRO Coverage Matrix — Always Render All 7 Layers (Feature 098)

**PRD**: `docs/product/02_PRD/098-maestro-7-layer-output-polish-2026-06-01.md`
**Date**: 2026-06-01
**Method**: Parallel research — Explore agent (codebase enumeration + line verification), general-purpose agent (KB + institutional knowledge + light web), direct Reads (canonical layer reference).

---

## Knowledge Base Findings

- **No prior "silently-dropped-layer" incident exists.** Greps of `docs/INSTITUTIONAL_KNOWLEDGE.md` for "silently dropped/omitted layer", "always render", "zero-finding row" returned nothing. F-098 is the first time the omission is treated as a defect — Feature 084 *intentionally* specified it. FR-1 therefore **reverses an 084 acceptance criterion**, not an accidental regression.
- **F-260b deterministic populator precedent (INSTITUTIONAL_KNOWLEDGE Entry 9)**: `scripts/populate-affected-assets.py` (469 lines, stdlib-only, `--check` dry-run, idempotent regex upsert) is the project's proven idiom for byte-stable, deterministic markdown blocks. **Caveat**: it writes a *machine-extractable* block consumed downstream; the MAESTRO table is *LLM-authored prose* (the orchestrator directive is the production authority). A populator for F-098 would be a **regeneration helper for committed examples**, not a production-path component. Keep that distinction crisp.
- **F-302 fixture-drift transitive risk (INSTITUTIONAL_KNOWLEDGE Entries 1 & 9)**: the `init-baseline-tree` test (`test_personalized_tree_bytes_match_baseline`) can fail on accumulated placeholder-doc drift whenever a PR touches a `tachi-pytest.yml` `paths:`-filtered file. The Team-Lead correctly notes the PDF `.baseline` fixture is a *different* surface — but the init-tree test could still re-trigger transitively. Standing remedy: `tests/fixtures/regenerate-baseline.sh`. Worth a one-line note in tasks.md.

## Codebase Analysis

### Verified root-cause locations (all PRD line claims confirmed against source)
- **`.claude/agents/tachi/orchestrator.md:714-722`** — directive reads: *"include a Risk by MAESTRO Layer subsection… **Omit layers with zero findings.** Order rows by highest severity descending, then finding count descending."* Current ordering = **severity-descending** (not canonical). This is the true root cause (D3).
- **`.claude/skills/tachi-orchestration/references/output-schemas.md:229-240`** — "Omission" bullet (L238): *"Layers with zero findings are omitted from the table."*; "Ordering" bullet (L237): severity-descending; Unclassified carve-out (L240): *"do not omit it."*
- **`scripts/extract-report-data.py`** — `parse_maestro_data` builds `parsed_layers` from the *parsed markdown table* (lines 261-291); `layer_groups` seeded from `parsed_layers` (363-370); `_MAESTRO_LAYERS = MAESTRO_LAYERS = ["L1".."L7"]` (tachi_parsers.py:44) is **sort-only** (399-400), NOT a seeding source; **filter at line 407**: `findings_by_layer = [layer_groups[lid] for lid in sorted_layer_ids if layer_groups[lid]["findings"]]` drops zero-finding layers. **PDF is strictly downstream of markdown (D3 confirmed).**
- **`templates/tachi/security-report/maestro-findings.typ:149-155`** — per-layer heading renders `(N findings)` (handles `0` correctly); empty-layer fallback (L154) *"No findings mapped to this layer."* is present but **unreachable dead code** (never receives empty layers because of the line-407 filter).

### Canonical layer source (single source of truth — reuse, do not duplicate)
`.claude/skills/tachi-shared/references/maestro-layers-shared.md` (L52-60) and `scripts/tachi_parsers.py:44`:
L1 Foundation Model · L2 Data Operations · L3 Agent Framework · L4 Deployment Infrastructure · L5 Evaluation and Observability · L6 Security and Compliance · L7 Agent Ecosystem.
> Note: L1-L7 *classification* evaluation order is load-bearing (L5-before-L6). F-098 changes *render* order, NOT *classification* order — distinct orderings; do not conflate.

### COMPLETE enumeration — 14 `threats.md` files carry a MAESTRO table (broader than PRD FR-4's named 7)
| File | Rows now | Layers present | Missing | Unclassified | Category |
|---|---|---|---|---|---|
| `examples/agentic-app/threats.md` | 6/7 | L1,L2,L3,L5,L6,L7 | **L4** | yes | shipped example (PR diff target) |
| `examples/agentic-app/sample-report/threats.md` | 6/7 | L1,L2,L3,L5,L6,L7 | L4 | yes | shipped sample-report |
| `examples/web-app/threats.md` | 4/7 | L2,L4,L6,L7 | L1,L3,L5 | no | shipped example **(baseline-gated)** |
| `examples/microservices/threats.md` | 2/7 | L2,L4 | L1,L3,L5,L6,L7 | yes | shipped example **(baseline-gated)** |
| `examples/ascii-web-api/threats.md` | 4/7 | L2,L4,L6,L7 | L1,L3,L5 | no | shipped example **(baseline-gated)** |
| `examples/mermaid-agentic-app/threats.md` | 4/7 | L1,L2,L3,L7 | L4,L5,L6 | no | shipped example **(baseline-gated)** |
| `examples/free-text-microservice/threats.md` | 2/7 | L2,L4 | L1,L3,L5,L6,L7 | yes | shipped example **(baseline-gated)** |
| `examples/maestro-reference/threats.md` | **7/7** | all | none | no | shipped example **(baseline-gated)** — only D2 re-order may change it |
| `examples/mobile-banking-app/sample-report/threats.md` | 2/7 | L2,L7 | L1,L3,L4,L5,L6 | yes | **shipped sample-report — NOT in PRD FR-4 list (Architect residual)** |
| `examples/agentic-app/test-output/2026-04-19T02-53-49/threats.md` | 6/7 | L1,L2,L3,L5,L6,L7 | L4 | yes | **frozen test snapshot (scope Q)** |
| `examples/agentic-app/test-output/2026-04-19T03-20-30/threats.md` | 6/7 | … | L4 | yes | frozen test snapshot |
| `examples/agentic-app/test-output/2026-04-23T19-30-00-F2-wave4/threats.md` | 6/7 | … | L4 | yes | frozen test snapshot |
| `examples/agentic-app/test-output/2026-04-26T03-39-12-F3-wave3/threats.md` | 6/7 | … | L4 | yes | frozen test snapshot |
| `examples/agentic-app/test-output/2026-04-27T17-11-26-F5-wave2/threats.md` | 6/7 | … | L4 | yes | frozen test snapshot |

**Two scope items the PRD's FR-4 named list did not capture (resolve at plan/tasks):**
1. **`examples/mobile-banking-app/sample-report/threats.md`** — a shipped sample-report at 2/7. Must be in scope to satisfy the Architect's "no sample-report left < 7 rows" residual.
2. **`test-output/` snapshots** — timestamped historical test artifacts. Recommended **out of scope** (frozen point-in-time captures, not user-facing shipped examples); a regression test that scans `examples/**/threats.md` must exclude `test-output/` by **path pattern** (not enumeration) or they will fail the invariant.

> **PM-verified enumeration correction (supersedes the table above where they differ)**: the authoritative in-scope set is the **9 files that carry a "Risk by MAESTRO Layer" table** — `agentic-app` (6/7), `agentic-app/sample-report` (6/7), `web-app` (4/7), `ascii-web-api` (4/7), `mermaid-agentic-app` (4/7), `microservices` (2/7), `free-text-microservice` (2/7), `mobile-banking-app/sample-report` (2/7), `maestro-reference` (7/7, re-order only). **Two sample-reports carry NO MAESTRO table and are correctly OUT of scope** — `predictive-ml-app/sample-report`, `consumer-agent-app/sample-report` — they must NOT be force-fit with a table. The in-scope criterion is *carries-a-MAESTRO-table*, not *directory exists*. `test-output/` actually contains **8** snapshots (the "5" above is a stale Explore count), all excluded by the FR-009 path pattern, so the exact count is immaterial and must not be hardcoded.

### Backward-compat baselines
- `tests/scripts/test_backward_compatibility.py` — `BASELINE_EXAMPLES` = **6**: web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice, maestro-reference. Validates `examples/*/security-report.pdf.baseline` byte-for-byte. **`SOURCE_DATE_EPOCH = "1700000000"`** (line 43).
- 13 `.pdf.baseline` files exist total; only the 6 above are the test gate. agentic-app is regenerated for its PR diff but is not in the 6-baseline test.

### Regression-test homes (FR-5)
- `tests/scripts/test_extract_report_data.py` — natural home for "filter no longer drops zero-finding layers → all 7 retained".
- `tests/scripts/test_backward_compatibility.py` — the 6-PDF byte-exact gate.
- Assert against `MAESTRO_LAYERS` from `scripts/tachi_parsers.py:44` (re-exported as `_MAESTRO_LAYERS` at extract-report-data.py:231) — satisfies the "no duplicate hard-coded layer list" NFR by import.

## Architecture Constraints

- **ADR-021 (determinism)**: `SOURCE_DATE_EPOCH=1700000000` (2023-11-14 UTC) must be set before `typst compile` for both baseline regen and the backward-compat test (test-path only; production unchanged). Typst otherwise embeds wall-clock dates + derived InstanceID. Matrix grows 1-5 rows **and** non-empty rows re-sort to canonical order (D2) → expect reorder churn in diffs, not just additions.
- **ADR-020 (MAESTRO classification)**: no new ADR needed (Architect concurred). Classification evaluation order untouched.
- **No SARIF / schema change**: layer counts already structured; markdown + PDF rendering only. F-098 adds no enum values → "no schema change" confirmed correct (per Feature 136 schema-versioning rule).

## Industry Research

- Public coverage-matrix practice (CMMC applicability matrices, MITRE ATT&CK coverage maps) confirms the UX principle: explicitly distinguishing *not-applicable* vs *assessed-clean* vs *gap* is the recognized way to make coverage matrices interpretable.
- **Stronger in-house precedent**: `.claude/skills/tachi-orchestration/references/coverage-matrix-model.md` §5 already defines a **three-state cell model** for the STRIDE matrix — integer (findings) / `---` em-dash ("analyzed, zero findings") / `n/a` ("not applicable"), with the rule *"all three states must be visually distinguishable."* This is exactly the analyzed-clean / not-applicable / dropped distinction. Model A (v1) deliberately collapses clean + n/a into one annotation (deferring the true three-state split to Model B/P1, which needs cross-pipeline `component_layer_map`). **Spec implication**: word the Model A annotation so it does not *contradict* the em-dash/`n/a` semantics already used elsewhere in the same report, and cite `coverage-matrix-model.md` as the precedent the eventual Model B should adopt.

## Recommendations for Spec

1. **Three user stories** map cleanly from the PRD (US-1 full span / US-2 self-documenting rows / US-3 regression-proofing). US-1 and US-2 are P1 (both close Issue #98); US-3 is P2.
2. **Pin the complete file enumeration** (Architect residual) — surface the 14-file reality, mark `mobile-banking-app/sample-report` **in scope**, mark the 5 `test-output/` snapshots **out of scope** (frozen artifacts), and require the regression test to exclude `test-output/`.
3. **Annotation wording (FR-3 Model A)** must be cross-format identical AND not contradict `coverage-matrix-model.md`'s `---`/`n/a` vocabulary; phrase as coverage metadata, never a severity.
4. **Canonical L1-L7 order in both pipelines (D2)** — markdown switches severity-desc → canonical; PDF already canonical. Expect reorder churn in baseline diffs.
5. **No new hard-coded layer list** — import `MAESTRO_LAYERS` from `tachi_parsers.py`.
6. **Defer to plan/tasks** (not spec ambiguities — document as scope notes, not NEEDS CLARIFICATION): (a) FR-6 maestro-stack infographic include-vs-defer (default defer); (b) FR-4 hand-edit vs populator mechanism; (c) the test-output/ exclusion decision.
7. **No NEEDS CLARIFICATION markers** — the PRD's D1/D2/D3 resolved the load-bearing decisions; remaining open items are plan-stage mechanism choices, not requirement ambiguities.
