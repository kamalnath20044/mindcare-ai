# MindCare AI — AI-Driven Mental Health Support Platform

> **How might we utilize AI chatbots and machine learning to address the challenges of incomplete alleviation of depression symptoms, attrition, and loss of follow-up in mental health treatment?**

## 🎯 Problem Statement

Mental health treatment faces critical challenges:
1. **Incomplete symptom alleviation** — Patients need continuous, personalized support
2. **Attrition** — Users drop off when engagement fades
3. **Loss of follow-up** — No mechanism to re-engage inactive users

MindCare AI solves these with an intelligent, AI-powered platform featuring context-aware conversations, automated follow-ups, crisis detection, and personalized recommendations.

---

## ✨ Key Features

### 🤖 AI Therapist (LLM Integration)
- Context-aware therapeutic conversations using HuggingFace transformers
- `distilbert-base-uncased-finetuned-sst-2-english` for sentiment analysis
- `facebook/blenderbot-400M-distill` for conversational AI
- Curated therapeutic response library with empathy + validation + techniques

### 🧠 Chat Memory (Context Awareness)
- Per-user persistent conversation history (Supabase)
- Session context building for intelligent follow-up responses
- Mood trend analysis from conversation patterns

### 🔔 Follow-Up System (Anti-Attrition)
- Automated inactivity detection (1, 2, 3, 7, 14 day tiers)
- Personalized re-engagement messages
- Activity streaks and daily check-ins
- Targeted recommendations based on recent moods

### 🆘 Crisis Detection System
- 3-tier risk assessment (critical, high, moderate)
- 30+ crisis/distress keyword patterns
- Immediate emergency resource presentation (helplines)
- Audit logging of crisis events for safety

### 📊 Dashboard & Analytics
- Real-time mood trend visualizations (Chart.js)
- Emotion distribution doughnut charts
- Chat activity bar charts
- Personalized AI-generated insights
- Time-range filtering (7d, 14d, 30d, 90d)

### 😊 Emotion Detection
- Real-time facial emotion detection via webcam (OpenCV + TensorFlow)
- Text-based emotion analysis
- Emotion history tracking

### 💊 Personalization Engine
- Emotional profile building from user history
- Context-aware coping strategy recommendations
- Personalized greetings based on mood trends
- Dynamic chat context for smarter AI responses

### 🎙️ Voice Input
- Speech-to-text via browser MediaRecorder API
- Voice message integration with chat

### 🧘 Wellness Tools
- Guided breathing exercises (4-7-8 technique)
- Meditation resources
- Relaxation techniques
- Motivational content
- Emergency helpline resources

---

## 🏗️ Architecture

```
┌──────────────── Frontend (React + Vite) ────────────────┐
│  Landing → Auth → Dashboard → Chat → Analytics → Tools  │
│  Netlify deployment                                      │
└────────────────────────┬────────────────────────────────-┘
                         │ REST API (Axios + JWT)
┌────────────────────────┴────────────────────────────────-┐
│              Backend (FastAPI + Python)                   │
│  Routers: auth, chat, mood, emotion, voice, wellness,    │
│           alerts, followup, analytics                    │
│  Services: nlp, crisis, personalization, followup,       │
│            analytics, chat_memory, smart_alerts, emotion │
│  Vercel deployment                                       │
└────────────────────────┬────────────────────────────────-┘
                         │
┌────────────────────────┴─────────────────────────────────┐
│              Database (Supabase / PostgreSQL)             │
│  Tables: profiles, chat_messages, mood_entries,          │
│          emotion_detections, follow_ups, crisis_events,  │
│          user_sessions, activity_streaks                 │
└──────────────────────────────────────────────────────────┘
```

## 📂 Folder Structure

```
final_year_project/
├── backend/
│   ├── main.py                    # FastAPI entry point
│   ├── config.py                  # Environment configuration
│   ├── requirements.txt           # Python dependencies
│   ├── vercel.json                # Vercel deployment config
│   ├── .env                       # Environment variables
│   ├── routers/
│   │   ├── auth.py                # JWT authentication
│   │   ├── chat.py                # AI Therapist chat
│   │   ├── mood.py                # Mood tracking CRUD
│   │   ├── emotion.py             # Emotion detection
│   │   ├── voice.py               # Voice transcription
│   │   ├── wellness.py            # Wellness tools
│   │   ├── alerts.py              # Smart alerts
│   │   ├── followup.py            # Follow-up system
│   │   └── analytics.py           # Dashboard analytics
│   └── services/
│       ├── nlp_service.py         # NLP (sentiment + response generation)
│       ├── crisis_service.py      # Crisis detection & safety
│       ├── personalization.py     # Personalization engine
│       ├── followup_service.py    # Follow-up & streaks
│       ├── analytics_service.py   # Analytics data layer
│       ├── chat_memory.py         # Conversation context
│       ├── smart_alerts.py        # Alert generation
│       ├── emotion_service.py     # Facial emotion detection
│       ├── voice_service.py       # Speech-to-text
│       └── supabase_client.py     # DB client singleton
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Routing (public + protected)
│   │   ├── main.jsx               # Entry point
│   │   ├── index.css              # Complete design system
│   │   ├── api/client.js          # Axios API client
│   │   ├── context/AuthContext.jsx # Auth state management
│   │   ├── pages/
│   │   │   ├── Landing.jsx        # SaaS landing page
│   │   │   ├── Login.jsx          # JWT login
│   │   │   ├── Register.jsx       # Registration
│   │   │   ├── Dashboard.jsx      # Main dashboard
│   │   │   ├── Chat.jsx           # WhatsApp-style AI chat
│   │   │   ├── Analytics.jsx      # Analytics dashboard
│   │   │   ├── EmotionDetection.jsx
│   │   │   ├── MoodTracker.jsx
│   │   │   └── WellnessTools.jsx
│   │   └── components/
│   │       ├── Sidebar.jsx
│   │       ├── CrisisModal.jsx    # Emergency helplines modal
│   │       ├── FollowUpBanner.jsx # Check-in notifications
│   │       └── EmergencyBanner.jsx
│   ├── netlify.toml               # Netlify config
│   ├── public/_redirects          # SPA redirect
│   └── package.json
└── supabase/
    └── schema.sql                 # Database schema v3.0
```

## 🚀 How to Run

### Prerequisites
- Python 3.10+
- Node.js 18+
- Supabase account (free tier)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

Create `.env`:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
FRONTEND_URL=http://localhost:5173
```

Start the server:
```bash
python -m uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
```

Create `.env`:
```env
VITE_API_URL=http://localhost:8000/api
```

Start dev server:
```bash
npm run dev
```

### 3. Database Setup
1. Go to your Supabase project → SQL Editor
2. Paste and run `supabase/schema.sql`

---

## 🌐 Deployment

### Frontend → Netlify
1. Push code to GitHub
2. Connect repo to [Netlify](https://netlify.com)
3. Set build command: `npm run build`
4. Set publish directory: `dist`
5. Add env variable: `VITE_API_URL=https://your-backend.vercel.app/api`

### Backend → Vercel
1. Push code to GitHub
2. Connect repo to [Vercel](https://vercel.com)
3. Set root directory: `backend`
4. Add env variables: `SUPABASE_URL`, `SUPABASE_KEY`, `FRONTEND_URL`

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/register` | POST | Register new user |
| `/api/auth/login` | POST | Login (returns JWT) |
| `/api/auth/me` | GET | Get current user |
| `/api/chat` | POST | Send message to AI therapist |
| `/api/chat/history` | GET | Get chat history |
| `/api/mood` | POST | Log mood entry |
| `/api/mood` | GET | Get mood entries |
| `/api/emotion/detect` | POST | Detect facial emotion |
| `/api/followup` | GET | Get follow-up messages |
| `/api/followup/checkin` | POST | Daily check-in |
| `/api/followup/streak` | GET | Get activity streak |
| `/api/analytics/dashboard` | GET | Dashboard statistics |
| `/api/analytics/mood` | GET | Mood trend analytics |
| `/api/analytics/emotions` | GET | Emotion analytics |
| `/api/analytics/chat` | GET | Chat usage analytics |
| `/api/analytics/recommendations` | GET | Personalized recommendations |
| `/api/wellness/tips` | GET | Wellness tips |
| `/api/alerts` | GET | Smart alerts |

---

## 🛡️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, Vite 7, Chart.js 4, Axios, React Router 7 |
| **Backend** | FastAPI, Python 3.10+, Uvicorn |
| **AI/ML** | HuggingFace Transformers, TensorFlow, OpenCV |
| **Database** | Supabase (PostgreSQL) |
| **Auth** | JWT (PyJWT), bcrypt hashing |
| **Hosting** | Netlify (frontend), Vercel (backend) |

---

## 📊 How the System Addresses the Problem Statement

| Challenge | Solution | Feature |
|---|---|---|
| Incomplete symptom alleviation | Continuous AI support + personalized coping strategies | AI Therapist + Personalization Engine |
| Attrition | Engagement streaks + automated re-engagement | Follow-Up System |
| Loss of follow-up | Inactivity detection + check-in prompts | Follow-Up Service + Notifications |
| Lack of monitoring | Real-time mood tracking + analytics | Dashboard + Mood Tracker |
| Crisis situations | Immediate safety protocols + helplines | Crisis Detection System |
| Generic responses | Context-aware AI using chat memory | Chat Memory + Personalization |

---

## 📝 License

This project is developed for educational and research purposes as a final year engineering project.

---

**Built with ❤️ for mental wellness**
