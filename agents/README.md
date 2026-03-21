# agents/

Core agent prompt definitions for tachi's threat modeling toolkit. Each agent encodes expertise for a specific threat category and produces structured threat findings.

## Subdirectories

### stride/

Classic STRIDE threat agents — one agent per STRIDE category. These cover the established Microsoft threat classification model.

### ai/

AI-specific threat agents extending STRIDE for agentic applications. These address attack surfaces unique to LLM-based systems, tool-use chains, and autonomous agents.

## Shared Files

- `VoiceProfile.md` — Consistent voice and tone for threat descriptions across all agents
- `StyleGuide.md` — Formatting conventions for threat output (severity ratings, evidence format, mitigation structure)
- `Narratives/` — Reusable attack scenario fragments agents embed into findings
- `MasterContent/` — Structured reference material (CWE mappings, OWASP references, common mitigations)

## Agent File Format

Each agent is a markdown file with frontmatter metadata:

```yaml
---
category: stride | ai
threat_class: "Spoofing"
mitre_mapping: ["T1078", "T1556"]
---
```

The agent body contains the prompt definition, detection heuristics, and output format instructions.
