---
name: ~aod-blueprint
description: >-
  Unified project setup and story generation skill that auto-detects new vs
  existing projects. Three modes: first-run (creates repo, registers project,
  activates), subsequent-run (skips setup, adds new stories with deduplication),
  and demo (loads pre-built Hello World stories). Generates ICE-scored,
  dependency-ordered stories as GitHub Issues and outputs a consumer guide.
  Use when a developer invokes /aod.blueprint to bootstrap or extend a project.
---

# /aod.blueprint Skill

## Purpose

Unified project setup and story generation in a single command. The skill auto-detects whether the current project is new or existing, then runs the appropriate workflow:

1. **First-Run** -- Creates GitHub repo, registers project with orchestrator API, activates it, runs interactive intake, generates stories, creates issues
2. **Subsequent-Run** -- Skips setup, runs interactive intake, generates new stories with deduplication against existing issues
3. **Demo Mode** (`--demo`) -- Loads pre-built Hello World stories from `HELLO_WORLD_STORIES.md`, skips interactive intake entirely

All modes end with issue creation, lifecycle sync, consumer guide generation, and a completion report.

---

## Step 0: Prerequisites Check

Validate that required tools and services are available before proceeding.

### 0.1: Check gh CLI

Run `gh --version` via Bash tool.

- If the command succeeds, continue to Step 0.2.
- If the command fails, display the following error and STOP:

```
ERROR: GitHub CLI (gh) is not installed or not in PATH.
Install it from https://cli.github.com/ and run `gh auth login` to authenticate.
```

### 0.2: Check API Health

Run the following command via Bash tool:

```bash
curl -sf ${AOD_API_URL:-http://localhost:8000}/health -H "X-AOD-Source: skill"
```

- If the command succeeds (exit code 0), display "Prerequisites OK" and continue to Step 1.
- If the command fails, display the following error and STOP:

```
ERROR: AOD Orchestrator API is not reachable at ${AOD_API_URL:-http://localhost:8000}.
Start the API with `make run` and try again.
```

---

## Step 1: Auto-Detection

Determine the project name, check for an existing project in the orchestrator, and set the execution mode.

### 1.1: Derive Project Name

Run `git remote get-url origin` via Bash tool.

- If the command succeeds, extract the repo name from the URL: take the last path segment and strip any `.git` suffix. For example, `https://github.com/org/my-project.git` yields `my-project`. Store as `{project_name}`.
- If the command fails (no remote configured), run `basename $(pwd)` via Bash tool and store the result as `{project_name}`.

### 1.2: Check for Existing Project

Run the following command via Bash tool:

```bash
curl -sf ${AOD_API_URL:-http://localhost:8000}/api/v1/projects -H "X-AOD-Source: skill"
```

Parse the JSON response. Filter for a project where:
- The `name` field matches `{project_name}` (case-insensitive comparison), OR
- The `repo_url` field contains `{project_name}`

### 1.3: Set Mode

Based on the result of Step 1.2:

- **If no matching project found** → set `mode = first-run`
- **If a matching project found** → set `mode = subsequent-run`, store the matched project's `id` as `{project_id}`

### 1.4: Parse Demo Flag

Check `$ARGUMENTS` for the `--demo` flag.

- If `$ARGUMENTS` contains `--demo` → set `demo = true`
- Otherwise → set `demo = false`

### 1.5: Display Detection Result

Display the detected configuration:

```
Mode: {first-run|subsequent-run}
Demo: {yes|no}
Project: {project_name}
```

Continue to Step 2.

---

## Step 2: First-Run Setup

**If `mode = subsequent-run`**: Skip this step entirely. The `{project_id}` was stored in Step 1.3. Continue to Step 3.

Create the GitHub repo (if needed), register the project with the orchestrator API, and activate it.

### 2.1: Check for Existing GitHub Repo

Run the following command via Bash tool:

```bash
gh repo view {project_name} 2>/dev/null
```

- If exit code is 0 (repo exists): skip repo creation. Extract the repo URL from the output and store as `{repo_url}`. Continue to Step 2.3.
- If exit code is non-zero (no repo): continue to Step 2.2.

### 2.2: Create GitHub Repo

Derive the GitHub org from the git remote. Run `git remote get-url origin` via Bash tool and extract the org/owner segment from the URL. For example, `https://github.com/my-org/some-repo.git` yields `my-org`.

- If no remote is available, use AskUserQuestion to ask: "What is your GitHub org or username? (used for repo creation)"
- Store the result as `{github_org}`.

Run the following command via Bash tool:

```bash
gh repo create {github_org}/{project_name} --public
```

Store the created repo URL as `{repo_url}`.

### 2.3: Register Project

Run the following command via Bash tool:

```bash
curl -sf -X POST ${AOD_API_URL:-http://localhost:8000}/api/v1/projects \
  -H "Content-Type: application/json" \
  -H "X-AOD-Source: skill" \
  -d '{"name":"{project_name}","repo_url":"{repo_url}","github_owner":"{github_org}","github_repo":"{project_name}","worktree_root":"{pwd}","aod_kit_path":"{pwd}"}'
```

Parse the JSON response and extract the `id` field. Store as `{project_id}`.

### 2.4: Activate Project

Run the following command via Bash tool:

```bash
curl -sf -X PATCH ${AOD_API_URL:-http://localhost:8000}/api/v1/projects/{project_id}/activate \
  -H "X-AOD-Source: skill"
```

### 2.5: Confirm Setup

Display: "Project '{project_name}' registered and activated (ID: {project_id})"

Continue to Step 3.

---

## Step 3: Story Generation

**If `demo = true`**: Skip to Step 3D (Demo Mode) below.

### 3.1: Capture Idea (Stage 1)

Use AskUserQuestion to capture the project idea:

```
Question: "Describe your project idea (what are you building and why?)"
```

Store as `{idea_description}`. Count words — if fewer than 20, ask for elaboration:

```
Question: "Your idea description is brief. Add more detail about what the project does, the problem it solves, or key workflows (aim for 2-3 sentences)."
```

Allow up to 2 clarification rounds. If still under 20 words after 2 rounds, accept as-is with note: "Note: Idea description is brief. Generated stories may need refinement."

### 3.2: Capture Target User

Use AskUserQuestion:

```
Question: "Who is the target user for this project?"
```

Store as `{target_user}`.

### 3.3: Capture Key Capabilities

Use AskUserQuestion:

```
Question: "List 3-5 key capabilities this project needs (one per line)"
```

Store as `{capabilities}`. Count the listed items:
- If more than 5: "You listed {count} capabilities. For a blueprint, recommend narrowing to 3-5 core capabilities. Which ones are essential?" Re-prompt once.
- If fewer than 3: "A blueprint typically needs at least 3 capabilities to generate meaningful stories. Can you add more?" Re-prompt once.

### 3.4: Confirm Summary

Display the captured information:

```
BLUEPRINT INTAKE SUMMARY

Idea: {idea_description}
Target User: {target_user}
Key Capabilities:
  1. {capability_1}
  2. {capability_2}
  ...
```

Use AskUserQuestion: "Does this look right?" with options:
- "Yes, proceed to stack selection"
- "Edit idea"
- "Edit target user"
- "Edit capabilities"

If "Yes": proceed to Step 3.5. Otherwise loop back to the relevant step.

### 3.5: Stack Selection (Stage 2)

Read `.aod/stack-active.json` using the Read tool.

**If file exists with valid JSON and a `pack` field**:
1. Extract `{pack_name}`, read `stacks/{pack_name}/STACK.md` (first 20 lines) for `{stack_description}`
2. Display: "Active pack detected: {pack_name} ({stack_description})"
3. AskUserQuestion: "Use this pack for story generation?" — "Yes" or "Select different stack"
4. If "Yes": store `{selected_pack} = {pack_name}`, proceed to Step 3.6

**If no active pack or user wants different**:
1. Glob `stacks/*/STACK.md`. If packs found, display numbered list and ask user to select, with options for "Help me choose" and "Custom stack"
2. If "Help me choose": ask 4 guided questions (project type, deployment, language, database), recommend best-fit pack
3. If "Custom stack" or no packs exist: AskUserQuestion "Describe your technology stack (languages, frameworks, database, deployment target)". Store as `{custom_stack_description}`, set `{selected_pack}` to empty

### 3.6: Generate Stories (Stage 3)

**If `{selected_pack}` is set**: Read `stacks/{selected_pack}/STACK.md` for full stack context.
**If custom stack**: Use `{custom_stack_description}` as stack context.

Generate 6-10 stories from the captured idea, capabilities, and stack. Each story must include:
- **Title**: Short descriptive name
- **Description**: 1-2 sentence summary
- **User Story**: As a {target_user}, I want {capability}, so that {benefit}
- **ICE Score**: Impact (1-10), Confidence (1-10), Effort (1-10)
- **DoD Checklist**: 3-5 concrete acceptance criteria

Order by dependency tier: **Foundation → Core → User-Facing → Polish**.

Display all stories to the user for confirmation before proceeding. Use AskUserQuestion: "Confirm these stories?" — "Yes, create issues" or "Regenerate stories". If regenerate, re-run generation with user feedback.

Store confirmed stories as `{stories}` list. Continue to Step 4.

### Step 3D: Demo Mode

When `demo = true`, skip all interactive intake.

1. Read `docs/guides/HELLO_WORLD_STORIES.md` via Read tool.
   - If file is missing, display error and STOP:
     ```
     ERROR: Demo stories file not found at docs/guides/HELLO_WORLD_STORIES.md.
     Run without --demo for interactive mode.
     ```
2. Parse stories by `## Story N:` headings. For each story, extract:
   - Title from `**Title**:` line (strip backticks)
   - User story from `**As a ...** ` line
   - Acceptance criteria from `### Acceptance Criteria` section
   - Technical notes from `### Technical Notes` section
3. Convert to internal story format with pre-set ICE scores: Impact 8, Confidence 9, Effort 7 for all demo stories. Derive DoD from acceptance criteria.
4. Set `{idea_description}` = "Hello World Greeting Dashboard", `{target_user}` = "developer evaluating AOD", `{capabilities}` from The App section.

Store parsed stories as `{stories}` list. Continue to Step 4.

---

## Step 4: Issue Creation with Deduplication

Derive `{owner}` and `{repo}` from the git remote URL (or from `{github_org}` and `{project_name}` used in Step 2).

### 4.1: Fetch Existing Issues

Run via Bash tool:

```bash
gh issue list --repo {owner}/{repo} --limit 200 --json title,number,url
```

Parse the JSON response into a list of existing issue titles and numbers.

### 4.2: Create Issues with Dedup

For each story in `{stories}`, in order:

1. Compare the story title against existing issue titles (case-insensitive exact match)
2. **If match found**: Log "Skipping duplicate: {title} (matches #{number})". Store the matched issue number and URL.
3. **If no match**: Create the issue via Bash tool:

```bash
bash .aod/scripts/bash/create-issue.sh --title "{story_title}" --body "{formatted_body}" --stage discover
```

The `{formatted_body}` must include: user story, ICE score breakdown, DoD checklist, dependency tier, and description.

4. After each creation, run `sleep 1` (rate limit protection per FR-010)
5. Store the created issue number (from script stdout) and construct the URL as `https://github.com/{owner}/{repo}/issues/{number}`

### 4.3: Summary

After all stories are processed, display:

```
Issues: {created_count} created, {skipped_count} duplicates skipped
```

Store all issue numbers and URLs (both new and matched) as `{issue_results}` for Step 6.

---

## Step 5: Lifecycle Sync

After all issues are created, sync with the orchestrator lifecycle engine.

Run via Bash tool (non-blocking per KB #14):

```bash
curl -sf -X POST ${AOD_API_URL:-http://localhost:8000}/api/v1/projects/{project_id}/issues/sync \
  -H "X-AOD-Source: skill" || true
```

- If the command succeeds: Display "Issues synced with orchestrator"
- If the command fails (caught by `|| true`): Display "Warning: Issue sync failed. Issues are created but may not appear in orchestrator until next sync." Continue to Step 6 regardless.

---

## Step 6: Consumer Guide Generation

### 6.1: Load Template

Read `BLUEPRINT_TEMPLATE.md` (co-located with this SKILL.md in `.claude/skills/~aod-blueprint/`) via the Read tool.

### 6.2: Generate Guide Content

Replace all template placeholders with actual values:
- `{project_name}`: from Step 1.1
- `{idea_description}`, `{target_user}`, `{capabilities_list}`: from Step 3 intake (or demo defaults)
- `{stack_description}`: from `{selected_pack}` STACK.md description, or `{custom_stack_description}` if custom
- `{date}`: current date (YYYY-MM-DD)
- `{story_*}` fields: from `{stories}` list
- `{issue_number}`, `{issue_url}`: from `{issue_results}` (Step 4)
- Tier groupings for execution order table

Derive `{PROJECT}` as SCREAMING_SNAKE_CASE from `{project_name}` (e.g., `my-project` → `MY_PROJECT`).

### 6.3: Write Guide (Non-Blocking)

Write the generated guide to `docs/guides/BLUEPRINT_{PROJECT}.md` via Write tool. On subsequent runs, overwrite the existing file (full regeneration per FR-016).

- If write succeeds: Display "Consumer guide written to docs/guides/BLUEPRINT_{PROJECT}.md"
- If write fails: Display "Warning: Guide generation failed. Issues are created — guide can be regenerated by re-running /aod.blueprint." Continue to Step 7 regardless.

---

## Step 7: Completion Report

Display a summary of everything that was done:

```
BLUEPRINT COMPLETE

Mode: {first-run|subsequent-run|demo}
Project: {project_name} (ID: {project_id})
Stories: {story_count} generated
Issues: {created_count} created, {skipped_count} duplicates skipped
Guide: docs/guides/BLUEPRINT_{PROJECT}.md

Next step: /aod.run
```

---

## Edge Cases

- **Orchestrator API unreachable**: Fast-fail at Step 0.2 with setup instructions. No partial state created.
- **`gh` CLI not installed or not authenticated**: Fast-fail at Step 0.1. Display install link and `gh auth login` instructions.
- **Project exists in GitHub but not in orchestrator**: First-run mode — skip repo creation (Step 2.1 detects existing repo), proceed with registration.
- **GitHub API rate limiting during issue creation**: The 1-second delay between `create-issue.sh` calls (Step 4.2) provides baseline protection. If `create-issue.sh` fails, log the error and continue with remaining stories.
- **`HELLO_WORLD_STORIES.md` missing with `--demo`**: Error with suggestion to run without `--demo` (Step 3D).
- **`worktree_root` not a git repo**: `POST /api/v1/projects` returns validation error. Display the error message and STOP.
- **User aborts at any intake step**: Exit gracefully. No issues created, no partial state.
- **Generated story count outside 6-10**: Adjust during generation — merge small stories if >10, expand scope if <6.

---

## Constraints

- **SKILL.md line budget**: This file must stay ≤500 lines (KB #12). Use BLUEPRINT_TEMPLATE.md for guide structure.
- **No kickstart modifications**: `/aod.kickstart` must remain unmodified (FR-018). Blueprint implements patterns independently.
- **ADR-016 headers**: All `curl` calls must include `-H "X-AOD-Source: skill"`.
- **Issue creation script**: All GitHub Issue creation must use `.aod/scripts/bash/create-issue.sh` (KB #20), not raw `gh issue create`.
- **Bash 3.2 compatibility**: Any inline bash scripts must avoid `declare -A`, `${var^}`, `readarray`, `|&`, `&>` (KB #6).
- **Non-fatal pattern**: Sync (Step 5) and guide generation (Step 6) must never block the critical workflow. Use `|| true` guards (KB #14).
