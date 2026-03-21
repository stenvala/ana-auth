# Tasks: {story_name}

**Parent**: [{spec_name}](../../proposal.md)
**Created**: {date}
**Status**: Draft
**Generated with**: {generated_with}

## Prerequisites

<!-- List any tasks from other stories or shared infrastructure that must be complete first. -->

## Format

- `[P##.T###]` -- Phase and task identifier (e.g., P01.T001)
- `[P]` -- Can be executed in parallel with other [P] tasks in the same phase
- Include exact file paths in descriptions
- Reference the relevant skill for each task
- Only checkbox tasks (`- [ ]`) are tracked for completion and when you implement these, they must be marked as [x]
- Manual verification items are suggestions, not tracked tasks
- **Mandatory to use skills: /skill-name** -- During as-codify, the agent
  MUST invoke each listed skill (`/skill-name`) BEFORE writing any code
  for that task. This is a blocking requirement.

<!-- Following are suggestions of steps and MUST be decided based on what is appropriate for the given feature and nature of the codebase that is supposed to be understood from root level AGENTS.md content as well as those related to lower folders -->

## Phase 1: Setup

- [ ] P01.T001 [Description with file path] **Mandatory to use skills: /skill-name, ...**

## Phase 2: Implementation

<!-- Split into sub-sections as applicable. Omit sections that do not apply to this story. -->

### Database Changes

- [ ] P02.T001 [Description with file path] **Mandatory to use skills: /skill-name, ...**

### Service Changes

- [ ] P02.T002 [Description with file path] **Mandatory to use skills: /skill-name, ...**

### API Changes

- [ ] P02.T003 [Description with file path] **Mandatory to use skills: /skill-name, ...**

### UI Changes

- [ ] P02.T004 [Description with file path] **Mandatory to use skills: /skill-name, ...**

## Phase 3: Test Automation

### Backend Tests

- [ ] P03.T001 [Description with file path] **Mandatory to use skills: /skill-name, ...**

### E2E Tests

- [ ] P03.T002 [Description with file path] **Mandatory to use skills: /skill-name, ...**

## Phase 4: Manual Verification

<!-- These are suggestions for the reviewer, not tracked tasks.
     No checkboxes -- the user performs these at their discretion. -->

### Verification Scenarios

- Verify all acceptance scenarios from functional-spec.md pass
- [scenario description]

### Exploratory Testing Suggestions

- [area to explore and what to look for]
