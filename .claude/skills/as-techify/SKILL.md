---
name: as-techify
description: Conduct technical research and create technical specifications.
---

Conduct technical research and create technical specifications for each story.

**Input**: The spec name (e.g., `add-user-auth`).

**Steps**

1. **Check acceptance gate**

   Run:

   ```
   uv run ana-speksi accept --toon
   ```

   If `files_to_accept` is NOT empty, stop and inform the user:

   > "Cannot proceed with techify. The following files need acceptance:
   >
   > - [list files from files_to_accept]
   >
   > Run `/as-accept` to accept them first."

   Do NOT proceed if the gate is not satisfied.

2. **Read all functional specs**

   Read `ana-speksi/ongoing/<name>/proposal.md` and all `functional-spec.md` files.

3. **Identify relevant skills**

   Search the repository for development skills (look in `.claude/skills/`,
   `.cursor/skills/`, `.github/skills/`). List all skills relevant
   to fulfilling the functional requirements.

4. **Create research.md**

   At `ana-speksi/ongoing/<name>/research.md`, document:
   - Relevant documentation under `ana-speksi/truth` -- start with `ana-speksi/truth/index.md` for a map of existing documentation, then explore relevant areas. Note that truth is recursive so identify the areas; if there are no areas, let user know that too so user can steer you if you didn't find anything
   - Codebase analysis findings
   - Existing patterns and integration points
   - External research (libraries, APIs, best practices, known solutions with code snippets)
   - Relevant skills table
   - Technical constraints discovered
   - Key decisions and rationale
   - Risks identified

   Use the template in `resources/research-template.md`.
   Look at the solution holistically across all stories.

5. **Create technical-spec.md for each story**

   **Story selection**: If `/as-continue` specified particular stories to
   process, only create artifacts for those stories. Otherwise, process all
   stories that do not yet have a `technical-spec.md`.

   For each story in `ana-speksi/ongoing/<name>/specs/<NN-story>/`, create:
   - `technical-spec.md` -- implementation approach, architecture, relevant skills.
     Must have `**Status**: Draft` and `**Generated with**: as-techify` in the header.
   - `api-contract.md` -- if the story involves API changes
   - `test-automation-plan.md` -- automated testing plan
   - `manual-testing-plan.md` -- manual testing scenarios

   Only create the optional files if they are relevant to the story.
   Templates are available in this skill's `resources/` directory.

6. **Create data model change documents**

   Analyze whether any story requires new persistent data (new entities,
   new database tables, new fields) or modifies existing data structures.
   This includes any feature that stores, retrieves, or manages data --
   even if the functional spec does not explicitly mention "database" or
   "table". If in doubt, create the document.

   Create `data-model.md` at `ana-speksi/ongoing/<name>/data-model.md`
   (one per spec, not per story). This document must use the **same
   structure** as `ana-speksi/truth/data-models/<domain>.md` so it can be
   directly merged during the docufy phase.

   Use the template in `resources/data-model-change-template.md`. Include:
   - Overview of what changes and why
   - Mermaid ER diagram showing new/modified tables
   - Full table structures for new tables
   - Delta table structures for modified tables (show changed/added fields)
   - New enum definitions (if any)
   - New business rules
   - New relationships
   - Migration notes (what SQL changes are needed)

   Reference existing data models in `ana-speksi/truth/data-models/` and
   `docs/datamodels/` to maintain consistency with established conventions.

7. **Update index.md**

   Update index.md immediately after each artifact is created.

   Only `technical-spec.md` gets a status indicator -- change `[]` to `[Draft]`.
   Resource files (research.md, data-model.md, api-contract.md,
   test-automation-plan.md, manual-testing-plan.md) are listed without status
   indicators. Just add them to the index when created (no `[]` prefix).

   Update the phase progress table.

8. **STOP and present to user**

   Show the research and technical specs for review.

**Guardrails**

- Do NOT write any code
- Do NOT create task lists yet
- Research must be thorough -- read the codebase, check skills
- Technical specs must reference relevant skills
- Data model changes must follow the truth/data-models/ structure exactly
- No emojis in any output or files

