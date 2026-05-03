# UX/UI Designer — Python FastAPI + React Supplement

## Stack Context

React 19 functional components with TypeScript strict mode, Tailwind CSS v4 (CSS-first configuration via `@theme` directive, no `tailwind.config.js`), Biome for formatting and linting, Vite 6 build tooling. No prescribed UI component library — the pack is framework-agnostic for component libs (user chooses shadcn/ui, Radix, Headless UI, or custom). Design tokens live in `src/app.css` under the `@theme` directive. All styling uses Tailwind v4 utility classes exclusively.

## Conventions

- ALWAYS use functional components with typed props: `interface Props` followed by explicit function signature, then named export
- ALWAYS use Tailwind CSS v4 utility classes for all styling — every visual property lives in JSX `className` attributes
- ALWAYS define design tokens (colors, fonts, spacing) in the `@theme` directive inside `src/app.css`
- ALWAYS use `bg-linear-to-*` for gradients — `bg-gradient-to-*` was renamed in Tailwind v4
- ALWAYS use CSS variable parenthesis syntax `bg-(--var)` not bracket syntax `bg-[--var]` for Tailwind v4
- ALWAYS use semantic HTML elements (`nav`, `main`, `section`, `article`, `header`, `footer`, `form`) for document structure
- ALWAYS add ARIA attributes (`aria-label`, `aria-describedby`, `aria-expanded`, `role`) to interactive elements that lack visible text labels
- ALWAYS design mobile-first: start with base styles, layer `sm:`, `md:`, `lg:`, `xl:` breakpoints progressively
- ALWAYS ensure visible focus indicators on all interactive elements using `focus-visible:ring-2` pattern
- ALWAYS specify component states in design docs using Tailwind class names: default, `hover:`, `focus-visible:`, `disabled:`, `aria-selected:`
- ALWAYS use named exports for all components — never default exports
- ALWAYS design loading, error, and empty states for every component that fetches data
- ALWAYS use query-compatible markup: prefer `role`, `aria-label`, and visible text so tests can query by `getByRole`, `getByLabelText`, `getByText`
- ALWAYS associate every `<input>` with a `<label>` via `htmlFor`/`id` pairing or by nesting

## Anti-Patterns

- NEVER use CSS Modules, styled-components, Emotion, or inline `style` objects — Tailwind utilities exclusively
- NEVER use `React.FC<Props>` — use explicit function signatures with typed props interface
- NEVER use `tailwind.config.js` — use CSS-first `@theme` directive in Tailwind v4
- NEVER use `bg-gradient-to-*` — use `bg-linear-to-*` (v4 rename)
- NEVER use arbitrary Tailwind values (`w-[347px]`, `text-[13px]`) when a design token exists on the `@theme` scale
- NEVER specify colors as raw hex/rgb values in design docs — reference `@theme` CSS variable names or Tailwind palette tokens
- NEVER use decorative `<img>` elements without `alt=""` and `aria-hidden="true"` to hide them from assistive technology
- NEVER create `<button>` elements without accessible labels (visible text, `aria-label`, or `aria-labelledby`)
- NEVER create `<input>` or `<select>` elements without associated `<label>` elements
- NEVER design components that require JavaScript for layout — use CSS Grid and Flexbox via Tailwind utilities
- NEVER skip loading/error/empty states in design specs for data-fetching components

## Guardrails

- No UI component library is prescribed — design specs MUST be implementable with any component lib or custom elements
- Component structure: `interface Props` -> function declaration with typed params -> named export
- All interactive elements MUST be keyboard accessible (focusable, operable via Enter/Space, escapable for overlays)
- Color contrast MUST meet WCAG 2.1 AA minimum: 4.5:1 for normal text, 3:1 for large text and UI components
- Touch targets: minimum `h-11 w-11` (44px) for all interactive elements on touch devices
- Breakpoints: Tailwind defaults — `sm:640px`, `md:768px`, `lg:1024px`, `xl:1280px`, `2xl:1536px`
- Focus management: use `focus-visible:` styles, not `focus:` — prevents focus rings on mouse clicks
- Design token format: express all values as Tailwind classes or `@theme` CSS variable names, never raw numeric values
- Maximum z-index: stay within Tailwind's `z-0` through `z-50` scale
