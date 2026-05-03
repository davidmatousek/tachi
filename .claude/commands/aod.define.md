---
description: Create PRD with Triad governance (PM + Architect + Team-Lead sign-offs) - Streamlined v2
---

## User Input

```text
$ARGUMENTS
```

Consider user input before proceeding (if not empty).

## Step 0: Parse --autonomous

1. If `$ARGUMENTS` contains `--autonomous`:
   - Set `autonomous = true`
   - Strip `--autonomous` from `$ARGUMENTS` (trim extra whitespace)
2. Default: `autonomous = false`

## Step 0y: Parse --revision

1. If `$ARGUMENTS` contains `--revision`:
   - Set `revision_mode = true`
   - Strip `--revision` from `$ARGUMENTS` (trim extra whitespace)
   - Read `.aod/revision-context.md` for reviewer feedback (contains reviewer name, attempt number, artifact path, and full feedback text)
   - Store feedback as `revision_feedback`
2. Default: `revision_mode = false`

## Overview

Wraps ~aod-define skill with automatic Triad triple sign-off.

**Flow**: Check vision docs → Validate topic → Classify type → Draft PRD → Reviews → Handle blockers → Inject frontmatter → Update INDEX

## Step 0: Check Product Vision (Optional)

Check if product vision documents exist:
- `docs/product/01_Product_Vision/product-vision.md`

**If vision docs DON'T exist** (first PRD for this project):
1. **If `autonomous == true`**: Auto-select `"Skip"`. Display: `"Auto-selected: Skip vision workshop (autonomous mode)"`. Proceed directly to Step 1.
2. Use AskUserQuestion:
   - **Quick Vision**: Answer 3 questions to create vision docs (recommended for new projects)
   - **Skip**: Proceed directly to PRD creation (for experienced users)

2. If "Quick Vision" selected, run mini-workshop:

```
🎯 Quick Product Vision (3 questions)

Q1: What problem are you solving and for whom?
(1-2 sentences: the pain point and who experiences it)

Q2: What's your solution in one sentence?
(How your product solves the problem differently)

Q3: What are the 2-3 core features?
(Brief list of key capabilities)
```

3. Generate `docs/product/01_Product_Vision/product-vision.md` with their answers:
   - Mission statement (derived from Q1+Q2)
   - Problem statement (Q1)
   - Solution overview (Q2)
   - Core capabilities table (Q3)

**If vision docs exist BUT contain `[To be refined]` markers** (seeded by `make init`):
1. **If `autonomous == true`**: Skip vision refinement. Display: `"Auto-selected: Skip vision refinement (autonomous mode)"`. Proceed to Step 1.
2. Display the current seeded vision (mission statement from init)
3. Run **Vision Refinement Workshop** — use AskUserQuestion for each:

```
🎯 Vision Refinement Workshop (5 questions)

Your mission is currently: "{current mission statement}"

Q1: What change do you want to create in the world?
(Refine or expand your mission — 1-2 sentences)
→ Replaces Mission Statement

Q2: Where will {project_name} be in 3-5 years?
(Your aspirational future state)
→ Replaces Vision Statement

Q3: Who is the primary user and what problem do they face?
(e.g., "CTOs who need to assess AI security posture")
→ Replaces Target Users

Q4: What makes this different from alternatives?
(Your unique value — why you, why now?)
→ Replaces Core Value Proposition

Q5: How will you measure success? (1-2 key metrics)
(e.g., "Monthly active users", "Conversion rate")
→ Replaces Success Metrics
```

3. Write refined answers back to `product-vision.md`, replacing all `[To be refined during /aod.define]` markers
4. Proceed to Step 1

**If vision docs exist and NO `[To be refined]` markers**:
1. **Placeholder Guard**: Scan all files in `docs/product/01_Product_Vision/` for unresolved template placeholders: `{{PROJECT_NAME}}`, `{{CURRENT_DATE}}`, `{{TEMPLATE_VARIABLES}}`
   - If any placeholders found: Display a non-blocking warning:
     ```
     Template placeholders detected in vision files:
       - {file_path}: {{PLACEHOLDER_NAME}}, {{PLACEHOLDER_NAME}}
       - {file_path}: {{PLACEHOLDER_NAME}}

     These placeholders may propagate into PRDs. Consider resolving them
     via /aod.stack scaffold or manual replacement before proceeding.
     ```
   - If no placeholders found: No output (silent pass)
   - **Non-blocking**: PRD creation proceeds regardless of findings
2. Skip to Step 1

## Step 1: Validate Topic

1. Parse topic from `$ARGUMENTS` (kebab-case format)
2. If empty: Error "Usage: /aod.define <topic>" and exit
3. Check `docs/product/02_PRD/` for existing PRD with same topic
4. If exists:
   - **If `autonomous == true`**: Auto-select `"Create with suffix (v2)"`. Display: `"Auto-selected: Create new PRD (autonomous mode)"`
   - Else: Use AskUserQuestion with options: View existing, Create with suffix (v2), Abort
5. **GitHub Lifecycle Update (early)**: Move the feature's GitHub Issue to `stage:define` at the *start* of PRD creation. Detection order (use first match):
   1. If `$ARGUMENTS` contains a numeric value (`#NNN` or bare `NNN`), look up the GitHub Issue directly: `source .aod/scripts/bash/github-lifecycle.sh && aod_gh_find_issue NNN`
   2. Search GitHub Issues by topic title: `source .aod/scripts/bash/github-lifecycle.sh && aod_gh_find_issue "TOPIC_TITLE"`
   3. Legacy fallback: Extract `[IDEA-NNN]` or `[RETRO-NNN]` tag from `$ARGUMENTS` and search: `source .aod/scripts/bash/github-lifecycle.sh && aod_gh_find_issue "[TAG]"`
   Once the issue number is found, run: `source .aod/scripts/bash/github-lifecycle.sh && aod_gh_update_stage ISSUE_NUMBER define`
   Then regenerate BACKLOG.md: `.aod/scripts/bash/backlog-regenerate.sh`
   **Issue-Required Gate**: If no issue is found after all detection methods:
   1. **If `autonomous == true`**: Auto-select `"Auto-create Issue"`. Display: `"Auto-selected: Auto-create Issue (autonomous mode)"`. Run the create-issue script and proceed.
   2. Use `AskUserQuestion` with three options:
      - **Auto-create Issue** (Recommended): Run `bash .aod/scripts/bash/create-issue.sh --title "TOPIC" --stage define` to create a new Issue with board sync. Use the returned Issue number as the PRD number.
      - **Provide Issue number**: User enters an existing GitHub Issue number manually. Validate it exists via `gh issue view NNN` before proceeding.
      - **Abort**: Cancel PRD creation cleanly with message "PRD creation requires a backing GitHub Issue. Create one at your repo's Issues page and re-run /aod.define."
   2. If `gh` CLI is unavailable and user cannot provide a number, abort with guidance: "The `gh` CLI is not available. Please create a GitHub Issue manually and re-run `/aod.define <topic> #NNN`."
   3. Store the resolved Issue number for use in Steps 5 and 6.

## Step 2: Classify PRD Type

**If `autonomous == true`**: Auto-select `"Feature"` workflow. Display: `"Auto-selected: Feature workflow (autonomous mode)"`. Skip to Step 3.

Use AskUserQuestion to determine workflow type:

| Type | Examples | Workflow |
|------|----------|----------|
| Infrastructure | deployment, database, migration, CI/CD | Sequential (Architect baseline → PM draft → Team-Lead → Architect final) |
| Feature | UI, API, dashboard, user-facing | Parallel (PM draft → Architect + Team-Lead reviews in parallel) |

## Step 3: Draft PRD

**If `revision_mode == true`** (re-invocation after governance rejection):
1. Read the existing PRD at `docs/product/02_PRD/{NNN}-*.md` (do not start from scratch)
2. Read `revision_feedback` from `.aod/revision-context.md`
3. Apply targeted changes to address the specific issues raised by the reviewer
4. Preserve sections the reviewer did not flag — only regenerate flagged sections
5. Skip the workflow classification (Step 2) — reuse the same workflow type as the original
6. Proceed directly to Step 4 (reviews) after updating the PRD

**Infrastructure workflow**:
1. Launch architect agent for baseline technical assessment
2. Invoke ~aod-define skill with architect baseline context
3. Launch team-lead agent for timeline/feasibility review
4. Launch architect agent for final technical review

**Feature workflow**:
1. Invoke ~aod-define skill directly
2. Launch **two Task agents in parallel** (single message, two Task tool calls):

| Agent | subagent_type | Focus | Key Criteria |
|-------|---------------|-------|--------------|
| Architect | architect | Technical | Feasibility, architecture, scalability, security |
| Team-Lead | team-lead | Timeline | Realism, resources, dependencies, complexity |

**Prompt template for each**:
```
Review PRD draft for {FOCUS AREA}.

PRD Topic: {topic}
Draft Content: {prd_draft_content}

Provide sign-off:
STATUS: [APPROVED | APPROVED_WITH_CONCERNS | CHANGES_REQUESTED | BLOCKED]
NOTES: [Your detailed feedback]
```

## Step 4: Handle Review Results

**All APPROVED/APPROVED_WITH_CONCERNS**: → Proceed to Step 5

**Any CHANGES_REQUESTED**:
1. Display feedback from reviewers who requested changes
2. Use product-manager agent to update PRD addressing the feedback
3. Re-run reviews only for reviewers who requested changes
4. Loop until all approved or user aborts (max 5 iterations)

**Any BLOCKED**:
1. Display blocker with veto domain (Architect=technical, Team-Lead=timeline)
2. **If `autonomous == true`**: **HALT** — save state and stop. Display: `"BLOCKED in autonomous mode — halting. Manual intervention required."`. Do NOT auto-override BLOCKED status.
3. Use AskUserQuestion with options:
   - **Resolve**: Address issues and re-submit to blocked reviewer
   - **Override**: Provide justification (min 20 chars), mark as BLOCKED_OVERRIDDEN
   - **Abort**: Cancel PRD creation

## Step 5: Assign PRD Number

1. Use the GitHub Issue number (resolved in Step 1) as the PRD number
2. Zero-pad to 3 digits (e.g., Issue #25 → 025)
3. Format: `{NNN}-{topic}-{YYYY-MM-DD}.md`

## Step 6: Write PRD with Frontmatter

1. Build YAML frontmatter with triad sign-offs:

```yaml
---
prd:
  number: {prd_number}
  topic: {topic}
  created: {YYYY-MM-DD}
  status: {Approved|In Review|Blocked|Draft}
  type: {infrastructure|feature}
triad:
  pm_signoff: {agent: product-manager, date: ..., status: ..., notes: ...}
  architect_signoff: {agent: architect, date: ..., status: ..., notes: ...}
  techlead_signoff: {agent: team-lead, date: ..., status: ..., notes: ...}
source:           # Automatically populated from GitHub Issue
  idea_id: null   # Always equals prd.number (GitHub Issue number)
  story_id: null  # Deprecated — user stories now stored in GitHub Issue body
---
```

2. Write to `docs/product/02_PRD/{filename}`

## Step 6b: Regenerate BACKLOG.md

After the PRD is written, regenerate BACKLOG.md to reflect the stage transition:
Run `.aod/scripts/bash/backlog-regenerate.sh`. If `gh` is unavailable, skip silently.

## Step 7: Update INDEX.md

1. Read `docs/product/02_PRD/INDEX.md`
2. Add new row to Active PRDs table with status symbols: ✓=APPROVED, ⚠=CONCERNS, 🔄=CHANGES, ⛔=BLOCKED, ⚠⚡=OVERRIDDEN
3. Update "Last Updated" date
4. Write updated INDEX.md

## Step 8: Report Completion

**CRITICAL — Re-ground before output**: The `Next:` line MUST be exactly `/aod.plan PRD: {prd_number} - {topic}`. NOT `/aod.spec`, NOT `/aod.project-plan`, NOT any other command. The command after `/aod.define` is ALWAYS `/aod.plan`. Copy the template below verbatim — do not improvise or substitute.

Display summary:
```
✅ PRD CREATION COMPLETE

PRD: {prd_number} - {topic}
Type: {workflow_type}
Status: {overall_status}
File: docs/product/02_PRD/{filename}

Triple Sign-offs:
- PM: {pm_status}
- Architect: {architect_status}
- Team-Lead: {techlead_status}

Next: /aod.plan PRD: {prd_number} - {topic}
```

## Step 10: Quality Checklist

- [ ] Topic validated (no duplicates or user-approved suffix)
- [ ] Workflow type classified (infrastructure or feature)
- [ ] PRD drafted via ~aod-define skill
- [ ] Reviews executed (sequential for infra, parallel for feature)
- [ ] Blockers handled (resolved, overridden, or aborted)
- [ ] PRD number matches GitHub Issue number
- [ ] Frontmatter injected with all three sign-offs
- [ ] INDEX.md updated with new row
- [ ] Completion summary displayed

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I'll run `/aod.define` first and link a GitHub Issue later" | Step 1 (line 130) blocks PRD creation without a backing Issue. Auto-create runs `bash .aod/scripts/bash/create-issue.sh`; the PRD number IS the Issue number per Step 5. |
| "I'll pass `--autonomous` so the Triad reviews skip themselves" | `--autonomous` (Step 0) auto-selects defaults at vision/duplicate/workflow gates only. Triad reviews still run; Step 4 HALTS on BLOCKED in autonomous mode. Not a Triad bypass. |
| "Architect BLOCKED on technical grounds — I'll override since I think it's fine" | Step 4 binds Architect to technical and Team-Lead to timeline (line 198). Override requires justification ≥20 chars and marks BLOCKED_OVERRIDDEN. Address the concern instead. |
| "I'll edit the Step 8 `Next:` line to point at `/aod.spec`" | Step 8 (line 249) binds `Next:` to `/aod.plan PRD: {prd_number}`. The orchestrator routes to the correct sub-step. Substituting strips PRD-aware routing. |

## Red Flags

- Agent invokes `/aod.define` and proceeds past Step 1 with no backing GitHub Issue resolved.
- Agent overrides a BLOCKED Architect or Team-Lead verdict while `autonomous == true` instead of halting per Step 4 line 199.
- Agent's Step 8 completion summary shows `Next: /aod.spec`, `Next: /aod.project-plan`, or any non-`/aod.plan` command.
- Agent runs Architect and Team-Lead reviews for a Feature-type PRD sequentially instead of parallel per Step 3 ("Feature workflow", line 168).
- Agent writes a PRD whose `prd.number` differs from the linked GitHub Issue number (Step 5 binds them).
- Agent skips the Step 0 vision check without confirming `docs/product/01_Product_Vision/product-vision.md` exists.
