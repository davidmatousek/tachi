# Quickstart: F-5 Verification Walkthrough

**Feature**: 229 / F-5 LLM10 Unbounded Consumption Verification
**Phase**: 1 (Design & Contracts)

## Purpose

Step-by-step verification walkthrough for F-5 deliverables — confirms ≥1 new `D-{N}` finding (Cat 12 OR 13) AND ≥1 new `LLM-{N}` finding (Cat 10 OR 11) emit on the regenerated `examples/agentic-app/` with valid `references` array, valid LLM-specific mitigation text, passing structural validations, and 6 non-LLM-serving baselines byte-identical under `SOURCE_DATE_EPOCH=1700000000`.

## Prerequisites

- F-5 build is complete through Wave 2 (DoS + model-theft enrichment edits applied; example regen on `agentic-app` complete).
- ADR-034 is at Proposed state (Wave 1.1 commit).
- Working tree is on `229-llm10-unbounded-consumption-verification` branch.

## Step 1 — Structural Validation (line counts + MAESTRO grep)

```bash
# Line count caps — both BLOCKERs
wc -l .claude/agents/tachi/denial-of-service.md
# Expected: ≤120 (target 56-60)

wc -l .claude/agents/tachi/model-theft.md
# Expected: ≤150 (target 98-102)

# MAESTRO zero-reference invariant — BLOCKER
grep -ic 'maestro' \
  .claude/agents/tachi/denial-of-service.md \
  .claude/agents/tachi/model-theft.md \
  .claude/skills/tachi-denial-of-service/references/detection-patterns.md \
  .claude/skills/tachi-model-theft/references/detection-patterns.md
# Expected: 0:0:0:0
```

## Step 2 — owasp_references metadata + Purpose extension verification

```bash
# DoS owasp_references — LLM10 added as 10th entry
grep -A 12 '^owasp_references:' .claude/agents/tachi/denial-of-service.md | grep -c 'LLM10'
# Expected: 1 (LLM10 present)

# DoS Purpose extension — naming LLM-inference-exhaustion surface
grep -A 6 '^## Purpose' .claude/agents/tachi/denial-of-service.md | grep -ciE 'inference|llm|token-budget|context-window'
# Expected: ≥1 mention

# model-theft owasp_references — LLM10 already present (zero net change)
grep '^owasp_references:' .claude/agents/tachi/model-theft.md
# Expected: includes "OWASP LLM10:2025"

# model-theft Purpose extension — naming cost-amplification + denial-of-wallet
grep -A 6 '^## Purpose' .claude/agents/tachi/model-theft.md | grep -ciE 'cost-amplification|denial-of-wallet|recursive|cost-asymmetric'
# Expected: ≥1 mention
```

## Step 3 — Pattern Category presence + structure verification

```bash
# DoS companion — Cat 12 + Cat 13 present
grep -c '^## Pattern Category 1[23]' .claude/skills/tachi-denial-of-service/references/detection-patterns.md
# Expected: 2 (Cat 12 + Cat 13)

# model-theft companion — Cat 10 + Cat 11 present
grep -c '^## Pattern Category 1[01]' .claude/skills/tachi-model-theft/references/detection-patterns.md
# Expected: 2 (Cat 10 + Cat 11)

# Cat 12 indicators — ≥4 bullets
sed -n '/^## Pattern Category 12/,/^## Pattern Category 13/p' \
  .claude/skills/tachi-denial-of-service/references/detection-patterns.md \
  | grep -c '^- '
# Expected: ≥5 (4 indicators + 1 mitigation; targets 5+ each)

# Cat 11 severity-floor 2-condition note present
grep -A 30 '^## Pattern Category 11' \
  .claude/skills/tachi-model-theft/references/detection-patterns.md \
  | grep -ciE 'critical floor|2-condition|multi-tenant freemium'
# Expected: ≥1 mention

# T1496 in mitigation prose only on Cat 10/11
grep -c 'T1496' .claude/skills/tachi-model-theft/references/detection-patterns.md
# Expected: ≥2 (one in Cat 10 mitigation, one in Cat 11 mitigation)

# T1496 NOT cited as structured taxonomy reference
grep -E '^- *taxonomy: *(mitre|attack)' .claude/skills/tachi-model-theft/references/detection-patterns.md | grep -i T1496
# Expected: 0 (T1496 prose-only, NOT in references)
```

## Step 4 — Existing Pattern Category byte-identity (BLOCKER)

```bash
# Capture pre-edit (from main branch) and post-edit (working tree) snapshots
# DoS companion Cat 1-11 + Overview + Targeted DFD + Primary Sources (existing entries)
git show main:.claude/skills/tachi-denial-of-service/references/detection-patterns.md \
  > /tmp/dos-pre.md
git show HEAD:.claude/skills/tachi-denial-of-service/references/detection-patterns.md \
  > /tmp/dos-post.md

# Extract pre-edit content + post-edit content for Cat 1-11 region
sed -n '1,/^## Pattern Category 12/p' /tmp/dos-post.md | head -n -1 \
  > /tmp/dos-post-1-11-region.md
diff /tmp/dos-pre.md /tmp/dos-post-1-11-region.md
# Expected: empty diff (byte-identity preserved on Cat 1-11 + Overview + Targeted DFD)

# model-theft companion Cat 1-9 + Overview + Targeted DFD + Trigger Keywords (line 19)
git show main:.claude/skills/tachi-model-theft/references/detection-patterns.md \
  > /tmp/mt-pre.md
git show HEAD:.claude/skills/tachi-model-theft/references/detection-patterns.md \
  > /tmp/mt-post.md
sed -n '1,/^## Pattern Category 10/p' /tmp/mt-post.md | head -n -1 \
  > /tmp/mt-post-1-9-region.md
diff /tmp/mt-pre.md /tmp/mt-post-1-9-region.md
# Expected: empty diff
```

## Step 5 — Schema invariant + 24-file zero-edit invariant

```bash
# Schema unchanged
diff <(git show main:schemas/finding.yaml) schemas/finding.yaml
# Expected: empty diff

# 24-file zero-edit invariant — none of the 12 other agents OR 12 other companions edited
for agent in spoofing tampering repudiation info-disclosure privilege-escalation prompt-injection data-poisoning agent-autonomy tool-abuse output-integrity misinformation human-trust-exploitation; do
  diff <(git show main:.claude/agents/tachi/${agent}.md) .claude/agents/tachi/${agent}.md
done
# Expected: 12 empty diffs

for skill in tachi-spoofing tachi-tampering tachi-repudiation tachi-info-disclosure tachi-privilege-escalation tachi-prompt-injection tachi-data-poisoning tachi-agent-autonomy tachi-tool-abuse tachi-output-integrity tachi-misinformation tachi-human-trust-exploitation; do
  diff <(git show main:.claude/skills/${skill}/references/detection-patterns.md) .claude/skills/${skill}/references/detection-patterns.md
done
# Expected: 12 empty diffs

# finding-format-shared.md unchanged
diff <(git show main:.claude/skills/tachi-shared/references/finding-format-shared.md) .claude/skills/tachi-shared/references/finding-format-shared.md
# Expected: empty diff

# orchestrator.md unchanged
diff <(git show main:.claude/agents/tachi/orchestrator.md) .claude/agents/tachi/orchestrator.md
# Expected: empty diff

# dispatch-rules.md unchanged (Q2 plan-day NO; cosmetic annotation skipped)
diff <(git show main:.claude/skills/tachi-orchestration/references/dispatch-rules.md) .claude/skills/tachi-orchestration/references/dispatch-rules.md
# Expected: empty diff (or 1-token cosmetic if architect overrode Q2 to YES at Wave 1.0)

# Infrastructure-tier consumer agents unchanged
for consumer in risk-scorer control-analyzer threat-report threat-infographic report-assembler; do
  diff <(git show main:.claude/agents/tachi/${consumer}.md) .claude/agents/tachi/${consumer}.md
done
# Expected: 5 empty diffs

# Dependency manifest unchanged
diff <(git show main:pyproject.toml) pyproject.toml
diff <(git show main:requirements.txt) requirements.txt 2>/dev/null || true
# Expected: empty diffs
```

## Step 6 — Example regeneration verification (FR-013, SC-013, SC-015)

```bash
# Regenerate example
SOURCE_DATE_EPOCH=1700000000 /tachi.threat-model examples/agentic-app/architecture.md
SOURCE_DATE_EPOCH=1700000000 /tachi.risk-score examples/agentic-app/threats.md
SOURCE_DATE_EPOCH=1700000000 /tachi.compensating-controls examples/agentic-app/threats.md examples/agentic-app/risk-scores.md
SOURCE_DATE_EPOCH=1700000000 /tachi.infographic all examples/agentic-app/threats.md examples/agentic-app/compensating-controls.md
SOURCE_DATE_EPOCH=1700000000 /tachi.security-report examples/agentic-app/

# Confirm new findings emit
grep -c '^# D-' examples/agentic-app/threats.md  # all D-{N} findings
# Expected: ≥1 increase from main baseline (post-F-3 + F-4 baseline + at least 1 new Cat 12/13)

grep -c '^# LLM-' examples/agentic-app/threats.md  # all LLM-{N} findings
# Expected: ≥1 increase from main baseline (at least 1 new Cat 10/11)

# Confirm LLM10 cited on at least 1 new D-{N} and LLM-{N} finding
grep -B 2 -A 30 '^# D-' examples/agentic-app/threats.md | grep -c 'OWASP LLM10:2025'
# Expected: ≥1

grep -B 2 -A 30 '^# LLM-' examples/agentic-app/threats.md | grep -c 'OWASP LLM10:2025'
# Expected: ≥1

# Confirm CWE-400 on at least 1 D-{N} finding
grep -B 2 -A 30 '^# D-' examples/agentic-app/threats.md | grep -c 'CWE-400'
# Expected: ≥1

# Confirm T1496 in mitigation prose on at least 1 LLM-{N} finding (Cat 10 OR 11)
grep -B 2 -A 30 '^# LLM-' examples/agentic-app/threats.md | grep -c 'T1496'
# Expected: ≥1 (Cat 10 or 11 mitigation prose)
```

## Step 7 — 6 non-LLM-serving baseline byte-identity gate (SC-014, BLOCKER)

```bash
# Owner: tester agent per team-lead MEDIUM-2
SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py -v
# Expected: 6 baselines pass (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice, maestro-reference)

# Per-baseline manual verification (in case test framework needs update)
for baseline in web-app microservices ascii-web-api mermaid-agentic-app free-text-microservice maestro-reference; do
  SOURCE_DATE_EPOCH=1700000000 /tachi.security-report examples/${baseline}/
  diff examples/${baseline}/security-report.pdf examples/${baseline}/security-report.pdf.baseline
  echo "---"
done
# Expected: 6 empty diffs
```

## Step 8 — Test fixture validation (SC-019)

```bash
# Run the F-5 enrichment test suite
pytest tests/scripts/test_llm10_unbounded_consumption_enrichment.py -v
# Expected: all tests pass (structural-diff + line-count + MAESTRO grep + Cat 12/13/10/11 references-array fixtures)

# Per-fixture references-array verification
for fixture in tests/scripts/fixtures/llm10_unbounded_consumption/valid_*.yaml; do
  python -c "
import yaml
with open('$fixture') as f:
    finding = yaml.safe_load(f)
refs = finding.get('references', [])
assert any('LLM10' in r for r in refs), f'$fixture: LLM10 missing'
if 'D-' in finding['id']:
    assert any('CWE-400' in r for r in refs), f'$fixture: CWE-400 missing on D-{N}'
print('$fixture: PASS')
"
done
# Expected: all fixtures PASS
```

## Step 9 — ADR-034 verification

```bash
# ADR-034 file present
ls docs/architecture/02_ADRs/ADR-034-llm10-unbounded-consumption-audit.md
# Expected: file exists

# ADR-034 contains 9 numbered Decisions
grep -c '^## Decision [1-9]' docs/architecture/02_ADRs/ADR-034-llm10-unbounded-consumption-audit.md
# Expected: 9

# ADR-034 contains 5-row mapping table per Decision 3
grep -A 12 '^## Decision 3' docs/architecture/02_ADRs/ADR-034-llm10-unbounded-consumption-audit.md \
  | grep -ciE 'inference-request flooding|context-window|cost amplification|denial-of-wallet'
# Expected: ≥4 mentions (5 rows minus header)

# Cross-references present
grep -ciE 'ADR-021|ADR-023|ADR-027|ADR-028|ADR-030|ADR-031|ADR-032|ADR-033' \
  docs/architecture/02_ADRs/ADR-034-llm10-unbounded-consumption-audit.md
# Expected: ≥8 cross-references

# Status transitions
grep -i 'Status:' docs/architecture/02_ADRs/ADR-034-llm10-unbounded-consumption-audit.md
# Expected: at Wave 1.1: "Status: Proposed"; at Wave 3: "Status: Accepted"

# Zero MAESTRO references in ADR Decision sections
grep -ic maestro docs/architecture/02_ADRs/ADR-034-llm10-unbounded-consumption-audit.md
# Expected: 0 (MAESTRO MAY appear in ADR if discussing inheritance semantics, but not as a Decision element)
```

## Step 10 — PR title verification

```bash
# Check current PR title
gh pr view --json title --jq .title
# Expected: starts with "feat(229):" — e.g., "feat(229): llm10 unbounded consumption verification"

# Pre-merge re-verification (Wave 4)
gh pr view --json title,state --jq '{title, state}'
# Expected: title starts with "feat(229):"; state is "OPEN" or "READY_FOR_REVIEW"

# Post-merge release-please verification (Wave 4 +30s)
gh pr list --state open --search "release-please" --limit 3
# Expected: at least 1 release-please PR opened within ~30s of squash-merge
```

## Step 11 — Coverage Matrix update verification (SC-021)

```bash
# Post-merge documentation commit on _internal/strategy/BLP-01-threat-coverage.md
grep -A 2 '^| LLM10' _internal/strategy/BLP-01-threat-coverage.md
# Expected: row shows "Covered" status with F-5 (Feature 229) named as closure feature

# OWASP LLM Top 10 framework rollup
grep -A 3 'LLM Top 10:2025' _internal/strategy/BLP-01-threat-coverage.md | grep -i covered
# Expected: "10 of 10 Covered"
```

## Step 12 — Delivery retrospective filing (SC-022)

```bash
# Delivery retrospective at specs/229.../delivery.md
ls specs/229-llm10-unbounded-consumption-verification/delivery.md
# Expected: file exists

# Captures required content per DoD bullet 15
grep -ciE 'actual.*estimated|heuristic A|two-agent|byte-identity|Q1 SPLIT|mapping table|SHA-fill' \
  specs/229-llm10-unbounded-consumption-verification/delivery.md
# Expected: ≥4 mentions covering required reflective dimensions
```

## Success Verdict

If Steps 1-12 all pass, F-5 is verified delivery-ready:
- All 22 spec SCs satisfied
- All 22 spec FRs implemented additively
- 24-file zero-edit invariant preserved
- 6-baseline byte-identity gate passes
- Catalog references resolve (LLM10, CWE-400, CWE-770, LLM03)
- T1496 prose-only mention preserved
- ADR-034 Accepted with mapping table populated complete
- LLM10:2025 Partial → Covered; OWASP LLM Top 10 = 10/10; OWASP AI top-10 = 20/20

## References

- F-3 quickstart precedent: `specs/219-asi07-tool-abuse-enrichment/quickstart.md`
- F-4 quickstart precedent: `specs/224-trust-exploitation-threat-agent/quickstart.md`
- Plan: `plan.md`
- Spec: `spec.md`
- Finding contract: `contracts/finding-contract.md`
- Data model: `data-model.md`
