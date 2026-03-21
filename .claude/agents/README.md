# Agents — Knowledge System Personas

## Pattern: Domain-Specific Agent Personas

Agent personas are focused specialists that commands invoke to execute domain tasks. Each persona has a clear expertise boundary and knows which content to reference.

## How to Design Agent Personas

1. **Identify expertise boundaries** — Each agent knows one aspect of your domain. A drafting agent knows voice and content; a review agent knows the scoring rubric; an export agent knows output formats.

2. **One file per persona** — Create persona files in this directory using kebab-case (e.g., `resume-drafter.md`, `chapter-reviewer.md`).

3. **Define what the agent knows** — Each persona file specifies:
   - What content the agent reads (VoiceProfile, specific MasterContent, Terms)
   - What quality criteria the agent applies
   - What anti-patterns the agent watches for

4. **Map agents to commands** — Document which commands invoke which agents. A command may use multiple agents; an agent may serve multiple commands.

## Example Structure

```
agents/
  content-drafter.md    # Knows voice, style, master content
  quality-reviewer.md   # Knows scoring rubric, quality dimensions
  format-exporter.md    # Knows output templates, delivery standards
```

## Design Guidelines

- **DO** give each agent a focused expertise scope
- **DO** specify which `_Global/` and `_Config/` files the agent references
- **DO** include domain-specific anti-patterns the agent should flag
- **DO NOT** create a single "do-everything" agent — decompose by expertise
- **DO NOT** duplicate content between persona files — reference shared content by path
- **DO NOT** include AOD governance concerns — those belong to the Triad agents (PM, Architect, Team-Lead)

## References

- Agent-to-command mapping: `STACK.md` → Architecture Pattern
- Voice and style context: `_Global/VoiceProfile.md`, `_Global/StyleGuide.md`
- Quality criteria: `_Config/ScoringRubric.md`
