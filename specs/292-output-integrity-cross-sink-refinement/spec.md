---
prd_reference: docs/product/02_PRD/292-output-integrity-cross-sink-refinement-2026-05-14.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-14
    status: APPROVED_WITH_CONCERNS
    notes: "0H / 3M / 3L. Spec faithfully translates all 12 PRD FRs, 7 NFRs, 12 SCs, 5 user stories, 3 gap closures. Architect-owned Q1-Q5 correctly deferred via Assumption A-7 + conditional FRs (not [NEEDS CLARIFICATION]). F-260 community-merge precedent translated with highest fidelity in tachi history (4 mechanical artifacts: CHANGELOG form, 7-day SLA, comment-first-give-choice, Co-Authored-By trailer). Findings flow into /aod.project-plan: M-1 Q3 ADR commitment tension (spec hard-codes MUST author; PRD frames as deferred-to-planning with no-ADR exception option) - recommend FR-016 modifier OR Assumption A-8 capturing Principle X exception path; M-2 R2 partial translation (output-handling vs poisoning corpus framing edge case missing) - recommend adding edge case OR strengthening FR-002 worked-example prose; M-3 Conditional baseline emission verification not gated by dedicated SC (covered semantically by SC-001 but not explicitly) - recommend conditional SC-015 if Q2=Add; L-1 F-4 trust-exploitation not explicitly cross-referenced in FR-010 (catch-all covers it); L-2 Architect M2 byte-identical full-pipeline diff vs SC-003 OI-scoped restriction tension; L-3 Architect L3 follow-up notification at Q5 SLA breach deferred to planning. Full review at .aod/results/product-manager.md."
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: Output-Integrity Cross-Sink Refinement

**Feature Branch**: `292-output-integrity-cross-sink-refinement`
**Created**: 2026-05-14
**Status**: Draft
**Input**: User description: "PRD: 292 - Output-Integrity Cross-Sink Refinement"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Multi-Tenant RAG Tenant-Scoping Signal (Priority: P1)

A security analyst is running a tachi threat-model scan against the architecture description of a multi-tenant RAG application. The application uses a vector database (Qdrant or Pinecone) and synthesizes metadata filters from LLM output to scope retrieval to the requesting tenant's documents. Today, the `output-integrity` agent emits no finding when the LLM-synthesized filter could omit the tenant-scoping clause — leaving the analyst with no signal about what is functionally a vector-DB equivalent of SQL injection across tenant boundaries.

**Why this priority**: This story closes the highest-frequency, highest-impact gap surfaced by the community contributor. Multi-tenant RAG is one of the most common adopter architectures, and the OWASP LLM08:2025 Vector and Embedding Weaknesses entry names "missing tenant isolation in multi-tenant RAG systems" as a canonical industry vulnerability. Shipping this signal alone delivers measurable adopter value.

**Independent Test**: Run `tachi.threat-model` against an architecture description containing an LLM Process that emits a Pinecone or Qdrant metadata filter into a multi-tenant query interface. Verify at least one `output-integrity` finding is emitted that names the vector-DB engine and the tenant-scoping bypass, with a mitigation that references at least one of: pre-retrieval filtering (server-side filter composition), allowlisted clause keys, or tenant filter pinning.

**Acceptance Scenarios**:

1. **Given** an architecture description containing an LLM Process emitting a Qdrant `must` / `must_not` filter into a multi-tenant query interface, **When** the analyst runs `tachi.threat-model`, **Then** the `output-integrity` agent emits at least one finding with `category` referencing query-DSL / vector-filter injection, `cwe.primary` set to `CWE-943` (Improper Neutralization of Special Elements in Data Query Logic), `owasp.primary` referencing OWASP LLM08:2025 or LLM05:2025, and `mitigation` naming at least one industry-recognized control (pre-retrieval filtering, base filter that cannot be overridden, namespace-per-tenant, or allowlisted clause keys).
2. **Given** an architecture description containing an LLM Process emitting a Pinecone metadata filter, **When** the analyst runs `tachi.threat-model`, **Then** the same finding class emits with the Pinecone-specific terminology surfaced in the worked example.
3. **Given** an architecture description with no LLM-synthesized query-language output, **When** the analyst runs `tachi.threat-model`, **Then** the `output-integrity` agent emits zero new findings under the vector-filter pattern surface (no false positives on architectures that lack the trigger signals).

---

### User Story 2 - AI-Coding-Assistant Package-Manager Signal (Priority: P1)

A security analyst is reviewing an AI-coding-assistant deployment whose LLM Process generates `npm install`, `pip install`, or GitHub Actions YAML steps from user input. Today, the `output-integrity` agent catches generic shell injection (`bash -c "rm -rf $LLM_OUTPUT"`) but emits no finding when the same LLM Process emits `npm install <attacker-controlled-name>` into a generated install script — even though both are functionally LLM-output-into-execution-sink. The analyst wants the same agent to catch both, without maintaining a second detection layer.

**Why this priority**: 2026 incident record shows this is an active attack surface: the SANDWORM_MODE npm worm injected prompt-injection blocks into AI assistant tool descriptions in early 2026; the LiteLLM PyPI compromise exfiltrated credentials via a `.pth` payload in March 2026. Academic literature (arXiv 2605.07135) formalizes the "Agentic Workflow Injection" attack pattern. Adopters building AI coding assistants need the signal urgently.

**Independent Test**: Verify the agent's trigger-keyword list includes package-manager and CI-workflow keywords (at minimum: `npm install`, `pip install`, `apt install`, `brew install`, `gh workflow`, `actions/`, `uses:`, `package-lock`, `requirements.txt`). Verify at least one worked example exercises the package-manager sink with a documented mitigation (allowlist of registries and scopes, microVM/gVisor/hardened-container sandbox, or Sigstore-backed signature verification).

**Acceptance Scenarios**:

1. **Given** an architecture description with an LLM Process emitting `npm install` strings into a generated install script execution sink, **When** the analyst runs `tachi.threat-model`, **Then** the `output-integrity` agent emits at least one finding referencing the package-manager execution surface with a mitigation naming at least one industry-recognized control (allowlist of registries and scopes, sandbox isolation via microVM/gVisor/hardened-container, or Sigstore-backed signature verification).
2. **Given** an architecture description with an LLM Process emitting GitHub Actions YAML (`uses:`, `gh workflow`, `actions/`) into a CI workflow execution sink, **When** the analyst runs `tachi.threat-model`, **Then** the agent emits at least one finding referencing the CI-workflow execution surface with the same mitigation taxonomy.
3. **Given** an architecture description with no LLM-synthesized package-manager or CI-workflow output, **When** the analyst runs `tachi.threat-model`, **Then** the agent emits zero new findings under the package-manager pattern surface (signals must require both trigger-keyword AND downstream-sink-indicator presence, no false positives on prose mentions of "npm" or "pip" outside execution-sink context).

---

### User Story 3 - Multi-Agent Handoff Boundary Navigation (Priority: P2)

A security analyst is running tachi against a multi-agent architecture where LLM output flows into a tool-call argument or a durable memory write. Today, three different agents emit overlapping findings: `output-integrity` on the encoding/sanitization signal, `tool-abuse` on the tool-argument injection signal, and `data-poisoning` on the durable-memory-write signal. The analyst wants `output-integrity` to surface a navigational pointer to the adjacent agents — making the boundary explicit so the analyst can attribute each finding to the correct owning agent rather than reconciling three disjoint findings.

**Why this priority**: This is a documentation and navigation refinement, not a new emission surface. It does NOT change finding counts on existing baselines — it improves the analyst's ability to reason about the multi-agent handoff boundary. Lower priority than US-1/US-2 because it adds clarity, not new signal.

**Independent Test**: Read the updated pattern catalog and the agent file's Purpose section. Verify a "Cross-Agent Handoff Sinks" subsection exists that (a) states the boundary explicitly ("harmless as text, dangerous as tool argument or memory entry"), (b) cross-links to the tool-abuse agent for tool-argument flows, (c) cross-links to the data-poisoning agent for durable-memory-write flows, (d) includes a Memory-Promotion Rules mitigation pattern with a worked schema example, and (e) explicitly states that the `output-integrity` agent does NOT emit findings on those handoff flows. Confirm by re-running an existing multi-agent baseline (e.g., `agentic-app/`) and verifying zero new `output-integrity`-tagged findings are emitted from the cross-link prose alone.

**Acceptance Scenarios**:

1. **Given** the refined `output-integrity` pattern catalog, **When** an analyst reads the "Cross-Agent Handoff Sinks" subsection, **Then** the subsection explicitly names the two handoff classes (tool-call argument, durable-memory write), explicitly states the boundary phrase ("harmless as text, dangerous as tool argument or memory entry"), and cross-links to the tool-abuse agent file and the data-poisoning agent file.
2. **Given** the refined `output-integrity` pattern catalog, **When** an analyst reads the Memory-Promotion Rules mitigation pattern, **Then** the pattern includes a worked schema example with at minimum: an allowlist of promotable keys, a value-schema reference, and a tenant-scope pin. The pattern cites OWASP ASI06 Memory & Context Poisoning (NOT OWASP LLM04) and references the A-MEMGUARD staging-buffer framing as an optional layered control.
3. **Given** an existing multi-agent baseline (`agentic-app/`) that today produces N `output-integrity` findings, **When** the analyst re-runs `tachi.threat-model` after the refinement is merged, **Then** the baseline produces exactly N `output-integrity` findings (zero new emissions from the cross-link prose alone) and the `output-integrity`-scoped finding set reproduces byte-identical under `SOURCE_DATE_EPOCH=1700000000`.
4. **Given** the refined `output-integrity` agent file, **When** an analyst reads the Purpose section, **Then** a navigational sentence (≤2 sentences, total agent-file diff ≤10 lines) points to the tool-abuse agent for tool-argument handoff and to the data-poisoning agent for durable-memory-write handoff, AND explicitly states that `output-integrity` does NOT detect those handoff cases.

---

### User Story 4 - Community-Contribution Attribution Chain (Priority: P3)

The tachi maintainer receives a thoughtful gap-analysis comment from a first-time contributor on a public discussion thread. The maintainer wants this feedback to convert into a shipped refinement with the contributor's authorship preserved through every stage of the contribution chain — comment → PRD → PR → CHANGELOG — so external contributors see their input land in shipped code and return for more contributions.

**Why this priority**: Process / governance story. Independent of the technical changes (US-1, US-2, US-3) but essential to honoring the community-merge precedent. F-260 (PR #262, @north-echo, v4.31.0) is the canonical precedent the project commits to follow. P3 because the attribution work happens at delivery time and doesn't block the technical refinement.

**Independent Test**: Inspect the CHANGELOG entry for the release containing this refinement and verify it explicitly attributes the contributor's GitHub handle. Inspect the discussion thread the contribution originated from and verify a delivery comment was posted within 24 hours of merge, linking the PR, the relevant pattern-catalog anchors for each gap closure, and the CHANGELOG section. The attribution form must match the F-260 precedent (`* **{NNN}:** {title} ([#{PR}](...)) ({SHA7})`) and, if maintainer-authored, include a `Co-Authored-By:` commit trailer (subject to contributor agreement).

**Acceptance Scenarios**:

1. **Given** the release containing this refinement, **When** an external observer reads `CHANGELOG.md`, **Then** the entry for that release explicitly attributes the contributor's preferred GitHub handle (confirmed via the discussion reply) in a form that matches the F-260 precedent.
2. **Given** the merged PR, **When** the maintainer checks the originating discussion thread within 24 hours of merge, **Then** a delivery comment has been posted that links the PR, the pattern-catalog file anchor for each of the three gap closures, and the CHANGELOG section. [MANUAL-ONLY] reviewer reads CHANGELOG + discussion comment.
3. **Given** the maintainer-authored path is taken (contributor declines or SLA breach), **When** an observer inspects the commit history for the refinement, **Then** at least one commit carries a `Co-Authored-By:` trailer for the contributor (if the contributor agreed to that form).

---

### User Story 5 - First-Time Contributor On-Ramp (Priority: P3)

The first-time contributor whose gap-analysis comment surfaced this refinement wants a clear, low-friction path to either authoring the PR themselves (with maintainer steerage) OR having their gap-surfacing attributed in the CHANGELOG when the maintainer authors the PR. Either path must result in their contribution being recognized; neither path should require them to absorb the full maintainer workflow if they only have time for the original comment.

**Why this priority**: Honors the F-260 community-merge precedent and the project's external-contributor-collision policy (comment-first-give-choice, path A default). P3 because the contributor-handoff offer runs in parallel non-blocking — the technical work (US-1, US-2, US-3) proceeds on the maintainer track regardless.

**Independent Test**: Inspect the originating discussion thread within 48 hours of this specification being signed off. Verify a public reply offers two choices: (a) contributor authors the PR with maintainer steerage (issue assignment + branch suggestion + review-ready guidance per F-260 precedent), or (b) maintainer authors the PR with explicit CHANGELOG attribution + commit-trailer attribution (if the contributor agrees). Verify that if no contributor response arrives within 7 days, the default fallback to (b) is invoked with explicit attribution.

**Acceptance Scenarios**:

1. **Given** this specification is signed off, **When** the maintainer posts a public reply on the originating discussion thread within 48 hours, **Then** the reply explicitly offers both paths (a) and (b) and names the 7-day response SLA. [MANUAL-ONLY] reviewer inspects discussion reply timestamp and content.
2. **Given** the contributor accepts path (a), **When** the contributor opens a PR within 7 days, **Then** the maintainer provides issue assignment, branch suggestion, and review-ready guidance per the F-260 precedent, and the contributor's PR remains the merged artifact under their authorship. [MANUAL-ONLY] reviewer inspects PR authorship and maintainer support comments.
3. **Given** the contributor does not respond within 7 days OR explicitly accepts path (b), **When** the SLA elapses or path (b) is confirmed, **Then** the maintainer authors the PR with `Co-Authored-By:` trailer (subject to contributor agreement) and explicit CHANGELOG attribution.

---

### Edge Cases

- **What happens when an architecture description mentions package-manager keywords (`npm install`, `pip install`) in prose context but no execution-sink indicator is present?** The agent MUST NOT emit a finding. Detection requires both a trigger keyword AND a downstream-sink-indicator signal; lone keyword mentions in commentary, documentation prose, or non-execution contexts do not qualify.
- **How does the system handle an LLM Process that emits a Pinecone filter to a single-tenant deployment with no tenant-scoping requirement?** The agent SHOULD NOT emit a vector-filter tenant-scoping finding on architectures that lack the multi-tenancy signal. Detection requires the architectural signal of multi-tenancy (`tenant_id` payload, namespace per tenant) in the data flow.
- **What happens when LLM output flows into a tool-call argument that is also a SQL query (both `tool-abuse` and `output-integrity` could plausibly claim ownership)?** Both findings can co-emit on the same architecture without contradiction. The cross-link prose makes this disjoint-tells boundary explicit: `output-integrity` owns the encoding/sanitization signal at the SQL-string-construction site; `tool-abuse` owns the tool-argument-passing site. Adopters see both findings with disjoint mitigation taxonomies.
- **How does the system handle a vector-filter that uses a base filter pinned by the application layer?** The pinned-filter pattern is the recommended mitigation. If the architecture description states the tenant filter is composed server-side (pre-retrieval filtering / base filter that cannot be overridden), the agent SHOULD recognize the mitigation and either suppress the finding or emit at a lower severity. Architect resolves the precise threshold during planning.
- **What happens when the contributor responds within the 7-day SLA but cannot deliver a PR in a reasonable timeframe?** The maintainer escalates to path (b) (maintainer-authored) with explicit attribution; the contributor's authorship is preserved via CHANGELOG + commit-trailer rather than native PR authorship.
- **How does the system handle the discussion-closure SLA slipping past 24 hours due to weekend or end-of-day merge?** The 24-hour SLA on the delivery comment is a quality-of-experience target, not a delivery gate. Best-effort within the next business day is acceptable.
- **What happens if a reviewer argues for a new finding-id prefix (e.g., `OQ-{N}` for "output query injection") instead of reusing the existing `OI-{N}` prefix?** The schema-bump constraint is non-negotiable. The existing `OI-{N}` prefix is preserved per ADR-030 Decision 8. A new prefix would cascade to populator wiring, taxonomy crosswalks, and source-attribution contracts — high blast radius, expressly out of scope.

## Requirements *(mandatory)*

> **Acceptance Criteria Rule**: Each AC MUST begin with **Given** and follow Given/When/Then structure. Use `[MANUAL-ONLY] <reason>` (reason ≥10 chars) inline to mark ACs that cannot be automated.

### Functional Requirements

- **FR-001**: The `output-integrity` pattern catalog MUST include at least one explicitly-named pattern surface for vector-filter / search-DSL injection (Gap 1). The pattern surface MAY be a new top-level category OR an extension to an existing Server-Side Execution Sinks category — placement is an architectural decision deferred to planning.

- **FR-002**: The vector-filter pattern surface MUST include at least one worked example referencing a named vector-DB engine (Qdrant OR Pinecone OR both), the tenant-scoping bypass mechanism, and a mitigation field naming at least one industry-recognized control (pre-retrieval filtering / server-side filter composition, base filter that cannot be overridden, namespace-per-tenant, or allowlisted clause keys).

- **FR-003**: The vector-filter pattern surface MUST cite OWASP LLM08:2025 (Vector and Embedding Weaknesses) and/or OWASP LLM05:2025 (Improper Output Handling) as the primary OWASP framework anchor, AND MUST cite CWE-943 (Improper Neutralization of Special Elements in Data Query Logic) as the primary CWE anchor. CWE-89 (SQL Injection) is acceptable as a taxonomic neighbor; CWE-94 is acceptable when the filter is templated as an expression.

- **FR-004**: The Server-Side Execution Sinks and/or Path Traversal + Unsafe File Writes trigger-keyword lists MUST include at minimum the following package-manager and CI-workflow keywords (Gap 2): `npm install`, `pip install`, `apt install`, `brew install`, `gh workflow`, `actions/`, `uses:`, `package-lock`, `requirements.txt`.

- **FR-005**: At least one worked example MUST exercise the package-manager / CI-workflow sink with a documented mitigation naming at minimum one of: allowlist of registries and scopes, sandbox isolation (microVM, gVisor, hardened container, or equivalent), or Sigstore-backed signature verification (`npm audit signatures` or equivalent). The worked example SHOULD note that layered controls (allowlist AND sandbox AND signature) provide defense-in-depth.

- **FR-006**: The pattern catalog MUST include a "Cross-Agent Handoff Sinks" subsection (Gap 3) that (a) states the boundary explicitly ("harmless as text, dangerous as tool argument or memory entry"), (b) cross-links to the tool-abuse agent for tool-call-argument handoff, (c) cross-links to the data-poisoning agent for durable-memory-write handoff, and (d) cites OWASP ASI06 Memory & Context Poisoning (NOT OWASP LLM04) as the canonical anchor for durable memory poisoning.

- **FR-007**: The "Cross-Agent Handoff Sinks" subsection MUST explicitly state that the `output-integrity` agent does NOT emit findings on tool-argument or durable-memory-write flows — those flows remain owned by the tool-abuse and data-poisoning agents respectively. This invariant MUST be testable by re-running an existing multi-agent baseline and verifying zero new `output-integrity`-tagged findings are emitted from the cross-link prose alone.

- **FR-008**: The pattern catalog MUST include a Memory-Promotion Rules mitigation pattern with a worked schema example containing at minimum: (a) an allowlist of promotable keys, (b) a value-schema reference, and (c) a tenant-scope pin. The pattern SHOULD reference the A-MEMGUARD staging-buffer framing as an optional layered control beyond schema validation alone.

- **FR-009**: The `output-integrity` agent file Purpose section MUST include navigational cross-link prose (≤2 sentences) pointing to the tool-abuse agent (for tool-argument handoff) and the data-poisoning agent (for durable-memory-write handoff). Total agent-file diff MUST be ≤10 lines.

- **FR-010**: NO modifications are permitted to the tool-abuse agent file, the tool-abuse companion skill references, the data-poisoning agent file, or the data-poisoning companion skill references — or to any other threat-agent file in this feature. Cross-links flow OUT of `output-integrity` only; target agents are referenced but unchanged.

- **FR-011**: NO `schemas/finding.yaml` schema bump is permitted. The existing `OI-{N}` finding-id prefix is reused for any new pattern surfaces. The schema-version field remains unchanged.

- **FR-012**: (Conditional, architectural decision deferred to planning) If a new multi-tenant RAG example baseline is added to exercise the vector-filter pattern surface, the baseline MUST emit at least one `output-integrity` finding under the new pattern surface AND reproduce byte-identical under `SOURCE_DATE_EPOCH=1700000000`.

- **FR-013**: A CHANGELOG entry for the release containing this refinement MUST explicitly attribute the originating contributor's preferred GitHub handle. The attribution form MUST match the F-260 precedent (`* **{NNN}:** {title} ([#{PR}](...)) ({SHA7})`).

- **FR-014**: A delivery comment MUST be posted on the originating discussion thread within 24 hours of PR merge, linking the PR, the pattern-catalog anchor for each gap closure, and the CHANGELOG section. The 24-hour SLA is best-effort; next-business-day is acceptable for weekend or end-of-day merges.

- **FR-015**: A public reply MUST be posted on the originating discussion thread within 48 hours of this specification being signed off, offering two contribution paths: (a) contributor-authored PR with maintainer steerage, or (b) maintainer-authored PR with explicit CHANGELOG and commit-trailer attribution. The reply MUST name a 7-day response SLA and the default fallback to (b) at SLA breach.

- **FR-016**: An Architecture Decision Record (ADR) MUST be authored documenting the architectural decisions resolved during planning (pattern-surface placement, optional new baseline inclusion, cross-link prose scope, Memory-Promotion Rules placement). The ADR slot is the next available number after reserved slots. The ADR MUST follow the Proposed → Accepted dual-commit governance protocol (Proposed at planning lock, Accepted at pre-PR with `<pending-post-merge-fill>` placeholder on Accepted-commit-SHA, post-merge SHA fill at delivery).

### Key Entities

- **Output-Integrity Pattern Catalog**: The structured reference document that enumerates the threat patterns the `output-integrity` agent detects. Currently contains five pattern categories (XSS/DOM, server-side execution, SSRF, template injection, path traversal). This refinement adds one new pattern surface (vector-filter / search-DSL injection — placement TBD in planning), extends two existing trigger-keyword lists (package-manager and CI-workflow keywords), and adds one new navigational subsection (Cross-Agent Handoff Sinks with Memory-Promotion Rules mitigation pattern).

- **Output-Integrity Agent File**: The agent definition that orchestrates `output-integrity` detection. This refinement appends a navigational cross-link sentence to its Purpose section (≤10 line diff).

- **Cross-Link Target Agents**: The tool-abuse agent and the data-poisoning agent. Referenced by the Cross-Agent Handoff Sinks subsection but unchanged by this refinement.

- **Finding Schema**: The shared schema defining the `OI-{N}` finding-id format. Reused without modification.

- **Multi-Agent Baseline**: An existing example architecture (`agentic-app/` or similar) used to verify the cross-link prose does not trigger new emissions. Byte-identity preserved under `SOURCE_DATE_EPOCH=1700000000`.

- **Multi-Tenant RAG Baseline** (conditional): An optional new example architecture exercising the vector-filter pattern surface. Inclusion is an architectural decision deferred to planning.

- **CHANGELOG Entry**: The release-notes record attributing the originating contributor. Form matches F-260 precedent.

- **Discussion Thread Replies**: Two replies on the originating discussion: the 48-hour two-choice offer, and the 24-hour delivery comment. Both preserve the F-260 community-merge attribution chain.

- **Architecture Decision Record (ADR)**: The architectural-decision document recording the planning-stage resolutions. Authored at the next-available slot per BLP-01 enrichment-branch lineage.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The vector-filter pattern surface emits at least one `output-integrity` finding on a multi-tenant RAG architecture (Qdrant or Pinecone) whose LLM-synthesized filter could omit the tenant-scoping clause, naming the engine and citing OWASP LLM08:2025 / LLM05:2025 and CWE-943.

- **SC-002**: The package-manager pattern surface emits at least one `output-integrity` finding on an architecture whose LLM Process emits `npm install` or equivalent into an execution sink, with a mitigation naming at minimum one industry-recognized control (allowlist of registries and scopes, sandbox isolation, or Sigstore-backed signature verification).

- **SC-003**: The cross-link prose does NOT cause new emissions on an existing multi-agent baseline. A multi-agent baseline (`agentic-app/` or equivalent) produces exactly the same `output-integrity` finding count before and after this refinement, and the `output-integrity`-scoped finding output reproduces byte-identical under `SOURCE_DATE_EPOCH=1700000000` (scope restricted to `output-integrity` findings, not whole-pipeline diff, to avoid the F-248-style over-scoped byte-comparison trap).

- **SC-004**: The five non-qualifying baselines (`web-app/`, `microservices/`, `ascii-web-api/`, `mermaid-agentic-app/`, `free-text-microservice/`) reproduce byte-identical under `SOURCE_DATE_EPOCH=1700000000` after this refinement is merged.

- **SC-005**: A reader reviewing the `output-integrity` agent file's Purpose section can identify, in ≤30 seconds, that the agent owns the encoding/sanitization signal class and does NOT detect tool-argument or durable-memory-write handoff flows. Verified by the presence of explicit cross-link navigational prose (≤10 line diff). [MANUAL-ONLY] reviewer reads the Purpose section.

- **SC-006**: A reader reviewing the Cross-Agent Handoff Sinks subsection can identify, in ≤60 seconds, (a) the boundary phrase, (b) the two cross-linked target agents, (c) the Memory-Promotion Rules mitigation pattern with allowlist + schema + tenant-scope, and (d) the OWASP ASI06 canonical anchor. [MANUAL-ONLY] reviewer reads the subsection.

- **SC-007**: The originating contributor's preferred GitHub handle appears in the CHANGELOG entry for the release containing this refinement, in the F-260 attribution form. [MANUAL-ONLY] reviewer inspects CHANGELOG.

- **SC-008**: A delivery comment is posted on the originating discussion thread within 24 hours of PR merge (or next-business-day for weekend / end-of-day merges), linking the PR, the pattern-catalog anchor for each gap closure, and the CHANGELOG section. [MANUAL-ONLY] reviewer inspects discussion timestamp and content.

- **SC-009**: A public reply offering the two-choice contribution paths is posted on the originating discussion thread within 48 hours of this specification being signed off, with the 7-day response SLA and default fallback to maintainer-authored named explicitly. [MANUAL-ONLY] reviewer inspects discussion timestamp and content.

- **SC-010**: Zero modifications are made to the tool-abuse agent file, the tool-abuse companion skill references, the data-poisoning agent file, the data-poisoning companion skill references, or any other threat-agent file. Verified by a structural diff of the threat-agent and skill-reference file surfaces.

- **SC-011**: Zero modifications are made to `schemas/finding.yaml`. Verified by structural diff. The `schema_version` field remains unchanged.

- **SC-012**: A post-merge security re-scan of the modified file surface emits zero new findings.

- **SC-013**: The PR title follows the Conventional-Commits format `feat(292): output-integrity cross-sink refinement` and a release-please release PR opens within 30 seconds of squash-merge to main.

- **SC-014**: An ADR documenting the architectural decisions is in `Accepted` status before squash-merge, with the post-merge Accepted-commit-SHA placeholder ready for fill at delivery.

## Assumptions

- **A-1**: The originating discussion thread remains open and the originating contributor remains reachable via their GitHub handle. If the contributor is unreachable, the maintainer-authored path with anonymized attribution proceeds with best-effort acknowledgment.

- **A-2**: The next available ADR slot after reserved slots is determined at the start of planning. ADR-043 is reserved for a future signed-updates decision; the actual slot allocated to this refinement is the next un-reserved number.

- **A-3**: The existing multi-agent baseline (`agentic-app/`) remains a valid regression-protection target. If the baseline is restructured during the refinement window, planning re-selects an equivalent multi-agent baseline.

- **A-4**: The 7-day contributor-response SLA is calendar days, not business days. Weekend and holiday windows count.

- **A-5**: The CHANGELOG generator (release-please or equivalent) renders the contributor handle from the squash-merge commit message or PR description. If the generator does not auto-link the handle, the maintainer adds the attribution line manually.

- **A-6**: The `output-integrity` agent's existing detection workflow already enforces the both-signal requirement (trigger-keyword AND downstream-sink-indicator). Pattern-catalog additions inherit this enforcement; no workflow logic changes are required.

- **A-7**: The vector-filter pattern-surface placement (top-level category vs sub-class extension), the optional new multi-tenant RAG baseline inclusion, the ADR authorship vs no-ADR-exception decision, the Memory-Promotion Rules surface placement (inline vs separate skill-reference file), and the contributor-handoff timing strategy are architectural decisions resolved during planning. The specification commits to the testable invariants; the architecture commits to the implementation choices.

## Dependencies

- **D-1**: The shipped F-1 `output-integrity` agent (parent feature) — merged and stable as of v4.21.0.

- **D-2**: The shared finding schema with the `OI-{N}` prefix — present at the current schema version with no further bump required.

- **D-3**: The shared CWE taxonomy containing CWE-943 — present in the catalog.

- **D-4**: The reproducible-builds discipline (`SOURCE_DATE_EPOCH=1700000000`) — established and plumbed into the regression test harness.

- **D-5**: The existing multi-agent baseline (`agentic-app/`) — present and regenerable.

- **D-6**: The community-merge precedent (F-260 / @north-echo / PR #262) — documented in the project's institutional knowledge and referenced as the canonical playbook.
