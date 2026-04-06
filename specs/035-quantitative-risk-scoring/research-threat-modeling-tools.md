# Research: Threat Modeling Tools Landscape (March 2026)

## Context

This research surveys the current threat modeling tools market to inform tachi's quantitative risk scoring feature. Understanding what tools exist, how they score and rank threats, what methodologies they support, and where they fall short -- particularly around AI/agentic systems -- directly informs how tachi should differentiate its approach.

---

## Findings

### FREE / OPEN-SOURCE TOOLS

---

#### 1. OWASP Threat Dragon

- **Creator**: OWASP Foundation
- **Pricing**: Free, open-source (Apache 2.0)
- **Website**: https://owasp.org/www-project-threat-dragon/
- **Key Features**:
  - Visual threat model diagramming (web and desktop versions)
  - Threat recording and mitigation tracking
  - Follows the Threat Modeling Manifesto values and principles
- **Methodology Support**: STRIDE, LINDDUN, CIA, DIE, PLOT4ai
- **Integration**: GitHub repository updates
- **Target Audience**: Security practitioners using established methodologies
- **Differentiators**: Broadest methodology support among free tools (5 frameworks); OWASP brand credibility; community-maintained
- **Weaknesses**: Infrequent updates (a few times yearly); limited automation; no AI-assisted threat generation; no quantitative scoring beyond manual severity assignment

---

#### 2. Microsoft Threat Modeling Tool

- **Creator**: Microsoft
- **Pricing**: Free (closed-source)
- **Website**: https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool
- **Key Features**:
  - Step-by-step guidance for non-security specialists
  - Automated threat generation after diagramming
  - Reporting capability
  - Extensive documentation and training modules
- **Methodology Support**: STRIDE-based
- **Integration**: Azure ecosystem alignment
- **Target Audience**: Non-security specialists; newcomers to threat modeling
- **Differentiators**: Designed specifically for non-security personnel; Microsoft ecosystem fit; well-documented learning path
- **Weaknesses**: Desktop-only; Windows-centric; infrequent GitHub updates; limited to STRIDE; no AI/ML threat categories; no quantitative risk scoring; Azure-biased
- **Note**: Microsoft published a blog post in February 2026 on "Threat Modeling AI Applications" and added an AI-driven threat-playbook generator to Azure DevOps in March 2025, signaling investment in AI-era threat modeling, but this has not yet flowed into the standalone tool.

---

#### 3. Threagile

- **Creator**: Open-source community
- **Pricing**: Free, open-source
- **Website**: https://threagile.io/
- **Key Features**:
  - YAML/JSON-based declarative threat modeling (threat-modeling-as-code)
  - Multi-view reporting with risk color-coding
  - Management summaries with clickable PDF links
  - Agile-friendly workflow
- **Methodology Support**: Custom YAML-driven (not tied to a single methodology)
- **Integration**: IDE and YAML editor compatibility; CI/CD pipeline friendly
- **Target Audience**: Developers comfortable with code-first approaches
- **Differentiators**: Developer-centric "made for developers" philosophy; excellent reporting; declarative approach fits DevSecOps workflows; no GUI required
- **Weaknesses**: Requires coding knowledge; smaller community than OWASP tools; not widely adopted in enterprise; limited to built-in rule set

---

#### 4. OWASP pytm

- **Creator**: OWASP Foundation
- **Pricing**: Free, open-source
- **Website**: https://github.com/OWASP/pytm
- **Key Features**:
  - Threat-Modeling-as-Code in Python
  - Define systems as Python objects (processes, data flows, boundaries)
  - Auto-generates Data Flow Diagrams and Sequence Diagrams
  - Auto-generates threat reports from model definitions
  - Diagrams stay in sync with code changes
- **Methodology Support**: STRIDE-based threat generation from model definitions
- **Integration**: CI/CD pipelines; Python ecosystem
- **Target Audience**: Development teams already using Python; teams wanting threat models versioned alongside code
- **Differentiators**: True code-first threat modeling; diagrams are outputs not inputs; version-controllable; CI/CD native
- **Weaknesses**: Python-only; steep learning curve for non-developers; limited visualization options; threat library depends on community contributions

---

#### 5. CAIRIS

- **Creator**: Bournemouth University (Dr. Shamal Faily)
- **Pricing**: Free, open-source (Apache 2.0)
- **Website**: https://cairis.org/
- **Key Features**:
  - Integrated requirements and security analysis
  - Auto-generates DFDs as designs evolve
  - Attacker persona creation
  - 12 system views (risk + architectural perspectives)
  - Attack pattern identification and mitigation insights
  - GDPR DPIA document generation
  - Volere-compliant requirement specifications
- **Methodology Support**: Multiple; attack pattern-based
- **Integration**: REST API for toolchain integration; Docker deployment
- **Target Audience**: Security researchers; teams needing requirements-security integration
- **Differentiators**: Unique integration of requirements engineering with security analysis; attacker personas; 12 distinct system views; GDPR compliance document generation
- **Weaknesses**: Academic origins make enterprise adoption challenging; complex setup; smaller user community; less intuitive UI than commercial tools

---

#### 6. STRIDE-GPT

- **Creator**: mrwadams (open-source)
- **Pricing**: Free, open-source
- **Website**: https://github.com/mrwadams/stride-gpt
- **Key Features**:
  - AI-powered threat model generation using LLMs
  - Attack tree generation with Mermaid diagrams
  - Mitigation recommendations
  - Gherkin test case generation from threats
  - DREAD risk scoring
  - Multi-modal input (architecture diagrams, flowcharts)
  - GitHub repository analysis for context-aware threat models
  - Agentic AI threat modeling with OWASP Top 10 for Agentic Applications (ASI01-ASI10)
  - Architectural pattern detection (RAG pipelines, multi-agent systems, code execution environments, tool ecosystems)
- **Methodology Support**: STRIDE, DREAD scoring, OWASP LLM Top 10, OWASP Top 10 for Agentic Applications, CSA MAESTRO-inspired patterns
- **LLM Providers**: OpenAI, Anthropic Claude, Google Gemini, Mistral, Groq, Azure OpenAI, Ollama, LM Studio
- **Integration**: Streamlit web UI; Docker deployment; local-only architecture
- **Target Audience**: Individual security practitioners; teams exploring AI-assisted threat modeling
- **Differentiators**: Most comprehensive AI-powered open-source threat modeler; agentic AI support is unique among free tools; multi-LLM provider support; actively maintained (v0.15, 999 GitHub stars)
- **Weaknesses**: Single-user focused (not enterprise multi-tenant); data sent to cloud LLM providers unless using local models; Gemini safety restrictions block attack tree generation; some local LLMs produce inconsistent JSON output; no persistent storage

---

#### 7. Threatspec

- **Creator**: Open-source community
- **Pricing**: Free, open-source
- **Website**: https://threatspec.org/
- **Key Features**:
  - Threat modeling annotations as source code comments
  - Dynamic report and DFD generation from code annotations
  - Bridges development and security processes
- **Methodology Support**: Annotation-driven (methodology agnostic)
- **Integration**: Source code integration; CI/CD pipeline compatible
- **Target Audience**: Development teams wanting inline threat documentation
- **Differentiators**: Unique "threat modeling as comments" approach; keeps threat models co-located with code; developer-friendly
- **Weaknesses**: Requires developer discipline to maintain annotations; limited visualization; small community; no quantitative scoring

---

#### 8. AWS Threat Composer

- **Creator**: AWS Labs
- **Pricing**: Free
- **Website**: https://awslabs.github.io/threat-composer/
- **Key Features**:
  - Browser-based, local storage (data never leaves the machine unless exported)
  - Threat statement authoring (not diagram-based)
  - JSON export for code integration
  - Inspired by Adam Shostack's Four Question Framework
- **Methodology Support**: STRIDE-based; Shostack's Four Question Framework
- **Integration**: JSON export; browser-only
- **Target Audience**: AWS developers; teams preferring structured threat statements over diagrams
- **Differentiators**: Privacy-first (fully local); minimal footprint; structured threat statement approach
- **Weaknesses**: No diagramming capability; no questionnaires; manual entry required; no automated threat generation; no scoring/quantification

---

#### 9. Precogly

- **Creator**: Vikramaditya Narayan (Bangalore/NYC)
- **Pricing**: Free, open-source (Apache 2.0)
- **Website**: https://precogly.org/ | https://github.com/precogly/precogly
- **Key Features**:
  - Advanced DFD editor with nested components, trust zones, and trust boundaries (React Flow)
  - Community library packs: MITRE ATT&CK, CAPEC, LINDDUN, STRIDE
  - Cloud-specific packs: AWS, Azure, GCP, plus banking sector
  - TM-BOM JSON import/export for interoperability (no vendor lock-in)
  - Compliance mapping: DORA, CRA, ASVS, NIST CSF, SOC 2
  - AI-ready REST API with OpenAPI documentation
  - Workspace-based team collaboration
- **Tech Stack**: React 19, TypeScript, Django 5.1, PostgreSQL 16, Docker
- **Methodology Support**: STRIDE, LINDDUN, MITRE ATT&CK, CAPEC (via library packs)
- **Integration**: REST API (OpenAPI); TM-BOM JSON format; Docker deployment
- **Target Audience**: Security architects seeking org-wide scalability; security engineers building AI assistants; consultants/trainers; compliance professionals
- **Differentiators**: Fills the gap between ad-hoc open tools and expensive commercial platforms; compliance-aware out of the box (DORA, CRA, NIST CSF, SOC 2); extensible library pack ecosystem; AI-ready API foundation; creator actively researching multi-agent threat modeling using LLM-driven pre-mortems across agentic architectures
- **Weaknesses**: Very new (48 GitHub stars, 177 commits as of April 2026); no AI-powered threat generation yet (roadmap); no quantitative risk scoring; requires Docker/PostgreSQL deployment (not local-first); no SARIF output
- **Note**: Creator spoke at ThreatModCon DC on emergent risks in multi-agentic systems. Published a comparison of attacker-centric (PASTA/attack trees) vs. architecture-driven (STRIDE-per-element) approaches, concluding neither paradigm is strictly superior. Certified Threat Modeling Professional with CMU MS; leads Bangalore chapter of Threat Modeling Connect.

---

### COMMERCIAL / ENTERPRISE TOOLS

---

#### 10. IriusRisk

- **Creator**: IriusRisk (Barcelona, Spain)
- **Pricing**: Free Community Edition; Commercial Enterprise (tiered by threat model volume, 5-500+; custom quote required)
- **Website**: https://www.iriusrisk.com/
- **Key Features**:
  - Draw.io-based diagramming in Community Edition
  - Security libraries with risks and countermeasures
  - Import/export (XLS, XML)
  - NIST, OWASP, GDPR, HIPAA compliance libraries
  - ML/AI threat library (first of its kind)
  - Customizable components, workflows, and rules
  - Threat templates
- **Methodology Support**: STRIDE, TRIKE, OCTAVE, PASTA (methodology-agnostic platform)
- **Integration**: Custom workflow automation; extensible architecture; AWS Marketplace listing
- **Target Audience**: Critical infrastructure; regulated industries (finance, medical devices, transport); enterprise security teams
- **Differentiators**: Broadest methodology support among commercial tools; ML/AI threat library; methodology-agnostic; free community tier with enterprise-grade libraries
- **Weaknesses**: Enterprise pricing opaque (quote required); community edition has limited scale; steep learning curve for full platform
- **Market Position**: Gartner Peer Insights reviewed; G2 reviewed; leading commercial threat modeling platform

---

#### 11. ThreatModeler

- **Creator**: ThreatModeler Software Inc.
- **Pricing**: Commercial (quote required; no public pricing)
- **Website**: https://threatmodeler.com/
- **Key Features**:
  - Unified platform: application security, IaC-Assist (infrastructure-as-code), CloudModeler
  - Enterprise-ready models in minutes
  - Patented automation technology
  - AI/ML-assisted modeling
  - Continuous threat detection (not point-in-time)
  - 2,500+ security requirements; 180+ compliance frameworks; 1,500+ threats; 2,900+ components; 100+ protocols
- **Methodology Support**: Multiple frameworks (specific list not published)
- **Integration**: CI/CD pipeline native; partner ecosystem (Deloitte, EY, GuidePoint, Optiv, SHI)
- **Target Audience**: Large enterprises; banking/finance, healthcare, manufacturing, critical infrastructure
- **Differentiators**: Only platform unifying application + cloud + infrastructure threat modeling; BYOAI (Bring Your Own AI); patented automation; massive built-in library; code-to-cloud visibility
- **Weaknesses**: No transparent pricing; limited public documentation on specific methodology support; complex enterprise deployment; no free tier

---

#### 12. SD Elements (Security Compass)

- **Creator**: Security Compass
- **Pricing**: Commercial (quote required)
- **Website**: https://www.securitycompass.com/sdelements/
- **Key Features**:
  - Questionnaire-driven threat assessment
  - Compliance-focused workflow
  - Developer guidance built-in
  - Extensive documentation and training modules
  - Now includes Devici (acquired) for diagram-based modeling
- **Methodology Support**: Compliance and control-based; NIST, FedRAMP alignment
- **Integration**: GitHub; CI/CD pipelines; Jira; Azure DevOps
- **Target Audience**: DoD, Military, Federal agencies; organizations seeking ATO (Authority to Operate); regulated enterprises
- **Differentiators**: Dominant in federal/military market; compliance-first approach; acquisition of Devici adds diagram-based capability
- **Weaknesses**: Enterprise-only pricing; compliance-heavy approach may limit agility; less suited for startup/agile environments

---

#### 13. Devici (Security Compass)

- **Creator**: Originally independent; acquired by Security Compass
- **Pricing**: Free tier (3 users, 3 threat models); paid Enterprise (unlimited users/models, per-user pricing, quote required)
- **Website**: https://www.securitycompass.com/devici/
- **Key Features**:
  - Diagram-first threat modeling
  - AI Diagram Assistant (text-to-DFD generation)
  - CodeGenius (source code analysis for auto-generating initial threat models)
  - Threat Model Health Score
  - Devici Codex (threat and mitigation library)
  - OTM (Open Threat Model) format support
  - Real-time collaboration
  - Reusable patterns, templates, version history
  - Workflow integration (tasks to Azure DevOps or Jira)
- **Methodology Support**: STRIDE; OTM standard
- **Integration**: Azure DevOps; Jira; OTM interoperability
- **Target Audience**: AppSec teams; DevSecOps engineers; collaborative security teams
- **Differentiators**: AI-powered diagram generation from text; source-code-to-threat-model pipeline (CodeGenius); Health Score for completeness measurement; OTM standard support for interoperability
- **Weaknesses**: Free tier limited to 3 models/3 users; recently acquired (integration with SD Elements still maturing); smaller user base than IriusRisk or ThreatModeler

---

#### 14. Apiiro AI Threat Modeling

- **Creator**: Apiiro
- **Pricing**: Commercial (private preview launched Mar 2026; demo required; enterprise sales model)
- **Website**: https://apiiro.com/blog/introducing-ai-threat-modeling/
- **Announced**: March 23, 2026 (showcased at RSA Conference 2026)
- **Product Context**: Capability within the Apiiro **Guardian Agent**, built on patented **Deep Code Analysis (DCA)** technology
- **Key Features**:
  - Autonomous threat model generation from design documents, tickets, architectural diagrams, and whiteboard images
  - **Apiiro Data Fabric** foundation:
    - **Software Graph™**: continuously maps code architecture, data flows, and dependencies
    - **Risk Graph™**: contextual threat prioritization, blast radius assessment, security control effectiveness
    - **Code-to-Runtime (C2R) Linking**: connects code components to actual runtime exposure
  - Seven-stage pipeline:
    1. **Initiation**: manual (portal/chat), autonomous (ticket monitoring in Jira/GitHub/Azure DevOps), or AI coding assistant trigger
    2. **Contextual Design Analysis**: identifies affected repos/services, detects PII/PHI handling, assesses internet exposure, checks existing auth controls
    3. **Threat Library & Multi-Framework Reasoning**: deterministic library spanning STRIDE, CIA, CAPEC, CWE, OWASP Top 10, MITRE ATT&CK, OWASP ASVS, NIST, ISO 27001 — no developer questionnaires needed
    4. **Contextual Threat & Countermeasure Generation**: evidence-based prioritization with architecture-specific countermeasures referencing exact file paths and line numbers (e.g., "use existing ResponseMiddleware at src/Middleware/ResponseMiddleware.cs:31")
    5. **Implementation Guidance**: tech-stack-specific, encourages reuse of existing security controls, actionable for both human developers and AI coding agents
    6. **Audit Evidence Collection**: living threat models in Data Fabric with ownership tracking, SLA management, exception workflows, full audit trail
    7. **Continuous Validation & Drift Detection** (roadmap): compares design intent against actual implementation during PR review
  - **Guardian Secure Prompt** (patent-pending): enriches AI coding assistant prompts with contextual security and compliance guidance
  - Scales to 100K+ repositories via read-only API
  - Compliance reporting: GDPR, CCPA, SOC 2, PCI v4
- **Methodology Support**: STRIDE, CIA Triad, OWASP Top 10, OWASP ASVS, NIST Controls, ISO 27001, CAPEC, CWE, MITRE ATT&CK (9 frameworks via deterministic library + AI)
- **Integration**: Jira, GitHub, Azure DevOps, IDE extensions (Guardian IDE), GitHub Copilot, Cursor, Claude (via MCP), OpenAI Codex, HashiCorp Vault, Okta
- **Target Audience**: Enterprise AppSec teams; platform engineering teams; organizations deploying AI coding agents at scale
- **Differentiators**: Architecture-grounded in actual code (Software Graph, not static diagrams); contextual countermeasures with specific file locations, line numbers, and code patterns; tech-stack-aligned recommendations reusing existing controls; noise reduction through automatic de-prioritization of mitigated threats; graph-powered blast radius analysis; developer-native (IDE, Copilot, Cursor, MCP integration); patent-pending Secure Prompt capability for AI coding agents; broadest framework coverage (9 standards); only tool linking threat models to runtime exposure via C2R
- **Weaknesses**: Private preview only (not GA as of April 2026); drift detection not yet available; requires deep organizational integration for autonomous operation (repo access, ticketing, runtime data); effectiveness depends on Software Graph coverage of codebase; enterprise pricing unknown; cloud-only (no local-first option); no SARIF output
- **Note**: Apiiro positions this as "design-phase security for the AI coding agent era" — the key innovation is that threat model countermeasures feed directly into AI coding assistant prompts (Cursor, Copilot) as "secure prompts", so generated code inherits security guidance automatically. This is the most direct commercial competitor to tachi's agentic approach, though Apiiro operates at the enterprise platform level while tachi operates at the local analysis level.

---

#### 15. Aristiun

- **Creator**: Aristiun
- **Pricing**: Free tier available; commercial tiers (pricing not published)
- **Website**: https://threat-modeling.com/
- **Key Features**:
  - STRIDE or Risk Assessment approach
  - Questionnaire-based workflow
  - Example use cases
  - Basic application diagram starter
  - AI-powered automated threat modeling
- **Methodology Support**: STRIDE, Risk Assessment
- **Integration**: GitHub Marketplace
- **Target Audience**: Organizations starting threat modeling; healthcare/regulated sectors
- **Differentiators**: Low barrier to entry; provides starter diagrams; questionnaire approach accessible to non-experts
- **Weaknesses**: Limited depth for mature security programs; less feature-rich than enterprise competitors

---

#### 16. Tutamen Threat Model Automator

- **Creator**: Tutamen
- **Pricing**: Commercial (no lock-in license)
- **Website**: SourceForge listing
- **Key Features**:
  - Add threat model metadata to any software diagram
  - Works with existing tools (Microsoft Visio, Excel)
  - CWE-driven threat identification
- **Methodology Support**: STRIDE, OWASP Top 10, CWE
- **Integration**: Microsoft Visio; Microsoft Excel
- **Target Audience**: Teams already using Visio/Excel for architecture documentation
- **Differentiators**: Works with existing diagramming tools rather than requiring a new tool; CWE-driven
- **Weaknesses**: Microsoft-tool dependent; less automated than newer AI-driven tools; limited community visibility

---

### GENERAL DIAGRAMMING TOOLS (Used for Threat Modeling)

---

#### 17. Draw.io / Diagrams.net

- **Pricing**: Free, open-source
- **Website**: https://www.drawio.com/
- **Differentiator**: No signup required; GitHub, GitLab, Atlassian, Microsoft, Google integrations
- **Limitation**: General diagramming; no threat-specific automation, libraries, or scoring

#### 18. Miro

- **Pricing**: Free tier (1 workspace, 3 editable boards); commercial tiers
- **Website**: https://miro.com/
- **Differentiator**: Best for whiteboard-to-digital transition; real-time collaboration
- **Limitation**: Not threat-modeling-specific; no threat libraries or automation

#### 19. Lucidchart

- **Pricing**: Free tier (1 workspace, 60 shapes); commercial tiers
- **Website**: https://www.lucidchart.com/
- **Differentiator**: Role-based content suggestions; specialized network shapes
- **Limitation**: Not threat-modeling-specific; shape limitations on free tier

---

### AI/AGENTIC-SPECIFIC FRAMEWORKS

---

#### 20. MAESTRO Framework

- **Creator**: Ken Huang (DistributedApps.ai) via Cloud Security Alliance
- **Type**: Framework/methodology (not a tool)
- **Published**: February 2025
- **Key Concepts**:
  - Multi-Agent Environment, Security, Threat, Risk, and Outcome
  - Seven-layer reference architecture for agentic AI systems
  - Extended security categories beyond STRIDE for AI-specific threats
  - Multi-agent focus (agent-to-agent interactions)
  - Risk-based prioritization with agent context
  - Continuous monitoring emphasis
- **AI-Specific Threats Covered**: Data poisoning, model extraction, adversarial ML attacks, agent autonomy risks, agent-to-agent collusion, supply chain security, explainability gaps
- **Compatibility**: Designed to augment (not replace) STRIDE, PASTA, LINDDUN, OCTAVE, VAST
- **Relevance to tachi**: Directly relevant as a supplementary framework for agentic AI threat categories; tachi already extends STRIDE with AI-specific threat agents

---

## Comparative Analysis

### Dedicated Threat Modeling Tools

| Criteria | OWASP Threat Dragon | Microsoft TMT | Threagile | pytm | STRIDE-GPT | Precogly | IriusRisk | ThreatModeler | SD Elements / Devici | Apiiro |
|----------|-------------------|---------------|-----------|------|------------|----------|-----------|---------------|---------------------|--------|
| **Cost** | Free | Free | Free | Free | Free | Free | Free-Enterprise | Enterprise | Enterprise | Enterprise |
| **AI-Powered** | No | No | No | No | Yes | No (roadmap) | Partial | Partial | Partial (Devici) | Yes |
| **Agentic AI Support** | No | No | No | No | Yes (ASI01-10) | No (roadmap) | Partial (ML/AI library) | No | No | No |
| **Quantitative Scoring** | No | No | Risk color-coding | No | DREAD scoring | No | Severity levels | Severity levels | Health Score | Graph-based prioritization |
| **Code-First** | No | No | Yes (YAML) | Yes (Python) | No | No | No | No | Partial (CodeGenius) | Yes (Software Graph) |
| **Methodology Breadth** | 5 frameworks | STRIDE only | Custom | STRIDE | STRIDE+DREAD+OWASP | 4 (STRIDE+LINDDUN+ATT&CK+CAPEC) | 4+ frameworks | Multiple | Compliance-based | 6+ frameworks |
| **CI/CD Integration** | Limited | No | Yes | Yes | No | REST API | Yes | Yes | Yes | Yes |
| **Enterprise Scale** | No | No | No | No | No | Yes (collaborative) | Yes | Yes | Yes | Yes |
| **SARIF Output** | No | No | No | No | No | No | No | No | No | No |
| **Local-First** | Yes | Yes | Yes | Yes | Yes (optional) | No (Docker/PostgreSQL) | No | No | No | No |
| **Compliance Mapping** | No | No | No | No | No | Yes (DORA, CRA, NIST CSF, SOC 2) | Yes | Yes | Yes | Yes |

### Scoring/Quantification Approaches Across Tools

| Tool | Scoring Method | Granularity | Automation |
|------|---------------|-------------|------------|
| STRIDE-GPT | DREAD (5 factors, 1-10 scale) | Per-threat | AI-generated |
| IriusRisk | Severity levels + compliance mapping | Per-risk | Rule-based |
| ThreatModeler | Severity classification | Per-threat | Automated |
| Devici | Threat Model Health Score | Per-model | Algorithmic |
| Apiiro | Graph-powered blast radius + multi-framework | Per-finding | AI + graph analysis |
| Threagile | Risk level color-coding | Per-risk | Rule-based |
| Microsoft TMT | Manual severity assignment | Per-threat | Manual |
| **tachi (planned)** | CVSS-aligned composite score (likelihood x impact x exposure) | Per-finding | Formula-based with reachability |

---

## Market Context

- The threat modeling tools market was USD 1.28 billion in 2025, projected at 14.89% CAGR through 2030.
- Cloud-based SaaS held 67.82% market share in 2024, expanding at 15.67% CAGR.
- OWASP released Threat Modeling Methodology v2.0 in May 2025, standardizing guidance on AI system exposure analysis and IaC mapping.
- Generative AI integration is the dominant trend: Apiiro, STRIDE-GPT, Devici (CodeGenius), and ThreatModeler (BYOAI) all ship AI-assisted features.
- No tool currently produces SARIF output for threat model findings -- this is a gap across the entire market.

---

## Key Gaps Across All Tools (tachi Opportunities)

1. **No SARIF output**: No threat modeling tool produces SARIF-format findings for GitHub Code Scanning integration. tachi's dual-format output (markdown + SARIF) is unique.

2. **No composite quantitative scoring**: Most tools use qualitative severity levels or simple DREAD scoring. No tool implements a composite score combining likelihood, impact, and exposure/reachability factors with CVSS alignment. tachi's planned formula-based approach fills this gap.

3. **Limited agentic AI threat coverage**: Only STRIDE-GPT (via OWASP ASI01-10) and IriusRisk (ML/AI library) address AI-specific threats. The MAESTRO framework exists but has no tooling implementation. tachi's STRIDE extension with AI-specific threat agents is differentiated.

4. **No local-first + enterprise-grade scoring**: Enterprise tools (IriusRisk, ThreatModeler, Apiiro) require cloud deployment. Free tools (Threagile, pytm) offer local-first but lack quantitative scoring. tachi combines local-first with quantitative scoring.

5. **No threat-model-to-code-scanning pipeline**: No tool bridges threat modeling output directly into developer code scanning workflows (GitHub Code Scanning, SARIF consumers). tachi's SARIF output creates this bridge.

6. **Reachability/exposure scoring absent**: No tool factors trust zone reachability or exposure surface into risk scores. tachi's planned exposure multiplier based on trust zone tables is novel.

### tachi vs Precogly (Closest OSS Competitor)

Precogly is the closest open-source competitor in ambition (enterprise-grade, compliance-aware) but takes a fundamentally different approach:

| Dimension | **tachi** | **Precogly** |
|-----------|-----------|-------------|
| **Approach** | Agent-driven analysis (LLM agents analyze architecture) | Platform-driven (humans diagram + annotate in web UI) |
| **Deployment** | Local-first, zero infrastructure (just files) | Docker + PostgreSQL + nginx server |
| **Input** | Natural language architecture descriptions | Visual DFD editor (drag-and-drop) |
| **Output** | Markdown + SARIF + PDF reports + infographics | Threat models in database, TM-BOM JSON export |
| **AI Role** | Core — agents generate threats, scores, controls, reports | None yet (AI-ready API on roadmap) |
| **Agentic AI Threats** | Yes — 5 dedicated agents (prompt injection, data poisoning, model theft, tool abuse, agent autonomy) | No |
| **Risk Scoring** | Composite quantitative (CVSS-aligned, 4-dimensional) | No scoring |
| **SARIF Output** | Yes (GitHub Code Scanning integration) | No |
| **Compliance Mapping** | No | Yes (DORA, CRA, NIST CSF, SOC 2, ASVS) |
| **Collaboration** | Single-user / CI pipeline | Multi-user workspaces |
| **Library Packs** | STRIDE + AI extensions | STRIDE, LINDDUN, ATT&CK, CAPEC, cloud packs |
| **Methodology Breadth** | STRIDE + 5 AI-specific categories | 4 frameworks via library packs |

**Summary**: tachi is an *agentic analysis engine* — feed it architecture, agents produce threats, scores, and reports. Precogly is a *collaborative platform* — humans draw DFDs, tag threats from libraries, and map to compliance frameworks. The tools are more complementary than competitive; Precogly's compliance mapping (DORA, CRA, NIST CSF) covers ground tachi doesn't, while tachi's AI/agentic threat coverage, quantitative scoring, and SARIF pipeline are unique. A team could diagram in Precogly and analyze with tachi.

---

## Recommendation

### For tachi's risk scoring feature:

**Primary differentiation points to emphasize**:
- CVSS-aligned composite scoring (no other tool does this for threat model findings)
- SARIF output for GitHub Code Scanning integration (market gap)
- Local-first architecture with quantitative rigor (unique combination)
- AI/agentic threat coverage built into the scoring model
- Reachability-based exposure factor (novel approach)

**Methodologies to reference/align with**:
- STRIDE (core, already supported) -- the dominant methodology across all tools
- DREAD (supplementary) -- familiar scoring framework; STRIDE-GPT demonstrates demand
- OWASP Risk Rating Methodology -- widely recognized, adds credibility
- MAESTRO (supplementary for agentic AI) -- emerging standard, signals forward-thinking

**Approaches to avoid**:
- Do not replicate IriusRisk/ThreatModeler's compliance-library approach (requires massive content investment, not aligned with tachi's methodology focus)
- Do not build diagram-based modeling (well-served market segment)
- Do not require cloud connectivity for scoring (local-first is a differentiator)

**Further research needed**:
- OWASP Threat Modeling Methodology v2.0 (May 2025) AI system exposure analysis guidance
- CVSS v4.0 supplemental metric groups for threat model alignment
- MAESTRO seven-layer architecture mapping to tachi's trust zone model

---

## Sources

### Primary (Tier 1 -- Official Documentation)
- [OWASP Threat Dragon](https://owasp.org/www-project-threat-dragon/)
- [Microsoft Threat Modeling Tool](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool)
- [Threagile](https://threagile.io/)
- [OWASP pytm](https://github.com/OWASP/pytm)
- [CAIRIS](https://cairis.org/)
- [STRIDE-GPT](https://github.com/mrwadams/stride-gpt)
- [AWS Threat Composer](https://awslabs.github.io/threat-composer/)
- [IriusRisk](https://www.iriusrisk.com/)
- [ThreatModeler](https://threatmodeler.com/)
- [SD Elements / Devici](https://www.securitycompass.com/devici/)
- [Apiiro AI Threat Modeling (Blog)](https://apiiro.com/blog/introducing-ai-threat-modeling/)
- [Apiiro Guardian Agent](https://apiiro.com/blog/apiiro-guardian-agent/)
- [Threatspec](https://threatspec.org/)
- [Precogly](https://precogly.org/) | [GitHub](https://github.com/precogly/precogly)
- [MAESTRO Framework (CSA)](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro)

### Secondary (Tier 2 -- Industry Analysis)
- [IriusRisk Blog: Recommended Threat Modeling Tools](https://www.iriusrisk.com/resources-blog/recommended-threat-modeling-tools)
- [Gartner Peer Insights: Threat Modeling Automation](https://www.gartner.com/reviews/market/threat-modeling-automation)
- [Mordor Intelligence: Threat Modeling Tools Market](https://www.mordorintelligence.com/industry-reports/threat-modeling-tools-market)
- [Microsoft Security Blog: Threat Modeling AI Applications (Feb 2026)](https://www.microsoft.com/en-us/security/blog/2026/02/26/threat-modeling-ai-applications/)
- [Apiiro Launch Announcement (Mar 2026)](https://www.globenewswire.com/news-release/2026/03/23/3260417/0/en/Apiiro-Redefines-Design-Phase-Security-with-AI-Threat-Modeling-Built-for-the-AI-Coding-Agent-Era-Preventing-Risks-Before-Code-Exists.html)
- [SD Times: Apiiro AI Threat Modeling for AI Coding Agent Era (Mar 2026)](https://sdtimes.com/security/apiiro-introduces-ai-threat-modeling-built-for-the-ai-coding-agent-era/)
- [Help Net Security: Apiiro AI Threat Modeling (Mar 2026)](https://www.helpnetsecurity.com/2026/03/23/apiiro-ai-threat-modeling/)
- [Security Compass: STRIDE vs LINDDUN vs PASTA](https://www.securitycompass.com/blog/comparing-stride-linddun-pasta-threat-modeling/)
- [Security Compass: Why We Acquired Devici](https://www.securitycompass.com/blog/devici-future-of-threat-modeling/)
- [SecureFlag: Threat Modeling APIs (Jan 2026)](https://blog.secureflag.com/2026/01/20/introducing-threat-modeling-apis/)
- [Vikramaditya Narayan: PASTA vs Component-Driven Threat Modeling (LinkedIn, Apr 2026)](https://www.linkedin.com/posts/vikramadityanarayan_so-you-want-to-scale-up-threat-modeling-in-ugcPost-7446851408429170688-E4VA)
- [Vikramaditya Narayan: ThreatModCon DC Speaker Profile](https://sessionize.com/vikram-s-narayan/)
