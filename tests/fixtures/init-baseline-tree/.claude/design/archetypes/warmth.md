# Warmth Archetype

> Friendly and inviting. Soft edges, earthy tones, and generous breathing room create spaces that feel like a conversation with a trusted friend.

---

## Font Pairing

| Role | Font | Weights | Fallback |
|------|------|---------|----------|
| **Headings** | Nunito | 600, 700, 800 | system-ui, sans-serif |
| **Body** | Quicksand | 400, 500, 600 | system-ui, sans-serif |

**Rationale**: Nunito's rounded terminals and warm geometry make headings approachable without losing clarity. Quicksand's open apertures and rounded forms create exceptionally friendly body text that invites reading.

**Loading**: Import from Google Fonts with `display=swap`. Subset to `latin` for performance.

```
https://fonts.googleapis.com/css2?family=Nunito:wght@600;700;800&family=Quicksand:wght@400;500;600&display=swap
```

---

## Color Palette Strategy

**Temperature**: Warm
**Saturation**: Moderate (25-50% saturation)
**Approach**: Earthy base with warm accent tones drawn from nature

| Token | Value | Usage |
|-------|-------|-------|
| `--color-primary` | `hsl(25, 30%, 25%)` | Primary text, headings |
| `--color-primary-light` | `hsl(25, 20%, 45%)` | Secondary text, captions |
| `--color-accent` | `hsl(25, 65%, 52%)` | Terracotta -- CTAs, active elements |
| `--color-accent-subtle` | `hsl(25, 50%, 94%)` | Warm tint backgrounds |
| `--color-secondary` | `hsl(145, 25%, 42%)` | Sage green -- secondary actions |
| `--color-secondary-subtle` | `hsl(145, 20%, 93%)` | Sage tint backgrounds |
| `--color-surface` | `hsl(35, 30%, 97%)` | Cream page background |
| `--color-surface-raised` | `hsl(35, 25%, 99%)` | Cards, elevated surfaces |
| `--color-border` | `hsl(30, 18%, 85%)` | Soft dividers |
| `--color-border-strong` | `hsl(30, 20%, 72%)` | Input borders, emphasis |
| `--color-success` | `hsl(145, 40%, 45%)` | Success states |
| `--color-warning` | `hsl(40, 80%, 52%)` | Amber warnings |
| `--color-error` | `hsl(8, 55%, 52%)` | Soft red errors |
| `--color-info` | `hsl(200, 45%, 50%)` | Info states |

---

## Spacing Preferences

**Density**: Generous
**Base unit**: 4px
**Philosophy**: Spacious layouts that breathe. Ample whitespace makes content feel curated, not crowded. Generous padding inside elements creates a sense of comfort.

| Token | Value | Usage |
|-------|-------|-------|
| `--space-xs` | `0.5rem` (8px) | Icon gaps, inline spacing |
| `--space-sm` | `0.75rem` (12px) | Tight groups, tag spacing |
| `--space-md` | `1.25rem` (20px) | Card padding, list item spacing |
| `--space-lg` | `2rem` (32px) | Section gaps, form field spacing |
| `--space-xl` | `3rem` (48px) | Section separation |
| `--space-2xl` | `4rem` (64px) | Page section boundaries |

---

## Motion Style

**Character**: Gentle and organic
**Philosophy**: Transitions should feel like a calm exhale. Nothing jolts or snaps. Elements arrive softly and settle into place.

| Token | Value |
|-------|-------|
| `--duration-fast` | `200ms` |
| `--duration-normal` | `300ms` |
| `--duration-slow` | `500ms` |
| `--easing-default` | `cubic-bezier(0.4, 0, 0.2, 1)` |
| `--easing-enter` | `cubic-bezier(0.0, 0, 0.2, 1)` |
| `--easing-exit` | `cubic-bezier(0.4, 0, 1, 1)` |

**Guidelines**:
- Hover effects: `--duration-fast` with gentle opacity or color shift
- Page transitions: `--duration-slow` with subtle fade
- Expanding/collapsing content: `--duration-normal`
- Avoid sharp linear motion -- always use eased curves
- Micro-interactions should feel like a soft pulse, not a snap

---

## Shadow Depth

**Approach**: Soft, diffused shadows that create gentle depth. Shadows should feel like natural light, not hard edges.

| Token | Value |
|-------|-------|
| `--shadow-sm` | `0 1px 3px hsla(25, 30%, 25%, 0.06), 0 1px 2px hsla(25, 30%, 25%, 0.04)` |
| `--shadow-md` | `0 4px 8px hsla(25, 30%, 25%, 0.07), 0 2px 4px hsla(25, 30%, 25%, 0.04)` |
| `--shadow-lg` | `0 10px 24px hsla(25, 30%, 25%, 0.08), 0 4px 8px hsla(25, 30%, 25%, 0.04)` |
| `--shadow-focus` | `0 0 0 3px hsla(25, 65%, 52%, 0.3)` |

**Guidelines**:
- Cards: `--shadow-sm` default, `--shadow-md` on hover
- Modals and dialogs: `--shadow-lg`
- Shadows use warm hue tinting to match the palette
- Large blur radius creates diffused, natural-feeling depth

---

## Border Radius

**Character**: Rounded and soft

| Token | Value |
|-------|-------|
| `--radius-sm` | `0.5rem` (8px) |
| `--radius-md` | `0.75rem` (12px) |
| `--radius-lg` | `1rem` (16px) |
| `--radius-xl` | `1.25rem` (20px) |
| `--radius-full` | `9999px` |

**Guidelines**:
- Buttons: `--radius-lg` for a friendly, pill-like feel
- Cards: `--radius-lg` to `--radius-xl`
- Inputs: `--radius-md`
- Tags and badges: `--radius-full`
- Images and avatars: `--radius-lg` or `--radius-full`
- Sharp corners are never used

---

## Layout Philosophy

**Grid**: Relaxed 12-column grid with generous gutters
**Whitespace**: Abundant -- whitespace is a primary design element
**Rhythm**: Flowing vertical rhythm with comfortable line heights (1.6-1.75 for body)
**Alignment**: Center-weighted layouts with organic visual balance

| Token | Value |
|-------|-------|
| `--grid-columns` | `12` |
| `--grid-gutter` | `1.5rem` (24px) |
| `--grid-margin` | `2rem` (32px) |
| `--content-max-width` | `1080px` |
| `--line-height-body` | `1.7` |
| `--line-height-heading` | `1.3` |

**Patterns**:
- Content sections: max-width with centered alignment
- Cards: generous internal padding, grouped with visible gaps
- Forms: spacious field spacing, helper text below inputs
- Images: rounded corners, occasional overlap for organic feel
- Testimonials and quotes: large text, ample margin

---

## Usage Notes

**Choose Warmth when building**:
- Wellness and health applications
- Community and social platforms
- Family-oriented products
- Non-profit and charitable organizations
- Educational platforms for general audiences
- Food and recipe applications
- Personal finance with a friendly tone

**Avoid Warmth for**:
- Data-heavy analytics dashboards
- Developer tools and technical interfaces
- Enterprise B2B platforms prioritizing density
- Gaming or high-energy entertainment products

**Accessibility considerations**:
- Warm color palette requires extra vigilance on contrast ratios -- test terracotta on cream carefully
- Generous spacing naturally aids users with motor impairments (larger touch targets)
- Rounded forms improve readability for users with dyslexia
- Ensure the sage green secondary passes contrast checks against light backgrounds

---

## Example Token Overrides

```css
:root {
  /* Typography */
  --font-heading: 'Nunito', system-ui, sans-serif;
  --font-body: 'Quicksand', system-ui, sans-serif;
  --font-weight-heading: 700;
  --font-weight-body: 400;

  /* Color */
  --color-primary: hsl(25, 30%, 25%);
  --color-primary-light: hsl(25, 20%, 45%);
  --color-accent: hsl(25, 65%, 52%);
  --color-accent-subtle: hsl(25, 50%, 94%);
  --color-secondary: hsl(145, 25%, 42%);
  --color-secondary-subtle: hsl(145, 20%, 93%);
  --color-surface: hsl(35, 30%, 97%);
  --color-surface-raised: hsl(35, 25%, 99%);
  --color-border: hsl(30, 18%, 85%);
  --color-border-strong: hsl(30, 20%, 72%);
  --color-success: hsl(145, 40%, 45%);
  --color-warning: hsl(40, 80%, 52%);
  --color-error: hsl(8, 55%, 52%);
  --color-info: hsl(200, 45%, 50%);

  /* Spacing */
  --space-xs: 0.5rem;
  --space-sm: 0.75rem;
  --space-md: 1.25rem;
  --space-lg: 2rem;
  --space-xl: 3rem;
  --space-2xl: 4rem;

  /* Motion */
  --duration-fast: 200ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
  --easing-default: cubic-bezier(0.4, 0, 0.2, 1);
  --easing-enter: cubic-bezier(0.0, 0, 0.2, 1);
  --easing-exit: cubic-bezier(0.4, 0, 1, 1);

  /* Shadows */
  --shadow-sm: 0 1px 3px hsla(25, 30%, 25%, 0.06), 0 1px 2px hsla(25, 30%, 25%, 0.04);
  --shadow-md: 0 4px 8px hsla(25, 30%, 25%, 0.07), 0 2px 4px hsla(25, 30%, 25%, 0.04);
  --shadow-lg: 0 10px 24px hsla(25, 30%, 25%, 0.08), 0 4px 8px hsla(25, 30%, 25%, 0.04);
  --shadow-focus: 0 0 0 3px hsla(25, 65%, 52%, 0.3);

  /* Radius */
  --radius-sm: 0.5rem;
  --radius-md: 0.75rem;
  --radius-lg: 1rem;
  --radius-xl: 1.25rem;
  --radius-full: 9999px;

  /* Layout */
  --grid-columns: 12;
  --grid-gutter: 1.5rem;
  --grid-margin: 2rem;
  --content-max-width: 1080px;
  --line-height-body: 1.7;
  --line-height-heading: 1.3;
}
```
