---
name: as-status
description: Show the current status of an ana-speksi change, including phase and acceptance readiness. Must be run before any phase skill.
---

Show the current status of an ana-speksi change and verify acceptance readiness
before any phase action can proceed.

**CRITICAL GATE**: Every phase skill (as-storify, as-techify, as-taskify,
as-codify, as-continue, as-docufy, as-accept, and any other action skill)
MUST check acceptance status before doing ANY work. If there are ANY files
or statuses that are not in "Accepted" state, the action MUST NOT proceed.
The user must run `/as-accept` first to accept all pending outputs.

This means:

- No phase skill may begin execution while unaccepted artifacts exist
- This applies to ALL actions, not just the next phase in sequence
- The only exception is `/as-accept` itself, which is the remedy
- If a user tries to invoke a phase skill and statuses are not all Accepted,
  refuse and tell them to run `/as-accept` first

**Input**: Optionally the spec name (e.g., `add-user-auth`). If not provided,
auto-detects if there is a single ongoing spec.

**Steps**

1. **Get acceptance status**

   Run:

   ```
   uv run ana-speksi accept --toon
   ```

   (or with a spec name: `uv run ana-speksi accept <name> --toon`)

   The `--toon` flag is a dry-run that does NOT modify any files. It returns:
   - Which spec and phase you are in
   - Which files need to be accepted
   - Which files are already accepted

2. **Get full spec status**

   Run:

   ```
   uv run ana-speksi status --toon
   ```

   (or with `--name <spec-name>` for a specific spec)

   This returns the full status of all ongoing specs, including story-level
   artifact statuses.

3. **Present the status and gate the next action**

   Summarize the information for the user:
   - Spec name and current phase
   - Acceptance readiness: list files that are already accepted and files
     still pending acceptance
   - Per-story artifact status (which functional specs, technical specs,
     tasks exist and their statuses)

   Then check the `files_to_accept` list from step 1:
   - **If `files_to_accept` is NOT empty** (there are pending files):

     Tell the user:

     > "The following files are not yet accepted:
     >
     > - [list files]
     >
     > All statuses must be Accepted before any action can proceed.
     > Run `/as-accept` to accept pending outputs."

     Do NOT suggest running any phase skill. Do NOT offer alternatives.
     STOP here. No action skill (as-taskify, as-codify, as-continue,
     as-storify, as-techify, as-docufy, etc.) may be invoked until
     all statuses are Accepted.

   - **If `files_to_accept` IS empty** (all files accepted):

     Tell the user all statuses are Accepted and which phase action
     is available next (e.g., "All statuses are Accepted. You can run
     `/as-continue` to advance to the next phase.").

**Guardrails**

- Do NOT modify any files
- Do NOT write any code
- Do NOT accept or advance phases -- only report status
- Do NOT invoke any phase skill if there are files pending acceptance
- No emojis in any output or files

