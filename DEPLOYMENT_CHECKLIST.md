# Production Deployment Checklist

## Pre-Deployment

### Code Quality
- [ ] All dependencies in `requirements.txt` and `package.json`
- [ ] No hardcoded credentials (use `.env`)
- [ ] Remove console.log/print statements for debugging
- [ ] Test app locally: `npm run dev` + `uvicorn main:app --reload`

### Security
- [ ] Update CORS to specific domains (don't use `"*"` in production)
- [ ] Add HTTPS enforcement
- [ ] Validate all user inputs
- [ ] Hide error details in production

### Environment Variables
- [ ] Backend: `SUPABASE_URL` and `SUPABASE_KEY` configured
- [ ] Frontend: `VITE_API_URL` set to production backend URL
- [ ] No `.env` files committed to Git (already in `.gitignore`)

---

## Frontend Deployment to Vercel

```bash
# 1. Push to GitHub
git add .
git commit -m "Deploy to Vercel"
git push origin main

# 2. Go to vercel.com → Import Project
# 3. Select your GitHub repo
# 4. Framework: Vite
# 5. Environment Variables:
#    VITE_API_URL = https://your-backend.onrender.com/api
# 6. Deploy
```

**Result:** `https://your-app.vercel.app`

---

## Backend Deployment to Render

```bash
# 1. Create app.render.yaml (optional, for auto-deployment)
# 2. Go to render.com → New → Web Service
# 3. Connect GitHub repo
# 4. Settings:
#    - Name: mindcare-backend
#    - Environment: Python
#    - Build Command: pip install -r requirements.txt
#    - Start Command: uvicorn main:app --host 0.0.0.0 --port 8000
#    - Environment Variables:
#      • SUPABASE_URL = your-url
#      • SUPABASE_KEY = your-key
# 5. Deploy
```

**Result:** `https://mindcare-backend.onrender.com`

---

## Post-Deployment Testing

### Test Backend
```bash
curl https://your-backend.onrender.com/
# Should return JSON with service info
```

### Test Frontend
1. Open `https://your-app.vercel.app`
2. Open browser DevTools (F12)
3. Check Network tab - API calls should go to backend URL
4. Test each feature:
   - [ ] Chat works
   - [ ] Mood tracking works
   - [ ] Emergency info loads
   - [ ] No 404 or CORS errors

### Test on Mobile
1. Open on phone: `https://your-app.vercel.app`
2. Same features work as desktop
3. Viewport fits phone screen

---

## Post-Deploy Configuration

### CORS Configuration (Production)
Update `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",
        "https://www.your-domain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Monitor Errors
- **Frontend:** Use Vercel Analytics (built-in)
- **Backend:** Use Render logs (built-in)

---

## Custom Domain (Optional)

1. Buy domain (namecheap.com, godaddy.com, etc.)
2. **For Vercel:** Go to Settings → Domains → Add custom domain
3. **For Render:** Go to Settings → Custom Domains
4. Update DNS settings as instructed
5. Both automatically get HTTPS certificate

---

## Environment Variables Reference

### Render Backend
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-anon-key
ENV=production
```

### Vercel Frontend
```
VITE_API_URL=https://mindcare-backend.onrender.com/api
```

---

## Estimated Times
- Vercel Deploy: ~2 minutes
- Render Deploy: ~15 minutes (may take time to spin up)
- Custom Domain: ~30 minutes (DNS propagation takes time)

**Total:** ~45 minutes to production

---

## Monitoring & Maintenance

### Weekly Checks
- [ ] Check Render logs for errors
- [ ] Check Vercel analytics
- [ ] Test critical features from mobile

### Monthly Tasks
- [ ] Review API usage/costs
- [ ] Update dependencies: `npm update`, `pip list --outdated`
- [ ] Check Supabase usage

### When Users Report Issues
1. Check browser console → Network tab (capture screenshot)
2. Check backend logs on Render
3. Check frontend on Vercel
4. Check Supabase status

---

## Rollback Plan

If something breaks:
1. **Frontend:** Vercel automatically keeps previous deployments → rollback in 1 click
2. **Backend:** Render also keeps versions → redeploy previous version
3. **Data:** Supabase creates automatic backups

---

## Questions?

- **Frontend issues:** Check Vercel logs + browser DevTools
- **Backend issues:** Check Render logs + network requests
- **Database issues:** Check Supabase dashboard
- **CORS issues:** Verify `allow_origins` in main.py matches your domain
