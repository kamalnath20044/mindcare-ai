# MindCare AI - Deployment & Mobile Testing Guide

## Table of Contents
1. [Mobile Testing (Same Local Network)](#mobile-testing)
2. [Production Deployment](#production-deployment)
3. [Troubleshooting](#troubleshooting)

---

## Mobile Testing (Same Local Network)

### Step 1: Find Your Computer's IP Address

**On Windows (PowerShell):**
```powershell
ipconfig
```
Look for "IPv4 Address" under your network adapter (e.g., `192.168.0.5`)

### Step 2: Start Backend on All Interfaces

**Modified command to run backend:**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The `--host 0.0.0.0` makes the backend accessible from other devices on your network.

### Step 3: Configure Frontend for Mobile Testing

Create/update `frontend/.env` with your computer's IP:
```
VITE_API_URL=http://192.168.0.5:8000/api
```

### Step 4: Start Frontend

```bash
cd frontend
npm run dev
```

Vite will display URLs:
```
  Local:     http://localhost:5173
  Network:   http://192.168.0.5:5173
```

### Step 5: Access on Mobile Phone

On your mobile phone (connected to same WiFi):
- Open browser
- Go to: `http://192.168.0.5:5173`
- Test all features

---

## Production Deployment

### Option 1: Deploy to Vercel (Frontend) + Render (Backend)

#### Backend Deployment on Render

1. **Push code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Go to render.com** → Sign up with GitHub

3. **Create Web Service**
   - Connect your GitHub repo
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port 8000`
   - Add environment variables:
     - `SUPABASE_URL=your-url`
     - `SUPABASE_KEY=your-key`
   - Deploy

4. **Get backend URL** (e.g., `https://mindcare-ai.onrender.com`)

#### Frontend Deployment on Vercel

1. **Create `.env.production` in frontend:**
   ```
   VITE_API_URL=https://mindcare-ai.onrender.com/api
   ```

2. **Go to vercel.com** → Connect GitHub repo

3. **Configure deployment:**
   - Framework: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Add environment variables from `.env.production`
   - Deploy

---

### Option 2: Deploy Everything on Same Server (AWS/DigitalOcean)

#### Using DigitalOcean App Platform

1. **Backend Dockerfile** (create `backend/Dockerfile`):
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Frontend Dockerfile** (create `frontend/Dockerfile`):
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json .
RUN npm install
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=builder /app/dist dist
CMD ["serve", "-s", "dist", "-l", "3000"]
```

3. **Deploy both to DigitalOcean App Platform**

---

### Option 3: Docker Compose (Local/VPS)

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
    networks:
      - mindcare

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://backend:8000/api
    depends_on:
      - backend
    networks:
      - mindcare

networks:
  mindcare:
    driver: bridge
```

Run with:
```bash
docker-compose up -d
```

---

## Common Issues & Fixes

### Issue 1: Mobile Can't Connect to Backend

**Check:**
- Ensure both devices on same WiFi network
- Firewall isn't blocking port 8000
- Backend running with `--host 0.0.0.0`
- Using correct IP address in `.env`

**Test connection from mobile:**
```
Open: http://192.168.0.5:8000/
Should show JSON response with service info
```

### Issue 2: CORS Errors

Backend `main.py` already handles this, but ensure:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production: specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 3: Facial Emotion Detection on Mobile

**Limitation:** Most mobile browsers don't support direct webcam access via HTTP (needs HTTPS for security).

**Solutions:**
1. Use HTTPS in production (Vercel/Render/etc provide free SSL)
2. Use camera API libraries (e.g., MediaPipe)
3. Consider native mobile app (React Native)

### Issue 4: Voice Features on Mobile

Mobile browsers support Web Audio API, but test browser compatibility.

---

## Recommended Stack for Your Project

| Component | Service | Cost |
|-----------|---------|------|
| Frontend | Vercel | Free tier available |
| Backend | Render | Free tier (sleeps after 15 min inactivity) |
| Database | Supabase | Free tier |
| SSL/HTTPS | Automatic (Vercel/Render) | Free |
| Domain | Namecheap | ~$1/year |

**Total Monthly Cost:** $0-10 (before removing free tier limits)

---

## Deployment Checklist

- [ ] Create GitHub repository
- [ ] Add `.env` to `.gitignore`
- [ ] Update frontend `.env` with backend URL
- [ ] Test locally with mobile device
- [ ] Update CORS to specific domains in production
- [ ] Set up environment variables on hosting platform
- [ ] Test all features on mobile after deployment
- [ ] Enable HTTPS (required for webcam/microphone)
- [ ] Set up error monitoring (optional but recommended)

---

## Next Steps

1. **For immediate testing:** Follow "Mobile Testing (Same Local Network)" section
2. **For production:** Choose one deployment option and follow the steps
3. **Questions?** Check the troubleshooting section
