# Contract: Tracking Issue Lifecycle (`gh`)

Single deduplicated, self-updating, self-closing issue. Native `gh` only (NFR-007).

## Identity

- **Title sentinel (load-bearing dedup)**: `[link-rot] Taxonomy citation link-rot — open findings`
- **Lookup**: `gh issue list --state open --search '"[link-rot] Taxonomy citation link-rot — open findings" in:title'`
- **Labels**: apply `follow-on-180` (existing lineage label). Best-effort ensure a `link-rot` label exists (`gh label create link-rot --color … 2>/dev/null || true`) — convenience only; the title sentinel is the dedup mechanism, not the label.

## Body schema

A single delimited machine block (rewritten in place each run) — see `data-model.md` `TrackingIssueBody`. Two sections: **Confirmed link-rot (N)** and **Needs manual verification (M)**, each grouped by host; per-URL line carries URL · final status · optional "previously healthy `<date>`"; sub-bullets list every source location.

## Transitions (exactly one open issue, ever)

| Pre-state | Condition | Action |
|---|---|---|
| no open issue | `confirmed_rot > 0` | `gh issue create` (sentinel title, body machine block, `follow-on-180` label) |
| open issue | `confirmed_rot > 0` | `gh issue edit` (replace machine block) **+** `gh issue comment` (dated delta: newly-rotted / newly-recovered) |
| open issue | `confirmed_rot == 0` | `gh issue comment` ("all citations healthy as of `<date>`") **+** `gh issue close` |
| no open issue | `confirmed_rot == 0` | no-op |

## Rules

- **Confirmed rot is the sole open/close driver.** `needs-review` entries (403/401/429) never create or keep an issue open on their own; they appear only as a secondary section inside an issue that already has confirmed rot.
- **No per-run or per-URL issues** — ever.
- Delta comment is best-effort; failure to comment must not block the edit/close (graceful degradation, but surfaced in the job log).
- Closing always comments first (audit trail), then closes.
