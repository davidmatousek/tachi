# T066: the small-run oracle over the shipped examples (NFR-1), PR 1's W4

> **Two runs and a confirmation are recorded here.** The first run is dated 2026-11-23, at commit `f43440b`: everything from the first heading to section 10 below. The **W4 re-run** is dated 2026-11-24, at commit `d8cf928`, after T146's fixes and the PM's W4 rulings: the section after it, W4-1 to W4-10 (W4-10, the same day, applies the PM's re-run rulings R-H, R-I and R-J to the same renders). The **W6 merge-candidate confirmation** is dated 2026-11-24, at commit `ad64a72`: the last section, W6-1 to W6-7. The first run's sections are kept unchanged as the dated record.

**Date:** 2026-11-23. **Commit under test:** `f43440b`, PR 1's pushed W3 tip, so `tachi_parts.VERSION` is `4.48.4`. **Python:** 3.11.13. **Where it ran:** scratch clones and scratch work trees only, never a tracked tree (H1). **Method:** T058's, reused: the code ran from a clone of the committed tip, and every render went to a separate work tree that mirrors the examples' relative paths, so `examples/**` was never written. **Contract reading:** PM W3 rulings 2, 2b and 2c, and spec NFR-1's W3 errata (six value classes, the contract reading of "every field").

## Result: the oracle ran on all five examples. It is not clean: 1,090 value diffs are unattributed, and they go to the PM

| Question | Result |
|---|---|
| Examples | **5**, the ones with scorer and controls output: `agentic-app/sample-report`, `consumer-agent-app/sample-report`, `maestro-reference`, `mobile-banking-app/sample-report` and `predictive-ml-app/sample-report`. 20 files compared (4 each) |
| Runs | **Run A**, the primary: the scorer with the example's own shipped scorer files as its baseline, then the controls stage over the scorer's rendered `risk-scores.md`. All ten renders finished: exit 0 for agentic-app's two stages and exit 5 (done with warnings) for the other eight, the warnings being `value-not-in-form`, `tag-source:block-absent`, `duplicate-finding-id`, `reachability-defaulted` and `baseline-unresolved`. **Run B**: the scorer with no baseline, over the four examples whose judgment the shipped files can carry, to run class 5 and the PM's "no baseline" note |
| Value diffs, Run A | **4,040** in all. Class 1: 842. Class 2: 773. Class 3: 10. Class 4: 1,102. Class 5: 0 (it can't occur in Run A, see section 3). Class 6: 223. **Unattributed: 1,090**, in 17 groups (section 4) |
| Run B | agentic-app: 28 diffs fall in **class 5**, on the four findings that the PM's ruling 2b names (D-10, D-11, LLM-15 and LLM-16). Class 1 is empty there by construction, and the silent corrections it leaves are listed in section 6 |
| Dropped by a named decision | 6 scorer `relatedLocations` diffs, and `partialFingerprints.correlationGroup` and `baselineRunId` on 34 results, all removed by ADR-050 D8's ruling C placement (section 5) |
| Uncontracted keys | listed per example and file in section 7: 42 distinct keys. Their information is in a contract field, in `threats.md`, or in no rendered file by design (`feature`, `asi07_emission`, rule `name` and `help`) |
| S-12 (a) to (d) | asserted on the three drift-form examples, and all four hold (section 8) |
| Taxa pin | `tests/scripts/test_sarif_identity.py`, run in a scratch clone of `f43440b`: **662 passed** (class 6's test) |
| H1 and H2 | No pytest, extractor or renderer ran in a tracked tree. `git status` in the lane worktree shows this record and nothing under `examples/`, and the scratch clone stayed clean after every run. No PDF baseline was regenerated, and no tracked PNG changed |

**What most needs a ruling** (details and counts in section 4):
- **U-1, the MAESTRO layer (368 diffs).** In all five threat models the layer sits in a table that the renderer doesn't read, so every re-rendered finding reads `Unclassified` where the shipped file had `L7 — Agent Ecosystem` and the like. The shipped `maestro-layer` is a contract field, so this is a loss on old inputs.
- **U-2, the drift forms' threat text (91).** For a finding whose Section 7 lacks `threat`, S-12(b) supplies the baseline's Section 2 cell, which v4.48.4 cut at 60 characters. The rendered `message.text` and §2 cells are those 60 characters, where the shipped SARIF held the full sentence.
- **U-3, the unflagged rounding normalization (114).** D9 step 3 normalizes a rounding-only difference without a flag, and counts it. No class names it. Its count equals the rendered file's §6 line "Normalized (rounding only)" in all five examples.
- **U-4, shipped files that don't match their own `threats.md` (179).** An example problem, not a renderer one: maestro-reference's scorer SARIF scores 35 of 110 findings, and predictive-ml-app's shipped files list 12 IDs that its `threats.md` doesn't hold. U-17 is a sibling: four of the five shipped scorer files state a Section 1 severity count that their own rows don't give.

## 1. What ran, and which baseline each example used

Each example got a work tree that mirrors the repo: `threats.md` copied to the example's own directory, the example's `architecture.md` at its own repo path, and `--out` set to that same relative directory, so the `source_file` and the architecture URI read as they do in the repo. Every script ran as a process, the way the commands run it, from the work tree. The date is the shipped file's own frontmatter date.

| Example | Scorer baseline (Run A) | Controls baseline (Run A) | Why |
|---|---|---|---|
| `agentic-app` | **with**: the shipped `risk-scores.md` and `.sarif`, as a stand-in for the baseline run that its `baseline.source` names and no checkout holds | **with**: the shipped `compensating-controls.md` | The only delta-mode example (82 UNCHANGED, 4 NEW). The stand-in already holds the four NEW findings' rows, so the run flags them `reused-id` (4): an artifact of the stand-in. Run B runs it **without**, which is the state of any checkout (P0-9) |
| `consumer-agent-app`, `maestro-reference`, `mobile-banking-app`, `predictive-ml-app` | **with**: the example's own shipped scorer files | **without**: their Section 7 has no Status column, and a status that the form lacks is derived for the scorer alone (ADR-050 D2), so nothing is carried | Class 1 needs a stored value to flag against (PM ruling 2b's note). With the shipped file as the baseline, each finding that has a usable row is carried and any correction of a shipped slip is flagged. These four were generated with no baseline. With the shipped file as the baseline, the ±1.0 bound reaches only a NEW finding that has no row (predictive-ml-app's R-1 to R-7), so no bound appears that v4.48.4 didn't apply |

**What each run exercises.**
- **Run A** reaches the renderer's carry path for 82 + 19 + 110 + 31 + 30 findings. The synthetic agent wrote parts only for the findings that the planner sent it: D-10 in agentic-app (its three peers copy it) and R-1 to R-7 in predictive-ml-app. The controls stage sent its agent every finding, 283 in all.
- **Run B** sends every finding to the scorer's synthetic agent: 75 planned units in agentic-app, 19, 31 and 105. It carries the shipped vector, the sub-scores and the reachability inputs, and it is the run that the brief describes (plan, synthetic parts, reconcile, render).
- predictive-ml-app has no Run B: its shipped file holds no vector, and two of its CVSS scores (9.5 at T-5 and at T-10) are not CVSS 3.1 base scores that any vector gives.

**The agent's side, and what it can't carry.**
- **Scorer parts** carry the shipped vector (searched for a vector with the shipped base score where the file holds none: 7 findings in Run A, 75 in maestro-reference's Run B), four integers for each of Exploitability and Scalability, chosen so that their half-up mean is the shipped value (every shipped mean was representable), and barrier counts that reproduce the shipped Reachability through the documented formula. Seven findings' Reachability can't be reproduced that way: agentic-app T-6, I-6 and D-6 (2.0 in a Trusted zone) and four in maestro-reference's Run B. The shipped value is outside the formula, so the renderer's value differs from it in Run B (section 6). In Run A, predictive-ml-app's R-1 to R-7 have no zone at all (their component is unknown).
- **Narrative prose is not carried.** Each rationale field holds one digit-free sentence, so no run takes the numeral-ban fallback. The prose, the methodology and every frame heading of the markdown are not value-compared: PM ruling 2c names no slot-aware test for them. They are listed as out of scope in section 9.
- **Controls parts** carry the shipped status (from the SARIF, else the K8 reader), the shipped evidence entries and each §4 block's four keys. The evidence file is a copy of the example's `architecture.md` at each shipped evidence path, because these runs are architecture-only. Two things are synthetic: 33 evidence entries in agentic-app, for partial findings that the shipped SARIF gives none, and a status of `missing` for 7 findings that the shipped file doesn't hold (agentic-app T-1, predictive-ml-app R-2 to R-7). The `relatedLocations` of those 33 are not compared.

## 2. Diff counts by class, per example and file (Run A)

A value diff is one (finding, field) difference in one file, or one rule or run field. Rows that exist on one side only are counted under membership (U-4). Keys that only the rendered file carries are additive and aren't diffs (section 9).

| Example · file | 1 flagged | 2 D-5 | 3 S-2 order | 4 reference set | 5 bound | 6 fixed SARIF | unattributed | total |
|---|---|---|---|---|---|---|---|---|
| agentic-app · `risk-scores.md` | 143 | 0 | 1 | 94 | 0 | 0 | 66 | 304 |
| agentic-app · `risk-scores.sarif` | 61 | 206 | 1 | 172 | 0 | 39 | 60 | 539 |
| agentic-app · `compensating-controls.md` | 52 | 0 | 0 | 85 | 0 | 0 | 9 | 146 |
| agentic-app · `compensating-controls.sarif` | 76 | 206 | 0 | 172 | 0 | 38 | 61 | 553 |
| consumer-agent-app · `risk-scores.md` | 48 | 0 | 1 | 0 | 0 | 0 | 28 | 77 |
| consumer-agent-app · `risk-scores.sarif` | 20 | 38 | 1 | 19 | 0 | 20 | 45 | 143 |
| consumer-agent-app · `compensating-controls.md` | 18 | 0 | 0 | 0 | 0 | 0 | 8 | 26 |
| consumer-agent-app · `compensating-controls.sarif` | 27 | 38 | 0 | 0 | 0 | 8 | 52 | 125 |
| maestro-reference · `risk-scores.md` | 69 | 0 | 1 | 130 | 0 | 0 | 24 | 224 |
| maestro-reference · `risk-scores.sarif` | 42 | 35 | 1 | 62 | 0 | 42 | 118 | 300 |
| maestro-reference · `compensating-controls.md` | 34 | 0 | 0 | 108 | 0 | 0 | 9 | 151 |
| maestro-reference · `compensating-controls.sarif` | 47 | 110 | 0 | 105 | 0 | 23 | 281 | 566 |
| mobile-banking-app · `risk-scores.md` | 81 | 0 | 1 | 31 | 0 | 0 | 17 | 130 |
| mobile-banking-app · `risk-scores.sarif` | 37 | 31 | 1 | 62 | 0 | 35 | 36 | 202 |
| mobile-banking-app · `compensating-controls.md` | 29 | 0 | 0 | 31 | 0 | 0 | 12 | 72 |
| mobile-banking-app · `compensating-controls.sarif` | 41 | 31 | 0 | 31 | 0 | 10 | 88 | 201 |
| predictive-ml-app · `risk-scores.md` | 17 | 0 | 1 | 0 | 0 | 0 | 50 | 68 |
| predictive-ml-app · `risk-scores.sarif` | 0 | 41 | 1 | 0 | 0 | 4 | 44 | 90 |
| predictive-ml-app · `compensating-controls.md` | 0 | 0 | 0 | 0 | 0 | 0 | 36 | 36 |
| predictive-ml-app · `compensating-controls.sarif` | 0 | 37 | 0 | 0 | 0 | 4 | 44 | 85 |
| **All** | **842** | **773** | **10** | **1,102** | **0** | **223** | **1,088** | **4,038** |

Two more unattributed diffs come from a separate correlation check (U-16): 1,090 unattributed and 4,040 in all.

## 3. Each class: its test, and what passed it

- **Class 1, a flagged value (842).** The test: the rendered result carries a `corrected` or `retagged` flag on the field, and its correction record's stored value is the shipped value and its rendered value is the rendered one. By file: scorer SARIF `cvss-base-score` 72, `security-severity` 64, and 4 each of `severity-band`, `remediation-sla`, `risk-disposition`, `review-date` and `level`. Scorer markdown: 72 CVSS cells, 64 composite cells, 58 composite lines in §3, 65 and 58 weighted-table rows (CVSS and composite), 11 band and 11 SLA changes, 7 disposition and 4 review-date changes. Controls files: `inherent-risk` 63, `residual-risk` 62 and `security-severity` 62 (the residual), `level` 4, and the markdown's inherent 63, residual 62 and 4 each of inherent and residual severity. Each controls value follows the scorer's flagged composite and is checked against `inherent x (1 - factor)` on the shipped and the rendered side. Eight class-1 entries are order entries (pairs moved by a flagged score). The causes are the renderer's own: `corrected:cvss_base:vector` where a shipped score disagrees with its own vector, `corrected:composite_score:arithmetic`, and `follows-band`. No `retagged` case occurs, because no shipped example carries asset tags.
- **Class 2, D-5 identity (773).** `partialFingerprints.primaryLocationLineHash` 436 (equal to `sarif_common.primary_location_line_hash`), `locations[].uri` 229 (equal to the plan's architecture path), `ruleId` 83 and rule `id` 4 (equal to `rule_id_for`: agentic-app's short forms `tachi/ai/agentic` and `tachi/ai/llm`, and predictive-ml-app's `tachi/risk/*`), `findingId/v1` 19 (predictive-ml-app: the shipped results carry none, and the rendered value is Section 7's spelling) and `driver.name` 2 (predictive-ml-app's `Tachi-RiskScorer` and `Tachi-ControlAnalyzer`).
- **Class 3, S-2's tie order (10).** One per scorer file and example. In each, the rendered order was verified on the file as composite descending, then the S-2 total order, and every pair that the two files put the other way round has equal composites in both (agentic-app 13 pairs, consumer-agent-app 1, maestro-reference 57 in the markdown and 13 in the SARIF, mobile-banking-app 5, predictive-ml-app 10 and 2). Pairs moved by a flagged score are class 1 (the order entries in section 4 count them).
- **Class 4, text from the reference set (1,102).** `message.text` 374, `message.markdown` 249, §2 Threat cells 227 (shortened at 60 as `output-formatting.md` says), §2 Component cells 28 (at 30), the controls files' `threat` cells 224. Each rendered value equals the finding's reference-set value on decoded values. Where the form lacks the value, the test fails and the diff is U-2.
- **Class 5, P0-9's bound (0 in Run A, 28 in Run B).** In Run A every example has a usable baseline, so D-10 is bounded as it was in v4.48.4 and its values match. Run B (agentic-app, no baseline, stage record warning `baseline-unresolved`): D-10 renders `cvss_base` 9.3, and the shipped value is 8.5. The test holds for all four findings. The chain on D-10's own vector and tags without the bound gives 9.3, with the denial-of-service bound (6.5 to 8.5) it gives 8.5, and the record states the missing baseline. D-11, LLM-15 and LLM-16 are NEW peers that copy D-10's assessment (R-31), and carry the same pair. The 28 diffs are `cvss_base` and composite, in the SARIF (8) and in the markdown (20: the §2 cells, §3's composite line and both weighted-table rows). The band stays High, so no SLA, date or `level` moves.
- **Class 6, the renderers' fixed SARIF values (223).** Rule `fullDescription` 46, `properties.tags` 40, `relationships` 32, `shortDescription` 30 and rule `security-severity` 27, each equal to the 1.1 template's rule of the same `id`. Run level, per file: `taxonomies` and `supportedTaxonomies` 10 each, `semanticVersion` 10 and `version` 10 (equal to `tachi_parts.VERSION`), `informationUri` 6 and `$schema` 2. The same-in-every-file test holds: the five rendered scorer files share one run-level block and one body per rule `id`, and so do the five controls files.
  - **Decisions cited for a change from v4.48.4** (the class's own condition): `informationUri` is FR-E.9 (v4.48.4's placeholder); `version` and `semanticVersion` are PM W3 ruling 2c (shipped "1.0" or "1.1", and 2 files with no `version`); the taxa are W1's taxa reading; `relationships` are ruling 2's gap A (the shipped rules carry none, or the OWASP 2021 names). The two `$schema` diffs (maestro-reference and mobile-banking-app, which carry the older `master/Schemata` link) need no decision: the 1.0 template's own value is the renderer's constant, so the shipped link was agent drift.
  - **Rule `security-severity`** equals the highest result in the same rendered file (27 rules). One more rule is held out of the class by the chain condition: consumer-agent-app's elevation-of-privilege rule (6.1 to 6.0), in both files, because its highest result is E-1, whose composite diff is U-3's (counted under U-13).

## 4. The unattributed diffs, by cause

Each group names the evidence from the run, and the class that comes closest and why it doesn't apply. Nothing here is attributed by analogy. Counts are Run A diffs, per file kind.

| Group | What differs | Count (by example) | Evidence | Nearest class, and why not |
|---|---|---|---|---|
| **U-1** MAESTRO layer | `maestro-layer` (scorer and controls SARIF), §3's `MAESTRO Layer` line: the shipped layer string becomes `Unclassified` | 368: agentic-app 171, consumer-agent-app 16, maestro-reference 158, mobile-banking-app 23. By file: scorer SARIF 131, scorer markdown 70, controls SARIF 167 | In all five threat models the reference set (Section 7) holds no layer and the `### Components` table has no `MAESTRO Layer` column, so `finding_layer` and the component fallback are empty. The shipped string is in the finding's own row of the per-finding tables for 56 of 57 findings (agentic-app), 23 of 23 (mobile-banking-app) and 81 of 110 (maestro-reference), and, for consumer-agent-app, in its Phase 1 inventory and dispatch tables. predictive-ml-app's shipped files carry no `maestro-layer` (additive) | Class 4 needs the reference set to hold the value, and it doesn't. The field is a contract field that the shipped files carry (PM ruling 2, condition 1) |
| **U-2** drift-form text | `message.text` (scorer and controls SARIF) and the §2 Threat cell: the full shipped sentence becomes its first 57 characters and `...` | 91: consumer-agent-app 56, predictive-ml-app 35 | Section 7's list form lacks `threat` for all 19 and all 37 findings. The renderer supplies the baseline row's §2 cell (D9, S-12(b)), which v4.48.4 shortened to 60 characters. The same text feeds both controls files | Class 4: the reference set holds no value to equal. S-12(b) is the decision, and it names no class |
| **U-3** unflagged rounding normalization | A composite (and the band, SLA, `level`, weighted table and controls scores that follow it) one tenth apart, with the band unchanged and no flag | 114: agentic-app 11, consumer-agent-app 20, maestro-reference 19, mobile-banking-app 38, predictive-ml-app 26 (15 findings: 1, 2, 3, 4 and 5; these include 9 order entries) | D9 step 3: "a rounding-only difference ... is normalized and counted when the band holds". In the markdown, the number of unflagged `stored.composite` diffs equals the rendered §6's "Normalized (rounding only)" count in all five examples (1, 2, 3, 4 and 5), and each is one tenth with the band held | Class 1 needs a flag, and a normalization raises none. A seventh class, or a fold into class 1, is the PM's call |
| **U-4** membership | A result or row on one side only, a duplicate result in a shipped file, a section block count, or a Section 1 coverage count that follows a row set | 179: agentic-app 2, maestro-reference 79, mobile-banking-app 1 (a duplicate result, I-1), predictive-ml-app 97 | maestro-reference's shipped scorer SARIF holds 35 results where its markdown and `threats.md` hold 110, and its controls SARIF holds duplicates of AG-1 and R-6. predictive-ml-app's shipped scorer and controls files list 12 IDs (S-1 to S-4, T-1, I-1 and others) that no open row of its `threats.md` has, and omit 27 and 28 of the 37 that it does. agentic-app's controls markdown lacks T-1. The controls Section 1 coverage counts (agentic-app 55 missing for 53, maestro-reference 108 for 110, predictive-ml-app 43 for 37) follow those row sets. The renderer writes one result per open finding (D8's N/N rule) | None: the six classes cover values. D8 is the decision, and it says nothing of a file that predates its input |
| **U-5** zone label | `fullyQualifiedName`: the renderer keeps the zone label as §2 writes it | 106: maestro-reference, controls SARIF | 103 differ only by the label's layer note (`User Interface Zone (L7)` for `User Interface Zone`). 3 differ in the zone (T-14, I-14, D-14: `Deployment Infrastructure Zone (L4)` for `Data Operations Zone`). The shipped scorer SARIF's value matches | Class 4 covers the reference set, not §2's zone table |
| **U-6** recommendation text | The controls SARIF `recommendation` and one markdown cell: the shipped SARIF text differs from the shipped markdown's §4 text | 81: consumer-agent-app 19, maestro-reference 31, mobile-banking-app 31 | The synthetic part carries the markdown's "What to Implement" text, and the renderer reads the SARIF back from it, so the two files agree. The shipped SARIF and markdown disagree with each other | None: the field is agent text, and class 4 is the reference set |
| **U-7** logical-location `kind` | `kind`: `data-store` becomes `data`, and a shipped slip becomes the §1 type | 56: consumer-agent-app 12, maestro-reference 30, mobile-banking-app 14 | The rendered value is `KIND_OF_DFD_TYPE` of the component's §1 Type in all 56. 24 are `data-store` for `data` (ADR-050 D8: "a data store is written `data`"), and the rest are agent slips (a store written `process`, `database`, `module`) | Class 6's list is closed and doesn't name `kind`. D8 names the spelling |
| **U-8** start line | `locations[].region.startLine`: the shipped agent's line becomes 1 | 31: mobile-banking-app, controls SARIF (shipped values 18, 29, 23, 24 and others) | The renderer writes `REGION = {"startLine": 1}`, as S-6 and the 1.0 scorer contract say. It isn't part of D-5's matching key | Class 2 covers the matching key, and the line isn't in it |
| **U-9** sections and frames | A section only the rendered file has (`Score Integrity`, `Analysis Integrity`), and predictive-ml-app's shipped section names | 11: agentic-app 2, consumer-agent-app 2, maestro-reference 2, mobile-banking-app 2, predictive-ml-app 3 | The renderer adds 1.1's §6 and §7 (D9, D2). predictive-ml-app's two shipped titles (`Dimensional Breakdowns`, `Methodology`) read `Dimensional Breakdown` and `Scoring Methodology` in 1.1. No shipped section is missing in the rendered file | None: PM ruling 2c's note says the markdown's frame text has no test yet |
| **U-10** frontmatter | `schema_version` 1.0 to 1.1 (10, every file), `source_file` (consumer-agent-app, 2), `target_path` (4), `rescan_scope` and `carry_forward_count` (agentic-app and predictive-ml-app, 4) | 20 | D15 sets 1.1. The path values name where the run happened: consumer-agent-app's shipped `source_file` is `threats.md` and a `test-output` path, and the shipped `target_path` is free text where the controls run's `--target` is `.`. predictive-ml-app's controls run had no baseline, so its `rescan_scope` is `full` where the shipped file says `first-run`. agentic-app's shipped frontmatter says `incremental` and 84 carried, but none of its shipped rows carries a CF mark, so the synthetic agent carried none and the render says `full` and 0 | None |
| **U-11** evidence wording | `relatedLocations[].message`: `Control evidence: <category> detected in <file>` replaces the shipped agent's wording | 9: consumer-agent-app 1, mobile-banking-app 8 | The rendered text is `sarif_common.EVIDENCE_MESSAGE` with the category's display name | Class 6's list is closed and doesn't name it |
| **U-12** unsorted shipped files | Pairs of rows that the shipped file leaves out of composite order | 6 entries: agentic-app 6 pairs in each file, maestro-reference 244 (markdown) and 6 (SARIF), predictive-ml-app 45 and 2 | Neither composite differs between the files for any of these pairs, so the shipped order is not composite descending | Class 3 needs equal composites |
| **U-13** rule score through U-3 | consumer-agent-app's elevation-of-privilege rule `security-severity`, 6.1 to 6.0 | 2 | Section 3's chain condition: the rule's highest result is E-1, and E-1's diff is U-3 | Class 6's own condition |
| **U-14** default reachability | predictive-ml-app R-1 to R-7: the controls markdown's inherent and residual scores (4.5 to 5.0) | 2 (6 more diffs sit in U-4: the rows have no shipped counterpart in the scorer files) | Section 7's list form lacks `component` for R-1 to R-7 and the baseline has no row for them, so the stage warns `reachability-defaulted` and uses 5.0, where the shipped group row held 2.5 | Class 1 needs a flag, and the default raises a warning and a flag of kind `input` |
| **U-15** controls result with no status | agentic-app T-1 in the controls SARIF: `security-severity` 5.0 to 4.4 | 1 | The shipped result carries no status, inherent or residual, so the residual test can't run. The scorer diff for T-1 is class 1 | Class 1's test needs the stored value |
| **U-16** correlation group | maestro-reference E-7: the shipped result carries `correlationGroup` CG-2, and the rendered one carries no `correlation-*` property | 2 (scorer SARIF and controls SARIF) | Section 4a lists AG-7 in both CG-1 and CG-2. `parse_correlation_groups` keeps CG-1, and CG-2's other member is left ungrouped. The stage record counts the issue under `parse_errors` | Class 1 needs a flag. D8 names no rule for a finding in two groups |
| **U-17** Section 1 counts | The scorer's severity table: a band count differs | 11: agentic-app 2, maestro-reference 3, mobile-banking-app 2, predictive-ml-app 4 | The shipped Section 1 disagrees with its own rows in four of the five: agentic-app states 21 High and 67 Medium (88 findings) where its rows give 21 and 65; maestro-reference states 6, 96 and 6 where its rows give 6, 102 and 2; mobile-banking-app states 11 High and 19 Medium where its rows give 10 and 20; predictive-ml-app states 1, 27, 13 and 2 where its rows give 1, 26, 10 and 5. The rendered table equals its own rows in all five. consumer-agent-app's matches and shows no diff | Class 1: the rendered counts are what the flagged band changes give from the shipped rows, but the shipped table isn't those rows |

**Order entries in the table above.** Section 2's "unattributed" counts include the order entries of U-3 (9) and U-12 (6).

## 5. Contract fields removed by a named decision (not NFR-1 failures, under ruling 2's condition 1)

ADR-050 D8, ruling C's placement ("peers leave `relatedLocations`, and `correlationGroup` and `baselineRunId` leave `partialFingerprints`"):
- **`relatedLocations` on a scorer result** (v4.48.4's §10h peer references): maestro-reference, 6 results. The N/N rule makes each peer a result, so the information lives in `correlation-role` and `correlation-primary`.
- **`partialFingerprints.correlationGroup`**: maestro-reference, 6 scorer results and 9 controls results. The rendered `correlation-group` property equals it on 5 and 8 of them, and E-7 is U-16.
- **`partialFingerprints.baselineRunId`**: consumer-agent-app, 19 scorer results, every value the empty string, so no information is lost.

## 6. Run B: the scorer without a baseline (agentic-app, consumer-agent-app, mobile-banking-app, maestro-reference)

Class 1 is empty here by construction: no stored value exists to flag against (PM ruling 2b's note). Where the renderer fixes a shipped slip, no flag marks it, and the diff comes back unattributed with the record.

| Example | Planned units | Class counts (markdown / SARIF) | Silent corrections left unattributed |
|---|---|---|---|
| agentic-app | 75 of 86 | md: 4:94, 5:20, unattributed 254. SARIF: 2:206, 4:172, 5:8, 6:39, unattributed 138 | `cvss_base` 36 (with its 36 weighted-table rows), composite 37, Reachability 3 (T-6, I-6, D-6) |
| consumer-agent-app | 19 | md: unattributed 133. SARIF: 2:38, 4:19, 6:21, unattributed 113 | `cvss_base` 14, composite 13; also all 19 component cells and names (the list form lacks `component`, and with no baseline row nothing supplies it) |
| mobile-banking-app | 31 | md: 4:31, unattributed 95. SARIF: 2:31, 4:62, 6:35, unattributed 71 | `cvss_base` 18, composite 17, one band, SLA, disposition and review date |
| maestro-reference | 105 | md: 4:130, unattributed 99. SARIF: 2:35, 4:62, 6:43, unattributed 167 | `cvss_base` 16, composite 21 (16 in the SARIF), Reachability 4 |

In maestro-reference, 75 rows have a `cvss_vector` that the oracle searched for because the shipped file holds none; they count as additive here, not as diffs. The rest of Run B's unattributed diffs are the Run A groups again (U-1, U-4, U-7 and U-9 in particular). The drift forms (consumer-agent-app) show what S-12(b) gives with no baseline: every finding is scored fresh and flagged `input:<field>:not-in-form`, and nothing supplies the component or the threat.

## 7. Uncontracted keys, per example and file (PM ruling 2, condition 2)

Counts are over every result of the shipped file, not only the matched ones. A key marked "twin" duplicates a contract field under another spelling, and the oracle compared it as that field wherever the shipped file lacked the contract spelling (PM ruling 2, condition 3), so no value left the comparison.

**`risk-scores.sarif`: result properties**

| Key | Where (count) | Where its information is in the rendered run |
|---|---|---|
| `cvss_base`, `composite`, `severity_band` | agentic-app (86 each) | twins of `cvss-base-score`, `security-severity`, `severity-band` |
| `governance.owner`, `governance.sla_days`, `governance.disposition` | agentic-app (86 each) | twins of `risk-owner`, `remediation-sla`, `risk-disposition` |
| `id`, `cvss_base`, `composite`, `severity`, `sla_days`, `disposition` | predictive-ml-app (12, 12, 12, 12, 12, 12) | the finding ID in `partialFingerprints["findingId/v1"]`, and twins of `cvss-base-score`, `security-severity`, `severity-band`, `remediation-sla` and `risk-disposition` |
| `tags` | consumer-agent-app (19), maestro-reference (35) | the category is in `ruleId`, the layer in `maestro-layer`, the other two values are constants, and maestro-reference's `maestro-pattern:<p>` is in `threats.md`'s pattern column and `threats.sarif` |
| `owasp-reference` | agentic-app (7) | `threats.md`'s references and `threats.sarif`'s `owasp_id` (the shipped values hold 2025-edition codes) |
| `owasp_references` | predictive-ml-app (9) | `threats.sarif`'s `owasp_references` and `threats.md` |
| `source-attribution` | agentic-app (11) | `threats.md`'s Source Attribution block |
| `new-finding` | agentic-app (5) | `threats.md`'s delta status (AG-8's shipped `true` contradicts its `[UNCHANGED]`) |
| `asi07_emission`, `feature` | agentic-app (1 each, AG-8) | nowhere, by design: build markers |
| `locations[].logicalLocation` (singular) | agentic-app (86), mobile-banking-app (31) | twin of `logicalLocations`, compared as it (name, FQN, kind) |
| `partialFingerprints.baselineRunId`, `.correlationGroup` | consumer-agent-app (19), maestro-reference (6) | section 5 |

**`risk-scores.sarif`: rule keys.** `name` in agentic-app (8), maestro-reference (8) and mobile-banking-app (6) repeats the rule ID's category, and `help` in consumer-agent-app (7) is generic advice. Neither is in any contract, and neither is written (ruled out by PM ruling 2). `shortDescription`, `fullDescription`, `properties` and `relationships` are contract fields.

**`compensating-controls.sarif`: result properties**

| Key | Where (count) | Where its information is in the rendered run |
|---|---|---|
| `cvss_base`, `exploitability`, `scalability`, `reachability`, `composite`, `composite-weights`, `severity_band`, `cvss-base-score`, `cvss-vector`, `governance.owner`, `governance.sla_days`, `governance.disposition`, `review-date`, `risk-owner`, `remediation-sla`, `risk-disposition`, `score-source` | agentic-app (86 each) | the scorer's property set copied in. It lives in `risk-scores.sarif`, for the same finding |
| `inherent_score` (85), `control_status` (85), `residual_score` (85) | agentic-app | twins of `inherent-risk`, `control-status`, `residual-risk` |
| `inherent_severity`, `residual_severity` | agentic-app (85 each) | derived from `inherent-risk` and `residual-risk` by the band thresholds, and the residual one by `level` |
| `findingId` | agentic-app (86) | `partialFingerprints["findingId/v1"]` |
| `owasp-reference` (7), `source-attribution` (11), `new-finding` (5), `asi07_emission` (1), `feature` (1) | agentic-app | as in the scorer table above |
| `locations[].logicalLocation` (singular) | agentic-app (86) | twin of `logicalLocations` |
| `maestro-pattern` | maestro-reference (8) | `threats.md`'s pattern column and `threats.sarif` |
| `partialFingerprints.correlationGroup` | maestro-reference (9) | section 5 |
| `id`, `control_status`, `inherent_composite`, `residual_composite`, `severity` | predictive-ml-app (10 each) | the finding ID in `partialFingerprints`, and twins of `control-status`, `inherent-risk` and `residual-risk`; `severity` is the residual band, which `residual-risk` gives by the band thresholds |
| `owasp_references` | predictive-ml-app (9) | `threats.sarif`'s `owasp_references` and `threats.md` |

`consumer-agent-app` and `mobile-banking-app` carry no uncontracted controls key. The agentic-app controls file has 28 uncontracted result-property keys here, plus the singular `logicalLocation` twin. The PM's table counted 30 for it, and the one-key difference isn't traced. `maestro-layer` is a contract field in the controls file (gap B): all four shipped controls files that carry it keep it in the rendered file, with the diffs of U-1. Over both files and all five examples there are 42 distinct uncontracted keys.

**The markdown files.** No markdown field turned out to be uncontracted. The oracle read the fields that 1.0's templates and `output-formatting.md` name (the §2 table, §3's component, category, layer, composite, vector and weighted table, §4's governance table, §1's counts and the frontmatter). Shipped lines in another layout are U-9.

## 8. S-12 (a) to (d), asserted on the three drift-form examples

| | consumer-agent-app (Section 7 as a numbered list) | predictive-ml-app (numbered list) | maestro-reference's scorer file (table with no Status column) |
|---|---|---|---|
| **(a) the form is read** | `parse_reference_set` reads form `list`, 19 open. The tolerant baseline reader reads the shipped scorer file as legacy form, 19 rows | form `list`, 37 open. Legacy form, 42 rows (7 unreadable rows go to issues) | form `table`, 110 open (one duplicate, I-17: the first row is kept). Legacy form, 110 rows |
| **(b) missing values: derived or scored fresh, flagged, never stopped** | lacks `component`, `threat`, `delta_status` (19 each). All 19 carried from baseline rows. 57 `input:<field>:not-in-form` flags, warning `value-not-in-form`, exit 5 | lacks `component`, `threat`, `delta_status` (37) and `risk_level` (13). 30 carried, 7 scored fresh (R-1 to R-7, no row in the baseline). 125 `input` flags, warnings `value-not-in-form` and `reachability-defaulted`, exit 5 | lacks `delta_status` (110). All 110 carried. 110 `input` flags and 75 `unverifiable` flags (no vector), exit 5 |
| **(c) any other Section 7 stops early** | Section 7 replaced by prose: `plan` exits 2, writes nothing (no `.tachi-build` directory), and the message names the file, Section 7, the two expected forms and the remedy (`regenerate threats.md with /tachi.threat-model, or correct the section ...`) | the same | the same |
| **(d) a baseline that is present but unreadable counts as missing** | A binary file as `risk-scores.md`: `plan` exits 0 and warns that it "can't be read (not-utf8) ... every finding is scored fresh". 19 units. The render exits 5 with warning `baseline-unreadable`, and §6 says the owners, SLAs and dispositions weren't carried | the same, 27 units (10 peers copy their primaries) | the same, 105 units |

(b)'s "derives what it can from the baseline" held in each: a finding with a usable row was carried (UNCHANGED, derived once in `route_scorer_units`), and a finding without one (R-1 to R-7) was scored fresh and flagged.

## 9. Additive keys, and what the oracle can't see

**Additive** (the rendered file carries a contract key that the shipped file lacks; NFR-1 allows it): `affected_assets` on 95 scorer results (consumer-agent-app, maestro-reference, mobile-banking-app and predictive-ml-app, whose shipped files predate F-260b's key), P0-8's `message.markdown` on 169 controls results and 10 predictive-ml-app scorer results, the five controls properties `control-evidence`, `control-carry-forward`, `control-effectiveness`, `recommendation` and `effort-estimate` on agentic-app's 86 and predictive-ml-app's 9 shipped results that lack them, predictive-ml-app's whole `locations` block, `cvss-vector`, `composite-weights`, `risk-owner`, `review-date` and `maestro-layer` on its 10 scorer and 9 controls results, `score-flags`, `score-corrections` and `score-source`, `integrity-flags`, the provenance stamp, §2a, §6 and §7. In predictive-ml-app's markdown, 27 rendered rows have no shipped counterpart, so their owner and review date have nothing to compare.

**What this oracle can't see:**
- Narrative prose and frame text (U-9). The markdown has no slot-aware test yet, so the rationale paragraphs, the methodology and the headings aren't value-compared.
- A fresh finding's sub-scores. The shipped files hold the means only, so the parts carry integers that give those means. Run A carries 82 + 19 + 110 + 31 + 30 findings through the carry path, which reads stored means and never needs the sub-scores.
- The controls stage in Run B. It ran in Run A only.
- The PDF and the infographics. T058's oracle covers the extractors' data layer.
- Python 3.9. Every run used 3.11.13.
- A real target codebase. The controls runs are architecture-only, like the shipped files, and every evidence path is a copy of the example's `architecture.md`.

## 10. Re-running

The harness is scratch code, not a tracked file. Its steps:
1. Clone the committed tip into a scratch directory (`git clone --shared`), and check out the commit. Run the taxa pin there: `python -m pytest tests/scripts/test_sarif_identity.py`.
2. For each example, make a fresh work tree. Copy in the example's `threats.md` and its parent `architecture.md` at their repo paths, and the shipped scorer files into `baseline/` for a baseline run.
3. From the work tree, run `tachi-stage.py plan --stage risk-score --out <the example's directory> --date <the shipped date> --threats <its threats.md> --architecture <its architecture.md> [--baseline-dir baseline]`. Write a part for every batch input, reconcile, then run `render-risk-scores.py`. Repeat for `compensating-controls` with `--risk-scores <the rendered file> --target .`.
4. Read the rendered and shipped SARIF as JSON and the markdown through `read_baseline_scores`, `parse_compensating_controls_md` and `parse_markdown_table`, and attribute each diff by the tests in section 3.
5. `git status` stays empty in the clone and in the lane worktree. A render goes to the work tree, never to `examples/`, so #365's PNG re-render can't happen.


---

## W4 re-run (2026-11-24): the oracle after T146 and the PM's W4 rulings

**Commit under test:** `d8cf928`, the W4 preview: PR 1's W3 tip with T146's fixes (FX-1 to FX-7), U-1's layer reader `tachi_parsers.parse_finding_layers`, R-F's repeated-member report, and the PM's W4 errata in the spec. `tachi_parts.VERSION` is `4.48.4`. **Python:** 3.11.13. **Where it ran:** scratch clones only (H1): one for the renders and one for the taxa pin, both clean afterwards. **Method:** the first run's (its sections 1 and 10), with the scratch harness copied rather than edited, so the first run's evidence stays. **Contract reading:** the spec's eleven classes (W3 errata plus W4 errata R-A to R-G), the example-defect table closed at five groups, and the gating rule: Run A gates, Run B gates the fifth class, and each other Run B diff takes the disposition of the identical Run A diff (same finding, field, shipped value and rendered value).

### Result under the PM's re-run rulings R-H, R-I and R-J (2026-11-24, W4-10): Run A and Run B are clean

*As first recorded the same day, before the PM's re-run rulings R-H and R-I: not clean. Run A leaves 81 diffs unattributed, all of one cause, and Run B returns 80 value diffs on 10 findings. The table below is that first reading, kept as the record.*

*After R-H and R-I, before R-J (2026-11-24, W4-10's first pass): Run A is clean (class 8 at 102, unattributed 0), and Run B returns 4 value diffs on 1 finding (TE-4's composite) to the PM, with its fifth class at 114 value diffs where the ruling counted 118.*

**Under R-H, R-I and R-J (2026-11-24, W4-10):** Run A's class 8 is 102 and its unattributed count 0. Run B's fifth class takes 118 value diffs (114 alone, and 4 joint with class 7: TE-4's composite, under R-J) and 4 aggregated entries alone (6 more are joint with another class). 0 value diffs and 0 aggregated entries go back to the PM.

| Question | Result |
|---|---|
| Examples and runs | 5 examples, 20 files, as before. **Run A** (the gate) and **Run B** (no baseline; agentic-app, consumer-agent-app, mobile-banking-app, maestro-reference). All ten Run A renders finished with the first run's exit codes: 0 for agentic-app's two stages, 5 for the other eight |
| Run A value diffs | **3,834**. In the eleven classes: 3,547 (class 1: 844, 2: 773, 3: 10, 4: 1,438, 5: 0, 6: 265, 7: 112, 8: 21, 9: 2, 10: 2, 11: 80). Five row-order entries follow two attributed classes (1 and 7). Example table: 195. Dropped by a named decision: 6. **Unattributed: 81** |
| The 81 | agentic-app's `compensating-controls.md`, section 2, the `CF` cell of 81 rows. They are the by-product of the architect's harness fix 2, which carries the UNCHANGED findings that the shipped controls file holds. Without fix 2, Run A is clean (W4-7, item 6) |
| U-1's residual | 368 falls to **83**, with the predicted distribution (W4-4). No deviation |
| Empty layer chain | **26** values, the PM's list exactly (W4-4). No other |
| Example-defect table | U-4 178, U-12 6, U-15 1, U-17 10, and the fifth group's 7 findings. Nothing outside the five groups, no group rises, every entry passes both tests (W4-5) |
| Run B | 1,930 value diffs. Class 5: 38. By identity with a Run A diff: 1,635. Own groups: 161. A rule's score through its attributed results (class 6's clause): 16. **Back to the PM: 80, on 10 findings** (W4-6) |
| U-6 after FX-1 and FX-5 | No value moved (W4-8) |
| Taxa pin | `tests/scripts/test_sarif_identity.py`, run in a scratch clone of `d8cf928`: **709 passed** (class 6's test) |
| H1 and H2 | No pytest, extractor or renderer ran in a tracked tree. `git status` in the lane shows this record and nothing under `examples/`, and no PDF or PNG moved. Both scratch clones stayed clean |

### W4-1. What changed in the harness

**The architect's three fixes** (the triage's "three harness artifacts"):
1. **The 700-character clip is gone.** The synthetic controls agent carries each shipped `What to Implement` text whole. The one markdown cell that differed (mobile-banking-app T-4) no longer does.
2. **The UNCHANGED findings that the shipped controls file holds are carried.** In agentic-app that is 81 findings (82 UNCHANGED, minus T-1, which the shipped file lacks). `rescan_scope` now matches. `carry_forward_count` is still a diff, in class 8 (W4-3).
3. **The rendered-only sections are additive**: `Score Integrity` (5 files), `Analysis Integrity` (5) and predictive-ml-app's controls `Methodology` (1). A section that only the shipped file has is a drop; none occurs.

**The oracle's own readers** (never a function that a renderer calls to compute the field, PM W4 rulings R-A and R-G):
- a pipe-table reader that honours code fences and GFM `\|`, and reads a long row by its header's positions;
- the MAESTRO layer's chain (Section 7's cell, the finding's own row in a per-finding table, the component's Section 1 cell, `Unclassified`);
- the component's Section 1 Type through D8's closed map, and the Section 2 zone as that table writes it;
- S-12(b)'s supply from the baseline row (the §3 heading or line, else the §2 cell);
- Section 4a's groups under D8's rules, and the §4 blocks of a controls file;
- the nine-reference decoder of ADR-050 D3, one pass, and the severity bands, the residual formula and the exact composite.

The readers import nothing from `tachi_parsers`, `tachi_parts` or the renderers. The attribution code still takes from them: the reference set for class 4's signed text and for "Section 7's form lacks the value" (corroborated by the renderer's `input:<field>:not-in-form` flag), `tachi_parts`' ID helpers and S-2 key, the control-status classifier (for Section 1's status counts), and the constants that class 6 names as its sources. The first run's detection layer is unchanged in what it compares. Where it differs: full text values (no 100-character cut), headings compared by section number, correlation properties compared, and each `relatedLocations` entry kept for class 6's test.

**One reading of class 5.** A finding is NEW when Section 7 says so, or when its form lacks the status and no baseline row supplies one (S-12(b)). The first run read Section 7's status only, so consumer-agent-app's T-3 and I-1 were missed in Run B.

### W4-2. Diff counts by class, per example and file (Run A)

Columns are the classes 1 to 11, then E (the example table), D (dropped by a named decision), J (the joint order entries) and U (unattributed). A value diff is one (finding, field) difference; the row-order and Section 1 entries are counted per file and type, as in the first run.

| Example · file | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | E | D | J | U | total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| agentic-app · `risk-scores.md` | 144 | 0 | 1 | 95 | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 2 | 0 | 1 | 0 | 247 |
| agentic-app · `risk-scores.sarif` | 61 | 206 | 1 | 173 | 0 | 39 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 483 |
| agentic-app · `compensating-controls.md` | 52 | 0 | 0 | 85 | 0 | 0 | 2 | 3 | 0 | 0 | 0 | 2 | 0 | 0 | 81 | 225 |
| agentic-app · `compensating-controls.sarif` | 76 | 206 | 0 | 173 | 0 | 38 | 3 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 497 |
| consumer-agent-app · `risk-scores.md` | 48 | 0 | 1 | 18 | 0 | 0 | 7 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 76 |
| consumer-agent-app · `risk-scores.sarif` | 20 | 38 | 1 | 60 | 0 | 21 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 143 |
| consumer-agent-app · `compensating-controls.md` | 18 | 0 | 0 | 0 | 0 | 0 | 4 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 |
| consumer-agent-app · `compensating-controls.sarif` | 27 | 38 | 0 | 25 | 0 | 10 | 6 | 0 | 0 | 0 | 19 | 0 | 0 | 0 | 0 | 125 |
| maestro-reference · `risk-scores.md` | 70 | 0 | 1 | 131 | 0 | 0 | 4 | 1 | 0 | 0 | 0 | 4 | 0 | 1 | 0 | 212 |
| maestro-reference · `risk-scores.sarif` | 42 | 35 | 1 | 72 | 0 | 42 | 0 | 0 | 0 | 1 | 0 | 76 | 6 | 0 | 0 | 275 |
| maestro-reference · `compensating-controls.md` | 34 | 0 | 0 | 108 | 0 | 0 | 6 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 150 |
| maestro-reference · `compensating-controls.sarif` | 47 | 110 | 0 | 271 | 0 | 23 | 9 | 0 | 0 | 1 | 31 | 2 | 0 | 0 | 0 | 494 |
| mobile-banking-app · `risk-scores.md` | 81 | 0 | 1 | 31 | 0 | 0 | 13 | 1 | 0 | 0 | 0 | 2 | 0 | 1 | 0 | 130 |
| mobile-banking-app · `risk-scores.sarif` | 37 | 31 | 1 | 70 | 0 | 35 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 180 |
| mobile-banking-app · `compensating-controls.md` | 29 | 0 | 0 | 31 | 0 | 0 | 8 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 70 |
| mobile-banking-app · `compensating-controls.sarif` | 41 | 31 | 0 | 60 | 0 | 49 | 12 | 0 | 0 | 0 | 30 | 1 | 0 | 0 | 0 | 224 |
| predictive-ml-app · `risk-scores.md` | 17 | 0 | 1 | 16 | 0 | 0 | 6 | 3 | 0 | 0 | 0 | 25 | 0 | 0 | 0 | 68 |
| predictive-ml-app · `risk-scores.sarif` | 0 | 41 | 1 | 10 | 0 | 4 | 4 | 0 | 0 | 0 | 0 | 30 | 0 | 0 | 0 | 90 |
| predictive-ml-app · `compensating-controls.md` | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 4 | 2 | 0 | 0 | 19 | 0 | 0 | 0 | 35 |
| predictive-ml-app · `compensating-controls.sarif` | 0 | 37 | 0 | 9 | 0 | 4 | 6 | 0 | 0 | 0 | 0 | 29 | 0 | 0 | 0 | 85 |
| **All** | **844** | **773** | **10** | **1,438** | **0** | **265** | **112** | **21** | **2** | **2** | **80** | **195** | **6** | **5** | **81** | **3,834** |

No diff passed the tests of two classes. The E column adds up to 195: U-4 178, U-12 6, U-15 1, U-17 10.

### W4-3. Each class: its test, and what passed it

- **Class 1, a flagged value (844).** The first run's test, unchanged: 842 as before, plus two Section 1 counts (the High band in agentic-app and in maestro-reference), where the shipped count equals its own rows and the gap is exactly the class-1 band moves.
- **Class 2, D-5 identity (773)** and **class 3, S-2's tie order (10).** Unchanged, with the same counts. Class 3's rendered order is verified as composite descending, then S-2, on each of the ten files.
- **Class 4, the reference set and R-A's added sources (1,438).**
  - *The signed text, 1,102* (unchanged): `message.text` 374, `message.markdown` 249, §2 Threat cells 227, §2 Component cells 28, the controls files' threat text 224.
  - *The added sources, 336*, each tested against the oracle's own reader: **the layer** 83 (the chain's step 2 gives 57 values, and its step 4, `Unclassified`, the 26 empty-chain values of W4-4); **S-12(b)'s supply** 91 (`message.text` 57, §2 Threat cells 27, §2 Component cells 7, each equal to the baseline row's §2 cell, after the documented cut at 60 and 30 characters, in consumer-agent-app and predictive-ml-app); **the kind** 56 (the component's Section 1 Type through D8's closed map); **the zone** 106 (maestro-reference's controls `fullyQualifiedName`, `<zone>/<component>` with the zone as Section 2 writes it).
  - *Agreement beyond the diffs:* the own readers agree with the renderers on every finding that has a source: layer 100% (the chain's step 2 on 85, 107, 31 and 37 findings of four examples; step 4 on agentic-app's AGP-01, maestro-reference's AGP-01 to AGP-03 and consumer-agent-app's 19), kind and zone 100%, and the supply on all 49 drift-form findings that a baseline row holds.
- **Class 5 (0 in Run A, 38 in Run B).** Run A can't show it (every example has a usable baseline). Run B: agentic-app's four findings (D-10, D-11, LLM-15 and LLM-16, 28 diffs, the first run's) and consumer-agent-app's T-3 and I-1 (10 diffs, NEW under S-12(b)), each with the three tests of the class text.
- **Class 6, the renderers' fixed SARIF values (265).** The first run's 223, plus R-B's two fields and the chain clause. `region`: 31 (mobile-banking-app's controls file; **all 566 rendered results** carry exactly `{"startLine": 1}`). The evidence message: 9 `relatedLocations` entries (consumer-agent-app 1, mobile-banking-app 8); **all 44 rendered entries** equal `sarif_common.EVIDENCE_MESSAGE` filled with the finding's control category (read from the rendered §2 cell) and the entry's file, and the template is the same in every file and v4.48.4's own template text (`<control-category>` and `<file-path>` for the two fills). The chain: consumer-agent-app's elevation-of-privilege rule, in both files (2), which follows E-1's class-7 composite.
- **Class 7, D9's rounding normalization (112, plus 5 joint order entries).** For each of the 15 findings, the oracle computes the exact composite from the rendered row's four dimensions and the weights 0.35, 0.30, 0.15 and 0.20; the rendered value is its half-up rounding, the shipped value is the other one-decimal neighbour, the bands are equal, and the finding carries no `corrected` or `retagged` flag on `composite_score`. The number of such findings equals §6's "Normalized (rounding only)" line in every example (1, 2, 3, 4 and 5). The values that follow, each by its own rule: 105 value diffs (scorer 39: §2 rows 15, SARIF 10, §3 lines 7 and weighted rows 7; controls 66: inherent, residual, `security-severity`) and 7 row-order entries. Findings: agentic-app S-6; consumer-agent-app E-1, TE-4; maestro-reference E-5, E-6, E-10; mobile-banking-app I-3, T-4, T-5, T-6; predictive-ml-app D-6, LLM-1, LLM-2, S-5, T-7. No renderer flag, as the PM ruled.
- **Class 8, the markdown frame values (21).** Rendered value equals its source exactly, and only `schema_version` differs from v4.48.4's own rule (D15); every other source is the 1.0 template's rule (its `source_file` and `target_path` placeholders, its `rescan_scope` and `carry_forward_count` definitions, its headings). Each diff with the shipped value's origin:

  | Key | Where | Shipped, rendered | Origin of the shipped value |
  |---|---|---|---|
  | `schema_version` | 10 files | `1.0`, `1.1` | v4.48.4's template value |
  | `source_file` | consumer-agent-app, scorer file | a bare file name, the plan's input path | the same file under another path |
  | `source_file` | consumer-agent-app, controls file | a path in the original run's output location, the plan's input path | not the example's copy |
  | `target_path` | agentic-app, consumer-agent-app, predictive-ml-app (controls) | free text, `.` | v4.48.4's agent wrote a description in place of the `--target` path |
  | `target_path` | mobile-banking-app (controls) | the architecture file's path, `.` | a path that the agent wrote, not the `--target` path |
  | `carry_forward_count` | agentic-app (controls) | 84, 81 | the baseline registry's size (the input threat model states "Baseline registry: 84 findings"); the shipped rows mark none with `CF`. The rendered 81 is the number of §2 rows that read `CF` |
  | `carry_forward_count`, `rescan_scope` | predictive-ml-app (controls) | 0 and `first-run`, `null` and `full` | outside the 1.0 template's rule (null when no baseline controls file resolved; `full` or `incremental`) |
  | heading of section 3, section 5 | predictive-ml-app (scorer) | `Dimensional Breakdowns` and `Methodology`, `Dimensional Breakdown` and `Scoring Methodology` | the agent's own titles; v4.48.4's template headings are the 1.1 template's |
- **Class 9, a drift-form finding that S-12(b) can't supply (2).** predictive-ml-app R-1 (its controls markdown row, inherent and residual): the finding carries `input:component:not-in-form`, the own baseline reader holds no row for it (the shipped group row's ID cell reads `R-1..R-7`), the stage record's `reachability-defaulted` warning names it, the rendered reachability is 5.0, and the composite is the documented formula on the rendered dimensions. R-2 to R-7 sit in the example table (U-4) because the shipped files hold no result or row for them. **A dependency:** the placeholders `Unspecified` and `No threat description.` are named in no contract, ADR, spec, skill or template text at `d8cf928` (they appear only in the renderers, the stage script and their tests), so this class compares against the strings in the PM's ruling. The architect's contract line has to land (W4-7, item 8).
- **Class 10, D8's group rules (2).** maestro-reference E-7 in the scorer and the controls SARIF: the shipped result carries CG-2; Section 4a lists AG-7 in CG-1 and in CG-2, CG-1 claims it, and CG-2 is left with E-7 alone and emits nothing. The oracle applied D8's rules to Section 4a for **all ten SARIF files** and the rendered `correlation-*` properties and ruling C's sentence match on every result (agentic-app 19, maestro-reference 10, predictive-ml-app 14 correlated results per file; the other two examples none). **R-F's report landed:** both renderers list AG-7 in Input Issues (the group that keeps it, the group that loses it, the group that falls away), and both stage records warn `correlation-member-repeated`. AG-7 is the only repeated ID in the five examples.
- **Class 11, the controls SARIF's text from its own §4 block (80).** `recommendation` in consumer-agent-app 19, maestro-reference 31, mobile-banking-app 30. The rendered value equals the rendered block's What to Implement text (own reader, decoded), and that text equals the shipped markdown's §4 text. No rendered value is empty where a block holds text, and no `effort-estimate` differs.

### W4-4. U-1's residual: 368 falls to 83

| Example | Scorer SARIF | Scorer markdown | Controls SARIF | Predicted |
|---|---|---|---|---|
| agentic-app | 1 | 1 | 1 | 1 / 1 / 1 |
| consumer-agent-app | 16 | 0 | 0 | 16 / 0 / 0 |
| maestro-reference | 3 | 1 | 37 | 3 / 1 / 37 |
| mobile-banking-app | 0 | 0 | 23 | 0 / 0 / 23 |
| predictive-ml-app | additive only | additive only | additive only | additive only |
| **Total** | 20 | 2 | 61 | **83** |

All 83 are in class 4 (R-A's layer source). By cause: **26** where the own reader finds no layer in any source of the chain; **31** maestro-reference controls values in which the shipped file wrote `L3 — Agent Frameworks` against its input's `L3 — Agent Framework`; **3** where it wrote `L2` against `L4`; **23** mobile-banking-app controls values in which the shipped file wrote `Unclassified` while its own scorer file held the layer (6 `L2`, 17 `L7`).

**The 26 empty-chain values, each by example, file and finding** (the shipped file held a layer, the rendered value is `Unclassified`, and the own reader finds none in Section 7, in any per-finding table or in Section 1):

| Example | Scorer SARIF | Scorer markdown (§3) | Controls SARIF | Values |
|---|---|---|---|---|
| agentic-app | AGP-01 | AGP-01 | AGP-01 | 3 |
| maestro-reference | AGP-01, AGP-02, AGP-03 | AGP-01 | AGP-01, AGP-02, AGP-03 | 7 |
| consumer-agent-app | S-1, S-2, T-1, T-3, I-1, I-3, R-1, R-2, D-1, D-3, E-1, TE-1 to TE-5 | none | none | 16 |

That is the PM's accepted list: agentic-app's AGP-01 (3), maestro-reference's AGP-01 to AGP-03 (7) and consumer-agent-app's 16. None other.

### W4-5. The example-defect table (closed at W4 to five groups)

Each entry passes both tests: the shipped file contradicts its own input or rows, shown mechanically; and the rendered side passes its own rule.

| Group | W4 count | Re-run | Test 1: the shipped file contradicts its input or rows | Test 2: the rendered side passes its rule |
|---|---|---|---|---|
| **U-4**, membership | 179 | **178** | maestro-reference's scorer SARIF holds 35 of its input's 110 open findings, and its controls SARIF 2 duplicate results (AG-1, R-6); mobile-banking-app's controls SARIF 1 (I-1); agentic-app's controls markdown lacks T-1; predictive-ml-app's shipped files list 12 IDs that no open row of its input has (2 in the scorer SARIF, 12 in each markdown file, 1 in the controls SARIF) and omit 27 (scorer SARIF), 7 (scorer markdown), 28 (controls SARIF) and 6 (controls markdown) of the 37 that it does | **all 20 rendered files** hold exactly their input's open set, by distinct `findingId/v1` or row (D8's N/N rule; for controls, the rendered `risk-scores.md`'s open rows) |
| **U-12**, unsorted | 6 | 6 | agentic-app (6 pairs in each file), maestro-reference (244 pairs in the markdown, 6 in the SARIF), predictive-ml-app (45 and 2): the pair's shipped order puts the lower composite first, and neither composite moved | the rendered order is composite descending, then S-2, verified on each of the six files |
| **U-15**, controls stub | 1 | 1 | agentic-app T-1: the shipped controls result holds no status, inherent or residual (or twins), and the shipped markdown has no row for it | the rendered inherent is the scorer's composite (4.4) and the residual is inherent × (1 − 0.00) for `missing` |
| **U-17**, Section 1 counts | 11 | **10** | the shipped count differs from its own rows' count in that band: agentic-app Medium; maestro-reference Medium and Low; mobile-banking-app High and Medium; predictive-ml-app High, Medium and Low (8 scorer entries); and, in the controls files, `total-missing` in agentic-app (55 stated, 52 rows) and maestro-reference (108 stated, 110 rows) | each rendered count equals its own rows' count, and the gap from the shipped rows is exactly the class-1 band moves plus the rows that only one file holds |
| **Reachability** (found in Run B) | 7 findings | 7 findings | agentic-app T-6, I-6, D-6 (shipped 2.0 in a Trusted zone) and maestro-reference S-1, S-2, R-1, R-2 (shipped 9.0 in an Untrusted zone): D2's formula gives 1.0, 1.5, 2.5 and 8.0, 8.5, 9.5 for barrier counts 0 to 3 and 0 to 3, so the shipped value is outside it | the rendered values (2.5 and 9.5) are in the formula's set, and each finding's composite follows each side's own dimensions |

**The counts moved inside the table, and none rose.** The first run's U-17 held 11 Section 1 counts, taken per file. This run tests each band by the architect's text, "the shipped §1 count for a band differs from its own rows' count in that band", and applies it to the controls files' coverage lines as well. So three entries leave U-17: agentic-app's and maestro-reference's High counts (the shipped count equals its rows, and the gap is the class-1 band moves: class 1) and predictive-ml-app's Critical count (it follows a row set: U-4). Two controls coverage lines leave U-4 for U-17, because the shipped count contradicts its own rows rather than following a row set. U-4 goes from 179 to 178, and U-17 from 11 to 10. The table's total falls by 2 (to class 1).

### W4-6. Run B: the scorer with no baseline

Run B gates class 5 and nothing else. The disposition of every other Run B diff is that of the identical Run A diff (same finding, field, shipped value and rendered value). The aggregated row-order and Section 1 entries are derived again from the dispositions that the row-level diffs took.

| Example | Value diffs | Class 5 | By identity | Own groups | Class 6 rule chain | Back to the PM |
|---|---|---|---|---|---|---|
| agentic-app | 817 | 28 | 710 (1: 194, 2: 206, 4: 268, 6: 37, 7: 4, 8: 1) | 21 (Reachability) | 2 | **56** |
| consumer-agent-app | 322 | 10 | 163 (1: 66, 2: 38, 4: 35, 6: 18, 7: 4, 8: 2) | 122 (placeholders, class 9) | 3 | **24** |
| mobile-banking-app | 300 | 0 | 295 (1: 116, 2: 31, 4: 101, 6: 30, 7: 16, 8: 1) | 0 | 5 | 0 |
| maestro-reference | 491 | 0 | 467 (1: 105, 2: 35, 4: 203, 6: 37, 7: 3, 8: 1, 10: 1, D: 6, U-4: 76) | 18 (Reachability) | 6 | 0 |
| **All** | **1,930** | **38** | **1,635** | **161** | **16** | **80** |

- **Class 5.** agentic-app's D-10, D-11, LLM-15 and LLM-16 (28 diffs: the rendered `cvss_base` is 9.3 and the shipped 8.5, the chain without and with the denial-of-service bound, and the stage record states the missing baseline), and consumer-agent-app's T-3 and I-1 (10 diffs, same test).
- **Own groups.** The out-of-formula Reachability goes to the example table (7 findings, section 5). consumer-agent-app's placeholders, `Unspecified` and `No threat description.` on all 19 findings, go to class 9, each flagged `input:<field>:not-in-form`.
- **The rule chain (16).** A rule's `security-severity` equals the highest rendered result's, and each result diff that moves it has a disposition. This is class 6's own clause, applied to Run B's dispositions. The PM may prefer to send these 16 back with the rest.
- **The aggregated entries.** All derive from row-level dispositions. Four return, because their members do: agentic-app's two row-order entries (the pairs that the 8 findings below move) and consumer-agent-app's High and Medium counts (TE-3's band change).

**Back to the PM: 80 value diffs, 10 findings.** agentic-app T-8, R-7, R-9, AG-7, LLM-3, LLM-9, LLM-11 and LLM-12 (7 diffs each: `cvss_base` and composite in the SARIF, the §2 row, §3's composite line and the two weighted rows) and consumer-agent-app TE-3 (17 diffs; its band moves from Medium to High) and TE-4 (7). Each has no identical Run A diff. In Run A the same finding is carried with the stored score and flagged `unchecked:cvss_base:bound-n17c` (the stored value can't be checked, because its assessed score isn't recorded and a ±1.0 bound may explain it). Run B has no stored value, so it scores the vector's chain without a bound. They fail class 5 as written, for two reasons: eight are UNCHANGED in Section 7 (not NEW), and for none does the shipped value equal the vector's chain under the category's ±1.0 bound (T-8: 8.5 against 8.1; R-7 and R-9: 6.5 against 4.3; LLM-3 and LLM-12: 6.5 against 8.3; AG-7, LLM-9, LLM-11, TE-3 and TE-4 fail the same test). Whether class 5 should cover a shipped value that Run A can only mark `unchecked` is the PM's ruling.

### W4-7. What comes back to the PM

W3's list stands, with "the six classes" read as the eleven classes and the example table, and W4's list follows.

1. **An empty-chain `Unclassified` beyond the 26:** none.
2. **U-1's residual:** 83, with the predicted distribution. No deviation.
3. **A value that moves when U-6 is re-run after FX-1 and FX-5:** none (W4-8).
4. **An example-table entry outside its five groups, a rising count, or a failed test:** none outside the five groups, no rising count, no failed test. The movement inside the table (U-4 179 to 178, U-17 11 to 10, two entries to class 1) is in W4-5, for acknowledgement.
5. **A Run B diff that no Run A diff matches and that isn't one of Run B's own groups: 80 value diffs on 10 findings, plus 4 aggregated entries that derive from them** (W4-6). The evidence is there, and the ruling needed is whether class 5 covers a shipped score that Run A can only flag `unchecked:cvss_base:bound-n17c`. The 16 rule-score diffs in the Run B table are a separate reading for the PM to accept.
6. **A diff that the three harness fixes leave behind: 81, from fix 2.**
   - *What they are.* agentic-app's `compensating-controls.md`, section 2, the `CF` cell of 81 rows. The shipped file's frontmatter says `rescan_scope: incremental` and `carry_forward_count: 84`, and its text says "84 findings carried forward", yet all 85 of its `CF` cells read `—`. With the fix, the rendered cells read `CF` on exactly the 81 findings that are UNCHANGED in Section 7 and that the shipped file holds (T-1 is UNCHANGED too, but the shipped file has no row for it).
   - *Why no class takes them.* Class 8 lists the count and the scope, not the cell that the count counts.
   - *The two ways out.* Either class 8's closed list gains the §2 `CF` cell (renderer-computed, ADR-050 D2; its test: the cell reads `CF` exactly for an UNCHANGED finding that the resolved baseline controls file holds; the shipped value's origin: the agent left every cell `—` against its own frontmatter), or the shipped file's contradiction of its own frontmatter becomes a sixth example-table group. **Or fix 2 goes:** run without it, Run A is clean for agentic-app (0 unattributed), and class 8 takes `rescan_scope` (`incremental` to `full`) and `carry_forward_count` (84 to 0, the 84 being the baseline registry's size).
   - Fixes 1 and 3 leave nothing behind.
7. **R-F's report, if the lead's re-pricing moves it out of PR 1:** it is in `d8cf928` and works (W4-3, class 10). Nothing to return.
8. **A dependency for PR 1's gate:** the architect's contract line for the placeholders is not in `d8cf928`. Class 9 compares against strings that no contract names (W4-3).

### W4-8. Other checks

- **U-6 after FX-1 and FX-5.** The first run's 271 `recommendation` diffs and this run's 270 are the same findings with the same values on both sides (compared on the first 100 characters, which the first run stored). The one that disappeared is the harness's clip (mobile-banking-app T-4's markdown cell). The 80 SARIF diffs pass class 11 on the full text. No value moved.
- **S-12 (a) to (d)** re-asserted on consumer-agent-app, predictive-ml-app and maestro-reference, and all four hold as in the first run's section 8: the forms read (list, list, table), the missing values flagged and never stopped (57, 125 and 110 `input` flags), any other Section 7 stops with exit 2 and no `.tachi-build` directory, and an unreadable baseline counts as missing (warning `baseline-unreadable`, §6 says the owners, SLAs and dispositions weren't carried).
- **Uncontracted keys** (PM W3 ruling 2, condition 2): re-derived, identical to the first run's section 7, key for key and count for count (53 file and key pairs, 38 distinct result-property names; with the two rule keys and the two retired fingerprint keys, the first run's 42). No new key, no dropped one.
- **Additive keys:** identical to the first run's section 9, plus the eleven rendered-only sections now listed one by one (harness fix 3).
- **Removed by a named decision** (first run, section 5): unchanged. The 6 scorer `relatedLocations` are D8's placement, and the group they named is now in the `correlation-*` properties.
- **The 1.1 SARIF templates' run-level blocks** (W3 ruling 2c, open): both templates now show `version` and `semanticVersion` as the release-version placeholder, and carry `supportedTaxonomies` and `taxonomies`.
- **Taxa pin:** 709 passed.

### W4-9. Re-running

The harness is scratch code, not tracked. This run's steps, over the first run's (its section 10):
1. Clone the committed tip into a scratch directory, and check out `d8cf928`. Run the taxa pin in a second clone, so the first stays clean.
2. Apply the three harness fixes (no clip; carry the UNCHANGED findings that the shipped controls file holds; the rendered-only sections are additive). Run A as before, then Run B (the scorer with no baseline).
3. Attribute each diff by the class tests above, with the oracle's own readers for the added class-4 sources and for class 11's block. Map each Run B diff to the identical Run A diff.
4. `git status` stays empty in both clones and in the lane worktree outside this record.

### W4-10. The PM's re-run rulings applied (R-H, R-I and R-J, 2026-11-24)

**What this is.** An attribution-only pass: the amended class tests, as spec NFR-1's W4 re-run errata word them, applied by the harness's attribution and report scripts over this re-run's existing renders. R-H and R-I were applied first; the PM's ruling R-J, on TE-4's composite, was applied later the same day and is recorded at the end of the TE-4 paragraph below. No render ran, no shipped code changed and no input moved. The commit under test, both runs' files and every other test are as in W4-1 to W4-9. Every disposition was compared before and after each application, and **only the intended ones moved**: for R-H and R-I, in Run A the 81 `CF` cells, and in Run B 76 value diffs, the 2 §1 counts that follow them, and the row-order entries that split by class; for R-J, 4 values (TE-4's composite) and nothing else.

| | As first recorded (W4-2, W4-6) | Under R-H and R-I (before R-J) | Under R-H, R-I and R-J |
|---|---|---|---|
| Run A, class 8 (the markdown frame values) | 21 | **102** | 102 |
| Run A, unattributed | 81 | **0** | 0 |
| Run A, value diffs in all | 3,834 | 3,834 | 3,834 |
| Run B, class 5, value diffs | 38 | **114** (38 under the signed text, 76 under the added case) | **118** (114 alone, 4 joint with class 7) |
| Run B, class 5, aggregated entries | 2 alone | **4 alone** (agentic-app's row order in each file, 46 pairs; consumer-agent-app's High and Medium §1 counts) and 6 joint with another class | the same |
| Run B, back to the PM, value diffs | 80 | **4** | **0** |
| Run B, back to the PM, aggregated entries | 4 | **0** | 0 |
| Run B, the other dispositions | identity 1,635; own groups 161; rule chain 16 | unchanged | unchanged |

The 4 aggregated entries that had returned are attributed. agentic-app's 68 unexplained pairs per file now sit in the class-5 entry (28 of them, making 46) and in three joint entries (classes 1 and 5: 32 pairs; 5 and 7: 2; 5 and the Reachability group: 6). consumer-agent-app's High and Medium counts follow TE-3's band move from Medium to High, so they are class 5. Run B's aggregated entries are 49 (45 before), none unattributed.

**R-H, the eighth class's `CF` test as applied.** agentic-app is the only example whose controls stage ran with a baseline controls file in this re-run. The other four ran fresh: their parts claim nothing, nothing is accepted, and their rendered §2 tables read `—` on every row (19, 110, 31 and 37 rows).
- *The source*, from the oracle's own readers: the accepted set is the findings whose controls part claims `carried_forward` and whose Section 7 status is UNCHANGED, when a baseline controls file resolved (the plan names one). The 8 part files (each batch's accepted attempt) hold 81 claims, all of them UNCHANGED. Section 7 has 82 UNCHANGED and 4 NEW; T-1 is the UNCHANGED finding that no part claims, and the shipped file has no row for it. Accepted: **81**. The oracle's Section 7 reader and the shared parser agree on every status.
- *The test*, on each cell: the rendered cell is `CF` for an accepted finding and `—` for every other row. The rendered §2 has 86 rows, with `CF` on exactly the 81 accepted findings (none extra, none missing) and `—` on the other 5. All 81 diffs pass. `carry_forward_count` is 81, equal to the `CF` cells, and `rescan_scope` is `incremental`, as W4-3 recorded. The controls stage record carries no `carried-forward-cleared` warning.
- *The shipped value's origin*, as class 8's table records each: the agent left every §2 cell `—` (0 of 85 rows read `CF`) against its own frontmatter (`carry_forward_count: 84`, `rescan_scope: incremental`) and its §1 note (84 findings carried forward). #364's regeneration replaces it.

**R-I, the fifth class's widened test as applied.** The two readings were already in the first re-run's tests (NEW through S-12(b); the disposition, the SARIF `level` and the §3 copies as values that follow). The added case runs only on a Run B score diff that no other disposition took (no identical Run A diff, and not an own group), which is why Run B's other dispositions did not move. For each such finding, conditions 1 to 4 are tested on the finding and condition 5 on each of its diffs:
1. The stage record states the missing baseline: `baseline-unresolved`, in both Run B stage records.
2. The rendered `cvss_base` equals the chain without any bound on the assessment the run used: the finding's own vector and tags, or for a peer (LLM-11, a peer of T-8 in Run B) its primary's assessment with its own tags, which are none.
3. The shipped value equals the chain on the finding's own vector (the shipped file's) and tags, held to a range from `cvss-vectors.md`'s table. The oracle's own reader reads the ranges and the prefix map, and agrees with `tachi_scoring` on all 8 ranges and 12 prefixes. All eight ranges are tried, and the categories that give the shipped value are listed.
4. In Run A the same finding is carried with the shipped `cvss_base`, flagged `unchecked:cvss_base:bound-n17c` where the range is another category's. The vector is the same in the shipped file, Run A and Run B.
5. The values that follow do so by their own rules: each side's composite is the formula on that side's own score and dimensions; the band follows it; the SLA, disposition and review date are the band's fresh governance at the run date; the SARIF `level` follows the band; the §2, §3 and SARIF copies read the same values; the weighted row reads each side's score, the weight 0.35 and their product to two decimals. This check accepts all 38 diffs that the signed text already takes, and rejects 76 of 76 variants with a score nudged by 1.0.

Ten findings pass conditions 1 to 4, and **76 of their 80 value diffs pass condition 5**:

| Example | Finding | Section 7 status | Shipped | Range that gives it (own category) | Run A | Run B | Diffs taken |
|---|---|---|---|---|---|---|---|
| agentic-app | T-8 | UNCHANGED | 8.5 | denial-of-service (tampering) | 8.5 | 9.9 | 7 of 7 |
| agentic-app | R-7 | UNCHANGED | 6.5 | denial-of-service (repudiation) | 6.5 | 4.3 | 7 of 7 |
| agentic-app | R-9 | UNCHANGED | 6.5 | denial-of-service (repudiation) | 6.5 | 4.3 | 7 of 7 |
| agentic-app | AG-7 | UNCHANGED | 8.5 | denial-of-service (agentic) | 8.5 | 9.9 | 7 of 7 |
| agentic-app | LLM-3 | UNCHANGED | 6.5 | denial-of-service (llm) | 6.5 | 5.3 | 7 of 7 |
| agentic-app | LLM-9 | UNCHANGED | 8.5 | denial-of-service (llm) | 8.5 | 9.9 | 7 of 7 |
| agentic-app | LLM-11 | UNCHANGED | 8.5 | denial-of-service (llm) | 8.5 | 9.9 (peer of T-8) | 7 of 7 |
| agentic-app | LLM-12 | UNCHANGED | 6.5 | denial-of-service (llm) | 6.5 | 5.3 | 7 of 7 |
| consumer-agent-app | TE-3 | absent from the form (derived NEW, S-12(b)) | 8.5 | denial-of-service (agentic) | 8.5 | 9.3 | 17 of 17 |
| consumer-agent-app | TE-4 | absent from the form (derived NEW, S-12(b)) | 8.5 | denial-of-service (agentic) | 8.5 | 9.3 | **3 of 7** (the other 4 under R-J, below) |

For all ten, the denial-of-service range (6.5 to 8.5) is the only one of the eight that gives the shipped value, and the finding's own category's clamp would give another: 8.1 for T-8, 4.3 for R-7 and R-9, 9.9 for AG-7, LLM-9 and LLM-11, 8.3 for LLM-3 and LLM-12, and 9.3 for TE-3 and TE-4. The own ranges are tampering 6.1 to 8.1 (T-8), repudiation 3.3 to 5.3 (R-7, R-9), agentic 8.9 to 10.0 (AG-7, TE-3, TE-4) and llm 8.3 to 10.0 (the LLM findings). Run A carries each of the ten at its shipped value and flags it `unchecked:cvss_base:bound-n17c`, because the range is another category's. The eight agentic-app findings take 7 diffs each (the score and the composite in the SARIF file and the §2 row, §3's Composite Score and its two weighted rows). TE-3 takes 17 (the score, the composite, the band, the SLA, the disposition, the review date and the `level`, across the SARIF file, the §2 row and §3), and its band moves from Medium to High.

**Where the count differs from the PM's: TE-4's composite, 4 value diffs.** The ruling's 118 includes 4 diffs that the test as worded doesn't take. They are TE-4's composite, shipped 6.5 and rendered 6.8, in the SARIF `security-severity`, the §2 row, §3's Composite Score and the weighted table's composite cell. TE-4's other 3 diffs (its score in the SARIF file, the §2 row and the weighted row) pass.
- *Why they fail condition 5.* On the shipped score (8.5) and the shipped dimensions, the formula gives exactly 6.550, which rounds half-up to 6.6. The shipped file holds 6.5, the other one-decimal neighbour. That is R-11's rounding-only difference, and it is why TE-4 is one of Run A's fifteen class 7 findings (the same finding and field in Run A: shipped 6.5, rendered 6.6, class 7). The rendered 6.8 is the formula, half-up, on the rendered score (9.3, exact 6.830), and both bands are Medium.
- *What they are.* One value with two attributed causes: class 7's rounding of the shipped value (6.5 to 6.6, Run A's own diff for this finding) and class 5's score (the formula on 8.5 against 9.3, 6.6 to 6.8). No identical Run A diff exists, because Run A's rendered value is 6.6. Class 7's own test fails on Run B's pair: it needs the shipped value to be the other neighbour of the rendered exact composite (6.830, neighbours 6.8 and 6.9), and 6.5 isn't. The W4 re-run supersede block lets a value that follows from attributed diffs take their dispositions, and names joint row-order entries, which have no value of their own. It doesn't say whether that reaches a value with one cause from each class, so I did not apply it.
- *If the PM rules them joint (classes 5 and 7):* Run B's class 5, with the joint, is 118, and the count back to the PM is 0. No other count moves.
- *2026-11-24, later the same day: the PM's ruling R-J (joint 5 and 7), applied.* All five conditions of the spec's test hold for each of TE-4's four composite values, each tested as the spec words it. (1) The score diff is the fifth class's, in Run B. (2) The shipped row (8.5, 7.0, 6.5, 2.5) gives exactly 6.550, with neighbours 6.5 and 6.6: the shipped 6.5 is the other neighbour of the half-up 6.6, and both are Medium. (3) In Run A each of the four copies is a class 7 diff from the same shipped 6.5 to the half-up 6.6. (4) The rendered row (9.3, 7.0, 6.5, 2.5) gives 6.830, whose half-up is the rendered 6.8, and the two rows differ in `cvss_base` alone. (5) All four copies (the SARIF `security-severity`, the §2 cell, §3's Composite Score and its weighted Composite cell) read 6.5 to 6.8. Each value counts once, in class 5, recorded as joint with class 7. **Run B's class 5 is 118 value diffs (114 alone, 4 joint with class 7) and 4 aggregated entries alone; 0 value diffs and 0 aggregated entries go back to the PM.** TE-4 is the only finding that the test touched. A comparison of every disposition before and after shows that only these 4 values moved: none in Run A, and in Run B no other value and no entry. A negative control breaks each condition in turn (11 in-memory perturbations, with the unbroken baseline as the twelfth case), and each is rejected as expected: a broken Run A leg rejects only its copy, and any other broken condition rejects all four.

**Back to the PM.** After R-J: none. At the first pass: (1) TE-4's four composite diffs, above. (2) Nothing else: no `CF` cell outside the accepted set, no no-baseline diff whose shipped score no documented range gives or whose finding Run A doesn't carry at the shipped value with the flag, and no other disposition moved in this pass.

**Where the oracle isn't independent, for these tests.** R-H: nowhere; the cells, the part files and Section 7's status come from the oracle's own readers. R-I: the CVSS chain, the composite and band formulas, the `level` map and the fresh-governance rule are the shipped modules' own, as the signed class 5's follow rules use them (each is pinned by its own tests). The ranges, the prefix map and Section 7's status come from the oracle's own readers. R-J: no shared piece beyond the detection layer that reads §3's copies for every class; the rows, the weights (0.35, 0.30, 0.15, 0.20), the half-up rounding and the bands are the oracle's own.

**Re-running.** After W4-9's step 3, apply the amended tests (R-H, R-I and R-J) and re-run the harness's attribution and its report scripts over the same renders. No render is needed.


---

## W6 merge-candidate confirmation (2026-11-24, ad64a72)

**Result: clean. On the merge candidate, Run A leaves 0 diffs unattributed, and Run B returns 0 value diffs and 0 aggregated entries to the PM. No value moved since the W4 re-run at `d8cf928`: all 28 rendered files are byte-identical to the re-run's, and so is every attribution record. P1-6: the eighth class's accepted set, derived with D2's held condition by the oracle's own readers, is 81 (R-H: 81), and it equals the harness's claims.**

**Commit under test:** `ad64a72`, the merge candidate: PR 1 after W6's P1 batch (`843ea01`) and the PM's W6 erratum on R-H, so `tachi_parts.VERSION` is still `4.48.4`. **Python:** 3.11.13, the interpreter that the harness's `env.sh` names. **Where it ran:** two fresh scratch clones of the commit (one for the renders and the attribution, one for the taxa pin) and scratch work trees for every render, never a tracked tree (H1). **Contract reading:** the W4 re-run's (the eleven classes with R-A to R-J, the example-defect table closed at five groups, and the gating rule: Run A gates, Run B gates the fifth class, and each other Run B diff takes the disposition of the identical Run A diff), plus the PM's W6 erratum under R-H (P1-6) and ruling Q3(a). **Why this run:** plan.md's Verification 7 holds the gate on the commit that PR 1 merges, so before W6 merges the oracle runs on the merge candidate, or its record shows that nothing its renders read or run has changed in a way that reaches the shipped examples. This record does both: the oracle ran on the candidate (W6-1 and W6-2), and W6-3 shows what each change since the re-run did.

| Question | Result |
|---|---|
| Examples and runs | 5 examples, 20 files, as at W4. **Run A** (the gate) over all five. **Run B** (no baseline) over the four whose shipped files can carry the judgment. The ten Run A renders finished with the re-run's exit codes: 0 for agentic-app's two stages, 5 for the other eight. Run B's four scorer renders exit 5 |
| Run A | **3,834** diffs in the eleven classes and the example table: the re-run's counts, cell for cell, with R-H's 81 read as class 8 (W6-2). **Unattributed: 0** |
| Run B | 1,930 value diffs: class 5 takes 118 (114 alone, 4 joint with class 7), identity with a Run A diff 1,635, Run B's own groups 161, a rule's score through its results 16. **To the PM: 0 value diffs, 0 aggregated entries** |
| A value that moved | **None.** Raw detection: the nine scenarios give 6,890 diffs, the same set as at `d8cf928` on file, scope, finding, field, shipped value and rendered value. Rendered files: 28 of 28 byte-identical, with the same permission bits. Stage records: 14 of 14 equal. All four attribution records are byte-identical. The one difference in the renderers' output is five lines of the scorer's stdout (P1-5's wording, W6-3) |
| P1-6 | Derived with D2's held condition from the oracle's own §2 and §7 readers: **81**, equal to the harness's claims (W6-4) |
| Uncontracted keys | No change: 53 (file kind, key) pairs, 38 distinct result-property names and the 2 rule keys (W6-5) |
| S-12 (a) to (d) | Re-asserted on the three drift-form examples: all four hold, with the re-run's results |
| Taxa pin | `tests/scripts/test_sarif_identity.py`, run in a scratch clone of `ad64a72`: **709 passed** (class 6's test, as at the re-run) |
| H1 and H2 | No pytest, extractor or renderer ran in a tracked tree. Both scratch clones and the lane worktree show nothing under `examples/`; no PDF baseline or PNG moved; neither clone holds a `__pycache__` or a cache directory |

### W6-1. What ran

1. **Two fresh scratch clones** (`git clone --shared --no-checkout`, then a detached checkout of `ad64a72`): the first for the renders and the attribution, the second for the taxa pin, so that the first stays clean (W4-9).
2. **The W4 re-run's harness with its three fixes**, copied into a new scratch directory and re-pointed at the new clone. The re-run's copy was not edited. The copy gained one opt-in switch in its controls driver, which adds extra `carried_forward` claims. It is unset in every gated run, and only P1-6's negative control uses it (W6-4).
3. **Run A and Run B** as W4-9's steps 2 and 3 describe: the scorer with each example's own shipped scorer files as its baseline and then the controls stage over the rendered `risk-scores.md` (agentic-app's controls stage reads its shipped controls file as the baseline, the other four run fresh), and the scorer with no baseline.
4. **The re-run's attribution and report steps, unchanged:** the class tests (W4-3), U-1's residual, the example-defect table, Run B's dispositions (W4-6), the R-H, R-I and R-J tests with their negative controls (W4-10), S-12 (a) to (d), and the taxa pin.
5. **Checks written for this run** (scratch only): the raw detection diffs, the rendered files, their permission bits, the stage records and the renderers' output streams, each compared with the re-run's; P1-6's derivation and its negative control; the census behind Q3(a).

### W6-2. Counts against W4-2

Run A's table (21 rows: each example and file, and the total, by classes 1 to 11, E, D, J and U) equals W4-2's in every cell. One reading is applied: W4-2 was recorded before R-H, and the 81 `CF` cells that it lists as unattributed in agentic-app's `compensating-controls.md` are class 8's since W4-10. The totals:

| | W4-2, as first recorded | W4-10 (R-H applied) | `ad64a72` |
|---|---|---|---|
| Class 1, a flagged value | 844 | 844 | 844 |
| Class 2, D-5 | 773 | 773 | 773 |
| Class 3, S-2's tie order | 10 | 10 | 10 |
| Class 4, the reference set and R-A's sources | 1,438 | 1,438 | 1,438 |
| Class 5, P0-9's bound | 0 | 0 | 0 |
| Class 6, fixed SARIF values | 265 | 265 | 265 |
| Class 7, D9's rounding normalization | 112 | 112 | 112 |
| Class 8, markdown frame values | 21 | 102 | **102** (21, and the 81 `CF` cells) |
| Class 9, a drift-form finding that S-12(b) can't supply | 2 | 2 | 2 |
| Class 10, D8's group rules | 2 | 2 | 2 |
| Class 11, controls text from its own §4 block | 80 | 80 | 80 |
| Example-defect table (U-4 178, U-12 6, U-15 1, U-17 10) | 195 | 195 | 195 |
| Dropped by a named decision (D8's placement) | 6 | 6 | 6 |
| Joint row-order entries | 5 | 5 | 5 |
| **Unattributed** | 81 | 0 | **0** |
| **All** | 3,834 | 3,834 | 3,834 |

The 3,834 are 3,784 value diffs and 50 row-order and §1 entries. The rest of W4-3 to W4-5 repeats:
- **U-1's residual** is 83 (scorer SARIF 20, scorer markdown 2, controls SARIF 61), with the predicted distribution. The empty-chain values are the PM's 26 and none other: agentic-app's AGP-01 (3 values), maestro-reference's AGP-01 to AGP-03 (7) and consumer-agent-app's 16.
- **The example-defect table** holds the same entries: U-4 178, U-12 6, U-15 1, U-17 10, and the fifth group's 7 findings (agentic-app T-6, I-6 and D-6; maestro-reference S-1, S-2, R-1 and R-2), which Run B shows. No group rises, and each entry passes both tests.
- **The own readers** agree with the renderers on every rendered result: the MAESTRO layer on all 566 results of the ten SARIF files, and the kind and the zone on every result whose component has a source (0 disagreements). All 566 results carry the region `{"startLine": 1}`, all 44 evidence messages equal `sarif_common.EVIDENCE_MESSAGE` filled from the entry, and D8's rules applied to Section 4a match all ten SARIF files (AG-7 in maestro-reference is the one ID that Section 4a lists twice, and both renderers still report it).
- **Every rendered file holds exactly its input's open set** (D8's N/N rule), in all 20 files.

**Run B**, with no baseline:

| Example | Value diffs | Class 5 | By identity | Own groups | A rule's score through its results | To the PM |
|---|---|---|---|---|---|---|
| agentic-app | 817 | 84 | 710 | 21 (Reachability) | 2 | 0 |
| consumer-agent-app | 322 | 34 (30 alone, 4 joint with class 7) | 163 | 122 (class 9) | 3 | 0 |
| mobile-banking-app | 300 | 0 | 295 | 0 | 5 | 0 |
| maestro-reference | 491 | 0 | 467 | 18 (Reachability) | 6 | 0 |
| **All** | **1,930** | **118** (114 alone, 4 joint) | **1,635** | **161** | **16** | **0** |

Run B's 49 aggregated entries (row order and §1 counts) all take a disposition: 4 in class 5 alone, and 6 joint with another class. The ten findings of W4-10's added-case table (agentic-app T-8, R-7, R-9, AG-7, LLM-3, LLM-9, LLM-11 and LLM-12; consumer-agent-app TE-3 and TE-4) pass again with the same shipped, Run A and Run B values. R-I's follow test takes the 38 signed-text diffs and rejects 76 of 76 variants with a score nudged by 1.0. R-J's twelve controls behave as expected, and TE-4's four composite copies are joint (5 and 7).

### W6-3. What changed since `d8cf928`, and what it did to the run

Between `d8cf928` and `ad64a72` no file under `examples/` changed, and `scripts/` changed in three commits only (`977a622`, `9bd337e` and `843ea01`). The renders themselves read nothing from the repository but their inputs and the scripts that run them (the oracle's own tests also read the 1.1 templates, the CVSS reference and the taxa catalogs). `843ea01` is W6's P1 batch: P1-2, P1-3, P1-4, P1-5 and EC-2. Each change, by what it can reach and what it did here:

| Change | What it can reach | What it did in this run |
|---|---|---|
| `977a622` (T146: R-F's report names no non-member for a group that falls away) | the repeated-member report, for an ID that isn't one of the run's open findings | Nothing. AG-7 in maestro-reference, the only repeated ID in the five examples, is an open finding, so the branch isn't taken: both renderers' Input Issues line and the `correlation-member-repeated` warning are unchanged |
| `9bd337e` (T146: the controls renderer accepts a carry claim only where the baseline holds it) | the controls renderer's acceptance of `carried_forward`, and `control-analyzer.md`'s and the shared contract's sentence | Nothing: all 81 claims of Run A are held by the shipped controls file, so none is cleared. 81 `CF` cells, `carry_forward_count` 81, no `carried-forward-cleared` warning (W6-4). The other four examples claim nothing |
| T147 (`1e3614a`) | agent and command text only (`risk-scorer.md`, `control-analyzer.md` and the two commands), no script | Nothing: the oracle's synthetic agent reads none of it, and no renderer does |
| P1-2 (`843ea01`): file modes | the permission bits of staged files and of `fail`'s restored pre-images | Nothing: a work tree holds no canonical file to inherit from, and all 28 rendered files have the re-run's bits (0644) |
| P1-3 (`843ea01`): GFM's escaped pipe in Section 7 | `parse_reference_set` and the layer chain's Section 7 cell | Nothing: none of the five threat models has an escaped pipe in its Section 7. The one in the five is in agentic-app's §4.2, a per-finding table that P1-3 leaves alone |
| P1-4 (`843ea01`): the effort check | the controls renderer's from-disk check of `effort-estimate`, which now reads the part's body | Nothing: a check, not a value. All five controls renders finish with the re-run's exit code and bytes |
| P1-5 (`843ea01`): template text and summary wording | the 1.1 risk-scores template's Source row, `output-formatting.md`, and the scorer renderer's summary line | **Five stdout lines**: "N findings carried from the baseline" is now "N findings scored from baseline inputs" (82, 19, 110, 31 and 30). No rendered file changes, and the markdown templates' headings, which class 8 reads, are unchanged |
| EC-2 (`843ea01`): the undeclared-paths key | both renderers' declared-paths check, for a file name that no plan could hold | Nothing: no work tree holds such a name, and none of the 14 stage records has an `undeclared-paths-*` warning |
| `bfe3e85` (docs: the controls template's `schema_version` row, D15) | one table cell's text in the 1.1 controls template | Nothing: a field definition, no heading. Class 6 reads the SARIF templates' rules, and class 8 the markdown templates' headings |

**New diffs: none.** Every diff of this run is a diff of the re-run, with the same finding, field, shipped value, rendered value and disposition, so no value needs a commit to explain it. The 14 stage records equal the re-run's, and the 14 renders' output streams differ from it only in P1-5's five lines.

### W6-4. P1-6: the eighth class's accepted set

**Method: derived**, and checked for equivalence with the harness's claims. The PM's W6 erratum under R-H (spec NFR-1; the architect's P1 checkpoint, P1-6) adds D2's held condition, as amended at W4 ("A claim needs a result to carry"), to the oracle's accepted set. The accepted set is the findings that are claimed, UNCHANGED in Section 7 and held by the resolved baseline controls file. The held set is read by the oracle's own pipe-table reader, split by `schema_version` as D2 splits it:
- **A 1.0 baseline** holds a result as a §2 row under one of the four `### <band> Residual Severity` headings. The shipped agentic-app controls file is 1.0, so this is the reading used: 85 findings (High 10, Medium 70, Low 5; it has no Critical heading). Its §7 has no Assessment Inputs, because a 1.0 file persists none.
- **A 1.1 baseline** holds a result as a `control_status` row in §7's `### Assessment Inputs`. No shipped file is 1.1, so the reader was tested on the rendered controls file: 86 findings, equal to its 86 §2 rows.

| Step | Count |
|---|---|
| Section 7 of the input threat model | 86 findings: 82 UNCHANGED, 4 NEW (D-10, D-11, LLM-15, LLM-16) |
| Held by the shipped controls file | 85 |
| UNCHANGED and held | 81 (T-1 is UNCHANGED, and the shipped file has no row for it; the four NEW findings are held but not UNCHANGED) |
| Claims in the eight accepted part files | 81, all UNCHANGED and all held |
| **Accepted: a baseline resolved, claimed, UNCHANGED, held** | **81** |
| R-H's two-condition set (claimed and UNCHANGED) | 81 |
| The most that D2 could accept if all 86 findings were claimed (UNCHANGED and held) | 81 |
| The rendered §2 | 86 rows: `CF` on the 81, the dash on the other 5 (T-1 and the four NEW findings) |
| `carry_forward_count` and `rescan_scope` | 81 (the number of `CF` cells) and `incremental` |
| The 81 `CF` diffs | each rendered cell equals its source (`CF` for an accepted finding, the dash for every other row): 81 of 81 pass, as class 8 |
| The controls stage record's warnings | none: no `carried-forward-cleared` |
| The other four examples | no baseline controls file resolved, so 0 claims and 0 accepted: every §2 cell reads the dash (19, 110, 31 and 37 rows), `carry_forward_count` is `null` and `rescan_scope` is `full` |

**Equivalence.** The held condition removes nothing from R-H's two-condition set, because the harness claims only findings that the shipped file holds (81 of 81). The two derivations agree here by the harness's choice, as the erratum says, and the set is 81 either way. R-H's accepted set doesn't change.

**A negative control, outside the gate.** A second controls run in a new scratch work tree claims two extra findings: T-1 (UNCHANGED, but the shipped file holds no result for it) and D-10 (NEW, held). The renderer clears both: the stage record warns `carried-forward-cleared`, the run exits 5, and the rendered `CF` cells stay at 81. That set equals the three-condition set (81) and not the two-condition one (82, which would accept T-1). So the held condition is live at `ad64a72`, and the oracle's derivation predicts what the renderer does. (The warning's parenthetical gives the first cleared finding's reason for the whole group, and the Input Issues line gives the rule.)

**Cross-check only, never a source.** `_baseline_held`, the renderer's reader, returns the same 85 findings as the oracle's reader on the shipped file. `parse_controls_assessment_inputs`, the planner's reader, returns the same 86 as the oracle's §7 reader on the rendered file.

**Where the oracle isn't independent, for this test:** nowhere. The held set, the claims, Section 7's statuses and the cells all come from the oracle's own readers.

### W6-5. Uncontracted keys (PM W3 ruling 2, condition 2)

**No change.** The key tables of all nine scenarios equal the re-run's, key for key and count for count: 53 (file kind, key) pairs (18 for the scorer SARIF, 35 for the controls SARIF), 38 distinct result-property names, and the 2 rule keys (`name` and `help`). Per example and file:

| Example | Scorer SARIF result keys | Controls SARIF result keys | Rule keys |
|---|---|---|---|
| agentic-app | 12 (627 occurrences) | 29 (2,084) | `name` (8, in each file) |
| consumer-agent-app | 1 (19): `tags` | none | `help` (7, scorer) |
| maestro-reference | 1 (35): `tags` | 1 (8): `maestro-pattern` | `name` (8, scorer) |
| mobile-banking-app | 1 (31): the singular `logicalLocation` | none | `name` (6, scorer) |
| predictive-ml-app | 7 (69): `id`, `cvss_base`, `composite`, `severity`, `sla_days`, `disposition`, `owasp_references` | 6 (54): `id`, `control_status`, `inherent_composite`, `residual_composite`, `severity`, `owasp_references` | none |

agentic-app's keys, with where their information is in the rendered run, are the first run's section 7 tables. The counts are over the results that match a rendered finding, as at the re-run. The first run's section 7 counted every shipped result, so it reads 12 and 10 for predictive-ml-app's six scorer keys and five controls keys, where the matched counts are 10 and 9 (the 2 and 1 results that carry IDs the input doesn't hold are U-4's). The key names are the same, and no other count differs. No new key appears and none drops out, so the PM's W3 disposition of the 42 keys stands.

### W6-6. Q3(a), and Q3(b)'s note

**Q3(a), the reading (PM W6 ruling).** A sub-section that no shipped file and no run writes is template reference text, not written. It counts as neither a value diff nor a drop: NFR-1 keeps only what a shipped file carries (PM W3 ruling 2, condition 1), so the renderer can't drop what no file holds. The four are the 1.1 scorer template's `Column Definitions`, `Field Definitions` and `Override Guidance`, and the 1.1 controls template's `Column Definitions`.
- **The census at `ad64a72`.** Each of the four headings was searched in all ten shipped scorer and controls files and in all fourteen rendered markdown files (Run A's ten and Run B's four scorer files), at any heading level and in any other line form. None holds any of the four. So each is "template reference text, not written": no diff, no drop, and no additive key.
- **The one reference sub-section that a shipped file carries**, the controls template's `Recommendation Field Definitions`, is in one shipped file (consumer-agent-app's). The renderer writes it in all five rendered controls files, so condition 1 holds for it: no drop, and additive in the other four.
- **A check outside the gate** (the oracle compares no sub-heading): of the 40 fixed sub-headings in the two 1.1 templates (17 scorer, 23 controls), none that a shipped file carries is missing from its render, except three band group headings in controls files: `Low Risk Gaps` (mobile-banking-app) and `Critical Residual Severity` and `Low Residual Severity` (predictive-ml-app). A band group appears only when a row falls in it, so these are instance structure: their rows sit under other bands in the render, or are U-4's IDs that the input doesn't hold.

**Q3(b)'s note.** Nothing to attribute: no shipped controls file lists a control that maps to no finding (the PM's check; the oracle's own count finds ten per-control blocks in three shipped files, each with at least one mapped finding, and the other two files' §3 list no control), so the oracle sees nothing and condition 1 doesn't fire. The change is ADR-050's Known-limitations line, "The controls file's §3 lists only mapped controls".

### W6-7. Hygiene, and what this result depends on

- **H1.** The renders, the attribution and every check ran from the first scratch clone and scratch work trees; the taxa pin ran in the second clone. `git status` shows nothing in either clone, even with ignored files, and the lane worktree shows this record and nothing else.
- **H2.** No PDF baseline was regenerated, no tracked PNG changed, and nothing under `examples/` changed anywhere (the renders went to work trees that mirror the examples' relative paths).
- **H8.** This section holds no local path, real target name or finding content, and no literal placeholder token.
- **The reach of this result.** It stands for any later commit that changes none of `scripts/` (the stage, the two renderers and the modules they import), `templates/tachi/output-schemas/`, `schemas/taxonomy/`, the CVSS reference that R-I's test reads (`.claude/skills/tachi-risk-scoring/references/cvss-vectors.md`), `tests/scripts/test_sarif_identity.py` and `examples/`. A commit that touches agent or command text, the ADR, the spec or the other records doesn't reach it: the oracle's synthetic agent reads none of them.
- **What the oracle can't see** is unchanged (section 9): narrative prose and frame text, a fresh finding's sub-scores, the controls stage in Run B, the PDF and the infographics, Python 3.9 (every run here used 3.11.13) and a real target codebase.
- **Re-running.** As W4-9's steps, from a fresh clone of the commit under test. The W4 copy of the harness is the starting point, and every directory name is new, because `rm -rf` is blocked.
