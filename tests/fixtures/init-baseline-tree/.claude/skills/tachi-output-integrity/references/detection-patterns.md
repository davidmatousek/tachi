---
name: output-integrity-detection-patterns
description: Externalized detection pattern catalog for LLM output-handling threats — XSS/DOM, server-side execution, SSRF, template injection, path traversal
consumers: [tachi-output-integrity]
last_updated: 2026-04-22
---

# Output Integrity Detection Patterns

## Overview

Detection vocabulary for OWASP LLM05:2025 Improper Output Handling. Loaded at detection start by `tachi-output-integrity` agent via a single `**MANDATORY**: Read` directive. Scope is the **encoding/sanitization signal class** — bytes, strings, and syntax primitives on LLM output flowing into downstream execution sinks. The catalog covers five pattern categories: Client-Side Execution Sinks (XSS/DOM), Server-Side Execution Sinks (SQLi/OS Command/Code), SSRF from LLM-Synthesized URLs, Template/Expression Injection, and Path Traversal + Unsafe File Writes.

**Documentation-only OWASP bundle per ADR-030 Decision 4 and BLP-01 §4**: this agent documents both OWASP LLM05:2025 (Improper Output Handling, 2025 OWASP LLM Top 10) and OWASP ML09:2023 (Output Integrity Attack, 2023 OWASP ML Top 10) as the two framework references describing this underlying threat class. `source_attribution` citations on emitted findings carry OWASP LLM05 only (plus applicable CWEs) because ML09 is not present in the F-A1 catalog at `schemas/taxonomy/owasp.yaml`; adopters see both framework IDs in prose documentation without triggering F-A2 referential-integrity validation failures.

**Out-of-scope (forward-referenced to F-4 per ADR-030 Decision 2)**: psychology/linguistics primitives on human-facing LLM output — manipulative tone, fabricated authority, absence of uncertainty disclaimers. ASI09:2026 Human-Agent Trust Exploitation is owned by the future `trust-exploitation` agent. This agent MUST emit zero findings on architectures whose only output-handling concern is human-trust exploitation without a downstream-execution-sink pathway.

## Detection Scope

### Trigger Keywords

This agent activates when a DFD element name or description matches any of the following patterns (case-insensitive) AND at least one structural downstream-sink indicator is present (both-keyword-AND-sink-indicator rule per FR-011):

- `LLM output`
- `rendered HTML`
- `model output to browser`
- `model output to SQL`
- `LLM-generated query`
- `template engine`
- `outbound HTTP from agent`
- `LLM-synthesized URL`
- `command construction`
- `file path from model`

The structural downstream-sink indicator is a data flow from an LLM Process into one of: browser rendering surface, SQL client, OS-level command invocation, code evaluator, HTTP client, or filesystem writer. A keyword match without a corresponding sink indicator does NOT activate the agent — this guards against false positives on architectures that describe LLM output abstractly without a concrete execution-sink destination.

### Applicable DFD Element Types

- **Process**: Any process node that invokes an LLM AND routes its output into a downstream execution sink. This is the ONLY applicable DFD element type per ADR-030 Decision 1 + Q3 (`dfd_targets: [Process]` metadata).

## Detection Patterns

### 1. Client-Side Execution Sinks (XSS / DOM Injection)

LLM output rendered as HTML, JavaScript, or DOM-manipulating content in a user's browser without contextual output encoding, CSP protection, or safe DOM APIs. Execution context is **client-side**: the payload runs in the victim user's browser under the application's origin, with access to session cookies, CSRF tokens, and downstream user-authenticated APIs.

**Primary citation**: `{taxonomy: owasp, id: LLM05, relationship: primary}`
**Related citation**: `{taxonomy: cwe, id: CWE-79, relationship: related}` (Improper Neutralization of Input During Web Page Generation)

**Trigger keywords**: `LLM output`, `rendered HTML`, `model output to browser`

**Applicable DFD element types**: Process

**Indicators**:
- LLM output rendered via `innerHTML`, `dangerouslySetInnerHTML`, or equivalent string-to-DOM conversion without escaping
- Absence of framework-native escape helpers (React default interpolation `{value}`, Vue `v-text`, Django auto-escape)
- No Content Security Policy declared, or CSP declared with `unsafe-inline` / `unsafe-eval` directives
- Model-generated content interpolated into HTML templates that then return via web response
- Chat or Q&A surfaces that render Markdown from LLM output without sanitizing embedded HTML / `<script>` tags

**Worked Example** (server-side execution context: tachi's server renders HTML; client-side execution context: the victim's browser):
- **Finding**: LLM-powered customer support widget renders model responses as raw HTML in the chat bubble DOM. An attacker primes the model via a prior conversation turn to emit `<img src=x onerror="fetch('/session')...">`; when rendered client-side, the payload exfiltrates session cookies to the attacker's callback URL.
- **Mitigation**: Apply HTML entity encoding on all model output before rendering — use `textContent` not `innerHTML`, React `{value}` not `dangerouslySetInnerHTML`, Django auto-escape `{{ value }}` not `{{ value|safe }}`. Layer a Content Security Policy with strict directives (`default-src 'self'`; `script-src 'self' 'nonce-<nonce>'`; no `unsafe-inline` / `unsafe-eval`). Do NOT rely on post-hoc string sanitization as the primary control — encoding at render-time is the invariant.

### 2. Server-Side Execution Sinks (SQLi / OS Command / Code Injection)

LLM output passed as SQL fragments, shell command components, or code evaluator input without parameterization, safe argument vectors, or sandboxed execution. Execution context is **server-side**: the payload runs on tachi's server (or the adopter's backend), with access to the database, filesystem, network, and process credentials the backend service holds.

**Primary citation**: `{taxonomy: owasp, id: LLM05, relationship: primary}`
**Related citations**: `{taxonomy: cwe, id: CWE-89, relationship: related}` (SQL Injection), `{taxonomy: cwe, id: CWE-78, relationship: related}` (OS Command Injection), `{taxonomy: cwe, id: CWE-94, relationship: related}` (Code Injection)

**Trigger keywords**: `model output to SQL`, `LLM-generated query`, `command construction`

**Applicable DFD element types**: Process

**Indicators**:
- LLM output concatenated into SQL strings via string interpolation (`f"SELECT * FROM {table}"`) rather than parameterized-query placeholders
- Shell commands built by string concatenation with model output then passed to `shell=True`, `os.system`, or equivalent
- Code evaluators (`eval`, `exec`, `Function()`, `vm.runInContext`, `subprocess` with `shell=True`) invoked on model output
- Database ORM bypasses using raw SQL with model-generated fragments (e.g., `db.execute(raw_sql_from_model)`)
- Absence of allowlist validation on model output against a closed enum (e.g., table names, command verbs) before injection into execution contexts

**Worked Example** (server-side execution context explicit):
- **Finding**: Natural-language-to-SQL translator concatenates LLM-generated WHERE clauses into a SQL query string executed by the backend database client. Adversarial user prompt induces the model to emit `' OR 1=1; DROP TABLE users; --`; when server-side executed, arbitrary SQL runs under the service account, enabling data exfiltration or destruction.
- **Mitigation**: Use parameterized SQL queries exclusively — SQLAlchemy `text(sql).bindparams()`, psycopg2 `cursor.execute(sql, params)`, Django ORM `.filter(**params)`. Apply JSON string escaping when the model emits JSON-formatted queries; construct OS command invocations via argument-vector form only (`subprocess.run([cmd, arg1, arg2], shell=False)`). Where enumerable inputs are required (table name, sort column), validate the model output against a closed allowlist before insertion.

### 3. SSRF from LLM-Synthesized URLs

LLM output used to construct outbound HTTP requests without URL allowlisting, scheme validation, or egress firewall protection. An attacker prompts the model to synthesize a URL targeting internal services (cloud metadata endpoints, internal admin APIs, RFC 1918 private IPs) that the server-side HTTP client then fetches with server-side credentials and network reach.

**Primary citation**: `{taxonomy: owasp, id: LLM05, relationship: primary}`
**Related citation**: `{taxonomy: cwe, id: CWE-918, relationship: related}` (Server-Side Request Forgery)

**Trigger keywords**: `outbound HTTP from agent`, `LLM-synthesized URL`

**Applicable DFD element types**: Process

**Indicators**:
- Agent tooling that takes a URL from model output and invokes `requests.get()` / `fetch()` / `http.Client.Do()` on it without URL validation
- Absence of a URL allowlist or deny-list declared on the outbound HTTP client
- No egress firewall rule preventing requests to RFC 1918 ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), link-local (`169.254.0.0/16`), or cloud metadata endpoints (`169.254.169.254`)
- URL scheme not validated against `{http, https}` (allows `file://`, `gopher://`, `dict://` SSRF variants)
- DNS rebinding protection absent (allowlist-by-hostname is bypassable without DNS pinning)

**Worked Example** (server-side execution context: the HTTP client runs on tachi's server):
- **Finding**: LLM-powered research agent takes a "fetch this URL and summarize" instruction. An attacker injects a prompt causing the model to emit `http://169.254.169.254/latest/meta-data/iam/security-credentials/`; the server-side HTTP client fetches AWS IAM credentials from the instance metadata service and passes them back to the attacker via the model's response.
- **Mitigation**: Implement a URL allowlist of permitted external hostnames; reject all other URLs pre-request. Enforce an egress firewall that blocks RFC 1918 / link-local / metadata endpoints from the service's egress path. Validate the URL scheme against `{http, https}` only. Apply DNS pinning: resolve the hostname once, pin the IP, and verify it is outside private ranges before dispatching the request.

### 4. Template / Expression Injection

LLM output interpolated into a server-side template engine (Jinja2, ERB, Thymeleaf, Freemarker) in a context where the template engine treats the output as an expression rather than a literal string. Enables arbitrary code execution via the template engine's expression language, even when the surrounding template is static.

**Primary citation**: `{taxonomy: owasp, id: LLM05, relationship: primary}`
**Related citation**: `{taxonomy: cwe, id: CWE-94, relationship: related}` (Improper Control of Generation of Code — Code Injection; substituting for absent CWE-1336 Template Injection per FR-007 F-A1 catalog constraint)

**Trigger keywords**: `template engine`

**Applicable DFD element types**: Process

**Indicators**:
- Model output passed to `Jinja2.Template(model_out).render()` where model_out is user-influenced (server-side template injection surface)
- Template engines configured in non-escape mode (`autoescape=False` in Jinja2, `disableAutoEscape` in Thymeleaf)
- Absence of a sandboxed template engine (Jinja2 `SandboxedEnvironment` not used for untrusted input)
- Dynamic template construction from model output rather than fixed templates with safe variable interpolation
- Use of template engines that expose dangerous primitives (filesystem access, process execution) in expression context without restrictions

**Worked Example** (server-side execution context):
- **Finding**: Report generation service passes an LLM-synthesized section heading into `Jinja2.Template(heading).render()`. An adversarial prompt coerces the model into emitting `{{ ''.__class__.__mro__[1].__subclasses__()[408]("id", shell=True, stdout=-1).communicate() }}`; the Jinja2 template engine evaluates the expression server-side and spawns a shell, enabling RCE.
- **Mitigation**: Never pass model output to template engines as the template source — use model output only as VALUES interpolated into a fixed, pre-authored template with `autoescape=True`. If dynamic templates are unavoidable, use Jinja2 `SandboxedEnvironment` and restrict the exposed globals/filters. Prefer structured output (JSON, data classes) over free-text templates when the data flow permits.

### 5. Path Traversal + Unsafe File Writes

LLM output used to construct filesystem paths without canonicalization or allowlist directory enforcement. An attacker prompts the model to emit relative-path sequences (`../../etc/passwd`) or absolute paths into writable system directories, causing the server-side file operation to escape the intended output directory.

**Primary citation**: `{taxonomy: owasp, id: LLM05, relationship: primary}`
**Related citation**: `{taxonomy: cwe, id: CWE-22, relationship: related}` (Improper Limitation of a Pathname to a Restricted Directory — Path Traversal; substituting for absent CWE-73 External Control of File Name or Path per FR-007 F-A1 catalog constraint)

**Trigger keywords**: `file path from model`

**Applicable DFD element types**: Process

**Indicators**:
- Model output used as filename or full path in `open(path, 'w')`, `fs.writeFile()`, `Path(path).write_bytes()`, or equivalent
- Absence of `pathlib.Path.resolve()` + `is_relative_to(allowlisted_dir)` check before opening write handles
- No rejection of path separators (`/`, `\`) in model-generated filenames when a filename (not path) is expected
- Filesystem operations in user-writable directories (`/tmp`, `$HOME`, adopter's config dir) with model-influenced paths
- Write operations with overly permissive modes (`0o777`, `0o666`) that widen the blast radius on traversal

**Worked Example** (server-side execution context):
- **Finding**: LLM-powered documentation generator takes an LLM-proposed filename for each output document. An adversarial prompt coerces the model into emitting `../../etc/logs/override.log`; the server-side `open(path, 'w')` call escapes the intended output directory and overwrites a log rotation file, enabling log injection or potential privilege escalation depending on downstream log processing.
- **Mitigation**: Canonicalize the path with `pathlib.Path(filename).resolve()` and enforce `resolved_path.is_relative_to(allowlisted_output_dir)` before opening the write handle. Reject filenames containing path separators (`/`, `\`) when a filename (not path) is expected. Generate filesystem names from a deterministic ID plus a sanitized suffix rather than model-generated strings; use model output only to label the file contents, not to name the file.
