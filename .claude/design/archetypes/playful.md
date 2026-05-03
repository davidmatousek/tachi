# Playful Archetype

> Joy in every interaction. Bouncy motion, vibrant color, rounded everything. Playful turns functional software into a delightful experience.

---

## Font Pairing

| Role | Font | Weights | Fallback |
|------|------|---------|----------|
| **Headings** | Baloo 2 | 500, 600, 700, 800 | system-ui, sans-serif |
| **Body** | Fredoka | 400, 500, 600 | system-ui, sans-serif |

**Rationale**: Baloo 2's bubbly, rounded letterforms bring instant friendliness to headings -- its thick strokes and open counters are readable even at display sizes. Fredoka's rounded geometric forms create a cohesive all-rounded typographic system with excellent legibility for younger and casual audiences.

**Loading**: Import from Google Fonts with `display=swap`. Subset to `latin` for performance.

```
https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Fredoka:wght@400;500;600&display=swap
```

---

## Color Palette Strategy

**Temperature**: Warm-cool mix (multi-temperature)
**Saturation**: High (65-90% saturation)
**Approach**: Rainbow-derived palette using multiple hues in harmony. Each color is a character in the palette, not just a functional assignment. Colors are vivid but never garish.

| Token | Value | Usage |
|-------|-------|-------|
| `--color-primary` | `hsl(260, 50%, 25%)` | Deep purple text on light backgrounds |
| `--color-primary-light` | `hsl(260, 30%, 45%)` | Secondary text |
| `--color-accent-1` | `hsl(340, 75%, 55%)` | Coral pink -- primary CTA |
| `--color-accent-2` | `hsl(170, 65%, 45%)` | Teal -- secondary actions |
| `--color-accent-3` | `hsl(45, 85%, 55%)` | Sunny yellow -- highlights, badges |
| `--color-accent-4` | `hsl(260, 65%, 60%)` | Violet -- tertiary, tags |
| `--color-accent-5` | `hsl(25, 80%, 55%)` | Tangerine -- alerts, callouts |
| `--color-surface` | `hsl(260, 30%, 98%)` | Very light lavender background |
| `--color-surface-raised` | `hsl(0, 0%, 100%)` | White cards |
| `--color-surface-fun` | `hsl(45, 80%, 96%)` | Warm yellow tint sections |
| `--color-border` | `hsl(260, 20%, 88%)` | Soft lavender borders |
| `--color-border-strong` | `hsl(260, 25%, 75%)` | Emphasis borders |
| `--color-success` | `hsl(145, 65%, 45%)` | Bright green |
| `--color-warning` | `hsl(35, 85%, 55%)` | Warm orange |
| `--color-error` | `hsl(0, 70%, 55%)` | Friendly red |
| `--color-info` | `hsl(200, 70%, 52%)` | Sky blue |

---

## Spacing Preferences

**Density**: Generous and airy
**Base unit**: 4px
**Philosophy**: Give everything room to breathe and bounce. Generous padding makes interactive elements easy to tap and creates a sense of open, uncluttered fun. Asymmetric spacing adds visual playfulness.

| Token | Value | Usage |
|-------|-------|-------|
| `--space-xs` | `0.5rem` (8px) | Icon gaps, badge padding |
| `--space-sm` | `0.75rem` (12px) | Tight groups, tag spacing |
| `--space-md` | `1.5rem` (24px) | Card padding, component gaps |
| `--space-lg` | `2.5rem` (40px) | Section internal spacing |
| `--space-xl` | `4rem` (64px) | Section separation |
| `--space-2xl` | `5rem` (80px) | Page section boundaries |

---

## Motion Style

**Character**: Springy with playful overshoot
**Philosophy**: Motion is a core part of the personality. Elements bounce into place, wiggle on interaction, and exit with a cheerful pop. Movement creates delight without delaying task completion.

| Token | Value |
|-------|-------|
| `--duration-fast` | `150ms` |
| `--duration-normal` | `300ms` |
| `--duration-slow` | `500ms` |
| `--duration-bounce` | `600ms` |
| `--easing-default` | `cubic-bezier(0.4, 0, 0.2, 1)` |
| `--easing-bounce` | `cubic-bezier(0.34, 1.56, 0.64, 1)` |
| `--easing-spring` | `cubic-bezier(0.2, 1.4, 0.4, 1)` |
| `--easing-enter` | `cubic-bezier(0.0, 0, 0.2, 1)` |
| `--easing-exit` | `cubic-bezier(0.4, 0, 1, 1)` |

**Guidelines**:
- Button hover: scale(1.05) with `--easing-bounce` at `--duration-normal`
- Element entry: scale(0.9) to scale(1) with `--easing-spring` at `--duration-bounce`
- Success states: brief scale pulse (1.0 -> 1.1 -> 1.0) with `--easing-bounce`
- Loading states: rhythmic bounce or wobble animation
- Toggle switches: overshoot snap with `--easing-bounce`
- Hover effects can include rotation (1-3 degrees) for playfulness
- Must respect `prefers-reduced-motion` -- fall back to opacity-only transitions

---

## Shadow Depth

**Approach**: Bouncy, color-tinted shadows that reinforce the multi-hue palette. Shadows are a decorative element, not just a depth cue.

| Token | Value |
|-------|-------|
| `--shadow-sm` | `0 2px 4px hsla(260, 50%, 25%, 0.08), 0 1px 2px hsla(340, 75%, 55%, 0.05)` |
| `--shadow-md` | `0 4px 12px hsla(260, 50%, 25%, 0.1), 0 2px 4px hsla(340, 75%, 55%, 0.06)` |
| `--shadow-lg` | `0 8px 24px hsla(260, 50%, 25%, 0.12), 0 4px 8px hsla(340, 75%, 55%, 0.08)` |
| `--shadow-fun` | `4px 4px 0 var(--color-accent-4)` |
| `--shadow-focus` | `0 0 0 3px var(--color-surface), 0 0 0 5px var(--color-accent-1)` |

**Guidelines**:
- Cards: `--shadow-sm` default, `--shadow-md` on hover
- Feature callouts: `--shadow-fun` for a comic-book pop effect
- Modals: `--shadow-lg` with a semi-transparent colorful backdrop
- Color-tinted shadows create a warmer, more dimensional feel
- The hard offset shadow (`--shadow-fun`) can rotate between accent colors

---

## Border Radius

**Character**: Fully rounded and bubbly

| Token | Value |
|-------|-------|
| `--radius-sm` | `0.5rem` (8px) |
| `--radius-md` | `0.75rem` (12px) |
| `--radius-lg` | `1rem` (16px) |
| `--radius-xl` | `1.5rem` (24px) |
| `--radius-full` | `9999px` |

**Guidelines**:
- Buttons: `--radius-full` -- always pill-shaped
- Cards: `--radius-lg` to `--radius-xl`
- Inputs: `--radius-lg`
- Images: `--radius-lg` or `--radius-full` for avatars
- Tags and badges: `--radius-full`
- Containers and sections: `--radius-lg`
- Sharp corners are never used -- everything is rounded

---

## Layout Philosophy

**Grid**: Flexible with intentional asymmetry and organic arrangement
**Whitespace**: Generous, creating a sense of openness and room to play
**Rhythm**: Varied vertical rhythm -- not rigidly uniform, allowing visual surprise
**Alignment**: Center-biased with occasional offset elements for energy

| Token | Value |
|-------|-------|
| `--grid-columns` | `12` |
| `--grid-gutter` | `1.5rem` (24px) |
| `--grid-margin` | `2rem` (32px) |
| `--content-max-width` | `1120px` |
| `--line-height-body` | `1.65` |
| `--line-height-heading` | `1.2` |

**Patterns**:
- Card layouts: staggered or masonry with varied card heights
- Hero sections: large illustrations or character graphics, centered CTA
- Color blocking: alternating section background colors from the palette
- Decorative elements: dots, squiggles, confetti as background patterns
- Callouts: colored background cards with icon + text, rounded corners
- Navigation: icon-heavy, large touch targets, color-coded sections
- Empty states: friendly illustrations with encouraging messages

---

## Usage Notes

**Choose Playful when building**:
- Children's educational products and games
- Creative tools (drawing, music, storytelling)
- Casual and social gaming platforms
- Social and community apps for younger audiences
- Party and event planning applications
- Pet and animal-related products
- Reward and gamification systems

**Avoid Playful for**:
- Enterprise B2B software
- Financial services or banking
- Healthcare and medical applications
- Legal or compliance-oriented tools
- Luxury or premium brand experiences
- Developer tools and technical platforms

**Accessibility considerations**:
- Multi-color palette requires individual contrast verification for every color-on-background combination
- Bouncy animations must always respect `prefers-reduced-motion` with non-animated fallbacks
- Large radius and generous spacing naturally support motor-impaired users with big touch targets
- Colorful UI must not rely solely on color to convey information -- always pair with icons or text labels
- Ensure the decorative elements (dots, squiggles) do not interfere with screen readers -- use `aria-hidden="true"`
- Test rainbow palette for color-blind users -- ensure information is distinguishable without color alone

---

## Example Token Overrides

```css
:root {
  /* Typography */
  --font-heading: 'Baloo 2', system-ui, sans-serif;
  --font-body: 'Fredoka', system-ui, sans-serif;
  --font-weight-heading: 700;
  --font-weight-body: 400;

  /* Color */
  --color-primary: hsl(260, 50%, 25%);
  --color-primary-light: hsl(260, 30%, 45%);
  --color-accent-1: hsl(340, 75%, 55%);
  --color-accent-2: hsl(170, 65%, 45%);
  --color-accent-3: hsl(45, 85%, 55%);
  --color-accent-4: hsl(260, 65%, 60%);
  --color-accent-5: hsl(25, 80%, 55%);
  --color-surface: hsl(260, 30%, 98%);
  --color-surface-raised: hsl(0, 0%, 100%);
  --color-surface-fun: hsl(45, 80%, 96%);
  --color-border: hsl(260, 20%, 88%);
  --color-border-strong: hsl(260, 25%, 75%);
  --color-success: hsl(145, 65%, 45%);
  --color-warning: hsl(35, 85%, 55%);
  --color-error: hsl(0, 70%, 55%);
  --color-info: hsl(200, 70%, 52%);

  /* Spacing */
  --space-xs: 0.5rem;
  --space-sm: 0.75rem;
  --space-md: 1.5rem;
  --space-lg: 2.5rem;
  --space-xl: 4rem;
  --space-2xl: 5rem;

  /* Motion */
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
  --duration-bounce: 600ms;
  --easing-default: cubic-bezier(0.4, 0, 0.2, 1);
  --easing-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
  --easing-spring: cubic-bezier(0.2, 1.4, 0.4, 1);
  --easing-enter: cubic-bezier(0.0, 0, 0.2, 1);
  --easing-exit: cubic-bezier(0.4, 0, 1, 1);

  /* Shadows */
  --shadow-sm: 0 2px 4px hsla(260, 50%, 25%, 0.08), 0 1px 2px hsla(340, 75%, 55%, 0.05);
  --shadow-md: 0 4px 12px hsla(260, 50%, 25%, 0.1), 0 2px 4px hsla(340, 75%, 55%, 0.06);
  --shadow-lg: 0 8px 24px hsla(260, 50%, 25%, 0.12), 0 4px 8px hsla(340, 75%, 55%, 0.08);
  --shadow-fun: 4px 4px 0 var(--color-accent-4);
  --shadow-focus: 0 0 0 3px var(--color-surface), 0 0 0 5px var(--color-accent-1);

  /* Radius */
  --radius-sm: 0.5rem;
  --radius-md: 0.75rem;
  --radius-lg: 1rem;
  --radius-xl: 1.5rem;
  --radius-full: 9999px;

  /* Layout */
  --grid-columns: 12;
  --grid-gutter: 1.5rem;
  --grid-margin: 2rem;
  --content-max-width: 1120px;
  --line-height-body: 1.65;
  --line-height-heading: 1.2;
}
```
