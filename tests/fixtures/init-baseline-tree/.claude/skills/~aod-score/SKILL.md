---
name: ~aod-score
description: "Re-score an existing idea's ICE rating when circumstances change. Use this skill when you need to re-evaluate ideas, update ICE scores, change idea priority, or re-assess deferred ideas."
---

# AOD Re-Score Skill

## Purpose

Update an existing idea's ICE (Impact, Confidence, Effort) score when circumstances change, new information emerges, or priorities shift. Reads from and writes to the idea's GitHub Issue.

## Source of Truth

**GitHub Issues are the sole source of truth for backlog items.** All idea state (ICE scores, status, evidence) is stored in the GitHub Issue body. BACKLOG.md is an auto-generated view regenerated from Issues.

## Inputs

- **NNN**, **#NNN**, or **IDEA-NNN** (legacy): The identifier of the idea to re-score (from user arguments)

## Workflow

### Step 1: Parse Input

Extract the idea identifier from user arguments. Accept three formats:
- **`NNN`** (bare number, e.g., `21`): Direct GitHub Issue lookup
- **`#NNN`** (hash-prefixed, e.g., `#21`): Strip `#` prefix, direct lookup
- **`IDEA-NNN`** (legacy, e.g., `IDEA-009`): Search issue titles for `[IDEA-NNN]` bracket tag

If invalid or missing, display usage: `Usage: /aod.score NNN` (or `#NNN` or `IDEA-NNN`)

### Step 2: Find GitHub Issue

Search for the matching GitHub Issue:

For numeric input (`NNN` or `#NNN`):
```bash
source .aod/scripts/bash/github-lifecycle.sh && aod_gh_find_issue NNN
```

For legacy `IDEA-NNN` input:
```bash
source .aod/scripts/bash/github-lifecycle.sh && aod_gh_find_issue "[IDEA-NNN]"
```

If no issue is found, display an error and exit:
```
Error: No GitHub Issue found for {identifier}
```

### Step 3: Read Current Scores

Read the GitHub Issue body using `gh issue view {number} --json body,title`. Parse the structured body to extract:
- Description (from `## Idea` section or title)
- ICE scores (from `## ICE Score` section)
- Source (from `## Metadata` section)
- Status (from `## Metadata` section)
- Evidence (from `## Evidence` section)

### Step 4: Display Current Scores

Show the existing idea details:

```
CURRENT SCORES — #{issue_number}

GitHub Issue: #{issue_number}
Idea: {description}
Source: {source}
Date: {date}
Status: {status}

ICE Score: {total} (I:{impact} C:{confidence} E:{effort})
Priority Tier: {tier}
```

### Step 5: New ICE Scoring

Present the ICE scoring quick-assessment table using AskUserQuestion. Ask each dimension separately:

#### Impact — "How much value does this deliver to users?"

```
Options:
  - High (9): "Transformative — significant user value"
  - Medium (6): "Solid improvement — meaningful but incremental"
  - Low (3): "Minor enhancement — small quality-of-life fix"
```

Allow the user to select "Other" to provide a custom numeric value (1-10).

#### Confidence — "How sure are we this will succeed?"

```
Options:
  - High (9): "Proven pattern — strong evidence it will work"
  - Medium (6): "Some unknowns — reasonable confidence with gaps"
  - Low (3): "Speculative — significant uncertainty"
```

Allow the user to select "Other" to provide a custom numeric value (1-10).

#### Effort (Ease of Implementation) — "How easy is this to build?"

```
Options:
  - High (9): "Days of work — straightforward implementation"
  - Medium (6): "Weeks of work — moderate complexity"
  - Low (3): "Months of work — significant engineering effort"
```

Allow the user to select "Other" to provide a custom numeric value (1-10).

### Step 6: Compute New ICE Total

```
New ICE Total = Impact + Confidence + Effort
Range: 3-30
```

### Step 7: Update Status

Apply status transitions based on threshold crossings:

- If current status is **"Deferred"** and new score >= 12: Set status to **"Scoring"**
- If current status is **"Scoring"** and new score < 12: Set status to **"Deferred"**
- If current status is **"Validated"**: **Preserve** status (already PM-approved, do not downgrade)
- If current status is **"Rejected"** and new score >= 12: Set status to **"Scoring"** (re-opens for re-validation via `/aod.validate`)
- If current status is **"Rejected"** and new score < 12: Set status to **"Deferred"**

**Note**: Re-scoring a Rejected idea resets it for a fresh PM review. The PM previously rejected the idea, but re-scoring indicates changed circumstances that warrant re-evaluation. The user must still run `/aod.validate` to get PM approval.

### Step 8: Update GitHub Issue

Update the GitHub Issue body with the new ICE scores and status:

1. Use `gh issue edit {number} --body "..."` to update the issue body with new ICE scores and status
2. Add a comment documenting the re-score: `"Re-scored: {old_total} → {new_total} (I:{new_i} C:{new_c} E:{new_e}). Status: {old_status} → {new_status}"`

### Step 9: Regenerate BACKLOG.md

Run `.aod/scripts/bash/backlog-regenerate.sh` to update the backlog snapshot.

### Step 10: Report Result

Display the comparison:

```
IDEA RE-SCORED

ID: #{issue_number}
GitHub Issue: #{issue_number}
Idea: {description}

Previous: {old_total} (I:{old_i} C:{old_c} E:{old_e}) — {old_tier}
Updated:  {new_total} (I:{new_i} C:{new_c} E:{new_e}) — {new_tier}

{If tier changed: "Priority tier changed: {old_tier} → {new_tier}"}
{If status changed: "Status changed: {old_status} → {new_status}"}
{If status preserved: "Status preserved: {status}"}

Date updated: {YYYY-MM-DD}
```

## ICE Scoring Reference

### Quick-Assessment Anchors

| Dimension | High (9) | Medium (6) | Low (3) |
|-----------|----------|------------|---------|
| **Impact** | Transformative | Solid improvement | Minor enhancement |
| **Confidence** | Proven pattern | Some unknowns | Speculative |
| **Effort (Ease)** | Days of work | Weeks of work | Months of work |

### Priority Tiers

| Score Range | Priority | Action |
|-------------|----------|--------|
| 25-30 | P0 (Critical) | Fast-track to development |
| 18-24 | P1 (High) | Queue for next sprint |
| 12-17 | P2 (Medium) | Consider when capacity allows |
| < 12 | Deferred | Auto-defer; requires PM override via `/aod.validate` |

### Auto-Defer Gate

Ideas scoring below 12 are automatically deferred. The PM can override this gate using `/aod.validate #NNN`.

## Edge Cases

- **Idea not found**: Search GitHub Issues by number (NNN, #NNN) or title tag (IDEA-NNN), display error with the identifier that was searched for
- **Invalid ID format**: Display usage guidance showing accepted formats (NNN, #NNN, or IDEA-NNN)
- **Validated status**: Preserve — PM has already approved, re-scoring only updates the numeric score
- **Rejected status**: Re-opens to Scoring (>= 12) or Deferred (< 12) — allows re-submission to PM via `/aod.validate`
- **Custom ICE score outside 1-10**: Clamp to valid range (1 minimum, 10 maximum)
- **Score doesn't change**: Still update the date to record that a re-evaluation occurred
- **`gh` unavailable**: Display error — re-scoring requires GitHub access since Issues are the source of truth

## Quality Checklist

- [ ] Idea identifier parsed and validated (NNN, #NNN, or IDEA-NNN)
- [ ] GitHub Issue found for the idea
- [ ] Current scores displayed before re-scoring
- [ ] New ICE score computed correctly (additive I+C+E)
- [ ] Status updated based on threshold crossings (Validated preserved; Rejected re-opens)
- [ ] GitHub Issue body updated with new scores
- [ ] Re-score documented as Issue comment
- [ ] BACKLOG.md regenerated
- [ ] Old vs new comparison displayed
