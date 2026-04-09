# Template-Specific Formats

Section 5 (Architecture Threat Overlay) format definitions for each infographic template. Sections 1-4 are shared across all templates -- see `infographic-specifications.md`. Each template uses a distinct Section 5 layout optimized for its visual design.

---

## Baseball Card Template -- Tabular Format

The Baseball Card template uses a **tabular** format for Section 5, summarizing component risk weights:

```markdown
## 5. Architecture Threat Overlay

| Component | Risk Weight | Finding Count | Annotation |
|-----------|-------------|---------------|------------|
| {component} | High | {N} | {Description of risk profile and dominant threat categories} |
| {component} | Medium | {N} | {Description} |
| {component} | Low | {N} | {Description} |
```

### Baseball Card Data Source Variations

**When data source is `compensating-controls`**: The Architecture Overlay includes an additional summary line in the table: "**Risk Reduction: {risk_reduction_pct}%**" showing overall control effectiveness from the Executive Summary. Component risk weights use residual scores (average `residual_score` per component, same thresholds as risk-scores path).

---

## System Architecture Template -- Spatial Format

The System Architecture template uses a **spatial** format for Section 5, providing zone-grouped layout with component placement, data flows, and boundary crossings. The full spatial Section 5 schema is defined in the System Architecture template file (`templates/tachi/infographics/infographic-system-architecture.md`).

This format is produced from three `template_data` JSON fields:

| JSON Field | Content |
|------------|---------|
| `template_data.trust_zones[]` | Trust zone groupings for spatial layout |
| `template_data.data_flows[]` | Data flow arrows with severity coloring |
| `template_data.boundary_crossings[]` | Trust boundary crossing annotations |

### System Architecture Data Source Variations

**When data source is `compensating-controls`**: Component box border colors use residual severity (highest `residual_score` determines color via severity band mapping). Badges show residual finding count and residual severity band. Data flow arrow colors use the highest `residual_score` among findings involving both source and destination. The finding legend groups findings by residual severity band. Header label reads "Residual Risk" per the risk label mapping.

---

## Risk Funnel Template -- Funnel-Tier Format

The Risk Funnel template uses a **funnel-tier** format for Section 5, showing a vertical tier table with progressive risk reduction:

```markdown
## 5. Architecture Threat Overlay

### Funnel Tiers

| Tier | Label | Width (%) | Severity Counts | Render State |
|------|-------|-----------|-----------------|--------------|
| 1 | Threats Identified | 100 | {critical}C / {high}H / {medium}M / {low}L | solid |
| 2 | Inherent Risk Scored | {width_2} | {critical}C / {high}H / {medium}M / {low}L | solid |
| 3 | Controls Applied | {width_3} | {coverage}% coverage, {mitigated}/{total} mitigated | solid |
| 4 | Residual Risk | {width_4} | {critical}C / {high}H / {medium}M / {low}L | solid |
```

### Tier Width Calculation

Tier widths are proportional to finding count or risk volume at each stage:

- **Tier 1**: Always 100% (baseline -- total threats identified)
- **Tier 2-4**: `actual_width = (tier_volume / tier_1_volume) * 100`
- **Minimum 10% narrowing** per tier enforced
- **Absolute floor**: 10% width

### Sidebar Metrics

```markdown
### Sidebar Metrics

| Metric | Value |
|--------|-------|
| Total Findings | {total_findings} |
| Risk Reduction | {risk_reduction_pct}% |
| Control Coverage | {control_coverage_pct}% |
```

### Risk Funnel Data Source Modes

The Risk Funnel template renders different numbers of solid tiers depending on the available data source:

#### 4-Tier Mode (compensating-controls)

All 4 tiers rendered as solid:

- **Tier 1**: Data from co-located `threats.md` Section 6 (Risk Summary): total finding count and qualitative severity distribution
- **Tier 2**: Data from co-located `risk-scores.md` Section 2 if present, otherwise recalculate from `compensating-controls.md` inherent scores
- **Tier 3**: Data from `compensating-controls.md` Section 1 (Executive Summary): control coverage percentage, findings with controls count
- **Tier 4**: Data from `compensating-controls.md` Section 2 (Coverage Matrix): residual severity distribution
- **Risk reduction percentage**: Delta between average inherent score and average residual score
- **Sidebar**: Shows full metrics

#### 3-Tier Mode (risk-scores)

Tiers 1-3 solid, Tier 4 ghost:

- **Tier 1**: Data from co-located `threats.md` Section 6
- **Tier 2**: Data from `risk-scores.md` Section 2 (Scored Threat Table): composite score distribution
- **Tier 3**: Label changes to "Unmitigated Risk" using Tier 2 severity data (no control reduction applied)
- **Tier 4**: Rendered as ghost with CTA: "Run /tachi.compensating-controls to complete the funnel"
- **Enhancement tip in spec**: "Run `/tachi.compensating-controls` to unlock the full 4-tier risk reduction funnel"
- **Sidebar**: Shows total findings, severity distribution, "Risk Reduction: N/A -- run /tachi.compensating-controls"

#### 1-Tier Mode (threats)

Tier 1 solid, Tiers 2-4 ghost:

- **Tier 1**: Data from `threats.md` Section 6: total count and severity distribution
- **Tier 2**: Ghost CTA: "Run /tachi.risk-score"
- **Tier 3**: Ghost CTA: "Run /tachi.compensating-controls"
- **Tier 4**: Ghost CTA: "Complete the pipeline"
- **Enhancement tip in spec**: "Run `/tachi.risk-score` to begin quantifying your risk reduction funnel"
- **Sidebar**: Shows total findings and qualitative severity counts only

### Risk Funnel Edge Cases

**Empty threats.md (zero findings)**: Render a single tier labeled "0 Threats Identified" with the message "No threats found -- threat model may need review". All other tiers ghost. Sidebar shows "Total Findings: 0". This applies regardless of data source -- if the upstream threats.md contains no findings, the funnel cannot populate any tier with real data.

**All findings same severity**: All tiers use uniform coloring (the single severity color from the color palette). Minimum 10% narrowing per tier still enforced to maintain funnel shape. The tier width calculation proceeds normally -- uniform severity does not collapse tiers to equal width; volume reduction across pipeline stages still drives narrowing.

**Large finding count (100+ findings)**: Tier labels show aggregate counts only (e.g., "142 findings -- 23C / 45H / 52M / 22L"). Individual finding details omitted from tier visuals -- detail is in the spec sections. This prevents visual clutter and keeps the funnel readable at standard 16:9 resolution.

**Zero risk reduction (all controls missing or none effective)**: Tier 4 width equals Tier 2 width (no narrowing for controls/residual tiers). Tier 1 to Tier 2 still narrows to maintain funnel shape. Sidebar note: "0% risk reduction -- no effective controls detected". This occurs when compensating-controls.md reports zero coverage or all controls have no impact on residual scores.

### Visual Guidance

Components with `High` risk weight should be rendered with the largest visual emphasis (bold borders, larger icons, red highlight). `Medium` components receive moderate emphasis (orange highlight). `Low` components receive minimal emphasis (standard rendering).

---

## MAESTRO Stack Template — Layer-Grouped Format

The MAESTRO Stack template uses a **layer-grouped** format for Section 5, showing per-layer finding distribution:

```markdown
## 5. Architecture Threat Overlay

| Layer | Name | Finding Count | Highest Severity | Top Findings |
|-------|------|---------------|------------------|--------------|
| L1 | Foundation Model | {N} | {severity} | {ID}: {summary}; {ID}: {summary} |
| L2 | Data Operations | {N} | {severity} | {ID}: {summary} |
```

### MAESTRO Stack Data Source

This format is produced from three `template_data` JSON fields:

| JSON Field | Content |
|------------|---------|
| `template_data.maestro_layer_distribution[]` | Per-layer aggregate data |
| `template_data.most_exposed_layer` | Layer with highest finding count |
| `template_data.per_layer_summaries[]` | Layer details with top 2 findings each |

### MAESTRO Stack Edge Cases

**No MAESTRO data (pre-Feature 084)**: `has_maestro_data` is false. Spec renders empty state: "No MAESTRO layer data available. Run threat analysis with schema version 1.2+ to enable layer classification."

**All findings in one layer**: One band fully highlighted, six muted. Sidebar shows "1 Layer with Findings, 6 Empty Layers".

**Empty layers**: Layers with zero findings still appear in the stack but are visually muted (darker background, grayed text).

---

## MAESTRO Heatmap Template — Component-Layer Grid Format

The MAESTRO Heatmap template uses a **component-layer grid** format for Section 5, showing intersection severity:

```markdown
## 5. Architecture Threat Overlay

### Component-Layer Intersection Grid

| Component | L1 | L2 | L3 | L4 | L5 | L6 | L7 |
|-----------|----|----|----|----|----|----|-----|
| {name} | {severity|—} | {severity|—} | ... | ... | ... | ... | ... |
```

### MAESTRO Heatmap Data Source

This format is produced from two `template_data` JSON fields:

| JSON Field | Content |
|------------|---------|
| `template_data.maestro_heatmap[]` | Component-layer intersection grid |
| `template_data.maestro_layer_distribution[]` | Per-layer aggregate data for legend |

### MAESTRO Heatmap Edge Cases

**No MAESTRO data**: `has_maestro_data` is false. Spec renders empty state message.

**Component name truncation**: Component names longer than 25 characters are truncated with "..." to maintain grid readability.

**Single-column concentration**: If all findings map to one layer, only that column has colored cells; all other columns show "—".
