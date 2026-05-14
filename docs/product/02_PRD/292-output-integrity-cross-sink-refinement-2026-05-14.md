---
prd:
  number: 292
  topic: output-integrity-cross-sink-refinement
  created: 2026-05-14
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-05-14, status: APPROVED, notes: "PRD grounded in Issue #292 community-feedback gap-analysis. Three pattern-catalog gaps in F-1 output-integrity (PRD #201, ADR-030, v4.21.0): (1) vector-filter/search-DSL injection, (2) package-manager/CI-workflow execution sinks, (3) cross-agent handoff sinks + Memory-Promotion Rules mitigation. Heuristic A enrichment-branch at single-agent scope. Schema invariance preserved (no finding.yaml bump). Five user stories (multi-tenant RAG, AI coding-assistant, multi-agent, maintainer, first-time-contributor @armorer-labs). 12 success criteria. 5 Architect-owned open questions (Q1 Cat 6 vs Cat 2 sub-class, Q2 optional baseline, Q3 ADR yes/no, Q4 Memory-Promotion surface placement, Q5 authorship handoff timing) carved for /aod.plan resolution. F-260 community-merge precedent (@north-echo, PR #262) applied verbatim. 3 HIGH findings (Architect H1+H2 + Team-Lead H1) + Architect M1 CWE-943 flip resolved inline before sign-off. Remaining MEDIUM/LOW findings flow into /aod.plan per reviewers' guidance. Ready for /aod.plan."}
  architect_signoff: {agent: architect, date: 2026-05-14, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 2 HIGH / 4 MEDIUM / 3 LOW. H1 (Principle VII miscited as ADR-public; actual is Principle X) + H2 (F-3 mis-identified as data-poisoning; actual F-3 = tool-abuse enrichment PRD #219 / ADR-032 with authored ADR; F-6 BLP-01 = ML Top 10 bundle PRD #232 / ADR-035 at multi-host scope; BLP-01 lineage authors ADRs for enrichment branches) + M1 (CWE-89 lean for vector-filter is suboptimal; CWE-943 already in F-A1 catalog at schemas/taxonomy/cwe.yaml:250 is the canonical primary) ALL resolved inline. NFR-6 + Q3 + SC-12 + References re-anchored to Principle X. FR-3 flipped to CWE-943 primary / CWE-89 related / CWE-94 conditional. Remaining: M2 strengthen NFR-2/SC-5 to full byte-identical diff per ADR-021; M3 prose-strengthener on FR-7 locking one-way navigational invariant; M4 README+SC-3 wiring if Q2=Add baseline; L1 verify ADR-043 gap on plan day; L2 reiterate both-signal requirement on Gap 2 keywords; L3 follow-up notification at Q5 SLA breach. Architecture sound; Heuristic A enrichment-branch framing aligns with F-3 (ADR-032) + F-6 (ADR-035) precedent. Q1 lean: Cat 6 (CWE-943 distinct from CWE-89 satisfies decision criterion). Q3 lean: author ADR-045 (BLP-01 lineage). Full review at .aod/results/architect.md."}
  techlead_signoff: {agent: team-lead, date: 2026-05-14, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 1 HIGH / 3 MEDIUM / 3 LOW. Independent calendar verification (cal 5 2026): 2026-05-14 Thu, 2026-05-15 Fri, 2026-05-16 Sat, 2026-05-17 Sun, 2026-05-18 Mon, 2026-05-19 Tue, 2026-05-20 Wed, 2026-05-21 Thu — all correctly verified. H1 (Days 2-3 originally Sat+Sun without weekend-cadence acknowledgment) resolved inline by shifting to weekday-anchored path (B): Day 0 Thu 2026-05-14, Day 1 Fri 2026-05-15, Day 2 Mon 2026-05-18, Day 3 Tue 2026-05-19, Buffer-1 Wed 2026-05-20, Buffer-2 Thu 2026-05-21. Working-day effort unchanged at ~1.5 focused days; wall-clock extends 3→6 calendar days. Remaining: M-1 worst-case contingency (Q1=Cat 6 + Q2=Add + Q3=Add-ADR shifts /aod.deliver to Buffer-1) — added to timeline narrative; M-2 Wave-level parallelism (T1a∥T1b, T2a∥T2b) — added to critical-path narrative; M-3 maintainer 5-hour bandwidth confirmation for Q5 path (a) — flow into /aod.plan. Capacity reconciliation clean (no in-flight conflict; BLP-02 closed 2026-05-10; BLP-03 still PROPOSED). Hard dependencies all merged (F-1 ✓, finding.yaml v1.6 ✓, ADR-030 Accepted ✓). NFR-7 + SC-11 release-please feat() prefix correctly enforced per project memory feedback_aod_deliver_release_gate.md. Performance metrics balanced (senior-backend-engineer ~60% Day 1-2; tester ~30% Day 2-3; devops ~30% Day 3 PM). Full review at .aod/results/team-lead.md."}
source:
  idea_id: 292
  story_id: null
---

# F-292 — Output-Integrity Cross-Sink Refinement: Product Requirements Document

**Status**: Approved
**Created**: 2026-05-14
**Spec**: TBD (will land at `specs/292-output-integrity-cross-sink-refinement/spec.md` after `/aod.plan`)
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: Community-feedback refinement (follow-on to BLP-01 F-1 `output-integrity`, PR #202, v4.21.0)
**Priority**: P1
**Parent Feature**: PRD #201 — F-1 LLM05 `output-integrity` threat agent (delivered 2026-04-19)
**Source**: Discussion [#179 comment](https://github.com/davidmatousek/tachi/discussions/179#discussioncomment-16897078) from @armorer-labs (2026-05-12)

---

## 📋 Executive Summary

### The One-Liner

Close three pattern-catalog gaps in the shipped F-1 `output-integrity` agent — **vector-filter / search-DSL injection**, **package-manager / CI-workflow execution sinks**, and **cross-agent handoff sinks** — plus add **Memory-Promotion Rules** as a named mitigation pattern. Heuristic A enrichment branch at smallest scope (single-agent refinement + two light cross-links into `tool-abuse` and `data-poisoning`), with explicit authorship attribution preserved per the F-260 community-merge precedent.

### Problem Statement

The shipped F-1 `output-integrity` agent (PR #202, v4.21.0, 2026-04-19) ships five pattern categories — Cat 1 Client-Side Execution Sinks (XSS/DOM), Cat 2 Server-Side Execution Sinks (SQLi/OS Command/Code), Cat 3 SSRF, Cat 4 Template/Expression Injection, Cat 5 Path Traversal + Unsafe File Writes — covering the OWASP LLM05:2025 surface as scoped under ADR-030 Decision 2 (encoding/sanitization signal class, Heuristic A Outcome B). A 2026-05-12 first-time-contributor comment on discussion #179 from @armorer-labs proposed a four-class taxonomy (render / query / execution / agent-tool sinks) with the design principle "validate the downstream representation, not generic sanitization" — well-aligned with F-1's shipped mitigation philosophy.

A 2026-05-14 maintainer gap-analysis (this PRD's anchor) crosswalked @armorer-labs's four classes against the shipped F-1 catalog and identified three coverage gaps:

| @armorer-labs class | F-1 coverage today | Gap |
|---|---|---|
| Render sinks (HTML/MD/email/ticket) | Cat 1 Client-Side Execution Sinks | None — full coverage |
| Query sinks (SQL, **vector filters, search DSLs**, templates) | Cat 2 SQLi + Cat 4 Template Injection | **Gap 1** — vector filters & search DSLs NOT explicitly named |
| Execution sinks (shell, **package mgr, CI workflow**, code interpreter) | Cat 2 cmd/code + Cat 5 path traversal | **Gap 2** — package manager & CI workflow NOT in keyword list |
| **Agent/tool sinks** (next model turn, function-call args, MCP tool input, memory write) | Scattered: `tool-abuse` (param injection) + `data-poisoning` (memory writes) + `prompt-injection` (next turn) | **Gap 3** — no unified handoff-boundary framing in `output-integrity` |

A security analyst running tachi against a multi-tenant RAG application today gets **no signal** when an LLM synthesizes a Qdrant/Pinecone metadata filter that omits the tenant-scoping clause — yet this is functionally equivalent to SQLi against a tenant boundary. Similarly, an AI-coding-assistant adopter generating `npm install` or GitHub Actions YAML steps from LLM output gets **no signal** from the same `output-integrity` agent that already catches `bash -c "rm -rf $LLM_OUTPUT"` — even though both are LLM-output-into-execution-sink, the keyword list misses the package-manager surface. And a multi-agent adopter whose LLM output flows into a tool-call argument or a durable memory write today gets **three disjoint findings to reconcile** instead of a coherent finding chain anchored in `output-integrity`'s handoff-boundary framing.

These three gaps do not invalidate F-1's shipped behavior — they extend it to three high-frequency real-world sink classes the v4.21.0 release missed. The fix is a docs-heavy refinement: one updated pattern catalog file, one updated agent prose surface (cross-links), optional one new example baseline, zero schema bumps, zero new agents.

### Proposed Solution

A **Heuristic A enrichment branch at smallest scope** — refine the existing `output-integrity` agent's pattern catalog and add navigational cross-links into `tool-abuse` and `data-poisoning`:

1. **Gap 1 closure — Vector-Filter / Search-DSL Injection**: Add a new pattern category (Cat 6) to `.claude/skills/tachi-output-integrity/references/detection-patterns.md` covering LLM-synthesized vector-DB filters (Qdrant `must_not`, Pinecone metadata filter), Elasticsearch DSL queries, hybrid-search filter clauses, and other structured query languages that gate tenant/RBAC scoping. **Alternative placement**: extend Cat 2 (Server-Side Execution Sinks) with a vector-DB sub-class. The category-vs-sub-class boundary is an **architect decision** in `/aod.plan` (see Open Question Q1).

2. **Gap 2 closure — Package-Manager / CI-Workflow Keyword Extension**: Append `npm install`, `pip install`, `apt install`, `brew install`, `gh workflow`, `actions/`, `uses:`, `package-lock` write, `requirements.txt` write to Cat 2 (Server-Side Execution Sinks) and Cat 5 (Path Traversal + Unsafe File Writes) trigger-keyword lists. Add one worked example: AI coding assistant emits `npm install <attacker-controlled-name>` into a generated install script; mitigation = allowlist enum of permitted package names OR sandbox-only execution OR `npm audit signatures` gate.

3. **Gap 3 closure — Cross-Agent Handoff Sinks (prose-only, navigational)**: Add a new prose subsection to `detection-patterns.md` stating the boundary explicitly ("harmless as text, dangerous as tool argument or memory entry") and cross-linking to:
   - `.claude/agents/tachi/tool-abuse.md` for the tool-arg case (currently covered there under LLM06 / ASI04 Pattern Cat 9/10)
   - `.claude/agents/tachi/data-poisoning.md` for the durable-memory-write case (currently covered there under LLM03 / LLM04)

   **No new emission from `output-integrity`** — the subsection is navigational, not generative. The agent does NOT emit findings on tool-arg or memory-write flows; those remain owned by `tool-abuse` and `data-poisoning` respectively. The cross-link prose surfaces the boundary to readers reviewing `output-integrity` who need a navigational pointer to the adjacent agents.

4. **Gap 3 mitigation pattern — Memory-Promotion Rules**: Add a named mitigation pattern with a worked JSON-schema example. The pattern: explicit allowlist + schema validation for what an agent may persist to durable memory (`promotable_keys` enum + `value_schema` ref + `tenant_scope` pin). The worked example sits in `detection-patterns.md` as part of Gap 3 prose so readers see the navigational pointer AND the recommended mitigation in one place.

5. **Cross-link surface on agent file**: Add a 1–2-sentence pointer to the `Purpose` section of `.claude/agents/tachi/output-integrity.md` mentioning that LLM output flowing into tool-call arguments is owned by `tool-abuse`, and LLM output flowing into durable memory writes is owned by `data-poisoning` — and that `output-integrity` itself does NOT detect those handoff cases (it owns the encoding/sanitization signal class only, per ADR-030 Decision 2).

6. **Optional new example baseline**: Add `examples/multi-tenant-rag-app/` exercising the Gap 1 vector-filter pattern with a worked architecture (RAG over Pinecone with tenant_id metadata; LLM-synthesized filter omits the tenant clause). New baseline emits OI-{N} findings of the new pattern category; baseline checked in, byte-identical reproduction verified at `SOURCE_DATE_EPOCH=1700000000`. **Architect decides whether to add in `/aod.plan`** (see Open Question Q2).

7. **CHANGELOG attribution**: Explicit credit to @armorer-labs (or contributor's preferred handle, confirmed in discussion #179 reply) for the gap-surfacing. Pattern is **F-260 community-merged precedent** (PR #262, v4.31.0, 2026-05-06): comment-first-give-choice, preserve authorship, find a way to accept.

### Scope

**In Scope (this feature)**:
- Refinement to `.claude/skills/tachi-output-integrity/references/detection-patterns.md` (three gap closures + Memory-Promotion Rules mitigation example)
- Cross-link prose addition to `.claude/agents/tachi/output-integrity.md` Purpose section (~1–2 sentences, total file diff ≤10 lines)
- Optional new `examples/multi-tenant-rag-app/` baseline (Architect decision in `/aod.plan`)
- CHANGELOG entry with @armorer-labs attribution
- Discussion #179 closure with delivery comment (PR link + `detection-patterns.md` anchor + CHANGELOG section + attribution line)
- Authorship handoff offer to @armorer-labs per F-260 precedent (parallel non-blocking track)

**Out of Scope (deferred / belongs elsewhere)**:
- `finding.yaml` schema bump — NOT required (the v1.6 regex `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\d+$` already supports `OI-{N}` ids; new patterns reuse the existing prefix)
- New AI-tier threat agent — NOT required (refinement extends the F-1 agent's catalog, not a new agent file)
- Emission from `output-integrity` on tool-arg or memory-write handoff flows — those stay owned by `tool-abuse` and `data-poisoning`; cross-link prose is navigational only
- Refactoring `tool-abuse` or `data-poisoning` themselves — only `output-integrity` cross-links are added; the target agents are unchanged
- ASI09 trust-exploitation prose — F-4 trust-exploitation agent (PRD #224, delivered 2026-04-26) already owns that surface; no overlap added here

**Deferred (may be follow-on F-292b or similar)**:
- Automated coverage matrix update reflecting the three gap closures (separate Coverage Attestation refresh — F-194 PRD owns that surface)
- Additional vector-DB engines (Weaviate, Milvus, Chroma) beyond Qdrant/Pinecone in the worked example (start with two; expand on community feedback)
- MCP-tool-input handoff (one of @armorer-labs's four sub-classes under "agent-tool sinks"): partially covered by Gap 3 cross-link; full enumeration is `tool-abuse` agent's surface, not `output-integrity`'s

---

## 🎯 User Stories

**US-1 (Multi-Tenant RAG Adopter, Gap 1 anchor)**:
> **When** I'm a tachi adopter running RAG over a multi-tenant Pinecone or Qdrant store, **I want** `output-integrity` to flag when an LLM-synthesized metadata filter could bypass tenant scoping, **so that** I don't ship a vector-DB equivalent of SQLi where one tenant's query returns another tenant's documents.

**Acceptance**: Running `tachi.threat-model` against an architecture description containing an LLM Process that emits a Pinecone/Qdrant filter into a multi-tenant query interface emits at least one OI-{N} finding under the new Gap 1 pattern category (or extended Cat 2 sub-class, per Architect decision). The finding's `description` explicitly names the vector-DB engine and the tenant-scoping bypass mechanism. The `mitigation` field names at least one specific control: server-side filter composition, allowlisted clause keys, or tenant filter pinning.

**US-2 (AI-Coding-Assistant Adopter, Gap 2 anchor)**:
> **When** I'm an AI-coding-assistant adopter generating `npm install`, `pip install`, or GitHub Actions YAML steps from LLM output, **I want** `output-integrity` to flag the package-manager / CI sink as an execution sink, **so that** the same agent that catches shell injection also catches package-manager injection — without me having to maintain a second detection layer.

**Acceptance**: The Cat 2 (Server-Side Execution Sinks) and/or Cat 5 (Path Traversal + Unsafe File Writes) trigger-keyword lists include at least `npm install`, `pip install`, `apt install`, `brew install`, `gh workflow`, `actions/`, `uses:`, `package-lock`, `requirements.txt`. At least one worked example in `detection-patterns.md` exercises the package-manager sink with a named mitigation (allowlist OR sandbox OR signature gate).

**US-3 (Multi-Agent Adopter, Gap 3 anchor)**:
> **When** I'm a tachi adopter running multi-agent architectures with shared memory and tool-calling, **I want** `output-integrity` to cross-link to `tool-abuse` and `data-poisoning` when LLM output flows into a tool argument or durable memory write, **so that** I get a coherent finding chain instead of three disjoint findings to reconcile across three agents.

**Acceptance**: `detection-patterns.md` contains a "Cross-Agent Handoff Sinks" subsection that (a) states the boundary explicitly ("harmless as text, dangerous as tool argument or memory entry"), (b) cross-links to `.claude/agents/tachi/tool-abuse.md` for the tool-arg case, (c) cross-links to `.claude/agents/tachi/data-poisoning.md` for the durable-memory-write case, and (d) includes the Memory-Promotion Rules mitigation pattern with a worked JSON-schema example. `output-integrity` itself does NOT emit findings on tool-arg or memory-write flows — confirmed by re-running an existing multi-agent example and verifying zero new findings under OI-{N} from the cross-link prose alone.

**US-4 (Maintainer, Community-Feedback Conversion)**:
> **When** I'm the maintainer of tachi receiving thoughtful first-time-contributor comments on discussion threads, **I want** community feedback to convert into shipped refinements with preserved authorship attribution and a clear closure comment, **so that** external contributors see their input land in shipped code and return for more contributions.

**Acceptance**: CHANGELOG entry for the release containing this refinement explicitly attributes @armorer-labs (or the contributor's preferred handle) for the gap-surfacing. Discussion #179 receives a delivery comment within 24 hours of PR merge linking the PR, the `detection-patterns.md` anchor for each gap closure, and the CHANGELOG section. Pattern matches F-260 precedent (PR #262, @north-echo, v4.31.0).

**US-5 (First-Time Contributor, @armorer-labs)**:
> **When** I'm @armorer-labs and I've posted a thoughtful gap-analysis comment on discussion #179 as a first-time contributor, **I want** a clear path to either authoring the PR myself with maintainer steerage OR having my gap-surfacing attributed in the CHANGELOG when the maintainer authors it, **so that** my contribution is recognized either way and I have a low-friction on-ramp to deeper involvement.

**Acceptance**: Within 48 hours of this PRD being signed off, a reply on discussion #179 offers two choices: (a) @armorer-labs authors the PR with maintainer steerage (F-260 precedent — issue assignment, branch suggestion, review-ready guidance), or (b) maintainer authors the PR with explicit CHANGELOG + commit-trailer attribution to @armorer-labs (`Co-authored-by:` trailer if @armorer-labs agrees to that form). Default if no response by 2026-05-21 (7-day window): proceed with (b) and explicit attribution in CHANGELOG + commit message.

---

## ✅ Functional Requirements

**FR-1**: `detection-patterns.md` MUST include at least one explicitly-named pattern surface for vector-filter / search-DSL injection (Gap 1). The pattern surface MAY be a new Cat 6 OR an extension to Cat 2 — Architect decides in `/aod.plan` (Q1).

**FR-2**: The new pattern surface MUST include at least one worked example referencing a named vector-DB engine (Qdrant OR Pinecone OR both) and the tenant-scoping bypass mechanism, with a `mitigation` field naming at least one specific control (server-side filter composition, allowlisted clause keys, or tenant filter pinning).

**FR-3**: The new pattern surface MUST cite at least one OWASP framework reference and at least one CWE — Architect pins the exact CWE in the ADR if one is added. **Lean**: `primary: CWE-943 "Improper Neutralization of Special Elements in Data Query Logic"` (already present in F-A1 catalog `schemas/taxonomy/cwe.yaml:250`; canonical parent CWE for query-language injection that is not SQL-specific); `related: CWE-89 (taxonomic neighbor, SQL-specific)` + `CWE-94 (when the filter is templated as an expression)`. CWE-602 (Client-Side Enforcement of Server-Side Security) is NOT the right anchor — vector-filter injection is server-side execution, not client-side enforcement bypass.

**FR-4**: Cat 2 (Server-Side Execution Sinks) and/or Cat 5 (Path Traversal + Unsafe File Writes) trigger-keyword lists MUST include at minimum: `npm install`, `pip install`, `apt install`, `brew install`, `gh workflow`, `actions/`, `uses:`, `package-lock`, `requirements.txt` (Gap 2).

**FR-5**: At least one worked example MUST exercise the package-manager sink with a named mitigation (allowlist enum OR sandbox-only execution OR `npm audit signatures` / equivalent supply-chain gate).

**FR-6**: `detection-patterns.md` MUST include a "Cross-Agent Handoff Sinks" prose subsection stating the boundary explicitly ("harmless as text, dangerous as tool argument or memory entry") with cross-links to `.claude/agents/tachi/tool-abuse.md` and `.claude/agents/tachi/data-poisoning.md` (Gap 3).

**FR-7**: The "Cross-Agent Handoff Sinks" subsection MUST explicitly state that `output-integrity` does NOT emit findings on tool-arg or memory-write flows — those remain owned by `tool-abuse` and `data-poisoning` respectively. This MUST be testable by re-running an existing multi-agent example baseline and verifying zero new OI-{N} findings are emitted from the prose addition alone.

**FR-8**: `detection-patterns.md` MUST include the **Memory-Promotion Rules** mitigation pattern with a worked JSON-schema example (`promotable_keys` enum + `value_schema` reference + `tenant_scope` pin) inside the Gap 3 subsection.

**FR-9**: `.claude/agents/tachi/output-integrity.md` Purpose section MUST include 1–2 sentences pointing to `tool-abuse` (for tool-arg handoff) and `data-poisoning` (for durable-memory-write handoff). Total agent file diff MUST be ≤10 lines.

**FR-10**: NO modifications to `tool-abuse.md`, `data-poisoning.md`, or any other threat-agent file in this feature. Cross-links flow OUT of `output-integrity` only; the target agents are referenced but unchanged.

**FR-11**: NO `finding.yaml` schema bump. The v1.6 schema's `id.pattern` regex already supports `OI-{N}` ids; new patterns reuse the existing prefix.

**FR-12** (conditional, Architect decides Q2): If a new `examples/multi-tenant-rag-app/` baseline is added, it MUST exercise the Gap 1 vector-filter sink, emit at least one OI-{N} finding under the new pattern surface, and reproduce byte-identical at `SOURCE_DATE_EPOCH=1700000000` per ADR-021.

---

## 🚧 Non-Functional Requirements

**NFR-1 (Regression Protection — Existing Baselines)**: Re-running the F-1 example baselines after this refinement MUST produce byte-identical findings to the v4.21.0 shipped baselines at `SOURCE_DATE_EPOCH=1700000000`. The new patterns extend the catalog without altering existing emission behavior.

**NFR-2 (Regression Protection — Cross-Link Prose)**: The Cross-Agent Handoff Sinks subsection MUST NOT cause `output-integrity` to emit findings that should belong to `tool-abuse` or `data-poisoning`. Verified by re-running at least one existing multi-agent example baseline and confirming zero new OI-{N} findings.

**NFR-3 (Documentation Quality)**: Each gap closure (Cat 6 OR extended Cat 2 sub-class for Gap 1; Cat 2/Cat 5 keyword extension for Gap 2; Cross-Agent Handoff Sinks prose for Gap 3) MUST include the same level of detail as the shipped Cat 1–5 entries: trigger keywords (or extension list), worked example, mitigation that names at least one specific library/encoding/pattern, and primary-source citation.

**NFR-4 (Security — /security re-scan)**: A post-merge `/security` re-scan of the F-6 file surface MUST pass with zero new findings on the modified files (`.claude/skills/tachi-output-integrity/references/detection-patterns.md`, `.claude/agents/tachi/output-integrity.md`, optional `examples/multi-tenant-rag-app/`).

**NFR-5 (Authorship Attribution Preservation)**: The contribution chain — discussion #179 comment → maintainer gap-analysis → PRD → PR → CHANGELOG — MUST preserve @armorer-labs's authorship visibly. If @armorer-labs authors the PR, GitHub's native authorship suffices. If the maintainer authors, both a CHANGELOG attribution line AND a commit-trailer (`Co-authored-by: @armorer-labs <handle@github>` if agreed) MUST be present.

**NFR-6 (Constitution Compliance)**: This refinement MUST comply with **Constitution Principle X (Product-Spec Alignment & Architecture Review)** — the principle that mandates "Architect documents all architectural decisions in `docs/architecture/02_ADRs/`". The BLP-01 enrichment-branch precedent is to **author an ADR even for docs-only refinements** when the change establishes or extends a Heuristic A precedent: F-3 (`tool-abuse` enrichment) authored ADR-032; F-6 (ML Top 10 coverage bundle = `data-poisoning` + `tampering` + `model-theft` enrichment) authored ADR-035. Q3 in `/aod.plan` resolves whether F-292 follows this precedent (author ADR-045 or next-free-slot covering Gap 1 placement + Gap 2 keyword extensions + Gap 3 cross-link prose) OR whether it argues for a no-ADR exception. The BLP-01 evidence leans toward authoring an ADR.

**NFR-7 (CHANGELOG Compliance)**: CHANGELOG entry under v{next-minor} MUST follow the existing tachi CHANGELOG format (feat/fix/perf section grouping, PR link, attribution line). The release-please flow auto-bumps on `feat:` squash-merge; this PR's title MUST be `feat(292): output-integrity cross-sink refinement` to trigger a minor bump.

---

## 🎯 Success Criteria

**SC-1**: `detection-patterns.md` updated with three gap closures.
- **Verify**: `grep -E "vector|qdrant|pinecone|search.dsl" .claude/skills/tachi-output-integrity/references/detection-patterns.md` returns at least one match (Gap 1).
- **Verify**: `grep -E "npm install|pip install|gh workflow|actions/" .claude/skills/tachi-output-integrity/references/detection-patterns.md` returns at least four matches (Gap 2).
- **Verify**: `grep -E "Cross-Agent Handoff|Memory-Promotion" .claude/skills/tachi-output-integrity/references/detection-patterns.md` returns at least two matches (Gap 3).

**SC-2**: Cross-link prose in `output-integrity.md` Purpose section points to `tool-abuse` and `data-poisoning`.
- **Verify**: `grep -E "tool-abuse|data-poisoning" .claude/agents/tachi/output-integrity.md` returns at least two matches in the Purpose section.
- **Verify**: `git diff main -- .claude/agents/tachi/output-integrity.md` shows ≤10 line diff.

**SC-3**: (Conditional Q2) If new example baseline added, `examples/multi-tenant-rag-app/` emits at least one OI-{N} finding under the new pattern surface, byte-identical at `SOURCE_DATE_EPOCH=1700000000`.

**SC-4**: Existing F-1 baselines emit byte-identical findings.
- **Verify**: Run `tachi.threat-model` against each F-1 example baseline; `diff` the new output against the v4.21.0-shipped baseline. Zero diff expected.

**SC-5**: Cross-link prose does NOT trigger new emissions on existing baselines.
- **Verify**: Re-run at least one existing multi-agent example baseline (e.g., `examples/mermaid-agentic-app/`); confirm zero new OI-{N} findings emitted from the Cross-Agent Handoff Sinks subsection.

**SC-6**: CHANGELOG entry explicitly attributes @armorer-labs.
- **Verify**: `grep -E "@armorer-labs|armorer-labs|north-echo style attribution" CHANGELOG.md` finds the attribution line in the section for the next release.

**SC-7**: Discussion #179 closed with delivery comment.
- **Verify**: `gh issue list --search "is:closed #179"` confirms closure; comment body links the PR + `detection-patterns.md` anchor + CHANGELOG section + attribution line.

**SC-8**: NO `finding.yaml` schema bump.
- **Verify**: `git diff main -- schemas/finding.yaml` shows zero modifications.

**SC-9**: NO new AI-tier agent files.
- **Verify**: `git diff main --name-only -- .claude/agents/tachi/` shows only `output-integrity.md` modified (no new agent files added).

**SC-10**: Post-merge `/security` re-scan PASSES on the F-6 file surface with zero new findings.

**SC-11**: PR title is `feat(292): output-integrity cross-sink refinement` and release-please opens a release PR within 30s of squash-merge.

**SC-12**: (Conditional Q3) If ADR is added (BLP-01 enrichment-branch precedent per ADR-032 + ADR-035), it MUST be Accepted status before squash-merge. If a no-ADR exception is invoked instead, the rationale MUST be captured in the CHANGELOG entry or PR description and cross-cite Constitution Principle X §Architect Synchronization Requirements explicitly.

---

## ❓ Open Questions (Architect-Owned, Resolve in `/aod.plan`)

**Q1 (Gap 1 pattern placement)**: Vector-filter / search-DSL injection — new pattern category (Cat 6) OR extension to Cat 2 (Server-Side Execution Sinks) with a vector-DB sub-class?
- **Lean**: New Cat 6 — separate CWE pinning, dedicated worked-example surface, and clean future expansion path for additional structured-query languages (GraphQL injection, NoSQL operator injection).
- **Counter-argument for Cat 2 sub-class**: Vector-filter injection IS a server-side execution sink semantically; promoting it to a category implies a coverage parity with Cat 2 that may not hold.
- **Decision criterion**: If the Architect's CWE pinning yields a CWE distinct from CWE-89 (e.g., a vector-DB-specific CWE), Cat 6 is justified. If the CWE collapses to CWE-89, sub-class is cleaner.

**Q2 (New example baseline)**: Add `examples/multi-tenant-rag-app/` to exercise Gap 1?
- **Lean**: Add. The baseline serves as both regression protection (the new pattern emits at least one finding it should) AND adopter documentation (a worked architecture showing the gap pattern in context). Cost: +0.5 day of baseline generation + byte-identical verification.
- **Counter-argument for skipping**: The worked example in `detection-patterns.md` may suffice for documentation, and regression protection can rely on the existing `examples/mermaid-agentic-app/` re-run.
- **Decision criterion**: If the Architect anticipates Gap 1 patterns to be re-exercised across multiple future refinements, adding the baseline now pays compounding regression-protection dividends. If Gap 1 is expected to be stable post-merge, skip.

**Q3 (Public ADR for F-292 enrichment branch?)**: Author a short ADR covering Gap 1 placement + Gap 2 keyword extensions + Gap 3 cross-link prose, OR invoke a no-ADR exception?
- **BLP-01 precedent (corrected after Architect H2 review)**: ALL six BLP-01 detection features authored ADRs, including the docs-only enrichment-branch features. F-3 (`tool-abuse` enrichment, PRD #219) authored **ADR-032** at single-agent scope. F-6 BLP-01 (ML Top 10 coverage bundle = `data-poisoning` + `tampering` + `model-theft`, PRD #232) authored **ADR-035** at three-agent scope. There is no BLP-01 precedent for skipping an ADR on a Heuristic A enrichment-branch refinement.
- **Lean**: **Author a short ADR** (slot ADR-045 or next free, after Architect verifies the ADR-043 gap on plan day per project memory `project_blp03_signed_updates.md`) covering Q1 placement decision, Q4 Memory-Promotion Rules surface decision, and the prose patterns for Gap 2 + Gap 3. The ADR is durable institutional knowledge that pays compounding dividends across future Heuristic A enrichments (more vector-DB engines, more package-manager surfaces, more cross-agent handoffs).
- **Counter-argument**: For a docs-only refinement at smallest scope with no schema bump and no new agent, the ADR may be heavier ceremony than the change warrants — a CHANGELOG entry + this PRD's open-questions resolution narrative could substitute. Architect's call.
- **Decision criterion**: Default = author the ADR (matches BLP-01 lineage). Deviate only if the Architect has explicit rationale for departure (which itself would belong in an ADR or a Constitution Principle X exception note).

**Q4 (Memory-Promotion Rules surface)**: Worked JSON-schema example placement — inside `detection-patterns.md` Gap 3 subsection (default), OR as a separate skill-reference file under `.claude/skills/tachi-output-integrity/references/memory-promotion-rules.md`?
- **Lean**: Inside `detection-patterns.md` Gap 3 subsection. Keeps the navigational pointer AND the mitigation pattern co-located for the reader. The example is ≤20 lines of JSON-schema; doesn't warrant a separate file at this scope.
- **Counter-argument**: Separate file enables reuse from `tool-abuse` or `data-poisoning` skill references in future refinements without coupling them to `output-integrity`.
- **Decision criterion**: If future reuse from adjacent agents is anticipated, separate file. If single-use, co-locate.

**Q5 (Authorship handoff timing)**: Wait for @armorer-labs to confirm PR-author intent before merge, OR proceed in parallel?
- **Lean**: Parallel non-blocking. Post the discussion #179 reply with the two-choice offer within 48 hours of PRD sign-off; PRD/plan/spec/build work proceeds on the maintainer track. If @armorer-labs replies before PR ready-for-review, switch to (a) the contributor-authored path (maintainer steerage, contributor PR). If no response by 2026-05-21 (7-day window), proceed with (b) maintainer-authored + explicit CHANGELOG attribution.
- **Counter-argument**: Wait — preserves the strongest authorship form (native GitHub PR authorship) but adds 3–7 days of wall-clock delay.
- **Decision criterion**: 7-day SLA on first response; switch to maintainer-authored at SLA breach. Default = parallel non-blocking, switch on response.

---

## ⚠️ Risks & Mitigations

**R1 (Cross-link prose triggers unintended emissions)**: The Gap 3 "Cross-Agent Handoff Sinks" subsection could be misinterpreted by `output-integrity` as a new pattern category and cause unintended finding emission on tool-arg or memory-write flows that should belong to `tool-abuse` / `data-poisoning`.
- **Likelihood**: LOW (the agent's detection workflow §6 already enforces "if no components match both trigger-keyword AND downstream-sink-indicator signals, return zero findings")
- **Impact**: MEDIUM (would produce false positives on multi-agent examples, eroding signal-to-noise)
- **Mitigation**: FR-7 makes the no-emission constraint explicit and testable. SC-5 verifies the constraint on at least one existing multi-agent example baseline. NFR-2 binds the regression-protection plan.

**R2 (Vector-filter pattern overlaps with `data-poisoning` RAG-corpus framing)**: Some readers may conflate "LLM-synthesized filter bypasses tenant scoping" (Gap 1, output-handling) with "attacker poisons RAG corpus to bias retrieval" (`data-poisoning` surface).
- **Likelihood**: MEDIUM (the framings are adjacent)
- **Impact**: LOW (both findings can co-emit on the same architecture — no contradiction)
- **Mitigation**: The Gap 1 worked example explicitly distinguishes output-handling (filter SYNTHESIS goes wrong) from poisoning (corpus CONTENT goes wrong). Architect may add cross-reference prose in `/aod.plan`.

**R3 (Authorship handoff stalls)**: @armorer-labs may not respond to the two-choice offer within 7 days, or may agree to (a) but not deliver a PR in a reasonable timeframe.
- **Likelihood**: MEDIUM (first-time contributors have variable response cadences)
- **Impact**: LOW (default fallback to maintainer-authored + attribution preserves the contribution chain)
- **Mitigation**: Q5 lean specifies the 7-day SLA and the maintainer-authored fallback. PRD/plan/spec work proceeds in parallel on the maintainer track regardless.

**R4 (Schema-bump scope creep)**: A reviewer or implementer may argue that the new Gap 1 pattern category warrants its own id prefix (e.g., `OQ-{N}` for "output query injection") rather than reusing `OI-{N}`.
- **Likelihood**: LOW (FR-11 + SC-8 explicitly forbid schema bump; ADR-030 Decision 8 establishes `OI-{N}` as the F-1 prefix)
- **Impact**: HIGH if accepted (schema bump cascades to populator, taxonomy crosswalk, source-attribution F-A2 contract)
- **Mitigation**: FR-11 is a hard requirement; SC-8 is a binary check. Architect override would require an explicit ADR with cross-cuts to ADR-030, ADR-028 (source-attribution), and ADR-027 (taxonomy crosswalk).

**R5 (Discussion #179 closure timing slips)**: The delivery comment on discussion #179 may slip past the 24-hour SLA after PR merge if the merge happens late in the day or over a weekend.
- **Likelihood**: LOW
- **Impact**: LOW (the SLA is a quality-of-experience metric, not a delivery gate)
- **Mitigation**: Include the discussion #179 closure step in the `/aod.deliver` Step 8 (post-merge documentation flow). Treat it as a release-day item, not a release gate.

---

## 📅 Estimated Timeline

**Schedule policy (Team-Lead H1 resolution)**: Weekday-anchored cadence. The original draft placed Days 2–3 on Sat 2026-05-16 + Sun 2026-05-17 without acknowledging weekend cadence — Team-Lead review correctly flagged this as a capacity-assumption error. Shifted to Mon–Tue weekdays per Team-Lead recommended path (B). Working-day effort estimate is unchanged (~1.5 focused working days); wall-clock extends from 3 to 6 calendar days.

| Day | Date | Activity | Owner |
|---|---|---|---|
| Day 0 | 2026-05-14 (Thu) | `/aod.define` — this PRD | product-manager |
| Day 1 AM | 2026-05-15 (Fri) | `/aod.plan` — spec.md + plan.md + tasks.md with Architect Q1–Q5 decisions | product-manager + architect + team-lead |
| Day 1 PM | 2026-05-15 (Fri) | `/aod.build` Wave 1 — `detection-patterns.md` Gap 1 catalog + Gap 2 keyword extensions (parallelizable sub-tasks per Team-Lead M-2) | senior-backend-engineer (docs) |
| — | 2026-05-16 (Sat) — 2026-05-17 (Sun) | Weekend (maintainer break) | — |
| Day 2 AM | 2026-05-18 (Mon) | `/aod.build` Wave 2a — `detection-patterns.md` Gap 3 prose + Memory-Promotion Rules JSON-schema + agent file cross-link (≤10 line diff) | senior-backend-engineer (docs) |
| Day 2 AM (parallel) | 2026-05-18 (Mon) | `/aod.build` Wave 2b — Existing-baseline byte-identical regression re-run (SC-4) on Wave 1 commits | tester |
| Day 2 PM | 2026-05-18 (Mon) | (Conditional Q2) Generate `examples/multi-tenant-rag-app/` baseline + byte-identical verification + `examples/README.md` wiring (Architect M4) | senior-backend-engineer + tester |
| Day 3 AM | 2026-05-19 (Tue) | `/aod.build` Wave 3 — Cross-link no-emission verification on `mermaid-agentic-app` + `agentic-app` baselines (SC-5, full byte-identity per Architect M2) | tester |
| Day 3 PM | 2026-05-19 (Tue) | `/security` re-scan + `/aod.deliver` close-out (PR ready-for-review → squash-merge → release-please verify → discussion #179 closure) | devops + product-manager |
| **Buffer-1** | 2026-05-20 (Wed) | Slip buffer for Q3 ADR drafting (if added per BLP-01 precedent) | architect |
| **Buffer-2** | 2026-05-21 (Thu) | Slip buffer for `@armorer-labs` PR-author handoff (if Q5 path (a) accepted) OR worst-case execution slip (Q1=Cat 6 + Q2=Add + Q3=Add-ADR per Team-Lead M-1) | — |

**Total wall-clock**: 6 calendar days (1.5 working days of focused effort) under the maintainer-authored path. **Add 3–7 days** if @armorer-labs accepts the (a) PR-authorship path — second buffer day plus handoff support extends to ~10–13 calendar days total.

**Critical path**:
1. Day 1 AM `/aod.plan` resolves Q1 (placement) + Q2 (baseline yes/no) + Q3 (ADR yes/no) → unlocks Wave 1 build.
2. Day 1 PM Wave 1 (Gap 1 + Gap 2) — parallelizable sub-tasks T1a (Gap 1 catalog) ∥ T1b (Gap 2 keyword extension) per Team-Lead M-2.
3. Day 2 AM Wave 2a (Gap 3 + cross-link) ∥ Wave 2b (SC-4 regression) — parallel tracks.
4. Day 2 PM (conditional Q2 baseline) blocks `/aod.deliver` close-out only if Q2=Add.
5. Day 3 AM SC-5 cross-link no-emission verification is the last quality gate before merge.
6. Day 3 PM `/aod.deliver` close-out with release-please verification (per project memory `feedback_aod_deliver_release_gate.md`).

**Worst-case path** (Team-Lead M-1): If Q1=Cat 6 + Q2=Add + Q3=Add-ADR (worst-case 9.5 hours of focused work), shift `/aod.deliver` to Buffer-1 (Wed 2026-05-20). PRD's two-buffer-day allocation accommodates this without slipping into a third calendar week.

---

## 🔗 Dependencies

**Hard dependencies (must be merged before this PRD's branch opens)**:
- F-1 `output-integrity` agent (PRD #201, PR #202, v4.21.0, merged 2026-04-19) — **MERGED ✓**
- `finding.yaml` v1.6 with `OI-{N}` id-prefix regex extension — **SHIPPED ✓** (PR #202)
- ADR-030 (output-integrity agent) — **ACCEPTED ✓**

**Soft dependencies (informational; may inform Q1–Q3 decisions in `/aod.plan`)**:
- F-260 asset-sensitivity tags (community-merged precedent, @north-echo, PR #262, v4.31.0, 2026-05-06) — establishes the comment-first-give-choice + preserve-authorship pattern; F-292 follows the same playbook.
- **F-3 BLP-01 (`tool-abuse` enrichment, PRD #219 / ADR-032)** — establishes the Heuristic A enrichment-branch precedent at **single-agent scope, no schema bump, with an authored ADR**. Direct architectural lineage for F-292.
- **F-6 BLP-01 (ML Top 10 coverage bundle: `data-poisoning` + `tampering` + `model-theft` enrichment, PRD #232 / ADR-035)** — establishes the multi-host Heuristic A enrichment precedent (three agents touched simultaneously) with an authored ADR. Informational reference for the cross-link-to-`data-poisoning` aspect of Gap 3.

**No dependencies on BLP-02 F-1 through F-5** (different surface — F-292 is a coverage refinement to F-1, not enterprise hardening).

**No dependencies on BLP-03 F-1 through F-2** (different surface — F-292 is docs-only refinement, not signed-update plumbing).

---

## 📚 References

- **Discussion #179 comment**: https://github.com/davidmatousek/tachi/discussions/179#discussioncomment-16897078 (@armorer-labs, 2026-05-12)
- **PRD #201** — F-1 `output-integrity` threat agent: `docs/product/02_PRD/201-output-integrity-threat-agent-2026-04-18.md`
- **ADR-030** — `output-integrity` agent: `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md`
- **ADR-021** — `SOURCE_DATE_EPOCH` for deterministic PDF comparison: `docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md`
- **F-1 detection-patterns**: `.claude/skills/tachi-output-integrity/references/detection-patterns.md` (151 lines, 5 categories)
- **F-1 agent file**: `.claude/agents/tachi/output-integrity.md` (120 lines, Purpose anchors the encoding/sanitization scope per ADR-030 Decision 2)
- **Constitution Principle X** — Product-Spec Alignment & Architecture Review (mandates ADR documentation for all architectural decisions): `.aod/memory/constitution.md` §X
- **ADR-032** — `tool-abuse` enrichment (F-3 BLP-01, PRD #219): `docs/architecture/02_ADRs/ADR-032-asi07-tool-abuse-enrichment.md` (single-agent enrichment-branch precedent)
- **ADR-035** — ML Top 10 coverage bundle (F-6 BLP-01, PRD #232): `docs/architecture/02_ADRs/ADR-035-ml-top-10-coverage-bundle.md` (multi-host enrichment-branch precedent)
- **F-A1 CWE catalog** — `schemas/taxonomy/cwe.yaml` line 250: CWE-943 "Improper Neutralization of Special Elements in Data Query Logic" (primary anchor for Gap 1 per FR-3)
- **F-260 community-merged precedent** — PR #262, @north-echo, v4.31.0: see project memory `project_f260_asset_tags.md`
- **`tool-abuse` agent** (Gap 3 cross-link target): `.claude/agents/tachi/tool-abuse.md`
- **`data-poisoning` agent** (Gap 3 cross-link target): `.claude/agents/tachi/data-poisoning.md`

---

## 📋 Triad Review Disposition

Three HIGH-level findings were resolved inline at the PRD layer before sign-off:

| Finding | Source | Resolution |
|---|---|---|
| H1 (Architect) | Constitution Principle VII miscited as "Architecture Decisions Are Public ADRs" | Re-anchored NFR-6 + Q3 + SC-12 + References section to **Principle X (Product-Spec Alignment & Architecture Review)** — the principle that actually mandates ADRs |
| H2 (Architect) | F-3 mis-identified as `data-poisoning` | Corrected to **F-3 = `tool-abuse` enrichment (PRD #219 / ADR-032)** at single-agent scope. Added F-6 = ML Top 10 bundle (PRD #232 / ADR-035) at multi-host scope. Q3 lean flipped from "invoke §Exceptions" to "author ADR per BLP-01 lineage" |
| H1 (Team-Lead) | Days 2–3 placed on Sat 2026-05-16 + Sun 2026-05-17 without weekend-cadence acknowledgment | Timeline shifted to weekday-anchored (Day 2 = Mon 2026-05-18, Day 3 = Tue 2026-05-19, Buffer-1 = Wed 2026-05-20, Buffer-2 = Thu 2026-05-21) per Team-Lead recommended path (B) |
| M1 (Architect) | FR-3 CWE pinning leaned to CWE-89 (SQL-specific) | Flipped to **CWE-943 "Improper Neutralization of Special Elements in Data Query Logic"** as primary (already in F-A1 catalog at `schemas/taxonomy/cwe.yaml:250`); CWE-89 demoted to taxonomic neighbor; CWE-94 added when filter is templated |

Remaining findings flow into `/aod.plan` for resolution during spec.md / plan.md / tasks.md generation:
- **Architect M2** — Strengthen NFR-2 / SC-5 to full byte-identical regression diff (not just OI emission count) per ADR-021 discipline.
- **Architect M3** — Add prose-strengthener to FR-7 locking the one-way navigational-pointer invariant (no scope extension to tool-call-argument sinks).
- **Architect M4** — If Q2=Add baseline, add FR-13 binding `examples/README.md` wiring + SC-3 expected-findings inventory.
- **Architect L1** — Verify ADR slot 043 gap on plan day; allocate ADR-045 if 043 is reserved for BLP-03 cosign decision.
- **Architect L2** — Strengthen Gap 2 keyword-list prose to reiterate both-signal requirement (keyword + sink-indicator).
- **Architect L3** — Add follow-up notification to discussion #179 at Q5 SLA breach so first-time contributor isn't ghosted.
- **Team-Lead M-1** — Add worst-case contingency clause to tasks.md (Q1=Cat 6 + Q2=Add + Q3=Add-ADR shifts `/aod.deliver` to Buffer-1).
- **Team-Lead M-2** — tasks.md parallelizes T1a (Gap 1) ∥ T1b (Gap 2) on Wave 1; T2a (Gap 3 + cross-link) ∥ T2b (SC-4) on Wave 2.
- **Team-Lead M-3** — Capacity gate: confirm maintainer 5-hour attention budget for Q5 path (a); default explicitly to (b) if not available.
- **Team-Lead L-1/L-2/L-3** — Positive confirmations / minor refinements; no action required.

**Full review artifacts**:
- Architect: `.aod/results/architect.md` (2H/4M/3L, APPROVED_WITH_CONCERNS)
- Team-Lead: `.aod/results/team-lead.md` (1H/3M/3L, APPROVED_WITH_CONCERNS)

---

## 🤝 Provenance / Attribution Note

This refinement is **community-surfaced**. Authorship preservation is a first-class requirement (NFR-5) and follows the F-260 precedent established by PR #262 (@north-echo, v4.31.0, 2026-05-06).

**Decision tree** (Q5 resolution in `/aod.plan`):
- **Default**: Comment on discussion #179 within 48 hours of PRD sign-off offering two choices:
  - **(a)** @armorer-labs authors the PR with maintainer steerage (F-260 precedent — issue-assignment + branch suggestion + review-ready guidance)
  - **(b)** Maintainer authors the PR with explicit CHANGELOG attribution + commit-trailer `Co-authored-by:` if @armorer-labs agrees
- **SLA**: 7-day window for first response. Default fallback to (b) at SLA breach.
- **Either way**: CHANGELOG attribution + delivery comment on discussion #179 are required (NFR-5).

**The contribution chain**:
1. @armorer-labs comment on discussion #179 (2026-05-12) — gap-surfacing
2. Maintainer gap-analysis (2026-05-14) — crosswalk against shipped F-1 catalog
3. This PRD (#292) — formal refinement scoping
4. `/aod.plan` resolves Q1–Q5 — architectural decisions
5. `/aod.build` — implementation
6. `/aod.deliver` — PR merge + CHANGELOG + discussion #179 closure + release
7. Future readers tracing F-1 → F-6 evolution see @armorer-labs's name in the CHANGELOG and the contribution chain.
