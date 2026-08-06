# Contract: Disposition Ledger Formats (F-362)

Both ledgers are checked-in markdown tables under `specs/362-remap-owasp-llm-top10-2026/`, scaffolded in W0 **before any edit** (KB 13 Foundational-artifact rule), completed incrementally by the wave that owns each surface, and verified at the W5 sweep gate. Schemas: [data-model.md](../data-model.md) §4–§5. Evidence bars: plan.md D7/D8.

## crosswalk-disposition-ledger.md
- 74 rows (one per LLM-keyed edge), columns per data-model §4.
- Mechanical σ-permutation is diff-reviewable; the ledger records the **human** disposition (target-verdict, confidence-action, citation-action) — the part no test can check.
- Completion bar: 74/74 dispositioned · 57/57 σ-applied · 54/54 citation-actions resolved (re-anchored or interim per plan D9).

## bare-code-ledger.md
- Tier A (occurrence-level): the 41 concentrated bare refs (8 files) + any file mixing `retained-historical` with active refs.
- Tier B (file-level): every remaining in-scope file with bare refs, accounting the 366-census; carve-out files (103 bare) row-marked `carve-out→F-362b` and transferred to the F-362b ledger at issue-filing time.
- Completion bar: Tier A 41/41 + escalations · Tier B census fully accounted (Σ Tier A + Tier B counts + carve-out = 366+103).

## Verification hooks (W5)

Verified command forms (PM plan-review CRITICAL fix, 2026-08-06 — git ERE has no `\b`; occurrence counts use `-oP`, since `-c` counts lines):
- Suffixed reconciliation: `git grep -oP '\bLLM(0[1-9]|10):2025' -- <in-scope paths> | wc -l` reconciles to ledger + exclusion counts.
- Bare census: `git grep -oP '\bLLM(0[1-9]|10)\b(?!:)' -- <in-scope paths> | cut -d: -f1 | sort | uniq -c` reconciles per-file to Tier A+B accounting; any unaccounted hit fails the sweep gate (SC-002 per plan D7: zero **undispositioned**).
- Sanity rule: every gate command must demonstrably produce hits on the pre-remap tree before it may be trusted to report zero after (a gate that cannot fail is not a gate).
