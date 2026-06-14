# Contract: `scripts/check-citation-urls.py` CLI

The checker is invoked directly by the workflow (no slash command, no import from `tests/`).

## Invocation

```
python scripts/check-citation-urls.py [OPTIONS]
```

## Options

| Flag | Type | Default | Purpose |
|---|---|---|---|
| `--taxonomy-glob` | str | `schemas/taxonomy/*.yaml` | discovery glob (overridable for tests) |
| `--ledger-path` | path | `linkrot-ledger.json` | last-success ledger (cache-restored) |
| `--no-cache` | flag | off | ignore ledger; check every URL (forces full sweep) |
| `--ttl-days` | int | `21` | skip URLs whose `last_ok` is newer than this |
| `--max-host-concurrency` | int | `3` | per-host in-flight cap (2–3) |
| `--global-concurrency` | int | `10` | global thread-pool ceiling |
| `--politeness-ms` | int | `150` | inter-request delay within a host bucket |
| `--connect-timeout` | float | `10` | seconds |
| `--read-timeout` | float | `15` | seconds |
| `--inject-sentinel-rot` | flag | off | append a pre-classified synthetic rot finding (TL-2 deterministic validation; no fetch) |
| `--dry-run` | flag | off | classify + render, but perform **no** `gh` issue I/O (prints body to stdout) |
| `--json` | flag | off | emit the machine summary to stdout |

## Behavior contract

- **Discovery**: glob (never a hardcoded file list); extract `citation` from `crosswalk.yaml`, `url` from all other matched YAMLs; keep `^https?://` only; drop file-paths; dedup with a URL→sources map.
- **Classification**: HEAD→ranged-GET fallback; ≤5 redirects; 2 retries on transient only; never retry 4xx; verdict per `data-model.md`.
- **Throttling**: per-host `Semaphore` under the global pool; descriptive `User-Agent` (`tachi-linkrot-monitor/1.0 (+https://github.com/davidmatousek/tachi; citation integrity check)`) + `Accept: text/html,*/*`; honor `Retry-After`.
- **Ledger**: TTL skip; cache-miss = check-all; only 2xx writes `last_ok`; 4xx never cached OK.
- **Issue I/O**: via `gh` only; single sentinel-titled issue; create / edit-in-place + delta comment / close-on-recovery. Suppressed entirely under `--dry-run`.

## Exit codes (load-bearing — monitor, not gate)

| Code | Meaning |
|---|---|
| `0` | run completed successfully — **including when link-rot was found** (rot is reported via the issue, not the exit code) |
| `2` | infrastructure error (cannot read taxonomy dir, `gh`/auth failure, malformed YAML) |

**Rule**: the script MUST NOT exit non-zero merely because rotted URLs exist. The workflow is a monitor; a non-zero "rot found" code would make a red run indistinguishable from infra failure and invites someone to wire it as a gate (violates NFR-001 intent). Only genuine infra failures are non-zero.

## stdout `--json` summary shape

```json
{
  "checked": 412,
  "skipped_cached": 488,
  "healthy": 405,
  "link_rot": 1,
  "needs_review": 6,
  "transient": 0,
  "issue_action": "created|updated|closed|none",
  "issue_number": 331,
  "sentinel_injected": false
}
```
