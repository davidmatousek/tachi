# Session Prompt: Fix Infographic Visual Quality

## Context

A 5 Whys analysis identified why generated threat model infographics look "technical and sharp" instead of polished and pleasant. **Root cause**: The Gemini prompt templates communicate WHAT data to render but not HOW the result should FEEL. They are data layout specifications, not creative design briefs. Gemini interprets the dense, technical prompt literally.

**Reference images** (current, technical-looking): `examples/agentic-app/test-output/threat-baseball-card.jpg` and `examples/agentic-app/test-output/threat-system-architecture.jpg` — view these first to understand the problem.

## Changes Required

There are 3 workstreams. Complete them in order, then test.

---

### Workstream 1: Add Unique Run Folders to `/threat-model` Command

**Problem**: Each `/threat-model` run overwrites the previous output. Runs should produce output in timestamped subfolders so results are preserved for comparison.

**File**: `.claude/commands/threat-model.md` (and the copy at `adapters/claude-code/commands/threat-model.md`)

**Change**: In Step 0 (Parse Flags), after the output_dir is resolved, add auto-timestamped subfolder creation:

```
9. Generate a unique run folder:
   - Compute timestamp: `YYYY-MM-DDTHH-MM-SS` (e.g., `2026-03-25T14-30-22`)
   - Append to output_dir: `{output_dir}/{timestamp}/`
   - This ensures each run produces output in a unique subfolder
   - Example: `examples/agentic-app/test-output/2026-03-25T14-30-22/`
```

Also update Step 3 (Report Results) to show the timestamped path in the summary.

---

### Workstream 2: Rewrite Infographic Templates (Design-First Prompts)

Fix the Gemini Prompt Template section in BOTH template files. The fix follows the same pattern for each:

1. **Lead with aesthetic goals** before any data
2. **Add mood/feel language** that communicates the target impression
3. **Reduce inline data density** — don't spell out every hex code in every sentence
4. **Commit to dark navy theme** (#1E293B) for presentation impact and visual depth

#### File 1: `adapters/claude-code/agents/templates/infographic-baseball-card.md`

Rewrite the `## Gemini Prompt Template` section (currently lines 169-190). Replace with a design-first prompt that:

- Opens with: "Create a premium, boardroom-ready security risk dashboard with a polished, modern dark-theme aesthetic. This should look like a professionally designed Figma dashboard — not a data table or spreadsheet."
- Specifies dark navy background (#1E293B) with white/light text for visual depth and executive presentation impact
- Describes the donut chart, heat map, and finding cards using **design language** (generous whitespace, rounded cards with subtle shadows, clean visual hierarchy, soft glows on severity colors) instead of raw data specs
- Moves hex codes to a single "Color reference" line instead of repeating them inline
- Keeps all the data placeholders ({project_name}, {critical_count}, etc.) but wraps them in design context
- Ends with: "The overall impression should be a polished executive briefing document — confident, clear, and visually sophisticated."

Also update the `## Style` table: change Background from "White (#FFFFFF)" to "Dark Navy (#1E293B)" and the `## Color Palette` section to include light text colors for dark backgrounds.

Also update `## Zone Specifications` > `### Background` section to remove the "Either theme is acceptable" ambiguity — commit to dark theme.

#### File 2: `adapters/claude-code/agents/templates/infographic-system-architecture.md`

Rewrite the `## Gemini Prompt Template` section (currently lines 219-243). Same design-first approach:

- Opens with: "Create a premium, professionally designed system architecture diagram showing security threat analysis findings. This should look like an architecture poster from a top-tier security consultancy — clean, authoritative, and visually sophisticated."
- Use a light/white background for this template (architecture diagrams need contrast for zone coloring) but add visual polish: subtle shadows on component boxes, rounded corners, professional spacing
- Describe trust zones as elegantly styled regions with subtle background tints, not flat boxes
- Component boxes should feel like "design system cards" — rounded corners, subtle drop shadows, clean typography
- Data flow arrows should be styled with smooth curves, not harsh straight lines
- Keep all data placeholders but reduce repetitive hex code specifications

Also update the `## Style` table and `## Color Palette` to reflect the polished aesthetic (add shadow colors, rounded corner specs, spacing guidelines).

#### File 3: `adapters/claude-code/agents/threat-infographic.md`

Update the `## Gemini API Prompt Construction` > `### Prompt Framing` section (around line 399). Add a subsection:

```markdown
### Design Philosophy

Every Gemini prompt MUST lead with the visual quality target before any data. The prompt communicates two things:
1. **Aesthetic intent** (first paragraph): How the final image should FEEL — polished, premium, boardroom-ready
2. **Data content** (remaining paragraphs): What data to include and where

Never send a data-only prompt. Gemini interprets dense technical specifications literally, producing flat, spreadsheet-like output. Leading with aesthetic language primes the model for visual quality.
```

Also resolve the dark/light theme contradiction:
- In Section 6 Visual Design Directives (around line 335-338), remove "Either theme is acceptable" — replace with: "Baseball Card uses dark navy theme (#1E293B). System Architecture uses white background with polished card styling. Template files are authoritative for theme selection."

#### Propagate Changes

After editing the 3 files above in `adapters/claude-code/agents/`:

1. Copy templates to root: `cp adapters/claude-code/agents/templates/infographic-*.md templates/`
2. Copy templates to active agents: `cp adapters/claude-code/agents/templates/infographic-*.md .claude/agents/tachi/templates/`
3. Copy agent to active agents: `cp adapters/claude-code/agents/threat-infographic.md .claude/agents/tachi/`
4. Copy command: `cp .claude/commands/threat-model.md adapters/claude-code/commands/threat-model.md`

---

### Workstream 3: Test

Run the threat model on the same architecture and compare:

```
/threat-model examples/agentic-app/architecture.md --output-dir examples/agentic-app/test-output/
```

**Verify**:
1. Output went to a NEW timestamped subfolder (not overwriting the previous run at `examples/agentic-app/test-output/`)
2. View both generated `.jpg` files
3. Compare visually against the previous run's images at:
   - `examples/agentic-app/test-output/threat-baseball-card.jpg`
   - `examples/agentic-app/test-output/threat-system-architecture.jpg`
4. The new images should feel polished and premium, not technical and flat

---

## Success Criteria

- [ ] `/threat-model` produces output in unique timestamped subfolders
- [ ] Baseball card infographic uses dark navy theme with polished aesthetic
- [ ] System architecture infographic has professional card styling with subtle shadows
- [ ] Neither image looks like a "data dump" or "spreadsheet"
- [ ] Previous test output at `examples/agentic-app/test-output/` is NOT overwritten
- [ ] All template copies are in sync (adapters/ -> templates/ -> .claude/agents/tachi/)
