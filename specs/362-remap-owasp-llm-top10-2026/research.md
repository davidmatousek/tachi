# Research Summary: F-362 — Remap OWASP LLM Top 10 Coverage to the 2026 Edition

**Date**: 2026-08-06 · **Phase**: `/aod.spec` Step 2 (pre-spec research)
**Repo state measured**: `747805c` (branch `362-remap-owasp-llm-top10-2026`)
**Full reports**: `.aod/results/research-kb.md` · `.aod/results/research-architecture.md` · `.aod/results/research-web.md` · codebase inventory consolidated below (§Codebase Analysis)

---

## Knowledge Base Findings

15 of 22 KB entries relevant (full detail: `.aod/results/research-kb.md`). Load-bearing lessons:

- **Entry 15/19 (F-185/F-329)**: `owasp` IS an `ORDERED_FRAMEWORKS` member, but the CA render consumes only `{id, classification}` — a rename holding ids `LLM01..LLM10` is **byte-neutral**. The #329 drift guard fingerprints `[id, out_of_scope]` only → **stays green through the entire remap; its green is uninformative** (false assurance). The byte-identity suite (`tests/scripts/test_backward_compatibility.py`) is wired into **no CI workflow** — its green must be produced in-loop, pre-merge. Record literal pre-state pytest totals before any edit so red→green flips are attributable.
- **Entry 13/14 (F-186/F-182)**: capture volatile reference sources to a **checked-in artifact before any edit** (Foundational task); reuse the existing integrity suite as the acceptance oracle for pure-data changes; commit honest measured counts, never pad to headlines. F-186 is also the feature that left the byte-identity suite **silently red on main** — the exact failure shape the F-362b split re-creates and must not repeat.
- **Entry 17 (F-183)**: run the live link-rot monitor dispatch **at deliver, never deferred** — the 41 dead URLs in open tracker #332 came from catalog expansions whose citation URLs were never live-validated. F-362 re-anchors 54 citation URLs + 10 record URLs; the monitor auto-discovers its URL set from the taxonomy YAMLs, so no config change is needed, but a live `workflow_dispatch` (with `no_cache: true`) at deliver is the validation gate.
- **Entries 1/3/9 + memory (F-248/F-250/F-256/F-302)**: the gated test harness clones **committed HEAD** — fixture regeneration (`tests/fixtures/init-baseline-tree/`) must land in the **same commit** as its source change; CI `paths:` filter and pytest invocation move in lockstep; ~19 pre-existing out-of-gate failures are expected noise to record in the pre-state.
- **Entry 22 (F-295)**: gate verification on **compiled artifacts consumers read** (threats.md/SARIF/CA pages); empty extraction = gate ERROR, never pass.
- **Entry 8 (F-296)**: `OWASP_COVERAGE.md` is hand-authored canon with **no generator** — born that way at F-296. F-362 is NOT docs-only (emitter code changes) → `feat(362):` PR title + release-please verification apply.
- **Edition-transition precedent**: there has never been a formal remap — `owasp.yaml` was born ON the 2025 edition (F-180). The only 2023→2025 transition artifact is the **live drift exhibit**: `scripts/generate-risk-scores-sarif.py` ships 2023-edition names under `version: "2025"`, undetected across an entire edition change. F-362 is the first edition remap in project history; duplicate hardcoded taxa declarations silently rot — only catalog-derived declarations make recurrence structurally impossible.

## Codebase Analysis (verified inventory)

Full sweep at `747805c`, tracked files, PCRE2. Measurement conventions: **bare** = `\bLLM(0[1-9]|10)\b(?!:)`; **plain-2025** = `LLM0N:2025` without `OWASP ` prefix; **owasp-2025** = `OWASP LLM0N:2025`; **any** = all forms.

**Confirmed exactly as PRD states**: catalog 60 records / 10 LLM (`schemas/taxonomy/owasp.yaml:439–517`) with `full_id: OWASP-LLM-2025-NN`, per-record `# citation:` comments, sort invariant holds by construction; crosswalk **74 LLM-keyed edges / 57 re-keys / 54 2025-slug citation URLs** (per-code: LLM01=8, LLM02=9, LLM03=8, LLM04=6, LLM05=8, LLM06=7, LLM07=6, LLM08=7, LLM09=4, LLM10=11); **9 personas** under `.claude/agents/tachi/` (nuance: 8 threat agents + `risk-scorer`); **15 skill reference files** (13 `references/` + 2 skill READMEs); **adapters 17 files / 4 formats** (a 5th dir `adapters/github-actions/` carries 0 LLM refs); all emitter/parser findings (below); `templates/tachi/output-schemas/threats.md:365` golden row; `schemas/finding.yaml` both example blocks; `examples/**` carve-out 47 suffixed files (48 any-form / 305 refs); protected set **114 files** exactly; all baseline machinery.

**Emitters/parsers (verified line-precise)**:
- `scripts/generate-risk-scores-sarif.py` — stale taxonomy block exists **twice**: `TAXONOMIES` at `:453` (`"version": "2025"` at `:456`, 2023-era names `LLM03 "Training Data Poisoning"` `:461`, `LLM10 "Model Theft"` `:464`, retired `informationUri` `:458`) **and** `supported_taxonomies()` at `:495–520` (`informationUri` again `:502`). `_OWASP_REFERENCE_BY_PREFIX` at `:234` (`OI → OWASP LLM05:2025`, `MI → OWASP LLM09:2025`; under 2026: OI→LLM10:2026, MI→LLM07:2026). Zero test coverage on any of it.
- `scripts/generate-threats-sarif.py` — `normalize_owasp_id` at `:387`, regex `^OWASP\s+LLM(\d+):\d+$` → `LLM-NN` at `:395`, **silent raw passthrough** `return s` at `:402`; zero test coverage (0 hits in `tests/`). Additional 2025/2023-era debt in rule prose at `:66`, `:259–260`, `:271`.
- `scripts/extract-report-data.py` — `classify_framework_items` at `:1174`, **exact-equality** match at `:1193`; no unmatched-ref warning → token-form drift silently yields an all-gap CA page. File contains no LLM literals (purely form-sensitive).

**Form bug (`id: LLM0N:2025` where the catalog contract requires bare ids)** — complete site list: `.claude/agents/tachi/prompt-injection.md:65,93,120` · `data-poisoning.md:77,105` · `model-theft.md:75,127` · `denial-of-service.md:134` (4 personas, 8 sites) + 2 fixtures `tests/scripts/fixtures/web_api_coverage_attestation/stream_1_f_a3_wiring/{prompt_injection,denial_of_service}_wired.md:36`.

**Coverage surfaces**: `docs/standards/OWASP_COVERAGE.md` (NOT repo root) — headline `:1/:8`, LLM row `:20`, per-bucket `:27`, anti-claims `:55`. **README has 5 restatement sites, not 2**: `:7` (poster alt-text), `:19`, `:24`, `:48`, `:390`. `.claude/rules/scope.md:21,24`. Plus doc-site copy: `docs/guides/DEVELOPER_GUIDE_TACHI.md:1805`, `docs/architecture/01_system_design/README.md:130`, `docs/architecture/README.md:61`, and LLM codes in `docs/INTERFACE-CONTRACT.md`, `docs/architecture/00_Tech_Stack/README.md`, `docs/architecture/03_patterns/README.md`, `docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md`, `docs/guides/prompts/developer-guide-prompt.md`, `schemas/taxonomy/README.md`, `schemas/taxonomy/cwe.yaml:17`. No `site/` directory exists.

**Sweep census (tracked files)**:

| Bucket | any refs / files | suffixed / files | bare / files |
|---|---|---|---|
| IN-SCOPE (F-362) | **867 / 91** | 498 / 77 | 366 / 40 |
| CARVE-OUT `examples/**` (excl. test-output) | 305 / 48 | 202 / 47 | 103 / 13 |
| PROTECTED (FR-8) | 2,118 / 190 | **952 / 114** | 1,149 / 151 |

In-scope plain-2025 = 98 refs / 26 files (PRD "~92" ≈ confirmed). Protected set per-bucket (suffixed): `specs/**` 690/92 · PRDs 160/9 · ADRs 85/9 · CHANGELOG 6/1 · init-baseline-tree 6/1 · `examples/*/test-output/**` 5/2 · CONSUMER_GUIDE 0 · INSTITUTIONAL_KNOWLEDGE 0.
**Tooling caution**: `examples/*/test-output/` is `.gitignore`d (`:210`) yet 36 files remain tracked — default `rg` silently skips them; the sweep must use `git grep` or `rg --no-ignore`.

**FR-13 ledger denominator (measured)** — aggregate 45 files / 346 refs on the four surfaces:

| Surface | Files | bare | plain-2025 | owasp-2025 | Total |
|---|---|---|---|---|---|
| `.claude/agents/tachi/**` | 9 | **20** | 17 | 47 | 84 |
| `.claude/skills/**` (15 refs) | 15 | **21** | 7 | 85 | 113 |
| `adapters/**` | 17 | **0** | 0 | 118 | 118 |
| `agents/**` (legacy) | 4 | **0** | 0 | 31 | 31 |

Bare-code exposure concentrates in **8 files / 41 occurrences** (personas: misinformation 7, output-integrity 5, data-poisoning 3, model-theft 3, prompt-injection 2; skill refs: output-integrity 11, misinformation 7, tool-abuse 3). Adapters + legacy agents carry **zero bare codes** — 100% `OWASP LLM0N:2025`, fully visible to a `:2025`-keyed sweep.

**DISCREPANCIES vs PRD** (spec adopts the measured values):

| # | Claim | PRD | Measured | Severity |
|---|---|---|---|---|
| 1 | Legacy `agents/**` with LLM codes | ~9 files | **4 files** (`agents/ai/{data-poisoning,model-theft,prompt-injection}.md`, `agents/orchestrator.md`) | Medium (over-scoped) |
| 2 | FR-12 adapters+legacy total | ~26 files / ~180 refs | **21 files / 149 refs** | Medium (over-scoped) |
| 3 | Bare-code census | ~460 | **366 in-scope** (+103 carve-out = 469) | Medium (conflates carve-out) |
| 4 | FR-14 test files | 7 | **8** (`test_backward_compatibility.py:19` docstring omitted — the FR-7 proof file itself) | Low |
| 5 | FR-14 fixtures | ~20 | **19** (13 suffixed / 6 bare-only) | Low |
| 6 | Success-metric baseline | ~715 refs / 126 files | **867 / 91** in-scope any-form | Low (not reproducible) |
| 7 | FR-8 protected set | 955 / 114 | **952 / 114** suffixed (any-form 2,118 / 190 — boundary matters 2.2× more for bare sweeps) | Low |
| 8 | README restatements | L24/L48 | **5 sites**: L7, L19, L24, L48, L390 | Medium (sweep would miss 3) |
| 9 | `OWASP_COVERAGE.md` path | implied root | `docs/standards/OWASP_COVERAGE.md` | Cosmetic |
| 10 | `coverage-attestation.typ` path | implied `report/` | `templates/tachi/security-report/coverage-attestation.typ:48` | Cosmetic |

**Additions beyond PRD**: (a) the FR-11a derive-from-catalog fix must cover **three** sites (`TAXONOMIES` `:453` + `supported_taxonomies()` `:495` + threats-sarif rule prose `:259–271`); (b) catalog record `url` fields embed 2025 slugs and `LLM01` uniquely uses the unversioned slug `llm01-prompt-injection`; (c) 4 sibling `test_coverage_attestation_*.py` files carry 0 LLM refs (only the base file is in scope).

## Architecture Constraints

Full detail: `.aod/results/research-architecture.md`. Key constraints:

- **ADR-048** is the next free number for the FR-6 alias/cutover ADR (ADR-004 historical gap, ADR-043 reserved for BLP-03 — never reclaim). Format: ADR-047 style; `Proposed` → `Accepted` dual-commit protocol (ADR-027 Decision 8); accepted **Day 1 of plan, before remap mechanics**. Related ADRs: 013, 021, 027 (+037 Extension-History discipline), 028, 030/031/034/045.
- **Catalog record shape is frozen** (ADR-027 D1 + extensions): `id` stays bare `LLM01..LLM10`; `full_id` is the ONE edition-carrying field; `name` must be the **verbatim** 2026 canonical name (no alias field exists in the record shape — aliasing belongs at the token-grammar layer); `url` regex-checked only (no HTTP at test time); `cwe_refs` populated ONLY where OWASP explicitly publishes CWE cross-refs; any new field requires an ADR-048 D-decision + ADR-027 Extension History + integrity-test update. **Recommendation: grammar-layer aliasing, zero schema churn.**
- **`references[]` grammar today** (`schemas/finding.yaml:103–112`, schema 1.9): free-form `list[string]`, de-facto token `OWASP LLM<NN>:<year>`, example `"OWASP LLM01:2025"`. **`source_attribution.id` MUST stay bare** (resolves against catalog `id:`) — enum of 5 taxonomies, `relationship ∈ primary|related|derived`.
- **Crosswalk invariants**: exactly 5 keys per edge (**extra keys rejected** — disposition ledger must live outside `crosswalk.yaml`); dedupe key `(source.taxonomy, source.id, target.taxonomy, target.id, edge_type)` unique; primary floor ≥ 500 (645 edges today, 66 primary LLM edges re-keyed not removed — floor unaffected); citations regex-or-repo-file, no fetch. **Re-key must be a single simultaneous 8-id permutation pass** — sequential renames collide on the dedupe key mid-flight.
- **SARIF scope fence**: threats-SARIF `run.taxonomies[]` is OWASP-**2021**/CWE (append-only, index-stable) and is **untouched** by the LLM remap; the LLM edition lives in `help.markdown` prose (skill templates + generator mirrors) and in the risk-scores TAXONOMIES block (the FR-11a drift exhibit). 2026 informationUri anchor: `https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/`.
- **Detection ADR lineage re-keys**: ADR-030/045 (LLM05:2025) → attests **LLM10:2026**; ADR-031 (LLM09:2025) → **LLM07:2026**; ADR-034 (LLM10:2025) → **LLM06:2026**. The four ADRs are immutable (FR-8 excluded); `OWASP_COVERAGE.md` needs the editorial note.
- **Link-rot monitor auto-discovers** its URL set from `schemas/taxonomy/*.yaml` — re-anchoring changes the monitored set automatically; no checker/workflow edit; scheduled-only (never PR CI); live `workflow_dispatch` with `no_cache: true` at deliver.

## Industry Research

Full detail: `.aod/results/research-web.md`. Verified live 2026-08-06:

- **2026 release page live** (published 2026-08-04); **per-entry 2026 URLs not yet web-indexed** — expected pattern `/llmrisk/llm{NN}2026-{slug}/` is **unconfirmed**. All 10 **2025** entry URLs currently resolve 200 (redirect fate unknown). ⇒ The spec must gate citation re-anchoring on **live verification of the actual 2026 URL scheme** (PDF + site) before authoring, with a defined fallback if per-entry pages don't exist at build time.
- **No official OWASP migration guidance for tool vendors** (no version-suffix standard, no machine-readable list). Inferred: `:YYYY` code suffix, year-slugged URLs.
- **Appendix A / LLM-to-ASI authority**: AIUC-1 crosswalk resource verified (May 2026); 2026 PDF Appendix A itself is behind the download — verify at ADR/build time.
- **Version-transition precedents**: MITRE ATLAS (dual content/format versioning, legacy preserved), Snyk (dual-support both editions simultaneously, no hard cutoff), Semgrep (deprecation markers + migration guidance). All three inputs to the ADR-048 hard-cutover-vs-dual-emission decision.

## Recommendations for Spec

1. **Adopt measured counts** everywhere (discrepancy table above): 21 files/149 refs for adapters+legacy; 8 test files; 19 fixtures; 5 README sites; bare-ledger denominator 366 in-scope (41 hand-review occurrences across 8 files); protected 952/114 suffixed.
2. **ADR-048 first as a hard gate** with the three mandatory contents (grammar; `normalize_owasp_id` + covering test lockstep; real enforcement points = personas + 15 skill refs + `finding.yaml` + sarif-spec templates). Prefer grammar-layer aliasing; keep catalog/crosswalk shapes frozen.
3. **Encode the no-churn proof as a testable gate**: byte-identity suite green pre-merge (it is in no CI); pre-state task records literal totals; #329 guard green declared uninformative; regen + sidecar re-emit causally bound to whichever loop re-keys example `source_attribution` (F-362b).
4. **Checked-in disposition ledgers as Foundational artifacts** in `specs/362-*/` (74-edge crosswalk ledger; bare-code ledger over the measured 45-file surface), authored before edits begin.
5. **Single-pass bijection** for the crosswalk permutation; integrity suite as acceptance oracle; honest counts (74/57/54, no padding).
6. **FR-11a covers three sites**; FR-11b stderr warning (byte-neutral); FR-11c form-bug fix at all 8 persona sites + 2 fixtures.
7. **Sweep tooling must see gitignored-but-tracked files** (`git grep` / `rg --no-ignore`); README sweep covers all 5 restatement sites.
8. **Live link-rot dispatch at deliver** (`no_cache: true`); verify 2026 slug shape exists before authoring URLs; pre-decide disposition for new rot (file, don't absorb).
9. **Same-commit fixture discipline** for `init-baseline-tree`; CI paths/pytest lockstep for any test file changes.
10. **FR-9a optional consistency test**: recommend **build** (one pytest: OWASP_COVERAGE.md LLM row ↔ catalog `full_id` edition) — cheap, aligned with the structural-impossibility goal; needs the explicit plan-stage scope decision.

---

## Plan-Stage Decisions (Phase 0 — added at /aod.project-plan, 2026-08-06)

Every registered decision point from the spec's Plan-Stage Decision Register plus the PM spec-review warnings, in Decision/Rationale/Alternatives form. D1–D3 are recorded normatively in **ADR-048** (`docs/architecture/02_ADRs/ADR-048-llm-top10-2026-alias-cutover.md`, Proposed → Accepted at architect plan sign-off); D4–D9 are plan rulings.

- **D1 — Alias policy: hard cutover + one-release prose breadcrumbs.** Rationale: year-suffixed grammar makes legacy tokens permanently self-describing (removes dual-emission's core motivation); `source_attribution` cannot dual-emit without double-counting CA classification (exact-equality matcher); dual-emission is the priced 10.0d ceiling for partial-by-construction protection; early-stage consumer base migrates on a changelog σ-table. Alternatives: dual-emission (rejected: partial + costly), catalog alias field (rejected: shape-frozen schemas, no identified consumer), pure cutover (rejected alone: breadcrumbs are free). Breadcrumb placement is normative: prose only — never in `references[]`, the References column, or `source_attribution` (the `$`-anchored parser would silently passthrough).
- **D2 — Grammar/parser lockstep.** `normalize_owasp_id` regex is year-agnostic (parses 2026 today); net-new covering test pins both editions, breadcrumb-suffix passthrough, ASI/MCP/CWE branches, unknown passthrough. Same-commit rule for any future grammar move.
- **D3 — Enforcement points.** Personas (9) + skill refs (15) + `finding.yaml` example blocks + sarif-specification templates + `threats.md:365` golden row; scripts lockstep but regeneration-only.
- **D4 — `relationship` values under 2026 (architect ruling, FR-004/spec register #3).** Carry forward unchanged at re-key (σ is category-preserving — the finding↔category semantic association is untouched by renumbering); absorption-driven upgrades (e.g. a finding matching a newly absorbed sub-class) are evaluated per-example during **F-362b** disposition, never blanket-flipped in F-362. Consequence: F-362 proper touches no example findings → no-churn proof stands.
- **D5 — FR-009 consistency test: BUILD.** One pytest function asserting the OWASP_COVERAGE.md LLM-row edition token matches the catalog `full_id` edition prefix. **Placement (architect HIGH-1 correction, plan-review 2026-08-06)**: `tests/scripts/test_catalog_drift_guard.py` — CI-gated by `tachi-catalog-drift.yml` whose `&drift_paths` anchor already covers `schemas/taxonomy/*.yaml` (genuinely zero paths churn; semantically correct home). The originally proposed `test_coverage_attestation.py` is in NO workflow — placement there would have re-created the F-186 in-loop-only assurance shape. Alternatives: skip (rejected — 20 lines buys structural doc↔catalog coupling, same class as FR-012a); new test file (rejected — paths-filter churn); optional follow-through: add `docs/standards/OWASP_COVERAGE.md` to `&drift_paths`.
- **D6 — `cwe_refs` fence (PM W2).** Populate only from explicitly-published 2026 CWE cross-refs whose ids already resolve in `cwe.yaml` (93 records); anything requiring `cwe.yaml` growth → follow-up issue. Protects budget and the FR-007a no-churn proof (`cwe` ∈ ORDERED_FRAMEWORKS — KB 15). Default `[]`.
- **D7 — SC-002 semantics / ADR-index prose (PM W1).** SC-002 operationalized as zero **undispositioned** suffixed refs outside exclusions. `docs/architecture/README.md:57–69` ADR-index lines (quoting immutable ADR titles) get bare-code-ledger disposition class `retained-historical` — annotated, never rewritten; the file's non-index content (e.g. `:61` F-5 prose) is dispositioned per-line. No blanket file exclusion.
- **D8 — Bare-code ledger evidence bar (PM W3).** Two tiers: occurrence-level for the 41 concentrated refs (8 files) + any mixed file (historical + active); file-level (count + form-class + disposition class) for the rest of the 366 census; 103 carve-out refs transfer to the F-362b ledger at issue-filing. Contracts: `contracts/disposition-ledgers.md`.
- **D9 — 2026 URL verification gate (spec edge case).** W0 build-gate task live-verifies the 2026 per-entry URL scheme (≥3 sample fetches) before any URL authoring; absent per-entry pages → interim anchor = official release resource page, per-edge ledger record; deliver-stage live link-rot dispatch (`no_cache: true`) is the final validator.
