# T066: the small-run oracle over the shipped examples (NFR-1), PR 1's W4

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
