# Contract: Input Format Specification

**Schema File**: `schemas/input.yaml`
**Producers**: Integrators (developers invoking tachi)
**Consumers**: Input parser (F-005), orchestrator (F-002)

## Purpose

Defines the 5 supported input formats, their recognition patterns, and validation rules. Integrators provide architecture descriptions in any supported format; the parser validates and normalizes them.

## Supported Formats (Priority Order)

| Priority | Format | Recognition Pattern | Trust Boundary Notation |
|----------|--------|-------------------|------------------------|
| 1 | ASCII | Box-drawing characters (`+--+`, `|`, `[...]`) | Dashed lines (`---`) or labeled zones |
| 2 | Free-text | No diagram syntax detected; prose description | Section headers or explicit "Trust boundary:" markers |
| 3 | Mermaid | `graph`, `flowchart`, `sequenceDiagram` keywords | `subgraph` blocks |
| 4 | PlantUML | `@startuml`/`@enduml` delimiters | `boundary` or `rectangle` with `<<boundary>>` stereotype |
| 5 | C4 | `Person`, `System`, `Container`, `Component` keywords | `System_Boundary` or `Enterprise_Boundary` |

## Format Field

```yaml
format:
  type: string
  enum: [auto, ascii, free-text, mermaid, plantuml, c4]
  default: auto
  description: "Explicit format declaration. 'auto' enables heuristic detection."
```

## Minimum Input Requirements

- At least 1 identifiable component
- At least 1 data flow or relationship between components
- If no components found: return error with supported format guidance

## Validation Schema Structure

```yaml
input:
  format:
    type: string
    enum: [auto, ascii, free-text, mermaid, plantuml, c4]
    default: auto
  content:
    type: string
    min_length: 10
    description: "Architecture description in the specified format"
  context:
    type: object
    optional: true
    description: "Optional metadata (project name, sensitivity, scope constraints)"
```
