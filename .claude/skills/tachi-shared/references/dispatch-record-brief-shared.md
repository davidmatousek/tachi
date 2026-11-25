---
type: shared-reference
name: dispatch-record-brief-shared
version: 1.0.0
source_schema: none
consumers:
  - orchestrator
---

# Dispatch Record and Brief — Shared Reference

> **Only the end marker is provisional.** Its text, its rule and the `reason` it sets for a truncated return are confirmed once the overflow spike has planted the four failure classes (a stop mid-reasoning, a stop mid-output, a stall and an empty return) and recorded what a dispatcher sees for each, and the detector is built against that table. Every other template here is final.

The orchestrator reads this file before it writes the Phase 1 inventory. It holds the template of each working file that Phases 1 to 3 write: the Phase 1 inventory and dispatch table, one brief before each Phase 2 dispatch, one record when the return arrives, and the ID map at the end of Phase 3. It also holds the fixed prompt that points an agent at its brief, and the end marker that closes a complete return.

---

## Where the Files Live

Every path sits under the run's output directory, written `{out}` below, and is absolute. `{dispatch_id}` is the dispatch's ID.

| File | Path | Written | At most |
|------|------|---------|---------|
| Phase 1 inventory | `{out}/.tachi-build/phase1/inventory.json` | once, before any dispatch | 512 KiB |
| Phase 1 dispatch table | `{out}/.tachi-build/phase1/dispatch.json` | once, before any dispatch | 256 KiB |
| Brief | `{out}/.tachi-build/briefs/{dispatch_id}.json` | once, before its dispatch | 32 KiB |
| Dispatch record | `{out}/.tachi-build/records/{dispatch_id}.json` | once, when the return arrives | 64 KiB |
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
| `reason` | `"no_end_marker"` or `"overflow_error"`, or `null`. It is `null` exactly when `status` is `"complete"` |
| `count` | An integer from 0 to 2,000: the findings the return holds |
| `local_ids` | A list of `ID` or `null`, one per finding, so its length equals `count`. These are the agent's own provisional IDs, and `null` marks a finding with no usable ID |

**Truncation.** A return that didn't close with the end marker is truncated, and it gets no `"complete"` record. When a retry is left, first allocate the IDs of the replacements. Then write the truncated record once, as `"superseded"`, with its `reason` and `superseded_by`, and let each replacement name it in `supersedes`. With no retry left, write it once as `"unrecovered"`, naming no replacement. Either way its findings leave the completeness set: only a `"complete"` record is live. The orchestrator's Dispatch Protocol holds the retry rules.

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

## End Marker (provisional)

A complete Phase 2 return closes with an end marker, so a dispatcher can tell a finished return from a cut-off one. The threat agents already read `finding-format-shared.md`, so the marker's text moves there once the detector is built, and no agent file changes.

**Text for the agents** (provisional):

> When you have listed every finding, end your reply with this line, alone and exactly as written, and write nothing after it:
>
> `TACHI-END`
>
> If your findings can't fit in one reply, don't stop mid-list. End instead with one line that starts `TACHI-OVERFLOW ` and carries a single `tachi.overflow/1` JSON object.

**Rule for the dispatcher** (provisional). Take the last non-blank line of the return, with trailing whitespace trimmed:

| Last line | `end_marker` | `reason` |
|-----------|--------------|----------|
| exactly `TACHI-END` | `true` | `null` |
| starts with `TACHI-OVERFLOW ` | `false` | `"overflow_error"` |
| anything else, or no return at all | `false` | `"no_end_marker"` |

A return with `end_marker` `true` gets a `"complete"` record. Any other return is truncated, and its record is `"superseded"` when a retry is left and `"unrecovered"` when none is.

The marker is not a finding: strip it before compiling, and it never enters `threats.md`. An overflow line is advisory. A missing end marker triggers the same retry, so no decision depends on the overflow object.
