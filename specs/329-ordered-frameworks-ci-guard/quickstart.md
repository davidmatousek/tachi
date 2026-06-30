# Quickstart / Verification Recipe — Feature 329 (Catalog-Drift CI Guard)

Local commands to build, run, and verify the guard. No network. Rendering (`typst`) runs ONLY in the T001 pre-state and the regen script.

## T001 — pre-state go/no-go (build hour-zero, OQ-3)

```bash
# Is the byte-identity suite green on the current tree? (the one place rendering is allowed)
python3 -m pytest tests/scripts/test_backward_compatibility.py -q
```
- **Green** → proceed; emit the sidecar from the current tree (guard goes green immediately).
- **Red** → bounded remediation: run the regen script (below) to refresh the 6 baselines AND emit the sidecar, in this same change-set, BEFORE wiring the guard green. (Git evidence: green is highly likely — Risk-4 Low.)

## Run the guard (the CI gate, environment-independent)

```bash
# Compare live ORDERED_FRAMEWORKS fingerprints against the committed sidecar.
python3 scripts/check-catalog-drift.py            # exit 0 = clean; exit 1 = drift (+ message to stderr)
```
Sub-second; no typst, no network. Fails closed if `examples/ca-baseline-fingerprints.json` is missing/partial/unparseable (FR-008).

## Regenerate baselines + emit the sidecar (the only sidecar producer — FR-002/OQ-1)

```bash
scripts/regenerate-ca-baselines.sh
# loops the 6 BASELINE_EXAMPLES under SOURCE_DATE_EPOCH=1700000000, recompiles the baselines,
# restores report-data.typ (D-9 invariant 5), then runs `check-catalog-drift.py --emit` as its last step.
git status            # expect: 6 baselines (if content changed) + examples/ca-baseline-fingerprints.json
```
Never hand-edit the sidecar — advance it only by re-running this script.

## Run the synthetic + live test (FR-007)

```bash
python3 -m pytest tests/scripts/test_catalog_drift_guard.py -q
```
Covers: live-tree==sidecar (real gate); grow / ID-swap / `out_of_scope`-flip → drift; citation-only (#333) / non-member (`nist-ai-600-1`) / clean → no drift. Each synthetic case clears `_load_framework_yaml_records.cache_clear()` (Risk-3 false-green guard).

## Verify the CI workflow locally (shape check)

```bash
# Dual-trigger + single-source path anchor + single runner + least privilege
grep -nE 'pull_request|push:|branches:|&drift_paths|\*drift_paths|ubuntu-latest|contents: read' \
  .github/workflows/tachi-catalog-drift.yml
```
Expect: `pull_request` + `push: branches:[main]` both resolving `*drift_paths`; one `ubuntu-latest`; `permissions: contents: read`.

## Negative checks (prove the guard actually bites)

```bash
# 1) Drift is caught: add/rename a record id in a member catalog, do NOT re-emit, then:
python3 scripts/check-catalog-drift.py ; echo "exit=$?"   # expect exit=1 naming the framework
git checkout -- schemas/taxonomy/<member>.yaml            # revert the probe

# 2) Count-neutral edit is ignored: change only a citation string (no id/out_of_scope change):
python3 scripts/check-catalog-drift.py ; echo "exit=$?"   # expect exit=0
git checkout -- schemas/taxonomy/<member>.yaml
```

## Deliver gate (KB-18)

Before any merge or direct-to-main doc push: confirm the branch is current and local `main`==`origin/main` (full-tree diff), then merge via devops and verify a release-please PR opens for the `feat(329):` squash-merge.
