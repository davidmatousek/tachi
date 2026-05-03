# Architect — Knowledge System Supplement

> **Informational overlay**: This supplement provides orchestration-design awareness for knowledge system projects. It does NOT override Architect methodology, technical decision authority, architecture ownership, or sign-off criteria. Standard architecture review practices apply in full.

## Stack Context

Knowledge systems use a two-level architecture: build-time (AOD lifecycle) and run-time (product commands). The Architect reviews *how* the orchestration is designed — command flow, agent-to-command mapping, content architecture soundness, and context loading efficiency.

Key architecture concepts:
- **Hub-and-spoke content model**: `_Global/` is the immutable hub; `_Config/` provides spoke configuration; outputs derive from hub content
- **Command-per-workflow pattern**: One command = one user workflow = one user intent
- **Lazy context loading**: `ContextLoading.yaml` declares per-phase content needs; commands load only what they require
- **Build-time/run-time separation**: AOD commands build the system; product commands operate it

## Conventions

- ALWAYS verify hub-and-spoke integrity — `_Global/` content is never modified per-output
- ALWAYS check command-to-agent mapping — each command declares which agents it invokes and why
- ALWAYS validate context loading design — commands should not load full context when phase-specific loading suffices
- ALWAYS confirm build-time/run-time separation — no AOD commands used as product commands, no product commands duplicating AOD functions
- ALWAYS verify the scaffold file structure matches the canonical layout defined in STACK.md

## Anti-Patterns

- **Monolithic command** (Source: PersonalResumeBuilder early design): A single `/generate` command handling analysis, drafting, scoring, and export in one invocation. Result: 15,000+ token context, inconsistent outputs, impossible to debug. Decompose into focused, independently runnable commands.
- **Build-time/run-time conflation** (Source: AOD Knowledge Collection early iteration): Using `/aod.build` to generate chapter drafts instead of building the commands and agents that generate chapters. No reusable orchestration resulted.
- **Eager context loading** (Source: PersonalResumeBuilder before ContextLoading.yaml): Every command loaded all content regardless of need. 70% wasted tokens. Use lazy-load pattern.

## Guardrails

- This supplement informs architecture review — it does NOT change what the Architect evaluates or how sign-offs are granted
- Architect scope remains: technical approach, infrastructure decisions, architecture soundness
- Orchestration architecture is an Architect concern; command inventory completeness is a PM concern
