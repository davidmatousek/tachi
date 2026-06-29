# Data Model: Citation-URL Remediation (F-333)

This feature has **no database and no new schema**. The "data model" here is (a) the existing taxonomy-record citation field this feature edits, and (b) the small in-script structures the re-classify path adds. No taxonomy record **shape** changes (out of scope).

## Existing entities touched (values only, shape unchanged)

### Taxonomy citation (`schemas/taxonomy/*.yaml`)
- **`url:`** (record-level, e.g. `mitre-atlas.yaml`, `nist-ai-rmf.yaml`) — the authority URL for a catalog record.
- **`citation:`** (edge-level, `crosswalk.yaml`) — the authority URL (or local-file path) backing a crosswalk edge.
- **Validation (unchanged)**: `test_citation_shape()` requires each citation be non-empty and either URL-shaped (`^https?://`) or resolve to a repo file. This feature edits the **string value**; the field, type, and validation are untouched.

### Fix-class (analysis grouping — not a stored entity)
| Class | Member set | Resolution | Mutation |
|---|---|---|---|
| ATLAS | 36 distinct `AML.Txxxx` IDs (37 `url:` refs; ~96 `citation:` refs) | Host-scoped re-classify (likely) | **None to data** (likely); else 36 distinct / ~133 occurrences |
| NIST | 1 shared DOI across 73 records | Re-point to verified AI 100-1 canonical | 1 pattern → 73 records |
| OWASP | subset of 16 distinct `genai.owasp.org` URLs (`llm01` live = excluded) | Re-point confirmed-dead to restructured canonicals | bounded subset |

## New in-script structures (re-classify path, `scripts/check-citation-urls.py`)

### `_HOST_STATUS_OVERRIDES` (new, module-level)
- **Purpose**: map a known anti-bot host + HTTP status → an override verdict, consulted before the global rot/needs-review frozensets.
- **Shape (illustrative)**: `{ "atlas.mitre.org": { 404: Verdict.NEEDS_REVIEW } }`
- **Invariants**: bounded (only documented anti-bot hosts), reversible (delete the entry to restore prior behavior), host-scoped (no effect on other hosts → NFR-005 preserved). Global `_HARD_ROT_STATUSES` / `_NEEDS_REVIEW_STATUSES` unchanged.

### `Verdict` (existing enum — reused, not extended)
- `HEALTHY` (2xx) · `LINK_ROT` (400·404·410·451) · `NEEDS_REVIEW` (401·403·429) · `TRANSIENT` (else). No new verdict value — the override reuses `NEEDS_REVIEW`.

## State transition (acceptance)

`#332 open (41 confirmed rot)` → *apply fixes* → `--no-cache monitor run` → `0 in-scope confirmed rot` → `#332 self-closed (recovery comment)`. The override moves ATLAS findings from the `LINK_ROT` set into `NEEDS_REVIEW`, which the tracker does not count as confirmed rot.
