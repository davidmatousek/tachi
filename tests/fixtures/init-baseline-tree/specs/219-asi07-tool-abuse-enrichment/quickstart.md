# Quickstart: F-3 ASI07 Tool-Abuse Enrichment Verification

**Feature**: 219 / F-3 — Heuristic A enrichment of `tool-abuse` agent for OWASP ASI07:2026 coverage
**Plan**: [plan.md](./plan.md)
**Audience**: Senior backend engineer / code-reviewer running pre-merge verification at Wave 4

## Purpose

Step-by-step verification walkthrough confirming all F-3 acceptance criteria pass post-build. Run this end-to-end before marking PR #220 ready for review.

## Prerequisites

- Branch: `219-asi07-tool-abuse-enrichment` checked out
- All Wave 1-3 commits present (ADR-032 Proposed, `tool-abuse.md` edits, `detection-patterns.md` edits, `tests/scripts/test_tool_abuse_enrichment.py`, regenerated `examples/agentic-app/`)
- Python venv activated; `pyyaml` + `pytest` installed
- `gh` CLI authenticated for PR ops

## Verification Procedure

### Step 1 — Structural validation on `tool-abuse.md` (BLOCKER per SC-002, SC-016)

```bash
# Line count cap: ≤150 lines
wc -l .claude/agents/tachi/tool-abuse.md
# Expected: ≤150 (target 100-106 post-edit; PRD-time baseline 98)

# Single MANDATORY Read directive preserved
grep -c '\*\*MANDATORY\*\*: Read' .claude/agents/tachi/tool-abuse.md
# Expected: 1

# Zero MAESTRO references
grep -i 'maestro' .claude/agents/tachi/tool-abuse.md
# Expected: empty (zero matches)
```

**Pass criteria**: All three commands return expected values. **FAIL if any return wrong value.**

### Step 2 — Metadata extension on `tool-abuse.md` (SC-001, SC-004)

```bash
# ASI-07 added to owasp_references
grep '^owasp_references:' .claude/agents/tachi/tool-abuse.md
# Expected: owasp_references: [ASI-02, ASI-04, MCP-03, MCP-05, LLM06:2025, ASI-07]

# Detection Workflow Step 5 references list extended
grep -E '(ASI-07|AML.T0060|CWE-287|CWE-345)' .claude/agents/tachi/tool-abuse.md
# Expected: ≥4 lines containing these references in Step 5
```

**Pass criteria**: `ASI-07` present in metadata; all 4 new references present in Step 5.

### Step 3 — `## Purpose` extension byte-identity check (SC-003)

```bash
# Diff against PRD-time baseline (use git history if needed)
git show main:.claude/agents/tachi/tool-abuse.md | sed -n '/^## Purpose/,/^## /p' > /tmp/purpose_pre.md
sed -n '/^## Purpose/,/^## /p' .claude/agents/tachi/tool-abuse.md > /tmp/purpose_post.md

# The diff should show ONLY appended lines (1-3 lines naming A2A / MCP-to-MCP surface)
diff /tmp/purpose_pre.md /tmp/purpose_post.md
# Expected: Only ">" lines (append-only); no "<" lines (no removals or modifications)
```

**Pass criteria**: Diff shows only additions; pre-existing prose is byte-identical.

### Step 4 — Pattern Categories 9 + 10 + Disambiguation present (SC-005, SC-007)

```bash
# Both new categories present
grep -E '^## Pattern Category (9|10):' .claude/skills/tachi-tool-abuse/references/detection-patterns.md
# Expected:
#   ## Pattern Category 9: Insecure Inter-Agent Communication (A2A)
#   ## Pattern Category 10: MCP-to-MCP Trust Propagation

# Pattern Category Disambiguation subsection present
grep '^## Pattern Category Disambiguation' .claude/skills/tachi-tool-abuse/references/detection-patterns.md
# Expected: 1 match

# Primary Sources extended with new entries
grep -E '(OWASP ASI07:2026|MITRE ATLAS AML.T0060)' .claude/skills/tachi-tool-abuse/references/detection-patterns.md
# Expected: ≥2 lines (one per new entry)
```

**Pass criteria**: All four greps return expected matches.

### Step 5 — Categories 1-8 byte-identity validation (BLOCKER per SC-006)

```bash
# Extract Categories 1-8 + Overview + Targeted DFD Element Types + Trigger Keywords
git show main:.claude/skills/tachi-tool-abuse/references/detection-patterns.md \
  | sed -n '1,/^## Pattern Category 9/p' \
  | head -n -1 > /tmp/categories_1_8_pre.md

sed -n '1,/^## Pattern Category 9/p' .claude/skills/tachi-tool-abuse/references/detection-patterns.md \
  | head -n -1 > /tmp/categories_1_8_post.md

# Strict byte-identity check
diff /tmp/categories_1_8_pre.md /tmp/categories_1_8_post.md
# Expected: empty diff (zero output)
```

**Pass criteria**: Empty diff. **BLOCKER FAIL otherwise.**

### Step 6 — Zero MAESTRO grep on `detection-patterns.md` (SC-016)

```bash
grep -i 'maestro' .claude/skills/tachi-tool-abuse/references/detection-patterns.md
# Expected: empty
```

**Pass criteria**: Empty output.

### Step 7 — Schema invariant verification (BLOCKER per SC-014)

```bash
# schema_version unchanged
grep '^schema_version:' schemas/finding.yaml
# Expected: schema_version: "1.7"

# id.pattern regex unchanged
grep 'pattern:' schemas/finding.yaml
# Expected: pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI)-\\d+$"

# Empty diff against main
git diff main -- schemas/finding.yaml
# Expected: empty
```

**Pass criteria**: All three checks pass. **BLOCKER FAIL otherwise.**

### Step 8 — Zero-edit invariant verification (BLOCKER per SC-013, FR-014, FR-016, FR-017)

```bash
# 12 other threat-agent files unchanged
for agent in spoofing tampering repudiation info-disclosure denial-of-service privilege-escalation \
             prompt-injection data-poisoning model-theft agent-autonomy output-integrity misinformation; do
  if [ -n "$(git diff main -- .claude/agents/tachi/$agent.md)" ]; then
    echo "FAIL: $agent.md modified"; exit 1
  fi
done
echo "12 threat-agent files: OK"

# 12 other companion detection-patterns.md files unchanged
for skill in spoofing tampering repudiation info-disclosure denial-of-service privilege-escalation \
             prompt-injection data-poisoning model-theft agent-autonomy output-integrity misinformation; do
  if [ -n "$(git diff main -- .claude/skills/tachi-$skill/references/detection-patterns.md)" ]; then
    echo "FAIL: tachi-$skill/references/detection-patterns.md modified"; exit 1
  fi
done
echo "12 companion detection-patterns.md files: OK"

# Infrastructure-tier consumers unchanged
for consumer in risk-scorer control-analyzer threat-report threat-infographic report-assembler; do
  if [ -n "$(git diff main -- .claude/agents/tachi/$consumer.md)" ]; then
    echo "FAIL: $consumer.md modified"; exit 1
  fi
done
echo "5 infrastructure-tier consumers: OK"

# orchestrator.md and finding-format-shared.md unchanged
git diff main -- .claude/agents/tachi/orchestrator.md
# Expected: empty

git diff main -- .claude/skills/tachi-shared/references/finding-format-shared.md
# Expected: empty

# dispatch-rules.md zero functional diff (cosmetic Q2 annotation if applied is single-token)
git diff main -- .claude/skills/tachi-orchestration/references/dispatch-rules.md
# Expected: empty OR single-token annotation diff (`tool-abuse (MCP-03)` → `tool-abuse (MCP-03, ASI-07)`)
```

**Pass criteria**: All commands report OK. **BLOCKER FAIL on any modification beyond the cosmetic Q2 annotation.**

### Step 9 — Dependency manifest empty diff (SC-012)

```bash
git diff main -- pyproject.toml requirements.txt requirements-dev.txt package.json package-lock.json
# Expected: empty
```

**Pass criteria**: Empty output.

### Step 10 — Test suite execution

```bash
# F-3 specific tests
pytest tests/scripts/test_tool_abuse_enrichment.py -v
# Expected: all tests pass — structural-diff + line-count + MAESTRO grep + Category-9/10 source_attribution fixtures

# Backward compatibility on 5 non-multi-agent baselines (BLOCKER per SC-010)
SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py -v
# Expected: all 5 baselines (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice) byte-identical
```

**Pass criteria**: Both test suites green. **BLOCKER FAIL on any byte-identity regression.**

### Step 11 — Multi-agent example regeneration verification (SC-009, SC-011, SC-019)

```bash
# Inspect regenerated threats.md for new Category-9/10 AG findings
grep -E '^- \*\*AG-[0-9]+\*\*' examples/agentic-app/threats.md | head -20
# Expected: existing AG findings + ≥1 new AG finding citing OWASP ASI07:2026

# Confirm at least 1 new finding cites ASI07
grep -B 1 -A 5 'OWASP ASI07:2026' examples/agentic-app/threats.md
# Expected: ≥1 hit showing finding context

# Verify cohesive Agentic-category rendering (Categories 1-10 in same section)
grep -E '^## (Agentic|category: agentic)' examples/agentic-app/threat-report.md
# Expected: single section heading (no fragmentation across "tool-abuse" vs "asi07-inter-agent-communication" sub-sections)
```

**Pass criteria**: ≥1 new ASI07-citing finding present; single Agentic-category section in threat-report.md.

### Step 12 — F-A2 referential integrity validation (BLOCKER per SC-015)

```bash
# Run validate_source_attribution on all regenerated AG findings
python -c "
from scripts.tachi_parsers import validate_source_attribution
import yaml
with open('examples/agentic-app/threats.yaml') as f:
    threats = yaml.safe_load(f)
errors = []
for f in threats.get('findings', []):
    if f['id'].startswith('AG-') and 'source_attribution' in f:
        result = validate_source_attribution(f)
        if result.errors:
            errors.append((f['id'], result.errors))
if errors:
    print('FAIL:', errors); exit(1)
print(f'OK: {sum(1 for f in threats[\"findings\"] if f[\"id\"].startswith(\"AG-\"))} AG findings validated')
"
# Expected: OK with positive count
```

**Pass criteria**: No referential-integrity errors. **BLOCKER FAIL otherwise.**

### Step 13 — ADR-032 Accepted transition + cross-references (SC-008)

```bash
# Status field
grep '^**Status**:' docs/architecture/02_ADRs/ADR-032-asi07-tool-abuse-enrichment.md
# Expected: **Status**: Accepted

# Required Decisions present
grep -E '^### Decision (1|2|3|4|5|6|7):' docs/architecture/02_ADRs/ADR-032-asi07-tool-abuse-enrichment.md | wc -l
# Expected: ≥6 (target 7 with Pattern Category Disambiguation Decision 7)

# Required cross-references present
grep -E '(ADR-021|ADR-023|ADR-027|ADR-028|ADR-030|ADR-031)' docs/architecture/02_ADRs/ADR-032-asi07-tool-abuse-enrichment.md | wc -l
# Expected: ≥6 cross-references

# Zero MAESTRO references in Decision sections
grep -i 'maestro' docs/architecture/02_ADRs/ADR-032-asi07-tool-abuse-enrichment.md
# Expected: empty

# Revision History table present
grep '^## Revision History' docs/architecture/02_ADRs/ADR-032-asi07-tool-abuse-enrichment.md
# Expected: 1 match
```

**Pass criteria**: All five checks pass.

### Step 14 — PR title verification (SC-020)

```bash
gh pr view 220 --json title -q .title
# Expected: starts with "feat(219):"
```

**Pass criteria**: Title is `feat(219): asi07-tool-abuse-enrichment` or similar Conventional Commits form.

### Step 15 — Final pre-merge sanity check

Walk through the **PR Pre-Merge Checklist** in [plan.md](./plan.md) and tick every box. If all green:

```bash
gh pr ready 220
# Marks draft PR as ready for review
```

## Post-Merge Verification

### Step 16 — Release-please monitoring (SC-020 / R6)

```bash
# Wait ~30s after merge then check
sleep 30 && gh pr list --state open --search "release-please" --limit 3
# Expected: ≥1 release-please PR open

# If no release-please PR appears, recover via empty marker commit
# git commit --allow-empty -m "feat(219): asi07 enrichment — release marker"
# git push origin main
```

### Step 17 — Coverage Matrix update (SC-018)

```bash
# Update _internal/strategy/BLP-01-threat-coverage.md ASI07 row from Planned → Covered with F-3 named
# (manual edit; not automated)
```

### Step 18 — Delivery retrospective (SC-021)

If Day 1 PM merge has ≥1 hour residual capacity, file `specs/219-asi07-tool-abuse-enrichment/delivery.md` immediately. Otherwise, file on Buffer Day 1 (2026-04-29 Wed). Mirrors F-1 + F-2 precedent at `specs/201-...` and `specs/206-...`.

Required content: actual vs. estimated effort; **first-execution Heuristic A enrichment-pattern lessons** (precedent for F-6/F-7 Tier 2 ML+Mobile bundles); byte-identity preservation evidence (SC-006 + SC-010 grep proofs); deviations from PRD timeline or scope.

## Failure Recovery

| Failure | Recovery |
|---------|----------|
| Step 1 line-count >150 | Trim Purpose extension to 1 line; move worked-example references to companion catalog if needed |
| Step 5 byte-identity regression | Identify the unintended edit; revert to baseline content; ADR-023 Decision 3 violation must be 100% pre-merge |
| Step 7 schema diff non-empty | Hard revert; F-3 has zero schema bump scope |
| Step 8 zero-edit violation | Hard revert the off-scope file; investigate cause (likely accidental concurrent edit from F-4/F-5 build) |
| Step 10 backward-compat regression | Investigate dispatch-tier change; F-3 should produce zero new findings on 5 non-multi-agent baselines via topology gate |
| Step 11 zero new ASI07 findings | Architect re-evaluates example target; consider Q3 fallback to `maestro-reference` or new minimal multi-agent fixture |
| Step 12 referential integrity error | Verify catalog citations match `schemas/taxonomy/{owasp,cwe,mitre-atlas}.yaml`; remove offending citation |
| Step 14 PR title not Conventional Commits | `gh pr edit 220 --title "feat(219): asi07-tool-abuse-enrichment"` before merge |
| Step 16 release-please skip | Push empty `feat(219): ... release marker` commit per F-212 incident recovery pattern |

## References

- Plan: [plan.md](./plan.md)
- Spec: [spec.md](./spec.md)
- Data Model: [data-model.md](./data-model.md)
- Finding Contract: [contracts/finding-contract.md](./contracts/finding-contract.md)
- F-1 quickstart precedent: [specs/201-output-integrity-threat-agent/quickstart.md](../201-output-integrity-threat-agent/quickstart.md)
- F-2 quickstart precedent: [specs/206-misinformation-threat-agent/quickstart.md](../206-misinformation-threat-agent/quickstart.md)
