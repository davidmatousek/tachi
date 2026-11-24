# Contract: part files, batch plans and stage records

> Normative for F-374. ADR-050 decision D3 (envelope), D6 (plan, overflow, stage record, item O-β for the `threats-md` payload, item O-γ for the `report` payload, and RR3 for PR 2's stage records and the check hand-off) and D2 (payloads) owns this contract; where this file and the ADR disagree, the ADR governs. Pointers are to `b040fa1`.

## Envelope, plan and record schemas

Every key is required, and an absent value is written as `null` or `[]`. IDs pass `tachi_parts`' allow-lists (ADR-050 D3), each an ASCII full match, and compare in canonical form:

- plan: `[0-9]{8}T[0-9]{6}Z-[0-9a-f]{12}`;
- batch: `B[0-9]{3}(-[12]){0,2}`;
- finding: `(S|T|R|I|D|E|AG|AGP|LLM|OI|MI|TE)-[0-9]{1,6}`.

Scripts recompute every path from `--out` and these IDs, never from a path stored in a file, except the plan's digest-checked `inputs` (ADR-050 D3).

**§1 Part, `tachi.part/1`** (agent-written; untrusted)

| Key | Type and range |
|---|---|
| `schema` | `"tachi.part/1"` |
| `plan_id`, `batch_id` | the current plan's; the planned batch's |
| `stage` | `risk-score` \| `compensating-controls` (PR 1); `trees` \| `report` \| `threats-md` (PR 2; `threats-md`'s payload is item O-β, ruled at ADR-050 rev. 3: "Stage payload: `threats-md`", below). Phase 2 has no stage here: it writes records, not parts, and has no plan (item O-α, ruled at ADR-050 rev. 3, D6; `threat-model-records.md`, "Phase 2 dispatches") |
| `agent_type` | the stage's agent: `tachi-risk-scorer`, `tachi-control-analyzer`, `tachi-attack-tree-delta`, `tachi-threat-report` or `tachi-orchestrator` |
| `finding_ids` | 1–500 unique IDs, equal to the planned set; `[]` only in a `report` section part or a `threats-md` row-section part (item O-β) |
| `items` | an array of objects, one per ID, each `{finding_id, …the stage's closed payload}`. In a `threats-md` row-section part, one per planned row, in order, with no `finding_id` (item O-β). A `report` section part carries none (`[]`) (item O-γ) |
| `fragments` | an array of 0–50 `{slot_key, text}`. PR 1's stages, `threats-md` and a `report` findings part carry none (`[]`). In a `report` section part, `slot_key` is one of that section's closed keys, and `text` is narrative prose, cut at that key's limit, which is at most 4,000 characters (ADR-050 D3, step 9; item O-γ: "Stage payload: `report`", below) |

**§2 Overflow error, `tachi.overflow/1`** (advisory). Six keys:
- `schema`, `plan_id`, `batch_id`, `stage` and `agent_type`, as in §1;
- `reason`: `output-budget` \| `input-too-large` \| `other`.

`schema` selects this key set before any other check, so a well-formed overflow object is classified `overflow`, never `invalid` (ADR-050 D3).

**§3 Batch input, `tachi.batch-input/1`** (written by the planner, read by the agent)

| Key | Type |
|---|---|
| `schema`, `plan_id`, `batch_id`, `stage`, `agent_type`, `finding_ids` | as in §1 |
| `attempt` | an integer, 1–3 |
| `part_path` | an absolute path under `<plan_id>/parts/` |
| `tree_paths` | in `trees`, `{finding_id: absolute path under <plan_id>/trees/}`, one per ID; `{}` elsewhere |
| `units` | the batch's unit rows, as verbatim data. In `compensating-controls`, an UNCHANGED unit's row also holds its baseline's persisted narrative text and its evidence-class values (`evidence[]`, `matrix_row`, `recommendation_body`), all decoded, for the agent to copy. So a carried string is escaped once per render (ADR-050 D2, RR1). In `threats-md`, each unit is `{section, finding_id}` or `{section, row}` (item O-β). In `report`, a section part's unit is `{section, key, …}` and a findings part's is `{section, finding_id, …}` (item O-γ) |
| `refs` | an object mapping the stage's closed pointer names (architecture, threats, baseline files, target) to absolute paths that the command validated |
| `params` | an object of the stage's closed parameters, for example `scoring_date` as `YYYY-MM-DD` |

**§4 Batch plan, `tachi.plan/1`** (written only by `tachi-stage.py`, and replaced atomically)

| Key | Type |
|---|---|
| `schema`, `plan_id`, `stage`, `agent_type` | as in §1, and `stage` may also be `threat-model`, the run-level plan (PR 2). No plan has the stage `phase2`, which item O-α leaves out (ADR-050 D6, rev. 3) |
| `created_utc` | ISO 8601, ending in `Z` |
| `tachi_version` | `X.Y.Z` |
| `inputs` | `{logical name: {path, sha256, bytes}}` |
| `params` | as in §3 |
| `batch_size` | an integer, 1–500, or `null` for a plan with no units (the run-level `threat-model` plan) and for a stage whose sizes are per section, `threats-md` and `report`, whose sizes are `tachi-stage.py` constants (items O-β and O-γ) |
| `unit_count` | an integer, 0 or more |
| `preimage` | `{canonical name: sha256 \| null}`. `plan` copies each existing file to `<plan_id>/preimage/<canonical name>`, and `fail` restores a copy whose digest matches (ADR-050 D4) |
| `out_snapshot` | `{relpath: [size, mtime_ns]}`, at most 20,000 entries, or `null` |
| `retry_budget` | `{limit, used}`, both integers. `limit` is 2 × the planned batch count, and `used` counts retry dispatches, so a halving counts 2 |
| `batches` | an array of `{batch_id, parent: id \| null, attempt: 1–3, finding_ids, input_sha256, state: pending \| done \| failed \| split}`. Input and part paths are recomputed from the IDs, never stored. In `threats-md`, a row section's batches have `finding_ids` `[]`, and their batch inputs' `units` name the rows (item O-β). In `report`, a section's batches have `finding_ids` `[]`, and their batch inputs' `units` name the fragment keys (item O-γ) |

- **The digest.** `plan` and `reconcile` print `plan_digest`, the SHA-256 of this file. `reconcile`, the renderers, `fail` and `close` take it back as `--plan-digest` and exit 2 on a mismatch, or on a batch input whose digest differs from `input_sha256`.
- **The pointer,** `tachi.plan-pointer/1`, has two keys: `{schema, plan_id}`. `--plan` overrides it, and a disagreement between the two exits 2.

**§5 Stage record, `tachi.stage-record/1`** (NFR-5). Its shape is fixed, so #399 can ingest it.

| Key | Type |
|---|---|
| `schema`, `stage`, `plan_id` | as in §4, `threat-model` included |
| `status` | `success` \| `success-with-warnings` \| `failed` |
| `tachi_version` | `X.Y.Z` |
| `started_utc`, `finished_utc` | ISO 8601 |
| `input_digest` | `sha256:<hex>` |
| `counts` | non-negative integers, under the stage's closed keys: `units`, `open`, `resolved`, `rendered`, `parse_errors`, `narrative_fallbacks`, `truncations`, plus D2's and D9's flag counts by kind, `retagged` and `reused-id` included |
| `batches` | `{planned, dispatched, done, retried, split, exhausted}` |
| `overflow_events` | `[{batch_id, attempt, kind: missing \| overflow-reported \| unparseable \| invalid}]` |
| `retries` | `[{batch_id, attempt, cause, children}]` |
| `warnings` | `[{code, detail}]` |
| `undeclared_paths` | `[relpath]` |
| `outputs` | `[{path, sha256}]` |
| `error` | `null`, or `{code, message, batch_id, finding_ids, remedy}` |

**PR 2's stage records** (RR3, ruled at ADR-050 rev. 3, D6). The shape above doesn't change. Each PR 2 stage has its own closed `counts` keys, and PR 1's two stages keep theirs. ADR-050 D6's RR3 table names each record's writer.

| Stage | `counts` keys | `batches`, `overflow_events`, `retries` | `undeclared_paths` |
|---|---|---|---|
| `threat-model`, the run | `open`, `resolved`, `recorded`, `carried`, `rule`, `renumbered`, `folded` and `reused-id`, taken from the provenance hand-off (§6) | `batches`: Phase 2's six counts, from the provenance hand-off. The two event lists are `[]`: Phase 2's events stay in its records (item O-α) | `close`'s declared-paths check over the whole run, against Step 1.5's snapshot, with D4's PR 2 grammar |
| `threats-md` | `units`, `open`, `resolved`, and `rendered` (the rows joined) | the plan's, as in PR 1 | `[]`, with no check |
| `trees` | `units` (the trees generated), `carried` (the trees copied from the baseline), and `rendered` (the merged manifest's trees) | the plan's | `[]`, with no check |
| `report` | `units`, `rendered` (the units the file holds), `narrative_fallbacks` and `truncations` | the plan's | `[]`, with no check |

- A batch stage's plan records `out_snapshot` `null`, and its record carries no `declared-paths-skipped` warning, because `close` checks the run.
- A batch stage's `fail` writes its failed record and moves nothing. Only `fail --stage threat-model` moves and restores the four canonical files (ADR-050 D4).
- The `threat-model` record's `outputs` are the four canonical files that are present in `{out}`, with their digests. With no hand-off, `fail` writes its `counts` as `{}` and its `batches` as zeros.
- `STAGE_AGENTS` gains `threat-model` and `threats-md`, both `tachi-orchestrator`, `trees` (`tachi-attack-tree-delta`) and `report` (`tachi-threat-report`).

**§6 Check hand-off, `tachi.check-handoff/1`** (PR 2; Architect re-review RR5; its key set ruled at ADR-050 rev. 3, by T088). One file per main-session check, written by that check at a fixed name under the run-level plan's `threat-model/<plan_id>/checks/`:
- `attack-chains.json`, by `attack-chains.py check` (D13);
- `provenance.json`, by `check-threat-model.py` (D12).

`close` and `fail` read it with the strict loader (closed keys, at most 1 MiB, no NaN, Infinity or duplicate keys) and fold it into the run-level stage record (ADR-050 D4, D15). Every key is required:

| Key | Type and rule |
|---|---|
| `schema` | `"tachi.check-handoff/1"` |
| `check` | `attack-chains` or `provenance`, equal to the file's stem |
| `plan_id` | the run-level plan's ID, equal to its directory's |
| `status` | `fail` when `error` isn't `null`; otherwise `warn` when `warnings` isn't empty; otherwise `pass`. It matches the check's exit code: 4, 5 or 0. `attack-chains` is never `fail` |
| `counts` | `null` in `attack-chains`. In `provenance`, exactly these keys, each an integer 0–1,000,000: `open` and `resolved`, the reference set's counts; `recorded`, `carried` and `rule`, the findings that each of FR-N4.5's three provenance classes accounts for (a dispatch record, a baseline carry-forward and Phase 3.6's rule); `renumbered`, the kept dispositions whose final ID differs from the provisional ID, folds excluded; `folded`, those that #356's fold table re-prefixed; and `reused-id`, FR-E.19's reissued IDs |
| `batches` | `null` in `attack-chains`. In `provenance`, Phase 2's six counts, `{planned, dispatched, done, retried, split, exhausted}`, each an integer 0–1,000,000, with the meanings in `threat-model-records.md`, "Phase 2 dispatches": the lineages' records, with coverage-gap records left out (item O-α) |
| `warnings` | `[{code, detail}]`, at most 1,000, under §5's warning rules. The codes are closed: `chain-outcome:rewritten`, when the check rewrote the record as `skipped (<reason>)`, with the new line and whether `attack-chains.md` was quarantined in the detail (D13); `section6:mismatch`, one per cell, with the cell and both values in the detail (FR-E.10); `id:reissued`, with the first 20 IDs in the detail (FR-E.19); and `coverage-gap:unrecovered:<reason>`, where `<reason>` is `no_end_marker` or `overflow_error`, with the record and its component in the detail (item O-α) |
| `error` | `null` in `attack-chains`. In `provenance`, `null`, or, when the check fails (exit 4), `{code, message, finding_ids, remedy}`: `code` is the failed rule, one of `no-records`, `envelope`, `lineage`, `provenance` and `completeness`; `message` is at most 2,000 characters and states how many IDs are involved; `finding_ids` holds the first 20, in S-2 order; and `remedy` is D12's |

- **Writing.** A check writes its file once, with `tachi_parts`' atomic write, before it exits 0, 4 or 5. A check that exits 2 writes none. The provenance check counts before it applies any rule, so its `counts` and `batches` are complete in every file it writes.
- **`close`, on the success path (Step 2.10).**
  - It strict-loads both files. `provenance.json` is required. Its absence, a file that fails to load, a `plan_id` that differs, or a `fail` status in either file exits 2, so a run whose check failed can't be closed.
  - A missing `attack-chains.json` is the warning `handoff-missing:attack-chains`, never a stop. The chain check's 2 prints and continues (R-24), and writes no file.
  - The run-level record takes its `counts` and `batches` from `provenance.json`. Its `warnings` are `attack-chains.json`'s, then `provenance.json`'s, then `close`'s own: `handoff-missing:attack-chains`, then the declared-paths warnings. Any warning makes the status `success-with-warnings`, and `close` exits 5.
- **`fail` (Step F)** folds whichever hand-off files exist and load, in the same order. It warns about no missing file, because a run can fail before Step 2.8. When `provenance.json`'s status is `fail`, the record's `error.message`, `finding_ids` and `remedy` come from its `error`, and `error.code` is `--reason`, as ruled at W1.
- **The record's cap.** Folded warnings that would pass §5's 1,000 keep the first 999 in the order above, then `warnings-truncated`, whose detail gives the full count, as `undeclared-paths-truncated` does for paths.

## Stage payloads: the scorer and controls items (ADR-050 D2, D9, D10)

Both payloads use closed key sets, and any other key is rejected, renderer-computed ones included. `finding_id` is allow-listed, belongs to the batch's list and is unique in the part. Prose limits are in characters. A field typed prose below that runs over its limit is cut there before escaping, flagged `input:<field>:truncated` and counted; it never rejects the part (ADR-050 D3, step 9). Narrative fields use only the `{{kind:arg}}` slots that ADR-050 D3's table gives their stage, such as `{{score:cvss_base}}`, `{{band:severity}}`, `{{name:component}}` or `{{ref:CWE-89}}`. Outside a slot they hold no digit: names and cited IDs go through `name` and `ref`; versions, ports and other terms with digits are written without the digits; and a count, score, band or percentage stays forbidden in words too. Other number words stay, such as "two-factor" and "third-party". A narrative field that breaks the slot grammar or the numeral ban takes D3's per-field fallback; it never rejects the part.

| Scorer key | Type and range |
|---|---|
| `finding_id` | string |
| `cvss_vector` | string, the pattern at `schemas/risk-scoring.yaml:25` |
| `exploitability` | object with exactly `known_techniques`, `attack_complexity`, `tooling_availability` and `skill_level`, each an integer 0–10 |
| `scalability` | object with exactly `scriptability`, `target_scope`, `resource_requirements` and `detection_difficulty`, each an integer 0–10 |
| `reachability` | object: `zone`, a string of 1–120 or null; `trust_level`, `Untrusted`, `Semi-Trusted` or `Trusted`, null exactly when `zone` is; `auth_barriers` and `network_boundaries`, integers 0–10 |
| `rationale` | object with exactly `cvss`, `exploitability`, `scalability` and `reachability`, each prose of 1–400, cut at 400 |
| `metric_rationale` | optional; keys from `AV AC PR UI S C I A`, prose up to 160, cut at 160 |
| `subscore_rationale` | optional; keys from the eight sub-score names, prose up to 160, cut at 160 |

| Controls key | Type and range |
|---|---|
| `finding_id` | string |
| `control_status` | `found`, `partial` or `missing` |
| `control_category` | one of the eight values at `schemas/compensating-controls.yaml:45-52` |
| `confidence` | `High`, `Medium` or `Low`; null exactly when `missing` |
| `carried_forward` | boolean |
| `evidence` | array of 1–5 entries for found or partial, empty for missing. Each entry has `file` (1–300, relative to the target, passing ADR-050 D7's resolver checks: no scheme, leading `/`, backslash, drive letter or `..`), `line` (integer ≥ 1), `language` (`[a-z0-9+#-]{1,20}`, a `tachi_parts` full match), `snippet` (at most 5 lines and 600), `summary` (prose up to 160, cut at 160) and an optional `assessment` (coverage, configuration, currency and completeness, each a rating of High, Medium or Low with a rationale of prose up to 160, cut at 160) |
| `matrix_row` | one line of up to 1,200, the 11 K8 cells (R-34) |
| `recommendation_body` | up to 2,000, required for partial or missing, null for found (R-34) |

**String classes (ADR-050 D3):**
- **Narrative:** `rationale.*`, `metric_rationale.*`, `subscore_rationale.*` and each `evidence[].assessment.*` rationale.
- **Evidence:** `evidence[].snippet`, `evidence[].summary`, `matrix_row` and `recommendation_body`.
- **Closed values:** every other string, checked against its pattern, enum or input. `reachability.zone` must name a §2 row.
- **Carried text (Architect re-review RR1):** the renderers persist each narrative field's validated, slotted text, escaped on write: in `risk-scores.md` §6's `### Scoring Inputs` and `compensating-controls.md` §7's `### Assessment Inputs`. The scorer renderer carries it, and the controls agent copies it from its batch input (§3). Either way it is decoded first, then re-validated as narrative and re-resolved against this run's values, with the per-field fallback. Only legacy prose, which has no slots, is evidence-class (ADR-050 D9).

**Renderer-computed, never in a part:** every field that D2's tables give to the renderer, plus flags, corrections, control IDs, the row-check results, and §3's prose carried from the baseline: persisted slotted text, re-validated as narrative, or a legacy file's prose, which is evidence-class (ADR-050 D9).

## Readings ruled at W1 (2026-11-22, T023)

Each reading is one the sources left open. `tachi_parts` (T012, T013), `tachi-stage.py` (T018) and the shared reference (T006) follow them.

**Field names and flags.**
- **A flag's `<field>`** is dotted, with no list index. An assessment rationale is named by its dimension. There are 28 names:
  - the 24 narrative fields: `rationale.<key>`, `metric_rationale.<metric>`, `subscore_rationale.<name>` and `evidence.assessment.<dimension>`;
  - the four evidence-class prose fields: `evidence.snippet`, `evidence.summary`, `matrix_row` and `recommendation_body`.

  These serve both `input:<field>:narrative-fallback` (the 24 narrative fields) and `input:<field>:truncated` (all 28). An item's flags are a set, so two truncated evidence summaries give one flag, while `counts.truncations` counts both.
- **The fixed fallback sentences** are keyed by the same 24 names. The wording in the shared reference's "Fixed Fallback Sentences" (T006) is the authority: `tachi_parts` embeds it verbatim (T013), and T010 drift-tests the two.
- **A value's address** is used only where one value must be found again, as in the persisted-inputs table (`module-signatures.md`). It is the field name with each list entry as a numeric segment, ending at the string: `evidence.0.summary`, `evidence.2.assessment.currency.rationale`.
- **The assessment dimension object** has exactly `rating` (`High`, `Medium` or `Low`) and `rationale` (narrative, up to 160), the template's Rating and Rationale columns.

**Validation order.**
- **A `tachi.overflow/1` object is `overflow` only when its `plan_id`, `batch_id`, `stage` and `agent_type` match the planned batch**, step 7's match. Otherwise it is `invalid`. "Well-formed" in ADR-050 D3 includes that match.
- **Step 10 runs on the strings that step 9 kept.** Over-limit prose is cut and flagged at any length, even above 16,384 characters. A forbidden character beyond the cut is cut away with the rest, and one inside the kept text rejects the part.
- **A snippet is cut to 5 lines first, then to 600 characters,** and flagged `input:evidence.snippet:truncated` once.
- **A cut that lands inside a slot token** leaves an unterminated slot, so that field takes the per-field fallback. This is accepted, with no extra rule: the field is flagged both `truncated` and `narrative-fallback`, and the part is never rejected.

**Values.**
- **`evidence[].file` and `line` are closed values.** Each is checked against its pattern and range: the 1–300 range and the relative-path rule for `file`, and an integer of at least 1 for `line`. A closed value is never cut, so a `file` over 300 characters rejects the part.
- **A `file` is checked, never rewritten.** `./a//b.py` is kept as written in the validated part. The resolver canonicalizes it at render time (ADR-050 D7), and both rendered files use that canonical spelling, so `.md` and `.sarif` agree. Like all agent text, it is escaped on output.
- **The validated part carries canonical finding IDs** (ADR-050 D3). `findingId/v1`, and any other place that prints Section 7's spelling, takes it from the reference set.
- **The total order on finding IDs (S-2)** is defined once in code, `tachi_parts`, and once in a shared reference, `part-file-contract-shared.md`'s "Identifiers". Every other file cites one of the two.
- **`atomic_write`** gives the replaced file the mode an ordinary write would, `0666 & ~umask`, never the temporary file's `0600`.

**Slots and escaping** (T013's slice 2).
- **A `finding` slot's argument** must pass `tachi_parts`' finding-ID pattern when the grammar is checked, or the field takes the fallback. It is then canonicalized, and its lookup decides membership: an ID outside the reference set, or outside the chain in a chain narrative, returns `None` and takes the fallback (D3's table; step 8's "before any other use").
- **`keep_slots=True` keeps every complete slot, whatever the stage.** A complete slot is a recognized kind, an argument matching the pattern, and `}}`.
  - The stage is checked earlier. Step 11 has already passed persisted narrative text for its stage, or replaced it with a fixed sentence, which holds no slot.
  - Evidence text, such as `matrix_row`'s score cells, is never resolved, so a token kept in it is never filled.
  - A complete slot's characters can't break a table cell.
- **A `{` just before a slot is escaped as `&#123;`.** With the slot's first brace it makes a `{{` that isn't a slot, which D3's rule covers. This holds when slots are kept and when they are resolved.
  - So `{{{score:x}}` is written `&#123;{{score:x}}`, and it decodes and re-renders to the same bytes on the next run.
  - A resolved value can't join a stray brace into a slot-like `{{` in the output.
- **A slot lookup that returns anything other than text or `None` is a shipped-code defect.** It raises, and the render fails through Step F (D4), never through the per-field fallback. `None` means "doesn't resolve", and it takes the fallback.
  - Where the table says a slot should resolve and the lookup returns `None`, the result is still a fallback in the run.
  - W5 counts each such fallback as a shipped-code defect to fix, under the PM's ruling 2.

**Documents and records** (T012's choices, confirmed).
- **Items in planned order.** A validated part's items come back in the planned order, whatever order the agent wrote, so `input_digest` is byte-stable (D4).
- **The document caps.** The plan is capped at 8 MiB, a batch input at 4 MiB, the pointer at 4 KiB and a stage record at 1 MiB. A writer never writes a document over its own cap.
  - A stage record keeps at most 1,000 `undeclared_paths`, sorted.
  - When there are more, the writer adds the warning `undeclared-paths-truncated`, with the full count, just as the snapshot is skipped above 20,000 entries with a warning.
- **Timestamps** are UTC and end in `Z`, and no other form is accepted. They are parsed without `datetime.fromisoformat`, which reads `Z` only from Python 3.11 (S-11).
- **`preimage`** has exactly one key per canonical output in the stage's closed set (D4), each mapped to a SHA-256 or `null`.
- **`STAGE_AGENTS`** holds only PR 1's two stages, `risk-score` and `compensating-controls`, and PR 1 rejects every other stage. PR 2 adds its stages with the code that handles them.
- **A batch's `parent`** is the batch its ID derives from (`B003-1` → `B003`), and `null` for a planned batch.
- **The stage record's `counts` keys** are the seven base counts plus one per D9 flag kind: `corrected`, `unverifiable`, `unchecked`, `divergent`, `override`, `resolved`, `retagged`, `reused-id` and `input`. `resolved` is both the base count and the flag kind, because the flag marks exactly the RESOLVED rows.
- **The layout path builders** live in `tachi_parts`, as the one copy that `tachi-stage.py` and both renderers call. They build every D3 path only from `--out`, the stage and pattern-checked IDs, and they never take a path read from a file, except the plan's digest-checked `inputs`.

**The batch plan (§4), as T017's tests pin it for T018.**
- **Halving.** A halving's children are `<parent>-1` and `<parent>-2`. They are split contiguously and differ in size by at most 1, and each carries `attempt` = the parent's + 1.
- **Retries.** An `invalid` retry keeps the batch ID and raises `attempt`. Each retry rewrites the batch input with its new `attempt` and `part_path`, and the plan's `input_sha256` follows it. So two retries per lineage fit `attempt` 1–3 and the batch-ID pattern.
- **A one-unit batch can't halve.** When it is `missing`, `overflow` or `unparseable`, it is retried once more with the same member and batch ID, `attempt` + 1, at a cost of 1, as an `invalid` retry is. No batch ever has zero units.
- **The budget.** A retry costs 1 against `retry_budget.used`, and a halving costs 2. A retry is refused when `used + cost > limit`, or when the batch is already at attempt 3, and either way `reconcile` exits 4.

## Stage payload: `threats-md` (item O-β; ADR-050 D6, rev. 3)

The orchestrator writes these parts itself, after Phase 4 and its section manifest (`threat-model-records.md`, "The section manifest"), and `join-threats-md.py` joins them. Every part holds rows of one table, and nothing in a part is markdown.

**The sections** are the template's 24 tables, in this order. `tachi_parts` holds this table as one constant, which the planner and the joiner import. A drift test pins its headings and headers against `templates/tachi/output-schemas/threats.md`. Each header cell is the template's, in item-key order.

| Section key | Heading it sits under | Keyed by | Item keys, in header order | Size (rows per part) |
|---|---|---|---|---|
| `components` | `## 1. System Overview`, then `### Components` | row | `component`, `type`, `maestro_layer`, `description` | 59 |
| `data_flows` | `### Data Flows` | row | `source`, `destination`, `data`, `protocol` | 59 |
| `technologies` | `### Technologies` | row | `category`, `technology`, `version` | 59 |
| `trust_zones` | `## 2. Trust Boundaries`, then `### Trust Zones` | row | `zone`, `trust_level`, `components` | 59 |
| `boundary_crossings` | `### Boundary Crossings` | row | `crossing`, `from_zone`, `to_zone`, `components`, `controls` | 59 |
| `spoofing`, `tampering`, `repudiation`, `information_disclosure`, `denial_of_service`, `elevation_of_privilege` | `## 3. STRIDE Tables`, then `### 3.1 Spoofing (S)` to `### 3.6 Elevation of Privilege (E)` | finding: the prefixes `S`, `T`, `R`, `I`, `D` and `E` | `finding_id`, `status`, `component`, `maestro_layer`, `threat`, `likelihood`, `impact`, `risk_level`, `mitigation` | 16 |
| `agentic` | `## 4. AI Threat Tables`, then `### 4.1 Agentic Threats (AG)` | finding: `AG`, `AGP` and `TE` | as for the STRIDE tables, with `owasp_reference` after `threat` | 16 |
| `llm` | `### 4.2 LLM Threats (LLM)` | finding: `LLM`, `OI` and `MI` | as for `agentic` | 16 |
| `correlated` | `## 4a. Correlated Findings` | row | `group`, `findings`, `component`, `threat_summary`, `risk_level` | 27 |
| `patterns` | `## 4b. Findings by Agentic Pattern`, only when it has rows | row | `pattern`, `count`, `findings` | 59 |
| `resolved` | `## 4c. Resolved Findings`, only when the run has a baseline | finding: the manifest's `resolved` | `finding_id`, `component`, `threat`, `last_risk_level`, `resolution_reason` | 59 |
| `coverage` | `## 5. Coverage Matrix` | row | `component`, `s`, `t`, `r`, `i`, `d`, `e`, `ag`, `llm`, `total` | 59 |
| `gate_requirements` | `## 5a. Coverage Gate Results`, then `### Coverage Requirements Matrix` | row | `component`, `determined_type`, `required_categories`, `evaluated`, `gaps` | 59 |
| `gate_gaps` | `### Gap Resolution Details`, only when it has rows | row | `component`, `missing_category`, `agents_dispatched`, `resolution`, `findings_added` | 59 |
| `risk_by_layer` | `## 6. Risk Summary`, then `#### Risk by MAESTRO Layer` | row | `maestro_layer`, `finding_count`, `highest_severity` | 59 |
| `risk_levels` | the same heading, after the template's sentence | row | `risk_level`, `count`, `percentage` | 59 |
| `actions` | `## 7. Recommended Actions` | finding: every open ID | `finding_id`, `status`, `pattern`, `component`, `maestro_layer`, `threat`, `risk_level`, `mitigation`. The joiner writes `Category` after `Status` | 41 |
| `lifecycle` | `## 8. Delta Summary`, only when the run has a baseline, then `### Finding Lifecycle` | row | `status`, `count`, `description` | 59 |
| `baseline_reference` | `### Baseline Reference` | row | `field`, `value` | 59 |

Where `output-schemas.md` and the template disagree, the template governs, except Section 4b, which takes `output-schemas.md`'s single table. So the category tables have no Agentic Pattern column, Section 7 has the template's nine columns, and Components has its MAESTRO Layer column. T119 aligns both files.

**The envelope (§1) in `threats-md`.**
- `agent_type` is `tachi-orchestrator`, and `fragments` is `[]`.
- **A finding section's part:** `finding_ids` is its batch's planned set, and it has one item per ID, each `{finding_id, …the section's other keys}` (step 8, unchanged).
- **A row section's part:** `finding_ids` is `[]`, and `items` holds exactly the rows its batch input names, in order. Each item has the section's keys and no `finding_id`. Any other count is `invalid`.
- Keys are closed per section, and every value is a string.

**String classes (ADR-050 D3).**
- **Closed values** are checked against their sets and never cut:
  - `finding_id`;
  - in a finding section, where it has them: `status` (`NEW`, `UNCHANGED` or `UPDATED`); `likelihood` and `impact` (`LOW`, `MEDIUM` or `HIGH`); `risk_level` and `last_risk_level` (`Critical`, `High`, `Medium`, `Low` or `Note`); and `maestro_layer` (`L1` to `L7`, optionally followed by ` — ` and a name of at most 60 characters, or `Unclassified`);
  - in `actions`, `pattern`: one of the six pattern values, `multiple`, or `—`.
- **Evidence** is every other value. Its digits stand, it is escaped on output, and the joiner never reads a number from it.
  - No value has a limit below step 10's 16,384 characters, so none is cut.
  - Edge whitespace is removed at intake, by PR 1's W1 reading for every evidence string, and a value that is empty after that rejects the part.
- No `threats-md` value is narrative, so step 11 doesn't run.

**The orchestrator's protocol** (T112):
1. After Phase 4, write `.tachi-build/sections.json` once.
2. Run `tachi-stage.py plan --stage threats-md --out {out} --date {date}`.
3. Write each listed part at its `part_path`, in one Write, one part per response, from the compiled findings. Waves don't apply here, because nothing is dispatched.
4. Run `reconcile` until it exits 0, writing the parts it lists. On 4, stop with ADR-050 D4's error.
5. Run `join-threats-md.py --out {out} PLAN`. On anything but 0, stop with D4's error.

**What `plan` and `reconcile` print for `threats-md`.** This overrides `cli.md`'s wave entry for this stage only, and T088 folds it into `cli.md`. Each wave entry is `{batch_id, input_path, part_path, section, finding_ids, rows, problem}`:
- `rows` is `[first, last]`, 1-based, for a row section, and `null` for a finding section;
- `problem` is `null` on a first attempt, and `missing` for a part that wasn't written. Otherwise it is the earlier attempt's first validation failure, naming the item and the key, never the value.

So the orchestrator writes each part without reading its batch input. The batch input stays the record that the plan's digest pins.

**Units, halving and retries.**
- A finding section's batch input has `units` `[{section, finding_id}]`, one per ID, in S-2 order. A row section's has `[{section, row}]`, one per row, contiguous.
- §4's readings apply, with a batch's units in place of its IDs:
  - a batch of two or more units that is `missing` or `unparseable` is halved into two contiguous runs;
  - an `invalid` batch, or a one-unit batch, is retried with the same units.
- The budget and the attempt cap are §4's.

**The joiner's layout.**
- **The frontmatter** comes from the manifest, in the template's YAML shape. `schema_version` is D15's `"1.4"`, as a constant. Strings are written double-quoted, and the manifest has already refused a `"`, a `\` or a control character in any of them.
- **The title** is the template's `# Threat Model Report`.
- **Then each section in order:**
  - its heading;
  - the template's fixed tables: Section 3's and Section 4's prefix tables, and Section 3's and Section 6's risk matrices;
  - its header and separator;
  - its rows. A finding section's rows are in S-2 order. Section 7's are sorted by risk level, `Critical` first, then in the order the findings appear in Sections 3 and 4 (the eight tables in order, and S-2 order within each). A row section's rows are in plan order.
- **Category** in Section 7 is the prefix's table title: `Spoofing`, `Tampering`, `Repudiation`, `Information Disclosure`, `Denial of Service` or `Elevation of Privilege`; `Agentic` for `AG`, `AGP` and `TE`; `LLM` for `LLM`, `OI` and `MI`.
- **IDs** are written as the manifest spells them, and compared in canonical form (D3).
- **Each cell** takes D3's cell sink. Every `#` in it is also written `&#35;`, in the same pass, so that a reference the sink writes is never escaped twice. `parse_markdown_table` finds a section by the first line that holds its heading's text, so without this a cell quoting `### Data Flows` would capture that table's reader.
- **Notes**, in fixed text, each printed only in its state:
  - Section 2's, when both of its tables are empty;
  - Section 4's, when both AI tables are empty, worded so that it stays true: `No AI threat findings were recorded.`;
  - Section 4a's `No cross-agent correlations detected.`, when it is empty;
  - Section 4c's `No baseline findings were resolved in this run.`, when the run has a baseline and no RESOLVED finding;
  - the coverage matrix's footnote, when Section 4a has rows. It holds no number: `Counts reflect deduplicated findings: each correlation group counts once.`;
  - Section 5a's `Coverage gate passed — all required threat categories evaluated for every component.`, when `gate_gaps` is empty;
  - Section 6's sentence before the risk-level table.
- **No other prose** is written. The joiner writes nothing for Phase 3.5's record, the populator's block or the two body lines, because their scripts upsert them after the join.
- **The stamp** follows D4, with `renderer=join-threats-md.py`. The input digest covers the manifest's digest and the accepted parts' items in plan order.

**The joiner's checks and exit codes.**
- **Exit 1:** the plan, the manifest or a part is missing or unreadable.
- **Exit 2:** the plan's digest differs, a batch isn't `done`, the manifest's digest differs from the one the plan recorded, or the manifest or a part fails re-validation.
- **Exit 4:** the staged file, read back from disk, fails a check:
  - `tachi_parsers.parse_reference_set` must return exactly the manifest's `open` IDs and its `resolved` IDs (none when it is null), with no duplicate. Each finding's values must equal its item's, under the reader's own normalization.
  - No character in step 10's set may appear (P0-4's backstop, through `tachi_parts.forbidden_character`).
- **Exit 0:** the staged file replaces `{out}/threats.md` (`os.replace`). On any other code the canonical file isn't written.
- Heading order and the headers are constants, so the joiner doesn't check them at run time. A drift test pins them against the template once T119 has aligned it.

**Sizes (ADR-050 D6).** Each size is ⌊8,000 × 2.598 ÷ p90⌋. The p90 is the item's bytes at two-space indentation, the higher of the shipped examples' and the fixture baseline's: 1,225 for the category tables, 506 for Section 7, 761 for Section 4a, and 349 for the heaviest of the others. 2.598 is W1's lower measured r, the scorer's. T130's fixture run confirms the sizes from the live parts.

## Stage payload: `report` (item O-γ; ADR-050 D6, rev. 3)

Typed `tachi-threat-report` agents write these parts. The orchestrator plans and reconciles them in Phase 5, and `assemble-report.py report` assembles `threat-report.md` from them at Step 2.9 (ADR-050 D4, D14). A part holds the units of one section, and nothing in a part is markdown structure: code writes every heading, table, list and fixed sentence. `tachi_parts` holds the parts table and the item table below as constants, which the planner, the validator and the assembler import. A drift test pins the headings against `templates/tachi/output-schemas/threat-report.md` once T113 has aligned the template.

**The parts**, in template order. Section 5, the appendix and the frontmatter have no part.

| Template section | Part kind and key | Planned | Units: fragment keys, or items | Limit per fragment (characters) |
|---|---|---|---|---|
| 1. Executive Summary | section, `exec_summary` | always | `risk_posture`, `top_threats` and `key_recommendations`; `compliance`, optional | 1,500; 4,000; 2,500; 2,000 |
| 2. Architecture Overview | section, `architecture_overview` | always | `system_context`, `trust_boundaries` | 4,000 each |
| 3. Threat Analysis | section, `threat_categories` | always | `overview`, optional; `category.<key>` for each category with an open finding; `summary.<key>` for each category with a summarized finding | 1,500; 600 each; 1,200 each |
| 3. Threat Analysis | findings, `threat_analysis` | when it has a unit | one per finding narrated one by one | — |
| 4. Cross-Cutting Themes | section, `cross_cutting_themes` | always | one unit, `themes`, which allows `theme.<n>.title` and `theme.<n>.body` for n from 1 to 6, all optional | 120; 2,000 |
| 6. Cross-Layer Attack Chains | section, `attack_chains` | for `chains written` | `chain.<chain ID>` for each surfaced chain | 2,000 each |
| Agentic Pattern Analysis | section, `agentic_patterns` | when an open finding has a pattern | `pattern.<value>` for each of the six pattern values that Section 7 holds; `multi` when it holds `multiple` | 1,500 each; 3,000 |
| 7. Remediation Roadmap | findings, `remediation_roadmap` | always | one per roadmap row | — |
| 9. Delta Summary | section, `delta_summary` | when the run has a baseline | `progress` | 3,000 |

- **Keys.** The category keys are item O-β's: `spoofing`, `tampering`, `repudiation`, `information_disclosure`, `denial_of_service` and `elevation_of_privilege`; `agentic` for `AG`, `AGP` and `TE`; and `llm` for `LLM`, `OI` and `MI`. The pattern values are Section 7's six.
- **Narrated or summarized.** A finding is summarized when the run has more than 30 open findings and its risk level is Medium, Low or Note. Every other open finding is narrated one by one.
- **A roadmap row** is an open finding that isn't a correlation group's non-primary member. A group's primary is its first member in Section 4a, read through `parse_correlation_groups`, and its row stands for the group.
- **The budget.** Each section's limits sum to at most 16,000 characters, so a section part stays within S-1's 8,000 tokens at W1's r of 2.598.

**The findings items.**

| Section | Item keys | Rules |
|---|---|---|
| `threat_analysis` | `finding_id`, `narrative`, `tree_summary` | `narrative`: 1–2,000 characters, cut at 2,000. `tree_summary`: 1–300, cut at 300, for a Critical or High finding, and `null` for any other |
| `remediation_roadmap` | `finding_id`, `effort`, `dependencies` | `effort`: `Low`, `Medium` or `High`. `dependencies`: 1–400, cut at 400, or `null`, which the assembler writes as `None` |

**The envelope (§1) in `report`.**
- `agent_type` is `tachi-threat-report`.
- **A section part:** `finding_ids` and `items` are `[]`. `fragments` holds one fragment for each required unit of its batch, at most one for each optional unit, and nothing else, with no key twice. The `themes` unit allows its theme keys in pairs, numbered from 1 with no gap.
- **A findings part:** `finding_ids` is its batch's planned set, with one item per ID under the section's keys, and `fragments` is `[]` (step 8, unchanged).

**String classes (ADR-050 D3).**
- **Closed values** reject the part when wrong: `finding_id`, `effort`, each fragment's `slot_key`, and whether `tree_summary` and `dependencies` are `null`.
- **Narrative:** every fragment's `text`, and `narrative`, `tree_summary` and `dependencies`. Each takes the slot grammar, the numeral ban, the per-field fallback and the cut at its limit (step 9, RR2).
- No `report` value is evidence.

**Slots.** These are the `report` rows of ADR-050 D3's table, as item O-γ rules them:

| Kind | Argument | Resolves to |
|---|---|---|
| `count` | `open`, `resolved`, `new`, `unchanged` or `updated`; a band, `critical`, `high`, `medium`, `low` or `note`; a category key; or `<category key>.<band>` | the reference set's count of open findings with that status, band or category; for `resolved`, of its RESOLVED findings |
| `pct` | a band | that band's share of the open findings, by largest remainder (D5) |
| `band` | `risk:<finding ID>` | that open finding's risk level |
| `finding` | a finding ID | the canonical ID. It must be in the reference set |
| `ref` | a taxonomy ID | the ID as written. In a findings part, it must be one of the item's own finding's taxonomy IDs (D3). In a section fragment, it must be one of any open finding's |
| `name` | `component:<finding ID>` | that finding's component |

**Fixed fallback sentences.** This table is the wording's authority until T113 copies it into the shared part-file reference. `tachi_parts` embeds it verbatim, and a drift test pins the copies.

| Field | Sentence |
|---|---|
| `narrative` | No narrative is shown for this finding because the text the agent wrote broke the narrative rules. |
| `tree_summary` | No summary is shown for this attack tree because the text the agent wrote broke the narrative rules. |
| `dependencies` | No dependency note is shown because the text the agent wrote broke the narrative rules. |
| `theme.<n>.title` | Untitled theme |
| every other fragment | This passage is not shown because the text the agent wrote broke the narrative rules. |

A field that falls back or is cut is counted in the report stage's record (`narrative_fallbacks`, `truncations`), and the report prints no flag.

**Batch inputs, units, halving and retries.**
- **A section's batch input** has one unit per planned key, `{section, key, …}`, holding the rows that key is about. `exec_summary`, `threat_categories`, `cross_cutting_themes` and `agentic_patterns` get the Section 7 rows of their findings, and the themes also get Section 4a's groups. `architecture_overview` gets Sections 1 and 2's tables, `attack_chains` the surfaced chains' rows, and `delta_summary` Section 4c's rows and the lifecycle counts. A category's unit lists its narrated and summarized IDs. `themes` is the one unit of `cross_cutting_themes`.
- **A findings batch input** has one unit per finding, in S-2 order: `{section, finding_id, …}`, holding the finding's Section 7 row and its category-table row, decoded. In `threat_analysis` it adds `tree`, whether the finding is Critical or High. In `remediation_roadmap`, a group primary's unit adds its group's ID and its members' Section 7 rows.
- **`refs` is `{}`.** No report agent reads `threats.md` (ADR-050 D6), and each batch input stays within its 4 MiB cap.
- **§4's readings apply,** with a batch's units in place of its IDs, as for `threats-md`. A batch of two or more units that is `missing` or `unparseable` is halved, and an `invalid` or one-unit batch is retried with the same units.

**The assembler's layout** (`assemble-report.py report`). It numbers the sections present in template order (ADR-050 D14), as `## <n>. <title>`. It takes each finding's lead and roadmap cells from the batch inputs, whose digests the plan pins, and the reference set from `threats.md` as Step 2.9 finds it. Every cell takes D3's cell sink, every fragment D3's prose sink, and each slot resolves against that reference set.
- **The frontmatter,** in the template's YAML shape, from the reference set, the merged manifest and `threats.md`'s frontmatter, with the plan's `date`.
- **Section 1:** `### Risk Posture`, `### Top 5 Threats by Business Impact`, `### Key Recommendations`, `### Compliance Relevance` (only with its fragment) and `### Remediation Timeline`, the names that `extract-report-data.py` reads. The timeline's lines are code's, in that reader's form, `- **<tier>** (<count> <band> findings)`, one per band with open findings: Immediate for Critical, Short-term for High, Medium-term for Medium, and Backlog for Low and for Note.
- **Section 2:** `### System Context` and `### Trust Boundary Summary`, each with its fragment.
- **Section 3:** the optional overview, then the eight subsections 3.1 to 3.8, on every run. A non-empty subsection holds its category fragment, then each narrated finding in S-2 order, then its summary fragment. Each narrated finding has a lead (its ID, component, MAESTRO layer, likelihood, impact and risk level, and its status in a baseline run, with `—` for a value its category table lacks), followed by its narrative. An empty subsection prints `No <category> threats were identified in this threat model.`
- **Section 4:** `### Theme <n>: <title>` and its body for each theme, or the template's note when there is none.
- **Section 5:** ADR-050 D14's, with each tree's `tree_summary` as its one-sentence summary.
- **Section 6,** on every run. For `chains written`, each surfaced chain, in rank order, has a heading with its ID and title, then a line with its layers, highest severity, member count and converging count, then its narrative. After the narrative come its chain-breaking control (the target's ID, layer and mitigation, verbatim), the template's disclaimer, and its members with their layers and roles, all from `attack-chains.md`. For any other outcome, the section holds D13's outcome line.
- **Agentic Pattern Analysis,** when planned. It opens with the template's boilerplate, then `### Multi-Pattern Findings` with the `multi` fragment, when Section 7 holds `multiple`. Each pattern's subsection follows, ordered by highest risk level, then finding count, then pattern order. Each has its heading, its definition copied from `maestro-agentic-patterns-shared.md` (drift-tested), a counts line in the template's `Critical: N | High: N | Medium: N | Low: N` form, and an impacted-findings line in Sections 3 and 4's order, both from Section 7's pattern column, then its fragment. A `multiple` finding is listed under Multi-Pattern Findings only.
- **Section 7:**
  - an intro with the row count, the rows per tier and the most impacted component, which is the one with the most open findings, with ties broken by name;
  - the table, ordered by risk level, then component, then S-2 order. Finding ID, Component and Mitigation come from Section 7, and Effort and Dependencies from the item. A group's row takes the primary's component and the group's highest risk level. Its Mitigation is each member's, verbatim, in member order, each led by the member's ID, and its Dependencies begin `Correlated: <IDs> (<group>).`;
  - the template's priority-tier and effort-scale tables.
- **The appendix:** one row for each place the report puts a finding, with that heading's text. The places are its Section 3 subsection, each theme whose body cites it through a `finding` slot, its tree, each surfaced chain it belongs to, its pattern subsection, and its roadmap row, or for a peer, its group's row. So every open finding has at least its Section 3 and roadmap rows, by construction.
- **Section 9,** when planned: `### Finding Lifecycle Breakdown`, from Section 7's statuses and Section 4c; `### Remediation Progress`, with its fragment; and `### Baseline Reference`, from the frontmatter.

**The assembler's checks and exit codes.** RR3 sets what it checks before it reads a part (ADR-050 D6).
- **Exit 1:** the plan, an input, a batch input or a part is missing or unreadable.
- **Exit 2:**
  - a plan's digest or pointer differs, a batch isn't `done`, or a part fails re-validation, for the report plan or the trees plan it pins;
  - an input's digest differs, except `threats.md`'s and `attack-chains.md`'s;
  - the reference set's digest differs from `params.reference_digest`;
  - for `chains written`, `attack-chains.md` doesn't hold exactly the planned surfaced chains.
- **Exit 4:** FR-K5.3, FR-K5.5 or FR-K5.7 fails (ADR-050 D14), or the staged file holds a character in step 10's set (P0-4's backstop, through `tachi_parts.forbidden_character`, as the joiner checks).
- **Exit 0:** the stamped file, staged under `report/<plan_id>/staged/`, replaces `{out}/threat-report.md` (`os.replace`), overwriting any file an agent wrote, and the report stage's record is written. On any other code the canonical file isn't written.

**Sizes (ADR-050 D6).** Each size is ⌊8,000 × 2.598 ÷ p90⌋ items: 22 for `threat_analysis` (p90 931 bytes) and 144 for `remediation_roadmap` (p90 144 bytes). The p90 is an item's bytes at two-space indentation, measured on the seven shipped example reports (115 analysis items and 160 roadmap rows), with each digit-bearing word written as a slot. The analysis items still held today's risk wording, which moves to the lead, so the size is conservative. A section part is one batch at planning. T130's fixture run confirms the sizes from the live parts.
