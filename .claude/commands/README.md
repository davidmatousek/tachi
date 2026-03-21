# Commands — Knowledge System Orchestration

## Pattern: Command-per-Workflow

Each user workflow maps to one command. A command orchestrates one complete user-facing operation — it is the unit of user intent.

**Rule**: One command = one workflow = one user intent.

## How to Design Commands

1. **List your workflows** — What does a user do with your knowledge system? Common workflows include creating new outputs, drafting content, reviewing quality, and exporting for delivery.

2. **One command per workflow** — Each workflow gets its own command file in this directory. Name files in kebab-case (e.g., `draft-resume.md`, `review-chapter.md`).

3. **Define context loading** — Each command declares which content it needs from `_Config/ContextLoading.yaml`. Never load everything; load only what the workflow requires.

4. **Map to agents** — Each command may invoke one or more agent personas from `.claude/agents/`. The command orchestrates; agents execute.

## Example Structure

```
commands/
  new-output.md       # Initialize from master content
  draft.md            # Generate using voice + style + context
  review.md           # Evaluate against scoring rubric
  export.md           # Format for delivery
```

## Anti-Patterns

- **Monolithic command**: A single command that handles analysis, drafting, scoring, and export. Decompose into focused commands instead.
- **Technical-operation commands**: Commands like `/load-context` or `/validate-yaml` expose internals. Technical operations belong inside command implementations, not as user-facing commands.
- **AOD command duplication**: Never create product commands that replicate `/aod.define`, `/aod.spec`, etc. AOD commands build the system; product commands operate it.

## References

- Command-per-workflow pattern: `STACK.md` → Architecture Pattern
- Context loading configuration: `_Config/ContextLoading.yaml`
- Agent persona mapping: `.claude/agents/README.md`
