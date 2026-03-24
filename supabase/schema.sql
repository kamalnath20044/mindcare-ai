-- MindCare AI — Database Schema v3.0
-- Full Mental Health Support Platform
-- Run this in your Supabase SQL Editor

-- ══════════════════════════════════════
-- 1. User Profiles (with auth)
-- ══════════════════════════════════════
CREATE TABLE IF NOT EXISTS profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  password_hash TEXT,
  avatar_url TEXT,
  timezone TEXT DEFAULT 'UTC',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_active_at TIMESTAMPTZ DEFAULT NOW()
);

-- ══════════════════════════════════════
-- 2. Chat Messages (persistent memory)
-- ══════════════════════════════════════
CREATE TABLE IF NOT EXISTS chat_messages (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  sentiment TEXT,
  emotion TEXT,
  therapist_mode BOOLEAN DEFAULT FALSE,
  context_used BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ══════════════════════════════════════
-- 3. Mood Entries (tracking)
-- ══════════════════════════════════════
CREATE TABLE IF NOT EXISTS mood_entries (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  mood TEXT NOT NULL,
  note TEXT,
  intensity INTEGER DEFAULT 3 CHECK (intensity BETWEEN 1 AND 5),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ══════════════════════════════════════
-- 4. Emotion Detections (facial + text)
-- ══════════════════════════════════════
CREATE TABLE IF NOT EXISTS emotion_detections (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  emotion TEXT NOT NULL,
  confidence REAL,
  source TEXT DEFAULT 'webcam' CHECK (source IN ('webcam', 'text', 'voice')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ══════════════════════════════════════
-- 5. User Sessions (for follow-up)
-- ══════════════════════════════════════
CREATE TABLE IF NOT EXISTS user_sessions (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  session_start TIMESTAMPTZ DEFAULT NOW(),
  session_end TIMESTAMPTZ,
  messages_count INTEGER DEFAULT 0,
  avg_sentiment REAL,
  primary_emotion TEXT
);

-- ══════════════════════════════════════
-- 6. Follow-Up Records
-- ══════════════════════════════════════
CREATE TABLE IF NOT EXISTS follow_ups (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  type TEXT NOT NULL CHECK (type IN ('check_in', 'reminder', 'recommendation', 'streak')),
  message TEXT NOT NULL,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'delivered', 'read', 'dismissed')),
  priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'critical')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  read_at TIMESTAMPTZ
);

-- ══════════════════════════════════════
-- 7. Crisis Events (audit log)
-- ══════════════════════════════════════
CREATE TABLE IF NOT EXISTS crisis_events (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  trigger_message TEXT NOT NULL,
  risk_level TEXT NOT NULL CHECK (risk_level IN ('moderate', 'high', 'critical')),
  keywords_matched TEXT[],
  response_given TEXT,
  helplines_shown BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ══════════════════════════════════════
-- 8. Activity Streaks
-- ══════════════════════════════════════
CREATE TABLE IF NOT EXISTS activity_streaks (
  id SERIAL PRIMARY KEY,
  user_id UUID UNIQUE REFERENCES profiles(id) ON DELETE CASCADE,
  current_streak INTEGER DEFAULT 0,
  longest_streak INTEGER DEFAULT 0,
  last_checkin_date DATE,
  total_checkins INTEGER DEFAULT 0,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ══════════════════════════════════════
-- Indexes for performance
-- ══════════════════════════════════════
CREATE INDEX IF NOT EXISTS idx_mood_user ON mood_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_mood_created ON mood_entries(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_user ON chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_created ON chat_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_emotion_user ON emotion_detections(user_id);
CREATE INDEX IF NOT EXISTS idx_followup_user ON follow_ups(user_id);
CREATE INDEX IF NOT EXISTS idx_followup_status ON follow_ups(status);
CREATE INDEX IF NOT EXISTS idx_crisis_user ON crisis_events(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_active ON profiles(last_active_at DESC);
