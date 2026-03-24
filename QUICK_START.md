# 🚀 Quick Start - Mobile Testing & Deployment

## What Changed?
✅ Frontend now reads API URL from `.env` file  
✅ Vite configured to accept network connections  
✅ Backend can bind to all interfaces using `--host 0.0.0.0`

---

## Test on Mobile (Same WiFi Network) - 5 Minutes

### 1. Find Your PC's IP
```powershell
ipconfig
```
Note: IPv4 Address (e.g., `192.168.0.5`)

### 2. Update Frontend Config
Edit `frontend/.env`:
```
VITE_API_URL=http://192.168.0.5:8000/api
```

### 3. Start Backend
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Start Frontend
```bash
cd frontend
npm run dev
```

### 5. Open on Phone
Open browser on phone (same WiFi):
```
http://192.168.0.5:5173
```

✅ Done! Test all features.

---

## Key Issues Fixed

| Problem | Solution |
|---------|----------|
| Mobile couldn't reach backend | Changed API client to use env variables |
| Frontend only accessible locally | Added `host: '0.0.0.0'` to Vite config |
| Backend locked to localhost | Use `--host 0.0.0.0` when running |

---

## Deploy to Cloud (Choose One)

### Fastest (Vercel + Render)
- **Frontend:** Deploy to Vercel (connects to GitHub, auto-deploys)
- **Backend:** Deploy to Render (free tier available)
- **Time:** ~15 minutes
- **Cost:** Free (production-ready)

### All-in-One (Docker + Cloud)
- Use Docker Compose locally or any VPS
- **Time:** ~30 minutes
- **Cost:** $5-10/month

### See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions

---

## Troubleshooting

**"Mobile shows blank page"**
→ Check browser console (F12) → Network tab → see if API calls fail

**"API connection refused"**
→ Make sure backend running with `--host 0.0.0.0`  
→ Check Windows Firewall allows port 8000

**"CORS error"**
→ Backend already configured, shouldn't happen

**Need help?**
→ Check [DEPLOYMENT.md](./DEPLOYMENT.md) troubleshooting section

---

## Files Changed
- ✏️ `frontend/src/api/client.js` - Environment-based API URL
- ✏️ `frontend/vite.config.js` - Network access + build config
- ✨ `frontend/.env` - Created
- ✨ `frontend/.env.example` - Created
- 📋 `DEPLOYMENT.md` - Created (full guide)
