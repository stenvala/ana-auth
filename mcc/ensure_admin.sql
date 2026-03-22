-- ============================================================================
-- MASTER ADMIN USER (idempotent)
-- ============================================================================

INSERT INTO user_account (user_name, password_hash, given_name, family_name, display_name)
VALUES (
    'stenvala',
    '$2b$12$.k1IKOT04eTkcDAsUBnCSOZY2WD4p1nem3IjVO4/Wbw9AMBZLXRte',
    'Admin',
    'Stenvala',
    'Admin'
)
ON CONFLICT (user_name) DO NOTHING;

-- Insert primary email for admin if no email exists yet
INSERT INTO user_email (user_account_id, email, is_primary, is_verified)
SELECT id, 'admin@ana-auth.local', TRUE, TRUE
FROM user_account
WHERE user_name = 'stenvala'
  AND NOT EXISTS (
      SELECT 1 FROM user_email WHERE user_account_id = (
          SELECT id FROM user_account WHERE user_name = 'stenvala'
      )
  );
