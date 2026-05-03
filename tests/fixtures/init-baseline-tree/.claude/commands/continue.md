---
description: Generate session handoff file for seamless work resumption
---

## Purpose

Capture current work context and generate NEXT-SESSION.md for seamless session handoff.

## File Location

| Branch Pattern | Output Location |
|----------------|-----------------|
| `NNN-*` (feature branch) | `specs/NNN-*/NEXT-SESSION.md` |
| Other branches | `docs/prompts/NEXT-SESSION.md` |

## Context to Capture

Run these git commands (in parallel):
- `git branch --show-current` - current branch
- `git status --porcelain` - uncommitted changes
- `git log -1 --format='%h %s'` - last commit
- `git log --oneline -5` - recent work

If on feature branch, also check:
- Which spec files exist (spec.md, plan.md, tasks.md)
- Task progress from tasks.md: count `[x]` (done) vs `[ ]` (pending)

## Phase Detection

| Files Present | Phase | Next Action |
|---------------|-------|-------------|
| No spec.md | specify | Run /aod.spec |
| No plan.md | plan | Run /aod.project-plan |
| No tasks.md | tasks | Run /aod.tasks |
| All present | implement | Next pending task from tasks.md |

## Output Template

```markdown
# Session Continuation: {Feature Name}

**Generated**: {YYYY-MM-DD HH:MM}
**Branch**: {branch}
**Last Commit**: {hash} {message}

## Completed This Session

{List recent commits from git log}

## Current State

- **Phase**: {specify|plan|tasks|implement}
- **Uncommitted**: {file count} files ({list} or "Clean - all committed")
- **Tasks**: {X}/{Y} complete (if tasks.md exists)

## Next Actions

1. {Immediate next step based on phase}
2. {Following step}

## Context Files

{List relevant files based on phase and changes}

## Resume Command

\`\`\`bash
claude "Resume {feature} (branch: {branch}). Last: {commit summary}. Next: {action}."
\`\`\`
```

## User Output

After writing NEXT-SESSION.md, report:

```
✓ Session file created: {path}

Current: {branch} | Phase: {phase} | {X} uncommitted files
Tasks: {completed}/{total} (if applicable)

Resume next session:
  claude "Resume {feature}. Last: {summary}. Next: {action}."
```

## Error Handling

| Scenario | Action |
|----------|--------|
| Not a git repo | ERROR: "Must be run from within a git repository" |
| Spec dir not found | Fall back to `docs/prompts/NEXT-SESSION.md` |
| Git commands fail | Report specific error |
