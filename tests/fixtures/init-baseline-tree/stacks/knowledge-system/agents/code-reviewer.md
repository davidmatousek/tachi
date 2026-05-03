# Code Reviewer — Knowledge System Supplement

## Stack Context

Knowledge systems produce markdown and YAML files, not compiled code. "Code review" for knowledge systems means reviewing orchestration quality: command consistency, agent persona coherence, content-as-data compliance, context loading efficiency, and naming convention adherence.

Key review surfaces:
- `.claude/commands/` — command files following command-per-workflow pattern
- `.claude/agents/` — agent persona files with focused expertise boundaries
- `_Config/ContextLoading.yaml` — lazy-load configuration with per-phase content allocation
- `_Global/` — master content adherence to immutability principle

## Conventions

- ALWAYS verify each command maps to one user workflow — reject monolithic commands that combine multiple operations
- ALWAYS check agent persona files for focused expertise scope — each agent should know one aspect of the domain
- ALWAYS validate content-as-data compliance — master content (`_Global/`) must never be modified per-output
- ALWAYS verify context loading references match actual file paths — broken references cause silent failures
- ALWAYS check naming convention adherence: PascalCase content directories, kebab-case command and agent files
- ALWAYS verify that commands declare their context loading needs rather than loading everything

## Anti-Patterns

- **Per-output master content modification** (Source: PersonalResumeBuilder v1): VoiceProfile.md was edited to match job posting language before each resume generation. Result: voice drift, lost baseline, merge conflicts. Master content is immutable; adaptations happen through presets and command parameters.
- **Monolithic command** (Source: PersonalResumeBuilder early design): A single command handling analysis through export. Commands should be focused on one workflow, independently testable and re-runnable.
- **Inconsistent naming** (Source: PersonalResumeBuilder early iteration): Mixed casing in directory names (`MasterContent/` alongside `master-content/`) caused path resolution failures. Content directories use PascalCase; command and agent files use kebab-case.
- **Orphaned context references** (Source: PersonalResumeBuilder): After restructuring content directories, ContextLoading.yaml still referenced old paths, causing silent content omission in outputs. Review loading config whenever file structure changes.

## Guardrails

- Review scope covers orchestration quality, not domain content accuracy — whether the voice is *good* is a product concern, not a code review concern
- Naming convention enforcement applies to new files; do not flag files that predate the convention
- Content-as-data compliance is a hard rule — flag any command that modifies `_Global/` files as a blocking issue
