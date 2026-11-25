# Contract: dispatch records, briefs, the ID map and chain files (PR 2)

> Normative for F-374. ADR-050 decision D11 to D14, with D6's items O-α for Phase 2's dispatches and O-β for the section manifest, owns this contract; where this file and the ADR disagree, the ADR governs. Pointers are to `b040fa1`.

## Record, brief and chain schemas (PR 2)

The JSON files are read by D3's strict loader. It enforces closed keys, a size cap, and rejects NaN, Infinity and duplicate keys. The tokens used below:
- `ID`: `tachi_parts`' finding pattern, `(S|T|R|I|D|E|AG|AGP|LLM|OI|MI|TE)-[0-9]{1,6}`, an ASCII full match, compared in canonical form (ADR-050 D3).
- `DSP`: `tachi_parts`' dispatch pattern, `dsp-[0-9]{3,4}`, an ASCII full match.
- `NAME`: 1–200 characters, with no control bytes.
- `PATH`: absolute, under `{out}`, a regular file and not a symlink. Read takes absolute paths, so prompts and briefs carry them.
- `ROSTER`: one of the 14 typed threat-agent names.
- `CAT`: one of `S T R I D E AG LLM`.

Versions follow D15: every new JSON file names `schema: "tachi.<kind>/<major>"`. The merged tree manifest keeps its existing `schema_version "1.0"` key.

**Dispatch record**: `records/{DSP}.json`, at most 64 KiB.
```
schema "tachi.dispatch-record/1" | dispatch_id DSP (= file stem) | agent_type ROSTER
origin "planned"|"redispatch"|"coverage-gap" | scope {"components": [NAME] 1-500, unique, in inventory; exactly 1 for "coverage-gap"}
brief PATH = {out}/.tachi-build/briefs/{dispatch_id}.json | prompt = "Read and follow the brief at " + brief + "."
end_marker bool | status "complete"|"superseded"|"unrecovered" (complete <=> end_marker true; "coverage-gap" is never superseded)
supersedes DSP|null (non-null <=> origin "redispatch") | superseded_by [DSP] (non-empty <=> superseded)
reason "no_end_marker"|"overflow_error"|"agent_failed"|"timed_out"|null (null <=> complete; T090, "The detector" below)
count int 0-2000 | local_ids [ID|null], length = count ("agent_failed" or "timed_out" => count 0: no report came)
```
**Brief**: `briefs/{DSP}.json`, at most 32 KiB.
```
schema "tachi.brief/1" | dispatch_id DSP | agent_type ROSTER | targets [NAME] 1-500, unique
inputs {"architecture": PATH, "inventory": PATH, "dispatch_table": PATH}
baseline_focus null | [{"component": NAME, "covered": [CAT]}]
```
**ID map**: `idmap.json`, at most 256 KiB.
```
schema "tachi.idmap/1" | records {DSP: [DISP]}  keys = the complete records; length = count
DISP := ID | "=" ID | "~" ID | ">" ID    (kept | matched exactly | matched by similarity | merged into)
```
**Persisted Phase 1 tables**: `phase1/inventory.json` (at most 512 KiB) and `phase1/dispatch.json` (at most 256 KiB).
```
inventory: schema "tachi.phase1-inventory/1"
  components [{"name": NAME, "dfd_type": "External Entity"|"Process"|"Data Store"|"Data Flow",
               "maestro_layer": "L1".."L7"|"Unclassified", "description": str <= 500}] 1-500,
               names unique after casefold + whitespace collapse
  data_flows [{"source": NAME, "destination": NAME, "data": str <= 200, "protocol": str <= 100}] 0-5000
  trust_zones [{"name": NAME, "components": [NAME]}] 0-200     (every NAME is a component)
dispatch:  schema "tachi.phase1-dispatch/1"
  rows [{"component": NAME, "stride": [S|T|R|I|D|E], "ai": [AG|LLM]}]  one row per component, lists unique
```
**Section manifest** (item O-β): `sections.json`, at most 256 KiB.
```
schema "tachi.sections/1"
frontmatter {"date": DATE, "input_format": "ascii"|"free-text"|"mermaid"|"plantuml"|"c4",
             "classification": TOKEN, "run_id": RUN,
             "baseline": {"source": TEXT|null, "date": TEXT|null, "finding_count": int >= 0|null, "run_id": TEXT|null},
             "coverage_gate": {"status": "pass"|"warn",
                               "gaps": [{"component": TEXT, "missing_category": TOKEN,
                                         "resolution": "findings_produced"|"analyzed_clean"|"dispatch_failure"}]}}
open [ID] at least 1, unique by canonical ID          Section 7's set
resolved [ID] unique, disjoint from open | null       null <=> frontmatter.baseline.source is null
rows {"components", "data_flows", "technologies", "trust_zones", "boundary_crossings", "correlated", "patterns",
      "coverage", "gate_requirements", "gate_gaps", "risk_by_layer", "risk_levels", "lifecycle",
      "baseline_reference": int 0-5000}
DATE := YYYY-MM-DD   RUN := YYYY-MM-DDTHH-MM-SS   TOKEN := [a-z][a-z0-9-]{0,39}
TEXT := 1-1000 characters, with no '"', '\' or control character
```
**The outcome record** in `threats.md`. Exactly one line in the file, outside code fences, matches `^\*\*Attack chain outcome\*\*: ` (ruled at W2′'s entry, S1P-A22).
- **Fences.** They follow the one fence rule of `tachi_parsers.match_heading(outside_fences=True)`, as the ID high-water mark below does (ADR-050 D3, "Finding a section"). So a fenced line is no record, and a fence that nothing closes hides every line after it: the record then reads as absent, and the check rewrites it.
- **One reader.** `tachi_parsers.parse_chain_outcome` reads the record (`module-signatures.md`).
- **The writers.** `render`'s upsert and `check`'s rewrite replace exactly the lines that the reader's `lines` names, all of them, whatever their form, and write the line as `CHAIN_OUTCOME_LABEL` followed by OUTCOME. They find their anchor headings (`## Attack Chain Outcome`, `## 5. Coverage Matrix` and `## Affected Assets`) as exact lines outside fences, through `match_heading(..., outside_fences=True)`. After a write, the reader gives one record, in the form written.
```
## Attack Chain Outcome

**Attack chain outcome**: OUTCOME
OUTCOME := "chains written (" N "); candidates " C "; surfaced " S
         | "0 chains passed filter (" R "); candidates " C
         | "skipped (" R ")"
N := [1-9][0-9]{0,5}   C := [0-9]{1,6}, C >= N   S := [1-5], S <= N   R := [A-Za-z0-9 .,:=-]{1,80}
```
- **Reasons for 0 chains:** `no STRIDE findings`, `fewer than two layers with STRIDE findings`, `no candidate links`, `no chain with a Critical or High finding`.
- **Reasons the script gives for skipped:** `Section 7 unreadable`, `inventory missing`, `inventory invalid`.
- **Reasons the check gives for skipped:** `no outcome recorded`, `outcome record malformed`, `multiple outcome records`, `attack-chains.md missing`, `attack-chains.md unexpected`, `attack-chains.md unreadable`, `full chains X expected Y`, `compact rows X expected Y`, `remainder X expected Y`, `frontmatter counts differ`.

**The ID high-water mark** in `threats.md` (ruling B, ADR-050 D7). Exactly one line, between the frontmatter and the first `## ` heading and outside code fences, matches `^\*\*ID high-water mark\*\*: `. Zero or several read as absent.
```
**ID high-water mark**: `MARKS`
MARKS := ID (", " ID)*     one per prefix in use, in S-2 prefix order
```
Only `tachi-stage.py id-mark` writes it. The reissue check reads the baseline's line, never this run's.

**`attack-chains.md`** (S-3(g)):
```
frontmatter: schema_version (D15) | date (threats.md's) | chain_count N | surfaced_count S | candidate_count C
## 1. Chain Summary    S rows: today's columns + "Converging Chains"
## 2. Chain Details    S sections "### CHAIN-NNN: {title}" with today's keys,
                       "**Surfaced**: Yes" and "**Converging chains**: k"
## 3. Other Consolidated Chains
| Chain ID | Layers | Findings | Max Severity | Chain-Breaking Target |
|---|---|---|---|---|
| CHAIN-007 | L2 → L3 → L7 | T-4 → I-9 → S-2 | High | I-9 |      rows = min(100, N - S), rank order
**Consolidated chains not listed**: K                              last line; K = N - S - rows
```
**Merged tree manifest**: `attack-trees/.manifest.json`. Schema 1.0 is unchanged and its key set is closed.
```
schema_version "1.0" | rule_applied "Rule 1"|"Rule 2"|"no-baseline"|"no-op" (the plan's)
attack_tree_count int = len(trees) = tree files on disk
trees [{"finding_id": ID, "delta_status": "NEW"|"UNCHANGED"|"UPDATED",
        "action": "carried_forward"|"generated_fresh"|"regenerated",
        "similarity_score": number in [0,1] (Rule 3 entries only, otherwise omitted),
        "file_path": "attack-trees/{id-lowercase}-attack-tree.md"}]   Critical first, then High, each in S-2 order
summary {"fresh", "carried_forward", "regenerated"}: ints summing to attack_tree_count
```
A tree batch's part is its manifest: D3's envelope, with one item per finding, `{finding_id, delta_status, action, similarity_score}` (the last under Rule 3 only). `delta_status` equals the batch input's. So does `action`, except for a Rule 3 unit, one whose batch input says `regenerated`: its item says `regenerated` or `carried_forward`, which is the agent's Rule 3 decision, and it alone carries `similarity_score` (erratum S1P-A43; `part-files.md`, "Readings ruled at W2′'s entry, pass 3"). Each tree goes to the path the batch input's `tree_paths` names, and the merge adds `file_path` (ADR-050 D6).

**Chain files** (`chains/`, D13). Their key sets are closed and were ruled at W2′'s entry (S1P-A30). `tachi_parts.KEY_SETS` holds them under the names in brackets, with no optional key. Each file is written with `tachi_parts.atomic_write` and read with the strict loader.
- `chains/chains.json`: `tachi.chains/1` (`chains`). Only `attack-chains.py plan` writes it, on every run of `plan`, unusable inputs included. `render` reads it.
  ```
  schema            "tachi.chains/1"
  outcome           "written" | "zero" | "skipped"   the record's form, in parse_chain_outcome's names
  reason            null for written; for zero, one of the four reasons for 0 chains; for skipped, one of the script's three (the outcome record, above)
  chain_count       N: int >= 1 for written, 0 for zero, null for skipped
  candidate_count   C: int 0-999999, >= N, for written and zero; null for skipped
  surfaced_count    S: int 1-5, <= N, for written; 0 for zero; null for skipped
  reference_digest  64 lowercase hex: the reference set's digest, by the helper that gives the trees and report plans
                    their params.reference_digest; null when Section 7 can't be read
  inventory_digest  64 lowercase hex: the SHA-256 of phase1/inventory.json's bytes; null when the file is missing
  chains            [chain], in rank order: every surfaced chain, and the first min(100, N - S) of the other
                    consolidated chains, so exactly the chains that attack-chains.md lists; [] unless written
  chain (chain):
    chain_id        "CHAIN-" + the rank, at least three digits (tachi_parts' chain pattern); ascending; no repeat
    surfaced        true | false; exactly S chains are true
    converging      for a surfaced chain, the number of other consolidated chains that end at its terminal-impact
                    finding (int >= 0); null for any other
    max_severity    the highest risk level among its members: "Critical" | "High" | "Medium" | "Low" | "Note"
    members         [member], 2 to 7, in chain order
    breaking_target the finding_id of one of its members, by Step 4's rules
  member (chain-member):
    finding_id      as Section 7 spells it: a STRIDE finding of the reference set, passing tachi_parts' finding pattern
    layer           "L1" to "L7": Section 7's cell, else the inventory's; no two members share one
    role            "initial_exploit" for the first, "terminal_impact" for the last, "intermediate_cascade" between
  ```
  - **Derived, with no key of their own.** A chain's layers are its members' layers, in order. Its rank is the number in its ID. Its finding count is the number of its members. The chains that aren't listed are counted only: K = N − S − (the listed chains that aren't surfaced).
  - **What `render` takes from the reference set,** whose digest it has just checked: each member's component and risk level, and the target's mitigation, verbatim. Each member's category comes from its ID's prefix.
  - **`render` refuses** a `chains.json` that fails its key set, its types or these rules: exit 2, or 1 when it can't be read. It also refuses one whose digests differ from its own reads of both inputs (exit 2). For `zero` and `skipped`, it upserts the record from `outcome`, `reason` and the counts, and writes no `attack-chains.md`.
- `chains/narratives.json`: `tachi.chain-narratives/1` (`chain-narratives`), written by the orchestrator after `plan`. Its form is `{"schema": "tachi.chain-narratives/1", "narratives": {CHAIN-ID: {"title": …, "narrative": …}}}`.
  - `narratives` maps each surfaced chain ID, and only those, to an object with exactly the keys `title` and `narrative` (`chain-text`). No other key set's name may match `chain.*narrat`, because T115's harness test reads the declared names.
  - `title` and `narrative` are both narrative-class text (D3), with the slots that D3's table gives chain narratives: `finding`, `ref`, `name` as `component:<ID>`, and `count` as `members`, `layers` or `converging`. No numeral may appear outside a slot. A title is at most 120 characters, and a narrative at most 2,000.
  - A chain whose entry is missing, or whose fields fail, has failed its validation. So does every surfaced chain when the file is missing, or fails its key set or types. A failed chain takes D13's one rewrite, then its fixed text, which `render` builds from its members.
  - `render` refuses unknown IDs, including an ID that isn't a surfaced chain of the current `chains.json`, and stale digests.

## Phase 2 dispatches (item O-α; ADR-050 D6, rev. 3)

Phase 2 has no plan. The orchestrator dispatches by these rules, writing a brief before each dispatch and a record after it, and `check-threat-model.py` enforces them over those files at Step 2.8 (ADR-050 D12). The end-marker predicate, which sets `end_marker` and `reason`, and the watch that bounds a dispatch that never returns were ruled at T090, from S-9's table (T104, `test-results/s9-spike.md`) and the PM's S1P-PM9: "The detector" and "The watch", below.

**The planned set** is a pure function of `phase1/dispatch.json` and the Phase 2 Roster in `agent-roster-shared.md`.
- An agent's scope is every component whose row carries the agent's dispatch key: its STRIDE letter in `stride`, or `AG` or `LLM` in `ai`.
- Each agent with a non-empty scope has exactly one planned dispatch, with that scope (S-1), and an agent with an empty scope has none. So a run plans at most 14 dispatches, in one wave.

**IDs.** The orchestrator allocates them, and the check verifies only that each is a `DSP` and unique.
- The planned dispatches take `dsp-001`, `dsp-002` and so on, in the roster's order.
- Every later dispatch takes the next unused number when the orchestrator decides it, before it writes the brief. A truncated record's replacements take consecutive numbers, in its scope order.
- The pattern stops at `dsp-9999`, so a run that would need more is unrecoverable.

**Lineage.** A planned dispatch starts a lineage, at attempt 1. Each replacement joins its parent's lineage at its parent's attempt plus one, with its parent's `agent_type`.
- **The split.** A truncated attempt-1 record with two or more components is `superseded` by one replacement per component, each scoped to that one component.
- **The repeat.** Any other truncated record of attempt 1 or 2 in a lineage is `superseded` by one replacement with its own scope.
- **The end.** A truncated attempt-3 record is `unrecovered`. Its lineage is exhausted, and the run fails (FR-N4.7; D-3).
- So each planned pair, an agent and one component of its planned scope, gets at most three attempts, and a planned dispatch of k components costs at most 2k retry dispatches. ADR-050 D6's stage budget counts these pairs, 2 × the planned pairs, so it never binds before a lineage's own cap and has no check of its own.

**Coverage-gap dispatches** (Phase 3b's targeted re-analysis, `coverage-requirements.md` Step 5) belong to no lineage. Each is one dispatch per gap and agent, scoped to the gap's one component. The gate retries nothing, so a truncated one is `unrecovered`: its findings are dropped, and its gap resolves `dispatch_failure`.

**The detector** (T090, S1P-A31 and S1P-A32; ADR-050 D6, item O-α). The orchestrator judges each dispatch once, from what reaches its context, and writes the dispatch's record then. On Claude Code 2.1.331 a delivered report reaches it only as a hand-back message, and every other ending only as a notification (S-9 §4).
- **The report** is the agent's own delivered text. Any line that the harness adds around it is ignored when present, and when there is none, the whole delivered text is the report. The recorded example is Claude Code 2.1.331's frame: the line that opens the message, the `<agent-message>` tags, the `[Subagent hand-back]` line, the fixed paragraph after the closing tag, and a two-space indent on every report line (amended at S1P-A39). So the report is what lies between the `[Subagent hand-back]` line and the closing `</agent-message>` tag.
- **The predicate.** Take the report's last line that isn't blank once leading and trailing whitespace are removed, which also removes the harness's two-space indent. It is the end marker when it is exactly `TACHI-END`, and the overflow line when it is `TACHI-OVERFLOW`, alone or followed by a space.
- **A notification** decides only when no report came. Its `<status>` alone decides nothing, because `completed` also carries the no-report and interim endings: its summary and result text decide. A `completed` notification whose result says the report was delivered as a message is judged by that message.

| What reaches the orchestrator for the dispatch | `end_marker` | `reason` | `count`, `local_ids` |
|---|---|---|---|
| a report whose last line is the end marker | `true` | `null` | the report's findings |
| a report whose last line is the overflow line | `false` | `"overflow_error"` | the report's findings |
| a report whose last line is anything else, such as the placeholder an empty hand-back becomes | `false` | `"no_end_marker"` | the report's findings |
| no report, and a `failed` notification: an output-cap stop, an API error or a refusal | `false` | `"agent_failed"` | `0`, `[]` |
| no report, and a final `completed` notification that says no report was delivered | `false` | `"no_end_marker"` | `0`, `[]` |
| an interim `completed` notification: the agent "has not reported yet" | not a return: the dispatch stays pending, and its deadline runs on | | |
| nothing before its wave's watch exits 3 | `false` | `"timed_out"` | `0`, `[]` |

- A record with `end_marker` `true` is `complete`. Any other is truncated: `superseded` or `unrecovered`, by the lineage rules above.
- The marker isn't a finding. It is stripped before compiling and never enters `threats.md`. The overflow line carries no object, and nothing reads it past its first word.
- The agents' text for the two lines is in `finding-format-shared.md`, which every threat agent reads, and this table is in `dispatch-record-brief-shared.md`'s End Marker section. ADR-050 D6 holds the words of both.
- **Drift fails loudly** (S1P-A39). Every path to `complete` runs through a report whose last line is exactly the marker. So a frame or a notification whose wording changes can only make a dispatch truncated, or pending until its watch times it out. It can never make a cut report complete. The one silent case, a delivery that drops a long report's middle lines, is checked at T130. The predicate's home names the recorded version, 2.1.331, beside the frame example, and `test_contract_text_374.py` pins it (ADR-050 D6).

**The watch** (T090, S1P-A33 to S1P-A35; the PM's S1P-PM9; ADR-050 D6, "A dispatch that never returns"). It bounds a dispatch that never returns, so that a blocked tool call in a Phase 2 agent can't hang the run.
```
python3 scripts/tachi-stage.py watch --out <out> DSP [DSP ...]
```
- **Arguments.** `--out` is the run's output directory, checked as the other subcommands check it, except that a directory that isn't there is exit 2 too: the watch has no exit 1. Then 1 to 16 `DSP`s, each a full match of the dispatch pattern, with no repeat. Anything else exits 2, in D4's form, before anything waits (`cli.md`, "Readings ruled at T162"; S1P-A70).
- **What it does.** It writes nothing. Every 5 seconds it checks whether each named dispatch's `{out}/.tachi-build/records/{DSP}.json` is a regular file and not a symlink, by D3's path guard under `--out`: a link in the place of `records/` or `.tachi-build/` counts for nothing too, and `--out` itself may be a link. It never opens the file (S1P-A71).
- **Exit 0,** as soon as every named dispatch has one. Stdout is one JSON object, `{"status": "done", "pending": []}`, printed with sorted keys, as every subcommand prints.
- **Exit 3,** when the deadline passes first, measured on a monotonic clock from the end of the argument checks. Its last sleep ends at the deadline, and it looks once more then, so a record that lands during that sleep still counts. Stdout is `{"status": "timed-out", "pending": [DSP]}`, with the IDs that have no record, in argument order.
- **The deadline** is `WATCH_SECONDS`, 5,400 s (90 minutes), a constant in `tachi-stage.py` and not an adopter setting. Tests set a smaller one only through the function interface. Its floor is the longest working child measured live, 1,356 s, and W5′ confirms or re-amends it (ADR-050 D6).
- **The orchestrator** starts one with each Phase 2 wave's Agent calls, through the Bash tool's background option, naming exactly that wave's dispatches. This holds for planned, re-dispatch and coverage-gap waves alike, and not for Phase 5's tree and report waves.
  - On exit 3, each listed dispatch that still has no record gets one with `reason` `"timed_out"`, by the table above, and the lineage rules take over. A listed dispatch that has its record by then is skipped.
  - Exit 0 needs nothing. Any other exit fails the run (ADR-050 D4).
- **A late result.** An agent that timed out may still return, because nothing within NG8 stops it. A return or a notice for a dispatch that already has its record changes nothing, and its findings are never compiled. After its reply, the orchestrator makes no tool call, even if a late message resumes it.

**The order of writes,** under ADR-050 D6's completion rule, read with the watch:
1. The brief, at `briefs/{dispatch_id}.json`, then the dispatch, with the fixed prompt and the dispatch ID as the Agent call's `description`, so that every notification names its dispatch. A replacement's brief targets its own scope, and its `baseline_focus` keeps only those components' entries. With the wave's Agent calls, the orchestrator starts the wave's watch.
2. The record, once, when the detector judges the dispatch or the watch times it out, and never rewritten. A `superseded` record is written after its replacements' IDs are allocated, so `superseded_by` names them.
3. The replacements, in the next wave, once every dispatch of the wave has its record. At most 16 are in flight, counting each agent that timed out until its late notice arrives. When those agents leave no room for a pending dispatch, the run fails as in step 4, and the error names the oldest record that timed out.
4. After an `unrecovered` record in a lineage, no further brief or dispatch. The orchestrator waits for its agents in flight, which the wave's watch bounds, records them, and returns ADR-050 D4's error, naming that record, its agent, its components and its reason. The command then runs `fail` with `unrecoverable-batch`, and the check doesn't run.

A dispatch that timed out counts as returned: it holds neither its wave, nor step 4's wait, nor the orchestrator's reply. The orchestrator never sends its final report while a dispatch is pending, and `/tachi.threat-model` goes on at that report without waiting for the orchestrator's completion notice, which an agent that timed out can hold (ADR-050 D6).

**Live records.** Only a `complete` record is live: its findings form the completeness set, and the ID map's keys are exactly the complete records. A `superseded` or `unrecovered` record's findings leave the set.

**The check over the records** (Step 2.8). It builds every path from `--run-dir` and pattern-checked IDs, and compares each stored path with the one it built, never opening a path read from a file. Each brief's `inputs` name the two Phase 1 files at their built paths, and every brief names the same architecture snapshot, a regular file directly in `{out}`. Besides D12's checks, it exits 4 when:
1. a `.json` file in `records/` or `briefs/` has a stem that isn't a `DSP`, or a record and its brief don't come as a pair;
2. the planned records aren't exactly the planned set: one per agent with a non-empty scope, with that scope as a set;
3. supersession disagrees in either direction, a replacement set is neither its parent's split nor its repeat, or a lineage passes three attempts;
4. a planned pair isn't in exactly one `complete` record of its lineage, or a lineage ends `unrecovered`.

An `unrecovered` coverage-gap record is a warning, `coverage-gap:unrecovered:<reason>`, with exit 5.

**The stage record.** Phase 2 writes none of its own. When the check runs, its hand-off (`part-files.md` §6, `checks/provenance.json`) carries Phase 2's counts, and `close` or `fail` folds them into the run-level `threat-model` stage record's `batches`, with PR 1's meanings:
- `planned`: the planned records;
- `retried`: the replacement records, so a split of k counts k, as a halving counts 2;
- `dispatched`: `planned` plus `retried`;
- `done`, `split` and `exhausted`: the lineages' `complete`, `superseded` and `unrecovered` records.

Coverage-gap records stay out of `batches`. The records keep each event's detail: which record was truncated, why, and what replaced it (US-1b #6).

## The section manifest (item O-β; ADR-050 D6, rev. 3)

The orchestrator writes `{out}/.tachi-build/sections.json` once, in one Write, after Phase 4 and before any `threats-md` part. It is the planner's only source of the parts' units, because the compiled findings live only in the orchestrator's context (C-7). `part-files.md`, "Stage payload: `threats-md`", holds the parts it plans.

- **What it holds:**
  - the frontmatter's values, which the joiner writes;
  - `open`, the open finding IDs, which is Section 7's set;
  - `resolved`, Section 4c's IDs, or null when the run has no baseline;
  - the row count of each of the 14 tables that aren't keyed by finding.
- **What the planner derives.** Each category table's IDs are the open IDs with its prefixes: `S`, `T`, `R`, `I`, `D` and `E` for 3.1–3.6; `AG`, `AGP` and `TE` for 4.1; `LLM`, `OI` and `MI` for 4.2. Section 7 holds every open ID, and Section 4c every RESOLVED one. So "one Section 7 row per ID" and Section 4c's set hold by construction.
- **No empty run.** `open` holds at least one ID, because every later reader of the reference set refuses an empty one (KB 22).
- **Spelling.** IDs compare in canonical form (ADR-050 D3), so two spellings of one ID, within a list or across the two lists, are a duplicate. The joiner writes each ID as the manifest spells it.
- **Strings** (W2′ entry erratum S1P-A18; ADR-050 D3's P0-4). No string among the frontmatter's values holds a `"`, a `\` or a character that `tachi_parts.forbidden_character` returns, because the joiner writes each one double-quoted and takes it from an input that isn't a part.
- **Refusal.** `tachi-stage.py plan --stage threats-md` strict-loads the manifest from its fixed path, and exits 2 when any rule above fails. The orchestrator then stops with ADR-050 D4's error, and the command runs `fail`.
- **One version.** The plan records the manifest's digest in `inputs`. The joiner reads the manifest at the same fixed path, and exits 2 unless its digest matches.
- **Size.** At fixture scale the manifest is about 7 KB. It stays within S-1's single-write budget up to about 1,400 open findings, at two-space indentation.
