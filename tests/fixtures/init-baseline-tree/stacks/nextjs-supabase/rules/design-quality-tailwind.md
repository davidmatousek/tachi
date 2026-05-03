# Tailwind v4 Design Quality — Next.js + Supabase

<!-- Stack-specific supplement to .claude/rules/design-quality.md -->
<!-- Loaded when the nextjs-supabase pack is active -->

This file provides Tailwind v4 implementation details for the core design quality rules.
Read `.claude/rules/design-quality.md` first — this file supplements, not replaces, those rules.

---

## Import Path

Next.js uses `app/globals.css` for the Tailwind `@theme` directive and global styles.
All `@theme` token definitions go in this file.

```css
/* app/globals.css */
@import "tailwindcss";

@theme {
  /* Token definitions here */
}
```

---

## 1. Micro-Interaction Patterns

### Button Hover / Active

```html
<button class="
  bg-(--color-primary) text-(--color-primary-foreground)
  hover:scale-[1.02] hover:shadow-md hover:bg-(--color-primary-hover)
  active:scale-[0.98] active:shadow-sm
  focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-(--color-primary)
  disabled:opacity-50 disabled:pointer-events-none
  transition-all duration-200 ease-out
">
  Submit
</button>
```

- `hover:scale-[1.02]` — subtle lift on hover
- `active:scale-[0.98]` — press-down feedback on click
- `hover:shadow-md` — elevation change reinforces the lift
- Combine scale + shadow + background shift for a layered hover effect

### Card Hover

```html
<div class="
  bg-(--surface-1) rounded-lg shadow-sm border border-(--border)
  hover:shadow-lg hover:-translate-y-0.5
  transition-all duration-200 ease-out
">
  <!-- Card content -->
</div>
```

- `hover:shadow-lg` — elevation increases on hover
- `hover:-translate-y-0.5` — physical lift reinforces the shadow change
- Keep `duration-200` for cards — fast enough to feel responsive, slow enough to notice

### Link Underline Animation

```html
<a class="
  text-(--color-primary)
  underline decoration-1 underline-offset-4
  hover:underline-offset-2 hover:decoration-2
  transition-all duration-150 ease-out
">
  Learn more
</a>
```

- Underline tightens toward text on hover (`offset-4` to `offset-2`)
- Decoration thickens (`decoration-1` to `decoration-2`)
- Combined effect draws the eye without layout shift

### Input Focus Ring

```html
<input class="
  bg-(--surface-1) border border-(--border) rounded-md px-3 py-2
  placeholder:text-(--color-muted-foreground)
  focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-(--color-primary)
  focus-visible:border-(--color-primary)
  disabled:opacity-50 disabled:cursor-not-allowed
  transition-colors duration-150
" />
```

- `focus-visible:ring-2` — visible keyboard focus indicator (WCAG requirement)
- `focus-visible:ring-offset-2` — gap between element and ring for clarity
- `ring` is outline-based, not box-shadow, so it does not affect layout

### Page Load Stagger

Use CSS custom properties for stagger delays. Define in your `@theme` or as inline styles:

```css
/* app/globals.css — inside @theme or as utility */
@layer utilities {
  .stagger-1 { animation-delay: 50ms; }
  .stagger-2 { animation-delay: 100ms; }
  .stagger-3 { animation-delay: 150ms; }
  .stagger-4 { animation-delay: 200ms; }
  .stagger-5 { animation-delay: 250ms; }
}
```

```html
<div class="animate-fade-in-up stagger-1 opacity-0 fill-mode-forwards">Item 1</div>
<div class="animate-fade-in-up stagger-2 opacity-0 fill-mode-forwards">Item 2</div>
<div class="animate-fade-in-up stagger-3 opacity-0 fill-mode-forwards">Item 3</div>
```

Define the keyframe in `@theme`:

```css
@theme {
  --animate-fade-in-up: fade-in-up 0.4s ease-out;
}

@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

---

## 2. Motion Variants

### Transition Durations

| Token | Duration | Use Case |
|-------|----------|----------|
| `duration-100` | 100ms | Micro-feedback (active press) |
| `duration-150` | 150ms | Color changes, opacity, focus rings |
| `duration-200` | 200ms | Default for most interactions (hover, scale) |
| `duration-300` | 300ms | Card transitions, layout shifts |
| `duration-500` | 500ms | Page-level transitions, modals |

### Easing Functions

| Utility | Curve | Use Case |
|---------|-------|----------|
| `ease-out` | `cubic-bezier(0, 0, 0.2, 1)` | Elements entering view, hover effects |
| `ease-in` | `cubic-bezier(0.4, 0, 1, 1)` | Elements leaving view |
| `ease-in-out` | `cubic-bezier(0.4, 0, 0.2, 1)` | Elements that move on screen (toggles, slides) |

Custom easings for polished feel (define in `@theme`):

```css
@theme {
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-smooth: cubic-bezier(0.25, 0.1, 0.25, 1);
}
```

### Reduced Motion Accessibility

ALWAYS provide `motion-safe:` and `motion-reduce:` variants:

```html
<div class="
  motion-safe:hover:-translate-y-0.5
  motion-safe:transition-all motion-safe:duration-200
  motion-reduce:transition-none
">
  <!-- Content -->
</div>
```

Rules:
- Wrap ALL transform animations with `motion-safe:` — users with vestibular disorders must not see movement.
- Opacity and color transitions are generally safe and do not require `motion-safe:`.
- `motion-reduce:transition-none` ensures zero animation for users who prefer reduced motion.
- Test with `prefers-reduced-motion: reduce` enabled in browser dev tools.

---

## 3. Tailwind v4 Utilities by Design Rule Section

### Typography Hierarchy (Section 3)

```html
<!-- Display heading: 48px+, weight 700-800, tight line-height -->
<h1 class="text-5xl font-extrabold leading-tight tracking-tight">
  Display Heading
</h1>

<!-- Body: 16px, weight 400, relaxed line-height -->
<p class="text-base font-normal leading-relaxed">
  Body text with comfortable reading line height.
</p>

<!-- Font pairing via next/font -->
<!-- Import in layout.tsx, apply via CSS variable -->
```

Use `next/font` for font loading in Next.js:

```tsx
// app/layout.tsx
import { DM_Sans, DM_Serif_Display } from "next/font/google";

const heading = DM_Serif_Display({
  subsets: ["latin"],
  weight: ["400"],
  variable: "--font-heading",
});

const body = DM_Sans({
  subsets: ["latin"],
  weight: ["300", "400", "500", "700"],
  variable: "--font-body",
});
```

Then reference in `@theme`:

```css
@theme {
  --font-heading: var(--font-heading);
  --font-body: var(--font-body);
}
```

### Spacing System (Section 4)

Tailwind v4 default spacing maps directly to the 8pt grid. Use these utilities:

| Class | Value | Grid Multiple |
|-------|-------|---------------|
| `p-1` | 4px | 1x |
| `p-2` | 8px | 2x |
| `p-3` | 12px | 3x |
| `p-4` | 16px | 4x |
| `p-5` | 20px | 5x |
| `p-6` | 24px | 6x |
| `p-8` | 32px | 8x |
| `p-10` | 40px | 10x |
| `p-12` | 48px | 12x |
| `p-16` | 64px | 16x |
| `p-20` | 80px | 20x |
| `p-24` | 96px | 24x |

NEVER use arbitrary spacing values like `p-[7px]` or `mt-[13px]`. If the design calls for a non-standard value, add it to `@theme` as a named token.

### Color Strategy (Section 5)

Define the 3-layer token system in `@theme`:

```css
@theme {
  /* Base layer — raw oklch values */
  --color-blue-600: oklch(0.55 0.2 260);
  --color-emerald-600: oklch(0.6 0.17 160);
  --color-red-600: oklch(0.55 0.22 25);

  /* Semantic layer — purpose-based */
  --color-primary: var(--color-blue-600);
  --color-success: var(--color-emerald-600);
  --color-destructive: var(--color-red-600);

  /* Component layer — applied in component classes */
  /* Use bg-(--color-primary) in markup */
}
```

Use oklch for perceptually uniform color manipulation. Tailwind v4 supports CSS variables with `bg-(--var)` syntax.

### Background Rules (Section 7)

```html
<!-- Page background: tinted neutral, not solid white -->
<body class="bg-(--surface-0)">
  <!-- Card: elevated surface -->
  <div class="bg-(--surface-1) rounded-lg shadow-sm">
    <!-- Modal: highest elevation -->
    <div class="bg-(--surface-2) rounded-xl shadow-lg">
    </div>
  </div>
</body>
```

Define surfaces in `@theme`:

```css
@theme {
  /* Light mode surfaces */
  --surface-0: oklch(0.985 0.005 80);    /* Warm off-white page background */
  --surface-1: oklch(0.995 0.002 80);    /* Near-white card surface */
  --surface-2: oklch(1.0 0 0);           /* Pure white for modals only */
}
```

### Shadow System (Section 8)

```css
@theme {
  --shadow-xs: 0 1px 2px oklch(0.2 0.02 260 / 0.04);
  --shadow-sm: 0 1px 3px oklch(0.2 0.02 260 / 0.06), 0 1px 2px oklch(0.2 0.02 260 / 0.04);
  --shadow-md: 0 4px 6px oklch(0.2 0.02 260 / 0.06), 0 2px 4px oklch(0.2 0.02 260 / 0.04);
  --shadow-lg: 0 10px 15px oklch(0.2 0.02 260 / 0.06), 0 4px 6px oklch(0.2 0.02 260 / 0.04);
  --shadow-xl: 0 20px 25px oklch(0.2 0.02 260 / 0.08), 0 8px 10px oklch(0.2 0.02 260 / 0.04);
}
```

Use tinted shadows (hue-shifted toward the color scheme), never `rgba(0,0,0,x)`.

### Component State Completeness (Section 6)

Full example combining all 6 states:

```html
<button class="
  bg-(--color-primary) text-(--color-primary-foreground) rounded-md px-4 py-2
  font-semibold text-sm

  hover:bg-(--color-primary-hover) hover:scale-[1.02] hover:shadow-md
  focus-visible:ring-2 focus-visible:ring-(--color-primary) focus-visible:ring-offset-2 focus-visible:outline-none
  active:scale-[0.98] active:shadow-sm
  disabled:opacity-50 disabled:pointer-events-none

  motion-safe:transition-all motion-safe:duration-200 motion-safe:ease-out
  motion-reduce:transition-none
">
  Submit
</button>
```

For loading state, conditionally swap content:

```tsx
<button disabled={isLoading} class="...">
  {isLoading ? (
    <span class="inline-flex items-center gap-2">
      <svg class="animate-spin h-4 w-4" /* spinner SVG */ />
      Loading...
    </span>
  ) : (
    "Submit"
  )}
</button>
```
