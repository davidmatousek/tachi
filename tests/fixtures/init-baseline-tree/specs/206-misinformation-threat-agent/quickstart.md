# Quickstart: Verifying F-2 `misinformation` Agent

**Feature**: 206
**Status**: Phase 1 design artifact
**Purpose**: Step-by-step verification walkthrough for post-implementation validation

## Pre-Requisites

- F-2 implementation complete through Wave 4 (example regeneration)
- Working directory at repo root: `/Users/david/Projects/tachi`
- Python environment with `pyyaml` and `pytest` available (already declared)
- `SOURCE_DATE_EPOCH=1700000000` honored by PDF regeneration pipeline (per ADR-021)

## Verification Steps

### Step 1: Structural Validation (FR-010, SC-001, SC-011)

```bash
# Agent line count ≤150 (AI tier cap per ADR-023)
wc -l .claude/agents/tachi/misinformation.md
# Expected: line count ≤150 (hard ceiling 180)

# Exactly one MANDATORY: Read directive under ## Detection Workflow
grep -c '\*\*MANDATORY\*\*: Read' .claude/agents/tachi/misinformation.md
# Expected: 1

# Zero MAESTRO references across agent + companion
grep -i 'maestro' .claude/agents/tachi/misinformation.md .claude/skills/tachi-misinformation/references/detection-patterns.md
# Expected: no matches
```

### Step 2: Pattern Catalog Validation (FR-003, SC-002)

```bash
# Count pattern categories (H3 headings under ## Detection Patterns)
awk '/^## Detection Patterns$/,/^## /' .claude/skills/tachi-misinformation/references/detection-patterns.md | grep -c '^### '
# Expected: ≥5

# Each category should cite OWASP LLM09:2025 as primary
grep -c 'OWASP LLM09:2025' .claude/skills/tachi-misinformation/references/detection-patterns.md
# Expected: ≥5 (at least one per pattern category)

# Each category should enumerate at least one anti-indicator (MEDIUM-5)
grep -c '^\*\*Anti-Indicator' .claude/skills/tachi-misinformation/references/detection-patterns.md
# Expected: ≥5
```

### Step 3: Schema Validation (FR-004, SC-012)

```bash
# Verify schema_version bumped to 1.7
grep 'schema_version:' schemas/finding.yaml
# Expected: schema_version: "1.7"

# Verify id.pattern includes MI prefix
grep 'pattern:' schemas/finding.yaml
# Expected: pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI)-\\d+$"

# Run regex unit test
pytest tests/scripts/test_misinformation.py::test_regex_matches_mi_prefix -v
# Expected: PASSED
```

### Step 4: Source Attribution Validation (FR-007, SC-010)

```bash
# Run source_attribution referential-integrity test on fixtures
pytest tests/scripts/test_misinformation.py -v
# Expected: all fixture tests PASSED

# Verify positive fixture
python -c "from scripts.tachi_parsers import validate_source_attribution; validate_source_attribution('tests/scripts/fixtures/misinformation/valid_mi_finding.yaml')"
# Expected: no errors

# Verify negative fixture (contains AML.T0042 — absent from catalog)
python -c "from scripts.tachi_parsers import validate_source_attribution; validate_source_attribution('tests/scripts/fixtures/misinformation/invalid_attribution_finding.yaml')"
# Expected: ValidationError citing AML.T0042 absent from catalog
```

### Step 5: Shared Reference Edit Validation (FR-005, SC-003)

```bash
# Verify misinformation in consumers list post-edit
grep 'misinformation' .claude/skills/tachi-shared/references/finding-format-shared.md
# Expected: presence in frontmatter consumers: list

# Verify ## headings byte-identical pre/post edit
# Capture pre-edit commit heading list (requires git)
git show HEAD~1:.claude/skills/tachi-shared/references/finding-format-shared.md | grep '^## ' > /tmp/finding-format-pre.txt
grep '^## ' .claude/skills/tachi-shared/references/finding-format-shared.md > /tmp/finding-format-post.txt
diff /tmp/finding-format-pre.txt /tmp/finding-format-post.txt
# Expected: empty diff
```

### Step 6: Orchestrator Dispatch Validation (FR-004, F-1 carry-over reconciliation)

```bash
# Verify misinformation in orchestrator.md dispatch list
grep 'misinformation' .claude/agents/tachi/orchestrator.md
# Expected: presence in AI-tier dispatch block + line 296 sequential-mode + line 370 LLM Threats row

# Verify quintet reconciliation consistency (5 callsites per FR-7)
grep -c 'output-integrity' .claude/agents/tachi/orchestrator.md .claude/skills/tachi-orchestration/references/dispatch-rules.md
# Expected: co-occurrence with misinformation at each of the 5 callsites
# (Lines: orchestrator.md:296, orchestrator.md:370, dispatch-rules.md quartet-line, dispatch-rules.md:120, trigger-keyword rules section)

# Verify dispatch-rules.md quintet
grep -A2 'LLM dispatch' .claude/skills/tachi-orchestration/references/dispatch-rules.md | head -10
# Expected: list includes prompt-injection, data-poisoning, model-theft, output-integrity, misinformation
```

### Step 7: 24-File Zero-Edit Invariant (FR-013, SC-009)

```bash
# Enumerate the 24 detection-tier files that MUST be unchanged
INVARIANT_FILES=(
  .claude/agents/tachi/spoofing.md
  .claude/agents/tachi/tampering.md
  .claude/agents/tachi/repudiation.md
  .claude/agents/tachi/info-disclosure.md
  .claude/agents/tachi/denial-of-service.md
  .claude/agents/tachi/privilege-escalation.md
  .claude/agents/tachi/prompt-injection.md
  .claude/agents/tachi/data-poisoning.md
  .claude/agents/tachi/model-theft.md
  .claude/agents/tachi/tool-abuse.md
  .claude/agents/tachi/agent-autonomy.md
  .claude/agents/tachi/output-integrity.md
  .claude/skills/tachi-spoofing/references/detection-patterns.md
  .claude/skills/tachi-tampering/references/detection-patterns.md
  .claude/skills/tachi-repudiation/references/detection-patterns.md
  .claude/skills/tachi-info-disclosure/references/detection-patterns.md
  .claude/skills/tachi-denial-of-service/references/detection-patterns.md
  .claude/skills/tachi-privilege-escalation/references/detection-patterns.md
  .claude/skills/tachi-prompt-injection/references/detection-patterns.md
  .claude/skills/tachi-data-poisoning/references/detection-patterns.md
  .claude/skills/tachi-model-theft/references/detection-patterns.md
  .claude/skills/tachi-tool-abuse/references/detection-patterns.md
  .claude/skills/tachi-agent-autonomy/references/detection-patterns.md
  .claude/skills/tachi-output-integrity/references/detection-patterns.md
)

# Check each file is unchanged vs pre-F-2 HEAD
for f in "${INVARIANT_FILES[@]}"; do
  if ! git diff --quiet HEAD~N -- "$f"; then  # N = number of F-2 commits
    echo "VIOLATION: $f modified"
  fi
done
# Expected: no VIOLATION messages
```

### Step 8: Backward Compatibility (FR-003, SC-006)

```bash
# Run backward-compatibility byte-identity test on 5 non-factual-output baselines
SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py -v
# Expected: all 5 baselines (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice) PASSED
```

### Step 9: Regenerated Example Validation (FR-009, SC-004, SC-007, SC-014)

```bash
# Assuming agentic-app was extended with a factual-output sub-component and regenerated in Wave 4

# Count MI-{N} findings in regenerated threats.md
grep -c 'id: MI-' examples/agentic-app/threats.md
# Expected: ≥1

# Verify LLM09 primary citation on every MI-{N} finding
python -c "
import yaml
with open('examples/agentic-app/threats.md') as f:
    content = f.read()
import re
mi_findings = re.findall(r'(id: MI-\d+.*?(?=id: |$))', content, re.DOTALL)
for finding in mi_findings:
    assert 'LLM09' in finding, f'LLM09 missing in: {finding[:200]}'
print(f'{len(mi_findings)} MI findings validated for LLM09 primary')
"
# Expected: all MI findings carry LLM09 primary

# Verify three-signal-class discipline (LLM-{N}, OI-{N}, MI-{N} findings adjacent without synthesis)
grep -E 'id: (LLM|OI|MI)-' examples/agentic-app/threats.md | head -10
# Expected: all three ID prefix families present

# Verify source_attribution populated on MI-{N} findings
grep -B1 -A5 'id: MI-' examples/agentic-app/threats.md | grep -A4 'source_attribution:'
# Expected: source_attribution array with OWASP LLM09 primary + CWE-345 and/or CWE-223 related
```

### Step 10: Zero New Dependencies (FR-015, SC-008)

```bash
# Verify no new runtime dependencies
git diff HEAD~N -- pyproject.toml requirements*.txt package.json
# Expected: empty diff (N = number of F-2 commits)
```

### Step 11: ADR-031 Validation (FR-008, SC-005)

```bash
# Verify ADR-031 exists
ls docs/architecture/02_ADRs/ADR-031-misinformation-agent.md
# Expected: file exists

# Verify Heuristic A three-way scope resolution in body
grep -c 'distinct from' docs/architecture/02_ADRs/ADR-031-misinformation-agent.md
# Expected: ≥2 ("distinct from prompt-injection" + "distinct from output-integrity")

# Verify ADR-030 Decision 1 cross-reference (PRD MEDIUM-1)
grep 'ADR-030.*Decision 1' docs/architecture/02_ADRs/ADR-031-misinformation-agent.md
# Expected: at least one match

# Verify ADR-030 Decision 8 cross-reference (regex-alternation minor-bump rule, 2nd recorded application)
grep 'Decision 8' docs/architecture/02_ADRs/ADR-031-misinformation-agent.md
# Expected: at least one match

# Verify CWE-1039 deliberate-exclusion note (MEDIUM-3)
grep 'CWE-1039' docs/architecture/02_ADRs/ADR-031-misinformation-agent.md
# Expected: at least one match (exclusion rationale present)

# Verify zero commercial framing
grep -iE '(tachi cloud|layer 2|enterprise only|commercial)' docs/architecture/02_ADRs/ADR-031-misinformation-agent.md
# Expected: no matches

# Verify Status transition Proposed → Accepted
grep 'Status:' docs/architecture/02_ADRs/ADR-031-misinformation-agent.md | head -2
# Expected: Status: Accepted (after transition at Wave 5)
```

### Step 12: BLP-01 Coverage Matrix Update (SC-013)

```bash
# Verify LLM09:2025 transitioned Planned → Covered
grep -A2 'LLM09' _internal/strategy/BLP-01-threat-coverage.md
# Expected: status: Covered (or equivalent) with F-2 (Feature 206) named as closure feature
```

## Acceptance

All 12 verification steps MUST pass for F-2 to be considered Delivered. Verification can be automated as part of the `/aod.deliver` workflow or run manually at PR pre-merge.

## References

- **Spec**: [spec.md](./spec.md) — SC-001 through SC-014 mapped to verification steps
- **Plan**: [plan.md](./plan.md) — Wave structure providing implementation context
- **Finding Contract**: [contracts/finding-contract.md](./contracts/finding-contract.md) — finding shape invariants verified in Step 4
- **Data Model**: [data-model.md](./data-model.md) — entity definitions underlying the verification predicates
