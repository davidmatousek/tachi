---
description: View lifecycle stage summary and regenerate BACKLOG.md from GitHub Issues
---

## Overview

On-demand backlog snapshot and lifecycle stage summary. Regenerates BACKLOG.md from GitHub Issues and displays item counts per lifecycle stage.

**No governance gates** — this is a read-only utility command.

## Execute

Follow the workflow defined in the ~aod-status skill (`.claude/skills/~aod-status/SKILL.md`):

1. Run `.aod/scripts/bash/backlog-regenerate.sh --json` to regenerate BACKLOG.md
2. Parse output to count items per stage (Discover, Define, Plan, Build, Deliver, Untracked)
3. Display formatted stage summary table with totals
4. If on a feature branch, show active feature artifact approval status

## Quality Checklist

- [ ] BACKLOG.md regenerated (or fallback used if gh unavailable)
- [ ] Stage counts displayed in table format
- [ ] Total count matches sum of stages
- [ ] Active feature context shown if on feature branch
