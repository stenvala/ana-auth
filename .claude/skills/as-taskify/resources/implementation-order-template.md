# Implementation Order

**Parent**: [{spec_name}](proposal.md)
**Created**: {date}
**Generated with**: {generated_with}

## Rationale

<!--
Analyze cross-story dependencies to determine the optimal implementation sequence.
The story numbering (01, 02, 03...) reflects the user-facing narrative order, but
implementation may require a different sequence when:
- A later story provides infrastructure needed by earlier stories
- Shared data models or services must exist before dependents
- Permission/security stories gate other functionality
- API contracts from one story are consumed by another
-->

## Implementation Sequence

| Order | Story | Depends On | Rationale |
|-------|-------|------------|-----------|
| 1 | NN-story-name | -- | Foundation: no dependencies |
| 2 | NN-story-name | NN-story-name | Reason this must come after its dependency |

## Dependency Graph

<!--
Show which stories block which others using arrow notation.
Example:
  01-prereqs --> 02-folder-management --> 03-file-upload
                                      --> 04-text-editing
  01-prereqs --> 05-permissions --> 06-protection
  02-folder-management --> 07-audit-trail
-->
