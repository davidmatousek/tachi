# Enrichment Brief — repudiation

**Agent type**: STRIDE
**Primary threat category**: Repudiation (Non-repudiation / Audit Trail)
**Created**: 2026-04-11
**Feature**: 082 — Threat Agent Skill References

## Candidate New Pattern Categories

### Category 1 — Security Logging and Monitoring Failures

- **Source**: OWASP Top 10 2021
- **Source citation**: `https://owasp.org/Top10/A09_2021-Security_Logging_and_Monitoring_Failures/`
- **Source item**: A09:2021 Security Logging and Monitoring Failures (promoted from OWASP Top 10 2017 A10)
- **Why this category**: Repudiation is historically under-documented in STRIDE implementations; OWASP A09 provides canonical pattern language for unlogged privileged actions, which is missing from inline patterns.
- **Proposed detection signal**:
  - DFD element performs privileged operation (authentication, authorization grant, financial transaction, configuration change, PII access) without declared audit event emission
  - Logs are written to local filesystem only (no central aggregation, no WORM/append-only store)
  - Log fields lack actor identity, action type, timestamp, request correlation ID, or outcome
- **False-positive risk**: Medium — architectures often under-specify logging; pattern flags absence, which may represent under-documentation rather than actual absence
- **Taxonomy alignment**: STRIDE Repudiation; OWASP A09:2021; CWE-778 Insufficient Logging

### Category 2 — Indicator Removal / Log Tampering

- **Source**: MITRE ATT&CK v15+ (Enterprise)
- **Source citation**: `https://attack.mitre.org/techniques/T1070/`
- **Source item**: T1070 Indicator Removal (sub-techniques .001 Clear Windows Event Logs, .002 Clear Linux/Mac System Logs, .006 Timestomp, .008 Clear Mailbox Data)
- **Why this category**: Post-compromise log destruction is a distinct repudiation vector that inline patterns treat as a footnote. ATT&CK provides the authoritative technique catalog.
- **Proposed detection signal**:
  - DFD log store is writable by the same identity that produces audit events (no write-once / append-only enforcement)
  - Log rotation or retention policy declared without immutable-store backing (e.g., S3 Object Lock, Azure Immutable Blob Storage)
  - Logs stored in same trust zone as the component being audited (no off-box forwarding)
  - Timestamp source is attacker-controllable (local clock without NTP or signed timestamps)
- **False-positive risk**: Low — lack of log immutability is a concrete repudiation gap
- **Taxonomy alignment**: STRIDE Repudiation; ATT&CK TA0005 Defense Evasion tactic

### Category 3 — Insufficient Log Output Neutralization (Log Injection)

- **Source**: CWE Top 25 Most Dangerous Software Weaknesses 2024
- **Source citation**: `https://cwe.mitre.org/data/definitions/117.html`
- **Source item**: CWE-117 Improper Output Neutralization for Logs
- **Why this category**: Log injection is a repudiation vector distinct from log deletion — attackers can forge log entries to implicate innocent parties or obscure their own actions. Not represented in inline patterns.
- **Proposed detection signal**:
  - DFD element writes user-controlled input directly to audit log (CRLF, ANSI escape, or structured log format) without neutralization
  - Log consumer parses structured logs (JSON/CEF/LEEF) without schema validation
  - Log query interface allows user-controlled filter expressions (risk of log-search evasion)
- **False-positive risk**: Medium — architectures rarely declare log sanitization practices explicitly
- **Taxonomy alignment**: STRIDE Repudiation; CWE-117

## Source Verification Notes

- NIST SP 800-53 Rev 5 AU-family controls (AU-2 Event Logging, AU-9 Protection of Audit Information, AU-10 Non-Repudiation, AU-11 Audit Record Retention) are the controls-side counterparts — per approved source set, these are reference-only and not used as detection-pattern sources here.
- OWASP A09 historically received less community attention than other OWASP categories; primary-source content is thinner than A01 or A03, but canonical URL is stable.
- CWE-778 (Insufficient Logging) is listed on CWE Top 25 watch list historically; verify current ranking during Phase 3.2 extraction.
- Checked but NOT used: CIS Benchmarks logging chapters — operational guidance, not a detection taxonomy.
