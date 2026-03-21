---
name: as-accept
description: Mark the current phase's outputs as Accepted. Run before advancing to the next phase.
---

Mark the current phase's outputs as Accepted so the workflow can advance.

**Input**: Optionally the spec name (e.g., `add-user-auth`). If not provided,
auto-detects if there is a single ongoing spec.

**Steps**

1. **Preview what will be accepted**

   Run:

   ```
   uv run ana-speksi accept --toon
   ```

   (or with a spec name: `uv run ana-speksi accept <name> --toon`)

   The output tells you:
   - Which spec and phase you are in
   - Which files need to be accepted
   - Which files are already accepted
   - Whether `auto_confirm` is enabled (from `ana-speksi/config.yml`)

2. **Confirmation or notification**

   Check the `auto_confirm` field from step 1.

   **If `auto_confirm` is `false` (default)**:

   Ask the user:

   > "The following files will be marked as Accepted:
   >
   > - [list files]
   >
   > Do you want to accept all of these?"

   **If `auto_confirm` is `true`**:

   Do NOT ask for confirmation. Instead, notify the user:

   > "auto_confirm is enabled. Accepting the following files:
   >
   > - [list files]"

   Then proceed directly to step 3.

3. **Apply acceptance**

   Run:

   ```
   uv run ana-speksi accept
   ```

   (or with a spec name: `uv run ana-speksi accept <name>`)

   The command will:
   - Update `**Status**: Draft` to `**Status**: Accepted` in each file
   - Update `[Draft]` to `[Accepted]` in index.md

4. **Stage ana-speksi files and commit (mandatory)**

   After acceptance, stage all files under the `ana-speksi/` directory and commit:

   ```
   git add ana-speksi/
   ```

   Then commit with a descriptive message. Use `/commit` or create the commit
   directly with a message like:

   > `ana-speksi: accept <phase> phase for <spec-name>`

   **If `auto_confirm` is `true`**: do NOT ask the user whether to commit.
   Just stage, commit, and notify them of the commit.

   **If `auto_confirm` is `false`**: ask the user to confirm the commit
   before running it.

5. **Comment on GitHub issue (if applicable)**

   Check the spec's folder name for a ticket ID (the numeric prefix in
   `ana-speksi/ongoing/<ticket-id>.<short-name>/`). If a ticket ID exists,
   post a summary comment to the corresponding GitHub issue:

   ```
   gh issue comment <ticket-id> --body "<summary>"
   ```

   The summary should describe what was completed in the accepted phase,
   based on the ana-speksi artifacts:

   | Phase    | Summary based on                                  |
   | -------- | ------------------------------------------------- |
   | proposal | Key points from proposal.md                       |
   | storify  | List of user stories from functional-spec.md files |
   | techify  | Key technical decisions from technical-spec.md     |
   | taskify  | Task breakdown from tasks.md files                 |
   | codify   | Implementation summary from the codify artifacts   |

   Format the comment as:

   > **ana-speksi: <phase> phase accepted for <spec-name>**
   >
   > <2-5 bullet points summarizing the phase outputs>

   If the `gh` command fails (e.g., no GitHub remote), log a warning but do
   NOT block the acceptance workflow.

**Acceptance Gates**

The following gates must be passed before advancing phases:

| Phase    | Must Accept                  |
| -------- | ---------------------------- |
| proposal | proposal.md                  |
| storify  | all functional-spec.md files |
| techify  | all technical-spec.md files  |
| taskify  | all tasks.md files           |

If any required file is not Accepted, `as-continue` will block the transition
and direct the user to run `as-accept` first.

**Guardrails**

- Do NOT modify any content other than the Status field
- Do NOT write any code
- Always present the list of files being accepted (even in auto_confirm mode)
- No emojis in any output or files

