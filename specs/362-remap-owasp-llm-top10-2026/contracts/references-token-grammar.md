# Contract: `references[]` Token Grammar (2026 cutover)

**Source of authority**: ADR-048 (D1/D2). This file is the normative excerpt used by build tasks; on any divergence, ADR-048 wins.

## Primary token (emitted from cutover release onward)

```
OWASP LLM<NN>:2026        # NN ∈ 01..10, zero-padded; single space after "OWASP"; no trailing text
```

Examples: `OWASP LLM01:2026`, `OWASP LLM10:2026`.

## Placement rules (normative)

| Surface | Rule |
|---|---|
| `references[]` (finding contract, `schemas/finding.yaml`) | Pure tokens only — primary token, `ASI-NN`, `MCP-NN`, `CWE-NNN`. **No breadcrumbs, no annotations.** |
| `threats.md` References column | Pure tokens only (parsed by `normalize_owasp_id`; the `$`-anchored regex treats any suffix as passthrough garbage). |
| `source_attribution` | Bare catalog-resolving ids only (`LLM01..LLM10`, 2026 meanings). Never year-suffixed (FR-012c fixes the 8 pre-existing violations). Never dual-rowed for aliasing (exact-equality classification would double-count). |
| Narrative prose (finding descriptions, persona/skill prose, docs, changelog) | Transition breadcrumb allowed for ONE release: `OWASP LLM03:2026 (2025: LLM06)` — exact parenthetical form `(2025: LLM<NN>)`. Optional, prose-only. |
| SARIF | `help.markdown` prose follows the prose rule; `run.taxonomies[]` in threats-SARIF stays OWASP-2021/CWE (out of scope, index-stable); risk-scores SARIF taxa derive from the catalog (FR-012a). |

## Parser lockstep (FR-006b)

`scripts/generate-threats-sarif.py::normalize_owasp_id` (`:387`): regex `^OWASP\s+LLM(\d+):\d+$` is year-agnostic — 2026 tokens parse today. Required in the same commit as any grammar change: a covering test asserting
`OWASP LLM01:2025` → `LLM-01`, `OWASP LLM10:2026` → `LLM-10`, breadcrumb-suffixed string → passthrough (pinned), non-OWASP strings (`ASI-01`, `CWE-287`) → their branches, unknown → passthrough (pinned).

## Legacy tokens

`OWASP LLM<NN>:2025` remains permanently self-describing (cites the 2025 edition explicitly). It is never re-emitted after cutover; occurrences in immutable records (FR-008 exclusion set) and ledger-dispositioned `retained-historical` sites persist unedited.

## Migration surface (changelog, FR-011)

The changelog carries the σ movement table (old token → new token, all 10 rows) + the Hidden Context Exposure rename note + the F-362b carve-out disclosure (mid-window: `examples/**` still shows 2025 tokens and CA pages attribute under 2025 meanings until F-362b lands).
