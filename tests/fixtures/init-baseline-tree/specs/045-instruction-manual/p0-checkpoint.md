# P0 Checkpoint Review: Feature 045 — End-to-End tachi Instruction Manual

**Reviewer**: Architect
**Date**: 2026-03-28
**File Reviewed**: `docs/guides/prompts/GUIDE_PROMPT.md`
**Scope**: Waves 1-2 (13/31 tasks) — Prompt specification updates for post-pipeline commands

---

## STATUS: APPROVED_WITH_CONCERNS

**Summary**: The prompt specification updates are substantially correct and well-structured. The post-pipeline enrichment commands are documented with accurate invocation patterns, flag handling, input/output specifications, and pipeline data flow. Three factual inaccuracies were found against authoritative source specifications, all in numerical parameters. These should be corrected before the guide is generated from this prompt.

---

## Review Criteria Results

### 1. Technical Accuracy

**Composite Score Weights (CRITICAL)**: The GUIDE_PROMPT.md states the composite formula as:

```
(CVSS * 0.3) + (Exploitability * 0.25) + (Scalability * 0.2) + (Reachability * 0.25)
```

The authoritative source (`adapters/claude-code/agents/risk-scorer.md`, line 684) defines the formula as:

```
Composite = (0.35 x CVSS Base) + (0.30 x Exploitability) + (0.15 x Scalability) + (0.20 x Reachability)
```

The weights are **0.35/0.30/0.15/0.20**, not 0.30/0.25/0.20/0.25. This is confirmed by the `composite-weights` SARIF property which stores `"0.35/0.30/0.15/0.20"` (risk-scorer.md line 1315). All four weights are incorrect in the prompt specification.

**Location in GUIDE_PROMPT.md**: Line 294
**Severity**: High — the composite formula is a core technical claim that the generated guide will reproduce. Incorrect weights will mislead developers interpreting risk scores.

---

**Severity Band Thresholds (MODERATE)**: The GUIDE_PROMPT.md states:

```
Critical (>= 8.0), High (6.0-7.9), Medium (4.0-5.9), Low (< 4.0)
```

The authoritative source (`adapters/claude-code/agents/risk-scorer.md`, lines 712-715) defines:

```
Critical: 9.0 - 10.0 (Score >= 9.0)
High:     7.0 - 8.9  (Score >= 7.0 and < 9.0)
Medium:   4.0 - 6.9  (Score >= 4.0 and < 7.0)
Low:      0.0 - 3.9  (Score < 4.0)
```

The Critical threshold is **>= 9.0** not >= 8.0. The High band is **7.0-8.9** not 6.0-7.9. The Medium band is **4.0-6.9** not 4.0-5.9. Only the Low band threshold (< 4.0) is correct.

**Location in GUIDE_PROMPT.md**: Line 294
**Severity**: High — severity bands determine remediation urgency. Incorrect thresholds will cause developers to misclassify risk levels.

---

**Residual Risk Formula (MODERATE)**: The GUIDE_PROMPT.md states:

```
Residual Risk = Inherent Score x (1 - Mitigation Factor)
where Mitigation Factor is 0.0 (no control) to 0.8 (full control)
```

The authoritative source (`adapters/claude-code/agents/control-analyzer.md`, lines 961-965) defines:

```
reduction_factor for "found" = 0.50
reduction_factor for "partial" = 0.25
reduction_factor for "missing" = 0.00
```

The maximum reduction factor is **0.50** (for a fully detected control), not 0.8. Additionally, the authoritative source uses the term "reduction_factor" rather than "Mitigation Factor", though this is a less critical naming concern.

The worked example in the GUIDE_PROMPT.md states: "A finding with composite score 8.5 and a full control has residual risk of 1.7." This math assumes 0.8: `8.5 * (1 - 0.8) = 1.7`. With the correct factor of 0.50, the residual risk would be: `8.5 * (1 - 0.50) = 4.25`.

**Location in GUIDE_PROMPT.md**: Line 342
**Severity**: High — the example demonstrates the formula with the wrong factor, reinforcing the error.

---

**Governance Field Disposition Values (MINOR)**: The GUIDE_PROMPT.md lists disposition values as:

```
Open, In Progress, Accepted, Mitigated
```

The authoritative source (`adapters/claude-code/agents/risk-scorer.md`, lines 814-819) defines the enum as:

```
Mitigate, Review, Accept, Transfer
```

The GUIDE_PROMPT.md uses different terminology. "Open" and "In Progress" are not defined values in the schema. "Mitigated" is not the same as "Mitigate" (the schema uses the imperative form). "Accepted" is not the same as "Accept".

**Location in GUIDE_PROMPT.md**: Line 303
**Severity**: Moderate — the disposition values will appear in generated examples and should match the actual schema.

---

### 2. Completeness

**PASS**: All four post-pipeline commands are covered:
- `/threat-model` (pre-existing, referenced as pipeline source)
- `/risk-score` — Section covers invocation, flags (`--output-dir`), inputs, outputs, 4 scoring dimensions, composite formula, governance fields
- `/compensating-controls` — Section covers invocation, flags (`--target`, `--output-dir`), inputs, outputs, control classification (3 statuses), residual risk formula, evidence format
- `/infographic` — Section covers invocation, flags (`--template`, `--output-dir`), auto-detection, template options (baseball-card, system-architecture, all, corporate-white alias), Gemini API requirement

**PASS**: Guide Structure Specification updated with Sections 4b-4e for post-pipeline enrichment.

**PASS**: OpenClaw worked example extended with Steps 7-9 (later renumbered to 11-13) for post-pipeline commands.

### 3. Data Flow Accuracy

**PASS**: The pipeline diagram (lines 242-253) correctly shows:
```
/threat-model -> /risk-score -> /compensating-controls -> /infographic
```

The dependencies are accurately represented:
- `/risk-score` consumes `threats.md` (correct per risk-score.md command spec)
- `/compensating-controls` consumes `risk-scores.md + target codebase` (correct per compensating-controls.md)
- `/infographic` auto-detects richest source, preferring `risk-scores.md > threats.md` (correct per infographic.md)

The "when to run" guidance (lines 256-258) accurately characterizes each command as recommended vs. optional.

### 4. Factual Corrections

**Agent count**: Correctly updated to **15** (line 102). Verified: 15 `.md` files exist in `adapters/claude-code/agents/`.

**Template names**: Correctly updated to `baseball-card` and `system-architecture` (lines 188-201, 371-377, 432). The `corporate-white` alias is correctly documented as resolving to `baseball-card`, matching the infographic command spec (line 18-23 of infographic.md).

**Output artifacts**: Correctly expanded from 6 to 12 items (lines 145-228), covering all pipeline outputs including risk-scores.md, risk-scores.sarif, compensating-controls.md, compensating-controls.sarif.

**Installation commands**: Correctly include all 4 command files and the source paths match actual file locations (lines 417-427). The `compensating-controls.md` correctly references `.claude/commands/` rather than `adapters/claude-code/commands/`.

---

## Findings Summary

| # | Severity | Category | Finding | Location |
|---|----------|----------|---------|----------|
| F-1 | HIGH | Technical Accuracy | Composite score weights are 0.35/0.30/0.15/0.20, not 0.30/0.25/0.20/0.25 | Line 294 |
| F-2 | HIGH | Technical Accuracy | Severity band thresholds incorrect: Critical >= 9.0, High 7.0-8.9, Medium 4.0-6.9 | Line 294 |
| F-3 | HIGH | Technical Accuracy | Maximum reduction factor is 0.50, not 0.8; worked example math is wrong | Line 342 |
| F-4 | MODERATE | Technical Accuracy | Disposition values should be Mitigate/Review/Accept/Transfer, not Open/In Progress/Accepted/Mitigated | Line 303 |

---

## Recommended Corrections

### F-1: Fix composite score weights

**Current** (line 294):
```
(CVSS * 0.3) + (Exploitability * 0.25) + (Scalability * 0.2) + (Reachability * 0.25)
```

**Correct**:
```
(CVSS * 0.35) + (Exploitability * 0.30) + (Scalability * 0.15) + (Reachability * 0.20)
```

### F-2: Fix severity band thresholds

**Current** (line 294):
```
Critical (>= 8.0), High (6.0-7.9), Medium (4.0-5.9), Low (< 4.0)
```

**Correct**:
```
Critical (>= 9.0), High (7.0-8.9), Medium (4.0-6.9), Low (< 4.0)
```

### F-3: Fix residual risk formula parameters and worked example

**Current** (line 342):
```
Residual Risk = Inherent Score x (1 - Mitigation Factor) where Mitigation Factor is 0.0 (no control) to 0.8 (full control). A finding with composite score 8.5 and a full control has residual risk of 1.7.
```

**Correct**:
```
Residual Risk = Composite Score x (1 - Reduction Factor) where Reduction Factor is 0.00 (no control), 0.25 (partial control), or 0.50 (full control). A finding with composite score 8.5 and a full control has residual risk of 4.3.
```

### F-4: Fix governance disposition values

**Current** (line 303):
```
Open, In Progress, Accepted, Mitigated
```

**Correct**:
```
Mitigate, Review, Accept, Transfer
```

With note: "Mitigate and Review are assigned automatically based on severity band. Accept and Transfer are human-override values assigned during triage."

---

## Conclusion

The P0 checkpoint demonstrates strong progress. The prompt specification structure is sound, the pipeline data flow is correct, and the command coverage is complete. The four findings above are all numerical/terminological accuracy issues that are straightforward to fix. None require structural rework. Recommend correcting these before proceeding to Wave 3 (guide generation), as these values will propagate into the generated guide content.
