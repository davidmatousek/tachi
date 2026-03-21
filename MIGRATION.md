# Migration Guide: CLAUDE.md Modular Rules

## Overview

This guide helps you migrate from the monolithic CLAUDE.md structure (192 lines) to the new modular rules structure (80 lines or fewer).

**Benefits of Migration:**

1. **Faster Context Loading**: Load governance context in under 1 second using @-references (vs 5-10 seconds with manual `cat` commands)
2. **Easier Customization**: Edit topic-specific rule files without touching unrelated governance
3. **Better Maintainability**: Modular structure with 6 focused files instead of 1 monolithic file
4. **Reduced File Size**: CLAUDE.md reduced from 192 lines to 80 lines or fewer (58% reduction)
5. **Parallel Editing**: Team members can edit different governance topics without merge conflicts
6. **Extensibility**: Add custom rules by creating new `.claude/rules/custom.md` files

**What Changes:**

- CLAUDE.md becomes a concise 80-line overview with @-references to detailed rule files
- Governance content extracted to 6 topic-specific files in `.claude/rules/` directory
- Context loading uses instant @-syntax instead of manual bash commands
- 100% of content preserved - no information loss

**Backward Compatibility:**

The old CLAUDE.md pattern continues to work. Migration is **opt-in** and you can proceed at your own pace.

---

## Prerequisites

Before starting migration, ensure you have:

- [ ] Git repository with CLAUDE.md file (current monolithic structure)
- [ ] Git working directory is clean (no uncommitted changes)
- [ ] Backup of current CLAUDE.md: `cp CLAUDE.md CLAUDE.md.backup`
- [ ] Basic understanding of markdown and file references
- [ ] Feature branch created: `git checkout -b migrate-modular-rules`
- [ ] Text editor or IDE with markdown support

**Estimated Time**: 15-30 minutes for initial migration

---

## Migration Steps

### Step 1: Create Modular Rules Directory

Create the `.claude/rules/` directory structure:

```bash
# Create rules directory
mkdir -p .claude/rules

# Verify directory exists
ls -la .claude/rules
```

**Expected Output**: Empty directory at `.claude/rules/`

---

### Step 2: Create Empty Rule Files

Create the 6 topic-specific rule files with headers:

```bash
# Create governance.md
cat > .claude/rules/governance.md << 'EOF'
# Governance Workflow

<!-- Governance rules, sign-off requirements, and SDLC Triad workflow -->
EOF

# Create git-workflow.md
cat > .claude/rules/git-workflow.md << 'EOF'
# Git Workflow

<!-- Branch naming, commit standards, and PR policies -->
EOF

# Create deployment.md
cat > .claude/rules/deployment.md << 'EOF'
# Deployment Policy

<!-- DevOps agent requirements and verification procedures -->
EOF

# Create scope.md
cat > .claude/rules/scope.md << 'EOF'
# Scope Boundaries

<!-- Project boundaries, what this is/isn't -->
EOF

# Create commands.md
cat > .claude/rules/commands.md << 'EOF'
# Commands

<!-- Triad command reference -->
EOF

# Create context-loading.md
cat > .claude/rules/context-loading.md << 'EOF'
# Context Loading

<!-- Context loading guide by domain -->
EOF
```

**Verification**: Run `ls .claude/rules/*.md | wc -l` - should return `6`

---

### Step 3: Extract Content to Rule Files

Extract content from CLAUDE.md to topic-specific files:

#### 3a. Extract Governance Content

Copy the "Governance Workflow (MANDATORY)" and "SDLC Triad Workflow" sections to `.claude/rules/governance.md`:

```markdown
# Governance Workflow

**CRITICAL**: After creating specs/plans/tasks, you MUST auto-trigger reviews. Do not wait for user request.

| Artifact | Required Sign-offs | Agents to Invoke |
|----------|-------------------|------------------|
| spec.md | PM | product-manager |
| plan.md | PM + Architect | product-manager, architect |
| tasks.md | PM + Architect + Team-Lead | product-manager, architect, team-lead |

[... rest of governance content ...]

## SDLC Triad Workflow

The SDLC Triad ensures Product-Architecture-Engineering alignment:
- **product-manager (PM)**: Defines **What** & **Why** (user value, business goals)
- **architect**: Defines **How** (technical approach, infrastructure baseline)
- **team-lead**: Defines **When** & **Who** (timeline, agent assignments)

[... rest of triad workflow content ...]
```

#### 3b. Extract Git Workflow

Copy "Git Workflow" section content to `.claude/rules/git-workflow.md`:

```markdown
# Git Workflow

**Always use feature branches**: `git checkout -b NNN-feature-name`

- Never commit to main directly
- Create PR for review before merge
- Branch naming: `NNN-descriptive-name` (e.g., `001-initial-feature`)
```

#### 3c. Extract Deployment Policy

Copy "Deployment Policy (MANDATORY)" section to `.claude/rules/deployment.md`:

```markdown
# Deployment Policy

**ALL deployments MUST go through the devops agent.**

Before deploying:
1. Invoke devops agent (never run deploy commands directly)
2. DevOps reads: `docs/architecture/04_deployment_environments/{env}.md`
3. DevOps reads: `docs/devops/{01_Local|02_Staging|03_Production}/README.md`
4. DevOps outputs verification summary
5. Only then proceed with deployment

**Never deploy without verification** - Mismatched targets can cause data loss or service disruption.
```

#### 3d. Extract Scope Boundaries

Copy "Scope Boundaries" section to `.claude/rules/scope.md`:

```markdown
# Scope Boundaries

**WHAT THIS IS:**
- Automated threat modeling toolkit extending STRIDE with AI-specific threat agents for agentic applications
- Agentic oriented development with clear governance
- Works with any agent workflow or framework

**WHAT THIS IS NOT:**
- NOT a quick prototype (we follow proper process)
- NOT limited to a single AI agent
- NOT skipping governance for speed
```

#### 3e. Extract Commands

Copy "Commands" section to `.claude/rules/commands.md`:

```markdown
# Commands

## Triad Commands (Automatic Governance - RECOMMENDED)

```bash
/aod.define <topic>         # Create PRD with Triad validation (includes optional vision workshop)
[... rest of commands ...]
```

## Utility Commands

[... utility commands ...]
```

#### 3f. Extract Context Loading

Copy "Context Loading (READ AS NEEDED)" section to `.claude/rules/context-loading.md`:

```markdown
# Context Loading

## Start of Session - Read These First

```bash
cat docs/AOD_TRIAD.md                          # SDLC Triad quick reference
cat .aod/memory/constitution.md               # Governance principles
```

## By Domain

| Domain | Read This | When Needed |
|--------|-----------|-------------|
[... rest of context loading content ...]
```

---

### Step 4: Refactor CLAUDE.md with @-references

Replace extracted sections in CLAUDE.md with concise summaries plus @-references:

#### Example: Governance Section

**Before** (detailed content):
```markdown
## Governance Workflow (MANDATORY)

**CRITICAL**: After creating specs/plans/tasks, you MUST auto-trigger reviews...
[20+ lines of governance rules]
```

**After** (summary + @-reference):
```markdown
## Governance Workflow

**CRITICAL**: All specs/plans/tasks require sign-offs. Auto-trigger reviews after creation.

@.claude/rules/governance.md
```

**Repeat for all 6 sections**: governance, git-workflow, deployment, scope, commands, context-loading.

**Keep inline** (do NOT extract):
- Core Constraints (4 bullet points)
- Project Structure (essential orientation)
- Key Principles (quick reference)
- Tips, Tech Stack, Recent Changes, Active Technologies (project-specific)

---

### Step 5: Validate Migration

Run validation checks to ensure successful migration:

```bash
# Check CLAUDE.md line count (should be ≤80)
wc -l CLAUDE.md

# Check all 6 rule files exist
ls .claude/rules/*.md | wc -l

# Verify file sizes (each rule file should contain content)
wc -l .claude/rules/*.md

# Test @-reference syntax (try loading CLAUDE.md in Claude Code)
# Expected: @-references load inline automatically
```

**Success Criteria**:
- `wc -l CLAUDE.md` returns ≤80
- `ls .claude/rules/*.md | wc -l` returns 6
- Each rule file contains extracted content (no empty files)
- Claude Code loads @-references inline without errors

---

### Step 6: Commit Changes

Commit the migrated structure:

```bash
# Stage all changes
git add CLAUDE.md .claude/rules/

# Commit with descriptive message
git commit -m "refactor: migrate CLAUDE.md to modular rules structure

- Extract governance to .claude/rules/governance.md
- Extract git workflow to .claude/rules/git-workflow.md
- Extract deployment policy to .claude/rules/deployment.md
- Extract scope boundaries to .claude/rules/scope.md
- Extract commands to .claude/rules/commands.md
- Extract context loading to .claude/rules/context-loading.md
- Reduce CLAUDE.md from 192 lines to 80 lines (58% reduction)
- Add @-references for instant context loading

Ref: specs/001-claude-code-memory/"

# Push to remote
git push origin migrate-modular-rules
```

---

## Before/After Examples

### Example 1: CLAUDE.md File Size

**Before** (192 lines):
```markdown
# CLAUDE.md - tachi

## Core Constraints
- Product-Led: Start with product vision, PRDs, and user stories
[... 4 more constraint bullets ...]

## Git Workflow
**Always use feature branches**: `git checkout -b NNN-feature-name`
- Never commit to main directly
- Create PR for review before merge
- Branch naming: `NNN-descriptive-name` (e.g., `001-initial-feature`)

## Governance Workflow (MANDATORY)

**CRITICAL**: After creating specs/plans/tasks, you MUST auto-trigger reviews...

| Artifact | Required Sign-offs | Agents to Invoke |
|----------|-------------------|------------------|
| spec.md | PM | product-manager |
[... 15+ more lines of governance rules ...]

## SDLC Triad Workflow

The SDLC Triad ensures Product-Architecture-Engineering alignment:
[... 10+ more lines ...]

## Deployment Policy (MANDATORY)

**ALL deployments MUST go through the devops agent.**
[... 10+ more lines ...]

[... 150+ more lines of detailed content ...]
```

**After** (80 lines):
```markdown
# CLAUDE.md - tachi

## Core Constraints
- Product-Led: Start with product vision, PRDs, and user stories
- Source of Truth: `.aod/spec.md`
- Validation Required: Run `/aod.analyze` before PRs
- Local-First: Always supports local `.aod/` file workflows

## Git Workflow

**Always use feature branches**. See detailed policies:

@.claude/rules/git-workflow.md

## Governance Workflow

**CRITICAL**: All specs/plans/tasks require sign-offs. Auto-trigger reviews.

@.claude/rules/governance.md

## Deployment Policy

**ALL deployments go through devops agent**. See verification requirements:

@.claude/rules/deployment.md

## Scope Boundaries

@.claude/rules/scope.md

## Commands

@.claude/rules/commands.md

## Context Loading

@.claude/rules/context-loading.md

[... remaining inline sections: Project Structure, Key Principles, Tips ...]
```

**Line Count Comparison**:
- Before: `192 lines`
- After: `78 lines` (59% reduction)

---

### Example 2: Editing Git Workflow

**Before** (edit monolithic CLAUDE.md):
```markdown
# CLAUDE.md - 192 lines total

[... scroll through 50+ lines to find Git Workflow section ...]

## Git Workflow
**Always use feature branches**: `git checkout -b NNN-feature-name`
- Never commit to main directly
- Create PR for review before merge
- Branch naming: `NNN-descriptive-name` (e.g., `001-initial-feature`)

[... risk editing unrelated sections above/below ...]
```

**After** (edit focused git-workflow.md):
```markdown
# .claude/rules/git-workflow.md - 15 lines total

# Git Workflow

**Always use feature branches**: `git checkout -b NNN-feature-name`

- Never commit to main directly
- Create PR for review before merge
- Branch naming: `NNN-descriptive-name` (e.g., `001-initial-feature`)

[... no unrelated content to navigate ...]
```

**Time to Edit**:
- Before: ~2 minutes (find section, edit carefully, avoid breaking other sections)
- After: ~30 seconds (open focused file, edit, save)

---

### Example 3: Context Loading Diff

**Before** (manual cat commands):
```markdown
## Context Loading (READ AS NEEDED)

### Start of Session - Read These First
```bash
cat docs/AOD_TRIAD.md                          # SDLC Triad quick reference
cat .aod/memory/constitution.md               # Governance principles
```

[Agent must execute bash commands manually - 5-10 seconds]
```

**After** (@-reference instant loading):
```markdown
## Context Loading

@.claude/rules/context-loading.md

[Agent loads content inline automatically - under 1 second]
```

**Performance**:
- Before: 5-10 seconds (agent executes `cat` commands, waits for output)
- After: <1 second (instant inline loading with @-references)

---

## Validation

### Automated Validation Commands

Run these commands to verify successful migration:

```bash
# 1. Verify CLAUDE.md line count ≤80
wc -l CLAUDE.md
# Expected output: ≤80 lines

# 2. Verify all 6 rule files exist
ls .claude/rules/*.md | wc -l
# Expected output: 6

# 3. Verify each rule file has content (not empty)
for file in .claude/rules/*.md; do
  echo "$file: $(wc -l < "$file") lines"
done
# Expected: Each file has >5 lines

# 4. Check for @-references in CLAUDE.md
grep -c "@.claude/rules/" CLAUDE.md
# Expected: ≥6 (one for each rule file)

# 5. Verify no broken @-references
for ref in $(grep -o "@.claude/rules/[a-z-]*\.md" CLAUDE.md); do
  file="${ref#@}"
  if [ ! -f "$file" ]; then
    echo "ERROR: Missing file: $file"
  else
    echo "OK: $file exists"
  fi
done
# Expected: All files exist

# 6. Compare total content size (should be similar)
cat CLAUDE.md.backup | wc -l
cat CLAUDE.md .claude/rules/*.md | wc -l
# Expected: Total lines similar (content preserved)
```

### Manual Validation Checklist

- [ ] CLAUDE.md is ≤80 lines
- [ ] All 6 rule files exist in `.claude/rules/`
- [ ] Each rule file contains focused, single-topic content
- [ ] @-references in CLAUDE.md match existing rule files
- [ ] No content lost during migration (compare old vs new)
- [ ] Claude Code loads @-references inline without errors
- [ ] Can edit individual rule files without affecting others

### Test in Claude Code

Open your project in Claude Code and verify:

1. **Test @-reference Loading**: Ask agent to read CLAUDE.md and confirm they can access rule file content inline
2. **Test Context Speed**: Measure how long it takes agent to load governance context (should be <1 second)
3. **Test Error Handling**: Temporarily rename a rule file and verify agent shows clear "file not found" error

---

## Rollback Instructions

If you encounter issues and need to revert to the monolithic structure:

### Quick Rollback (restore backup)

```bash
# 1. Restore backup CLAUDE.md
cp CLAUDE.md.backup CLAUDE.md

# 2. Remove modular rules directory (optional)
rm -rf .claude/rules/

# 3. Verify restoration
wc -l CLAUDE.md
# Expected: 192 lines (original size)

# 4. Commit rollback
git add CLAUDE.md
git commit -m "rollback: revert to monolithic CLAUDE.md structure"
git push origin migrate-modular-rules
```

### Gradual Rollback (keep some modular rules)

If you want to keep the modular structure but restore some content to CLAUDE.md:

```bash
# 1. Open CLAUDE.md and rule file side-by-side
code CLAUDE.md .claude/rules/governance.md

# 2. Copy content from rule file back to CLAUDE.md section
# 3. Remove @-reference from CLAUDE.md
# 4. Delete rule file (optional)

# Repeat for each section you want to roll back
```

**Note**: You can migrate incrementally. No need to migrate all sections at once.

---

## Troubleshooting

### Issue 1: CLAUDE.md still over 80 lines after migration

**Symptoms**: `wc -l CLAUDE.md` returns >80 lines

**Causes**:
- Not all extractable content was moved to rule files
- Too much inline content kept in CLAUDE.md

**Solutions**:
1. Review each section in CLAUDE.md and identify content that can be extracted
2. Ensure only summaries (1-2 sentences) plus @-references remain for extracted topics
3. Keep only essential orientation content inline (Project Structure, Key Principles)

**Validation**:
```bash
# Identify longest sections in CLAUDE.md
awk '/^## / {if (section) print lines, section; section=$0; lines=0} {lines++} END {print lines, section}' CLAUDE.md | sort -rn
```

---

### Issue 2: @-references not loading inline

**Symptoms**: Agent doesn't see rule file content when reading CLAUDE.md

**Causes**:
- Incorrect @-reference syntax
- File path doesn't exist
- Claude Code version doesn't support @-syntax

**Solutions**:
1. Verify @-reference syntax: `@.claude/rules/filename.md` (no spaces, starts with @)
2. Check file exists: `ls .claude/rules/filename.md`
3. Ensure relative path from repository root (not absolute path)

**Validation**:
```bash
# Test @-reference file exists
for ref in $(grep -o "@[^ ]*\.md" CLAUDE.md); do
  file="${ref#@}"
  [ -f "$file" ] && echo "✓ $file" || echo "✗ $file (MISSING)"
done
```

---

### Issue 3: Content missing after migration

**Symptoms**: Some governance rules no longer accessible

**Causes**:
- Content wasn't copied to rule file before removing from CLAUDE.md
- Rule file was deleted accidentally

**Solutions**:
1. Restore from backup: `cp CLAUDE.md.backup CLAUDE.md.temp`
2. Compare original vs new: `diff CLAUDE.md.backup CLAUDE.md`
3. Extract missing content from backup to appropriate rule file
4. Re-add @-reference to CLAUDE.md

**Prevention**: Always verify content preservation before deleting from CLAUDE.md

---

### Issue 4: Merge conflicts when collaborating

**Symptoms**: Git merge conflicts in CLAUDE.md when teammate made changes

**Causes**:
- Multiple people editing CLAUDE.md simultaneously
- Migration happened while teammate was working on old structure

**Solutions**:
1. Coordinate migration timing with team (avoid during active development)
2. Create migration PR and have team review before merging
3. After migration, team members update their branches: `git rebase main`

**Best Practice**: Announce migration in team channel before starting

---

### Issue 5: Circular @-reference error

**Symptoms**: Error message about circular reference detected

**Causes**:
- Rule file A references rule file B, which references rule file A
- Nested @-references exceed depth limit (3 levels)

**Solutions**:
1. Review @-references in rule files: `grep -r "@.claude/rules/" .claude/rules/`
2. Remove circular references (rule files should be self-contained)
3. Restructure content to avoid circular dependencies

**Validation**:
```bash
# Check for @-references in rule files (should be minimal)
grep -r "@" .claude/rules/
```

---

## FAQ

### Q1: Do I have to migrate immediately?

**A**: No, migration is **opt-in**. The old monolithic CLAUDE.md pattern continues to work. You can migrate at your own pace or stay on the old structure indefinitely.

---

### Q2: Can I migrate only some sections?

**A**: Yes, you can migrate incrementally. For example, extract only governance and deployment rules first, then migrate other sections later. Just ensure each extracted section has a corresponding @-reference in CLAUDE.md.

---

### Q3: What if my customized CLAUDE.md has extra sections?

**A**: You can create custom rule files for your sections:
1. Create `.claude/rules/my-custom-rule.md`
2. Extract your custom content to that file
3. Add `@.claude/rules/my-custom-rule.md` to CLAUDE.md

The modular structure supports custom rules beyond the 6 core files.

---

### Q4: Will this break existing agents that read CLAUDE.md?

**A**: No. Claude Code supports @-reference syntax and loads files inline automatically. Agents will see the same content, just structured differently. If an agent doesn't support @-syntax, they'll see the @-reference path as plain text (graceful degradation).

---

### Q5: How do I know which content belongs in which rule file?

**A**: Follow the single responsibility principle:

- **governance.md**: Sign-off requirements, review workflows, SDLC Triad roles
- **git-workflow.md**: Branch naming, commit standards, PR policies
- **deployment.md**: DevOps agent requirements, verification procedures
- **scope.md**: Project boundaries, what this is/isn't
- **commands.md**: Triad command reference
- **context-loading.md**: Context loading guide by domain

If content doesn't fit these 6 categories, create a custom rule file.

---

### Q6: Can I use @-references in rule files?

**A**: Yes, but keep it minimal. Nested @-references are supported up to depth 3. However, rule files should generally be self-contained to avoid complexity.

---

### Q7: What happens if I delete a rule file by accident?

**A**: Claude Code will show a clear error message indicating the file is missing. You can restore from git history:

```bash
# Restore deleted file
git checkout HEAD -- .claude/rules/governance.md
```

Or restore from your backup: `cp CLAUDE.md.backup CLAUDE.md` and re-extract.

---

### Q8: Does this work with CI/CD pipelines?

**A**: Yes, the modular structure works seamlessly with CI/CD. All files are committed to git, so agents in CI/CD environments can access them normally. Just ensure `.claude/rules/` is not in `.gitignore`.

---

### Q9: How do I validate that 100% of content is preserved?

**A**: Compare line counts and content:

```bash
# Total lines before migration
wc -l CLAUDE.md.backup

# Total lines after migration (CLAUDE.md + all rule files)
cat CLAUDE.md .claude/rules/*.md | wc -l

# Should be similar (±10 lines due to headers)
```

Manually review each section to ensure nothing was lost.

---

### Q10: Can I revert to the old structure later?

**A**: Yes, see [Rollback Instructions](#rollback-instructions). You can restore your backup or gradually move content back to CLAUDE.md. Migration is fully reversible.

---

## Extending with Custom Rules

The modular rules structure supports custom rule files beyond the 6 core governance files. This allows you to add project-specific or team-specific rules without modifying core files.

### Why Create Custom Rules?

**Use Cases**:
- Team-specific code review standards
- Project-specific security policies
- Custom deployment procedures
- Domain-specific architectural patterns
- Team collaboration guidelines

**Benefits**:
- Keeps core rule files unchanged (easier to upgrade template)
- Isolates team-specific customizations
- Maintains modular structure benefits
- Prevents merge conflicts with template updates

---

### Creating a Custom Rule File

**Step 1**: Create your custom rule file in `.claude/rules/`

```bash
# Example: Create code review standards file
cat > .claude/rules/code-review.md << 'EOF'
# Code Review Standards

<!-- Custom rule file for team-specific code review policies -->
<!-- This file is referenced from CLAUDE.md using @-syntax -->

## Overview

This file defines code review standards for our team. All pull requests must follow these guidelines before merge.

---

## Review Checklist

Before approving a PR, reviewers must verify:

- [ ] Code follows team style guide
- [ ] All tests pass in CI/CD
- [ ] No security vulnerabilities introduced
- [ ] Documentation updated if API changes
- [ ] Performance impact assessed for critical paths

---

## Approval Requirements

| PR Type | Required Approvals | Review Time SLA |
|---------|-------------------|-----------------|
| Bug fix | 1 reviewer | 24 hours |
| Feature | 2 reviewers (1 architect) | 48 hours |
| Breaking change | 3 reviewers (1 architect + 1 PM) | 72 hours |

---

## Security Review

All PRs touching authentication, authorization, or sensitive data require:
1. Security review from designated security champion
2. Automated security scan (Snyk, SonarQube) passing
3. Manual penetration testing for authentication changes

EOF
```

**Step 2**: Add @-reference in CLAUDE.md

Open `CLAUDE.md` and add a new section with @-reference:

```markdown
# CLAUDE.md - tachi

<!-- ... existing sections ... -->

## Code Review Standards

All PRs must follow team review policies:

@.claude/rules/code-review.md

<!-- ... rest of CLAUDE.md ... -->
```

**Step 3**: Validate the custom rule

```bash
# Verify file exists
ls .claude/rules/code-review.md

# Check @-reference syntax
grep "@.claude/rules/code-review.md" CLAUDE.md

# Test in Claude Code (agent should load content inline)
```

---

### Custom Rule Best Practices

**1. Keep Files Focused**: One topic per file
```
✅ Good: .claude/rules/security-standards.md (single topic)
❌ Bad: .claude/rules/misc-rules.md (multiple unrelated topics)
```

**2. Use Clear Headers**: Help agents navigate content
```markdown
# Security Standards

## Overview
[Brief description]

## Password Requirements
[Specific rules]

## Data Encryption
[Specific rules]
```

**3. Add Metadata Comments**: Document purpose and ownership
```markdown
# Code Review Standards

<!-- Custom rule file for team-specific code review policies -->
<!-- Owner: Engineering Team -->
<!-- Last Updated: 2025-12-15 -->
```

**4. Self-Contained Content**: Minimize @-references to other rule files
```
✅ Good: Complete content in single file
⚠️ OK: Reference 1-2 related core files
❌ Bad: Chain of 5+ @-references
```

**5. Keep CLAUDE.md Summary Brief**: 1-2 sentences + @-reference
```markdown
## Code Review Standards

All PRs follow team review policies with approval requirements:

@.claude/rules/code-review.md
```

---

### Custom Rule Examples

#### Example 1: Security Policy

**File**: `.claude/rules/security-policy.md`

```markdown
# Security Policy

## Data Classification

- **Public**: No restrictions
- **Internal**: Employee access only
- **Confidential**: Role-based access required
- **Restricted**: Legal/compliance approval required

## Encryption Requirements

| Data Type | At Rest | In Transit |
|-----------|---------|------------|
| Passwords | bcrypt (12 rounds) | TLS 1.3 |
| PII | AES-256 | TLS 1.3 |
| API Keys | Vault (encrypted) | TLS 1.3 |

## Vulnerability Response SLA

- **Critical**: Patch within 24 hours
- **High**: Patch within 7 days
- **Medium**: Patch within 30 days
- **Low**: Patch within 90 days
```

**CLAUDE.md Reference**:
```markdown
## Security Policy

Security standards for data classification and vulnerability response:

@.claude/rules/security-policy.md
```

---

#### Example 2: Testing Standards

**File**: `.claude/rules/testing-standards.md`

```markdown
# Testing Standards

## Test Coverage Requirements

| Code Type | Minimum Coverage | Required Tests |
|-----------|-----------------|----------------|
| Business Logic | 80% | Unit + Integration |
| API Endpoints | 100% | Integration + E2E |
| UI Components | 70% | Unit + Visual Regression |
| Utilities | 90% | Unit |

## Test Pyramid

1. **70% Unit Tests**: Fast, isolated, mock dependencies
2. **20% Integration Tests**: Real dependencies, realistic scenarios
3. **10% E2E Tests**: Full user journeys, critical paths only

## CI/CD Requirements

All PRs must:
- [ ] Pass all existing tests (100% pass rate)
- [ ] Maintain or improve coverage (no coverage decrease)
- [ ] Add tests for new features (code + tests in same PR)
```

**CLAUDE.md Reference**:
```markdown
## Testing Standards

Test coverage requirements and CI/CD policies:

@.claude/rules/testing-standards.md
```

---

#### Example 3: Deployment Checklist

**File**: `.claude/rules/deployment-checklist.md`

```markdown
# Deployment Checklist

## Pre-Deployment

- [ ] All tests passing in staging
- [ ] Database migrations tested
- [ ] Feature flags configured
- [ ] Rollback plan documented
- [ ] Monitoring alerts configured
- [ ] Stakeholders notified

## During Deployment

- [ ] Deploy to staging first
- [ ] Smoke tests pass
- [ ] Gradual rollout (10% → 50% → 100%)
- [ ] Monitor error rates and latency

## Post-Deployment

- [ ] Verify health checks passing
- [ ] Check error logs for anomalies
- [ ] Validate key user journeys
- [ ] Update deployment log
- [ ] Announce deployment completion
```

**CLAUDE.md Reference**:
```markdown
## Deployment Checklist

Pre/during/post deployment validation steps:

@.claude/rules/deployment-checklist.md
```

---

### Managing Custom Rules

**Version Control**:
```bash
# Commit custom rules to your repository
git add .claude/rules/code-review.md
git commit -m "feat: add code review standards"
```

**Upgrading Template**:
When upgrading Agentic Oriented Development Kit template:
1. Core rule files may be updated (governance.md, commands.md, etc.)
2. Your custom rule files remain untouched
3. Merge conflicts only in CLAUDE.md (easy to resolve)

**Team Collaboration**:
```bash
# Create feature branch for new custom rule
git checkout -b add-security-policy

# Add custom rule file
# Add @-reference to CLAUDE.md
# Create PR for team review

git add .claude/rules/security-policy.md CLAUDE.md
git commit -m "feat: add security policy custom rule"
git push origin add-security-policy
```

---

### Validation Checklist

After creating a custom rule file:

- [ ] File exists in `.claude/rules/`
- [ ] File has clear header and sections
- [ ] Content is focused on single topic
- [ ] CLAUDE.md has @-reference to custom file
- [ ] @-reference loads inline in Claude Code
- [ ] No circular @-references (rule A → rule B → rule A)
- [ ] File committed to git and pushed to remote

---

## Next Steps

After successful migration:

1. **Delete backup**: `rm CLAUDE.md.backup` (once you've verified migration)
2. **Update team documentation**: Inform team about new structure
3. **Create custom rules**: Add team-specific rules as needed (see [Extending with Custom Rules](#extending-with-custom-rules))
4. **Monitor performance**: Track context loading speed improvements (<1 second)
5. **Share feedback**: Report any issues or suggestions for future improvements

**Migration Support**: If you encounter issues not covered in this guide, please file an issue in the repository with:
- Description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Output of validation commands

---

**End of Migration Guide**
