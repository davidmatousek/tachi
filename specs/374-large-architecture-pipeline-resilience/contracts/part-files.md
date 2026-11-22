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
