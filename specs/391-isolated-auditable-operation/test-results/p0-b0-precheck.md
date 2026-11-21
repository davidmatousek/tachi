# P0-B0 pre-check: the Part B contracts before any B code

**STATUS: APPROVED_WITH_CONCERNS.** All four checks pass, so P0-B0 passes. B1 and B2 may commit code on the part-b branch, applying rulings P0B0-1 to P0B0-11 below. Part A is unaffected.

| Item | Value |
|---|---|
| Gate | P0-B0 (`agent-assignments.md:297`; R-6 at `:61`) |
| Reviewer | `architect` |
| Date | 2026-11-19 |
| Read at | Part A tip `3387a39`. During the review the tip moved to `5d528cc`. Its two new commits (`0ee101b`, `5d528cc`) add only test-results records (`field-list.md`, the census, and lines appended after `w0-prestate.md:129`), so every anchor cited here holds at `5d528cc`. Part-b tip `97db2e6`, an empty commit that opens the branch with no files. The part-b worktree had no changes, so no B code was committed before this gate. |
| Method | Read-only review. No tests, extractors or scripts were run. |
| Precedence | Where a ruling below differs from the text of `contracts/run-manifest.md`, `contracts/cli-contracts.md`, `contracts/version-marker.md` or `data-model.md`, the ruling governs B1 and B2. T040 checks that each ruling was applied and folds it into the contract text. |

## The four checks

| # | Check | Result |
|---|---|---|
| 1 | T002 = PASS, and T002 applied the AD-6 / RC-P1 dispatch definitions at every depth | **PASS** |
| 2 | T039 places Step 2.6 between the Step 2.5 re-assert and Step 3, and leaves `orchestrator.md` untouched; the cited lines hold at HEAD | **PASS**, with one concern (P0B0-9) |
| 3 | T037 includes the re-install case | **PASS**, with one concern (P0B0-10) |
| 4 | T032 follows `run-manifest.md`, `cli-contracts.md` and `data-model.md` | **PASS**. The contracts have gaps, which P0B0-1 to P0B0-6 and P0B0-11 close |

### Check 1: T002

- **Verdict.** `w0-spike.md:3` records that TW-B1 passes. Checks (a) to (g) are at `w0-spike.md:28–34`, and `tasks.md:63` marks T002 done.
- **The definitions were applied at every depth.** RC-P1 (`.aod/results/architect-plan-391.md:49–54`, carried into `plan.md:175` AD-6, `plan.md:231`, `run-manifest.md:33` and `tasks.md:232`) defines a dispatch as an `Agent` (legacy `Task`) `tool_use` that names a tachi agent, in any transcript, main or subagent. The spike searched every transcript:
  - check (f) matched each dispatched `subagent_type` to the meta's `agentType` through `toolUseId` at depths 1, 2 and 3 (`w0-spike.md:33`);
  - it found `Agent` blocks inside subagent transcripts at depth 1 (the orchestrator) and depth 2 (`tachi-threat-report`), each with a matching meta (`w0-spike.md:36`). That is the look inside subagent transcripts that RC-P1 asked for.
- **All four states are listed** (`w0-spike.md:38–50`): 9 tachi agents recorded, none dispatch-failed, none no-transcript, 12 not dispatched. 9 + 12 = 21, the installed roster: `.claude/agents/tachi/` holds 21 agent files besides `_TACHI_AGENT_BEST_PRACTICES.md`. The 12 metas are the 9 tachi instances plus 3 `general-purpose` instances.
- **The record has every item T002 requires**: the Claude Code version (`:15`), the tachi version (`:12`), and the entry types and keys (`:52–58`).
- **T001's input precondition held.** Phase 5 reaches depth 3 only with a Critical or High finding, and the input's sample `threats.md` has 2 Critical and 5 High (`examples/ascii-web-api/threats.md:185–186`).
- **One gap, not a fail.** The record gives no count of legacy `Task`-named blocks. The run used a single Claude Code version, 2.1.328 (`:15`), and every one of its 12 metas matched an `Agent` dispatch one to one (`:28`, `:33`, `:36`). The only case a name-specific search could miss is a `Task` dispatch that left no meta. P0B0-4(i) asks for the count of both names.

### Check 2: T039 and Step 2.6

- **T039's text** (`tasks.md:160`) places Step 2.6 "between the Step 2.5 populator re-assert (:150–194) and Step 3 (:195)" and leaves "`orchestrator.md` untouched". The same rule appears at `tasks.md:52`, `agent-assignments.md:148`, `plan.md:176` (AD-7) and `cli-contracts.md:27`.
- **Lines at HEAD `3387a39`** in `.claude/commands/tachi.threat-model.md`:
  - `## Step 2.5: Re-assert Affected Assets Block (idempotent safety net)` is at `:150`;
  - Step 2.5 ends at `:193`, the last line of its sequencing note, and `:194` is blank;
  - `## Step 3: Report Results` is at `:195`.

  The part-b tip `97db2e6` has the same lines, and the working tree had no change to this file at review time. T003's anchor check found no drift here (`w0-prestate.md:88`). The cited `:150–194` and `:195` hold.
- **`orchestrator.md` can stay untouched**:
  - it mentions neither `tachi_version` nor Step 2.6;
  - its only `schema_version` literal (`.claude/agents/tachi/orchestrator.md:491`) belongs to `attack-chains.md`;
  - no tachi agent body hard-codes the `threats.md` schema version, so T038a's 1.5 bump reaches the orchestrator through the template and the skill reference;
  - the populator rewrites only its own block (`scripts/populate-affected-assets.py:321`). The Step 2.5 re-assert and `/tachi.risk-score` Step 1.5 (`.claude/commands/tachi.risk-score.md:93`), the only later writer of `threats.md`, therefore keep a stamped key.
- **Concern.** T024 edits `:67` of the same file on Part A, and BX carries that edit to part-b, so line numbers may move. P0B0-9 anchors Step 2.6 on headings instead.

### Check 3: T037

- **The case is in the task.** `tasks.md:157` includes "a marker-writing install followed by a marker-skipping install reads `unknown`". So do `version-marker.md:7` ("tested"), `plan.md:242`, and RC-P2's test item (`.aod/results/architect-plan-391.md:61`).
- **The mechanism holds.** The placeholder is tracked (`version-marker.md:3`). The manual loop copies each directory with `cp -R "$TACHI/$p." "$p"` (`README.md:149`; `docs/guides/DEVELOPER_GUIDE_TACHI.md:123` and `:1027`). That copy overwrites a marker that an earlier install wrote.
- **Concern.** The test can pass vacuously, and it breaks once T048 adds the marker line to the README loop. P0B0-10 covers both.

### Check 4: T032

I compared T032 (`tasks.md:142`) item by item against `cli-contracts.md:14–20`, `run-manifest.md:1–33` and `data-model.md:14–37`. Every item matches:

- discovery by `cwd`, with `CLAUDE_CONFIG_DIR` honoured;
- the roster read from the installed agent files, where a missing matrix never exits 2;
- the destination default and `--dest`;
- the refusal matrix;
- modes 0700/0600 and `O_EXCL`;
- a verbatim, hash-equal copy that follows no symlinks;
- the dispatch rules at any depth;
- the `<synthetic>` exemption;
- tolerance of unknown entry types and keys;
- `Z` timestamps parsed on 3.9;
- the v1 fields;
- `denial_detection` failing closed;
- artifacts hashed when `--output-dir` is given;
- the final secret scan;
- chunked hashing and `--json`;
- the whitelist line in the same commit.

T032 adds nothing outside the contracts and drops nothing they require. The gaps are in the contracts themselves:

- non-tachi subagents;
- dispatch-state precedence;
- the turn unit;
- where "counted" goes;
- the re-archive no-op;
- the source of the manifest's `tachi_version`;
- the secret-scan floor.

The rulings below close them. `plan.md:175` still calls the roster "the matrix roster", but the contracts and T032 use the `name:` values of the installed agent files (`cli-contracts.md:20`, `data-model.md:27`), and the contracts govern (O-2).

## Rulings

### P0B0-1: non-tachi subagent instances (MEDIUM; B1: T031, T032.2, T033; T051)

At depth 3, `tachi-threat-report` dispatched three built-in `general-purpose` subagents, which ran Bash and Write (`w0-spike.md:46`, `:63`). The contracts define dispatches only for tachi agents, and `data-model.md:24` already allows `pinned_model` to be `null`.

1. **Listed.** `subagents[]` has one entry for every subagent instance in the archive, whatever its `agentType`: each `subagents/*.meta.json` together with its transcript.
2. **Which names count as tachi agents.** An agent type is a tachi agent when its name starts with `tachi-`. `pinned_model` comes only from the installed roster (`.claude/agents/tachi/*.md`). Every other type, built-in or project-defined, gets `null`, and so does a `tachi-` name that the roster lacks.
3. **Attributed by the same rules.** The per-instance parse contract (`run-manifest.md:33`) applies to every instance:
   - the meta has `agentType` and `toolUseId`;
   - every assistant line has `message.model`;
   - every line that carries `attributionAgent` equals the meta's `agentType` (`<synthetic>` lines are exempt), and at least one non-synthetic line carries it;
   - the transcript has at least one assistant turn, and the histogram is not empty.

   If a non-tachi instance fails the contract, the run fails (exit 1, no manifest), as it would for a tachi instance. `parent_tool_use_id` (the meta's `toolUseId`) and `spawn_depth` (P0B0-4(c)) give its parent.
4. **Not dispatches.** An `Agent` or `Task` `tool_use` that names a non-tachi type is not a dispatch (RC-P1). It never appears in `dispatches[]`, `tachi_agents_not_recorded` or `tachi_agents_not_dispatched`. The parser still indexes every `Agent` and `Task` `tool_use`, whatever it names, to build the topology (P0B0-2).
5. **Counted in the session-level fields.** Every instance's transcript feeds:
   - `transcripts[]` and its hashes;
   - `claude_code_versions`;
   - the three egress fields;
   - `permission_modes_seen` and `denial_detection`;
   - the final secret scan.

   A non-tachi instance's tool calls stay in its own `tool_calls_by_tool`. The dispatching agent's `tool_calls_by_tool` counts its `Agent` calls.
6. **TW-B1 (T051, and any re-run of T002).** A non-tachi instance counts toward two conditions: "any subagent that ran yields an empty histogram" and "meta and line agent names disagree". Denials in its transcript count toward "a planted denial kind is detected". It does not count toward attributing a dispatched tachi agent, or toward `no-transcript`: neither is defined for non-tachi types. T002 already applied checks (a) to (e) to the three `general-purpose` instances (12 of 12, `w0-spike.md:28–32`), so its PASS stands.

**Test (T031, T033).** The gen2 fixture gains one `general-purpose` instance at depth 3, dispatched by `tachi-threat-report`, with one Bash call and one Write call (placeholders only). Assert that:
- it is in `subagents[]` with `pinned_model: null`;
- it is absent from all three dispatch lists;
- its Bash host is counted in `egress_observed`.

Negative case: give one of its lines a different `attributionAgent`. The run must exit 1 with no manifest.

**For T048.** The runbook's §7 D-1 sentence and ADR-049's B1 section say that the manifest lists every subagent instance, tachi or not, and that a non-tachi instance has `pinned_model: null`.

### P0B0-2: dispatch states, precedence and fail-closed cases (MEDIUM; B1: T032.2, T033)

For each `Agent` or `Task` `tool_use` X that names a `tachi-` type:

| Case | State |
|---|---|
| (a) A meta has `toolUseId` = X and the same `agentType`, and its transcript has at least one assistant turn | `recorded`, whatever the `tool_result` says |
| (b) As (a), but the transcript has zero assistant turns and the `tool_result` is an error | `dispatch-failed`. The instance gets no `subagents[]` entry; its files are still archived and hashed. The same applies to a non-tachi instance |
| (c) A meta has `toolUseId` = X but a different `agentType` | Exit 1, no manifest. This is a name disagreement (TW-B1's third condition), never "not recorded" |
| (d) No meta, and the `tool_result` is an error | `dispatch-failed` |
| (e) No meta, and the `tool_result` succeeded | `not-recorded`, reason `no-transcript` |
| (f) No meta, and no `tool_result` anywhere in the archive (an interrupted or live session) | `not-recorded`, reason `no-transcript`. An unknown outcome is never filed as the kind of failure that does not trip TW-B1 |
| (g) A meta, tachi or not, whose `toolUseId` matches no `Agent` or `Task` `tool_use` in any archived transcript | Exit 1, no manifest. The topology cannot be established |

- **Zero turns with any other `tool_result`.** An instance with zero assistant turns stays a failure under the existing "at least one assistant turn" rule in every case except (b).
- **Status and reason.** `dispatches[].status: not-recorded` corresponds to `tachi_agents_not_recorded[].reason: no-transcript`, and `dispatch-failed` is the same word in both lists. `tachi_agents_not_recorded` holds both kinds (`run-manifest.md:23`, `:33`).

**Test.** One fixture case each for (b), (c), (f) and (g).

### P0B0-3: `requestedModel`, the meta's `model` and `parentAgentId` are not in manifest v1 (LOW; B1: T032.2; T048)

**Ruling.** Manifest v1 keeps what AD-1 decided (`plan.md:170`): `pinned_model` from the agent file, beside `served_model_histogram` from `message.model`. It records none of the following:
- the line key `requestedModel`;
- the meta keys `model` and `parentAgentId`;
- `toolUseResult.resolvedModel`;
- `attachment.identity.modelId`.

**Why the gap is not material for v1:**
- **The histogram already shows what served.** It records which model served every turn. So any unexpected model is visible, whether an environment override, a client fallback or a server-side switch caused it. `requestedModel` would explain the cause, not reveal the fact.
- **`requestedModel` is new.** Sessions one to three weeks older than the newest lack it (`.aod/results/team-lead-391.md:160`, E-11). A v1 field built on it would be absent on older layouts and would need its own fail-closed rule, which adds TW-B3 risk on a near-critical lane.
- **The archive keeps it.** The transcripts are archived verbatim, so a requested-versus-served check stays possible after the fact.
- **The pin is an alias.** Comparing pinned with served is a reading, not an equality check, because alias resolution depends on the Claude Code version. The stopped attempt on 2.1.258 resolved `sonnet` to `claude-sonnet-5`; the measured run on 2.1.328 resolved it to `claude-sonnet-5-5` (`w0-spike.md:17`, `:22`).

**Constraints:**
- (a) `pinned_model` is the alias string exactly as the agent file writes it. The archiver never resolves aliases and never compares pinned with served.
- (b) Dispatch parsing stays mandatory, and `parentAgentId` may not replace it. A topology built from metas alone cannot see a successful dispatch that left no meta, which is the one class that trips TW-B1.
- (c) T048's D-1 sentence and ADR-049's B1 section say that the pin is an alias that Claude Code resolves, and that the histogram records the served model ids. They never say that the manifest shows the pin was honoured.
- (d) Follow-up for `delivery.md` (T045): a manifest v2 with `requested_model_histogram` and a count of turns where the requested and served models differ. SBE-B1 may leave an `AOD-SIMPLIFICATION` marker that names this upgrade path (`.claude/rules/code-economy.md` §3).

### P0B0-4: parser clarifications, the contracts against the observed layout (MEDIUM; B1: T031, T032.2, T033)

- **(a) Where `attributionAgent` sits.** It is a top-level key of assistant lines (`w0-spike.md:31`, `:56`), and both layout generations carry it (`.aod/results/architect-plan-391.md:146`). The fixtures put it there.
- **(b) The known set for `unknown_meta_keys`.** It is the twelve meta keys observed at 2.1.328 (`w0-spike.md:57`). Only `agentType` and `toolUseId` are required.
  - At 2.1.328, the normal value is then `[]`, as in the contract's example.
  - A non-empty list signals layout drift: E-11 recorded sidecar key sets changing between versions.
  - The archiver lists key names, never values (`description` holds free text).
- **(c) `spawn_depth` comes from the dispatch chain.** The main session is depth 0, and an instance's depth is its dispatcher's depth plus 1.
  - A `not-recorded` dispatch has no meta to read a depth from, so the chain is the only source that covers every case.
  - The meta's `spawnDepth` is neither required nor cross-checked in v1. T002 found every value consistent (`w0-spike.md:33`).
- **(d) A turn is one model response.**
  - **Grouping.** Group a transcript's non-synthetic assistant lines by `message.id`. A line without one is its own turn, and each `<synthetic>` line is one synthetic turn.
  - **Counting.** `turns`, `synthetic_turns` and the histogram count turns, so in every object `turns` equals the histogram's total plus `synthetic_turns`.
  - **Failure.** A group whose lines disagree on `message.model` makes the run exit 1.
  - **Tool calls.** `tool_calls_by_tool` counts distinct `tool_use` ids by name.
  - **Why.** A transcript can carry one response across several lines that share a `message.id`, and the spike counted lines, not responses (`w0-spike.md:30`). If every line is its own response, grouping changes nothing, so the rule holds on either layout.
  - **Contract fix.** The contract example's `main` object breaks the invariant: a histogram of 41 plus 1 synthetic turn, but `turns` 41 (`run-manifest.md:13`). When T040 folds the rulings, it should read `turns: 42`.
- **(e) Where "counted" goes.** `run-manifest.md:33` says unknown entry types and keys are "counted", but manifest v1 has no field for those counts. They go in the `--json` summary and the stderr summary: a count by entry type, and a count of the top-level keys on assistant lines. Nothing is added to `run-manifest.json` v1.
- **(f) Where permission modes come from.** `permission_modes_seen` is read from the main transcript's `permission-mode` entries (`w0-spike.md:54`). If there are none, it is `[]`, and the `--json` summary says so.
- **(g) Fail closed instead of writing an empty listing.** The archiver exits 2 when the project's `.claude/agents/tachi/` has no `name: tachi-*`, or when no main transcript's `cwd` matches the project. It never writes a manifest whose `tachi_agents_not_dispatched` is silently empty.
- **(h) Discovery compares real paths on both sides**: the transcript's `cwd` and `--project-dir`. A project reached through a symlinked directory, such as the macOS temp directories, then still matches its W2 session.
- **(i) A recommended addendum, before T032.2 but not blocking.** `tester` appends to `w0-spike.md`, structure-only, from the same private copy:
  - the key that carries the mode in `permission-mode` entries;
  - for each transcript, the number of assistant lines against the number of distinct `message.id` values;
  - the number of `Task`-named `tool_use` blocks;
  - the number of `tool_result` blocks with `is_error`.

  Without the addendum, (d) and (f) still hold, and T051 records the same facts on the W2 archives.

### P0B0-5: a re-archive is a no-op only when the manifest is present (MEDIUM; B1: T032.1, T032.3, T033)

**The defect.** Read literally, the contracts let a failed archive pass on its second run:
- `cli-contracts.md:20` makes a non-empty destination an exit-0 no-op when its transcript hashes match;
- `data-model.md:37` puts `copied` before `parsed`, and a `failed` run leaves no manifest;
- so a run that copied the files and then hit a parse failure or a secret-scan hit leaves hash-identical transcripts and no manifest;
- the next run exits 0 as a no-op. The operator never gets a manifest, and the fail-closed result is lost on the second try.

A hand-made private copy laid out like an archive does the same.

**Rule.** A destination counts as a finished archive only when it holds `run-manifest.json`.

| Destination | Result |
|---|---|
| Every source transcript is hash-equal to its archived copy, and `run-manifest.json` is present | Exit 0, no-op |
| The transcripts are hash-equal, but `run-manifest.json` is absent | Exit 1, with the reason "incomplete archive: run-manifest.json absent; use a new --dest". The archiver writes nothing into it and never exits 0 without a manifest |
| Any hash mismatch | Exit 1 (unchanged) |

**Test.** Both new cases join T033's refusal matrix.

### P0B0-6: the source of the manifest's `tachi_version` (LOW; B1: T032.3; contract text)

**The conflict.** `data-model.md:18` makes the manifest's `tachi_version` the marker value, but `version-marker.md:9` names `stamp-tachi-version.py` as the marker's only reader.

**Rule.**
- The archiver also reads the marker, at `templates/tachi/VERSION` under `--project-dir`, with the stamp's parse rule: one line, `tachi_version: <value>`.
- An absent or malformed marker reads `unknown`.
- The archiver reads the value from no other file.

**Consequences.**
- If B2 is deferred, every manifest reads `unknown`, and T048's text must not claim otherwise.
- The value describes the install at archive time. The runbook already says to archive right after the session.
- When T040 folds the rulings, `version-marker.md:9` reads "Readers: `stamp-tachi-version.py` and `archive-run-transcripts.py`; agents never read it".

### P0B0-7: `INSTALL_MANIFEST.md` changes in the whitelist commits (MEDIUM; B1: T032, T033; B2: T039; R-4)

**Confirmed.** `INSTALL_MANIFEST.md:15` and `:64` say "4 Python files" (also noted at `w0-prestate.md:118`). T032 and T039 must each update the following in the same commit as their whitelist line:
- **The whitelist line** in the BEGIN/END MANIFEST block, next to `:127–130`.
- **A row in the Script Files table** (`:62–71`). The archiver's row names the operator, who runs it after a session. The stamp's row names `/tachi.threat-model` Step 2.6.
- **The counts at `:64` and `:15`.** Set each to the number of Script Files rows after the edit, so R-4's order does not matter. The first commit writes 5 and the second writes 6. If B1 stops before T032 lands, T039 writes 5. Also extend the Purpose and Required By cells at `:15` so they stay true.
- **T039 only:** the failure sentence at `:75` also names the stamp script. Per P0B0-9, Step 2.6 reports a missing script.

T033's commit adds `run-manifest.yaml` to the Schema Files list (`:79–90`), together with the schema file. That makes T033 a third part-b writer of this file, serialised under R-4.

**What CI catches, and what it misses.** No test reads the prose counts: `test_install_manifest_completeness.py` checks only the floors (at least 4) and whitelist coverage.
- CI does force T039's whitelist line. Step 2.6 puts `scripts/stamp-tachi-version.py` into a distributed command file, and `test_referenced_scripts_covered` (`:364–368`) scans those files.
- CI does not force T032's line. Only the runbook and `schemas/` name the archiver, and the scan reads neither.

So T040 reviews the counts and T032's line by hand.

**Reverts.** The same-commit rule also keeps an honest-stop revert clean. If B1 stops after T032 lands, reverting T032's and T033's commits with `git revert` (never a rebase) removes, in one go:
- the script;
- its whitelist line;
- its row;
- the count change;
- the schema-list item.

The honest-stop dispositions (`agent-assignments.md:190–196`) do not say whether B1 commits that have already landed are reverted. The orchestrator decides that at T051.

### P0B0-8: a stdlib-only check for the Part B scripts (MEDIUM; B1: T033; B2: T039)

**The gap.** Nothing checks that the archiver and the stamp import only the standard library:
- S-13 (`test_distributable_imports_stdlib_only`, `test_install_manifest_completeness.py:385`) walks a hard-coded `REQUIRED_SCRIPT_NAMES` of four scripts (`:79–84`);
- only T028 may edit that module (`tasks.md:52`). T028 is on Part A, and Part A may not name Part B scripts (AD-14; T046 step 3 searches for the names);
- the 3.9 CI step catches APIs that need 3.11, but not a PyYAML import, because CI installs PyYAML.

**Rule.**
- `test_archive_run_transcripts.py` (T033) and `test_threats_schema_contract.py` (T039) each assert that their script's module-level imports are all in `sys.stdlib_module_names`.
- Each check skips below 3.10 and uses the same AST walk as S-13.
- **Follow-up.** After Part B reaches `main`, add both names to `REQUIRED_SCRIPT_NAMES`, so that one list covers every installed script.

### P0B0-9: Step 2.6 anchoring and failure handling (LOW; B2: T039)

- **(a) Anchor on headings, not line numbers.** Insert `## Step 2.6: …` after the end of Step 2.5, which is its sequencing note (now `:185–193`), and directly before `## Step 3: Report Results` (now `:195`).
- **(b) The body.** A `bash`-labelled block that holds exactly T039's command: `python3 scripts/stamp-tachi-version.py --threats {output_dir}/threats.md`. Add `--schema-version-from-template` only if T038a's CF-21 measurement shows zero churn.
- **(c) A failure is reported, and the run continues.** On a non-zero exit (a missing script, no frontmatter, or an I/O error), the command:
  - reports "tachi_version not stamped (exit N)" in Step 3's output;
  - keeps the outputs and does not retry;
  - never writes or edits `tachi_version` by hand (`cli-contracts.md:27`: the model never writes the field).

  An absent field is the documented legacy case (`plan.md:44`, Constitution III).
- **(d) `orchestrator.md` gets no step** (see Check 2).

**Test.** T039's "Step 2.6 present" assertion finds the step by its heading and checks that it sits between the Step 2.5 and Step 3 headings.

### P0B0-10: T037's re-install case (LOW; B2: T037)

- **(a) Build the marker-skipping install without relying on the README loop's text.** Once T048 adds the marker line, the README loop as written becomes a marker-writing install, and the case would fail or test the wrong path. Use either of these:
  - the loop's copy step for `templates/tachi/`, which copies `<src>/templates/tachi/.` over the target (`README.md:149`);
  - the loop extracted from the README with the marker line removed.
- **(b) Assert the precondition first.** After the marker-writing install, the marker must read a describe value, not `unknown`. Only then run the skipping install and assert `unknown`.
- **(c) When it lands.** The case belongs to T037's W1 set. Only the manual-loop write case waits for T048 (`tasks.md:157`).

### P0B0-11: a floor for the secret scan (MEDIUM; routed to T034; B1: T032.3, T033)

**The problem.** `data-model.md:34` scans the manifest for the values of environment variables named `*KEY*`, `*TOKEN*`, `*SECRET*`, `*PASSWORD*` or `*CREDENTIAL*`, and fails the run on a hit. With no floor, a short value in a matching variable collides with counts, mode names or model ids, and the archiver refuses a clean session. Examples are `1`, `true`, `auto` or a short word.

**Recommended floor**, which `security-analyst` confirms or changes in T034 (the architect defers to `security-analyst` on security policy):
- skip values shorter than 8 characters, and boolean or numeric literals;
- keep matching known key formats by pattern, at any length;
- the stderr reason names the variable, never its value.

**Test.**
- A short value that appears in manifest strings does not fail the run.
- A long dummy value does fail it. Key-shaped dummies are assembled at runtime (ADR-042).

## Observations (no ruling)

- **O-1.** The record has no count of legacy `Task`-named blocks (Check 1). P0B0-4(i) covers it.
- **O-2.** `plan.md:175` (AD-6) still says "the matrix roster". The contracts and T032 use the `name:` values of the installed agent files, and the contracts govern. ADR-049's B1 text (T048) should use the contract wording.
- **O-3.** `plan.md:114` still lists "end-to-end install accepts VERSION" under the T028 module. v1.2's T028 (`tasks.md:128`) no longer includes it, and T037 owns the placeholder assertion. That split is correct under AD-14: no Part A file may name `templates/tachi/VERSION`.
- **O-4.** Two spike findings are Part A inputs, for T004's audit, §8 (T023) and T040; P0-B0 does not rule on them:
  - observation 2 (`w0-spike.md:63`): `Agent` reaches any tool through built-in subagents;
  - the one `general-purpose` Write. Where it landed matters for the write-confinement claim (SC-005), and T020's write listing should show it.
- **O-5.** `w0-spike.md:20` has one Pattern B hit, a technical use (the byte-identity check of the private copy). Record it as such if T041's sweep reaches `test-results/`. Pattern A has zero hits in that file.
- **O-6.** T001's text describes the input as about 1.7 KB, but it is 2,560 bytes (`w0-spike.md:13`). This has no effect.
- **O-7.** The spike ran stock v4.48.1. v4.48.2 (the key-handling patch) does not touch dispatch, so the topology stands. T051 re-confirms it on the 391 build.

## Cost

These rulings add fixture and test cases worth about 0.05–0.08 d to B1 (T031, T033) and about 0.01 d to B2 (T037, T039):
- B1's re-cost moves from 1.38 d to about 1.45 d, still under TW-B2's B1 line of 1.55 d;
- SBE-B1 logs the actual at T032.1, as an input to the TW-B3 watch;
- these cases are designed in now, so they do not count as parser rework under TW-B3.
