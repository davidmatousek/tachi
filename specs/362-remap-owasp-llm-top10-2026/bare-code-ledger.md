# Bare-Code Disposition Ledger (F-362)

Scaffolded at **T002** per [contracts/disposition-ledgers.md](contracts/disposition-ledgers.md) and [data-model.md](data-model.md) §5. Two-tier ledger (plan D8): **Tier A** (occurrence-level) covers the 41 concentrated bare refs across 8 files; **Tier B** (file-level) covers every remaining in-scope bare-ref file, accounting the 366-file in-scope census. Carve-out files (103 bare refs, `examples/**`) transfer to the F-362b ledger at issue-filing time.

**Completion bar** (target, per contract): Tier A 41/41 (union of both lanes) · Tier B census fully accounted (366 + 103).
**Current status (T022, Session D, 2026-08-10 — re-verified after in-wave absorption fix)**: Tier A **41/41 canonical COMPLETE** (T008 20/20 + T009 21/21; 55 rows total = 41 canonical + 7 FR-012c form-bug + 7 breadcrumb `retained-historical`) · Tier B census **COMPLETE**: 32 in-scope files (Σ 325) + Tier A (41) = **366/366 reconciled**; 13 carve-out files (Σ 103) row-marked `carve-out→F-362b`; grand total 469 = research.md cross-reference exact. A supplementary "net-new bare occurrences" table (§ below Tier B) accounts the 26 breadcrumbs + 5 FR-012c bare conversions + 7 T017 legacy-form test-literal occurrences introduced *by this feature* outside the pre-remap 366/103 baseline — these are HEAD-state content the W5 sweep gate (SC-002) must also see, and are fully dispositioned here.
**✅ SC-002 SATISFIED — zero undispositioned residue.** T022's initial sweep found 2 genuine gaps (`schemas/taxonomy/owasp.yaml:7` stale header comment; 12× "OWASP LLM Top 10 v2025" across 7 files). Both were fixed in-wave by senior-backend-engineer as a pre-authorized absorption (`.aod/results/senior-backend-engineer-T022-absorption.md`, 8 files / 13-line swaps, `2025`→`2026`/`v2025`→`v2026` only, comment-only on `owasp.yaml`) and independently re-verified by T022 (tester), not merely trusted: Form 2 re-run at working tree returns exactly 20 hits (33 − 13), all previously-dispositioned (17 retained-historical + 3 false-positive), zero new; Form 3 spot-check on `owasp.yaml:7` confirms `:2026`; taxonomy integrity suite re-run independently, 5 passed; `git diff --stat` confirms exactly the claimed 8 files / 13+13. See "Fixed in-wave (T022 absorption)" section (former "UNDISPOSITIONED" section, retitled) and `.aod/results/tester-T022.md` §9 for full re-verification evidence.

---

## Suffixed / prose / spaced-hyphenated sweep (quickstart.md §3 Forms 1-3)

Run repo-wide (in-scope pathspec: full `EXCL` array from quickstart §3 — `specs`, `docs/product/02_PRD`, `CONSUMER_GUIDE_TACHI.md`, `docs/architecture/02_ADRs`, `INSTITUTIONAL_KNOWLEDGE.md`, `tests/fixtures/init-baseline-tree`, `examples`, `CHANGELOG.md` all excluded). Sanity rule confirmed for all 3 forms against pre-remap `747805c` (non-zero hits each). Full per-hit evidence: `.aod/results/tester-T022.md`.

| Form | HEAD occurrences | Files | Disposition |
|---|---|---|---|
| 1 — suffixed `\bLLM(0[1-9]\|10):2025` | 52 | 7 | 4 files / 47 occ `retained-historical` (`docs/architecture/01_system_design/README.md` 6, `docs/architecture/README.md` 9, `docs/product/05_User_Stories/README.md` 18, `docs/product/06_OKRs/README.md` 14 — historical narrative); 3 files / 5 occ `documented-current-behavior` (`scripts/generate-threats-sarif.py:390` ×1, `scripts/extract-report-data.py:1188` ×1, `tests/scripts/test_owasp_2026_contract.py:105-107` ×3). **Zero undispositioned.** |
| 2 — prose `LLM Top 10 (for LLM Applications )?2025\|llm top 10.*2025` (case-insensitive) | **20** (re-verified post-fix; was 33) | 6 | 5 files / 17 occ `retained-historical` (`.claude/skills/tachi-shared/references/attack-chain-patterns-shared.md:15` "v2025" provenance ×1, `docs/architecture/01_system_design/README.md` ×5, `docs/architecture/README.md` ×1, `docs/product/05_User_Stories/README.md` ×5, `docs/product/06_OKRs/README.md` ×5); 1 file / 3 occ **false-positive** (`docs/architecture/00_Tech_Stack/README.md:140,174,195` — regex's greedy `.*` spans past the already-correct "LLM Top 10 2026" to an unrelated "2025" later in the same long line, e.g. "October 2025 agent techniques" / "CWE Top 25 2025"; verified via precise python match extraction — zero genuine residue in this file). **Zero undispositioned** (was 8 files / 13 occ UNDISPOSITIONED — fixed in-wave, see "Fixed in-wave" section below). |
| 3 — spaced-prose / hyphenated `LLM[[:space:]]+2025\|OWASP-LLM-2025` | 0 | 0 | Clean at HEAD (pre-remap sanity: 14 hits — 4 outside `owasp.yaml` [scope.md:24, README.md:24, OWASP_COVERAGE.md:8,20, all T021-fixed] + 10 inside `owasp.yaml`'s `full_id` fields [T005-fixed]; `owasp.yaml:7`'s header-comment `:2025`→`:2026` fix confirmed by re-run — spot-checked directly, not merely inferred). **PASS, zero residue.** |

Cross-check: Form 1's 4 retained-historical files are the SAME 4 files contributing Form 2's `01_system_design`/`README.md`/`05_User_Stories`/`06_OKRs` retained-historical rows (both forms hit the same historical-narrative prose via different sub-strings on the same lines — not double-counted as separate defects, each form's hits are tracked and dispositioned independently since they are literally different substrings).

**Unscoped-variant supplementary check** (`git grep -niE 'llm top 10.*v2025'`, no EXCL pathspec, run to confirm the fix didn't merely dodge the quickstart pathspec): 68 raw hits repo-wide. Filtered to outside `specs/**` (always-excluded feature-workspace self-reference, including this ledger's own 4 hits quoting the phrase as evidence, and ~15 other historical features' specs directories, e.g. `specs/082-threat-agent-skill/**` — different, older features, correctly out of scope): 34 hits, all falling into already-established exclusion classes — **no new class needed, no new gap**: `docs/product/02_PRD/**` (12 occ, 4 files — D7 archive, quickstart-EXCL'd), `tests/fixtures/init-baseline-tree/**` (5 occ, 1 file — the `#345`/T023 fixture-mirror surface, quickstart-EXCL'd), `examples/**` (2 occ, 2 files — `carve-out→F-362b`, quickstart-EXCL'd), `.claude/skills/tachi-shared/references/attack-chain-patterns-shared.md` (1 occ) + `docs/architecture/01_system_design/README.md` (5 occ) — both already counted and dispositioned `retained-historical` in the Form-2 EXCL-scoped 20-hit row directly above (not new).

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

Bare counts below are the **pre-remap baseline** (measured at `747805c`, same convention as Tier A) — the denominator the 366/103 completion bar reconciles against. Where post-remap (HEAD) content diverges from this baseline (form-bug conversions, breadcrumbs), the delta is accounted separately in "Net-new bare occurrences" below, never blended into this table (mixing baselines would break the arithmetic both sections are individually exact against).

| file | bare count | form classes present | disposition class |
|---|---|---|---|
| `schemas/taxonomy/crosswalk.yaml` | 75 | bare | **fully-re-keyed** — 74 `source.id` edges via T006 single-simultaneous-pass σ-permutation, human-dispositioned 74/74 in `crosswalk-disposition-ledger.md` (separate ledger, owns this file's occurrence-level trail — not duplicated here) + 1 **retained-historical** (`:4245`, "Batch 9 (T024)" composition comment "OWASP LLM05/08 ↔ ATLAS cross-mappings" — describes that batch's 2025-era composition as-authored; D7 class, same genre as the file's own `:10-15` "Edit lineage" header) |
| `docs/product/06_OKRs/README.md` | 31 | bare+suffixed+prose | **retained-historical** — append-only "Last Updated" per-feature delivery log; every hit verified individually (python precise-match extraction) as narrating a past feature's as-shipped content under the then-current 2025 numbering (e.g. F-082's "Source attribution: …OWASP LLM Top 10 2025…", F-5/ADR-034's "OWASP LLM Top 10:2025 framework" 10/10-closure narrative). Same genre as `docs/architecture/README.md`'s ADR index. |
| `tests/scripts/fixtures/coverage_attestation/pagination_smoke/findings.yaml` | 25 | bare | **retained-historical** — T012-dispositioned: deterministic fixed-seed (`rng.choice`, seed 194) generated artifact; ids are positional, carry zero classification semantics; hand-editing breaks the byte-determinism contract with its generator |
| `docs/product/05_User_Stories/README.md` | 23 | bare+suffixed+prose | **retained-historical** — same genre/verification as `06_OKRs/README.md` above |
| `docs/architecture/00_Tech_Stack/README.md` | 21 | bare+suffixed+prose | **fully-re-keyed** — T021 ran a full sweep including bare (non-suffixed) codes on this file specifically because it is a "living," architect-owned, Last-Updated doc (not a point-in-time snapshot); count unchanged pre/post (pure content substitution) |
| `tests/scripts/test_coverage_attestation.py` | 16 | bare | **fully-re-keyed** — T012 (LLM05→LLM10 ×8, LLM06→LLM03 ×4, LLM07→LLM08 ×4) |
| `docs/architecture/01_system_design/README.md` | 16 | bare (all inside named `### Feature NNN` historical sections: 201/206/219) | **retained-historical** — D7 pre-declared "at the time of planning approval" per-feature archive (architect MEDIUM-2/T023 ruling); T021's one active edit at `:130` is a *suffixed*-form occurrence (`OWASP LLM Top 10:2025→2026`), disjoint from this file's 16 bare occurrences — not a "mixed" escalation case |
| `schemas/taxonomy/owasp.yaml` | 12 | bare (10× `id:` field + 2× header-comment range mention) | **fully-re-keyed**. The 10 `id: LLM0N` record fields are untouched-by-design (ADR-027: `id` is edition-invariant); the header `:7` range mention "LLM01-LLM10" was always bare-correct — its co-located "…2025…" label was the defect, fixed in-wave (see "Fixed in-wave (T022 absorption)" below), bare-census count unaffected (13 before/after — comment-only edit) |
| `docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md` | 12 | bare+suffixed+prose | **fully-re-keyed** — T021 §2/§3/§12/§13 corrections (10-row category table + cross-reference fixes); 1 pre-existing v2025 PDF URL deliberately kept `(superseded)` per T021 (real historical link, not a bare-code concern) |
| `tests/scripts/test_llm10_unbounded_consumption_enrichment.py` | 11 | bare+suffixed | **fully-re-keyed** — T012 (35/35 refs; file/class/method names intentionally frozen on the `llm10` label per instruction — label-class exception, zero functional impact, all human-readable assertion content re-keyed) |
| `tests/scripts/generate_pagination_fixture.py` | 11 | bare | **retained-historical** — T012-dispositioned: `OWASP_IDS` is the complete LLM01-LLM10 set, σ-invariant as a *pool*; `rng.choice` selects by index so reordering would desync the committed fixture; nothing-to-do |
| `scripts/generate-threats-sarif.py` | 10 | bare+suffixed | **fully-re-keyed** — T015 (2023/2025-era rule prose at `:259-260,:271` corrected to 2026 category associations, verified semantically correct: LLM01=prompt injection, LLM05=data poisoning, LLM07=misinformation, LLM10=improper output handling); the file's separate suffixed Form-1 hit at `:390` (docstring) is `documented-current-behavior`, tracked in the suffixed-sweep section, not double-counted here |
| `schemas/taxonomy/README.md` | 10 | bare | **fully-re-keyed** — T021, including a post-delivery correction (orchestrator fact-check on `crosswalk.yaml` edition state; 3 lines changed, 3 confirmed already-correct) |
| `docs/guides/DEVELOPER_GUIDE_TACHI.md` | 10 | bare+suffixed+prose | **fully-re-keyed** — T021 (Appendix A bare-code category list rewritten with σ-map + FR-002 alias, all at `:1815`) |
| `docs/architecture/README.md` | 9 | bare+suffixed+prose | **retained-historical** — D7 pre-declared (plan D7 / data-model §5): ADR-index prose (`:57-69`) citing immutable, already-shipped ADR records (ADR-030/031/034/045) by their as-published 2025 id |
| `scripts/generate-risk-scores-sarif.py` | 5 | bare+suffixed | **fully-re-keyed** — T015 replaced the hardcoded per-id taxa block with catalog-derived `TAXONOMIES`/`supported_taxonomies()` (FR-012a); 2 residual bare hits at `:488` are a generic docstring range mention ("yields LLM01..LLM10"), edition-agnostic, correctly current |
| `tests/scripts/test_catalog_drift_guard.py` | 3 | bare | **verify-only / fully-re-keyed-context** — T012: synthetic hand-built records (`:51,:204`→shifted to `:53,:206`), edition-agnostic, T020 territory; T020 added 2 more edition-agnostic bare mentions in its own new docstring/comment (`:297,:313`, "LLM01-LLM10" range descriptions) — all 4 net-new hits verified generic/correctly-current, not year-specific claims |
| `tests/scripts/fixtures/misinformation/valid_mi_finding.yaml` | 3 | bare | **fully-re-keyed** — T012 |
| `tests/scripts/fixtures/coverage_attestation/one_primary_attribution.yaml` | 3 | bare | **fully-re-keyed** — T012 |
| `tests/scripts/fixtures/coverage_attestation/multi_mixed_attribution.yaml` | 3 | bare | **fully-re-keyed** — T012 |
| `tests/scripts/test_output_integrity.py` | 2 | bare | **fully-re-keyed** — T012 |
| `tests/scripts/fixtures/output_integrity/valid_oi_finding.yaml` | 2 | bare+suffixed | **fully-re-keyed** — T012 |
| `schemas/finding.yaml` | 2 | suffixed (example blocks) | **fully-re-keyed** — T014 (`:330-332` source_attribution examples, LLM05→LLM10 per σ) |
| `docs/standards/OWASP_COVERAGE.md` | 2 | bare | **fully-re-keyed** — T019 [MANUAL-ONLY canon]; net-new 10-row per-category verdict table + residual notes substantially expanded this file's bare content post-edit (2→21), all verified current/correct 2026 dispositions |
| `tests/scripts/test_source_attribution.py` | 1 | bare | **fully-re-keyed** — T012 |
| `tests/scripts/test_backward_compatibility.py` | 1 | bare (docstring, `:19`) | **fully-re-keyed** — T012 |
| `tests/scripts/fixtures/web_api_coverage_attestation/stream_1_f_a3_wiring/agent_autonomy_wired.md` | 1 | bare | **fully-re-keyed** — T012 (LLM06→LLM03) |
| `tests/scripts/fixtures/tool_abuse_enrichment/valid_category_10_mcp_to_mcp_finding.yaml` | 1 | bare+suffixed | **fully-re-keyed** — T012 |
| `tests/scripts/fixtures/source_attribution/valid_multi_record.md` | 1 | bare | **fully-re-keyed** — T012 |
| `tests/scripts/fixtures/source_attribution/invalid_relationship.md` | 1 | bare | **fully-re-keyed** — T012 |
| `tests/scripts/fixtures/output_integrity/invalid_attribution_finding.yaml` | 1 | bare+suffixed | **fully-re-keyed** — T012 |
| `tests/scripts/fixtures/exec_arch/agentic_app/compensating-controls.md` | 1 | bare | **already-2026-correct** — T012: σ(01)=01 hold, no edit required |

**Tier B subtotal: 32 files, Σ = 325.** Reconciliation: Tier A (41) + Tier B (325) = **366 in-scope ✓** (exact match to research.md / contract target, independently re-verified by T022 via `git grep -oP '\bLLM(0[1-9]|10)\b(?!:)' 747805c -- <protected-excl, examples-excl>` = 366 across the same 40 files research measured — 8 Tier A + 32 Tier B).

### Carve-out — `examples/**` (103 bare refs, 13 files, `carve-out→F-362b`)

Re-verified byte-identical pre-remap (`747805c`) vs HEAD — F-362 has not touched `examples/**`, confirming the carve-out boundary held throughout the feature:

| file | bare count | disposition class |
|---|---|---|
| `examples/agentic-app/sample-report/threats.md` | 17 | `carve-out→F-362b` |
| `examples/agentic-app/sample-report/risk-scores.sarif` | 15 | `carve-out→F-362b` |
| `examples/agentic-app/sample-report/compensating-controls.sarif` | 15 | `carve-out→F-362b` |
| `examples/agentic-app/threats.md` | 14 | `carve-out→F-362b` |
| `examples/agentic-app/sample-report/threats.sarif` | 10 | `carve-out→F-362b` |
| `examples/mermaid-agentic-app/threats.md` | 9 | `carve-out→F-362b` |
| `examples/maestro-reference/threats.md` | 6 | `carve-out→F-362b` |
| `examples/agentic-app/sample-report/threat-report.md` | 6 | `carve-out→F-362b` |
| `examples/mermaid-agentic-app/threat-report.md` | 4 | `carve-out→F-362b` |
| `examples/agentic-app/sample-report/risk-scores.md` | 3 | `carve-out→F-362b` |
| `examples/agentic-app/sample-report/threat-baseball-card-spec.md` | 2 | `carve-out→F-362b` |
| `examples/agentic-app/sample-report/threat-risk-funnel-spec.md` | 1 | `carve-out→F-362b` |
| `examples/agentic-app/sample-report/compensating-controls.md` | 1 | `carve-out→F-362b` |

**Carve-out subtotal: 13 files, Σ = 103 ✓** (exact match, both pre-remap and HEAD).

### Grand-total reconciliation

**366 in-scope (Tier A 41 + Tier B 325) + 103 carve-out = 469 grand-total bare census** — exact match to research.md's "366 in-scope (+103 carve-out = 469)" and to T002's scaffold-time cross-reference. ✓ RECONCILED.

### Net-new bare occurrences (introduced by this feature, outside the 366/103 pre-remap baseline)

The pre-remap baseline necessarily excludes content that did not exist in bare form until the remap edits created it (breadcrumbs, and suffixed→bare form-bug fixes). These ARE part of the HEAD-state sweep gate (SC-002 applies to current content, not just the historical baseline) and are dispositioned here, not blended into the 366/325 arithmetic above.

**Breadcrumbs — ADR-048 D1 exact form `(2025: LLM<NN>)`, all `retained-historical`, one-release sunset (F-362b issue body, T026(a)):**

Independently re-verified by T022 via `git grep -oP '\(2025:\s*LLM(0[1-9]|10)\)'` — **26 total** (25 landed by T008/T009/T011 as previously enumerated in their own results files + 1 not previously counted: `tests/scripts/test_owasp_2026_contract.py:142`, T017's `test_breadcrumb_suffixed_string_is_passthrough_not_normalized` literal — itself `documented-current-behavior`, see below, counted here only because it happens to also match the breadcrumb regex):

| Source lane | Count | Files |
|---|---|---|
| T008 (Tier A, already ledgered as Group 3) | 3 | `misinformation.md:25`, `model-theft.md:33`, `output-integrity.md:25` |
| T008 (Tier B, net-new for T022) | 3 | `agent-autonomy.md:25,:40`, `denial-of-service.md:37` |
| T009 (Tier A, already ledgered as Group 2) | 4 | `misinformation:12`, `output-integrity:12`, `tool-abuse:12` ×2 |
| T009 (Tier B, net-new for T022) | 9 | `tachi-agent-autonomy…:81,:133`, `tachi-data-poisoning…:65,:211`, `tachi-denial-of-service…:158`, `tachi-misinformation/README.md:12`, `tachi-model-theft…:115,:143`, `tachi-output-integrity/README.md:11` |
| T011 (Tier B, net-new for T022) | 6 | `agents/ai/data-poisoning.md:154,155,156`, `model-theft.md:171,172`, `prompt-injection.md:153` |
| T017 (Tier B, net-new for T022, test literal) | 1 | `tests/scripts/test_owasp_2026_contract.py:142` |
| **Total** | **26** | — |

**FR-012c bare conversions outside Tier A** (suffixed `id: LLMNN:2025` → bare `id: LLMNN`, form-bug fix per ADR-028; not part of the 366 baseline since pre-remap these were suffixed, not bare):

| File | Occurrences | Disposition |
|---|---|---|
| `.claude/agents/tachi/denial-of-service.md:134` | 1 | `fully-re-keyed` (T008, 8th FR-012c site, `id: LLM06`) |
| `tests/scripts/fixtures/web_api_coverage_attestation/stream_1_f_a3_wiring/prompt_injection_wired.md:36` | 2 | `fully-re-keyed` (T012, `id: LLM01`) |
| `tests/scripts/fixtures/web_api_coverage_attestation/stream_1_f_a3_wiring/denial_of_service_wired.md:36` | 2 | `fully-re-keyed` (T012, `id: LLM06`) |

**Legacy-form-exercising test literals** (`documented-current-behavior` — the bare/suffixed 2025-form content IS the thing under test; rewriting would invalidate the test):

| File | Occurrences | Note |
|---|---|---|
| `tests/scripts/test_owasp_2026_contract.py:103,142` (bare, 4) + `:105,106,107` (suffixed, 3) | 7 | T017's `normalize_owasp_id` D2 covering matrix deliberately pins BOTH-edition-identical normalization (2025-token AND 2026-token parametrize cases) and the breadcrumb-passthrough behavior — the exact function documented at `generate-threats-sarif.py:390` below |
| `scripts/generate-threats-sarif.py:390` (suffixed, 1) | 1 | `normalize_owasp_id` docstring example `"OWASP LLM01:2025" → "LLM-01"` — function is genuinely year-agnostic (verified: T017 tests both editions), so the example is a true, current illustration of real behavior |
| `scripts/extract-report-data.py:1188` (suffixed, 1) | 1 | T016's new stderr-warning docstring: "…contaminated id that no longer parses, such as \`\`LLM05:2025\`\` against…" — illustrative example of a STALE id the warning is designed to flag; the "2025" is deliberately shown as the wrong/legacy shape |

Known `retained-historical` candidates (plan D7 — annotated in the ledger, never rewritten):
- `docs/architecture/README.md:57–69` — ADR-index prose citing immutable, already-shipped ADR records by their as-published 2025 id.
- Legacy-form-exercising fixtures — test fixtures whose bare-form content is the thing under test (rewriting the fixture would invalidate what it tests).

### Fixed in-wave (T022 absorption) — formerly "UNDISPOSITIONED — real gaps"

Both genuine gaps T022 found did **not** fit `fully-re-keyed`, `retained-historical`, or `carve-out` at discovery time — they were live, in-scope content that was simply still wrong. Rather than block the gate, they were absorbed as a pre-authorized fix by senior-backend-engineer in the same wave (`.aod/results/senior-backend-engineer-T022-absorption.md`) and independently re-verified by T022 (tester) — not merely trusted on the implementer's self-report. Both now carry `disposition class: fully-re-keyed`.

1. **`schemas/taxonomy/owasp.yaml:7`** — file header "Composition per FR-020" comment block: `#   - LLM Top 10:2025 (10 items: LLM01-LLM10)` → `#   - LLM Top 10:2026 (10 items: LLM01-LLM10)`. The sibling line `:6` for the Agentic list already correctly read `Top 10 for Agentic Applications:2026`; T005's catalog-surgery task was explicitly scoped to lines `439-517`, so the header block sat outside that range and was never in anyone's stated task scope until this absorption. **Fixed**: 1 line, comment-only. **Re-verified by T022**: `sed`-read of `:1-10` confirms `:2026`; `git grep -nE 'LLM[[:space:]]+2025|OWASP-LLM-2025' -- schemas/taxonomy/owasp.yaml` returns 0 hits; bare-census count on this file unchanged at 13 (comment-only edit, no field touched); `python -m pytest tests/schemas/test_taxonomy_integrity.py -q` independently re-run by tester, 5 passed.
2. **12 occurrences of the literal phrase "OWASP LLM Top 10 v2025"** across 7 files → `v2026`, same 7 files. Confirmed genuine at discovery (all sat in files whose OTHER LLM content was already correctly 2026-keyed, proving T010/T011 touched the files but missed this specific edition-label phrase — it matches neither task's own verification regex). T011's own results file had explicitly flagged the adapter-side instances as "out of scope for T011 — flagging so the T022 sweep… picks them up deliberately."

   | File | Line(s) | Occurrences | Fixed? |
   |---|---|---|---|
   | `adapters/claude-code/agents/orchestrator.md` | 235, 641 | 2 | ✓ re-verified 0 hits |
   | `adapters/copilot/agents/orchestrator.agent.md` | 168 | 1 | ✓ re-verified 0 hits |
   | `adapters/copilot/instructions/tachi-orchestrator-context.instructions.md` | 151, 579 | 2 | ✓ re-verified 0 hits |
   | `adapters/cursor/rules/orchestrator.mdc` | 221, 659 | 2 | ✓ re-verified 0 hits |
   | `adapters/generic/prompts/00-orchestrator.md` | 223, 661 | 2 | ✓ re-verified 0 hits |
   | `agents/ai/README.md` | 24 | 1 | ✓ re-verified 0 hits |
   | `agents/orchestrator.md` | 224, 662 | 2 | ✓ re-verified 0 hits |

   **Re-verified by T022**: `git grep -n 'OWASP LLM Top 10 v2025' -- adapters agents` returns 0 hits (was 12); Form 2 prose sweep at working tree returns exactly 20 hits (33 − 13), matching the pre-computed expectation exactly; `git diff --stat` on the 8 touched files shows exactly 13 insertions / 13 deletions, matching the claimed scope with no bleed into other content on the same lines (each edit swapped only the `v2025`→`v2026` token).

**Unscoped-variant check** (coordinator-requested): confirmed no other instance of "OWASP LLM Top 10 v2025" (or the broader `llm top 10.*v2025` pattern) survives outside already-established exclusion classes — see the "Unscoped-variant supplementary check" note under the sweep-forms table above.

Carve-out files (103 bare refs, `examples/**`) are row-marked `carve-out→F-362b` in Tier B as they are encountered, and transferred to the F-362b ledger at issue-filing time — they are never dispositioned in F-362 proper.
