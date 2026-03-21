---
name: as-one-shot
description: Execute the entire ana-speksi workflow without stopping between phases.
---

Execute the entire ana-speksi workflow from proposal through implementation
without stopping between phases.

**Input**: The user's description of what they want to build or change.

**Steps**

1. Execute as-new (proposal)
   - After creating proposal.md, set `**Status**: Accepted` (auto-accept)
   - Set `**Generated with**: one-shot` in the header

2. Execute as-storify (functional specs)
   - After creating each functional-spec.md, set `**Status**: Accepted` (auto-accept)
   - Set `**Generated with**: one-shot` in each functional-spec.md and index.md

3. Execute as-techify (research + technical specs)
   - After creating each technical-spec.md, set `**Status**: Accepted` (auto-accept)
   - Set `**Generated with**: one-shot` in each technical-spec.md

4. Execute as-taskify (task creation)
   - After creating each tasks.md, set `**Status**: Accepted` (auto-accept)
   - Set `**Generated with**: one-shot` in each tasks.md

5. Execute as-codify (implementation)
   - Regardless of project configuration, treat `auto_story_implementation_continue`
     as `true`. Do NOT prompt the user for whether to continue after each story
     is implemented — automatically proceed to the next story.

6. **STOP. Do NOT execute as-docufy.** After codify completes, you MUST
   stop and wait for the user to verify the implementation. Do not proceed
   to as-docufy or any further phase without explicit user approval.

Follow each phase's skill instructions in sequence. Do not stop between
phases unless an error occurs that requires user intervention.
After step 5 (codify), always stop and require user verification before
proceeding.

**Auto-acceptance**: In one-shot mode, all acceptance gates are bypassed
because every document is immediately set to Accepted after creation.
This means no `/as-accept` calls are needed.

**Generated with**: All key documents (proposal.md, functional-spec.md,
technical-spec.md, tasks.md, index.md) must have `**Generated with**: one-shot`
in their headers.

**Index format**: Only four artifact types carry status indicators in
index.md: proposal.md, functional-spec.md, technical-spec.md, tasks.md.
Use `[Accepted]` for these (since they are auto-accepted). All other
files are resources listed without status indicators. Do NOT use checkboxes.

**Extensions**: If during codify you discover critical missing functionality
that is not an iteration of existing tasks but entirely new, create an
extension document using `/as-extend`. In one-shot mode, set
`**Generated with**: one-shot` in the extension and immediately mark it
as `[Implemented]` in index.md after implementing it.

**Guardrails**

- Code changes only during the codify phase
- Each phase must complete fully before the next begins
- If any phase produces results that seem wrong, pause and ask the user
- No emojis in any output or files

