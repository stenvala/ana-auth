# Data Model Changes: {spec_name}

**Created**: {date}
**Target Domain(s)**: <!-- e.g., accounting, auth -->

## Summary of Changes

<!-- Brief overview of what data model changes this spec introduces. -->

## Affected Domains

<!-- List each domain that is modified or created. -->

---

## {domain_name} Domain

<!-- Repeat this entire section for each affected domain.
     Structure matches ana-speksi/truth/data-models/<domain>.md exactly
     so the content can be merged directly during the docufy phase. -->

### Overview

<!-- If this is a new domain, provide the full overview.
     If modifying an existing domain, describe only the delta. -->

### Mermaid Diagram

<!-- For new domains: full ER diagram.
     For existing domains: diagram showing new/changed tables and their
     relationships to existing tables. -->

```mermaid
erDiagram
   [new_table]
   [existing_table]

   [existing_table] ||--o{ [new_table] : "relationship"

   %% Styling
   style [new_table] fill:#HEX_COLOR,stroke:#000,stroke-width:2px,color:#000
   style [existing_table] fill:#HEX_COLOR,stroke:#000,stroke-width:1px,color:#000
```

### New Tables

<!-- Full table definitions for tables being added. -->

#### [table_name]

| Field | Type | Constraints | Description |
| ----- | ---- | ----------- | ----------- |
| id | STRING | PRIMARY KEY | UUID v4 unique identifier |
| [field_name] | [TYPE] | [CONSTRAINTS] | [Description] |
| created_at | INTEGER | NOT NULL | Unix epoch timestamp (seconds) |
| updated_at | INTEGER | NOT NULL | Unix epoch timestamp (seconds) |

### Modified Tables

<!-- Only the changed/added fields for existing tables. -->

#### [existing_table_name]

**Changes**:

| Field | Type | Constraints | Description | Change |
| ----- | ---- | ----------- | ----------- | ------ |
| [field] | [TYPE] | [CONSTRAINTS] | [Description] | ADDED / MODIFIED / REMOVED |

### Enumeration Definitions

<!-- New or modified enums. Each should also become a file in truth/enums/. -->

#### [Enum Name] Values

- `VALUE_1` - Description
- `VALUE_2` - Description

### Business Rules

<!-- New business rules introduced by this change. Use MUST / MUST NOT. -->

1. **[Rule Name]**: [Rule description]

### Relationships

<!-- New or modified relationships. -->

- **[field_name]** -> [target_table].[target_field]: [Cardinality]

### Migration Notes

<!-- SQL changes needed. Reference the create_schema.sql conventions. -->

```sql
-- New tables
-- ALTER TABLE statements for modifications
```

---

## Merge Instructions

<!-- Notes for the docufy phase on how to merge these changes into
     the existing truth/data-models/ files. -->

- [ ] Merge into `ana-speksi/truth/data-models/{domain}.md`
- [ ] Create/update enum files in `ana-speksi/truth/enums/`
- [ ] Update Mermaid diagrams in affected domain files
