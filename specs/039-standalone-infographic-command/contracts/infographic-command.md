# Command Interface Contract: /infographic

## Invocation

```
/infographic [data-source-path] [--template {baseball-card|system-architecture|all}] [--output-dir <path>]
```

## Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `data-source-path` | filepath | No | Auto-detect | Explicit path to `threats.md` or `risk-scores.md` |
| `--template` | enum | No | `all` | Template to generate: `baseball-card`, `system-architecture`, `all` |
| `--output-dir` | filepath | No | Same as input | Directory for output files |

## Aliases

| Alias | Resolves To |
|-------|-------------|
| `corporate-white` | `baseball-card` |

## Input Resolution

### Auto-Detection (no explicit path)

1. Scan current working directory for `risk-scores.md` — if found, use as primary
2. If `risk-scores.md` found, verify co-located `threats.md` exists — error if missing
3. If `risk-scores.md` not found, scan for `threats.md` — if found, use as sole source
4. If neither found, exit with error listing expected file paths

### Explicit Path

1. Validate file exists at provided path — error if missing
2. Detect file type from content structure:
   - Contains `## 2. Scored Threat Table` with `Composite` column → risk-scores.md
   - Contains `## 6. Risk Summary` → threats.md
3. If risk-scores.md detected, verify co-located threats.md in same directory

## Output Contract

### Per Template

| Output | Filename | Condition |
|--------|----------|-----------|
| Specification | `threat-{template-name}-spec.md` | Always generated |
| Image | `threat-{template-name}.jpg` | Only when GEMINI_API_KEY available and API succeeds |

### Template = `all` (default)

Generates both:
- `threat-baseball-card-spec.md` + `threat-baseball-card.jpg`
- `threat-system-architecture-spec.md` + `threat-system-architecture.jpg`

## Exit Codes

| Condition | Behavior |
|-----------|----------|
| Success (spec generated) | Display summary, exit normally |
| No input files found | Error message listing expected files |
| Explicit path not found | Error message with provided path |
| risk-scores.md without threats.md | Error explaining co-location requirement |
| Invalid template name | Error listing valid template names |
| Gemini API failure | Spec saved, image skipped, info message (not an error) |
| Missing GEMINI_API_KEY | Spec saved, image skipped, info message (not an error) |

## Graceful Degradation

Per ADR-014, six conditions result in spec saved + image skipped:
1. Missing API key
2. Rate limit (429)
3. API timeout (60s)
4. Content policy rejection
5. Missing Section 6 in input
6. Empty threat model
