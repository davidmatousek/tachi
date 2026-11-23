---
type: shared-reference
name: dispatch-record-brief-shared
version: 1.0.0
status: staged
source_schema: none
consumers: []
---

# Dispatch Record and Brief — Shared Reference

> **Staged: nothing loads this file yet.** No agent and no command reads it today. It holds the templates for a Phase 2 dispatch record and brief, and the end marker's text, so they can be read and reviewed before the orchestrator starts to use them. The end marker's text is **provisional**. It is confirmed once the overflow spike has planted the four failure classes (a stop mid-reasoning, a stop mid-output, a stall and an empty return) and recorded what a dispatcher sees for each, and the detector is built against that table.

The orchestrator writes one brief before each Phase 2 dispatch and one record when the return arrives. This file defines both, the fixed prompt that points an agent at its brief, and the end marker that closes a complete return. The ID map and the persisted Phase 1 tables join this file when it is finalized.

---

## Where the Files Live

Every path sits under the run's output directory, written `{out}` below. `{dispatch_id}` is the dispatch's ID.

| File | Path | Written |
|------|------|---------|
| Phase 1 inventory | `{out}/.tachi-build/phase1/inventory.json` | once, before any dispatch |
| Phase 1 dispatch table | `{out}/.tachi-build/phase1/dispatch.json` | once, before any dispatch |
| Brief | `{out}/.tachi-build/briefs/{dispatch_id}.json` | once, before its dispatch |
| Dispatch record | `{out}/.tachi-build/records/{dispatch_id}.json` | once, when the return arrives |

The orchestrator writes all four files itself. The threat agents are read-only: they write no brief and no record.

---

## Tokens

The templates use these tokens. Each pattern is an ASCII full match.

| Token | Meaning |
|-------|---------|
| `DSP` | A dispatch ID: `dsp-` and three or four digits `[0-9]`, such as `dsp-001`. |
| `ID` | A finding ID: one of the prefixes `S`, `T`, `R`, `I`, `D`, `E`, `AG`, `AGP`, `LLM`, `OI`, `MI` or `TE`, a hyphen, and one to six digits `[0-9]`. |
| `NAME` | A component name: 1 to 200 characters, with no control bytes. |
| `PATH` | An absolute path under `{out}` to a regular file that is not a symlink. Read takes absolute paths, so briefs and prompts carry them. |
| `ROSTER` | One of the 14 threat-agent `subagent_type`s in the Phase 2 roster of `.claude/skills/tachi-shared/references/agent-roster-shared.md`. |
| `CAT` | A dispatch key: `S`, `T`, `R`, `I`, `D`, `E`, `AG` or `LLM`. |

Each JSON file is one object with exactly the keys shown. Every key is present, and an absent value is written as `null` or `[]`. A check reads the files with a strict loader: closed key sets, a size cap, and no `NaN`, `Infinity` or duplicate keys. Each file names its `schema` as `tachi.<kind>/<major>`.

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
| `origin` | `"planned"` (the Phase 2 plan), `"redispatch"` (a per-component retry of a superseded record) or `"coverage-gap"` (the coverage gate's targeted re-analysis) |
| `scope` | `{"components": [NAME]}`: 1 to 500 unique names, each a component in the Phase 1 inventory |
| `brief` | A `PATH`, equal to `{out}/.tachi-build/briefs/{dispatch_id}.json` |
| `prompt` | The fixed prompt below, with `{brief_path}` filled in from `brief`, verbatim |
| `end_marker` | `true` if the return closed with the end marker, otherwise `false` |
| `status` | `"complete"` or `"superseded"`. `"complete"` requires `end_marker` to be `true` |
| `supersedes` | The `DSP` this dispatch replaces, or `null`. It is set exactly when `origin` is `"redispatch"` |
| `superseded_by` | A list of `DSP`s, the replacements. It is non-empty exactly when `status` is `"superseded"` |
| `reason` | `"no_end_marker"` or `"overflow_error"`, or `null`. It is set exactly when `status` is `"superseded"` |
| `count` | An integer from 0 to 2,000: the findings the return holds |
| `local_ids` | A list of `ID` or `null`, one per finding, so its length equals `count`. These are the agent's own provisional IDs, and `null` marks a finding with no usable ID |

**Truncation.** When a return is flagged, first allocate the IDs of the per-component re-dispatches. Then write the truncated record once, as `"superseded"`, with its `reason` and `superseded_by`. Each replacement names it in `supersedes`. The superseded record's findings leave the completeness set.

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
    "architecture": "{out}/<architecture snapshot file>",
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
| `inputs` | Exactly `architecture` (the architecture snapshot), `inventory` and `dispatch_table` (the two Phase 1 files above), each a `PATH` |
| `baseline_focus` | `null` when the run is stateless. In a baseline run, a list of `{"component": NAME, "covered": [CAT]}`: each target component with the categories the baseline already covers. It carries no finding text, scores, mitigations or finding IDs, so discovery stays isolated |

The agent reads its brief, then the files `inputs` names, and analyzes the `targets` and nothing else.

---

## Fixed Prompt

Each agent is dispatched with this one line, and nothing else:

```
Read and follow the brief at {brief_path}.
```

`{brief_path}` is the brief's absolute path. The record's `prompt` equals this line with the path filled in, so each dispatch can be audited against it.

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

| Last line | `end_marker` | Record |
|-----------|--------------|--------|
| exactly `TACHI-END` | `true` | `status` `"complete"` |
| starts with `TACHI-OVERFLOW ` | `false` | `"superseded"`, `reason` `"overflow_error"` |
| anything else, or no return at all | `false` | `"superseded"`, `reason` `"no_end_marker"` |

The marker is not a finding: strip it before compiling, and it never enters `threats.md`. An overflow line is advisory. A missing end marker triggers the same per-component retry, so no decision depends on the overflow object.
