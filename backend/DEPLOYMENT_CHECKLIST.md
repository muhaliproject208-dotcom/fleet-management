# Quick Deployment Checklist

## Before Deploying

- [ ] All code pushed to GitHub
- [ ] Supabase database is running
- [ ] Have Supabase credentials ready

## Backend Deployment on Render (5 Steps)

### Step 1: Create Web Service
- Go to https://dashboard.render.com
- Click "New +" → "Web Service"
- Connect your GitHub repository

### Step 2: Configure Service
```
Name: fleet-management-backend
Region: [Choose closest to users]
Branch: main
Root Directory: backend
Runtime: Python 3
Build Command: ./build.sh
Start Command: gunicorn config.wsgi:application
Instance Type: Free (or Starter for production)
```

### Step 3: Add Environment Variables
Copy these and fill in your values:
```
PYTHON_VERSION=3.11.0
DEBUG=False
SECRET_KEY=[generate random key]
ALLOWED_HOSTS=.onrender.com

SUPABASE_URL=[from Supabase dashboard]
SUPABASE_KEY=[anon public key]
SUPABASE_SERVICE_KEY=[service role key]

SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=[from Supabase connection string]
SUPABASE_DB_PASSWORD=[your db password]
SUPABASE_DB_HOST=[from Supabase connection string]
SUPABASE_DB_PORT=5432

ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Step 4: Generate SECRET_KEY
Run locally:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### Step 5: Deploy
- Click "Create Web Service"
- Wait 3-5 minutes for deployment
- Copy your Render URL: `https://your-app.onrender.com`

## After Backend is Live

### Update Frontend (Vercel)
Add environment variable in Vercel:
```
NEXT_PUBLIC_API_URL=https://your-render-app.onrender.com
```

### Update CORS (Render)
After deploying frontend, add to Render environment variables:
```
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
ALLOWED_HOSTS=.onrender.com,your-frontend.vercel.app
```

## Testing

1. Visit `https://your-app.onrender.com/admin/` - Should see Django admin
2. Visit `https://your-app.onrender.com/api/v1/` - Should see API
3. Test login from frontend

## Troubleshooting

**Build fails?**
- Check build logs in Render dashboard
- Ensure `build.sh` has execute permissions
- Verify all dependencies in requirements.txt

**Can't connect to database?**
- Verify all SUPABASE_DB_* variables
- Check Supabase database is not paused
- Test connection string

**CORS errors?**
- Add frontend URL to CORS_ALLOWED_ORIGINS
- Ensure corsheaders middleware is active
- Redeploy after env var changes

**Free tier sleeping?**
- Free tier sleeps after 15 min inactivity
- First request takes 30-60s to wake up
- Upgrade to Starter ($7/month) for always-on

## Useful Commands

**View logs:**
- Go to service → "Logs" tab

**Run Django commands:**
- Go to service → "Shell" tab
- Example: `python manage.py migrate`

**Redeploy:**
- Push to GitHub (auto-deploys)
- Or: "Manual Deploy" → "Deploy latest commit"

## Cost

- **Free:** $0 (spins down after inactivity)
- **Starter:** $7/month (always on, 512 MB RAM)
- **Standard:** $25/month (2 GB RAM)

---

For detailed instructions, see [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md)
