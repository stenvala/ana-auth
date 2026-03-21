---
name: as-taskify
description: Create implementation tasks for each user story.
---

Create implementation tasks for each user story.

**Input**: The spec name (e.g., `add-user-auth`).

**Steps**

1. **Check acceptance gate**

   Run:

   ```
   uv run ana-speksi accept --toon
   ```

   If `files_to_accept` is NOT empty, stop and inform the user:

   > "Cannot proceed with taskify. The following files need acceptance:
   >
   > - [list files from files_to_accept]
   >
   > Run `/as-accept` to accept them first."

   Do NOT proceed if the gate is not satisfied.

2. **Read all specs**

   Read proposal.md, research.md, and all functional-spec.md and
   technical-spec.md files.

3. **Create implementation-order.md**

   Before creating individual task files, analyze all stories and their
   cross-dependencies to determine the correct implementation sequence.
   The story numbering (01, 02, 03...) reflects the user-facing narrative
   order, but implementation may require a different sequence (e.g., a
   permissions story may need to be implemented before a feature that
   depends on it).

   Create `implementation-order.md` in the spec root
   (`ana-speksi/ongoing/<name>/implementation-order.md`) using the template
   in `resources/implementation-order-template.md`.

   The file must contain:
   - `**Generated with**: as-taskify` in the header
   - An ordered table listing each story in implementation sequence
   - A "Depends On" column showing which stories must be completed first
   - A "Rationale" column explaining why this position in the sequence
   - A dependency graph showing blocking relationships

   Analyze dependencies by examining:
   - Data model dependencies (which tables/entities must exist first)
   - API dependencies (which endpoints are consumed by other stories)
   - UI dependencies (which components or pages are prerequisites)
   - Permission/security gates (what must be in place before features)

4. **Create tasks.md for each story**

   **Story selection**: If `/as-continue` specified particular stories to
   process, only create tasks for those stories. Otherwise, process all
   stories that do not yet have a `tasks.md`.

   For each story in `ana-speksi/ongoing/<name>/specs/<NN-story>/`, create
   `tasks.md` using the template in `resources/tasks-template.md`.

   Each tasks.md must have:
   - `**Status**: Draft` in the header
   - `**Generated with**: as-taskify` in the header

   Each tasks.md is organized into phases with sub-sections:
   - **Phase 1: Setup** -- scaffolding, configuration, migrations
   - **Phase 2: Implementation** -- split into sub-sections as applicable:
     Database Changes, Service Changes, API Changes, UI Changes.
     Omit sub-sections that do not apply.
   - **Phase 3: Test Automation** -- Backend Tests, E2E Tests
   - **Phase 4: Manual Verification** -- suggestions only, NO checkboxes.
     Include verification scenarios and exploratory testing suggestions.
     The user performs these at their discretion.

   Task IDs use the format `P##.T###` (e.g., P01.T001, P02.T003).
   Tasks within a phase are numbered sequentially. Use `[P]` to mark
   tasks that can run in parallel within the same phase.

   Each tasks.md must also contain:
   - Prerequisites (dependencies on other stories or shared tasks)
   - Exact file paths in every task description
   - A referenced skill for each task

   Tasks must be:
   - Specific enough for an AI agent to implement
   - Include exact file paths where changes go
   - Reference the skill that guides the implementation via the
     `**Mandatory to use skills: /skill-name**` annotation. This is NOT
     decorative text -- during as-codify, the agent MUST invoke each
     listed skill (`/skill-name`) before writing any code for that task.
     Choose skills carefully: each one will be loaded into context and
     its rules enforced.
   - Independently verifiable

5. **Update index.md**

   Update index.md immediately after creating implementation-order.md and
   each story's tasks.md:
   - Add `[implementation-order.md](implementation-order.md)` to the
     Artifacts section (no status indicator -- it is a resource)
   - Change `[]` to `[Draft]` for each story's tasks.md
   - Add a placeholder `(0/0 tasks complete)` after each tasks.md entry
   - Ensure each story keeps `**Implementation**: Not Started`
   - Update the phase progress table

   Then run the following command to sync the correct task counts from
   the actual tasks.md files (do NOT count tasks manually):

   ```
   uv run ana-speksi sync-counts
   ```

6. **STOP and present to user**

   Show the implementation order and task lists for review.

**Guardrails**

- Do NOT write any code
- Every task must reference a skill
- Tasks must include file paths
- Tasks should be small and focused (completable in one step)
- No emojis in any output or files

