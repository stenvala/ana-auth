---
name: database-design
description: Create data model documentation with ERD diagrams and business rules
---

# Database Design

Create data model documentation with ERD diagrams, table structures, enumerations, and business rules.

## When to Use

- Starting a new feature that needs database tables
- Designing relationships between entities
- Adding new tables to existing domains
- Documenting data model decisions

## File Location

Create design files at: `docs/datamodels/<domain>.md`

Each domain groups related tables (e.g., `event.md` for event, event_category, event_signup).

## Instructions

### 1. Create Domain File Structure

Every domain documentation includes:

1. **Overview** - Brief description of the domain
2. **Mermaid ERD Diagram** - Visual table relationships
3. **Table Structures** - Detailed field definitions
4. **Enumerations** - String enum values with descriptions
5. **Business Rules** - Constraints and validation rules
6. **Relationships** - Foreign key documentation
7. **Indices** - Query optimization indexes

### 2. Update Master Reference

After creating/updating a domain, update `docs/datamodels/all_tables.md`:
- Add table entries
- Assign domain color for ERD diagrams

## Template

**IMPORTANT**: Use the MANDATORY documentation template from database-model skill:
`.claude/skills/database-model/resources/datamodel-docs-template.md`

This template defines the exact structure that ALL data model documentation MUST follow:
- Domain-specific colors for ERD diagrams (each domain MUST have unique color)
- Table structure with Type, Constraints, Description columns
- Complete enumeration definitions
- Numbered business rules
- Relationship documentation
- Security considerations
- JSONB schema documentation

Also see `resources/domain-template.md` for additional guidance.

## Verification

After design is complete:
1. Review ERD for correct relationships
2. Verify all fields have types and constraints
3. Ensure enums have clear descriptions
4. Confirm business rules are documented

