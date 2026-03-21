# Schema Examples

## Creating a New Table

```sql
-- ============================================================================
-- NOTIFICATION DOMAIN
-- ============================================================================

CREATE TABLE IF NOT EXISTS notification (
    id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('EVENT_PUBLISHED', 'REGISTRATION_OPENED', 'RESULTS_POSTED')),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_notification_user_id ON notification(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_is_read ON notification(is_read);
CREATE INDEX IF NOT EXISTS idx_notification_created_at ON notification(created_at);

-- Comments
COMMENT ON TABLE notification IS 'User notifications for system events';
COMMENT ON COLUMN notification.type IS 'Notification type enum';
```

## Adding a Column to Existing Table

### Step 1: Update Table Definition (for new databases)

```sql
CREATE TABLE IF NOT EXISTS results_phase (
    id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    category_id VARCHAR(255) NOT NULL,
    phase VARCHAR(50) NOT NULL CHECK (phase IN ('KNOCKOUT', 'QF', 'SF', 'F')),
    heat VARCHAR(10),
    phase_order INTEGER NOT NULL,
    start_date DATE,
    start_time TIME,
    laps INTEGER NOT NULL,
    sections JSONB NOT NULL,
    is_ongoing BOOLEAN NOT NULL DEFAULT FALSE,  -- NEW COLUMN
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES results_category(id) ON DELETE CASCADE
);
```

### Step 2: Add Migration (for existing databases)

In the `SCHEMA MODIFICATION SUPPORT` section:

```sql
DO $$
BEGIN
    -- Results phase table modifications
    ALTER TABLE results_phase ADD COLUMN IF NOT EXISTS is_ongoing BOOLEAN NOT NULL DEFAULT FALSE;
END $$;
```

### Step 3: Add Comment (optional)

```sql
COMMENT ON COLUMN results_phase.is_ongoing IS 'Tracks if phase is currently active during competition';
```

## JSONB Field Example

```sql
CREATE TABLE IF NOT EXISTS signup_form (
    id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    event_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    form_fields JSONB NOT NULL DEFAULT '[]',  -- Array of form field definitions
    settings JSONB,  -- Optional settings object
    status VARCHAR(50) NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'PUBLISHED', 'CLOSED', 'DELETED')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES event(id) ON DELETE CASCADE
);
```

## Composite Index Example

```sql
-- Composite index for common query pattern
CREATE INDEX IF NOT EXISTS idx_signup_entry_form_status
    ON signup_entry(signup_form_id, status);

-- Partial index for active records only
CREATE INDEX IF NOT EXISTS idx_event_active
    ON event(group_id)
    WHERE status = 'ACTIVE';
```

## Unique Constraint Example

```sql
-- Unique constraint on combination of fields
ALTER TABLE event_category
    ADD CONSTRAINT uq_event_category_event_name
    UNIQUE (event_id, name);
```
