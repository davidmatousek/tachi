# Session Continuation: F-374 Large-Architecture Pipeline Resilience

**Generated:** 2026-11-23 03:10
**Branch:** `374-large-architecture-pipeline-resilience`, draft PR #423 (PR 1)
**Last pushed commit:** `5d218af`, W2's push, with CI 14 of 14 green. This handoff's records commit follows it locally (see "State").

## Completed in session 1 (S1)

PR 1's W0, W1 and W2 are complete. S1 hit the 3-wave ceiling, as `agent-assignments.md` planned.

- **W0.** The pre-state census, with the ratchet floor at 44.9%. The 5 Whys gave TW-K4 (c). The S-1 proxy, and the fixture generator's skeleton. Gate G0 (`test-results/w0-gate.md`).
- **W1, the cut line.** The shared references (T005–T007), the contract text (T008–T010), and the renderer core: `tachi_parts`, `tachi_scoring`, `sarif_common` and `tachi-stage.py` (T011–T018, T140, T149). Also the fixture (T019, T020), the v4.48.4 baselines with a calibration Write (T021), the wiring (T022), and ADR-050's sizes and back-pointer notes (T023–T025). Gate G1 PASSED: the cut line is **`03a8f0d`**, with CI 12 of 12 green (`test-results/g1-cutline.md`).
- **W2, US1a's scorer, US5, US6a and US3's parsers.** The risk-scores renderer: T027, T028, T041 and T045–T050. The scoring-rules module (T042–T044). The scorer's contract, command and 1.1 templates (T029–T031, T051). The parsers and the data-layer oracle (T032, T033, T048, T057, T058, T142, T143). The fixture's variants (T040). The wiring (T047).
  - P0 (T061): APPROVED_WITH_CONCERNS.
  - TW-ESC (T062): does not fire, so T063 isn't fired (`test-results/tw-esc.md`).
- **Tests.** The post-wave scratch-clone suites (`test-results/wave-00` to `wave-02`) show no regressions against T001. All 34 pre-existing failures are in ungated modules. The coverage gate is about 95% over the six gated scripts, against an 80% bar, and the `tachi_parsers` ratchet is about 82%, against a 44.9% floor.

## State

- **Phase:** implement. **Tasks:** 56 of 150 done (PR 1: 56 of 91; PR 2: 0 of 59).
- **The batch sizes** in ADR-050 D6 are "Amended at W1": `risk-score` 13, `compensating-controls` 11 and `trees` 12. The architect's W1 and W2 rulings are all recorded in ADR-050 and `contracts/`. The scorer's flag vocabulary is **closed**, in `contracts/module-signatures.md`.
- **TW-N3: ARMED.** N3 hasn't merged. It affects lanes **D** (W3) and **O2** (W1′), whose agents need the private no-touch notes (see the private track).
- **The local records commit** (`tw-esc.md`, `wave-02/results.json`, this file and tasks.md's T062 and T063 marks) is **not pushed**. H6 forbids pushing records alone, so S2's first push carries it.

## Next Actions: session S2, which is PR 1's W3 and W4, plus PR 2's W1′

1. **Resume** `/aod.build 374` on the branch. The branch lives in a linked worktree, so check `git worktree list`, and never switch branches in the main checkout (H9). The handoff check finds this file.
2. **W3, with a new fix lane FX0** (`senior-backend-engineer`, from the team-lead's S2 plan in `tw-esc.md`).
   - **FX0's first slice, about 0.4 d, is W3's first commit,** alongside T034, T052 and T037:
     - **P0-1 (HIGH):** escape a prose line that starts with `~` as `&#126;`, so a line-start `~~~` can't open a code fence. Otherwise the next run's reader silently loses §4 and §6. It touches `tachi_parts`' escaping, the part-file reference and `tachi_parsers`' decoder, plus tests. ADR-050 D3 records the amendment.
     - **P0-4's** forbidden-character check: control bytes from `threats.md` or the baseline must not reach output (NFR-10). T064 confirms it.
     - **P0-3's** reader: the `threats.sarif` fallback crashes on unnamed groups (`maestro-reference`), and blanks the legacy `properties.id` form's identity text without a warning. It needs a committed test.
   - **FX0's second slice, about 0.85 d, is the risk-scores fixes**, in files no W3 lane owns:
     - **P0-2:** a finding carried from a legacy baseline loses its tag history, so a later tag change is flagged `corrected` instead of `retagged` (ruling A).
     - **P0-3's** renderer side.
     - **P0-5:** §3 drops D2's weighted values and the MAESTRO line.
     - **P0-8:** always write `message.markdown`, even when it's `""`.
     - **P0-7:** a dead batch-input `refs` fallback.
     - R3a, R2 and D take the P0 pieces that fall in their own files.
   - **P0-6** (a copied peer keeps its primary's tags, so its next run is flagged `retagged`) needs an architect and PM ruling in W3. It is a known limit until then.
   - **P0-9** (the bound-predicate reading) is ADR and R1t work in W3. P0-10 to P0-12 are T080 follow-ups. The full P0 record is the architect's `architect-374-p0.md`, a gitignored results file from S1.
   - **W3's planned tasks:**
     - **R2t:** T034 and T056 (goldens first).
     - **R2:** T035, then T053 and T059.
     - **R3a:** T036, then T052 and T054.
     - **D:** T037, T038 and T060. TW-N3 applies to `control-analyzer.md`.
     - **X:** T039 and T055.
     - **SEC:** T064.
   - **Slot rules.** When R2t finishes, its slot goes to a second FX0 instance if FX0 would otherwise outlast R2's chain. Otherwise it goes to T093.
3. **W4.**
   - **In parallel:** T065 (offline end-to-end), T066 (the small-run oracle, in `--build-dir` mode so the clones stay clean), T067 (the review, split in two) and T068 (the Step 7 scan).
   - **Then:** T146 if its findings need fixing, then T069 (the push, recording ADR-050 D16's coverage figures), then T070 (the P1 checkpoint).
4. **PR 2's W1′,** inside S2.
   - **First:** T084, which cuts `374-pipeline-resilience-track-o` from the cut line `03a8f0d`.
   - **Then:**
     - T086–T088, the rulings O-α, O-β and O-γ, on a **second architect instance**;
     - T089, the TW-ADR gate;
     - T148, the fixture cases;
     - T093, once T086 commits, during W3.
   - The PM's scope guard applies (spec S-8 erratum). If S-9 shows that a subagent can't wait on its own agents, moving Phase 2's dispatch to the command layer is a scope change for the PM.
5. **S2 ends** after T070 (M4), with the next handoff. Sessions L and S3 follow (W5's live matrix, then W6's close-out).

## How S1 ran, and what S2 should repeat

- **Lane worktrees and cherry-picks** (H9).
  - Each lane works in its own detached worktree. The orchestrator commits on the lane, then cherry-picks onto the integration branch, and skips the cherry-picks that only carried a predecessor.
  - Agents never commit.
  - Hand-offs to a running lane go as an **unstaged** `git checkout <sha> -- <file>` of the files the lane doesn't own, followed by one short message.
- **One task per agent instance.** Six long-lived agents overflowed their context in S1. For multi-task lanes, start a fresh agent at each hand-off. Keep messages to running agents short.
- **Create a lane's worktree before dispatching its agent.**
- **The post-wave suite.** Run T001's census command in a scratch clone of the pushed tip (`python3 -m pytest tests/scripts tests/schemas --timeout=1080`, Python 3.11, scrubbed environment), and classify the results by test ID. `failures.log` is gitignored, and `results.json` is the record. Step 4.6 (test generation) is skipped, because the tasks write every test first, and H7 and one writer per file leave no room for an unplanned writer.
- **H1:** no pytest, extractor or renderer runs in a tracked tree. `rm -rf` is blocked here, so use a new directory name for every scratch clone.

## Notes for later tasks

- **W5** (T072–T077):
  - **The adopters.** SC-8's baseline (T021(b)) ran in a cloned v4.48.4 adopter under a neutral path that doesn't embed the source checkout's path. T072 and T075 must reproduce that arrangement.
  - **The controls target** is a fixed copy of the fixture's stub codebase at `c84ff16`, whose tree digest is in `sc8-baseline.md`, passed as `--target`. The SC-8 ceilings are 29,753 output tokens (scorer) and 38,720 (controls).
  - **Pricing.** F17 is re-priced at about 132–152 dispatches. Controls has no margin at size 11, so check each live part's size.
  - **The completion rule** replaces "foreground" (ADR-050 D6's dated note). Claude Code 2.1.330 has no foreground dispatch.
- **T079** (W6 notes):
  - The response cap depends on the environment: a clean environment carried `max_tokens` 128,000, and 64k was Runs A and B's cap.
  - Adopter files that hold `&amp;` and similar now read as the character, because of T033's decoder.
  - The ASI01 taxa name stays as "Agent Autonomy Abuse" in PR 1. A rename is a PM follow-up.
- **T080 follow-ups:**
  - `check-citation-urls.py` imports `yaml` at module level.
  - Older `tachi-pytest.yml` `paths:` gaps.
  - `stride-categories-shared.md`'s missing roster rows.
  - The adapter `VERSION` hashes (#369).
  - `WIRED_BY_T047` in `test_contract_text_374.py` is now inert.
  - `docs/devops/CI_CD_GUIDE.md` lacks the f374 modules (T080, T136).
  - P0-10 to P0-12.
- **PR 2:**
  - T114 deletes `generate-threats-sarif.py` from the manifest test's `EXCLUDED` list in the same commit that adds it.
  - R3b's rewrite removes `sarif_common.PREFIX_TO_RULE` and `generate-threats-sarif.py:320`'s raw `|` split.
  - O2 rewrites Phase 3.6's stale "13 detection agents".
  - O3 points `output-schemas.md`'s roster at `agent-roster-shared.md`.
  - FR-K5.6 is covered by the S-8 erratum.

## Context files

`tasks.md` (W3, W4 and W1′), `agent-assignments.md`, `test-results/tw-esc.md`, `test-results/g1-cutline.md`, ADR-050, `contracts/` (especially `module-signatures.md`), `plan.md` and `quickstart.md`.

## Resume command

```bash
claude "Resume F-374 implementation (branch: 374-large-architecture-pipeline-resilience). Waves W0-W2 complete (56/150 tasks; G1 cut line 03a8f0d; W2 pushed 5d218af, CI 14/14). Run /aod.build 374 to continue with W3 (FX0 P0-fix lane first) + W4 + PR 2's W1'."
```
