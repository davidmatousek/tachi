---
description: Quality review — code simplification, docstrings, CHANGELOG, API docs (supports --autonomous)
---

## User Input

```text
$ARGUMENTS
```

Consider user input before proceeding (if not empty).

## Step 0a: Parse --autonomous

1. If `$ARGUMENTS` contains `--autonomous`:
   - Set `autonomous = true`
   - Strip `--autonomous` from `$ARGUMENTS` (trim extra whitespace)
2. If `$ARGUMENTS` does NOT contain `--autonomous`:
   - Set `autonomous = false`

## Overview

Post-delivery quality review for the completed feature. This is Stage 6 of the AOD
lifecycle — the one stage designed for human judgment. Each step presents findings
interactively and commits only what the human approves.

**Flow**: Validate context → Branch → Code simplification → Docs-lint → CHANGELOG → API sync → KB review → PR squash-merge → Report

**IMPORTANT**: Execute ALL steps 0–7 sequentially. Do not stop or wait for further instructions between steps. After completing each step (including user interaction), immediately proceed to the next step until the Step 7 Report is displayed.

## Step 0: Validate Context

1. Get branch: `git branch --show-current`
2. Determine feature number NNN:
   - If on a `NNN-*` branch: extract NNN from branch name
   - If on `main`: extract NNN from user input `$ARGUMENTS`, or detect from most recent `feat(NNN)` or `docs(NNN)` commit on main
   - If NNN cannot be determined: prompt the user for the feature number
3. Find tasks: `specs/{NNN}-*/tasks.md` → verify all tasks marked `[X]` (build complete)
4. If tasks incomplete: warn "Build may not be complete — {incomplete_count} tasks remain" and ask whether to proceed
5. Display: "Document stage for Feature {NNN}"

## Step 0b: Create Document Branch

1. If not already on main: `git checkout main && git pull origin main`
2. Create branch: `git checkout -b {NNN}-document-stage`
3. Display: "Working on branch {NNN}-document-stage"

## Step 1: Code Simplification

Detect changed code files and run /simplify for human review.

### 1a: Detect Changed Files

1. Run: `git diff --name-only main...HEAD`
2. Filter to code extensions: `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.sh`, `.go`, `.rs`, `.java`, `.rb`, `.swift`, `.kt`
3. Exclude: `*.lock`, `*.min.js`, `*.min.css`, `*.map`, `*.generated.*`, `vendor/`, `dist/`, `build/`, `node_modules/`, `.aod/`, `docs/`
4. Store as `changed_files` list and `file_count`
5. If `file_count` is 0: display "No code files changed — skipping simplification", proceed to Step 2
6. If `file_count` > 50: warn "Large diff ({file_count} files). Simplify may take several minutes." and ask whether to continue or skip

### 1b: Run Simplification

1. Record pre-invocation file states: `git diff --name-only`
2. Invoke `/simplify` skill via Skill tool
3. If skill fails: display error, ask (A) Retry, (B) Skip → proceed to Step 2, (C) Abort

### 1c: Review Results

1. Detect modified files: `git diff --name-only`
2. If no files modified: display "No simplification changes — code looks good", proceed to Step 2
3. Get diff stats: `git diff --stat`
4. If `autonomous == true`: auto-accept all simplification changes — stage and commit with `refactor({NNN}): simplify code per /simplify review` → proceed to Step 2
5. If `autonomous == false`: Present summary via AskUserQuestion:
   ```
   Code Simplification Review:
     Files reviewed: {file_count}
     Files modified: {modified_count}
     Changes: +{insertions} -{deletions} lines

     {one-line summary per modified file}

   Options:
     (A) Accept all — commit as refactor({NNN}): simplify
     (B) Reject all — revert and continue
     (C) Abort
   ```
   - Accept: stage and commit with `refactor({NNN}): simplify code per /simplify review` → proceed to Step 2
   - Reject: revert modified files with `git checkout -- {files}` → proceed to Step 2

## Step 2: Docs-Lint

Analyze changed code for undocumented complex functions and suggest docstrings.

### 2a: Analyze Complexity

1. Use the `changed_files` list from Step 1a (re-detect if Step 1 was skipped)
2. Filter to supported languages: `.py`, `.ts`, `.tsx`, `.js`, `.jsx`, `.go`, `.rs`, `.java`
3. For each file, identify functions/methods and count branch statements (if, else, for, while, match, switch, case)
4. Flag functions where: complexity >= 3 AND no existing docstring
5. If no functions flagged: display "All complex functions are documented", proceed to Step 3

### 2b: Present Docstring Suggestions

1. For each flagged function, generate a docstring matching the file's existing style
2. If `autonomous == true`: auto-accept all suggested docstrings — apply docstrings, stage, commit with `docs({NNN}): add docstrings per docs-lint` → proceed to Step 3
3. If `autonomous == false`: Present via AskUserQuestion:
   ```
   Docs-Lint Review:
     Files analyzed: {file_count}
     Functions flagged: {flagged_count}

     {list each: file:line — function_name (complexity: N)}

   Options:
     (A) Accept all suggested docstrings
     (B) Skip all
     (C) Review individually
   ```
   - If accepted: apply docstrings, stage, commit with `docs({NNN}): add docstrings per docs-lint` → proceed to Step 3
   - If skipped or reviewed individually: apply approved changes (if any), then proceed to Step 3

## Step 3: CHANGELOG Generation

Generate CHANGELOG entries from the feature's delivery commits on main (not the document branch).

### 3a: Collect and Categorize Commits

1. Run: `git log --format="%H %s" main` and filter to commits matching `(NNN)` or the feature name from `specs/{NNN}-*/`
2. If no commits: display "No commits found", proceed to Step 4
3. If `CHANGELOG.md` exists: read it and exclude commits whose SHA (first 7 chars) already appear
4. If all commits already captured: display "CHANGELOG is up to date", proceed to Step 4
5. Parse conventional commit prefixes:
   - `feat:` → **Added**
   - `fix:` → **Fixed**
   - `refactor:`, `docs:`, `chore:`, `style:`, `perf:`, `test:` → **Changed**
   - Contains "remove"/"delete"/"drop" → **Removed**
   - Others → **Other**

### 3b: Generate and Review

1. Build markdown section: `### Feature {NNN}`
2. List entries by category with short SHA
3. Create `CHANGELOG.md` if missing (Keep a Changelog format)
4. If `autonomous == true`: auto-accept CHANGELOG entries — insert under `## [Unreleased]`, stage, commit with `docs({NNN}): update CHANGELOG` → proceed to Step 4
5. If `autonomous == false`: Present via AskUserQuestion:
   ```
   CHANGELOG Preview:
     New entries: {count}
     Categories: {list}

   (A) Accept and commit
   (B) Skip
   ```
   - If accepted: insert under `## [Unreleased]`, stage, commit with `docs({NNN}): update CHANGELOG` → proceed to Step 4
   - If skipped: proceed to Step 4

## Step 4: API Documentation Sync

Compare code endpoints against OpenAPI spec and flag mismatches.

### 4a: Discover Spec and Changed Endpoints

1. Search for OpenAPI spec: `openapi.yaml`, `openapi.json`, `swagger.yaml`, `swagger.json` in root, `docs/`, `api/`, `spec/`
2. If no spec found: display "No OpenAPI spec found — skipping", proceed to Step 5
3. Get changed files: `git diff --name-only main...HEAD`
4. Filter to API-relevant extensions: `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.go`, `.java`, `.rb`
5. Scan for framework endpoint patterns (FastAPI, Express, Flask decorators)
6. If no endpoints in changed files: display "No API endpoints changed", proceed to Step 5

### 4b: Compare and Report

1. Extract endpoint signatures from code (method, path, params, response type)
2. Parse OpenAPI spec for corresponding definitions
3. Identify mismatches: new endpoints, changed params, removed endpoints, response type diffs
4. If no mismatches: display "API docs are in sync", proceed to Step 5
5. If `autonomous == true`: auto-accept all mismatches — update spec for each mismatch, stage, commit with `docs({NNN}): sync OpenAPI spec` → proceed to Step 5
6. If `autonomous == false`: Present via AskUserQuestion:
   ```
   API Sync Review:
     Spec: {spec_path}
     Mismatches: {count}

     {list each mismatch}

   (A) Review each individually
   (B) Skip all
   ```
   - For each mismatch user approves: update spec, then stage and commit with `docs({NNN}): sync OpenAPI spec` → proceed to Step 5
   - If skipped: proceed to Step 5

## Step 5: KB Entry Review

Review knowledge base entries captured during build and deliver.

1. Check `docs/INSTITUTIONAL_KNOWLEDGE.md` for recent entries related to Feature {NNN}
2. If no entries found: display "No KB entries to review", proceed to Step 6
3. If `autonomous == true`: auto-accept KB entries as-is — commit any KB updates with `docs({NNN}): review KB entries` → proceed to Step 6
4. If `autonomous == false`: Present each entry for validation: confirm accuracy, improve wording if needed
5. Commit any KB updates with `docs({NNN}): review KB entries`

## Step 6: PR Squash-Merge

Push the document branch, create a PR, and squash-merge to main.

1. If no commits on the document branch (`git log main..HEAD --oneline` is empty): display "No changes to merge — skipping PR", proceed to Step 7
2. Push: `git push -u origin {NNN}-document-stage`
3. Create PR:
   ```
   gh pr create --title "docs({NNN}): post-delivery quality review" --body "$(cat <<'EOF'
   ## Summary
   Post-delivery documentation review for Feature {NNN}.

   {one-line summary per commit on the branch}

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```
4. If `autonomous == true`: proceed directly to squash-merge without confirmation
5. If `autonomous == false`: display PR URL and ask for confirmation before merging:
   ```
   PR created: {pr_url}

   (A) Squash-merge and delete branch
   (B) Leave PR open for manual review
   ```
   - If (B): display "PR left open — skipping merge", proceed to Step 7
6. Squash-merge: `gh pr merge --squash --delete-branch`
7. Switch to main: `git checkout main && git pull origin main`
8. Prune stale remote refs: `git remote prune origin`

## Step 7: Report

Display summary of all documentation activities:

```
DOCUMENT STAGE COMPLETE

Feature: {NNN}
PR: #{pr_number} (squash-merged)

Results:
  Code Simplification: {accepted/rejected/skipped/no changes}
  Docs-Lint: {N functions documented / skipped / no flags}
  CHANGELOG: {N entries added / skipped / up to date}
  API Sync: {N mismatches resolved / skipped / in sync / no spec}
  KB Review: {N entries reviewed / no entries}
```

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "Feature is delivered — I'll skip `/aod.document` and let the user run it later" | Without it, the Step 3 CHANGELOG, Step 4 OpenAPI sync, and Step 5 KB review drift from merged code. Run immediately after `/aod.deliver`. |
| "I'll pause between Step 1 (simplify) and Step 2 (docs-lint) to let the user verify" | Important note (line 29) requires steps 0-7 to execute sequentially without stops. The AskUserQuestion at each step IS the gate; pausing stalls the flow. |
| "I'll run `/aod.document --autonomous` to skip the AskUserQuestion prompts" | `--autonomous` (Step 0a) auto-accepts decisions at Steps 1c, 2b, 3b, 4b, 5, and 6. Reserved for `aod.run` orchestrator runs; pause at each gate interactively. |
| "I'll run `/aod.document` directly on the feature branch instead of `{NNN}-document-stage`" | Step 0b creates `{NNN}-document-stage` from main (line 45). Feature-branch use mixes build and post-delivery commits and breaks the Step 6 squash-merge. |

## Red Flags

- Agent invokes `/aod.document` on a feature branch whose build commits are not yet merged to main.
- Agent stops mid-flow between Steps 0-7 waiting for instructions despite the line 29 "Do not stop" rule.
- Agent runs `--autonomous` outside an `aod.run` orchestrator context and rubber-stamps every Step 1-5 change.
- Agent skips Step 0b branch creation and commits directly on the feature branch.
- Agent reports "DOCUMENT STAGE COMPLETE" without producing the Step 7 per-stage Results breakdown.
