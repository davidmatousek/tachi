# Enrichment Brief — tampering

**Agent type**: STRIDE
**Primary threat category**: Tampering (Data Integrity)
**Created**: 2026-04-11
**Feature**: 082 — Threat Agent Skill References

## Candidate New Pattern Categories

### Category 1 — Deserialization Gadget Chains

- **Source**: CWE Top 25 Most Dangerous Software Weaknesses 2024
- **Source citation**: `https://cwe.mitre.org/data/definitions/502.html`
- **Source item**: CWE-502 Deserialization of Untrusted Data (also OWASP Top 10 A08:2021 Software and Data Integrity Failures)
- **Why this category**: Current inline patterns focus on injection but do not cover object deserialization gadget chains (Java, Python pickle, Ruby Marshal, .NET BinaryFormatter, PHP unserialize). This is a known major gap in STRIDE tampering detection.
- **Proposed detection signal**:
  - DFD element accepts serialized objects from an untrusted trust zone (HTTP body, message queue, file upload, cache read)
  - Architecture declares use of Java ObjectInputStream, Python pickle/cloudpickle, Ruby Marshal, or PHP unserialize on cross-boundary data
  - Framework-level auto-deserialization without allowlist (e.g., Jackson default typing, YAML unsafe loader, XStream without security framework)
- **False-positive risk**: Low — untrusted deserialization is a clear high-severity pattern
- **Taxonomy alignment**: STRIDE Tampering; CWE-502, OWASP A08:2021

### Category 2 — Software Supply Chain Integrity Failures

- **Source**: MITRE ATT&CK v15+ (Enterprise)
- **Source citation**: `https://attack.mitre.org/techniques/T1195/`
- **Source item**: T1195 Supply Chain Compromise (sub-techniques .001 Compromise Software Dependencies, .002 Compromise Software Supply Chain, .003 Compromise Hardware Supply Chain)
- **Why this category**: Modern applications pull dependencies at build and runtime; inline patterns miss package-manager tampering, dependency confusion, and typosquatting attacks.
- **Proposed detection signal**:
  - DFD build/deploy pipeline pulls dependencies from public registries (npm, PyPI, crates.io, HuggingFace, DockerHub) without declared lockfile verification or sigstore/SLSA attestation
  - Architecture describes package fetch at runtime (ad-hoc install) rather than baked-into-image
  - Dependency resolution spans mixed public/private registries with known precedence ambiguity (dependency confusion risk)
- **False-positive risk**: Medium — most architectures legitimately use public registries; pattern flags absence of integrity controls
- **Taxonomy alignment**: STRIDE Tampering; OWASP A08:2021 Software and Data Integrity Failures

### Category 3 — Injection Attacks Beyond SQL (OS Command, LDAP, NoSQL, Expression Language)

- **Source**: OWASP Top 10 2021
- **Source citation**: `https://owasp.org/Top10/A03_2021-Injection/`
- **Source item**: A03:2021 Injection (consolidated XSS into Injection in 2021); cross-references CWE-78 OS Command Injection, CWE-90 LDAP Injection, CWE-943 NoSQL Injection, CWE-917 Expression Language Injection
- **Why this category**: Existing patterns commonly cover SQL injection but under-cover the broader injection family. Critical gap for microservice architectures using LDAP, NoSQL stores, and template engines (SSTI).
- **Proposed detection signal**:
  - DFD element constructs queries/commands via string concatenation from untrusted input (OS shell, LDAP filter, MongoDB query, template engine expression)
  - Architecture declares shell-out pattern (`exec`, `system`, `subprocess.shell=True`) in a component that processes external input
  - Template engine with user-controllable templates (Jinja2, Velocity, FreeMarker, Handlebars) declared without sandbox
- **False-positive risk**: Medium — depends on architecture description granularity
- **Taxonomy alignment**: STRIDE Tampering; OWASP A03:2021, multiple CWE family members

## Source Verification Notes

- CWE-502 is at rank 15 in CWE Top 25 2024 — verify rank during Phase 3.2 extraction.
- ATT&CK T1195 has three sub-techniques; all three are valid citations depending on specific detection focus.
- OWASP A08:2021 (Software and Data Integrity Failures) covers both deserialization and supply chain; can cite either A08 or A03 depending on attack vector.
- Checked but NOT used: SLSA framework spec — cited in tampering contexts but is a controls-and-attestation taxonomy, not a detection source per approved set.
