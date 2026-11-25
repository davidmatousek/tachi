---
type: shared-reference
name: dispatch-record-brief-shared
version: 1.0.0
source_schema: none
consumers:
  - orchestrator
---

# Dispatch Record and Brief — Shared Reference

The orchestrator reads this file before it writes the Phase 1 inventory. It holds the template of each working file that Phases 1 to 3 write: the Phase 1 inventory and dispatch table, one brief before each Phase 2 dispatch, one record when the return arrives or its watch times it out, and the ID map at the end of Phase 3. It also holds the fixed prompt that points an agent at its brief, and the detector that tells a complete return from a truncated one by the end marker that closes it.

---

## Where the Files Live

Every path sits under the run's output directory, written `{out}` below, and is absolute. `{dispatch_id}` is the dispatch's ID.

| File | Path | Written | At most |
|------|------|---------|---------|
| Phase 1 inventory | `{out}/.tachi-build/phase1/inventory.json` | once, before any dispatch | 512 KiB |
| Phase 1 dispatch table | `{out}/.tachi-build/phase1/dispatch.json` | once, before any dispatch | 256 KiB |
| Brief | `{out}/.tachi-build/briefs/{dispatch_id}.json` | once, before its dispatch | 32 KiB |
| Dispatch record | `{out}/.tachi-build/records/{dispatch_id}.json` | once, when the return arrives or the watch times it out | 64 KiB |
| ID map | `{out}/.tachi-build/idmap.json` | once, at the end of Phase 3 | 256 KiB |

The orchestrator writes all five files itself, each in one Write call, and never rewrites one or reads one back. They are working files, not output. The threat agents are read-only: they write no brief and no record.

---

## Tokens

The templates use these tokens. Each pattern is an ASCII full match.

| Token | Meaning |
|-------|---------|
| `DSP` | A dispatch ID: `dsp-` and three or four digits `[0-9]`, such as `dsp-001`. |
| `ID` | A finding ID: one of the prefixes `S`, `T`, `R`, `I`, `D`, `E`, `AG`, `AGP`, `LLM`, `OI`, `MI` or `TE`, a hyphen, and one to six digits `[0-9]`. IDs compare in canonical form, with leading zeros dropped, so `AGP-01` and `AGP-1` are one ID. |
| `NAME` | A component name: 1 to 200 characters, with no control bytes. |
| `PATH` | An absolute path under `{out}` to a regular file that is not a symlink. Read takes absolute paths, so briefs and prompts carry them. |
| `ROSTER` | One of the 14 threat-agent `subagent_type`s in the Phase 2 roster of `.claude/skills/tachi-shared/references/agent-roster-shared.md`. |
| `CAT` | A dispatch key: `S`, `T`, `R`, `I`, `D`, `E`, `AG` or `LLM`. |

Each JSON file is one object with exactly the keys shown. Every key is present, and an absent value is written as `null` or `[]`. A check reads the files with a strict loader: closed key sets, a size cap, and no `NaN`, `Infinity` or duplicate keys. Each file names its `schema` as `tachi.<kind>/<major>`.

---

## Phase 1 Inventory

The components, data flows and trust zones that Phase 1 found, written before Phase 1a or Phase 2 starts. Every other file names a component exactly as this one does, and each brief points its agent here for the DFD type of its targets.

```json
{
  "schema": "tachi.phase1-inventory/1",
  "components": [
    { "name": "Component A", "dfd_type": "Process", "maestro_layer": "L3", "description": "Routes requests to the data store." },
    { "name": "Component B", "dfd_type": "Process", "maestro_layer": "L3", "description": "An agent that serves a second request path." },
    { "name": "Data Store C", "dfd_type": "Data Store", "maestro_layer": "L2", "description": "Holds the records." }
  ],
  "data_flows": [
    { "source": "Component A", "destination": "Data Store C", "data": "Record reads and writes", "protocol": "SQL" }
  ],
  "trust_zones": [
    { "name": "Internal", "components": ["Component A", "Component B", "Data Store C"] }
  ]
}
```

| Key | Value |
|-----|-------|
| `schema` | `"tachi.phase1-inventory/1"` |
| `components` | 1 to 500 objects, each with exactly `name` (a `NAME`), `dfd_type` (`"External Entity"`, `"Process"`, `"Data Store"` or `"Data Flow"`), `maestro_layer` (`"L1"` to `"L7"`, or `"Unclassified"`: the layer's ID, without its name) and `description` (a string of at most 500 characters). No two names match once case is folded and whitespace is collapsed |
| `data_flows` | 0 to 5,000 objects, each with exactly `source` and `destination` (each the `name` of a component), `data` (a string of at most 200 characters) and `protocol` (a string of at most 100 characters) |
| `trust_zones` | 0 to 200 objects, each with exactly `name` (a `NAME`) and `components` (a list of names from `components`) |

---

## Dispatch Table

The categories whose agents analyze each component, written once the self-check in `.claude/skills/tachi-orchestration/references/dispatch-rules.md` passes. The planned dispatches are made from this file and the Phase 2 roster in `.claude/skills/tachi-shared/references/agent-roster-shared.md`, so it holds the categories and nothing else: no agent names, no counts and no notes.

```json
{
  "schema": "tachi.phase1-dispatch/1",
  "rows": [
    { "component": "Component A", "stride": ["S", "T", "R", "I", "D", "E"], "ai": [] },
    { "component": "Component B", "stride": ["S", "T", "R", "I", "D", "E"], "ai": ["AG"] },
    { "component": "Data Store C", "stride": ["T", "I", "D"], "ai": [] }
  ]
}
```

| Key | Value |
|-----|-------|
| `schema` | `"tachi.phase1-dispatch/1"` |
| `rows` | One object for each component in the inventory, in the inventory's order, each with exactly `component` (the inventory's name for it, character for character), `stride` (the STRIDE letters that apply to its DFD type, each at most once, in the order `S`, `T`, `R`, `I`, `D`, `E`) and `ai` (the AI categories that its keywords matched, each at most once, in the order `AG`, `LLM`, or `[]` when none matched) |

---

## Dispatch Record

One record per dispatch, at most 64 KiB. It is a manifest, not a copy of the return: it holds no finding text, scores or mitigations, and no hash, because a model can't compute one.

```json
{
  "schema": "tachi.dispatch-record/1",
  "dispatch_id": "dsp-001",
  "agent_type": "tachi-spoofing",
  "origin": "planned",
  "scope": { "components": ["Component A", "Component B"] },
  "brief": "{out}/.tachi-build/briefs/dsp-001.json",
  "prompt": "Read and follow the brief at {out}/.tachi-build/briefs/dsp-001.json.",
  "end_marker": true,
  "status": "complete",
  "supersedes": null,
  "superseded_by": [],
  "reason": null,
  "count": 2,
  "local_ids": ["S-1", "S-2"]
}
```

| Key | Value |
|-----|-------|
| `schema` | `"tachi.dispatch-record/1"` |
| `dispatch_id` | A `DSP`, equal to the file's name without `.json` |
| `agent_type` | A `ROSTER` name |
| `origin` | `"planned"` (the Phase 2 plan), `"redispatch"` (a replacement for a superseded record) or `"coverage-gap"` (the coverage gate's targeted re-analysis) |
| `scope` | `{"components": [NAME]}`: 1 to 500 unique names, each a component in the Phase 1 inventory. A `"coverage-gap"` record names exactly 1 |
| `brief` | A `PATH`, equal to `{out}/.tachi-build/briefs/{dispatch_id}.json` |
| `prompt` | The fixed prompt below, with `{brief_path}` filled in from `brief`, verbatim |
| `end_marker` | `true` if the return closed with the end marker, otherwise `false` |
| `status` | `"complete"`, `"superseded"` (truncated, and replaced) or `"unrecovered"` (truncated, and not replaced). `"complete"` exactly when `end_marker` is `true`. A `"coverage-gap"` record is never `"superseded"` |
| `supersedes` | The `DSP` this dispatch replaces, or `null`. It is set exactly when `origin` is `"redispatch"` |
| `superseded_by` | A list of `DSP`s, the replacements. It is non-empty exactly when `status` is `"superseded"` |
| `reason` | `"no_end_marker"`, `"overflow_error"`, `"agent_failed"` or `"timed_out"`, or `null`. It is `null` exactly when `status` is `"complete"`. The End Marker section's table sets it |
| `count` | An integer from 0 to 2,000: the findings the return holds. It is 0 when no report came, which is `reason` `"agent_failed"` or `"timed_out"` |
| `local_ids` | A list of `ID` or `null`, one per finding, so its length equals `count`, and `[]` when no report came. These are the agent's own provisional IDs, and `null` marks a finding with no usable ID |

**Truncation.** A return that didn't close with the end marker is truncated, and it gets no `"complete"` record. So is a dispatch that never returned before its wave's watch timed it out. When a retry is left, first allocate the IDs of the replacements. Then write the truncated record once, as `"superseded"`, with its `reason` and `superseded_by`, and let each replacement name it in `supersedes`. With no retry left, write it once as `"unrecovered"`, naming no replacement. Either way its findings leave the completeness set: only a `"complete"` record is live. The orchestrator's Dispatch Protocol holds the retry rules.

---

## Brief

One brief per dispatch, at most 32 KiB. It is the scope file for that dispatch, and it holds only the keys below: the target components, pointers to the agent's inputs, and the baseline focus. It points at its inputs and never copies them.

```json
{
  "schema": "tachi.brief/1",
  "dispatch_id": "dsp-001",
  "agent_type": "tachi-spoofing",
  "targets": ["Component A", "Component B"],
  "inputs": {
    "architecture": "{out}/architecture.md",
    "inventory": "{out}/.tachi-build/phase1/inventory.json",
    "dispatch_table": "{out}/.tachi-build/phase1/dispatch.json"
  },
  "baseline_focus": null
}
```

| Key | Value |
|-----|-------|
| `schema` | `"tachi.brief/1"` |
| `dispatch_id`, `agent_type` | As in the record. The record and its brief share both, and `targets` lists the components the record's `scope.components` names |
| `targets` | 1 to 500 unique `NAME`s |
| `inputs` | Exactly `architecture` (the architecture snapshot that the caller copied into `{out}` as `architecture.md`, a regular file directly in `{out}`), `inventory` and `dispatch_table` (the two Phase 1 files above), each a `PATH`. The three are the same in every brief of a run |
| `baseline_focus` | `null` when the run is stateless. In a baseline run, a list of `{"component": NAME, "covered": [CAT]}`: each target component with the categories the baseline already covers. It carries no finding text, scores, mitigations or finding IDs, so discovery stays isolated |

The agent reads its brief, then the files `inputs` names, and analyzes the `targets` and nothing else. A replacement's brief targets only its own scope, and its `baseline_focus` keeps only the entries of those components.

---

## ID Map

What became of each finding that a dispatch returned, written once at the end of Phase 3 and never read back. It is the audit copy: Phase 3 compiles from the returns already in the orchestrator's context.

```json
{
  "schema": "tachi.idmap/1",
  "records": {
    "dsp-001": ["S-1", "=S-2"],
    "dsp-002": ["~T-3", ">T-4"]
  }
}
```

| Key | Value |
|-----|-------|
| `schema` | `"tachi.idmap/1"` |
| `records` | One key for each `"complete"` record, of any origin, and no other key. Each value is a list of dispositions, one for each finding the return held, in the order the return listed them, so its length equals the record's `count` |

A disposition is one of these:

| Disposition | Meaning |
|-------------|---------|
| an `ID`, such as `S-7` | kept, as the final `S-7` |
| `=` and an `ID`, such as `=S-2` | matched exactly to carried `S-2` in Phase 3a |
| `~` and an `ID`, such as `~S-2` | matched by similarity to carried `S-2` in Phase 3a |
| `>` and an `ID`, such as `>T-4` | merged into the surviving `T-4` |

A kept ID is the one the finding has in the tables, and so in `threats.md`. When it differs from the ID the agent gave the finding, the entry records the renumbering. That includes today's folds, where Phase 3 gives an `OI-`, `MI-` or `TE-` finding an `LLM-` or `AG-` ID. Carried-forward findings, `AGP-` findings and the findings of a `"superseded"` or `"unrecovered"` record have no entry. No kept ID appears twice.

---

## Fixed Prompt

Each agent is dispatched with this one line, and nothing else:

```
Read and follow the brief at {brief_path}.
```

`{brief_path}` is the brief's absolute path. A replacement takes the same line with its own brief's path. The record's `prompt` equals this line with the path filled in, so each dispatch can be audited against it.

---

## End Marker

A complete Phase 2 return closes with an end marker, so the dispatcher can tell a finished return from a cut-off one. This section is the one home of the detector: how the orchestrator reads a return, and what it records for each ending. The agents' text is not here. It is in `finding-format-shared.md`, in the section "Ending Your Report", which every threat agent reads. That text tells an agent to end a report that lists every finding with `TACHI-END`, alone on its last line, and to end one whose findings can't all fit with `TACHI-OVERFLOW`, alone on its last line. No agent spec names either line.

**The detector.** The orchestrator judges each dispatch once, from what reaches its context, and writes the dispatch's record then. On Claude Code 2.1.331 a delivered report reaches it only as a hand-back message, and every other ending only as a notification.

- **The report** is the agent's own delivered text. Any line that the harness adds around it is ignored when present, and when there is none, the whole delivered text is the report. The recorded example is Claude Code 2.1.331's frame: the line that opens the message, the `<agent-message>` tags, the `[Subagent hand-back]` line, the fixed paragraph after the closing tag, and a two-space indent on every report line. So the report is what lies between the `[Subagent hand-back]` line and the closing `</agent-message>` tag.
- **The predicate.** Take the report's last line that isn't blank once leading and trailing whitespace are removed, which also removes the harness's two-space indent. It is the end marker when it is exactly `TACHI-END`, and the overflow line when it is `TACHI-OVERFLOW`, alone or followed by a space. Any other last line is neither.
- **A notification** decides only when no report came. Its `<status>` alone decides nothing, because `completed` also carries the no-report and interim endings: its summary and result text decide. A `completed` notification whose result says that the report was delivered as a message is judged by that message.

**The classes.** `end_marker` is `true` only in the first row. A record without a report has `count` 0 and `local_ids` `[]`.

| What reaches the orchestrator for the dispatch | `end_marker` | `reason` | `count`, `local_ids` |
|---|---|---|---|
| a report whose last line is the end marker | `true` | `null` | the report's findings |
| a report whose last line is the overflow line | `false` | `"overflow_error"` | the report's findings |
| a report whose last line is anything else: the placeholder that an empty hand-back becomes, a cut report, or one that left the marker off | `false` | `"no_end_marker"` | the report's findings |
| no report, and a `failed` notification: an output-cap stop in reasoning or in output (the client has already retried it), an API error or a refusal | `false` | `"agent_failed"` | `0`, `[]` |
| no report, and a final `completed` notification that says no report was delivered: a plain-text or turn-limit ending | `false` | `"no_end_marker"` | `0`, `[]` |
| an interim `completed` notification: the agent "has not reported yet", and the result "may be interim" | not a return: the dispatch stays pending, and its deadline runs on | | |
| nothing before its wave's watch exits 3 | `false` | `"timed_out"` | `0`, `[]` |

- A record with `end_marker` `true` is `complete`. Any other is truncated: `superseded` when a retry is left, `unrecovered` when none is. The orchestrator's Dispatch Protocol holds the lineage rules.
- The marker is not a finding: strip it before compiling, and it never enters `threats.md`. The overflow line carries no object, and nothing reads it past its first word.
- A return or a notice for a dispatch that already has its record changes nothing, and its findings are never compiled, even from an agent that timed out and returns late.
- **Drift.** The detector is stated against Claude Code 2.1.331. A frame or a notice that reads differently on another version can only make a dispatch truncated, or pending until its watch times it out. It can't make a cut report complete, because a cut removes the report's tail, where the marker is. So drift fails the run loudly, and loses no finding quietly.
