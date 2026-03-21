---
name: as-docufy
description: Archive a completed spec and update the ground truth.
---

Archive a completed spec and update the ground truth.

**Input**: The spec name (e.g., `add-user-auth`).

**Steps**

1. **Verify all tasks are complete**

   Run:

   ```
   uv run ana-speksi status --toon
   ```

   Check that ALL tasks across ALL stories are marked as complete (`[x]`).
   If any tasks are incomplete, stop and inform the user:

   > "Cannot proceed with docufy. The following tasks are still incomplete:
   >
   > - [list incomplete tasks]
   >
   > Complete all tasks before archiving."

   Do NOT proceed if any tasks are incomplete.

2. **Check for deferred work (final-verdict.md)**

   Check if `final-verdict.md` exists at the spec root (same directory as `proposal.md`).

   If found:
   - Read the **Summary** section to identify which stories are deferred
   - Read the **Impact** section to understand implications for the current spec
   - Use these decisions to inform which specs are archived vs. kept in truth
   - Deferred stories should NOT be archived yet -- they may be continued in future iterations via `/as-continue`

   If NOT found:
   - Proceed normally -- all completed stories will be archived

   This step aligns with the `/as-final-verdict` skill which documents deferred work and implementation deviations.

3. **Update ground truth**

   **Story selection**: If `/as-continue` specified particular stories to
   process, only update truth for those stories. Otherwise, process all
   stories. The user can run `/as-continue` again to process more stories
   later. The spec is only archived (step 5) when all stories have been
   processed into truth.

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

   The truth directory (`ana-speksi/truth/`) has three special areas:

   - `ana-speksi/truth/platform/` -- High-level architecture documentation.
     This is the most important part of truth. It tells the story of how
     the system is built at a high level: services, components, technology
     stack, deployment topology, and cross-cutting concerns. When the
     completed spec involves platform-level changes (new services,
     infrastructure, cross-cutting patterns), update the relevant platform
     documentation. Use mermaid diagrams for architecture visualization.
   - `ana-speksi/truth/data-models/` -- Database design documentation per
     domain. Each file describes one domain's tables, relationships,
     constraints, seed data, and business rules. Use
     `resources/data-model-template.md` for the expected structure.
   - `ana-speksi/truth/enums/` -- All enumerations and their descriptions.
     Each file documents one enum: its values, which table/field uses it,
     and any notes. Use `resources/enum-template.md` for the expected
     structure.

   Analyze the completed spec and determine the right place in the
   hierarchy. Think in terms of domains and modules first, then features
   within them:
   - Does this belong to an existing domain or module in truth?
   - Is this a new domain/module, or a feature within an existing one?
   - Should this be a sub-feature of an existing feature?
   - Does it introduce or modify data models? Update `truth/data-models/`.
   - Does it introduce or modify enums? Update `truth/enums/`.
   - Does it affect platform-level architecture? Update `truth/platform/`.

   For the identified location in truth, create or update:
   - `functional-spec.md` -- consolidated functional specification. Use
     `resources/functional-spec-template.md` for the expected structure.
     Consolidate the story-level functional specs from the ongoing spec
     into a single feature-level truth spec.
   - `technical-spec.md` -- consolidated technical specification. Use
     `resources/technical-spec-template.md` for the expected structure.
     Consolidate the ongoing spec's technical information but do NOT
     include implementation patterns already covered by project skills.
     Distill into architectural decisions and feature-specific patterns.
     Reference the relevant skills table from the ongoing spec's research
     or technical specs.
   - Sub-folders for sub-features if applicable

   Do NOT create `api-contract.md` in truth. API interface details belong
   in code (OpenAPI specs, route definitions, etc.). If the ongoing spec
   included an api-contract.md, merge any relevant architectural
   information into the technical-spec.md Architecture section.

   **Extensions**: Check each story folder for `extension-*.md` files. These
   document additional functionality discovered and implemented during codify
   that was not in the original spec. Merge extension content into the truth
   alongside the regular specs -- extensions describe real functionality that
   was shipped and must be reflected in the ground truth.

   The truth is a living document that represents the current state of the
   system. Merge the new spec's content into the existing truth structure.

4. **Update truth index**

   Create or update `ana-speksi/truth/index.md` -- a navigable tree of all
   truth content. Use `resources/index-template.md` if the file does not
   yet exist.

   - Add any new features to the Features section
   - Add new platform documentation entries
   - Add new data model or enum entries
   - Remove entries for features that were reorganized or removed
   - Keep descriptions current

5. **Archive the spec**

   Move the spec folder from `ana-speksi/ongoing/<name>/` to
   `ana-speksi/archive/<date>-<name>/` where date is `yyyy-mm-dd` format.

6. **Close GitHub issue (if applicable)**

   Check the spec's folder name for a ticket ID (the numeric prefix in
   `ana-speksi/ongoing/<ticket-id>.<short-name>/`). If a ticket ID exists,
   post a closing comment summarizing the documentation updates and close
   the issue:

   ```
   gh issue close <ticket-id> --comment "<summary>"
   ```

   The comment should summarize what was delivered and what was updated in
   the ground truth:

   > **ana-speksi: spec completed and archived for <spec-name>**
   >
   > **Delivered:**
   > - <2-5 bullet points from the proposal/functional specs>
   >
   > **Documentation updated:**
   > - <list truth paths that were created or updated>
   >
   > **Deferred (if any):**
   > - <list deferred stories from final-verdict.md, or omit section>
   >
   > The branch is ready for merge.

   If the `gh` command fails (e.g., no GitHub remote), log a warning but do
   NOT block the archival workflow.

7. **Report**

   Show what was archived and where truth was updated.

**Guardrails**

- Do NOT modify any code during this phase
- Do NOT create api-contract.md in truth
- Technical specs must NOT re-document implementation patterns already covered by project skills
- Always update `ana-speksi/truth/index.md` after modifying truth
- Truth follows domain-driven hierarchy: platform -> domain/module -> feature -> sub-feature
- Functional specs must be rich enough to answer "how does X work" without needing low-level technical detail
- Archive preserves everything as-is
- No emojis in any output or files

