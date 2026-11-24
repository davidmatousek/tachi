<!--
Binding release notes for #374 (PRD-374 ruling R-1; spec, "Release notes, per PR").
Each PR has one top-level section. When a PR's release publishes, the text of its section, from the line
after its heading to the next top-level heading, goes under release-please's version heading and above
its "Bug Fixes" list. PR 2 appends its own section below this one.
-->

# PR 1 (Tracks S and R), Refs #374

This release is the first of two fixes for #374 (large-architecture pipeline resilience), and it fixes #397's N14, N15 and N16. `/tachi.risk-score` and `/tachi.compensating-controls` now plan their work in batches, dispatch one typed agent per batch, resume from the files on disk, and stop with a named remedy when a batch can't finish. The agents supply only their judgment. Shipped, tested code computes every score and writes all four output files. `/tachi.threat-model` gets its new instruction text in this release and the checks behind it in the second #374 release. Item 5 says what stays fragile until then.

### Upgrading

1. **Re-install.** Update your tachi clone, re-run `<tachi-repo>/scripts/install.sh` from your project's root, and restart Claude Code. This release adds `scripts/tachi-stage.py`, two renderers and the helper modules they import, and each command stops with `TACHI ... NOT INSTALLED` when a file it needs is missing. Install only with `install.sh`. The agent copies under `adapters/claude-code/` are superseded, and copying them over `.claude/agents/tachi/` drops the shipped agents' tool limits (#427).
2. **Python 3.9 or later, as `python3`.** All three commands now need it, `/tachi.compensating-controls` included (item 2). The new scripts use only the standard library.
3. **Ignore `.tachi-build/`.** Add `**/.tachi-build/` to your `.gitignore` (item 4).
4. **Your architecture file's path.** If your architecture file isn't at `docs/security/architecture.md`, re-run `/tachi.threat-model` before you score, so that it records the file's path in `threats.md`, or pass `--architecture-path <path>` to both commands. Your alerts then re-key only once (item 1).
5. **Code Scanning.** The first upload re-keys the scorer and controls alerts once, so re-apply their dismissals. The developer guide's snippets now upload both files, each under its own category (item 1).

### 1. SARIF alerts from the scorer and controls

- **One re-key.** The first upload of `risk-scores.sarif` and `compensating-controls.sarif` after upgrading closes every `tachi-risk-scorer` and `tachi-control-analyzer` alert once and opens one alert per open finding. Dismissals don't carry over, so re-apply them once. Before this release, these alerts could already close and reopen on every run.
- **Stable from then on.** Each result now carries tachi's own `primaryLocationLineHash`, computed from the finding's ID, and points at your architecture file by its repo-relative path. A regroup, a new primary, a re-score, a new output directory or a later upgrade doesn't re-key an alert.
- **What still re-keys.** A run with no baseline renumbers its findings, so its alerts re-key. Moving or renaming the architecture file re-keys every alert once. Keep successive runs in the same output folder (by default `docs/security/`), so that each `/tachi.threat-model` run takes the previous one as its baseline and keeps its finding IDs.
- **Alert count.** Each file holds one result, and so one alert, per open finding. The scorer's count rises from primaries plus uncorrelated findings to every open finding. The controls count stays the same, and a correlated finding is no longer listed twice. RESOLVED findings appear in neither file.
- **Tool names and categories.** The tool names are unchanged: `tachi-risk-scorer` and `tachi-control-analyzer`. No file sets `automationDetails`, so the upload's `category` decides. The developer guide's snippets upload each file from the run's timestamped directory, with `category: risk-score` and `category: compensating-controls`. If you already upload under categories of your own, keep them. A new category re-keys too, and a category you stop uploading stays in Code Scanning until you delete it. A repository with several architecture files needs its own categories for each system.
- **The alerts' location.** Every result points at one architecture file: the `--architecture-path` flag's path, else the `**Architecture source**` line that `/tachi.threat-model` now writes into `threats.md`, else `docs/security/architecture.md`. Files written before this release have no such line (item 2). If your architecture file is elsewhere and you neither re-run `/tachi.threat-model` nor pass the flag, the first upload keys the alerts to the default path. They then re-key once more when a later run records the real one.
- **Reused IDs, until the second #374 release.** `/tachi.threat-model` can still give a NEW finding the ID of a finding that was resolved. Code Scanning then attaches the new finding to the old alert, dismissal included. The scorer and controls stages flag such a finding `reused-id` when the baseline `risk-scores.md` lists its ID. Look for `reused-id` in the `Flags` column of `risk-scores.md`, and re-check any dismissed alert for that finding. The second release stops IDs from being reissued.
- **Correlation.** Peers are results of their own, and a result's group is in its `correlation-group`, `correlation-role` and `correlation-primary` properties. The message of a correlated result ends with one sentence that names its group and its primary, or on a primary its peers (up to 10, then a count), such as `Correlated in CG-3; primary S-1.` on a peer. `partialFingerprints` holds only the hash and `findingId/v1`. No `relatedLocations` entry names a finding: the controls file's entries are code evidence only. If you read peers from `relatedLocations`, or the group from `partialFingerprints`, read the properties instead.
- **`threats.sarif`** doesn't change in this release, and its alerts still churn (item 5).
- **How this was checked.** No Code Scanning scratch repository was used. The alert behavior above is modeled from GitHub's documentation of how Code Scanning matches alerts, and tested offline.

### 2. Runs that stop

Where a run used to work around a problem, it now stops and says what failed and what to do. A failed scorer or controls run prints:

```text
TACHI <STAGE> FAILED: <reason>
Batch <id>: <finding IDs>   (or: Agent: <type>)
Remedy: <what to do>
Kept for diagnosis: <plan directory>
```

It also moves any output it changed into the plan's `failed/` folder and puts the previous run's files back. A failed file never sits under an output's name, and no later command reads it as input or as a baseline.

The new stops:

- **An instruction change: no stand-ins, no code hand-backs, shipped scripts only.** The agent and command instructions now forbid dispatching a generic agent in place of a typed tachi agent, handing back code for the caller to run, and running any script that tachi doesn't ship. In `/tachi.risk-score` and `/tachi.compensating-controls`, a typed agent that can't be spawned ends the run (`agent-not-spawned`), and no substitute runs. Re-run `install.sh`. In `/tachi.threat-model`, the orchestrator's instructions now say to stop the same way, and that stage's dispatch records and checks ship in the second #374 release (item 5).
- **A missing file, or Python below 3.9.** At Step 1, each of the three commands now checks that its agent and scripts are installed and that `python3` is 3.9 or later. It stops with `TACHI ... NOT INSTALLED` and the missing file, or with `PYTHON 3.9+ NOT FOUND — tachi renders this stage with Python 3.9 or later (found: <version, or none>); install it and re-run`. A Python 3.9+ renderer now writes the scorer and controls outputs, so `/tachi.compensating-controls` needs `python3` for the first time.
- **An unreadable Section 7.** Both stages read the findings from Section 7 of `threats.md`, under a `## 7.` or `## Section 7:` heading. Section 7 can be a table with a `Finding ID` column, or the numbered list of bolded IDs that some tachi samples show. Any other Section 7, whether missing, empty or malformed, stops the run before any agent is dispatched (exit 2). The error names the file, the section, the expected form and the remedy: regenerate `threats.md` with `/tachi.threat-model`, or correct the section to one of the two forms. When a stage reads `threats.sarif` or `risk-scores.sarif` because the markdown file is missing, an empty result set stops it the same way.
- **A raw `|` in a Section 7 cell.** A row in `threats.md` Section 7 with more cells than its header, which a raw `|` in a cell produces, stops `/tachi.risk-score` and `/tachi.compensating-controls` before any agent runs (exit 2). Write the pipe as `&#124;`. Both stages also read GitHub's escaped `\|` as a pipe.
- **A forbidden character in an input.** A stage stops (exit 2) when a value it takes from its inputs holds a control character, a bidirectional-text control, a Unicode line or paragraph separator, or a Unicode tag character. Remove the character and re-run.
- **Inputs that change during a run.** Each batch plan records the digests of its inputs. If `threats.md`, the scored input or a batch input changes while the stage runs, the next step refuses the plan (exit 2). The run fails, and your earlier outputs stay as they were. Re-run the command.
- **A batch that can't finish.** A batch whose agent leaves no valid part file is retried, at most twice per batch and within a retry budget per stage. A retry splits the batch in half when the part is missing, unreadable or reported too large. When the retries run out, the run fails with `unrecoverable-batch` and names the batch and its findings. Remedy: re-run, and report the kept plan directory if the same batch fails again. Two causes are known. Target code that the controls agent quotes as evidence can hold a control or bidirectional-text character, such as a Trojan Source line, and every attempt quotes it again. Or a row of the baseline controls file's `### Assessment Inputs` was edited into a form that no longer validates: restore or delete that row, or run without the baseline (#445).
- **A failed completeness check.** Before it replaces any output, the renderer reads back what it wrote. It checks one row and one SARIF result per open finding, and that the `.md` and the `.sarif` agree. A failure ends the run with `check-failed`, and your earlier outputs stay as they were. One known case: a `risk-scores.md` above 16 MiB, about 4,000 findings, can't be read back, so its render fails.
- **A path that holds a single quote.** Each command passes paths to its scripts inside single quotes, so a path that holds `'` stops the command. Rename the folder or file.

**Warnings on the first run after upgrading.** These runs complete. The report ends with the warning, and the stage exits 5 (done, with warnings).

- **No architecture-source line.** Every `threats.md` written before this release lacks the `**Architecture source**` line. So the first scorer and controls runs after upgrading warn `architecture-path:body-line:absent`, use `docs/security/architecture.md` (item 1) and exit 5, even when your architecture file is at that path. The warning stops once `/tachi.threat-model` writes the line, or when you pass `--architecture-path`.
- **No Status column on a first run.** On a first run, `/tachi.threat-model` can write Section 7 without its Status column. Both stages then treat every finding as NEW, which is right when there is no baseline, but they flag each one `input:delta_status:not-in-form` and finish with warnings (exit 5). No score is affected. The flag goes away once Section 7 has the column, which a baseline-aware `/tachi.threat-model` run writes. The fix is #436.

### 3. Scores

- **Carried scores are recomputed.** A finding carried over from the baseline keeps its inputs as stored: its CVSS vector, its sub-scores, its reachability inputs and its human governance fields. Its CVSS score, composite, band, SLA, disposition and review date are recomputed from them. Each change is flagged with its cause: in the new `Flags` column of `risk-scores.md`, in its Section 6 (Score Integrity) and in the SARIF `score-flags` property. Earlier releases copied these values forward, so one run's slip became permanent.
- **Reading the flags.**
  - `corrected:<field>:<cause>`: the stored value didn't follow from its inputs, and the renderer replaced it. The causes include `vector`, `arithmetic`, `band-mapping` and `follows-band`, and `rounding` when a rounding difference moves the band.
  - `unverifiable`: the finding has no CVSS vector, so its stored score is kept and `cvss_vector` is null. It changes when the finding is next re-assessed.
  - `unchecked`: the check depends on a scoring rule that tachi hasn't settled yet, such as a compound trust label or another category's CVSS bound. The stored value is kept, and it isn't reported as wrong.
  - A difference that comes only from rounding, and leaves the band as it was, is normalized and counted in Section 6, not flagged.
  - The other flags are `retagged`, `divergent` and `override` (below), `resolved` (item 4), `reused-id` (item 1), and `input:<field>:<cause>` for a problem in an input: two sources that disagree, a reachability value outside its range, a value the input's form lacks, or the narrative fallback.
- **Which baseline.** Both stages now inherit from the run that `threats.md`'s `baseline.source` names. `--baseline <run-dir>` names another run and takes precedence. The controls stage finds that `threats.md` through `risk-scores.md`. If the named baseline can't be used, because it is free text, a path that doesn't resolve or a missing file, the stage scores every finding fresh and warns `baseline-unresolved`. A baseline file that is present but unreadable counts as missing: the stage warns `baseline-unreadable` and says that its owners, SLAs and dispositions weren't carried. A NEW finding is held to its category's ±1.0 CVSS bound only when the run read a usable baseline `risk-scores.md`.
- **Review dates after a correction.** A corrected band keeps the finding's original scoring date: its review date becomes that date plus the corrected SLA. So on the first run after upgrading, some findings can become due, or overdue, at once. Their `corrected` flag tells them apart from findings that slipped.
- **Human values.** The owner is always carried. An Accept or Transfer disposition, or an SLA or disposition that differs from the stored band's default, is carried verbatim and flagged `override`, and an SLA override keeps its review date.
- **Asset tags now reach carried findings.** Earlier releases skipped the asset-modifier step for UNCHANGED findings. The renderer now recomputes each carried finding's CVSS score with this run's tags, so on the first run after upgrading, carried findings on tagged components can score higher, and some move up a band. Such a change is flagged `retagged`, never `corrected`. When tags raise a band, the review date becomes this run's date plus the new SLA, unless the stored review date is earlier, so tagging never makes a finding overdue on the day. When removing a tag lowers a band, the original scoring date stays, so a deadline that was already missed stays missed. A tag never lowers a score: a finding assessed above the 9.2 modifier ceiling keeps its score.
- **Correlated findings.** A correlated finding is now scored with its own component's asset tags. It takes its group primary's assessment, so a group whose members share tags still shows one score; a member whose own tags change its score shows that score and is flagged `divergent`. An UNCHANGED member keeps its own score, flagged `divergent` when it differs from its primary's, and a regroup alone changes no carried score.
- **The Source column.** `inherited` now means that a finding's scoring inputs came from the baseline, so a NEW or UPDATED peer of a carried primary shows `inherited` too. The summary line reads `<n> findings scored from baseline inputs, <m> scored fresh`.

### 4. Rendered files

- **The renderers write the files.** Shipped scripts, `scripts/render-risk-scores.py` and `scripts/render-compensating-controls.py`, now write `risk-scores.md`, `risk-scores.sarif`, `compensating-controls.md` and `compensating-controls.sarif`, and no agent writes them. Each agent writes only its judgment, as one JSON part file per batch. The renderer computes every score, band, total and identity, and checks both files before it replaces anything. Each `.md` ends with a `tachi-provenance` comment, and each SARIF run carries a `tachi_provenance` property: the renderer, tachi's version and an input digest.
- **Controls Sections 2 and 4 are this release's exception.** The controls agent still writes each Section 2 row and each Section 4 recommendation, inside its part file, against the one Section 2 schema. The renderer fills every score, band and `CF` cell, and checks four agent-written cells, Control Status, Control Category, Component and MAESTRO Layer, against the structured values. A mismatch is flagged `input:<field>:sources-disagree`. The SARIF file and the totals follow the structured values, but anything that reads Section 2, the PDF report and the infographics included, shows the agent's text. Rendering both sections is #432.
- **One Section 2 schema.** All four band tables of `compensating-controls.md` use one schema, which adds the MAESTRO Layer and Control Category columns.
- **The `CF` column.** The controls file's `CF` column, which 1.0 already has, is now filled by the renderer from each finding's carried-forward result. So `carry_forward_count` always equals the rows marked `CF`, and on an incremental run each carried row reads `CF`, including where an earlier output left the column `—`. A row reads `CF` only when the baseline controls file holds that finding's result. Any other carry-forward claim is cleared, listed under Input Issues and warned `carried-forward-cleared`.
- **Controls Section 3.** Section 3 of `compensating-controls.md` now lists each detected control that at least one scored finding maps to. A control that the scan found but that maps to no finding, which some earlier outputs listed, is no longer written. No score changes, because such a control never lowered a finding's residual risk. Whether to list such controls is #435.
- **RESOLVED findings.** `risk-scores.md` lists them in a new `## 2a. Resolved Findings` table after Section 2. Each row keeps its last-known values verbatim, reads `RESOLVED` and is flagged `resolved`. These rows are never recomputed or put on the SLA clock. The Executive Summary counts them on a line of their own, outside the severity distribution, and no SARIF file carries them.
- **Schema 1.1, additive.** Both files move from schema 1.0 to 1.1, and every 1.0 section stays. `risk-scores.md` gains Section 2a, the `Flags` column, Section 3's MAESTRO Layer, Correlation Group and Integrity lines and its weighted table, and Section 6 (Score Integrity: the integrity summary, the flags, input issues, and the scoring inputs that the next run reads back). `compensating-controls.md` gains the two Section 2 columns, one Section 4 block for each finding that has a recommendation, and Section 7 (Analysis Integrity: the integrity summary, the flags, input issues and the assessment inputs).
- **The Executive Summary.** The Executive Summary of `risk-scores.md` now opens with one templated sentence that the renderer fills from its own counts: `<N> open findings were scored on <date>: <c> Critical, <h> High, <m> Medium and <l> Low.`
- **Working files.** Each run's output directory now holds `.tachi-build/`: the batch plans and inputs, the agents' part files, the staged outputs, and one stage record per stage with its counts, batches, retries and warnings. Its files contain absolute local paths, so add `**/.tachi-build/` to your `.gitignore`. A stage also warns when a file it doesn't declare appears in the output directory during the run.
- **SARIF properties.** Each SARIF result now carries exactly the properties its contract names. Keys that some earlier outputs added on their own, such as result-level `tags`, `owasp-reference` and `source-attribution`, are no longer written; their information is in the contract properties or in `threats.md` and `threats.sarif`.
- **Fixed SARIF values.** Each SARIF file's rule descriptions, tags and taxonomy links, its taxonomies, its schema link and its tool version are now fixed by tachi, the same in every run of a release, where earlier outputs varied between runs. The tool version is tachi's release version, and `informationUri` is tachi's repository rather than a placeholder (#412; `threats.sarif` follows in the second release). The taxon names stay as they were, so ASI01 still reads `Agent Autonomy Abuse` in these files, where tachi's OWASP catalog says `Agent Goal Hijack`. The rules' taxonomy links name `OWASP` or `CWE`, which the run's taxonomies don't list in full, so a consumer that resolves a link inside the file can find nothing. GitHub Code Scanning reads neither field. Aligning both is #457.
- **SARIF locations.** Each SARIF result's location now follows fixed rules: its region starts at line 1, its kind is the component's Section 1 type (a data store is `data`), and its zone is written as Section 2 writes it. Each evidence location's message is tachi's fixed sentence, `Control evidence: <category> detected in <file>`.
- **Older `threats.md` files.** On an older `threats.md`, the renderers take some identity values only from what the file records. A finding with no MAESTRO layer in Section 7, in its own per-finding table row or in its component's Section 1 row reads `Unclassified`, the contract's own default. Where Section 7 is a numbered list, a carried finding's threat text is the short form that its baseline row holds, and a finding that no baseline row supplies takes the renderer's placeholders for its component and threat (`Unspecified` and `No threat description.`), flagged `input:<field>:not-in-form`. Regenerating `threats.md` with `/tachi.threat-model` restores each value. Follow-ups: #437 and #438.
- **Character references.** The renderers write `&`, `<`, `>`, `|`, a backtick and a few other characters in cells and prose as character references. tachi's readers decode exactly that set: `&amp;`, `&lt;`, `&gt;`, `&#124;`, `&#96;`, `&#123;`, `&#10;`, `&#35;` and `&#126;`. So any of those written literally in your files, such as `&amp;` in `threats.md`, now reads as the character it stands for. That holds in the scorer and controls stages, the PDF report and the infographics.

### 5. What stays fragile until the second #374 release

- **Large threat models and the report can still overflow.** In `/tachi.threat-model`, the model still writes `threats.md`, `threats.sarif` and `threat-report.md` itself, so a large architecture can still exceed what one response holds.
- **A large threat-model run may now stop, or come out incomplete.** The new instructions forbid generic stand-ins for typed agents, but Phase 2's re-dispatch of an agent that overflowed ships only in the second release. So a large threat-model run that used to finish by improvising may now stop, or come out incomplete. If Phase 2 can't be held at that scale, moving its dispatch into the command is a possible escalation, which needs a scope decision first (#430).
- **The attack-chain phase can still be skipped without a record.**
- **`threats.sarif` alerts still churn.** Its identity and its upload line change together in the second release, so its alerts re-key only once.

### Narrative fallback

The agents' rationale prose states a score, count, band, percentage or date only through slots, placeholders that the renderer fills, so the prose can't contradict the tables. A rationale field that breaks this rule, with a digit outside a slot or a slot that is malformed or doesn't resolve, doesn't fail the run. The renderer writes that field's fixed sentence instead, flags the finding `input:<field>:narrative-fallback`, and counts it in the stage record. A prose field longer than its limit is cut at the limit, flagged `input:<field>:truncated` and counted. A cut that lands inside a slot also gives the field its fixed sentence. Neither ever drops a row or rejects a part. The flags appear in Section 6 of `risk-scores.md` and Section 7 of `compensating-controls.md`, and in each SARIF result's `score-flags` or `integrity-flags` property.

`<field>` is the part's field name: `rationale.<dimension>`, `metric_rationale.<metric>` and `subscore_rationale.<sub-score>` for the scorer, and `evidence.assessment.<dimension>`, `evidence.snippet`, `evidence.summary`, `matrix_row` and `recommendation_body` for controls. The limits, in characters: 400 for the four dimension rationales; 160 for each metric, sub-score and assessment rationale and for an evidence summary; 600 for an evidence snippet, after it is cut to 5 lines; 1,200 for a controls matrix row; and 2,000 for a recommendation.

In this release's live runs, the highest fallback rate was 1.3% of a stage's narrative fields (1 of 80 controls fields, in one run), so no stage needed a follow-up.

<details>
<summary>The 24 fixed sentences</summary>

| Field | Fixed sentence |
|---|---|
| `rationale.cvss` | No CVSS rationale is shown because the text the agent wrote broke the narrative rules. |
| `rationale.exploitability` | No exploitability rationale is shown because the text the agent wrote broke the narrative rules. |
| `rationale.scalability` | No scalability rationale is shown because the text the agent wrote broke the narrative rules. |
| `rationale.reachability` | No reachability rationale is shown because the text the agent wrote broke the narrative rules. |
| `metric_rationale.AV` | No attack vector metric rationale is shown because the text the agent wrote broke the narrative rules. |
| `metric_rationale.AC` | No attack complexity metric rationale is shown because the text the agent wrote broke the narrative rules. |
| `metric_rationale.PR` | No privileges required metric rationale is shown because the text the agent wrote broke the narrative rules. |
| `metric_rationale.UI` | No user interaction metric rationale is shown because the text the agent wrote broke the narrative rules. |
| `metric_rationale.S` | No scope metric rationale is shown because the text the agent wrote broke the narrative rules. |
| `metric_rationale.C` | No confidentiality impact metric rationale is shown because the text the agent wrote broke the narrative rules. |
| `metric_rationale.I` | No integrity impact metric rationale is shown because the text the agent wrote broke the narrative rules. |
| `metric_rationale.A` | No availability impact metric rationale is shown because the text the agent wrote broke the narrative rules. |
| `subscore_rationale.known_techniques` | No known techniques sub-score rationale is shown because the text the agent wrote broke the narrative rules. |
| `subscore_rationale.attack_complexity` | No attack complexity sub-score rationale is shown because the text the agent wrote broke the narrative rules. |
| `subscore_rationale.tooling_availability` | No tooling availability sub-score rationale is shown because the text the agent wrote broke the narrative rules. |
| `subscore_rationale.skill_level` | No skill level sub-score rationale is shown because the text the agent wrote broke the narrative rules. |
| `subscore_rationale.scriptability` | No scriptability sub-score rationale is shown because the text the agent wrote broke the narrative rules. |
| `subscore_rationale.target_scope` | No target scope sub-score rationale is shown because the text the agent wrote broke the narrative rules. |
| `subscore_rationale.resource_requirements` | No resource requirements sub-score rationale is shown because the text the agent wrote broke the narrative rules. |
| `subscore_rationale.detection_difficulty` | No detection difficulty sub-score rationale is shown because the text the agent wrote broke the narrative rules. |
| `evidence.assessment.coverage` | No coverage assessment rationale is shown because the text the agent wrote broke the narrative rules. |
| `evidence.assessment.configuration` | No configuration assessment rationale is shown because the text the agent wrote broke the narrative rules. |
| `evidence.assessment.currency` | No currency assessment rationale is shown because the text the agent wrote broke the narrative rules. |
| `evidence.assessment.completeness` | No completeness assessment rationale is shown because the text the agent wrote broke the narrative rules. |

</details>

### Cost

**Small runs use fewer output tokens.** On a small shipped example (11 findings, so one batch in each stage), at the default effort, each stage used fewer output tokens than v4.48.4 on the same input:

| Stage | This release | v4.48.4 | Change |
|---|---|---|---|
| `/tachi.risk-score` | 9,493 | 27,049 | -17,556 (-64.9%) |
| `/tachi.compensating-controls` | 10,207 | 35,200 | -24,993 (-71.0%) |

Output tokens are what Claude Code reports for the whole stage: the command's own turns and every agent's, thinking included. Each figure is one run, so the direction is firm and the size is not. Most of the saving is in the agents, which now write one compact part file instead of the whole output.

This is the release's only cost claim, and it holds for that small example at the default effort. "The default effort" here means a session started with `--effort medium`. Claude Code's own default can now start higher, and no run sampled it. On the large synthetic fixture (408 open findings) there is no like-for-like figure, because v4.48.4's scorer didn't finish there within its contract.

**What max effort costs.** On the large fixture, one run per cell:

| Stage | Medium | Max (main session and agents) |
|---|---|---|
| `/tachi.risk-score` | 233,319 tokens, 2 min 44 s | 4,295,809 tokens, 46 min 24 s |
| `/tachi.compensating-controls` | 357,397 tokens, 4 min 38 s | 4,110,230 tokens, 43 min 14 s |

About 90% of the scorer's tokens at max were thinking. Nine of its 26 agents each had one response stop at the 128,000-token cap while thinking. Claude Code resumed each agent in the same run, and every part was valid. But tachi's stage record doesn't show such stops, and the largest writes left under 1,000 tokens of margin (#431).

**Effort and the response cap.**

- **Setting max for the agents.** In the Claude Code version these runs used (2.1.331), `claude --effort max` raised only the main session, and the agents stayed at medium. To run tachi's agents at max too, also set `CLAUDE_CODE_EFFORT_LEVEL=max` when you start Claude Code.
- **The response cap depends on your environment.** These runs had a 128,000-token cap per response, and earlier large runs stopped at 64,000. tachi sizes each batch so that its largest write fits a 32,000-token response, the smallest documented default, so batching doesn't depend on your cap. At max effort, though, thinking counts against the same cap.

### Known limitations

- **Reference reads at the default effort.** Scorer agents at the default effort can skip reference files that their instructions require: on the large fixture, 9 of 26 skipped at least one, and one read none. None of the checks this release claims depends on those reads, but such an agent judges its vectors and sub-scores without those rules (#433).
- **Architecture files not named `architecture.md`.** `/tachi.threat-model` names its snapshot of the architecture file after the source file, while the populator and the scorer and controls agents look for `architecture.md` beside `threats.md`. With another name, `threats.md` gets no Affected Assets block, and the agents judge reachability and map components without the architecture unless you pass `--architecture-path` (#428). The alerts' location and the renderers' asset tags are unaffected.
- **Generic agents under the isolated-operation profile.** The instruction text is what keeps generic stand-ins out. The published session profile doesn't deny the `general-purpose` agent type yet (#429).
- **Prose carried from an older baseline.** A `risk-scores.md` written before this release stores its rationale without slots, so the next run carries that prose as quoted text. It can state a number that the renderer has since corrected, and the finding's flags show the correction.
- **A Section 7 without a Status column.** A finding that the baseline lists is then carried as UNCHANGED. So if `/tachi.threat-model` gave a new finding the ID of a baseline finding, the new finding inherits that finding's inputs. Its `input:delta_status:not-in-form` flag is the signal until the second release stops IDs from being reissued.

### What this release checked, and what it doesn't claim

**Checked:**

- **Large inputs, live.** On a synthetic architecture with 25 components, 408 open findings and 6 resolved ones, both stages ran at the default effort and at max, in 26 scorer and 38 controls batches. Each run wrote complete files: one row and one SARIF result per open finding, the `.md` and the `.sarif` in agreement, every total equal to the sum of its rows, and no file assembled by hand. In the last run at each effort, no agent returned code to its caller, wrote a program file or stood in for another agent type, and the commands ran only the shipped scripts they name.
- **Offline, on synthetic variants.** Seeded score errors are corrected and flagged, and documented exceptions aren't. Alert keys hold across a regroup and an unchanged re-run. A missing, stale or invalid part is never counted: its batch is retried, and when the retries run out the run fails with its earlier outputs restored.
- **The isolated-operation runbook.** One small run of all three commands under the published session profile, on macOS, finished with no permission prompt or denial and wrote only where the runbook says. The runbook's "Last validated" line names that run. It didn't cover `/tachi.infographic`, `/tachi.security-report`, Linux or WSL2.

**Not claimed:**

- That agents read the reference files their instructions require, or read only the files their instructions list, at any effort.
- That `/tachi.threat-model` or the report runs on its contract. That stage's checks ship in the second release, and this release's small smoke run still showed the threat-model stage running inline code.
- That a run scores like v4.48.4, or like another run. The agents still judge each vector and sub-score, and single runs on the same input gave different band counts.
- That the controls stage finds the same controls, or assigns the same statuses, as v4.48.4.
- That tachi's own retry path works in a live run. Every live batch finished at its first attempt, so the retry and failure paths are tested offline only.
- A fully rendered controls file (item 4), or any change to `threats.sarif`.
