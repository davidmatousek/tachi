---
description: Generate an architecture description for tachi threat modeling input
---

## User Input

```text
$ARGUMENTS
```

Consider user input before proceeding (if not empty).

## Overview

Generates a structured architecture description suitable as input for `/tachi.threat-model`. Analyzes the target codebase or project documentation to produce a DFD-style architecture description with components, data flows, trust boundaries, and external entities.

**Output**: `architecture.md` — structured architecture description in the target directory.

## Step 0: Detect Existing File

1. After determining the output path (Step 1), check if an architecture file already exists at that path
2. If the file exists:
   - Read the file contents
   - Check for YAML frontmatter (content between opening `---` and closing `---` delimiters at the start of the file)
   - If frontmatter exists, parse these fields:
     - `version` — integer version number
     - `date` — generation date (YYYY-MM-DD)
     - `description` — change summary
     - `checksum` — `sha256:{hash}` of the content body
     - `previous_version` — archive path or `null`
   - If no frontmatter is found: treat as a legacy file with version `0`
3. If no file exists at the output path: this is a fresh generation (version will be `1`)
4. Store the detected state (file exists, current version, has frontmatter) for use by Step 0a and Step 3a

## Step 0a: Archive Current Version

1. Skip this step entirely if no existing file was detected (first-time generation)
2. Derive the archive path: `{parent_dir}/.archive/v{N}/{filename}` where:
   - `{parent_dir}` = directory containing the architecture file
   - `{N}` = current version number (`0` for legacy files without frontmatter, extracted `version` for managed files)
   - `{filename}` = architecture filename (default: `architecture.md`)
3. Create the archive directory: `mkdir -p {parent_dir}/.archive/v{N}/`
4. Copy the complete file (including frontmatter, if present) to the archive location
5. If the same version already exists in the archive, overwrite it (idempotent retry — supports re-runs after failed generations)
6. Display:
   ```
   Archived v{N} to {archive_path}
   ```

## Step 0b: Guided Update Mode

1. **Skip condition**: If no existing file was detected in Step 0 (first-time generation), skip this step entirely and proceed to Step 1
2. **Display current architecture summary**: Extract and display key elements from the existing file:
   - **Components**: Services, databases, APIs, queues, caches found in the file
   - **Data flows**: Connections between components (protocols, directions)
   - **Trust boundaries**: Security zones and network boundaries
   - **External entities**: Users, third-party APIs, external services
3. **Present guided update categories** — for each category in sequence, ask the user what changed:
   - New services or components added?
   - Components removed or decommissioned?
   - Data flows changed (new connections, protocol changes)?
   - Trust boundaries modified?
   - External entities added or removed?
   - AI capabilities changed (new models, tools, agents)?
4. For each category: the user can provide specific changes or skip (indicate no changes)
5. Collect all changes as context to pass to the generation steps (Step 2 and Step 3). The collected changes inform both the architecture analysis scope and the `description` field in Step 3a.
6. **Abort condition**: If the user indicates no changes across ALL categories:
   - Leave the architecture file untouched (do not overwrite)
   - No version increment occurs
   - Display: `No changes indicated. Architecture file unchanged.`
   - Skip Steps 1, 2, 3, and 3a entirely — proceed directly to Step 4 with a "no changes" report

## Step 1: Determine Scope

1. If `$ARGUMENTS` specifies a path or directory, use that as the analysis target
2. Default: analyze the current working directory
3. If `$ARGUMENTS` contains `--output <path>`:
   - Write output to the specified path
   - Default: `docs/security/architecture.md`

## Step 2: Analyze Architecture

Examine the target for architectural elements:

1. **Components**: Services, modules, databases, APIs, queues, caches
2. **Data Flows**: How data moves between components (protocols, formats)
3. **Trust Boundaries**: Network boundaries, authentication gates, privilege transitions
4. **External Entities**: Users, third-party APIs, external services
5. **Data Stores**: Databases, file systems, object storage, caches

Sources to examine (in priority order):
- Existing architecture documentation (`docs/architecture/`)
- Infrastructure files (Dockerfile, docker-compose, Kubernetes manifests, Terraform)
- API definitions (OpenAPI specs, GraphQL schemas, protobuf)
- Source code structure (service boundaries, module organization)
- Configuration files (environment variables, service endpoints)

## Step 3: Generate Architecture Description

Produce a structured markdown document containing:

1. **System Overview**: One-paragraph description of the system
2. **Architecture Diagram**: Mermaid flowchart showing components and data flows
3. **Components Table**: Name, type, description, technology for each component
4. **Data Flows Table**: Source, destination, protocol, data classification
5. **Trust Boundaries**: Named boundaries with contained components
6. **External Entities**: Name, type, interaction pattern

## Step 3a: Inject Frontmatter

This step uses a two-pass write pattern: Step 3 writes the markdown body first, then this step computes the checksum and prepends frontmatter.

1. Compute the checksum of the file written by Step 3: run `shasum -a 256 {output_path}` and capture the hash
2. Determine the version number:
   - First-time generation (no existing file): `version: 1`, `previous_version: null`
   - Legacy file upgrade (existing file without frontmatter): `version: 1`, `previous_version: .archive/v0/{filename}`
   - Managed update (existing file with frontmatter containing version N): `version: N+1`, `previous_version: .archive/v{N}/{filename}`
3. Assemble the YAML frontmatter block:
   ```yaml
   ---
   version: {version_number}
   date: {YYYY-MM-DD}
   description: "{change_summary}"
   checksum: sha256:{hash}
   previous_version: {archive_path_or_null}
   ---
   ```
4. Prepend the frontmatter to the file: read the current file content, then write the frontmatter block followed by the content
5. For the `description` field:
   - First-time generation: `"Initial architecture description"`
   - Legacy upgrade: `"Lifecycle upgrade from unmanaged file"`
   - Managed update with guided mode (Step 0b collected changes): Summarize the specific changes from the guided update categories into a concise, human-readable string (e.g., `"Added payment gateway service, updated API data flows, removed legacy auth component"`)
   - Managed update without guided mode (edge case — future direct-edit flows): `"Architecture update"`

## Step 4: Report

Display summary:

```
ARCHITECTURE DESCRIPTION GENERATED
Output: {output_path}
Version: {version_number}
Checksum: sha256:{hash}
Archived: {archive_path or "n/a (first generation)"}

Components: {count}
Data Flows: {count}
Trust Boundaries: {count}
External Entities: {count}

Next: /tachi.threat-model {output_path}
```

## Usage Examples

```bash
# Analyze current project
/tachi.architecture

# Analyze specific directory
/tachi.architecture src/backend/

# Custom output location
/tachi.architecture --output reports/arch.md
```
