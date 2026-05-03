# SDLC Team Orchestration Guide

## Strategic Vision

This orchestration guide maximizes our team's specialized capabilities through intelligent parallel work streams, clear decision authorities, and quality-gated handoffs. We optimize for **speed without sacrificing quality** by leveraging each agent's expertise while maintaining architectural coherence and production readiness.

## Team Roster & Core Strengths

### Strategic Layer (Opus Models)
- **head-honcho**: Product Strategy & Requirements - Transforms business ideas into structured product plans with user stories and acceptance criteria
- **architect**: System Architecture & Technical Design - Creates comprehensive technical blueprints and API contracts from product requirements
- **Jimmy**: AI Systems & Prompt Engineering - Optimizes AI components, prompts, and agent interactions for maximum effectiveness

### Implementation Layer (Sonnet Models)
- **code-monkey**: Frontend Engineering - Builds modern, responsive UIs following design specifications and architectural patterns
- **senior-backend-engineer**: Backend Engineering - Implements robust server-side systems, APIs, and data persistence with production security standards
- **ux-ui-designer**: User Experience Design - Creates comprehensive design systems and user interaction specifications
- **security-analyst**: Security Analysis - Ensures comprehensive security validation and vulnerability assessment throughout development
- **tester**: Quality Assurance - Validates functionality, security, and performance with automated testing including UI testing
- **devops**: Deployment Engineering - Orchestrates containerization to production deployment with cloud infrastructure and CI/CD pipelines

## Optimized SDLC Workflow

### Phase 1: Strategic Foundation (Duration: 1-2 days)
**Lead: head-honcho | Parallel Execution: Yes**

**Parallel Work Streams:**
```
head-honcho: Product requirements & user stories
     ↓ (immediate handoff)
ux-ui-designer: Information architecture & user journey mapping (can start with rough requirements)
     ↓ (continuous feedback loop)  
Jimmy: AI component identification & prompt strategy planning
```

**Deliverables:**
- Product requirements document with user stories and acceptance criteria
- Initial user journey maps and information architecture
- AI component strategy and prompt engineering approach
- Success metrics and validation criteria

**Quality Gates:**
- [ ] User stories have clear acceptance criteria with edge cases
- [ ] AI components identified with clear functional requirements
- [ ] UX strategy aligns with user stories and business goals
- [ ] All stakeholders can clearly understand what will be built

### Phase 2: Architecture & Design (Duration: 2-3 days)
**Lead: architect | Parallel Execution: Maximum**

**Parallel Work Streams:**
```
architect: Technical architecture & API contracts
     ↕ (continuous collaboration)
ux-ui-designer: Complete design system & component specifications
     ↕ (design-architecture alignment)
Jimmy: Prompt development & AI system architecture
     ↓ (early feedback to backend design)
security: Architecture security review & threat modeling
```

**Deliverables:**
- Complete technical architecture with API specifications
- Comprehensive design system with all component specifications
- Production-ready prompts and AI integration patterns
- Security architecture and threat model
- Database schema and migration strategy

**Quality Gates:**
- [ ] API contracts fully specified with request/response schemas
- [ ] Design system components match architectural capabilities
- [ ] Security architecture addresses identified threats
- [ ] AI components have testable interfaces and fallback strategies
- [ ] All dependencies and integration points clearly defined

### Phase 3: Rapid Development (Duration: 3-5 days)
**Lead: Shared (code-monkey & senior-backend-engineer) | Maximum Parallelization**

**Parallel Work Streams:**
```
code-monkey: Frontend implementation from design specs
     ↕ (API contract coordination)
senior-backend-engineer: Backend APIs & business logic implementation
     ↕ (database schema coordination)
devops: Local containerization for immediate testing (PHASE 3 MODE)
     ↓ (continuous integration)
tester: Automated test suite development
     ↓ (security test coordination)
security-analyst: Security implementation review & vulnerability testing
     ↓ (AI system validation)
Jimmy: Prompt optimization based on implementation feedback
```

**Critical Dependencies:**
- Backend API implementation must align with frontend integration needs
- Database migrations must be executed before dependent business logic
- Local containerization enables immediate testing and validation

**Deliverables:**
- Complete frontend application with responsive design
- Production-ready backend APIs with authentication
- Local development environment with hot reloading
- Automated test suite with security validation
- Optimized AI components integrated into application flow

**Quality Gates:**
- [ ] Frontend matches design specifications across all breakpoints
- [ ] Backend APIs pass contract validation and security review
- [ ] Local environment runs successfully with single command
- [ ] Automated tests achieve >80% coverage with security validation
- [ ] AI components perform within acceptable parameters

### Phase 4: Quality Assurance & Optimization (Duration: 2-3 days)
**Lead: tester | Structured Parallel Execution**

**Parallel Work Streams:**
```
tester: Comprehensive testing including UI automation with Playwright
     ↓ (bug coordination)
code-monkey & senior-backend-engineer: Bug fixes and performance optimization in respective domains
     ↓ (UX validation coordination)
ux-ui-designer: Design validation & usability testing
     ↓ (security coordination)
security-analyst: Comprehensive vulnerability assessment & penetration testing
     ↓ (architecture validation)
architect: Performance benchmarking & scalability validation
     ↓ (AI performance coordination)
Jimmy: AI system performance optimization & edge case handling
```

**Deliverables:**
- Complete test suite execution with >95% pass rate
- Performance optimization with benchmarked improvements
- Security assessment with vulnerability remediation
- UX validation with usability testing results
- AI component reliability testing and optimization

**Quality Gates:**
- [ ] All critical and high-priority bugs resolved
- [ ] Security vulnerabilities addressed with verification testing
- [ ] Performance meets or exceeds specified benchmarks
- [ ] UX validation confirms intuitive user experience
- [ ] AI components handle edge cases gracefully

### Phase 5: Production Readiness (Duration: 2-4 days)
**Lead: devops | Infrastructure-Focused Execution**

**Execution Strategy:**
```
devops: Production infrastructure & CI/CD (PRODUCTION MODE)
     ↕ (security integration)
security-analyst: Production security audit & compliance validation
     ↓ (final validation)
tester: Production deployment validation & smoke testing
     ↓ (documentation coordination)
architect: Final architecture documentation & handoff guides
     ↓ (monitoring setup)
All agents: Production monitoring setup & alerting configuration
```

**Deliverables:**
- Complete production infrastructure with auto-scaling
- Secure CI/CD pipeline with automated quality gates
- Production monitoring and alerting systems
- Comprehensive deployment documentation
- Disaster recovery and rollback procedures

**Quality Gates:**
- [ ] Production infrastructure passes security audit
- [ ] CI/CD pipeline successfully deploys to staging environment
- [ ] Monitoring systems provide comprehensive observability
- [ ] Documentation enables independent deployment and maintenance
- [ ] Disaster recovery procedures tested and verified

## Decision Authority Matrix

### Strategic Decisions
| Decision Type | Primary Authority | Required Approval | Can Override |
|---------------|------------------|------------------|--------------|
| Product roadmap & priorities | head-honcho | - | Project sponsor |
| Technical architecture & stack | architect | security (security concerns) | head-honcho (business impact) |
| User experience & design | ux-ui-designer | head-honcho (business alignment) | architect (technical constraints) |
| AI system architecture | Jimmy | architect (integration), security (safety) | head-honcho (business needs) |

### Implementation Decisions  
| Decision Type | Primary Authority | Required Consultation | Can Override |
|---------------|------------------|---------------------|--------------|
| Frontend implementation patterns | code-monkey | ux-ui-designer, architect | architect (major changes) |
| Backend architecture & APIs | senior-backend-engineer | architect, security-analyst | architect (design violations) |
| Security controls & policies | security-analyst | architect (feasibility) | head-honcho (business risk acceptance) |
| Testing strategies & coverage | tester | All implementing agents | architect (technical constraints) |
| Deployment & infrastructure | devops | architect, security-analyst | architect (major changes) |

### Escalation Procedures
1. **Technical disputes**: Implementing agent → architect → head-honcho
2. **Security concerns**: Any agent → security-analyst → architect → head-honcho  
3. **UX/Business conflicts**: ux-ui-designer → head-honcho
4. **Performance issues**: Implementing agent → architect → devops → head-honcho
5. **AI system issues**: Jimmy → architect → head-honcho
6. **Quality disputes**: tester → architect → head-honcho

## Intelligent Parallel Work Optimization

### Always Run in Parallel
- **Phase 1**: head-honcho + ux-ui-designer + Jimmy (requirements, UX, AI strategy)
- **Phase 2**: architect + ux-ui-designer + Jimmy + security-analyst (architecture, design, AI, security)
- **Phase 3**: code-monkey + senior-backend-engineer + devops + tester + security-analyst + Jimmy (full parallel development)
- **Phase 4**: tester + all implementing agents (testing with parallel fixes)
- **Phase 5**: devops + security-analyst + tester (production deployment coordination)

### Sequential Dependencies (Must Respect)
- Product requirements → Technical architecture → Implementation
- Technical architecture → Local containerization → Testing
- Implementation completion → Quality assurance → Production deployment
- Security architecture → Security implementation → Security validation

### Cross-Phase Optimization
- **ux-ui-designer** can start design system work with rough requirements
- **Jimmy** can begin prompt development with early architectural input  
- **devops** can prepare containerization templates during architecture phase
- **tester** can develop test frameworks during implementation phase
- **security-analyst** provides continuous feedback rather than gate-based approval

## Quality Gates & Handoff Requirements

### Universal Handoff Standards
Every phase handoff must include:
- [ ] **Deliverable completeness**: All specified outputs produced to quality standards
- [ ] **Documentation currency**: Implementation details documented for next phase
- [ ] **Validation results**: Quality gates passed with evidence
- [ ] **Known issues log**: Documented blockers, limitations, or technical debt
- [ ] **Next phase readiness**: Clear requirements and context for downstream work

### Phase-Specific Quality Requirements

#### Phase 1 → Phase 2
- [ ] User stories have measurable acceptance criteria
- [ ] Business requirements prioritized with clear rationale
- [ ] Success metrics defined and measurable
- [ ] UX strategy aligns with business goals
- [ ] AI components identified with functional requirements

#### Phase 2 → Phase 3
- [ ] API contracts fully specified with schemas
- [ ] Database schema documented with relationships
- [ ] Component architecture enables parallel development
- [ ] Security architecture addresses threat model
- [ ] Design system provides complete implementation guidance

#### Phase 3 → Phase 4
- [ ] Code complete with local environment functional
- [ ] Security controls implemented per specifications
- [ ] AI components integrated and functional
- [ ] Automated tests written (coverage >80%)
- [ ] Performance baseline established

#### Phase 4 → Phase 5
- [ ] All critical bugs resolved with verification
- [ ] Security vulnerabilities remediated
- [ ] Performance meets specified benchmarks
- [ ] UX validation confirms usability
- [ ] Production readiness checklist completed

### Emergency Bypass Protocol

**When to Use**: Critical security issues, business-critical bugs, or severe production incidents

**Process**:
1. **Issue identification**: Any agent can trigger emergency protocol
2. **Impact assessment**: security + architect + head-honcho (15 min response)
3. **Minimal fix implementation**: Relevant technical agent with security oversight
4. **Expedited testing**: tester focuses on affected functionality only
5. **Emergency deployment**: devops with rollback plan ready
6. **Post-incident review**: All agents participate in retrospective within 24 hours

**Authority**: devops has deployment authority with security-analyst + tester approval for emergency fixes

## Success Metrics & Monitoring

### Phase Completion Metrics
- **Phase 1**: Requirements clarity score (stakeholder validation survey)
- **Phase 2**: Architecture completeness score (implementation readiness checklist)
- **Phase 3**: Implementation quality score (automated quality gates)
- **Phase 4**: Quality assurance score (test coverage + performance benchmarks)
- **Phase 5**: Production readiness score (deployment success + monitoring health)

### Cross-Phase Efficiency Metrics
- **Handoff quality**: Number of clarification requests between phases
- **Parallel efficiency**: Percentage of work completed in parallel vs sequential
- **Decision latency**: Average time for decision authority resolution
- **Quality velocity**: Ratio of features passing quality gates on first review

### Continuous Improvement
- **Weekly retrospectives**: Process improvement and bottleneck identification
- **Monthly architecture reviews**: Technical debt assessment and optimization
- **Quarterly capability assessment**: Agent skill development and role optimization

## Quick Start Commands & Workflows

### Starting New Feature Development
```bash
# Phase 1: Strategic Foundation
@head-honcho create product requirements for [FEATURE_NAME] with user stories and acceptance criteria
@ux-ui-designer analyze user journey and information architecture for [FEATURE_NAME]
@Jimmy identify AI components and develop prompt strategy for [FEATURE_NAME]

# Phase 2: Architecture & Design (Parallel)
@architect design technical architecture and API contracts for [FEATURE_NAME]
@ux-ui-designer create complete design system and component specifications
@security-analyst conduct architecture security review and threat modeling
@Jimmy develop production prompts and AI integration patterns

# Phase 3: Rapid Development (Maximum Parallel)
@code-monkey implement frontend following design specs and architecture
@senior-backend-engineer implement backend APIs and business logic with database migrations  
@devops setup local containerization for immediate testing
@tester develop automated test suite with security validation
@security-analyst implement security controls and vulnerability testing

# Phase 4: Quality Assurance (Structured Parallel)
@tester execute comprehensive testing including UI automation
@security-analyst perform comprehensive vulnerability assessment  
@ux-ui-designer validate design implementation and usability
@architect validate performance benchmarks and scalability

# Phase 5: Production Readiness (Infrastructure-Focused)
@devops provision production infrastructure and CI/CD pipeline
@security-analyst conduct production security audit and compliance validation
@tester perform production deployment validation and smoke testing
```

### Emergency Response
```bash
# Critical Issue Response
@security-analyst assess security impact and threat level
@architect evaluate technical impact and system implications
@head-honcho determine business impact and priority
@[relevant-agent] implement minimal viable fix with security oversight
@devops prepare emergency deployment with rollback ready
```

This orchestration maximizes our team velocity while ensuring production quality through intelligent parallel work streams, clear decision authorities, and comprehensive quality gates. Each agent operates at their peak effectiveness while maintaining seamless collaboration and architectural coherence.