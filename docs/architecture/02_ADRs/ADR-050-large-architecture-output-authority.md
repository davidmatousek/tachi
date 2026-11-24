# ADR-050: Output Authority at Scale: Rendered Files, Batched Dispatch and Stable Alert Identity

**Status**: Accepted (provisional pre-PR; commit SHA filled at merge)
**Date**: 2026-11-22
**Deciders**: Architect (owner), Product Manager, Team-Lead
**Feature**: [374-large-architecture-pipeline-resilience](../../../specs/374-large-architecture-pipeline-resilience/spec.md) (PRD-374 §13, items 1–16; spec plan input P-1)
**Supersedes**: None in full. In part: [ADR-046](ADR-046-asset-tag-output-wiring.md) D1 and D4; [ADR-013](ADR-013-sarif-output-format-adoption.md) D1 (in part), D4 and D5, with D6 amended; [ADR-020](ADR-020-maestro-layer-classification.md) Phase 2 (in part: the boolean, the bound and the tie claim, D13). Each decision states its scope
**Superseded by**: None
**Related ADRs**:
- [ADR-046](ADR-046-asset-tag-output-wiring.md) (the authoring-tier boundary; its D5 "structural ideal" is adopted here);
- [ADR-013](ADR-013-sarif-output-format-adoption.md) (SARIF adoption);
- [ADR-049](ADR-049-privilege-contract-and-write-confinement.md) (confinement; D7 gains a dated note);
- [ADR-018](ADR-018-baseline-aware-pipeline-correlation.md) (baseline correlation; its delta classes are refined);
- [ADR-020](ADR-020-maestro-layer-classification.md) (Phase 2 cross-layer chains);
- [ADR-017](ADR-017-deterministic-infographic-extraction.md) (deterministic extraction; the precedent for D4's failure behavior, and D2's percentages);
- [ADR-024](ADR-024-owasp-aivss-evaluation.md) (scoring; unchanged);
- [ADR-026](ADR-026-pattern-classification-mechanism.md) (Phase 3.6; a dated note on its new place in the order, D13);
- [ADR-047](ADR-047-maestro-coverage-state-authority.md) (MAESTRO coverage authority; unchanged);
- [ADR-048](ADR-048-llm-top10-2026-alias-cutover.md) (OWASP 2026 tokens; the shipped emitters become enforcement points).

---

## Context

Two stock runs on large architectures failed silently (PRD-374 §1). Every LLM-authored stage assumed that its output fits one model response, and that its agent stays inside its contract. At scale neither held.
- **Overflow.** The threat report, the scorer and the control analyzer each overflowed one response.
- **Arithmetic.** A dropped finding, totals that didn't equal their rows, and composites inherited wrong for several runs all went unnoticed, because no code checks the arithmetic.
- **Improvisation.** When output didn't fit, agents left their contracts: stand-in agents, helper scripts and code handed back to the caller.
- **Alert identity.** The scorer and controls SARIF carry no fingerprint, so GitHub's upload action derives one from a line of the user's architecture file. `threats.sarif` shares one fingerprint across distinct findings. Alerts therefore close and reopen when nothing was fixed.

ADR-046 drew the authoring-tier line, under which production SARIF is LLM-authored and consistency is test-checked. It deferred a "structural ideal" in which code emits the files. This ADR adopts that ideal for the surfaces where the model can't be correct at scale. It also records the shared mechanism that makes batched, resumable, checkable authoring possible, and the alert-identity rules for all three SARIF files.

The bundle ships as two patch PRs (PRD ruling R-34):
- **PR 1** carries the cut line and Track R: the renderer, the scorer and controls contracts, and the parsers.
- **PR 2** carries Track O: the orchestrator, the report, the chain script and the checks.

Each decision names its track. PR 1 rests only on decisions tagged S (the cut line) or R, so that PR 2's size rests on rulings made now.

## Decision

| # | Decision | Track |
|---|---|---|
| D1 | Which surfaces leave the model tier | R (four scorer and controls files); O (`threats.sarif`, `threats.md` emission, report assembly, Phase 3.5) |
| D2 | The judgment/computation line, field by field | R |
| D3 | The part-file contract | S |
| D4 | Where each script runs, in what order, and how failure is marked | R, O |
| D5 | Scoring constants, arithmetic and the scoring-rules module | R |
| D6 | Batching, overflow and resume | S (planner, error); R and O (ownership) |
| D7 | SARIF identity | R (scorer, controls, the carrier); O (`threats.sarif`) |
| D8 | SARIF membership and the N/N rule | R, O |
| D9 | Score-inheritance mechanics | R |
| D10 | The exception rules | R |
| D11 | Dispatch records and the ID map | O |
| D12 | The provenance and completeness checks | O |
| D13 | Phase 3.5: the chain script and the outcome record | O |
| D14 | Report assembly and tree batches | O |
| D15 | Schema versions | R, O |
| D16 | Test and CI placement | S, R, O |

### D1: Which surfaces leave the model tier [Track: R for the four scorer and controls files; O for the rest]

- **Decision.**
  - **Rendered by shipped code, in PR 1:** `risk-scores.md`, `risk-scores.sarif`, `compensating-controls.md` and `compensating-controls.sarif`. The renderer owns each whole file.
    - *The exception (R-34):* controls Sections 2 and 4 stay model-authored inside the part files, against the single template. The renderer assembles them into the file, and every score and band in them is either filled by the renderer or checked by a shipped check (D2).
  - **Generated by shipped code, in PR 2:** `threats.sarif`, from the compiled `threats.md`, through the shared emitter that D7 and D8 define (SV-2a).
  - **Emitted in bounded parts and joined by a shipped step, in PR 2:** `threats.md`.
    - Its tables stay model-authored: SV-2b's table rendering isn't adopted in this bundle.
    - Phase 3's compilation stays in the model, with dispatch records and an ID map (D11).
    - Section 6's counts and percentages are checked against the reference set (FR-E.10), not computed.
  - **Assembled by a shipped step, in PR 2:** `threat-report.md`, from per-section and per-batch parts. Section 5 is assembled by copying the standalone tree files (D14).
  - **Computed by a shipped script, in PR 2:** Phase 3.5's chain formation (R-19 adopted). The script covers indexing, candidate links, assembly, deduplication, folding, the filter, ranking, IDs, surfacing, the chain-breaking heuristic, the bound and the outcome record. The model writes titles and narratives for the surfaced chains only (D13).
  - **Stays model-authored:** every judgment:
    - Phase 2's analyses, and Phase 3's deduplication and correlation;
    - dimension sub-scores, CVSS vectors, reachability inputs, rationale and narrative prose;
    - control status, evidence and recommendations;
    - the report's narrative sections;
    - Section 6's counts (checked).
  - **SV-2b is carved at the plan stage.** `threats.md`'s tables stay model-authored, so the bundle runs in the state that R-8 and FR-N4.2 describe for a carved SV-2b. The dispatch records are therefore per-dispatch manifests, not verbatim findings (D11). Verbatim records would add 60–80k tokens of orchestrator output, which only a code-compiled Phase 3 would offset (RK-4).
  - **The regeneration-tier generators.**
    - **Retired:** `scripts/generate-risk-scores-sarif.py`, at PR 1. `scripts/render-risk-scores.py` subsumes it, closing #357.
    - **Rewritten:** `scripts/generate-threats-sarif.py`, at PR 2, as the shipped `threats.sarif` generator: installed, and on the shared emitter.
    - **Installed:** `scripts/sarif_common.py`, which becomes the shared emitter (D7, D8).
    - **The tests that pin the old generators** migrate with them (D16).
- **Why.**
  - A whole file at Run B's scale passes one response's output cap. At about 395 tokens per finding, an agent-written `risk-scores.md` passes 64k tokens at roughly 160 findings (PRD D-2).
  - Arithmetic and completeness can only be made true by construction in code, and code can be checked (PRD D-2, D-4; KB 22).
  - When its output gets large, the agent writes a generator anyway (N14). A shipped, tested renderer replaces an improvised, unreviewed one.
  - Keeping `threats.md`'s tables and Phase 3's compilation in the model keeps Track O, the less certain track, inside its estimate (feasibility check row 9, central). It also keeps #356 separate, under NG4: the ID map records each renumbering, and a test pins today's behavior (R-13).
- **Alternatives considered.**
  - *(a) Chunked or incremental agent output everywhere* (PRD D-2 option (a)). It keeps today's tier, but leaves the arithmetic, completeness and identity to the model, which is where both runs failed. Rejected.
  - *(b) Render `threats.md`'s tables in code (SV-2b).* It would move ADR-047's coverage authority into code and fold #356 in. It is also the first budget carve (R-23), and it adds the most effort to the least certain track. Not adopted. Bounded emission keeps `threats.md` complete either way.
  - *(c) Keep chain formation in the model* (R-19's alternative). A model can't meet the determinism claim or the more-than-105-chain bound at the fixture's scale (feasibility C-2). Rejected.
- **Consequences.**
  - **ADR-046.** D1 is superseded for these surfaces in two steps: the four scorer and controls files at PR 1, and `threats.sarif` at PR 2. Its D4 tests become structural guarantees on the rendered surfaces, and stay as tests where output remains model-authored (Section 6, the `threats.md` tables). D5's structural ideal is adopted for the rendered surfaces. D2 and D3 stand: the renderer reads the populator's block and adds no second authority (D2 of this ADR).
  - **ADR-047** is unchanged, because Section 6 stays model-written.
  - **ADR-013** D1's single Phase 4 co-generation pass is superseded for `threats.sarif` at PR 2.
  - **ADR-048** D3: the shipped emitters become enforcement points (only `:2026` tokens are emitted, and `LLMnn:2025` is rejected).
- **Supersedes or amends.** ADR-046 D1 (in part) and D4 (in part); ADR-013 D1 (`threats.sarif`, at PR 2); ADR-048 D3 (the enforcement points).

### D2: The judgment/computation line, field by field [Track: R]

- **Decision.**
  - **Rule.** An agent authors a value only when it must read third-party text or the architecture to produce it. Everything else is computed, and the agent contract stops authoring it.
  - **Routing.** The scorer agent gets only open findings that need judgment: non-peers that are NEW, UPDATED or lack a usable baseline row. The renderer inherits UNCHANGED findings that have a row, and gives other peers their primary's assessment, scored with their own asset tags (D9). The controls agent gets every scored open finding and copies UNCHANGED results from the baseline, as today (`control-analyzer.md:93-105`). Their narrative fields come only from the baseline's persisted slotted text in §7's `### Assessment Inputs`, never from rendered text: the planner puts that text, decoded, in the unit's batch-input row, and the agent copies it from there (Architect re-review RR1; D3). Their evidence-class text (`evidence[]`, `matrix_row` and `recommendation_body`) takes the same path: the planner decodes the baseline's values into the same row, so a carried string is escaped exactly once per render and never compounds across runs (rev. 2, the lead's check).
  - **AR-T3's reading (recorded at W1, 2026-11-22, T023).** A carried UNCHANGED controls result is read from one place: its baseline's §7 `### Assessment Inputs`, decoded, through `tachi_parsers.parse_controls_assessment_inputs` (T143).
    - That covers its narrative text and every evidence-class value: `evidence[]`, `matrix_row` with its slot tokens, and `recommendation_body`.
    - The planner never takes them from the rendered §2 row, whose computed cells the renderer filled, nor from §3, whose control details are per control, nor from the §4 block (T035, T036, T143).
    - So T035 persists all three evidence-class values beside the narrative text, escaped on write, and T143's reader returns all three. The table holds the whole controls item in the shared persisted-inputs format (`contracts/module-signatures.md`), so the item's closed values come from it too, re-checked against their enums on read.
    - A pre-1.1 baseline has no §7, so the reader returns nothing for it. The agent copies the UNCHANGED result from the baseline file as today (`control-analyzer.md:93-105`), and that text was never escaped by a renderer, so no escape compounds.
    - **A Section 7 with no Status column (ruled at W3, 2026-11-23, from T036).** Such a finding has no status, so the controls agent scans it fresh and nothing is carried for it. S-12(b)'s derived UNCHANGED (D9) is the scorer's alone: it keeps human governance fields there, the controls file has none, and a derived status could hand a reissued ID's control result to a new finding (ruling B's exposure).

  | Scorer field | Author |
  |---|---|
  | ID, component, threat, category (D10), MAESTRO layer, DFD kind, original risk level | renderer, from the reference set and `threats.md` §1; the MAESTRO layer by its chain, which also reads the per-finding tables (ruled at W4, below) |
  | Assessed CVSS vector | agent |
  | Metric cells, base score, ±1.0 bound (`score_bounds`), elevated vector and score, 9.2 ceiling, final `cvss_base` and its clamp cause | renderer |
  | Eight sub-scores | agent |
  | Exploitability and scalability means | renderer |
  | Zone, trust level, auth-barrier and network-boundary counts | agent. The zone must name a §2 row; a trust level that contradicts an unambiguous §2 label is flagged `corrected:trust_level:trust-label` |
  | Reachability: baseline, keyword adjustment, clamps, caps, the 5.0 default and its warning | renderer |
  | Composite, band, §3's weighted values | renderer |
  | Owner | carried verbatim; `Unassigned` when fresh |
  | SLA, disposition, review date, scored-on date | renderer (D9) |
  | `score_source`, flags, `affected_assets` | renderer |
  | Rationale per dimension; optional per-metric and per-sub-score rationale | agent, as prose with slots |

  Per file, the scorer renderer writes everything, the SARIF included. The Executive Summary's one sentence is templated from computed counts, because no batch sees every finding.
  - **The Executive Summary's reading (W1, 2026-11-22, T023, from T027).**
    - §1's first table is the severity band table: Severity, Count and Percentage, with percentages by largest remainder (D5), and a Total row equal to the open count. `parse_risk_scores_severity` reads it unchanged (NFR-1), so lane P has nothing to teach.
    - The sentence's wording is the template's (T031). The goldens pin what it states and in what order: the open count, then Critical, High, Medium and Low.

  | Controls field | Author |
  |---|---|
  | ID, component, threat, MAESTRO layer, category | renderer (inputs) |
  | Inherent score | renderer: this run's `risk-scores.md` composite, read through D9's reader, never re-scored |
  | Inherent severity | renderer: band(inherent), the K11 reader's rule (`tachi_parsers.py:1575`) |
  | Control status, control category, confidence, evidence, optional effectiveness assessment | agent |
  | `carried_forward` | agent; accepted only for an UNCHANGED finding whose result the resolved baseline controls file holds (amended at W4, below), otherwise cleared with the reason recorded |
  | P0 effectiveness, reduction factor, residual score and severity, `CF`, `carry_forward_count`, `rescan_scope` | renderer |
  | Recommendation and effort | agent, as the §4 block body (R-34) |

  Per file, the controls renderer writes everything except the model cells below:
  - §1's highest-risk unmitigated finding is the partial or missing one with the highest inherent score, ties in S-2 order;
  - §3 has one control per distinct category, file and line;
  - a new `## 7. Analysis Integrity` lists input issues, row checks and each finding's flags (FR-K7.4), and each result carries the flags as the SARIF `integrity-flags` property (D3, D7). Its `### Assessment Inputs` persists each narrative field's validated, slotted text, escaped on write, for the next run to copy (RR1);
  - SARIF's `recommendation` and `effort-estimate` are read from each finding's own §4 block, found outside code fences, by the shared rules (`tachi_parsers.recommendation_text` and the Effort line), and D4's step 5 checks each against the validated part's body.

  **Controls §2 and §4 in PR 1 (R-34), cell by cell:**

  | Cell | PR 1 |
  |---|---|
  | The §2 band table each row sits under (band of residual), the band headers (empty bands omitted), the K8 header row, row order (residual descending, then S-2) | fill |
  | §2 Inherent Score, Inherent Severity, Residual Score, Residual Severity, `CF` (`CF` or `—`) | fill, overwritten by column position. The agent writes slot tokens there; other content is overwritten and counted in the stage record's `counts.cell_overwrites`, and `CF` isn't counted (ruled at W3) |
  | §2 Threat ID and the cell count (11) | structural: a mismatch rejects the item (D3), and its batch is re-dispatched |
  | §2 Control Status (through `classify_control_status`, `tachi_parsers.py:248`), Control Category, Component, MAESTRO Layer | check against the structured judgment or input. A mismatch is flagged per finding in §1's warnings, §7 and the stage record; SARIF and totals follow the structured value, and §2 keeps the agent's cell (ruled at W3) |
  | §2 Threat | model text (NFR-10 only) |
  | The §4 group each block sits under (band of inherent), block order (inherent descending, then S-2), number, heading `#### n. ID — Component (Composite: x, Band)`, `**Current Status**:` line | fill (renderer-written) |
  | The §4 body: What, Where, Reference Patterns, Effort | model, structurally checked: each key once and in order, Effort in {Low, Medium, High}, no heading or table line. A failure rejects the item |

  - **Rulings at W3 (2026-11-23, from T056, T059 and T052).**
    - **The overwrite count** is the stage record's `counts.cell_overwrites`, an eighth base count: the computed §2 cells, over every row, that held anything but their own slot token. The controls renderer always writes it, `0` included, and the scorer never does, because its agent writes no table cell. It raises no flag, because a computed cell is right by construction. It isn't added to `corrected`, which counts `corrected` flags, of which the controls file raises none (`contracts/part-files.md`).
    - **A checked cell stays the agent's.** §2 shows Control Status, Control Category, Component and MAESTRO Layer as the agent wrote them, escaped. A disagreement is flagged `input:<field>:sources-disagree`, with `control_status`, `control_category`, `component` or `maestro_layer` (`contracts/module-signatures.md`). The SARIF, every total, §3 to §6 and the from-disk checks follow the structured value. "Check" isn't "fill": R-34 keeps §2 model-authored in PR 1, FR-K7.3 lets this shipped check cover it, and FR-K8.1's follow-up turns each check into a fill (Known limitations).
    - **A list of finding IDs** in either rendered markdown file, §5's Examples cell included, names at most 10 IDs, in S-2 order, then ` and N more`, where N counts the rest. The cap is `sarif_common.PEER_CAP`, the cap of ruling C's sentence.
    - **An evidence `file` that the resolver refuses at render time** (missing, a link, or not a regular file) is flagged, never refused.
      - Its entry stays in §3, `control-evidence` and §7 with the `file` as the agent wrote it, and `relatedLocations` leaves it out (D8).
      - The finding is flagged `input:evidence.file:unresolved`, and the stage record warns `evidence-file-unresolved`, so the run exits 5.
      - The control status and every computed value follow the part.
      - Why not refuse: the control analyzer copies an UNCHANGED finding's evidence verbatim, so after a file moves, a refusal would recur on every baseline-aware run, and no re-run could clear it.
      - Syntax still rejects the part at step 9 (D3).
  - **A claim needs a result to carry (ruled at W4, 2026-11-24, from the PM's open question on T066's re-run).** The renderer accepts `carried_forward` only for an UNCHANGED finding whose result the resolved baseline controls file holds. That is the result that `control-analyzer.md` gives the agent to copy:
    - in a 1.1 file, the finding's persisted result in §7's `### Assessment Inputs`, read by `tachi_parsers.parse_controls_assessment_inputs`, the planner's reader for the unit row (AR-T3);
    - in a 1.0 file (by `schema_version`, as `tachi_parsers.parse_frontmatter` reads it), a §2 row with the finding's ID under one of the four `### <band> Residual Severity` headings, read by the renderer's `_rows_under`, the reader of its own from-disk check. A 1.0 file has no persisted results, so the agent copies from the file itself.

    The bytes are the plan's digest-checked input `baseline_compensating_controls`, which `_load_plan` already loads. A claim for a finding that the file doesn't hold is cleared as the two existing cases are (no resolved baseline, a status other than UNCHANGED), with its own reason: the stage record's warning `carried-forward-cleared` and an Input Issue line record it, it raises no flag, and the row counts as scanned. Clearing changes no value that the agent wrote, so the rule can err only one way: a copied result can show `—`, but a result that wasn't copied can't show `CF`.
    - **Why.** From PR 1 the renderer, not the agent, writes `CF` and `carry_forward_count`, and adopters and auditors read them as a statement that a result came from the baseline. A status and a resolved file don't show that. `agentic-app`'s T-1 is UNCHANGED, and the shipped controls file has no row for it. Until this ruling, an agent that claimed such a finding anyway, against `control-analyzer.md`, got `CF` and no record.
    - **Why these readers.** Each is the copy contract's own source, so for a 1.1 baseline the renderer accepts a claim only for a finding whose persisted result the planner could hand over. A §2 row doesn't count in a 1.1 file, because its text is rendered and the agent never copies from it (the Routing bullet above; Architect re-review RR1). `parse_compensating_controls_md` isn't used, because it writes warnings to stderr.
    - **The oracle.** D3's eighth class (R-H) takes its accepted set from this rule. T066's renders don't move: harness fix 2 claims only findings that the shipped controls file holds, so Run A's set stays the same 81.
    - **The fix is PR 1's:** `render-compensating-controls.py`, its tests, and `control-analyzer.md`'s sentence on what the renderer accepts.
  - **The MAESTRO layer's chain (ruled at W4, 2026-11-24, from T066's group U-1).** A finding's layer, in the scorer file and the controls file alike, is the first of these that holds one:
    1. Section 7's MAESTRO Layer cell, where the reference set's reader finds Section 7;
    2. the finding's own row in a per-finding table. That is a table outside code fences whose header's first cell is `ID` and that has a MAESTRO Layer column: the template's §3 and §4 tables, and any table under them, such as a bold-labelled sub-table in §4.2;
    3. its component's Section 1 MAESTRO Layer cell, found by name, then case-folded;
    4. `Unclassified`.

    Under D8's fallback, the member's own `maestro-layer` still comes before step 3.
    - **Why step 2.** v4.48.4's scorer read the layer from those tables' MAESTRO Layer column (`risk-scorer.md` §1a on `b040fa1`), and the report and infographic extractors read it there too. The five shipped threat models hold it there and in no other contract section. Without step 2, every finding of a v4.48.x threat model renders `Unclassified` (T066's U-1: 368 values), and ADR-020's layer, a contract field that the shipped files carry, is lost on old inputs (PM W3 ruling 2, condition 1). With it, 308 of the 368 values come back. The other 60 are values that no contract section of the input holds, or that a shipped controls file wrote differently from its own input. The fix also exposes 23 in one shipped controls file, which wrote `Unclassified` where its own scorer file held the layer. Those 83 go to the PM with T066's re-run.
    - **Precedence.** A finding's own cell comes before its component's, because Phase 3 writes the inherited layer on each finding's rows (ADR-020; `orchestrator.md`). Section 7 comes before the tables, because the reference set is the one source of a finding's identity (D-4), and PR 2's chain script reads Section 7 first (D13). Two sources that disagree raise no flag. The layer moves no score (ADR-020), no reader would act on such a flag, and none of the 17 tracked `threats.md` files that hold both disagrees in any row (checked at `f43440b`).
    - **Rows.** Each table is read by `parse_markdown_table`'s row rules. The per-finding tables are read in one pass over the file, never by one call per table, whose cost grows with the square of the file's size (confirmed at W4 from T146's measurement; `contracts/module-signatures.md`). A short row is skipped. A long row is read by its header's positions, as the extractors read the same rows (NFR-1): the GFM `\|` rows at `examples/agentic-app/sample-report/threats.md:315` and `examples/agentic-app/threats.md:230` both hold their pipe after the layer cell. The first row of an ID wins within each step, and a blank cell there passes to the next step. A layer read this way meets P0-4's intake check, like every other value from `threats.md` (D3).
    - **Not read.** Two sources are left out. One is the printed Phase 1 inventory in a pipeline execution log: no `threats.md` template has it, its headings vary, and PR 2 replaces it with `inventory.json` (D11). The other is a layer inferred from other findings on the same component.
    - **One reader.** `tachi_parsers.parse_finding_layers` returns steps 1 and 2 (`contracts/module-signatures.md`). Both renderers, and the planner's controls unit row (T067b's M3), take those steps from it, so the chain's three copies can't drift, and the controls file's `maestro-layer` stays the scorer file's (gap B). PR 2's readers of the layer call it too.

  ADR-046's tier change for this file is therefore partial in PR 1: every number and band is renderer-tier.
  - **The one tag source (S-13).** It is the `## Affected Assets` block of the input `threats.md`, ADR-046 D2's value authority.
    - The renderer recomputes the tags from the command's resolved architecture file with the populator's own join, run over the reference set so drift forms are covered (`parse_component_asset_map` and `match_component`, the body of `compute_affected_assets`, `populate-affected-assets.py:233-271`).
    - A block equal to the recomputation is used. One that is absent, unparseable, different or missing an open finding is stale, so the recomputation is used, with a warning.
    - With no architecture file, the block is used and recorded as unverified. With neither, no finding is elevated; the run warns, records the cause and continues.
      - **"Recorded as unverified" (ruled at W2, 2026-11-23).** The record is written in two places: §6's Integrity Summary names the tag source, and the stage record carries the warning `tag-source:no-architecture-file`. The stage record has no other key that names the tag source, so the warning is its only trace. Its detail says the block's tags were applied unverified, and names any tag outside the closed set that was dropped. So every tag source except a verified block warns under `tag-source:<cause>`, and a reader of the record can tell the two apart. The run is already `success-with-warnings` here, because D7's resolver warns whenever no architecture file validates.
    - The choice is made once per run, never per finding, and the same values feed the modifier step, D10 and `affected_assets`.
  - **F-302's wording.** "Provenance only — does NOT affect scoring" (`risk-scorer.md:528`, `asset-modifiers.md:165-167`) becomes: "`affected_assets` lists the tags the asset-modifier step used for this finding. Emitting it changes no score; only the modifier step does, and it reads the same tags from the same source (ADR-050 D2)." The copy-verbatim instructions (`tachi.risk-score.md:83-90`, `:135-140`; `risk-scorer.md:519`) retire with SARIF authoring, and `asset-modifiers.md:169-178` stops exempting UNCHANGED findings (D9).
- **Why.**
  - D-2's "one source of truth" and R-34. Filling the computed cells keeps SC-5 true by construction, where a check would only report a broken file. The checks reuse what consumers read (KB 19, 22).
  - S-13's two sources today: the modifier reads `parse_component_asset_map` (`risk-scorer.md:281`), `affected_assets` copies the block (`:519`), and `--output-dir` skips the populate step (`tachi.risk-score.md:104-111`).
  - Routing only judgment means no agent retypes a carried number, and it cuts scorer output (SC-8).
- **Alternatives considered.**
  - **Render the §2 rows from data in PR 1.** R-34 binds; it is FR-K8.1's follow-up, which turns each check into a fill.
  - **Check the score cells only.** Wrong numbers would sit next to right totals.
  - **Always take tags from the architecture.** Two authorities (ADR-046 D2), and silent re-tagging.
- **Consequences.**
  - **Files.** Both agent specs keep only judgment instructions, the arithmetic references become renderer documentation, and both templates gain the K8 schema, the slots and the new sections.
  - **Offline tests.** Field ownership per schema. Seeded wrong §2 numbers are overwritten and counted. A seeded status mismatch is flagged while the SARIF follows the structure. The §4 extraction round-trips. The tag source is tested in each case, including drift forms, with no mixing.
  - **Risks.** A literal `|` in a §2 cell shifts the columns and rejects the item; the template rule and the retry cap bound this.
  - **Ruled by the PM at the plan review (2026-11-22), ruling A.** A band change that the asset tags alone explain is an input change, not a correction. It is flagged `retagged` and follows its own review-date rule (D9, "Tag-driven band changes", folded verbatim).
- **Supersedes or amends.** ADR-046 D4 becomes structural for `risk-scores.sarif`'s `affected_assets` (shared with D1). ADR-046 D2 stands.

### D3: The part-file contract [Track: S]

- **Decision.**
  - **Identity.**
    - A part is one UTF-8 JSON object, written by one Write call.
    - Its `schema` is exactly `tachi.part/1`. Readers accept only the version they implement, and any change to the envelope or to a stage payload bumps the integer.
    - Parts never cross versions, because a part is read only within the plan that named it.
  - **The closed envelope.** Eight keys, all required: `schema`, `plan_id`, `batch_id`, `stage`, `agent_type`, `finding_ids`, `items` and `fragments` (`contracts/part-files.md` §1; `scripts/tachi_parts.py` is the authority).
    - `items` holds one object per finding ID, keyed by `finding_id` in every stage.
    - Each stage's payload keys (D2, D9, D10) sit beside `finding_id`, and they are closed too.
  - **String classes.** Every payload string has exactly one class, and the contract lists them field by field.
    - *Closed values*: IDs, enums, vectors, paths, and names that must match an input (a zone names a §2 row). Each is checked against its pattern, enum or input.
    - *Narrative*: `fragments[].text`, the scorer's rationale fields and the controls assessment rationale; in PR 2, the report's per-finding text and the chain narratives (D13, D14). Numbers that state a count, score, band or percentage come only from slots, so the prose can't contradict the tables (D-2).
    - *Evidence*: file paths, line numbers, snippets, controls evidence summaries, R-34's controls Sections 2 and 4 cell text, and a legacy baseline's §3 prose, which has no slots (D9). Digits are allowed. The renderer escapes these fields and never reads a number from them.
    - **The reading of an evidence entry's `file` and `line` (W1, 2026-11-22, T023).** Both are closed values on input: each is checked against its pattern and range and never cut, so a bad or over-long `file` rejects the part. They are evidence on output: escaped, digits allowed, and never read for a number. `contracts/part-files.md` and the shared reference follow this reading.
  - **Carried narrative (Architect re-review RR1).** Each narrative field's validated, slotted text is persisted, escaped on write: the scorer's in §6's `### Scoring Inputs` (D9), and the controls' in §7's `### Assessment Inputs` (D2). The scorer renderer carries it, and the controls agent copies it from its batch input. Either way it is decoded first, then re-validated as narrative and re-resolved against this run's values, with the per-field fallback. Only legacy prose, which has no slots, is carried as evidence.
  - **Slots.** A slot is `{{kind:arg}}`, the one spelling in every stage, contract and shared reference.
    - It is recognized only as `{{`, then a kind from the table below, then `:`. Any other `{{` is plain text, escaped on output.
    - The argument fully matches `[A-Za-z0-9_.:-]{1,64}`. The renderer fills the slot from computed or input data, never from the agent's text.
    - The table is closed per stage:

    | Kind | Argument | Resolves to | Stages |
    |---|---|---|---|
    | `score` | `cvss_base`, `exploitability`, `scalability`, `reachability`, `composite`, or one of the eight sub-score names | this item's rendered value, to one decimal; a sub-score is the agent's own integer | `risk-score` |
    | `score` | `inherent`, `residual` | this item's rendered value | `compensating-controls` |
    | `count` | `auth_barriers`, `network_boundaries` | the agent's own count for this item | `risk-score` |
    | `count` | `evidence` | this item's number of evidence entries | `compensating-controls` |
    | `count` | `members`, `layers`, `converging` | the chain's computed counts (D13) | chain narratives |
    | `count` | `open`, `resolved`, or a band name | the reference set's count | `report` |
    | `band` | `severity`; `inherent`, `residual` | this item's rendered band | `risk-score`; `compensating-controls` |
    | `pct` | `reduction` | this item's reduction percentage (D5) | `compensating-controls` |
    | `pct` | a band name | that band's share of the open findings, by largest remainder (D5) | `report` |
    | `date` | `scored`, `review` | this item's rendered dates | `risk-score` |
    | `finding` | a finding ID | the canonical ID. It must be in the reference set, and in a chain narrative, a member | all |
    | `ref` | a taxonomy ID, such as `CWE-89`, `LLM01:2026`, `T1190`, `AML.T0051` or `L3` | the ID as written. It must be one of the finding's own taxonomy IDs: those in its reference cell, its rule's relationships in the renderer's rule table, and its MAESTRO layer. In a chain narrative the finding is any member; a section fragment has none | all |
    | `name` | `component`, or `zone` (`risk-score` only) | this item's component, or the zone the agent named | `risk-score`, `compensating-controls` |
    | `name` | `component:<finding ID>` | that finding's component, under `finding`'s rule | chain narratives, `report` |

    - **Outside a slot,** a narrative field holds no numeric character (`str.isnumeric()`). Component names and cited IDs that carry digits come through `name` and `ref`, and S-4's variants include digit-bearing component names.
  - **The per-field fallback (PM plan review, finding 1).** A narrative field that fails only the numeral ban or the slot grammar doesn't reject its part.
    - The grammar fails on an unterminated slot, an argument outside the pattern, or an argument that doesn't resolve.
    - The renderer writes that field's fixed sentence from the shared reference instead, flags the finding `input:<field>:narrative-fallback` (scorer §6, controls §7) and counts it in the stage record, as D13 does for chain narratives.
    - Structural failures (validation steps 1–10 below) still reject the part. Over-limit prose doesn't: it is cut (step 9).
    - **W5's fallback rate: ruled by the PM at the rev. 1 confirmation (2026-11-22), ruling 2, verbatim:**

      > W5 reports each stage's fallback rate, per run and effort level, under TW-L2's dispositions, decided now:
      > - A fallback from a slot that the table says should resolve is a shipped-code defect: fix it and re-run once.
      > - A stage above 10% of its narrative fields is recorded and gets a follow-up, which that PR's release notes link. It doesn't fail the PR.
      > - A stage above 25% in any W5 run, the SC-8 small runs included, comes back to the PM before that PR merges, unless a contract-text fix and TW-L2's second attempt bring it to 25% or below. The return includes a sample of the rejected fields.
      > - A fallback loses prose, never a row, so it never decides SC-1.

  - **The contract text states the check** (PM confirmation, ruling 2): no digit outside a slot. Names and cited IDs go through `name` and `ref`. Versions, ports and other terms with digits are written without the digits. A count, score, band or percentage stated outside a slot stays forbidden in words too. Other number words stay, such as "two-factor" and "third-party".
  - **Batch granularity.**
    - One batch is one dispatch of one agent, and yields one part.
    - Its units are a contiguous run of the stage's units, in S-2 order.
    - Sizes are balanced (they differ by at most 1), at D6's per-stage size.
    - Every dispatched unit is in exactly one batch.
  - **Layout (P-6).** The stage is `risk-score` or `compensating-controls` (PR 1). In PR 2 it is the run-level `threat-model` plan, or one of its batch stages: `phase2`, `trees`, `report` and `threats-md` (D6's batch-stage table).

    ```
    {out}/.tachi-build/<stage>/current.json                            the current-plan pointer
    {out}/.tachi-build/<stage>/<plan_id>/plan.json                     the batch plan
    {out}/.tachi-build/<stage>/<plan_id>/inputs/<batch_id>.json        the batch input
    {out}/.tachi-build/<stage>/<plan_id>/parts/<batch_id>.a<n>.json    the part, attempt n
    {out}/.tachi-build/<stage>/<plan_id>/preimage/<canonical name>     an earlier output, copied by plan (D4)
    {out}/.tachi-build/<stage>/<plan_id>/staged/<canonical name>       a rendered output, checked before it replaces the canonical file (D4)
    {out}/.tachi-build/<stage>/<plan_id>/stage-record.json
    {out}/.tachi-build/<stage>/<plan_id>/failed/<canonical name>
    ```

    Track O's run files sit flat under `{out}/.tachi-build/`, because every threat-model run has its own `{out}`:
    - `phase1/`, `briefs/`, `records/` and `idmap.json` (D11);
    - `chains/` (D13).

    Its batch stages use the layout above, and a `trees` batch also writes the tree files its input names under `<plan_id>/trees/` (D6). The run-level `threat-model/<plan_id>/` holds the pre-images, the `{out}` snapshot, the main-session checks' hand-off files under `checks/`, the stage record and `failed/` (D4).
  - **Path naming.**
    - Only the planner and the reconciler compute paths.
    - Each batch input carries an absolute `part_path`.
    - The dispatch prompt is fixed: `Read and follow the batch input at <input_path>. Write only the part file it names.`
    - No path is ever built from part content.
  - **Planner state is checked, not trusted.** The writers' directory holds `plan.json`, `inputs/` and `current.json`, so:
    - every script recomputes each path from `--out`, the stage, and plan and batch IDs that pass `tachi_parts`' patterns, and ignores paths stored in files, except the plan's digest-checked `inputs` paths and its `refs` paths, which the renderer reads;
      - **`refs` (ruled at W2, 2026-11-23).** The plan holds `refs` once, and each batch input carries a copy for its agent, so a plan with no units keeps its pointers. No script reads a path from a batch input. A `refs` path is a candidate, never trusted: the renderer passes it through the shared resolver (D7) or R-6's checks before it reads anything;
    - `plan` and `reconcile` print the plan file's SHA-256 as `plan_digest`, and the command passes the latest one back as `--plan-digest`. `reconcile`, the renderer, `fail` and `close` refuse a plan file with another digest (exit 2). This was chosen over re-passing the inputs, because one check also covers the batch states, the retry budget, the pre-image digests and each batch input's recorded digest;
    - `--plan` names the plan ID and overrides `current.json`. When the two disagree, the script exits 2;
    - §8.3's writer cells narrow to `{out}/.tachi-build/<stage>/{plan-id}/parts/`, and §8.2's closed placeholder set gains `{plan-id}` (C7). The cell is a declaration, so the digest is the check.
  - **Identifiers.** One allow-list module in `tachi_parts` holds every identifier pattern: finding, plan, batch, dispatch, group and chain IDs, and the evidence language. Each is an ASCII `re.fullmatch` with `[0-9]`, never `\d` or `$` (KB 24), and every contract cites the module.
    - Every comparison, sort and hash uses the canonical finding ID, `{PREFIX}-{N}` with leading zeros dropped, so `AGP-01` (`orchestrator.md:641`) compares as `AGP-1`. `findingId/v1` keeps Section 7's spelling.
    - Two spellings of one canonical ID in one input are a duplicate.
  - **Retention and staleness.**
    - Nothing under `.tachi-build/` is deleted (KB 21).
    - Each invocation makes a fresh `<plan_id>/` and replaces `current.json` atomically.
    - Readers open only the paths the current plan names, and count a part only if its `plan_id` equals the pointer's. An earlier plan's part, or an earlier attempt's, never counts.
  - **Validation (NFR-10).** In order. A failure in steps 1–10 rejects the part, except over-limit prose (step 9): steps 2–4 make it `unparseable`, and the others `invalid` (D6).
    1. The file is the planned path, a regular file, has no symlink below `{out}`, and lies under `{out}` by `samefile` identity (KB 24).
    2. It is at most 512 KiB. A markdown or SARIF input written by an agent is at most 16 MiB.
    3. Strict UTF-8, with no BOM and no surrogates.
    4. `json.loads` runs with four hooks: `object_pairs_hook`, which rejects duplicate keys; `parse_constant`, which rejects `NaN` and `Infinity`; `parse_float=Decimal`, so `1e999` arrives as `Decimal("1E+999")`, which the range checks reject, never as `inf`; and a bounded `parse_int`, which rejects an integer literal of more than 20 digits, because Python 3.9 caps none. A `RecursionError` also rejects the part. Nesting is at most 8 levels, and the top level is an object.
    5. `schema` selects the key set. `tachi.overflow/1` is checked against its six keys and classified `overflow` (D6). `tachi.part/1` continues. Any other value is `invalid`.
    6. The closed key set, then the types and ranges.
    7. `plan_id` equals the current plan's. `batch_id`, `stage` and `agent_type` equal the planned batch's.
    8. Before any other use, each ID passes `tachi_parts`' finding pattern, `(S|T|R|I|D|E|AG|AGP|LLM|OI|MI|TE)-[0-9]{1,6}` as an ASCII full match, which rejects Unicode digits and trailing newlines. `finding_ids` equals the planned set by canonical ID, with no duplicates, and there is exactly one item per ID.
    9. The stage payload (D2), field by field, with each string's class. In this step, only keys, types, closed values, IDs and structure reject the part. A prose field over its limit, narrative or evidence, is cut at its limit before escaping, flagged `input:<field>:truncated` and counted in the stage record. The same rule covers PR 2's `fragments[].text` (Architect re-review RR2).
    10. Strings: each is at most 16,384 characters, and contains no Cc character other than `\n` and `\t`, and none of U+2028, U+2029, U+200E, U+200F, U+061C, U+202A–U+202E, U+2066–U+2069 or the Unicode tag block, U+E0000–U+E007F. The tag block was added at W4 (2026-11-24, T146, from T064's SA-7): its characters render as nothing and carry ASCII text to any later reader, the report stage's agent included. Variation selectors and the joiners stay allowed, because ordinary emoji and several scripts use them. No tracked text file holds a tag character (checked at `f43440b`), so NFR-1 is unaffected.
    11. Narrative fields: the slot grammar, then the numeral ban. A failure here takes the per-field fallback and never rejects the part.

    **Output (NFR-10).** The renderer escapes only untrusted strings: agent text, and text read from untrusted inputs such as the reference set's Threat cells. Template constants such as `< 4.0` and `Critical -> High` are written as they are. Truncation (`output-formatting.md:36`, §3 untruncated) comes first, so no reference is cut. Per sink:
    - **Markdown table cells and prose:** `&`, `<` and `>` as `&amp;`, `&lt;` and `&gt;`; `|` as `&#124;`; a backtick as `&#96;`; each `{` of a `{{` that isn't a slot as `&#123;`; a newline in a cell as `&#10;`. A prose line that would start with `#`, `|` or `~` starts with `&#35;`, `&#124;` or `&#126;`.
      - **A line-start `~` (ruled at the P0 checkpoint, 2026-11-23, P0-1).** A prose line that starts with `~~~` opens a code fence, for GitHub and for the next run's tolerant reader. Every later heading, §4 and §6 included, then reads as inside the fence, and that run silently loses every human governance field and persisted input. So a prose line's first `~`, after any leading whitespace but a newline, as for `#`, is written `&#126;`. A `~` anywhere else, and any `~` in a cell, stays as written. CommonMark never reads a character reference as syntax, so `&#126;~~` is plain text in both views. No shipped example contains `&#126;` or a line that starts with `~~~` (re-checked at `8fbfa9f`), so every example parses as before.
        - **The leading whitespace (ruled at W3, 2026-11-23, from FX0's probe).** P0-1 ruled "after any spaces or tabs". The tolerant reader tests a line after `str.strip()`, which drops every Unicode whitespace character, and step 10 allows the Unicode space separators, U+00A0 and U+3000 among them. So a line led by one of them, then `~~~` or `#`, still opened a fence or forged a heading for tachi's reader, though not for GitHub. Both sides change:
          - **The guard** looks past any whitespace but a newline, by `str.isspace()`, the class that `str.strip()` removes. So no reader that strips a line before its structure test sees a rendered prose line start with `#` or `~`. Its line boundaries stay `\n` alone: every other character that `str.splitlines()` treats as one is in step 10's set, and none reaches output (P0-4). So the guard rests on the three checks that keep those characters out of a render: step 10 in a part, the intake in an input and `_check_staged`'s backstop in the staged file. It is no second line against a forged line break, such as a lone `\r` before `## `, which CommonMark reads as a heading (T064's Q1, recorded at W3's closing sweep).
          - **The tolerant reader's structure tests** (D9, R-26) look past only spaces and tabs at a line's start, as CommonMark does, and still strip the line's end. So a file tachi didn't render, a v4.48.x baseline or a hand edit, can't hide §4 from the carry while GitHub shows it. None of the 28 tracked `risk-scores.md` files has a line led by other whitespace, and none is CRLF, so no parse changes (NFR-1).
    - **Code snippets:** unescaped, inside a fence longer than their longest backtick run.
      - **Finding a section (ruled at W3, 2026-11-23, from T087's observation).** A snippet's lines stay raw, so a quoted `### Assessment Inputs` line sits in the file as written, and a cell or a prose line can hold a heading's text after its first character, which no rule escapes. So every reader that a renderer's from-disk checks or the next run rely on finds a section by its exact heading line outside code fences, through `tachi_parsers.match_heading(pattern, text, outside_fences=True)` and then `parse_markdown_table(..., start_line=...)`, never by `parse_markdown_table`'s substring search. A fence closes only on a run of its own character at least as long as its opener, with nothing after it (CommonMark's rule), so no snippet line closes its fence early. Under the sink rules above, no rendered line outside a fence starts with `#`, so nothing rendered can stand in for a heading. This covers `parse_controls_assessment_inputs` and every lookup in both renderers' `_check_staged`. `read_baseline_scores` already reads by outline. Otherwise a quoted heading fails a legitimate render with exit 4 (P0-10's class), or hides §7 from the next run. The report and infographic extractors keep their substring search until a follow-up (Known limitations).
    - **SARIF strings:** through `json.dumps` only.

    **Control characters in inputs that aren't parts (ruled at the P0 checkpoint, 2026-11-23, P0-4).** Step 10 checks parts only, and the escapes above translate no control character. Without a check, a value that a renderer takes from another input would reach its files as written: from `threats.md` (a threat, a mitigation, component and zone names, labels), from a baseline file (an owner, persisted narrative, legacy prose, S-12(b)'s supplied values) or from D8's SARIF fallback. NFR-10 names these inputs untrusted. A lone `\r` is a line ending in CommonMark, so `x\r## Forged` forges a heading on GitHub, though tachi's readers split on `\n` only. An ESC is a terminal escape, and a bidi control reorders the displayed text. The minimum:
    - **At intake.** A renderer refuses a value that holds a character in step 10's set, at the point it takes the value from the input. It exits 2, which the command routes to Step F (D4), and the message names the finding, the field and the remedy: regenerate the input, or edit the value.
    - **A whole-file backstop.** `_check_staged` checks the staged markdown, raw, and every decoded string of the staged SARIF for a character in step 10's set, and exits 4 on one (D4).
    - **One predicate.** `tachi_parts.forbidden_character(text: str) -> Optional[str]` returns the first character of `text` that is in step 10's set, or `None`. Step 10 and both checks use it, so the controls renderer and PR 2's writers share one definition (`contracts/module-signatures.md`). Step 10's length limit isn't part of it.
      - **A lone surrogate (ruled at W3, 2026-11-23, from R3a's planner).** The predicate also returns a surrogate code point, U+D800–U+DFFF. Only a JSON escape can spell one, in `threats.sarif`, `risk-scores.sarif` or a baseline SARIF, and no UTF-8 file can carry one. A part never reaches step 10 with one, because step 3 refuses it, so no part's outcome changes. The intake and the backstop above now refuse it as they refuse a step-10 character, which covers values that the planner doesn't read, such as the controls fallback's zone and the baseline SARIF's vector.
      - **At plan time.** `plan` refuses a lone surrogate in any value it reads for a member from a JSON input, peers included: the renderer reads every member's text, and a batch input that held one couldn't be read back (`tachi_parts.load_json`). It exits 2 before anything is written, naming the finding, the value and the file, with the regenerate remedy. The planner checks nothing else of the predicate's set; whether it should is T064's question. T064 answers it (Q4, with SA-1 and SA-3), and W4 rules on the answer with T146's fixes.
    - **Left to T064:** whether a baseline cell that holds such a character should drop its row to Input Issues instead, S-12(d)'s path. No shipped input or output holds one (P0-4's scan), so NFR-1 is unaffected. T064 answers it (Q3), and W4 rules on the answer with T146's fixes.

    **Readers decode exactly these references:** `&amp;`, `&lt;`, `&gt;`, `&#124;`, `&#96;`, `&#123;`, `&#10;`, `&#35;` and, since P0-1, `&#126;`, nine in all. One shared decoder in `tachi_parsers` runs after a row is split on raw `|`, in `parse_markdown_table` and every other reader of rendered text (lane P). So the PDF and the infographics show the text, never `&lt;`.
    - No shipped example contains one of these references (checked at `b040fa1`), so every example parses as before. A test pins that.
    - GFM's `\|` isn't decoded, so the rows at `examples/agentic-app/sample-report/threats.md:315` and `examples/agentic-app/threats.md:230` parse as they do today (NFR-1).
    - **A GFM `\|` in a Section 7 cell (the P1 checkpoint's P1-3, moved into PR 1 by the PM's W6 ruling Q1, 2026-11-24).** Section 7's readers, the reference set and the layer chain's Section 7 cell (step 1 of `parse_finding_layers`), read GFM's `\|` as a literal pipe inside a cell, through `parse_markdown_table`'s additive `escaped_pipes` option, so both read a row alike and a `\|` before the layer cell can't shift the layer. A row whose cell count still exceeds its header after that, which a raw `|` makes, is still refused at `plan` with exit 2 and the `&#124;` remedy (S-12(c)). The per-finding tables and the extractors keep D3's rule, so the two rows above, both in per-finding tables, parse as they do today (NFR-1).
    - The round trip, the `.md`–`.sarif` agreement, the from-disk checks and the oracle compare decoded values. The oracle's first three classes are spec NFR-1's: a flagged value (corrected, or retagged under ruling A); D-5; and S-2's reorder of rows with equal scores. Its fourth, the reference-set class, bounded by the PM at the rev. 1 confirmation (ruling 4), verbatim:

      > text the renderer takes from the reference set where today's agent paraphrased it: a field that ADR-050 D2 has the renderer take from the reference set, whose rendered value equals that finding's reference-set value on decoded values, after the documented truncation. A diff in such a field that fails this test is unattributed (PM confirmation, ruling 4).

      **Widened by the PM at W4 (2026-11-24, ruling R-A, from T066's oracle)**, verbatim:

      > the text stays as signed, and the class also covers text or a closed value that the renderer takes from another of its inputs, where the shipped file holds another value.
      > - **The added fields and their sources**, a closed list:
      >   - **The threat and the component that Section 7's form lacks** (`message.text`, the §2 Threat and Component cells, §3's `**Threat**:` line, `logicalLocations[0].name` and the controls files' threat text): the value that S-12(b) supplies from the baseline row (ADR-050 D9: the threat from the row's §3 `**Threat**:` line, else its §2 cell; the component from its §3 heading, else its §2 cell).
      >   - **The MAESTRO layer** (`maestro-layer` in both SARIF files, and §3's `**MAESTRO Layer**:` line): ADR-050 D2's layer chain, that is Section 7's cell, else the finding's own row in a per-finding table, else its component's Section 1 cell, else `Unclassified`.
      >   - **`logicalLocations[0].kind`:** the component's Section 1 Type, through ADR-050 D8's closed map.
      >   - **`logicalLocations[0].fullyQualifiedName`:** `<zone>/<component>`, where the zone is that of the Section 2 row that lists the component, as Section 2 writes it (`contracts/sarif-result.md`, the primary location).
      >   - A component that no Section 1 row lists has no kind source here, and one that no Section 2 row lists has no zone source.
      > - **The test.** The oracle reads each added source from the input files with its own reader. A generic table reader is allowed, but never a function that the renderer calls to compute the field, such as `tachi_parsers.parse_finding_layers` or the renderer's S-12(b) supply, so the test isn't circular. The rendered value equals the source's value for the finding, on decoded values, after the documented truncation (60 characters for a §2 Threat cell and 30 for a Component cell). Where the finding is correlated, `message.text` also ends with ruling C's sentence.
      > - **An empty layer chain.** A rendered `Unclassified` where the shipped file held a layer is attributed only when the oracle's own reader finds no layer for the finding in any source of the chain. The record lists each such value by example, file and finding. The PM accepted 26 at W4, all in threat models that lack the template's Section 7 and Section 1 MAESTRO Layer columns: `agentic-app`'s AGP-01 (3 values), `maestro-reference`'s AGP-01 to AGP-03 (7) and `consumer-agent-app`'s 16. Any other comes back to the PM.
      > - A diff in an added field that fails its test is unattributed.

    - **The oracle's field scope and its fifth class (ruled by the PM at W3, 2026-11-23, ruling 2).** NFR-1's "keeps every section and field" means every section and field that the file's contract names. That is v4.48.4's template and agent mapping for the file, with `output-formatting.md` for the markdown, and 1.1's templates, this ADR and `contracts/`. A key that no contract names isn't written, and its absence isn't a diff: the oracle lists each one per example and file, with its count and where its information now sits (T066). A contract field that a shipped file carries is kept, unless a decision here removes it by name. The fifth class, for P0-9's reading of D10, verbatim:

      > a NEW finding's score that v4.48.4 held to its category's ±1.0 bound and that the renderer scores without it, because the run read no usable baseline `risk-scores.md` (ADR-050 D10, as P0-9 amends it), together with the values that follow from that score (composite, band, SLA, review date, the row's position and §1's counts) and the same values on the NEW or UPDATED peers that copy it (R-31). The test: the rendered `cvss_base` equals the finding's chain on its own vector and tags without the bound; the shipped value equals that chain with the bound; and the stage record states the missing or unreadable baseline. A diff in such a finding that fails the test is unattributed.

      **Widened by the PM at the W4 re-run (2026-11-24, ruling R-I, from T066's re-run)**, verbatim:

      > the text stays as signed, with two readings and one added case.
      > - **NEW** includes S-12(b)'s derived-NEW: a finding whose Section 7 form lacks the status and that no usable baseline row supplies (ADR-050 D10, as P0-9 amends it).
      > - **The values that follow** include the disposition and the SARIF `level`, which follow the band, and each value's copies in §3 and in the SARIF file.
      > - **The added case.** The class also covers two kinds of finding that its text leaves out, each scored fresh only because the run read no usable baseline: one that Section 7 marks UNCHANGED or UPDATED, and one whose shipped score is its vector's chain held to another category's ±1.0 bound. Run A, which reads the baseline, carries such a score unchanged: ADR-050 D10's step 3 passes its own category's clamp, and step 5 flags another category's `unchecked:cvss_base:bound-n17c`.
      > - **The test for the added case.** All of these hold:
      >   - the stage record states the missing or unreadable baseline;
      >   - the rendered `cvss_base` equals the chain without any bound on the assessment that the run used: the finding's own vector and tags or, for a peer, its primary's assessment with its own tags;
      >   - the shipped value equals the chain on the finding's own vector and tags, held to its own category's ±1.0 range or to one other category's, from `cvss-vectors.md`'s table;
      >   - in Run A, the same finding is carried with the shipped `cvss_base`, and where the range is another category's, it is flagged `unchecked:cvss_base:bound-n17c`;
      >   - the values that follow do so by their own rules.
      > - The record lists each such finding with its Section 7 status, its shipped value, the category whose range gives it, and its rendered value in both runs.
      > - This names the diff's cause, the missing baseline, and doesn't rule the shipped score right. A score held to another category's bound is an N17 ambiguity, which R-10 reports as unchecked, never as a violation (NG2).
      > - A diff in such a finding that fails the test is unattributed.

    - **The sixth class, for the renderers' fixed SARIF values (ruled by the PM at W3, 2026-11-23, ruling 2c)**, verbatim:

      > a fixed value, one that a renderer writes the same way on every run of a release, in `risk-scores.sarif` or `compensating-controls.sarif`, where the shipped file holds another value, whatever its origin (an agent's own value, v4.48.4's placeholder, a passthrough of `threats.sarif`, or the generator that PR 1 retires).
      > - **The fixed values and their sources**, a closed list:
      >   - each rule's `shortDescription`, `fullDescription`, `properties.tags` and `relationships`: the rule with the same `id` in that file's 1.1 template;
      >   - the run's `taxonomies` and the driver's `supportedTaxonomies`: `sarif_common`'s taxa table, as W1's taxa reading fixes it (`contracts/sarif-result.md`);
      >   - the driver's `informationUri` (FR-E.9) and the document's `$schema`: `sarif_common`'s constants;
      >   - the driver's `semanticVersion` and `version`: tachi's release version, `tachi_parts.VERSION` at the oracle's commit.
      >   - *Added at W4 (PM ruling R-B):* each result's primary `locations[0].physicalLocation.region`: the constant `{"startLine": 1}` (ADR-050 D7).
      >   - *Added at W4 (PM ruling R-B):* each `compensating-controls.sarif` `relatedLocations` entry's `message.text`: `sarif_common.EVIDENCE_MESSAGE`, a fixed template filled with the entry's control-category display name and its `file`. Its test fills the template from the rendered entry, and the template is the same in every rendered controls file. Both W4 sources are v4.48.4's own template values, so the change clause below cites nothing for them.
      > - **The test.** The rendered value equals its source's value exactly, as parsed JSON. It is the same in every rendered file of its kind, per rule `id` for the rules' fields. And `tests/scripts/test_sarif_identity.py`, which pins the taxa table to the catalogs, passes at the oracle's commit.
      > - **A change from v4.48.4.** Where a source differs from v4.48.4's own value for the field (its 1.0 template or its agent's mapping), the oracle's record cites the F-374 decision that changed it: FR-E.9 for `informationUri`, W1's taxa reading for the taxa, ruling 2's gap A for `relationships`, and ruling 2c for the version fields. A change that no decision names is unattributed.
      > - **A rule's `security-severity`** follows from its results. Its rendered value is the highest `security-severity` among that rule's results in the same rendered file, as both files' contracts define it, and any result diff that moves it is itself attributed.
      > - **Not in this class:** the driver's `name`, a rule's `id` and a result's `ruleId`, which are identity under D-5, and every markdown value.
      > - A diff in a listed field that fails its test is unattributed.

      The driver's `version` is a contract field the renderers keep (PM W3 ruling 2c, gap C), unless a decision here removes it by name.

    - **The seventh class, D9's rounding normalization (ruled by the PM at W4, 2026-11-24, ruling R-C, from T066's oracle)**, verbatim:

      > a carried finding's composite that ADR-050 D9 step 3 normalized, with the values that follow from it. It is R-11's rounding-only difference, normalized and counted, never flagged.
      > - **The test.** For each such finding, all of these hold:
      >   - the oracle computes the exact composite, unrounded, from the rendered row's four dimension values and the documented weights (0.35, 0.30, 0.15 and 0.20);
      >   - the rendered composite is that value's half-up rounding to one decimal, and the shipped composite is the exact value's other one-decimal neighbour;
      >   - the two bands are equal;
      >   - the finding carries no `corrected` or `retagged` flag on `composite_score`;
      >   - in each rendered `risk-scores.md`, the number of such findings equals §6's "Normalized (rounding only)" line.
      > - **The values that follow**, each checked against its own rule, are attributed with it: §3's composite line and weighted-table rows; the row's position, where the rendered order is D5's on the rendered composites; in the controls files, the inherent score (the rendered composite), the residual score and `security-severity` (inherent × (1 − factor)) and `level`; and a rule's `security-severity`, through class 6's own clause.
      > - A diff that fails its test is unattributed.

    - **The eighth class, the markdown frame values (ruled by the PM at W4, ruling R-D)**, verbatim:

      > a markdown frame value that the renderer writes from the 1.1 template or from the run's own inputs, in `risk-scores.md` or `compensating-controls.md`, where the shipped file holds another value.
      > - **The values and their sources**, a closed list:
      >   - each `## ` section heading: the 1.1 template's heading for the same section number;
      >   - the frontmatter's `schema_version`: `"1.1"` (ADR-050 D15);
      >   - `source_file`: the run's input path, as the plan records it; and `target_path`: the run's `--target`. Each is relative to the working directory;
      >   - the controls frontmatter's `carry_forward_count`: the number of §2 rows whose `CF` cell reads `CF`, or `null` when no baseline controls file resolved;
      >   - `rescan_scope`: `incremental` when that count is above 0, else `full`.
      >   - *Added at the W4 re-run (PM ruling R-H):* the controls §2 `CF` cell, the one row cell in this class, because the count above counts it: `CF` for each finding whose `carried_forward` the run accepted, and `—` for every other row. ADR-050 D2 accepts the claim only for an UNCHANGED finding when a baseline controls file resolved. The oracle derives the accepted set from the run's inputs with its own readers: the findings whose controls part claims `carried_forward` and whose Section 7 status is UNCHANGED, when a baseline controls file resolved. The 1.0 template has the same column and counts carried-forward results the same way, so the change clause below cites nothing for it: D2 moves only its author. No other table cell is in this class.
      > - **The test.** The rendered value equals its source exactly.
      > - **A change from v4.48.4.** Only `schema_version` differs from v4.48.4's own rule for its value, under ADR-050 D15. Every other source is the 1.0 template's own rule: its headings, the input path, the `--target` value and its carry-forward definitions. A change that no decision names is unattributed.
      > - The record lists each diff with the shipped value's origin, as for class 6.
      > - **Not in this class:** narrative prose and the other frame text, which the oracle doesn't value-compare, and every SARIF value. A section that only the rendered file has is additive under NFR-1, not a diff. A section that only the shipped file has is a drop under PM W3 ruling 2's condition 1.
      > - A diff in a listed value that fails its test is unattributed.

    - **The ninth class, a drift-form finding that S-12(b) can't supply (ruled by the PM at W4, ruling R-E)**, verbatim:

      > a fresh finding that Section 7's form gives no component and that no usable baseline row supplies (S-12(b)), whose missing values the renderer fills with its documented placeholders and defaults, where the shipped file held the agent's own.
      > - **The values:**
      >   - its component and its threat, where the form lacks them: the renderer's documented placeholders, each flagged `input:<field>:not-in-form`, and the identity values that follow from them (the §2 cells, `message.text`, and `logicalLocations[0]`'s name, kind and fully qualified name, by `contracts/sarif-result.md`'s rules for a component that no Section 1 or Section 2 row lists);
      >   - its Reachability, where it has no trust zone: ADR-050 D2's documented default, 5.0, and the values that follow from it (composite, band, SLA, review date, position, and the controls files' inherent and residual scores and bands).
      > - **The test.** All of these hold: the finding carries `input:component:not-in-form`; the run read no usable baseline row for it; each rendered placeholder or default equals its documented value; where the default applies, the stage record's warning `reachability-defaulted` names the finding; the rendered composite equals the documented formula on the rendered dimension values; and each controls value follows by its rule.
      > - A diff in such a finding that fails the test is unattributed.

      The placeholders are `Unspecified` for the component and `No threat description.` for the threat, in both renderers (`contracts/module-signatures.md`, recorded at W4 for this class).

    - **The tenth class, D8's group rules (ruled by the PM at W4, ruling R-F)**, verbatim:

      > a correlation property, or ruling C's sentence, that ADR-050 D8's group rules give or withhold, where the shipped file grouped the finding otherwise.
      > - **The test.** The oracle applies D8's rules to Section 4a itself: groups keep their order, and members their listed order, filtered to the file's member set; the first group that lists an ID claims it; a group left with fewer than two members emits nothing. The rendered `correlation-*` properties and the sentence equal its result, and the record names each ID that Section 4a lists in two groups.
      > - A diff that fails the test is unattributed.

    - **The eleventh class, the controls SARIF's text from its own §4 block (ruled by the PM at W4, ruling R-G)**, verbatim:

      > a controls result's `recommendation` or `effort-estimate` that the renderer reads from its own `compensating-controls.md`'s §4 block (ADR-050 D2), where the shipped SARIF held a text other than its own markdown's.
      > - **The test.** Both hold:
      >   - the rendered value equals the What to Implement text, or the Effort, of the rendered §4 block for the finding, decoded, by D2's rule. The oracle reads the block with its own reader, never with a function that the renderer calls to derive the value, such as `tachi_parsers.recommendation_text`, and a rendered value that is empty where the block holds text is unattributed;
      >   - that block's text equals the shipped markdown's §4 text for the finding.
      >
      >   So the only change is that the SARIF now agrees with its own markdown.
      > - A diff that fails the test is unattributed.

    - **The example-defect table and the gating run (ruled by the PM at W4, 2026-11-24).** With class 4 widened and class 6's two added fields, a value diff falls in one of these eleven classes. A diff where the shipped example disagrees with its own input or its own rows goes to the oracle record's own table, closed at W4 to five groups, never to a class. Run A, with each example's own shipped files as its baseline, is the gate. Run B, with none, gates the fifth class, and each of its other diffs takes the disposition of the Run A diff with the same finding, field, shipped value and rendered value (spec, "PM rulings from the build, W4").

    - **The W4 re-run (ruled by the PM, 2026-11-24, rulings R-H and R-I, from T066's re-run).** The classes stay eleven: the eighth also covers the controls §2 `CF` cell (R-H), and the fifth also covers a score that a run with no usable baseline can't carry (R-I). The example-defect table is closed at the re-run's counts: U-4 178, U-12 6, U-15 1, U-17 10, and the Reachability group's 7 findings, with each Section 1 count tested per band. A value that follows by a class's own rule from attributed diffs takes their dispositions, in either run. A row-order entry whose two rows moved under two classes follows both and has no value of its own, and a rule's `security-severity` follows its results by the sixth class's clause (spec, "PM rulings from the build, W4", the re-run).

      **Added by the PM at T066's attribution pass (2026-11-24, ruling R-J)**, verbatim:

      > **a composite with one cause in each of the fifth and seventh classes is joint (5 and 7).** Its shipped value is the seventh class's rounding on the shipped row, and its rendered value follows the fifth class's score. The rule for a value that follows from attributed diffs doesn't reach it, because the rounding is the shipped value's own departure from its row, not a diff that the value follows from.
      > - **The test.** All of these hold:
      >   - the finding's score diff is the fifth class's, in Run B;
      >   - the shipped side passes the seventh class's test on the shipped row: the exact composite, unrounded, from the shipped row's four dimension values and the documented weights, has the shipped composite as its other one-decimal neighbour, and its half-up in the shipped composite's band;
      >   - in Run A, the same finding and field, with the same shipped value, is a seventh-class diff whose rendered value is that half-up;
      >   - the rendered composite is the half-up of the exact composite on the rendered row's four dimension values, and the two rows differ in no dimension but `cvss_base`;
      >   - each copy of the composite (the §2 cell, §3's Composite Score and weighted Composite cell, and the SARIF `security-severity`) reads the same pair.
      > - **How it counts.** Once, in the fifth class, recorded as joint with the seventh. The band, and each value that follows the band, takes the fifth class alone, because the rounding moves no band.
      > - Any other value with causes in two classes comes back to the PM.

- **Why.**
  - Agents that have just read third-party text write the parts (D-2, NFR-10, #360). The closed keys, the strict parse and checking IDs before they become paths make NFR-10 executable.
  - Plan scoping gives D-3's "no stale parts" without a delete permission (KB 21).
  - A digit-free narrative class is the one enforceable form of D-2's rule that "every number the prose states" comes from a slot. The per-field fallback makes a slip cost one field, never the stage.
  - `\d` and `$` admit Unicode digits and a trailing newline (the KB 24 class).
  - Numeric character references split nowhere, and a closed decoder leaves every old parse as it was.
- **Alternatives considered.**
  - **File names chosen by the agent and globbed:** this reopens the stale-part and path-forgery classes.
  - **A numeric regex over prose:** it leaks numbers and blocks identifiers.
  - **Banning only standalone numeric tokens:** versions and ports still fall back, and cited IDs go unchecked, where `name` and `ref` check them.
  - **Rejecting a part for a prose slip:** a typo would end the stage once its lineage ran out of retries.
  - **Decoding GFM's `\|` in the readers:** it changes the `:315` and `:230` rows' parse, against NFR-1.
  - **JSON Schema files:** the standard library has no validator, and a second copy would drift. The code (`scripts/tachi_parts.py`) is the authority, and the shared reference is drift-tested against it.
- **Consequences.**
  - **New files:** `scripts/tachi_parts.py` (loader, validator, guards, identifier patterns, atomic write, digest and stamp) and `.claude/skills/tachi-shared/references/part-file-contract-shared.md`, which every writer agent reads. It holds the slot table and the fixed fallback sentences.
  - **Growth:** `.tachi-build/` grows by about 1 MB per invocation at fixture scale. It is kept, it holds absolute local paths, and it is as sensitive as `{out}`, so adopters ignore `**/.tachi-build/` (FR-E.11).
  - **Residual risks:**
    - a number word that states a count, score, band or percentage ("twelve findings") passes the ban. The contract text forbids it;
    - a digit-bearing term that no slot covers, such as a protocol version or a port, sends its field to the fallback. W5's rate shows whether a slot kind is needed.
- **Supersedes or amends.** ADR-049 D7, by a dated note (2026-11-22, F-374):
  - the scorer and the controls analyzer write only under `{out}/.tachi-build/<stage>/<plan_id>/parts/`;
  - the command-run renderer writes the four files (PR 1);
  - PR 2 extends this to the tree and report writers, under `.tachi-build/trees/` and `report/` (D14).

  The note adds no D10, which #396 adds.

### D4: Where each script runs, in what order, and what failure does [Track: R (scorer, controls); O (threat model)]

- **Decision.**
  - **Exit codes.** They are shared by every F-374 entry script. Codes 0–2 keep `tachi_parsers`' meanings.

    | Code | Meaning | The caller's next step |
    |---|---|---|
    | 0 | done | continue |
    | 1 | an input is missing or unreadable | stop and print the error |
    | 2 | a validation, usage or guard failure; a plan digest or pointer mismatch (D3); a forbidden character in an input (D3, P0-4); or Python below 3.9 (checked before any import) | stop, and run the fail step if a plan exists, with three exceptions (below) |
    | 3 | batches are pending (`reconcile` only; no other script returns it) | dispatch exactly the listed batches, then reconcile |
    | 4 | unrecoverable: a cap or the budget is exhausted, or a completeness or parity check failed | run the fail step |
    | 5 | done, with warnings (undeclared paths, FR-E.10, R-24, a reissued ID) | print the warnings and continue |

    **Row 2's exceptions** (Architect re-review RR6):
    - `attack-chains.py plan` and `render`: the orchestrator ignores their codes, 2 included, and continues (R-24, D13);
    - `attack-chains.py check`: argparse exits 2 on a usage error, so its codes are 0, 2 and 5. The command prints a 2 and continues, as R-24 asks of every chain-check event;
    - `fail`: its own 2 means stop with the error, and `fail` never runs a second time.

    This is the one exit table. `contracts/cli.md` copies it, with each script's codes and these exceptions.

  - **Presence check (KB 20; PM plan review, finding 7).**
    - All three commands run `python3 scripts/tachi-stage.py --version` in Step 1, before any dispatch. The script checks the 3.9 floor before any import, prints the version it found, and exits 2 below the floor.
    - If `python3` is missing or the floor fails, the command stops with `PYTHON 3.9+ NOT FOUND — tachi renders this stage with Python 3.9 or later (found: <version, or none>); install it and re-run`.
  - **Scorer and controls (PR 1).** Everything runs in the main session, at depth 1.
    1. Step 1: prerequisites and the presence check.
    2. Step 1.5: the populator (`/tachi.risk-score` only, unchanged), before anything reads `threats.md` (ADR-046 D2).
    3. Step 2: `tachi-stage.py plan`. It reads the reference set, so S-12(c) exits 2 before any dispatch.
    4. Step 3: dispatch the waves, in the foreground, with the fixed prompt.
    5. Step 4: `tachi-stage.py reconcile`, looping while it exits 3. On 4, go to Step F.
    6. Step 5: the renderer (`render-risk-scores.py` or `render-compensating-controls.py`).
       - It re-validates every part.
       - It computes the values.
       - It writes both files, stamped, to `<plan_id>/staged/`.
       - It re-reads the staged files from disk through `tachi_parsers`, and checks row parity against the reference set, SARIF N/N and `.md`–`.sarif` agreement, on decoded values (KB 22).
       - It reads the staged markdown back through the reader the next run uses, and every open finding must come back as rendered (P0-1; ruled at W3, 2026-11-23): through `read_baseline_scores` for `risk-scores.md`, in renderer form wherever its sub-scores were written and with its owner, SLA, disposition and review date; through `parse_controls_assessment_inputs` for `compensating-controls.md`, each item equal to the validated one, with no error.
       - **The standing rule (ruled at the P1 checkpoint, 2026-11-24, P1-4).** A from-disk check compares each written value with its source, the validated part or the computed row. It never compares it with a second read of the file by the reader that produced it (KB 22), because a defect in that reader would agree with itself. Today's instances:
         - the controls `recommendation` and `effort-estimate`, each checked against the validated part's body: the first since T067b's H1, the second since PR 1's W6 batch (P1-4);
         - the scorer's read-back above, which compares the rows' form and their owner, SLA, disposition and review date with the computed rows. Comparing every value the next run reads, legacy prose included, is T080's, in one change with T067a's L8 reader fix.
       - Neither staged file may hold a character that `tachi_parts.forbidden_character` returns, D3's step-10 set or, since W3, a lone surrogate: not the raw markdown, and not any decoded string or key of the SARIF (P0-4).
       - Only when every check passes does it move each staged file onto its canonical name with `os.replace`, on the same filesystem. A failed check leaves the canonical files untouched.
       - It runs the declared-paths check and writes the stage record.

       A 0 or 5 means success. Anything else goes to Step F.
    7. Step 6: print the renderer's summary, so the model restates no number.
    8. Step F: `tachi-stage.py fail`, then stop with the error.
  - **`/tachi.threat-model` (PR 2).** [O] is the orchestrator, at depth 1, dispatching at depth 2. [M] is the main session.
    - The Step 2.5 and Step 3 anchors stay, and Step 2.6 stays free for #396 (P-2).
    - D11–D14 own each phase's content.

    | # | Who | Step |
    |---|---|---|
    | 1 | [M] | Steps 0–1.4, plus the presence check |
    | 2 | [M] | Step 1.5 (PR 2): `tachi-stage.py plan --stage threat-model`, the run-level plan. It takes no `--threats` and plans no units: it copies the four canonical files' pre-images and snapshots `{out}`, so `fail` and `close` have a plan |
    | 3 | [O] | Phase 1 persists the inventory and the dispatch table (D11) |
    | 4 | [O] | Phase 2: plan, dispatch, reconcile, and re-dispatch per component (D6's batch-stage table, item O-α) |
    | 5 | [O] | Phase 3 compiles: deduplication, correlation and the ID map (D11). Then Phase 3.6 sets every finding's pattern and adds any `AGP-` findings, and Phase 4 composes Sections 5–7, with no SARIF. Both come before any part is written, because Sections 4b and 7 carry their results |
    | 6 | [O] | The `threats-md` parts, then the shipped joiner, `join-threats-md.py` (item O-β) |
    | 7 | [O] | Phase 3.5's chain script on the joined file (D13), then the Phase 3.7 populator |
    | 8 | [O] | Phase 5 (D14): the tree batches (plan, dispatch, reconcile); then `assemble-report.py trees`, which copies the carried trees and merges the manifests; then the report batches |
    | 9 | [M] | Step 2.5: the populator re-assert, unchanged |
    | 10 | [M] | Step 2.7, added in PR 1: the FR-E.18 carrier write, `tachi-stage.py architecture-source` (D7). PR 2 adds `tachi-stage.py id-mark`, which writes the high-water mark line (D7, ruling B) |
    | 11 | [M] | Step 2.8, the checks, in this order (PR 2): `attack-chains.py check` (FR-K4.1b; exits 5 on an R-24 rewrite), then `check-threat-model.py` (FR-N4.5, FR-N4.6 and P-11 exit 4 on failure; FR-E.10 and a reissued ID exit 5). Each writes its events to a hand-off file under `threat-model/<plan_id>/checks/`, which `close` or `fail` folds into the stage record |
    | 12 | [M] | Step 2.9 (PR 2): `assemble-report.py report`. Its FR-K5.3, FR-K5.5 and FR-K5.7 checks exit 4 on failure |
    | 13 | [M] | Step 2.10 (PR 2): `generate-threats-sarif.py`, after every `threats.md` writer (the orchestrator authors no SARIF; RK-4). Then `tachi-stage.py close`, which runs the declared-paths check and writes the stage record. Then Step 3 |

  - **D-3's three paths.**
    1. **A typed agent can't be spawned.** The Agent call fails, and the command runs Step F with `agent-not-spawned`. In the threat model, the orchestrator stops (text, S), and in PR 2 the command runs `fail`.
    2. **A provenance or completeness check fails.** A Step 2.8 check exits 4 (PR 2), or the renderer's from-disk parity check does (PR 1).
    3. **An unrecoverable batch.** `reconcile` exits 4.

    **Path 1's bounds (ruled at W1, 2026-11-22, T023).**
    - A shipped script that an agent or command file names, but that isn't installed, is path 1's installation case. The run stops with an error that names the script and gives the `scripts/install.sh` remedy, and nothing is written in its place (N14).
    - A typed agent that was spawned and then failed isn't path 1. In PR 1 it stays the coverage gate's `dispatch_failure` warning, and from PR 2, FR-N4.7's detector re-dispatches it.

    Every error follows today's installer-message pattern:

    ```
    TACHI <STAGE> FAILED: <reason>
    Batch <id>: <IDs>   (or: Agent: <type>)
    Remedy: <text>
    Kept for diagnosis: <plan dir>
    ```
  - **Failed outputs (P-4; no N7 change).**
    - Only shipped steps write canonical files: atomically, and only after full validation.
    - The planner records the digest of each existing canonical file of its stage, and copies the file into `<plan_id>/preimage/`.
    - `fail` writes the failed stage record first. It then moves into `<plan_id>/failed/`, with `os.replace` and never overwriting, any canonical file whose bytes have changed since the plan, and puts the pre-image copy back in its place when the copy's digest matches the recorded one. Each moved or restored file must be a regular file directly in `{out}`, named in the stage's closed set (KB 21's double gate).
    - So a check that fails on the staged files changes nothing, and a half-applied pair, or a threat-model output written before a check failed, gives way to the earlier run's file.
    - The sets are:
      - threat model: `threats.md`, `threats.sarif`, `threat-report.md` and `attack-chains.md`;
      - scorer: `risk-scores.{md,sarif}`;
      - controls: `compensating-controls.{md,sarif}`.
    - Outputs of an earlier successful run stay where they are.
    - Every auto-detect site, including the baseline search, matches exact names one level down, so none can select a failed run.
  - **Stamp (FR-E.7).**
    - The stamped markdown files are `risk-scores.md` and `compensating-controls.md` (PR 1), and `threats.md`, `threat-report.md` and `attack-chains.md` (PR 2). Each renderer writes `<!-- tachi-provenance: renderer=<entry>; version=<X.Y.Z>; input-digest=sha256:<hex> -->` at the end. Prose can't forge it, because `<` is escaped.
    - In `threats.md`, the populator's block can follow the stamp (`populate-affected-assets.py:323-351`), so readers take the last provenance comment in the file.
    - All three SARIF files carry `runs[0].properties.tachi_provenance` = `{renderer, version, input_digest}`.
    - `version` is a constant in `tachi_parts.py`, kept current by release-please (`x-release-please-version`). Release-please bumps it in its own PR, where the f374 jobs run, so the goldens read the constant, never a literal.
    - `input_digest` is the SHA-256 of the canonical JSON of the source digests, the accepted parts' `items` and `fragments` in plan order, and the parameters. It excludes the plan ID, so output stays byte-stable (NFR-2).
  - **Declared paths.**
    - The plan snapshots the `{out}` tree: each path, its size and `mtime_ns`. Above 20,000 entries the check is skipped, with a warning.
    - Every path new or changed since then must match the stage's grammar: its canonical files and D3's exact layout (in PR 2, also `architecture.md`, `attack-trees/*` and D11–D14's names).
    - Anything else, such as a `gen.py`, goes to `undeclared_paths` and exits 5. SC-3 is measured, not gated (KB 17).
- **Why.**
  - Only code makes the retry cap and "no partial output presented as complete" hold, whatever the model does (D-3).
  - Exact-name auto-detect plus moves scoped to the run keep N7 untouched (NG3).
  - The populator goes first (ADR-046 D2).
  - The checks run in the main session (FR-N4.5).
  - Generating SARIF after the checks takes a phase off the orchestrator (RK-4).
- **Alternatives considered.**
  - **In-place `*.FAILED.*` names:** eight more declared tokens, and a second failure overwrites the first.
  - **Exit 0 with a JSON "pending" status:** the model would decide when to stop.
  - **Failing a run on undeclared paths:** it would gate model behavior (KB 17).
  - **A plan ID in the stamp:** it would break NFR-2.
- **Consequences.**
  - **One commit (C7) changes the permission tables and the runbook:**
    - §8.3: the scorer's Writes cell becomes `{out}/.tachi-build/risk-score/{plan-id}/parts/`, and the controls analyzer's becomes `{out}/.tachi-build/compensating-controls/{plan-id}/parts/`, with `{plan-id}` added to §8.2's placeholders (D3);
    - §8.4: each command row adds its stage directory, and `/tachi.compensating-controls` gains `python3` in "Bash it instructs" and "Child processes";
    - §8.5: the four rendered files are "Written by" the renderer, run by the command;
    - the runbook's §5 follows suit, and R-27 re-validates it;
    - PR 2 adds `{out}/.tachi-build/threat-model/`.
  - **Tests:** one per failure path and one per exit code.
  - **Risk:** a model that ignores exit 4. The stage record's `status` and the missing stamp expose it, and SC-3 counts it.
- **Supersedes or amends.**
  - **ADR-046:** D1 for the scorer and controls files (PR 1) and for `threats.sarif` (PR 2); D2's order becomes script order.
  - **ADR-017:** D4 is the precedent.
  - **ADR-049:** D5 holds.

### D5: Scoring constants and arithmetic [Track: R]

- **Decision.**
  - **Modules.**
    - `scripts/tachi_scoring.py` (Track S, W1) is the CVSS module. It holds the calculator moved from `tests/scripts/test_cvss_category_defaults.py:34-87`, plus `elevate()`, the embedded constants and the arithmetic below, and it keeps FIRST's 16 examples as `self_test()`. The renderer runs the self-test at start-up and fails closed.
    - **The scoring-rules module is ruled in.** `scripts/tachi_scoring_rules.py` (Track R, the second W2 lane) holds R-25's asset outcome, R-26's tolerant reader, R-31's peer, override and scoring-date rules, ruling A's tag-driven rule, and R-6's resolver (D9): pure functions over `tachi_scoring` and `tachi_parsers`, reading only the paths they're given. The signatures freeze at the end of W1, and PR 1's 8.0-day central, against TW-0's 9.0, stands.
    - **The frozen signatures (W1, 2026-11-22, T023)** are in [`contracts/module-signatures.md`](../../../specs/374-large-architecture-pipeline-resilience/contracts/module-signatures.md). That file covers the scoring-rules module, lane P's new `tachi_parsers` functions, and the persisted-inputs format that `risk-scores.md` §6 and `compensating-controls.md` §7 share. Additive changes keep the freeze. A rename, removal or type change needs an architect amendment to that file.
  - **Constants**, embedded as `Decimal` strings: weights; bands with SLAs and dispositions; the eight category vectors; D10's prefix map; tag forces and the 9.2 ceiling; the P0 reduction factors; reachability baselines, ranges, keyword adjustments and caps. One drift test loads `schemas/risk-scoring.yaml` and `schemas/compensating-controls.yaml` (PyYAML, test-only) and compares every value. A second compares the reachability tables with `reachability-analysis.md`. The doc-drift tests stay, now importing the shipped calculator.
  - **Arithmetic.**
    - No float enters stored-value arithmetic. Values come from strings, or from JSON parsed with `parse_float=Decimal`, under a module-private context.
    - `q1(x)` is `quantize(Decimal("0.1"), ROUND_HALF_UP)`. It rounds the sub-score means, the composite (`0.35C + 0.30E + 0.15S + 0.20R` over the stored one-decimal values), the residual (`inherent × (1 − factor)`, so 4.55 gives 4.6) and the reduction percentage.
    - **CVSS** uses FIRST §7's equations in float, as the calculator does, then Appendix A's integer Roundup. The result enters `Decimal` as an integer count of tenths. Roundup is used only for CVSS, and `q1` never is. The bound is `max(0, d − 1)` to `min(10, d + 1)`, in `Decimal`.
    - **One band helper**, `band(x)`, refuses a value not already quantized to 0.1. Its minimums are inclusive: 9.0 Critical, 7.0 High, 4.0 Medium, Low below.
    - **Distributions that must sum to 100** use ADR-017 D2's largest remainder, in integers: floors of `100·n // total`, remainders `100·n % total` descending, ties by label ascending, all zero when the total is 0. Totals are exact sums.
    - **Dates.** The date is an input (`--date YYYY-MM-DD`, required and passed by the command); the clock never enters rendered output. SLA days: `<n>h` gives ⌈n/24⌉, `<n>d` gives n, and anything else is unparseable. A review date is a date plus SLA days, in calendar arithmetic.
  - **Sort.** By score descending, then S-2, replacing "natural alphanumeric" (`output-formatting.md:31`).
- **Why.**
  - NFR-2 and C-10: Python's `round()` gives 4.5 for `residual-risk.md:112`'s 4.55, and Roundup isn't half-up (research item 18).
  - R-32 and KB 26: Patch A found a hand-typed agentic score that had drifted from its vector, and one test over every embedded constant catches the next drift.
  - Feasibility §13.2: without the module, the risk-scores lane carries 2.7 days and the one-bundle central is about 10.5.
- **Alternatives considered.**
  - **Load the YAML at run time.** PyYAML would then sit on the core path (S-11).
  - **CVSS in `Decimal`.** It would diverge from FIRST's float arithmetic, which the 16 examples pin.
  - **Rules inside the risk-scores renderer.** That brings back the 2.7-day lane.
- **Consequences.**
  - **Files.** Both modules join the manifest's three places, `REQUIRED_SCRIPT_NAMES` and F-373's S-13 import gate's allowance (D16). The calculator test's `paths:` entry gains `tachi_scoring.py` (KB 3).
  - **Tests.** Goldens for 4.55, composites of exactly 4.0, 7.0 and 9.0, and x.x5 sums; Roundup of 0.1 + 0.2 and FIRST's 16; largest-remainder ties; `band(4.55)` raises; byte-identical output under a patched clock; the core path with `yaml` blocked.
  - **Risk.** S-2 reorders rows with equal scores relative to today. The release notes (item 4) say so, and the oracle attributes the reorder as its own class (NFR-1).
- **Supersedes or amends.** ADR-017 D2 extends to the renderers' percentages (a dated note). ADR-024 is unchanged (NG7).

### D6: Batching and overflow [Track: S (planner, error); R and O (ownership per layer)]

- **Decision.**
  - **Sizes.**
    - S-1 sets the budget: at most 8,000 tokens per single write and 32,000 per batch.
    - The sizes are constants in `tachi-stage.py`, not adopter settings. Until W0 they are `risk-score` 40, `compensating-controls` 30 and `trees` 12.
    - At the contract's maxima a scorer item is about 600 tokens and a controls item about 1,600, so the measured sizes may fall well below these. `/aod.tasks` prices the live matrix at the measured p90, which may double the planned dispatches (C-3).
    - At or below its size, a stage plans one batch, so the agent is invoked once (NFR-4).
    - Tests can set smaller sizes only through the planner's function interface.
  - **The W0 measurement.**
    - Per stage, u = the p90 of the per-unit output bytes ÷ 4, × 1.25 for the envelope. W0 measures a proxy on the v4.48.4 outputs of the shipped examples, and W1 confirms it on the pre-fix fixture run (D-7), because the fixture exists only from W1.
    - Size = min(⌊8,000 ÷ u⌋, ⌊32,000 ÷ (u × files per unit)⌋).
    - The result is recorded as an "Amended at W0" table, with a Revision History entry. The stage record logs each live part's size, and an overflow invokes TW-L2.
  - **Amended at W0 (2026-11-22, T023, from T003's measure and gate G0).** The constants in `tachi-stage.py` are:

    | Stage | The unit, as its writer emits it | Files per unit | u (tokens) | Size | Row A, the literal proxy | Planning value |
    |---|---|---|---|---|---|---|
    | `risk-score` | one scorer part item (D3) | 1, the batch's part | 475 | **16** | 9 | 40 |
    | `compensating-controls` | one controls part item (D3) | 1, the batch's part | 603 | **13** | 9 | 30 |
    | `trees` | one tree file | 1 | 656 | **12** | 12 | 12 |

    - **The reading.** u is the p90 cost of what the stage's writer emits per unit.
      - The scorer and the controls analyzer write one JSON part per batch, in one Write. The part holds one item per finding, with only D2's judgment fields. So S-1's 8,000 tokens bound the whole part, and the batch-total term never binds.
      - A tree keeps its v4.48.4 shape, and each tree is one Write. An agent can issue several Writes in one response, so for trees the single-write term binds, not the batch total's 48.
    - **The measure** (T003's shipped-example corpus, `test-results/s1-proxy.md`). For the two part stages, it is §4 row E's contract-shaped item, plus the two terms that row E left out:
      - D3's numeral ban: each number in carried narrative becomes a slot token, and so does each computed cell of the controls `matrix_row`;
      - the agent's JSON layout, at two-space indentation.

      The p90 is 1,520 bytes for the scorer (row E's 1,190, plus 236 for the slots and 94 for the layout) and 1,930 for controls (1,811, plus 57 and 62). Then u = bytes ÷ 4 × 1.25, and size = ⌊8,000 ÷ u⌋. Trees take row A as measured.
    - **Not adopted.**
      - Row A (9 and 9) measures v4.48.4's heavier file per finding. Most of that file is now the renderer's, and the envelope factor would count an envelope twice. It would plan about four times the plan's dispatches.
      - Row E's own values (21 and 14) would put the p90 part at about 9,980 and 8,440 tokens once the slots and the layout are counted, over S-1's 8,000.
    - **Cross-check.** At the part contract's required-field maxima, with each scorer rationale field at 400 characters, the scorer's size is 11.
    - **Known limit.** The shipped controls outputs carry little code evidence, so the controls proxy understates evidence-rich targets. W5's stage records, which log each live part's size, check it under TW-L2.
    - **Cost.** On the base set (390–450 open findings), a stage-run plans 25–29 scorer batches and 30–35 controls batches. That is about 2.3–2.5 times the plan's 10–12 and 13–15, against 44–50 at row A. T062 prices F17 (T073, T074) from these counts.
    - **Confirm or re-amend from T021(a), before W1's push.** T021(a) records two things from the v4.48.4 scorer run on the fixture:
      1. the per-unit text of whatever `risk-scores.md` the run wrote, measured by the method above;
      2. for each Write of a whole output file, the file's UTF-8 bytes, and the output tokens of the response that carried the Write, from the session's usage records.

      The rules, decided now:
      - A fixture size at or above a constant confirms it. One below it re-amends the constant to the fixture's size.
      - A JSON file with at least 3.2 bytes per output token confirms the ÷4 estimator within the 1.25 envelope. A lower ratio re-amends both part stages with the measured ratio in place of 4, but only where the record separates that response's thinking. Otherwise the estimator stands, and the record says so.
      - If the run wrote no per-unit output before it failed, the constants stand, and the record says so.

      Each re-amendment adds a Revision History row. The trees aren't measured at W1: PR 2's fixture runs (T130) confirm them.
    - **SC-8's example (P-7).** Both part sizes are at least 11, so `ascii-web-api`, with 11 open findings, is one batch in both stages, as G0 routed. A re-amendment below 11 returns P-7's example to the PM before T021(b).
  - **At W1 (2026-11-22, T023, from T021(a)): a calibration Write decides, before T021(b).** T021(a) (`test-results/prefix-baseline.md` §5) gave neither rule a valid input:
    - **The per-unit text.** The v4.48.4 scorer handed back a script, so the rationale in `risk-scores.md` is a script's template, not model prose. The size of 13 there measures v4.48.4's markdown unit, which the W0 reading rejected. So the first rule doesn't fire, and the W0 measure stands until W5's live parts confirm it.
    - **The ratio.** No JSON part was written, so the 3.2 test had no input. But every reading in the session's usage records was below 3.2:
      - 2.4–2.6 bytes per token for markdown and prose;
      - 2.8–3.0 for a pretty-printed JSON file, read as input;
      - 2.04 for the one Write, whose content is JSON-escaped in the tool call.

      So ÷4 is probably optimistic for a part. The constants aren't confirmed on that evidence, and they aren't re-amended on it either, since none of it is a part Write.
    - **The second rule, made continuous.** Below 3.2, u = p90 bytes ÷ r, where the measured ratio r replaces both ÷4 and its 1.25 slack. At 3.2 that gives the same u as ÷4 × 1.25, so the sizes no longer jump there. The rule as written kept the 1.25, which counts the slack twice.
    - **The calibration (lane L, before T021(b)).**
      - **The files.** In a scratch directory (H1), build two `tachi.part/1` objects at two-space indentation, by the W0 measure (row E's items, with slots, from the shipped examples): 16 `risk-score` items of about 1,520 bytes each, and 13 `compensating-controls` items of about 1,930 bytes each, within ±5%.
      - **The session.** In a T141 adopter at its install commit, open a fresh session arranged as T021(a)'s was. Dispatch `tachi-risk-scorer` in the foreground, the pinned model at medium effort, once per file, with the prompt: write this JSON to `<absolute path>` in one Write call, byte for byte, and reply with nothing else.
      - **The measure.** r = the file's bytes on disk ÷ (that response's `output_tokens` − `thinking_tokens`), from the subagent's usage record. A file that differs from its source is re-run once.
      - **The cost** is about 20–25k output tokens.
    - **The outcome follows without another ruling.** For each stage, the size stays at 16 or 13 when r ≥ 3.2. Below that it is ⌊8,000 × r ÷ 1,520⌋ for `risk-score` and ⌊8,000 × r ÷ 1,930⌋ for `compensating-controls`, so at r = 2.5 they are 13 and 10, and at 2.8 they are 14 and 11. `trees` stays 12 until T130.
      - **P-7.** It stands with `ascii-web-api` if both sizes are at least 11, that is, r ≥ 2.654 for controls and r ≥ 2.09 for the scorer. Otherwise P-7's example goes to the PM before T021(b).
      - T018 takes the resulting constants, and T023 adds their Revision History row.
    - **The response cap.** T021(a)'s requests carried `max_tokens` 128,000. PRD D-2's 64k is the cap that Runs A and B hit, and it is accurate as history. S-1 still designs against 32,000, and the fixture's outputs exceed 128k (1.49× and 1.76×). So the PRD and the spec don't change.
      - T020's sizing check (lane F) notes that its 64k constant is Runs A and B's cap.
      - T079's release notes say that the cap depends on the environment.
  - **Amended at W1 (2026-11-22, T023, from the calibration, `test-results/prefix-baseline.md` §8).** The constants in `tachi-stage.py` are:

    | Stage | r (bytes ÷ visible tokens of the Write) | Size | W0 |
    |---|---|---|---|
    | `risk-score` | 2.598 | **13** | 16 |
    | `compensating-controls` | 2.781 | **11** | 13 |
    | `trees` | not measured | **12** | 12 |

    - **Each stage takes its own r,** as the rule above reads ("for each stage"). Each stage writes its own part type, and r follows the content mix: half of the scorer part is structure, and three quarters of the controls part is text.
      - The check on the measured parts: 13 × 594 and 11 × 706 real tokens are 7,722 and 7,766, both within S-1's 8,000.
      - The record's r slightly overstates the cost: the file path is in the call, and the content travels JSON-escaped.
    - **P-7 stands.** Both sizes are at least 11, so `ascii-web-api`, with 11 open findings, is one batch in each stage. Controls has no margin left, so W5's stage records (each live part's size) re-check it under TW-L2.
    - **Cost, for T062.** On the base set (390–450 units), a stage-run plans 30–35 scorer batches and 36–41 controls batches, in 2–3 and 3 waves. W5's matrix (T073, T074) plans 132–152 dispatches, against 46–54 at the planning sizes.
    - **SC-8's controls target** is the same in T021(b) and T075.
      - It is a copy of the fixture's committed stub codebase, at T019's commit, placed at one fixed path in each adopter, outside tachi's installed paths and outside `{out}`, and committed in the adopter's restore point.
      - It is passed as `--target <that path>`, never the default `.`, whose installed tachi files differ between v4.48.4 and the branch build.
      - `sc8-baseline.md` records the copy's tree digest, and T075 checks it.
  - **One planner, three layers.** `tachi-stage.py plan` runs only where Bash runs:
    - the command, for the scorer and controls, and for the threat model's run-level plan (D4);
    - the orchestrator, for Phase 2, the trees, the `threats.md` part boundaries and the report batches (D14).

    It reads its stage's input once and copies each batch's unit rows into its batch input, so no layer re-reads `threats.md`. Each plan has a fresh ID, and the digests of its inputs and of each batch input. A change to either makes `reconcile` or the renderer exit 2.
  - **Track O's batch stages.** Two are ruled here:

    | Stage | Unit | Planner input | Payload | Reconcile |
    |---|---|---|---|---|
    | `trees` | one open Critical or High finding whose tree is generated: the missing ones under Rule 1, all under Rule 2 (D14) | the joined `threats.md`'s reference set, and the baseline's `attack-trees/` listing | the part is the batch manifest: D3's envelope, with one item per finding, `{finding_id, delta_status, action, similarity_score}` (the last under Rule 3 only). Each tree is one Write, within S-1's 8,000 tokens, to the path its batch input names under `<plan_id>/trees/` | done when the part validates and every named tree passes `assemble-report.py trees`' per-file checks. A missing tree makes the batch `missing` |
    | `report` | one section part (D14's three fixed and three conditional sections), or a batch of findings for the per-finding sections | the reference set, the outcome record, the merged tree manifest, and whether a baseline exists | D3's envelope. A section part has `finding_ids` `[]` and its text in `fragments`, keyed by the template's paragraph keys for that section. A findings part has one item per finding, whose keys are item O-γ | as for every part (D3, D6) |

    The other two stages, and the `report` stage's payload, are named items, ruled before W2′, each with a contingency that `/aod.tasks` prices as its own line:
    - **O-α, `phase2`.** The unit (one planned dispatch, from `phase1/dispatch.json`); whether the planner or the orchestrator allocates dispatch and re-dispatch IDs; how a dispatch record stands in for a part, since the agents can't write; and the reconcile rule that enforces this decision's cap over records. The end-marker predicate inside it still waits for S-9's table. *Contingency:* a records mode in `tachi-stage.py reconcile`, with its tests, in lane O2.
    - **O-β, `threats-md`.** The unit (a section, with table sections split by rows, S-1); where the planner gets units before the join, such as a section manifest the orchestrator writes after Phase 4; the part payload, which holds model-authored table rows while SV-2b is carved; and the joiner's structural checks (heading order, table headers against the template, one Section 7 row per ID, Section 4c's set). *Contingency:* the manifest and payload schemas, and the joiner's checks and tests, in lanes O3 and OC.
    - **O-γ, the `report` payload (Architect re-review RR4).** The keys of a findings part's items; what the "rows" that D14 says parts hold look like; where the Medium and Low category summaries go, since they aren't per finding; and whether one findings part spans `threat_analysis`, `remediation_roadmap` and `appendix`. *Contingency:* the payload schemas, their validator cases and the assembly tests, in lane T.
    - **RR3, the report assembler's plan check, ruled with them (Architect re-review RR3).** Both `assemble-report.py` modes take `PLAN`; the orchestrator's return carries each batch stage's final `plan_id` and `plan_digest`, so the main session can pass them to `report`; and each batch stage's stage-record writer is named.
  - **Overflow error (advisory).**
    - A writer agent writes a `tachi.overflow/1` object at its part path.
    - A read-only Phase 2 agent ends its reply with `TACHI-OVERFLOW <object>`, which D11's record keeps verbatim.
    - Both are counted, but no decision depends on them: a missing part triggers the same retry. `schema` selects the overflow key set first (D3), so a well-formed overflow object is never `invalid`.
  - **Resume** reconciles from disk. Each batch is `done`, `missing`, `overflow`, `unparseable` or `invalid`. The model keeps no state of its own: it dispatches what `reconcile` lists, until `reconcile` exits 0 or 4.
  - **Retry cap (P-8), the same in every layer.**
    - At most 2 retries per lineage, and at most 2 × the planned batch count in retry dispatches per stage. `retry_budget.used` counts retry dispatches, so a halving counts 2.
    - On `missing`, `overflow` or `unparseable`, the batch is halved (minimum 1 unit; children `B003-1` and `B003-2`).
    - On `invalid`, it is retried with the same members.
    - In Phase 2, the first retry goes per component, and the second repeats it.
    - Exhaustion exits 4 and names the lineage and its IDs.
  - **Limits (S-8).**
    - At most 16 in flight per wave, which leaves margin under 20.
    - Depth below the main session:
      - the scorer and controls: 1;
      - Phase 2: 2;
      - the report agent: 2;
      - the trees: 2.

      The orchestrator dispatches and reconciles the tree batches itself, before the report agent. This is D-3's first option; the report agent has no Bash, so it can't reconcile.
    - No path reaches 3 unless D14 keeps a report sub-dispatch.
    - Every dispatch runs in the foreground.
    - **Note (2026-11-22, T023, from the W1 calibration).** In Claude Code 2.1.330 the Agent tool has no foreground option, so every dispatch runs in the background. A main session waits by ending its turn and resuming on each completion notice.
      - **What holds instead.** The intent stands: no result is used before its agent completes, and no agent outlives the layer that dispatched it (KB 22). Wherever this ADR says "foreground", here and in D4's Step 3, the rule is:
        - a wave's agents run at most 16 at once;
        - the layer dispatches every wave that `plan` or the latest `reconcile` listed before it runs `reconcile`, and it runs `reconcile` once, after every agent of those waves has reported completion;
        - while any agent it dispatched is still running, it runs no renderer, reports no result, doesn't end the stage and doesn't return to its own caller.
      - **The command text (T030, T038)** says this in these words: "Dispatch every wave that `plan` or the latest `reconcile` listed, in order, before you run `reconcile`. Run `reconcile` once, after every agent of those waves has reported completion. While an agent you dispatched is still running, don't run the renderer, report a result or end the stage. If you end your turn to wait, resume this loop on each completion notice." The shared part-file contract quotes them too. `test_contract_text_374.py` pins those sentences in both commands, the contract and this note, not the word "foreground".
        - **Amended at W4 (2026-11-24, T146, from T067b's H2).** The first wording named only "the wave", so it could be read as one `reconcile` after each wave. `reconcile` can't tell a batch that was never dispatched from one whose agent wrote nothing, so it plans a retry for both: it halves the batch, or retries a one-unit batch with the same member. One early `reconcile` therefore spends retry budget on every batch of the later waves. At the base set's 2–3 waves, a `reconcile` after each wave can exhaust a lineage or the stage's budget, so `reconcile` exits 4 and the stage fails. With one wave, as in SC-8's runs, the two readings agree, which is why no offline test or small run showed it. The rule now names every listed wave and one `reconcile` after them. No script changes: `reconcile` still reads only the disk.
      - **The spec's "foreground"** in S-8 and FR-E.14 names a mechanism this platform lacks, so it goes to the PM as an erratum. It blocks nothing, because the intent is unchanged.
      - **For PR 2.** Whether a dispatching subagent (the orchestrator, at depth 2) can wait for its children's completion before it returns is a question for the S-9 spike (T104), before O-α is ruled (T086). If it can't, dispatching Phase 2 from the command layer, today an S-16 follow-up, becomes PR 2's design question.
  - **The S-9 spike** runs in W2′, under the published profile, before FR-N4.7's detector is built (Track O).
    - It plants four failure classes: a stop mid-reasoning, a stop mid-output, a stall and an empty return.
    - Its layout table goes in `specs/374-large-architecture-pipeline-resilience/test-results/`, and D11's end-marker predicate is built against it.
    - PR 1's reconciler reads only the disk, so it doesn't wait on the spike.
- **Why.**
  - D-3: batching belongs to the dispatching layer, and a `max_tokens` stop can return nothing.
  - S-1, S-8 and KB 22: orphaned background children have outlived their parent.
  - KB 25: spike the overflow signals before building the detector.
  - A missing part's cause can't be read from disk, so halving the batch is the safe response.
- **Alternatives considered.**
  - **Retries judged by the model:** unbounded, and untestable.
  - **Trees dispatched by the report agent:** depth 3, and a resume loop with no code behind it.
  - **Waves of 20:** no margin left for the dispatcher itself.
  - **Sizes adopters can tune:** S-1 makes them constants.
- **Consequences.**
  - A lineage that halves twice takes 7 dispatches, 6 of them retries, so a stage budget of 2 × P covers that for at most a third of P planned batches. With one planned batch, the first halving spends the whole budget.
  - The sizes enter at W0 as a proxy, confirmed at W1.
  - Phase 2's predicate waits for S-9's table.
- **Supersedes or amends.** Nothing.

### D7: SARIF identity [Track: R for the scorer and controls files and the carrier; O for `threats.sarif`]

- **Decision.** GitHub matches an alert on four parts: the tool and upload category, the `ruleId`, `primaryLocationLineHash` and `artifactLocation.uri`. D7 pins all four for each file. Nothing else is identity: message, level, scores, logical locations and properties can change without re-keying.

  | File | Tool (R-33) | Upload `category` | Re-key event |
  |---|---|---|---|
  | `threats.sarif` | `Tachi` | `threat-model` | once, at PR 2, with its upload line |
  | `risk-scores.sarif` | `tachi-risk-scorer` | `risk-score` | once, at PR 1 |
  | `compensating-controls.sarif` | `tachi-control-analyzer` | `compensating-controls` | once, at PR 1 |

  - **Categories.** Each is the command's name. No file carries `runs[].automationDetails`, so the upload step's `category` input governs (S-6). tachi recommends a category and never writes one.
  - **`ruleId`.** A constant function of category, shared by all three files (ADR-013 D2).
    - The values are the eight IDs in `sarif-specification.md`'s mapping table, including `tachi/ai/agentic-threats` and `tachi/ai/llm-threats`.
    - One prefix map sends `AG`, `AGP` and `TE` to `agentic`, and `LLM`, `OI` and `MI` to `llm` (`finding.yaml` rule 1; `orchestrator.md:373-374`).
    - `sarif_common.PREFIX_TO_RULE`'s short forms are never emitted, and the map gains the `TE` entry it lacks.
    - `level` keeps ADR-013 D3's per-file mapping. It isn't identity.
  - **`primaryLocationLineHash`.** `sha256("tachi-plh/1|" + tool + "|" + id)` over UTF-8, its first 16 hex digits, then `:1`. `tool` is the file's driver name. `id` is the canonical ID `{PREFIX}-{N}`, with no leading zeros, allow-listed first (NFR-10).
    - **Stable.** Carry-forward preserves the ID. A regroup, a new primary, a re-score, an UPDATED finding's new component or an upgrade leaves it alone. No model prose goes in (S-6).
    - **Unique.** If two present results share a hash, the emitter fails the render and names both IDs (F-012). The `tool` term keeps the files apart even if a server ignored the tool.
    - **Form.** `<16 hex>:1` is what the upload action writes for a line hash that occurs once; GitHub's example is `39fa2ee980eb94b0:1`. `/1` versions the recipe.
    - **Always tachi's.** It's on every result. It is never copied from upstream, and never left to the action, whose backfill hashes line 1 of the architecture file.
  - **`artifactLocation.uri`.** The user's architecture file: repo-relative, one canonical spelling, identical on every result in a run chain. One shared resolver sets it (FR-E.18).
    1. **Candidates, in order:**
       - the explicit path: the `--architecture-path` flag on the scorer and controls commands, or the command's own path for the body-line writer and PR 2's generator. Each reaches its script as `--architecture PATH`, a candidate that the resolver checks in code; no script takes a finished URI;
       - the body line;
       - `docs/security/architecture.md`.
    2. **Checks:**
       - non-empty, at most 4,096 bytes, and no control byte, backslash or backtick;
       - `.` and empty components dropped, `..` refused;
       - an absolute path counts only if an ancestor *is* the working directory by `os.path.samefile` (KB 24), and is then made relative;
       - every component exists, none is a symlink (an `lstat` walk), and the last is a regular file;
       - controls evidence `file` values become SARIF URIs, so they pass the same checks relative to the target directory, and must be relative: no scheme, leading `/`, backslash or drive letter. An entry that fails a filesystem check at render time is flagged and left out of `relatedLocations`, never refused (D2, ruled at W3).
    3. **Spelling.**
       - The path is rebuilt from the working directory down. Each component takes the name of the parent-directory entry with the same `(st_dev, st_ino)`. On a tie, the typed name wins, then the lowest code point.
       - So a case variant gives the same URI.
       - It is percent-encoded per RFC 3986, except for unreserved characters and `/`.
       - **The `https%3A//` edge (accepted at the P1 checkpoint, 2026-11-24).** An encoded first-segment colon followed by an empty segment decodes to a scheme form, yet passes D8's URI guard, which leads the decoded path with `./` when its first segment holds a colon. The emitter can't write one: it joins the spelled components after the checks above drop every empty one, so no written URI holds an empty segment. Refusing an empty segment in `self_check`'s guard is an optional T080 hardening.
    4. **NFR-10's name check (body line only).** `{run}` is the directory of the `threats.md` that was read, and `{basename}` is the candidate's last component.
       - The snapshot `{run}/{basename}` must be a regular file that isn't a symlink.
       - Its basename must not be one of D4's canonical names (`threats.md`, `threats.sarif`, `threat-report.md`, `attack-chains.md`, `risk-scores.{md,sarif}` and `compensating-controls.{md,sarif}`), and by `samefile` the snapshot must not be the candidate itself. So a line can't name a tachi output or a per-run snapshot, and the default snapshot name, `architecture.md`, passes.
       - **With no snapshot,** the line fails closed: it is untrusted content with no anchor.
    5. **Fallback.**
       - An absent or failed candidate passes to the next, with a warning that names it, the failed check and the flag. The stage record lists the warning.
       - The constant is emitted in its canonical spelling if it validates, otherwise literally.
       - Nothing here stops a run.
       - **The explicit candidate across the plan (ruled at W2, 2026-11-23).** On the scorer and controls commands the flag reaches `tachi-stage.py plan`, and the renderer sets the URI. So the planner checks the candidate once, with the resolver's own first step (`sarif_common.resolve_explicit`, `contracts/module-signatures.md`):
         - a candidate it accepts goes to the agents as `refs.architecture`, and the renderer resolves from that path;
         - a candidate it refuses, whatever check fails, syntactic ones included, is left out of `refs` and printed on stderr. It is recorded as the plan's `architecture_warning`, with the resolver's own code and text, `architecture-path:explicit:<check>`. `plan` still exits 0;
         - the renderer's stage record lists that warning first, then its resolver's, so the record holds the whole chain in this order. `fail`'s record lists it too;
         - the value as typed is never stored, except as the escaped short form in that warning's text, and no agent sees it.
         - **With no flag (ruled at W3, 2026-11-23, from T038 and T036).** `refs` holds no `architecture` on either command, and the planner never fills it, from the chain or from a snapshot. Both agents then read the run's snapshot, an `architecture.md` in the same directory as the `threats` file, as data for their judgment. That is the scorer's rule (`risk-scorer.md`, Reachability), now the control analyzer's too, so the controls command's default flow keeps v4.48.4's architecture-aware component mapping, which T038 dropped with the snapshot flag. The renderer resolves the body line and then the default, so the URI never names a snapshot (Known limitations). Resolving the chain at plan time was ruled out at the P0 checkpoint, because it changes the agents' fallback, and doing it for one stage would split the two commands' rules.
    6. **The body line,** ``**Architecture source**: `<canonical path>` ``.
       - It appears once, between the frontmatter and the first `## ` heading, outside code fences, and needs no schema bump.
       - A shipped upsert in `/tachi.threat-model` (`tachi-stage.py architecture-source`, at Step 2.7) writes it from the command's own path, through the same resolver. If that fails, the upsert removes any existing line, so a line the orchestrator wrote can't survive.
       - Zero matches, or several, read as absent.
       - The controls command reaches `threats.md` through `risk-scores.md`'s validated `source_file`.
  - **`region`.** The constant `{"startLine": 1}` (ADR-013 D6), never a line derived from content.
  - **`partialFingerprints`.** Exactly the hash and `findingId/v1`, the ID as Section 7 writes it. SARIF counts every partial fingerprint toward identity (3.27.17). So `correlationGroup`, and `threats.sarif`'s `baselineRunId`, both of which change on a regroup or re-assessment, move to `properties` (D8).
  - **Decoupled from Phase 3 (S-7).**
    - Phase 3's secondary key keeps today's formula and inputs (`baseline-correlation.md:78-106`), computed from `threats.md`, and is renamed there "location key".
    - It is never written to SARIF, and no stage reads a baseline SARIF's hashes.
    - The ambiguity at `:79` (is the first term the rule ID or the finding ID?) stays as it is, because resolving it could change matches (FR-E.13). It is a follow-up.
  - **`:339` against `:612`.** Both go. GitHub reads no key but the hash, so `findingId/v1` can't separate findings that share a rule and component. The shared reference states that no two present results in a file share a hash, and that `findingId/v1` is a cross-reference.
  - **Migration: one re-key event per file.**
    - **Scorer and controls, at PR 1: no compatible option exists.**
      - On the canonical path these results carry no hash (`risk-scorer.md:492`; `control-analyzer.md:384`) and point at the per-run snapshot (`tachi.risk-score.md:70-72`), so their key changes on every run.
      - With the snapshot checked in, the action's line-1 hash also collapses each rule into one alert.
      - No stable key exists to keep (D-5).
    - **`threats.sarif`, at PR 2, with its upload line (S-15).** No compatible option exists here either (see Alternatives).
    - **Sequencing.**
      - In PR 1 the orchestrator keeps authoring `threats.sarif` under an unchanged `sarif-specification.md`. A model can't compute the recipe, and identity text it read in PR 1 would force a second re-key.
      - That file's identity and membership sections change in PR 2, with the generator. PR 1's ledger (FR-E.17) records them as deferred to PR 2, because the change isn't inert (S-5).
- **Why.**
  - Among fingerprints, GitHub reads only the hash and uses only `locations[0]`, and it closes an alert when the alert's path changes (research-374-web §1). All four parts must therefore hold while a finding is present (principles 1 and 2).
  - The action's backfill keys on a line's text and collides (codeql-action `fingerprints.ts`; S-6).
  - SARIF 3.27.16–17 and Appendix B ask for one fingerprint for logically identical results, with no line numbers. Carry-forward keeps only the ID constant (ADR-018).
- **Alternatives considered.**
  - **A compatible option for `threats.sarif`: one finding per old `(rule, component)` hash keeps that hash.** Rejected, for four reasons:
    - **The old hash includes the component,** so the finding holding it would re-key on a rename. That breaks the spec's rule for UPDATED findings.
    - **No pick of the holder is safe.** A pure-function pick, such as the lowest S-2 ID, moves when a finding that sorts lower joins (a new `AG-` beside an `AGP-`). The alert's history and dismissal would then move silently to another finding, and a misplaced dismissal hides a live finding, which is worse than a clean re-key. A pick that sticks needs the previous run's SARIF, which is SV-3 state.
    - **The alert has no heir.** The old alert stood for several collapsed findings, so none of them is its heir.
    - **The old URI is unknown.** It is whatever the agent wrote, often a snapshot, and reproducing it needs the baseline SARIF. Where it differs from the new URI, the alert closes anyway.
  - **Also rejected:**
    - the rule, component or threat text beside the ID (the key changes on renames and prose edits);
    - the action's backfill (S-6);
    - no `region` (how GitHub displays it is undocumented);
    - the snapshot or `threats.md` as the URI (either moves on every run);
    - an unanchored body line (fails open).
- **Consequences.**
  - **PR 1:**
    - the shared reference, with its `threats.sarif` section dormant until PR 2;
    - the shared emitter in `scripts/sarif_common.py`, installed in PR 1: its rule map, hash and resolver;
    - the body-line writer, under P-2's anchors, and its reader;
    - `--architecture-path` on both commands;
    - `risk-scorer.md` §10a and §10e, including the case fix at `:462`;
    - `control-analyzer.md` Phase 6c;
    - `sarif-generation.md` (FR-K8.3). Its "SARIF Supersession" claim is false under R-33;
    - both renderer-owned templates;
    - the `reused-id` flag in both renderers (ruling B);
    - notes in ADR-013 and ADR-018.
  - **PR 2:**
    - the generator;
    - `sarif-specification.md:329-413` and `:593-624`;
    - the rename in `baseline-correlation.md`, and its numbering rule at `:142-146`, which now numbers above the mark;
    - `tachi-stage.py id-mark` and the reissue check (ruling B);
    - the `threats.sarif` template.

    `generate-threats-sarif.py`'s `md5` hash and its `artifact_uri_for` don't survive. Their FR-014 tests follow D1's ruling on the regeneration tier.
  - **Tests (FR-E.2's model), per file:**
    - the regroup pair keeps every carried key;
    - an unchanged re-run keeps its keys and bytes;
    - no shared key among present results;
    - a case variant gives the same URI (a fake-filesystem case everywhere, plus a real case-insensitive volume in D16's macOS job);
    - a body line naming an `architecture.md` outside `docs/security/` resolves to that path;
    - the three (tool, category) pairs differ;
    - no `automationDetails`;
    - the hash's form and its recomputation;
    - no copied upstream hash;
    - each carrier failure warns.
  - **Risks:**
    - GitHub's server key is undocumented. D-7's optional scratch-repository check covers it;
    - an action version that hashes line 1 anyway logs one expected mismatch warning per result;
    - a repository with several architecture files needs one category per system. That predates this ADR, and the guide notes it.
  - **ID reuse: ruled by the PM at the plan review (2026-11-22), ruling B.**
    - **The risk.** Phase 3 numbers NEW findings after the baseline's live IDs only (`baseline-correlation.md:142-146`). So under D7, a NEW finding given a recently resolved ID inherits that finding's alert, dismissal included. Today's `(rule, component)` key is worse, but for the scorer and controls files the exposure is new.
    - **The ruling, verbatim** (spec FR-E.19):

      > - **PR 2.** Phase 3 numbers each prefix above a per-prefix high-water mark, kept as a `threats.md` body line under P-2's anchors, with no schema bump. Shipped code, not the model, writes the mark: the larger of the baseline's mark and this run's highest ID. The first PR 2 run seeds it from the baseline's live IDs and Section 4c. ADR-050 records the limit: an ID resolved before the baseline run, which the baseline no longer lists, can still be reissued once.
      > - **A shipped check.** Phase 3 stays in the model, so the rule can't rest on instruction text alone. `check-threat-model.py` reports any NEW finding whose ID the baseline used or that sits at or below the mark. It warns (exit 5) and counts the event. It doesn't end the run, so D-3 keeps three paths.
      > - **PR 1.** The scorer's flag is as recommended. The controls renderer carries the flag for the same finding, because both files' alerts can inherit a dismissal.
      > - **Release notes.** PR 1's item 1 states the exposure until PR 2 and names the flag. PR 2's item 1 says that IDs are no longer reissued, so numbering can skip.

    - **The mechanism.**
      - **The flag (PR 1).** `render-risk-scores.py` flags `reused-id:finding_id:baseline` on a NEW finding whose canonical ID is in any row of the baseline `risk-scores.md`, and scores it fresh, never from that row. `render-compensating-controls.py` carries the flag from its input `risk-scores.md` into §7 and the result's `integrity-flags` property (`contracts/sarif-result.md`).
      - **The mark (PR 2).** One body line, ``**ID high-water mark**: `S-14, T-22, …` ``, with one `PREFIX-N` for each prefix in use, in S-2 order. It sits between the frontmatter and the first `## ` heading, outside code fences, and zero matches or several read as absent. At Step 2.7, `tachi-stage.py id-mark` upserts it (D4): per prefix, the larger of this run's highest ID and the baseline's mark, or, where the baseline has none, its highest live or Section 4c ID.
      - **The check (PR 2).** `check-threat-model.py` reads the baseline's mark, not this run's. It flags each NEW finding whose ID the baseline used, or that sits at or below that mark, with the same `reused-id` code, writes the count to its hand-off file and exits 5 (D12).
      - **Tests.** S-4's variants hold one case for each PR.
    - **The limit** is listed under Known limitations.
- **Supersedes or amends.**
  - ADR-013: D4 is superseded, D6 is amended (the URI and the fixed region), and D1 changes per this ADR's D1.
  - ADR-018: a dated note that the secondary key is local to correlation.
  - Also superseded: `risk-scorer.md` §10e, `control-analyzer.md:384`, and `sarif-generation.md`'s fingerprint and supersession sections.

### D8: SARIF membership and the N/N rule [Track: R for the scorer and controls files; O for `threats.sarif`]

- **Decision.**
  - **One top-level result per open finding, in every file.** Peers are results.
    - **The member set.** For `threats.sarif` and `risk-scores.sarif`, it is the reference set's open findings: Section 7, statuses NEW, UPDATED and UNCHANGED, read through D-4's wrapper, drift forms included. For `compensating-controls.sarif`, it is the open rows of the input `risk-scores.md`, which FR-K6.1 makes the same set.
    - **RESOLVED findings** (Section 4c, or a legacy result with `baselineState: absent`) appear nowhere: not as results, not in `relatedLocations`, and not as property values (R-30). Text that a renderer copies, a quoted snippet for example, may still mention one, because a mention isn't a reference (the self-check, below; ruled at W3).
  - **The counting rule.** The shared reference states it, correcting `sarif-specification.md:585`.
    - A file's findings are `runs[0].results[]`. N = the number of results = the number of distinct `findingId/v1` values = the size of the member set.
    - Nothing else counts. No `relatedLocations` entry names a finding in any file. The controls file's entries are code evidence only, each with a `physicalLocation` in the scanned code.
  - **Correlation** is recorded on each member's own result, in `properties`:
    - `correlation-group`: the `CG-N` ID;
    - `correlation-role`: `primary` or `peer`. This is the peer marker;
    - `correlation-primary`: the primary's ID.

    An uncorrelated result carries none of them.
  - **Group membership** comes from `threats.md` Section 4a, through one new shared parser, `tachi_parsers.parse_correlation_groups` (lane P). The generator, both renderers and the scorer's inheritance (D9) all use it.
    - **Order.** Groups keep Section 4a's order, and members keep their listed order, filtered to the file's member set.
    - **The primary** is the first remaining member. A group left with fewer than two members emits nothing. An ID listed in two groups stays in the first.
      - **Reported, never silent (ruled at W4, 2026-11-24, from PM W4 ruling R-F).** The rule stands, and each run now says what it did. `parse_correlation_groups` also returns `repeated`: one entry per ID that two or more of Section 4a's groups list, naming the group that claims it, the later groups that list it, and those of them that would have kept two or more of the run's findings but for earlier claims, so they emit nothing (`contracts/module-signatures.md`). Each renderer writes one Input Issues line per entry (scorer §6, controls §7), which `counts.parse_errors` counts, and warns `correlation-member-repeated` once, with the count, so the run exits 5. No flag or count key is added.
        - An ID that isn't one of the run's open findings is reported too, because Section 4a lists it twice. Its line says that no group holds it, and it names no group as falling away, because such an ID never counts toward a group's two.
        - The groups are what these rules always gave. The planner, which routes by the same groups, reports nothing.
        - Under the SARIF fallback, which reads no Section 4a, nothing is reported (Known limitations).
    - **Malformed rows.** A row whose group ID fails `tachi_parts`' group pattern (`CG-[0-9]{1,6}`), or whose members fail its finding pattern, is skipped and listed in the parse-error section (FR-K6.1). A missing or empty Section 4a means no groups.
    - **The controls renderer** reads the `threats.md` that its input's validated `source_file` names, which it already reads for the body line (D7). If that file can't be read, the file gets no correlation properties, the stage record says why, and no key changes.
  - **The fallback input.** This is `threats.sarif` for the scorer, or `risk-scores.sarif` for controls, when the markdown input is absent.
    - **The member set** is the SARIF's results, by `findingId/v1`, plus any legacy peer references in `relatedLocations`. A legacy reference is an allow-listed ID at the start of `message.text`, followed by `: ` (`sarif-specification.md:209`). Each one is grouped under its result.
    - **Dropped:** results whose `baselineState` or `baseline-state` property is `absent`. Correlation properties supply groups where present.
    - **An empty extraction** stops the run before dispatch (KB 22; S-12(c)'s path).
    - **The legacy member form (W1, 2026-11-22, T023).** A result with no `findingId/v1` takes its member ID from `properties.id`, the form tachi's older SARIF writes. It must pass the finding allow-list. Any other form still stops the run, with the regenerate remedy (`contracts/module-signatures.md`).
    - **A member's details, and unnamed groups (ruled at the P0 checkpoint, 2026-11-23, P0-3).**
      - **Details.** A fallback member's details come from its own result, whichever ID form it uses: the component from its logical location's `name`, else `properties.component`; the threat from `message.text`; the mitigation from `message.markdown`; the risk level from `properties.risk_level`, else `properties.severity`, else `security-severity`; the layer from `maestro-layer`; and the kind from the logical location's `kind`. The planner's fallback units and both renderers take them from one reader, `parse_sarif_member_set`'s `with_details` (`contracts/module-signatures.md`), so a legacy-form member keeps its identity text and the planner's agent set equals the renderer's.
        - **Ruled at W3 (2026-11-23, from FX0-3 and R3a).**
          - **The logical location** is `locations[0].logicalLocations[0]`, else `locations[0].logicalLocation`, the form that tachi's older scorer and controls SARIF write. Two shipped `risk-scores.sarif` files carry only that form.
          - **`properties.severity`** is where `generate-threats-sarif.py` writes Section 7's risk level, so the modern `threats.sarif` gains its level. A word is kept as written, and a score is banded with four bands, so a score under 1.0 is `Low`.
          - **A kind** is read back through the closed spellings `external-entity`, `process`, `data` and `data-store`. So a data store is written `data`, as the markdown path writes it, and any other value is `process`. No key holds the kind (D7), so nothing re-keys.
          - **The controls renderer** reads itself only what the details lack: the zone, from the same logical location's `fullyQualifiedName`, and `reused-id`, from `score-flags`.
      - **Unnamed groups.** A group that the SARIF gives no group ID still routes its peers (copy and divergence, D9). It carries no `correlation-*` properties and no ruling-C sentence, because both name a group ID, and no ID is invented: only named groups reach the emitter's role assignment. The stage record warns `correlation-group-unnamed`, with the count.
    - **Hashes** are recomputed (D7), never read.
  - **SV-3's trigger doesn't fire.**
    - Each key is a function of the file's constants, the finding's own ID, and the chain's architecture path.
    - IDs stay stable through the carry-forward that the threat-model stage already performs from the baseline `threats.md`. No stage reads a baseline SARIF's membership or hashes.
    - So N12 is implemented here, US-6a, US-6b and SC-6 stay claimed, and #397 ticks N12 at PR 2.
  - **Alert count (principle 4).** Each file holds one alert per open finding, never more than the deduplicated count. At Run B's scale that is about 210 per file, against GitHub's limit of 25,000.
    - `threats.sarif` rises from at most one alert per `(rule, component)`.
    - The scorer's file rises from primaries plus uncorrelated findings (`risk-scorer.md:534`).
    - The controls file keeps its count and drops its double listing.
    - When all three files are uploaded (FR-E.11), each finding shows once per tool.
- **Why.**
  - **Principle 1 by construction.** A regroup or a new primary changes properties, never membership or a key. That fixes N12.
  - **The asymmetry.** The controls file already emits peers as results (PRD D-5). "Primaries only" would close a controls peer alert at every regroup, and "stable primaries" needs SV-3 state.
  - **The spec's own wording.** FR-K7.1's "never as both" and D-5's "exactly once" hold literally, so a consumer counts with one length.
  - **One source.** Groups originate in Section 4a, and no shared parser reads it yet (research item 13).
- **Alternatives considered.**
  - **Primaries only.** Every regroup drops a result, which is N12. That breaks principle 1.
  - **Stable primaries.** They need the baseline SARIF's membership, so SV-3 would fire, and N12, US-6 and SC-6 would leave the release. Principle 4 ranks below 1 to 3.
  - **One result per group.** Group IDs are reassigned on every run.
  - **Peers as results and as marked `relatedLocations` references** (PRD §6's wording). Every peer would be listed twice, against FR-K7.1. Ruling C, below, accepts the placement.
  - **A group map in the scorer's output.** It needs a new field, plus a Section 4a fallback for pre-fix files: two paths for one fact.
- **Consequences.**
  - **Files:**
    - the shared reference's membership section;
    - the emitter's membership functions and self-check;
    - the Section 4a parser and the fallback reader;
    - `risk-scorer.md` §10h, plus D-6(a)'s seven count sentences, reworded once to "one result per open finding" (FR-N15.1(a));
    - `control-analyzer.md:383`;
    - the templates;
    - `sarif-generation.md`'s correlated mapping (PR 1);
    - `sarif-specification.md:197-280`, `:570` and `:585` (PR 2).
  - **The self-check runs before any write.** It and its tests assert that:
    - the result count equals the number of distinct IDs, which equals the member set;
    - no RESOLVED ID appears in a string that a renderer composes or takes as a closed value. That is `findingId/v1` and every property, except copied text: `message.text` and `message.markdown` (the reference set's threat and mitigation; ruling C's sentence keeps its own exact check, below), the scorer's `risk-owner`, and the controls file's `control-evidence`, `recommendation` and `relatedLocations` messages. An ID in copied text is a mention, not a reference. This was ruled at W3 (2026-11-23, from T053). It is P0-10's class, and in the controls file a repository that annotates its code with finding IDs would otherwise make the render exit 4 on every run. It also settles P0-10;
    - no `relatedLocations` entry names a finding;
    - every `correlation-primary` and every group member is a result, with one primary per group;
    - every correlated result's message ends with ruling C's sentence, and an uncorrelated one has none;
    - the regroup pair keeps every key;
    - **every URI passes D7's relative-path checks (recorded at W4, 2026-11-24, from T064's SA-11, landed by T146's FX-4).** Each result's `artifactLocation.uri` and each `relatedLocations` URI must pass `tachi_parts.path_problem` as written and as percent-decoded once, strictly as UTF-8. So a scheme, a leading `/`, a drive letter, a backslash or a `..`, written or encoded, fails the render. A colon in a clean first segment, which RFC 3986 section 4.2 makes the emitter encode (a directory named `a:b`), is led by `./` before the decoded check. The primary URI's problem is named once per run, and an evidence URI's names its finding (`contracts/module-signatures.md`).

    Further tests cover Section 4a (missing, empty, malformed, a member in two groups, an absent primary) and the fallback (the new form, the legacy form, and an empty extraction, which is an error).
  - **Release-note facts, §8 item 1. PR 1 (scorer and controls):**
    - the first upload after upgrading closes every `tachi-risk-scorer` and `tachi-control-analyzer` alert once and opens one per open finding. Dismissals are re-applied once. These alerts already churned on every run;
    - afterwards, nothing re-keys them: not a regroup, a new primary, a re-score, a new output directory or an upgrade;
    - one alert per open finding per file;
    - the tool names are unchanged. The snippets use `risk-score` and `compensating-controls`. An adopter's own existing category should be kept, because changing it re-keys, and a configuration that is no longer uploaded stays until deleted;
    - identity holds across baseline-aware runs, so successive runs go under one output directory. A stateless re-run re-keys (R-29), and so does moving or renaming the architecture file, once;
    - an architecture file that isn't at `docs/security/architecture.md` needs `/tachi.threat-model` re-run first, or `--architecture-path`;
    - peers are results, correlation is in the `correlation-*` properties, `partialFingerprints` holds only the hash and `findingId/v1`, and `relatedLocations` name no findings;
    - `threats.sarif` alerts churn until PR 2;
    - until PR 2, a NEW finding can be given a resolved finding's ID and inherit its alert, and the `reused-id` flag marks it (ruling B);
    - each correlated result's message names its group, and its primary or its peers (ruling C);
    - unless a scratch-repository check ran, the alert behavior is modeled from GitHub's documentation.
  - **PR 2 (`threats.sarif`):** the same facts for `Tachi`, plus:
    - the upload line reads the run's timestamped directory with `category: threat-model`;
    - an earlier upload without a category stays as a stale configuration to delete once;
    - distinct findings on one component and category get separate alerts;
    - a regroup drops none;
    - IDs are no longer reissued, so numbering can skip (ruling B).
  - **Risk.** Consumers that read peers from `relatedLocations`, or `correlationGroup` from `partialFingerprints`, must move to `properties`. No shipped script reads SARIF, so the exposure is external.
  - **Field placement: ruled by the PM at the plan review (2026-11-22), ruling C, placement accepted.**
    - Peers leave `relatedLocations`, and `correlationGroup` and `baselineRunId` leave `partialFingerprints`. FR-K7.1's "never as both" refines PRD §6's line "a peer marker sits in relatedLocations", which assumed peers listed there, so no PRD revision is needed.
    - **The ruling restores the link outside identity, verbatim** (spec FR-E.20):

      > Each correlated result's `message.text` ends with one sentence that names its group and either its primary (on a peer) or its peers (on a primary, up to a cap the shared reference sets, then a count). The message isn't identity (D7), so a regroup changes the text and never a key.

    - **The mechanism.** The shared emitter appends the sentence to the file's own message text, for example `Correlated in CG-3; primary S-1.` on a peer and `Correlated in CG-3; peers T-2, I-4 and 3 more.` on a primary. The shared reference sets the cap at 10 peers. The sentence names only the file's members, so no RESOLVED ID appears (R-30).
- **Supersedes or amends.**
  - ADR-013 D5 is superseded.
  - Also superseded: `sarif-specification.md:217` and `:570`, `risk-scorer.md` §10h, and `control-analyzer.md:383`.

### D9: Score-inheritance mechanics [Track: R]

- **Decision.**
  - **Baseline resolution (R-6).**
    - The command's `--baseline <run-dir>` flag comes first; a file path counts as its directory.
    - Otherwise `threats.md`'s `baseline.source` (`tachi_parsers.py:567`) applies. It must name a regular file called `threats.md`, not a symlink, under the working directory by resolved identity (NFR-10, KB 24). The controls command reaches it through `risk-scores.md`'s `source_file`, under the same checks. Baseline files need their canonical names.
    - Free text (#379), an unresolvable path, a failed check or a missing file means no baseline: the stage scores fresh and records why.
    - **Unreadable (S-12(d)).** A present file that fails NFR-10's checks, isn't UTF-8 or yields no row in any accepted form counts as missing, and §6 and the command summary warn that its owners, SLAs and dispositions weren't carried. Single unreadable rows go to Input Issues and are scored fresh.
  - **Tolerant reader (R-26, S-12(a)).** It accepts `## N.` and `## Section N:` headings, header aliases (`Exploit`, `Exploit.`, `Exploitability` and their kin, `Disp`), §3 subsections headed `### ID — …` or `### ID: …`, vectors written as ``**CVSS Vector**: `…` `` or after `**Vector**:`, the §4 table, and the renderer's `### Scoring Inputs`. An ID cell that isn't one allow-listed ID yields no row. A legacy vector comes from the markdown, or else from the baseline SARIF's `cvss-vector` keyed by `findingId/v1`. When the two differ, the markdown's is used, flagged `input:cvss_vector:sources-disagree`.
  - **Carried findings.** These are UNCHANGED findings, and drift-form findings the baseline can supply (S-12(b)).
    1. **Inputs are inherited verbatim.** From a renderer-form file: the assessed vector, `score_bounds`, the sub-scores, zone, trust level, barrier counts, the tags used and the scored-on date. From a legacy file: the vector, and C, E, S and R as stored. From either: owner, SLA, disposition and review date.
       - **§3's prose** (the per-dimension, per-metric, per-sub-score and reachability rationale) keeps its slots (Architect re-review RR1). A renderer-form file holds each narrative field's validated, slotted text in §6's Scoring Inputs, escaped on write. The renderer decodes it, re-validates it as narrative and re-resolves its slots against this run's values, with D3's per-field fallback, so a value that moves moves in the prose too. A legacy file's prose has no slots: it comes through the tolerant reader as evidence-class text, escaped, never validated as narrative, and never read for a number. Where the baseline has none, the cell reads `—`.
       - **A legacy-carried row (ruled at the P0 checkpoint, 2026-11-23, P0-2).** When a run carries a legacy row, the 1.1 file it writes records the row's vector, the tags used and the scored-on date in §6's Scoring Inputs, but no sub-scores, so the next run reads it as a legacy row again. That run reads the tags used and the scored-on date from §6 whenever §6 records them, whatever the row's form. So those tags are "the baseline's recorded tags" of ruling A and D10's step 3a: such a row isn't "a legacy row [that] records no tags". The scored-on date is the original scoring date of the review-date rungs. Its §3 prose, all four dimension paragraphs, is read back as legacy prose.
    2. **Recompute** the CVSS chain (D10), then E, S and R (renderer form) or R's range check (legacy, D10), then the composite and the band.
    3. **Compare** each value with its stored value. A rounding-only difference (the stored value is the exact value's other one-decimal neighbour) is **normalized** and counted when the band holds, and flagged `corrected:severity_band:rounding` when it moves the band. A change that the asset tags alone explain, including a value that follows a band the tags moved, such as the SLA and the review date, is flagged `retagged:<field>:asset-tags`, never `corrected`, `follows-band` included (ruling A, below; PM confirmation, ruling 1). Anything else is `corrected:<field>:<cause>`, with causes `vector`, `arithmetic`, `band-mapping` and `follows-band`.
    4. **Missing vector (R-7).** `cvss_vector` is null, the score is kept, and the finding is flagged `unverifiable`. It changes when the finding is next UPDATED.
    - **What the baseline can supply (S-12(b); ruled at W2, 2026-11-23).** Some forms lack values: a Section 7 drift form, and D8's SARIF fallback, which lacks `delta_status` for every member. For those, the baseline supplies a value only from a usable open row for the same canonical ID, an entry of R-26's `rows`, and only a value that row records. It never supplies one from §2a's RESOLVED rows, an unreadable row or another finding's row. Per value:
      - **`delta_status`.** A usable row supplies it. The finding is routed as UNCHANGED and carried by steps 1–4, its owner, overrides and review date included. Without a usable row the finding is NEW. The agent scores it fresh, and ruling B's test applies to it as to any NEW finding. The status is derived once, in `route_scorer_units`, so the planner and the renderer route by the same rule.
      - **`component`, `threat` and `risk_level`.** These are supplied for a carried finding only. The component comes from the row's §3 heading, or else its §2 cell; the threat from its §3 `**Threat**:` line, or else its §2 cell; and the original risk level from its §3 line. A fresh finding (NEW, UPDATED or without a usable row) is never supplied, because an UPDATED finding may have changed. The renderer supplies the component before S-13's tag join, so a carried finding's tags follow its own component and a drift form raises no false `retagged` flag.
      - **The flag stays.** Each value the form lacks is flagged `input:<field>:not-in-form`, whether the baseline supplied it or not, and the stage record lists it (US-1a #8).
  - **Governance (R-5, R-31).**
    - **Overrides.** An Accept or Transfer disposition, or an SLA or disposition that differs from the stored band's default (`schemas/risk-scoring.yaml:180-183`), is carried verbatim and flagged `override:<field>:human`. The owner is always carried and never flagged. Other SLAs and dispositions follow the rendered band.
      - **"Verbatim" by value class (ruled at W2, 2026-11-23).** The owner is free text (`risk_owner`). It is read as the cell holds it: decoded once and stripped of edge whitespace, with its markdown emphasis kept. So `**Platform** team` carries byte for byte, and a cell is no owner only when it is a placeholder once its emphasis is set aside. The SLA and the disposition are closed-ish: one is a duration and the other an enum, and the override test compares each with the band's default. Their emphasis is formatting around the value, so they are read without it, and "verbatim" means the value as written, less emphasis and edge whitespace. §2a's RESOLVED values are read the same way.
    - **Review date.** It is kept when the band holds or the SLA is an override. A corrected band gives the original scoring date plus the new SLA, where that date is the stored scored-on date (whenever §6 records one, P0-2) or the stored review date minus the stored SLA. A tag-driven band change follows ruling A, below.
    - **Fallback**, when either value is missing or unparseable: the baseline file's frontmatter `date` (`corrected:review_date:baseline-date`). Without it, the stored review date is kept (`unchecked:review_date:scoring-date-unknown`). Without that too, the current date plus the SLA is used (`corrected:review_date:clock-restarted`). No step is silent.
    - **UPDATED findings** keep their owner and overrides. A band change restarts their clock (`risk-scorer.md:378-382`).
    - **Tag-driven band changes: ruled by the PM at the plan review (2026-11-22), ruling A, verbatim** (spec US-5 #13 and #14):

      > **Tag-driven band changes.** A band change that the asset tags alone explain isn't a correction. It is never flagged `corrected`, and D9 gives it a flag of its own. Then:
      > - **Up:** the review date becomes this run's scoring date plus the new SLA, unless the stored review date is earlier, in which case the stored date is kept. Tagging never makes a finding overdue on the day, and a higher band never gets more time.
      > - **Down:** the original scoring date is kept, as for a correction (R-5). Removing a tag never clears a deadline that was already missed under the lower band's SLA.
      > - An SLA override (R-31) still keeps its review date.
      > - "The tags alone" means that recomputing with the baseline's recorded tags gives the stored band. A legacy row records no tags, so there a band change that comes only from the elevation this run's tags apply follows this rule. That covers the first renderer run, where D9 ends the UNCHANGED exemption (`asset-modifiers.md:169-178`), so the upgrade itself can't make carried findings overdue.
      > - Any other band change follows R-5.

      - **The flag** is `retagged:severity_band:asset-tags`. The values the tags alone move on the way, such as `cvss_base` and `composite_score`, and the values that follow the band they moved, such as the SLA and the review date, are flagged `retagged` too. None is flagged `corrected`, `follows-band` included, so no tag change reads as a correction (PM confirmation, ruling 1). D10 applies the same test in the vector check.
      - **This run's scoring date** is the `--date` input (D5).
      - **Tests.** S-4's variants cover both directions and the legacy case.
  - **Peers (R-4, R-31).** Groups come from D8's source.
    - **NEW and UPDATED peers take their primary's assessment (ruled by the PM at W3, 2026-11-23, ruling 1, from P0-6).** That is the assessed vector, `score_bounds`, the sub-scores (a legacy-carried primary's stored E, S and R) and the reachability inputs. The renderer scores each peer with its own asset tags from S-13's source, so its `affected_assets` and §6's tags used are its own, and D2's F-302 sentence holds for peers too. A peer whose tags equal its primary's has its primary's values exactly. A peer whose own tags move its composite keeps that score, and is flagged `divergent:composite_score:primary=<ID>` from the run that scores it, so the next run carries it as UNCHANGED with the same values and the same flag. UPDATED peers keep their own owner. So R-31's "one score per group" now means "one assessment per group, and one score wherever the members share asset tags", which covers every shipped group.
      - **The mechanics (ruled at W3).** With equal tags, the peer copies its primary's values and no chain runs, whatever D10 step decided a legacy-carried primary's score. With different tags, its CVSS score is R-25's outcome t(a) under its own tags, on its primary's vector and assessed score a. Its composite and band follow, and its governance follows its own band: fresh when NEW, the UPDATED rule otherwise. For a primary scored fresh or carried from a renderer-form row, a is the chain's assessed value. For a legacy-carried primary, a is the candidate whose outcome D10's check rendered (steps 3, 3a, 4 and 6, and a missing stored score). Where there is no such a, the renderer doesn't guess: the peer keeps its primary's values and is flagged `unchecked:cvss_base:assessed-unrecorded`. That is a legacy primary decided at step 2 or 5, or passed by step 3's ceiling clause alone. A primary with no vector gives R-7's `unverifiable:cvss_base:no-vector` instead (`contracts/module-signatures.md`, `VectorCheck.assessed`).
    - An UNCHANGED peer keeps its own score, and is flagged `divergent:composite_score:primary=<ID>` when its composite differs from its primary's.
    - A regroup changes no carried value.
  - **RESOLVED (R-30).** Section 4c's findings move to a new `## 2a. Resolved Findings` table after §2. It has §2's columns plus `Status` (`RESOLVED`), Owner and Review Date. Values are taken verbatim from the baseline's open or §2a row: never recomputed or clocked, and flagged only `resolved`, in the row's Flags cell.
    - The marker is additive and readable. §2's readers stop at the first table (`parse_risk_scores_findings`, `tachi_parsers.py:1302`), and `parse_markdown_table` already reads §2a.
    - The Executive Summary counts them on a separate line, and no SARIF carries them.
  - **In `risk-scores.md`.** §2 and §2a gain a trailing `Flags` column (kinds in a fixed order, or `—`), and §3 an `**Integrity**:` line per flagged finding. A new `## 6. Score Integrity` holds:
    - `### Integrity Summary`: counts by kind and cause, the normalized count, and the baseline and tag sources;
    - `### Score Flags`: `ID | Flag | Field | Stored | Rendered | Cause`, in S-2 order;
    - `### Input Issues`, FR-K6.1's defined place;
    - `### Scoring Inputs`: every step-1 input per open finding, plus the tags used and each narrative field's validated, slotted text, escaped on write (RR1), so the next run reads them from one place, re-resolves the prose against its own values, and never takes a number from prose.
  - **SARIF properties** (identity is D7's): `score-source`; `score-flags`, a sorted array of `kind:field:cause` strings, always present; `score-corrections`, objects `{field, from, to, cause}`; and `cvss-vector` as JSON `null` when unverifiable.
  - **Flag kinds.** The spec's eight (`corrected`, `unverifiable`, `unchecked`, `divergent`, `override`, `resolved`, `retagged` and `reused-id`), plus `input`: a kept input with a problem (source disagreement, out-of-range reachability, a value missing from the input's form), a narrative field replaced by its fixed sentence (`input:<field>:narrative-fallback`, D3), or a prose field cut at its limit (`input:<field>:truncated`, D3, RR2).
    - **The two "missing" causes (ruled at W2, 2026-11-23).**
      - `input:<field>:not-in-form` is a value that Section 7's form has no place for, with `component`, `threat`, `delta_status` or `risk_level` as the field (S-12(b)).
      - `input:<field>:missing` is a value the baseline row's form has a place for but this row leaves empty or unreadable. Only `cvss_base` and `review_date` take it. The renderer computes the score from the chain (D10), and the review date by R-5's rules. A missing owner becomes `Unassigned`, and a missing SLA or disposition follows the rendered band, all with no flag, since no reader would mistake a default for a human value.
      - With D2's `corrected:trust_level:trust-label`, these strings are in the closed vocabulary (`contracts/module-signatures.md`).
- **Why.**
  - D-6(b)'s ranking (R-4), R-5, R-7, R-11, R-30 and R-31. Today's "zero drift" copies derived fields verbatim (`risk-scorer.md:71-76`), so one run's slip becomes permanent.
  - With a stored scored-on date, only legacy files ever need the fallback.
- **Alternatives considered.**
  - **RESOLVED rows in §2 with a Status value.** Every existing reader would count them as open.
  - **Flags in SARIF only.** The people acting on SLAs read the markdown.
- **Consequences.**
  - **Files.** `risk-scorer.md`'s baseline and governance sections become documentation of the renderer, and the template gains §2a, §6 and `Flags`.
  - **Offline tests.** S-4's variants, asserting SC-4's counts, ruling A's two directions and legacy case, and ruling B's PR 1 case; R-30's split parity; each fallback rung; free-text, missing and unreadable baselines; the round-trip through `tachi_parsers`; the PM's five peer conditions (W3 ruling 1).
  - **Risk.** A baseline form the reader doesn't know becomes Input Issues and fresh scoring, never a wrong inheritance. S-12(c)'s stop applies to Section 7 only.
- **Supersedes or amends.** ADR-018's "UNCHANGED: inherit all scores and control status" (line 44) is amended: inputs and control judgment are inherited, derived fields are recomputed, and each change is flagged (a dated note).

### D10: The exception rules [Track: R]

- **Decision.**
  - **A category for every prefix.** S, T, R, I, D and E map to their STRIDE categories. AG, AGP and TE map to `agentic`; LLM, OI and MI map to `llm`. One resolver in `tachi_scoring` serves the CVSS defaults and bounds, the controls' STRIDE-to-control mapping and the rule IDs. `tachi_parsers.STRIDE_PREFIXES` stays as it is: its "Other" roll-up is what the PDF renders (NFR-1).
  - **Fresh scoring.** The assessed score is base(v), clamped to the finding's own category's ±1.0 bound only for a NEW finding in a baseline-aware run (stored as `score_bounds`). When the tags force a bit, R-25 then gives `max(assessed, min(base(elevate(v)), 9.2))` (`asset-modifiers.md:13-22`).
    - **"Baseline-aware" (ruled at the P0 checkpoint, 2026-11-23, P0-9).** It means that a usable baseline `risk-scores.md` was read: R-6 resolved one and R-26's reader found it readable. Only then is a NEW finding bounded, S-12(b)'s derived-NEW findings included. A delta-mode `threats.md` whose baseline `risk-scores.md` is missing or unreadable bounds nothing, in line with S-12(d)'s "counts as missing, scores fresh". v4.48.4's scorer bounded the NEW findings of any baseline-aware threat-model run, whatever its own baseline's state, so T066 attributes a diff there to the oracle's fifth class (D3, PM W3 ruling 2b), and R1t pins it.
  - **The vector check (R-9) on a carried finding.** For a renderer-form row, the chain above is recomputed from the stored inputs and this run's tags. A difference is flagged `corrected:cvss_base:vector`, or `retagged:cvss_base:asset-tags` when recomputing with the baseline's recorded tags gives the stored value (ruling A).

    For a legacy row with score s and vector v, a candidate assessed score a is base(v) or its own-category bound clamp. t(a) is R-25's outcome under this run's tags: `max(a, min(base(elevate(v)), 9.2))` when a tag forces a bit, otherwise a. So the tags are tested before anything passes (PM plan review, finding 2). The first matching step decides:
    1. no vector: `unverifiable`;
    2. R-25's legacy case: a forcing tag, v already carries the forced bits (elevate(v) = v), and 9.2 < s ≤ base(v). Only an elevated score is stored, so the finding is `unchecked` (`assessed-unrecorded`) and s is kept;
    3. a documented outcome: pass. That is s = t(a) for either a, or a forcing tag with s = 9.2 and base(elevate(v)) above 9.2;
       - **Step 3a, the recorded tags (ruled at the P0 checkpoint, 2026-11-23, P0-2).** It runs only for a row that records the tags it was scored with (D9, step 1). Let t′(a) be R-25's outcome under those recorded tags. If s = t′(a) for either a, or the recorded tags give step 3's ceiling case (a recorded tag forces a bit, s = 9.2, and base(elevate(v)) under the recorded tags is above 9.2), then the tags alone moved the score. It becomes t(a) under this run's tags for that same a, flagged `retagged:cvss_base:asset-tags` (ruling A). The candidates are tried in step 3's order, base(v) and then its clamp, and the ceiling case takes base(v). Otherwise, as for a row that records no tags, the check goes on to step 4;
    4. a forcing tag and s = a < t(a) for either a: the stored score lacks the elevation. It becomes t(a), flagged `retagged:cvss_base:asset-tags` under ruling A's legacy case;
    5. an N17 dependency: `unchecked`, and s is kept. That is s equal to another category's bound clamp of base(v) (a possible cross-category peer, cause `bound-n17c`), or a forcing tag with 9.2 < s < base(elevate(v)) (cause `assessed-unrecorded`);
    6. otherwise: `corrected:cvss_base:vector`, to t(base(v)).
  - **The ±1.0 bound check stays unchecked (N17c, NG2).** No carried score is flagged or re-clamped for where it sits against a bound. Bounds enter a check only through the candidate a (steps 3 and 4) and step 5, and none of them reads group membership, so the vector check needs no peer exception (D-4).
  - **Reachability range (R-10).** A legacy R is checked against its trust level's range only when the component's §2 label normalizes unambiguously: a canonical match, or keywords from a single category (`trust-zones.md` §2c). Otherwise it is flagged `unchecked:reachability:compound-trust-label`. An unambiguous label out of range keeps the value, flagged `input:reachability:out-of-range` (SC-4).
- **Why.**
  - D-4 asks for a category for every prefix, and resolution covers only eight today (`cvss-vectors.md:100`, `risk-scorer.md:267`, `control-analyzer.md:149-151`).
  - The map follows the AI tables Phase 3 files these prefixes under (`orchestrator.md:373-374`, NG4) and `sarif_common.py:30-42`, which gains `TE` (D7), so a finding scores the same whether or not #356 folds its prefix.
  - R-9, R-10 and R-25; NG2 defers the cross-category bound.
- **Alternatives considered.**
  - **Accepting any category's bound as a clamp.** That passes wrong scores at 13 values.
  - **Re-clamping carried scores.** That is the N17c check NG2 defers.
  - **Widening `STRIDE_PREFIXES`.** Old inputs would render differently.
- **Consequences.**
  - **Files.** `cvss-vectors.md`'s prefix column and its category resolution text, `risk-scorer.md:267`, `control-analyzer.md:149-151` and `asset-modifiers.md:169-178`.
  - **Tests.** For each of the 12 prefixes: a wrong-vector score corrected, an own-bound clamp passed, and another category's bound value marked unchecked. The tagged cases in S-4's variants, including a stored score that lacks the elevation (retagged) and a stored elevated vector above 9.2 (unchecked). Zero documented exceptions flagged.
  - **Risk.** A slip that equals the finding's own bound passes as a clamp.
- **Supersedes or amends.** Nothing: no vector, default, ceiling or threshold moves (NG7).

### D11: Dispatch records, the ID map and the persisted Phase 1 tables [Track: O]

- **Decision.**
  - **Phase 3 stays a model compilation (D1).** The model compiles from the agent returns already in the orchestrator's context and never reads the records back (C-7). The records and the ID map are the audit copy.
  - **The record is a per-dispatch manifest (R-8).** D1 keeps the tables model-authored. That is SV-2b's carved state, so under FR-N4.2 the record shrinks to the agent, its scope, the count and the provisional IDs.
    - **The file.** One JSON file per dispatch, `{out}/.tachi-build/records/{dispatch_id}.json`, written once, when the return arrives.
    - **The envelope:** the roster `agent_type`, `origin`, `scope.components`, the brief's path, the prompt line verbatim, the end-marker flag, the status and the supersession links (`contracts/threat-model-records.md`).
    - **No digest in the record.** A model can't compute a hash, so the check derives the prompt's SHA-256 for the stage record, which #399 reads.
  - **`schemas/finding.yaml` is not bumped,** because the record holds no finding objects.
    - D1 records why: SV-2b's state applies. Verbatim findings would need no bump either, but they would add 60–80k tokens of orchestrator output (C-7).
  - **Truncation (FR-N4.7).** When a return is flagged (D6, S-9), the orchestrator first allocates the IDs of the per-component re-dispatches. Item O-α (D6) may move that allocation into code.
    - It then writes the truncated record once, as `superseded`, with its `reason` and `superseded_by`. Each replacement names it in `supersedes`.
    - The superseded record's findings leave the completeness set.
  - **The ID map.** `{out}/.tachi-build/idmap.json` is written once, at the end of Phase 3. It gives one disposition for each finding a non-superseded record received, in the order received:
    - `S-7`: kept, as final `S-7`;
    - `=S-2`: matched to carried `S-2` in Phase 3a, exactly;
    - `~S-2`: matched to carried `S-2` by similarity;
    - `>T-4`: merged into the surviving `T-4`.

    The map from each final finding back to its source is the inverse, and D12 computes it. This form stays near 2k tokens, inside S-1's 8k budget for a single write.
  - **#356 stays separate (NG4, R-13).** A kept ID that differs from the provisional ID is a recorded renumbering. The check allows each agent its own prefix, plus today's folds: `OI` and `MI` into `LLM`, and `TE` into `AG`. A test pins that table, which narrows when #356 lands.
  - **The Phase 1 tables.** After the self-checks and before any dispatch, the orchestrator writes two files under `.tachi-build/phase1/`, in place of the printed intermediates:
    - `inventory.json`: the components, data flows and trust zones;
    - `dispatch.json`: the categories for each component.
  - **The briefs (FR-N4.3).** With no rendering script (R-34), the orchestrator writes each brief itself, to `.tachi-build/briefs/{dispatch_id}.json`. A brief holds:
    - `targets`;
    - `inputs`: the snapshot, `inventory.json` and `dispatch.json`;
    - `baseline_focus`, which is null when the run is stateless;
    - its identity keys.
  - **The prompt** is exactly `Read and follow the brief at {brief_path}.`, with `{brief_path}` absolute, because Read takes absolute paths.
  - **Where the text lives.** In PR 1, the record and brief templates and the end marker's text sit in `.claude/skills/tachi-shared/references/dispatch-record-brief-shared.md`, which no PR 1 agent or command loads, and the marker text is provisional until S-9's spike (KB 25). PR 2 moves the marker into the shared finding-format reference, which every threat agent reads, so no protected detection file changes (S-9, KB 6).
  - **P-11 is adopted,** at the cost of one more file read. Each roster agent's planned components come from `dispatch.json`, and that agent's non-superseded records must cover them.
- **Why.**
  - R-8, FR-N4.2 and PRD §10 bind the manifest form while the tables stay in the model. Verbatim records pay off only if code compiles Phase 3 (RK-4, C-7).
  - Storing one direction of the map keeps a single model-written source, and makes "exactly one provenance entry" computable (C-8).
  - P-11 turns an agent that was never dispatched into a check over files that already exist.
- **Alternatives considered.**
  - *(a) Verbatim records:* R-8 rules them out.
  - *(b) An origin field in `finding.yaml`:* a schema bump and an edit to every agent contract.
  - *(c) Phase 3 re-reading the records:* that adds a third copy of the findings to the context.
  - *(d) A two-direction map:* about 12k tokens, over S-1's budget for a single write.
- **Consequences.**
  - **Files:**
    - `orchestrator.md`: Phases 1 to 3, and the protocol at `:276-282`;
    - `dispatch-rules.md`;
    - `finding-format-shared.md`, where "dispatch record" becomes "brief" (`:160`, `:212` and `:218`) and the end marker lands, both in PR 2. `test_contract_text_374.py` pins that PR 1 leaves the file with neither (D16);
    - `output-schemas.md`.
  - **Offline tests:** the loader rejects bad input in each file; a truncation followed by a stateless re-dispatch; the fold table pin.
  - **Live:** US-4 #3's prompt audit (SC-3).
  - **RK-4:** these files add about 11k tokens of orchestrator output, and D13 and D14 remove far more. TW-CTX records the peak.
- **Supersedes or amends.**
  - ADR-049 D7 gains a dated note: the orchestrator now writes to `.tachi-build/`.
  - The inline-payload protocol is replaced. No ADR states it.

### D12: The provenance and completeness check [Track: O]

- **Decision.**
  - **Where it runs.** `scripts/check-threat-model.py` runs in the main session, under `/tachi.threat-model`, at Step 2.8. It runs after D13's check and before report assembly. It also runs FR-E.10's Section 6 parity check, classifying applicability through ADR-047 D2's helper, and FR-E.19's reissue check (ruling B, D7). Each reports a mismatch with exit 5 and never ends the run, and both write their counts to the run-level plan's hand-off file (D4).
    - **Paths** come from the command: `--run-dir {output_dir}`, `--plan` (the run-level plan's ID), plus `--baseline {path}` or `--no-baseline`.
    - **Untrusted inputs (NFR-10):** the run's reference set (FR-E.16), the baseline's open set, the records, the briefs, the ID map and the Phase 1 tables.
  - **FR-N4.5: from each final finding back to its source.** Every finding in the reference set has exactly one provenance entry, of one of three classes:
    1. **A dispatch record.** Exactly one kept disposition names the finding, its status is NEW, and the record's agent is allowed its prefix.
    2. **A baseline carry-forward.** Its status is UNCHANGED or UPDATED, its ID is in the baseline's open set, and no disposition keeps it.
    3. **A named rule.** It is an `AGP-NN` finding from Phase 3.6, with status NEW, and no disposition claims it.

    A finding with no entry, or with several, fails. So does a run with no live record (a record that isn't superseded).
  - **FR-N4.6: from each source to its final finding.**
    - The map's keys are exactly the live records, and each array is as long as its record's `count`.
    - Every disposition target exists. A kept or merged target is in the reference set, and a matched target is a carried finding.
    - Supersession agrees in both directions.
    - P-11's coverage holds.

    ID changes and folds go to the stage record.
  - **The envelopes.**
    - Each record names a roster agent.
    - Its brief holds only the closed key set (US-4 #3) and matches the record.
    - Its `prompt` equals the fixed line.
  - **What it proves.** The orchestrator's record of itself is consistent and complete.
  - **What it doesn't prove.** That the agents ran: records that are fabricated but consistent still pass. That proof belongs to #399 (NG6). So the check catches mode 3 when records are missing, and mode 1 only when a record names an agent that isn't in the roster.
  - **Failure (D-3).**
    - **The error** names the stage (`threat-model provenance`), the IDs involved (the first 20, then a count) and the remedy: re-run `/tachi.threat-model`. When there are no records at all, the remedy also says to re-run `install.sh`.
    - **Then** assembly doesn't run, and D4's P-4 mechanism marks the outputs failed.
- **Why.**
  - FR-N4.5 and FR-N4.6 are never carved, and the spec fixes where the check runs, its classes and its limits.
  - Running before assembly means a failed run never yields a report that looks complete (D-3).
- **Alternatives considered.**
  - *Running inside the orchestrator:* that is the layer being audited.
  - *Warning instead of failing:* D-3 forbids it.
  - *Matching findings by content:* that is correlation (S-7), not provenance.
- **Consequences.**
  - **Files:** the script; a step in `tachi.threat-model.md` after Step 2.5, which leaves Step 2.6 free (P-2); §8.4 and §8.5.
  - **Tests, one per case:**
    - carried, renumbered, folded and pattern findings;
    - a truncation re-dispatched in a stateless run;
    - no records at all;
    - a planned agent with no record;
    - a finding with two entries;
    - an orphan finding;
    - an extra key in a brief;
    - a prompt that doesn't match;
    - a NEW finding whose ID the baseline used, or that sits at or below its mark (S-4's variants).
  - **Risk:** false failures from the model's bookkeeping. TW-L2 measures them.
- **Supersedes or amends.** Nothing. The check adds detection beside ADR-049 D4.

### D13: Phase 3.5: the chain script, the outcome record and its check [Track: O]

- **Decision.**
  - **Shipped code computes the chains (R-19 adopted).** `scripts/attack-chains.py` uses only the standard library and runs on Python 3.9 or later. Every mode takes `--run-dir {output_dir}`.
    - **`plan` and `render`:** the orchestrator runs them in `python3` fences (C6), as it runs the Phase 3.7 populator.
    - **`check`:** the main session runs it.
  - **The inputs.**
    - **The compiled `threats.md`.** From Section 7, through the reference-set wrapper, the script takes each finding's ID, component, Risk Level, MAESTRO Layer and Mitigation. A missing layer falls back to the inventory's.
    - **The persisted data-flow table:** `inventory.json`'s `data_flows`.

    Component names are compared after casefolding and collapsing whitespace.
  - **When it runs.** Phase 3.5 keeps its label but runs after the join (D4). Its output doesn't change, because chains use only STRIDE findings and Phase 3.6 reads no chains.
  - **The algorithm** is S-3's, with S-2's order wherever an ID decides an order.
    - **The finding set.** Findings with a STRIDE prefix, on layers L1 to L7.
    - **Links (S-3(b), unchanged).** F_a → F_b is a link when the two findings are on different layers, one component is reachable from the other through the flow graph's transitive closure (a direct flow counts as one hop), and (cat_a, L_a) → (cat_b, L_b) is in the transition table.
      - The table is embedded in the script, and a drift test compares it with `attack-chain-patterns-shared.md`.
      - Narrowing the closure is an R-21 change, so it goes to the PM.
    - **Assembly (S-3(c)).** Starts are taken by severity, then in S-2 order. Each start with an outgoing link that doesn't already start a chain starts one chain, which extends greedily to the first candidate, in that order, on a layer the chain doesn't have yet.
    - **Consolidation (S-3(d)).** First drop identical finding sets, keeping the higher-ranked chain. Then filter. Then fold each contiguous run into a longer chain that survives. This gives the counts C (candidates), N (consolidated) and S (surfaced).
    - **IDs.** `CHAIN-` plus the rank, padded to at least three digits (S-3(e)).
    - **Surfacing.** At most five chains surface (S-3(f)). Each one carries `converging`, the number of other consolidated chains that end at its terminal-impact finding.
    - **Chain-breaking.** The orchestrator's Step 4 rules apply. The recommendation is the target finding's Mitigation, verbatim.
  - **Titles and narratives** are written for the surfaced chains only.
    - `plan` writes `.tachi-build/chains/chains.json`, holding every computed field and both input digests, and prints the surfaced chains.
    - The orchestrator writes `chains/narratives.json`: a `{title, narrative}` for each surfaced chain ID.
    - `render` refuses stale digests, validates and neutralizes the narratives (NFR-10), writes `attack-chains.md` (`contracts/threat-model-records.md`) and records the outcome.
    - When validation fails, the orchestrator rewrites the narratives once. If they fail again, `render` builds a fixed title and narrative from the members, and counts the fallback.
  - **The outcome record (P-3)** is a body line, so it needs no schema bump.
    - **Where it lands.** Under an unnumbered `## Attack Chain Outcome` heading, directly before `## 5. Coverage Matrix`. Failing that it goes before `## Affected Assets`, and failing that at the end of the file.
    - **Who writes it.** The joiner never writes it. The script upserts it after the join, as the populator upserts its block, so the order in which the scripts run doesn't move it. Step 7 of D4's table runs `render` after the join, so the joined file always gets the record.
    - **Its three forms:**
      - when N ≥ 1, `chains written (N)`;
      - when N = 0, `0 chains passed filter (<reason>)`;
      - when an input is unusable, `skipped (<reason>)`.
    - **It never stops the run.** The orchestrator continues whatever the script returns (R-24).
  - **The check (FR-K4.1b) and R-24.**
    - **`chains written (N)` passes** only when the file parses, has S full chains and min(100, N − S) compact rows, states the remainder on its last line, and carries frontmatter equal to (N, S, C).
    - **`0 chains` and `skipped`** require the file to be absent and a reason to be stated.
    - **A missing record** becomes `skipped (no outcome recorded)`. A bad or duplicated record becomes one `skipped (<what disagreed>)`.
    - **When the record is skipped,** the check renames any `attack-chains.md` to `attack-chains.inconsistent.md`, so neither a reader nor a person takes it for complete output.
    - **Then** the check warns, writes the event to its hand-off file under `threat-model/<plan_id>/checks/`, which `close` or `fail` folds into the stage record, and exits 5 (D4).
  - **The readers** read the record first, and fall back to file presence only when no record exists.
    - **The parser.** A new `tachi_parsers.parse_chain_outcome` serves `detect_artifacts`, `prepare_attack_chains`, the check and the assembly step.
    - **`chains written`** keeps today's path. The ID pattern widens to `tachi_parts`' chain pattern, `CHAIN-[0-9]{3,6}`.
    - **Any other outcome** shows the outcome line in the report's Section 6 and on the PDF's Assessment Scope page.
    - **The PDF.** `#let chain-outcome` is emitted only when a record exists, and `main.typ` reads it with `default: none`. Pre-fix inputs therefore render byte-identically (US-2 #4).
  - **The report agent's text.** `threat-report.md:232` becomes: "Use the surfaced chains, at most five and one per terminal-impact finding (S-3(f)), in rank order. Print each one's converging count."
- **Why.**
  - A model can't meet SC-2's determinism or S-3(g)'s bound at fixture scale (C-2).
  - R-24 lets the run continue, but chains that don't match the record must never read as complete.
  - The populator's upsert is the proven way for a script to own a block inside a joined file.
- **Alternatives considered.**
  - *(a) A key that #396 declares:* it would tie the bundle to schema 1.5.
  - *(b) Leaving the file in place:* readers that go by file presence would still see it.
  - *(c) The model editing the rendered file:* the file would then have mixed authorship.
  - *(d) Reading the parts before the join:* the chains wouldn't come from the reference set (D-4).
- **Consequences.**
  - **Files:**
    - `orchestrator.md:395-554`;
    - `attack-chain-patterns-shared.md:127-143`, losing its `chain_id` tie-break and its no-tie claim;
    - `dispatch-rules.md:309` and `:332`;
    - `output-schemas.md:285` and `:359`;
    - the `threats.md` template and `attack-chain.yaml`;
    - `threat-report.md`;
    - the three readers and `main.typ`;
    - §8.3 and §8.5.
  - **Offline tests:**
    - two `plan` runs are byte-identical (US-2 #5);
    - the chain-cap variant (more than 105 chains) covers the cap, the remainder and every check case;
    - the tie cases;
    - a two-hop closure link, pinned under R-21;
    - the drift test, the fallback and the quarantine.
  - **Unchanged:** today's chain tests and goldens, for pre-fix inputs.
  - **Live:** US-2 #1.
  - **RK-4:** the pair scan and the chain file leave the orchestrator, whose share drops to at most five narratives, about 2k tokens. C-6(a) estimates the file at 90–120k tokens.
- **Supersedes or amends.**
  - **ADR-020 Phase 2.** The record replaces the boolean. "All chains recorded" becomes S-3(g). "No tie possible" becomes S-3(e) with S-2. "Top 5" becomes S-3(f). The placement moves to after the join.
  - **ADR-026** gains a dated note: Phase 3.6 no longer follows Phase 3.5.

### D14: Report assembly and the tree batches [Track: O]

- **Decision.**
  - **The tree batches: the orchestrator dispatches them (P-5).**
    - **Planning.** In Phase 5, D6's planner runs a `trees` stage over Section 7's open Critical and High findings and the baseline's `attack-trees/` listing. The planner, not the agent, applies today's Step 1 table:
      - **Rule 1** copies trees that have a baseline file, and generates only the missing ones;
      - **Rule 2** regenerates every tree, with Rule 3 reconciling the UNCHANGED ones.
    - **Dispatch.** The orchestrator dispatches typed `tachi-attack-tree-delta` batches of about 12 trees (D6 measures the size). They run in the foreground, at most 16 in flight (D6), two layers below the main session (S-8).
    - **Output.** Each batch writes its trees and its manifest part under `.tachi-build/trees/<plan_id>/`, as D6's batch-stage table rules.
  - **The copy and the merge: `scripts/assemble-report.py trees`.** The orchestrator runs it before the report batches.
    - **Copies** every generated tree from the path its batch input named, and every carried-forward tree from the baseline, byte for byte, under both Rule 1 and Rule 3 (FR-K5.3).
    - **Validates** each tree file: one Mermaid block, a size cap, and its ID on the allow-list before the ID becomes a path.
    - **Runs after `reconcile`.** The orchestrator runs it only once the `trees` stage reconciles to 0. A tree still missing then exits 4, which applies FR-K5.5 early, and the script never returns 3 (D4).
    - **Merges** the batch manifests into the schema-1.0 `attack-trees/.manifest.json` that the report agent reads (US-1b #5).
  - **The report parts.** The orchestrator dispatches typed `tachi-threat-report` batches, two layers below the main session. Each writes D3 parts under `.tachi-build/report/`, holding prose fragments and rows, with no markdown structure (NFR-10). D6's batch-stage table gives the unit, planner input and payload.
    - **One part per section:** `exec_summary`, `architecture_overview`, `cross_cutting_themes`, and three conditional ones:
      - `attack_chains`, only for `chains written`;
      - `agentic_patterns`, only when patterns are present;
      - `delta_summary`, only when there is a baseline.
    - **One part per batch of findings:**
      - `threat_analysis`: per-finding narratives, a one-line `tree_summary` for each Critical and High finding, and category summaries for Medium and Low findings;
      - `remediation_roadmap`;
      - `appendix`.
    - **Code alone writes** the frontmatter and Section 5.
  - **The assembly: `/tachi.threat-model` runs it (P-5).** `assemble-report.py report` runs after D13's and D12's checks.
    - It numbers the sections present, in template order, and writes the frontmatter.
    - It builds Section 5 in manifest order: `### {ID}: {threat}`, the metadata line, the `tree_summary`, the tree, then the delta and correlation notes.
      - Each tree is the Mermaid source between the standalone file's fences, byte for byte. It is re-fenced longer than any backtick run inside it (FR-K5.2).
    - It stamps the file (D4) and overwrites any `threat-report.md` an agent wrote.
  - **The checks.** A failure ends the run (D-3).
    - **FR-K5.5:** Section 7's Critical and High open IDs, the manifest and the tree files are one set.
    - **FR-K5.7:** every `.md` file in `attack-trees/` is listed, and the manifest equals its recomputed merge.
    - **FR-K5.3:** every carried tree equals its baseline file.
  - **The report agent loses its unused `Agent` tool.** NG8 bars only gains, and the removal closes the path for failure mode 2. This item can be cut from PR 2 on its own.
  - **Rule 2 is unchanged.** Every Critical and High tree is still regenerated after any delta, so no PM item arises. Copying UNCHANGED trees instead would be a PM item, and isn't proposed.
- **Why.**
  - The report agent has no Bash, and D-3 makes the orchestrator own Phase 5's batching. Two layers are cheaper than three, and in Run B the report agent spawned 17 stand-ins.
  - Assembly must follow the final outcome record and FR-N4.5's verdict.
  - File copies and a Section 5 built in code make FR-K5.2 and FR-K5.3 true by construction.
- **Alternatives considered.**
  - *(a) The orchestrator assembles:* it would run before the main session's checks.
  - *(b) `/tachi.threat-model` dispatches the trees:* Phase 5's batching would split across two layers, against D-3.
  - *(c) The plan in the report agent's brief:* the agent still can't reconcile, and the depth stays three.
  - *(d) A model-written Section 5:* transcription again.
- **Consequences.**
  - **Files:**
    - the script and its wiring (FR-E.5);
    - `threat-report.md`;
    - `attack-tree-delta.md`, whose parent becomes the orchestrator and which loses Step 1 and Rule 1's copy;
    - the reporting references and the template;
    - `orchestrator.md:766-790` and `tachi.threat-model.md`;
    - §8.3, §8.5 and the runbook's §5.
  - **Offline tests:**
    - inline equals standalone;
    - carried trees are byte-identical;
    - a missing tree, an unlisted file, a stale batch manifest;
    - section numbering across the conditional sections;
    - the merged manifest.
  - **Live:** US-1b #4 and SC-3.
  - **RK-4:** no tree or report text passes through the orchestrator.
- **Supersedes or amends.**
  - `attack-tree-delta.md` Step 1 and Rule 1.
  - ADR-049 D7, by a dated note covering `.tachi-build/trees/` and `report/`.
  - D1's tier change for `threat-report.md`.

### D15: Schema versions [Track: R (risk-scores.md, compensating-controls.md, the part schemas); O (threats.md, the record schemas)]

- **Decision.**

  | Artifact | Version | PR | Basis |
  |---|---|---|---|
  | `threats.md` | 1.4, unchanged | both | Body lines (FR-E.18, P-3's first option) need no bump. 1.5 belongs to #396. PR 2 fixes "1.2" at `output-schemas.md:285` |
  | `risk-scores.md` | 1.0 → **1.1** | 1 | Additive: R-30's marker, D9's flag and override markers, and FR-K6.1's parse-error section. The stamp is a comment |
  | `compensating-controls.md` | 1.0 → **1.1** | 1 | Additive: K8's two columns, the `CF` column's rule (the column is 1.0's; the renderer now fills it), one Section 4 block per finding, and FR-K7.4's section |
  | `attack-chains.md` | 1.0 → **1.1** | 2 | Additive: S-3(g)'s compact rows, remainder line and frontmatter counts, declared in `schemas/attack-chain.yaml`. D13 sets the shape |
  | Tree manifest | 1.0, unchanged | 2 | The per-batch manifests use the 1.0 shape. The merge validates its closed keys and emits one 1.0 file |
  | `threat-report.md`; `finding.yaml` (1.9); `output.yaml` | unchanged | — | D11 and D14 add no field to them. `output.yaml` stays untouched (C-4) |
  | `tachi.part/1`, `tachi.overflow/1`, `tachi.batch-input/1`, `tachi.plan/1`, `tachi.plan-pointer/1`, `tachi.stage-record/1` | 1 | 1 (S) | `contracts/part-files.md`; `tachi_parts.py` is the authority |
  | D11's and D13's files, and the checks' hand-off files | 1 | 2 | The same rule: `tachi.dispatch-record/1`, `tachi.brief/1`, `tachi.idmap/1`, `tachi.phase1-inventory/1`, `tachi.phase1-dispatch/1`, `tachi.chains/1`, `tachi.chain-narratives/1` and `tachi.check-handoff/1`, which `close` and `fail` strict-load (D4; RR5). The merged tree manifest keeps its own schema 1.0 key |

  **`risk-scores.md` 1.1's §2a when it would be empty (W1, 2026-11-22, T023).** It is omitted, as the 1.1 template says, so a file with no Section 4c finding keeps 1.0's layout. tachi's other conditional sections, such as `threats.md`'s 4c on a first run and the controls' empty bands, are omitted the same way. No reader depends on the heading:
  - §2's reader stops at the first table;
  - `parse_markdown_table(…, "## 2a. Resolved Findings")` returns `[]` without it;
  - R-26's tolerant reader reads its absence as no RESOLVED rows;
  - no extractor reads §2a.

  **The rule.**
  - Every JSON file names `schema: "tachi.<kind>/<major>"`.
  - A schema's key set is closed per version, and any key change bumps the major.
  - Readers accept exactly the versions they implement.
  - The key sets live in `tachi_parts.py`, and the shared reference is drift-tested against them.
  - #399 pins the stage-record versions it reads.
- **Why.**
  - NFR-1 permits additive changes, and a minor bump signals one. No reader gates on these two files' version: `extract-report-data.py:2806` reads `threats.md` only.
  - P-1 forbids claiming 1.5.
- **Alternatives considered.**
  - **No bump:** consumers can't see the additive change.
  - **YAML schemas:** they need PyYAML (R-32).
- **Consequences.**
  - The templates' `schema_version` lines and the "Always 1.0" prose change.
  - `schemas/risk-scoring.yaml` and `schemas/compensating-controls.yaml` move only if their own structure changes.
- **Supersedes or amends.** ADR-020's attack-chains 1.0, through a Revision History entry, made together with D13.

### D16: Test and CI placement [Track: S, R, O]

- **Decision.**

  | Gate | What it runs |
  |---|---|
  | `tachi-install-fidelity.yml`: two new jobs, `f374-offline` (ubuntu-latest, 3.11) and `f374-py39-floor` (ubuntu-24.04, Python 3.9, pinned for #396's reason), on one module list. A third job, `f374-macos` (macos-latest, 3.11), runs `test_sarif_identity.py` alone, so D7's real case-insensitive URI case runs on the platform most adopters use (KB 24). `f374-offline` alone also enforces the coverage gate below (`/aod.analyze` D1) | **PR 1:** `test_tachi_parts.py`, `test_tachi_stage.py`, `test_fixture_374.py`, `test_runtime_floor_374.py`, `test_contract_text_374.py`, `test_render_risk_scores.py`, `test_render_compensating_controls.py` and `test_sarif_identity.py`. **PR 2:** `test_threats_md_join.py`, `test_threats_sarif.py`, `test_chain_script.py`, `test_threat_model_checks.py` and `test_report_assembly.py`. The ungated `test_attack_chains.py` and `test_attack_chain_extraction.py` join `extraction-fidelity`, because PR 2 changes their readers |
  | `tachi-pytest.yml` | No new module, because none needs the bash matrix. `test_cvss_category_defaults.py` stays, and its `paths:` gain the shipped CVSS module (KB 3). D1 retires `generate-risk-scores-sarif.py` at PR 1, so three modules migrate in that PR and keep their gates: `test_owasp_2026_contract.py` and `test_affected_assets_wiring.py`, which load it at import, and `test_tachi_parsers.py:610` and `:620`. The renderer emits the taxa, so FR-012a's taxa contract moves to it |
  | `tachi-permissions-verify.yml` | No pytest module. Its guard checks every agent, command, §8 and runbook edit: §8.3–§8.5 and the runbook's §5 change in the commit that adds the write (C7), and the commands keep `{description}` (C5) |

  - **F-373's S-13 import gate and the manifest.**
    - `REQUIRED_SCRIPT_NAMES` gains each new entry and helper.
    - The `{"tachi_parsers"}` allowance widens to each new helper.
    - `INSTALL_MANIFEST.md` changes in all three places: the "4 Python files" row, the Script Files table and the machine block.
  - **Confinement.**
    - `ENTRY_SCRIPTS_IMPORTING_PARSERS` gains each new entry, and the AR-14 case copies each entry's local-import closure, computed with `_import_closure`.
    - `test_write_confinement.py` gains a group that runs each new entry on the gated fixture in a throwaway project, and asserts that every write lands under `{out}` and that no bytecode is written.
    - `RECIPE_DOCS` gains the three commands.
  - **Lock-step (KB 3).** A module, its input surfaces, its `paths:` entries and its invocation line in each f374 job that runs it land in one commit.
  - **The coverage gate (Amendment, 2026-11-22, `/aod.analyze` D1).** Constitution VI and VII require at least 80% unit coverage of business logic (`constitution.md:80`, `:107`).
    - **Tool.** `pytest-cov>=4.1`, already in `requirements-dev.txt` (F-128), installed only in `f374-offline`. It is a test dependency, so the shipped scripts stay stdlib-only (NFR-2).
    - **The gated set** is each PR's new and rewritten shipped modules:
      - PR 1: `tachi_parts.py`, `tachi_scoring.py`, `tachi_scoring_rules.py`, `sarif_common.py`, `tachi-stage.py`, `render-risk-scores.py` and `render-compensating-controls.py`;
      - PR 2 adds `join-threats-md.py`, `attack-chains.py`, `check-threat-model.py`, `assemble-report.py` and the rewritten `generate-threats-sarif.py`.

      `tachi_parsers.py` is extended, not new, and its legacy code would set most of its figure, so it is held to a ratchet instead of the 80% bar (below). `sarif_common.py` exists today too, but it stays in the 80% set, because it becomes the shared emitter and is largely rewritten (D7, D8).
    - **Mechanism: in-process import.** The gated tests load each hyphenated entry from its path with `tests/conftest.py`'s importlib loader (`_load_hyphenated_script`) and call its `main(argv)`, so pytest-cov measures it in the test process. Each entry keeps its work in `main(argv=None) -> int` behind a thin `__main__` guard, as `populate-affected-assets.py` does. Subprocess runs stay for what only a process shows (the 3.9 refusal before any import, bytecode and write confinement), and they don't count. Coverage's subprocess support was rejected: its child processes can write `.coverage.*` files into the tree under test, where the declared-paths and confinement checks would see them, and its setup differs across pytest-cov and coverage versions.
    - **What counts (re-run C3).** A test that drives a gated script by subprocess doesn't count toward its coverage. So each gated script's tests exercise its `main(argv)` in-process, exit codes and printed output included, and a subprocess case is kept only for what a process alone shows.
    - **The config,** `tests/scripts/coverage-f374.ini`. `[run]` sets `source = scripts`, so a gated module that no test runs counts at 0%. `[report]` lists the gated set in `include` and sets `fail_under = 80`, for total line coverage over the set. A module joins `include` in the commit that wires it (lock-step), and the file joins the workflow's `paths:`.
    - **The `tachi_parsers.py` ratchet (re-run E3).** The floor and the check count the same tests: `tests/scripts/test_tachi_parsers.py`, where the bundle's parser tests land, so each new parser function's unit tests go there.
      - **The floor.** T001's pre-state census, in a scratch clone before any parser change and under Python 3.11 as in the job, runs `python3 -m pytest --cov=scripts --cov-report= tests/scripts/test_tachi_parsers.py`, then `python3 -m coverage report --include=scripts/tachi_parsers.py --precision=1 --show-missing`. `prestate.md` records the total as the floor.
      - **The check.** `f374-offline` repeats both commands after the gate step, with `--fail-under=<floor>` on the report. So the module may not fall below its floor, and new parser code must be tested at least as well as the code already there.
      - The floor is never lowered within the bundle.
    - **Enforcement.** `f374-offline` runs its module list as `python3 -m pytest --cov --cov-config=tests/scripts/coverage-f374.ini --cov-report=term-missing …`, so a gated set below 80% fails the job. The ratchet's check then fails it if `tachi_parsers.py` falls below its floor.
    - **Record.** Each PR's CI record carries the gate's per-module and total figures, and `tachi_parsers.py`'s figure against its floor, with the missed lines that `--show-missing` lists inside the bundle's new parser functions.
  - **Named tests.**
    - The offline identity test (FR-E.2), in `test_sarif_identity.py`: in PR 1, the two files and the cross-file pairs; PR 2 adds `threats.sarif` and FR-E.13's pin.
    - The R-34 Sections 2/4 check, in `test_render_compensating_controls.py`: every cell D2 lists is filled, or its mismatch is flagged.
    - S-11, in `test_runtime_floor_374.py`: `ast.parse(..., feature_version=(3, 9))`, a required `from __future__ import annotations`, and the core path run with `yaml` blocked by an import hook, which must give byte-identical output. The 3.9 path uses no later API, such as `sys.stdlib_module_names` (3.10) or `datetime.fromisoformat` on a `Z` suffix (3.11).
    - Goldens read `tachi_parts.VERSION`, never a literal (D4).
    - S-4's generator: it regenerates into `tmp_path` and byte-compares; the sizing check; an AST ban on every `random` method except `random()` and `seed()`.
    - Hostile inputs:
      - a stale part, a forged heading and a fence break-out;
      - `NaN`, `Infinity`, `1e400` and a 30-digit integer;
      - duplicate and unknown keys, and a six-key overflow object, classified `overflow`;
      - out-of-batch, duplicate, Unicode-digit and trailing-newline IDs, and two spellings of one canonical ID;
      - a symlinked part and an oversized one;
      - C0, C1, bidi (U+200E, U+200F and U+061C included), U+2028 and tag-block (U+E0000–U+E007F) characters;
      - in a narrative field, digits outside a slot, a bad slot and a digit-bearing component name written out (S-4's variants): each takes the per-field fallback, while a structural failure still rejects the part;
      - a literal `{{` that isn't a slot, such as `{{7*7}}` in an evidence field, written escaped;
      - an evidence `file` with a scheme, a leading `/`, a backslash or a drive letter;
      - a plan file or batch input edited after `plan`, and a `--plan` that disagrees with `current.json` (exit 2);
      - changed inputs;
      - exhausted caps;
      - `fail` leaving earlier outputs alone in KB 21's four cases: re-run, resume, failed run and `--output-dir`. Plus a check that fails on the staged files, which changes nothing, and a half-applied pair, which `fail` restores.
    - Escaping: every reference the renderer writes decodes back through `tachi_parsers`, and every shipped example parses as before (D3). The round trip includes a literal `&lt;` in agent text, so a double decode fails it. An UNCHANGED controls result whose evidence holds `&lt;` and `|` is carried across two runs, and its evidence must be byte-identical, so escaping never compounds (D2).
    - Contract text, in `test_contract_text_374.py`:
      - no hand-back and no platform-neutral clause;
      - shipped scripts only;
      - orchestrator fences that use `python3` and shipped names only (FR-N4.4);
      - the fixed prompts;
      - foreground dispatch;
      - the presence check, with its 3.9 floor;
      - the reference matching the code's key sets and slot table;
      - PR 1's inert Track O text: no PR 1 agent or command loads the record and brief templates, and `finding-format-shared.md` carries neither the end marker nor the "brief" rename until PR 2 (D11).
  - **The init baseline.**
    - A commit that edits one of the 61 substitution targets regenerates `tests/fixtures/init-baseline-tree/` in the same commit, after the substitution unit tests pass (KB 1, as KB 26 applied it; live since #419).
    - The targets this bundle is likely to touch: `docs/INSTITUTIONAL_KNOWLEDGE.md`, `docs/architecture/01_system_design/README.md`, `docs/devops/CI_CD_GUIDE.md`, `docs/testing/README.md` and `.claude/README.md`.
  - **Process.**
    - `release-please-config.json`'s `extra-files` gains `scripts/tachi_parts.py`.
    - Commit before gating, because the harnesses clone HEAD.
    - Run only in a scratch clone (#365).
    - T001 records every job's pre-state, the new jobs included.
- **Why.**
  - FR-E.5 and NFR-7 require it.
  - Only a real 3.9 interpreter catches a post-3.9 standard-library API, and F-373's S-13 import gate sees only load-time imports (S-11).
  - The two chain modules are ungated today.
- **Alternatives considered.**
  - **Waiting for #396's floor job:** this bundle merges first.
  - **Pytest in permissions-verify:** that workflow has no pytest (ADR-049, Alternative 3).
- **Consequences.**
  - The new jobs take under 2 minutes, but the 33-minute matrix still runs on every push.
  - The two floor jobs consolidate when #396 rebases (filed on #400).
- **Supersedes or amends.**
  - F-373's manifest contract: the list and the allowance widen.
  - ADR-049 D1: the guard is unchanged.

## Ruled by the PM at the plan review (2026-11-22)

The PM ruled on the three items that change what users see, and on P-7. Each ruling's text is folded verbatim where it applies.
- **A (D2, D9): asset tags and the SLA clock. AMENDED.** A changed tag set is an input change, not a correction: its own `retagged` flag, and a review-date rule for each direction. Folded in D9, "Tag-driven band changes", and applied in D2 and D10 (spec US-5 #13 and #14).
- **B (D7): ID reuse. AMENDED.** IDs are never reissued: a high-water mark written by shipped code and checked with exit 5 in PR 2, and the `reused-id` flag in both PR 1 renderers. Folded in D7, "ID reuse" (spec FR-E.19, US-6a #10 and US-6b #5).
- **C (D8): field placement. AMENDED, placement accepted.** Each correlated result's message names its group, and its primary or its peers. Folded in D8, "Field placement" (spec FR-E.20, US-6a #11).
- **P-7: SC-8's tolerance. AMENDED, 10% accepted.** At most 10% per stage, with output tokens read from the session's usage records. Folded in the spec's SC-8 and in plan.md's P-7, and this ADR claims a cheaper stage only as P-7 allows (Consequences).

**Confirmed at rev. 1 (condition 3), 2026-11-22: CONFIRMED_WITH_AMENDMENTS.** The PM confirmed rev. 1's folds that went beyond the ruled text:
- **1. `retagged` scope: CONFIRMED.** It also covers the values that follow a band the tags moved, such as the SLA and the review date. None is flagged `corrected`, `follows-band` included (D9).
- **2. TW-L2's fallback threshold: AMENDED.** 10% stays the follow-up trigger, and a stage above 25% in any W5 run comes back to the PM before its PR merges. The contract text states the check (no digit outside a slot), and each PR's notes name the fixed sentence and the flags. Folded verbatim in D3, and in Consequences and plan.md's W5.
- **3. Ruling C's peer cap: CONFIRMED** at 10 (D8).
- **4. The reference-set oracle class: AMENDED, accepted and bounded.** Folded verbatim in D3. The oracle's first class reads "a flagged value (corrected, or retagged under ruling A)" (spec NFR-1; plan.md, Verification 7).
- **PM 1(b), the `ref` narrowing: ACCEPTED.** `ref` takes only the finding's own taxonomy IDs and has no CVE form, so a cited CVE, or an ID the finding doesn't carry, takes the fallback (D3).

**For the PM's awareness, no objection:**
- **D1:** SV-2b is carved at the plan stage, so the dispatch records are manifests. PR 2's release notes (item 5) say what stays model-authored.
- **D5:** rows with equal scores sort in S-2 order, so some rows reorder against today (release notes, item 4). The oracle attributes the reorder as its own class.
- **D14:** the report agent loses its unused `Agent` tool. This is a reduction, and NG8 bars only gains.
- **D4:** the presence check runs in all three commands. It also checks the 3.9 floor before any dispatch and names the version found (PM finding 7).

## Alternatives Considered

Each decision records its own alternatives. Three bundle-level alternatives were weighed:
- **Chunked agent output, with checks added afterwards** (PRD D-2 option (a)). It keeps today's tier, but leaves the arithmetic, completeness and identity to the model, and the checks would only report failures that code could prevent. Rejected.
- **Render everything in code, including `threats.md`'s tables and Phase 3's compilation** (SV-2b, at the feasibility ceiling). It would fold #356 in and move ADR-047's authority into code. It is also the most expensive item on the least certain track, and the first budget carve (R-23). Not adopted in this bundle.
- **One PR.** It fails TW-0 at the priced central (9.4 against 9.0 days; feasibility §13.4). The PM ruled the split (R-34).

## Consequences

### Positive

- **Complete outputs at any size.** Each stage's output is bounded per response, reconciled from disk, and complete by construction (SC-1).
- **Correct arithmetic.** Composites, bands, residuals and totals come from tested code, and inherited scores are recomputed and flagged (SC-4, SC-5).
- **Stable alerts.** Alert identity is stable across baseline-aware runs, under GitHub's documented key, for all three files (SC-6).
- **Contracts that can be checked.** Typed dispatch, provenance, completeness and the Phase 3.5 outcome are all checked by shipped code.
- **Small runs should cost less, and the orchestrator's context shrinks.** No agent authors SARIF, so a small run's output tokens should fall. Public text claims a stage got cheaper only if its measured delta is below zero (P-7, SC-8). The chain script and report assembly take large outputs out of the orchestrator's context (RK-4).

### Negative

- **More code to maintain.** About nine new installed scripts and helpers form a production code tier.
- **More intermediate files.** `.tachi-build/` grows with parts, plans and records, about 1 MB per invocation at fixture scale.
- **One re-key event per SARIF file:** the scorer and controls files at PR 1, and `threats.sarif` at PR 2.
- **More dispatches on large runs.** Batching multiplies agent invocations above the threshold.
- **A fragile window.** Between the releases, PR 1's contract text forbids stand-ins, but Phase 2's re-dispatch doesn't ship until PR 2.

### Mitigation

- **The gates.** Each script is tested offline on synthetic fixtures and gated in CI with lock-step wiring (D16). The renderer's goldens are written before its code.
- **Binding release notes, per PR** (spec, "Release notes, per PR"), state each re-key event, each new stop and each fragile area. For the stages each PR changes, they also name the narrative fallback's fixed sentence, the `input:<field>:narrative-fallback` flag and the `input:<field>:truncated` flag (PM confirmation, ruling 2; Architect re-review RR2).
- **Smoke runs.** R-27's runs under the session profile, one per PR that changes a write set.
- **Constants, not settings.** The batch sizes are constants measured at W0 (D6), and an overflow in a live run re-batches narrower and is recorded.

### Back-pointer notes

At the cut line, the amended ADRs gain dated notes pointing here:
- ADR-046 and ADR-013: partially superseded;
- ADR-049 D7: the new `.tachi-build/` writers;
- ADR-018: correlation's location key is local, and the delta classes are refined;
- ADR-020 Phase 2: the record, the bound and the total order;
- ADR-017 D2: largest remainder in the renderers;
- ADR-048 D3: the emitters enforce;
- ADR-026: Phase 3.5 now runs after the join.

## Known limitations

- **Consistency, not provenance.** The provenance and completeness checks prove that the orchestrator's records are consistent with each other. A fabricated but consistent record passes, and transcript-level proof stays with #399 (D12).
- **GitHub's server-side alert key isn't documented.** FR-E.2 models the documented inputs, and, unless a scratch-repository check runs, the release notes say so (D7).
- **Numbers in narrative prose.** A number word that states a count, score, band or percentage passes the digit ban, though the contract text forbids it. The contract text has the agent write a version, a port or any other term with digits without them, and one written with its digits sends its field to the per-field fallback (D3).
- **Carried legacy prose.** A pre-1.1 `risk-scores.md` stores its prose without slots, so D9 carries it as evidence. It can state a number that the renderer has since corrected, and the finding's flags mark that (Architect re-review RR1).
- **Quoted control characters.** Step 10 of D3 rejects a part with any string that holds a C0 or C1 control character or a bidi control, evidence included. So a part that quotes such a snippet from the target, a Trojan Source line for example, is rejected and retried, and if every attempt quotes it, the stage exits 4. The failure is loud, never silent. A later revision may escape these characters in evidence fields instead.
- **An ID can be reissued once** (ruling B). An ID resolved before the baseline run, which the baseline no longer lists, can still be reissued once (D7).
- **A drift form's derived status** (ruled at W2). Where Section 7's form has no Status column, a finding with a usable baseline row is carried as UNCHANGED (D9). If the threat model gave a live ID to a new finding, that finding inherits the old row's inputs. Until PR 2's ID mark (ruling B), the only signals are its `input:delta_status:not-in-form` flag and the stage record's list.
- **A drift form's carried threat text is the baseline's short form** (ruled at W4, 2026-11-24, from T066's group U-2, and accepted by the PM at W4 for PR 1, whose release notes name it with the regenerate remedy). Where Section 7's form lacks `threat`, S-12(b) takes it from the baseline row: its §3 `**Threat**:` line, else its §2 cell (D9).
  - A v4.48.x baseline has no such line, and its agent cut the §2 cell to about 60 characters. So a carried finding's `message.text`, §2 cell and controls text are that cut text.
  - The 1.1 file's §3 line then carries it to the next run, until `threats.md` is regenerated in the table form, whose Threat column supplies the text again.
  - Neither fuller source is safe to read in PR 1, and neither would match the shipped files, whose copies of the text differ from each other:
    - a legacy §3 heading's `### ID: <title>` holds the threat in four shipped scorer files, but the component in a tracked legacy fixture;
    - a baseline SARIF's `message.text` holds the agent's own summary, scores included, in one shipped file, and ruling C's sentence in any 1.1 file. It would also be a second-file source, which D9's "only a value that row records" excludes.
  - The upgrade is a filed T080 issue, not only an idea (PM W4): read the colon-form title as the threat only when the row's §2 cell is its documented truncation, in `read_baseline_scores`. That check passes 17 of `consumer-agent-app`'s 19 carried findings. Its value falls with every PR 1 run, because a 1.1 baseline's §3 `**Threat**:` line then holds the short form, which S-12(b) reads first, so the issue names regenerating `threats.md` as the durable remedy.
- **The SARIF fallback reports no repeated member** (ruled at W4, 2026-11-24, with PM W4 ruling R-F's report). Under D8's fallback, which reads no Section 4a, a member that two of the SARIF's groups list goes to the first by the same claim rule, and nothing reports it. A file that the shared emitter writes gives each result one group, so only a model-authored `threats.sarif` (until PR 2), a legacy file or an edited one can list a member twice. Returning the same `repeated` entries from `parse_sarif_member_set` is a follow-up for T080.
- **The architecture file isn't a digest-checked plan input** (ruled at the P0 checkpoint). When `refs` names no `architecture`, both agents read the run's snapshot, the `architecture.md` beside the `threats` file (D7, ruled at W3 for the control analyzer), while the renderer resolves D7's chain: the body line, then the default. So a mid-run edit, or a source that has drifted from its snapshot, can give the agents' judgment (the scorer's reachability, the control analyzer's component mapping) and the renderer's asset tags different bytes. That is consistency, not identity: the URI chain is the same both times, and the digest of the file the renderer read is in `input_digest`. Making the file a digest-checked input would turn a mid-run edit into exit 2, against D7's "Nothing here stops a run", and resolving the whole chain at plan time would change the agents' fallback, so PR 1 does neither.
- **The extractors find a section by substring** (ruled at W3, from T087's observation). `parse_risk_scores_findings`, `parse_risk_scores_severity`, `parse_compensating_controls_md` and `generate-risk-scores-sarif.py` take the first line that holds a heading, or a label such as `Severity Distribution`, anywhere in it. A component name, a cell, a prose line or a quoted snippet that holds that text earlier in the file makes them read the wrong table, and nothing warns: the report's and the infographics' counts come out wrong. v4.48.4 has the same readers and layout, so PR 1 doesn't widen the exposure, and none of PR 1's checks or carries uses these readers (D3, "Finding a section"). The follow-up (T080) matches the rendered heading or label as an exact line outside fences first, keeps today's search for a file that lacks it, and re-checks the extractors' goldens. PR 2's joiner escapes `#` in every `threats.md` cell (O-β).
- **A very large `risk-scores.md` fails its read-back** (ruled at W3, from FX0's question). The next run's reader stops at D3's 16 MiB input cap, so a staged file above it wouldn't read back, and the render exits 4 with the staged files kept for diagnosis. That takes some 4,000 findings (FX0's estimate), about ten times W5's base set. Writing the file anyway would make the next run score fresh and carry no human governance field. A later revision may raise the cap for a stamped file.
- **Still model-authored:** `threats.md`'s tables and Section 6 (D1). Section 6 is checked against the reference set.
- **A flagged controls §2 cell shows the agent's text** (ruled at W3). In PR 1, §2's Control Status, Control Category, Component and MAESTRO Layer cells stay the agent's (R-34, D2).
  - Where one disagrees with the structure, the SARIF and the totals follow the structure. A reader of §2 reads the agent's text instead: `parse_compensating_controls_md`, and so the PDF report and the infographics.
  - §1's flag line, §7 and `integrity-flags` mark the finding.
  - FR-K8.1's follow-up, which T080 files, turns the four checks into fills.
- **The controls file's §3 lists only mapped controls** (ruled by the PM at W6, 2026-11-24, Q3(b)). Section 3 of `compensating-controls.md` lists only the controls that a finding's evidence names. A control that the scan detects but that no finding maps to isn't written, because a part carries evidence per finding (D2), so no part can hold it. v4.48.4's 1.0 template asked for one subsection per detected control, which let its agent list such a control. No residual score depends on one. Whether such controls are listed, and how, is a contract question for a follow-up that T080 files.
- **A slip that equals a finding's own ±1.0 bound** passes as a documented clamp (D10).
- **A peer of a legacy primary whose assessment isn't recorded** (ruled at W3). With tags that differ from its primary's, it keeps the primary's score, flagged `unchecked` (D9, "Peers"). Its primary has no sub-scores, so the peer's 1.1 row records none either, and the next run reads it as a legacy row: D10's legacy check then tests that score under the peer's own tags. It can pass, stay `unchecked`, or be corrected, and a correction is flagged. This needs a pre-1.1 baseline, a correlated group and differing tags together.
- **The rules' taxonomy links name their taxonomy only** (ruled at W3). Each rule's `relationships` target names `OWASP` or `CWE` by `toolComponent.name`, as both templates have since 1.0. The run's `taxonomies` list no `OWASP` Top 10 component and only some of the CWE targets, so a consumer that resolves a target by index or guid finds none. Aligning the two joins T080's taxa follow-up (`contracts/sarif-result.md`).
- **A malformed persisted controls item** (the residual of T064's SA-1, ruled at the P1 checkpoint, for T080). A baseline controls file whose persisted `matrix_row` or `recommendation_body` was edited into a form the part validator rejects stops the controls stage: every attempt of that finding's batch is rejected, and `reconcile` exits 4. Restore or delete that row of §7's `### Assessment Inputs`, or run without the baseline. A public item check is a follow-up.
- **Link syntax passes the escapers** (from T064's SA-9, for T080). D3's sink rules don't escape `[`. So copied text that holds `[text](url)` or `![x](url)`, a threat or a cited file name for example, is a live link or image where GitHub renders `risk-scores.md` or `compensating-controls.md`, §7's Assessment Inputs included. A code span, such as §3's "Detected in" line, stays inert. Raw HTML and `<url>` autolinks are already out, because `<` is escaped, and a bare URL links anyway. v4.48.4 is the same. Escaping `[` would be a tenth reference, a question that T080 takes to the PM.
- **The declared-paths check sees `{out}` only** (from T064's SA-14 and T067a's L9). An agent's Write tool reaches whatever the permission profile allows. A changed file that fits the stage's grammar, a rewritten `plan.json` or another batch's input for example, isn't undeclared, and the plan's digest and each batch input's catch those two (D3, D6). So the profile, not these scripts, confines an agent, and D4's check stays detective (KB 17). The snapshot also grows with every run: it counts every file under `{out}`, `.tachi-build/` included, where nothing is deleted (D3). A full run of both stages adds about 160 files at fixture scale, so after about 125 runs into one `{out}` the snapshot passes D4's 20,000 entries, and every later run skips the check with `declared-paths-skipped`. Pruning old plan directories restores it. Naming that remedy in the warning, or bounding the snapshot, is a T080 follow-up.
- **Parts aren't pinned between `reconcile` and the render** (from T064's SA-15, for T080). The render re-validates every part, so what it reads is valid either way. But any agent can write any batch's part, so two renders of one plan can differ if a part is rewritten between them. Recording each accepted part's SHA-256 in the plan would change the plan schema, so PR 1 doesn't.
- **An input can be hashed and parsed from two reads** (from T064's SA-6, for T080). The planner reads the baseline `risk-scores.md` and the controls stage's scored input once to hash and once to parse. Each renderer re-reads one input after checking its digest: the scorer its baseline, the controls renderer its `risk-scores.md`. Only a writer racing the run can make two reads differ, and `input_digest` would then describe bytes other than those parsed. No such race was built, so this is a provenance gap, not a shown safety one.
- **Evidence text isn't checked against the cited file** (from T064's SA-16, for T080 with #360). The controls renderer resolves each evidence `file` and never reads it. So a snippet or a summary can hold text that the file doesn't: a hallucinated one, or one that an injected agent puts under a real file name. Requiring the snippet's first line at its `file:line` would catch both.
- **Follow-ups (spec S-16).** These stay out of scope:
  - the architecture snapshot's basename;
  - an `Agent(general-purpose)` deny rule for the isolated-operation profile;
  - dispatching Phase 2 from the command layer.

## References

- **This feature:**
  - PRD: [PRD-374 v1.3](../../product/02_PRD/374-large-architecture-pipeline-resilience-2026-11-21.md), §4 (D-1 to D-7), §10 and §13;
  - spec: [spec.md](../../../specs/374-large-architecture-pipeline-resilience/spec.md), with its rulings S-1 to S-16 and the PM's spec-review rulings;
  - research: [research.md](../../../specs/374-large-architecture-pipeline-resilience/research.md);
  - feasibility: [feasibility-check.md](../../../specs/374-large-architecture-pipeline-resilience/feasibility-check.md), §3, §4 and §13.
- **The normative key sets and CLI:** [contracts/](../../../specs/374-large-architecture-pipeline-resilience/contracts/) and [data-model.md](../../../specs/374-large-architecture-pipeline-resilience/data-model.md).
- **Platform:**
  - GitHub Docs, "SARIF support for code scanning": https://docs.github.com/en/code-security/reference/code-scanning/sarif-files/sarif-support
  - OASIS SARIF 2.1.0: https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html
  - FIRST CVSS v3.1 specification: https://www.first.org/cvss/v3.1/specification-document
  - Claude Code sub-agents: https://code.claude.com/docs/en/sub-agents
- **Institutional knowledge:** KB Entries 3, 7, 18, 19, 21, 22, 24, 25 and 26 (`docs/INSTITUTIONAL_KNOWLEDGE.md`).

## Revision History

| Date | Change |
|---|---|
| 2026-11-22 | Proposed at `/aod.project-plan`. Four architect passes (scoring, SARIF, mechanism, orchestrator) drafted D2–D16, which were merged with D1 and harmonized: script names, the `.tachi-build/` layout and the step order. Acceptance is pending the plan review, and PM items A to C go to the PM |
| 2026-11-22 | Rev. 1, after the plan review (Architect CHANGES_REQUESTED, 18 findings; PM APPROVED_WITH_CONCERNS, 8 findings). Folds the PM's rulings A, B and C verbatim in D9, D7 and D8, with the `retagged` and `reused-id` flags, and applies P-7. D3 gains one slot syntax, a closed per-stage slot table with `name` and `ref`, a class for every payload string, a per-field narrative fallback, schema-first validation, a checked plan digest and one identifier module, and its escaping now uses references the readers decode. D4 renders to `staged/` before replacing, restores pre-images on failure, checks the 3.9 floor, keeps one exit table, and fixes PR 2's order: a run-level plan at Step 1.5, and Phase 3.6 and Phase 4 before the parts. D6 rules the `trees` and `report` stages and names items O-α and O-β, to be ruled before W2′. D9 carries §3's prose, and D10's legacy list tests the tags first. D16 adds a macOS job and names the migrating modules. Status stays Proposed until the Architect's re-review |
| 2026-11-22 | Rev. 2, after the Architect's re-review (APPROVED_WITH_CONCERNS: RR1 and RR2 MEDIUM, RR3 to RR6 LOW, and nits) and the PM's confirmation of rev. 1 (CONFIRMED_WITH_AMENDMENTS). RR1: each narrative field's validated, slotted text is persisted (scorer §6, controls §7's `### Assessment Inputs`), and carried or copied text is decoded, re-validated and re-resolved, while legacy prose stays evidence (D2, D3, D9, Known limitations). RR2: over-limit prose is cut and flagged `input:<field>:truncated`, never rejected (D3, D9). RR3, and RR4 as item O-γ, are ruled before W2′ with O-α and O-β (D6). RR5: `threat-model` joins the plan and stage-record enums, a plan with no units takes a null `batch_size`, and `tachi.check-handoff/1` is named (D15). RR6: the ADR-049 note's writers, and row 2's exceptions (D3, D4). The nits, the second escaped-pipe row and a literal `&lt;` in the round trip (D3, D6, D9, D13, D16). The PM's rulings 1, 2 and 4 are folded verbatim, with the release-note facts (D3, D9, Mitigation), and the confirmations are recorded. Accepted (provisional pre-PR; the commit SHA is filled at merge) once the lead checks this fold, with no further Architect pass |
| 2026-11-22 | **Accepted** (provisional pre-PR; the commit SHA is filled at merge). The lead checked rev. 2 against RR1's and RR2's required text. It accepted the author's readings: the chain check's 2 prints and continues under R-24, and step 9's reject rule is scoped to step 9, so step 10's character checks still reject. It folded the gap rev. 2 noticed: a carried UNCHANGED controls result's evidence takes RR1's decoded path, with a two-run test (D2, D16). It recorded quoted control characters under Known limitations. plan.md is dual-signed: PM and Architect, both APPROVED_WITH_CONCERNS. This ADR cites the re-review's findings as RR1–RR6 (N1–N6 in its results file), so they don't collide with #397's N-items |
| 2026-11-22 | **Amendment (2026-11-22, `/aod.analyze` D1).** Not a numbered revision: "ADR-050 rev. 3" is reserved for PR 2's rulings (T086–T088). D16 gains a coverage gate for Constitution VI and VII's 80% bar. `pytest-cov>=4.1` is installed in `f374-offline` only. That job enforces total line coverage of at least 80% over each PR's new and rewritten shipped modules, measured in-process through `tests/conftest.py`'s importlib loader. `tests/scripts/coverage-f374.ini` holds `source`, the `include` list and `fail_under = 80`, and `tachi_parsers.py`'s figure is reported, not gated. Also (`/aod.analyze` F2): D5 and D16 call the import gate "F-373's S-13 import gate", and bare S-13 stays the asset-tag ruling. After the re-run (E3 and C3), `tachi_parsers.py` is held to a ratchet at its T001 floor, measured over `test_tachi_parsers.py` alone, instead of only being reported, and D16 states that tests driving a gated script by subprocess don't count |
| 2026-11-22 | **Amendment (W1, T023).** Not a numbered revision. D6 gains its "Amended at W0" table: `risk-score` 16, `compensating-controls` 13 and `trees` 12. They come from the contract-shaped reading of T003's proxy, which adds D3's slots and the JSON layout to row E, and T021(a)'s confirm-or-re-amend rules are decided in advance. SC-8's example is `ascii-web-api` (P-7, as G0 routed). D2 records AR-T3's reading: a carried UNCHANGED controls result, its evidence-class values included, is read from §7's persisted inputs, never from the rendered §2, §3 or §4. D5 points to the frozen signatures in `contracts/module-signatures.md`. The eight amended ADRs gain their dated back-pointer notes (P-1) |
| 2026-11-22 | **Amendment (W1, T023, after the review of T005–T009).** Not a numbered revision. D3 records the reading of an evidence entry's `file` and `line`: closed values on input, evidence on output. D4 records path 1's bounds: a named shipped script that isn't installed stops the run with the install remedy, and a spawned agent that fails stays the coverage gate's warning in PR 1. The readings that the sources left open are ruled in the governing contracts: `part-files.md` (field paths and flags, validation order, values, and the plan's halving and retry readings), `cli.md` (the `reconcile`, `fail`, `architecture-source` and `--version` outputs) and `sarif-result.md` (the correlation sentence's exact form) |
| 2026-11-22 | **Amendment (W1, T023, from T021(a)).** Not a numbered revision. T021(a) confirms none of D6's sizes and re-amends none. Its per-unit text is a script's template, its 13 measures a rejected reading, and no JSON part was written. Every token reading in the session was below 3.2, though. D6's second W1 rule is made continuous: below 3.2, u = p90 ÷ r, with no extra 1.25. One calibration Write per part stage (lane L, before T021(b)) now decides, by a table in D6, and fixes whether P-7's example stands, which needs r ≥ 2.654. D6 also notes the 128k response cap of W1's environment |
| 2026-11-22 | **Amended at W1 (T023, from the calibration).** Not a numbered revision. Each stage takes its own measured r. With `risk-score` at 2.598 and `compensating-controls` at 2.781, the sizes are 13, 11 and `trees` 12 (from 16, 13 and 12). Both part sizes are at least 11, so P-7's example, `ascii-web-api`, stands. SC-8's controls target is a fixed copy of the fixture's stub codebase, passed as `--target` in T021(b) and T075. D6's Limits gain a dated note: Claude Code 2.1.330 has no foreground dispatch, so the completion rule replaces "foreground" here and in D4's Step 3, and the spec's wording goes to the PM as an erratum. For PR 2, the S-9 spike asks whether a dispatching subagent can wait for its children |
| 2026-11-23 | **Amendment (W2, before T045 and T046).** Not a numbered revision. **D7:** `plan` checks the explicit `--architecture` candidate with the resolver's first step. A refusal, a syntactic one included, no longer stops `plan`, and is recorded as the plan's `architecture_warning`, which every stage record of the plan lists first. **D3:** the plan holds `refs`, and each batch input a copy, so a plan with no units keeps its pointers. A script reads stored paths only from the plan's `inputs` and `refs`. **D9:** S-12(b)'s rule for what the baseline supplies to a form that lacks a value, with the status derived once in `route_scorer_units`; the owner is carried with its emphasis, while the SLA and disposition are read without it; and the two "missing" causes. **D2:** "recorded as unverified" includes the stage-record warning `tag-source:no-architecture-file`. **Known limitations:** a drift form's derived status. The scorer's closed flag vocabulary in `contracts/module-signatures.md` gains `corrected:trust_level:trust-label`, `input:cvss_base:missing`, `input:review_date:missing` and `input:<field>:not-in-form` |
| 2026-11-23 | **Amendment (W3, from the P0 checkpoint, T061).** Not a numbered revision. **D3:** a prose line's first `~` is written `&#126;`, so prose can't open a code fence that hides §4 and §6 from the next run, and the readers' closed set grows to nine references (P0-1). Ruled at W3 from FX0's probe: the guard looks past any whitespace but a newline, for `#` too, and the tolerant reader's structure tests look past only spaces and tabs, so a Unicode space can't lead a fence or a heading past either. A value that a renderer takes from an input that isn't a part is refused with exit 2 if it holds a character in step 10's set, `_check_staged` adds a whole-file backstop that exits 4, and `tachi_parts.forbidden_character` is the one predicate (P0-4). **D8:** a fallback member's details come from its own result in either ID form, and an unnamed group routes its peers without `correlation-*` properties, warning `correlation-group-unnamed` (P0-3). **D9 and D10:** a legacy-carried row's tags and scored-on date are read whenever §6 records them, and D10's legacy list gains step 3a (P0-2). "Baseline-aware" means that a usable baseline `risk-scores.md` was read (P0-9). A copied peer's tags wait for the PM's ruling (P0-6). **Known limitations:** the architecture file isn't a digest-checked plan input. `contracts/module-signatures.md`, `contracts/part-files.md` and `contracts/sarif-result.md` follow, the last with `message.markdown` always written (P0-8). Then, from the PM's W3 rulings 1 and 2: **D9:** NEW and UPDATED peers take their primary's assessment and are scored with their own asset tags. A peer whose tags move its composite is flagged `divergent` from the run that scores it, and one whose primary's assessed score isn't known keeps the primary's values, flagged `unchecked` (P0-6). **D3:** NFR-1's field scope is the contract's, and the oracle gains a fifth class for P0-9's reading. **Known limitations:** a legacy-derived peer's next run, and the rules' taxonomy links. `contracts/module-signatures.md` gains `VectorCheck.assessed`, `peer_divergence`'s wider use and the controls `matrix_row`'s form, with `CF` out of the overwrite count. `contracts/sarif-result.md` gains the rules' `relationships`, the controls file's `maestro-layer` and "no other key is written". `contracts/part-files.md` points to the `matrix_row` form. Then, from the W3 sweep: **D7:** with no `--architecture-path`, `refs` holds no `architecture` on either command, and both agents read the run's snapshot (T038). **D3:** a reader that a renderer's checks or the next run rely on finds a section by its exact heading line outside code fences (T087's observation). **D4:** exit 2 names a forbidden character in an input, and step 5 reads each staged markdown back through the next run's reader, with no step-10 character in either file (FX0). **D2:** a controls finding whose Section 7 has no Status column is scanned fresh (T036). **Known limitations:** the extractors' substring search, and a `risk-scores.md` over the reader's cap. `contracts/cli.md` gains the controls plan's flags and W3's readings, `contracts/module-signatures.md` the `details` shape with `kind`, the fallback risk label and `match_heading`'s `outside_fences`, and `contracts/sarif-result.md` what the controls `markdown` holds. Then, from W3's rulings d (T056, T059, T053, FX0-3 and R3a): **D2:** the overwrite count is the stage record's `counts.cell_overwrites`, a base count with no flag. A checked §2 cell stays the agent's, flagged `input:<field>:sources-disagree`. A list of finding IDs names at most 10 (`PEER_CAP`), then a count of the rest. An evidence `file` that the resolver refuses at render time is flagged `input:evidence.file:unresolved` and left out of `relatedLocations`, never refused. **D3 and D4:** `forbidden_character` also returns a lone surrogate, and `plan` refuses one at plan time. **D7** points to D2's evidence ruling. **D8:** the details read `properties.severity` after `risk_level`, and the singular `logicalLocation` after the plural, and a `data-store` kind is written `data`. Both renderers use the one reader. The self-check's RESOLVED scan skips copied text, which settles P0-10. **Known limitations:** a flagged §2 cell shows the agent's text. `contracts/module-signatures.md` gains the controls renderer's closed flag vocabulary and these readings, `contracts/part-files.md` the count key and the evidence reading, and `contracts/sarif-result.md` the evidence and RESOLVED rules. Then, from W3's closing sweep: **D3:** the line-start guard rests on step 10, the intake and `_check_staged`'s backstop to keep every other line break out of a render, so it is no second line against a forged one (T064's Q1). T064 answers the planner's and the baseline cell's questions (Q3, Q4), and W4 rules on its answers with T146's fixes. D3, D4 and D7 wait for T146's fixes for SA-7, SA-5 and SA-11. **Known limitations:** link syntax, the declared-paths check's reach, unpinned parts, an input hashed and parsed from two reads, and unchecked evidence text (T064's SA-9, SA-14, SA-15, SA-6 and SA-16). `contracts/module-signatures.md` gains `tachi_parts`' controls item checks and `sarif_common`'s rule table, taxonomy names, driver version, copied-text list and evidence-URI guard. `contracts/part-files.md` points to the item checks, `contracts/sarif-result.md` names the shared rule table, and `sarif-identity-shared.md`'s three RESOLVED lines follow Q9's ruling. Then, from W4's fix lane (T146, 2026-11-24): **D6:** the dated note's completion rule is amended in place. The layer dispatches every wave that `plan` or the latest `reconcile` listed, and runs `reconcile` once, after every agent of those waves has reported completion, because a `reconcile` between waves spends a retry on every batch that hasn't been dispatched yet (T067b's H2). Both commands and the shared part-file contract carry the new words, and one pin covers all four texts. **D3:** step 10's set gains the Unicode tag block, U+E0000–U+E007F, and D16's hostile inputs name it (T064's SA-7). The shared contract's character list follows. Then, from W4's oracle triage (T066, 2026-11-24): **D2:** the MAESTRO layer's chain gains the finding's own row in a per-finding table, after Section 7's cell and before the component's Section 1 cell, because the v4.48.x threat models hold the layer only there (T066's U-1). `tachi_parsers.parse_finding_layers` is its one reader, for both renderers and the planner's controls unit row. **Known limitations:** a drift form's carried threat text is the baseline's short form (U-2). **D8:** the self-check's list gains D7's checks on both URIs, as written and percent-decoded once (T064's SA-11, landed by T146's FX-4). `contracts/module-signatures.md` gains `parse_finding_layers`, and its URI-guard bullet and `forbidden_character`'s list follow FX-4 and SA-7. `contracts/sarif-result.md` gains the controls layer's new step, the primary location's `region`, `kind` and zone, and the evidence message. `data-model.md`'s string rule gains the tag block. The other oracle groups are rulings already made, example problems or class wording for the PM, so they change nothing here. Then, from the PM's W4 oracle rulings (2026-11-24): **D3**'s copy of the oracle's classes gains, verbatim, class 4's added sources (R-A), class 6's two added fields (R-B) and the seventh to eleventh classes (R-C to R-G), with the example-defect table and the gating run, and the ninth class names the renderers' placeholders. **D8:** an ID that two groups list is reported, never silent. `parse_correlation_groups` returns `repeated`, and each renderer writes one Input Issues line per ID and warns `correlation-member-repeated`, so the run exits 5 (R-F, as T146's lane wrote it, with one change for an ID that isn't one of the run's open findings). **D2:** the per-finding tables are read in one pass by `parse_markdown_table`'s row rules, and a blank first row passes to the next step (T146's measurement). **Known limitations:** the PM accepts U-2's entry, whose upgrade is a filed T080 issue, and the SARIF fallback reports no repeated member. `contracts/module-signatures.md` gains `repeated` in the freeze and in the reader's shape, `parse_finding_layers`' one-pass reading, and the placeholders `Unspecified` and `No threat description.`, which `contracts/sarif-result.md`'s primary location and message point to. Then, from the PM's W4 re-run rulings (2026-11-24, from T066's re-run): **D3**'s copy of the oracle's classes gains, verbatim, the fifth class's widening (R-I) and the eighth class's `CF` cell (R-H), and the gating paragraph gains the re-run's readings. Then, from the architect's ruling on the re-run's open question and the PM's suggested fold A5 (2026-11-24): **D2:** `carried_forward` is accepted only for an UNCHANGED finding whose result the resolved baseline controls file holds (its persisted result in a 1.1 file, a §2 row in a 1.0 file), and a claim for any other finding is cleared through the existing `carried-forward-cleared` path. The fix is PR 1's, and T066's renders don't move. **D15:** the controls row no longer lists `CF` as added, because 1.0 has the column; 1.1 adds its rule, and the renderer fills it. The 1.1 controls template's `schema_version` row says the same. Then, from the PM's ruling R-J at T066's attribution pass (2026-11-24): **D3**'s gating paragraph gains, verbatim, the joint (5 and 7) composite and its test. Then, from the P1 checkpoint's ADR items (W6, 2026-11-24): **D2:** SARIF's `recommendation` and `effort-estimate` come from each finding's own §4 block by the shared rules, and D4's step 5 checks each against the validated part's body (P1-4). **D4:** step 5's standing rule: a from-disk check compares each written value with its source, never with a second read by the reader that produced it (P1-4). **D3:** ruling 4's quote is verbatim, and classes 1 to 3 are named (P1-7). **D7:** the `https%3A//` edge is accepted (P1 section 4). **Known limitations:** a malformed persisted controls item (SA-1's residual), and the declared-paths snapshot's growth (T067a's L9). Then, from the PM's W6 rulings (2026-11-24): **D3:** Section 7's readers, the reference set and the layer chain's Section 7 cell, read GFM's escaped pipe as a literal pipe, and the raw-pipe stop stays (P1-3, ruling Q1). **Known limitations:** the controls file's §3 lists only mapped controls (ruling Q3(b)). |
