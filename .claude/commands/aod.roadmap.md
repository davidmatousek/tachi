---
description: Scaffold a quarterly roadmap document from completed PRDs with PM sign-off
---

## User Input

```text
$ARGUMENTS
```

Consider user input before proceeding (if not empty).

## Overview

Scans completed PRDs in `docs/product/02_PRD/`, aggregates feature data, and scaffolds a quarterly roadmap document in `docs/product/03_Product_Roadmap/` with PM sign-off.

**Flow**: Scan PRDs → Aggregate data → Scaffold roadmap → PM sign-off → Write file

## Step 1: Scan PRDs

1. Read `docs/product/02_PRD/INDEX.md`
2. Parse the PRD Registry table for entries with status containing "Delivered" or "Approved"
3. For each matching PRD, extract:
   - **ID**: PRD number (NNN)
   - **Title**: Feature name
   - **Status**: Current status (Delivered, Approved, etc.)
   - **Created**: Creation date
4. If zero completed PRDs found: Display "No completed PRDs found" and exit
5. Store as `prd_entries` list

## Step 2: Determine Quarter

1. Parse current date to determine the quarter:
   - Jan-Mar → Q1
   - Apr-Jun → Q2
   - Jul-Sep → Q3
   - Oct-Dec → Q4
2. Format as `YYYY-QN` (e.g., `2026-Q1`)
3. If `$ARGUMENTS` contains a quarter override (e.g., `2026-Q2`), use that instead
4. Check if `docs/product/03_Product_Roadmap/{quarter}.md` already exists
   - If exists: Use AskUserQuestion with options: View existing, Create with suffix (v2), Abort

## Step 3: Scaffold Roadmap Document

Build the roadmap document with aggregated PRD data:

```markdown
---
roadmap:
  quarter: {YYYY-QN}
  created: {YYYY-MM-DD}
  status: Draft
  feature_count: {count}
triad:
  pm_signoff: null  # Populated after review
---

# tachi Roadmap — {YYYY-QN}

**Quarter**: {QN} {YYYY}
**Status**: Draft
**Created**: {YYYY-MM-DD}
**Features**: {count} from completed PRDs

## Quarter Objectives

1. [Objective 1 — derived from highest-priority delivered features]
2. [Objective 2 — derived from approved features pending implementation]

## Delivered Features

| ID | Feature | Status | Delivered |
|----|---------|--------|-----------|
{for each Delivered PRD: | NNN | Title | Delivered | Date |}

## Approved Features (Pending Implementation)

| ID | Feature | Status | Approved |
|----|---------|--------|----------|
{for each Approved PRD: | NNN | Title | Approved | Date |}

## Stretch Goals

[Features explicitly deferred to next quarter]

## Not This Quarter

[Features explicitly excluded with rationale]

## Dependencies

[Cross-feature dependencies identified from PRD data]

## Risks

[Risks identified from PRD review]
```

## Step 4: PM Sign-off

1. Launch product-manager agent for review:

```
Review quarterly roadmap document for {YYYY-QN}.

Roadmap Content: {roadmap_content}

Verify:
- Feature aggregation is accurate (all completed PRDs included)
- Quarter objectives are realistic and aligned with product vision
- Prioritization makes sense given current product state

Provide sign-off:
STATUS: [APPROVED | APPROVED_WITH_CONCERNS | CHANGES_REQUESTED | BLOCKED]
NOTES: [Your detailed feedback]
```

2. **If APPROVED/APPROVED_WITH_CONCERNS**: Proceed to Step 5
3. **If CHANGES_REQUESTED**: Address feedback, re-submit (max 3 iterations)
4. **If BLOCKED**: Display blocker, offer Resolve/Override/Abort options

## Step 5: Write Roadmap File

1. Update frontmatter with PM sign-off:
   ```yaml
   triad:
     pm_signoff:
       agent: product-manager
       date: {YYYY-MM-DD}
       status: {PM_STATUS}
       notes: "{PM_NOTES}"
   ```
2. Write to `docs/product/03_Product_Roadmap/{YYYY-QN}.md`

## Step 6: Report Completion

Display summary:
```
ROADMAP CREATED

Quarter: {YYYY-QN}
Features: {count} aggregated from PRDs
File: docs/product/03_Product_Roadmap/{YYYY-QN}.md

PM Sign-off: {pm_status}

Next: Review and refine objectives, then share with team.
```

## Quality Checklist

- [ ] PRD INDEX.md scanned for completed PRDs
- [ ] Zero-PRD edge case handled (exit with message)
- [ ] Quarter correctly determined from date or user override
- [ ] Duplicate file check performed
- [ ] PRD data accurately aggregated (IDs, titles, statuses, dates)
- [ ] PM sign-off obtained via product-manager agent
- [ ] Frontmatter includes PM sign-off record
- [ ] File written to correct directory
- [ ] Completion summary displayed
