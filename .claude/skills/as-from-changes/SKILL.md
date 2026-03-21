---
name: as-from-changes
description: Create or update ground truth from existing changes (commits, PRs, diffs, codebase).
---

Create or update ground truth based on existing changes (code, commits, PRs).

Use this when:

- Manual changes were made without a spec
- Initializing truth for an existing codebase
- Retroactively documenting changes

**Input**: The source of changes. Must be one of:

- `--staged` -- From git staged changes
- `--commit <hash>` -- From a specific commit
- `--pr <number>` -- From a pull request
- `--diff` -- From current git diff
- `--folder <path>` -- From a specific folder
- `--codebase` -- From the entire codebase (initialization)

If no source is specified, ask the user which source to use.

**Steps**

1. **Analyze the changes**

   Based on the source, carefully analyze:
   - What files changed and how
   - What functional behavior was added or modified
   - What technical decisions were made
   - What database tables or fields were affected

   **For `--codebase` (whole codebase documentation):**

   When documenting an entire codebase, the analysis scope expands to include:
   - Overall system architecture and component interactions
   - Technology stack and framework choices
   - Deployment topology and infrastructure
   - Cross-cutting concerns (authentication, logging, error handling)
   - Integration points between subsystems

2. **Identify relevant skills**

   Search the repository for development skills (look in `.claude/skills/`,
   `.cursor/skills/`, `.github/skills/`). List all skills relevant
   to the changes discovered.

   This step is critical for avoiding documentation duplication. Read the
   content of each relevant skill to understand what implementation patterns
   they already document. The technical specs you create in step 3 must NOT
   repeat this information. Instead:

   - In the "Relevant Skills" table, list each skill with a brief
     explanation of why it is relevant to this feature
   - In "Key Implementation Patterns", document only decisions and patterns
     SPECIFIC to this feature that go beyond what the skills describe
   - Example: If a `backend-service` skill documents how to create REST
     endpoints with standard middleware, do NOT describe middleware setup
     in the technical spec. Instead, note "Follows backend-service skill
     patterns" and document only feature-specific deviations or additions.

   Think of it this way: Skills document the HOW (reusable patterns,
   conventions, templates). Truth documents the WHAT and WHY (what was
   built, what architectural decisions were made, and why).

3. **Create truth entries**

   **Truth follows domain-driven architecture.** The hierarchy is organized
   from high-level to low-level: platform (system-wide) -> domain/module ->
   feature -> sub-feature. Each level should be self-contained enough that
   a reader can understand what something does and why it exists without
   drilling deeper. Specifically:

   - The functional-spec.md at each level should fully answer "how does X
     work?" -- covering behavior, requirements, and acceptance scenarios in
     enough detail that a separate low-level technical spec is not needed.
   - The technical-spec.md captures architectural decisions and how the
     feature fits into the system, NOT implementation instructions. Project
     skills handle the detailed how-to.
   - Higher levels (platform, domain) provide context and structure. Lower
     levels (feature, sub-feature) provide specifics. A reader navigates
     top-down to find what they need.

   For each logical feature or change identified, determine the right place
   in this hierarchy. Think in terms of domains and modules first, then
   features within them. Group related changes into coherent features. Each
   feature gets its own folder under `ana-speksi/truth/`.

   The truth directory has three special areas:

   - `ana-speksi/truth/platform/` -- High-level architecture documentation.
     This is the most important part of truth. It tells the story of how
     the system is built at a high level: services, components, technology
     stack, deployment topology, and cross-cutting concerns. Use mermaid
     diagrams for architecture visualization. Update platform/ whenever
     changes affect platform-level architecture -- this is not exclusive
     to `--codebase` mode.
   - `ana-speksi/truth/data-models/` -- Database design documentation per
     domain. Each file describes one domain's tables, relationships,
     constraints, seed data, and business rules. Use
     `resources/data-model-template.md` for the expected structure.
   - `ana-speksi/truth/enums/` -- All enumerations and their descriptions.
     Each file documents one enum: its values, which table/field uses it,
     and any notes. Use `resources/enum-template.md` for the expected
     structure.

   **For `--codebase` (whole codebase documentation):**

   When documenting an entire codebase, FIRST create the
   `ana-speksi/truth/platform/` folder structure to document overall
   architecture. This is the foundation of truth.

   Create subfolders as appropriate for the codebase, such as:
   - `platform/` -- Root for platform-level documentation
     - `architecture.md` -- Overall system architecture with mermaid diagrams
     - `ui/` -- Frontend/UI architecture and patterns
     - `backend/` -- Backend services architecture
     - `async-workers/` -- Background jobs, queues, async processing
     - `ci-cd/` -- Build, deployment, and CI/CD pipelines
     - `infrastructure/` -- Cloud resources, networking, hosting
     - `integrations/` -- Third-party service integrations

   **Mermaid diagrams are strongly encouraged** for visual documentation:
   - System context diagrams (C4 style)
   - Component interaction diagrams
   - Sequence diagrams for key flows
   - Deployment diagrams
   - ER diagrams for data models

   Example architecture.md structure:

   ````markdown
   # Platform Architecture

   ## System Overview

   [Description of the system purpose and scope]

   ## High-Level Architecture

   ```mermaid
   graph TB
       subgraph Frontend
           UI[Web UI]
       end
       subgraph Backend
           API[API Service]
           Workers[Async Workers]
       end
       subgraph Data
           DB[(Database)]
           Queue[Message Queue]
       end
       UI --> API
       API --> DB
       API --> Queue
       Workers --> Queue
       Workers --> DB
   ```

   ## Technology Stack

   [List of technologies with rationale]

   ## Component Interactions

   [Detailed component diagrams]
   ````

   **Enhancing existing platform documentation:**

   When the user asks to enhance or update the overall architecture, revise
   all content under `ana-speksi/truth/platform/` based on current codebase
   state. Compare existing documentation against actual implementation and
   update:
   - Add newly discovered components or services
   - Update diagrams to reflect current architecture
   - Remove documentation for deprecated/removed components
   - Improve diagram clarity and detail level

   Create the following artifacts per feature:

   ### functional-spec.md

   Create using `resources/functional-spec-template.md`. Each functional
   spec must contain:
   - Story definition (As a / I want / So that) -- reconstruct from the code
   - Detailed description of what the feature does
   - Requirements with WHEN/THEN acceptance scenarios -- derive from actual
     behavior in the code, not aspirational
   - Edge cases observed in the implementation
   - UI/UX considerations (if applicable)
   - Constraints

   The WHEN/THEN scenarios must be testable and reflect the real behavior.

   ### technical-spec.md

   Create using `resources/technical-spec-template.md`. Each technical spec
   must contain:
   - Overview of the implementation approach
   - Relevant skills table (from step 2) -- reference skills, do not
     re-document their content
   - Architecture -- how the feature fits into the system
   - Data model references (link to `ana-speksi/truth/data-models/` entries)
   - Key architectural decisions specific to this feature
   - Testing strategy (automated and manual)
   - Security considerations (if applicable)

   Do NOT create `api-contract.md` in truth. API interface details belong
   in code (OpenAPI specs, route definitions, etc.). Summarize relevant
   API architecture in the technical-spec.md Architecture section if needed.

   ### Data models

   If the change involves database tables, create or update a domain file
   in `ana-speksi/truth/data-models/` using `resources/data-model-template.md`.
   Include:
   - Mermaid ER diagram
   - Full table structures with field types and constraints
   - Enumeration definitions
   - Business rules (MUST / MUST NOT language)
   - Relationships

   ### Enums

   If the change introduces or modifies enums, create or update files in
   `ana-speksi/truth/enums/` using `resources/enum-template.md`.

4. **Update truth index**

   Create or update `ana-speksi/truth/index.md` -- a navigable tree of all
   truth content. Use `resources/index-template.md` if the file does not
   yet exist.

   - Add all newly created features to the Features section
   - Add new platform documentation entries
   - Add new data model or enum entries
   - For `--codebase`, this will be a comprehensive index of the entire
     truth hierarchy

5. **Cross-reference**

   Ensure consistency across all created artifacts:
   - Functional specs reference their technical specs
   - Technical specs reference relevant data models
   - Data model entries are referenced from technical specs
   - Enum files are referenced from data model entries
   - All entries are reflected in index.md

6. **Report**

   Show what truth entries were created or updated. Present a summary table:

   | Feature | Artifacts Created | Location |
   | ------- | ----------------- | -------- |
   | [name]  | [list]            | [path]   |

**Guardrails**

- Do NOT modify any code
- Do NOT create api-contract.md in truth
- Technical specs must NOT re-document implementation patterns already covered by project skills
- Always update `ana-speksi/truth/index.md` after creating or modifying truth entries
- Truth follows domain-driven hierarchy: platform -> domain/module -> feature -> sub-feature
- Functional specs must be rich enough to answer "how does X work" without needing low-level technical detail
- Group related changes into coherent features within their domain
- Functional specs must have testable WHEN/THEN scenarios derived from real behavior
- For `--codebase`, always create `platform/` folder with architecture documentation first
- Use mermaid diagrams extensively for visual documentation (architecture, flows, ER diagrams)
- When enhancing architecture, review and update all `platform/` content against current code
- No emojis in any output or files

