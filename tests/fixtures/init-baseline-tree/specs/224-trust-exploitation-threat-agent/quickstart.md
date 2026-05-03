# Quickstart: Verifying Feature 224 — `human-trust-exploitation` Threat Agent

**Phase**: 1 (Design & Contracts — verification walkthrough)
**Date**: 2026-04-26

## Goal

Demonstrate end-to-end that the `human-trust-exploitation` agent emits ≥1 valid `TE-{N}` finding on the regenerated example architecture (Q5 lean: `examples/consumer-agent-app/`; Q5 fallback: `examples/agentic-app/` extension), passes F-A2 referential-integrity validation, and surfaces correctly in the rendered `threat-report.md` without prose-synthesis collisions with adjacent finding families.

## Prerequisites

- Branch: `224-trust-exploitation-threat-agent` checked out
- All Wave 1-5 tasks complete (agent file + companion skill + ADR-033 + schema bump + 6 coordinated additive edits + example regeneration)
- Working directory: tachi repo root

## Step 1 — Schema sanity (post-bump verification)

Confirm schema is at v1.8 with TE prefix in regex:

```bash
grep -E '^(schema_version|  pattern):' schemas/finding.yaml | head -3
```

**Expected**:
```
schema_version: "1.8"
  pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\\d+$"
```

Run the regex unit test:

```bash
pytest tests/scripts/test_human_trust_exploitation.py::test_regex_matches_te_prefix -v
```

**Expected**: PASS — `TE-1`, `TE-99` match; malformed values rejected.

## Step 2 — Agent file structural validation

```bash
wc -l .claude/agents/tachi/human-trust-exploitation.md
grep -c '\*\*MANDATORY\*\*: Read' .claude/agents/tachi/human-trust-exploitation.md
grep -i maestro .claude/agents/tachi/human-trust-exploitation.md
grep -i maestro .claude/skills/tachi-human-trust-exploitation/references/detection-patterns.md
```

**Expected**:
- `wc -l`: ≤150 (≤180 hard ceiling)
- `grep -c '\*\*MANDATORY\*\*: Read'`: 1 (exactly one MANDATORY Read directive)
- Both `grep -i maestro` invocations: empty output (zero MAESTRO references)

## Step 3 — Wave 2.0 grep-checklist verification (FR-009 / SC-015)

Confirm all 6 coordinated edits landed:

```bash
# orchestrator.md (3 edits)
grep -c "human-trust-exploitation" .claude/agents/tachi/orchestrator.md
# Expected: ≥2 (dispatch list addition + Agentic Threats row update; sequential-mode text optional)

# dispatch-rules.md (3 edits)
grep -c "human-trust-exploitation" .claude/skills/tachi-orchestration/references/dispatch-rules.md
# Expected: ≥3 (dispatch list + table row + trigger-keyword rules)

# finding-format-shared.md
grep "human-trust-exploitation" .claude/skills/tachi-shared/references/finding-format-shared.md
# Expected: 1 line in `consumers:` between `tool-abuse` and `output-integrity`
```

## Step 4 — Run threat model on regenerated example

For Q5 lean (`examples/consumer-agent-app/`):

```bash
/tachi.threat-model examples/consumer-agent-app/architecture.md
```

For Q5 fallback (`examples/agentic-app/` extension), substitute the path. Pipeline output:

```bash
/tachi.risk-score examples/{consumer-agent-app|agentic-app}
/tachi.compensating-controls examples/{consumer-agent-app|agentic-app}
/tachi.infographic all examples/{consumer-agent-app|agentic-app}
/tachi.security-report examples/{consumer-agent-app|agentic-app}
```

## Step 5 — Verify TE-{N} finding emission (SC-004)

```bash
grep -E '^- id: "TE-[0-9]+"' examples/{consumer-agent-app|agentic-app}/threats.md | head -5
```

**Expected**: ≥1 line. Each `TE-{N}` finding has `category: "agentic"`, populated `source_attribution` array starting with `{taxonomy: "owasp", id: "ASI09", relationship: "primary"}`, and a non-generic `mitigation` field naming a specific AI-disclosure / confidence-calibration / refusal-pattern / persona-boundary / synthetic-relationship-safeguard mechanism.

## Step 6 — F-A2 referential-integrity validation (SC-010)

```bash
python3 scripts/tachi_parsers.py validate-source-attribution examples/{consumer-agent-app|agentic-app}/threats.md
```

**Expected**: zero validation errors. Every `TE-{N}` finding's `source_attribution` references catalog-resolvable IDs only:
- `OWASP ASI09:2026` (verified at `schemas/taxonomy/owasp.yaml:318-322`)
- `CWE-223` / `CWE-287` / `CWE-290` / `CWE-345` (verified at `cwe.yaml:82,106,110,118`)
- **NOT** `CWE-451` (absent from catalog)
- **NOT** MITRE ATLAS entries (no direct trust-exploitation match)
- **NOT** external regulatory references (FTC/FDA/ABA/SEC/SB-1001/AARP)

## Step 7 — Three-prefix-family discipline within agentic (SC-014)

```bash
# Look for AG-, AGP-, TE- prefixes in the agentic section of threat-report.md
grep -E '^- (AG|AGP|TE)-[0-9]+' examples/{consumer-agent-app|agentic-app}/threat-report.md
```

**Expected**: AG-{N}, AGP-{N} (if multi-agent topology applicable), TE-{N} prefixes appear adjacent in the `## Agentic Threats` section without prose synthesis. Each finding ID is preserved as a distinct bullet/section.

## Step 8 — FR-018 grep-checkable test (R11 mitigation / SC-012)

```bash
pytest tests/scripts/test_human_trust_exploitation.py::test_no_agp_te_prose_synthesis -v
```

**Expected**: PASS — `AGP-` and `TE-` prefixes appear in distinct prose blocks (no shared bullet, no shared sentence, no shared synthesis paragraph) on the regenerated `threat-report.md`. This verifies that the report-tier rendering preserves the Naming Disambiguation discipline — `AGP-{N}` (multi-agent topology, agentic_pattern: trust_exploitation) and `TE-{N}` (human-trust communication axis) findings render separately.

## Step 9 — Backward-compatibility byte-identity (SC-006)

```bash
SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py -v
```

**Expected**: PASS on all 5 non-consumer-facing baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`). The PDF SHA-256 digests match the post-F-3 baselines exactly — zero qualifying Process + human-user-facing emission indicator means zero new findings, means unchanged report content, means byte-identical PDFs.

## Step 10 — 26-file zero-edit invariant (SC-009)

```bash
git diff main..HEAD --stat -- .claude/agents/tachi/ .claude/skills/ | grep -v "human-trust-exploitation\|orchestrator.md\|dispatch-rules.md\|finding-format-shared.md"
```

**Expected**: empty output (no other detection-tier files modified). Confirms 26-file invariant including `agent-autonomy.md` NOT-edit despite the ASI09 sub-scope carve-up.

## Step 11 — NFR-006 + NFR-007 spot-check

Code-reviewer at Wave 6 runs:

```bash
# NFR-006 four safe-language patterns
grep -c 'Hypothetical:' .claude/skills/tachi-human-trust-exploitation/references/detection-patterns.md
# Expected: ≥5 (one per worked example)

grep -c 'for context, not legal interpretation' .claude/skills/tachi-human-trust-exploitation/references/detection-patterns.md
# Expected: ≥1 (regulatory-citation framing)

grep -i 'suicidal ideation\|clinical depression' .claude/skills/tachi-human-trust-exploitation/references/detection-patterns.md
# Expected: empty (non-clinical distress framing — uses "user expresses high emotional distress" instead)

# NFR-007 self-disclosure discipline (no persuasive language)
grep -i 'you really should\|critical to fix immediately' .claude/skills/tachi-human-trust-exploitation/references/detection-patterns.md
# Expected: empty
```

## Step 12 — PR title verification (R12 / SC-013)

```bash
gh pr view --json title --jq '.title'
```

**Expected**: starts with `feat(224):` (Conventional-Commit-formatted). At deliver-stage, also verify post-merge release-please PR exists:

```bash
gh pr list --state open --search "release-please" --limit 3
```

**Expected**: at least one release-please PR opened within ~30s of squash-merge. If empty, push empty `feat(224):` marker commit on main.

## Acceptance Summary

The feature is verified complete when all 12 steps return the expected outputs. Map to spec SCs:

| Step | Spec SC | Verifies |
|------|---------|----------|
| 1 | (FR-011) | Schema bump 1.7 → 1.8 with TE prefix |
| 2 | SC-001 | Agent file structural validation |
| 3 | SC-015 | Wave 2.0 grep-checklist (6 coordinated edits) |
| 4-5 | SC-004, SC-007 | Regenerated example emits ≥1 TE-{N} finding |
| 6 | SC-010 | F-A2 referential-integrity validation |
| 7 | SC-014 | Three-prefix-family discipline within agentic |
| 8 | SC-012 | FR-018 grep test (R11 mitigation) |
| 9 | SC-006 | Byte-identity on 5 non-consumer-facing baselines |
| 10 | SC-009 | 26-file zero-edit invariant including agent-autonomy.md NOT-edit |
| 11 | (NFR-006, NFR-007) | Safe-language + self-disclosure discipline |
| 12 | SC-013 | PR title + release-please verification |

Combined with the broader PR pre-merge checklist in plan.md, this quickstart constitutes the end-to-end verification path for Feature 224.
