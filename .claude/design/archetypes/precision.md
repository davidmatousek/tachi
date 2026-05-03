# Precision Archetype

> Engineered clarity. Every pixel justified, every element measured. Precision strips away ornament to reveal pure function.

---

## Font Pairing

| Role | Font | Weights | Fallback |
|------|------|---------|----------|
| **Headings** | Space Grotesk | 500, 600, 700 | system-ui, sans-serif |
| **Body** | DM Sans | 400, 500, 600 | system-ui, sans-serif |

**Rationale**: Space Grotesk's geometric construction and tabular figures make it ideal for data-heavy headings. DM Sans provides a slightly warmer geometric companion for body text without sacrificing technical clarity.

**Loading**: Import from Google Fonts with `display=swap`. Subset to `latin` for performance.

```
https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=DM+Sans:wght@400;500;600&display=swap
```

---

## Color Palette Strategy

**Temperature**: Cool neutral
**Saturation**: Desaturated (5-15% saturation)
**Approach**: Monochromatic base with a single functional accent

| Token | Value | Usage |
|-------|-------|-------|
| `--color-primary` | `hsl(220, 14%, 20%)` | Primary text, strong UI elements |
| `--color-primary-light` | `hsl(220, 12%, 40%)` | Secondary text, icons |
| `--color-accent` | `hsl(215, 60%, 50%)` | Interactive elements, links, focus rings |
| `--color-accent-subtle` | `hsl(215, 40%, 95%)` | Accent backgrounds, selected states |
| `--color-surface` | `hsl(220, 10%, 98%)` | Page background |
| `--color-surface-raised` | `hsl(0, 0%, 100%)` | Cards, panels |
| `--color-border` | `hsl(220, 10%, 88%)` | Dividers, input borders |
| `--color-border-strong` | `hsl(220, 10%, 75%)` | Active input borders, emphasis |
| `--color-success` | `hsl(145, 45%, 42%)` | Success states |
| `--color-warning` | `hsl(38, 70%, 50%)` | Warning states |
| `--color-error` | `hsl(0, 55%, 50%)` | Error states |
| `--color-info` | `hsl(215, 60%, 50%)` | Info states (matches accent) |

---

## Spacing Preferences

**Density**: Compact
**Base unit**: 4px
**Philosophy**: Tight but never cramped. Spacing serves information density -- reduce whitespace to maximize data visibility.

| Token | Value | Usage |
|-------|-------|-------|
| `--space-xs` | `0.25rem` (4px) | Icon gaps, inline spacing |
| `--space-sm` | `0.5rem` (8px) | Input padding, tight groups |
| `--space-md` | `0.75rem` (12px) | Card padding, list item spacing |
| `--space-lg` | `1rem` (16px) | Section gaps, form field spacing |
| `--space-xl` | `1.5rem` (24px) | Section separation |
| `--space-2xl` | `2rem` (32px) | Page section boundaries |

---

## Motion Style

**Character**: Snappy and purposeful
**Philosophy**: Motion should confirm actions, not entertain. Fast transitions signal responsiveness.

| Token | Value |
|-------|-------|
| `--duration-fast` | `100ms` |
| `--duration-normal` | `150ms` |
| `--duration-slow` | `250ms` |
| `--easing-default` | `cubic-bezier(0.2, 0, 0, 1)` |
| `--easing-enter` | `cubic-bezier(0, 0, 0, 1)` |
| `--easing-exit` | `cubic-bezier(0.2, 0, 1, 1)` |

**Guidelines**:
- Tooltips and dropdowns: `--duration-fast`
- State transitions (hover, focus): `--duration-normal`
- Panel/modal entry: `--duration-slow`
- Avoid spring or bounce effects entirely

---

## Shadow Depth

**Approach**: Minimal elevation. Shadows are used sparingly to indicate interactive layering only.

| Token | Value |
|-------|-------|
| `--shadow-sm` | `0 1px 2px hsla(220, 14%, 20%, 0.06)` |
| `--shadow-md` | `0 2px 4px hsla(220, 14%, 20%, 0.08)` |
| `--shadow-focus` | `0 0 0 2px var(--color-accent-subtle), 0 0 0 4px var(--color-accent)` |

**Guidelines**:
- Cards and panels: `--shadow-sm` or border only
- Dropdowns and popovers: `--shadow-md`
- Avoid `lg` or `xl` shadows -- prefer borders for elevation
- Focus rings use a double-ring pattern for visibility

---

## Border Radius

**Character**: Sharp and technical

| Token | Value |
|-------|-------|
| `--radius-sm` | `0.125rem` (2px) |
| `--radius-md` | `0.25rem` (4px) |
| `--radius-lg` | `0.375rem` (6px) |
| `--radius-full` | `9999px` |

**Guidelines**:
- Buttons and inputs: `--radius-sm`
- Cards: `--radius-md`
- Tags and badges: `--radius-sm`
- Avatars and indicators: `--radius-full`
- Never exceed `--radius-lg` for rectangular elements

---

## Layout Philosophy

**Grid**: Strict 12-column grid with mathematical precision
**Whitespace**: Economical -- space is functional, not decorative
**Rhythm**: Consistent vertical rhythm on 4px baseline grid
**Alignment**: Hard left alignment preferred; center only for hero content

| Token | Value |
|-------|-------|
| `--grid-columns` | `12` |
| `--grid-gutter` | `1rem` (16px) |
| `--grid-margin` | `1.5rem` (24px) |
| `--content-max-width` | `1200px` |
| `--sidebar-width` | `240px` |

**Patterns**:
- Data tables: full-width, dense rows, sticky headers
- Dashboards: card grid with uniform sizing
- Forms: single-column, labels above inputs
- Navigation: compact sidebar with icon + label

---

## Usage Notes

**Choose Precision when building**:
- SaaS dashboards with dense data displays
- Developer tools and admin panels
- Analytics and monitoring platforms
- Fintech applications
- Enterprise B2B software
- CLI companions with web interfaces

**Avoid Precision for**:
- Consumer-facing marketing sites
- Children's or family-oriented products
- Wellness or lifestyle applications
- Brands emphasizing warmth or personality

**Accessibility considerations**:
- The desaturated palette requires careful contrast checking on gray-on-gray combinations
- Compact spacing demands clear focus indicators -- the double-ring focus pattern is essential
- Tabular figures in Space Grotesk aid readability in data-heavy screens

---

## Example Token Overrides

```css
:root {
  /* Typography */
  --font-heading: 'Space Grotesk', system-ui, sans-serif;
  --font-body: 'DM Sans', system-ui, sans-serif;
  --font-weight-heading: 600;
  --font-weight-body: 400;

  /* Color */
  --color-primary: hsl(220, 14%, 20%);
  --color-primary-light: hsl(220, 12%, 40%);
  --color-accent: hsl(215, 60%, 50%);
  --color-accent-subtle: hsl(215, 40%, 95%);
  --color-surface: hsl(220, 10%, 98%);
  --color-surface-raised: hsl(0, 0%, 100%);
  --color-border: hsl(220, 10%, 88%);
  --color-border-strong: hsl(220, 10%, 75%);
  --color-success: hsl(145, 45%, 42%);
  --color-warning: hsl(38, 70%, 50%);
  --color-error: hsl(0, 55%, 50%);
  --color-info: hsl(215, 60%, 50%);

  /* Spacing */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 0.75rem;
  --space-lg: 1rem;
  --space-xl: 1.5rem;
  --space-2xl: 2rem;

  /* Motion */
  --duration-fast: 100ms;
  --duration-normal: 150ms;
  --duration-slow: 250ms;
  --easing-default: cubic-bezier(0.2, 0, 0, 1);
  --easing-enter: cubic-bezier(0, 0, 0, 1);
  --easing-exit: cubic-bezier(0.2, 0, 1, 1);

  /* Shadows */
  --shadow-sm: 0 1px 2px hsla(220, 14%, 20%, 0.06);
  --shadow-md: 0 2px 4px hsla(220, 14%, 20%, 0.08);
  --shadow-focus: 0 0 0 2px var(--color-accent-subtle), 0 0 0 4px var(--color-accent);

  /* Radius */
  --radius-sm: 0.125rem;
  --radius-md: 0.25rem;
  --radius-lg: 0.375rem;
  --radius-full: 9999px;

  /* Layout */
  --grid-columns: 12;
  --grid-gutter: 1rem;
  --grid-margin: 1.5rem;
  --content-max-width: 1200px;
  --sidebar-width: 240px;
}
```
