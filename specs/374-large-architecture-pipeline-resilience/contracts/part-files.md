# Contract: part files, batch plans and stage records

> Normative for F-374. ADR-050 decision D3 (envelope), D6 (plan, overflow, stage record) and D2 (payloads) owns this contract; where this file and the ADR disagree, the ADR governs. Pointers are to `b040fa1`.

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
| `stage` | `risk-score` \| `compensating-controls` (PR 1); `trees` \| `report` \| `threats-md` (PR 2; `threats-md`'s payload is item O-β, and `phase2` writes records, not parts, under item O-α, ADR-050 D6) |
| `agent_type` | the stage's agent: `tachi-risk-scorer`, `tachi-control-analyzer`, `tachi-attack-tree-delta`, `tachi-threat-report` or `tachi-orchestrator` |
| `finding_ids` | 1–500 unique IDs, equal to the planned set; `[]` only in a `report` section part |
| `items` | an array of objects, one per ID, each `{finding_id, …the stage's closed payload}` |
| `fragments` | an array of 0–50 `{slot_key, text}`. PR 1's stages carry none (`[]`). In a `report` section part, `slot_key` is one of the template's paragraph keys for that section (ADR-050 D6), and `text` is narrative prose of at most 4,000 characters, cut at 4,000 (ADR-050 D3, step 9) |

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
| `units` | the batch's unit rows, as verbatim data. In `compensating-controls`, an UNCHANGED unit's row also holds its baseline's persisted narrative text and its evidence-class values (`evidence[]`, `matrix_row`, `recommendation_body`), all decoded, for the agent to copy. So a carried string is escaped once per render (ADR-050 D2, RR1) |
| `refs` | an object mapping the stage's closed pointer names (architecture, threats, baseline files, target) to absolute paths that the command validated |
| `params` | an object of the stage's closed parameters, for example `scoring_date` as `YYYY-MM-DD` |

**§4 Batch plan, `tachi.plan/1`** (written only by `tachi-stage.py`, and replaced atomically)

| Key | Type |
|---|---|
| `schema`, `plan_id`, `stage`, `agent_type` | as in §1, and `stage` may also be `threat-model`, the run-level plan (PR 2; `phase2` joins when item O-α is ruled) |
| `created_utc` | ISO 8601, ending in `Z` |
| `tachi_version` | `X.Y.Z` |
| `inputs` | `{logical name: {path, sha256, bytes}}` |
| `params` | as in §3 |
| `batch_size` | an integer, 1–500, or `null` for a plan with no units (the run-level `threat-model` plan) |
| `unit_count` | an integer, 0 or more |
| `preimage` | `{canonical name: sha256 \| null}`. `plan` copies each existing file to `<plan_id>/preimage/<canonical name>`, and `fail` restores a copy whose digest matches (ADR-050 D4) |
| `out_snapshot` | `{relpath: [size, mtime_ns]}`, at most 20,000 entries, or `null` |
| `retry_budget` | `{limit, used}`, both integers. `limit` is 2 × the planned batch count, and `used` counts retry dispatches, so a halving counts 2 |
| `batches` | an array of `{batch_id, parent: id \| null, attempt: 1–3, finding_ids, input_sha256, state: pending \| done \| failed \| split}`. Input and part paths are recomputed from the IDs, never stored |

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

**§6 Check hand-off, `tachi.check-handoff/1`** (PR 2; Architect re-review RR5). One file per main-session check, under the run-level plan's `threat-model/<plan_id>/checks/`, written by `attack-chains.py check` and `check-threat-model.py`. `close` and `fail` read it with the strict loader (closed keys, a size cap, no NaN, Infinity or duplicate keys) and fold its events into the stage record (ADR-050 D4, D15). Its keys are fixed with PR 2's checks, in lane OC.

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
- **Edge whitespace is removed at intake** (ruled at W1, from T033).
  - **The rule.** In step 9, after any cut, every narrative and evidence-class string loses its edge whitespace, by `str.strip()`, the same predicate the table readers apply to a cell before they decode. A snippet is dedented first (`textwrap.dedent`), so its lines keep their relative indentation.
  - **Why.** No value begins or ends with whitespace, so a table cell loses nothing on the round trip. A carried value is then byte-identical on every later run: T056's UNCHANGED controls results, and RR1's carried scorer prose. The rule is idempotent, because a value that is normalized again doesn't change.
  - **What it doesn't do.** Removing edge whitespace isn't a cut and raises no flag. A required prose field that is empty afterwards rejects the part, just as an empty one does.
  - **Step 10 judges only what step 9 kept** (confirmed from `c37b353`; T061 and T064 re-check it). `str.strip()` removes some characters that step 10 forbids: `\r`, VT, FF, the C0 separators U+001C–U+001F, NEL (U+0085), U+2028 and U+2029. At an edge they are stripped away and never reach output, as text beyond a cut is. Inside the kept text they still reject the part. Bidi controls aren't whitespace, so they reject wherever they appear.
  - **Not chosen:**
    - stripping only on write, inside `escape_cell` and `escape_prose`, because SARIF strings and code fences would keep the whitespace and drift between runs;
    - escaping edge whitespace as references, because that would turn D3's closed set of eight references into an open whitespace class.
  - **Owner.** R0a makes the edit, as a T013 follow-up slice before W1's push, since it owns `tachi_parts.py` and `test_tachi_parts.py` in W1. Its test carries a value with edge spaces, a tab, a newline and an indented snippet through two write-and-read round trips.
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
