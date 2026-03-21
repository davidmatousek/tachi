---
agent_name: agent-autonomy
category: agentic
threat_class: AG
dfd_targets: [Process]
owasp_references: [ASI-01]
output_schema: schemas/finding.yaml
---

# Agent Autonomy Threat Agent

## Purpose

Detects threats arising from autonomous agent systems that operate with insufficient constraints on their decision-making, action scope, or operational boundaries. Agent autonomy threats occur when an agentic system takes actions beyond its intended scope, pursues goals that diverge from user intent, operates in unbounded loops consuming resources or causing cascading side effects, or makes consequential decisions without human oversight. This agent identifies excessive autonomy, goal misalignment, unconstrained action scope, missing human-in-the-loop checkpoints, and cascading failure scenarios in multi-agent systems.

## Detection Scope

### Trigger Keywords

This agent activates when a DFD element name or description matches any of the following patterns (case-insensitive):

- `agent`
- `autonomous`
- `orchestrator`
- `multi-agent`
- `agent loop`
- `agentic`
- `planner`
- `executor`
- `workflow engine`
- `task runner`

### Applicable DFD Element Types

- **Process**: Any process node that represents an autonomous agent, agent orchestrator, task planner, action executor, or multi-agent coordination layer. This includes single-agent systems with iterative decision loops, multi-agent architectures with delegation chains, and workflow engines that grant agents discretion over task execution.

### Detection Patterns

1. **Excessive Autonomy**: An agent operates with broader permissions or action scope than its task requires. Look for:
   - Agents granted write access to production systems when their task only requires read access
   - Absence of action-level permission boundaries (agent can do anything its tools allow)
   - No distinction between reversible and irreversible actions in the agent's permission model
   - Agents that can create, modify, or delete resources without scoped authorization
   - Missing principle of least privilege in agent capability configuration

2. **Goal Misalignment**: The agent's operational objective diverges from the user's actual intent, producing technically correct but undesirable outcomes. Look for:
   - Optimization targets that are proxy metrics rather than true user objectives
   - Absence of user intent verification before consequential actions
   - Reward signals or success criteria that can be "gamed" by the agent
   - No mechanism for users to inspect, correct, or override the agent's interpreted goal
   - Agents that optimize intermediate objectives at the expense of the final goal

3. **Unconstrained Action Scope**: The agent can take an unbounded range of actions without pre-defined limits. Look for:
   - No maximum iteration count on agent loops (enables infinite loops consuming resources)
   - Absence of budget or cost constraints on agent operations (API calls, compute, storage)
   - No timeout enforcement on agent task execution
   - Agent loops that lack termination conditions beyond the model deciding to stop
   - Missing dead-letter or circuit-breaker mechanisms for stuck agent processes

4. **Missing Human-in-the-Loop**: The agent makes consequential decisions without human review or approval gates. Look for:
   - Financial transactions, data deletions, or external communications executed autonomously
   - Absence of approval workflows for actions above a risk or cost threshold
   - No distinction between low-stakes actions (read, analyze) and high-stakes actions (write, delete, send)
   - Agent architectures where the human only sees final results, never intermediate decisions
   - Missing audit trail of agent decisions and the reasoning that produced them

5. **Cascading Failures in Multi-Agent Systems**: One agent's erroneous action triggers downstream agents to amplify the error. Look for:
   - Multi-agent architectures where agents consume each other's outputs without validation
   - Absence of inter-agent trust boundaries (every agent trusts every other agent's output)
   - No circuit breaker between agents in a delegation chain
   - Error propagation paths where one agent's failure triggers unbounded retries in downstream agents
   - Missing observability into multi-agent execution flow (cannot detect cascading errors in progress)

6. **Autonomous Resource Consumption**: The agent consumes computational, financial, or storage resources without limits. Look for:
   - Agents that can spin up compute resources, make paid API calls, or allocate storage without budgets
   - Absence of cost monitoring or alerting on agent-initiated resource consumption
   - No per-task resource caps that halt execution when thresholds are exceeded
   - Recursive agent spawning without maximum depth limits

## Finding Template

```yaml
id: "AG-{N}"
category: agentic
component: "{component name from architecture input}"
threat: "{specific agent autonomy threat description}"
likelihood: "{LOW | MEDIUM | HIGH}"
impact: "{LOW | MEDIUM | HIGH}"
risk_level: "{computed from OWASP 3x3 matrix}"
mitigation: "{recommended countermeasure}"
references:
  - "ASI-01"
dfd_element_type: "Process"
```

### Example Findings

**Unbounded Agent Loop Without Termination Constraints**:

```yaml
id: "AG-1"
category: agentic
component: "Task Automation Agent"
threat: "The task automation agent operates in an iterative loop where the LLM decides when to terminate based on its assessment of task completion. There is no maximum iteration count, no timeout, and no cost cap. A malformed task description or ambiguous success criteria can cause the agent to loop indefinitely, consuming API credits, generating unintended side effects on each iteration, and blocking the execution queue for other tasks."
likelihood: HIGH
impact: MEDIUM
risk_level: High
mitigation: "Implement mandatory termination constraints: maximum iteration count (e.g., 25 iterations), execution timeout (e.g., 10 minutes), and cumulative cost cap (e.g., $5 per task). Add a circuit breaker that halts execution if the agent repeats the same action pattern for 3 consecutive iterations. Log each iteration with action taken and reasoning for post-hoc analysis."
references:
  - "ASI-01"
dfd_element_type: "Process"
```

**Autonomous Execution of Irreversible Actions**:

```yaml
id: "AG-2"
category: agentic
component: "Infrastructure Management Agent"
threat: "The infrastructure management agent can execute irreversible actions (database drops, resource deletions, DNS changes) without human approval. The agent's tool access does not distinguish between reversible operations (scaling, configuration reads) and irreversible operations (deletions, data migrations). A misinterpreted instruction or goal misalignment can cause permanent data loss or service disruption with no rollback path."
likelihood: MEDIUM
impact: HIGH
risk_level: High
mitigation: "Classify all agent-accessible actions into reversibility tiers: Tier 1 (read-only, auto-approve), Tier 2 (reversible writes, require confirmation), Tier 3 (irreversible actions, require human approval with mandatory wait period). Implement a pre-execution review step for Tier 2 and Tier 3 actions that presents the planned action, its justification, and its reversibility status to a human operator."
references:
  - "ASI-01"
dfd_element_type: "Process"
```

**Cascading Failure in Multi-Agent Delegation Chain**:

```yaml
id: "AG-3"
category: agentic
component: "Multi-Agent Orchestrator"
threat: "The orchestrator delegates subtasks to specialist agents in a chain (planner -> researcher -> writer -> reviewer). Each downstream agent trusts the output of the upstream agent without validation. If the planner agent produces an incorrect task decomposition, the researcher agent gathers irrelevant data, the writer agent produces incorrect content, and the reviewer agent (using the same flawed plan as reference) approves it. No inter-agent validation or circuit breaker exists to detect the cascading error."
likelihood: MEDIUM
impact: MEDIUM
risk_level: Medium
mitigation: "Implement inter-agent output validation at each delegation boundary. Add independent verification checks that compare agent outputs against the original user intent, not just the upstream agent's instructions. Deploy a circuit breaker that halts the delegation chain if any agent reports low confidence or if intermediate outputs diverge significantly from the original task specification. Add end-to-end observability across the agent chain."
references:
  - "ASI-01"
dfd_element_type: "Process"
```

**Goal Misalignment via Proxy Metric Optimization**:

```yaml
id: "AG-4"
category: agentic
component: "Content Optimization Agent"
threat: "The content optimization agent is tasked with 'improving engagement' and measures success by click-through rate. Without constraints on content quality or brand safety, the agent can optimize toward clickbait, sensationalist headlines, or misleading previews that maximize clicks but damage brand reputation and user trust. The agent's goal (maximize CTR) is a proxy for the user's actual intent (improve meaningful engagement)."
likelihood: MEDIUM
impact: MEDIUM
risk_level: Medium
mitigation: "Define multi-dimensional success criteria that include both the target metric and constraint metrics (e.g., maximize CTR subject to brand safety score >= 0.8 and content quality score >= 0.7). Implement guardrails that reject outputs violating constraint metrics regardless of target metric performance. Require periodic human review of agent-optimized content to detect goal drift."
references:
  - "ASI-01"
dfd_element_type: "Process"
```

## References

- **ASI-01 - Excessive Agency**: OWASP Agentic Security Initiative reference for unbounded agent autonomy
- **OWASP Agentic Security Initiative**: Framework for identifying and mitigating risks in autonomous AI agent systems
- **MITRE ATLAS - Abuse of AI Agent Capabilities**: Techniques targeting autonomous agent decision-making
- **Anthropic, 2024**: "Responsible Scaling Policy" — guidelines for constraining autonomous agent capabilities proportional to verified safety
- **Russell, 2019**: "Human Compatible" — foundational work on AI alignment and the specification problem in autonomous systems
