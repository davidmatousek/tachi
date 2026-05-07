# ADR-044: Dual-Frame Public Positioning — Threat Modeling and AI-Reasoning Vulnerability Detection Harness

**Status**: Accepted
**Date**: Proposed: 2026-05-07; Accepted: 2026-05-07
**Deciders**: Project owner (davidmatousek)
**Feature**: [264-dual-frame-public-positioning](https://github.com/davidmatousek/tachi/issues/264) — public-positioning record (no implementation work)
**Supersedes**: None
**Superseded by**: None
**Related ADRs**: None — this ADR has no code or schema impact.

---

## Context

Through v4.31.0, tachi's public positioning was "automated threat modeling sidecar for your projects." Two things had drifted from that frame:

**Drift 1 — Single frame masked the dual product.** The product is functionally two views of one engine:

1. **Threat modeling** — the artifact view: structured `threats.md`, SARIF, narrative report, attack trees, MAESTRO classification.
2. **AI-reasoning vulnerability detection** — the scanning modality: tachi reasons over architecture descriptions to surface logic-level risks SAST cannot detect, the same way SAST surfaces syntax-level ones.

This dual frame already shaped the three-product strategy (SAST / AI Reasoning Scan / Agent Governance, with AI Reasoning Scan as the middle product) and the signature framing "SAST catches syntax. AI reasoning catches logic." The public surface lagged.

**Drift 2 — "Sidecar" no longer fit the architectural metaphor.** A sidecar runs *next to* a main process — it's a passive companion. Tachi instruments and drives the architecture under analysis: it parses the input, dispatches 14 specialized agents to probe each component, asserts findings, and produces structured outputs. That behavior matches a **harness** (test harness, evaluation harness) rather than a sidecar. The harness wraps the project; the project's architecture description runs *through* the harness.

## Decision

Adopt a dual-frame public positioning with **"harness"** as the primary architectural noun:

- **Headline**: "Threat Modeling and Vulnerability Detection Harness for Claude Code"
- **Sub-line**: "AI-Reasoning Scanner — STRIDE + AI + MAESTRO"
- **Signature framing**: "SAST catches syntax-level bugs; tachi reasons over your architecture description to catch logic-level ones."

Updated surfaces in this PR (Issue #264):

| Surface | Change |
|---------|--------|
| `README.md` (line 3) | Headline + sub-line; "What is tachi?" lead reframed; cycle-outcomes poster added at top; duplicate funnel image removed |
| `docs/product/01_Product_Vision/product-vision.md` | Mission, Vision, Core Value Proposition reframed |
| `.claude/rules/scope.md` (first bullet) | "Sidecar" → "harness"; deployment context tightened to Claude Code |
| `docs/guides/DEVELOPER_GUIDE_TACHI.md` (title) | Reflects dual frame |
| GitHub repo description | Applied manually post-merge |
| `brand/posters/2026-05-08-cycle-outcomes-poster.jpg` | New brand asset; visual confirmation of the dual frame |

## Consequences

### Positive
- Public surface matches the internal three-product mental model (SAST / AI Reasoning Scan / Agent Governance).
- Adopters reading the README can place tachi alongside their existing scanning tools (a column in the dashboard, not a separate methodology).
- "Harness" communicates instrumentation accurately — adopters understand that tachi wraps and drives the analysis, not that it sits passively beside the project.
- The "logic vs. syntax" framing gives prospective users an immediate, concrete contrast with familiar tooling.

### Neutral / Negative
- "Sidecar" language is dropped from public surfaces. Adopters who recognized the term will see the new framing on their next visit; the install model itself is unchanged.
- `.claude/rules/scope.md` retains pre-existing AOD-Kit-vs-tachi conflation in bullets 2–5 (e.g., "Works with any agent workflow or framework — not Claude Code-specific" contradicts the new deployment context). Cleanup deferred to a follow-up PR.
- `CONTRIBUTING.md` still says "Contributing to AOD Kit" with a stale clone URL pointing at `agentic-oriented-development-kit`. Cleanup deferred to a follow-up PR.

## What Does Not Change

This ADR is a positioning record. Out of scope:

- **No code changes** — no scanning engine, agent, schema, SARIF, or command behavior is modified.
- **No agent surface changes** — the 14 detection agents and 7 utility agents are unchanged in name, prompt, or output.
- **No methodology changes** — STRIDE-per-Element dispatch (ADR-003), MAESTRO classification (ADR-021 family), Pattern Synthesis (ADR-026), source attribution schema (ADR-028), and OWASP coverage (ADRs 035–037) are unchanged.
- **No deployment-context changes** — tachi continues to run inside Claude Code; the install model and prerequisites are unchanged.
- **No pricing or licensing changes** — Apache 2.0, no commercial pivot.
- **No internal-strategy changes** — `_internal/strategy/BLP-01`, `BLP-02`, `BLP-03`, prior ADRs, and PRDs are point-in-time records and are not edited.

## Compliance

- Internal-strategy artifacts and ADRs 001–043 are point-in-time records and are not edited.
- `CONSUMER_GUIDE_TACHI.md` is immutable per the project's documentation lineage policy and is not edited.
- Adopter-facing release notes (CHANGELOG.md) document the rename; release-please cuts a `feat:` minor bump because the change is visible to adopters.
