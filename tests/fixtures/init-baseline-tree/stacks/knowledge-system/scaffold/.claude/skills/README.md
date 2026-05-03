# Skills — Reusable Multi-Step Operations

## Pattern: Skill Extraction

Skills encapsulate repeated multi-step operations that multiple commands share. When you notice the same sequence of steps appearing in two or more commands, extract it into a skill.

## When to Create a Skill

- A multi-step operation appears in 2+ commands
- The operation has a clear input and output
- The steps are always performed in the same order
- The operation is complex enough that inline duplication would cause maintenance burden

## How to Create Skills

1. **Identify the repeated operation** — Look for step sequences that commands share (e.g., loading context, scoring against rubric, formatting output).

2. **Create a skill directory** — Use kebab-case naming (e.g., `score-output/`, `load-context/`).

3. **Define the skill contract** — Each skill directory contains a `SKILL.md` that specifies inputs, outputs, and the step sequence.

## Example Structure

```
skills/
  score-output/
    SKILL.md          # Inputs: draft + rubric → Outputs: score report
  load-context/
    SKILL.md          # Inputs: workflow phase → Outputs: loaded content set
```

## Guidelines

- **DO** extract skills only when reuse is proven (2+ commands use the same steps)
- **DO** keep skills focused on one operation
- **DO** document inputs and outputs clearly in SKILL.md
- **DO NOT** create skills preemptively — wait until duplication is observed
- **DO NOT** create skills for single-step operations — those belong inline in commands
- **DO NOT** create skills that duplicate AOD lifecycle skills (e.g., `/aod.analyze`)

## References

- Command-per-workflow pattern: `.claude/commands/README.md`
- Skill file format: AOD Kit documentation
