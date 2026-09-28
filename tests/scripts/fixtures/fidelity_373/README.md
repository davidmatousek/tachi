# Fixtures: Adopter Install + Output Fidelity Fixes (Feature 373, T003)

Synthetic run directories for K9, K10, K11, K12 and K13.1 (`scripts/tachi_parsers.py`,
`scripts/extract-infographic-data.py`, `scripts/extract-report-data.py`). Every
fixture uses the real templates' section order and header spellings
(`templates/tachi/output-schemas/threats.md`, `risk-scores.md`,
`compensating-controls.md`), synthetic/generic content only (NFR-6: no real
project names), and is deliberately minimal for its scenario.

**How to read this file.** Each scenario below gives: its purpose and the
requirement IDs it serves; the files it contains; and the hand-computed
expected values a test author checks the parser/extractor output against.
Where cheap, it also records what **today's** (pre-Feature-373) parser reads,
because several fixtures deliberately hit current bugs (K9, K10, K12) — that
is `tasks.md` T016's test-first evidence. All "today" values below were
collected by importing the unmodified `scripts/tachi_parsers.py` in a scratch
clone (never the main tree) and calling it directly against these files; nothing
here required running `install.sh` or the extractor CLIs.

**Numeric ground truth.** The K11 funnel arithmetic (widths, reductions,
`risk_reduction`) was independently computed with `decimal.Decimal` and
`ROUND_HALF_UP`, per data-model.md §4, rather than by hand — see the per-scenario
figures below. `STEP = 10`, `FLOOR = 30`.

**Tier detection**, confirmed against every directory below via
`detect_artifacts()` + `determine_tier()` (unchanged by Feature 373): a
directory with `compensating-controls.md` is tier 1 (4-tier funnel); with
`risk-scores.md` only, tier 2 (3-tier); with `threats.md` only, tier 3
(threats-only).

---

## controls_bands_shortform/

**Purpose**: US-3a #1 (short-form controls headers) and #2 (empty last band
before Summary Statistics). Serves K9 / FR-K9.1–K9.2.

**Files**: `compensating-controls.md` only.

**Content**: short-form Coverage Matrix headers (`Inherent`, `Status`,
`Residual`, `Residual Sev.` in place of `Inherent Score`, `Control Status`,
`Residual Score`, `Residual Severity`). The **Critical** band has no table at
all (heading with nothing under it), and the **Low** band likewise has no
table and sits directly before `### Summary Statistics`. High and Medium each
carry one real row.

**Expected values** (post-fix, `normalize_header` + `HEADER_ALIASES` +
level-aware stop rule in place):
- exactly **2** findings: `T-1` (High, inherent 8.0, residual 8.0, No Control
  Found) and `T-2` (Medium, inherent 6.5, residual 4.5, Control Found);
- severity totals: critical 0, high 1, medium 1, low 0, total 2 — matching the
  `### Summary Statistics` table verbatim;
- the alias map resolves `Inherent` → inherent score, `Status` → control
  status, `Residual` → residual score, `Residual Sev.` → residual severity.

**Today's (pre-fix) read, collected as evidence**: `parse_markdown_table`'s
stop rule only recognizes a literal `"## "` or `"# "` line prefix, which a
`"### …"` heading never matches. Querying `"### Critical Residual Severity"`
therefore scans straight through the empty Critical section, past
`"### High Residual Severity"`, and returns **High's own row** as if it were
Critical's (the "adopts the next band's table" bug). Querying
`"### Low Residual Severity"` similarly scans past the empty Low heading and
into `"### Summary Statistics"`, misreading its 5-row table (Critical/High/
Medium/Low/Total counts) as Low findings — "phantom rows" whose `Threat ID`
comes up empty (the Summary table's first column is `Residual Severity`, not
`Threat ID`). Confirmed count today: **7** rows returned (`T-1`, `T-2`, plus 5
phantom empty-ID rows), vs. the correct **2**.

---

## maestro_heading_h3/

**Purpose**: US-3a #4 (a `###` MAESTRO heading). Serves K10 / FR-K10.1.

**Files**: `threats.md` only.

**Content**: Section 6 uses `### Risk by MAESTRO Layer` (3 hashes) instead of
the canonical `####` (4 hashes), with 2 rows: `L1 — Foundation Model` (3
findings, Critical) and `L4 — Deployment Infrastructure` (2 findings, High).

**Expected values** (post-fix, `match_heading` with `^#{3,4}\s+Risk by
MAESTRO Layer`): layer distribution = `[{layer: "L1 — Foundation Model",
finding_count: 3, highest_severity: "Critical"}, {layer: "L4 — Deployment
Infrastructure", finding_count: 2, highest_severity: "High"}]`; most-exposed
layer = `L1 — Foundation Model` (Critical outranks High).

**Today's (pre-fix) read, collected as evidence**: both extractors call
`parse_markdown_table(threats_content, "#### Risk by MAESTRO Layer")` — an
exact 4-hash substring. Against this fixture's literal 3-hash heading, that
call returns **0 rows** (confirmed). The same file parsed with the literal
3-hash substring returns the 2 rows correctly, confirming the fixture's shape
is sound and the only defect is today's heading-level rigidity.

---

## baseline_resolved_4c/ and baseline_resolved_4b_legacy/

**Purpose**: US-3a #5 (a `## 4c.` baseline with known NEW/UPDATED/UNCHANGED
and resolved counts, plus one placeholder row) and #6 (the legacy `## 4b.`
twin yields the same resolved count); N6 (bracketed statuses). Serves K12 /
FR-K12.1–K12.5.

**Files**: `threats.md` only, in each directory.

**Content** (`baseline_resolved_4c/`): `has_baseline = true`. Section 7 has 6
findings whose Status column deliberately mixes every bracketed spelling N6
must normalize to `NEW`: `F-1` = `NEW` (bare), `F-2` = `[NEW]`, `F-3` =
`**[NEW]**`, `F-4` = `` `[NEW]` ``, `F-5` = `UPDATED`, `F-6` = `UNCHANGED`.
`## 4c. Resolved Findings` has 3 rows: `F-7` and `F-8` (real), plus one
placeholder row (`ID` = `—`, an em dash) that `is_placeholder_id` must skip.

**Content** (`baseline_resolved_4b_legacy/`): same baseline shape, under the
legacy `## 4b. Resolved Findings` heading, with the identical 3 resolved rows
(2 real + 1 placeholder) but a smaller, non-bracketed Section 7 (`F-1`,
`F-5`, `F-6`) since the bracket-normalization variety is already covered by
the 4c twin — this directory exists only to prove the resolved count agrees
across headings.

**Expected values** (post-fix, `normalize_delta_status` + `compute_delta_counts`
+ `match_heading` for `^##\s+4[bc]\.\s+Resolved Findings\s*$`):
- `baseline_resolved_4c/`: `delta_counts = {new: 4, updated: 1, unchanged: 1,
  resolved: 2}` (F-1..F-4 all normalize to `NEW`; the placeholder row is
  excluded from `resolved`, which is **2**, not 3);
- `baseline_resolved_4b_legacy/`: `delta_counts = {new: 1, updated: 1,
  unchanged: 1, resolved: 2}` — the **same resolved count (2)** as the 4c
  twin, proving heading-spelling parity.

**Today's (pre-fix) read, collected as evidence**: `parse_resolved_findings`
matches only the literal substring `"## 4b. Resolved Findings"`, so today it
finds **0** rows in `baseline_resolved_4c/` (the 4c heading isn't matched at
all) and **3** rows in `baseline_resolved_4b_legacy/` (today has no
placeholder-skip in that path either, so the placeholder row is *not*
excluded — resolved comes back as 3, not 2). `compute_delta_counts` today
reads the RAW (non-normalized) `Status` cell text directly, so `F-2`/`F-3`/
`F-4`'s bracketed spellings are counted under `"unchanged": 0`-style buckets
that never match `"NEW"` (today's counts on the 4c file: `{new: 1, updated:
1, unchanged: 1, resolved: 0}` — only the bare `F-1` is recognized as `NEW`;
the three bracketed variants are silently dropped from every bucket).

---

## baseline_status_id_mismatch/

**Purpose**: US-3a #7 (a baseline run whose Section 7 status map has an ID
set that differs from the tier's finding IDs — warns). Serves K12 / FR-K12.2,
architect finding F1 / re-review NM-1.

**Files**: `threats.md` (the map) + `compensating-controls.md` (the tier-1 ID
set).

**Content**: Section 7 carries `A-1` (NEW), `A-2` (UNCHANGED), `A-3`
(UPDATED) — map ID set = `{A-1, A-2, A-3}`. The controls report's Coverage
Matrix carries `A-1`, `A-2`, `A-4` — tier-1 ID set = `{A-1, A-2, A-4}`. `A-3`
is a map-only ID; `A-4` is a tier-only ID.

**Expected values**: `warn_delta_scope` emits the ID-set warning
`"Section 7 status IDs differ from tier finding IDs (1 only-in-map, 1
only-in-tier)"`. `delta_counts` are still computed over the **normalized
Section 7 map**, unrestricted by the tier's ID set (FR-K12.1/K12.2, NM-1):
`{new: 1, updated: 1, unchanged: 1, resolved: 0}`.

**Today's (pre-fix) read, collected as evidence**: `compensating-controls.md`
parses cleanly to its intended 3 rows (`A-2`, `A-1`, `A-4`) with today's
parser — the empty Critical/High headings were deliberately removed from this
file (they aren't part of this scenario) precisely to avoid incidental
contamination from the unrelated K9 stop-rule bug (see `controls_bands_shortform/`
above for that bug in isolation). `threats.md`'s raw Status values read today
as `['NEW', 'UNCHANGED', 'UPDATED']` with no ID-set cross-check at all (that
check does not exist pre-K12).

---

## non_baseline_no_status_column/

**Purpose**: US-3a #7 (second half): a run without a baseline, or whose
Section 7 has no Status column, must not emit the ID-set warning. Serves K12
/ FR-K12.2 scope guard.

**Files**: `threats.md` only.

**Content**: `has_baseline = false`; Section 7 omits the `Status` column
entirely (`Finding ID | Category | Pattern | Component | MAESTRO Layer |
Threat | Risk Level | Mitigation`), matching the real
`maestro-reference`/`mobile-banking-app` shape data-model.md §6 cites.

**Expected values**: `has_status_column = False`, `has_baseline = False` →
`warn_delta_scope` fires **neither** the ID-set warning nor the empty-map
warning (both require `has_baseline AND has_status_column`). `delta_counts =
{new: 0, updated: 0, unchanged: 0, resolved: 0}` (no map to count).

---

## recommendations_partial_join/ and recommendations_drifted/

**Purpose**: US-3a #8 (a controls Section 4 that covers only some findings)
and #9 (a drifted Section 4: content present, zero joins). Serves K13.1 /
data-model.md §7.

**Files**: `threats.md` + `compensating-controls.md`, in each directory.

**`recommendations_partial_join/` content**: 3 tier-1 findings. Controls
Section 4 covers only `T-1`. `T-2` has a non-empty Section 7 Mitigation;
`T-3`'s Section 7 Mitigation is empty.

**Expected values** (data-model.md §7 precedence: analyzer recommendation →
prefixed Section 7 mitigation → placeholder):
- `T-1.recommendation` = `"Implement per-tenant rate limiting and a Web
  Application Firewall rule set at the API Gateway ingress to absorb
  volumetric requests before they reach backend services."` (verbatim from
  Section 4's `**What to Implement**:` line, since it's covered);
- `T-2.recommendation` = `"Threat-model mitigation: Apply rate limiting at
  the ingress."` (`REC_FALLBACK_PREFIX` + Section 7 mitigation);
- `T-3.recommendation` = `"No recommendation available"` (`REC_PLACEHOLDER`
  — neither source has text);
- no Section 4 drift warning (at least one join succeeded).

**`recommendations_drifted/` content**: 2 tier-1 findings (`T-1`, `T-2`).
Controls Section 4 has one full recommendation block, but for ID `Z-9` —
which does not appear among the tier-1 rows at all.

**Expected values**: the recommendations dict is `{"Z-9": "..."}`, so **zero**
of `T-1`/`T-2` join → the Section 4 drift warning fires (`"controls Section 4
has content but no recommendations matched; using threat-model mitigations"`).
`T-1.recommendation` = `"Threat-model mitigation: Restrict admin endpoints to
VPN access"` (Section 7 fallback, verbatim — the source Mitigation cell carries
no trailing period, and the prefix concatenation adds none); `T-2.recommendation`
= `"No recommendation available"` (Section 7 mitigation is empty too).

**Note**: both directories originally included a trailing, empty
`### Low Residual Severity` heading directly before `### Summary Statistics`
for template-order fidelity; it was removed after the self-check (below)
showed it incidentally re-triggered the unrelated K9 empty-band bug under
today's parser (5 phantom rows), which would have muddied these two K13.1-only
fixtures. Neither band-emptiness scenario is part of these two directories'
purpose — that is `controls_bands_shortform/`'s job alone. Confirmed clean
today (2 and 3 real rows respectively, no phantoms) after the fix.

---

## recommendations_tier3_empty_mitigation/ (T019 addition)

**Purpose**: data-model.md §7's tier-3 row — "an empty `mitigation` becomes
the placeholder on the card, the roadmap and the attack path" — which no
existing fixture covered (T003's list only named tier-1 K13.1 scenarios).
Serves K13.1 / FR-K13.1, tier 3.

**Files**: `threats.md` only (no `risk-scores.md`, no
`compensating-controls.md` → `determine_tier` selects tier 3).

**Content**: 2 Section 7 findings, `has_baseline = false`. `T-1` carries a
real Mitigation cell; `T-2`'s Mitigation cell is empty.

**Expected values** (post-K13.1, resolved once in `main()` on the finding's
own `mitigation` field, per data-model.md §7 — the card, the roadmap
(`build_remediation_actions`) and the attack path (`_get_finding_mitigation`
+ `_build_remediation`) then all read that same resolved field rather than
each applying their own empty-check):
- `T-1.mitigation` = `"Apply per-IP rate limiting at the gateway"` (verbatim,
  unchanged);
- `T-2.mitigation` = `"No recommendation available"` (`REC_PLACEHOLDER`).

**Today's (pre-fix) read, collected as evidence**: `parse_threats_findings`
already reads `mitigation` straight from the table with no placeholder
guard, so `T-2.mitigation` comes back as `""` (confirmed) and stays that way
through every consumer until K13.1's `main()`-level resolution lands.

---

## funnel_step_bound/, funnel_strong_reduction/, funnel_3tier/, funnel_threats_only/, funnel_volumes_unavailable/

**Purpose**: US-3b #1–#3, #7, #8 — the five K11 funnel shapes tasks.md T003
calls out by name. Serves K11 / FR-K11.1–K11.5.

All widths/reductions below were computed with `decimal.Decimal` and
`ROUND_HALF_UP` exactly per data-model.md §4 (`STEP = 10`, `FLOOR = 30`); see
`scripts/tachi_parsers.py`'s eventual `compute_risk_funnel` (T021).

### funnel_step_bound/ (`threats.md` + `compensating-controls.md`)

Two rows: `T-1` (inherent 8.0, **Control Found**, residual 7.9) and `T-2`
(inherent 8.0, **Partial Control**, residual 7.8).

- Tier-3 per-row score: `T-1` is `found` → uses residual (7.9); `T-2` is
  `partial` (not `found`) → uses inherent (8.0).
- `V2 = 16.0`, `V3 = 15.9`, `V4 = 15.7`.
- **Widths: 100 / 90 / 80 / 70** — both raw ratios (`raw3 = 89.4375`,
  `raw4 = 88.3125`) exceed their upper clamp bounds (80, 70 respectively), so
  both are STEP-bound (bound by "at least one step narrower per stage"), not
  by their own ratio.
- Reductions: `(0→1) = 0.0`, `(1→2) = 0.6`, `(2→3) = 1.3`.
- `risk_reduction = 1.9`.

### funnel_strong_reduction/ (`threats.md` + `compensating-controls.md`)

Two rows: `T-1` (inherent 5.0, **Control Found**, residual 1.0) and `T-2`
(inherent 5.0, **Partial Control**, residual 2.0). Same volume *ratios* as the
extraction-data-contract's own pinned example (`V2=100, V3=60, V4=30 → widths
100/90/54/30`), scaled by 0.1 so real 0.0–10.0 composite scores can produce
them.

- `V2 = 10.0`, `V3 = 6.0` (`T-1` found → residual 1.0; `T-2` partial → inherent
  5.0; sum 6.0), `V4 = 3.0`.
- **Widths: 100 / 90 / 54 / 30** — `raw3 = 54` and `raw4 = 27`; `27` is below
  its lower clamp bound (`FLOOR = 30`), so Tier 4 is **FLOOR-bound**.
- Reductions: `(0→1) = 0.0`, `(1→2) = 40.0`, `(2→3) = 50.0`.
- `risk_reduction = 70.0`.

### funnel_3tier/ (`threats.md` + `risk-scores.md`, no `compensating-controls.md`)

Tier 2 (composite-score) run: `T-1` composite 8.0, `T-2` composite 6.0 →
`V2 = 14.0`. `determine_tier` selects tier 2 (3-tier funnel mode).

- JSON tier-index 2 ("Unmitigated Risk") mirrors Tier 2's own volume: `14.0`.
- **Widths: 100 / 90 / 80 (real) / 70 (ghost)** — the JSON tier-index-2 width
  formula uses `V3/V2 = 1.0` exactly, so `raw3 = 90`, clamped down to its
  upper bound `80` regardless of `V2`'s actual value.
- Reductions: `(0→1) = 0.0`; `(1→2) = 0.0` ("V3 = V2" by the 3-tier rule);
  `(2→3) = null` (JSON tier-index-3 is a ghost).
- `risk_reduction = null` (§4.4: null in 3-tier mode).

### funnel_threats_only/ (`threats.md` only)

No `risk-scores.md`, no `compensating-controls.md` → `determine_tier` selects
tier 3. Tier 1 is real (2 Section 7 findings); JSON tiers 1–3 (indices 1, 2,
3) are all `ghost: true`.

- **Widths: 100 / 90 (ghost) / 80 (ghost) / 70 (ghost)** — pure STEP cascade.
- All three reductions are `null` (`(0→1)` is null because "a ghost wins over
  'by definition'").
- `risk_reduction = null`.

### funnel_volumes_unavailable/ (`threats.md` + `compensating-controls.md`, no `risk-scores.md`)

The Coverage Matrix table has **no** `Inherent Score` / `Inherent` column at
all (columns: `Threat ID | CF | Component | Threat | Control Status |
Residual Score | Residual Severity`), and no `risk-scores.md` sits alongside
it, so no ID join is possible. No row in the one row set carries an inherent
score → `V2` has no terms (data-model.md §4.3, condition 1: "no row carries an
inherent score").

- `volume` is **null on every tier**; `(1→2)` and `(2→3)` are **null**;
  `(0→1) = 0.0` still holds (Tier 1 is real).
- `risk_reduction`, `inherent_score`, `residual_score` are **null on both the
  funnel and the baseball card**.
- **Widths still follow the plain STEP cascade: 100 / 90 / 80 / 70** (§4.1:
  "unavailable volumes (with a warning): `W_k = W_{k-1} - STEP`" — these
  tiers are real/non-ghost, just volumeless).
- One warning: `"Warning: no controls row carries an inherent score; funnel
  volumes and risk reduction are unavailable"`.
- (Not built here, but easy to construct if a future test needs it:
  §4.3's *second* volumes-unavailable precondition, `V2 == 0.0` despite every
  row carrying an `Inherent Score` of exactly `0.0` — this fixture only
  covers precondition 1, "no column at all".)

---

## funnel_join_inherent_less/

**Purpose**: US-3b #6 (a controls row with no inherent score is filled from
the risk-scores composite with the same ID). Serves K11 / architect finding
F2, the K11 carve unit's join-path parity case (also consumed by
`test_extraction_sibling_parity.py` per T019).

**Files**: `threats.md` + `risk-scores.md` + `compensating-controls.md`.

**Content**: the Coverage Matrix table has no `Inherent Score` / `Inherent`
column at all. `risk-scores.md` supplies composites for the same two IDs:
`T-1 = 8.0`, `T-2 = 7.0`. `T-1` is `Control Found` (residual 7.5, High);
`T-2` is `Partial Control` (residual 6.6, Medium) — each row sits under the
Coverage Matrix band heading matching its **own** residual-derived severity
(High, then Medium), so today's pre-K11 heading/score cross-check does not
fire a spurious "misclassified" warning unrelated to this scenario.

**Expected values**: `parse_compensating_controls_md(content,
composites_by_id={"T-1": Decimal("8.0"), "T-2": Decimal("7.0")})` fills
`inherent` by ID join for both rows (F2).
- Tier-3 per-row score: `T-1` found → residual 7.5; `T-2` partial → inherent
  (joined) 7.0.
- `V2 = 15.0`, `V3 = 14.5`, `V4 = 14.1`.
- **Widths: 100 / 90 / 80 / 70** (`raw3 = 87`, `raw4 = 84.6`, both above their
  upper bounds, both STEP-bound).
- Reductions: `(0→1) = 0.0`, `(1→2) = 3.3`, `(2→3) = 2.8`.
- `risk_reduction = 6.0`.
- Sibling parity (T019): both the funnel JSON and `report-data.typ` must
  agree on the clamp, the residual bands, the severity counts and the
  posture, all derived from this same joined row set.

**Today's (pre-fix) read, collected as evidence**: today's
`parse_compensating_controls_md` has no `composites_by_id` parameter and no
"Inherent" column read path at all — it returns the 2 rows with
`residual_score` populated (`7.5`, `6.6`) but no `inherent`/`inherent_score`
concept; there is nothing to join today, which is exactly the gap K11 closes.

---

## controls_warnings_kitchen_sink/

**Purpose**: the five remaining T003 bullets, deliberately combined in one
run directory since they are all just different rows/values in the same
table structure (a realistic controls report mixes good and bad rows):
control-status variants (`Missing`, empty, unrecognized, `Partially Found`,
`None found`), unparseable scores (`—`, `8.5 (High)`, `NaN`), residual above
inherent, a Section 1 comparand mismatch, and a controls/risk-scores
row-count mismatch. Serves K9 (`parse_score`), K11 (`classify_control_status`,
the clamp, the join-miss path) and data-model.md §4.5's warning classes.

**Files**: `threats.md` + `risk-scores.md` + `compensating-controls.md`.

**The ten rows** (`W-1`..`W-10`), by `classify_control_status` outcome in
application order (partial-prefix → silent whole-string → found-with-no-negation
→ else-warns):

| ID | Status cell | Classification | Warns? | Inherent | Residual (raw) |
|----|---|---|---|---|---|
| W-1 | `Missing` | `none` | no (whole-string silent set) | 6.0 | 6.0 |
| W-2 | *(empty)* | `none` | **yes** | 5.5 | 5.5 |
| W-3 | `Foobar` | `none` | **yes** | 4.5 | 4.5 |
| W-4 | `Partially Found` | `partial` (prefix rule wins) | no | 7.0 | 5.5 |
| W-5 | `None found` | `none` (contains "found" **and** the negation token "none") | **yes** | 5.0 | 5.0 |
| W-6 | `Control Found` | `found` | no | 8.0 | `—` (unparseable) |
| W-7 | `No Control Found` | `none` (whole-string silent set) | no | 7.2 | `8.5 (High)` (unparseable) |
| W-8 | `Partial Control` | `partial` | no | `NaN` (unparseable/non-finite) | 5.0 |
| W-9 | `No Control Found` | `none` | no | 8.0 | `9.5` (parseable, > inherent) |
| W-10 | `Control Found` | `found` | no (clean anchor row) | 6.5 | 3.0 |

**Expected warnings** (data-model.md §4.5, each aggregated to one line):
- unrecognized-or-empty status: **2** rows (`W-2`, `W-3`, `W-5`; first-seen
  IDs in that order) — note `W-5`'s inclusion here even though "None found"
  reads as a negative on its face: it fails the whole-string silent-set match
  (`"none found"` ≠ any of `"no control found"/"missing"/"none"/"not found"`)
  and fails the found-with-no-negation rule (it contains the negation token
  `"none"`), so it falls to the warning bucket by construction, exactly as
  data-model.md §3 calls out explicitly;
- unparseable score: **3** occurrences (`W-6:residual`, `W-7:residual`,
  `W-8:inherent`) — `parse_score` must reject `"—"` (`InvalidOperation`),
  `"8.5 (High)"` (`InvalidOperation`, trailing text), and `"NaN"` (parses as a
  `Decimal` but is rejected for being non-finite, per K9's explicit
  `NaN`/`Infinity` rule);
  the recorded name is `"NaN"`, capital N-a-N (`Decimal("NaN")` succeeds; only
  the finiteness check rejects it — do not confuse this with a parse
  failure);
- missing residual → defaults to inherent, no credit: **2** rows (`W-6`
  residual becomes `8.0`; `W-7` residual becomes `7.2`) — both stem from the
  same cells the unparseable-score warning already named;
- missing inherent after the join: **1** row (`W-8`; no `risk-scores.md`
  entry exists for `W-8` — see the row-count-mismatch note below — so the
  join cannot fill it either; `W-8` is excluded from `V2`/`V3`/`V4`);
- residual above inherent, clamped: **1** row (`W-9`; raw residual `9.5` >
  inherent `8.0`, clamped to `8.0`, band **High** post-clamp — this fixture
  deliberately places `W-9` under the `### High Residual Severity` heading
  and gives its `Residual Severity` column `High` too, i.e. *already* the
  post-clamp band, so today's separate legacy "heading vs. raw-score" check
  (see below) is the only thing that disagrees, not this fixture's own
  design);
- Section 1 comparand, **two separate field warnings** (not aggregated —
  §4.5 is explicit that this class is "per field, not aggregated"): the
  stated inherent total (`60.0`) differs from the row-derived total (`57.7`,
  computed below); the stated reduction (`26.9%`) differs from the
  row-derived reduction (`8.7%`). The stated **residual** total (`52.7`)
  is deliberately left matching the row-derived value exactly, so the
  residual field must **not** warn — proving the granularity is genuinely
  per-field;
- row-count mismatch: controls has **10** rows, `risk-scores.md` has **11**
  (`W-1..W-7, W-9, W-10` = 9, matching, plus `W-11` and `W-12`, scored but not
  yet analyzed for controls; `W-8` has no `risk-scores.md` entry by design, so
  its join-miss above is preserved) → `"Warning: controls rows (10) differ
  from risk-scores rows (11)"`.

**Row-derived funnel arithmetic** (9 rows carry an inherent value; `W-8` is
excluded from all three volumes, per data-model.md §4.1's "over rows with
inherent"):
- `V2 = 57.7` (sum of the 9 inherents), `V3 = 54.2`, `V4 = 52.7`.
- Widths: 100 / 90 / 80 / 70 (`raw3 = 84.5…`, `raw4 = 82.2…`, both
  STEP-bound).
- Reductions: `(0→1) = 0.0`, `(1→2) = 6.1`, `(2→3) = 2.8`.
- `risk_reduction = 8.7` — this is the value the Section 1 comparand warning
  above measures against.

**A documented open nuance for the implementer** (not a defect in this
fixture — flagging it because the ambiguity is real and this exact row was
chosen to surface it): data-model.md §4.1 says a tier's `severity_mix`
excludes "rows missing a band" for *that* tier only, while the volumes
(`V2`/`V3`/`V4`) are explicitly "over rows with inherent". `W-8` has no
inherent (excluded from all volumes) but *does* have a parseable residual
(`5.0`, band Medium) and a parseable Tier-3-relevant status (`partial`, so its
Tier-3 score would be its — absent — inherent). Whether `W-8` should still
contribute to the Tier 4 `severity_mix` (its `residual_band` exists) even
though it is excluded from `V4` (the volume), is a judgment call data-model.md
does not spell out row-by-row; this fixture exists so T020/T023 can decide it
deliberately rather than by accident.

**Today's (pre-fix) read, collected as evidence**: today's parser already
runs its own (different, legacy) "row vs. heading" cross-check based on the
*raw* score, independent of any future clamp. It fires exactly once here:
`"Warning: W-9 in '### High Residual Severity' section but residual score 9.5
maps to Critical. Using score-derived band."` — i.e. today's code reassigns
`W-9`'s severity to **Critical** (from the raw 9.5), not the post-clamp
**High** this fixture's design assumes. This is expected and is exactly the
kind of pre-existing behavior K11's clamp-then-band rule supersedes (band
comes from the clamped value uniformly, so the raw-vs-heading question this
legacy check asks should no longer arise — data-model.md's new §4.5 warnings
table has no equivalent "heading mismatch" class). Today's Section 1 regex
read (`inherent_score`/`residual_score`/`risk_reduction`) returns exactly the
stated, deliberately-wrong values (`60.0`/`52.7`/`26.9`) verbatim — it has no
concept of a row-derived comparison yet, so no warning fires pre-K11 either.

---

## posture_mmdc_free/

**Purpose**: LOW-9 — an mmdc-free run directory `test_report_posture_contract.py`
(T025) can feed to `scripts/extract-report-data.py` to generate a fresh
`report-data.typ` without `mmdc` installed, for the stale-data gate's positive
control. Serves K13-posture / FR-K13.4–K13.5.

**Files**: `threats.md` + `risk-scores.md` + `compensating-controls.md`. No
`attack-chains.md`, no `attack-trees/` directory, and no finding's Mitigation
text embeds a Mermaid block, so nothing in this directory needs `mmdc` to
render.

**Content**: 3 tier-1 findings spanning all three non-zero bands: `T-1`
(residual 8.0, **High**), `T-2` (residual 5.0, **Medium**), `T-3` (residual
2.5, **Low**).

**Expected values** (data-model.md §5, post-clamp residual counts since K11
ships): residual severity counts are `{critical: 0, high: 1, medium: 1, low:
1}` → the highest band present is **High** → `risk_posture_level = "high"`,
`risk_posture_label = "HIGH RISK"`. Both the infographic JSON's
`metadata.risk_posture_{level,label}` and `report-data.typ`'s `#let
risk-posture-level` / `#let risk-posture-label` must agree on this pair.

---

## Self-check performed for this task

All 16 scenario directories were copied into a scratch clone
(`git clone --no-hardlinks` of `main` at `0ce39d0`, never the main tree) and
parsed with the **unmodified** `scripts/tachi_parsers.py` to confirm: (a) no
file raises on any existing parser function; (b) `detect_artifacts` +
`determine_tier` select the intended tier for every directory (confirmed:
tier 1 for every directory with a `compensating-controls.md`, tier 2 for
`funnel_3tier/`, tier 3 for the three `threats.md`-only directories); (c) the
K9/K10/K12 "today's read" evidence quoted above. Two real defects this
self-check caught and fixed before this hand-off: `funnel_join_inherent_less/`
originally placed both rows under one `### High Residual Severity` heading
despite `T-2`'s residual scoring Medium (fixed by splitting `T-2` into its own
`### Medium Residual Severity` block); `recommendations_partial_join/`,
`recommendations_drifted/` and `baseline_status_id_mismatch/` each had one or
two empty band headings left over from copy-paste that incidentally
re-triggered the K9 stop-rule bug under today's parser, contaminating results
unrelated to those fixtures' own purpose (fixed by removing the unused empty
headings).

---

## `tests/scripts/install_sh_helpers.py`

Symlink sandbox **builders** for the K3 installer tests (`contracts/installer-cli.md`
§ "Test harness contract"), committed separately from this fixtures directory
(LOW-3: the builder commit can be cherry-picked alone, since `install_sh_helpers.py`
does not exist on `main`). Full usage is documented inline (module + per-function
docstrings); in short:

- `build_source_tree(root, entries=..., extra_files=...)` and
  `build_project_tree(root)` build a minimal synthetic tachi-like clone and an
  empty target project (the "no-link project" baseline) respectively;
- `add_symlink`, `add_nested_symlink`, `add_dangling_symlink`,
  `add_looping_symlink`, `build_symlink_chain` (parametrized hop count, for
  the 40-resolves/41-unresolvable boundary), and `add_wrong_type_symlink`
  cover the generic link classes;
- `add_symlink_into_source_clone`, `add_symlink_to_source_clone_parent`,
  `vendor_source_tree_inside_project` (a real, non-symlink nested clone —
  data-model.md §2.2's "no link at all" case) and
  `add_dangling_deprecated_command_link` (using the same
  `DEPRECATED_COMMANDS` tuple as `scripts/install.sh`) cover the
  containment- and cleanup-specific classes;
- `filesystem_is_case_sensitive` and `case_variant_path` /
  `add_case_variant_symlink_to_source_clone` cover the rev-2 macOS-only
  case-sensitivity probe and case-variant link/path cases (AR-1).

**Self-check performed**: imported the module with plain `python3` (never
pytest, never against the main tree) from this session's scratchpad and built
one instance of every sandbox into a fresh tmp dir, then inspected each with
`find`/`ls -la`/`readlink` and small resolution probes. Confirmed, among
other things: the 40-hop chain resolves to its terminal target while the
41-hop chain does not; the wrong-type builder produces a real file when
`need="dir"` and a real directory when `need="file"`; `clone_parent/templates/tachi`
resolves (via `os.path.realpath`) to the exact same path as the source root
itself, reproducing the contract's own `templates -> ..` example; the
vendored-clone builder produces a real nested directory with no symlink
anywhere in its chain; and the case-sensitivity probe correctly reported
`False` (case-insensitive) on the local macOS/APFS volume, with
`case_variant_path` flipping `tachi` to `TACHI` as expected.
