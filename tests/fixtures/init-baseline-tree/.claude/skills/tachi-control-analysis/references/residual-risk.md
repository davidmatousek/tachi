---
source_agent: control-analyzer
extracted_from: .claude/agents/tachi/control-analyzer.md
version: 1.0.0
---

# Residual Risk Calculation and Recommendations

This reference defines recommendation generation rules, residual risk computation formulas, and summary statistics for Phase 5 of the control analysis pipeline.

## Recommendation Generation

For each threat in the classified finding set with `control_status` of `partial` or `missing`, generate a remediation recommendation. Threats with `control_status` of `found` do not receive recommendations -- set `recommendation: null` and `effort_estimate: null` for these.

**Processing order**: Sort all `partial` and `missing` threats by `composite_score` descending (highest risk first). Generate recommendations in this order so the output is already priority-sorted.

### Recommendation Structure

Each recommendation must contain four components:

1. **What to implement** -- The specific control mechanism to add or harden
2. **Where to implement** -- The suggested file, module, or architectural location
3. **Reference patterns** -- Common libraries, frameworks, or implementation patterns
4. **Effort estimate** -- The expected implementation effort level

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

Write each recommendation as a single paragraph of actionable guidance. The recommendation should be self-contained -- a developer should be able to read it and begin implementation without referring back to other sections.

**Template for missing controls**:
```
Implement {control_type} for {component}. {What to build and why it addresses the threat}. Suggested location: `{file_path}`. Reference implementations: {library_1}, {library_2}. This control would address {threat_description_brief}.
```

**Template for partial controls**:
```
Harden existing {control_type} in `{existing_file}:{line}`. {What is missing and how to extend}. {Specific files or endpoints needing coverage}. The current implementation covers {covered_scope} but leaves {uncovered_scope} unprotected.
```

### Effort Estimate Calibration

| Effort | Typical Scope | Examples |
|--------|--------------|---------|
| **Low** | Configuration change, single-line addition, enabling a built-in feature | Add `SameSite=Strict` to session cookie; enable `helmet()` HSTS; add `--require-auth` flag to existing CLI |
| **Medium** | New file, new middleware, new validation schema, new logging integration | Create rate limiter middleware; add Zod schemas for API endpoints; integrate structured logging library; add CSRF token middleware |
| **High** | Cross-cutting architectural change, new subsystem, redesign of existing flow | Implement RBAC/ABAC authorization system; add field-level encryption across data layer; redesign authentication from session-based to JWT; add comprehensive audit trail system |

### Recommendation Completeness Check

After recommendation generation, verify that every threat with `control_status` of `partial` or `missing` has a non-null `recommendation` and `effort_estimate`. Every threat with `control_status` of `found` has null values for both. If any violation is found, halt with: **"Recommendation completeness check failed: {count} threats have inconsistent recommendation/status pairing. IDs: {id_list}"**

## Residual Risk Calculation

For every threat in the classified finding set (regardless of `control_status`), calculate the residual risk score that reflects the risk remaining after accounting for detected compensating controls.

### Reduction Factor Assignment

The `reduction_factor` is determined by `control_status` and was already assigned during Phase 4 classification. Verify the assignment is consistent with the P0 binary reduction model:

| `control_status` | `reduction_factor` | Interpretation |
|------------------|-------------------|----------------|
| `found` | 0.50 | Control detected with High/Medium confidence; risk reduced by 50% |
| `partial` | 0.25 | Control detected with gaps or Low confidence; risk reduced by 25% |
| `missing` | 0.00 | No control detected; risk unchanged |

**Validation**: If any threat's `reduction_factor` does not match its `control_status` per the table above, correct it and emit a warning: **"Reduction factor corrected for {id}: was {old_value}, expected {expected_value} for status '{control_status}'"**

### Residual Score Computation

For each threat, calculate:

```
residual_score = composite_score * (1 - reduction_factor)
```

**Clamping**: Clamp the result to the range [0.0, 10.0]:
- If `residual_score` < 0.0, set to 0.0
- If `residual_score` > 10.0, set to 10.0

**Precision**: Round `residual_score` to one decimal place (matching the precision of `composite_score` from the upstream risk scorer).

**Worked examples**:

| Threat | composite_score | control_status | reduction_factor | Calculation | residual_score |
|--------|----------------|----------------|-----------------|-------------|---------------|
| S-1 | 7.8 | found | 0.50 | 7.8 * (1 - 0.50) = 3.9 | 3.9 |
| T-2 | 6.5 | partial | 0.25 | 6.5 * (1 - 0.25) = 4.875 | 4.9 |
| D-3 | 8.2 | missing | 0.00 | 8.2 * (1 - 0.00) = 8.2 | 8.2 |
| I-4 | 9.1 | found | 0.50 | 9.1 * (1 - 0.50) = 4.55 | 4.6 |

### Residual Severity Band Mapping

Map each `residual_score` to a `residual_severity_band` using the same thresholds as the upstream risk scorer (from `schemas/risk-scoring.yaml`):

| Severity Band | Score Range |
|--------------|-------------|
| **Critical** | >= 9.0 |
| **High** | 7.0 - 8.9 |
| **Medium** | 4.0 - 6.9 |
| **Low** | < 4.0 |

**Severity shift tracking**: When `residual_severity_band` differs from the original `severity_band` (inherent), this represents a severity downgrade due to compensating controls. Track these shifts for the summary statistics.

### Summary Statistics

After computing residual risk for all threats, calculate aggregate statistics:

1. **Total inherent risk**: Sum of all `composite_score` values across all threats
2. **Total residual risk**: Sum of all `residual_score` values across all threats
3. **Risk delta**: `total_inherent_risk - total_residual_risk`
4. **Overall reduction percentage**: `(risk_delta / total_inherent_risk) * 100`, rounded to one decimal place
5. **Severity distribution (inherent)**: Count of threats per severity band before controls
6. **Severity distribution (residual)**: Count of threats per severity band after controls
7. **Severity shifts**: Count of threats that moved to a lower severity band due to controls

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
    medium: 17
    low: 8
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

After residual risk calculation, verify that every threat has a non-null `residual_score` and `residual_severity_band`. The count of threats with residual risk must equal the total finding count from Phase 1. If any finding is missing residual risk, halt with: **"Residual risk incomplete: {missing_count} findings lack residual scores. IDs: {id_list}"**

### Arithmetic Verification

For each threat, verify: `residual_score == round(composite_score * (1 - reduction_factor), 1)` (after clamping). If any value is inconsistent, recalculate and emit a warning: **"Residual score recalculated for {id}: was {old_value}, corrected to {correct_value}"**
