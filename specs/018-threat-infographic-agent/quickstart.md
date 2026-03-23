# Quickstart: Threat Infographic Agent (F-018)

## Prerequisites

- Completed threat model: `threats.md` produced by the orchestrator (Phases 1–4)
- Optional: `GEMINI_API_KEY` environment variable for image generation

## Usage

### Via Orchestrator (recommended)

The infographic agent runs automatically as Phase 6 after Phase 5 (Report):

```
# Run full pipeline — Phase 6 included by default
orchestrator analyze <architecture-input>

# Skip infographic generation
orchestrator analyze --skip-infographic <architecture-input>

# Or via environment variable
TACHI_SKIP_INFOGRAPHIC=true orchestrator analyze <architecture-input>
```

### Standalone (manual invocation)

Invoke the infographic agent by providing `threats.md` as the sole input in a fresh context. The agent is a markdown prompt file — pass it to your LLM runtime with `threats.md` as context:

```
# Pseudo-syntax: provide threats.md as the agent's sole input
agent run agents/threat-infographic.md --input <path-to-threats.md>
```

## Output Files

| File | When Produced | Description |
|------|--------------|-------------|
| `threat-infographic-spec.md` | Always (when Phase 6 runs) | Structured infographic specification with 6 sections |
| `threat-infographic.jpg` | Only when `GEMINI_API_KEY` is set and API succeeds | Presentation-ready 16:9 landscape image |

## Configuration

| Setting | Default | Options |
|---------|---------|---------|
| Phase 6 enabled | `true` | `--skip-infographic` flag or `TACHI_SKIP_INFOGRAPHIC=true` |
| Gemini model | `gemini-3-pro-image-preview` | Configurable in `schemas/infographic.yaml` |
| Image resolution | 2K | Defined in schema |
| Aspect ratio | 16:9 landscape | Defined in schema |
| Heat map max rows | 8 | Components beyond 8 aggregated as "Other" |

## Gemini API Setup

1. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/)
2. Set the environment variable:
   ```
   export GEMINI_API_KEY=your-key-here
   ```
3. Run the pipeline — image generation is automatic when the key is present

## Troubleshooting

| Symptom | Cause | Resolution |
|---------|-------|------------|
| No `threat-infographic.jpg` | `GEMINI_API_KEY` not set | Set the environment variable; spec is still generated |
| API rate limit error in logs | Gemini API quota exceeded | Wait and retry; spec is saved regardless |
| Content policy rejection | Prompt triggered safety filter | Spec is saved; review Gemini prompt for sensitive terms |
| Empty heat map | No findings in threats.md | Expected behavior for clean threat models |
