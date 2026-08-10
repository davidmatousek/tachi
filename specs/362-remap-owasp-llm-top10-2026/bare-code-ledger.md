# Bare-Code Disposition Ledger (F-362)

Scaffolded at **T002** per [contracts/disposition-ledgers.md](contracts/disposition-ledgers.md) and [data-model.md](data-model.md) §5. Two-tier ledger (plan D8): **Tier A** (occurrence-level) covers the 41 concentrated bare refs across 8 files; **Tier B** (file-level) covers every remaining in-scope bare-ref file, accounting the 366-file in-scope census. Carve-out files (103 bare refs, `examples/**`) transfer to the F-362b ledger at issue-filing time.

**Completion bar** (target, per contract): Tier A 41/41 (union of both lanes) · Tier B census fully accounted (366 + 103).
**Current status**: Tier A **41/41 canonical COMPLETE** (T008 20/20 + T009 21/21; 55 rows total = 41 canonical + 7 FR-012c form-bug + 7 breadcrumb `retained-historical`; reconciled by orchestrator after both B1 lanes landed, 2026-08-10) · Tier B census not yet populated — **T022, Session D** (must pick up the 4 T008 out-of-section bares and the 9 T009 Tier-B breadcrumbs enumerated in the lane-arithmetic notes below).

---

## Tier A — occurrence-level (41 concentrated bare refs, 8 files)

**Lane rule (architect MEDIUM-3 / team-lead F4)**: Tier A is pre-partitioned below into two independently-owned lane sections, in this order: personas (T008), then skill references (T009). Each owning task appends rows **only** within its own section. Nothing row-level is pre-seeded here — only the expected populations from data-model §5, stated as the completion target each lane's task fills toward.

### Tier A — personas (T008)

append-only within your own section — never write into the other lane (architect MEDIUM-3 / team-lead F4).

Expected population: **20 occurrences / 5 files** — misinformation (7), output-integrity (5), data-poisoning (3), model-theft (3), prompt-injection (2).

All line numbers below are **post-edit** (measured after T008's persona edits). Paths are relative to repo root; the `.claude/agents/tachi/` prefix is elided for width.

**Group 1 — the 20 canonical bare occurrences** (the completion bar; bare form preserved on both sides of the re-key):

| file:line | form | 2025 meaning | action | note |
|---|---|---|---|---|
| data-poisoning.md:55 | bare | LLM03 Supply Chain | re-key → LLM04:2026 Supply Chain | `references` emission list `OWASP LLM03/LLM04/LLM08` → `OWASP LLM04/LLM05/LLM09`; pure-token list, no breadcrumb (ADR-048 D1) |
| data-poisoning.md:55 | bare | LLM04 Data and Model Poisoning | re-key → LLM05:2026 Data and Model Poisoning | same slash-list, 2nd element |
| data-poisoning.md:55 | bare | LLM08 Vector and Embedding Weaknesses | re-key → LLM09:2026 Vector and Embedding Weaknesses | same slash-list, 3rd element |
| misinformation.md:27 | bare | LLM01 Prompt Injection | re-key → LLM01:2026 Prompt Injection | σ-hold; cross-agent scope carve-out prose (`prompt-injection` ownership) |
| misinformation.md:27 | bare | LLM07 System Prompt Leakage | re-key → LLM08:2026 Hidden Context Exposure | FR-002 alias retained inline at this first mention ("renamed from the 2025 System Prompt Leakage category") |
| misinformation.md:27 | bare | LLM05 Improper Output Handling | re-key → LLM10:2026 Improper Output Handling | cross-agent scope carve-out prose (`output-integrity` ownership) |
| misinformation.md:45 | bare | LLM09 Misinformation | re-key → LLM07:2026 Misinformation | inline `source_attribution` contract snippet `{taxonomy: owasp, id: LLM07, relationship: primary}` — bare correct per ADR-028 |
| misinformation.md:66 | bare | LLM09 Misinformation | re-key → LLM07:2026 Misinformation | example finding MI-1 `source_attribution.id` |
| misinformation.md:90 | bare | LLM09 Misinformation | re-key → LLM07:2026 Misinformation | example finding MI-2 `source_attribution.id` |
| misinformation.md:114 | bare | LLM09 Misinformation | re-key → LLM07:2026 Misinformation | example finding MI-3 `source_attribution.id` |
| model-theft.md:53 | bare | LLM10 Unbounded Consumption | re-key → LLM06:2026 Unbounded Consumption | `references` emission list `OWASP LLM10/LLM07/LLM03` → `OWASP LLM06/LLM08/LLM04` |
| model-theft.md:53 | bare | LLM07 System Prompt Leakage | re-key → LLM08:2026 Hidden Context Exposure | same slash-list, 2nd element; FR-002 alias lives at first mention (:31) |
| model-theft.md:53 | bare | LLM03 Supply Chain | re-key → LLM04:2026 Supply Chain | same slash-list, 3rd element |
| output-integrity.md:25 | bare | LLM05 Improper Output Handling | re-key → LLM10:2026 Improper Output Handling | "`source_attribution` citations carry OWASP LLM10 only" — bare correct per ADR-028 |
| output-integrity.md:47 | bare | LLM05 Improper Output Handling | re-key → LLM10:2026 Improper Output Handling | inline `source_attribution` contract snippet `{taxonomy: owasp, id: LLM10, relationship: primary}` |
| output-integrity.md:68 | bare | LLM05 Improper Output Handling | re-key → LLM10:2026 Improper Output Handling | example finding OI-1 `source_attribution.id` |
| output-integrity.md:92 | bare | LLM05 Improper Output Handling | re-key → LLM10:2026 Improper Output Handling | example finding OI-2 `source_attribution.id` |
| output-integrity.md:116 | bare | LLM05 Improper Output Handling | re-key → LLM10:2026 Improper Output Handling | example finding OI-3 `source_attribution.id` |
| prompt-injection.md:43 | bare | LLM01 Prompt Injection | re-key → LLM01:2026 Prompt Injection | σ-hold; `OWASP LLM01/LLM08 references` emission guidance |
| prompt-injection.md:43 | bare | LLM07 System Prompt Leakage | re-key → LLM08:2026 Hidden Context Exposure | same guidance line; FR-002 alias retained later in the same line |

**Group 2 — FR-012c compound form-bug fixes** (architect LOW-2). Pre-edit form was `plain-2025` (year-suffixed `id:`), so these are **not** part of the 20 above; research classified them under the 17 plain-2025 refs. Fix = strip `:2025` **and** apply σ, yielding a bare catalog id per ADR-028 / ADR-048 D1. 7 of the 8 FR-012c sites fall in T008 ledger files; the 8th (`denial-of-service.md:134` → `id: LLM06`) is outside the 5 and is recorded in the T008 results file instead.

| file:line | form | 2025 meaning | action | note |
|---|---|---|---|---|
| data-poisoning.md:77 | plain-2025 | LLM03 Supply Chain | re-key → LLM04:2026 Supply Chain | FR-012c form-bug: `id: LLM03:2025` → `id: LLM04` (example finding LLM-1) |
| data-poisoning.md:105 | plain-2025 | LLM03 Supply Chain | re-key → LLM04:2026 Supply Chain | FR-012c form-bug: `id: LLM03:2025` → `id: LLM04` (example finding LLM-2) |
| model-theft.md:75 | plain-2025 | LLM03 Supply Chain | re-key → LLM04:2026 Supply Chain | FR-012c form-bug: `id: LLM03:2025` → `id: LLM04` (example finding LLM-1) |
| model-theft.md:127 | plain-2025 | LLM03 Supply Chain | re-key → LLM04:2026 Supply Chain | FR-012c form-bug: `id: LLM03:2025` → `id: LLM04` (example finding LLM-3) |
| prompt-injection.md:65 | plain-2025 | LLM01 Prompt Injection | re-key → LLM01:2026 Prompt Injection | σ-hold; FR-012c form-bug: `id: LLM01:2025` → `id: LLM01` (example finding LLM-1) |
| prompt-injection.md:93 | plain-2025 | LLM01 Prompt Injection | re-key → LLM01:2026 Prompt Injection | σ-hold; FR-012c form-bug: `id: LLM01:2025` → `id: LLM01` (example finding LLM-2) |
| prompt-injection.md:120 | plain-2025 | LLM01 Prompt Injection | re-key → LLM01:2026 Prompt Injection | σ-hold; FR-012c form-bug: `id: LLM01:2025` → `id: LLM01` (example finding LLM-3) |

**Group 3 — breadcrumb lineage bares** (net-new, introduced by T008). ADR-048 D1 permits a one-release prose breadcrumb in the exact form `(2025: LLM<NN>)`. The `LLM<NN>` inside a breadcrumb is a deliberate **2025** lineage code, not a 2026 category id, so a bare-ref sweep will match it — dispositioned here as `retained-historical` so the W5 sweep gate (SC-002) does not flag it. All are removable at the next minor release when the breadcrumb window closes.

| file:line | form | 2025 meaning | action | note |
|---|---|---|---|---|
| misinformation.md:25 | bare | LLM09 Misinformation | retained-historical | breadcrumb `OWASP LLM07:2026 (2025: LLM09)` — Purpose first-mention; drop at next minor |
| model-theft.md:33 | bare | LLM10 Unbounded Consumption | retained-historical | breadcrumb `OWASP LLM06:2026 (2025: LLM10)` — cost-amplification surface prose; drop at next minor |
| output-integrity.md:25 | bare | LLM05 Improper Output Handling | retained-historical | breadcrumb `OWASP LLM10:2026 (2025: LLM05)` — Purpose first-mention; drop at next minor |

**T008 lane arithmetic** — completion bar **20/20 met** (Group 1). Rows appended: **30** = 20 canonical bare + 7 FR-012c form-bug (pre-edit `plain-2025`, counted in research's 17, not in the 20) + 3 breadcrumb lineage bares (net-new, `retained-historical`). Post-edit bare census across the 5 T008 ledger files is 30, and reconciles exactly: 20 + 7 + 3. Three further breadcrumb bares were introduced outside the 5 ledger files (`agent-autonomy.md:25`, `agent-autonomy.md:40`, `denial-of-service.md:37`) and belong to the Tier B file-level census (T022), together with `denial-of-service.md:134` (the 8th FR-012c site) — see `.aod/results/senior-backend-engineer-T008.md`.

### Tier A — skill references (T009)

append-only within your own section — never write into the other lane (architect MEDIUM-3 / team-lead F4).

Expected population: **21 occurrences / 3 files** — output-integrity (11), misinformation (7), tool-abuse (3).

All line numbers below are **post-edit** (measured after T009's skill-reference edits; every T009 re-key was an in-line substitution, so post-edit line numbers equal pre-edit line numbers). Paths are relative to repo root; the `.claude/skills/` prefix and the `/references/detection-patterns.md` suffix are elided for width (`output-integrity:47` = `.claude/skills/tachi-output-integrity/references/detection-patterns.md:47`).

**Group 1 — the 21 canonical bare occurrences** (the completion bar; bare form preserved on both sides of the re-key, per ADR-028 bare-catalog-id contract / ADR-048 D1 `source_attribution` placement rule):

| file:line | form | 2025 meaning | action | note |
|---|---|---|---|---|
| misinformation:14 | bare | LLM09 Misinformation | re-key → LLM07:2026 Misinformation | catalog-scope prose "…that complete the LLM07 surface" (FR-017 five-category alignment sentence) |
| misinformation:49 | bare | LLM09 Misinformation | re-key → LLM07:2026 Misinformation | Pattern Cat 1 `**Primary citation**: {taxonomy: owasp, id: LLM07, relationship: primary}` — bare correct per ADR-028 |
| misinformation:75 | bare | LLM09 Misinformation | re-key → LLM07:2026 Misinformation | Pattern Cat 2 prose "…the citation-fabrication sub-class of LLM07" |
| misinformation:77 | bare | LLM09 Misinformation | re-key → LLM07:2026 Misinformation | Pattern Cat 2 `Primary citation` snippet |
| misinformation:105 | bare | LLM09 Misinformation | re-key → LLM07:2026 Misinformation | Pattern Cat 3 `Primary citation` snippet |
| misinformation:134 | bare | LLM09 Misinformation | re-key → LLM07:2026 Misinformation | Pattern Cat 4 `Primary citation` snippet |
| misinformation:162 | bare | LLM09 Misinformation | re-key → LLM07:2026 Misinformation | Pattern Cat 5 `Primary citation` snippet |
| output-integrity:14 | bare | LLM05 Improper Output Handling | re-key → LLM10:2026 Improper Output Handling | ADR-030 D4 documentation-only bundle prose: "`source_attribution` citations on emitted findings carry OWASP LLM10 only" |
| output-integrity:47 | bare | LLM05 Improper Output Handling | re-key → LLM10:2026 Improper Output Handling | Pattern Cat 1 (Client-Side Execution Sinks) `Primary citation` snippet |
| output-integrity:69 | bare | LLM05 Improper Output Handling | re-key → LLM10:2026 Improper Output Handling | Pattern Cat 2 (Server-Side Execution Sinks) `Primary citation` snippet |
| output-integrity:109 | bare | LLM05 Improper Output Handling | re-key → LLM10:2026 Improper Output Handling | Pattern Cat 3 (SSRF from LLM-Synthesized URLs) `Primary citation` snippet |
| output-integrity:131 | bare | LLM05 Improper Output Handling | re-key → LLM10:2026 Improper Output Handling | Pattern Cat 4 (Template/Expression Injection) `Primary citation` snippet |
| output-integrity:153 | bare | LLM05 Improper Output Handling | re-key → LLM10:2026 Improper Output Handling | Pattern Cat 5 (Path Traversal + Unsafe File Writes) `Primary citation` snippet |
| output-integrity:175 | bare | LLM08 Vector and Embedding Weaknesses | re-key → LLM09:2026 Vector and Embedding Weaknesses | Pattern Cat 6 (Vector/Search-DSL Injection, F-292 ADR-045) `Primary citation` — category name unchanged across σ, id moves 08→09 |
| output-integrity:175 | bare | LLM05 Improper Output Handling | re-key → LLM10:2026 Improper Output Handling | same line, `relationship: related` cross-anchor beside the LLM09 primary |
| output-integrity:213 | bare | LLM04 Data and Model Poisoning | re-key → LLM05:2026 Data and Model Poisoning | cross-agent carve prose "OWASP ASI06 … is the canonical anchor (NOT OWASP LLM05, which covers training-time data poisoning)" — σ collision-sensitive: LLM04→LLM05 applied in the SAME single pass as LLM05→LLM10 (sequential renames would have mapped it to LLM10) |
| output-integrity:267 | bare | LLM04 Data and Model Poisoning | re-key → LLM05:2026 Data and Model Poisoning | Related-references bullet, 1st of 2 on the line; same collision-sensitive pass |
| output-integrity:267 | bare | LLM04 Data and Model Poisoning | re-key → LLM05:2026 Data and Model Poisoning | same bullet, 2nd occurrence ("— LLM05 is training-time data poisoning") |
| tool-abuse:251 | bare | LLM03 Supply Chain | re-key → LLM04:2026 Supply Chain | Pattern Category Disambiguation heading "Category 6 (LLM04 Supply Chain) vs. Category 10"; σ collision-sensitive — LLM03→LLM04 and LLM06→LLM03 applied in one simultaneous pass in this file |
| tool-abuse:258 | bare | LLM03 Supply Chain | re-key → LLM04:2026 Supply Chain | co-emission contract prose "Category 10 cites LLM04 as `relationship: related`" |
| tool-abuse:258 | bare | LLM03 Supply Chain | re-key → LLM04:2026 Supply Chain | same line, "Category 6 cites LLM04 as `relationship: primary`" |

**Group 2 — breadcrumb lineage bares** (net-new, introduced by T009 — same class T008 records as its Group 3). ADR-048 D1 permits a one-release prose breadcrumb in the exact form `(2025: LLM<NN>)`; the `LLM<NN>` inside a breadcrumb is a deliberate **2025** lineage code, not a 2026 category id, so a bare-ref sweep matches it — dispositioned `retained-historical` so the W5 sweep gate (SC-002) does not flag it. Sunset is already tracked in the F-362b issue body (T026(a), architect MEDIUM-3). Only the 4 breadcrumbs landing in the 3 T009 Tier-A files are rows here; the other 9 landed in Tier B files and are listed in `.aod/results/senior-backend-engineer-T009.md` for T022.

| file:line | form | 2025 meaning | action | note |
|---|---|---|---|---|
| misinformation:12 | bare | LLM09 Misinformation | retained-historical | breadcrumb `OWASP LLM07:2026 Misinformation (2025: LLM09)` — Overview first-mention; drop at next minor |
| output-integrity:12 | bare | LLM05 Improper Output Handling | retained-historical | breadcrumb `OWASP LLM10:2026 Improper Output Handling (2025: LLM05)` — Overview first-mention; drop at next minor |
| tool-abuse:12 | bare | LLM03 Supply Chain | retained-historical | breadcrumb `OWASP LLM04:2026 Supply Chain (2025: LLM03)` — Overview first-mention; drop at next minor |
| tool-abuse:12 | bare | LLM06 Excessive Agency | retained-historical | breadcrumb `OWASP LLM03:2026 Excessive Agency (2025: LLM06)` — same Overview sentence, 2nd breadcrumb; drop at next minor |

**T009 lane arithmetic** — completion bar **21/21 met** (Group 1), matching the data-model §5 expected population exactly (output-integrity 11 + misinformation 7 + tool-abuse 3). Rows appended: **25** = 21 canonical bare + 4 breadcrumb lineage bares (net-new, `retained-historical`). Post-edit bare census across the 3 T009 ledger files is 25 and reconciles exactly: 21 + 4. Nine further breadcrumb bares were introduced in the other 12 skill-reference files (Tier B surface, T022) — enumerated with file:line in `.aod/results/senior-backend-engineer-T009.md`. T009 introduced **zero** net-new suffixed refs and **zero** FR-012c-class form bugs beyond the one recorded in the results file (`tachi-shared/references/finding-format-shared.md:228`, pre-edit `plain-2025` with a missing `OWASP ` prefix — counted in research's plain-2025 class, not in the 21).

### Tier A total

Both lanes combined: **41 occurrences / 8 files** (20 personas + 21 skill references, 5 files + 3 files). Any file discovered to mix `retained-historical` content with active refs is also handled at occurrence level (per contract), appended into whichever lane owns that file.

---

## Tier B — file-level census

Every remaining in-scope bare-ref file (i.e., outside the 8 Tier-A files), accounted at file level only. Columns per data-model §5 Tier B: `disposition class` ∈ `fully-re-keyed` \| `retained-historical` \| `mixed→escalated to Tier A` \| `carve-out→F-362b`.

| file | bare count | form classes present | disposition class |
|---|---|---|---|

_(populated during the Phase 3/4/5 repo-wide sweep, T022, using the verified command forms in quickstart.md §3)_

### Census accounting

Must reconcile at the **W5 sweep gate** (SC-002: zero undispositioned bare refs outside exclusions). Per the contract: "Σ Tier A + Tier B + carve-out must reconcile to 366 in-scope + 103 carve-out." Concretely: Tier A (41) + Tier B (Σ of the `bare count` column above) = **366 in-scope**; **+ 103 carve-out** (tracked separately, transferred to F-362b, not part of the 366) = **469 grand-total bare census** (research.md cross-reference: "366 in-scope (+103 carve-out = 469)").

Known `retained-historical` candidates (plan D7 — annotated in the ledger, never rewritten):
- `docs/architecture/README.md:57–69` — ADR-index prose citing immutable, already-shipped ADR records by their as-published 2025 id.
- Legacy-form-exercising fixtures — test fixtures whose bare-form content is the thing under test (rewriting the fixture would invalidate what it tests).

Carve-out files (103 bare refs, `examples/**`) are row-marked `carve-out→F-362b` in Tier B as they are encountered, and transferred to the F-362b ledger at issue-filing time — they are never dispositioned in F-362 proper.
