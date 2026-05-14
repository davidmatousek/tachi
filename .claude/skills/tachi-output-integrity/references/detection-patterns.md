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

**Trigger keywords**: `model output to SQL`, `LLM-generated query`, `command construction`, `npm install`, `pip install`, `apt install`, `brew install`, `gh workflow`, `actions/`, `uses:`, `package-lock`, `requirements.txt`

> **Both-signal requirement**: The keyword extension above adds package-manager and CI-workflow trigger keywords to the existing Cat 2 list. Per the Detection Workflow both-keyword-AND-sink-indicator rule (see Detection Scope above), a prose mention of `npm install` or `pip install` outside an execution-sink context (e.g., a comment, a README, a documentation passage) does NOT activate the agent. Activation requires both the keyword AND an architectural signal of a downstream execution sink — install-script runner, CI workflow runner, agent tool capable of executing the install command — in the data flow.

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

##### Sub-example: Package-Manager / CI-Workflow Injection (AI Coding Assistant)

**Finding**: `OI-{N} AI coding assistant emits attacker-controlled package name into npm install (supply-chain execution sink)`

**Architecture**: An LLM Process generates an install script or GitHub Actions workflow YAML from user input. The output contains `npm install <attacker-controlled-name>` or a `uses: malicious/action@<commit>` step. The CI runner or developer machine executes the LLM output without validation; the install phase fetches and executes arbitrary post-install scripts under the executor's credentials.

**Real-world urgency** (2026 incident record):
- **SANDWORM_MODE** (Sep 2025 → Apr 2026): self-propagating npm worm injecting prompt-injection blocks into AI assistant tool descriptions; affected 170+ npm packages with 404 malicious versions on a single day.
- **LiteLLM PyPI compromise** (Mar 2026): `pip install litellm` for ~4 hours silently exfiltrated environment variables, AWS credentials, and SSH keys via a `.pth` payload.
- **Agentic Workflow Injection (AWI)** (arXiv 2605.07135): formalized academic attack pattern in GitHub Actions where LLM-emitted workflow steps escalate to repository-wide compromise.

**Mitigation** (at least one required; defense-in-depth recommends all three layered):
- **Allowlist of registries and scopes**: the agent may only resolve names from a fixed registry list (a private registry plus a handful of vetted public packages); arbitrary npm / PyPI / GitHub Action names are rejected before resolution. Pattern is named in NVIDIA / Nesbitt 2026 agentic-workflow guidance.
- **Sandbox isolation** (canonical 2026 isolation trio): the install phase runs inside a microVM (Firecracker), a gVisor user-space kernel, or a hardened container with no network egress beyond the allowlisted registry. Even if the install resolves an attacker-controlled package, the post-install script cannot reach the host filesystem or credentials.
- **Sigstore-backed signature verification**: `npm audit signatures` or the PyPI equivalent gates the install on cryptographic provenance; unsigned or signature-mismatched installs fail closed. The npm and PyPI signature pipelines both rolled to production in 2025.

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

### 6. Vector / Search-DSL Injection

LLM-synthesized filters for vector databases (Qdrant, Pinecone) and structured search DSLs (Elasticsearch, hybrid-search backends) gate tenant and RBAC scoping on retrieval. When the LLM emits filter clauses without server-side composition, the resulting query can bypass the tenant-scoping clause — functionally equivalent to SQL injection across a tenant boundary. Execution context is server-side: the query runs against the vector DB or search backend with the service account's reach across all tenants whose data is not explicitly excluded.

**Primary citation**: `{taxonomy: owasp, id: LLM08, relationship: primary}` (Vector and Embedding Weaknesses; cross-anchor `{taxonomy: owasp, id: LLM05, relationship: related}` for Improper Output Handling)
**Related citations**: `{taxonomy: cwe, id: CWE-943, relationship: related}` (Improper Neutralization of Special Elements in Data Query Logic — primary CWE anchor for non-SQL query-language injection); `{taxonomy: cwe, id: CWE-89, relationship: related}` (SQL Injection — taxonomic neighbor); `{taxonomy: cwe, id: CWE-94, relationship: related}` (Code Injection — when filter is templated as expression)

**Trigger keywords**: `qdrant`, `pinecone`, `metadata filter`, `must_not`, `must` (in vector-filter context), `tenant_id`, `namespace`, `embedding query`, `hybrid search`, `elasticsearch DSL`, `vector index`, `RAG retrieval filter`

**Applicable DFD element types**: Process

**Indicators**:
- LLM Process emits filter/query content into a vector-DB or structured-search query interface
- Multi-tenancy signal present in the data flow (`tenant_id` payload field, namespace-per-tenant convention, RBAC scoping on retrieval)
- Filter composition happens at the LLM-output layer, not at the application or middleware layer (the LLM-emitted filter reaches the vector DB as authoritative input)
- Architecture lacks server-side filter pinning or base-filter override-prevention — there is no middleware layer composing the tenant clause with `AND` against an immutable pin

> **Distinguishing prose (output-handling vs corpus-poisoning)**: This is an **output-handling** signal — the LLM's *filter SYNTHESIS* goes wrong. It is distinct from `data-poisoning` corpus-side signals where the *corpus CONTENT* goes wrong. Both findings can co-emit on the same multi-tenant RAG architecture without contradiction: the output-integrity Cat 6 finding fires on the filter-synthesis surface; a co-located data-poisoning finding fires on the corpus-content surface. See `.claude/agents/tachi/data-poisoning.md` for the corpus-content surface.

**Worked Example** (server-side execution context: the query runs on the vector DB or search backend across the multi-tenant corpus):

- **Finding**: `OI-{N} Multi-tenant RAG metadata filter omits tenant_id clause (vector-DB injection)`. An LLM Process synthesizes a Pinecone metadata filter from user input. The application sends the filter directly to Pinecone without server-side composition. The filter is supposed to include `tenant_id == "{requesting_tenant}"`, but the LLM-synthesized filter contains only the user's query terms, omitting the tenant clause entirely. As a result, the query returns documents from all tenants whose `tenant_id` is not explicitly excluded — functionally equivalent to SQL injection across tenant boundaries. The same failure mode applies to Qdrant `must` / `must_not` filters and to Elasticsearch DSL bool queries.
- **Mitigation** (at least one required; defense-in-depth recommends all three layered):
  - **Pre-retrieval filtering / server-side filter composition**: the application composes the tenant_id clause server-side before the filter reaches Pinecone or Qdrant. The LLM-emitted filter is wrapped, not interpreted as authoritative. Pattern is named in Microsoft Azure secure-RAG and AWS Bedrock + OpenSearch JWT-scoped retrieval guidance.
  - **Base filter that cannot be overridden** (Mavik Labs 2026 / Authzed pattern): middleware injects the `tenant_id` pin; the LLM-emitted filter is composed with `AND` against the pin and raises `SecurityError` if the LLM-emitted filter attempts to override the pin.
  - **Namespace-per-tenant** (Pinecone Silo model — strongest control per OWASP LLM08:2025): each tenant has a dedicated Pinecone namespace; the LLM-emitted filter never crosses tenant boundaries because the namespace is fixed at the application layer before the query runs. Pool model (shared namespace with metadata-filter scoping) is acceptable but weaker than Silo.
  - **Allowlisted clause keys**: the LLM-emitted filter is parsed and rejected if any clause key is not in the application's allowlist. Tenant context is extracted from a validated JWT, never from request parameters or LLM output.

## Cross-Agent Handoff Sinks (Navigational — NO emission from `output-integrity`)

> **Boundary phrase**: LLM output is **harmless as text, dangerous as tool argument or memory entry.** The `output-integrity` agent does NOT emit findings on tool-call-argument or durable-memory-write flows — those flows are owned by adjacent agents.

### When LLM output flows into a tool-call argument

Cross-link target: `.claude/agents/tachi/tool-abuse.md` (Pattern Categories 9 "Insecure Inter-Agent Communication" and 10 "MCP-to-MCP Trust Propagation").

The `tool-abuse` agent owns the surface where LLM-synthesized strings become parameters of downstream tool invocations (MCP calls, function-calling middleware, plugin APIs). The signal class is **command/parameter injection across an agent-to-agent communication channel**, distinct from the encoding/sanitization signal class owned here. Adopters reviewing a multi-agent architecture that hands LLM output to a downstream tool should expect to see `tool-abuse` findings on that handoff, not `output-integrity` findings.

### When LLM output flows into a durable memory write

Cross-link target: `.claude/agents/tachi/data-poisoning.md` (OWASP ASI06 Memory & Context Poisoning).

The `data-poisoning` agent owns the surface where LLM-synthesized content gets persisted to a durable knowledge store (RAG corpus, agent memory, knowledge base) that future agent decisions will consult. The signal class is **persistent integrity violation of agent durable state**, distinct from the encoding/sanitization signal at the output-handling moment. OWASP ASI06 Memory & Context Poisoning is the canonical anchor (NOT OWASP LLM04, which covers training-time data poisoning — a distinct surface). Adopters reviewing an architecture that promotes LLM output into a durable memory store should expect to see `data-poisoning` findings on that handoff, not `output-integrity` findings.

### Mitigation Pattern: Memory-Promotion Rules

The recommended mitigation when LLM output may flow into a durable memory store is **structured allowlist gating before promotion**. The pattern names three required fields:

- `promotable_keys`: allowlist enum of which memory-store keys the agent may write
- `value_schema`: reference to a JSON-schema validating the shape of permitted values
- `tenant_scope`: pin binding the write to the requesting tenant's namespace

#### Worked schema example (YAML)

```yaml
# Memory-Promotion Rules — agent durable-write gate
memory_promotion_rules:
  promotable_keys:
    enum:
      - user_preferences.theme
      - user_preferences.timezone
      - session_summary
    description: |
      The agent may only write to these three keys. Any write to a key
      not in this list raises PromotionDeniedError and is logged.
  value_schema:
    $ref: "schemas/agent-memory-value.yaml"
    description: |
      Every promoted value must validate against this schema. Schema
      rejects malformed or unexpected payloads. See A-MEMGUARD framework
      (arXiv 2510.02373) for the canonical "staging buffer with validation"
      pattern that this allowlist implements.
  tenant_scope:
    binding: "request.tenant_id"
    description: |
      The write is namespaced to the requesting tenant's memory store.
      Cross-tenant memory writes are rejected. AWS Bedrock AgentCore
      Memory exposes `scope` dicts implementing this pattern.
  optional_layered_controls:
    staging_buffer:
      enabled: true
      description: |
        Writes go to a staging buffer first; promotion to live store
        requires schema validation plus optional human approval. Pattern
        is named in A-MEMGUARD (arXiv 2510.02373).
    human_approval_gate:
      enabled: false
      description: |
        Additive control for modifications that affect future session
        behavior. Disabled by default; enable for high-trust memory
        categories.
```

**Distinguishing prose**: This mitigation pattern lives in `output-integrity`'s navigational surface, but the durable-memory-write *detection* is owned by `data-poisoning`. Adopters implementing the rules should consult `data-poisoning` for the detection-side workflow and `output-integrity` for the output-handling-side framing.

**Industry anchors**:
- OWASP ASI06 Memory & Context Poisoning (NOT OWASP LLM04 — LLM04 is training-time data poisoning, a distinct surface)
- OWASP Agent Memory Guard project
- A-MEMGUARD (arXiv 2510.02373) — "staging buffer with validation"
- MemoryGraft (arXiv 2512.16962) — persistent memory poisoning attack
- MINJA Memory Injection Attack (arXiv 2601.05504, >95% success rate without schema validation)
- AWS Bedrock AgentCore Memory; Vertex AI Memory Bank IAM Conditions

> **One-way navigational invariant (FR-007)**: This subsection adds NO new trigger keywords and NO new downstream-sink-indicators to the `output-integrity` agent's emission surface. It is a navigational pointer only. The agent's existing both-signal workflow (see Detection Workflow §6 in `output-integrity.md`) enforces zero emissions from the prose in this subsection alone. Re-running an existing multi-agent baseline (e.g., `examples/agentic-app/`) under `SOURCE_DATE_EPOCH=1700000000` is expected to produce a byte-identical OI-scoped finding subset pre/post merge of this refinement.
