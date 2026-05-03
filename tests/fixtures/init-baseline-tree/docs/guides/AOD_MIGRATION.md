# AOD Migration Reference

A quick-lookup guide for transitioning from the old `/pdl.*` and `/triad.*` command namespaces to the unified `/aod.*` namespace. All behavior is identical -- only names have changed.

---

## Command Mapping

### Lifecycle Commands

| Before | After | Stage |
|--------|-------|-------|
| `/pdl.idea` + `/pdl.validate` + `/pdl.run` | `/aod.discover` | Discover |
| `/pdl.score` | `/aod.score` | Discover (utility) |
| `/aod.define` | `/aod.define` | Define |
| `/aod.spec` | `/aod.spec` | Plan (sub-step) |
| `/aod.project-plan` | `/aod.project-plan` | Plan (sub-step) |
| `/aod.tasks` | `/aod.tasks` | Plan (sub-step) |
| -- (NEW) | `/aod.plan` | Plan (router) |
| `/aod.build` | `/aod.build` | Build |
| `/aod.deliver` | `/aod.deliver` | Deliver |
| -- (NEW) | `/aod.document` | Document |

### Utility Commands

| Before | After | Notes |
|--------|-------|-------|
| `/aod.analyze` | `/aod.analyze` | Cross-artifact consistency check |
| `/aod.clarify` | `/aod.clarify` | Resolve spec ambiguities |
| `/aod.checklist` | `/aod.checklist` | Definition of Done checklist |
| `/aod.constitution` | `/aod.constitution` | View or update governance |
| -- (NEW) | `/aod.status` | On-demand backlog snapshot |

### Unchanged Commands

| Command | Notes |
|---------|-------|
| `/continue` | Not lifecycle-specific -- unchanged |
| `/execute` | Not lifecycle-specific -- unchanged |

---

## Skill Directory Renames

| Old Directory | New Directory | Notes |
|---------------|---------------|-------|
| `.claude/skills/pdl-idea/` | `.claude/skills/~aod-discover/` | Merged with pdl-validate and pdl-run |
| `.claude/skills/pdl-validate/` | `.claude/skills/~aod-discover/` | Merged into ~aod-discover |
| `.claude/skills/pdl-run/` | `.claude/skills/~aod-discover/` | Merged into ~aod-discover |
| `.claude/skills/pdl-score/` | `.claude/skills/~aod-score/` | Renamed |
| `.claude/skills/prd-create/` | `.claude/skills/~aod-define/` | Renamed |
| `.claude/skills/spec-validator/` | `.claude/skills/~aod-spec/` | Renamed |
| `.claude/skills/architecture-validator/` | `.claude/skills/~aod-project-plan/` | Renamed |
| `.claude/skills/thinking-lens/` | `.claude/skills/aod-lens/` | Renamed (no ~ prefix — no command collision) |
| `.claude/skills/implementation-checkpoint/` | `.claude/skills/~aod-build/` | Renamed |

**New skills** (no old equivalent):

| Directory | Purpose |
|-----------|---------|
| `.claude/skills/~aod-plan/` | Plan stage router -- auto-detects sub-step |
| `.claude/skills/~aod-status/` | On-demand backlog regeneration |
| `.claude/skills/~aod-deliver/` | Delivery with structured retrospective |

---

## Guide File Renames

| Old File | New File |
|----------|----------|
| `docs/guides/PDL_TRIAD_QUICKSTART.md` | `docs/guides/AOD_QUICKSTART.md` |
| `docs/guides/PDL_TRIAD_LIFECYCLE.md` | `docs/guides/AOD_LIFECYCLE_GUIDE.md` |
| `docs/guides/PDL_TRIAD_INFOGRAPHIC.md` | `docs/guides/AOD_INFOGRAPHIC.md` |

**New files** (no old equivalent):

| File | Purpose |
|------|---------|
| `docs/guides/AOD_LIFECYCLE.md` | Lifecycle reference (6 stages, governance tiers, command mapping) |
| `docs/guides/AOD_MIGRATION.md` | This document |

---

## For Existing Users

If you have muscle memory for the old command names, here is what you need to know:

1. **All behavior is identical.** The `/aod.*` commands do exactly the same thing as their `/pdl.*` and `/triad.*` predecessors. Only the names changed.

2. **`/continue` and `/execute` are unchanged.** These commands are not lifecycle-specific and were not renamed.

3. **Your existing specs, plans, and tasks files are unaffected.** The `.aod/spec.md`, `.aod/plan.md`, and `.aod/tasks.md` files keep their names and format. Frontmatter structure is unchanged.

4. **The lifecycle documentation explains the new model.** See `docs/guides/AOD_LIFECYCLE.md` for the full 6-stage lifecycle reference, governance tier descriptions, and a "Where Do I Find Things?" cross-zone guide.

---

## New Concepts

Three capabilities are new in this release and have no old equivalent.

### Plan Router (`/aod.plan`)

A single entry point for the Plan stage. Instead of remembering whether to run `/aod.spec`, `/aod.project-plan`, or `/aod.tasks`, type `/aod.plan` at the start of each session. The router reads artifact frontmatter to detect which sub-step you are on and auto-invokes the correct command.

- No spec.md yet? Router calls `/aod.spec`.
- Spec approved but no plan.md? Router calls `/aod.project-plan`.
- Plan approved but no tasks.md? Router calls `/aod.tasks`.
- All approved? Router reports "Plan stage complete. Run `/aod.build` to proceed."

Direct sub-commands (`/aod.spec`, `/aod.project-plan`, `/aod.tasks`) still work independently for power users.

### Governance Tiers (Light / Standard / Full)

Choose how much ceremony your project needs. The tier determines which governance gates are active at each lifecycle stage.

| Tier | Gates | Best For |
|------|-------|----------|
| **Light** | 2 (Triple sign-off + DoD) | Solo projects, prototypes, low-risk features |
| **Standard** | 6 (default) | Team projects, production features |
| **Full** | All gates including separate PM spec sign-off | Regulated environments, high-risk features |

Configure in `.aod/memory/constitution.md`:

```yaml
governance:
  tier: standard  # light | standard | full
```

Triple sign-off is the minimum governance floor for all tiers.

### GitHub-Backed Tracking

Every `/aod.*` lifecycle command now updates a GitHub Issue with a `stage:*` label reflecting the current lifecycle stage. After each command, `BACKLOG.md` is regenerated from GitHub Issues, grouped by stage (Discover, Define, Plan, Build, Deliver, Document).

- Run `/aod.status` at any time for an on-demand backlog snapshot with item counts per stage.
- If `gh` CLI is unavailable or no GitHub remote is configured, commands proceed normally and skip GitHub operations with a warning.
