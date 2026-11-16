---
artifact: feasibility-check
feature_id: 391
owner: team-lead
date: 2026-11-16
prd_number: 391
status: draft
estimate:
  planning_days: 4.0
  floor_days: 2.0
  ceiling_days: 7.5
---

# Team-Lead Feasibility Check: Feature 391, Isolated and Auditable Operation

**Verdict**: APPROVED_WITH_CONCERNS · **FEASIBLE WITH MODIFICATIONS**. One bundle with a Part A cut line, and Part B behind a mechanical deferral gate.
**Estimate**: planning **4.0** · floor **2.0** · ceiling **7.5** eng-days, branch to merge · **Part A 3.2 / Part B 0.8** · confidence **MEDIUM**
**Scope reviewed**: PRD-391 v1.0 (US-A1..A3, US-B1..B2, D-1..D-12). Pointers verified at `3ecba74`.
**Lenses**: Constraint Analysis, Systems Thinking (file-ownership map)
**Vetoes**: timeline and capacity vetoes **not exercised**
**Concerns**: 9 (2 HIGH, 5 MEDIUM, 2 LOW). All resolve as PRD fold-ins or plan-stage rulings. None blocks Define exit.
**Full review**: `.aod/results/team-lead-391.md` (local; it has the full evidence table and the lens record)

---

## 1. Verdict

- **Effort and duration.** Bottom-up effort is about **6.7 eng-days** across five lanes that share no files. That compresses to about **4.0 attention-days from branch to merge**. The only long serial step is one maintainer-run live validation session. That one session can serve:
  - SC-A1, with and without the key;
  - the B1 recorded fixture;
  - the SC-B3 field check.
- **Part B is about half the PM's §4.4 view (1–1.5 weeks).** Three cost drivers measured smaller than assumed:
  - The schema 1.4 → 1.5 bump touches no rendered baseline. Parsers ignore unknown frontmatter keys, no report template renders the schema version, and the infographic goldens carry their own JSON version.
  - `scripts/install.sh` is already a release-please extra-file, and it already computes an installed version.
  - Per-agent attribution is a join on fields Claude Code already writes: a per-subagent sidecar with the agent type, and the served model on every assistant turn.
- **One Part B risk measured larger.** No retained local transcript contains a tachi orchestrator run, so nobody has observed how its 14 threat-agent dispatches are recorded. The transcript layout also changed between sessions only weeks apart. This is the Part B honest-stop trip-wire (TW-B1). It can be tested cheaply before any Part B code is written.
- **Calendar is set by three gates outside this feature.**
  - The build starts only after the infographic key-handling patch merges.
  - The merge waits on #364, which is still unscheduled.
  - OpenClaw Phase B cannot be SC-A1's vehicle: in the maintainer's run plan it follows #374.

**"With modifications"** means six PRD fold-ins before `/aod.tasks`. Each is detailed under the concern it resolves:
1. C-1: SC-A1 vehicle.
2. C-2: start gate and client pin.
3. C-3: relative milestones and escape hatch.
4. C-4: attribution spike and trip-wires.
5. C-5 and C-6: audited write set, link targets, guard placement.
6. C-7: SC-B3 wording and examples ruling.

---

## 2. Estimate

**Unit.** An eng-day is an attention-day at the AOD agent-orchestrated pace, measured from branch to merge. It is the same unit as the F-373, F-362, F-329 and F-295 checks.

| Band | Days | Part A / Part B | Conditions |
|---|---|---|---|
| **floor** | **2.0** | 2.0 / 0 | Part B honest-stopped at TW-B0 or at the TW-B1 spike. Part A is clean: the audit finds nothing new, the guard goes green first time, and both live runs pass first time |
| **planning (central)** | **4.0** | 3.2 / 0.8 | Full scope. Assumes:<br>• one SC-A1 debug loop;<br>• the spike passes;<br>• one transcript-layout adjustment in B1;<br>• examples stay at schema 1.4 and the SARIF version is out;<br>• one CI fix-forward and a small rebase |
| **ceiling** | **7.5** | 6.0 / 1.5 | Full scope, and everything grows:<br>• 3 SC-A1 debug loops (`mmdc`/Chromium under the sandbox, TLS-terminated key masking, auto mode on the Gemini POST), plus a blocked-path write-up;<br>• body-scan churn and 2 CI fix-forwards;<br>• B1 needs two layout generations and a scrub iteration;<br>• B2 takes SARIF `tool.driver.version` and an example bump;<br>• rebases across the patch, #374 and #364;<br>• a third build session |

`floor ≤ planning ≤ ceiling` holds (2.0 ≤ 4.0 ≤ 7.5).
- The full-scope clean floor is 2.5.
- With the trip-wires enforced, the practical worst case is about 6.0 (Part A at its ceiling, with B carved).
- If Part B is deferred and later resumed as its own feature, budget 2.5–3.0 d. It then loses the shared plan, the shared live run and the parallel lanes.

**Calibration** (branch to merge, from the delivery records):

| Feature | Estimate (floor / central / ceiling) | Actual | Reading for 391 |
|---|---|---|---|
| F-329 CI guard | 1.0 / 1.5 / 3.0 | same day | A3 has the same shape. Budget it near central, because the matrix needs an audit first |
| F-295 live verification runs | 0.5 / 1.0 / 2.0 | 1 day, including an honest stop | SC-A1 has the same shape. Honest stops declared in advance are cheap |
| F-302 scripts + gated tests | 1–2 | ~2 days | B1 has the same shape |
| F-373 multi-lane bundle | 2.5 / 4.5 / 7.0 | 4 active days, 13 calendar days | The closest whole-bundle analogue. Effort came in under estimate, but the calendar slipped on gaps between sessions |
| F-362 semantic bundle | 4.0 / 4.9 / 6.0 | 6 days (+22%) | Serial semantic work overruns. 391 has little of it |

**Effort vs duration.** Bottom-up effort is **6.70 central / 4.35 full-scope clean / 12.15 ceiling** eng-days. Duration is about 0.6 of effort, for three reasons:
- five disjoint lanes run in W1;
- the live session is the only long serial step;
- about 1.5 d of attention-bound work is serial (plan rulings, the live session, reviews, deliver).

---

## 3. Per-group estimates (effort, eng-days)

| Group | Central | Floor | Ceiling | Dominant driver |
|---|---|---|---|---|
| **A1** egress truth (FR-1..3) | 0.30 | 0.20 | 0.50 | The literal claims are only at `scope.md:16` and `:37`. Implied claims are at `CLAUDE_PERMISSIONS.md:11` and `:43`. Also: the README `:164` decision point, the Developer Guide key sections, D-3 wording review, and the SC-A2 sweep |
| **A2** runbook: research | 0.30 | 0.20 | 0.45 | Claude Code docs as of build day (sandbox, auto mode, `--settings` scope, `cleanupPeriodDays`), public CVP sources, OQ-3 |
| **A2** runbook: authoring | 0.50 | 0.35 | 0.70 | Ten sections. The write locations come from the A3 audit |
| **A2** SC-A1 live validation | 0.60 | 0.30 | 1.65 | Two full pipelines, with and without the key, in a separately launched session. Plus the probe table, denial review and the stamp |
| **A3** write-set audit + matrix (FR-10) | 0.30 | 0.20 | 0.40 | 21 rows. For the Bash-capable agents, trace commands and writes through skills and the scripts they invoke |
| **A3** cross-check test (FR-11) | 0.40 | 0.25 | 0.70 | Multi-line YAML `tools:` lists; select agents by `name:`; bounded body-scan |
| **A3** wiring + SC-A3 CI evidence (FR-12) | 0.15 | 0.10 | 0.30 | Anchor and step in an existing workflow; a synthetic red, then green |
| **A3** SC-A4 + FR-13 + runbook manifest line | 0.25 | 0.20 | 0.35 | Add one assertion to F-373's existing end-to-end and manual-block install harness |
| **Part A items** | **2.80** | **1.80** | **5.05** | |
| **B0** attribution spike | 0.15 | 0.10 | 0.25 | One scoped run in a scratch project, then a structure check. Decides TW-B1 before any B code |
| **B1** archiver, manifest, redaction, fixtures (FR-14..17) | 1.60 | 1.10 | 2.90 | Stdlib only. Join sidecar agent type to served model; fail loudly against a minimal stable contract; refuse committable destinations; planted-key test; scrub a recorded fixture for a public repo |
| **B2** install marker + schema 1.5 (FR-18..19) | 0.80 | 0.50 | 1.60 | Bash 3.2 marker, read after any `--version` checkout; additive field; same-commit init-baseline-tree regen; examples stay at 1.4 |
| **Part B items** | **2.55** | **1.70** | **4.75** | |
| Shared overhead (plan, W0, reviews, CI and handoffs, deliver, rebase) | 1.35 | 0.85 | 2.35 | |
| **Effort total** | **6.70** | **4.35** | **12.15** | |
| **Duration, branch to merge** | **4.0** | **2.0** (Part A only) | **7.5** | |

---

## 4. Dependency chain

```
[now]   Plan stage (Architect rulings D-1, D-4, D-6, D-8, D-9)
[now]   W0' attribution spike (scratch project, no sandbox, no key)  ──► TW-B0 + TW-B1 decided
        key-handling patch merges  ═══ T0 (build start gate)
           ▼
        W0 pre-state ─► W1 [D | R | E | B1 | B2] (cut line: D + E green)
           ─► W2 live session(s) (maintainer) ─► W3 [B1 fixture | runbook stamp | CI evidence | reviews]
           ▼
        #364 merged? ── yes ─► W4 deliver feat(391)
                     └─ no ──► TW-A2: PM rules hold, or ship Part A alone as fix(391)

#374 ─► OpenClaw Phase B  (optional, lagging confirmation; not SC-A1's vehicle)
391  ─► #360              (builds on the matrix)
```

| Dependency | Role | Status (2026-11-16) | Effect |
|---|---|---|---|
| Infographic key-handling patch | **start gate** | not shipped (latest tag v4.48.1) | Branch the build from `main` after it merges. The plan stage and the spike can run now |
| #364 | **merge gate** | Discover, unscheduled | `feat(391)` is a minor release, and #364 blocks the next minor. TW-A2 is the escape hatch. If examples stay at 1.4, B2 shares no files with #364 |
| #374 | coordinate | Discover | Overlaps B2 on `output-schemas.md` and the orchestrator, so whichever merges second rebases. It also gates OpenClaw Phase B |
| #365 | pre-state | open | 6 byte-identity reds already exist (see C-7). Run everything in scratch clones only |
| #360 | after | Discover | Builds on the matrix. The FR-11 bound keeps its scope-block prose green |
| #369 | coordinate | open | Same workflow family. Never edit the same workflow anchor in two branches at once |
| Auto Mode availability, Gemini key item | external | not verified in this review | Confirm both before W2 |

---

## 5. Parallel waves and agent assignments

Agent names come from `.claude/agents/_README.md`. The `tachi-*` agents are the subject under test, not assignees. `orchestrator` coordinates the waves.

**Sessions:**
- **P**: plan.
- **S1**: W0 + W1.
- **L**: W2, launched by the maintainer. Sandbox and auto-mode settings apply at launch, so the orchestrated build session can't run it.
- **S2**: W3 + W4.

### Plan (0.4 d)
- `product-manager`: PM decisions and the TW-A2 ruling.
- `architect`: rulings on D-1, D-4, D-6, D-8 and D-9, plus the examples and SARIF calls.
- `team-lead`: evaluates TW-0, TW-B0 and TW-A3.

### W0' spike (0.15 d, any time before T0)
- The maintainer runs `/tachi.threat-model` on the smallest example, in a scratch project.
- `tester` checks that every dispatched tachi agent has its own transcript, carrying the agent type and the served model.

### W0 (0.1 d)
- `devops`: rebase onto `main` after the patch merges, and record the CI and byte-identity pre-state.

### W1 (5 lanes; window ≈ 1.45 d)
- **Lane D, docs (0.35):** `senior-backend-engineer` does A1, FR-13, the links and the manifest line. `product-manager` reviews the D-3 wording.
- **Lane R, runbook (0.80):**
  - `web-researcher` does the research;
  - `devops` authors the runbook;
  - `product-manager` writes the framing and the CVP mapping;
  - `architect` reviews the D-6 profile.
- **Lane E, guard (1.00):** `senior-backend-engineer` does the audit first, then the matrix, the test and SC-A4. `devops` does the wiring.
- **Lane B1, archiver (1.15):** `senior-backend-engineer` builds it against a synthetic fixture. `security-analyst` reviews redaction and refusal.
- **Lane B2, version (0.55):** `senior-backend-engineer` does the marker and the schema changes. `tester` writes the marker tests on F-373's installer harness and the static contract test.
- **Cut line:** Lanes D and E are committed green before W1 closes.
- `architect` holds the P0 checkpoint.

### W2 (0.6 d, serial)
The maintainer, in a scratch project with the branch's tachi installed via `install.sh`:
1. Runs the probe table.
2. Runs the full pipeline with the key, and again without it. The key is injected from the vault into the environment only.
3. Archives each session with the B1 archiver.

### W3 (window ≈ 0.65 d)
- `senior-backend-engineer`: scrub the recorded fixture and run its tests.
- `security-analyst`: leakage review and runbook snippet review.
- `devops`: runbook stamp, the FR-9 record, and SC-A3 red/green evidence.
- `tester`: SC-A2 and SC-B3 records.
- `code-reviewer`: full-diff review.
- `architect`: final checkpoint.

### W4 (0.25 d)
- `product-manager`: release notes, and the deferral record if Part B stopped.
- `devops`: PR title and release check.

**Load check.** In W1 there are four `senior-backend-engineer` instances on disjoint files, at 24%, 69%, 79% and 38% of the window. `devops` is at about 45%. No instance exceeds 80%. Expect about 24–28 tasks, scoped by bucket, not by file.

---

## 6. Trip-wires (the Part B deferral gate, made mechanical)

### At `/aod.tasks`
- **TW-0 (aggregate).** If the projected duration exceeds **5.0 d**, carve in this order:
  1. the FR-11 body-scan;
  2. SARIF `tool.driver.version`;
  3. Part B.
- **TW-B0 (the PRD's gate).** Part B proceeds only if:
  - D-1, D-8 and D-9 are ruled in plan.md;
  - the examples and SARIF calls are recorded;
  - Part B's tasks total **≤ 3.0 effort-days**.

  Otherwise, honest-stop Part B (F-295 precedent).
- **TW-A3.** The FR-11 Bash check must be bounded to fenced shell blocks in the 3 Bash-capable agents, checked against a per-agent allow-list. If it can't be bounded, carve it. SC-A3 still ships.

### Empirical
- **TW-B1, the attribution trip-wire (this one triggers the honest stop).** Decided at the W0' spike and re-confirmed on the W2 sessions. Part B1 stops if either is true:
  - any dispatched tachi agent's turns cannot be attributed to its agent name from the transcript structure;
  - any subagent that ran yields an empty histogram.

  In that case SC-B1 cannot be met as written, so B1 is honest-stopped. The check fails closed: an empty or partial histogram never counts as a pass. Record the observed layout in `delivery.md`. B2 may still ship if green.
- **TW-B2 (cost).** At the start of S2: if Part B has more than **1.5 d** of projected work left, or any B lane is more than **50%** over budget, ship Part A at the cut line and defer Part B.
- **TW-B3 (layout).** If parser rework exceeds **0.5 d**, or the layout changes again mid-build, honest-stop B1.
- **TW-B4 (scrub).** If scrubbing plus leakage review exceeds **0.35 d**, or the review doesn't clear: commit a synthetic structure-only fixture, and verify the recorded run locally only. The PM rules on the wording of AC-B1.1.
- **TW-A1 (live budget).** Cap SC-A1 at **3 debug loops or 1.0 d**. Beyond that:
  - document the limitation;
  - make the key-less path the isolated default (PRD R-1);
  - stamp only what was verified;
  - file a follow-up.
- **TW-A2 (merge gate).** If Part A is ready but #364 hasn't merged, the PM rules: hold as `feat(391)`, or ship Part A alone as `fix(391)` (the false-claim correction is a genuine defect fix).

---

## 7. Concerns (severity-ranked)

**C-1 (HIGH): SC-A1 gates both parts and can't wait for OpenClaw Phase B.**
- **Why Phase B can't serve.**
  - It follows #374, which isn't defined yet.
  - It runs a large architecture, the class #374 exists to fix. That's the worst first test for a new sandbox profile.
- **Why the run needs its own session.** The settings apply at launch. If a key such as `network.strictAllowlist` is honored only at user or managed scope, the maintainer must make a temporary user-settings edit, back it up, and restore it afterwards.
- **Fold-in (§11):**
  - Make SC-A1 a dedicated small-example run in a scratch project (W2).
  - Make Phase B an optional, lagging confirmation.
  - Confirm Auto Mode and the key item before W2.

**C-2 (HIGH): the key-handling patch hasn't shipped, Part A's key text sits on top of it, and the Gemini HTTP client isn't pinned.**
- The README `:164` and Developer Guide key-setup sections are text the patch also changes.
- The skill specifies only the endpoint and headers (`gemini-prompt-construction.md:239-253`). So the agent picks the client at run time. Whether TLS-terminated key masking works depends on that client, which makes the with-key SC-A1 result non-deterministic. It also means the matrix can't list an exact command for that agent.
- **Fold-in:** branch the build after the patch merges, and ask the patch to pin the client. That request is coordination, not 391 scope.

**C-3 (MEDIUM): the merge gate (#364) is unscheduled.**
- The calendar is set by #364, not by 391's effort.
- #374 overlaps B2's files.
- **Fold-in:**
  - State milestones relative to the patch and #364.
  - Adopt TW-A2.
  - Whoever merges second rebases.
  - The rebase tax is already budgeted.

**C-4 (MEDIUM): per-agent attribution is unproven on a tachi run, and the transcript layout is drifting.**
- **Fold-in:**
  - Run the W0' spike before any B1 investment.
  - Fail loudly against a minimal contract (served model plus agent type), not a closed key set.
  - Cover two layout generations.
  - Give `<synthetic>` turns an explicit rule.
  - Record the Claude Code version in the manifest.

**C-5 (MEDIUM): one-source integrity.**
- D-4's write set misses three writes:
  - the conditional overwrite of the installed `templates/tachi/security-report/report-config.typ` (`report-assembler.md:112-115`);
  - `$TMPDIR` (`extract-report-data.py:998`, `:1558`);
  - the `mmdc`/Chromium subprocess (`extract-report-data.py:939-940`, `:1599-1600`).

  SC-A1 won't exercise the conditional path, so only an audit catches it.
- The runbook will be linked from the installed Developer Guide (`INSTALL_MANIFEST.md:19`). But the matrix's home, `CLAUDE_PERMISSIONS.md`, is not installed.
- **Fold-in:**
  - Derive the write set by audit, transitively.
  - Add the runbook to the manifest.
  - The Architect picks the link form, keeping one source.

**C-6 (MEDIUM): placement traps in the guard.**
- **(a) Section placement.**
  - The AC-2 cross-check extracts the block between `## 4.` and `## 5.` of `CLAUDE_PERMISSIONS.md`.
  - The permissions workflow greps the §3 and §4 headings byte-exactly.
  - So append the matrix after §7.
- **(b) Workflow host.**
  - `tachi-install-fidelity.yml` already anchors `.claude/agents/tachi/**` and already installs Python and PyYAML on both triggers.
  - `tachi-permissions-verify.yml` has no Python.
  - Either works; the Architect picks under D-4 and coordinates with #369.
- **(c) Agent selection.** Select agents by `name:`. A glob matches 22 files, because `_TACHI_AGENT_BEST_PRACTICES.md` also has a `tools:` key.
- **(d) Body-scan.** Bound it (TW-A3), or #360's prose will false-red.
- **(e) Push-leg evidence.** The `push:[main]` evidence arrives only at merge.

**C-7 (MEDIUM): SC-B3 and AC-B2.2 can't be met as worded.**
- #365's 6 byte-identity reds already exist.
- The schema bump changes no rendered output.
- **Fold-in:**
  - Reword to "no new byte-identity failures vs. the W0 pre-state".
  - The Architect rules that the examples stay at schema 1.4. FR-19's regeneration then becomes a no-op, and B2 no longer collides with #364.
  - If the examples are bumped anyway, do it frontmatter-only, after #364, and measure the example-snapshot tests first.
  - Editing `docs/architecture/01_system_design/README.md` requires a same-commit regen of `tests/fixtures/init-baseline-tree/`.

**C-8 (LOW): version-source semantics (D-9).**
- FR-18 needs no `release-please-config.json` change.
- Read the release manifest after any `--version` checkout. A template line inside `install.sh` would mis-stamp `--version` installs.
- Decide what an install from untagged `main` reports.
- Manual-block installs report `unknown`.
- Keep SARIF `tool.driver.version` out.

**C-9 (LOW): the SC-A2 sweep only covers the repo.**
- A copy of the "stays on your machine" claim exists in `specs/296-…/notes/cybersec-article-draft.md:131`, and wherever that article was published.
- The maintainer should correct the published copies. This is out of 391's scope; note it in `delivery.md`.

---

## 8. Milestones (proposed for PRD §10)

T0 is the day the key-handling patch merges. Dates assume back-to-back sessions, and the calendar will run longer: F-373 took 13 calendar days for 4 active days.

| Milestone | Central | Floor | Ceiling |
|---|---|---|---|
| Plan complete (triple sign-off; TW-0/B0/A3) | 2026-11-17 | 2026-11-17 | 2026-11-18 |
| Attribution spike (TW-B1 pre-check) | before T0 | before T0 | before T0 |
| Build Session 1 (W0–W1, cut line green) | T0 + 1.6 d | T0 + 1.0 d | T0 + 2.9 d |
| Live validation (W2) | T0 + 2.2 d | T0 + 1.3 d | T0 + 4.6 d |
| Build Session 2 (W3) | T0 + 3.0 d | T0 + 1.5 d | T0 + 6.2 d |
| Deliver | max(T0 + 3.6 d, #364 merged + 0.25 d) | T0 + 1.7 d | T0 + 6.9 d |

---

## 9. Sign-off conditions for tasks.md

- **Assignments.** Every task has an agent from the registry, and no two lanes edit the same file.
- **Cut line.** Lanes D and E are the W1 cut line.
- **Trip-wires.** TW-0, TW-B0..B4 and TW-A1..A3 are written into tasks.md.
- **Attribution spike.** The spike task comes before any B1 attribution code.
- **Live run.** W2 is a maintainer task, run in its own session, in a scratch project, with the key in the environment only.
- **Fold-ins.** C-5, C-6 and C-7 are reflected in plan.md:
  - the write set is audited;
  - the runbook is in the manifest;
  - the matrix sits after §7;
  - SC-B3 is reworded;
  - the examples ruling is recorded.
- **Repo hygiene.** No pytest or extractor runs in the main tree. Stage explicit paths only; never `git add -A`.
- **Size.** About 24–28 tasks, scoped by bucket. No agent instance above 80% of its wave window.
