---
name: tachi-tool-abuse
description: "AI agentic tool-use abuse threat agent — detects threats from agentic systems invoking external tools, MCP servers, plugins, or APIs, including unauthorized tool invocation, capability escalation through tool composition, parameter injection, and tool poisoning attacks."
user-invocable: false
---

## Metadata

```yaml
category: agentic
threat_class: AG
dfd_targets: [Process]
owasp_references: [ASI-02, ASI-04, MCP-03, MCP-05]
output_schema: ../../../schemas/finding.yaml
```

# Tool-Use Abuse Threat Agent

## Purpose

Detects threats arising from agentic systems that invoke external tools, MCP servers, plugins, or APIs as part of their execution. Tool-use abuse occurs when an agent invokes tools it should not have access to, manipulates tool parameters to achieve unintended effects, or chains tool calls in sequences that escalate privileges beyond the agent's intended scope. This agent identifies unauthorized tool invocation, capability escalation through tool composition, parameter injection in tool calls, tool chain manipulation where individually safe operations combine to produce dangerous outcomes, and tool poisoning attacks (direct poisoning, tool shadowing, and rug pulls) where malicious tool definitions alter agent behavior.

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

### Empty Results Guidance

If the architecture input contains **no** components matching the trigger keywords above (no agents, MCP servers, tool servers, plugins, function-calling layers, or tool chains), this agent MUST produce **zero findings**. Do not generate speculative findings about hypothetical tool-use components. An architecture without tool servers, MCP integrations, plugin systems, or agentic tool invocation is outside this agent's detection scope. Return an empty findings list.

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

5. **Tool Poisoning**: A malicious or compromised tool server manipulates tool definitions to alter agent behavior without detection. This category covers three distinct attack vectors:

   **5a. Direct Poisoning**: A tool server provides tool definitions with hidden malicious instructions embedded in descriptions or parameter schemas. Look for:
   - Tool descriptions containing embedded instructions that influence model behavior beyond the tool's stated purpose
   - Hidden directives in parameter descriptions that cause the model to pass sensitive data as arguments
   - Tool definitions where the description payload exceeds what is necessary for functional use
   - Absence of tool description sanitization or length limits at the MCP client level

   **5b. Tool Shadowing**: A malicious tool server registers a tool with the same name or similar description as a legitimate tool, intercepting calls intended for the original. Look for:
   - Multiple MCP servers registering tools with identical or near-identical names
   - No namespace isolation or server-of-origin verification for tool registrations
   - Tool discovery mechanisms that do not disambiguate between tools from different servers
   - Absence of tool identity verification (server signature, hash of tool definition)

   **5c. Rug Pull / Tool Redefinition**: A tool server modifies its tool definitions after initial registration, altering behavior without the agent or user being aware. Look for:
   - MCP servers that can dynamically update tool schemas after connection
   - No integrity verification or pinning of tool definitions at registration time
   - Absence of change detection for tool description, parameter schema, or behavior
   - No versioning or changelog for tool definition updates

## Finding Template

```yaml
id: "AG-{N}"
category: agentic
component: "{component name from architecture input}"
threat: "{specific tool abuse threat description — must describe attacker action and trust assumption violated}"
likelihood: "{LOW | MEDIUM | HIGH}"
impact: "{LOW | MEDIUM | HIGH}"
risk_level: "{computed from OWASP 3x3 matrix}"
mitigation: "{actionable countermeasure with specific technology or configuration}"
references:
  - "{one or more of: ASI-02, ASI-04, MCP-03, MCP-05 — select references relevant to the specific threat}"
dfd_element_type: "Process"
```

### Example Findings

**Unauthorized Tool Access via Unscoped MCP Server**:

```yaml
id: "AG-1"
category: agentic
component: "Code Assistant Agent"
threat: "An attacker exploits the Code Assistant Agent's connection to an MCP server that exposes all registered tools (filesystem, database, network, code execution) to every connected agent without per-agent capability scoping. This violates the trust assumption that agents can only invoke tools within their authorized capability set — a code review agent intended only for read operations can invoke file-write and shell-execute tools, enabling unintended modifications to the codebase or host system."
likelihood: HIGH
impact: HIGH
risk_level: Critical
mitigation: "Implement per-agent tool allowlists at the MCP server level. Each agent connection should declare its required capabilities, and the server should enforce that only declared tools are invocable. Log all tool invocations with agent identity for audit purposes."
references:
  - "ASI-02"
  - "MCP-03"
dfd_element_type: "Process"
```

**Capability Escalation via Tool Chaining**:

```yaml
id: "AG-2"
category: agentic
component: "Data Analysis Agent"
threat: "An attacker manipulates the Data Analysis Agent (via prompt injection or task specification) to chain individually authorized tools — a database-query tool and a file-write tool — to export arbitrary database contents to the local filesystem, then use a file-share tool to transmit the export externally. This violates the trust assumption that individually authorized tools cannot combine to exceed their intended permissions — no cross-tool policy evaluates the composite effect of this chain, enabling data exfiltration that no single tool authorization would permit."
likelihood: MEDIUM
impact: HIGH
risk_level: High
mitigation: "Implement a tool chain policy engine that evaluates composite effects of sequential tool calls. Define forbidden tool combinations (e.g., data-read + network-send) and require human approval for chains that cross trust boundaries. Enforce maximum chain depth limits."
references:
  - "ASI-04"
  - "MCP-03"
dfd_element_type: "Process"
```

**Parameter Injection in Tool Calls**:

```yaml
id: "AG-3"
category: agentic
component: "SQL Assistant Agent"
threat: "An attacker achieves prompt injection against the SQL Assistant Agent and manipulates the model to produce tool calls with malicious SQL fragments (DROP TABLE, UNION SELECT) as query parameters. The agent constructs SQL query parameters from model output without validation. This violates the trust assumption that model-generated tool parameters are safe and well-formed — the query originates from a trusted agent process, bypassing application-level SQL injection protections that only guard against external user input."
likelihood: MEDIUM
impact: HIGH
risk_level: High
mitigation: "Enforce strict parameter schema validation at the tool server level. Use parameterized queries exclusively — never pass raw SQL from model output. Implement an output classifier on the model that detects tool calls with suspicious parameter patterns before execution."
references:
  - "MCP-05"
  - "MCP-03"
  - "CWE-89"
dfd_element_type: "Process"
```

### Risk Level Computation

Apply the OWASP 3x3 matrix to determine `risk_level` from `likelihood` and `impact`:

|  | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

## References

- **ASI-02 - Unauthorized Tool Access**: OWASP Agentic Security Initiative reference for agents invoking tools outside their granted capability set due to absent per-agent scoping or allowlist enforcement
- **ASI-04 - Cross-Agent Trust Exploitation**: OWASP Agentic Security Initiative reference for capability escalation through tool composition where individually authorized operations combine to exceed intended permissions
- **MCP-03 - Tool Poisoning / Rug Pull**: Model Context Protocol security advisory on tool definition manipulation — covers direct poisoning, tool shadowing, and post-registration redefinition attacks
- **MCP-05 - Tool Parameter Injection**: Model Context Protocol security advisory on unvalidated parameters in tool calls — SQL fragments, shell commands, or file paths passed as tool arguments without sanitization
- **OWASP Agentic Security Initiative**: Framework for agentic application threat modeling
- **Anthropic, 2024**: "Tool Use Security Considerations" — guidelines for safe tool-use patterns in agentic systems
- **MITRE ATLAS - Abuse of AI Capabilities**: Techniques for exploiting tool-augmented AI systems
