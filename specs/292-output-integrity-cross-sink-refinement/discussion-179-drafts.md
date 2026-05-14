# Discussion #179 Reply Drafts (T005 + T022)

These are ready-to-paste drafts for the two community-facing replies F-292 requires. They are NOT posted automatically — you (the maintainer) need to post them under your GitHub authentication.

URL: https://github.com/davidmatousek/tachi/discussions/179

---

## Draft 1 — T005: Two-Choice Contribution Offer (post within 48h of plan sign-off)

**Spec anchor**: FR-015 + SC-009
**Target post date**: 2026-05-16 (T+48h from spec sign-off 2026-05-14); best-effort by Fri evening Day 1 PM acceptable per timeline.

```markdown
@armorer-labs — first, thank you for the thoughtful gap-analysis comment. The three pattern surfaces you named (vector-DB metadata filter / package-manager + CI-workflow execution sinks / cross-agent handoff boundary disambiguation) all landed in our planning queue as legitimate coverage gaps in the shipped `output-integrity` agent, and we've now drafted a refinement that closes them.

The refinement is tracked as **F-292** (Output-Integrity Cross-Sink Refinement). The architectural decisions are codified in ADR-045 (see `docs/architecture/02_ADRs/ADR-045-output-integrity-cross-sink-refinement.md` on the feature branch). PRD #292, spec.md, plan.md, and tasks.md are all PM + Architect + Team-Lead signed off.

I want to honor your contribution end-to-end. Following our F-260 community-merge precedent (where @north-echo's discussion comment converted into PR #262 with native authorship), I'd like to offer you two paths:

**Path (a) — contributor-authored PR**:
- I assign you Issue #292 and suggest the branch name `292-output-integrity-cross-sink-refinement`.
- You author the PR; I provide maintainer steerage (review-ready guidance, ADR-045 + plan.md + tasks.md as your implementation reference, code review on draft).
- Your authorship is preserved natively in the GitHub PR commit history.
- The CHANGELOG attributes the F-260 form: `* **292:** output-integrity cross-sink refinement ([#{PR}](...)) ({SHA7})`.

**Path (b) — maintainer-authored PR with explicit attribution**:
- I author the PR; the squash-merge commit carries `Co-Authored-By: @armorer-labs <your-email>` (if you agree to that form).
- The CHANGELOG entry explicitly lists "Surfaced by @armorer-labs in discussion #179."
- You're recognized in the contribution chain even if you don't have the bandwidth to drive a PR right now.

Both paths preserve your attribution; the choice is about whether you want to drive the PR or have the work proceed without that overhead on your side.

**SLA**: I'll proceed on the maintainer track in parallel so the refinement isn't blocked, and I'll default to path (b) with attribution preserved if I don't hear back within 7 days (by 2026-05-21). If you'd prefer path (a), just reply on this thread and I'll re-route — I'll pause the maintainer track at the pre-PR gate so we don't double-author.

Either way: thanks for the contribution.
```

---

## Draft 2 — T022: Delivery Comment (post within 24h of PR squash-merge)

**Spec anchor**: FR-014 + SC-008
**Target post date**: within 24h of squash-merge to main (best-effort; next-business-day acceptable for weekend / end-of-day merges)
**Prerequisite**: PR squash-merged, release-please PR opened, CHANGELOG entry generated

```markdown
@armorer-labs — F-292 (Output-Integrity Cross-Sink Refinement) just shipped on main. Quick summary of what landed and where:

**PR**: #{PR} (squash-merged {YYYY-MM-DD})
**CHANGELOG**: [v{NEXT_VERSION}](https://github.com/davidmatousek/tachi/blob/main/CHANGELOG.md#v{NEXT_VERSION})
**Release**: [v{NEXT_VERSION}](https://github.com/davidmatousek/tachi/releases/tag/v{NEXT_VERSION})

**Three gap closures (per your discussion #179 comment)**:

1. **Vector / Search-DSL Injection (new Cat 6)** — [detection-patterns.md#6-vector--search-dsl-injection](https://github.com/davidmatousek/tachi/blob/main/.claude/skills/tachi-output-integrity/references/detection-patterns.md#6-vector--search-dsl-injection). LLM-synthesized Pinecone / Qdrant metadata filters into multi-tenant query interfaces now emit `OI-{N}` findings under Cat 6 with CWE-943 primary + OWASP LLM08:2025 primary. Worked example exercises the failure mode (LLM-output-layer filter composition without tenant_id pin); 4 defense-in-depth mitigations enumerated.

2. **AI-coding-assistant package-manager sinks (Cat 2 extension)** — [detection-patterns.md#2-server-side-execution-sinks](https://github.com/davidmatousek/tachi/blob/main/.claude/skills/tachi-output-integrity/references/detection-patterns.md#2-server-side-execution-sinks-sqli--os-command--code-injection). Cat 2 trigger-keyword list extended with `npm install`, `pip install`, `apt install`, `brew install`, `gh workflow`, `actions/`, `uses:`, `package-lock`, `requirements.txt`. Sub-example anchors SANDWORM_MODE npm worm + LiteLLM PyPI compromise + arXiv 2605.07135 (Agentic Workflow Injection) for real-world urgency.

3. **Cross-Agent Handoff Sinks (navigational subsection)** — [detection-patterns.md#cross-agent-handoff-sinks](https://github.com/davidmatousek/tachi/blob/main/.claude/skills/tachi-output-integrity/references/detection-patterns.md#cross-agent-handoff-sinks-navigational--no-emission-from-output-integrity). Boundary phrase ("harmless as text, dangerous as tool argument or memory entry"), cross-links to `tool-abuse` (tool-argument handoff) and `data-poisoning` (durable-memory-write, OWASP ASI06 — NOT LLM04), and a Memory-Promotion Rules YAML schema example (promotable_keys / value_schema / tenant_scope) for the canonical durable-write mitigation pattern.

**Architecture decision record**: [ADR-045](https://github.com/davidmatousek/tachi/blob/main/docs/architecture/02_ADRs/ADR-045-output-integrity-cross-sink-refinement.md) (Heuristic A enrichment at same-agent scope; 7 decisions mirroring ADR-032 template).

**New example baseline**: [`examples/multi-tenant-rag-app/`](https://github.com/davidmatousek/tachi/tree/main/examples/multi-tenant-rag-app) exercises the Cat 6 vector-filter sink for adopter regression-protection.

Thank you again for the contribution. If you have follow-on gap analyses or want to deepen the multi-tenant RAG or AI-coding-assistant coverage further, this discussion thread stays open. Or open a new issue any time.
```

---

## Optional Draft 3 — T023: T+5d Courtesy Nudge (conditional, only if no contributor response by 2026-05-19)

**Spec anchor**: PM L-3 + Architect L3 resolution

```markdown
@armorer-labs — quick courtesy update. I haven't heard back on the two-choice contribution offer above, which is totally fine — I know discussion threads can drift off your radar. Just wanted to confirm the maintainer track is proceeding on schedule and your attribution is preserved regardless of which path lands at the 7-day SLA (2026-05-21). I'll post a delivery comment here once the PR merges to main. No action required from you.
```

---

## Optional Draft 4 — T024: T+7d SLA Breach Decision Log (conditional, only if no contributor response by 2026-05-21)

**Format**: Comment on the PR description or in the squash-merge commit message. Not posted to discussion #179.

```markdown
T024 SLA decision log (2026-05-21): contributor @armorer-labs did not respond to the two-choice contribution offer posted on 2026-05-14 within the 7-day SLA. Defaulting to path (b) maintainer-authored per spec FR-015. Attribution preserved via `Co-Authored-By: @armorer-labs <handle>` commit trailer and CHANGELOG entry "Surfaced by @armorer-labs in discussion #179."
```

---

## Posting Instructions

```bash
# T005 (post to discussion #179):
gh api graphql -F discussionId="$(gh api repos/davidmatousek/tachi/discussions/179 --jq '.node_id')" \
  -F body="$(cat <<'EOF'
# paste Draft 1 content here
EOF
)" -F query='mutation($discussionId: ID!, $body: String!) {
  addDiscussionComment(input: {discussionId: $discussionId, body: $body}) {
    comment { url }
  }
}'

# Alternative manual approach:
# 1. Open https://github.com/davidmatousek/tachi/discussions/179 in browser
# 2. Scroll to "Add a comment"
# 3. Paste Draft 1 content
# 4. Click "Comment"
```

The manual browser approach is fine — the `gh api graphql` flow is just a reference for scripted use.
