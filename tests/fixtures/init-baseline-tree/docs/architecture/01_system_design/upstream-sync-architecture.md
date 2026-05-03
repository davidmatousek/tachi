# Upstream Sync Architecture

**Owner**: Architect
**Last Updated**: 2026-03-19

---

## Overview

The AOD methodology is developed in an upstream development repo and published to a public template repo (`agentic-oriented-development-kit`) via a manifest-driven extraction pipeline. Adopters fork/clone the public template and pull improvements back using a safe merge workflow.

---

## System Diagram

```mermaid
graph TB
    subgraph DEV["Upstream Development Repo"]
        direction TB
        LIFECYCLE["/aod.define → /aod.plan → /aod.build → /aod.deliver"]
        AOD_FILES[".aod/ workspace<br/>.claude/ agents, skills, rules<br/>docs/ standards, architecture<br/>scripts/ tooling<br/>stacks/ stack packs"]
        EXTRACT["scripts/extract.sh --sync<br/>Manifest-driven extraction"]

        LIFECYCLE --> AOD_FILES
        AOD_FILES --> EXTRACT
    end

    subgraph UPSTREAM["agentic-oriented-development-kit (Public Template)"]
        direction TB
        TEMPLATE["Template files with<br/>tachi<br/>Automated threat modeling toolkit extending STRIDE with AI-specific threat agents for agentic applications<br/>placeholders"]
        SYNC_SCRIPT["scripts/sync-upstream.sh<br/>setup · check · merge · validate"]
    end

    EXTRACT -- "One-way push<br/>/aod.deliver Step 8<br/>or /aod.sync-upstream" --> TEMPLATE

    subgraph ADOPTERS["Adopter Projects"]
        direction TB
        A1["Project A<br/>(fork)"]
        A2["Project B<br/>(clone)"]
        A3["Project C<br/>(template button)"]
    end

    TEMPLATE -- "Fork / Clone /<br/>Use Template" --> A1
    TEMPLATE -- "Fork / Clone /<br/>Use Template" --> A2
    TEMPLATE -- "Fork / Clone /<br/>Use Template" --> A3

    A1 -. "Pull improvements<br/>sync-upstream.sh merge" .-> SYNC_SCRIPT
    A2 -. "Pull improvements<br/>sync-upstream.sh merge" .-> SYNC_SCRIPT
    A3 -. "Pull improvements<br/>sync-upstream.sh merge" .-> SYNC_SCRIPT

    style DEV fill:#1a1a2e,stroke:#e94560,color:#fff
    style UPSTREAM fill:#16213e,stroke:#0f3460,color:#fff
    style ADOPTERS fill:#0f3460,stroke:#533483,color:#fff
    style EXTRACT fill:#e94560,stroke:#e94560,color:#fff
    style SYNC_SCRIPT fill:#533483,stroke:#533483,color:#fff
```

---

## Push Flow: Private → Public Template

Triggered by `/aod.deliver` (Step 8) or standalone `/aod.sync-upstream`.

```mermaid
sequenceDiagram
    participant Dev as Upstream Dev Repo
    participant Extract as scripts/extract.sh
    participant Upstream as agentic-oriented-development-kit

    Dev->>Extract: --sync --dry-run (preview)
    Extract-->>Dev: Files to copy/reset/create/delete
    Dev->>Dev: User confirms
    Dev->>Extract: --sync (execute)

    Note over Extract: Manifest defines what ships

    Extract->>Upstream: Copy MANIFEST_DIRS<br/>(.claude/*, docs/*, stacks/*, .aod/scripts/*)
    Extract->>Upstream: Copy MANIFEST_FILES<br/>(CLAUDE.md, Makefile, LICENSE, etc.)
    Extract->>Upstream: Reset CONTENT_RESET_FILES<br/>(PRD INDEX, IK — cleared to template state)
    Extract->>Upstream: Delete MANIFEST_EXCLUDE_FILES<br/>(from .extractignore)

    Note over Upstream: Result: clean template<br/>with {{PLACEHOLDERS}}

    Dev->>Upstream: git commit + push (or PR)
```

### What Gets Synced (Extract Manifest)

| Category | Content | Action |
|----------|---------|--------|
| **Agent Infrastructure** | `.claude/agents/`, `skills/`, `commands/`, `rules/`, `hooks/`, `lib/`, `config/` | Copy |
| **Docs & Standards** | `docs/core_principles/`, `standards/`, `architecture/`, `guides/`, `testing/` | Copy |
| **DevOps** | `docs/devops/01_Local/`, `02_Staging/`, `03_Production/` | Copy |
| **Product Templates** | `docs/product/03_Product_Roadmap/`, `04_Journey_Maps/`, `05_User_Stories/`, `06_OKRs/` | Copy |
| **AOD Runtime** | `.aod/scripts/bash/`, `.aod/templates/` | Copy |
| **Stack Packs** | `stacks/` | Copy |
| **Root Files** | `CLAUDE.md`, `Makefile`, `.gitignore`, `LICENSE`, `.env.example`, `MIGRATION.md` | Copy |
| **Seeded Content** | `.aod/memory/constitution.md`, `scripts/init.sh`, `check.sh`, `sync-upstream.sh` | Copy |
| **Content Reset** | `docs/product/02_PRD/INDEX.md`, `docs/INSTITUTIONAL_KNOWLEDGE.md` | Copy then reset to template state |
| **Private Content** | Files in `.extractignore` | Deleted from destination |

### What Never Ships

- `specs/` (feature-specific artifacts)
- `docs/product/02_PRD/*.md` (actual PRDs, except INDEX template)
- `.aod/spec.md`, `plan.md`, `tasks.md` (active workspace)
- `.aod/memory/` (except `constitution.md` seed)
- `archive/`, `node_modules/`, `.git/`
- Any path listed in `.extractignore`

---

## Pull Flow: Public Template → Adopter

Adopters use `scripts/sync-upstream.sh` to pull improvements from the public template.

```mermaid
sequenceDiagram
    participant Adopter as Adopter Project
    participant Script as sync-upstream.sh
    participant Upstream as agentic-oriented-development-kit

    Adopter->>Script: setup (one-time)
    Script->>Upstream: git remote add aod-upstream

    Adopter->>Script: check
    Script->>Upstream: git fetch aod-upstream
    Script-->>Adopter: Categorized change list<br/>(Skills, Rules, Docs, Scripts, Core)

    Adopter->>Script: merge [--dry-run]
    Note over Script: Creates backup branch<br/>Protects .aod/memory/
    Script->>Adopter: Merged changes<br/>(resolve conflicts if any)

    Adopter->>Script: validate
    Script-->>Adopter: Post-sync integrity checks<br/>(file existence, YAML, placeholders)
```

### Protected During Merge

| Path | Why Protected |
|------|---------------|
| `.aod/memory/` | Adopter's governance memory, constitution customizations |
| Project-specific PRDs | Adopter's product decisions |
| Custom rules in `.claude/rules/` | Conflict resolution preserves local changes |

---

## Trigger Points

| Trigger | Command | What Happens |
|---------|---------|--------------|
| Feature delivery | `/aod.deliver` Step 8 | Asks user whether to sync upstream |
| Ad-hoc sync | `/aod.sync-upstream` | Standalone extract + push/PR |
| Adopter update | `sync-upstream.sh merge` | Pulls latest template into adopter repo |

---

## Key Design Decisions

- **One-way push**: Private repo is always the source of truth; public template never feeds back
- **Manifest-driven**: `scripts/extract.sh` is the single source of truth for what constitutes template content
- **Content resets**: Some files are copied then overwritten to remove project-specific data (e.g., PRD index, institutional knowledge)
- **`.extractignore`**: Works like `.gitignore` — adopters of the private repo can exclude paths from extraction
- **Bash 3.2 compatible**: All scripts use `case` statements and `while read` loops (no associative arrays) for macOS compatibility
