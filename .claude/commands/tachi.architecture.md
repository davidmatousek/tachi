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

## Step 4: Report

Display summary:

```
ARCHITECTURE DESCRIPTION GENERATED
Output: {output_path}

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
