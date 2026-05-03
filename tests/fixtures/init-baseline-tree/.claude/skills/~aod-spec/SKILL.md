---
name: ~aod-spec
description: Validates specification completeness and quality by checking for mandatory sections, [NEEDS CLARIFICATION] markers, testable criteria, and clear scope boundaries. Use this skill when you need to check if spec is complete, validate specifications, review spec.md, or check specification quality. Ensures specifications are ready for architecture and implementation phases.
---

# Spec Validator Skill

## Purpose

Automatically validates specification files (spec.md) for completeness, quality, and readiness for architecture and implementation phases. Implements FR-004 from the feature specification.

## How It Works

### Step 1: Locate Specification

- Search for `specs/*/spec.md` files in the repository
- If specific feature directory provided, validate that spec.md
- Report if spec.md not found

### Step 2: Validate Mandatory Sections

Check for required sections per specification template:

- **User Scenarios & Testing** (mandatory)
  - User stories with acceptance scenarios
  - Independent test criteria
  - Edge cases identified

- **Requirements** (mandatory)
  - Functional requirements
  - Key entities

- **Success Criteria** (mandatory)
  - Measurable outcomes

- **Scope** (mandatory)
  - In scope
  - Out of scope

- **Assumptions** (optional but recommended)
- **Dependencies** (optional but recommended)
- **References** (optional)

### Step 3: Check for Clarification Markers

- Grep for `[NEEDS CLARIFICATION]` markers
- Report all instances with line numbers
- Specification not ready if any markers remain

### Step 4: Validate Testable Criteria

- Check that each user story has clear acceptance scenarios
- Verify success criteria are measurable (contain numbers/percentages)
- Ensure requirements have validation criteria

### Step 5: Check Scope Boundaries

- Verify "In Scope" section exists and is populated
- Verify "Out of Scope" section exists (clear boundaries)
- Check that scope is clearly bounded (not open-ended)

### Step 6: Generate Validation Report

Report format:
```
Specification Validation Report

File: specs/{feature-id}/spec.md

Mandatory Sections:
- [✓/✗] User Scenarios & Testing
- [✓/✗] Requirements (Functional Requirements)
- [✓/✗] Success Criteria
- [✓/✗] Scope (In/Out)

Quality Checks:
- [✓/✗] No [NEEDS CLARIFICATION] markers
- [✓/✗] All requirements testable
- [✓/✗] Scope clearly bounded
- [✓/✗] Success criteria measurable

Status: READY / NOT READY

Issues Found:
1. [Issue description with line number]
2. [Issue description with line number]

Recommendations:
- [Specific action to resolve each issue]
```

## Examples

### Example 1: Complete Specification

**User Query**: "Is my spec complete?"

**Skill Actions**:
1. Read `specs/005-create-a-specification/spec.md`
2. Check all mandatory sections present
3. Grep for [NEEDS CLARIFICATION] - none found
4. Validate testable criteria - all pass
5. Check scope boundaries - clearly defined

**Result**:
```
Specification Validation: READY

File: specs/005-create-a-specification/spec.md

All mandatory sections present ✓
No clarification markers found ✓
All requirements testable ✓
Scope clearly bounded ✓

Your specification is ready for /aod.project-plan!
```

### Example 2: Incomplete Specification

**User Query**: "Check spec.md"

**Skill Actions**:
1. Read `specs/004-feature/spec.md`
2. Missing "Success Criteria" section
3. Found 3 [NEEDS CLARIFICATION] markers
4. Some requirements not testable

**Result**:
```
Specification Validation: NOT READY

Issues Found:
1. Missing mandatory section: Success Criteria
2. Found 3 [NEEDS CLARIFICATION] markers:
   - Line 42: "[NEEDS CLARIFICATION] How should errors be handled?"
   - Line 78: "[NEEDS CLARIFICATION] What is the performance target?"
   - Line 103: "[NEEDS CLARIFICATION] Which authentication method?"
3. Requirements lack testable criteria:
   - FR-003: No validation method specified
   - FR-007: Vague acceptance criteria

Recommendations:
1. Add Success Criteria section with measurable outcomes
2. Resolve all [NEEDS CLARIFICATION] markers using /aod.clarify
3. Add specific validation criteria to FR-003 and FR-007

Run /aod.clarify to resolve clarification markers.
```

## Integration

### Uses

- **Read**: Load spec.md file contents
- **Grep**: Search for [NEEDS CLARIFICATION] markers and section headers
- **Glob**: Find spec.md files if location not specified
- **TodoWrite**: Track validation issues if fixing specification

### Updates

- None (read-only validation)

### Invokes

- Can suggest using /aod.clarify command if clarifications needed

## Validation Logic

```bash
# Find specification
find specs/ -name "spec.md"

# Check for mandatory sections
grep "## User Scenarios & Testing" spec.md
grep "## Requirements" spec.md
grep "## Success Criteria" spec.md
grep "## Scope" spec.md

# Check for clarification markers
grep -n "\[NEEDS CLARIFICATION\]" spec.md

# Check for testable criteria
grep -A 5 "Acceptance Scenarios:" spec.md
grep -E "[0-9]+%" spec.md  # Measurable success criteria
```

## Constitutional Compliance

- **Specification-Driven**: Enforces spec completion before proceeding (Principle II)
- **Quality Focus**: Ensures high-quality specifications for better outcomes
- **Read-Only**: No modifications to specs, only validation

---

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "A few [NEEDS CLARIFICATION] markers won't fail the report" | Step 3 (line 46) flags every marker; the report status drops to NOT READY until each one is resolved. |
| "Out of Scope is obvious — I can skip the section" | Step 5 (line 56) requires the explicit Out of Scope section; missing it returns NOT READY with bounded-scope failure. |
| "This requirement is testable enough — adding numbers is pedantic" | Step 4 (line 53) checks for measurable values; vague criteria fail the testable-criteria gate. |
| "Success Criteria can be added at plan time" | Step 2 (line 33) lists Success Criteria as mandatory; absence returns NOT READY before plan even starts. |
| "Edge cases live in tasks.md, not spec.md" | Step 2 (line 27) requires Edge Cases under User Scenarios — the validator expects them at spec time. |

## Red Flags

- Agent reports READY while `grep -n "\[NEEDS CLARIFICATION\]"` (Step 3) still returns matches.
- Agent skips Step 5 scope-boundary check by treating "everything reasonable is in scope" as sufficient.
- Agent's report omits the Quality Checks block defined in Step 6's report format.
- Agent invokes Step 4 without verifying acceptance scenarios per user story (Step 2 line 26).
- Agent suggests proceeding to `/aod.project-plan` despite NOT READY status from Step 6.
- Agent treats optional sections (Assumptions, Dependencies — line 40) as mandatory and blocks on their absence.
