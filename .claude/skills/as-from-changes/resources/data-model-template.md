# {domain_name} Data Model

## Overview

<!-- Brief description of what this domain handles and its purpose in the system.
     2-4 sentences explaining the core entities and their role. -->

## Mermaid Diagram

```mermaid
erDiagram
   {table_1}
   {table_2}

   {table_1} ||--o{{ {table_2} : "relationship_name"

   %% Styling - [DOMAIN_COLOR] for {domain_name} tables
   style {table_1} fill:#HEX_COLOR,stroke:#000,stroke-width:2px,color:#000
   style {table_2} fill:#HEX_COLOR,stroke:#000,stroke-width:1px,color:#000
```

## Table Structure

### {table_name}

| Field | Type | Constraints | Description |
| ----- | ---- | ----------- | ----------- |
| id | STRING | PRIMARY KEY | UUID v4 unique identifier |
| [field_name] | [TYPE] | [CONSTRAINTS] | [Description] |
| [foreign_key]_id | STRING | FOREIGN KEY REFERENCES [table](id), NOT NULL, INDEX | Reference to [related entity] |
| created_at | INTEGER | NOT NULL | Unix epoch timestamp (seconds) |
| updated_at | INTEGER | NOT NULL | Unix epoch timestamp (seconds) |

<!-- Repeat for each table in the domain -->

## Enumeration Definitions

<!-- List all enum values used in CHECK constraints.
     Each enum should also have its own file in ana-speksi/truth/enums/. -->

### [Enum Name] Values

- `VALUE_1` - Description
- `VALUE_2` - Description

## Business Rules

<!-- Use MUST / MUST NOT language. Number every rule. -->

1. **[Rule Name]**: [Rule description]
2. **[Rule Name]**: [Rule description]

## Relationships

<!-- Document all foreign keys and back-references. -->

- **[field_name]** -> [target_table].[target_field]: [Cardinality description]
- **[table]** <- [source_table].[field]: Referenced by [description]

## Security Considerations

<!-- Access control, data protection, audit requirements. -->

1. **[Aspect]**: [Description]

## Data Schemas

<!-- Document JSONB / JSON fields with example payloads. -->

### [Field Name] Schema ([table].[field] JSONB)

<!-- Description of the structure and purpose. -->

```json
{{}}
```

## Seed Data

<!-- If this domain requires initial data, document it here. -->

### [Table Name]

| field_1 | field_2 | field_3 |
| ------- | ------- | ------- |
| value | value | value |
