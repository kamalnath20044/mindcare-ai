-- MindCare AI — Migration: Role-Based Auth + Homework Fix
-- Run this in Supabase SQL Editor

-- ══════════════════════════════════════════════
-- 1. Add is_admin column to profiles
--    (for simple boolean admin check)
-- ══════════════════════════════════════════════
ALTER TABLE profiles
  ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;

-- ══════════════════════════════════════════════
-- 2. Ensure role column also exists (belt + suspenders)
-- ══════════════════════════════════════════════
ALTER TABLE profiles
  ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'user'
  CHECK (role IN ('user', 'therapist', 'admin'));

-- ══════════════════════════════════════════════
-- 3. Make a user an admin/therapist:
--    Replace 'your-email@example.com' with the
--    actual email of the therapist account.
-- ══════════════════════════════════════════════
-- UPDATE profiles
-- SET is_admin = TRUE, role = 'therapist'
-- WHERE email = 'your-email@example.com';

-- ══════════════════════════════════════════════
-- 4. Homework fix: ensure assigned_at column exists
-- ══════════════════════════════════════════════
ALTER TABLE homework_assignments
  ADD COLUMN IF NOT EXISTS assigned_at TIMESTAMPTZ DEFAULT NOW();

-- ══════════════════════════════════════════════
-- 5. Index for fast role lookups
-- ══════════════════════════════════════════════
CREATE INDEX IF NOT EXISTS idx_profiles_is_admin ON profiles(is_admin);

-- ══════════════════════════════════════════════
-- DONE — Check profiles table to confirm columns:
-- SELECT id, email, name, is_admin, role FROM profiles LIMIT 5;
-- ══════════════════════════════════════════════
