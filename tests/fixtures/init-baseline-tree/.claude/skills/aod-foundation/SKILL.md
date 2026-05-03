---
name: aod-foundation
description: >-
  Guided post-init workshop that helps new AOD Kit adopters establish product vision
  and design identity. Two-part flow: Part 1 (Vision) asks 5 guided questions to populate
  product-vision.md; Part 2 (Design) browses archetypes to generate brand files (brand.md,
  tokens.css, anti-patterns.md). Supports --vision and --design flags for partial execution.
  Use when a developer invokes /aod.foundation after running make init.
---

# /aod.foundation Skill

## Purpose

Guided post-init workshop with two parts:
- **Part 1 (Vision)**: 5 storytelling-arc questions that populate `product-vision.md`
- **Part 2 (Design)**: Archetype browser that generates `brands/{project-name}/` files

Run after `make init` to replace placeholder markers with real content.

---

## Step 0: Parse Flags

Parse `--vision` and `--design` flags from the user's arguments.

1. If arguments contain `--vision`:
   - Set `vision_only = true`
   - Strip `--vision` from arguments
2. If arguments contain `--design`:
   - Set `design_only = true`
   - Strip `--design` from arguments
3. If neither flag is present:
   - Set `run_both = true` (full workshop)
4. If both flags are present:
   - Treat as `run_both = true` (equivalent to no flags)

---

## Step 1: State Detection

Detect the current project state to determine which parts to activate and whether this is a first-run or re-run.

### 1a: Derive Project Name

Use this ordered fallback to determine `{project-name}`:

1. **Repository directory name**: Run `basename $(git rev-parse --show-toplevel)` — use this if it yields a non-empty value
2. **CLAUDE.md PROJECT_NAME**: Read `CLAUDE.md`, grep for a line matching `PROJECT_NAME` that does NOT contain `tachi` (the un-replaced placeholder). Extract the value.
3. **AskUserQuestion fallback**: If neither source yields a usable name, ask: "What is your project name?" with a text input.

Sanitize the derived name to **kebab-case**: lowercase, replace spaces/underscores with hyphens, strip non-alphanumeric/non-hyphen characters.

Store as `project_name` for use throughout the workshop.

### 1b: Check Vision State

Read `docs/product/01_Product_Vision/product-vision.md`:

- If the file does **not exist**: Set `vision_state = "missing"` — Part 1 will create from scratch
- If the file contains `[To be refined` or `[To be defined`: Set `vision_state = "placeholder"` — Part 1 activates normally
- If the file exists with **no** placeholder markers: Set `vision_state = "populated"` — Part 1 enters re-run mode

### 1c: Check Design State

Check for brand directories under `brands/`:

- Glob `brands/*/brand.md` excluding `brands/_example/brand.md`
- If **no** brand directory found (only `_example`): Set `design_state = "missing"` — Part 2 activates normally
- If a brand directory **exists**: Set `design_state = "populated"` — Part 2 enters re-run mode

### 1d: Determine Flow

| vision_only | design_only | run_both | Action |
|-------------|-------------|----------|--------|
| true | false | false | Execute Part 1 only, skip Part 2 |
| false | true | false | Execute Part 2 only, skip Part 1 |
| false | false | true | Execute Part 1, then Part 2 |

Display state summary:
```
Foundation Workshop
  Project: {project_name}
  Vision:  {vision_state} → {Part 1 will: create/update/offer re-edit}
  Design:  {design_state} → {Part 2 will: create/offer re-edit}
  Mode:    {Full workshop | Vision only | Design only}
```

### 1e: Execution Flow

Based on flag state, execute parts in order:

1. If `vision_only`: Part 1 → completion summary → **end**
2. If `design_only`: Part 2 → completion summary → **end**
3. If `run_both`: Part 1 → `"Part 1 complete. Moving to Design Identity."` → Part 2 → completion summary → **end**

At each part entry, check the state for re-run handling. If user chooses "Keep current" during re-run detection, skip that part and advance to the next step in the flow. Choosing "Keep current" for Part 1 proceeds directly to Part 2 (if `run_both`). Choosing "Keep current" for Part 2 proceeds to the completion summary.

### 1f: Modification Isolation

Each part writes to independent file paths:
- **Part 1**: only `docs/product/01_Product_Vision/product-vision.md`
- **Part 2**: only `brands/{project_name}/` directory (brand.md, tokens.css, anti-patterns.md, reference/)

Modifying vision leaves brand files untouched. Modifying design leaves product-vision.md untouched. "Keep current" means zero writes to that part's files.

---

## Shared Patterns

### Progress Announcements

Display progress at every transition point. Format:

- During vision questions: `"Vision: Question {N}/5 — {question_title}"`
- Between parts: `"Part 1 complete. Moving to Design Identity."`
- During design: `"Design: {step_description}"`
- At completion: `"Workshop complete. {N} file(s) created/updated."`

### Show-Before-Write

After generating any file content, display it for user review before writing to disk.

1. Display the generated content (full file or relevant section)
2. Use AskUserQuestion with options:
   - **"Write to file"** — Write the content to disk, continue
   - **"Edit a section"** — Ask which section to change, apply edit, re-display
   - **"Cancel"** — Skip writing this file, continue to next step
3. Only write to disk on explicit "Write to file" confirmation
4. If "Edit a section": loop back to step 1 after applying changes

### Re-Run Detection

When existing populated content is detected (vision_state = "populated" or design_state = "populated"):

1. Display current content summary (key values, not full file)
2. Use AskUserQuestion with options:
   - **"Keep current"** — Skip this part entirely, preserve existing content
   - **"Update specific sections"** — Show sections, let user pick which to re-answer
   - **"Replace entirely"** — Run the full creation flow from scratch
3. If "Keep current": proceed to next part without modifying files
4. If "Update specific sections": present only the selected sections for re-answering, merge with existing content
5. If "Replace entirely": run the normal first-run flow

---

## Part 1: Vision Workshop

### Vision Questions

Present these 5 questions sequentially, following a storytelling arc from audience to measurement.

**Question 1 — "Who is this for?"**
- Arc position: Setting the scene
- Prompt: "Who is the primary user of your product? Describe them in 1-2 sentences — their role, context, and what makes them your target audience."
- Example: "Spotify targets music listeners who want personalized discovery without manual playlist curation."
- Default suggestion: Derive from `CLAUDE.md` description if available, otherwise: "Developers and small teams building software products"
- Maps to: **Target Users** section

**Question 2 — "What problem do they have?"**
- Arc position: The conflict
- Prompt: "What specific problem or frustration does your target user face today? What are they struggling with or missing?"
- Example: "Notion users struggled with scattered notes, docs, and project boards across multiple disconnected tools."
- Default suggestion: "They lack a structured approach to [domain]"
- Maps to: **Problem Statement** section

**Question 3 — "What does your product do?"**
- Arc position: The solution
- Prompt: "In 1-2 sentences, what does your product do to solve that problem? Focus on the core action, not features."
- Example: "Linear provides a streamlined issue tracker that's fast enough to feel invisible, so engineering teams focus on building, not managing tools."
- Default suggestion: Derive from `CLAUDE.md` description if available
- Maps to: **Core Value Proposition** + **Mission Statement** + **Core Capabilities**

**Question 4 — "How is it different?"**
- Arc position: The twist
- Prompt: "What makes your approach unique? How is it different from alternatives or the status quo?"
- Example: "Unlike traditional CRMs, HubSpot started free and grew with the customer — the product itself was the sales pitch."
- Default suggestion: "It takes a [specific approach] that existing solutions don't"
- Maps to: **Vision Statement**

**Question 5 — "How will you know it's working?"**
- Arc position: The resolution
- Prompt: "What 2-3 metrics or signals would tell you the product is succeeding? Think about what you'd check after launch."
- Example: "Figma tracks multiplayer sessions (collaboration), time-to-first-design (activation), and team plan upgrades (revenue)."
- Default suggestion: "User adoption, engagement frequency, and [domain-specific outcome]"
- Maps to: **Success Metrics**

### Question Presentation Flow

For each of the 5 questions:

1. Display progress: `"Vision: Question {N}/5 — {question_title}"`
2. Display the question prompt text
3. Display the example (italicized)
4. Use AskUserQuestion with:
   - A text input for the user's answer
   - A **"Skip"** option that marks the field as `[To be defined]`
5. Validate: if answer is empty and not skipped, re-prompt once
6. Store the answer for document generation

If all 5 questions are skipped: display warning — "All questions were skipped. The vision file will contain only placeholder markers. Downstream governance (/aod.define) may flag incomplete vision."

### Vision Document Generation

After all 5 questions are answered (or skipped), generate the product-vision.md content.

**Section mapping** (answer → document section):

| Answer | Document Section | Generation Rule |
|--------|-----------------|-----------------|
| Q1 (Who) | Target Users | Use answer directly. If skipped: `[To be defined]` |
| Q2 (Problem) | Problem Statement | Use answer directly. If skipped: `[To be defined]` |
| Q3 (What) | Mission Statement | Condense to 1 sentence if longer. If skipped: `[To be defined]` |
| Q3 (What) | Core Value Proposition | Use full answer. If skipped: `[To be defined]` |
| Q3 (What) | Core Capabilities | Extract key capabilities as a table. If skipped: `[To be defined]` |
| Q4 (Different) | Vision Statement | Frame as forward-looking "In a world where..." narrative. If skipped: `[To be defined]` |
| Q5 (Metrics) | Success Metrics | Format as a table with Metric and Target columns. If skipped: `[To be defined]` |

**Document structure** — follow the existing `product-vision.md` format:

```markdown
# Product Vision — {project_name}

**Last Updated**: {YYYY-MM-DD}
**Owner**: Product Manager (product-manager)
**Status**: Active

---

## Mission Statement
{derived from Q3}

## Vision Statement
{derived from Q4}

## Problem Statement
{derived from Q2}

## Core Value Proposition
{derived from Q3}

## Core Capabilities

| Capability | Description |
|---|---|
{derived from Q3 — extract 2-4 key capabilities}

## Target Users

### Primary: {derived from Q1}
{expand Q1 answer into user persona description}

## Success Metrics

| Metric | Target |
|---|---|
{derived from Q5 — format each metric as a row}

---

**Maintained By**: Product Manager (product-manager)
```

After generation:
1. Display the full generated document
2. Apply show-before-write pattern
3. Write to `docs/product/01_Product_Vision/product-vision.md`

### Skip Part 1 Entirely

When running the full workshop (`run_both = true`) and vision_state is "placeholder" or "missing":

After displaying the state summary (Step 1d), before starting questions, offer:
- Use AskUserQuestion: "Ready to start the Vision Workshop (5 questions)?"
  - **"Start"** — Begin Question 1
  - **"Skip to Design"** — Skip Part 1 entirely, proceed to Part 2 without modifying `product-vision.md`

When `vision_only = true`: do NOT offer skip — proceed directly to questions.

### Vision Re-Run Handling

When `vision_state = "populated"` (no placeholder markers):

1. Read existing `product-vision.md` and extract current values for each section
2. Display summary:
   ```
   Current Vision:
     Mission:    {first 80 chars}...
     Vision:     {first 80 chars}...
     Problem:    {first 80 chars}...
     Value Prop: {first 80 chars}...
     Users:      {first 80 chars}...
     Metrics:    {count} defined
   ```
3. Apply re-run detection pattern (Keep current / Update specific sections / Replace entirely)
4. If "Update specific sections": present checkboxes for which sections to update, then ask only the corresponding questions
5. If "Replace entirely": run the full 5-question flow, overwriting the entire file

---

## Part 2: Design Identity Workshop

### Design Re-Run Handling

When `design_state = "populated"` (brand directory already exists):

1. Read existing `brands/{project_name}/brand.md` and extract: archetype name (from tagline or heading), heading font, body font, primary color
2. Display summary:
   ```
   Current Design Identity:
     Archetype:   {name or "Custom"}
     Fonts:       {heading font} + {body font}
     Primary:     {color value}
     Temperature: {warm/cool/neutral}
   ```
3. Apply re-run detection pattern (Keep current / Update specific sections / Replace entirely)
4. If "Keep current": skip Part 2 entirely, preserve all brand files
5. If "Update specific sections": allow modifying individual brand file sections, merge with existing
6. If "Replace entirely": run the full archetype selection flow below

### Step 2a: Archetype Discovery

Discover available archetypes at runtime:

1. Glob `.claude/design/archetypes/*.md`
2. If **no files found**: display warning — "No design archetypes found in `.claude/design/archetypes/`. Check your installation." Offer only the Custom option (skip to Step 2c).
3. For each archetype file, parse:
   - **Name**: Derive from filename, title-cased (e.g., `precision.md` → "Precision")
   - **Tagline**: First blockquote line (`> ...`) after the `# {Name} Archetype` heading
   - **Font pairing**: Extract **Headings** and **Body** font names from the "Font Pairing" table's Font column
   - **Color temperature**: Extract from the `**Temperature**:` line under "Color Palette Strategy"

### Step 2b: Archetype Browser

Present discovered archetypes as a numbered selection list via AskUserQuestion.

Display `"Design: Archetype Selection"` as progress announcement.

Format per archetype:
```
{N}. {Name} — "{Tagline (first ~60 chars)}"
   Fonts: {Heading Font} + {Body Font} | Temperature: {temperature}
```

AskUserQuestion options: numbered options `"1"` through `"{N}"` for each archetype, plus `"Custom"`.

After selection:
- If numbered option: store the archetype name, read the full archetype file for value extraction
- If "Custom": proceed to Step 2c

### Step 2c: Custom Design Flow

When the user selects "Custom" (no archetype):

1. Ask: "What is your primary brand color? (e.g., 'deep blue', '#1a365d', 'warm terracotta')"
   - AskUserQuestion with text input
   - Store as `custom_primary_color`

2. Ask: "What font style fits your brand? (e.g., 'clean and modern', 'editorial serif', 'technical monospace')"
   - AskUserQuestion with text input
   - Store as `custom_font_style`

3. Ask: "What is the overall visual mood? (e.g., 'professional and minimal', 'warm and inviting', 'bold and energetic')"
   - AskUserQuestion with text input
   - Store as `custom_mood`

Generate brand files using these custom inputs. Select appropriate fonts, colors, radius, and shadow values that match the described mood and font style. Use design knowledge to produce a coherent set of tokens.

### Step 2d: Brand Directory and brand.md Generation

1. Create directory `brands/{project_name}/` (if not exists)
2. Create empty `brands/{project_name}/reference/` directory
3. Generate `brand.md` following the structure from `brands/_example/brand.md`:

   **Replacements from archetype (or custom inputs)**:
   - `{{BRAND_NAME}}` → `{project_name}` in title case
   - `{{BRAND_TAGLINE}}` → archetype tagline (or custom mood description)
   - **Primary Colors** table → from archetype's `--color-primary`, `--color-primary-light`, `--color-accent` values with hex + oklch
   - **Secondary Colors** table → from archetype's `--color-secondary`, `--color-accent`, and a neutral derived from palette
   - **Semantic Colors** table → from archetype's success/warning/error/info values
   - `{{HEADING_FONT}}` → archetype heading font name
   - `{{BODY_FONT}}` → archetype body font name
   - `{{MONO_FONT}}` → `JetBrains Mono` (default for all)
   - **Personality / Voice** → derive from archetype description and character notes
   - **Visual Tone** → derive from archetype's Layout Philosophy and overall description
   - **Usage Notes** → adapt from archetype's guidelines and constraints

### Step 2e: Anti-Patterns Generation

Generate `brands/{project_name}/anti-patterns.md` from archetype constraints:

1. Read the selected archetype's sections:
   - "Usage Notes" → "Avoid {archetype} for" items and accessibility considerations
   - "Shadow Depth" → guidelines (e.g., "Avoid lg shadows" for precision)
   - "Border Radius" → guidelines (e.g., "Never exceed --radius-lg" for precision, "Sharp corners never used" for warmth)
   - "Motion Style" → guidelines (e.g., "Avoid bounce effects" for precision)
   - "Layout Philosophy" → patterns and constraints

2. Generate anti-patterns following `brands/_example/anti-patterns.md` structure with these categories:
   - **Visual Constraints**: From radius, shadow, and spacing guidelines
   - **Typography Constraints**: From font pairing rationale and weight guidance
   - **Motion / Animation Constraints**: From motion style guidelines
   - **Layout Constraints**: From layout philosophy
   - **Color Constraints**: From palette approach and accessibility notes

3. Each constraint MUST be specific and actionable:
   - Good: "Avoid border-radius larger than 6px on rectangular elements" (precision)
   - Good: "Never use sharp corners on any element" (warmth)
   - Bad: "Keep it clean" (not actionable)

### Step 2f: Token Mapping and tokens.css Generation

Generate `brands/{project_name}/tokens.css` with all 19 semantic tokens.

1. **Read** the canonical mapping from `.claude/skills/aod-foundation/references/token-mapping.md`
2. **Extract** values from the selected archetype's markdown tables:
   - Color Palette Strategy table → color values (hsl/oklch format)
   - Font Pairing table → font family names and fallbacks
   - Border Radius table → radius values
   - Shadow Depth table → shadow values
3. **Apply rename layer** (archetype name → tokens.css name):
   - `--color-error` → `--color-destructive`
   - `--color-surface` → `--color-background` (and also informs `--color-muted`)
   - Body font → `--font-sans`
   - Heading font → `--font-heading`
4. **Apply derivation rules** for missing tokens:
   - `--color-secondary` if absent: primary hue + 30 degrees
   - `--color-muted` if absent: primary at 10% saturation, 95% lightness
   - `--shadow-lg` if absent (precision, technical): derive from `--shadow-md` with 2.5x spread/offset, 1.25x opacity
   - `--radius-lg` if absent: `--radius-md` * 1.5
   - `--font-mono`: always `"JetBrains Mono", "Fira Code", monospace`
5. **Generate** single-layer `:root {}` block:

```css
/**
 * Brand Tokens — {project_name}
 * Generated by /aod.foundation from {archetype_name} archetype
 */

:root {
  /* --- Colors --- */
  --color-primary:     {value};
  --color-secondary:   {value};
  --color-accent:      {value};
  --color-muted:       {value};
  --color-destructive: {value};
  --color-success:     {value};
  --color-warning:     {value};
  --color-info:        {value};
  --color-background:  {value};
  --color-foreground:  {value};

  /* --- Typography --- */
  --font-sans:    "{body font}", {fallbacks};
  --font-heading: "{heading font}", {fallbacks};
  --font-mono:    "JetBrains Mono", "Fira Code", monospace;

  /* --- Border Radius --- */
  --radius-sm: {value};
  --radius-md: {value};
  --radius-lg: {value};

  /* --- Shadows --- */
  --shadow-sm: {value};
  --shadow-md: {value};
  --shadow-lg: {value};
}
```

Total: 19 individual tokens (10 color + 3 font + 3 radius + 3 shadow).

### Step 2g: Stack Pack Compatibility Check

If `.aod/stack-active.json` exists:

1. Read the file and extract the active pack name
2. Display note: `"Note: Stack pack '{pack_name}' is active. Generated tokens use standard CSS custom property names compatible with the pack's scaffold."`

If no stack pack is active: skip silently.

### Step 2h: Preview and Write All Brand Files

After generating all three files:

1. Display each file's content with progress announcements:
   ```
   Design: Preview — brand.md
   {full content}

   Design: Preview — tokens.css
   {full content}

   Design: Preview — anti-patterns.md
   {full content}
   ```

2. Apply show-before-write pattern for ALL files together:
   - **"Write all files"** — Write all three to `brands/{project_name}/`
   - **"Edit a section"** — Ask which file and section to change, apply edit, re-display
   - **"Cancel"** — Skip writing brand files entirely

3. Only write to disk on explicit "Write all files" confirmation
4. After writing: `"Design: Brand files written to brands/{project_name}/"`

---

## Edge Cases

- **Missing archetypes directory**: If `.claude/design/archetypes/` has no `.md` files, warn and offer only the Custom design option (Step 2c)
- **Missing product-vision.md**: When `vision_state = "missing"`, create from scratch using the full 5-question flow — do not read or parse a nonexistent file
- **Special characters in project name**: Step 1a sanitization handles this — always use the kebab-case `project_name` for directory and file paths
- **All vision questions skipped**: Warning displayed per Question Presentation Flow. Still proceed to Part 2 if `run_both = true` — skipping vision does not block design
- **All of Part 2 skipped during full workshop**: Display completion summary with design artifacts marked "Skipped"

---

## Workshop Completion Summary

After all parts complete, display a summary table:

```
Foundation Workshop Complete

| Artifact | Path | Status |
|----------|------|--------|
| Product Vision | docs/product/01_Product_Vision/product-vision.md | {Created/Updated/Skipped} |
| Brand Identity | brands/{project-name}/brand.md | {Created/Updated/Skipped} |
| Design Tokens | brands/{project-name}/tokens.css | {Created/Updated/Skipped} |
| Anti-Patterns | brands/{project-name}/anti-patterns.md | {Created/Updated/Skipped} |

{count} file(s) created, {count} file(s) updated, {count} file(s) skipped.
```
