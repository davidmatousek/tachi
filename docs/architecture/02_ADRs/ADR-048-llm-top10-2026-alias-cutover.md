# ADR-048: OWASP LLM Top 10 2026 Cutover — Alias Policy and References Token Grammar

**Status**: Accepted (provisional pre-PR) 2026-08-06 — ratified at architect review of F-362 plan.md (dual-commit protocol, ADR-027 Decision 8)
**Date**: Proposed 2026-08-06 · Accepted 2026-08-06
**Accepted-commit-SHA**: `e6316e34ae1be6e3967ba836945994b076b19b76` (PR #363 squash-merge, 2026-08-12)
**Deciders**: architect (owner), product-manager (consumer-contract input), team-lead (cost input)
**Feature**: [F-362 spec](../../../specs/362-remap-owasp-llm-top10-2026/spec.md) (FR-006 hard gate)
**Supersedes**: None
**Superseded by**: None
**Related ADRs**: [ADR-013](ADR-013-sarif-2.1.0-adoption.md) (SARIF adoption — help.markdown prose is the LLM-reference surface), [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) (determinism posture the no-churn proof rides on), [ADR-027](ADR-027-taxonomy-crosswalk-schema.md) (catalog/crosswalk shapes this decision keeps frozen; +ADR-037 Extension-History discipline), [ADR-028](ADR-028-source-attribution-referential-integrity.md) (bare-id contract), ADR-030/031/034/045 (immutable detection lineage whose category attestations re-key)

> **Note (2026-11-22, Feature 374)**: Under [ADR-050](ADR-050-large-architecture-output-authority.md) D1, D3's enforcement points gain the shipped emitters. They emit only `:2026` tokens, and they reject `LLMnn:2025`.
>
> - **PR 1.** `scripts/sarif_common.py`, installed as the shared emitter, and the scorer and controls renderers, which write `risk-scores.sarif` and `compensating-controls.sarif` through it. `generate-risk-scores-sarif.py` retires, and FR-012a's taxa contract moves to the scorer renderer (ADR-050 D16).
> - **PR 2.** `scripts/generate-threats-sarif.py`, rewritten as the shipped `threats.sarif` generator on the shared emitter.
> - The authored-prose enforcement points stay for the surfaces that remain model-authored, such as `threats.md`'s tables. D1 and D2 stand.

> **Note (2026-11-25, Feature 374, PR 2; S1P-A92)**: `normalize_owasp_id` retires with the old `scripts/generate-threats-sarif.py`, which PR 2 rewrites on the shared emitter ([ADR-050](ADR-050-large-architecture-output-authority.md) D1). Its one caller wrote the result property `owasp_id`, which no `threats.sarif` contract names, so the new generator writes no such property (ADR-050's S1P-A28), and the regex that D2 pinned has no caller left.
>
> - **D2, superseded in part.** The parser side of D2's lockstep goes with the function, and so does its covering matrix in `tests/scripts/test_owasp_2026_contract.py`. 16 of the matrix's 22 items exercised branches that only `owasp_id` used: the LLM, ASI and MCP token forms, zero-padding, the breadcrumb and passthrough cases and the unmapped prefix. The other 6, each STRIDE prefix's OWASP 2021 category, still hold through each STRIDE rule's `relationships`, and one case pins them. FR-012b's unmatched-reference warning in `classify_framework_items` stays, so a drifted token form is still loud at extraction time. A future grammar change now moves D3's enforcement points and their tests in lockstep.
> - **D3, the shipped `threats.sarif` generator.** What it writes of its own, the driver's rules, their `help` and the taxonomies, names no OWASP LLM token but 2026's, and the module's surviving section (b) pins that. The prose it copies from `threats.md` stays under the authored-prose enforcement points.
> - **D1 stands.** Token surfaces still carry pure tokens only, because exact-match readers such as `classify_framework_items` read them, and adopters' tools may too.

## Context

OWASP published the Top 10 for LLM Applications 2026 (v1.0, 2026-08-04). The rank order changed, so bare codes changed meaning (LLM03: Supply Chain in 2025 → Excessive Agency in 2026); LLM07:2025 System Prompt Leakage was renamed and re-scoped to LLM08:2026 Hidden Context Exposure. Downstream consumers may be pinned to 2025 identifiers. F-362 (PRD FR-6 / spec FR-006) requires this alias/cutover decision **before any remap mechanics**, because it constrains every emission surface.

Constraints established at research (specs/362-*/research.md):
- Production `threats.md`/`.sarif` are **LLM-authored**; the SARIF generator scripts have no production caller — the real enforcement points are authored prose: 9 agent personas, 15 skill reference files, `schemas/finding.yaml` example blocks, the sarif-specification templates, and the `threats.md` golden row.
- `source_attribution.id` must remain a bare catalog-resolving id; `extract-report-data.py::classify_framework_items` matches by exact equality — a dual/aliased attribution row would double-count CA-page classification.
- `normalize_owasp_id` (`generate-threats-sarif.py:387`) parses `^OWASP\s+LLM(\d+):\d+$` with `$`-anchor and silent passthrough on mismatch; zero test coverage today.
- Catalog and crosswalk schemas are shape-frozen (crosswalk edges hard-reject extra keys); adding an alias field would trigger ADR-027 Extension History + integrity-test churn.
- Industry precedent is split: MITRE ATLAS (dual content/format versioning), Snyk (structural dual-support), Semgrep (deprecation markers + migration guidance). No official OWASP vendor-migration guidance exists.
- Team-lead pricing: dual-emission is the 10.0-attention-day ceiling driver; hard cutover holds the ~4.5-day central path.
- OWASP's own token grammar is edition-suffixed (`LLM01:2025`, `LLM01:2026`) — an emitted legacy token is permanently self-describing.

## Decision

### D1 — Hard cutover with one-release prose breadcrumbs (no dual-emission)

From the F-362 release onward, tachi emits **only** 2026 tokens. The primary `references[]` token is:

```
OWASP LLM<NN>:2026        # NN ∈ 01..10 zero-padded; single space; no trailing text
```

**Placement rules (normative)**:
- `references[]` arrays, the `threats.md` References column, and all machine-parsed token surfaces carry **pure tokens only** — no annotations (the `$`-anchored parser treats any suffix as passthrough).
- `source_attribution` carries bare 2026-meaning ids (`LLM01..LLM10`) — never year-suffixed, never dual-rowed for aliasing (F-362 FR-012c also fixes the 8 pre-existing year-suffixed violations).
- Narrative prose (finding descriptions, persona/skill prose, docs, changelog) MAY carry a transition breadcrumb for **one release**: exact form `(2025: LLM<NN>)` — e.g. `OWASP LLM03:2026 (2025: LLM06)`. Prose only; removed no later than the following minor release.
- Legacy `OWASP LLM<NN>:2025` tokens are never re-emitted; occurrences persist unedited only in immutable records (FR-008 exclusion set) and ledger-dispositioned `retained-historical` sites.

**Why hard cutover**: (1) the year suffix already version-disambiguates every historical output — the usual dual-emission motivation (ambiguous legacy identifiers) does not apply; (2) dual-emission cannot reach `source_attribution` without corrupting CA classification counts, so it would cover only prose/references surfaces while doubling churn across the 45-file authored surface and adding alias machinery + tests (the priced ceiling); (3) the consumer base is early-stage with no known pinned pipelines — a changelog migration table (full σ movement map) plus breadcrumbs delivers the migration value at near-zero machinery.

### D2 — Parser/test lockstep

`normalize_owasp_id`'s regex is year-agnostic and parses 2026 tokens unchanged. A **net-new covering test** lands in the same commit as the first grammar-bearing edit, pinning: `OWASP LLM01:2025` → `LLM-01`; `OWASP LLM10:2026` → `LLM-10`; breadcrumb-suffixed string → passthrough (documents why token surfaces forbid breadcrumbs); ASI/MCP/CWE branches; unknown-string passthrough. Any future grammar change moves the regex and this test in lockstep (spec FR-006b). Complementarily, `classify_framework_items` gains an unmatched-ref stderr warning (spec FR-012b) so token-form drift is loud at extraction time.

### D3 — Enforcement points

The grammar is enforced where production emissions are actually authored: the 9 tachi agent personas, the 15 skill reference files, `schemas/finding.yaml` (both example blocks), `sarif-specification.md` templates, and the `templates/tachi/output-schemas/threats.md:365` golden row. The generator scripts (`generate-threats-sarif.py`, `generate-risk-scores-sarif.py`) move in lockstep but are regeneration-only, not the contract's enforcement mechanism. The risk-scores SARIF taxa derive from the catalog (spec FR-012a), making next-edition taxa drift structurally impossible.

## Alternatives Considered

- **Dual-emission (2026 primary + 2025 alias for one release)** — Pros: softest consumer migration; Snyk precedent. Cons: cannot reach `source_attribution` (double-count) so coverage is partial by construction; ~2× churn on 45 authored files; alias machinery + schema/test cost = priced 10.0d ceiling; mid-window outputs mix meanings. **Why not**: partial protection at maximal cost; the year-suffixed grammar already protects historical outputs.
- **Catalog alias field (e.g. `aliases: [LLM06:2025]`)** — Pros: machine-readable lineage. Cons: breaks the frozen record shape; ADR-027 Extension History + integrity-test churn; crosswalk cannot mirror it (extra keys rejected); consumers of the field are hypothetical. **Why not**: schema churn for no identified consumer; σ lineage is already machine-readable in the changelog table and ledgers.
- **Pure cutover, no breadcrumbs** — Pros: minimal. Cons: a consumer grepping an old code gets zero forwarding signal in fresh outputs during the transition window. **Why not chosen alone**: breadcrumbs are zero-machinery (prose convention, no parser impact) and time-boxed.

## Consequences

**Positive**: holds the ~4.5d central estimate (floor path); zero schema churn; CA classification integrity preserved; single-meaning outputs (no mixed-edition emissions); recurrence-proof taxa via FR-012a.
**Negative**: consumers pinned to 2025 identifiers must migrate in one step at upgrade.
**Mitigation**: changelog migration table (σ movement map, all 10 rows) + one-release breadcrumbs + self-describing legacy tokens + F-362b carve-out disclosure (mid-window `examples/**` still shows 2025 tokens); deliver-stage live link-rot dispatch validates the re-anchored citation set.

## References

- F-362 PRD v1.2 (FR-6) · spec FR-006 · plan.md Phase 0 D1–D3 · contracts/references-token-grammar.md (normative excerpt)
- OWASP Top 10 for LLM Applications 2026 v1.0 — https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/
- Industry precedent survey: specs/362-remap-owasp-llm-top10-2026/research.md §Industry Research (MITRE ATLAS, Snyk, Semgrep)

---

**2026-08-12 (Amendment — F-362 final-review S6, recorded at deliver alongside the Accepted-commit-SHA fill)**: The F-142 zero-edit invariant narrowing shipped in this cutover (`tests/scripts/test_backward_compatibility.py:249-291` — the invariant now enforces only on `142-*` branches) is an architect-acknowledged **scope correction**, not a weakening: ADR-026 constrains F-142's synthesis mechanism specifically, not the detection tier repo-wide. Prior to F-362 the check over-enforced, freezing detection-tier files against edits ADR-026 never governed.
