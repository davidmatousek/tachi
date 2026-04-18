# Quickstart — F-A2 Source Attribution Schema Extension

**Audience**: F-A3 developers, F-B coverage-attestation authors, ecosystem integrators building adapters to tachi findings.

**Purpose**: Show in ~10 minutes how to read `source_attribution` from a tachi threat finding and validate that its citations resolve against F-A1 catalog YAMLs.

---

## Prerequisites

- Python 3.11+
- `pip install pyyaml pytest` (developer-only; already in `requirements-dev.txt`)
- A tachi working tree at HEAD after F-A2 merge (schema 1.5)

---

## Step 1 — Inspect the Schema Shape

```bash
head -20 schemas/finding.yaml
# => schema_version: "1.5"

grep -A 20 "source_attribution:" schemas/finding.yaml
# Shows the new field's type, enum constraints, and default-handling contract.
```

The field is **optional** and **absent by default** on findings that cite no framework items. This is a conditional-key semantic — absent is distinct from `source_attribution: []`.

---

## Step 2 — Read a Finding With Attribution

Given a `threats.md` file carrying `source_attribution` on one or more findings via the Q1-resolved serialization surface:

```python
from scripts.tachi_parsers import parse_threats_findings

with open("path/to/threats.md") as f:
    findings = parse_threats_findings(f.read())

for finding in findings:
    if "source_attribution" in finding:
        print(f"{finding['id']}: cites {len(finding['source_attribution'])} framework items")
        for record in finding['source_attribution']:
            print(f"  - {record['taxonomy']}/{record['id']} ({record['relationship']})")
```

**Key behaviors**:
- Findings without attribution will NOT have the `source_attribution` key — check with `if "source_attribution" in finding`, NOT `if finding.get("source_attribution")`.
- Every emitted record has all three keys `{taxonomy, id, relationship}` populated. Missing `relationship` on input is injected as `"primary"` on emission.

---

## Step 3 — Validate Referential Integrity

```python
from pathlib import Path
from scripts.tachi_parsers import parse_threats_findings, validate_source_attribution

findings = parse_threats_findings(open("threats.md").read())

errors = validate_source_attribution(findings, taxonomy_dir=Path("schemas/taxonomy"))

if errors:
    for err in errors:
        print(f"Validation failure in {err.finding_id}: {err.reason} (target: {err.target_yaml_path})")
else:
    print(f"All {sum(len(f.get('source_attribution', [])) for f in findings)} attribution records resolve.")
```

**When to call validation**:
- In tachi's pipeline: orchestrator Phase 4 (per Q2-B architect preference).
- In your ecosystem adapter: after parsing findings and before any aggregation. This catches drift between the finding corpus and the F-A1 catalog state.

---

## Step 4 — Aggregate By Framework (F-B Preview)

```python
from collections import defaultdict

by_framework = defaultdict(list)

for finding in findings:
    for record in finding.get("source_attribution", []):
        by_framework[record["taxonomy"]].append(finding["id"])

for taxonomy, finding_ids in by_framework.items():
    print(f"{taxonomy}: {len(finding_ids)} findings cite this framework")
```

This is the shape F-B's coverage attestation section will consume. F-B will go further by joining against `schemas/taxonomy/crosswalk.yaml` to surface cross-framework coverage claims (e.g., "X findings cite OWASP LLM05, which maps via crosswalk to CWE-79, CWE-89, CWE-116 — per-CWE coverage implied").

---

## Step 5 — Author a Populator (F-A3 Teaser)

F-A2 ships the contract only. Populators are F-A3 scope. If you are authoring an F-A3 populator:

```python
# Inside a threat-detection agent's finding construction (F-A3 only):

finding = {
    "id": "LLM-5",
    "category": "llm",
    # ... all existing schema 1.4 fields ...
}

# Only add source_attribution when the finding genuinely cites framework items.
# Leave the key absent when no framework item applies.
attribution = _determine_framework_citations(detection_context)  # F-A3-specific logic
if attribution:  # Non-empty list
    finding["source_attribution"] = attribution
```

**F-A3 responsibilities (NOT F-A2)**:
- Decide which framework items each detection pattern cites.
- Wire populator logic into the 11 threat-detection agents + 11 skill references.
- Design SARIF, Typst, and `extract-report-data.py` propagation for the new field.

---

## Round-Trip Test Example

```python
# tests/scripts/test_source_attribution_example.py (illustrative)

def test_round_trip_multi_record(tmp_path):
    threats_md = tmp_path / "threats.md"
    threats_md.write_text("""
# Section 7 table omitted for brevity — populated with 1 finding LLM-5.

<!-- Q1-E surface: new Section 9 YAML block -->
## 9. Source Attribution

```yaml
LLM-5:
  - {taxonomy: owasp, id: LLM05, relationship: primary}
  - {taxonomy: cwe, id: CWE-116, relationship: primary}
  - {taxonomy: mitre-atlas, id: AML.T0051, relationship: primary}
```
""")

    findings = parse_threats_findings(threats_md.read_text())
    assert findings[0]["id"] == "LLM-5"
    assert "source_attribution" in findings[0]
    assert len(findings[0]["source_attribution"]) == 3
    assert findings[0]["source_attribution"][0] == {
        "taxonomy": "owasp", "id": "LLM05", "relationship": "primary"
    }
```

*(Q1-E example shown; if Q1-B (sidecar) is selected instead, the test loads a companion `threats-attribution.yaml` file.)*

---

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|--------------|------------|
| `KeyError: 'source_attribution'` on every finding | Using `finding['source_attribution']` instead of `.get()` or `in` | Use `if "source_attribution" in finding:` (conditional-key semantic) |
| `ValueError: invalid taxonomy 'OWASP'` | Using uppercase or non-hyphenated value | Lowercase-hyphenated: `owasp`, `mitre-attack`, `mitre-atlas`, `nist-ai-rmf`, `cwe` |
| `ValueError: invalid relationship 'primary_'` | Typo | Closed enum: `primary`, `related`, `derived` |
| `ValidationError: id 'X' not found in schemas/taxonomy/owasp.yaml` | Stale or invalid OWASP ID | Check `schemas/taxonomy/owasp.yaml` for the canonical id spelling |
| SC-2 byte-identity regression after F-A2 merge | Attribution surface leaked into a baseline example | Verify no example under `examples/` carries `source_attribution` data |

---

## References

- **Schema**: `schemas/finding.yaml` (v1.5)
- **Contract**: `specs/189-source-attribution-schema-extension/contracts/source-attribution-record.yaml`
- **Data model**: `specs/189-source-attribution-schema-extension/data-model.md`
- **ADR**: `docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md` (authored at Day 1 Wave 1)
- **F-A1 catalogs**: `schemas/taxonomy/{owasp,mitre-attack,mitre-atlas,nist-ai-rmf,cwe}.yaml`
