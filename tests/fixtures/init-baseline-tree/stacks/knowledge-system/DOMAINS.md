# Domain Adaptation Guide

This guide maps the knowledge-system scaffold's two-level architecture to specific knowledge domains. Use it to understand how each architectural layer translates to your domain, then fill in the blank worksheet for your own domain.

**Usage**: This is a reference document. It is NOT loaded as agent context during pack activation. Consult it when scaffolding a new knowledge system to understand where your domain content belongs.

---

## Architecture Layers

The scaffold has two levels, each with distinct layers:

### Orchestration Layer (`.claude/`)

| Layer | Purpose |
|-------|---------|
| Commands | One command per user workflow — the verbs of your system |
| Agents | Domain-specialist personas invoked by commands |
| Skills | Reusable multi-step operations shared across commands |

### Content Architecture Layer

| Layer | Purpose |
|-------|---------|
| VoiceProfile (`_Global/`) | Perspective, tone, sentence patterns — the voice contract |
| StyleGuide (`_Global/`) | Structure rules, formatting standards, anti-patterns |
| MasterContent (`_Global/`) | Core reusable content — never modified per-output |
| Narratives (`_Global/`) | Atomic story fragments for selective embedding |
| ProjectMeta (`_Config/`) | Project identity and content tracking |
| ContextLoading (`_Config/`) | Which content loads per workflow phase |
| ScoringRubric (`_Config/`) | Quality dimensions and passing threshold |
| Presets (`_Config/`) | Audience, format, and role configurations |
| Terms (`_Config/`) | Domain terminology — one file per term |
| Templates (`_Templates/`) | Output format definitions — one subfolder per format |
| Output (`_Output/`) | Active work-in-progress instances |
| Archive (`_Archive/`) | Completed outputs with metadata |

---

## Domain: Resume Tailoring (Validated)

A system that produces tailored resumes from a professional's master content, adapting voice and content selection to match specific job postings and audiences.

### Orchestration Layer

| Layer | Resume Tailoring |
|-------|-----------------|
| **Commands** | `/analyze` (parse job posting), `/draft` (generate tailored resume), `/score` (evaluate against rubric), `/export` (format for delivery — PDF, DOCX) |
| **Agents** | `resume-drafter` (content selection + voice adaptation), `job-analyzer` (posting requirements extraction), `resume-scorer` (rubric evaluation) |
| **Skills** | `extract-requirements` (parse job posting into structured requirements), `select-narratives` (match narratives to job requirements) |

### Content Architecture Layer

| Layer | Resume Tailoring |
|-------|-----------------|
| **VoiceProfile** | Professional perspective (first-person vs third-person), tone (confident, measured), sentence patterns (action-result, quantified achievements), opening patterns (summary statement style) |
| **StyleGuide** | Bullet format (action verb + context + result + metric), section ordering rules, length constraints per section, formatting standards (dates, titles, locations) |
| **MasterContent** | Complete work history entries, education records, certifications, project descriptions, technical skills inventory — all in structured markdown |
| **Narratives** | `leadership-turnaround.md`, `technical-migration.md`, `cost-reduction.md` — atomic achievement stories for selective embedding |
| **ProjectMeta** | Professional's name, target industry, version tracking, output count, last generated date |
| **ContextLoading** | `always_load`: VoiceProfile, StyleGuide; `on_demand.analyze`: Terms; `on_demand.draft`: MasterContent, Narratives, Presets; `on_demand.review`: ScoringRubric |
| **ScoringRubric** | Dimensions: keyword alignment (job posting match), voice consistency, quantification density, length compliance, ATS compatibility |
| **Presets** | `executive-formal.md`, `startup-casual.md`, `technical-detailed.md` — audience-specific formatting and tone adjustments |
| **Terms** | `agile.md`, `machine-learning.md`, `devops.md` — domain terminology with preferred phrasing and context rules |
| **Templates** | `pdf-single-page/`, `pdf-two-page/`, `docx-ats-friendly/` — output format templates |
| **Output** | `2026-03-01-senior-engineer-acme.md` — active resume draft in progress |
| **Archive** | `2026-02-15-product-manager-startup.md` — completed resume with delivery metadata |

---

## Domain: Publishing (Validated)

A system that produces edited, voice-consistent chapters or articles from a writer's master content, narratives, and style conventions.

### Orchestration Layer

| Layer | Publishing |
|-------|-----------|
| **Commands** | `/outline` (structure a new piece), `/draft` (generate chapter/article draft), `/edit` (revise against style guide), `/review` (score against rubric), `/publish` (format for publication) |
| **Agents** | `content-drafter` (voice-consistent writing), `style-editor` (StyleGuide enforcement), `content-reviewer` (rubric-based evaluation) |
| **Skills** | `embed-narrative` (weave atomic narratives into prose), `check-consistency` (cross-chapter voice and fact verification) |

### Content Architecture Layer

| Layer | Publishing |
|-------|-----------|
| **VoiceProfile** | Author's perspective (first-person memoir, third-person narrative), tone (authoritative, conversational, academic), sentence patterns (short-long rhythm, paragraph transitions), opening patterns (hook styles) |
| **StyleGuide** | Chapter structure rules, heading hierarchy, citation format, dialogue formatting, paragraph length targets, transition patterns between sections |
| **MasterContent** | Research notes, interview transcripts, fact sheets, biographical entries, reference material — structured source content for chapters |
| **Narratives** | `founding-story.md`, `customer-discovery.md`, `pivot-moment.md` — atomic story fragments that can be embedded across multiple chapters |
| **ProjectMeta** | Book/series title, genre, target word count, publication timeline, chapter tracking (drafted, edited, reviewed, published) |
| **ContextLoading** | `always_load`: VoiceProfile, StyleGuide; `on_demand.outline`: MasterContent; `on_demand.draft`: MasterContent, Narratives; `on_demand.review`: ScoringRubric; `on_demand.publish`: Templates |
| **ScoringRubric** | Dimensions: voice consistency, narrative flow, factual accuracy, engagement (hook strength), readability (grade level), structural compliance |
| **Presets** | `long-form-chapter.md`, `short-article.md`, `newsletter-excerpt.md` — format and length configurations |
| **Terms** | `product-market-fit.md`, `series-a.md`, `churn-rate.md` — domain terminology with preferred definitions and usage context |
| **Templates** | `epub-chapter/`, `blog-post/`, `newsletter/` — output format templates per publication channel |
| **Output** | `chapter-03-growth-strategy.md` — active chapter draft in progress |
| **Archive** | `chapter-01-origins.md` — completed, published chapter with publication metadata |

---

## Domain: Education (Experimental)

A system that produces curriculum materials — lesson plans, assessments, and learning guides — from a course's master content, adapted to different learning levels and formats.

> **Note**: This domain mapping is experimental. It has not been validated through a production implementation. Use as a starting point and refine based on your experience.

### Orchestration Layer

| Layer | Education |
|-------|-----------|
| **Commands** | `/plan-lesson` (create lesson plan from objectives), `/create-assessment` (generate quiz/exam), `/adapt` (adjust for learning level), `/review` (evaluate against rubric), `/package` (format for LMS or print) |
| **Agents** | `curriculum-designer` (lesson structure + learning objectives), `assessment-builder` (question generation + difficulty calibration), `content-adapter` (reading level and complexity adjustment) |
| **Skills** | `align-objectives` (map content to learning standards), `calibrate-difficulty` (adjust assessment difficulty per level) |

### Content Architecture Layer

| Layer | Education |
|-------|-----------|
| **VoiceProfile** | Teaching perspective (instructor, facilitator, mentor), tone (encouraging, formal-academic, conversational), explanation patterns (concept → example → practice), opening patterns (learning objective statement) |
| **StyleGuide** | Lesson plan structure (objectives, materials, activities, assessment, reflection), heading conventions, activity formatting, time allocation rules, accessibility requirements |
| **MasterContent** | Course syllabus, lecture notes, concept explanations, worked examples, reference materials — the canonical knowledge base for the course |
| **Narratives** | `real-world-application.md`, `historical-context.md`, `student-scenario.md` — contextual stories that make abstract concepts concrete |
| **ProjectMeta** | Course title, subject area, grade level, semester, module tracking (planned, drafted, reviewed, delivered) |
| **ContextLoading** | `always_load`: VoiceProfile, StyleGuide; `on_demand.plan-lesson`: MasterContent, Terms; `on_demand.create-assessment`: MasterContent, ScoringRubric; `on_demand.review`: ScoringRubric |
| **ScoringRubric** | Dimensions: learning objective alignment, cognitive level (Bloom's taxonomy), engagement quality, accessibility compliance, assessment validity |
| **Presets** | `introductory-level.md`, `advanced-level.md`, `workshop-format.md` — difficulty and format configurations |
| **Terms** | `photosynthesis.md`, `supply-demand.md`, `recursion.md` — domain terminology with grade-appropriate definitions |
| **Templates** | `lesson-plan/`, `quiz/`, `study-guide/`, `slide-deck-outline/` — output format templates |
| **Output** | `module-04-lesson-03-loops.md` — active lesson plan in progress |
| **Archive** | `module-01-lesson-01-intro.md` — delivered lesson with student feedback metadata |

---

## Layer-Mapping Worksheet

Copy and fill in this worksheet to map your domain to the scaffold. Each row represents one architectural layer.

### Your Domain: _______________

**Description**: _One-sentence description of what your system produces._

### Orchestration Layer

| Layer | Your Domain |
|-------|------------|
| **Commands** | _List your user-facing commands (one per workflow)_ |
| **Agents** | _List your domain-specialist agent personas_ |
| **Skills** | _List reusable multi-step operations_ |

### Content Architecture Layer

| Layer | Your Domain |
|-------|------------|
| **VoiceProfile** | _Perspective, tone, sentence patterns for your domain_ |
| **StyleGuide** | _Structure rules, formatting standards for your outputs_ |
| **MasterContent** | _What is your core reusable content? (never modified per-output)_ |
| **Narratives** | _What atomic story fragments do you embed in outputs?_ |
| **ProjectMeta** | _Project identity and tracking fields_ |
| **ContextLoading** | _Which content loads per workflow phase?_ |
| **ScoringRubric** | _What quality dimensions define a good output?_ |
| **Presets** | _What audience/format/role variations do you support?_ |
| **Terms** | _What domain terminology needs consistent usage?_ |
| **Templates** | _What output formats do you produce?_ |
| **Output** | _What does an active work-in-progress look like?_ |
| **Archive** | _What metadata accompanies a completed output?_ |

### Validation Checklist

After mapping, verify:

- [ ] Every layer has a clear, non-empty mapping
- [ ] MasterContent is genuinely reusable (not output-specific)
- [ ] Commands map to user workflows, not technical operations
- [ ] VoiceProfile describes style patterns, not personal facts
- [ ] ContextLoading phases match your command inventory
- [ ] ScoringRubric dimensions are measurable, not subjective
