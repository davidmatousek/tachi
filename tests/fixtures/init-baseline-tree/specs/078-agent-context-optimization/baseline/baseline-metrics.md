# Baseline Metrics - Feature 078 Regression Reference

**Source**: `examples/agentic-app/test-output/2026-03-25T12-53-57/`
**Captured**: 2026-04-01
**Purpose**: Regression comparison baseline for agent context optimization (Feature 078)

---

## threats.md Metrics

### Finding Count by STRIDE+AI Category

| Category | Prefix | Count | Finding IDs |
|----------|--------|-------|-------------|
| Spoofing | S | 5 | S-1, S-2, S-3, S-4, S-5 |
| Tampering | T | 6 | T-1, T-2, T-3, T-4, T-5, T-6 |
| Repudiation | R | 5 | R-1, R-2, R-3, R-4, R-5 |
| Information Disclosure | I | 5 | I-1, I-2, I-3, I-4, I-5 |
| Denial of Service | D | 5 | D-1, D-2, D-3, D-4, D-5 |
| Elevation of Privilege | E | 4 | E-1, E-2, E-3, E-4 |
| Agentic Threats | AG | 4 | AG-1, AG-2, AG-3, AG-4 |
| LLM Threats | LLM | 4 | LLM-1, LLM-2, LLM-3, LLM-4 |
| **Total (raw)** | | **38** | |

### Severity Distribution

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Critical | 7 | 20.6% |
| High | 15 | 44.1% |
| Medium | 10 | 29.4% |
| Low | 1 | 2.9% |
| Note | 0 | 0.0% |
| **Total (deduplicated)** | **33** | **100%** |

Note: 38 raw findings deduplicate to 33 due to 5 correlation groups (each merging 2 correlated findings into 1 unique threat).

### Section Presence

All 7 standard sections present:

| # | Section | Present |
|---|---------|---------|
| 1 | System Overview | Yes |
| 2 | Trust Boundaries | Yes |
| 3 | STRIDE Tables | Yes |
| 4 | AI Threat Tables | Yes |
| 5 | Coverage Matrix | Yes |
| 6 | Risk Summary | Yes |
| 7 | Recommended Actions | Yes |

### Correlation Groups

| Group | Correlated Findings | Component | Risk Level |
|-------|---------------------|-----------|------------|
| CG-1 | T-2, LLM-3 | LLM Agent Orchestrator | High |
| CG-2 | E-1, AG-1 | LLM Agent Orchestrator | Critical |
| CG-3 | I-1, LLM-1 | LLM Agent Orchestrator | Critical |
| CG-4 | R-4, AG-3 | MCP Tool Server | Critical |
| CG-5 | D-2, AG-4 | MCP Tool Server | High |

**Total correlation groups**: 5 (merging 10 individual findings)

---

## threats.sarif Metrics

| Metric | Value |
|--------|-------|
| SARIF version | 2.1.0 |
| Run count | 1 |
| Total results | 33 |
| Rule definitions | 8 |

### Results by Rule

| Rule ID | Count |
|---------|-------|
| tachi/stride/spoofing | 5 |
| tachi/stride/tampering | 6 |
| tachi/stride/repudiation | 5 |
| tachi/stride/information-disclosure | 5 |
| tachi/stride/denial-of-service | 5 |
| tachi/stride/elevation-of-privilege | 4 |
| tachi/ai/agentic-threats | 1 |
| tachi/ai/llm-threats | 2 |
| **Total** | **33** |

### Results by SARIF Level

| Level | Count | Maps to Severity |
|-------|-------|------------------|
| error | 22 | High / Critical |
| warning | 10 | Medium |
| note | 1 | Low |
| **Total** | **33** | |

Note: The SARIF contains 33 results (deduplicated). Five results carry `correlationGroup` markers in `partialFingerprints` (T-2/CG-1, E-1/CG-2, I-1/CG-3, R-4/CG-4, D-2/CG-5). The correlated partners (LLM-3, AG-1, LLM-1, AG-3, AG-4) are referenced via `relatedLocations` on the marked results but do not appear as separate SARIF result entries, explaining the 33 vs 38 raw count difference.

---

## Additional Baseline Files (Phase 4 Regression)

The following files were copied from `examples/agentic-app/sample-report/` for Phase 4 regression testing (T051-T053):

| File | Source | Size |
|------|--------|------|
| risk-scores.md | sample-report/ | 75,837 bytes |
| risk-scores.sarif | sample-report/ | 69,657 bytes |
| compensating-controls.md | sample-report/ | 17,344 bytes |

---

## Regression Comparison Rules

When comparing post-optimization output against this baseline:

1. **Finding count**: New output must produce >= 38 raw findings across the same 8 categories
2. **Severity distribution**: Critical + High count must be >= 22 (no severity downgrade)
3. **Section completeness**: All 7 sections must be present
4. **Correlation groups**: Must produce >= 5 correlation groups
5. **SARIF compliance**: Must produce valid SARIF 2.1.0 with >= 33 results and 1 run
