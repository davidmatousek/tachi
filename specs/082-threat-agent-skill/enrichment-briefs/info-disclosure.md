# Enrichment Brief — info-disclosure

**Agent type**: STRIDE
**Primary threat category**: Information Disclosure (Confidentiality)
**Created**: 2026-04-11
**Feature**: 082 — Threat Agent Skill References

## Candidate New Pattern Categories

### Category 1 — SSRF to Cloud Metadata and Internal Services

- **Source**: OWASP Top 10 2021
- **Source citation**: `https://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/`
- **Source item**: A10:2021 Server-Side Request Forgery (new dedicated category in 2021); cross-references CWE-918 SSRF
- **Why this category**: SSRF against cloud metadata endpoints (IMDSv1 at `169.254.169.254`) is the most-reported cloud confidentiality breach pattern. Current inline patterns treat it as a footnote to general disclosure.
- **Proposed detection signal**:
  - DFD element makes outbound HTTP requests to URLs derived from user input (webhooks, image fetch, URL previews, PDF rendering, proxying)
  - Cloud workload uses IMDSv1 rather than IMDSv2 (declared via instance metadata version)
  - No declared egress allowlist or denylist for RFC1918/link-local addresses
  - Component proxies or fetches on behalf of users (URL preview, screenshot service, RSS aggregator)
- **False-positive risk**: Low — when user-controlled URL fetch is declared, SSRF risk is concrete
- **Taxonomy alignment**: STRIDE Information Disclosure; OWASP A10:2021, CWE-918

### Category 2 — Information Exposure Through Error Messages and Debug Output

- **Source**: CWE Top 25 Most Dangerous Software Weaknesses 2024
- **Source citation**: `https://cwe.mitre.org/data/definitions/209.html`
- **Source item**: CWE-209 Generation of Error Message Containing Sensitive Information; related CWE-200 Exposure of Sensitive Information to an Unauthorized Actor (rank 17 on 2024 Top 25)
- **Why this category**: Inline patterns mention error exposure but do not differentiate stack trace leakage, verbose error messages in HTTP responses, debug endpoints left enabled, or source-map leakage in minified frontend bundles.
- **Proposed detection signal**:
  - Component declares debug/verbose error mode enabled in production (or no declared distinction between dev and prod error handling)
  - DFD element returns framework-default error pages (Django debug page, Flask debugger, ASP.NET Yellow Screen of Death, Rails error page) to external trust zones
  - Frontend bundle published with source maps to public trust zone without access control
  - API returns detailed SQL/ORM error messages on query failure
- **False-positive risk**: Medium — depends on declared environment separation
- **Taxonomy alignment**: STRIDE Information Disclosure; CWE-209, CWE-200, CWE-215 Insertion of Sensitive Information into Debugging Code

### Category 3 — Data Staging and Collection from Information Repositories

- **Source**: MITRE ATT&CK v15+ (Enterprise)
- **Source citation**: `https://attack.mitre.org/techniques/T1213/`
- **Source item**: T1213 Data from Information Repositories (sub-techniques .001 Confluence, .002 SharePoint, .003 Code Repositories, .005 Messaging Applications); related T1005 Data from Local System
- **Why this category**: Shared knowledge repositories (wikis, chat, code repos) are increasingly the source-of-truth store and are under-represented as threat surfaces in STRIDE implementations.
- **Proposed detection signal**:
  - DFD element is an internal knowledge repository (Confluence, SharePoint, Notion, Slack/Teams, GitLab/GitHub, Jira) with broad read permissions
  - Repository lacks declared data classification or sensitivity labeling
  - Search/indexing component has elevated read permissions spanning multiple zones
  - Bot or service account with read access to repositories for agentic assistance
- **False-positive risk**: Medium — most orgs intentionally permit broad internal read access
- **Taxonomy alignment**: STRIDE Information Disclosure; ATT&CK TA0009 Collection tactic

## Source Verification Notes

- CWE-200 ranks at 17 on CWE Top 25 2024 list — verify exact position during Phase 3.2 extraction.
- OWASP A10:2021 SSRF was a new dedicated category in 2021 (previously distributed across other categories) — a clean citation.
- IMDSv1 vs IMDSv2 distinction is AWS-specific; equivalent concepts exist on Azure (IMDS) and GCP (metadata server) — phrase generically during extraction.
- ATT&CK T1213 sub-techniques are updated regularly; general T1213 citation is stable.
- Checked but NOT used: OWASP A01:2021 Broken Access Control — overlaps with privilege-escalation agent; avoid double-counting there.
