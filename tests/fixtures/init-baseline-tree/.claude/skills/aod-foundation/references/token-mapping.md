# Canonical Token Mapping

Maps archetype token names to `tokens.css` semantic token names.
Used by Part 2 of `/aod.foundation` during brand file generation.

## Color Tokens

| tokens.css Name | Archetype Source | Derivation if Absent |
|---|---|---|
| `--color-primary` | `--color-primary` from Color Palette Strategy | Required — always present |
| `--color-secondary` | `--color-secondary` from palette | Derive from primary at +30 hue shift |
| `--color-accent` | `--color-accent` (or `--color-accent-1` for playful) | Required — always present |
| `--color-muted` | `--color-surface` from palette | Derive from primary at 10% saturation, 95% lightness |
| `--color-destructive` | `--color-error` from semantic colors | Fallback: `oklch(0.55 0.2 25)` (warm red) |
| `--color-success` | `--color-success` from semantic colors | Fallback: `oklch(0.6 0.15 145)` (green) |
| `--color-warning` | `--color-warning` from semantic colors | Fallback: `oklch(0.75 0.15 85)` (amber) |
| `--color-info` | `--color-info` from semantic colors | Fallback: `oklch(0.6 0.15 245)` (blue) |
| `--color-background` | `--color-surface` from palette | Required — always present |
| `--color-foreground` | `--color-primary` from palette | Primary text color serves as foreground |

### Key Renames

- `--color-error` in archetype becomes `--color-destructive` in tokens.css
- `--color-surface` in archetype becomes both `--color-background` AND `--color-muted`
- `--color-primary` serves double duty as `--color-primary` AND `--color-foreground`

## Typography Tokens

| tokens.css Name | Archetype Source | Derivation if Absent |
|---|---|---|
| `--font-sans` | **Body** font from Font Pairing table | Required — always present |
| `--font-heading` | **Headings** font from Font Pairing table | Required — always present |
| `--font-mono` | Not in archetypes | Always: `"JetBrains Mono", "Fira Code", monospace` |

### Key Renames

- `--font-body` in archetype becomes `--font-sans` in tokens.css

## Radius Tokens

| tokens.css Name | Archetype Source | Derivation if Absent |
|---|---|---|
| `--radius-sm` | `--radius-sm` from Border Radius | Required — always present |
| `--radius-md` | `--radius-md` from Border Radius | Required — always present |
| `--radius-lg` | `--radius-lg` from Border Radius | Derive: `--radius-md` value * 1.5 |

## Shadow Tokens

| tokens.css Name | Archetype Source | Derivation if Absent |
|---|---|---|
| `--shadow-sm` | `--shadow-sm` from Shadow Depth | Required — always present |
| `--shadow-md` | `--shadow-md` from Shadow Depth | Required — always present |
| `--shadow-lg` | `--shadow-lg` from Shadow Depth | Derive from `--shadow-md` (see below) |

### Shadow-lg Derivation

For archetypes that only define sm and md (precision, technical):

1. Parse `--shadow-md` to extract offset-y, blur-radius, and opacity
2. Multiply offset-y by 2.5 (e.g., 2px -> 5px)
3. Multiply blur-radius by 2.5 (e.g., 4px -> 10px)
4. Multiply opacity by 1.25 (e.g., 0.08 -> 0.10)
5. Keep the same hsla hue/saturation/lightness values
6. Result: `0 {new-offset-y}px {new-blur}px hsla({h}, {s}%, {l}%, {new-opacity})`
