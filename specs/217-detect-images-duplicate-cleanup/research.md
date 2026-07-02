# Research Summary: Detect-Images Duplicate Cleanup (F-217)

**Date**: 2026-07-01
**PRD**: `docs/product/02_PRD/217-detect-images-duplicate-cleanup-2026-07-01.md` (Approved v1.1)
**Method**: 4 parallel research tracks — Knowledge Base, Codebase (Explore), Architecture (Explore), Web (web-researcher)

## Knowledge Base Findings

Source: `docs/INSTITUTIONAL_KNOWLEDGE.md` (20 entries; single-file KB). No KB entry exists for #215/PR #216 itself (CHANGELOG-only, `672b7fb`).

- **Entry 15 (F-185)** — byte-identity suite was once left silently red on main; record LITERAL pre-state pytest totals before touching baseline-coupled files (`docs/INSTITUTIONAL_KNOWLEDGE.md:551`)
- **Entry 19 (F-329)** — byte-identity suite is wired into NO CI workflow; render-coupled file changes can trip `tachi-catalog-drift.yml` (`:617`) — extractor changes are NOT render-coupled, but verify at build
- **Entry 2 (F-250)** — file DROPS are FAIL in `test_personalized_tree_bytes_match_baseline` — that fixture covers the init template tree only, NOT `examples/`; US-2 deletions are outside it (verified: CI pytest gate runs only init.sh/template-hardening suites)
- **Entry 13 (F-186)** — wasting-asset rule: before destructive/removal edits, secure the recovery source. Satisfied here by design: deletion requires a byte-identical survivor + git history retains the deleted files
- **Entry 17 (F-183)** — opt-in/side-effecting features: run the MANUAL-ONLY live validation AT deliver; pre-decide disposition of first-run findings
- **Entry 1 (F-248)** — scope tests to the invariant, not the whole tree (byte-comparison fixtures drift on file add/remove)
- **Memory: gated harness clones committed HEAD** — commit before running the gated pytest subset (`tachi-pytest.yml` 15-module subset is the real gate)
- **Opt-in precedent**: Entry 17's `inject_sentinel_rot` workflow input and `/aod.update --dry-run` insurance are the closest opt-in-destructive precedents; no dedicated KB entry on opt-in flags

## Codebase Analysis

`scripts/extract-report-data.py`:
- `_file_format(path)` magic-byte probe at **L1449–1460** (`png` / `jpeg` / `None`); `_IMAGE_FORMAT_TO_EXT` at **L1446**
- `detect_images(target_dir, template_dir)` **L1463–1530**; 6 stems (L1488–1495); candidate collection excludes zero-byte files (L1498–1504); **self-consistent/best-match branch L1506–1510** (pre-existing pairs — US-2's primary case, deletion location #1, mislabeled file silently ignored today); **recovery branch `if chosen is None:` L1512–1525** (writes corrected sibling via `shutil.copyfile` L1523, stderr mismatch note, deletion location #2)
- Imports L14–23: `shutil` present; **`filecmp` absent — must be added** (stdlib, code-economy rung 3)
- `build_parser()` **L2020–2044**: long-form kebab flags, sentence-fragment help; idiomatic addition is `action="store_true"`
- Single production call site **L2164**: `detect_images(target_dir, template_dir)` — two positional args

Tests:
- `tests/scripts/test_extract_report_data.py`: `PNG_MAGIC`/`JPEG_MAGIC` L28–29; `_write_minimal_png/_jpeg` L49–59; **`run_extract` L62–89 has NO extra-flags parameter — harness needs an `extra_args` extension** for cleanup tests; `_build_byte_probe_fixture` L232–239; existing #215 coverage: recovery-path L242, self-consistent-preference L284, clean-jpeg L316 — all must stay green
- `tests/scripts/test_extractor_contract_fixes.py:200`: direct `detect_images(target_dir, template_dir)` two-positional-arg call → **flag must thread as defaulted kwarg** (`cleanup: bool = False`); `test_existing_image_flags_unchanged` at :211

US-2 target `examples/agentic-app/test-output/2026-04-19T03-20-30/`: **confirmed 6 pairs**, every `.jpg` has PNG magic and is byte-identical (`cmp`) to its `.png` sibling (~6.75 MB reclaimable); dir also holds `security-report.pdf` + `.baseline`

Callers/consumers (complete): production call site L2164; direct test call :200; subprocess tests via `run_extract`; runtime invocation only in `.claude/agents/tachi/report-assembler.md` L158–163 (must NOT auto-pass the flag per OQ-1). No Makefile target; **no CI workflow runs the extractor tests** (tachi-pytest.yml paths L84–107 = init/template suites only) — confirms R-1 downgrade.

US-3 doc surface: `.claude/skills/tachi-report-assembly/references/typst-artifacts.md` (image validation L30–35, legacy extraction L112–114) is the primary home; `typst-template-contract.md` L92–103 documents image-path resolution. `README.md` and `DEVELOPER_GUIDE_TACHI.md` do NOT reference the script — no root-guide edits needed.

## Architecture Constraints

- **ADR-021** (SOURCE_DATE_EPOCH deterministic PDF): extraction is byte-deterministic for identical inputs — the basis of US-2's **path-invariance proof** (the `.png` is already selected with the `.jpg` present, so deletion cannot change `report-data.typ`)
- **ADR-017**: stdlib-only constraint for extraction — `filecmp` complies, no new dependencies
- **ADR-016/ADR-014**: best-effort/graceful-degradation posture for images — aligns with "cleanup failure never fails extraction"
- **ADR-008:74**: "Opt-in is appropriate for experimental or high-risk steps" — directional precedent for a positive opt-in flag on a destructive operation (ADR-008/011 govern `/aod.build` flags, so directional, not binding)
- **Constitution Principle III (Backward Compatibility, NON-NEGOTIABLE)**: "Migration … is opt-in, never forced" — constitutional anchor for the safe default
- **Constitution Principle VI (Testing Excellence)**: 80% unit minimum, test-first for core features
- **Caveat**: no constitutional principle governs destructive *filesystem* operations (Principle IX's destructive clause is git-scoped) — the deletion gate rests on ADR-008 reasoning + Principle III; do not over-cite
- Report-assembly contract that must survive: zero-byte image validation (typst-artifacts.md L30–36) and template-relative image-path emission (typst-template-contract.md L92–101); after cleanup the emitted path must be the correctly-labeled survivor (it already is)
- No ADR needed for this feature (PR-level change to `detect_images`; #215/#216 had none)

## Industry Research

- **CLI destructive-op conventions** (clig.dev): explicit opt-in for destructive behavior is standard; `--dry-run` pairing is the common baseline. F-217's no-flag default IS the safe preview (lists nothing, deletes nothing, warning fires only on recovery runs) — a `--dry-run` companion is NOT in PRD scope (revisit with OQ-1 on adopter signal)
- **`filecmp.cmp(shallow=False)` gotcha**: results are cached keyed on both files' stat signatures (size/mtime); `filecmp.clear_cache()` exists. Risk is same-pair re-comparison after sub-mtime-resolution content change within one process — not this feature's pattern (each pair compared once per run). Plan may add `clear_cache()` defensively at cleanup start — cheap and removes the class
- **Verify-then-delete ordering + TOCTOU**: verify byte-identity, then delete, accepting the small race window as appropriate for a local single-user CLI; per-file try/except with stderr logging is the proportional mitigation (CERT FIO45-C context)
- **Dedupe-tool precedents** (fdupes/jdupes/rmlint): all gate deletion behind explicit flags/interaction, never default — validates option (c) over option (b); errors to stderr is the established logging convention
- References: https://clig.dev/ · https://docs.python.org/3/library/filecmp.html · https://rmlint.readthedocs.io/en/latest/cautions.html · https://wiki.sei.cmu.edu/confluence/display/c/FIO45-C

## Recommendations for Spec

- Anchor the safe-default requirement to byte-identical no-flag behavior (Principle III language), with the two-positional-arg caller compatibility as an explicit FR
- Specify deletion as double-gated, direction-agnostic, keyed on mislabeled-ness — with all four safety negatives (non-identical, truncated copy, cross-swap, mixed legitimate pair) as first-class acceptance scenarios
- Require BOTH code moments (pre-existing pairs + recovery write) in the FR language so recovery-only wiring cannot pass review
- US-2 proof = path-invariance (`report-data.typ` byte-identical pre/post) + extractor module green; keep AC-2b defer fallback documented
- US-3 lands in `tachi-report-assembly/references/typst-artifacts.md` (+ contract doc if needed); explicitly do NOT wire the flag into the report-assembler agent
- Out-of-scope: `--dry-run` companion, generic directory janitor, producer-side changes, auto-pass from agent, standalone script
- Carry to plan: `run_extract` harness `extra_args` extension; `filecmp` import; optional `clear_cache()`; commit-before-gated-suite build gotcha; record pre-state pytest totals (Entry 15)

## Phase 0 Decisions (plan stage)

- **Decision**: Positive opt-in flag `--cleanup-mislabeled-images` (`action="store_true"`), threading into `detect_images` as defaulted kwarg `cleanup: bool = False`.
  **Rationale**: PRD decision (c); ADR-008 opt-in-for-high-risk precedent; two-positional-arg caller at `test_extractor_contract_fixes.py:200` must stay valid.
  **Alternatives considered**: option (b) `copyfile→move` (rejected by PRD — silently destructive default); `--no-cleanup` default-on (violates Principle III safe default); standalone cleanup script (rejected — code economy, probe already lives in the extractor).
- **Decision**: Byte-identity gate via stdlib `filecmp.cmp(a, b, shallow=False)` with one defensive `filecmp.clear_cache()` per cleanup-enabled `detect_images` run.
  **Rationale**: stdlib-only (ADR-017); `shallow=False` forces content comparison; `clear_cache()` removes the stat-signature cache class entirely for near-zero cost (≤6 stems).
  **Alternatives considered**: hash comparison (hashlib) — more code for no gain at 6 files; byte-loop — reinvents stdlib (rung 3); fd/inode TOCTOU hardening — disproportionate for a local single-user CLI, per-file try/except is the proportional mitigation.
- **Decision**: One shared deletion helper used by BOTH moments (pre-existing-pairs branch and recovery-write branch), predicate = mislabeled (content format ≠ extension) AND correctly-labeled counterpart byte-identical; recovery moment additionally gated on `pre_existed` recorded before `copyfile`.
  **Rationale**: FR-004 both-moments mandate; single predicate implementation prevents drift between the two call sites; `pre_existed` gate closes the AC-1g cross-swap data-loss edge.
  **Alternatives considered**: recovery-only wiring (explicitly forbidden — misses the primary US-2 case); post-loop directory sweep (a generic janitor — out of scope per PRD).
- **Decision**: Test harness extension — add optional `extra_args: list[str] | None = None` parameter to `run_extract` (appended to the subprocess argv).
  **Rationale**: existing signature `run_extract(target_dir, template_dir=None)` has no flag pass-through; optional-with-default keeps all existing call sites byte-identical.
  **Alternatives considered**: new parallel helper `run_extract_with_flags` (duplication); invoking the module directly for cleanup tests (loses the CLI-path coverage the ACs require).
- **Decision**: US-3 documentation lands in `.claude/skills/tachi-report-assembly/references/typst-artifacts.md` (primary), with a one-line cross-reference from `typst-template-contract.md` image-paths section only if it reads naturally.
  **Rationale**: typst-artifacts.md owns image validation + legacy extraction reference (L30–36, L112–114) — the canonical "report-assembly reference surface" of AC-3a; README/DEVELOPER_GUIDE don't reference the script at all.
  **Alternatives considered**: root-level guide edits (no existing extractor surface there — would create a new doc surface for a P3 story).
- **Decision**: US-2 dogfood proof = path-invariance (`report-data.typ` byte-identical pre/post) + extractor test module green; proceed per OQ-2 CLEAN with AC-2b defer fallback retained.
  **Rationale**: ADR-021 determinism makes byte-comparison of emitted data the strongest cheap oracle; no test consumes the snapshot images (triple-verified: BASELINE_EXAMPLES excludes agentic-app, MAESTRO invariant globs out test-output/, CI runs neither extractor suite).
  **Alternatives considered**: full PDF re-render comparison (needs Typst + fonts, adds noise for no additional proof); deferring US-2 outright (unwarranted — OQ-2 resolved CLEAN).
