# Quickstart: F-292 Output-Integrity Cross-Sink Refinement

**Feature**: F-292
**Phase**: 1 (Design)
**Date**: 2026-05-14

This quickstart shows a verifier how to confirm the F-292 refinement landed correctly. Each section maps to one or more spec functional requirements and success criteria.

---

## 1. Verify FR-001: Cat 6 Vector-Filter Pattern Surface Exists

```bash
grep -E "vector|qdrant|pinecone|search.dsl|CWE-943" .claude/skills/tachi-output-integrity/references/detection-patterns.md | head -10
```

**Expected**: At least 5 matches including engine names (`qdrant`, `pinecone`) and CWE pinning (`CWE-943`).

**Stronger check** (section heading present):
```bash
grep -E "^### 6\. Vector" .claude/skills/tachi-output-integrity/references/detection-patterns.md
```

**Expected**: 1 match for `### 6. Vector / Search-DSL Injection` (or similar heading depth-3 Cat 6 entry).

---

## 2. Verify FR-002 + FR-003: Cat 6 Worked Example with Mitigation + CWE + OWASP

```bash
grep -E "OWASP LLM08|OWASP LLM05|CWE-943|pre-retrieval filtering|namespace-per-tenant" \
  .claude/skills/tachi-output-integrity/references/detection-patterns.md
```

**Expected**: ≥3 matches confirming OWASP framework anchor, CWE pinning, and at least one industry-named mitigation.

---

## 3. Verify FR-004: Package-Manager / CI-Workflow Keywords

```bash
grep -E "npm install|pip install|apt install|brew install|gh workflow|actions/|uses:|package-lock|requirements\.txt" \
  .claude/skills/tachi-output-integrity/references/detection-patterns.md | wc -l
```

**Expected**: ≥9 matches (one per keyword from the FR-004 list).

---

## 4. Verify FR-005: Package-Manager Worked Example with Mitigation

```bash
grep -E "allowlist of registries|sandbox|Sigstore|microVM|gVisor" \
  .claude/skills/tachi-output-integrity/references/detection-patterns.md
```

**Expected**: ≥1 match for each of the three mitigation classes (allowlist / sandbox / signature gate).

---

## 5. Verify FR-006 + FR-007: Cross-Agent Handoff Sinks Subsection + Cross-Links + No-Emission Statement

```bash
grep -E "Cross-Agent Handoff|harmless as text|tool-abuse\.md|data-poisoning\.md|does NOT emit" \
  .claude/skills/tachi-output-integrity/references/detection-patterns.md
```

**Expected**: ≥4 matches confirming subsection heading, boundary phrase, both cross-link targets, and explicit no-emission invariant statement.

---

## 6. Verify FR-008: Memory-Promotion Rules Schema Example

```bash
grep -E "Memory-Promotion Rules|promotable_keys|value_schema|tenant_scope|A-MEMGUARD" \
  .claude/skills/tachi-output-integrity/references/detection-patterns.md
```

**Expected**: ≥4 matches confirming the pattern name, three required fields (`promotable_keys`, `value_schema`, `tenant_scope`), and A-MEMGUARD academic anchor.

**Stronger check** (OWASP ASI06 NOT LLM04 per PM finding alignment):
```bash
grep -E "OWASP ASI06|Memory & Context Poisoning" .claude/skills/tachi-output-integrity/references/detection-patterns.md
```

**Expected**: ≥1 match.

```bash
grep -E "OWASP LLM04" .claude/skills/tachi-output-integrity/references/detection-patterns.md | grep -v "NOT.*LLM04\|distinct from LLM04"
```

**Expected**: 0 matches. (LLM04 should appear ONLY in the form "NOT LLM04" or "distinct from LLM04" — never as the primary anchor for Memory-Promotion Rules.)

---

## 7. Verify FR-009: Agent File Cross-Link Prose ≤10 Line Diff

```bash
git diff main -- .claude/agents/tachi/output-integrity.md | grep -E "^[+-]" | grep -vE "^[+-]{3}" | wc -l
```

**Expected**: ≤10.

**Content check**:
```bash
grep -E "tool-abuse|data-poisoning|Cross-agent handoff" .claude/agents/tachi/output-integrity.md
```

**Expected**: ≥3 matches in the Purpose section.

---

## 8. Verify FR-010 + SC-010: 22+2 File Zero-Edit Invariant

```bash
# Threat-agent file surface — only output-integrity.md modified
git diff main --name-only -- .claude/agents/tachi/ | sort
```

**Expected**: Only `output-integrity.md` appears.

```bash
# Skill-reference file surface — only tachi-output-integrity modified
git diff main --name-only -- .claude/skills/ | sort
```

**Expected**: Only files under `.claude/skills/tachi-output-integrity/` appear.

**Explicit F-4 trust-exploitation check** (per PM L-1 resolution):
```bash
git diff main -- .claude/agents/tachi/human-trust-exploitation.md
git diff main -- .claude/skills/tachi-human-trust-exploitation/
```

**Expected**: Both empty.

---

## 9. Verify FR-011 + SC-011: No Schema Bump

```bash
git diff main -- schemas/finding.yaml
```

**Expected**: Empty output.

```bash
grep "^schema_version:" schemas/finding.yaml
```

**Expected**: `schema_version: "1.8"` (UNCHANGED from current state).

---

## 10. Verify FR-012 (Conditional Q2 = Add): Multi-Tenant RAG Baseline

```bash
ls examples/multi-tenant-rag-app/
```

**Expected** (if Q2=Add per plan.md resolution): directory exists with `architecture.md` and auto-generated artifacts.

```bash
# Run tachi.threat-model and verify Cat 6 emission
SOURCE_DATE_EPOCH=1700000000 tachi.threat-model examples/multi-tenant-rag-app/architecture.md > /tmp/multi-tenant.json
jq '.runs[0].results[] | select(.ruleId | startswith("OI-")) | select(.message.text | contains("vector") or contains("Qdrant") or contains("Pinecone"))' /tmp/multi-tenant.json
```

**Expected**: At least 1 finding emitted under Cat 6 surface, with the engine name (Qdrant or Pinecone) in the message.

---

## 11. Verify SC-003: Cross-Link No-Emission on `agentic-app/` Baseline

```bash
# Pre-F-292 OI-tagged subset (use main branch or git stash)
SOURCE_DATE_EPOCH=1700000000 tachi.threat-model examples/agentic-app/architecture.md > /tmp/agentic-current.json
jq '.runs[0].results[] | select(.ruleId | startswith("OI-"))' /tmp/agentic-current.json > /tmp/oi-current.json

# Post-F-292 OI-tagged subset (use feature branch)
git checkout 292-output-integrity-cross-sink-refinement
SOURCE_DATE_EPOCH=1700000000 tachi.threat-model examples/agentic-app/architecture.md > /tmp/agentic-post.json
jq '.runs[0].results[] | select(.ruleId | startswith("OI-"))' /tmp/agentic-post.json > /tmp/oi-post.json

# Byte-identical comparison
diff /tmp/oi-current.json /tmp/oi-post.json
```

**Expected**: Empty output (OI-scoped finding subset byte-identical).

---

## 12. Verify SC-004: 5 Non-Qualifying Baselines Byte-Identical

```bash
for baseline in web-app microservices ascii-web-api mermaid-agentic-app free-text-microservice; do
  SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py::test_${baseline}_baseline_byte_identical -v
done
```

**Expected**: All 5 tests PASS.

---

## 13. Verify SC-007: CHANGELOG Attribution

```bash
grep -E "292:|@armorer-labs|armorer-labs" CHANGELOG.md | head -5
```

**Expected**: ≥1 match referencing F-292 in the F-260 attribution form.

---

## 14. Verify SC-008: Discussion #179 Delivery Comment

```bash
gh api repos/davidmatousek/tachi/discussions/179/comments --jq '.[] | select(.author.login=="davidmatousek") | {created_at, body_excerpt: (.body | .[0:200])}' | head -20
```

**Expected**: A delivery comment posted within 24 hours of merge linking the PR, pattern-catalog anchors, and CHANGELOG section. [MANUAL-ONLY] reviewer inspects the comment content.

---

## 15. Verify SC-013: Conventional Commit + Release-Please Trigger

```bash
# After squash-merge to main
gh pr list --state closed --search "head:292-output-integrity-cross-sink-refinement" --json title --jq '.[0].title'
```

**Expected**: `feat(292): output-integrity cross-sink refinement` (or equivalent Conventional Commit form).

```bash
# Within 30 seconds of squash-merge
sleep 30
gh pr list --state open --search "release-please" --limit 3 --json title
```

**Expected**: A release-please PR is open.

**If release-please did NOT open** (per project memory `feedback_aod_deliver_release_gate.md`):
```bash
git commit --allow-empty -m "feat(292): output-integrity cross-sink refinement — release marker"
git push origin main
```

---

## 16. Verify SC-014: ADR-045 Accepted Before Squash-Merge

```bash
# Status field is Accepted
grep "^\\*\\*Status\\*\\*:" docs/architecture/02_ADRs/ADR-045-output-integrity-cross-sink-refinement.md
```

**Expected**: `**Status**: Accepted` (post pre-PR Wave 5 flip).

```bash
# Accepted-commit-SHA placeholder pre-merge, real SHA post-merge
grep "Accepted-commit-SHA" docs/architecture/02_ADRs/ADR-045-output-integrity-cross-sink-refinement.md
```

**Expected pre-merge**: `**Accepted-commit-SHA**: \`<pending-post-merge-fill>\``
**Expected post-merge** (after delivery step fills): `**Accepted-commit-SHA**: \`{actual_sha_7_chars}\`` (or full 40-char SHA per project convention).

---

## 17. Verify SC-012: Security Re-Scan Zero New Findings

```bash
# Run /security skill on modified file surface
/security  # via Claude Code skill
```

**Expected**: Zero new findings on the modified files (`.claude/skills/tachi-output-integrity/references/detection-patterns.md`, `.claude/agents/tachi/output-integrity.md`, `docs/architecture/02_ADRs/ADR-045-*.md`, optional `examples/multi-tenant-rag-app/`).

---

## End-to-End Smoke Test

After all 17 verifications above pass, the F-292 refinement is ready for `/aod.deliver`. The delivery step performs:
1. Pre-merge PR title verification (`feat(292):` prefix per SC-013)
2. Squash-merge to main
3. Release-please PR opens within 30 seconds (or empty release-marker commit if it doesn't)
4. Post-merge ADR-045 Accepted-commit-SHA fill
5. Discussion #179 delivery comment posting (within 24h)
6. KB entry creation (if any pattern or institutional knowledge was generated)
7. BACKLOG.md regeneration
