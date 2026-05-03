# AOD Guide Index

The decision page for anyone starting an AOD session. Pick the mode that matches what you're trying to do today, then follow the linked guide.

---

## Taxonomy

Terms used on this page and across the AOD docs. Skim this once — the modes table below assumes these definitions.

| Term | Meaning in AOD |
|---|---|
| **Sprint** | One feature taken through the six-stage lifecycle (Discover → Define → Plan → Build → Deliver → Document). A single unit of delivery. |
| **Epic** | A multi-sprint effort. Typically 6-10 related features sequenced by `/aod.kickstart` (into a consumer guide) and then executed as a batch via `/aod.blueprint` + `/aod.orchestrate`. |
| **Consumer guide** | The markdown output of `/aod.kickstart` — a dependency-ordered backlog of seed features with user stories, acceptance criteria, and interface contracts. Input to `/aod.blueprint`. |
| **Blueprint** | ICE-scored GitHub Issues generated from a consumer guide. The structured backlog that `/aod.orchestrate` consumes. |
| **Wave** | A group of GitHub Issues `/aod.orchestrate` runs in parallel. Grouped by priority tier (P0, P1, P2); waves execute sequentially but issues within a wave run concurrently. |
| **Stage** | One of the six lifecycle steps. Each produces a specific artifact (scored idea, PRD, spec.md, plan.md, tasks.md, shipped code, retrospective, quality review). |
| **Phase** | A grouping of stages — Discovery (stages 1-2), Delivery (stages 3-5), Quality (stage 6). |
| **Triad** | The three governance roles that sign off at gates: PM (what/why), Architect (how), Team-Lead (when/who). |
| **Tier** | Governance depth — Light (2 gates), Standard (6 gates, default), Full (all gates). Configured in `.aod/memory/constitution.md`. See [AOD_LIFECYCLE.md](AOD_LIFECYCLE.md#governance-tiers). |
| **ICE** | Impact × Confidence × Effort scoring. Each dimension 1-10, total 3-30. P0 = 25-30, P1 = 18-24, P2 = 12-17, Deferred = <12. |
| **AOD-kit** | The public AOD template repository your project was created from. `.aod/aod-kit-version` records which tag your project is synced to. `/aod.update` fetches new versions from here. |

---

## Ways to Use AOD

Eight modes organized by intent.

### Feature work (one feature at a time)

| Mode | Entry | Read |
|---|---|---|
| Classic sprint — human-led, full Triad governance | `/aod.discover` → `/aod.define` → `/aod.plan` → `/aod.build` → `/aod.deliver` → `/aod.document` | [AOD_LIFECYCLE.md](AOD_LIFECYCLE.md) |
| Full automated lifecycle — chains stages 1-5 with session-resilient state | `/aod.run` | [AOD_LIFECYCLE.md](AOD_LIFECYCLE.md) + [`aod.run.md`](../../.claude/commands/aod.run.md) |
| Bug fix — diagnose, fix, test, deliver, document _(planned, not yet shipped)_ | `/aod.bugfix` | TBD |

### Project bootstrap (many features at once)

| Mode | Entry | Read |
|---|---|---|
| POC kickstart — turn a raw idea into a sequenced consumer guide with seed features | `/aod.kickstart` | [AOD_KICKSTART.md](AOD_KICKSTART.md) |
| Multi-sprint epic (generate backlog) — convert a consumer guide into ICE-scored GitHub Issues | `/aod.blueprint` | [`aod.blueprint.md`](../../.claude/commands/aod.blueprint.md) |
| Multi-sprint epic (execute autonomously) — run the backlog in P0/P1/P2 parallel waves | `/aod.orchestrate` | [`aod.orchestrate.md`](../../.claude/commands/aod.orchestrate.md) |

### Setup (one-time, post-init)

| Mode | Entry | Read |
|---|---|---|
| Foundation workshop — establish product vision and design identity | `/aod.foundation` | [AOD_QUICKSTART.md](AOD_QUICKSTART.md) + [`aod.foundation.md`](../../.claude/commands/aod.foundation.md) |

### Template maintenance

| Mode | Entry | Read |
|---|---|---|
| Pull upstream AOD-kit template updates into your project | `/aod.update` | [DOWNSTREAM_UPDATE.md](DOWNSTREAM_UPDATE.md) |

---

## Guides Index

| File | What it covers |
|---|---|
| [AOD_QUICKSTART.md](AOD_QUICKSTART.md) | 5-minute onboarding — the six primary lifecycle commands, ICE scoring, governance tiers |
| [AOD_LIFECYCLE.md](AOD_LIFECYCLE.md) | Full lifecycle reference — stage definitions, governance tiers, command reference, traceability, end-to-end example |
| [AOD_INFOGRAPHIC.md](AOD_INFOGRAPHIC.md) | Visual at-a-glance lifecycle diagram |
| [AOD_KICKSTART.md](AOD_KICKSTART.md) | Walkthrough for `/aod.kickstart` — POC bootstrap with seed features |
| [DOWNSTREAM_UPDATE.md](DOWNSTREAM_UPDATE.md) | Adopter-facing `/aod.update` guide — pull upstream template updates (F129) |

---

## Related

- Slash command definitions: [`.claude/commands/aod.*.md`](../../.claude/commands/)
- SDLC Triad reference: [`docs/AOD_TRIAD.md`](../AOD_TRIAD.md)
- Governance constitution: [`.aod/memory/constitution.md`](../../.aod/memory/constitution.md)
