---
name: as-codify
description: Implement code changes based on the task lists. THIS IS THE ONLY PHASE WHERE CODE CHANGES ARE ALLOWED.
---

Implement code changes based on the task lists.

THIS IS THE ONLY PHASE WHERE CODE CHANGES ARE ALLOWED.

**Input**: The spec name (e.g., `add-user-auth`).

**Steps**

1. **Check acceptance gate**

   Run:

   ```
   uv run ana-speksi accept --toon
   ```

   If `files_to_accept` is NOT empty, stop and inform the user:

   > "Cannot proceed with codify. The following files need acceptance:
   >
   > - [list files from files_to_accept]
   >
   > Run `/as-accept` to accept them first."

   Do NOT proceed if the gate is not satisfied.

   Then run:

   ```
   uv run ana-speksi status --toon
   ```

   Identify the spec. List all stories and their tasks.

2. **Read context**

   Read:
   - proposal.md for overall context
   - research.md for technical decisions
   - data-model.md for data model changes (if exists)
   - implementation-order.md for the story implementation sequence
   - Any `extension-*.md` files in the current story's folder (these
     document additional functionality discovered during implementation
     that must also be implemented)

3. **Select the next story (MUST follow implementation-order.md)**

   CRITICAL: Stories MUST be processed in the exact order defined in
   `implementation-order.md`. Do NOT use folder order (01, 02, 03...) --
   folder numbering is narrative order, NOT implementation order.
   Dependencies between stories mean implementing out of order will fail.

   Read `implementation-order.md` and follow its sequence table. If
   `implementation-order.md` does not exist, fall back to folder order.

   **Story selection**: If `/as-continue` specified particular stories to
   process, only implement tasks for those stories. Otherwise, pick the
   FIRST story (in implementation-order.md sequence) that still has
   incomplete tasks. Process ONE story per invocation.

   For the selected story:

   a. Read the story's functional-spec.md, technical-spec.md, and tasks.md
   b. Execute tasks in phase order (Phase 1, then Phase 2, etc.).
   Within each phase, execute tasks in order (P01.T001, P01.T002, ...).
   Tasks marked `[P]` may be executed in parallel within the same phase.
   c. For each checkbox task, follow this EXACT sequence:

   i. **Invoke every skill** listed in the task's
   `**Mandatory to use skills: /...**` annotation. Use the Skill tool
   (i.e., `/skill-name`) for EACH referenced skill BEFORE writing
   any code. This loads the skill's patterns, rules, file location
   conventions, and templates into context.
   THIS IS A BLOCKING REQUIREMENT. Do NOT implement any task
   without first invoking its listed skills.
   ii. Implement the task following the loaded skill instructions.
   iii. Mark the task as complete in tasks.md: `- [x]`
   iv. **Update index.md** immediately to reflect current progress:
   run `uv run ana-speksi sync-counts` to update the task count
   (do NOT count tasks manually) and set the story's
   `**Implementation**` line to `In Progress`

   d. **Phase 4: Manual Verification** contains suggestions only (no
   checkboxes). Do NOT execute these -- they are for the user to
   perform at their discretion. Skip this phase during codify.
   e. After completing ALL checkbox tasks for the story, implement any
   `extension-*.md` requirements for the story. For each extension:
   - Read the extension document
   - Implement the requirements and acceptance scenarios
   - Update index.md: add `[Implemented]` before the extension link
     (e.g., `- [Implemented] [extension-foo.md](...)`)
     f. Verify all acceptance scenarios from functional-spec.md AND all
     extension documents are satisfied
     g. **Update index.md** to mark the story as complete: set the
     story's `**Implementation**` line to `Complete`

4. **After the story is complete**

   After finishing all tasks in the current story, present a summary to
   the user:
   - Which story was completed
   - How many tasks were executed
   - Which stories remain (with their task counts)
   - Any issues or deviations noted during implementation

   Check `auto_story_implementation_continue` in `ana-speksi/config.yml`.

   **If `auto_story_implementation_continue` is `false` (default)**: STOP
   and wait for the user. The user runs `/as-continue` to process the
   next story in a fresh context. This prevents context window overflow
   on large specs.

   **If `auto_story_implementation_continue` is `true`**: automatically
   continue to the next story in the implementation-order.md sequence
   without waiting for user confirmation. Repeat from step 3 for the
   next story that has incomplete tasks.

   The codify phase is complete only when every task across all stories
   is marked `[x]`. After the last story, update index.md with:
   - All story `**Implementation**` lines set to `Complete`
   - Codify phase marked as complete

**Guardrails**

- CRITICAL: Before implementing ANY task, invoke every skill listed in
  its `**Mandatory to use skills: /...**` annotation using the Skill tool.
  Never skip this step. The skills contain file location rules, naming
  conventions, templates, and patterns that MUST be followed. Implementing
  without invoking the skill produces incorrect code structure.
- Execute tasks in phase order within each story (Phase 1 before Phase 2, etc.)
- CRITICAL: Process stories in the EXACT order defined by implementation-order.md.
  NEVER use folder order (01, 02, 03...) -- it reflects narrative, not dependencies.
- Unless `auto_story_implementation_continue` is `true`, process ONE story per invocation to avoid context overflow, then STOP
- Mark tasks complete as you go -- never batch
- Update index.md after every task completion
- If a task reveals issues in the spec, note them but continue
- Run linting and tests as appropriate
- No emojis in any output or files

