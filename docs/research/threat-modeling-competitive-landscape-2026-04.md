# Threat Modeling Tools: Competitive Landscape Report

**Date**: April 2026
**Scope**: 20 tools and frameworks across free/OSS, commercial, diagramming, and AI/agentic categories
**Purpose**: Standalone competitive intelligence for threat modeling tooling decisions

---

## Executive Summary

The threat modeling tools market reached USD 1.28 billion in 2025 with a projected 14.89% CAGR through 2030. Cloud-based SaaS holds 67.82% market share, but a strong local-first segment persists in the open-source tier.

**Three dominant trends are reshaping the market in 2026:**

1. **AI-powered threat generation** is becoming table stakes. Apiiro, STRIDE-GPT, Devici (CodeGenius), and ThreatModeler all ship AI-assisted features. Precogly has AI on its roadmap.

2. **Agentic AI security** is emerging as a category. Only STRIDE-GPT (OWASP ASI01-10) and IriusRisk (ML/AI library) address AI-specific threats today. The CSA MAESTRO framework provides methodology but has no tooling implementation. Apiiro positions itself for the "AI coding agent era" but focuses on secure prompts rather than agentic threat categories.

3. **No tool produces SARIF output** for integration with GitHub Code Scanning or other SARIF consumers. This remains a market-wide gap.

---

## Market Segmentation

### Tier 1: Free / Open-Source (9 tools)

| Tool | Approach | AI-Powered | Agentic AI | Scoring | Key Strength |
|------|----------|------------|------------|---------|-------------|
| **OWASP Threat Dragon** | Visual diagramming | No | No | Manual | 5 methodology frameworks; OWASP credibility |
| **Microsoft TMT** | Guided diagramming | No | No | Manual | Best for non-security specialists; Azure fit |
| **Threagile** | YAML-as-code | No | No | Color-coded | Developer-centric; CI/CD native |
| **OWASP pytm** | Python-as-code | No | No | None | True code-first; diagrams are outputs |
| **CAIRIS** | Requirements + security | No | No | None | 12 system views; GDPR DPIA generation |
| **STRIDE-GPT** | LLM-powered analysis | Yes | Yes (ASI01-10) | DREAD | Multi-LLM; most comprehensive OSS AI tool |
| **Threatspec** | Code annotations | No | No | None | Threat models co-located with source code |
| **AWS Threat Composer** | Statement authoring | No | No | None | Privacy-first; fully local |
| **Precogly** | Collaborative platform | No (roadmap) | No (roadmap) | None | Compliance mapping (DORA, CRA, NIST CSF); library packs |

**Key observations:**
- STRIDE-GPT is the only free tool with both AI generation and agentic AI threat coverage
- Precogly is the only free tool with built-in compliance mapping (DORA, CRA, NIST CSF, SOC 2)
- Threagile and pytm own the "threat-modeling-as-code" niche
- No free tool offers composite quantitative risk scoring
- No free tool produces SARIF output

### Tier 2: Commercial / Enterprise (7 tools)

| Tool | Approach | AI-Powered | Pricing | Key Strength |
|------|----------|------------|---------|-------------|
| **IriusRisk** | Library + diagramming | Partial | Free-Enterprise | Broadest methodology support (STRIDE, TRIKE, OCTAVE, PASTA); ML/AI library |
| **ThreatModeler** | Unified platform | Partial (BYOAI) | Enterprise | App + cloud + IaC unified; 2,500+ requirements |
| **SD Elements** | Questionnaire-driven | Partial | Enterprise | Dominant in federal/military; compliance-first |
| **Devici** | Diagram-first + AI | Yes (CodeGenius) | Free tier-Enterprise | Text-to-DFD; source-code-to-threat-model; Health Score |
| **Apiiro** | Autonomous agent | Yes (Guardian Agent) | Enterprise (preview) | Architecture-grounded via Software Graph; 9 frameworks; Secure Prompt for AI coding agents |
| **Aristiun** | Questionnaire-based | Yes | Free tier-Commercial | Low barrier to entry |
| **Tutamen** | Diagram metadata | No | Commercial | Works with existing Visio/Excel tools |

**Key observations:**
- Apiiro is the most technically ambitious, with a 7-stage autonomous pipeline and patent-pending Secure Prompt technology
- IriusRisk has the broadest methodology support among commercial tools
- ThreatModeler is the only platform unifying application, cloud, and infrastructure threat modeling
- SD Elements / Devici (Security Compass) dominate the federal compliance market
- No commercial tool produces SARIF output either

### Tier 3: General Diagramming (3 tools)

Draw.io, Miro, and Lucidchart are commonly used for threat modeling but lack threat-specific automation, libraries, or scoring. They serve as drawing tools, not analysis tools.

### Tier 4: AI/Agentic Frameworks (1 framework)

**MAESTRO** (Cloud Security Alliance, Feb 2025) defines a 7-layer reference architecture for agentic AI systems with extended threat categories (data poisoning, model extraction, agent autonomy risks, agent-to-agent collusion). Designed to augment STRIDE/PASTA/LINDDUN, not replace them. No tooling implementation exists.

---

## Comparative Matrix: Dedicated Tools

| Criteria | Threat Dragon | Microsoft TMT | Threagile | pytm | STRIDE-GPT | Precogly | IriusRisk | ThreatModeler | Devici | Apiiro |
|----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Cost** | Free | Free | Free | Free | Free | Free | Free-Ent | Ent | Free-Ent | Ent |
| **AI-Powered** | - | - | - | - | Yes | Roadmap | Partial | Partial | Yes | Yes |
| **Agentic AI** | - | - | - | - | Yes | - | Partial | - | - | - |
| **Quant. Scoring** | - | - | Colors | - | DREAD | - | Severity | Severity | Health | Graph |
| **Code-First** | - | - | YAML | Python | - | - | - | - | Partial | Yes |
| **Methodology Breadth** | 5 | 1 | Custom | 1 | 4+ | 4 | 4+ | Multi | 1+ | 9 |
| **CI/CD** | Limited | - | Yes | Yes | - | API | Yes | Yes | Yes | Yes |
| **Enterprise Scale** | - | - | - | - | - | Yes | Yes | Yes | Yes | Yes |
| **SARIF Output** | - | - | - | - | - | - | - | - | - | - |
| **Local-First** | Yes | Yes | Yes | Yes | Yes | - | - | - | - | - |
| **Compliance** | - | - | - | - | - | Yes | Yes | Yes | Yes | Yes |

---

## Scoring & Quantification Approaches

| Tool | Method | Granularity | Automation |
|------|--------|-------------|------------|
| STRIDE-GPT | DREAD (5 factors, 1-10 scale) | Per-threat | AI-generated |
| IriusRisk | Severity levels + compliance mapping | Per-risk | Rule-based |
| ThreatModeler | Severity classification | Per-threat | Automated |
| Devici | Threat Model Health Score | Per-model | Algorithmic |
| Apiiro | Graph-powered blast radius + multi-framework | Per-finding | AI + graph |
| Threagile | Risk level color-coding | Per-risk | Rule-based |
| Microsoft TMT | Manual severity assignment | Per-threat | Manual |

**Gap**: No tool implements composite quantitative scoring combining likelihood, impact, and exposure/reachability factors with CVSS alignment.

---

## Market Gaps (Opportunity Areas)

| # | Gap | Coverage Today |
|---|-----|---------------|
| 1 | **SARIF output** for code scanning integration | Zero tools (entire market) |
| 2 | **Composite quantitative scoring** (CVSS-aligned) | No tool; closest is STRIDE-GPT's DREAD |
| 3 | **Agentic AI threat categories** | STRIDE-GPT (ASI01-10), IriusRisk (partial); MAESTRO is framework-only |
| 4 | **Local-first + enterprise-grade scoring** | Free tools are local but lack scoring; enterprise tools score but require cloud |
| 5 | **Threat-model-to-code-scanning pipeline** | No tool bridges threat findings into developer scanning workflows |
| 6 | **Reachability/exposure scoring** | No tool factors trust zone reachability into risk scores |
| 7 | **Compliance mapping in OSS** | Only Precogly; all others are commercial |

---

## Competitive Threat Assessment

### Primary Threats

**Apiiro** (Commercial)
- Most technically ambitious entrant. 7-stage autonomous pipeline, patent-pending Secure Prompt for AI coding agents, 9 framework coverage, Software Graph grounded in actual code.
- Targets the same "AI coding agent era" positioning.
- Weakness: Enterprise-only, cloud-only, not GA (private preview), no SARIF, pricing unknown.

**STRIDE-GPT** (Free/OSS)
- Most popular AI-powered open-source tool (999 GitHub stars). Multi-LLM support, DREAD scoring, agentic AI coverage (OWASP ASI01-10).
- Direct mindshare competitor in the OSS space.
- Weakness: Single-shot generation (no multi-agent pipeline), no SARIF, no compensating controls analysis, no PDF/infographic output.

### Secondary Threats

**IriusRisk** (Commercial)
- Broadest methodology support (STRIDE, TRIKE, OCTAVE, PASTA). ML/AI threat library. Free community tier.
- Established market leader with Gartner/G2 presence.
- Weakness: Enterprise-focused, no agentic AI categories, no SARIF.

**Precogly** (Free/OSS)
- Enterprise ambitions with compliance mapping (DORA, CRA, NIST CSF). Creator actively researching multi-agent threat modeling.
- Weakness: Very early (48 GitHub stars), no AI generation yet, requires Docker/PostgreSQL.

**Devici / Security Compass** (Commercial)
- CodeGenius (source-code-to-threat-model) and AI Diagram Assistant are innovative.
- Federal/military market dominance through SD Elements.
- Weakness: Recently acquired, integration maturing, no agentic AI focus.

### Low Threats

| Tool | Why Low Threat |
|------|---------------|
| Microsoft TMT | Stagnant; Windows-only; no AI |
| Threagile | Niche (YAML-as-code); no AI; small community |
| pytm | Niche (Python-only); no scoring |
| ThreatModeler | Enterprise-only; opaque; no agentic AI |
| AWS Threat Composer | Minimal; no automation; AWS-centric |
| CAIRIS | Academic; complex setup |
| Threatspec | Niche (code annotations); tiny community |
| Aristiun | Limited depth |
| Tutamen | Microsoft-tool dependent |

---

## Key Differentiators to Defend

Any tool competing in this space should consider which of these capabilities create defensible positioning:

| Differentiator | Who Has It | Rarity |
|---------------|-----------|--------|
| SARIF output for code scanning | Nobody | Unique gap |
| Composite CVSS-aligned scoring | Nobody | Unique gap |
| Agentic AI threat agents (dedicated) | STRIDE-GPT (partial) | Rare |
| Local-first + quantitative scoring | Nobody | Unique combination |
| Threat-to-code-scanning pipeline | Nobody | Unique gap |
| Reachability/exposure scoring | Nobody | Novel |
| Architecture-grounded analysis (actual code) | Apiiro | Rare (enterprise-only) |
| Compliance mapping (OSS) | Precogly | Rare |
| Multi-agent analysis pipeline | Nobody (STRIDE-GPT is single-shot) | Unique |
| PDF report + infographic generation | Nobody | Unique |

---

## Sources

### Primary (Official Documentation)
- [OWASP Threat Dragon](https://owasp.org/www-project-threat-dragon/)
- [Microsoft Threat Modeling Tool](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool)
- [Threagile](https://threagile.io/)
- [OWASP pytm](https://github.com/OWASP/pytm)
- [CAIRIS](https://cairis.org/)
- [STRIDE-GPT](https://github.com/mrwadams/stride-gpt)
- [AWS Threat Composer](https://awslabs.github.io/threat-composer/)
- [Precogly](https://precogly.org/) | [GitHub](https://github.com/precogly/precogly)
- [IriusRisk](https://www.iriusrisk.com/)
- [ThreatModeler](https://threatmodeler.com/)
- [SD Elements / Devici](https://www.securitycompass.com/devici/)
- [Apiiro AI Threat Modeling](https://apiiro.com/blog/introducing-ai-threat-modeling/)
- [Apiiro Guardian Agent](https://apiiro.com/blog/apiiro-guardian-agent/)
- [Threatspec](https://threatspec.org/)
- [MAESTRO Framework (CSA)](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro)

### Secondary (Industry Analysis)
- [Gartner Peer Insights: Threat Modeling Automation](https://www.gartner.com/reviews/market/threat-modeling-automation)
- [Mordor Intelligence: Threat Modeling Tools Market](https://www.mordorintelligence.com/industry-reports/threat-modeling-tools-market)
- [Microsoft Security Blog: Threat Modeling AI Applications (Feb 2026)](https://www.microsoft.com/en-us/security/blog/2026/02/26/threat-modeling-ai-applications/)
- [SD Times: Apiiro AI Threat Modeling (Mar 2026)](https://sdtimes.com/security/apiiro-introduces-ai-threat-modeling-built-for-the-ai-coding-agent-era/)
- [Help Net Security: Apiiro AI Threat Modeling (Mar 2026)](https://www.helpnetsecurity.com/2026/03/23/apiiro-ai-threat-modeling/)
- [Apiiro Launch Announcement (Mar 2026)](https://www.globenewswire.com/news-release/2026/03/23/3260417/0/en/Apiiro-Redefines-Design-Phase-Security-with-AI-Threat-Modeling-Built-for-the-AI-Coding-Agent-Era-Preventing-Risks-Before-Code-Exists.html)
- [Security Compass: STRIDE vs LINDDUN vs PASTA](https://www.securitycompass.com/blog/comparing-stride-linddun-pasta-threat-modeling/)
- [Security Compass: Why We Acquired Devici](https://www.securitycompass.com/blog/devici-future-of-threat-modeling/)
- [SecureFlag: Threat Modeling APIs (Jan 2026)](https://blog.secureflag.com/2026/01/20/introducing-threat-modeling-apis/)
- [IriusRisk Blog: Recommended Threat Modeling Tools](https://www.iriusrisk.com/resources-blog/recommended-threat-modeling-tools)
- [Vikramaditya Narayan: PASTA vs Component-Driven Threat Modeling (LinkedIn, Apr 2026)](https://www.linkedin.com/posts/vikramadityanarayan_so-you-want-to-scale-up-threat-modeling-in-ugcPost-7446851408429170688-E4VA)
- [Vikramaditya Narayan: ThreatModCon DC Speaker Profile](https://sessionize.com/vikram-s-narayan/)

---

*Report compiled April 2026. Market data from Mordor Intelligence (2025 figures). Tool capabilities verified against official documentation and public announcements.*
