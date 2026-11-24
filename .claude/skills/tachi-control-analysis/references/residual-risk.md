---
source_agent: control-analyzer
extracted_from: .claude/agents/tachi/control-analyzer.md
version: 1.0.0
---

# Residual Risk Calculation and Recommendations

This reference defines recommendation generation rules, residual risk computation formulas, and summary statistics for Phase 5 of the control analysis pipeline.

**Who does what.** The control-analyzer agent writes the recommendations: that is everything down to "Residual Risk Calculation". Everything from there on is the renderer's. `scripts/render-compensating-controls.py` computes the reduction factor, the residual score and its band, the totals, the percentages and the shift counts for every open finding, over `scripts/tachi_scoring.py` (`REDUCTION_FACTOR_P0`, `residual_score`, `band`, `reduction_percentage` and `largest_remainder`). The agent calculates none of it and applies none of it, and its part has no key for any of these values. ADR-050 D2 and D5 are the authority where this reference and the code differ.

## Recommendation Generation

For each finding in your batch with `control_status` of `partial` or `missing`, write a remediation recommendation, as that finding's `recommendation_body`. A finding with `control_status` of `found` receives none: its `recommendation_body` is `null`.

**Order**: Write the recommendations in any order. The renderer orders Section 4 by inherent score, highest first and then by finding ID, and it groups the blocks by inherent band.

### Recommendation Structure

Each recommendation must contain four components, and `recommendation_body` holds them as four keys, each once and in this order:

1. **What to implement** (`**What to Implement**:`) -- The specific control mechanism to add or harden
2. **Where to implement** (`**Where to Implement**:`) -- The suggested file, module, or architectural location
3. **Reference patterns** (`**Reference Patterns**:`) -- Common libraries, frameworks, or implementation patterns
4. **Effort estimate** (`**Effort Estimate**:`) -- The expected implementation effort level, which starts with `Low`, `Medium` or `High`

### Recommendation Rules by Control Status

**For `missing` threats** (no control detected):

Generate a full implementation recommendation:

- **What**: Describe the specific control type to implement based on the threat's STRIDE category and the missing control category from Phase 4. Be specific: "Add JWT-based authentication middleware" not "Add authentication."
- **Where**: Suggest an implementation location based on Phase 2 codebase discovery. If the component has an identifiable middleware directory, suggest placing the control there. If no obvious location exists, suggest the most architecturally appropriate location (e.g., "Create `src/middleware/rate-limiter.ts`" or "Add validation to `src/routes/api.ts`").
- **Reference patterns**: List 1-3 commonly used libraries or patterns for this control category. Draw from the library lists in the Phase 3 category definitions. Prefer libraries that match the target codebase's technology stack (e.g., if the codebase uses Express, recommend `express-rate-limit` not `flask-limiter`).
- **Effort**: Assign based on implementation complexity:
  - **Low**: Configuration change or enabling an existing feature (e.g., adding `SameSite=Strict` to cookie config, enabling HSTS header)
  - **Medium**: New middleware, function, or module (e.g., adding rate limiting middleware, implementing input validation schemas, adding structured logging)
  - **High**: Architectural change or cross-cutting concern (e.g., implementing RBAC across all endpoints, adding end-to-end encryption, redesigning authentication flow)

**For `partial` threats** (control exists but incomplete):

Generate a hardening recommendation that focuses on extending the existing control:

- **What**: Describe what is missing from the existing control. Reference the specific gap identified during Phase 4 classification (e.g., "Extend input validation to cover the `/admin` and `/webhook` endpoints currently lacking schema validation" or "Add rate limiting to the WebSocket handler -- HTTP endpoints are protected but WebSocket connections are not").
- **Where**: Point to the existing control's location (from Phase 3 evidence) and the locations that need coverage extension.
- **Reference patterns**: If the existing control uses a specific library, recommend extending with the same library. If the gap requires a different approach, explain why.
- **Effort**: Typically **Low** or **Medium** since the foundational control exists. Only assign **High** if the gap requires significant rearchitecting of the existing control.

### Recommendation Text Format

Write each recommendation as the four keys of `recommendation_body`, one to a line, each with actionable guidance. The recommendation should be self-contained -- a developer should be able to read it and begin implementation without referring back to other sections. Write no heading and no table line, and keep the whole body within the part contract's limit of 2,000 characters.

**Template for missing controls**:
```
**What to Implement**: Implement {control_type} for {component}. {What to build and why it addresses the threat}. This control would address {threat_description_brief}.
**Where to Implement**: `{file_path}`
**Reference Patterns**: {library_1}, {library_2}
**Effort Estimate**: {Low, Medium or High}
```

**Template for partial controls**:
```
**What to Implement**: Harden existing {control_type}. {What is missing and how to extend}. The current implementation covers {covered_scope} but leaves {uncovered_scope} unprotected.
**Where to Implement**: `{existing_file}:{line}`, and {specific files or endpoints needing coverage}
**Reference Patterns**: {the library the existing control uses, or the different approach and why}
**Effort Estimate**: {Low, Medium or High}
```

### Effort Estimate Calibration

| Effort | Typical Scope | Examples |
|--------|--------------|---------|
| **Low** | Configuration change, single-line addition, enabling a built-in feature | Add `SameSite=Strict` to session cookie; enable `helmet()` HSTS; add `--require-auth` flag to existing CLI |
| **Medium** | New file, new middleware, new validation schema, new logging integration | Create rate limiter middleware; add Zod schemas for API endpoints; integrate structured logging library; add CSRF token middleware |
| **High** | Cross-cutting architectural change, new subsystem, redesign of existing flow | Implement RBAC/ABAC authorization system; add field-level encryption across data layer; redesign authentication from session-based to JWT; add comprehensive audit trail system |

### Recommendation Completeness Check

You run no check of your own. The part validator enforces the pairing: `recommendation_body` is required for a `partial` or `missing` finding and `null` for a `found` one, and a part that breaks it is rejected, so its batch is re-dispatched.

## Residual Risk Calculation

**The renderer's section.** The renderer computes the residual risk of every open finding, whatever its `control_status`, and whether or not its control result was carried forward from a baseline. The inputs are this run's scored input (the inherent score) and the finding's `control_status`. A value that an agent or a baseline file stored never stands in for a computed one.

### Reduction Factor Assignment

The renderer derives each finding's `reduction_factor` from its `control_status`, by the P0 binary reduction model. The factors are `tachi_scoring.REDUCTION_FACTOR_P0`, and a drift test keeps them equal to `reduction_factor_p0` in `schemas/compensating-controls.yaml`:

| `control_status` | `reduction_factor` | Interpretation |
|------------------|-------------------|----------------|
| `found` | 0.50 | Control detected with High/Medium confidence; risk reduced by 50% |
| `partial` | 0.25 | Control detected with gaps or Low confidence; risk reduced by 25% |
| `missing` | 0.00 | No control detected; risk unchanged |

**Derived, so never corrected**: no value from a part or a baseline can disagree with this table, and no step corrects a factor or warns about one. The renderer derives the P0 `control_effectiveness` from the same status, as `evidence-criteria.md` states.

### Residual Score Computation

For each finding, the renderer calculates:

```
residual_score = composite_score * (1 - reduction_factor)
```

**Range**: The result needs no clamping. `tachi_scoring.residual_score` takes a stored inherent score (0.0 to 10.0, already on the 0.1 grid) and a factor from 0 to 1, and refuses any other input, so the result stays within 0.0 to 10.0.

**Precision**: The renderer rounds `residual_score` half up to one decimal place with `tachi_scoring.q1`, matching the precision of `composite_score` from the upstream risk scorer. It never uses Python's `round()` on a float, which gives 4.5 for 4.55: the exact product of 9.1 and 0.50 is 4.55, and half up makes it 4.6.

**Worked examples**:

| Threat | composite_score | control_status | reduction_factor | Calculation | residual_score |
|--------|----------------|----------------|-----------------|-------------|---------------|
| S-1 | 7.8 | found | 0.50 | 7.8 * (1 - 0.50) = 3.9 | 3.9 |
| T-2 | 6.5 | partial | 0.25 | 6.5 * (1 - 0.25) = 4.875 | 4.9 |
| D-3 | 8.2 | missing | 0.00 | 8.2 * (1 - 0.00) = 8.2 | 8.2 |
| I-4 | 9.1 | found | 0.50 | 9.1 * (1 - 0.50) = 4.55 | 4.6 |

### Residual Severity Band Mapping

The renderer maps each `residual_score` to a `residual_severity_band` with `tachi_scoring.band`, using the same thresholds as the upstream risk scorer (from `schemas/risk-scoring.yaml`). The minimums are inclusive, and `band` takes only a score already rounded to one decimal, so a residual is always rounded before it is banded. The inherent severity of each finding is `band` of its inherent score, by the same rule.

| Severity Band | Score Range |
|--------------|-------------|
| **Critical** | >= 9.0 |
| **High** | 7.0 - 8.9 |
| **Medium** | 4.0 - 6.9 |
| **Low** | < 4.0 |

**Severity shift tracking**: When `residual_severity_band` differs from the original `severity_band` (inherent), this represents a severity downgrade due to compensating controls. The renderer counts these shifts for the summary statistics, and it counts a finding whose band holds under "No Shift".

### Summary Statistics

After computing residual risk for all open findings, the renderer calculates the aggregate statistics. Each total is the exact decimal sum of the stored one-decimal scores in the rows, never a float sum, so the totals equal the sums of the rows by construction. Section 1, Section 2's Summary Statistics and Section 5 of `compensating-controls.md` carry them.

1. **Total inherent risk**: Sum of all `composite_score` values across all open findings
2. **Total residual risk**: Sum of all `residual_score` values across all open findings
3. **Risk delta**: `total_inherent_risk - total_residual_risk`
4. **Overall reduction percentage**: `(risk_delta / total_inherent_risk) * 100`, rounded half up to one decimal place (`tachi_scoring.reduction_percentage`, which gives 0.0 for a zero inherent total)
5. **Severity distribution (inherent)**: Count of findings per severity band before controls
6. **Severity distribution (residual)**: Count of findings per severity band after controls
7. **Severity shifts**: Count of findings that moved to a lower severity band due to controls
8. **Percentages of a distribution** (the coverage split and the residual severity split): whole numbers that sum to exactly 100, by the largest-remainder method (`tachi_scoring.largest_remainder`), with ties going to the label that sorts first

The values below are an illustration of the quantities, with counts that agree with each other. The renderer writes them in the template's tables.

```yaml
residual_risk_summary:
  total_inherent_risk: 234.5
  total_residual_risk: 178.2
  risk_delta: 56.3
  overall_reduction_percentage: 24.0
  inherent_distribution:
    critical: 3
    high: 12
    medium: 15
    low: 4
  residual_distribution:
    critical: 1
    high: 8
    medium: 16
    low: 9
  severity_shifts:
    critical_to_high: 2
    critical_to_medium: 0
    critical_to_low: 0
    high_to_medium: 4
    high_to_low: 2
    medium_to_low: 3
    total_shifts: 11
```

### Residual Risk Completeness Check

The renderer checks completeness from the files it wrote, before it replaces a canonical file: every open finding of the scored input has exactly one row in Section 2 and one SARIF result, with a residual score and a residual band. A finding that lacks a row or a result, or that has two, fails the render with a diagnostic that names the finding. Nothing is reported as complete before the check passes.

### Arithmetic Verification

The arithmetic is the renderer's own, so there is no agent arithmetic to verify: each residual is `tachi_scoring.residual_score` of the inherent score and the derived factor, and each total is a sum of the rows. The one place an agent writes into a computed column is Section 2's `matrix_row`, whose computed cells the renderer fills by column position, overwriting any other content and counting each overwrite in the stage record.
