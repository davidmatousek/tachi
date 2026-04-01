# Quickstart: Baseline-Aware Pipeline Validation

## Prerequisites

- tachi repository cloned with feature branch `074-baseline-aware-pipeline`
- Claude Code CLI available
- Example architecture file (e.g., `examples/second-brain-mcp/architecture.md`)

## Test 1: First Run (Stateless Mode)

Verify backward compatibility — first run without baseline produces identical output to current behavior.

```bash
# Run threat model on example architecture (no baseline)
/threat-model examples/second-brain-mcp/architecture.md

# Verify output has no baseline frontmatter
# All findings should be annotated [NEW]
# Output should match current stateless format
```

**Expected**: Output identical to current behavior. All findings annotated `[NEW]`. No `baseline:` block in frontmatter.

## Test 2: Stable Re-Scan (Zero Drift)

Verify finding ID and score stability on unchanged codebase.

```bash
# Run 1: Generate baseline
/threat-model examples/second-brain-mcp/architecture.md
# Save output as baseline

# Run 2: Re-run with baseline
/threat-model examples/second-brain-mcp/architecture.md --baseline threats.md

# Compare: IDs, scores, counts must be identical
# All findings should be annotated [UNCHANGED]
```

**Expected**: 100% ID match, zero score drift, zero count drift. All findings `[UNCHANGED]`.

## Test 3: Remediation Verification

Verify resolved findings are correctly detected.

```bash
# Modify architecture to remove a component targeted by finding S-3
# Re-run with baseline
/threat-model modified-architecture.md --baseline threats.md

# Verify S-3 is marked [RESOLVED] with original ID preserved
```

**Expected**: S-3 annotated `[RESOLVED]` with original ID, description, and last-known score.

## Test 4: New Threat Discovery

Verify new findings are discovered without anchoring bias.

```bash
# Add a new LLM Process component to architecture
# Re-run with baseline
/threat-model expanded-architecture.md --baseline threats.md

# Verify new findings appear with [NEW] and sequential IDs
# Existing findings retain baseline IDs
```

**Expected**: New findings annotated `[NEW]` with IDs sequential after highest existing per category. No duplicates.

## Test 5: Coverage Gate

Verify coverage gate detects missing threat categories.

```bash
# Run pipeline on architecture with LLM Process component
# Verify coverage gate checks for: prompt injection, data poisoning, model theft
# If any category missing, targeted re-analysis should trigger
```

**Expected**: Coverage gate passes when all required categories evaluated. Flags gaps and triggers targeted re-analysis.

## Test 6: Risk Score Inheritance

Verify scores carry forward correctly.

```bash
# Run /risk-score with baseline risk-scores.md
/risk-score threats.md --baseline risk-scores.md

# UNCHANGED findings should have score_source: "inherited"
# NEW findings should have score_source: "fresh" with bounded CVSS
```

**Expected**: UNCHANGED scores identical to baseline. NEW scores within ±1.0 of category defaults.

## Test 7: Compensating Controls Carry-Forward

Verify control status carries forward correctly.

```bash
# Run /compensating-controls with baseline
/compensating-controls risk-scores.md --baseline compensating-controls.md

# UNCHANGED findings should have control_carry_forward: true
# Only NEW/UPDATED findings re-scanned
```

**Expected**: UNCHANGED controls identical to baseline. Only changed findings re-scanned.

## Validation Checklist

- [ ] First run without baseline works identically to current behavior
- [ ] Re-scan on unchanged codebase produces zero drift (IDs, scores, counts)
- [ ] Resolved findings correctly marked with original ID preserved
- [ ] New findings discovered with sequential IDs and bounded scores
- [ ] Coverage gate detects missing categories and triggers re-analysis
- [ ] Risk scores inherited for unchanged findings
- [ ] Compensating controls carry forward for unchanged findings
- [ ] SARIF output includes baselineState and baselineRunId
- [ ] Delta annotations present on every finding
