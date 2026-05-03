# UX/UI Designer — Next.js + Supabase Supplement

## Stack Context

Tailwind CSS v4 for utility-first styling, shadcn/ui as the component library (built on Radix UI primitives), Next.js App Router for layout composition, Server Components for static UI / Client Components for interactive UI, `next/font` for zero-layout-shift web fonts, `next/image` for optimized responsive images, `cn()` utility (clsx + tailwind-merge) for conditional class composition, CSS variables from shadcn/ui theme for design tokens, Lucide React for iconography.

## Conventions

- ALWAYS use Tailwind CSS utility classes for all styling — every visual property lives in JSX className attributes
- ALWAYS use shadcn/ui as the component library base — extend with Tailwind variants, never build parallel primitives
- ALWAYS use the `cn()` utility for conditional class composition — never string concatenation or template literals
- ALWAYS design mobile-first: start with base styles, layer `sm:`, `md:`, `lg:` breakpoints progressively
- ALWAYS use Tailwind's design token scale (colors, spacing, typography, sizing) — prefer `w-96` over `w-[384px]`
- ALWAYS use `next/font` for font loading with `variable` CSS custom properties assigned on the root layout
- ALWAYS use `next/image` with explicit `width`/`height` or `fill` prop plus `sizes` attribute for responsive images
- ALWAYS use shadcn/ui CSS variables for color theming (`--background`, `--foreground`, `--primary`, `--muted`, `--destructive`, etc.)
- ALWAYS use Radix UI primitives via shadcn/ui for accessible interactive components (Dialog, DropdownMenu, Tooltip, Popover, Select, etc.)
- ALWAYS specify dark mode styles using Tailwind's `dark:` variant paired with shadcn/ui's theme toggle system
- ALWAYS use semantic HTML elements (`nav`, `main`, `section`, `article`, `aside`, `header`, `footer`) for document structure
- ALWAYS ensure visible focus indicators on all interactive elements: `ring-2 ring-ring ring-offset-2` pattern
- ALWAYS design loading states for every async data boundary — `loading.tsx` files or inline `<Suspense>` with skeleton fallbacks
- ALWAYS specify component states in design docs using Tailwind class names: default, `hover:`, `focus-visible:`, `disabled:`, `aria-selected:`, `data-[state=open]:`
- ALWAYS use App Router layouts (`layout.tsx`) for persistent shared UI and route groups for section-level layout segmentation
- ALWAYS co-locate component styles with markup — Tailwind classes live in the JSX, never in separate files

## Anti-Patterns

- NEVER use CSS modules, styled-components, Emotion, or any CSS-in-JS solution — Tailwind utilities exclusively
- NEVER use inline `style` objects (`style={{ }}`) — express all visual properties as Tailwind classes
- NEVER create custom CSS files when a Tailwind utility or shadcn/ui component covers the need
- NEVER use arbitrary Tailwind values (`w-[347px]`, `text-[13px]`, `p-[7px]`) when a design token exists on the scale
- NEVER use raw `px` units in custom CSS — use Tailwind's rem-based spacing scale for consistency
- NEVER build custom interactive primitives (modals, dropdowns, tooltips, popovers, select menus) — use shadcn/ui components backed by Radix
- NEVER ignore dark mode in design specs — every color choice must reference a CSS variable that resolves in both light and dark themes
- NEVER skip loading/skeleton states — every route with async data needs a `loading.tsx` or `Suspense` fallback in the design
- NEVER specify colors as raw hex/rgb values in design docs — reference shadcn/ui CSS variable names or Tailwind palette tokens
- NEVER use arbitrary `z-index` values — stay within Tailwind's `z-0` through `z-50` scale
- NEVER design components that require JavaScript for layout — use CSS Grid and Flexbox via Tailwind utilities

## Guardrails

- Component library: shadcn/ui only — do not introduce alternative component libraries (Material UI, Chakra, Ant Design, etc.)
- Color system: shadcn/ui CSS variables (`--background`, `--foreground`, `--card`, `--popover`, `--primary`, `--secondary`, `--muted`, `--accent`, `--destructive`, `--border`, `--input`, `--ring`)
- Icon library: Lucide React (default with shadcn/ui) — do not introduce Heroicons, Font Awesome, or other icon sets
- Animation: Tailwind's built-in transition utilities and `tailwindcss-animate` plugin — no Framer Motion or GSAP unless the spec explicitly requires complex animation
- Layout patterns: use App Router `layout.tsx` for shared UI shells, route groups `(auth)`, `(dashboard)`, `(marketing)` for section layouts
- Breakpoints: Tailwind defaults — `sm:640px`, `md:768px`, `lg:1024px`, `xl:1280px`, `2xl:1536px`
- Maximum z-index: `z-50` — shadcn/ui manages overlay z-indexes internally via Radix portals
- Touch targets: minimum `h-10 w-10` (40px) for interactive elements, `h-11 w-11` (44px) preferred for primary actions
- Focus management: all interactive elements must use `focus-visible:` styles, not `focus:` — prevents focus rings on mouse clicks
- Design token format: when handing off to frontend-developer, express all values as Tailwind classes or shadcn/ui CSS variable names, never raw numeric values
