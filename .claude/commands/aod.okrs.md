---
description: Scaffold an OKR document with standard template and PM sign-off
---

## User Input

```text
$ARGUMENTS
```

Consider user input before proceeding (if not empty).

## Overview

Scaffolds a quarterly OKR (Objectives and Key Results) document in `docs/product/06_OKRs/` with a PM sign-off gate.

**Flow**: Determine quarter → Scaffold OKR template → PM sign-off → Write file

## Step 1: Determine Quarter

1. Parse current date to determine the quarter:
   - Jan-Mar → Q1
   - Apr-Jun → Q2
   - Jul-Sep → Q3
   - Oct-Dec → Q4
2. Format as `YYYY-QN` (e.g., `2026-Q1`)
3. If `$ARGUMENTS` contains a quarter override (e.g., `2026-Q2`), use that instead
4. Check if `docs/product/06_OKRs/{quarter}.md` already exists
   - If exists: Use AskUserQuestion with options: View existing, Create with suffix (v2), Abort

## Step 2: Gather Context (Optional)

1. If `docs/product/03_Product_Roadmap/` contains a roadmap for the same quarter, read it for alignment context
2. If `docs/product/01_Product_Vision/product-vision.md` exists, read mission statement for objective alignment
3. Store as `context` for template population hints

## Step 3: Scaffold OKR Document

Build the OKR document with standard template:

```markdown
---
okrs:
  quarter: {YYYY-QN}
  created: {YYYY-MM-DD}
  status: Draft
  review_date: null
triad:
  pm_signoff: null  # Populated after review
---

# tachi OKRs — {YYYY-QN}

**Quarter**: {QN} {YYYY}
**Status**: Draft
**Created**: {YYYY-MM-DD}
**Review Date**: [Schedule end-of-quarter review]

## Objective 1: [Qualitative Goal]

**Why This Matters**: [Alignment with product vision]

### Key Result 1.1: [Measurable Outcome]
- **Baseline**: [Starting value]
- **Target**: [End of quarter goal]
- **Current**: —
- **Status**: Not Started
- **Owner**: [Team member]

### Key Result 1.2: [Measurable Outcome]
- **Baseline**: [Starting value]
- **Target**: [End of quarter goal]
- **Current**: —
- **Status**: Not Started
- **Owner**: [Team member]

## Objective 2: [Qualitative Goal]

**Why This Matters**: [Alignment with product vision]

### Key Result 2.1: [Measurable Outcome]
- **Baseline**: [Starting value]
- **Target**: [End of quarter goal]
- **Current**: —
- **Status**: Not Started
- **Owner**: [Team member]

### Key Result 2.2: [Measurable Outcome]
- **Baseline**: [Starting value]
- **Target**: [End of quarter goal]
- **Current**: —
- **Status**: Not Started
- **Owner**: [Team member]

---

## Progress Tracking

**Week of [Date]**:
- KR 1.1: [Update]
- KR 1.2: [Update]
- KR 2.1: [Update]
- KR 2.2: [Update]

**Risks**:
- [Identified risks to OKR achievement]

**Actions**:
- [ ] [Action items to address risks]

---

## Scoring Guide

At end of quarter, score each Key Result:
- **1.0**: Fully achieved
- **0.7**: Strong progress, nearly there
- **0.4**: Some progress, but short of target
- **0.0**: No meaningful progress

**Target average**: 0.6–0.7 (stretch goals should be ambitious)
```

## Step 4: PM Sign-off

1. Launch product-manager agent for review:

```
Review quarterly OKR document for {YYYY-QN}.

OKR Content: {okr_content}

Verify:
- Template structure follows OKR best practices
- Objectives are qualitative and inspiring
- Key Results are measurable and time-bound
- Alignment with product vision (if available)

Provide sign-off:
STATUS: [APPROVED | APPROVED_WITH_CONCERNS | CHANGES_REQUESTED | BLOCKED]
NOTES: [Your detailed feedback]
```

2. **If APPROVED/APPROVED_WITH_CONCERNS**: Proceed to Step 5
3. **If CHANGES_REQUESTED**: Address feedback, re-submit (max 3 iterations)
4. **If BLOCKED**: Display blocker, offer Resolve/Override/Abort options

## Step 5: Write OKR File

1. Update frontmatter with PM sign-off:
   ```yaml
   triad:
     pm_signoff:
       agent: product-manager
       date: {YYYY-MM-DD}
       status: {PM_STATUS}
       notes: "{PM_NOTES}"
   ```
2. Write to `docs/product/06_OKRs/{YYYY-QN}.md`

## Step 6: Report Completion

Display summary:
```
OKR DOCUMENT CREATED

Quarter: {YYYY-QN}
File: docs/product/06_OKRs/{YYYY-QN}.md

PM Sign-off: {pm_status}

Next: Fill in objectives and key results with your team,
then schedule a quarterly review.
```

## Quality Checklist

- [ ] Quarter correctly determined from date or user override
- [ ] Duplicate file check performed
- [ ] Roadmap alignment context loaded (if available)
- [ ] OKR template follows standard structure (Objectives → Key Results)
- [ ] PM sign-off obtained via product-manager agent
- [ ] Frontmatter includes PM sign-off record
- [ ] File written to correct directory
- [ ] Completion summary displayed
