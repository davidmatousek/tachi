# AOD Lifecycle Infographic

**Version**: 2.0.0

**Related**:
- [AOD Quickstart](AOD_QUICKSTART.md) -- Quick onboarding guide
- [AOD Lifecycle Reference](AOD_LIFECYCLE.md) -- Full stage reference, governance tiers, end-to-end example
- [SDLC Triad Reference](../AOD_TRIAD.md) -- Governance layer documentation

---

```
+==============================================================================================+
||              AOD: AGENTIC ORIENTED DEVELOPMENT LIFECYCLE                                   ||
||                        End-to-End Feature Lifecycle                                         ||
+==============================================================================================+

  TRIAD GOVERNANCE LAYER (configurable — Light / Standard / Full)
  +---------------------------------------------------------------------------+
  |  [PM]  What & Why: Scope & requirements                                   |
  |  [Architect]  How: Technical decisions                                     |
  |  [Team-Lead]  When & Who: Timeline & resources                            |
  +---------------------------------------------------------------------------+

================================================================================================
  STAGE 1: DISCOVER                                              Command: /aod.discover
================================================================================================

  /aod.discover <idea>
       |
       v
  +-----------+      +--------------+      +------------------+      +------------------+
  |  Capture  | ---> | Score (ICE)  | ---> | Evidence         | ---> | PM Validation    |
  |  Idea     |      |              |      | Prompt           |      | (tier-dependent) |
  +-----------+      +--------------+      +------------------+      +------------------+
       |                    |                      |                         |
       v                    v                      v                         v
   GitHub Issue        ICE Dimensions         Evidence Capture         PM Decision
   stage:discover      +-----------+           +-----------------+
                       | Impact  1-10 |        | Score < 12      |---> Auto-deferred
                       | Confidence 1-10 |     | Score >= 12     |---> Proceed
                       | Effort  1-10 |        | Score 25+       |---> P0 Fast-track
                       +-----------+           +-----------------+

================================================================================================
  STAGE 2: DEFINE                                                Command: /aod.define
================================================================================================

  /aod.define <topic>
  +-----------------------------------------------------------------------+
  |  PM drafts PRD --> Architect + Team-Lead review --> PM finalizes       |
  |  Output: docs/product/02_PRD/{NNN}-{topic}-{date}.md                  |
  +-----------------------------------------------------------------------+
       +-----------------------------------------------------------------+
       | Gate: [PM] [Architect] [Team-Lead] TRIPLE SIGN-OFF              |
       +-----------------------------------------------------------------+
                                     |
                                     v

================================================================================================
  STAGE 3: PLAN                                                  Command: /aod.plan
================================================================================================

  /aod.plan (router — auto-detects sub-step)

  SUB-STEP 1: Specification                 /aod.spec (via /aod.plan)
  +-----------------------------------------------------------------------+
  |  Research (KB + Codebase + Architecture + Web) --> Generate spec       |
  |  Output: .aod/spec.md                                                 |
  +-----------------------------------------------------------------------+
       +-----------------------------------------------------------------+
       | Gate: [PM] PM SIGN-OFF                                          |
       +-----------------------------------------------------------------+
                                     |
                                     v
  SUB-STEP 2: Architecture Plan             /aod.project-plan (via /aod.plan)
  +-----------------------------------------------------------------------+
  |  Architecture decisions, API contracts, data models                    |
  |  Output: .aod/plan.md                                                 |
  +-----------------------------------------------------------------------+
       +-----------------------------------------------------------------+
       | Gate: [PM] [Architect] DUAL SIGN-OFF                            |
       +-----------------------------------------------------------------+
                                     |
                                     v
  SUB-STEP 3: Task Breakdown               /aod.tasks (via /aod.plan)
  +-----------------------------------------------------------------------+
  |  Task breakdown, agent assignments, parallel execution waves          |
  |  Output: .aod/tasks.md + agent-assignments.md                        |
  +-----------------------------------------------------------------------+
       +-----------------------------------------------------------------+
       | Gate: [PM] [Architect] [Team-Lead] TRIPLE SIGN-OFF              |
       +-----------------------------------------------------------------+
                                     |
                                     v

================================================================================================
  STAGE 4: BUILD                                                 Command: /aod.build
================================================================================================

  /aod.build
  +-----------------------------------------------------------------------+
  |  Wave 1: [Agent] [Agent] [Agent]   (parallel)                        |
  |       +----- Architect checkpoint -----+                              |
  |  Wave 2: [Agent] [Agent]              (parallel)                      |
  |       +----- Architect checkpoint -----+                              |
  |  Wave 3: [Agent]                       (sequential)                   |
  +-----------------------------------------------------------------------+
       +-----------------------------------------------------------------+
       | Gate: [Architect] checkpoints at wave boundaries                |
       +-----------------------------------------------------------------+
                                     |
                                     v

================================================================================================
  STAGE 5: DELIVER                                               Command: /aod.deliver
================================================================================================

  /aod.deliver
  +-----------------------------------------------------------------------+
  |  1. Definition of Done validation                                     |
  |  2. Retrospective: metrics, surprises, next ideas                     |
  |  3. KB entry from lessons learned                                     |
  |  4. New ideas --> GitHub Issues (stage:discover) --> FEEDBACK LOOP     |
  +-----------------------------------------------------------------------+
       +-----------------------------------------------------------------+
       | Gate: DoD check (all tiers)                                     |
       +-----------------------------------------------------------------+
                                    |
                                    v

================================================================================================
  STAGE 6: DOCUMENT                                              Command: /aod.document
================================================================================================

  /aod.document (human-driven — each step requires approval)
  +-----------------------------------------------------------------------+
  |  1. Code Simplification  → /simplify on changed files                 |
  |  2. Docs-Lint            → Docstrings for complex undocumented funcs  |
  |  3. CHANGELOG            → Entries from conventional commits          |
  |  4. API Sync             → Compare endpoints vs OpenAPI spec          |
  |  5. KB Review            → Validate institutional knowledge entries   |
  +-----------------------------------------------------------------------+
       +-----------------------------------------------------------------+
       | Gate: Human approval per step (accept / reject / skip)          |
       +-----------------------------------------------------------------+

  NOTE: Stage 6 is NOT part of /aod.run. It runs separately after Deliver
  because it requires sustained human interaction and judgment.

================================================================================================
  ARTIFACT TRAIL
================================================================================================

  GitHub Issue --> PRD --> spec.md --> plan.md --> tasks.md --> CODE --> Retrospective --> Quality Review
     Discover     Define    Plan       Plan       Plan       Build      Deliver          Document

================================================================================================
  OUTSIDE-THE-LIFECYCLE COMMANDS
================================================================================================

  PRE-LIFECYCLE    /aod.foundation       Guided workshop: product vision + design identity
                   /aod.kickstart        POC kickstart: consumer guide + seed features
                   /aod.blueprint        Multi-feature story generation from consumer guide

  ORCHESTRATION    /aod.run              Full lifecycle orchestrator (chains stages 1-5)
                   /aod.orchestrate      Multi-feature parallel wave execution (P0/P1/P2)

  TEMPLATE SYNC    /aod.update           Adopter pulls upstream template updates (F129)
```
