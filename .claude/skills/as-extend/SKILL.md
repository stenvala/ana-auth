---
name: as-extend
description: Document a critical missing piece discovered during implementation as a story extension.
---

Document a critical missing piece discovered during implementation. Extensions
capture entirely new functionality that was not part of the original story spec --
not iterations or refinements, but new requirements discovered while coding.

**Input**: Description of what is missing. Optionally the story it belongs to.

**Steps**

1. **Identify the spec and story**

   Run:

   ```
   uv run ana-speksi status --toon
   ```

   If there is a single ongoing spec, use it. Otherwise, ask the user to choose.

   If the user did not specify a story, list the stories and ask which one
   the extension belongs to. If only one story exists, use it directly.

2. **Gather the extension details**

   The user describes what is missing. Clarify:
   - What functionality is missing?
   - Why is it critical (cannot ship without it)?
   - What was being implemented when this gap was discovered?

3. **Create the extension document**

   Slugify the extension name (e.g., "error handling" becomes
   `extension-error-handling.md`). The prefix `extension-` is mandatory.

   Create the file at:

   ```
   ana-speksi/ongoing/<name>/specs/<NN-story>/extension-<slug>.md
   ```

   Use the template in `resources/extension-template.md`. Fill in:
   - `**Parent**`: link to the story's functional-spec.md
   - `**Created**`: today's date (yyyy-mm-dd)
   - `**Generated with**`: as-extend
   - Discovery context, description, requirements, and impact

   Requirements must include WHEN/THEN acceptance scenarios, same as
   functional specs. Keep them focused -- this is a lightweight document.

4. **Update index.md**

   Add the extension under the story's section in index.md. Place it after
   the Resources subsection (or after the status-tracked artifacts if no
   Resources subsection exists). Use an "Extensions:" subsection:

   ```
   Extensions:
   - [extension-<slug>.md](specs/<NN-story>/extension-<slug>.md)
   ```

   No status indicator -- extensions are resources. The `[Implemented]`
   marker is added later by as-codify when the extension is implemented.

   If an "Extensions:" subsection already exists for the story, append the
   new entry to it.

5. **STOP and present to user**

   Show the created extension document and the updated index.md entry.
   Remind the user that the extension will be implemented as part of the
   current codify cycle and should be considered when completing the story.

**Guardrails**

- Do NOT modify any code -- this is documentation only
- Extensions must be placed under a specific story, not at the spec root
- The `extension-` filename prefix is mandatory
- Keep the document lightweight -- it supplements the existing spec, not replaces it
- No emojis in any output or files

