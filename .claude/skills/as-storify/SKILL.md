---
name: as-storify
description: Create functional specifications for each user story from the proposal.
---

Create functional specifications for each user story from the proposal.

**Input**: The spec name (e.g., `add-user-auth`).

**Steps**

1. **Check acceptance gate**

   Run:

   ```
   uv run ana-speksi accept --toon
   ```

   If `files_to_accept` is NOT empty, stop and inform the user:

   > "Cannot proceed with storify. The following files need acceptance:
   >
   > - [list files from files_to_accept]
   >
   > Run `/as-accept` to accept them first."

   Do NOT proceed if the gate is not satisfied.

2. **Read the proposal**

   Read `ana-speksi/ongoing/<name>/proposal.md` to extract user stories.

3. **Create the specs directory structure**

   For each user story, create a folder:

   ```
   ana-speksi/ongoing/<name>/specs/<NN-story-name>/
   ```

   Where NN is zero-padded order (01, 02, 03...).

4. **Create functional-spec.md for each story**

   Run:

   ```
   uv run ana-speksi status --toon
   ```

   to confirm current state. For each story, create `functional-spec.md`
   using the template in this skill's `resources/functional-spec-template.md`.

   Each functional spec must have:
   - `**Status**: Draft` in the header
   - `**Generated with**: as-storify` in the header
   - Story definition (As a / I want / So that)
   - Detailed description expanding on the proposal
   - Requirements with WHEN/THEN acceptance scenarios
   - Edge cases
   - UI/UX considerations (if applicable)
   - Constraints

5. **Create index.md**

   Create `ana-speksi/ongoing/<name>/index.md` using the template in
   `resources/index-template.md`. Set `**Generated with**: as-storify` in the header.

   Extract the ticket ID from the spec folder name (format: `TICKET-123.slug`)
   and set `**Ticket ID**: TICKET-123` in the header.

   Each story section includes `**Ticket ID**:` (initially empty) which can
   be populated when creating story-level tickets in your ticket management system.

   Only four artifact types carry status indicators (NOT checkboxes):
   `proposal.md`, `functional-spec.md`, `technical-spec.md`, `tasks.md`.
   All other files (research.md, data-model.md, api-contract.md, etc.)
   are resources -- they are listed without status indicators and are
   implicitly covered when the related spec is accepted.

   Status indicators: `[]` = not created, `[Draft]` = created,
   `[Accepted]` = reviewed and accepted.

   At this point:
   - `[Accepted]` -- proposal.md (already accepted before storify)
   - `[Draft]` -- functional-spec.md (just created)
   - `[]` -- technical-spec.md, tasks.md (not yet created)

   Each story section must include:
   - `**Ticket ID**:` (empty, populated when creating story-level tickets)
   - `**Implementation**: Not Started`

   The Implementation line tracks per-story implementation progress and is
   updated during codify (`In Progress`, `Complete`).

   Example:

   ```
   - [Accepted] [proposal.md](proposal.md)
   - [research.md](research.md)
   ```

   **index.md is the single source of truth for progress.** Every subsequent
   phase must update it immediately when artifacts are created or completed.
   When a document's Status changes, update the corresponding index entry.

6. **STOP and present to user**

   Show the created functional specs and ask for review.

**Guardrails**

- Do NOT create technical specs yet
- Do NOT write any code
- Focus on WHAT, not HOW
- Each functional spec must have testable WHEN/THEN scenarios
- No emojis in any output or files

