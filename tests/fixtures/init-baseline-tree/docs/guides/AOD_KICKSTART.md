# /aod.kickstart Guide

**Version**: 1.0.0
**Read Time**: ~3 minutes

**Related**:
- [AOD Quickstart](AOD_QUICKSTART.md) -- Full lifecycle reference
- Stack Pack Consumer Guide -- (Example guide available after running `/aod.kickstart`)

---

## What is Kickstart?

`/aod.kickstart` transforms a project idea into a **consumer guide** -- a sequenced backlog of 6-10 seed features ready for the AOD lifecycle. Instead of staring at an empty repo wondering "what do I build first?", you get an ordered plan with user stories, acceptance criteria, and dependency chains.

```
Your idea  ──▶  /aod.kickstart  ──▶  Consumer Guide (docs/guides/CONSUMER_GUIDE_*.md)
                                          │
                                          ├── Setup phases (clone, scaffold, install)
                                          ├── 6-10 seed features in dependency order
                                          │     ├── User stories + acceptance criteria
                                          │     ├── Interface contracts
                                          │     └── Definition of Done
                                          └── Execution instructions
```

Each seed feature block is structured for direct copy-paste into `/aod.discover`.

---

## Quick Start

```bash
/aod.kickstart
```

That's it. The skill walks you through three interactive stages:

1. **Idea Intake** -- Describe your project, target user, and 3-5 key capabilities
2. **Stack Selection** -- Use an active stack pack, pick from available packs, or describe a custom stack
3. **Guide Generation** -- Outputs a consumer guide to `docs/guides/CONSUMER_GUIDE_{PROJECT}.md`

---

## Walkthrough: AOD Information Site

Here's what a kickstart session looks like for building an information site at agentic-oriented-development.com -- a site with AOD definitions, infographics, newsletter signup, and a books section.

### Stage 1: Idea Intake

The skill asks 3 questions, then confirms:

**Q1: Describe your project idea**
> An information and marketing site for Agentic Oriented Development (AOD) at
> agentic-oriented-development.com. The site explains what AOD is through definitions
> and infographics, provides a newsletter signup for updates, and includes a section
> to showcase and sell books on AI-assisted development methodology.

**Q2: Who is the target user?**
> Technical leaders and developers evaluating AOD methodology for their teams

**Q3: List 3-5 key capabilities**
> 1. AOD definitions and methodology explainer pages with infographics
> 2. Newsletter subscription and email capture
> 3. Book showcase and purchase links
> 4. Responsive design with SEO optimization
> 5. Content management for updating articles and resources

**Confirm**: The skill shows a summary. Say "Yes" to proceed.

### Stage 2: Stack Selection

The skill checks for an active stack pack. Three paths:

| Scenario | What Happens |
|----------|-------------|
| Pack already active | Asks "Use this pack?" -- confirm or change |
| Packs available | Shows a list -- pick one or say "Custom stack" |
| No packs | Asks you to describe your stack |

For a content site, you might select `fastapi-react-local` for a dynamic site, or describe a custom stack like "Next.js 14 with MDX content, Tailwind CSS, and Vercel deployment."

### Stage 3: Guide Generation

The skill generates a consumer guide with seed features like:

| ID | Feature | Group |
|----|---------|-------|
| F-001 | Project skeleton + health check | Foundation |
| F-002 | AOD methodology content pages | Foundation |
| F-003 | Infographic components | Core |
| F-004 | Newsletter signup + email capture | Core |
| F-005 | Book showcase section | Core |
| F-006 | SEO + meta tags + Open Graph | User-Facing |
| F-007 | Responsive layout + navigation | User-Facing |
| F-008 | Content management workflow | Polish |

Each feature includes user stories, acceptance criteria, and a dependency chain -- ready to feed into the AOD lifecycle one at a time.

---

## After Kickstart: Using the Guide

The consumer guide is your project roadmap. Work through it in order:

```bash
# For each seed feature (F-001, F-002, ...):
# 1. Copy the feature block from the guide
# 2. Feed it into the AOD lifecycle:

/aod.discover    # Paste the feature block as the idea
/aod.define      # Create PRD
/aod.plan        # Spec → project-plan → tasks (auto-advances; run up to 3 times)
/aod.build       # Implement
/aod.deliver     # Close and retrospect
```

Track progress using the completion tracker at the bottom of the generated guide.

---

## How It Works

### Three Stages

| Stage | Interactive? | What It Does |
|-------|-------------|-------------|
| 1. Idea Intake | Yes (3 prompts + confirm) | Captures idea, target user, capabilities |
| 2. Stack Selection | Yes (1-4 prompts) | Detects or selects technology stack |
| 3. Guide Generation | No (autonomous) | Writes the consumer guide file |

### Stack Selection Paths

```
                    ┌─ Path A: Active pack detected ──▶ Confirm or change
                    │
Start ──▶ Check ────┼─ Path B: Packs available ──────▶ Pick from list
   .aod/            │                                     │
   stack-active     │                                     ├─ Path D: "Help me choose"
   .json            │                                     │   (4 guided questions)
                    │                                     │
                    └─ Path C: Custom stack ◀─────────────┘
                         (describe your own)
```

### Ordering Principles

Seed features follow a strict ordering:

| Tier | Position | Examples |
|------|----------|---------|
| Foundation | First | Skeleton, config, data models |
| Core Value | Second | Primary features, business logic |
| User-Facing | Third | UI, interactions, auth |
| Polish | Last | SEO, integrations, monitoring |

Every feature is independently demonstrable and only depends on earlier features.

---

## FAQ

**Do I need a stack pack to use kickstart?**
No. You can describe any custom stack. Packs just provide richer conventions for the generated guide.

**Can I run kickstart multiple times?**
Yes. If a guide already exists at the target path, the skill asks whether to overwrite, rename (date-suffixed), or cancel.

**Does kickstart create GitHub Issues?**
No. It only writes a guide document. You create issues by feeding each feature block into `/aod.discover`.

**What if my idea is vague?**
The skill asks for elaboration if your description is under 20 words. After 2 rounds, it proceeds with a note that the guide may need refinement.

**Can I edit the guide after generation?**
Absolutely. The guide is a starting point. Add features, reorder, adjust stories -- it's your roadmap.
