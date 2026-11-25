# W2′ entry: PR 1 integrated into PR 2's branch (T085)

**Date:** 2026-11-24, session S1′, lane X (devops). **Branch:** `374-pipeline-resilience-track-o` (draft PR #425).

**Result:** PR 1's final head is merged into PR 2's branch, `origin/main` is an ancestor of it, and the parity check passes (KB 18).
- **Method:** T127's two legs, as ruled at S1P-A1 and S1P-A2. Leg 1 is M1 (`7abc02a`), a merge of `8111c5e`. Leg 2 is M2 (`bb0154b`), a merge of a marker (`bed95a9`) built on `origin/main` (`47a4f95`).
- **Conflicts:** 5 conflicted files, 4 in leg 1 and 1 in leg 2 (7 hunks in all). They are the 5 that S1P-A3 predicted. Each was resolved by its rule, and no text was added or edited.
- **Result of the merges:** the branch now differs from `origin/main` in 18 paths (+8546/−36). Those are PR 2's own 19 paths without `NEXT-SESSION.md`. A trial merge of the branch into `origin/main` is clean, so #425's `dirty` state should clear at the entry push.
- **Not done here:**
  - nothing was pushed, and no test, script, extractor or renderer ran (H1);
  - the byte check of the merged fixture generator (S1P-A5) is T103's first step, in lane F;
  - the cross-read of the merged ADR and contracts (S1P-A4) is the architect's;
  - the census at the entry (S1P-A6) is the orchestrator's.

## Method and SHAs

| Item | Commit | Tree | Notes |
|---|---|---|---|
| PR 2's head before T085 | `9fd2266` | `c746793` | Clean, one commit ahead of its remote |
| PR 1's final head | `8111c5e` | `d888c71` | `refs/pull/423/head`. Its tree equals the squash `d03ee9a`'s: `git diff 8111c5e d03ee9a` is empty |
| `origin/main` | `47a4f95` | `d6e168e` | Fetched at the start, and as expected. Local `main` (`b040fa1`) was never used (H11, KB 18) |
| **M1** | `7abc02a` | `4054d92` | Leg 1: `git merge --no-ff --no-commit 8111c5e`. Parents `9fd2266`, `8111c5e` |
| **Marker** | `bed95a9` | `d6e168e` | `git commit-tree 'origin/main^{tree}' -p origin/main -p 8111c5e`. Parents `47a4f95`, then `8111c5e`. Its tree equals `origin/main`'s. No branch points to it, and M2's second parent keeps it reachable |
| **M2** | `bb0154b` | `6ae1713` | Leg 2: `git merge --no-ff --no-commit bed95a9`. Parents M1, then the marker |

The steps, in order:
1. `git fetch origin`, then `origin/main` read `47a4f95`, the expected SHA.
2. Before each merge, a read-only `git merge-tree --write-tree` preview gave the conflict set that S1P-A3 predicts: 4 files, then 1.
3. Leg 1 ran, and the conflicts were resolved by rule with a scratch script outside the repository. The script recombines whole lines that the two sides already hold, and it asserts that no line was added or lost. The four paths were staged by explicit path (H3), and M1 was committed.
4. The marker was built by plumbing: no checkout, no scratch worktree, and no ref moved. Its tree and parents were checked.
5. Leg 2 ran the same way and gave M2.
6. The parity check ran (below).

The pre-commit hook (gitleaks) passed for M1 and M2, and `--no-verify` was not used. There was no push, rebase, reset, stash, branch checkout or force.

## Conflicts and how each was resolved

| Leg | File | Hunks | Rule (S1P-A3) | Result |
|---|---|---|---|---|
| 1 | `docs/architecture/02_ADRs/ADR-050-large-architecture-output-authority.md` | 1: Revision History | Keep every row, in date order. Rows with the same date go in the order they were made | PR 1's W2 and W3 amendment rows (both 2026-11-23), then PR 2's rev. 3 row (2026-11-23). No row was edited |
| 1 | `specs/374-large-architecture-pipeline-resilience/contracts/cli.md` | 1: the end of the file | Keep all three "Readings ruled at" sections | W2 and W3 (PR 1), then rev. 3 (PR 2). The earlier W1 section was already in place |
| 1 | `specs/374-large-architecture-pipeline-resilience/contracts/part-files.md` | 2 | In §3, keep each side's edit. After §4, PR 1's W2 readings, then PR 2's two payloads | (a) §3's table: PR 2's `units` row (the `threats-md` and `report` unit shapes) with PR 1's `refs` row (its W2 sentence). The unedited base row on each side was dropped. (b) After "The batch plan (§4), as T017's tests pin it for T018": "Readings ruled at W2 (2026-11-23, before T045 and T046)", then "Stage payload: `threats-md`" and "Stage payload: `report`" |
| 1 | `specs/374-large-architecture-pipeline-resilience/NEXT-SESSION.md` | 2: add/add | Take PR 2's side whole | PR 2's file (blob `31e9e3e`), which is the same blob as `origin/main`'s handoff |
| 2 | ADR-050 | 1: the end of the table | Keep both appended rows | Rev. 3's row (2026-11-23), then main's "Merged (PR 1)" row (2026-11-24). The status line auto-merged to main's text: line 3 equals `origin/main`'s |

## Auto-merged files, looked over (S1P-A3)

- **`tasks.md`.** The two PRs' hunks don't overlap.
  - Leg 1: PR 1's marks come in as 8 hunks (58 lines), all in Part 1 (Phases 1.1 to 1.8). The result differs from PR 1's head in 4 hunks (7 lines), all in Part 2, which are PR 2's own.
  - Leg 2: main's change from #465 (2 hunks, 3 lines) lands in Part 1.
  - At M2, `git diff origin/main M2 -- tasks.md` is those same 4 Part 2 hunks.
- **The generator.** `PARTS` keeps `"id-reuse": part_id_reuse_pr1_pr2`. That function calls PR 1's `part_id_reuse` and adds PR 2's `id_reuse_pr2_files`. The other twelve entries match PR 1's table.
- **`test_fixture_374.py`.** PR 2's +405 lines sit on PR 1's version, and no hunk overlaps.
- **The fixture tree (S1P-A5).** PR 1 added 71 files under `tests/scripts/fixtures/large_arch/` and PR 2 added 9. The two sets share no path, so there was nothing to hand-merge, and T085's "take PR 2's side" had nothing to apply to. The merged generator must still reproduce the union of 80 files byte for byte. That check runs the generator (H1), so it stays T103's first step, and it must land before the first push (condition 2).
- **Release-commit files.** The release commit `cb06251` changed 6 files: `.release-please-manifest.json`, `CHANGELOG.md`, `README.md`, `docs/guides/ISOLATED_OPERATION_TACHI.md`, `scripts/install.sh` and `scripts/tachi_parts.py`. PR 2 touches none of them, so leg 2 took all six from main. With #465's 5 files, that is main's 11.
- **`scripts/`.** PR 2 changes nothing there. After M1, `scripts/` equals `8111c5e`'s. The staged deletion of `scripts/generate-risk-scores-sarif.py` is PR 1's. PR 2 never touched that file. After M2, `scripts/` equals `origin/main`'s.

## Parity (S1P-A2 step 5, KB 18)

All list comparisons ran in Python, because zsh doesn't word-split.

| Check | Result |
|---|---|
| REF = `git diff --name-only 8111c5e M1` | 19 paths, equal to PR 2's own paths (`git diff --name-only 03a8f0d 9fd2266`) |
| `git diff --name-only origin/main M2` | 18 paths: REF without `NEXT-SESSION.md`, with nothing extra on either side |
| `-U0` +/− lines, per path | Equal for all 18 paths. ADR-050 and `tasks.md` match too, so there is no context-only difference to excuse |
| `scripts/` | `git diff 8111c5e M1 -- scripts/` is empty, and so is `git diff origin/main M2 -- scripts/` |
| `tests/` | 11 paths in both diffs, the same list, with equal +/− lines per path (explained below) |
| The 12 paths that only PR 2 touched | Byte-identical to `9fd2266` at M1 and at M2 |
| PR 2's edits in the 6 files that both PRs touched (`NEXT-SESSION.md` apart) | `git diff -U0 03a8f0d 9fd2266` and `git diff -U0 8111c5e M1` carry the same +/− lines for each. No edit of PR 2's or of PR 1's was lost or altered by a resolution |
| Conflict markers; `.orig` or `.rej` files | None |
| `git merge-base --is-ancestor origin/main HEAD` | Yes, and `git merge-base origin/main HEAD` is `47a4f95` |
| Trial merge of the branch into `origin/main` (`git merge-tree --write-tree`) | Clean. Its tree equals M2's (`6ae1713`) |
| GitHub's diff after a push (`git diff origin/main...HEAD`) | 18 files, +8546/−36 |

**The `tests/` paths PR 2 owns.** All 11 come from `544e4f1`, T148's chain-cap and id-reuse fixture cases: nine fixture files under `tests/scripts/fixtures/large_arch/` (`chain-cap/main/`, `id-reuse/pr2/` and `id-reuse/pr2-no-mark/`, three each), the generator and `test_fixture_374.py`. Main changed nothing under `tests/` after `8111c5e`, so both diffs hold PR 2's T148 change and nothing else.

**The numbers at this entry**, for T127's re-check if `origin/main` moves. The columns are +/− in `git diff 8111c5e M1` and in `git diff origin/main M2`, and the two are equal for every path. `S` is `specs/374-large-architecture-pipeline-resilience`, and `F` is `tests/scripts/fixtures/large_arch`.

| Path | +/− |
|---|---|
| `docs/architecture/02_ADRs/ADR-050-large-architecture-output-authority.md` | +146/−7 |
| `S/contracts/cli.md` | +22/−5 |
| `S/contracts/part-files.md` | +243/−10 |
| `S/contracts/threat-model-records.md` | +83/−5 |
| `S/tasks.md` | +7/−7 |
| `S/test-results/prestate-pr2.md` | +194/−0 |
| `S/test-results/tw-adr-pr2.md` | +43/−0 |
| `F/chain-cap/main/expected-outcomes.json` | +2108/−0 |
| `F/chain-cap/main/run/tachi-build/phase1/inventory.json` | +2736/−0 |
| `F/chain-cap/main/run/threats.md` | +577/−0 |
| `F/id-reuse/pr2-no-mark/baseline/threats.md` | +75/−0 |
| `F/id-reuse/pr2-no-mark/expected-outcomes.json` | +176/−0 |
| `F/id-reuse/pr2-no-mark/run/threats.md` | +457/−0 |
| `F/id-reuse/pr2/baseline/threats.md` | +77/−0 |
| `F/id-reuse/pr2/expected-outcomes.json` | +213/−0 |
| `F/id-reuse/pr2/run/threats.md` | +457/−0 |
| `tests/scripts/generate_large_arch_fixture.py` | +527/−2 |
| `tests/scripts/test_fixture_374.py` | +405/−0 |

`S/NEXT-SESSION.md` is the 19th path of REF. PR 2's copy is byte-identical to main's, so it drops out of the second diff.

## Departures (S1P-A8)

These are departures from documents that still say otherwise. The team-lead edits `tasks.md`, and `plan.md` gets a note.

1. **The W3-tip merge is retired.** T085 said to merge PR 1's committed W3 tip once its push (T039) is green. That tip, `f43440b`, is an ancestor of `8111c5e`, and 59 later commits changed 7 scripts by +834/−174 lines. They are `tachi-stage.py` (219), `tachi_parsers.py` (375), `tachi_parts.py` (136), `sarif_common.py` (52), and three smaller files. They are W2′'s own files, so a merge of the W3 tip would have started the lanes on stale versions (S1P-A1).
2. **`plan.md`, PR 2's Branch bullet and the first Risks bullet.** They say PR 2's branch is "rebased onto `origin/main`… once, after PR 1's squash". It is now a marker merge at W2′'s entry (this record), then plain merges at later wave boundaries. The "Superseded at `/aod.tasks`" note gains a line saying so. The spec's "merge `origin/main`" (§ The split) is met by the marker merge (F5).
3. **T085.** It changes in six ways:
   - the method is T127's two legs, not a one-leg merge;
   - the gate is PR 1's merge, rather than T039's push;
   - the record is this file;
   - the effort is about 0.2 d, from 0.1 d;
   - the fixture clause is no hand-merge, because the two sets are disjoint, and T103's regeneration and byte check land before the first push (S1P-A5);
   - the pre-state is re-based (the last section).
4. **T127.** It loses its first merge and the marker. It keeps S1P-A7's list:
   - a plain re-merge of `origin/main`, only if main moved since the last integration, with H11's fetch first;
   - KB 18's parity re-check against the current `origin/main`;
   - ADR-050 D16's coverage figures for PR 2's gated modules, and `tachi_parsers.py`'s ratchet (G3′);
   - the push and TW-CI, when W4′ has a commit that isn't records.

   "Against T084's totals" becomes "against the entry's totals". Its effort is about 0.1 to 0.15 d, from 0.25 d.
5. **T124, T125 and T126 (AR-T8's two clauses).** T124's re-run becomes conditional: it runs only if T127's re-merge changed a path outside this feature's records. T125 reviews `git diff origin/main...HEAD`. From this entry on, that is GitHub's diff, so "against PR 1's final head" no longer applies. T126's Step 7 scan and its Step 8 economy gate diff against `origin/main` too.
6. **The DoD's "(T001, T084)".** T084 is read as re-based at the entry.
7. **"Dependencies & Execution Order".** T085 waits for PR 1's merge, not for T039's push. "T127 merges `origin/main` after PR 1's squash" becomes "T085 merged it; T127 re-merges if main moved". W2′'s "First:" line gains the hoist (S1P-A14).
8. **H6.** If the entry push is taken, it is the one exception to one push per wave (S1P-A15, S1P-T11).
9. **Later integrations.** `47a4f95` is now an ancestor of the branch. So any later integration (TW-N3's merge, #396, a patch release) is a plain `git merge origin/main` with this parity check, and no second marker is needed (S1P-A2).

## Pre-state at the entry (S1P-A6)

T084's totals were taken at the cut line (`03a8f0d`), before PR 1's W2–W6 tests existed. At that line f374-offline ran 2,576 tests, and PR 1's W4 record shows 5,937. A reading against T084's totals can't see a regression in the later tests. The entry commit's literal totals (KB 15, KB 16) replace T084's as PR 2's pre-state, for T114, T098, T127, T138 and the DoD's item 2. They come from a scratch-clone census and from the entry push's CI (S1P-A15).

- **The integrated state T085 leaves:** M2, `bb0154b` (tree `6ae1713`). The orchestrator names the entry commit when it runs the census.
- **The reading rule stands:** a run regresses only if a node id that passes at the baseline fails later, or if a gate total drops. Skips are named, so that a new skip is visible. Only the baseline changes.

**Totals at the entry commit `a8b0cbe`** (M2's tree plus this record): the integrated tree before T151 (S1P-PM5). Every run used a scratch clone of the committed tip (H1, H6). The commits after it carry records only, so these totals hold for the pre-hoist push's tree.

| Run | Interpreter | Totals |
|---|---|---|
| Full census: `tests/scripts` and `tests/schemas` | 3.11.13 | 7,671 passed, 26 failed, 8 errors, 25 skipped (990 s) |
| f374-offline, with D16's coverage gate | 3.11.13 | 6,014 passed, 20 skipped; TOTAL 96.37% (the gate is 80%) |
| The `tachi_parsers.py` ratchet | 3.11.13 | 733 passed; 83.6%, against the floor of 44.9 |
| f374-py39-floor | 3.9.6 | 5,984 passed, 20 skipped |
| extraction-fidelity, report-posture and manifest-completeness | 3.11.13 | 1,064 passed |
| The same three jobs | 3.9.6 | 1,063 passed, 1 skipped |

- **Against PR 1's merge candidate.** This is W6's census at `ad64a72`. There are 0 regressions and 0 new failures. The 34 failures and errors are all pre-existing, and all lie outside every gated job, in nine modules:
  - `test_backward_compatibility.py` (6);
  - `test_coverage_attestation_audit.py` (2);
  - `test_coverage_attestation_in_scope.py` (3);
  - `test_human_trust_exploitation.py` (9);
  - `test_llm10_unbounded_consumption_enrichment.py` (2);
  - `test_ml_top_10_coverage_bundle_enrichment.py` (2);
  - `test_mobile_top_10_coverage_bundle_enrichment.py` (6);
  - `test_pyyaml_deferred_import.py` (1);
  - `test_tool_abuse_enrichment.py` (3).

  No gated job fails, so the entry carries no T085 defect (S1P-PM5).
- **T103's regeneration slice** is a zero diff. The merged generator reproduces all 292 fixture files byte for byte: 212 at the merge base, 71 from PR 1 and 9 from PR 2. T020's byte check passes 190 of 190 on 3.11.13 and on 3.9.6.
- **The CI half** comes from the pre-hoist push's run (T114 step 1). This corrects the paragraph above, which named the entry push's CI (S1P-PM5). Its totals are added here when the run finishes. The entry push, which carries the hoist, is the first gate read against this pre-state.

## Rev. 3 cross-read (S1P-A4)

**Date:** 2026-11-24, session S1′, lane ADR (architect).

**What was read, at `a8b0cbe`:**
- ADR-050's rev. 3 text: D6's O-α, O-β, O-γ and RR3, and rev. 3's pointers in D4 and D11. It was read against PR 1's merged D2–D4, D6–D10, D15, D16 and Known limitations.
- The contracts `part-files.md`, `threat-model-records.md`, `cli.md` and `module-signatures.md`.
- T093's held `orchestrator.md` (`8a08fb0`).
- tasks.md's T093, T094, T100, T106, T108, T109 and T112.
- The shipped readers in `scripts/`, wherever the text says what one of them does.

**Method:** read-only `git show` and `git diff`. Nothing ran (H1).

**Result: 4 errata, S1P-A18 to S1P-A21, each with a minimal text fix in this lane.**
- One of them changes a ruling (S1P-A19), and `tw-adr-pr2.md` records it.
- No contingency fires.
- With these fixes, the bindings that S1P-A4 named hold.

### Errata

- **S1P-A18: D3's P0-4 and D4's row 2 at PR 2's three writers.** PR 1's text says a renderer refuses, at intake and with exit 2, a value from an input that isn't a part, through one predicate, `tachi_parts.forbidden_character`. That predicate covers step 10's set, the tag block and a lone surrogate. `module-signatures.md` adds that "PR 2's writers call it too". Rev. 3's contracts fall short of this in three places:
  - **The section manifest.** `part-files.md` had the manifest refuse "a `"`, a `\` or a control character" in a frontmatter string, which misses U+2028, U+2029, the bidi controls, the tag block and a lone surrogate. `threat-model-records.md` stated no string rule at all. **Fix:** `threat-model-records.md` gains the manifest's string rule, with the predicate, and `part-files.md` names the predicate. `plan --stage threats-md` and the joiner's re-validation then refuse such a string with exit 2.
  - **The assembler.** Its exit 2 list had no intake check, only exit 4's whole-file backstop. **Fix:** `part-files.md`'s exit 2 list gains the intake, which names the finding, the field and the regenerate remedy, and covers a carried tree in `trees`.
  - **The trees.** D14's tree checks had no character check. So a tree with a bidi control would reach Step 2.9's backstop and fail the whole run after every tree had been written. **Fix:** D14's checks gain the predicate. `reconcile` already holds a generated tree to D14's checks (D6's `trees` row), so a failing generated tree is retried, and `trees` stops with exit 2 only on a carried one.
  - **Lanes:** T092, T106, T108 and T109.
- **S1P-A19: D8's R-F in PR 2's run.**
  - **The contradiction.** PR 1's W4 ruling R-F makes a finding that two of Section 4a's groups list "reported, never silent": each renderer warns `correlation-member-repeated`, and the run exits 5. In PR 2's run, `generate-threats-sarif.py` (D8's Track O renderer) and `assemble-report.py report` both read Section 4a, and `cli.md` gives both of them 0, 1, 2 and 4. So the run that wrote Section 4a would never name the finding.
  - **Ruling.** The run reports it once, from `check-threat-model.py` at Step 2.8. The check writes one warning, with the count and the first 20 IDs, into its hand-off and exits 5, and `close` folds the warning into the run's stage record. The generator and the assembler apply the claim rule and keep their exit codes.
  - **Fix:** D8 gains the sentence, `part-files.md` §6's closed warning codes gain `correlation-member-repeated`, and `cli.md`'s check row names it.
  - **Lanes:** T095 and T096 (OC, W3′).
- **S1P-A20: the roadmap's primary.**
  - **The contradiction.** `part-files.md` said that a group's primary is "its first member in Section 4a". D8 and `parse_correlation_groups` take the first member left after the claim rule, filtered to the run's open IDs. The two differ when the first listed member isn't open, or an earlier group has claimed it. In that case the roadmap and `threats.sarif` would name different primaries.
  - **Fix:** the roadmap takes `parse_correlation_groups`' groups and primaries, with the run's open IDs as `member_ids`.
  - **Lanes:** T092 and T109.
- **S1P-A21: D3's P1-3 (W6) and the joiner's rows.**
  - **The contradiction.** Section 7's readers read GitHub's `\|` as a pipe inside its cell (`escaped_pipes`). A value can end in `\`, because only edge whitespace is stripped at intake. So a row written without spaces around its delimiters would give a `\|` that shifts the row. A legitimate join would then fail its read-back with exit 4, and GitHub would show a broken table.
  - **Fix:** `part-files.md` has the joiner write each row with a space on each side of every delimiter.
  - **Lane:** T106.

ADR-050 gains a Revision History row for S1P-A18 and S1P-A19, and the contracts follow.

### The bindings S1P-A4 named

- **D3's plan-level `refs`: holds.**
  - The `threats-md` and `report` plans hold `refs` `{}`, and `threats-md`'s `architecture_warning` is null.
  - Every path that the joiner or the assembler reads is in the plan's digest-pinned `inputs`, or is recomputed from `--out` (D3 and D7, as ruled at W2 and W3).
- **D3's `~` guard and its nine references: hold.**
  - The joiner writes no prose, and a `~` in a cell stays as written. Its one extra escape, `&#35;` for a `#` in a cell, is one of the nine.
  - In the report, every fragment takes D3's prose sink and every cell its cell sink.
  - Rev. 3's reason for the `#` escape still stands. `parse_reference_set` still finds Section 7 by substring (`tachi_parsers._reference_set_start`). D3's exact-heading rule, ruled at W3, names only PR 1's readers, and Known limitations cites O-β's escape as the other half.
  - One residual: a frontmatter string that holds Section 7's heading text would fail the join's read-back with exit 4. The failure is loud and needs a contrived value, so it gets no fix.
- **D4's exit 2 for a forbidden character:** fixed by S1P-A18, for the joiner's manifest, the assembler's intake and the trees.
- **P1-4's from-disk rule: holds for both.**
  - The joiner compares what `parse_reference_set` reads back from the staged file with its sources, the manifest and the validated items, never with a second read of its own.
  - The assembler's FR-K5.3, FR-K5.5 and FR-K5.7 compare with the baseline tree files, the reference set and the merge recomputed from the parts.
- **D6's W4 loop wording:**
  - **T093's held text** doesn't contradict it. Phase 2 has no `reconcile`. Each wave starts only once every agent of the wave before has completed and has its record. No replacement starts until its wave is over. The completion rule bars compiling, reporting or returning while an agent runs. That is W4's rule, without the `reconcile` sentence, which has no Phase 2 counterpart.
  - **`threats-md`'s protocol** (`part-files.md`) is consistent. Every listed part is written before `reconcile` runs ("Waves don't apply here").
  - **T112's Phase 5** isn't written yet. It must copy W4's four command sentences for the `trees` and `report` loops (below).
- **D7 and D8's URI guard, for T100: holds.**
  - `sarif_common.self_check` checks every written `artifactLocation.uri`, as written and percent-decoded once, whether or not its caller passes `uri`. So T100 inherits the guard by calling the shared emitter's self-check.
  - Rev. 3 and the contracts say nothing against it.

### Read and consistent (no erratum)

- **D2.** The `threats-md` rows carry a MAESTRO layer wherever D2's W4 layer chain reads one: Section 7, the per-finding tables, and Section 1's components.
- **D9 and D10.** Rev. 3 touches no scoring.
- **D15.**
  - O-β reads `tachi.sections/1` into D15's PR 2 row.
  - `threat-report.md` stays at 1.1. O-γ adds no frontmatter key, and its sections are the template's, which T113 aligns.
  - No reader depends on whether Section 6 is present: the PDF reads its chains from `attack-chains.md`.
- **D16.** PR 2's five scripts are in the gated set, and the tag block is among the hostile inputs.
- **Known limitations.**
  - "Model-authored tables" reads as their cells (O-β).
  - The entry on the extractors' substring search names O-β's escape.
  - The SARIF fallback's unreported repeated member is PR 1's entry.
- **`cli.md` and `part-files.md`.**
  - On a digest mismatch, PR 1's `fail` still writes its record, with `plan-digest-mismatch`, which RR3's Step F order relies on.
  - PR 2's stage-record counts and §6's key set agree with D15's row and with D4's table.
- **`module-signatures.md`.**
  - Every name that rev. 3 relies on exists: `forbidden_character`, `parse_correlation_groups` with `repeated`, and `EFFORT_LEVELS`.
  - Rev. 3's constants in `tachi_parts` add no import, so C1 holds.

### For the lanes and tasks.md v1.5 (not errata)

- **T112 (O2, W3′).**
  - Phase 5's `trees` and `report` loops copy D6's W4 sentences, and `test_contract_text_374.py`'s pin extends to `orchestrator.md`.
  - RR3's single `TACHI PLAN report` line replaces "each batch stage's `plan_id` and `plan_digest`" in T112's text. The team-lead makes that edit in v1.5.
- **T100 (R3b).** Keep writing `properties.severity` as Section 7's risk level. D8's fallback reads it, as ruled at W3.
- **The new readers of `threats.md`** (T096, T100, T109 and T117) read it through `tachi_parsers`' decoding readers. From PR 2 on, `threats.md` is rendered text, so any cell may hold D3's references.
- **Cost.** About 0.1 d in all, across T092, T095, T096, T106, T108 and T109. The team-lead prices it.

### Rulings for W2′'s lanes, second pass (2026-11-24, S1P-A22 to S1P-A30)

These are contract readings only. None changes a decision of ADR-050, and the details are in the architect's results for the second pass.
- **S1P-A22.** The chain outcome record is read only outside code fences, by the shared fence rule. `render`'s upsert and `check`'s rewrite replace `parse_chain_outcome`'s `lines` (`threat-model-records.md`).
- **S1P-A23.** `parse_chain_outcome` and `CHAIN_OUTCOME_LABEL` are recorded in `module-signatures.md`.
- **S1P-A24.** The model-keyword note stays in the orchestrator's working notes, and `phase1/dispatch.json` gains no key. D11 had already ruled out the printed intermediates where the note appeared, so this needs no PM item. T119 aligns `output-schemas.md`.
- **S1P-A25.** `coverage-requirements.md` Step 5 goes to T111.
- **S1P-A26 and S1P-A27.** The generator's `--architecture` is optional, and its stdout is one JSON object (`cli.md`).
- **S1P-A28.** `threats.sarif` keeps `tags`, `maestro-layer`, `severity`, `baselineState` and `affected_assets`, plus `baseline-run-id` and the correlation keys. The uncontracted keys are dropped and listed (`sarif-result.md`).
- **S1P-A29.** T100 migrates `test_affected_assets_wiring.py` and `test_owasp_2026_contract.py` (D1, D16).
- **S1P-A30.** The `tachi.chains/1` and `tachi.chain-narratives/1` key sets are closed, and T115's narratives form stands (`threat-model-records.md`).
