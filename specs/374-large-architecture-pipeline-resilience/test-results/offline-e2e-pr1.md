# Offline end-to-end run, PR 1 (T065, W4)

**Date:** 2026-11-23. **Tip under test:** `f43440b`, PR 1's W3 tip, committed and with nothing overlaid. **Lane:** E2E (tester). **Interpreters:** Python 3.11.13 and 3.9.6 (the floor). **Model:** none. Every agent was synthetic. **Where it ran:** a scratch clone of the tip, and project roots outside every tracked tree (H1). The lane's worktree gained nothing but this record (section 11).

## Result: PASS. No new defect found in shipped code; 7 observations (section 10)

| Item | Verdict | What shows it |
|---|---|---|
| SC-4, inherited scores on the seeded baseline | **PASS** | The 13 scorer scenarios of S-4's PR 1 variants (the regroup pair's three runs among them), 234 findings. Every finding's rendered values and flag set equal its `expected-outcomes.json`, and every SC-4 line holds (section 3) |
| SC-5, the offline half | **PASS**; the live half is T074's | 32 controls runs, base set and variants. One schema in every band table, totals equal the sums of the rows, `.md` and `.sarif` agree, no unjoined Section 4 recommendation, and the shipped parser and extractor read the corrected files and the pre-fix fixtures (section 4) |
| SC-6, SARIF identity, Track R (scorer, controls) | **PASS** | The regroup pair, both files: no carried finding loses its key, the unchanged re-run's keys are identical, no two findings share a key, the tool names differ. Repeated at scale on 408 findings (section 5) |
| US-1a #4, stale, invalid and missing parts | **PASS** | Both stages. Only the unfinished batches are listed again, narrower when the batch was missing, unparseable or overflowed, up to the cap. A stale, invalid or missing part is never counted by `reconcile` or by the renderer (section 6) |
| US-1a #5, a lineage that can't be recovered | **PASS** | Both stages. `reconcile` exits 4 and names the batch and its finding IDs. `fail` exits 0, writes a `failed` record with the remedy, and no canonical file is left holding a failed output (section 6) |

Not claimed here: US-1a #1 to #3, #6 and #7, SC-5's live half, SC-1 and SC-8. They need live runs (T073 to T075). Also shown on the way: NFR-2's byte-stable output and its Python 3.9 floor (sections 2 and 5), and the exit-code table of `contracts/cli.md` (section 7).

**Checks run:** 2592 on Python 3.11.13 and 2592 on Python 3.9.6, none failed on either. All 63 stage runs write byte-identical files on the two interpreters. 15 deliberate defects, each caught by the check that guards it, show that the checks can fail (section 9).

## 1. What was run

- **The clone and the install.** A shared clone of the repository, checked out detached at `f43440b`. `scripts/install.sh --source <clone>` then installed tachi into an empty adopter root (it reported `v4.48.4-126-gf43440b` and 45 items copied). Its `scripts/` holds the 11 installed scripts (`extract-infographic-data.py`, `extract-report-data.py`, `populate-affected-assets.py`, `render-compensating-controls.py`, `render-risk-scores.py`, `sarif_common.py`, `tachi-stage.py`, `tachi_parsers.py`, `tachi_parts.py`, `tachi_scoring.py`, `tachi_scoring_rules.py`). Every scenario got its own project root with a copy of that `scripts/`, and every call was `python3 scripts/<name> ...` from that root, as the two commands make it. So the run also shows that the installed set alone is enough for both stages.
- **The sequence.** For each stage and run: `plan`, then a synthetic agent writes the part of every batch to its planned path, wave by wave as Step 3 does, then `reconcile` (again while it exits 3), then the renderer. The scorer runs first. The controls stage then reads the scorer's `risk-scores.md` and the stub codebase.
  - Scorer: `tachi-stage.py plan --stage risk-score --out run --date 2026-11-23 --threats run/threats.md`, then `reconcile --stage risk-score --out run --plan ID --plan-digest HEX`, then `render-risk-scores.py --out run --plan ID --plan-digest HEX`.
  - Controls: `tachi-stage.py plan --stage compensating-controls --out run --date 2026-11-23 --risk-scores run/risk-scores.md --target target`, then `reconcile` and `render-compensating-controls.py` with the same arguments.
  - The baseline comes from the commands' default, the `baseline.source` of `threats.md`. The architecture file is at `docs/security/architecture.md`, the default. The probes in section 8 pass `--baseline-dir`, `--architecture`, a non-default `--out` and absolute paths.
- **The scenarios.** The base set (`baseline/threats.md`, 408 open findings, as the precomputed scorer input), the gated subset (42 findings), the 14 PR 1 variants of S-4, and two kinds of scenario of mine. `base-carry` is the base set a second time, with the first run's outputs as its baseline. The `-fresh` runs are each of the 12 single-run variants again with its baseline directory left out, so that every finding is scored fresh and the scorer's parts carry the run. PR 2's variants (`chain-cap`, `id-reuse/pr2`, `pr2-runs`) don't exist at this tip.
- **The synthetic agents** use no model. Each reads its batch input and writes the part that the input names. The scorer's judgment comes from a hash of the finding ID (the category's default vector, sub-scores, the zone from the threat model), except where a variant's outcomes file gives the judgment (`id-reuse`). The controls agent gives a status by hash, evidence from the stub codebase's real files and lines, an 11-cell `matrix_row` with the four slot tokens, and a four-key body. For an UNCHANGED finding whose unit row holds a baseline result it copies that result and sets `carried_forward`. Every part passed `tachi_parts.read_part`, which is what `reconcile` exiting 0 shows.
- **The checks** read the written files back, with readers of their own (the shipped code supplies only the nine-entry decoder, the ID canonicalizer and sort key, and the reference-set wrapper that FR-E.16 names). A scenario with an outcomes file is compared finding by finding.
- **Wall time** is the sum of a stage's script steps (`plan`, `reconcile`, render). The synthetic agents are instant and left out, so it isn't an estimate of a live run.

## 2. Both stages on the base set and every variant

`Units` is what the plan sends to an agent: for the scorer the non-peer findings that need judgment, for the controls stage every scored finding. D6's sizes are 13 and 11. Exits are plan / reconcile / render, and 5 is success with warnings. `Open/resolved` and `Parse err.` are the stage record's counts of those names, and its `rendered` equals `open` in every row. Flags are the record's counts by kind. `2 runs` says whether a second run on the same inputs, in another project root, wrote byte-identical `.md` and `.sarif` files.

| Scenario | Stage | Units | Batches (waves) | Exits | Open/resolved | Parse err. | Flags | Wall s | 2 runs |
|---|---|--:|---|---|---|--:|---|--:|---|
| base | scorer | 326 | 26 (16+10) | 0 / 0 / 5 | 408/6 | 0 | none | 0.54 | yes |
| base | controls | 408 | 38 (16+16+6) | 0 / 0 / 5 | 408/6 | 0 | none | 0.67 | yes |
| gated-subset | scorer | 33 | 3 (3) | 0 / 0 / 5 | 42/3 | 0 | none | 0.28 | yes |
| gated-subset | controls | 42 | 4 (4) | 0 / 0 / 5 | 42/3 | 0 | none | 0.30 | yes |
| seeded-error | scorer | 0 | none | 0 / 0 / 5 | 108/2 | 12 | corrected 73, unverifiable 12, unchecked 14, override 2, input 12 | 0.41 | yes |
| seeded-error | controls | 108 | 10 (10) | 0 / 0 / 5 | 108/2 | 12 | none | 0.52 | yes |
| legacy-format | scorer | 0 | none | 0 / 0 / 5 | 24/0 | 0 | corrected 20, unverifiable 1, input 2 | 0.26 | yes |
| legacy-format | controls | 24 | 3 (3) | 0 / 0 / 5 | 24/0 | 1 | none | 0.27 | yes |
| legacy-format/no-baseline-date | scorer | 0 | none | 0 / 0 / 5 | 4/0 | 0 | corrected 5, unchecked 1 | 0.26 | yes |
| legacy-format/no-baseline-date | controls | 4 | 1 (1) | 0 / 0 / 5 | 4/0 | 0 | none | 0.26 | yes |
| tagged/renderer-form | scorer | 0 | none | 0 / 0 / 5 | 12/0 | 0 | override 1, retagged 25 | 0.25 | yes |
| tagged/renderer-form | controls | 12 | 2 (2) | 0 / 0 / 5 | 12/0 | 0 | none | 0.26 | yes |
| tagged/legacy-form | scorer | 0 | none | 0 / 0 / 5 | 8/0 | 0 | unchecked 2, retagged 13 | 0.25 | yes |
| tagged/legacy-form | controls | 8 | 1 (1) | 0 / 0 / 5 | 8/0 | 0 | none | 0.25 | yes |
| tagged/s13-block-equal | scorer | 0 | none | 0 / 0 / 5 | 6/0 | 0 | retagged 8 | 0.25 | yes |
| tagged/s13-block-equal | controls | 6 | 1 (1) | 0 / 0 / 5 | 6/0 | 0 | none | 0.25 | yes |
| tagged/s13-stale-block | scorer | 0 | none | 0 / 0 / 5 | 6/0 | 0 | retagged 8 | 0.26 | yes |
| tagged/s13-stale-block | controls | 6 | 1 (1) | 0 / 0 / 5 | 6/0 | 0 | none | 0.25 | yes |
| tagged/s13-drift-form | scorer | 0 | none | 0 / 0 / 5 | 6/0 | 1 | retagged 8, input 18 | 0.24 | yes |
| tagged/s13-drift-form | controls | 6 | 1 (1) | 0 / 0 / 5 | 6/0 | 1 | input 24 | 0.25 | yes |
| tagged/s13-no-architecture | scorer | 0 | none | 0 / 0 / 5 | 6/0 | 0 | retagged 12 | 0.25 | yes |
| tagged/s13-no-architecture | controls | 6 | 1 (1) | 0 / 0 / 5 | 6/0 | 0 | none | 0.25 | yes |
| tagged/s13-neither-source | scorer | 0 | none | 0 / 0 / 5 | 6/0 | 0 | none | 0.25 | yes |
| tagged/s13-neither-source | controls | 6 | 1 (1) | 0 / 0 / 5 | 6/0 | 0 | none | 0.25 | yes |
| id-reuse-pr1 | scorer | 2 | 1 (1) | 0 / 0 / 5 | 7/1 | 0 | reused-id 1 | 0.25 | yes |
| id-reuse-pr1 | controls | 7 | 1 (1) | 0 / 0 / 5 | 7/1 | 0 | reused-id 1 | 0.25 | yes |
| ties-scorer | scorer | 0 | none | 0 / 0 / 5 | 9/0 | 0 | corrected 10 | 0.25 | yes |
| ties-scorer | controls | 9 | 1 (1) | 0 / 0 / 5 | 9/0 | 0 | none | 0.26 | yes |
| ties-controls | controls | 6 | 1 (1) | 0 / 0 / 5 | 6/0 | 0 | none | 0.26 | yes |
| regroup-pair:run1 | scorer | 0 | none | 0 / 0 / 5 | 9/0 | 0 | none | 0.25 | yes |
| regroup-pair:run1 | controls | 9 | 1 (1) | 0 / 0 / 5 | 9/0 | 0 | none | 0.27 | yes |
| regroup-pair:run2 | scorer | 0 | none | 0 / 0 / 5 | 10/0 | 0 | divergent 2 | 0.25 | yes |
| regroup-pair:run2 | controls | 10 | 1 (1) | 0 / 0 / 5 | 10/0 | 0 | none | 0.26 | yes |
| regroup-pair:run3 | scorer | 0 | none | 0 / 0 / 5 | 10/0 | 0 | divergent 2 | 0.25 | yes |
| regroup-pair:run3 | controls | 10 | 1 (1) | 0 / 0 / 5 | 10/0 | 0 | none | 0.27 | yes |
| base-carry:run1 | scorer | 326 | 26 (16+10) | 0 / 0 / 5 | 408/6 | 0 | none | 0.52 | yes |
| base-carry:run1 | controls | 408 | 38 (16+16+6) | 0 / 0 / 5 | 408/6 | 0 | none | 0.65 | yes |
| base-carry:run2 | scorer | 52 | 4 (4) | 0 / 0 / 5 | 408/6 | 0 | reused-id 41 | 0.62 | yes |
| base-carry:run2 | controls | 408 | 38 (16+16+6) | 0 / 0 / 5 | 408/6 | 0 | reused-id 41 | 0.68 | yes |

**Each single-run variant again, with its baseline left out.** As shipped, nearly every variant finding is UNCHANGED and carried, so the scorer's parts are barely used. With the baseline directory removed nothing resolves, every finding is scored fresh, and the agent's parts carry the whole run. The same checks apply (there is no outcomes file for a changed input). Units and batches are the scorer's, then the controls stage's; the stage record's `open` and `resolved` are the scorer's; `Flags` are its `input` flags: the values that the drift form lacks (S-12(b)), and the fallbacks described below.

| Variant | Scorer units in batches | Controls units in batches | Render exits | Open/resolved | Flags | Wall s (scorer / controls) | 2 runs |
|---|---|---|---|---|---|---|---|
| seeded-error | 108 in 9 | 108 in 10 | 5 / 5 | 108/2 | input 2 | 0.34 / 0.36 | yes |
| legacy-format | 24 in 2 | 24 in 3 | 5 / 5 | 24/0 | none | 0.27 / 0.28 | yes |
| legacy-format/no-baseline-date | 4 in 1 | 4 in 1 | 5 / 5 | 4/0 | none | 0.25 / 0.26 | yes |
| tagged/renderer-form | 12 in 1 | 12 in 2 | 5 / 5 | 12/0 | none | 0.25 / 0.28 | yes |
| tagged/legacy-form | 8 in 1 | 8 in 1 | 5 / 5 | 8/0 | none | 0.30 / 0.28 | yes |
| tagged/s13-block-equal | 6 in 1 | 6 in 1 | 5 / 5 | 6/0 | none | 0.29 / 0.31 | yes |
| tagged/s13-stale-block | 6 in 1 | 6 in 1 | 5 / 5 | 6/0 | none | 0.26 / 0.26 | yes |
| tagged/s13-drift-form | 6 in 1 | 6 in 1 | 5 / 5 | 6/0 | input 24 | 0.28 / 0.30 | yes |
| tagged/s13-no-architecture | 6 in 1 | 6 in 1 | 5 / 5 | 6/0 | none | 0.26 / 0.26 | yes |
| tagged/s13-neither-source | 6 in 1 | 6 in 1 | 5 / 5 | 6/0 | none | 0.28 / 0.29 | yes |
| id-reuse-pr1 | 7 in 1 | 7 in 1 | 5 / 5 | 7/1 | none | 0.26 / 0.26 | yes |
| ties-scorer | 9 in 1 | 9 in 1 | 5 / 5 | 9/0 | none | 0.26 / 0.27 | yes |

- **The base set at D6's sizes.** The scorer plans 326 units (408 open findings, less 82 correlated peers that take their primary's assessment) into 26 batches: 14 of 13 and 12 of 12, in waves of 16 and 10. The controls stage plans 408 units into 38 batches: 28 of 11 and 10 of 10, in waves of 16, 16 and 6. Each is at least two batches (US-1a #1's offline half), and no batch is over its size.
- **Where the batches go.** In 14 of the 19 scorer runs of the first table the plan has no batch, because every finding is UNCHANGED and carried (`Units` 0). The renderer carries and recomputes them, and `reconcile` exits 0 on a plan with no batches. `id-reuse` sends its 2 NEW findings, and `base-carry` run 2 sends 52 (the 41 NEW and 21 UPDATED findings, less the peers) into 4 batches.
- **Output sizes, base set.** `risk-scores.md` 1.32 MB and `.sarif` 785 KB; `compensating-controls.md` 716 KB and `.sarif` 984 KB. By UTF-8 bytes divided by 4 each is well over the 64k-token cap (about 329k, 196k, 178k and 246k tokens), so no single response could write one. The largest synthetic part is 14 KB for the scorer and 17 KB for the controls stage (indicative only: the judgment is synthetic).
- **The records.** `truncations` and `cell_overwrites` are 0 in every run. `narrative_fallbacks` is 0 in every run but two, the scorer's in `seeded-error-fresh` (2) and `tagged-s13-drift-form-fresh` (6). There my synthetic reachability rationale names its zone through `{{name:zone}}`, while the part gives a null zone (a compound or unknown trust label). The renderer accepts the part, writes the fixed sentence for that field, flags it `input:rationale.reachability:narrative-fallback` and counts it: D3's per-field fallback, working as written. The mistake is my agent's, not the code's. No run lists an undeclared path. Every stage record is `success-with-warnings`, and one warning is common to every row: see O1.
- **Two runs, one set of bytes.** The 63 stage runs of the two tables were repeated in a second project root, with other absolute paths. All 63 pairs of `.md` and `.sarif` files are byte-identical. The stage record is not, since it holds a plan ID and a clock, and NFR-2's byte-stable output means the two files. So NFR-2's byte stability holds for every run here.

## 3. SC-4: the seeded baseline, decidable cases

Each of the 234 findings of S-4's scorer scenarios was compared with its `expected-outcomes.json`, the oracle that the generator wrote without the renderer: the eight values of Section 2 (CVSS, the three sub-scores, composite, band, SLA and disposition), the owner and review date, the vector in the SARIF, and the flag set (`pinned` and `derived` flags required, `optional` ones free, nothing unlisted). The counts by flag kind, the routing, and Section 6's `Normalized` count were compared too.

| SC-4 line | Findings | Values equal | Flags equal |
|---|--:|--:|--:|
| Composite errors are corrected and flagged | 20 | 20/20 | 20/20 |
| Band errors are corrected and flagged | 13 | 13/13 | 13/13 |
| A CVSS score that its vector doesn't give is corrected and flagged | 18 | 18/18 | 18/18 |
| A missing vector is reported unverifiable, never invented | 12 | 12/12 | 12/12 |
| An out-of-range reachability under an unambiguous label is flagged | 12 | 12/12 | 12/12 |
| 0 documented exceptions are flagged (clamped scores, clean rows, RESOLVED rows kept as they were) | 34 | 34/34 | 34/34 |
| N17-dependent cases are reported as unchecked | 14 | 14/14 | 14/14 |
| Rounding-only differences are counted, and flagged only when they move a band | 12 | 12/12 | 12/12 |
| 0 carried scores change because of a regroup alone | 20 | 20/20 | 20/20 |
| 100% of the peer divergences are flagged | 4 | 4/4 | 4/4 |
| The legacy-format baseline is handled under R-26 (every case, both directories) | 28 | 28/28 | 28/28 |
| The tagged cases are handled under R-25 and ruling A (every case, seven scenarios) | 50 | 50/50 | 50/50 |

- **No score moves on a regroup.** In the regroup pair's runs 2 and 3, 18 carried findings (peers whose primary changed included) render the composite, band and sub-scores that they were stored with (18 of 18). The same property at scale: 274 UNCHANGED findings were carried by `base-carry` and 0 of them changed a score or band between its two runs.
- **The flag census, `seeded-error`.** corrected 73, input 12, override 2, resolved 2, unchecked 14, unverifiable 12. These are the counts the outcomes file requires, and the stage record's counts equal them.
- **S-12 and the form cases.** `tagged/s13-drift-form` (Section 7 as a numbered list) is read as the reference set, flags each value its form lacks with `input:` flags and the cause, and finishes (S-12(a), (b)). A `threats.md` with no Section 7 stops at `plan` with exit 2, names the file, the section and the expected form, and writes nothing (S-12(c); the exit table in section 7 counts it).

## 4. SC-5, the offline half: the controls report

Over 32 controls runs (the base set, the gated subset, every variant, the regroup pair's three runs, `base-carry`'s two, and the 12 variants again scored fresh). Each row counts the checks that guard the property, one or more in each run:

| Property | What was compared | Checks passed |
|---|---|---|
| One schema in every band table | The 11-column K8 header in each band table, and no row with another cell count | 32/32 |
| Every scored finding once, under its own band | Section 2 holds exactly the scored open findings, once, and each row sits under its own residual severity | 64/64 |
| Totals equal the sums of the rows | Section 1's headline and distribution, Section 2's statistics, Section 5's totals, shift table and distribution, each recomputed from the rows in exact decimal arithmetic; each residual is the inherent score times the P0 factor, half up | 224/224 |
| `.md` and `.sarif` agree | Per finding: control status, inherent and residual score, the recommendation text and the effort word | 32/32 |
| 0 unjoined Section 4 recommendations | One block for each Partial or missing finding and none for a found one, joined to its row by ID, numbered 1 to n in the template's order, each with its four keys | 160/160 |
| The N/N rule and identity | One result per scored finding, unique hashes, one URI spelling, no `automationDetails`, `integrity-flags` and `maestro-layer` on every result, and a hash that differs from the scorer file's for the same finding | 415/415 |
| One digest | The markdown's stamp, the SARIF's `tachi_provenance` and the stage record agree | 32/32 |
| #373's parsers read the corrected files | `tachi_parsers.parse_compensating_controls_md` finds every finding and coverage totals that sum to the rows; the shipped `extract-infographic-data.py` (risk funnel) reaches the renderer's own inherent total, residual total and reduction | 64/64 |

- **The pre-fix fixtures.** The committed v4.48.4 files of the base set (408 findings) and of the gated subset (42) go through the same parser and the same extractor. Both read them: the parser finds every finding, and the extractor's inherent and residual totals equal the totals the pre-fix file states (inherent 2273.6, residual 1836.7; inherent 249.9, residual 178.3).
- **Carry-forward at scale** (`base-carry`, run 2). The controls file carries 346 UNCHANGED results, `rescan_scope` `incremental`, and a carried row reads as in run 1: its text isn't escaped a second time (RR1).
- **`ties/controls`** (R-11): the 6 residual cases, 4 of them exact ties that a float or half-even rounding would move, render as the outcomes file says, with the judgment taken from the file's `controls_cases`.

## 5. SC-6: SARIF identity under the matching key

The matching key is the tool name, the upload category, the rule ID, tachi's own `primaryLocationLineHash` and the repo-relative URI. The regroup pair (three runs, each the next one's baseline, correlation regrouping carried findings in run 2) was run through both stages, and the written SARIF files compared per file.

| File | Run 1 to run 2 (regroup) | Dropped out | Run 2 to run 3 (unchanged re-run) | Unique within each run |
|---|---|---|---|---|
| `risk-scores.sarif` | 9 findings present in run 1 and run 2, 0 lost their key | none missing | run 3 re-runs run 2: 10 keys equal, sets equal | 9 keys for 9 findings; 10 keys for 10 findings; 10 keys for 10 findings |
| `compensating-controls.sarif` | 9 findings present in run 1 and run 2, 0 lost their key | none missing | run 3 re-runs run 2: 10 keys equal, sets equal | 9 keys for 9 findings; 10 keys for 10 findings; 10 keys for 10 findings |

- **The tool and category pairs differ:** `Tachi` with `threat-model`, `tachi-risk-scorer` with `risk-score`, and `tachi-control-analyzer` with `compensating-controls`. The first is the shipped `threats.sarif`'s tool, which PR 1 doesn't change.
- **The instrument can see a change.** The pair's baseline `risk-scores.sarif` is a v4.48.4 file with the legacy hash. 9 of 9 pre-fix findings re-keyed once, in run 1 (the release notes' one re-key event).
- **Correlation is untouched** (S-7): each run's groups and primaries, read from the SARIF, equal the outcomes file's (run 2's primary of CG-1 moves from I-1 to T-1, and the keys don't).
- **At scale** (`base-carry`, the base set run twice, the second with the first as its baseline): scorer file, 408 findings present in both runs, 0 lost their key; controls file, 408 findings in both runs, 0 lost their key.
- **Across interpreters.** The hash is the same on Python 3.11.13 and 3.9.6: all 63 scorer and controls files are byte-identical, `primaryLocationLineHash` included.

## 6. US-1a #4 and #5: stale, invalid and missing parts, and a lineage that can't be recovered

These ran on the gated subset (the scorer plans 3 batches, the controls stage 4), in a project root that already held an earlier run's outputs, so that `fail`'s "earlier outputs come back" rule had something to keep. Each case starts a fresh plan. The scorer's and the controls stage's numbers are the same unless noted. The checks count is for both stages.

**US-1a #4, a batch whose part is missing, fails validation or carries another plan's ID**

| Case | What the scripts did | Checks passed |
|---|---|---|
| A part is missing (B002 never written) | `reconcile` exits 3 and `waves` lists only B002's two halves, `B002-1` and `B002-2`. B001 and B003 are in `done`, and their part files are byte-identical after the retry. The budget is charged 2 of its limit of 6. The record has the event `missing` and one retry with both children | 22/22 |
| A part fails validation (a vector that isn't CVSS 3.1; a status that isn't one of three) | `reconcile` exits 3 and lists B001 alone, as the same batch with `attempt` 2 and a new part path (`B001.a2.json`). The attempt-1 file stays on disk and is never counted, and none of its values reaches either output. Event `invalid` | 18/18 |
| A part carries a key that the renderer computes | Rejected as `invalid` (the key sets are closed), and the batch is retried in place | 16/16 |
| A part names other finding IDs than the batch's | Rejected as `invalid` and retried in place | 16/16 |
| A part is cut off (not JSON) | Event `unparseable`: B001 is halved into B001-1 and B001-2 (sizes within 1), each at attempt 2 | 14/14 |
| An agent hands back a `tachi.overflow/1` object | Event `overflow-reported`: halved, as for an unparseable part | 14/14 |
| A part carries another plan's ID; another slot holds another batch's part | A valid part of an earlier plan sits at B001's path, and B003's part at B002's. Both are `invalid` and both batches are listed again under their own IDs. The rest are left alone | 12/12 |
| The renderer is given a part that went stale, bad or missing after `reconcile` exited 0 | Another plan's part: exit 2. No file: exit 1. Not JSON: exit 2. A part that fails validation: exit 2. Each prints the four-line message with `Batch B001: <IDs>`. The earlier run's two files are byte-identical afterwards and `staged/` is empty. With the good part restored, the same plan renders. A plan that was never reconciled is refused with exit 2 (`batch B001 is pending`) | 16/16 |

In every recovered case the stage then finished with exit 0 on `reconcile` and rendered with exit 0 or 5, and its outputs passed the same row-parity and N/N checks as a clean run.

**The retry cap.** Two limits end a lineage, and both were reached. A batch at attempt 3 gets no retry (below). And the budget, twice the planned batches, can run out first: with every batch missing, the 6 halvings of round 1 spend it, round 2's retries are refused, `reconcile` exits 4 and lists all 6 lineages in plan order. Its stderr says `(6 batches in all ran out of retries)`, and `fail` then names the first (`B001-1`) and counts them all in `batches.exhausted` (8/8 checks).

**US-1a #5, a batch that can't be recovered within the retry cap**

B001 was made invalid at attempts 1, 2 and 3. `reconcile` exited 3, 3 and 4. At exit 4 it prints `status: exhausted` and `exhausted: [{batch_id: B001, finding_ids: [...]}]`, and its stderr is the four-line message: the stage, the batch with its finding IDs, the remedy and the kept plan directory. B001's lineage stops at attempt 3, in state `failed`. Then:

| Step | What the scripts did | Checks passed |
|---|---|---|
| `fail --reason unrecoverable-batch` | Exit 0, as the contract lists. The stage record is `failed`, with `error.code` `unrecoverable-batch`, `error.batch_id` B001, all 11 of B001's finding IDs, a remedy, and `batches.exhausted` 1. `fail` prints the same four lines | 20/20 |
| With an earlier run's outputs in place | `moved` and `restored` are empty, and the earlier `.md` and `.sarif` are byte-identical to what they were. The earlier plan's directory is byte-identical too (KB 21's re-run moment). The renderer refuses the failed plan with exit 2 (`batch B001 is failed`) | in the row above |
| With no earlier outputs | None of `risk-scores.md`, `risk-scores.sarif`, `compensating-controls.md` and `compensating-controls.sarif` exists after `fail`. The controls `plan` that follows a failed scorer run exits 1, so a later command has no failed file to take as its input or its baseline | 18/18 and 1/1 |
| A render that finished, then judged failed (`fail --reason render-failed`) | Both canonical files move into the plan's `failed/` directory, byte-identical to what the render wrote, and the record's `outputs` lists them under `.tachi-build/`. With an earlier run in place its two files come back byte-identical (`restored` lists both). With none, the canonical names are empty. This is the "kept for diagnosis, marked failed" state | 10/10 and 10/10 |
| The other two reasons, and a guard | `agent-not-spawned --detail <agent>` and `check-failed` give exit 0 and a `failed` record, and the first names the agent on an `Agent:` line. A digest that differs gives exit 2, `moved` is empty, and the record is still written | 6/6 |
| A render that can't write its staged files | With `staged/` read-only the renderer exits 4 and names the cause, the canonical files are untouched, and `fail` then exits 0 | 6/6 |

US-1a #5's clauses, one by one:
- **The error names the stage, the batch, its finding IDs and the remedy:** the four-line message, from `reconcile` at exit 4 and again from `fail`.
- **The outputs stay for diagnosis but are marked failed:** the plan directory keeps every part, including each bad attempt's, and the stage record says `status: failed` with the error. When a render had finished, its two files are kept under `failed/` and listed in the record. A lineage that fails before the render has no new output to keep.
- **No later command takes them as input or as a baseline:** no canonical name ever holds a failed file. What `fail` puts back under those names is the earlier run's own pair, byte-identical, which is what a later command will read (KB 21's design). The failed run is visible there only in its stage record.

## 7. Exit codes against `contracts/cli.md`

Every process the run started was logged with its exit code, and each invocation's codes were compared with the contract's table. `Times seen` counts every call, the repeat runs of section 2 included. The rarer codes come from the failure cases of section 6, the checks of section 8 and a set of guard probes, one for each cause listed.

| Invocation | Contract code | Times seen | Cause in this run |
|---|--:|--:|---|
| `plan` | 0 | 183 | every scenario |
| `plan` | 1 | 5 | `--threats` names no file; controls `--target` isn't a directory; controls `--risk-scores` names nothing; `--out` doesn't exist (the command creates it first) |
| `plan` | 2 | 5 | a date that isn't a calendar date; the scorer without `--threats`; controls without `--target`; an unreadable Section 7 (S-12(c)); a usage error (no `--stage`) |
| `reconcile` | 0 | 167 | every complete plan, and a plan with no batches |
| `reconcile` | 1 | 1 | no plan pointer under `--out` |
| `reconcile` | 2 | 6 | a wrong digest; a `--plan` that disagrees with `current.json`; a malformed plan ID; an input or a batch input that changed since `plan`; a usage error |
| `reconcile` | 3 | 24 | a part that is missing, invalid, unparseable, overflowed or stale |
| `reconcile` | 4 | 6 | a lineage with no retry left |
| `fail` | 0 | 17 | all four reasons |
| `fail` | 2 | 3 | a digest that differs (the record is still written); a usage error (no `--reason`) |
| `render` | 0 | 2 | `--architecture` given, or the body line and the run's snapshot present |
| `render` | 1 | 4 | a part deleted after `reconcile`; `--out` not a directory; no plan |
| `render` | 2 | 17 | a stale, bad or unparseable part; a pending or failed batch; a wrong digest; a malformed plan ID; a control character in `threats.md` (P0-4); a usage error |
| `render` | 4 | 2 | the staged files can't be written |
| `render` | 5 | 162 | a warning only: O1's architecture-path warning, or a file the stage doesn't declare |
| `architecture-source` | 0 | 1 | the line written |
| `architecture-source` | 1 | 1 | `--threats` names no file |
| `architecture-source` | 2 | 1 | a usage error (no `--architecture`) |
| `architecture-source` | 5 | 1 | a path the resolver refuses: no line written, a warning |

Every code in the contract's list was returned at least once, and no process returned a code outside it (614 process calls logged). The one cause of exit 2 not reached is Python below 3.9: the host has no interpreter below 3.9, and `test_runtime_floor_374.py` owns that refusal. `--version` and `--help` exit 0 on all three entries.

## 8. Other checks run on the way

- **The fixture is what its generator makes.** `generate_large_arch_fixture.py --variant all` under Python 3.11.13 and under 3.9.6 writes 283 files and 7,048,389 bytes, and `diff -r` against the committed `tests/scripts/fixtures/large_arch/` is empty both times.
- **The commands' own flags.** With `--output-dir reports --baseline-dir baseline` for both stages, the input directory's tree digest is unchanged by both stages, and everything is written under `reports/`. A `fail` under `--output-dir` moves and restores inside it (KB 21's fourth moment: `moved` and `restored` both list the two scorer files, the earlier pair is back, and `run/` is still untouched). The same scenario under the defaults writes the same bytes (the scorer's two files and the controls SARIF are identical; the controls markdown differs only in the `source_file` line, which names the input's path).
- **Absolute paths.** Both stages with absolute `--out`, `--threats`, `--risk-scores` and `--target` write the same bytes as with relative ones (4 of 4 output files byte-identical), and no output file holds the working directory's path.
- **Exit 0 is reachable.** `--architecture` given: render exit 0, record `success`, no warning. Or `architecture-source` first, then the run's snapshot beside `threats.md`: render exit 0. Without either, every run exits 5 (O1).
- **A file the stage doesn't declare** (a `render_helper.py` dropped into `--out` after `plan`): render exit 5, status `success-with-warnings`, the file named in `undeclared_paths` and in the summary (FR-E.10, SC-3's "0 program files" signal).
- **A control character in `threats.md`** (U+0007 in a threat cell): `plan` exits 0, the agents run, `reconcile` exits 0 and the renderer refuses with exit 2, naming the finding and the field. No file holds the character. See O2.

## 9. Positive controls: the checks can fail

A clean report proves little unless the instrument could have shown a defect. Each case copies the finished files of the base set, the seeded-error run or the regroup pair, makes the one change that a real defect would make, and runs the check that guards that property. The check must fail, and the untouched copies must pass. The SC-4 row that puts back a stored, wrong composite is the "error carried forward silently" that the criterion exists to prevent.

| Mutation | Change | Check expected to fail | Result |
|---|---|---|---|
| none (control) | an untouched copy of the base set's four output files | none | passes, as it should |
| a composite score edited in risk-scores.md | S-1's Composite cell replaced by 0.1 | `S.md-sarif-agree`, `S.composite-is-weighted-sum`, `S.band-follows-composite`, `S.sect2-order` | caught |
| a SARIF result dropped (the N/N rule) | the last result of risk-scores.sarif removed | `S.sarif.nn`, `S.sarif-ids-equal-open` | caught |
| two present findings share a key | the second result takes the first's primaryLocationLineHash | `S.sarif.plh-unique` | caught |
| a case variant of the architecture URI | one result's uri spelled Docs/Security/Architecture.md | `S.sarif.uri-one-spelling` | caught |
| a total that is not the sum of its rows | Section 5's Total Residual Risk Score replaced by 1.0 | `C.totals-section5-sums` | caught |
| a headline count off by one | Section 1's Control Found count raised by 1 | `C.totals-section1-headline` | caught |
| a band table with a different schema | the first band table loses its CF column | `C.one-schema` | caught |
| a recommendation that joins no row | block 1's finding ID replaced by S-999 | `C.sect4-join-exactly` | caught |
| the SARIF residual differs from the markdown's | one result's residual-risk replaced by 0.1 | `C.md-sarif-agree` | caught |
| a blank recommendation in the SARIF | the first result that has a recommendation loses its text | `C.md-sarif-agree` | caught |
| none (SC-4 control) | an untouched copy of the seeded-error run | none | passes, as it should |
| a wrong composite is carried forward silently (SC-4) | AG-2 shows its stored composite 5.5, not the corrected 5.1 | `sc4.values` | caught |
| a seeded error is corrected but not flagged (SC-4) | AG-1 loses its score-flags in the SARIF | `sc4.flags` | caught |
| none (identity control) | the regroup pair's three runs as rendered | none | passes, as it should |
| a regroup moves a carried finding's key (scorer) | run 2's key for S-1 replaced | `risk-score.regroup-keeps-keys` | caught |
| an unchanged re-run changes a key (controls) | run 3's key for S-1 replaced | `compensating-controls.unchanged-rerun-identical` | caught |
| a still-present finding drops out | S-1 removed from run 2's scorer file | `risk-score.no-present-finding-drops-out` | caught |

## 10. Observations

- **O1. Every first-stage run exits 5.** No fixture `threats.md` carries FR-E.18's `**Architecture source**` line (the fixtures are v4.48.4-shaped), so each stage warns `architecture-path:body-line:absent` and falls back to `docs/security/architecture.md`, where the fixture's architecture is. The run completes either way. For T079: release-notes item 1 advises only the adopters whose architecture file is elsewhere, but any `threats.md` written before PR 1 has no such line, so every adopter sees this warning, and exit 5, on the first run after upgrading, at the default path too. The next `/tachi.threat-model` writes the line. Exit 0 appears once `--architecture` is passed, or the line and the run's snapshot are there (section 8). The live runs (T073, T074) will show the warning too.
- **O2. A forbidden character in `threats.md` is refused only at render.** The run spends every agent first. This is T064's SA-3 (the planner checks only a lone surrogate), observed again at the process level; ADR-050 D3 leaves it to W4's ruling, and T146 owns the fix: `scripts/tachi-stage.py`, with the shared predicate in `scripts/tachi_parts.py`.
- **O3. `base-carry` run 2 carries 41 `reused-id` flags.** The fixture's `threats.md` marks 41 findings NEW, and run 1 has already scored them, so their IDs are in the baseline: ruling B working as written. It is a property of reusing one `threats.md` as both runs, not of the code. The flags reach both files (scorer and controls).
- **O4. `ties/controls` can't reach its threat model.** Its `run/risk-scores.md` names `baseline/threats.md` as `source_file`, a file that scenario doesn't ship (its own is `run/threats.md`). The planner therefore warns `threats-unreadable`, every layer is `Unclassified`, and each unit holds the ID only, so the controls stage ran on the scored input alone and my agent read each row's component and threat from it. The R-11 residuals are right regardless. The scenario can't exercise the controls stage's threat-model join. Owner: `ties_controls_files` in `tests/scripts/generate_large_arch_fixture.py`, which reuses the baseline writer's `baseline/threats.md` constant; `source_file` should read `run/threats.md`. No in-process test runs this scenario through the controls renderer, so nothing noticed. Low.
- **O5. `plan` needs `--out` to exist** (exit 1, "is not a directory"); the commands create it first (Step 1, item 5). Nothing to change.
- **O6. Output size.** The base set's `risk-scores.md` is 1.32 MB against 697 KB for the pre-fix fixture's: Section 3's per-finding detail and Section 6's persisted inputs are new in schema 1.1. It is within `MAX_AGENT_INPUT_BYTES` (16 MiB) by a wide margin, and a later stage's `plan` read it without trouble.
- **O7. Wall time.** Each stage's script steps took 0.54 s and 0.67 s on the base set (scorer and controls). The longest run in the table is base-carry:run2's controls stage, 0.68 s. A live run's time is the agents'.

## 11. Hygiene

- **H1.** No pytest, extractor or renderer ran in a tracked tree. The scripts ran from project roots under the scratchpad, from a copy that the shipped installer wrote. The clone's `git status` is empty after all runs. The lane's worktree `git status --short` was empty before the first run, and after every pass it showed nothing but this record, once the record was in it.
- **H2.** No PDF baseline was regenerated, and nothing under `examples/` changed. No test was added: every case above is a process-level run of shipped code, and `test_render_risk_scores.py`, `test_render_compensating_controls.py`, `test_tachi_stage.py` and `test_sarif_identity.py` already pin the same properties in-process.
- **H8.** Fixture names only (the synthetic platform's components, `S-1`-style IDs). No path, company or real finding is in this record.
- **The driver** (the synthetic agents, the readers, the checks and the positive controls) is in the session scratchpad, not in the repository, as T065 asks. Its inputs are the committed fixture and the installed scripts, so a re-run is the sequence in section 1.
