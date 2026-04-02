-- MindCare AI — Database Schema v4.0
-- Production-Level Mental Health Support Platform
-- Run this in your Supabase SQL Editor (after v3 schema)

-- ══════════════════════════════════════
-- 9. PHQ-9 Depression Assessments
-- ══════════════════════════════════════
CREATE TABLE IF NOT EXISTS phq9_entries (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  q1 INTEGER NOT NULL CHECK (q1 BETWEEN 0 AND 3),
  q2 INTEGER NOT NULL CHECK (q2 BETWEEN 0 AND 3),
  q3 INTEGER NOT NULL CHECK (q3 BETWEEN 0 AND 3),
  q4 INTEGER NOT NULL CHECK (q4 BETWEEN 0 AND 3),
  q5 INTEGER NOT NULL CHECK (q5 BETWEEN 0 AND 3),
  q6 INTEGER NOT NULL CHECK (q6 BETWEEN 0 AND 3),
  q7 INTEGER NOT NULL CHECK (q7 BETWEEN 0 AND 3),
  q8 INTEGER NOT NULL CHECK (q8 BETWEEN 0 AND 3),
  q9 INTEGER NOT NULL CHECK (q9 BETWEEN 0 AND 3),
  total_score INTEGER NOT NULL CHECK (total_score BETWEEN 0 AND 27),
  severity TEXT NOT NULL CHECK (severity IN ('none', 'mild', 'moderate', 'moderately_severe', 'severe')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ══════════════════════════════════════
-- 10. GAD-7 Anxiety Assessments
-- ══════════════════════════════════════
CREATE TABLE IF NOT EXISTS gad7_entries (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  q1 INTEGER NOT NULL CHECK (q1 BETWEEN 0 AND 3),
  q2 INTEGER NOT NULL CHECK (q2 BETWEEN 0 AND 3),
  q3 INTEGER NOT NULL CHECK (q3 BETWEEN 0 AND 3),
  q4 INTEGER NOT NULL CHECK (q4 BETWEEN 0 AND 3),
  q5 INTEGER NOT NULL CHECK (q5 BETWEEN 0 AND 3),
  q6 INTEGER NOT NULL CHECK (q6 BETWEEN 0 AND 3),
  q7 INTEGER NOT NULL CHECK (q7 BETWEEN 0 AND 3),
  total_score INTEGER NOT NULL CHECK (total_score BETWEEN 0 AND 21),
  severity TEXT NOT NULL CHECK (severity IN ('none', 'mild', 'moderate', 'severe')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ══════════════════════════════════════
-- 11. Session Summaries (AI-generated)
-- ══════════════════════════════════════
CREATE TABLE IF NOT EXISTS session_summaries (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  session_start TIMESTAMPTZ NOT NULL,
  session_end TIMESTAMPTZ NOT NULL,
  message_count INTEGER DEFAULT 0,
  summary TEXT NOT NULL,
  key_topics TEXT[],
  dominant_emotion TEXT,
  sentiment_trend TEXT,
  techniques_used TEXT[],
  risk_level TEXT DEFAULT 'none',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ══════════════════════════════════════
-- 12. Homework Assignments (CBT Loop)
-- ══════════════════════════════════════
CREATE TABLE IF NOT EXISTS homework_assignments (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  category TEXT NOT NULL CHECK (category IN (
    'thought_record', 'behavioral_activation', 'grounding',
    'journaling', 'breathing', 'gratitude', 'social', 'physical', 'mindfulness'
  )),
  difficulty TEXT DEFAULT 'easy' CHECK (difficulty IN ('easy', 'medium', 'hard')),
  status TEXT DEFAULT 'assigned' CHECK (status IN ('assigned', 'in_progress', 'completed', 'skipped')),
  assigned_at TIMESTAMPTZ DEFAULT NOW(),
  due_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  completion_note TEXT,
  rating INTEGER CHECK (rating BETWEEN 1 AND 5),
  follow_up_done BOOLEAN DEFAULT FALSE
);

-- ══════════════════════════════════════
-- 13. Therapist Alerts
-- ══════════════════════════════════════
CREATE TABLE IF NOT EXISTS therapist_alerts (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  alert_type TEXT NOT NULL CHECK (alert_type IN ('crisis', 'high_risk', 'phq9_severe', 'inactivity', 'declining_trend')),
  risk_level TEXT NOT NULL CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
  context TEXT,
  trigger_data JSONB,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'acknowledged', 'resolved')),
  sent_at TIMESTAMPTZ,
  acknowledged_at TIMESTAMPTZ,
  acknowledged_by TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ══════════════════════════════════════
-- 14. User Consent Tracking (GDPR)
-- ══════════════════════════════════════
CREATE TABLE IF NOT EXISTS user_consents (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  consent_type TEXT NOT NULL CHECK (consent_type IN ('data_processing', 'analytics', 'email_notifications', 'research')),
  granted BOOLEAN DEFAULT FALSE,
  granted_at TIMESTAMPTZ,
  revoked_at TIMESTAMPTZ,
  ip_address TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ══════════════════════════════════════
-- Add role column to profiles (admin support)
-- ══════════════════════════════════════
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'user' CHECK (role IN ('user', 'therapist', 'admin'));
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS therapist_email TEXT;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS consent_given BOOLEAN DEFAULT FALSE;

-- ══════════════════════════════════════
-- Add sleep/energy to mood_entries
-- ══════════════════════════════════════
ALTER TABLE mood_entries ADD COLUMN IF NOT EXISTS sleep_hours REAL;
ALTER TABLE mood_entries ADD COLUMN IF NOT EXISTS energy_level INTEGER CHECK (energy_level BETWEEN 1 AND 10);
ALTER TABLE mood_entries ADD COLUMN IF NOT EXISTS mood_score INTEGER CHECK (mood_score BETWEEN 1 AND 10);

-- ══════════════════════════════════════
-- New Indexes for Performance
-- ══════════════════════════════════════
CREATE INDEX IF NOT EXISTS idx_phq9_user ON phq9_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_phq9_created ON phq9_entries(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_gad7_user ON gad7_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_gad7_created ON gad7_entries(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_session_summaries_user ON session_summaries(user_id);
CREATE INDEX IF NOT EXISTS idx_homework_user ON homework_assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_homework_status ON homework_assignments(status);
CREATE INDEX IF NOT EXISTS idx_therapist_alerts_user ON therapist_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_therapist_alerts_status ON therapist_alerts(status);
CREATE INDEX IF NOT EXISTS idx_consents_user ON user_consents(user_id);
CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role);
