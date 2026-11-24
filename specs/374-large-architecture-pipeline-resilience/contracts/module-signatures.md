# Contract: frozen module signatures for W2

> Normative for F-374. Frozen at W1 (2026-11-22, T023) under ADR-050 D5, and ADR-050 governs where this file and the ADR disagree. W2's lanes code to these names, parameters and return shapes:
> - R1b writes `tachi_scoring_rules.py` (T042–T044);
> - P writes the new `tachi_parsers` functions (T033, T048, T142, T143);
> - R1, C, R2, R3a and D call these functions, or write the formats below.

**The freeze.**
- Additive changes keep it: a new keyword argument with a default, or a new dataclass field or dict key with a default, added last. The owning lane names each one in its commit message.
- A rename, removal, reorder or type change needs an architect amendment to this file.
- **Additions ruled at W2 (2026-11-23), all additive:** `BaselineRow.component`, `.threat` and `.risk_level`; `ScorerRouting.status`; `route_scorer_units(..., lacking=None)`; `parse_markdown_table`'s `row_lines` and `keep_bold` (lane P's, recorded here); and `sarif_common.resolve_explicit`. The scorer's closed flag vocabulary gains four strings.
- **Additions ruled at the P0 checkpoint (2026-11-23, T061), all additive:** `BaselineResolution.file_reasons` (R1b's, named in T042's commit and recorded here, P0-12); `parse_sarif_member_set(..., with_details=False)` (P0-3); `tachi_parts.forbidden_character` (P0-4); and `"3a"` among `VectorCheck.step`'s values (P0-2). The comments on `BaselineRow.tags_used` and `.scored_on` now read "whenever §6 records them" (P0-2), which widens what the reader fills without changing a type.
- **Additions ruled at W3 (2026-11-23), from P0-6 and the PM's W3 ruling 1, all additive:** `VectorCheck.assessed`, last, defaulting to `None`. `peer_divergence` keeps its signature and now also serves NEW and UPDATED peers. The controls `matrix_row`'s form is pinned in the persisted-inputs format below, with no change to a type.
- **From the W3 sweep (2026-11-23), also additive:** `parse_sarif_member_set`'s return gains `details` only with `with_details=True`, and each entry carries `kind` too (FX0, named in `7d133c6`); `match_heading` gains `outside_fences=False`, keyword-only (from T087's observation). The fallback risk label is pinned under `details`, with no new function.
- **From W3's closing sweep (2026-11-23), also additive, each recorded below from W3's code:**
  - `tachi_parts.MATRIX_ROW_CELLS`, `matrix_row_cells`, `RECOMMENDATION_KEYS` and `EFFORT_LEVELS`, with the two controls checks that step 9 runs (FX0c, named in `c6ee943`);
  - `sarif_common.RULES`, `taxonomy_name_for`, `build_rules` and `COPIED_TEXT_PROPERTIES`, `build_driver(..., version=None)` and `self_check`'s evidence-URI guard (R3a, named in `d0277a3`), and the RESOLVED scan's skip list (`b9b4962`, W3 ruling Q9).

  W3's rulings d had already recorded `COUNT_KEYS`' `cell_overwrites` and `forbidden_character`'s lone surrogate. No name is renamed or removed.

**Shared conventions.**
- Every module has `from __future__ import annotations` and runs on Python 3.9 (S-11). Annotations use `typing` forms, so nothing here needs 3.10.
- Every finding ID passed in or returned is canonical (`tachi_parts`, ADR-050 D3), and passes the allow-list before any other use. Sequences of IDs are in S-2 order unless stated otherwise.
- No float enters stored-value arithmetic: scores are `Decimal` (D5). No function reads the clock, so dates are parameters.
- Content problems never raise. They come back as flags (`kind:field:cause`, D9), issues or reasons. Each exception to this is listed with its function.

## `scripts/tachi_scoring_rules.py` (lane R1b, W2)

It imports only the standard library, `tachi_scoring`, `tachi_parsers` and `tachi_parts`. It never imports `sarif_common`, an entry script or `yaml`, and it reads only the paths its callers pass (D5).

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Callable, Mapping, Optional, Sequence, Tuple

BASELINE_FILE_NAMES: Tuple[str, ...] = (
    "threats.md", "risk-scores.md", "risk-scores.sarif",
    "compensating-controls.md", "compensating-controls.sarif",
)
```

### R-6: the baseline resolver (T042, first)

```python
@dataclass(frozen=True)
class PathCheck:
    path: Optional[Path]    # set when every check passes
    reason: Optional[str]   # set when path is None

def check_run_file(candidate: Optional[str], *, cwd: Path, expected_name: str) -> PathCheck: ...

@dataclass(frozen=True)
class BaselineResolution:
    run_dir: Optional[Path]
    origin: Optional[str]       # "flag" | "baseline.source"
    files: Mapping[str, Path]   # each BASELINE_FILE_NAMES entry in run_dir that passes check_run_file
    reason: Optional[str]       # why run_dir is None; the stage record carries it
    file_reasons: Mapping[str, str] = field(default_factory=dict)  # T042: each BASELINE_FILE_NAMES entry not in files -> why check_run_file failed it; {} when run_dir is None

def resolve_baseline(*, flag: Optional[str], baseline_source: Optional[str], cwd: Path) -> BaselineResolution: ...
```

- **`check_run_file`** applies D9's checks (NFR-10, KB 24). The candidate must name a regular file called `expected_name`, no component may be a symlink, and it must lie under `cwd` by `os.path.samefile` identity.
  - Its reasons are `absent`, `free-text`, `wrong-name`, `missing`, `symlink`, `not-regular-file` and `outside-working-directory`.
  - The controls planner also calls it on `risk-scores.md`'s `source_file`, with `expected_name="threats.md"` (D8, D9).
- **`resolve_baseline`.** `flag`, the command's `--baseline`, comes first, and a file path counts as its directory. Otherwise `baseline_source` applies: the input `threats.md`'s `baseline.source`, as `parse_baseline_frontmatter` reads it, which must pass `check_run_file(..., expected_name="threats.md")`. Free text, an unresolvable path or a failed check gives `run_dir=None` with the reason, and the stage scores fresh.

### R-26: the tolerant reader (T042, first)

```python
@dataclass(frozen=True)
class InputIssue:
    finding_id: Optional[str]   # None for a file-level issue
    field: str
    cause: str
    detail: str

@dataclass(frozen=True)
class BaselineRow:
    finding_id: str
    form: str                                        # "renderer" | "legacy"
    cvss_vector: Optional[str]
    vector_source: Optional[str]                     # "md" | "sarif"
    score_bounds: Optional[Tuple[Decimal, Decimal]]  # renderer form only
    subscores: Optional[Mapping[str, int]]           # by the eight bare sub-score names; renderer form only
    zone: Optional[str]
    trust_level: Optional[str]
    auth_barriers: Optional[int]
    network_boundaries: Optional[int]
    tags_used: Optional[Tuple[str, ...]]             # whenever §6 records them (P0-2); None means no tags were recorded
    scored_on: Optional[date]                        # whenever §6 records them (P0-2)
    stored: Mapping[str, Optional[Decimal]]          # cvss_base, exploitability, scalability, reachability, composite
    band: Optional[str]
    owner: Optional[str]
    sla: Optional[str]                               # as written, such as "24h" or "7d"
    disposition: Optional[str]
    review_date: Optional[date]
    narrative: Mapping[str, str]                     # renderer form: field path -> decoded slotted text
    legacy_prose: Mapping[str, str]                  # legacy form: field path -> prose, evidence-class
    flags: Tuple[str, ...]                           # raised while reading, such as input:cvss_vector:sources-disagree
    component: Optional[str] = None                  # W2: the row's component, for S-12(b)'s supply (D9)
    threat: Optional[str] = None                     # W2: the row's threat text, for S-12(b)'s supply
    risk_level: Optional[str] = None                 # W2: the row's original risk level, for S-12(b)'s supply

@dataclass(frozen=True)
class BaselineScores:
    readable: bool
    reason: Optional[str]                     # "missing" | "not-utf8" | "too-large" | "no-rows"
    form: Optional[str]                       # "renderer" | "legacy"
    rows: Mapping[str, BaselineRow]           # the open rows
    resolved_rows: Mapping[str, BaselineRow]  # the §2a rows (R-30)
    ids_in_any_row: frozenset                 # for ruling B's reused-id test
    frontmatter_date: Optional[date]          # D9's review-date fallback
    issues: Tuple[InputIssue, ...]            # unreadable rows go to Input Issues and are scored fresh

def read_baseline_scores(md_path: Optional[Path], *, sarif_path: Optional[Path] = None) -> BaselineScores: ...
```

- **Reading.** It reads `md_path` as strict UTF-8, at most 16 MiB (D3, step 2). It accepts every form D9 lists, including the renderer's `### Scoring Inputs` in the shared format below. An ID cell that isn't one allow-listed ID yields no row.
- **Unreadable files.** A file that is missing, isn't UTF-8, is too large or yields no row comes back with `readable=False`, and counts as missing (S-12(d)).
- **Vectors.** A legacy vector comes from the markdown, or else from `sarif_path`'s `cvss-vector`, keyed by `findingId/v1`. When both exist and differ, the markdown's is used, flagged `input:cvss_vector:sources-disagree`.
- **Prose.** Narrative text is decoded with `tachi_parsers.decode_references` and returned unvalidated, because the renderer re-validates it and re-resolves its slots (D3). Legacy prose comes back as evidence-class text, and nothing reads a number from it.
- **Identity values (ruled at W2, for S-12(b)).** `component`, `threat` and `risk_level` are what the row records, decoded once, or `None`.
  - The component comes from the §3 heading `### ID — component`, or else the §2 Component cell. A `### ID: title` heading names a title, not a component.
  - The threat comes from §3's `**Threat**:` line, or else the §2 Threat cell, which the renderer shortens.
  - The risk level comes from §3's `**Original Risk Level**:` value.
  - The renderer uses them only for a carried finding whose input form lacks the value (D9).
- **Governance cells, by value class (ruled at W2, from R1b's check; D9's "verbatim").**
  - **The owner is free text** (`risk_owner`). It is read as the cell holds it, decoded once with edge whitespace stripped, and its `**` is kept. So `**Platform** team` carries byte for byte. The renderer escapes on write by D3's table-cell rule, which leaves `*` alone. A cell is no owner only when it is a placeholder once its `**` is set aside: empty, a dash or `n/a`. Today's `_text_value` drops the `**`, so the owner needs its own reader (R1b's fix).
  - **The SLA and the disposition** keep today's reading, without `**`. The disposition is an enum and the SLA a duration, and the override test compares each with the band's default, so the emphasis is formatting, not value. A bolded legacy `**Accept**` or `**7d**` then reads as the value the test compares.
  - **The band and the review date** are parsed as before.
  - These rules hold for §2, §2a and §4 in every form.

### S-13: the one tag source (T042)

```python
Matcher = Callable[[str, Sequence[str]], Optional[str]]

def recompute_tags(architecture_text: str, open_rows: Sequence[Mapping[str, str]], matcher: Matcher) -> Mapping[str, Tuple[str, ...]]: ...

@dataclass(frozen=True)
class TagSource:
    source: str                          # "block" | "recomputed" | "block-unverified" | "none"
    tags: Mapping[str, Tuple[str, ...]]  # one entry per open ID, () when none
    warning: Optional[str]
    cause: Optional[str]

def select_tag_source(*, open_ids: Sequence[str], block: Mapping[str, Sequence[str]], recomputed: Optional[Mapping[str, Sequence[str]]]) -> TagSource: ...
```

- **`recompute_tags`** is the populator's join, run over the reference set's open rows (D2).
  - It calls `tachi_parsers.parse_component_asset_map(architecture_text)`, then `matcher(row["component"], keys)` for each row. It takes the matched component's tags as the map holds them, or `()` when nothing matches.
  - `matcher` is the populator's `match_component`, unchanged. The caller loads `populate-affected-assets.py` by path, as `generate-risk-scores-sarif.py:476-487` loads its extractor. So this module stays over `tachi_scoring` and `tachi_parsers` (D5).
- **`select_tag_source`** decides once per run, never per finding.
  - `block` is the input `threats.md`'s `## Affected Assets` block, as `sarif_common.parse_affected_assets` reads it (`{}` when absent).
  - `recomputed` is `None` when the run has no architecture file.

  The outcomes:
  - the block equals the recomputation on every open ID: `block`;
  - the block is absent, differs, or misses an open ID: `recomputed`, with a warning;
  - no architecture file: `block-unverified`, and the block is used as it is. It always carries a warning, cause `no-architecture-file`, which the renderer records as `tag-source:no-architecture-file`. The warning says the block's tags were applied unverified, and names any tag outside the closed set that was dropped (ruled at W2, ADR-050 D2). Today's code warns only for a dropped tag, so `select_tag_source` and its test change (R1b);
  - neither source: `none`. No finding is elevated, and the run warns, records the cause and continues.

  So every outcome except `block` warns under `tag-source:<cause>`, and the renderer's existing `run.warn("tag-source:%s" % cause, ...)` needs no change.

### R-25 and the CVSS chain (T043)

```python
@dataclass(frozen=True)
class CvssChain:
    base: Decimal                                    # base(v), FIRST's equations (tachi_scoring)
    score_bounds: Optional[Tuple[Decimal, Decimal]]
    assessed: Decimal                                # base, clamped to score_bounds when they're given
    forced: bool                                     # a tag forces a bit (asset-modifiers.md:13-22)
    elevated_vector: Optional[str]                   # elevate(v), when forced
    elevated_base: Optional[Decimal]                 # base(elevate(v)), when forced
    cvss_base: Decimal                               # the final score
    clamp_cause: Optional[str]                       # "bound" | "ceiling": the clamp that set cvss_base

def asset_outcome(assessed: Decimal, vector: str, tags: Sequence[str]) -> Decimal: ...
def cvss_chain(vector: str, *, tags: Sequence[str], score_bounds: Optional[Tuple[Decimal, Decimal]]) -> CvssChain: ...
```

- **`asset_outcome`** is R-25's t(a): `max(a, min(base(elevate(v)), 9.2))` when a tag forces a bit, otherwise `a`.
- **`cvss_chain`** is D10's fresh-scoring chain.
  - The caller passes `score_bounds` in two cases only: for a NEW finding in a baseline-aware run, where `tachi_scoring` gives the finding's own category ±1.0, and for a carried renderer-form row, which passes its stored bounds.
    - **"Baseline-aware" (ruled at the P0 checkpoint, 2026-11-23, P0-9)** means that a usable baseline `risk-scores.md` was read: `read_baseline_scores` returned `readable=True` for the file R-6 resolved, which is when the renderer holds a baseline. Only then is a NEW finding bounded, S-12(b)'s derived-NEW findings included. A missing or unreadable baseline bounds nothing (ADR-050 D10), and R1t pins this.
  - R1 calls it for every fresh item, and `check_carried_vector` calls it for renderer-form rows.

### D10: the vector check on a carried finding (T043)

```python
@dataclass(frozen=True)
class VectorCheck:
    cvss_base: Optional[Decimal]   # the value to render: the stored one kept, or the corrected or retagged one
    flag: Optional[str]            # one kind:field:cause, or None when the carried value passes
    step: str                      # "renderer", or "1" to "6" or "3a" (P0-2): D10's legacy step that decided
    assessed: Optional[Decimal] = None   # W3 (P0-6): the a whose R-25 outcome is cvss_base, or None when none is known

def check_carried_vector(row: BaselineRow, *, tags: Sequence[str]) -> VectorCheck: ...
```

- **`assessed` (ruled at W3, 2026-11-23, P0-6; PM W3 ruling 1).** It is the assessed score a, before R-25's elevation, whose outcome under `tags` is the returned `cvss_base`. A NEW or UPDATED peer with other tags is scored on it (ADR-050 D9, "Peers").
  - **Renderer form:** `cvss_chain(vector, tags=tags, score_bounds=row.score_bounds).assessed`, whatever the flag.
  - **Legacy form:** the candidate that decided. At step 3, it is the first candidate, in order, whose outcome equals the stored score; at step 3a, the a it used, `base(v)` in its ceiling case; at step 4, the candidate it retagged from; and at step 6, and for a missing stored score, `base(v)`.
  - **`None`** at step 1 (no vector), step 2 and step 5, and at step 3 when only its ceiling clause passed, because no candidate's outcome is the stored score there.
  - The renderer takes a fresh row's a from `cvss_chain(...).assessed`, so every rendered row has one source for it.

- **Renderer form.** It recomputes `cvss_chain` from the stored vector, `score_bounds` and this run's `tags`. A difference is `corrected:cvss_base:vector`, unless recomputing with `row.tags_used` gives the stored value, in which case it is `retagged:cvss_base:asset-tags` (ruling A).
- **Legacy form.** It runs D10's steps 1–6 in order, testing this run's tags first (PM plan review, finding 2). The candidates are `base(v)` and its own-category bound clamp.
  - **Step 3a (ruled at the P0 checkpoint, 2026-11-23, P0-2)** runs after step 3, only when `row.tags_used` is not `None`. If the stored score is R-25's outcome under `row.tags_used` for either candidate, or the recorded tags give step 3's ceiling case, the result is `retagged:cvss_base:asset-tags` at `asset_outcome(a, vector, tags)` for that same candidate, with step `"3a"`. Candidates are tried in order, `base(v)` first, and the ceiling case takes `base(v)` (ADR-050 D10).
- **Flag names (ratified at W1, from T043).** A flag's `<field>` is the value whose status the flag describes, by its `schemas/risk-scoring.yaml` name, and its `<cause>` is kebab-case. So a missing vector is `unverifiable:cvss_base:no-vector`, like `unchecked:cvss_base:assessed-unrecorded`. The governance flags name `remediation_sla` and `risk_disposition`, beside `severity_band`, `composite_score` and `review_date`, for example `override:remediation_sla:human`.
  - **Two more sources of names (ruled at W2).**
    - A value of the reference set takes its `schemas/finding.yaml` name: `component`, `threat`, `delta_status` and `risk_level`.
    - `trust_level` is ADR-050 D2's name for the payload's `reachability.trust_level`, which the risk-scoring schema doesn't name, and the flag keeps D2's text.
    - The prose fields keep their dotted payload names (`part-files.md`).
- **The scorer's flag vocabulary, closed** (ruled at W1 from T040 and T043). The renderer (T045, T046), the goldens (T041) and the fixture's expected outcomes (T040) use exactly these strings. A finding carries at most one flag per kind and field.
  - **`corrected:<field>:<cause>`.** The cause names the derivation step that produced the field's new value (D9's four words):
    - `cvss_base:vector`;
    - `composite_score:arithmetic`, and `exploitability`, `scalability` or `reachability` with `:arithmetic`;
    - `severity_band:band-mapping`, or `severity_band:rounding` when only rounding moved the band;
    - `remediation_sla`, `risk_disposition` or `review_date` with `:follows-band`;
    - `trust_level:trust-label`, verbatim from ADR-050 D2 (added at W2). The renderer replaces an agent's trust level that contradicts an unambiguous §2 label with the label's level. The cause names the value's source, the label, as D2 words it, and §6's Score Flags row shows the agent's level as Stored and the label's as Rendered.
  - **The review date's fallbacks.** When a fallback set the date, `review_date:baseline-date` or `review_date:clock-restarted` replaces `follows-band`, so the field carries one flag.
  - **A rounding-only composite difference** is normalized and counted, never flagged. Only a band it moves is flagged, as `severity_band:rounding`.
  - **Ruling A.** `retagged:<field>:asset-tags` goes on every field that the tags alone moved, the values that follow the band included. None of those fields is also flagged `corrected`.
  - **The rest:**
    - `unverifiable:cvss_base:no-vector`;
    - `unchecked:cvss_base:assessed-unrecorded`, `unchecked:cvss_base:bound-n17c`, `unchecked:reachability:compound-trust-label` and `unchecked:review_date:scoring-date-unknown`;
    - `divergent:composite_score:primary=<ID>`;
    - `override:remediation_sla:human` and `override:risk_disposition:human`;
    - `reused-id:finding_id:baseline`, verbatim from D7;
    - `input:cvss_vector:sources-disagree` and `input:reachability:out-of-range`;
    - `input:<field>:narrative-fallback` and `input:<field>:truncated`, over the 28 field names (`part-files.md`);
    - `input:cvss_base:missing` and `input:review_date:missing` (added at W2, from R1b's code). The baseline row's form has a place for the value, but the row leaves it empty or unreadable. The score is then rendered from the chain (`check_carried_vector`), and the review date by R-5's rules (`governance_for`). `governance_for` adds `input:review_date:missing` only when no other flag already explains the review date, so the date carries one explanation. A missing owner, SLA or disposition takes its default with no flag (ADR-050 D9);
    - `input:<field>:not-in-form`, with `component`, `threat`, `delta_status` or `risk_level` (added at W2, from T032: `tachi_parsers.FORM_LACKS_FLAG` and `FORM_LACKS_CAUSE`). Section 7's form, or D8's SARIF fallback for `delta_status`, has no place for the value. The flag stays whether or not the baseline supplied the value (R-31, below);
    - `resolved`, alone, with no field or cause.
  - **No open string is left.** A new string needs an amendment here. The controls renderer (W3) uses the same `input:<field>:not-in-form` strings for its reference-set values.
- **The controls renderer's flag vocabulary, closed** (ruled at W3, 2026-11-23, from T056 and T059). The renderer (T035, T053, T059) and the goldens (T034, T056) use exactly these strings, in `integrity-flags` and §7:
  - **The row checks** (ADR-050 D2): `input:control_status:sources-disagree`, `input:control_category:sources-disagree`, `input:component:sources-disagree` and `input:maestro_layer:sources-disagree`. The field is the value's schema name (`schemas/compensating-controls.yaml` for the first two, `schemas/finding.yaml` for the others). The cause is the scorer's for two sources of one value that disagree, where the structured one is used. §2 keeps the agent's cell (the controls `matrix_row`, below);
  - **an evidence `file` that the resolver refuses at render time:** `input:evidence.file:unresolved`, once per finding (`part-files.md`);
  - `input:<field>:narrative-fallback` over the controls narrative fields (`evidence.assessment.<dimension>`), and `input:<field>:truncated` over those and the four evidence-class fields (`part-files.md`);
  - `input:<field>:not-in-form`, with `component`, `threat`, `delta_status` or `risk_level`, as above;
  - `reused-id:finding_id:baseline`, carried from the scored input (ruling B).

  A finding carries each string at most once. `input:component:not-in-form` and `input:component:sources-disagree` can stand together: the first says that the threat model's form had no Component, and the second that the part's cell disagreed with the value used.

  Two outcomes raise no flag:
  - A cleared `carried_forward` claim. An Input Issue line and the stage record's warning `carried-forward-cleared` record it, which is D2's "cleared with the reason recorded".
  - An overwritten computed cell. It is `counts.cell_overwrites` (`part-files.md`).

  A new string needs an amendment here.

### R-31: routing, peers, dates and governance (T043, T044)

```python
@dataclass(frozen=True)
class ScorerRouting:
    to_agent: Tuple[str, ...]         # non-peers that are NEW or UPDATED, or have no usable baseline row
    carried: Tuple[str, ...]          # UNCHANGED findings with a usable row, peers included
    copy_primary: Mapping[str, str]   # every other peer -> its group's primary
    carried_peers: Mapping[str, str]  # each carried peer -> its primary, for the divergence check
    status: Mapping[str, str] = field(default_factory=dict)  # W2: each open ID -> the status it was routed under

def route_scorer_units(open_rows: Sequence[Mapping[str, str]], *, groups: Sequence[Mapping[str, object]], baseline: Optional[BaselineScores],
                       lacking: Optional[Mapping[str, Sequence[str]]] = None) -> ScorerRouting: ...

def peer_divergence(*, peer_composite: Decimal, primary_id: str, primary_composite: Decimal) -> Optional[str]: ...

@dataclass(frozen=True)
class ScoringDate:
    value: Optional[date]
    flag: Optional[str]

def original_scoring_date(row: BaselineRow, *, baseline_date: Optional[date]) -> ScoringDate: ...

def classify_band_change(*, stored_band: Optional[str], rendered_band: str, band_with_baseline_tags: Optional[str]) -> str: ...

@dataclass(frozen=True)
class Governance:
    owner: str
    sla: str
    disposition: str
    review_date: date
    scored_on: date
    flags: Tuple[str, ...]

def governance_for(status: str, *, rendered_band: str, run_date: date, row: Optional[BaselineRow], band_change: str, baseline_date: Optional[date]) -> Governance: ...
```

- **`route_scorer_units`** is the one partition. Both the planner (T044) and the renderer (T028, T045) call it, so they always agree (D2).
  - `open_rows` are the reference-set wrapper's open rows, with at least `id`, `component` and `delta_status`. Unless `lacking` names `delta_status` for it (below), a row with no usable `delta_status` counts as NEW, as today. That covers an absent value and a value that isn't NEW, UPDATED or UNCHANGED, and the default `lacking=None` changes no caller.
  - `groups` is `parse_correlation_groups(...)["groups"]`, filtered to the open IDs.
  - A usable row is an entry of `baseline.rows`. A NEW finding whose ID is in `baseline.ids_in_any_row` goes to the agent, never to `carried` (ruling B).
  - **S-12(b)'s derivation (ruled at W2; ADR-050 D9).** `lacking` is the reference set's `lacking` map, canonical ID to the names of the values its form lacks. For D8's SARIF fallback it is `{id: ["delta_status"]}` for every member. When `lacking` names `delta_status` for an ID, its status is UNCHANGED if `baseline.rows` holds the ID, so it is carried, and NEW otherwise, so it goes to the agent under ruling B as any NEW finding does. A status is derived here and nowhere else.
  - **`status`** maps every open ID to the status it was routed under, the Section 7 value or the derived one. The renderer takes each row's status from it, for governance, ruling B's test and the bounds of a NEW finding. So the planner (T044) and the renderer (T045) can't disagree. Both pass the same `lacking`: the planner gets it from the reference set it read, or builds the SARIF fallback's.
  - **The renderer's supply (T045).** For each carried ID, each of `component`, `threat` and `risk_level` that `lacking` names takes the `BaselineRow`'s value, when the row records one. It happens before S-13's tag join, so the join, the zone lookup and §1's type lookup use the supplied component. A fresh ID is never supplied. Each lacking value keeps `input:<field>:not-in-form`, supplied or not, and the stage record's `value-not-in-form` warning lists the IDs.
- **`peer_divergence`** gives `divergent:composite_score:primary=<ID>` when the two composites differ, and otherwise `None`.
  - **Its callers (ruled at W3, 2026-11-23, PM W3 ruling 1).** The renderer calls it for every peer: each of `carried_peers` (R-4), and each of `copy_primary` once the peer is scored with its own tags. So a peer whose tags move its composite is flagged on the run that scores it, and a peer with equal tags has its primary's composite and no flag (ADR-050 D9, "Peers").
- **`original_scoring_date`** returns the stored scored-on date (whenever §6 records one, P0-2), or the stored review date minus the stored SLA (legacy). If neither exists, D9's fallbacks apply in order:
  1. the baseline file's frontmatter date, flagged `corrected:review_date:baseline-date`;
  2. `None`, flagged `unchecked:review_date:scoring-date-unknown`, which tells `governance_for` to keep the stored review date.

  The last fallback, the run date plus the SLA (`corrected:review_date:clock-restarted`), is applied by `governance_for`.
- **`classify_band_change`** returns `none`, `corrected`, `retagged-up` or `retagged-down`. `band_with_baseline_tags` is the band recomputed with the baseline's recorded tags, or with no tags for a row that records none (ruling A's legacy case). A legacy-carried row records them, so its recorded tags are used (P0-2). When it equals the stored band and the rendered band differs, the change is a retag, up or down by band order.
- **`governance_for`** applies D9's governance for `status`, which is NEW, UPDATED or UNCHANGED:
  - overrides are kept and flagged `override:<field>:human`;
  - the owner is always carried and never flagged;
  - the review date follows R-5 and ruling A;
  - a fresh finding gets `Unassigned` and the run date.

  SLA days use `tachi_scoring`'s date arithmetic.

## `scripts/tachi_parsers.py`: lane P's new functions (W2)

`tachi_parsers` may import `tachi_parts` for its identifier patterns, and `tachi_parts` never imports `tachi_parsers` (C1). The module's existing functions keep their signatures:
- T057 widens `parse_compensating_controls_md` to read K8's corrected format and the pre-fix one. Its parameters don't change, and its rows only gain keys.
- T032 widens the reference-set wrapper's accepted forms without changing its signature. The wrapper is lane R0c's, written in W1 (T018), and G1 records its name and return shape.

**Settled by T018 (ruled at W1, 2026-11-22, T023):**

```python
def parse_reference_set(content: str, source: str = "threats.md") -> dict: ...  # {"open", "resolved", "duplicates", "form", "lacking", "flags"}
def parse_markdown_table(content: str, section_header: str = None, start_line: int = None, skipped: list = None,
                         row_lines: list = None, keep_bold: bool = False) -> list: ...
```

- **Updated at W2 (2026-11-23), from lane P's code.** Each addition below is additive, with a default that leaves every caller unchanged.
  - `parse_reference_set` returns three more keys from T032: `form`, `lacking` and `flags` (S-12(b), R-31 below).
  - `parse_markdown_table` takes two more keywords:
    - `row_lines` receives the 1-based line of each *returned* row, in step with the rows, so a caller can name a row's line in a message, as the Section 4a reader does;
    - `keep_bold=True` keeps the `**` markers in data cells, and header cells always lose them. The persisted-inputs readers ask for it, because a persisted value is stored exactly as written (the persisted-inputs format, below).

- **`parse_reference_set`** returns `open` (Section 7, as `parse_threats_findings` builds each row) and `resolved` (Section 4c), each in S-2 order. Every ID passes the allow-list, and `id` keeps the file's spelling. It raises `ReferenceSetError`, a `ValueError`, so the stage stops before dispatch (S-12(c)).
- **A repeated canonical ID is read, never refused.** The first row wins, and an open row beats a resolved one. `duplicates` lists the repeated IDs in S-2 order.
  - **Why read it.** One ID is one finding (D-4). The shipped `maestro-reference` example lists one twice, so this is one of the forms tachi's own samples show, which S-12 reads.
  - **The warning.** `plan` prints it on stderr and still exits 0, because its exit codes are 0, 1 and 2. Each renderer lists the IDs under Input Issues (scorer §6, controls §7) and as the stage record's warning `duplicate-finding-id`, and exits 5.
  - **The oracle (NFR-1).** A diff explained by the dedup belongs to the class "duplicate reference-set ID, first row wins", naming the ID: an old output's second row for the ID, or a value or text that follows the first row. The class applies only when the run's warning names the same ID. Otherwise the diff is unattributed.
- **`skipped`** is additive, with a default that leaves every caller unchanged. It receives the 1-based line of each row dropped as malformed, so the reference set can refuse to lose a row.
  - T033's decoder runs on each cell after the split on raw `|`, so decoding never changes a row's cell count.
- **`tachi_parsers` imports `tachi_parts` at module level** from the commit that wires `tachi_parts` into the install manifest (T022), in lock-step (H7).
  - R0c, the file's W1 writer, supplies the edit. If T022 has already landed, lane P makes it W2's first change to the file.
  - A function-level import hides the dependency from F-373's S-13 import gate and from `_import_closure`, and it would fail mid-run instead of at load.

```python
from typing import Iterable, Optional

def decode_references(text: str) -> str: ...
def parse_correlation_groups(content: str, member_ids: Optional[Iterable[str]] = None) -> dict: ...
def parse_sarif_member_set(sarif_text: str, *, with_scores: bool = False, with_details: bool = False) -> dict: ...
def parse_controls_assessment_inputs(content: str) -> dict: ...
def match_heading(pattern: str, text: str, *, outside_fences: bool = False) -> Optional[int]: ...  # existing; W3 adds the keyword
```

- **`decode_references` (T033)** is D3's one closed decoder.
  - It decodes exactly `&amp;`, `&lt;`, `&gt;`, `&#124;`, `&#96;`, `&#123;`, `&#10;`, `&#35;` and `&#126;` (the ninth, added at the P0 checkpoint, P0-1), in a single left-to-right pass, and leaves anything else as written. Replaced text is never re-scanned, so `&amp;lt;` decodes to `&lt;`.
  - `parse_markdown_table` applies it to each cell after splitting the row on raw `|`, and so does every other reader of rendered text. GFM's `\|` isn't decoded.
- **`parse_correlation_groups` (T048, D8)** returns `{"groups": [{"group_id", "primary", "members"}], "errors": [{"line", "row", "reason"}]}`.
  - Groups come in Section 4a's order. `members` are canonical, in listed order, with the primary first, and filtered to `member_ids` when that is given.
  - A group left with fewer than two members is omitted, and an ID listed in two groups stays in the first.
  - **Which group claims an ID (ruled at W1, from T015).** The first group that lists an ID claims it, even if that group then falls away, which is D8's literal reading. So a later group never takes the ID over, and an ID claimed by a group that falls away stays uncorrelated.
  - **This function is the one authority for D8's four rules**: order, the claim, the primary and the two-member minimum. The scorer's routing and peer inheritance and both renderers' SARIF correlation use its result.
    - `sarif_common.correlation_assignments` receives `(group["group_id"], group["members"])` for each of its groups, and only assigns roles.
    - Any rule it re-applies must give the same result on the same input, and one test runs the same edge cases through both: a member in two groups, and a first group that falls away.
  - A row whose group ID fails `tachi_parts`' group pattern, or whose members fail its finding pattern, goes to `errors`.
  - A missing or empty Section 4a gives `{"groups": [], "errors": []}`.
  - **A repeated group ID (confirmed from T048).** A later row with an earlier row's group ID is a malformed row: it goes to `errors` (Input Issues), the first row wins, and the repeat claims none of its members. That keeps one primary per group, which the emitter's self-check needs.
- **`parse_sarif_member_set` (T142, D8's fallback)** returns `{"members": [...], "groups": [...], "scores": {...}}`.
  - `members` are canonical IDs in result order, from `findingId/v1`, plus legacy peer references. A legacy reference is an allow-listed ID at the start of a `relatedLocations` entry's `message.text`, followed by `: `, and each one is grouped under its result.
  - `groups` take the shape `parse_correlation_groups` returns. `group_id` comes from the `correlation-group` property, and is `None` where the file names none.
  - `scores` is filled only with `with_scores=True`, for `risk-scores.sarif`: `{id: {"composite": Decimal or None, "band": str or None}}`, read across the property names the shipped files use.
  - **`details` (ruled at the P0 checkpoint, 2026-11-23, P0-3; amended at W3 from FX0's reader)** is present only with `with_details=True`. The default return has no `details` key, so its dict is what it was, and a caller that forgets the flag gets a `KeyError`, never a silent blank. It is `{id: {...}}`, one entry per member that has its own result, in either ID form. The first kept result of an ID wins, and a member that only a legacy peer reference names has no entry, so a caller iterates `members` and looks each one up with `details.get(id, {})`.
    - Each entry holds D8's reading of that result: `component` (the logical location's `name`, else `properties.component`), `threat` (`message.text`), `mitigation` (`message.markdown`), `risk_level` (`properties.risk_level`, else `properties.severity`, else `security-severity`), `layer` (`maestro-layer`) and `kind` (the logical location's `kind` as written, such as `process` or `data-store`).
      - **The logical location** is `locations[0].logicalLocations[0]`, else `locations[0].logicalLocation`, the form that tachi's older scorer and controls SARIF write.
      - **Why both amendments (W3, 2026-11-23, from FX0-3 and R3a).** `generate-threats-sarif.py` writes Section 7's risk level as `severity`, and `agentic-app`'s modern `threats.sarif` carries no other level. `agentic-app`'s and `mobile-banking-app`'s shipped `risk-scores.sarif`, the controls fallback's input, carry only the singular location. Without them, those members' units and rows lost the level or the component.
    - **The kind, read back (confirmed at W3).** A renderer reads `kind` through the closed spellings `external-entity`, `process`, `data` and `data-store`, where the last two both name a Data Store. It writes its own map's kind, so a data store is `data` from either input form. Any other value is `process`, the default for a component with no §1 type. No key holds the kind (ADR-050 D7).
    - A value is the string as written: unstripped, unescaped and unchecked, so the renderer's P0-4 intake sees it. It is `None` when the result holds none, and a blank string or a non-string counts as none.
    - An absent mitigation is `None`. The renderer writes `""` for it as `message.markdown`, which is always written (P0-8).
    - The planner's fallback units (R1b, R3a) and the renderer's fallback reference set (R1) both read it, so neither reads a result a second way. So does the controls renderer (R2, ruled at W3). It reads itself only what an entry lacks: the zone, from the same logical location's `fullyQualifiedName`, and `reused-id`, from `score-flags`. A unit row takes `component`, `threat`, `risk_level` and `mitigation`, and leaves out one that is `None`, as `_unit_row` leaves out what a finding lacks.
    - **The risk label (confirmed at W3).** Every reader of `details` turns `risk_level` into the finding's label the same way, so a planner's unit and the renderer's row agree. A string that `tachi_parsers.parse_score` doesn't read as a finite number is kept as written, such as the band word `High` or `Note`. A score is clamped to 0.0–10.0, rounded with `tachi_scoring.q1` and banded with `tachi_scoring.band`, as the renderer's `_risk_level` and `_grid` do. Its four bands make a score under 1.0 `Low`, never `Note`, while a `Note` word is kept as written (confirmed at W3, FX0-3's decision 1). `None` gives no label: the unit leaves the key out, and the renderer writes `—`. `tachi-stage.py` keeps one local copy for both stages' fallbacks, and a test runs the planner's and the renderer's labels over the shipped samples and the edges `8.95`, `6.95`, `-1`, `10.5`, `NaN` and `High`.
  - **A group whose `group_id` is `None` (ruled at the P0 checkpoint, P0-3)** still routes its peers (D9), but carries no `correlation-*` property and no ruling-C sentence: the renderer passes only named groups to `sarif_common.correlation_assignments`, and its stage record warns `correlation-group-unnamed`, with the count (ADR-050 D8).
  - Results whose `baselineState` or `baseline-state` property is `absent` are dropped, and no hash is ever read.
  - It raises `ValueError` on JSON that doesn't parse and on an empty extraction, so the stage stops before dispatch (KB 22).
  - **The legacy member form (ruled at W1, from T142).** A result with no `findingId/v1` takes its member ID from `properties.id`. This is a closed legacy form: tachi's own older SARIF writes it, and four shipped samples carry it (Constitution III; S-12's principle).
    - `findingId/v1` wins whenever both are present.
    - The value must pass the finding allow-list, and a result whose value fails it is skipped.
    - Any other form still makes an empty extraction, whose error names the file and the remedy: regenerate the markdown input with its command.
    - **Lane P lands it now, as a T142 follow-up in W2.** The four shipped samples are its read-only test inputs.
- **`parse_controls_assessment_inputs` (T143, AR-T3)** returns `{"inputs": {id: item}, "errors": [...]}`.
  - Each item is the controls payload as `contracts/part-files.md` keys it, without `finding_id`, decoded. Narrative values keep their slot tokens, and evidence-class values come back as written.
  - A pre-1.1 file, which has no `### Assessment Inputs`, gives `{"inputs": {}, "errors": []}`.
  - A row whose field isn't in the controls payload's closed key set goes to `errors`.
  - It finds `### Assessment Inputs` with `match_heading(..., outside_fences=True)` (ruled at W3), so a quoted snippet in §3 can't stand in for it.
- **`match_heading` (existing; `outside_fences` ruled at W3, 2026-11-23, from T087's observation)** returns the 0-based index of the first line that `pattern`, a line-anchored regex, matches, or `None`. The default is today's one search over the whole text, so every existing caller is unchanged. With `outside_fences=True` it tests the lines, split on `\n` only, one at a time, and skips every line of a fenced code block, the fence lines included:
  - a fence opens on a run of at least three backticks or three tildes, after spaces and tabs only. A backtick run with another backtick later on its line opens none;
  - it closes only on a run of the same character at least as long as the opener's, followed by nothing but spaces, tabs or a `\r`;
  - an unclosed fence runs to the end of the text, so no heading after it is found.

  Every reader that a renderer's from-disk checks or the next run rely on passes `True` (ADR-050 D3, "Finding a section"): `parse_controls_assessment_inputs`, and every section lookup in both renderers' `_check_staged`. The extractors keep the default until their follow-up.

## `scripts/sarif_common.py`: one W2 addition (lane R0b, ruled at W2, 2026-11-23)

```python
def resolve_explicit(candidate: object, *, root: Optional[str] = None, fs: Any = None) -> Tuple[Optional[ResolvedPath], Optional[Dict[str, str]]]: ...
```

- **What it is.** D7's first candidate, split out of `resolve_architecture` so that `tachi-stage.py plan` runs the same step.
  - It returns `(resolved, None)` when `resolve_file(candidate, root=root, allow_absolute=True, fs=fs)` passes.
  - Otherwise it returns `(None, warning)`. The warning is the `{code, detail}` that `resolve_architecture` lists for that failure: code `architecture-path:explicit:<check>`, and a detail that names the candidate in its escaped short form, the check and `--architecture-path`.
- **`resolve_architecture`'s step 1 calls it.** Its signature, outputs and warnings don't change.
- **The planner** records the warning as the plan's `architecture_warning` (`part-files.md` §4). The renderer lists it ahead of its own resolver's warnings.
- **Order.** It lands before R1b's planner change that calls it.

## `scripts/sarif_common.py`: W3 additions (lane R3a, named in `d0277a3`; the scan's skip list from `b9b4962`; recorded at W3's closing sweep, 2026-11-23)

```python
RULES: Tuple[Tuple[str, str, str, Tuple[str, ...], Tuple[str, ...]], ...]  # (category, short description, full description, tags, taxonomy IDs), in the 1.1 templates' order
COPIED_TEXT_PROPERTIES: Dict[str, Tuple[str, ...]]  # driver name -> the top-level properties whose text is copied from an input

def taxonomy_name_for(taxon_id: str) -> str: ...
def build_rules(highest: Mapping[str, Decimal]) -> List[Dict[str, Any]]: ...
def build_driver(sarif_file: str, *, semantic_version: str, rules: Sequence[Mapping[str, Any]],
                 supported: Optional[Sequence[Mapping[str, Any]]] = None, version: Optional[str] = None) -> Dict[str, Any]: ...  # existing; W3 adds version, last
def self_check(results: Sequence[Mapping[str, Any]], *, tool: str, member_ids: Iterable[str],
               assignments: Optional[Mapping[str, Correlation]] = None, resolved_ids: Iterable[str] = (),
               uri: Optional[str] = None) -> None: ...  # existing; W3 changes what it checks, not its signature
```

- **`RULES`** is the one rule table of `risk-scores.sarif` and `compensating-controls.sarif` (PM W3 ruling 2, gap A). It moved here from the scorer's renderer, and each renderer keys it by category. A row holds what the 1.1 templates write for the rule. Its taxonomy IDs are the rule's `relationships`, and the IDs that a finding's `{{ref:...}}` slot may cite for that category (ADR-050 D3's table). `test_sarif_identity.py` pins every field to both templates.
- **`taxonomy_name_for`** is a closed map: `CWE-<n>` gives `CWE`, and `A01` to `A10` gives `OWASP`. Any other ID is a defect in shipped code and raises `ValueError`. The links name a taxonomy only, so they may not resolve inside the file (ADR-050, Known limitations).
- **`build_rules`** returns one rule per category in `highest`, in `RULES`' order and in `sarif-result.md`'s form: `id`, `shortDescription`, `fullDescription`, `properties` (`tags`, then `security-severity`) and `relationships`, one entry per taxonomy ID of the row, in the row's order.
  - `highest` maps a category to the highest score among that file's results: the composite in the scorer's file, the residual in the controls file. The rule writes it as text, rounded with `tachi_scoring.q1`.
  - A category with no result has no rule. A key that isn't one of the eight categories raises `ValueError`. Each call returns new lists and objects.
  - The controls renderer's from-disk check compares the staged driver's `rules` with it.
- **`build_driver`'s `version` (PM W3 ruling 2, gap C).** Given, `"version"` is written right after `"name"`, where the 1.1 templates put it. Both PR 1 renderers pass `tachi_parts.VERSION`, the value they pass as `semantic_version` (`sarif-result.md`). Not given, the driver has no `version` key, so `threats.sarif`'s generator, which passes none, keeps its bytes. A value that isn't a non-empty string raises `ValueError`.
- **`self_check`'s RESOLVED scan (ruled at W3 as Q9, settling P0-10; ADR-050 D8).** It reads `findingId/v1` and every property at any depth, except the top-level properties that `COPIED_TEXT_PROPERTIES` lists for `tool`: the scorer's `risk-owner`, and the controls file's `control-evidence` and `recommendation`. It never reads `message.text`, `message.markdown` or a `relatedLocations` message. An ID in copied text is a mention, not a reference, and ruling C's sentence keeps its own exact check. A driver with no entry, which is `threats.sarif`'s until PR 2, has every property read.
- **`self_check`'s evidence-URI guard (from R3a; ADR-050 D7).** Each `relatedLocations` entry's `uri` must pass `tachi_parts.path_problem`, the resolver's own relative-path rule. So a scheme, a leading `/`, a drive letter, a backslash or a `..` fails the render, and the problem names the finding and the check.
  - The URI is checked as written, not percent-decoded, which holds while the emitter encodes `%` (the code's `AOD-SIMPLIFICATION` marker).
  - A malformed entry is a shape problem, never an `AttributeError`.
  - The primary `artifactLocation.uri` is only compared with the run's `uri`. T064's SA-11, which asks for the check on both URIs and for decoding first, goes to T146.

## `scripts/tachi_parts.py`: W3 additions (lane FX0; the first ruled at the P0 checkpoint, the others at W3's rulings and its closing sweep, 2026-11-23)

```python
def forbidden_character(text: str) -> Optional[str]: ...
```

- **Published** by FX0's first slice, with this signature, and `tachi_parts`' step 10 now calls it.
- **What it is.** The first character of `text` in D3's step-10 set, or `None`: a control character other than tab and newline (C0, DEL and C1), U+2028, U+2029, and the bidi controls U+200E, U+200F, U+061C, U+202A–U+202E and U+2066–U+2069. Step 10's length limit isn't part of it.
- **A lone surrogate (amended at W3, 2026-11-23, from R3a's planner).** It also returns a surrogate code point, U+D800–U+DFFF (Unicode category `Cs`), which only a JSON escape can spell and no UTF-8 file can carry.
  - A part never reaches step 10 with one, because `load_json` refuses it first ("a string holds a surrogate code point"), so no part's outcome changes. The renderers' intake and backstop refuse it with their usual exits, 2 and 4 (ADR-050 D3).
  - The test that checks the set over the whole Basic Multilingual Plane adds category `Cs`, which is 2,048 code points.
  - `tachi-stage.py plan` keeps its own codec test, for the values it copies from a JSON input.
- **`COUNT_KEYS` gains `cell_overwrites`** (ruled at W3, 2026-11-23, from T056 and T059), the eighth base count (`part-files.md`). One commit adds it in four places: here, in `test_tachi_parts.py`'s key set, in the shared reference's §5 `counts` row and in `test_contract_text_374.py`'s key count (15 to 16).
- **Who calls it (P0-4, ADR-050 D3).** Step 10 itself, on every string of a part. A renderer, at the point it takes a value from an input that isn't a part, refusing the value with exit 2. `_check_staged`'s whole-file backstop, on the staged markdown and every decoded SARIF string, with exit 4. The controls renderer and PR 2's writers call it too, so the set has one definition.

**The controls item's structural checks (recorded at W3's closing sweep, 2026-11-23, from FX0c, `c6ee943`).** They carry out ADR-050 D2's cell table, where a structural mismatch rejects the item and its batch is re-dispatched. They run at `read_part` time, so `reconcile` retries the batch (exit 3) instead of the render failing after the agents have run.

```python
MATRIX_ROW_CELLS: int = 11
RECOMMENDATION_KEYS: Tuple[str, ...] = ("What to Implement", "Where to Implement", "Reference Patterns", "Effort Estimate")
EFFORT_LEVELS: Tuple[str, ...] = ("Low", "Medium", "High")

def matrix_row_cells(row: str) -> List[str]: ...
```

- **`matrix_row_cells`** is the controls `matrix_row`'s "Pipes" rule (below) as code. It strips the line's edge whitespace, drops one leading and one trailing `|` where present, splits on raw `|`, and strips each cell's edge whitespace, as `parse_markdown_table` strips a cell. Nothing is decoded, and `row` must be a `str`. Step 9 and the controls renderer both split a row with it, so they count the same cells.
- **Step 9's controls checks** run on each value after its cut and strip, so they judge the value that is kept. A failure makes the part `invalid`.
  - **`matrix_row`:** exactly `MATRIX_ROW_CELLS` cells, and a first (Threat ID) cell that passes the finding allow-list and canonicalizes to the item's `finding_id`. No other cell rejects the item. The renderer flags a checked cell that disagrees, and fills a computed one, counting it when it held anything but its slot token (the controls `matrix_row`, below).
  - **`recommendation_body`, when it isn't null:**
    - each of `RECOMMENDATION_KEYS` once and in order, on a line that starts, after any whitespace, with `**<key>**:`. Any other line belongs to the key above it, so a value may run over several lines;
    - an Effort Estimate whose text after the key, on the key's own line, starts with `Low`, `Medium` or `High` as a whole word;
    - no line that starts, after any whitespace, with `#` or `|`.
  - A detail names the finding and, for the keys, the key names that it found. It never echoes the row's or the body's text.
- **The renderer reads §4 back with the same names.** It takes each block's Effort word after `**Effort Estimate**:` through `EFFORT_LEVELS`, and SARIF's `effort-estimate` is that word (ADR-050 D2). So the part check, the render and the from-disk check agree.

## The persisted-inputs format: `risk-scores.md` §6 and `compensating-controls.md` §7

`render-risk-scores.py` writes `### Scoring Inputs` under `## 6. Score Integrity` (D9). `render-compensating-controls.py` writes `### Assessment Inputs` under `## 7. Analysis Integrity` (D2). The next run reads each back: §6 through `read_baseline_scores`, and §7 through `parse_controls_assessment_inputs`.

Both sections use one table, so the writers (R1, R2), the readers (R1b, P) and the templates (C, D) agree before any of them lands:

| ID | Field | Value |
|---|---|---|
| T-12 | control_status | partial |
| T-12 | evidence.0.snippet | first line&#10;second line |

- **One row per value.** A row holds one finding and one field that has a value. A null field or an empty list writes no row.
- **Order.** Rows go in S-2 order of ID, then in the payload's key order (`contracts/part-files.md`). §6's extra fields come last.
- **Field names** are value addresses, as `part-files.md`'s "Readings ruled at W1" defines them: dotted, with a list entry as a numeric segment indexed from 0, ending at the string. Examples are `rationale.cvss`, `exploitability.known_techniques`, `subscore_rationale.skill_level`, `evidence.1.summary` and `evidence.0.assessment.coverage.rationale`. A flag's `<field>` drops the indexes (`evidence.summary`, `evidence.assessment.coverage`), because it names a field, not one value.
  - §6 adds the renderer's other step-1 inputs: `score_bounds` (low and high, joined by `,`), `tags` (sorted, joined by `,`, and empty for none) and `scored_on` (`YYYY-MM-DD`).
  - **`tags` is always written for an open finding,** with an empty value when there are none. It is the exception to "a null field or an empty list writes no row", because its absence means that no tags were recorded, ruling A's legacy case (D9). `score_bounds` is written only when the finding has bounds. Confirmed from T027.
  - §7 holds the whole controls item (D2, AR-T3's reading).
- **Values** are escaped on write by D3's table-cell rule, and decoded on read with `decode_references`. Narrative values keep their slot tokens. Booleans are `true` or `false`, and integers are written in decimal. No value has edge whitespace, because `tachi_parts` removes it at intake (`part-files.md`), so the readers' cell strip loses nothing.
- **Reading.**
  - A value is read as the cell holds it, decoded once, and keeps its `**` (ruled at W2). `read_baseline_scores` reads the raw Value cell, and `parse_controls_assessment_inputs` passes `keep_bold=True`. So prose emphasis round-trips byte for byte, as the edge-whitespace rule intends.
  - A reader re-checks each value's class: closed values against their pattern or enum, and narrative values by D3's step 11 when they're re-resolved.
  - A row with an unknown field goes to the reader's issues or errors.
  - No number is ever read from a narrative value.

### The controls `matrix_row` (ruled at W3, 2026-11-23, from lane D's T037 question)

`matrix_row` is one finding's row of `compensating-controls.md` §2 (K8, R-34). The agent writes it in its part, the renderer checks and fills it (ADR-050 D2's cell table) and §7 persists it. The planner then copies it into an UNCHANGED unit's row, and the agent copies it back. One form serves every step. `parse_controls_assessment_inputs` returns it as written, so the reader needs no change.

- **Cells, in this order:** `Threat ID | CF | Component | MAESTRO Layer | Threat | Inherent Score | Inherent Severity | Control Status | Control Category | Residual Score | Residual Severity`. It is K8's §2 header, which the 1.1 template writes (T060), and the order of lane D's example and lane P's fixtures.
- **Pipes.** The row is written as a GFM table line: `| ` before the first cell, ` | ` between cells and ` |` after the last, with no `|` inside a cell. The renderer reads a row with or without the outer pipes: it strips the line's edge whitespace, drops one leading and one trailing `|` where present, and splits on raw `|`. A count other than 11 cells rejects the item (D2). Step 9 counts them with `tachi_parts.matrix_row_cells` (above). Only `|` splits a row, so a line break inside one isn't refused. The renderer writes it as `&#10;`, so the row stays one line in §2 and §7, and it reads back with the same cells (T064's SA-17, a T080 note).
- **Cell values.**
  - **Threat ID:** the finding's ID. It must pass the allow-list and canonicalize to the item's `finding_id`, or the item is rejected (D2).
  - **Component:** the unit row's component, checked against the input (D2). **Threat:** model text, under NFR-10 only (D2).
  - **MAESTRO Layer:** the finding's layer as the input records it, or `Unclassified`. It is checked against the value that the controls SARIF writes as `maestro-layer` (`sarif-result.md`), by layer code (`L1` to `L7`), with `Unclassified` matching only itself. A value with no code is compared as written.
  - **Control Status:** `Control Found`, `Partial Control` or `No Control Found`, the display form of `control_status`, checked through `classify_control_status` (D2).
  - **Control Category:** the display name of `control_category`, as `control-categories.md` heads it: `Authentication`, `Input Validation`, `Rate Limiting`, `Encryption`, `Logging/Audit`, `CSRF Protection`, `CSP/Security Headers` or `Access Control`. The slug itself, such as `input-validation`, names the same value, so it isn't flagged.
  - **The four computed cells:** exactly `{{score:inherent}}`, `{{band:inherent}}`, `{{score:residual}}` and `{{band:residual}}`.
  - A mismatch in Component, MAESTRO Layer, Control Status or Control Category is flagged, never rejected, and the SARIF and every total follow the structured value (D2).
    - **Ruled at W3 (2026-11-23, from T056 and T059).** The flag is `input:<field>:sources-disagree` (the controls vocabulary, above).
    - §2 shows the cell as the agent wrote it, escaped, because R-34 keeps §2 model-authored in PR 1 and FR-K8.1's follow-up turns the check into a fill.
    - §3 to §6 and the from-disk checks follow the structured value, as the SARIF does.
- **`CF` is the renderer's cell, and it isn't counted.** The renderer fills it by column position from the accepted `carried_forward` (`CF` or `—`), and never counts it as an overwrite. The judgment is `carried_forward` itself, and the renderer already records a cleared one with its reason (D2). So a row copied from a run in which the finding was fresh holds `—` and shows `CF`, with no overwrite. The overwrite count covers only the four computed cells. It is the stage record's `counts.cell_overwrites`, ruled at W3 (`part-files.md`).
- **What §7 persists:** the row in this form, rebuilt from its 11 cells. The four computed cells hold their slot tokens, never the numbers §2 shows, and `CF` holds the value §2 shows. Every other cell is kept as the part wrote it. So a carried row is copied, read and checked with no overwrite (T056), whatever its first run put in those cells.
