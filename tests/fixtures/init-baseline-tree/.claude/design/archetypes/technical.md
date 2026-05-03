# Technical Archetype

> Code-native clarity. Monospace precision meets information density. Technical treats the screen like a well-organized terminal -- every character earns its place.

---

## Font Pairing

| Role | Font | Weights | Fallback |
|------|------|---------|----------|
| **Headings / Code** | JetBrains Mono | 400, 500, 700 | 'Fira Code', 'SF Mono', monospace |
| **Body** | Inter | 400, 500, 600 | system-ui, sans-serif |

**Rationale**: JetBrains Mono is the primary visual identity -- its ligatures, distinct character shapes (0/O, 1/l/I), and increased x-height make it ideal for technical headings and all code contexts. Inter provides clean, highly legible body text with tabular figures and a neutral character that stays out of the way of the monospace personality.

**Loading**: Import from Google Fonts with `display=swap`. Subset to `latin` for performance.

```
https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600&display=swap
```

**Note on Inter**: While Inter appears in other design systems, it serves a distinct supporting role here. The monospace font is the dominant visual identity. Inter functions as a neutral substrate -- body text that disappears so the code-forward personality of JetBrains Mono can dominate.

---

## Color Palette Strategy

**Temperature**: Cool neutral
**Saturation**: Very low for UI chrome (0-10%), moderate for syntax-like semantic colors (40-60%)
**Approach**: Slate/gray structural palette inspired by code editor themes. Semantic colors borrow from syntax highlighting conventions -- green for success/strings, blue for info/functions, yellow for warnings, red for errors.

| Token | Value | Usage |
|-------|-------|-------|
| `--color-primary` | `hsl(215, 15%, 18%)` | Primary text, near-black slate |
| `--color-primary-light` | `hsl(215, 10%, 45%)` | Secondary text, comments |
| `--color-accent` | `hsl(215, 55%, 55%)` | Steel blue -- links, interactive elements |
| `--color-accent-subtle` | `hsl(215, 30%, 95%)` | Light blue tint for selected/active |
| `--color-secondary` | `hsl(170, 45%, 45%)` | Teal -- secondary actions, string-like |
| `--color-surface` | `hsl(215, 12%, 97%)` | Light gray background |
| `--color-surface-raised` | `hsl(0, 0%, 100%)` | Cards, panels |
| `--color-surface-code` | `hsl(215, 15%, 95%)` | Code block backgrounds |
| `--color-surface-dark` | `hsl(215, 20%, 13%)` | Dark mode surfaces, terminal areas |
| `--color-border` | `hsl(215, 10%, 85%)` | Structural borders |
| `--color-border-strong` | `hsl(215, 12%, 70%)` | Active borders, focus states |
| `--color-success` | `hsl(145, 50%, 40%)` | Green -- success, pass, string |
| `--color-warning` | `hsl(45, 65%, 50%)` | Yellow -- warning, caution |
| `--color-error` | `hsl(0, 55%, 50%)` | Red -- error, fail, deletion |
| `--color-info` | `hsl(215, 55%, 55%)` | Blue -- info (matches accent) |
| `--color-syntax-keyword` | `hsl(280, 45%, 55%)` | Purple -- keyword highlighting |
| `--color-syntax-function` | `hsl(215, 55%, 55%)` | Blue -- function highlighting |
| `--color-syntax-string` | `hsl(145, 50%, 40%)` | Green -- string highlighting |
| `--color-syntax-comment` | `hsl(215, 10%, 55%)` | Gray -- comment highlighting |

---

## Spacing Preferences

**Density**: Tight and information-dense
**Base unit**: 4px
**Philosophy**: Maximize information per viewport. Tight spacing reduces scrolling and keeps related data visually grouped. Every pixel of whitespace must justify its existence by aiding scanability.

| Token | Value | Usage |
|-------|-------|-------|
| `--space-xs` | `0.25rem` (4px) | Icon gaps, inline code padding |
| `--space-sm` | `0.5rem` (8px) | Cell padding, tight groups |
| `--space-md` | `0.75rem` (12px) | Card padding, list item spacing |
| `--space-lg` | `1rem` (16px) | Section gaps, form field spacing |
| `--space-xl` | `1.5rem` (24px) | Panel separation |
| `--space-2xl` | `2rem` (32px) | Page section boundaries |

---

## Motion Style

**Character**: Precise and instantaneous
**Philosophy**: Motion should be near-invisible. Transitions exist only to prevent visual jarring -- they are functional, not decorative. Linear easing matches the mechanical precision of the archetype.

| Token | Value |
|-------|-------|
| `--duration-fast` | `75ms` |
| `--duration-normal` | `100ms` |
| `--duration-slow` | `200ms` |
| `--easing-default` | `linear` |
| `--easing-enter` | `cubic-bezier(0, 0, 0.2, 1)` |
| `--easing-exit` | `cubic-bezier(0.4, 0, 1, 1)` |

**Guidelines**:
- State changes (hover, focus): `--duration-fast` with `linear` -- nearly instant
- Panel expand/collapse: `--duration-normal`
- Dropdown/popover: `--duration-normal` with `--easing-enter`
- Avoid all spring, bounce, or overshoot effects
- Avoid opacity fades longer than `--duration-slow`
- Loading indicators: simple spinner or progress bar, no playful animations
- Motion should feel like a state machine changing states, not an animation

---

## Shadow Depth

**Approach**: Flat design preferred. Shadows are rarely used. When needed, they are minimal and functional -- indicating focus or layering, not decoration.

| Token | Value |
|-------|-------|
| `--shadow-sm` | `0 1px 2px hsla(215, 15%, 18%, 0.05)` |
| `--shadow-md` | `0 2px 4px hsla(215, 15%, 18%, 0.08)` |
| `--shadow-focus` | `0 0 0 2px var(--color-accent)` |
| `--shadow-inset` | `inset 0 1px 2px hsla(215, 15%, 18%, 0.06)` |

**Guidelines**:
- Cards and panels: border only, no shadow (use `1px solid var(--color-border)`)
- Dropdowns and popovers: `--shadow-md` for layering indication
- Code blocks: `--shadow-inset` for a recessed, terminal-like feel
- Focus rings: solid 2px outline using accent color
- Modals: `--shadow-md` only, with a subtle backdrop
- The flat aesthetic means borders do most of the separation work

---

## Border Radius

**Character**: Minimal and technical

| Token | Value |
|-------|-------|
| `--radius-sm` | `0.125rem` (2px) |
| `--radius-md` | `0.25rem` (4px) |
| `--radius-full` | `9999px` |

**Guidelines**:
- Buttons: `--radius-sm`
- Cards and panels: `--radius-sm` to `--radius-md`
- Inputs: `--radius-sm`
- Code blocks: `--radius-md`
- Tags and status indicators: `--radius-full`
- Most elements use `--radius-sm` -- the overall aesthetic is nearly square
- Avoid any radius larger than `--radius-md` on rectangular elements

---

## Layout Philosophy

**Grid**: Tight, systematic grid optimized for information density
**Whitespace**: Minimal -- functional only
**Rhythm**: Strict vertical rhythm on a tight baseline grid
**Alignment**: Hard left alignment, monospace-width columns where possible

| Token | Value |
|-------|-------|
| `--grid-columns` | `12` |
| `--grid-gutter` | `0.75rem` (12px) |
| `--grid-margin` | `1rem` (16px) |
| `--content-max-width` | `1400px` |
| `--sidebar-width` | `260px` |
| `--line-height-body` | `1.55` |
| `--line-height-heading` | `1.2` |
| `--line-height-code` | `1.5` |

**Patterns**:
- Dashboard: sidebar + main content, resizable panels
- Data tables: compact rows, sticky headers, sortable columns
- Code views: line numbers, syntax highlighting, scrollable containers
- Documentation: sidebar navigation, narrow content column (max 720px), code examples
- Terminal/console: dark background, monospace, scrollback buffer
- Status pages: compact cards with status indicators (colored dots)
- Navigation: text-only sidebar with keyboard shortcuts displayed
- Split views: resizable vertical or horizontal panes (editor + preview)

---

## Usage Notes

**Choose Technical when building**:
- Developer tools and IDEs
- CLI tools with web interfaces
- Documentation sites and knowledge bases
- API platforms and developer portals
- Code editors and review tools
- System monitoring and observability dashboards
- Database management interfaces
- DevOps and infrastructure tools

**Avoid Technical for**:
- Consumer-facing marketing sites
- Children's or family products
- Wellness and lifestyle applications
- Luxury or fashion brands
- Products targeting non-technical audiences

**Accessibility considerations**:
- High information density demands clear visual hierarchy -- use weight and size contrast in headings
- Monospace fonts at small sizes can be harder to read for users with dyslexia -- maintain minimum 14px for code
- Low-saturation palette naturally provides sufficient contrast, but verify gray-on-gray combinations
- Compact spacing requires precise focus indicators -- the 2px solid outline is essential for keyboard navigation
- Ensure resizable panels respect minimum width constraints for content readability
- Code blocks with syntax highlighting must not rely on color alone -- provide alternative indicators where possible

---

## Example Token Overrides

```css
:root {
  /* Typography */
  --font-heading: 'JetBrains Mono', 'Fira Code', 'SF Mono', monospace;
  --font-body: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', 'SF Mono', monospace;
  --font-weight-heading: 700;
  --font-weight-body: 400;

  /* Color */
  --color-primary: hsl(215, 15%, 18%);
  --color-primary-light: hsl(215, 10%, 45%);
  --color-accent: hsl(215, 55%, 55%);
  --color-accent-subtle: hsl(215, 30%, 95%);
  --color-secondary: hsl(170, 45%, 45%);
  --color-surface: hsl(215, 12%, 97%);
  --color-surface-raised: hsl(0, 0%, 100%);
  --color-surface-code: hsl(215, 15%, 95%);
  --color-surface-dark: hsl(215, 20%, 13%);
  --color-border: hsl(215, 10%, 85%);
  --color-border-strong: hsl(215, 12%, 70%);
  --color-success: hsl(145, 50%, 40%);
  --color-warning: hsl(45, 65%, 50%);
  --color-error: hsl(0, 55%, 50%);
  --color-info: hsl(215, 55%, 55%);
  --color-syntax-keyword: hsl(280, 45%, 55%);
  --color-syntax-function: hsl(215, 55%, 55%);
  --color-syntax-string: hsl(145, 50%, 40%);
  --color-syntax-comment: hsl(215, 10%, 55%);

  /* Spacing */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 0.75rem;
  --space-lg: 1rem;
  --space-xl: 1.5rem;
  --space-2xl: 2rem;

  /* Motion */
  --duration-fast: 75ms;
  --duration-normal: 100ms;
  --duration-slow: 200ms;
  --easing-default: linear;
  --easing-enter: cubic-bezier(0, 0, 0.2, 1);
  --easing-exit: cubic-bezier(0.4, 0, 1, 1);

  /* Shadows */
  --shadow-sm: 0 1px 2px hsla(215, 15%, 18%, 0.05);
  --shadow-md: 0 2px 4px hsla(215, 15%, 18%, 0.08);
  --shadow-focus: 0 0 0 2px var(--color-accent);
  --shadow-inset: inset 0 1px 2px hsla(215, 15%, 18%, 0.06);

  /* Radius */
  --radius-sm: 0.125rem;
  --radius-md: 0.25rem;
  --radius-full: 9999px;

  /* Layout */
  --grid-columns: 12;
  --grid-gutter: 0.75rem;
  --grid-margin: 1rem;
  --content-max-width: 1400px;
  --sidebar-width: 260px;
  --line-height-body: 1.55;
  --line-height-heading: 1.2;
  --line-height-code: 1.5;
}
```
