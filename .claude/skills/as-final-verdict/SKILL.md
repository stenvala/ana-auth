---
name: as-final-verdict
description: Document final implementation decisions during codify phase. Use this skill to record what work was deferred to future iterations, implementation deviations from the spec, and their impact. Creates final-verdict.md at spec root for as-docufy to reference when archiving specs. Use when you've decided to leave stories/tasks for future work or implemented significant deviations from the original proposal.
---

# As Final Verdict

## Overview

During the codify phase, you may decide that certain stories or work should be deferred to future iterations, or you may make implementation choices that deviate from the original spec. The `/as-final-verdict` skill lets you formally document these decisions in a structured final-verdict.md file that sits at the spec root.

This file serves two purposes:

1. **Record-keeping**: Documents what was left undone and why, creating a clear record for future work
2. **Integration with as-docufy**: When archiving specs, the `as-docufy` skill reads final-verdict.md to make informed decisions about which specs to archive and how

## When to Use

Use `/as-final-verdict` during the codify phase when:

- You've decided to defer remaining stories/work to future iterations (common practice)
- Your implementation significantly deviates from the original proposal
- You want to document the rationale and impact of these decisions

## Workflow

### 1. Identify Deviations

During codify, note what stories/tasks are being deferred or what implementation choices differ from the spec.

### 2. Create/Update final-verdict.md

Use this skill to document the decisions with three required sections:

- **Summary**: Brief overview of what's being deferred and key deviations
- **Why**: Rationale for these decisions (time constraints, technical discovery, priority shifts, etc.)
- **Impact**: What this means for the project, future work, and current deliverables

### 3. Format Reference

See [final-verdict.md](resources/final-verdict.md) for the complete template and format guidelines.

### 4. File Location

The final-verdict.md file is created at the spec root (same location as proposal.md, specs/, and tasks/).

## How as-docufy Uses It

When `as-docufy` runs after this skill is used:

- It will detect final-verdict.md at the spec root
- It will read the deferred stories and deviations documented
- It will factor these decisions into what specs get archived and how the spec tree is updated
- It is optional—if final-verdict.md doesn't exist, as-docufy proceeds normally

## Resources

### resources/

- **final-verdict.md**: Template, format guidelines, and examples for creating the final-verdict.md file

