# Quickstart: Authoring F-182 `related` + `superseded` Edges

**Feature**: [spec.md](spec.md) · **Date**: 2026-06-07

Reproducible survey → author → verify flow for the crosswalk edge expansion. Any engineer can run this.

## Prerequisites

```bash
cd /Users/david/Projects/tachi
python -c "import yaml"                              # pyyaml present
pytest tests/schemas/test_taxonomy_integrity.py -q  # baseline: 5 passed
```

## Step 0 — Baseline counts (verify starting state)

```bash
python - <<'PY'
import yaml
edges = yaml.safe_load(open("schemas/taxonomy/crosswalk.yaml"))
from collections import Counter
c = Counter(e["edge_type"] for e in edges)
print(c)   # expect: {'primary': 542, 'related': 0, 'superseded': 0}
PY
```

## Step 1 — Survey & harvest (FR-002, FR-012) → `reference-edges.yaml`

Harvest candidate published relations from the four audited source classes, gated by what resolves in the current catalogs:

- **CWE↔CWE**: from cwe.mitre.org Relationships / XML views, candidates where **both** CWEs are among the 53 in `cwe.yaml`. Record Nature + View ID (FR-006).
- **OWASP-Web→CWE**: from owasp.org/Top10 category pages' counted CWE lists, where the target CWE is in `cwe.yaml`.
- **ATLAS→ATT&CK**: from atlas-data `ATT&CK-reference`, where the ATLAS id is in `mitre-atlas.yaml` (36) and the ATT&CK id is in `mitre-attack.yaml` (701).
- **OWASP-LLM→ATLAS**: from genai.owasp.org "Reference Links", where the ATLAS id is in `mitre-atlas.yaml`.

Write all candidates (with `source_class`, `confidence`, `citation`, `disposition`) to `specs/182-*/reference-edges.yaml` per [contracts/reference-edges.schema.md](contracts/reference-edges.schema.md). Compute `high_medium_core_total`. **If < 80 → set `tripwire_fired: true`** and proceed with the documented achievable floor (do NOT pad with `low` edges).

## Step 2 — Survey of `superseded` pairs (FR-007/008) → `deferred-superseded.md`

Scan catalogs for deprecation/replacement pairs whose **both** endpoints resolve today (e.g., a deprecated CWE + its replacement both in `cwe.yaml`; an ATT&CK deprecation pair both in `mitre-attack.yaml`). Authorable pairs → Step 3. Non-authorable classes → one-line rationale in `deferred-superseded.md` (must exist even if the authored set is empty).

## Step 3 — Author into `crosswalk.yaml` (FR-001/003/004/005/006/007)

Promote `disposition: authored` candidates from `reference-edges.yaml` into `crosswalk.yaml` — **strip annotation keys** (`source_class`, `disposition`) so the crosswalk carries only `{source, target, edge_type, confidence, citation}`. Re-run the integrity suite after each batch and keep it green:

```bash
pytest tests/schemas/test_taxonomy_integrity.py -q
```

## Step 4 — Verify (FR-013) + anti-drift audit (FR-014)

```bash
# structural gate
pytest tests/schemas/test_taxonomy_integrity.py -q          # 5 passed

# count + band check
python - <<'PY'
import yaml
from collections import Counter
edges = yaml.safe_load(open("schemas/taxonomy/crosswalk.yaml"))
c = Counter(e["edge_type"] for e in edges)
print(c)                                  # primary still 542; related in [80,150]; superseded = authorable set
assert c["primary"] == 542, "primary floor disturbed"
assert 80 <= c["related"] <= 150 or "tripwire documented"
# uniqueness
keys = [(e["source"]["taxonomy"], e["source"]["id"], e["target"]["taxonomy"], e["target"]["id"], e["edge_type"]) for e in edges]
assert len(keys) == len(set(keys)), "duplicate edge"
print("OK")
PY
```

**Anti-drift audit (manual, FR-014)**: for every `high`/`medium` related edge, open its citation and confirm the source supports the label; downgrade any that don't. Confirm **0** `high`/`medium` edges from OWASP-LLM→CWE.

## Step 5 — README rubric extension (FR-009) + close (FR-015)

- Extend `schemas/taxonomy/README.md` with the related/superseded calibration section (worked example per source class, the View-ID rule, the OWASP-LLM→CWE prose-only caution).
- Add `crosswalk.yaml` header provenance note (F-186 convention) + `feat(182)` CHANGELOG entry; close Issue #182 `stage:done`.

## Done when

5/5 integrity green · `related` ∈ [80,150] (or documented floor) · `primary` = 542 · 0 duplicates · anti-drift audit clean · `superseded` = authorable set with `deferred-superseded.md` present · README extended · 0 schema/test/ADR changes.
