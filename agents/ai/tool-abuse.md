---
agent_name: tool-abuse
category: agentic
threat_class: AG
dfd_targets: [Process]
owasp_references: [MCP-03]
output_schema: schemas/finding.yaml
---

# Tool-Use Abuse Threat Agent

## Purpose

Detects threats arising from agentic systems that invoke external tools, MCP servers, plugins, or APIs as part of their execution. Tool-use abuse occurs when an agent invokes tools it should not have access to, manipulates tool parameters to achieve unintended effects, or chains tool calls in sequences that escalate privileges beyond the agent's intended scope. This agent identifies unauthorized tool invocation, capability escalation through tool composition, parameter injection in tool calls, and tool chain manipulation where individually safe operations combine to produce dangerous outcomes.

## Detection Scope

### Trigger Keywords

This agent activates when a DFD element name or description matches any of the following patterns (case-insensitive):

- `agent`
- `MCP server`
- `tool server`
- `plugin`
- `tool use`
- `function calling`
- `tool chain`
- `orchestrator`
- `action executor`

### Applicable DFD Element Types

- **Process**: Any process node that represents an agent, orchestrator, or tool execution layer. This includes MCP client processes, plugin hosts, function-calling middleware, and agentic frameworks that dispatch tool invocations based on model output.

### Detection Patterns

1. **Unauthorized Tool Invocation**: An agent accesses tools outside its granted capability set. Look for:
   - Tool registries that do not enforce per-agent capability boundaries
   - MCP servers that expose all tools to all connected clients without scoping
   - Absence of an allowlist or deny-list mechanism for tool access per agent role
   - Dynamic tool discovery where the agent can enumerate and call tools not explicitly granted

2. **Capability Escalation via Tool Composition**: Individually authorized tool calls are chained to achieve an effect the agent should not be capable of. Look for:
   - File-read tool + network-send tool = data exfiltration capability
   - Database-query tool + file-write tool = unauthorized data export
   - Code-execution tool + system-command tool = arbitrary command execution
   - No cross-tool authorization policy that evaluates composite effects

3. **Tool Parameter Injection**: The agent (or an attacker via prompt injection) manipulates tool call parameters to alter tool behavior. Look for:
   - Tool parameters constructed from unvalidated model output
   - SQL fragments, shell commands, or file paths passed as tool arguments without sanitization
   - Absence of parameter schema validation at the tool server level
   - Tool descriptions that are overly permissive about accepted parameter values

4. **Tool Chain Manipulation**: An attacker influences the sequence or selection of tool calls to redirect agent behavior. Look for:
   - Tool selection driven entirely by model reasoning without human-in-the-loop checkpoints
   - Absence of tool call logging or audit trail for post-hoc analysis
   - No maximum tool call depth or iteration limit on agentic loops
   - Tool results that are fed back to the model without integrity verification

5. **Rug Pull / Tool Redefinition**: A tool server modifies its tool definitions after initial registration, altering behavior without the agent or user being aware. Look for:
   - MCP servers that can dynamically update tool schemas after connection
   - No integrity verification or pinning of tool definitions at registration time
   - Absence of change detection for tool description, parameter schema, or behavior

## Finding Template

```yaml
id: "AG-{N}"
category: agentic
component: "{component name from architecture input}"
threat: "{specific tool abuse threat description}"
likelihood: "{LOW | MEDIUM | HIGH}"
impact: "{LOW | MEDIUM | HIGH}"
risk_level: "{computed from OWASP 3x3 matrix}"
mitigation: "{recommended countermeasure}"
references:
  - "MCP-03"
dfd_element_type: "Process"
```

### Example Findings

**Unauthorized Tool Access via Unscoped MCP Server**:

```yaml
id: "AG-1"
category: agentic
component: "Code Assistant Agent"
threat: "The MCP server exposes all registered tools (filesystem, database, network, code execution) to every connected agent without per-agent capability scoping. A code review agent intended only for read operations can invoke file-write and shell-execute tools, enabling unintended modifications to the codebase or host system."
likelihood: HIGH
impact: HIGH
risk_level: Critical
mitigation: "Implement per-agent tool allowlists at the MCP server level. Each agent connection should declare its required capabilities, and the server should enforce that only declared tools are invocable. Log all tool invocations with agent identity for audit purposes."
references:
  - "MCP-03"
dfd_element_type: "Process"
```

**Capability Escalation via Tool Chaining**:

```yaml
id: "AG-2"
category: agentic
component: "Data Analysis Agent"
threat: "The agent has authorized access to a database-query tool and a file-write tool individually. By chaining these tools, the agent can export arbitrary database contents to the local filesystem, then use a file-share tool to transmit the export externally. No cross-tool policy evaluates the composite effect of this chain, enabling data exfiltration that no single tool authorization would permit."
likelihood: MEDIUM
impact: HIGH
risk_level: High
mitigation: "Implement a tool chain policy engine that evaluates composite effects of sequential tool calls. Define forbidden tool combinations (e.g., data-read + network-send) and require human approval for chains that cross trust boundaries. Enforce maximum chain depth limits."
references:
  - "MCP-03"
dfd_element_type: "Process"
```

**Parameter Injection in Tool Calls**:

```yaml
id: "AG-3"
category: agentic
component: "SQL Assistant Agent"
threat: "The agent constructs SQL query parameters from model output without validation. An attacker who achieves prompt injection can manipulate the model to produce tool calls with malicious SQL fragments (DROP TABLE, UNION SELECT) as query parameters, bypassing application-level SQL injection protections because the query originates from a trusted agent process."
likelihood: MEDIUM
impact: HIGH
risk_level: High
mitigation: "Enforce strict parameter schema validation at the tool server level. Use parameterized queries exclusively — never pass raw SQL from model output. Implement an output classifier on the model that detects tool calls with suspicious parameter patterns before execution."
references:
  - "MCP-03"
  - "CWE-89"
dfd_element_type: "Process"
```

## References

- **MCP-03 - Tool Poisoning / Rug Pull**: Model Context Protocol security advisory on tool definition manipulation
- **OWASP Agentic Security Initiative**: Framework for agentic application threat modeling
- **Anthropic, 2024**: "Tool Use Security Considerations" — guidelines for safe tool-use patterns in agentic systems
- **MITRE ATLAS - Abuse of AI Capabilities**: Techniques for exploiting tool-augmented AI systems
