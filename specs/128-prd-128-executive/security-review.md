---
task: T037
reviewer: security-analyst
date: 2026-04-10
feature: 128-executive-threat-architecture
branch: 128-prd-128-executive
status: APPROVED_WITH_CONCERNS
---

# Security Review — Feature 128 (Executive Threat Architecture)

## Review Scope

T037 per `specs/128-prd-128-executive/tasks.md` — confirm no new secrets, PII,
or credentials introduced via the Feature 128 implementation, with a primary
focus on the example regeneration (T033). The agentic-app `threats.md` is a
pre-F-128 sanitized fixture; the new image (`threat-executive-architecture.jpg`)
was generated via the `mcp__mcp-image__generate_image` MCP tool (Gemini backend)
from the fixture's extracted payload and should also be sanitized.

## Files Under Review

### New Artifacts (T033 Regeneration)

| File | Size | Status |
|------|------|--------|
| `examples/agentic-app/sample-report/threat-executive-architecture-spec.md` | 13,334 B | New |
| `examples/agentic-app/sample-report/threat-executive-architecture.jpg` | 2,080,516 B | New (Gemini) |
| `examples/agentic-app/sample-report/security-report.pdf` | 5,907,302 B | Regenerated |
| `examples/agentic-app/sample-report/attack-trees/*.png` (7 files) | varies | Pre-existing, regenerated |

### Modified Python Scripts

| File | Change Category |
|------|-----------------|
| `scripts/extract-infographic-data.py` | +293 lines: executive-architecture branch, helper functions |
| `scripts/extract-report-data.py` | ~+30 lines: image detection, attack-tree H1 fallback |

### Modified Typst Templates

| File | Change Category |
|------|-----------------|
| `templates/tachi/security-report/main.typ` | +21 lines: conditional executive-architecture page |
| `templates/tachi/security-report/attack-path.typ` | +4 lines: defensive string coercion |

### Modified Agent / Command Docs

- `.claude/agents/tachi/threat-infographic.md`
- `.claude/agents/tachi/report-assembler.md`
- `.claude/commands/tachi.infographic.md`
- `.claude/skills/tachi-infographics/references/executive-architecture.md` (new)
- `schemas/infographic.yaml`

### New Test Infrastructure

| File | Purpose |
|------|---------|
| `tests/__init__.py`, `tests/conftest.py` | Pytest session fixtures (importlib loading) |
| `tests/scripts/test_extract_infographic_data.py` | Unit tests for F-128 helpers |
| `tests/scripts/test_extract_report_data.py` | Unit tests for image detection |
| `tests/scripts/test_backward_compatibility.py` | Byte-cmp baseline PDFs |
| `tests/scripts/test_command_dispatch.py` | Command-doc dispatch validation |
| `tests/scripts/test_pdf_page_positioning.py` | PDF page-order assertion |
| `tests/scripts/test_smoke.py` | Smoke test |
| `tests/scripts/fixtures/**` | Minimal test fixtures |
| `pyproject.toml` | Pytest configuration |
| `requirements-dev.txt` | pytest and pytest-cov dev deps |

### F-128 Spec Artifacts

- `specs/128-prd-128-executive/` — 16 files (spec.md, plan.md, tasks.md,
  decisions.md, checkpoints, manual-verification, quickstart, data-model,
  research, NEXT-SESSION, contracts/, checklists/)

---

## Finding 1 — PII and Credential Scan of New/Modified Files

**Status**: PASS

### Scan Patterns Applied

- Email addresses: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
- Phone numbers: `[0-9]{3}[-.][0-9]{3}[-.][0-9]{4}`
- US SSN: `[0-9]{3}-[0-9]{2}-[0-9]{4}`
- IP addresses (v4): `\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b`
- Internal hostnames: `*.internal`, `*.local`, `*.corp`, `*.private`, `*.intranet`
- AWS access keys: `AKIA[0-9A-Z]{16}`
- OpenAI / Anthropic keys: `sk-[A-Za-z0-9]{20,}`
- GitHub PATs: `ghp_[A-Za-z0-9]{20,}`
- Slack tokens: `xox[baprs]-[0-9A-Za-z-]{20,}`
- Bearer tokens: `Bearer\s+[A-Za-z0-9_.-]{20,}`
- Private keys: `BEGIN.*PRIVATE.*KEY`
- User home paths: `\b/Users/[a-z]+/`

### Results by File Category

| File Category | Email | Phone | AWS | Private Key | Local Path | Result |
|---------------|-------|-------|-----|-------------|------------|--------|
| agentic-app spec (`threat-executive-architecture-spec.md`) | 0 | 0 | 0 | 0 | 0 | Clean |
| agentic-app JPEG (binary scan) | 0 | 0 | 0 | 0 | 0 | Clean |
| agentic-app PDF (pdftotext) | 0 | 0 | 0 | 0 | 0 | Clean |
| `scripts/extract-infographic-data.py` diff | 0 | 0 | 0 | 0 | 0 | Clean |
| `scripts/extract-report-data.py` diff | 0 | 0 | 0 | 0 | 0 | Clean |
| Typst template diffs | 0 | 0 | 0 | 0 | 0 | Clean |
| Agent/command docs | 0 | 0 | 0 | 0 | 0 | Clean |
| `tests/**` | 0 | 0 | 0 | 0 | 0 | Clean |
| `specs/128-prd-128-executive/**` | 0 | 0 | 0 | 0 | 0 | Clean |

### Benign Pattern Matches (False Positives)

1. **SARIF `primaryLocationLineHash` fields** in `threats.sarif` and
   `risk-scores.sarif` — e.g., `"2b7cc5858485093d"`. These are SARIF-standard
   content hashes used for line identification across scans; they are not
   credentials or secrets. Pre-existing (not introduced by F-128).
2. **`SOURCE_DATE_EPOCH=1700000000`** in `specs/128-prd-128-executive/decisions.md`
   and `checkpoint-p0.md`. This is a Unix timestamp used as a build environment
   variable for reproducible PDF generation, not a phone number or credential.
3. **PDF `/Title <FEFF0046...>`** entry matched by generic regex. This is a
   UTF-16 BOM-prefixed hex encoding of the TOC section title "Findings Detail
   — Residual Risk" — a PDF outline metadata field, not PII.

### Conclusion

Zero real PII, credential, or secret findings across all F-128 files. The
agentic-app fixture remains the same sanitized example that existed before
the feature, and the new spec file + JPEG + PDF derived from it carry no
new sensitive content.

---

## Finding 2 — JPEG Image Content Sanitization

**Status**: PASS

### Image Format Verification

```
$ file examples/agentic-app/sample-report/threat-executive-architecture.jpg
JPEG image data, JFIF standard 1.01, resolution (DPI), density 300x300,
segment length 16, baseline, precision 8, 1696x2528, components 3
```

- **Format**: Valid JPEG (JFIF 1.01)
- **Dimensions**: 1696 x 2528 pixels (portrait, ~5.65" x 8.43" at 300 DPI)
- **Color space**: sRGB IEC61966-2.1, 3 components (RGB), no alpha
- **Size**: 2,080,516 bytes
- **Embedded document/script**: None — verified by `file` command and
  `sips -g all`. The image is a legitimate raster JPEG and cannot contain
  executable content.

### C2PA Content Credentials Analysis

The image carries C2PA (Coalition for Content Provenance and Authenticity)
metadata identifying it as Gemini-generated:

- Signer: `Google LLC` via `Google C2PA Media Services 1P ICA G3`
- Producer: `Google System 600321` / `Google Media Processing Services`
- Validity: Signed certificate chain with OCSP responder at
  `http://c2pa-ocsp.pki.goog/`
- Claim URN: `urn:c2pa:73b78b28-7e5a-4dbd-cb48-4f72942b13c5`

This is **positive attestation** that the image was produced by Google's
Gemini image-generation service as expected per `decisions.md`. The C2PA
block does NOT contain any user-identifiable information beyond Google's
signing certificate metadata.

### Binary String Scan

Ran `strings` over the JPEG (22,087 total strings). After filtering out
Base64-encoded C2PA certificate data, JFIF headers, and signature blobs,
no PII-matching plaintext was found. Regex matches for email/phone/AWS
keys/private keys all returned zero.

### Prompt Content Review (Section 6 of Spec)

The Gemini prompt embedded in `threat-executive-architecture-spec.md`
Section 6 was cross-checked against the source `threats.md` fixture. The
prompt contains:

- Component names from the fixture (User, External API, Audit Logger,
  Guardrails Service, Knowledge Base, LLM Agent Orchestrator, MCP Tool
  Server) — all generic architectural labels, no PII
- One callout text: "Adversarial prompts override system prompt" →
  plain-English rewrite "An attacker can craft a trick prompt that
  overrides the AI assistant's safety rules and makes it behave in
  unapproved ways." — generic threat narrative, no sensitive data
- Hex color codes (`#DC2626`, `#F0F4FF`, etc.) and typography directives
  — safe, decorative
- Finding reference `LLM-1` — an internal fixture ID, not a secret

No real threat model content, no customer data, no credentials were passed
into the Gemini API call.

### Conclusion

The JPEG is a valid raster image with no embedded documents or scripts,
signed by Google's C2PA service as Gemini-produced, and its source prompt
contained only sanitized fixture content. Image sanitization verified.

---

## Finding 3 — Python Code Review (extract-infographic-data.py)

**Status**: PASS

### New Code Surface

- 5 new helper functions (~293 lines):
  - `_normalize_component_name(name)` — string normalization
  - `_compute_dfd_type_layers(scope_data)` — component grouping
  - `_select_critical_high_callouts(findings, layers)` — per-layer dedup
  - `_build_executive_architecture_payload(...)` — top-level orchestrator
- New argparse choice: `executive-architecture`
- New early-exit branch in `main()`

### Security Analysis

| Risk | Assessment | Notes |
|------|------------|-------|
| New imports | None beyond `datetime`/`timezone` (already used) | No `requests`, `urllib`, `httpx`, `socket`, `subprocess`, `os.system`, `eval`, `exec()`, `pickle`, `shell=True` |
| Network calls | None | Pure data transformation over dicts |
| File system writes | `output_path.write_text(json.dumps(...))` | Writes JSON only; path comes from argparse |
| Input trust | Reads from local `threats.md` in the user's target dir | No remote fetches |
| Injection surface | None | No shell, no SQL, no eval. String concatenation is limited to log output written to stderr |
| Untrusted input reflection | Finding descriptions are passed through unmodified, but downstream escaping is handled by `escape_typst_string()` in `tachi_parsers.py` (line 50) which escapes `\`, `"`, and `\n` before emitting Typst literals |
| Resource exhaustion | Bounded by the fixed number of layers/findings in the input; no unbounded recursion or loops |

### Conclusion

No new security risks introduced. All changes are pure Python dict/list
transformations feeding a JSON serializer. No untrusted input flows into
dangerous sinks.

---

## Finding 4 — Python Code Review (extract-report-data.py)

**Status**: PASS with INFO observation

### New Code Surface

1. **Attack-tree H1 heading fallback parser** (~20 lines in
   `_parse_attack_tree_file()`)
2. **Finding ID colon strip** in `_parse_inline_attack_trees()` (1-line fix)
3. **Component/title enrichment** fallback (2 lines)
4. **Image detection and Typst data emission** for
   `executive_architecture_image_path` (~6 lines)

### Regex Safety Analysis

Two new regex patterns added in the H1 fallback:

```python
re.match(r"^Attack Tree:\s+(\S+?):?\s+[-\u2014]+\s+(.*)$", heading)
re.match(r"^([A-Za-z]+-\d+):\s+(.*)$", heading)
```

- Both anchored with `^` and `$`
- No nested quantifiers that would trigger ReDoS (exponential backtracking)
- Match against single stripped lines (bounded input length)
- Capture groups extract simple identifiers; no eval, no shell, no URL
- Safe against ReDoS and injection

### String Coercion Safety

The `component = component or finding.get("component", "")` pattern is a
harmless defaulting; likewise `title = title or finding.get("threat", "")`.
Both values pass through `escape_typst_string()` before reaching Typst
templates, per the existing pipeline contract.

### INFO Observation

The attack-tree H1 fallback *does* accept any attacker-controlled markdown
in an attack-tree file. However, in the tachi threat-modeling pipeline,
attack-tree files are produced by trusted agents from the user's own input
and are not loaded from third-party sources. Even if a malicious user
wrote a crafted attack-tree file, the worst outcome would be an
incorrectly-parsed finding ID/title, which is then escaped via
`escape_typst_string()` before Typst consumption. No RCE, file read, or
exfiltration surface is exposed.

### Conclusion

Safe. No new subprocess or network calls. The new parsers are purely
textual and well-bounded.

---

## Finding 5 — Typst Template Review

**Status**: PASS

### `templates/tachi/security-report/main.typ`

New block: `#if has-executive-architecture { infographic-page(...) }` —
reuses the existing `infographic-page()` function with two new bindings:

- `has-executive-architecture` (bool)
- `executive-architecture-image-path` (string)

Both bindings are emitted by `extract-report-data.py` after passing
through `escape_typst_string()`. The page is gated by an existing image
detection check (file exists and non-zero size), preserving the
backward-compatibility guarantee in FR-031.

### `templates/tachi/security-report/attack-path.typ`

Added defensive string-to-array coercion:

```typst
let remediation = entry.at("remediation", default: ())
if type(remediation) == str {
  remediation = if remediation != "" { (remediation,) } else { () }
}
```

This fix addresses a subtle iteration bug where a bare string would
iterate character-by-character in Typst's `for step in remediation`
loop. The fix converts a string into a single-element array. No security
impact — it is purely a rendering correctness fix.

### Conclusion

Typst templates handle F-128 bindings safely. No XSS-equivalent concerns
(Typst is a document-typesetting language that does not execute embedded
scripts in user data). String escaping is enforced at the extraction layer
via `escape_typst_string()`.

---

## Finding 6 — Dependency Surface Review

**Status**: PASS

### New Dependencies

| Package | Version | Purpose | Risk |
|---------|---------|---------|------|
| `pytest` | >=8.0 | Test runner | Dev-only, widely used, active maintenance |
| `pytest-cov` | >=4.1 | Coverage reporting | Dev-only, widely used, active maintenance |

### Scope

Both dependencies are declared in `requirements-dev.txt` and marked as dev
dependencies. They are NOT required for production pipeline execution and
do NOT ship with the example artifacts. The `pyproject.toml` configures
pytest with `addopts = "-ra --strict-markers"` and standard test
discovery settings — no plugin auto-loading from untrusted sources.

### Production Dependencies

Zero new production dependencies. The tachi pipeline continues to rely
only on Python standard library (`argparse`, `json`, `re`, `pathlib`,
`datetime`, `subprocess`, `concurrent.futures`, `shutil`, `tempfile`)
plus the existing `tachi_parsers.py` internal module.

### CVE Check

- `pytest>=8.0` — no known CVEs in 8.x series affecting normal test use
- `pytest-cov>=4.1` — no known CVEs in 4.x series affecting normal test use

### Conclusion

No supply-chain risk from F-128 dependency additions.

---

## Finding 7 — MCP Image Generation Supply-Chain Analysis

**Status**: INFO (non-blocking observation)

### Overview

Task T033 used the `mcp__mcp-image__generate_image` MCP tool (Gemini
backend) to render `threat-executive-architecture.jpg` from the spec
file's Section 6 prompt. This is the only external service call in the
F-128 workflow.

### Data Flowing to the External Service

The prompt passed to Gemini contains:

- Architectural layer names: "User Zone", "External Services",
  "Application Zone"
- Component names: "User", "External API", "Audit Logger", "Guardrails
  Service", "Knowledge Base", "LLM Agent Orchestrator", "MCP Tool Server"
- One callout narrative: "An attacker can craft a trick prompt that
  overrides the AI assistant's safety rules and makes it behave in
  unapproved ways."
- Styling directives (hex colors, font sizes, layout instructions)

All of this content is derived from the pre-existing sanitized agentic-app
fixture. No customer data, no real threat models, no credentials are
passed to Gemini.

### Prompt Injection Risk

The prompt is deterministically constructed by the extraction script from
fixed template strings plus fixture payload fields. Because the fixture
is checked into the repository and does not accept untrusted input at
generation time, there is no live prompt-injection vector. A contributor
who wished to poison the prompt would need to modify committed source
files, which would be visible in code review.

However, in **user deployments** that run the F-128 template against
real threat models, a supply-chain concern exists:

> If a user generates the executive-architecture infographic against a
> real customer threat model, the callout narrative and layer/component
> names are transmitted to the Gemini API. This is an acceptable pattern
> (identical to the existing baseball-card, system-architecture, and
> risk-funnel templates which already transmit threat content to Gemini),
> but it is a concern consultants must consider when deciding whether to
> upload their threat model content to a third-party image service.

### Recommendation

Document the data-flow expectation once in the
`.claude/skills/tachi-infographics/` reference material: "All infographic
templates that call Gemini transmit their payload to Google's image
generation API. Do not run infographic generation against threat models
whose content is classified above the level authorized for transmission
to Google." This guidance applies to ALL five pre-existing infographic
templates in addition to F-128 and is not a regression introduced by
F-128.

### Data Exfiltration Risk

Running tachi tests or the extraction script alone does NOT call the
MCP image tool. The MCP call happens only when the threat-infographic
agent explicitly invokes it. Script-level unit tests, backward
compatibility tests, and PDF compilation are all offline and make no
network calls.

### Conclusion

The MCP tool call is **safely scoped** for F-128's agentic-app example
regeneration because the input is a sanitized fixture. The tool's use
does introduce a data-flow dependency on Google's Gemini service for
*user deployments* that is consistent with existing infographic templates
and does not represent a regression. A one-time documentation update is
recommended (INFO severity, non-blocking).

---

## Finding 8 — Spec Artifact Content Review

**Status**: PASS

### Scan Targets

All 16 files in `specs/128-prd-128-executive/` — spec.md, plan.md, tasks.md,
decisions.md, checkpoint-p0.md, checkpoint-p1.md, NEXT-SESSION.md,
manual-verification.md, quickstart.md, data-model.md, research.md,
agent-assignments.md, contracts/, checklists/.

### Results

- **Email addresses**: 0
- **Phone numbers**: 0
- **AWS/OpenAI/GitHub keys**: 0
- **Private keys**: 0
- **Local user paths** (`/Users/...`): 0
- **Hardcoded credentials or tokens**: 0

The only numeric strings that triggered generic regex patterns were
`SOURCE_DATE_EPOCH=1700000000` (a Unix timestamp constant documented as
a reproducible-build env var) and SARIF `primaryLocationLineHash` content
hashes — both benign.

### Conclusion

Spec artifacts are clean. No sensitive content was committed to the
feature workspace.

---

## Overall Conclusion

### Summary

Feature 128 introduces a new infographic template (`executive-architecture`),
adds 5 new pytest-based test modules, regenerates the agentic-app example
with a Gemini-produced JPEG, and adds two defensive fixes to the
attack-tree parser and Typst remediation iteration. Across all changed
files and generated artifacts, **no PII, credentials, secrets, or
sensitive data were introduced**.

The JPEG carries positive C2PA attestation from Google confirming Gemini
origin, contains no embedded documents, and its prompt was derived
entirely from a pre-existing sanitized fixture. The Python changes
introduce no new network, subprocess, or dangerous-sink usage.

### Dependency Changes

Only dev-only test dependencies (`pytest`, `pytest-cov`) were added.
Zero new production dependencies.

### Observations (Non-Blocking)

1. **INFO — MCP / Gemini data flow for user deployments**: Users who run
   the executive-architecture template against real customer threat
   models should be aware their payload transits the Google Gemini API.
   This is consistent with the existing 5 infographic templates and is
   not a regression. Recommend adding a one-line data-flow note to
   `.claude/skills/tachi-infographics/SKILL.md`. Non-blocking.

### Status

**APPROVED_WITH_CONCERNS** — safe to merge. The single INFO observation is
a documentation-only recommendation that applies to the infographic
subsystem as a whole (not just F-128) and should be handled as a small
follow-up.
