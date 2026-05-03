<!--
File: CLAUDE_MD_ORGANIZATION.md
Description: Standards for organizing CLAUDE.md files in monorepos and large projects
Author/Agent: architect
Created: 2026-01-28
Last Updated: 2026-01-28
Sources: Boris Cherny (Claude Code creator), Anthropic official documentation, community best practices
-->

# CLAUDE.md Organization Standard

This document defines standards for organizing CLAUDE.md files in the AI Security Scanner monorepo, based on official Anthropic guidance and Boris Cherny's (Claude Code creator) recommendations.

## Overview

Claude Code uses **hierarchical memory loading** to provide context-appropriate guidance. Properly organized CLAUDE.md files reduce token consumption, improve relevance, and prevent context window bloat.

### Key Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| Root CLAUDE.md | <100 lines (~2,500 tokens) | Boris Cherny's team target |
| Total per-session load | <10,000 words | Recommended threshold |
| Subdirectory files | <100 lines each | Domain-specific context only |

## Memory Loading Mechanisms

### Ancestor Loading (Upward) - EAGER
When Claude Code starts, it traverses **UP** from your current directory to the filesystem root, loading every CLAUDE.md it finds. These load **immediately at startup**.

```
/Users/david/Projects/CISO_Agent/src/api/
  ↑ loads src/CLAUDE.md
  ↑ loads CLAUDE.md (root)
```

### Descendant Loading (Downward) - LAZY
CLAUDE.md files in subdirectories below your current location use **lazy loading** - they're only included when Claude reads/writes files in those directories.

```
Working in /CISO_Agent/:
  ✅ CLAUDE.md loads immediately (current directory)
  ⏳ src/CLAUDE.md loads when Claude touches src/ files
  ⏳ deployment/CLAUDE.md loads when Claude touches deployment/ files
  ❌ Sibling directories never auto-load
```

### Sibling Isolation
Files in sibling directories **never load automatically**. This is the key optimization for monorepos - frontend context doesn't pollute backend work.

## Directory Structure

### Required Structure

```
CISO_Agent/
├── CLAUDE.md                    # Root - always loads (~70 lines) ✅
├── src/
│   └── CLAUDE.md                # Source code context ✅
├── deployment/
│   └── CLAUDE.md                # Deployment context ✅
├── docs/
│   ├── CLAUDE.md                # Documentation navigation ✅
│   ├── agents/
│   │   └── CLAUDE.md            # Agent workflow context ✅
│   └── architecture/
│       └── CLAUDE.md            # Architecture navigation ✅
├── .claude/
│   ├── CLAUDE.md                # Optional: project-level overrides
│   └── rules/                   # Modular topic rules ✅
│       ├── commands.md
│       ├── governance.md
│       ├── git-workflow.md
│       └── ...
└── CLAUDE.local.md              # Personal preferences (gitignored)
```

### Current Status: ✅ Well-Organized

This project already follows best practices with 6 CLAUDE.md files:
- Root CLAUDE.md (~70 lines) - under 100 line target ✅
- 5 subdirectory CLAUDE.md files for domain-specific context ✅
- 6 modular rules in `.claude/rules/` ✅

## Memory Types Hierarchy

| Priority | Type | Location | Scope | Git |
|----------|------|----------|-------|-----|
| 1 | Managed Policy | `/Library/Application Support/ClaudeCode/CLAUDE.md` | Organization-wide | N/A |
| 2 | Project Memory | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team-shared | ✅ Commit |
| 3 | Project Rules | `./.claude/rules/*.md` | Modular topics | ✅ Commit |
| 4 | User Memory | `~/.claude/CLAUDE.md` | Personal (all projects) | ❌ Don't commit |
| 5 | Project Local | `./CLAUDE.local.md` | Personal (this project) | ❌ Gitignored |

## Content Guidelines

### What to Include

| ✅ Include | Example |
|-----------|---------|
| Commands Claude can't guess | `make deploy-backend-prod` |
| Style rules differing from defaults | "Use ES modules, not CommonJS" |
| Testing instructions | `pytest src/api/tests/` |
| Repo conventions | "Always use feature branches" |
| Architectural decisions | "PostgreSQL-only (no Redis)" |
| Environment quirks | "Requires Python 3.11+" |
| Common gotchas | "Check INSTITUTIONAL_KNOWLEDGE.md first" |

### What to Exclude

| ❌ Exclude | Why |
|-----------|-----|
| Obvious patterns | Claude can read code |
| Standard conventions | Claude knows language idioms |
| Detailed API docs | Link to docs instead |
| Frequently changing info | Gets stale |
| File-by-file descriptions | Claude can explore |
| Self-evident practices | "Write clean code" is noise |

### Import Syntax

Use `@path/to/file` to reference external files without duplicating content:

```markdown
# CLAUDE.md
See @README.md for project overview.
Testing guide: @docs/guides/DEVELOPER-TESTING-GUIDE.md
Architecture: @docs/architecture/README.md
```

**Rules:**
- Relative and absolute paths allowed
- `@~/path` for home directory imports
- Max import depth: 5 hops
- Not evaluated inside code blocks

## Path-Specific Rules

Use YAML frontmatter in `.claude/rules/` files to scope rules to specific paths:

```markdown
---
paths:
  - "src/api/**/*.py"
  - "src/core/**/*.py"
---

# Backend Development Rules
- Use parameterized queries (see DB-001 pattern)
- All endpoints require authentication
- Run `pytest` before committing
```

### Glob Patterns

| Pattern | Matches |
|---------|---------|
| `**/*.ts` | All TypeScript files |
| `src/**/*` | All files under src/ |
| `*.md` | Markdown in project root |
| `src/**/*.{ts,tsx}` | TypeScript and TSX in src/ |

## Team Workflow

### Updating CLAUDE.md

Based on Boris Cherny's team practices:

1. **When Claude does something wrong** → Add to CLAUDE.md so it doesn't repeat
2. **Multiple times per week** → Team updates CLAUDE.md regularly
3. **PR review** → Use `@.claude` tags on PRs to capture learnings
4. **Test changes** → Observe if Claude's behavior actually shifts

### Review Checklist

For each CLAUDE.md line, ask:
- "Would removing this cause Claude to make mistakes?"
- If no → Delete it
- If Claude ignores rules → File is too long, prune it

## Troubleshooting

### Claude ignores CLAUDE.md rules

**Cause:** File too long, rules getting lost in noise.
**Fix:** Ruthlessly prune. Target <100 lines for root file.

### Claude asks questions answered in CLAUDE.md

**Cause:** Phrasing is ambiguous.
**Fix:** Rewrite with emphasis ("IMPORTANT:", "YOU MUST") or clearer language.

### Context window filling too fast

**Cause:** Too much eager loading.
**Fix:** Move domain-specific content to subdirectory CLAUDE.md files (lazy loading).

### Wrong context loaded for task

**Cause:** Working directory doesn't match task domain.
**Fix:** `cd` to appropriate directory before starting Claude, or use subdirectory CLAUDE.md files.

## Maintenance Schedule

| Frequency | Action |
|-----------|--------|
| Weekly | Review and prune based on Claude behavior |
| After incidents | Add learnings to prevent recurrence |
| After refactors | Update affected subdirectory files |
| Quarterly | Audit all CLAUDE.md files for relevance |

## References

- [Claude Code Memory Documentation](https://code.claude.com/docs/en/memory)
- [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices)
- [Boris Cherny's Workflow Tips](https://karozieminski.substack.com/p/boris-cherny-claude-code-workflow)
- [Monorepo Organization Guide](https://github.com/shanraisshan/claude-code-best-practice/blob/main/reports/claude-md-for-larger-mono-repos.md)

---

*This standard ensures efficient context management and consistent CLAUDE.md organization across the AI Security Scanner project.*
