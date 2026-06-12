# Quickstart: CWE Catalog Expansion — T029 Drift-Edge Restoration (F-A1.2)

**Feature**: 185 · verification + regeneration runbook. All commands from repo root on branch `185-cwe-catalog-expansion`.

## 0. Sanity: recovery objects + baseline state

```bash
git cat-file -t e58f247 && git cat-file -t 991e1ee          # both → commit
git show e58f247:schemas/taxonomy/crosswalk.yaml | /usr/bin/python3 -c "import sys,yaml;print(len(yaml.safe_load(sys.stdin)))"   # 551
/usr/bin/python3 -c "import yaml;print(len(yaml.safe_load(open('schemas/taxonomy/crosswalk.yaml'))))"                            # 578
/usr/bin/python3 -m pytest tests/schemas/test_taxonomy_integrity.py -q    # 5 passed (~1s)
```

> Count edges via YAML parse, never `grep -c "edge_type:"` — the naive grep over-counts +1 (a commented header example line matches). Architect tasks-review erratum, 2026-06-11.

> **Known red pre-state**: `tests/scripts/test_backward_compatibility.py` is **6/6 FAIL on main today** — inherited #186 ATLAS drift (mitre-atlas 30→36, CA pages only; verified at plan review). Do NOT "fix" this before W1-3; the W1-3 regen absorbs it together with the CWE delta and restores green.

## 1. W0-b — extract the restore-set (first build task)

```bash
/usr/bin/python3 specs/185-cwe-catalog-expansion/scripts/extract_restore_set.py
# → specs/185-cwe-catalog-expansion/restored-edges.yaml
# expect: 67 edges (65 owasp→cwe + 2 mitre-attack→cwe), 40 distinct _blocked_on IDs,
#         34 high / 32 medium / 1 low, all primary — commit immediately
```

## 2. W0-a — harvest + disposition input

```bash
curl -sO https://cwe.mitre.org/data/xml/cwec_v4.20.xml.zip && unzip -o cwec_v4.20.xml.zip
/usr/bin/python3 specs/185-cwe-catalog-expansion/scripts/harvest_cwe_names.py cwec_v4.20.xml
# → 40-row table: id, name (verbatim), type (Weakness|Category|Pillar), status
# architect publishes add/reject/defer per ID on Issue #185 (zip/xml are NOT committed)
```

## 3. W1-1 — insert records, then gate

```bash
# scripted lexicographic merge of the add-set into schemas/taxonomy/cwe.yaml
/usr/bin/python3 -m pytest tests/schemas/test_taxonomy_integrity.py -q   # 5 passed
grep -c "^- id: " schemas/taxonomy/cwe.yaml                              # 53+|add-set| (93 add-all)
```

## 4. W1-2 — restore edges, then gate

```bash
# insert add-set-targeted edges from restored-edges.yaml (strip _blocked_on), re-run dedupe check
/usr/bin/python3 -m pytest tests/schemas/test_taxonomy_integrity.py -q   # 5 passed
```

## 5. W1-3 — regenerate the 6 gated baselines

Per [contracts/baseline-regen.contract.md](contracts/baseline-regen.contract.md): recipe + CA-page-only diff verification (expected deltas: cwe 53→93 AND inherited mitre-atlas 30→36), restore `report-data.typ` after the final run, then:

```bash
/usr/bin/python3 -m pytest tests/scripts/test_backward_compatibility.py -q   # 6 passed (red→green flip; slow — typst required)
```

## 6. W2 — verification gates

```bash
/usr/bin/python3 specs/185-cwe-catalog-expansion/scripts/name_diff.py cwec_v4.20.xml   # 0 mismatches (all 40)
/usr/bin/python3 -m pytest tests/ -q                                                   # full suite green
grep -rn "53 record\|53-record" docs/ schemas/ | grep -v specs/                        # stale-count sweep → empty
```

## 7. Done criteria

Spec SC-001..SC-006 all evidenced; Issue #185 carries the 40-line disposition; CHANGELOG `feat(185)`; ADR-037 D-7 annotated; F-180 NEXT-SESSION residual closed; `/aod.analyze` clean.
