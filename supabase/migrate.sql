-- MindCare AI — Migration Script
-- Run this FIRST if you have v1/v2 tables, then run schema.sql
-- ⚠️ WARNING: This drops existing tables and data!

-- Drop old tables (in reverse dependency order)
DROP TABLE IF EXISTS activity_streaks CASCADE;
DROP TABLE IF EXISTS crisis_events CASCADE;
DROP TABLE IF EXISTS follow_ups CASCADE;
DROP TABLE IF EXISTS user_sessions CASCADE;
DROP TABLE IF EXISTS emotion_detections CASCADE;
DROP TABLE IF EXISTS mood_entries CASCADE;
DROP TABLE IF EXISTS chat_messages CASCADE;
DROP TABLE IF EXISTS profiles CASCADE;

-- Now run schema.sql to recreate everything
