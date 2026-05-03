# Presets

Presets are self-contained configuration files that modify output behavior for specific audiences, formats, or roles. Each preset is one file, loaded on demand during the draft phase.

## Preset Types

### Audience Presets

Adapt output tone and content selection for a specific audience.

```
Presets/
  formal-executive.md     # Conservative tone, strategic focus
  casual-team.md          # Conversational tone, collaborative focus
  technical-peer.md       # Detailed technical depth, assumed expertise
```

### Format Presets

Control output length, density, and structural patterns.

```
Presets/
  long-form-detailed.md   # Comprehensive coverage, full narratives
  brief-summary.md        # Key points only, minimal narrative
  bullet-focused.md       # Scannable format, action-oriented items
```

### Role Presets

Combine audience and format settings for common use cases.

```
Presets/
  senior-leadership.md    # Executive audience + brief format + strategic content
  hiring-manager.md       # Technical audience + moderate detail + achievement focus
```

## File Format

Each preset file specifies parameters that commands use during output generation:

```yaml
---
type: audience           # audience | format | role
name: "Formal Executive"
---

# Tone adjustments
- Use measured, authoritative language
- Lead with strategic impact, follow with evidence

# Content selection bias
- Prioritize leadership and business outcomes
- Minimize technical implementation details

# Formatting overrides
- Keep paragraphs to 3-4 sentences maximum
- Use quantified results wherever possible
```

## Guidelines

- **One file per preset** — keeps loading atomic and composable
- **Presets modify, not replace** — VoiceProfile and StyleGuide remain the baseline; presets adjust within those boundaries
- **Name descriptively** — the filename should make the preset's purpose obvious

## Security Note

Scan preset files for API keys, tokens, passwords, or connection strings that may have been pasted in. Never store credentials in preset files.
