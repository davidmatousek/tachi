# Contract: `.github/workflows/tachi-citation-linkrot.yml`

Modeled file-for-file on `tachi-maestro-coverage.yml` (single-concern, single OS/runner).

## Triggers (MUST)

```yaml
on:
  schedule:
    - cron: "17 9 * * 1"        # Mondays 09:17 UTC — off-:00 (cron-throttle dodge), off-peak
  workflow_dispatch:
    inputs:
      inject_sentinel_rot:
        description: "Inject a pre-classified synthetic rot finding to validate the issue lifecycle (no network)."
        type: boolean
        default: false
```

**MUST NOT** declare `on: pull_request` or `on: push` (NFR-001 — the load-bearing invariant).

## Permissions (MUST — least privilege, NFR-005)

```yaml
permissions:
  contents: read     # checkout
  issues: write      # create/edit/comment/close the tracking issue
```

No `pull-requests`, no `contents: write`.

## Job steps (single job, `ubuntu-latest`)

1. `actions/checkout@v4`
2. `actions/setup-python@v5` with `python-version: "3.11"`
3. `actions/cache@v4` — restore the ledger:
   - `path: linkrot-ledger.json`
   - `key: linkrot-ledger-v1-${{ github.run_id }}`
   - `restore-keys: |` → `linkrot-ledger-v1-`  (rolling accumulation; restore newest prior)
4. Run checker:
   ```yaml
   - run: python scripts/check-citation-urls.py --json ${{ inputs.inject_sentinel_rot && '--inject-sentinel-rot' || '' }}
     env:
       GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}   # ambient token for gh
   ```
5. **Cache save**: use the **combined** `actions/cache@v4` action (the single step #3 above), NOT `actions/cache/restore`. The combined action auto-saves the `path` in its post-job hook keyed by the primary `key` (`linkrot-ledger-v1-${{ github.run_id }}`); because the primary key always misses by design, the post-save always fires and the ledger accumulates. Do **not** split into `restore`-only (it performs no save → the ledger never accumulates — architect MINOR-1). *(Operational note, MINOR-2: `actions/cache` is a new pattern for this repo; devops validates restore-key accumulation on the first two dispatch runs per quickstart §4.)*

## Invariants

- No `pip install` of a new runtime dependency — `pyyaml` already present; install it inline (`pip install 'pyyaml>=6'`) mirroring the precedent, or rely on setup-python + a one-line install. **No `requests`.**
- The job is a **monitor**: a found-rot run is still a green run (checker exits 0); only infra failure is red.
- `gh` uses the ambient `GITHUB_TOKEN` (`GH_TOKEN` env) — no PAT, no secret beyond the auto-provided token.
