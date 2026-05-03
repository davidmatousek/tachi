<!--
  Template Instructions
  =====================
  This constitution template is part of the Agentic Oriented Development Kit (AOD Kit).

  To customize for your project:
  1. Replace all {{PROJECT_NAME}} with your project name
  2. Replace {{PROJECT_DESCRIPTION}} with your project description
  3. Replace {{TECH_STACK_*}} placeholders with your technology choices
  4. Review and customize System Architecture Constraints section
  5. Update versioning to 1.0.0 when first deploying

  DO NOT modify:
  - Core Principles (I-XI) - These are universal governance rules
  - Triad Collaboration framework - This is the core workflow
  - Amendment Process - This ensures constitution stability
-->

# {{PROJECT_NAME}} Constitution

## Core Principles

### I. General-Purpose Architecture

{{PROJECT_NAME}} MUST be domain-agnostic and work with any agent-based development workflow. The platform SHALL NOT contain security-specific, domain-specific, or use-case-specific logic in core components.

**Rationale**: As a standalone SaaS platform, {{PROJECT_NAME}} must serve diverse projects across industries. Domain-specific features limit adoption and create maintenance burden.

**Requirements**:
- Core API endpoints are use-case neutral (tasks, knowledge, strategy)
- No hardcoded assumptions about project types or domains
- Extensibility through configuration, not code modifications
- Documentation uses generic examples applicable across domains

### II. API-First Design

All functionality MUST be accessible via RESTful API before any UI or MCP interface is implemented. API contracts are the source of truth for system capabilities.

**Rationale**: API-first ensures consistency across interfaces (web UI, MCP, CLI) and enables programmatic integration. This principle prevents UI-driven design that creates backend retrofitting.

**Requirements**:
- OpenAPI/Swagger specification maintained for all endpoints
- API versioning follows semantic versioning (v1, v2, etc.)
- Breaking changes require new API version, not in-place modifications
- MCP tools and web UI are thin clients over the same API layer
- All state mutations go through API (no direct database access from clients)

### III. Backward Compatibility (NON-NEGOTIABLE)

The system MUST maintain 100% backward compatibility with local Triad `.aod/` file workflows. Agents can always fall back to local files if the cloud service is unavailable.

**Rationale**: Forced migrations create adoption barriers and single points of failure. Local-first fallback ensures developers are never blocked by network issues or service outages.

**Requirements**:
- MCP server detects service availability and falls back gracefully
- Local `.aod/` files remain valid and usable without modification
- Migration from local to cloud is opt-in, never forced
- Import/export tools support bidirectional sync
- No data loss when switching between local and cloud modes

### IV. Concurrency & Data Integrity

All state transitions MUST be atomic with ACID guarantees. Task locking prevents race conditions. Lock expiration prevents deadlocks from crashed agents.

**Rationale**: Multi-agent workflows are the core value proposition. Without robust concurrency control, the platform fails its primary purpose.

**Requirements**:
- Optimistic locking with `locked_until` timestamp for tasks
- Lock timeout defaults to 10 minutes, configurable per project
- Database transactions ensure atomicity of state changes
- Clear error messages when lock conflicts occur (include holder identity)
- Audit logging for all state transitions (debugging and compliance)
- No manual locks - all locks managed by system with automatic expiration

### V. Privacy & Data Isolation

Project data MUST be isolated per user/organization with strict access controls. Vector embeddings and knowledge base content are encrypted at rest.

**Rationale**: SaaS platforms handle sensitive intellectual property. Security breaches destroy trust and violate legal compliance requirements.

**Requirements**:
- Row-level security enforced at database layer
- API authentication required for all endpoints (JWT tokens)
- API keys are rotatable and revocable
- Vector embeddings encrypted at rest (AES-256 or equivalent)
- Rate limiting per user (default: 100 requests/minute)
- No cross-project data leakage in search results or API responses
- Audit logs for access and modifications

### VI. Testing Excellence

Testing is MANDATORY for {{PROJECT_NAME}}. All features MUST have corresponding test coverage before being marked as complete.

**Rationale**: As a SaaS platform managing critical development workflows, reliability and correctness are non-negotiable. Comprehensive testing builds user trust and prevents regressions.

**Requirements**:
- **Unit Tests**: Required for all business logic (minimum 80% coverage)
- **Integration Tests**: Required for API endpoints, MCP tools, and database operations
- **End-to-End Tests**: Required for critical user workflows (task claiming, knowledge search, multi-agent coordination)
- **Performance Tests**: Required for concurrency scenarios, vector search, and API response times
- **Test-First Development**: Tests written BEFORE implementation for core features
- **Contract Testing**: Required for all API endpoints and MCP protocol compliance
- **Continuous Testing**: All tests run in CI/CD pipeline; failing tests block merges

**Testing Framework**:
- Test frameworks appropriate to technology stack (Jest, Pytest, Playwright, etc.)
- Test execution documented in project README
- Test results visible in CI/CD pipeline
- Performance benchmarks tracked over time

### VII. Definition of Done (NON-NEGOTIABLE)

Every feature and deliverable MUST complete all validation steps before being marked as "DELIVERED". This is a constitutional mandate that cannot be bypassed.

**Rationale**: Three-step validation ensures production-ready quality, real-world usability, and actual user value delivery. It prevents premature completion declarations and ensures reliable deployments.

**Non-Negotiable Validation Steps**:
1. **✅ Pushed to Production** - Feature deployed and operational in production environment
2. **✅ Tested** - All automated tests pass (unit, integration, E2E, performance)
3. **✅ User Validated** - Real-world usage confirmed working by actual users or stakeholders

**Quality Gates**:
- No feature marked complete until all DoD steps verified
- Test coverage meets minimum thresholds (80% for unit tests)
- User acceptance required for all customer-facing functionality
- Performance requirements met (API <500ms, search <2s)
- Documentation updated and accurate

**Enforcement**:
- See `docs/standards/DEFINITION_OF_DONE.md` for detailed validation procedures
- Features that skip any step MUST be reverted to in-progress status
- DoD checklist required in all PRs for feature work

**Exceptions**:
- Documentation-only changes may not require production deployment
- Architecture/planning phases validated through implementation phases
- Infrastructure changes validated through smoke tests and monitoring

### VIII. Observability & Root Cause Analysis

All complex work and debugging sessions MUST capture learnings and patterns for institutional knowledge. Root cause analysis prevents surface-level fixes.

**Rationale**: Observability ensures rapid issue resolution, captures organizational learning, and prevents repeated mistakes. Root cause analysis addresses underlying problems rather than symptoms.

**Requirements**:
- **Five Whys Methodology**: ALWAYS use Five Whys Root Cause Analysis for complex issues (see `docs/core_principles/01-FIVE_WHYS_METHODOLOGY.md`)
- **Structured Logging**: Required for all critical operations (API requests, task state changes, lock operations, search queries)
- **Health Checks**: Required for all services (API `/health` endpoint, MCP server status, database connectivity)
- **Performance Monitoring**: Track API response times, search latency, concurrent agent metrics
- **Error Tracking**: Comprehensive error handling with automatic retry mechanisms and graceful degradation
- **Audit Logging**: All state transitions logged for debugging and compliance

**Error Handling Standards**:
- Graceful degradation when services unavailable (fallback to local files)
- Clear, actionable error messages for users and agents
- Rate limiting with appropriate backoff strategies
- Automated alerting for system health issues

**Knowledge Capture**:
- Document root cause analyses in project documentation
- Capture patterns and solutions for future reference
- Share learnings across team through PRs and retrospectives

### IX. Git Workflow & Feature Branching (NON-NEGOTIABLE)

ALL development work MUST use feature branches. Direct commits to main branch are STRICTLY PROHIBITED.

**Rationale**: Feature branch workflow prevents accidental main branch corruption, enables code review, maintains development history for debugging and auditing, and supports multi-agent collaboration.

**Non-Negotiable Rules**:
- ALWAYS use feature branches: `git checkout -b NNN-feature-name`
- NEVER commit directly to main branch
- ALWAYS create PR (Pull Request) for review before merge
- Branch naming: `NNN-descriptive-name` (e.g., `001-task-locking-api`)
- NEVER run destructive git commands (force push, hard reset) without explicit user request
- NEVER skip hooks (--no-verify, --no-gpg-sign) without explicit user request

**Commit Standards**:
- Follow conventional commit format: `type(scope): description`
  - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`
  - Scopes: `api`, `mcp`, `database`, `auth`, `ui`, `infra`, `test`
- Include descriptive commit body explaining "why" not "what"
- Reference related issues: `Closes #123` or `Fixes #456`
- Include agent co-authorship: `Co-Authored-By: Agent <agent@{{PROJECT_NAME}}>`
- Run `git status` before and after commits to verify changes

**Pull Request Requirements**:
- Title follows convention: `type(scope): description`
- Description explains objective, changes, testing, and validation
- All automated tests pass (CI/CD pipeline)
- Code review approval required (minimum 1 reviewer)
- Constitution compliance verified
- Security scan passes (no vulnerabilities)
- Documentation updated if applicable

**Branch Protection**:
- Main branch requires PR reviews before merge
- All CI/CD status checks must pass
- Branches must be up to date before merging
- Enforce code review from CODEOWNERS for critical paths

**Reference**: See `docs/standards/GIT_WORKFLOW.md` for detailed git workflow guidance

### X. Product-Spec Alignment & Architecture Review (NON-NEGOTIABLE)

ALL Triad artifacts (spec.md, plan.md, tasks.md) MUST receive dual sign-off before implementation begins:
1. **Product Manager (product-manager)** validates product alignment and user value
2. **Architect** validates technical soundness and architectural consistency

Product artifacts in docs/product/ are the strategic foundation, and project architecture in docs/architecture/ is the technical foundation that specifications must serve.

**Rationale**:
- **Product Alignment**: Technical excellence without product alignment wastes resources building the wrong solution. The Product Manager ensures every feature serves user needs, supports strategic objectives, and delivers measurable value.
- **Architecture Review**: Sound product strategy without technical consistency creates fragmented systems. The Architect ensures every technical decision aligns with project architecture, maintains system integrity, and avoids technical debt.

**Non-Negotiable Requirements**:
- ALWAYS create PRD before spec.md (use `/aod.define`)
- ALWAYS validate spec.md aligns with product vision, OKRs, and user stories
- ALWAYS get PM sign-off on spec.md before creating plan.md
- ALWAYS get Architect review on plan.md for technical decisions and architecture alignment
- ALWAYS get PM sign-off on plan.md before creating tasks.md
- ALWAYS get Architect review on tasks.md for implementation approach
- ALWAYS get PM sign-off on tasks.md before implementation begins
- NEVER implement features without documented product context
- NEVER implement technical designs that violate project architecture

**Product Manager Authority**:

The Product Manager (product-manager) has **VETO AUTHORITY** over:
1. **Spec Creation**: Can reject spec.md that doesn't align with product vision
2. **Plan Approval**: Can reject plan.md that doesn't fit roadmap or user value
3. **Task Prioritization**: Can reorder tasks.md to align with product priorities

**Architect Authority**:

The Architect has **VETO AUTHORITY** over:
1. **Plan Approval**: Can reject plan.md that violates project architecture or creates technical debt
2. **Technical Decisions**: Can require alternative approaches that maintain architectural consistency
3. **Task Implementation**: Can reject tasks.md that uses inappropriate patterns or technologies

**Collaborative Decision-Making**:

When PM and Architect disagree:
- PM has final authority on **WHAT** to build and **WHY** (product decisions)
- Architect has final authority on **HOW** to build it (technical decisions)
- If conflict persists, escalate to project lead with both perspectives documented

**Required Sign-Off Checklist**:

Before implementation, PM validates:

```markdown
## Product Manager Sign-Off

### Vision Alignment
- [ ] Aligns with product vision (docs/product/01_Product_Vision/product-vision.md)
- [ ] Serves target user needs (docs/product/01_Product_Vision/target-users.md)
- [ ] Fits competitive positioning (docs/product/01_Product_Vision/competitive-landscape.md)

### Strategic Alignment
- [ ] Supports current quarter OKRs (docs/product/06_OKRs/)
- [ ] Fits phase roadmap timeline (docs/product/03_Product_Roadmap/)
- [ ] Delivers on user stories (docs/product/05_User_Stories/)

### Quality Standards
- [ ] Problem statement is clear and user-focused
- [ ] Success metrics are measurable
- [ ] Scope is well-defined with clear boundaries
- [ ] Dependencies are identified and documented
- [ ] Technical constraints are realistic

### Documentation Standards
- [ ] spec.md has clear user value proposition
- [ ] plan.md references relevant product docs
- [ ] tasks.md prioritization aligns with product priorities
- [ ] All artifacts reference source PRD

**PM Approval**: [Name] - [Date]
**Status**: [✅ Approved / 🟡 Approved with Comments / ❌ Rejected]
**Comments**: [Any concerns, recommendations, or context]
```

Before implementation, Architect validates (for plan.md and tasks.md):

```markdown
## Architect Review

### Architecture Alignment
- [ ] Aligns with project architecture (docs/architecture/README.md)
- [ ] Follows established patterns and conventions
- [ ] Maintains system boundaries and interfaces
- [ ] Respects architectural constraints

### Technical Soundness
- [ ] Technical approach is feasible and appropriate
- [ ] Technology choices align with project stack
- [ ] No unnecessary complexity or over-engineering
- [ ] Avoids known anti-patterns

### System Integrity
- [ ] Doesn't introduce technical debt
- [ ] Maintains separation of concerns
- [ ] Preserves API contracts and interfaces
- [ ] Considers backward compatibility

### Implementation Approach
- [ ] Tasks use appropriate design patterns
- [ ] Database schema changes are reversible
- [ ] Performance implications considered
- [ ] Security implications addressed

**Architect Approval**: [Name] - [Date]
**Status**: [✅ Approved / 🟡 Approved with Comments / ❌ Rejected]
**Technical Notes**: [Architecture considerations, alternatives considered, trade-offs]
```

**Veto Process**:

When PM exercises veto:

```markdown
## Product Manager Veto - [Date]

**Artifact**: [spec.md / plan.md / tasks.md]
**Reason**: [Clear explanation of misalignment]

### Required Changes:
1. [Specific change needed]
2. [Specific change needed]
3. [Specific change needed]

### Rationale:
[Explain how changes restore product alignment]

### References:
- [Link to product vision / OKRs / roadmap / user stories]

**Resubmit After**: [Changes are made]
```

When Architect exercises veto:

```markdown
## Architect Veto - [Date]

**Artifact**: [plan.md / tasks.md]
**Reason**: [Clear explanation of architectural violation or technical concern]

### Required Changes:
1. [Specific technical change needed]
2. [Specific architectural alignment needed]
3. [Specific pattern or approach to use instead]

### Rationale:
[Explain how changes maintain architectural integrity]

**Architecture Violations**:
- [Violation 1: How approach breaks architecture]
- [Violation 2: Technical debt introduced]
- [Violation 3: System integrity concerns]

### Alternative Approaches:
- **Option A**: [Description, pros/cons]
- **Option B**: [Description, pros/cons]
- **Recommended**: [Which option and why]

### References:
- [Link to project architecture docs]
- [Link to relevant architectural decision records (ADRs)]
- [Link to design patterns or conventions]

**Resubmit After**: [Changes are made]
```

**Product & Architecture Synchronization**:

Product Manager is responsible for maintaining alignment between:

**Product Artifacts** (docs/product/):
- 01_Product_Vision/ - Strategic direction
- 02_PRD/ - Product requirements
- 03_Product_Roadmap/ - Phase planning
- 04_Customer_Journey_Maps/ - User experience flows
- 05_User_Stories/ - Feature user stories
- 06_OKRs/ - Objectives & Key Results

**Architecture Artifacts** (docs/architecture/):
- README.md - Project architecture overview
- 01_system_design/ - System architecture and component diagrams
- 02_ADRs/ - Architectural Decision Records
- 03_patterns/ - Design patterns and conventions

**Triad Artifacts** (.aod/):
- constitution.md - Governance principles
- spec.md - Feature specification
- plan.md - Technical plan
- tasks.md - Implementation tasks

**PM Synchronization Requirements**:
- When product vision changes, PM updates affected specs
- When OKRs change, PM validates all in-flight work still aligns
- When roadmap changes, PM updates affected plans and timelines
- When user stories change, PM validates affected specs and acceptance criteria
- PM documents all product decisions in docs/product/
- PM ensures bi-directional traceability (PRD ↔ spec.md ↔ plan.md ↔ tasks.md)

**Architect Synchronization Requirements**:
- When project architecture changes, Architect reviews all in-flight plans
- When new patterns are established, Architect updates affected plans and tasks
- When technical constraints change, Architect validates affected implementations
- Architect documents all architectural decisions in docs/architecture/02_ADRs/
- Architect ensures technical consistency (architecture ↔ plan.md ↔ tasks.md ↔ code)

**Enforcement**:
- Use `/aod.analyze` to validate product-spec-architecture consistency
- Triad workflows enforce dual sign-off (PM + Architect) before progression
- PRs without PM and Architect approval are blocked from merge
- Sign-offs are documented in artifact metadata

**Tools & Skills**:
- **product-manager agent**: Product Manager with alignment validation expertise
- **architect agent**: Architect with technical design and review expertise
- **/aod.define**: Create PRD documents
- **/aod.plan**: Plan stage orchestrator — chains spec → project-plan → tasks with governance gates
- **/aod.analyze**: Validate consistency across artifacts

**Reference**: See `.claude/agents/product-manager.md` for PM responsibilities, `.claude/agents/architect.md` for Architect responsibilities, and `docs/standards/PRODUCT_SPEC_ALIGNMENT.md` for comprehensive alignment guide

---

### XI. SDLC Triad Collaboration

**Objective**: Ensure Product, Architecture, and Engineering alignment through structured collaboration at PRD creation stage

#### The Triad

1. **Product-Manager (Product Manager)**: Defines **What** and **Why**
2. **Architect (System Architect)**: Defines **How** (Strategic/Technical)
3. **Tech-Lead (Engineering Manager)**: Defines **When** and **Who** (Tactical/Resourcing)

#### Triad Boundaries

| Role | MUST Do | MUST NOT Do |
|------|---------|-------------|
| **PM** | Define user problems, business value, priorities, validate product-market fit | Make technical decisions, estimate development timelines, claim infrastructure status without verification |
| **Architect** | Design architecture, select technology, document current state, provide infrastructure baselines | Manage timelines, assign agents to tasks, define user problems or business priorities |
| **Tech-Lead** | Estimate effort/timelines, assign agents, optimize execution, validate capacity | Rewrite architecture (unless timeline/budget breaks), change feature priorities, choose technology stack |

#### PRD Creation Workflow (Triad Collaboration)

**For Infrastructure/Deployment PRDs**:

0. **PM**: Analyze product need (What & Why) - read product vision, OKRs, user stories
0.5. **Architect**: Provide baseline report documenting current infrastructure state
1. **PM**: Draft PRD via `/aod.define`, incorporating Architect baseline into "Current State" section
2. **Tech-Lead**: Feasibility review - estimate timeline, identify agents needed, validate capacity
3. **Architect**: Technical review - validate infrastructure claims match baseline, confirm technical feasibility
4. **PM**: Finalize PRD incorporating all Triad feedback

**For Feature PRDs** (greenfield work):

0. **PM**: Analyze product need (What & Why)
1. **PM**: Draft PRD via `/aod.define`
2. **[Parallel]** Architect + Tech-Lead: Review PRD for technical feasibility and timeline accuracy
3. **PM**: Finalize PRD incorporating Triad feedback

**Auto-Detection Criteria**:
PRD is classified as "Infrastructure/Deployment" if topic/description contains keywords: "deploy", "deployment", "infrastructure", "production", "staging", "vercel", "database provisioning", "environment setup"

#### Validation Gates

All PRDs MUST have:
- ✅ Architect baseline report (if infrastructure work)
- ✅ Tech-Lead feasibility check with timeline estimate
- ✅ Architect technical review with approval
- ✅ PRD timeline based on Tech-Lead estimate (not PM guess)
- ✅ PRD infrastructure claims validated by Architect against baseline

#### Veto Authority Matrix

| Scenario | Who Can Veto | Veto Grounds |
|----------|-------------|--------------|
| PRD claims infrastructure status | **Architect** | Claims contradict architecture baseline documentation |
| PRD proposes technical approach | **Architect** | Approach is technically infeasible or violates architectural principles |
| PRD estimates timeline | **Tech-Lead** | Timeline ignores capacity constraints or current completion state |
| PRD changes feature priority | **PM** | Misaligned with product vision, OKRs, or user needs |
| plan.md violates product requirements | **PM** | Technical design doesn't serve user needs or business goals |
| tasks.md timeline unrealistic | **Tech-Lead** | Task breakdown doesn't account for dependencies or capacity |

**Veto Process**:
1. Agent invokes veto with clear rationale and supporting evidence
2. Agent provides specific corrections required
3. Originating agent addresses corrections
4. Re-submit for review
5. Approve OR escalate to user for final decision

#### Triad Disagreement Escalation

**Level 1: Triad Negotiation** (<30 minutes)
- PM, Architect, Tech-Lead discuss disagreement
- Each agent presents rationale and supporting evidence
- Attempt to reach consensus or compromise

**Level 2: Constitution Arbitration** (<15 minutes)
- If no consensus, check Constitution for governing principle
- Apply constitutional principle to resolve disagreement
- Example: PM wants 2-week timeline, Tech-Lead says 4 weeks → Apply Principle IX (realistic timelines), defer to Tech-Lead's capacity-based estimate

**Level 3: User Decision** (variable time)
- If Constitution doesn't resolve, escalate to user
- Present both positions with pros/cons and evidence
- User makes final decision
- Document decision in PRD/spec with rationale for future reference

#### Success Criteria

- PRDs have <3 technical inaccuracies (measured by Architect review)
- PRD timelines within 20% of actual delivery (measured post-implementation)
- Architect review time <30 minutes for technical validation
- Triad workflow adds <2 hours to PRD creation cycle time (quality over speed)

#### Non-Compliance

- **PRD finalized without Triad review** → Reject PRD, request revision with proper Triad validation
- **PM makes technical claims without Architect validation** → Architect exercises veto authority
- **PM estimates timeline without Tech-Lead input** → Tech-Lead exercises veto authority
- **Repeated violations** → Escalate to user for governance review

#### Document Storage Standards

| Document | Location | Owner | Purpose |
|----------|----------|-------|---------|
| Architect Baseline | `specs/{feature-id}/architect-baseline.md` | Architect | Current infrastructure state for deployment PRDs |
| Feasibility Check | `specs/{feature-id}/feasibility-check.md` | Tech-Lead | Timeline, agent assignments, capacity validation |
| Architect PRD Review | `docs/agents/architect/{date}_{feature}_prd-review_ARCH.md` | Architect | Technical validation report |

**Reference**: See `docs/standards/TRIAD_COLLABORATION.md` for comprehensive Triad workflow guide, artifact templates, and practical examples

---

## AOD Lifecycle Model

### Lifecycle Stages

The AOD Lifecycle is a single, named sequence of **6 stages** organized into **3 phases**. All work passes through these stages in order.

**Discovery Phase** (What to build):

| Stage | Purpose | Primary Command |
|-------|---------|-----------------|
| **Discover** | Capture ideas, score with ICE, gather evidence | `/aod.discover` |
| **Define** | Create PRD with Triad validation | `/aod.define` |

**Delivery Phase** (How to build and ship):

| Stage | Purpose | Primary Command |
|-------|---------|-----------------|
| **Plan** | Create spec, architecture plan, and task breakdown | `/aod.plan` |
| **Build** | Implement tasks with Architect checkpoints | `/aod.build` |
| **Deliver** | Validate against DoD, run retrospective, close feature | `/aod.deliver` |

**Quality Phase** (Is the quality where it needs to be):

| Stage | Purpose | Primary Command |
|-------|---------|-----------------|
| **Document** | Human-driven code simplification, docstrings, CHANGELOG, API docs | `/aod.document` |

### Governance Gates

Governance gates are a **separate layer** from lifecycle stages. Gates are Triad approval checkpoints that operate **at stage boundaries** -- they determine who approves, not what work is done.

| Gate Location | Checkpoint | Approvers |
|---------------|------------|-----------|
| Discover exit | ICE score + PM validation | PM |
| Define exit | PRD Triad review | PM + Architect + Team-Lead |
| Plan: spec | Spec sign-off | PM |
| Plan: project-plan | Plan sign-off | PM + Architect |
| Plan: tasks | Triple sign-off | PM + Architect + Team-Lead |
| Build (continuous) | Architect checkpoints | Architect |
| Deliver exit | Definition of Done check | PM + Architect + Team-Lead |
| Document (per step) | Human approval | Human (accept/reject/skip per step) |

**Invariants**:
- Triple sign-off (PM + Architect + Team-Lead on tasks.md) is the **minimum governance floor** for all tiers
- DoD check applies to **all tiers**
- Architect build checkpoints apply to **all tiers**
- Document stage (human approval per step) applies to **all tiers**

### Governance Tiers

Three tiers determine which gates are active. Tiers affect only the Discover, Define, and Plan stage gates.

| Tier | Discover Gate | Define Gate | Plan Gates | Build Gate | Deliver Gate | Document Gate |
|------|---------------|-------------|------------|------------|--------------|---------------|
| **Light** | Optional | Skip | Triple sign-off only | On | DoD | Human approval |
| **Standard** (default) | On | On | PM+Arch + Triple | On | DoD | Human approval |
| **Full** | On | On | PM spec + PM+Arch plan + Triple | On | DoD | Human approval |

**When to use each tier**:

- **Light** (2 gates): Solo developers, prototypes, internal tools. Minimizes ceremony while preserving the governance floor (Triple sign-off + DoD).
- **Standard** (6 gates, default): Team projects and production features. All Discover, Define, and Plan gates active with Architect checkpoints in Build.
- **Full** (all gates): Regulated industries, critical systems, high-risk deployments. Adds a separate PM spec sign-off in the Plan stage for maximum traceability.

### Governance Configuration

Configure the active governance tier in the constitution frontmatter or project configuration:

```yaml
governance:
  tier: standard  # valid values: light | standard | full
```

The tier is configured **per project**, not per feature. The default tier is `standard`.

---

## System Architecture Constraints

### Backend Requirements

- **Database**: {{TECH_STACK_DATABASE}} (e.g., PostgreSQL, MySQL)
- **Vector Search**: {{TECH_STACK_VECTOR}} (e.g., pgvector, Pinecone, Qdrant)
- **API Response Time**: <500ms for 95% of requests (excluding RAG search operations)
- **Horizontal Scalability**: Stateless design with no session affinity required
- **Authentication**: {{TECH_STACK_AUTH}} (e.g., JWT, OAuth2)

### Frontend Requirements

- **Responsive Design**: Mobile-friendly (tablet minimum, 768px breakpoint)
- **Real-time Updates**: Task board reflects state changes within 5 seconds
- **Accessibility**: WCAG 2.1 Level AA compliance
- **Performance**: Time to Interactive (TTI) <3 seconds on 4G connection

### MCP Interface Requirements

- **Protocol Compliance**: Full Model Context Protocol specification adherence
- **Tool Response Time**: <500ms (excluding search operations)
- **Resource Caching**: Support client-side caching with cache invalidation
- **Error Handling**: Structured errors agents can handle programmatically
- **Stateless Design**: No session affinity, horizontally scalable

### Performance Targets

- **Concurrent Agents**: Support 10+ concurrent connections per project
- **Vector Search**: <2s response time for 90th percentile queries
- **Task Locking**: <100ms for claim/release operations
- **Document Ingestion**: <60s for typical documentation page
- **System Uptime**: 99.9% SLA (excluding planned maintenance)

## Development Standards

### Testing Requirements

- **Unit Tests**: Required for all business logic (minimum 80% coverage)
- **Integration Tests**: Required for API endpoints and database operations
- **End-to-End Tests**: Required for critical user flows (task claiming, search)
- **Performance Tests**: Required for concurrency scenarios and vector search
- **Test-First Development**: Tests written before implementation for core features

### Code Quality Standards

- **Linting**: Automated linting enforced in CI/CD pipeline
- **Type Safety**: Static typing required (TypeScript, Python type hints, etc.)
- **Code Review**: All changes require peer review before merge
- **Documentation**: Public APIs must have inline documentation and examples
- **Error Handling**: Graceful degradation, no silent failures

### Deployment Standards

- **CI/CD Pipeline**: Automated testing and deployment
- **Database Migrations**: Versioned, reversible, tested in staging
- **Feature Flags**: New features behind flags for gradual rollout
- **Monitoring**: Observability for all critical paths (logging, metrics, tracing)
- **Rollback Plan**: Documented rollback procedure for each deployment

### Security Standards

- **Dependency Scanning**: Automated vulnerability scanning in CI/CD
- **Secret Management**: No secrets in code or configuration files
- **Input Validation**: All user input sanitized and validated
- **SQL Injection Prevention**: Parameterized queries only, no string concatenation
- **XSS Prevention**: Output encoding, Content Security Policy headers
- **OWASP Compliance**: OWASP Top 10 vulnerabilities addressed

## Governance

### Amendment Process

1. **Proposal**: Document proposed change with rationale and impact analysis
2. **Review**: Technical review by project maintainers
3. **Approval**: Requires consensus from core team
4. **Migration Plan**: For breaking changes, document migration path
5. **Version Bump**: Update constitution version following semantic versioning

### Versioning Policy

- **MAJOR**: Backward incompatible governance changes or principle removal
- **MINOR**: New principle added or material guidance expansion
- **PATCH**: Clarifications, wording improvements, non-semantic refinements

### Compliance Verification

- All pull requests MUST verify compliance with constitution principles
- Architecture decisions MUST reference relevant principles
- Use `/aod.analyze` to verify consistency across spec, plan, and tasks
- Constitution supersedes all other practices and conventions

### Living Document

This constitution is a living document that evolves with the project. When principles conflict with practical needs, the constitution should be amended rather than ignored.

**Version**: 1.0.0 | **Ratified**: {{RATIFICATION_DATE}} | **Last Amended**: {{RATIFICATION_DATE}}

---

## Template Instructions

### How to Customize This Constitution

**Step 1: Replace Project Identifiers**
- `{{PROJECT_NAME}}`: Your project name (e.g., "my-saas-platform")
- `{{PROJECT_DESCRIPTION}}`: Brief description of what your project does

**Step 2: Replace Technology Stack**
- `{{TECH_STACK_DATABASE}}`: Your database choice (PostgreSQL, MySQL, MongoDB, etc.)
- `{{TECH_STACK_VECTOR}}`: Your vector search solution (pgvector, Pinecone, Qdrant, etc.)
- `{{TECH_STACK_AUTH}}`: Your authentication approach (JWT, OAuth2, Auth0, etc.)

**Step 3: Replace Dates**
- `{{RATIFICATION_DATE}}`: Date you deploy this constitution (YYYY-MM-DD format)

**Step 4: Review System Architecture Constraints**
- Adjust performance targets based on your requirements
- Modify backend/frontend requirements if needed
- Update MCP interface requirements if not using MCP

**Step 5: Remove This Section**
- Delete this "Template Instructions" section after customization
- Keep all Core Principles (I-XI) - they are universal governance rules
- Keep Triad Collaboration framework - it's the core workflow

**What NOT to Change**:
- Core Principles (I-XI) - These are universal and project-agnostic
- SDLC Triad Collaboration framework - This is the governance model
- Amendment Process - This ensures constitution stability
- Versioning Policy - Standard semantic versioning

**First Deployment**:
1. Customize all `{{PLACEHOLDERS}}`
2. Set version to 1.0.0
3. Set ratification date to deployment date
4. Delete this "Template Instructions" section
5. Commit to repository: `git add .aod/memory/constitution.md && git commit -m "feat(governance): deploy project constitution v1.0.0"`
