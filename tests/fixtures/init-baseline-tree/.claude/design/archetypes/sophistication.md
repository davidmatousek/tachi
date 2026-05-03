# Sophistication Archetype

> Refined restraint. Serif elegance meets minimal composition. Every detail whispers quality, nothing shouts.

---

## Font Pairing

| Role | Font | Weights | Fallback |
|------|------|---------|----------|
| **Headings** | Cormorant Garamond | 400, 500, 600 | Georgia, serif |
| **Body** | Source Sans 3 | 300, 400, 500 | system-ui, sans-serif |

**Rationale**: Cormorant Garamond brings editorial authority and classical proportions to headings -- its high contrast strokes command attention without bulk. Source Sans 3's clean humanist forms provide excellent readability at body sizes while deferring to the serif's personality.

**Loading**: Import from Google Fonts with `display=swap`. Subset to `latin` for performance.

```
https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=Source+Sans+3:wght@300;400;500&display=swap
```

---

## Color Palette Strategy

**Temperature**: Neutral with warm undertone
**Saturation**: Low (5-20% saturation)
**Approach**: Muted neutrals with restrained gold and cream accents. Color is used sparingly -- the palette relies on value contrast rather than chromatic contrast.

| Token | Value | Usage |
|-------|-------|-------|
| `--color-primary` | `hsl(30, 10%, 15%)` | Primary text, near-black with warm cast |
| `--color-primary-light` | `hsl(30, 8%, 40%)` | Secondary text, meta information |
| `--color-accent` | `hsl(42, 45%, 48%)` | Muted gold -- links, highlights |
| `--color-accent-subtle` | `hsl(42, 30%, 94%)` | Cream tint for selected states |
| `--color-secondary` | `hsl(30, 6%, 55%)` | Tertiary text, decorative lines |
| `--color-surface` | `hsl(40, 15%, 97%)` | Off-white page background |
| `--color-surface-raised` | `hsl(40, 12%, 100%)` | Cards, white with warm cast |
| `--color-surface-dark` | `hsl(30, 15%, 12%)` | Dark sections, footers |
| `--color-border` | `hsl(35, 12%, 88%)` | Subtle dividers |
| `--color-border-strong` | `hsl(35, 10%, 75%)` | Input borders, rules |
| `--color-success` | `hsl(155, 30%, 40%)` | Muted success |
| `--color-warning` | `hsl(42, 55%, 50%)` | Warm warning |
| `--color-error` | `hsl(5, 45%, 48%)` | Subdued error |
| `--color-info` | `hsl(210, 25%, 50%)` | Quiet info |

---

## Spacing Preferences

**Density**: Generous with editorial rhythm
**Base unit**: 4px
**Philosophy**: Generous whitespace signals luxury. Content should feel curated and unhurried. Vertical spacing creates dramatic pauses between sections.

| Token | Value | Usage |
|-------|-------|-------|
| `--space-xs` | `0.5rem` (8px) | Inline spacing, metadata gaps |
| `--space-sm` | `1rem` (16px) | Paragraph spacing, tight groups |
| `--space-md` | `1.5rem` (24px) | Card padding, component spacing |
| `--space-lg` | `2.5rem` (40px) | Section gaps |
| `--space-xl` | `4rem` (64px) | Major section separation |
| `--space-2xl` | `6rem` (96px) | Hero spacing, page section breaks |

---

## Motion Style

**Character**: Elegant and deliberate
**Philosophy**: Movement should feel choreographed, not animated. Transitions are slow enough to notice, fast enough to never frustrate. Ease-in-out creates a sense of considered pacing.

| Token | Value |
|-------|-------|
| `--duration-fast` | `200ms` |
| `--duration-normal` | `250ms` |
| `--duration-slow` | `500ms` |
| `--easing-default` | `cubic-bezier(0.4, 0, 0.2, 1)` |
| `--easing-enter` | `cubic-bezier(0.0, 0.0, 0.2, 1)` |
| `--easing-exit` | `cubic-bezier(0.4, 0.0, 1, 1)` |
| `--easing-elegant` | `cubic-bezier(0.25, 0.1, 0.25, 1)` |

**Guidelines**:
- Hover effects: subtle opacity shifts or underline reveals at `--duration-fast`
- Page transitions: crossfade at `--duration-slow`
- Scroll-triggered reveals: fade-up with `--easing-elegant` at `--duration-slow`
- Avoid bouncing, overshoot, or playful easing
- Prefer opacity and transform over color transitions

---

## Shadow Depth

**Approach**: Extremely subtle. Shadows exist only to create the faintest sense of layering. Very low opacity, wide spread.

| Token | Value |
|-------|-------|
| `--shadow-sm` | `0 1px 3px hsla(30, 10%, 15%, 0.04)` |
| `--shadow-md` | `0 4px 12px hsla(30, 10%, 15%, 0.05)` |
| `--shadow-lg` | `0 8px 30px hsla(30, 10%, 15%, 0.06)` |
| `--shadow-focus` | `0 0 0 2px hsla(42, 45%, 48%, 0.25)` |

**Guidelines**:
- Cards: `--shadow-sm` or no shadow (use border instead)
- Modals: `--shadow-lg` with backdrop overlay
- Prefer hairline borders (`1px solid var(--color-border)`) over shadows for separation
- Shadow opacity should never exceed 8%
- Focus ring uses the gold accent at low opacity

---

## Border Radius

**Character**: Moderate and refined

| Token | Value |
|-------|-------|
| `--radius-sm` | `0.25rem` (4px) |
| `--radius-md` | `0.375rem` (6px) |
| `--radius-lg` | `0.5rem` (8px) |
| `--radius-full` | `9999px` |

**Guidelines**:
- Buttons: `--radius-sm` to `--radius-md` -- understated, not pill-shaped
- Cards: `--radius-md`
- Inputs: `--radius-sm`
- Images: `--radius-sm` or no radius for editorial photography
- Avoid fully rounded buttons -- they feel casual rather than refined

---

## Layout Philosophy

**Grid**: Asymmetric editorial layouts with intentional tension
**Whitespace**: Primary design element -- whitespace does the heavy lifting
**Rhythm**: Long-form vertical rhythm with dramatic section breaks
**Alignment**: Mixed alignment for editorial interest; left-aligned body, centered headings

| Token | Value |
|-------|-------|
| `--grid-columns` | `12` |
| `--grid-gutter` | `2rem` (32px) |
| `--grid-margin` | `2.5rem` (40px) |
| `--content-max-width` | `960px` |
| `--content-narrow` | `680px` |
| `--line-height-body` | `1.75` |
| `--line-height-heading` | `1.15` |

**Patterns**:
- Article layouts: narrow column (680px) for optimal reading
- Image galleries: asymmetric grid with varied aspect ratios
- Product showcases: large hero images with minimal text overlay
- Navigation: minimal, text-only, generous spacing
- Section dividers: thin hairline rules or generous empty space
- Pull quotes: large italic serif, indented

---

## Usage Notes

**Choose Sophistication when building**:
- Luxury and premium brand sites
- Editorial and publishing platforms
- Fashion and beauty products
- Wine, spirits, and fine dining
- Boutique services and high-end consulting
- Art galleries and museums
- Architecture and interior design portfolios

**Avoid Sophistication for**:
- Data-dense dashboards requiring compact layouts
- Children's or youth-oriented products
- Fast-paced gaming or entertainment
- Technical documentation or developer tools
- Budget or value-oriented brands

**Accessibility considerations**:
- Thin font weights (300) in Source Sans 3 require minimum 16px body size for readability
- Low-contrast aesthetic conflicts with WCAG -- verify all text against its background carefully
- Muted gold accent on cream backgrounds is a high-risk contrast pairing -- test rigorously
- Generous spacing and large text naturally benefit low-vision users
- Consider offering a high-contrast mode for critical interactive elements

---

## Example Token Overrides

```css
:root {
  /* Typography */
  --font-heading: 'Cormorant Garamond', Georgia, serif;
  --font-body: 'Source Sans 3', system-ui, sans-serif;
  --font-weight-heading: 500;
  --font-weight-body: 400;
  --font-weight-light: 300;

  /* Color */
  --color-primary: hsl(30, 10%, 15%);
  --color-primary-light: hsl(30, 8%, 40%);
  --color-accent: hsl(42, 45%, 48%);
  --color-accent-subtle: hsl(42, 30%, 94%);
  --color-secondary: hsl(30, 6%, 55%);
  --color-surface: hsl(40, 15%, 97%);
  --color-surface-raised: hsl(40, 12%, 100%);
  --color-surface-dark: hsl(30, 15%, 12%);
  --color-border: hsl(35, 12%, 88%);
  --color-border-strong: hsl(35, 10%, 75%);
  --color-success: hsl(155, 30%, 40%);
  --color-warning: hsl(42, 55%, 50%);
  --color-error: hsl(5, 45%, 48%);
  --color-info: hsl(210, 25%, 50%);

  /* Spacing */
  --space-xs: 0.5rem;
  --space-sm: 1rem;
  --space-md: 1.5rem;
  --space-lg: 2.5rem;
  --space-xl: 4rem;
  --space-2xl: 6rem;

  /* Motion */
  --duration-fast: 200ms;
  --duration-normal: 250ms;
  --duration-slow: 500ms;
  --easing-default: cubic-bezier(0.4, 0, 0.2, 1);
  --easing-enter: cubic-bezier(0.0, 0.0, 0.2, 1);
  --easing-exit: cubic-bezier(0.4, 0.0, 1, 1);
  --easing-elegant: cubic-bezier(0.25, 0.1, 0.25, 1);

  /* Shadows */
  --shadow-sm: 0 1px 3px hsla(30, 10%, 15%, 0.04);
  --shadow-md: 0 4px 12px hsla(30, 10%, 15%, 0.05);
  --shadow-lg: 0 8px 30px hsla(30, 10%, 15%, 0.06);
  --shadow-focus: 0 0 0 2px hsla(42, 45%, 48%, 0.25);

  /* Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-full: 9999px;

  /* Layout */
  --grid-columns: 12;
  --grid-gutter: 2rem;
  --grid-margin: 2.5rem;
  --content-max-width: 960px;
  --content-narrow: 680px;
  --line-height-body: 1.75;
  --line-height-heading: 1.15;
}
```
