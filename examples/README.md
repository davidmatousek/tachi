# examples/

Example architecture inputs and their corresponding threat model outputs. These serve as reference implementations for users learning the toolkit and as test fixtures for validating agent behavior.

## Structure

Each example is a self-contained directory with input and expected output:

```
examples/
  web-api/
    input.md          # Architecture description (data flow, components, trust boundaries)
    threats.md        # Expected threat findings
  agentic-app/
    input.md          # Architecture with LLM agents, tool use, RAG pipelines
    threats.md        # Expected findings including AI-specific threats
```

## Guidelines

- Keep examples minimal but realistic — enough detail to trigger meaningful findings
- Include at least one example exercising AI-specific threat agents
- Examples use immutable dated directories when versioning is needed (e.g., `web-api-2026-03/`)
