# Agent Directory

<!-- Reference: Feature 003 - Agent Refactoring -->
<!-- Version: 2.0.0 | Created: 2026-01-31 -->

Quick reference for all agents in tachi.

---

## Agent Roster

| Agent | Role | Lines | Primary Use Cases |
|-------|------|-------|-------------------|
| [architect](./architect.md) | System Architect | 269 | Technical design, architecture decisions, technology selection |
| [code-reviewer](./code-reviewer.md) | Code Quality Analyst | 269 | Pull request reviews, code quality assessment, best practices |
| [debugger](./debugger.md) | Root Cause Analyst | 239 | Bug investigation, 5 Whys analysis, error diagnosis |
| [devops](./devops.md) | Infrastructure Engineer | 291 | Deployment, CI/CD, environment management |
| [frontend-developer](./frontend-developer.md) | Frontend Engineer | 243 | UI implementation, component development, client-side code |
| [orchestrator](./orchestrator.md) | Workflow Executor | 255 | Multi-agent coordination, parallel wave execution, progress monitoring |
| [product-manager](./product-manager.md) | Product Owner | 259 | PRD creation, requirements, scope decisions, product vision |
| [security-analyst](./security-analyst.md) | Security Specialist | 277 | Security reviews, vulnerability assessment, compliance |
| [senior-backend-engineer](./senior-backend-engineer.md) | Backend Engineer | 278 | API development, server-side logic, database operations |
| [team-lead](./team-lead.md) | Engineering Lead | 210 | Governance, sign-offs, feasibility, capacity, agent assignments |
| [tester](./tester.md) | QA Engineer | 187 | Test strategy, test cases, BDD scenarios, quality validation |
| [ux-ui-designer](./ux-ui-designer.md) | UX/UI Designer | 245 | UI/UX design, user experience, interface design, wireframes |
| [web-researcher](./web-researcher.md) | Research Specialist | 265 | Web research, documentation lookup, technology investigation |

**Total Agents**: 13 | **Total Lines**: 3,287 | **Average**: 253 lines/agent

---

## Quick Selection Guide

### By Task Type

| When you need to... | Use this agent |
|--------------------|----------------|
| Design system architecture | architect |
| Review code changes | code-reviewer |
| Debug an issue | debugger |
| Deploy or configure infrastructure | devops |
| Build frontend components | frontend-developer |
| Define product requirements | product-manager |
| Assess security risks | security-analyst |
| Implement backend logic | senior-backend-engineer |
| Get governance sign-off | team-lead |
| Execute multi-agent workflow | orchestrator |
| Create test cases | tester |
| Design user interfaces | ux-ui-designer |
| Research external resources | web-researcher |

### By Workflow Stage

| SDLC Stage | Primary Agent | Supporting Agents |
|------------|---------------|-------------------|
| Vision/Requirements | product-manager | ux-ui-designer |
| Architecture | architect | security-analyst |
| Planning | team-lead | architect, product-manager |
| Orchestration | orchestrator | team-lead |
| Implementation | senior-backend-engineer, frontend-developer | code-reviewer |
| Testing | tester | debugger |
| Deployment | devops | security-analyst |

---

## Triad Governance Matrix

The SDLC Triad governs key artifacts. This matrix shows each agent's participation.

### Sign-off Authority

| Agent | spec.md | plan.md | tasks.md | Role |
|-------|---------|---------|----------|------|
| product-manager | **APPROVE** | **APPROVE** | **APPROVE** | What & Why |
| architect | Review | **APPROVE** | **APPROVE** | How |
| team-lead | Inform | Review | **APPROVE** | When & Who |

### Veto Authority

| Agent | Can Veto | Domain |
|-------|----------|--------|
| product-manager | Yes | Product scope, user value, business alignment |
| architect | Yes | Technology choices, system design, technical feasibility |
| team-lead | Yes | Timeline, resource allocation, capacity |
| security-analyst | Advisory | Security-critical decisions (escalates to architect) |

### Governance Participation by Agent

| Agent | Participates In | Authority Level |
|-------|----------------|-----------------|
| architect | plan.md review, technical decisions | Approve/Veto |
| product-manager | spec.md review, PRD creation, scope | Approve/Veto |
| team-lead | tasks.md review, assignments, capacity | Approve/Veto |
| code-reviewer | PR reviews | Approve (code) |
| security-analyst | Security reviews | Advisory |
| tester | Quality validation | Advisory |
| devops | Deployment verification | Execute |
| debugger | None (execution only) | None |
| frontend-developer | None (execution only) | None |
| senior-backend-engineer | None (execution only) | None |
| ux-ui-designer | Design review | Advisory |
| web-researcher | None (execution only) | None |
| orchestrator | Workflow execution | Execute |

---

## Agent Collaboration Patterns

### Standard Feature Flow

```
product-manager (requirements)
        │
        ▼
   architect (design)
        │
        ▼
   team-lead (planning + assignments)
        │
        ▼
   orchestrator (execution)
        │
        ├─────────────────────────────────┐
        ▼                                 ▼
senior-backend-engineer            frontend-developer
        │                                 │
        └─────────────────────────────────┘
                      │
                      ▼
              code-reviewer
                      │
                      ▼
                   tester
                      │
                      ▼
                  devops
```

### Debugging Flow

```
Issue Reported
      │
      ▼
  debugger (5 Whys analysis)
      │
      ├── Backend issue ──► senior-backend-engineer
      ├── Frontend issue ──► frontend-developer
      └── Security issue ──► security-analyst
```

### Research Flow

```
Unknown Technology
       │
       ▼
 web-researcher (investigation)
       │
       ▼
   architect (evaluation)
       │
       ▼
   team-lead (decision)
```

---

## Agent Details Summary

### architect

**Expertise**: System design, API architecture, database design, technology selection

**Key Responsibilities**:
- Technical plan creation and review
- Technology stack decisions
- Architecture documentation
- Technical feasibility assessment

**Triad Role**: Defines HOW (technical approach)

---

### product-manager

**Expertise**: Product strategy, user research, requirements, prioritization

**Key Responsibilities**:
- PRD creation and maintenance
- User story definition
- Scope decisions
- Business alignment validation

**Triad Role**: Defines WHAT & WHY (product vision)

---

### team-lead

**Expertise**: Project planning, resource management, governance, agent coordination

**Key Responsibilities**:
- Tasks.md sign-off
- Agent assignments
- Feasibility validation
- Capacity management

**Triad Role**: Defines WHEN & WHO (execution planning)

---

### orchestrator

**Expertise**: Multi-agent coordination, parallel execution, progress monitoring, wave-based workflows

**Key Responsibilities**:
- Execute agent assignments from team-lead
- Coordinate parallel wave execution
- Monitor progress and detect blockers
- Report completion to team-lead

**Relationship to team-lead**: Receives approved assignments, executes workflows, reports back for sign-off.

---

### Customization

For guidance on customizing agents:
- [Agent Best Practices](./_AGENT_BEST_PRACTICES.md) - Design principles and standards
- Template variable usage for tech stack customization
- Quality checklist for validation

---

**End of Agent Directory**
