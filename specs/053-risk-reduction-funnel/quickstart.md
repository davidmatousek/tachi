# Quickstart: Risk Reduction Funnel

## Prerequisites

Run the full tachi pipeline on your architecture description:

```bash
# Step 1: Threat model (always required)
/threat-model path/to/architecture.md

# Step 2: Risk scoring (enables 3-tier funnel)
/risk-score path/to/threats.md

# Step 3: Compensating controls (enables full 4-tier funnel)
/compensating-controls path/to/risk-scores.md
```

## Generate the Funnel

```bash
# Auto-detect richest data source in current directory
/infographic --template risk-funnel

# Or specify explicit data source
/infographic path/to/compensating-controls.md --template risk-funnel

# Generate all three templates (baseball-card + system-architecture + risk-funnel)
/infographic --template all
```

## Output Files

| File | Content |
|------|---------|
| `threat-risk-funnel-spec.md` | 6-section infographic specification with funnel tier data |
| `threat-risk-funnel.jpg` | Photorealistic 3D funnel image (when GEMINI_API_KEY available) |

## What You Get

### Full Pipeline (4 tiers)
All 4 tiers rendered with data: Threats Identified → Inherent Risk Scored → Controls Applied → Residual Risk. Metrics sidebar shows risk reduction % and control coverage %.

### Partial Pipeline (3 tiers)
3 solid tiers + 1 ghost tier with CTA: "Run /compensating-controls to complete the funnel."

### Minimal Pipeline (1 tier)
1 solid tier + 3 ghost tiers. Enhancement tip: "Run /risk-score to begin quantifying your risk reduction funnel."

## Implementation Files

| File | Action | Purpose |
|------|--------|---------|
| `.claude/agents/tachi/templates/infographic-risk-funnel.md` | CREATE | Design template (9 sections) |
| `.claude/agents/tachi/threat-infographic.md` | UPDATE | Add to template registry + extraction logic |
| `.claude/commands/infographic.md` | UPDATE | Add `risk-funnel` as valid template value |
