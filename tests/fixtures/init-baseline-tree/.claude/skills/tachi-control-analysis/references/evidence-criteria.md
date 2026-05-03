---
source_agent: control-analyzer
extracted_from: .claude/agents/tachi/control-analyzer.md
version: 1.0.0
---

# Evidence Criteria and Effectiveness Classification

This reference defines evidence collection rules, confidence level assignments, and the Phase 4 classification rules that map detected controls to threats.

## Evidence Collection

For each candidate that survives Phase B semantic analysis, collect a `control_evidence` entry conforming to the `control_evidence` item schema in `schemas/compensating-controls.yaml`:

```yaml
control_evidence:
  - file: "src/middleware/auth.ts"        # Relative path from target root
    line: 42                               # Line number of the control
    snippet: |                             # Max 5 lines showing the control
      const authMiddleware = (req, res, next) => {
        const token = req.headers.authorization?.split(' ')[1];
        if (!token) return res.status(401).json({ error: 'Unauthorized' });
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded;
```

### Snippet Selection Rules

1. **Length**: Maximum 5 lines of code. Never capture entire files or entire functions.
2. **Representativeness**: Select the lines that most clearly demonstrate the control mechanism in action. Prefer:
   - The function/block declaration line + core implementation logic
   - Middleware registration if it appears within 5 lines of the implementation
   - The verification/enforcement call, not just the setup or configuration
3. **Self-contained**: The snippet should be understandable without additional context. Include enough surrounding code to show what the control does and what it protects.
4. **Deduplication**: If the same control implementation is applied to multiple routes (e.g., the same auth middleware on 10 endpoints), collect evidence from the middleware definition only -- do not duplicate evidence for each route.
5. **Multiple controls per category**: If a component has multiple distinct controls in the same category (e.g., JWT auth for API routes AND session auth for web routes), collect separate evidence entries for each.

**File path format**: Always use forward slashes and paths relative to the target codebase root (the path provided as input). Never use absolute paths in evidence.

**Line number accuracy**: The `line` field must reference the first line of the captured snippet within the original file. When a file was truncated during Phase 2 large file handling, map the truncated position back to the original file line number.

## Confidence Levels

Assign a detection confidence to each detected control based on the strength of evidence from Phase A and Phase B:

| Confidence | Criteria | Example |
|------------|----------|---------|
| **High** | Explicit security library or framework usage confirmed with clear middleware registration or guard application. Both Phase A pattern match and Phase B semantic analysis confirm the control is active and enforced. | `app.use(helmet())` registered at application level; `jwt.verify()` inside a middleware that is applied to protected routes. |
| **Medium** | Security-relevant code patterns detected without standard library usage, OR a recognized library is imported and used but its registration or wiring to routes cannot be confirmed within the scanned file set. Phase A matches, Phase B confirms implementation exists but cannot verify full enforcement scope. | Custom token validation function that checks headers manually; `bcrypt.hash` used in a user service but the calling route is outside the scanned files. |
| **Low** | Heuristic match only -- code uses security-adjacent keywords and the surrounding context suggests possible control intent, but implementation details are ambiguous or the code may be a false positive that Phase B could not definitively resolve. | A function named `checkAccess` that reads a role field but the enforcement path (returning 403 vs. logging) is unclear from the available code. |

### Confidence Assignment Rules

- When the same control category has multiple evidence entries with different confidence levels, use the **highest** confidence entry as the representative control for that category.
- Report the confidence level alongside each evidence entry in the internal detection results. Confidence feeds into Phase 4 classification decisions.
- A **High** confidence control in any mapped category is sufficient to classify a threat as having a found control. A **Low** confidence control alone warrants a **partial** classification unless corroborated by additional evidence.

## Classification Rules (Phase 4)

Map each detected control to the specific threats it addresses using the STRIDE-to-control-category mapping. Assign a `control_status` (found, partial, missing) and determine the `reduction_factor` for each threat-control pair. When a threat has multiple applicable controls, select the control with the highest reduction factor.

### Threat-to-Control Mapping

For each scored threat in the finding set:

1. **Identify relevant control categories**: Using the STRIDE-to-Control-Category Mapping table, look up which control categories are relevant for this threat's `category`.
2. **Retrieve detection results**: From the Phase 3 detection output for this threat's `component`, check each relevant control category's detection status.
3. **Match controls to threat**: A control is "matching" if it was detected in a category that maps to this threat's STRIDE category.

### Classification Status Rules

**Control Found** (`found`):
- At least one relevant control category has `detected: true` with `confidence: High` or `confidence: Medium`
- The detected control directly addresses the threat's attack vector
- Reduction factor: **0.50** (P0 binary)

**Partial Control** (`partial`):
- One or more relevant control categories have `detected: true` but:
  - The detected control has `confidence: Low` only, OR
  - The threat maps to multiple control categories and only some have detections (e.g., Spoofing maps to Authentication + Access Control, but only Authentication is detected), OR
  - The detected control covers some but not all paths/endpoints for the component (evidence suggests incomplete coverage)
- Reduction factor: **0.25** (P0 binary)

**No Control Found** (`missing`):
- No relevant control categories have any detections for this component
- Or the component was unmapped (no files found in Phase 2)
- Reduction factor: **0.00**

### Multi-Control Resolution

When a threat maps to multiple control categories (e.g., Spoofing -> Authentication + Access Control):

1. **Evaluate each mapped category independently**: Check detection status and confidence for each.
2. **Classification priority**:
   - If ALL mapped categories have High/Medium confidence detections -> `found`
   - If SOME but not all mapped categories have detections -> `partial`
   - If NONE of the mapped categories have detections -> `missing`
3. **Best evidence selection**: Select the evidence from the category with the highest confidence detection. If tied, prefer the category that is more directly aligned with the threat (e.g., for Spoofing, prefer Authentication evidence over Access Control evidence).

### Cross-Component Controls

Some controls are global -- they apply across all components (e.g., a CORS middleware registered at the application root, a global rate limiter, a security headers middleware). Handle cross-component controls as follows:

1. **Detection during Phase 3**: Global controls are detected when scanning root-level or middleware-level files. They appear in the detection results for the component that contains the global middleware.
2. **Application to other components**: When a global control is detected for one component, it MAY apply to other components' threats if:
   - The control is registered at the application/server level (not route-specific)
   - The control category is relevant to the other component's threats
3. **Evidence inheritance**: When applying a global control to a different component's threat, the evidence references the global middleware file but the classification applies to the threat's component.
4. **Conservative approach**: When uncertain whether a global control applies to a specific component, classify as `partial` rather than `found`.

### P0 Effectiveness Note

In P0, `control_effectiveness` is derived from `control_status` (found -> "strong", partial -> "moderate", missing -> "none"). The full 4-dimension effectiveness assessment (Coverage, Configuration, Currency, Completeness) is a P1 feature. In P0, display the effectiveness rating but omit the dimension breakdown table -- replace with: *"Detailed effectiveness assessment available in P1 (User Story 6)."*

### Exhaustive Classification Requirement

Every finding in the Phase 1 finding set must receive exactly one classification. After Phase 4, the count of classified threats must equal the count of parsed findings. If any finding is missing a classification, halt with: **"Classification incomplete: {missing_count} findings unclassified. IDs: {id_list}"**
