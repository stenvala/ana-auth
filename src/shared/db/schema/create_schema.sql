-- ============================================================================
-- AUTH DOMAIN
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_account (
    id VARCHAR(255) PRIMARY KEY DEFAULT REPLACE(gen_random_uuid()::text, '-', ''),
    user_name VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    given_name VARCHAR(255),
    family_name VARCHAR(255),
    display_name VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE user_account IS 'User identity and authentication';

CREATE TABLE IF NOT EXISTS user_email (
    id VARCHAR(255) PRIMARY KEY DEFAULT REPLACE(gen_random_uuid()::text, '-', ''),
    user_account_id VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_account_id) REFERENCES user_account(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_user_email_user_account_id ON user_email(user_account_id);
CREATE INDEX IF NOT EXISTS idx_user_email_is_primary ON user_email(is_primary);

COMMENT ON TABLE user_email IS 'User email addresses with primary and verification flags';

-- ============================================================================
-- MIGRATION TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS _deployment_log (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL UNIQUE,
    checksum VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE _deployment_log IS 'Tracks applied database migrations';

-- ============================================================================
-- SCHEMA MODIFICATION SUPPORT
-- ============================================================================
-- Add ALTER TABLE statements here for existing database migrations.
