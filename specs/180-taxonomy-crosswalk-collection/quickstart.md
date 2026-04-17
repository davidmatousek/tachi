# Quickstart: F-A1 Taxonomy Crosswalk Collection

**Feature**: 180-taxonomy-crosswalk-collection
**Phase**: 1 — Design & Contracts
**Audiences**: adopter, maintainer, reviewer (maps 1:1 to spec.md primary personas)

This quickstart demonstrates the **independent test** for each user story in spec.md. Each section delivers complete value to one persona without the other personas' workflows being active.

---

## 1. Adopter quickstart (validates US-180-1 independent test)

**Goal**: Resolve a tachi-cited taxonomy ID (e.g., OWASP LLM05) to a canonical record with display name, source URL, and cross-framework references — programmatically, in ≤1 statement per lookup.

**Setup**: Fresh Python 3.11 virtual environment with only `pyyaml` installed.
```bash
python3.11 -m venv /tmp/taxonomy-quickstart
source /tmp/taxonomy-quickstart/bin/activate
pip install pyyaml
```

**Invocation**:
```python
import yaml

# Resolve an OWASP LLM Top 10 item
records = yaml.safe_load(open('schemas/taxonomy/owasp.yaml'))
llm05 = next(r for r in records if r['id'] == 'LLM05')
print(llm05['full_id'])    # OWASP-LLM-2025-05
print(llm05['name'])       # Improper Output Handling
print(llm05['url'])        # https://genai.owasp.org/llmrisk/llm05-improper-output-handling/
print(llm05['cwe_refs'])   # [CWE-79, CWE-89, CWE-116]

# Resolve a MITRE ATLAS technique
records = yaml.safe_load(open('schemas/taxonomy/mitre-atlas.yaml'))
agent_tech = next(r for r in records if r['id'] == 'AML.T0058')
print(agent_tech['name'])  # Publish Poisoned AI Agent Tool
```

**Expected outcome**: Both resolutions succeed in a fresh environment without any tachi-specific dependencies beyond `pyyaml`. Delivers complete US-180-1 value.

---

## 2. Maintainer quickstart (validates US-180-2 independent test)

**Goal**: Given a tachi concept (e.g., OWASP LLM05 "Improper Output Handling"), find all cross-framework edges in one canonical crosswalk file.

**Invocation**:
```python
import yaml

crosswalk = yaml.safe_load(open('schemas/taxonomy/crosswalk.yaml'))

# Find all edges sourced from OWASP LLM05
llm05_edges = [
    e for e in crosswalk
    if e['source']['taxonomy'] == 'owasp' and e['source']['id'] == 'LLM05'
]
for e in llm05_edges:
    print(f"  → {e['target']['taxonomy']}:{e['target']['id']} ({e['edge_type']}, {e['confidence']})")
    print(f"    citation: {e['citation']}")
```

**Expected outcome** (illustrative — actual output depends on crosswalk authoring):
```
  → cwe:CWE-79 (primary, high)
    citation: https://genai.owasp.org/llmrisk/llm05-improper-output-handling/
  → cwe:CWE-89 (primary, high)
    citation: https://genai.owasp.org/llmrisk/llm05-improper-output-handling/
  → mitre-attack:T1189 (related, medium)
    citation: https://attack.mitre.org/techniques/T1189/
```

Delivers complete US-180-2 value — single-file lookup replaces multi-file grep across agent detection-patterns.md references.

---

## 3. Reviewer quickstart (validates US-180-3 independent test)

**Goal**: Audit the curation methodology, provenance, confidence calibration, and update procedure for one framework (e.g., CWE).

**Invocation** (no code needed):
```bash
# Open the README
less schemas/taxonomy/README.md

# Navigate to sections:
# §Purpose                — why the directory exists + adopter runnable snippet
# §What F-A1 does NOT     — explicit "not yet in F-A1" scope signal (per PM H-PM-2)
# §Harvest methodology    — how items were gathered
# §Per-framework provenance → CWE section
#   • seed source: 41 CWEs from 11 detection-patterns.md files
#   • external curation: CWE Top 25 (2025) — published 2025-12-11
#   • what was added: 12 net-new CWEs (CWE-79, CWE-94, …)
# §Confidence calibration rubric → three-level rubric + anti-drift rule
# §Canonical-URL conventions → CWE uses https://cwe.mitre.org/data/definitions/<N>.html
# §Update procedure → CWE section → "When CWE Top 25 (2026) publishes …"
# §Crosswalk methodology → how edges were authored + confidence calibration
```

**Expected outcome**: Reviewer can trace every record in `cwe.yaml` to either (a) the agent citation seed or (b) the CWE Top 25 (2025) external source. Reviewer can file a PR to add CWE-XXX with a clear update-procedure precedent. Delivers complete US-180-3 value.

---

## 4. Integrity-test quickstart (validates US-180-4 independent test)

**Goal**: Confirm the authored YAMLs are internally consistent before merging.

**Setup**: fresh clone with `pip install -r requirements-dev.txt`.

**Invocation**:
```bash
pytest tests/schemas/test_taxonomy_integrity.py -v
```

**Expected outcome**:
```
tests/schemas/test_taxonomy_integrity.py::test_framework_yamls_load PASSED
tests/schemas/test_taxonomy_integrity.py::test_crosswalk_loads PASSED
tests/schemas/test_taxonomy_integrity.py::test_crosswalk_referential_integrity PASSED
tests/schemas/test_taxonomy_integrity.py::test_citation_shape PASSED
tests/schemas/test_taxonomy_integrity.py::test_records_sorted PASSED  # optional
===== 5 passed in 0.XXs =====
```

All 4+1 tests pass. Delivers complete US-180-4 value.

---

## 5. ADR review quickstart (validates US-180-5 independent test)

**Goal**: Understand the rationale behind the schema decisions.

**Invocation** (no code needed):
```bash
less docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md
```

**Expected content**:
- **Status**: Accepted (at PR merge; Proposed at end of Day 1)
- **Decision**: introduce `schemas/taxonomy/` with FR-003 / FR-009 shapes
- **Rationale**: Interpretation C (9-file structure) rationale; scope/cadence exception rationale; anti-drift rule rationale
- **Related ADRs**: ADR-020, ADR-021, ADR-023, ADR-024, ADR-025

Delivers complete US-180-5 value.

---

## 6. Backward-compatibility verification

**Goal**: Confirm the ADR-021 byte-identity invariant is preserved (PRD Metric 4).

**Invocation**:
```bash
SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py -v
```

**Expected outcome**: 5/5 or 6/6 non-agentic example PDFs regenerate byte-identically. PRD FR-9 invariant preserved automatically because F-A1 touches zero runtime scripts.
