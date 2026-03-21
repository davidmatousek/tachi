---
name: aod-stack
description: >-
  Manage stack packs — activate, remove, list, and scaffold technology-specific
  conventions for AI coding agents. Use when developers want to select a stack,
  set up conventions, or manage pack lifecycle.
---

# Stack Pack Management Skill

Activate, list, and manage stack packs that encode technology-specific conventions,
security patterns, and agent persona supplements into AOD.

## Subcommands

| Command | Purpose |
|---------|---------|
| `/aod.stack use {pack-name}` | Activate a stack pack |
| `/aod.stack list` | Show available packs and active status |
| `/aod.stack remove` | Deactivate the active pack |
| `/aod.stack scaffold` | Scaffold project structure from the active pack |

---

## `/aod.stack use {pack-name}`

Activate a stack pack by copying its rules, generating a persona loader, and
persisting activation state.

### Step 1: Validate the pack exists

1. Check that `stacks/{pack-name}/` exists as a directory.
2. Check that `stacks/{pack-name}/STACK.md` exists and is non-empty.
3. If the directory or STACK.md does not exist, display the error:
   ```
   Pack not found: {pack-name}

   Available packs:
     - {list each directory under stacks/ that contains a STACK.md}

   Use: /aod.stack use {pack-name}
   ```
   Then stop.

### Step 2: Handle already-active pack

1. Read `.aod/stack-active.json` if it exists.
2. If another pack is active (the `pack` field differs from `{pack-name}`):
   - Prompt the user: "Pack `{current-pack}` is currently active. Switch to
     `{pack-name}`? This will deactivate `{current-pack}` first. (y/n)"
   - If the user declines, stop.
   - If the user confirms, execute full deactivation:
     a. Delete all files in `.claude/rules/stack/`.
     b. Delete `.aod/stack-active.json`.
3. If the same pack is already active (`pack` field equals `{pack-name}`):
   - Prompt: "Pack `{pack-name}` is already active. Re-activate to update
     rules and persona loader? (y/n)"
   - If the user declines, stop.
   - If the user confirms, proceed (this refreshes rules from the pack source).

### Step 3: Detect and resolve inconsistent state

Before proceeding, check for inconsistencies:

- If `.aod/stack-active.json` exists but is not valid JSON:
  - Warn: "Inconsistent state: `.aod/stack-active.json` is corrupted.
    Cleaning up stale state."
  - Delete all files in `.claude/rules/stack/`.
  - Delete `.aod/stack-active.json`.
  - Then continue with activation.

- If `.aod/stack-active.json` exists but references a pack directory that does
  not exist under `stacks/`:
  - Warn: "Inconsistent state: `.aod/stack-active.json` references pack
    `{missing-pack}` which no longer exists. Cleaning up stale state."
  - Delete all files in `.claude/rules/stack/`.
  - Delete `.aod/stack-active.json`.
  - Then continue with activation.

- If `.claude/rules/stack/` contains files but `.aod/stack-active.json` does
  not exist:
  - Warn: "Inconsistent state: `.claude/rules/stack/` has files but no
    activation state. Cleaning up orphaned rules."
  - Delete all files in `.claude/rules/stack/`.
  - Then continue with activation.

### Step 4: Copy stack rules and agent supplements

1. Ensure the directory `.claude/rules/stack/` exists (create it if missing).
2. Copy every `.md` file from `stacks/{pack-name}/rules/` to
   `.claude/rules/stack/`.
3. Copy every `.md` file from `stacks/{pack-name}/agents/` to
   `.claude/rules/stack/`, prefixing each filename with `agent-` to avoid
   collisions (e.g., `tester.md` → `agent-tester.md`).
4. If either directory is empty or does not contain `.md` files,
   note this in the activation summary but do not treat it as an error.

### Step 5: Generate persona-loader.md

Create the file `.claude/rules/stack/persona-loader.md` with the following
content (substitute `{pack-name}` with the actual pack name):

```markdown
# Stack Pack Persona Loader

When you are a **specialized** or **hybrid** agent, read your persona supplement
from the active stack pack before executing any task.

## Active Pack: {pack-name}

## Agent Tier Classification

**Core agents** (product-manager, architect, team-lead, orchestrator,
web-researcher): You are stack-agnostic. Do NOT read persona supplements.
Ignore this file entirely.

**Specialized agents** (frontend-developer, senior-backend-engineer,
security-analyst, tester, code-reviewer, devops): Read your persona
supplement from `stacks/{pack-name}/agents/{your-agent-name}.md` as
supplementary context before executing any task.

**Hybrid agents** (ux-ui-designer, debugger): Read your persona supplement
from `stacks/{pack-name}/agents/{your-agent-name}.md` for stack-specific
tooling context before executing any task.

## Instructions

1. Determine your agent name (e.g., `frontend-developer`).
2. Check if `stacks/{pack-name}/agents/{your-agent-name}.md` exists.
3. If it exists, read it and apply its conventions, anti-patterns, and
   guardrails to all outputs in this session.
4. If it does not exist, proceed with your core expertise only.
5. Do NOT modify your core behavior — persona supplements are additive context.
```

### Step 6: Write activation state

Write the file `.aod/stack-active.json` with this exact structure:

```json
{
  "pack": "{pack-name}",
  "activated_at": "{current ISO 8601 timestamp}",
  "version": "1.0"
}
```

Use the current UTC time for `activated_at` (e.g., `2026-02-27T14:30:00Z`).

### Step 7: Validate context budget

After writing all files, check the context budget:

1. Count the number of lines in `stacks/{pack-name}/STACK.md`.
2. Count the number of persona supplement files in `stacks/{pack-name}/agents/`
   and the line count of each.
3. Count the total lines across all files copied to `.claude/rules/stack/`
   (including the generated `persona-loader.md`).
4. Compute total pack overhead = STACK.md lines + max persona supplement lines
   + total rules lines.
5. Warn if any threshold is exceeded:
   - STACK.md > 500 lines: "WARNING: STACK.md is {N} lines (limit: 500).
     Consider splitting into STACK.md and STACK-EXTENDED.md."
   - Any persona file > 100 lines: "WARNING: {filename} is {N} lines
     (limit: 100). Brevity forces precision."
   - Total pack overhead > 800 lines: "WARNING: Total pack context is {N}
     lines (limit: 800). Agent performance may degrade."

### Step 8: Display activation summary

Display the following output, filling in actual values:

```
Stack pack activated: {pack-name}

Rules loaded:
  - .claude/rules/stack/{rule1}.md
  - .claude/rules/stack/{rule2}.md
  - .claude/rules/stack/persona-loader.md

Agent supplements available for:
  - {comma-separated list of .md filenames in stacks/{pack-name}/agents/,
    without the .md extension}

Context budget:
  - STACK.md: {N} lines (limit: 500)
  - Persona supplements: {count} files (<=100 lines each)
  - Stack rules: {N} lines (limit: 200)
  - Total pack overhead: {N} lines (limit: 800)

Run /aod.stack scaffold to create the project structure.
```

---

## `/aod.stack remove`

Deactivate the currently active pack, removing all stack-specific rules and state.

### Step 1: Detect and resolve inconsistent state

Before proceeding, check for inconsistencies:

- If `.aod/stack-active.json` is not valid JSON:
  - Warn: "Inconsistent state: `.aod/stack-active.json` is corrupted. Cleaning
    up all stack state."
  - Delete all files in `.claude/rules/stack/`.
  - Delete `.aod/stack-active.json`.
  - Display: "Stack state cleaned. No pack is active."
  - Then stop.

- If `.aod/stack-active.json` exists but references a pack directory that does
  not exist under `stacks/`:
  - Warn: "Inconsistent state: `.aod/stack-active.json` references pack
    `{missing-pack}` which no longer exists. Cleaning up stale state."
  - Delete all files in `.claude/rules/stack/`.
  - Delete `.aod/stack-active.json`.
  - Display: "Stale state cleaned. No pack is active."
  - Then stop.

- If `.claude/rules/stack/` contains files but `.aod/stack-active.json` does
  not exist:
  - Warn: "Inconsistent state: `.claude/rules/stack/` has files but no
    activation state. Cleaning up orphaned rules."
  - Delete all files in `.claude/rules/stack/`.
  - Display: "Orphaned rules cleaned. No pack is active."
  - Then stop.

### Step 2: Check for active pack

1. If `.aod/stack-active.json` does not exist AND `.claude/rules/stack/` is
   empty (or does not exist):
   - Display: "No stack pack is currently active."
   - Then stop.
2. Read `.aod/stack-active.json` to get the active pack name.

### Step 3: Remove stack rules

1. Delete all files in `.claude/rules/stack/` (including `persona-loader.md`).
2. If the directory `.claude/rules/stack/` is now empty, leave it (do not
   delete the directory itself).

### Step 4: Delete activation state

Delete the file `.aod/stack-active.json`.

### Step 5: Display deactivation summary

```
Stack pack removed: {pack-name}

Cleaned:
  - .claude/rules/stack/ (emptied)
  - .aod/stack-active.json (deleted)

Implementation agents reverted to generic behavior.
Previously scaffolded project files remain untouched.
```

---

## `/aod.stack scaffold`

Create the project structure from the active pack's scaffold templates.

### Step 1: Check for active pack

1. Read `.aod/stack-active.json`. If it does not exist, display:
   ```
   No stack pack is active.

   Activate a pack first: /aod.stack use {pack-name}
   ```
   Then stop.
2. Read the `pack` field to determine the active pack name.

### Step 2: Scan scaffold templates

1. Check if `stacks/{pack-name}/scaffold/` exists and contains files (not just
   `.gitkeep`).
2. If the scaffold directory does not exist or is empty, display:
   ```
   No scaffold templates found for pack: {pack-name}

   The pack does not include project scaffolding.
   ```
   Then stop.
3. Build a list of all files in `stacks/{pack-name}/scaffold/` (recursively),
   preserving their relative paths from `scaffold/`.

### Step 3: Detect conflicts

For each scaffold file, check if the target path already exists at the project
root:

1. Compute the target path: project root + relative path from scaffold/.
2. If the target file exists, mark it as a conflict.
3. If no conflicts exist, skip to Step 4.
4. If conflicts exist, display the conflict list and prompt per-file:
   ```
   Scaffold conflicts detected:

     - {file1} (exists)
     - {file2} (exists)

   For each conflict:
   ```
   For each conflicting file, prompt: "Overwrite `{file}`? (y/n/abort)"
   - **y**: Overwrite the file with the scaffold version.
   - **n**: Skip the file (keep existing).
   - **abort**: Stop scaffolding entirely. Files already copied remain.

### Step 4: Copy scaffold files

1. For each non-conflicting file (and each conflict the user chose to overwrite):
   a. Ensure the parent directory exists (create if missing).
   b. Copy the file from `stacks/{pack-name}/scaffold/{path}` to the project
      root at `{path}`.
2. Skip `.gitkeep` files — they are directory placeholders, not scaffold content.

### Step 5: Placeholder Resolution

After scaffold files are copied, automatically resolve template placeholders in `docs/` files.

1. **Baseline grep** (per KB #22): Run `grep -r 'tachi\|2026-03-21' docs/` to map all placeholder occurrences before replacement. Record the count for the summary.
2. **Source project name**:
   a. Read `.aod/memory/constitution.md` and extract the project name from its heading or body
   b. If not found or file does not exist: fallback to git repo basename via `basename $(git rev-parse --show-toplevel)`
3. **Replace placeholders** in `docs/` files only:
   - Replace all `tachi` occurrences with the resolved project name
   - Replace all `2026-03-21` occurrences with the current date in `YYYY-MM-DD` format
   - **Scope boundary**: Do NOT modify files outside the `docs/` directory
4. **Idempotent**: If a file contains no placeholders (already resolved), it remains unchanged
5. **Display summary**:
   ```
   Placeholder resolution:
     Files modified: {count}
     Placeholders resolved: {total_count}
       - tachi: {count} → {resolved_name}
       - 2026-03-21: {count} → {resolved_date}
   ```
   If zero placeholders found, display: "Placeholder resolution: no placeholders found in docs/ files"

### Step 6: Display scaffold summary

```
Project scaffolded from: {pack-name}

Created:
  - {file1}
  - {file2}
  - ...

Skipped (already exists):
  - {conflict1}
  - ...

Next: Install dependencies and start your development server.
```

If no files were skipped, omit the "Skipped" section.

---

## `/aod.stack list`

Display all available stack packs with descriptions and active status.

### Step 1: Scan for available packs

1. Look for directories under `stacks/` that contain a `STACK.md` file.
2. If the `stacks/` directory does not exist, display:
   ```
   No stack packs found.

   Create stacks/{pack-name}/STACK.md to get started.
   See specs/058-prd-058-stack/contracts/stack-md-format.md for the format spec.
   ```
   Then stop.
3. If `stacks/` exists but no subdirectory contains a `STACK.md`, display:
   ```
   No stack packs found.

   Pack directories exist but none contain a STACK.md convention contract:
     - {list directories without STACK.md}

   Create a STACK.md in a pack directory to register it.
   See specs/058-prd-058-stack/contracts/stack-md-format.md for the format spec.
   ```
   Then stop.

### Step 2: Read active pack state

1. If `.aod/stack-active.json` exists, read its `pack` field.
2. If the file references a pack that does not exist under `stacks/`, display
   a warning: "WARNING: Active pack `{pack-name}` no longer exists in
   `stacks/`. Run `/aod.stack remove` to clean up stale state."
3. If `.claude/rules/stack/` has files but `.aod/stack-active.json` does not
   exist, display a warning: "WARNING: Orphaned rules found in
   `.claude/rules/stack/` with no activation state. Run `/aod.stack remove`
   to clean up."

### Step 3: Extract pack descriptions

For each pack directory containing a `STACK.md`:

1. Read the `STACK.md` file.
2. Find the first `#` heading (the pack title line, e.g., `# Next.js Supabase Stack`).
3. Extract the **Stack** field value from the Summary section (the line starting
   with `**Stack**:`) to use as the technology tagline.
4. Extract the **Use Case** field value from the Summary section (the line
   starting with `**Use Case**:`) to use as the description.
5. If these fields cannot be found, use the first non-heading, non-empty
   paragraph after the title as the description.

### Step 4: Display formatted list

Display the list using this format:

```
Available Stack Packs:

  * {active-pack-dir-name} (active)
    {Stack field value — e.g., Next.js . TypeScript . Supabase . Prisma . Vercel}
    {Use Case field value — e.g., Full-stack web applications with auth, database, and deployment}

    {other-pack-dir-name}
    {Stack field value}
    {Use Case field value}

Use: /aod.stack use {pack-name}
```

Rules:
- Prefix the active pack with `*` and append `(active)`.
- Indent non-active packs at the same level but without the `*` prefix.
- Leave one blank line between pack entries.
- Sort packs alphabetically by directory name.
- If no pack is active, omit the `*` prefix and `(active)` suffix from all entries.

---

## Error Handling (all subcommands)

### Inconsistent state detection

Apply these checks at the start of `use`, `list`, `remove`, and `scaffold`:

| Condition | Action |
|-----------|--------|
| `.aod/stack-active.json` exists but its `pack` field references a directory not in `stacks/` | Warn user, suggest `/aod.stack remove` |
| `.claude/rules/stack/` has `.md` files but `.aod/stack-active.json` does not exist | Warn user about orphaned rules, suggest `/aod.stack remove` |
| `.aod/stack-active.json` is not valid JSON | Warn user, suggest deleting the file manually and re-activating |

### Pack validation errors

When `use` encounters a STACK.md that is empty:
```
Invalid pack: stacks/{pack-name}/STACK.md is empty.

A valid STACK.md requires at minimum a Summary section.
See specs/058-prd-058-stack/contracts/stack-md-format.md for the format spec.
```

---

## Agent Tier Reference

Used by the persona-loader.md and context budget calculations.

| Tier | Agents | Pack Behavior |
|------|--------|---------------|
| **Core** | product-manager, architect, team-lead, orchestrator, web-researcher | Never modified by packs |
| **Specialized** | frontend-developer, senior-backend-engineer, security-analyst, tester, code-reviewer, devops | Persona supplements loaded |
| **Hybrid** | ux-ui-designer, debugger | Universal methodology + stack tooling supplement |

---

## File Paths Reference

| File | Purpose | Committed |
|------|---------|-----------|
| `stacks/{pack}/STACK.md` | Convention contract | Yes |
| `stacks/{pack}/agents/*.md` | Persona supplements | Yes |
| `stacks/{pack}/rules/*.md` | Source rules | Yes |
| `stacks/{pack}/scaffold/**` | Project template files | Yes |
| `.claude/rules/stack/*.md` | Runtime rules (copied on activation) | No (gitignored) |
| `.claude/rules/stack/persona-loader.md` | Generated persona loading instructions | No (gitignored) |
| `.aod/stack-active.json` | Activation state | No (gitignored) |

---

## Constraints

- Do NOT modify any files in `.claude/agents/` — persona supplements are additive context, not replacements.
- Do NOT register stack-specific skills (FR-002 skill registration is deferred).
- Core agent files are NEVER modified by pack activation.
- Only ONE pack can be active at a time.
- Pack removal does NOT affect scaffolded project files — removal only cleans agent context, not user code.
- Governance behavior (Triad reviews, lifecycle stages, sign-offs) is identical with or without an active pack.
