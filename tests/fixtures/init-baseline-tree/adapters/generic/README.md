# Generic Adapter

Self-contained prompt files for running tachi's STRIDE + AI threat analysis with **any LLM** -- Claude, GPT, Gemini, Llama, or any model that accepts text prompts. No specific platform, IDE, or tooling required.

---

## Prerequisites

- Access to any LLM that accepts text prompts (chat UI or API)
- Your system's architecture description (diagram, text, or both)

No API keys, CLI tools, or platform accounts are needed beyond the LLM itself.

---

## Usage Mode 1 -- Sequential Chat UI

Copy-paste prompts into your LLM conversation in numbered order.

### Steps

1. **Start a new conversation** with your LLM.

2. **Paste `prompts/00-orchestrator.md`** into the conversation. Replace the `{{ARCHITECTURE_INPUT}}` placeholder with your system's architecture description:
   ```
   <architecture-input>
   My system has a React frontend, a Node.js API server,
   a PostgreSQL database, and an OpenAI LLM integration
   for document summarization...
   </architecture-input>
   ```

3. **Collect the orchestrator output.** It will complete Phase 1 (Scope) and Phase 2 (dispatch planning), identifying which components to analyze.

4. **Paste each threat agent prompt sequentially** (`01` through `11`), providing the architecture context and target components from Phase 2 as input to each:
   - `01-spoofing.md` through `06-privilege-escalation.md` (STRIDE agents)
   - `07-prompt-injection.md` through `11-tool-abuse.md` (AI agents)
   - Collect findings from each agent before moving to the next.

5. **Return to the orchestrator context** for Phase 3 (Countermeasures), Phase 4 (Assessment) -- this assembles all findings into the final `threats.md`.

6. **Paste `prompts/12-threat-report.md`** with the `threats.md` output to generate a narrative threat report with attack trees.

7. **Paste `prompts/13-threat-infographic.md`** with the `threats.md` output to generate a visual risk infographic specification.

### Tips

- If your LLM has a short context window, start a fresh conversation for each threat agent and carry findings forward manually.
- Each threat agent prompt is self-contained -- it includes its own "How to Use" header explaining required input and expected output.

---

## Usage Mode 2 -- Programmatic API

Send prompt files to any LLM API endpoint. Run prompts sequentially and pass context between steps.

### Example: curl

```bash
curl -X POST YOUR_LLM_API_ENDPOINT \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LLM_API_KEY" \
  -d @- <<EOF
{
  "prompt": "$(cat prompts/00-orchestrator.md)\n\n<architecture-input>\nYour architecture here\n</architecture-input>",
  "max_tokens": 4096
}
EOF
```

### Example: Python

```python
import httpx
from pathlib import Path

def run_prompt(prompt_file: str, context: str) -> str:
    with open(prompt_file) as f:
        prompt = f.read()
    # Replace with your LLM API endpoint and auth
    response = httpx.post("YOUR_LLM_API_ENDPOINT", json={
        "prompt": prompt + "\n\n" + context,
        "max_tokens": 4096
    })
    return response.json()["completion"]

# Step 1: Run orchestrator with architecture input
architecture = Path("my-architecture.md").read_text()
orchestrator_output = run_prompt("prompts/00-orchestrator.md", architecture)

# Step 2: Run each threat agent with orchestrator context
agents = [f"prompts/{i:02d}-{name}.md" for i, name in enumerate([
    "", "spoofing", "tampering", "repudiation",
    "info-disclosure", "denial-of-service", "privilege-escalation",
    "prompt-injection", "data-poisoning", "model-theft",
    "agent-autonomy", "tool-abuse"
], start=0) if i > 0]

findings = []
for agent in agents:
    result = run_prompt(agent, orchestrator_output)
    findings.append(result)

# Step 3: Assemble findings back into orchestrator for final output
# Pass all findings to the orchestrator context for Phases 3-4
threats_md = run_prompt("prompts/00-orchestrator.md",
    orchestrator_output + "\n\n" + "\n\n".join(findings))

# Step 4: Generate report and infographic from threats.md
report = run_prompt("prompts/12-threat-report.md", threats_md)
infographic_spec = run_prompt("prompts/13-threat-infographic.md", threats_md)
```

**Note**: Adapt the endpoint URL, authentication, and response parsing to match your LLM provider. The pattern above is vendor-neutral -- it works with any API that accepts a prompt and returns a completion.

---

## What's Included

The `prompts/` directory contains 14 self-contained prompt files:

| File | Agent | Description |
|------|-------|-------------|
| `00-orchestrator.md` | Orchestrator | Central coordinator -- scopes the analysis, plans dispatch, assembles final `threats.md` |
| `01-spoofing.md` | STRIDE: Spoofing | Detects identity impersonation threats |
| `02-tampering.md` | STRIDE: Tampering | Detects unauthorized data or code modification threats |
| `03-repudiation.md` | STRIDE: Repudiation | Detects threats to audit trail integrity |
| `04-info-disclosure.md` | STRIDE: Information Disclosure | Detects unauthorized data exposure threats |
| `05-denial-of-service.md` | STRIDE: Denial of Service | Detects availability and resource exhaustion threats |
| `06-privilege-escalation.md` | STRIDE: Elevation of Privilege | Detects unauthorized access escalation threats |
| `07-prompt-injection.md` | AI: Prompt Injection | Detects prompt manipulation threats against LLM components |
| `08-data-poisoning.md` | AI: Data Poisoning | Detects training and fine-tuning data corruption threats |
| `09-model-theft.md` | AI: Model Theft | Detects model extraction and intellectual property theft threats |
| `10-agent-autonomy.md` | AI: Agent Autonomy | Detects excessive autonomous action threats in AI agents |
| `11-tool-abuse.md` | AI: Tool Abuse | Detects misuse of tools and integrations by AI agents |
| `12-threat-report.md` | Threat Report | Generates narrative report with attack trees and remediation roadmap |
| `13-threat-infographic.md` | Threat Infographic | Generates visual risk infographic specification |

---

## Output

The final output is a **`threats.md`** file containing:

- **Section 1**: System overview with components and data flows
- **Section 2**: DFD element classification and trust boundaries
- **Section 3**: STRIDE findings tables (6 categories)
- **Section 4**: AI threat findings tables (5 categories)
- **Section 4a**: Correlated findings across threat categories
- **Section 5**: Coverage matrix (component x threat category)
- **Section 6**: Risk summary with aggregate severity counts
- **Section 7**: Recommended actions prioritized by risk level

The report prompt (`12-threat-report.md`) produces a supplementary **`threat-report.md`** with executive summary, Mermaid attack trees, and a remediation roadmap. The infographic prompt (`13-threat-infographic.md`) produces a **`threat-infographic-spec.md`** visual risk specification.

---

## VERSION File

The `VERSION` file records which tachi source commit generated these prompt files, along with SHA-256 checksums for each prompt. Use it to detect drift between the adapter prompts and the core agent definitions. If the source version does not match your tachi checkout, regenerate the adapter with `scripts/generate-adapter-version.sh`.
