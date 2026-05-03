# NAMING_GUIDELINES.md - Phase-Based File Naming Convention

## Overview

This document defines the phase-based file naming convention for all project planning documents. The new structure groups all documents by phase number to ensure clear organization and prevent confusion between planning levels.

## Core Principle: Phase-Based Organization

All documents are organized by their phase number first, creating clear phase groupings:
- Phase-specific documents are prefixed with `PHASEXX_`
- Overall project documents use `MASTER_PROJECT_PLAN_` prefix
- Status suffixes indicate document lifecycle

## File Naming Formats

### Overall Project Plan (No Phase Number)
```
MASTER_PROJECT_PLAN_OVERALL_ACTIVE.md
```
- Contains all phases 1-5, cross-phase dependencies, overall vision
- Maintained throughout entire project lifecycle
- Never archived

### Phase Master Plans
```
PHASEXX_MASTER_PLAN_STATUS.md
```
Where:
- **PHASEXX** = Phase number (PHASE01, PHASE02, PHASE03, etc.)
- **STATUS** = Current status (ARCHIVED, ACTIVE, PLANNED)

Examples:
- `PHASE01_MASTER_PLAN_ARCHIVED.md` - Completed phase
- `PHASE03_MASTER_PLAN_ACTIVE.md` - Current active phase
- `PHASE04_MASTER_PLAN_PLANNED.md` - Future phase

### Phase Feature Documents
```
PHASEXX_feature-name_STATUS.md
PHASEXX_GROUP[A-H]_feature-name_STATUS.md
```
Where:
- **PHASEXX** = Phase number
- **GROUP[A-H]** = Optional work group classification for better sorting
- **feature-name** = Descriptive kebab-case name
- **STATUS** = Current status

#### Work Group Classifications (Optional)
- **GROUP A**: OWASP LLM Integration (complete)
- **GROUP B**: SaaS Platform MVP 
- **GROUP C**: Go-to-Market Launch
- **GROUP D**: Production Readiness
- **GROUP E**: Website Quality Assurance
- **GROUP F**: Customer Support Infrastructure
- **GROUP G**: MCP Server Distribution
- **GROUP H**: User Validation Testing

Examples:
- `PHASE03_MVP03-billing-frontend_ACTIVE.md`
- `PHASE03_GROUPC_pricing-research_ACTIVE.md`
- `PHASE03_GROUPD_production-deployment-strategy_ACTIVE.md`
- `PHASE03_GROUPH_test-strategy_ACTIVE.md`

## Status Definitions

### For Phase Master Plans
- **ARCHIVED**: Phase completed, historical record
- **ACTIVE**: Current phase in execution
- **PLANNED**: Future phase, not yet started

### For Feature Documents
- **ACTIVE**: Currently being worked on
- **COMPLETE**: Work finished, awaiting archival
- **ARCHIVED**: Historical record
- **PLANNED**: Future work within the phase
- **BLOCKED**: Work stopped due to dependencies

## Directory Structure

```
docs/development/
├── MASTER_PROJECT_PLAN_OVERALL_ACTIVE.md    # Overall vision
├── PHASE01_MASTER_PLAN_ARCHIVED.md          # Phase 1 (archived)
├── PHASE01_*_ARCHIVED.md                    # Phase 1 features
├── PHASE02_MASTER_PLAN_ARCHIVED.md          # Phase 2 (archived)
├── PHASE02_*_ARCHIVED.md                    # Phase 2 features
├── PHASE03_MASTER_PLAN_ACTIVE.md            # Phase 3 (current)
├── PHASE03_*_ACTIVE.md                      # Phase 3 features
├── PHASE03_GROUP*_*_ACTIVE.md               # Phase 3 grouped features
├── PHASE04_MASTER_PLAN_PLANNED.md           # Phase 4 (planned)
├── PHASE04_*_PLANNED.md                     # Phase 4 features
├── PHASE05_MASTER_PLAN_PLANNED.md           # Phase 5 (planned)
└── PHASE05_*_PLANNED.md                     # Phase 5 features
```

## Feature Name Guidelines

### Standard Feature Types
- **mvpXX-name**: SaaS platform features (mvp01-infrastructure, mvp03-billing)
- **llm-name**: LLM agent features (llm-implementation-plan)
- **test-name**: Testing features (test-strategy)
- **pricing-name**: Business features (pricing-research)
- **vc-name**: Investment materials (vc-pitch)
- **nist-name**: Compliance features (nist-compliance)
- **enterprise-name**: Enterprise features (enterprise-expansion)

### Naming Best Practices
- Use lowercase with hyphens (kebab-case)
- Keep names descriptive but concise
- Group related features with common prefixes
- Avoid version numbers in names (use git for versioning)

## Cross-Reference Format

When referencing other documents:
```markdown
**Overall Vision**: See [MASTER_PROJECT_PLAN_OVERALL_ACTIVE.md]
**Phase Plan**: See [PHASE03_MASTER_PLAN_ACTIVE.md]
**Feature Details**: See [PHASE03_MVP03-billing-frontend_ACTIVE.md]
```

## Migration from Old Format

### Old Level-Based Format (DEPRECATED)
```
L01_P03_F00-name_STATUS.md  →  MASTER_PROJECT_PLAN_OVERALL_ACTIVE.md
L02_P03_F00-name_STATUS.md  →  PHASE03_MASTER_PLAN_STATUS.md
L03_P03_name_STATUS.md      →  PHASE03_name_STATUS.md
```

### Migration Complete
All files have been migrated to the new phase-based format as of 2025-01-09.

## Archival Rules

### Phase Completion
When a phase is completed:
1. Change phase master plan status to ARCHIVED
2. Change all phase feature documents to ARCHIVED
3. Keep in main directory for reference (not moved to subdirectory)

### Document Lifecycle
1. **Planning**: Create as PLANNED
2. **Execution**: Change to ACTIVE when work begins
3. **Completion**: Change to COMPLETE when done
4. **Archival**: Change to ARCHIVED after phase completion

## Implementation Guidelines

### For doc agent
- **Use phase-based naming** for all new documents
- **Group by phase number** when organizing files
- **Update cross-references** to use new format
- **Maintain phase integrity** - don't mix phase content

### For head-honcho agent
- **Orchestrate by phase** not by level
- **Maintain clear phase boundaries** in planning
- **Archive entire phases** together
- **Keep phase documents grouped** in listings

### For All Agents
- **Reference phase documents** directly
- **Avoid level terminology** (L01, L02, L03)
- **Think in phases** not hierarchical levels
- **Maintain phase consistency** across documents

## Examples by Use Case

### Starting New Phase
1. Create `PHASE04_MASTER_PLAN_PLANNED.md`
2. Update `MASTER_PROJECT_PLAN_OVERALL_ACTIVE.md`
3. Archive Phase 3 documents (change all to ARCHIVED)

### Adding New Feature to Current Phase
1. Create `PHASE03_new-feature_ACTIVE.md`
2. Update `PHASE03_MASTER_PLAN_ACTIVE.md` with reference
3. Track in phase-specific feature list

### Completing Current Phase
1. Change `PHASE03_MASTER_PLAN_ACTIVE.md` to ARCHIVED
2. Change all `PHASE03_*_ACTIVE.md` to ARCHIVED
3. Activate `PHASE04_MASTER_PLAN_PLANNED.md` to ACTIVE

## Valid Examples

✅ `MASTER_PROJECT_PLAN_OVERALL_ACTIVE.md`
✅ `PHASE03_MASTER_PLAN_ACTIVE.md`
✅ `PHASE03_MVP03-billing-frontend_ACTIVE.md`
✅ `PHASE03_GROUPC_pricing-research_ACTIVE.md`
✅ `PHASE03_GROUPD_production-deployment-strategy_ACTIVE.md`
✅ `PHASE03_GROUPH_test-strategy_ACTIVE.md`
✅ `PHASE04_enterprise-expansion_PLANNED.md`

## Invalid Examples

❌ `L01_P03_F00-master_ACTIVE.md` (old level format)
❌ `phase3_plan.md` (missing proper prefix)
❌ `PHASE3_PLAN.md` (missing underscore, wrong format)
❌ `MVP03_billing_ACTIVE.md` (missing phase prefix)

## Version History

- **v2.0** (2025-01-09): Complete redesign to phase-based organization
- **v1.0** (2025-08-31): Initial level-based system (deprecated)

---
*Maintained by: Head Honcho Project Manager*
*Last Updated: 2025-01-09*
*System: Phase-based organization with zero hierarchy confusion*