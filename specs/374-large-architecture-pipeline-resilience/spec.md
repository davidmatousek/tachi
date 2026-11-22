---
prd_reference: docs/product/02_PRD/374-large-architecture-pipeline-resilience-2026-11-21.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-11-22
    status: APPROVED_WITH_CONCERNS
    notes: "Traces 1:1 to PRD v1.3: every PRD FR, D-1 to D-7 and R-1 to R-34 is carried, and S-5's PR 1 claims and non-claims match PRD §10. No spec ruling adds scope outside G1 to G5. S-3(d), (f) and (g) were AMENDED and are folded verbatim: contiguous runs and tails fold, converging chains stay, and the candidate, consolidated and surfaced counts are defined; one surfaced chain per terminal finding, each with its convergence count; up to 100 compact rows plus a count, N is the consolidated count, and the outcome check reconciles the file to N. S-2, S-3(b) and S-3(c) were ACCEPTED under R-21. 13 findings (2 HIGH, 5 MEDIUM, 6 LOW); findings 1 to 12 were FOLDED on 2026-11-22. HIGH 1: tachi's shipped drift forms are read, and anything else stops before dispatch (S-12). HIGH 2: FR-K4.1b reconciles to S-3(g). MEDIUM 3 to 7: the carrier FR-E.18, per-PR release notes, R-27 per PR, NFR-10's expected-name check, and S-13 never stopping. Finding 13 goes to the plan (P-11). Conditions: unpriced additions count toward each PR's TW-0, and a PR 1 projection above 9.0 days returns to the PM; any fold beyond the stated text returns to the PM. Full review: .aod/results/product-manager-374-spec.md"
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: Large-Architecture Pipeline Resilience

**Feature Branch**: `374-large-architecture-pipeline-resilience`
**Created**: 2026-11-22
**Status**: Draft
**Input**: Bundle PRD `docs/product/02_PRD/374-large-architecture-pipeline-resilience-2026-11-21.md` (v1.3, Approved; PM ⚠, Architect ⚠, Team-Lead ⚠). Lead issue **#374** carries K4–K8, and **#397** folds in N4, N12, N14, N15 and N16. Under ruling R-34 the bundle ships as two `fix(374)` patch PRs: **PR 1 (Track R)** first, then **PR 2 (Track O)**, based on `main`. Research: [research.md](research.md). Estimate and trip-wires: [feasibility-check.md](feasibility-check.md).

> **Why (PRD §1).** Two stock runs on large architectures failed silently: outputs overflowed one response, and agents left their contracts to finish. tachi's place as a scanning column rests on outputs that are complete, computed correctly and stable from run to run, because its users can't spot a wrong composite or an improvised agent.
>
> **Bundle spec.** This spec refines PRD-374 into testable requirements. It keeps the PRD's IDs (`FR-K4.1`, `FR-N14.2` and so on) for 1:1 traceability. PRD decisions D-1 to D-7 and rulings R-1 to R-34 bind it. Where this spec and PRD §10 disagree about the split between the two PRs, §10 governs.
>
> The spec adds four things:
> - **Spec rulings S-1 to S-16** (§ Rulings). They answer the PRD's three open questions (OQ-5, the batching thresholds; OQ-6, the chain rules; OQ-7, the fixture) and absorb what research found. Three of them change what users see, and the PM amended them at the spec review (§ PM rulings from the spec review).
> - **A track tag** on every story, requirement and criterion:
>   - **S** for the cut line, which ships in PR 1;
>   - **R** for Track R (PR 1);
>   - **O** for Track O (PR 2).
>
>   PR 1 rests only on S and R.
> - **The plan-stage inputs.** ADR-050's sixteen items, each with its track, are registered as plan inputs, not as ambiguities.
> - **The consequence scope**: the consumers of every surface the bundle changes (KB Entries 15 and 16).
>
> **Research changed or sharpened six premises** (research.md, "PRD corrections"):
> - **The upload action's fallback hash.** When a result has no `primaryLocationLineHash`, GitHub's upload action computes one from the architecture file's text at the result's line. Today's scorer and controls alerts are therefore keyed by a line of the user's architecture file, so every result must carry tachi's own hash (S-6).
> - **Baseline correlation.** Phase 3 uses today's SARIF hash recipe as its secondary match key. The new recipe must not change how findings match across runs (S-7).
> - **Dispatch limits.** By default, Claude Code runs at most 20 subagents at once and nests them at most three layers below the main session. What a caller receives when a subagent stops on `max_tokens` isn't documented, so the overflow detector is spiked before it is built (S-8, S-9).
> - **The output budget.** Thinking tokens count against the per-response cap, and the documented default cap can be as low as 32,000 tokens. The batching thresholds are therefore set by an output budget (S-1).
> - **Runtime.** The new scripts must run on Python 3.9, and a lazily imported PyYAML would pass the import gate unnoticed (S-11).
> - **The tree manifest.** Only the report agent reads `attack-trees/.manifest.json`; the PDF reads the tree files. This corrects an aside in D-3, and the merged manifest stays for the report agent.

### Terminology

| Term | Meaning |
|---|---|
| **Track S, R, O** | **S**, the cut line: ADR-050, the shared references, N4's and N14's contract text, the renderer core and the fixture, committed by the end of W1 with both CI legs green. **R**, Track R: the renderer, the scorer and controls contracts, and the K8 parsers. **O**, Track O: the orchestrator, the report, the chain script, the checks and the K4.1 readers. PR 1 = S + R; PR 2 = O |
| **Reference finding set** | The findings in `threats.md` Section 7, read once by shared code, where every finding appears exactly once (D-4). Every parity check compares against it. The reader accepts the table form and the drift forms that tachi's shipped samples show (S-12). Any other unreadable Section 7 ends the run before any agent is dispatched, and an empty extraction is an error, never a pass (KB 22) |
| **Open, RESOLVED** | An open finding is in Section 7, with status NEW, UPDATED or UNCHANGED. A RESOLVED finding is in Section 4c |
| **Carried finding** | An UNCHANGED or UPDATED finding that comes from the baseline run |
| **Inputs, derived fields** | A carried finding's **inputs** are the most granular values its baseline stores: the vector, the dimension sub-scores, the reachability inputs and the human governance fields. Its **derived fields** are the composite, the band, and the SLA, disposition and review date that follow from the band (D-6(b), R-26) |
| **Part file** | A bounded JSON file that an agent writes for one batch: structured judgment plus the prose fragments for narrative sections. It carries its plan ID and batch ID, and it is untrusted input (NFR-10) |
| **Batch plan** | The shipped planner's output: a fresh plan ID, the digests of its inputs, and the batches, each with its list of finding IDs (FR-E.3) |
| **Batched path** | A stage path on which the planner splits the work into two or more batches |
| **Renderer** | Shipped, tested, stdlib-only code that owns a whole output file and computes D-2's right-hand column |
| **Dispatch record** | One file per Phase 2 dispatch. SV-2b is carved at the plan stage (ADR-050 D1), so it is a manifest: the agent type, its scope, the count and the provisional IDs, possibly none (FR-N4.2, R-8) |
| **Brief** | The scope file for one dispatch, under `.tachi-build/briefs/`. It holds only the brief template's closed set of fields (FR-N4.3) |
| **ID map** | Phase 3's map from each final finding ID to its source record, and from each record finding to its disposition (FR-N4.2, FR-N4.6) |
| **Provenance entry** | One of three kinds per finding: a dispatch record, a baseline carry-forward reference, or a named deterministic rule (FR-N4.5) |
| **Outcome record** | Phase 3.5's line in `threats.md`: `chains written (N)`, `0 chains passed filter (<reason>)` or `skipped (<reason>)`. In `chains written (N)`, N is the consolidated count, and the record also carries the candidate and surfaced counts (FR-K4.1; S-3(d), (g)) |
| **Stage record** | One small JSON file per stage: counts, batches, overflow events and retries (NFR-5) |
| **Matching key** | GitHub's alert key: the tool and upload category, the `ruleId`, `partialFingerprints.primaryLocationLineHash` and `artifactLocation.uri` (D-5) |
| **Re-key event** | A release after which some alerts close and reopen once. Under R-34 there are at most two, at most one per file |
| **Flags** | **Corrected**, with its cause; **unverifiable** (no vector, R-7); **unchecked** (an N17 ambiguity, R-10); **divergent** (an UNCHANGED peer whose score differs from its primary's, R-4); **override** (a human governance value, R-31); **resolved** (a RESOLVED row in `risk-scores.md`, R-30); **retagged** (a value the asset tags alone moved: the band, or a value on the way to it such as `cvss_base` or `composite_score`, even when the band holds; never `corrected`, ruling A); **reused-id** (a NEW finding whose ID the baseline used, ruling B); **input** (a kept input with a problem, such as two sources that disagree or a reachability outside its range; a narrative field replaced by its fixed sentence, PM plan-review finding 1; or a prose field cut at its length limit, Architect re-review RR2). A rounding-only difference is **normalized** and counted, not flagged (R-11) |
| **Adopter default effort** | A session launched with no effort override (R-18) |

---

## User Scenarios & Testing *(mandatory)*

Each story carries its PM priority (R-12). The stories are grouped by the stage they cover, not ordered by priority, and each one can be tested on its own. PR 1 claims US-1a, US-3, US-5 and US-6a. PR 2 claims US-1b, US-2, US-4 and US-6b. PR 1 ships US-4's contract text without claiming US-4.

### User Story 1a — Scorer and controls finish complete at any size (Priority: P1 · Track R) · K6, K7, N14

*As an adopter running `/tachi.risk-score` and `/tachi.compensating-controls` on a large system (25+ components, 200+ findings),* I want both stages to finish with complete markdown and SARIF output, *so that* I never hand-assemble a file or run code an agent handed back.

**Why this priority**: These stages carry PM priorities 1 and 2: N14's no-hand-back contract and the scorer renderer. Run A's scorer wrote about a quarter of its SARIF and dropped a finding. Run B's scorer wrote nothing and handed back an unrun program, the #360 exposure. The scorer's bands set the remediation SLAs that security leads act on.

**Independent Test**: Run both commands on the fixture's precomputed `threats.md` (S-4: at least 390 open findings), with no orchestrator run, and compare each output with the reference finding set.

**Acceptance Scenarios**:

1. **Given** the fixture's precomputed `threats.md`, **When** `/tachi.risk-score` runs at the adopter default effort, **Then**:
   - `risk-scores.md` has exactly one open row per open finding in the reference set, and one RESOLVED row per Section 4c finding;
   - `risk-scores.sarif` satisfies the N/N rule (FR-E.1) and agrees with the `.md`'s open rows;
   - the stage record shows at least two batches, and no file was assembled by hand.

   `[MANUAL-ONLY] needs a live scorer run on the fixture; the offline half, the renderer on synthetic parts, is automated`
2. **Given** the same input and the fixture's stub codebase, **When** `/tachi.compensating-controls` runs at the adopter default effort, **Then**:
   - `compensating-controls.md` covers every scored open finding exactly once;
   - its totals equal the sums of its rows;
   - `compensating-controls.sarif` satisfies the N/N rule and agrees with the `.md`.

   `[MANUAL-ONLY] needs a live controls run on the fixture; the offline half, the renderer on synthetic parts, is automated`
3. **Given** either stage at `effort=max`, **When** it runs on the fixture, **Then** scenarios 1 and 2 hold (R-18). `[MANUAL-ONLY] needs live runs at effort=max`
4. **Given** a batch whose part file is missing, fails validation or carries another plan's ID, **When** the command reconciles from disk, **Then** it re-dispatches only the unfinished batches, narrower if the batch overflowed, up to the retry cap. The renderer never counts a stale or invalid part.
5. **Given** a batch that can't be recovered within the retry cap, **When** the command stops, **Then**:
   - the run fails with an error that names the stage, the batch, its finding IDs and the remedy;
   - the outputs stay for diagnosis but are marked failed, and no later command takes them as input or as a baseline (D-3).
6. **Given** either stage, **When** its run is inspected, **Then** no agent returned code to its caller, wrote a program file, or substituted another agent type, and the command ran only the shipped scripts it names. `[MANUAL-ONLY] needs a live run's transcript`
7. **Given** a shipped example below the batching threshold, **When** both stages run, **Then**:
   - each agent is invoked once (NFR-4);
   - the outputs keep every section and field (NFR-1);
   - output tokens are no worse than the v4.48.4 baseline, within the stated tolerance (SC-8).

   `[MANUAL-ONLY] needs live runs on a shipped example and the v4.48.4 baseline run`
8. **Given** a `threats.md` in one of the drift forms that tachi's shipped samples show (Section 7 as a numbered list of bolded IDs, or `## Section N: Title` headings), **When** the scorer and controls stages run, **Then**:
   - they read it as the reference set (S-12(a));
   - each finding whose needed value the form lacks, such as Section 7's Status column, gets what the baseline can supply, is otherwise scored fresh, and is flagged with the cause and listed in the stage record. The stage never stops for this (S-12(b));
   - any other unreadable Section 7 ends the run before any agent is dispatched, with an error that names the file, the section, the expected form and the remedy (S-12(c));
   - a baseline file that is present but unreadable is treated as missing: the stage scores fresh, records why, and warns that the baseline's human overrides weren't carried (S-12(d)).

---

### User Story 1b — The threat model and the report finish complete at any size (Priority: P2 · Track O) · K5, N4, FR-O.1

*As an adopter running `/tachi.threat-model` on a large system,* I want `threats.md`, `threats.sarif` and the narrative report to finish complete, *so that* the stage that feeds every other stage never silently loses a finding or an attack tree.

**Why this priority**: K5 is PM priority 5, but FR-O.1's membership and identity are never carved. This story ships in PR 2.

**Independent Test**: One baseline-aware `/tachi.threat-model` run against the fixture's synthetic baseline (S-4).

**Acceptance Scenarios**:

1. **Given** the synthetic baseline, **When** the threat model runs baseline-aware at the adopter default effort, **Then** `threats.md` is written as bounded parts that a shipped step joins, and its Section 7 holds every finding exactly once. `[MANUAL-ONLY] needs a live baseline-aware threat-model run; the joiner itself is tested offline`
2. **Given** the run's dispatch records, **When** record completeness is checked (FR-N4.6), **Then**:
   - every finding in every record has exactly one disposition in the ID map: kept, matched to a carried finding, merged into a named surviving finding, or superseded by a re-dispatch;
   - every ID change is recorded.
3. **Given** the compiled `threats.md`, **When** the shipped generator writes `threats.sarif`, **Then** the file satisfies the N/N rule and D-5's identity rules.
4. **Given** Phase 5, **When** the report is produced, **Then**:
   - a shipped step assembles `threat-report.md` from bounded parts;
   - Section 5 holds exactly one tree per Critical and High finding in `threats.md`, RESOLVED excluded;
   - every inline tree is byte-identical to its standalone file, and every carried-forward tree is byte-identical to its baseline file.

   `[MANUAL-ONLY] needs a live Phase 5; the assembly step and its checks run offline on synthetic parts`
5. **Given** the tree batches, **When** they finish, **Then** each batch's manifest is merged into one schema-1.0 `attack-trees/.manifest.json`, which the report agent reads.
6. **Given** a Phase 2 agent whose return is truncated (planted), **When** the orchestrator detects it by a missing end marker or a structured error, **Then**:
   - it re-dispatches that agent per component, with capped retries;
   - it marks the truncated record superseded, naming the records that replace it, and records the event in the stage record;
   - if it can't recover, the run fails (D-3).

   `[MANUAL-ONLY] needs a planted truncation in a live session (S-9's spike)`

---

### User Story 2 — An empty chain section means "none found", never "skipped" (Priority: P3 · Track O) · K4

*As a security lead reading the report,* I want to know whether cross-layer attack-chain analysis ran and what it concluded, *so that* an empty chain section means "none found", not "skipped".

**Why this priority**: K4 is PM priority 6. FR-K4.1 and FR-K4.1b are never carved, because they are cheap and they are the observability fix.

**Independent Test**: Offline, on the fixture's chain material and on hand-built `threats.md` files whose outcome records are missing or inconsistent.

**Acceptance Scenarios**:

1. **Given** any run, **When** the threat model finishes, **Then** `threats.md` records exactly one Phase 3.5 outcome, `chains written (N)`, `0 chains passed filter (<reason>)` or `skipped (<reason>)`, where N is the consolidated count, together with the candidate and surfaced counts (S-3(d), (g)). `[MANUAL-ONLY] needs a live threat-model run; the chain script's record is tested offline`
2. **Given** a `threats.md` with no outcome record, **When** the main session's post-run check runs, **Then**:
   - the record is written as `skipped (no outcome recorded)`;
   - the check warns, the stage record counts it, and the run continues (R-24).
3. **Given** a record that disagrees with the artifacts, for example `chains written (3)` with `attack-chains.md` absent, or accounting for two chains rather than three under S-3(g)'s rule, **When** the check runs, **Then**:
   - the record is rewritten as `skipped (<what disagreed>)`;
   - the chain output isn't presented as complete;
   - the report and the PDF read "skipped".
4. **Given** a pre-fix `threats.md` with no record, **When** the report and the PDF render, **Then** they fall back to today's file-presence rule and render byte-identically to today.
5. **Given** the fixture's chain material, **When** the shipped chain script forms chains twice on the same finding set, **Then** the two runs' chain-script output, titles and narratives excluded, is byte-identical, holds at least one chain, and stays within S-3(g)'s bound. If ADR-050 keeps chain formation in the model, the run records the algorithm and the counts instead (R-19).
6. **Given** the chain fixture, **When** the report and the PDF render, **Then** both show the surfaced chains, and the report prints, with each surfaced chain, how many other consolidated chains end at its terminal-impact finding (S-3(f)).

---

### User Story 3 — One controls schema, every recommendation joined (Priority: P2 · Track R) · K8, K7

*As a consumer of `compensating-controls.md`,* I want every Section 2 table to use the same columns, MAESTRO included, and every recommendation tied to its finding, *so that* parsers and readers get consistent data.

**Why this priority**: K7 and K8 are PM priority 4. In PR 1, controls Sections 2 and 4 stay model-authored inside the part files (R-34), so SC-5 is shown on the fixture's live runs rather than by construction.

**Independent Test**: Generate a controls file from the fixture, compare its tables, and parse it in both formats.

**Acceptance Scenarios**:

1. **Given** a generated controls file, **When** its Section 2 band tables are compared, **Then** all of them use one column schema that includes MAESTRO Layer and Control Category, and `CF` is the carried-forward marker that `carry_forward_count` counts (R-20).
2. **Given** Section 4, **When** its blocks are joined to Section 2's rows, **Then** there is one block per finding, each joined to its finding, with no unjoined recommendation.
3. **Given** the totals and Section 5's aggregate and band-shift tables, **When** they are compared with the rows, **Then** the renderer computed them, the totals equal the sums of the rows, and the `.md` agrees with the `.sarif`.
4. **Given** a controls file in either the corrected or the pre-fix format, **When** #373's parsers read it, **Then** both formats parse, to the same rows.
5. **Given** PR 1, where R-34's fallback applies, **When** an agent authors Sections 2 and 4 inside its part files against the single template, **Then**:
   - every score and band in those sections is either filled by the renderer or checked by a shipped check that flags each mismatch (ADR-050 item 2 decides, cell by cell);
   - the renderer still writes the whole file.

   `[MANUAL-ONLY] needs live controls runs on the fixture (R-34); the renderer's fill-or-check of each cell is tested offline`

---

### User Story 4 — Typed agents do the analysis, under their published contracts (Priority: P1 · Track S for the text, Track O for the checks) · N4, N14

*As an adopter scanning a codebase I don't control,* I want the analysis done by tachi's typed agents under their published contracts, with no improvised agents, policy or scripts, *so that* I can trust the result, reproduce it, and know which tools touched the code.

**Why this priority**: N4's and N14's contract text is PM priority 1 and lands by the cut line, so PR 1 ships it, after one small `/tachi.threat-model` smoke run on a shipped example is recorded (R-27). PR 1 doesn't claim the story, because its checks (FR-N4.5 to FR-N4.7) ship in PR 2. Run B's stand-ins read third-party source through Bash while holding Write, Edit and Agent. The typed threat agents they replaced hold Read, Glob and Grep.

**Independent Test**:
- In PR 1: static assertions on the agent and command text.
- In PR 2: the provenance and completeness checks on synthetic runs, plus the fixture runs' structure-only audit.

**Acceptance Scenarios**:

1. **Given** any run, **When** Phase 2 dispatches, **Then** every analysis is done by a typed tachi agent from the canonical roster. When a typed agent can't be spawned, the run stops with an error that names the agent and the remedy (re-run `install.sh`), and no substitute runs. `[MANUAL-ONLY] needs a live threat-model run, plus an uninstalled agent for the stop`
2. **Given** any run, **When** the provenance check runs, **Then** every finding in `threats.md` has exactly one provenance entry: a typed agent's dispatch record (through the ID map), a baseline carry-forward reference, or a named deterministic rule (`AGP-NN`, Phase 3.6). A run with no dispatch records fails.
3. **Given** any dispatch, **When** its prompt and brief are inspected, **Then**:
   - the agent was given the fixed one-line prompt that tells it to read and follow its brief;
   - the brief is saved under the run's `.tachi-build/briefs/` and holds only the brief template's closed set of fields;
   - the brief points at the architecture snapshot and at the persisted Phase 1 inventory and dispatch table, rather than copying them.

   `[MANUAL-ONLY] needs a live run's prompts; the briefs' field set is checked offline`
4. **Given** the report agent's sub-dispatches, **When** they are checked, **Then** each one is a typed tachi agent. A tree file missing from the merged manifest, or a report that the assembly step didn't write, fails the FR-K5.7 check.
5. **Given** every tachi agent spec, **When** its text is checked, **Then**:
   - none tells the agent to return code, write a program for someone else to run, or substitute an agent type;
   - none carries the platform-neutral clause (FR-N4.1);
   - the three commands say to run only the shipped scripts they name, and to stop on failure.
6. **Given** any fixture run, **When** its transcript is audited (structure only, kept private), **Then**:
   - it shows 0 `general-purpose` dispatches, 0 unshipped scripts run, 0 program files written and 0 code hand-backs;
   - every rendered output carries the renderer's stamp;
   - the output directory holds only declared paths.

   `[MANUAL-ONLY] needs a fixture run's transcript (structure-only audit, kept private)`

---

### User Story 5 — Carried scores are recomputed, and every change is flagged (Priority: P1 · Track R) · N16, N15

*As a security lead tracking risk over time,* I want findings that carry over from a baseline to have their scores recomputed from their inputs, with any change flagged, *so that* one run's slip never becomes permanent baseline data.

**Why this priority**: N16 is part of PM priority 2. In Run B's baseline, 64 of 202 composites disagreed with their own dimensions, all of them inherited from an older run, and only 83 of 202 vectors reproduced their stated score.

**Independent Test**: Offline. Feed the renderer the fixture's seeded-error, legacy-format, tagged, ties and regroup variants (S-4), and compare its output with each variant's expected outcomes.

**Acceptance Scenarios**:

1. **Given** a carried finding whose inputs didn't change, **When** the scorer stage runs, **Then**:
   - its inputs are inherited verbatim;
   - its derived fields are recomputed;
   - any change from the stored values is flagged with its cause.
2. **Given** a stored CVSS base score that its vector doesn't give, outside the documented clamps, **When** the renderer runs, **Then** it corrects the score and flags the correction (R-9). The asset-modifier outcomes of R-25 count as documented clamps.
3. **Given** a carried finding with no vector, **When** the renderer runs, **Then** the finding keeps its inherited score with `cvss_vector: null` and is flagged unverifiable. Its score changes only if the agent re-assesses it and records that judgment (R-7).
4. **Given** a check that depends on an N17 ambiguity, such as a compound trust label, **When** the renderer runs, **Then** the case is reported as unchecked, never as a violation (R-10).
5. **Given** a difference that comes only from rounding, **When** the renderer runs, **Then**:
   - if the band, SLA, disposition and review date all stay the same, the difference is normalized and counted in the run summary, not flagged per finding;
   - if it moves the band, it is flagged as a band correction with rounding as its cause, and R-5 applies (R-11).
6. **Given** the regroup pair, in which correlation regroups carried findings and changes a group's primary, **When** the scorer stage runs on run 2, **Then**:
   - no carried finding's score, band or SLA changes because of the regroup alone;
   - an UNCHANGED peer whose carried score differs from its new primary's keeps its score and is flagged divergent;
   - NEW and UPDATED peers inherit their primary's vector and scores (R-31).
7. **Given** a band that recomputation corrects, **When** the review date is set, **Then** it moves to the corrected SLA counted from the original scoring date, which is the stored review date minus the stored SLA. Only an input change restarts the clock (R-5). Where either stored value is missing, ADR-050 item 9's fallback applies, and the case is flagged.
8. **Given** an Accept or Transfer disposition, or an SLA or disposition that differs from the **stored** band's default, **When** the renderer runs, **Then** the value is carried verbatim and marked as an override (R-31).
9. **Given** RESOLVED findings in the baseline, **When** `risk-scores.md` is rendered, **Then**:
   - their rows keep their last-known values, governance fields included, verbatim: never recomputed or flagged, and outside the SLA clock;
   - each row is marked resolved;
   - the Executive Summary counts them separately, never in its severity distribution;
   - no SARIF file carries them, as a result or in `relatedLocations` (R-30).
10. **Given** a legacy-format baseline (no sub-score tables, vectors on only some markdown rows, full vectors in the SARIF), **When** the renderer runs, **Then**:
    - the exploitability, scalability and reachability values are the inputs, kept verbatim;
    - the base score is checked against the markdown's vector, or else the baseline SARIF's `cvss-vector` property;
    - when both carry a vector and they differ, the markdown's is used and the disagreement is flagged;
    - the seeded composite and vector errors are corrected and flagged (R-26).
11. **Given** a `threats.md` whose `baseline.source` names a prior run, **When** the scorer and controls stages run, **Then**:
    - they read their baseline files from that run's directory;
    - the command's override flag, when given, takes precedence;
    - if the baseline file is missing, the stage scores fresh and records why (R-6, D-6(c)).
12. **Given** a tagged component, **When** the asset-modifier step runs, **Then**:
    - a finding's score is the larger of its assessed score and its elevated score capped at 9.2, so a finding assessed above 9.2 keeps its score;
    - a carried legacy finding that stores only an elevated score above 9.2 keeps its stored score and is reported as unchecked (R-25).
13. **Given** a carried finding whose band rises only because of its asset tags, **When** the renderer runs, **Then**:
    - the change isn't flagged `corrected`; it gets its own `retagged` flag;
    - its review date becomes this run's scoring date plus the new SLA, unless the stored review date is earlier, in which case the stored date is kept;
    - an SLA override still keeps its review date.

    "Only because of its asset tags" means that recomputing with the baseline's recorded tags gives the stored band. A legacy row records no tags, so there it means a band change that comes only from the elevation this run's tags apply. That covers the first run after upgrading (ruling A).
14. **Given** a carried finding whose band falls only because a tag was removed, **When** the renderer runs, **Then** the original scoring date is kept, as for a correction (R-5). A deadline already missed under the lower band's SLA stays missed (ruling A).

---

### User Story 6a — Scorer and controls alerts keep their identity across runs (Priority: P1 · Track R) · N12, K6, K7

*As a Code Scanning consumer uploading tachi's SARIF on every baseline-aware run,* I want a finding that is still present to keep its alert, *so that* alerts aren't closed as fixed when nothing was fixed, and my dismissals and history stay with the finding.

**Why this priority**: D-5's identity rule is PM priority 3, and it is never carved except through SV-3's technical trigger. Today the scorer and controls alerts can close and reopen on every run (§1 of the PRD, root problem 5).

**Independent Test**: Offline. Run the renderer on both runs of the regroup pair and on an unchanged re-run, then compare the matching keys.

**Acceptance Scenarios**:

1. **Given** two baseline-aware runs in which correlation regroups carried findings, **When** the scorer and controls SARIF of both runs are compared under the matching key, **Then** every carried finding that is present in run 2 keeps its run-1 key, in each file.
2. **Given** an unchanged re-run, **When** the keys are compared, **Then** every key is identical.
3. **Given** the three SARIF files, **When** their tools and categories are compared, **Then**:
   - the tool names are `Tachi`, `tachi-risk-scorer` and `tachi-control-analyzer`, verbatim (R-33);
   - the three (tool, category) pairs differ.
4. **Given** any result in these files, **When** its identity fields are read, **Then**:
   - it carries tachi's own `primaryLocationLineHash`, unique among the file's present findings and computed from a stable per-finding key, never from model prose (S-6);
   - its `artifactLocation.uri` is the user's repo-relative architecture path, in one canonical spelling;
   - no file carries `runAutomationDetails`.
5. **Given** a RESOLVED finding, **When** the SARIF is rendered, **Then** the finding is neither a result nor a `relatedLocations` entry.
6. **Given** a stateless re-run, which renumbers findings, **When** its keys are compared, **Then** they may differ, and the release notes say so (R-29).
7. **Given** the scorer or controls command run with the architecture-path override flag, **When** it writes its SARIF, **Then** every `artifactLocation.uri` is the flag's path, validated and repo-relative (FR-E.18).
8. **Given** no flag and a `threats.md` that carries the architecture-path body line, **When** the command writes its SARIF, **Then** every URI is the body line's path, validated and repo-relative.
9. **Given** no flag and a pre-fix `threats.md` with no body line, **When** the command writes its SARIF, **Then** every URI is `docs/security/architecture.md`, and the command warns that the body line is absent and names the override flag.
10. **Given** a NEW finding whose ID appears in the baseline `risk-scores.md`, **When** the scorer and controls render, **Then** both files flag it `reused-id`, and PR 1's release notes state the exposure until PR 2 and name the flag (ruling B).
11. **Given** a correlated result, **When** the emitter writes it, **Then** its `message.text` ends with one sentence. On a peer, the sentence names its group and its primary. On a primary, it names its group and its peers, up to the shared reference's cap, then a count. A regroup changes that text, never a key (ruling C).

---

### User Story 6b — `threats.sarif` alerts keep their identity across runs (Priority: P1 · Track O) · N12, FR-O.1

*As a Code Scanning consumer of the file the docs tell me to upload,* I want regrouping to leave my `threats.sarif` alerts alone, *so that* distinct findings don't collapse into one alert, and regrouped findings don't drop out.

**Why this priority**: D-5's identity rule is PM priority 3 for all three files, and it is never carved, except through SV-3's technical trigger. N12 was observed in `threats.sarif` (38 results dropped in Run B). Its identity and its upload line change together in PR 2, so its alerts re-key only once.

**Independent Test**: Offline. Generate `threats.sarif` for both runs of the regroup pair and for an unchanged re-run, then compare the matching keys.

**Acceptance Scenarios**:

1. **Given** the regroup pair, **When** both runs' `threats.sarif` files are compared under the matching key, **Then** every carried finding present in run 2 keeps its run-1 key, and none drops out.
2. **Given** two distinct findings with the same rule and component, **When** `threats.sarif` is generated, **Then** their keys differ.
3. **Given** an unchanged re-run, **When** the keys are compared, **Then** every key is identical.
4. **Given** the developer guide, **When** PR 2 merges, **Then** both Code Scanning snippets upload `threats.sarif` with `category: threat-model` from a run's timestamped output directory (FR-E.11).
5. **Given** a baseline with live and resolved IDs, **When** Phase 3 numbers NEW findings, **Then**:
   - each prefix's new IDs sit above a per-prefix high-water mark, which shipped code writes as a `threats.md` body line. The first PR 2 run seeds it from the baseline's live IDs and Section 4c;
   - `check-threat-model.py` warns (exit 5) on any NEW finding whose ID the baseline used, or that sits at or below the mark, and the run continues (ruling B).

---

### Edge Cases

- **Small inputs.** An input that fits one batch is processed by one invocation, as today (NFR-4).
- **A stop that returns nothing parseable.** A `max_tokens` stop mid-reasoning can return nothing a parser can read. The dispatching layer works out what is done from the part files on disk, never from the agent's reply (D-3).
- **Re-runs.** A re-run reuses the same `.tachi-build/` directory, and agents can't delete files. Each plan carries a fresh plan ID, so a part from an earlier plan is never counted (FR-E.3).
- **Hostile parts.** A part with unknown keys, NaN or Infinity, duplicate IDs, or IDs outside its batch's list is rejected (NFR-10).
- **Forged structure.** A prose fragment that would start a line with `#` or `|` is neutralized, and a code snippet that contains a backtick run gets a longer fence (NFR-10).
- **The architecture path.** A path that resolves outside the repository, is a symlink, or differs from the real path only in letter case falls back to a stated value with a warning, or is emitted in its canonical spelling (D-5, KB 24).
- **`baseline.source`.** When it is free text or doesn't resolve to a run directory (#379), the stage scores fresh and records why (D-6(c)).
- **Legacy baselines.** A baseline written by a pre-fix version is read by the tolerant baseline parser under R-26.
- **Drift forms of Section 7.** A `threats.md` that writes Section 7 as a numbered list of bolded IDs, or uses `## Section N: Title` headings, is read. Findings whose needed values that form lacks are derived from the baseline, or scored fresh and flagged. Any other unreadable Section 7 ends the run before any agent is dispatched, and an empty extraction is an error, never a pass (S-12).
- **An unreadable baseline file.** A baseline file that is present but unreadable is treated as missing: the stage scores fresh, records why, and warns that the baseline's human overrides weren't carried (S-12(d)).
- **A failed run.** Its outputs stay for diagnosis, marked failed, and no later command takes them as input or as a baseline (D-3).
- **A missing typed agent.** The run stops with the installer remedy (D-3).
- **Fan-out.** A per-component re-dispatch that would put more than 20 subagents in flight is sent in waves (S-8).
- **No PyYAML.** The scorer and controls core path runs without PyYAML; only the PDF attestation page needs it (NFR-2).
- **#356 renumbering.** While #356 is open, `OI-`, `MI-` and `TE-` findings that Phase 3 folds into the `LLM-N` and `AG-N` sequences are recorded in the ID map, and a test pins today's behavior (NG4).
- **Zero chains, legitimately.** A model whose findings span one MAESTRO layer, or that has no STRIDE findings, records `0 chains passed filter (<reason>)`.
- **Identity under change.** An UPDATED finding whose component changed keeps its key, because its ID carries over. Moving or renaming the architecture file re-keys every alert once, and the release notes say so (§8 item 1).
- **Upload limits.** Each file stays far below GitHub's limits of 25,000 results per run and 10 MB per gzipped file. At most one result per deduplicated finding is about 210 results at Run B's scale.

## Requirements *(mandatory)*

> **AC rule.** The acceptance scenarios above follow Given/When/Then. A requirement that no story covers carries its own scenario. `[MANUAL-ONLY] <reason>`, inline, marks each scenario that needs a live model session:
> - US-1a #1, #2, #3, #6 and #7;
> - US-1b #1, #4 and #6;
> - US-2 #1;
> - US-3 #5;
> - US-4 #1, #3 and #6;
> - the live halves of SC-1, SC-3 and SC-8.
>
> When a marked scenario also has an offline half (the shipped scripts on synthetic parts), its marker says so, and that half is automated. Every other scenario is automatable, by one of three methods:
> - synthetic fixtures (S-4);
> - static assertions on agent, command and reference text;
> - offline runs of the shipped scripts.
>
> **Traceability.** IDs match the PRD. Requirements this spec adds are marked *(spec S-n)*. File pointers are to `main` at `b040fa1` (v4.48.4), which is this branch's base. Research re-verified 51 of them, with two corrections (research.md, items 8 and 9).
>
> **Track tags.** Each requirement carries **[S]**, **[R]** or **[O]** (Terminology). A requirement tagged **[R+O]** is split by file: Track R takes the scorer and controls files, and Track O the rest.

### Functional Requirements

#### Group A — Orchestrator (`orchestrator.md`, `.claude/skills/tachi-orchestration/references/`, `.claude/skills/tachi-shared/references/`, `templates/tachi/output-schemas/threats.md`, `.claude/commands/tachi.threat-model.md`)

##### K4 — Phase 3.5 has no recorded outcome, and two algorithms disagree

- **FR-K4.1 (outcome record) [O]** — Phase 3.5 MUST write its outcome to `threats.md` in every run. It replaces the in-memory `has-attack-chains` boolean (`orchestrator.md:486`, `:546-550`). The record holds:
  - the outcome: `chains written (N)`, `0 chains passed filter (<reason>)` or `skipped (<reason>)`;
  - the candidate, consolidated and surfaced counts (S-3).

  Which of the two options the record uses (a body line that needs no schema bump, or a key that #396 then declares) is plan input P-3. The plan also corrects the stale "1.2" at `output-schemas.md:285`. Every reader reads the record and falls back to today's file-presence rule when it is absent: the report agent, `tachi_parsers.detect_artifacts`, `extract-report-data.py`'s `prepare_attack_chains`, and `main.typ`. Exempt from SV-1. → US-2 #1, #4
- **FR-K4.1b (outcome check) [O]** — After the orchestrator returns, the main session MUST check the record against the artifacts:
  - "chains written (N)" passes when `attack-chains.md` accounts for exactly N consolidated chains, under S-3(g)'s rule: its full chains equal the surfaced count, its compact rows equal the smaller of 100 and N minus the surfaced count, its last line gives the rest, and its frontmatter counts match the record;
  - "0 chains" and "skipped" each require the file to be absent and a reason recorded.

  An offline test with more than 105 consolidated chains exercises the cap, the remainder line and this check (S-3(g)).

  A missing record is written as `skipped (no outcome recorded)`. An inconsistent one is rewritten as `skipped (<what disagreed>)`, and the chain output isn't presented as complete (ADR-050 item 13 picks the mechanism). Either way, the check warns, the stage record counts the event, and the run continues (R-24). A test covers each case. Exempt from SV-1. → US-2 #2, #3
- **FR-K4.2 (one algorithm) [O]** — Phase 3.5 and `attack-chain-patterns-shared.md` MUST describe one algorithm: S-3's rules, with the S-2 order replacing "lower finding ID" (`orchestrator.md:449`). The run records the candidate, consolidated and surfaced counts as S-3(d) defines them, and surfaces chains under S-3(f), each surfaced chain with the number of other consolidated chains that end at its terminal-impact finding. If ADR-050 adopts R-19, the computational steps run in a shipped script, and the model writes titles and narratives for the surfaced chains only. → US-2 #5
- **FR-K4.3 (root cause first) [O, evaluated at the end of W0]** — A 5 Whys on Run A's skip, time-boxed at 0.25 day, MUST weigh all four of #374's candidates (context pressure, instruction ordering, a skipped conditional, link criteria that legitimately yield zero) before the K4 build. Its disposition is decided in advance (TW-K4). A finding that would change which findings join chains goes to the PM first (R-21). *Scenario:* **Given** the time-boxed analysis, **When** it ends, **Then** the PR records the candidate it confirmed or ruled out for each of the four, and TW-K4's outcome (a), (b) or (c).
- **FR-K4.4 (fixture) [O]** — On the fixture's chain material, chain formation MUST form chains; `attack-chains.md` stays within S-3's bound; and the report and the PDF show the surfaced chains. → US-2 #5, #6

##### N4 — typed dispatch, records, briefs and checks

- **FR-N4.1 (typed dispatch) [S]** — Phase 2 and the report agent's sub-dispatches MUST name typed `subagent_type`s from one canonical roster, kept in one shared reference (D-3). The text that does so:
  - replaces `orchestrator.md:278-280` and `:302`;
  - removes or rewrites the platform-neutral clauses at `orchestrator.md:68`, `risk-scorer.md:18`, `control-analyzer.md:20`, `threat-report.md:44`, `report-assembler.md:52` and `threat-infographic.md:99`;
  - corrects the stale body-table rosters (`finding-format-shared.md:87-88` and `:200-202`; `coverage-requirements.md:153-154`);
  - tells the orchestrator to stop with an actionable error when a typed agent can't be spawned (FR-E.6).

  This implements #408's body-instruction option (R-14). No agent's `tools:` list carries an `Agent(...)` type list (S-10). → US-4 #1, #5
- **FR-N4.2 (dispatch records) [O; record template S]** — The orchestrator MUST persist one record per dispatch under the run's `.tachi-build/` (R-8). SV-2b is carved at the plan stage (ADR-050 D1), so the record is a per-dispatch manifest: the agent type, the scope, the count and the provisional IDs, possibly none. Phase 3 writes the ID map. The threat agents stay read-only (NG8). → US-1b #2, US-4 #2
- **FR-N4.3 (briefs) [O; brief template S]** — A brief MUST hold only the brief template's closed set of fields: the target components, the agent's input pointers and the baseline focus. It points at the architecture snapshot, and at the Phase 1 inventory and dispatch table persisted under `.tachi-build/`. Each agent is dispatched with the fixed one-line prompt, and the SC-3 audit compares each actual prompt with it. The recommended brief-rendering script drops under R-34 (feasibility row 13). → US-4 #3
- **FR-N4.4 (no ad-hoc scripts) [S]** — The orchestrator MUST run only shipped scripts (R-22). Its fenced commands use `python3` with no `$(`, backticks, `xargs` or `bash -c` (guard C6), so the resume reconciliation is a shipped script. *Scenario:* **Given** the orchestrator spec, **When** guard C6 and a static assertion scan its fenced commands, **Then** each one runs a shipped script by name.
- **FR-N4.5 (provenance check) [O]** — After the orchestrator returns, the main session MUST check that every finding in `threats.md` has exactly one provenance entry (Terminology). A run with no dispatch records fails, which catches failure mode 3. The check confirms the orchestrator's own record; it doesn't prove provenance, which is #399's job. → US-4 #2
- **FR-N4.6 (record completeness) [O]** — The same check MUST run the other way: every finding in every dispatch record has exactly one disposition in the ID map (kept; matched to a carried finding by Phase 3a, exactly or by similarity; merged into a named surviving finding; superseded by a re-dispatch). Every ID change is recorded, and an empty record set is an error. Tests cover carried, renumbered and pattern findings, plus an agent that is truncated and then re-dispatched in a stateless run. → US-1b #2
- **FR-N4.7 (Phase 2 overflow) [O]** — The orchestrator MUST detect a truncated or overflowed return, by a missing end marker or a structured error. It then re-dispatches that agent per component, with capped retries and within S-8's limits, and records the event; if it can't recover, the run fails (D-3). The end marker is defined in the shared finding-format reference (S-9). The detector is built against S-9's spike. → US-1b #6

##### FR-O.1 — the orchestrator's own outputs at scale

- **FR-O.1 (orchestrator outputs) [O]** —
  - **SV-2a, never carved:** `threats.sarif` MUST come from a shipped generator over the compiled `threats.md`, sharing the renderer's D-5 emitter.
  - **Bounded emission:** `threats.md` MUST be emitted in bounded parts that a shipped step joins, each part within S-1's budget.
  - **SV-2b, may be carved:** rendering `threats.md`'s tables in code may be carved at TW-0 or TW-R. Bounded emission stays either way. If SV-2b's rendering ships, ADR-047's applicability authority moves to that code, as a single authority.

  → US-1b #1, #3

#### Group B — Threat report (`threat-report.md`, `attack-tree-delta.md`, `.claude/skills/tachi-threat-reporting/references/`, `templates/tachi/output-schemas/threat-report.md`)

- **FR-K5.1 (whole report bounded) [O]** — No single response MAY carry the whole report. A shipped step MUST assemble `threat-report.md` from bounded part files: one per section, and one per batch of findings for the per-finding sections. Section 5 is one part, taken from the standalone tree files. The plan decides who runs the step: the orchestrator after Phase 5 returns, or `/tachi.threat-model` (ADR-050 item 14). → US-1b #4
- **FR-K5.2 (inline equals standalone) [O]** — Every inline tree MUST be byte-identical to its standalone file. This is true by construction, because the assembly copies the files, and a test checks it. → US-1b #4
- **FR-K5.3 (carried-forward trees unchanged) [O]** — Tree carry-forward MUST be a file copy done by the shipped step, never a model transcription. A test checks it. → US-1b #4
- **FR-K5.4 (typed helpers) [S]** — The report agent's sub-dispatches MUST be typed tachi agents only (FR-N4.1). → US-4 #4
- **FR-K5.5 (tree count) [O]** — Section 5 MUST hold exactly one tree per Critical and High finding in `threats.md`, RESOLVED excluded. Code checks this against `threats.md`, not against the tree agent's manifest. → US-1b #4
- **FR-K5.6 (tree batches) [O]** — A layer that runs Bash (the orchestrator, or `/tachi.threat-model`) MUST plan and batch the tree sub-dispatches and handle their overflow (D-3; ADR-050 item 6). The batches stay within S-8's limits and run in the foreground. Each batch writes its own manifest under `.tachi-build/`, and the assembly step merges them into one schema-1.0 `attack-trees/.manifest.json`, which the report agent reads (research item 8). No agent gains a tool. → US-1b #5
- **FR-K5.7 (failure-mode 2 check) [O]** — Every tree file MUST be listed in the merged manifest, and Section 5 MUST be assembled by the shipped step. This confirms consistency, not provenance: a helper that writes both the trees and the manifest passes. It catches a helper that skips the manifest or writes the report itself, because the assembly step overwrites the report and D-7's stamp shows who wrote it. → US-4 #4

#### Group C — Risk scorer (`risk-scorer.md`, `.claude/commands/tachi.risk-score.md`, `.claude/skills/tachi-risk-scoring/`, `templates/tachi/output-schemas/risk-scores.md`)

- **FR-K6.1 (row parity) [R]** — `risk-scores.md`'s rows MUST equal the reference finding set: its open rows equal Section 7, and its RESOLVED rows equal Section 4c (R-30). Rows the agent couldn't parse, which today are "reported as parsing errors" with no defined place (`risk-scorer.md:179-182`), are listed in a defined section of the output. → US-1a #1
- **FR-K6.2 (SARIF N/N and identity) [R]** — `risk-scores.sarif` MUST satisfy the N/N rule and D-5's identity rules, and agree with the `.md`'s open rows by construction. → US-1a #1, US-6a
- **FR-K6.3 (the renderer owns the files) [R]** — The renderer MUST write the whole of `risk-scores.md` and `risk-scores.sarif` (D-2). The agent spec drops its output-format instructions. → US-1a #1
- **FR-N14.1 (overflow) [R; contract text S]** — No agent MAY hand back code. `/tachi.risk-score` MUST own batching and resume (D-3): it runs the shipped planner, dispatches the batches within S-8's limits, reconciles from disk, and re-batches narrower on overflow, with capped retries. Today `risk-scorer.md:93` leaves batching to the command, which invokes the scorer once (`tachi.risk-score.md:114-147`). → US-1a #4, #5, #6
- **FR-N14.2 (renderer) [R]** — The renderer MUST compute D-2's right-hand column and write both whole files. It is shipped, tested, installed and listed under S-13. → US-1a #1
- **FR-N16.1 (recompute and flag) [R]** — D-4 and D-6 apply:
  - derived fields are recomputed;
  - vector mismatches are corrected and flagged;
  - reachability ranges are checked for labels that normalize unambiguously;
  - every ID prefix gets a category, `AGP`, `OI`, `MI` and `TE` included;
  - "unchecked" and rounding-only cases are reported as such.

  The asset-modifier step follows R-25, and the formula at `asset-modifiers.md:56` is corrected to match. A tolerant baseline parser reads legacy baselines under R-26. → US-5
- **FR-N16.2 (one source for asset tags) [R] *(spec S-13)*** — The asset-modifier step and the SARIF `affected_assets` property MUST read a finding's tags from one named source. When that source is stale or absent, the renderer recomputes the tags through the populator's own function. When it can't, it scores without the asset elevation, warns that the tags weren't applied, and records the cause in the stage record. It never stops the run for this, and it never mixes sources. → US-5 #12
- **FR-N15.1 (inheritance) [R]** —
  - (a) The SARIF-count text is reworded once, after ADR-050 fixes the membership rule, in all seven places (D-6(a)).
  - (b) and (c) follow D-6.

  → US-5
- **FR-C.1 (adapter copies) [S+R+O]** — Each adapter copy of an edited spec MUST follow R-17: a superseded-by header and a follow-up in the #369 family. A warning at the top of the adapter README says to install with `scripts/install.sh`, never by copying that directory over `.claude/agents/tachi/`. *Scenario:* **Given** an edited spec that has a copy under `adapters/claude-code/`, **When** its PR merges, **Then** the copy carries the header and the follow-up issue exists.

#### Group D — Control analyzer (`control-analyzer.md`, `.claude/commands/tachi.compensating-controls.md`, `templates/tachi/output-schemas/compensating-controls.md`, `.claude/skills/tachi-control-analysis/references/`)

- **FR-K7.1 (SARIF N/N) [R]** — `compensating-controls.sarif` MUST satisfy the N/N rule and D-5's identity rules. Each peer is counted once, never as both a result and a `relatedLocations` entry. Correlation-group membership comes from the one source that ADR-050 item 8 names: `threats.md` Section 4a, read through a shared parser, or a group map in the scorer's output (research item 13). → US-1a #2, US-6a
- **FR-K7.2 (totals) [R]** — The renderer MUST compute the residuals, the totals and the Section 5 tables, so the totals equal the sums of the rows by construction. A test keeps that from regressing. Today the agent's check verifies counts only (`control-analyzer.md:353`). → US-3 #3
- **FR-K7.3 (agreement) [R]** — The `.md` and the `.sarif` MUST agree, by construction. Under R-34's fallback, a shipped check covers Sections 2 and 4. → US-3 #3, #5
- **FR-K7.4 (the scorer's gaps) [R]** — Four of the scorer's fixes apply here too:
  - `/tachi.compensating-controls` owns batching and resume (`control-analyzer.md:133`), and its new `python3` step first checks that the interpreter is present, naming the remedy (KB 20);
  - the baseline is resolved under D-6(c) (`:116`);
  - the agent's input contract matches what the command passes: paths, not file contents (`:52-62`);
  - the rows the agent couldn't parse are listed in a defined section of the output, as FR-K6.1 does for the scorer (D-4).

  → US-1a #2, #4
- **FR-K8.1 (one Section 2 schema) [R]** — Section 2 MUST use one schema that includes MAESTRO Layer and Control Category. The output-schema template documents it, and `CF` is the carried-forward marker (R-20). In PR 1, under R-34, Sections 2 and 4 stay model-authored against the single template inside the part files, with their scores and bands filled or checked by code. Rendering them is a follow-up, which PR 2 may take on if that doesn't move its date. The agent spec stops restating the schema (`control-analyzer.md:349`). → US-3 #1, #5
- **FR-K8.2 (every table, and Section 4) [R]** — Every band table MUST use the schema, and Section 4 uses one block per finding, each joined to its finding. #373's K9 and K13 parsers read both the corrected and the pre-fix formats. → US-3 #2, #4
- **FR-K8.3 (the installed SARIF guide) [R]** — Once the renderer writes the controls SARIF, the guide that tells agents how to author it (`adapters/claude-code/agents/references/sarif-generation.md`) MUST be updated or retired. *Scenario:* **Given** PR 1, **When** the guide is read, **Then** it no longer instructs an agent to author SARIF that the renderer owns.

#### Group E — Shared

- **FR-E.1 (N/N and identity reference) [S]** — One shared reference MUST cover all three SARIF files (D-5). It replaces the four contract copies: `sarif-specification.md`, `risk-scorer.md` §10, the installed `sarif-generation.md`, and the control analyzer's Phase 6c. It also:
  - states ADR-050's counting rule;
  - corrects `sarif-specification.md:585` ("exactly N entries");
  - resolves the contradiction between `:339` and `:612`;
  - corrects `risk-scorer.md:462`'s lowercase tool name (R-33).

  *Scenario:* **Given** the shared reference, **When** the other three contract copies are read, **Then** each one points at the reference or is retired, and the census (FR-E.17) records which.
- **FR-E.2 (identity test) [R; the `threats.sarif` case O]** — An offline two-run test MUST model GitHub's matching key. Per file, it asserts that:
  - no still-present finding's key disappears;
  - an unchanged re-run's keys are identical;
  - no two present findings share a key (the F-012 lesson);
  - a case variant of the architecture path yields the same URI (KB 24).

  A cross-file assertion checks that the three (tool, category) pairs differ (R-33). → US-6a, US-6b
- **FR-E.3 (overflow and batching contract) [S]** — The structured overflow error and the batch planner's contract MUST each be defined once:
  - input slicing;
  - resume from the files on disk;
  - a fresh plan ID and the input digests on every plan;
  - the plan ID and batch ID on every part.

  The planner runs only where Bash runs, and its batch sizes follow S-1. A test seeds a stale part. → US-1a #4
- **FR-E.4 (fixture) [S]** — The fixture generator and its outputs MUST be committed, with the shape that S-4 pins. → all stories
- **FR-E.5 (tests and wiring) [S, R and O, per module]** — Tests MUST run on synthetic fixtures only, in three gates:
  - **`tachi-install-fidelity.yml`** is the default for the renderer, checker and parser suites. Its scope includes S-13 and `test_write_confinement.py`, which is extended to every new script.
  - **`tachi-pytest.yml`** takes only modules that need its cross-platform bash matrix.
  - **`tachi-permissions-verify.yml`** covers every agent, command, §8 and runbook edit.

  Each module is wired together with its input surfaces in its gate's `paths:` list and invocation, in the same commit (KB 3). Every new script, and every helper it imports, goes into all three places in `INSTALL_MANIFEST.md`, into `REQUIRED_SCRIPT_NAMES` and S-13's allowance, and into `ENTRY_SCRIPTS_IMPORTING_PARSERS`. *Scenario:* **Given** a commit that adds a test module or a shipped script, **When** it is checked, **Then** the module is in exactly one gate's `paths:` list and that gate's invocation, with its input surfaces, and the script is in every listing above, all in that same commit.
- **FR-E.6 (failure handling) [R+O]** — D-3's failure behavior MUST apply on its three run-ending paths: a typed agent that can't be spawned [text S, check O], a failed provenance or completeness check [O], and an unrecoverable batch [R for the scorer and controls, O for Phase 2 and the trees]. The error names the stage, the agent or finding IDs involved, and the remedy. The outputs are marked failed through a mechanism that needs no N7 change (plan input P-4). There is one test per path. → US-1a #5, US-4 #1
- **FR-E.7 (in-run signals) [R+O]** — Every rendered output MUST carry the renderer's version and an input digest, and a post-run check MUST assert that the output directory holds only declared paths (D-7). → US-4 #6
- **FR-E.8 (#409's dispatch-target check)** — *Drops at `/aod.tasks` under R-34 (feasibility row 13).* #409 is sequenced right after this bundle (R-15), and #408 stays open for R-14's run-time bound.
- **FR-E.9 (#412) [R; `threats.sarif` O]** — Each emitter MUST write the real `informationUri`, and the templates and instructions that carry the placeholder are corrected (R-16). *Scenario:* **Given** any SARIF file a shipped emitter writes, **When** its `tool.driver.informationUri` is read, **Then** it is the real repository URL, never the placeholder.
- **FR-E.10 (Section 6 parity) [O]** — `threats.md` Section 6's counts and percentages MUST be checked against the reference finding set (D-4), classifying MAESTRO applicability through ADR-047 D2's helper, never re-deriving it from Section 1. They stay model-written unless SV-2b's rendering ships. *Scenario:* **Given** a compiled `threats.md` whose Section 6 disagrees with the reference set, **When** the check runs, **Then** it reports each mismatched count or percentage, and a Section 6 that agrees passes.
- **FR-E.11 (upload instructions) [R+O] *(per S-15)*** — Both Code Scanning snippets in the developer guide (`DEVELOPER_GUIDE_TACHI.md:1118-1135` and `:1692-1712`) MUST upload from a run's timestamped output directory, each file with its own category. PR 1 adds the scorer and controls uploads and leaves the `threats.sarif` line as it is. PR 2 changes the `threats.sarif` line together with its identity, keeping `category: threat-model`. The batch files hold absolute local paths, so PR 1's edit also tells adopters to ignore `**/.tachi-build/`, as tachi's own `.gitignore` does (PM plan review, finding 6). → US-6b #4
- **FR-E.12 (SARIF identity fields) [R; `threats.sarif` O] *(spec S-6)*** — Every result in every tachi SARIF file MUST carry tachi's own `partialFingerprints.primaryLocationLineHash`, and no file MAY carry `runAutomationDetails`. → US-6a #4
- **FR-E.13 (correlation matching unchanged) [O] *(spec S-7)*** — Phase 3's baseline correlation MUST keep matching findings exactly as it does today. *Scenario:* **Given** the regroup pair, **When** correlation runs before and after the SARIF recipe changes, **Then** it produces the same matches. → US-6b #1
- **FR-E.14 (dispatch limits) [R+O] *(spec S-8)*** — No dispatching layer MAY have more than 20 subagents in flight, no dispatch path MAY nest more than three layers below the main session, and every re-dispatch and batch MUST run in the foreground. → US-1a #4, US-1b #5, #6
- **FR-E.15 (runtime floor) [S] *(spec S-11)*** — Every new shipped script MUST run on Python 3.9 and later, and a test MUST run the renderer's core path with `yaml` unimportable. *Scenario:* **Given** every new shipped script, **When** it is checked against Python 3.9's grammar and its core path runs with `yaml` unimportable, **Then** both checks pass.
- **FR-E.16 (the reference set) [S] *(spec S-12)*** — The reference finding set MUST be built by one shared wrapper. It accepts the table form and the drift forms that tachi's shipped samples show, and it raises on any other missing, empty or unreadable Section 7, which ends the run before any agent is dispatched (D-3's failed-completeness path). It leaves `parse_threats_findings` unchanged for its four existing callers. The tolerant baseline parser accepts the same forms. → US-1a #1, #8
- **FR-E.17 (disposition census) [S, R and O] *(spec S-14)*** — Each PR MUST carry a disposition ledger for the occurrences it changes, pinned at `b040fa1`: the four SARIF contract copies (FR-E.1), D-6(a)'s seven count rewordings, and the six platform-neutral clauses (FR-N4.1). Each occurrence gets exactly one disposition: changed, retired, or carved out with a filed issue (KB 23). *Scenario:* **Given** a PR, **When** its ledger is compared with the pinned census, **Then** every occurrence in that PR's track has exactly one disposition.
- **FR-E.18 (architecture-path carrier) [R] *(PRD D-5; PM spec review, finding 3)*** —
  - **The writer.** `/tachi.threat-model` MUST write the user's repo-relative architecture path as a body line in `threats.md`, which needs no schema bump.
  - **The readers.** The scorer and controls commands MUST read it, in this order of precedence: the override flag if given, then the body line, then `docs/security/architecture.md`.
  - **Validation.** Before it is emitted, the path is validated under NFR-10 and normalized as repo-relative, in one canonical spelling. A path outside the repository falls back to a stated value, with a warning.
  - **A missing line.** When the body line is absent, the command warns and names the override flag.
  - **Coordination.** P-2's #396 anchors bind this edit.

  → US-6a #4, #7, #8, #9
- **FR-E.19 (no reissued IDs) [R; O] *(PM plan review, ruling B)*** — Finding IDs MUST never be reissued.
  - **PR 2.** Phase 3 numbers each prefix above a per-prefix high-water mark, kept as a `threats.md` body line under P-2's anchors, with no schema bump. Shipped code, not the model, writes the mark: the larger of the baseline's mark and this run's highest ID. The first PR 2 run seeds it from the baseline's live IDs and Section 4c.
  - **The check.** `check-threat-model.py` warns (exit 5) and counts any NEW finding whose ID the baseline used, or that sits at or below the mark. It doesn't end the run.
  - **PR 1.** The scorer and the controls renderer flag `reused-id` on a NEW finding whose ID appears in the baseline `risk-scores.md`.
  - **The limit**, which ADR-050 records: an ID resolved before the baseline run, which the baseline no longer lists, can still be reissued once.

  → US-6a #10, US-6b #5
- **FR-E.20 (correlation in the message) [R; O] *(PM plan review, ruling C)*** — Each correlated result's `message.text` MUST end with one sentence that names its group, plus either its primary (on a peer) or its peers (on a primary, up to a cap the shared reference sets, then a count). The message isn't identity (D7), so a regroup changes the text and never a key. → US-6a #11

### Non-Functional Requirements

- **NFR-1: compatibility.**
  - **A small-run oracle**, run in a scratch clone, covers each shipped example that has scorer or controls output, the PRD's rule. The renderer's output keeps every section and field. It is compared on decoded values (ADR-050 D3), and every value diff is attributed to one of four classes:
    - a flagged value (corrected, or retagged under ruling A);
    - D-5;
    - S-2's reorder of rows with equal scores;
    - text the renderer takes from the reference set where today's agent paraphrased it: a field that ADR-050 D2 has the renderer take from the reference set, whose rendered value equals that finding's reference-set value on decoded values, after the documented truncation. A diff in such a field that fails this test is unattributed (PM confirmation, ruling 4).

    The three examples whose files use a drift form are drift-form cases that assert S-12(a) to (d).
  - **Parsers keep working.** They read by header name. A round-trip test checks that the renderer's output, parsed by `tachi_parsers`, equals the renderer's input.
  - **Old inputs render the same.** The PDF and the infographics render them byte-identically.
  - **Schemas change additively.** The frozen enum and the ceiling are unchanged (NG7).
- **NFR-2: determinism, imports and arithmetic.**
  - **Byte-stable output.** The renderer's output is byte-stable for the same input, and the scoring date is an input, not the clock.
  - **Imports.** The core path imports and needs only the standard library, at load time and at run time (S-11). S-13 enforces the load-time half, with the renderer and its helpers on its list. PyYAML stays optional, for the PDF attestation page only. The taxa are sourced without PyYAML (research item 15).
  - **Runtime.** Python 3.9 and later; bytecode suppressed (ADR-049 D8).
  - **The arithmetic ADR-050 pins:**
    - half-up `Decimal` rounding on the stored one-decimal inputs (Python's `round()` gives 4.5 for the documented 4.55 → 4.6);
    - CVSS Roundup by FIRST's integer method, kept separate from half-up rounding;
    - inclusive band boundaries, applied after rounding to one decimal;
    - ADR-017 D2's largest-remainder rule for percentages;
    - the review-date and SLA rules.
  - **Constants.** The scoring constants are embedded, with a drift test against `schemas/risk-scoring.yaml` (R-32), and the shipped CVSS calculator keeps FIRST's 16 reference examples as a self-test (KB 26).
- **NFR-3: privilege and confinement.**
  - **No agent gains a tool** (NG8). The threat agents keep Read, Glob and Grep, and the commands keep `{description}` (guard C5).
  - **Intermediates.** Every file an agent writes as an intermediate (parts, dispatch records, briefs) sits under the run's `.tachi-build/`, the ADR-049 D7 precedent. `$TMPDIR` holds only files that scripts create through `tempfile`.
  - **The declarations that change:**
    - ADR-049 D7, by a dated note;
    - the Writes cells in `CLAUDE_PERMISSIONS.md` §8.3 and §8.4, and §8.5's "Written by" column;
    - the `/tachi.compensating-controls` row, which gains `python3` under "Bash it instructs" and "Child processes";
    - the runbook's §5 table.

    The session profile stays unchanged. R-27 covers re-validation, for each PR that changes a write set (§ The split).
  - **Every new path is declared** (plan input P-6). Guard C7 can't see an undeclared path, so review enforces declaration, and `test_write_confinement.py` enforces script writes.
- **NFR-4: cost.**
  - Below the batching threshold, each agent is invoked once.
  - The PR records token usage and wall time for the fixture runs and for one shipped example (SC-8).
- **NFR-5: observability.** Each stage writes one small JSON stage record (counts, batches, overflow events and retries), in a form #399's manifest can ingest.
- **NFR-6: public hygiene.**
  - Issues, the PRD, this spec, PRs, commits and the CHANGELOG describe the defects generically, with no real-world findings, threat text, IDs or report content.
  - Fixtures are synthetic.
  - Public text never lists which agent specs or sections the private N3 fix touches.
- **NFR-7: CI.**
  - **Gates.** There are three, with lock-step wiring (FR-E.5).
  - **Commit first.** The gated harnesses clone the committed HEAD.
  - **Known failures.** About 19 failures outside the gate pre-exist and are known, and #365's reds are known.
  - **Pre-state.** T001 records every gate's literal pre-state totals (KB 15, 16).
  - **One push per wave.** Each push costs about 33 minutes on two operating systems.
- **NFR-8: images.** Re-rendered example PNGs are never committed (#365), and commits stage explicit paths only.
- **NFR-9: portability.** Any command or shell change runs on bash 3.2 and on both GNU and BSD userlands.
- **NFR-10: the trust boundary of the shipped scripts.** The scripts are the renderer, the planner, the assembly steps, the `threats.md` joiner, the `threats.sarif` generator, the chain script and the checks. Every agent-authored file they read is untrusted input:
  - parts and dispatch records;
  - `threats.md` and its parts;
  - `risk-scores.md`, which is the controls renderer's input;
  - the tree files and the manifests;
  - the baseline run's `risk-scores.md`, `compensating-controls.md` and SARIF files.

  The rules:
  - **Strict JSON.** JSON inputs are parsed against a closed, versioned key set, with types and ranges. Unknown keys, NaN, Infinity, duplicate IDs and IDs outside the batch's list are rejected.
  - **IDs before paths.** The allow-list is applied before an ID becomes part of a path, with a resolved-path containment check as a backstop. An ID is one of the prefixes S, T, R, I, D, E, AG, AGP, LLM, OI, MI and TE, a hyphen, and ASCII digits `[0-9]`, matched against the whole string: never `\d`, which accepts non-ASCII digits, and never `$`, which accepts a trailing newline (KB 24; ADR-050 D3's identifier module).
  - **Paths come from the command**, never from file content. The exceptions are three paths read from files: `baseline.source`, `risk-scores.md`'s `source_file`, and the architecture path in `threats.md`'s body. Each is validated as KB Entry 24 prescribes: a regular file, not a symlink, under the working directory, compared by resolved identity.
    - **Expected names.** `baseline.source`, `source_file`, and the baseline files read from that directory must also have the expected name.
    - **The architecture path** has no fixed name, so its name check is replaced by a match against the run: its basename must equal that of the architecture snapshot that `/tachi.threat-model` copied into the run directory, which keeps the source's basename. ADR-050 item 7 designs the check, including the case where the snapshot is absent. The path is also normalized as repo-relative, in one canonical spelling.
    - **Precedence.** The command's override flag takes precedence.
  - **No forged structure.**
    - `|`, backticks and newlines are escaped in table cells, and SARIF's string rules are followed.
    - After rendering, no prose line begins with `#` or `|`.
    - Raw HTML is escaped.
    - Code snippets use a fence longer than any backtick run inside them.
    - Control bytes are refused before any write.
  - **Limits.** Each file has a size cap. There is no `eval` or `exec`, and writes go only under the output directory (ADR-049 D5).

  Tests seed a stale part, a forged heading and a fence break-out. The Step 7 security review names each new script.

### Key Entities

The Terminology table defines each entity. Their relationships:
- **Reference finding set** (from `threats.md` Section 7). Every parity check reads it: rows, SARIF N/N, `.md`–`.sarif` agreement, the tree count and Section 6. Section 4c supplies the RESOLVED set.
- **Batch plan** → **Batches** → **Part files.** A plan has an ID and input digests. Each batch has an ID and a list of finding IDs. Each part carries both IDs, and the renderer accepts only the current plan's parts.
- **Dispatch record** → **ID map** → **`threats.md` finding.** The ID map gives each record finding exactly one disposition, and each final finding exactly one **provenance entry**.
- **Carried finding**: its inputs are inherited and its derived fields recomputed. Each change produces a **flag** with a cause, in the `.md` and in the SARIF (ADR-050 item 9 decides how they appear).
- **SARIF result**: its matching key is a constant tool name per file, the upload category, the category's `ruleId`, tachi's own per-finding hash, and the repo-relative architecture path.
- **Outcome record** (one per run) and **stage record** (one per stage). Both are small and machine-readable.

### Key Artifacts

| Group | Item | New / modified | Path | Track |
|---|---|---|---|---|
| A | K4.1, K4.2, N4.1–N4.7, FR-O.1 | modified | `.claude/agents/tachi/orchestrator.md` | S (N4.1, N4.4 text), O |
| A | K4.1, FR-O.1, N4 | modified | `.claude/skills/tachi-orchestration/references/{output-schemas,dispatch-rules,baseline-correlation}.md`, `templates/tachi/output-schemas/threats.md` | O |
| A, E | K4.1, FR-O.1, N4, FR-E.18 | modified | `.claude/commands/tachi.threat-model.md` | S (command text), R (carrier), O |
| A | K4.2 | modified | `.claude/skills/tachi-shared/references/attack-chain-patterns-shared.md` | O |
| A | K4.2, FR-O.1, N4.5–N4.6, K4.1b | **new** | the chain script, the `threats.md` part joiner, the `threats.sarif` generator, and the provenance, completeness and outcome checks | O |
| B | K5 | modified | `.claude/agents/tachi/{threat-report,attack-tree-delta}.md`, `.claude/skills/tachi-threat-reporting/references/*`, `templates/tachi/output-schemas/threat-report.md` | S (K5.4 text), O |
| B | K5.1–K5.7 | **new** | the report assembly step and its checks | O |
| C | K6, N14, N15, N16 | modified | `.claude/agents/tachi/risk-scorer.md`, `.claude/commands/tachi.risk-score.md`, `.claude/skills/tachi-risk-scoring/references/*`, `templates/tachi/output-schemas/risk-scores.md` | R |
| C, D | D-2 | **new** | the renderer modules (core, scorer, controls, scoring rules), the CVSS module, the batch planner, and the part loader and validator | S (core, CVSS, planner, loader), R |
| D | K7, K8 | modified | `.claude/agents/tachi/control-analyzer.md`, `.claude/commands/tachi.compensating-controls.md`, `templates/tachi/output-schemas/compensating-controls.md`, `.claude/skills/tachi-control-analysis/references/*`, `adapters/claude-code/agents/references/sarif-generation.md` | R |
| D, A | K8.2, K4.1 | modified | `scripts/tachi_parsers.py`, `scripts/extract-report-data.py` | R (K8), O (K4.1 readers) |
| E | FR-E.1, FR-E.3, N4 templates, the roster, the end marker | **new** and modified | the shared references; `sarif-specification.md`; `finding-format-shared.md`; `coverage-requirements.md` | S |
| E | FR-E.4 | **new** | the fixture generator and the fixture tree under `tests/scripts/fixtures/` | S |
| E | FR-E.5 | modified | `INSTALL_MANIFEST.md`, `tests/scripts/test_install_manifest_completeness.py`, `tests/scripts/test_write_confinement.py`, the three workflows | S, R, O |
| E | NFR-3 | modified | `docs/standards/CLAUDE_PERMISSIONS.md` §8.3–§8.5, `docs/guides/ISOLATED_OPERATION_TACHI.md` (§5 and its header) | R, O |
| E | FR-E.11 | modified | `docs/guides/DEVELOPER_GUIDE_TACHI.md` (two snippets) | R, O |
| E | D-2, #357 | replaced or fenced (ADR-050) | `scripts/generate-threats-sarif.py`, `scripts/generate-risk-scores-sarif.py`, `scripts/sarif_common.py` | R, O |
| E | P-1 | **new** and modified | `docs/architecture/02_ADRs/ADR-050-*.md`; dated notes or amendments in ADR-013, 017, 018, 020, 026, 046, 048 and 049 (ADR-047 is unchanged, because SV-2b is carved) | S |
| E | FR-C.1 | modified | `adapters/claude-code/agents/*` copies (header), `adapters/claude-code/README.md` (warning) | S, R, O |

### Consequence scope

These consumers read what the bundle changes. They form T001's pre-state census (P-10):
- **Readers of the four renderer-owned files:**
  - `tachi_parsers` (`parse_risk_scores_findings`, `parse_risk_scores_severity`, `parse_compensating_controls_md`);
  - `extract-report-data.py` and `extract-infographic-data.py`;
  - the `golden/` and `report_data/` fixtures and the coverage pins;
  - the six byte-gated example PDFs (#365).
- **Readers of `attack-chains.md` and the Phase 3.5 outcome:**
  - the report agent;
  - `detect_artifacts` and `prepare_attack_chains`;
  - `main.typ:108` and `:275`;
  - `test_attack_chains.py` and `test_attack_chain_extraction.py`.
- **Tests that pin the regeneration-tier generators:** `test_affected_assets_wiring.py` (SC-006, FR-014), `test_owasp_2026_contract.py` and `test_tachi_parsers.py:611-621`.
- **Example-tied tests:** the `agentic_app` extractor fixture's 9.1, which five golden JSONs depend on, is a named exception (KB 26).
- **Shipped examples:** they regenerate through the renderer under #364 (NG5).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

| # | Criterion | Track | Baseline | Target |
|---|---|---|---|---|
| **SC-1** | Each changed stage on the synthetic large fixture | R (scorer, controls); O (threat model, report) | Measured on the fixture at v4.48.4: token estimates, plus one scorer run (D-7) | Complete N/N outputs, and 0 hand-assembled files. Record completeness (FR-N4.6) and the tree count (FR-K5.5) pass |
| **SC-2** | Phase 3.5 | O | Nothing recorded; a skip looks like zero | The outcome is recorded in 100% of runs, and the post-run check catches a missing or inconsistent record and records it as skipped, with the reason (R-24). The chain fixture forms chains. With the chain script, the chain-script output (titles and narratives excluded) is byte-identical on a fixed finding set, offline; without it, the algorithm and counts are recorded (R-19) |
| **SC-3** | On-contract execution in the fixture runs (structure-only transcript audit, plus the in-run signals) | O (measured; PR 1 records its smoke run) | Run B: 33 stand-ins; outputs rendered by orchestrator-written scripts; one code hand-back | 0 `general-purpose` dispatches; 0 unshipped scripts run; 0 program files written; 0 code hand-backs; every rendered output stamped; only declared paths in the output directory |
| **SC-4** | Inherited scores on the seeded baseline, decidable cases | R | Errors carried forward silently | 100% of seeded composite, band and vector errors are corrected and flagged. 100% of seeded out-of-range reachability values (unambiguous labels) are flagged. 0 documented exceptions are flagged. N17-dependent cases are reported as unchecked. Rounding-only differences are counted, not flagged, unless they move a band. 0 carried scores change because of a regroup alone. 100% of seeded peer divergences are flagged. The legacy-format baseline and the tagged case are handled under R-26 and R-25 |
| **SC-5** | Controls report | R | Drifting tables; totals ≠ sum of rows; blank recommendations | One schema in every band table; totals equal the sums of the rows; `.md` and `.sarif` agree; 0 unjoined Section 4 recommendations; #373's parsers read the corrected and the pre-fix fixtures. In PR 1, shown on the fixture's live runs (R-34) |
| **SC-6** | SARIF identity under the matching key, per file, on the baseline-aware regroup pair (offline) | R (scorer, controls); O (`threats.sarif`) | Scorer and controls alerts churn on every run; regrouped `threats.sarif` results drop out | For each file: 0 still-present findings lose their key; an unchanged re-run's keys are identical; no two present findings share a key; the three (tool, category) pairs differ |
| **SC-7** | Release | S, R, O | — | Each PR yields a `fix(374)` patch release whose notes carry what "Release notes, per PR" (below) lists |
| **SC-8** | Small runs | R | One v4.48.4 run of the scorer and controls on one shipped example's `threats.md` (D-7) | The small-run oracle passes. For `/tachi.risk-score` and `/tachi.compensating-controls` separately, output tokens are at most 10% above that stage's v4.48.4 baseline. **The runs:** the same shipped example, named before W1's baseline run and below both stages' batching thresholds, at the adopter default effort, under the same session conditions (if the post-fix run doubles as R-27's smoke run, the baseline also runs under the profile). **Output tokens** are what Claude Code reports for the whole stage (the command's turns and every subagent, thinking included), read from the session's usage records. **Reporting:** the PR records each stage's delta, and public text claims a stage got cheaper only if its delta is below zero. **Overage:** a stage still over 10% after TW-L2's second attempt goes back to the PM before PR 1 merges. Wall time is recorded, not gated (P-7, as ruled) |
| **SC-9** | Live confirmation *(lagging; tracked outside this feature)* | — | — | The next large real-world run completes every stage with no stand-ins, no hand assembly and no code hand-back |

### Release notes, per PR (R-1, binding)

- **PR 1 carries all five §8 items.**
  - **Item 1 (SARIF)**, for the scorer and controls files:
    - their one re-key event, their stable identity from then on, the alert count, and the per-file tool names and categories;
    - advice to adopters whose architecture file isn't at `docs/security/architecture.md`: re-run `/tachi.threat-model` first, or pass the override flag (FR-E.18);
    - the ID-reuse exposure until PR 2, and the `reused-id` flag that marks it (ruling B);
    - each correlated result's message now names its group (ruling C).
  - **Item 2 (runs that stop)**:
    - the new stops and their remedies, including the unreadable-Section-7 stop (S-12(c)), and the stop when inputs change during a run (ADR-050 D6), whose remedy is to re-run;
    - a Python 3.9+ renderer now writes the scorer and controls outputs, so `/tachi.compensating-controls` needs `python3` for the first time.
  - **Item 3 (scores)**, as §8 states it, plus:
    - asset tags now apply to carried findings, so on the first run after upgrading their scores can rise, flagged `retagged`, and some move up a band;
    - ruling A's review-date rule for tag-driven changes, beside the correction rule.
  - **Item 4 (rendering)**, as §8 states it, with its PR 1 caveat for controls Sections 2 and 4 (R-34), plus:
    - both files move to schema 1.1, additively: `risk-scores.md` gains §2a, the `Flags` column, and §6 with the scoring inputs; the controls file gains K8's columns, `CF` and §7;
    - the Executive Summary of `risk-scores.md` becomes one templated sentence;
    - the batch files under `.tachi-build/`, which adopters should ignore in version control (PM plan review, finding 6).
  - **SC-8.** A stage is claimed cheaper only as P-7 allows: its measured delta is below zero.
  - **Item 5** says what stays fragile until PR 2:
    - large threat-model runs, and the report, can still overflow;
    - the N4 text now forbids stand-ins, but Phase 2 re-dispatch ships only in PR 2, so a large threat-model run that used to finish by improvising may stop or come out incomplete;
    - Phase 3.5 can still be skipped silently;
    - `threats.sarif` alerts still churn.
- **PR 2 carries items 1, 2 and 5**, each for its own scope. Item 1 adds that IDs are no longer reissued, so numbering can skip (ruling B). Item 5 adds that SV-2b is carved: `threats.md`'s tables and Section 6 stay model-authored (Section 6 is checked), and the dispatch records are manifests.
- **Both PRs, the narrative fallback** (PM confirmation, ruling 2):
  - Each PR's notes cover the stages that PR changes.
  - They name each field's fixed sentence, the `input:<field>:narrative-fallback` flag, and the `input:<field>:truncated` flag for prose cut at its length limit (Architect re-review RR2).
  - They link the follow-up for any stage whose W5 fallback rate is above 10%.

---

## Scope Boundaries & Split Valves

### In scope

D-1's bundle: #374's K4–K8, and #397's N4, N12, N14, N15 and N16. Three small adjacent items fold in:
- #408's body-instruction option (R-14);
- #412's `informationUri` fix (R-16);
- #357, if the renderer subsumes its generator.

#409's check and R-14's run-time bound drop under R-34 (FR-E.8).

### The split (R-34, pre-fired)

- **PR 1** ships Tracks S and R, and says "Refs #374".
- **PR 2** ships Track O. It is based on `main`, not on PR 1's branch, so that merging PR 1 with `--delete-branch` can't close it (KB 25). After PR 1's squash, PR 2 merges `origin/main` in and checks the full tree (KB 18). #374 closes with PR 2.
- **Claims** follow S-5.
- **#397 bookkeeping.** N14, N15 and N16 are ticked at PR 1, and N4 and N12 at PR 2 (N12 unless SV-3 fires).
- **R-27, per PR.** R-27 applies to each PR that changes a write set. PR 1's smoke run covers the commands it changes. PR 2 either repeats the smoke run for the commands it changes, or marks the runbook's "Last validated" header as predating PR 2.

### Split valves

Definitions are in PRD §10:
- **SV-1** (K4): fires only on TW-K4(b).
- **SV-2a**: never carved.
- **SV-2b** (`threats.md` tables in code): may be carved.
- **SV-3**: fires only on its technical trigger at ADR-050, never for schedule (R-23).
- **SV-4**: pre-fired.

**Budget carves**, in reverse PM priority: SV-2b, then SV-1, then TW-R's fallback (already fired), then SV-4 (already fired). Under R-34, if TW-0 or TW-ESC fires on PR 1, no carve is left, and the decision goes back to the PM.

**Never carved:**
- FR-K4.1 and FR-K4.1b;
- FR-N14.1;
- the risk-scores renderer;
- FR-N4.5 to FR-N4.7;
- D-5's membership and identity for all three files, except through SV-3.

### Out of scope

- **NG1 to NG10**, as the PRD states them:
  - the N3 reference-loading track;
  - the scoring/delta bundle (N9–N11, N17), with R-25 settling N17(a) here;
  - the hygiene items;
  - #356, unless R-13 folds it in;
  - example and baseline regeneration (#364, #365);
  - #399's archive and manifest;
  - scoring semantics;
  - new agent tools;
  - committing real-world output;
  - the other adapters.
- **S-16's follow-ups**, filed as issues at delivery.

---

## Rulings

### Made in this spec

**S-1 — Batching thresholds (answers OQ-5).**
- **The unit per stage:**
  - scorer and controls: open findings in the reference set;
  - trees: the Critical and High trees to regenerate;
  - report: one part per section, with the per-finding sections batched by findings;
  - `threats.md`: one part per section, with table sections split by rows;
  - Phase 2: one dispatch per agent, re-dispatched per component on overflow.
- **The budget.** A batch is sized so that its largest single write (a part file, a tree file or a `threats.md` part) is expected to be **at most 8,000 tokens**, and all its writes together **at most 32,000 tokens**. 8,000 tokens is a quarter of a 32,000-token response, the smallest documented default cap. Thinking counts against the cap, so this leaves at least three quarters of the response for reasoning at `effort=max`.
- **Calibration.** At W0, the plan measures the output cost per unit (per finding, per tree, per table row) on the fixture. ADR-050 item 6 records that measurement and the batch size it gives for each stage. The sizes are constants in the planner, not adopter settings. *Planning assumption, until the measurement replaces it:* about 40 findings per scorer batch, 30 per controls batch, and 12 trees per tree batch.
- **Below the threshold**, the stage invokes its agent once (NFR-4).
- **Acceptance** is the live matrix at both effort levels (D-7, R-18). An overflow in a live run is handled by the dispatching layer (narrower, with capped retries) and recorded (NFR-5), and TW-L2's dispositions apply.

**S-2 — One total order on finding IDs (OQ-6).** IDs are ordered first by prefix rank, `S`, `T`, `R`, `I`, `D`, `E`, `AG`, `AGP`, `LLM`, `OI`, `MI`, `TE`, then by their numeric suffix as an integer, so `T-9` comes before `T-10`. Every rule that says "lower finding ID", or sorts by ID, uses this order. It is defined once in shared code and once in a shared reference.

**S-3 — Chain rules (OQ-6).** Items (d), (f) and (g) change what users see. The PM amended all three at the spec review (2026-11-22), and the amendments are folded in verbatim. The PM accepted S-2, (b) and (c) as written, under R-21.
- **(a) One algorithm.** The orchestrator's Phase 3.5 steps are canonical: index, candidate links, assembly, deduplication, filter, rank, IDs and chain-breaking. `attack-chain-patterns-shared.md` is rewritten to match. Two of its claims go: its tie-break on `chain_id`, which is assigned only after ranking, and its claim that no tie is possible.
- **(b) The link test is unchanged.** A link needs a structural connection (direct data-flow lineage, or reachability through the transitive closure) and a valid entry in the transition table, among STRIDE findings only. Any change to which findings can link, including dropping or narrowing the transitive-closure test (ADR-050 item 13), is an R-21 change, and it goes to the PM before it is built.
- **(c) Deterministic iteration.** Start findings are taken by severity, highest first, then in S-2 order. Extensions are considered in the same order, replacing "lower finding ID".
- **(d) Redundancy** *(amended by the PM, 2026-11-22)*.
  - Chains with identical finding sets keep the higher-ranked one.
  - A chain whose ordered findings form a contiguous run of another consolidated chain (at its start, middle or end) is folded into that chain and isn't listed. This includes the tail of a longer chain. Under greedy assembly any step can also start a chain, so a tail shows no attack path that the longer chain doesn't.
  - Chains that converge on a shared tail from different initial exploits, where neither is a contiguous run of the other, are distinct attack paths, and both stay.
  - **Counts.** The *candidate* count is every chain assembled. The *consolidated* count is what remains after deduplication, the filter and folding. The *surfaced* count is the number of chains shown in full (S-3(f)). A chain that is deduplicated, filtered out or folded counts only as a candidate.
- **(e) Ranking is total.** Chains are ranked by max severity, descending; then by layer count, descending; then by their ordered finding IDs, compared element by element in S-2 order. Identical sets are deduplicated, so no two chains tie.
- **(f) Surfacing** *(amended by the PM, 2026-11-22)*. Walk the consolidated chains in rank order, and surface each one unless an already-surfaced chain ends at the same terminal-impact finding. Stop at five. When fewer than five distinct terminal impacts exist, fewer chains surface. Each surfaced chain records how many other consolidated chains end at its terminal-impact finding, and the report prints that number with the chain, so a convergence point stays visible. The report agent's "top 5 by ranking" (`threat-report.md:232`) changes to match.
- **(g) The bound** *(amended by the PM, 2026-11-22)*. `attack-chains.md` holds, in this order:
  - every surfaced chain in full;
  - then one compact row for each other consolidated chain, in rank order and at most 100 rows. Each row gives at least the chain's ordered finding IDs, its max severity and its chain-breaking target;
  - then one line stating how many consolidated chains aren't listed.

  In `chains written (N)`, N is the consolidated count. The record also carries the candidate and surfaced counts, and the file's frontmatter counts match the record. FR-K4.1b passes when the file accounts for exactly N chains: its full chains equal the surfaced count, its rows equal the smaller of 100 and N minus the surfaced count, and its last line gives the rest. An offline test with more than 105 consolidated chains exercises the cap, the remainder line and the check. The bound amends ADR-020's "all chains recorded" (P-1 records the amendment). The model writes titles and narratives for the surfaced chains only (R-19).

**S-4 — The fixture (answers OQ-7).**
- **One generator.**
  - It is stdlib-only, with a fixed seed.
  - Every choice is derived from `random()` or from a hash of a label, never from `choice`, `sample` or `randint`, whose sequences Python doesn't guarantee across versions.
  - Its outputs are byte-identical on Python 3.9 to 3.13.
  - Component names are synthetic. Some carry digits (for example `worker-2` and `s3-archive`), so the numeral and slot rules are exercised (Architect plan review, F1).
- **One base set.**
  - **The architecture:** 25 components over at least four trust zones and all seven MAESTRO layers. It includes at least two LLM components and two agentic components, so every threat agent dispatches.
  - **The baseline run directory:** its `threats.md` holds at least **390 open findings**, raised until the sizing check passes, up to a ceiling of **450**, across all 12 prefixes, with at least 40 Critical. If the check still fails at the ceiling, the fixture is adjusted once, as TW-L3 does it. It has at least 20 correlation groups, one of them cross-category, and at least 5 RESOLVED findings in Section 4c. Its chain material forms at least three chains, with at least two distinct terminal impacts. The directory also holds `attack-trees/` with its manifest, `risk-scores.md`, `compensating-controls.md`, and all three SARIF files.
  - **Why one set.** It is at or above both of D-7's sizes (about 325 findings for the scorer input and about 390 for the orchestrator's outputs). So it serves both the precomputed scorer and controls input and the baseline-aware threat-model run.
- **Variants:**
  - **seeded-error:** for each prefix, at least one each of: a wrong composite, a wrong band, an out-of-clamp vector score, an out-of-range reachability value with an unambiguous label, and a missing vector. Plus the documented exceptions as controls (clamped scores, R-25 outcomes, rounding-only differences) and N17-dependent cases;
  - **legacy-format:** no sub-score tables; vectors on only some markdown rows; full vectors in the SARIF; one markdown-versus-SARIF disagreement; and seeded composite and vector errors (R-26);
  - **tagged:** a tagged component with a finding assessed above 9.2, one that the tag elevates, and a carried legacy finding that stores only an elevated score above 9.2 (R-25). It also covers ruling A's tag-driven band changes in both directions, and their legacy case;
  - **id-reuse:** one case for each PR. For PR 1, a NEW finding whose ID the baseline `risk-scores.md` used. For PR 2, a baseline whose high-water mark sits above its live IDs (ruling B);
  - **ties:** a band-moving composite tie, a rounding-only tie that doesn't move the band, and a residual tie (R-11);
  - **regroup pair:** two runs in which correlation regroups carried findings and changes a primary. The pair includes an UNCHANGED peer whose carried score differs from its new primary's, a NEW peer and an UPDATED peer, plus an unchanged re-run;
  - **chain-cap:** chain material that yields more than 105 consolidated chains, for S-3(g)'s offline test;
  - **stub codebase:** a small synthetic code tree with detectable controls for some findings;
  - **gated subset:** Mermaid-free and small, for gated CI. Tests may pass a smaller batch size through the planner's internal interface, so that every batched path still runs at least twice.
- **Sizing check.** The generator's test asserts two things:
  - each targeted single-response output is at least twice the 64k cap, by a stated estimator (UTF-8 bytes ÷ 4);
  - every batched path gets at least two batches at S-1's sizes.
- **Use in tests.** Tests regenerate into a temporary directory and compare byte for byte with the committed copy. They never rewrite tracked files.

**S-5 — Track tags and PR claims.** Every story, requirement and criterion carries S, R or O.
- **PR 1** ships S and R, and claims:
  - SC-4, SC-5, SC-7, SC-8, US-3 and US-5;
  - SC-1 and US-1a, for the scorer and controls stages;
  - SC-6 and US-6a, for those stages' two SARIF files.
- **PR 1 doesn't claim:**
  - SC-2, SC-3, US-1b, US-2, US-4 or US-6b;
  - the threat-model or report stages;
  - a wholly rendered controls file;
  - any `threats.sarif` change.
- **Track O text committed before the split** ships in PR 1 only if it is inert and readable by today's readers. Otherwise it waits for PR 2.

**S-6 — SARIF identity fields (refines D-5 for ADR-050 item 7).**
- **Tachi's own hash.** Every result in all three files carries tachi's own `primaryLocationLineHash`. It is computed from a stable per-finding key, is unique among the file's present findings, and never includes model prose.
  - **Why it is never left to the upload action:** the action would hash a line of the user's architecture file. Editing that line would then re-key the alert, and identical lines would collide.
- **No `runAutomationDetails`.** No file carries it, so the upload step's `category` input sets each file's category, which R-33's distinct pairs need. A file's own `automationDetails.id` would override the input.
- **The location.** `locations[0]` is the architecture file at its repo-relative path, in one canonical spelling decided by file identity (KB 24).

**S-7 — Correlation matching is unchanged.**
- **Phase 3's match keys stay as they are.** Baseline correlation keeps its own keys, computed from `threats.md` as today (ADR-018; `baseline-correlation.md:78-106`), and the D-5 recipe is a separate function.
- **A test pins it.** The regroup pair's correlation outcome must not change when the SARIF recipe does.
- **Legacy hashes.** Hashes stored in a legacy baseline SARIF are never used for matching.

**S-8 — Dispatch limits.** Every dispatching layer stays inside Claude Code's defaults:
- at most 20 subagents in flight. The orchestrator therefore sends Phase 2 re-dispatches in waves, and so does a command with its batches;
- no path nests more than three layers below the main session;
- every re-dispatch and batch runs in the foreground, with the dispatcher waiting for it, because orphaned background children have outlived their parent (KB 22).

The plan states each path's depth.

**S-9 — Spike the overflow signals before building the detector.**
- **The spike.** Before FR-N4.7's detector is built, a spike under the published session profile plants four failure classes: a stop mid-reasoning, a stop mid-output, a stall, and an empty return. It records, in a layout table, what the dispatcher observes for each (KB 25). The detector is built against that table.
- **The end marker.** The marker that closes a complete Phase 2 return is defined in the shared finding-format reference, which every threat agent already reads. No protected detection file is edited (the F-142 invariant, KB 6). If one must change, its carve-out is a named task.

**S-10 — The scope of prevention.**
- **What prevents.** FR-N4.1's body text (#408's option) is the prevention.
- **What isn't used.** An `Agent(...)` type list in an agent's `tools:`, because Claude Code ignores it inside subagent definitions.
- **Follow-up.** A settings-level `Agent(general-purpose)` deny rule in the isolated-operation profile, because the profile is pinned (NFR-3).
- **Dropped.** #409's static check, under R-34.

**S-11 — The runtime floor.** Every new shipped script runs on Python 3.9 and later, with no syntax or standard-library API newer than 3.9. S-13 checks module-level imports only, so a test also runs the renderer's core path with `yaml` made unimportable.

**S-12 — The reference set, the drift forms and the oracle** *(amended at the PM's spec review, finding 1)*.
- **The wrapper.** One shared wrapper around `parse_threats_findings` builds the reference set. The parser itself is unchanged, because the extractors rely on its `[]`-with-a-warning behavior.
- **(a) Drift forms are read.** The reference-set wrapper and the tolerant baseline parser accept the forms that tachi's shipped samples show: Section 7 as a numbered list of bolded IDs, and `## Section N: Title` headings. The four samples serve as read-only test inputs.
- **(b) Missing values.** Where an accepted form lacks a value a stage needs (for example, Section 7's Status column), the stage derives what it can from the baseline. It scores the rest fresh, flags each of those findings with the cause, and records them in the stage record. It never stops for this.
- **(c) Anything else stops the run early.** Any other unreadable Section 7 ends the run before any agent is dispatched. The error names the file, the section, the expected form and the remedy. This is D-3's failed-completeness path, not a new one.
- **(d) A baseline file that is present but unreadable** is treated as missing under D-6(c). The stage scores fresh, records why, and warns that the baseline's human overrides weren't carried.
- **(e) The oracle** keeps the PRD's rule: every shipped example with scorer or controls output (NFR-1). The three examples whose files use a drift form (`consumer-agent-app`, `predictive-ml-app`, and `maestro-reference`'s scorer file) become drift-form cases that assert (a) to (d).
- **(f) Release notes.** PR 1's notes name the new stop and its remedy (§8 item 2).

**S-13 — One source for asset tags.**
- **The rule.** The asset-modifier step and the SARIF `affected_assets` property read a finding's tags from one named source, which ADR-050 item 2 names.
- **When that source is stale or absent,** for example when `--output-dir` skips the populate step, the renderer recomputes the tags through the populator's own function. When it can't, it scores without the asset elevation, warns that the tags weren't applied, and records the cause in the stage record. It never stops the run for this, and it never mixes sources *(amended at the PM's spec review, finding 7)*.
- **Wording.** F-302's NFR-2 wording, "does not affect scoring" (`risk-scorer.md:528`), is reworded to match.

**S-14 — The disposition census.** Each PR carries a ledger, pinned at `b040fa1`, for the occurrences in its track:
- the four SARIF contract copies;
- D-6(a)'s seven count rewordings;
- the six platform-neutral clauses.

Every occurrence gets exactly one disposition: changed, retired, or carved out with a filed issue (KB 23).

**S-15 — The upload snippets, per PR.**
- **PR 1** adds the scorer and controls uploads, each with its own category, and leaves the `threats.sarif` line unchanged.
- **PR 2** changes the `threats.sarif` line together with its identity.

Each file therefore re-keys at most once, and each PR's release notes say which files re-key (§8 item 1).

**S-16 — Follow-ups, kept out of scope.** Each is filed as an issue at delivery:
- the architecture snapshot keeps the source file's basename, while the populator and the downstream commands assume `architecture.md` (research item 11);
- an `Agent(general-purpose)` deny rule for the isolated-operation profile (S-10);
- the architectural escalation that dispatches Phase 2 from the command layer (RK-4, TW-CTX).

The KB entry on output-cap overflow isn't a follow-up. It is part of delivery.

### PM rulings from the spec review (2026-11-22; binding for `/aod.plan` and `/aod.tasks`)

The PM signed APPROVED_WITH_CONCERNS, with 13 findings (2 HIGH, 5 MEDIUM, 6 LOW). The rulings and required changes are folded in, verbatim where the PM gave text:
- **S-3(d), (f) and (g):** AMENDED, and folded verbatim above. FR-K4.1b, FR-K4.2, US-2 #1, #3 and #6, and the Terminology's outcome record are aligned with them (findings 2 and 11).
- **S-2, S-3(b) and S-3(c):** ACCEPTED under R-21. Any change to the link test, the transitive closure included, still goes to the PM before it is built.
- **Finding 1 (HIGH):** S-12 amended.
  - The shipped drift forms are read.
  - Missing values are derived from the baseline, or scored fresh and flagged.
  - Anything else stops the run before dispatch.
  - An unreadable baseline file is treated as missing.
  - The oracle keeps the PRD's rule.

  US-1a #8, FR-E.16, NFR-1 and the edge cases follow.
- **Finding 2 (HIGH):** FR-K4.1b checks the file against S-3(g)'s accounting rule, with an offline test above 105 chains.
- **Finding 3:** FR-E.18 states the carrier's mechanics, and US-6a #7 to #9 cover each precedence step. The Key Artifacts row and P-2 follow, and PR 1's notes carry the re-run advice.
- **Finding 4:** "Release notes, per PR" defines what each PR's notes carry (SC-7).
- **Finding 5:** R-27 applies to each PR that changes a write set (§ The split).
- **Finding 6:** NFR-10 restores the expected-name check and states the architecture path's replacement check.
- **Finding 7:** S-13 and FR-N16.2 never stop the run for missing tags.
- **Findings 8 to 12:**
  - the controls agent's parse errors get a defined place (FR-K7.4);
  - the stories' priority sentence is corrected, and US-6b is P1;
  - every live scenario is marked `[MANUAL-ONLY]`, with its offline half;
  - US-2 #5 compares the chain script's output without titles and narratives;
  - S-4's base set has a ceiling of 450 findings.
- **Finding 13:** the plan's call (P-11).
- **Condition 4:** the unpriced additions, finding 1's reader work included, count toward the TW-0 of the PR that carries them, and a PR 1 projection above 9.0 days comes back to the PM (see Assumptions).
- **Full review:** `.aod/results/product-manager-374-spec.md`.

### PM rulings from the plan review (2026-11-22; binding for `/aod.tasks` and the build)

The PM signed the plan APPROVED_WITH_CONCERNS, with 8 findings (1 HIGH, 3 MEDIUM, 4 LOW). Its rulings are folded here and in ADR-050, verbatim where the PM gave text:
- **A (asset tags and the SLA clock): AMENDED.** A tag change is an input change, not a correction. A raise restarts the clock, but never past the stored review date; a lowering keeps the original scoring date. So the upgrade can't make carried findings overdue (US-5 #13, #14; the `retagged` flag).
- **B (ID reuse): AMENDED.** IDs are never reissued. PR 2 adds a high-water mark that shipped code writes, and a check that warns. PR 1's scorer and controls renderer flag `reused-id`. Both PRs' notes say so (FR-E.19; US-6a #10, US-6b #5).
- **C (correlation fields): AMENDED, placement accepted.** Each correlated result's message names its group and its primary or peers (FR-E.20; US-6a #11).
- **P-7 (SC-8's tolerance): AMENDED.** At most 10% per stage, measured over the whole stage's output tokens, thinking included (SC-8).
- **Findings.**
  - Finding 4 (the release notes), finding 6 (ignoring `.tachi-build/`, FR-E.11) and finding 8's spec half (the dispatch-record wording) are folded here.
  - Findings 1 to 3, 5, 7 and the rest of 8 are folded in ADR-050 and the plan (rev. 1).
- **Condition.** A PR 1 projection above 9.0 days comes back to the PM before `/aod.tasks` signs off, with the items that drive it named.
- **Condition 4 at `/aod.tasks` (2026-11-22): TRIGGERED, ruled Option A.**
  - **The re-derivation.** tasks.md v1.1 derives each window from its wave's longest dependency chain plus its push-and-gate tail. That puts PR 1's central at T0 + 10.05.
  - **The re-base.** TW-0 for PR 1 is re-based once, to T0 + 11.0, and PR 1 keeps every S-5 claim.
  - **PR 2's bound** is its central plus 1.0: T0 + 13.75 + 1.0 = T0 + 14.75.
  - **The caps.** A PR 1 central above T0 + 10.5, or a PR 2 central above T0 + 15.0, would have come back to the PM.
  - **TW-ESC for PR 1** is restated as a re-projection at M3 against the re-based TW-0, and the "4.0 d remaining" test retires.
  - **Full review:** `.aod/results/product-manager-374-tasks.md`.
- **Full review:** `.aod/results/product-manager-374-plan.md`.
- **Confirmation of rev. 1's dispositions (condition 3): CONFIRMED_WITH_AMENDMENTS, 2026-11-22.**
  - **`retagged` scope: CONFIRMED.**
    - It covers every value the tags alone move, including the values that follow a band the tags moved (the SLA and the review date).
    - None is flagged `corrected`, `follows-band` included.
  - **TW-L2's narrative fallback: AMENDED.**
    - A stage above 10% of its narrative fields gets a follow-up, which that PR's notes link.
    - A stage above 25% in any W5 run, the SC-8 small runs included, comes back to the PM before that PR merges, with a sample of the rejected fields. The exception: a contract-text fix and TW-L2's second attempt bring it to 25% or below.
    - The contract text states the check: no digit outside a slot.
  - **Ruling C's peer cap: CONFIRMED** at 10 peers, then a count.
  - **NFR-1's reference-set oracle class: AMENDED.** It is bounded to the fields that ADR-050 D2 takes from the reference set. The first class reads "a flagged value (corrected, or retagged under ruling A)".
  - **PM 1(b)'s `ref` narrowing: ACCEPTED.** `ref` has no CVE form, so a cited CVE takes the fallback.
  - **Full text:** `.aod/results/product-manager-374-plan-confirm.md`.

### Registered as plan inputs (the architect's domain; not ambiguities)

- **P-1: ADR-050.**
  - **Scope.** It rules all sixteen items of PRD §13, each naming its track, before the build wave that depends on it (TW-ADR).
  - **The ADRs it changes:**
    - ADR-046 (D1, D4, D5);
    - ADR-047: unchanged, because SV-2b is carved at the plan stage (ADR-050 D1);
    - ADR-026 (Phase 3.5 now runs after the join);
    - ADR-049 D7, by a dated note, because #396 adds D10;
    - ADR-013 (D1, D4, D5);
    - ADR-018 (delta classes);
    - ADR-020 Phase 2 (the boolean, the bound, the tie claim);
    - ADR-017 (D-3's precedent; D2 for percentages);
    - ADR-048 (the shipped emitters become enforcement points; the taxa are sourced without PyYAML).
  - **What it must not claim:** `threats.md` schema 1.5, which belongs to #396.
  - **The items, with their tracks:**

  | # | Item | Track |
  |---|---|---|
  | 1 | Surfaces that leave the model tier | R (scorer, controls); O (`threats.sarif`, the `threats.md` tables, report assembly, Phase 3.5) |
  | 2 | The judgment/computation line, field by field, including controls Sections 2 and 4's cells under R-34, and S-13's source | R |
  | 3 | The part-file contract | S |
  | 4 | Where each script runs and in what order; exit codes; failure behavior; the stamp | R, O |
  | 5 | Scoring constants and arithmetic; the scoring-rules module | R |
  | 6 | Batching and overflow: S-1's measured sizes, the planner, the error schema, resume, ownership per agent, the retry cap | S (planner, error), R and O (ownership) |
  | 7 | SARIF identity under S-6, with at most one re-key event per file | R (scorer, controls, the carrier); O (`threats.sarif`) |
  | 8 | SARIF membership, the peer marker, the counting rule, the group-membership source | R, O |
  | 9 | Score-inheritance mechanics | R |
  | 10 | The exception rules | R |
  | 11 | The dispatch records | O |
  | 12 | The provenance check | O |
  | 13 | Phase 3.5, under S-2 and S-3 | O |
  | 14 | Report assembly | O |
  | 15 | Schema versions | R (`risk-scores.md`, `compensating-controls.md`, the part schemas); O (`threats.md`, the record schemas) |
  | 16 | Test and CI placement | S, R, O |

- **P-2: the #396 rule (C-4).** This bundle lands first, and #396 rebases. The plan files the expected conflicts on #400, keeps `/tachi.threat-model`'s Step 2.5 and Step 3 anchors in place, and keeps the Step 2.6 slot free. The same anchors bind FR-E.18's body-line edit.
- **P-3: FR-K4.1's record option:** a body line, or a key that #396 declares.
- **P-4: the failed-output mechanism** (D-3). It needs no N7 change.
- **P-5: who runs report assembly, and who dispatches the tree batches** (ADR-050 items 6 and 14), within S-8.
- **P-6: the `.tachi-build/` layout** for parts, records, briefs, plans, the persisted Phase 1 tables and the stage records, with every path declared (NFR-3).
- **P-7: SC-8's tolerance.** Ruled by the PM at the plan review: at most 10% per stage, measured as SC-8 states.
- **P-8: the retry cap**, per dispatching layer.
- **P-9: TW-N3's ordering**, kept generic in public text.
- **P-10: the consequence-scope list**, which becomes T001's pre-state census.
- **P-11: a planned dispatch that never produced a record** (PM spec review, finding 13). If it costs next to nothing, FR-N4.6 compares the records with the persisted dispatch table; both are persisted already. Otherwise it joins S-16's follow-ups.

---

## Dependencies

- **#373 (delivered, v4.48.1).** Its K9 and K13 parsers must read K8's corrected format, and its manifest completeness check requires every new script and helper to be listed.
- **#364.** It blocks the next minor release, so this bundle ships as `fix:`. This bundle lands first, and #364 regenerates the examples through the renderer. N16's example audit leads are posted to #364 at delivery.
- **#365.** Test runs re-render tracked example PNGs. They are never committed, and the PDF baselines aren't regenerated.
- **#396 (F-391 Part B) and #400.** About nine code and contract paths overlap (P-2).
- **The N3 hardening track (#360, #391).** It edits some of the same agent specs. It merges first, as its own `fix:`, if it is ready first, and the plan orders the two (P-9).
- **#399.** The dispatch records and briefs give its manifest something to record, and its planned check is the transcript-level complement to FR-N4.5.
- **#356 (R-13), #357, #408 (R-14), #409 (R-15, dropped under R-34) and #412 (R-16).**
- **Platform facts.**
  - Claude Code's documented dispatch limits and output caps (S-1, S-8).
  - GitHub's documented matching inputs (S-6). The server-side key isn't documented, so FR-E.2 models the documented inputs.
- **CI gates:** `tachi-install-fidelity.yml`, `tachi-pytest.yml` and `tachi-permissions-verify.yml`.
- **Delivered foundations:** ADR-013, 017, 018, 020, 024, 046, 047, 048 and 049, and KB Entries 22, 24, 25 and 26.

## Assumptions

- **T0 is 2026-11-22**, the day the plan stage started (the 21st was the define day). M1, the tasks sign-off, is also 2026-11-22. PR 1 lands at about T0 + 8.0 and PR 2 at about T0 + 11 to 12 (PRD §11), and `/aod.tasks` re-baselines both: tasks.md v1.1 puts them at about T0 + 10.05 and T0 + 13.75, under the PM's condition-4 ruling.
- **Unpriced spec additions.** A few spec rulings add small items that the feasibility check doesn't price:
  - S-9's spike, S-11's checks and S-14's census;
  - S-3's rules and S-4's larger single base set;
  - S-12's drift-form reader work (PM finding 1).

  The team-lead prices them at `/aod.tasks`, where they count toward TW-0 for the PR that carries them: S-3 and S-9 belong to PR 2; S-4, S-11 and S-12 to PR 1; and S-14 to both. A PR 1 projection above 9.0 days goes back to the PM (R-34).
- **Adopters run tachi inside Claude Code**, with the agents installed by `scripts/install.sh`.
- **Output cap.** Runs A and B stopped at a 64,000-token output cap. S-1 designs against 32,000, so a lower default doesn't break batching.
- **Synthetic stand-ins.** The fixture's synthetic findings reproduce the size and shape of the real-world runs without their content.
- **Unchanged sources.** `schemas/risk-scoring.yaml` stays canonical for the scoring constants. The isolated-operation session profile stays unchanged.
- **Agents mostly follow their contracts.** The checks detect when they don't, and transcript-level proof stays with #399.
- **Code Scanning evidence.** If no scratch-repository check runs, the release notes say that the alert behavior is modeled from GitHub's documentation (D-7).
