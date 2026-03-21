---
name: database-model
description: Create SQLModel Python classes that map to database tables
---

# Database Model Creation

Create SQLModel Python classes that map to database tables.

## When to Use

- Creating Python models after schema is in place
- Adding relationships between existing models
- Creating enum classes for type-safe field values
- Adding JSONB field type definitions

## Prerequisites

1. Data model documentation exists in the data model documentation directory (MANDATORY - see `resources/datamodel-docs-template.md`)
2. Schema exists in the database scripts directory
3. Base infrastructure exists (use `resources/base-infrastructure.md` for fresh projects)

**IMPORTANT**: If documentation doesn't exist, create it first using `resources/datamodel-docs-template.md` before proceeding with model implementation.

## File Locations

- **Models**: The domain models directory, one file per table
- **Enums**: Enum file in the domain models directory
- **JSONB Types**: Types file in the domain models directory

## Instructions

### 1. Create Model File

Create the SQLModel class with proper inheritance and field definitions.

### 2. Create Enums (if needed)

Create enum classes for CHECK constraint fields.

### 3. Create JSONB Types (if needed)

Define Pydantic models for JSONB field contents.

### 4. Verify Import

Verify the model can be imported successfully from the models module.

## Key Rules

1. **Inheritance**: Always `class TableName(SQLModel, BaseDBModelMixin, table=True)`
2. **Table name**: Set `__tablename__` to match schema exactly
3. **ID fields**: `id: str = Field(primary_key=True, default=None)`
4. **Foreign keys**: `Field(foreign_key="table.id", index=True)`
5. **Optional fields**: `Optional[Type] = Field(default=None)`
6. **Timestamps**: `datetime = Field(default_factory=lambda: datetime.now(timezone.utc))`
7. **Enums**: Import from `<domain>_enums.py`
8. **JSONB**: Use `Field(sa_type=JSON)` with type alias

## Templates

See `resources/` folder for:
- `datamodel-docs-template.md` - **MANDATORY**: Data model documentation structure (create docs FIRST)
- `base-infrastructure.md` - **Start here for fresh projects**: BaseDBModelMixin, package structure
- `model-template.md` - Basic model structure
- `enum-template.md` - Enum class patterns
- `jsonb-pattern.md` - JSONB field handling

