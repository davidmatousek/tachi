# Design Context Loader

## Purpose

This rule instructs all UI-generating agents to discover and load design context before generating any UI code. The context loading follows a 5-step discovery sequence with a defined precedence order.

## Discovery Sequence

Before generating any UI component, HTML, CSS, or visual element, execute this discovery sequence:

### Step 1: Check for Brand Identity

Look for `brands/*/` directories in the repository root.
- If found: Read `brand.md` (mandatory) and `tokens.css` (mandatory) from the brand directory
- Read `anti-patterns.md` (if present) as constraints
- Read files in `reference/` (if present) for visual context

### Step 2: Check for Active Archetype

Look for archetype files in `.claude/design/archetypes/`.
- If a project has selected an archetype (referenced in brand.md or project config), load that archetype file
- Archetype defines: font pairing, color palette, spacing preferences, motion style, shadow depth, border-radius

### Step 3: Load Stack Pack Design Tokens

If a stack pack is active (`.aod/stack-active.json`), load the scaffold CSS file containing `@theme` tokens:
- nextjs-supabase: `stacks/nextjs-supabase/scaffold/app/globals.css`
- fastapi-react: `stacks/fastapi-react/scaffold/frontend/src/app.css`

### Step 4: Load Design Quality Rules

Read `.claude/rules/design-quality.md` for core design standards.
If a stack pack is active, also read `stacks/{pack}/rules/design-quality-tailwind.md` for framework-specific patterns.

### Step 5: Answer Aesthetic Philosophy Questions

Before writing any UI code, answer the 4 questions from design-quality.md Section 1:
1. What is the dominant visual mood?
2. What typeface pairing communicates this mood?
3. What is the color temperature?
4. What level of visual density is appropriate?

## Precedence Order

When values conflict between sources, apply this precedence (highest wins):

1. **Brand identity** (`brands/{name}/`) — explicit client requirements
2. **Archetype** (`.claude/design/archetypes/`) — aesthetic direction
3. **Scaffold defaults** (`stacks/{pack}/scaffold/`) — baseline tokens
4. **Core rules** (`.claude/rules/design-quality.md`) — minimum standards

Core rules (layer 4) always apply as minimum standards regardless of higher-layer overrides.

## When This Applies

- Any task that generates HTML, CSS, JSX, TSX, or visual UI components
- Any task that modifies existing UI components
- Does NOT apply to: backend-only tasks, documentation, CLI tools, configuration files
