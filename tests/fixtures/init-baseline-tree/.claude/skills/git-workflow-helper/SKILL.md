---
name: git-workflow-helper
description: Automates git workflow tasks including status checks, branch creation, file staging, conventional commit message generation, and pull request creation with gh CLI. Use this skill when you need to commit changes, create PRs, check git status, create branches, push code, or generate commit messages. Ensures proper git workflow and commit standards.
---

# Git Workflow Helper Skill

## Purpose

Automates common git workflow tasks while enforcing best practices and commit standards. Implements FR-008 from the feature specification. Follows constitutional requirement for feature branching and proper git workflow.

## How It Works

### Step 1: Git Status Check

Always start with status to understand current state:

```bash
# Check git status
git status

# Check branch name
git branch --show-current

# Check for uncommitted changes
git diff --stat
git diff --cached --stat

# Check unpushed commits
git log @{u}.. --oneline
```

Report:
```
📊 Git Status

Branch: feature/new-feature
Tracking: origin/feature/new-feature

Changes:
  Modified: 3 files
  Staged: 1 file
  Untracked: 2 files

Unpushed commits: 2

Files:
  M  src/api/users.ts
  M  tests/users.test.ts
  ?? docs/API.md
```

### Step 2: Branch Creation

Create feature branch following naming conventions:

```bash
# Feature branch
git checkout -b feature/feature-name

# Bug fix branch
git checkout -b fix/bug-description

# Documentation branch
git checkout -b docs/topic

# Test branch
git checkout -b test/test-description

# Refactor branch
git checkout -b refactor/refactor-description
```

### Step 3: Stage Files

Intelligently stage relevant files:

```bash
# Stage specific files
git add src/api/users.ts src/models/user.ts

# Stage all in directory
git add src/

# Check what will be committed
git diff --cached
```

Avoid staging:
- Build artifacts (dist/, build/)
- Dependencies (node_modules/)
- Secrets (.env, credentials.json)
- Temporary files (*.tmp, *.log)

### Step 4: Generate Conventional Commit Message

Follow conventional commit format:

**Format**: `<type>(<scope>): <description>`

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting changes
- `refactor`: Code restructuring
- `test`: Adding/updating tests
- `chore`: Build process or auxiliary tools

**Example Generation**:

Analyze staged changes:
```bash
git diff --cached --name-only
# Output:
# src/api/users.ts
# src/models/user.ts
# tests/users.test.ts
```

Analyze diff content:
```bash
git diff --cached src/api/users.ts
# Detect: New endpoint added
```

Generated message:
```
feat(api): Add user profile update endpoint

Implements user profile update functionality with validation
and authentication checks. Includes tests for success and error cases.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Step 5: Create Commit

```bash
# Create commit with generated message
git commit -m "$(cat <<'EOF'
feat(api): Add user profile update endpoint

Implements user profile update functionality with validation
and authentication checks. Includes tests for success and error cases.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

# Verify commit
git log -1 --format="%h %s"
```

### Step 6: Push Changes

```bash
# Push to remote (creates branch if needed)
git push -u origin feature/new-feature

# Verify push
git log @{u}.. --oneline
# (should be empty - all commits pushed)
```

### Step 7: Create Pull Request

Use gh CLI to create PR. Open as **draft** during plan/build stages; mark ready at delivery.

```bash
# Generate PR description from commits
PR_TITLE="feat(api): User Profile Management"
PR_BODY=$(git log origin/main..HEAD --format="- %s")

# Create draft PR (default — used at plan stage)
gh pr create --draft \
  --title "$PR_TITLE" \
  --body "$(cat <<EOF
## Summary
${PR_BODY}

## Changes
- Added user profile update endpoint
- Implemented validation and auth checks
- Added comprehensive tests

## Testing
- Unit tests: ✓ Pass
- Integration tests: ✓ Pass
- Manual testing: ✓ Completed

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"

# Mark PR ready for review (used at deliver stage)
gh pr ready

# Get PR URL
gh pr view --web
```

**Draft vs Ready**:
- `/aod.plan` opens a draft PR at branch creation for early visibility
- `/aod.deliver` marks the PR ready via `gh pr ready` when work is complete
- If no draft PR exists (e.g., ad-hoc branches), create a regular PR directly

## Examples

### Example 1: Commit Changes

**User Query**: "Commit my changes"

**Skill Actions**:
1. Run `git status` - 3 modified files
2. Analyze changes - new feature added
3. Stage relevant files
4. Generate conventional commit message
5. Create commit
6. Verify commit created

**Result**:
```
✅ Changes Committed

Branch: feature/user-profiles
Commit: a3f2c1d

Message:
  feat(api): Add user profile endpoints

  Implements GET and PUT endpoints for user profile management
  with validation and authentication.

  🤖 Generated with Claude Code

Staged files:
  src/api/users.ts
  src/models/user.ts
  tests/users.test.ts

Next steps:
  git push -u origin feature/user-profiles
```

### Example 2: Create Pull Request

**User Query**: "Create a pull request"

**Skill Actions**:
1. Check git status - on feature branch
2. Verify commits pushed to origin
3. Generate PR title and description from commits
4. Create PR using gh CLI
5. Get PR URL

**Result**:
```
✅ Pull Request Created

PR #42: feat(api): User Profile Management
URL: https://github.com/user/repo/pull/42

Summary:
- feat(api): Add user profile endpoints
- test(api): Add profile endpoint tests
- docs(api): Document profile API

Branch: feature/user-profiles → main

Status: Ready for review

The PR has been created successfully. Share the URL with your team!
```

### Example 3: Branch Creation

**User Query**: "Create a branch for the new notification system"

**Skill Actions**:
1. Check current branch - on main
2. Ensure working directory clean
3. Create feature branch
4. Verify branch created

**Result**:
```
✅ Branch Created

Branch: feature/notification-system
Base: main (a3f2c1d)

You're now on the new branch and ready to start work!

Workflow:
1. Make your changes
2. Commit with: "commit my changes"
3. Push with: git push -u origin feature/notification-system
4. Create PR with: "create PR"
```

## Integration

### Uses

- **Bash**: Execute git and gh CLI commands
- **Read**: Analyze changed files for commit message generation
- **Grep**: Pattern match for commit types and scopes
- **TodoWrite**: Track PR creation and review tasks

### Updates

- Git repository (commits, branches, pushes)
- GitHub (pull requests via gh CLI)

### Safety Features

- **Never force push** to main/master without explicit confirmation
- **Warn on destructive operations** (reset --hard, push --force)
- **Verify before push** - show what will be pushed
- **Check for secrets** before committing

## Commit Message Generation Logic

```bash
# Analyze file types
MODIFIED_FILES=$(git diff --cached --name-only)

# Detect scope
if [[ $MODIFIED_FILES == *"src/api"* ]]; then
  SCOPE="api"
elif [[ $MODIFIED_FILES == *"tests/"* ]]; then
  SCOPE="test"
elif [[ $MODIFIED_FILES == *"docs/"* ]]; then
  SCOPE="docs"
fi

# Detect type
if grep -q "new.*function\|new.*class" <(git diff --cached); then
  TYPE="feat"
elif grep -q "fix\|bug" <(git diff --cached); then
  TYPE="fix"
elif [[ $MODIFIED_FILES == *".md" ]]; then
  TYPE="docs"
fi

# Generate message
COMMIT_MSG="${TYPE}(${SCOPE}): ${DESCRIPTION}"
```

## Constitutional Compliance

- **Git Workflow**: Enforces feature branching and proper workflow (Principle V)
- **Commit Standards**: Conventional commits for clarity
- **Never Skip Hooks**: Respects pre-commit hooks and validation
- **No Force Push**: Prevents destructive operations on shared branches
- **Safety First**: Warns before potentially dangerous git operations
