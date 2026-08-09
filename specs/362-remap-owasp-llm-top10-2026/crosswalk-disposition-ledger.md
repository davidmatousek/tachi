# Crosswalk Disposition Ledger (F-362)

Scaffolded at **T002** per [contracts/disposition-ledgers.md](contracts/disposition-ledgers.md) and [data-model.md](data-model.md) §4. One row per LLM-keyed edge in `schemas/taxonomy/crosswalk.yaml`, in the file's native edge order. The mechanical σ-permutation (T006) and the citation URL-scheme gate (T003) are diff-reviewable elsewhere; this ledger records the **human** disposition — the part no test can check.

**Completion bar** (target, per contract): 74/74 dispositioned · 57/57 σ-applied · 54/54 citation-actions resolved (re-anchored or interim per plan D9).
**Current status**: 0/74 dispositioned · 0/57 σ-applied · 0/54 citation-actions resolved — **scaffold only (T002)**. `re-key` / `target-verdict` / `confidence-action` are filled by **T006**; `citation-action` is finalized by **T007** after the **T003** URL-policy gate.

---

### URL policy (T003)

**Verdict**: BRANCH 2 (interim-resource-page) — Verified 2026-08-09

**Anchor Policy**: Per-entry OWASP LLM Top 10 2026 pages do NOT exist on genai.owasp.org. All attempted 2026-specific URL patterns returned 404 (tested: `/llmrisk/llm012026-prompt-injection/`, `/llmrisk/llm082026-hidden-context-exposure/`, `/llm-top-10-2026/`, and variants). Evidence: 8 fetch attempts, 6 unique 404s, 2 successful confirmations of 2025 editions still live. The released 2026 Top 10 document (published 2026-08-04) is currently only available as a PDF download from the release resource page.

**Citation Anchor** (all re-anchored citations per T007):
```
https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/
```

**Application**: 54 crosswalk edges with year-slugged (2025-edition) OWASP LLM citations will be re-anchored to the interim resource page (per data-model §4). When per-entry 2026 pages appear and are verified, T007 will update ledger rows and apply the new URLs in bulk. Non-year-slugged URLs (20 edges) remain candidates for unchanged status pending T007 review. See full fetch evidence in `.aod/results/web-researcher.md`.

---

### σ-oracle preconditions (T002)

**Method**: live Python script (stdlib + PyYAML, no new dependency — rung 3/5 of the laziness ladder) against `schemas/taxonomy/crosswalk.yaml` at HEAD `601d7d4` (branch `362-remap-owasp-llm-top10-2026`), run 2026-08-09. `yaml.safe_load()` over the full edge list (a flat list of 5-key edge dicts — no nested traversal needed); counts computed by exact key match on `source.taxonomy`, `source.id` (regex `^LLM(0[1-9]|10)$`), `target.taxonomy`, `target.id`, `edge_type`, and substring `"2025"` in `citation`. This is a direct structural read, not a `grep` approximation, so it cannot be fooled by formatting (e.g., the four edges whose `target.taxonomy` is `mitre-attack`/`mitre-atlas` but whose `citation` still anchors to a year-slugged `genai.owasp.org` URL are correctly counted because the check reads each edge's own `citation` field, not an inference from its target).

| # | Check | Expected | Live result | Verdict |
|---|---|---|---|---|
| 1 | Total crosswalk edges | 645 | 645 | MATCH |
| 2 | LLM-keyed edges (`source.taxonomy == owasp`, `source.id` ∈ LLM01–LLM10) | 74 (66 primary / 8 related) | 74 (66 primary / 8 related) | MATCH |
| 3 | LLM-keyed edges as a **target** endpoint (any source, `target.taxonomy == owasp`, `target.id` ∈ LLM01–LLM10) | 0 | 0 | MATCH |

**Header status: CLEAN — no count divergence.** All three σ-oracle counts match the data-model §3 / plan MEDIUM-2 projections exactly.

Check 3 is the **σ-oracle precondition for T006** (architect plan MEDIUM-2): source-only permutation is only complete if zero crosswalk edges carry an OWASP-LLM id as a target endpoint. Verified 0 at `601d7d4` — T006 may proceed with a source-only single-pass σ-permutation. T006 re-verifies this count immediately before applying the permutation (an LLM target endpoint added between this measurement and T006's run would be invisible to both the byte-identity integrity suite and this source-keyed ledger).

**Citation year-slug pre-note** (mechanical URL inspection, see Ledger below): of the 74 LLM-keyed edges, **54 carry a year-slugged (2025-edition) citation URL** needing re-anchor, and 20 carry a non-year URL (`unchanged-candidate`). 54 matches the plan D9 / data-model §4 completion-bar denominator exactly.

**Independent cross-check** (not one of the three required counts, included for confidence): per-`source.id` 2025 edge counts are LLM01=8, LLM02=9, LLM03=8, LLM04=6, LLM05=8, LLM06=7, LLM07=6, LLM08=7, LLM09=4, LLM10=11 (Σ=74). Permuting these through σ (data-model §1: LLM03→LLM04, LLM04→LLM05, LLM05→LLM10, LLM06→LLM03, LLM07→LLM08, LLM08→LLM09, LLM09→LLM07, LLM10→LLM06, LLM01/LLM02 held) reproduces the post-σ per-2026-id projection in data-model §3 (8/9/7/8/6/11/4/6/7/8) exactly, an independent confirmation that the live file matches the plan's counting.

---

## Ledger

Columns per data-model §4. Only `#` and `edge` are pre-seeded from the live file. `re-key`, `target-verdict`, and `confidence-action` are left `—` (pending T006/T007). `citation-action` also reads `—` (no disposition made yet) but carries a **mechanical** parenthetical pre-note — year-slugged vs non-year URL, from live URL inspection only, **not** a disposition — so T007 can triage without re-deriving it; the actual `re-anchored: <2026 URL>` / `interim-resource-page` / `unchanged: <URL>` verdict is T007's, applied after the T003 gate. `reviewer-note` is free text, left `—`.

| # | edge | re-key | target-verdict | confidence-action | citation-action | reviewer-note |
|---|------|--------|-----------------|--------------------|--------------------|-----------------|
| 1 | LLM01 → cwe:CWE-77 (primary) | — | — | — | — (non-year URL; unchanged-candidate) | — |
| 2 | LLM02 → cwe:CWE-200 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 3 | LLM03 → cwe:CWE-1395 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 4 | LLM04 → cwe:CWE-20 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 5 | LLM05 → cwe:CWE-79 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 6 | LLM01 → cwe:CWE-20 (primary) | — | — | — | — (non-year URL; unchanged-candidate) | — |
| 7 | LLM01 → cwe:CWE-94 (primary) | — | — | — | — (non-year URL; unchanged-candidate) | — |
| 8 | LLM01 → cwe:CWE-1427 (primary) | — | — | — | — (non-year URL; unchanged-candidate) | — |
| 9 | LLM02 → cwe:CWE-201 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 10 | LLM02 → cwe:CWE-538 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 11 | LLM02 → cwe:CWE-359 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 12 | LLM03 → cwe:CWE-1357 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 13 | LLM03 → cwe:CWE-494 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 14 | LLM03 → cwe:CWE-829 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 15 | LLM04 → cwe:CWE-502 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 16 | LLM04 → cwe:CWE-915 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 17 | LLM04 → cwe:CWE-1395 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 18 | LLM05 → cwe:CWE-89 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 19 | LLM05 → cwe:CWE-116 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 20 | LLM05 → cwe:CWE-78 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 21 | LLM05 → cwe:CWE-601 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 22 | LLM06 → cwe:CWE-250 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 23 | LLM06 → cwe:CWE-269 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 24 | LLM06 → cwe:CWE-285 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 25 | LLM06 → cwe:CWE-732 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 26 | LLM07 → cwe:CWE-200 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 27 | LLM07 → cwe:CWE-538 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 28 | LLM07 → cwe:CWE-540 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 29 | LLM07 → cwe:CWE-1426 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 30 | LLM08 → cwe:CWE-200 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 31 | LLM08 → cwe:CWE-209 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 32 | LLM08 → cwe:CWE-285 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 33 | LLM08 → cwe:CWE-639 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 34 | LLM09 → cwe:CWE-345 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 35 | LLM09 → cwe:CWE-1426 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 36 | LLM09 → cwe:CWE-20 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 37 | LLM10 → cwe:CWE-400 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 38 | LLM10 → cwe:CWE-770 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 39 | LLM10 → cwe:CWE-799 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 40 | LLM10 → cwe:CWE-918 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 41 | LLM01 → mitre-atlas:AML.T0051 (primary) | — | — | — | — (non-year URL; unchanged-candidate) | — |
| 42 | LLM04 → mitre-atlas:AML.T0020 (primary) | — | — | — | — (non-year URL; unchanged-candidate) | — |
| 43 | LLM04 → mitre-atlas:AML.T0018 (primary) | — | — | — | — (non-year URL; unchanged-candidate) | — |
| 44 | LLM03 → mitre-atlas:AML.T0010 (primary) | — | — | — | — (non-year URL; unchanged-candidate) | — |
| 45 | LLM03 → mitre-attack:T1195 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 46 | LLM06 → mitre-atlas:AML.T0061 (primary) | — | — | — | — (non-year URL; unchanged-candidate) | — |
| 47 | LLM06 → mitre-attack:T1548 (primary) | — | — | — | — (non-year URL; unchanged-candidate) | — |
| 48 | LLM07 → mitre-atlas:AML.T0057 (primary) | — | — | — | — (non-year URL; unchanged-candidate) | — |
| 49 | LLM10 → mitre-attack:T1499 (primary) | — | — | — | — (non-year URL; unchanged-candidate) | — |
| 50 | LLM10 → mitre-attack:T1498 (primary) | — | — | — | — (non-year URL; unchanged-candidate) | — |
| 51 | LLM05 → mitre-atlas:AML.T0051 (primary) | — | — | — | — (non-year URL; unchanged-candidate) | — |
| 52 | LLM05 → mitre-atlas:AML.T0060 (primary) | — | — | — | — (non-year URL; unchanged-candidate) | — |
| 53 | LLM08 → mitre-atlas:AML.T0057 (primary) | — | — | — | — (non-year URL; unchanged-candidate) | — |
| 54 | LLM08 → mitre-atlas:AML.T0051 (primary) | — | — | — | — (non-year URL; unchanged-candidate) | — |
| 55 | LLM01 → cwe:CWE-79 (primary) | — | — | — | — (non-year URL; unchanged-candidate) | — |
| 56 | LLM01 → cwe:CWE-116 (primary) | — | — | — | — (non-year URL; unchanged-candidate) | — |
| 57 | LLM02 → cwe:CWE-532 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 58 | LLM02 → cwe:CWE-209 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 59 | LLM05 → cwe:CWE-94 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 60 | LLM06 → cwe:CWE-284 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 61 | LLM08 → cwe:CWE-287 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 62 | LLM10 → cwe:CWE-1333 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 63 | LLM02 → mitre-attack:T1005 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 64 | LLM02 → mitre-attack:T1213 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 65 | LLM03 → mitre-attack:T1195.001 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 66 | LLM03 → mitre-attack:T1195.002 (primary) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 67 | LLM01 → mitre-atlas:AML.T0054 (related) | — | — | — | — (non-year URL; unchanged-candidate) | — |
| 68 | LLM02 → mitre-atlas:AML.T0024 (related) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 69 | LLM07 → mitre-atlas:AML.T0051 (related) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 70 | LLM09 → mitre-atlas:AML.T0048 (related) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 71 | LLM10 → mitre-atlas:AML.T0024 (related) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 72 | LLM10 → mitre-atlas:AML.T0025 (related) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 73 | LLM10 → mitre-atlas:AML.T0029 (related) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
| 74 | LLM10 → mitre-atlas:AML.T0034 (related) | — | — | — | — (year-slugged 2025 URL; needs re-anchor per T003 policy) | — |
