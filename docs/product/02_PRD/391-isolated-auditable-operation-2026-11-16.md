---
prd:
  number: 391
  topic: isolated-auditable-operation
  created: 2026-11-16
  status: Approved
  approved: 2026-11-16
  feasibility: specs/391-isolated-auditable-operation/feasibility-check.md
  type: feature
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-11-16
    status: APPROVED
    notes: "v1.2: PM authored v1.0 from issue #391 and its validation (APPROVED_WITH_CONCERNS, ICE 22/P1); v1.1 folded the Triad review of v1.0 (architect CHANGES_REQUESTED 0/6/8/7 with 6 technical inaccuracies; team-lead APPROVED_WITH_CONCERNS C-1..C-9) per .aod/results/pm-revision-391.md. PM rulings: TW-A2 (Part A ships alone as fix(391) if #364 is open, Part B as feat(391) after it), C-7 wording, examples stay at 1.4, D-10 Verification Portal, C-9 out of scope, SARIF tool.driver.version out, runbook named ISOLATED_OPERATION_TACHI.md. v1.2 records the sign-offs and carries the architect iteration-2 items I2-N1..N6 to section 13."
  architect_signoff:
    agent: architect
    date: 2026-11-16
    status: APPROVED_WITH_CONCERNS
    notes: "Iteration 2 (delta re-review of v1.1): RC-1..RC-7 verified 7/7, technical inaccuracies remaining 0 (v1.0 had 6, above the constitution threshold), new findings 0 BLOCKING / 0 HIGH / 1 MEDIUM / 5 LOW. Rulings recorded as decided: D-1 pins stay sonnet with pinned-vs-served in the manifest and a dated ADR-019 note; D-4 matrix as a new section 8 appended to CLAUDE_PERMISSIONS.md guarded by extending tachi-permissions-verify.yml, out-of-output writes relocated into the output dir; D-6 session-scoped claude --settings profile primary; D-8 ~/.tachi/runs default, refuse inside any work tree, 0700 archive, structured manifest with fail-loud secret scan, no generated_at; D-9 install.sh saves its git describe value, version stamped by script, schema 1.1/1.2/1.4 and the 1.7/1.8 examples reconciled before 1.5. Carry-forwards for /aod.plan: I2-N1 (MEDIUM) FR-11 roster selection must not open a guard bypass; I2-N2..N6 (LOW) in section 13. Full review: .aod/results/architect-391.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-11-16
    status: APPROVED_WITH_CONCERNS
    notes: "FEASIBLE WITH MODIFICATIONS; neither veto exercised. Estimate: planning 4.0 / floor 2.0 / ceiling 7.5 eng-days branch-to-merge (Part A 3.2 / Part B 0.8), calibrated against F-373/F-362/F-329/F-295. 9 concerns (2 HIGH, 5 MEDIUM, 2 LOW), all folded in v1.1: SC-A1 as a dedicated scratch-project session not OpenClaw Phase B (C-1); build branches only after the key-handling patch merges, T0 (C-2); #364 merge gate with the TW-A2 escape hatch (C-3); W0 attribution spike before any B1 code (C-4); write set by transitive audit and the runbook in INSTALL_MANIFEST.md (C-5); guard traps a-e (C-6); SC-B3/AC-B2.2 reworded, examples stay at 1.4 (C-7); D-9 semantics (C-8); published-copy note (C-9). Trip-wires TW-0, TW-A1..A3, TW-B0..B4 in sections 9-10. Full review: .aod/results/team-lead-391.md; estimate: specs/391-isolated-auditable-operation/feasibility-check.md."
source:
  idea_id: 391        # equals prd.number (GitHub Issue #391)
  story_id: null
parts:
  A: [US-A1, US-A2, US-A3]   # egress truth, isolated-operation runbook + write confinement, permission matrix + CI guard
  B: [US-B1, US-B2]          # run provenance (archive + manifest), artifact version
  deferral_gate: "(v1.1) Trip-wires, not open decisions (section 9). Part B proceeds only if TW-B0 holds at /aod.tasks: D-1, D-8 and D-9 ruled in plan.md, the examples and SARIF rulings recorded, and Part B tasks at or under 3.0 effort-days. B1 also needs TW-B1 to pass at the W0' attribution spike and again on the W2 sessions: every dispatched tachi agent attributable by name from transcript structure, meta and line agent names agreeing, no empty histogram, and (from W2) each planted denial kind detected. B2 also waits for #364 and the schema reconciliation. B1 and B2 defer independently by honest stop (F-295 precedent; TW-B2 to TW-B4 also apply); the PRD then delivers on Part A and delivery.md records which trip-wire fired"
  sequencing: "(v1.1) Plan and the W0' spike now; the build branches from main after the key-handling patch merges (T0); feat(391) merges after #364, or Part A ships alone as fix(391) under the TW-A2 ruling (section 4); before #360"
---

# PRD-391 — Isolated and Auditable Operation

**Status**: Approved 2026-11-16 (PM ✓, Architect ⚠ after iteration 2, Team-Lead ⚠). v1.1 goes to the Architect for a delta re-review of RC-1 to RC-7. Source: GitHub Issue [#391](https://github.com/davidmatousek/tachi/issues/391), validated 2026-11-16 (PM: APPROVED_WITH_CONCERNS, ICE 22 / P1). Analysis: `_internal/planning/ANL-2026-11-16-cvp-best-practices-gap.md` (private). Reviews (local): `.aod/results/product-manager.md`, `.aod/results/architect-391.md`, `.aod/results/team-lead-391.md`. Estimate: `specs/391-isolated-auditable-operation/feasibility-check.md`.

> **Framing.** This PRD and every public doc it changes use neutral wording: "isolated and auditable operation". They make no claim about tachi's standing with Anthropic or under any program (D-2). Anthropic's Cyber Verification Program (CVP) guidance for members is the trigger and is covered by a mapping section in the runbook; its intent is cited and paraphrased, never reproduced. Technical recipes come from the public Claude Code documentation, cited per item (§14).
>
> **v1.1** folds in the Triad review of v1.0: the Architect's CHANGES_REQUESTED (0 blocking / 6 HIGH / 8 MEDIUM / 7 LOW; RC-1 to RC-7 and six technical inaccuracies, TI-1 to TI-6, all corrected) and its five rulings, now recorded as decided (D-1, D-4, D-6, D-8, D-9); the team-lead's APPROVED_WITH_CONCERNS (C-1 to C-9, the trip-wires in §9 and the estimate in §10); and the PM's rulings on review items (end of §4). LOW items are folded or carried to §13. Items marked *(v1.1)* are new or rewritten.

---

## 1. Problem Statement

tachi is positioned as local-first. `.claude/rules/scope.md` says architecture descriptions "never leave their machine" (line 16) and promises "no remote inference, no data leaving your environment" (line 37). Both statements are wrong in two ways, and nothing at the adopter's decision point says so:

1. **Inherent flow.** tachi runs inside Claude Code. The architecture description, every target-repo file an agent reads, and every finding the agents write are sent to the adopter's model provider (Anthropic, or their cloud provider's Claude endpoint). This is true of every run. *(v1.1)* Claude Code itself also sends usage metrics and error reports and fetches feature flags unless the adopter switches them off. That traffic is Claude Code's, governed by its settings; tachi's statements point to those settings rather than speak for them.
2. **Optional flow.** When `GEMINI_API_KEY` is set and `/tachi.infographic` runs, derived threat-model content, including names and descriptions taken from the adopter's architecture (the project name and assessment date; the names, types and short descriptions of components, trust zones, trust boundaries and data flows; finding IDs, descriptions, severities and risk scores; correlation groups of related findings and their descriptions; finding counts, severities and analysis coverage, overall and by component, zone, boundary, flow, threat category and MAESTRO layer; the overall risk posture; control-coverage and risk-reduction figures from compensating-control runs; counts of new, updated, unchanged and resolved findings since a baseline, with new findings marked; and, if a template cannot be loaded, a one-line system description) is posted to Google's Gemini API at `generativelanguage.googleapis.com`. README line 164 presents the key as a cosmetic choice ("if you want infographic images"), not as a data-handling decision.

Three further gaps turn up when a security team tries to run tachi inside an isolated environment, which is what Anthropic now asks of members using its reduced-safeguard models (sandbox with an egress allow-list, API keys injected from outside the sandbox, tooling validated before a run, transcripts kept at least 30 days and reviewed for unexpected egress, Claude Code auto mode with the environment described in `autoMode.environment`, scope phrased as intent, read-only and mutating tools separated):

3. **No runbook, and writes outside the run's output.** tachi documents no egress profile, no sandbox or auto-mode recipe, no retention guidance, and no statement that it is passive. Adopters have to reverse-engineer which hosts it reaches (two: the model provider and, optionally, Gemini; typst and mmdc run locally, and tachi's scripts and templates make no network calls) and which paths it writes. *(v1.1)* Some of those writes break or leak under a sandbox: the report step overwrites the installed `templates/tachi/security-report/report-config.typ` when a custom config is supplied and leaves `report-data.typ` in the installed template directory after a failed compile, and the infographic step writes predictable file names to the shared `/tmp`, which a sandboxed command cannot write.
4. **Implicit, unguarded privilege tiers.** The 21 agents under `.claude/agents/tachi/` are already tiered: 14 threat agents with Read/Glob/Grep only, four writers (attack-tree-delta, control-analyzer, risk-scorer, threat-report with Agent), and three Bash-capable agents (orchestrator with Agent and Write, report-assembler, threat-infographic). No document states this and no test pins it. *(v1.1)* The six `tachi.*` commands declare no `allowed-tools`, so they run Bash and write files with the main session's full toolset. The 15 copies under `adapters/claude-code/agents/` carry neither a `tools:` nor a `model:` key, so on that path they inherit every tool and the session's model. `docs/standards/CLAUDE_PERMISSIONS.md` describes the repo's own dev-time settings, which are not installed, as if they protected adopters.
5. **No provenance.** Every agent pins `model: sonnet`, and on the adopter's machine the model that actually served a turn is recorded only in Claude Code's transcripts *(v1.1)*, which it deletes after `cleanupPeriodDays`. In July 2026 a tachi run concluded that its agents "executed on Opus 4.8"; the September re-check found only the main session had been histogrammed and the subagent transcripts were gone. `threats.md` carries a schema version but not the tachi release that produced it, so a consumer cannot tell which taxonomy edition (for example OWASP LLM 2025 vs 2026) a file was written against. *(v1.1)* The schema version is itself unreliable: three documents declare 1.1, 1.2 and 1.4, and two tracked examples carry "1.7" and "1.8", which are the finding schema's version numbers, written into `threats.md` by the model (D-9).

**Why now.** The maintainer's CVP application is in progress, and adopters who gain CVP access will run tachi on reduced-safeguard models under Anthropic's isolation guidance. For a security product, a false "nothing leaves your machine" claim is a credibility defect on its own.

---

## 2. Goals & Non-Goals

### Goals

- **G1 (US-A1): egress truth.** Every public statement about data leaving the machine names both flows, at the point where the adopter decides, and says tachi sends nothing else *(v1.1)*.
- **G2 (US-A2): a validated runbook and confined writes.** A runbook for running tachi in an isolated environment, with a CVP mapping that separates what the session profile covers from what needs a process-level boundary *(v1.1)*, tested live on the platforms its header names and stamped with Claude Code version, OS, permission mode and date *(v1.1)*. tachi writes only under the run's output directory and the sandbox's per-user temp directory *(v1.1)*.
- **G3 (US-A3): a permission matrix with a CI guard.** One documented source for each agent's and command's tools, model, Bash commands and write locations *(v1.1)*, with the runtime-enforced columns pinned by CI on PR and on `push:[main]`.
- **G4 (US-B1): run provenance.** Each run's main and subagent transcripts archived outside any committable path, with a manifest that attributes a served model to every turn of every recorded subagent instance *(v1.1)*.
- **G5 (US-B2): artifact provenance.** `threats.md` records the tachi release that produced it, stamped by a deterministic step, not by the model *(v1.1)*.

### Non-Goals

- Any automated transcript scanner or review tool beyond the manifest (Anthropic's own review guidance is still forthcoming; no speculative machinery).
- Installing settings in adopter projects. *(v1.1)* The runbook documents one session profile that the adopter saves and passes with `claude --settings <file>` (D-6); it is a snippet, not an installed file. The auto-mode classifier ignores project-scope `autoMode` blocks, and the repo's own settings are dev-time only.
- The key-handling patch. It ships separately; its merge is the build's start gate (T0) and a precondition for the runbook's key-injection guidance.
- A process-level boundary (container, VM, sandbox runtime) *(v1.1)*. The runbook points to Claude Code's documented options for what the session profile cannot cover (FR-8).
- Scope-as-intent blocks in every agent (#360). This PRD lands first; #360 builds on the matrix.
- `/tachi.preflight` and a `--no-image` flag (ideas backlog).
- Changing the `model: sonnet` pins (D-1, decided). A supported override is a separate ADR-019 amendment.
- An adapter roster refresh (route to #369 or a follow-up; only the repair *path* is in scope, D-5).
- SARIF `tool.driver.version` *(v1.1, PM ruling)*.
- Correcting copies of the old claim published outside this repository *(v1.1, C-9)*: a maintainer action recorded in `delivery.md`.
- Any wording that claims standing, approval or certification for tachi (D-2).

---

## 3. User Stories

Part A (P1) ships first. *(v1.1)* Part B (P2/P3) is gated by trip-wires (§9), not by open decisions: the five Architect decisions are ruled (§4).

### US-A1 (P1): both data flows named at the decision point
**When** I decide whether to set `GEMINI_API_KEY`, or read what tachi promises about data handling, **I want to** see exactly what leaves my machine and where (my Claude Code model provider on every run; Google's Gemini API only if I set the key and run `/tachi.infographic`), **so I can** make an informed data-handling decision.
- AC-A1.1 *(v1.1)*: Given the docs in SC-A2's surface, when I search for any statement that no data leaves the machine, then every such statement uses the D-3 sentence or is gone (SC-A2).
- AC-A1.2: Given README's key instruction, when I read it, then it states what the infographic step sends and to which host before it tells me how to set the key.
- AC-A1.3 *(v1.1)*: Given `CLAUDE_PERMISSIONS.md`, when I read it as an adopter, then its header says §1–§7 describe the repo's dev-time settings, which are not installed; it states that WebFetch outside the allow list falls to "ask", not "deny", and that Bash `curl` is not covered; and §8 is the adopter-facing matrix (FR-3, FR-10).

### US-A2 (P1): a validated isolated-operation runbook
**When** my team or program requires isolation controls around reduced-safeguard models, **I want to** follow a runbook that gives tachi's egress profile, a session profile with sandbox and auto-mode settings, probe checks, write locations, retention, reporting routes and a passivity statement, **so I can** meet the guidance without trial and error.
- AC-A2.1 *(v1.1)*: Given the runbook's session profile, when a full run (`/tachi.threat-model` → `/tachi.risk-score` → `/tachi.compensating-controls` → `/tachi.infographic` → `/tachi.security-report`) executes with and without the key in a scratch adopter project installed with `install.sh`, then it completes with every SC-A1 probe passing and zero unexpected egress denials, on each platform the runbook header names (SC-A1).
- AC-A2.2 *(v1.1)*: Given the runbook, when I read its egress section, then it lists exactly the two hosts a tachi run reaches, names Claude Code's own operational traffic separately with the switches that turn it off, and states that typst and mmdc run locally; "nothing is fetched mid-run" rests on FR-9's offline render check, not on an absence of denials.
- AC-A2.3 *(v1.1)*: Given the runbook, when I look for how to retain transcripts, then it names `cleanupPeriodDays` at user scope, says the default of 30 days meets the floor and must never be lowered, and gives the reporting routes (D-10).
- AC-A2.4 *(v1.1)*: Given the runbook, when I read its header, then it carries "Last validated: Claude Code vX.Y.Z on <OS>, <permission mode>, YYYY-MM-DD", the minimum Claude Code version (v2.1.285), an owner and refresh triggers (D-12).
- AC-A2.5 *(v1.1)*: Given a full run under the profile, when I list the paths it wrote, then every path is under the run's output directory or the sandbox's per-user temp directory, and the installed `templates/tachi/` tree is byte-unchanged, including after a run with a custom `report-config.typ` (SC-A5).
- AC-A2.6 *(v1.1)*: Given the runbook's CVP mapping, when I read an item, then it is marked as covered by the session profile or as needing a process-level boundary, with a pointer to Claude Code's documented options for the latter.

### US-A3 (P2): a CI-enforced permission matrix
**When** I review tachi for approval or upgrade it, **I want to** read one matrix of every agent's and command's tools, model, Bash commands and write locations, guarded by CI, **so I can** trust that no release silently widens an agent's privileges.
- AC-A3.1 *(v1.1)*: Given the matrix, when CI runs on a synthetic change that adds or removes a tool, changes `model:` or adds a frontmatter key on any agent under `.claude/agents/tachi/`, or changes a tachi command's frontmatter, then it goes red; on the unchanged tree it is green; the guard's self-test exercises the red path on every run; it runs on PR and on `push:[main]` (SC-A3).
- AC-A3.2: Given every documented install or repair path, when I follow it, then the installed agents' tools match the matrix (SC-A4).
- AC-A3.3 *(v1.1)*: Given the matrix, when I read a Bash-capable agent's or a command's row, then it lists the exact command families it may run, the paths it writes and the child processes it spawns, and each column says whether Claude Code enforces it at runtime or it is a declaration.

### US-B1 (P2): run provenance
**When** a run finishes, **I want to** archive its main and subagent transcripts to a safe location and get a manifest (tachi version, session id, the model that served each agent, tool-call counts, outbound hosts, denied egress, artifact hashes), **so I can** show how a threat model was produced.
- AC-B1.1 *(v1.1)*: Given a recorded fixture run, when the archiver runs, then the manifest attributes a served model to 100% of assistant turns, main and per recorded subagent instance by agent name; it counts `<synthetic>` turns separately and never as served, and lists any tachi agent that did not appear as a separate subagent instead of inferring its attribution (SC-B1).
- AC-B1.2 *(v1.1)*: Given an unparseable line, a missing required meta key (`agentType`, `toolUseId`), a meta agent name that differs from the line-level `attributionAgent`, zero assistant turns or an empty histogram, when the archiver runs, then it exits non-zero; extra meta keys are tolerated and recorded.
- AC-B1.3 *(v1.1)*: Given a destination inside any git work tree (found with `git rev-parse`, since `git check-ignore` exits 128 outside a repository), when the archiver resolves it, then it refuses unless `git check-ignore` passes on a path inside it; it never writes into a non-empty destination, refuses a live session without `--allow-live`, and creates directories 0700 and files 0600 (SC-B2).
- AC-B1.4 *(v1.1)*: Given dummy keys planted in six places (a Bash header, a URL query, URL userinfo, `tool_result` text, a meta `description`, a denial message), when the manifest is built, then none appears in it, and a hit in the final scan fails the run with no manifest written (SC-B2).
- AC-B1.5 *(v1.1)*: Given a fixture with each denial kind planted (a sandbox refusal, a classifier block, a permission-rule deny), when the archiver runs, then each is reported, and the manifest's `denial_detection` field names the Claude Code versions whose fixture passed; for any other version it says detection is not validated, never an empty list (SC-B1).

### US-B2 (P3): artifact version
**When** I consume a `threats.md` written by any tachi release, **I want to** read the producing tachi version in its frontmatter, **so I can** interpret taxonomy codes correctly across releases.
- AC-B2.1 *(v1.1)*: Given a tachi installed by `install.sh`, when a threat model is written, then `tachi_version` equals the version the installer recorded (D-9), written by a deterministic step, and the schema change is additive (SC-B3).
- AC-B2.2 *(v1.1)*: Given the example baselines, when B2 lands, then the byte-identity suite shows no new failures vs the W0 pre-state (#365's six reds excepted), and no example is regenerated for the new field (SC-B3).

---

## 4. PRD Decisions

*(v1.1)* All twelve decisions are decided. D-1, D-4, D-6, D-8 and D-9 record the Architect's final rulings from the v1.0 review; the others are PM rulings. The PM's rulings on review items close the section.

### D-1: model pins vs provenance (Architect, decided: document-only) *(v1.1)*
No pin change and no ADR-019 amendment. A dated Note on ADR-019 records that the pins are kept deliberately and that each run's served model is evidenced by the B1 manifest. Pins are a reliability control as well as a cost one: session-model safeguards have switched models mid-run, and `inherit` would expose the 14 threat agents to that. The manifest records, per subagent instance, the pinned model (installed frontmatter at archive time) and the served-model histogram (transcript). Runbook wording: "tachi pins every agent to the `sonnet` model alias. Claude Code resolves that alias through your provider, whatever model your interactive session uses. A model passed explicitly when an agent is invoked would override the pin; tachi's commands pass none. Program access applies only to the models your program covers." The sentence "The run manifest records the model that actually served each turn." is added only if B1 ships. Any override (`inherit` pins, an installer `--model` flag) needs an output-quality and refusal-behaviour evaluation and stays a separate ADR-019 amendment.

### D-2: framing, title and sources (PM)
Title: "Isolated and auditable operation". No public doc claims standing, approval or certification for tachi; the spec fixes the exact term list that the SC-A2 sweep greps *(v1.1)*. Anthropic's guidance is cited by name and paraphrased. Recipes (session-profile keys, probe table, `autoMode.environment` slots, `cleanupPeriodDays`, credential masking) come from the public Claude Code docs, linked per item.

### D-3: truth-correction wording and locations (PM) *(v1.1, RC-5)*
One sentence pattern, used everywhere: "Your Claude Code model provider receives the architecture description, the files tachi reads and the findings on every run. If you set `GEMINI_API_KEY` and run `/tachi.infographic`, Google's Gemini API (`generativelanguage.googleapis.com`) also receives image prompts made of tachi's fixed layout instructions and derived threat-model content, including names and descriptions taken from your architecture (the project name and assessment date; the names, types and short descriptions of components, trust zones, trust boundaries and data flows; finding IDs, descriptions, severities and risk scores; correlation groups of related findings and their descriptions; finding counts, severities and analysis coverage, overall and by component, zone, boundary, flow, threat category and MAESTRO layer; the overall risk posture; control-coverage and risk-reduction figures from compensating-control runs; counts of new, updated, unchanged and resolved findings since a baseline, with new findings marked; and, if a template cannot be loaded, a one-line system description). By design, tachi sends nothing else, but an AI agent following tachi's templates writes each prompt, and no code checks it against this list before it is sent. Claude Code's own operational traffic, such as usage metrics, error reports and feature-flag fetches, is separate from tachi; it is governed by Claude Code's privacy and telemetry settings, and setting `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` turns these off." The last sentence links to those settings. Locations: `.claude/rules/scope.md` (lines 16 and 37), `README.md` (line 164 and the `/tachi.infographic` section), `docs/guides/DEVELOPER_GUIDE_TACHI.md`, `docs/standards/CLAUDE_PERMISSIONS.md` (adopter-facing claims), `SECURITY.md` and the runbook. The auto-mode `hard_deny` is tool-scoped (FR-6), so it never contradicts the inherent provider flow.

### D-4: matrix home, guard host, write set (Architect, decided) *(v1.1, RC-1)*
- **Guard host**: extend `.github/workflows/tachi-permissions-verify.yml`, which already runs on PR and `push:[main]` from one anchor with `contents: read`; no new workflow.
- **Matrix home**: a new section appended after §7 of `docs/standards/CLAUDE_PERMISSIONS.md`, "8. Shipped agent permission matrix (applies to adopters)", with the doc header restructured so §1–§7 read as dev-time (FR-3). Append-only: §3–§5 are never renumbered or renamed and no matrix row sits between §4 and §5, because the workflow greps those headings byte-exactly and the AC-2 script parses the §4–§5 range. The guard is a stdlib script that the job invokes directly: the job has no Python test runner, and a pytest module would be un-gated or pull pytest into it. Checks: FR-11. The installed runbook links the matrix at a version-pinned URL; `CLAUDE_PERMISSIONS.md` stays uninstalled.
- **Writes: relocate, not document.** `report-data.typ` and `report-config.typ` are generated in a run-scoped build directory under the run's output directory (a copy of `templates/tachi/security-report/`), using the extractor's existing `--output` and `--template-dir` flags (no script change), compiled from there with `--root .`, deleted on success and kept on failure inside the output directory. The infographic JSON goes into the output directory, or the extractor's stdout, never the shared `/tmp`. Resulting write set: the output directory (including `attack-trees/` and `attack-chains/` PNGs); the sandbox's per-user temp directory (Python `tempfile`, the Chromium profile); the main session's `{out}/architecture.md` snapshot; and, for `/tachi.architecture`, its output file plus `.archive/v{N}/`. No `allowWrite` entry is needed.

### D-5: adapter repair path (PM)
`docs/guides/DEVELOPER_GUIDE_TACHI.md` tells adopters to re-copy agents from `adapters/claude-code/agents/`, whose 15 files have no `tools:` or `model:` key *(v1.1)* and a stale roster. **Ruling**: point the repair path at `install.sh`; route the adapter roster to #369 or a follow-up; the guard covers `.claude/agents/tachi/**` and the runbook says so.

### D-6: settings delivery (Architect, decided: session-scoped profile) *(v1.1, L-1)*
The runbook gives one JSON profile that the adopter saves anywhere and passes with `claude --settings <file>` for tachi sessions. `--settings` applies above user, project and local settings and below managed settings, for that session only; Claude Code reads the profile's `sandbox` (including `credentials`, `strictAllowlist` and `tlsTerminate`), `permissions`, `env` and `autoMode` keys from it. `allowUnsandboxedCommands: false` set there makes the sandbox admin-required, so a repository's settings cannot loosen it. Subagents run in the session's process and use its sandbox, so the profile covers every tachi agent. User-global snippets are kept only for `cleanupPeriodDays` and as an opt-in always-on alternative, presented merge-not-replace. Conditions:
- **Merge, not replace.** Lists combine across scopes: the profile can add entries but cannot remove them, so the adopter's own `allowedDomains` and `WebFetch(domain:...)` allow rules still widen the Bash allowlist. Adopters check the effective config (the `/sandbox` Config tab; `claude --settings <file> auto-mode config`, confirmed at SC-A1) and run the probes under the profile.
- Every `autoMode` list includes `"$defaults"`; without it the built-in list is replaced, including the data-exfiltration `hard_deny`.
- **Path forms.** Permission rules use `~/` or `//` prefixes (a `/path` rule anchors at the profile file's directory). Sandbox paths use `~/` or absolute forms (an unprefixed sandbox path is not project-anchored; in user settings it resolves under `~/.claude`).
- **Retention** stays at user scope: the sweep runs after any session starts, so a per-session value need not protect earlier transcripts.
- **SC-A1 confirms** that the file form is honoured for `autoMode` (the auto-mode page lists inline JSON for `--settings`; fall back to inline JSON if not) and for `strictAllowlist` and `tlsTerminate` (the reference's scope column says "User or managed"; the sandboxing page also lists `--settings`).
- **Minimum version**: Claude Code v2.1.285, for the admin-required repository semantics; the header also records the version actually run.

### D-7: retention (PM)
The runbook uses Claude Code's native `cleanupPeriodDays` at user scope *(v1.1)*; the default of 30 days meets the floor, and the runbook says never to lower it. The archiver (US-B1) is justified by provenance, not retention.

### D-8: archive location, refusal, manifest, redaction (Architect, decided with changes) *(v1.1)*
- **Destination**: `~/.tachi/runs/<claude-project-dir-name>/<YYYY-MM-DD>-<session-id>/` by default (the date from the transcript's first timestamp, UTC), with `--dest` to override. The source project directory is found by matching the transcripts' `cwd` field to the project's realpath, never by re-deriving Claude Code's slug encoding; `CLAUDE_CONFIG_DIR` is honoured.
- **Refusal**: resolve the nearest existing ancestor of the destination with realpath. Inside **any** git work tree (for example a dotfiles repo at `$HOME`), require `git check-ignore -q` to pass on a path inside it, otherwise exit non-zero. Never write into a non-empty destination (re-archiving a session is a no-op checked by transcript hashes); refuse a live session (transcript modified within N seconds) without `--allow-live`; create directories 0700 and files 0600 with `O_EXCL`; never follow symlinks into a work tree.
- **Archive**: `<session>.jsonl` and the whole `<session>/` directory (`subagents/*.jsonl`, `subagents/*.meta.json`, `tool-results/`), copied verbatim and unredacted for evidence integrity. The runbook marks the archive sensitive: it holds the architecture, code, findings and any secret that ever entered a transcript.
- **Operation**: an operator tool, run from a plain shell after the session ends (under the profile's sandbox the default destination is, correctly, unwritable). It joins the `INSTALL_MANIFEST.md` script whitelist, and its tests join `tachi-pytest.yml`'s explicit module list.
- **Manifest**: JSON, `manifest_version: 1`, structured fields only, no free text. Run identity: `tachi_version` (marker or `unknown`), `session_id`, `claude_code_versions`, `started_at`/`ended_at` (transcript timestamps), `archived_at`. Integrity: `transcripts[{path, bytes, sha256}]`. Attribution: `main{served_model_histogram, turns, tool_calls_by_tool}` and `subagents[{agent_id, agent_type, attribution_agent, spawn_depth, parent_tool_use_id, pinned_model, served_model_histogram, synthetic_turns, turns, tool_calls_by_tool, unknown_meta_keys}]`. Context: `permission_modes_seen`. Egress: `egress_observed[{host, tool, count}]`, `egress_unparsed_count`, `egress_denied[{host, kind, count}]`, `denial_detection`. Artifacts: `artifacts[{path, bytes, sha256}]`, which needs `--output-dir` (otherwise `null` with a reason).
- **Redaction**: structural first (host names only, stripped of userinfo, query and fragment; anything failing a hostname check is recorded as `<unparseable>`), then a final scan of the manifest for known key formats and for the values of environment variables named `*KEY*`, `*TOKEN*`, `*SECRET*`, `*PASSWORD*` or `*CREDENTIAL*` (hash fields excluded). A hit fails the run with no manifest written: it signals a parser leak, which must never be redacted silently.
- **`generated_at`**: dropped from `threats.md`. It would be non-deterministic in baselines, and real frontmatter already carries `run_id`; `archived_at` lives in the manifest only.

### D-9: version source and schema (Architect, redirected) *(v1.1, RC-6)*
- **Source**: `install.sh` already computes `git describe --tags --always` after the `--version` checkout and before the EXIT-trap restore (`scripts/install.sh:589-593`), then discards it. It persists that value, adding `--dirty`; with no `.git` it falls back to `.release-please-manifest.json`'s `"."`; otherwise it writes `unknown`. No release-please `extra-files` wiring and no `release-please-config.json` change: a release-bumped tracked file would label every post-release `main` install with the previous release, the exact misreading `tachi_version` exists to prevent.
- **Marker**: one line at a tachi-owned installed path (preferably `templates/tachi/VERSION`, not the `.claude/` root), written after the copy loop through the installer's containment and symlink guards. The README manual-install loop writes the same line; installs that skip it read `unknown`, and the docs say so. Format coordinated with #369 (`adapters/*/VERSION` use `source_version:`). Post-release builds stay distinguishable (`v4.48.1-2-g3ecba74[-dirty]`), never rendered as SemVer `+` build metadata.
- **Deterministic stamp**: an idempotent stdlib step at the command layer writes `tachi_version`, following the affected-assets populator pattern; the model never authors it.
- **Reconcile, then bump.** Today `schemas/output.yaml` (installed) declares "1.1"; the `output-schemas.md` template declares "1.4"; its own validation checklist says "1.2"; the SARIF spec sources `semanticVersion` from output.yaml ("currently 1.1") while the examples emit "1.4"; real frontmatter carries six undeclared keys (`run_id`, `baseline`, `coverage_gate`, `has_attack_chains`, `has_agentic_patterns`, `has_source_attribution`). Tracked `threats.md` files sit at "1.1" (22), "1.4" (23), "1.7" (1) and "1.8" (1), and 11 lack `schema_version` in their first three lines. "1.7" and "1.8" were `schemas/finding.yaml`'s versions when those examples were written (it is now "1.9"). B2 updates output.yaml, the template, the checklist and the SARIF spec in lock-step, documents the de-facto keys, then bumps additively to "1.5".
- **No parser change and no baseline regeneration for the new field.** `parse_frontmatter` ignores unknown keys and has no version gate, and absence of `tachi_version` is the documented legacy case. The release still ships after #364 (minor-release ordering).

### D-10: reporting routes (PM) *(v1.1, OQ-3 closed)*
Out-of-scope model behaviour goes to Anthropic through the program's own channel. The public program pages read on 2026-11-16 (the Help Center article and the announcement) name no reporting address, so the runbook points members to the Verification Portal and their program terms. It prints an address only if Lane R finds one on a public Anthropic page at build time, cited with its URL and retrieval date. tachi defects and vulnerabilities go to the `SECURITY.md` private advisory route.

### D-11: runbook name and links (PM) *(v1.1, M-2)*
The runbook lives at `docs/guides/ISOLATED_OPERATION_TACHI.md`. The tachi suffix matches `DEVELOPER_GUIDE_TACHI.md` and cannot collide with the AOD template guides that `/aod.update` syncs into `docs/guides/`. It joins `INSTALL_MANIFEST.md` and its completeness test, so the link from the installed developer guide resolves in adopter projects. It is linked from README "How It Works", `docs/guides/DEVELOPER_GUIDE_TACHI.md` and `SECURITY.md`, and it links the matrix at a version-pinned URL. Not from `docs/security/`, which is gitignored here and not installed.

### D-12: freshness (PM) *(v1.1)*
The runbook header carries "Last validated: Claude Code vX.Y.Z on <OS>, <permission mode>, YYYY-MM-DD", the minimum Claude Code version (v2.1.285), an owner (maintainer) and refresh triggers: a Claude Code change to sandbox, auto-mode, `--settings` or retention behaviour; new program guidance; any change to an agent's or command's tools, model or write set.

### v1.1 PM rulings on review items

| Item | Ruling | Rationale |
|---|---|---|
| **TW-A2**: release classification | **Ship, don't hold.** If Part A is merge-ready and #364 has not merged, Part A ships alone as `fix(391)` (patch). Part B follows as a second PR, `feat(391)`, after #364, with the §9 trip-wires still applying. If #364 merged first, the bundle ships once as `feat(391)`. | The false data-flow claim is a defect in a security product, and #364 is unscheduled. PRD-373 shipped as `fix:` while #364 blocks minors. Part A is the correction plus the runbook and guard that keep it true. Part B adds a schema field and an operator tool, so it never rides a `fix` PR. |
| **C-7**: byte-identity wording | **Adopt** "no new byte-identity failures vs the W0 pre-state (#365's six reds excepted)" in AC-B2.2, SC-B3 and DoD item 3. | "Suite green" cannot hold while #365's six reds are open, and an added frontmatter field changes no rendered output. |
| **Examples** | **Stay at 1.4.** No example is bumped to 1.5 or regenerated for the new field. The two drifted tracked examples ("1.7", "1.8") are corrected to "1.4", frontmatter-only, in Lane B2 after #364, with the example-snapshot tests measured first in a scratch clone; if any rendered baseline would move, the correction carves out to a follow-up. The schema doc tells consumers to feature-detect `tachi_version` and to treat `schema_version` in pre-1.5 files as declared, not ordinal. | Keeps B2 free of baseline churn and clear of #364. Adopters' own files may carry drifted values that tachi cannot correct, so consumers need feature detection either way. |
| **D-10**: reporting address | The Verification Portal by default; an address only if a public Anthropic page names one at build time (D-10). | The program pages read on 2026-11-16 name none. |
| **C-9**: published copies | **Out of scope.** The maintainer corrects published copies of the old claim, including the article drafted at `specs/296-…/notes/cybersec-article-draft.md:131`, with the D-3 sentence; `delivery.md` records it. | SC-A2 is bounded to this repo. |
| **SARIF** `tool.driver.version` | **Out** (the SARIF ruling TW-B0 needs). | Consumers read `tachi_version` from `threats.md`; SARIF would add up to 0.25 d and touch `semanticVersion` semantics. Revisit with #369. |
| **Fallbacks** (TW-B4, auto mode) | If TW-B4 fires, AC-B1.1 is met by a committed synthetic structure-only fixture in CI plus a local check against the recorded run, logged in `delivery.md`. If auto mode is unavailable at W2, SC-A1 runs in default mode under the same profile, the header stamps the mode actually run, and the auto-mode recipe ships marked as not yet run live, with a follow-up issue. | Pre-ruled, so neither fallback stalls the build waiting on the PM. |

---

## 5. Functional Requirements

### Group A1: egress truth (`scope.md`, `README.md`, `DEVELOPER_GUIDE_TACHI.md`, `CLAUDE_PERMISSIONS.md`, `SECURITY.md`)
- **FR-1** *(v1.1)* Replace every data-locality statement with the D-3 sentence at every D-3 location. Immutable records are not edited: PRD-054:310 and PRD-060:400 stay as written, and ADR-014's "entirely self-contained" Context gets a dated Note (FR-20). → US-A1
- **FR-2** README's key instruction states the Gemini flow before the setup step. → US-A1
- **FR-3** *(v1.1, L-4)* `CLAUDE_PERMISSIONS.md`: the header says §1–§7 describe the repo's dev-time settings, which are not installed; state the two coverage gaps (WebFetch falls to ask; Bash `curl` is uncovered); correct the adopter-facing errors at `:11` ("default-secure … for adopters"), `:43` ("default-deny on outbound network egress") and `:235` (`--deny-tool`; the documented flag is `--disallowedTools`), the §6 fork-and-edit adopter model (adopters install with `install.sh` and receive no settings), and §7.4's wildcard claims, re-checked against current docs (the sandbox honours a bare `*`). The §3–§5 headings stay byte-exact. → US-A1

### Group A2: runbook and write confinement (`docs/guides/ISOLATED_OPERATION_TACHI.md`; report-assembler, threat-infographic, `tachi.infographic.md`)
- **FR-4** *(v1.1)* Egress profile: the two hosts; Claude Code's own operational traffic named separately with its switches; the local-only tools; the no-fetch, no-install statement, backed by FR-9's offline render check. → US-A2
- **FR-5** *(v1.1, RC-2, RC-3)* Session profile, one file passed with `claude --settings <file>` (D-6), every key checked in SC-A1:
  - sandbox: `enabled: true`, `failIfUnavailable: true`, `allowUnsandboxedCommands: false`; `network.allowedDomains: ["generativelanguage.googleapis.com"]`, `network.strictAllowlist: true`, and `network.tlsTerminate: {}`, the stated prerequisite of `mask` (without it the placeholder reaches the server unchanged and authentication fails);
  - `sandbox.credentials`: `envVars` masks `GEMINI_API_KEY` with `injectHosts: ["generativelanguage.googleapis.com"]` (each inject host must also be in `allowedDomains`); `files` denies `~/.ssh` and `~/.aws` with home-anchored paths (an unprefixed sandbox path is not project-anchored, and in user settings it resolves under `~/.claude`, so v1.0's `**/.env*` entry protected nothing);
  - `permissions.deny`: `WebFetch`, `WebSearch`, `Read(~/.ssh/**)`, `Read(~/.aws/**)` and `Read(.env*)`. Read deny rules are the primary secret-file control: they cover the Read tool and recognised Bash file commands, which `sandbox.credentials` never reaches (it covers sandboxed Bash only), and they merge into the sandbox config. A bare `.env*` pattern matches at any depth under the working directory;
  - `env.CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC: "1"`;
  - MCP servers: the runbook has adopters list any configured server in `deniedMcpServers` (it merges from every scope) or confirm there are none, and states the residual that hooks, the status line and local MCP servers run outside the sandbox;
  - no `excludedCommands` entry (never for an interpreter or a tachi script), no `allowWrite`, no `allowNestedUserNamespaces`;
  - the public probe table (`touch ~/sandbox-probe` fails; `curl --noproxy '*' https://example.com` fails) plus the FR-9 probes. `tlsTerminate` is experimental and lets the local proxy read sandboxed commands' HTTPS; the runbook says so and gives the fallback of denying the key, which leaves the key-less isolated default (no image). → US-A2, D-6
- **FR-6** *(v1.1, RC-4)* Auto-mode block in the same profile, every list keeping `"$defaults"`:
  - `environment`: primary use (threat modeling with tachi: it reads an architecture description and a local checkout, writes only under the run's output directory, and never connects to, scans or modifies a running system); host containment (Bash runs in Claude Code's sandbox with network limited to the Gemini host; the cloud metadata endpoint is not reachable); trusted internal domains (the Gemini host, only for the optional `/tachi.infographic` image request); sensitive data locations and audiences (the output directory and the architecture file hold confidential threat models; audiences: the security team, and Google's Gemini API for the derived infographic prompt only, meaning the content D-3 lists: the project name and assessment date; the names, types and short descriptions of components, trust zones, trust boundaries and data flows; finding IDs, descriptions, severities and risk scores; correlation groups of related findings and their descriptions; finding counts, severities and analysis coverage, overall and by component, zone, boundary, flow, threat category and MAESTRO layer; the overall risk posture; control-coverage and risk-reduction figures from compensating-control runs; counts of new, updated, unchanged and resolved findings since a baseline, with new findings marked; and, if a template cannot be loaded, a one-line system description); data retention (30 days or more via `cleanupPeriodDays`);
  - `hard_deny`, one tool-scoped prohibition: "Never use a tool (Bash, WebFetch, WebSearch, an MCP server or any other) to send tachi threat-model outputs, the architecture description, or files read from the analyzed repository to any network host other than generativelanguage.googleapis.com. Requests to that host are acceptable only from the /tachi.infographic image step and only with the derived infographic prompt." A `hard_deny` only blocks and grants nothing. The provider flow is not a tool call, so it is never contradicted. Gemini's allowance comes from `environment` alone; an audience that excluded Gemini would trigger the default block on sending data from a sensitive location to an excluded audience;
  - the classifier reads commands, not their output (a `-d @file` body hides content from it), so the entries must be accurate rather than relied on to see content. → US-A2, D-6
- **FR-7** *(v1.1, RC-1)* Write locations: "tachi writes only under the run's output directory and the sandbox's per-user temp directory; no `allowWrite` entries are needed." `/tachi.architecture` writes its output file and `.archive/v{N}/` inside the working directory. The list comes from the FR-10 audit, traced transitively through agents, skills, scripts and child processes. → US-A2
- **FR-7a** *(v1.1, D-4)* Relocation: report-assembler Steps 2a, 2c, 3a and 3d, the threat-infographic extraction step and `tachi.infographic.md` (lines 160–166) relocate every write outside the output directory, as D-4 rules; nothing writes to the installed `templates/tachi/` tree. The byte-identity suites are shown unaffected in a scratch clone (#365). → US-A2
- **FR-8** *(v1.1, RC-3)* Retention (D-7), reporting routes (D-10), the D-1 pin wording, the passivity statement ("tachi reads an architecture description and a local checkout; it never connects to, scans or modifies a running system"), the archive's sensitivity (if B1 ships) and the freshness header (D-12). A CVP mapping, cited and paraphrased, marks each item as covered by the session profile or as needing a process-level boundary, and points to Claude Code's documented options for the latter (sandbox runtime, dev container, VM). It says the sandbox covers shell commands only, that file and web tools, hooks and MCP servers run outside it, and that its hostname-based allowlist carries a domain-fronting caveat. → US-A2
- **FR-9** *(v1.1, RC-7, C-1, M-8)* Live validation record (W2): a dedicated maintainer-run session in a scratch adopter project installed with `install.sh`, not the tachi repo (its dev-time settings add WebFetch allow rules and hooks); macOS and a Linux VM, or "validated" scoped to the platforms actually run, with Linux using the R-2 fix; the full pipeline with and without the key, the key injected into the process environment only. Probes: the probe table; a planted `.env` refused through Read and through `cat`; WebFetch denied; `mmdc` rendering offline to byte-identical PNGs (scratch clone); the Gemini client trusting the session CA under `tlsTerminate`; auto mode working with non-essential traffic disabled. Stamp: Claude Code version, OS, permission mode and date. Before W2 the Gemini HTTP client form is pinned in `gemini-prompt-construction.md` (C-2), by the key-handling patch if it carries it, otherwise as a Lane R task. → US-A2

### Group A3: permission matrix and guard (`CLAUDE_PERMISSIONS.md` §8, guard script, `tachi-permissions-verify.yml`)
- **FR-10** *(v1.1, M-1)* The §8 matrix, appended after §7: per agent, tier, `tools:`, `model:`, Bash command families (exact), writes and hosts; a commands table for the six `tachi.*` commands (main session, full toolset: the populate script; `which typst` and `command -v mmdc`; `mkdir -p`, a copy into `.archive/v{N}/` and `shasum`; the architecture snapshot); a child-process note (`mmdc` and headless Chromium are spawned by the extractor and are invisible to transcripts and permission rules); and an "enforced vs declared" statement: Claude Code enforces `tools:` and `model:` at runtime, while the Bash and writes columns are declarations that only the adopter's sandbox and permission rules enforce. The Architect's privilege baseline (review §10) is the starting input; the writes column comes from the FR-7 audit. → US-A3
- **FR-11** *(v1.1, D-4, C-6)* Guard script (stdlib, invoked directly): a bidirectional roster selected by `name: tachi-*` frontmatter (21 agents; `_TACHI_AGENT_BEST_PRACTICES.md` excluded by name, with a negative test); the exact `tools:` set and `model:` value; the frontmatter key set pinned to `{name, description, tools, model}`, so adding `permissionMode`, `mcpServers`, `hooks`, `disallowedTools` or similar turns CI red; tachi command frontmatter (`allowed-tools`, `model`); Bash families from fenced shell blocks of the three Bash-capable agents against a per-agent allow-list (TW-A3 bound; prose is never scanned, so #360's scope blocks cannot false-red); a cross-check of the runbook's write-location list; and a `--self-test` mode that mutates a temp copy and must fail. → US-A3
- **FR-12** *(v1.1)* The workflow's path anchor gains `.claude/agents/tachi/**`, `.claude/commands/tachi.*.md`, the guard script and the runbook; the guard runs in the existing job on both triggers; anchor edits are sequenced with #369. SC-A3's `push:[main]` evidence arrives at merge, a lagging check as in F-329. → US-A3
- **FR-13** *(v1.1)* `DEVELOPER_GUIDE_TACHI.md`'s repair path points at `install.sh` (D-5); the runbook joins `INSTALL_MANIFEST.md` (D-11); SC-A4's installed-tools assertion joins the existing install-fidelity harness. → US-A3
- **FR-20** *(v1.1, L-7)* ADR-049 records the CI-enforced privilege contract and the write confinement (and, if Part B ships, the provenance manifest and the schema change), with dated Notes on ADR-019 (D-1) and ADR-014 (egress profile). → US-A1, US-A3

### Group B1: archiver and manifest (`scripts/archive-run-transcripts.py`)
- **FR-14** *(v1.1)* Inputs: a session id, or `--latest` for the project found by `cwd` match (D-8); copies the main `.jsonl` and the whole `<session-id>/` directory verbatim; stdlib only; honours `CLAUDE_CONFIG_DIR`; runs from a plain shell after the session; joins the `INSTALL_MANIFEST.md` script whitelist. → US-B1
- **FR-15** *(v1.1)* Destination, refusal and file-mode rules per D-8. → US-B1
- **FR-16** *(v1.1)* Manifest per D-8 (structured fields only, `manifest_version: 1`, with a schema doc); fail-loud rules per AC-B1.2; the `<synthetic>` rule; per-instance attribution, with agents that did not appear as separate subagents listed rather than inferred; redaction whose final scan fails loudly. → US-B1
- **FR-17** *(v1.1)* Fixtures: a synthetic structure-only fixture for the Lane B1 core, modelled on the W0' spike and covering two layout generations; and a real run recorded in W2 (the main session plus at least two subagents, one of them Bash-capable; each denial kind; a dummy key in all six places), scrubbed with its structure preserved and leakage-reviewed by security-analyst (TW-B4 governs the fallback). Tests join `tachi-pytest.yml`'s explicit module list. → US-B1

### Group B2: version (`scripts/install.sh`, the stamp step, `schemas/output.yaml`, `output-schemas.md`, SARIF spec)
- **FR-18** *(v1.1)* The installed marker per D-9 (Bash 3.2; harness tests on local-clone `--version` cases only); the README manual-install line; no `release-please-config.json` change. → US-B2
- **FR-19** *(v1.1, RC-6)* Reconcile output.yaml, the template, its checklist and the SARIF spec in lock-step and document the de-facto keys (D-9); bump additively to "1.5" with `tachi_version`, written by the deterministic stamp step from the marker, or as `unknown`; consumer guidance to feature-detect `tachi_version`; a static contract test (parsers unchanged); the examples ruling (§4); and, if `docs/architecture/01_system_design/README.md` is edited, a regeneration of `tests/fixtures/init-baseline-tree/` in the same commit (the harness clones HEAD). → US-B2

---

## 6. Non-Functional Requirements

Only the subsections with a surface are included.

- **Security** *(v1.1)*: the manifest never contains a secret value (planted keys in six places; a final-scan hit fails loudly); the archive is written only outside committable paths, with 0700/0600 modes; the profile adds only the Gemini host to the sandbox allowlist and adds no `excludedCommands`, `allowWrite` or `allowNestedUserNamespaces` entry.
- **Determinism** *(v1.1)*: `tachi_version` is written by a deterministic step, never by the model; no non-deterministic field enters `threats.md` (D-8 drops `generated_at`); no new byte-identity failures vs the W0 pre-state.
- **Code economy**: the archiver and the guard are stdlib-only Python; the guard reuses the existing permissions workflow; the matrix has one source; the relocation uses the extractor's existing flags *(v1.1)*.
- **Documentation accuracy** *(v1.1)*: every host, path and command in the runbook comes from the audited matrix or the live run; every recipe line cites the public Claude Code docs, re-read at build time (W1); the header stamps only what was run.
- **Repo hygiene** *(v1.1)*: no pytest or extractor runs in the main tree (#365); verification runs use scratch clones; reviewers check `git status` after agents return; staging uses explicit paths.

---

## 7. Definition of Done

1. *(v1.1)* FR-1 to FR-13, FR-7a and FR-20 implemented; SC-A1 to SC-A5 met and recorded, with SC-A1 stamped with what actually ran.
2. *(v1.1)* Part B: FR-14 to FR-19 implemented and SC-B1 to SC-B3 met, **or** B1, B2 or both deferred by honest stop, with the fired trip-wire recorded in `delivery.md`.
3. *(v1.1)* `/aod.analyze` clean; all PR checks green; no new byte-identity failures vs the W0 pre-state (#365's six reds excepted); no tracked example image or PDF baseline changed.
4. *(v1.1)* CHANGELOG and docs updated; no public doc claims standing, approval or certification for tachi (the spec's term list); PR title per the TW-A2 ruling.

---

## 8. Success Criteria

| ID | Criterion | Evidence |
|----|-----------|----------|
| SC-A1 *(v1.1)* | A full run, with and without the key, completes in a scratch adopter project under the session profile on each platform the header names (macOS and a Linux VM, or the claim scoped to the platforms run): the probe table and the FR-9 probes pass, auto mode works with non-essential traffic off, and there are zero unexpected egress denials | W2 live session(s); Claude Code version, OS, permission mode and date stamped in the runbook |
| SC-A2 *(v1.1)* | Zero data-locality claims without the D-3 sentence in README, DEVELOPER_GUIDE_TACHI.md, scope.md, CLAUDE_PERMISSIONS.md, SECURITY.md and the runbook; PRD-054, PRD-060 and ADR-014 excluded by name as immutable records | `grep` sweep record |
| SC-A3 *(v1.1)* | CI red on a synthetic tool add or remove, `model:` change or new frontmatter key on any agent, or a tachi command frontmatter change; green on the unchanged tree; the `--self-test` red path exercised on every run; PR and `push:[main]` | Workflow run evidence |
| SC-A4 | Every documented install or repair path yields agents matching the matrix | An assertion in the install-fidelity harness |
| SC-A5 *(v1.1)* | A full run writes only under the output directory and the sandbox's per-user temp directory; the installed `templates/tachi/` tree is byte-unchanged, including with a custom `report-config.typ` | W2 write listing; a scratch-clone test of the custom-config path |
| SC-B1 *(v1.1)* | 100% of assistant turns classified (served or synthetic), per recorded subagent instance by agent name; meta and line names agree; each planted denial kind detected; non-zero exit on unparseable structure or an empty histogram | Fixture tests in `tachi-pytest.yml` |
| SC-B2 *(v1.1)* | A destination inside any git work tree is refused unless ignored; modes 0700/0600; no planted key in the manifest; a scan hit writes no manifest | Tests |
| SC-B3 *(v1.1)* | `tachi_version` equals the installer's recorded version (or `unknown`), written deterministically; the schema change is additive; no new byte-identity failures vs the W0 pre-state (#365's six reds excepted) | Unit tests; install check; W2 field check |

---

## 9. Scope and Deferral Gate *(v1.1)*

**In (P1)**: Groups A1, A2 (with the write relocation) and A3, and FR-20. **In (P2/P3, trip-wire gated)**: Groups B1 and B2. **Out**: see Non-Goals.

**Cut line.** Lanes D (docs) and E (matrix and guard) are committed green before W1 closes; from then on, Part A's deterministic half can ship on its own.

The v1.0 gate (Part B waits until D-1, D-8 and D-9 are decided) opened at review, because all three are now ruled. The team-lead's trip-wires replace it. The team-lead evaluates them, and `delivery.md` records any that fire.

| Trip-wire | When | Rule |
|---|---|---|
| **TW-0** aggregate | `/aod.tasks` | Projected duration above 5.0 d (planning + 1.0) → carve the FR-11 body scan, then Part B (SARIF is already out). |
| **TW-B0** Part B entry | `/aod.tasks` | Part B proceeds only if D-1, D-8 and D-9 are ruled in plan.md, the examples and SARIF rulings are recorded (§4 records both), and Part B's tasks total 3.0 effort-days or less; otherwise honest-stop Part B (F-295 precedent). |
| **TW-A3** FR-11 bound | `/aod.tasks` | The Bash check is limited to fenced shell blocks in the three Bash-capable agents, against a per-agent allow-list; if it cannot be bounded, carve it (SC-A3 still ships). |
| **TW-B1** attribution, the honest stop | W0' spike; re-confirmed on the W2 sessions | B1 stops if any dispatched tachi agent's turns cannot be attributed to its name from transcript structure, any subagent that ran yields an empty histogram, meta and line agent names disagree, or a planted denial kind goes undetected. The denial criterion applies from W2, where the probes plant denials; the spike runs without a sandbox. It fails closed: an empty or partial histogram never passes. `delivery.md` records the observed layout; B2 may still ship. |
| **TW-B2** cost | Start of build session 2 | Part B's remaining work above 1.5 d, or any B lane more than 50% over budget → ship Part A at the cut line and defer Part B. |
| **TW-B3** layout | During B1 | Parser rework above 0.5 d, or a layout change mid-build → honest-stop B1. |
| **TW-B4** scrub | W3 | Scrub plus leakage review above 0.35 d, or a review that does not clear → commit a synthetic structure-only fixture and check the recorded run locally only (§4 fallback ruling). |
| **TW-A1** live budget | W2 | At most 3 debug loops or 1.0 d on SC-A1. Beyond that: document the limitation, make the key-less path the isolated default (R-1), stamp only what ran, file a follow-up, and do not hold the bundle. |
| **TW-A2** merge gate | Part A merge-ready | If #364 has not merged, Part A ships alone as `fix(391)` (PM ruling, §4). |

B1 and B2 defer independently. B2 also waits for #364 and the schema reconciliation; it does not depend on D-1 or D-8.

---

## 10. Timeline & Milestones *(v1.1)*

From the team-lead's `specs/391-isolated-auditable-operation/feasibility-check.md`: **planning 4.0 · floor 2.0 · ceiling 7.5 eng-days**, branch to merge (Part A 3.2 / Part B 0.8; bottom-up effort 6.7 / 4.35 / 12.15), confidence MEDIUM. An eng-day is an attention-day at the agent-orchestrated pace. The floor is Part A alone, with Part B honest-stopped at TW-B0 or TW-B1; the full-scope clean floor is 2.5, and with the trip-wires enforced the practical worst case is about 6.0. If Part B is deferred and later resumed as its own feature, budget 2.5–3.0 d.

**T0** is the day the key-handling patch merges to `main`. Dates assume back-to-back sessions; calendar time runs ahead of attention-days (F-373 took 13 calendar days for 4 active days).

| Milestone | Gate (trip-wires evaluated) | Central | Floor | Ceiling | Owner |
|---|---|---|---|---|---|
| M1 Plan complete | triple sign-off; TW-0, TW-B0, TW-A3 | 2026-11-17 | 2026-11-17 | 2026-11-18 | PM, architect, team-lead |
| M1' Attribution spike (W0') | TW-B1 pre-check | before T0 | before T0 | before T0 | maintainer, tester |
| M2 Build session 1 (W0–W1) | cut line green; architect P0 checkpoint | T0 + 1.6 d | T0 + 1.0 d | T0 + 2.9 d | team-lead |
| M3 Live validation (W2) | SC-A1 record; sessions archived; TW-A1; TW-B1 re-confirmed | T0 + 2.2 d | T0 + 1.3 d | T0 + 4.6 d | maintainer |
| M4 Build session 2 (W3) | TW-B2 at start; TW-B4; reviews; runbook stamp; CI evidence | T0 + 3.0 d | T0 + 1.5 d | T0 + 6.2 d | team-lead |
| M5 Deliver | `feat(391)` merged, or `fix(391)` under TW-A2 | T0 + 3.6 d (Part B: max(T0 + 3.6 d, #364 merged + 0.25 d)) | T0 + 1.7 d | T0 + 6.9 d | maintainer |

---

## 11. Dependencies *(v1.1)*

- **Start gate (T0)**: the key-handling patch. Part A edits README and developer-guide text that the patch also edits, and the runbook's key-injection guidance assumes it, so the build branches from `main` after it merges. The plan stage and the W0' spike run now.
- **Merge gate**: #364, which blocks the next minor release and is unscheduled. `feat(391)` merges after it; the TW-A2 ruling covers Part A. With the examples at 1.4, B2 shares no files with #364 apart from the drift correction, which follows it.
- **Coordinate**: #374 overlaps B2 on `output-schemas.md` and agent definitions; whichever merges second rebases, and any new Bash-invoked script changes the matrix rows. #369 shares the workflow family and the VERSION format; anchor edits are never concurrent. OpenClaw Phase B is an optional, lagging confirmation of the runbook, not SC-A1's vehicle (C-1): it follows #374 and runs a large architecture.
- **After**: #360 (scope-as-intent blocks build on the matrix; the FR-11 bound keeps their prose green; refresh its AC3 after the key-handling patch).
- **Pre-state**: #365 (six byte-identity reds; scratch clones only).
- **External**: Claude Code sandbox, `--settings`, auto-mode and retention behaviour as documented on 2026-11-16 and re-read at W1 (minimum v2.1.285). Auto-mode availability on the maintainer's account and the Gemini key item, both confirmed by name before W2; any temporary user-settings edit is backed up and restored. Anthropic's forthcoming transcript-review guidance (out of scope until published).

---

## 12. Risks & Open Questions

### Risks
- **R-1 Auto mode blocks the Gemini POST** as exfiltration despite the environment entries. Mitigation: FR-6's trusted-domain and audience entries; SC-A1 runs with the key; under TW-A1 the runbook documents the denial and makes the key-less path the isolated default.
- **R-2 Chromium fails inside the sandbox on Linux and WSL2** *(v1.1, H-6)*, exiting with "No usable sandbox!". `mmdc` runs as a child of the extractor, so `/tachi.security-report` with attack trees fails. Mitigation: never an `excludedCommands` entry for the extractor (Claude could edit the script and run it unsandboxed) and never `allowNestedUserNamespaces` (it turns off a sandbox boundary). Acceptable fixes: a puppeteer `--no-sandbox` config for `mmdc` (a reviewed code change, also checked under auto mode) or a documented attack-tree-less isolated default. Native Windows has no sandbox and `failIfUnavailable` makes Claude Code exit, so Windows is WSL2-only.
- **R-3 TLS termination is experimental** *(v1.1)*, and masking depends on the Gemini client trusting the session CA. Mitigation: the client form pinned before W2, CA trust probed on each OS, and the deny fallback (FR-5).
- **R-4 The effective config is a union** *(v1.1)*: the profile adds entries but cannot remove the adopter's own. Mitigation: effective-config checks and probes under the profile; plan evaluates `--setting-sources`.
- **R-5 The transcript layout is internal and drifting** (the meta key set grew from 6 to 9–10 keys between Claude Code 2.1.282 and 2.1.319). Mitigation: fail only on missing required keys and record extras; two layout generations in the fixtures; the Claude Code version in the manifest; TW-B3.
- **R-6 The orchestrator's dispatch topology is unobserved** *(v1.1)*: no retained transcript holds a tachi orchestrator run. Mitigation: the W0' spike before any B1 code; per-instance attribution; agents that did not appear as subagents are listed, not inferred; TW-B1.
- **R-7 "Zero denials" can mean "format not recognised"** *(v1.1, M-5)*. Mitigation: each denial kind planted in the fixture; `denial_detection` names validated versions only.
- **R-8 Recipes drift.** Mitigation: the D-12 header and triggers.

### Open Questions *(v1.1)*
All four v1.0 questions are closed: OQ-1 by the D-1 and D-6 rulings, OQ-2 by the D-4, D-8 and D-9 rulings, OQ-3 by the D-10 ruling, and OQ-4 by the feasibility check (§10) and the trip-wires (§9). What remains is listed as plan carry-forwards (§13).

---

## 13. Carry-forwards for /aod.plan *(v1.1)*

1. **D-1**: confirm whether `ANTHROPIC_DEFAULT_SONNET_MODEL` remaps the alias for subagents and whether `CLAUDE_CODE_SUBAGENT_MODEL` outranks agent frontmatter; the runbook states only what is confirmed.
2. **D-6**: evaluate `--setting-sources` to exclude user settings; confirm the `cleanupPeriodDays` sweep's cross-project scope; pre-stage the W2 profile from the Architect's skeleton (review §6.5).
3. **L-6, exact-command defects on lines FR-7a edits**: `threat-infographic.md:167` runs `python` (absent on stock macOS) where the command uses `python3`, and `tachi.infographic.md:166` uses `grep -P`, which BSD grep rejects, so MAESTRO templates are skipped silently on macOS. Both can fail SC-A1 on macOS; decide before W2 whether to fold them into FR-7a or file them as defects.
4. **Relocation**: the exact step edits and the scratch-clone byte-identity proof; if the relocation slips, file the `report-config.typ` overwrite as a defect.
5. **B1**: the manifest schema doc, the fixture contents, the `N` seconds of the live-session rule, and the install-manifest entry.
6. **B2**: marker placement inside the containment guards, the #369 format and the consumer guidance; also decide whether the stamp step should write `schema_version` too, which would end the drift class (default: no).
7. **W2 logistics**: one session serves SC-A1 in both configurations, the B1 recorded fixture, SC-B3's field check and a denial sample; the key comes from the maintainer's secret store into the process environment and is never echoed.
8. **#365 hygiene**: every verification that runs extractors or pytest uses a scratch clone; reviewers check `git status` after agents return.

---


**Architect iteration 2 (v1.2)**: I2-N1 (MEDIUM) FR-11 must select the agent roster so that no file can opt out of the guard (see `.aod/results/architect-391.md` I2-N1 for the bypass); I2-N2 (LOW) architect self-corrections to iteration-1 rulings; I2-N3 (LOW) wording precision; I2-N4 (LOW) make the ADR-019 note and FR-20 conditional on B1 shipping; I2-N5 (LOW) give TW-B1's "dispatched" an operational definition before the W0' spike; I2-N6 (LOW) the Read-deny baseline invites extension to other credential stores (`~/.netrc`, `~/.git-credentials`, `~/.kube`, `~/.docker/config.json`, cloud-CLI configs).

## 14. References

- Issue #391 and its PM validation comments; `.aod/results/product-manager.md` (local)
- Triad reviews of v1.0 (local): `.aod/results/architect-391.md`, `.aod/results/team-lead-391.md`; `specs/391-isolated-auditable-operation/feasibility-check.md`
- `_internal/planning/ANL-2026-11-16-cvp-best-practices-gap.md` (private gap analysis)
- `.claude/rules/scope.md`; `README.md`; `docs/guides/DEVELOPER_GUIDE_TACHI.md`; `docs/standards/CLAUDE_PERMISSIONS.md`; `SECURITY.md`; `INSTALL_MANIFEST.md`
- `.claude/agents/tachi/*.md` and `.claude/commands/tachi.*.md` frontmatter; `adapters/claude-code/agents/`
- `.github/workflows/tachi-permissions-verify.yml`; `.aod/scripts/bash/claude-permissions-ac2-crosscheck.sh`; `.github/workflows/tachi-pytest.yml`
- `schemas/output.yaml`; `schemas/finding.yaml`; `.claude/skills/tachi-orchestration/references/output-schemas.md` and `sarif-specification.md`; `scripts/install.sh` (`:589-593`)
- ADR-014, ADR-019 (model field governance), ADR-049 (new); #360, #361, #364, #365, #369, #374; F-295 (honest-stop precedent); PRD-373 (`fix:` while #364 blocks minor releases)
- Claude Code docs, read 2026-11-16: [sandboxing](https://code.claude.com/docs/en/sandboxing) (default write set, credential masking and `tlsTerminate`, strict allowlist, what runs outside the sandbox, Chromium on Linux, limitations and scope); [auto-mode configuration](https://code.claude.com/docs/en/auto-mode-config) (scopes, `environment`, `hard_deny`, `"$defaults"`); [permission modes](https://code.claude.com/docs/en/permission-modes) (default classifier blocks); [permissions](https://code.claude.com/docs/en/permissions) (Read rule paths and anchors); [settings](https://code.claude.com/docs/en/settings) (`--settings` precedence); [settings reference](https://code.claude.com/docs/en/settings-reference) (sandbox path prefixes, `strictAllowlist`, `tlsTerminate`, `cleanupPeriodDays`, privacy and telemetry)
- Anthropic: "Expanding the Cyber Verification Program" (2026-10-06) and the Cyber Verification Program Help Center article

---

## Approval & Sign-Off

| Role | Agent | Status | Date | Comments |
|------|-------|--------|------|----------|
| Product Manager | product-manager | ✅ Approved | 2026-11-16 | v1.0 author; v1.1 fold-in; rulings in frontmatter |
| Architect | architect | 🟡 Approved with Comments | 2026-11-16 | Iteration 2: 0/0/1/5 new, 0 inaccuracies, RC 7/7 (`.aod/results/architect-391.md`) |
| Engineering Lead | team-lead | 🟡 Approved with Comments | 2026-11-16 | 4.0 / 2.0 / 7.5 eng-days; C-1..C-9 folded (`feasibility-check.md`) |

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-16 | product-manager | Initial PRD from issue #391 and the PM validation findings (D-1..D-12) |
| 1.1 | 2026-11-16 | product-manager | Folded the Triad review of v1.0. Architect: RC-1 to RC-7 and TI-1 to TI-6 corrected (D-3, D-4, D-9, FR-5 to FR-7, FR-9, FR-19); rulings D-1, D-4, D-6, D-8 and D-9 recorded as decided; H-1 to H-6 and M-1 to M-8 folded; L-1 to L-5 and L-7 folded, L-6 carried to §13. Team-lead: C-1 to C-9 folded; trip-wires TW-0, TW-A1 to TW-A3 and TW-B0 to TW-B4 replace the deferral gate (§9 and frontmatter); §10 milestones relative to T0, from feasibility-check.md. New: FR-7a, FR-20, SC-A5, AC-A2.5, AC-A2.6, AC-B1.5; references moved to §14. PM rulings: TW-A2 (Part A ships alone as fix(391) if #364 is open), C-7 wording, examples stay at 1.4, D-10 (Verification Portal), C-9 out of scope, SARIF out, D-11 runbook name, TW-B4 and auto-mode fallbacks. OQ-1 to OQ-4 closed. Status stays In Review |
| 1.2 | 2026-11-16 | product-manager | Triad sign-offs recorded (PM APPROVED; Architect APPROVED_WITH_CONCERNS after iteration 2, 0 inaccuracies; Team-Lead APPROVED_WITH_CONCERNS). Architect iteration-2 items I2-N1..N6 carried to section 13. Status: Approved |
| 1.3 | 2026-11-16 | product-manager | PM wording amendment from the plan review (R-3): the D-3 parenthetical and the auto-mode audiences entry now describe what the infographic step sends as finding IDs with one-line threat descriptions, component/trust-zone/data-flow labels, severity counts and the overall risk posture; Lane R confirms the field list against the pinned client form at the start of W1. No build work changes; no Triad re-review. |
| 1.4 | 2026-11-19 | product-manager | D-3 field list per T005; PM ruling (`specs/391-isolated-auditable-operation/test-results/field-list.md` §10). T005 found nine items beyond R-8's list and none droppable, so D-3, §1 item 2 and the FR-6 audiences now carry the complete list: R-8's items plus component types, per-finding severities and risk scores, correlation groups, analysis coverage, threat-category and MAESTRO-layer breakdowns, compensating-control figures and baseline change counts. "One-line threat descriptions" became "descriptions" (the executive-architecture callouts send full text); the system description is marked as sent only when a template cannot be loaded; the lead-in names the host, the fixed layout instructions, and the names and descriptions taken from the architecture. "tachi sends nothing else" now reads "By design, tachi sends nothing else", followed by the disclosure that an AI agent writes each prompt and no code checks it. The last sentence names `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` (plan.md:162). No build work changes; no Triad re-review. |
