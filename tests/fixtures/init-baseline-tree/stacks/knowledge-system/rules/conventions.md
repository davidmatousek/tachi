# Knowledge System Conventions

## Architecture

- ALWAYS maintain the two-level architecture: build-time (AOD lifecycle) and run-time (product commands)
- ALWAYS keep `_Global/` as the immutable content hub — outputs derive from it, never modify it
- ALWAYS follow the hub-and-spoke model: `_Global/` (hub) → `_Config/` (configuration) → `_Templates/` (format) → `_Output/` (active) → `_Archive/` (completed)

## Commands

- ALWAYS map one command to one user workflow — one command = one workflow = one user intent
- ALWAYS declare context loading needs in each command — reference `_Config/ContextLoading.yaml` phases
- NEVER create commands for technical operations (e.g., `/load-context`, `/validate-yaml`) — these belong inside command implementations
- NEVER create product commands that duplicate AOD lifecycle commands (`/aod.define`, `/aod.spec`, etc.)
- NEVER use AOD commands as run-time product commands

## Content-as-Data

- ALWAYS treat master content (`_Global/MasterContent/`) as immutable source data
- ALWAYS use one file per narrative in `_Global/Narratives/` — atomic fragments enable selective loading
- ALWAYS use one file per term in `_Config/Terms/` — atomic terms enable lazy loading
- ALWAYS use one file per preset in `_Config/Presets/` — each preset is self-contained
- NEVER modify master content to fit a specific output — create a new output instance that selects and adapts
- NEVER embed narrative content directly in command files — reference by file path
- NEVER duplicate content between `Narratives/` and `MasterContent/` — narratives are stories; master content is structured professional content

## Context Loading

- ALWAYS define context loading phases in `_Config/ContextLoading.yaml`
- ALWAYS load VoiceProfile and StyleGuide on every invocation (`always_load`)
- ALWAYS use on-demand loading for phase-specific content (analyze, draft, review, export)
- NEVER load all content on every command invocation — use lazy-load pattern

## Naming

- ALWAYS use PascalCase with underscore prefix for content directories (`_Global/`, `_Config/`, `_Templates/`)
- ALWAYS use PascalCase for content subdirectories (`MasterContent/`, `Narratives/`, `Presets/`)
- ALWAYS use PascalCase for template and configuration files (`VoiceProfile.md`, `ContextLoading.yaml`)
- ALWAYS use kebab-case for command files, agent persona files, narrative files, term files, and preset files
- ALWAYS use kebab-case with date prefix for output instances (`2026-03-01-senior-resume.md`)

## Output Lifecycle

- ALWAYS place active output instances in `_Output/`
- ALWAYS move completed outputs to `_Archive/` with completion metadata
- ALWAYS use one subfolder per output format in `_Templates/`
