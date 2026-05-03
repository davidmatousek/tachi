---
name: ~aod-project-plan
description: Validates architecture documentation completeness by checking for technology stack, API specifications, database schema, security architecture, and alignment with feature specification. Use this skill when you need to check if plan.md is complete before implementation, validate architecture documentation, or review technical plans for completeness.
---

# Architecture Validator Skill

## Purpose

Automatically validates architecture documentation (plan.md) for completeness, technical rigor, and alignment with feature specifications. Implements FR-006 from the feature specification.

## How It Works

### Step 1: Locate Architecture Plan

- Search for `specs/*/plan.md` files
- If specific feature directory provided, validate that plan.md
- Report if plan.md not found

### Step 2: Validate Required Sections

Check for mandatory sections per AOD plan template:

#### Technical Context (Required)
- Language/Version
- Primary Dependencies
- Storage solution
- Testing approach
- Target Platform
- Project Type
- Performance Goals
- Constraints
- Scale/Scope

#### Constitution Check (Required)
- All 7 constitutional principles validated
- Evidence for each principle
- Violations justified (if any)

#### Project Structure (Required)
- Documentation structure
- Source code structure
- File organization

#### Technology Stack (Required)
- Languages and versions
- Frameworks and libraries
- Database and storage
- Infrastructure components

### Step 3: Check Technical Decisions

Verify technical decisions are documented:
- **data-model.md**: Entity definitions and relationships
- **contracts/**: API specifications (if applicable)
- **research.md**: Technical unknowns resolved

### Step 4: Validate Spec Alignment

- Compare plan.md with spec.md
- Check all functional requirements addressed
- Verify success criteria have implementation strategy
- Ensure out-of-scope items respected

### Step 5: Security Architecture Check

Verify security considerations documented:
- Authentication approach
- Authorization model
- Data protection strategy
- API security measures
- Secrets management

### Step 6: Generate Validation Report

```
✅ Architecture Validation Report

File: specs/{feature-id}/plan.md

Required Sections:
- [✓/✗] Technical Context
- [✓/✗] Constitution Check (7/7 principles)
- [✓/✗] Project Structure
- [✓/✗] Technology Stack

Design Artifacts:
- [✓/✗] data-model.md (entities defined)
- [✓/✗] contracts/ (API specs)
- [✓/✗] research.md (decisions documented)

Quality Checks:
- [✓/✗] All FRs from spec.md addressed
- [✓/✗] Security architecture documented
- [✓/✗] Performance targets specified
- [✓/✗] Complexity justified

Status: READY / NOT READY

Issues Found:
1. [Issue description]
2. [Issue description]

Recommendations:
- [Specific action to resolve each issue]
```

## Examples

### Example 1: Complete Architecture Plan

**User Query**: "Is my plan complete?"

**Skill Actions**:
1. Read `specs/005-create-a-specification/plan.md`
2. Validate all required sections present
3. Check constitution compliance (7/7 pass)
4. Verify design artifacts exist (data-model.md, contracts/)
5. Validate spec alignment

**Result**:
```
✅ Architecture Validation: READY

File: specs/005-create-a-specification/plan.md

All required sections complete ✓
Constitution check: 7/7 passed ✓
Design artifacts present ✓
Spec alignment validated ✓

Your architecture is ready for /aod.tasks!

Highlights:
- Comprehensive data model (5 entities)
- 10 technical decisions documented
- Security architecture complete
- Performance targets specified (<500ms)
```

### Example 2: Incomplete Architecture

**User Query**: "Validate architecture"

**Skill Actions**:
1. Read `specs/004-feature/plan.md`
2. Missing security architecture section
3. Constitution check incomplete (missing principle VI)
4. No performance targets specified

**Result**:
```
✗ Architecture Validation: NOT READY

Issues Found:
1. Missing Security Architecture section
   - No authentication approach documented
   - No authorization model specified
   - No secrets management strategy

2. Constitution Check incomplete
   - Principle VI (Observability): No evidence provided
   - Need to document root cause analysis approach

3. Performance targets not specified
   - No latency requirements
   - No throughput targets
   - No scalability goals

4. data-model.md missing relationship diagrams
   - Entities defined but relationships unclear

Recommendations:
1. Add Security Architecture section:
   - Document authentication method (JWT, OAuth, etc.)
   - Define authorization model (RBAC, ABAC, etc.)
   - Specify secrets management (env vars, vault, etc.)

2. Complete Constitution Check:
   - Add evidence for Principle VI
   - Document observability and root cause analysis approach

3. Add Performance Goals section:
   - Specify latency targets (e.g., <500ms)
   - Define throughput requirements
   - Document scalability approach

4. Enhance data-model.md with relationship diagrams
```

## Integration

### Uses

- **Read**: Load plan.md and related design artifacts
- **Grep**: Search for required section headers and keywords
- **Glob**: Find plan.md and design artifact files
- **TodoWrite**: Track architecture issues if revising plan

### Updates

- None (read-only validation)

### Cross-References

- **spec.md**: Validate alignment with requirements
- **data-model.md**: Check entity definitions
- **contracts/**: Verify API specifications
- **research.md**: Confirm technical decisions
- **.aod/memory/constitution.md**: Validate constitutional compliance

## Validation Logic

```bash
# Check required sections
grep "## Technical Context" plan.md
grep "## Constitution Check" plan.md
grep "## Project Structure" plan.md

# Validate constitution compliance
grep -A 5 "### I\." plan.md  # Defensive Security
grep -A 5 "### II\." plan.md  # Spec-Driven
grep -A 5 "### III\." plan.md  # 3-Step DoD
# ... (continue for all 7 principles)

# Check design artifacts
test -f data-model.md && echo "✓ data-model.md exists"
test -d contracts && echo "✓ contracts/ directory exists"
test -f research.md && echo "✓ research.md exists"

# Validate spec alignment
diff -u <(grep "^- \*\*FR-" spec.md | cut -d: -f1) \
        <(grep "FR-" plan.md | cut -d: -f1)
```

## Constitutional Compliance

- **Specification-Driven**: Enforces plan completion before implementation (Principle II)
- **Constitution Validation**: Ensures all 7 principles addressed
- **Quality Focus**: Prevents incomplete designs from proceeding
- **Read-Only**: No modifications, only validation

---

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "Architect can sign off later — PM approval is what matters" | plan.md requires both PM AND Architect sign-off (CLAUDE.md governance); Architect-pending blocks `/aod.tasks`. |
| "Constitution Check is boilerplate, I'll just write 'pass' for all 7" | Step 2 (line 38) requires evidence per principle; Example 2 NOT READY shows missing evidence on Principle VI fails. |
| "Security architecture lives in code review, not the plan" | Step 5 (line 65) requires auth, authz, secrets, and API security documented; absence returns NOT READY. |
| "data-model.md is overkill for this feature" | Step 3 (line 53) treats data-model.md as a design artifact; missing entities show in the report's Design Artifacts row. |
| "Spec alignment is implicit if the plan addresses the feature" | Step 4 (line 58) cross-checks every spec FR against plan; unaddressed FRs flag a quality-check failure. |

## Red Flags

- Agent reports READY without confirming all 7 constitutional principles per Step 2 Constitution Check.
- Agent skips Step 5 Security Architecture review because "no user-facing auth in this feature."
- Agent's report omits the Design Artifacts block (data-model.md, contracts/, research.md) defined in Step 6.
- Agent declares dual sign-off complete with only one signoff present in the plan.md frontmatter.
- Agent invokes `/aod.tasks` while plan.md status is NOT READY from Step 6's report.
- Agent fills Constitution Check rows with empty evidence and reports 7/7 pass per Step 2 (line 36).
