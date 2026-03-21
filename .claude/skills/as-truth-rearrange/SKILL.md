---
name: as-truth-rearrange
description: Rearrange the ground truth hierarchy.
---

Rearrange the ground truth hierarchy based on user direction.

**Input**: User's description of how truth should be reorganized.

**Steps**

1. **Read current truth structure**

   Start by reading `ana-speksi/truth/index.md` for an overview, then list
   the current hierarchy under `ana-speksi/truth/`.

2. **Understand the desired structure**

   Ask the user what changes they want:
   - Moving features under other features
   - Splitting features
   - Merging features
   - Renaming

3. **Execute reorganization**

   Move folders and update any internal references (links in markdown files).

4. **Update truth index**

   Update `ana-speksi/truth/index.md` to reflect the new structure.

5. **Report**

   Show the before and after structure.

**Guardrails**

- Do NOT modify any code
- Preserve all content during moves
- Update internal markdown links
- Always update `ana-speksi/truth/index.md` after reorganization
- No emojis in any output or files

