# Knowledge System Stack

**Target**: Knowledge workers building agentic content systems — professionals who manage domain expertise (resume writing, publishing, education, consulting) and want AI-orchestrated workflows to produce high-quality, voice-consistent outputs at scale
**Stack**: Markdown + YAML + Claude Code (orchestration layer via `.claude/` commands, agents, skills)
**Use Case**: Two-level architecture for knowledge-intensive domains — build the orchestration (commands, agents, content architecture) using the AOD lifecycle, then run that orchestration to produce domain outputs
**Deployment**: Local filesystem. No server, no database, no cloud services required
**Philosophy**: Content-as-data, command-per-workflow, lazy context loading, master content immutability

---

## Architecture Pattern

### Two-Level Architecture

Knowledge systems operate at two distinct levels. Conflating them is the most common failure mode.

**Build-time (AOD lifecycle)**: You use `/aod.define`, `/aod.spec`, `/aod.project-plan`, `/aod.tasks`, `/aod.build`, and `/aod.deliver` to design and construct the orchestration itself — the commands, agent personas, content architecture, quality rubric, and context loading configuration. The product of build-time is a working orchestration system.

**Run-time (domain orchestration)**: You use the commands YOU built (e.g., `/new`, `/draft`, `/review`, `/export`) to produce domain outputs — tailored resumes, edited chapters, lesson plans, consulting deliverables. The product of run-time is domain content.

**Rule**: AOD commands design the system. Product commands operate the system. NEVER use AOD commands as run-time product commands. NEVER build product commands that duplicate AOD lifecycle functions.

### Hub-and-Spoke Content Architecture

All knowledge systems share a hub-and-spoke model:

```
                    _Global/ (hub)
                   /    |    \
          Voice  Style  Master  Narratives
            |      |   Content    |
            v      v      |      v
         _Config/ (spoke configuration)
        /    |      \        \
  Context  Scoring  Presets  Terms
  Loading  Rubric
            |
            v
      _Templates/ (output format definitions)
            |
            v
      _Output/ (active instances) --> _Archive/ (completed)
```

- **Hub** (`_Global/`): Source of truth. VoiceProfile, StyleGuide, MasterContent, and Narratives. NEVER modified per-output.
- **Spoke configuration** (`_Config/`): ContextLoading, ScoringRubric, Presets, Terms. Controls how hub content flows into outputs.
- **Output lifecycle**: `_Templates/` define format, `_Output/` holds work-in-progress, `_Archive/` stores completed outputs with metadata.

### Command-per-Workflow Pattern

Each user workflow maps to one command. A command orchestrates one complete user-facing operation.

- `/new` — Initialize a new output instance from master content
- `/draft` — Generate or revise a draft using voice + style + context
- `/review` — Evaluate a draft against the scoring rubric
- `/export` — Format a reviewed draft for delivery

These are examples. The builder defines their own command inventory during `/aod.spec` based on their domain workflows. The pattern is: one command = one workflow = one user intent.

NEVER create commands that map to technical operations (e.g., `/load-context`, `/validate-yaml`). Technical operations are internal to command implementations.

### Agent-to-Command Mapping

Each command may invoke one or more agent personas. Agents are domain specialists with focused expertise:

- A **drafting agent** knows voice, style, and content architecture
- A **review agent** knows the scoring rubric and quality dimensions
- A **export agent** knows output format requirements and delivery standards

The builder designs agent personas during `/aod.spec` and builds them during `/aod.build`. Agent persona files live in `.claude/agents/` of the knowledge system project.

### Context Loading Strategy

Context loading determines which content loads for each workflow phase. The lazy-load pattern achieves significant token savings by loading only what each phase needs.

**Configuration**: `_Config/ContextLoading.yaml` defines three tiers:
- `always_load`: VoiceProfile + StyleGuide (loaded every invocation)
- `on_demand`: Phase-specific content keyed by workflow (analyze, draft, review, export)
- `token_budget`: Maximum tokens per invocation

**Implementation**: The builder implements context loading logic in their command files. ContextLoading.yaml is the configuration contract — it declares intent, not executable logic.

---

## File Structure

```
{project-root}/
.claude/                          # Orchestration layer — build-time product
  commands/                       # Domain commands (one per workflow)
    README.md                     # Guide: command-per-workflow pattern
  agents/                         # Domain agent personas
    README.md                     # Guide: agent persona design
  skills/                         # Reusable multi-step operations
    README.md                     # Guide: skill creation pattern
_Global/                          # Content hub — source of truth (never modify per-output)
  VoiceProfile.md                 # Perspective, tone, sentence patterns
  StyleGuide.md                   # Structure rules, formatting standards
  MasterContent/                  # Core reusable content (domain-specific)
    README.md                     # Guide: content-as-data principle
  Narratives/                     # Atomic story fragments for embedding
    README.md                     # Guide: one file per narrative
_Config/                          # Workflow configuration
  ProjectMeta.yaml                # Project name, status, content tracking
  ContextLoading.yaml             # Lazy-load pattern (always, on-demand, budget)
  ScoringRubric.md                # Quality dimensions and passing threshold
  Presets/                        # Audience, format, and role presets
    README.md                     # Guide: one file per preset
  Terms/                          # Domain terminology (atomic, one file per term)
    README.md                     # Guide: lazy-loading terminology
_Templates/                       # Output format definitions (one subfolder per format)
  README.md                       # Guide: template-per-format pattern
_Output/                          # Active output instances (work-in-progress)
_Archive/                         # Completed outputs with metadata
```

**Orchestration layer** (`.claude/`): Commands, agents, and skills that the builder designs and constructs using the AOD lifecycle. These ARE the product.

**Content architecture** (`_Global/`, `_Config/`, `_Templates/`, `_Output/`, `_Archive/`): Domain content managed by the orchestration. The hub (`_Global/`) is immutable per-output; configuration (`_Config/`) controls behavior; templates define format; output directories manage lifecycle.

---

## Naming Conventions

| Category | Convention | Example |
|----------|-----------|---------|
| Content directories | PascalCase with underscore prefix | `_Global/`, `_Config/`, `_Templates/` |
| Content subdirectories | PascalCase | `MasterContent/`, `Narratives/`, `Presets/` |
| Template files | PascalCase `.md` or `.yaml` | `VoiceProfile.md`, `ContextLoading.yaml` |
| Command files | kebab-case `.md` | `draft-resume.md`, `review-chapter.md` |
| Agent persona files | kebab-case `.md` | `resume-drafter.md`, `chapter-reviewer.md` |
| Skill directories | kebab-case | `score-output/`, `load-context/` |
| Narrative files | kebab-case `.md`, descriptive | `leadership-story.md`, `technical-growth.md` |
| Term files | kebab-case `.md`, one per term | `machine-learning.md`, `agile.md` |
| Preset files | kebab-case `.md` | `formal-executive.md`, `casual-blog.md` |
| Output instances | kebab-case with date prefix | `2026-03-01-senior-resume.md` |
| Archive entries | Same as output, moved to `_Archive/` | `_Archive/2026-03-01-senior-resume.md` |
| Configuration files | PascalCase `.yaml` | `ProjectMeta.yaml`, `ContextLoading.yaml` |
| Guide files | `README.md` | One per directory explaining its purpose |

---

## Security Patterns

### PII Detection in Master Content

- ALWAYS audit `_Global/VoiceProfile.md` for personally identifiable information before committing. Voice attributes describe style patterns, NOT personal facts (addresses, phone numbers, social security numbers).
- ALWAYS audit `_Global/MasterContent/` files for embedded PII. Master content should contain reusable professional content, not personal contact details or government identifiers.
- NEVER store real names, addresses, phone numbers, email addresses, or government IDs in VoiceProfile, StyleGuide, or Narratives unless the builder explicitly intends public disclosure.

### Sensitive Content in Narratives

- ALWAYS review `_Global/Narratives/` files for sensitive personal stories, health information, legal matters, or financial details that should not be included in automated output generation.
- ALWAYS mark sensitive narratives with a `sensitivity: high` frontmatter field so that commands can filter them from bulk operations.
- NEVER embed narrative content directly in command files — always reference by file path to maintain audit trail.

### Credential and Secret Scanning

- ALWAYS scan `_Config/Presets/` for API keys, tokens, passwords, or connection strings that may have been pasted into preset files.
- ALWAYS scan `_Config/ContextLoading.yaml` for hardcoded file paths containing user home directories or system paths.
- NEVER store credentials in any content file. If external service integration is needed, use environment variables referenced by path, not by value.

### Content Audit Patterns

- ALWAYS run a PII scan before the first output generation (during `/aod.build` validation phase).
- ALWAYS include PII detection as a quality dimension in `_Config/ScoringRubric.md` when the domain involves personal information.
- NEVER skip security review on `_Global/` content changes — these files propagate to every subsequent output.

---

## Coding Standards

### Content Authoring Rules

**ALWAYS**:
- Treat master content (`_Global/`) as immutable source data. Outputs derive FROM master content; they never modify it.
- Use one file per narrative in `_Global/Narratives/`. Atomic narratives enable selective embedding and lazy loading.
- Use one file per term in `_Config/Terms/`. Atomic terminology enables per-term loading instead of full-glossary loading.
- Use one file per preset in `_Config/Presets/`. Each preset is a self-contained configuration for a specific audience or format.
- Define context loading phases in `_Config/ContextLoading.yaml`. Every command should declare which content it needs, not load everything.
- Keep VoiceProfile and StyleGuide in `_Global/` as always-loaded context. These define the voice contract for all outputs.
- Place output format templates in `_Templates/` with one subfolder per output format.
- Move completed outputs from `_Output/` to `_Archive/` with completion metadata.

**NEVER**:
- Modify master content to fit a specific output. Create a new output instance that selects, combines, and adapts master content through commands.
- Create a single monolithic command that handles all workflows. One command = one workflow = one user intent.
- Load all content on every command invocation. Use ContextLoading.yaml to define phase-specific loading.
- Mix build-time (AOD) and run-time (product) concerns in the same command file. AOD commands build the system; product commands operate it.
- Duplicate content between Narratives and MasterContent. Narratives are story fragments; MasterContent is structured professional content. They serve different purposes.

### Anti-Patterns (Sourced from Production Systems)

**AP-1: Monolithic Command** (Source: PersonalResumeBuilder early design)
A single `/generate` command that analyzed job postings, selected content, drafted the resume, scored it, and formatted for export — all in one invocation. Result: 15,000+ token context per run, inconsistent outputs, impossible to debug which phase failed. Fix: decompose into `/analyze`, `/draft`, `/score`, `/export` — each focused, testable, and independently re-runnable.

**AP-2: Per-Output Master Content Modification** (Source: PersonalResumeBuilder v1)
Editing VoiceProfile.md to match a specific job posting's language before generating a resume. Result: voice drift across outputs, lost original voice baseline, merge conflicts when multiple outputs were in progress. Fix: master content is immutable. Output-specific adaptations happen in the command logic, using presets and context parameters.

**AP-3: Full-Context Loading Every Phase** (Source: PersonalResumeBuilder before ContextLoading.yaml)
Every command loaded VoiceProfile + StyleGuide + all Narratives + all Terms + ScoringRubric regardless of whether the command needed them. Result: 70% wasted tokens, slower responses, hitting context limits on complex domains. Fix: ContextLoading.yaml with `always_load` (voice, style) and `on_demand` (phase-specific content).

**AP-4: Build-Time/Run-Time Conflation** (Source: AOD Knowledge Collection early iteration)
Using `/aod.build` to generate chapter drafts (run-time output) instead of using it to build the commands and agents that generate chapters. Result: no reusable orchestration, every output required re-running the AOD lifecycle, no quality framework for systematic evaluation. Fix: `/aod.build` builds the orchestration. Product commands (built during `/aod.build`) generate outputs.

### AOD Stage Conventions for Knowledge Systems

When building a knowledge system through the AOD lifecycle, each stage has domain-specific focus:

| AOD Stage | Knowledge System Focus |
|-----------|----------------------|
| `/aod.define` | Define command inventory, target audience, content domains, output types |
| `/aod.spec` | Specify each command's behavior, agent personas, content architecture schema, quality dimensions |
| `/aod.project-plan` | Plan orchestration architecture: command flow, agent mapping, context loading design, content migration |
| `/aod.tasks` | Break down into buildable tasks: command files, agent personas, content templates, rubric dimensions |
| `/aod.build` | Author commands, build agent personas, populate content templates, configure context loading, define quality rubric |
| `/aod.deliver` | Validate end-to-end: run each command, verify output quality against rubric, confirm voice consistency |

---

## Testing Conventions

### What Testing Means for Knowledge Systems

Knowledge systems are not traditional software. Testing is NOT unit testing code — it is end-to-end orchestration validation. The question is: "Does the orchestration produce outputs that meet the quality rubric?"

### Validation Approach

**Command validation**: Run each command in sequence (`/new` → `/draft` → `/review` → `/export`) and verify:
- The command completes without errors
- The output reflects the correct voice (VoiceProfile compliance)
- The output follows style rules (StyleGuide compliance)
- The output incorporates relevant master content and narratives
- Context loading respects ContextLoading.yaml phases (no unnecessary content loaded)

**Rubric-based scoring**: After generating an output, evaluate against `_Config/ScoringRubric.md`:
- Each quality dimension receives a score (e.g., 1-5 scale)
- The output passes if the aggregate score meets the configured threshold
- Failed dimensions identify specific improvement areas

**Cross-output consistency**: Generate 2-3 outputs for different targets and verify:
- Voice remains consistent across outputs (same perspective, tone, patterns)
- Master content is reused correctly (not modified, properly adapted)
- Different presets produce appropriately differentiated outputs

### What to Validate at Each Stage

| Stage | Validation |
|-------|------------|
| After scaffold | Directory structure complete, templates contain guidance, ContextLoading.yaml pre-filled |
| After content population | VoiceProfile has all sections filled, MasterContent organized, Terms atomic |
| After command authoring | Each command runs independently, context loading respects phases |
| After full build | End-to-end: `/new` → `/draft` → `/review` → `/export` produces quality output |
| Before delivery | Rubric scores meet threshold, voice consistent, no PII in outputs |

### Quality Rubric Usage

The ScoringRubric in `_Config/ScoringRubric.md` is the quality contract for the knowledge system. Builders define domain-specific quality dimensions during `/aod.build`:

- **Dimension definition**: Name, description, scoring criteria per level (1-5)
- **Passing threshold**: Minimum aggregate score for an output to be considered production-ready
- **Automatic evaluation**: Review commands score outputs against the rubric systematically
- **Continuous improvement**: Track scores over time to identify weakening dimensions
