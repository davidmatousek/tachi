# Quickstart: Verifying F-1 `output-integrity` Delivery

**Feature**: 201 — output-integrity-threat-agent
**Purpose**: Step-by-step verification walkthrough for reviewers and the implementation team.

## Prerequisites

- On branch `201-output-integrity-threat-agent`
- Wave 1.1 schema bump + ADR-030 Proposed commit present
- Wave 2-4 implementation waves complete
- Wave 4 example regeneration complete

## Step 1: Structural Validation (Wave 2 outputs)

```bash
# Line count ≤ 150 (AI tier cap per ADR-023)
wc -l .claude/agents/tachi/output-integrity.md
# Expect: N ≤ 150 (hard ceiling 180)

# Exactly one MANDATORY Read directive
grep -c '\*\*MANDATORY\*\*: Read' .claude/agents/tachi/output-integrity.md
# Expect: 1

# Zero MAESTRO references in agent + companion
grep -i maestro .claude/agents/tachi/output-integrity.md .claude/skills/tachi-output-integrity/references/detection-patterns.md
# Expect: (no output)

# Pattern category count ≥ 5
grep -c '^### Pattern Category' .claude/skills/tachi-output-integrity/references/detection-patterns.md
# Expect: N ≥ 5 (6 if Heuristic A Outcome A was chosen; Outcome B per current plan → 5)
```

## Step 2: Schema Validation (Wave 1.1 output)

```bash
# schema_version bumped to 1.6
grep -E 'schema_version:.*1\.6' schemas/finding.yaml
# Expect: schema_version: "1.6"

# id.pattern includes OI prefix
grep -E 'id\.pattern.*OI' schemas/finding.yaml || grep -A2 '^id:' schemas/finding.yaml | grep -E 'OI'
# Expect: line containing "(S|T|R|I|D|E|AG|LLM|AGP|OI)-\\d+"

# Regex unit test
pytest tests/scripts/test_output_integrity.py::test_regex_matches_oi_prefix -v
# Expect: 1 passed
```

## Step 3: Shared Reference Additive-Edit Validation (Wave 3 output)

```bash
# consumers list includes output-integrity between tool-abuse and risk-scorer
grep -A20 '^consumers:' .claude/skills/tachi-shared/references/finding-format-shared.md | head -20
# Expect: tool-abuse line immediately followed by output-integrity line, followed by risk-scorer

# Structural diff: ## headings byte-identical pre/post edit
git diff main -- .claude/skills/tachi-shared/references/finding-format-shared.md | grep -E '^[+-]## '
# Expect: (no output — no ## heading changes)
```

## Step 4: Orchestrator Registration Validation (Wave 3 output)

```bash
# orchestrator.md lists output-integrity.md in AI-tier dispatch
grep 'output-integrity.md' .claude/agents/tachi/orchestrator.md
# Expect: line with - output-integrity.md

# dispatch-rules.md has LLM quartet
grep -A10 'LLM dispatch' .claude/skills/tachi-orchestration/references/dispatch-rules.md | grep -E '(prompt-injection|data-poisoning|model-theft|output-integrity)'
# Expect: 4 lines (trio → quartet)
```

## Step 5: 22-File Zero-Edit Invariant Check (pre-merge)

```bash
# 11 detection-tier agent files unchanged
git diff main --stat -- \
  .claude/agents/tachi/spoofing.md \
  .claude/agents/tachi/tampering.md \
  .claude/agents/tachi/repudiation.md \
  .claude/agents/tachi/info-disclosure.md \
  .claude/agents/tachi/denial-of-service.md \
  .claude/agents/tachi/privilege-escalation.md \
  .claude/agents/tachi/prompt-injection.md \
  .claude/agents/tachi/data-poisoning.md \
  .claude/agents/tachi/model-theft.md \
  .claude/agents/tachi/tool-abuse.md \
  .claude/agents/tachi/agent-autonomy.md
# Expect: (no output — zero diff on all 11)

# 11 companion detection-patterns.md files unchanged
git diff main --stat -- '.claude/skills/tachi-*/references/detection-patterns.md' \
  | grep -v 'tachi-output-integrity'
# Expect: (no output — zero diff on all 11 pre-existing)

# Infrastructure-tier consumers unchanged
git diff main --stat -- \
  .claude/agents/tachi/risk-scorer.md \
  .claude/agents/tachi/control-analyzer.md \
  .claude/agents/tachi/threat-report.md \
  .claude/agents/tachi/threat-infographic.md \
  .claude/agents/tachi/report-assembler.md
# Expect: (no output)
```

## Step 6: Example Regeneration Validation (Wave 4 output)

```bash
# agentic-app has fresh OI-{N} findings
grep -E '^\| OI-[0-9]+' examples/agentic-app/threats.md | head -5
# Expect: ≥1 line matching | OI-N | ...

# Every OI-{N} finding has source_attribution with OWASP LLM05 primary
python -c "
import yaml, sys
from pathlib import Path
sys.path.insert(0, 'scripts')
from tachi_parsers import parse_threats_findings
findings = parse_threats_findings(Path('examples/agentic-app/threats.md').read_text())
oi_findings = [f for f in findings if f['id'].startswith('OI-')]
assert len(oi_findings) >= 1, 'Expected ≥1 OI finding'
for f in oi_findings:
    sa = f.get('source_attribution', [])
    assert any(
        entry.get('taxonomy') == 'owasp' and entry.get('id') == 'LLM05' and entry.get('relationship') == 'primary'
        for entry in sa
    ), f'Finding {f[\"id\"]} missing OWASP LLM05 primary attribution'
print(f'✓ {len(oi_findings)} OI findings all carry OWASP LLM05 primary attribution')
"
# Expect: ✓ N OI findings all carry OWASP LLM05 primary attribution

# F-A2 referential validation passes
pytest tests/scripts/test_output_integrity.py -v
# Expect: all tests passed

# F-B coverage-attestation fires on regenerated PDF
# (no direct CLI — checked by inspecting security-report.pdf TOC)
ls -la examples/agentic-app/security-report.pdf examples/agentic-app/security-report.pdf.baseline
# Expect: both files present, regenerated timestamps
```

## Step 7: Backward Compatibility Validation (Wave 4 output)

```bash
# 5 non-agentic baselines byte-identical under SOURCE_DATE_EPOCH
SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py -v
# Expect: 5/5 passed (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice)

# If mermaid-agentic-app fails: escalate per TL-H1 re-baseline decision
# (architect + team-lead approval required before re-baselining)
```

## Step 8: ADR-030 Validation (Wave 5 output)

```bash
# ADR-030 exists with Accepted status
head -15 docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md
# Expect: Status: Accepted

# Revision History table present
grep -A5 '## Revision History' docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md
# Expect: markdown table with Proposed + Accepted entries

# Cross-references present
grep -E 'ADR-02[1-9]' docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md
# Expect: ADR-021, ADR-023, ADR-026, ADR-027, ADR-028, ADR-029 all referenced
```

## Step 9: Dependency Invariant Check

```bash
git diff main --stat -- pyproject.toml 'requirements*.txt' package.json
# Expect: (no output — zero diff on all dependency manifests)
```

## Step 10: End-to-End Smoke (PR Pre-Merge)

```bash
# Full pytest suite
pytest tests/ -v
# Expect: all passed

# Full pipeline run on agentic-app (repeats Wave 4 for sanity)
SOURCE_DATE_EPOCH=1700000000 <pipeline invocation>
# Expect: fresh artifacts + ≥1 OI-{N} finding + valid source_attribution

# Summary: all 12 spec SCs green
# SC-001 (Step 1), SC-002 (Step 1), SC-003 (Step 3), SC-004 (Step 6), SC-005 (Step 8),
# SC-006 (Step 7), SC-007 (Step 6), SC-008 (Step 9), SC-009 (Step 5), SC-010 (Step 6),
# SC-011 (Step 1), SC-012 (Step 2)
```

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `grep -i maestro` returns matches | MAESTRO reference leaked into agent/companion | Remove MAESTRO mentions — orchestrator owns layer classification per ADR-023 Decision 2 |
| Line count > 150 | Agent file bloat | Trim `## Purpose` or `## Example Findings` until ≤150; move verbose content to `detection-patterns.md` |
| `validate_source_attribution` fails on CWE-73 or CWE-1336 | Pattern worked example cites absent CWE | Substitute CWE-22 (path traversal) or CWE-94 (template injection) per FR-007 |
| Byte-identity breaks on `mermaid-agentic-app` | Baseline example matches output-integrity triggers | Plan stage must flag; architect + team-lead decide re-baseline or scope carve-out |
| Dual-commit ADR lineage missing Accepted transition | Wave 5 not yet run | Transition Proposed → Accepted at PR merge; post-merge SHA fill recording squash commit |
