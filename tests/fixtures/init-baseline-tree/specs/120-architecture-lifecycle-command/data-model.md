# Data Model: Architecture Lifecycle Command

## Entities

### Architecture File
A markdown document managed by `/tachi.architecture` with optional YAML frontmatter.

| Field | Type | Description | Rules |
|-------|------|-------------|-------|
| version | integer | Monotonically increasing version number | Starts at 1, increments by 1 per update |
| date | ISO date | Date of this version (YYYY-MM-DD) | Set at generation/update time |
| description | string | Human-readable change summary | Populated from guided update or generation context |
| checksum | string | SHA-256 hash of content body | Format: `sha256:{hex}`, computed from body excluding frontmatter |
| previous_version | string or null | Relative path to archived predecessor | null for v1, `.archive/v{N}/{filename}` for subsequent versions |
| body | markdown | Architecture description content | Unchanged from current format (overview, diagram, tables) |

**Frontmatter Schema**:
```yaml
---
version: 1
date: 2026-04-09
description: "Initial architecture"
checksum: sha256:abc123...
previous_version: null
---
```

### Archive Entry
A frozen, read-only copy of an Architecture File at a specific version.

| Attribute | Value |
|-----------|-------|
| Location | `{parent_dir}/.archive/v{N}/{filename}` |
| Content | Complete file including frontmatter |
| Lifecycle | Append-only (idempotent per version number) |
| Created by | `/tachi.architecture` archive step |

### Architecture Snapshot
A verbatim copy of the current Architecture File placed in a threat model output folder.

| Attribute | Value |
|-----------|-------|
| Location | `{output_dir}/{filename}` (inside timestamped folder) |
| Content | Verbatim copy — no modifications |
| Created by | `/tachi.threat-model` Step 1.4 |
| Consumed by | Human review only — not parsed by downstream stages |

## State Transitions

```
[No File] --generate--> [v1, frontmatter, no archive]
[v1]      --update-->   [v2, archive/v1, frontmatter updated]
[vN]      --update-->   [v{N+1}, archive/vN, frontmatter updated]
[legacy]  --upgrade-->  [v1, archive/v0 (legacy content), frontmatter added]
[any]     --snapshot--> [copy in threat model output] (no state change to source)
```

## File Layout Example

```
docs/security/
├── architecture.md              # Current version (v3)
├── .archive/
│   ├── v0/
│   │   └── architecture.md      # Legacy (pre-frontmatter)
│   ├── v1/
│   │   └── architecture.md      # First managed version
│   └── v2/
│       └── architecture.md      # Second version
└── 2026-04-09T14-30-22/
    ├── architecture.md           # Snapshot of v3
    ├── threats.md
    ├── threats.sarif
    ├── threat-report.md
    └── attack-trees/
```
