# Quickstart: Rename Tachi Commands to tachi.* Namespace

## Prerequisites

- Git repository with tachi installed
- Current branch: `121-rename-tachi-commands`

## Implementation Quick Reference

### Wave 1: File Renames (Foundation)

```bash
# Rename primary commands
cd .claude/commands/
git mv threat-model.md tachi.threat-model.md
git mv risk-score.md tachi.risk-score.md
git mv compensating-controls.md tachi.compensating-controls.md
git mv infographic.md tachi.infographic.md
git mv security-report.md tachi.security-report.md

# Rename adapter copies
cd adapters/claude-code/commands/
git mv threat-model.md tachi.threat-model.md
git mv infographic.md tachi.infographic.md
git mv risk-score.md tachi.risk-score.md

# Rename GitHub Actions workflow
cd adapters/github-actions/
git mv tachi-threat-model.yml tachi.threat-model.yml

# Create new architecture command
# (content per Issue #120)
```

### Wave 2: Cross-Reference Updates

For each renamed command, search and replace across the active codebase:
- Slash invocations: `/threat-model` → `/tachi.threat-model`
- File references: `threat-model.md` → `tachi.threat-model.md`

Exclude: `docs/product/02_PRD/`, `specs/*/` (except current feature)

### Wave 3: Infrastructure + Docs

1. Update `INSTALL_MANIFEST.md` with new filenames
2. Add deprecated-file cleanup to `scripts/install.sh`
3. Update all guides and root documentation
4. Add CHANGELOG migration entry

### Wave 4: Verification

```bash
# Verify zero old names outside immutables
grep -r "/threat-model\b" --include="*.md" --include="*.yml" \
  --exclude-dir="specs" --exclude-dir="docs/product/02_PRD" .

# Repeat for: /risk-score, /compensating-controls, /infographic, /security-report
```

## Validation Checklist

- [ ] All 6 `tachi.*` command files exist in `.claude/commands/`
- [ ] Zero old command name matches outside immutable artifacts
- [ ] Install script removes deprecated files on upgrade
- [ ] Install script works cleanly on fresh install
- [ ] All 6 examples validated with new names
- [ ] CHANGELOG migration entry present
