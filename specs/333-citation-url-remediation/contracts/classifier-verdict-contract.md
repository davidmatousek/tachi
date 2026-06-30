# Contract: Monitor Verdict Logic (re-classify path)

The only behavioral "contract" this feature changes is the monitor's status→verdict mapping in
`scripts/check-citation-urls.py::_verdict_for_status(url, status, final_url, detail)`. This is the
surface the synthetic-404 unit test (FR-8) validates and the code-reviewer audits (NFR-005).

## Current contract (unchanged for all hosts except documented anti-bot hosts)

| HTTP status | Verdict | Counted as confirmed rot by #332? |
|---|---|---|
| 200–299 | `HEALTHY` | No |
| 400, 404, 410, 451 | `LINK_ROT` | **Yes** |
| 401, 403, 429 | `NEEDS_REVIEW` | No |
| anything else (5xx, timeout) | `TRANSIENT` | No (never reported) |

## New contract (host-scoped override, additive)

A documented anti-bot host's status may be overridden to a softer verdict **before** the global
table is consulted. All other hosts are unaffected.

| Input (host, status) | Verdict | Rationale |
|---|---|---|
| `atlas.mitre.org`, 404 | `NEEDS_REVIEW` (override) | R7 anti-bot 404; IDs valid in `atlas-data` |
| `atlas.mitre.org`, 200–299 | `HEALTHY` | unchanged |
| `atlas.mitre.org`, 410/451 | `LINK_ROT` | unchanged — a genuine *gone* on this host still flags |
| any other host, 404 | `LINK_ROT` | **unchanged — real-rot detection preserved (NFR-005)** |
| any host, 401/403/429 | `NEEDS_REVIEW` | unchanged |

## Contract guarantees (assertions for the test + review)

1. **Host-scoped, not global**: `(other-host, 404) → LINK_ROT` MUST still hold. A change that makes *any* 404 needs-review violates the contract.
2. **Status-scoped**: only the enumerated status(es) for a host are overridden; `(atlas.mitre.org, 410) → LINK_ROT` still holds (genuine gone is not masked).
3. **Reversible & documented**: the override lives in one bounded table with an explaining comment; removing the entry restores the prior contract exactly.
4. **Offline-verifiable**: the mapping is a pure function of `(url, status)` — no network — so it is unit-tested over synthetic statuses (ADR-021), never a live fetch.

## Acceptance contract (FR-6, MANUAL-ONLY)

A `--no-cache` (`no_cache=true` dispatch) full-sweep monitor run MUST find **0** in-scope confirmed-rot
findings and self-close #332 with its recovery comment. A green #332 is necessary; a landing-content
spot-check on a sampled corrected URL is the sufficiency check (guards wrong-but-2xx).
