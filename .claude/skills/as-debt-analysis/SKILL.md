---
name: as-debt-analysis
description: Analyze technical debt by comparing code against skills.
---

Analyze technical debt by comparing code against skills or examining a folder.

NO CODE CHANGES ARE ALLOWED during this analysis.

**Input**: One of:

- A folder path to analyze
- A skill name to check alignment against

**Steps**

1. **Determine scope**

   If a folder is given:
   - Analyze all code in that folder
   - Find all relevant skills and check alignment

   If a skill is given:
   - Find all code that should follow that skill
   - Check how well the code aligns with the skill's expectations

2. **Analyze alignment**

   For each relevant skill:
   - Read the skill's instructions and best practices
   - Compare against actual code
   - Identify deviations, missing patterns, outdated approaches

3. **Create debt document**

   Create `ana-speksi/technical-debt/<date>-<area>.md` using the template in
   `resources/debt-analysis-template.md`. Include:
   - Summary of findings
   - Detailed findings with severity, current vs expected state
   - Prioritized action items
   - References to relevant skills

4. **Report**

   Show the findings and suggest next steps:
   - Run `as-new` pointing to this debt document to create a clearing plan

**Guardrails**

- Do NOT modify any code
- Be specific about file paths and line numbers
- Reference skills accurately
- Prioritize findings by impact
- No emojis in any output or files

