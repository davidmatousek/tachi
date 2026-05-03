# Product Backlog

**Purpose**: Centralized product backlog powered by GitHub Issues with AOD lifecycle tracking.

---

## Source of Truth

**GitHub Issues** with `stage:*` labels are the sole source of truth for all backlog items. `BACKLOG.md` is an auto-generated view regenerated from Issues.

| Resource | Purpose | Managed By |
|----------|---------|------------|
| GitHub Issues | All ideas, scores, evidence, status, user stories | `/aod.discover`, `/aod.score`, `/aod.validate` |
| `BACKLOG.md` | Auto-generated snapshot grouped by lifecycle stage | `.aod/scripts/bash/backlog-regenerate.sh` |

### How It Works

1. **Capture**: Run `/aod.discover` to add ideas with ICE scoring → creates GitHub Issue with `stage:discover` label
2. **Score**: Ideas are scored on Impact, Confidence, and Effort (1-10 each) — stored in Issue body
3. **Validate**: Run `/aod.validate` to submit ideas for PM review → user story added to Issue body
4. **Define**: Run `/aod.define` to create a PRD → Issue moves to `stage:define`
5. **Plan/Build/Deliver**: Subsequent commands advance the Issue through lifecycle stages

### Regenerating BACKLOG.md

```bash
.aod/scripts/bash/backlog-regenerate.sh
# or
/aod.status
```

### Single-User Assumption

The backlog assumes single-user/single-agent editing via GitHub Issues. For concurrent editing, GitHub's built-in conflict resolution handles most cases.

---

## Individual Backlog Files (Legacy)

For projects not using the AOD lifecycle, individual backlog files are still supported.

## What Goes Here

- Features identified during `/aod.define` that are "nice to have"
- Ideas from `/aod.define` that were descoped from MVP
- User requests that align with vision but aren't prioritized yet
- Technical improvements that aren't urgent

## Template for Backlog Items

```markdown
# [Feature Name]

**Added**: YYYY-MM-DD
**Source**: [/aod.define | User Request | Team Idea]
**Priority**: [High | Medium | Low]
**Effort Estimate**: [Small | Medium | Large | Unknown]

## Description
[1-3 sentences describing the feature]

## Why It Was Deferred
[Why this didn't make the current cut]

## When to Revisit
[Trigger or timeframe for reconsidering this feature]
```

## Moving Items Out of Backlog

When a backlog item is ready to build:

1. Create a PRD: `/aod.define <feature-name>`
2. Reference the backlog item in the PRD
3. Follow normal Triad workflow

## Review Cadence

Review the backlog:
- **Quarterly**: During OKR planning — re-score deferred ideas with `/aod.score`
- **After MVP Launch**: Prioritize next wave of features
- **When Capacity Opens**: Look for quick wins — check P2 items in BACKLOG.md
- **Monthly**: Review deferred ideas for changed circumstances

---

*The backlog is where good ideas wait for their time.*
