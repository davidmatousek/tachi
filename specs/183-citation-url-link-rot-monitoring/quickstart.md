# Quickstart: Citation-URL Link-Rot Monitoring (#183)

How to develop, test (offline), and validate (live dispatch) the link-rot monitor.

## 1. Run the offline guard + classifier tests (no network)

These run in `pytest` and are PR-gate-eligible — they perform **no** outbound fetch.

```bash
python3 -m pytest tests/schemas/test_citation_linkrot_parity.py -v
```

Asserts:
- **Set-parity** (both directions): the checker's glob+filter URL set == `test_citation_shape()`'s URL set.
- **Field rule**: crosswalk → `citation`; all other `schemas/taxonomy/*.yaml` → `url`.
- **Classifier dispositions**: stubbed responses (200, 301→200, 404, 410, 403, 429, 500, timeout, HEAD-405→GET-200, redirect-loop, >5-hops) map to the correct verdict.
- **NFR-001 boundary**: importing the test module opens no socket / resolves no DNS.

## 2. Dry-run the checker locally (network fetch, but no issue I/O)

```bash
python3 scripts/check-citation-urls.py --dry-run --json
```

- Fetches the live URLs and prints the rendered issue body + JSON summary to stdout.
- **No** `gh` calls (safe to run anywhere). Use `--no-cache` to force a full sweep.
- Tune politeness while iterating: `--max-host-concurrency 2 --politeness-ms 250`.

## 3. Validate the deterministic sentinel locally (no network for the sentinel)

```bash
python3 scripts/check-citation-urls.py --dry-run --inject-sentinel-rot --json
```

Confirms a pre-classified synthetic `LINK_ROT` finding (`https://example.invalid/tachi-linkrot-sentinel`) appears in the rendered body with `issue_action` that *would* be `created/updated` — without touching the network or GitHub.

## 4. Validate the full lifecycle via GitHub Actions (live, two runs)

Once merged, validate SC-002 → SC-003 with two manual dispatches:

```bash
# Run 1 — inject sentinel rot ⇒ exactly one tracking issue is created/updated
gh workflow run tachi-citation-linkrot.yml -f inject_sentinel_rot=true

# (verify) exactly one open issue with the sentinel title naming the sentinel URL + 404 + source
gh issue list --state open --search '"[link-rot] Taxonomy citation link-rot — open findings" in:title'

# Run 2 — no sentinel ⇒ zero confirmed rot ⇒ the tracking issue self-closes
gh workflow run tachi-citation-linkrot.yml -f inject_sentinel_rot=false
```

Expected: Run 1 leaves exactly one open tracking issue; Run 2 comments "all citations healthy…" and closes it. This is the reproducible TL-2 validation — it never depends on a live external 404.

## 5. Update the README note (FR-009)

After the monitor is live, edit `schemas/taxonomy/README.md` (~line 224): replace the "out of F-A1 scope" deferral with a reference to the scheduled monitor (`.github/workflows/tachi-citation-linkrot.yml`).

## Definition-of-done quick check

- `pytest` green, **network-free**; no HTTP module reachable from collection.
- `tachi-citation-linkrot.yml`: `schedule` + `workflow_dispatch` only; `contents: read` + `issues: write`.
- Two-run dispatch: one issue created, then self-closed.
- No new runtime dependency in `requirements-dev.txt`.
- README note updated.
