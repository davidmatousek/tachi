# Design Quality Standards

<!-- Stack-agnostic core rules — loaded by ALL agents working on UI code -->
<!-- Prevents "AI slop" by codifying premium design standards -->

These rules apply to ALL agents generating UI code, regardless of stack.
Follow every section as a hard constraint. Do not deviate without explicit user override.

---

## 1. Aesthetic Philosophy Step

Before writing ANY UI code, answer these four questions. Document answers as a code comment at the top of the first UI file you create or modify.

1. **What is the dominant visual mood?** (e.g., professional, playful, editorial, brutalist, minimal, warm-corporate)
2. **What typeface pairing communicates this mood?** (choose specific fonts, not generic ones)
3. **What is the color temperature?** (warm / cool / neutral — this guides your palette)
4. **What level of visual density is appropriate?** (spacious / balanced / compact)

If the project has a `brands/*/brand.md` file, derive answers from it. If an archetype is active in `.claude/design/archetypes/`, use it as a starting point. Otherwise, propose answers and confirm with the user before proceeding.

---

## 2. Banned Defaults

These patterns produce recognizable "AI-generated" output. NEVER use them as primary choices.

### Banned Primary Fonts
- Inter
- Roboto
- Arial
- Open Sans
- Lato

These fonts ARE permitted as fallbacks in a font-stack (e.g., `"IBM Plex Sans", "Inter", sans-serif`), but NEVER as the first-choice font.

**Use instead**: IBM Plex Sans, Source Sans 3, DM Sans, Geist, Instrument Sans, Plus Jakarta Sans, Outfit, Satoshi, General Sans, Manrope, or any font that matches the Aesthetic Philosophy answers.

### Banned Gradient Patterns
- Purple-to-blue gradients as primary palette
- Rainbow gradients as primary palette
- Neon color transitions

### Banned Backgrounds
- Solid `#ffffff` or `#fff` as the page background
- Solid `#f5f5f5` or `#fafafa` as the page background

### Banned Patterns
- Uniform `16px` border-radius on all elements (vary radius by component purpose)
- Identical padding on every component regardless of hierarchy

---

## 3. Typography Hierarchy

### Display-to-Body Ratio
- The ratio of the largest display heading to body text MUST be 3x or greater.
- Example: if body is `16px`, display headings must be `48px` or larger.

### Font Weight Range
- Body text: **300-400** (light to regular)
- Headings: **600-800** (semi-bold to extra-bold)
- Use weight contrast to create clear visual hierarchy between levels.

### Font Pairing
- Maximum **2 font families**: one for headings, one for body.
- A single-family approach (different weights) is also acceptable.
- NEVER use 3+ unrelated font families on the same page.

### Line Height
- Body text: **1.5 - 1.75**
- Headings (H1-H4): **1.1 - 1.3**
- Display text: **1.0 - 1.2**
- Captions and small text: **1.4 - 1.6**

### Type Scale
Define a consistent scale. Recommended starting point:
- `display`: 48-72px
- `h1`: 36-48px
- `h2`: 28-36px
- `h3`: 22-28px
- `h4`: 18-22px
- `body`: 16px
- `small`: 14px
- `caption`: 12px

---

## 4. Spacing System

### 8pt Grid
All spacing values MUST be multiples of 4px. The primary scale:

```
4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96
```

NEVER use arbitrary spacing values (e.g., 7px, 13px, 15px, 18px, 22px, 50px).

### Internal vs External Spacing
- Internal padding (inside a component) MUST be less than or equal to external margin (between components).
- Components should appear grouped, not floating in empty space.

### Vertical Rhythm
- Maintain consistent vertical spacing between sections.
- Section gaps should be 2-3x the spacing between elements within a section.
- Example: if intra-section spacing is `16px`, inter-section spacing is `32-48px`.

---

## 5. Color Strategy

### Semantic Naming
Use purpose-based names, NEVER raw color values as identifiers:

| Token Name | Purpose |
|------------|---------|
| `primary` | Brand color, primary actions |
| `secondary` | Supporting elements |
| `accent` | Highlights, calls to action |
| `muted` | Subdued backgrounds, secondary text |
| `destructive` | Errors, delete actions |
| `success` | Confirmations, positive states |
| `warning` | Cautions, pending states |
| `info` | Informational notices |

NEVER name tokens after their color value (e.g., `blue-500`, `gray-200`). Always name by purpose.

### 3-Layer Token System
1. **Base layer** (raw values): `--color-blue-600: oklch(0.55 0.2 260)`
2. **Semantic layer** (purpose): `--color-primary: var(--color-blue-600)`
3. **Component layer** (specific use): `--button-bg: var(--color-primary)`

Agents MUST define all three layers. Never reference base tokens directly in components.

### Dominant + Accent Rule
- ONE dominant color for primary brand and actions.
- 1-2 accent colors maximum for highlights and secondary actions.
- All other colors are neutrals and semantic status colors.

### Contrast Requirements (WCAG AA)
- Normal text (below 18px or 14px bold): **4.5:1** contrast ratio minimum
- Large text (18px+ or 14px+ bold): **3:1** contrast ratio minimum
- UI components and graphical objects: **3:1** contrast ratio minimum
- Decorative elements: no contrast requirement

---

## 6. Component State Completeness

Every interactive component MUST implement these 6 states:

| State | Requirement |
|-------|-------------|
| `default` | Resting appearance, no user interaction |
| `hover` | Visual change on mouse-over (cursor pointer for clickable elements) |
| `focus-visible` | Keyboard focus indicator — MUST use outline, NOT just a color change |
| `active` / `pressed` | Momentary feedback during click or tap |
| `disabled` | Visually muted, non-interactive, cursor not-allowed |
| `loading` | Skeleton, spinner, or progress indicator replacing content |

### Rules
- Each state MUST be visually distinct from every other state.
- `focus-visible` MUST use an outline (e.g., `2px solid` with offset) — never rely solely on color change, background change, or shadow.
- `disabled` MUST reduce opacity or desaturate, AND set `pointer-events: none` or `cursor: not-allowed`.
- `loading` MUST prevent duplicate submissions (disable interaction while loading).

---

## 7. Background Rules

### Page Backgrounds
- NEVER use solid white (`#fff`, `#ffffff`) as the page background.
- NEVER use solid light gray (`#f5f5f5`, `#fafafa`) as the page background.
- USE layered backgrounds instead:
  - Subtle gradient (e.g., warm off-white to cool off-white)
  - Tinted neutral (e.g., `oklch(0.985 0.005 80)` — barely warm white)
  - Noise texture overlay at very low opacity
  - Dot grid or subtle pattern at very low opacity

### Card/Surface Hierarchy
- Card backgrounds MUST contrast with the page background.
- Use 2-3 surface levels:
  - `surface-0`: page background (base)
  - `surface-1`: cards, panels (slightly elevated)
  - `surface-2`: modals, popovers (highest elevation)
- Each surface level should be progressively lighter (light mode) or darker (dark mode).

---

## 8. Shadow System

### Named Shadow Levels
Define a maximum of 3-5 named shadow levels:

| Level | Use Case |
|-------|----------|
| `sm` | Subtle depth for inputs, small controls |
| `md` | Cards, dropdowns, default elevation |
| `lg` | Modals, popovers, floating elements |
| `xs` (optional) | Barely visible, inner depth cues |
| `xl` (optional) | Dramatic elevation for hero elements |

### Rules
- Shadow direction MUST be consistent across the entire project (typically light from top-left).
- Shadow color MUST be a desaturated, semi-transparent dark — NEVER pure black (`rgba(0,0,0,x)`). Use a tinted shadow that matches the color scheme (e.g., `oklch(0.2 0.02 260 / 0.1)`).
- NEVER use more than 5 shadow levels — if you need more, the visual hierarchy is too complex.
- Combine shadow with subtle border for better definition on light backgrounds.
