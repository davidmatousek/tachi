---
prd:
  number: 374
  topic: large-architecture-pipeline-resilience
  created: 2026-11-21
  status: In Review
  type: feature
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-11-21
    status: APPROVED_WITH_CONCERNS
    notes: "v1.2 delta re-review: APPROVED_WITH_CONCERNS. All 16 findings of the v1.1 re-review are resolved, both HIGH included (budget carves follow R-12 and SV-3 fires only on its technical trigger; TW-N3 is generic), and the hygiene re-scan of the PRD and the feasibility check is clean. R-28 and R-29 are accepted as proposed, and R-25, R-26, R-27, R-30 and R-31 bind as amended in product-manager-374-r3.md; 5 new LOW findings. The bundle corrects what tachi already promises (complete outputs, agents on contract, alert identity that stays stable), so it ships as fix(374) with binding release notes, once the feasibility check matches R-23 and the team-lead's pricing addendum lands, both before /aod.plan. Full reviews: .aod/results/product-manager-374.md, product-manager-374-r2.md and product-manager-374-r3.md."
  architect_signoff:
    agent: architect
    date: 2026-11-21
    status: APPROVED_WITH_CONCERNS
    notes: "v1.1 re-review: APPROVED_WITH_CONCERNS. The six v1.0 inaccuracies are corrected, and all 28 findings are resolved, ruled on or placed in ADR-050. Two minor inaccuracies remained (NG4's TE prefix and D-5's 'forever'), within the target of fewer than 3, and v1.2 corrects both. The 22 new findings (0 BLOCKING, 0 HIGH, 11 MEDIUM, 11 LOW) refine the spec and ADR-050, chiefly the tree-batching layer, stale part files on resume, NFR-10's scope, per-file SARIF tool names, the architecture-path carrier and legacy baselines; v1.2 folds them in ahead of /aod.tasks (TW-ADR). Full reviews: .aod/results/architect-374.md and architect-374-r2.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-11-21
    status: APPROVED_WITH_CONCERNS
    notes: "FEASIBLE WITH MODIFICATIONS; neither veto exercised. Estimate: planning 8.0 / floor 5.5 / ceiling 13.0 eng-days, branch to merge (effort 17.9 / 11.3 / 29.7; confidence LOW–MEDIUM). 14 concerns (3 HIGH, 8 MEDIUM, 3 LOW), all folded in v1.1: threats.sarif identity in scope (C-1), chain formation in shipped code (C-2), the live matrix restructured (C-3), merge order with #396 and the N3 track (C-4, C-5), three uncovered overflow surfaces (C-6), RK-4 corrected (C-7), provenance back-references (C-8), part files as a trust boundary (C-9), pinned arithmetic (C-10), fixture design (C-11), the adapter copies (C-12), K4 evidence (C-13), text fold-ins (C-14). No split at Define; SV-4 is armed through TW-0 and TW-ESC. Full review: specs/374-large-architecture-pipeline-resilience/feasibility-check.md."
source:
  idea_id: 374        # equals prd.number (GitHub Issue #374)
  story_id: null
bundle:
  lead: 374
  members: [K4, K5, K6, K7, K8, N4, N12, N14, N15, N16]
  folded_from: 397    # N4, N12, N14, N15, N16, plus the K4, K5–K7 and K6-live evidence and the #391 dispatch evidence
  folds_in: [408-body-instruction, 409-if-small, 412]
  companion: 373      # K1–K3, K9–K15; delivered in v4.48.1
  coordinate: [356, 357, 360, 364, 365, 396, 399, 400, 408, 409, 412]
  split_valve_candidates: [SV-1-K4, SV-2b-threats-md-tables, SV-3-N12, SV-4-track-split]
  release: "patch — PR titled fix(374); #364 blocks the next minor release; release-note content is binding (§8)"
---

# PRD-374 — Large-Architecture Pipeline Resilience

**Status**: In Review (v1.2, 2026-11-21). Lead issue [#374](https://github.com/davidmatousek/tachi/issues/374) carries K4–K8. Five defects from [#397](https://github.com/davidmatousek/tachi/issues/397) fold in: N4, N12, N14, N15 and N16. The bundle ships as a **patch release** (`fix(374):`), because #364 blocks the next minor release.

> **Bundle PRD.** K-numbers and N-numbers are stable defect IDs. K1–K3 and K9–K15 shipped in #373 (v4.48.1). #397 tracks N1–N17 from a second real-world run; N5 and N13 shipped in Patch A (#421, v4.48.4). This PRD owns the items whose fix is one mechanism. Output doesn't fit one response. Agents leave their contracts when it doesn't. Nobody checks the values.
>
> **v1.1** folds in the Triad review of v1.0:
> - **PM**: CHANGES_REQUESTED, with 27 findings and 7 rulings.
> - **Architect**: CHANGES_REQUESTED, with 6 technical inaccuracies (corrected in Appendix A) and 28 findings.
> - **Team-Lead**: APPROVED_WITH_CONCERNS, with 14 concerns and the estimate that §11 is sized from.
>
> Appendix B maps every HIGH finding to the section that resolves it. Mechanisms the reviewers placed in the plan are listed for ADR-050 in §13.
>
> **v1.2** folds in the re-review of v1.1:
> - **PM**: CHANGES_REQUESTED. Two new HIGH findings, on the carve order and on hygiene in the feasibility check, plus five MEDIUM and nine LOW, and six rulings.
> - **Architect**: APPROVED_WITH_CONCERNS. Two inaccuracies remained (Appendix A), plus 11 MEDIUM and 11 LOW findings.
>
> Rulings R-23 to R-33 are new. R-25 to R-31 settle decisions the Architect said the PRD must make, and are marked *proposed* until the PM rules on them. Risks are renumbered RK-1 to RK-10, so that their IDs no longer collide with the rulings.

---

## 1. Problem Statement

Two stock runs on large real-world architectures failed the same way. **tachi's LLM-authored stages assume that each output fits in one model response and that each agent stays inside its contract. At scale neither holds, and the failures are silent.**

- **Run A** (v4.48.0; 26 components, 200+ findings, 40+ Critical; #374):
  - the threat-report agent hit the 64k output-token cap while emitting every Critical attack tree inline;
  - the risk scorer wrote about a quarter of its SARIF results and silently dropped one finding from `risk-scores.md`;
  - the control analyzer's SARIF overflowed, and its summary totals didn't equal the sum of its own rows;
  - cross-layer attack-chain analysis (Phase 3.5) produced no artifact and recorded no outcome;
  - the controls report's tables drifted between formats within one file.

  Each overflow was recovered only by assembling the missing output by hand.
- **Run B** (v4.48.1; ~40 components, ~390 raw and ~210 deduplicated findings; #397). The pipeline "completed" only by leaving its contracts:
  - the orchestrator ran all Phase 2 analyses as built-in `general-purpose` agents, under a brief that added policy the contract doesn't have (per-pair caps, a Critical-calibration rule). With the report agent's helpers, that was 33 stand-ins against 10 typed spawns;
  - orchestrator-written scripts rendered the outputs, and helper scripts assembled the report and its trees after 14 `max_tokens` stops;
  - the risk scorer spent its whole 64k output budget in one reasoning turn, then handed back an unrun program instead of its outputs;
  - inherited scores were never re-validated: in the baseline, 64 of 202 composites disagreed with their own dimensions, all 64 inherited from an older run;
  - SARIF result identity churned across runs: 38 earlier results became correlation peers while 0 findings were resolved, so Code Scanning would close those alerts as fixed.
- **Small-scale signal.** A spike on the smallest example input (2 Critical and 5 High findings in its sample) saw five `max_tokens` stops across four agents (#374, comment of 2026-11-21). Two of the five were Phase 2 threat agents, so output-cap pressure starts well below "large", and it starts in Phase 2.

**Five root problems.**
1. **Single-response emission.** Each of these is written in one response today, and nothing checks its completeness against its input:
   - the whole threat report, and the attack-tree sub-agent's session;
   - `risk-scores.md` and `risk-scores.sarif`;
   - `compensating-controls.md` and `compensating-controls.sarif`;
   - `attack-chains.md`;
   - each Phase 2 agent's return;
   - at ~390 findings, the orchestrator's `threats.md` and `threats.sarif`, each over 120k tokens.
2. **No contract for failure.** When an agent can't finish, nothing tells it what to do, so it improvises: stand-in agents, helper scripts, code handed back to the caller. None of that is recorded, so the run can't be reproduced and its outputs can't be trusted.
3. **Silent outcomes and unchecked arithmetic.** A skipped phase looks the same as an empty result (K4). Row counts, totals and inherited composites are never checked against their inputs (K6, K7, N16).
4. **Contradictory contracts.** The two contracts disagree on several points:
   - the controls Section 2 schema (K8);
   - the SARIF result count (the two agents count it differently; N15a);
   - how peers and unchanged findings inherit scores, and from which baseline file (N15b, N15c).
5. **Unstable alert identity.** GitHub Code Scanning matches an alert by its rule, its `primaryLocationLineHash` and its file path.
   - On the canonical path, the scorer and controls SARIF carry no hash (`risk-scorer.md:492`; `control-analyzer.md:384`), and they point at a per-run snapshot path (`.claude/commands/tachi.risk-score.md:71-72`, `tachi.compensating-controls.md:86-88`). Their alerts can therefore close and reopen on every run.
   - In `threats.sarif`, the hash is shared by every finding with the same rule and component (`sarif-specification.md:333-339`), so distinct findings collapse into one alert, and regrouping drops results (N12).

**Why now.**
- The next large real-world run needs a release in which every stage completes on contract.
- tachi's place as a scanning column depends on SARIF that is complete and stable from run to run, because that is what Code Scanning and downstream tools consume.
- tachi's target users are developers without deep security expertise. They can't spot a wrong composite or an improvised agent, so outputs have to be correct by construction.
- The improvised layer is also a security exposure:
  - Run B's stand-ins read third-party source through Bash while holding Write, Edit, Agent and deferred web and browser tools. The typed threat agents they replaced hold Read, Glob and Grep.
  - Running a handed-back program executes code written by an agent that had just ingested third-party text (#360).

---

## 2. Goals & Non-Goals

### Goals

- **G1 (K5, K6, K7, N4): complete outputs at any size.** No stage depends on fitting its output in one response. Every stage, the threat model included, accounts for every input finding, and the whole report is bounded.
- **G2 (K4, K6, K7): no silent outcomes.** Phase 3.5 always records what happened. Count, total and completeness parity are checked by code on the compiled artifacts.
- **G3 (N4, N14): agents stay on contract.** Typed dispatch only. Every finding has a provenance entry. Briefs carry no policy, and no agent hands back code. Overflow is handled by whichever layer dispatched the agent.
- **G4 (N14, N16, N15): computed values are computed.** The arithmetic in D-2's table comes from shipped, tested code: sub-score averages, reachability adjustments, the asset-modifier elevation, composites, bands, governance fields, residuals and totals. Inherited scores are recomputed, and any change is flagged. `threats.md` Section 6's counts and percentages are checked against the reference finding set (D-4).
- **G5 (K8, K6/K7, N12, N15): one contract per surface.** That means one controls table schema and one SARIF completeness ("N/N") rule for all three SARIF files. Alert identity stays stable across runs under GitHub's matching key, and score inheritance follows ranked rules.

### Non-Goals

- **NG1: reference-loading hardening** (#397 N3). It has its own security track (#360/#391). It edits some of the same agent specs, so it merges first as its own `fix:` if it is ready first. Otherwise the two ship in consecutive patch releases, in the order the plan sets.
- **NG2: the scoring/delta bundle** (#397 N9–N11 and N17):
  - the likelihood rubric;
  - the UNCHANGED/UPDATED rule;
  - rule R-02 and MAESTRO matching;
  - the scoring ambiguities.

  Where a check here depends on an N17 ambiguity, the case is reported as "unchecked", never as a violation (D-4). Those ambiguities are compound trust labels and the bound for cross-category peers. The 9.2 ceiling's scope (N17a) is settled here by R-25, and the scoring/delta bundle inherits that reading.
- **NG3: the hygiene items** (#397 N1, N2, N6, N7 and N8). N7's run-directory auto-detection stays there. This bundle resolves the baseline from `threats.md`'s own `baseline.source` (D-6), so it needs no auto-detect change.
- **NG4: #356**, the Phase 3 compilation that can fold findings into the AI tables' sequences. `OI-` and `MI-` findings fold into `LLM-N`, and `TE-` findings into `AG-N` (`orchestrator.md:373-374`; `output-schemas.md:297`). *Ruling (v1.1):*
  - if FR-O.1 moves Phase 3's table emission into code, that code must pick an AI-table prefix rule, so #356 folds in and closes;
  - otherwise #356 stays separate, the completeness check records each renumbering in its ID map, and a test pins today's behavior.
- **NG5: example and baseline regeneration** (#364), PDF baselines and tracked PNGs (#365). This bundle lands **before** #364's re-score, so #364 regenerates through the renderer. The new checks don't gate on `examples/**` until #364 lands. N16's example audit leads are posted to #364 at delivery.
- **NG6: the run archive and provenance manifest** (#399). This bundle keeps dispatch records and briefs in the run directory, and transcript-level proof of who ran stays with #399.
- **NG7: scoring semantics.** These stay as they are:
  - CVSS vectors and category defaults;
  - the frozen 9.2 asset-modifier ceiling (ADR-046);
  - the 6-value asset-tag enum;
  - the severity-band thresholds;
  - the composite weights.
- **NG8: new agent tools.** Deterministic steps run where Bash already runs: the main session and the orchestrator. Every agent keeps its tools, and the 14 threat agents stay read-only (Read, Glob, Grep).
- **NG9: committing real-world run output.** Tests use synthetic fixtures only.
- **NG10: other adapter copies.** The Copilot, Cursor and generic adapters are out of scope; the scanner runs in Claude Code (`.claude/rules/scope.md`). The Claude Code adapter's copies follow ruling R-17.

---

## 3. User Stories

- **US-1 (adopter modeling a large system; K5, K6, K7, N4, N14).** When I run tachi on a large system (25+ components, 200+ findings), I want every stage (threat model, report, risk score and controls) to finish with complete output, so that I never hand-assemble SARIF or report sections.
  - *Given* the synthetic large fixture, *when* each stage runs, *then* each output accounts for every input finding exactly once, and no file is assembled by hand.
  - *Given* the threat-model stage, *when* Phase 3 compiles, *then* every finding in every dispatch record appears in `threats.md`, as a finding or merged into a named surviving finding, with every ID change recorded.
  - *Given* any agent that reaches its output limit, *when* it stops, *then* the layer that dispatched it re-runs the remaining work in batches. No agent ever hands back code for me to run.
- **US-2 (security lead; K4).** When I read the report, I want to know whether cross-layer attack-chain analysis ran and what it concluded, so that an empty chain section means "none found", not "skipped".
  - *Given* any run, *when* the threat model finishes, *then* `threats.md` records the Phase 3.5 outcome: chains written, 0 chains with the reason, or skipped with the reason. The post-run check catches a missing or inconsistent record and records it as skipped, with the reason. It never ends the run (R-24).
  - *Given* a fixed finding set, *when* chain formation runs twice in the shipped chain script, *then* it forms and surfaces the same chains. If ADR-050 keeps chain formation in the model, the algorithm and the counts are recorded instead (R-19).
- **US-3 (consumer of `compensating-controls.md`; K8).** When I parse or read the controls report, I want every Section 2 table to have the same columns, including MAESTRO, and every recommendation tied to its finding, so that parsers and readers get consistent data.
  - *Given* a generated controls file, *when* its band tables are compared, *then* all use one column schema, and Section 4 uses one block per finding, each joined to its finding.
  - *Given* a controls file in either the corrected or the pre-fix format, *when* #373's parsers read it, *then* both parse.
- **US-4 (adopter scanning a codebase they don't control; N4, N14).** When tachi analyzes third-party code, I want the analysis done by tachi's typed agents under their published contracts, with no improvised agents, policy or scripts, so that I can trust the result, reproduce it, and know which tools touched the code.
  - *Given* any run, *when* Phase 2 dispatches, *then* every analysis is done by a typed tachi agent. A typed agent that can't be spawned stops the run with an actionable error instead of a substitute.
  - *Given* any run, *then* every finding in `threats.md` has exactly one provenance entry: a typed agent's dispatch record, a baseline carry-forward, or a named deterministic rule. A run with no dispatch records fails.
  - *Given* any run, *then* each agent is dispatched with a fixed one-line prompt that tells it to read its brief, and that brief is saved in the run directory. The brief holds only the brief template's fields.
- **US-5 (security lead tracking risk over time; N16, N15).** When findings carry over from a baseline, I want their scores recomputed from their inputs and any change flagged, so that one run's slip never becomes permanent baseline data.
  - *Given* a carried finding whose inputs didn't change, *when* the stage runs:
    - its inputs are inherited verbatim;
    - its composite, band and governance fields are recomputed;
    - any change from the stored values is flagged with its cause.
  - *Given* a CVSS base score its vector doesn't give (outside the documented clamps), *when* the renderer runs, *then* it corrects the score and flags the correction. A case that depends on an N17 ambiguity is reported as unchecked.
  - *Given* the two-run fixture in which correlation regroups carried findings, *when* the scorer runs, *then* no carried finding's score, band or SLA changes because of the regroup alone. An UNCHANGED peer whose carried score differs from its new primary's keeps that score and is flagged as divergent.
- **US-6 (Code Scanning consumer; N12, K6, K7).** When I upload tachi's SARIF on every baseline-aware run, I want a finding that is still present to keep its alert, so that alerts aren't closed as fixed when nothing was fixed, and my dismissals and history stay with the finding. Stateless runs renumber findings, so they re-key their alerts (R-29).
  - *Given* two baseline-aware runs in which correlation regroups carried findings, *when* both runs' SARIF files are compared under GitHub's matching key (tool and category, `ruleId`, `primaryLocationLineHash`, `artifactLocation.uri`), *then* every carried finding present in run 2 keeps its run-1 key. This holds for each of the three SARIF files.
  - *Given* an unchanged re-run, *then* every key is identical.

---

## 4. PRD Decisions

These decisions bind the spec. The issue left one design question open, how SARIF gets emitted. D-2 answers it at the product level, and ADR-050 records the technical design at the plan stage. No build wave starts on a contract that ADR-050 hasn't ruled (TW-ADR, §10). If an item outgrows its estimate, the split valves (§10) apply.

### D-1: scope is the shared mechanism, nothing else

F2 takes #374's K4–K8 and #397's N4, N12, N14, N15 and N16.
- **N12 is decided and implemented here.** The PR ticks it off in #397, unless SV-3 fires, in which case US-6 and SC-6 move with it (§10).
- **Why these.** They share files and one mechanism:
  - the files are the orchestrator, threat-report, risk-scorer and control-analyzer specs, three commands, and the shared references;
  - the mechanism is output that doesn't fit, agents that improvise when it doesn't, and values that no code checks.

  Fixing them apart would rewrite the same contracts twice.
- **Small adjacent items fold in** (rulings R-14 to R-16):
  - #408's body-instruction option;
  - #409's dispatch-target check, if it is small;
  - #412's SARIF `informationUri` fix. Without it, the renderer would emit the placeholder.
- **Why not more.** Everything else in #397 keeps its own bundle (NG1–NG3), so this release doesn't grow into the scoring redesign.

### D-2: computed values move to shipped code, and the renderer owns each whole file

- **Decision.** The risk scorer and the control analyzer keep authoring judgment. A **shipped, tested renderer**, run where Bash already runs, **owns each whole output file**: `risk-scores.md`, `risk-scores.sarif`, `compensating-controls.md` and `compensating-controls.sarif`.
  - **What the agents write.** Bounded part files, one per batch. They hold structured judgment and the prose fragments for the narrative sections. The agent specs drop their output-format instructions, so K8's single schema becomes a property of the renderer, and the output-schema template documents it.
  - **Why part files.** The writer agents hold Write but not Edit, and one Write replaces a whole file from one response. An agent can't share a file with a script. At about 395 tokens per finding, an agent-written `risk-scores.md` passes the 64k cap at roughly 160 findings.
- **The line between judgment and computation** (the Architect's field-by-field list is ADR-050 item 2):

  | Agents author (judgment) | The renderer computes |
  |---|---|
  | Dimension sub-scores | Their averages (exploitability, scalability) |
  | CVSS vectors | The base score from the vector, plus the documented clamps |
  | — (the asset tags come from the populator, not the agent) | The asset-modifier elevation: the tags' forced vector bits, the recomputed base score, and the 9.2 ceiling, which never lowers an assessed score (R-25) |
  | Reachability inputs: zone, trust level, barrier counts | The reachability baseline, its adjustments and its clamps |
  | Rationale, and the prose fragments for narrative sections | Composites, severity bands and governance fields (SLA, disposition, review date), plus every number the prose states, filled from renderer slots so the prose can't contradict the tables |
  | Control status, evidence and recommendations | Residual scores, residual bands, totals, percentages, and the Section 5 aggregate and band-shift tables |
- **Authoring tier.** This changes the production authoring tier that ADR-046 records; production SARIF is LLM-authored today. The plan stage writes **ADR-050**. It is the "structural ideal" that ADR-046 D5 deferred, and it records how ADR-046 (D1, D4), ADR-047 and ADR-049 (D7) change. ADR-050 also decides the orchestrator's outputs (FR-O.1).
- **One source of truth.** Once the renderer computes a field, the agent contract stops authoring it. `scripts/populate-affected-assets.py` is the precedent for a deterministic value authority wired into production (ADR-046). `scripts/populate-maestro-coverage.py` is barred from production wiring precisely to avoid a second source of truth. The renderer follows the first pattern.
- **Why.**
  - **What users see.** A wrong composite moves a finding's band. The band sets the remediation SLA and the disposition that a security lead acts on and that downstream tools ingest.
  - **The evidence.** In Run B's baseline, 64 of 202 composites disagreed with their own dimensions, all inherited from an older run. Only 83 of 202 baseline vectors reproduced their stated score; some differences are legitimate, such as clamps.
  - **The agent writes a generator anyway.** N14 shows that once its output gets large, the agent writes one. A shipped, tested renderer is better than an improvised, unreviewed one.
  - **It's checkable.** A renderer makes N/N, totals and identity true by construction, and checkable.
  - **It's cheaper.** Every run gets cheaper, not just large ones, because the agent no longer authors SARIF (SC-8).
- **Options considered.**
  - (a) Chunked or incremental agent output. It keeps today's tier, but leaves arithmetic and completeness to the model.
  - (b) Agent data plus a deterministic renderer. **Chosen; the Architect endorses it.**
- **Constraints.**
  - **It is new production code.** The regeneration-tier generators aren't a drop-in:
    - neither they nor `sarif_common.py` is installed, and neither suppresses bytecode (ADR-049 D8);
    - `generate-risk-scores-sarif.py` is hardcoded to one example (#357);
    - both emit correlation peers as top-level results, against tachi's own SARIF specification reference (`sarif-specification.md:217`);
    - their identity hash and property bag differ from the agents' contracts.

    The renderer reproduces the agents' current SARIF contract, except where D-5 changes membership or identity. If it replaces `generate-risk-scores-sarif.py`, it subsumes #357.
  - **Imports and bytecode.** It imports only the standard library at load time, enforced by S-13 (`test_distributable_imports_stdlib_only` in `tests/scripts/test_install_manifest_completeness.py`, gated in `tachi-install-fidelity.yml`). The renderer and every helper it imports join `REQUIRED_SCRIPT_NAMES`, and S-13's local-import allowance widens to them. Each new installed script sets `sys.dont_write_bytecode` before its local imports (ADR-049 D8).
  - **Where it runs.** In the main session, or in the orchestrator. The commands set no `allowed-tools` (CI guard C5), and `/tachi.risk-score` already runs `scripts/populate-affected-assets.py`. No agent gains a tool (NG8).
  - **The CVSS calculator.** The stdlib CVSS 3.1 calculator that Patch A added as a test (`tests/scripts/test_cvss_category_defaults.py`) moves into shipped code.
  - **Scoring constants.** The weights, bands, SLAs and category vectors are embedded in the renderer, with a drift test against `schemas/risk-scoring.yaml`, as Patch A's test does for the vectors (R-32). The core path needs nothing beyond the standard library. PyYAML stays optional, for the PDF attestation page only.
  - **A trust boundary.** The part files are written by agents that have just read third-party text (#360). NFR-10 lists the validation rules.

### D-3: failure has a contract

- **No code hand-backs.** No agent returns code for its caller to run, writes a program for someone else to run, or substitutes a different agent type for one it was told to use. This applies to every tachi agent.
- **The dispatching layer owns batching and resume:**
  - the command, for the scorer and the control analyzer;
  - the orchestrator, for the Phase 2 threat agents and the Phase 5 report agent;
  - the orchestrator or `/tachi.threat-model`, for the attack-tree batches. The report agent has no Bash, so it can't run the planner. Either the orchestrator dispatches the tree batches itself after the report agent returns, which also cuts the dispatch depth to two layers, or it plans them and passes the plan in the report agent's brief (ADR-050 item 6). Each batch writes its own manifest under `.tachi-build/`, and the assembly step merges them into today's single schema-1.0 `.manifest.json`, which the report and PDF readers keep reading.

  How it works:
  - A shipped script plans the batches and slices the input for each one, so no layer re-reads a 120k-token `threats.md` to plan. The planner runs only where Bash runs: the main session or the orchestrator.
  - The layer works out what's done and what's left by comparing the part files on disk with each batch's ID list. The agent's structured overflow error is advisory, because a `max_tokens` stop can return nothing parseable (Run B's scorer stopped mid-reasoning).
  - **No stale parts.** Each plan carries a fresh plan ID and the digests of its inputs, and every part file carries its plan ID and batch ID. The reconciler and the renderer accept only the current plan's parts, so a part left by an earlier invocation is never counted as done. A re-run of a command reuses the same `.tachi-build/` directory, and agents can't delete files (ADR-050 item 3).
  - Retries are capped, and a batch that can't be recovered fails the run loudly.
- **Phase 2 overflow is handled.** The orchestrator detects a truncated or overflowed agent return, by a missing end marker or a structured error. It re-dispatches that agent on a narrower scope (per component), and records the event. If it can't recover, the run fails.
- **Typed dispatch only.** Phase 2 uses typed `subagent_type`s, and so do the threat-report agent's sub-dispatches. Three failure modes are on record:
  - (1) `general-purpose` stand-ins for the threat agents (#397);
  - (2) the report agent's `general-purpose` helpers running Bash and Write (Feature 391's attribution spike);
  - (3) an orchestrator that analyzes inline and dispatches no threat agent at all (`docs/guides/ISOLATED_OPERATION_TACHI.md`, re-check R6).

  Nothing blocks `general-purpose` today, because ADR-049 D4 leaves `Agent` unguarded. So prevention and detection both ship:
  - **Prevention.** FR-N4.1 names the permitted targets in the dispatcher bodies (#408's body-instruction option), and #409's static check guards those names if it folds in.
  - **Detection, modes 1 and 3.** The provenance check (FR-N4.5) covers these as a record the orchestrator keeps about itself: it proves consistency, not provenance.
  - **Detection, mode 2.** A separate check on the tree files and their manifest (FR-K5.7). Like FR-N4.5, it confirms consistency, not provenance, because the manifest has no author field.
  - **Transcript-level proof** stays with #399.
- **Briefs carry scope, not policy.**
  - **What counts as policy.** Anything beyond the agent's published contract. The contract's own baseline guidance (focus on uncovered pairs) is a scope input, and it stays.
  - **The saved brief is the brief the agent read.** Each agent is dispatched with a fixed one-line prompt that tells it to read and follow its brief, which is saved in the run directory. "Scope only" is checked against the brief template's closed set of fields.
  - **No architecture copy.** A brief points at the run's architecture snapshot, and at the Phase 1 component inventory and dispatch table, which are persisted under `.tachi-build/`. It doesn't carry copies of them.
- **Failure behavior.** Three new paths end a run: a typed agent that can't be spawned, a failed provenance or completeness check, and an unrecoverable batch. On any of them:
  1. the error names the stage, the agent or finding IDs involved, and the remedy, in the pattern of today's "not installed … re-run the installer" message;
  2. the run's outputs stay for diagnosis but are marked failed, and no later command takes them as input or as a baseline. The plan picks a mechanism that needs no N7 change, such as non-canonical file names;
  3. no partial output is ever presented as complete;
  4. a test covers each path.
- **One contract voice.** The agent specs say they "do not reference any specific agentic coding tool". That contradicts typed dispatch, which is a Claude Code construct, and tachi's scope, which isn't agent-agnostic. Those clauses are removed or rewritten (FR-N4.1), including the same clause in the report-assembler and infographic agents. The three commands' text also says to run only the shipped scripts it names, and to stop on failure.

### D-4: outcomes are recorded, and arithmetic is checked by code

- **Phase 3.5 always records its outcome** in `threats.md`: chains formed and surfaced, `0 chains passed filter (<reason>)`, or `skipped (<reason>)`.
  - It replaces the in-memory `has-attack-chains` boolean, which the contract never writes to an artifact. Some outputs carry it as a de-facto frontmatter key, and its consumers re-derive it from whether the chains file exists.
  - The main session checks the record after the run. "Chains written" requires `attack-chains.md` with that count, and "0 chains" or "skipped" requires the file to be absent and a reason recorded. A bad record never ends the run, and never lets the chains read as complete (R-24):
    - a missing record is written as `skipped (no outcome recorded)`;
    - an inconsistent record is rewritten as `skipped (<what disagreed>)`, and the chain output isn't presented as complete (ADR-050 item 13 picks the mechanism);
    - either way, the check reports it and warns, the report and the PDF read "skipped", the stage record counts it (NFR-5), and a test covers it.
  - The report and the PDF read the record. When it's absent they fall back to today's file-presence rule, so old inputs render byte-identically.
- **Chain formation follows one algorithm**, and is deterministic for a given finding set when it runs in the shipped chain script (R-19).
  - Today the orchestrator's Phase 3.5 and `attack-chain-patterns-shared.md`, which the orchestrator is told to read, describe different ones.
  - The spec defines a total order across ID prefixes for tie-breaks, a redundancy rule for sub-chains and shared tails, and the surfacing rule. These rules carry real weight: structural connection through the transitive closure links almost every pair of findings on a large connected graph.
  - **Recommended:** the computational steps move into a shipped, stdlib-only script that the orchestrator runs, as it already runs the Phase 3.7 populator. Those steps are indexing, link candidates, assembly, deduplication, the filter, ranking, IDs and chain-breaking. The model writes the titles and narratives for the surfaced chains only. The script also bounds `attack-chains.md` and writes the outcome record (ruling R-19; ADR-050 decides).
- **Parity is checked by code on the compiled artifacts**, against one reference finding set, never against what an agent parsed (KB Entry 22).
  - **The reference set** is defined once, in code: reuse `tachi_parsers.parse_threats_findings`, which reads Section 7, where every finding appears exactly once. It settles:
    - which prefixes count, `AGP-NN` included, plus `OI-`, `MI-` and `TE-` while #356 is open;
    - how RESOLVED findings count: `risk-scores.md`'s open rows are compared with Section 7, its RESOLVED rows with Section 4c, and the `.md`–`.sarif` agreement check compares open rows only (R-30);
    - how the `threats.sarif` fallback input is handled.
  - **Parse errors.** Today both agents skip malformed rows and "report them as parsing errors" with no defined place in the output. Parse errors get a defined place in the output.
  - **The checks:**
    - `risk-scores.md` rows equal the reference set;
    - the controls totals equal the sum of the rows (true by construction under D-2; the check stays as a test);
    - each SARIF is complete under D-5;
    - each `.md` agrees with its `.sarif`;
    - `threats.md` Section 6's counts and percentages match the reference set;
    - the threat-model stage passes record completeness (FR-N4.6).

    An empty extraction is an error, never a pass.
- **Inherited scores are recomputed** (D-6). Derived fields are recomputed from the inherited inputs, and any change from the stored value is flagged with its cause.
  - **Vector-to-score mismatches** outside the documented clamps are **corrected and flagged** (ruling R-9).
  - **NEW and UPDATED peers copy their primary's vector along with its scores** (R-31). So the vector check needs no peer exception; the peer exception belongs to the ±1.0 bound check (N17c, NG2).
  - **Every ID prefix gets a category**, `AGP`, `OI`, `MI` and `TE` included, because category resolution covers only eight prefixes today.
  - **Reachability** is checked against its trust-level range only for labels that normalize unambiguously.
  - **Unchecked cases.** A stored value whose check depends on an N17 ambiguity, such as a compound trust label, is reported as "unchecked", never as a violation (ruling R-10). R-25 settles the 9.2 ceiling's scope. A carried legacy finding whose outcome would depend on an unrecorded assessed score keeps its stored score, and is reported as unchecked.
  - **Rounding.** A difference that comes only from rounding is normalized and counted in the run summary, not flagged per finding, provided the band, SLA, disposition and review date all stay the same. A rounding difference that moves the band is flagged as a band correction, with rounding as its cause, and R-5 applies (ruling R-11, amended; ADR-050 pins the rounding).

### D-5: SARIF completeness and identity, for all three files

- **Scope.** All three SARIF files tachi emits, whichever tier authors each: `threats.sarif`, `risk-scores.sarif` and `compensating-controls.sarif` (ruling R-2).
  - `threats.sarif` is where N12 was observed, and it is the file the docs tell adopters to upload (`README.md:193`; `docs/guides/DEVELOPER_GUIDE_TACHI.md:1118`).
  - The controls SARIF carries forward the upstream fingerprints, so identity has to be defined where findings originate.
  - One shared reference (FR-E.1) replaces the four SARIF contract copies that exist today:
    - `sarif-specification.md`;
    - §10 of `risk-scorer.md`;
    - the installed `adapters/claude-code/agents/references/sarif-generation.md`, which the control analyzer reads;
    - the control analyzer's own Phase 6c, which D-2 removes anyway.
- **GitHub's matching key.** Code Scanning matches an alert on:
  - the tool (and upload category);
  - the `ruleId`;
  - the `primaryLocationLineHash`;
  - the `artifactLocation.uri`.

  Only a top-level result counts as present; a peer listed in `relatedLocations` isn't one. GitHub reads neither `baselineState` nor custom fingerprint keys such as `findingId/v1`. ADR-050 pins all four parts for all three files:
  - **one constant tool name per file, distinct across the three files**, keeping today's names verbatim: `Tachi`, `tachi-risk-scorer` and `tachi-control-analyzer` (R-33). Renaming a tool re-keys its alerts, and one example has drifted from these names. Under a single shared name, uploading one file would overwrite another's alerts, which GitHub does for the same tool and category;
  - **the user's repo-relative architecture path.** Nothing records it today: `/tachi.threat-model` copies the architecture into the run directory, and the downstream commands find that snapshot.
    - `/tachi.threat-model` writes the path as a body line in `threats.md`, which needs no schema bump.
    - The scorer and controls commands read it. The precedence is the override flag if given, then the body line, then `docs/security/architecture.md`.
    - The path is validated as NFR-10 prescribes and normalized as repo-relative before it is emitted. A path outside the repository falls back to a stated value, with a warning.
    - The carrier lands in Track R if SV-4 can fire, and ADR-050 item 7 designs it;
  - **a hash recipe built from a stable per-finding key.** Finding IDs are stable only under baseline carry-forward; stateless runs renumber;
  - **RESOLVED findings are never results.** GitHub doesn't read `baselineState`, so a RESOLVED result counts as present in the run that resolves it, and its alert closes one run late.

  The upload instructions show all three uploads, each with its own category. Today's guide has two snippets that disagree. One uploads only `docs/security/threats.sarif`, with no category, from a path a default run doesn't write. The other uses `category: threat-model`, which `threats.sarif` keeps (FR-E.11).
- **The N/N rule.** Each SARIF file accounts for every finding exactly once, so a consumer can count findings from the file alone. ADR-050 states the counting rule for the mechanism it picks.
  - A finding reference in `relatedLocations` needs a machine-readable marker, because the controls SARIF also lists code-evidence locations there.
  - The controls renderer needs a named source for correlation-group membership: `threats.md` Section 4a, or a group map in the scorer's output.
- **PM principles, in rank order** (ruling R-3):
  1. **No false fixed.** A finding present in the current run never closes its alert; a regroup, a change of primary or a tachi upgrade is not a fix. This holds across baseline-aware runs, because a stateless run renumbers its findings and re-keys its alerts (R-29). A one-time identity migration at upgrade is allowed only when ADR-050 shows there is no compatible option. The release notes then say which alerts close and reopen once, and that dismissals must be re-applied.
  2. **One alert per finding, across runs.** A finding that is still present keeps the same alert, so its dismissals and history stay with it.
  3. **Exactly once.** As stated above.
  4. **Volume.** Where principles 1 to 3 allow, alerts track correlation groups. If principle 1 needs one result per deduplicated finding, the higher alert count is accepted; it never exceeds the deduplicated finding count, and the release notes state it.
- **Membership is ADR-050's to pick**, with the asymmetry in view:
  - The controls SARIF already emits peers as results; the maestro-reference controls SARIF has 112 results, against 35 in its scorer SARIF. "Primaries only" would therefore close every controls peer alert once, which breaks principle 1.
  - "Stable primaries" needs the baseline's SARIF membership, which is SV-3 territory.
  - Both reviews point toward one result per finding.
- **The migration ships in this patch** (ruling R-1). On the scorer and controls path, identity already churns on every run, so a stable key is a fix. The release notes carry it (§8).

### D-6: score-inheritance rules (N15), ranked

- **(a) Editorial.** The SARIF-count text is reworded once, after ADR-050 fixes the membership rule, in all seven places:
  - `risk-scorer.md:450`, `:456`, `:474` and `:548`;
  - `control-analyzer.md:345`, `:394` and `:402`.
- **(b) Peers vs zero drift.** In rank order (ruling R-4):
  1. **A finding's own inputs carry forward.** A carried finding's inputs are the most granular values its baseline stores, inherited verbatim until one of them changes: the vector, the dimension sub-scores, the reachability inputs and the human governance fields (risk owner, overrides). Today's baselines are coarser. No committed example stores sub-score tables, and the markdown carries only some vectors. For such a legacy baseline, the exploitability, scalability and reachability values are the inputs, kept verbatim. The CVSS base score is checked against the vector under R-9, with the vector taken from the markdown or else from the baseline SARIF's `cvss-vector` property (R-26). Group membership and the identity of the primary are not inputs. A regroup or a new primary never changes a carried score, band or SLA on its own. Today the primary is the first ID listed in the group, and groups are recomputed on every run.
  2. **Derived fields are always recomputed:** the composite, the band, and the SLA, disposition and review date that follow from the band. RESOLVED rows are excepted (R-30). This supersedes `risk-scorer.md:71-76` for derived fields.
  3. **One score per group, at the group level.** A group shows its primary's score. A NEW or UPDATED peer inherits from its primary, as today (R-31). An UNCHANGED peer keeps its carried score; when that differs from the primary's, the output flags the divergence instead of overwriting the score.
  4. **Every change to a carried value is flagged, with its cause.**
- **Edges, for ADR-050 item 9** (R-31):
  - The original scoring date isn't stored. It is derived as the stored review date minus the stored SLA. Where either is missing, ADR-050 item 9 picks a fallback that never restarts the clock silently, and the case is flagged.
  - An override is recognized by rule. An Accept or Transfer disposition is always human, and so is any SLA or disposition that differs from the **stored** band's default, never the recomputed band's.
  - Overrides are carried verbatim and marked as overrides in the output. A model slip that the rule takes for an override then stays visible.
- **The SLA clock** (ruling R-5). A band corrected by recomputation keeps the finding's original scoring date, so its review date moves to the corrected SLA from that date. Only an input change restarts the clock (today's UPDATED rule, `risk-scorer.md:378-382`).
- **(c) One baseline per run** (ruling R-6).
  - Every stage inherits from the baseline run the threat model used: the scorer and the control analyzer read their baseline files from the directory of `threats.md`'s `baseline.source`.
  - The commands gain an explicit override flag, which also covers a baseline run scored with `--output-dir`.
  - If the baseline file is missing, the stage scores fresh and records why.
  - Since #391 Part A, the scorer writes to its output directory, so today's "same directory" rule doesn't point at the baseline run's directory. The control analyzer has the same gap.
- **A missing vector is never fabricated** (ruling R-7). The finding keeps its inherited score, with `cvss_vector: null`, and is flagged "unverifiable" (not "mismatch"). It changes only if the agent re-assesses it and records that judgment.

### D-7: verified at scale, cheaply where possible

- **The fixture** (Arch 6; TL C-11) comes from a fixed-seed generator, modeled on `tests/scripts/generate_pagination_fixture.py`. It emits:
  - an architecture description of about 25 components;
  - a synthetic baseline run directory: a `threats.md` with 200+ findings and 40+ Critical, correlation groups and chain material, plus `attack-trees/`, `risk-scores.md`, `compensating-controls.md` and all three SARIF files;
  - a seeded-error variant: wrong composites, bands, vectors and reachability values, missing vectors, and the documented exceptions as controls, for each prefix;
  - a legacy-format baseline variant, like the baselines adopters have today: no sub-score tables, partial vectors in the markdown, full vectors in the SARIF, with seeded composite and vector errors (R-26);
  - a tagged component for the asset-modifier step, including a finding assessed above 9.2 and a carried legacy finding of that kind (R-25), and boundary ties for a composite and a residual (R-11);
  - the two-run pair in which correlation regroups carried findings;
  - a stub codebase for the controls stage.

  It is **sized so every batched path runs at least twice** against OQ-5's thresholds: at least two `threats.md` parts, and at least two scorer, controls and tree batches.
  - Each single-response output it targets is at least twice the 64k cap. For `risk-scores.md`, at about 395 tokens per finding, that means roughly 325 findings.
  - A Run-B-scale variant (~390 findings) covers the orchestrator's own outputs.
  - Each stage's record counts its parts and batches (NFR-5).
  - Only a Mermaid-free subset goes into gated CI.
- **The stages are decoupled where stock commands allow.** The scorer and controls stages run on precomputed synthetic inputs.
  - No command dispatches the report agent on its own, so the report runs live only through the threat-model runs' Phase 5. Its `effort=max` coverage is the threat model's max run (R-28).
  - The threat-model stage runs baseline-aware against the synthetic baseline, so the 200+ findings and 40+ Critical come from the baseline rather than fresh discovery (#397 N9 records that new findings rarely reach Critical).
- **Offline evidence comes first.** The deterministic claims get offline evidence: SC-2's repeat check if the chain script is adopted, SC-4, SC-5 and SC-6. The live runs prove only what needs a model: agents staying on contract, and complete outputs.
- **A pre-fix baseline on the fixture** makes SC-1 non-vacuous. It has two parts:
  - a token measurement showing that each targeted output exceeds one response;
  - one v4.48.4 run of the cheapest stage (the scorer on the fixture's precomputed `threats.md`) that reproduces the overflow or the dropped finding.
- **Effort levels** (ruling R-18). Every live stage runs at the adopter default effort, meaning a session launched without an effort override.
  - The scorer and controls stages also run at `effort=max`, and the report runs at max through the threat model's max run (R-28). Reasoning-driven overflow is plausible there; Run B's scorer ran at `effort=max`, inherited from the session.
  - If TW-L1 fires, the scorer and controls keep both levels, while the threat-model and PDF runs use the default only. That drops the report's max run, which the PM re-review accepted.
- **SC-8's baseline.** In the same session as the pre-fix run, one v4.48.4 run of the scorer and controls stages on one shipped example's `threats.md`. SC-8 gates on output tokens, with a stated tolerance. Wall time is recorded but not gated.
- **Code Scanning evidence** (optional). If it fits W5, the two-run fixture's SARIF is uploaded once to a scratch repository with Code Scanning, and the PR records which alerts close and reopen. Otherwise the release notes say that the alert behavior is modeled from GitHub's documentation (FR-E.2).
- **The isolated-operation runbook is re-validated** (R-27). The bundle adds write locations and changes the write sets of agents and commands, which trips the runbook's own refresh trigger.
  - **The run.** The small smoke run runs under the published session profile, covering `/tachi.threat-model`, `/tachi.risk-score` and `/tachi.compensating-controls`, with a before-and-after write listing like re-check R6.
  - **The header.** It advances only on a pass. Under TW-L2, a shipped-code defect is fixed and the run repeated once; otherwise the header says it predates this release, and a follow-up is filed.
  - **The PDF stage.** `/tachi.security-report` stays outside the profile on macOS.
  - **SC-8.** The scorer and controls part can double as SC-8's post-fix comparison run.
- **Budget gates.**
  - **Attempts:** at most two live attempts per stage and effort level, with the disposition decided in advance: fix a shipped-code defect and re-run once, or record an agent leaving its contract honestly and file a follow-up (KB Entry 22).
  - **TW-L1 to TW-L3** (feasibility check §4) re-plan the matrix if the first fixture threat-model run exceeds its budget.
- **Measuring SC-3.** Each fixture run gets a structure-only transcript audit, kept private: subagent types, Bash calls that run unshipped scripts, and Writes of program files. Two cheap in-run signals back it:
  - the renderer stamps every output with its version and an input digest;
  - a post-run check asserts that the output directory holds only declared paths.

### v1.1 rulings

| # | Topic | Ruling | Source |
|---|---|---|---|
| R-1 | Release type | Keep `fix:`; the release-note content in §8 is binding | PM 5; Arch 20 |
| R-2 | SARIF scope | D-5 covers all three SARIF files, whichever tier authors each | PM 1; TL C-1; Arch 3 |
| R-3 | D-5 principles | No false fixed → one alert per finding → exactly once → volume | PM 7 |
| R-4 | D-6(b) | Own inputs carry forward → derived fields recomputed → one score per group (NEW peers inherit, UNCHANGED peers keep theirs and divergence is flagged) → every change flagged | PM 4; Arch 13 |
| R-5 | SLA clock | A correction keeps the original scoring date; only an input change restarts it | Arch 13 |
| R-6 | Baseline | One per run, from `threats.md`'s `baseline.source`, with an explicit override flag | PM 8; Arch 14 |
| R-7 | Missing vector | Never fabricated: inherited score, `cvss_vector: null`, flagged unverifiable | PM 8; Arch 14 |
| R-8 | Hand-off granularity | One record per dispatch, possibly empty; a per-dispatch manifest if SV-2b fires | Arch 2 |
| R-9 | Vector/score mismatch | Corrected and flagged, outside the documented clamps | PM 12; Arch 8 |
| R-10 | N17-dependent cases | Reported as "unchecked", never as violations; SC-4 counts decidable cases only | PM 12; Arch 8 |
| R-11 | Rounding-only differences | Normalized and counted in the run summary, not flagged per finding, but only when the band, SLA, disposition and review date all stay the same. A rounding difference that moves the band is flagged per finding as a band correction, and R-5 applies *(amended in v1.2)* | TL C-10; PM r2 31 |
| R-12 | Cut priority | See §10 | PM 10 |
| R-13 | #356 | Folds in if FR-O.1 moves Phase 3's table emission into code; otherwise NG4, with each renumbering recorded and today's behavior pinned in a test | PM 2; TL C-8 |
| R-14 | #408 | FR-N4.1 implements its body-instruction option. A run-time bound folds in only if it validates live within the attempt cap; otherwise #408 stays open for it | PM 11 |
| R-15 | #409 | Its dispatch-target check folds in if the plan finds it small; otherwise it is sequenced right after | PM 11 |
| R-16 | #412 | Its SARIF `informationUri` fix folds in | TL C-14 |
| R-17 | Adapter copies | The Claude Code adapter copies of edited specs get a superseded-by header and a follow-up in the #369 family. A warning at the top of the adapter README says to install with `scripts/install.sh`, and never to copy that directory over `.claude/agents/tachi/` *(v1.2)*. The installed SARIF guide is updated or retired (FR-K8.3). Other adapters: NG10 | PM 18; TL C-12; Arch 24; PM r2 41 |
| R-18 | Effort matrix | Default effort for every live stage, plus `effort=max` for the scorer and controls, and for the report through the threat model's max run. The TW-L1 fallback is accepted: the scorer and controls keep both levels, and the threat model and PDF run at the default only | Arch 27; TL C-3; PM r2 |
| R-19 | Chain formation | Recommended in shipped code. If ADR-050 keeps it in the model, SC-2 becomes "the algorithm and counts recorded" | TL C-2; Arch 7; PM 16 |
| R-20 | The `CF` column | Defined as the carried-forward marker that `carry_forward_count` counts, not dropped | PM 21 |
| R-21 | K4 scope guard | A fix that changes which findings join chains comes back to the PM before it is built | PM 23 |
| R-22 | FR-N4.4 scope | Binds the orchestrator. The infographic and report-assembler agents, which are Bash-capable by design, are out of scope here | Arch 26 |
| R-23 | Carve order *(v1.2)* | SV-3 is not a budget carve: it fires only on its technical trigger, at ADR-050. Budget carves go in reverse PM priority, and only carves that shorten the projection count: SV-2b, then SV-1, then TW-R's fallback (controls Sections 2 and 4 authored against the single template), then the SV-4 track split. "Never carved" gains D-5's membership and identity for all three files, except through SV-3's technical trigger, and FR-N4.5 to FR-N4.7 | PM r2 28; Arch L9 |
| R-24 | Phase 3.5 record *(v1.2)* | A missing or inconsistent record never ends the run. It becomes "skipped" with the reason, is reported and warned on, and is covered by a test. D-3's list of run-ending paths stays at three | PM r2 30; Arch M4 (deferred to the PM) |
| R-25 | Asset-modifier ceiling *(v1.2; PM r3, amended)* | The asset modifier never lowers a finding's score. A tag raises the base score to the elevated vector's score, capped at 9.2, and a finding whose assessed (pre-modifier) score is already above 9.2 keeps it. In effect the result is the larger of the assessed score and the capped elevated score, which is the reading of `asset-modifiers.md:59` and the floor-only rule at `:41`. **R-9:** its vector check treats these outcomes as documented clamps. **Legacy baselines:** some carried findings store only the elevated vector and an elevated score above 9.2, so the outcome would depend on an unrecorded assessed score; they keep the stored score, reported as unchecked (R-10). **NG7** stands: the ceiling's value doesn't move. **N17(a):** settled here for this bundle, NG2's list drops it, and the scoring/delta bundle inherits this reading. **Fixture:** the tagged component includes a finding assessed above 9.2, and a carried legacy finding of that kind | Arch M7; PM r3 |
| R-26 | Legacy baselines *(v1.2; PM r3, amended)* | A carried finding's inputs are the most granular values its baseline stores. A legacy baseline stores no sub-scores or barrier counts, so three rules apply to it. The exploitability, scalability and reachability values are the inputs, kept verbatim. The CVSS base score is checked against the vector under R-9, because the vector is the more granular value: it comes from the markdown, or else from the baseline SARIF's `cvss-vector` property; if both carry one and they differ, the markdown's is used and the disagreement is flagged; if neither does, R-7 applies. The composite, the band and the governance fields are recomputed. The legacy-format fixture variant carries seeded composite and vector errors, so SC-4 shows correction on the format adopters have today | Arch M8; PM r3 |
| R-27 | Runbook re-validation *(v1.2; PM r3, amended)* | The small smoke run runs under the published session profile and covers every command whose write set this bundle changes: `/tachi.threat-model`, `/tachi.risk-score` and `/tachi.compensating-controls`. It records a before-and-after write listing, as re-check R6 did, and the runbook's "Last validated" header moves to the build that ran. `/tachi.security-report` stays outside the profile on macOS (runbook §6), and this bundle doesn't change its write set. If the run finds an undeclared write or an unexpected denial, TW-L2's dispositions apply: a defect in shipped code is fixed and the run repeated once; otherwise the header isn't advanced, it says it predates this release, and a follow-up is filed. The runbook never claims a validation that didn't pass | Arch M10; PM r3 |
| R-28 | Report stage, live *(v1.2; PM r3, accepted)* | The report runs live only through the threat-model runs' Phase 5, with no harness dispatch. Its max coverage is the threat model's max run, which the TW-L1 fallback drops | Arch M11; PM r3 |
| R-29 | Identity scope *(v1.2; PM r3, accepted)* | Principle 1 and US-6 cover baseline-aware runs. A stateless re-run re-keys its alerts, and the release notes recommend keeping successive runs under the same output directory, so each run carries the previous run's IDs forward | Arch L3; PM r3 |
| R-30 | RESOLVED rows *(v1.2; PM r3, amended)* | **`risk-scores.md`** keeps them as history, as today. Their last-known values, governance fields included, are kept verbatim: never recomputed or flagged, and outside the SLA clock. Each is marked as resolved, so no reader can take it for an open finding; ADR-050 picks the marker, which must be additive and readable by tachi's parsers (NFR-1). The Executive Summary counts them separately, never in its severity distribution. **The controls report** omits them, as today. **No SARIF file** carries them, either as a result or in `relatedLocations`. The parity check compares `risk-scores.md`'s open rows with Section 7 and its RESOLVED rows with Section 4c, and the `.md`–`.sarif` agreement check compares open rows only | Arch L4; PM r3 |
| R-31 | Peers and overrides *(v1.2; PM r3, amended)* | UPDATED peers inherit from their primary, as NEW peers do and as today (`severity-bands.md:81`). The original scoring date is the stored review date minus the stored SLA; where either is missing, ADR-050 item 9 picks a fallback that never restarts the clock silently, and the case is flagged. A human override is any Accept or Transfer disposition, or any SLA or disposition that differs from the **stored** band's default, never the recomputed band's. Overrides are carried verbatim and marked as overrides in the output, so a model slip that the rule takes for an override stays visible instead of becoming permanent baseline data | Arch L5; PM r3 |
| R-32 | Scoring constants *(v1.2)* | Embedded in the renderer, with a drift test against `schemas/risk-scoring.yaml`. The core path needs nothing beyond the standard library, and PyYAML stays optional, for the PDF only | PM r2 43 |
| R-33 | SARIF tool names *(v1.2; amended in v1.3)* | One constant tool name per file, distinct across the three files, keeping today's names verbatim: `Tachi`, `tachi-risk-scorer` and `tachi-control-analyzer`. Renaming a tool re-keys its alerts. FR-E.1 corrects `risk-scorer.md:462`, which spells the first one in lowercase. FR-E.2 asserts that the three (tool, category) pairs differ | PM r2 39; Arch M5; PM r3 44 |

---

## 5. Functional Requirements

Pointers are to `main` at `b040fa1` (v4.48.4). `orchestrator.md`, `risk-scorer.md`, `control-analyzer.md`, `threat-report.md` and `attack-tree-delta.md` are the agent specs under `.claude/agents/tachi/`.

### Group A: orchestrator

Files: `orchestrator.md`; `.claude/skills/tachi-orchestration/references/`; `.claude/skills/tachi-shared/references/` (`attack-chain-patterns-shared.md`, `finding-format-shared.md`); `templates/tachi/output-schemas/threats.md`; `.claude/commands/tachi.threat-model.md`.

- **FR-K4.1 (outcome record).** Phase 3.5 writes its outcome to `threats.md` in every run, instead of skipping the artifact and setting an in-memory boolean (`orchestrator.md:486`, `:546-550`).
  - The `consumer-agent-app` sample report already records a zero-chain reason, which sets the precedent for the format.
  - **Coordination with #396.** This bundle lands first, and #396 rebases onto it. The plan picks one of two options:
    - record the outcome in the `threats.md` body, which needs no schema bump;
    - record it under a key that #396 then declares.

    The plan also corrects the stale "1.2" in the validation checklist (`output-schemas.md:285`).
  - Exempt from SV-1.
- **FR-K4.1b (outcome check).** The main session's post-run check (D-4) catches a missing or inconsistent outcome record and records it as skipped, with the reason. It never ends the run (R-24). A test covers each case. Exempt from SV-1.
- **FR-K4.2 (one algorithm).** The chain algorithm is reconciled between `orchestrator.md` Phase 3.5 (`:441-460`) and `attack-chain-patterns-shared.md` (`:127-143`).
  - The cross-prefix tie-break replaces "lower finding ID" (`orchestrator.md:449`).
  - The redundancy and surfacing rules are defined, and the run records the candidate, consolidated and surfaced counts.
  - The computational steps run in a shipped script if ADR-050 adopts R-19.
- **FR-K4.3 (root cause first).** The 5 Whys on Run A's skip is time-boxed at 0.25 day, with its disposition decided in advance (TW-K4). Run A's evidence may no longer exist. It weighs all four of #374's candidates:
  - orchestrator context pressure;
  - instruction ordering;
  - a skipped conditional;
  - link criteria that legitimately yield zero (STRIDE-only participation, `orchestrator.md:419`, or the structural-connection rule).

  #397 records that the earlier run's zero-chain result was a skip. Ruling R-21 applies.
- **FR-K4.4 (fixture).** On the synthetic large fixture, chain formation forms chains, `attack-chains.md` is bounded, and the report and the PDF show the chains.
- **FR-N4.1 (typed dispatch).** Phase 2 dispatches only typed `subagent_type`s, from one canonical roster (D-3).
  - Replaced text: the contract names no `subagent_type`, describes the agents as prompt files whose content is the payload, and leaves dispatch adapters out of scope (`orchestrator.md:278-280`, `:302`).
  - Removed or rewritten: the platform-neutral clauses at `orchestrator.md:68`, `risk-scorer.md:18`, `control-analyzer.md:20` and `threat-report.md:44`, plus the same clause in `report-assembler.md:52` and `threat-infographic.md:99`.
  - Corrected: the stale rosters in `coverage-requirements.md` and `finding-format-shared.md`, which list 5 of the 8 AI agents (output-integrity, misinformation and human-trust-exploitation are missing).
  - This implements #408's body-instruction option (R-14).
- **FR-N4.2 (dispatch records).** The orchestrator persists **one record per dispatch** under the run's `.tachi-build/` directory (R-8): the agent type, the scope, and the agent's findings verbatim, possibly none.
  - Phase 3 writes a map from each final finding ID to its source record.
  - The records always add orchestrator output. ADR-050 decides them together with FR-O.1, because that cost is offset only if code compiles Phase 3 and emits the tables (RK-4).
  - If SV-2b fires, the record shrinks to a per-dispatch manifest: agent, scope, count and provisional IDs.
  - The 14 threat agents stay read-only (NG8).
  - *Watch #356 here* (R-13).
- **FR-N4.3 (briefs).** A brief holds only the fields of the brief template's closed set: the target components, the agent's input pointers and the baseline focus. It points at the run's architecture snapshot, and at the Phase 1 inventory and dispatch table persisted under `.tachi-build/`, instead of copying them.
  - **Required:** each agent is dispatched with a fixed one-line prompt that tells it to read and follow its brief in `.tachi-build/briefs/`. The SC-3 audit compares each actual prompt with that line.
  - **Recommended:** a shipped script renders the briefs and the prompt from the dispatch table.
- **FR-N4.4 (no ad-hoc scripts).** The orchestrator runs only shipped scripts (R-22).
- **FR-N4.5 (provenance check).** After the orchestrator returns, the main session checks that every finding in `threats.md` has **exactly one** provenance entry, of one of three kinds:
  - a typed agent's dispatch record, found through the Phase 3 ID map;
  - a baseline carry-forward reference (UNCHANGED and UPDATED keep their baseline IDs, and Phase 3a discards a Phase 2 copy that matches a carried finding exactly or by similarity);
  - a named deterministic rule (Phase 3.6, `AGP-NN`).

  A run with no dispatch records fails, which catches mode 3. The check confirms the orchestrator's own record. It doesn't prove provenance, which is #399's job.
- **FR-N4.6 (record completeness).** The same check runs the other way. Like FR-N4.5, it confirms consistency, not provenance. Every finding in every dispatch record has exactly one disposition, recorded in the ID map:
  - kept as a finding;
  - matched to a carried finding by Phase 3a, exactly or by similarity;
  - merged into a named surviving finding;
  - superseded by a re-dispatch (FR-N4.7). A truncated dispatch's record is marked superseded and names the records that replace it, and its findings leave the completeness set.

  Every ID change is recorded, and an empty record set is an error. Tests cover carried, renumbered and pattern findings, plus an agent that is truncated and then re-dispatched in a stateless run.
- **FR-N4.7 (Phase 2 overflow).** The orchestrator detects a truncated or overflowed return and re-dispatches that agent per component, with capped retries. It records the event, or fails the run (D-3).
- **FR-O.1 (orchestrator outputs at scale).**
  - **SV-2a: membership and identity are never carved.** `threats.sarif` comes from a shipped generator over the compiled `threats.md`, sharing the renderer's D-5 emitter (R-2). Only SV-3 can carve identity, and then for all three files.
  - **Bounded emission.** `threats.md` is emitted in bounded parts that a shipped step joins.
  - **SV-2b: may be carved.** Rendering `threats.md`'s tables in code may be carved at TW-0 or TW-R. Bounded emission stays either way, and if it fires the hand-off becomes a manifest (FR-N4.2).

### Group B: threat report

Files: `threat-report.md`, `attack-tree-delta.md`, `.claude/skills/tachi-threat-reporting/references/`, `templates/tachi/output-schemas/threat-report.md`.

- **FR-K5.1 (whole report bounded).** No single response carries the whole report. A shipped step assembles `threat-report.md` from bounded part files: per section, and per batch of findings for the per-finding sections. Section 5 is one part, taken from the standalone tree files. The plan decides who runs the step: the orchestrator after Phase 5 returns, or `/tachi.threat-model`.
- **FR-K5.2 (inline equals standalone).** True by construction, because the assembly copies the tree files. A test checks it.
- **FR-K5.3 (carried-forward trees unchanged).** Carry-forward is a file copy done by the shipped step, not a model transcription. Run B's three edited carried-forward trees show what a transcription does. A test checks it.
- **FR-K5.4 (typed helpers).** The report agent's sub-dispatches are typed tachi agents only. In Run B it spawned 17 stand-ins.
- **FR-K5.5 (tree count).** Section 5 holds exactly one tree per Critical and High finding in `threats.md`, RESOLVED excluded. Code checks this against `threats.md`, not against the tree agent's manifest.
- **FR-K5.6 (tree batches).** A layer that runs Bash (the orchestrator, or `/tachi.threat-model`) batches the tree sub-dispatch and handles its overflow (D-3; ADR-050 item 6). No agent gains a tool. Each batch writes its own manifest under `.tachi-build/`, and the assembly step merges them into the schema-1.0 `.manifest.json`. Today Rule 2 regenerates every Critical and High tree after any delta, in one session.
- **FR-K5.7 (mode 2 check).** Every tree file is listed in the typed sub-agent's `.manifest.json`, and Section 5 is assembled by the shipped step. Like FR-N4.5, this confirms consistency, not provenance.
  - **What passes.** The manifest has no author field, so a helper that writes both the trees and the manifest passes.
  - **What it catches.** A helper that skips the manifest, or that writes the report itself, since the assembly step overwrites the report and D-7's stamp shows who wrote it.
  - **Transcript proof** stays with #399.

### Group C: risk scorer

Files: `risk-scorer.md`, `.claude/commands/tachi.risk-score.md`, `.claude/skills/tachi-risk-scoring/`, `templates/tachi/output-schemas/risk-scores.md`.

- **FR-K6.1 (row parity).** `risk-scores.md` rows equal the reference finding set (D-4). Rows the agent couldn't parse (`risk-scorer.md:179-182`) are listed in a defined place.
- **FR-K6.2 (SARIF N/N).** `risk-scores.sarif` is complete and identity-stable under D-5, and it agrees with the `.md` by construction.
- **FR-K6.3 (renderer owns the files).** The renderer writes both whole files (D-2).
- **FR-N14.1 (overflow).** No code hand-back. `/tachi.risk-score` owns batching and resume (D-3). Today `risk-scorer.md:93` leaves batching to the command, which invokes the scorer once (`tachi.risk-score.md:114-147`).
- **FR-N14.2 (renderer).** The renderer computes D-2's right-hand column and writes the whole `risk-scores.md` and `risk-scores.sarif`. It is shipped, tested, installed and listed under S-13.
- **FR-N16.1 (recompute and flag).** D-4 and D-6 apply:
  - recompute derived fields;
  - correct and flag vector mismatches;
  - check reachability ranges for unambiguous labels;
  - give every prefix a category;
  - report "unchecked" and rounding-only cases.

  The asset-modifier step is computed under R-25, and the formula in `asset-modifiers.md:56` is corrected to match when the renderer takes the step over. A tolerant baseline parser reads legacy baselines under R-26.
- **FR-N15.1 (inheritance).** (a) The rewording happens once, after ADR-050 fixes membership. (b) and (c) follow D-6.
- **FR-C.1 (adapter copies).** Ruling R-17.

### Group D: control analyzer

Files: `control-analyzer.md`, `.claude/commands/tachi.compensating-controls.md`, `templates/tachi/output-schemas/compensating-controls.md`, `.claude/skills/tachi-control-analysis/references/`.

- **FR-K7.1 (SARIF N/N).** `compensating-controls.sarif` is complete and identity-stable under D-5. Each peer is counted once, never as both a result and a `relatedLocations` entry.
- **FR-K7.2 (totals).** The renderer computes the residuals, the totals and the Section 5 tables (D-2), so totals equal the sum of the rows by construction. A test keeps that from regressing. Today `residual-risk.md` defines the totals as row sums, but the agent's check verifies counts only (`control-analyzer.md:353`).
- **FR-K7.3 (agreement).** The `.md` and the `.sarif` agree, by construction.
- **FR-K7.4 (the scorer's gaps).** Three of the scorer's fixes apply here too:
  - `/tachi.compensating-controls` owns batching and resume (`control-analyzer.md:133`);
  - the baseline is resolved under D-6(c) (`:116`);
  - the agent's input contract matches what the command passes. It says it receives file contents (`:52-62`), while the command passes paths.
- **FR-K8.1 (one Section 2 schema).** The schema includes MAESTRO Layer and Control Category. It is a renderer property, and the output-schema template documents it. The agent spec (`control-analyzer.md:349`) stops restating it. `CF` is the carried-forward marker (R-20).
- **FR-K8.2 (every table, and Section 4).** Every band table uses the schema, and Section 4 uses one block per finding, each joined to its finding. #373's K9 and K13 parsers read both the corrected and the pre-fix formats.
- **FR-K8.3 (the installed SARIF guide).** Once the renderer writes the controls SARIF, the guide that tells agents how to author it (`adapters/claude-code/agents/references/sarif-generation.md`) is updated or retired.

### Group E: shared

- **FR-E.1 (N/N and identity reference).** One shared reference covers all three SARIF files (D-5) and replaces the four contract copies. It corrects `sarif-specification.md:585` ("exactly N entries") and resolves the contradiction between `:339` and `:612`.
- **FR-E.2 (identity test).** An offline two-run test models GitHub's matching key and asserts, per file, that no still-present finding's key disappears and that an unchanged re-run's keys are identical. A cross-file assertion checks that the three (tool, category) pairs differ (R-33).
- **FR-E.3 (overflow and batching).** The structured overflow error and the batch planner's contract (input slicing, and resume from disk) are each defined once. Plans carry a fresh plan ID and the digests of their inputs, and every part file carries its plan ID and batch ID. A test seeds a stale part.
- **FR-E.4 (fixture).** The fixture generator and its outputs (D-7) are committed.
- **FR-E.5 (tests and wiring).** Tests run on synthetic fixtures only, across three gates:
  - **`tachi-install-fidelity.yml`** is the default for the renderer, checker and parser suites. Its scope includes S-13 and `tests/scripts/test_write_confinement.py`, which is extended to cover the new scripts.
  - **`tachi-pytest.yml`** takes only modules that need its cross-platform bash matrix.
  - **`tachi-permissions-verify.yml`** covers every agent, command, §8 or runbook edit.

  Each module is wired together with its input surfaces (scripts, schemas, references and fixtures) in its gate's `paths:` list and invocation, in the same commit. Every new script and the helpers it imports go into `INSTALL_MANIFEST.md`.
- **FR-E.6 (failure handling).** D-3's failure behavior applies, with a test for each path.
- **FR-E.7 (in-run signals).** These are the provenance stamp and the declared-paths check (D-7).
- **FR-E.8 (#409).** The dispatch-target static check, if it folds in (R-15).
- **FR-E.9 (#412).** The renderer writes the real `informationUri`, and the templates and instructions that carry the placeholder are corrected (R-16).
- **FR-E.10 (Section 6 parity).** `threats.md` Section 6's counts and percentages are checked against the reference finding set (D-4). They stay model-written unless SV-2b's table rendering ships.
- **FR-E.11 (upload instructions).** Both of the developer guide's Code Scanning snippets (`DEVELOPER_GUIDE_TACHI.md:1118-1135` and `:1692-1712`) upload all three SARIF files, each with its own category, from a run's timestamped output directory. `threats.sarif` keeps `category: threat-model` (D-5; R-33).

---

## 6. Interface Contract

- **`compensating-controls.md` Sections 2 and 4.** The renderer writes them, the output-schema template documents them, and #373's parsers still accept the pre-fix format.
- **Phase 3.5 outcome.** Always recorded in `threats.md`, and checked by the main session. A bad record becomes "skipped" and never ends the run (R-24). Consumers fall back to file presence when it is absent. #396 coordinates (FR-K4.1).
- **SARIF, all three files.** One N/N rule, and identity pinned to GitHub's matching key: a constant tool name per file, distinct across the three (R-33); the repo-relative architecture path, carried in `threats.md`'s body; and a per-finding hash recipe. RESOLVED findings are never results. A peer marker sits in `relatedLocations` (D-5).
- **Dispatch records.** One per dispatch, under `.tachi-build/`, attributed to the agent, with the Phase 3 ID map (FR-N4.2).
- **Part files.** JSON, with a versioned schema, under `.tachi-build/`. They carry judgment and prose fragments, and each carries its plan ID and batch ID (FR-E.3). They are validated as untrusted input (NFR-10).
- **Overflow error and batch plan.** The error is advisory, and resume is reconciled from the files on disk (FR-E.3).
- **Adopter-facing outputs.** `threats.md`, `risk-scores.md`, `compensating-controls.md` and the three SARIF files keep their sections and fields. Changes are additive, with three exceptions:
  - corrected values (composites, totals, bands, base scores);
  - D-5's membership and identity change;
  - K8's Section 2 columns (MAESTRO Layer and Control Category added, `CF` defined).

---

## 7. Non-Functional Requirements

- **NFR-1: compatibility.**
  - **A small-run oracle**, run in a scratch clone, covers each shipped example that has scorer or controls output. The renderer's output keeps every section and field, and every value diff is attributed to a corrected value or to D-5.
  - **Parsers keep working.** They read by header name. A round-trip test checks that the renderer's output, parsed by `tachi_parsers`, equals the renderer's input.
  - **Old inputs render the same.** The PDF and infographics render them byte-identically.
  - **Additive schemas.** The frozen enum and ceiling are unchanged (NG7).
- **NFR-2: determinism and imports.**
  - The renderer's output is byte-stable for the same input. The scoring date is an input, not the clock.
  - Stdlib-only imports at load time are enforced by S-13, with the renderer and its helpers added to its list (D-2).
  - The core path also needs nothing beyond the standard library at run time. The scoring constants are embedded with a drift test (R-32), and PyYAML stays optional, for the PDF only.
  - Bytecode is suppressed (ADR-049 D8).
  - ADR-050 pins the arithmetic:
    - half-up `Decimal` rounding on the stored one-decimal inputs, because Python's `round()` gives 4.5 for the documented 4.55 → 4.6;
    - inclusive band boundaries;
    - CVSS Roundup;
    - the review-date and SLA rules.
- **NFR-3: privilege and confinement.** No agent gains a tool (NG8).
  - **Where intermediates go.** Every file an agent writes as an intermediate (part files, dispatch records, briefs) sits under the run's `.tachi-build/` directory, the ADR-049 D7 precedent. `$TMPDIR` is only for temporary files that scripts create through `tempfile`.
  - **The declarations this changes:**
    - ADR-049 D7, for the scorer's writes;
    - the Writes cells in `docs/standards/CLAUDE_PERMISSIONS.md` §8.3 and §8.4, and the "Written by" column in §8.5;
    - the `/tachi.compensating-controls` row, which gains `python3` under "Bash it instructs" and "Child processes";
    - the runbook's §5 write table. Its §2 and §10 hold no shell lists, because §10 links the matrix at the release tag. The session profile stays unchanged: any edit changes its pinned SHA-256, and R-27 covers re-validation.
  - **Every new path is listed**, because C7 can't see an undeclared one:
    - the dispatch records and the briefs;
    - the persisted Phase 1 inventory and dispatch table;
    - the Phase 3 ID map and the batch plans;
    - the scorer, controls and report part files, and the `threats.md` parts;
    - the per-stage records (NFR-5);
    - the file names D-3 gives failed outputs.
  - **What guard C7 can and can't see.** C7 checks that these declarations agree with one another, so it can't see an undeclared path. Review enforces declaration, and `tests/scripts/test_write_confinement.py` enforces script writes.
- **NFR-4: cost.** Below the batching threshold, each agent is invoked once. The PR records token usage and wall time for the fixture runs and for one shipped example (SC-8).
- **NFR-5: observability.** Each stage writes one small JSON record (counts, batches, overflow events, retries) in a form #399's manifest can ingest.
- **NFR-6: public hygiene.**
  - Issues, PRDs, specs, PRs and the CHANGELOG describe the defects generically, with no real-world findings, threat text, IDs or report content. Fixtures are synthetic.
  - Public text never lists which agent specs or sections the private N3 fix touches.
- **NFR-7: CI.**
  - Three gates, with lock-step wiring of each module and its input surfaces (FR-E.5).
  - The gated suites clone the committed HEAD, so commit before running them.
  - About 19 failures outside the gate pre-exist and are known.
  - Every push costs about 33 minutes on two operating systems, so plan one push per wave.
- **NFR-8: images.** Re-rendered example PNGs are never committed (#365). Commits stage explicit paths only.
- **NFR-9: portability.** Any command or shell change runs on bash 3.2 and on both GNU and BSD userlands.
- **NFR-10: the trust boundary of the shipped scripts.** The scripts are the renderer, the assembly steps, the `threats.md` joiner, the `threats.sarif` generator, the chain script and the checks. Every agent-authored file they read is untrusted input:
  - the part files and the dispatch records;
  - `threats.md` and its parts;
  - `risk-scores.md`, which is the controls renderer's input;
  - the tree files and `.manifest.json`;
  - the baseline run's `risk-scores.md`, `compensating-controls.md` and SARIF files (D-6, R-26).

  The rules:
  - **Strict JSON.** JSON inputs are parsed against a closed, versioned key set, with types and ranges. Unknown keys, NaN, Infinity, duplicate IDs and IDs outside the batch's list are all rejected.
  - **IDs before paths.** The finding-ID allow-list `^(S|T|R|I|D|E|AG|AGP|LLM|OI|MI|TE)-\d+$` is applied before any ID becomes part of a path, with a resolved-path containment check as a backstop (the KB Entry 24 class).
  - **Paths come from the command**, never from file content. Three paths must be read from files: `threats.md`'s `baseline.source`, `risk-scores.md`'s `source_file`, and the architecture path in `threats.md`'s body (D-5). That last one becomes every SARIF result's `artifactLocation.uri`, so it is also normalized as repo-relative before it is emitted. They are validated as KB Entry 24 prescribes: a regular file, not a symlink, with the expected name, under the working directory, compared by resolved identity. The command's override flag takes precedence.
  - **No forged structure.**
    - `|`, backticks and newlines are escaped in table cells, and SARIF's string rules are followed.
    - After rendering, no prose line begins with `#` or `|`, so a fragment can't forge a heading that the parsers, which find sections by substring, would pick up.
    - Raw HTML is escaped.
    - Code snippets from the scanned repository use a fence longer than any backtick run inside them.
  - **Limits.** Each file has a size cap, there is no `eval` or `exec`, and writes go only under the output directory (ADR-049 D5).

  Tests seed a stale part, a forged heading and a fence break-out. The Step 7 security review names each new script.

---

## 8. Definition of Done

- **The fixture** (D-7) and its generator are committed, with a Mermaid-free subset in gated CI.
- **Pre-fix baseline.** It is recorded on the fixture as SC-1's baseline column.
- **The live matrix** (D-7, ruling R-18) is recorded in the PR, with each stage's disposition decided in advance and TW-L1 to TW-L3 applied. The SC-3 transcript audit is structure-only, and stays private.
- **Regression tests**, all on synthetic fixtures:
  - count parity;
  - totals;
  - record completeness and provenance (with carried, renumbered, pattern and superseded findings);
  - SARIF N/N, the identity model of GitHub's key, and distinct (tool, category) pairs;
  - recompute-and-flag;
  - vector correction, "unchecked" and rounding classes, including band-moving ties;
  - the regroup case, the legacy-format baseline and the tagged asset-modifier case;
  - renderer goldens, with the date as input;
  - the round-trip;
  - every failure path, and the Phase 3.5 "skipped" cases;
  - hostile input: invalid parts, a stale part, a forged heading and a fence break-out;
  - write confinement.

  Each is wired into its gate in lock-step (FR-E.5).
- **ADR-050** is accepted at the plan stage, before any build wave (TW-ADR). It covers §13's list.
- **Install manifest and S-13.** Every new script and the helpers it imports are listed, bytecode is suppressed, and the #373 completeness check is green.
- **Privilege declarations** are updated (NFR-3), and `tachi-permissions-verify.yml` is green.
- **The isolated-operation runbook** is re-validated and its "Last validated" header updated, or the header is marked as predating this release, under R-27.
- **The small-run oracle** passes (NFR-1), in a scratch clone.
- **Release notes**, binding (ruling R-1). They say plainly:
  1. **SARIF:**
     - whether any alerts close and reopen once, and if so which ones, and that dismissals must then be re-applied;
     - that scorer and controls alerts stop churning from then on;
     - whether the alert count rises, up to one per deduplicated finding;
     - that each file keeps its tool name and is uploaded with its own category, as the updated snippets show, and that an earlier `threats.sarif` upload without a category can remain in Code Scanning as a stale configuration, which adopters remove once;
     - that identity is stable across baseline-aware runs, so successive runs belong under the same output directory, while a stateless re-run re-keys its alerts; and that moving or renaming the architecture file re-keys every alert once;
     - if no scratch-repository check ran, that the alert behavior is modeled from GitHub's documentation;
  2. **Runs that stop.** A run now stops when a typed agent can't be spawned, a finding can't be traced or accounted for, or a batch can't finish. The notes say what to do: re-run `install.sh` for an install gap;
  3. **Scores:**
     - that carried scores are recomputed, and how to read the correction, "unverifiable" and "unchecked" flags;
     - which baseline the scorer and controls now inherit from (`threats.md`'s `baseline.source`), and the override flag;
     - that a corrected band keeps its original scoring date, so some findings can become due or overdue at once, and that the correction flag tells these apart from real slips;
     - that human overrides are carried verbatim and marked as overrides;
  4. **Rendering.** The scorer and controls files are now rendered, and the controls Section 2 schema changes. RESOLVED rows in `risk-scores.md` are marked as resolved and counted separately;
  5. **Split valves.** If a split valve fired, what still isn't resilient.
- **PR and release.** The PR is titled `fix(374): …` from the draft onward, and the release is a patch.
- **Hand-offs.** This bundle lands before #364's re-score, and N16's example audit leads are posted to #364.
- **Issue bookkeeping.**
  - Tick N4, N12, N14, N15 and N16 in #397 (N12 unless SV-3 fires).
  - Close #357 if subsumed, and #412.
  - Update #408 and #409 per rulings R-14 and R-15.
  - Close #356 if R-13 folds it in.
  - File R-17's follow-up for the adapter copies, in the #369 family.
  - If SV-1 fires, file FR-K4.2 to FR-K4.4 as their own issue.
  - Note on #397 that N17(a), the 9.2 ceiling's scope, is settled here (R-25).
- **Public text** describes the defects generically (NFR-6). No real-world run output is committed.
- **Live confirmation** happens on the next large real-world run, after the release. It is tracked outside this feature.

---

## 9. Success Criteria

| # | Criterion | Baseline | Target |
|---|---|---|---|
| SC-1 | Each changed stage on the synthetic large fixture | Measured on the fixture at v4.48.4: token estimates, plus one scorer run (D-7) | Complete N/N outputs; 0 hand-assembled files; record completeness (FR-N4.6) and the tree count (FR-K5.5) pass |
| SC-2 | Phase 3.5 | Nothing recorded; a skip looks like zero | Outcome recorded in 100% of runs; the post-run check catches a missing or inconsistent record and records it as skipped, with the reason (R-24). The chain fixture forms chains. With the chain script: byte-identical chains on a fixed finding set, offline. Without it: the algorithm and counts recorded (R-19) |
| SC-3 | On-contract execution in fixture runs (transcript audit plus in-run signals) | Run B: 33 stand-ins; outputs rendered by orchestrator-written scripts; one code hand-back | 0 `general-purpose` dispatches; 0 unshipped scripts run; 0 program files written; 0 code hand-backs; every rendered output stamped; only declared paths in the output directory |
| SC-4 | Inherited scores on the seeded baseline, decidable cases | Errors carried forward silently | 100% of seeded composite, band and vector errors corrected and flagged; 100% of seeded out-of-range reachability values flagged (unambiguous labels); 0 documented exceptions flagged; N17-dependent cases reported as unchecked; rounding-only differences counted, not flagged, unless they move a band; 0 carried scores changed by a regroup alone; 100% of seeded peer divergences flagged; the legacy-format baseline and the tagged case handled under R-26 and R-25 |
| SC-5 | Controls report | Drifting tables; totals ≠ sum of rows; blank recommendations (#373 K13) | One schema in every band table; totals equal the sum of the rows; `.md` and `.sarif` agree; 0 unjoined Section 4 recommendations; #373's parsers read the corrected and pre-fix fixtures |
| SC-6 | SARIF identity under GitHub's matching key, per file, on the baseline-aware two-run fixture (offline) | Scorer and controls alerts churn on every run; regrouped `threats.sarif` results drop out (38 in Run B) | For each of the three files: 0 still-present findings lose their key; an unchanged re-run's keys are identical; the three (tool, category) pairs differ |
| SC-7 | Release | — | A `fix(374)` patch release whose notes carry the five §8 items |
| SC-8 | Small runs | One v4.48.4 run of the scorer and controls on one shipped example's `threats.md` (D-7) | The small-run oracle passes; output tokens on that example are no worse than the baseline, within a stated tolerance; wall time is recorded, not gated |
| SC-9 | Live confirmation *(lagging; tracked outside this feature)* | — | The next large real-world run completes every stage with no stand-ins, no hand assembly and no code hand-back |

---

## 10. Bundle & Split-Valve Strategy

**Lanes follow files.** Several items edit each hot file: about ten edits land in `orchestrator.md`, about eight in `risk-scorer.md` and about six in `control-analyzer.md`. So each hot file has one lane per wave. The team-lead's plan (`specs/374-large-architecture-pipeline-resilience/feasibility-check.md` §3) has these lanes:
- S: shared contracts;
- R: renderer code;
- C: scorer contracts;
- D: controls contracts;
- O: orchestrator contracts;
- OC: orchestrator-side code;
- T: report;
- P: parsers;
- F: fixture;
- X: wiring;
- L: live.

**The cut line is the end of W1**, with both CI legs green. By then these are committed:
- ADR-050, accepted at the plan stage;
- the shared references: N/N and identity, the overflow error and batch plan, the dispatch-record and brief templates, the part schema and the roster;
- N4's and N14's contract text: typed dispatch, no code hand-backs and the overflow contract;
- the renderer core and its tests;
- the fixture and its generator.

After the cut line, Track R (the renderer, the scorer and controls contracts, and the K8 parsers) and Track O (the orchestrator, the report, the chain script, the checks and the K4.1 readers) are independent.

**PM priority for waves and any cut** (ruling R-12):
1. N4's and N14's contract text, which lands by the cut line, so every shape ships it;
2. the scorer renderer, with K6, N16 and N15(a);
3. D-5's identity rule across all three SARIF files;
4. K7 and K8;
5. K5;
6. K4, with FR-K4.1 and FR-K4.1b protected.

**Budget carves** (TW-0, TW-R and TW-ESC; ruling R-23) go in reverse PM priority, and only carves that shorten the projection count:
1. SV-2b;
2. SV-1;
3. TW-R's fallback, in which controls Sections 2 and 4 are authored against the single template;
4. the SV-4 track split.

The full adapter port is already out (R-17), and the optional fold-ins under R-14 and R-15 are the first to drop. SV-3 is not a budget carve.

**Never carved:**
- FR-K4.1 and its check;
- FR-N14.1;
- the risk-scores renderer;
- FR-N4.5 to FR-N4.7;
- D-5's membership and identity for all three files, except through SV-3's technical trigger.

**Split valves.**
- **SV-1 (K4).** If the 5 Whys points to orchestrator context pressure that the chain script and the rendered outputs don't remove, move FR-K4.2–K4.4 to their own issue. FR-K4.1 and FR-K4.1b stay.
- **SV-2a and SV-2b.**
  - SV-2a: `threats.sarif` membership and identity stay, always.
  - SV-2b: rendering `threats.md`'s tables in code may be carved. If it fires, bounded emission still keeps `threats.md` complete, so SC-1 still applies to the threat-model stage, and the dispatch records shrink to a manifest (FR-N4.2).
- **SV-3 (implementing N12).** This fires only if ADR-050's mechanism needs cross-run state beyond the baseline the stage already reads. The rule is then decided here and implemented in the scoring/delta bundle. US-6 and SC-6 come out of the release claim, and the release notes say so. SV-3 is never used to cut schedule (R-23).
- **SV-4 (the track split).** Pre-authorized, and fires only through TW-0 or TW-ESC. Track R ships first as `fix(374)` PR 1, once its live runs pass. Track O follows as PR 2 under the same issue, **based on `main`, not on PR 1's branch**, so that merging PR 1 with `--delete-branch` can't close it (KB Entry 25). PR 1's notes don't claim SC-2, SC-3 or US-4, and claim identity only for the scorer and controls SARIF. The architecture-path carrier (D-5) lands in Track R.

Where `feasibility-check.md` §3.4 or §4 differs from this section, this section governs.

**Trip-wires** (definitions in `feasibility-check.md` §4):
- at `/aod.tasks`: TW-0 (aggregate, 9.0 days), TW-ADR (rulings present), TW-R (renderer budget) and TW-N3 (ordering);
- at the end of W0: TW-K4;
- during the build: TW-ESC (end of session 1), TW-CI, TW-L1 to TW-L3, and TW-CTX (orchestrator peak context).

---

## 11. Timeline & Milestones

Sized 1:1 from the team-lead's feasibility check (`specs/374-large-architecture-pipeline-resilience/feasibility-check.md`; APPROVED_WITH_CONCERNS). An eng-day is an attention-day at the agent-orchestrated pace, measured from branch to merge.

**Scope covered.** The estimate covers v1.0 plus the team-lead's own fold-ins (C-1 to C-14). These v1.1 and v1.2 additions aren't priced yet:
- the whole-report assembly (FR-K5.1), beyond the bounded Section 5;
- D-3's failure behavior on three paths (FR-E.6), and one batch planner shared by three layers, with plan IDs (FR-E.3);
- the small-run oracle (NFR-1), and the two v4.48.4 baseline runs (D-7, SC-8);
- the smaller checks: FR-N4.6's dispositions, FR-K5.5, FR-K5.7, FR-E.7, FR-E.10, and a defined place for parse errors;
- NFR-10's wider scope, the legacy-format baseline (R-26), the architecture-path carrier (D-5) and the runbook re-validation (R-27);
- the conditional fold-ins under R-14 and R-15, and FR-N4.3's brief script;
- from v1.2:
  - the renderer's asset-modifier step and its tagged fixture cases (R-25);
  - R-31's mechanics;
  - the per-batch tree manifests and their merge (D-3, FR-K5.6);
  - the persisted Phase 1 inventory and dispatch table, and the fixed dispatch prompt with its SC-3 comparison (FR-N4.3);
  - FR-E.11's upload snippets, and FR-E.2's cross-file assertion;
  - the larger precomputed scorer input that D-7's twice-the-cap rule implies (roughly 325 findings);
- from the PM's v1.2 rulings: R-27's wider smoke run, R-30's resolved marker and its split parity check, and R-31's override marker.

R-17 removes the full adapter port, which offsets part of this. A team-lead addendum to `feasibility-check.md` prices the delta before `/aod.plan`, and this section adopts it. TW-0 re-tests the projection at `/aod.tasks` either way, and the optional fold-ins count against TW-0 and drop first.

| Band | Eng-days | Conditions |
|---|---|---|
| Floor | 5.5 | SV-1, SV-2b and SV-3 fire at `/aod.tasks`. The adapter port is out, and chain formation stays spec-only with SC-2 reworded. Every wave goes green on its first CI cycle, and every live run passes first time |
| **Planning (central)** | **8.0** | Full scope, with chain formation in a script, `threats.sarif` from a shipped generator, and bounded `threats.md` emission. One CI fix-forward. Seven fixture live runs, one small smoke run and one retry. N3 lands before W2 |
| Ceiling | 13.0 | Everything grows. Renderer contract gaps; `threats.md` tables rendered by code; the 5 Whys points at context pressure but the bundle stays together; three CI fix-forwards; two stages need a second attempt; long fixture runs that hit usage limits; a fourth build session |

**Confidence: LOW–MEDIUM.** It is medium for the renderer track and low for the orchestrator track. Bottom-up effort is 17.9 eng-days (11.3 to 29.7), about 2.1× F-373 and 2.3× F-391: the largest bundle tachi has attempted. With TW-0 enforced, the projection stays at 9.0 days or less by carving scope.

| Milestone | Gate | Central | Floor | Ceiling |
|---|---|---|---|---|
| M1: Plan complete | spec, plan, ADR-050 and tasks with triple sign-off; TW-0, TW-ADR, TW-R and TW-N3 evaluated | T0 + 0.6 | T0 + 0.4 | T0 + 1.0 |
| M2: Cut line green (end of W1) | the cut-line set committed; both CI legs green | T0 + 2.0 | T0 + 1.5 | T0 + 3.0 |
| M3: End of build session 1 (W2) | architect P0 checkpoint; TW-ESC evaluated; NEXT-SESSION handoff | T0 + 4.0 | T0 + 2.9 | T0 + 6.25 |
| M4: Implementation complete (W3, W4) | offline end-to-end run on the fixture green; architect P1 checkpoint; code and security reviews | T0 + 6.25 | T0 + 4.3 | T0 + 9.75 |
| M5: Live verification recorded (W5) | the live matrix in the PR; TW-L1 to TW-L3 recorded | T0 + 7.5 | T0 + 5.1 | T0 + 12.25 |
| **M6: Deliver** | `fix(374)` squash-merged; patch-release PR verified | **T0 + 8.0** | **T0 + 5.5** | **T0 + 13.0** |
| SC-9: Live confirmation | the next large real-world run | lagging; tracked outside this feature | | |

T0 is the day the plan stage starts. If T0 is 2026-11-23 and sessions run on consecutive working days, M6 lands around 2026-12-02 at the central estimate (floor 2026-11-30, ceiling 2026-12-09). Gaps between sessions push the dates out without adding effort. *ICE note:* the issue's Effort 4 predates the fold-in from #397, and an 8-day central suggests 3, giving an ICE of 17.

---

## 12. Dependencies

- **#373 (delivered, v4.48.1).** Its K9 and K13 parsers must read K8's corrected format, and its manifest completeness check requires every new script and its helpers in `INSTALL_MANIFEST.md`.
- **#364.** It blocks the next minor release, so this bundle ships as `fix:`. This bundle lands first, and #364 regenerates the examples through the renderer (NG5).
- **#365.** Test runs re-render tracked example PNGs. Don't commit them, and don't regenerate the PDF baselines.
- **#396 (F-391 Part B) and #400.** About nine code and contract paths overlap. This bundle lands first, #396 rebases, and the plan files the expected conflicts on #400. This bundle leaves `/tachi.threat-model`'s Step 2.5 and Step 3 anchors in place, and keeps the Step 2.6 slot free (FR-K4.1).
- **The N3 hardening track (#360/#391).** It edits some of the same agent specs. It merges first as its own `fix:` if it is ready first, and the plan orders the two (TW-N3).
- **#399.** The dispatch records and briefs give #399's manifest something to record. Its planned `tachi_agents_not_dispatched` check is the transcript-level complement to FR-N4.5.
- **#356 (R-13), #357** (closed if subsumed), **#408 (R-14), #409 (R-15) and #412 (R-16).**
- **CI gates.** `tachi-install-fidelity.yml`, `tachi-pytest.yml` and `tachi-permissions-verify.yml` (FR-E.5).
- **Delivered foundations:**
  - ADR-046 (the tier boundary; D5's structural ideal);
  - ADR-047;
  - ADR-049 (D4, D5, D7, D8);
  - ADR-024 (scoring);
  - KB Entries 22, 24, 25 and 26.

---

## 13. Risks, Open Questions and ADR-050

### Risks

- **RK-1: scope.** The largest bundle yet. *Mitigation:* the cut line, the PM priority, SV-1 to SV-4, TW-0 and TW-ESC (§10).
- **RK-2: live-run cost.** *Mitigation:* decoupled stages, a baseline-aware threat-model run, offline evidence first, the effort matrix (R-18), two attempts at most, TW-L1 to TW-L3, and usage recorded (NFR-4).
- **RK-3: the authoring-tier change breaks consumers.** *Mitigation:* ADR-050; additive schemas; renderer goldens; the round-trip test; the small-run oracle; #373's tolerant parsers.
- **RK-4: orchestrator context** *(corrected in v1.1)*. Run B's orchestrator peaked near 700k tokens without compaction. Persisting dispatch records **adds** orchestrator output; it doesn't remove context. Relief comes only from moving computation and emission out of the orchestrator: the chain script, the `threats.sarif` generator and bounded emission. *Mitigation:* the 5 Whys first; SV-1; TW-CTX records peak context on every fixture run. Dispatching Phase 2 from the command layer is the architectural escalation, and it is a follow-up, not this bundle.
- **RK-5: the effort confound.** *Mitigation:* the effort matrix (R-18).
- **RK-6: merge conflicts** with #396 and the N3 track. *Mitigation:* the merge order in §12.
- **RK-7: the renderer is more work than "no production caller" suggests.** *Mitigation:* contract tests against the agents' current SARIF contract; ADR-050 scopes the gaps; TW-R.
- **RK-8: the alert-identity migration.** *Mitigation:* D-5's principle 1, under which ADR-050 shows no compatible option exists; the binding release notes (§8).
- **RK-9: a new trust boundary.** Part files are written by agents that read third-party text. *Mitigation:* NFR-10, and the Step 7 security review.
- **RK-10: rounding noise.** *Mitigation:* the pinned arithmetic (NFR-2) and ruling R-11.

### Open questions for the spec

- **OQ-5:** the batching thresholds.
- **OQ-6:** the cross-prefix total order, and the redundancy and surfacing rules (FR-K4.2).
- **OQ-7:** the fixture generator's exact shape (D-7), and its Run-B-scale variant.

OQ-1 to OQ-4 from v1.0 are now rulings (§4) or ADR-050 items.

### ADR-050 must decide

The Architect's list, plus TW-ADR. Each item must be ruled before the build wave that depends on it.

1. **Which surfaces leave the model tier**, and how ADR-046 (D1, D4), ADR-047 and ADR-049 (D7, with D5 and D8 applied) change. The candidates:
   - `risk-scores.{md,sarif}` and `compensating-controls.{md,sarif}`;
   - `threats.sarif`, and the `threats.md` tables;
   - the report's assembly;
   - Phase 3.5's computation.
2. **The judgment/computation line**, field by field (D-2's table).
3. **The part-file contract:** schema and version (the encoding is JSON, fixed by NFR-10), batch granularity, `.tachi-build/` location, prose fragments, plan and batch IDs, retention and stale parts, validation, and who names the paths.
4. **Where each script runs and in what order:** Phase 5 sequencing, exit codes, behavior on failure, and the provenance stamp.
5. **The scoring constants and arithmetic:** the embedded constants and their drift test (R-32), one band helper, `Decimal` half-up rounding, and the date as an input.
6. **Batching and overflow:** thresholds; the planner and slicing (the planner runs only where Bash runs); the error schema; resume from disk; ownership per agent, including which layer dispatches the tree batches; and the retry cap.
7. **SARIF identity:** GitHub's key; the hash recipe and its stable per-finding key; the repo-relative URI and its carrier; a tool name and category per file (R-33); the `:339` / `:612` contradiction; and the migration.
8. **SARIF membership:** one result per finding or stable primaries (with the asymmetry and SV-3 in view), the peer marker, how correlation is expressed, RESOLVED excluded, the reference finding set, and the `threats.sarif` fallback input.
9. **Score-inheritance mechanics:** how recomputed values, flags, "unverifiable" and "unchecked" appear in the `.md` and the SARIF; the tolerant parser for legacy baselines (R-26); the resolved marker (R-30); and the derivation of the original scoring date, its fallback, the override rule and the override marker (R-31).
10. **The exception rules:** a category for every prefix, and the vector check separated from the bound check.
11. **The dispatch records:** attribution envelope or `schemas/finding.yaml` bump, the ID map, whether code or the model compiles Phase 3, and the coupling to FR-O.1 and SV-2b.
12. **The provenance check:** its classes, and what it proves and doesn't.
13. **Phase 3.5:** code or model for the computational steps; the outcome record's format and writer; the mechanism that keeps an inconsistent record's chains from reading as complete (R-24); the order across prefixes; redundancy and surfacing; and whether the transitive-closure link test stays.
14. **Report assembly:** part granularity, who runs the step, tree batching, and carry-forward by copy.
15. **Schema versions:** `threats.md` (with #396's 1.5), `risk-scores.md` and `compensating-controls.md`, and the part and record schemas.
16. **Test and CI placement:** the workflow per suite, S-13's list and allowance, the write-confinement extension, the lock-step anchors, and the offline identity test.

---

## 14. References

- Lead issue: [#374](https://github.com/davidmatousek/tachi/issues/374), with the #397 evidence comment of 2026-11-21.
- Defect tracker: [#397](https://github.com/davidmatousek/tachi/issues/397): N4, N12, N14, N15 and N16, and "Evidence for existing issues".
- Companion bundle: [PRD-373](373-adopter-install-output-fidelity-2026-09-27.md).
- Feasibility: [`specs/374-large-architecture-pipeline-resilience/feasibility-check.md`](../../../specs/374-large-architecture-pipeline-resilience/feasibility-check.md).
- ADRs:
  - [ADR-046](../../architecture/02_ADRs/ADR-046-asset-tag-output-wiring.md);
  - [ADR-047](../../architecture/02_ADRs/ADR-047-maestro-coverage-state-authority.md);
  - [ADR-049](../../architecture/02_ADRs/ADR-049-privilege-contract-and-write-confinement.md);
  - [ADR-024](../../architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md).
- Institutional knowledge: [KB Entries 22, 24, 25 and 26](../../INSTITUTIONAL_KNOWLEDGE.md).
- GitHub Docs, "SARIF support for code scanning" (alert matching on `ruleId`, `primaryLocationLineHash` and the file path): https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning
- Product vision: [product-vision.md](../01_Product_Vision/product-vision.md). No current-quarter OKR file exists.
- Constitution: `.aod/memory/constitution.md`.

---

## Appendix A: technical inaccuracies, corrected

**In v1.1** (the Architect's re-review found 2, within the target of fewer than 3; both trace to the v1.0 review's own wording):

| # | v1.1 claim | Correction (v1.2) |
|---|---|---|
| 1 | NG4: `TE-` findings fold into the `LLM-N` sequence | `TE-` findings fold into `AG-N`, and `OI-` and `MI-` into `LLM-N` (`orchestrator.md:373-374`; NG4) |
| 2 | D-5: a RESOLVED result keeps its alert open forever | It counts as present in the run that resolves it, so its alert closes one run late (D-5) |

**In v1.0** (the Architect's review found 6):

| # | v1.0 claim | Correction (v1.1) |
|---|---|---|
| 1 | The trace check "catches all three failure modes" | It covers modes 1 and 3, as a record the orchestrator keeps about itself. It now admits carried and pattern findings (FR-N4.5). Mode 2 has its own check (FR-K5.7), and transcript proof stays with #399 |
| 2 | The hand-off "moves finding bodies out of the orchestrator's context" | It adds orchestrator output. Relief comes only from moving computation and emission to code (RK-4) |
| 3 | Today's shared `primaryLocationLineHash` is the identity problem | True for `threats.sarif` only. The scorer and controls SARIF carry no hash on the canonical path, and they point at a per-run path, so their alerts churn on every run (§1, root problem 5; D-5) |
| 4 | Guard C7 fails on any undeclared write path | C7 cross-checks the declarations; review and `test_write_confinement.py` enforce declaration (NFR-3) |
| 5 | Stdlib-only imports are enforced by `test_pyyaml_deferred_import.py` | That module isn't gated. S-13 in `test_install_manifest_completeness.py`, run in `tachi-install-fidelity.yml`, is the gate (D-2, NFR-2) |
| 6 | The CI gates are `tachi-pytest.yml` and `tachi-permissions-verify.yml` | `tachi-install-fidelity.yml` is a third gate, and the default for renderer, checker and parser suites (FR-E.5) |

## Appendix B: disposition of HIGH findings

| Review | Finding | Resolved in |
|---|---|---|
| PM 1, TL C-1, Arch 3 | `threats.sarif` identity, and GitHub's matching key | D-5, R-2, FR-O.1 (SV-2a), FR-E.1, FR-E.2, SC-6 |
| PM 2 | Completeness of the threat-model stage | FR-N4.6, R-13 |
| PM 3, Arch 5 | Bounding the whole report; the tree agent; a tree-count check | FR-K5.1, FR-K5.5, FR-K5.6 |
| PM 4 | Ranking D-6(b) | D-6(b), R-4 |
| PM 5 | Release-note content | §8, SC-7, R-1 |
| PM 6 | §12's publication of the N3 track's reach | §12, NG1, NFR-6 (generalized) |
| Arch 1 | The trace check's premise | FR-N4.5, FR-K5.7, Appendix A item 1 |
| Arch 2 | The hand-off adds output; per-dispatch granularity | FR-N4.2, R-8, RK-4 |
| Arch 4 | The renderer owns whole files and sub-score arithmetic | D-2 (table), FR-K6.3, FR-K8.1 |
| Arch 6, TL C-11 | SV-2 versus SC-1, and fixture sizing | §10 (SV-2a/b), D-7 |
| Arch 7, TL C-2 | Chain formation without a mechanism | D-4, R-19, FR-K4.1b, SC-2 |
| Arch 8 | Undecidable exceptions | D-4, R-10, SC-4 |
| Arch 9 | Batching for agents a command doesn't dispatch | D-3, FR-N4.7, FR-K5.6, FR-E.3 |
| TL C-3 | The live matrix | D-7, R-18, §10 trip-wires |
| PM r2 28 | The carve order against R-12 | §10, R-23 |
| PM r2 29 | TW-N3's lane letters disclosed the N3 fix's reach | `feasibility-check.md` TW-N3 (generalized); NFR-6 |

---

## Approval & Sign-Off

| Role | Agent | Status | Date | Notes |
|------|-------|--------|------|-------|
| Product Manager | product-manager | 🟡 Approved with Concerns (v1.2 delta re-review) | 2026-11-21 | 16 of 16 v1.1 re-review findings resolved; R-25 to R-31 ruled (2 accepted, 5 amended, folded verbatim in v1.3); 5 LOW |
| Architect | architect | 🟡 Approved with Concerns (v1.1 re-review) | 2026-11-21 | 2 inaccuracies corrected in v1.2 (Appendix A); 22 new findings folded |
| Team-Lead | team-lead | 🟡 Approved with Concerns | 2026-11-21 | 8.0 / 5.5 / 13.0 eng-days; 14 concerns folded |

Legend: ✅ Approved | 🟡 Approved with Concerns | 🔄 Changes Requested | ⛔ Blocked | 📋 Pending

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-21 | product-manager (via /aod.define) | Initial PRD from lead issue #374 with the #397 fold-ins (N4, N14, N15, N16) and the N12 identity decision |
| 1.1 | 2026-11-21 | /aod.define orchestrator (PM rulings adopted; PM re-review validates) | Folds in the Triad review of v1.0 (PM 27 findings, Architect 28 plus 6 inaccuracies, Team-Lead 14 concerns and the estimate). `threats.sarif` and GitHub's matching key are in scope (D-5); the renderer owns whole files and the controls arithmetic (D-2); the dispatching layer owns batching, and Phase 2 overflow is covered (D-3); provenance and completeness checks replace the v1.0 trace check (FR-N4.5, FR-N4.6); the whole report is bounded (Group B); D-6 is ranked; 22 rulings; §10–§11 are sized from the feasibility check; §12 is generalized for public hygiene. Written in the define session from the three reviews, adopting the PM review's rulings, rather than by a separate product-manager agent; the PM re-review validated it and accepted the deviation, on conditions |
| 1.2 | 2026-11-21 | /aod.define orchestrator (PM rulings adopted; PM re-review validates) | Folds in the v1.1 re-reviews (PM CHANGES_REQUESTED: 2 HIGH, 5 MEDIUM, 9 LOW; Architect APPROVED_WITH_CONCERNS: 2 inaccuracies, 11 MEDIUM, 11 LOW). Budget carves follow R-12, and SV-3 fires only on its technical trigger (R-23); TW-N3 is generalized in the feasibility check; a bad Phase 3.5 record never ends the run (R-24); band-moving rounding is flagged (R-11); the regroup case is tested (US-5, SC-4); tree batching moves to a layer with Bash, and stale parts are rejected (D-3); per-file tool names and the architecture-path carrier (D-5); NFR-10's scope is widened; legacy baselines (R-26); the release notes are extended; §11 lists the unpriced delta. R-25 to R-31 are proposed for the PM's ruling. Risks are renumbered RK-1 to RK-10 |
