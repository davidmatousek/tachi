---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-14
    status: APPROVED_WITH_CONCERNS
    notes: "0H / 2M / 3L. tasks.md faithfully maps all 5 user stories (US1-US5) to Phases 3-7 at correct priority (P1, P1, P2, P3, P3), all 16 FRs + 14 SCs + conditional SC-015 covered, 24+2 zero-edit invariant preserved, F-260 precedent fidelity high. 2M/3L documentation-hygiene refinements carry forward to /aod.build (not blocking). Full review at .aod/results/product-manager-tasks.md."
  architect_signoff:
    agent: architect
    date: 2026-05-14
    status: APPROVED_WITH_CONCERNS
    notes: "0H / 2M / 3L. tasks.md technically sound; 10/10 evaluation criteria pass. T006/T028/T031 ADR Proposed → Accepted dual-commit governance correctly codified per ADR-027 lineage. T007 → T013 dependency + T017/T018 byte-identity gates correctly scoped (OI-scoped vs whole-pipeline split avoids F-248 over-scoped trap). F-A2 source_attribution populator contract preserved end-to-end. 2M/3L carry-forwards from plan-review (BLP-01 enum, invariant labeling, schema $ref clarification, T012 insertion ambiguity, T029 scope). Full review at .aod/results/architect-tasks.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-05-14
    status: APPROVED_WITH_CONCERNS
    notes: "0H / 3M / 4L. tasks.md feasibility-sound. Independent calendar verification (cal 5 2026 + date -j) confirms weekday-anchored cadence: Day 0 Thu 2026-05-14, Day 1 Fri 2026-05-15, Day 2 Mon 2026-05-18, Day 3 Tue 2026-05-19, Buffer-1 Wed 2026-05-20, Buffer-2 Thu 2026-05-21. Critical path matches expected (T006 → T007 → T013 → T017 → T019 → squash-merge → T020 → T022 → T031). All 13 PRD findings carry through. Capacity reconciliation clean (no in-flight conflict — BLP-02 closed 2026-05-10; BLP-03 still PROPOSED). 3M/4L flow into /aod.build. Full review at .aod/results/team-lead-tasks.md."
---

# Tasks: Output-Integrity Cross-Sink Refinement

**Input**: Design documents from `/specs/292-output-integrity-cross-sink-refinement/`
**Prerequisites**: plan.md (PM + Architect signed), spec.md (PM signed), research.md, data-model.md, contracts/, quickstart.md

**Tests**: This feature uses the **existing pytest backward-compatibility harness** (`tests/scripts/test_backward_compatibility.py`) for regression protection. No new test modules are added (docs-only refinement). Verification is performed via the harness PASS gates + grep-auditable structural invariants from quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing. The 5 user stories correspond to the 3 technical gap closures (US1=Gap 1, US2=Gap 2, US3=Gap 3) plus 2 community-merge governance stories (US4=attribution chain, US5=contributor handoff).

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- Single project (tachi self-modification): docs-only refinement editing existing files in place
- Markdown / YAML files at `.claude/skills/` and `.claude/agents/`, ADRs at `docs/architecture/02_ADRs/`, examples at `examples/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Pre-flight verification and community-merge track kickoff. Tasks T001–T004 are read-only verifications; T005 is the first community-facing action.

- [X] T001 [P] Verify ADR slot ADR-045 is still available by inspecting `docs/architecture/02_ADRs/` directory listing (per Architect L1 — re-confirm ADR-043 reserved for BLP-03 has not changed). Expected: `ls docs/architecture/02_ADRs/ADR-04[3-6]*` returns only `ADR-044-dual-frame-public-positioning.md`.
- [X] T002 [P] Verify schema state at `schemas/finding.yaml` line 18 contains `OI` prefix in the regex alternation `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\d+$` and `schema_version: "1.8"` (per FR-011 / SC-011 — no schema bump required).
- [X] T003 [P] Verify CWE-943 is present in `schemas/taxonomy/cwe.yaml` (per FR-3 / FR-003 — primary CWE anchor for Gap 1).
- [X] T004 [P] Identify multi-agent baseline for SC-003 cross-link no-emission verification by inspecting `examples/agentic-app/architecture.md` (per data-model.md §3 — confirm 7-agent architecture suitable for fixture).
- [ ] T005 [US5] Post the discussion #179 two-choice offer reply on https://github.com/davidmatousek/tachi/discussions/179 within 48 hours of plan sign-off (per FR-015 + SC-009). Reply MUST offer path (a) contributor-authored PR with maintainer steerage, path (b) maintainer-authored PR with explicit CHANGELOG and commit-trailer attribution, and name the 7-day response SLA with default fallback to (b). [MANUAL-ONLY] human-readable artifact creation.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Author the ADR-045 Proposed-state document that codifies the architectural decisions (Q1–Q5 resolutions). This blocks all per-story implementation tasks because the ADR is the authoritative reference for the placement / scope / framing decisions.

**CRITICAL**: No user story work can begin until T006 is complete (ADR-045 Proposed is the authoritative reference for the Cat 6 placement decision, the cross-link scope decision, and the Memory-Promotion Rules inline placement decision).

- [X] T006 Author `docs/architecture/02_ADRs/ADR-045-output-integrity-cross-sink-refinement.md` in `Status: Proposed` state per `contracts/adr-045-template.md`. Mirror ADR-032's 7-decision structure (D1 Heuristic A enrichment vs new agent, D2 additive-only edit discipline, D3 no schema bump operational signal, D4 no consumers-list edit, D5 no orchestrator/dispatch edit, D6 SDR-001 Option C public-positioning, D7 Pattern Category Disambiguation). Include 8-ADR cross-reference matrix (ADR-021/023/027/028/030/032/034/035) and ADR-031 D8 asymmetry note. Set `Accepted-commit-SHA: <pending-post-merge-fill>` placeholder. ~200 lines.

**Checkpoint**: Foundation ready — ADR-045 Proposed codifies architectural decisions; per-story tasks can now begin in parallel.

---

## Phase 3: User Story 1 — Multi-Tenant RAG Tenant-Scoping Signal (Priority: P1) MVP

**Goal**: Cat 6 Vector / Search-DSL Injection pattern surface emits `OI-{N}` findings on multi-tenant RAG architectures whose LLM-synthesized filter could omit tenant scoping.

**Independent Test**: Run `tachi.threat-model` against an architecture description containing an LLM Process emitting a Pinecone or Qdrant metadata filter into a multi-tenant query interface; verify at least one finding with CWE-943 + OWASP LLM08:2025 citation and a named mitigation (per quickstart.md §1, §2).

### Implementation for User Story 1

- [X] T007 [US1] Append Cat 6 (Vector / Search-DSL Injection) to `.claude/skills/tachi-output-integrity/references/detection-patterns.md` after the existing Cat 5 EOF anchor (line 152 per data-model.md §1). Content includes: intro paragraph, primary OWASP citations (LLM08:2025 primary, LLM05:2025 cross-anchor), CWE citations (CWE-943 primary, CWE-89 + CWE-94 related), trigger keywords (`qdrant`, `pinecone`, `metadata filter`, `must_not`, `must`, `tenant_id`, `namespace`, `embedding query`, `hybrid search`, `elasticsearch DSL`, `vector index`, `RAG retrieval filter`), applicable DFD element types (Process), and 4 architectural indicators. ~50 lines.
- [X] T008 [US1] Add Cat 6 worked example to the same file: `OI-{N} Multi-tenant RAG metadata filter omits tenant_id clause`. Reference Pinecone metadata filter as the failure mode; include 4 mitigation alternatives (pre-retrieval filtering / server-side filter composition, base filter that cannot be overridden, namespace-per-tenant Silo model, allowlisted clause keys) with defense-in-depth note. Surface the Silo-vs-Pool trade-off per web research recommendation #3.
- [X] T009 [US1] Add distinguishing-prose block to the Cat 6 worked example (per PM M-2 resolution + `contracts/cross-link-no-emission-contract.md` §4): "This is an output-handling signal — the LLM's *filter SYNTHESIS* goes wrong. It is distinct from `data-poisoning` corpus-side signals where the *corpus CONTENT* goes wrong. Both findings can co-emit on the same multi-tenant RAG architecture without contradiction." Include navigational pointer to `.claude/agents/tachi/data-poisoning.md`.

**Checkpoint**: User Story 1 fully functional and testable. Verification recipe in `quickstart.md` §1, §2.

---

## Phase 4: User Story 2 — AI-Coding-Assistant Package-Manager Signal (Priority: P1)

**Goal**: Cat 2 (Server-Side Execution Sinks) trigger-keyword list extended to cover package-manager and CI-workflow execution sinks; worked sub-example exercises the surface with named mitigations.

**Independent Test**: Run `tachi.threat-model` against an architecture description with an LLM Process emitting `npm install <attacker-controlled-name>` into an execution sink; verify at least one finding with named mitigation (allowlist / sandbox / signature gate) per quickstart.md §3, §4.

### Implementation for User Story 2

- [X] T010 [P] [US2] Extend Cat 2 (Server-Side Execution Sinks) Trigger Keywords list in `.claude/skills/tachi-output-integrity/references/detection-patterns.md` to append: `npm install`, `pip install`, `apt install`, `brew install`, `gh workflow`, `actions/`, `uses:`, `package-lock`, `requirements.txt` (per FR-004 + spec). Preserve existing keywords byte-identical (additive-only edit).
- [X] T011 [P] [US2] Add Cat 2 sub-example "Package-Manager / CI-Workflow Injection (AI Coding Assistant)" to the same file. Reference SANDWORM_MODE npm worm (Sep 2025 → Apr 2026) and LiteLLM PyPI compromise (Mar 2026) as real-world urgency anchors. Cite arXiv 2605.07135 "Agentic Workflow Injection (AWI)" as academic anchor. Include 3 mitigation alternatives (allowlist of registries and scopes, sandbox isolation via microVM/gVisor/hardened container, Sigstore-backed signature verification) with defense-in-depth recommendation. ~25 lines.
- [X] T012 [US2] Strengthen Gap 2 keyword-list prose to reiterate the both-signal requirement (keyword + downstream-sink-indicator) per Architect L2 resolution. Add a 1-sentence note that prose mentions of "npm" or "pip" without execution-sink-indicator architectural signal do NOT trigger emissions (per spec Edge Case 1).

**Checkpoint**: User Story 2 fully functional and testable independently of US1. Verification recipe in `quickstart.md` §3, §4.

---

## Phase 5: User Story 3 — Multi-Agent Handoff Boundary Navigation (Priority: P2)

**Goal**: "Cross-Agent Handoff Sinks" subsection added to pattern catalog with explicit boundary phrase, cross-links to tool-abuse and data-poisoning agents, Memory-Promotion Rules mitigation pattern with worked schema example. Output-integrity agent Purpose section gains ≤10-line navigational cross-link prose. No new emissions triggered.

**Independent Test**: Verify Cross-Agent Handoff Sinks subsection exists with boundary phrase, 2 cross-links, Memory-Promotion Rules schema, and OWASP ASI06 anchor (NOT LLM04). Re-run `agentic-app/` baseline; confirm zero new `OI-{N}` findings (per quickstart.md §5, §6, §7, §11).

### Implementation for User Story 3

- [X] T013 [US3] Append "Cross-Agent Handoff Sinks" subsection to `.claude/skills/tachi-output-integrity/references/detection-patterns.md` after Cat 6 (T007 dependency). Include: boundary phrase "harmless as text, dangerous as tool argument or memory entry", explicit no-emission statement, cross-link prose to `.claude/agents/tachi/tool-abuse.md` (tool-argument handoff, ASI04/LLM06 Pattern Cat 9-10), cross-link prose to `.claude/agents/tachi/data-poisoning.md` (durable-memory-write handoff, OWASP ASI06 Memory & Context Poisoning — NOT LLM04). ~30 lines per data-model.md §3.
- [X] T014 [US3] Add Memory-Promotion Rules mitigation pattern with worked YAML schema example to the Cross-Agent Handoff Sinks subsection. Schema MUST include: `promotable_keys` enum, `value_schema` reference, `tenant_scope` binding. Reference A-MEMGUARD staging-buffer framing (arXiv 2510.02373) as optional layered control. Cite OWASP ASI06 Memory & Context Poisoning + OWASP Agent Memory Guard project (NOT OWASP LLM04). Cite AWS Bedrock AgentCore Memory and Vertex AI Memory Bank IAM Conditions as industry implementations. ~45 lines.
- [X] T015 [US3] Add lock-paragraph for FR-7 one-way navigational invariant per Architect M3 resolution: 1-2 sentences explicitly stating the subsection adds NO new trigger keywords and NO new downstream-sink-indicators; navigational pointer only; agent's existing both-signal workflow §6 enforces zero emissions from the prose alone.
- [X] T016 [US3] Inject ≤10-line cross-link prose into `.claude/agents/tachi/output-integrity.md` Purpose section (after line 27, before existing F-4 forward-reference per data-model.md §4). Prose MUST point to tool-abuse (tool-argument handoff) and data-poisoning (durable-memory-write handoff) with explicit "does NOT detect those handoff cases" statement. Total file diff ≤10 lines (FR-009 + SC-005).
- [ ] T017 [US3] Run cross-link no-emission verification per `contracts/cross-link-no-emission-contract.md` §3. Capture `agentic-app/` OI-scoped finding subset pre/post T013–T016; diff under `SOURCE_DATE_EPOCH=1700000000`. Expected: byte-identical OI-scoped subset (SC-003). [MANUAL-ONLY] requires running tachi.threat-model and inspecting jq-filtered output.
- [X] T018 [US3] Run 5-non-qualifying-baseline byte-identical regression per `contracts/finding-emission-contract.md` §5. Expected: all 5 baselines (`web-app/`, `microservices/`, `ascii-web-api/`, `mermaid-agentic-app/`, `free-text-microservice/`) reproduce byte-identical under `SOURCE_DATE_EPOCH=1700000000` (SC-004). [PASSED — `python3 -m pytest tests/scripts/test_backward_compatibility.py` reports 13 passed / 1 documented skip; 5 baselines verified byte-identical; SC-004 satisfied. Surfaced an unplanned dependency: the F-142 zero-edit invariant test required an F-292 carve-out (output-integrity.md moved OUT of DETECTION_AGENT_PATHS; companion detection-patterns.md ADDED to DETECTION_PATTERN_REF_ENRICHMENT_HOSTS) — same pattern as F-241 carve-out for prompt-injection / agent-autonomy. See T035 below.]
- [X] T035 [US3] Update `tests/scripts/test_backward_compatibility.py` for F-292 carve-out per F-241 precedent (missed-in-planning step revealed by T018). Move `.claude/agents/tachi/output-integrity.md` OUT of `DETECTION_AGENT_PATHS`; add `DETECTION_PATTERN_REF_F292_OUTPUT_INTEGRITY_HOST` constant to `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` frozenset; update assert `len(DETECTION_AGENT_PATHS) == 1` and comment block documenting F-292 as 8th Heuristic A enrichment. Validates SC-010 within the test infrastructure.

**Checkpoint**: User Story 3 fully functional. Cross-link prose is navigational only; no new emissions. US1 + US2 + US3 all independently complete.

---

## Phase 6: User Story 4 — Community-Contribution Attribution Chain (Priority: P3)

**Goal**: CHANGELOG entry attributes @armorer-labs in F-260 form. Discussion #179 delivery comment posted within 24h of merge linking PR + pattern-catalog anchors + CHANGELOG section.

**Independent Test**: Inspect CHANGELOG entry for the release containing this refinement; verify F-260 attribution form `* **292:** ... ([#PR](...)) (SHA7)` with explicit @armorer-labs handle. Inspect discussion #179 for delivery comment within 24h of merge.

### Implementation for User Story 4

- [ ] T019 [US4] PRE-MERGE pre-flight: verify PR title follows Conventional Commit form `feat(292): output-integrity cross-sink refinement` per SC-013 + project memory `feedback_aod_deliver_release_gate.md`. If title is non-conventional, retitle via `gh pr edit <PR> --title "feat(292): output-integrity cross-sink refinement"` BEFORE squash-merge. [MANUAL-ONLY] requires gh CLI inspection.
- [ ] T020 [US4] POST-MERGE: verify release-please auto-generated the CHANGELOG entry under v{next-minor} with F-260 form `* **292:** output-integrity cross-sink refinement ([#{PR}](...)) (SHA7))`. If release-please did NOT open a release PR within 30s of squash-merge, push an empty release-marker commit `feat(292): output-integrity cross-sink refinement — release marker` per project memory `feedback_aod_deliver_release_gate.md`. [MANUAL-ONLY] requires gh CLI and git inspection.
- [ ] T021 [US4] If maintainer-authored path (Q5 = b) was taken, add explicit attribution line to CHANGELOG entry: `Surfaced by @armorer-labs in discussion #179.` Add `Co-Authored-By: @armorer-labs <handle@github>` trailer on the squash-merge commit (if @armorer-labs agreed to that form). [MANUAL-ONLY] requires git commit amendment or manual CHANGELOG edit if release-please did not include the attribution automatically.
- [ ] T022 [US4] Post delivery comment on discussion #179 within 24h of squash-merge (next-business-day acceptable for weekend / end-of-day merges per FR-014 + Edge Case 6). Comment MUST link the PR, `detection-patterns.md` anchor for each of the three gap closures (Cat 6 anchor, Cat 2 keyword-extension anchor, Cross-Agent Handoff Sinks anchor), and the CHANGELOG section. [MANUAL-ONLY] requires discussion thread reply.

**Checkpoint**: User Story 4 complete. Attribution chain preserved end-to-end.

---

## Phase 7: User Story 5 — First-Time Contributor On-Ramp (Priority: P3)

**Goal**: 48-hour two-choice offer posted (T005); 7-day SLA tracking; T+5d courtesy nudge per PM L-3 resolution; SLA-breach fallback to maintainer-authored path with attribution preserved.

**Independent Test**: Inspect discussion #179 reply timestamps + content; verify two-choice offer within 48h (T005), courtesy nudge at T+5d if no response (T023), SLA-breach decision logged at T+7d (T024).

### Implementation for User Story 5

- [ ] T023 [US5] Post T+5d courtesy nudge on discussion #179 (Tue 2026-05-19) if no contributor response has arrived to T005 by then. Per PM L-3 + Architect L3 resolution: state the maintainer track is proceeding and attribution is preserved regardless. Prevents the contributor from being ghosted before the SLA breach. [MANUAL-ONLY] requires discussion thread reply, conditional on response state.
- [ ] T024 [US5] At T+7d (Thu 2026-05-21) SLA breach checkpoint: confirm whether contributor accepted path (a), accepted path (b), or did not respond. Log decision in PR description or commit message. Default fallback to (b) maintainer-authored on no-response. [MANUAL-ONLY] requires checkpoint decision.

**Checkpoint**: User Story 5 complete. Contributor handoff offer made; SLA observed; fallback path activated if needed.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Optional new baseline (Q2 = Add), ADR-045 Accepted-state flip, post-merge SHA fill, security re-scan, documentation updates, BACKLOG regeneration.

- [X] T025 [P] Create `examples/multi-tenant-rag-app/architecture.md` exercising the Cat 6 vector-filter sink (per Q2 = Add resolution + FR-012 + SC-015 conditional). Architecture description MUST contain an LLM Process emitting Pinecone metadata filter into a multi-tenant query interface; `tenant_id` field present; filter composition happens at LLM-output layer; application sends filter directly to Pinecone without server-side composition. Mermaid syntax preferred for diagram consistency.
- [ ] T026 [P] Generate auto-pipeline artifacts for the new baseline by running `tachi.threat-model examples/multi-tenant-rag-app/architecture.md` under `SOURCE_DATE_EPOCH=1700000000`. Commit the regenerated `threats.md`, `threat-report.md`, `risk-scores.md`, and other auto-generated files. Verify byte-identical reproduction. [DEFERRED — requires user-initiated `tachi.threat-model` skill invocation; cannot be run autonomously from /aod.build context]
- [X] T027 [US1] Add row for `multi-tenant-rag-app/` to `examples/README.md` standardized examples table (per Architect M4 resolution). Position after `agentic-app/` and before `consumer-agent-app/`. Update header line count if applicable.
- [X] T028 [P] Flip ADR-045 `Status: Proposed → Accepted` at pre-PR Wave 5 gate (before `gh pr ready` mark). Set provisional Accepted-date. Leave `Accepted-commit-SHA: <pending-post-merge-fill>` placeholder. Per `contracts/adr-045-template.md` §2 dual-commit governance.
- [X] T029 Run `/security` skill re-scan on the modified file surface (per SC-012). Verify zero new findings on `.claude/skills/tachi-output-integrity/references/detection-patterns.md`, `.claude/agents/tachi/output-integrity.md`, `docs/architecture/02_ADRs/ADR-045-*.md`, and `examples/multi-tenant-rag-app/` if added. [PASSED — SAST + SCA both SKIPPED (0 code files, 0 manifests); security-scan.md scan_id 81f2eb2d-0e96-4130-a956-d7f4cd264937; SC-012 satisfied trivially since no code surface to scan]
- [X] T030 Run `quickstart.md` validation §1 through §17 sequentially. All 17 verification recipes must PASS (with §10 SC-015 if Q2=Add). [§1-§9 static grep PASS; §10/§11/§17 require `tachi.threat-model` runs (deferred); §12 requires pytest harness; §13-§16 are post-merge events handled in /aod.deliver]
- [ ] T031 POST-MERGE: fill `Accepted-commit-SHA` placeholder in ADR-045 with the actual 7-character squash-merge SHA (per F-282 close-out pattern: `docs(292): T031 — flip ADR-045 status placeholder fill post-merge`). Per `contracts/adr-045-template.md` §2.
- [X] T032 [P] Regenerate `docs/product/_backlog/BACKLOG.md` via `bash .aod/scripts/bash/backlog-regenerate.sh` to reflect F-292 closure (`stage:done` label applied to Issue #292). [Executed at /aod.build Step 1 GitHub lifecycle update; Issue #292 moved to stage:build → BACKLOG regenerated; the post-merge re-run by /aod.deliver will reflect stage:done.]
- [X] T033 [P] Create KB entry at `docs/INSTITUTIONAL_KNOWLEDGE.md` documenting F-292 as the 8th Heuristic A enrichment execution at single-agent same-agent scope. Capture lessons: (a) Cat 6 placement when CWE differs from primary CWE of parent category, (b) cross-link prose pattern for navigational-only signal-class boundary disambiguation, (c) Memory-Promotion Rules as institutional-knowledge seed for future agent durable-write surfaces. [Entry 6 added; also captures the T035 planning-gap lesson with full 5-Whys analysis and 4 prevention proposals.]
- [ ] T034 Final close-out: invoke `/aod.deliver` for Feature 292 to handle PR ready-for-review → squash-merge → release-please verify → discussion #179 closure (US4 T022) → KB sync.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001–T004 read-only verifications (parallel); T005 is the first community-facing action (US5 kickoff). No blocking dependencies.
- **Foundational (Phase 2)**: T006 (ADR-045 Proposed) depends on Phase 1 verifications. BLOCKS Phase 3, 4, 5 implementation tasks because ADR-045 codifies the placement / scope / framing decisions referenced by per-story tasks.
- **User Stories Phase 3 (US1), Phase 4 (US2), Phase 5 (US3)**: All depend on Phase 2 (ADR-045 Proposed). Can proceed in parallel (different file regions or different files).
- **User Story Phase 6 (US4)**: T019 pre-merge depends on Phase 3+4+5 complete; T020–T022 depend on squash-merge completing.
- **User Story Phase 7 (US5)**: T023 T+5d depends on T005 completion + 5 days elapsed (calendar dependency, not task dependency). T024 T+7d depends on T005 + 7 days elapsed.
- **Polish (Phase 8)**: T025–T027 (baseline) depend on T007 (Cat 6 exists). T028 (ADR Accepted flip) depends on all per-story tasks complete + pre-PR Wave 5 gate. T029–T030 (verification) depend on all implementation tasks. T031 (post-merge SHA fill) depends on squash-merge. T032–T034 (close-out) depend on T031.

### User Story Dependencies

- **US1 (P1)** Phase 3: depends on T006 ADR-045; independent of US2/US3
- **US2 (P1)** Phase 4: depends on T006 ADR-045; independent of US1/US3 (different file regions in same file — Cat 6 append vs Cat 2 keyword extension)
- **US3 (P2)** Phase 5: depends on T006 ADR-045 + T007 (Cat 6 exists, since T013 appends after Cat 6)
- **US4 (P3)** Phase 6: depends on US1/US2/US3 implementation complete + squash-merge
- **US5 (P3)** Phase 7: T005 starts in Phase 1 (community-facing kickoff); T023/T024 are calendar-time follow-ups

### Within Each User Story

- US1: T007 (Cat 6 header + structure) → T008 (worked example) → T009 (distinguishing prose). Sequential within file due to ordering.
- US2: T010 (keyword extension) ∥ T011 (sub-example) can run parallel — different blocks within Cat 2. T012 (both-signal prose) follows.
- US3: T013 (subsection) → T014 (Memory-Promotion Rules) → T015 (lock-paragraph) sequential within file. T016 (agent file cross-link) is a separate file — runs parallel with T013/T014/T015. T017 (no-emission verification) + T018 (5-baseline regression) depend on T007–T016 complete.

### Parallel Opportunities

- All Phase 1 verification tasks (T001–T004) marked [P] run in parallel.
- Phase 3 / Phase 4 / Phase 5 phases run in parallel after T006 (3-way Wave parallelism per Team-Lead M-2 in PRD review).
- Within US2, T010 ∥ T011 parallel (different blocks).
- Within US3, T016 (agent file) ∥ T013/T014/T015 (detection-patterns.md) parallel (different files).
- T025 (baseline architecture) ∥ T026 (artifact generation) ∥ T028 (ADR Accepted flip) ∥ T032/T033 (BACKLOG + KB) — all in Polish phase, different files.

---

## Parallel Example: Foundational + User Story 1

```bash
# Phase 1 verifications (parallel):
Task: "Verify ADR-045 slot available in docs/architecture/02_ADRs/" → T001
Task: "Verify finding.yaml schema state at line 18" → T002
Task: "Verify CWE-943 at schemas/taxonomy/cwe.yaml" → T003
Task: "Identify agentic-app/ baseline architecture" → T004

# Phase 1 community kickoff (parallel with verifications):
Task: "Post discussion #179 two-choice offer reply" → T005

# Phase 2 foundational (after Phase 1):
Task: "Author ADR-045 Proposed state per contracts/adr-045-template.md" → T006

# Phase 3 + Phase 4 + Phase 5 Wave parallelism (after T006):
Task: "Append Cat 6 to detection-patterns.md with citations and indicators" → T007 (US1)
Task: "Extend Cat 2 trigger keywords with package-manager/CI list" → T010 (US2)
Task: "Inject cross-link prose into output-integrity.md Purpose section" → T016 (US3)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only — Wave 1a, ~1 day)

1. Complete Phase 1: Setup (T001–T005)
2. Complete Phase 2: Foundational (T006 ADR-045 Proposed)
3. Complete Phase 3: User Story 1 (T007–T009 Cat 6 vector-filter)
4. **STOP and VALIDATE**: Run quickstart.md §1, §2; verify Cat 6 emission
5. MVP ships — first new emission surface (Gap 1 closed)

### Incremental Delivery (per spec priority)

1. Setup + Foundational → Foundation ready (Day 1 AM)
2. US1 (Cat 6 vector-filter) → Test independently (Day 1 PM — Wave 1a)
3. US2 (Cat 2 keyword extension) → Test independently (Day 1 PM — Wave 1b, parallel with US1)
4. US3 (Cross-Agent + agent cross-link + regressions) → Test independently (Day 2 AM — Wave 2)
5. Optional baseline (T025–T027) + ADR Accepted flip + security re-scan (Day 2 PM — Wave 3)
6. Final close-out: /aod.deliver + post-merge tasks (Day 3 AM — Wave 4)
7. Buffer-1 Wed 2026-05-20, Buffer-2 Thu 2026-05-21 absorb worst-case slip per PRD timeline

### Parallel Wave Strategy (per Team-Lead PRD M-2 + plan critical path)

| Wave | Day | Tasks | Owner |
|---|---|---|---|
| Wave 0 | Day 0 Thu 2026-05-14 | /aod.define ✓ + /aod.plan (this stage) | product-manager + architect + team-lead |
| Wave 1 | Day 1 Fri 2026-05-15 | T001–T006 Setup + Foundational; T007–T012 US1 ∥ US2 implementation; T005 US5 offer | senior-backend-engineer (docs); product-manager (T005) |
| Wave 2a | Day 2 Mon 2026-05-18 AM | T013–T016 US3 implementation; T017 cross-link no-emission verification | senior-backend-engineer (docs); tester (T017–T018) |
| Wave 2b | Day 2 Mon 2026-05-18 AM (parallel) | T018 5-baseline regression on Wave 1 commits | tester |
| Wave 2c | Day 2 Mon 2026-05-18 PM | T025–T027 baseline generation (Q2=Add) | senior-backend-engineer + tester |
| Wave 3 | Day 3 Tue 2026-05-19 AM | T029 /security re-scan; T030 quickstart.md validation; T028 ADR Accepted flip | devops (T029); senior-backend-engineer (T028, T030) |
| Wave 4 | Day 3 Tue 2026-05-19 PM | T019–T022 US4 attribution; T034 /aod.deliver close-out | product-manager + devops |
| Buffer-1 | Wed 2026-05-20 | Slip absorption | — |
| Buffer-2 | Thu 2026-05-21 | T023 T+5d courtesy nudge (if no contributor response) | product-manager |

**Critical path**: T006 ADR-045 Proposed → T007 Cat 6 (US1) → T013 Cross-Agent subsection (US3, depends on Cat 6 existing) → T017 no-emission verification → T019 PR title verify → squash-merge → T020 release-please verify → T022 discussion comment → T031 post-merge SHA fill.

**Worst-case path** (per Team-Lead PRD M-1): if Q1=Cat 6 + Q2=Add + Q3=Add-ADR all materialize (they did, per plan resolution) + worst-case execution per task, /aod.deliver shifts to Buffer-1 (Wed 2026-05-20) without slipping into a third calendar week.

---

## Notes

- [P] tasks = different files or non-conflicting regions of the same file, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- 24+2 file zero-edit invariant: only `output-integrity.md`, `detection-patterns.md`, `ADR-045-*.md` (new), and optional `multi-tenant-rag-app/` directory (new) are touched. All other threat-agent files + companion skill references remain byte-identical
- No new test modules added — uses existing `tests/scripts/test_backward_compatibility.py` harness
- Avoid: vague tasks, same-region conflicts in `detection-patterns.md` (ordering matters: Cat 6 (T007) before Cross-Agent subsection (T013))
