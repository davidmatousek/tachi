# Data Model: Adopter Install + Output Fidelity Fixes (Feature 373)

These are the entities, rules and algorithms behind the spec's Key Entities. Names follow PD-13. Every numeric rule follows PD-5, and every algorithm here is deterministic.

**Revision 1 (2026-09-27).** This revision folds in the architect's plan review (`.aod/results/architect-373-plan.md`: H1, H2, M1, M4, M5, L4–L6) and the PM's plan review (`.aod/results/product-manager-373-plan.md`: RC-P7, R-P6, PM §9 item 3). Changed sections are marked **(rev. 1)**. The decisions behind them are PD-10, PD-14 and PD-16 to PD-19 in `research.md`.

---

## 1. Install manifest block (K1, K2)

The block is the ordered list of relative paths between the exact lines `<!-- BEGIN MANIFEST -->` and `<!-- END MANIFEST -->` in `INSTALL_MANIFEST.md`.

| Field | Rule |
|---|---|
| `entry` | A relative path. A **directory entry** ends with `/`; a **file entry** does not |
| Parsing (mirrors `install.sh` `parse_manifest`) | Split on `\n` only. Markers match by exact string equality. Inside the block, skip `""` and any line whose first character is `#`. The installer concatenates multiple sections; the test forbids more than one (see validation) |
| Validation (completeness test only) | Each marker occurs **exactly once**. No entry has leading or trailing whitespace. No entry contains a `..` segment or starts with `/` or `~`. The block yields at least one entry. **(rev. 1)** No entry is a path prefix of another entry, which keeps the checked-set origins unambiguous (§2). No line inside the block starts with `<!--`: the installer would copy it as an entry, while the manual loop drops it |
| Coverage | A required path `P` is covered when some entry `E` satisfies one of: `E == P`; `E` is a directory entry and `P` starts with `E`; `P` is a directory and `E == P + "/"` |

**The required set:**
- (a) every directory matching `.claude/skills/tachi-*`;
- (b) every file matching `.claude/commands/tachi.*.md`;
- (c) every `scripts/<name>.py` matched by `(?<![\w./-])(?:\./)?scripts/[\w-]+\.py` in the distributed globs (`.claude/commands/tachi.*.md`, `.claude/agents/tachi/**`, `.claude/skills/tachi-*/**`, `templates/tachi/**`), minus the commented exclusion list;
- (d) the transitive closure of local imports: `ast` `Import`/`ImportFrom` names that resolve to `scripts/<name>.py`.

**Cardinality floors.** All are non-vacuous at HEAD, as verified at plan review: (a) ≥ 21, (b) ≥ 6, (c) ≥ 4, (d) ≥ 1.

**S-13.** Every import executed at module load in the four distributable scripts must be in `sys.stdlib_module_names ∪ {"tachi_parsers"}`. That includes imports nested in module-level `if`, `try` or `with` blocks, but not imports inside function bodies. Only the top-level package name is checked. The assertion skips on Python < 3.10. At HEAD, the only non-stdlib names are `tachi_parsers` at module level and `yaml` inside a function.

---

## 2. Checked-set member, classification and destination containment (K3, D-1) **(rev. 1)**

| Field | Meaning |
|---|---|
| `component` | Path relative to the physical project root `TARGET_P` |
| `origins` | The **set** of origins that produced it: `ancestor` (a strict prefix of a manifest entry), `entry` (the entry path itself), `subtree` (strictly inside a **directory** entry's destination, from the source-subtree walk), `cleanup-file` (one of the five deprecated-command files) or `cleanup-ancestor` (an ancestor of one). A component keeps every origin it has; the decision uses the set, so enumeration order never matters |
| `need` | `dir` for an ancestor or a directory entry; `file` for a file entry or a cleanup file |
| `is_link` | `[ -L "$TARGET_P/$component" ]`, **not** gated on `[ -e ]` |
| `readlink_text` | The raw `readlink` output (reported for unresolvable links) |
| `resolved` | The physical path from `resolve`, or empty when unresolvable. **(amended at P0, 2026-09-28)** `resolve` accepts at most 32 hops in the link's own chain, down from 40 (SEC-K3-01). It also requires the OS to be able to look up the path as given (`[ -e ]`), because the platform's symlink limit counts every link in one lookup, ancestors included (RC-1; `contracts/installer-cli.md`) |
| `class` | One of the classes below |

### 2.1 Link classes

Link classes apply only when `is_link` is true. The first matching row wins.

| Precedence | Class | Condition |
|---|---|---|
| 1 | `cleanup-only` | `origins == {cleanup-file}`: the deprecated file itself is the link, and it is on no copy path. The class of its target is irrelevant: it is never deleted through |
| 2 | `unresolvable` | `resolve` fails: a dangling target, or looping. Looping means more than 32 hops in the link's own chain, or a whole-path lookup the OS refuses with ELOOP: more links in one lookup than the platform allows (Darwin 32, Linux 40), counting linked ancestors. **(amended at P0, 2026-09-28; was "more than 40 hops")** **Or the target has the wrong type**: `need == dir` but the target is not a directory, or `need == file` but the target is a directory. Otherwise `mkdir -p` or `cp` would fail mid-copy with the flag, leaving a partial install |
| 3 | `nested` | `subtree ∈ origins` |
| 4 | `inside` | `resolved` is `TARGET_P` or inside it |
| 5 | `outside` | otherwise |

A component that is not a link is `not-link`, and it never blocks.

### 2.2 Destination containment (replaces the per-link `source-tree` class) **(rev. 1)**

- For every manifest entry, and for every cleanup file that is **not itself a link**, compute its **physical destination**, `dest = phys_dest("$TARGET_P/<path>")`. That is `resolve` of the path's deepest existing component, plus the components that do not exist yet (`contracts/installer-cli.md`). A cleanup file that is itself a link is governed by the `cleanup-only` rule alone: it is never deleted through, whatever its target.
- If `dest` is `SRC_P` or lies inside it, the path is `source-tree`: refused regardless of the flag. Containment is tested **by file identity**, with the `under` walk (`[ -ef ]`, same device and inode), never by string prefix. So a case-variant path on macOS APFS, or a firmlink, cannot bypass it (rev. 2, architect ruling AR-1). Project-root containment uses the same walk: `under "$TARGET_P" "$SRC_P"`.
- This covers:
  - a link straight into the clone (the old class);
  - a link to an **ancestor** of the clone (for example `templates → ..`, where entry `templates/tachi/` would land at the clone root);
  - a clone vendored at a destination path with no link at all.
- The earlier per-link check missed the last two; the plan review reproduced the second case.
- `phys_dest` fails only where the walk meets a dangling link, or a looping one (an ELOOP whole-path lookup, RC-1). §2.1 already refuses both. **(amended at P0, 2026-09-28: "or a looping one")**

### 2.3 Decision table

| Class or check | Without `--follow-symlinks` | With `--follow-symlinks` |
|---|---|---|
| `not-link` | proceed | proceed |
| `inside` / `outside` (origin `ancestor`, `entry` or `cleanup-ancestor`) | **refuse**; the flag is offered as a remedy | **follow** for copies: named before copying and in the summary. Every cleanup under a linked `cleanup-ancestor` is **skipped**, listed as skipped and never deleted |
| `nested` | **refuse**; no flag remedy | **refuse**; no flag remedy |
| `unresolvable` (dangling, looping or wrong type) | **refuse**, with the `readlink` text; no flag remedy | **refuse**, with the `readlink` text; no flag remedy |
| `source-tree` (§2.2) | **refuse**; no flag remedy | **refuse**; no flag remedy |
| `cleanup-only` | **refuse** | **skip that cleanup**: listed as skipped, never deleted |

**Project-root containment** is checked first, before the version block. If `under "$TARGET_P" "$SRC_P"` holds (`TARGET_P` is the clone or lies inside it, compared by file identity per AR-1), the install is refused regardless of the flag. This generalizes the logical-path self-install guard.

**State:** `pre-flight → (refused → exit 1, ref restored) | (proceed → cleanup → copy → summary → exit 0/1)`. The pre-flight writes nothing.

---

## 3. Controls row (K9, K11, K12) **(rev. 1)**

| Field | Source and rule |
|---|---|
| `threat_id` | The `Threat ID` column. A **placeholder** (empty after strip, or matching `^[-–—]+$`) drops the row before dedup |
| header matching | Normalize: casefold → strip one trailing `.` → collapse whitespace. Then look up the alias map: `residual score`/`residual` → residual score; `residual severity`/`residual sev` → residual severity; `inherent score`/`inherent` → inherent score; `control status`/`status` → control status |
| scores | **(rev. 1)** Every score goes through one helper, `parse_score(s) -> Decimal \| None`. It catches `decimal.InvalidOperation`, `ValueError` and `TypeError` (`InvalidOperation` is **not** a `ValueError` subclass). It rejects non-finite values (`NaN`, `Infinity`), and it returns `None` for anything unparseable (`""`, `—`, `8.5 (High)`), counted in the aggregated "unparseable score" warning. `_score_to_band` uses the same helper |
| `inherent` | `parse_score` of the column. If missing, it is filled by ID join to the risk-scores composites (`parse_compensating_controls_md(content, composites_by_id=None)`, fed from `parse_risk_scores_findings`; the report path reads `risk-scores.md` at data tier 1 when it is present, so both surfaces join the same way; tasks.md T020). If still missing, the row gets `inherent = None`, is excluded from the volumes, and warns |
| `inherent_band` | Banded from `inherent` (9.0 / 7.0 / 4.0 → critical / high / medium / else low). If `inherent` is None, the `Inherent Severity` column is used. If neither exists, the row is absent from the Tier 2 mix, and it warns |
| `status_class` | **(rev. 1)** Computed **once per row, at parse time**, by `classify_control_status`. Every consumer reads the stored value: the funnel, the STRIDE coverage matrix (`tachi_parsers.py:1203`) and the coverage fallback (`:1255`). So the warning fires once per row. Rules, whole-token and case-insensitive: a token **starting** `partial` (`partial`, `partially`) → `partial`; the normalized status in {`no control found`, `missing`, `none`, `not found`} → `none` (silent); a `found` token with no negation token (`no`, `not`, `none`, `nothing`) → `found`; anything else (including empty) → `none`, with a warning. Observed labels (`Control Found`, `Control Found (implemented)`, `Partial Control`, `No Control Found`) classify the same as under today's idiom. `Partially Found` → partial (the whole-token rule alone would have said found). `None found` → none, with a warning |
| `residual` | `parse_score` of the column. If it is greater than `inherent`, it is **clamped** to `inherent` once, here, with a warning. If it is missing while `inherent` is present, `residual = inherent` (no credit), with a warning |
| `residual_band` | Banded from the clamped `residual`; otherwise the `Residual Severity` column |
| dedup | First occurrence by `threat_id`, after placeholder rows are dropped |

**One row set.** In 4-tier mode, every Tier 2–4 figure comes from these rows.

**Tier-3 per-row score:** `residual if status_class == found else inherent`. Its band follows the same thresholds. Without `inherent`, it falls back to `residual_band` when found, and `inherent_band` otherwise.

**K11 carve unit (rev. 1, PM §9 item 3).** The `inherent` read, `parse_score`'s use for inherent, the classifier's replacement of both row idioms, and the clamp-once all belong to **K11**. If TW-0 or TW-1 carves K11:
- the parser keeps today's residual handling (unclamped) and today's substring status idiom;
- `parse_score` still serves `_score_to_band` (K9);
- §5's "after the clamp" reads as "today's unclamped residual counts".

That is consistent: without K11 there is no Tier 4 mix for the posture to match. It is written here so that the carve stays mechanical.

---

## 4. Funnel (K11, D-2, PD-4, PD-5, PD-18) **(rev. 1)**

### 4.1 Tier entries

`template_data.funnel_tiers` **always has four entries, all objects**; no entry is `null` any more. JSON `tier` k is funnel Tier k+1: 0 = Threats Identified, 1 = Inherent Risk Scored, 2 = Controls Applied, 3 = Residual Risk. This is **not** the data tier.

| Field | Type | Rule |
|---|---|---|
| `tier` | int 0–3 | as above |
| `label` | str | Today's labels. In 3-tier mode, JSON tier 2's label is `"Unmitigated Risk"` (the template's existing alternate label) |
| `source` | str or null | Today's source strings; `null` on a ghost tier |
| `ghost` | bool | **(rev. 1)** `true` when the tier's data source is absent. The template renders ghost tiers with its CTA text, keyed on this field, never on a `null` entry |
| `count` | int or null | Tier 1: threats.md findings. Tiers 2–4: the number of rows in the one row set (4-tier) or the risk-scores rows (3-tier). `null` on a ghost tier |
| `volume` | number (1 dp) or null | Tier 1: always null. 4-tier: V2 = Σ `inherent`, V3 = Σ Tier-3 per-row score, V4 = Σ `residual`, over rows with `inherent`. 3-tier: V2 = Σ composites, and JSON tier 2 ("Unmitigated Risk") = V2. Null on a ghost tier, and null on every tier when volumes are **unavailable** (§4.3) |
| `severity_mix` | {critical, high, medium, low} ints, or null | Tier 1: qualitative (threats.md). Tier 2: `inherent_band`. Tier 3: the Tier-3 band (in 3-tier mode, Tier 2's mix). Tier 4: `residual_band`. Rows missing a band are absent from that mix only. `null` on a ghost tier |
| `width` | int (percent) | Every entry, ghost tiers included: W1 = 100, W2 = 100 − STEP. For k = 3, 4: `round_half_up(clamp(W2·V_k/V2, FLOOR + (4−k)·STEP, W_{k−1} − STEP))`, where `W_{k−1}` is the **emitted, rounded** width. Ghost tiers, or unavailable volumes (with a warning): W_k = W_{k−1} − STEP. **STEP = 10, FLOOR = 30**. Implementation: the clamp bounds must be `Decimal`, because `min(max(x, 40), 80)` returns a bare `int` when a bound wins, and a following `.quantize()` then raises (reproduced at plan review) |

### 4.2 Reductions

`template_data.reduction_percentages` **always has three entries**: `{from_tier: 0, to_tier: 1}`, `{1, 2}` and `{2, 3}`, each with `percentage` a number (1 dp) or `null`.

| Pair | Value |
|---|---|
| (0→1) | `0.0` by definition when JSON tier 1 is real. `null` when it is a ghost (threats-only mode): a ghost wins over "by definition" |
| (1→2) | (V2 − V3)/V2 × 100. 3-tier mode: `0.0` (V3 = V2) |
| (2→3) | (V3 − V4)/V3 × 100 |

- (1→2) and (2→3) are `null` when either side is a ghost or volumes are unavailable.
- **(rev. 1) Quantize, then derive.** Reductions are computed from the **emitted** (0.1-quantized) volumes, so any reader can reproduce them from the JSON.
- A zero denominator with volumes available gives `0.0`.

### 4.3 Volumes unavailable (rev. 1, PD-18)

- **When.** In 4-tier mode, when **no** row in the one row set carries an inherent score (V2 has no terms), or when V2 = 0. The first case arises when the controls table lacks an Inherent column and `risk-scores.md` is absent, for example a run that kept only `risk-scores.sarif`. `detect_artifacts` never reads SARIF, so no join is possible.
- **What is emitted.** The volumes are **unavailable**, not zero:
  - `volume` is `null` on every tier;
  - (1→2) and (2→3) are `null`;
  - `risk_reduction`, `inherent_score` and `residual_score` are `null` **on both the funnel and the baseball card** (S-9's agreement still holds);
  - widths use the STEP cascade;
  - one warning: `Warning: no controls row carries an inherent score; funnel volumes and risk reduction are unavailable`.
- **Templates.** The "0% risk reduction — no effective controls detected" note keys on a numeric `0.0` only, never on `null`. A `null` Risk Reduction renders as "not available".
- **Rationale.** Emitting 0.0 would claim zero effect for controls that were never measured, and would replace today's Section 1 figure on the baseball card with a false one.

### 4.4 `risk_reduction` and the baseball-card totals

- `risk_reduction` = (V2 − V4)/V2 × 100, computed from the emitted V2 and V4 and quantized to 0.1. It is one computed value, assigned to both the funnel's and the baseball card's `template_data.risk_reduction`.
- The baseball card's `inherent_score` = V2 and `residual_score` = V4.
- It is null in 3-tier and threats-only modes, and whenever volumes are unavailable (§4.3).
- **S-9 carve unit.** If K11 is carved, the baseball card keeps Section 1's values (PM ruling P-9.5).

### 4.5 Warnings

All warnings go to stderr and are non-fatal. Per-row warning classes are **aggregated (rev. 1, R-P6)**: one line per class, with the count and the first five IDs in first-seen order, for example `Warning: 7 controls rows have an unrecognized status (first: S-3, T-9, …); counted as no control`. The classes are:
- a Section 1 total or reduction that differs from the row-derived value by more than 0.1 (per field, not aggregated);
- controls and risk-scores row counts that differ. **(amended at P0, 2026-09-28)** This is compared only when `risk-scores.md` is present and its Scored Threat Table yields at least one row. An unreadable table is reported once per run by the existing "could not find Scored Threat Table" warning, never as a count of 0 (RC-2);
- an unrecognized or empty status;
- a clamp;
- a missing `residual` defaulted to `inherent` (§3's residual rule). **(amended at P0, 2026-09-28)** This class was implemented in `a837ae8` but missing from this list;
- a missing `inherent` after the join;
- an unparseable score;
- volumes unavailable (§4.3).

The exact stems are in `contracts/extraction-data-contract.md`.

**Removed with K11 (amended at P0, 2026-09-28).** The legacy per-row warning is gone, together with its summary line:
- the per-row line: `<ID> in '### <Band> Residual Severity' section but residual score <X> maps to <Band2>. Using score-derived band.`;
- the summary: `<N> findings in wrong severity sections (corrected using score-derived bands)`.

The reasons:
- banding was already score-derived, so the output never depended on the heading;
- after the clamp, the legacy check would name the raw score's band while the row is banded from the clamped value, which is a contradictory claim;
- the per-row, unaggregated form conflicts with R-P6.

T035 attributes the removed lines to K11.

---

## 5. Posture (K13, D-3)

| Field | Values | Rule |
|---|---|---|
| `risk_posture_level` | `critical` \| `high` \| `medium` \| `low` | Take the data-tier severity counts: residual when a controls report exists (**after the clamp**, so the posture equals the funnel's Tier 4 mix; if K11 is carved, today's unclamped counts, per §3), else the inherent composite, else qualitative. critical > 0 → `critical`; else high > 0 → `high`; else medium > 0 → `medium`; else → `low` (including zero findings, the same as today's cover) |
| `risk_posture_label` | `CRITICAL RISK` \| `HIGH RISK` \| `MODERATE RISK` \| `LOW RISK` | A 1:1 mapping from the level |
| `risk_posture` | sentence | Unchanged, kept as supporting text |

- **Where it is emitted.** As `metadata.risk_posture_level` and `metadata.risk_posture_label` in every infographic JSON, and as `#let risk-posture-level = "…"` and `#let risk-posture-label = "…"` in `report-data.typ`.
- **(rev. 1) Executive-architecture.** Its payload is written by `_build_executive_architecture_payload`, which exits before `build_json_output` (`extract-infographic-data.py:1869`). That builder adds the two fields to its own `metadata`, computed from the same tier severity dict that `main()` already holds. The change is additive and no golden covers it.
- **Rendering.** The surfaces render the label verbatim and take their color from the level. **(rev. 1)** The baseball-card badge shows the label alone (for example `HIGH RISK`), not `RISK POSTURE: HIGH RISK`, to avoid the doubled word.

---

## 6. Delta status map (K12) **(rev. 1, PD-16)**

- **Signature.** `delta_status_by_id(threats_md) -> (status_by_id: dict[str, str], has_status_column: bool, row_count: int)` reads the threats.md Section 7 "Recommended Actions" table (`Finding ID`, `Status`). Placeholder IDs are skipped. `row_count` feeds the scoped empty-map check.
- **Companion helpers** (all in `tachi_parsers.py`, written by B1 in W1; AR-3; tasks.md T016):
  - `apply_delta_status(findings, map)` stamps normalized statuses onto a tier's findings, **for the badges and `top_findings[].delta_status` only**; it plays no part in the counts;
  - `compute_delta_counts(status_by_id, resolved)` counts the **normalized Section 7 map** (placeholder IDs excluded), plus the resolved rows, identically on both surfaces (FR-K12.1/K12.2; architect re-review NM-1);
  - `warn_delta_scope(has_baseline, has_status_column, map, row_count, tier_ids)` emits the scoped warnings below, aggregated.

  Both extractors call the same helpers, so neither needs a W2 parser edit.
- **Normalization before matching (N6 order, rev. 2).** Strip a surrounding run of backticks, `*`, `_` and whitespace; then strip one surrounding `[`…`]` pair; then strip the run again; then upper-case. So `[NEW]`, `**[NEW]**`, `` `[NEW]` ``, `**NEW**` and ` new ` all count as `NEW`. This matters because:
  - the orchestrator prescribes bracketed lifecycle tags (`orchestrator.md:64`, `:288`);
  - both shipped baseline examples (`agentic-app` and `agentic-app/sample-report`, `has_baseline = true`) carry `[NEW]` and `[UNCHANGED]`.
- **Counted values.** Only `NEW`, `UPDATED` and `UNCHANGED` after normalization. Any other non-empty value, or an empty cell on a baseline run, counts toward one aggregated warning.
- **`delta_counts`** = {`new`, `updated`, `unchanged`} counted from the map, plus `resolved` = the count of non-placeholder rows under `^##\s+4[bc]\.\s+Resolved Findings\s*$`.
- **Scoped checks (warnings, never raised).** Both run only when `has_baseline` is true **and** `has_status_column` is true:
  - the map is empty although Section 7 has rows;
  - the map's ID set differs from the tier's finding-ID set.

  Otherwise neither check runs. The scope is what keeps legacy Status-less tables from warning or failing, for example `maestro-reference` (the live-render example: 111 Section 7 rows, no Status column, no baseline) and `mobile-banking-app/sample-report`.
- **Missing column on a baseline run.** When `has_baseline` is true and Section 7 has no Status column: one warning, `Warning: baseline run but threats.md Section 7 has no Status column; delta counts unavailable`, and the counts stay 0.
- **Badges.** The report path's badges use the normalized status. `_merge_delta_status` stays importable and delegates to `delta_status_by_id` and `apply_delta_status`, keeping its `(findings, threats_md)` signature.
- **Tier 3 (amended at P0, 2026-09-28).**
  - `parse_threats_findings` stores `normalize_delta_status(Status)` at parse. Commit `9019528` closed a T016 gap: before it, raw `[NEW]` values reached the tier-3 badges and `top_findings[].delta_status`.
  - So all three data tiers badge from the same normalized value as the map, and tier 3 needs no `apply_delta_status` call. The key stays absent when the cell is empty.

---

## 7. Recommendation (K13.1) **(rev. 1, RC-P7, PD-19)**

**Resolution on data tier 1**, per finding, in precedence order:
1. the analyzer recommendation joined from controls Section 4;
2. `"Threat-model mitigation: " + <Section 7 Mitigation>` when that mitigation is non-empty;
3. `"No recommendation available"`.

The result is written to the finding's `recommendation` field.

**Every data tier (rev. 1).** After resolution, an empty recommendation text becomes `No recommendation available`. The prefix fallback (step 2) stays tier-1 only. Where the rule is applied:

| Tier | Finding field (read by the finding cards, `findings-detail.typ:95`) | Remediation-roadmap action text | Attack-path remediation |
|---|---|---|---|
| 1 | `recommendation` (steps 1–3 above) | the finding's `recommendation` | `_get_finding_mitigation` → the finding's `recommendation` |
| 2 | no recommendation field exists; the card keeps its missing-key `—` (unchanged, not blank) | today's source (the threat text); the placeholder only if that is empty | unchanged: `_get_finding_mitigation` returns `""` and `_build_remediation` renders its generic step (not blank) |
| 3 | `mitigation`, or the placeholder when empty | the finding's `mitigation` (so the placeholder when empty) | `_get_finding_mitigation` → the finding's `mitigation` (so the placeholder when empty) |

- **Consistency.** On tiers 1 and 3, the three consumers read one field and so always agree. `_build_remediation("No recommendation available")` yields that single step.
- **Tier 2** has no recommendation source; its surfaces are unchanged and never blank.
- **Drift signal.** It warns when Section 4 has content but zero recommendations join.

---

## 8. Allow-list (K15) **(rev. 1, PD-17)**

The allow-list is a top-level `allow_list: {finding_ids: [...], component_names: [...]}`. Both lists are sorted, unique, with empty strings dropped.

**`finding_ids`: exactly the set of IDs the template's prompt renders.** It was re-derived from each template's DATA CONTENT placeholders at plan review:

| Template | `finding_ids` | Why (prompt evidence) |
|---|---|---|
| baseball-card | the **full tier finding-ID set** | The right panel shows the top findings, and the BOTTOM STRIP annotates boundary crossings and correlation callouts with finding IDs (`infographic-baseball-card.md:209`); either can name any finding |
| system-architecture | the **full tier finding-ID set** | Every component box carries its findings' ID pills (`:312`), IDs run along boundaries (`:316`), and the legend has one entry "for each finding in `threats.md` Section 3" (`:364`) |
| maestro-stack | `template_data.per_layer_summaries[].top_findings[].id` | Up to 2 `"{ID}: {short threat}"` summaries per layer (`infographic-maestro-stack.md:117`) |
| maestro-heatmap | `[]` | Cells show severity letters; no finding ID is rendered |
| risk-funnel | `[]` | Tiers and sidebar show counts, volumes and percentages; no finding ID is rendered |
| executive-architecture | `callouts[].finding_id` | Only CALLOUTS carry IDs |

The full tier finding-ID set is the IDs of the tier's findings (today's validation-only `findings_ids`, `extract-infographic-data.py:1893`), now emitted where it is the rendered set. It still blocks invented IDs and IDs from other runs, which is the failure SC-5 measures.

**`component_names`: one common set for every template.** It holds the component names the run knows:
- the scope components;
- trust-zone members and zone names;
- data-flow endpoints (`scope["data_flows"][].source/destination`);
- the tier findings' `component` values.

The names clause in the prompts forbids *inventing* components. It tolerates the system-architecture legend's own abbreviated names (`:371`), which the agent composes and the extractor cannot enumerate (PD-17).

**Where it is emitted.**
- The five scaffolded templates emit it through `build_json_output`.
- **Executive-architecture** emits it inside `_build_executive_architecture_payload`, because that path writes its own payload and exits at `extract-infographic-data.py:1869`. `test_executive_architecture_payload.py` asserts field subsets, so the addition is safe.

---

## 9. Request configuration (K14) **(rev. 1)**

| Template key | Request-body field |
|---|---|
| `model` | the URL path `models/{model}:generateContent` (the first model in the chain) |
| `fallback_model` | the next model, tried **only** when the model is unavailable to the key: HTTP 404 `NOT_FOUND` or 403 `PERMISSION_DENIED` (PD-14, rev. 1) |
| `response_modalities` | `generationConfig.responseModalities` (`["TEXT","IMAGE"]`) |
| `aspect_ratio` | `generationConfig.imageConfig.aspectRatio` (in {1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9}) |
| `image_size` (only if PD-3's P-10.3 rule restores it) | `generationConfig.imageConfig.imageSize` (`"2K"`) |

- **Chain:** `gemini-3-pro-image`, then `gemini-3.1-flash-image`.
- **Instances:** five template blocks at 16:9, and executive-architecture's configuration (PD-1) at 3:4.
- **(rev. 1) Response.** The REST response carries the image at `candidates[0].content.parts[].inlineData` (`mimeType`, `data`). The agent also accepts the SDK spelling (`inline_data`, `mime_type`).
