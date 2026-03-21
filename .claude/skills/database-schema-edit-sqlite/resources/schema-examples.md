# Schema Examples (SQLite)

## Creating a New Table

```sql
-- ============================================================================
-- NOTIFICATION DOMAIN
-- ============================================================================

CREATE TABLE IF NOT EXISTS notification (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('EVENT_PUBLISHED', 'REGISTRATION_OPENED', 'RESULTS_POSTED')),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_notification_user_id ON notification(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_is_read ON notification(is_read);
CREATE INDEX IF NOT EXISTS idx_notification_created_at ON notification(created_at);
```

## Adding a Column to Existing Table

### Step 1: Update Table Definition (for new databases)

Update `create_schema.sql`:

```sql
CREATE TABLE IF NOT EXISTS results_phase (
    id TEXT PRIMARY KEY,
    category_id TEXT NOT NULL,
    phase TEXT NOT NULL CHECK (phase IN ('KNOCKOUT', 'QF', 'SF', 'F')),
    heat TEXT,
    phase_order INTEGER NOT NULL,
    start_date TEXT,
    start_time TEXT,
    laps INTEGER NOT NULL,
    sections TEXT NOT NULL,  -- JSON stored as TEXT
    is_ongoing INTEGER NOT NULL DEFAULT 0,  -- NEW COLUMN
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES results_category(id) ON DELETE CASCADE
);
```

### Step 2: Create Migration File

Create `migrations/003_add_is_ongoing_to_results_phase.sql`:

```sql
-- Migration: 003_add_is_ongoing_to_results_phase
-- Add is_ongoing column to track active phases during competition

ALTER TABLE results_phase ADD COLUMN is_ongoing INTEGER NOT NULL DEFAULT 0;
```

## JSON Field Example

SQLite stores JSON as TEXT. Use SQLite JSON functions for queries.

```sql
CREATE TABLE IF NOT EXISTS signup_form (
    id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL,
    name TEXT NOT NULL,
    form_fields TEXT NOT NULL DEFAULT '[]',  -- JSON array as TEXT
    settings TEXT,  -- Optional JSON object as TEXT
    status TEXT NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'PUBLISHED', 'CLOSED', 'DELETED')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES event(id) ON DELETE CASCADE
);
```

Querying JSON in SQLite:

```sql
-- Extract JSON field
SELECT json_extract(settings, '$.max_participants') FROM signup_form;

-- Filter by JSON value
SELECT * FROM signup_form WHERE json_extract(form_fields, '$[0].type') = 'text';
```

## Composite Index Example

```sql
-- Composite index for common query pattern
CREATE INDEX IF NOT EXISTS idx_signup_entry_form_status
    ON signup_entry(signup_form_id, status);
```

## Unique Constraint Example

```sql
-- Unique constraint on combination of fields
CREATE UNIQUE INDEX IF NOT EXISTS uq_event_category_event_name
    ON event_category(event_id, name);
```

## Complex Schema Migration (Recreate Table)

When SQLite's limited ALTER TABLE isn't sufficient (dropping columns, changing types, adding constraints):

Create migration file `migrations/005_restructure_user_table.sql`:

```sql
-- Migration: 005_restructure_user_table
-- Restructure user table: remove deprecated column, add new constraint

-- Step 1: Create new table with desired structure
CREATE TABLE user_account_new (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'USER' CHECK (role IN ('USER', 'ADMIN', 'MODERATOR')),
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Step 2: Copy data from old table
INSERT INTO user_account_new (id, email, name, role, is_active, created_at)
SELECT id, email, name, role, is_active, created_at FROM user_account;

-- Step 3: Drop old table
DROP TABLE user_account;

-- Step 4: Rename new table
ALTER TABLE user_account_new RENAME TO user_account;

-- Step 5: Recreate indexes
CREATE INDEX IF NOT EXISTS idx_user_account_email ON user_account(email);
CREATE INDEX IF NOT EXISTS idx_user_account_role ON user_account(role);
```

## Enabling Foreign Keys

SQLite requires explicit foreign key enforcement. Add at the start of `create_schema.sql`:

```sql
-- Enable foreign key constraints
PRAGMA foreign_keys = ON;
```

## Migrations Table

Every schema must include the migrations tracking table:

```sql
-- Migrations tracking table (required)
CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Date/Time Handling

SQLite stores dates as TEXT. Use ISO 8601 format:

```sql
CREATE TABLE IF NOT EXISTS event (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    start_date TEXT NOT NULL,  -- Format: 'YYYY-MM-DD'
    start_time TEXT,           -- Format: 'HH:MM:SS'
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

Query dates:

```sql
-- Filter by date range
SELECT * FROM event WHERE start_date >= '2024-01-01' AND start_date < '2024-02-01';

-- Order by datetime
SELECT * FROM event ORDER BY datetime(start_date || ' ' || COALESCE(start_time, '00:00:00'));
```
