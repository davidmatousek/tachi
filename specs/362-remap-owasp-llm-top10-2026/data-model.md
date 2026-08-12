# Data Model: F-362 Remap OWASP LLM Top 10 → 2026

**Date**: 2026-08-06 · Companion to [plan.md](plan.md). All line refs verified at `747805c`.

## 1. Permutation Map σ (normative — derived from the movement map)

σ maps a 2025 id to the 2026 id carrying the **same category**. Applied to crosswalk `source.id` (re-key) and to every mapping decision. Verified bijection (image = all 10 ids, no collisions).

| 2025 id | σ → 2026 id | Category (2026 name) | Re-key? |
|---|---|---|---|
| LLM01 | LLM01 | Prompt Injection | hold (disposition only) |
| LLM02 | LLM02 | Sensitive Information Disclosure | hold (disposition only) |
| LLM03 | LLM04 | Supply Chain | yes |
| LLM04 | LLM05 | Data and Model Poisoning | yes |
| LLM05 | LLM10 | Improper Output Handling | yes |
| LLM06 | LLM03 | Excessive Agency | yes |
| LLM07 | LLM08 | **Hidden Context Exposure** (renamed) | yes |
| LLM08 | LLM09 | Vector and Embedding Weaknesses | yes |
| LLM09 | LLM07 | Misinformation | yes |
| LLM10 | LLM06 | Unbounded Consumption | yes |

**Application rule**: single simultaneous pass (all 57 re-keying edges permuted in one edit operation) — sequential per-id renames collide on the crosswalk dedupe key mid-flight.

## 2. Catalog Slot Table (post-surgery target state, `schemas/taxonomy/owasp.yaml:439–517`)

Ids and record order unchanged (sort invariant by construction). Per-slot 2026 content + `# citation:` re-attestation target:

| id slot | 2026 `name` (verbatim) | `full_id` | Scope delta | Citation re-attestation anchor (detection tier) |
|---|---|---|---|---|
| LLM01 | Prompt Injection | OWASP-LLM-2026-01 | + cross-modal (image/audio) injection | prompt-injection agent |
| LLM02 | Sensitive Information Disclosure | OWASP-LLM-2026-02 | — | info-disclosure / prompt-injection tier |
| LLM03 | Excessive Agency | OWASP-LLM-2026-03 | was LLM06:2025 | tool-abuse / agent-autonomy (NOT data-poisoning) |
| LLM04 | Supply Chain | OWASP-LLM-2026-04 | + model-artifact authenticity | data-poisoning + model-theft supply-chain tier (P1 ruling 2026-08-09: `tachi-tampering` carries no LLM attestation — its supply-chain cats are A08/A06:2021 + M2:2024; do not cite tampering here) |
| LLM05 | Data and Model Poisoning | OWASP-LLM-2026-05 | + fine-tuning subversion | data-poisoning agent |
| LLM06 | Unbounded Consumption | OWASP-LLM-2026-06 | was LLM10:2025 | denial-of-service + model-theft (ADR-034 lineage) |
| LLM07 | Misinformation | OWASP-LLM-2026-07 | was LLM09:2025 | misinformation agent (ADR-031 lineage) |
| LLM08 | Hidden Context Exposure | OWASP-LLM-2026-08 | renamed from System Prompt Leakage; broader hidden-context trust failure | prompt-injection / info-disclosure tier |
| LLM09 | Vector and Embedding Weaknesses | OWASP-LLM-2026-09 | was LLM08:2025 | data-poisoning (RAG/embedding patterns) |
| LLM10 | Improper Output Handling | OWASP-LLM-2026-10 | + insecure generated code at scale | output-integrity agent (ADR-030/045 lineage) |

Field rules: `id`/`out_of_scope`/order untouched · `url` = live-verified 2026 URL per plan D9 (interim = release resource page, ledger-recorded) · `cwe_refs` per plan D6 fence (default `[]`) · `# citation:` comment content follows the **category**, not the id slot.

## 3. Crosswalk Edge (existing shape — frozen)

`{source{taxonomy,id}, target{taxonomy,id}, edge_type: primary|related|superseded, confidence: high|medium|low, citation}` — exactly 5 keys, extras rejected. LLM-keyed population 74 (66 primary / 8 related) of 645. Expected post-σ per-2026-id counts: LLM01=8, LLM02=9, LLM03=7, LLM04=8, LLM05=6, LLM06=11, LLM07=4, LLM08=6, LLM09=7, LLM10=8 (Σ=74).

**Target-endpoint completeness (architect MEDIUM-2)**: verified at `747805c` — **0** crosswalk edges carry an owasp LLM id as a *target* endpoint, so source-only σ is complete. W1's oracle re-verifies this count before applying the permutation (an LLM target endpoint added since the measurement would be invisible to both the integrity suite and the source-keyed ledger).

## 4. Crosswalk Disposition Ledger (checked-in: `specs/362-*/crosswalk-disposition-ledger.md`)

One row per LLM-keyed edge (74 rows). Columns:

| Column | Values / rule |
|---|---|
| `edge` | ordinal + old `source.id` + target `taxonomy:id` + `edge_type` (unique per dedupe key) |
| `re-key` | `held` (LLM01/LLM02) \| `σ-applied: LLMNN→LLMMM` |
| `target-verdict` | `valid-2026` \| `revised: <new target>` \| `dropped: <reason>` (vs the 2026 category definition; LLM08 broadened scope + LLM01 cross-modal are the acute reviews) |
| `confidence-action` | `hold` \| `downgrade: <one-sentence reason>` (anti-drift rule: no articulable citation ⇒ downgrade) |
| `citation-action` | `re-anchored: <2026 URL>` \| `interim-resource-page` (D9) \| `unchanged: <non-year URL/repo file>` |
| `reviewer-note` | free text (may be empty for clean holds) |

Completion bar: 74/74 rows; 57/57 σ-applied; 54/54 citation-actions ∈ {re-anchored, interim-resource-page}.

## 5. Bare-Code Disposition Ledger (checked-in: `specs/362-*/bare-code-ledger.md`, two-tier per plan D8)

**Tier A — occurrence-level** (41 concentrated bare refs in 8 files + any mixed file): columns `file:line` · `form` (bare/plain-2025) · `2025 meaning` · `action` (`re-key → LLMNN:2026 context` \| `retained-historical` \| `already-2026-correct`) · note.
**Tier B — file-level** (remaining in-scope bare files, 366-census accounting): columns `file` · `bare count` · `form classes present` · `disposition class` (`fully-re-keyed` \| `retained-historical` \| `mixed→escalated to Tier A` \| `carve-out→F-362b`).
Known Tier-A population: personas misinformation(7) output-integrity(5) data-poisoning(3) model-theft(3) prompt-injection(2); skill refs output-integrity(11) misinformation(7) tool-abuse(3). Known `retained-historical` candidates: `docs/architecture/README.md:57–69` ADR-index prose (plan D7); legacy-form-exercising fixtures.

## 6. Coverage Matrix Row (`docs/standards/OWASP_COVERAGE.md:20`)

`| LLM 2026 | OWASP-LLM-2026 | LLM01–LLM10 | <n>/10 | <2026 anchor URL> | ADR-030, ADR-031, ADR-034, ADR-045 |` + editorial note that the cited detection ADRs are immutable 2025-code records whose lineage re-keys (030/045→LLM10:2026; 031→LLM07:2026; 034→LLM06:2026). Verdict model per category: `Covered(evidence: agent + pattern category)` | `Partial(gap: <absorbed sub-class>, issue #NNN)`.

## 7. Gap-Analysis Disposition (checked-in: `specs/362-*/gap-analysis.md`)

One record per absorption: `{sub-class, 2026 category, existing-detection evidence (agent + pattern-catalog citation) | gap → follow-up issue #, verdict impact (none | Partial downgrade)}` — 4 records: cross-modal injection (LLM01), model-artifact authenticity (LLM04), fine-tuning subversion (LLM05), insecure generated code at scale (LLM10).

## 8. Token Grammar

Normative contract: [contracts/references-token-grammar.md](contracts/references-token-grammar.md) (mirrors ADR-048 D1/D2).
