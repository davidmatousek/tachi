# Quickstart: MITRE ATT&CK + ATLAS Catalog Expansion (F-A1.3)

**Feature**: 186 · **Date**: 2026-06-07

Reproducible verify/repro steps. All commands run from repo root on branch `186-mitre-catalog-expansion`.

## Prerequisites
- Dangling commits present (verify before anything else — they are unreachable from `main` and unpushed):
  ```bash
  git cat-file -t e58f247 && git cat-file -t 991e1ee   # both → "commit"
  ```
  If absent (fresh clone / post-`git gc`): recovery is impossible — see the FR-002 checked-in `restored-edges.yaml` instead, which is the durable fallback.

## Step 1 — Extract the restore-set (FR-002, do this FIRST)
```bash
git show e58f247:schemas/taxonomy/crosswalk.yaml > /tmp/cw_pre.yaml   # 551 edges
git show 991e1ee:schemas/taxonomy/crosswalk.yaml > /tmp/cw_post.yaml  # 438 edges
# Filter the (pre − post) diff to edges referencing the 16 gap IDs → specs/186-*/restored-edges.yaml
# (see research.md for the exact 16; annotate each with _resolvable + _blocked_on)
```

## Step 2 — Disposition the 6 missing ATLAS IDs (FR-003, architect gate)
```bash
# Authoritative source (per F-180 R7: atlas.mitre.org pages 404 via fetch — use the repo):
#   mitre-atlas/atlas-data techniques.yaml
# For each of AML.T0001/T0005/T0025/T0037/T0043/T0048 → add | reject | defer (+ rationale) on Issue #186.
```

## Step 3 — Apply edits
```bash
# a) Insert the 10 resolvable edges into schemas/taxonomy/crosswalk.yaml (strip _resolvable/_blocked_on keys).
# b) For each "add" ID: insert the mitre-atlas.yaml record in lexicographic position + restore its edge.
# c) Add the F-A1.3 provenance note to the mitre-atlas.yaml header.
```

## Step 4 — Verify (the acceptance gate)
```bash
python3 -c "import yaml; e=yaml.safe_load(open('schemas/taxonomy/crosswalk.yaml')); \
print('primary edges:', sum(1 for x in e if x['edge_type']=='primary'))"   # expect 536 (+k)

pytest tests/schemas/test_taxonomy_integrity.py -q                          # expect: 5 passed
```

## Step 5 — Guard against drift (FR-006 / US-3)
```bash
# Confirm ONLY the intended edges were added (none of the ~72 non-gap T029 removals, none of the 2 CWE-blocked):
git diff schemas/taxonomy/crosswalk.yaml | grep '^+- source:' | wc -l       # expect 10 (+k), not more
```

## Step 6 — Close
```bash
# CHANGELOG feat(186) entry; update specs/180-*/NEXT-SESSION.md decision trail; /aod.analyze; close #186.
```

## Expected end state
- `crosswalk.yaml`: 536 (+k) primary edges; all endpoints resolve.
- `mitre-atlas.yaml`: 30 (+k) records, still sorted, with F-A1.3 header note.
- `mitre-attack.yaml`: unchanged (701 records).
- `tests/schemas/test_taxonomy_integrity.py`: **5 passed**.
- Issue #186: 6/6 IDs dispositioned; closed `stage:done`.
