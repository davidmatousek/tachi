---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-08-06
    status: APPROVED_WITH_CONCERNS
    notes: "15/15 FRs land in work streams; spec warnings W1/W2/W3 resolved faithfully by D7/D6/D8; ADR-048 serves US-2; FR-004 re-derivation intact; no scope creep; ~4.5d holds PRD milestones. CRITICAL (sweep-gate grep forms could not fail) FIXED in-loop 2026-08-06 with empirically verified -P forms + sanity rule; warnings folded in: currency-detector limitation recorded in Risks, DEVELOPER_GUIDE :1815 + CONSUMER_GUIDE_TACHI_RESEARCH.md + README poster disposition added to W4; SC-005 gating carried to tasks. Full: .aod/results/product-manager.md"
  architect_signoff:
    agent: architect
    date: 2026-08-06
    status: APPROVED_WITH_CONCERNS
    notes: "ADR-048 RATIFIED → Accepted (provisional pre-PR). Verified empirically: σ category-preserving bijection (live counts match projections, Σ=74), no-churn proof at render layer, placement rules protect both fragile parsers, round-2 carries NEW-1/NEW-3/MEDIUM-7/8 resolved, D4-D9 sound. 7 conditions: 1 (D5→test_catalog_drift_guard.py), 3 (catalog-drift gate annotated), 4 (target-endpoint check), 6 (W4 citation reconcile), 7 (ADR status line) APPLIED in-loop; 2 (net-new test placement task + tachi-pytest lockstep) and 5 (breadcrumb sunset into F-362b issue body) CARRIED to /aod.tasks. Full: .aod/results/architect.md"
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: Remap OWASP LLM Top 10 Coverage to the 2026 Edition

**Branch**: `362-remap-owasp-llm-top10-2026` | **Date**: 2026-08-06 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/362-remap-owasp-llm-top10-2026/spec.md` (PM: APPROVED_WITH_CONCERNS 2026-08-06)
**PRD**: [362-remap-owasp-llm-top10-2026-2026-08-05.md](../../docs/product/02_PRD/362-remap-owasp-llm-top10-2026-2026-08-05.md) (v1.2)

## Summary

Category-level remap of every LLM Top 10 contract surface from the OWASP 2025 edition to the 2026 edition (rank permutation, Hidden Context Exposure rename, four scope absorptions), governed by the movement map as remap authority. The alias/cutover policy is decided first via **ADR-048** (hard cutover with one-release prose breadcrumbs — Proposed in this plan, ratified at architect sign-off). Per-category coverage is re-derived from detection evidence; two checked-in disposition ledgers (74 crosswalk edges; bare codes) make the semantic pass auditable; the byte-identity suite green pre-merge is the no-churn proof; `examples/**` splits to F-362b under the declared carve-out. All counts are research-measured at `747805c` (spec discrepancy table is normative).

## Technical Context

**Language/Version**: Python 3.11+ (repo scripts: stdlib + PyYAML only — no new dependencies); Bash (verification tooling); Typst (local-only CA-PDF recipe, F-362b)
**Primary Dependencies**: existing catalog loader in `scripts/` (reused for FR-012a derive-from-catalog); `tests/schemas/test_taxonomy_integrity.py` as the data-change acceptance oracle; `tests/scripts/test_backward_compatibility.py` as the byte-identity gate (in **no CI** — run in-loop on committed HEAD)
**Storage**: Markdown + YAML files (the repo IS the data store — `schemas/taxonomy/*.yaml`, persona/skill markdown, adapters, docs)
**Testing**: pytest (gated 15-module subset in `tachi-pytest.yml`; `paths:` filter + invocation move in lockstep, same commit); pre-commit gitleaks
**Target Platform**: tachi repo consumed inside Claude Code (production outputs are LLM-authored; SARIF generator scripts are regeneration-only with no production caller)
**Project Type**: single (data/content surgery + minimal script/test changes; no new components, no API, no UI)
**Performance Goals**: N/A (no runtime surface changes; CA-page extraction stays byte-identical for well-formed inputs)
**Constraints**: catalog/crosswalk schemas shape-frozen (crosswalk edges hard-reject extra keys); `source_attribution.id` must stay bare catalog-resolving ids; threats-SARIF `run.taxonomies[]` (OWASP-2021/CWE) append-only index-stable and out of scope; sweep tooling must see gitignored-but-tracked files (`git grep` / `rg --no-ignore`); FR-008 exclusion set is a hard boundary (952 suffixed refs / 114 files)
**Scale/Scope**: 91 in-scope files / 867 any-form refs (498 suffixed, 366 bare); 10 catalog records; 74 crosswalk edges (57 re-keys, 54 URL re-anchors); 21 mirror files / 149 refs; 8 test files + 19 fixtures; ~4.5 ± 1.0 attention-days (team-lead projection with hard-cutover ADR + split confirmed; floor 3.5 / ceiling 10.0)

## Constitution Check

*GATE: evaluated pre-Phase-0; re-checked post-design — PASS (no violations; Complexity Tracking empty).*

- **III Backward Compatibility (NON-NEGOTIABLE)**: the consumer-facing code cutover is a deliberate, ADR-governed contract change (ADR-048) with a changelog migration table; emitted 2025 tokens remain permanently self-describing (year-suffixed grammar), so historical outputs stay interpretable. PASS.
- **VI Testing Excellence**: data changes ride the existing integrity suite (acceptance oracle — no new suite needed, F-186 precedent); net-new coverage exactly where a contract moves: `normalize_owasp_id` covering test (currently zero), derive-from-catalog taxa test (file placement assigned at /aod.tasks per architect HIGH-2, with `tachi-pytest.yml` lockstep if a new module is created), D5 coverage-consistency test in the CI-gated `test_catalog_drift_guard.py` (architect-corrected placement). PASS.
- **VII DoD / IX Git & branching / X dual sign-off**: feature branch + draft PR #363 open; `feat(362):` title set; this plan carries PM + Architect sign-off before `/aod.tasks`. PASS.
- **Code economy (laziness ladder)**: no generator built for `OWASP_COVERAGE.md` (rung 1 — spec forbids); FR-012a reuses the existing catalog loader (rung 2); ledgers are markdown artifacts, not tooling; no scanner/parser machinery for the breadcrumb convention. PASS.

## Project Structure

### Documentation (this feature)

```
specs/362-remap-owasp-llm-top10-2026/
├── plan.md                      # This file
├── research.md                  # Spec-stage research + Phase 0 plan-stage decisions
├── data-model.md                # Catalog slot table, permutation map, ledger schemas
├── contracts/
│   ├── references-token-grammar.md   # ADR-048 grammar contract (normative excerpt)
│   └── disposition-ledgers.md        # Ledger authoring contracts (columns, evidence bars)
├── quickstart.md                # Verification battery runbook
├── checklists/requirements.md   # Spec quality checklist (done)
├── feasibility-check.md         # Team-lead estimate (define stage)
└── tasks.md                     # /aod.tasks output (next)
```

### Source Code (repository root — the surgery surfaces)

```
schemas/taxonomy/owasp.yaml           # 10 LLM records :439–517 (full_id/name/url/citation comments)
schemas/taxonomy/crosswalk.yaml       # 74 LLM-keyed edges of 645 (57 re-keys, 54 URL re-anchors)
schemas/finding.yaml                  # references[] example :109; source_attribution examples :330–332
.claude/agents/tachi/*.md             # 9 personas (84 refs; 8 with-year id sites to fix)
.claude/skills/**                     # 15 skill reference files (113 refs)
adapters/{claude-code,copilot,cursor,generic}/   # 17 files / 118 refs (github-actions: 0)
agents/{ai/*,orchestrator}.md         # 4 legacy mirror files / 31 refs
scripts/generate-risk-scores-sarif.py # TAXONOMIES :453 + supported_taxonomies() :495 + prefix map :234
scripts/generate-threats-sarif.py     # normalize_owasp_id :387 + rule prose :66,:259–260,:271
scripts/extract-report-data.py        # classify_framework_items :1174 (add unmatched-ref warning)
tests/scripts/                        # 8 test files + 19 fixtures; test_backward_compatibility.py gate
templates/tachi/output-schemas/threats.md:365    # golden row
docs/standards/OWASP_COVERAGE.md      # hand-authored coverage canon
README.md (:7,:19,:24,:48,:390) · .claude/rules/scope.md (:21,:24) · docs/guides + docs/architecture   # restatements
docs/architecture/02_ADRs/ADR-048-*.md           # NEW — alias/cutover decision (this plan)
```

**Structure Decision**: single-project data surgery on existing paths; the only net-new files are ADR-048, the two `specs/362-*/` ledgers, and plan artifacts. No `src/` changes; no new directories outside `specs/` and one ADR.

## Phase 0: Plan-Stage Decisions (all registered decision points resolved)

Full Decision/Rationale/Alternatives records: [research.md §Plan-Stage Decisions](research.md). Summary:

| # | Decision point | Ruling |
|---|----------------|--------|
| D1 | **Alias policy (FR-006)** | **Hard cutover** to 2026 tokens; **one-release prose breadcrumbs** `(2025: LLMNN)` allowed in narrative prose ONLY — never inside `references[]` tokens, the threats.md References column, or `source_attribution` (breaks `normalize_owasp_id` `$`-anchor / double-counts CA classification). Recorded as ADR-048. |
| D2 | **Grammar + lockstep test (FR-006b)** | `references[]` token: `OWASP LLM<NN>:2026`. `normalize_owasp_id` regex is already year-agnostic (`:\d+$`) — behavior pinned by a net-new covering test (2025 token, 2026 token, near-miss forms, silent-passthrough branch). |
| D3 | **Enforcement points (FR-006c)** | Personas (9), skill refs (15), `schemas/finding.yaml` both example blocks, `sarif-specification.md` templates, `threats.md:365` golden row. Scripts move in lockstep but are regeneration-only. |
| D4 | **`relationship` values under 2026 (FR-004, architect ruling)** | Carry forward unchanged at re-key (category-preserving bijection); absorption-driven upgrades evaluated per-example **in F-362b disposition**, never blanket-flipped. F-362 proper touches no example findings. |
| D5 | **FR-009 optional consistency test** | **BUILD** — one pytest function asserting the `OWASP_COVERAGE.md` LLM row edition matches the catalog `full_id` edition prefix; placed in `tests/scripts/test_catalog_drift_guard.py`, which IS CI-gated by `tachi-catalog-drift.yml` (`&drift_paths` already covers `schemas/taxonomy/*.yaml`) — genuinely zero `paths:` churn. **Architect HIGH-1 correction applied**: the originally proposed `test_coverage_attestation.py` is in NO workflow; placing the test there would have left it in-loop-only assurance. Optional one-line follow-through: add `docs/standards/OWASP_COVERAGE.md` to `&drift_paths` to gate the doc-side direction. |
| D6 | **`cwe_refs` fence (PM W2)** | Populate ONLY from CWE cross-refs the 2026 publication explicitly lists AND whose ids already resolve in `cwe.yaml` (93 records). Any cross-ref requiring `cwe.yaml` growth → follow-up issue, never in-loop (protects the FR-007a no-churn proof and the budget; F-185 precedent). Default expectation: `[]`. |
| D7 | **SC-002 semantics / ADR-index prose (PM W1)** | SC-002 = zero **unreviewed/undispositioned** suffixed refs outside the exclusion list. Historical citations of immutable records — ADR-index prose (`docs/architecture/README.md:57–69`) and legacy-form-exercising fixtures — get ledger disposition class `retained-historical` (annotated, not rewritten). `docs/architecture/README.md` is NOT blanket-excluded: its non-index content remaps normally. |
| D8 | **Bare-code evidence bar (PM W3)** | Two-tier ledger: **occurrence-level** for the 41 concentrated bare refs (8 files) and for any file mixing retained-historical with active refs; **file-level** (count + form-class + disposition class) for the remaining in-scope bare files (366 total census). Carve-out files (103 bare) transfer to the F-362b ledger. |
| D9 | **2026 URL verification (spec edge case)** | Build-gate task before any URL authoring: live-verify the actual 2026 per-entry URL scheme (≥3 sample fetches). If per-entry pages are absent → interim anchor = official release resource page, recorded per-edge in the ledger; deliver-stage live link-rot dispatch (`no_cache: true`) is the final validator. |

## ADR-048 (authored with this plan)

`docs/architecture/02_ADRs/ADR-048-llm-top10-2026-alias-cutover.md` — Status **Proposed** at plan authoring; flips to **Accepted (provisional pre-PR)** on architect sign-off of this plan (dual-commit protocol, ADR-027 Decision 8; final commit-SHA filled post-merge). Contains D1–D3 as D-numbered decisions, alternatives (dual-emission; catalog alias field; pure cutover without breadcrumbs), consequences + mitigations, and the exact grammar contract mirrored in [contracts/references-token-grammar.md](contracts/references-token-grammar.md). Related: ADR-013, ADR-021, ADR-027/037, ADR-028, ADR-030/031/034/045 (re-keyed lineage).

## Technical Approach (work streams → wave sketch for /aod.tasks)

Dependency chain (team-lead-corrected, C3 honored): **W0 → W1 → W2 → W3 → W4 → W5** with W2 as the widest parallel lane.

- **W0 — Gate + Foundational artifacts** (serial, Day 1): pre-state capture (literal pytest totals: byte-identity suite + gated subset, incl. ~19 known out-of-gate failures); ADR-048 ratified; both disposition ledgers scaffolded from data-model.md schemas; D9 URL-scheme live verification.
- **W1 — Catalog + crosswalk** (serial pair): 10-record surgery per data-model.md slot table (`full_id` flip, verbatim 2026 names, verified URLs, `# citation:` re-attestation per re-keyed category); crosswalk single-pass simultaneous σ-permutation (bijection on the dedupe key — never sequential), then 74-edge human disposition (target/citation/confidence vs 2026 definitions; anti-drift downgrade rule; 54 URL re-anchors per D9). Oracle: integrity suite green; 645 edges; 0 duplicates; primary floor ≥500 holds; **re-verify 0 owasp-LLM target endpoints before the permutation** (σ is source-only by design — architect MEDIUM-2; an LLM target endpoint added since `747805c` would be invisible to both the suite and the source-keyed ledger).
- **W2 — Authored contract surfaces** (parallel fan-out, 3–4 lanes): 9 personas + 15 skill reference files (2026 codes/names, Hidden Context Exposure alias notes, FR-012c bare-id form fix at all 8 sites); then adapters (17 files, 4-format checklist) + legacy mirrors (4 files) — FR-013 sequencing: after `.claude/`, before sweep.
- **W3 — Emitters/parsers + tests**: FR-012a derive-from-catalog at all three stale sites + informationUri fix + prefix map re-key (OI→LLM10:2026, MI→LLM07:2026) + covering tests; FR-012b unmatched-ref stderr warning (byte-neutral — verified against CA extraction); D2 `normalize_owasp_id` test; FR-015: 8 test files, 19 fixtures, `threats.md:365` golden row, `finding.yaml` both example blocks (the LLM05 source_attribution example re-keys to LLM10); 2 web-api-coverage fixtures; D5 consistency test.
- **W4 — Coverage truth**: FR-003 gap analysis (4 absorptions vs detection patterns; per-sub-class disposition artifact); FR-004 re-derivation of all 10 verdicts with evidence; `OWASP_COVERAGE.md` hand-update (row, headline, anchor, immutable-ADR editorial note: 030/045→LLM10:2026, 031→LLM07:2026, 034→LLM06:2026); **reconcile the 10 catalog `# citation:` comments against the re-derived verdicts** (architect MEDIUM-4 — both are review-only surfaces; the last wave touching coverage truth reconciles them so a W4 Partial downgrade cannot leave a W1 comment asserting withdrawn coverage); headline restatements (README ×5 — incl. the hero **poster image** at :7 whose pixels assert 50/50: disposition = regenerate-or-annotate on any downgrade, no-op if 50/50 holds (PM plan-review W3) —, scope.md, developer guide :1805 **and :1815** (rename + bare codes, PM W2), `docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md` (in scope — only the base CONSUMER_GUIDE is immutable), system-design README :130, remaining doc-site copy). A Partial downgrade cascades honestly (triad-visible scope.md edit).
- **W5 — Sweep + close-out**: FR-008 exclusion-listed sweep (`git grep`, gitignored-but-tracked visible); FR-014 bare-code ledger completion per D8; `init-baseline-tree` regen same-commit if its sources moved; byte-identity suite green on committed HEAD (no-churn proof); changelog (movement map, migration table, carve-out + mid-window wrong-attribution disclosure); file follow-up issues (F-362b blocking-before-next-minor; `_canonical()` decided-defer incl. false-docstring defect; any FR-003 gap issues).
- **Deliver stage (not build)**: live link-rot `workflow_dispatch` (`no_cache: true`); expect #332 tracker churn; new-rot disposition pre-decided (file, don't absorb). Deliver hygiene per KB 18 (branch-current, `main`==`origin/main` full-tree check).

**Session strategy** (team-lead C-plan + KB clean-session phasing): W0+W1 one session; W2 its own session (widest fan-out); W3–W5 one to two sessions. Task ceiling ≤26, bucket-scoped.

## PM Spec-Review Concern Resolutions (W1–W3 from spec sign-off)

- **W1 (ADR-index prose vs SC-002)** → resolved by **D7**: ledger class `retained-historical`; README-architecture file stays in scope for its non-index content; SC-002 reworded operationally as "zero undispositioned".
- **W2 (`cwe_refs` unbounded pull)** → resolved by **D6**: resolve-only fence + follow-up-issue escape; no `cwe.yaml` growth in-loop.
- **W3 (residual bare-code evidence bar)** → resolved by **D8**: two-tier bar with the mixed-file escalation rule; denominators pinned to research-measured censuses (41 occurrence-level / 366 file-level total / 103 transferred to F-362b).

## Verification & Gates

1. **Pre-state artifact** (W0): literal totals checked into `specs/362-*/test-results-prestate.md`.
2. **Integrity suite** after W1 and at W5: `tests/schemas/test_taxonomy_integrity.py` all green.
3. **Byte-identity gate** (FR-007a/FR-010): `test_backward_compatibility.py` green on **committed HEAD** pre-merge; zero baseline bytes changed; #329 guard green explicitly uninformative.
4. **Sweep gate** (SC-002 per D7): `git grep -nE 'LLM(0[1-9]|10):2025'` outside exclusions → every hit ledger-dispositioned or zero; prose scan for `LLM Top 10 2025`-style strings likewise.
5. **Gated pytest subset** green on committed HEAD; totals reconciled to pre-state. Note (architect HIGH-2 favorable fact): `tachi-pytest.yml` `&hardening_paths` already covers `scripts/generate-threats-sarif.py` and `schemas/finding.yaml` — the gated subset fires in CI on this PR, so this gate is CI-verifiable, not in-loop-only.
6. **Catalog-drift workflow** (`tachi-catalog-drift.yml`) fires on this PR (`&drift_paths` covers `schemas/taxonomy/*.yaml` and `scripts/extract-report-data.py`): **expected green, uninformative for this change class** (architect MEDIUM-1) — a green check is NOT remap validation; `_canonical()` fingerprints `[id, out_of_scope]` only, both unchanged.
7. **Deliver**: live link-rot dispatch; release-please verification (`feat(362):`).

## Risks (delta over PRD — plan-stage additions)

- **2026 per-entry URLs may not exist at build time** (research-verified unindexed) → D9 interim-anchor rule; ledger records substitutions; deliver dispatch validates.
- **Breadcrumb leakage into token surfaces** would silently break SARIF regeneration (passthrough) → D1 placement rule is normative; D2 test pins near-miss forms; FR-012b warning catches drift at extraction.
- **W2 fan-out drift** (41 files authored in parallel lanes) → per-surface checklists in tasks.md; FR-008 sweep + FR-014 ledger are the closing net.
- **Coverage downgrade cascade discovered late in W4** → gap analysis (FR-003) sequenced before restatements; restatement surface list is closed (research-enumerated), so a downgrade is a mechanical propagation, not a re-scope.
- **Accepted limitation — no in-repo detector for edition *currency*** (PM plan-review W1): D5 + FR-012a make doc↔catalog↔emitter **consistency** structural, but nothing in-repo can know OWASP published a new edition — currency is inherently an external-watch concern. De-facto tripwire: the weekly link-rot monitor reddens when an edition transition changes the upstream URL space (exactly how #332 surfaced the ATLAS scheme change). Recorded as a known limitation, not a gap to engineer around.

## Complexity Tracking

*No constitution violations — table intentionally empty.*
