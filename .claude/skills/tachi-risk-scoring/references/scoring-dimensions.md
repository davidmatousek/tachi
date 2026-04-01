---
source_agent: risk-scorer
extracted_from: .claude/agents/tachi/risk-scorer.md
version: 1.0.0
---

# Scoring Dimensions Reference

Domain knowledge for three of the four risk scoring dimensions: exploitability, scalability, and reachability. CVSS 3.1 base scoring has its own reference file (`cvss-vectors.md`).

---

## Exploitability Assessment

Assess how easily each threat can be exploited in practice. This dimension captures operational attack feasibility that CVSS base scores do not fully reflect -- particularly for AI-specific threats where novel attack techniques may not map to traditional vulnerability patterns.

### Sub-Dimensions

Evaluate four sub-dimensions, each scored 0-10. The exploitability score is the **average** of the four sub-dimensions, rounded to one decimal place.

**`Exploitability = (Known Techniques + Attack Complexity + Tooling Availability + Skill Level) / 4`**

| Sub-Dimension | 0-3 (Low) | 4-6 (Medium) | 7-10 (High) |
|---------------|-----------|--------------|-------------|
| **Known Techniques** | No known exploits; theoretical only; requires novel research | PoC exists but not weaponized; technique documented in academic papers | Active exploitation in the wild; public exploit code available; CISA KEV listed |
| **Attack Complexity** | Requires chaining multiple vulnerabilities, precise timing, or rare conditions | Single vulnerability but needs specific configuration or version | Simple single-step exploitation; no special conditions needed |
| **Tooling Availability** | Requires custom exploit development from scratch | Open-source tools exist but need modification or expertise to operate | Off-the-shelf tools (Metasploit, Burp, nuclei) with ready-made modules |
| **Skill Level** | Requires deep expertise (firmware RE, cryptanalysis, ML model internals) | Intermediate attacker with scripting and common tool proficiency | Script-kiddie level; copy-paste exploits; no specialized knowledge |

**Inversion note**: Attack Complexity and Skill Level use an inverted scale where *low complexity/skill = high exploitability score*. A trivially simple attack with no skill requirement scores 9-10 on both sub-dimensions.

### AI-Specific Exploitability Guidance

| AI Threat Type | Known Techniques | Complexity | Tooling | Skill | Typical Score |
|----------------|-----------------|------------|---------|-------|---------------|
| **Direct prompt injection** | 9 (extensively documented) | 9 (simple text input) | 8 (many prompt injection tools) | 9 (no special skills) | 8.8 |
| **Indirect prompt injection (RAG)** | 7 (growing body of research) | 6 (requires knowledge base access) | 5 (limited specialized tooling) | 6 (moderate understanding needed) | 6.0 |
| **Agent autonomy abuse** | 6 (emerging research area) | 5 (needs understanding of agent capabilities) | 4 (mostly manual testing) | 5 (moderate agent knowledge needed) | 5.0 |
| **Tool abuse / capability escalation** | 5 (limited public research) | 6 (requires understanding tool APIs) | 3 (no standard tooling) | 6 (needs API expertise) | 5.0 |
| **Model extraction / theft** | 6 (academic papers available) | 7 (requires many queries but straightforward) | 5 (custom scripts needed) | 7 (ML knowledge helpful but not required) | 6.3 |
| **Data poisoning** | 4 (limited practical examples) | 3 (requires privileged data pipeline access) | 2 (custom attack development) | 3 (requires ML expertise) | 3.0 |

These values are guidance baselines. Adjust per-finding based on the specific threat description -- a prompt injection attack on a public-facing endpoint with no input filtering scores higher than one behind authentication with content filtering.

---

## Scalability Assessment

Assess how well the attack scales -- whether it can be automated, how many targets it affects, what resources are needed, and how likely it is to be detected. Scalability captures the blast radius and operational economics of exploitation that CVSS does not address.

### Sub-Dimensions

Evaluate four sub-dimensions, each scored 0-10. The scalability score is the **average** of the four sub-dimensions, rounded to one decimal place.

**`Scalability = (Scriptability + Target Scope + Resource Requirements + Detection Difficulty) / 4`**

| Sub-Dimension | 0-3 (Low) | 4-6 (Medium) | 7-10 (High) |
|---------------|-----------|--------------|-------------|
| **Scriptability** | Requires manual, hands-on exploitation for each target; cannot be scripted | Partially automatable; requires manual setup but repeated execution can be scripted | Fully automatable end-to-end; exploit can run unattended against many targets |
| **Target Scope** | Single specific target; requires precise configuration knowledge per victim | Category of targets (e.g., all instances running a specific version) | Universal; affects all instances of the component regardless of configuration |
| **Resource Requirements** | Requires significant infrastructure (botnet, compute cluster, specialized hardware) | Moderate resources (cloud VM, moderate bandwidth, standard hardware) | Minimal resources (laptop, basic internet connection, no special infrastructure) |
| **Detection Difficulty** | Easily detected; triggers immediate alerts; leaves obvious forensic evidence | Detectable with purpose-built monitoring; may evade basic logging | Difficult to detect; blends with legitimate traffic; minimal forensic artifacts |

**Inversion note**: Resource Requirements uses an inverted scale where *low resources needed = high scalability score*. An attack requiring only a laptop and internet connection scores 8-10.

### Scoring Examples by Threat Category

| Category | Typical Scriptability | Typical Target Scope | Typical Resources | Typical Detection | Typical Score |
|----------|----------------------|---------------------|-------------------|-------------------|---------------|
| Spoofing (credential replay) | 8 (easily scripted) | 6 (affects users with weak tokens) | 8 (minimal resources) | 5 (moderate detection) | 6.8 |
| Tampering (data modification) | 5 (depends on access path) | 4 (specific data stores) | 7 (minimal resources) | 4 (detectable with integrity monitoring) | 5.0 |
| Repudiation (audit evasion) | 3 (manual exploitation typical) | 3 (specific audit systems) | 8 (minimal resources) | 7 (hard to detect by definition) | 5.3 |
| Info-disclosure (data exposure) | 7 (API scraping is automatable) | 6 (all users of the endpoint) | 8 (minimal resources) | 4 (detectable via access patterns) | 6.3 |
| Denial-of-service (resource exhaustion) | 9 (highly scriptable) | 8 (all service consumers) | 5 (moderate bandwidth needed) | 3 (easily detected) | 6.3 |
| Privilege-escalation (IDOR/RBAC bypass) | 6 (automatable with enumeration) | 5 (users with same role boundary) | 8 (minimal resources) | 5 (moderate detection) | 6.0 |
| Agentic (autonomy abuse) | 4 (requires prompt crafting) | 5 (all agent instances) | 8 (minimal resources) | 6 (hard to distinguish from normal use) | 5.8 |
| LLM (prompt injection) | 7 (easily repeated) | 7 (all model-facing endpoints) | 9 (text input only) | 6 (hard to detect without specialized monitoring) | 7.3 |

These values are guidance baselines. Adjust per-finding based on the specific attack described.

---

**Note**: Reachability analysis has been extracted to its own reference file: `reachability-analysis.md`. Load that file when entering the reachability assessment phase (Section 6).

