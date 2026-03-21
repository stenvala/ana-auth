# Data Model Documentation Template

This template defines the MANDATORY structure for all data model documentation files in `docs/datamodels/<domain>.md`.

## Template Structure

```markdown
# [Domain Name] Data Model

## Overview

[Brief description of what this domain handles and its purpose in the system. 2-4 sentences explaining the core entities and their role.]

## Mermaid Diagram

\`\`\`mermaid
erDiagram
   [table_1]
   [table_2]
   [table_3]
   [external_table_from_other_domain]

   [table_1] ||--o{ [table_2] : "relationship_name"
   [table_1] }o--|| [external_table] : "relationship_name"
   [table_2] ||--o{ [table_3] : "relationship_name"

   %% Styling - [DOMAIN_COLOR] for [domain] tables
   style [table_1] fill:#[HEX_COLOR],stroke:#000,stroke-width:1px,color:#000
   style [table_2] fill:#[HEX_COLOR],stroke:#000,stroke-width:1px,color:#000
   style [table_3] fill:#[HEX_COLOR],stroke:#000,stroke-width:1px,color:#000
   %% Other domain tables (use their respective colors)
   style [external_table] fill:#[OTHER_DOMAIN_COLOR],stroke:#000,stroke-width:1px,color:#000
\`\`\`

## Table Structure

### [table_name]

| Field              | Type      | Constraints                                       | Description                              |
| ------------------ | --------- | ------------------------------------------------- | ---------------------------------------- |
| id                 | STRING    | PRIMARY KEY                                       | Unique identifier for the [entity]       |
| [field_name]       | [TYPE]    | [CONSTRAINTS]                                     | [Description of the field]               |
| [foreign_key]_id   | STRING    | FOREIGN KEY REFERENCES [table](id), [NULL/NOT NULL] | Reference to [related entity]          |
| created_at         | TIMESTAMP | NOT NULL, DEFAULT NOW()                           | When the record was created              |
| updated_at         | TIMESTAMP | NOT NULL, DEFAULT NOW()                           | When the record was last updated         |

[Repeat for each table in the domain]

## Enumeration definitions

### [Enum Name] Values

- `VALUE_1` - Description of what this value represents
- `VALUE_2` - Description of what this value represents
- `VALUE_3` - Description of what this value represents

[Repeat for each enum in the domain]

## Business Rules

1. **[Rule Name]**: [Rule description - what MUST or MUST NOT happen]
2. **[Rule Name]**: [Rule description]
3. **[Rule Name]**: [Rule description]
[Continue numbering all business rules]

## Relationships

- **[field_name]** -> [target_table].[target_field]: [Cardinality description]
- **[table]** <- [source_table].[field]: Referenced by [description]

## Security Considerations

1. **[Security Aspect]**: [Description of access control or data protection requirement]
2. **[Security Aspect]**: [Description]

## Data Schemas

### [JSONB Field Name] Schema ([field_name] JSONB)

[Description of the JSONB structure and its purpose]

\`\`\`json
{
  "field_key": "example_value",
  "nested_object": {
    "sub_field": "value"
  }
}
\`\`\`

[Repeat for each JSONB field that needs schema documentation]
```

## Domain Color Palette

Each domain MUST have a unique color for ERD diagrams. Use these predefined colors:

| Domain          | Color Code | Preview     |
| --------------- | ---------- | ----------- |
| user/auth       | `#1E90FF`  | Blue        |
| group/org       | `#32CD32`  | Green       |
| audit           | `#FFD700`  | Gold        |
| documents       | `#9370DB`  | Purple      |
| transactions    | `#FF6347`  | Tomato      |
| accounts        | `#20B2AA`  | Teal        |
| invoices        | `#FF69B4`  | Pink        |
| reports         | `#87CEEB`  | Sky Blue    |
| settings        | `#DDA0DD`  | Plum        |
| events          | `#FF6B35`  | Orange      |
| results         | `#DC143C`  | Crimson     |
| [new domain]    | [pick unique] | [describe] |

**Rules**:
- Each domain MUST use a distinct color
- Domain tables use the same color within a diagram
- External/referenced tables from other domains use their own domain color
- Text color should be `#000` (black) for light backgrounds, `#FFF` (white) for dark backgrounds (e.g., crimson)

## Field Type Conventions

| SQL Type          | Documentation Type | Notes                           |
| ----------------- | ------------------ | ------------------------------- |
| TEXT              | STRING             | Variable-length text            |
| VARCHAR(n)        | STRING             | Note max length in constraints  |
| INTEGER           | INTEGER            |                                 |
| BIGINT            | BIGINT             |                                 |
| BOOLEAN           | BOOLEAN            |                                 |
| TIMESTAMP         | TIMESTAMP          | Always with timezone            |
| DATE              | DATE               |                                 |
| TIME              | TIME               |                                 |
| DECIMAL(p,s)      | DECIMAL(p,s)       | Include precision and scale     |
| JSON/JSONB        | JSONB              | Always document schema below    |

## Constraint Conventions

| Constraint Type   | Format                                    |
| ----------------- | ----------------------------------------- |
| Primary Key       | `PRIMARY KEY`                             |
| Foreign Key       | `FOREIGN KEY REFERENCES table(id)`        |
| Not Null          | `NOT NULL`                                |
| Nullable          | `NULL`                                    |
| Default Value     | `DEFAULT [value]`                         |
| Default Now       | `DEFAULT NOW()`                           |
| Index             | `INDEX`                                   |
| Unique            | `UNIQUE`                                  |
| Check             | `CHECK([condition])`                      |

Multiple constraints are comma-separated: `NOT NULL, DEFAULT 'value', INDEX`

## Relationship Notation

Use standard ERD notation:
- `||--||` : One to one
- `||--o{` : One to many
- `}o--||` : Many to one
- `}o--o{` : Many to many
- `}o--o|` : Many to zero-or-one

## Example: Complete Domain Documentation

See the Event Data Model example provided in the constitution command for a complete reference implementation.

## Validation Checklist

Before finalizing documentation, verify:

- [ ] Overview clearly explains domain purpose
- [ ] Mermaid diagram renders correctly
- [ ] All tables documented with complete field list
- [ ] Domain color is unique and consistent
- [ ] All foreign keys documented with REFERENCES clause
- [ ] All enums have complete value lists with descriptions
- [ ] Business rules are numbered and use MUST/MUST NOT language
- [ ] Relationships section covers all FKs and back-references
- [ ] Security considerations address access control
- [ ] JSONB fields have schema documentation with examples
- [ ] created_at and updated_at present on all tables
