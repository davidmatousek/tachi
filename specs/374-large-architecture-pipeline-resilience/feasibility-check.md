---
artifact: feasibility-check
feature_id: 374
owner: team-lead
date: 2026-11-21
prd_number: 374
status: draft
estimate:
  planning_days: 8.0
  floor_days: 5.5
  ceiling_days: 13.0
---

# Team-Lead Feasibility Check: Feature 374, Large-Architecture Pipeline Resilience

**STATUS: APPROVED_WITH_CONCERNS**

- **Verdict:** FEASIBLE WITH MODIFICATIONS (§1).
- **Estimate:** planning **8.0** · floor **5.5** · ceiling **13.0** eng-days, branch to merge. Bottom-up effort 17.9 / 11.3 / 29.7 eng-days. Confidence **LOW–MEDIUM**: medium for the renderer track, low for the orchestrator track.
- **Scope reviewed:** PRD-374 v1.0, which covers K4–K8, N4, N14, N15, N16 and the N12 decision (D-1 to D-7, FR Groups A to E). Pointers come from `.aod/results/pointer-refresh-374.md` (60 checked at `b040fa1`: 47 hold, 9 moved, 4 changed, 0 gone), plus the re-reads cited below.
- **Lenses:** Constraint Analysis (§2.3 and §12) and Systems Thinking (the file-ownership map, §3.1).
- **Vetoes:** neither is exercised. PRD §11 has no timeline to veto yet, and no lane is planned above 80% of its wave.
- **Concerns:** 14 (3 HIGH, 8 MEDIUM, 3 LOW). Each resolves as a PRD fold-in or a plan-stage ruling. None blocks Define exit.

---

## 1. Verdict

**The scope can be built as one bundle:**
- Every item has a known root cause except K4. K4's fix, the outcome record, doesn't depend on that cause.
- The central mechanism is computed values in shipped code, run from the main session. It has a production precedent in `scripts/populate-affected-assets.py` (ADR-046), and a test-only CVSS calculator exists to promote (`tests/scripts/test_cvss_category_defaults.py:66-89`).
- No agent gains a tool (NG8). The privilege-guard work is declarations, not new tiers.

**It is the largest bundle tachi has attempted.**
- Its effort is about 2.1× F-373's and 2.3× F-391's.
- It carries the most new production code since F-302: a renderer, a chain-formation script, a trace check and a tree-assembly step.
- It has the heaviest live verification so far. F-391's live validation took about 4 hours of wall clock; this bundle needs 7–9 runs, most of them hours long.

**The critical path is the renderer, not the orchestrator.** The path runs from the renderer core (W1) to the risk-scores renderer (W2), then the controls renderer and the `threats.sarif` generator (W3), then the live wave. The orchestrator lane carries the variance: K4's unknown cause, context pressure, and how Phase 2 behaves once Run B's improvised caps are gone.

**"With modifications"** means seven fold-ins before `/aod.tasks`, each detailed under its concern:
1. C-1: `threats.sarif` identity is in scope, because that is where N12 was observed and what the docs tell adopters to upload.
2. C-2: chain formation moves into shipped code, or SC-2's repeat-run clause is reworded.
3. C-3: the D-7 live matrix is restructured and given a budget gate.
4. C-4 and C-5: merge order with #396 and with the N3 track.
5. C-6: three overflow surfaces that no FR covers.
6. C-9 and C-10: the renderer's input validation and arithmetic semantics are pinned before any code is written.
7. C-11: the fixture design (OQ-7).

**Split now? No** (§8). The renderer is the critical path in both shapes. A split at Define ships the first PR about one day sooner and costs two to three days in total. The split is pre-armed instead, through TW-0 and TW-ESC.

---

## 2. Estimate

**Unit.** An eng-day is an attention-day at the AOD agent-orchestrated pace, measured from branch to merge. It is the unit used by the F-373, F-391, F-362 and F-295 checks and their delivery records.

### 2.1 Bands

| Band | Days | Conditions |
|---|---|---|
| **floor** | **5.5** | At `/aod.tasks`, SV-1, SV-2b and SV-3 fire (§8), FR-C.1 becomes a superseded-by note, and chain formation stays spec-only with SC-2 reworded. Every wave goes green on its first CI cycle, and every live run passes on its first attempt. What ships: the shared contracts; the renderer for risk scores and controls (N/N, totals, recompute-and-flag); the scorer and controls contracts with command-layer batching; K8; typed dispatch, the hand-off and the trace check; the K4.1 outcome record; a bounded Section 5; `threats.sarif` from a shipped generator; bounded `threats.md` emission. |
| **planning (central)** | **8.0** | Full scope plus the C-2 and C-6 additions. Assumes ADR-050 rules every open question in one plan pass. Chain formation moves to a script. `threats.sarif` comes from a shipped generator that shares the renderer's D-5 emitter. `threats.md` uses bounded emission, not table rendering. One CI fix-forward. 7 fixture live runs, 1 small smoke run and 1 retry. N3 lands before W2. Five concurrent lanes hold up in W2. |
| **ceiling** | **13.0** | Full scope, and everything grows. Contract gaps in the renderer (R-7) add a day. The `threats.md` tables are rendered by code. The 5 Whys points at context pressure, but the bundle stays together. Three CI fix-forwards. Two stages need a fix and a second live attempt. Fixture threat-model runs take 5 hours each and hit usage limits. Rebases across N3 and `main`. A fourth build session. |

`floor ≤ planning ≤ ceiling` holds (5.5 ≤ 8.0 ≤ 13.0).

With the trip-wires enforced, the practical worst case is lower:
- TW-0 keeps the projection at 9.0 days or less by carving scope.
- If TW-ESC fires, Track R merges at about T0 + 7 days and Track O at about T0 + 10–11 days.

### 2.2 Bottom-up effort (eng-days)

Track: **R** is the renderer track (scorer and controls), **O** is the orchestrator track (threat model and report), and **S** is shared work.

| # | Work package | Items | Track | Central | Floor | Ceiling | Main driver |
|---|---|---|---|---|---|---|---|
| 1 | Plan stage: spec, plan, ADR-050, tasks, triple sign-off | all | S | 0.60 | 0.40 | 1.00 | ADR-050, OQ-1 to OQ-7, and the C-1, C-2, C-4, C-8 and C-10 rulings |
| 2 | Pre-state, in a scratch clone | NFR-7 | S | 0.10 | 0.10 | 0.15 | gated set, install fidelity and the guard; #365's 6 reds; the out-of-gate census |
| 3 | Synthetic large fixture and its generator | FR-E.4, D-7 | S | 0.80 | 0.60 | 1.30 | architecture, synthetic baseline run directory, seeded variant, regrouping pair, stub codebase (C-11) |
| 4 | Shared contracts | FR-E.1, FR-E.3, OQ-3, OQ-5, roster, brief template | S | 0.50 | 0.35 | 0.80 | one N/N text that replaces three SARIF contract copies (C-1) |
| 5 | Renderer core | D-2 | R | 0.80 | 0.60 | 1.20 | part-file validation (C-9); CVSS calculator promoted to shipped code; SARIF base; `sarif_common.py` installed, with bytecode suppressed |
| 6 | Renderer: risk scores | FR-N14.2, FR-K6.1–6.2, FR-N16.1, D-6 (b)(c) | R | 1.60 | 1.10 | 2.60 | parity with the agent's §10 SARIF contract (R-7); governance carry-forward; arithmetic pins (C-10) |
| 7 | Renderer: controls | FR-K7.1–7.3, K8 tables | R | 1.00 | 0.70 | 1.60 | residuals, and totals as sums of rows; Sections 2, 4 and 5; each peer counted once |
| 8 | Identity mechanism and the two-run test | D-5, FR-E.2 | R | 0.40 | 0.00 | 0.80 | the floor is 0 because SV-3 fires |
| 9 | Orchestrator outputs at scale | FR-O.1 | O | 1.20 | 0.80 | 2.20 | `threats.sarif` from a shipped generator (0.8, kept per C-1) plus bounded `threats.md` emission (0.4); at the ceiling, code renders the tables |
| 10 | Scorer contract and command | FR-K6.3, FR-N14.1, FR-N15.1, D-6 (a) | R | 0.80 | 0.60 | 1.20 | rewrite of the 550-line spec; batch-and-resume loop in `/tachi.risk-score` |
| 11 | Adapter copy | FR-C.1 | R | 0.40 | 0.10 | 0.70 | a 1,419-line hand-maintained copy (C-12) |
| 12 | Controls contract, command and template | FR-K7.4, FR-K8.1–8.2 | R | 0.70 | 0.50 | 1.00 | input contract (paths); `CF`; Section 4; the command starts instructing Bash |
| 13 | Parsers read both controls formats | FR-K8.2 | R | 0.30 | 0.20 | 0.60 | `tachi_parsers.py` and `extract-report-data.py`; data-layer oracle |
| 14 | 5 Whys on Run A's skip | FR-K4.3 | O | 0.25 | 0.15 | 0.40 | time-boxed; evidence retention (C-13) |
| 15 | Phase 3.5 outcome record | FR-K4.1 | O | 0.50 | 0.35 | 0.80 | template, output-schemas, orchestrator, and the report and PDF readers |
| 16 | One chain algorithm and a chain-formation script | FR-K4.2, FR-K4.4 | O | 1.40 | 0.30 | 2.20 | floor: spec text only, with SC-2 reworded; central: script (C-2) |
| 17 | Typed dispatch, hand-off, briefs, no ad-hoc scripts | FR-N4.1–N4.4 | O | 1.15 | 0.80 | 1.80 | Phase 3 compiled from the records; origin back-references (C-8) |
| 18 | Trace check | FR-N4.5 | O | 0.50 | 0.35 | 0.80 | shipped script, command step and tests |
| 19 | Phase 2 batching by component on overflow | C-6 (b) | O | 0.30 | 0.15 | 0.60 | FR-N4.3 removes the improvised per-pair caps |
| 20 | Bounded Section 5, its checks and typed helpers | FR-K5.1–K5.4 | O | 1.10 | 0.75 | 1.75 | shipped assembly step; carried-forward trees copied by code (C-6 (c)) |
| 21 | Privilege matrix and CI/manifest wiring | NFR-3, FR-E.5 | S | 0.55 | 0.40 | 0.95 | rows in §8.3–8.5 and runbook §5 (guard C7); lock-step `paths:` and invocation |
| 22 | Offline end-to-end run on the fixture | SC-2, SC-4, SC-5, SC-6 | S | 0.30 | 0.20 | 0.50 | deterministic evidence with no model in the loop |
| 23 | Live verification | D-7, SC-1, SC-3 | S | 1.20 | 0.80 | 2.20 | §5 |
| 24 | CI cycles and session handoffs | NFR-7 | S | 0.40 | 0.25 | 0.80 | §6 |
| 25 | Architect checkpoints, code review, security review | — | S | 0.50 | 0.35 | 0.80 | the renderer is a new trust boundary (C-9) |
| 26 | Deliver | SC-7 | S | 0.30 | 0.25 | 0.40 | release notes state the identity change (R-8); CHANGELOG; release check |
| 27 | Rebase and coordination | N3, `main` | S | 0.20 | 0.10 | 0.50 | §7 |
| | **Effort total** | | | **17.85** | **11.25** | **29.65** | |
| | **Duration, branch to merge** | | | **8.0** | **5.5** | **13.0** | |

Central effort by track: Track R 6.0, Track O 6.4, shared 5.45.

### 2.3 Effort vs duration

- **Wave model.** Each wave's window is its pacing lane × 1.25, the F-362 and F-373 model:
  - central: plan 0.6 + W0 0.35 + W1 1.0 + W2 2.0 + W3 1.5 + W4 0.65 + W5 1.25 + W6 0.5 + coordination 0.2 = **8.05**;
  - floor: 0.4 + 0.3 + 0.8 + 1.4 + 0.9 + 0.5 + 0.8 + 0.35 + 0.05 = **5.5**;
  - ceiling: 1.0 + 0.5 + 1.5 + 3.25 + 2.5 + 1.0 + 2.5 + 0.5 + 0.25 = **13.0**.
- **The pacing lane is the renderer** in W1 to W3: 0.8, then 1.6, then 1.2 days of lane time.
- **About 2.3 days of the central are serial and attention-bound:** plan rulings, checkpoints and reviews, attention on the live runs, and the deliver step.
- **Duration is about 0.45 of effort.** The precedents' actual ratios were 0.48 for F-373 (4 active days on 8.31 effort) and 0.65 for F-391 (5 days on 7.7). At F-391's ratio, this bundle would take about 11.6 days. That spread is why confidence is LOW–MEDIUM and why TW-0 sits at 9.0 days.

### 2.4 Assumptions

- **Models.** The same setup as the recent runs: tachi agents pinned to `sonnet`, an Opus main session, Claude Code 2.1.330 or later.
- **ADR-050 is accepted at the plan stage**, before any build wave starts (TW-ADR).
- **Live runs are Claude-driven tmux sessions** in scratch adopter projects, installed with `scripts/install.sh` from the branch, as in F-391's W2. That run used the AD-12 deviation, which the maintainer authorized.
- **Each lane works in its own worktree** and commits only once it finishes, because the pre-commit hook stashes unstaged files. Lanes are integrated by cherry-pick, as F-373 did with its 18 lane branches.
- **No pytest, extractor or renderer runs in the main working tree** (#365). Every gated run uses a scratch clone of the committed HEAD.
- **#364 doesn't gate the merge.** `fix(374)` is a patch release.
- **Sessions run back to back.** Calendar gaps add days without adding effort: F-373's 4 active days took 13 calendar days.

---

## 3. Lanes and the cut line

### 3.1 File ownership (one writer per file per wave)

| Lane | Owner | Files it owns | Items |
|---|---|---|---|
| **S**: shared contracts | `senior-backend-engineer`; `architect` reviews | new shared references for N/N and identity, the overflow error, the hand-off record and brief template, and the scored-part schema; `.claude/skills/tachi-orchestration/references/sarif-specification.md`; the roster lines in `coverage-requirements.md` and `finding-format-shared.md`; `schemas/finding.yaml` if OQ-3 adds a field | FR-E.1, FR-E.3, the FR-N4.1 roster, OQ-3, OQ-5 |
| **R**: renderer code | `senior-backend-engineer` (one instance per wave: R0, R1, R2, R3), with `tester` | the new renderer modules; the promoted CVSS module; `scripts/sarif_common.py`; `scripts/generate-threats-sarif.py` and `scripts/generate-risk-scores-sarif.py` (subsumed or replaced, #357); their tests and goldens | D-2, FR-N14.2, FR-K6.1–6.2, FR-K7.1–7.3, FR-N16.1, D-5, D-6 (b)(c), FR-E.2, the `threats.sarif` half of FR-O.1 |
| **C**: scorer contracts | `senior-backend-engineer` | `.claude/agents/tachi/risk-scorer.md`; `.claude/commands/tachi.risk-score.md`; `.claude/skills/tachi-risk-scoring/references/*`; `templates/tachi/output-schemas/risk-scores.md`; `adapters/claude-code/agents/risk-scorer.md` | FR-K6.3, FR-N14.1, FR-N15.1, FR-C.1 |
| **D**: controls contracts | `senior-backend-engineer` | `.claude/agents/tachi/control-analyzer.md`; `.claude/commands/tachi.compensating-controls.md`; `templates/tachi/output-schemas/compensating-controls.md`; `.claude/skills/tachi-control-analysis/references/*`; `adapters/claude-code/agents/references/sarif-generation.md` | FR-K7.4, FR-K8.1 |
| **O**: orchestrator contracts | `senior-backend-engineer`; `architect` for the chain algorithm | `.claude/agents/tachi/orchestrator.md`; `output-schemas.md`, `dispatch-rules.md` and `baseline-correlation.md`; `.claude/skills/tachi-shared/references/attack-chain-patterns-shared.md`; `templates/tachi/output-schemas/threats.md`; `.claude/commands/tachi.threat-model.md` (`schemas/output.yaml` stays untouched, C-4) | the text of FR-K4.1–4.2 and FR-O.1; FR-N4.1–4.4; Phase 2 batching; the wiring steps handed over by lanes T and OC |
| **OC**: orchestrator-side code | `senior-backend-engineer` | new scripts for chain formation, the trace check and the `threats.md` part joiner, with their tests | FR-K4.2 (script), FR-N4.5, the `threats.md` half of FR-O.1 |
| **T**: report | `senior-backend-engineer` | `.claude/agents/tachi/threat-report.md`; `.claude/agents/tachi/attack-tree-delta.md`; `.claude/skills/tachi-threat-reporting/references/*`; `templates/tachi/output-schemas/threat-report.md`; the new Section 5 assembly script and its checks | FR-K5.1–K5.4 |
| **P**: parsers | `senior-backend-engineer` | `scripts/tachi_parsers.py`, `scripts/extract-report-data.py` | FR-K8.2 (both formats); FR-K4.1 (the PDF reads the outcome record) |
| **F**: fixture | `tester` | the fixture tree under `tests/scripts/fixtures/` and its generator | FR-E.4, D-7 |
| **X**: wiring | `devops` | `INSTALL_MANIFEST.md`; `docs/standards/CLAUDE_PERMISSIONS.md` §8.3–8.5; `docs/guides/ISOLATED_OPERATION_TACHI.md` §5; `.github/workflows/tachi-pytest.yml` and `tachi-install-fidelity.yml` | FR-E.5, NFR-3 |
| **L**: live | `tester` drives the sessions; `devops` prepares the scratch adopters | the `test-results/live-*.md` records in this feature's directory | D-7, SC-1, SC-3 |

**Rules.**
- **Each hot file has exactly one lane.** About ten item edits land in `orchestrator.md`, about eight in `risk-scorer.md` and about six in `control-analyzer.md`. They belong to lanes O, C and D, which commit to those files in sequence. Three commands are touched, not two: `/tachi.threat-model` gains the trace-check step, the assembly step and the rendering step (lane O).
- **Code lanes are separate from contract-text lanes.** R and OC write scripts. C, D, O and T write agent and command text. When a command or agent has to invoke a script, the lane that owns that command or agent file does the wiring.
- **Lane X applies the cross-cutting rows once per wave.** The other lanes list their manifest, matrix, runbook and CI entries in their tasks, and never edit those files themselves.
- **Lane P runs an oracle.** It snapshots the data layer at a pinned SHA and attributes every diff after its change, using the F-373 C-4 method. It regenerates no PDF baseline (#365).
- **The `tachi-*` agents are the subjects under test**, never assignees. `orchestrator` coordinates the waves.

### 3.2 Waves and agent assignments

**Sessions:**
- P: the plan stage.
- S1: W0 to W2.
- S2: W3 and W4.
- L: W5, the live runs.
- S3: W6 and the deliver step.

Each session runs at most three waves and ends with a NEXT-SESSION handoff.

- **P, the plan stage (0.6 d).**
  - `product-manager`: the C-1 scope ruling, the C-3 live-matrix rulings, SC-2's wording if C-2 isn't adopted, and C-12.
  - `architect` writes ADR-050. It covers the authoring tier, including `threats.sarif`; the tier for chain formation; the D-5 mechanism and per-finding identity; D-6 (b) and (c); the hand-off layout with its back-references; the part schema; and the arithmetic semantics. The architect also rules on #396.
  - `team-lead`: TW-0, TW-ADR, TW-R and TW-N3, plus `agent-assignments.md`.
  - The draft PR opens as `fix(374): …`.
- **W0 (0.35 d).**
  - `devops`: the pre-state, in a scratch clone.
  - `debugger`: FR-K4.3's 5 Whys (TW-K4).
  - `tester`: starts the fixture generator.
- **W1, foundations (window 1.0 d).**
  - `senior-backend-engineer` ×4:
    - S, the shared references and roster (0.5);
    - R0, the renderer core (0.8);
    - O1, the typed-dispatch text, the brief template, the no-scripts rule and the K4.1 text (0.75);
    - T, the bounded Section 5 contracts, the assembly script and the typed helpers (0.8).
  - `tester`: F (0.8).
  - `devops`: the W1 wiring rows.
  - **The cut line falls at the end of W1** (§3.4).
- **W2, implementation (window 2.0 d).**
  - `senior-backend-engineer` ×5:
    - R1, the risk-scores renderer with recompute-and-flag (1.6);
    - C, the scorer contract, the command and the adapter copy (1.2);
    - O2, the hand-off, Phase 2 batching and the chain text (1.3);
    - OC, the chain-formation script (1.0);
    - P, the parsers plus T's K5.2 and K5.3 checks (0.8).
  - `tester` writes the renderer's contract and golden tests first, within R1's budget (Principle VI).
  - `architect`: the P0 checkpoint at the end of W2. Then the TW-ESC check.
- **W3, implementation and wiring (window 1.5 d).**
  - `senior-backend-engineer` ×4:
    - R2, the controls renderer (1.0);
    - R3, the identity mechanism and the `threats.sarif` generator on the shared D-5 emitter (1.2);
    - D, the controls contract and command (0.7);
    - O3, the trace check, the `threats.md` emission and the command steps (1.1).
  - `devops`: X (0.55).
  - `security-analyst`: an advisory review of part-file validation and path handling.
- **W4, integration (window 0.65 d).**
  - `tester`: the offline end-to-end run on the fixture, which is the evidence for SC-2, SC-4, SC-5 and SC-6.
  - `devops`: one push, with both CI legs green.
  - `code-reviewer`: the full diff.
  - `security-analyst`: the Step 7 scan names every new script.
  - `architect`: the P1 checkpoint.
- **W5, live runs (window 1.25 d).**
  - `tester`: drives the live matrix (§5) and the structure-only dispatch census for SC-3.
  - `devops`: prepares the scratch adopters and installs, and provides `mmdc` for the PDF run.
  - `product-manager`: rules if TW-L1 fires.
- **W6, close-out (0.5 d).**
  - `product-manager`: the release notes, which cover the identity change in generic wording (NFR-6), and the follow-ups.
  - `devops`: confirms the PR title `fix(374): …`, checks that `main` equals `origin/main` before any deliver push, and checks the release.
  - `architect`: records ADR-050's accepted-commit SHA.

### 3.3 Load check

Each lane's share of its wave window:

| Wave | Lanes |
|---|---|
| W1 | R0 80%, F 80%, T 80%, O1 75%, S 50% |
| W2 | R1 80%, O2 65%, C 60%, OC 50%, P 40% |
| W3 | R3 80%, O3 73%, R2 67%, D 47%, X 37% |

- No instance is above 80%.
- W2's five concurrent `senior-backend-engineer` lanes go beyond the precedent of four (F-391's W1). If five can't be sustained, lane P moves to W3. The window holds, because R1 paces W2.
- Expect about 44–50 tasks, scoped by work bucket rather than by file.

### 3.4 Cut line and carve order

- **The cut line is the end of W1.** By then the following are committed, with both CI legs green:
  - ADR-050, accepted at the plan stage;
  - the shared references: N/N and identity, the overflow error, the hand-off record and brief template, the scored-part schema and the roster;
  - the renderer core and its tests: the part-file loader and validation, the CVSS module and the SARIF base;
  - the fixture and its generator.
- **After the cut line the two tracks are independent**, and either can ship as its own `fix(374)` PR:
  - Track R: lanes R, C and D, plus lane P's K8 work.
  - Track O: lanes O, OC and T, lane P's K4.1 work, and the `threats.sarif` generator (R3).
- **Track R goes first.** It carries N14's code hand-back (the #360 exposure) and the observed SARIF overflow, and its live runs don't need an orchestrator run (§5).
- **Carve order** (used by TW-0 and TW-ESC):
  1. the full port of FR-C.1;
  2. SV-2b, rendering the `threats.md` tables (bounded emission stays);
  3. SV-3;
  4. SV-1;
  5. splitting Track O into PR 2.
- **Never carved:**
  - the K4.1 outcome record, which is cheap and is the observability fix;
  - FR-N14.1: no code hand-back, and the overflow contract;
  - the risk-scores renderer;
  - `threats.sarif` membership and identity. The only exception is SV-3 carving identity for all three SARIF files, in which case US-6 and SC-6 come out of the release claim (C-1).

---

## 4. Trip-wires

### At `/aod.tasks` (evaluated during the triple sign-off)

- **TW-0, aggregate.** Compute the projected duration from tasks.md: the sum of each wave's pacing-lane estimate × 1.25, plus plan and deliver.
  - If it exceeds **9.0 d** (planning + 1.0), carve in the §3.4 order until it is 9.0 or less.
  - If it still exceeds 9.0 after SV-1, split Track O into its own PR and re-baseline Track R.
- **TW-ADR, rulings present.** No build wave starts on a contract that hasn't been ruled. plan.md and ADR-050 must rule on:
  - the D-5 mechanism and per-finding identity, including `threats.sarif` (C-1);
  - D-6 (b) and (c);
  - FR-O.1's tier, and the tier for chain formation (C-2);
  - the hand-off layout with origin back-references (OQ-3, C-8);
  - the batching threshold and the overflow schema (OQ-5);
  - the part-file validation rules (C-9) and the arithmetic semantics (C-10);
  - the fixture design (OQ-7, C-11);
  - the #396 rule (C-4).

  An item that isn't ruled is carved together with its dependents, or its tasks stay `[BLOCKED]`.
- **TW-R, renderer budget.** If the tasks for work packages 5–8 add up to more than **5.3 effort-days** (1.4 × the 3.8 central), carve SV-3 first. If that isn't enough, the controls renderer keeps only the totals and SARIF, and Sections 2 and 4 stay agent-authored against the single template (K8 through the template plus tolerant parsers).
- **TW-N3, ordering.** If N3's fix hasn't merged by the start of W2:
  - the lanes that own a spec the N3 fix edits leave alone the sections it edits, which the private track's notes list;
  - the task records which side rebases (C-5).
- **TW-K4, root cause (evaluated at the end of W0).** The 5 Whys is time-boxed at 0.25 d, and its outcome is decided in advance:
  - (a) the cause lies within the plan's design: proceed;
  - (b) the cause is orchestrator context pressure that neither the chain script nor the rendered outputs remove: apply SV-1, moving K4.2 and K4.4 to their own issue while K4.1 stays;
  - (c) the evidence wasn't retained: record that and proceed. The fixture threat-model runs, which now record their outcome, serve as the reproduction (C-13).

### During the build

- **TW-ESC, escape hatch (at the end of S1).** This fires if the remaining projected work exceeds **4.0 d**, or if any lane is more than **50%** over its budget. Then:
  - ship Track R as `fix(374)` PR 1 once its live runs pass;
  - continue Track O as PR 2 under the same issue;
  - base PR 2 on `main`, not on PR 1's branch, so that merging PR 1 with `--delete-branch` can't close it (KB Entry 25);
  - PR 1's release notes don't claim SC-2, SC-3 or US-4, and claim identity only for the scorer and controls SARIF.
- **TW-CI.** If the same gated failure is red on two consecutive pushes, stop fixing forward and run an RCA (`debugger`) before the next push. Never push a records-only commit on its own: each push costs one 30–35-minute run on two operating systems.
- **TW-L1, live budget (after the first fixture threat-model run).** If that run took more than **6 h** of wall clock, or used more than one plan usage window, the PM re-plans the rest of the matrix before it continues:
  - both effort levels stay for the scorer, where the effort confound was observed, and for the controls stage;
  - the threat-model and PDF runs use the adopter default only;
  - the change is recorded in the PR.
- **TW-L2, attempts.** At most **2 attempts per stage and effort level**. What happens after a failed attempt is decided in advance:
  - a defect in shipped code (the renderer, the checks, the assembly step or the chain script): fix it and re-run once, if the fix takes 0.25 d or less;
  - an agent leaving its contract (a stand-in, a hand-back or an ignored overflow contract): record it honestly, file a follow-up, and don't claim that stage's SC (KB Entry 22).
- **TW-L3, scale.** The fixture threat-model runs are baseline-aware, so the 200+ findings and 40+ Critical come from the carried baseline rather than from fresh discovery. If a run's `threats.md` still has fewer than 200 findings, adjust the fixture once and don't chase it a second time.
- **TW-CTX.** Record the orchestrator's peak context on every fixture threat-model run. If it goes above 800k tokens, or if any compaction happens during Phases 3 and 4, consider SV-1. File the architectural escalation (dispatching Phase 2 from the command layer) as a follow-up rather than adding it to this bundle (C-7).

---

## 5. Live-run cost and duration

| Run | Input | Estimated wall clock | Count (central) |
|---|---|---|---|
| `/tachi.threat-model`, baseline-aware, with Phase 5 | the fixture architecture and its synthetic baseline run directory | 2–5 h each. For scale: the W0′ spike's run on the smallest example took about 63 min, 57 of them in the orchestrator, across 1,086 assistant lines | 2 (default effort, then max) |
| `/tachi.risk-score`, in baseline mode with the seeded errors | the synthetic `threats.md` and the seeded baseline `risk-scores.md` | 0.75–1.5 h each | 2 |
| `/tachi.compensating-controls` | a `risk-scores.md` produced by the renderer, and the stub codebase | 1–2 h each | 2 |
| `/tachi.security-report` | a fixture threat-model run directory with chains (FR-K4.4) | 0.3–0.75 h | 1 |
| Small smoke run (NFR-1) | `examples/ascii-web-api/input.md`, in a scratch adopter | about 1 h | 1 |
| Retries (TW-L2) | — | 1–5 h | 1 |

- **Wall clock.** About 15 hours if the runs go one at a time. With two sessions at once it is about 8–10 hours, or roughly 1.5 working days.
- **Attention.** About 1.0 d for setup, monitoring, the shipped checks and the evidence, plus 0.2 d for the write-up. This is work package 23.
- **Tokens.** Usage hasn't been measured at this scale.
  - Each fixture threat-model run is a full large-architecture pipeline. Run B's orchestrator peaked near 700k tokens of context.
  - Expect roughly 3–6× the turns of the W0′ run, and more at `effort=max`.
  - Two concurrent threat-model runs may not fit into one usage window.
  - The first run sets the budget (TW-L1), and the PR records the usage of every run (NFR-4).
- **Cost levers built into the plan:**
  1. **Downstream stages run on precomputed synthetic inputs.** They don't wait for a threat-model run, they reproduce exactly, and they can run in parallel.
  2. **The threat-model runs are baseline-aware**, against a synthetic baseline. The baseline carries the 40+ Critical findings, which a fresh run can't guarantee: #397 N9 records that new findings rarely reach Critical. It also exercises FR-K5.3 and carry-forward at scale. Phase 2 still dispatches every agent in baseline mode, so discovery runs at full load.
  3. **Deterministic claims get offline evidence:** SC-2's repeat-run clause (if C-2 is adopted), SC-4, SC-5 and SC-6. The live runs prove only what needs a model: agents staying on contract, and complete outputs.
  4. **SC-3 is a claim about transcripts** ("0 `general-purpose` dispatches"). Its evidence is a structure-only census of each threat-model run's dispatches, using the W0′ spike's method, and kept private. It costs about 0.1 d per run, which is included above.
  5. **The PDF run needs `mmdc` and Chromium.** It therefore runs outside the macOS sandbox profile (F-391 finding F1), in a scratch adopter (#365).

---

## 6. CI-cycle constraints

- **Measured run times.**
  - `tachi pytest`: the six most recent successful runs took 28.8–33.1 min for both legs; the three before them took 20.4–23.1 min.
  - `tachi permissions-verify` and `tachi install fidelity`: under one minute each.
- **Every push re-runs the two-OS matrix.**
  - `.claude/agents/tachi/**` and `.claude/commands/tachi.*.md` have been in `&hardening_paths` since F-391 T026, and a `pull_request` path filter sees the whole PR diff.
  - So once the first agent edit lands, every push costs about 33 minutes, including records-only pushes.
  - Plan for one push per wave. That is six or seven pushes, about 3.5–4 hours of CI wall clock.
  - Budget one fix-forward at the central estimate and three at the ceiling (TW-CI).
- **Commit before running the gated set**, because it clones the committed HEAD. Run it in a scratch clone only (#365). About 19 failures outside the gate already exist; don't chase them.
- **Lock-step wiring** (FR-E.5).
  - Each new test module goes into both the `paths:` anchor and the pytest invocation, in the same commit.
  - #396 adds 112 lines to the same two lists, so whichever PR merges second resolves a textual conflict (C-4).
- **The second gate is `tachi-permissions-verify.yml`.** On every push it runs `scripts/check-agent-privileges.py --self-test`, which fails in two cases:
  - a new write path is missing from §8.3–8.5 or from the runbook's §5 table (C7);
  - a command sets `allowed-tools` (C5).
  `/tachi.compensating-controls` starts instructing Bash, so its "Bash it instructs" cell changes from "—" to `python3` (`CLAUDE_PERMISSIONS.md:379`). The guard runs in seconds and renders nothing, so lanes can check against it locally before pushing.
- **The third gate is `tachi-install-fidelity.yml`.** It runs #373's manifest-completeness check (K2). Every new script invoked by a command or by the orchestrator, and every helper such a script imports, must be listed in `INSTALL_MANIFEST.md`, or the check fails.

---

## 7. Dependencies and ordering

| Dependency | Status (2026-11-21) | Effect and ordering |
|---|---|---|
| **N3 hardening track** (#360/#391) | private; edits some of the same agent specs | Merge N3 first, as its own `fix:`. Don't hold its release for this bundle. Until it lands, the no-touch zone applies (TW-N3, C-5). |
| **#396**, F-391 Part B (schema 1.5) | draft PR, waiting on #364 | Overlaps nine code and contract paths. #374 merges first in every likely order, so #396 rebases onto it. #374 takes no schema bump and follows the step-numbering rule (C-4). The expected conflicts are filed on #400. |
| **#364** | `stage:discover` | Blocks the next minor release. `fix(374)` is a patch, so it is not a merge gate. |
| **#365** | open | Regenerate no PDF baselines. Run no test or extractor in the main tree. Stage explicit paths only. |
| **#399** | `stage:discover` | Independent. #374 documents its run-directory layout (briefs, hand-off records, part files) for #399's manifest. FR-N4.5 is the artifact-level counterpart of `tachi_agents_not_dispatched`. |
| **#356** | open | Coupled through FR-N4.2 and FR-N4.5, and through FR-O.1 if the tables are rendered (C-8). The plan rules on it. |
| **#357** | open | Subsumed if the renderer replaces `generate-risk-scores-sarif.py`. Close it at deliver. |
| **#373** | delivered (v4.48.1) | Its K9/K13 parsers must read both controls formats (lane P). Its completeness check enforces the manifest. |
| **#408, #409** | `stage:discover` | Missing from the PRD's coordinate list. #408 bounds which subagent types the orchestrator and the report agent can start. #409 guards the dispatch targets that texts name. Both complement FR-N4.1 and FR-N4.5, and neither blocks (C-14). |
| **#412** | `stage:discover` | Under the current contract, the renderer would emit the placeholder `informationUri`, unless the plan folds in #412's SARIF line (about 0.05 d) (C-14). |
| **Process hazards** | known | In an orchestrated plan, skip `create-new-feature.sh`. Export `AOD_REPO` before filing follow-ups. Check that `main` equals `origin/main` before any deliver push. Cleaning up the lane branches is permission-blocked, so hand it to the maintainer. |

---

## 8. Split decision (SV-1 to SV-3)

**Recommendation: don't split at Define. Arm the split instead.**

**Why not now:**
- **The renderer is the critical path in both shapes.**
  - Track R alone runs about 7.0 d: plan 0.6, W0 0.35, renderer waves 1.0 + 2.0 + 1.25, integration 0.6, live runs 0.75 and deliver 0.4.
  - The bundle runs 8.0 d. Splitting at Define ships the first PR only about a day sooner.
- **A split adds 2–3 d in total:** a second plan pass, a second live wave, a second review and a second deliver.
- **Track O can't be sized yet.** Its size depends on rulings ADR-050 hasn't made: FR-O.1's tier, the tier for chain formation, and the D-5 mechanism. Splitting before those rulings would size it blind.

**Per valve:**
- **SV-1 (K4): don't fire it.** K4.1 ships in every shape, and TW-K4 decides the rest at the end of W0. If C-2 is adopted, the heavy chain computation leaves the orchestrator, which makes SV-1 less likely.
- **SV-2 (FR-O.1): split it in two.**
  - **SV-2a**, `threats.sarif` membership and identity, stays. It is where N12 was observed, and it is the file adopters upload (C-1).
  - **SV-2b**, rendering the `threats.md` tables in code, may be carved at TW-0 or TW-R. Bounded emission stays either way, because at fixture scale `threats.md` sits near the output cap. The committed examples run about 250–360 tokens per finding.
- **SV-3 (implementing N12): don't fire it now.** ADR-050 rules on it. It fires only if the chosen mechanism needs cross-run state beyond the baseline that the stage already reads. If it fires, US-6 and SC-6 come out of the release claim, and the release notes say so.
- **Add SV-4 (the track split) to PRD §10.** It is pre-authorized and fires only through TW-0 or TW-ESC. Track R ships first.

---

## 9. Concerns

### C-1 (HIGH): N12 was observed in `threats.sarif`, but D-5 covers that file only conditionally.

- **`threats.sarif` is where N12's evidence comes from.**
  - Run B's risk scorer produced no outputs (N14).
  - The rules N12 cites belong to the orchestrator's SARIF specification: peers appear only in `relatedLocations`, and `absent` maps only from RESOLVED (`sarif-specification.md:197-219` and `:385-396`).
- **It is also the file the docs tell adopters to upload** to Code Scanning (`README.md:193`, `docs/guides/DEVELOPER_GUIDE_TACHI.md:1118`).
- **Identity has to be defined where findings originate.** The three SARIF files form a supersession chain: the controls SARIF preserves the upstream fingerprints (`control-analyzer.md:159`, `:384`).
- **D-5 covers `threats.sarif` only "if ADR-050 moves it".** If SV-2 fires, or if ADR-050 leaves `threats.sarif` LLM-authored, US-6 and SC-6 go unmet on the very file adopters upload.
- **Three SARIF contract copies exist today:**
  - `sarif-specification.md`;
  - §10 of `risk-scorer.md`;
  - the installed `adapters/claude-code/agents/references/sarif-generation.md`, which the control analyzer loads (`control-analyzer.md:40`).
- **Fix:**
  - Bring `threats.sarif` membership and identity into scope, however the `threats.md` tables are decided. Generate it with a shipped generator over the compiled `threats.md`, sharing the renderer's D-5 emitter (SV-2a).
  - FR-E.1's single N/N text replaces all three contract copies.
  - Otherwise, reword US-6 and SC-6 to name only `risk-scores.sarif` and `compensating-controls.sarif`, and say so in the release notes.

### C-2 (HIGH): an LLM running chain formation at fixture scale can't meet FR-K4.2's determinism or SC-2's repeat-run clause.

- **Phase 3.5 is an algorithm** (`orchestrator.md:413-460`):
  - a scan of every pair of cross-layer STRIDE findings, with a transitive closure;
  - a lookup in the transition table;
  - greedy depth-first assembly;
  - deduplication, ranking and surfacing.

  With more than 150 STRIDE findings, an LLM won't reproduce it byte for byte.
- **A live re-run can't test the repeat clause.** "The same chains on a repeat run" needs the same finding set, and a live threat-model re-run doesn't provide one, because Phase 2 regenerates the findings.
- **Fix:** ADR-050 moves Steps 1 to 4 (index, links, assembly, chain-breaking) into a shipped, stdlib-only script, which the orchestrator runs through Bash just as it runs the Phase 3.7 populator. The LLM writes narratives for the surfaced chains only.
  - SC-2's repeat-run clause becomes an offline byte-identity test on the fixture's finding set.
  - The script also bounds `attack-chains.md` (C-6 (a)) and takes load off the orchestrator (C-7).
  - **Cost:** +1.0 d, already in the central estimate. If the script isn't adopted, subtract 1.0 d and reword SC-2 to "the outcome and the counts are recorded".

### C-3 (HIGH): the D-7 live matrix is the binding constraint on the calendar, and the PRD doesn't size it.

- Four changed stages plus the PDF, each at two effort levels with up to two attempts, comes to 8–16 runs, most of them hours long.
- For scale: the threat-model run on the smallest example took about 63 min (`specs/391-isolated-auditable-operation/test-results/w0-spike.md`).
- **Fix:** fold §5 into D-7:
  - decouple the stages by giving them precomputed synthetic inputs;
  - run the threat-model stage baseline-aware;
  - give the deterministic SCs offline evidence;
  - adopt TW-L1 to TW-L3.

  The PM decides in advance which stages keep both effort levels if TW-L1 fires. The confound observed so far is the scorer's.

### C-4 (MEDIUM): #396 overlaps nine paths, and #374 will merge first.

- **The shared paths:** `tachi.threat-model.md`, `output-schemas.md`, `sarif-specification.md`, `tachi-pytest.yml`, `INSTALL_MANIFEST.md`, `CLAUDE_PERMISSIONS.md`, `schemas/output.yaml`, `generate-threats-sarif.py` and the `threats.md` template. Four docs overlap as well.
- **#396 waits on #364**, so #374 lands first in every likely order.
- **#396's new contract test pins two things:**
  - one declared set of keys across `output.yaml`, the template, `output-schemas.md` and the SARIF specification;
  - its Step 2.6 sitting between Step 2.5 and Step 3 of `/tachi.threat-model`.
- **Fix:**
  - #374 doesn't bump `schema_version` and declares no new key in `output.yaml`.
  - The Phase 3.5 outcome is recorded either in the body of `threats.md`, or as a key that #396 declares when it rebases. The plan agrees which.
  - #374's new command steps leave the Step 2.5 and Step 3 anchors in place and keep the Step 2.6 slot free.
  - The plan files the list of expected conflicts on #400.

### C-5 (MEDIUM): the N3 track edits some of the same agent specs, and a security fix shouldn't wait behind an 8-day bundle.

- **Fix:**
  - N3 merges first, as its own `fix:` with its own patch release, unless #374 is within about two days of merging.
  - #374 rebases onto it at the start of W2.
  - Until N3 lands, TW-N3's no-touch zone applies.
  - "One release train" can still mean consecutive patch releases.

### C-6 (MEDIUM): no FR covers three of the surfaces that overflow.

- **(a) `attack-chains.md` is written in a single Write.**
  - The committed examples run about 750–1,000 tokens per chain.
  - At Run B's scale of about 120 chains, that is roughly 90–120k tokens, beyond the 64k cap.
- **(b) Phase 2 threat agents overflow.**
  - They hit `max_tokens` even on the smallest example (`tachi-info-disclosure` and `tachi-denial-of-service`, in the W0′ spike).
  - FR-N4.3 removes the per-pair caps that Run B's stand-ins worked under, so at about 25 components the typed agents will overflow.
  - The orchestrator must re-dispatch the agent on a subset of the components after a structured overflow error. Target components are a scope input, so this fits FR-N4.3.
- **(c) `tachi-attack-tree-delta` writes every tree in one session**, with no cap. It hit `max_tokens` once even on the smallest example.
  - With any delta, Rule 2 regenerates every Critical and High tree.
  - Rule 1 re-emits carried-forward trees through Write (`attack-tree-delta.md:75`; Rule 2 at `:77-81`). That is how three carried-forward trees were edited in Run B.
- **Fix:**
  - For (a): C-2's script bounds the file, or a redundancy rule with a stated cap does.
  - For (b): Group A gains an FR for batching Phase 2 by component when an agent overflows.
  - For (c): FR-K5.1 bounds the delta agent's batches, and the shipped assembly step copies the carried-forward trees. FR-K5.3 then holds by construction, and its check stays as a guard.
  - About +0.6 d, already in the central estimate.

### C-7 (MEDIUM): R-4's mitigation doesn't hold under NG8.

- **Persisting the findings doesn't take them out of the orchestrator's context.**
  - The threat agents can't write, so their returns reach the orchestrator as tool results in any design.
  - FR-N4.2 then adds them a second time as Write output, about 60–80k tokens at fixture scale.
  - If Phase 3 "compiles from the persisted records" by reading them back, that adds a third copy.
- **The hand-off buys reproducibility and the trace check, not context relief.** Only moving computation and emission out of the orchestrator lightens its load: C-2's chain script, and FR-O.1's rendering.
- **Fix:**
  - Reword R-4.
  - The plan states whether Phase 3 reads the records back or compiles from the returns, with the records kept as the audit copy.
  - Adopt TW-CTX.
  - Dispatching Phase 2 from the command layer is the architectural escalation. It is a follow-up, not part of this bundle.

### C-8 (MEDIUM): the trace check needs back-references to each finding's origin, and that is the surface of #356.

- **Phase 3 changes finding IDs.**
  - It renumbers every finding (`orchestrator.md:363`, `:376`).
  - The AI-table assembly folds output-integrity and misinformation findings into the LLM-N sequence (#356).
- **So a compiled finding can't be matched to its record by ID.** "Every finding in `threats.md` traces to a persisted record" requires each compiled finding to carry its record's origin agent and origin ID.
- **Rendering the tables forces the #356 decision.** If FR-O.1 renders the tables in code, that code has to pick a rule for AI-table prefixes, and that rule is #356's fix.
- **Fix:**
  - OQ-3 defines the back-reference.
  - The trace-check tests cover renumbered and re-prefixed IDs.
  - The plan rules on #356 explicitly. If the tables are rendered, fold #356 in, for about +0.3 d. Otherwise keep NG4, and pin today's behavior in a test.

### C-9 (MEDIUM): the renderer and the other new scripts are a new trust boundary.

- They run in the main session and read part files written by agents that have just read third-party text (#360).
- Tree IDs become file names (`attack-trees/{id}-attack-tree.md`). F-373 had to close a CWE-22 traversal on exactly this path (KB Entry 24).
- **Fix.** The plan requires the following of the renderer, the Section 5 assembly step, the chain script and the trace check:
  - a closed, versioned key set with types and ranges, rejecting unknown keys, NaN and Infinity (Python's `json` accepts both by default);
  - the finding-ID allow-list `^(S|T|R|I|D|E|AG|AGP|LLM|OI|MI|TE)-\d+$` applied before any ID becomes part of a path, with a check that the resolved path stays inside its directory as a backstop;
  - escaping of `|` and newlines in agent-authored text before it goes into a table cell;
  - a size cap per file;
  - writes only under `{out}` (ADR-049 D5);
  - a runtime that needs nothing beyond the standard library. `/tachi.risk-score` mustn't need PyYAML, so constants such as the composite weights are pinned by a test against `schemas/risk-scoring.yaml`.

  The Step 7 security review names each new script.

### C-10 (MEDIUM): pin the arithmetic before writing the renderer, or recompute-and-flag will flag rounding noise.

- **The rounding mode is unstated.** `severity-bands.md:25` says "rounded to one decimal place" and stops there.
- **Python's default rounding contradicts a documented example.** `residual-risk.md:112` gives 9.1 × (1 − 0.50) = 4.55 → **4.6**, but Python's float `round()` returns **4.5**.
- **Band boundaries are inclusive** ("7.0 = High", `severity-bands.md:53`), yet a weighted sum in floating point can land at 6.999….
- **CVSS 3.1 has its own Roundup function.** Patch A's test calculator implements it and is self-tested on FIRST's examples.
- **Consequence:** without these pins, N16's check flags differences that are only rounding, and SC-4's "0 documented exceptions flagged" fails for reasons that have nothing to do with the defect.
- **Fix:**
  - ADR-050 pins:
    - decimal round-half-up on one-decimal inputs;
    - the boundary rule;
    - CVSS Roundup;
    - the review-date and SLA rules.
  - The golden rows include 4.55, composites of exactly 4.0, 7.0 and 9.0, and the documented clamps.
  - The PM decides whether a difference that is only rounding, in an old baseline, gets flagged as a correction.

### C-11 (MEDIUM): the fixture design (OQ-7) determines both the cost and whether the Definition of Done can be met.

- **The DoD's scale can't be guaranteed by a fresh live run.** On about 25 components it won't reliably produce 200+ findings or 40+ Critical (#397 N9).
- **The controls stage needs a target codebase to scan.**
- **The gated fixtures must avoid the `mmdc` path**, because no runner installs it.
- **Fix:** a fixed-seed generator, modeled on `tests/scripts/generate_pagination_fixture.py`, emits:
  - the architecture description;
  - a synthetic baseline run directory: a `threats.md` with 200+ findings, 40+ Critical, correlation groups and chain material, together with `attack-trees/`, `risk-scores.md`, `compensating-controls.md` and all three SARIF files;
  - the seeded-error variant, which carries wrong composites, bands, vectors and reachability values, plus missing vectors, with the documented exceptions included as controls;
  - the pair of runs that regroups findings;
  - a stub codebase.

  Only a Mermaid-free subset goes into the gated CI tests.

### C-12 (LOW): FR-C.1's scope is unclear, and the other adapter copies drift.

- **The adapter's risk-scorer copy is costly to port and no longer referenced.** The Claude Code adapter's `risk-scorer.md` is 1,419 lines in a different shape. Porting the new contract into it costs about 0.4 d. Since Part A, the command no longer tells users to copy it; `tachi.risk-score.md:42` now says to re-run the installer.
- **The adapter's orchestrator and report copies will fall behind.** Its `orchestrator.md` (1,226 lines) and `threat-report.md` (472 lines) will lack typed dispatch and the bounded Section 5.
- **Fix:**
  - The PM rules on FR-C.1: either a full port, or a superseded-by header plus a follow-up in the #369/#383 family.
  - The PRD states that the adapters' orchestrator and report copies are out of scope, following the precedent of F-373's FR-K14.6, which led to #383.

### C-13 (LOW): FR-K4.3's evidence may no longer exist.

- Run A ran in late September on v4.48.0.
- Claude Code keeps transcripts for 30 days by default (`cleanupPeriodDays`, as F-391's W2 record notes). Run A's transcripts likely survive only if they were archived privately.
- **Fix:** time-box the 5 Whys and decide its disposition in advance (TW-K4 (c)).

### C-14 (LOW): PRD text fold-ins.

- **§11:** the milestones come from this check (§10).
- **§10:** split SV-2 into 2a and 2b, and add SV-4 (the track split).
- **§12:** add #408, #409 and #412 to the coordinate list.
- **ICE:** recheck Effort 4. It predates the fold-in from #397, and an 8-day central suggests 3.
- **R-1:** its mitigation line should reference TW-0 and TW-ESC.

---

## 10. Milestones (proposed for PRD §11)

T0 is the day the plan stage starts. The dates assume back-to-back sessions; gaps between sessions push them out without adding effort.

| Milestone | Gate | Central | Floor | Ceiling |
|---|---|---|---|---|
| M1: Plan complete | spec, plan, ADR-050 and tasks have triple sign-off; TW-0, TW-ADR, TW-R and TW-N3 are evaluated | T0 + 0.6 | T0 + 0.4 | T0 + 1.0 |
| M2: Cut line green (end of W1) | shared contracts, renderer core and fixture committed; both CI legs green | T0 + 2.0 | T0 + 1.5 | T0 + 3.0 |
| M3: End of build session 1 (W2) | architect P0 checkpoint; TW-ESC evaluated; NEXT-SESSION handoff | T0 + 4.0 | T0 + 2.9 | T0 + 6.25 |
| M4: Implementation complete (W3 and W4) | offline end-to-end run on the fixture green; architect P1 checkpoint; code and security reviews | T0 + 6.25 | T0 + 4.3 | T0 + 9.75 |
| M5: Live verification recorded (W5) | the §5 matrix is in the PR; TW-L1 to TW-L3 recorded | T0 + 7.5 | T0 + 5.1 | T0 + 12.25 |
| M6: Deliver | `fix(374)` squash-merged; patch-release PR verified | **T0 + 8.0** | **T0 + 5.5** | **T0 + 13.0** |
| SC-8: live confirmation | the next large real-world run | lagging; tracked outside this feature | | |

If the plan starts on 2026-11-23 and the work runs on consecutive working days, M6 lands around 2026-12-02 at the central estimate, 2026-11-30 at the floor and 2026-12-09 at the ceiling.

---

## 11. Sign-off conditions for tasks.md

- **Assignments.** Every task has an agent from `.claude/agents/_README.md`, and no two lanes in a wave edit the same file (§3.1).
- **Cut line and trip-wires.**
  - The cut line is the end of W1.
  - Every trip-wire is written into tasks.md, together with the task that evaluates it: TW-0, TW-ADR, TW-R, TW-N3, TW-K4, TW-ESC, TW-CI, TW-L1 to TW-L3, and TW-CTX.
- **Rulings.** ADR-050 and plan.md rule on every TW-ADR item. Otherwise the dependent item is carved or held.
- **Repository hygiene.**
  - There is a W0 pre-state task, plus a task for lane P's data-layer oracle.
  - No PDF baseline is regenerated, and no pytest or extractor runs in the main tree.
  - Only explicit paths are staged.
- **Live runs.**
  - They sit in W5, in scratch adopters.
  - Each stage's disposition is decided in advance.
  - The SC-3 dispatch census is included.
- **Size.** No agent instance runs above 80% of its wave window. Expect about 44–50 tasks.

---

## 12. Calibration notes

Durations are branch to merge, taken from the delivery records:

| Feature | Estimate (floor / central / ceiling) | Re-cost at `/aod.tasks` | Actual | Reading for 374 |
|---|---|---|---|---|
| F-295, live verification runs | 0.5 / 1.0 / 2.0 | — | 1 day, including an honest stop decided in advance | Live gates with dispositions decided in advance are cheap. TW-L2 copies the pattern |
| F-362, semantic bundle | 4.0 / 4.9 / 6.0 | — | 6 days (+22%) | Serial semantic work overruns. Here lane O is the semantic lane |
| F-373, multi-lane bundle | 2.5 / 4.5 / 7.0 | 3.5 / 5.2 / 7.7 (effort 8.31) | 4 active days over 13 calendar days | The closest lane shape. Ratio 0.48 |
| F-391, Parts A and B | 2.0 / 4.0 / 7.5 | 2.9 / 4.7 / 7.5 (effort 7.7) | 5 days. Part A shipped, B2 is built and waiting, and B1 honest-stopped at TW-B1 | Ratio 0.65. About 4 h of live validation, and a trip-wire stop on a live gate |
| Fix 397 Patch A (#421) | — | — | about 1 day (13 files, two gated tests) | Small fixes at this pace take a day |

**What the precedents say:**
1. **Expect a small re-cost.** In both recent bundles, `/aod.tasks` re-costed the central upward by about 0.7 d (+16%). This check already includes the items its own review found (C-2, C-6), so expect a re-cost of 0.5 d or less, which still stays under TW-0.
2. **Effort held; the calendar slipped.** In both bundles, effort came in at or under the estimate. F-373's calendar slipped on gaps between sessions, not on effort.
3. **Live gates are where honest stops happen**: F-295's T026 and F-391's TW-B1. This bundle has 7–9 live runs, so plan for at least one follow-up filed from them.
4. **Scale.** This bundle's effort is 17.9 eng-days, against 8.31 for F-373 and 7.7 for F-391: about 2.1× and 2.3×. The renderer (about 3.8 effort-days, work packages 5–8) is the largest single new piece of code since F-302's populator, which took about 2 days.
5. **Output sizes**, measured in the committed examples at about 4 bytes per token:
   - SARIF: about 300–750 tokens per result;
   - `threats.md`: about 250–360 tokens per finding;
   - attack trees: about 1.0–1.45 KB each;
   - chains: about 750–1,000 tokens each.

   At 200+ findings, all three SARIF files and `attack-chains.md` exceed one 64k response, and `threats.md` comes close. That is why the fixture exercises FR-O.1, and why C-6 (a) exists.
6. **ICE.** Effort 4 was set before the fold-in. F-373's Effort 6 corresponded to about 4.5 days, so an 8-day bundle suggests 3.

**Lens record (Constraint Analysis):**
- **Identify.** The binding constraints are the renderer lane (the critical path) and the live wave (wall clock and usage). Agent capacity isn't binding.
- **Exploit.** One push per wave. Live runs on precomputed inputs, two at a time. Offline evidence for deterministic claims.
- **Subordinate.** Lanes C and D feed the renderer's part schema. Nothing runs live until W4 is green.
- **Elevate.** The chain script and the rendered SARIF move computation out of the orchestrator. The baseline-aware fixture makes the scale deterministic.
- **Repeat.** TW-ESC at the end of S1, and TW-L1 after the first live run, check whether the constraint has moved.
