# Contract: frozen module signatures for W2

> Normative for F-374. Frozen at W1 (2026-11-22, T023) under ADR-050 D5, and ADR-050 governs where this file and the ADR disagree. W2's lanes code to these names, parameters and return shapes:
> - R1b writes `tachi_scoring_rules.py` (T042–T044);
> - P writes the new `tachi_parsers` functions (T033, T048, T142, T143);
> - R1, C, R2, R3a and D call these functions, or write the formats below.

**The freeze.**
- Additive changes keep it: a new keyword argument with a default, or a new dataclass field or dict key with a default, added last. The owning lane names each one in its commit message.
- A rename, removal, reorder or type change needs an architect amendment to this file.

**Shared conventions.**
- Every module has `from __future__ import annotations` and runs on Python 3.9 (S-11). Annotations use `typing` forms, so nothing here needs 3.10.
- Every finding ID passed in or returned is canonical (`tachi_parts`, ADR-050 D3), and passes the allow-list before any other use. Sequences of IDs are in S-2 order unless stated otherwise.
- No float enters stored-value arithmetic: scores are `Decimal` (D5). No function reads the clock, so dates are parameters.
- Content problems never raise. They come back as flags (`kind:field:cause`, D9), issues or reasons. Each exception to this is listed with its function.

## `scripts/tachi_scoring_rules.py` (lane R1b, W2)

It imports only the standard library, `tachi_scoring`, `tachi_parsers` and `tachi_parts`. It never imports `sarif_common`, an entry script or `yaml`, and it reads only the paths its callers pass (D5).

```python
from __future__ import annotations

from dataclasses import dataclass
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
    tags_used: Optional[Tuple[str, ...]]             # renderer form only; None means no tags were recorded
    scored_on: Optional[date]                        # renderer form only
    stored: Mapping[str, Optional[Decimal]]          # cvss_base, exploitability, scalability, reachability, composite
    band: Optional[str]
    owner: Optional[str]
    sla: Optional[str]                               # as written, such as "24h" or "7d"
    disposition: Optional[str]
    review_date: Optional[date]
    narrative: Mapping[str, str]                     # renderer form: field path -> decoded slotted text
    legacy_prose: Mapping[str, str]                  # legacy form: field path -> prose, evidence-class
    flags: Tuple[str, ...]                           # raised while reading, such as input:cvss_vector:sources-disagree

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
  - no architecture file: `block-unverified`, and the block is used as it is;
  - neither source: `none`. No finding is elevated, and the run warns, records the cause and continues.

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
  - R1 calls it for every fresh item, and `check_carried_vector` calls it for renderer-form rows.

### D10: the vector check on a carried finding (T043)

```python
@dataclass(frozen=True)
class VectorCheck:
    cvss_base: Optional[Decimal]   # the value to render: the stored one kept, or the corrected or retagged one
    flag: Optional[str]            # one kind:field:cause, or None when the carried value passes
    step: str                      # "renderer", or "1" to "6": D10's legacy step that decided

def check_carried_vector(row: BaselineRow, *, tags: Sequence[str]) -> VectorCheck: ...
```

- **Renderer form.** It recomputes `cvss_chain` from the stored vector, `score_bounds` and this run's `tags`. A difference is `corrected:cvss_base:vector`, unless recomputing with `row.tags_used` gives the stored value, in which case it is `retagged:cvss_base:asset-tags` (ruling A).
- **Legacy form.** It runs D10's steps 1–6 in order, testing this run's tags first (PM plan review, finding 2). The candidates are `base(v)` and its own-category bound clamp.

### R-31: routing, peers, dates and governance (T043, T044)

```python
@dataclass(frozen=True)
class ScorerRouting:
    to_agent: Tuple[str, ...]         # non-peers that are NEW or UPDATED, or have no usable baseline row
    carried: Tuple[str, ...]          # UNCHANGED findings with a usable row, peers included
    copy_primary: Mapping[str, str]   # every other peer -> its group's primary
    carried_peers: Mapping[str, str]  # each carried peer -> its primary, for the divergence check

def route_scorer_units(open_rows: Sequence[Mapping[str, str]], *, groups: Sequence[Mapping[str, object]], baseline: Optional[BaselineScores]) -> ScorerRouting: ...

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
  - `open_rows` are the reference-set wrapper's open rows, with at least `id`, `component` and `delta_status`. A row without `delta_status` counts as NEW, unless T032's drift-form rule derives it from the baseline (S-12(b)).
  - `groups` is `parse_correlation_groups(...)["groups"]`, filtered to the open IDs.
  - A usable row is an entry of `baseline.rows`. A NEW finding whose ID is in `baseline.ids_in_any_row` goes to the agent, never to `carried` (ruling B).
- **`peer_divergence`** gives `divergent:composite_score:primary=<ID>` when the two composites differ, and otherwise `None`.
- **`original_scoring_date`** returns the stored scored-on date (renderer form), or the stored review date minus the stored SLA (legacy). If neither exists, D9's fallbacks apply in order:
  1. the baseline file's frontmatter date, flagged `corrected:review_date:baseline-date`;
  2. `None`, flagged `unchecked:review_date:scoring-date-unknown`, which tells `governance_for` to keep the stored review date.

  The last fallback, the run date plus the SLA (`corrected:review_date:clock-restarted`), is applied by `governance_for`.
- **`classify_band_change`** returns `none`, `corrected`, `retagged-up` or `retagged-down`. `band_with_baseline_tags` is the band recomputed with the baseline's recorded tags, or with no tags for a legacy row (ruling A's legacy case). When it equals the stored band and the rendered band differs, the change is a retag, up or down by band order.
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

```python
from typing import Iterable, Optional

def decode_references(text: str) -> str: ...
def parse_correlation_groups(content: str, member_ids: Optional[Iterable[str]] = None) -> dict: ...
def parse_sarif_member_set(sarif_text: str, *, with_scores: bool = False) -> dict: ...
def parse_controls_assessment_inputs(content: str) -> dict: ...
```

- **`decode_references` (T033)** is D3's one closed decoder.
  - It decodes exactly `&amp;`, `&lt;`, `&gt;`, `&#124;`, `&#96;`, `&#123;`, `&#10;` and `&#35;`, in a single left-to-right pass, and leaves anything else as written. Replaced text is never re-scanned, so `&amp;lt;` decodes to `&lt;`.
  - `parse_markdown_table` applies it to each cell after splitting the row on raw `|`, and so does every other reader of rendered text. GFM's `\|` isn't decoded.
- **`parse_correlation_groups` (T048, D8)** returns `{"groups": [{"group_id", "primary", "members"}], "errors": [{"line", "row", "reason"}]}`.
  - Groups come in Section 4a's order. `members` are canonical, in listed order, with the primary first, and filtered to `member_ids` when that is given.
  - A group left with fewer than two members is omitted, and an ID listed in two groups stays in the first.
  - A row whose group ID fails `tachi_parts`' group pattern, or whose members fail its finding pattern, goes to `errors`.
  - A missing or empty Section 4a gives `{"groups": [], "errors": []}`.
- **`parse_sarif_member_set` (T142, D8's fallback)** returns `{"members": [...], "groups": [...], "scores": {...}}`.
  - `members` are canonical IDs in result order, from `findingId/v1`, plus legacy peer references. A legacy reference is an allow-listed ID at the start of a `relatedLocations` entry's `message.text`, followed by `: `, and each one is grouped under its result.
  - `groups` take the shape `parse_correlation_groups` returns. `group_id` comes from the `correlation-group` property, and is `None` where the file names none.
  - `scores` is filled only with `with_scores=True`, for `risk-scores.sarif`: `{id: {"composite": Decimal or None, "band": str or None}}`, read across the property names the shipped files use.
  - Results whose `baselineState` or `baseline-state` property is `absent` are dropped, and no hash is ever read.
  - It raises `ValueError` on JSON that doesn't parse and on an empty extraction, so the stage stops before dispatch (KB 22).
- **`parse_controls_assessment_inputs` (T143, AR-T3)** returns `{"inputs": {id: item}, "errors": [...]}`.
  - Each item is the controls payload as `contracts/part-files.md` keys it, without `finding_id`, decoded. Narrative values keep their slot tokens, and evidence-class values come back as written.
  - A pre-1.1 file, which has no `### Assessment Inputs`, gives `{"inputs": {}, "errors": []}`.
  - A row whose field isn't in the controls payload's closed key set goes to `errors`.

## The persisted-inputs format: `risk-scores.md` §6 and `compensating-controls.md` §7

`render-risk-scores.py` writes `### Scoring Inputs` under `## 6. Score Integrity` (D9). `render-compensating-controls.py` writes `### Assessment Inputs` under `## 7. Analysis Integrity` (D2). The next run reads each back: §6 through `read_baseline_scores`, and §7 through `parse_controls_assessment_inputs`.

Both sections use one table, so the writers (R1, R2), the readers (R1b, P) and the templates (C, D) agree before any of them lands:

| ID | Field | Value |
|---|---|---|
| T-12 | control_status | partial |
| T-12 | evidence[0].snippet | first line&#10;second line |

- **One row per value.** A row holds one finding and one field that has a value. A null field or an empty list writes no row.
- **Order.** Rows go in S-2 order of ID, then in the payload's key order (`contracts/part-files.md`). §6's extra fields come last. List entries are indexed from 0, as in `evidence[1].summary`.
- **Field names** are the stage payload's key paths, such as `rationale.cvss`, `exploitability.known_techniques`, `subscore_rationale.skill_level` or `evidence[0].assessment.coverage.rationale`.
  - §6 adds the renderer's other step-1 inputs: `score_bounds` (low and high, joined by `,`), `tags` (sorted, joined by `,`, and empty for none) and `scored_on` (`YYYY-MM-DD`).
  - §7 holds the whole controls item (D2, AR-T3's reading).
- **Values** are escaped on write by D3's table-cell rule, and decoded on read with `decode_references`. Narrative values keep their slot tokens. Booleans are `true` or `false`, and integers are written in decimal.
- **Reading.**
  - A reader re-checks each value's class: closed values against their pattern or enum, and narrative values by D3's step 11 when they're re-resolved.
  - A row with an unknown field goes to the reader's issues or errors.
  - No number is ever read from a narrative value.
