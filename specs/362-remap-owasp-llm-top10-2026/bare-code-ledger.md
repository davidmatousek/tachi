# Bare-Code Disposition Ledger (F-362)

Scaffolded at **T002** per [contracts/disposition-ledgers.md](contracts/disposition-ledgers.md) and [data-model.md](data-model.md) §5. Two-tier ledger (plan D8): **Tier A** (occurrence-level) covers the 41 concentrated bare refs across 8 files; **Tier B** (file-level) covers every remaining in-scope bare-ref file, accounting the 366-file in-scope census. Carve-out files (103 bare refs, `examples/**`) transfer to the F-362b ledger at issue-filing time.

**Completion bar** (target, per contract): Tier A 41/41 (union of both lanes) · Tier B census fully accounted (366 + 103).
**Current status**: Tier A 0/41 (both lanes empty — **scaffold only, T002**) · Tier B census not yet populated — **scaffold only (T002)**.

---

## Tier A — occurrence-level (41 concentrated bare refs, 8 files)

**Lane rule (architect MEDIUM-3 / team-lead F4)**: Tier A is pre-partitioned below into two independently-owned lane sections, in this order: personas (T008), then skill references (T009). Each owning task appends rows **only** within its own section. Nothing row-level is pre-seeded here — only the expected populations from data-model §5, stated as the completion target each lane's task fills toward.

### Tier A — personas (T008)

append-only within your own section — never write into the other lane (architect MEDIUM-3 / team-lead F4).

Expected population: **20 occurrences / 5 files** — misinformation (7), output-integrity (5), data-poisoning (3), model-theft (3), prompt-injection (2).

| file:line | form | 2025 meaning | action | note |
|---|---|---|---|---|

_(T008 appends its rows here, in this table, per data-model §5 Tier A columns: `action` ∈ `re-key → LLMNN:2026 context` \| `retained-historical` \| `already-2026-correct`.)_

### Tier A — skill references (T009)

append-only within your own section — never write into the other lane (architect MEDIUM-3 / team-lead F4).

Expected population: **21 occurrences / 3 files** — output-integrity (11), misinformation (7), tool-abuse (3).

| file:line | form | 2025 meaning | action | note |
|---|---|---|---|---|

_(T009 appends its rows here, in this table, per data-model §5 Tier A columns: `action` ∈ `re-key → LLMNN:2026 context` \| `retained-historical` \| `already-2026-correct`.)_

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
