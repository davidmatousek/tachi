# Quickstart: F-6 ML Top 10 Coverage Bundle Verification

**Feature**: 232 — ML Top 10 Coverage Bundle
**Phase**: 1 (Design)
**Generated**: 2026-04-27

This walkthrough verifies F-6 enrichment on the new `examples/predictive-ml-app/` architecture and confirms byte-identity preservation on the 6 non-predictive-ML baselines.

---

## Prerequisites

- Branch: `232-ml-top-10-coverage-bundle` (current)
- Draft PR #233 opened with `feat(232): ML Top 10 Coverage Bundle` title
- All 6 file edits applied per Wave 1.1 + Wave 2.x + Wave 3.x of plan.md
- ADR-035 Proposed at Wave 1.0
- New `examples/predictive-ml-app/architecture.md` authored at Wave 0.0

---

## Verification flow

### 1. Static checks (post-edit, pre-regen)

```bash
# Line-count caps (FR-001 / SC-002 + FR-005 / SC-007 + FR-008 / SC-011)
wc -l .claude/agents/tachi/{tampering,data-poisoning,model-theft}.md
# Expected: 54-58 / 84-90 / 103-108 (all within respective tier caps)

# Six-file edit invariant (US-2 acceptance scenario 1)
git diff --name-only main HEAD -- '.claude/agents/tachi/' '.claude/skills/tachi-*/references/'
# Expected: exactly 6 files
#   .claude/agents/tachi/tampering.md
#   .claude/agents/tachi/data-poisoning.md
#   .claude/agents/tachi/model-theft.md
#   .claude/skills/tachi-tampering/references/detection-patterns.md
#   .claude/skills/tachi-data-poisoning/references/detection-patterns.md
#   .claude/skills/tachi-model-theft/references/detection-patterns.md

# Schema invariant (FR-017 / SC-022)
grep -E '^schema_version:|^\s+pattern:' schemas/finding.yaml | head -3
# Expected: schema_version: "1.8" + pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\\d+$"

# Pattern Category Disambiguation header presence (FR-011 / SC-014)
grep -c "Pattern Category Disambiguation" .claude/skills/tachi-{tampering,data-poisoning,model-theft}/references/detection-patterns.md
# Expected: 1 / 1 / 1 (3 total — one per host companion)

# Zero MAESTRO references (FR-015 / SC-024)
grep -i 'maestro' .claude/agents/tachi/{tampering,data-poisoning,model-theft}.md .claude/skills/tachi-{tampering,data-poisoning,model-theft}/references/detection-patterns.md
# Expected: no matches (exit 1)

# Consumers list unchanged (FR-018 / SC-025)
git diff main HEAD -- .claude/skills/tachi-shared/references/finding-format-shared.md
# Expected: empty diff

# Orchestrator dispatch unchanged (FR-020 / SC-025)
git diff main HEAD -- .claude/agents/tachi/orchestrator.md .claude/skills/tachi-orchestration/references/dispatch-rules.md
# Expected: empty diff

# 22-file zero-edit invariant (FR-019 / SC-021)
git diff --name-only main HEAD -- '.claude/agents/tachi/spoofing.md' '.claude/agents/tachi/repudiation.md' '.claude/agents/tachi/info-disclosure.md' '.claude/agents/tachi/denial-of-service.md' '.claude/agents/tachi/privilege-escalation.md' '.claude/agents/tachi/prompt-injection.md' '.claude/agents/tachi/agent-autonomy.md' '.claude/agents/tachi/tool-abuse.md' '.claude/agents/tachi/output-integrity.md' '.claude/agents/tachi/misinformation.md' '.claude/agents/tachi/human-trust-exploitation.md'
# Expected: empty (zero entries — 11 other threat agents unchanged)

# Run enrichment test suite
pytest tests/scripts/test_ml_top_10_coverage_bundle_enrichment.py -v
# Expected: all tests pass (structural-diff + line-count + MAESTRO grep + Pattern Category Disambiguation header + references-array fixtures)
```

### 2. Backward-compatibility verification (Wave 4.1 spot-check + Wave 5.0 full)

**Wave 4.1 (tester) — early-signal byte-identity spot-check on 1–2 baselines**:

```bash
# Spot-check 1: web-app
SOURCE_DATE_EPOCH=1700000000 cd examples/web-app && /tachi.threat-model
SOURCE_DATE_EPOCH=1700000000 /tachi.risk-score
SOURCE_DATE_EPOCH=1700000000 /tachi.compensating-controls
SOURCE_DATE_EPOCH=1700000000 /tachi.infographic all
SOURCE_DATE_EPOCH=1700000000 /tachi.security-report
diff -q examples/web-app/sample-report/security-report.pdf examples/web-app/sample-report/security-report.pdf.baseline
# Expected: identical (no diff)

# Spot-check 2: maestro-reference
# (same flow)
```

**Wave 5.0 (tester) — full byte-identity verification across 6 baselines** (FR-016 / SC-018):

```bash
SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py -k "byte_identity" -v
# Expected: 6/6 baselines pass byte-identical:
#   - examples/web-app/
#   - examples/microservices/
#   - examples/ascii-web-api/
#   - examples/mermaid-agentic-app/
#   - examples/free-text-microservice/
#   - examples/maestro-reference/
# (agentic-app + consumer-agent-app + predictive-ml-app excluded — mutation targets)
```

### 3. New `predictive-ml-app/` regen (Wave 4.0 — FR-014 / SC-019)

```bash
# Pre-conditions: examples/predictive-ml-app/architecture.md authored at Wave 0.0
# (architect + senior-backend-engineer co-authoring, ~150-200 lines, 5 predictive-ML topology indicators)

cd examples/predictive-ml-app
SOURCE_DATE_EPOCH=1700000000 /tachi.threat-model
SOURCE_DATE_EPOCH=1700000000 /tachi.risk-score
SOURCE_DATE_EPOCH=1700000000 /tachi.compensating-controls
SOURCE_DATE_EPOCH=1700000000 /tachi.infographic all
SOURCE_DATE_EPOCH=1700000000 /tachi.security-report

# Verify ≥6 new ML findings (≥1 per host agent)
grep -c "^- id: T-" sample-report/threats.md
grep -c "^- id: D-" sample-report/threats.md
grep -c "^- id: LLM-" sample-report/threats.md
# Expected: at least 1 T-{N} (Cat 10), at least 1 D-{N} (Cat 8/9/10), at least 1 LLM-{N} (Cat 12/13/14)
# Aggregate: ≥6 new ML findings across the 6 closed ML Top 10 items

# Verify references array carries OWASP ML primaries
grep -E "OWASP ML0[1-9]:2023|OWASP ML10:2023" sample-report/threats.md
# Expected: at least 6 distinct OWASP ML primaries cited across all new findings

# Commit baseline
git add sample-report/security-report.pdf.baseline
git commit -m "chore(232): predictive-ml-app initial baseline (excluded from byte-identity loop)"
```

### 4. Coverage Matrix update (Wave 5.3 — FR-023 / SC-025)

```bash
# Apply 6-row transition (single commit per F-3/F-4/F-5 precedent)
$EDITOR _internal/strategy/BLP-01-threat-coverage.md
# §6 Coverage Matrix:
#   ML01: Planned → Covered (closure: F-6 / Feature 232)
#   ML03: Planned → Covered (closure: F-6 / Feature 232)
#   ML04: Planned → Covered (closure: F-6 / Feature 232)
#   ML06: Partial → Covered (closure: F-6 / Feature 232)
#   ML07: Planned → Covered (closure: F-6 / Feature 232)
#   ML08: Planned → Covered (closure: F-6 / Feature 232)
#
# Coverage milestones panel:
#   OWASP ML Top 10:2023: 4/10 → 10/10 Covered
#   OWASP three-framework total: 24/30 → 30/30 Covered

git add _internal/strategy/BLP-01-threat-coverage.md
git commit -m "docs(232): BLP-01 Coverage Matrix six-row transition (F-6 closure)"
```

### 5. ADR-035 Accepted transition (Wave 5.1 — FR-024 / SC-016)

```bash
# Pre-merge: provisional date in Revision History
$EDITOR docs/architecture/02_ADRs/ADR-035-ml-top-10-coverage-bundle.md
# Revision History:
#   2026-04-27: Proposed (Wave 1.0)
#   2026-05-01: Accepted (Wave 5.1; SHA pending post-merge fill)

# Post-merge SHA fill (per FR-026 + git-workflow.md two-step Pre-merge + Post-merge):
git rev-parse HEAD  # capture squash-merge SHA
$EDITOR docs/architecture/02_ADRs/ADR-035-ml-top-10-coverage-bundle.md
# Revision History:
#   2026-05-01: Accepted (squash commit: <SHA>)
git add docs/architecture/02_ADRs/ADR-035-ml-top-10-coverage-bundle.md
git commit -m "docs(232): ADR-035 Accepted — post-merge SHA fill"
```

### 6. PR title verification + release-please gate (FR-024 / SC-026)

```bash
# Pre-merge title verification (per .claude/rules/git-workflow.md)
gh pr view 233 --json title --jq .title
# Expected: "feat(232): ML Top 10 Coverage Bundle"
# If title is non-conventional, retitle BEFORE merge:
#   gh pr edit 233 --title "feat(232): ML Top 10 Coverage Bundle"

# Squash-merge
gh pr merge 233 --squash --auto
git checkout main && git pull

# Post-merge release-please verification (within ~30s of merge)
gh pr list --state open --search "release-please" --limit 3
# Expected: release-please PR opened with v4.x.0 bump
# If empty, push empty release-marker commit:
#   git commit --allow-empty -m "feat(232): ML Top 10 Coverage Bundle — release marker"
#   git push origin main
```

### 7. Delivery retrospective filing (Wave 5.5 — FR-026 / SC-026)

```bash
$EDITOR specs/232-ml-top-10-coverage-bundle/delivery.md
# Retrospective contents (mirrors F-1 / F-2 / F-3 / F-4 / F-5 precedent):
#   - Actual vs estimated effort
#   - Third execution of Heuristic A enrichment branch at three-agent scope
#     lessons (precedent for F-7 5-agent fan-out)
#   - ML06 two-facet split coordination lessons
#   - Byte-identity preservation evidence (FR-019 + FR-016 grep proofs across
#     6 baselines + new predictive-ml-app/ ≥6 findings)
#   - Canonical 8-row mapping table audit-deliverable lessons
#   - ADR-035 Accepted-commit SHA-fill execution
#   - ATLAS catalog gap propagation handling (3 of 6 ATLAS techniques as
#     prose-only at 3x F-5 T1496 precedent scale)
#   - Any deviations from PRD timeline or scope

git add specs/232-ml-top-10-coverage-bundle/delivery.md
git commit -m "docs(232): F-6 delivery retrospective"
```

---

## Acceptance Gate Checklist

Verify each before declaring F-6 delivered:

- [ ] **6 file edits**: tampering.md, data-poisoning.md, model-theft.md, all 3 companions
- [ ] **22 files unchanged**: all other detection-tier agents + companions byte-identical
- [ ] **3 Pattern Category Disambiguation subsections** present (1 per host companion)
- [ ] **Schema unchanged**: `finding.yaml` v1.8, `id.pattern` regex unchanged
- [ ] **6 baselines byte-identical** under `SOURCE_DATE_EPOCH=1700000000`
- [ ] **`predictive-ml-app/` ≥6 new findings** with OWASP ML primaries in `references`
- [ ] **0 MAESTRO references** in all 6 enriched files
- [ ] **ADR-035 Proposed → Accepted** with 8-row mapping table + 9-10 D-numbered decisions
- [ ] **BLP-01 Coverage Matrix** 6-row transition with F-6 closure-feature attribution
- [ ] **PR title `feat(232):` Conventional Commit form** + release-please PR opened
- [ ] **Delivery retrospective** filed at `specs/232-ml-top-10-coverage-bundle/delivery.md`
- [ ] **Triple Triad sign-off** on tasks.md (PM + Architect + Team-Lead)
- [ ] **Test infrastructure updated**: `DETECTION_AGENT_PATHS` 10 → 8; `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` 5 → 7
- [ ] **All 7 fixture findings** valid (Cat 10 T + Cat 8/9/10 D + Cat 12/13/14 LLM)

---

## Failure Modes

| Failure | Diagnosis | Recovery |
|---------|-----------|----------|
| Byte-identity test fails on a baseline | Indicator gate too broad; emits spurious finding on non-ML architecture | Tighten indicator gate language; re-verify on full 6-baseline loop. Buffer day reserved (Mon 2026-05-04). |
| Cat 12 + Cat 13 emit duplicate findings on same prediction-API | Architectural-tells too overlapping | Re-tighten ADR-035 D-5 disjoint-tells language; add explicit boundary in `mitigation` narrative. |
| `predictive-ml-app/` regen yields <6 findings | Architecture missing ≥1 predictive-ML topology indicator | Add missing indicator to architecture.md; re-regen. (~30 min effort.) |
| ADR-035 length >400 lines | Mapping-table verbosity | Split into ADR-035 (decision-tier) + companion `_internal/strategy/F-6-mapping-table.md` (reference-tier) per R7 contingency (unlikely per F-3/F-5 inline-table precedent). |
| R5 (Heuristic A 3-agent emergent issues) triggers | Pattern Category interaction surfaces unexpected cross-agent dependency | Invoke pre-named deferral pair (data-poisoning Cat 10 + model-theft Cat 14, both ML06 facets) per spec OoS-15. Ship 5 of 7 categories closing ML01 + ML07 + ML08 + ML03 + ML04. |
| 3x ATLAS prose-only causes false-negatives in references-array assertions | Test fixture expects T0015 / T0019 / T0031 in `references` but they are absent | Verify fixture excludes catalog-absent ATLAS IDs from `references` and includes them in `mitigation` prose only. |
| release-please PR not opened post-merge | Title prefix or hidden-bump-types regression | Push empty `feat(232): ML Top 10 Coverage Bundle — release marker` commit per F-212 incident precedent (`.claude/rules/git-workflow.md`). |
