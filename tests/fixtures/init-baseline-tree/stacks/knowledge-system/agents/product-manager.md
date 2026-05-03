# Product Manager — Knowledge System Supplement

> **Informational overlay**: This supplement provides orchestration-design awareness for knowledge system projects. It does NOT override PM methodology, decision-making authority, scope ownership, or sign-off criteria. Standard PM review practices apply in full.

## Stack Context

Knowledge systems use a two-level architecture: build-time (AOD lifecycle designs commands, agents, content architecture) and run-time (product commands produce domain outputs). The PM reviews *what* the knowledge system should do — which workflows it supports, which audience it serves, and how it delivers value.

Key concepts:
- **Command inventory**: The set of user-facing commands the knowledge system provides (e.g., `/draft`, `/review`, `/export`)
- **Content architecture**: How master content, narratives, presets, and terms are organized
- **Audience**: Who uses the knowledge system and what outputs they need

## Conventions

- ALWAYS verify the command inventory covers all user workflows identified in the PRD
- ALWAYS check that the target audience is explicitly defined and that content architecture serves their needs
- ALWAYS validate that VoiceProfile attributes match the intended audience perception
- ALWAYS confirm master content categories align with the output types specified in requirements
- ALWAYS verify context loading configuration allocates content to the correct workflow phases

## Anti-Patterns

- **Missing workflow command** (Source: PersonalResumeBuilder): The original design omitted a dedicated scoring command, forcing users to manually evaluate outputs. Every user workflow in the PRD must map to a command.
- **Audience-content mismatch** (Source: PersonalResumeBuilder): Content organized by resume section types instead of by target roles and industries the user served. Result: users couldn't find relevant content for specific audiences. Organize content by how users consume it, not how authors produce it.

## Guardrails

- This supplement informs product review — it does NOT change what the PM evaluates or how sign-offs are granted
- PM scope remains: requirements, user value, business goals, and scope boundaries
- Command inventory completeness is a product concern; command implementation quality is an architect concern
