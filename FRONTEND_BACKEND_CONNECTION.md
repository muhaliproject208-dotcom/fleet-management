# Frontend Configuration for Deployed Backend

## After Backend Deployment

Once your backend is deployed on Render, you need to configure your frontend to connect to it.

## Step 1: Get Your Backend URL

From Render dashboard:
- Example: `https://fleet-management-backend.onrender.com`
- Copy this URL (without trailing slash)

## Step 2: Update Frontend Environment Variables

### For Local Development (testing with deployed backend)

Create/update `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

### For Vercel Deployment

1. Go to your project on Vercel
2. Navigate to Settings → Environment Variables
3. Add/Update:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
   ```
4. Select all environments (Production, Preview, Development)
5. Save and redeploy

## Step 3: Update Backend CORS Settings

In Render dashboard, add/update environment variables:

```
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
ALLOWED_HOSTS=.onrender.com,your-frontend.vercel.app
```

**Important:** 
- Replace `your-frontend.vercel.app` with your actual Vercel URL
- If you have multiple frontend URLs (preview, production), separate with commas:
  ```
  CORS_ALLOWED_ORIGINS=https://fleet-management.vercel.app,https://fleet-management-preview.vercel.app
  ```

## Step 4: Redeploy

After updating environment variables:
- **Backend (Render):** Manual Deploy → Deploy latest commit
- **Frontend (Vercel):** Deployments → Redeploy (or push to trigger auto-deploy)

## Step 5: Test Connection

1. Open your frontend in browser
2. Try to login
3. Check browser console for errors
4. If CORS errors appear, verify Step 3

## Common Issues

### CORS Errors
**Error:** `Access to fetch at 'https://backend...' has been blocked by CORS policy`

**Solution:**
- Add frontend URL to `CORS_ALLOWED_ORIGINS` in backend
- Include the protocol (`https://`)
- No trailing slash
- Redeploy backend

### API Not Found
**Error:** `404 Not Found` or `ERR_NAME_NOT_RESOLVED`

**Solution:**
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check backend is deployed and running
- Test backend URL directly in browser

### Backend Sleeping (Free Tier)
**Symptom:** First request takes 30-60 seconds

**Explanation:**
- Free tier spins down after 15 min inactivity
- First request wakes it up
- Subsequent requests are fast

**Solution:**
- Expected behavior on free tier
- Upgrade to Starter plan ($7/month) for always-on
- Or use uptime monitoring to keep it awake

## Environment Variables Reference

### Frontend (.env.local or Vercel)
```
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

### Backend (Render)
```
ALLOWED_HOSTS=.onrender.com,your-frontend.vercel.app
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
DEBUG=False
SECRET_KEY=[your-secret-key]
[... other variables ...]
```

## Testing Checklist

- [ ] Backend health check: `https://your-backend.onrender.com/admin/`
- [ ] API accessible: `https://your-backend.onrender.com/api/v1/`
- [ ] Frontend can connect
- [ ] Login works
- [ ] Can create inspection
- [ ] Can view reports
- [ ] PDF download works
- [ ] All features functional

## Monitoring

### Check Backend Logs
- Render Dashboard → Your Service → Logs
- Watch for errors during API calls

### Check Frontend Console
- Browser DevTools → Console
- Watch for network errors or CORS issues

### Test API Endpoints
Use browser or Postman:
```
GET https://your-backend.onrender.com/api/v1/inspections/
Authorization: Bearer [your-token]
```

---

**Both Deployed!** 🎉

Your full-stack application should now be live:
- Backend: https://your-backend.onrender.com
- Frontend: https://your-frontend.vercel.app
