---
name: ~aod-kickstart
description: >-
  POC kickstart skill that transforms a project idea into a sequenced consumer
  guide with 6-10 seed features. Use when a developer invokes /aod.kickstart to
  generate a consumer guide, when starting a new project and needing a structured
  backlog plan, or when converting a project idea into seed features for the AOD
  lifecycle. Three-stage workflow: Idea Intake, Stack Selection, Guide Generation.
---

# /aod.kickstart Skill

## Purpose

Transform a project idea into a sequenced consumer guide with 6-10 seed features ready for the AOD lifecycle. The skill runs three stages:

1. **Idea Intake** -- Capture the project idea, target user, and key capabilities through structured prompts
2. **Stack Selection** -- Detect an active stack pack or guide the developer to select/describe a stack
3. **Guide Generation** -- Produce a consumer guide at `docs/guides/CONSUMER_GUIDE_{PROJECT_NAME}.md` with setup phases, a feature summary table, and per-feature seed blocks ordered for incremental value delivery

Each seed feature block is structured for direct copy-paste into `/aod.discover`.

---

## Prerequisites Check

Before starting, validate the output directory exists.

1. Use Glob to check for `docs/guides/` directory
2. If `docs/guides/` does not exist, display the following error and stop:

```
ERROR: docs/guides/ directory not found.
Run `make init` to set up project structure.
```

Do not proceed to Stage 1 until `docs/guides/` is confirmed to exist.

---

## Stage 1: Idea Intake

Capture the project idea through 5 structured prompts. Store responses in variables for use in later stages.

### Step 1.1: Capture Idea Description

Use AskUserQuestion:

```
Question: "Describe your project idea (what are you building and why?)"
```

Store the response as `{idea_description}`.

**Vagueness validation (FR-014)**: Count the words in the response. If fewer than 20 words, ask for elaboration:

```
Question: "Your idea description is brief. Add more detail about what the project does, the problem it solves, or key workflows (aim for 2-3 sentences)."
```

Allow up to 2 rounds of clarification. If still under 20 words after 2 rounds, accept the response as-is and proceed with a note:

```
Note: Idea description is brief. The generated guide may need refinement.
```

### Step 1.2: Capture Target User

Use AskUserQuestion:

```
Question: "Who is the target user for this project?"
```

Store the response as `{target_user}`.

Expected responses: persona descriptions such as "solo developer," "small team lead," "project manager," "end consumer."

### Step 1.3: Capture Key Capabilities

Use AskUserQuestion:

```
Question: "List 3-5 key capabilities this project needs (one per line)"
```

Store the response as `{capabilities}`.

**Scope check (FR-015)**: Count the listed capabilities.

- If more than 5 capabilities, display:

```
You listed {count} capabilities. For a POC, recommend narrowing to 3-5 core capabilities. Which ones are essential for the first version?
```

Then re-prompt with AskUserQuestion to capture the narrowed list. Accept the revised list.

- If fewer than 3 capabilities, display:

```
A POC typically needs at least 3 capabilities to demonstrate value. Can you add more?
```

Then re-prompt with AskUserQuestion to capture additional capabilities.

### Step 1.4: Capture GitHub Org

Use AskUserQuestion:

```
Question: "What is your GitHub org or username? (used for repo creation in the guide)"
```

Store the response as `{github_org}`.

### Step 1.5: Confirm Summary

Display the captured information:

```
PROJECT IDEA SUMMARY

Idea: {idea_description}
Target User: {target_user}
GitHub Org: {github_org}
Key Capabilities:
  1. {capability_1}
  2. {capability_2}
  3. {capability_3}
  ...
```

Use AskUserQuestion:

```
Question: "Does this look right?"
Options:
  - Yes: "Proceed to stack selection"
  - Edit idea: "Change the project idea description"
  - Edit user: "Change the target user"
  - Edit org: "Change the GitHub org"
  - Edit capabilities: "Change the key capabilities"
```

- If "Yes": proceed to Stage 2
- If "Edit idea": return to Step 1.1
- If "Edit user": return to Step 1.2
- If "Edit org": return to Step 1.4
- If "Edit capabilities": return to Step 1.3

---

## Stage 2: Stack Selection

Determine the technology stack for guide generation. Four paths based on current state and developer preference.

### Step 2.1: Check for Active Pack

Read `.aod/stack-active.json` using the Read tool.

- **If file exists and contains valid JSON** with a `pack` field: extract `{pack_name}` and proceed to Step 2.2 (Path A)
- **If file does not exist, is empty, or has invalid JSON**: proceed to Step 2.3 (Path B — no active pack)

### Step 2.2: Active Pack Detected (Path A)

1. Read `stacks/{pack_name}/STACK.md` (first 20 lines)
2. Extract the `**Stack**:` line value as `{stack_description}`
3. Display:

```
Active pack detected: {pack_name} ({stack_description})
```

4. Use AskUserQuestion:

```
Question: "Use this pack for guide generation?"
Options:
  - Yes: "Use {pack_name}"
  - Change: "Select a different pack or describe a custom stack"
```

- If "Yes": store `{selected_pack} = {pack_name}`, proceed to Stage 3
- If "Change": proceed to Step 2.3 (Path B)

### Step 2.3: No Active Pack — Enumerate Available Packs (Path B)

1. Glob `stacks/*/STACK.md`. If none found: skip to Path C (custom stack)
2. For each STACK.md, read first 20 lines and extract pack name (directory name), `**Stack**:` value, `**Use Case**:` value
3. Display numbered list: `{N}. {pack_name} — {stack_value}` with `Use case: {use_case}` on next line
4. AskUserQuestion: "Select a stack pack for guide generation" with options: one per discovered pack + "Help me choose" (→ Step 2.4 Path D) + "Custom stack" (→ Step 2.5 Path C)
5. If pack selected: store `{selected_pack}`, proceed to Stage 3

### Step 2.4: Guided Selection Questions (Path D)

Ask 4 questions via AskUserQuestion to recommend the best-fit pack from those discovered in Step 2.3:

1. "What type of project?" → Options: Web app | Mobile app | CLI tool | API service | Knowledge system → store `{project_type}`
2. "Where will this be deployed?" → Options: Local development | Cloud (AWS/GCP/Azure) | Serverless | App Store → store `{deployment_target}`
3. "Primary programming language?" → Options: Python | TypeScript | Swift | Rust | Other → store `{primary_language}`
4. "Database preference?" → Options: SQL (PostgreSQL, SQLite) | NoSQL (MongoDB, DynamoDB) | Managed (Supabase, Firebase) | None → store `{db_preference}`

**Recommendation**: Match answers against pack metadata (`**Stack**:` for language, `**Deployment**:` for target, `**Use Case**:` for project type). Display:

```
Recommended: {best_fit_pack} ({stack_description})
Rationale: {1-2 sentences}
Alternatives: {alt_pack_1} — {reason}, {alt_pack_2} — {reason}
```

AskUserQuestion: "Use the recommended pack?" with options: "Yes" (use recommendation) | each alternative pack | "Custom stack" (→ Step 2.5 Path C). Store `{selected_pack}`, proceed to Stage 3.

### Step 2.5: Custom Stack Capture (Path C)

When the developer selects "Custom stack" from Path B or Path D, capture their technology stack.

Use AskUserQuestion:

```
Question: "Describe your technology stack (languages, frameworks, database, deployment target)"
```

Store the response as `{custom_stack_description}`. Set `{selected_pack}` to empty (no pack selected). Proceed to Stage 3.

---

## Stage 3: Guide Generation

Generate the consumer guide document. This stage is autonomous — no user interaction except conflict detection.

### Step 3.1: Load Pack Conventions

**If `{selected_pack}` is set** (pack-based generation):

1. Read `stacks/{selected_pack}/STACK.md` in full
2. Extract these fields from the file:
   - `**Stack**:` → `{stack_tech}` (e.g., "Python 3.12, FastAPI, React 18, SQLite")
   - `**Use Case**:` → `{use_case}`
   - `**Target**:` → `{pack_target}`
   - `**Deployment**:` → `{deployment}`
   - `## Architecture Pattern` section → `{architecture_notes}` (key conventions)
3. Store all extracted fields for use in guide content

**If no pack selected** (custom stack path):

Use the `{custom_stack_description}` captured in Stage 2 Path C as the stack context. Set `{stack_tech}` to the developer's described technologies.

### Step 3.2: Derive Project Name

From `{idea_description}`, derive a short project name:

1. Extract the core noun phrase (e.g., "a task management API" → "Task Manager API")
2. Convert to SCREAMING_SNAKE_CASE for the filename: `TASK_MANAGER_API`
3. Store as `{project_name}` (display) and `{file_name}` (SCREAMING_SNAKE_CASE)
4. Output path: `docs/guides/CONSUMER_GUIDE_{file_name}.md`

### Step 3.3: Generate Guide Content

Using the Guide Template (below), generate the full consumer guide. The content must:

1. **Header**: Use `{idea_description}`, `{target_user}`, and `{capabilities}` from Stage 1
2. **Setup phases**: Use `{selected_pack}` conventions if pack-based, or generic instructions if custom stack
3. **Requirements**: Derive functional requirements from `{capabilities}`
4. **Feature summary table**: List all seed features with IDs, groups, story counts, and dependency annotations
5. **Seed feature blocks**: Generate 6-10 features following the Ordering Principles (below), each with goal, stories, interface contracts, and DoD
6. **Execution guide**: Standard AOD lifecycle instructions
7. **Quick Start Commands**: Pre-formatted `/aod.discover --seed read #### F-NNN: {name} in {guide_path}` commands for every feature, enabling one-command-per-feature GitHub Issue creation
8. **Completion tracker**: Checkbox table for all features

**Custom stack generation**: When `{selected_pack}` is empty (custom stack), use `{custom_stack_description}` for all stack-dependent content. Seed features must be technology-appropriate — e.g., a Django + HTMX project should reference Django views, HTMX partials, and Django ORM patterns, not generic REST boilerplate. Infer architecture patterns from the described technologies.

### Step 3.4: Conflict Detection (FR-012)

Before writing, check for an existing guide at the target path.

1. Glob `docs/guides/CONSUMER_GUIDE_*.md`
2. If a file matching `docs/guides/CONSUMER_GUIDE_{file_name}.md` exists, display:

```
Existing guide found: docs/guides/CONSUMER_GUIDE_{file_name}.md
```

3. Use AskUserQuestion:

```
Question: "A consumer guide already exists at this path. What would you like to do?"
Options:
  - Overwrite: "Replace the existing guide"
  - Rename: "Save as a date-suffixed alternative (CONSUMER_GUIDE_{file_name}_{YYYY-MM-DD}.md)"
  - Cancel: "Cancel guide generation"
```

- If "Overwrite": proceed to Step 3.5 with the original path `docs/guides/CONSUMER_GUIDE_{file_name}.md`
- If "Rename": update output path to `docs/guides/CONSUMER_GUIDE_{file_name}_{YYYY-MM-DD}.md` (using today's date), proceed to Step 3.5
- If "Cancel": display "Kickstart cancelled. No files were written." and stop execution

4. If no matching file exists: proceed to Step 3.5 with the original path

### Step 3.5: Write Guide File

1. Use the Write tool to create the guide at the determined output path
2. Display completion summary:

```
Guide written to docs/guides/CONSUMER_GUIDE_{file_name}.md
  - {feature_count} seed features across {group_count} groups
  - {line_count} lines
  - Quick Start Commands included for one-command seeding
  - Ready for /aod.discover intake

Next steps:
  Use the Quick Start Commands section to seed all features into GitHub Issues.
  Copy-paste each command into Claude Code — one per feature, in dependency order.
  Then run the AOD lifecycle for each: /aod.define → /aod.deliver
```

---

## Guide Template

At the start of Step 3.3, use the Read tool to load `KICKSTART_TEMPLATE.md` (co-located with this SKILL.md in `.claude/skills/~aod-kickstart/`). This template defines the exact structure, section ordering, and formatting for all generated consumer guides — including setup phases, feature blocks, and tail sections. Follow it section by section, replacing all `{placeholders}` with actual content derived from Stages 1-2.

Derive `{project_slug}` from `{project_name}` (lowercase, kebab-case). Use `{github_org}` from Step 1.4.

---

## Ordering Principles

Order seed features according to these tiers (FR-009). Every generated guide must follow this sequence.

| Tier | Position | Examples |
|------|----------|----------|
| Foundation | First | Project skeleton, health check, data models, config, environment setup |
| Core Value | Second | Primary CRUD/workflow, business logic, core API endpoints or CLI commands |
| User-Facing | Third | Dashboard/UI views, interactions, forms, notifications, auth |
| Polish | Last | Error handling, external integrations, performance, monitoring |

### Ordering Rules

1. Each feature must be **independently demonstrable** — a developer can verify it works after completion
2. Each feature **only depends on earlier features** — never on a later feature in the sequence
3. **No circular dependencies** — validate the dependency graph is a DAG before writing
4. **Group related features** — use Group headings (Foundation, Core, User-Facing, Polish)
5. **Dependency chain in summary table** — `Depends On` column must reflect the actual dependency graph

---

## Edge Cases

- **No `stacks/` directory**: Skip pack recommendation entirely. Proceed directly to custom stack path (Path C)
- **Empty `stacks/` directory** (no STACK.md files found): Same as above — proceed to custom stack path
- **Invalid `.aod/stack-active.json`** (malformed JSON or missing `pack` field): Treat as no active pack — proceed to Path B
- **Pack in `stack-active.json` not found on disk**: Display warning "Pack '{pack_name}' is configured but not found in stacks/. Proceeding without pack." then proceed to Path B
- **Vague idea after 2 clarification rounds**: Accept the response as-is. Display note: "Idea description is brief. The generated guide may need refinement." Generate best-effort guide
- **User aborts at any stage**: Exit gracefully. Do not write any files. Display "Kickstart cancelled. No files were written."
- **Generated feature count outside 6-10 range**: Adjust by merging small features (if > 10) or expanding scope (if < 6) to stay within the required range
- **Dependency cycle detected**: Reorder features to eliminate the cycle before writing the guide. Foundation features must have no upstream dependencies

---

## Constraints

- **Read-only enforcement (FR-016)**: This skill MUST NOT modify any files outside of `docs/guides/`. The following directories are read-only: `.aod/`, `.claude/`, `stacks/`. Only the Write tool targeting `docs/guides/CONSUMER_GUIDE_*.md` is permitted
- **No pack state modification (FR-017)**: This skill MUST NOT activate, deactivate, or modify stack pack state. Stack activation is handled separately via `/aod.stack use`. Never write to `.aod/stack-active.json`
- **Feature count (FR-010)**: Generate exactly 6-10 seed features. Fewer than 6 does not demonstrate enough scope; more than 10 overwhelms a POC
- **Guide line budget (SC-007)**: Generated guides must be 200-600 lines. Enough detail to be actionable, not so much that it overwhelms
- **Discover compatibility (FR-013, SC-004)**: Each seed feature block (from `#### F-NNN:` to `---`) must be directly copy-pasteable into `/aod.discover` as the idea description. The block must contain goal, stories with acceptance criteria, interface contracts, and DoD in the exact format shown in `KICKSTART_TEMPLATE.md`
- **Skill file budget (SC-008)**: This SKILL.md file must remain under 500 lines
- **No GitHub Issues (NFR-5)**: This skill is idempotent — it only produces a guide document. It does not create GitHub Issues, modify backlog state, or trigger any side effects beyond writing the guide file
