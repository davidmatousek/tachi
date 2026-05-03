# Boldness Archetype

> Maximum impact. Heavy type, vivid color, dramatic scale. Boldness demands attention and refuses to be ignored.

---

## Font Pairing

| Role | Font | Weights | Fallback |
|------|------|---------|----------|
| **Headings** | Plus Jakarta Sans | 700, 800 | system-ui, sans-serif |
| **Body** | Outfit | 400, 500, 600 | system-ui, sans-serif |

**Rationale**: Plus Jakarta Sans at heavy weights delivers punchy, contemporary headings with strong geometric character. Outfit provides clean, modern body text that supports the headings without competing -- its even proportions maintain readability at all sizes.

**Loading**: Import from Google Fonts with `display=swap`. Subset to `latin` for performance.

```
https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800&family=Outfit:wght@400;500;600&display=swap
```

---

## Color Palette Strategy

**Temperature**: Neutral to cool (shifts depending on brand primary)
**Saturation**: High (60-90% saturation)
**Approach**: High-contrast vivid primaries with near-black and white as structural anchors. Color is used for impact, not subtlety.

| Token | Value | Usage |
|-------|-------|-------|
| `--color-primary` | `hsl(0, 0%, 8%)` | Near-black text, strong structural elements |
| `--color-primary-inverse` | `hsl(0, 0%, 100%)` | White text on dark backgrounds |
| `--color-accent` | `hsl(250, 85%, 58%)` | Electric violet -- primary CTA, links |
| `--color-accent-hover` | `hsl(250, 90%, 48%)` | Darkened accent for hover states |
| `--color-accent-subtle` | `hsl(250, 60%, 95%)` | Light accent backgrounds |
| `--color-secondary` | `hsl(165, 80%, 42%)` | Electric teal -- secondary actions |
| `--color-surface` | `hsl(0, 0%, 100%)` | Clean white background |
| `--color-surface-dark` | `hsl(0, 0%, 8%)` | Dark sections, hero backgrounds |
| `--color-surface-raised` | `hsl(0, 0%, 100%)` | Cards on light backgrounds |
| `--color-border` | `hsl(0, 0%, 88%)` | Light borders |
| `--color-border-strong` | `hsl(0, 0%, 20%)` | Strong borders, dark mode dividers |
| `--color-success` | `hsl(145, 70%, 40%)` | Vivid success |
| `--color-warning` | `hsl(45, 90%, 50%)` | Bold warning |
| `--color-error` | `hsl(0, 75%, 55%)` | Strong error |
| `--color-info` | `hsl(210, 75%, 55%)` | Bold info |

---

## Spacing Preferences

**Density**: Standard with dramatic scale jumps
**Base unit**: 4px
**Philosophy**: Spacing creates drama through contrast. Tight internal spacing within components, generous spacing between sections. The gap between elements matters as much as the elements themselves.

| Token | Value | Usage |
|-------|-------|-------|
| `--space-xs` | `0.25rem` (4px) | Icon gaps, badge padding |
| `--space-sm` | `0.5rem` (8px) | Button padding, tight groups |
| `--space-md` | `1rem` (16px) | Card padding, standard gaps |
| `--space-lg` | `2rem` (32px) | Section internal spacing |
| `--space-xl` | `4rem` (64px) | Section separation |
| `--space-2xl` | `6rem` (96px) | Hero spacing, dramatic breaks |
| `--space-3xl` | `8rem` (128px) | Full-bleed section margins |

---

## Motion Style

**Character**: Punchy with controlled overshoot
**Philosophy**: Motion should feel powerful and decisive. Quick attacks with a slight overshoot convey confidence. Elements arrive fast and land with authority.

| Token | Value |
|-------|-------|
| `--duration-fast` | `100ms` |
| `--duration-normal` | `200ms` |
| `--duration-slow` | `400ms` |
| `--easing-default` | `cubic-bezier(0.2, 0, 0, 1)` |
| `--easing-overshoot` | `cubic-bezier(0.34, 1.4, 0.64, 1)` |
| `--easing-enter` | `cubic-bezier(0, 0, 0, 1)` |
| `--easing-exit` | `cubic-bezier(0.5, 0, 1, 1)` |

**Guidelines**:
- Button hover: scale(1.02) at `--duration-fast` with `--easing-default`
- Element entry: translate + fade with `--easing-overshoot` at `--duration-normal`
- Page transitions: fast crossfade at `--duration-normal`
- Scroll-triggered elements: slide-up with overshoot at `--duration-slow`
- Hover scale transforms add physicality
- Avoid gentle or floaty motion -- keep it decisive

---

## Shadow Depth

**Approach**: Deep, confident shadows that create strong elevation hierarchy. High opacity, clear directionality.

| Token | Value |
|-------|-------|
| `--shadow-sm` | `0 2px 4px hsla(0, 0%, 0%, 0.12)` |
| `--shadow-md` | `0 4px 12px hsla(0, 0%, 0%, 0.15)` |
| `--shadow-lg` | `0 8px 30px hsla(0, 0%, 0%, 0.2)` |
| `--shadow-xl` | `0 16px 50px hsla(0, 0%, 0%, 0.25)` |
| `--shadow-focus` | `0 0 0 3px var(--color-accent), 0 0 0 5px hsla(250, 85%, 58%, 0.25)` |

**Guidelines**:
- Cards: `--shadow-md`, elevate to `--shadow-lg` on hover
- Hero elements: `--shadow-xl` for dramatic floating effect
- Buttons: `--shadow-sm`, elevate on hover
- Modals: `--shadow-xl` with dark backdrop
- Shadow intensity reinforces hierarchy -- use the full range

---

## Border Radius

**Character**: Sharp and direct

| Token | Value |
|-------|-------|
| `--radius-none` | `0` |
| `--radius-sm` | `0.125rem` (2px) |
| `--radius-md` | `0.25rem` (4px) |
| `--radius-full` | `9999px` |

**Guidelines**:
- Buttons: `--radius-none` or `--radius-sm` -- sharp edges signal confidence
- Cards: `--radius-none` to `--radius-sm`
- Inputs: `--radius-sm`
- Tags and pills: `--radius-full` (the only rounded element)
- Hero sections: no radius, full-bleed
- The contrast between sharp rectangles and occasional pills creates visual tension

---

## Layout Philosophy

**Grid**: Bold asymmetric layouts with dramatic scale contrast
**Whitespace**: Strategic -- dense in some areas, vast in others
**Rhythm**: Dramatic vertical rhythm with oversized headings and tight body text
**Alignment**: Strong left alignment with occasional full-bleed breaks

| Token | Value |
|-------|-------|
| `--grid-columns` | `12` |
| `--grid-gutter` | `1.5rem` (24px) |
| `--grid-margin` | `2rem` (32px) |
| `--content-max-width` | `1280px` |
| `--line-height-body` | `1.6` |
| `--line-height-heading` | `1.0` |

**Patterns**:
- Headlines: oversized (4rem-8rem), tight line height (1.0), sometimes breaking the grid
- Hero sections: full-bleed dark backgrounds with massive type
- Cards: uniform height, strong borders instead of shadows for variation
- CTAs: full-width buttons, high contrast, impossible to miss
- Images: full-bleed, high contrast, cropped aggressively
- Split layouts: 50/50 or 60/40 with strong color blocking
- Scale contrast: pair 8rem headings with 1rem body text

---

## Usage Notes

**Choose Boldness when building**:
- Startup landing pages and launch sites
- Gaming and esports platforms
- Sports and fitness applications
- Entertainment and media products
- Bold marketing and campaign sites
- Conference and event platforms
- Music and nightlife products

**Avoid Boldness for**:
- Healthcare or wellness applications requiring a calming tone
- Financial services needing conservative presentation
- Accessibility-first products for elderly users
- Long-form reading experiences
- Enterprise software with dense data requirements

**Accessibility considerations**:
- High contrast palette naturally supports WCAG compliance, but verify vivid accent on white
- Tight heading line-height (1.0) may be problematic for wrapped multi-line headings -- test at mobile widths
- Oversized text benefits low-vision users but ensure responsive scaling does not break at small screens
- Overshoot animations should respect `prefers-reduced-motion` -- fall back to simple fade
- Ensure dark-on-dark sections maintain sufficient contrast for body text

---

## Example Token Overrides

```css
:root {
  /* Typography */
  --font-heading: 'Plus Jakarta Sans', system-ui, sans-serif;
  --font-body: 'Outfit', system-ui, sans-serif;
  --font-weight-heading: 800;
  --font-weight-body: 400;

  /* Color */
  --color-primary: hsl(0, 0%, 8%);
  --color-primary-inverse: hsl(0, 0%, 100%);
  --color-accent: hsl(250, 85%, 58%);
  --color-accent-hover: hsl(250, 90%, 48%);
  --color-accent-subtle: hsl(250, 60%, 95%);
  --color-secondary: hsl(165, 80%, 42%);
  --color-surface: hsl(0, 0%, 100%);
  --color-surface-dark: hsl(0, 0%, 8%);
  --color-surface-raised: hsl(0, 0%, 100%);
  --color-border: hsl(0, 0%, 88%);
  --color-border-strong: hsl(0, 0%, 20%);
  --color-success: hsl(145, 70%, 40%);
  --color-warning: hsl(45, 90%, 50%);
  --color-error: hsl(0, 75%, 55%);
  --color-info: hsl(210, 75%, 55%);

  /* Spacing */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 2rem;
  --space-xl: 4rem;
  --space-2xl: 6rem;
  --space-3xl: 8rem;

  /* Motion */
  --duration-fast: 100ms;
  --duration-normal: 200ms;
  --duration-slow: 400ms;
  --easing-default: cubic-bezier(0.2, 0, 0, 1);
  --easing-overshoot: cubic-bezier(0.34, 1.4, 0.64, 1);
  --easing-enter: cubic-bezier(0, 0, 0, 1);
  --easing-exit: cubic-bezier(0.5, 0, 1, 1);

  /* Shadows */
  --shadow-sm: 0 2px 4px hsla(0, 0%, 0%, 0.12);
  --shadow-md: 0 4px 12px hsla(0, 0%, 0%, 0.15);
  --shadow-lg: 0 8px 30px hsla(0, 0%, 0%, 0.2);
  --shadow-xl: 0 16px 50px hsla(0, 0%, 0%, 0.25);
  --shadow-focus: 0 0 0 3px var(--color-accent), 0 0 0 5px hsla(250, 85%, 58%, 0.25);

  /* Radius */
  --radius-none: 0;
  --radius-sm: 0.125rem;
  --radius-md: 0.25rem;
  --radius-full: 9999px;

  /* Layout */
  --grid-columns: 12;
  --grid-gutter: 1.5rem;
  --grid-margin: 2rem;
  --content-max-width: 1280px;
  --line-height-body: 1.6;
  --line-height-heading: 1.0;
}
```
