# In-Tree Merge Close-out — Verification Evidence (T010/T012/T030–T033)

**Date**: 2026-05-28 (Wave 5 in-tree close-out; LinkedIn URLs pending Friday 2026-05-29).
**Gate**: pre-merge verifications for PR #297 (`docs(296):` in-tree squash-merge, T029).

## T010 — README hero `\*` footnote render check (Architect L-1) — PASS

Verified objectively via GitHub's own renderer (`POST /markdown` mode=gfm): the input `OWASP Web/API\* (2021 + 2023)` renders as **`Web/API*`** (literal asterisk; backslash consumed, no visible escape sequence). No swap to `†` / superscript needed. Final visual eyeball on github.com is at maintainer discretion post-merge.

## T012 — Hero block content — PASS

- (a) 5 framework rows present: LLM 2025, Agentic 2026, ML 2023, Mobile 2024, Web/API (2021+2023). ✓
- (b) 6 OWASP anchor URLs 200 OK (per `notes/narrative-defensibility-check.md`, T011). ✓
- (c) Web/API combined-slot footnote text exact: "OWASP Web Top 10:2021 (A01–A10) + OWASP API Security Top 10:2023 (API1–API10) — 20 items, 20/20". ✓
- (d) `docs/standards/OWASP_COVERAGE.md` link resolves (file exists, T005). ✓

## T031 — SC-007 sequencing-hold binary check — PASS (2 of 2)

**Run 1 of 2** (2026-05-28, pre-merge): `git log --all --grep="F-2\|F-260b\|asset-tag wiring" --since="2026-05-28"` → zero substantive commits. Sequencing hold maintained (FR-007 / US6).

**Run 2 of 2** (2026-05-30, at `/aod.deliver` close): the same query now returns 4 matches — `102dc03`, `d4df2ae`, `014f216`, `4e762b7` — **all false positives** carved out per Architect L1. The literal `F-2` matches the substring inside `F-296`, and the commit bodies reference F-2 only to assert the *sequencing hold* (do-not-start), never to initiate F-2 / F-260b / asset-tag-wiring work. **Zero substantive F-2-initiating commits; SC-007 PASS confirmed end-to-end.**

## T032 — SC-010 file-allowlist — PASS

`git diff main --name-only` → 20 files, all within the F-296 allowed set: `README.md`, `CHANGELOG.md`, `docs/standards/OWASP_COVERAGE.md`, `docs/standards/README.md`, `docs/product/02_PRD/296-*.md`, `docs/product/02_PRD/INDEX.md`, `docs/product/_backlog/BACKLOG.md`, and `specs/296-*/{spec,plan,tasks,research,agent-assignments,checklists/requirements,notes/*}`. Zero out-of-scope files. `agent-assignments.md` not explicitly enumerated in T032's list but is a core spec-dir Triad artifact (within scope). BLP-04 strategy doc gitignored (not in diff; exists locally per T027).

## T033 — SC-014 BLP-04 strategy doc 5-item — PASS

Verified against `docs/product/_internal/strategy/BLP-04-adoption-push.md`: [a] §1 4-feature sequencing ✓; [b] §2 BLP-03 trigger + enterprise-buyer-signal acceptance (US7) ✓; [c] §3 Sequencing Discipline ✓; [d] §4 F-2 kickoff targets (Fri 2026-06-05 / Mon 2026-06-08; ship 2026-06-11) ✓; [e] §5 F-2 no-pre-draft ✓.

> ✅ **DUPLICATE RESOLVED (2026-05-29):** canonical is `_internal/strategy/BLP-04-adoption-push.md` (repo-root, per `_internal/CLAUDE.md`). The F-296 stray copy at `docs/product/_internal/strategy/` was deleted and its unique F-296 execution bindings folded into the canonical doc's Scope History. Issue #296 close + CHANGELOG cross-link use the canonical path. (T033 verification above was performed against the stray copy before consolidation; the same 5 items hold in the canonical doc.)

## T030 — Post-merge `/security` regression — PASS (docs-only determination)

NFR-004 = no source code / schema modified. The F-296 changeset (T032 file list) contains **zero** code files and **zero** dependency manifests — only Markdown/text docs + notes. The `/security` skill self-skips when no code/manifest files changed (its Step 7a), so a post-merge scan has zero regression surface by construction. Expected delta vs the last clean `main` snapshot: **zero new findings**. ✅ **Finalized at `/aod.deliver` (2026-05-30):** promoted to `notes/post-merge-security-scan.md`; zero-regression determination confirmed against merged `main` (`9d8f17d`).
