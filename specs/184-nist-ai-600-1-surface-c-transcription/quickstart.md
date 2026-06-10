# Quickstart: Verifying F-184 (NIST AI 600-1 Surface C Transcription)

All commands from repo root. **Interpreter pin** (Team-Lead C5): use `/usr/bin/python3` — the default `python3` lacks pytest/pyyaml.

## 1. Integrity suite (the acceptance oracle — 5/5 required)

```bash
/usr/bin/python3 -m pytest tests/schemas/test_taxonomy_integrity.py -v
```

Baseline (pre-change, HEAD `f57a9c1`): 5 passed in ~1.0s. Required green at every commit boundary (spec FR-008).

## 2. Edge-class checks (W2 gate)

```bash
/usr/bin/python3 - <<'EOF'
import yaml
edges = yaml.safe_load(open('schemas/taxonomy/crosswalk.yaml'))
cls = lambda s, t: [e for e in edges
                    if e['source']['taxonomy'] == s and e['target']['taxonomy'] == t]

added   = cls('tachi-stride-ai-category', 'nist-ai-600-1')
removed = cls('tachi-stride-ai-category', 'nist-ai-rmf')
ctrl_rmf = cls('tachi-control-category',  'nist-ai-rmf')

print(f"Surface C edges (expect 15): {len(added)}")
print(f"Drift class    (expect 0):  {len(removed)}")
# 31 = 27 Surface B table cells + 4 legacy non-table edges (out of F-184 scope — do NOT remove)
print(f"control→rmf    (expect 31): {len(ctrl_rmf)}")
assert all(e['edge_type'] == 'primary' and e['confidence'] == 'high' and
           e['citation'] == '.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md'
           for e in added)
assert all(isinstance(e['target']['id'], str) for e in added), "target ids must be strings (quoted)"
print("pairs:", sorted((e['source']['id'], e['target']['id']) for e in added))
EOF
```

Expected pairs = the 15-row C2 table in [contracts/surface-c-transcription.contract.md](contracts/surface-c-transcription.contract.md).

## 3. Count arithmetic (W2/W3 gate)

```bash
/usr/bin/python3 - <<'EOF'
import yaml, collections
edges = yaml.safe_load(open('schemas/taxonomy/crosswalk.yaml'))
c = collections.Counter(e['edge_type'] for e in edges)
print(f"primary={c['primary']} related={c['related']} superseded={c['superseded']} total={len(edges)}")
assert (c['primary'], c['related'], c['superseded'], len(edges)) == (541, 37, 0, 578)
print("arithmetic OK: 541/37/0 = 578")
EOF
```

## 4. Catalog checks (W1 gate)

```bash
/usr/bin/python3 - <<'EOF'
import yaml
recs = yaml.safe_load(open('schemas/taxonomy/nist-ai-600-1.yaml'))
assert len(recs) == 12, len(recs)
assert all(isinstance(r['id'], str) for r in recs), "ids must be quoted strings"
assert [r['id'] for r in recs] == [f"2.{i}" for i in range(1, 13)], "publication order"
assert all(r['url'] == 'https://doi.org/10.6028/NIST.AI.600-1' and r['cwe_refs'] == [] for r in recs)
print("catalog OK:", [r['id'] for r in recs])
EOF
```

## 5. Byte-untouched + exemption checks (W1/W3/W4 gates)

```bash
# _sort_key_nist (code + docstring) must be byte-identical to main — AST extraction
# comparison (a diff-grep false-FAILs on context lines of adjacent hunks)
/usr/bin/python3 - <<'EOF'
import ast, subprocess
def fn_src(src, name="_sort_key_nist"):
    lines = src.splitlines()
    fn = next(n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef) and n.name == name)
    return "\n".join(lines[fn.lineno - 1:fn.end_lineno])
new = open('tests/schemas/test_taxonomy_integrity.py').read()
old = subprocess.check_output(['git', 'show', 'main:tests/schemas/test_taxonomy_integrity.py'], text=True)
assert fn_src(old) == fn_src(new), "FAIL: _sort_key_nist changed"
print("OK: _sort_key_nist byte-untouched (code + docstring)")
EOF

# Exempt surfaces must show zero diffs
git diff main --stat -- docs/architecture/01_system_design/README.md specs/180-taxonomy-crosswalk-collection/ | grep . && echo "FAIL: exempt surface touched" || echo "OK: exempt surfaces untouched"

# Baseline-fixture byte-identity test still green
/usr/bin/python3 -m pytest tests/scripts/test_init_sh_substitution.py -q
```

## 6. Stale-count sweep check (W4 gate — inventory surfaces only)

```bash
grep -n "7-value\|7 catalog\|seven taxonom\|taxonomy (7)\|542\|(14)" \
  tests/schemas/test_taxonomy_integrity.py \
  schemas/taxonomy/README.md \
  schemas/taxonomy/crosswalk.yaml \
  && echo "check hits above" || echo "OK: sweep clean"
# `taxonomy (7)` catches the crosswalk header enum line (comment, invisible to the suite);
# `542`/`(14)` catch the stale composition + README §2 "(14) … 41 edges" text.
# ONE expected historical survivor: the crosswalk-header F-186 lineage line "(526 -> 542)" —
# any other hit is a sweep failure.
# docs/architecture/README.md L54 blurb checked manually (historical '7-value' phrasing inside the
# ratified-decision description is updated only via the F-184 amendment clause per contract C5)
```

## 7. Full pre-PR gate (W3)

```bash
/usr/bin/python3 -m pytest tests/schemas/ tests/scripts/test_init_sh_substitution.py -q
# then: /aod.analyze (cross-artifact consistency)
```
