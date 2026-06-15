# Data Model: Citation-URL Link-Rot Monitoring (#183)

This feature has no database. "Data model" here means the in-memory structures the checker (`scripts/check-citation-urls.py`) builds and the JSON ledger it persists to the Actions cache. All structures are plain stdlib types (`dict`, `list`, `dataclass`, `enum.Enum`); no ORM, no schema migration.

---

## Entity: `SourceLocation`

Where a URL is cited. One URL maps to many.

| Field | Type | Notes |
|---|---|---|
| `file` | `str` | basename of the taxonomy YAML, e.g. `mitre-attack.yaml` or `crosswalk.yaml` |
| `kind` | `"catalog"` \| `"crosswalk"` | which extraction rule produced it |
| `record_ref` | `str` | catalog: the record `id` (e.g. `T1234`); crosswalk: `"<src.taxonomy>:<src.id> → <dst.taxonomy>:<dst.id>"` |

**Display form**: catalog → `mitre-attack.yaml: T1234`; crosswalk → `crosswalk edge owasp:LLM01 → cwe:CWE-77`.

---

## Entity: `UrlCitation`

A distinct in-scope URL plus its back-references. Built by `discover_urls()`.

| Field | Type | Notes |
|---|---|---|
| `url` | `str` | matches `^https?://` (the integrity test's `URL_REGEX`) |
| `host` | `str` | `urllib.parse.urlsplit(url).hostname` — the throttling/grouping key |
| `sources` | `list[SourceLocation]` | every citing location (≥1) |

**Validation / derivation rules**:
- Only `^https?://` values are retained; internal file-path citations are dropped (already covered offline by `test_citation_shape()`).
- Field rule: crosswalk edges → `citation`; all other `schemas/taxonomy/*.yaml` → `url`.
- Dedup key is the exact URL string; identical URLs from different records merge into one `UrlCitation` with multiple `sources`.

---

## Entity: `Classification` (result of fetching one URL)

| Field | Type | Notes |
|---|---|---|
| `url` | `str` | the checked URL |
| `verdict` | `Verdict` enum | see below |
| `final_status` | `int \| None` | HTTP status after redirects/retries; `None` for DNS/conn failures/timeout |
| `final_url` | `str \| None` | post-redirect URL if it differed |
| `detail` | `str` | short reason, e.g. `"HEAD 405 → GET 200"`, `"redirect loop"`, `"timeout x3"` |

### `Verdict` enum

| Value | Triggers | Reported as |
|---|---|---|
| `HEALTHY` | final 2xx | nothing (writes ledger) |
| `LINK_ROT` | final 404 / 410 / post-retry hard-4xx (400/451) | **confirmed rot** (issue) |
| `NEEDS_REVIEW` | 401 / 403 / 429 | "needs manual verification" section (issue, separate) |
| `TRANSIENT` | 5xx / timeout / DNS / conn-reset after retries; redirect loop or >5 hops also → reported under broken | not reported (except loop/hop-exceed → treated as rot-broken) |

**State rules**:
- 4xx is **never** retried (deterministic). 5xx/timeout/conn → 2 retries, exp backoff (1→2→4s) + jitter.
- Classification is always on the **final** status after ≤5 redirects.
- A redirect **loop or >5 hops** classifies as broken → reported alongside `LINK_ROT`.
- HEAD returning 405/403/501 → retry once as ranged `GET` (`Range: bytes=0-0`) before verdict.

---

## Entity: `LedgerEntry` (persisted to `actions/cache`)

The per-URL last-success ledger. File: `linkrot-ledger.json` in the runner workspace (restored/saved via `actions/cache@v4`); **never committed to the repo**.

```json
{
  "https://attack.mitre.org/techniques/T1059/": {
    "last_ok": "2026-06-08T09:18:42Z",
    "last_status": 200
  }
}
```

| Field | Type | Notes |
|---|---|---|
| `last_ok` | ISO-8601 UTC `str` | timestamp of the most recent 2xx-final outcome |
| `last_status` | `int` | most recent observed final status (enables "previously healthy on `<date>`" context — adopted plan decision) |

**Lifecycle rules (FR-006)**:
- **TTL skip**: if `now - last_ok < ~21 days`, the URL is skipped this run (assumed healthy *only because it was recently confirmed*).
- **Cache miss / eviction**: treated as "check everything" — never "assume healthy."
- **Write rule**: only a **2xx-final** outcome writes/refreshes `last_ok`. A 4xx is **never** written as OK; `last_status` may record the 4xx for context but the URL is re-checked every run until it recovers.
- The ledger is an **optimization, never a source of truth** — correctness of "is this URL rotted now?" never depends on it.

---

## Entity: `TrackingIssueBody`

The rendered Markdown body of the single tracking issue (FR-007). Contains a machine-parseable block so the next run can diff state.

```markdown
<!--linkrot:start-->
## Confirmed link-rot (N)

### attack.mitre.org
- `https://attack.mitre.org/techniques/T9999/` — **404** — previously healthy 2026-05-18
  - mitre-attack.yaml: T9999
  - crosswalk edge owasp:LLM01 → mitre-attack:T9999

## Needs manual verification (M) — possibly bot-blocked
### cwe.mitre.org
- `https://cwe.mitre.org/data/definitions/1427.html` — 403
  - cwe.yaml: CWE-1427
<!--linkrot:end-->

_Last run: 2026-06-15T09:18Z · sentinel: `[link-rot] Taxonomy citation link-rot — open findings`_
```

| Element | Rule |
|---|---|
| Machine block | delimited `<!--linkrot:start--> … <!--linkrot:end-->`; rewritten in place each run |
| Grouping | by host, within each verdict section |
| Per-URL line | URL · final status · (optional) "previously healthy `<date>`" from `last_status`/`last_ok` |
| Sub-bullets | every `SourceLocation` display form |
| Confirmed vs needs-review | two distinct sections; needs-review never counts toward the "rot==0 ⇒ close" decision |

---

## State Transitions: Tracking Issue Lifecycle (FR-007 / NFR-006)

Keyed by stable title sentinel `[link-rot] Taxonomy citation link-rot — open findings`.

```
                 ┌────────────── confirmed_rot == 0 ──────────────┐
                 ▼                                                 │
        (no open issue)                                            │
            │   confirmed_rot > 0                                  │
            ▼                                                      │
   gh issue create ──► (open issue) ──── confirmed_rot > 0 ───► gh issue edit (machine block)
                              │                                    + gh issue comment (dated delta)
                              │ confirmed_rot == 0
                              ▼
                   gh issue comment "all citations healthy as of <date>"
                   gh issue close  ──► (no open issue)
```

**Invariants**:
- At most **one** open tracking issue at any time (title-sentinel dedup; never per-run/per-URL).
- `needs-review`-only (zero confirmed rot) does **not** create or keep an issue open — confirmed rot is the sole open/close driver. (Needs-review entries ride along in an open issue's body only when confirmed rot also exists.)
- Recovery always posts a comment before closing (audit trail).

---

## Sentinel Injection (TL-2, deterministic validation)

When `--inject-sentinel-rot` is passed (wired to the `workflow_dispatch` input `inject_sentinel_rot`), the checker appends a **pre-classified** `Classification(url="https://example.invalid/tachi-linkrot-sentinel", verdict=LINK_ROT, final_status=404, detail="injected sentinel")` directly into the confirmed-rot set **without any network fetch**, and a synthetic `SourceLocation(file="(sentinel)", kind="catalog", record_ref="validation")`. This drives the create/update path deterministically; a follow-up run with the flag off yields zero confirmed rot → self-close. `example.invalid` (RFC 2606 reserved) guarantees the identity can never collide with a real citation, and because it is injected pre-classified it is never resolved.
