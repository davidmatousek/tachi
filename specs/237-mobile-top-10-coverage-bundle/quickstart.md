# Quickstart: F-7 Mobile Top 10 Coverage Bundle Verification

**Feature**: 237-mobile-top-10-coverage-bundle
**Date**: 2026-04-28
**Source**: Inline §Phase 1 → Quickstart in [plan.md](./plan.md)

---

## Purpose

Walk through verifying F-7 enrichment on the new `examples/mobile-banking-app/` mutation target and confirming byte-identity preservation on the 6 non-mobile baselines. **Note**: full wave-by-wave verification flow is inlined in [plan.md](./plan.md) §Phase 1 → Quickstart and §Wave Allocation. This file holds the operator-facing command summary.

---

## Pre-Build Verification

Before any wave runs, confirm the baselines (single source of truth = [research.md](./research.md)):

```bash
# 1. Spec-time line counts unchanged at plan time
wc -l .claude/agents/tachi/{spoofing,tampering,info-disclosure,privilege-escalation,repudiation}.md
# Expect: 51, 55, 54, 52, 50

wc -l .claude/skills/tachi-{spoofing,tampering,info-disclosure,privilege-escalation,repudiation}/references/detection-patterns.md
# Expect: 146, 221, 192, 213, 148

# 2. Schema unchanged
grep "^schema_version" schemas/finding.yaml
# Expect: schema_version: "1.8"

grep "pattern:" schemas/finding.yaml | head -1
# Expect: pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\\d+$"

# 3. M1-M10 catalog-resolvable
grep -c "^- id: M[0-9]" schemas/taxonomy/owasp.yaml
# Expect: 10

# 4. T1474 / T1626 / T1398 NOT catalog-resolvable (Q3 plan-time RESOLVED prose-only)
grep "T1474\|T1626\|T1398" schemas/taxonomy/mitre-attack.yaml
# Expect: (no output)

# 5. Mobile-signal grep on existing examples
grep -rln "android\|ios\|mobile\|keystore\|keychain\|sharedpref\|nsuser" examples/*/architecture.md
# Expect: only examples/microservices/architecture.md (incidental "mobile app" External Entity descriptor — NOT structural)
```

---

## During-Build Verification (per Wave)

### After Wave 0.1 (Wed 2026-04-29 AM-early)

```bash
# mobile-banking-app full draft present
ls examples/mobile-banking-app/architecture.md
wc -l examples/mobile-banking-app/architecture.md
# Expect: ~180-220 lines

# ADR-036 Proposed
ls docs/architecture/02_ADRs/ADR-036-mobile-top-10-coverage-bundle.md
grep -E "^Status:" docs/architecture/02_ADRs/ADR-036-mobile-top-10-coverage-bundle.md
# Expect: Status: Proposed
```

### After Wave 1.1 (Wed 2026-04-29 AM-late)

```bash
wc -l .claude/agents/tachi/spoofing.md
# Expect: 55-60 lines (≤120 cap preserved)

wc -l .claude/skills/tachi-spoofing/references/detection-patterns.md
# Expect: ~200-220 lines

grep -c "## Pattern Category Disambiguation" .claude/skills/tachi-spoofing/references/detection-patterns.md
# Expect: 1
```

### After Wave 2.x (Wed 2026-04-29 PM)

```bash
wc -l .claude/agents/tachi/tampering.md
# Expect: 60-66 lines (≤120 cap preserved)

wc -l .claude/skills/tachi-tampering/references/detection-patterns.md
# Expect: ~315-345 lines

grep -c "## Pattern Category Disambiguation" .claude/skills/tachi-tampering/references/detection-patterns.md
# Expect: 1
```

### After Wave 3.x (Thu 2026-04-30 AM)

```bash
wc -l .claude/agents/tachi/info-disclosure.md
# Expect: 60-66 lines (≤120 cap preserved)

wc -l .claude/skills/tachi-info-disclosure/references/detection-patterns.md
# Expect: ~315-345 lines

grep -c "## Pattern Category Disambiguation" .claude/skills/tachi-info-disclosure/references/detection-patterns.md
# Expect: 1
```

### After Wave 4.0 / 4.0b (Thu 2026-04-30 PM, dual-host M8 path)

```bash
wc -l .claude/agents/tachi/privilege-escalation.md .claude/agents/tachi/repudiation.md
# Expect: 56-58, 54-56 lines (≤120 cap preserved)

wc -l .claude/skills/tachi-privilege-escalation/references/detection-patterns.md .claude/skills/tachi-repudiation/references/detection-patterns.md
# Expect: ~245-260, ~180-195 lines

grep -c "## Pattern Category Disambiguation" .claude/skills/tachi-privilege-escalation/references/detection-patterns.md .claude/skills/tachi-repudiation/references/detection-patterns.md
# Expect: 1, 1
```

### After Wave 4.1 (Thu 2026-04-30 PM, tester early-signal spot-check)

```bash
# 1-2 baseline byte-identity spot-check (web-app + maestro-reference)
SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py -k "byte_identity and (web_app or maestro_reference)" -v
# Expect: 2 passed
```

### After Wave 4.2 (Thu 2026-04-30 PM late)

```bash
# Full mobile-banking-app pipeline regen
cd examples/mobile-banking-app/
# (Pipeline executed via /tachi.threat-model → /tachi.risk-score → /tachi.compensating-controls → /tachi.infographic all → /tachi.security-report)
ls sample-report/security-report.pdf.baseline
# Expect: present (new mutation target baseline)

# ≥10 new mobile findings (≥1 per M1-M10; ≥11 in dual-host with M8 split)
grep -c "^id: " threats.md
# Expect: total finding count >= existing baselines + 10 (or 11)

grep -c "OWASP M[0-9]:2024" threats.md
# Expect: ≥10 (or ≥11 dual-host)
```

---

## Post-Build Verification (Wave 5.x)

### Wave 5.0 (Fri 2026-05-01 AM-1, tester full byte-identity)

```bash
SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py -k "byte_identity" -v
# Expect: 6 passed (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice, maestro-reference)
```

### Wave 5.1 (Fri 2026-05-01 AM-2, ADR-036 Accepted)

```bash
grep -E "^Status:" docs/architecture/02_ADRs/ADR-036-mobile-top-10-coverage-bundle.md
# Expect: Status: Accepted (provisional pre-merge; final SHA filled post-merge per FR-26-equivalent)
```

### Wave 5.2 (Fri 2026-05-01 AM, test infrastructure)

```bash
pytest tests/scripts/test_mobile_top_10_coverage_bundle_enrichment.py -v
# Expect: all enrichment tests passing — line caps, MAESTRO grep, MANDATORY Read directive, Pattern Category Disambiguation 5x dual-host (4x single-host fallback), references-array fixtures (10 dual-host, 9 single-host), ATT&CK Mobile catalog-resolvability gap T1474/T1626/T1398 prose-only

pytest tests/scripts/test_backward_compatibility.py -v
# Expect: 6/6 byte-identity baselines passing + DETECTION_AGENT_PATHS / DETECTION_PATTERN_REF_ENRICHMENT_HOSTS counts updated correctly
```

### Wave 5.3 (Fri 2026-05-01 PM, BLP-01 Coverage Matrix)

```bash
grep -E "^| M[0-9]+ \|" _internal/strategy/BLP-01-threat-coverage.md | head -10
# Expect: M1-M10 rows show "Covered" status with "Feature 237 (F-7)" closure-feature column
```

### Final diff verification

```bash
# Detection-tier diff scope
git diff main HEAD -- '.claude/agents/tachi/' '.claude/skills/tachi-*/references/' | grep "^diff --git"
# Expect: 10 files dual-host (8 single-host fallback)

# 18-or-20 of 28 file zero-edit invariant
find .claude/agents/tachi -name "*.md" | wc -l
# Expect: 14 (excluding orchestrator + risk-scorer + control-analyzer + threat-report + threat-infographic + report-assembler infrastructure agents — but counting only detection-tier hosts; verify exact count via test_backward_compatibility.py)

find .claude/skills/tachi-* -name "detection-patterns.md" | wc -l
# Expect: 14

# Schema invariant
git diff main HEAD -- schemas/finding.yaml
# Expect: empty

# Orchestrator-tier zero-edit invariant
git diff main HEAD -- .claude/agents/tachi/orchestrator.md .claude/skills/tachi-orchestration/references/dispatch-rules.md .claude/skills/tachi-shared/references/finding-format-shared.md
# Expect: empty (or annotation-only if architect Wave 1 catalogues a cosmetic update — default is zero edits)

# MAESTRO grep zero-mention invariant on enriched files
grep -i "maestro" .claude/agents/tachi/{spoofing,tampering,info-disclosure,privilege-escalation,repudiation}.md .claude/skills/tachi-{spoofing,tampering,info-disclosure,privilege-escalation,repudiation}/references/detection-patterns.md
# Expect: 0 matches

# Prior-feature mutation targets zero-touch
git diff main HEAD -- examples/agentic-app/ examples/consumer-agent-app/ examples/predictive-ml-app/
# Expect: empty
```

---

## Acceptance Gates Summary

| Gate | Threshold | Owner | Wave |
|------|-----------|-------|------|
| Line cap ≤120 on all 5 host agents | 5 of 5 within cap | senior-backend-engineer | 1.1, 2.0, 3.0, 4.0, 4.0b |
| Companion line counts within plan estimates | within ±10% | senior-backend-engineer | 1.1, 2.x, 3.x, 4.0, 4.0b |
| Pattern Category Disambiguation subsections | 5 dual-host (4 single-host) | senior-backend-engineer | each enrichment wave |
| MAESTRO zero-mention | 0 matches across 10 files | senior-backend-engineer | 5.2 (test gate) |
| Schema invariant | finding.yaml unchanged at v1.8 | senior-backend-engineer | 5.2 (test gate) |
| 6 baseline byte-identity | 6 of 6 passing | tester | 5.0 |
| ≥10 mobile findings on mutation target | ≥10 (≥11 dual-host) | senior-backend-engineer | 4.2 |
| ADR-036 Accepted with SHA fill | post-merge | architect | 5.1 + post-merge |
| BLP-01 Coverage Matrix M1-M10 transitioned | 10 rows Planned → Covered | senior-backend-engineer | 5.3 |
| Triple Triad sign-off on tasks.md | PM + Architect + Team-Lead APPROVED | governance | 5.4 |
| `feat(237):` Conventional Commit on PR | pre-merge title verified | senior-backend-engineer + architect | 5.5 |
| release-please PR opened post-merge | within ~30s of merge | senior-backend-engineer | 5.5 |
