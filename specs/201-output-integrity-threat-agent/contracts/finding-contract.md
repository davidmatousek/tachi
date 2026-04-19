# Finding IR Contract for `OI-{N}` Findings

**Feature**: 201 — output-integrity-threat-agent
**Schema version target**: `schemas/finding.yaml` v1.6

## Purpose

Document the shape of `OI-{N}` findings emitted by the new `output-integrity` agent. This contract is consumed by (a) the agent itself during finding emission, (b) `scripts/tachi_parsers.py` during parsing and validation, (c) downstream infrastructure-tier consumers (risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler), and (d) the F-B coverage-attestation renderer (Feature 194).

## Canonical Finding Shape

```yaml
id: "OI-{N}"                          # monotonically increasing per pipeline run; matches schema 1.6 regex ^(S|T|R|I|D|E|AG|LLM|AGP|OI)-\d+$
category: "llm"                       # existing enum value from schemas/finding.yaml — NOT changed in this feature
title: "{sink_type}: {short_summary}" # e.g., "XSS via LLM output rendered as innerHTML without encoding"
severity: "low" | "medium" | "high" | "critical"   # OWASP 3×3 matrix; computed via severity-bands-shared.md
component: "{DFD Process component name}"          # e.g., "LLM Agent Orchestrator"
description: |
  {2-4 sentence threat description. MUST distinguish server-side vs client-side execution
  per FR-017. MUST name the specific sink type (HTML render, SQL execution, shell invocation,
  template render, URL construction, file path write). MUST name at least one concrete
  downstream consequence (XSS on user browser, SQL data leakage, RCE on backend, etc.)}
mitigation: |
  {Stack-specific mitigation naming at least one specific encoding, library, or pattern.
   MUST NOT be generic "sanitize output" prose. Examples:
   - Client-side execution: "Apply HTML entity encoding (e.g., DOMPurify.sanitize / html-entities.encode) before rendering. Use framework-native escape helpers (React {} interpolation, Vue v-text). Declare strict Content Security Policy with script-src 'self' directive set."
   - Server-side SQL: "Use parameterized queries (psycopg2.execute(sql, params), sqlx.Query with ? placeholders). NEVER string-concatenate LLM output into SQL fragments."
   - Server-side command: "Use command-line arg vector (subprocess.run([cmd, arg1, arg2], shell=False), exec.Command(cmd, arg1, arg2)). NEVER pass LLM output through a shell interpreter."
   - SSRF: "Validate LLM-synthesized URLs against an allowlist (permitted hosts + schemes). Enforce egress firewall at the network layer. Reject URLs with metadata-service hostnames (169.254.169.254, metadata.google.internal)."
   - Template injection: "Configure template engine in escape mode (Jinja2 autoescape=True, Handlebars with {{ }} triple-brace disabled). Consider sandboxed renderer (Jinja2 SandboxedEnvironment)."
   - Path traversal: "Canonicalize LLM-generated paths (os.path.realpath). Enforce allowlist directory restriction (pathlib.Path.resolve().is_relative_to(SAFE_ROOT)). Reject paths containing `..` or absolute segments."}
references:
  - "OWASP LLM05:2025"
  - "https://cwe.mitre.org/data/definitions/{CWE_NUMBER}.html"
source_attribution:                  # REQUIRED per SC-010 — every OI-{N} finding MUST carry this
  - {taxonomy: "owasp", id: "LLM05", relationship: "primary"}    # REQUIRED on every OI-{N}
  - {taxonomy: "cwe", id: "CWE-{NUMBER}", relationship: "related"}  # per applicable pattern category
# --- downstream-assigned fields (NOT set by the agent) ---
maestro_layer: "L5"                   # orchestrator Phase 1 (existing Feature 084); typical L5 Security
agentic_pattern: "none"               # orchestrator Phase 3.6 (existing Feature 142)
delta_status: null                    # orchestrator delta-propagation (existing Feature 104) — set iff baseline present
```

## Invariants

### I1 — Schema Compliance
- `id` MUST match `^(S|T|R|I|D|E|AG|LLM|AGP|OI)-\d+$` (schema 1.6 regex)
- `category` MUST be `llm` (existing enum value; no new enum required)

### I2 — Source Attribution Required (SC-010)
- `source_attribution` MUST be a non-empty array
- `source_attribution` MUST contain at minimum `{taxonomy: "owasp", id: "LLM05", relationship: "primary"}`
- All `(taxonomy, id)` pairs MUST resolve in `schemas/taxonomy/{taxonomy}.yaml` at orchestrator Phase 4 validation (`validate_source_attribution()` at `scripts/tachi_parsers.py:826`)

### I3 — CWE IDs Must Be In-Catalog
- CWE IDs used in `source_attribution` MUST be verified present in `schemas/taxonomy/cwe.yaml`
- Verified present at PRD time: **CWE-22, CWE-78, CWE-79, CWE-89, CWE-94, CWE-918**
- Verified absent at PRD time: **CWE-73, CWE-1336** (MUST NOT be cited)
- Path traversal substitution: CWE-22 alone (CWE-73 absent)
- Template injection substitution: CWE-94 (CWE-1336 absent)

### I4 — CWE Mapping per Pattern Category (FR-007)
| Pattern Category | Required Primary (`relationship: primary`) | Required Related (`relationship: related`) |
|---|---|---|
| Client-Side Execution Sinks (XSS / DOM) | `owasp:LLM05` | `cwe:CWE-79` |
| Server-Side Execution Sinks (SQLi) | `owasp:LLM05` | `cwe:CWE-89` |
| Server-Side Execution Sinks (Command Injection) | `owasp:LLM05` | `cwe:CWE-78` |
| Server-Side Execution Sinks (Generic Code Injection) | `owasp:LLM05` | `cwe:CWE-94` |
| SSRF from LLM-Synthesized URLs | `owasp:LLM05` | `cwe:CWE-918` |
| Template / Expression Injection | `owasp:LLM05` | `cwe:CWE-94` (substitutes for absent CWE-1336) |
| Path Traversal + Unsafe File Writes | `owasp:LLM05` | `cwe:CWE-22` (substitutes for absent CWE-73) |
| (Conditional) Human-Trust Exploitation | `owasp:ASI09` (verify in `owasp.yaml` before authoring) | — |

### I5 — Mitigation Text Specificity (US-2 AC-1 + AC-2)
- `mitigation` MUST name at least one specific encoding mechanism, library, framework helper, or defensive pattern
- Generic phrases like "sanitize output" or "validate input" alone MUST NOT appear as the sole mitigation
- Server-side vs client-side execution classification MUST be discernible from the `description` text

### I6 — No Agent-Set `agentic_pattern` (FR-016)
- Agent MUST NOT set `agentic_pattern` in the emitted finding
- Orchestrator Phase 3.6 assigns `agentic_pattern: none` post-hoc per ADR-026 (OI-{N} findings are single-agent output-surface, not multi-agent pattern)

### I7 — Downstream-Set Fields
- `maestro_layer` — set by orchestrator Phase 1 via keyword classification (existing Feature 084)
- `agentic_pattern` — set by orchestrator Phase 3.6 (existing Feature 142)
- `delta_status` — set by orchestrator delta-propagation if baseline present (existing Feature 104)
- Agent MUST emit the finding WITHOUT these fields; they are set downstream

### I8 — Zero-Finding Non-Speculation (US-1 AC-4, FR-011)
- When no DFD `Process` component matches both a trigger keyword AND a structural downstream-sink indicator, the agent MUST emit **zero** findings
- Keyword match alone is insufficient; keyword + indicator is required

### I9 — References Field
- `references` array MUST include `OWASP LLM05:2025` as the first entry
- Per-pattern-category CWE references MUST include the canonical CWE URL: `https://cwe.mitre.org/data/definitions/{CWE_NUMBER}.html`

## Validation Checkpoints

| Checkpoint | Phase | Validator |
|---|---|---|
| Schema regex match | Parse (orchestrator Phase 5) | `scripts/tachi_parsers.py::parse_threats_findings` regex check |
| Source attribution referential integrity | Validate (orchestrator Phase 4) | `scripts/tachi_parsers.py::validate_source_attribution` |
| Mitigation text non-empty | Parse | existing finding-IR validator |
| Non-empty `source_attribution` | Agent emission time | ADR-023-compliant agent `## Detection Workflow` step 5 |
| Zero-finding on non-qualifying arch | Agent emission time | `## Detection Workflow` step 2 (indicator collection) |

## Example Findings (Illustrative — Not Exhaustive)

### Example 1 — Client-Side XSS
```yaml
id: "OI-1"
category: "llm"
title: "XSS via LLM-generated HTML rendered as innerHTML"
severity: "high"
component: "Response Formatter"
description: |
  The Response Formatter Process receives LLM-generated content and renders it into the user's
  browser DOM using `element.innerHTML` without intervening encoding. An attacker who influences
  the LLM's output (via prompt injection or upstream poisoning) can inject `<script>` tags that
  execute in the user's browser context, enabling session hijacking or data exfiltration. This
  is client-side execution — the payload runs in the browser.
mitigation: |
  Apply HTML entity encoding via a vetted library (DOMPurify.sanitize / html-entities.encode)
  before assigning to innerHTML. Prefer safe DOM APIs (textContent over innerHTML). Declare strict
  Content Security Policy with script-src 'self' to block inline-script injection. Framework
  alternatives: React {} interpolation, Vue v-text directive.
references:
  - "OWASP LLM05:2025"
  - "https://cwe.mitre.org/data/definitions/79.html"
source_attribution:
  - {taxonomy: "owasp", id: "LLM05", relationship: "primary"}
  - {taxonomy: "cwe", id: "CWE-79", relationship: "related"}
```

### Example 2 — Server-Side SQLi
```yaml
id: "OI-2"
category: "llm"
title: "SQL Injection via LLM-synthesized query fragment concatenated into SELECT"
severity: "critical"
component: "Query Builder Agent"
description: |
  The Query Builder Agent Process receives a natural-language request, invokes the LLM to produce
  a WHERE-clause fragment, and string-concatenates the fragment into a SELECT statement executed
  against the user data store. An attacker who influences the LLM's output can inject SQL
  (e.g., `1=1 UNION SELECT * FROM users`) to read arbitrary rows or trigger data modifications.
  This is server-side execution — the payload runs on the backend.
mitigation: |
  Use parameterized queries (psycopg2.execute("SELECT * FROM t WHERE id = %s", (id_val,));
  sqlx.Query with $1 / ? placeholders). NEVER string-concatenate LLM output into SQL fragments.
  If LLM must shape query structure, use a structured intermediate representation (e.g., SQLAlchemy
  Core Select with explicit column references) and validate IR nodes against an allowlist.
references:
  - "OWASP LLM05:2025"
  - "https://cwe.mitre.org/data/definitions/89.html"
source_attribution:
  - {taxonomy: "owasp", id: "LLM05", relationship: "primary"}
  - {taxonomy: "cwe", id: "CWE-89", relationship: "related"}
```

### Example 3 — SSRF from LLM-Synthesized URL
```yaml
id: "OI-3"
category: "llm"
title: "SSRF via LLM-synthesized URL passed to outbound HTTP client"
severity: "high"
component: "External Data Fetcher"
description: |
  The External Data Fetcher Process invokes the LLM to build URLs for outbound HTTP requests
  (fetching data to enrich responses). No allowlist enforcement exists; the LLM can be induced to
  emit URLs pointing at cloud metadata services (169.254.169.254), internal admin endpoints, or
  attacker-controlled callback servers. This enables SSRF with consequences ranging from cloud
  credential theft to internal-service reconnaissance.
mitigation: |
  Validate LLM-synthesized URLs against an allowlist of permitted hosts and schemes before fetch.
  Reject URLs whose hostname resolves to private/metadata IP ranges (169.254.169.254, 10.0.0.0/8,
  172.16.0.0/12, 192.168.0.0/16). Enforce egress firewall at the network layer. Deny redirect
  following to disallowed hosts.
references:
  - "OWASP LLM05:2025"
  - "https://cwe.mitre.org/data/definitions/918.html"
source_attribution:
  - {taxonomy: "owasp", id: "LLM05", relationship: "primary"}
  - {taxonomy: "cwe", id: "CWE-918", relationship: "related"}
```
