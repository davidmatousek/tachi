# T001 — Pre-State Evidence (Feature 185, Wave 0 Lane B)

**Date**: 2026-06-11 · **Branch**: `185-cwe-catalog-expansion` · **Executor**: senior-backend-engineer (W0-b)

Recorded BEFORE any production-data edit. Nothing was fixed, no baselines touched, no tests edited.

---

## 1. Recovery object verification

```
$ git cat-file -t e58f247
commit

$ git cat-file -t 991e1ee
commit
```

Both recovery objects resolve and are `commit` objects, as required.

## 2. Blob edge counts (YAML parse — NOT grep)

Counted by parsing the top-level YAML list (`crosswalk.yaml` is a flat list of edge mappings; there is no `edges:` top-level key). Per the architect erratum, `grep -c "edge_type:"` is forbidden here — it over-counts +1 by matching the commented header line `# Edge shape: {source: ..., edge_type, confidence, citation}`.

```
$ git show e58f247:schemas/taxonomy/crosswalk.yaml | /usr/bin/python3 -c "import sys,yaml; print(len(yaml.safe_load(sys.stdin)))"
551

$ git show 991e1ee:schemas/taxonomy/crosswalk.yaml | /usr/bin/python3 -c "import sys,yaml; print(len(yaml.safe_load(sys.stdin)))"
438
```

| Blob | Role | Edge count | Expected | Match |
|---|---|---|---|---|
| `e58f247` | source (pre-T029) | 551 | 551 | YES |
| `991e1ee` | control (post-T029) | 438 | 438 | YES |

Count delta = 113 (the full T029 removal set).

## 3. Integrity suite — GREEN pre-state

```
$ /usr/bin/python3 -m pytest tests/schemas/test_taxonomy_integrity.py -q
.....                                                                    [100%]
5 passed in 1.00s
```

(A `urllib3 NotOpenSSLWarning` banner line precedes the dots; environmental, not test output.)

5/5 green in ~1s, matching the contract pre-state (53 records / 578 edges, 541 primary).

## 4. Backward-compatibility suite — EXPECTED RED pre-state

Known pre-state on main: latent #186 mitre-atlas 30→36 drift — the 6 committed PDF baselines embed 30-row ATLAS Coverage Attestation tables, while regeneration against the live `schemas/taxonomy/mitre-atlas.yaml` (36 records) produces 36-row tables. This suite regenerates all 6 example PDFs internally.

```
$ /usr/bin/python3 -m pytest tests/scripts/test_backward_compatibility.py -q
```

Literal pytest totals line:

```
6 failed, 7 passed, 1 skipped in 21.32s
```

Literal short test summary:

```
SKIPPED [1] tests/scripts/test_backward_compatibility.py:392: mermaid-agentic-app is excluded from SC-003 per T033 narrowed interpretation (multi-agent gate predicate evaluates TRUE via condition (a)+(b); pattern classification is a documented known-limitation pending R-04/R-06 rule-tuning follow-up).
FAILED tests/scripts/test_backward_compatibility.py::test_unmodified_examples_byte_identical_pdfs[web-app]
FAILED tests/scripts/test_backward_compatibility.py::test_unmodified_examples_byte_identical_pdfs[microservices]
FAILED tests/scripts/test_backward_compatibility.py::test_unmodified_examples_byte_identical_pdfs[ascii-web-api]
FAILED tests/scripts/test_backward_compatibility.py::test_unmodified_examples_byte_identical_pdfs[mermaid-agentic-app]
FAILED tests/scripts/test_backward_compatibility.py::test_unmodified_examples_byte_identical_pdfs[free-text-microservice]
FAILED tests/scripts/test_backward_compatibility.py::test_unmodified_examples_byte_identical_pdfs[maestro-reference]
6 failed, 7 passed, 1 skipped in 21.32s
```

**Attribution (per plan review)**: all 6 parametrized failures are `test_unmodified_examples_byte_identical_pdfs[*]` byte-mismatches attributable to the ATLAS Coverage Attestation section of the regenerated PDFs (mitre-atlas 30→36 row growth vs the committed baselines). Representative failure detail (`maestro-reference`): baseline 7,032,004 bytes vs generated 7,032,279 bytes, first divergence at byte offset 41018 inside a PDF page-tree object (`... 1831 0 R]` vs `... 1831 0 R 1831 0 R 1831 0 R ...` — object-reference growth consistent with CA table rows added), NOT inside the Info dictionary or XMP stream — `SOURCE_DATE_EPOCH=1700000000` determinism pin is honored; this is content drift, not a determinism regression.

**Nothing was fixed.** This red pre-state is the T015 (US3) red→green reference point; baselines regenerate there, not here.

---

## 5. T005 verification — restore-set artifact (appended at W0-b gate G0a)

Extraction run (literal script output, counts via YAML parse):

```
$ /usr/bin/python3 specs/185-cwe-catalog-expansion/scripts/extract_restore_set.py
wrote specs/185-cwe-catalog-expansion/restored-edges.yaml
total edges: 67
source-taxonomy split: owasp->cwe = 65, mitre-attack->cwe = 2
confidence: high = 34, medium = 32, low = 1
edge_type: primary = 67 (all primary)
distinct _blocked_on IDs: 40
low edge preserved as-is: T1070.006 -> CWE-1269 (confidence: low)
mitre-attack pair: T1070.006 -> CWE-1269, T1562 -> CWE-693
exclusions absent: 0 artifact targets in frozen-53; 0 non-cwe targets; 0 artifact edges present in control blob 991e1ee
frozen-53 check: live schemas/taxonomy/cwe.yaml has exactly 53 records
contract verification: PASS
```

Independent verification (separate YAML re-parse of the emitted artifact from disk, not the script's own asserts) — literal output:

```
INDEPENDENT ARTIFACT VERIFICATION (parse from disk)
total: 67
source split: {'owasp': 65, 'mitre-attack': 2}
confidence: {'high': 34, 'medium': 32, 'low': 1}
edge_type: {'primary': 67}
distinct _blocked_on: 40
all _blocked_on == target.id: True
all targets cwe: True
keys per edge: ['_blocked_on', 'citation', 'confidence', 'edge_type', 'source', 'target']
targets in frozen-53: 0
stripped edges still in control blob: 0
artifact field lines not byte-present in source blob: 0
low edge: [('T1070.006', 'CWE-1269', 'low')]
mitre pair: [('T1070.006', 'CWE-1269'), ('T1562', 'CWE-693')]
```

Byte-fidelity: every non-annotation field line of the artifact is byte-present verbatim in the `e58f247` blob (raw-block extraction, no YAML re-serialization) — 0 deviating lines.

| Check | Expected | Actual | Match |
|---|---|---|---|
| Total edges | 67 | 67 | YES |
| owasp → cwe | 65 | 65 | YES |
| mitre-attack → cwe | 2 | 2 | YES |
| Distinct `_blocked_on` IDs | 40 | 40 | YES |
| Confidence high/medium/low | 34/32/1 | 34/32/1 | YES |
| All `edge_type: primary` | yes | yes | YES |
| Exclusions absent (drift / non-CWE / dedupe) | absent | absent | YES |

**Exclusion accounting** (removed-set decomposition, set semantics on full edge content): 113 count-delta = 99 content-removed + 14 identical-copy dedupe extras; 99 content-removed = 67 CWE-blocked (the artifact) + 1 other-drift cwe-target (`T1190 → CWE-20`, target exists in frozen-53) + 20 non-CWE-target removals + 11 near-dup dedupe collapses (exact edge tuple survives in 991e1ee with changed content). Dedupe total = 14 + 11 = 25. Artifact ∪ {1 drift, 20 non-CWE, 25 dedupe} = full T029 removal set, per data-model.md §3 invariant.

**Gate G0a: PASS** — artifact committed before any production-data edit (Risk 185.1 closed).
