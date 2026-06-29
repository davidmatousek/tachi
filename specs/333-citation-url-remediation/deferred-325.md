# Deferred: Issue #325 — Local-File Citation Edges (FR-005 / PM Carry-Forward M2)

> **Status**: DEFERRED STANDALONE — out of F-333 scope
> **Formalized**: 2026-06-29 (T002)
> **FR reference**: FR-005 (spec.md); AC-1 documented-deferred artifact for `/aod.deliver`
> **Tracking issue**: #325

---

## Verification

Grepped `schemas/taxonomy/crosswalk.yaml` for `citation:` lines containing
`.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`.

**Actual edge count found**: **31 edges** across 8 distinct `tachi-control-category` source IDs:

| Source ID (tachi-control-category) | Edge count |
|------------------------------------|-----------|
| `logging-audit` | 6 |
| `input-validation` | 5 |
| `access-control` | 5 |
| `authentication` | 4 |
| `encryption` | 4 |
| `rate-limiting` | 3 |
| `csrf-protection` | 2 |
| `csp-security-headers` | 2 |
| **Total** | **31** |

All 31 edges are `tachi-control-category → nist-ai-rmf` edge type with:
```
citation: .claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md
```

The `citation:` field points to a LOCAL FILE path, not a web URL. This means:
- The #332 link-rot monitor does NOT flag these (the monitor checks HTTP URLs, not local paths).
- The dead `https://doi.org/10.6028/NIST.AI.100-1` DOI (FR-003 target) is NOT the citation used here.
- These edges are therefore a **distinct defect class** from the dead-DOI issue addressed by FR-003.

---

## Defect Classification

| Attribute | Value |
|-----------|-------|
| Defect type | Citation-unsupported local-file reference |
| Files affected | `schemas/taxonomy/crosswalk.yaml` |
| Citation pattern | `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` (local path) |
| Edge type | `tachi-control-category → nist-ai-rmf` (primary edges) |
| Edge count | 31 edges, 8 distinct control categories |
| Detected by | Manual inspection; NOT surfaced by #183 link-rot monitor (monitor is HTTP-only) |
| Monitor coverage | Out of scope for scheduled URL monitor |

---

## Why FR-003 Does NOT Resolve These

FR-003 (F-333 US-2) re-points the dead `https://doi.org/10.6028/NIST.AI.100-1` DOI in
`schemas/taxonomy/nist-ai-rmf.yaml` (73 records). That fix touches `url:` fields in the
NIST catalog itself.

The 31 #325 edges in `crosswalk.yaml` cite a local markdown file, not the dead DOI:
- They are `citation:` fields, not `url:` fields.
- They reference an internal skill reference doc, not an external URL.
- The defect is that a local file path is used as a citation instead of an authoritative
  external URL — a citation-quality issue, not link-rot.

These are **separate defect classes** requiring separate scoping, research, and remediation.

---

## Deferral Decision

| Attribute | Value |
|-----------|-------|
| F-333 scope decision | **OUT OF SCOPE** (FR-005, spec.md line 127) |
| Reason | Distinct defect class; not addressable by the F-333 DOI re-point; requires independent scoping |
| Deferred to | Standalone issue #325 |
| PM carry-forward | M2 (plan.md sign-off notes) |
| Action at deliver | Cite this file as FR-005 AC-1 documented-deferred artifact |

**AC-1 fulfillment**: Given the #325 edges, when F-333 scope is finalized, they are
documented as deferred-standalone and not modified by this feature. This file is that
documentation. F-333 implementation tasks (T008–T014) MUST NOT modify any of the 31
crosswalk edges identified above.

---

## Follow-On Work (Issue #325)

Resolution of #325 requires:
1. Determine the correct authoritative external URL(s) for each `tachi-control-category → nist-ai-rmf` mapping.
2. Replace local-file `citation:` paths with verified external references.
3. Confirm the `nist-ai-rmf-mapping.md` skill reference doc either (a) can be retired or (b) remains as an internal reference with no citation role.

This work is independent of F-333 and should be scoped as a standalone feature or maintenance item.
