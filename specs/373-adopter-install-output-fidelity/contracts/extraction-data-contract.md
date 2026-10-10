# Contract: extraction outputs (K9–K13, K15 allow-list; D-2, D-3)

This contract covers the outputs of `scripts/extract-infographic-data.py` (infographic JSON) and `scripts/extract-report-data.py` (`report-data.typ`). All shared logic lives in `scripts/tachi_parsers.py`, which is stdlib only (NFR-2). The rules are in data-model §3–§8.

**Revision 1 (2026-09-27).** This revision folds in:
- the architect's plan review: H1 (delta statuses), H2 (the allow-list), M4 and M5 (funnel shape), L4 (numerics) and L9;
- the PM's plan review: RC-P7 (the placeholder on every tier) and R-P6 (warning aggregation).

Changed sections are marked **(rev. 1)**.

## Shared helpers in `tachi_parsers.py` (new or changed)

| Helper | Behavior |
|---|---|
| `normalize_header(h)` + `HEADER_ALIASES` | casefold → strip one trailing `.` → collapse whitespace → alias map (data-model §3) |
| `is_placeholder_id(s)` | `s.strip() == ""` or `re.fullmatch(r"[-–—]+", s.strip())` |
| `parse_score(s) -> Decimal \| None` **(rev. 1)** | `Decimal(s.strip())`. It catches `decimal.InvalidOperation`, `ValueError` and `TypeError`, rejects non-finite values, and returns `None` on failure (the caller counts it toward the aggregated warning). It is used for every score, including `_score_to_band`. **It never raises (amended at P1, 2026-10-10; T036 L-5, `3dcaf84`):** it also catches `AttributeError`, so `None` or any other non-string input returns `None` like an unparseable string |
| `classify_control_status(s) -> ("found" \| "partial" \| "none", warn: bool)` **(rev. 1)** | Whole-token rules with a `partial` **prefix** and the negation set {`no`, `not`, `none`, `nothing`} (data-model §3). It is called **once per row at parse time**; the result is stored as `status_class`. It replaces both copies of the row idiom (`:1202-1208`, `:1253-1260`). The Section 1 summary reader (`:1241-1249`) keeps its own matching |
| `parse_markdown_table` stop rule | Stop at the next heading of the same or higher level than the **matched line**. A non-heading match keeps today's stop rule (`#` or `##`). **(amended at P0, 2026-09-28; RC-3)** For a heading match of level L, stop at the next heading of level ≤ max(L, 2). So a level-1 or level-2 match keeps today's `#`/`##` stop, and only a level-3+ match gets the tighter rule. The literal "same or higher" rule would *loosen* a level-1 match: it would scan past `##` sections and could adopt a later section's table, for example when the bare-substring fallbacks (`"Risk Summary"`, `"Severity Distribution"`, `"Coverage Distribution"`) hit a document title. That breaks FR-K9.2's "existing callers unaffected" |
| `match_heading(pattern, text) -> int \| None` **(rev. 1)** | Returns the **index of the first line** matching the regex (with `re.MULTILINE` semantics per line). `parse_markdown_table` gains an optional `start_line` argument, so a regex match never falls back to a substring re-search. Used by K10 (`^#{3,4}\s+Risk by MAESTRO Layer`) and K12 (`^##\s+4[bc]\.\s+Resolved Findings\s*$`) |
| `parse_compensating_controls_md` | Aliased reads, the inherent score, placeholder skip, `status_class`, **clamp once** (with a warning) and banding from the clamped scores. The K11 carve unit is noted in data-model §3 |
| `parse_resolved_findings` | 4b\|4c heading; skips placeholder rows |
| `normalize_delta_status(s)` **(rev. 2, N6)** | Strip a surrounding run of backticks, `*`, `_` and whitespace; then one `[`…`]` pair; then the run again; then upper-case (data-model §6) |
| `delta_status_by_id(threats_text) -> (dict, has_status_column, row_count)` **(rev. 2)** | `{id: normalized status}` from Section 7, whether a Status column exists, and the row count (data-model §6) |
| `apply_delta_status(findings, map)` **(rev. 2, AR-3)** | Stamps normalized statuses onto a tier's findings, for the badges and `top_findings[].delta_status` only. It plays no part in the counts: `compute_delta_counts(status_by_id, resolved)` counts the normalized map (NM-1) |
| `warn_delta_scope(has_baseline, has_status_column, map, row_count, tier_ids)` **(rev. 2, AR-3)** | PD-16's scoped warnings (empty map, ID-set mismatch, baseline without a Status column, unknown statuses after normalization), aggregated. Warnings only |
| `compute_risk_posture(counts) -> (level, label)` | data-model §5 |

`compute_allow_list(template, findings, scope, template_data, payload) -> {finding_ids, component_names}` is **not** a shared helper. It lives in `extract-infographic-data.py`, its single consumer (AR-3, laziness-ladder rung 2), and follows data-model §8.

`_merge_delta_status` stays importable from `extract-report-data.py` and delegates to `delta_status_by_id` and `apply_delta_status`, keeping its `(findings, threats_md)` signature.

## Infographic JSON **(rev. 1)**

| Path | Change | Type |
|---|---|---|
| `metadata.risk_posture_level` | **added** in every template, executive-architecture included (through its early-exit builder) | `"critical" \| "high" \| "medium" \| "low"` |
| `metadata.risk_posture_label` | **added** likewise | `"CRITICAL RISK" \| "HIGH RISK" \| "MODERATE RISK" \| "LOW RISK"` |
| `metadata.risk_posture` | unchanged (a sentence) | string |
| `allow_list` | **added** at top level, in every template, executive-architecture included | `{finding_ids: [str], component_names: [str]}`, sorted and unique (data-model §8) |
| `template_data.funnel_tiers[]` (risk-funnel) | **changed shape**: always 4 **objects** (no `null` entries); each gains `ghost`, `volume`, `severity_mix` and `width` | object per data-model §4.1 |
| `template_data.reduction_percentages[]` (risk-funnel) | **changed**: always 3 entries (0→1, 1→2, 2→3); `percentage` on volume at 1 dp, or `null` | number or null |
| `template_data.risk_reduction` (risk-funnel, baseball-card) | **corrected**: row-derived Tier 2→4 (S-9); `null` when volumes are unavailable | number (1 dp) or null |
| `template_data.inherent_score` / `.residual_score` (risk-funnel, baseball-card) | **corrected**: V2 / V4 (S-9); `null` when volumes are unavailable | number (1 dp) or null |
| `delta.delta_counts` (when a baseline is present) | **corrected**: the normalized Section 7 map plus the resolved rows | `{new, updated, unchanged, resolved}` ints |
| `prompt_scaffold.{preamble,postamble}` (five scaffolded templates) | content changes with K11, K13 and K15 text only. The splitter hardening (PD-6, now in W1) is byte-neutral on today's templates | string |

**Numeric emission.**
- Volumes, reductions and `risk_reduction` are computed in `Decimal`, quantized to 0.1 with ROUND_HALF_UP, and emitted as `float(q)`. Python's shortest-repr float prints the one-decimal value.
- Widths are emitted as `int`.
- Reductions are derived from the **emitted** volumes.
- `json.dumps` is never given a `Decimal`.

### Funnel examples (STEP = 10, FLOOR = 30)

In these examples, `{"...": 0}` stands for an elided severity mix.

**4-tier.** These are the golden fixture's real values (`tests/scripts/fixtures/exec_arch/agentic_app`), recomputed at plan review; the Tier 1 mix is illustrative:
```json
"funnel_tiers": [
  {"tier": 0, "label": "Threats Identified",   "source": "threats.md Section 6", "ghost": false, "count": 34, "volume": null,  "severity_mix": {"critical": 2, "high": 9, "medium": 15, "low": 8}, "width": 100},
  {"tier": 1, "label": "Inherent Risk Scored", "source": "...", "ghost": false, "count": 34, "volume": 209.8, "severity_mix": {"...": 0}, "width": 90},
  {"tier": 2, "label": "Controls Applied",     "source": "...", "ghost": false, "count": 34, "volume": 187.8, "severity_mix": {"...": 0}, "width": 80},
  {"tier": 3, "label": "Residual Risk",        "source": "...", "ghost": false, "count": 34, "volume": 167.6, "severity_mix": {"...": 0}, "width": 70}
],
"reduction_percentages": [
  {"from_tier": 0, "to_tier": 1, "percentage": 0.0},
  {"from_tier": 1, "to_tier": 2, "percentage": 10.5},
  {"from_tier": 2, "to_tier": 3, "percentage": 10.8}
],
"risk_reduction": 20.1, "inherent_score": 209.8, "residual_score": 167.6
```
Section 1 of that fixture says 26.9%, so the comparand warning fires as designed. A strong-reduction fixture (V2 = 100, V3 = 60, V4 = 30) gives widths 100/90/54/30, bound by FLOOR.

**3-tier** (risk scores, no controls; illustrative values):
```json
"funnel_tiers": [
  {"tier": 0, "label": "Threats Identified",   "ghost": false, "count": 34, "volume": null,  "severity_mix": {"...": 0}, "width": 100, "source": "threats.md Section 6"},
  {"tier": 1, "label": "Inherent Risk Scored", "ghost": false, "count": 34, "volume": 214.5, "severity_mix": {"...": 0}, "width": 90,  "source": "risk-scores.md"},
  {"tier": 2, "label": "Unmitigated Risk",     "ghost": false, "count": 34, "volume": 214.5, "severity_mix": {"...": 0}, "width": 80,  "source": "risk-scores.md (no controls applied)"},
  {"tier": 3, "label": "Residual Risk",        "ghost": true,  "count": null, "volume": null, "severity_mix": null,     "width": 70,  "source": null}
],
"reduction_percentages": [
  {"from_tier": 0, "to_tier": 1, "percentage": 0.0},
  {"from_tier": 1, "to_tier": 2, "percentage": 0.0},
  {"from_tier": 2, "to_tier": 3, "percentage": null}
],
"risk_reduction": null
```

**Threats-only.** JSON tier 0 is real. Tiers 1–3 are `ghost: true` with widths 90/80/70 and `count`, `volume`, `severity_mix` and `source` all `null`. All three reductions are `null`: (0→1) is null because a ghost wins over "by definition". `risk_reduction` is `null`.

**Volumes unavailable** (4-tier, no row carries an inherent score; data-model §4.3):
- Tiers 1–3 are real (`ghost: false`, counts and mixes present) with `volume: null` and widths 90/80/70.
- (0→1) = `0.0`; (1→2) and (2→3) are `null`.
- `risk_reduction`, `inherent_score` and `residual_score` are `null` on the funnel **and** the baseball card.
- One warning.

The funnel template and its skill reference (W2 Lane C2) key ghost rendering on `ghost` and the 0% note on a numeric `risk_reduction == 0.0`. B2a (emitter) and C2 (text) implement against these examples. The tester adds the 3-tier, threats-only and volumes-unavailable fixtures to the K11 set.

## `report-data.typ`

- **Emitted right after the severity-count block** (`#let critical-count …` through `#let total-findings …`):
  ```typst
  #let risk-posture-level = "high"
  #let risk-posture-label = "HIGH RISK"
  ```
- **The Typst variable contract** (`typst-template-contract.md`, "Severity Count Variables") lists both as **REQUIRED, no default**. The note is scoped to these two variables; every other group keeps its compile-cleanly defaults.
- **`main.typ` guard**, using the existing `_report-data-dict` binding. It goes **after** `#let _report-data-dict = dictionary(report-data-module)` (`main.typ:117`) and **before** `#cover-page(` (`:147`):
  ```typst
  #if not ("risk-posture-level" in _report-data-dict and "risk-posture-label" in _report-data-dict) {
    panic("report-data.typ predates the risk-posture variables. Regenerate it: re-run scripts/extract-report-data.py (or /tachi.security-report).")
  }
  ```
  Verified at plan review on Typst 0.14.2: with the wildcard import in place, the panic fires before the first reference to the missing variable, and a fresh file compiles.
- **`cover.typ`** takes `label` and `level` from data. The color comes from the level (`critical` → `severity-critical`, `high` → `severity-high`, `medium` → `severity-medium`, `low` → `severity-low`). The label is rendered verbatim, and the local `risk-posture()` derivation is removed.
- **`cover-page` fails closed too (amended at P1, 2026-10-10; T036 L-6, `da7a196`).**
  - Its `risk-posture-level` and `risk-posture-label` parameters default to `none`, not `"low"`/`"LOW RISK"`.
  - It panics, with a regenerate instruction, when either is still `none`.
  - On the shipped path the `main.typ` guard fires first, and `main.typ` passes both arguments. The function's own guard covers any other caller, which would otherwise render **LOW RISK** silently.
  - So "REQUIRED, no default" holds at both layers.
  - The harness tests compile a template copy in `tmp_path`.
- **The report-assembler deprecation note** (`report-assembler.md:184`) gains one sentence: "A hand-built `report-data.typ` without `risk-posture-level`/`risk-posture-label` no longer compiles."
- **(rev. 1, R-P5) The funnel caption** (`main.typ:292`) says that Tier 3 credits fully effective controls and Tier 4 adds partial ones. It adds: "Widths narrow by at least one step per stage for readability; the percentages are exact." This is only if K11 ships.

## Recommendations (K13.1) **(rev. 1)**

These constants live in `extract-report-data.py`:
```python
REC_FALLBACK_PREFIX = "Threat-model mitigation: "
REC_PLACEHOLDER = "No recommendation available"
```

The rule is in data-model §7:
- On **data tier 1**, the finding's `recommendation` is written once (analyzer, then prefixed mitigation, then placeholder), so the roadmap, the finding cards and the attack-path remediation (through `_get_finding_mitigation`, reused) show identical text.
- **On every data tier**, a text that resolves empty becomes `REC_PLACEHOLDER`:
  - tier 3's finding-level `mitigation` (read by all three consumers);
  - any remediation-roadmap action text.
- Tier 2's surfaces keep today's non-blank behavior.
- The prefix fallback is tier-1 only.

## Warnings **(rev. 1)**

All warnings go to stderr, in the existing `Warning: …` style, and are never fatal. **Per-row classes are aggregated** into one line per class, giving the count and the first five IDs in first-seen order (R-P6).

| Trigger | Message stem |
|---|---|
| Empty or unrecognized control status | `Warning: <n> controls rows have an unrecognized or empty status (first: <ids>); counted as no control` |
| Residual above inherent | `Warning: <n> controls rows have a residual above the inherent score (first: <ids>); clamped` |
| Missing residual, inherent present **(amended at P0, 2026-09-28: the implemented stem, `a837ae8`)** | `Warning: <n> controls rows have no residual score (first: <ids>); defaulted to the inherent score (no credit)` |
| Missing inherent after the join | `Warning: <n> controls rows have no inherent score (first: <ids>); excluded from funnel volumes` |
| Unparseable score | `Warning: <n> unparseable scores (first: <id>:<column>, …); treated as missing` |
| Volumes unavailable | `Warning: no controls row carries an inherent score; funnel volumes and risk reduction are unavailable` |
| Section 1 vs the rows. It fires when the two differ by **more than** 0.1 (data-model §4.5), compared exactly in `Decimal`, never in float **(amended at P1, 2026-10-10; T036 L-4, `819830e`)** | `Warning: controls Section 1 <field> <a> differs from row-derived <b>; using rows` (one per field) |
| Row counts **(amended at P0, 2026-09-28; RC-2)**: compared only when `risk-scores.md` is present and its Scored Threat Table yields ≥ 1 row. It reuses the tier-1 join's parse, so the existing `could not find Scored Threat Table` warning prints at most once per run, and an unreadable table is never reported as `(0)`. **On tier 2 (amended at P1, 2026-10-10; T036 L-3, `e12318b`):** the funnel reuses `extract_severity`'s own parse too, so that warning also prints at most once per run there. Tier 2 has no row-count comparison, because it has no controls rows | `Warning: controls rows (<n>) differ from risk-scores rows (<m>)` |
| Unknown delta statuses (baseline runs only) | `Warning: <n> Section 7 statuses are not NEW/UPDATED/UNCHANGED after normalization (first: <id>='<normalized>', …); not counted` |
| Empty map (baseline run with a Status column) | `Warning: threats.md Section 7 has <n> rows but no readable Finding ID/Status pairs; delta counts are 0` |
| Delta ID sets (baseline run with a Status column) | `Warning: Section 7 status IDs differ from tier finding IDs (<k> only-in-map, <j> only-in-tier)` |
| Baseline run without a Status column | `Warning: baseline run but threats.md Section 7 has no Status column; delta counts unavailable` |
| Section 4 drift | `Warning: controls Section 4 has content but no recommendations matched; using threat-model mitigations` |

**Removed with K11 (amended at P0, 2026-09-28).**
- The legacy lines are gone: `Warning: <ID> in '### <Band> Residual Severity' section but residual score <X> maps to <Band2>. Using score-derived band.` and its summary `Warning: <N> findings in wrong severity sections (corrected using score-derived bands)`.
- The row's band is always score-derived from the clamped residual, so the heading never affected output. After the clamp, the legacy check would name the raw score's band, not the one used.
- T035 attributes the removed lines to K11 (data-model §4.5).

## Sibling-parity set (`test_extraction_sibling_parity.py`)

For the same fixture and data tier, the infographic JSON and the `report-data.typ` values must be equal for:
- the posture level and label;
- the severity counts;
- the delta counts (NEW, UPDATED, UNCHANGED, resolved), including a **bracketed-status** baseline fixture (rev. 1);
- the MAESTRO layer distribution and the most-exposed layer.

The fixture carries no attack trees or chains, so the report path stays off mmdc.
