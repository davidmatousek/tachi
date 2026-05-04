# Documentation Update Checklist - After New Feature

**Purpose**: Ensure all documentation stays current after implementing new features
**When to Use**: After merging any feature branch to main
**Owner**: Feature implementer (with PM/Architect review)

---

## Overview

This checklist ensures that documentation stays synchronized with code changes. Complete this checklist before marking a feature as "Done".

---

## Documentation Update Checklist

### 1. Product Documentation

#### docs/product/02_PRD/INDEX.md
- [ ] Update PRD status (Draft → In Progress → Delivered)
- [ ] Add delivery date
- [ ] Link to related spec in `.aod/`

#### docs/product/05_User_Stories/
- [ ] Mark completed user stories as ✅ Complete
- [ ] Update acceptance criteria status

#### docs/product/06_OKRs/
- [ ] Update key result progress if feature impacts OKRs
- [ ] Add feature delivery notes to quarterly OKR document

---

### 2. Architecture Documentation

#### docs/architecture/00_Tech_Stack/README.md
- [ ] Add any new dependencies or frameworks
- [ ] Update version numbers if major upgrades
- [ ] Document why new technology was chosen

#### docs/architecture/01_system_design/
- [ ] Update system diagrams if architecture changed
- [ ] Document new components or services
- [ ] Update data flow diagrams

#### docs/architecture/02_ADRs/
- [ ] Create ADR for any significant technical decisions
- [ ] Number sequentially (ADR-NNN)
- [ ] Document decision context, alternatives, and consequences

#### docs/architecture/03_patterns/
- [ ] Document new reusable patterns discovered
- [ ] Add code examples
- [ ] Link to related implementations

#### docs/architecture/04_deployment_environments/
- [ ] Update environment configurations if infrastructure changed
- [ ] Document new environment variables
- [ ] Update URLs or endpoints

---

### 3. DevOps Documentation

#### docs/devops/01_Local/README.md
- [ ] Update local setup instructions if new dependencies added
- [ ] Add new environment variables to example `.env`
- [ ] Document new Docker services if applicable

#### docs/devops/02_Staging/README.md
- [ ] Update staging testing procedures for new features
- [ ] Add new endpoints to smoke test checklist
- [ ] Document staging-specific configuration changes

#### docs/devops/03_Production/README.md
- [ ] Update production deployment checklist if new steps required
- [ ] Add new monitoring metrics or alerts
- [ ] Document rollback procedures for new feature

#### docs/devops/CI_CD_GUIDE.md
- [ ] Update CI/CD pipeline if new build steps added
- [ ] Document new environment variables for CI
- [ ] Add new test stages

---

### 4. Testing Documentation

#### docs/testing/README.md
- [ ] Document new testing patterns if discovered
- [ ] Add examples of tests for new feature types
- [ ] Update coverage targets if changed

---

### 5. Institutional Knowledge

#### docs/INSTITUTIONAL_KNOWLEDGE.md
- [ ] Add entry for any significant learnings
- [ ] Document solutions to non-obvious problems
- [ ] Add performance optimizations discovered
- [ ] Record architectural decisions or patterns

**When to Add Entries**:
- Solved a tricky bug (document root cause)
- Discovered a non-obvious pattern
- Made a performance optimization
- Learned something that will help future development

---

### 6. Feature-Specific Documentation

#### .aod/spec.md
- [ ] Mark spec as "Delivered" or "Complete"
- [ ] Add actual delivery date
- [ ] Document any scope changes during implementation

#### .aod/plan.md
- [ ] Mark plan as "Implemented"
- [ ] Document any architectural deviations
- [ ] Add notes on technical challenges encountered

#### .aod/tasks.md
- [ ] Mark all tasks as complete
- [ ] Document actual vs estimated effort
- [ ] Note any tasks added during implementation

---

### 7. Project-Level Documentation

#### README.md (if at project root)
- [ ] Update feature list if public-facing feature
- [ ] Update screenshots if UI changed
- [ ] Add new configuration instructions
- [ ] Update version number (if using semantic versioning)

#### CHANGELOG.md (if maintained)
- [ ] Add feature to changelog under appropriate version
- [ ] Link to PRD and spec documents
- [ ] Note breaking changes (if any)

#### Public Template Sync (agentic-oriented-development-kit)
- [ ] Run `scripts/extract.sh --sync` to propagate changes to public template
- [ ] Review diff in `../agentic-oriented-development-kit/` for any private content leakage
- [ ] Commit and push updates to public repo: https://github.com/davidmatousek/agentic-oriented-development-kit

#### API Documentation (if API changed)
- [ ] Update OpenAPI/Swagger specs
- [ ] Add new endpoint documentation
- [ ] Document new request/response schemas
- [ ] Update example requests

---

## Quick Reference: What to Update by Feature Type

### New API Endpoint
- ✅ docs/architecture/01_system_design/ (API diagram)
- ✅ docs/architecture/03_patterns/ (if new pattern)
- ✅ API documentation (OpenAPI/Swagger)
- ✅ docs/devops/02_Staging/ (smoke tests)

### New UI Component
- ✅ docs/architecture/01_system_design/ (component diagram)
- ✅ docs/architecture/03_patterns/ (component patterns)
- ✅ README.md (screenshots if major UI change)

### Infrastructure Change
- ✅ docs/architecture/00_Tech_Stack/
- ✅ docs/architecture/02_ADRs/ (new ADR)
- ✅ docs/architecture/04_deployment_environments/
- ✅ docs/devops/ (all environments affected)

### Database Schema Change
- ✅ docs/architecture/01_system_design/ (data model)
- ✅ docs/architecture/02_ADRs/ (schema decision)
- ✅ docs/architecture/03_patterns/ (migration pattern)
- ✅ docs/devops/01_Local/ (migration instructions)

### New Integration/Dependency
- ✅ docs/architecture/00_Tech_Stack/ (new dependency)
- ✅ docs/architecture/02_ADRs/ (why this integration)
- ✅ docs/devops/01_Local/ (setup instructions)
- ✅ docs/devops/03_Production/ (configuration)

---

## Automation Opportunities

Consider automating documentation updates where possible:

### Auto-Update Candidates
- **Tech Stack**: Parse package.json for dependency versions
- **API Docs**: Generate from OpenAPI spec
- **Coverage**: Auto-update test coverage metrics
- **Version**: Use conventional commits for CHANGELOG

### Manual Updates Required
- Product decisions and rationale
- Architectural context and trade-offs
- Operational procedures
- Institutional knowledge and learnings

---

## Documentation Debt

If you can't update all documentation immediately:

1. **Create GitHub Issues** for documentation debt
   - Label: `documentation`
   - Link to feature PR
   - Specify which docs need updating

2. **Track in docs/TODO.md** (create if needed)
   ```markdown
   ## Documentation TODOs
   - [ ] Update API docs for new /api/tasks endpoint (Feature 042)
   - [ ] Add ADR for Redis caching decision (Feature 043)
   ```

3. **Set Reminder** in calendar for documentation cleanup (weekly/monthly)

---

## Sign-Off

After completing this checklist:

**Documentation Updates Complete**: ✅
**Reviewed By**: [PM/Architect/Team-Lead]
**Date**: {{YYYY-MM-DD}}

**Notes**: [Any documentation that was intentionally skipped and why]

---

## Template Customization

**Project-Specific Additions**:
- Add sections for your specific documentation structure
- Include links to documentation standards
- Reference project-specific documentation tools

**Remove if Not Applicable**:
- Sections for documentation you don't maintain
- Tools you don't use (OpenAPI, CHANGELOG, etc.)

---

**Last Updated**: 2026-05-04
**Maintained By**: All team members
**Review Trigger**: When documentation structure changes
