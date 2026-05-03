# Team Lead — Knowledge System Supplement

> **Informational overlay**: This supplement provides orchestration-design awareness for knowledge system projects. It does NOT override Team Lead methodology, timeline authority, resource allocation decisions, or sign-off criteria. Standard team-lead review practices apply in full.

## Stack Context

Knowledge systems are content-authoring projects — all deliverables are markdown and YAML files, not compiled code. Build scheduling must account for content dependencies: master content before commands, commands before quality rubric validation, scaffold before domain population.

Key scheduling concepts:
- **Content→command dependency**: Master content, voice, and style must be authored before commands that reference them
- **Parallel command development**: Commands targeting different workflows can be built simultaneously
- **Scaffold-first**: Directory structure and templates are created before domain content is populated

## Conventions

- ALWAYS identify the content dependency chain: scaffold → master content → voice/style → commands → rubric → validation
- ALWAYS maximize parallelism for independent commands — commands targeting different workflows have no cross-dependencies
- ALWAYS schedule context loading configuration (`ContextLoading.yaml`) before command authoring — commands reference loading phases
- ALWAYS plan for quality rubric dimensions to be defined before review command implementation
- ALWAYS account for content population time — knowledge systems require domain expertise input that may not parallelize

## Anti-Patterns

- **Out-of-order build sequence** (Source: AOD Knowledge Collection): Building commands before master content was populated, resulting in commands that referenced empty directories and placeholder content. Content must exist before commands can be validated.
- **Sequential command development** (Source: AOD Knowledge Collection): Chapters were built one at a time when different content areas had no cross-dependencies, doubling build duration. Commands for independent workflows can be built in parallel.

## Guardrails

- This supplement informs scheduling review — it does NOT change what the Team Lead evaluates or how sign-offs are granted
- Team Lead scope remains: timeline, resource allocation, agent assignments, feasibility
- Build ordering is a Team Lead concern; orchestration architecture is an Architect concern
